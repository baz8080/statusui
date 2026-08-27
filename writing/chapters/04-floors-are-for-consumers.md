# 4. Floors are for consumers
*~7 min read · PRs #4, #5 · 26 August 2026*

*Where we are:* the layer has a mirror suite (chapter 3) that anyone can run and nothing
makes anyone run. This chapter is one morning — 26 August, roughly nine till half ten —
in which the repo gets CI, loses a Python version it never needed, and writes two of its
conventions down.

## The question that opened this stretch

For its first week this repo had no `.github/` directory at all: nothing verified a change
except whoever remembered to run the suite before pushing. That is a worse deal here than
it would be in an application, because of who inherits a mistake — three sites inline
`base.css` and `ui.js` into every page they build, so a broken file reaches uisce, esb and
lifts the moment their pins move, wearing each site's name when it fails. The question
was not whether to add CI — that part is routine — but what, precisely, this repo's CI has
to promise that a normal project's doesn't. Two answers came out of the morning: the
guards must not be able to skip silently, and the *floor* must be true.

## What changed

### CI, with the skip nailed shut (PR #4)

The workflow itself is uisce's shape: lint, tests, demo build — the same three things
`CLAUDE.md` already told a human to run by hand. The two decisions worth prose are in the
margins.

**node is installed on purpose.** The mirror tests and the freshness tests (chapter 5) are
`skipUnless(node)` — the polite behaviour for a contributor's laptop, and a trap on a
runner: left to whatever the image happens to ship, a green suite would not tell you
whether the Python/JS pairing was checked or silently skipped. A skipped guard looks
exactly like a passed one from a distance, and these are the tests that hold the layer's
two languages together — so the workflow pins node explicitly rather than hoping. The
skip stays for humans; CI is the place where it must be impossible.

**The demo build runs too.** `demo/build.py` is the only place the two files are rendered
together as a page, so a failure there is a broken file every consumer would inline. Its
limit got written down at the same time: CI catches a change that *throws*, not one that
*renders wrong* — looking at the page stays a human job. A layer with no site of its own
has no screenshot diff against reality; the honest thing is to say where the machine's
assurance ends rather than imply the pipeline sees pixels. (uisce has the same limit for
different reasons: its pages are checked by a human against real data. Here there is no
real data to be wrong against.)

What PR #4 deliberately left out matters to the next PR: no Python version matrix, yet.
The floor stood at 3.9, guarded only by `ast.parse(feature_version=(3, 9))` — a syntax
check the repo itself called best-effort, blind to a 3.10-and-up standard-library call.
A 3.9 leg in CI would close that hole; but nobody could say why the floor was 3.9.

### The floor moves to where the consumers are (PR #5)

> **Concept: a floor is a promise to your slowest consumer.** A library's `requires-python`
> is not a statement about the machine it is developed on; it is the oldest interpreter it
> promises to keep working for, and the correct value is set by the consumers, not the
> library. Two rules fall out. A floor *below* every consumer's is harmless slack — uisce
> demands 3.14 and can install a `>=3.11` dependency without noticing. A floor *above* a
> consumer's is a broken promise, and modern resolvers refuse it loudly at lock time rather
> than letting it fail at import time. So the number to find is the highest floor no
> consumer sits below: raising it costs the slowest consumer an upgrade; keeping it low
> costs the library — every syntax choice and standard-library call is constrained by the
> oldest interpreter on the list. This layer's floor was about to be set by a single-board
> computer in a house.

The 3.9 floor, it turned out, was inherited folklore: it "was never for this repo — it was
esb's Raspberry Pi and lifts" (PR #5). The esb pipeline runs on a Raspberry Pi, and the Pi
runs whatever Python its operating system ships.

#### Worked example: the Pi sets the number

Raspberry Pi OS *bookworm* ships `python3` at **3.11.2**. So 3.11 is the floor: high
enough that nobody is maintaining 3.9 compatibility out of superstition, low enough that
the Pi takes a deploy with the interpreter it already has, no hand-built Python involved.
uisce, at 3.14, is unaffected by rule one above. And rule two fired for real: lifts still
declared `requires-python = ">=3.9"`, which sits *below* the new floor, and resolving it
against this change fails at lock time with the resolver saying exactly what this chapter
says —

```
hint: The `requires-python` value (>=3.9) includes Python versions that are
not supported by your dependencies (e.g., statusui==0.1.0 only supports
>=3.11). Consider using a more restrictive `requires-python` value (like >=3.11).
```

— so `rollout.sh` would stop on its lifts leg until lifts took the one-line bump (PR #5,
26 Aug 2026; esb needed the same bump and its own cleanup, esb PR #16). The floor stopped
being folklore and became a number with an owner: it moves when the Pi's OS does.

Two clarifications rode along. The **browser floor is not the Python floor**: `ui.js`
stays ES5 — the pages carry no transpile step, so what is written is what every reader's
browser must run — and that floor moves on the browsers' schedule, not the Pi's;
`CLAUDE.md` had stated the two in one sentence that read as though they moved together,
and now says they don't. And **the floor and the interpreter are different questions**:
`.python-version` pins 3.14 for local work, same as the sites — the floor says how far
*down* the package must work, not where it is developed. The 3.9 syntax-parse test went
with the floor it guarded, since at 3.11 it would only re-ask whether the file parses,
which every other test already needs to be true. Verified on 3.11.15 before merging, not
just linted: 32 tests, demo builds.

### The matrix closes the loop (commit `95462f5`, same morning)

With `requires-python` at 3.11 and development on 3.14, the metadata described an
interpreter nothing exercised: ruff guards the floor's *syntax*, but a 3.12-only
standard-library call would lint clean, pass CI on 3.14, and be a lie in the metadata. So
the CI job became a two-leg matrix — 3.11 and 3.14 — with `UV_PYTHON` picking the
interpreter (it out-ranks `.python-version`, so the checkout isn't edited per leg) and
`fail-fast` off, because a floor that only fails after the other leg is cancelled says
nothing about which one broke. The commit is candid about the weight class: nothing runs
this package on 3.11 in production today — the sites build on 3.14; the Pi constraint
arrives via what esb *resolves*, not what it runs here. But the floor is what esb resolves
against, so it should be true, and now a machine checks it both ways: the resolver refuses
a floor set too high, the matrix catches one claimed too low.

### Writing the rules down (commits `57cbafd`, `b929690`)

The morning ended with two smaller commits that belong to the same theme. The CI YAML's
comments got cut back to what the YAML cannot say — and then the principle itself went
into `CLAUDE.md`: comments say **why**, not what; one line where one will do. The commit
message gives the reason the rule earned a written home: it "had to be asked for by hand
across four repos, which is the definition of a convention that should be written down
rather than remembered." Four repositories sharing one author's conventions is the same
drift problem as three sites sharing one stylesheet — chapter 2's lesson, applied to
prose. `CLAUDE.md` is the conventions' `base.css`.

### How uisce does it

uisce develops and ships on one interpreter, 3.14, and its CI runs one version — correct
for an application that deploys to machines it controls. The floor question exists here
*because* this repo is a dependency: it inherits the union of its consumers' constraints,
including a Raspberry Pi it has never met. Same asymmetry in the suites: uisce's CI runs
its site's tests; this repo's CI must also prove the package resolves and runs where the
*consumers* stand. The dependency arrow decides what CI has to mean.

## Where it left the layer

Green checks on every push, on both the floor and the development interpreter; the mirror
un-skippable where it matters; a floor with a named owner instead of a folk memory; and
the comment rule in writing. One morning, three PRs' worth of hygiene — and the afternoon
of the same day put the machinery straight to work, because the design-alignment pass
(chapter 5) was already waiting with three promotions.

## Notes

- PR #4 / commit `dfd8379` (26 Aug 2026): no `.github/` before; node pinned so
  `TestMirror`/`TestFreshness` cannot skip in CI; demo build as the only joint render;
  "catches a change that throws, not one that renders wrong"; matrix deferred. From the PR
  body and commit message.
- PR #5 / commit `cca0f46` (26 Aug): 3.9 → 3.11; Raspberry Pi OS bookworm ships 3.11.2;
  uisce at 3.14 unaffected; lifts `>=3.9` fails `uv lock` (hint quoted from the PR body);
  `test_python_39_floor` removed; verified on 3.11.15, 32 tests. esb PR #16, uisce PR #60.
- Commit `95462f5` (26 Aug): matrix 3.11 + 3.14, `UV_PYTHON` over `.python-version`,
  `fail-fast: false`; "the floor is what esb resolves against, so it should be true."
- Commits `57cbafd`, `b929690` (26 Aug): comment rule; "asked for by hand across four
  repos." Current `ci.yml` (41 lines) verified in the working tree, 27 Aug 2026.
