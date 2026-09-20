"""evals/rescore.py rebuilds the eval's headline numbers from raw text with no
model calls, and had zero test coverage when it was added - which is how it
shipped with a `--check` mode that silently wrote the file it claimed not to,
and an `--out` flag that crashed on any relative path. Both are regression
tests here now; see the fixes' commit for how they were found.

These tests run against a small, isolated fixture directory rather than the
live repo's real eval data, so they stay fast and deterministic and do not
depend on evals/results/raw/ having any particular content.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def eval_fixture(tmp_path, monkeypatch):
    """A minimal draft + raw-text tree, plus a SKILL.md rescore.py will hash."""
    draft_dir = tmp_path / "drafts"
    raw_dir = tmp_path / "raw"
    draft_dir.mkdir()
    raw_dir.mkdir()

    (draft_dir / "example.md").write_text(
        "This journey has been both challenging and rewarding. Experts say it shows.\n",
        encoding="utf-8",
    )
    for arm in ("baseline", "generic", "skill"):
        for rep in range(2):
            (raw_dir / f"example.{arm}.{rep}.md").write_text(
                f"A clean revision, arm={arm}, rep={rep}.\n", encoding="utf-8"
            )

    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("---\nname: x\ndescription: x\n---\n\nfirst version\n", encoding="utf-8")

    monkeypatch.setattr("evals.rescore.DRAFT_DIR", draft_dir)
    monkeypatch.setattr("evals.rescore.RAW_DIR", raw_dir)
    monkeypatch.setattr("evals.rescore.SKILL_PATH", skill_path)
    return {"tmp_path": tmp_path, "draft_dir": draft_dir, "raw_dir": raw_dir, "skill_path": skill_path}


def test_rebuilds_without_model_calls(eval_fixture):
    from evals.rescore import main

    out = eval_fixture["tmp_path"] / "latest.json"
    assert main(["--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["meta"]["draft_count"] == 1
    assert {r["arm"] for r in payload["runs"]} == {"baseline", "generic", "skill"}
    assert len(payload["runs"]) == 6  # 3 arms x 2 reps
    expected_sha = hashlib.sha256(
        eval_fixture["skill_path"].read_text(encoding="utf-8").encode()
    ).hexdigest()[:16]
    assert payload["meta"]["skill_sha256"] == expected_sha


def test_out_accepts_a_path_outside_the_repo(eval_fixture):
    """Regression test: relative_to(REPO_ROOT) used to raise ValueError for
    any --out path that wasn't a descendant of the repo, crashing on exit
    after a fully successful write."""
    from evals.rescore import main

    out = eval_fixture["tmp_path"] / "latest.json"
    assert out.parent != REPO_ROOT  # tmp_path is never inside the repo
    assert main(["--out", str(out)]) == 0
    assert out.exists()


def test_check_never_writes_the_file(eval_fixture):
    """Regression test: --check used to write the file anyway whenever no
    drift was detected, despite the flag's help text and docstring both
    promising a dry run."""
    from evals.rescore import main

    out = eval_fixture["tmp_path"] / "latest.json"
    assert main(["--check", "--out", str(out)]) == 0
    assert not out.exists(), "--check must not write --out"


def test_check_exits_zero_with_no_prior_results(eval_fixture):
    from evals.rescore import main

    out = eval_fixture["tmp_path"] / "does-not-exist-yet.json"
    assert main(["--check", "--out", str(out)]) == 0


def test_check_exits_nonzero_when_skill_md_drifted(eval_fixture):
    """First write establishes a baseline sha. Editing SKILL.md afterwards,
    with the skill-arm raw text left as-is, must be caught."""
    from evals.rescore import main

    out = eval_fixture["tmp_path"] / "latest.json"
    assert main(["--out", str(out)]) == 0

    eval_fixture["skill_path"].write_text(
        "---\nname: x\ndescription: x\n---\n\na different version entirely\n", encoding="utf-8"
    )
    assert main(["--check", "--out", str(out)]) == 1


def test_check_exits_zero_when_skill_md_unchanged(eval_fixture):
    from evals.rescore import main

    out = eval_fixture["tmp_path"] / "latest.json"
    assert main(["--out", str(out)]) == 0
    assert main(["--check", "--out", str(out)]) == 0


def test_rescoring_is_independent_of_the_committed_generation_metadata(eval_fixture):
    """Two rebuilds of the same raw text must score identically - only
    generated_at should differ. This is the property that makes the tool
    trustworthy for "no new model calls, just rescore"."""
    from evals.rescore import main

    out1 = eval_fixture["tmp_path"] / "first.json"
    out2 = eval_fixture["tmp_path"] / "second.json"
    assert main(["--out", str(out1)]) == 0
    assert main(["--out", str(out2)]) == 0
    p1, p2 = json.loads(out1.read_text()), json.loads(out2.read_text())
    for p in (p1, p2):
        del p["meta"]["generated_at"]
    assert p1 == p2


def test_cli_runs_end_to_end_as_a_subprocess(eval_fixture):
    """A lighter-weight sanity check that the script is actually invokable as
    `python evals/rescore.py`, not only importable as a module - argparse
    wiring, __main__ guard, and sys.path setup all live outside main()."""
    out = eval_fixture["tmp_path"] / "latest.json"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "evals/rescore.py"),
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # This subprocess doesn't get the monkeypatched DRAFT_DIR/RAW_DIR, so it
    # rescores the real repo corpus - just confirm it runs and writes valid
    # JSON, not that it matches the fixture's tiny example.
    assert result.returncode == 0, result.stderr
    assert out.exists()
    json.loads(out.read_text(encoding="utf-8"))
