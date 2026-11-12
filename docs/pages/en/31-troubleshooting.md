---
title: Troubleshooting
slug: troubleshooting
group: Operations
order: 31
summary: The symptoms that come up most, their causes, and the fix. Ordered by frequency.
---

# Troubleshooting

## The agent does not use the skill

**Most common cause.** The skill is installed, but the agent never activated it —
activation is decided by the `description` in `SKILL.md` matching your task.

Check it is installed where the agent looks:

```bash
ls ~/.agents/skills/ironclad/SKILL.md      # generic / Codex / Cursor
ls ~/.claude/skills/ironclad/SKILL.md      # Claude Code
ls ~/.hermes/skills/ironclad/SKILL.md      # Hermes
```

If it is not there, the installer put it somewhere else — check the `→` lines it
printed, or re-run with an explicit `--dir`.

If it is there and still not used, name it: "use ironclad for this migration".
Codex users: Codex reads `.agents/skills` **inside the repo**, not `$HOME`.

## `ironclad: command not found`

`~/.local/bin` is not on `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Or call it directly: `~/.local/bin/ironclad check`.

## `ironclad: skill not found at …`

The launcher points at a directory that no longer exists — usually because
`ironclad` was installed with `--target claude` and then someone removed it, or
`HOME` differs between the install shell and the current one.

Re-run the installer. It rewrites the launcher's `IRONCLAD_HOME` to the directory
it just used.

## `unknown preset` / exit code 2

Exit `2` is misuse, not a violation. Either the preset name is misspelled, or the
config file is missing where the checker expected it.

```bash
python3 scripts/check_schema.py --list-presets   # what it can actually see
```

A copied checker needs its presets beside it. `ironclad init` handles this by
writing `scripts/presets/`. If you copied `check_schema.py` by hand, copy the
presets too.

## `no .sql/.php/.prisma files found` (exit 2)

The path is wrong, or everything under it was skipped. The checker ignores
`node_modules`, `vendor`, `dist`, `build`, `.git`, `storage`, and dot-directories.

```bash
ironclad check app/database     # point at the schema, not the repo root
```

## Two machines, different results

Look at the last line of the report:

```
preset: balanced (.agent/standards.yml)    ← read from the repo
preset: balanced (preset:balanced)         ← fell back to the skill default
```

If one machine says `preset:balanced`, `.agent/standards.yml` is not there — not
committed, or the command ran from the wrong directory.

## Score got worse after adding a rule

Expected. A new rule finds things the old set did not look for. Roll it out as
`warn` in `legacy-friendly` first, fix the findings, then promote it to `error`.

## `curl … | bash` seems to ignore my input

It does not read stdin — by design, there is nothing to answer. If you passed
flags and they were ignored, they must come after `-s --`:

```bash
npx github:wilsench/ironclad#v0.8.5 --target claude
```

Without `-s --`, the arguments go to `bash` itself, which ignores them.

## Behind a proxy, or the mirror is unreachable

```bash
IRONCLAD_BASE=https://raw.githubusercontent.com/wilsench/ironclad/main/skills/ironclad \
  npx github:wilsench/ironclad#v0.8.5
```

`IRONCLAD_BASE` overrides the payload source entirely. Use it for an internal
mirror — the file list is fixed and printed in the installer's `FILES` variable.

## Nothing here matches

Open an issue at <https://github.com/wilsench/ironclad/issues> with:

- the command you ran
- the exact output (exit code included)
- `python3 --version`
- which agent, and where the skill is installed

## `ironclad version` still shows an old version after installing

`npx` caches, and without a ref it follows `main` as-is. Check what you actually have:

```bash
ironclad version
```

If that is not the version you meant to install:

```bash
npx --yes github:wilsench/ironclad#v0.8.5 --force
```

`--force` makes the installer overwrite the existing payload. If it is still stale,
clear the npm cache: `npm cache clean --force`.

If `ironclad` is not found at all, `~/.local/bin` is not on your `PATH` — the
installer prints the line to add to `~/.bashrc`.

## The agent does not ask, even though it is installed

Check two things, in order:

1. **Was the block actually written?** The installer prints `created`/`updated` per
   agent. If it printed "no agent config directory was found", that agent's config
   directory does not exist yet — launch the agent once, then re-run the installer.
2. **Does the agent read that file?** For Antigravity/`agy` the global rules live in
   `~/.gemini/AGENTS.md` and `~/.gemini/GEMINI.md`. For Claude Code, `~/.claude/CLAUDE.md`.
   If the file is there and the agent stays silent, that agent is not loading it —
   report it rather than assuming it works.

Repair without reinstalling: `ironclad attach --global`.
