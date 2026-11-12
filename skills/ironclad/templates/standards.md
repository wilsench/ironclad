# How we store status

> Decision record, not a rulebook. One question: **how does this project store
> status, and why.** Agents read this before writing schema so they follow the
> project instead of inventing a second style.

## The decision

Status is stored as an **integer code + lookup table + foreign key**:

```sql
status_code SMALLINT NOT NULL REFERENCES order_status(code)
```

Codes step by 10 (10, 20, 30) and are never reused. Names live in application
constants, not as bare numbers in queries.

Adopted: 2026-11-12 · Default for new tables in this team's projects.

## Why

Two developers storing the same concept two ways is the failure this prevents. An
integer code with a foreign key makes an invalid status impossible to insert — the
database rejects it. A native enum cannot drop or rename a value without a table
rewrite, and a text column with a CHECK lets typos reach production until someone
adds the constraint.

## Where it lives

| Table | Column | Type |
|---|---|---|
| any table with a status | `status_code` | `smallint NOT NULL` |
| `<entity>_status` | `code` | `smallint PRIMARY KEY` |
| `<entity>_status` | `label` | `text NOT NULL` |

Label the lookup rows in the migration that creates them, or in a seeder if the
rows are expected to change without a deploy.

## When an existing repo disagrees

A repo that already stores status another way keeps doing so. Consistency inside a
project beats consistency with this document — rewriting a working schema to match
a default is how you lose a weekend and gain a bug. If a repo has two styles at
once, that is a decision to make deliberately, not drift into.

## What this does not cover

Money (integer minor units), timestamps (`timestamptz`), and naming conventions are
separate decisions. This file answers only the status question.
