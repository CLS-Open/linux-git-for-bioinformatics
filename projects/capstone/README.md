# Capstone — a reproducible, audited mini-analysis you could hand to a collaborator

**Level:** L5 · **Time:** 20–30 hours · **Prerequisite:** Modules 1–7 of this repository (or equivalent), plus a domain question from another CLS-Open course.

## The brief

Take **one small biological question** answerable from public data, and deliver an analysis
that a stranger can re-run on their own machine and get the same numbers.

You choose the question. It must be small enough to finish (a single gene family, one
public run, one handful of sequences) and specific enough to be wrong-able:

> *"GC content of the shipped simulated reads is 60.4%"* — too small.
> *"Which of these 12 public genomes have GC content above 50%?"* — good.
> *"Is GC content correlated with optimal growth temperature across these genomes?"* — good,
> and requires you to state a test and its assumptions.

## Required components

1. **Question and design** (`01_question.md`): the question, why it matters, the unit of
   analysis, the pre-specified decision rule, and what result would falsify your hypothesis.
2. **Data provenance** (`02_data.md`): accessions, retrieval commands, checksums, licences,
   and what you *chose not to use* and why.
3. **Pipeline** (`03_pipeline/`): declared inputs/outputs, pinned environment, one command
   to reproduce everything from raw to final.
4. **Validation** (`04_validation.md`): how you know your numbers are right — an independent
   implementation, a hand calculation, or a positive/negative control. State which you used
   and what it does *not* prove.
5. **Results** (`05_results.md`): figures with units, n, and uncertainty; a table of numbers;
   no p-values without an effect size.
6. **Limitations** (`06_limitations.md`): at least four, each concrete ("my sampling excludes
   plasmids, so GC is genome-chromosomal only") rather than ritual.
7. **Reproducibility statement** (`07_reproducibility.md`): fresh-clone test, timing, and the
   exact commands. Include the hash of your outputs.
8. **Self-audit** (`08_audit.md`): score your own submission against this rubric and say where
   you would mark yourself down.

## Rubric (60 points)

| Criterion | Points | Excellent looks like |
|---|---|---|
| Question is specific and falsifiable | 6 | A stranger can tell what would count as "no" |
| Data provenance complete | 8 | Accessions, licences, checksums, exclusion rationale |
| Pipeline reproduces from clean clone | 12 | One command; documented time and size |
| Validation is independent | 10 | A second implementation or a control, with the numbers |
| Figures and statistics honest | 10 | Uncertainty shown; effect sizes; no over-claiming |
| Limitations are concrete | 6 | Each one is specific to *your* analysis |
| Writing and structure | 4 | Someone outside the field can follow the question |
| Self-audit is candid | 4 | Names a real weakness, not a humble-brag |

## Submission structure

```text
capstone-<yourname>/
├── 01_question.md … 08_audit.md
├── 03_pipeline/{pipeline.yml, environment.yml, run.sh}
├── data/{raw/ (not committed), processed/, checksums.sha256}
├── figures/*.png + figures/make_figures.py
└── README.md   <- the five-minute reproduction guide
```

Publish on your own GitHub profile if you wish. **You are not required to publish**, and
you are not required to cite this repository unless you actually used it.

## What this capstone deliberately does not do

It does not simulate a "big data" project. It trains the thing that fails most often in real
research: a small analysis, done honestly, that someone else can re-run. Get that right and
scale is an engineering problem; get it wrong and scale only produces faster wrongness.
