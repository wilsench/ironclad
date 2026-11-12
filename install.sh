#!/usr/bin/env bash
# Ironclad — install for the agent you actually use.
#
#   curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
#   curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --project .
#
# Targets (pick one, or --all):
#   agents    ~/.agents/skills          Codex, Cursor, opencode, Antigravity  (default)
#   claude    ~/.claude/skills          Claude Code
#   hermes    ~/.hermes/skills          Hermes Agent
#   gemini    ~/.gemini/config/skills   Antigravity global
#   opencode  ~/.config/opencode/skills opencode native
#
# Options:
#   --target NAME        which agent (agents|claude|hermes|gemini|opencode|all)
#   --dir PATH           explicit skills directory (overrides --target)
#   --project PATH       also bootstrap policy + checker into that repo
#   --preset NAME        balanced (default) | strict | legacy-friendly
#   --policy-only        bootstrap .agent/ only, skip the checker
#   --ref REF            git branch/tag (default: main)
#   --repo OWNER/REPO    source repo (default: wilsench/ironclad)
#   --uninstall          remove the skill from the chosen target(s)
#   -h, --help
#
# Needs: curl + bash. Python is NOT required to install or to bootstrap policy.
# Python 3.8+ is required only to RUN the schema checker.

set -euo pipefail

SKILL_NAME="ironclad"
REPO="${REPO:-wilsench/ironclad}"
REF="${REF:-main}"
TARGET="auto"
DEST=""
PROJECT=""
PRESET="balanced"
POLICY_ONLY=""
UNINSTALL=""
ALL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --target)      TARGET="${2:?--target needs a value}"; shift 2 ;;
    --dir)         DEST="${2:?--dir needs a value}"; shift 2 ;;
    --project)     PROJECT="${2:?--project needs a value}"; shift 2 ;;
    --preset)      PRESET="${2:?--preset needs a value}"; shift 2 ;;
    --policy-only) POLICY_ONLY=1; shift ;;
    --ref)         REF="${2:?--ref needs a value}"; shift 2 ;;
    --repo)        REPO="${2:?--repo needs a value}"; shift 2 ;;
    --all)         ALL=1; shift ;;
    --uninstall)   UNINSTALL=1; shift ;;
    -h|--help)     sed -n '2,26p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1 (try --help)" >&2; exit 2 ;;
  esac
done

case "$TARGET" in
  auto) [ "$ALL" = "1" ] && TARGET="all" || TARGET="agents" ;;
  agents|claude|hermes|gemini|opencode|all) ;;
  *) echo "unknown target: $TARGET" >&2; exit 2 ;;
esac

case "$PRESET" in
  balanced|strict|legacy-friendly) ;;
  *) echo "unknown preset: $PRESET (balanced|strict|legacy-friendly)" >&2; exit 2 ;;
esac

# ---- resolve destination(s) -------------------------------------------------
dest_for() {
  case "$1" in
    agents)   echo "$HOME/.agents/skills" ;;
    claude)   echo "$HOME/.claude/skills" ;;
    hermes)   echo "$HOME/.hermes/skills" ;;
    gemini)   echo "$HOME/.gemini/config/skills" ;;
    opencode) echo "$HOME/.config/opencode/skills" ;;
  esac
}

if [ -n "$DEST" ]; then
  DESTS="$DEST"
elif [ "$TARGET" = "all" ]; then
  DESTS=""
  for t in agents claude hermes gemini opencode; do
    # only touch agents that are actually installed on this machine
    parent="$(dirname "$(dest_for "$t")")"
    if [ -d "$parent" ]; then DESTS="$DESTS $(dest_for "$t")"; fi
  done
  [ -z "$DESTS" ] && DESTS="$(dest_for agents)"
else
  DESTS="$(dest_for "$TARGET")"
fi

if [ -n "$UNINSTALL" ]; then
  for d in $DESTS; do
    if [ -d "$d/$SKILL_NAME" ]; then
      rm -rf "$d/$SKILL_NAME"
      echo "removed $d/$SKILL_NAME"
    else
      echo "not installed: $d/$SKILL_NAME"
    fi
  done
  exit 0
fi

# ---- fetch ------------------------------------------------------------------
# Two sources: GitHub when the repo exists, this domain's mirror otherwise.
# The mirror means `curl ... | bash` works before the repo is published, and keeps
# working if GitHub rate-limits a first-time visitor.
PRIMARY="https://raw.githubusercontent.com/${REPO}/${REF}/skills/${SKILL_NAME}"
MIRROR="${IRONCLAD_MIRROR:-https://wilsench.my.id/ironclad/pkg}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FILES="SKILL.md templates/standards.md
references/database.md references/presets.md references/extending.md
assets/presets/balanced.yml assets/presets/strict.yml assets/presets/legacy-friendly.yml
scripts/check_schema.py scripts/init_standards.py"

fetch_from() {
  base="$1"; label="$2"
  for f in $FILES; do mkdir -p "$TMP/$(dirname "$f")"; done
  # probe one file first so a dead source fails fast with a single message
  curl -fsSL --retry 1 --max-time 20 "$base/SKILL.md" -o "$TMP/SKILL.md" 2>/dev/null || return 1
  for f in $FILES; do
    [ "$f" = "SKILL.md" ] && continue
    curl -fsSL --retry 2 --max-time 30 "$base/$f" -o "$TMP/$f" 2>/dev/null || {
      echo "  incomplete payload from $label (missing $f)" >&2; return 1; }
  done
  SOURCE="$label"
  return 0
}

SOURCE=""
echo "Fetching ${SKILL_NAME} ..."
if [ -n "${IRONCLAD_BASE:-}" ]; then
  fetch_from "$IRONCLAD_BASE" "IRONCLAD_BASE" || { echo "failed: $IRONCLAD_BASE" >&2; exit 1; }
elif fetch_from "$PRIMARY" "${REPO}@${REF}"; then
  :
else
  echo "  GitHub not reachable (repo not published yet or rate-limited) — trying mirror" >&2
  fetch_from "$MIRROR" "wilsench.my.id mirror" || {
    echo "failed to fetch from GitHub and from the mirror. Check network, then retry." >&2; exit 1; }
fi
echo "  source: ${SOURCE}"

if ! head -5 "$TMP/SKILL.md" | grep -q "^name: ${SKILL_NAME}$"; then
  echo "downloaded SKILL.md does not look like ${SKILL_NAME} — aborting" >&2
  exit 1
fi

# ---- install ----------------------------------------------------------------
for d in $DESTS; do
  if [ -d "$d/$SKILL_NAME" ]; then
    echo "Replacing existing install at $d/$SKILL_NAME"
    rm -rf "$d/$SKILL_NAME"
  fi
  mkdir -p "$d/$SKILL_NAME"
  cp -R "$TMP/." "$d/$SKILL_NAME/"
  chmod +x "$d/$SKILL_NAME/scripts/"*.py 2>/dev/null || true
  echo "Installed: $d/$SKILL_NAME"
done

# ---- optional: bootstrap a repo --------------------------------------------
if [ -n "$PROJECT" ]; then
  if [ ! -d "$PROJECT" ]; then
    echo "project not found: $PROJECT" >&2
    exit 1
  fi
  AGENT_DIR="$PROJECT/.agent"
  mkdir -p "$AGENT_DIR"

  if [ -f "$AGENT_DIR/standards.yml" ] && [ "$PRESET" = "balanced" ]; then
    echo "kept existing $AGENT_DIR/standards.yml"
  else
    cp "$TMP/assets/presets/$PRESET.yml" "$AGENT_DIR/standards.yml"
    echo "wrote $AGENT_DIR/standards.yml (preset: $PRESET)"
  fi

  if [ -f "$AGENT_DIR/standards.md" ]; then
    echo "kept existing $AGENT_DIR/standards.md"
  else
    cp "$TMP/templates/standards.md" "$AGENT_DIR/standards.md"
    echo "wrote $AGENT_DIR/standards.md"
  fi

  if [ -z "$POLICY_ONLY" ]; then
    mkdir -p "$PROJECT/scripts/presets"
    cp "$TMP/scripts/check_schema.py" "$PROJECT/scripts/check_schema.py"
    cp "$TMP/assets/presets/"*.yml "$PROJECT/scripts/presets/"
    chmod +x "$PROJECT/scripts/check_schema.py"
    echo "wrote $PROJECT/scripts/check_schema.py (+ presets)"
  fi
  echo
  echo "Commit these, or the next teammate gets a different rulebook:"
  echo "  git add .agent scripts && git commit -m 'chore: adopt ironclad standards'"
fi

echo
echo "Done. The agent picks the skill up on its next launch — no command to run."
echo "It reads .agent/standards.md before designing schema; the checker enforces the rest."
