# statusui

The design layer shared by three status sites — [uisce](https://github.com/baz8080/uisce),
[esb](https://github.com/baz8080/esb) and [lifts](https://github.com/baz8080/lifts) — so a UI
fix is written once and carried to each site by a file copy rather than ported by hand.

```
ui/base.css      design tokens (light + dark) and every shared rule
ui/ui.js         shared browser helpers: plain ES5 globals, nothing runs at load
ui/statusui.py   shared build helpers, stdlib only, Python 3.9 syntax
sync.sh          copies ui/ into a consumer and stamps UPSTREAM with this repo's commit
demo/            python3 demo/build.py → demo/out/index.html, every component with fake data
tests/           python3 -m unittest discover -s tests -t .
```

## How it reaches a site

Each site keeps a **vendored copy** under `<site_pkg>/ui/` — `esb_site/ui`, `lift_site/ui`,
`src/uisce/ui` — committed like any other file. Nothing is installed and nothing is fetched at
build or in CI; the pages stay single-file because `statusui.assemble()` inlines `base.css`
and `ui.js` into each template at the `<!--UI-CSS-->` and `<!--UI-JS-->` markers. A site's
own stylesheet and script follow the markers and override or extend.

This repo is expected at `../statusui` relative to each site, the way the data repos sit at
`../esb-data` and `../lifts-data`. Each site has a test that compares its vendored copy to
`../statusui/ui` when that directory exists, and skips when it does not.

## To ship a change

1. Edit `ui/*` here. `python3 -m unittest discover -s tests -t .`; `python3 demo/build.py` and
   look at it.
2. Commit and push here.
3. In each site: `scripts/sync-ui.sh`, run its tests, build it, look at it, commit.
4. If a site needed anything beyond the sync, that was a site change, not a UI change — and it
   probably belongs in that site's own block, not here.

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
