---
name: ironclad
description: "Use when several developers share one database — keep status/field choices consistent across the team."
version: 0.4.0
author: Chia Wilsen, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [conventions, database, schema, code-review, team-standards]
    related_skills: [requesting-code-review, codebase-inspection]
---

# Ironclad

**The problem it solves:** two developers on one project, both touching the database, choosing different ways to store the same thing — one writes `status ENUM('paid')`, the other writes `status_code = 2`. Both work. Together they make the project unmaintainable: reports need branches, new code guesses, "how do we add a status?" has two answers, and nobody can say which one is current.

Ironclad makes that choice **once, in a file the repo owns**, so every developer and every agent reads the same answer before writing a line. It ships the policy file (`.agent/standards.md`), a decision procedure the agent follows, and a checker CI can enforce. This skill is the executor, not the rulebook.

The default answer is **integer code + lookup table + foreign key** — not because enums are forbidden, but because adding an integer code is one row of data while adding an enum value is `ALTER TABLE`. If a team chooses otherwise, it must be written down and checked, not assumed. `DB-08` catches the failure this exists to prevent: one project storing status two different ways.

Ships with a worked database policy because that is where teams drift fastest; the same shape extends to any domain via `references/extending.md`.

## Install (one line, any agent)

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash          # ~/.agents/skills
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target claude
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --project .
```

Docs: <https://wilsench.my.id/ironclad/>. Python is not needed to install; only the checker needs it.

## When to Use

- Starting a new app, module, or migration inside the company
- Reviewing someone else's schema or PR against company rules
- A user says "we don't do it that way here" and you need it to hold for every future build
- Don't use for: one-off scripts with no persistence, or repos with no standards file (bootstrap one with `ironclad init` instead)

## Two-Layer Model (this is the whole point)

| Layer | Lives in | Enforced by |
|---|---|---|
| Policy — what the company wants | `.agent/standards.md`, git-versioned | Code review + this skill |
| Mechanism — what a machine can check | `scripts/check_schema.py` | CI, pre-commit, agent before commit |

Never hardcode company rules in this skill. A rule that only exists in a skill does not exist for a new teammate or a new agent, and it will drift. Put it in `.agent/standards.md`, give it an ID (`DB-04`), cite that ID when you report.

## Three Presets, One Default

The guardrail level is a **file in the repo** (`.agent/standards.yml`), not a fact baked into this skill. Default is `balanced`.

| Preset | Blocks | Warns | Use when |
|---|---|---|---|
| `balanced` *(default)* | DB-01, DB-02, DB-04 | DB-03, DB-05, DB-06, DB-07, DB-08 | normal product work |
| `legacy-friendly` | — | all | brownfield repo with existing debt |
| `strict` | all | — | regulated, audit-bearing, finance/health |

```bash
ironclad init                 # balanced, writes .agent/ + scripts/
ironclad check                # uses .agent/standards.yml if present
ironclad preset strict        # switch later, no reinstall
python3 scripts/check_schema.py --list-presets
```

No wizard, nothing to answer: `ironclad init` never prompts, so it is safe to
run from an agent or CI. Switching later = `ironclad preset <name>` or edit
`.agent/standards.yml` directly. Details in `references/presets.md`.

## Procedure

1. **Read the policy, and the existing choice.** `read_file` on `.agent/standards.md`. If missing, run `ironclad init` — it writes both `standards.md` (human) and `standards.yml` (severity config) with the `balanced` preset, and never prompts. Then find out how this project *already* stores status: `grep -rn "status" --include=*.sql --include=*.prisma --include=*.php .` If the project already chose enum or text, follow it and say so — consistency with the codebase beats your preference. Only when nothing exists yet do you apply the default (integer + lookup). Completion: you can name the rule IDs governing the tables you touch, the active preset, and which status style the repo already uses.
2. **Classify every status-like field** using the decision table in `references/database.md` *before* writing DDL. Completion: each field has a written verdict and a one-line reason.
3. **Design the schema** per the verdict — integer code + lookup table + FK + constraint + app-level named constants. Match the style the project already uses; if that style contradicts the policy, flag it once (DB-08) instead of quietly writing a third style.
4. **Write the migration** per the naming rule. No bare integer literal compared against a status field in app code.
5. **Run the checker** — `python3 scripts/check_schema.py <paths> --json`. Exit 0 required. Fix the schema; do not suppress the rule. Downgrading a rule to `warn`/`off` in `.agent/standards.yml` is a reviewed decision, not a shortcut — say so explicitly.
6. **Report with citations.** Every deviation gets a line: rule ID, what you did instead, why. Undocumented deviation is a defect.

## Quick Reference

```
ironclad init                                          # → .agent/standards.{md,yml}
ironclad preset strict                                 # switch the active preset
python3 scripts/check_schema.py . --json               # auto-uses .agent/standards.yml
python3 scripts/check_schema.py . --preset legacy-friendly
python3 scripts/check_schema.py --list-presets
```

Rules: `DB-01` enum in schema, `DB-02` magic number on a status field, `DB-03` status integer with no FK/CHECK, `DB-04` text status column, `DB-05` boolean named for a non-binary concept, `DB-06` money as float, `DB-07` timestamp without timezone, `DB-08` the project mixes status styles (enum in one table, integer in another).

Resolution order for severity: `--config` > `--preset` > `.agent/standards.yml` > built-in `balanced`.

## Verification

- Checker exits 0 on the repo.
- Every status field has a verdict recorded in the PR/report.
- Adding one status value is doable with a single data migration — prove it by writing that migration, not by asserting it.
- `ironclad check` reports no DB-08: the whole project stores status one way, not per table or per developer.
- Agent report cites a rule ID for each deviation.

## Pitfalls

1. **Shipping the skill without the policy file.** Agents then invent rules. Bootstrap `.agent/standards.md` in the same commit.
2. **Treating the skill as enforcement.** A skill advises; a model can ignore it. The checker in CI is what makes standards hold across many programmers.
3. **`CHECK` constraints are the exception, not a violation.** Literal codes inside `CHECK (...)` are correct DDL. The checker tracks paren depth and ignores them — do not "fix" a real constraint to silence a false positive.
4. **Over-constraining at the DB layer while claiming flexibility.** If a `CHECK` hardcodes every legal code, you rebuilt an enum. Validate via FK to the lookup table instead.
5. **Boolean growth.** Confirm a field cannot become 3-state before committing to `boolean`.
6. **Substring-matching status words false-positives.** `mimeType`, `prototype`, `fileType` are not status columns. Match whole segments (`(?<![a-z])type`) and validate the checker against a real repo before trusting it in CI.
7. **Running the checker on legacy code floods the report.** Start report-only, then gate changed files — otherwise the team disables the check outright.
8. **Suppressing the checker to ship.** If a rule is genuinely wrong, change `.agent/standards.md` in review — that is the escape hatch.
9. **Putting the preset in the skill instead of the repo.** A preset chosen in the skill file is invisible to CI and to the next teammate. The active preset must live in `.agent/standards.yml`, committed alongside the code.
10. **Copying the checker without the presets.** `check_schema.py` reads presets from its own `scripts/presets/` when installed into a repo and from `assets/presets/` when running from the skill. Ship only the `.py` and `--preset` dies with `unknown preset`. Use `--with-checker`, which copies both.
11. **`warn` is not a mute button.** A repo that warns on everything forever is a repo with no standard. Either fix the findings or move to a preset where they are errors; say which, in the PR.

## Files

- `references/database.md` — full decision table, worked examples, migration rules
- `references/presets.md` — how the three presets differ, how to write a custom one
- `references/extending.md` — adding a non-database rule domain and checker rule
- `templates/standards.md` — the policy file to copy into a repo
- `assets/presets/balanced.yml` — the default level
- `assets/presets/strict.yml` — everything blocks
- `assets/presets/legacy-friendly.yml` — everything warns
- `scripts/check_schema.py` — SQL / Laravel migration / Prisma linter
- `scripts/init_standards.py` — bootstrap behind `ironclad init`; with `--with-checker` it copies the checker **and** the presets into the target repo (`scripts/presets/`), so `--preset` keeps working after the skill directory is gone
- `bin/ironclad` — the `check` / `init` / `preset` / `status` command the installer links into `~/.local/bin`
