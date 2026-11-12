# Presets — the adjustable guardrail

The skill ships one default and two alternatives. The active choice lives in the **repo**, not in the skill, so CI and every teammate read the same setting.

## Where the setting lives

```
your-repo/
└── .agent/
    ├── standards.md    # human-readable policy, rule IDs, the "why"
    └── standards.yml   # machine-readable severities — this is the dial
```

`standards.yml` is committed. Changing the guardrail level is a one-line PR, reviewable like any other decision.

The shipped presets live in the skill at `assets/presets/` (Hermes only bundles `references/`, `templates/`, `scripts/`, `assets/`, and `examples/` — a top-level `presets/` folder would silently fail to install).

## The four presets

| Preset | Errors (block the build) | Warnings | Choose when |
|---|---|---|---|
| `legacy-friendly` | none | DB-01…DB-08 | repo already has debt; you want visibility, not a wall |
| `coherence` | DB-08 | DB-01…DB-07 | you have no business imposing a style — only mixed styles fail |
| `balanced` **(default)** | DB-01, DB-02, DB-04 | DB-03, DB-05…DB-08 | normal product work — the safe starting point |
| `strict` | DB-01…DB-08 | none | finance, health, anything audited; a migration is a compliance event |

`coherence` is the preset for a stranger: an enum repo that is internally consistent
passes, and the only hard failure is two styles for one concept (DB-08). Its DB-08
message also drops the "integer is the default" hint, because that hint is exactly the
imposition this preset exists to avoid.

Every preset can be auto-selected or overridden at runtime:

```bash
python3 scripts/init_standards.py .                       # wizard, balanced pre-selected
python3 scripts/init_standards.py . --preset strict --yes # scripted
python3 scripts/init_standards.py . --preset strict --force  # switch later

python3 scripts/check_schema.py . --preset legacy-friendly   # one-off, no file change
python3 scripts/check_schema.py . --config path/to/custom.yml
python3 scripts/check_schema.py --list-presets
```

## Severity resolution order

```
--config  >  --preset  >  .agent/standards.yml (auto-discovered, walks up)  >  built-in balanced
```

Precedence means a developer can check a legacy branch without editing the repo config, and CI can pin the committed config without anyone passing flags.

## Writing a custom preset

Copy a shipped preset and edit the dial. Everything is additive — you list only what you want to change.

```yaml
name: our-team
title: Our team — balanced plus audit rules
rules:
  DB-01: error
  DB-02: error
  DB-03: warn
  DB-04: error
  DB-05: off          # we accept is_status; tracked separately
  DB-06: error        # money bugs cost real money
  DB-07: error
exceptions:           # paths skipped entirely (substring match, one per line)
  - migrations/legacy
  - vendor/our-legacy-bundle
boolean_allowlist:    # DB-05 never fires on these names
  - is_active
  - is_deleted
  - is_status
```

Allowed severities: `error`, `warn`, `off`.

## Choosing well (honest guidance)

- **Start one notch softer than you think you need.** A checker that fails 400 findings on day one gets deleted from CI. `legacy-friendly` first, then `balanced` once the baseline is clean.
- **`warn` is a budget, not a lifestyle.** Track the count. If it only goes up, the setting is hiding a problem — move those rules to `error` or fix them.
- **Don't fork the checker per team.** Presets exist so one checker serves all of them; forked scripts drift and nobody knows which one CI runs.
- **`strict` in a greenfield repo is cheap.** There is no legacy to fight, so paying the constraint cost up front is usually cheaper than a later migration.
