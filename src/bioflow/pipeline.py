"""A minimal, readable declarative pipeline engine.

What it does
------------
1. Loads a YAML pipeline of named *steps*, each with ``inputs``, ``outputs``
   and a shell ``command`` (placeholders ``{inputs}`` / ``{outputs}`` are
   substituted with space-separated, shell-quoted paths).
2. Builds a dependency graph: a step depends on any step that produces one of
   its inputs. Unproducible inputs are an error *before* anything runs.
3. Detects cycles and raises an explicit error rather than hanging.
4. Executes steps in a deterministic topological order (declaration order is
   the tie-breaker, so runs are reproducible).
5. Skips steps that are up to date, using SHA-256 of every input plus the
   command string, recorded in ``.bioflow/stamps/<step>.json``.
6. Writes a provenance log (``bioflow_run.log``) with timestamps, commands and
   content hashes for every step executed.

What it deliberately does *not* do (documented limitations)
-----------------------------------------------------------
* No parallelism (``--jobs`` is accepted and ignored with a warning).
* No container isolation, no cluster submission, no retry policy.
* No wildcard/pattern rules — the learner should meet those in Snakemake.
* Shell commands are executed with ``shell=True``: pipelines are code, and
  should be treated as such (this is true of every workflow manager).
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml


class PipelineError(ValueError):
    """Invalid pipeline definition."""


@dataclass(frozen=True, slots=True)
class Step:
    name: str
    command: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    environment: dict[str, str] = field(default_factory=dict)


def load_pipeline(path: str | Path) -> list[Step]:
    """Parse and validate a pipeline YAML file."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "steps" not in raw:
        raise PipelineError("pipeline must be a mapping with a top-level 'steps' key")
    steps: list[Step] = []
    names: set[str] = set()
    for i, item in enumerate(raw["steps"]):
        if not isinstance(item, dict) or "name" not in item or "command" not in item:
            raise PipelineError(f"step {i} must be a mapping with 'name' and 'command'")
        name = str(item["name"])
        if name in names:
            raise PipelineError(f"duplicate step name: {name!r}")
        names.add(name)
        steps.append(
            Step(
                name=name,
                command=str(item["command"]),
                inputs=tuple(str(x) for x in item.get("inputs", []) or []),
                outputs=tuple(str(x) for x in item.get("outputs", []) or []),
                environment={str(k): str(v) for k, v in (item.get("env") or {}).items()},
            )
        )
    if not steps:
        raise PipelineError("pipeline contains no steps")
    return steps


def producer_map(steps: list[Step]) -> dict[str, str]:
    """Map each output path to the step that produces it (last writer wins)."""
    producers: dict[str, str] = {}
    for step in steps:
        for out in step.outputs:
            producers[out] = step.name
    return producers


def dependencies(steps: list[Step]) -> dict[str, set[str]]:
    producers = producer_map(steps)
    deps: dict[str, set[str]] = {s.name: set() for s in steps}
    for step in steps:
        for inp in step.inputs:
            producer = producers.get(inp)
            if producer and producer != step.name:
                deps[step.name].add(producer)
    return deps


def validate(steps: list[Step], check_filesystem: bool = True) -> None:
    """Raise :class:`PipelineError` if the pipeline cannot be executed."""
    producers = producer_map(steps)
    missing: list[str] = []
    for step in steps:
        if not step.outputs:
            raise PipelineError(f"step {step.name!r} declares no outputs")
        for inp in step.inputs:
            produced = inp in producers
            exists = Path(inp).exists()
            if not produced and not (exists or not check_filesystem):
                missing.append(f"{step.name!r} needs {inp!r} (not produced by any step and not on disk)")
    if missing:
        raise PipelineError("unsatisfiable inputs:\n  - " + "\n  - ".join(missing))
    _topological_order(steps)  # raises on cycles


def _topological_order(steps: list[Step]) -> list[Step]:
    deps = dependencies(steps)
    by_name = {s.name: s for s in steps}
    order: list[Step] = []
    state: dict[str, int] = {}  # 0=unvisited 1=visiting 2=done

    def visit(name: str, stack: list[str]) -> None:
        mark = state.get(name, 0)
        if mark == 2:
            return
        if mark == 1:
            cycle = " -> ".join(stack[stack.index(name):] + [name])
            raise PipelineError(f"dependency cycle detected: {cycle}")
        state[name] = 1
        for dep in sorted(deps[name]):
            visit(dep, stack + [name])
        state[name] = 2
        order.append(by_name[name])

    for step in steps:  # declaration order breaks ties deterministically
        visit(step.name, [])
    return order


def topological_order(steps: list[Step]) -> list[Step]:
    """Public wrapper returning steps in executable order."""
    validate(steps, check_filesystem=False)
    return _topological_order(steps)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_fingerprint(step: Step) -> str:
    """SHA-256 over the command string and the content of every existing input."""
    h = hashlib.sha256()
    h.update(step.command.encode("utf-8"))
    for inp in step.inputs:
        p = Path(inp)
        h.update(inp.encode("utf-8"))
        h.update(_sha256(p).encode("utf-8") if p.is_file() else b"<missing>")
    return h.hexdigest()


def _stamp_path(stamp_dir: Path, name: str) -> Path:
    return stamp_dir / f"{name}.json"


def is_up_to_date(step: Step, stamp_dir: Path) -> bool:
    """True only if the stamp exists, matches, and every output is present."""
    stamp = _stamp_path(stamp_dir, step.name)
    if not stamp.exists():
        return False
    try:
        recorded = json.loads(stamp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if recorded.get("fingerprint") != input_fingerprint(step):
        return False
    return all(Path(out).exists() for out in step.outputs)


def _render(command: str, step: Step) -> str:
    """Substitute ``{inputs}`` / ``{outputs}`` placeholders into a command string.

    We deliberately use explicit token replacement rather than ``str.format``:
    shell commands routinely contain literal braces (``awk '{print $1}'``,
    ``find -exec {} \;``, bash brace expansion ``{1..10}``), and ``str.format``
    would either raise ``KeyError`` or silently mangle them. A learner who has
    ever had an awk one-liner explode inside a workflow manager will recognise
    this bug — it is documented in docs/limitations.md and covered by
    tests/test_pipeline.py::test_awk_braces_survive_rendering.
    """
    return command.replace("{inputs}", " ".join(shlex.quote(i) for i in step.inputs)).replace(
        "{outputs}", " ".join(shlex.quote(o) for o in step.outputs)
    )


@dataclass
class RunReport:
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: str | None = None

    @property
    def ok(self) -> bool:
        return self.failed is None

    def as_dict(self) -> dict:
        return {"executed": self.executed, "skipped": self.skipped, "failed": self.failed}


def run_pipeline(
    steps: list[Step],
    stamp_dir: str | Path = ".bioflow/stamps",
    log_path: str | Path = "bioflow_run.log",
    dry_run: bool = False,
    base_dir: str | Path = ".",
) -> RunReport:
    """Execute the pipeline. Returns a :class:`RunReport` (never raises on step failure)."""
    validate(steps)
    order = _topological_order(steps)
    stamp_dir = Path(stamp_dir)
    stamp_dir.mkdir(parents=True, exist_ok=True)
    report = RunReport()
    log_lines: list[str] = []

    for step in order:
        if is_up_to_date(step, stamp_dir):
            report.skipped.append(step.name)
            log_lines.append(f"SKIP\t{step.name}\tup to date")
            continue
        rendered = _render(step.command, step)
        if dry_run:
            report.executed.append(step.name)
            log_lines.append(f"DRY\t{step.name}\t{rendered}")
            continue
        for out in step.outputs:
            Path(out).parent.mkdir(parents=True, exist_ok=True)
        started = time.strftime("%Y-%m-%dT%H:%M:%S")
        result = subprocess.run(
            rendered,
            shell=True,
            cwd=base_dir,
            env={**os.environ, **step.environment},
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            report.failed = step.name
            log_lines.append(
                f"FAIL\t{step.name}\t{started}\trc={result.returncode}\t{rendered}\t{result.stderr.strip()[:500]}"
            )
            break
        missing_outputs = [o for o in step.outputs if not Path(o).exists()]
        if missing_outputs:
            report.failed = step.name
            log_lines.append(
                f"FAIL\t{step.name}\t{started}\tmissing outputs {missing_outputs}\tcommand did not create declared outputs"
            )
            break
        fingerprint = input_fingerprint(step)
        _stamp_path(stamp_dir, step.name).write_text(
            json.dumps(
                {
                    "step": step.name,
                    "fingerprint": fingerprint,
                    "command": rendered,
                    "completed_at": started,
                    "outputs": {
                        o: _sha256(Path(o)) for o in step.outputs if Path(o).is_file()
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        report.executed.append(step.name)
        log_lines.append(f"RUN\t{step.name}\t{started}\t{rendered}")

    Path(log_path).open("a", encoding="utf-8").write(
        "\n".join(
            [
                f"# bioflow run {time.strftime('%Y-%m-%dT%H:%M:%S')} "
                f"dry_run={dry_run} python={sys.version.split()[0]}",
                *log_lines,
                "",
            ]
        )
    )
    return report
