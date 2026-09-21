# Self-edit timing: does the Generation Workflow's audit step actually work?

**Status: investigation only. No fix has been applied to `SKILL.md`.** This
documents a reproduced finding and stops there, on purpose, pending a
decision on what to change.

## The question

Two people reported the same thing, independently, on a public thread about
this skill:

- A model cannot reliably self-edit "mid-task." Editing works much better as
  a separate pass over already-finished text than as a check applied inside
  the same completion that produced the draft - an independent reviewer
  (human or subagent) does better than self-review in the moment.
- By analogy to speech: once words are out, in the same breath, they cannot
  be unsaid, only added to. A model streaming a response cannot rewrite a
  sentence it already emitted in that same stream - it can only write more
  after it.

`SKILL.md`'s **Generation Workflow** asks for exactly the case this
describes: draft the piece (steps 1-4), then, in the *same response*, "Run
the AI-Likeness Audit below" (step 5). The skill's own eval
(`evals/run_eval.py`) never tests this path - every `skill`-arm call there
revises an *already-frozen* draft in a fresh process, which is
architecturally the **Revision Workflow**, not the Generation Workflow's
self-audit step. The distinction that matters is not "who wrote the
original text" but whether it is fully present in context *before*
generation of the fix begins, or whether the audit is expected to happen
inside the same continuous stream that is still producing the draft.

## Test design

Two conditions, same topic, same `SKILL.md`, same `tools/slopscore.py`
scorer (see `run.py`):

| condition | what happens |
|---|---|
| `midtask` | One `claude -p` call. System prompt = full `SKILL.md`. User prompt asks for the piece, in a slop-inducing register, and explicitly says to apply the Generation Workflow's self-audit step within that same response. |
| `twopass` | Two separate `claude -p` calls, each a fresh process. Call A: no skill, same slop-inducing prompt (an unedited baseline). Call B: fresh process, system prompt = full `SKILL.md`, the standard revision instruction + call A's draft. This is exactly what `evals/run_eval.py`'s `skill` arm already does. |

Topics reuse three already-calibrated genres from `evals/prompts.json`
(`founder-retrospective`, `product-philosophy`, `oped-remote-work`), each
appended with the same slop-inducing register `evals/make_drafts.py` uses to
calibrate the repo's frozen drafts. That register turned out to matter: the
first run of this test used a plain topic prompt with no register, and both
conditions sat at 0-2/32 with nothing to observe (`results/v1_no_register_null.json`)
- the same confound `evals/README.md` already documents for clean-context
generation through the Claude Code CLI. Every result below uses the
register.

## Results

Total slopscore /32 (lower = fewer AI-like patterns). n=3 per cell unless
noted. `raw` is the unedited baseline from `twopass`'s call A - the same
prompt, no skill.

| topic | model | raw | midtask | twopass |
|---|---|---:|---:|---:|
| product-philosophy | sonnet | 9.00 | **9.33** | **4.33** |
| oped-remote-work | sonnet | 11.67 | **9.33** | **4.67** |
| founder-retrospective | sonnet (run 1) | 9.00 | 9.33 | 5.67 |
| founder-retrospective | sonnet (run 2) | 9.67 | 6.00 | 7.67 |
| founder-retrospective | sonnet (pooled, n=6) | 9.33 | 7.67 | 6.67 |
| product-philosophy | opus | 6.00 | **8.00** | **3.00** |

Raw JSON, including every generated text, is in `results/`:
`v2_founder_retrospective_sonnet.json`, `sonnet_haiku_sweep_3topics.json`,
`opus_product_philosophy.json` (and the null result, `v1_no_register_null.json`).

### Reading this

On two of three topics (`product-philosophy`, `oped-remote-work`), and on
both models tested cleanly (Sonnet and Opus), the pattern is the same and
the gap is large: `midtask` barely moves the score from the unedited
baseline - on Opus it made the text *worse* than not applying the skill at
all (8.00 vs a raw baseline of 6.00) - while `twopass`, using the identical
skill and an equivalent instruction, cuts the score roughly in half. Across
all six clean `midtask` vs `twopass` cells (3 topics x sonnet, plus opus),
`twopass` beat `midtask` in five of six; only `founder-retrospective`
run 2 went the other way, and pooling both founder-retrospective runs
(n=6 per condition) narrows that topic's gap to within noise range (7.67 vs
6.67) rather than reversing the other topics' finding.

This is consistent with both reports: self-auditing inside the same
completion that produced the draft does not reliably do what
`SKILL.md`'s Generation Workflow step 5 asks of it; running the same audit
as a separate pass over finished text - which is what the Revision
Workflow, and the existing `skill` eval arm, actually test - does.

### Caveats

- **Small N.** n=3 per cell, one repeated to n=6 for one topic. This is a
  reproducibility check, not a statistically powered result - treat the
  effect sizes as indicative, not precise. `evals/README.md` already
  documents comparable score volatility at this sample size in the main
  eval (+0.83 -> -0.66 on the same 2-draft subset across two regenerations).
- **Two topics only were tested cleanly** on more than one model
  (`product-philosophy` on Sonnet and Opus). The third
  (`founder-retrospective`) is the noisiest result and the one place the
  direction flipped between runs.
- **The scorer is a regex-pattern proxy**, same limits documented
  throughout `evals/README.md` - it counts surface patterns, not writing
  quality.
- **This was run through the Claude Code CLI** (`claude -p`), which
  contributes its own system prompt to every call, same limitation
  `evals/run_eval.py`'s docstring already names for the main eval.

## Haiku: excluded, not just noisy

Haiku was tested across the same three topics and both conditions
(`results/sonnet_haiku_sweep_3topics.json`) and is **not included in the
findings above** - not because the numbers were unfavorable, but because a
majority of them do not measure what they were supposed to.

Two distinct failure modes showed up only with Haiku:

1. **`twopass` call A (no skill) sometimes described the piece instead of
   writing it.** Given the slop-register instruction, Haiku would
   occasionally respond with something like *"A 400-word founder's
   retrospective with three section headings. Opens on economic
   pressure..."* - a meta-description of the essay's structure, not the
   essay. 6 of 9 Haiku `twopass` calls across the three topics produced
   fewer than 150 words for what should have been a ~400-word piece; three
   of those were explicit refusals asking for the actual draft to be
   pasted in. `run.py` now flags any raw draft under 150 words
   (`raw_draft_suspicious`) so this does not silently corrupt a future run's
   numbers.
2. **`midtask` sometimes skipped the slop register entirely.** With the
   skill loaded as system prompt, Haiku would write clean, direct prose
   from the first sentence rather than following the "write it in the
   corporate-marketing register" framing in the user prompt - which drove
   its `midtask` scores to near zero (0.00-0.67 across the three topics),
   but for a different reason than successful self-editing: there was
   nothing sloppy generated in the first place for the self-audit step to
   have to catch.

Both failure modes are about Haiku's handling of this specific compound
instruction (a topic plus a register plus, in one condition, a skill
system prompt), not about the self-edit-timing question this investigation
is about. Keeping Haiku out of the comparison table above is deliberate,
not a suppression of an inconvenient result - the raw data stays in
`results/sonnet_haiku_sweep_3topics.json` for anyone who wants to look at
it, including the meta-description outputs themselves.

## What this does not decide

This investigation confirms the timing problem is real and reproducible
under the conditions tested. It does not, by itself, say what to change:
whether the Generation Workflow's step 5 should be rewritten to rely on
extended thinking (a private draft-and-revise phase before any visible
output, which would not be subject to the same-stream constraint this
tested), whether it should be replaced with an explicit two-call pattern
matching the Revision Workflow, or something else. That decision, and any
change to `SKILL.md`, is left for later.
