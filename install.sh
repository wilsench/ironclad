#!/usr/bin/env bash
# Install ironclad for the agent you actually use.
#
#   curl -fsSL https://raw.githubusercontent.com/<owner>/ironclad/main/install.sh | bash
#   ./install.sh --target claude      # ~/.claude/skills
#   ./install.sh --target hermes      # ~/.hermes/skills
#   ./install.sh --target agents      # ~/.agents/skills  (Codex, Cursor, generic)
#   ./install.sh --dir /path/to/skills
#
# Copies the skill directory only. It never touches your other skills.

set -euo pipefail

SKILL_NAME="ironclad"
REPO="${REPO:-<owner>/ironclad}"
REF="${REF:-main}"
TARGET="auto"
DEST=""

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:?--target needs a value}"; shift 2 ;;
    --dir)    DEST="${2:?--dir needs a value}"; shift 2 ;;
    --ref)    REF="${2:?--ref needs a value}"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$DEST" ]; then
  case "$TARGET" in
    auto)
      if   [ -d "$HOME/.hermes" ];   then DEST="$HOME/.hermes/skills"
      elif [ -d "$HOME/.claude" ];   then DEST="$HOME/.claude/skills"
      elif [ -d "$HOME/.agents" ];   then DEST="$HOME/.agents/skills"
      else DEST="$HOME/.agents/skills"
      fi ;;
    hermes) DEST="$HOME/.hermes/skills" ;;
    claude) DEST="$HOME/.claude/skills" ;;
    agents) DEST="$HOME/.agents/skills" ;;
    *) echo "unknown target: $TARGET (use hermes, claude, agents, or --dir)" >&2; exit 2 ;;
  esac
fi

BASE="https://raw.githubusercontent.com/${REPO}/${REF}/skills/${SKILL_NAME}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Fetching ${SKILL_NAME} from ${REPO}@${REF} ..."
FILES="SKILL.md templates/standards.md \
  references/database.md references/presets.md references/extending.md \
  assets/presets/balanced.yml assets/presets/strict.yml assets/presets/legacy-friendly.yml \
  scripts/check_schema.py scripts/init_standards.py"
for f in $FILES; do
  mkdir -p "$TMP/$(dirname "$f")"
  curl -fsSL "$BASE/$f" -o "$TMP/$f"
done

if [ -d "$DEST/$SKILL_NAME" ]; then
  echo "Replacing existing install at $DEST/$SKILL_NAME"
  rm -rf "$DEST/$SKILL_NAME"
fi
mkdir -p "$DEST"
mv "$TMP/$SKILL_NAME" "$DEST/$SKILL_NAME" 2>/dev/null || { mkdir -p "$DEST/$SKILL_NAME"; cp -R "$TMP/." "$DEST/$SKILL_NAME/"; }
chmod +x "$DEST/$SKILL_NAME/scripts/"*.py 2>/dev/null || true

echo "Installed to: $DEST/$SKILL_NAME"
echo
echo "Next: in your repo, bootstrap the policy file"
echo "  python3 $DEST/$SKILL_NAME/scripts/init_standards.py . --with-checker"
