---
title: What this is, and who it is for
slug: overview
group: Start
order: 1
summary: The plain-language explanation — what problem it solves, what you have to do, and what you never have to touch.
---

# Ironclad, without the jargon

**Ironclad is a rulebook for the AI that writes your code.** Not an app, not a
subscription — a text file the AI reads before it starts, plus a checker that
rejects the result if it breaks the rules.

If that is still abstract, here it is another way: *if your team uses AI to build
software, Ironclad keeps the output consistent — so nobody has to tear it apart a
year later.*

**Who this is for:**

- **You write code** and use AI (Claude, Copilot, Cursor) for the database part.
  You will use this daily.
- **You do not write code**, but you decide whether the team adopts this. All you
  have to do is forward it to a developer, then ask three questions
  [near the bottom](#if-you-are-not-the-one-writing-code).

**What you do not need to know to start:** what an enum is, what a foreign key is,
what a migration is. Every term like that lives in the [Glossary](/glossary/), and
you never have to read it in order.

## The problem it solves

This happens on teams over and over.

You ask an AI — Claude, Copilot, Cursor, whatever — to add an "orders" feature. It
writes the database part (where the data lives). The feature works. Everyone is
happy.

Six months later, three problems surface at once:

- In one table, order status is stored as `1`, `2`, `3`. Nobody remembers what `2`
  means. Whoever wrote it has changed jobs.
- In another table, status is stored as text: `"Paid"`, `"paid"`, `"PAID"` — three
  spellings, and the sales report now undercounts.
- A client wants a new status: "delayed by weather". To add it, you have to change
  the database **structure**, not just the data. On a production server that can
  lock the table — meaning the shop stops serving for a few minutes.

None of this is the AI's fault. It wrote what made sense at the time. What was
missing: a written rulebook it reads before it starts.

## Why this is expensive to fix later

Think of renovating a house.

You are free to choose paint colours, door handles, furniture layout — those are
cheap to change any time. But plumbing and wiring have to follow a standard. Not
because anyone loves rules, but because fixing them means tearing open walls.

The database is the plumbing. A UI can be replaced in a day. A wrong data structure
sticks around for years, and the cost rises every time new data lands in it.

Ironclad is the building code for that part — not for the paint.

## What Ironclad actually does

Three things, and only three:

**1. It gives the AI a rulebook before it starts.**
A text file in your repo (`.agent/standards.md`) holds decisions the team already
made: how status is stored, how money is stored, how dates are stored. The AI reads
it before writing the database.

**2. It keeps those rules in the repo, not in someone's head.**
It travels with git and gets reviewed when it changes. A new team member — human
or AI — reads the same file.

**3. It checks the result automatically.**
A script (`check_schema.py`) reads the database code and points at violations with
a rule number. You can run it by hand, or wire it into CI so a pull request that
violates a rule cannot be merged.

Point 1 is advice. Point 3 is enforcement. You need both, because an AI that only
gets advice will sometimes ignore it, and a checker with no written rules just
produces a list of errors nobody knows how to fix.

## What you have to do

Two commands. Nothing to answer, nothing to configure.

```bash
# 1. install (once per machine)
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

```bash
# 2. inside your repo — look only, changes nothing
ironclad check
```

If the result makes sense, make it permanent:

```bash
ironclad init
```

That is it. About two minutes, and your repo is untouched until you run the third
command.

Step by step: [Quickstart](/quickstart/).

## If you are not the one writing code

You can still use this. What you do:

**Send this page to your developer** — or to whoever maintains the app. Ask them to
run the two commands above.

**Then ask three questions.** The answers show whether this is actually installed
or merely promised:

1. "Which preset are we on?" — the right answer is one of `balanced`, `strict`, or
   `legacy-friendly`. If the answer is "what's a preset", it has not been run.
2. "How many findings right now?" — a number. Not "it's fine".
3. "Does a violating pull request actually fail?" — if it was never tested, the gate
   is unproven.

**What you never need to learn:** how the checker works, what a foreign key is, or
what is inside the YAML file. That belongs to whoever writes the code.

## What Ironclad does not do

- **Not a replacement for a programmer.** It does not write features or fix bugs.
- **Not a replacement for review.** It catches wrong patterns; it does not know
  whether your business logic is right.
- **Not a security tool.** It does not check for data leaks or access holes.
- **Does not change your app's appearance.** Nothing to do with design.
- **Does not send data anywhere.** Everything runs on your own machine.

## The honest limits

- The checker works by pattern matching, not understanding. It can flag code that
  is actually fine, and it can miss things it should have flagged. A human is still
  the last layer.
- It knows seven rules about databases. Not two hundred.
- There is no auto-update. For a newer version, re-run the installer.
- If your team has never used AI to write database code, the benefit is small —
  this is built for a problem that appears precisely because AI writes a lot, fast.

## Where to go next

| If you want to… | Read |
|---|---|
| look up a term used here | [Glossary](/glossary/) |
| install right now | [Install](/install/) |
| see every step | [Quickstart](/quickstart/) |
| know what it checks | [Rules](/rules/) |
| worry the team will rip it out | [Three layers](/three-layers/) — why tools like this get abandoned |
