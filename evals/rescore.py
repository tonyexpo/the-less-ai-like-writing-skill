#!/usr/bin/env python3
"""Rebuild evals/results/latest.json from raw revision text already on disk,
using the current scorer. No model calls.

Useful after a scorer/pattern change that doesn't require new generations: the
raw text under evals/results/raw/ is real, already-paid-for model output: any
future -unrelated- scoring change can be re-applied to it for free instead of
re-running the eval. It is also how this repo went from twelve to sixteen
categories without regenerating the `baseline`/`generic` arms, since neither
arm's system prompt depends on SKILL.md content - only `skill` needed fresh
generations (see evals/README.md for that reasoning in full).

    python evals/rescore.py                       # rebuild latest.json
    python evals/rescore.py --check                # report drift, write nothing, exit 1 if found
    python evals/rescore.py --model sonnet --repeats 3

This will happily rescore text that is stale relative to the *current*
SKILL.md - it has no way to know that from the text alone. What it CAN check:
whether the `skill`-arm raw text on disk was generated against a different
SKILL.md than the one on disk right now, by comparing sha256(SKILL.md) against
the `meta.skill_sha256` already stored in the previous latest.json (the sha
recorded the last time this file - or run_eval.py - wrote one). That is only
evidence of drift since the *last write*, not a general guarantee: if nothing
is stored yet, or the stored sha itself predates this field existing, there is
nothing to compare against and no warning is possible - regenerate with
`run_eval.py --arms skill --save-raw` if in doubt.

--check is a dry run: it always reports the drift status and exits 1 if any
was found, 0 otherwise, and never writes `--out` either way - safe to call in
CI without touching a tracked results file. Without --check, drift merely
prints a warning (results are written regardless).
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evals.run_eval import ARMS, summarise  # noqa: E402
from tools.patterns import CATEGORIES  # noqa: E402
from tools.slopscore import score_text  # noqa: E402

RAW_DIR = REPO_ROOT / "evals/results/raw"
DRAFT_DIR = REPO_ROOT / "evals/drafts"
DEFAULT_OUT = REPO_ROOT / "evals/results/latest.json"
SKILL_PATH = REPO_ROOT / "SKILL.md"

FNAME_RE = re.compile(r"^(?P<draft>[a-z0-9-]+)\.(?P<arm>baseline|generic|skill)\.(?P<rep>\d+)\.md$")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", default="sonnet", help="recorded in meta.model - does not affect scoring")
    parser.add_argument("--repeats", type=int, default=3, help="recorded in meta.repeats")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check", action="store_true", help="dry run: report drift, write nothing, exit 1 if drift found"
    )
    args = parser.parse_args(argv)

    draft_texts = {p.stem: p.read_text(encoding="utf-8") for p in sorted(DRAFT_DIR.glob("*.md"))}
    if not draft_texts:
        parser.error(f"no drafts in {DRAFT_DIR}")
    draft_reports = {stem: score_text(text) for stem, text in draft_texts.items()}
    draft_scores = {stem: r.total for stem, r in draft_reports.items()}

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    current_sha = hashlib.sha256(skill_text.encode()).hexdigest()[:16]
    prior_sha = None
    if args.out.exists():
        with contextlib.suppress(json.JSONDecodeError, KeyError):
            prior_sha = json.loads(args.out.read_text(encoding="utf-8"))["meta"].get("skill_sha256")

    records = []
    skipped = 0
    for path in sorted(RAW_DIR.glob("*.md")):
        m = FNAME_RE.match(path.name)
        if not m or m["draft"] not in draft_scores:
            skipped += 1
            continue
        draft_id, arm, rep = m["draft"], m["arm"], int(m["rep"])
        report = score_text(path.read_text(encoding="utf-8"))
        records.append(
            {
                "draft_id": draft_id,
                "draft_score": draft_scores[draft_id],
                "arm": arm,
                "rep": rep,
                "seconds": None,
                "error": None,
                "words": report.words,
                "total": report.total,
                "band": report.band,
                "categories": {c.key: c.score for c in report.categories},
                "counts": {c.key: c.count for c in report.categories},
            }
        )
    if skipped:
        print(f"skipped {skipped} file(s) with no matching frozen draft", file=sys.stderr)
    if not records:
        parser.error(f"no matching raw text under {RAW_DIR}")

    drift = prior_sha is not None and prior_sha != current_sha
    skill_arm_count = sum(1 for r in records if r["arm"] == "skill")
    drift_message = (
        f"{skill_arm_count} 'skill' arm file(s) on disk were generated against a SKILL.md whose "
        f"sha256 was {prior_sha}; the current SKILL.md hashes to {current_sha}. Their scores are "
        "still whatever the current scorer sees in that text, but the text itself may not reflect "
        "the SKILL.md you're about to commit. Regenerate with "
        "`python evals/run_eval.py --arms skill --save-raw` if that matters here."
        if drift and skill_arm_count
        else None
    )
    if drift_message:
        print(f"::warning:: {drift_message}", file=sys.stderr)

    if args.check:
        # A dry run: report drift status, touch nothing, exit non-zero only
        # if drift was actually found (not merely "unknown" - see the
        # docstring for what this can and can't detect).
        print("no drift detected" if not drift_message else "drift detected", file=sys.stderr)
        return 1 if drift_message else 0

    records.sort(key=lambda r: (r["draft_id"], r["arm"], r["rep"]))
    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "model": args.model,
            "repeats": args.repeats,
            "arms": list(ARMS),
            "draft_count": len(draft_texts),
            "skill_sha256": current_sha,
            "scorer_max": 2 * len(CATEGORIES),
            "harness": "claude-code-cli",
            "note": (
                "Rebuilt by evals/rescore.py from raw text already on disk - no new model calls. "
                + (
                    drift_message
                    or "No SKILL.md drift detected between the skill-arm raw text and the SKILL.md committed alongside this file."
                )
            ),
        },
        "summary": summarise(records, draft_reports),
        "runs": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    s = payload["summary"]
    try:
        shown_path = args.out.relative_to(REPO_ROOT)
    except ValueError:
        shown_path = args.out
    print(f"wrote {shown_path}", file=sys.stderr)
    print(f"  runs_ok {s['runs_ok']}  runs_failed {s['runs_failed']}  draft_mean {s['draft_mean']}")
    for arm in ARMS:
        a = s["arms"][arm]
        print(f"  {arm:<10} {a['mean']:>6}  n={a['n']}")
    print(f"  skill_vs_generic {s['skill_vs_generic']:+}  density {s['skill_vs_generic_density']:+}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
