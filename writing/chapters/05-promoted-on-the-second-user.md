# 5. Promoted on the second user
*~8 min read · commit `2076735`, PRs #3, #6, #7 · 25–26 August 2026*

*Where we are:* the layer is pinned, mirrored and CI'd (chapters 2–4). This chapter is about
how it grows — four promotions in two days, each triggered the same way — and about the gap
between merging here and being live anywhere, which turns out to be a tool.

## The question that opened this stretch

Chapter 1's rule said what may enter the layer: what at least two sites want, none of them
differently. That answers *whether*; a week of living with it produced the operating
question: *when?* The answer the week settled into is a rule I'd state now as: **nothing
moves up on speculation; everything moves up on its second user.** The first site to need
something builds it at home, where it can change daily without a rollout. The day a second
site starts writing the same thing, the copy is moved here — not rewritten, *moved*, with
its constants turned into parameters. Every promotion in this chapter ran that pattern.

> **Concept: promoted on the second user.** Shared code has a fixed overhead — a rollout to
> ship, three consumers to not break, a mirror or node test to maintain — so putting a
> thing in the layer is a bet that its generality will pay that rent. One user is no
> evidence; a second user is the bet already won, and it also performs the design work
> speculation cannot: only when esb actually adopted uisce's freshness stamp did it become
> a fact, rather than a guess, that the threshold and the warning sentence are the *only*
> two things that differ. The second user tells you where the parameters go. The cost of
> the rule is honest duplication in the window between first and second user — accepted,
> because duplication is visible and mis-designed abstraction is not. (uisce's series tells
> this rule from the site's side in its chapter 16; this chapter is the receiving end.)

## What changed

### Dates the way a reader says them (commit `2076735`, 25 August)

uisce's plain-reader copy pass (its chapter 16) had built `fmtDay` — "2026-08-01" rendered
as "Sat 1 Aug", the year appearing only when it isn't the caller's current one — for its
own pages. When esb wanted the same rendering, the pair moved here, with Python mirrors
`fmt_day`/`fmt_date` and mirror tests per chapter 3's habit. The promotion improved the
layer's own components in passing: `day_cells` captions now open "Sat 1 Aug: …" instead of
an ISO date. Two smaller things rode along, both uisce conventions becoming layer
conventions: `stampLine` stopped showing the build clock — a reader wants to know how far
the *data* reaches, not when the generator last ran; the timestamp stays in the payload
for cache-busting — and the part-day footnote traded its em-dash for a plain hyphen,
because that is the sites' prose convention and the layer had drifted from it in a string
the sites can't edit.

Note what `fmt_date` takes: the caller's *own* clock, not the wall clock — a page rebuilt
later renders the same bytes. Small, but it is the difference between a formatter a static
site can use and one it can't.

### Worked example: freshness, parameterised by its second user (PR #3, 26 August)

uisce answered "is this page current?" with an age — "Updated 2 hours ago" — computed in
its own `site.html`. esb was about to write the same arithmetic. The promotion is one
function:

```js
freshness(iso, staleHours, note)
```

- uisce calls `freshness(D.data_as_of_iso, 24, "the last data build may have failed")`
- esb calls `freshness(D.observed_iso, D.stale_hours, "collection has stopped")` — its
  threshold is its own `STALE_AFTER`, 16 hours

Everything else — the clock-skew guard, the unit ladder, the rounding — is identical, and
the identity was *checked*, not felt: called with uisce's two constants, the shared
function was compared minute-by-minute against the one it replaces, every age from −2
hours to 40 days — **identical across 57,721 ages** (PR #3, 26 Aug 2026). That is this
repo's version of uisce's replay evaluations: no ground truth, but a proof that a
refactor is a refactor.

`freshness` has no Python twin — no build writes an age, since an age is only true at
reading time — so chapter 3's habit adapts: it gets a node test of its own over the
boundaries worth pinning. Two of them show what boundary-hunting looks like on a
function this small: ages round *up*, never down, because a page understating its own age is
the one direction that must not happen; and the overdue gate reads exact minutes rather
than the rounded age, so a 16-hour threshold does not fire at 15h30m just because the
display already says "16 hours ago". `stampLine` stays alongside rather than being
replaced: lifts still wants the absolute form, and an age is a different thing from a
horizon — esb now shows both.

One mechanical detail carried the coordination: adding a global to `ui.js` adds it to
`JS_GLOBALS` (chapter 3), and every consumer's guard test fails until that site stops
declaring its own copy. uisce's suite went red until it deleted its local `freshness` —
which is, as the PR put it, what made this "one coherent change rather than three."
The treaty list turned a convention into a forcing function.

### The search box, and the biggest promotion (PR #6, 26 August)

The afternoon's design-alignment pass (uisce's chapter 16 tells the reader-facing half)
moved the largest piece yet: esb's place search. `searchHits` is the pure half — ranking:
counties whose name starts with the query first, then indexed places by match position,
alphabetical within a rank, capped at 40 — and `bindSearch` runs the box: the lazy index
fetch with a queue while the script loads, a 10-second timeout with retry, the dropdown
lifecycle, the pick. A site supplies its index URL, its county list, the pick handler,
and — after lifts joined — an optional per-hit note, because lifts annotates a hit with
its status ("nothing listed in Aug 2026") where the siblings annotate it with its county.

The port is not a copy, and the differences are each a lesson the original had already
paid for. esb's version wrote each result as a button with an inline `onclick`; the
shared one writes the place into a data attribute read by one delegated listener —
because the second user's data broke the first user's assumption. uisce's seventeen
hundred place names include apostrophes, and a name interpolated into inline JavaScript
inside HTML needs escaping *twice over*, for two different parsers —
exactly the kind of fragility that looks fine until the data changes. A data attribute is
escaped once, by `esc()`, as data. Then the *third* user found the next assumption: lifts
indexes each station under its own name, so a prefix-ranked hit and an indexed hit can be
the same place, which rendered two identical buttons until deduplication landed — with
the cap moved inside the dedupe walk so forty *distinct* places survive it (commits
`0be69a9`, `8b8c438`). Each consumer stress-tested a different clause of the contract.
Two review findings closed the PR: a settled-guard on the index fetch so a timed-out
script's late arrival can't corrupt a retry, and a queued render no longer reopens a
dropdown the reader dismissed while the fetch was in flight — focus still in the box is
the signal they're still typing (commit `b890924`).

The same PR carried two one-liners in CSS whose justifications are the rule working at
its edges. esb's `.cml` stat rule moved up because uisce now styles a percentage the
same two-line way: second user, textbook. And the 640-pixel reflow now puts the legend
*above* the county list — because both sites that have a legend overrode the layer's
below-the-list order identically, which is the shared-rule test failing in the field:
when every site wants the same *different* value, the base was simply wrong, and the
override migrates inward.

### The deploy gap, used on purpose (PRs #6, #7)

Cross-repo changes have an ordering problem the sites never face alone: merging here
deploys nothing, and the window between this repo's merge and the sites' pin bumps is a
moment when the two disagree. The week's last two PRs treat that window as a first-class
thing. PR #6's consumer PRs were pinned at the *branch's* commit so both sides were
testable together before anything merged — with the note that the branch must merge with
a merge commit, not a squash, so the locked commit stays reachable afterwards; the pins
then repoint to main. And PR #7 — the drill-down sub line, a three-line rule lifts and
esb carried byte for byte and uisce now wanted, the two-sites test met twice over — spells
the deletion rule out: the sites' local copies *stay* until the pin moves, because a
site's lock can only track this repo's main, and deleting the local rule in the same
change would leave the line unstyled on the deployed sites between merge and rollout.
Additions land here first; deletions ride the pin bump. The gap stopped being a hazard
and became the staging area chapter 2 predicted.

### How uisce does it

uisce creates: it decides what its readers need and builds it, sole user, same day. The
layer is constitutionally forbidden from that — it holds second-hand code only, every
line already proven on a real site. So the two repos improve differently: uisce by
invention, this repo by *selection*, and the direction of the dependency arrow is also
the direction good ideas flow. Nothing in this chapter was designed in this repo; it was
designed in esb or uisce, paid its rent there, and was promoted with its constants
turned into arguments. The uisce series names the pattern from below ("promoted on the
second user", its chapter 16); from up here it reads as: a shared layer earns trust
precisely by refusing to have ideas of its own.

## Where it left the layer

Four promotions — dates, freshness, search, one sub line — in two days, each with its
mirror or node test, each forced coherent by the globals treaty, each shipped through
the pin-bump discipline. `ui.js` more than doubled in the week after the first rollout:
142 lines on 21 August to 300 on the 27th, all of it promotion, none of it invention.
The chapter's rule is now the repo's metabolism; what's left is to say what the whole
thing amounts to, which is the closing chapter.

## Notes

- Commit `2076735` (25 Aug 2026): `fmtDay`/`fmtDate` + `fmt_day`/`fmt_date`, promoted
  from uisce, esb the second consumer; `stampLine` horizon-only, `D.generated` kept for
  cache-busting; `PARTIAL_NOTE` em-dash → hyphen. From the commit message; uisce-side
  story in its series ch 16.
- PR #3 / commit `5959b1c` (26 Aug): `freshness(iso, staleHours, note)`; call sites and
  57,721-age equivalence from the PR body; node-test boundaries from the commit message;
  uisce PR #59, esb PR #15; `test_ui_globals` forcing.
- PR #6 / commits `fb950dc`, `0be69a9`, `8b8c438`, `b890924` (26 Aug): search promotion
  from esb; ranking and cap 40; apostrophes → data attribute + delegated listener;
  lifts self-indexing → dedupe; `note()` hook; settled guard and dismissed-dropdown
  fix; `.cml`; legend-order migration. From the PR body and commit messages.
- PR #7 / commit `1a1a59e` (26 Aug): `.chead + .sub`; deletion-rides-the-pin-bump rule
  from the PR body.
- `ui.js` 142 → 300 lines: 142 at commit `61b642c` (21 Aug, matches uisce series ch 14's
  count); 300 measured in the working tree, 27 Aug 2026.
