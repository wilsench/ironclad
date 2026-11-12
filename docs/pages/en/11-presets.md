---
title: Presets
slug: presets
group: Concepts
order: 11
summary: Three enforcement levels, one automatic default. Set it once at init, change it later with one command.
---

# Presets — guardrails you pick

A rule system with a single strictness gets abandoned. Too soft and it catches
nothing; too hard and the first legacy repo kills it. So enforcement is a setting.

## The three levels

| Preset | Blocks the build | Only warns | For |
|---|---|---|---|
| `legacy-friendly` | — | everything | a repo that already has debt |
| `balanced` **(default)** | DB-01, DB-02, DB-04 | the rest | normal product work |
| `strict` | everything | — | finance, health, anything audited |

Real numbers from the same fixture (`examples/bad.sql`):

```
balanced           errors=3 warns=2
legacy-friendly    errors=0 warns=7
strict             errors=7 warns=0
```

## The automatic default

No prompts. `ironclad init` with no argument uses `balanced`:

```
$ ironclad init
wrote   .agent/standards.yml (preset: balanced)
wrote   .agent/standards.md
wrote   scripts/check_schema.py + scripts/presets/
```

This is deliberate. A command that asks questions hangs in CI and hangs inside an
agent with no TTY — and a command that hangs is worse than one that picks the
wrong option but can be changed (see below).

## Choosing at install

Straight from the installer:

```bash
npx github:wilsench/ironclad#v0.8.2 --project . --preset strict
```

Or later, from inside the repo:

```bash
ironclad init strict
```

## Changing it afterwards

Your choice lives in `.agent/standards.yml` **inside your repo**, not inside the
skill. Three ways to change it, all valid:

**1. Rewrite from a preset:**

```bash
ironclad preset strict
```

**2. Edit it directly — seven lines, reviewable in a PR:**

```yaml
name: balanced
rules:
  DB-01: error      # enum forbidden
  DB-02: error      # magic number on a status column
  DB-03: warn       # status without FK/CHECK
  DB-04: error      # human labels stored as status
  DB-05: warn       # boolean for a non-binary concept
  DB-06: warn       # money as float
  DB-07: warn       # timestamp without a timezone
exceptions: []
```

**3. Per-rule overrides**, when one rule genuinely does not apply:

```yaml
name: balanced
rules:
  DB-06: off        # this service stores cents as integer; no money columns
```

A rule turned `off` is a decision someone made, visible in the diff. That is the
point — not that every rule is on, but that every exception is written down.

## What a preset is not

It is not a maturity badge. Do not move to `strict` because it sounds better.
Move when the finding count is near zero and the team agrees the gate should
hold, not before.

## Writing your own

`assets/presets/*.yml` are plain YAML with the same schema. Copy `balanced.yml`,
change severities, commit it, and point `.agent/standards.yml` at it. The
[extending](/extending/) page covers adding new rule domains.
