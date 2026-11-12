#!/usr/bin/env bash
# Copy the current skill payload to the public mirror that install.sh reads.
# Run after editing SKILL.md, references/, scripts/, templates/ or presets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/home/wilsench/htdocs/wilsench.my.id/public/ironclad/pkg}"
SKILL="$ROOT/skills/ironclad"
OWNER="wilsench:wilsench"

[ -d "$DEST" ] || { echo "no mirror dir: $DEST" >&2; exit 1; }

mkdir -p "$DEST"/{assets/presets,bin,references,scripts,templates}
cp "$SKILL/SKILL.md"                 "$DEST/"
cp "$SKILL"/references/*.md          "$DEST/references/"
cp "$SKILL"/scripts/*.py             "$DEST/scripts/"
cp "$SKILL"/templates/*.md           "$DEST/templates/"
cp "$SKILL"/assets/presets/*.yml     "$DEST/assets/presets/"
cp "$SKILL"/bin/ironclad             "$DEST/bin/ironclad"
chmod +x "$DEST/bin/ironclad"
chown -R "$OWNER" "$DEST"

# the installer itself lives beside the docs, not inside pkg/
cp "$ROOT/install.sh" "$(dirname "$DEST")/install.sh"
chown "$OWNER" "$(dirname "$DEST")/install.sh"

echo "mirror synced: $(find "$DEST" -type f | wc -l) files → $DEST"
