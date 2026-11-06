# Validation — what was checked, how, and with what result

A tool is not validated because it has tests. It is validated when its outputs are compared against something **independent** and the comparison is published. This page records both.

## 1. Cross-validation against Biopython (external implementation)

Command (reproduce with `scripts/validate_against_biopython.py`, requires `pip install biopython`):

| Quantity | `bioflow` | Biopython (`SeqIO`) | Agreement |
|---|---|---|---|
| FASTQ records | 200 | 200 | exact |
| FASTQ total bases | 12 000 | 12 000 | exact |
| FASTQ GC% | 60.4 | 60.4 | exact to 2 dp |
| FASTQ mean Phred | 30.46 | 30.46 | exact to 2 dp |
| FASTQ per-position means | — | — | max abs diff 5.0×10⁻³ (rounding to 2 dp) |
| FASTA records | 12 | 12 | exact |
| FASTA total bases | 1 039 | 1 039 | exact |
| FASTA N50 | 102 | 102 | exact |

Date: 2026-11-06. Datasets: `datasets/sample/*` (simulated, fixed seed).
**What this establishes:** our parser and statistics agree with the field's reference library on the shipped data.
**What it does not establish:** correctness on adversarial inputs (that is the unit-test suite's job) or correctness of *definitions* (both implementations could be wrong the same way — hence the definitions are stated in the module and computed by hand in `tests/test_stats.py`).

## 2. Hand-computed unit tests

`tests/test_stats.py` contains cases whose expected values are derived by hand in the comments, e.g. lengths `[10, 9, 2]` → total 21 → half 10.5 → cumulative 10, then 19 ≥ 10.5 → N50 = 9. These catch definitional errors that cross-validation cannot.

## 3. Behavioural tests for the pipeline engine (65 tests total)

| Area | Tests | Key properties proven |
|---|---|---|
| Parsing | 13 | format detection, multi-line FASTA, gzip, malformed FASTQ raises, length-mismatch raises |
| Statistics | 13 | GC definition, N50 definition, Phred offset, empty input, generator streaming |
| DAG + execution | 15 | topological order, cycle detection, unsatisfiable input detected *before* running, failing step stops the pipeline, missing declared output is a failure |
| Caching | 4 | second run skips, changed input reruns, deleted output reruns, stamps record hashes |
| CLI | 20 | real argv/exit codes, JSON schema, error paths, `--dry-run`, `--jobs` honesty warning |

## 4. Reproducibility of the material itself

- `notebooks/01_unix_mindset.ipynb` executes end-to-end with 0 errors; it is re-executed in CI on every push.
- `scripts/make_figures.py` regenerates all three figures from data; CI fails if the figures change without a data or code change being committed.
- `scripts/make_sample_data.py` regenerates the datasets byte-identically (fixed seed).

## 5. Known limits of this validation

1. The datasets are **simulated**, so the validation says nothing about real instrument behaviour (quality-score drift, adapters, GC bias).
2. Biopython agreement is on 200 records × 60 bp — small; a large-file cross-check is part of Challenge 01.
3. No external reviewer has yet audited this repository. When one does, their name and comments will be recorded here **only with their consent**.
4. Performance is not benchmarked beyond the memory demonstration in Practical 02; Challenge 01 requires real numbers.
