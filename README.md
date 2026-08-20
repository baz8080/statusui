# statusui

The design layer shared by three status sites — [uisce](https://github.com/baz8080/uisce),
[esb](https://github.com/baz8080/esb) and [lifts](https://github.com/baz8080/lifts) — so a UI
fix is written once and rolled out to each site as a pinned dependency bump.

```
src/statusui/__init__.py   shared build helpers, stdlib only, Python 3.9 syntax
src/statusui/base.css      design tokens (light + dark) and every shared rule
src/statusui/ui.js         shared browser helpers: plain ES5 globals, nothing runs at load
rollout.sh                 bumps each consumer's pin, runs its tests, opens the three PRs
demo/                      python3 demo/build.py → demo/out/index.html, fake data, every component
tests/                     python3 -m unittest discover -s tests -t .
```

## How it reaches a site

Each site declares `statusui` as a **uv git dependency** on this repo, pinned to a commit in
its `uv.lock`. Nothing is fetched at page-load time; the pages stay single-file because
`statusui.assemble()` inlines `base.css` and `ui.js` into each template at the
`<!--UI-CSS-->` and `<!--UI-JS-->` markers during the build. A site's own stylesheet and
script follow the markers and override or extend.

The three site repos are expected at `../uisce`, `../esb` and `../lifts` relative to this one
(the same sibling convention as the `../esb-data` and `../lifts-data` repos) — that is where
`rollout.sh` finds them.

## To ship a change

1. Edit `src/statusui/*` here. `python3 -m unittest discover -s tests -t .`;
   `python3 demo/build.py` and look at it.
2. Commit and push here.
3. `./rollout.sh` — for each site it bumps `uv.lock` to this commit, runs that site's tests,
   pushes a `bump-statusui` branch and opens the PR. Merge the three PRs.
4. If a site needed anything beyond the pin bump, that was a site change, not a UI change —
   and it probably belongs in that site's own block, not here.

To try an unpushed change against a site first:
`uv run --with-editable ../statusui <build-cmd>` from that site's directory.

## What is shared and what is not

**Shared** — tokens; reset, body, `.wrap`, header; `.banner`, `.dot`; `.tiles/.tile`;
`.controls`, `.months`, `.search/.results`; `.legend`, `.basis`, `.natheading`; the overview
row (`.place > .row`, `.cname`, `.stats`, `.chev`, focus ring); `.gradechip` and grades; `.bar`,
`.daycap` and the hover/touch rules; the drill-down (`.back`, `.chead`, `.card`, `.empty`,
`.case`, `.tl`, `.nav`); footer and its disclosures; the 640 px reflow. In JS: `esc`, `slug`,
`monthLabel(Long)`, `num`, `plural`, `fmtHours`, `fmtDays`, `when`, `monthTabs`, `dayCells`,
`bindDayCaption`, `cacheBust`, `loadShard`, `stampLine`. In Python: `assemble`, `slug`,
`month_label`, `dumps`, `stamp`, `when`, `hours`, `days`, `day_cells`, `sitemap`, `robots`,
`size_report`.

**Per site, on purpose** — the bar colour classes (each site maps its own cell values to hues);
the two layout knobs `--row-cols` and `--stats-cols`; every domain widget (uisce's health mark,
towns table and badges; esb's repeat-fault tag; lifts' notice text); the data shapes, the
renderers, the routes and all the copy.

A rule goes in `base.css` when at least two sites want it and none wants it different. The
moment one site needs a different value, it becomes a custom property here and a one-line
override there.
