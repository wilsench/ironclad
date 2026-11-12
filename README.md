# Ironclad

**Your team's engineering rules, enforced by the agent — not by memory.**

A skill for AI coding agents. Ten people vibe-code the same app, nobody reads the same wiki, and six months later the schema is a museum of individual taste. Ironclad gives every agent the same rulebook, the same decision procedure, and a linter that fails the build when someone drifts.

Ships a worked database policy as the headline example — **integer codes + lookup table + FK, not `enum`** — because that is the drift that hurts most and shows up latest.

## Install

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

No questions, no Python. It puts the skill where your agent looks and adds an
`ironclad` command to `~/.local/bin`.

Then, in any repo:

```bash
ironclad check          # verdict in a second, writes nothing
ironclad init           # make it permanent — writes .agent/ + scripts/
ironclad preset strict  # switch strictness later, no reinstall
```

`init` writes `.agent/standards.md`, `.agent/standards.yml`,
`scripts/check_schema.py`, and `scripts/presets/`. Commit all four — otherwise
the next teammate gets a different rulebook. From then on the agent reads the
policy before writing DDL, and CI reads the same file to decide what blocks.

Python 3.8+ is needed only to *run* the checker; `check` calls it for you.

**Targets:** `agents` (Codex, Cursor, opencode, Antigravity — default), `claude`, `hermes`, `gemini`, `opencode`, or `--all`. Docs: <https://wilsench.my.id/ironclad/>

Format is [agentskills.io](https://agentskills.io/specification), so the same
folder works in Hermes, Claude Code, Codex, Cursor, opencode, and Antigravity.
Hermes users can also install through the hub:

```bash
hermes skills install wilsench/ironclad/skills/ironclad
```

## Strictness is a setting, not a hardcoded opinion

`ironclad init` defaults to `balanced`. The choice lands in `.agent/standards.yml` inside your repo — committed, reviewable, changeable later with `ironclad preset`, no reinstall.

| Preset | Blocks the build | Only warns | For |
|---|---|---|---|
| `legacy-friendly` | — | everything | a repo that already has debt |
| `balanced` **(default)** | DB-01, DB-02, DB-04 | the rest | normal product work |
| `strict` | everything | — | finance, health, anything audited |

The wizard pre-selects `balanced`, and non-interactive installs fall back to it silently — so an agent never blocks on a question it cannot ask. Switch whenever:

```bash
python3 scripts/init_standards.py . --preset strict --force
python3 scripts/check_schema.py . --preset legacy-friendly   # one-off, no file change
python3 scripts/check_schema.py --list-presets
```

Or just edit `.agent/standards.yml` — one line per rule, `error` / `warn` / `off`. See [presets.md](skills/ironclad/references/presets.md).

## Why three layers

| Layer | File | Enforced by |
|---|---|---|
| Policy — what the team wants | `.agent/standards.md` | Code review |
| Procedure — how the agent decides | `SKILL.md` + `references/` | The agent |
| Mechanism — what a machine checks | `scripts/check_schema.py` | CI / pre-commit |

A skill alone is advice; a model can ignore advice. The checker is what actually holds twenty programmers to one standard. Install both, then wire the checker into CI.

## Rules

```
DB-01  no native enum in schema (unless justified in the migration comment)
DB-02  no magic numbers compared against status fields
DB-03  status integer must carry a FK or CHECK
DB-04  never store a human label as the status
DB-05  boolean only for genuine binaries
DB-06  money as bigint minor units + currency, never float
DB-07  timestamps carry a timezone
DB-08  one project stores status one way (no enum table beside an integer table)
```

## Verified, not asserted

Same fixture, three presets — this is the actual output:

```
$ check_schema.py examples/bad.sql --preset balanced
[DB-01] ERROR  enum column
[DB-04] ERROR  status stored as text (`stock_state`)
[DB-03] warn   `status_code` has no FK or CHECK
[DB-05] warn   `is_status` is not a binary concept
→ exit 1

$ check_schema.py examples/bad.sql --preset legacy-friendly
→ exit 0   (4 warnings, nothing blocks)

$ check_schema.py examples/good.sql --preset strict
→ exit 0   (integer + lookup table + FK + CHECK)
```

## Honest limitations

- The checker is **regex-based**, not a real SQL/Prisma parser. It reads SQL DDL, Laravel migrations, and Prisma schema. It does not see your ORM's query builder, runtime-built SQL, or TypeScript types.
- It will not catch a status field that is *semantically* wrong but syntactically fine. A human reviewer is still the last line.
- Run it report-only first, then gate changed files. Gating an entire legacy repo on day one is how the check gets deleted from CI by lunch.

## Arbitrary codes are fine — undocumented codes are not

`88` for "empty stock", `99` for "departed" — that works, and this skill does not fight it. Integer codes are exactly what the policy asks for. Two things make it safe:

```sql
INSERT INTO stock_state (code, label) VALUES (88, 'empty'), (89, 'low'), (90, 'available');
--                        ^ single source of truth: the DB rejects 87
```

```ts
const STOCK = { EMPTY: 88, LOW: 89, AVAILABLE: 90 } as const;   // no bare 88 in app code
```

The gaps are the point — reserve `8x` for stock states, `9x` for departure states, and the number carries meaning to a human reading a query six months later. What the checker blocks is the *bare literal*: `if (status === 88)` scattered through the codebase. That is the same number with no name, no foreign key, and no reviewer.

## Repo layout

```
skills/ironclad/
├── SKILL.md                  # procedure + pitfalls
├── references/
│   ├── database.md           # decision table, worked SQL/TS/PHP
│   ├── presets.md            # strictness levels, custom presets
│   └── extending.md          # adding API-/SEC- rule domains
├── templates/standards.md    # policy file for your repo
├── assets/presets/*.yml      # balanced · legacy-friendly · strict
└── scripts/
    ├── check_schema.py       # SQL / Laravel / Prisma linter
    └── init_standards.py     # wizard + bootstrap
```

Publishing your own fork: `./scripts/set-repo-owner.sh <username>`, then follow [PUBLISH.md](PUBLISH.md).

## License

MIT

