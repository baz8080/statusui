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

  # A site that reads ui.js itself sees half the bundle since caption.js split
  # off, and its redeclaration guard silently stops covering what moved - it
  # passes by seeing fewer names, so the site's own suite cannot catch it. The
  # pin and that switch have to land together, by hand, in that site's repo:
  # the switch needs a statusui this rollout has not given it yet. So skip the
  # site rather than carry a pin that quietly weakens it - and only that site,
  # because the others are not blocked by it. Asking js_globals() is the test,
  # not the quoting of a filename: a site is clear the moment it asks.
  if ! grep -rql 'js_globals(' "$dir/tests" 2>/dev/null &&
     grep -rql 'ui\.js' "$dir/tests" 2>/dev/null; then
    echo "   skipped: $repo parses ui.js; bump it by hand, with the switch to js_globals()" >&2
    git -C "$dir" checkout -q -- uv.lock
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
