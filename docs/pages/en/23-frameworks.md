---
title: Laravel, Prisma, and other backends
slug: frameworks
group: Reference
order: 23
summary: What the checker reads, what it cannot read, and how to stay consistent when your framework is not supported yet.
---

# Laravel, Prisma, and other backends

The short answer: **it does not matter as long as your project writes its schema in
one of the three file types the checker reads.** For everything else there is a
limit you should know before trusting a green result.

## What is read

The checker reads file contents; it does not run your app. So the question is not
"are you on Laravel", it is "what form do the rules eventually take".

| Source | Example | Status |
|---|---|---|
| Raw SQL | `CREATE TABLE`, `.sql` migration | **supported** |
| Laravel / PHP | `Schema::create`, `$table->enum()`, `$table->unsignedSmallInteger()` | **supported** |
| Prisma | `model Order`, `enum OrderStatus` | **supported** |
| Django / Python | `models.CharField`, `models.FloatField` | no — reported, not checked |
| Rails / Ruby | `create_table`, `t.integer` | no — reported, not checked |
| TypeORM / Drizzle | `@Entity`, `pgTable` | no — reported, not checked |
| Sequelize | `Model.init`, `DataTypes.*` | no — reported, not checked |
| GORM / Go | `gorm:"..."` | no — reported, not checked |
| JPA / Java / Kotlin | `@Entity` | no — reported, not checked |
| Entity Framework / C# | `[Table(`, `DbSet<` | no — reported, not checked |
| Diesel / sqlx / Rust | `#[derive(...)]`, `table_name` | no — reported, not checked |

## The part that matters: it says so

A Django repo that passes silently is more dangerous than one that is rejected,
because the first makes you believe you are covered.

```bash
$ ironclad check
no .sql/.php/.prisma files found

This repo does have schema files this checker cannot read: .py.
Nothing was checked. Do not treat this as a pass.
  .py: models.py
```

Exit code `2`. In CI that is not green — the job fails.

And when the repo is mixed (some files read, some not), a `COVERAGE` warning sits
on top of the other findings:

```
models.py:1: [COVERAGE] warn  1 schema file(s) checked, but this repo also has
.py schema files this checker cannot read — those files were NOT checked
```

Meaning: only part of the repo is green. Do not read it as "all clean".

## If your backend is not supported yet

Two honest options, and one bad one.

**1. Put the rules where they can be checked.** Most frameworks emit SQL. Commit
the resulting SQL schema too and point the checker at it:

```bash
ironclad check db/schema.sql
```

**2. Check it by review instead of by machine.** `.agent/standards.md` is still
useful in the meantime: the agent reads it and follows the same rules even where
the checker cannot verify. Only the gate is missing — so do that review manually
on PRs.

**3. The bad one: adding `|| true`.** That makes CI green without checking
anything. Better to install no checker at all than one that is decoration.

## Why Laravel is still safe

The three Laravel traps that actually bite, all caught:

```php
// rejected DB-01 — an enum cannot be extended without ALTER TABLE
$table->enum('status', ['new', 'paid', 'shipped']);

// accepted — integer + foreign key to a lookup table
$table->unsignedSmallInteger('status_code');
$table->foreign('status_code')->references('code')->on('order_status');
```

```php
// rejected DB-07 — Laravel's timestamp() stores WITHOUT a timezone
$table->timestamp('created_at');

// accepted
$table->timestampTz('created_at')->useCurrent();
```

```php
// rejected DB-06 — money is never a float
$table->float('total');

// accepted — minor units + currency code
$table->bigInteger('total_minor');
$table->char('currency', 3);
```

One filename note: Laravel migrations are named
`2024_01_01_000000_create_orders_table.php` — the word "migration" is in the
**folder**, not the filename. The checker now recognises both, and also matches
`Schema::create` regardless of filename.

## Eloquent and controllers

It reads application code too, not just migrations. What it looks for there is
magic numbers:

```php
// rejected DB-02
if ($order->status_code === 2) { ... }

// accepted
if ($order->status_code === OrderStatus::PAID) { ... }
```

This is the rule most often broken, not from laziness but because `2` feels obvious
when you write it and is not obvious six months later.

## When in doubt

```bash
ironclad check --json
```

The output names every file checked and every finding. If a file is absent and
there is no `COVERAGE` warning, that file was never read — which is not the same as
clean.
