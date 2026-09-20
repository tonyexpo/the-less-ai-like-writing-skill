"""One positive and one negative case per audit category.

The negative cases matter more than the positive ones. A detector that fires on
"experts say" is easy; a detector that stays quiet on "Nakamura's 2021 paper
found" is the one that keeps the score honest.
"""

from __future__ import annotations

import pytest

from tools.patterns import CATEGORIES
from tools.slopscore import score_text

# (category, text that should trigger it, text that should not)
CASES: list[tuple[str, str, str]] = [
    (
        "significance_inflation",
        "The release highlights the importance of testing in an ever-evolving landscape.",
        "The release cut the test suite from 41 minutes to 9.",
    ),
    (
        "automatic_interpretation",
        "Revenue rose 4%, underscoring the strength of the subscription business.",
        "Revenue rose 4%. Subscriptions accounted for all of the increase.",
    ),
    (
        "promotional_adjectives",
        "A groundbreaking, cutting-edge platform with unparalleled, seamless integration.",
        "A caching layer that keeps parsed configs in memory between requests.",
    ),
    (
        "formulaic_contrast",
        "This is not only faster but also cheaper to run at scale.",
        "This is faster and cheaper to run at scale.",
    ),
    (
        "rule_of_three",
        "It improves speed, reliability, and flexibility for every team.",
        "It improves speed and reliability.",
    ),
    (
        "synonym_cycling",
        "The company grew. The firm hired 40 people. The organization now has offices "
        "in three cities, and the business expects more.",
        "The company grew. The company hired 40 people. The company now has offices "
        "in three cities and expects more.",
    ),
    (
        "elevated_verbs",
        "The team utilizes a queue that serves as a buffer and facilitates retries.",
        "The team uses a queue as a buffer so failed jobs can retry.",
    ),
    (
        "vague_attribution",
        "Experts say the approach is sound, and studies suggest it scales.",
        "Nakamura's 2021 paper measured a 30% improvement on the same benchmark.",
    ),
    (
        "template_conclusion",
        "In conclusion, only time will tell how this plays out. Ultimately, "
        "one thing is clear: the field keeps moving.",
        "The migration finishes in March. After that the old endpoint returns 410.",
    ),
    (
        "meta_chatbot",
        "Sure! Here is a detailed overview. It is important to note the caveats. "
        "Let me know if you would like more.",
        "The caveats are in the appendix, with the raw timings.",
    ),
    # The four categories below come from StoryScope (arXiv:2604.03136). Each
    # is a narrow lexical proxy for a whole-document judgment, so the negative
    # case matters even more than usual - see the module docstring in
    # tools/patterns.py for the floors and reasoning.
    (
        "metaphor_saturation",
        "If the first version was a sketch, this one is the underpainting. "
        "The old system is a kind of scaffolding we never fully removed.",
        "The rollout felt like pulling teeth, but the queue backs up once "
        "the worker pool saturates, which is a known limit of the design.",
    ),
    (
        "missing_anchors",
        "A popular streaming service ran into trouble last year after a "
        "well-known book on management inspired its new engagement strategy.",
        "Netflix ran into trouble last year after 'High Output Management' "
        "inspired its new engagement strategy.",
    ),
    (
        "over_unified_argument",
        "Each of these threads points back to the same underlying question. "
        "Taken together, the picture is clear, and those aren't contradictions, they're the point.",
        "Two of the three changes helped. The third one I still can't explain.",
    ),
    (
        "unrelieved_earnestness",
        "This journey has been both challenging and rewarding. Every obstacle "
        "became an opportunity to grow, and we carry a deep sense of gratitude.",
        "The migration was straightforward and finished on time.",
    ),
]

STRUCTURAL_CASES: list[tuple[str, str, str]] = [
    (
        "over_structuring",
        "# A\ntext\n## B\ntext\n### C\ntext\n#### D\ntext\n##### E\ntext\n"
        "- **Speed:** fast\n- **Cost:** cheap\n- **Scale:** big\n",
        "# Rate limits\n\n" + "Every token gets 600 requests per minute and the "
        "counter resets on a sliding window rather than on the minute boundary. " * 4,
    ),
    (
        "artificial_completeness",
        "# Introduction\na\n# Benefits\nb\n# Challenges\nc\n# Future Outlook\nd\n# Conclusion\ne\n",
        "# Rate limits\na\n# Raising the limit\nb\n",
    ),
]


@pytest.mark.parametrize("category,positive,negative", CASES + STRUCTURAL_CASES, ids=lambda v: None)
def test_detector_fires_on_positive(category, positive, negative):
    assert score_text(positive).count_of(category) > 0, f"{category} missed its positive case"


@pytest.mark.parametrize("category,positive,negative", CASES + STRUCTURAL_CASES, ids=lambda v: None)
def test_detector_silent_on_negative(category, positive, negative):
    assert score_text(negative).count_of(category) == 0, f"{category} false-positived"


def test_every_category_has_a_case():
    covered = {c for c, _, _ in CASES + STRUCTURAL_CASES}
    assert covered == set(CATEGORIES), f"uncovered categories: {set(CATEGORIES) - covered}"


def test_empty_text_scores_zero():
    report = score_text("")
    assert report.total == 0
    assert report.words == 0
    assert report.band == "low"


def test_code_blocks_are_not_prose():
    """Patterns quoted inside code fences must not count against the author."""
    fenced = "Here are the timings.\n\n```\nutilize leverage groundbreaking seamless\n```\n"
    assert score_text(fenced).count_of("promotional_adjectives") == 0
    assert score_text(fenced).count_of("elevated_verbs") == 0


def test_inline_code_is_not_prose():
    assert score_text("Call `utilize_cache()` when the config is hot.").count_of("elevated_verbs") == 0


def test_line_numbers_survive_code_stripping():
    text = "```\nfoo\nbar\n```\n\nExperts say this works.\n"
    hits = score_text(text).by_key["vague_attribution"].hits
    assert hits and hits[0].line == 6


def test_scoring_is_density_based_not_length_based():
    """Repeating a clean paragraph must not inflate the score."""
    clean = "The p99 latency stayed at 210ms after the change. " * 40
    assert score_text(clean).total == 0


def test_one_hit_in_a_long_text_scores_occasional_not_frequent():
    text = "The queue drains in under a second. " * 60 + " Experts say so."
    assert score_text(text).score_of("vague_attribution") == 1


def test_repeated_hits_score_frequent():
    text = (
        "Experts say it works. Critics argue otherwise. Studies suggest a third view. "
        "Many believe the truth is elsewhere."
    )
    assert score_text(text).score_of("vague_attribution") == 2


def test_total_is_the_sum_of_categories():
    from pathlib import Path

    fixture = Path(__file__).parent / "fixtures/slop/obama_overview.md"
    report = score_text(fixture.read_text(encoding="utf-8"))
    assert report.total == sum(c.score for c in report.categories)
    assert 0 <= report.total <= 2 * len(CATEGORIES)


@pytest.mark.parametrize(
    "total,band", [(0, "low"), (7, "low"), (8, "revise"), (15, "revise"), (16, "rewrite"), (32, "rewrite")]
)
def test_bands_follow_the_skill_thresholds(total, band):
    from tools.slopscore import _band

    assert _band(total) == band


def test_unsupported_language_is_rejected():
    with pytest.raises(ValueError, match="unsupported language"):
        score_text("testo di prova", lang="it")


# SKILL.md lists tactics that must NOT be used to make text look less AI-like.
# A scorer that rewards them would push writers straight into them, so the
# guards below are as important as the detectors themselves.


def test_em_dashes_are_not_penalised():
    """SKILL.md names "banning em dashes" as an anti-pattern. The detector
    targets the significance clause a dash can introduce, never the dash."""
    plain = (
        "The build takes 40 seconds — down from four minutes last quarter. "
        "We moved the parser out of the request path — the obvious fix — and "
        "the p99 followed."
    )
    assert score_text(plain).count_of("automatic_interpretation") == 0
    reveal = "We shipped it in a week — a reminder that small teams move fast."
    assert score_text(reveal).count_of("automatic_interpretation") == 1


def test_contractions_and_first_person_are_not_penalised():
    text = (
        "I haven't chased the tail latency yet. It's probably the disk, but I "
        "can't prove that from the traces we keep."
    )
    assert score_text(text).total == 0


def test_correct_spelling_is_not_penalised():
    """The score must not reward the deliberate errors SKILL.md forbids."""
    clean = "The migration finished at 02:14 and the replicas caught up by 02:20."
    broken = "teh migraiton finished at 02:14 and the replicas cought up by 02:20."
    assert score_text(clean).total == score_text(broken).total == 0


def test_a_single_three_item_list_is_not_a_finding():
    """One list is ordinary English. SKILL.md asks for the number of items the
    content requires, not for the shape to be avoided."""
    one = "We support Postgres, MySQL, and SQLite."
    assert score_text(one).score_of("rule_of_three") == 0
    many = (
        "We support Postgres, MySQL, and SQLite. It is fast, cheap, and simple. "
        "The team is small, focused, and remote."
    )
    assert score_text(many).score_of("rule_of_three") > 0


def test_technical_repetition_is_not_penalised():
    """SKILL.md prefers repeating the precise term over synonym cycling, so
    repetition must not cost anything."""
    text = "The parser caches the config. The parser reads it once. The parser never re-reads it."
    assert score_text(text).count_of("synonym_cycling") == 0


# StoryScope (arXiv:2604.03136) explicitly found these do NOT separate AI from
# human writing - see tools/patterns.py's module docstring. The point of these
# tests is to keep it that way: a future change that adds a raw em-dash-count
# or sentence-length detector should fail loudly, not slip in quietly because
# it "sounds right".


def test_frequent_em_dashes_alone_are_not_penalised():
    """The paper measured em-dash/parenthetical-aside frequency directly (its
    own question wording covers 'parentheses, dashes, or commas') and found
    TVD 0.03 - negligible, and if anything tilted toward human writing. Do not
    add a frequency-based em-dash detector on the strength of that paper."""
    text = (
        "The service degraded at 14:02 — a config push, not a deploy — and "
        "recovered by 14:11. The root cause — a missing timeout — was fixed "
        "the same day, and the postmortem — three paragraphs, no blame — "
        "went out that afternoon."
    )
    report = score_text(text)
    assert report.total == 0, report.as_dict(with_hits=True)


def test_short_fragments_alone_are_not_penalised():
    """The paper found sentence fragments run the OPPOSITE direction from folk
    wisdom: present and stylistically significant in 85% of AI passages versus
    67% of human ones. A punchy fragment is not evidence of a human hand, and
    the scorer must not reward choppiness as if it were."""
    text = "Shipped Tuesday. Broke Wednesday. Fixed by lunch. Nobody was happy about it."
    assert score_text(text).total == 0
