#!/usr/bin/env python3
"""Schema convention checker for Ironclad.

Scans SQL files, Laravel migrations, and Prisma schemas for rule violations.

Exit codes: 0 = no error-severity findings, 1 = violations, 2 = usage error.

Severity comes from a preset, so the same checker can be gentle on a brownfield
repo and block hard on a regulated one:

    presets/legacy-friendly.yml   everything warns
    presets/balanced.yml          default — most rules block
    presets/strict.yml            everything blocks, no warnings
    .agent/standards.yml          per-repo override, created by init_standards.py

Resolution order: --config > --preset > .agent/standards.yml > built-in balanced.

Rules:
  DB-01 native enum in schema
  DB-02 magic number compared to / assigned on a status-like field
  DB-03 status integer with no FK/CHECK
  DB-04 status stored as text
  DB-05 boolean named for a non-binary concept
  DB-06 money stored as float
  DB-07 timestamp without timezone
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
# Two layouts: inside the skill (assets/presets/) and inside a target repo where
# init_standards.py --with-checker copied the checker next to its presets (presets/).
_HERE = Path(__file__).resolve().parent
PRESET_DIR = next((d for d in (_HERE / "presets", SKILL_DIR / "assets" / "presets") if d.is_dir()),
                  _HERE / "presets")

DEFAULT_PRESET = "balanced"

BUILTIN_PRESET = {
    "name": "balanced",
    "rules": {"DB-01": "error", "DB-02": "error", "DB-03": "warn",
              "DB-04": "error", "DB-05": "warn", "DB-06": "warn", "DB-07": "warn"},
    "exceptions": [],
    "boolean_allowlist": ["is_active", "is_deleted", "is_published",
                          "is_verified", "is_terminal", "has_invoice"],
}

RULE_TITLES = {
    "DB-01": "native enum in schema",
    "DB-02": "magic number on a status field",
    "DB-03": "status integer without FK/CHECK",
    "DB-04": "status stored as text",
    "DB-05": "boolean named for a non-binary concept",
    "DB-06": "money stored as float",
    "DB-07": "timestamp without timezone",
}

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

MONEY_WORD = r"(?:amount|price|harga|total|subtotal|cost|biaya|fee|tarif|salary|gaji|balance|saldo)"
MONEY_FLOAT = re.compile(
    rf"\b([a-z0-9_]*(?:{MONEY_WORD})[a-z0-9_]*)\b\s+(?:float|double|real|float8|float4)\b", re.I)
MONEY_FLOAT_LARAVEL = re.compile(rf"\$table\s*->\s*(?:float|double)\s*\(\s*['\"]([^'\"]+)['\"]", re.I)

TIMESTAMP_BARE = re.compile(r"\b([a-z0-9_]+)\s+timestamp\b(?!\s*\(?\s*\d*\s*\)?\s*with\s+time\s+zone)", re.I)

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next",
             "storage", "__pycache__", ".venv", "venv"}
TARGETS = {".sql", ".php", ".prisma"}


# ---------------------------------------------------------------- preset loading
# Deliberately dependency-free: CI often has no PyYAML, and a checker that fails
# to import its own config is worse than no checker. Parses the subset we ship:
# `key: value` under `rules:`, and `- item` lists under named keys.
def _parse_simple_yaml(text):
    data = {"rules": {}, "exceptions": [], "boolean_allowlist": []}
    section = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(("name:", "title:", "description:")):
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip()
            section = None
            continue
        if line.startswith("rules:"):
            section = "rules"
            continue
        if line.startswith(("exceptions:", "boolean_allowlist:")):
            section = line.split(":")[0].strip()
            continue
        if section == "rules" and ":" in line:
            key, _, val = line.partition(":")
            data["rules"][key.strip()] = val.split("#")[0].strip().lower()
            continue
        if section in ("exceptions", "boolean_allowlist") and line.lstrip().startswith("-"):
            data[section].append(line.lstrip()[1:].strip().strip("'\""))
    return data


def load_preset(name=None, config_path=None, repo_paths=None):
    """Merge preset layers. Returns (config, source_label)."""
    layers = []
    source = "builtin:balanced"

    if name and (PRESET_DIR / f"{name}.yml").is_file():
        layers.append(_parse_simple_yaml((PRESET_DIR / f"{name}.yml").read_text()))
        source = f"preset:{name}"
    elif name:
        print(f"unknown preset '{name}' — available: "
              f"{', '.join(sorted(p.stem for p in PRESET_DIR.glob('*.yml')))}", file=sys.stderr)
        return None, None

    if config_path:
        cfg = Path(config_path)
        if not cfg.is_file():
            print(f"config not found: {cfg}", file=sys.stderr)
            return None, None
        layers.append(_parse_simple_yaml(cfg.read_text()))
        source = str(cfg)

    if not layers:
        # auto-discover .agent/standards.yml, walking up from the first target
        for base in (Path(p) for p in (repo_paths or ["."])):
            base = base.resolve()
            for d in [base, *base.parents]:
                cand = d / ".agent" / "standards.yml"
                if cand.is_file():
                    layers.append(_parse_simple_yaml(cand.read_text()))
                    source = str(cand)
                    break
            if layers:
                break

    merged = {"name": DEFAULT_PRESET, "rules": dict(BUILTIN_PRESET["rules"]),
              "exceptions": [], "boolean_allowlist": list(BUILTIN_PRESET["boolean_allowlist"])}
    for layer in layers:
        merged["rules"].update(layer.get("rules") or {})
        if layer.get("exceptions"):
            merged["exceptions"] = layer["exceptions"]
        if layer.get("boolean_allowlist"):
            merged["boolean_allowlist"] = layer["boolean_allowlist"]
        if layer.get("name"):
            merged["name"] = layer["name"]
    return merged, source


# ------------------------------------------------------------------- rule engine
def iter_files(paths, exceptions=()):
    exc = [e.rstrip("/") for e in exceptions]
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix in TARGETS:
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.suffix not in TARGETS:
                    continue
                if set(f.parts) & SKIP_DIRS:
                    continue
                s = str(f)
                if any(e in s for e in exc):
                    continue
                yield f


def is_migration_like(path, text):
    name = path.name.lower()
    return ("migration" in name or "migrasi" in name
            or "$table->" in text or re.search(r"\bCREATE\s+TABLE\b", text, re.I) is not None)


def check_file(path, cfg):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [{"rule": "IO", "severity": "error", "line": 0,
                 "msg": f"unreadable: {e}", "file": str(path)}]

    def add(rule, line, msg):
        sev = cfg["rules"].get(rule, "warn")
        if sev in ("off", "ignore", "none"):
            return
        findings.append({"rule": rule, "severity": sev, "line": line,
                         "msg": msg, "file": str(path)})

    lines = text.splitlines()
    migration = is_migration_like(path, text)
    bool_allow = {b.lower() for b in cfg.get("boolean_allowlist") or []}

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
                add("DB-01", i, f"{label}; use integer code + lookup table (see DB-03)")
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
                add("DB-02", i, f"magic number in {kind} on `{m.group(1)}`; use a named constant")
                break

        # DB-04
        m = VARCHAR_STATUS.search(line) or LARAVEL_STRING_STATUS.search(line)
        if m and migration:
            add("DB-04", i, f"status stored as text (`{m.group(1)}`); use smallint code + lookup table")

        # DB-05
        m = BOOL_NAMES.search(line)
        if m and m.group(0).lower() not in bool_allow:
            add("DB-05", i, f"`{m.group(0)}` is not a binary concept; use a code column")

        # DB-06
        if migration:
            m = MONEY_FLOAT.search(line) or MONEY_FLOAT_LARAVEL.search(line)
            if m:
                add("DB-06", i, f"money column `{m.group(1)}` uses a float type; "
                                f"use bigint minor units + currency code")

        # DB-07 — camelCase `*At` is the Laravel/Prisma timestamp convention, not a smell
        if migration:
            m = TIMESTAMP_BARE.search(line)
            if m and not re.search(r"[a-z]At$", m.group(1)) and "timestamptz" not in line.lower():
                add("DB-07", i, f"`{m.group(0).strip()}` has no timezone; "
                                f"use timestamptz (or createdAt/updatedAt in Laravel)")

    # DB-03: a status code column with no FK/CHECK anywhere in the file
    if migration:
        for i, line in enumerate(lines, 1):
            m = re.search(rf"\b([a-z0-9_]*{STATUS_WORD}[a-z0-9_]*(?:_code)?)\b\s+"
                          rf"(?:smallint|tinyint|integer|int|bigint)", line, re.I)
            if not m:
                continue
            col = m.group(1)
            if not STATUS_COL.match(col):
                continue
            if re.search(rf"{re.escape(col)}[^\n]*(REFERENCES|references|constrained|CHECK|check)",
                         text, re.I):
                continue
            add("DB-03", i, f"`{col}` has no FK to a lookup table or CHECK constraint")

    return findings


def main():
    ap = argparse.ArgumentParser(
        description="Company schema convention checker",
        epilog="presets: " + ", ".join(sorted(p.stem for p in PRESET_DIR.glob("*.yml"))))
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--preset", help="preset name (balanced, strict, legacy-friendly)")
    ap.add_argument("--config", help="explicit config file (overrides --preset)")
    ap.add_argument("--strict", action="store_true",
                    help="escalate every warn to an error (legacy flag, still supported)")
    ap.add_argument("--list-presets", action="store_true")
    args = ap.parse_args()

    if args.list_presets:
        for p in sorted(PRESET_DIR.glob("*.yml")):
            data = _parse_simple_yaml(p.read_text())
            n_err = sum(1 for v in data["rules"].values() if v == "error")
            n_warn = sum(1 for v in data["rules"].values() if v == "warn")
            print(f"{p.stem:18} errors={n_err} warns={n_warn}  {data.get('title','')}")
        return 0

    targets = args.paths or ["."]
    cfg, source = load_preset(args.preset, args.config, targets)
    if cfg is None:
        return 2

    files = list(iter_files(targets, cfg.get("exceptions") or ()))
    if not files:
        print("no .sql/.php/.prisma files found", file=sys.stderr)
        return 2

    findings = []
    for f in files:
        findings.extend(check_file(f, cfg))

    if args.strict:
        for f in findings:
            f["severity"] = "error"

    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warn"]

    if args.json:
        print(json.dumps({"preset": cfg.get("name"), "source": source,
                          "files": len(files), "findings": findings,
                          "errors": len(errors), "warnings": len(warns)},
                         indent=2, ensure_ascii=False))
    else:
        for f in findings:
            tag = "ERROR" if f["severity"] == "error" else "warn "
            print(f"{f['file']}:{f['line']}: [{f['rule']}] {tag} {f['msg']}")
        if findings:
            print()
        print(f"preset: {cfg.get('name')} ({source})")
        print(f"{len(files)} file(s), {len(errors)} error(s), {len(warns)} warning(s)")
        if warns and not errors:
            print("warnings do not fail the build; use --strict to escalate")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
