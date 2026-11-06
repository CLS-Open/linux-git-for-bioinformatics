"""Command-line interface for bioflow.

Usage
-----
    bioflow stats reads.fastq [--json]
    bioflow plan pipeline.yml
    bioflow run  pipeline.yml [--dry-run] [--jobs N]
    bioflow version
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .pipeline import (
    PipelineError,
    load_pipeline,
    run_pipeline,
    topological_order,
)
from .seqio import SequenceFormatError, read_records
from .stats import summarise


def _cmd_stats(args: argparse.Namespace) -> int:
    try:
        records = read_records(args.path)
        stats = summarise(records)
    except (SequenceFormatError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    payload = stats.as_dict()
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"file            : {args.path}")
    print(f"records         : {payload['n_records']}")
    print(f"total bases     : {payload['total_bases']}")
    print(f"GC              : {payload['gc_percent']}%  (ambiguous bases excluded)")
    print(f"length min/mean/max : {payload['min_length']} / {payload['mean_length']} / {payload['max_length']}")
    print(f"N50             : {payload['n50']}")
    if "mean_quality" in payload:
        print(f"mean Phred      : {payload['mean_quality']}")
    return 0


def _cmd_plan(args: argparse.Namespace) -> int:
    try:
        steps = load_pipeline(args.pipeline)
        order = topological_order(steps)
    except (PipelineError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for i, step in enumerate(order, start=1):
        print(f"{i}. {step.name}")
        if step.inputs:
            print(f"     in : {', '.join(step.inputs)}")
        print(f"     out: {', '.join(step.outputs)}")
        print(f"     cmd: {step.command}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        steps = load_pipeline(args.pipeline)
    except (PipelineError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.jobs > 1:
        print(
            "warning: bioflow executes steps sequentially; --jobs is accepted for "
            "interface compatibility and ignored by design (see docs/limitations.md)",
            file=sys.stderr,
        )
    report = run_pipeline(steps, dry_run=args.dry_run, log_path=args.log)
    for name in report.skipped:
        print(f"skip (up to date): {name}")
    for name in report.executed:
        print(f"{'plan' if args.dry_run else 'run '}: {name}")
    if report.failed:
        print(f"FAILED at step: {report.failed}", file=sys.stderr)
        return 1
    print(f"ok: {len(report.executed)} executed, {len(report.skipped)} skipped")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bioflow",
        description="Auditable minimal pipeline runner and sequence-QC toolkit.",
    )
    parser.add_argument("--version", action="version", version=f"bioflow {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_stats = sub.add_parser("stats", help="sequence statistics for FASTA/FASTQ (gzip ok)")
    p_stats.add_argument("path")
    p_stats.add_argument("--json", action="store_true", help="machine-readable output")
    p_stats.set_defaults(func=_cmd_stats)

    p_plan = sub.add_parser("plan", help="show the execution order without running")
    p_plan.add_argument("pipeline")
    p_plan.set_defaults(func=_cmd_plan)

    p_run = sub.add_parser("run", help="execute a pipeline")
    p_run.add_argument("pipeline")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--jobs", type=int, default=1)
    p_run.add_argument("--log", default="bioflow_run.log")
    p_run.set_defaults(func=_cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
