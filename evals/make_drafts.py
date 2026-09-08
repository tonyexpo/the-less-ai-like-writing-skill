#!/usr/bin/env python3
"""Generate the frozen corpus of AI-slop drafts used by the revision eval.

Run once. The output is committed to ``evals/drafts/`` so the eval has a fixed,
inspectable input and every later run is comparable to the last.

The drafts are produced by asking a model for the polished content-marketing
register that generic LLM prose falls into by default. That is a controlled
stimulus, not a claim that any particular model writes this way unprompted -
see evals/README.md for what this benchmark does and does not show.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.slopscore import score_text  # noqa: E402

DRAFT_DIR = REPO_ROOT / "evals/drafts"
PROMPTS = REPO_ROOT / "evals/prompts.json"

SLOP_REGISTER = (
    "Write it in the polished, upbeat register of corporate content marketing: "
    "open by establishing why the topic matters in today's world, add a short "
    "interpretive comment after each fact, use section headings, balanced "
    "three-part lists, and contrast constructions, and close with a forward-looking "
    "conclusion. Keep every claim vague enough to be safe."
)


def generate_once(spec: dict, model: str, timeout: int) -> str:
    prompt = f"{spec['prompt']}\n\n{SLOP_REGISTER}"
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--allowed-tools", ""],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO_ROOT,
        )
    except subprocess.TimeoutExpired:
        return ""
    return result.stdout.strip()


def generate(spec: dict, model: str, timeout: int, attempts: int, min_score: int) -> tuple[str, str, int]:
    """Resample until the draft is actually sloppy enough to be worth revising.

    A draft the scorer already rates clean gives the revision arms nothing to
    remove, so it would only add noise to the benchmark.
    """
    best, best_score = "", -1
    for _ in range(attempts):
        text = generate_once(spec, model, timeout)
        if not text:
            continue
        total = score_text(text).total
        if total > best_score:
            best, best_score = text, total
        if total >= min_score:
            break
    return spec["id"], best, best_score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the frozen slop-draft corpus.")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--min-score", type=int, default=10, help="reject drafts below this")
    parser.add_argument("--attempts", type=int, default=4, help="resamples before giving up")
    parser.add_argument("--out-dir", type=Path, default=DRAFT_DIR)
    args = parser.parse_args(argv)

    specs = json.loads(PROMPTS.read_text(encoding="utf-8"))["prompts"]
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rejected = []
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        work = lambda spec: generate(spec, args.model, args.timeout, args.attempts, args.min_score)  # noqa: E731
        for prompt_id, text, total in pool.map(work, specs):
            if not text:
                rejected.append((prompt_id, "no output"))
                continue
            if total < args.min_score:
                rejected.append((prompt_id, f"best of {args.attempts} was {total}/24"))
                continue
            report = score_text(text)
            (out_dir / f"{prompt_id}.md").write_text(text + "\n", encoding="utf-8")
            print(f"  {prompt_id:<20} {report.total}/24 ({report.band}), {report.words} words")

    for prompt_id, why in rejected:
        print(f"  rejected {prompt_id}: {why}", file=sys.stderr)
    return 1 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
