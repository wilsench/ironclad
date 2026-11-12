---
title: Overview
slug: overview
group: Start
order: 1
summary: Ironclad gives every AI coding agent the same rulebook, plus a linter that enforces it in CI.
---

# Ironclad

Engineering rules decay the moment they live in a wiki. Ten people vibe-code the
same app, nobody reads the same page, and six months later the schema is a museum
of individual taste: three different ways to store "status", money as a float,
timestamps without a timezone.

Ironclad is the answer to that, in three layers:

1. **A skill** every AI coding agent reads before it writes DDL.
2. **A policy file** in your repo — `.agent/standards.md` — so the rules are
   reviewable, diffable, and the same for the agent and the human.
3. **A checker** — `check_schema.py` — that fails CI when someone drifts.

The skill is advice. The checker is enforcement. You need both, because an agent
that only has advice will eventually ignore it, and a checker with no advice
produces violations nobody knows how to fix.

## Who this is for

Teams where an AI agent writes a meaningful share of the schema, and where
"we'll clean it up later" has already been said three times.

It is not a style guide for formatting. It is a small set of decisions that are
expensive to reverse — `enum` columns, status stored as prose, money as `float`,
naive timestamps — each with a preferred alternative.

## The one opinion that matters

Status is data, and data belongs in a table with a foreign key, not in a column
type that needs `ALTER TABLE` to change.

```sql
-- what an agent writes when nobody stops it
status ENUM('pending', 'paid', 'shipped')

-- what you want instead
status_code smallint NOT NULL REFERENCES order_status(code)
```

The knife cuts both ways: you are free to pick any code you like — `88`, `99`,
`990` — as long as the number is registered in the lookup table and guarded by a
foreign key. The database rejects unknown codes; the app uses named constants
instead of bare `if (status === 88)`.

See [Rules](/rules/) for all seven.

## What it deliberately does not do

- **No GUI.** Rules live in YAML and Markdown, in your repo.
- **No cloud service.** The checker is a Python script. It runs offline.
- **No formatting opinions.** Use Prettier, Biome, Pint — whatever you already use.
- **No autofix.** Fixing a schema is a design decision, not a regex.

## The honest limits

- The checker is regex-based, not a SQL parser. It can produce false positives
  and it will miss things a human reviewer would catch. It is a floor, not a
  ceiling — a human is still the last layer.
- There is no automatic update mechanism yet. Re-run the installer to upgrade.
- It knows seven rules about databases. It is not a security scanner.

## Where to go

- [Install](/install/) — one command, no Python, no questions
- [Quickstart](/quickstart/) — from zero to a green checker in two minutes
- [Presets](/presets/) — pick how hard the rules should bite
- [Rules](/rules/) — what it actually checks
