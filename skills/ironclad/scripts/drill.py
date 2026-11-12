#!/usr/bin/env python3
"""Selftest and drill for Ironclad.

Two different questions, two different answers:

  --selftest   Does the gate work? Deterministic. Runs canonical fixtures through
               the checker and asserts the verdicts. If this fails, the install is
               broken and no agent can be trusted with it.

  --prompt     Print a task to paste into your agent. It deliberately does not
               mention integer codes — the point is to see whether the agent
               applies the rule on its own.

  --grade F    Score the schema the agent produced. Says PASS/FAIL per criterion
               with the evidence, so "it looks fine" is not an accepted answer.

Nothing here calls a model. A tool that grades models by asking a model would be
grading itself.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "check_schema.py"

GREEN, RED, DIM, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = DIM = OFF = ""

# (sql, preset, expected_exit, rule that must appear)
# The preset matters and is printed, because balanced is not "everything blocks":
# money-as-float and naive timestamps warn unless the repo chose strict. Pretending
# otherwise would make this selftest lie in the flattering direction.
FIXTURES = {
    "enum blocked in the default preset": (
        """CREATE TABLE orders (
  id bigint PRIMARY KEY,
  status enum('new','paid','shipped') NOT NULL
);
""",
        "balanced", 1, "DB-01",
    ),
    "integer + lookup + fk accepted": (
        """CREATE TABLE order_status (code smallint PRIMARY KEY, label text NOT NULL);
CREATE TABLE orders (
  id bigint PRIMARY KEY,
  status_code smallint NOT NULL REFERENCES order_status(code)
);
""",
        "balanced", 0, None,
    ),
    "text label blocked in the default preset": (
        """CREATE TABLE orders (
  id bigint PRIMARY KEY,
  status varchar(32) NOT NULL DEFAULT 'new'
);
""",
        "balanced", 1, "DB-04",
    ),
    "money as float blocks under strict": (
        """CREATE TABLE invoices (
  id bigint PRIMARY KEY,
  total double precision NOT NULL
);
""",
        "strict", 1, "DB-06",
    ),
    "naive timestamp blocks under strict": (
        """CREATE TABLE events (
  id bigint PRIMARY KEY,
  happened_at timestamp NOT NULL
);
""",
        "strict", 1, "DB-07",
    ),
    # Most real migrations wrap the constraint onto a second line. Reading only the
    # column's own line called this a violation — a false positive on correct SQL,
    # which is worse than a miss because it teaches people to distrust the tool.
    "multi-line FOREIGN KEY accepted": (
        """CREATE TABLE order_status (code smallint PRIMARY KEY);
CREATE TABLE orders (
  id bigint PRIMARY KEY,
  status_code smallint NOT NULL,
  CONSTRAINT orders_status_fk FOREIGN KEY (status_code)
      REFERENCES order_status (code)
);
""",
        "strict", 0, None,
    ),
    "status integer with no FK blocked": (
        """CREATE TABLE orders (
  id bigint PRIMARY KEY,
  status_code smallint NOT NULL
);
""",
        "strict", 1, "DB-03",
    ),
    # Laravel: enum, float money, and naive timestamp in the framework's own idiom.
    # A regex checker that only understands raw SQL silently passes all three.
    "laravel enum + float + naive timestamp caught": (
        ".php",
        """<?php
Schema::create('orders', function (Blueprint $t) {
    $t->enum('status', ['new', 'paid']);
    $t->float('total');
    $t->timestamp('created_at');
});
""",
        "balanced", 1, "DB-01",
    ),
    "laravel integer + timestampTz accepted": (
        ".php",
        """<?php
Schema::create('order_status', function (Blueprint $t) {
    $t->unsignedSmallInteger('code')->primary();
});
Schema::create('orders', function (Blueprint $t) {
    $t->unsignedSmallInteger('status_code');
    $t->foreign('status_code')->references('code')->on('order_status');
    $t->bigInteger('total_minor');
    $t->timestampTz('created_at')->useCurrent();
});
""",
        "strict", 0, None,
    ),
}


def run_checker(paths: list[str], preset: str = "balanced") -> tuple[int, str]:
    cmd = [sys.executable, str(CHECKER), *paths, "--preset", preset]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def selftest() -> int:
    failures = 0
    print("Ironclad selftest — does the gate actually block?\n")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for name, spec in FIXTURES.items():
            # A fixture may carry its own suffix; PHP content in a .sql file never
            # matches the Laravel patterns and would silently "pass" a broken test.
            if len(spec) == 5:
                suffix, sql, preset, want_exit, want_rule = spec
            else:
                sql, preset, want_exit, want_rule = spec
                suffix = ".sql"
            f = tmp / (re.sub(r"\W+", "_", name) + suffix)
            f.write_text(sql)
            code, out = run_checker([str(f)], preset)
            ok = code == want_exit
            rule_ok = want_rule is None or want_rule in out
            if ok and rule_ok:
                print(f"  {GREEN}PASS{OFF}  {name}")
            else:
                failures += 1
                print(f"  {RED}FAIL{OFF}  {name}")
                print(f"        expected exit {want_exit}"
                      f"{', mentions ' + want_rule if want_rule else ''}"
                      f" — got exit {code} (preset {preset})")
                for line in out.strip().splitlines()[:4]:
                    print(f"        {DIM}{line}{OFF}")

        # Clear the fixture files first: this sub-test asserts on the WHOLE tmpdir,
        # and leftovers from the loop above would trip DB-08 for the wrong reason.
        for leftover in tmp.iterdir():
            if leftover.is_file():
                leftover.unlink()

        # The one rule that reads across files: two developers, two styles.
        (tmp / "dev_a.sql").write_text(
            "CREATE TABLE orders (\n  id bigint PRIMARY KEY,\n"
            "  status_code smallint NOT NULL REFERENCES order_status(code)\n);\n"
        )
        (tmp / "dev_b.sql").write_text(
            "CREATE TABLE invoices (\n  id bigint PRIMARY KEY,\n"
            "  status enum('draft','sent') NOT NULL\n);\n"
        )
        code, out = run_checker([str(tmp)])
        if "DB-08" in out and code == 1:
            print(f"  {GREEN}PASS{OFF}  mixed project flagged (DB-08) — the two-developer case")
        else:
            failures += 1
            print(f"  {RED}FAIL{OFF}  mixed project NOT flagged — this is the rule the tool exists for")
            for line in out.strip().splitlines()[:4]:
                print(f"        {DIM}{line}{OFF}")

        # Identical style must stay quiet, or the rule is noise.
        for f in tmp.glob("*.sql"):
            f.unlink()
        (tmp / "a.sql").write_text(
            "CREATE TABLE orders (\n  id bigint PRIMARY KEY,\n"
            "  status_code smallint NOT NULL REFERENCES s(code)\n);\n"
        )
        (tmp / "b.sql").write_text(
            "CREATE TABLE invoices (\n  id bigint PRIMARY KEY,\n"
            "  status_code smallint NOT NULL REFERENCES s(code)\n);\n"
        )
        code, out = run_checker([str(tmp)], "strict")
        if code == 0 and "DB-08" not in out:
            print(f"  {GREEN}PASS{OFF}  consistent project stays silent (no false alarm)")
        else:
            failures += 1
            print(f"  {RED}FAIL{OFF}  false positive: consistent project was flagged")

        # The grader itself must accept both FK spellings, or it fails beginner
        # answers that a senior would call correct.
        table_fk = tmp / "table_fk.sql"
        table_fk.write_text(
            "CREATE TABLE order_status (code smallint PRIMARY KEY, label text NOT NULL);\n"
            "INSERT INTO order_status (code, label) VALUES (1, 'new');\n"
            "CREATE TABLE orders (\n  id bigint PRIMARY KEY,\n"
            "  status_code smallint NOT NULL,\n  created_at timestamptz NOT NULL DEFAULT now(),\n"
            "  CONSTRAINT fk_status FOREIGN KEY (status_code) REFERENCES order_status (code)\n);\n"
        )
        g = subprocess.run([sys.executable, str(HERE / "drill.py"), "--grade", str(table_fk)],
                           capture_output=True, text=True)
        if "PASS  status column has a foreign key" in g.stdout:
            print(f"  {GREEN}PASS{OFF}  grader accepts table-level FOREIGN KEY syntax")
        else:
            failures += 1
            print(f"  {RED}FAIL{OFF}  grader rejected a correct table-level FK")

        bad = tmp / "bad_grader_input.sql"
        bad.write_text("CREATE TABLE orders (id bigint PRIMARY KEY, status enum('a','b'));\n")
        g = subprocess.run([sys.executable, str(HERE / "drill.py"), "--grade", str(bad)],
                           capture_output=True, text=True)
        if g.returncode == 1 and "enum found" in g.stdout:
            print(f"  {GREEN}PASS{OFF}  grader still rejects an enum answer")
        else:
            failures += 1
            print(f"  {RED}FAIL{OFF}  grader passed an enum answer — it is now useless")

    print()
    if failures:
        print(f"{RED}{failures} check(s) failed{OFF} — do not trust the gate yet.")
        return 1
    print(f"{GREEN}All checks passed{OFF}. The gate blocks enum, text status, float money,")
    print("naive timestamps, and mixed styles — and stays quiet when the repo is consistent.")
    print("\nNext: prove your agent knows.  ironclad drill")
    return 0


PROMPT_ID = """\
Kerjakan di repo ini.

Buat migrasi SQL untuk fitur pesanan:
- tabel `orders`: id, nomor pesanan, status pesanan (baru, dibayar, dikemas,
  dikirim, selesai, dibatalkan), total, waktu dibuat
- tabel `order_items`: id, referensi ke orders, nama barang, jumlah, harga satuan

Simpan sebagai `answer.sql` di root repo. Tulis kodenya saja, tanpa penjelasan."""

PROMPT_EN = """\
Work in this repository.

Write a SQL migration for an order feature:
- `orders` table: id, order number, order status (new, paid, packed, shipped,
  completed, cancelled), total, created time
- `order_items` table: id, reference to orders, item name, quantity, unit price

Save it as `answer.sql` in the repo root. Code only, no explanation."""


def prompt(lang: str = "id") -> int:
    text = PROMPT_ID if lang == "id" else PROMPT_EN
    print("Paste this into your agent (inside the repo that has .agent/standards.md).")
    print("Do not add hints — the whole point is to see what it does on its own.\n")
    print("-" * 68)
    print(text)
    print("-" * 68)
    print("\nThen grade what it wrote:")
    print("  ironclad drill answer.sql")
    return 0


def find_lookup_tables(sql: str) -> list[str]:
    return re.findall(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"']?([a-z0-9_]*(?:status|state)[a-z0-9_]*)",
        sql, re.I,
    )


def grade(path: Path, preset: str = "balanced") -> int:
    sql = path.read_text(encoding="utf-8", errors="replace")
    low = sql.lower()
    results: list[tuple[bool, str, str]] = []

    # 1. mechanical: whatever the repo policy says
    code, out = run_checker([str(path)], preset)
    results.append((
        code == 0,
        "policy check",
        "clean" if code == 0 else "see findings below",
    ))

    # 2. did it avoid enum at all
    has_enum = bool(re.search(r"\benum\s*\(", low)) or "table->enum" in low
    results.append((not has_enum, "no enum column",
                    "enum found" if has_enum else "none"))

    # 3. is there a lookup table for the status
    lookups = find_lookup_tables(sql)
    results.append((bool(lookups), "lookup table for status",
                    ", ".join(lookups) if lookups else "no *_status table"))

    # 4. does the status column carry a foreign key — two legitimate spellings:
    #      inline:   status_code smallint NOT NULL REFERENCES order_status(code)
    #      table:    CONSTRAINT fk FOREIGN KEY (status_code) REFERENCES order_status(code)
    # Only recognising the first one fails correct answers, which is worse than
    # missing a bad one: it teaches people to ignore the tool.
    fk = re.search(
        r"([a-z_]*status[a-z_]*)\s+(?:smallint|int|integer|bigint)[^,;]*?\bREFERENCES\s+([a-z0-9_]+)",
        sql, re.I,
    )
    if not fk:
        fk = re.search(
            r"FOREIGN\s+KEY\s*\(\s*([a-z_]*status[a-z_]*)\s*\)\s*REFERENCES\s+([a-z0-9_]+)",
            sql, re.I,
        )
    results.append((bool(fk), "status column has a foreign key",
                    f"{fk.group(1)} → {fk.group(2)}" if fk else "no REFERENCES on a status column"))

    # 5. are the six statuses seeded, i.e. is adding one a data change
    inserts = re.findall(r"INSERT\s+INTO\s+[a-z0-9_]*status[a-z0-9_]*[^;]*;", sql, re.I | re.S)
    seeded = len(inserts) > 0
    results.append((seeded, "statuses seeded as data (not schema)",
                    f"{len(inserts)} INSERT statement(s)" if seeded else "no INSERT — statuses may live in the type"))

    # 6. money not float
    float_money = re.search(r"(total|amount|price|harga|total_amount)[a-z_]*\s+(float|double|real|numeric\s*\(\s*\d+\s*,\s*\d+\s*\))", sql, re.I)
    results.append((not float_money, "money is integer minor units",
                    float_money.group(0) if float_money else "ok"))

    # 7. timezone
    naive = re.search(r"[a-z_]*at\s+timestamp\b(?!\s+with)", sql, re.I)
    results.append((not naive, "timestamps carry a timezone",
                    naive.group(0) if naive else "ok"))

    # 8. did it cite the rule it followed
    cited = re.findall(r"DB-0[1-8]", sql)
    results.append((bool(cited), "cites a rule ID", ", ".join(sorted(set(cited))) if cited else "no DB-0x reference"))

    print(f"Grading {path}\n")
    passed = 0
    for ok, name, evidence in results:
        mark = f"{GREEN}PASS{OFF}" if ok else f"{RED}FAIL{OFF}"
        print(f"  {mark}  {name:<38} {DIM}{evidence}{OFF}")
        passed += ok

    if code != 0:
        print()
        for line in out.strip().splitlines():
            if "[DB-" in line:
                print(f"        {line}")

    total = len(results)
    print(f"\n{passed}/{total} criteria")
    if passed == total:
        print(f"{GREEN}The agent applied the policy on its own.{OFF} Keep the checker in CI anyway:")
        print("an agent that behaves today can behave differently tomorrow, and the")
        print("checker is what makes that a failed build instead of a bad schema.")
        return 0

    print(f"{RED}The agent did not hold the line.{OFF} What to do, in order:")
    if not results[0][0] or not results[1][0]:
        print("  1. Make sure the agent actually loaded the skill: ask it to quote")
        print("     .agent/standards.md, and check the file is committed.")
    if not results[7][0]:
        print("  2. Ask it to report rule IDs. An agent that cannot name the rule")
        print("     it followed was guessing.")
    print("  3. Put the checker in CI. The skill is advice; the gate is the")
    print("     only thing that cannot be argued with at 2am.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--selftest", action="store_true", help="verify the checker gates correctly")
    ap.add_argument("--prompt", action="store_true", help="print a task for your agent")
    ap.add_argument("--lang", default="id", choices=["id", "en"])
    ap.add_argument("--grade", metavar="FILE", help="score the schema an agent produced")
    ap.add_argument("--preset", default="balanced")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.prompt:
        return prompt(a.lang)
    if a.grade:
        p = Path(a.grade)
        if not p.exists():
            print(f"no such file: {p}", file=sys.stderr)
            return 2
        return grade(p, a.preset)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
