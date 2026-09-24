#!/bin/sh
# Roll the statusui pin forward in every consumer: bump its uv.lock, run its
# tests, commit on a bump-statusui branch, push, open or update the PR. Fails
# fast and leaves the failing site clean; run again after fixing, and sites
# already pinned or already carrying an open bump to this commit are skipped.
set -eu
root="$(cd "$(dirname "$0")" && pwd)"

[ -z "$(git -C "$root" status --porcelain)" ] || { echo "statusui is dirty; commit first" >&2; exit 1; }
git -C "$root" fetch -q origin
[ -z "$(git -C "$root" rev-list origin/main..HEAD)" ] || { echo "statusui has unpushed commits; push first" >&2; exit 1; }
[ -z "$(git -C "$root" rev-list HEAD..origin/main)" ] || { echo "statusui is behind origin/main; pull first" >&2; exit 1; }

rev="$(git -C "$root" rev-parse --short HEAD)"
full="$(git -C "$root" rev-parse HEAD)"
trap '[ -z "${bumped:-}" ] || git -C "$bumped" checkout -q HEAD -- uv.lock' EXIT
# dash skips the EXIT trap on a signal, and Ctrl-C mid-test is the likely one
trap 'exit 130' INT
trap 'exit 143' TERM

for repo in uisce esb lifts; do
  dir="$root/../$repo"
  echo "== $repo"
  [ -z "$(git -C "$dir" status --porcelain)" ] || { echo "$repo is dirty; commit or stash there first" >&2; exit 1; }
  git -C "$dir" checkout -q main
  git -C "$dir" pull -q --ff-only

  old="$(sed -n 's|.*github.com/baz8080/statusui#\([0-9a-f]*\).*|\1|p' "$dir/uv.lock" | head -1)"
  bumped="$dir"
  (cd "$dir" && uv lock -q --upgrade-package statusui)
  if git -C "$dir" diff --quiet -- uv.lock; then
    echo "   already pinned to statusui $rev"
    continue
  fi
  n="$(cd "$dir" && gh pr list --head bump-statusui --state open --json number -q '.[0].number')"
  if [ -n "$n" ]; then
    git -C "$dir" fetch -q origin bump-statusui
    open="$(git -C "$dir" rev-parse FETCH_HEAD)"
    [ "$(git -C "$dir" rev-list --count "main..$open")" = 1 ] ||
      { echo "$repo's bump-statusui has commits besides the pin; sort it out by hand" >&2; exit 1; }
    if [ "$(git -C "$dir" rev-parse "$open^")" = "$(git -C "$dir" rev-parse main)" ] &&
       git -C "$dir" show "$open:uv.lock" | grep -q "statusui#$full"; then
      git -C "$dir" checkout -q -- uv.lock
      echo "   bump to statusui $rev already open"
      continue
    fi
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
  # the branch is this script's, rebuilt from main on every run
  if [ -n "$n" ]; then
    git -C "$dir" push -q --force-with-lease="bump-statusui:$open" -u origin bump-statusui
    (cd "$dir" && gh pr edit "$n" --title "Bump statusui to $rev" --body "$body")
  else
    git -C "$dir" push -q --force -u origin bump-statusui
    (cd "$dir" && gh pr create --title "Bump statusui to $rev" --body "$body")
  fi
  git -C "$dir" checkout -q main
done
