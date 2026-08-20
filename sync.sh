#!/bin/sh
# Copy the shared UI into a consumer: sync.sh <dest-dir>, e.g. esb_site/ui.
# Writes <dest>/UPSTREAM with the statusui commit the copy came from — but
# only when a file actually changed, so a sync with nothing to bring in
# leaves the consumer's tree untouched and says so.
set -eu
src="$(cd "$(dirname "$0")" && pwd)"
dest="$1"
mkdir -p "$dest"

changed=0
for f in base.css ui.js statusui.py __init__.py; do
  if ! cmp -s "$src/ui/$f" "$dest/$f" 2>/dev/null; then
    cp "$src/ui/$f" "$dest/$f"
    changed=1
  fi
done

rev="$(git -C "$src" rev-parse --short HEAD 2>/dev/null || echo unknown)"
if [ -n "$(git -C "$src" status --porcelain -- ui 2>/dev/null)" ]; then rev="$rev-dirty"; fi

if [ "$changed" = 0 ] && [ -f "$dest/UPSTREAM" ]; then
  echo "no changes — vendored copy already matches statusui $rev (stamped $(cat "$dest/UPSTREAM"))"
  exit 0
fi
echo "$rev" > "$dest/UPSTREAM"
echo "statusui $rev -> $dest"
