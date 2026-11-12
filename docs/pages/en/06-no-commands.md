---
title: Using it without commands
slug: no-commands
group: Start
order: 6
summary: Three steps. After that you run nothing — the agent asks and does the checking.
---

# Using it without commands

If you do not want to remember commands, this is the path. Three steps, once, and
you are done.

## 1. Install

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

## 2. Done — actually done

After step 1 there is **no second step**. The installer already wrote the rules into
each agent's global config on this machine:

```
created  .claude/CLAUDE.md     (Claude Code)
created  .codex/AGENTS.md      (Codex)
created  .gemini/GEMINI.md     (Gemini CLI)
```

That is what the agent reads **at the start of every session, in any repo** — with
nothing for you to run.

## 3. Optional: pin the rules per repo

If you want the rules committed so every teammate and CI share the same answer, run
this once per repo:

```bash
cd your-repo
ironclad init
```

It asks one question:

```
How strict should this repo be?
  1) balanced  (default) — enum and text status block, the rest warn
  2) strict    — everything blocks; use for new or clean repos
  3) legacy-friendly — everything warns; use for an old repo with debt
Choose 1-3 [1]:
```

Then writes:

```
wrote   .agent/standards.yml      ← this repo's rules (reviewable in a PR)
wrote   .agent/standards.md       ← the explanation, for humans and agents
wrote   scripts/check_schema.py   ← the checker CI can run

  created        AGENTS.md                             (Codex, opencode, etc.)
  created        CLAUDE.md                             (Claude Code)
  created        GEMINI.md                             (Gemini CLI)
  created        .cursor/rules/ironclad.mdc            (Cursor)
  created        .github/copilot-instructions.md       (GitHub Copilot)
```

Then commit:

```bash
git add .agent scripts AGENTS.md CLAUDE.md GEMINI.md .cursor .github
git commit -m "chore: adopt ironclad standards"
```

That last part is the trick. The agent **reads those files by itself** every time
you open the repo — no instruction from you, no slash command, no skill to
activate.

Without `ironclad init` the agent still asks and still uses the `balanced` default
from the skill. You only lose two things: the rules are not in git, and CI has no
file to run.

## 4. Work as usual

Open your agent, ask for any feature that touches the database. What happens:

> **You:** add an order feature: orders table with status, total, created time
>
> **Agent:** Ironclad: enforce the rules while we write, or check at the end?

Pick one and it proceeds:

- **while** — rules applied as it writes, `ironclad check` run on each file before
  reporting it done.
- **end** — it writes first, then checks before finishing and fixes everything
  reported.

You type no commands. The agent runs them.

## Why this works

A skill is only loaded when the agent judges it relevant — and that judgement
often comes too late: the code is written before the skill is read. Files like
`AGENTS.md` and `CLAUDE.md` are different: they are read **every session, up
front**, before the agent answers anything.

What goes into those files:

- when the rules apply (any schema change, Laravel and Prisma included)
- the question to ask first, and the choices
- the eight rules in one paragraph
- the ban on silencing the checker to get a green build
- the obligation to cite a rule ID when deviating

## Choosing a preset without being asked

```bash
ironclad init strict
ironclad init legacy-friendly
```

The default is `balanced`, and the agent still asks which preset to use when
`.agent/` is missing — it does not pick silently.

## If you do not want AGENTS.md touched

```bash
ironclad init --no-agent-files
```

Or at install time: `curl ... | bash -s -- --no-agent-files`.

Without that block the agent only knows the rules if it loads the skill — so you
are back to a world that needs commands. The option exists for repos that already
maintain their own `AGENTS.md` and do not want it edited.

## Removing just that block

```bash
ironclad attach . --remove
```

Only the block marked `<!-- ironclad:begin v1 -->` is removed. Your own text in
the same file is untouched. Tested: a `CLAUDE.md` holding office rules survives
intact after the Ironclad block is pulled out.
