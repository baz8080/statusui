#!/bin/sh
# Roll the statusui pin forward in every consumer: bump its uv.lock, run its
# tests, commit on a bump-statusui branch, push, open the PR. Fails fast; run
# again after fixing — repos already bumped are skipped as "already pinned".
set -eu
root="$(cd "$(dirname "$0")" && pwd)"

[ -z "$(git -C "$root" status --porcelain)" ] || { echo "statusui is dirty; commit first" >&2; exit 1; }
git -C "$root" fetch -q origin
[ -z "$(git -C "$root" rev-list origin/main..HEAD)" ] || { echo "statusui has unpushed commits; push first" >&2; exit 1; }
[ -z "$(git -C "$root" rev-list HEAD..origin/main)" ] || { echo "statusui is behind origin/main; pull first" >&2; exit 1; }

rev="$(git -C "$root" rev-parse --short HEAD)"

for repo in uisce esb lifts; do
  dir="$root/../$repo"
  echo "== $repo"
  [ -z "$(git -C "$dir" status --porcelain)" ] || { echo "$repo is dirty; commit or stash there first" >&2; exit 1; }
  git -C "$dir" checkout -q main
  git -C "$dir" pull -q --ff-only

  old="$(sed -n 's|.*github.com/baz8080/statusui#\([0-9a-f]*\).*|\1|p' "$dir/uv.lock" | head -1)"
  (cd "$dir" && uv lock -q --upgrade-package statusui)
  if git -C "$dir" diff --quiet -- uv.lock; then
    echo "   already pinned to statusui $rev"
    continue
  fi

  case "$repo" in
    uisce) (cd "$dir" && uv run -q pytest -q) ;;
    *)     (cd "$dir" && uv run -q python -m unittest discover -s tests -t .) ;;
  esac

  # what the pin move carries, for the commit and PR body
  body="$(git -C "$root" log --no-decorate --oneline "$old..HEAD" 2>/dev/null || echo "statusui @ $rev")"
  git -C "$dir" checkout -q -B bump-statusui main
  git -C "$dir" add uv.lock
  git -C "$dir" commit -q -m "Bump statusui to $rev" -m "$body"
  git -C "$dir" push -q -u origin bump-statusui
  (cd "$dir" && gh pr create --title "Bump statusui to $rev" --body "$body")
  git -C "$dir" checkout -q main
done
