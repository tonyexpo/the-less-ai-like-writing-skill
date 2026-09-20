"""tools/render_chart.py had zero test coverage before this file. That is how
the chart's x-axis ended up hardcoded to 24 (the old max score) and silently
wrong the moment a category was added and the real max became 32 - the axis
label lied and, worse, would have clipped any bar past 24 without complaint.

These tests exist so a future change to the category count fails loudly here
instead of shipping a wrong chart.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tools.patterns import CATEGORIES
from tools.render_chart import THEMES, by_category_chart, by_draft_chart, main

REPO_ROOT = Path(__file__).resolve().parent.parent
LATEST = REPO_ROOT / "evals/results/latest.json"


def _fake_data(scorer_max: int) -> dict:
    """A minimal, schema-correct results payload for a hypothetical scorer
    with a different category count, so the chart is tested against more than
    just whatever the current live category count happens to be."""
    return {
        "meta": {
            "model": "sonnet",
            "repeats": 3,
            "arms": ["baseline", "generic", "skill"],
            "generated_at": "2026-01-01T00:00:00Z",
            "scorer_max": scorer_max,
        },
        "summary": {
            "by_draft": {
                "example": {"draft": scorer_max - 1, "baseline": 8, "generic": 7, "skill": 3},
            },
            "by_category": {
                "made_up_category": {
                    "name": "Made-up category",
                    "draft": 2,
                    "baseline": 1,
                    "generic": 1,
                    "skill": 0,
                },
            },
        },
    }


@pytest.mark.parametrize("scorer_max", [24, 32, 40])
def test_by_draft_axis_tracks_scorer_max(scorer_max):
    """The regression test for the actual bug: the axis must scale with
    whatever scorer produced the data, not with a number written down once."""
    svg = by_draft_chart(_fake_data(scorer_max), THEMES["light"])
    assert f"0-{scorer_max}" in svg
    assert f"sum of {scorer_max // 2} audit categories" in svg
    # The old hardcoded value must not leak in when the real max is different.
    if scorer_max != 24:
        assert "0-24" not in svg


def test_by_draft_chart_is_well_formed_svg():
    svg = by_draft_chart(_fake_data(32), THEMES["light"])
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")


def test_by_category_chart_is_well_formed_svg():
    svg = by_category_chart(_fake_data(32), THEMES["dark"])
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")


def _svg_declared_height(svg: str) -> int:
    root = ET.fromstring(svg)
    return int(root.get("height"))


def _rows_of(n: int) -> dict:
    return {
        f"cat_{i}": {"name": f"Category {i}", "draft": 2, "baseline": 1, "generic": 1, "skill": 0}
        for i in range(n)
    }


def test_chart_height_grows_with_row_count_not_a_hardcoded_bar_count():
    """A chart with more rows than the current live category count must still
    render, and be tall enough to hold them - nothing here should be sized
    for exactly 12 or 16. Checking that every label string merely *appears
    somewhere* in the SVG (the original version of this test) would pass even
    if rows were drawn stacked on top of each other outside the canvas."""
    small = _fake_data(32)
    small["summary"]["by_category"] = _rows_of(5)
    large = _fake_data(32)
    large["summary"]["by_category"] = _rows_of(20)

    svg_small = by_category_chart(small, THEMES["light"])
    svg_large = by_category_chart(large, THEMES["light"])

    for i in range(20):
        assert f"Category {i}" in svg_large

    height_small = _svg_declared_height(svg_small)
    height_large = _svg_declared_height(svg_large)
    # 20 rows is 4x the rows of 5; fixed top/bottom margins mean the total
    # height grows a bit slower than a full 4x, but it must grow well past
    # "somewhat bigger" - a fixed-size canvas with clipped overflow would
    # produce a small, constant difference here instead.
    assert height_large > height_small * 2.5, (height_small, height_large)

    # The last row's own y-coordinate must fall inside the declared canvas -
    # a row positioned past the bottom would still match the string-contains
    # check above while being invisible in any renderer.
    last_label_y = max(int(y) for y in re.findall(r'class="l"[^>]*\by="(\d+)', svg_large))
    assert last_label_y < height_large, "last row's label falls outside the declared SVG height"


def test_live_charts_match_the_live_scorer():
    """The committed evals/results/latest.json should describe exactly as
    many categories as tools/patterns.py currently defines - if this drifts,
    the chart axis is describing a scorer that no longer exists."""
    if not LATEST.exists():
        pytest.skip("no committed eval results to check")
    meta = json.loads(LATEST.read_text(encoding="utf-8"))["meta"]
    assert meta["scorer_max"] == 2 * len(CATEGORIES), (
        "evals/results/latest.json was generated by a different category count "
        "than tools/patterns.py currently defines - regenerate it with "
        "`python evals/run_eval.py` (or rescore the existing raw texts) and "
        "`python -m tools.render_chart`"
    )


def test_main_writes_all_four_files(tmp_path):
    out_dir = tmp_path / "assets"
    results = tmp_path / "latest.json"
    results.write_text(json.dumps(_fake_data(32)), encoding="utf-8")
    assert main([str(results), "--out-dir", str(out_dir)]) == 0
    written = sorted(p.name for p in out_dir.glob("*.svg"))
    assert written == [
        "slopscore-by-category-dark.svg",
        "slopscore-by-category-light.svg",
        "slopscore-by-draft-dark.svg",
        "slopscore-by-draft-light.svg",
    ]
