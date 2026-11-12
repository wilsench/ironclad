---
title: Rules DB-01…DB-08
slug: rules
group: Reference
order: 20
summary: Eight database rules, each with a wrong and a right example the checker actually tests. DB-08 is the one that answers the team problem.
---

# Rules

Each rule has an ID. Use the ID in reviews, in commit messages, in CI output.
"Use DB-03 here" is a shorter conversation than a paragraph about foreign keys.

## Summary

The **Status** column below is behaviour under the `balanced` preset (the
default). Under `strict` everything becomes `error`; under `legacy-friendly`
everything is `warn`.

| ID | Rule | Status |
|---|---|---|
| DB-01 | No `enum` columns for status | error |
| DB-02 | No magic numbers compared against status | error |
| DB-03 | Status needs a lookup table + FK | warn |
| DB-04 | No human labels stored as status text | error |
| DB-05 | No boolean for a non-binary concept | warn |
| DB-06 | No money as `float`/`double` | warn |
| DB-07 | No `timestamp` without a timezone | warn |
| DB-08 | One status style per project — no mixing enum and integer | warn |

## DB-01 — no enum columns

```sql
-- wrong
status ENUM('pending', 'paid', 'shipped')

-- right
status_code smallint NOT NULL REFERENCES order_status(code)
```

`enum` forces every new value through a schema migration. In MySQL that means
`ALTER TABLE`, which locks the table while it rewrites. Business status always
grows: "scheduled", "awaiting confirmation", "delayed by weather", "partially
refunded".

## DB-02 — no magic numbers

```php
// wrong: what is 2 and what is 7?
if ($order->status_code === 2 || $order->status_code === 7) { ... }

// right
if (in_array($order->status_code, [OrderStatus::PAID, OrderStatus::PARTIAL_REFUND], true)) { ... }
```

The checker flags comparisons against bare integer literals on status-like
columns. `INSERT` values and `CHECK` constraints are exempt — those are where
codes are legitimately declared.

> This is not an argument against arbitrary codes. `88`, `99`, `990` are all
> fine. What is not fine is a bare `88` appearing in application logic in five
> places with no name attached.

## DB-03 — status needs a lookup table and a foreign key

```sql
-- wrong: any integer is acceptable, including 87, which means nothing
status_code smallint NOT NULL

-- right: the database rejects anything not registered
status_code smallint NOT NULL REFERENCES order_status(code)
```

This is the rule that makes arbitrary codes safe. Without it, `88` and `8` are
equally valid to the database and equally wrong.

## DB-04 — no human labels as status

```sql
-- wrong
stock_state varchar(32)   -- 'In Stock', 'Sold Out', 'in stock '

-- right
stock_state_code smallint NOT NULL REFERENCES stock_state(code)
```

Text status invites whitespace variants, casing variants, translated labels, and
a `WHERE` clause that misses half the rows.

## DB-05 — no boolean for a non-binary concept

```sql
-- wrong: what does true mean here?
is_status boolean

-- right
status_code smallint NOT NULL REFERENCES ...
```

A boolean is correct only when the domain is genuinely two-valued and expected to
stay that way: `is_active`, `is_deleted`, `email_verified`.

## DB-06 — no money as float

```sql
-- wrong
total float
total double precision

-- right
total_cents bigint NOT NULL          -- or NUMERIC(14,2)
```

Binary floating point cannot represent `0.10`. Sum a thousand rows of `float` and
the total is off by real money.

## DB-07 — no timestamp without a timezone

```sql
-- wrong
created_at timestamp

-- right
created_at timestamptz NOT NULL DEFAULT now()
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
```

A naive timestamp is ambiguous across servers, timezones and DST. The checker
does not flag camelCase columns like `createdAt` in Prisma schemas — Prisma
handles the mapping, and flagging them was a false positive.

## DB-08 — One project, one status style

This is the rule that answers the team problem most directly: **not** "enum is
wrong", but "do not let one project use three approaches at once".

```sql
-- wrong: one project, two different styles
CREATE TABLE orders (
  status ENUM('new','paid','shipped')
);
CREATE TABLE shipments (
  status_code smallint NOT NULL REFERENCES shipment_status(code)
);
```

```
a.sql:1: [DB-08] warn  status is stored 2 different ways in this project:
  enum (a.sql), integer (b.sql) — pick one for the whole project;
  integer code + lookup is the default
```

```sql
-- right: every table uses the same approach
CREATE TABLE orders (
  status_code smallint NOT NULL REFERENCES order_status(code)
);
CREATE TABLE shipments (
  status_code smallint NOT NULL REFERENCES shipment_status(code)
);
```

**Why:** enum and integer both work — what does not work is both in the same
project. Every report needs two queries, every new developer has to guess, and "how
do we add a status?" has no single answer. DB-08 is the only rule that reads
**across files**, because inconsistency is a property of the project, not of one
table.

**Why integer is the default:** adding an integer code adds one row of data; adding
an enum value is `ALTER TABLE`, which locks the table. Not taste — cost, when status
grows.

**Deviating on purpose:** if the team chooses enum, write the reason in
`.agent/standards.md` and set `DB-01`/`DB-08` to `warn` or `off`. What is forbidden
is not a different choice — what is forbidden is having no choice at all.

---

## Rule IDs are permanent

Numbers are never reused. If `DB-03` is retired, that number is retired with it —
not reassigned, because old review comments would then point at the wrong rule.
