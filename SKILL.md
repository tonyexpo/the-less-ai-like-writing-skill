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

Do not claim that the resulting text will defeat AI detectors. Detection systems are unreliable and no stylistic process can guarantee a classification outcome. This is not a hedge: a 2026 study of AI-generated fiction (StoryScope, arXiv:2604.03136) found that its 304 narrative features — across ten dimensions including plot and style, with no access to raw text at all — separate human from AI writing at 93.2% macro-F1. Reducing generic phrasing changes some of what those features measure; it does not change all of it, and it is not a way to hide what wrote a piece.

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

This is one of the best-evidenced patterns in the whole audit. In StoryScope's
narrative-feature study (arXiv:2604.03136), the narrator explicitly commented
on the meaning of events in 76.4% of AI stories versus 51.6% of human ones,
and themes were rated fully explicit rather than left implicit in 74.8% of AI
stories versus 37.4% of human ones — the fourth-strongest separator the study
found among 304 narrative features tested.

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

The same pattern shows up as structure, not just phrasing: in the StoryScope
study (arXiv:2604.03136), AI-written stories kept going well past their climax
— multiple extra scenes, time jumps, or an epilogue — in 51.3% of cases versus
14.8% for human stories, which far more often ended at or just after the
climax. Writing past the natural stopping point and zooming out to a
summarizing vantage is a structural form of "looking ahead."

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

The four patterns below come from StoryScope (Russell et al., arXiv:2604.03136),
a study of ~61,600 parallel human and LLM stories that induces 304 features
across ten dimensions (plot, style, agents, and seven others) and finds them,
together, separable from human writing at 93.2% macro-F1. Style is in fact
the single highest-separating dimension on average and supplies 11 of the 20
strongest individual features - the strongest of them (category 13's, below)
is second-strongest overall. The study is about long-form fiction, not blog
posts or memos, so each pattern here is the subset of its findings that
plausibly transfers to ordinary prose, restated as prose advice rather than
as the paper's own narrative-specific language. All
four are whole-document judgments — call them by reading the piece, not by
scanning for a keyword.

### 13. Metaphor saturation

AI-like:
> If the first release was a sketch, this one is the underpainting. Each
> layer since has pressed down on the one before it, the way sediment does.
> The whole product eroded, then cracked, then gave way to something
> sturdier underneath.

Prefer:
> The first release was rough. Since then we have shipped four incremental
> improvements, each fixing what the last one exposed.

Rule:
One well-chosen figure of speech can be the clearest way to say something.
A figure of speech that gets extended across several sentences, or a single
image (tides, layers, threads, weather, machinery) that recurs as the piece's
organizing device, usually means a plain statement was avoided rather than
earned. Cut back to the plain statement and keep the figure only if it is
still doing real work once the extension is gone.

Evidence: figurative density rated as heavy in 65% of AI-written passages
versus 18% of human ones; an image extended across multiple sentences in 83%
of AI passages versus 40% of human ones (StoryScope, TVD 0.48 - the single
strongest style-dimension feature in the study, though not the strongest of
all 304).

---

### 14. Missing real-world anchors

AI-like:
> A popular streaming service ran into trouble last year after a well-known
> book on management inspired its new engagement strategy.

Prefer:
> Netflix ran into trouble last year after "High Output Management" inspired
> its new engagement strategy.

Rule:
Use the real name once you know it: the product, the company, the book, the
person, the date, the number. "A popular streaming service" and "a well-known
book" are not more careful than the real names — they are less informative,
and the reader cannot check them. If the specific isn't known, say so plainly
("I don't know which one") rather than reaching for a vague placeholder.

Evidence: reference to a specific, nameable brand or cultural touchstone
appeared in 40% of human-written passages versus 13% of AI-written ones —
a 27-point gap, one of the larger human-leaning ones StoryScope measured.

---

### 15. Over-unified argument

AI-like:
> Each of these examples points back to the same underlying theme: that
> patience and ambition were never really in tension. Taken together, the
> picture is clear.

Prefer:
> Two of the three setbacks were avoidable in hindsight. The third we still
> don't fully understand.

Rule:
Real arguments usually have a loose end: a detail that doesn't fit the
thesis but is true anyway, an example that only partly supports the point, a
verdict that stays mixed. Forcing every thread to serve one clean idea, and
resolving every tension into a tidy lesson, is a sign the material was pruned
to fit a conclusion rather than reported as it was. Keep the loose end if it
is real.

Evidence: thematic unity rated maximal in 74% of AI-written stories versus
41% of human ones (TVD 0.33). Human-written stories left the ending
ambiguous more often (35% human vs 19% AI) and gave the central figure a
morally mixed verdict more often (58% human vs 38% AI) than AI-written ones
did (StoryScope).

---

### 16. Unrelieved earnestness

AI-like:
> This journey has been both challenging and rewarding. Every obstacle
> became an opportunity to grow, and the results speak for themselves.

Prefer:
> The migration took three weeks longer than planned. I'm still annoyed
> about the two weeks we lost to a config bug nobody caught in review.

Rule:
A piece that never once undercuts itself, treats every difficulty as
meaningful rather than merely annoying, and maintains one solemn register
from start to finish reads as performed sincerity rather than the real
thing. Real writing usually has at least one dry, wry, or deflating moment,
or admits a plain annoyance instead of reframing it as growth. This does not
apply to subject matter that has earned its gravity — an incident report on
a safety failure, an obituary — where plain, unadorned seriousness is
simply accurate.

Evidence: AI-written passages were rated entirely straight-faced with no
discernible humor in 38% of cases versus 12% for human-written ones; an
ironic or wry dominant tone appeared in 36% of human passages versus 13% of
AI ones (StoryScope).

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

This is prose advice, not an anti-AI-detection tactic: sentence length barely
separates AI from human writing in practice (StoryScope, arXiv:2604.03136,
found only a weak signal, and sentence fragments specifically ran the other
way — present and stylistically significant in 85% of AI-written passages
versus 67% of human ones). A string of punchy fragments is not evidence of a
human hand. Vary rhythm because it serves the argument, not to seem human.

---

### Loose, digressive sentences

Not every sentence needs to resolve cleanly. A sentence that runs on, picks
up a second clause loosely with "and" or a comma rather than a tight
subordinate structure, and only gets to the point after a slight detour, is
a normal feature of how people actually write and talk.

AI prose defaults to tight parallel construction almost universally instead:
StoryScope found frequent parallel or list-like sentence structure in 99% of
AI-written passages versus 70% of human ones, while loosely-joined,
multi-clause chains ran the other way (55% AI versus 76% human). Do not force
a loose sentence in edit, but do not tighten one into parallel structure
purely for polish either.

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

### Step 5: Treat the audit as a separate pass, not a check on text still being written

A self-audit only works reliably against a draft that already exists in
full, not against text still being emitted. Once a sentence is part of the
visible response, it cannot truly be rewritten within that same response —
only added to.

**Finish the draft as a complete piece of writing first. Then apply the
Revision Workflow below to it as its own, later step** — against a draft
that is now finished and in front of you, not one still being composed.
When it is possible to make this a genuinely separate turn or call (a new
conversation turn, a fresh context, an independent reviewer), prefer that:
it is the version of this that was actually measured to work.

If reasoning is available before the visible answer is written, drafting
there first and revising before any visible output begins is worth doing
in addition — but do not rely on it alone. Measured directly, that
private-draft approach only partly closed the gap on one model and did
not move the score at all on another, while the same audit run as a
genuinely separate pass over a finished draft cut the score roughly in
half on every model and topic tested cleanly. See `evals/selfedit_timing/`
for the test and the numbers, including this second round.

---

## Revision Workflow

When editing an existing draft — including a draft produced in a prior,
separate pass per Step 5 above:

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
13. Metaphor saturation
14. Missing real-world anchors
15. Over-unified argument
16. Unrelieved earnestness

Interpretation:

- 0–7: low density of common AI-like patterns
- 8–15: revise the most repetitive patterns
- 16+: substantial rewrite recommended

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

> Write with high specificity and low rhetorical padding. Prefer simple accurate verbs, concrete nouns, natural repetition, variable sentence rhythm, and selective explanation. Avoid generic significance claims, automatic "highlighting/underscoring" commentary, promotional language, forced three-part lists, template contrasts, synonym cycling, fake completeness, vague attribution, excessive headings, chatbot meta-language, and generic conclusions. Do not extend a single figure of speech across the whole piece, do not use vague placeholders where a real name is known, do not force every example toward one tidy lesson, and do not maintain one solemn register with no tonal relief anywhere. Do not add deliberate errors or artificial quirks. Preserve the author's established voice when available.

---

## Final Quality Test

Apply this against a draft that is already finished and fully in view —
privately reasoned or from a separate pass, per Generation Workflow Step 5
— not while still composing the sentences being checked.

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

8. Did I extend a figure of speech past the point it was earning its place,
   reach for a vague placeholder where I actually knew the name, force a
   mixed result into one tidy lesson, or write a whole piece with no tonal
   relief anywhere?
   - If yes, cut back to the plain statement, name the thing, keep the loose
     end, or let one moment be dry.

The target is not imperfect writing.

The target is writing that is specific, proportionate, purposeful, and recognizably authored.
