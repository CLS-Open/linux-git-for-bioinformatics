# Roadmap — what exists, what is next, and when

**Principle:** this file is a contract with the reader. Anything listed as *not started* is genuinely absent from the repository.

## Status at v0.1.0 (2026-11-06)

| Module | Title | Status | Target release |
|---|---|---|---|
| 1 | The Unix mindset: files, pipes and biological text | ✅ **complete** | 0.1.0 |
| 2 | Bash scripting that fails safely (`set -euo pipefail`, `bats` tests) | 🟡 outlined (practical 01/02 cover the essentials) | 0.2.0 |
| 3 | Working on remote machines (`ssh`, `tmux`, `rsync`, `scp`) | ⬜ not started | 0.2.0 |
| 4 | Environments and containers (`venv`, `uv`, `conda`/`mamba`, Docker) | ⬜ not started | 0.3.0 |
| 5 | Git: because your future self is a stranger | ⬜ not started | 0.3.0 |
| 6 | GitHub collaboration: issues, PRs, review, CODEOWNERS | ⬜ not started | 0.3.0 |
| 7 | Workflow managers: Snakemake (and why `bioflow` is not one) | ⬜ not started | 0.4.0 |
| 8 | HPC and Slurm: job arrays, resources, queue etiquette | ⬜ not started | 0.4.0 |
| 9 | CI for scientists: GitHub Actions that run your analysis | ⬜ not started | 0.5.0 |

## Also planned

- Guided practicals 3–5 (Git conflict surgery; a Snakemake rewrite of the example pipeline; a Slurm job array).
- Independent assignments 2–3.
- Challenge 02 (build a reproducible analysis container).
- Mini-project 2 (audit a public repository's reproducibility).
- A worked capstone exemplar (not a solution to the capstone — an *unrelated* worked example).

## What will change this roadmap

- **Adoption reports** from instructors reorder the modules (if a cohort needs remote work first, Module 3 moves up).
- **Issue reports** can promote anything: if three learners independently fail at the same step, that step becomes a priority, not a footnote.

## How to hold us to this

Each release is tagged and has a `CHANGELOG` entry. If a release slips, the tag simply is not created — we do not move a date quietly. Open an issue titled `roadmap: <module>` if a target has passed.
