---
title: Glossary
slug: glossary
group: Start
order: 2
summary: Every technical term in these docs, explained in everyday language. No need to read in order.
---

# Glossary

If a word on another page is unclear, it is probably here. Order does not matter —
this is a reference, not a read-through.

## Basic terms

**Database** — where data lives permanently. If your app dies and restarts, the
data is still there. Think of a giant filing cabinet you can search in a fraction
of a second.

**Table** — one drawer in that cabinet. A `orders` table holds all orders; a
`customers` table holds all customers.

**Column** — one field inside a table. The `orders` table has `order_number`,
`date`, `total`, `status`.

**Row** — one complete record. One order = one row with all its columns filled.

**Schema** — the blueprint of the tables: which tables exist, what columns they
have, what types those columns are. Not the data — the frame. A house plan, not the
furniture.

## Terms that come up when discussing the problem

**Status** — the current state of something. An order can be `new`, `paid`,
`shipped`, `delivered`, `cancelled`. This simple thing is the most common source
of trouble.

**Enum** — a way of storing status as a locked list of choices baked into the
database structure. Adding a new choice means rebuilding structure — and on a
production server that can stop the site from serving for a few minutes. Ironclad
recommends a different approach: see [rule DB-01](/rules/).

**Status code** — storing status as a number, e.g. `1` for `new`, `2` for `paid`.
More flexible, but dangerous when the numbers have no documented meaning.

**Lookup table** — a small table that registers what each code means. It reads like
a dictionary: `1 = new`, `2 = paid`, `3 = shipped`. Its job is to make sure a code
like `7` that was never registered is **rejected** by the database, not silently
accepted.

**Foreign key (FK)** — a rule tying one column to another table. If
`orders.status_code` has an FK to that lookup table, the database refuses to store a
number that is not on the list. This is what makes arbitrary codes like `88` or `99`
safe.

**Migration** — a file containing commands that change the database structure: add a
column, change a type, create a table. Every structural change goes through one, so
it can be replayed on another machine and undone.

**Production** — the server real users use. Its counterparts are **staging** (a copy
for testing) and **local** (your own computer).

## Terms about AI agents

**AI coding agent** — an AI program that can read files, write code, and run
commands on your machine. Examples: Claude Code, Codex, Cursor, opencode,
Antigravity, Hermes.

**Skill** — a package of instructions an agent reads when working on a specific
task. It is a folder containing `SKILL.md`. Not a program, not a plugin — just text
that gets read.

**Repo (repository)** — a project folder tracked by git, along with its change
history. "In your repo" means in your project folder.

**Commit** — saving changes into the git history, with a note on why.

**Pull request (PR)** — a proposed change that needs someone's approval before it
joins the main code. This is where automated checks usually live.

**CI (Continuous Integration)** — a robot that runs automated checks whenever a pull
request appears. If something violates a rule, the PR is marked red and cannot be
merged.

**Pre-commit hook** — a check that runs on your machine **before** the commit is
saved. Faster than waiting for CI, because the mistake surfaces while you still
remember what you were writing.

**TTY** — the term for "a terminal held by a human". A command that asks questions
needs a TTY; inside CI or inside an agent there is none, so such a command hangs.
Ironclad never asks, for exactly this reason.

**PATH** — the list of folders the system searches for commands. If you see
`ironclad: command not found`, the folder it was installed into is not on that list.

## Ironclad-specific terms

**Preset** — how hard the rules bite. Four exist:

- `legacy-friendly` — everything is a warning, the build never fails. For an old
  repo that already has problems.
- `coherence` — no style is punished; only **mixing** styles fails. For anyone who
  does not want a style imposed.
- `balanced` — the most dangerous patterns block, the rest warn. This is the default.
- `strict` — everything blocks. For a new or already-clean repo.

**Mode** — who decides when the repo has no answer yet. `ask` (default): the agent
asks. `house`: the agent applies the office default. Difference from a preset: a
mode acts **before** code is written, a preset acts **after**.

**Rule ID** — a rule's number, e.g. `DB-04`. It makes discussion short: "this breaks
DB-04" beats a paragraph of explanation.

**Checker / linter** — a program that reads code and points at rule violations. It
does not fix anything; it only points.

**Gate** — a check that **blocks**. The difference from a warning: a warning can be
ignored, a gate cannot.

**Finding** — one violation the checker found, with file name and line number.

**Exit code** — the number a program returns when it finishes. `0` means clean, `1`
means violations, `2` means the command was misused. CI robots read this number,
not the prose.

## Questions that keep confusing people

**"Why two commands? Isn't one better?"**
The first installs the tool on your machine. The second applies it to one specific
project. One machine can hold ten projects with different rules.

**"What is the difference between the skill and the checker?"**
The skill is the rulebook the AI reads. The checker inspects the work afterwards.
The first prevents, the second catches.

**"If the checker exists, why still the skill?"**
Because the checker only speaks after the code is written. The skill makes the AI
write the right thing the first time — far cheaper than fixing it.

**"Does this change my code?"**
No. `ironclad check` only reads. `ironclad init` adds four new files and touches
nothing that already exists.

**"Is my data sent anywhere?"**
No. Everything runs locally. The installer downloads files once, then stops.

**"If I don't understand the technical terms, can I still use this?"**
Yes, for installation — two commands, nothing to answer. For choosing a preset,
bring in whoever writes the code. See [If you are not the one writing
code](/overview/#if-you-are-not-the-one-writing-code).
