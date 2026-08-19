#!/bin/sh
# Copy the shared UI into a consumer: sync.sh <dest-dir>, e.g. esb_site/ui.
# Writes <dest>/UPSTREAM with the statusui commit the copy came from.
set -eu
src="$(cd "$(dirname "$0")" && pwd)"
dest="$1"
mkdir -p "$dest"
for f in base.css ui.js statusui.py __init__.py; do
  cp "$src/ui/$f" "$dest/$f"
done
rev="$(git -C "$src" rev-parse --short HEAD 2>/dev/null || echo unknown)"
if [ -n "$(git -C "$src" status --porcelain -- ui 2>/dev/null)" ]; then rev="$rev-dirty"; fi
echo "$rev" > "$dest/UPSTREAM"
echo "statusui $rev -> $dest"
