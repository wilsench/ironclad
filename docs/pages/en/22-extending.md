---
title: Extending
slug: extending
group: Reference
order: 22
summary: Adding a new rule domain — API, security, performance — without touching the database rules that already work.
---

# Extending

The seven database rules are one domain. Nothing in the design assumes it is the
only one, or that it is permanent.

## Adding a rule to an existing domain

1. **Pick the next free ID.** Database rules are `DB-01`…`DB-07`, so the next one
   is `DB-08`. Never reuse a retired number.
2. **Add the check** in `scripts/check_schema.py`. One function, one rule ID.
3. **Add a fixture** that violates it — `examples/bad_<topic>.sql` — and a
   passing counterpart.
4. **Set the severity per preset** in all three files in `assets/presets/`. A new
   rule with no entry in `strict.yml` is a rule that silently does not apply.
5. **Document it** in `references/database.md` and in the docs `rules` page.
6. **Run every fixture against every preset** before committing:

```bash
for p in balanced strict legacy-friendly; do
  for f in examples/*.sql; do
    python3 scripts/check_schema.py "$f" --preset "$p" >/dev/null
    echo "$f $p → $?"
  done
done
```

## Adding a whole new domain

Use a different prefix and keep the same shape: `API-01`, `SEC-01`, `PERF-01`.

```
skills/ironclad/
├── SKILL.md
├── references/
│   ├── database.md
│   ├── api.md          ← new domain rationale
│   └── security.md
├── scripts/
│   ├── check_schema.py
│   └── check_api.py    ← new domain checker
├── assets/presets/
│   ├── balanced.yml    ← add API-01: warn, SEC-01: error
│   └── ...
└── templates/standards.md
```

Two rules for new domains:

- **Separate checkers, shared config.** One script per domain. A team that cares
  about API rules and not security should be able to run one without the other.
- **One ID namespace per domain.** `SEC-01` must never collide with `DB-01`, and
  the prefix must tell you which file to open.

## What makes a rule worth adding

A rule earns its place when it is:

1. **deterministic** — same input, same verdict, no model in the loop
2. **cheap to check** — a regex or an AST walk, not a build
3. **expensive to reverse** — a schema decision, not a formatting preference

Formatting belongs in a formatter. Style belongs in a linter with autofix. Ironclad
is for decisions that reach production and stay there.

## What not to add

- rules that need a running database
- rules that depend on another repository's state
- rules that require reading application intent ("is this status meaningful?")
- anything with "sometimes" in the description

## Changing the skill itself

`SKILL.md` is the contract an agent follows. If you add a rule that the agent
should apply *before* writing DDL, it must appear in both:

1. `references/<domain>.md` — the reasoning
2. the **Procedure** section of `SKILL.md` — the step the agent executes

A rule documented only in `references/` will be read only if the agent feels like
it. The procedure section is what gets followed.
