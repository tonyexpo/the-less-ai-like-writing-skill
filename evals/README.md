# Eval

What this measures, how, and what it cannot tell you.

## The question

Does `SKILL.md` remove more generic-LLM prose patterns than ordinary writing
advice does?

Not "does the skill beat an empty prompt". A long style instruction beating no
instruction at all is not a finding, it is a length effect. So the benchmark
runs three arms over the same drafts with the same user instruction, and the
only thing that varies is the system prompt:

| arm | system prompt |
| --- | --- |
| `baseline` | nothing |
| `generic` | one short paragraph of ordinary copy-editing advice |
| `skill` | the full `SKILL.md` |

`skill_vs_generic` is the number worth quoting. `skill_vs_baseline` is the
flattering one.

## Why it revises drafts instead of generating from scratch

The first version of this harness asked a clean-context model to write, then
compared it against the same model with the skill. It measured almost nothing,
for a reason worth recording:

**Modern models do not produce much slop unprompted, and this harness cannot
reach a clean-context model anyway.** The eval shells out to the Claude Code
CLI, which supplies a system prompt of its own that already pushes toward
concise, concrete prose. `--system-prompt` does not fully displace it: asked
who it is under an overridden prompt, the model still answers "Claude Code".
Both arms inherit that, so the generation baseline was never clean, and it
scored 1-2 out of 24 (the scorer had twelve categories at the time) before
the skill touched it. There was no headroom to measure.

Revising a fixed draft removes that problem. The input is controlled and
identical for every arm, so the comparison is about what each system prompt
removes rather than about what the model would have written unprompted. It also
matches the skill's own Revision Workflow, which is its main use.

## The drafts

`evals/drafts/*.md` is a frozen corpus, committed so every run is comparable.
`make_drafts.py` produced the original eight of these by asking for the
polished content-marketing register that generic LLM prose falls into, then
resampling until the draft scored at least 10 points - about 42% of the max
at the time, when the scorer had twelve categories (24 points); the same
absolute floor is about 31% of today's 32-point max, so don't read "10" as a
bar that got easier to clear, the scorer just grew around it. Two genres are
missing because they never got there in four attempts: a LinkedIn post and a
laptop review both stayed low even under a slop-inducing prompt. That is a
result, not a gap - some genres resist the register.

Two drafts - `founder-retrospective` and `product-philosophy` - were added
later specifically to give the four StoryScope-derived categories (13-16,
see below) a fair shot: personal-narrative and origin-story registers are
where that paper's findings are most likely to show up in prose, and the
original eight prompts (mostly explainer, marketing, and technical registers)
produced almost no hits on those four categories. See "What the new
categories actually measured" below for how that turned out.

The drafts are a **stimulus**, not evidence that any model writes this way on
its own. They were explicitly asked for.

## Running it

```sh
python evals/make_drafts.py            # only to rebuild the frozen corpus
python evals/run_eval.py --repeats 3   # the eval itself
python -m tools.render_chart           # refresh the README charts
```

`run_eval.py --gate-delta N` exits non-zero unless the skill beats the generic
arm by N points, which is what the scheduled workflow uses to catch drift when
the underlying model changes.

## What the new categories actually measured

Categories 13-16 (metaphor saturation, missing real-world anchors,
over-unified argument, unrelieved earnestness) come from StoryScope
(arXiv:2604.03136) - see `tools/patterns.py`'s module docstring and each
category's "Evidence" line in `SKILL.md` for the paper findings behind it,
independently re-derived from the paper's own released feature data (its PDF
was unreachable from this environment) before being written down anywhere.
`test_detectors.py` exercises each one with a positive and a negative case,
and the hand-written `tests/fixtures/slop/*.md` fixtures were extended to
trip all four - that proves the regex mechanics work on text built to
contain the pattern. It does not prove they reliably find the pattern in text
nobody built for the purpose, which is a different and harder claim; see
"How narrow, concretely" below before trusting these four rows on any other
corpus.

On this eval corpus, they mostly did not fire. Mean per-category score across
all 90 revisions:

| category | draft | baseline | generic | skill |
| --- | ---: | ---: | ---: | ---: |
| Metaphor saturation | 0.00 | 0.00 | 0.00 | 0.00 |
| Missing real-world anchors | 0.00 | 0.00 | 0.00 | 0.00 |
| Over-unified argument | 0.10 | 0.00 | 0.00 | 0.00 |
| Unrelieved earnestness | 0.10 | 0.10 | 0.00 | 0.10 |

That is close to nothing to measure, and it would be dishonest to imply
otherwise.

**The skill still got measurably better anyway, but not by as much as the
headline number suggests once the corpus is held fixed.** The eval grew from
eight drafts to ten *while* the skill was being extended, so the 2.96 → 4.00
move quoted in the main README mixes two changes. Splitting it apart:

| slice | draft | baseline | generic | skill | skill vs generic |
| --- | ---: | ---: | ---: | ---: | ---: |
| all 10 drafts | 11.60 | 9.43 | 9.10 | 5.10 | +4.00 |
| original 8 drafts only | 11.62 | 10.00 | 9.71 | 4.54 | **+5.17** |
| the 2 new drafts only | 11.50 | 7.17 | 6.67 | 7.33 | **-0.66** |

The `baseline`/`generic` means on the original 8 are bit-for-bit identical to
the prior twelve-category run (they are the same reused raw text, rescored),
so the like-for-like comparison is 2.96 → 5.17 - a bigger move than the
headline 4.00, not a smaller one, attributable entirely to the strengthened
guidance on *existing* categories (the StoryScope citations added to
categories 2 and 10, the new "loose, digressive sentences" counterpattern,
the corrected "variable sentence length" advice). Categories 13-16 did not
drive it: on the original 8 drafts they scored 0.00 in every column. (A
"where the old X did A, the new X does B" pattern was briefly added to
`formulaic_contrast` this session, then removed after review found it fired
just as readily on a plain factual comparison as on the rhetorical version -
see `tools/patterns.py`'s comment there. It fired at most twice, real but
negligible, before removal, so its absence changes nothing above.)

**The 2-new-draft slice is a live demonstration of exactly how noisy a small
subset of this eval is - don't trust it, that's the point.** The `skill` arm
was regenerated twice during this work (once mid-session, once after a
review pass changed several patterns and some `SKILL.md` wording). The two
runs gave `skill_vs_generic` on those same two drafts as **+0.83** and then
**-0.66** - a sign flip, from six revisions each time. Nothing about the
skill or the drafts changed between those two runs in a way that should
plausibly reverse the result; this is sampling noise on n=6, exactly what
limitation 5 below already warns about, now with a concrete example instead
of an abstract caveat. Treat both numbers, and any future rerun of this
slice, as noise until n is much larger. The 10-draft headline (+4.00) and the
original-8 slice (+5.17) are far more stable across the same two runs (they
moved by 0.16 and 0.17 respectively) because they average over far more
revisions.

**Both drafts added specifically to test categories 13-16 tell a real,
draft-level story that the noisy revision numbers above obscure.** Both
(`founder-retrospective`, `product-philosophy`) were chosen because their
genre - personal narrative, origin story - is where the paper's phenomena
concentrate. It partly worked at the draft stage: the frozen
`founder-retrospective.md` draft scores 1 (not 2) on both
`over_unified_argument` (2 lexical hits, under the category's floor-of-2
scoring rule) and `unrelieved_earnestness` (3 hits) - these are stable
facts about a fixed, committed file, not resampled on every eval run. But
`product-philosophy.md`, added for the identical reason, scores **0 on all
four** despite containing a real "not the end of a journey, it was the
beginning of a new one" closing move that reads as exactly the pattern
categories 13 and 15 are meant to catch - the regexes just do not cover that
phrasing. And every arm's *revision* of `founder-retrospective` - including
`baseline`, which gets no system prompt at all - washed its two hits out to
near zero, which rules out "the skill specifically suppresses this" as an
explanation (baseline has no skill guidance and still lost the signal).

### How narrow, concretely

A review pass wrote 18 adversarial inputs by hand, not copied from
`tests/test_detectors.py`, to see how these four regexes (plus one new
`formulaic_contrast` pattern added the same session) hold up outside their
calibration sentences. Three false positives it found were fixed on the
spot - each is now `tools/patterns.py`'s "NOT included, on purpose" comment
next to the category it used to belong to:

- `"A raccoon is a kind of procyonid, and a coati is a kind of procyonid too."` used to score `metaphor_saturation` (a plain taxonomic statement, not a reached-for figure) - the bare `is a kind of` / `think of X as` patterns responsible were removed.
- `"Re-seating the connector required great patience because the clips are brittle."` used to score `unrelieved_earnestness` (a flat factual predicate) - the `required (great) patience/perseverance/...` pattern was removed; it had also contributed zero real hits anywhere in the eval corpus.
- `"Where the old boiler burned oil, the new boiler burns gas."` used to score `formulaic_contrast` on a plain factual comparison - the "where the old X did A, the new X does B" pattern was removed (see the note above; it had fired twice, real but negligible, before removal).

One more was narrowed rather than removed: `"Under the NDA I can only say
that a major provider had an outage that week."` used to score
`missing_anchors` **2/2** from a single sentence, because two of the
category's patterns overlapped and both matched it; the redundant pattern
was deleted, so the same sentence now correctly scores 1. Whether it should
score anything at all is a closer call left open - "a major provider" is a
genuinely vague placeholder, even in an otherwise legitimate confidentiality
disclaimer.

False negatives remain, by design as regexes rather than semantic judgments,
and none of the fixes above touched them - these are paraphrases of
`SKILL.md`'s own worked examples that trigger nothing:

- `"If the first release was **like** a sketch, this one is **like** the underpainting."` → 0 (swapping `was a` for `was like a` defeats the metaphor pattern entirely)
- A fully sustained four-sentence tide metaphor, no single clause matching the narrow triggers → 0
- `"A **famous podcast** covered this, and a **widely-read essay** on management convinced the team..."` → `missing_anchors` stays at 0 (the pattern only knows a fixed list of nouns: "streaming service", "provider", "platform", and a handful of others)
- `"Every one of these setbacks leads back to a single lesson. Seen as a whole, the picture is clear."` → `over_unified_argument` 0 (a clean paraphrase of SKILL.md's own category-15 example, worded just differently enough)
- `"This has been a demanding and deeply fulfilling road. Every setback turned into a chance to learn, and the outcome speaks for itself."` → `unrelieved_earnestness` 0 (same shape as SKILL.md's own example, different vocabulary throughout)

The honest conclusion: categories 13-16 are good, specific *writing guidance*
- the SKILL.md prose and worked examples for all four hold up - but their
regex proxies in `tools/slopscore.py` are calibration-sentence matchers
today, not validated detectors of the underlying pattern in general text.
This review pass raised their precision (three false positives fixed, a
fourth narrowed) without touching their recall, which was never the claim -
"narrow" is still the right word for what's left, and the false negatives
above are the concrete evidence for why. Treat the scores in this eval, and
any future eval, as a lower bound on how often these patterns actually
occur, not a measurement of it. Widening recall past single source
sentences - ideally by testing against a corpus nobody involved in writing
the patterns has read - is the obvious next step.

## Limitations

Take these seriously before quoting a number.

1. **The harness is not a clean model.** Everything runs through the Claude Code
   CLI and inherits its system prompt. The arms are compared against each other
   under identical conditions, which is valid, but none of them represents a raw
   model. Re-running this against the API directly would be a better experiment
   and is the obvious next step.
2. **The scorer is a proxy.** It counts sixteen categories of surface pattern. It
   cannot see whether a sentence is true, whether a cut lost something, or
   whether the result is pleasant to read. A text can score 0 and still be dull.
   It is a writing heuristic, not a judge and not an AI detector. Four of the
   sixteen categories are themselves proxies for whole-document judgments from
   a paper about fiction, not blog posts - see the section above.
3. **It only reads English**, and only the patterns in `tools/patterns.py`.
   Slop it has no pattern for is slop it will not report.
4. **The scorer cannot check factual preservation.** Both arms are told not to
   invent facts; nothing verifies that they obeyed. Revisions are saved under
   `evals/results/raw/` so this can be checked by hand.
5. **Small n.** Ten drafts, three arms, three samples each. Enough to see a
   large effect, not enough to resolve a small one. Model sampling varies
   between runs, so treat one-point differences as noise - and see "What the
   new categories actually measured" above for a concrete case where a
   6-revision subset flipped sign (+0.83 to -0.66) between two runs of the
   identical `skill` arm, while the full 90-revision result moved by 0.16.
6. **Selection.** Drafts were kept only if the scorer already rated them sloppy,
   using the same scorer that later measures the improvement. That is
   appropriate for choosing a stimulus, but it does mean the drafts are ones
   this scorer is good at seeing.
7. **Partial regeneration.** Most of the `baseline` and `generic` arms in the
   current `evals/results/latest.json` were reused from the run that first
   validated all three arms together (documented above: drafts 11.62,
   baseline 10.00, generic 9.71, skill 6.75 on the original twelve
   categories), rather than regenerated, because neither arm's system prompt
   depends on `SKILL.md` content. Only the `skill` arm, plus baseline and
   generic for the two drafts added afterward, were generated fresh - and the
   `skill` arm specifically was regenerated a second time after a review pass
   changed both `SKILL.md` and several detector patterns, so its raw text
   reflects the version of both actually committed here. This is a
   deliberate cost-saving choice, not a shortcut that changes what the
   comparison measures: `run_eval.py --arms baseline,generic` regenerates
   both from scratch if that assumption is ever worth re-checking, and
   `evals/rescore.py` rebuilds `latest.json` from whatever raw text already
   exists (no new model calls) whenever only the scorer changes - it also
   warns if the raw `skill` text on disk was generated against a different
   `SKILL.md` than the one it's about to score, by comparing against the
   `meta.skill_sha256` recorded in the previous `latest.json`.
