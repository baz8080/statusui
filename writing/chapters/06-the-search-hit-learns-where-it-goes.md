# 6. The search hit learns where it goes
*~7 min read · PR #8 · 27 August 2026*

*Where we are:* chapter 5 ended with the place search promoted out of esb and into the layer,
ranking hits and handing the pick back to the site. This chapter is the day after, and it is
about the half of the search box nobody had looked at: where a hit actually takes you.

A note on the punctuation, since this is the chapter where it changes: from here on the
chapters carry no em dashes. Chapter 8 is why.

## The question that opened this stretch

The search box could only ever land a reader on the parent county. `searchHits` returned
`[name, county]` pairs, `bindSearch` rendered a button carrying the county alone, and the
matched name, the thing the reader actually typed, was thrown away at the moment of the
click. That was fine when a county page was the only page there was. By late August it was
not: both uisce and esb publish a page per area now, and neither could reach one from the
control readers actually use. Type your town, get your county, hunt for your town again in a
directory of seventeen hundred rows.

## What changed

An index entry may now be a plain name or a `[name, target]` pair, and a hit is
`[name, county]` or `[name, county, target]`. A site that indexes plain names sees exactly
the shape it saw before, which is the property that kept lifts to a pin bump.

> **Concept: shipped, not derived.** The obvious implementation is to compute the target:
> the site's page URLs are its place names run through a slug function, and the layer has a
> slug function, so let the layer slug the name at click time and save everyone the payload.
> It is wrong, and chapter 3 already said why without knowing it would matter. The layer's
> two slug functions are the one pair deliberately left unpaired: the Python one folds a
> fada to its plain letter, the JavaScript one does not, because the Python one builds
> static URLs and the JavaScript one never needed to. So the browser's slug and the
> build's slug disagree on exactly the names Ireland is full of, and a derived target would
> send about twenty place names to a URL that does not exist (PR #8, 27 Aug 2026). The
> general rule: when a value is produced by one system and consumed by another, ship the
> value. Recomputing it at the far end means maintaining two functions that must agree
> forever, and they will not.

### Worked example: the name the two sides spell differently

Run the same place name through both halves of the layer today:

| | `Dún Laoghaire` | `Béal Átha na Sluaighe` |
|---|---|---|
| Python `statusui.slug` (builds the page) | `dun-laoghaire` | `beal-atha-na-sluaighe` |
| JavaScript `slug` (would build the link) | `d-n-laoghaire` | `b-al-tha-na-sluaighe` |

(measured 12 Sep 2026 against the working tree.) The browser's version replaces every run
of non-ASCII with a hyphen, so `ú` becomes a dash and the fada eats the letter with it. A
reader in Dún Laoghaire clicking their own town would land on a 404 while every ASCII town
in the county worked perfectly, which is the worst shape a bug can have: correct for the
author, broken for a fifth of the country, and invisible to any test written in English.

### A hit is an entry point, so it is a link

The second half of the change is that with an `href` option the hits become real anchors
rather than buttons. The argument is the one uisce made about its overview rows the week
before (its series, chapter 11, "Be findable"): a search hit is an entry point, not a
drill-down, so it should be something a reader can middle-click, copy, share and open in a
new tab. A button can do none of those, because a button is a thing that happens rather
than a place that exists.

That leaves the awkward case of a hit that lands somewhere the app is already showing. A
county hit does not want a page load: the app can switch views instantly, and reloading the
whole page to show something it already has is a regression. The answer is that `pick()`
returning true suppresses the link. So a county hit carries a real URL, which is what the
reader's browser and the reader's right mouse button see, and still does not reload when
clicked normally. The href is the truth about where the row goes; the handler is an
optimisation over it. That ordering is what makes the row honest: everything a reader can
do with a link works, and the fast path is a bonus rather than the only path.

And where a site supplies no `href` at all, the hits stay buttons, exactly as before. lifts
has no per-station targets to point at yet, so lifts takes this entire change as a pin bump
and nothing else.

### What the tests were asked to prove

Two things, and the second is the one worth copying. The five existing `searchHits` cases
pass **unmodified**, and that is deliberate rather than lucky: they are the backward
compatibility guard, and a change that had to edit them would have been a change that broke
lifts. An untouched old test is evidence in a way a new passing test is not.

The other half: `bindSearch` had no coverage at all. It is the DOM side, the part that is
awkward to test and therefore was not, and it had just grown a link, a modifier-key rule and
a delegated click handler. It gets tests now, driven against a small DOM shim.

## What went wrong: three holes in one click handler

The review of that handler found three, all shipped the same day (commit `84578c7`).

**A modified click was swallowed before `pick()` ran.** The new guard said: if the reader
held a modifier, leave the click to the browser. Correct where there is a link to follow,
and actively destructive where there is not. On lifts, which supplies no `href`, the hits are
buttons, and nothing follows a button. So a Ctrl-click or Cmd-click on a lifts search result
now did precisely nothing, where before it had picked the place. The guard belongs only where
there is a link.

**Alt was missing from the modifier list.** Alt-click is save-link in several browsers, so
the one modifier left out was the one that turned a download into a view switch.

**The selector lost its `button` qualifier** when hits became links, and `closest()` climbs
as far as it likes: a click that matched no row would keep walking up the document and pick
up whatever ancestor happened to carry a `data-c` attribute. On a page where the search box
sits inside a county card, that is a click on empty dropdown space navigating somewhere. The
lookup is bounded to the results box now.

All three are pinned by tests that fail against the previous commit, which is the only
standard worth having for a regression test: if it passes on the broken code, it is testing
something else.

### How uisce does it

uisce owns its URLs. It decides what a page is called, slugs the name itself at build time,
and if it wants to change the scheme it changes one function and rebuilds. The layer owns
none of that and must not: it cannot know that uisce folds fadas and lifts has no area pages
at all. So where uisce's equivalent problem is "what should this URL be?", the layer's is
"how do I carry a URL I am not allowed to compute?" The answer, an opaque string travelling
with the data, is less elegant than a shared slug function and is the only version that
cannot quietly break a site the layer has never seen.

## Where it left the layer

The search box now ranks, dedupes, links and picks, and a site can adopt as much of that as
it has pages for. The dedup key it inherited from chapter 5 is the one part of the machinery
this change did not touch, and it had a fortnight left before it broke fourteen towns.
That is chapter 10.

## Notes

- PR #8 / commits `e2910d5`, `84578c7` (27 Aug 2026): index entries as `[name, target]`;
  hits as pairs or triples; `opts.href`; `pick()` returning true suppressing the link; the
  twenty fada place names; five `searchHits` cases unmodified as the compatibility guard;
  `bindSearch` tested against a DOM shim; modified-click, Alt and `closest()` holes. All
  from the two commit messages.
- Slug divergence re-measured 12 Sep 2026 by running `src/statusui/ui.js` under node and
  `statusui.slug` in Python over the same two names.
- uisce's hash-route retraction and the shareable-URL argument: uisce series chapter 11.
