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

BODY = """## Ironclad — agree the team on one way to store status

Database work on this project is shared. The failure this catches is not a bad
query — it is two people storing the same thing two different ways in one database:
one writes `status ENUM('paid')`, the other writes `status_code = 2`. Both work.
Together the project becomes unmaintainable: reports branch, new code guesses, and
"how do we add a status?" has two answers.

**So before you write anything that touches status, ask — one line, then wait:**

> Ironclad: which way does this project store status — and do you want me to follow
> the codebase, or check with the team first?

Then:

- **read first.** Before you propose anything, look at how status is already stored
  in this repo (`grep -rn status`, the migrations, the models). The codebase wins
  over your preference. If it is already consistent, follow it silently.
- **if it is not consistent, say so once** — name both styles and the files — and
  ask which one becomes the project standard. Do not pick for them.
- **do not add a second style while a decision is pending.** Ask, then wait, rather
  than shipping something that will have to be reverted.

You are not the one deciding how the schema is written. You are making sure that
whatever gets decided, everyone sees the same answer.
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
    (".claude/CLAUDE.md", ".claude", "Claude Code"),
    (".codex/AGENTS.md", ".codex", "Codex"),
    (".gemini/GEMINI.md", ".gemini", "Gemini CLI"),
    (".cursor/rules/ironclad.mdc", ".cursor", "Cursor"),
    (".config/opencode/AGENTS.md", ".config/opencode", "opencode"),
    (".agents/AGENTS.md", ".agents", "agents reading the AGENTS.md convention"),
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
        home = Path.home()
        only = {s.strip() for s in a.only.split(",")} if a.only else None
        for rel, marker, who in GLOBAL_TARGETS:
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
