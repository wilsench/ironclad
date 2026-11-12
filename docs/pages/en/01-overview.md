---
title: Apa ini, untuk siapa
slug: overview
group: Start
order: 1
summary: The plain-language explanation — what problem it solves, what you have to do, and what you never have to touch.
---

# Ironclad, without the jargon

**Ironclad keeps one project consistent when more than one person works on its
database.**

Not an app, not a subscription. It is two things: a rules file inside your repo,
and a checker that rejects work which breaks those rules.

## The real problem: two developers, two styles

This is not a story about AI. It is a story about teams.

One project. Three developers. All three touch the database — add a column, create
a table, change a status.

Developer A stores order status as an **enum**:

```sql
status ENUM('new', 'paid', 'shipped')
```

Developer B stores the same thing as an **integer**:

```sql
status_code smallint NOT NULL
```

Both work. Both survive review, because each makes sense on its own. What is
missing: a shared decision about which one this project uses.

Six months later, one table stores status as an enum, another as an integer, a
third as free text. Every report needs three different queries for the same
question. And when a client asks for a new status — "delayed by weather" —
developer C first has to work out which table uses which approach, because adding
an enum value and adding a lookup row are two very different jobs.

None of this is anyone's fault. What was missing is one thing: **a written rule
everybody reads before they start.**

## The recommendation: integer, not enum

Ironclad leans toward **integer + lookup table** as the default. The reason is not
taste:

- **Adding an enum value changes the database structure.** In MySQL that is
  `ALTER TABLE`, and on a large table it locks the table while it runs. Business
  status always grows — and every growth should not be a maintenance event.
- **Adding one integer code adds one row of data.** An ordinary operation, no lock,
  no deploy.
- **A registered number is no more fragile than text.** As long as the code exists
  in a lookup table and is guarded by a foreign key, the database rejects numbers
  that were never registered. `88` is safe when `88` is registered; `87` is refused.

So the rule is not "never use enum". The rule is: **one approach per project**, and
the approach is integer + lookup — unless there is a written reason to deviate, and
that reason goes through review.

## Why this is expensive to fix later

Think of renovating a house.

You are free to choose paint colours, door handles, furniture layout — cheap to
change any time. But plumbing and wiring have to follow one standard. Not because
anyone loves rules, but because fixing them means tearing open walls.

The database is the plumbing. A UI can be replaced in a day. An inconsistent data
structure sticks around for years, and the cost rises every time new data lands.

## AI accelerates this problem; it does not cause it

If one developer writes enum and another writes integer, that happens because each
decided alone. AI makes those decisions happen **faster and in greater numbers** —
it writes in seconds, across many files, and never asks "how does this project
usually do it?"

That is why Ironclad puts the rules where the agent reads them: not to make the AI
smarter, but so it does not become a fourth team member with its own style.

## What Ironclad actually does

Three things, and only three:

**1. It writes the team's decisions into the repo.**
`.agent/standards.md` holds decisions already made: how status is stored, how money
is stored, how dates are stored. Not one person's preference — an agreement that
gets committed.

**2. It makes the AI read them before starting.**
The agent reads that file before writing the database. A new developer — human or
AI — reads the same file on day one.

**3. It checks the result automatically.**
`check_schema.py` reads the database code and points at violations with a rule
number. You can run it by hand, or wire it into CI so a pull request that violates a
rule cannot be merged. This is what catches a developer who does not use AI at all —
or who simply forgot.

Points 1 and 2 are advice. Point 3 is enforcement. You need both: advice without
enforcement gets ignored under deadline, and enforcement without written rules just
produces a list of errors nobody knows how to fix.

## What you have to do

Two commands. Nothing to answer.

```bash
# 1. install (once per machine)
npx github:wilsench/ironclad#v0.8.2
```

```bash
# 2. inside your repo — look only, changes nothing
ironclad check
```

If the result makes sense, make it permanent:

```bash
ironclad init
```

Then commit the four files it writes. From that commit on, everyone in the project —
and every agent — reads the same rules.

Walkthrough: [Quickstart](/quickstart/).

## If you are not the one writing code

You can still use this. What you do:

**Send this page to your developer.** Ask them to run the two commands above, then
commit the result.

**Then ask three questions.** The answers show whether this is actually installed or
merely promised:

1. "Which preset are we on?" — the right answer is one of `balanced`, `strict`, or
   `legacy-friendly`. If the answer is "what's a preset", it has not been run.
2. "How many findings right now?" — a number. Not "it's fine".
3. "Does a violating pull request actually fail?" — if it was never tested, the gate
   is unproven.

**A fourth question, specific to the enum problem:** "Is status stored as an enum or
an integer in this project?" If the answer is "it depends", the problem is still
there — and that is exactly what Ironclad solves.

**What you never need to learn:** how the checker works, what a foreign key is, or
what is inside the YAML file.

## What Ironclad does not do

- **Not a replacement for a programmer.** It does not write features or fix bugs.
- **Not a replacement for review.** It catches wrong patterns; it does not know
  whether your business logic is right.
- **Not a security tool.** It does not check for data leaks or access holes.
- **Does not change your app's appearance.** Nothing to do with design.
- **Does not send data anywhere.** Everything runs on your own machine.

## The honest limits

- The checker works by pattern matching, not understanding. It can flag code that is
  actually fine, and it can miss things it should have flagged. A human is still the
  last layer.
- It knows eight rules about databases. Not two hundred.
- **It cannot force anyone to read.** If a developer ignores `.agent/standards.md`
  and CI is never wired up, nothing catches it. What makes this work is CI, not good
  intentions.
- There is no auto-update. For a newer version, re-run the installer.

## Where to go next

| If you want to… | Read |
|---|---|
| look up a term used here | [Glossary](/glossary/) |
| install right now | [Install](/install/) |
| see every step | [Quickstart](/quickstart/) |
| know what it checks | [Rules](/rules/) |
| worry the team will rip it out | [Three layers](/three-layers/) |
