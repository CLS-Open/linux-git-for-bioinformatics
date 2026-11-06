# Repository README — Linux, Git and Reproducible Workflows for Bioinformatics

**CLS-Open repository #8 of 15** · Level: **beginner** · Status: **v0.1.0 (honest launch standard: Module 1 complete, Modules 2–9 specified)**

> A first-principles, CI-tested course on the command line, version control and workflow management — using biological data, and enforcing the reproducibility practices that most tutorials only mention.

---

## What you get in v0.1.0

| Component | Status |
|---|---|
| **Module 1** — The Unix mindset: files, pipes and biological text | ✅ complete (13-part lesson + executed notebook) |
| **`bioflow`** — pipeline runner + sequence QC toolkit | ✅ working, 65 tests, validated against Biopython |
| Guided practicals 1 and 2 | ✅ complete |
| Independent assignment + challenge 1 | ✅ complete |
| Level-1 quiz + capstone and mini-project specifications | ✅ complete |
| Instructor pack (12/24/36-hour plans, marking load) | ✅ complete |
| Modules 2–9 (bash scripting, remote work, environments, Git, GitHub collaboration, Snakemake, Slurm, CI) | 🗺️ specified in [`docs/roadmap.md`](docs/roadmap.md) — not yet written |

We publish early and state what is missing. If a module is not in the table above, it is not in the repository.

## Why this repository exists

Most bioinformatics teaching assumes you already live in a terminal. Most terminal teaching uses `~/tmp/file.txt` and never touches a FASTQ. This repository closes both gaps at once, and it enforces a rule that the reproducibility literature recommends but curricula rarely implement: **every lesson's numbers are recomputed by CI**, so a broken example cannot silently survive.

## Install

```bash
git clone https://github.com/cls-open/linux-git-for-bioinformatics.git
cd linux-git-for-bioinformatics
python -m venv .venv && source .venv/bin/activate     # Windows: use WSL2
pip install -e ".[dev]"
bioflow --version      # bioflow 0.1.0
```

Windows note: use WSL2. The course teaches a POSIX shell; Git Bash will produce confusing failures.

## Run in five minutes

```bash
# 1. Sequence statistics on a shipped (simulated) FASTQ
bioflow stats datasets/sample/reads.fastq

# 2. Dependency-ordered pipeline, twice (second run skips everything)
bioflow plan examples/pipeline.yml
bioflow run  examples/pipeline.yml
bioflow run  examples/pipeline.yml

# 3. The flagship lesson, executed
jupyter lab notebooks/01_unix_mindset.ipynb

# 4. Regenerate every figure from data
python scripts/make_figures.py
```

Expected output for step 1 is in [`docs/modules/01-unix-mindset.md` §7](docs/modules/01-unix-mindset.md).

## The `bioflow` tool

`bioflow` is deliberately small enough to read in one sitting — the pedagogical point is that a workflow manager is not magic.

```text
bioflow stats <file> [--json]     sequence QC: records, bases, GC%, N50, Phred profile
bioflow plan  <pipeline.yml>      show derived execution order (validates first)
bioflow run   <pipeline.yml>      execute, skipping up-to-date steps; writes provenance log
```

**Validation.** `bioflow stats` was cross-checked against Biopython (`SeqIO`) on the shipped datasets: record counts, total bases, GC%, mean Phred and per-position means agree to <1×10⁻² (float rounding only), and N50 agrees exactly. See [`docs/validation.md`](docs/validation.md) for the numbers and the commands that produced them.

**Documented limitations** (not bugs — design boundaries): sequential execution only (`--jobs` accepted and ignored), no containers, no cluster submission, no wildcard rules, `shell=True` execution. See [`docs/limitations.md`](docs/limitations.md).

Two real bugs were found by *running* this material, and both are now lessons:
- `str.format` broke on `awk` braces → placeholders are substituted explicitly, with a regression test.
- `gsub()` mutates `$0`, so an "obvious" GC one-liner returned 152% → the buggy and fixed versions are both in the notebook, because impossible numbers are how you learn to distrust plausible ones.

## Data

| File | Records | Size | Provenance |
|---|---|---|---|
| `datasets/sample/reads.fastq` | 200 reads × 60 bp | 34 KB | **Simulated** (fixed seed) by `scripts/make_sample_data.py` |
| `datasets/sample/proteins.fasta` | 12 sequences | 1.8 KB | **Simulated** |
| `datasets/sample/contigs.fasta` | 3 contigs | 302 B | **Simulated** |

**These are simulated sequences, not experimental measurements**, and are labelled as such in every figure. Their purpose is to make every number in the lessons exactly reproducible on any machine, including one with no internet connection.

## Repository structure

```text
docs/            MkDocs site: modules, tutorials, practicals, assessments, instructor pack
notebooks/       executed notebooks (source of truth: the .py percent files next to them)
src/bioflow/     the installable package (seqio, stats, pipeline, cli)
tests/           65 tests: parsing, statistics, DAG behaviour, CLI, validation
datasets/        simulated data + metadata (licence, checksum, provenance)
examples/        pipeline.yml used throughout the lessons
scripts/         make_sample_data.py, make_figures.py (figures are regenerated, never hand-edited)
projects/        mini-project and capstone specifications
```

## Learning path

```text
Module 1 (this repo, now)
   ├── → Module 2 bash scripting → Module 3 remote work → Module 4 environments
   ├── → Module 5 Git → Module 6 GitHub collaboration
   └── → Module 7 Snakemake → Module 8 Slurm/HPC → Module 9 CI
                     ↓
   feeds: #4 bioinformatics-foundations, #11 genomics-and-ngs-analysis
```

## Contributing

Corrections are genuinely welcome — especially **scientific errors, broken commands, and accessibility problems**. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and the code of conduct first. Every pull request must keep `pytest` and notebook execution green.

Learners: publish your completed capstone on your own GitHub profile. You may cite this repository using the DOI of the release you used (see [`CITATION.cff`](CITATION.cff)). **You are not required to cite anything you did not use**, and no backlink is expected in exchange for the material.

## Licence

Content (prose, figures, notebooks' markdown): **CC BY 4.0** · Code (`src/`, `tests/`, `scripts/`): **MIT**. See [`LICENSES/README.md`](LICENSES/README.md).

## Citation

```bibtex
@software{cls_open_linux_git_2026,
  title  = {Linux, Git and Reproducible Workflows for Bioinformatics (CLS-Open)},
  author = {Tolulope, Ademola Emmanuel},
  year   = {2026},
  version = {0.1.0},
  url    = {https://github.com/cls-open/linux-git-for-bioinformatics}
}
```

*Part of the [CLS-Open](https://github.com/cls-open) initiative: 15 interlinked, executable open courses across computational life sciences.*
