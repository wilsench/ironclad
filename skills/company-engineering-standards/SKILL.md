---
name: company-engineering-standards
description: "Enforce company DB and app conventions on every build."
version: 0.2.0
author: Chia Wilsen, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [conventions, database, schema, code-review, team-standards]
    related_skills: [requesting-code-review, codebase-inspection]
---

# Company Engineering Standards Skill

Makes an agent build software the way *this company* builds it, not the way the model personally prefers. Ships a policy file the repo owns, a decision procedure the agent follows, and a checker that CI can enforce. The rules live in the repo (`.agent/standards.md`) — this skill is the executor, not the rulebook.

Ships with a worked database policy (integer codes over enums) because that is where teams drift fastest; the same shape extends to any domain via `references/extending.md`.

## When to Use

- Starting a new app, module, or migration inside the company
- Reviewing someone else's schema or PR against company rules
- A user says "we don't do it that way here" and you need it to hold for every future build
- Don't use for: one-off scripts with no persistence, or repos with no standards file (bootstrap one with `scripts/init_standards.py` instead)

## Two-Layer Model (this is the whole point)

| Layer | Lives in | Enforced by |
|---|---|---|
| Policy — what the company wants | `.agent/standards.md`, git-versioned | Code review + this skill |
| Mechanism — what a machine can check | `scripts/check_schema.py` | CI, pre-commit, agent before commit |

Never hardcode company rules in this skill. A rule that only exists in a skill does not exist for a new teammate or a new agent, and it will drift. Put it in `.agent/standards.md`, give it an ID (`DB-04`), cite that ID when you report.

## Procedure

1. **Read the policy.** `read_file` on `.agent/standards.md`. If missing, run `python3 scripts/init_standards.py` to bootstrap `templates/standards.md` into the repo, then tell the user to review it. Completion: you can name the rule IDs governing the tables you are about to touch.
2. **Classify every status-like field** using the decision table in `references/database.md` *before* writing DDL. Completion: each field has a written verdict and a one-line reason.
3. **Design the schema** per the verdict — integer code + lookup table + FK + constraint + app-level named constants.
4. **Write the migration** per the naming rule. No bare integer literal compared against a status field in app code.
5. **Run the checker** — `python3 scripts/check_schema.py <paths> --json`. Exit 0 required. Fix the schema; do not suppress the rule.
6. **Report with citations.** Every deviation gets a line: rule ID, what you did instead, why. Undocumented deviation is a defect.

## Quick Reference

```
python3 scripts/init_standards.py .              # bootstrap .agent/standards.md
python3 scripts/check_schema.py . --json         # whole repo
python3 scripts/check_schema.py database/migrations --strict
```

Checker rules: `DB-01` enum in schema, `DB-02` magic number on a status field, `DB-03` status column with no lookup/FK (strict), `DB-04` text status column, `DB-05` boolean named for a non-binary concept.

## Verification

- Checker exits 0 on the repo.
- Every status field has a verdict recorded in the PR/report.
- Adding one status value is doable with a single data migration — prove it by writing that migration, not by asserting it.
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

## Files

- `references/database.md` — full decision table, worked examples, migration rules
- `references/extending.md` — adding a non-database rule domain and checker rule
- `templates/standards.md` — the policy file to copy into a repo
- `scripts/check_schema.py` — SQL / Laravel migration / Prisma linter
- `scripts/init_standards.py` — policy bootstrap
