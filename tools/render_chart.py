#!/usr/bin/env python3
"""Render the eval results as SVG bar charts for the README.

No plotting dependency: the charts are hand-built SVG, so CI can regenerate them
without installing anything. Two themes are emitted so the README can serve the
right one with a <picture> element.

    python -m tools.render_chart evals/results/latest.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

SERIES_ORDER = ("draft", "baseline", "generic", "skill")
SERIES_LABEL = {
    "draft": "original draft",
    "baseline": "revised, no guidance",
    "generic": "revised, generic advice",
    "skill": "revised with the skill",
}

THEMES = {
    "light": {
        "bg": "#ffffff",
        "grid": "#d8dee4",
        "text": "#1f2328",
        "muted": "#59636e",
        "series": {"draft": "#8c959f", "baseline": "#d1495b", "generic": "#c9852a", "skill": "#2f7d4f"},
    },
    "dark": {
        "bg": "#0d1117",
        "grid": "#30363d",
        "text": "#e6edf3",
        "muted": "#9198a1",
        "series": {"draft": "#6e7681", "baseline": "#f0788a", "generic": "#d29922", "skill": "#57ab5a"},
    },
}


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


@dataclass
class Row:
    label: str
    sublabel: str
    values: dict[str, float]


def _chart(
    rows: list[Row],
    series: list[str],
    title: str,
    subtitle: str,
    footnote: str,
    theme: dict,
    axis_max: float,
    axis_label: str,
) -> str:
    left, right, top, bottom = 196, 62, 92, 62
    bar_h, gap = 9, 2.5
    row_h = len(series) * (bar_h + gap) + 15
    width = 780
    plot_w = width - left - right
    height = top + int(row_h * len(rows)) + bottom

    def x(value: float) -> float:
        return left + (max(value, 0) / axis_max) * plot_w

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        "<style>"
        "text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}"
        ".t{font-size:15px;font-weight:600}.s{font-size:11.5px}.l{font-size:12px}"
        ".n{font-size:10px}.a{font-size:10.5px}"
        "</style>",
        f'<rect width="{width}" height="{height}" fill="{theme["bg"]}"/>',
        f'<text class="t" x="24" y="30" fill="{theme["text"]}">{esc(title)}</text>',
        f'<text class="s" x="24" y="49" fill="{theme["muted"]}">{esc(subtitle)}</text>',
    ]

    lx = 24
    for key in series:
        out.append(
            f'<rect x="{lx}" y="{top - 26}" width="10" height="10" rx="2" fill="{theme["series"][key]}"/>'
        )
        out.append(
            f'<text class="a" x="{lx + 14}" y="{top - 17}" fill="{theme["muted"]}">'
            f"{esc(SERIES_LABEL.get(key, key))}</text>"
        )
        lx += 14 + int(6.0 * len(SERIES_LABEL.get(key, key))) + 22

    step = 4 if axis_max > 8 else 0.5
    tick = 0.0
    while tick <= axis_max + 1e-9:
        gx = x(tick)
        out.append(
            f'<line x1="{gx:.1f}" y1="{top - 6}" x2="{gx:.1f}" y2="{height - bottom + 6}" '
            f'stroke="{theme["grid"]}" stroke-width="1"/>'
        )
        out.append(
            f'<text class="a" x="{gx:.1f}" y="{height - bottom + 20}" text-anchor="middle" '
            f'fill="{theme["muted"]}">{tick:g}</text>'
        )
        tick += step

    out.append(
        f'<text class="a" x="{left + plot_w / 2:.1f}" y="{height - bottom + 38}" text-anchor="middle" '
        f'fill="{theme["muted"]}">{esc(axis_label)}</text>'
    )
    if footnote:
        out.append(f'<text class="a" x="24" y="{height - 12}" fill="{theme["muted"]}">{esc(footnote)}</text>')

    for index, row in enumerate(rows):
        y0 = top + index * row_h
        out.append(
            f'<text class="l" x="{left - 12}" y="{y0 + 10}" text-anchor="end" '
            f'fill="{theme["text"]}">{esc(row.label)}</text>'
        )
        if row.sublabel:
            out.append(
                f'<text class="a" x="{left - 12}" y="{y0 + 23}" text-anchor="end" '
                f'fill="{theme["muted"]}">{esc(row.sublabel)}</text>'
            )
        for offset, key in enumerate(series):
            value = row.values.get(key, 0.0)
            by = y0 + offset * (bar_h + gap)
            w = max(x(value) - left, 1.0)
            out.append(
                f'<rect x="{left}" y="{by:.1f}" width="{w:.1f}" height="{bar_h}" rx="2" '
                f'fill="{theme["series"][key]}"/>'
            )
            out.append(
                f'<text class="n" x="{left + w + 5:.1f}" y="{by + bar_h - 1:.1f}" '
                f'fill="{theme["muted"]}">{value:g}</text>'
            )

    out.append("</svg>")
    return "\n".join(out) + "\n"


def _subtitle(meta: dict, extra: str = "") -> str:
    return (
        f"{meta['model']} via the Claude Code CLI - {meta['repeats']} revisions per draft per arm"
        + (f" - {extra}" if extra else "")
        + f" - {meta['generated_at'][:10]}"
    )


def by_draft_chart(data: dict, theme: dict) -> str:
    summary, meta = data["summary"], data["meta"]
    series = ["draft", *meta["arms"]]
    rows = [Row(label=draft_id, sublabel="", values=entry) for draft_id, entry in summary["by_draft"].items()]
    rows.sort(key=lambda r: -r.values.get("draft", 0))
    return _chart(
        rows,
        series,
        "How much slop each revision arm removes",
        _subtitle(meta),
        "Lower is better. The gap that matters is generic advice vs the skill.",
        theme,
        axis_max=24,
        axis_label="slopscore (0-24, sum of twelve audit categories)",
    )


def by_category_chart(data: dict, theme: dict) -> str:
    summary, meta = data["summary"], data["meta"]
    series = ["draft", *meta["arms"]]
    rows = [Row(label=entry["name"], sublabel="", values=entry) for entry in summary["by_category"].values()]
    rows.sort(key=lambda r: -(r.values.get("draft", 0) - r.values.get("skill", 0)))
    axis_max = max(2.0, max((r.values.get("draft", 0) for r in rows), default=2.0))
    return _chart(
        rows,
        series,
        "Which patterns each arm actually removes",
        _subtitle(meta),
        "Mean category score: 0 absent, 1 occasional, 2 frequent.",
        theme,
        axis_max=axis_max,
        axis_label="mean category score",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render eval results as SVG charts.")
    parser.add_argument("results", type=Path, nargs="?", default=Path("evals/results/latest.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("assets"))
    args = parser.parse_args(argv)

    data = json.loads(args.results.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for name, builder in (("by-draft", by_draft_chart), ("by-category", by_category_chart)):
        for theme_name, theme in THEMES.items():
            path = args.out_dir / f"slopscore-{name}-{theme_name}.svg"
            path.write_text(builder(data, theme), encoding="utf-8")
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
