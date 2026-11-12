#!/usr/bin/env bash
# Ironclad — one rulebook for every AI coding agent.
#
#   curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
#
# That is the whole install. No questions. It puts the skill where your agent
# looks for it and adds an `ironclad` command to ~/.local/bin.
#
# Then, inside any repo:
#   ironclad check      # instant verdict, nothing written
#   ironclad init       # commit the policy + checker (preset: balanced)
#   ironclad preset strict
#
# Flags, for CI and for people who like flags:
#   --target NAME        agents | claude | hermes | gemini | opencode | all
#   --dir PATH           explicit skills directory (overrides --target)
#   --no-bin             skip the ~/.local/bin/ironclad launcher
#   --project PATH       bootstrap policy + checker into that repo, then exit
#   --preset NAME        balanced (default) | strict | legacy-friendly
#   --policy-only        with --project: write .agent/ only, skip the checker
#   --repo OWNER/REPO    payload repo (default: wilsench/ironclad)
#   --ref REF            git branch or tag (default: main)
#   --uninstall          remove the skill from every agent dir + the launcher
#   --purge              with --uninstall: also delete this project's .agent/ and
#                        scripts/ files (default is to leave them — they are a repo
#                        decision, not an installer artefact)
#   -h, --help
#
# Payload source order: $IRONCLAD_BASE → wilsench.my.id mirror → GitHub.
# The mirror is tried first so the script and the payload always match.
#
# Needs curl + bash. Python is NOT needed to install or to write the policy;
# Python 3.8+ is needed only to RUN the checker.

set -euo pipefail

SKILL_NAME="ironclad"
REPO="${REPO:-wilsench/ironclad}"
REF="${REF:-main}"
TARGET="agents"
DEST=""
PROJECT=""
PRESET="balanced"
POLICY_ONLY=""
UNINSTALL=""
PURGE=""
NO_BIN=""
ALL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --target)      TARGET="${2:?--target needs a value}"; shift 2 ;;
    --dir)         DEST="${2:?--dir needs a value}"; shift 2 ;;
    --project)     PROJECT="${2:?--project needs a value}"; shift 2 ;;
    --preset)      PRESET="${2:?--preset needs a value}"; shift 2 ;;
    --policy-only) POLICY_ONLY=1; shift ;;
    --repo)        REPO="${2:?--repo needs a value}"; shift 2 ;;
    --ref)         REF="${2:?--ref needs a value}"; shift 2 ;;
    --all)         ALL=1; shift ;;
    --uninstall)   UNINSTALL=1; shift ;;
    --purge)       PURGE=1; shift ;;
    --no-bin)      NO_BIN=1; shift ;;
    -y|--yes)      shift ;;
    -h|--help)     sed -n '2,29p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1 (try --help)" >&2; exit 2 ;;
  esac
done

[ -n "$ALL" ] && { [ "$TARGET" != "agents" ] && { echo "--all conflicts with --target" >&2; exit 2; }; TARGET="all"; }

case "$TARGET" in
  agents|claude|hermes|gemini|opencode|all) ;;
  *) echo "unknown target: $TARGET" >&2; exit 2 ;;
esac
case "$PRESET" in
  balanced|strict|legacy-friendly) ;;
  *) echo "unknown preset: $PRESET (balanced|strict|legacy-friendly)" >&2; exit 2 ;;
esac

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
    parent="$(dirname "$(dest_for "$t")")"
    if [ -d "$parent" ]; then DESTS="$DESTS $(dest_for "$t")"; fi
  done
  [ -z "$DESTS" ] && DESTS="$(dest_for agents)"
else
  DESTS="$(dest_for "$TARGET")"
fi

find_project_root() {
  local d="$PWD"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.agent" ] || [ -d "$d/scripts/presets" ]; then echo "$d"; return 0; fi
    d="$(dirname "$d")"
  done
  return 1
}

# ---- uninstall --------------------------------------------------------------
# Removing only one target leaves working copies behind in the other agents, and
# the skill keeps loading there with no command to manage it. So: sweep every
# known location, plus --dir if given, and say what was actually there.
if [ -n "$UNINSTALL" ]; then
  SCAN="$DESTS"
  for t in agents claude hermes gemini opencode; do
    SCAN="$SCAN $(dest_for "$t")"
  done
  FOUND=0
  SEEN=""
  for d in $SCAN; do
    case ":$SEEN:" in *":$d:"*) continue ;; esac
    SEEN="$SEEN:$d:"
    [ -d "$d/$SKILL_NAME" ] || continue
    rm -rf "$d/$SKILL_NAME"
    echo "removed $d/$SKILL_NAME"
    FOUND=$((FOUND + 1))
  done
  [ -f "$HOME/.local/bin/$SKILL_NAME" ] && {
    rm -f "$HOME/.local/bin/$SKILL_NAME"
    echo "removed $HOME/.local/bin/$SKILL_NAME"
    FOUND=$((FOUND + 1))
  }
  [ "$FOUND" -eq 0 ] && echo "nothing to remove — not installed in any known location"

  # The policy in a project is a repo decision, not an installer artefact, so it
  # survives by default. --purge is for "I am dropping this entirely".
  if [ -n "$PURGE" ]; then
    ROOT="$(find_project_root)"
    if [ -z "$ROOT" ]; then
      echo "purge: no .agent/ or scripts/presets/ found at or above $PWD — nothing to purge"
    else
      for rel in "$ROOT/.agent/standards.yml" "$ROOT/.agent/standards.md" \
                 "$ROOT/scripts/check_schema.py" "$ROOT/scripts/presets"; do
        if [ -e "$rel" ]; then
          rm -rf "$rel"
          echo "purged  ${rel#$ROOT/}"
        fi
      done
      rmdir "$ROOT/.agent" "$ROOT/scripts" 2>/dev/null || true
      echo "purged project files — if they were committed, finish with: git rm -r .agent scripts"
    fi
  else
    echo
    echo "Project files were left alone: .agent/standards.{md,yml}, scripts/check_schema.py,"
    echo "scripts/presets/. They are a repo decision — delete them in a commit, or rerun with"
    echo "--uninstall --purge to remove them from disk."
  fi
  exit 0
fi

# ---- fetch ------------------------------------------------------------------
PRIMARY="https://raw.githubusercontent.com/${REPO}/${REF}/skills/${SKILL_NAME}"
MIRROR="${IRONCLAD_MIRROR:-https://wilsench.my.id/ironclad/pkg}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FILES="SKILL.md templates/standards.md
references/database.md references/presets.md references/extending.md
assets/presets/balanced.yml assets/presets/strict.yml assets/presets/legacy-friendly.yml
scripts/check_schema.py scripts/init_standards.py scripts/drill.py bin/ironclad"

fetch_from() {
  base="$1"; label="$2"
  for f in $FILES; do mkdir -p "$TMP/$(dirname "$f")"; done
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
if [ -n "${IRONCLAD_BASE:-}" ]; then
  fetch_from "$IRONCLAD_BASE" "IRONCLAD_BASE" || { echo "failed: $IRONCLAD_BASE" >&2; exit 1; }
elif fetch_from "$MIRROR" "wilsench.my.id"; then
  :
elif fetch_from "$PRIMARY" "${REPO}@${REF}"; then
  :
else
  echo "failed to fetch from the mirror and from GitHub. Check network, then retry." >&2
  exit 1
fi

if ! head -5 "$TMP/SKILL.md" | grep -q "^name: ${SKILL_NAME}$"; then
  echo "downloaded SKILL.md does not look like ${SKILL_NAME} — aborting" >&2
  exit 1
fi

# ---- install ----------------------------------------------------------------
PRIMARY_DIR=""
for d in $DESTS; do
  [ -d "$d/$SKILL_NAME" ] && echo "updating $d/$SKILL_NAME"
  mkdir -p "$d/$SKILL_NAME"
  rm -rf "$d/$SKILL_NAME"
  mkdir -p "$d/$SKILL_NAME"
  cp -R "$TMP/." "$d/$SKILL_NAME/"
  rm -rf "$d/$SKILL_NAME/bin"
  chmod +x "$d/$SKILL_NAME/scripts/"*.py 2>/dev/null || true
  [ -z "$PRIMARY_DIR" ] && PRIMARY_DIR="$d/$SKILL_NAME"
  echo "  → $d/$SKILL_NAME"
done

# ---- the `ironclad` command -------------------------------------------------
if [ -z "$NO_BIN" ]; then
  BIN_DIR="$HOME/.local/bin"
  mkdir -p "$BIN_DIR"
  sed "s|^IRONCLAD_HOME=.*|IRONCLAD_HOME=\"$PRIMARY_DIR\"|" "$TMP/bin/ironclad" > "$BIN_DIR/$SKILL_NAME"
  chmod +x "$BIN_DIR/$SKILL_NAME"
  # remember where it went, so a second install can replace the entry point
  echo "  → $BIN_DIR/$SKILL_NAME"
  case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "  note: $BIN_DIR is not on PATH — add it to use the bare command" ;;
  esac
fi

# ---- --project: bootstrap and exit -----------------------------------------
if [ -n "$PROJECT" ]; then
  [ -d "$PROJECT" ] || { echo "project not found: $PROJECT" >&2; exit 1; }
  AGENT_DIR="$PROJECT/.agent"
  mkdir -p "$AGENT_DIR"

  if [ -f "$AGENT_DIR/standards.yml" ] && [ "$PRESET" = "balanced" ]; then
    echo "kept    .agent/standards.yml"
  else
    cp "$TMP/assets/presets/$PRESET.yml" "$AGENT_DIR/standards.yml"
    echo "wrote   .agent/standards.yml (preset: $PRESET)"
  fi
  if [ -f "$AGENT_DIR/standards.md" ]; then
    echo "kept    .agent/standards.md"
  else
    cp "$TMP/templates/standards.md" "$AGENT_DIR/standards.md"
    echo "wrote   .agent/standards.md"
  fi
  if [ -z "$POLICY_ONLY" ]; then
    mkdir -p "$PROJECT/scripts/presets"
    cp "$TMP/scripts/check_schema.py" "$PROJECT/scripts/check_schema.py"
    cp "$TMP/assets/presets/"*.yml "$PROJECT/scripts/presets/"
    chmod +x "$PROJECT/scripts/check_schema.py"
    echo "wrote   scripts/check_schema.py + scripts/presets/"
  fi
  echo
  echo "Commit these, or the next teammate gets a different rulebook:"
  echo "  git add .agent scripts && git commit -m 'chore: adopt ironclad standards'"
  exit 0
fi

# ---- done -------------------------------------------------------------------
echo
echo "Installed ($SOURCE). Nothing else to configure."
echo
echo "Try it in any repo — reads only, writes nothing:"
echo "  ironclad check"
echo
echo "Make it permanent:"
echo "  ironclad init"
