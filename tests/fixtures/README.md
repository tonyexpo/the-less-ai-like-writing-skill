# Fixture corpus

Provenance matters here, so it is recorded rather than assumed.

## `slop/`

Hand-written by the repository author as dense examples of the patterns in
`SKILL.md`. They are deliberately concentrated - real model output is rarely
this bad - and they exist to check that every detector fires at all.

They are **not** calibration data. An early version of the scorer was tuned
against these files alone and looked excellent while missing most of the tells
in real model output, because the fixtures and the pattern tables had been
written by the same author from the same mental list. The corpus below exists
so that mistake stays fixed.

## `clean/`

Two kinds of negative control:

- `obama_note.md`, `release_note.md`, `api_guide.md` - hand-written prose that
  should score near zero.
- `model-*.md` - **unedited** model output, kept exactly as generated. These are
  the important ones: they were not written with the detectors in mind, so they
  are the honest test of whether the scorer flags good writing. Anything that
  makes these score highly is a false positive, not a finding.

## Frozen slop drafts

`evals/drafts/*.md` is a third corpus: real model output produced under a
slop-inducing prompt. `tests/test_corpus.py` asserts it stays separated from
`clean/`, which is what keeps the scorer honest against text nobody hand-tuned.
