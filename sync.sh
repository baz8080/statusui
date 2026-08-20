#!/bin/sh
# Copy the shared UI into a consumer: sync.sh <dest-dir>, e.g. esb_site/ui.
# Writes <dest>/UPSTREAM with the statusui commit the copy came from. A sync
# with nothing to bring in leaves the consumer's tree untouched and says so —
# unless the stamp names no commit, which is how a dirty sync gets its hash
# once the change is committed here.
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

stamp="$(cat "$dest/UPSTREAM" 2>/dev/null || echo "")"
if [ "$changed" = 0 ]; then
  case "$stamp" in
    "" | unknown | *-dirty) ;;
    *)
      echo "no changes — vendored copy already matches statusui $rev (stamped $stamp)"
      exit 0
      ;;
  esac
  echo "$rev" > "$dest/UPSTREAM"
  echo "statusui $rev -> $dest (stamp only, files already matched)"
  exit 0
fi
echo "$rev" > "$dest/UPSTREAM"
echo "statusui $rev -> $dest"
