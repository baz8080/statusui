# statusui

The design layer shared by three status sites — [uisce](https://github.com/baz8080/uisce),
[esb](https://github.com/baz8080/esb) and [lifts](https://github.com/baz8080/lifts) — so a UI
fix is written once and rolled out to each site as a pinned dependency bump.

```
src/statusui/__init__.py   shared build helpers, stdlib only, Python 3.11
src/statusui/base.css      design tokens (light + dark) and every shared rule
src/statusui/ui.js         shared browser helpers: plain ES5 globals, nothing runs at load
src/statusui/caption.js    the day-cell caption listener alone, for pages that call only it
src/statusui/freshness.js  the data-age line alone, for a page that wants it without the app
rollout.sh                 bumps each consumer's pin, runs its tests, opens the four PRs
demo/                      python3 demo/build.py → demo/out/index.html, fake data, every component
tests/                     python3 -m unittest discover -s tests -t .
```

## How it reaches a site

Each site declares `statusui` as a **uv git dependency** on this repo, pinned to a commit in
its `uv.lock`. Nothing is fetched at page-load time; the pages stay single-file because
`statusui.assemble()` inlines `base.css` and `ui.js` into each template at the
`<!--UI-CSS-->` and `<!--UI-JS-->` markers during the build. A site's own stylesheet and
script follow the markers and override or extend.

A consumer's redeclaration test must ask `statusui.js_globals()` for the names its own script
may not use, rather than parsing `ui.js`: the bundle is three files now, and a site reading one
of them would pass a script that shadows a name from the other - and would pass by seeing
fewer names, so its own suite cannot catch it - which is why it is a step on the checklist
below rather than something a green rollout can vouch for.

That guard also splits each template on `<!--UI-JS-->` to find where the site's own script
begins. Neither narrow marker contains that string, so a template converted to one of them
needs the split taught every marker - or it raises `IndexError` on the first converted page,
and drops that page from the check once it stops raising.

A template that calls one or two of these takes a narrow marker instead of `<!--UI-JS-->` and
gets that piece, about 1 to 2 KB, rather than 15 KB of app it never calls: `<!--UI-JS-CAPTION-->`
for the day-cell listener, `<!--UI-JS-FRESH-->` for `freshness` and the two helpers it calls.
A template that wants both takes both markers. That is the static pages - lifts'
`s/<station>.html` and rail-delays' month pages - where the body is rendered by Python and the
script is a listener and a line of text. The full bundle still carries both pieces, so an app
page is unaffected and no site script may redeclare any of the names.

An app page that draws its overview from data puts `<!--UI-WAIT-->` in its `<head>` and
`data-wait` on whatever its first render fills or pushes down (the overview, the footer). Those
stay out of the first paint until the page calls `pending(false)`, or until the `load` event or
an 8-second timer if its script never gets that far, so the browser never paints an empty
skeleton for the render to shove down the screen. A page can call `pending(true)` again while it
waits on a shard. Static pages need none of this.

`assemble()` strips the comments out of every inline `<style>` and classic `<script>` on the way
out - a third of an app page's gzipped HTML - with a tokenizer that leaves strings, template
literals and regex literals alone; the mirror tests run again over the stripped bundle. HTML
comments are left, because a site may fill its own markers after `assemble()` returns.

The consumers are expected at `../uisce`, `../esb`, `../lifts` and `../rail-delays` relative
to this one (the same sibling convention as the `../esb-data` and `../lifts-data` repos), and
that is where `rollout.sh` finds them. `rail-delays` is the fourth, of the narrow markers only.

## To ship a change

1. Edit `src/statusui/*` here. `python3 -m unittest discover -s tests -t .`;
   `python3 demo/build.py` and look at it.
2. Commit and push here.
3. `./rollout.sh` - for each site it bumps `uv.lock` to this commit, runs that site's tests,
   pushes a `bump-statusui` branch and opens or updates the PR. Merge the four PRs.
4. If a site needed anything beyond the pin bump, that was a site change, not a UI change —
   and it probably belongs in that site's own block, not here.
5. **Done, as of the freshness split**: all three guards ask `statusui.js_globals()` and
   split on whichever marker their own template carries, so a piece moving between files no
   longer weakens them. What each site still carries is a canary naming one global per file,
   and `freshness` is not in any of those lists yet; a site adds it in its own PR. Nothing in
   a site's suite or a green rollout says it is missing: the guard passes by seeing fewer
   names.

To try an unpushed change against a site first:
`uv run --with-editable ../statusui <build-cmd>` from that site's directory.

## Why not a monorepo (2026-10-02)

Folding statusui and the four sites into one repository was considered and declined.

What it would have bought: a change that needs statusui and the sites together becomes one PR
with every site's suite run on it, and there are no pins, bumps or `rollout.sh`. Since the pin
replaced vendoring on 2026-08-20, esb's pin has moved 19 times and lifts' 16, mostly in two
bursts: the alignment pass on 2026-08-26 (six moves in esb that day) and the first-paint pass on
2026-10-02 (three re-pins per site against a statusui branch under review, then the bump).
Between them, September's four landings were one `rollout.sh` run each.

What it would have cost, for good:

- GitHub Pages serves one site per repository, so keeping the URLs means each old repository
  stays as a shell whose `pages.yml` builds from the monorepo. Every site would live in two
  places: its code in one, its Pages settings and old issues in the other.
- uisce's Build DB commits its JSONL to `main` twice a day and publishes a release per build.
  Neither belongs in a shared repository, so both would move to a new `uisce-data`, reopening
  the 2026-08-21 rejection in uisce's `notes/rules-vs-llm-end-times.md`. The old `uisce`
  repository could still never go: its releases are the only copy of the 9,052 cases the feed
  purged on 2026-08-10.
- The repository boundary that stops one site importing another's code would have to become a
  test.
- With no bump PR there is no pause to look at a site before a statusui change reaches it.

The bursts were deliberate cross-site passes, and the 2026-10-02 one was a performance fix that
could have been made while it was uisce's alone; the costs above do not come and go.
Reconsider if passes that touch statusui and several sites at once become routine, around one
a fortnight.

When a change does need both, land the statusui half first as something no site uses yet (a
new marker, helper or custom property), roll it out as a plain bump, then adopt it in each
site's own PR. Re-pinning sites to a statusui branch under review is what made 2026-10-02
expensive.

## What is shared and what is not

**Shared** — tokens; reset, body, `.wrap`, header; `.banner`; `.tiles/.tile`;
`.controls`, `.months`, `.search/.results`; `.legend`, `.basis`, `.natheading`; the overview
row (`.place > .row`, `.cname`, `.stats`, `.chev`, focus ring); `.gradechip` and grades; `.bar`,
`.daycap` and the hover/touch rules; the drill-down (`.back`, `.chead`, `.chead + .sub`, `.card`,
`.empty`, `.case`, `.tl`, `.nav`); footer and its disclosures; the 640 px reflow. In JS: `esc`, `slug`,
`monthLabel(Long)`, `num`, `plural`, `fmtHours`, `fmtDays`, `when`, `monthTabs`, `dayCells`,
`bindDayCaption`, `cacheBust`, `loadShard`, `pending`, `freshness`, `stampLine`, and the place search:
`searchHits` ranks, `bindSearch` runs the box (lazy index fetch, dropdown, pick); a site
supplies the index file, its counties, the pick handler, and optionally a per-hit note, a
per-hit target in the index and an `href` that turns the hits into real links. A targeted entry
that shares its county's name keeps its own row under the county's, annotated with the county
by default; a site will want its own word for it. In Python: `assemble` (and the `strip_comments` it ends with), `slug`,
`month_label`, `dumps`, `stamp`, `when`, `hours`, `days`, `day_cells`, `sitemap`, `robots`,
`size_report`.

**Per site, on purpose** — the bar colour classes (each site maps its own cell values to hues);
the two layout knobs `--row-cols` and `--stats-cols`; every domain widget (uisce's health mark,
towns table and badges; esb's repeat-fault tag; lifts' notice text); the data shapes, the
renderers, the routes and all the copy.

A rule goes in `base.css` when at least two sites want it and none wants it different. The
moment one site needs a different value, it becomes a custom property here and a one-line
override there.
