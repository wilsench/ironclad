---
title: Install
slug: install
group: Start
order: 3
summary: One command, no questions. Then three words to use it. No Python needed.
---

# Install into your agent

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

That is the entire install. No questions, no Python, no menu.

What it does:

1. puts the skill in `~/.agents/skills/ironclad/` — the directory Codex, Cursor,
   opencode and Antigravity read
2. adds an `ironclad` command to `~/.local/bin/`
3. stops. Your repo is untouched.

If `~/.local/bin` is not on your `PATH`, the installer tells you. Add one line to
`~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Then, three commands

```bash
ironclad check          # score this repo's schema, writes nothing
ironclad init           # make it permanent: .agent/ + scripts/
ironclad preset strict  # switch strictness whenever, no reinstall
```

`check` works immediately after install, without `init` — it falls back to the
preset shipped in the skill (`balanced`) until your repo has its own
`.agent/standards.yml`.

## Why install does not need Python

The installer is bash + curl. Python 3.8+ is needed only to **run** the checker,
and `ironclad check` calls it for you.

If the machine has no Python, `ironclad init` still succeeds — only `check`/CI
stay dark until you install it. Do that whenever you are ready to add the gate.

## Other agents

The default is `~/.agents/skills`. For agents with their own directory:

```bash
# Claude Code
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target claude

# Hermes
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target hermes

# opencode (native)
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target opencode

# Antigravity, global
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target gemini

# everything installed on this machine
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --all
```

| Agent | Directory |
|---|---|
| Codex | `.agents/skills/` **inside the repo** — use `--dir .agents/skills` |
| Cursor | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Hermes | `~/.hermes/skills/` |
| opencode | `~/.config/opencode/skills/`, also reads `~/.agents/skills/` |
| Antigravity | `~/.gemini/config/skills/` (global), `.agents/skills/` (workspace) |

> **Codex has no global skill directory.** Per OpenAI's docs, Codex reads
> `$CWD/.agents/skills` and `$CWD/../.agents/skills`. If you use Codex, install
> inside the repo so it travels with the code:
>
> ```bash
> curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --dir .agents/skills
> ```

## If you want the rules to travel with the repo

This is what makes a whole team use the same rulebook — the skill is in git, not
only on one person's laptop:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --dir .agents/skills
git add .agents/skills/ironclad && git commit -m "chore: add ironclad skill"
```

## CI: nothing to skip

There are no prompts in the first place, so there is nothing to suppress. For a
pipeline that wants everything at once:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh \
  | bash -s -- --target agents --project . --preset legacy-friendly
```

## Uninstall

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --uninstall
```

Removes the skill directory and the `ironclad` command. `.agent/` and `scripts/`
in your repo are **not** touched — they are yours, not the installer's.
