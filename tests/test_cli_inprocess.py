"""In-process CLI tests.

The subprocess-based tests in test_cli.py prove the tool works as a *user*
experiences it (real argv, real exit codes). These tests call ``main()``
directly so that coverage measurement sees the CLI code path — because
coverage tools do not follow subprocesses by default, an unmeasured CLI would
look untested when it is in fact well tested.
"""

from __future__ import annotations

import json

import pytest
import yaml

from bioflow.cli import main


def test_main_stats_json(capsys):
    assert main(["stats", "datasets/sample/reads.fastq", "--json"]) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["n_records"] == 200


def test_main_stats_human_readable(capsys):
    assert main(["stats", "datasets/sample/proteins.fasta"]) == 0
    out = capsys.readouterr().out
    assert "records" in out and "N50" in out
    assert "mean Phred" not in out


def test_main_stats_error(capsys):
    assert main(["stats", "nope.fastq"]) == 2
    assert "error:" in capsys.readouterr().err


def test_main_plan(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("x")
    p = tmp_path / "p.yml"
    p.write_text(
        yaml.safe_dump(
            {"steps": [{"name": "s1", "command": "cp {inputs} {outputs}", "inputs": ["a.txt"], "outputs": ["b.txt"]}]}
        )
    )
    assert main(["plan", str(p)]) == 0
    assert "cmd:" in capsys.readouterr().out


def test_main_plan_cycle_error(tmp_path, capsys):
    p = tmp_path / "p.yml"
    p.write_text(
        yaml.safe_dump(
            {
                "steps": [
                    {"name": "a", "command": "true", "inputs": ["y"], "outputs": ["x"]},
                    {"name": "b", "command": "true", "inputs": ["x"], "outputs": ["y"]},
                ]
            }
        )
    )
    assert main(["plan", str(p)]) == 2
    assert "cycle" in capsys.readouterr().err


def test_main_run_success(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    p = tmp_path / "p.yml"
    p.write_text(
        yaml.safe_dump(
            {"steps": [{"name": "s1", "command": "cp {inputs} {outputs}", "inputs": ["a.txt"], "outputs": ["b.txt"]}]}
        )
    )
    assert main(["run", str(p)]) == 0
    assert "ok: 1 executed" in capsys.readouterr().out


def test_main_run_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "p.yml"
    p.write_text(yaml.safe_dump({"steps": [{"name": "bad", "command": "exit 9", "outputs": ["z"]}]}))
    assert main(["run", str(p)]) == 1
    assert "FAILED at step: bad" in capsys.readouterr().err


def test_main_jobs_warning(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    p = tmp_path / "p.yml"
    p.write_text(
        yaml.safe_dump(
            {"steps": [{"name": "s1", "command": "cp {inputs} {outputs}", "inputs": ["a.txt"], "outputs": ["b.txt"]}]}
        )
    )
    assert main(["run", str(p), "--jobs", "8"]) == 0
    assert "ignored by design" in capsys.readouterr().err


def test_main_missing_pipeline_file(capsys):
    assert main(["plan", "absent.yml"]) == 2
    assert "error:" in capsys.readouterr().err


def test_parser_requires_subcommand(capsys):
    with pytest.raises(SystemExit):
        main([])
