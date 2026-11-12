---
title: Updating
slug: update
group: Start
order: 8
summary: How to find out there is a newer version, what changed, and three ways to not update.
---

# Updating

Ironclad has no auto-update. No daemon runs, there is no telemetry, and nothing
contacts the network unless you ask it to.

What exists is **one lightweight check that you run yourself.**

## `ironclad update`

```bash
ironclad update
```

If you are current:

```
installed: 0.9.5
latest:    0.9.5
You are on the latest version.
```

If something is newer, it shows **what changed** in human words, not commit hashes:

```
installed: 0.9.4
latest:    0.9.5
A newer version is available.

What changed since 0.9.4:
  1 change: 1 docs

  • three layers had the wrong first layer

What do you want to do?
  1) Install 0.9.5 now  (recommended)
  2) Stay on 0.9.4 for now  (nothing changes)
  3) Show me what changed
  4) Stop asking on this machine
Choose 1-4 [2]:
```

## The four choices, and what they cost

| Choice | What happens | Safe? |
|---|---|---|
| **1) Install now** | Runs the installer for the new version. The agent block is replaced in place, not stacked. | Yes. A `.agent/standards.md` you filled in is left alone. |
| **2) Stay on this version** | Nothing changes. The choice is remembered, so it does not ask again that day. | Yes. |
| **3) Show me what changed** | Prints the list again and returns to the menu. | Yes, read-only. |
| **4) Stop asking** | Turns the check off for good on that machine. | Yes. Turn it back on with `ironclad update`. |

The default is **2** — pressing Enter does nothing.

## When it checks

- **At most once per 24 hours.** The result is cached in `~/.ironclad/`.
- **Never inside a pipe or CI.** Without a terminal it prints the facts and exits —
  it never hangs waiting for an answer.
- **Never changes the exit code of `ironclad check`.** The gate stays 0 or 1 whether
  or not GitHub is reachable.
- **At most one line.** If a newer version exists, `ironclad check` adds one line at
  the end:

  ```
  Ironclad 0.9.5 is available (you have 0.9.4). Run `ironclad update`.
  ```

## For CI and scripts

```bash
ironclad update --check     # 0 = current, 10 = newer exists, 1 = network failure
ironclad update --notes     # print only the list of changes
ironclad update --mute      # stop checking
```

`--check` uses **10** deliberately, not 1, so it cannot be confused with "the schema
has findings". If you want CI to fail when you are behind, write it yourself:

```yaml
- run: ironclad update --check || [ $? -ne 10 ]
```

## On a machine without internet

The check fails quietly: one line saying GitHub could not be reached, then done.
Everything else — `check`, `init`, `drill` — works fully offline. The installed agent
block needs no network either.

## If you installed from a working tree, not a tag

The check compares the version in `SKILL.md` against the newest release tag. If you
installed from an unreleased working tree, it treats your version as newer than any
tag and stays quiet. That is correct: there is nothing to update.
