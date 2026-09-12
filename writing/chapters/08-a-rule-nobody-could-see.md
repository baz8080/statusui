# 8. A rule nobody could see
*~5 min read · PR #10 · 29 August 2026*

*Where we are:* chapter 4 ended with a convention being written into `CLAUDE.md` because it
"had to be asked for by hand across four repos". This is the same lesson a fortnight later,
with a sharper cause, and it is the reason this chapter and the ones after it are punctuated
differently from the ones before.

## The question that opened this stretch

I have a house style, and part of it is: no em dashes. The long dash that separates this
clause from the last one in chapters 0 through 5, and that this chapter has so far managed
without. I have held that preference for years, and I had asked for it, by hand, in session
after session working on these four repositories, and it kept coming back.

The question was why a rule I state constantly was being broken constantly. The answer was
not carelessness, and it was not the model. It was a file path.

## What changed

The rule lived in `~/.claude/CLAUDE.md`, a user-level file that applies to everything I do on
my own machine. It had never been written into this repository's `CLAUDE.md`, nor lifts', nor
the others'. And a Claude Code web session, which is where a great deal of this work happens,
starts from a fresh container that clones the repository and nothing else. No home directory,
no user-level preferences, no accumulated context. The rule was not weakly stated in those
sessions. It was absent from them, every time, and the prose came out accordingly.

> **Concept: a convention lives where the work happens.** A rule is only in force in the
> contexts that can read it. That sounds obvious stated plainly, and it is easy to get wrong
> because the author is never in one of those contexts: from where I sit, the rule is
> visible, because my machine loads the file that holds it. The test is not "have I written
> this down?" but "would a collaborator arriving with nothing but a clone of this repository
> see it?" For a fresh container, a new contributor, or a session that starts from a bare
> checkout, the repository is the entire world. Anything outside it, however firmly held, is
> a preference the work cannot observe, and its violations will read as defiance when they
> are really just silence. This is chapter 7's failure shape in prose: a rule nobody can see
> is indistinguishable from a rule that does not exist.

So the rule went into `CLAUDE.md`, where a fresh clone will find it. The house dash is a
spaced hyphen, like the one in this sentence. Where a sentence reads better without one,
write it out: "which is", "because", a colon, or two sentences.

## Stated, not enforced

The interesting half of the commit is what it refused to do. A lint rule banning the
character would have been three lines and would have failed on day one, because this
repository's existing prose is full of em dashes, including the paragraph immediately above
the new section that bans them. The only way to a green check was a re-punctuation of settled
notes, comments and README paragraphs that nobody had asked for and that would have made
every one of those lines look freshly edited in `git blame` for no reader's benefit.

So the section states the rule, binds new prose to it, records the current count, and says to
fix the old ones only on lines already being edited.

### Worked example: what a rule without enforcement actually buys

The count in `CLAUDE.md` on 29 August was 29 em dashes and 2 en dashes across 6 files. On 12
September, the same six files carry 27 em dashes and the same 2 en dashes (measured 12 Sep
2026). Two gone in two weeks, both on lines that were being edited for other reasons. That is
the whole mechanism: attrition at the rate the files are touched, no rewrite, no flag day,
and no check that can go green only by damaging the thing it guards.

At that rate the backlog outlives the repository, and it does not matter. The rule exists to
stop the count growing, and the count is not growing. Contrast chapter 7's rollout gate,
which tried to enforce a cross-repository step and failed open four times before being
deleted: a written rule that everyone can see and that nothing checks is worth more than a
check that returns a confident answer to the wrong question.

## The awkward part, which belongs here

This series is the largest body of prose in the repository, and it was written on 27 August,
two days before the rule was written down. It carries 222 em dashes across its ten files
(measured 12 Sep 2026), against 27 in all of the rest of the repository. When it merges, it
will multiply the count it is describing by roughly nine.

Under the rule as written, that is fine and it stays. "Fix them on lines you are already
editing" is exactly the instruction, and a bulk re-punctuation of seven finished chapters is
the rewrite the rule exists to prevent. What binds is new prose, so chapters 6 onward are
written to it, and the closing chapter, which is substantially rewritten each time the
inventory moves, loses its em dashes as those lines are edited.

The result is a series that changes punctuation halfway through, which is ugly, and is the
honest record of a convention arriving mid-project. Smoothing it over would mean either
pretending the rule was always there or pretending it does not apply to me. The uisce series
made the same call about its numbers: quote them as they were measured, say when they moved,
and let the seam show.

### How uisce does it

uisce's `CLAUDE.md` carries its own house rules, and the same user-level file was invisible
to its web sessions too. There is no fixing this once in the layer, which is the thing worth
noticing: a shared design layer can absorb a colour token or a date formatter, but it cannot
absorb a writing convention. Nothing in `base.css` reaches a commit message. So the same
paragraph now has to exist in four repositories and drift between them exactly the way the
three stylesheets drifted in chapter 1, with no `rollout.sh` to bump. Conventions are the
part of this problem the layer cannot solve, and the four copies are the price.

## Where it left the layer

No code changed. A `CLAUDE.md` section, a number in it, and a rule that new sessions can
finally see.

## Notes

- PR #10 / commit `4a0025d` (29 Aug 2026): the rule, its cause (a user-level
  `~/.claude/CLAUDE.md` that web sessions never load), the decision to state rather than
  enforce, and the 29 em dash / 2 en dash count across 6 files. From the commit message and
  `CLAUDE.md`'s "Punctuation" section.
- Current counts measured 12 Sep 2026: 27 em dashes and 2 en dashes across the same six
  files on `main`; 222 em dashes across the ten files of `writing/`.
- Chapter 4's comment rule, the earlier instance of the same lesson: commits `57cbafd`,
  `b929690` (26 Aug 2026).
