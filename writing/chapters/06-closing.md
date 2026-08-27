# 6. Closing: a layer is a set of promises
*~6 min read · the repo as of 27 August 2026*

*Where we are:* the end of the first week. Seven pull requests, thirty-two commits, 19–26
August 2026. This chapter is the inventory, the promises, the open threads, and the uisce
comparisons collected in one place.

## What the repo is, in one paragraph

statusui is the design layer of three status sites: 245 lines of CSS, 300 of JavaScript
and 190 of Python (measured 27 Aug 2026), with zero runtime dependencies and a dev-tool
list one item long. Each site pins it to an exact commit in a lock file; a build calls
`assemble()` to inline the two browser files into every page, so readers still get
single-file pages and never fetch this repo's name. A change ships by `rollout.sh`
opening three pin-bump PRs, each gated on that site's own tests. 410 lines of tests —
38 of them, a third needing `node` — hold the Python and JavaScript halves to identical
output, the ES5 and 3.11 floors, the contrast claims, the globals treaty and the one
`!important` invariant. Growth is by promotion only: code enters when a second site
starts writing it, with its constants turned into parameters.

## The promises, collected

Reading the week back, the repo's real content is not the 735 lines — it is a short list
of promises, each with a mechanism that keeps it:

| Promise | Kept by |
|---|---|
| A reader costs one request per page | `assemble()` inlines at build; nothing is linked at load |
| Nothing runs until a page asks | the top-level-statement walk in the tests (ch 1) |
| No site script collides with the layer | `JS_GLOBALS` here + each site's `test_ui_globals` (ch 3) |
| Both languages format a figure identically | the node mirror, un-skippable in CI (chs 3–4) |
| Every `*-text` token reads at 4.5:1, both schemes | contrast computed in the tests (chs 1, 3) |
| `[hidden]` always wins | the only-`!important`-display-rule test (ch 1) |
| The floor is where the consumers stand | 3.11 for the Pi, checked by a CI leg and by `uv`'s resolver (ch 4) |
| Old browsers run `ui.js` as written | the ES5 guard; no transpile step exists (chs 3–4) |
| What a site builds with is recorded | the pin in `uv.lock`; drift is visible, not silent (ch 2) |
| A deployed site never renders half a change | additions land here first, deletions ride the pin bump (ch 5) |

None of these promises existed as *mechanisms* on 19 August. Most existed as habits, and
chapter 2 is the measured record of what habits are worth across three repositories: one
day, five commits of drift, zero failures reported.

## What this repo cannot see

The honest inventory has a second column. **It cannot see rendering.** CI catches a
change that throws; a change that renders *wrong* — a colour that reads badly on a real
phone, a strip that wraps — is invisible to every test here, which is why "look at the
demo: light, dark, 375 pixels" is a written step of the change loop and not a nicety.
**It cannot see its consumers.** Nothing here knows what the sites' pages do with the
layer; the globals treaty is enforced by tests that live *there*, and a site that stops
running them leaves the treaty unsigned. **It cannot make a pin move.** A site can sit on
an old commit indefinitely; the drift is recorded rather than prevented, and `rollout.sh`
is a hand that must be run. **And its browser floor is asserted, not experienced** — the
ES5 guard is a regex over syntax, and no elderly browser is in the loop anywhere; the
mirror runs under one modern node. Each of these is a known limit accepted on purpose,
which is as much as a week-old repo can honestly claim.

One open thread, in the uisce series' tradition of ending on a stale line: the package
docstring still says "Python 3.9 syntax: the consumers' floor" — the floor moved to 3.11
in PR #5 and this sentence was missed (measured 27 Aug 2026). Chapter 4's whole argument,
restated by the repo itself: a fact written where no test reads it is a fact on borrowed
time. It will be some small commit's footnote.

## How uisce does it — the collected differences

The series promised the contrasts in one table. Neither column is the better practice;
each is the fit for what its repo is, and the interesting part is *why* the same author
under the same conventions lands in different places one directory apart.

| | uisce (the site) | statusui (the layer) |
|---|---|---|
| Subject | a feed, a database, readers | three other repos' shared look |
| Its numbers | person-hours, populations, grades | line counts, test counts, commit distances |
| Hard truth problem | the world: is the model's reading right? — hand labels, confidence bounds | itself: do two translations agree? — the mirror, no ground truth |
| Tests | pytest, a data stack, 443 tests | stdlib `unittest` + a node binary, 38 tests, zero dependencies |
| Interpreter | 3.14, one CI version | develops on 3.14, promises 3.11 (a Raspberry Pi's), CI runs both |
| Floors | its own machines' | two, both borrowed: Python from the slowest consumer, ES5 from the readers' browsers |
| Shipping | push to main, live in minutes | merge changes nothing; three pin-bump PRs, each behind that site's tests |
| A mistake's blast radius | one site, until the next push | three sites, wearing their names — hence the un-skippable CI |
| Growth | invention: build what readers need, sole user, same day | selection: second-hand code only, promoted on the second user |
| Pace | 61 PRs, ~8 weeks | 7 PRs, one week |
| This series' machinery | source packets generated from 61 PRs | none: `git log --reverse` fits in an evening |

The last row is the honest summary of the whole comparison: a layer is *supposed* to have
the shorter story. Its ambition is to be the part of three histories that stopped needing
to be told three times.

## Glossary

The concept boxes, one line each:

- **design layer** (ch 1) — the decisions three pages have agreed to make identically,
  written once; membership test: already the same everywhere, on purpose.
- **stamp** (ch 2) — provenance written as a side effect of an action will drift from the
  content; derive it from the content or use machinery that does (a lock file).
- **mirror** (ch 3) — paired implementations held to identical output; asserts `f(x) =
  g(x)` with neither side the specification, so it proves consistency, never correctness.
- **floor** (ch 4) — a promise to your slowest consumer; below every consumer is slack,
  above any one is a broken promise the resolver rejects; the floor and the interpreter
  you develop on are different questions.
- **promoted on the second user** (ch 5) — one user is no evidence; the second user wins
  the bet and locates the parameters; duplication in the window is the accepted price.
- **the deploy gap** (chs 2, 5) — the window between merging here and pins moving there;
  a hazard for deletions (they ride the pin bump), a staging area for everything else.

## The last word

The uisce series ends by weighing what its site can and cannot say about the water. This
repo's equivalent is smaller and stranger: everything it "says", three other websites say
for it, in their own names, to readers who will never hear of it. The week's work was
arranging to be *safely invisible* — pinned so its absence of news is provable, mirrored
so its two voices cannot disagree, floored where its consumers actually stand, and
forbidden from having ideas until two sites have had them first. A design layer at rest
is three sites that look like one decision. As of 27 August 2026, they do.

## Notes

- Inventory (245/300/190 source lines, 410 test lines, 38 tests, `dependencies = []`,
  ruff as the only dev tool, 42-line `rollout.sh`, 41-line `ci.yml`): measured against
  the working tree, 27 Aug 2026. 735 = 245 + 300 + 190.
- Seven PRs, thirty-two commits, 19–26 Aug 2026: `git log`, measured 27 Aug 2026.
- uisce column: 443 tests from the uisce series ch 16; 61 PRs / ~8 weeks from its intro
  and ledger; pytest from `rollout.sh`'s uisce leg (the script runs `pytest` there and
  `unittest` for the siblings); 3.14 from statusui PR #5's body.
- `JS_GLOBALS` count (26 names) and the promise table's mechanisms verified against
  `tests/test_ui.py`, 27 Aug 2026.
- Stale docstring: `src/statusui/__init__.py` line 4 vs PR #5, observed 27 Aug 2026.
