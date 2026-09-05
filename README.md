# Less AI-Like Writing Skill

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

### ChatGPT or other tools that accept file attachments

1. Download [`SKILL.md`](https://github.com/tonyexpo/the-less-ai-like-writing-skill/raw/refs/heads/main/SKILL.md).
2. Upload the file to ChatGPT, Claude, or another AI tool that accepts instruction files or project attachments.
3. Ask the tool to apply the skill when drafting or revising text.

Example requests:

> Use the attached skill to rewrite this draft. Keep my meaning and tone, but make the prose more direct and less generically AI-like.

> Edit this article using the attached skill. Preserve the technical terminology and remove rhetorical padding.

> Draft a concise announcement using the attached skill. Do not add claims or details that I have not provided.

## What the skill does not do

The skill does not deliberately insert spelling mistakes, awkward grammar, random slang, fake anecdotes, or fabricated sources. It does not ban individual words or punctuation marks mechanically.

It also does not guarantee that a text will pass an AI detector. Detector results are unreliable, and no stylistic process can guarantee a particular classification. This skill focuses on writing quality rather than detector evasion.

## Guiding principle

The target is not imperfect writing. The target is writing that is specific, proportionate, purposeful, and recognizably authored.

## License

Distributed under the [Apache License 2.0](LICENSE).
