# Less AI-Like Writing Skill

[![CI](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/ci.yml)
[![Eval](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/eval.yml/badge.svg)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/eval.yml)
[![License: Apache-2.0](https://img.shields.io/github/license/tonyexpo/the-less-ai-like-writing-skill?color=blue)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/tonyexpo/the-less-ai-like-writing-skill)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/tonyexpo/the-less-ai-like-writing-skill?style=flat)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/stargazers)

A reusable writing and editing skill for prose that reads like generic LLM output: too polished, vague, repetitive, promotional, or predictable in its structure. It cuts those patterns while keeping the text clear and factually accurate, and it leaves the author's natural voice alone.

The aim is better writing. The skill does not manufacture imperfections, and it is not a trick for defeating AI detectors.

## Sources

The skill's pattern catalog is not folk wisdom. It draws on two sources, in this order:

1. [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), a community-maintained Wikipedia essay that catalogues recurring tells in AI-generated prose: em dashes used as formulaic emphasis, the compulsive rule of three, "not only X but also Y" symmetry, boosterish language, and more. The audit's original twelve categories cover much of the same ground and were written before this citation was added to the repo. Treat the essay as the closest public reference for that catalog, not as a claim about which of the two was built from the other.

2. [StoryScope (Russell et al., arXiv:2604.03136)](https://arxiv.org/abs/2604.03136), a 2026 study of ~61,600 parallel human- and LLM-written stories. It induces 304 narrative features across ten dimensions (plot, style, agents, and seven others) and finds that those features alone, with no access to the raw text, separate human from AI writing at 93.2% macro-F1. Style, which covers tone and figurative language among other things, is the single highest-separating dimension on average.

   Four of the paper's findings plausibly transfer from fiction to ordinary prose, and they became categories 13–16: metaphor saturation, missing real-world anchors, over-unified arguments, and unrelieved earnestness.

   Two findings from the paper's released data explicitly did **not** become detectors. Raw em-dash *frequency* barely separates AI from human text, and neither does sentence length; sentence fragments actually run the opposite direction from folk wisdom. The em-dash finding is a different claim from source 1's "used in a formulaic way": a construction can be a recognizable tell without occurring more often overall. That is why this project's own em-dash detector, in category 2, targets one specific construction instead of counting dashes. `tools/patterns.py` records why both were left out, so the omission does not get quietly reintroduced later.

   See [`evals/README.md`](evals/README.md) for how this project verified the paper's numbers and where its own regex proxies for these four categories still fall short.

## What it improves

The skill looks for patterns such as:

- abstract claims of importance without supporting facts;
- unnecessary interpretation after every statement;
- promotional or brochure-like language;
- forced contrasts and three-part lists;
- synonym cycling where simple repetition would be clearer;
- overly elaborate verbs, headings, introductions, and conclusions;
- vague attribution and assistant-style filler;
- sustained metaphor, missing real-world anchors, over-unified arguments, and unrelieved earnestness.

It then favors concrete details, simple accurate verbs, natural rhythm, selective explanation, and a voice suited to the author and context.

### Small example

**Generic LLM-style prose**

> This development highlights the crucial role of technology in an ever-evolving digital landscape.

**More specific prose**

> The update cuts export time from 12 minutes to about 7.

The revision does not try to sound human by adding mistakes. It replaces a generic claim with the fact that makes the change worth mentioning.

## Download and use

This repository *is* the skill: `SKILL.md` sits at the repository root, in the standard Claude Skill format (YAML frontmatter with `name` and `description`, followed by the instructions).

### Claude Code / Claude apps that support Skills

Clone (or add as a git submodule) directly into your skills folder, keeping the repository name as the skill's folder name:

```sh
git clone https://github.com/tonyexpo/the-less-ai-like-writing-skill.git .claude/skills/the-less-ai-like-writing-skill
```

Claude will pick it up automatically based on the `description` in the frontmatter.

### Claude/ChatGPT or others

[![Download SKILL.md](https://img.shields.io/badge/Download-SKILL.md-2ea44f?style=for-the-badge&logo=github)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/raw/refs/heads/main/SKILL.md)

1. Download the file above (or [`SKILL.md`](https://github.com/tonyexpo/the-less-ai-like-writing-skill/raw/refs/heads/main/SKILL.md) directly).
2. Upload it to ChatGPT, Claude, or another AI tool that accepts instruction files or project attachments.
3. Ask the tool to apply the skill when drafting or revising text.

Example requests:

> Use the attached skill to rewrite this draft. Keep my meaning and tone, but make the prose more direct and less generically AI-like.

> Edit this article using the attached skill. Preserve the technical terminology and remove rhetorical padding.

> Draft a concise announcement using the attached skill. Do not add claims or details that I have not provided.

## Does it work?

Ten AI-slop drafts are revised three times each under three conditions that
differ only in the system prompt. [`tools/slopscore.py`](tools/slopscore.py)
then scores every revision against the sixteen-category audit in `SKILL.md`
(0-32, lower is better).

The generic-advice arm is the comparison that matters. Testing the skill
against an empty prompt would only show that a long instruction beats none, so
the third arm gets a short paragraph of ordinary copy-editing advice instead.

| condition | slopscore | hits per 100 words |
| --- | ---: | ---: |
| the original drafts | 11.60 | 6.46 |
| revised, no guidance | 9.43 | 5.82 |
| revised, generic writing advice | 9.10 | 6.05 |
| **revised with this skill** | **5.10** | **3.99** |

Generic advice removes almost nothing (11.60 to 9.10, 2.50 points). The skill
removes about two and a half times as much (6.50 points). The gap between the
two, 4.00 points of score and 2.06 hits per 100 words, is what the skill adds
beyond prompting in general.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/slopscore-by-draft-dark.svg">
  <img alt="Slopscore per draft for each revision arm" src="assets/slopscore-by-draft-light.svg">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/slopscore-by-category-dark.svg">
  <img alt="Mean score per audit category for each revision arm" src="assets/slopscore-by-category-light.svg">
</picture>

### Caveats

- **Part of the gain is length.** The skill's revisions are shorter (249 words
  against 332 unguided), and shorter text trips fewer patterns outright. Cutting
  padding is one of the skill's stated goals, so this is not cheating. It does
  mean the honest margin over generic advice is 4.00 points of score and 2.06
  hits per 100 words, and the second, smaller number is the length-adjusted one.
- **Structure survives every arm.** "Excessive headings or bullets" barely moves
  (2.00 to 1.63): asked to revise, the model rewrites sentences and leaves the
  scaffolding alone more than it should. If a draft is over-structured, the
  skill will not fix that by itself.
- **Three detectors are inert on this corpus, and two more barely fired.**
  "Forced synonym variation" (one of the original twelve) scored 0 in every
  column across all 90 revisions, and so did two of the four StoryScope-derived
  categories (13-16, see Sources above): "Metaphor saturation" and "Missing
  real-world anchors". The other two, "Over-unified argument" and "Unrelieved
  earnestness", scored at most 0.10, which is real but negligible. Read that
  as a sign of narrow regexes, not a genre mismatch. A review pass wrote
  adversarial paraphrases of the worked examples for categories 13-16 in
  `SKILL.md`; most of them triggered nothing, while a few genuinely fine
  sentences triggered falsely. The `SKILL.md` guidance for all four is sound,
  but their automated detectors are not yet validated the way the original
  twelve are. [`evals/README.md`](evals/README.md) has the full breakdown. It
  includes a like-for-like comparison showing that the measured *score*
  improvement comes from strengthened guidance on *existing* categories, not
  from these four. That is the most this eval can claim, because it cannot
  separate a category's own score from any knock-on effect its guidance has on
  other categories. It also shows, with a real run, how noisy a small subset of
  this eval can get between runs.
- **The harness is not a clean model.** Everything runs through the Claude Code
  CLI, which adds a system prompt of its own to all three arms. They are
  compared under identical conditions, but none of them is a raw model.
- **Small n**, one model, English only. Ten drafts, three samples per arm.

Full method, the confounds behind these choices, and how to reproduce:
[`evals/README.md`](evals/README.md).

## The scorer

`tools/slopscore.py` turns the audit in `SKILL.md` into something a test can
assert on. No dependencies.

```sh
python -m tools.slopscore draft.md            # a report with line-level evidence
python -m tools.slopscore --json draft.md     # machine-readable
cat draft.md | python -m tools.slopscore -    # from a pipe
python -m tools.slopscore --max-score 7 *.md  # exit 1 above the threshold
```

It scores each of the sixteen categories 0 (absent), 1 (occasional) or 2
(frequent), and reads the total against the bands the skill already defines:
0-7 low, 8-15 revise, 16+ substantial rewrite.

It is a writing heuristic, not an AI detector, and it does not read minds: it
counts surface patterns. A text can score 0 and still be boring, wrong, or
plagiarised. What it will not do is reward the tactics `SKILL.md` forbids:
tests assert that em dashes, contractions, correct spelling and honest
repetition all cost nothing.

## Development

```sh
pip install -r requirements-dev.txt
python -m pytest            # scorer, CLI, corpus and SKILL.md contract tests
ruff check . && ruff format --check .
```

CI runs the suite on Python 3.10 to 3.13 on every push. The live model eval is a
separate workflow: it needs an `ANTHROPIC_API_KEY` secret, runs weekly, and
fails if the skill stops beating the generic-advice arm.

One test is worth knowing about: `tests/test_skill_contract.py` asserts that the
sixteen categories in the `SKILL.md` audit match the scorer's, in the same order,
and that the prose band thresholds match the `BANDS` cutoffs in code.
Add a category to the skill without teaching the scorer about it and the build
goes red instead of quietly under-reporting.

## What the skill does not do

The skill does not deliberately insert spelling mistakes, awkward grammar, random slang, fake anecdotes, or fabricated sources. It does not ban individual words or punctuation marks mechanically.

Nor does it guarantee that a text will pass an AI detector. Detector results are unreliable, and no stylistic process can guarantee a particular classification.

## Guiding principle

`SKILL.md` ends on the standard it holds every revision to:

> The target is not imperfect writing.
>
> The target is writing that is specific, proportionate, purposeful, and recognizably authored.

## License

Distributed under the [Apache License 2.0](LICENSE).
