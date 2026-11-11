# Database Policy — integer codes over enums

Full decision table and rationale. `SKILL.md` carries the procedure; this file carries the reasoning so the agent can defend a choice in review rather than recite a rule.

## Decision table — ask in this order

| Question | If yes | If no |
|---|---|---|
| Genuinely two states, forever, never a third? | `boolean` | next row |
| Business owns the value set, it will grow, ops/users maintain it? | `integer` + lookup table + FK | next row |
| Values fixed by an external standard you do not control (ISO, HTTP, country, currency)? | `integer` code + constants, no lookup table | next row |
| Values are structural to code logic and every branch must be handled? | app-level enum / union type | next row |
| Set is small, closed, and changing it *should* be a reviewed code change? | DB `enum` is legitimate — document why | reconsider |

## Why enums lose (the real costs, not taste)

- **Postgres**: a value cannot be dropped, the type cannot be reordered, renaming requires a type rebuild plus cast. `ALTER TYPE ... ADD VALUE` cannot be used in the same transaction that uses the new value (pre-PG12).
- **Three-place sync**: every new value means a DB migration, a backend constant, and a frontend label. In practice these drift, and drift here means a 500 on a real user's order.
- **Analytics**: statuses land in logs and BI as strings — worse compression, worse index selectivity, and no join to metadata like `is_terminal` or `sort_order`.
- **Ordering is lost**: an enum has no ordinal you can sort by without a `CASE` expression.

## Why a bare integer is worse than an enum

`status = 7` inserts happily and fails silently in the UI. An enum at least self-documents. An integer only becomes safe with:

1. **A lookup table** the business owns, joined by FK — this is what makes the number readable and rejects a typo.
2. **Named constants** in app code (`STOCK_EMPTY = 0`) — this is what makes the number readable in a diff.
3. **A constraint** — FK or `CHECK` — so an unmapped code is impossible.

All three, not two. Integer without a lookup table just relocates the mystery.

**`00` is not a storage concept.** `00` as "empty stock" is display formatting. Storage is `0`; the two-digit rendering belongs in the presenter. Storing `00` means either a string column (worse than an enum) or a false precision that vanishes the moment someone sums the column.

## When enum is the right answer

Reach for it when adding a value **must** be a reviewed code change — a state machine whose transitions the code must explicitly handle, where a new state means new behaviour. That is a code decision, not a data decision, and encoding it in the DB makes the omission loud. Write the justification in the migration comment so the next reader knows it was deliberate.

The failure mode is not "enum exists"; it is enum used for *business lists* that ops should be able to extend without a deploy.

## Worked example — stock status

```sql
CREATE TABLE ref_stock_status (
  code        smallint PRIMARY KEY,
  label       text NOT NULL,
  sort_order  smallint NOT NULL DEFAULT 0,
  is_terminal boolean NOT NULL DEFAULT false
);
INSERT INTO ref_stock_status VALUES
  (0,'Kosong',0,false),(1,'Menipis',1,false),
  (2,'Tersedia',2,false),(3,'Dipesan',3,false);

CREATE TABLE product_stock (
  product_id  bigint NOT NULL REFERENCES products(id),
  status_code smallint NOT NULL DEFAULT 0 REFERENCES ref_stock_status(code),
  qty         integer  NOT NULL DEFAULT 0,
  CONSTRAINT stock_status_qty_consistent
    CHECK ((status_code = 0 AND qty = 0) OR (status_code <> 0 AND qty >= 0))
);
```

```ts
const STOCK = { EMPTY: 0, LOW: 1, AVAILABLE: 2, RESERVED: 3 } as const;
type StockCode = (typeof STOCK)[keyof typeof STOCK];
```

```php
final class StockStatus {
    const EMPTY = 0; const LOW = 1; const AVAILABLE = 2; const RESERVED = 3;
}
```

Departure status follows the same shape: codes in `ref_departure_status`, FK from `departures`, never `enum('scheduled','departed','cancelled')` copied across migrations.

## Migration rules

- Naming: `YYYY_MM_DD_HHMMSS_<verb>_<subject>.php` or `<nnn>_<verb>_<subject>.sql` — verb first, imperative, one intent each.
- Adding a status value = **one lookup-row migration**, no app deploy. That is the payoff; if adding a value still needs a code change, the design failed.
- Every FK gets an index. Every status column gets FK or `CHECK`.
- Destructive changes ship a down-migration that restores data, not just drops the column.

## Money and time

- Money: `bigint` minor units + `char(3)` currency. No floats, ever.
- Timestamps: `timestamptz` in UTC; convert at the display layer, not in storage.
