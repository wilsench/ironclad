---
title: Quickstart
slug: quickstart
group: Start
order: 4
summary: Two minutes from nothing to a green checker in one repo, without disturbing anyone else's work.
---

# Quickstart

Two minutes. No questions to answer, no files to hand-edit.

## 1. Install

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

Done. The skill is in `~/.agents/skills/ironclad/`, the `ironclad` command is in
`~/.local/bin/`.

## 2. Look first, change nothing

```bash
cd your-repo
ironclad check
```

This only reads. Output looks like this:

```
bad.sql:4: [DB-01] ERROR SQL/prisma enum column; use integer code + lookup table (see DB-03)
bad.sql:6: [DB-04] ERROR status stored as text (`stock_state`); use smallint code + lookup table

preset: balanced (preset:balanced)
1 file(s), 2 error(s), 2 warning(s)
```

If your repo is large, do not panic at the count. That is what step 4 is for.

## 3. Make it permanent

```bash
ironclad init
```

It writes four things, all meant to be committed:

```
wrote   .agent/standards.yml (preset: balanced)
wrote   .agent/standards.md
wrote   scripts/check_schema.py + scripts/presets/
```

```bash
git add .agent scripts
git commit -m "chore: adopt ironclad standards"
```

From that commit on, the agent reads `.agent/standards.md` before writing DDL,
and CI reads `.agent/standards.yml` to decide what blocks. One source, two
readers.

## 4. Pick a strictness that will not make the team disable CI

This is the step most people skip, and the main reason tools like this get ripped
out within a week.

| Your repo | Start with | Why |
|---|---|---|
| new, or already clean | `strict` | everything blocks, no debt |
| live product, normal debt | `balanced` (default) | enum & text-status block, the rest warns |
| old repo, hundreds of findings | `legacy-friendly` | everything warns, build stays green |

```bash
ironclad preset legacy-friendly   # old repo: install, then clean up slowly
ironclad preset balanced          # once the baseline is clean
ironclad preset strict            # once nothing is left warning
```

Step up when the finding count drops, not when a date arrives.

## 5. Prove the gate actually works

Do not trust a green checkmark. Test three things:

```bash
ironclad check examples/good.sql   # must exit 0
ironclad check examples/bad.sql    # must exit 1
```

Then open a PR that adds one `enum` column — it must go red on GitHub. If it does
not go red, your CI is wrong, not the checker.

## That is it

What remains is habit: `ironclad check` before you commit, and let CI run the same
thing on every PR.

If something does not work as described here, see
[Troubleshooting](/troubleshooting/) — organised by symptom, not by theory.
