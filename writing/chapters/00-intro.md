# 0. Three websites walk into a stylesheet
*~5 min read · an introduction to the series*

## The premise

Over the summer of 2026 I ended up running three status websites. The first, uisce, answers a
question about water — *are other areas having as many outages as Leixlip?* — and grew, over
eight weeks and sixty-one pull requests, into a site with letter grades, Census-weighted
availability and 1,700-odd named places. (That story is its own series, in the uisce
repository's `writing/` directory; this one does not retell it.) The second, esb, does the
same job for electricity outages. The third, lifts, does it for broken lifts at rail stations.

Three different feeds, three different databases, three different sets of caveats — and,
deliberately, one look. The same county rows, the same bars of little day cells, the same
grade chips, the same footer. A person who has learned to read one site has learned to read
all three. That was the intent, anyway. What actually existed by mid-August was three
*copies* of that look, one per repository, "kept in step by hand" — a phrase, as the uisce
series puts it, that describes a wish rather than a mechanism. A contrast fix landed on the
water site on 18 August and simply never reached the electricity site. Nothing failed.
Nothing ever fails when a copy drifts; that is the problem with copies.

So on 19 August the shared part of the look moved into a fourth repository, `statusui` — the
one this series is about. It is small: on the day I write this it is 245 lines of CSS, 300
lines of JavaScript and 190 lines of Python (measured 27 Aug 2026), plus the tests that hold
them together. Each site installs it as a dependency pinned to an exact commit, and a change
here reaches a site only when that pin moves.

## Why a repo this small gets a series

Because almost nothing about it behaved the way I expected, and the ways it misbehaved are
general. In its first week this repo:

- was vendored — copied file-by-file into each site — and un-vendored again within a day,
  after the copies drifted five commits apart with nothing failing to say so;
- needed three fixes in one evening to a four-line provenance stamp, before the whole
  mechanism was abandoned for a pin;
- caught its own two languages disagreeing about what "2.25 hours" is, fixed that, and then
  had the fix break thirty-six commoner values while the tests stayed green;
- discovered that its Python "floor" — the oldest interpreter it promises to run on — was
  being set not by anything in this repo but by the operating system of a Raspberry Pi in
  someone's house.

A shared UI layer is the smallest possible distributed system: one producer, three consumers,
no telemetry. Everything that makes distributed systems interesting — versioning, drift,
contracts, staged deployment — shows up here in miniature, small enough to see whole.

## How this series relates to the uisce one

This is a companion series, same author, same voice, same rules: every number carries its
source and the date it was measured, every hard idea gets a plain-English concept box, every
concept gets a worked example with real names in it. Two of the events told here are told
from the other side in the uisce series — its chapter 14 covers the extraction and the phone
review as the *site* experienced them, its chapter 16 the design alignment — and where that
happens I point across rather than repeat.

But the two series have different centres of gravity, and the differences are the point. The
uisce repo is a site: it has data, and readers, and its numbers are person-hours and
populations. This repo has neither. Its "users" are three build scripts; its numbers are line
counts and commit hashes; nobody who reads the water site will ever knowingly see it. The
questions that shaped it are correspondingly different — not *is this number fair to Cork?*
but *when both sides of a page format the same figure, who checks they agree?* and *whose
Python version is a library allowed to require?* Each chapter carries a short *How uisce does
it* note where the answers genuinely differ, and the closing chapter collects them.

## The shape of the story

| | | |
|---|---|---|
| **1** | *Three copies of one look* | 19 August: the extraction. What the three sites already agreed on word for word, what they didn't, and the rule that decided — plus the demo page and the sync script. |
| **2** | *A pointer beats a copy* | One day of vendoring: the stamp that needed three fixes in an evening, the five-commit drift, and the switch to a pinned dependency with a one-command rollout. |
| **3** | *Hold the mirror to account* | The layer speaks Python at build time and JavaScript in the browser. A test harness runs both and holds them to identical output — and immediately finds them lying. |
| **4** | *Floors are for consumers* | CI arrives; the Python floor moves from 3.9 to 3.11 because of what a Raspberry Pi ships; the floor and the interpreter turn out to be different questions. |
| **5** | *Promoted on the second user* | The rule that fills the layer: nothing moves up on speculation, everything moves up on its second user. Date formatters, a freshness stamp, a search box — and the deploy gap that dictates what may be deleted when. |
| **6** | *Closing* | The inventory, the constraints, what this repo can never check about itself, and the uisce comparisons in one table. |

## How it was built, said once

Like the three sites, this repo was written with an AI assistant — Claude, in Anthropic's
Claude Code — under my direction, and so was this series. The commit trailers name the models;
I chose what to extract, reviewed every diff, and the mistakes recounted here are mistakes I
approved. As with the uisce series, nothing in the account depends on who typed it: the
figures are measurements against a public repository, and the tests that back them are in it.
I say this once, here, so the chapters can say "I" without a footnote each time.

## A note on the numbers

Everything quoted is either measured against the working tree on a stated date (mostly 27
August 2026), or lifted from a pull request, commit message or the uisce series with its date,
and `figures.md` in this directory has a row for each. The week this series covers ended the
day before it was written, which makes the sourcing easy and the hindsight suspiciously fresh;
where I can no longer tell what I believed at the time from what I know now, I say so.
