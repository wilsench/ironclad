#!/usr/bin/env python3
"""Write the Ironclad instruction block into the files AI agents read on their own.

A skill is only loaded when the agent judges it relevant. That is too late for
"before you write schema, follow these rules" — by then the code is written.
The always-read files are AGENTS.md, CLAUDE.md, GEMINI.md, .cursor/rules/*.mdc and
copilot-instructions.md, so the standing instruction goes there.

The block is fenced with sentinels so re-installing updates it in place instead of
appending a second copy, and so uninstalling removes exactly what we added and
nothing the user wrote.

Usage:
  agent_files.py --project .            write/update the block for this repo
  agent_files.py --project . --remove   remove only our block
  agent_files.py --project . --print    show what would be written
  agent_files.py --project . --only AGENTS.md,CLAUDE.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BEGIN = "<!-- ironclad:begin v1 -->"
END = "<!-- ironclad:end -->"

BODY = """## Ironclad — one way to store status per project

Two people on one database can each add a "status" and store it differently:
`status ENUM('paid')` in one table, `status_code = 2` in another. Both pass review;
together the project becomes unmaintainable.

Before writing anything that stores status, read the repo first (`grep -rn status`,
migrations, models). Then:

- **one consistent style already used** → follow it. Say which style in one line and
  carry on; do not stop to ask.
- **two styles already present** → stop, name both with their files, and ask which
  becomes the standard. Never add a third while that is open.
- **no status anywhere yet** → use the house default. Do not ask.
  `status_code SMALLINT NOT NULL` + lookup table (`code` PK, `label`) + FK from the
  column, codes step by 10 (10, 20, 30), never reused, plus named constants in code.
  Say "house default: status_code + lookup" in one line, then write it.

Money: integer minor units, never float. Timestamps: `timestamptz`, never naive.
"""

# Per-repo: only files this repo owns. Written by `ironclad init`.
TARGETS = [
    ("AGENTS.md", "Codex, opencode, and anything reading the AGENTS.md convention"),
    ("CLAUDE.md", "Claude Code"),
    ("GEMINI.md", "Gemini CLI"),
    (".cursor/rules/ironclad.mdc", "Cursor"),
    (".github/copilot-instructions.md", "GitHub Copilot"),
]

# Global: what each agent reads when it starts anywhere on this machine. Written by
# the installer, so a fresh repo needs no `ironclad init` before the agent behaves.
# Only installed when the agent's own config dir already exists — we do not create
# ~/.claude for someone who does not use Claude Code.
GLOBAL_TARGETS = [
    (".claude/CLAUDE.md", ".claude", "Claude Code", False),
    (".codex/AGENTS.md", ".codex", "Codex", False),
    (".gemini/GEMINI.md", ".gemini", "Gemini CLI", False),
    (".cursor/rules/ironclad.mdc", ".cursor", "Cursor", False),
    (".config/opencode/AGENTS.md", ".config/opencode", "opencode", False),
    (".agents/AGENTS.md", ".agents", "agents reading the AGENTS.md convention", True),
]

CURSOR_HEADER = """---
description: Ironclad database rules — apply before writing schema code
alwaysApply: true
---
"""


def upsert(path: Path, body: str, header: str = "") -> str:
    """Insert or replace our fenced block. Returns 'created' | 'updated' | 'unchanged'."""
    block = f"{BEGIN}\n{body}{END}\n"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text((header + block), encoding="utf-8")
        return "created"

    text = path.read_text(encoding="utf-8", errors="replace")
    if BEGIN in text and END in text:
        lo = text.index(BEGIN)
        hi = text.index(END) + len(END)
        new = text[:lo] + block.rstrip("\n") + text[hi:]
        if new == text:
            return "unchanged"
        path.write_text(new, encoding="utf-8")
        return "updated"

    # Append, keeping a blank line between the user's content and ours.
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    path.write_text(text + sep + block, encoding="utf-8")
    return "created"


def remove(path: Path) -> str:
    if not path.exists():
        return "absent"
    text = path.read_text(encoding="utf-8", errors="replace")
    if BEGIN not in text or END not in text:
        return "no-block"
    lo = text.index(BEGIN)
    hi = text.index(END) + len(END)
    out = (text[:lo] + text[hi:]).rstrip("\n")
    if out.strip() == "" or out.strip() == CURSOR_HEADER.strip():
        path.unlink()
        # clean up an empty .cursor/rules we created
        parent = path.parent
        if parent.name == "rules" and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
        return "removed-file"
    path.write_text(out + "\n", encoding="utf-8")
    return "removed-block"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="repo to write into (default) ")
    ap.add_argument("--global", dest="glob", action="store_true",
                    help="write into each agent's own config dir under $HOME")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--print", dest="show", action="store_true")
    ap.add_argument("--only", help="comma-separated filenames to touch")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.show:
        print(BODY)
        return 0

    if a.glob:
        written = 0
        home = Path.home()
        only = {s.strip() for s in a.only.split(",")} if a.only else None
        for rel, marker, who, generic in GLOBAL_TARGETS:
            if only is not None and rel not in only:
                continue
            # Do not create a config dir for an agent this machine does not use.
            marker_dir = home / marker
            if not marker_dir.exists():
                continue
            path = home / rel
            header = CURSOR_HEADER if rel.endswith(".mdc") else ""
            state = remove(path) if a.remove else upsert(path, BODY, header)
            if not a.quiet and state != "absent":
                print(f"  {state:14} {rel}  ({who})")
            if state != "absent" and not generic:
                written += 1
        # The installer needs a machine-readable count: with zero agents found it
        # must not claim the machine is set up.
        print(f"IRONCLAD_AGENTS_WRITTEN={written}")
        return 0

    root = Path(a.project or ".").resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    only = {s.strip() for s in a.only.split(",")} if a.only else None
    targets = [(p, d) for p, d in TARGETS if only is None or p in only]

    for rel, who in targets:
        path = root / rel
        header = CURSOR_HEADER if rel.endswith(".mdc") else ""
        if a.remove:
            state = remove(path)
            if state != "absent" and not a.quiet:
                print(f"  {state:14} {rel}")
        else:
            state = upsert(path, BODY, header)
            if not a.quiet:
                print(f"  {state:14} {rel}  ({who})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
