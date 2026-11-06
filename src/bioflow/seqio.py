"""Sequence-file parsing: FASTA and FASTQ, optionally gzip-compressed.

Design notes
------------
* Records are yielded lazily, so a 2 GB FASTQ is processed in constant memory.
* Format is detected from the first non-empty character, not from the file
  extension. A file named ``reads.fastq`` that actually contains FASTA is a
  common real-world error, and silently mis-parsing it is worse than failing.
* No third-party dependency is used. That is deliberate: the learner should be
  able to check every line against the specification.
"""

from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TextIO


class SequenceFormatError(ValueError):
    """Raised when a file does not conform to FASTA or FASTQ."""


@dataclass(frozen=True, slots=True)
class Record:
    """One sequence record.

    Attributes
    ----------
    id:
        The first whitespace-delimited token of the header.
    description:
        The remainder of the header line (may be empty).
    sequence:
        Upper-case sequence with whitespace removed.
    qualities:
        FASTQ quality characters as raw ASCII, or ``None`` for FASTA.
        Use :func:`bioflow.stats.phred_scores` to convert.
    """

    id: str
    description: str
    sequence: str
    qualities: str | None = None

    @property
    def length(self) -> int:
        return len(self.sequence)

    @property
    def is_fastq(self) -> bool:
        return self.qualities is not None


def _open_text(path: str | Path) -> TextIO:
    path = Path(path)
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("rt", encoding="utf-8")


def detect_format(path: str | Path) -> str:
    """Return ``"fasta"`` or ``"fastq"`` by inspecting the first record."""
    with _open_text(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                return "fasta"
            if line.startswith("@"):
                return "fastq"
            raise SequenceFormatError(
                f"{path}: first non-empty line starts with {line[0]!r}; "
                "expected '>' (FASTA) or '@' (FASTQ)"
            )
    raise SequenceFormatError(f"{path}: file contains no records")


def _parse_header(raw: str) -> tuple[str, str]:
    raw = raw[1:].strip()
    if not raw:
        raise SequenceFormatError("empty FASTA/FASTQ header")
    parts = raw.split(maxsplit=1)
    return parts[0], (parts[1] if len(parts) > 1 else "")


def read_fasta(handle: TextIO) -> Iterator[Record]:
    header: str | None = None
    chunks: list[str] = []
    for line_no, line in enumerate(handle, start=1):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if header is not None:
                rid, desc = _parse_header(header)
                yield Record(rid, desc, "".join(chunks).upper())
            header, chunks = line, []
        elif line.strip():
            if header is None:
                raise SequenceFormatError(f"line {line_no}: sequence data before first header")
            chunks.append(line.strip())
    if header is not None:
        rid, desc = _parse_header(header)
        yield Record(rid, desc, "".join(chunks).upper())


def read_fastq(handle: TextIO) -> Iterator[Record]:
    while True:
        header = handle.readline()
        if not header:
            return
        if not header.strip():
            continue
        seq = handle.readline()
        plus = handle.readline()
        qual = handle.readline()
        if not header.startswith("@"):
            raise SequenceFormatError(f"FASTQ record does not start with '@': {header[:40]!r}")
        if not plus.startswith("+"):
            raise SequenceFormatError(f"FASTQ record missing '+' separator: {plus[:40]!r}")
        sequence = seq.strip().upper()
        qualities = qual.rstrip("\n")
        if len(sequence) != len(qualities):
            raise SequenceFormatError(
                f"sequence/quality length mismatch for {header.strip()!r}: "
                f"{len(sequence)} vs {len(qualities)}"
            )
        rid, desc = _parse_header(header)
        yield Record(rid, desc, sequence, qualities)


def read_records(path: str | Path) -> Iterator[Record]:
    """Parse any supported sequence file, detecting the format automatically."""
    fmt = detect_format(path)
    with _open_text(path) as handle:
        if fmt == "fasta":
            yield from read_fasta(handle)
        else:
            yield from read_fastq(handle)
