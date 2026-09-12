# 9. Six letters, two metrics
*~8 min read · PR #11 · 29–30 August 2026*

*Where we are:* the grade chip is the small coloured square carrying a county's letter, and
it has been shared since the extraction in chapter 1, where the tokens took uisce's
contrast-checked values and a test held every text colour to 4.5:1. This chapter adds the
letter that was missing and then discovers that the test had never looked at the chips
themselves.

## The question that opened this stretch

The three sites grade A, B, C, D, F. Skipping E is an American-ism. Irish and British
scales run A to F inclusive, with E as the band above F, and these sites are read by an
Irish audience, so the missing letter reads as an import. The band tables that decide which
score earns which letter belong to each site and move in their own commits. What the layer
owes them is a chip for every letter they might emit.

## What changed

A sixth chip needs a sixth fill, and the palette already had one: `--severe` was declared in
both schemes and already held to white lettering by the contrast test, because the banner
uses it. So no new token was needed for the letter itself. F moved down onto `--severe`, and
E took the red that F used to wear. Every chip clears 4.5:1 against the lettering colours
already in the file, in both schemes: A 5.19, B 4.79, C 9.49, D 6.60, E 4.80, F 8.89 in
light and 6.52 in dark. The separation stays wide, at a CIELAB delta-E of 28 between D and
E, and 20.7 between E and F in light, 8.9 in dark (PR #11, 29 Aug 2026).

The alternative, which was tried and rejected, was to leave F on `--critical` and invent a
new E between `--serious` and `--critical`, somewhere around `#de5f4a`. It fails on
contrast: white on that colour is 3.59:1, so E alone would have to take dark lettering,
breaking the pattern where the darkest chips carry white. And D, E and F would land within a
delta-E of 12 to 15 of each other, which is three shades of orange-red that a reader would
have to tell apart by the letter anyway.

### The test that could not see the chips

Two guards went with the new letter, and the reason they were needed is the interesting
part. The contrast test from chapter 3 checks *tokens*: it asks whether `--good-text` is
readable on `--surface`, and whether the fills that carry white lettering can. It does not
know which chip uses which token, and it cannot parse `color-mix()` at all.

That left a hole exactly the shape of chip B, which was not a plain colour but a mix of two
other tokens, and had therefore been unchecked since the day it was written. It also meant
that C, D and the ungraded chip had no guard of their own.

The new pairing test resolves each `.g-*` rule's own fill and lettering and holds the pair to
4.5:1 in both schemes, and it failed immediately on the chip nobody thinks about: `.g-none`,
the grey square shown where there is no grade, was `--muted` on `--cell-empty` at **4.24:1 in
light and 3.90:1 in dark**. The one chip in the set that could not be read was the one
carrying no letter, which is why six months of looking at these pages had never caught it. It
takes `--ink-2` now, at 6.41 and 7.81, and still reads as quieter than a lettered chip.

The second guard pins the letter set itself, so a site cannot emit a letter that has no fill
here and render white on nothing.

And the demo, which chapter 1 called this repo's substitute for having a site of its own, had
been quietly lying by omission: its fixture only ever rendered A, C, F and the ungraded dash.
D had never been looked at, and E would not have been either. It grows a key row carrying all
six letters, which is the only way a human reviewing the page can see what the page now
contains.

## What went wrong: the parser, and the metric

The pairing test bought its coverage with 33 lines of regular expression and sRGB colour
mixing, to answer a question the stylesheet can mostly answer without them. A, E and F were
already covered by the token test. C, D and the ungraded chip only needed their token pairs
named. Exactly one chip in the set actually required a parser: B, the one fill built from a
`color-mix()`.

So the parser went (commit `2050d84`), the token test grew the three pairs it can express,
and the commit was candid that B was now the gap: at 4.79:1 it was the thinnest margin in the
set, and both of its inputs were shared with the day-bar colour ramps, so retuning a bar
could drop a chip under 4.5:1 with nobody looking at a chip. The commit wrote down what to do
if that ever needed guarding: **give B its own token rather than bring a parser back.** That
is what happened two commits later, for a different and better reason.

> **Concept: a value with no name cannot be checked by name.** B was the only chip the test
> could not express, and that was not a limitation of the test. It was that B had no
> identity: it was an expression evaluated at render time from two values owned by something
> else. Anything derived like that is invisible to a guard written in terms of names, and it
> moves when its inputs move, for reasons that have nothing to do with it. The choice is
> either to grow machinery that evaluates the derivation, which is a colour parser here and
> was a JavaScript parser in chapter 7, or to give the value a name and check the name. The
> second is almost always right. A named token costs one line, is checkable by the cheapest
> possible test, and stops a change to the bar palette from silently moving a grade chip.

### Worked example: when two measures disagree, move the design

Giving B its own token forced a decision that had been hiding inside the mix, because the
lettering was wrong and the two available metrics did not agree about how wrong.

**WCAG 2**, the standard this file has always tested, rated the old B as 4.79:1 with dark ink
and 3.63:1 with white. On that measure, dark ink wins and passes.

**APCA**, the WCAG 3 candidate, puts dark ink on the old B at **Lc 38.6** and white at
**Lc 69.2**. Not close, and in the opposite direction. Lc 38.6 made B by a wide margin the
least readable chip in the set, the next worst being D at 51.3.

This is a known failure mode of the WCAG 2 formula on saturated mid-tones rather than a
curiosity, so "which metric do I believe?" is a real question with no satisfying answer. The
resolution was to refuse the question. `--fair` is set at `#5a7a10`, dark enough that **white
clears both**: 4.97:1 and Lc 79.6, in line with A at 5.19 and Lc 80.4, and E at 4.80 and
Lc 77.5. It stays a distinct olive, at a delta-E of 24.0 from A and 59.0 from C, and it moves
13.3 from the mix it replaces, which is a visible change and a deliberate one.

The technique generalises past colour: when two defensible measures of the same property
disagree about a design, the cheapest move is usually to change the design until they agree,
rather than to adjudicate between the measures and ship something that one of them calls a
failure. Adjudicating costs an argument every time the question comes up again. Moving the
design costs one commit and ends it.

The same logic then came for D. Dark ink on `--serious` sat at Lc 51.3, usable for 14px bold
and the lowest of the six, on the same disagreement that had made B unreadable. Again no new
token was needed: `--serious-deep` already existed, already declared for both schemes,
already documented in the file's header as "a serious fill dark enough to carry white text",
and already used by uisce for exactly that in its health mark and quality swatch. It was the
token the chip should have been on. White on it is 5.36:1 and Lc 81.3, the strongest of the
six on the perceptual measure.

That leaves the set with one chip taking dark lettering: C, the amber, which is the one fill
genuinely light enough to need it. And it leaves the six no longer running as a lightness
ramp, since D now lands three L\* points darker than E. That is fine, because the ramp was
never doing the work: the order is carried by the hue and by the letter printed on it, and B
was already darker than both C and D. The closest pair in the finished set is D and E at a
delta-E of 20.2. `--serious` keeps its declaration for the sites' bar ramps and badge mixes,
but nothing sets text on it any more, so that pair left the contrast test.

### How uisce does it

uisce decides what a D *means*. Its chapter 12 calibrated the thresholds against its own
distribution of 78 county-months, cutting at the 97th, 76th, 33rd and 10th percentiles,
because a letter grade is a claim about water and only uisce has the water. The layer decides
what a D *looks like*, and must not know anything about the first question. That division is
chapter 1's rule at its cleanest: the letter's meaning is domain and stays per site, the
letter's colour is design and moves up. What the layer owes the sites in return is that every
letter they can emit has a fill, that every fill can carry its lettering, and that the set is
checked rather than assumed. Before this PR, two of those three were untrue.

## Where it left the layer

Six chips plus the ungraded one, every one of them a plain named token, every one in the
pairing test, and a letter-set test that fails if a site could emit a letter with no fill.
One real unreadable chip found and fixed, one colour parser written and deleted, and one
lettering decision made by moving the design until two rival metrics agreed.

## Notes

- PR #11 / commits `f7d9562`, `b2898ab`, `2050d84`, `58c086d`, `855023b` (29–30 Aug 2026,
  merged 30 Aug). All contrast ratios, APCA Lc values and delta-E figures are from those
  commit messages: A 5.19, B 4.79, C 9.49, D 6.60, E 4.80, F 8.89 light / 6.52 dark;
  `.g-none` 4.24 and 3.90 before, 6.41 and 7.81 after; the rejected `#de5f4a` at 3.59:1;
  `--fair` `#5a7a10` at 4.97:1 and Lc 79.6; `--serious-deep` at 5.36:1 and Lc 81.3;
  delta-E 28 (D to E), 20.7 / 8.9 (E to F), 24.0 (B to A), 59.0 (B to C), 13.3 (B's move),
  20.2 (D to E, final).
- Chip-to-token mapping and the `--fair` hex verified against `src/statusui/base.css`,
  12 Sep 2026; `test_fills_carry_the_lettering_set_on_them` and
  `test_the_scale_runs_a_to_f_inclusive` in `tests/test_ui.py`.
- uisce's grade calibration: uisce series chapter 12.
