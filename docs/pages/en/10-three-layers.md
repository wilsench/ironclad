---
title: Three layers
slug: three-layers
group: Concepts
order: 10
summary: Why a skill alone is not enough, and a checker alone is not either. Each closes a gap the others cannot.
---

# Three layers

Six months of agent-written schema gives you a museum. Each layer of Ironclad
closes a different hole — drop one and it breaks in a specific, predictable way.

## Layer 1 — the skill (advice, before the fact)

`SKILL.md` is read by the agent when it is about to design a table. It contains a
decision procedure, not just rules:

> *Is this column a status? Then: integer code, lookup table, FK, named constants.*

**What it fixes:** bad decisions never get made. The agent writes the right thing
the first time, which is cheaper than every later layer.

**What it cannot fix:** the agent can skip the skill. It activates by
description match, not by force. An agent that never reads it produces the same
schema it would have produced without you.

## Layer 2 — the policy file (the shared memory)

`.agent/standards.md` lives in your repo and is committed. It is what the agent
reads, and it is also what a new human reads on day one.

**What it fixes:** drift between people and between sessions. Two agents, six
months apart, produce the same schema because they read the same file.

**What it cannot fix:** it is still a document. Nothing stops anyone from
ignoring it.

## Layer 3 — the checker (enforcement, after the fact)

`check_schema.py` reads the SQL, migrations and Prisma schema and fails on
violations. This is the only layer that cannot be talked out of its position.

**What it fixes:** everything the first two layers missed, including commits that
never went through an agent at all.

**What it cannot fix:** it knows what is wrong, not why. A checker with no policy
file produces a wall of rule IDs nobody knows how to satisfy.

## Why all three

| Failure | Caught by |
|---|---|
| agent picks `enum` because the prompt was vague | skill (layer 1) |
| new hire writes an integer status with no lookup table | policy (layer 2) |
| hand-written migration slips past review | checker (layer 3) |
| someone downgrades a rule silently | policy is in git — it shows up in the PR |

## The order matters

The mistake is starting at layer 3. Turning on a checker against an existing repo
produces hundreds of findings, the team mutes it, and the whole thing is dead by
Friday.

Start at layer 1, add layer 2 with `legacy-friendly`, and only then tighten
toward layer 3 as the count drops.

## What is not in the stack

- **Not a formatter.** It has no opinion on spacing.
- **Not a security scanner.** Different problem, different tool.
- **Not a replacement for review.** It is a floor. A human is still the ceiling.
