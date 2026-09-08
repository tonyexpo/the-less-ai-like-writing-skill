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
scored at least 10/24. Two genres are missing because they never got there in
four attempts: a LinkedIn post and a laptop review both stayed around 9/24 even
under a slop-inducing prompt. That is a result, not a gap - some genres resist
the register.

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

## Limitations

Take these seriously before quoting a number.

1. **The harness is not a clean model.** Everything runs through the Claude Code
   CLI and inherits its system prompt. The arms are compared against each other
   under identical conditions, which is valid, but none of them represents a raw
   model. Re-running this against the API directly would be a better experiment
   and is the obvious next step.
2. **The scorer is a proxy.** It counts twelve categories of surface pattern. It
   cannot see whether a sentence is true, whether a cut lost something, or
   whether the result is pleasant to read. A text can score 0 and still be dull.
   It is a writing heuristic, not a judge and not an AI detector.
3. **It only reads English**, and only the patterns in `tools/patterns.py`.
   Slop it has no pattern for is slop it will not report.
4. **The scorer cannot check factual preservation.** Both arms are told not to
   invent facts; nothing verifies that they obeyed. Revisions are saved under
   `evals/results/raw/` so this can be checked by hand.
5. **Small n.** Eight drafts, three arms, three samples each. Enough to see a
   large effect, not enough to resolve a small one. Model sampling varies
   between runs, so treat one-point differences as noise.
6. **Selection.** Drafts were kept only if the scorer already rated them sloppy,
   using the same scorer that later measures the improvement. That is
   appropriate for choosing a stimulus, but it does mean the drafts are ones
   this scorer is good at seeing.
