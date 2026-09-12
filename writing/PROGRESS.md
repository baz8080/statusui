# Progress ledger

Read this first each session. Statuses: `todo` → `drafted` → `reviewed` (continuity pass by
a later session) → `final`.

| Ch | Title | Sources | Status | Words |
|---|---|---|---|---|
| 00 | Three websites walk into a stylesheet (intro) | - | drafted | 1,566 |
| 01 | Three copies of one look | `c9f8beb`-`0567472`, PR #2 | drafted | 1,559 |
| 02 | A pointer beats a copy | `78515fa`-`61b642c` | drafted | 1,673 |
| 03 | Hold the mirror to account | PR #1, `d553b7f` | drafted | 1,575 |
| 04 | Floors are for consumers | PRs #4, #5 | drafted | 1,648 |
| 05 | Promoted on the second user | `2076735`, PRs #3, #6, #7 | drafted | 1,937 |
| 06 | The search hit learns where it goes | PR #8 | drafted | 1,494 |
| 07 | A guard that fails open | PR #9 | drafted | 2,005 |
| 08 | A rule nobody could see | PR #10 | drafted | 1,220 |
| 09 | Six letters, two metrics | PR #11 | drafted | 1,884 |
| 10 | What the layer is in no position to say | PRs #12, #13, #14 | drafted | 2,003 |
| 11 | Closing: a layer is a set of promises (was 06) | - | drafted | 2,137 |

Two sittings. 27 Aug 2026: chapters 00 to 05 and the closing, covering 19 to 26 Aug (PRs
#1 to #7). 12 Sep 2026: chapters 06 to 10, covering 27 Aug to 5 Sep (PRs #8 to #14), with
the closing renumbered from 06 to 11 and re-measured, the intro's table and figures updated,
and `figures.md` given a second anchors section. Anchors verified against the working tree on
each of those dates.

## Punctuation

`CLAUDE.md` gained a no-em-dash rule on 29 Aug 2026 (chapter 8 is the story). Chapters 00 to
05 predate it and keep their em dashes, per the rule's own "fix them on lines you are already
editing". Chapters 06 to 11 have none, and neither does anything added to the older files
since. Check a new chapter with `grep -c '—'` before marking it drafted; the answer is 0.

## Chapter summaries (3 lines each)

- **00** The premise: three sites, one deliberately identical look, three drifting copies;
  the 18 Aug contrast fix that never reached esb. Why an 820-line repo gets a series (the
  smallest distributed system). Relation to the uisce series; per-chapter *How uisce does
  it* notes promised; AI-assistance said once; the note on figures and rules moving.
- **01** Birth `c9f8beb`: extraction by measurement, tokens take uisce's contrast-checked
  values, disagreements become the two knobs, membership = "already the same everywhere, on
  purpose". `[hidden]` invariant; demo as the site-substitute; PR #2 ships the iPhone
  findings (month strip 1,095 px/356 px, `pointerType` touch, column rhythm) to three sites
  at once; `bindMonthReveal` coda. Boxes: a design layer.
- **02** The stamp's three fixes in one day (no-op sync, `-dirty` wedge, stale-rev wedge) →
  box: a stamp names content, not effort. Measured drift: five UI commits in one day,
  guard that skips. `da21d4f` package + pin + `rollout.sh` (walked as worked example);
  first rollout drops the dot. Contrast: uisce ships on push; here merge ships nothing.
- **03** PR #1: node harness holds the pairs to identical output; box: the mirror
  (`f(x)=g(x)`, consistency not correctness). First catch 2.25 h "2.3 vs 2.2"; the ×10 fix
  breaks ~36 commoner values (1.15 → manufactured tie at 11.5); `tenth()` via
  `Decimal(float)` + `ROUND_HALF_UP`; 7,200-value sweep. ES5 guard's destructuring hole.
  Leaves `slug` deliberately unpaired, which chapter 06 collects.
- **04** PR #4: CI where the mirror cannot skip (node pinned), demo build as the only joint
  render, "catches a change that throws, not one that renders wrong". PR #5: 3.9 was
  folklore; Pi bookworm ships 3.11.2 → floor 3.11; lifts' `>=3.9` fails `uv lock`;
  floor ≠ interpreter; matrix 3.11+3.14. Comment rule written down. Box: a floor is a
  promise to your slowest consumer.
- **05** The metabolism: box "promoted on the second user". `fmtDay`/`fmtDate`;
  `freshness(iso, staleHours, note)` with the 57,721-age equivalence; the search port
  (apostrophes → data attribute, lifts self-indexing → dedupe, `note()` hook); `.cml` and
  the legend-order migration; PR #7's deletions-ride-the-pin-bump rule. **Corrected by ch
  10**: the `note` parameter was a preserved mistake, not a requirement.
- **06** PR #8: index entries become `[name, target]`, hits become triples, `opts.href`
  makes them real links, `pick()` returning true keeps a county hit in the app, no href
  keeps lifts to a pin bump. Box: shipped, not derived, because the JS slug renders
  `Dún Laoghaire` as `d-n-laoghaire` (~20 place names). Three click-handler holes fixed the
  same day (modified click on a button site, Alt, unbounded `closest()`).
- **07** PR #9: `caption.js` + `<!--UI-JS-CAPTION-->`, 1.1 KB vs 15.9 KB, lifts 732.7 →
  467.1 KB over twenty pages. Box: a guard that passes by seeing less (consumers parsed
  `ui.js`, so the split dropped `bindDayCaption` from their check silently) →
  `js_globals()`. Then a regex fooled by `esc()`'s quotes → a bare `vm` context; four
  commits of a rollout gate that failed open four ways → deleted, replaced by README step 5.
- **08** PR #10: the no-em-dash rule lived in `~/.claude/CLAUDE.md`, which a web session's
  fresh container never clones, so it was absent rather than weak. Box: a convention lives
  where the work happens. Stated not enforced; 29 em dashes on 29 Aug, 27 on 12 Sep, pure
  attrition. Owns the awkward fact that this series carries 222.
- **09** PR #11: E added (A-F inclusive is the Irish scale), F onto `--severe`; the pairing
  test finds `.g-none` unreadable at 4.24/3.90 → `--ink-2`. Colour parser written then
  deleted (box: a value with no name cannot be checked by name) → `--fair` `#5a7a10`.
  WCAG 2 vs APCA disagree on B (4.79 dark ink vs Lc 38.6) → move the design until both
  agree; D onto `--serious-deep`; C the only dark-ink chip.
- **10** PRs #12/#13: the banner claimed "collection has stopped" when the build had failed;
  box: a page can see its own age, not its cause; `note` dropped, then restored hedged
  inside the function, which corrects ch 5's rule. PR #14: the `name|county` dedup key hid
  fourteen town pages (Sligo worked example); key gains the target; the default note keeps
  the county so two rows are never identical.
- **11** Inventory; the promises table with the one promise whose mechanism stops at the
  repo's edge; what the repo cannot see; two open threads; the collected uisce differences;
  glossary of the eleven boxes.

## Open threads

- `src/statusui/__init__.py` line 4 still says "Python 3.9 syntax" (PR #5 moved the floor to
  3.11 on 26 Aug). Flagged in the closing on 27 Aug, still stale on 12 Sep. The closing
  quotes it with both dates; when it is fixed, update that paragraph rather than deleting
  it, and add the fix's date.
- README step 5 (consumers must ask `js_globals()` and teach their template split the second
  marker) is open in all three sites. When each closes, chapter 07's "Where it left the
  layer" and the closing's open-threads section both need a dated line.
- Word counts are pre-review; re-count after a continuity pass and update the read-time lines
  if a chapter moves by more than a minute.
- `figures.md` "Lifted" rows quote uisce-series figures (443 tests, 1,767 places); if that
  series' final pass changes them, follow.

## Brief for the next session

Continuity pass over the whole series, which has not had one: read 00 to 11 in order checking
cross-references (chapter numbers after the renumbering, box names, the promise table's
chapter pointers, ch 5's forward reference to its own correction in ch 10), then mark
chapters `reviewed`. The renumbering was the risk: anything that said "chapter 6" before
12 Sep meant the closing and now means the search chapter. One such reference was found and
fixed on 12 Sep (chapter 02's notes, which now say "the closing chapter" instead of a
number), and a `grep -rn 'chapter [0-9]'` came back clean after that. Prefer "the closing
chapter" to a number in any new cross-reference to it, for the same reason.

A chapter 12 exists only if the repo gains another comparable stretch. If it does, the working
method at the end of `README.md` says how to start.
