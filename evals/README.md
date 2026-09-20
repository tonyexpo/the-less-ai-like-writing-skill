# Eval

What this measures, how, and what it cannot tell you.

## The question

Does `SKILL.md` remove more generic-LLM prose patterns than ordinary writing
advice does?

Not "does the skill beat an empty prompt". A 12 KB style instruction beating no
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
scored 1-2/24 before the skill touched it. There was no headroom to measure.

Revising a fixed draft removes that problem. The input is controlled and
identical for every arm, so the comparison is about what each system prompt
removes rather than about what the model would have written unprompted. It also
matches the skill's own Revision Workflow, which is its main use.

## The drafts

`evals/drafts/*.md` is a frozen corpus, committed so every run is comparable.
`make_drafts.py` produced it by asking for the polished content-marketing
register that generic LLM prose falls into, then resampling until the draft
scored at least 10/32. Two genres are missing because they never got there in
four attempts: a LinkedIn post and a laptop review both stayed low even
under a slop-inducing prompt. That is a result, not a gap - some genres resist
the register.

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
(arXiv:2604.03136) - see `tools/patterns.py`'s module docstring for the paper
findings behind each one, verified against the paper's own released data
before being written down anywhere. They are real detectors: `test_detectors.py`
exercises each one with a positive and a negative case, and the hand-written
`tests/fixtures/slop/*.md` fixtures were extended to trip all four.

On this eval corpus, they mostly did not fire. Mean per-category score across
all 90 revisions:

| category | draft | baseline | generic | skill |
| --- | ---: | ---: | ---: | ---: |
| Metaphor saturation | 0.00 | 0.00 | 0.00 | 0.00 |
| Missing real-world anchors | 0.00 | 0.00 | 0.00 | 0.00 |
| Over-unified argument | 0.10 | 0.00 | 0.00 | 0.00 |
| Unrelieved earnestness | 0.10 | 0.10 | 0.00 | 0.00 |

That is close to nothing to measure, and it would be dishonest to imply
otherwise. Two things are worth separating here:

- **The skill still got measurably better anyway** - `skill_vs_generic` moved
  from 2.96 (twelve categories) to 4.16 (sixteen categories) on the same
  three original-arm structure. That improvement is attributable to the
  strengthened existing-category guidance (the StoryScope citations added to
  categories 2 and 9, the new "loose, digressive sentences" counterpattern,
  the corrected "variable sentence length" advice) and to one new lexical
  pattern added to an *existing* category (formulaic_contrast's "where the
  old X did A, the new X does B" reversal), not to categories 13-16 firing.
- **Categories 13-16 were given a real but limited chance, and one result is
  worth reading carefully.** Two of the ten drafts (`founder-retrospective`,
  `product-philosophy`) were chosen specifically because their genre -
  personal narrative, origin story - is where the paper's phenomena
  concentrate, and it worked at the draft stage: the frozen
  `founder-retrospective.md` draft itself trips `over_unified_argument`
  (2 hits) and `unrelieved_earnestness` (3 hits). But every arm's *revision*
  of that same draft - including `baseline`, which gets no system prompt at
  all - washed those hits out to near zero. The most likely explanation is
  the revision instruction itself ("revise so it reads better"), which
  seems to push the model toward tightening and de-dramatizing regardless of
  which system prompt it is given, before the skill-specific guidance gets a
  chance to matter. That is a property of this eval's revision-based design,
  not evidence against the categories: `test_detectors.py` and the
  hand-written fixtures confirm the detectors themselves work correctly on
  text that does exhibit the pattern.

The honest conclusion: categories 13-16 are validated at the unit-test level
(they fire on real, unedited model output when the genre calls for it) but
**not yet validated at the eval level** on this corpus. A dedicated eval
corpus of personal-narrative prompts generated *without* the corporate-register
wrapper would be a better instrument and is the obvious next step for anyone
extending this further.

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
   between runs, so treat one-point differences as noise.
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
   generic for the two drafts added afterward, were generated fresh. This is
   a deliberate cost-saving choice, not a shortcut that changes what the
   comparison measures: `run_eval.py --arms baseline,generic` regenerates
   both from scratch if that assumption is ever worth re-checking.
