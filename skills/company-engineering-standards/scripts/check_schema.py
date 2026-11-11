#!/usr/bin/env python3
"""Schema convention checker for company-engineering-standards.

Scans SQL files, Laravel migrations, and Prisma schemas for rule violations.
Exit 0 = clean, 1 = violations, 2 = usage error.

Rules:
  DB-01 native enum in schema
  DB-02 magic number compared to / assigned on a status-like field
  DB-03 status column with no FK/CHECK nearby (strict mode only)
  DB-04 varchar status column
  DB-05 boolean named for a non-binary concept
"""

import argparse
import json
import re
import sys
from pathlib import Path

# `type`/`tipe` must start a word segment, otherwise `mimeType`/`prototype` false-positive.
_LEAD = r"(?<![a-z])"
STATUS_WORD = _LEAD + r"(?:status|state|stage|kondisi|keberangkatan|ketersediaan|kategori|type|tipe)"
STATUS_COL = re.compile(rf"^[a-z0-9_]*{STATUS_WORD}[a-z0-9_]*$", re.I)

ENUM_PATTERNS = [
    (re.compile(r"\$table\s*->\s*enum\s*\(", re.I), "Laravel $table->enum()"),
    (re.compile(r"\bALTER\s+TABLE\b[^;]*\bADD\s+COLUMN\b[^;]*\benum\s*\(", re.I),
     "SQL enum column"),
    (re.compile(r"^\s*\w+\s+enum\s*\(", re.I | re.M), "SQL/prisma enum column"),
    (re.compile(r"^\s*enum\s+\w+\s*\{", re.I | re.M), "prisma enum block"),
]

# status = 0 | ->where('status', 2) | === 3 on a status-y name
MAGIC_COMPARE = re.compile(
    rf"({STATUS_WORD}[a-zA-Z0-9_]*)\s*(?:===?|!==?|<>|==|!=)\s*'?\d+'?", re.I)
MAGIC_WHERE = re.compile(
    rf"['\"]([a-z0-9_]*{STATUS_WORD}[a-z0-9_]*)['\"]\s*,\s*'?\d+'?", re.I)
MAGIC_ASSIGN = re.compile(
    rf"\$?\w*{STATUS_WORD}\w*\s*=\s*'?[0-9]'?\s*;", re.I)

VARCHAR_STATUS = re.compile(
    rf"['\"]?([a-z0-9_]*{STATUS_WORD}[a-z0-9_]*)['\"]?\s+(?:varchar|string|text)", re.I)
# Laravel puts the type first: $table->string('departure_status')
LARAVEL_STRING_STATUS = re.compile(
    rf"\$table\s*->\s*(?:string|text)\s*\(\s*['\"]([a-z0-9_]*{STATUS_WORD}[a-z0-9_]*)['\"]", re.I)

BOOL_NAMES = re.compile(r"\b(is|has|should|can)_(?:status|state|kondisi|tipe|type|kategori)\b", re.I)

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", "storage", "__pycache__"}
TARGETS = {".sql", ".php", ".prisma"}


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix in TARGETS:
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.suffix in TARGETS and not (set(f.parts) & SKIP_DIRS):
                    yield f


def is_migration_like(path, text):
    name = path.name.lower()
    return ("migration" in name or "migrasi" in name
            or "$table->" in text or re.search(r"\bCREATE\s+TABLE\b", text, re.I) is not None)


def check_file(path):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [{"rule": "IO", "line": 0, "msg": f"unreadable: {e}", "file": str(path)}]

    lines = text.splitlines()
    migration = is_migration_like(path, text)

    in_comment_block = False
    check_depth = 0          # paren depth inside a CHECK(...) constraint
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("/*"):
            in_comment_block = True
        if in_comment_block:
            if "*/" in stripped:
                in_comment_block = False
            continue
        if stripped.startswith(("//", "#", "--", "*")):
            continue

        # DB-01
        for pat, label in ENUM_PATTERNS:
            if pat.search(line):
                findings.append({
                    "rule": "DB-01", "line": i, "file": str(path),
                    "msg": f"{label}; use integer code + lookup table (see DB-03)",
                })
                break

        # a CHECK constraint is exactly where literal codes belong (DDL, not app logic)
        line_in_check = check_depth > 0 or re.search(r"\bCHECK\b", line, re.I) is not None
        if re.search(r"\bCHECK\b", line, re.I):
            check_depth += line.count("(") - line.count(")")
        elif check_depth > 0:
            check_depth += line.count("(") - line.count(")")
            if check_depth < 0:
                check_depth = 0

        # DB-02
        for pat, kind in ((MAGIC_COMPARE, "comparison"), (MAGIC_WHERE, "query filter"),
                          (MAGIC_ASSIGN, "assignment")):
            m = pat.search(line)
            if m and line_in_check:
                break
            if m and (migration or kind != "assignment"):
                findings.append({
                    "rule": "DB-02", "line": i, "file": str(path),
                    "msg": f"magic number in {kind} on `{m.group(1)}`; use a named constant",
                })
                break

        # DB-04
        m = VARCHAR_STATUS.search(line) or LARAVEL_STRING_STATUS.search(line)
        if m and migration:
            findings.append({
                "rule": "DB-04", "line": i, "file": str(path),
                "msg": f"status stored as text (`{m.group(1)}`); use smallint code + lookup table",
            })

        # DB-05
        m = BOOL_NAMES.search(line)
        if m:
            findings.append({
                "rule": "DB-05", "line": i, "file": str(path),
                "msg": f"`{m.group(0)}` is not a binary concept; use a code column",
            })

    # DB-03: a status code column with no FK/CHECK anywhere in the file
    if migration:
        for i, line in enumerate(lines, 1):
            m = re.search(rf"\b([a-z0-9_]*{STATUS_WORD}[a-z0-9_]*(?:_code)?)\b\s+(?:smallint|tinyint|integer|int|bigint)", line, re.I)
            if not m:
                continue
            col = m.group(1)
            if not STATUS_COL.match(col):
                continue
            if re.search(rf"{re.escape(col)}[^\n]*(REFERENCES|references|constrained|CHECK|check)", text, re.I):
                continue
            findings.append({
                "rule": "DB-03", "line": i, "file": str(path),
                "msg": f"`{col}` has no FK to a lookup table or CHECK constraint (DB-06)",
            })

    return findings


def main():
    ap = argparse.ArgumentParser(description="Company schema convention checker")
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat DB-03 as an error")
    args = ap.parse_args()

    targets = args.paths or ["."]
    files = list(iter_files(targets))
    if not files:
        print("no .sql/.php/.prisma files found", file=sys.stderr)
        return 2

    findings = []
    for f in files:
        findings.extend(check_file(f))

    errors = [f for f in findings if f["rule"] != "DB-03" or args.strict]

    if args.json:
        print(json.dumps({"files": len(files), "findings": findings,
                          "errors": len(errors)}, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']}: [{f['rule']}] {f['msg']}")
        print(f"\n{len(files)} file(s), {len(errors)} violation(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
