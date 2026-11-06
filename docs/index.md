# CLS-Open #8 — Linux, Git and Reproducible Workflows for Bioinformatics

A beginner course that treats the command line, version control and workflow files as **scientific instruments**, not incidental plumbing.

!!! warning "Honest version status — v0.1.0"
    **Module 1 is complete** (13-part lesson, executed notebook, two guided practicals, assignment, challenge, quiz, instructor pack). **Modules 2–9 are specified but not yet written** — see [Roadmap](roadmap.md). Nothing in this repository is a placeholder pretending to be a lesson.

## Start here

| If you are… | Go to |
|---|---|
| a life-science student with no terminal experience | [Installation](installation.md) → [Module 1](modules/01-unix-mindset.md) |
| a researcher who "uses the command line a bit" | [Prerequisites](prerequisites.md) self-check → Practical 01 |
| an instructor | [Instructor pack](instructor/teaching-plans.md) (12/24/36-hour plans, marking load) |
| a reviewer or contributor | [Validation](validation.md) · [Limitations](limitations.md) · [References](references.md) |
| looking for the software | `pip install -e .` then `bioflow --help` |

## What makes this repository different

1. **Every number is recomputed by CI.** The notebooks execute on every push; if an example breaks, the build fails.
2. **Disagreement is taught, not hidden.** The record-count trap (200 vs 204) is a lesson, not an erratum.
3. **Two real bugs found while writing the material are documented** — one in our own pipeline engine, one in an "obvious" GC one-liner — because a course that shows only clean code teaches the wrong instinct.
4. **Validation against an independent implementation** (Biopython) with published numbers, not a claim.
5. **Assessment that instructors can actually use**: rubrics, answer keys, common wrong answers, marking-load estimates.

## Repository map

- **Lessons** — [Module 1: The Unix mindset](modules/01-unix-mindset.md)
- **Practicals** — [01 counting and composition](practicals/practical-01-counting-and-composition.md) · [02 pipes and streams](practicals/practical-02-pipes-and-streams.md)
- **Assessments** — [Assignment](assessments/assignment-01-shell-audit.md) · [Challenge](assessments/challenge-01-streaming-qc.md) · [Quiz + key](assessments/quiz-01-module1.md)
- **Projects** — [mini-project](../projects/mini_projects/README.md) · [capstone](../projects/capstone/README.md)
- **Software** — `src/bioflow/` · [validation](validation.md) · [limitations](limitations.md)
- **Data** — [datasets README](../datasets/README.md)

## Licence and citation

Content CC BY 4.0; code MIT. Cite the release you used — see `CITATION.cff`. No citation or backlink is required to use the material for learning.
