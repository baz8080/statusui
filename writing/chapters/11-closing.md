# 11. Closing: a layer is a set of promises
*~9 min read · the repo as of 12 September 2026*

*Where we are:* the end. Fourteen pull requests, sixty-one commits, 19 August to 5 September
2026. This chapter is the inventory, the promises, the open threads, and the uisce
comparisons collected in one place.

## What the repo is, in one paragraph

statusui is the design layer of three status sites: 246 lines of CSS, 320 of JavaScript in
`ui.js`, 23 more in `caption.js` and 231 of Python (measured 12 Sep 2026), with zero runtime
dependencies and a dev-tool list one item long. Each site pins it to an exact commit in a
lock file; a build calls `assemble()` to inline the shared files into every page, so readers
still get single-file pages and never fetch this repo's name. A page that wants the whole app
takes the 15.9 KB bundle; a static page of day bars takes the 1.1 KB caption listener alone.
A change ships by `rollout.sh` opening three pin-bump PRs, each gated on that site's own
tests. 675 lines of tests, 54 of them, 23 needing `node`, hold the Python and JavaScript
halves to identical output, the ES5 and 3.11 floors, the contrast of every text token and
every grade chip, the published set of globals, the A to F letter set and the one
`!important` invariant. That `node` share has gone from a third of a smaller suite to nearly
half of this one, which is what a layer looks like when its JavaScript grows a search box and
a published contract: the parts worth guarding are increasingly the parts Python cannot see. Growth is by promotion only: code enters when a second site starts
writing it, with its constants turned into parameters, and chapter 10 is the correction to
that rule.

## The promises, collected

Reading the month back, the repo's real content is not the 820 lines of source. It is a short
list of promises, each with a mechanism that keeps it:

| Promise | Kept by |
|---|---|
| A reader costs one request per page | `assemble()` inlines at build; nothing is linked at load |
| A static page pays for the listener, not the app | the caption marker, and a test that fails if `caption.js` grows a body (ch 7) |
| Nothing runs until a page asks | the top-level-statement walk in the tests (ch 1) |
| The two files join without eating a line | the newline in `ui_js()`, checked with a trailing comment (ch 7) |
| No site script collides with the layer | `js_globals()` here, and each site's guard, once it asks (chs 3, 7) |
| Both languages format a figure identically | the node mirror, un-skippable in CI (chs 3, 4) |
| Every text token reads at 4.5:1, both schemes | contrast computed in the tests (chs 1, 3) |
| Every grade chip can be read, and every letter has a chip | the pairing and letter-set tests (ch 9) |
| `[hidden]` always wins | the only-`!important`-display-rule test (ch 1) |
| The floor is where the consumers stand | 3.11 for the Pi, a CI leg and `uv`'s resolver (ch 4) |
| Old browsers run the bundle as written | the ES5 guard, now including `class` (chs 3, 7) |
| What a site builds with is recorded | the pin in `uv.lock`; drift is visible, not silent (ch 2) |
| A deployed site never renders half a change | additions land here first, deletions ride the pin bump (chs 5, 10) |
| The layer asserts only what its inputs prove | a hedged sentence, and a default that shows the ambiguity (ch 10) |

One row of that table is different from the others and the difference is the month's main
lesson. "No site script collides with the layer" is the only promise whose mechanism stops at
this repository's edge: `js_globals()` is published here, and whether a consumer asks it or
keeps parsing `ui.js` is a checklist item in three other repositories that nothing here can
observe. Chapter 7 spent an evening and four commits trying to make it a mechanism, and the
gate failed open in a new way at every review round before being deleted. A promise that crosses a repository
boundary degrades to documentation at the boundary, and the honest response is to make the
documented step small and single rather than to write a check that cannot see the failure.

## What this repo cannot see

**It cannot see rendering.** CI catches a change that throws; a change that renders wrong is
invisible to every test here, which is why "look at the demo, light, dark, 375 pixels" is a
written step rather than a nicety. Chapter 9 is what that costs: the demo fixture rendered
four of the seven chips, so the unreadable one went unnoticed until a test resolved the pairs
by name.

**It cannot see its consumers.** Not their scripts, not their guards, not whether the
checklist step is done. The set of globals is published; the asking is voluntary.

**It cannot see why its data is old**, which chapter 10 is entirely about, and by extension it
cannot see anything upstream of the values a site hands it.

**It cannot make a pin move.** A site can sit on an old commit indefinitely. The drift is
recorded rather than prevented, and `rollout.sh` is a hand that must be run.

**And its browser floor is asserted, not experienced.** The ES5 guard is a regex over syntax
plus an engine check that runs on one modern node. No elderly browser is in the loop anywhere.

## Open threads

Two, both of them the same shape as everything else in this series.

The package docstring still says "Standard library only, Python 3.9 syntax: the consumers'
floor". The floor moved to 3.11 in PR #5 on 26 August. I noted the stale line in this
chapter's first draft on 27 August; it is still there on 12 September (measured), three weeks
and seven pull requests later, in a repository that has since written down two separate rules
about writing things down. A fact stated where no test reads it is a fact on borrowed time,
and the borrowing compounds.

README step 5 is open in all three sites: every consumer's redeclaration guard still reads
`ui.js` off disk, and every consumer's template split still knows one marker. Neither that
site's suite nor a green rollout can tell anyone it is outstanding, because the guard passes
by seeing fewer names. It will be closed one site at a time, by hand, alongside a pin bump.

## How uisce does it: the collected differences

Neither column is the better practice. Each is the fit for what its repo is, and the
interesting part is why the same author under the same conventions lands in different places
one directory apart.

| | uisce (the site) | statusui (the layer) |
|---|---|---|
| Subject | a feed, a database, readers | three other repos' shared look |
| Its numbers | person-hours, populations, grades | line counts, test counts, kilobytes, contrast ratios |
| Hard truth problem | the world: is the model's reading right? Hand labels and confidence bounds | itself: do two translations agree? A mirror, with no ground truth |
| Tests | pytest, a data stack, 443 tests | stdlib `unittest` plus a node binary, 54 tests, zero dependencies |
| Interpreter | 3.14, one CI version | develops on 3.14, promises 3.11 (a Raspberry Pi's), CI runs both |
| Floors | its own machines' | two, both borrowed: Python from the slowest consumer, ES5 from readers' browsers |
| Shipping | push to main, live in minutes | merge changes nothing; three pin-bump PRs, each behind that site's tests |
| A mistake's blast radius | one site, until the next push | three sites, wearing their names, hence the un-skippable CI |
| Enforcement | can check its invariants: one repo owns both sides | cross-repo contracts degrade to a checklist at the boundary (ch 7) |
| What it may claim | caveats on its own page: a floor, an assumption, a radius | no page to disclaim on, so it hedges or stays silent (ch 10) |
| Growth | invention: build what readers need, sole user, same day | selection: second-hand code, promoted on the second user, minus the differences that were mistakes |
| Pace | 61 PRs, about 8 weeks | 14 PRs, about 3.5 weeks |
| This series' machinery | source packets generated from 61 PRs | none: `git log --reverse` still fits in an evening |

The last row is the honest summary. A layer is supposed to have the shorter story. Its
ambition is to be the part of three histories that stopped needing to be told three times.

## Glossary

The concept boxes, one line each:

- **design layer** (ch 1). The decisions three pages have agreed to make identically, written
  once; membership test: already the same everywhere, on purpose.
- **stamp** (ch 2). Provenance written as a side effect of an action will drift from the
  content; derive it from the content, or use machinery that does.
- **mirror** (ch 3). Paired implementations held to identical output; asserts `f(x) = g(x)`
  with neither side the specification, so it proves consistency, never correctness.
- **floor** (ch 4). A promise to your slowest consumer; below every consumer is slack, above
  any one is a broken promise the resolver rejects; the floor and the interpreter you develop
  on are different questions.
- **promoted on the second user** (ch 5, corrected in ch 10). One user is no evidence; the
  second wins the bet and locates the differences. It does not tell you which differences are
  real, and parameterising a mistake ships it to everyone.
- **the deploy gap** (chs 2, 5, 10). The window between merging here and pins moving there. A
  hazard for deletions, a staging area for everything else, and compatible in only one
  direction at a time.
- **shipped, not derived** (ch 6). When a value is produced by one system and consumed by
  another, send the value. Recomputing it at the far end means two functions that must agree
  forever, and they will not.
- **a guard that passes by seeing less** (ch 7). A check derived from the thing it checks goes
  green when coverage is lost. Derive it from something that does not move when the guarded
  thing moves.
- **a convention lives where the work happens** (ch 8). A rule is only in force in the
  contexts that can read it; for a fresh clone, the repository is the entire world.
- **a value with no name cannot be checked by name** (ch 9). Give the derived value a token
  rather than building a parser to evaluate the derivation.
- **a page can see its own age, not its cause** (ch 10). A component may report what it
  observes; naming a mechanism it cannot see is a guess made on everyone's behalf.

## The last word

The uisce series ends by weighing what its site can and cannot say about the water. This
repo's equivalent is smaller and stranger: everything it says, three other websites say for
it, in their own names, to readers who will never hear of it. A month's work was arranging to
be safely invisible. Pinned, so its absence of news is provable. Mirrored, so its two voices
cannot disagree. Floored where its consumers actually stand. Forbidden from having ideas
until two sites have had them first, and now forbidden from keeping a difference just because
two sites had one. A design layer at rest is three sites that look like one decision. As of
12 September 2026, they do, and there is a checklist item outstanding in each of them.

## Notes

- Inventory measured against the working tree, 12 Sep 2026: `base.css` 246 lines,
  `ui.js` 320, `caption.js` 23, `__init__.py` 231 (820 source lines); `tests/test_ui.py`
  675 lines and 54 tests, 12 of them in node-gated classes; `dependencies = []`, ruff the
  only dev tool; `rollout.sh` 42 lines, `ci.yml` 41; `statusui.ui_js()` 16,270 bytes,
  `caption_js()` 1,123; `js_globals()` 26 names.
- Fourteen PRs and sixty-one commits, 19 Aug to 5 Sep 2026: `git log` and the PR list,
  measured 12 Sep 2026.
- uisce column: 443 tests from the uisce series ch 16; 61 PRs and about 8 weeks from its
  intro and ledger; pytest from `rollout.sh`'s uisce leg; 3.14 from PR #5's body.
- Stale docstring: `src/statusui/__init__.py` line 4 against PR #5, observed 27 Aug and
  again 12 Sep 2026. README step 5 read in the working tree, 12 Sep 2026.
