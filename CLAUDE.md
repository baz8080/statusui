# statusui

The design layer shared by three status sites — uisce, esb and lifts, checked out beside this
repo at `../uisce`, `../esb`, `../lifts`. Nothing here is installed anywhere: each site holds
a **vendored copy** of `ui/` (`src/uisce/ui`, `esb_site/ui`, `lift_site/ui`) refreshed by its
`scripts/sync-ui.sh`, and inlines `base.css` and `ui.js` into its pages at build. A change here
reaches a site only when that site syncs; the sites' `tests/test_ui_vendored.py` fail if their
copy drifts from this checkout.

## To ship a change

1. Edit `ui/*`. `python3 -m unittest discover -s tests -t .`; `python3 demo/build.py` and look
   at `demo/out/index.html` (light, dark, 375px).
2. Commit and push here.
3. In each site: `scripts/sync-ui.sh`, its tests, a build, a look, a commit — three PRs.
4. If a site needed anything beyond the sync, that was a site change and belongs in that site's
   own `site.css` or inline block, not here.

## Constraints

- `ui/statusui.py`: standard library only, Python 3.9 syntax (esb/lifts' floor; ruff here
  targets it). `ui/ui.js`: ES5 — `var`, `function`, no arrows or template literals — and
  nothing runs at load; pages call what they need. Both guarded by `tests/test_ui.py`.
- Every global `ui.js` declares is listed in `tests/test_ui.py::JS_GLOBALS`; adding one is a
  deliberate act, because no site script may redeclare it.
- `[hidden] { display: none !important }` is the only `!important` display rule in
  `base.css`; that is the invariant that keeps the sites' view switching working.

## Writing conventions

Never hard-wrap prose in commit messages or PR descriptions: each paragraph is one line, and
the renderer does the wrapping. Line breaks only between paragraphs or list items.

## What goes here and what does not

A rule goes in `base.css` when at least two sites want it and none wants it different. The
moment one site needs a different value it becomes a CSS custom property here (like
`--row-cols`, `--stats-cols`) and a one-line override there. Data shapes, renderers, routes,
copy and every domain widget (uisce's health mark and towns table, esb's repeat-fault tag,
lifts' notice text) stay per site. The README carries the full inventory.
