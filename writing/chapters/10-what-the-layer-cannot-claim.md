# 10. What the layer is in no position to say
*~9 min read · PRs #12, #13, #14 · 2–5 September 2026*

*Where we are:* the layer now writes sentences and rows that appear on three sites, in their
names, to readers who have never heard of it. This chapter is two separate bugs, a week
apart, that turn out to be the same bug: the shared code asserting something about a site's
data that only the site could know.

## Part one: the banner that knew too much

### The question that opened this stretch

The stale banner said, in red, at the top of a site:

> Updated 22 hours ago - collection has stopped

The collector had not stopped. It had run and pushed on schedule all night. What had fallen
over was the site build, downstream of it, so the data was exactly as old as the banner said
and the sentence explaining why was false.

> **Concept: a page can see its own age, not its cause.** The browser has one fact: a
> timestamp in the payload, and the current time. Everything upstream of that timestamp is
> invisible. A collector that died and a build that died present identically from here,
> because both arrive as data that has stopped moving, and so does a deploy that failed, a
> feed that went quiet, and a cache serving yesterday. `freshness()` had been reading a cause
> off an effect that has several. The general rule: a component may report what it can
> observe. The moment it names a mechanism it cannot see, it is guessing on behalf of
> everyone who reads it, and it will be confidently wrong at exactly the moment someone is
> relying on it, because that is when people read the banner.

### What changed, twice, in one evening

The first fix (PR #12) removed the cause entirely. The banner states the age and stops; the
red carries "something is wrong" on its own, which is what the comment above the function
had always said the *warning*, rather than the wording, was for. `stampLine()` had been
making the same inference and got the same treatment.

The migration mechanics are worth a paragraph, because they run the opposite way to
chapter 5's rule and for the same reason. `freshness()` lost its `note` argument. Extra
arguments are ignored in JavaScript, so a site still passing one keeps working until its pin
moves, which is the usual direction: the layer changes first, the sites catch up. But a site
that *tidied* its call early, dropping the argument while still pinned to an older statusui,
would render a dangling " - " before an empty note. So the call sites must not be cleaned up
before the bump. Chapter 5's version of this was "deletions ride the pin bump"; this is the
same constraint seen from the caller's side, and the general form is that a compatible change
is only compatible in one direction at a time.

Then, the same evening, it came back (PR #13). Naming no cause is defensible and unhelpful: a
reader who sees a big number still has to work out whether something is broken or whether
they have simply arrived at an awkward hour. The sentence that returned is hedged:

> Updated 22 hours ago - the last data build may have failed

"May have failed" names the likeliest cause without asserting it, and it stays true when the
other half is the one that broke. That is the whole difference from the sentence it replaces,
and it is the difference between a claim and a reading. The wording is uisce's own, which
predates all of this and was always the better of the two.

### The parameter that was not a parameter

Here is the part that revises chapter 5. That chapter presented `freshness(iso, staleHours,
note)` as the model promotion: uisce wrote it, esb became the second user, and the two
constants that differed between them, the threshold and the sentence, became arguments. The
second user, I wrote, tells you where the parameters go.

Two weeks later, one of those two parameters is gone. The sentence is back inside the
function, identical for all three sites, because esb's "collection has stopped" was never a
different requirement. It was a wrong sentence. The parameter existed to preserve a
difference that should have been resolved by someone noticing one of the callers was making a
claim it could not support.

So the rule needs its qualifier. A second user tells you where the *differences* are; it does
not tell you which of them are real. Some differences are requirements, like esb's 16-hour
staleness threshold against uisce's 24, which is genuinely per site because the feeds update
at different rates. Others are one caller being wrong, and parameterising those does not
absorb the mistake, it ships it to everyone and gives it a home with a name. The test worth
applying at promotion time is not "do the callers differ?" but "should they?", and that
question cannot be answered by reading the callers alone.

## Part two: fourteen towns named for their county

### The question that opened this stretch

Fourteen Irish towns share the name of their county: Carlow, Cavan, Donegal, Kildare,
Kilkenny, Leitrim, Longford, Louth, Monaghan, Roscommon, Sligo, Tipperary, Wexford and
Wicklow. On uisce and esb, each of those towns has an area page of its own, distinct from the
county page. Not one of them could be reached from the search box.

The cause is a line from chapter 5. The dedup that landed in PR #6 keyed on name and county,
because lifts indexes each station under its own name and a place could otherwise render two
identical buttons. That key is correct for lifts and wrong here: the county hit ranks first,
takes the key `Sligo|Sligo`, and the town's targeted entry, which is a different destination
with the same name in the same county, collides with it and is dropped. The page existed, was
listed in the area directory, and was invisible to the control readers actually use.

#### Worked example: typing "Sligo"

| | ranked | key under the old rule | rendered |
|---|---|---|---|
| County Sligo | first, county-prefix | `Sligo\|Sligo` | yes |
| Sligo town, target `sligo` | second, match at position 0 | `Sligo\|Sligo` | no, collides |

Under the new rule the key includes the target, so the second row keys as
`Sligo|Sligo|sligo` and survives. The county still ranks first, so typing a county name still
lands on the county, exactly as before. The town is now one row below it instead of nowhere.
A bare name that is also a county still collapses to one row, which is what keeps lifts
rendering as it did.

This is the same shape as chapter 6's slug: a rule that is provably correct for the consumer
that motivated it, and quietly wrong for a consumer with different data. Three sites is
apparently enough to keep finding these, and each one is found by the site that has the
unusual data rather than by the layer that wrote the rule.

### The review finding, which is the better bug

The first version left the default annotation blank for both rows, on the reasoning that a
site indexing targets should supply its own word for the distinction. The demo now uses
"town". But shared code has to be safe for a consumer that supplies nothing, and this one was
not: a site that indexed pairs and passed no `note` would render two rows reading exactly
`Sligo` and `Sligo`, one going to the county and one to the town, with nothing to tell them
apart.

That is worse than the bug it fixed. One row going to the wrong place is a limitation a
reader can learn. Two identical rows going to different places is a coin toss presented as a
choice, and the reader has no way to know which is which or that there was a difference at
all.

So the default now keeps the county beside such a hit: the shared code is legible on its own,
and a site's `note` only chooses a better word for what is already distinguishable. The
supporting test learned something too, and it is a small lesson worth keeping: it now asserts
that both links are present before comparing their order, so a regression reads as a failed
assertion showing the markup rather than a `ValueError` thrown while unpacking a list that
turned out to be one element long. A test that crashes tells you it is unhappy; a test that
fails tells you why.

### The thread running through both

The banner claimed to know why data was old. The search claimed two rows were the same place.
Both are the layer asserting something about a site's data that its own inputs do not prove,
and in both cases the shared code had every reason to believe it: one timestamp really does
usually mean a stalled collector, and two rows with the same name in the same county really
are usually the same place. The rule that falls out is narrower than "be careful":

**Shared code may compute freely, and may only assert what its inputs establish.** Where the
inputs are ambiguous, the honest options are to hedge the claim, as the banner does, or to
keep the ambiguity visible, as the search now does by printing the county next to both rows.
What it may not do is resolve the ambiguity on the sites' behalf and present the result as
fact, because the layer is the one participant in the system with no access to the thing
being claimed.

### How uisce does it

uisce has the same problem and solves it with a vocabulary this repo cannot borrow. Its
series ends on what the site can and cannot say: that a start time is publication rather than
onset, that a `closed_at` is a floor, that the 500 metre radius is an assumption. It can write
those caveats down because it has a page of its own, a methodology section and readers who
arrived to learn about water. The layer has none of that. It has no page to disclaim on and
no reader who knows it exists, so its only way to be honest is structural: a sentence hedged
enough to be true for every site, or no sentence at all, and a default that shows the
ambiguity rather than a note that explains it. uisce can caveat. The layer can only be
careful.

## Where it left the layer

`freshness(iso, staleHours)`, two arguments, one hedged sentence that all three sites share.
A search dedup keyed on the destination rather than the name, with fourteen town pages
reachable again on two sites, and a default annotation that is safe for a consumer that
configures nothing. And one revision to the rule chapter 5 was built on, which is the first
time this series has had to correct itself.

## Notes

- PR #12 / commit `1d99bcf` (merged 2 Sep 2026): the false "collection has stopped", the
  build rather than the collector, `note` dropped from `freshness()` and `stampLine()`, and
  the one-directional compatibility of the argument removal. From the commit message.
- PR #13 / commit `adbb30d` (merged 2 Sep 2026): the hedged sentence restored inside the
  function, uisce's original wording, `stampLine()` left without one. From the commit
  message; the current two-argument signature verified in `src/statusui/ui.js`, 12 Sep 2026.
- PR #14 / commits `eecdf2d`, `1119cb9`, `c4bb768` (3–5 Sep 2026, merged 5 Sep): the fourteen
  towns by name, the `name|county` collision, the key including the target, the default note
  keeping the county, and the test asserting presence before order. The uisce half of
  `baz8080/esb#28`. From the commit messages; dedup and default-note behaviour verified in
  `searchHits` and `bindSearch`, 12 Sep 2026.
- Chapter 5's promotion of `freshness` and its `note` parameter: PR #3, 26 Aug 2026.
