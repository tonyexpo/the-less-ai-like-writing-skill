#!/usr/bin/env python3
"""Measure what the skill removes from a fixed set of AI-slop drafts.

Three arms revise the same frozen drafts with the same user instruction. The
only thing that changes is what the system prompt carries:

    baseline  nothing beyond the revision instruction
    generic   a short paragraph of ordinary writing advice
    skill     the full SKILL.md

The ``generic`` arm is the one that makes the result mean anything. Without it
the benchmark cannot tell the skill apart from the general effect of pasting
some style guidance into the prompt, and a 12 KB instruction beating an empty
one is not a finding.

Read evals/README.md before quoting any number from this: the harness runs
through the Claude Code CLI, which contributes a system prompt of its own to
every arm, and that is a real limit on what the comparison can show.

    python evals/run_eval.py --repeats 3
    python evals/run_eval.py --drafts blog-ai-education --repeats 1
    python evals/run_eval.py --gate-delta 2.0
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.patterns import CATEGORIES  # noqa: E402
from tools.slopscore import score_text  # noqa: E402

SKILL_PATH = REPO_ROOT / "SKILL.md"
DRAFT_DIR = REPO_ROOT / "evals/drafts"
DEFAULT_OUT = REPO_ROOT / "evals/results/latest.json"

INSTRUCTION = (
    "Revise the draft below so it reads better. Keep the author's meaning and "
    "every factual claim as they are: do not add facts, sources, numbers or "
    "anecdotes that are not already in the draft. Return only the revised text, "
    "with no commentary.\n\n---\n\n"
)

# The control arm: the sort of guidance someone would write in one sitting
# without this repository. Short on purpose - it is a floor, not a straw man.
GENERIC_ADVICE = (
    "You are an experienced copy editor. Make writing clear and concrete. Prefer "
    "plain words and simple verbs, cut padding and filler, avoid cliches and "
    "marketing language, vary sentence length, and do not pad the ending. Keep "
    "the author's meaning and facts unchanged."
)

ARMS = ("baseline", "generic", "skill")


def system_prompt_for(arm: str, skill: str) -> str | None:
    return {"baseline": None, "generic": GENERIC_ADVICE, "skill": skill}[arm]


def call_model(draft: str, arm: str, model: str, skill: str, timeout: int) -> tuple[str, float, str | None]:
    command = ["claude", "-p", INSTRUCTION + draft, "--model", model, "--allowed-tools", ""]
    extra = system_prompt_for(arm, skill)
    if extra:
        command += ["--append-system-prompt", extra]
    started = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=REPO_ROOT)
    except subprocess.TimeoutExpired:
        return "", time.monotonic() - started, f"timed out after {timeout}s"
    elapsed = time.monotonic() - started
    if result.returncode != 0:
        return "", elapsed, (result.stderr or "").strip()[:400] or f"exit {result.returncode}"
    return result.stdout.strip(), elapsed, None


def mean(values: list[float]) -> float:
    return round(statistics.fmean(values), 2) if values else 0.0


def summarise(records: list[dict], draft_reports: dict) -> dict:
    ok = [r for r in records if not r["error"]]
    drafts = {stem: report.total for stem, report in draft_reports.items()}
    draft_mean = mean(list(drafts.values()))

    def density(records_in: list[dict]) -> float:
        rates = [sum(r["counts"].values()) / r["words"] * 100 for r in records_in if r["words"]]
        return mean(rates)

    draft_density = mean(
        [
            sum(c.count for c in report.categories) / report.words * 100
            for report in draft_reports.values()
            if report.words
        ]
    )

    arms = {}
    for arm in ARMS:
        rows = [r for r in ok if r["arm"] == arm]
        totals = [r["total"] for r in rows]
        arms[arm] = {
            "mean": mean(totals),
            "removed_from_draft": round(draft_mean - mean(totals), 2),
            # The skill also shortens the text, and shorter text trips fewer
            # patterns outright. Hits per 100 words is the length-adjusted view;
            # quote it alongside the score, never instead of it.
            "hits_per_100w": density(rows),
            "n": len(totals),
        }

    by_category = {}
    for key, name in CATEGORIES.items():
        entry = {
            "name": name,
            "draft": mean([r.score_of(key) for r in draft_reports.values()]),
        }
        for arm in ARMS:
            entry[arm] = mean([r["categories"][key] for r in ok if r["arm"] == arm])
        by_category[key] = entry

    by_draft = {}
    for draft_id, draft_score in drafts.items():
        entry = {"draft": draft_score}
        for arm in ARMS:
            entry[arm] = mean([r["total"] for r in ok if r["draft_id"] == draft_id and r["arm"] == arm])
        by_draft[draft_id] = entry

    return {
        "runs_ok": len(ok),
        "runs_failed": len(records) - len(ok),
        "draft_mean": draft_mean,
        "draft_hits_per_100w": draft_density,
        "arms": arms,
        # The number worth quoting: how much better the skill is than ordinary
        # writing advice, not how much better it is than nothing.
        "skill_vs_generic": round(arms["generic"]["mean"] - arms["skill"]["mean"], 2),
        "skill_vs_baseline": round(arms["baseline"]["mean"] - arms["skill"]["mean"], 2),
        "skill_vs_generic_density": round(
            arms["generic"]["hits_per_100w"] - arms["skill"]["hits_per_100w"], 2
        ),
        "mean_words": {arm: mean([r["words"] for r in ok if r["arm"] == arm]) for arm in ARMS},
        "by_category": by_category,
        "by_draft": by_draft,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure what the skill removes from AI-slop drafts.")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--repeats", type=int, default=3, help="samples per draft per arm")
    parser.add_argument("--drafts", default="", help="comma-separated draft ids (default: all)")
    parser.add_argument("--arms", default=",".join(ARMS), help="comma-separated arms to run")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--save-raw", action="store_true")
    parser.add_argument(
        "--gate-delta",
        type=float,
        default=None,
        metavar="N",
        help="exit 1 unless the skill beats the generic-advice arm by at least N points",
    )
    args = parser.parse_args(argv)

    skill = SKILL_PATH.read_text(encoding="utf-8")
    paths = sorted(DRAFT_DIR.glob("*.md"))
    if args.drafts:
        wanted = {d.strip() for d in args.drafts.split(",") if d.strip()}
        paths = [p for p in paths if p.stem in wanted]
    if not paths:
        parser.error(f"no drafts in {DRAFT_DIR}; run evals/make_drafts.py first")

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = set(arms) - set(ARMS)
    if unknown:
        parser.error(f"unknown arms: {', '.join(sorted(unknown))}")

    texts = {p.stem: p.read_text(encoding="utf-8") for p in paths}
    draft_reports = {stem: score_text(text) for stem, text in texts.items()}
    drafts = {stem: report.total for stem, report in draft_reports.items()}

    jobs = [(stem, arm, rep) for stem in texts for arm in arms for rep in range(args.repeats)]
    print(
        f"{len(jobs)} revisions: {len(texts)} drafts x {len(arms)} arms x {args.repeats} reps",
        file=sys.stderr,
    )

    def work(job):
        stem, arm, rep = job
        text, seconds, error = call_model(texts[stem], arm, args.model, skill, args.timeout)
        return stem, arm, rep, text, seconds, error

    records: list[dict] = []
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for done, (stem, arm, rep, text, seconds, error) in enumerate(pool.map(work, jobs), start=1):
            report = score_text(text) if text else None
            records.append(
                {
                    "draft_id": stem,
                    "draft_score": drafts[stem],
                    "arm": arm,
                    "rep": rep,
                    "seconds": round(seconds, 1),
                    "error": error,
                    "words": report.words if report else 0,
                    "total": report.total if report else None,
                    "band": report.band if report else None,
                    "categories": {c.key: c.score for c in report.categories} if report else {},
                    "counts": {c.key: c.count for c in report.categories} if report else {},
                }
            )
            print(
                f"  [{done}/{len(jobs)}] {stem:<20} {arm:<9} "
                f"{error or f'{drafts[stem]} -> {report.total}/24'}",
                file=sys.stderr,
            )
            if args.save_raw and text:
                raw = args.out.parent / "raw" / f"{stem}.{arm}.{rep}.md"
                raw.parent.mkdir(parents=True, exist_ok=True)
                raw.write_text(text + "\n", encoding="utf-8")

    records.sort(key=lambda r: (r["draft_id"], r["arm"], r["rep"]))
    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "model": args.model,
            "repeats": args.repeats,
            "arms": arms,
            "draft_count": len(texts),
            "skill_sha256": hashlib.sha256(skill.encode()).hexdigest()[:16],
            "scorer_max": 2 * len(CATEGORIES),
            "harness": "claude-code-cli",
        },
        "summary": summarise(records, draft_reports),
        "runs": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    summary = payload["summary"]
    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"  drafts in           {summary['draft_mean']:>5}")
    for arm in arms:
        print(f"  {arm:<19} {summary['arms'][arm]['mean']:>5}")
    print(f"  skill vs generic    {summary['skill_vs_generic']:>+5}")
    if summary["runs_failed"]:
        print(f"  {summary['runs_failed']} revision(s) failed", file=sys.stderr)

    if args.gate_delta is not None:
        actual = summary["skill_vs_generic"]
        if actual < args.gate_delta:
            print(f"\ngate failed: skill vs generic {actual} < required {args.gate_delta}", file=sys.stderr)
            return 1
        print(f"\ngate passed: skill vs generic {actual} >= {args.gate_delta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
