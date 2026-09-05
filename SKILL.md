---
name: the-less-ai-like-writing-skill
description: Produce or revise prose to reduce common generic LLM writing patterns while preserving clarity, specificity, factual accuracy, and the author's natural voice.
---

# Less AI-Like Writing

## Purpose

Produce or revise prose so that it reads as natural, specific, context-aware human writing rather than generic LLM-style prose.

This skill is not a detector-evasion trick and must not rely on cosmetic substitutions alone. Its goal is to improve writing quality by reducing common LLM tendencies such as over-explanation, excessive symmetry, generic abstraction, promotional phrasing, fake completeness, and repetitive rhetorical structures.

Use this skill when the user asks for writing that should feel:
- more natural
- less generic
- less "AI-written"
- more personal or authorial
- less polished in a synthetic way
- less templated
- more direct, concrete, or idiomatic

Do not claim that the resulting text will defeat AI detectors. Detection systems are unreliable and no stylistic process can guarantee a classification outcome.

---

## Core Principle

Do not optimize for "looking human" through random imperfection.

Optimize for:
1. specificity,
2. useful selection,
3. natural variation,
4. simple wording when simple wording is sufficient,
5. justified interpretation,
6. a consistent authorial voice.

A text becomes suspiciously AI-like mostly through the accumulation of patterns, not through one forbidden word or punctuation mark.

---

## Primary AI-Like Patterns

Inspect the draft for combinations of the following.

### 1. Generic significance inflation

AI-like:
> This development highlights the crucial role of technology in an ever-evolving digital landscape.

Prefer:
> The update cuts export time from 12 minutes to about 7.

Rule:
Replace abstract claims about importance with the concrete fact that makes the point important.

---

### 2. Automatic interpretation after every fact

Common forms:
- highlighting...
- underscoring...
- reflecting...
- showcasing...
- demonstrating...
- contributing to...

Rule:
After each factual sentence, ask whether the interpretation adds information.

If not, delete it.

---

### 3. Promotional or brochure-like language

Watch for:
- vibrant
- groundbreaking
- renowned
- rich tapestry
- pivotal
- transformative
- remarkable
- diverse array
- commitment to
- nestled in
- testament to

These words are not forbidden.

Rule:
Keep them only when they are the most accurate words for the context and the surrounding prose does not contain several similar intensifiers.

---

### 4. Excessive rhetorical symmetry

Common patterns:
- not only X, but also Y
- not just X, but Y
- rather than X, Y
- from X to Y
- whether X or Y
- three-item conceptual lists
- paragraphs with identical internal structure

Rule:
Do not force balance where the subject itself is not balanced.

---

### 5. Compulsive rule of three

AI often groups ideas into three even when two or four would be more natural.

Rule:
Use the number of examples or arguments the content actually requires.

Do not add a third item merely for cadence.

---

### 6. Unnecessary synonym cycling

AI-like:
> The processor... the chip... the computing unit... the silicon solution...

Prefer:
> The processor... the processor...

Rule:
Repeat the correct noun when repetition improves precision.

Do not replace words merely to avoid repetition.

---

### 7. Avoidance of simple verbs

Watch for unnecessary replacements of:
- is
- has
- uses
- says
- wrote
- made
- changed

with:
- serves as
- features
- utilizes
- articulates
- authored
- facilitated
- underwent a transformation

Rule:
Use the simplest accurate verb unless nuance requires another one.

---

### 8. Artificial completeness

AI drafts often try to cover:
- advantages
- disadvantages
- challenges
- implications
- future outlook
- conclusion

even when the task does not require them.

Rule:
Stop when the useful content is finished.

Do not create closure for its own sake.

---

### 9. Template conclusions

Watch for:
- In conclusion...
- Looking ahead...
- Despite these challenges...
- Ultimately...
- As the landscape continues to evolve...

Rule:
Delete generic conclusions.

End on the last useful fact, argument, image, implication, or decision.

---

### 10. Vague attribution

Avoid:
- experts say
- critics argue
- observers note
- many believe
- studies suggest

unless the source is known or the phrasing is intentionally general and justified.

Prefer:
> A 2025 study by X found...

or:
> I could not find a source that establishes this.

---

### 11. Meta-chatbot language

Remove from standalone prose:
- Here is a detailed overview...
- Below are...
- It is important to note...
- As requested...
- I hope this helps...
- Let me know if...
- I can also...

unless the format genuinely calls for conversational assistant language.

---

### 12. Over-structured formatting

Possible signals:
- a heading for every small idea
- identical bullet structure
- bold lead-in + colon for every bullet
- Key Takeaways added automatically
- excessive Title Case

Rule:
Use structure only when it improves navigation.

For short prose, paragraphs are often better than a miniature report.

---

## Human-Like Counterpatterns

Prefer the following.

### Concrete before abstract

Bad:
> The change represents an important shift in user behavior.

Better:
> Users now open the app mostly from notifications rather than from the home screen.

If interpretation matters, put it after the evidence.

---

### Natural repetition

Do not fear repeating a precise technical term.

Controlled repetition often sounds more credible than forced synonym variation.

---

### Variable sentence length

Allow:
- short sentences,
- medium explanatory sentences,
- occasional longer sentences where the thought requires it.

Do not manufacture variation mechanically.

The rhythm should follow the argument.

---

### Uneven paragraph size

Paragraphs do not need matching lengths.

One paragraph may contain one sentence if that sentence deserves isolation.

---

### Selective explanation

Explain what the intended reader is unlikely to know.

Do not explain obvious consequences merely to make the prose sound complete.

---

### Specific verbs and nouns

Prefer:
> The patch broke Bluetooth pairing on older Intel cards.

over:
> The update introduced challenges affecting connectivity functionality in legacy hardware environments.

---

### Qualified uncertainty

Natural writing can say:
- probably
- apparently
- I suspect
- the evidence is limited
- this may be
- I could not verify

when uncertainty is real.

Do not artificially sound certain.

---

### Authorial judgment with a reason

Instead of generic evaluation:
> This is a significant improvement.

Prefer:
> This is the first version I would actually use daily, mainly because the latency is no longer noticeable.

The reason makes the judgment specific.

---

## Generation Workflow

When writing from scratch:

### Step 1: Identify the actual information

Before drafting, determine:
- What facts must be communicated?
- What does the reader need to understand?
- What judgment, if any, belongs to the author?
- What can be omitted?

Do not pad incomplete information with generic prose.

### Step 2: Draft directly

Start with the most informative sentence rather than an introduction about the topic's importance.

### Step 3: Prefer concrete language

Replace abstractions with:
- examples,
- measurements,
- named mechanisms,
- observable effects,
- actual actions.

### Step 4: Let structure emerge from content

Do not automatically create:
Introduction → Benefits → Challenges → Future → Conclusion.

### Step 5: Run the AI-like pattern audit below.

---

## Revision Workflow

When editing an existing draft:

### Pass A — Information density

For every sentence ask:
> Does this sentence add a fact, argument, example, necessary transition, or meaningful judgment?

If no, cut or merge it.

### Pass B — Abstract language

Flag sentences containing several abstract nouns or significance phrases.

Rewrite them using concrete nouns and verbs.

### Pass C — Repetitive rhetoric

Look for repeated:
- participial endings,
- contrast constructions,
- three-item lists,
- identical paragraph openings,
- generic conclusions.

Break the pattern.

### Pass D — Vocabulary

Replace unnecessarily elevated vocabulary with ordinary accurate language.

Do not intentionally misspell words or insert grammatical mistakes.

### Pass E — Voice

Check whether the text sounds like one identifiable writer rather than a neutral composite voice.

Preserve domain-specific vocabulary, preferences, skepticism, humor, restraint, or directness when supplied by the user.

### Pass F — Final cut

Delete sentences that merely summarize what the preceding sentence already made obvious.

---

## AI-Likeness Audit

Score each category from 0 to 2.

0 = absent  
1 = occasional  
2 = frequent

Categories:

1. Generic statements of importance
2. Automatic interpretation after facts
3. Promotional adjectives
4. Formulaic contrasts
5. Three-item lists
6. Forced synonym variation
7. Avoidance of simple verbs
8. Excessive headings or bullets
9. Vague attribution
10. Generic conclusion
11. Meta-chatbot phrasing
12. Artificially comprehensive coverage

Interpretation:

- 0–5: low density of common AI-like patterns
- 6–11: revise the most repetitive patterns
- 12+: substantial rewrite recommended

This score is a writing heuristic, not an AI detector.

---

## Anti-Patterns for This Skill

Do NOT make text "less AI-like" by:

- inserting spelling mistakes
- adding random grammatical errors
- using slang that does not match the writer
- replacing punctuation mechanically
- banning em dashes
- banning individual words
- deliberately lowering clarity
- introducing factual inconsistency
- adding fake anecdotes
- pretending to have personal experiences
- fabricating sources
- changing every sentence merely for variation
- making the prose erratic on purpose

These tactics reduce quality and can themselves become recognizable patterns.

---

## Style Preservation

If the user provides a sample of their own writing, treat it as the strongest style reference.

Extract only non-sensitive stylistic properties such as:
- average sentence length
- directness
- amount of first-person language
- use of irony
- technical density
- preferred paragraph length
- tolerance for repetition
- formality
- typical transitions

Do not caricature the sample.

Preserve the author's normal level of polish.

---

## Output Behavior

Unless the user asks for analysis, return the revised or generated text rather than a long explanation of the edits.

When useful, briefly identify the main changes:
- reduced generic commentary
- simplified verbs
- removed repetitive rhetorical structures
- increased specificity
- preserved natural repetition

Do not state or imply:
> This text cannot be detected as AI.

A safer formulation is:
> This version reduces several stylistic patterns commonly associated with generic LLM prose.

---

## Compact Prompt Version

When a full workflow is unnecessary, apply this internal instruction:

> Write with high specificity and low rhetorical padding. Prefer simple accurate verbs, concrete nouns, natural repetition, variable sentence rhythm, and selective explanation. Avoid generic significance claims, automatic "highlighting/underscoring" commentary, promotional language, forced three-part lists, template contrasts, synonym cycling, fake completeness, vague attribution, excessive headings, chatbot meta-language, and generic conclusions. Do not add deliberate errors or artificial quirks. Preserve the author's established voice when available.

---

## Final Quality Test

Before returning the text, ask:

1. Could any paragraph apply almost unchanged to a different topic?
   - If yes, make it more specific.

2. Did I explain why something matters without showing why?
   - If yes, add evidence or remove the claim.

3. Did I use a rhetorical pattern more than once?
   - If yes, vary or simplify it.

4. Did I choose a fancy synonym only to avoid repetition?
   - If yes, restore the precise term.

5. Does the ending add information?
   - If no, cut it.

6. Does the text sound polished beyond the needs of the context?
   - If yes, simplify it.

7. Did I introduce imperfections merely to simulate humanity?
   - If yes, remove them.

The target is not imperfect writing.

The target is writing that is specific, proportionate, purposeful, and recognizably authored.
