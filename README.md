# company-engineering-standards

A Hermes Agent skill that makes AI coding agents build software to *your* company's conventions instead of the model's defaults.

Ships a worked policy for the most common drift point: database status fields. The default position is **integer codes + lookup table + FK**, not `enum` — because enums cannot be extended without a deploy and cannot be dropped or reordered at all in Postgres.

## Install

```bash
# One skill, no tap required
hermes skills install <owner>/company-standards-skill/skills/company-engineering-standards

# Or subscribe to the whole repo as a tap
hermes skills tap add <owner>/company-standards-skill
hermes skills install company-standards-skill/company-engineering-standards
```

Works with any agent that reads the [agentskills.io](https://agentskills.io/specification) `SKILL.md` format, not just Hermes.

## What it actually does

Three layers, and you need all three:

| Layer | File | Who enforces it |
|---|---|---|
| Policy — what the company wants | `.agent/standards.md` in *your* repo | Code review |
| Procedure — how the agent decides | `SKILL.md` + `references/` | The agent |
| Mechanism — what a machine checks | `scripts/check_schema.py` | CI / pre-commit |

A skill alone is advice; a model can ignore it. The checker is what makes standards hold across twenty programmers. Install the skill, then wire the checker into CI.

## Quick start

```bash
# 1. Bootstrap the policy file into your repo
python3 scripts/init_standards.py . --with-checker

# 2. Review .agent/standards.md and delete rules you don't hold

# 3. Check
python3 scripts/check_schema.py . --json
```

## The rule it enforces

```
DB-01  no native enum in schema (unless justified in the migration comment)
DB-02  no magic numbers compared against status fields
DB-03  status integer must carry a FK or CHECK
DB-04  never store a human label as the status
DB-05  boolean only for genuine binaries
```

## Verified behaviour

```
$ python3 scripts/check_schema.py examples/bad.sql examples/bad_migration.php --strict
examples/bad.sql:4:  [DB-01] SQL/prisma enum column; ...
examples/bad.sql:5:  [DB-05] `is_status` is not a binary concept; ...
examples/bad.sql:6:  [DB-04] status stored as text (`stock_state`); ...
examples/bad.sql:11: [DB-03] `status_code` has no FK to a lookup table ...
examples/bad_migration.php:7: [DB-01] Laravel $table->enum(); ...
examples/bad_migration.php:8: [DB-04] status stored as text (`departure_status`); ...

$ python3 scripts/check_schema.py examples/good.sql --strict
1 file(s), 0 violation(s)     # integer + lookup + FK + CHECK
```

## Honest limitations

- The checker is **regex-based**, not a real SQL/Prisma parser. It understands SQL DDL, Laravel migrations, and Prisma schema. It does not understand your ORM's query builder, raw query strings built at runtime, or TypeScript types.
- It will not catch a status field that is *semantically* wrong but syntactically fine.
- Run it report-only first, then gate changed files. Gating a legacy repo on day one is how teams end up disabling the check.

## Why `00` is not the answer

If "empty stock = 00" is your plan: `00` in an integer column is just `0`. The two-digit form is display formatting, never storage. Storing `00` means a string column (worse than an enum) or a precision that disappears the moment someone sums the column. What you actually want is a named constant plus a lookup table:

```ts
const STOCK = { EMPTY: 0, LOW: 1, AVAILABLE: 2, RESERVED: 3 } as const;
```

## License

MIT
