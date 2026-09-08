"""The skill file is the product. These tests keep it loadable and in sync
with the scorer.

The important one is ``test_audit_categories_match_scorer``: if someone adds a
thirteenth category to the audit in SKILL.md without teaching the scorer about
it, the suite fails instead of silently under-reporting.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.patterns import CATEGORIES

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "SKILL.md"
SKILL_TEXT = SKILL_PATH.read_text(encoding="utf-8")

# Claude Skills frontmatter limits.
MAX_NAME = 64
MAX_DESCRIPTION = 1024


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError("SKILL.md must open with a YAML frontmatter block")
    fields: dict[str, str] = {}
    key = None
    for line in match.group(1).splitlines():
        if re.match(r"^\s+", line) and key:
            fields[key] += " " + line.strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip()
    return fields


FRONTMATTER = parse_frontmatter(SKILL_TEXT)


def test_frontmatter_has_required_fields():
    assert set(FRONTMATTER) >= {"name", "description"}


def test_name_matches_repository_directory():
    assert FRONTMATTER["name"] == REPO_ROOT.name


def test_name_is_a_valid_skill_slug():
    name = FRONTMATTER["name"]
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), name
    assert len(name) <= MAX_NAME


def test_description_is_present_and_within_limits():
    description = FRONTMATTER["description"]
    assert 40 <= len(description) <= MAX_DESCRIPTION
    assert description[0].isupper()


@pytest.mark.parametrize(
    "heading",
    [
        "Core Principle",
        "Primary AI-Like Patterns",
        "Human-Like Counterpatterns",
        "Generation Workflow",
        "Revision Workflow",
        "AI-Likeness Audit",
        "Anti-Patterns for This Skill",
        "Compact Prompt Version",
        "Final Quality Test",
    ],
)
def test_required_section_present(heading):
    assert re.search(rf"^#+\s+{re.escape(heading)}\s*$", SKILL_TEXT, re.MULTILINE)


def audit_categories() -> list[str]:
    section = re.search(r"^## AI-Likeness Audit\s*$(.*?)^## ", SKILL_TEXT, re.MULTILINE | re.DOTALL)
    assert section, "AI-Likeness Audit section not found"
    return re.findall(r"^\d+\.\s+(.+?)\s*$", section.group(1), re.MULTILINE)


def test_audit_lists_twelve_categories():
    assert len(audit_categories()) == len(CATEGORIES) == 12


def test_audit_categories_match_scorer():
    """The audit in SKILL.md and the scorer's categories are the same list,
    in the same order."""
    assert audit_categories() == list(CATEGORIES.values())


def test_scoring_bands_documented_in_skill():
    for band in ("0–5", "6–11", "12+"):  # noqa: RUF001 - en dashes quoted from SKILL.md
        assert band in SKILL_TEXT, f"band {band} missing from SKILL.md"


def test_skill_refuses_to_promise_detector_evasion():
    """The skill must not claim it defeats AI detectors. Guard the claim, not
    the wording, by requiring the disclaimer and rejecting the promise."""
    assert re.search(r"not a detector-evasion trick", SKILL_TEXT, re.IGNORECASE)
    forbidden = [
        r"undetectable",
        r"bypass\s+(?:ai\s+)?detect",
        r"defeat\s+(?:ai\s+)?detect(?:ors|ion)\b(?!\w)",
        r"guarantee\w*\s+(?:that\s+)?(?:the\s+)?text\s+will\s+pass",
    ]
    for pattern in forbidden:
        for match in re.finditer(pattern, SKILL_TEXT, re.IGNORECASE):
            line_start = SKILL_TEXT.rfind("\n", 0, match.start()) + 1
            line = SKILL_TEXT[line_start : SKILL_TEXT.find("\n", match.start())]
            # A negated mention ("must not rely on", "Do not claim") is fine.
            assert re.search(r"\b(?:not|never|cannot|no)\b", line, re.IGNORECASE), (
                f"SKILL.md appears to promise detector evasion: {line.strip()!r}"
            )
