"""Tests for the bioflow command-line interface (subprocess, as a user would run it)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
FASTQ = REPO / "datasets" / "sample" / "reads.fastq"
FASTA = REPO / "datasets" / "sample" / "contigs.fasta"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "bioflow.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def test_stats_fastq_text_output():
    result = run_cli("stats", str(FASTQ))
    assert result.returncode == 0, result.stderr
    assert "records         : 200" in result.stdout
    assert "N50" in result.stdout


def test_stats_json_output_is_valid_and_consistent():
    result = run_cli("stats", str(FASTQ), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["n_records"] == 200
    assert payload["total_bases"] == 200 * 60
    assert 0.0 <= payload["gc_fraction"] <= 1.0
    assert "mean_quality" in payload
    assert len(payload["per_position_mean_quality"]) == 60


def test_stats_fasta_has_no_quality_fields():
    result = run_cli("stats", str(FASTA), "--json")
    payload = json.loads(result.stdout)
    assert "mean_quality" not in payload
    assert payload["n_records"] == 3


def test_stats_missing_file_exit_code():
    result = run_cli("stats", "does_not_exist.fastq")
    assert result.returncode == 2
    assert "error:" in result.stderr


def test_stats_malformed_file_exit_code(tmp_path):
    bad = tmp_path / "bad.fq"
    bad.write_text("@r\nACGT\n+\nII\n")
    result = run_cli("stats", str(bad))
    assert result.returncode == 2
    assert "length mismatch" in result.stderr


def test_plan_shows_order(tmp_path):
    (tmp_path / "in.txt").write_text("ACGT\n")
    p = tmp_path / "pipeline.yml"
    p.write_text(
        yaml.safe_dump(
            {
                "steps": [
                    {"name": "b", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["mid.txt"]},
                    {"name": "a", "command": "cp {inputs} {outputs}", "inputs": ["mid.txt"], "outputs": ["final.txt"]},
                ]
            }
        )
    )
    result = run_cli("plan", str(p))
    assert result.returncode == 0, result.stderr
    assert result.stdout.index("b") < result.stdout.index("a")


def test_plan_reports_cycle(tmp_path):
    p = tmp_path / "pipeline.yml"
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
    result = run_cli("plan", str(p))
    assert result.returncode == 2
    assert "cycle" in result.stderr


def test_run_end_to_end(tmp_path):
    (tmp_path / "in.txt").write_text("ACGT\n")
    p = tmp_path / "pipeline.yml"
    p.write_text(
        yaml.safe_dump(
            {
                "steps": [
                    {"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}
                ]
            }
        )
    )
    result = run_cli("run", str(p), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "o.txt").exists()
    assert "ok: 1 executed, 0 skipped" in result.stdout


def test_run_dry_run_creates_nothing(tmp_path):
    (tmp_path / "in.txt").write_text("ACGT\n")
    p = tmp_path / "pipeline.yml"
    p.write_text(
        yaml.safe_dump(
            {
                "steps": [
                    {"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}
                ]
            }
        )
    )
    result = run_cli("run", str(p), "--dry-run", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "o.txt").exists()
    assert "plan: copy" in result.stdout


def test_run_failure_exit_code(tmp_path):
    p = tmp_path / "pipeline.yml"
    p.write_text(yaml.safe_dump({"steps": [{"name": "boom", "command": "exit 1", "outputs": ["x"]}]}))
    result = run_cli("run", str(p), cwd=tmp_path)
    assert result.returncode == 1
    assert "FAILED at step: boom" in result.stderr


def test_jobs_flag_warns_but_runs(tmp_path):
    (tmp_path / "in.txt").write_text("A\n")
    p = tmp_path / "pipeline.yml"
    p.write_text(
        yaml.safe_dump(
            {"steps": [{"name": "c", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}]}
        )
    )
    result = run_cli("run", str(p), "--jobs", "4", cwd=tmp_path)
    assert result.returncode == 0
    assert "ignored by design" in result.stderr


def test_version_flag():
    result = run_cli("--version")
    assert result.returncode == 0
    assert "bioflow 0.1.0" in result.stdout


@pytest.mark.parametrize("subcommand", ["stats", "plan", "run"])
def test_subcommands_require_arguments(subcommand):
    result = run_cli(subcommand)
    assert result.returncode != 0
