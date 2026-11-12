# Engineering Standards

> Single source of truth for how we build apps. Agents load this file before designing a schema.
> Every rule has an ID so reviews and agent reports can cite it.
> Changing a rule = a PR to this file, not a verbal agreement.

## Database

**DB-01 — No native `enum` in schema unless explicitly justified.**
Reasons: values cannot be dropped, reordered, or renamed without a type rebuild; `ALTER TYPE ... ADD VALUE` cannot run in the same transaction as its use. If a field genuinely needs an enum (closed set where adding a value must be a reviewed code change), write the justification in the migration comment.

**DB-02 — No magic numbers.**
A numeric literal compared against a status/state/type field is a defect. Use named constants or the lookup table. `00` is display formatting, never storage.

**DB-03 — Business-owned status sets use integer codes + lookup table.**
`status_code smallint NOT NULL REFERENCES ref_<subject>_status(code)`, with `label`, `sort_order`, and where relevant `is_terminal`. The lookup table is what keeps integers readable.

**DB-04 — Never store a human label as the status.**
No `varchar` holding `'out_of_stock'` or `'Terkirim'`. Copy changes must not require a data migration.

**DB-05 — `boolean` only for genuine binaries.**
`is_active`, `is_deleted`, `has_invoice`. If a third state is plausible within the product's lifetime, use a code column.

**DB-06 — Every status column carries a constraint.**
FK to the lookup table, or a `CHECK` for externally-defined codes. An unconstrained integer is worse than an enum.

**DB-07 — Adding a status value is a data migration, not an app release.**
One row in `ref_*`. No code deploy, no downtime.

**DB-08 — Money is `bigint` minor units + currency code.**
No floats. `amount_minor bigint`, `currency char(3)`.

**DB-09 — Timestamps are `timestamptz` in UTC.**
Display conversion happens in the app layer.

**DB-10 — Migrations are verb-first, one intent each, reversible.**
`2026_11_11_101500_add_status_code_to_orders`. Down-migration must restore data, not just drop the column.

## Application

**APP-01 — Status constants live in one module per domain.**
No literals scattered across controllers, views, and jobs. One file, imported everywhere.

**APP-02 — Validate at the boundary.**
Codes coming from outside (API, form) are checked against the lookup table before write.

**APP-03 — Frontend mirrors the backend code list; it does not invent labels.**
Labels come from the API or a shared i18n map, so a rename never desyncs.

## Process

**PR-01 — Deviations are declared.**
If you must break a rule, say which ID, what you did, and why. Undeclared deviation is a defect. Declared and justified deviation is engineering.

**PR-02 — The checker runs in CI.**
`python3 scripts/check_schema.py . --strict` must exit 0 to merge.
