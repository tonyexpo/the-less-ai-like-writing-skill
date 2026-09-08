"""Whole-document tests over three corpora with different provenance.

The unit tests check that each detector fires. These check that the detectors
add up to a score that separates generic LLM prose from specific prose, which is
the only claim the tool actually makes.

The corpus that matters most is ``evals/drafts`` versus ``clean/model-*``: both
are unedited model output, neither was written with the detectors in mind, and
the scorer has to tell them apart. See tests/fixtures/README.md for why.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.slopscore import score_file

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
SLOP = sorted((FIXTURES / "slop").glob("*.md"))
CLEAN = sorted((FIXTURES / "clean").glob("*.md"))
MODEL_CLEAN = sorted((FIXTURES / "clean").glob("model-*.md"))
DRAFTS = sorted((REPO_ROOT / "evals/drafts").glob("*.md"))

# The bands from SKILL.md.
SLOP_FLOOR = 12
CLEAN_CEILING = 5
# Real model slop is milder than the hand-written fixtures, so it gets its own
# floor. Anything lower and the draft is not worth putting through the eval.
DRAFT_FLOOR = 10
MIN_SEPARATION = 4


def test_corpora_are_populated():
    assert len(SLOP) >= 2
    assert len(CLEAN) >= 4
    assert len(MODEL_CLEAN) >= 2, "unedited model output is the important control"
    assert len(DRAFTS) >= 5


@pytest.mark.parametrize("path", SLOP, ids=lambda p: p.name)
def test_slop_fixture_lands_in_rewrite_band(path):
    report = score_file(path)
    assert report.total >= SLOP_FLOOR, f"{path.name} scored {report.total}"
    assert report.band == "rewrite"


@pytest.mark.parametrize("path", CLEAN, ids=lambda p: p.name)
def test_clean_fixture_lands_in_low_band(path):
    report = score_file(path)
    assert report.total <= CLEAN_CEILING, f"{path.name} scored {report.total}"
    assert report.band == "low"


@pytest.mark.parametrize("path", MODEL_CLEAN, ids=lambda p: p.name)
def test_good_model_output_is_not_flagged(path):
    """The false-positive test. These are unedited generations that read well;
    if the scorer punishes them it is measuring style, not slop."""
    report = score_file(path)
    assert report.total <= 3, f"{path.name} scored {report.total}: likely a false positive"


@pytest.mark.parametrize("path", DRAFTS, ids=lambda p: p.stem)
def test_frozen_eval_drafts_are_actually_sloppy(path):
    """A draft the scorer already rates clean gives the eval nothing to measure."""
    report = score_file(path)
    assert report.total >= DRAFT_FLOOR, f"{path.stem} scored {report.total}"


def test_generated_corpora_are_separated():
    """Model slop versus model prose that reads well, with no hand-written text
    on either side."""
    worst_clean = max(score_file(p).total for p in MODEL_CLEAN)
    best_draft = min(score_file(p).total for p in DRAFTS)
    assert best_draft - worst_clean >= MIN_SEPARATION, (
        f"only {best_draft - worst_clean} points between real model slop "
        f"({best_draft}) and real model prose ({worst_clean})"
    )


def test_hand_written_corpora_are_separated():
    worst_clean = max(score_file(p).total for p in CLEAN)
    best_slop = min(score_file(p).total for p in SLOP)
    assert best_slop - worst_clean >= 8


@pytest.mark.parametrize("path", CLEAN, ids=lambda p: p.name)
def test_clean_fixtures_trip_at_most_two_categories(path):
    tripped = [c.key for c in score_file(path).categories if c.score > 0]
    assert len(tripped) <= 2, f"{path.name} tripped {tripped}"


@pytest.mark.parametrize("path", SLOP, ids=lambda p: p.name)
def test_slop_fixtures_trip_most_categories(path):
    tripped = [c.key for c in score_file(path).categories if c.score > 0]
    assert len(tripped) >= 9, f"{path.name} only tripped {tripped}"


def test_readme_stays_readable():
    """The README quotes the patterns it describes, so it will never score 0.
    It should not drift into the rewrite band either."""
    report = score_file(REPO_ROOT / "README.md")
    assert report.band != "rewrite", f"README scored {report.total}"
