# Ironclad

**Your team's engineering rules, enforced by the agent — not by memory.**

A skill for AI coding agents. Ten people vibe-code the same app, nobody reads the same wiki, and six months later the schema is a museum of individual taste. Ironclad gives every agent the same rulebook, the same decision procedure, and a linter that fails the build when someone drifts.

Ships a worked database policy as the headline example — **integer codes + lookup table + FK, not `enum`** — because that is the drift that hurts most and shows up latest.

## One command

```bash
# Hermes
hermes skills install <owner>/ironclad/skills/ironclad

# Claude Code / Codex / Cursor / any SKILL.md agent
curl -fsSL https://raw.githubusercontent.com/<owner>/ironclad/main/install.sh | bash
```

The installer auto-detects `~/.hermes`, `~/.claude`, or `~/.agents`, or takes `--target hermes|claude|agents` / `--dir /path/to/skills`. Format is [agentskills.io](https://agentskills.io/specification), so it is not Hermes-only.

## Then, in your repo

```bash
python3 scripts/init_standards.py . --with-checker   # asks which strictness, default pre-picked
python3 scripts/check_schema.py . --json             # exit 0 or it fails CI
```

## Strictness is a setting, not a hardcoded opinion

Pick a level **once**, at install. The choice lands in `.agent/standards.yml` inside your repo — committed, reviewable, changeable later with no reinstall.

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

Or just edit `.agent/standards.yml` — seven lines, `error` / `warn` / `off`. See [presets.md](skills/ironclad/references/presets.md).

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

## Why `00` is not the answer

If "empty stock = 00" is the plan: `00` in an integer column is just `0`. Two-digit form is display formatting, never storage. What you want is a named constant plus a lookup table:

```ts
const STOCK = { EMPTY: 0, LOW: 1, AVAILABLE: 2, RESERVED: 3 } as const;
```

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
