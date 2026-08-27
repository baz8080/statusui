# Figures registry

Every number quoted in a chapter gets a row here. *Source* is a PR number, a commit hash or
subject, a uisce-series chapter, or "measured" (a read-only command run by the writing
session against the working tree). *Verified* means re-run on the date given; figures lifted
from PR bodies, commit messages or the uisce series are quoted as recorded there, not re-run,
and marked N.

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
