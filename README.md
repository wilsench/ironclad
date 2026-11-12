# Ironclad

**Make the AI agent understand that the database belongs to the team — not to it.**

A skill for AI coding agents. Two developers, one database: one stores status as
`ENUM('paid')`, the other as `status_code = 2`. Both pass review. Six months later
reports need a branch per table, new code has to guess, and nobody can say which is
current.

Ironclad changes one thing: before an agent writes anything that stores status, it
**asks which way this project does it, and reads the codebase to check** — instead of
quietly adding a second style.

**It is not a style guide.** There is no house rule about how to write a query, and
you do not have to adopt one. If you want your team's answer written down and checked
automatically, the repo ships that as optional tooling; if you only wanted the
understanding, the install is enough.

## Install

```bash
npx github:wilsench/ironclad#v0.8.5
```

Same installer without Node:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

No questions, no second step. It puts the skill where your agent looks, adds an
`ironclad` command to `~/.local/bin`, and writes the rule block into each agent's
**global** config (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`,
`~/.cursor/rules/`, `~/.config/opencode/AGENTS.md`, `~/.agents/AGENTS.md`) — only for
agents whose config directory already exists.

That last part is why there is nothing else to do: the agent reads it at the start of
every session, in any repo, and asks **"which way does this project store status —
follow the codebase, or check with the team first?"** before touching schema.

Optional, once per repo, to record your project's decision in git:

```bash
ironclad init           # writes .agent/standards.md — a decision record
ironclad check          # does this repo store status more than one way?
ironclad preset strict  # severity levels, if you use the checker
```

`init` writes `.agent/standards.md` (the decision record) plus, if you use the
checker, `.agent/standards.yml`, `scripts/check_schema.py`, and `scripts/presets/`.
Commit them — otherwise the next teammate reads a different answer.

**Needs Python 3.8+** (preinstalled on macOS, most Linux, Termux) to write the block
and to run the checker. Without `python3` the installer exits 3 and tells you how to
install it, instead of claiming success with nothing written. `--no-agent-files`
installs the skill alone.

**Targets:** `agents` (Codex, Cursor, opencode, Antigravity — default), `claude`, `hermes`, `gemini`, `opencode`, or `--all`. Docs: <https://wilsench.my.id/ironclad/>

Format is [agentskills.io](https://agentskills.io/specification), so the same
folder works in Hermes, Claude Code, Codex, Cursor, opencode, and Antigravity.
Hermes users can also install through the hub:

```bash
hermes skills install wilsench/ironclad/skills/ironclad
```

## Optional: the checker

Everything below is for teams that want machine-checked consistency. None of it is
required for the agent to understand the problem, and a repo that skips it is not
"wrong" — it just has no automated record.

`ironclad init` defaults to `balanced`. The choice lands in `.agent/standards.yml`
inside your repo — committed, reviewable, changeable later with `ironclad preset`,
no reinstall.

| Preset | Blocks the build | Only warns | For |
|---|---|---|---|
| `legacy-friendly` | — | everything | a repo that already has debt |
| `balanced` **(default)** | DB-01, DB-02, DB-04 | the rest | normal product work |
| `strict` | everything | — | finance, health, anything audited |

`init` asks which level once, when a human is at the terminal, and stays silent in CI. Switch whenever:

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
DB-06  money exact (`numeric` fixed scale or bigint minor units), never float
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
    └── init_standards.py     # bootstrap
```

Publishing your own fork: `./scripts/set-repo-owner.sh <username>`, then follow [PUBLISH.md](PUBLISH.md).

## License

MIT

