# Less AI-Like Writing Skill

[![CI](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/ci.yml)
[![Eval](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/eval.yml/badge.svg)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/actions/workflows/eval.yml)
[![License: Apache-2.0](https://img.shields.io/github/license/tonyexpo/the-less-ai-like-writing-skill?color=blue)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/tonyexpo/the-less-ai-like-writing-skill)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/tonyexpo/the-less-ai-like-writing-skill?style=flat)](https://github.com/tonyexpo/the-less-ai-like-writing-skill/stargazers)

A reusable writing and editing skill that reduces common generic LLM prose patterns while preserving clarity, factual accuracy, and the author's natural voice.

It is designed for text that feels too polished, vague, repetitive, promotional, or structurally predictable. The goal is better writing—not manufactured imperfections or tricks intended to defeat AI detectors.

## What it improves

The skill looks for patterns such as:

- abstract claims of importance without supporting facts;
- unnecessary interpretation after every statement;
- promotional or brochure-like language;
- forced contrasts and three-part lists;
- synonym cycling where simple repetition would be clearer;
- overly elaborate verbs, headings, introductions, and conclusions;
- vague attribution and assistant-style filler.

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

Measured, not asserted. Eight AI-slop drafts are revised three times each under
three conditions that differ only in the system prompt, and the revisions are
scored by [`tools/slopscore.py`](tools/slopscore.py) against the twelve-category
audit in `SKILL.md` (0-24, lower is better).

The middle arm is the one that makes this worth reading. Comparing the skill
against an empty prompt would only show that 12 KB of instructions beats none,
so a third arm gets a short paragraph of ordinary copy-editing advice instead.

| condition | slopscore | hits per 100 words |
| --- | ---: | ---: |
| the original drafts | 11.62 | 6.60 |
| revised, no guidance | 10.00 | 6.19 |
| revised, generic writing advice | 9.71 | 6.38 |
| **revised with this skill** | **6.75** | **5.31** |

Generic advice removes almost nothing (11.62 to 9.71). The skill removes about
three times as much, and the gap between the two is the part attributable to
the skill rather than to prompting in general.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/slopscore-by-draft-dark.svg">
  <img alt="Slopscore per draft for each revision arm" src="assets/slopscore-by-draft-light.svg">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/slopscore-by-category-dark.svg">
  <img alt="Mean score per audit category for each revision arm" src="assets/slopscore-by-category-light.svg">
</picture>

### Read the numbers with these caveats

- **Part of the gain is length.** The skill's revisions are shorter (255 words
  against 340 unguided), and shorter text trips fewer patterns outright. Cutting
  padding is one of the skill's stated goals, so this is not cheating, but it
  does mean the honest margin over generic advice is 2.96 points of score and
  1.07 hits per 100 words - the smaller number is the length-adjusted one.
- **Structure survives every arm.** "Excessive headings or bullets" barely moves
  (2.00 to 1.92): asked to revise, the model rewrites sentences and leaves the
  scaffolding alone. If a draft is over-structured, the skill will not fix that
  by itself.
- **One detector is inert.** "Forced synonym variation" scored 0 everywhere. It
  only knows a fixed list of synonym clusters, so treat that row as unmeasured
  rather than as a clean result.
- **The harness is not a clean model.** Everything runs through the Claude Code
  CLI, which adds a system prompt of its own to all three arms. They are
  compared under identical conditions, but none of them is a raw model.
- **Small n**, one model, English only. Eight drafts, three samples per arm.

Full method, the confounds behind these choices, and how to reproduce:
[`evals/README.md`](evals/README.md).

## The scorer

`tools/slopscore.py` turns the audit in `SKILL.md` into something a test can
assert on. No dependencies.

```sh
python -m tools.slopscore draft.md            # a report with line-level evidence
python -m tools.slopscore --json draft.md     # machine-readable
cat draft.md | python -m tools.slopscore -    # from a pipe
python -m tools.slopscore --max-score 5 *.md  # exit 1 above the threshold
```

It scores each of the twelve categories 0 (absent), 1 (occasional) or 2
(frequent), using the bands the skill already defines: 0-5 low, 6-11 revise,
12+ substantial rewrite.

It is a writing heuristic, not an AI detector, and it does not read minds: it
counts surface patterns. A text can score 0 and still be boring, wrong, or
plagiarised. What it will not do is reward the tactics `SKILL.md` forbids -
there are tests asserting that em dashes, contractions, correct spelling and
honest repetition all cost nothing.

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
twelve categories in the `SKILL.md` audit match the scorer's, in the same order.
Add a category to the skill without teaching the scorer about it and the build
goes red instead of quietly under-reporting.

## What the skill does not do

The skill does not deliberately insert spelling mistakes, awkward grammar, random slang, fake anecdotes, or fabricated sources. It does not ban individual words or punctuation marks mechanically.

It also does not guarantee that a text will pass an AI detector. Detector results are unreliable, and no stylistic process can guarantee a particular classification. This skill focuses on writing quality rather than detector evasion.

## Guiding principle

The target is not imperfect writing. The target is writing that is specific, proportionate, purposeful, and recognizably authored.

## License

Distributed under the [Apache License 2.0](LICENSE).
