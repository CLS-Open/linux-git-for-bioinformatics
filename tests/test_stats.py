"""Tests for bioflow.stats.

Arithmetic checks use hand-computed values (documented in each test) rather
than values produced by the same code — otherwise the test proves nothing.
"""

from __future__ import annotations

import math

import pytest

from bioflow.seqio import Record
from bioflow.stats import gc_content, n50, phred_scores, summarise


# --- GC content -------------------------------------------------------------

def test_gc_content_hand_computed():
    # ACGTACGTAC -> A=3 C=3 G=2 T=2 -> GC = 5/10
    assert gc_content("ACGTACGTAC") == pytest.approx(0.5)


def test_gc_content_excludes_ambiguous_bases():
    # GCNN -> G=1, C=1, N=2 excluded -> 2/2 = 1.0
    assert gc_content("GCNN") == pytest.approx(1.0)


def test_gc_content_all_ambiguous_is_zero():
    assert gc_content("NNNN") == 0.0


def test_gc_content_lowercase():
    assert gc_content("ggcc") == pytest.approx(1.0)


# --- Phred ------------------------------------------------------------------

def test_phred_scores_offset():
    # 'I' is ASCII 73 -> Q40 ; '!' is ASCII 33 -> Q0 ; '5' is 53 -> Q20
    assert phred_scores("I!5") == [40, 0, 20]


# --- N50 --------------------------------------------------------------------

def test_n50_hand_computed():
    # lengths 10, 9, 2 -> total 21, half 10.5. Sorted desc: 10 (10 < 10.5), 9 (19 >= 10.5) -> 9
    assert n50([10, 9, 2]) == 9


def test_n50_single_contig():
    assert n50([7]) == 7


def test_n50_empty():
    assert n50([]) == 0


def test_n50_order_independent():
    assert n50([3, 5, 8, 1]) == n50([1, 3, 5, 8])


# --- summarise --------------------------------------------------------------

def test_summarise_fasta_records():
    recs = [
        Record("a", "", "ACGTACGTAC"),  # len 10, GC 5
        Record("b", "", "GGGGCCCC"),    # len 8, GC 8
    ]
    s = summarise(recs)
    d = s.as_dict()
    assert d["n_records"] == 2
    assert d["total_bases"] == 18
    # GC = (5+8)/(10+8) = 13/18
    assert d["gc_percent"] == pytest.approx(round(13 / 18 * 100, 2))
    assert d["mean_length"] == pytest.approx(9.0)
    assert d["min_length"] == 8 and d["max_length"] == 10
    # lengths 10, 8 -> total 18, half 9; 10 >= 9 -> N50 = 10
    assert d["n50"] == 10
    assert d["length_histogram"] == {8: 1, 10: 1}
    assert "mean_quality" not in d


def test_summarise_fastq_quality_hand_computed():
    # qualities 'IIII' = Q40 x4 ; '!!!!' = Q0 x4 -> mean = (160 + 0)/8 = 20
    recs = [
        Record("a", "", "ACGT", "IIII"),
        Record("b", "", "GGCC", "!!!!"),
    ]
    d = summarise(recs).as_dict()
    assert d["mean_quality"] == pytest.approx(20.0)
    # per position: pos0 (40+0)/2 = 20 for all four positions
    assert d["per_position_mean_quality"] == [20.0, 20.0, 20.0, 20.0]


def test_per_position_quality_handles_unequal_lengths():
    # rec1: Q40,Q40 ; rec2: Q20 -> pos0 = 30, pos1 = 40 (only rec1 has pos1)
    recs = [
        Record("a", "", "AC", "II"),
        Record("b", "", "A", "5"),
    ]
    d = summarise(recs).as_dict()
    assert d["per_position_mean_quality"] == [30.0, 40.0]


def test_summarise_empty_input():
    d = summarise([]).as_dict()
    assert d["n_records"] == 0
    assert d["total_bases"] == 0
    assert d["n50"] == 0
    assert d["gc_percent"] == 0.0


def test_gc_percent_is_monotonic_in_gc_bases():
    low = summarise([Record("a", "", "AAAATTTT")]).as_dict()["gc_percent"]
    high = summarise([Record("a", "", "GGGGCCCC")]).as_dict()["gc_percent"]
    assert low == 0.0
    assert high == 100.0


def test_n50_never_exceeds_max_length():
    lengths = [100, 90, 80, 5]
    assert n50(lengths) <= max(lengths)


def test_summarise_streams_generator():
    def gen():
        for i in range(5):
            yield Record(f"r{i}", "", "ACGT")

    d = summarise(gen()).as_dict()
    assert d["n_records"] == 5
    assert d["total_bases"] == 20


def test_mean_quality_matches_manual_arithmetic():
    qualities = "I5!5I"
    recs = [Record("a", "", "A" * len(qualities), qualities)]
    scores = [ord(c) - 33 for c in qualities]
    assert summarise(recs).as_dict()["mean_quality"] == pytest.approx(
        round(sum(scores) / len(scores), 2)
    )
    # hand arithmetic: [40, 20, 0, 20, 40] -> 120 / 5 = 24.0
    assert math.isclose(sum(scores) / len(scores), 24.0)
