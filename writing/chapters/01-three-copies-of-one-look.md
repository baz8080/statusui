# 1. Three copies of one look
*~7 min read · birth commit and PR #2 · 19–20 August 2026*

*Where we are:* the start. Three status sites — uisce (water), esb (electricity), lifts
(rail lifts) — each carry their own copy of a deliberately identical design. On 19 August
the shared part becomes this repository.

## The question that opened this stretch

The immediate trigger was told in the uisce series (chapter 14): a contrast fix landed on the
water site on 18 August and never reached the electricity site, because there was no mechanism
by which it could — only a habit, and habits don't fail loudly. The question for this repo was
narrower and came first: *which lines, exactly, are "the shared part"?* Three stylesheets had
been written by looking at each other. Nobody had ever listed what they actually agreed on.

## What changed

### The extraction (commit `c9f8beb`, 19 August)

The birth commit answers the question by measurement rather than intention. Its message is
the whole method: the tokens take uisce's contrast-checked values, the per-site layout widths
become two custom properties, "and the rest is what at least two sites already had word for
word." Where all three sites agreed, the line moved here. Where they disagreed because one
site genuinely needs something different, the difference became a named knob. Where a thing
belonged to one site's subject matter — uisce's health marker, esb's repeat-fault tag, lifts'
notice text — it stayed home, however shared it *looked*.

> **Concept: a design layer.** Not a framework and not a theme — a layer is the set of
> decisions three pages have agreed to make identically, written once. Here it is three
> files. `base.css` holds the *tokens* (named values: the page colour, the six status hues,
> two layout widths) and every shared *rule* (the county row, the day bar, the grade chip,
> the footer, the phone reflow). `ui.js` holds the shared browser helpers. `statusui.py`
> holds the build helpers a site's generator calls. The test of membership is not "could
> this be shared?" — almost anything could — but "is this already the same everywhere, on
> purpose?" A layer built from the second question can only shrink a codebase; one built
> from the first grows speculative knobs nobody turns. (The uisce series states the rule
> from the site's side; this repo is the rule, enforced.)

The result, on day one: 228 lines of CSS, 116 of JavaScript, 163 of Python, and 122 lines of
tests — eleven of them — plus a 14-line copying script, `sync.sh`, and a demo (below). 928
lines added across 13 files (commit `c9f8beb`, 19 Aug 2026).

Two of the CSS lines deserve their sentence. First, `[hidden] { display: none !important }`
is the only `!important` display rule in the file, and the tests keep it that way: all three
sites switch views by setting and clearing `hidden`, so any other rule that could out-rank it
would be able to un-hide a view. That invariant predates the repo; now it has a home and a
guard. Second, the tokens carry a claim in a comment — that every `*-text` colour reads at
4.5:1 contrast on both background colours, in both light and dark schemes. On day one that
claim was documentation. In chapter 3 it becomes a test.

### Worked example: the knob that absorbed a disagreement

Each site's county row is a grid: name, day bar, stats, chevron. The sites agreed on the row
— hover band, focus ring, spacing — but not on its column widths: the sites list different
kinds of places, and their stats columns carry different words. So the row's grid is shared
and its widths are two tokens with defaults:

```css
--row-cols: 150px 1fr 190px 10px;
--stats-cols: 92px auto;
```

A site that wants different widths writes one line in its own block, overriding the token,
and everything else about the row stays common. That is
the pattern for every disagreement the extraction found: the *structure* moves up, the
*value* stays down, and the knob's existence documents that the sites once disagreed here.
The moment no site overrides a knob it is a candidate for deletion; the moment a third kind
of disagreement appears it becomes a third knob. There were exactly two knobs at birth, and
there are exactly two today (measured 27 Aug 2026) — which says the extraction cut in
roughly the right place.

### A page that exists to be looked at

The birth commit also contains `demo/` — a 145-line fake page and a 17-line build script that
inlines the layer into it, the way each real site's build does. The demo is this repo's
substitute for having a site of its own: every shared component appears once, with invented
data, so a change to the layer can be *seen* before three real sites inherit it. Its build
doubles as the only integration test — it is the one place `base.css` and `ui.js` are
rendered together — and "look at the demo, light, dark and at 375 pixels" became step one of
the change loop that evening, when a `CLAUDE.md` wrote the working rules down (commit
`fb9fab0`, 19 Aug).

#### How uisce does it

uisce checks its rendered pages by looking at the real site with real data, and its numbers
give the review teeth — a wrong page shows a wrong number. This repo's demo can only show
that components render, not that they render *truthfully*; there is no truth here to check
against. That gap — a change that renders wrong rather than throws — stays a human's job for
the whole series, and chapter 4 writes it into the CI comments explicitly.

### The first shared fix arrives from a phone (PR #2, 19–20 August)

The extraction's premise — fix once, ship thrice — got its first test the same evening. I
spent it going through the water site on a 390-pixel iPhone as an owner rather than a
developer (the uisce series tells that review from the site's side, with its measurements, in
chapter 14). Three of the findings were the layer's, and they became this repo's first
functional PR:

- **The month strip scrolls instead of wrapping.** The sites add one month tab forever; at
  twelve simulated months the tabs measured 1,095 pixels laid end to end in a 356-pixel
  strip — wrapped, that is ⌈1,095 ÷ 356⌉ = 4 rows of pills above the first county. The strip
  became one horizontally scrolling row, scrollbar hidden, edge shadows only where more tabs
  lie, and a new global `revealMonthTab()` scrolls the selected tab back into view after each
  render — via `scrollLeft`, not `scrollIntoView()`, which would helpfully scroll the whole
  page too.
- **Touch is not hover.** iOS fires a hover event (`pointerover`) on the touch that starts a
  tap or a scroll, so the day-bar caption — hidden on phones precisely because hover is
  meaningless there — was being filled, and un-hiding itself, by the first touch. The binder
  now ignores hovers whose `pointerType` is `"touch"`; an iPad trackpad reports `"mouse"`
  and keeps its caption.
- **The phone column owns its rhythm.** Below 640 pixels the overview stacks into one
  column, where the desktop margins had stopped overlapping and the section gaps landed
  wherever they fell: 22 / 6 / 14 / 14 / 18 / 30 / 16 pixels down the page. The column now
  zeroes its children's vertical margins and spaces them itself: 24 / 12 / 12 / 24 / 24 /
  24 / 12 / 12 after (PR #2, measurements in uisce's `notes/frontend-notes.md`, "The iPhone
  review pass 2026-08-19").

One review of one site, three fixes, three sites improved: the layer doing what it was built
for, on day one. The strip then produced a finding against the finding — the reveal ran only
on render, so rotating a phone from 851 to 375 pixels left the selected tab stranded
off-screen at `scrollLeft` 0 while the page below showed its figures; a resize listener,
`bindMonthReveal()`, closed that the next evening (commit `0567472`, 20 Aug). Nothing runs at
load, as ever — the page calls the binder. That rule, stated in `ui.js`'s header since birth,
is the layer's oldest constitutional clause: a file inlined into every page of three sites
must never *do* anything until asked, because no one page wants all of it.

## Where it left the layer

By the evening of 20 August the layer was real and vendored: three sites carried its files
under a `ui/` directory, copied in by `sync.sh`, each copy stamped with the commit it came
from. Eleven tests, two knobs, one demo, one constitutional clause, and a copying script with
a design flaw nobody had noticed yet. Chapter 2 is about the flaw.

## Notes

- Commit `c9f8beb` (19 Aug 2026): the extraction; 13 files, 928 insertions; `ui/base.css`
  228 lines, `ui/ui.js` 116, `ui/statusui.py` 163, `tests/test_ui.py` 122 (11 tests),
  `sync.sh` 14, `demo/demo.html` 145, `demo/build.py` 17. Reconciliation description from
  the commit message.
- Commit `fb9fab0` (19 Aug): CLAUDE.md — consumers, change loop, floors.
- PR #2 / commit `da7723f` (19–20 Aug, merged 20 Aug): month strip, `pointerType` gate,
  phone rhythm; figures from the commit message and uisce `notes/frontend-notes.md` "The
  iPhone review pass 2026-08-19". Reader-side account: uisce series chapter 14.
- Commit `0567472` (20 Aug): `bindMonthReveal()`; rotate measurements (851 → 375 px, tab at
  x 352–439) from the commit message.
- Knob count and `[hidden]` invariant verified against `src/statusui/base.css` and
  `tests/test_ui.py`, 27 Aug 2026.
