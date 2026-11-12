---
title: How agents use it
slug: how-agents-use-it
group: Start
order: 3
summary: Skills activate on their own — but only when the description matches the task. Here is how that works and how to force it.
---

# How an agent actually picks this up

Short answer: **automatically, but not unconditionally.** That distinction
matters more than it sounds.

## Every turn, the agent sees only a list

Agents that implement [Agent Skills](https://agentskills.io) follow one
pattern — Hermes, Claude Code, Codex, opencode and Antigravity all do this:

1. **Discovery.** On every turn the agent gets a list of available skills:
   name and description only. Not the body.
2. **Activation.** If a task looks relevant, it reads the full `SKILL.md`.
3. **Execution.** It follows the instructions while doing the work.

So the body of Ironclad is not in the model's context until there is schema work
to do. That is deliberate: if every skill loaded fully on every turn, the context
window would be gone before you asked your first question.

## What decides whether it activates

The `description` field in `SKILL.md`:

```yaml
description: "Enforce team engineering standards with presets."
```

The agent matches your request against that sentence. Which means:

| You say | Result |
|---|---|
| "add a `status` column to orders" | likely activates — schema work |
| "why does the build fail on DB-04?" | likely activates — names a rule ID |
| "rename this variable" | does not activate — nothing to do with schema |
| "write a landing page" | does not activate |

This is a feature. An agent that injects a database rulebook into every unrelated
task is noise.

## How to force it

When you want it guaranteed:

- **mention the name** — "use ironclad for this migration"
- **Hermes** — the skill is loaded on demand; asking by name is enough
- **Antigravity** — type `/ironclad` in the message box
- **opencode** — mention `@ironclad`, or set permissions in `opencode.json`
- **Claude Code / Codex** — naming the skill in the prompt is the reliable way

## Where it stops being optional

Skill activation is fuzzy. The checker is not:

```bash
ironclad check     # exit 1 = violations, whether or not the agent read anything
```

If the agent never reads `SKILL.md`, you still get enforcement from CI. You just
lose the good decisions made *before* the DDL was written — which is the part
that actually saves time.

## What the agent does when it is active

1. reads `.agent/standards.md` (the repo's policy)
2. classifies every status-like field using the decision table
3. designs the schema: integer code + lookup table + FK + constraint
4. writes the migration
5. runs the checker
6. reports every deviation with a rule ID and a reason

Step 6 is the one people skip. An undocumented deviation is a defect, because the
next agent has no way to know the rule was consciously overridden.

If `.agent/standards.md` is missing, the agent runs `ironclad init` (preset
`balanced`). That command never prompts, so an agent can never hang waiting for
an answer that will not come.
