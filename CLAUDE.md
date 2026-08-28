# statusui

The design layer shared by three status sites — uisce, esb and lifts, checked out beside this
repo at `../uisce`, `../esb`, `../lifts`. Each site installs this repo as a **uv git
dependency pinned in its `uv.lock`**, and inlines `base.css` and `ui.js` into its pages at
build via `statusui.assemble()`. A change here reaches a site only when its pin moves;
`./rollout.sh` moves all three pins in one command.

## To ship a change

1. Edit `src/statusui/*`. `uv run python -m unittest discover -s tests -t .`;
   `uv run python demo/build.py` and look at `demo/out/index.html` (light, dark, 375px).
   CI runs both on every push, with node installed so the mirror tests cannot skip —
   but only looking at the page catches a change that renders wrong rather than throws.
2. Commit and push here.
3. `./rollout.sh` — bumps each site's `uv.lock`, runs its tests, pushes a `bump-statusui`
   branch and opens the PR. Merge the three PRs.
4. If a site needed anything beyond the pin bump, that was a site change and belongs in that
   site's own `site.css` or inline block, not here.

To test an **unpushed** change against a site, run its build with the local checkout overlaid:
`uv run --with-editable ../statusui <build-cmd>` from that site's directory.

## Constraints

- `src/statusui/__init__.py`: standard library only, and never a floor above the
  consumers' — 3.11, which is what esb's Raspberry Pi runs; ruff here targets it. `src/statusui/ui.js`: ES5 — `var`, `function`, no arrows or
  template literals; that one is a *browser* floor and moves independently of the Python one
  — and nothing runs at load; pages call what they need. Both guarded by `tests/test_ui.py`.
- Every global the bundle declares is listed in `tests/test_ui.py::JS_GLOBALS`; adding one is
  a deliberate act, because no site script may redeclare it. `caption.js` is part of that
  bundle and part of that list: it holds `bindDayCaption` alone so a static page can inline
  the listener without the app, and a test keeps it that size. Consumers get the set from
  `statusui.js_globals()`; a site that parses `ui.js` itself sees only half of it.
- `[hidden] { display: none !important }` is the only `!important` display rule in
  `base.css`; that is the invariant that keeps the sites' view switching working.

## Writing conventions

Never hard-wrap prose in commit messages or PR descriptions: each paragraph is one line, and
the renderer does the wrapping. Line breaks only between paragraphs or list items.

Comments earn their place or they go. Say **why**, not what — never a paraphrase of the line
below, a heading for an obviously-named block, or an explanation of a standard flag. One line
where one will do; if the reasoning needs a paragraph it belongs in the commit message or the
PR, not above the line. This covers CI YAML as much as Python and JS.

## What goes here and what does not

A rule goes in `base.css` when at least two sites want it and none wants it different. The
moment one site needs a different value it becomes a CSS custom property here (like
`--row-cols`, `--stats-cols`) and a one-line override there. Data shapes, renderers, routes,
copy and every domain widget (uisce's health mark and towns table, esb's repeat-fault tag,
lifts' notice text) stay per site. The README carries the full inventory.
