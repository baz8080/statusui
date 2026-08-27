# Progress ledger

Read this first each session. Statuses: `todo` → `drafted` → `reviewed` (continuity pass by
a later session) → `final`.

| Ch | Title | Sources | Status | Words |
|---|---|---|---|---|
| 00 | Three websites walk into a stylesheet (intro) | — | drafted | 1,137 |
| 01 | Three copies of one look | `c9f8beb`–`0567472`, PR #2 | drafted | 1,559 |
| 02 | A pointer beats a copy | `78515fa`–`61b642c` | drafted | 1,672 |
| 03 | Hold the mirror to account | PR #1, `d553b7f` | drafted | 1,575 |
| 04 | Floors are for consumers | PRs #4, #5 | drafted | 1,648 |
| 05 | Promoted on the second user | `2076735`, PRs #3, #6, #7 | drafted | 1,899 |
| 06 | Closing: a layer is a set of promises | — | drafted | 1,476 |

All seven drafted in one session (27 Aug 2026) — the history is a week long and fit in one
read, which the uisce series' one-chapter-per-session discipline was built to avoid needing.
Figures registered in `figures.md` as written; anchors verified against the working tree
27 Aug 2026.

## Chapter summaries (3 lines each)

- **00** The premise: three sites, one deliberately identical look, three drifting copies;
  the 18 Aug contrast fix that never reached esb. Why a 735-line repo gets a series (the
  smallest distributed system). Relation to the uisce series; per-chapter *How uisce does
  it* notes promised; AI-assistance said once.
- **01** Birth `c9f8beb`: extraction by measurement — tokens take uisce's contrast-checked
  values, disagreements become the two knobs, membership = "already the same everywhere, on
  purpose". `[hidden]` invariant; demo as the site-substitute; PR #2 ships the iPhone
  findings (month strip 1,095 px/356 px, `pointerType` touch, column rhythm) to three sites
  at once; `bindMonthReveal` coda. Boxes: a design layer.
- **02** The stamp's three fixes in one day (no-op sync, `-dirty` wedge, stale-rev wedge) →
  box: a stamp names content, not effort. Measured drift: five UI commits in one day,
  guard that skips. `da21d4f` package + pin + `rollout.sh` (walked as worked example);
  first rollout drops the dot. Contrast: uisce ships on push; here merge ships nothing —
  and recorded drift beats silent drift.
- **03** PR #1: node harness holds the pairs to identical output; box: the mirror
  (`f(x)=g(x)`, consistency not correctness). First catch 2.25 h "2.3 vs 2.2"; the ×10 fix
  breaks ~36 commoner values (1.15 → manufactured tie at 11.5); `tenth()` via
  `Decimal(float)` + `ROUND_HALF_UP`; 7,200-value sweep. ES5 guard's destructuring hole.
  Contrast: uisce measures against the world, this repo against itself.
- **04** PR #4: CI where the mirror cannot skip (node pinned), demo build as the only joint
  render, "catches a change that throws, not one that renders wrong". PR #5: 3.9 was
  folklore; Pi bookworm ships 3.11.2 → floor 3.11; lifts' `>=3.9` fails `uv lock`;
  floor ≠ interpreter; matrix 3.11+3.14. Comment rule written down ("asked for by hand
  across four repos"). Box: a floor is a promise to your slowest consumer.
- **05** The metabolism: box "promoted on the second user". `fmtDay`/`fmtDate` and the
  horizon-only `stampLine`; `freshness(iso, staleHours, note)` with the 57,721-age
  equivalence and its node-only tests; the search port (apostrophes → data attribute,
  lifts self-indexing → dedupe, `note()` hook, two review findings); `.cml` and the
  legend-order migration; PR #7's deletions-ride-the-pin-bump rule. Contrast: uisce
  invents, the layer selects.
- **06** Inventory; the promises table (each promise + its mechanism); what the repo cannot
  see (rendering, consumers, unmoved pins, real old browsers); the stale-3.9 docstring as
  the open thread; the collected uisce differences table; glossary of the five boxes.

## Open threads

- The `__init__.py` docstring still says 3.9 (ch 6 quotes it as an open thread; a repo fix
  is queued separately). When it is fixed, ch 6's "one open thread" paragraph needs a
  dated update, not deletion — the series quotes numbers as they were.
- Word counts are pre-review; re-count after the continuity pass and update the read-time
  lines if a chapter moves by more than a minute.
- `figures.md` "Lifted" rows quote uisce-series figures (443 tests, 1,767 places); if that
  series' final pass changes them, follow.

## Brief for the next session

Continuity pass: read 00→06 in order checking cross-references (chapter numbers, box
names, the promise table's chapter pointers), then mark chapters `reviewed`. No new
chapters planned; a chapter 07 exists only if the repo gains a comparable stretch of
history (a fourth consumer, a breaking change, a token redesign).
