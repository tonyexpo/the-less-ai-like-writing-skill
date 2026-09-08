"""The CLI is the CI entry point, so its contract is tested too."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.slopscore import main

REPO_ROOT = Path(__file__).resolve().parent.parent
SLOP = REPO_ROOT / "tests/fixtures/slop/obama_overview.md"
HUMAN = REPO_ROOT / "tests/fixtures/clean/obama_note.md"


def run(*args: str, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.slopscore", *args],
        cwd=REPO_ROOT,
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_text_report_names_the_band():
    result = run(str(HUMAN))
    assert result.returncode == 0
    assert "(low)" in result.stdout


def test_json_report_is_valid_and_complete():
    result = run("--json", str(SLOP))
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    entry = payload[0]
    assert entry["max_total"] == 24
    assert entry["total"] == sum(c["score"] for c in entry["categories"])
    assert len(entry["categories"]) == 12
    assert entry["categories"][0]["hits"], "hits should be included by default"


def test_quiet_omits_hits():
    payload = json.loads(run("--json", "--quiet", str(SLOP)).stdout)
    assert "hits" not in payload[0]["categories"][0]


def test_stdin_is_accepted():
    result = run("-", stdin="Experts say it is groundbreaking. In conclusion, time will tell.")
    assert result.returncode == 0
    assert "<stdin>" in result.stdout


def test_max_score_gate_passes_clean_text():
    assert run("--max-score", "5", str(HUMAN)).returncode == 0


def test_max_score_gate_fails_slop():
    result = run("--max-score", "5", str(SLOP))
    assert result.returncode == 1
    assert "over the --max-score" in result.stderr


def test_multiple_files_are_reported_together():
    result = run("--quiet", str(SLOP), str(HUMAN))
    assert result.returncode == 0
    assert result.stdout.count("/24") == 2


def test_main_is_importable_and_returns_exit_code(capsys):
    assert main(["--json", "--quiet", str(HUMAN)]) == 0
    assert main(["--max-score", "0", str(SLOP)]) == 1
    capsys.readouterr()
