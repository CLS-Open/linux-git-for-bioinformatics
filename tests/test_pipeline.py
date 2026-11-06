"""Tests for bioflow.pipeline — DAG construction, validation, execution, caching."""

from __future__ import annotations

import json

import pytest
import yaml

from bioflow.pipeline import (
    PipelineError,
    dependencies,
    load_pipeline,
    run_pipeline,
    topological_order,
)


def write_pipeline(tmp_path, steps):
    p = tmp_path / "pipeline.yml"
    p.write_text(yaml.safe_dump({"steps": steps}))
    return p


def test_load_pipeline_minimal(tmp_path):
    p = write_pipeline(
        tmp_path,
        [{"name": "a", "command": "echo hi > out.txt", "outputs": ["out.txt"]}],
    )
    steps = load_pipeline(p)
    assert len(steps) == 1
    assert steps[0].name == "a"
    assert steps[0].outputs == ("out.txt",)


def test_duplicate_step_names_rejected(tmp_path):
    p = write_pipeline(
        tmp_path,
        [
            {"name": "a", "command": "true", "outputs": ["x"]},
            {"name": "a", "command": "true", "outputs": ["y"]},
        ],
    )
    with pytest.raises(PipelineError, match="duplicate"):
        load_pipeline(p)


def test_missing_name_or_command_rejected(tmp_path):
    p = write_pipeline(tmp_path, [{"name": "a", "outputs": ["x"]}])
    with pytest.raises(PipelineError, match="name.*command"):
        load_pipeline(p)


def test_step_without_outputs_rejected(tmp_path):
    p = write_pipeline(tmp_path, [{"name": "a", "command": "true"}])
    steps = load_pipeline(p)
    with pytest.raises(PipelineError, match="no outputs"):
        topological_order(steps)


def test_dependencies_follow_paths(tmp_path):
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [
                {"name": "first", "command": "true", "outputs": ["a.txt"]},
                {"name": "second", "command": "true", "inputs": ["a.txt"], "outputs": ["b.txt"]},
            ],
        )
    )
    assert dependencies(steps)["second"] == {"first"}
    assert dependencies(steps)["first"] == set()


def test_topological_order_respects_dependencies(tmp_path):
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [
                {"name": "c", "command": "true", "inputs": ["b.txt"], "outputs": ["c.txt"]},
                {"name": "a", "command": "true", "outputs": ["a.txt"]},
                {"name": "b", "command": "true", "inputs": ["a.txt"], "outputs": ["b.txt"]},
            ],
        )
    )
    assert [s.name for s in topological_order(steps)] == ["a", "b", "c"]


def test_cycle_detection(tmp_path):
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [
                {"name": "a", "command": "true", "inputs": ["y"], "outputs": ["x"]},
                {"name": "b", "command": "true", "inputs": ["x"], "outputs": ["y"]},
            ],
        )
    )
    with pytest.raises(PipelineError, match="cycle"):
        topological_order(steps)


def test_unsatisfiable_input_detected_before_running(tmp_path):
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [{"name": "a", "command": "true", "inputs": ["nope.txt"], "outputs": ["x"]}],
        )
    )
    with pytest.raises(PipelineError, match="unsatisfiable"):
        run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")


def test_run_executes_in_order_and_creates_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("ACGT\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [
                {
                    "name": "copy",
                    "command": "cp {inputs} {outputs}",
                    "inputs": ["in.txt"],
                    "outputs": ["out/copy.txt"],
                },
                {
                    "name": "count",
                    "command": "wc -c < {inputs} > {outputs}",
                    "inputs": ["out/copy.txt"],
                    "outputs": ["out/count.txt"],
                },
            ],
        )
    )
    report = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "run.log")
    assert report.ok
    assert report.executed == ["copy", "count"]
    assert (tmp_path / "out/copy.txt").read_text() == "ACGT\n"
    assert (tmp_path / "out/count.txt").read_text().strip() == "5"


def test_second_run_skips_up_to_date_steps(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("ACGT\n")
    p = write_pipeline(
        tmp_path,
        [{"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}],
    )
    steps = load_pipeline(p)
    first = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    second = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert first.executed == ["copy"] and first.skipped == []
    assert second.executed == [] and second.skipped == ["copy"]


def test_changed_input_triggers_rerun(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("AAAA\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [{"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}],
        )
    )
    run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    (tmp_path / "in.txt").write_text("CCCC\n")
    report = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert report.executed == ["copy"]
    assert (tmp_path / "o.txt").read_text() == "CCCC\n"


def test_deleted_output_triggers_rerun(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("AAAA\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [{"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}],
        )
    )
    run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    (tmp_path / "o.txt").unlink()
    report = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert report.executed == ["copy"]


def test_failing_step_stops_pipeline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [
                {"name": "boom", "command": "exit 3", "outputs": ["x.txt"]},
                {"name": "never", "command": "touch y.txt", "inputs": ["x.txt"], "outputs": ["y.txt"]},
            ],
        )
    )
    report = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert not report.ok
    assert report.failed == "boom"
    assert not (tmp_path / "y.txt").exists()


def test_step_that_forgets_its_outputs_is_a_failure(tmp_path, monkeypatch):
    """A command that succeeds but declares an output it never creates must fail loudly."""
    monkeypatch.chdir(tmp_path)
    steps = load_pipeline(
        write_pipeline(tmp_path, [{"name": "liar", "command": "true", "outputs": ["ghost.txt"]}])
    )
    report = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert report.failed == "liar"


def test_dry_run_executes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("A\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [{"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}],
        )
    )
    report = run_pipeline(steps, dry_run=True, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert report.executed == ["copy"]
    assert not (tmp_path / "o.txt").exists()


def test_stamp_records_output_hashes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("ACGT\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [{"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}],
        )
    )
    run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    stamp = json.loads((tmp_path / "stamps/copy.json").read_text())
    assert stamp["step"] == "copy"
    assert len(stamp["outputs"]["o.txt"]) == 64  # sha256 hex digest
    assert "completed_at" in stamp


def test_run_log_is_appended_with_provenance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.txt").write_text("ACGT\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [{"name": "copy", "command": "cp {inputs} {outputs}", "inputs": ["in.txt"], "outputs": ["o.txt"]}],
        )
    )
    run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log.txt")
    run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log.txt")
    log = (tmp_path / "log.txt").read_text()
    assert log.count("# bioflow run") == 2
    assert "RUN\tcopy\t" in log
    assert "SKIP\tcopy\t" in log


def test_awk_braces_survive_rendering(tmp_path, monkeypatch):
    """Regression test: awk/bash braces must not be touched by placeholder rendering.

    This bug was found by actually running examples/pipeline.yml: ``str.format``
    raised KeyError on ``awk '{if (n) print n}'``. See docs/limitations.md.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in.fa").write_text(">a\nACGT\n>b\nACGTAC\n")
    steps = load_pipeline(
        write_pipeline(
            tmp_path,
            [
                {
                    "name": "lengths",
                    "command": "awk '/^>/{if (n) print n; print; n=0; next} {n+=length($0)} END{if (n) print n}' {inputs} > {outputs}",
                    "inputs": ["in.fa"],
                    "outputs": ["lengths.txt"],
                }
            ],
        )
    )
    report = run_pipeline(steps, stamp_dir=tmp_path / "stamps", log_path=tmp_path / "log")
    assert report.ok, report.as_dict()
    out = (tmp_path / "lengths.txt").read_text()
    # expected: header, then previous record's length, then next header ...
    assert out.split() == [">a", "4", ">b", "6"]


def test_unrecognised_braces_are_left_alone(tmp_path):
    from bioflow.pipeline import Step, _render

    step = Step(name="s", command="echo {1..3} {inputs}", inputs=("a.txt",), outputs=("o.txt",))
    rendered = _render(step.command, step)
    assert "{1..3}" in rendered
    assert "{inputs}" not in rendered
