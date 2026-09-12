# 7. A guard that fails open
*~9 min read · PR #9 · 28 August 2026*

*Where we are:* the layer is one JavaScript file inlined into every page of three sites, and
a treaty list called `JS_GLOBALS` names everything it declares so no site script can shadow
one. This chapter splits that file in two, and spends the rest of the evening discovering
what the split did to the treaty.

## The question that opened this stretch

A page that renders its day bars in Python and calls one listener still had to inline the
whole of `ui.js` to get that listener: the search box, the shard loader, the month tabs,
`freshness`, `stampLine`, all of it. That is 15.9 KB on a page whose only interactive
element is a caption strip, and those pages are per place, per site. lifts publishes twenty
station pages today and will publish a hundred. uisce's and esb's county and area pages ship
no JavaScript at all, which is why their day bars have no captions: the cost of adding one
was the whole app.

## What changed

`bindDayCaption` moved into its own file, `caption.js`, and a template may take
`<!--UI-JS-CAPTION-->` instead of `<!--UI-JS-->`. The static page gets 1.1 KB instead of
15.9 KB (measured 12 Sep 2026 against the working tree). `ui_js()` still returns both files
concatenated, so an app page is unchanged and the published list of globals is unchanged:
the listener is still in the bundle, still in the treaty, still un-shadowable. The only new
fact is that a page may now ask for a slice.

One ordering detail carries more weight than it looks: `caption.js` goes **last**. `ui.js`
opens with the `"use strict"` directive, and a directive is only a directive while nothing
precedes it. Put the caption file first and the strict-mode pragma of the entire bundle
silently becomes a string literal that evaluates to itself and does nothing.

### Worked example: what twenty pages weigh

Measured against lifts with the change overlaid, its twenty station pages go from 732.7 KB
to 467.1 KB (PR #9, 28 Aug 2026). That is 265.6 KB saved across twenty pages, or 13.3 KB a
page, against a 14.8 KB difference between the two bundles: close, and short of it, because
what a page drops is the app it never called and not one byte more. At the hundred pages
lifts is heading for, the same arithmetic is 1.3 MB. The front page grows very slightly, by
the comment at the head of the new file.

## The part that took the rest of the evening

Here is the problem the split created, and it is a good one. All three sites build their
redeclaration guard by reading the layer's source off disk:

```python
Path(statusui.__file__).parent / "ui.js"
```

That worked when the bundle was one file. The moment a site's pin moves to this commit, that
line reads two thirds of a bundle: `bindDayCaption` is no longer in `ui.js`, so it drops out
of the set the site checks against, and a site script may now declare its own
`bindDayCaption` and shadow the shared listener with every test in every repository still
green.

> **Concept: a guard that passes by seeing less.** The dangerous shape is a check derived
> from the thing it checks. This guard asked "does my script redeclare any name in that
> file?", so shrinking the file shrank the question, and the suite went green *because*
> coverage had been lost. Nothing fails. Nothing can fail: a passing test and an
> absent test are the same colour. Compare the drift of chapter 2, where three copies of
> the layer fell five commits apart and nothing said so, or chapter 4's mirror tests
> skipping silently where node was missing. It is the same failure wearing a third costume,
> and the family resemblance is that in each case the mechanism reported success for a
> question it had stopped asking. A guard must therefore be derived from something that
> does not move when the guarded thing moves: an independently stated list, or a single
> published answer that the producer maintains.

The fix is the published answer: `statusui.js_globals()` returns the names the whole bundle
declares, whatever the bundle is split into next, and a test holds it to the documented list.
A consumer changes one line at rollout, from reading a file to asking a function, and the
guard cannot go stale again.

That was the second of nine commits. The seven that follow are about how badly I wanted to
enforce the thing I had just documented.

### Four rounds on a parser

`js_globals()` reads declarations with a regular expression, one name per declaration at
column zero, so `var a = 1, b = 2;` would publish `a` and leave `b` guarding nothing. The
bundle has no such line today; the consumers' own scripts do, so the style was worth pinning
rather than assuming. The first guard for it emptied string literals and bracketed groups so
that what remained of a declaration was its own commas.

That guard guarded nothing. Its string-emptying pass mis-pairs on the quotes inside `esc()`'s
character class, `/[&<>"']/g`, and swallows the rest of the file from there: an injected
`var zqA = 1, zqB = 2;` anywhere below line 12 left the test green. My own check of the guard
had injected above line 12, which is the only region of the file where it worked (commit
`7203cdd`). Regex was the wrong tool twice over, so the assumption is now checked against a
JavaScript engine instead: run the bundle in a bare `vm` context and ask which names it left
behind. That is the truth `js_globals()` is approximating, and the same injection now fails
at every position. node is already a test dependency for the mirror suite of chapter 3, and
chapter 4's CI installs it.

Two later rounds tightened the same area. The multi-declarator test had been comparing the
engine against *its own inline copy* of the regex, so rewriting `js_globals()` would have
left it green; it calls the shipped function now. And `js_globals()` briefly grew an optional
argument for the convenience of that test, which quietly widened the public API into the
exact failure it exists to prevent: a site that kept reading `ui.js` off disk could pass it
in as `js_globals(shared_js)`, look migrated, pass its suite and the rollout, and still miss
`bindDayCaption`. There is one right answer, so the public function takes no argument and
returns it; the parser moved to a module-private `_declared()` that only the tests drive.

### The gate, and why it went

Documentation that says "every consumer must change this line" is a promise nobody checks,
so the same PR taught `rollout.sh` to refuse a site that still parses `ui.js`. The gate
lasted four review rounds and failed in a new way each time.

1. It aborted the **whole rollout** at the first site that parses `ui.js`. That site is
   uisce, first in the loop, so esb and lifts were never reached. Worse, it demanded a change
   those sites cannot make until their pin moves, which is the pin it was refusing to move.
   Fixed by skipping the blocked site, saying so, and reverting its bumped lockfile rather
   than leaving it dirty for the next run.
2. It matched the double-quoted literal `"ui.js"`, and nothing makes a consumer quote it that
   way. A guard written with single quotes sails through, and the pin lands on a site whose
   redeclaration check has quietly stopped covering `bindDayCaption`.
3. The last round found three at once. A mention of `js_globals(` anywhere under `tests/`
   opened the gate while the real guard still read the file. A skipped site left the script
   exiting 0, while its own header promises fail-fast and the README promises three pull
   requests. And `ui.js` is a substring of `statusui.js_globals`, so the fallback grep matched
   the very migration it was meant to detect, and would have skipped a migrated site forever.

So the gate was deleted (commit `050c9a8`), and the commit message is the lesson:

> A gate that fails open is worse than the documentation it replaced, because it reads like
> enforcement.

The deeper reason it could never work is worth stating plainly. Two greps over a directory
cannot tell whether a test parses a file. Only running that test could, and it passes either
way, which is the whole problem the gate was trying to route around. An enforcement mechanism
that cannot observe the failure it exists to prevent is not weak enforcement; it is a second
thing to maintain that returns a confident answer to a question it never asked. `rollout.sh`
is a pin bumper again.

What replaced it is honest and much less satisfying: **step 5 of the README checklist**,
marked open until each site has done it once, naming both halves of the work. The guard must
ask `js_globals()`, and the template split that finds where a site's own script begins must
learn the second marker, because `<!--UI-JS-CAPTION-->` does not contain the string
`<!--UI-JS-->` and the first converted template otherwise raises `IndexError`, then drops
that page from the check once it stops raising. The checklist says, in as many words, that
neither the site's suite nor a green rollout can tell you the step is still outstanding.

One smaller find rode along in the same rounds, and it is the chapter in miniature:
`ui_js()` had been concatenating the two files with nothing between them. It worked, because
`ui.js` happens to end in a newline, which is an invariant nothing stated and nothing
checked. A trailing line comment would have eaten `caption.js`'s first line and killed every
page that inlines the bundle. The newline is the join now, checked by giving `ui.js` a
trailing comment and watching the listener survive.

### How uisce does it

uisce can enforce its invariants because it owns every line that could violate one. When its
schema grows a column, the code that reads the column is in the same repository as the code
that writes it, and one test run covers both. The layer's equivalent violation lives in
another repository, on a clock the layer does not control, and the only mechanisms available
across that boundary are the ones a consumer opts into: a published function it may choose to
call, a checklist item a human may choose to do. Chapter 2 said the deploy gap is a staging
area; this chapter is the bill for it. Where a contract crosses a repository boundary, it
degrades to documentation at the boundary, and the useful work is making the documented step
small, single and hard to misread rather than pretending a script can police it.

## Where it left the layer

Two JavaScript files, one bundle, one published set of globals, and a checklist item
outstanding in three repositories. The suite grew a class that runs the bundle in a bare
engine context to check the parser that publishes the set, which is a strange sentence to
write about 23 lines of caption listener, and is the right amount of paranoia for something
three sites inline into every page. `test_es5_syntax_only` also learned to ban `class` as a
declaration, since a top-level class would be invisible to both the regex and the engine
check, and `class` is otherwise the HTML attribute the bar builders write into strings all
day.

## Notes

- PR #9 / commits `6c99e87`, `2a03777`, `dead8f2`, `7203cdd`, `0a20abb`, `73f772c`,
  `050c9a8`, `0a91fcf`, `13f02b7` (28 Aug 2026): the caption split and everything above.
  Figures and quotations from the commit messages.
- Bundle sizes re-measured 12 Sep 2026: `statusui.ui_js()` 16,270 bytes (15.9 KB),
  `statusui.caption_js()` 1,123 bytes (1.1 KB), `caption.js` 23 lines.
- lifts 732.7 KB to 467.1 KB across twenty station pages: PR #9, measured 28 Aug 2026 with
  the change overlaid; the per-page and hundred-page arithmetic is mine.
- README step 5 and the `IndexError` note verified in the working tree, 12 Sep 2026;
  `js_globals()` returns 26 names, matching `JS_GLOBALS`.
