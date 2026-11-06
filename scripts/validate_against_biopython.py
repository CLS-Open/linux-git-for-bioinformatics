#!/usr/bin/env python3
"""Cross-validate bioflow's statistics against Biopython (an independent implementation).

This is the script behind docs/validation.md. It is NOT part of the test suite,
because Biopython is deliberately not a dependency of the teaching package --
but CI runs it in a separate job so the validation claim cannot rot.

Requires: pip install biopython
Exit code 0 = all checks agree; 1 = disagreement (prints which).
"""
from __future__ import annotations

import sys
from pathlib import Path

from bioflow.seqio import read_records
from bioflow.stats import summarise

try:
    from Bio import SeqIO
except ImportError:  # pragma: no cover
    print("Biopython is required: pip install biopython", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
TOL = 0.01
failures: list[str] = []


def check(label: str, ours, theirs, tol: float = 0.0) -> None:
    ok = abs(ours - theirs) <= tol if isinstance(ours, (int, float)) else ours == theirs
    print(f"{'PASS' if ok else 'FAIL'}  {label:<28} bioflow={ours!s:<12} biopython={theirs!s}")
    if not ok:
        failures.append(label)


def validate_fastq() -> None:
    path = ROOT / "datasets" / "sample" / "reads.fastq"
    ours = summarise(read_records(path)).as_dict()
    ref = list(SeqIO.parse(str(path), "fastq"))
    gc = sum(str(r.seq).upper().count("G") + str(r.seq).upper().count("C") for r in ref)
    at = sum(str(r.seq).upper().count("A") + str(r.seq).upper().count("T") for r in ref)
    total_bases = sum(len(r) for r in ref)
    mean_q = sum(sum(r.letter_annotations["phred_quality"]) for r in ref) / total_bases
    check("FASTQ records", ours["n_records"], len(ref))
    check("FASTQ total bases", ours["total_bases"], total_bases)
    check("FASTQ GC%", ours["gc_percent"], round(gc / (gc + at) * 100, 2), TOL)
    check("FASTQ mean Phred", ours["mean_quality"], round(mean_q, 2), TOL)


def validate_fasta() -> None:
    path = ROOT / "datasets" / "sample" / "proteins.fasta"
    ours = summarise(read_records(path)).as_dict()
    ref = list(SeqIO.parse(str(path), "fasta"))
    lengths = sorted((len(r.seq) for r in ref), reverse=True)
    total = sum(lengths)
    running, expected_n50 = 0, lengths[-1]
    for length in lengths:
        running += length
        if running * 2 >= total:
            expected_n50 = length
            break
    check("FASTA records", ours["n_records"], len(ref))
    check("FASTA total bases", ours["total_bases"], total)
    check("FASTA N50", ours["n50"], expected_n50)


def main() -> int:
    validate_fastq()
    validate_fasta()
    if failures:
        print(f"\nFAILED: {len(failures)} disagreement(s): {failures}", file=sys.stderr)
        return 1
    print("\nAll cross-validation checks agree with Biopython.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
