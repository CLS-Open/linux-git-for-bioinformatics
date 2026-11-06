# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- Module 2 (bash scripting that fails safely) and Module 3 (remote machines).
- Practicals 3–5, assignments 2–3, challenge 02.
- Streaming N50 (see `docs/assessments/challenge-01-streaming-qc.md`).

## [0.1.0] — 2026-11-06

### Added
- **Module 1**: "The Unix mindset: files, pipes and biological text" — full 13-part lesson
  (`docs/modules/01-unix-mindset.md`) with executed companion notebook.
- **`bioflow` 0.1.0**: streaming FASTA/FASTQ parser (gzip-aware), sequence statistics
  (GC%, N50, Phred profile), and a declarative YAML pipeline engine with DAG validation,
  cycle detection, content-hash caching and a provenance log. CLI: `stats`, `plan`, `run`.
- 65 tests covering parsing, statistics, DAG behaviour, caching, CLI and validation.
- Validation of `bioflow stats` against Biopython on shipped data (`docs/validation.md`).
- Two guided practicals, one independent assignment, one challenge, a Level-1 quiz with
  answer key, and an instructor pack (12/24/36-hour plans, marking load).
- Mini-project and capstone specifications.
- Simulated datasets with a committed, deterministic generator and metadata.
- Three figures, regenerated from data by script (never hand-edited).
- CI: test matrix, notebook execution, figure reproducibility, link check, docs deploy.

### Fixed (found while developing the material — kept as documented lessons)
- Pipeline command rendering used `str.format`, which raised `KeyError` on shell commands
  containing braces (e.g. `awk`). Now explicit placeholder substitution, with regression test.
- Test expectations that were arithmetically wrong were corrected rather than "made to pass":
  a FASTQ mean-quality expectation (24.0, not 20.0) and an awk program missing its pattern.

### Known limitations
- Sequential execution only; no containers, wildcards, cluster execution or BAM/VCF support.
- Modules 2–9 specified but not written (`docs/roadmap.md`).
- No cohort-based learning-outcome data; no efficacy claim is made.
