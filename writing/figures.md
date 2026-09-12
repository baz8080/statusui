# Figures registry

Every number quoted in a chapter gets a row here. *Source* is a PR number, a commit hash or
subject, a uisce-series chapter, or "measured" (a read-only command run by the writing
session against the working tree). *Verified* means re-run on the date given; figures lifted
from PR bodies, commit messages or the uisce series are quoted as recorded there, not re-run,
and marked N.

## Anchors verified 2026-09-12 (chapters 06 to 11)

| Figure | Value | How | Verified |
|---|---|---|---|
| Source line counts | `base.css` 246 · `ui.js` 320 · `caption.js` 23 · `__init__.py` 231 (sum 820) | `wc -l src/statusui/*` | Y |
| Test file / suite | `tests/test_ui.py` 675 lines · 54 tests, all passing | `wc -l`; `uv run python -m unittest discover -s tests -t .` | Y |
| Tests needing node | 23 of 54 (TestPublishedGlobals 2, TestMirror 6, TestSearchHits 7, TestBindSearch 7, TestFreshness 1) | class counts in `tests/test_ui.py` | Y |
| Bundle sizes | `ui_js()` 16,270 bytes (15.9 KB) · `caption_js()` 1,123 bytes (1.1 KB) · difference 14.8 KB | `len(...encode())` via the package | Y |
| `js_globals()` | 26 names, equal to `JS_GLOBALS`, includes `bindDayCaption` | the function; `tests/test_ui.py` | Y |
| Grade chips | `.g-A` `--good` · `.g-B` `--fair` (#5a7a10) · `.g-C` `--warning` + `#1a1a19` · `.g-D` `--serious-deep` · `.g-E` `--critical` · `.g-F` `--severe` · `.g-none` `--cell-empty` + `--ink-2`; letter set = A-F plus none | `base.css`; `test_the_scale_runs_a_to_f_inclusive` | Y |
| `freshness` signature | `freshness(iso, staleHours)`, sentence "the last data build may have failed" inside the function | `src/statusui/ui.js` | Y |
| Search dedup key | name + county + target; default note keeps the county when a targeted hit is named for it | `searchHits`, `bindSearch` in `ui.js` | Y |
| Slug divergence | `Dún Laoghaire` → Python `dun-laoghaire`, JS `d-n-laoghaire`; `Béal Átha na Sluaighe` → `beal-atha-na-sluaighe` vs `b-al-tha-na-sluaighe` | ran `ui.js` under node against `statusui.slug` | Y |
| History | 61 commits, 14 PRs, 19 Aug to 5 Sep 2026 | `git rev-list --count`; GitHub PR list | Y |
| Em dashes | 27 em + 2 en across 6 files on `main` (was 29 + 2 on 29 Aug, per `CLAUDE.md`); 222 em across the 10 files of `writing/` | `grep -o` counts | Y |
| Stale docstring | `__init__.py` line 4 still says "Python 3.9 syntax" vs `requires-python >=3.11`; unchanged since 27 Aug | read | Y |
| README step 5 | open: consumers still read `ui.js` off disk and split templates on one marker | `README.md` | Y |
| `rollout.sh` | 42 lines, no gate: a pin bumper again | the file | Y |

## Anchors verified 2026-08-27

| Figure | Value | How | Verified |
|---|---|---|---|
| Source line counts | `base.css` 245 · `ui.js` 300 · `__init__.py` 190 (sum 735) | `wc -l src/statusui/*` | Y |
| Test file / suite | `tests/test_ui.py` 410 lines · 38 tests, all passing | `wc -l`; `python3 -m unittest discover -s tests -t .` | Y |
| Tests needing node | 12 of 38 (TestMirror 6, TestSearchHits 5, TestFreshness 1) ≈ a third | class counts in `tests/test_ui.py` | Y |
| `JS_GLOBALS` | 26 names | `tests/test_ui.py` | Y |
| Layout knobs | 2 (`--row-cols: 150px 1fr 190px 10px`; `--stats-cols: 92px auto`), unchanged since birth | `base.css`; commit `c9f8beb` | Y |
| `!important` display rules | 1 (`[hidden]`) | `base.css`; `test_hidden_always_wins` | Y |
| `rollout.sh` / `ci.yml` | 42 / 41 lines; uisce leg runs `pytest`, esb/lifts legs `unittest`; CI matrix 3.11 + 3.14, `fail-fast: false`, node 22 pinned | the files | Y |
| Dependencies | runtime `[]`; dev group = ruff only; `requires-python = ">=3.11"` | `pyproject.toml` | Y |
| History | 32 commits, 7 PRs, 19–26 Aug 2026 | `git log`; GitHub PR list | Y |
| Birth commit `c9f8beb` (19 Aug) | 13 files, 928 insertions; `ui/base.css` 228 · `ui/ui.js` 116 · `ui/statusui.py` 163 · `tests/test_ui.py` 122 (11 tests) · `sync.sh` 14 · `demo/demo.html` 145 · `demo/build.py` 17 | `git show --stat`; `git show c9f8beb:<file>` | Y |
| Tests over time | 11 (birth) → 30 (PR #1 merge `374b358`) → 38 (today) | `git show <rev>:tests/test_ui.py`, counting `def test_` | Y |
| `ui.js` over time | 116 (birth) → 142 (`61b642c`, 21 Aug; matches uisce ch 14's count) → 300 (today) | `git show <rev>` / `wc -l` | Y |
| Commit `da21d4f` (package switch) | +107/−132; `sync.sh` −33 lines with the stamp and its tests | `git show --stat` | Y |
| Commit `61b642c` (dot removal) | 9 lines deleted here | `git show --stat` | Y |
| Vendoring era | ~31 hours: `c9f8beb` authored 19 Aug 15:27 → `da21d4f` 20 Aug 22:31; stamp fixes `78515fa` 07:48, `93894a9` 21:32, `f248ac3` 21:47 | commit author dates | Y |
| Stale docstring | `__init__.py` line 4 still says "Python 3.9 syntax" vs `requires-python >=3.11` | read, 27 Aug 2026 | Y |
| Mirror sample carries | 1.15, 1.45, 8.95 among `TestMirror.HOURS` | `tests/test_ui.py` | Y |
| 2.25 h / 1.15 h behaviour | `hours(2.25)` = "2.3 h", `hours(1.15)` = "1.1 h", asserted in suite | `test_hours_boundaries` | Y |

## Lifted figures (source + date recorded; not re-run)

| Figure | Value | Source |
|---|---|---|
| Drift at one day of vendoring | esb & lifts synced to `f248ac3`, uisce main at `c9f8beb` — five UI commits behind; byte-compare guard skipped without a sibling checkout | uisce PR #48 / uisce series ch 14, measured 20 Aug 2026 |
| uisce's dot-removal PR | +2/−4 | uisce PR #49 / series ch 14, 21 Aug 2026 |
| Month strip on a 390 px iPhone | 12 tabs = 1,095 px in a 356 px strip → ⌈1095/356⌉ = 4 wrapped rows | PR #2 / uisce notes "The iPhone review pass 2026-08-19" |
| Rotate finding | 851 → 375 px leaves `scrollLeft` 0 in a 341 px strip, selected tab at x 352–439 off-view | commit `0567472`, 20 Aug 2026 |
| Phone column gaps | 22/6/14/14/18/30/16 px → 24/12/12/24/24/24/12/12 | PR #2 / uisce notes, 19 Aug 2026 |
| Tie divergence | 2.25 h → JS "2.3 h" vs Python "2.2 h" | PR #1 / commit `2bff71c`, 20 Aug 2026 |
| First fix's damage | ~36 commoner values wrong in the 1–10 h range; 1.15 stored as 1.1499…, ×10 floats to exactly 11.5 | commit `d553b7f`, 20 Aug 2026 |
| Sweep | `hours()` vs `fmtHours` 0.01–72 h at 0.01 steps = 7,200 values, no divergences | commit `d553b7f`, 20 Aug 2026 |
| Raspberry Pi OS bookworm `python3` | 3.11.2 | PR #5, 26 Aug 2026 |
| PR #5 verification | on 3.11.15: 32 tests pass, demo builds; lifts `>=3.9` fails `uv lock` (hint quoted in ch 4) | PR #5 body, 26 Aug 2026 |
| Suite size at PR #3 | 33 tests | PR #3 body, 26 Aug 2026 |
| freshness equivalence | identical across 57,721 ages, −2 h to 40 d, minute by minute | PR #3 body, 26 Aug 2026 |
| freshness call sites | uisce `(D.data_as_of_iso, 24, "the last data build may have failed")`; esb `(D.observed_iso, D.stale_hours, "collection has stopped")`, `STALE_AFTER` = 16 h | PR #3 body |
| Search contract | county-prefix first, then match position, ties alphabetical, cap 40; index fetch 10 s timeout with retry | PR #6 body, 26 Aug 2026 |
| lifts search note example | "nothing listed in Aug 2026" | commit `8b8c438`, 26 Aug 2026 |
| uisce named places | 1,767 towns and parishes ("seventeen hundred" in ch 5) | uisce series intro, 26 Aug 2026 |
| uisce test count | 443 | uisce series ch 16 / PROGRESS, 26 Aug 2026 |
| uisce series scale | 61 PRs, ~8 weeks, ~200 commits | uisce series intro and ledger |
| Contrast fix that never reached esb | landed on uisce 18 Aug 2026 | uisce series ch 14 |

## Lifted figures, chapters 06 to 10 (source + date recorded; not re-run)

| Figure | Value | Source |
|---|---|---|
| Derived-slug breakage | about 20 Irish place names would get a URL that does not exist | PR #8 / commit `e2910d5`, 27 Aug 2026 |
| Backward-compatibility guard | the five existing `searchHits` cases pass unmodified | PR #8, 27 Aug 2026 |
| Click-handler holes | modified click swallowed before `pick()` on a no-href site; Alt missing from the modifier list; `closest()` unbounded past the dropdown | commit `84578c7`, 27 Aug 2026 |
| Caption split saving on lifts | twenty station pages 732.7 KB → 467.1 KB (265.6 KB, 13.3 KB a page) | PR #9 / commit `6c99e87`, 28 Aug 2026 |
| Bundle at the time of the split | 1.1 KB caption vs 15.8 KB bundle | commit `6c99e87`, 28 Aug 2026 |
| Regex fooled by `esc()` | `var zqA = 1, zqB = 2;` left the test green anywhere below line 12; the author's own check had injected above it | commit `7203cdd`, 28 Aug 2026 |
| Rollout gate failures | four rounds: aborts the whole run at uisce; matches only double-quoted `"ui.js"`; `js_globals(` anywhere under `tests/` opens it; skipped site exits 0; `ui.js` is a substring of `statusui.js_globals` | commits `0a20abb`, `73f772c`, `050c9a8`, 28 Aug 2026 |
| Em dash count when the rule landed | 29 em dashes and 2 en dashes across 6 files | PR #10 / `CLAUDE.md`, 29 Aug 2026 |
| Chip contrast, WCAG 2 | A 5.19 · B 4.79 · C 9.49 · D 6.60 · E 4.80 · F 8.89 light, 6.52 dark | PR #11 / commit `f7d9562`, 29 Aug 2026 |
| `.g-none` before and after | 4.24 light / 3.90 dark on `--muted`; 6.41 / 7.81 on `--ink-2` | commit `f7d9562`, 29 Aug 2026 |
| Rejected E colour | `#de5f4a`, white on it 3.59:1; D/E/F within delta-E 12 to 15 | commit `f7d9562`, 29 Aug 2026 |
| Separation | delta-E 28 (D to E), 20.7 light / 8.9 dark (E to F), 24.0 (B to A), 59.0 (B to C), 13.3 (B's move), 20.2 (D to E, final) | commits `f7d9562`, `58c086d`, `855023b` |
| The two metrics on old B | WCAG 2: dark ink 4.79:1, white 3.63:1. APCA: dark ink Lc 38.6, white Lc 69.2; next-worst chip D at Lc 51.3 | commit `58c086d`, 30 Aug 2026 |
| `--fair` and `--serious-deep` | white on `--fair` 4.97:1 / Lc 79.6; on `--serious-deep` 5.36:1 / Lc 81.3; A 5.19 / Lc 80.4, E 4.80 / Lc 77.5 | commits `58c086d`, `855023b`, 30 Aug 2026 |
| The false banner | "Updated 22 hours ago - collection has stopped" while the collector had pushed on schedule | PR #12 / commit `1d99bcf`, 2 Sep 2026 |
| Fourteen towns named for their county | Carlow, Cavan, Donegal, Kildare, Kilkenny, Leitrim, Longford, Louth, Monaghan, Roscommon, Sligo, Tipperary, Wexford, Wicklow | PR #14 / commit `eecdf2d`, 3 Sep 2026 |
