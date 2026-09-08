#!/usr/bin/env python3
"""Score a text for the AI-like patterns catalogued in SKILL.md.

The scale is the one in the skill's own audit: each of twelve categories gets
0 (absent), 1 (occasional) or 2 (frequent), for a total of 0-24.

    0-5   low density of common AI-like patterns
    6-11  revise the most repetitive patterns
    12+   substantial rewrite recommended

This is a writing heuristic, not an AI detector. A low score means the text
avoids a specific list of tells; it says nothing about who wrote it.

Usage:
    python -m tools.slopscore draft.md
    python -m tools.slopscore --json draft.md
    cat draft.md | python -m tools.slopscore -
    python -m tools.slopscore --max-score 5 draft.md   # exit 1 if above
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools.patterns import (
    CATEGORIES,
    COMPLETENESS_SECTIONS,
    LEXICAL,
    STRUCTURAL,
    SUPPORTED_LANGUAGES,
    SYNONYM_CLUSTERS,
)

# Minimum hits before a category scores at all. One three-item list is ordinary
# English; a habit of them is the tell, and SKILL.md asks for the number of items
# the content requires rather than banning the shape. Everything else trips on
# the first hit.
CATEGORY_FLOORS: dict[str, int] = {"rule_of_three": 2}

# A category counted this many times per 100 words is "frequent" (score 2).
FREQUENT_RATE = 1.0
# ...or this many raw hits, whichever comes first. Short texts can be dense
# without reaching the rate threshold on a small denominator.
FREQUENT_COUNT = 4

BANDS = ((5, "low"), (11, "revise"), (24, "rewrite"))

_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_WORD_RE = re.compile(r"\b[\w'-]+\b")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S", re.MULTILINE)
_BOLD_LEADIN_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*\n]+\*\*\s*[:—-]", re.MULTILINE)


@dataclass(frozen=True)
class Hit:
    """One match of one pattern."""

    category: str
    line: int
    text: str
    pattern: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class CategoryScore:
    key: str
    name: str
    count: int
    rate: float
    score: int
    hits: list[Hit] = field(default_factory=list)

    def as_dict(self, with_hits: bool = True) -> dict:
        out = {
            "key": self.key,
            "name": self.name,
            "count": self.count,
            "rate": round(self.rate, 3),
            "score": self.score,
        }
        if with_hits:
            out["hits"] = [h.as_dict() for h in self.hits]
        return out


@dataclass
class Report:
    words: int
    total: int
    band: str
    categories: list[CategoryScore]

    @property
    def by_key(self) -> dict[str, CategoryScore]:
        return {c.key: c for c in self.categories}

    def score_of(self, key: str) -> int:
        return self.by_key[key].score

    def count_of(self, key: str) -> int:
        return self.by_key[key].count

    def as_dict(self, with_hits: bool = True) -> dict:
        return {
            "words": self.words,
            "total": self.total,
            "max_total": 2 * len(CATEGORIES),
            "band": self.band,
            "categories": [c.as_dict(with_hits) for c in self.categories],
        }


def _compile(lang: str) -> dict[str, list[re.Pattern[str]]]:
    if lang not in LEXICAL:
        raise ValueError(f"unsupported language {lang!r}; available: {', '.join(SUPPORTED_LANGUAGES)}")
    compiled: dict[str, list[re.Pattern[str]]] = {}
    for category, patterns in LEXICAL[lang].items():
        compiled[category] = [re.compile(p if p.startswith("(?") else f"(?i){p}") for p in patterns]
    return compiled


def strip_code(text: str) -> str:
    """Blank out fenced and inline code so examples don't count as prose.

    Newlines are preserved so line numbers in hits stay accurate.
    """

    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    return _INLINE_CODE_RE.sub(blank, _FENCE_RE.sub(blank, text))


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text))


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _lexical_hits(text: str, compiled: dict[str, list[re.Pattern[str]]]) -> dict[str, list[Hit]]:
    hits: dict[str, list[Hit]] = {key: [] for key in CATEGORIES}
    for category, patterns in compiled.items():
        seen: set[tuple[int, int]] = set()
        for pattern in patterns:
            for match in pattern.finditer(text):
                span = match.span()
                if span in seen:
                    continue
                seen.add(span)
                hits[category].append(
                    Hit(
                        category=category,
                        line=_line_of(text, span[0]),
                        text=" ".join(match.group(0).split())[:120],
                        pattern=pattern.pattern,
                    )
                )
    return hits


def _structuring_hits(text: str) -> list[Hit]:
    """Category 8: structure used as decoration rather than navigation.

    One hit per structural excess, so a document can accumulate them the way a
    reader accumulates the impression of a miniature report.
    """
    hits: list[Hit] = []
    words = max(count_words(text), 1)
    headings = _HEADING_RE.findall(text)

    # More than one heading per 120 words reads as a heading for every idea.
    heading_budget = max(1, words // 120)
    for extra in range(len(headings) - heading_budget):
        _level, title = headings[heading_budget + extra]
        hits.append(Hit("over_structuring", 0, f"heading: {title}"[:120], "heading-density"))

    bullets = _BULLET_RE.findall(text)
    bullet_budget = max(3, words // 60)
    for _ in range(len(bullets) - bullet_budget):
        hits.append(Hit("over_structuring", 0, "bullet beyond budget", "bullet-density"))

    for match in _BOLD_LEADIN_RE.finditer(text):
        hits.append(
            Hit(
                "over_structuring",
                _line_of(text, match.start()),
                " ".join(match.group(0).split())[:120],
                "bold-leadin-colon",
            )
        )

    # Title Case headings ("The Early Years And Political Rise").
    for match in _HEADING_RE.finditer(text):
        title = match.group(2)
        content = [w for w in title.split() if w.isalpha() and len(w) > 3]
        if len(content) >= 3 and all(w[0].isupper() for w in content):
            hits.append(
                Hit(
                    "over_structuring",
                    _line_of(text, match.start()),
                    f"title case: {title}"[:120],
                    "title-case-heading",
                )
            )
    return hits


def _completeness_hits(text: str, lang: str) -> list[Hit]:
    """Category 12: the canned Intro -> Benefits -> Challenges -> Future skeleton."""
    section_res = [re.compile(p, re.IGNORECASE) for p in COMPLETENESS_SECTIONS[lang]]
    hits: list[Hit] = []
    for match in _HEADING_RE.finditer(text):
        title = match.group(2).strip().strip(":").strip()
        title = re.sub(r"^\d+[.)]\s*", "", title)
        title = re.sub(r"[*_`]", "", title).strip()
        if any(r.match(title) for r in section_res):
            hits.append(
                Hit(
                    "artificial_completeness",
                    _line_of(text, match.start()),
                    f"section: {title}"[:120],
                    "canned-section",
                )
            )
    if re.search(r"(?i)\bpros\s+and\s+cons\b", text):
        hits.append(Hit("artificial_completeness", 0, "pros and cons", "pros-and-cons"))
    return hits


def _synonym_cycling_hits(text: str, lang: str) -> list[Hit]:
    """Category 6: one referent renamed repeatedly to avoid repetition.

    Detected per cluster: three or more distinct members of the same cluster in
    one text is elegant variation. Known limitation - only the clusters in
    ``patterns.py`` are visible, so domain-specific cycling is missed.
    """
    hits: list[Hit] = []
    for cluster, members in SYNONYM_CLUSTERS[lang].items():
        found: list[tuple[int, str]] = []
        for member in members:
            match = re.search(f"(?i){member}", text)
            if match:
                found.append((match.start(), " ".join(match.group(0).split())))
        if len(found) >= 3:
            for offset, label in sorted(found)[2:]:
                hits.append(
                    Hit("synonym_cycling", _line_of(text, offset), f"{cluster}: {label}", "synonym-cluster")
                )
    return hits


# Categories that need a look at the document's shape rather than its wording.
STRUCTURAL_DETECTORS = {
    "over_structuring": lambda text, _lang: _structuring_hits(text),
    "artificial_completeness": _completeness_hits,
    "synonym_cycling": _synonym_cycling_hits,
}
assert set(STRUCTURAL_DETECTORS) == set(STRUCTURAL), "structural detector table out of sync"


def _score_category(count: int, words: int, floor: int = 1) -> tuple[float, int]:
    rate = (count / words * 100) if words else 0.0
    if count < floor:
        return rate, 0
    if count >= FREQUENT_COUNT + (floor - 1) or (count > floor and rate >= FREQUENT_RATE):
        return rate, 2
    return rate, 1


def _band(total: int) -> str:
    for ceiling, name in BANDS:
        if total <= ceiling:
            return name
    return BANDS[-1][1]


def score_text(text: str, lang: str = "en") -> Report:
    """Score ``text`` and return a full report with per-hit evidence."""
    prose = strip_code(text)
    words = count_words(prose)

    hits = _lexical_hits(prose, _compile(lang))
    for key, detector in STRUCTURAL_DETECTORS.items():
        hits[key] = detector(prose, lang)

    categories: list[CategoryScore] = []
    for key, name in CATEGORIES.items():
        found = sorted(hits[key], key=lambda h: (h.line, h.text))
        rate, score = _score_category(len(found), words, CATEGORY_FLOORS.get(key, 1))
        categories.append(
            CategoryScore(key=key, name=name, count=len(found), rate=rate, score=score, hits=found)
        )

    total = sum(c.score for c in categories)
    return Report(words=words, total=total, band=_band(total), categories=categories)


def score_file(path: str | Path, lang: str = "en") -> Report:
    return score_text(Path(path).read_text(encoding="utf-8"), lang=lang)


def format_report(report: Report, source: str, show_hits: bool = True) -> str:
    lines = [
        f"{source}: {report.total}/{report.as_dict(False)['max_total']} ({report.band}), {report.words} words",
        "",
    ]
    width = max(len(c.name) for c in report.categories)
    for category in report.categories:
        marker = "." if category.score == 0 else ("!" if category.score == 1 else "!!")
        lines.append(
            f"  {marker:<3}{category.name:<{width}}  score {category.score}  "
            f"hits {category.count:<3} ({category.rate:.2f}/100w)"
        )
        if show_hits and category.hits:
            for hit in category.hits[:5]:
                where = f"L{hit.line}" if hit.line else "-"
                lines.append(f"        {where:>6}  {hit.text}")
            if len(category.hits) > 5:
                lines.append(f"        ... {len(category.hits) - 5} more")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="slopscore",
        description="Score text for the AI-like patterns catalogued in SKILL.md.",
    )
    parser.add_argument("paths", nargs="+", metavar="FILE", help="files to score, or - for stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a text report")
    parser.add_argument("--lang", default="en", choices=SUPPORTED_LANGUAGES)
    parser.add_argument("--quiet", action="store_true", help="omit per-hit evidence")
    parser.add_argument(
        "--max-score",
        type=int,
        default=None,
        metavar="N",
        help="exit 1 if any file scores above N",
    )
    args = parser.parse_args(argv)

    reports: list[tuple[str, Report]] = []
    for path in args.paths:
        if path == "-":
            reports.append(("<stdin>", score_text(sys.stdin.read(), lang=args.lang)))
        else:
            reports.append((path, score_file(path, lang=args.lang)))

    if args.json:
        payload = [{"source": src, **rep.as_dict(not args.quiet)} for src, rep in reports]
        print(json.dumps(payload, indent=2))
    else:
        print("\n\n".join(format_report(rep, src, not args.quiet) for src, rep in reports))

    if args.max_score is not None:
        over = [src for src, rep in reports if rep.total > args.max_score]
        if over:
            print(f"\nover the --max-score {args.max_score} limit: {', '.join(over)}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
