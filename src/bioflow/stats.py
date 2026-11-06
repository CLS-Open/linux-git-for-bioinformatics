"""Sequence statistics with definitions stated as code.

Every metric here is defined in a docstring so that a learner can verify the
arithmetic by hand. Ambiguity in bioinformatics statistics is the norm — N50,
GC%, and "mean quality" all have subtly different conventions. We fix ours.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .seqio import Record

#: Phred+33 offset used by Illumina 1.8+ and virtually all modern FASTQ.
PHRED_OFFSET = 33

#: IUPAC ambiguity codes that are neither G/C nor A/T.
AMBIGUOUS = set("NRYKMSWBDHVX-.")


def gc_content(sequence: str) -> float:
    """GC content as a fraction in [0, 1], ignoring ambiguous symbols.

    ``GC%`` is *defined* here as ``(G + C) / (A + T + G + C)``. Ambiguous bases
    (N, R, Y, ...) are excluded from both numerator and denominator, because
    including them silently deflates GC content in draft assemblies — a classic
    source of irreproducible QC numbers.
    """
    seq = sequence.upper()
    gc = seq.count("G") + seq.count("C")
    at = seq.count("A") + seq.count("T")
    unambiguous = gc + at
    if unambiguous == 0:
        return 0.0
    return gc / unambiguous


def phred_scores(qualities: str) -> list[int]:
    """Convert FASTQ quality characters to Phred scores (Q = ord(char) - 33)."""
    return [ord(c) - PHRED_OFFSET for c in qualities]


def n50(lengths: Sequence[int]) -> int:
    """N50 of an assembly.

    Sort lengths descending, accumulate until the cumulative sum reaches at
    least half of the total length; that length is the N50. Ties are resolved
    by the first cut-off reached, which is the standard convention used by
    QUAST and assembly-stats.
    """
    if not lengths:
        return 0
    ordered = sorted(lengths, reverse=True)
    total = sum(ordered)
    running = 0
    for length in ordered:
        running += length
        if running * 2 >= total:
            return length
    return ordered[-1]


@dataclass
class SequenceStats:
    """Aggregate statistics over a set of records."""

    n_records: int = 0
    total_bases: int = 0
    gc_fraction: float = 0.0
    mean_length: float = 0.0
    min_length: int = 0
    max_length: int = 0
    n50: int = 0
    mean_quality: float | None = None
    per_position_mean_quality: list[float] = field(default_factory=list)
    length_histogram: dict[int, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        out = {
            "n_records": self.n_records,
            "total_bases": self.total_bases,
            "gc_fraction": round(self.gc_fraction, 4),
            "gc_percent": round(self.gc_fraction * 100, 2),
            "mean_length": round(self.mean_length, 2),
            "min_length": self.min_length,
            "max_length": self.max_length,
            "n50": self.n50,
            "length_histogram": dict(sorted(self.length_histogram.items())),
        }
        if self.mean_quality is not None:
            out["mean_quality"] = round(self.mean_quality, 2)
            out["per_position_mean_quality"] = [
                round(q, 2) for q in self.per_position_mean_quality
            ]
        return out


def summarise(records: Iterable[Record]) -> SequenceStats:
    """Compute :class:`SequenceStats` in a single streaming pass."""
    lengths: list[int] = []
    gc_bases = 0
    at_bases = 0
    total = 0
    quality_sums: list[int] = []
    quality_counts: list[int] = []
    n_quality_records = 0

    for rec in records:
        lengths.append(rec.length)
        total += rec.length
        for base in rec.sequence:
            if base in ("G", "C"):
                gc_bases += 1
            elif base in ("A", "T"):
                at_bases += 1
        if rec.qualities is not None:
            n_quality_records += 1
            scores = phred_scores(rec.qualities)
            if len(quality_sums) < len(scores):
                pad = len(scores) - len(quality_sums)
                quality_sums.extend([0] * pad)
                quality_counts.extend([0] * pad)
            for i, q in enumerate(scores):
                quality_sums[i] += q
                quality_counts[i] += 1

    hist: dict[int, int] = {}
    for length in lengths:
        hist[length] = hist.get(length, 0) + 1

    stats = SequenceStats(
        n_records=len(lengths),
        total_bases=total,
        gc_fraction=(gc_bases / (gc_bases + at_bases)) if (gc_bases + at_bases) else 0.0,
        mean_length=(total / len(lengths)) if lengths else 0.0,
        min_length=min(lengths) if lengths else 0,
        max_length=max(lengths) if lengths else 0,
        n50=n50(lengths),
        length_histogram=hist,
    )
    if n_quality_records:
        per_pos = [
            s / c for s, c in zip(quality_sums, quality_counts) if c > 0
        ]
        stats.per_position_mean_quality = per_pos
        flat_total = sum(s for s in quality_sums)
        flat_count = sum(c for c in quality_counts)
        stats.mean_quality = (flat_total / flat_count) if flat_count else None
    return stats
