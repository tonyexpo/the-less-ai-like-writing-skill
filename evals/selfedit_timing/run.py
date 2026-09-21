#!/usr/bin/env python3
"""Does the Generation Workflow's self-audit step (SKILL.md, step 5 - "Run
the AI-Likeness Audit below") actually work when it runs inside the same
completion as the draft it is meant to check?

Two users reported, independently, that a model cannot reliably self-edit
"mid-task": once text has left the completion, the model cannot go back and
rewrite it in that same stream, only add to it going forward. If that is
right, SKILL.md's Generation Workflow - draft, then self-audit, all in one
response - asks for something a single forward pass cannot really do. The
Revision Workflow (and the existing `skill` arm in evals/run_eval.py) never
tests this, because every call there receives an already-finished draft as
input, in a fresh process, which is architecturally a different situation:
the flawed text is fully present in context *before* generation of the fix
begins, not something the model is still in the middle of emitting.

This script isolates that variable with two conditions over the same topic:

    midtask   ONE claude -p call. System prompt = full SKILL.md. The user
              prompt asks for the piece in a slop-inducing register AND says
              to apply the Generation Workflow's self-audit step within that
              same response.

    twopass   TWO separate claude -p calls, each a fresh process. Call A: no
              skill, same slop-inducing prompt (a raw baseline). Call B:
              fresh process, system prompt = full SKILL.md, standard revision
              instruction + call A's draft. This is exactly what
              evals/run_eval.py's `skill` arm already does.

See results/ for what was actually run and evals/selfedit_timing/README.md
for the write-up and the caveats (small N, and a Haiku-specific instruction-
following confound found and excluded - read it before trusting Haiku
numbers in any results/*.json file that mentions Haiku).

    python evals/selfedit_timing/run.py --topics product-philosophy --models opus --repeats 3
    python evals/selfedit_timing/run.py --topics founder-retrospective,product-philosophy,oped-remote-work --models sonnet --repeats 3
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.slopscore import score_text  # noqa: E402

SKILL_PATH = REPO_ROOT / "SKILL.md"
CONDITIONS = ("midtask", "twopass")

# Same slop-inducing register evals/make_drafts.py uses to calibrate the
# repo's frozen drafts (min score 10/32). Without it, both conditions sit at
# the Claude Code CLI's own clean-by-default floor and there is nothing to
# observe - see evals/README.md's "Why it revises drafts instead of
# generating from scratch", and results/v1_no_register_null.json here, where
# both conditions scored 0-2/32 with no register applied.
SLOP_REGISTER = (
    "Write it in the polished, upbeat register of corporate content marketing: "
    "open by establishing why the topic matters in today's world, add a short "
    "interpretive comment after each fact, use section headings, balanced "
    "three-part lists, and contrast constructions, and close with a forward-looking "
    "conclusion. Keep every claim vague enough to be safe."
)

# Prompt bodies match evals/prompts.json verbatim - reusing genres the repo
# already calibrated rather than inventing new ones.
TOPICS = {
    "founder-retrospective": (
        "Write a 400-word founder's retrospective, in the first person, looking "
        "back on the hard first year of building a small startup."
    ),
    "product-philosophy": (
        "Write a 400-word essay explaining the design philosophy behind why your "
        "engineering team rebuilt its product from the ground up."
    ),
    "oped-remote-work": (
        "Write a 400-word opinion piece arguing that remote work is better for most software teams."
    ),
}

REVISE_INSTRUCTION = (
    "Revise the draft below so it reads better. Keep the author's meaning and "
    "every factual claim as they are: do not add facts, sources, numbers or "
    "anecdotes that are not already in the draft. Return only the revised text, "
    "with no commentary.\n\n---\n\n"
)


def midtask_prompt(topic_sloppy: str) -> str:
    return (
        topic_sloppy + " Apply the Generation Workflow described in the system prompt, including "
        "its self-audit step (running the AI-Likeness Audit against your own draft "
        "before finalizing), entirely within this response. Return only the final "
        "text, with no commentary."
    )


def call(prompt: str, system_prompt: str | None, model: str, timeout: int) -> tuple[str, float, str | None]:
    command = ["claude", "-p", prompt, "--model", model, "--allowed-tools", ""]
    if system_prompt:
        command += ["--append-system-prompt", system_prompt]
    started = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=REPO_ROOT)
    except subprocess.TimeoutExpired:
        return "", time.monotonic() - started, "timeout"
    elapsed = time.monotonic() - started
    if result.returncode != 0:
        return "", elapsed, (result.stderr or "").strip()[:300] or f"exit {result.returncode}"
    return result.stdout.strip(), elapsed, None


def run_midtask(topic_id: str, model: str, rep: int, skill: str, timeout: int) -> dict:
    topic_sloppy = TOPICS[topic_id] + " " + SLOP_REGISTER
    text, secs, err = call(midtask_prompt(topic_sloppy), skill, model, timeout)
    report = score_text(text) if text else None
    return {
        "topic": topic_id,
        "model": model,
        "condition": "midtask",
        "rep": rep,
        "seconds": round(secs, 1),
        "error": err,
        "words": report.words if report else 0,
        "total": report.total if report else None,
        "text": text,
    }


def run_twopass(topic_id: str, model: str, rep: int, skill: str, timeout: int) -> dict:
    topic_sloppy = TOPICS[topic_id] + " " + SLOP_REGISTER
    raw, secs_a, err_a = call(topic_sloppy, None, model, timeout)
    if err_a:
        return {
            "topic": topic_id,
            "model": model,
            "condition": "twopass",
            "rep": rep,
            "seconds": secs_a,
            "error": err_a,
            "words": 0,
            "total": None,
            "text": "",
            "raw_draft_text": "",
        }
    raw_report = score_text(raw)
    # The failure mode found with Haiku: a "raw draft" that is actually a
    # meta-description of the piece rather than the piece itself, which
    # invalidates the comparison for that call. Flag it instead of silently
    # trusting the score - see README.md's Haiku section. raw_draft_text is
    # kept so this can be checked directly instead of inferred from the
    # revision's word count, which is a different call's output.
    suspicious = raw_report.words < 150
    revised, secs_b, err_b = call(REVISE_INSTRUCTION + raw, skill, model, timeout)
    report = score_text(revised) if revised else None
    return {
        "topic": topic_id,
        "model": model,
        "condition": "twopass",
        "rep": rep,
        "seconds": round(secs_a + secs_b, 1),
        "error": err_b,
        "words": report.words if report else 0,
        "total": report.total if report else None,
        "raw_draft_total": raw_report.total,
        "raw_draft_words": raw_report.words,
        "raw_draft_suspicious": suspicious,
        "raw_draft_text": raw,
        "text": revised,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--topics", default=",".join(TOPICS), help="comma-separated topic ids")
    parser.add_argument("--models", default="sonnet", help="comma-separated claude -p --model values")
    parser.add_argument("--conditions", default="midtask,twopass")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    unknown = set(topics) - set(TOPICS)
    if unknown:
        parser.error(f"unknown topics: {', '.join(sorted(unknown))}")
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    unknown_conditions = set(conditions) - set(CONDITIONS)
    if unknown_conditions:
        # A typo here (e.g. "twpass") used to run the wrong function silently
        # and mislabel the result with the misspelled condition's own name,
        # which get() calls of the form r["condition"] == "twopass" would
        # then just never match - quietly halving a cell's n instead of
        # erroring. Catch it at parse time instead.
        parser.error(f"unknown conditions: {', '.join(sorted(unknown_conditions))}")

    skill = SKILL_PATH.read_text(encoding="utf-8")
    skill_sha256 = hashlib.sha256(skill.encode()).hexdigest()[:16]

    jobs = [
        (cond, topic_id, model, rep)
        for topic_id in topics
        for model in models
        for cond in conditions
        for rep in range(args.repeats)
    ]
    print(f"{len(jobs)} jobs (twopass = 2 subprocess calls each)", file=sys.stderr)

    def work(job):
        kind, topic_id, model, rep = job
        fn = run_midtask if kind == "midtask" else run_twopass
        r = fn(topic_id, model, rep, skill, args.timeout)
        status = r["error"] or f"{r['total']}/32, {r['words']}w"
        print(f"  [{topic_id:<24} {model:<7} {kind:<8} rep{rep}] {status}", file=sys.stderr)
        return r

    records = []
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(work, jobs):
            records.append(r)

    out = args.out or (Path(__file__).parent / "results" / "latest_run.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "skill_sha256": skill_sha256,
            "topics": topics,
            "models": models,
            "conditions": conditions,
            "repeats": args.repeats,
        },
        "runs": records,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {out} (skill_sha256={skill_sha256})", file=sys.stderr)

    # total is None for a call that returned exitcode 0 with empty stdout
    # (error is None too in that case) - exclude those from the mean, not
    # just calls that set error, or sum() below crashes on a None.
    ok = [r for r in records if not r["error"] and r["total"] is not None]
    print("\n=== summary (mean total /32) ===")
    for topic_id in topics:
        for model in models:
            cells = []
            for cond in conditions:
                totals = [
                    r["total"]
                    for r in ok
                    if r["topic"] == topic_id and r["model"] == model and r["condition"] == cond
                ]
                cells.append(
                    f"{cond}={sum(totals) / len(totals):.2f}(n={len(totals)})" if totals else f"{cond}=NA"
                )
            print(f"{topic_id:<24} {model:<7} " + "  ".join(cells))

    failed = [r for r in records if r["error"]]
    if failed:
        print(f"\n{len(failed)} failed call(s) - see error field in {out}", file=sys.stderr)
    suspicious = [r for r in records if r.get("raw_draft_suspicious")]
    if suspicious:
        print(
            f"\n{len(suspicious)} raw draft(s) under 150 words - likely a meta-description "
            f"instead of the actual piece, not a genuinely low-slop draft. Do not read these "
            f"as evidence of good editing.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
