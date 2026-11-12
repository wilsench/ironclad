# How we store status

> This is a decision record, not a rulebook. It answers one question:
> **how does this project store status, and why.**
>
> Agents read this before writing schema so they follow the project instead of
> introducing a second style. Reviewers read it to see whether a change agrees
> with what we already decided.

## The decision

<!-- Fill in. One line. Delete the options that do not apply. -->

We store status as: **(one of)**

- `integer code + lookup table + foreign key` — e.g. `status_code smallint NOT NULL REFERENCES order_status(code)`
- `native enum` — e.g. `status ENUM('new','paid','cancelled')`
- `text code + CHECK` — e.g. `status text NOT NULL CHECK (status IN ('new','paid'))`

Decided on: <!-- date --> · Decided by: <!-- names -->

## Why

<!-- Two or three sentences. What made this the right choice here. -->

## Where it lives

<!-- Name the tables and the files, so an agent can check the claim. -->

| Table | Column | Type |
|---|---|---|
| `orders` | `status` | `smallint → order_status(code)` |

## How we add a new value

<!-- This is the part agents get wrong. Be concrete. -->

- **current answer:** one row in the lookup table, in a data migration
  (`INSERT INTO order_status (code, label) VALUES (...)`), no code deploy
- if the choice above is `enum`, say instead: a schema migration plus a code change,
  reviewed together

## If you disagree

Do not quietly write the other style. Ask, and put the change in this file in the
same pull request — so the next person reads one answer, not two.
