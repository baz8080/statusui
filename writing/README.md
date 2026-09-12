# The statusui series — brief and style guide

A chapter-by-chapter account of how this repo came to exist: how the design layer of three
status sites, uisce (water), esb (electricity) and lifts (rail lifts), stopped being three
hand-synced copies and became one pinned dependency. A companion to the uisce series
(`../uisce/writing/`), written in the same voice and to the same rules, and much shorter,
because the history is: 19 August to 5 September 2026, fourteen pull requests, sixty-one
commits.

Written in two sittings. Chapters 0 to 5 and the closing were drafted on 27 August, covering
the first week; chapters 6 to 10 were added on 12 September, covering the fortnight after,
and the closing was renumbered from 6 to 11 and re-measured. The uisce series does the same
thing (its chapters 14 to 16 were added as the PRs landed, and its closing moved from 13 to
17), and for the same reason: a new stretch of history goes in before the closing, and the
closing is rewritten rather than appended to.

Nothing in `writing/` is imported by the package. It is prose and diagrams only.

## How this differs from the uisce series

The persona, voice and rules below are the uisce series' own; read that series' README for the
long form. What differs here follows from what the repo is:

- **The subject has no data.** uisce's numbers are person-hours and populations; this repo's
  are line counts, test counts, pixel measurements and commit distances. The sourcing rule is
  the same — every number carries a source and a date — the numbers are just smaller.
- **The reader of the sites never sees this repo.** Its users are three build scripts. Where
  the uisce series asks "what does the reader see?", this one asks "what do the consumers
  inline?" — and the chapters say so when the two questions pull apart.
- **Cross-series references are allowed and expected.** Several of these events appear in the
  uisce series from the site's side (its chapters 14 and 16). A chapter here may point there
  in one line — "the reader-side story is uisce chapter 14" — and must not retell it. A concept
  the uisce series already boxed is re-boxed here only if this repo's angle on it is different.
- **No `sources/` machinery.** uisce's writing directory generates per-chapter source packets
  from sixty-one PRs; this repo's fourteen PRs and sixty-one commits are readable whole
  (`git log --reverse` is the packet). The outline below carries what each chapter needs.
- **Explicit contrasts are part of the brief.** Each chapter carries a short *How uisce does
  it* note where the two repos genuinely differ (test runner, floors, shipping, direction of
  authority), and the closing chapter collects them.

## Who it is for

Same persona as the uisce series: an intelligent professional who is not a programmer. They
can follow arithmetic when it is shown and a table with real names in it. New here: they have
not necessarily read the uisce series, so the intro must earn the premise — three websites,
one look — without assuming it.

## Voice

First person, "I". Candid: the wrong turns — the sync stamp that needed three fixes in one
evening before the whole mechanism was abandoned, the rounding fix that broke thirty-six
commoner values while fixing the ties — are the story. Chronological within a chapter. Plain:
"the copy" not "the vendored artefact", "the pin" not "the locked revision".

## Rules

The uisce series' rules apply unchanged; restated in short:

1. Every number carries a source and a date, and a row in `figures.md`.
2. No figure without a sentence saying what it means.
3. One concept box per hard idea, `> **Concept: <name>**`, ≤ 200 words, at first use.
4. At least one worked example per hard concept, real names, arithmetic shown.
5. Diagrams earn their place; mermaid for flows. Most of this repo is not spatial — expect few.
6. Target ~1,500–2,000 words; hard ceiling 3,000. Light chapters may be shorter; do not pad.
   Each chapter carries a "~N min read" line (≈ 230 words/min).
7. Standalone: each chapter opens with a two-line *Where we are*.
8. Vocabulary is fixed (below); do not drift between synonyms.
9. Missing number → `[verify: what]`, collected in the final pass.
10. **No em dashes in new prose.** `CLAUDE.md` carries the house rule (added 29 Aug 2026,
    chapter 8 is the story); the house dash is a spaced hyphen, en dashes survive only in
    numeric ranges such as "29–30 August". Chapters 0 to 5 predate the rule and keep their
    punctuation, per the rule's own "fix them on lines you are already editing": a bulk
    re-punctuation of finished chapters is exactly the rewrite it exists to prevent. So the
    series changes dash halfway through, chapter 6 says so in a line, and chapter 8 explains
    it. Anything drafted or substantially rewritten from 12 Sep 2026 follows the rule,
    including the closing.

## Fixed vocabulary

| Use | Not | Meaning |
|---|---|---|
| **site / consumer** | client, downstream | uisce, esb or lifts: a repo that installs this one. *Site* in prose; *consumer* where the dependency direction is the point |
| **the layer** | the library, the framework | `base.css` + `ui.js` + the Python helpers, taken as one thing |
| **token** | variable, custom property (after first use) | a named value in `:root` — a colour, a width |
| **rule** | style, class | one CSS declaration block |
| **global** | export, function (when the contract is the point) | a name `ui.js` declares at top level; the treaty list is `JS_GLOBALS` |
| **helper** | util, API | a Python function the package offers a build |
| **mirror** | port, twin (after first use) | a Python/JS pair that must format identically |
| **floor** | minimum version, target | the oldest thing still supported: the *Python floor* (consumers' interpreter) and the *browser floor* (ES5); they move independently |
| **copy** | vendored tree | the layer's files as duplicated into a consumer, in the vendoring era |
| **stamp** | marker | the `UPSTREAM` file naming the commit a copy came from |
| **pin** | lock, ref | the commit a consumer's `uv.lock` records |
| **rollout** | release, deploy | moving all three pins: `rollout.sh` |
| **promotion** | upstreaming, extraction (after ch 1) | moving code from a site into the layer |
| **demo** | test page, fixture | `demo/` — the fake-data page that renders every component |

## Chapter template

As the uisce series, plus the contrast note:

```markdown
# NN. Title
*~N min read · PRs #a–#b · dates*

*Where we are:* two lines.

## The question that opened this stretch
## What changed
> **Concept: <name>** — ≤ 200 words.
### Worked example: <thing>
## What went wrong / what got retracted   ← when applicable
### How uisce does it                     ← when the repos genuinely differ
## Where it left the layer
## Notes
```

## Outline

- **00 — intro.** Three sites, one look, and why that became a fourth repository. The series
  premise; how it was built, said once; the chapters in one table.
- **01 — Three copies of one look.** Birth (19 Aug): extraction and reconciliation, what the
  two-sites rule kept out, the demo, `sync.sh`. PR #2 lands the iPhone-review findings as the
  layer's first shared fix.
- **02 — A pointer beats a copy.** The stamp's three fixes in one evening; the five-commit
  drift; the package, the pin and `rollout.sh`; the first real rollout (the dot). PRs — none
  and that is part of the story; commits 78515fa → 61b642c.
- **03 — Hold the mirror to account.** PR #1: running `ui.js` under node against the Python
  helpers; the tie that disagreed; the fix that broke thirty-six commoner values; the ES5
  guard's hole; contrast as a test.
- **04 — Floors are for consumers.** PRs #4, #5: CI, the 3.9 floor that was never this repo's,
  the Raspberry Pi arithmetic, two interpreters in the matrix, the comment rule.
- **05 — Promoted on the second user.** PRs #3, #6, #7 and commit 2076735: the date formatters,
  `freshness()`, the place search, the sub line — and the deploy gap that dictates what may be
  deleted when.
- **06 - The search hit learns where it goes.** PR #8: targets in the index, hits as links,
  `pick()` returning true, and the slug asymmetry chapter 3 left unpaired coming back as a
  reason to ship the destination rather than derive it.
- **07 - A guard that fails open.** PR #9: `caption.js` and the second marker; the
  redeclaration guard that stopped covering what moved; a regex, an engine, and four commits
  of a rollout gate that failed open four ways before deletion; README step 5.
- **08 - A rule nobody could see.** PR #10: the no-em-dash rule, the user-level file a web
  session never loads, stated rather than enforced, and this series' own 222 em dashes.
- **09 - Six letters, two metrics.** PR #11: the E grade, the unreadable `.g-none`, the colour
  parser written and deleted, and WCAG 2 against APCA on `--fair` and `--serious-deep`.
- **10 - What the layer is in no position to say.** PRs #12, #13, #14: the banner's false
  cause and its hedged replacement; the dedup key that hid fourteen town pages; the correction
  to chapter 5's rule.
- **11 - Closing** (was 06). The inventory today; what stays per site; what this repo cannot
  see; the open threads; the differences from uisce, collected.

## Working method

The history is small enough that the cost discipline is different from uisce's: a session may
draft two or three chapters, but must still register figures as it goes and update
`PROGRESS.md` before stopping. Verify numbers against the working tree with read-only
commands; figures quoted from uisce's series or PR bodies are lifted, not re-run, and say so.

When a later stretch lands, read `PROGRESS.md`, then this file, then
`git log --reverse <last-covered-commit>..origin/main` whole, which is still the session's
source packet. New chapters go in before the closing; the closing is renumbered and
re-measured rather than appended to; and a figure an earlier chapter quoted is re-quoted with
both dates rather than silently updated.
