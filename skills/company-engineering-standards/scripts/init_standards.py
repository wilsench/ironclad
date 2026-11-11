#!/usr/bin/env python3
"""Bootstrap a repo with the company standards policy file.

Copies templates/standards.md to <repo>/.agent/standards.md (never overwrites),
and optionally drops a working checker into the repo so CI does not depend on
the skill being installed.

Usage:
  python3 scripts/init_standards.py [repo_path] [--with-checker] [--force]
"""

import argparse
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "standards.md"
CHECKER = SKILL_DIR / "scripts" / "check_schema.py"


def main() -> int:
    ap = argparse.ArgumentParser(description="Bootstrap company standards into a repo")
    ap.add_argument("repo", nargs="?", default=".", help="repo root (default: .)")
    ap.add_argument("--with-checker", action="store_true",
                    help="also copy check_schema.py into the repo's scripts/")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"not a directory: {repo}", file=sys.stderr)
        return 2
    if not TEMPLATE.is_file():
        print(f"template missing: {TEMPLATE}", file=sys.stderr)
        return 2

    agent_dir = repo / ".agent"
    agent_dir.mkdir(exist_ok=True)
    target = agent_dir / "standards.md"

    if target.exists() and not args.force:
        print(f"exists, left untouched: {target.relative_to(repo)}")
    else:
        shutil.copyfile(TEMPLATE, target)
        print(f"wrote {target.relative_to(repo)}")

    if args.with_checker:
        scripts = repo / "scripts"
        scripts.mkdir(exist_ok=True)
        dest = scripts / "check_schema.py"
        if dest.exists() and not args.force:
            print(f"exists, left untouched: {dest.relative_to(repo)}")
        else:
            shutil.copyfile(CHECKER, dest)
            dest.chmod(0o755)
            print(f"wrote {dest.relative_to(repo)}")

    print("\nnext: review .agent/standards.md, then run")
    print("  python3 scripts/check_schema.py . --json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
