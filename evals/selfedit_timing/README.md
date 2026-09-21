# Self-edit timing: does the Generation Workflow's audit step actually work?

**Status: fix applied to `SKILL.md` (Generation Workflow, step 5), through
three attempts - the first two were each found insufficient (once by
re-validating against live generations, once by an independent adversarial
review) before the third shipped.** See "The fix" below for what changed
and why, and "Independent adversarial review" for what that review found
and how each finding was resolved.

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
skill and an equivalent instruction, cuts the score by roughly half
(-50% to -60%; see the exact reductions in the table above). The third
topic, `founder-retrospective` on Sonnet, is weaker and noisier: `twopass`
beat `midtask` on run 1 but not run 2, and the reduction it does show is
smaller than the other two topics' (pooled: 9.33 -> 6.67, about -29%, not
"roughly half"). Counting distinct (topic, model) cells rather than
individual runs - `product-philosophy`/sonnet, `product-philosophy`/opus,
`oped-remote-work`/sonnet, and `founder-retrospective`/sonnet pooled -
`twopass` wins all 4 of 4; counting every individual run separately
(`founder-retrospective` ran twice), it wins 4 of 5. "Five of six" was an
earlier miscount here that double-counted the pooled founder-retrospective
row alongside its own two constituent runs; corrected above.

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
- **`midtask` and `twopass` are not identical except for timing.** The
  `midtask` prompt asks the model to write in the slop-inducing
  `SLOP_REGISTER` *and* follow the skill's system prompt in the same
  breath - a direct conflict `twopass`'s call B never faces, since call B
  only ever sees `REVISE_INSTRUCTION`, with no register instruction at
  all. This matters in practice, not just in principle: the one
  `midtask` run where `twopass` did *not* win
  (`sonnet`/`founder-retrospective` rep 1, scored 1/32) is a case where
  the model appears to have simply ignored the register and written
  direct, specific prose from the first sentence - the same failure mode
  documented below for Haiku, just less frequent on Sonnet. A `midtask`
  score is therefore partly a measure of which instruction the model
  gave precedence to, not purely a measure of self-audit timing. This
  doesn't change the overall finding - the topics/models where the
  register *was* followed still show the same large gap - but it means
  individual low `midtask` scores should be read with this in mind
  before being cited as evidence of successful self-editing.

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
   essay - or with an outright refusal, e.g. *"I don't see the actual
   draft text to revise - only a description of one. Could you paste the
   400-word opinion piece itself?"* Of the 9 Haiku `twopass` calls, 6
   produced a call-B (revised) output under 150 words for what should
   have been a ~400-word piece; inspecting those 6 directly, 2 are
   meta-descriptions and 4 are explicit refusals of the second kind. The
   6-under-150-words figure is measured on the *revision*'s word count
   (the field `run.py` recorded at the time), not on the raw call-A
   draft's - `run.py` did not persist call A's own text in this run, so
   the raw drafts themselves could only be inspected indirectly, through
   what call B said about them. This has been fixed: `run.py` now saves
   `raw_draft_text` for every `twopass` call and flags any raw draft
   under 150 words directly (`raw_draft_suspicious`), rather than relying
   on the revision's length as a proxy. Runs before this fix
   (`v1_no_register_null.json` through `post_fix_midtask.json`) do not
   have `raw_draft_text`; only the revised `text` field and the
   `raw_draft_total` score are available for those.
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
not a suppression of an inconvenient result - `results/sonnet_haiku_sweep_3topics.json`
stays in the repo for anyone who wants to look at it themselves. For the
two meta-description cases, what's inspectable there is call B's revision
of the meta-description (which mostly just restates it), not call A's
original output verbatim - see the note above on `raw_draft_text` not
existing yet when this file was generated.

## The fix

Two candidate mechanisms for fixing the Generation Workflow's step 5 were
on the table: rely on extended thinking (a private draft-and-revise phase
before any visible output, not subject to the same-stream constraint this
tested), or replace the single-completion audit with an explicit
separate-pass pattern matching the Revision Workflow. Both were tried, and
each of the first two attempts at wording them into `SKILL.md` was found
insufficient in turn - the first by re-validating it against live
generations, the second by an independent adversarial review - before a
third attempt shipped. All three are documented below, including what
was wrong with the first two.

### Attempt 1: private draft first (insufficient)

The first rewrite of step 5 offered "private draft first" and "separate
pass" as two co-equal ways to audit reliably, leaning on whichever
reasoning phase the model has before its visible output. Re-running
`midtask` against this version (`results/post_fix_midtask.json`, same
topics/models, n=3 per cell) showed why that framing was wrong to present
as sufficient on its own:

This run actually produced 4 cells (2 topics x 2 models, n=3 each); the
table originally published here showed only 3 and silently dropped
`founder-retrospective`/opus, which has no pre-fix `midtask` or `twopass`
number to compare against (opus was never tested on that topic before the
fix). It's included below rather than left out, with that caveat stated
instead of implied:

| topic | model | pre-fix midtask | post-fix midtask (attempt 1) | twopass (unchanged) | raw baseline |
|---|---|---:|---:|---:|---:|
| product-philosophy | sonnet | 9.33 | 6.67 | 4.33 | 9.00 |
| product-philosophy | opus | 8.00 | 7.67 | 3.00 | 6.00 |
| founder-retrospective | sonnet (pooled) | 7.67 | 8.33 | 6.67 | 9.33 |
| founder-retrospective | opus | *(no prior run)* | 9.00 | *(no prior run)* | *(no prior run)* |

Sonnet on `product-philosophy` improved partially (9.33 -> 6.67) and
finally dropped below the raw baseline, which the pre-fix version never
did. Opus barely moved (8.00 -> 7.67) and stayed *above* its own raw
baseline (6.00) - the private-draft instruction made essentially no
difference for that model on that topic, the same pattern the original
finding showed. `founder-retrospective` on Sonnet, already the noisiest
topic, moved the wrong way. `founder-retrospective`/opus has nothing to
compare against, but at 9.00 it's the highest (worst) score in this whole
table - not evidence the fix worked there either. None of the four came
close to `twopass`.

**Conclusion: telling a model to draft privately and self-audit before
answering helps a little, inconsistently, and not on every model. It is
not a fix by itself.**

### Attempt 2: separate pass as the primary instruction (superseded)

Step 5 was rewritten again to state the separate-pass pattern as the
primary instruction - finish the draft, then apply the Revision Workflow
to it as its own later step, ideally a genuinely separate turn or call -
with the private-draft approach demoted to "worth doing in addition, do
not rely on it alone," and the attempt-1 numbers cited directly in the
skill text as the reason why.

This rewrite was not re-validated with a further live-generation round
beyond attempt 1's data, on the reasoning that it didn't introduce a new
mechanism - it just stated the already-measured `twopass` pattern as the
primary path. That reasoning was itself checked by an independent
adversarial review (see below) and found to prove less than it claimed:
the number it leaned on, "cuts the score roughly in half on every model
and topic tested cleanly," is contradicted by this investigation's own
`founder-retrospective` data (pooled: -29%, not -50%; see "Reading this"
above, corrected). More importantly, the review pointed out a design
problem attempt 2's wording didn't address: **"prefer a separate turn or
call" cannot be executed by an assistant answering an ordinary single-turn
request** - which is most of how this skill gets used. Nothing in the
skill grants a second turn, a fresh context, or a subagent on demand. For
that case, attempt 2's text quietly degrades to "finish the draft, then
apply the Revision Workflow to it" *inside the same completion* - which is
the same-completion self-audit this whole investigation exists to correct,
just described at length instead of in one sentence, while demoting the
one mechanism that actually is available in a single turn (private
reasoning) on the strength of a partial result.

### Attempt 3: ranked fallback, single-turn case made executable (what shipped)

Step 5 was rewritten a third time as an explicit, ranked list rather than
a "prefer X, else Y" pair:

1. A genuinely separate turn or call, when available - the version
   measured to actually cut the score roughly in half on most models and
   topics tested (not all; see the corrected claim above).
2. A private reasoning phase before the visible answer, when (1) isn't
   available - weaker, per attempt 1's data, but still worth doing.
3. When neither is available - the common single-turn case - auditing as
   a distinct step within the same completion, explicitly labeled as the
   floor rather than the goal, so the instruction remains something an
   assistant can actually follow rather than silently defaulting to it
   while believing it did (1).

This is the version currently in `SKILL.md`. It was not validated with a
further live-generation round either, for the same reason attempt 2's
skip was defensible in part but incomplete: option (3)'s mechanism is not
new - it's a same-completion audit, the exact thing measured (weakly
effective at best) as the *original*, pre-fix step 5 and, in a milder
form, as attempt 1. What's new in attempt 3 is the ranking and the
explicit floor label, which change what an assistant is told to do, not
the underlying mechanics of any option once chosen - so no option in this
version is untested, but the ranking's effect on which option an assistant
actually reaches for in practice is, like attempt 2's compliance question
below, unmeasured.

## What this does not decide

Whether an assistant reliably *follows* the separate-pass instruction in
ordinary use (as opposed to a fresh `claude -p` process where "two passes"
is unambiguous) is not measured here - the closest evidence is that this
was already how `evals/run_eval.py`'s `skill` arm has always worked, and
those numbers (`evals/README.md`) are the ones actually published as the
skill's headline results. Whether extended thinking, where available,
narrows the gap between attempt 1 and `twopass` further than this test
showed also remains untested - `claude -p` was not run with reasoning
tokens made visible or controlled here, so "private draft" in attempt 1
may not have reliably engaged real reasoning at all versus just being one
more sentence in a long system prompt. And attempt 3's ranking is, as
noted above, a change to instruction wording rather than to any tested
mechanism - whether it actually gets assistants to reach for option (1) or
(2) more often than attempt 2's wording did is not something this
investigation measured.

## Independent adversarial review

Before this branch was considered finished, attempt 2 (then the shipped
version) and everything above it - the harness, every committed result
file, the writeup itself - was reviewed by a separate, clean-session
subagent (Opus, high reasoning effort) with no access to this session's
reasoning, instructed to independently recompute every number from the
raw JSON rather than trust the prose, read a sample of the raw Haiku text
itself, run the test suite and linter itself, and actively look for
overclaims and bugs rather than confirm what was written.

**What the review got right, verified independently before accepting it:**
every number in the main results table recomputes exactly from the raw
JSON to four decimal places; the harness's prompt-provenance claims
(topics matching `evals/prompts.json` verbatim, the revision instruction
matching `evals/run_eval.py`'s, the slop register matching
`evals/make_drafts.py`'s) are byte-exact; the Haiku exclusion is
substantively justified, not an excuse (confirmed by reading the raw text
myself - see the Haiku section above); git hygiene (branch, attribution
trailers, fully pushed) was clean.

**Must-fix findings, and what was done about each:**

| # | finding | resolution |
|---|---|---|
| 1 | `ruff format --check .` failed on the new `run.py` (CI would have gone red); the commit claimed 146 tests, actual count is 145 | ran `ruff format`, verified both `ruff check` and `ruff format --check` pass; corrected the test count in this document (the wrong count was never in a tracked file, only a commit message, which is not rewritten) |
| 2 | `SKILL.md` claimed the separate-pass fix works "on every model and topic tested cleanly" - false for `founder-retrospective` (-29% pooled, not -50%) | reworded in both `SKILL.md` and here to state the actual range and name the exception |
| 3 | the rewrite removed the only pointer from any workflow to the `## AI-Likeness Audit` section - nothing in `SKILL.md` instructed running it anymore | added back explicitly as Revision Workflow's Pass G |
| 4 | the Final Quality Test section, edited one commit before step 5's final rewrite, still presented private reasoning and a separate pass as co-equal ("X or Y"), contradicting step 5's ranking | reworded to point at step 5's ranking rather than restate an independent, now-inconsistent version of it |
| 5 | the attempt-1 table silently dropped the `founder-retrospective`/opus cell - the highest (worst) score in the file | added it back with the reason it has no prior-run comparator, rather than omitted without comment |
| 6 | "three of those were explicit refusals" undercounted - it's four refusals and two meta-descriptions, not three and three | recounted directly from the raw text (see above) and corrected |
| 7 | "twopass beat midtask in five of six" double-counted the pooled `founder-retrospective` row alongside its own two constituent runs | reworded to give both honest countings - 4 of 4 distinct (topic, model) cells, 4 of 5 individual runs - without a total that mixes the two |
| 8 | undisclosed confound: `midtask`'s prompt asks the model to follow a slop-inducing register *and* the skill's system prompt at once, a conflict `twopass`'s call B never faces; the one `midtask` run where `twopass` didn't win is a case of the model dropping the register entirely | disclosed as a new Caveats entry, with the specific run named as the mechanism |
| 9 | "6 of 9 Haiku twopass calls under 150 words" was measured on call B's (revised) word count, not call A's (raw draft's) - and call A's own text was never persisted, so the "raw data stays in results/" claim was only true of call B's restatement of it | corrected the attribution; added a `raw_draft_text` field to `run.py` so future runs persist call A directly, and noted which existing result files predate that field |
| 10 | no `skill_sha256` (or any metadata) recorded per run, unlike `evals/run_eval.py`/`evals/rescore.py`'s established convention - the attempt-1-vs-attempt-2 "same test, different `SKILL.md`" comparison had no way to be verified from the files themselves | added a `meta` block (`skill_sha256`, `generated_at`, topics/models/conditions/repeats) to `run.py`'s output going forward; existing result files predate this and cannot be retrofitted, which is now stated rather than left implicit |
| 11 | the fix's own primary instruction ("prefer a separate turn or call") is not executable by an assistant answering an ordinary single-turn request, which is most of how this skill is used - in that case it silently degrades to the same-completion audit the investigation exists to correct, while the one option usable in a single turn was demoted on partial data | rewrote step 5 a third time as an explicit ranked list with a labeled floor for the single-turn case (attempt 3, above), instead of a "prefer X, else Y" pair that assumed X was generally reachable |

**Worth-considering findings, and what was done:** `--conditions` (and, by
the same logic, a typo in `--models`) was unvalidated, so a misspelled
condition would silently run `twopass` twice under the `twopass` label
instead of erroring - fixed, `--conditions` now validates against a fixed
set. The summary could crash with a `TypeError` if a call returned exit 0
with empty output (`error=None`, `total=None`) - fixed, the summary now
filters on both. A regression test pinning the old flawed phrasing and the
Audit cross-reference (in the idiom of `tests/test_skill_contract.py`) was
recommended and added - see `tests/test_skill_contract.py`. The
`raw_draft_suspicious` flag not being surfaced per-cell in the printed
summary, and the Opus "worse than raw baseline" headline resting on n=3
unpaired samples, were both judged reasonable as-is: the former is
visible in the JSON and in the run's stderr warning count, and the latter
already carries the document's general small-N caveat - both are noted
here rather than silently accepted. Tightening step 5's prose to reduce
its length relative to Generation Workflow's other steps was addressed
in the attempt-3 rewrite (a ranked list reads shorter than the prose
attempt 2 used for the same content), though it remains the longest
single step in that workflow, which is a reasonable proportionality
trade-off given it is also the step with a wrong version already shipped
twice.
