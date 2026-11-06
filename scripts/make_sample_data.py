#!/usr/bin/env python3
"""Generate the small SYNTHETIC datasets shipped with this repository.

Why synthetic data?
-------------------
The teaching datasets must be small (<200 KB) so the whole repository clones in
seconds on a slow connection, completely deterministic so that every learner and
every CI run sees identical numbers, and free of any data-use agreement.

**These reads are simulated. They are not experimental measurements and must
never be presented as such.** The generator is committed so that anyone can
verify the provenance and regenerate byte-identical files.

Usage
-----
    python scripts/make_sample_data.py
"""

from __future__ import annotations

import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "datasets" / "sample"
SEED = 20261106
N_READS = 200
READ_LEN = 60


def make_reads() -> None:
    rng = random.Random(SEED)
    # A GC-rich "genome" so that GC content is a meaningful statistic to compute.
    genome = ("GGCCATGCGC" * 400) + ("ATATATAT" * 200)
    out = SAMPLE / "reads.fastq"
    with out.open("w", encoding="utf-8") as fh:
        for i in range(N_READS):
            start = rng.randrange(0, len(genome) - READ_LEN)
            seq = genome[start : start + READ_LEN]
            # Simulate per-position quality decaying along the read (realistic shape)
            quals = []
            for pos in range(READ_LEN):
                base_q = 38 - int(pos * 0.25)
                q = max(2, min(41, rng.gauss(base_q, 3)))
                quals.append(chr(int(q) + 33))
            fh.write(f"@synthetic_read_{i:03d} simulated genome={start} length={READ_LEN}\n")
            fh.write(seq + "\n+\n" + "".join(quals) + "\n")


def make_proteins() -> None:
    rng = random.Random(SEED + 1)
    amino = "ACDEFGHIKLMNPQRSTVWY"
    out = SAMPLE / "proteins.fasta"
    with out.open("w", encoding="utf-8") as fh:
        for i in range(12):
            length = rng.randint(40, 120)
            seq = "".join(rng.choice(amino) for _ in range(length))
            fh.write(f">synthetic_protein_{i:02d} organism=Simulateda examplea length={length}\n")
            for j in range(0, length, 60):
                fh.write(seq[j : j + 60] + "\n")


def make_pipeline_input() -> None:
    """A tiny FASTA used by the example pipeline in tutorials/ and the lesson."""
    out = SAMPLE / "contigs.fasta"
    seqs = {
        "contig_1": "ATGCGTACGTAGCTAGCTAGCATCGATCGTAGCTAGCTAGCTAGCAT",
        "contig_2": "GGGGCCCCGGGGCCCCAAAATTTTGGGGCCCCAAAATTTTGGGGCCCCAAAATTTT",
        "contig_3": "ACGT" * 30,
    }
    with out.open("w", encoding="utf-8") as fh:
        for name, seq in seqs.items():
            fh.write(f">{name} synthetic=True\n")
            for j in range(0, len(seq), 60):
                fh.write(seq[j : j + 60] + "\n")


def main() -> None:
    SAMPLE.mkdir(parents=True, exist_ok=True)
    make_reads()
    make_proteins()
    make_pipeline_input()
    for f in sorted(SAMPLE.iterdir()):
        print(f"{f.name}: {f.stat().st_size} bytes")


if __name__ == "__main__":
    main()
