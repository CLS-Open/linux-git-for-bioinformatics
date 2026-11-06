#!/usr/bin/env python3
"""CI guard 1 — every shipped dataset must have valid metadata with a matching sha256.

Rationale: a datasets/README.md that silently becomes false is worse than no
README. This check makes the README's claims machine-verified.

Exit code 0 = all good; 1 = problems (printed).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "datasets" / "sample"
META_DIR = ROOT / "datasets" / "metadata"
REQUIRED_KEYS = {"name", "path", "format", "synthetic", "licence", "contains_personal_data", "source"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    problems: list[str] = []
    data_files = sorted(p for p in DATA_DIR.iterdir() if p.is_file())
    meta_files = sorted(META_DIR.glob("*.yml")) if META_DIR.exists() else []

    print(f"data files: {len(data_files)}  metadata files: {len(meta_files)}")

    covered: set[str] = set()
    for meta_path in meta_files:
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        missing = REQUIRED_KEYS - set(meta)
        if missing:
            problems.append(f"{meta_path.name}: missing keys {sorted(missing)}")
            continue
        target = ROOT / meta["path"]
        if not target.exists():
            problems.append(f"{meta_path.name}: refers to missing file {meta['path']}")
            continue
        covered.add(target.name)
        # A synthetic-data flag must be explicit for every file that is not real data.
        if meta.get("synthetic") is not True:
            problems.append(
                f"{meta_path.name}: synthetic is not explicitly true — real data needs "
                "accession, licence and data-use terms before it may be shipped"
            )
        if meta.get("contains_personal_data") is not False:
            problems.append(f"{meta_path.name}: contains_personal_data must be stated (false expected here)")
        recorded = meta.get("sha256")
        if recorded:
            actual = sha256(target)
            if recorded != actual:
                problems.append(
                    f"{meta_path.name}: sha256 mismatch for {meta['path']}\n"
                    f"    recorded {recorded}\n    actual   {actual}\n"
                    "    (regenerate the metadata or the data — do not edit the hash to match)"
                )
        else:
            print(f"note: {meta_path.name} has no sha256 yet -> {sha256(target)}")

    for f in data_files:
        if f.name not in covered:
            problems.append(f"datasets/sample/{f.name}: no metadata entry in datasets/metadata/")

    if problems:
        print("\nFAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK: every dataset has metadata; all recorded hashes match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
