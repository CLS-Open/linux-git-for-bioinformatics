"""Tests for bioflow.seqio — parsing correctness and failure modes."""

from __future__ import annotations

import gzip

import pytest

from bioflow.seqio import SequenceFormatError, detect_format, read_records


FASTA = ">seq1 first sequence\nACGTACGTAC\n>seq2\nGGGGCCCC\n"
FASTQ = "@read1 desc\nACGT\n+\nIIII\n@read2\nGGCC\n+\n!!!!\n"


def test_detect_format_fasta(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text(FASTA)
    assert detect_format(p) == "fasta"


def test_detect_format_fastq(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text(FASTQ)
    assert detect_format(p) == "fastq"


def test_detect_format_ignores_leading_blank_lines(tmp_path):
    p = tmp_path / "x.fa"
    p.write_text("\n\n" + FASTA)
    assert detect_format(p) == "fasta"


def test_detect_format_rejects_garbage(tmp_path):
    p = tmp_path / "x.fa"
    p.write_text("ACGT\n")
    with pytest.raises(SequenceFormatError):
        detect_format(p)


def test_detect_format_rejects_empty(tmp_path):
    p = tmp_path / "x.fa"
    p.write_text("\n\n")
    with pytest.raises(SequenceFormatError):
        detect_format(p)


def test_fasta_records(tmp_path):
    p = tmp_path / "s.fa"
    p.write_text(FASTA)
    recs = list(read_records(p))
    assert [r.id for r in recs] == ["seq1", "seq2"]
    assert recs[0].description == "first sequence"
    assert recs[0].sequence == "ACGTACGTAC"
    assert recs[0].qualities is None
    assert recs[1].description == ""


def test_fasta_multiline_sequence_is_joined(tmp_path):
    p = tmp_path / "s.fa"
    p.write_text(">a\nACGT\nACGT\nAC\n")
    assert list(read_records(p))[0].sequence == "ACGTACGTAC"


def test_fasta_lowercase_is_normalised(tmp_path):
    p = tmp_path / "s.fa"
    p.write_text(">a\nacgt\n")
    assert list(read_records(p))[0].sequence == "ACGT"


def test_fastq_records(tmp_path):
    p = tmp_path / "s.fq"
    p.write_text(FASTQ)
    recs = list(read_records(p))
    assert recs[0].id == "read1"
    assert recs[0].description == "desc"
    assert recs[0].qualities == "IIII"
    assert recs[1].qualities == "!!!!"
    assert all(r.is_fastq for r in recs)


def test_fastq_length_mismatch_raises(tmp_path):
    p = tmp_path / "bad.fq"
    p.write_text("@r\nACGT\n+\nIII\n")
    with pytest.raises(SequenceFormatError, match="length mismatch"):
        list(read_records(p))


def test_fastq_missing_plus_raises(tmp_path):
    p = tmp_path / "bad.fq"
    # second record has no '+' line
    p.write_text("@r\nACGT\nACGT\nIIII\n")
    with pytest.raises(SequenceFormatError):
        list(read_records(p))


def test_gzip_fasta(tmp_path):
    p = tmp_path / "s.fa.gz"
    with gzip.open(p, "wt") as fh:
        fh.write(FASTA)
    assert len(list(read_records(p))) == 2


def test_gzip_fastq(tmp_path):
    p = tmp_path / "s.fq.gz"
    with gzip.open(p, "wt") as fh:
        fh.write(FASTQ)
    assert len(list(read_records(p))) == 2


def test_empty_fasta_record_sequence(tmp_path):
    p = tmp_path / "e.fa"
    p.write_text(">a\n>b\nACGT\n")
    recs = list(read_records(p))
    assert recs[0].sequence == ""
    assert recs[0].length == 0
    assert recs[1].sequence == "ACGT"
