# Contributing

Thank you for considering a contribution. This repository is part of the CLS-Open
initiative: 15 interlinked open courses across the computational life sciences.

## The contributions we most want

| Priority | Contribution | How |
|---|---|---|
| 1 | **Scientific or factual errors** | Open a "Content error" issue quoting the file and line |
| 2 | **Broken commands / non-reproducible examples** | Issue or PR; CI should have caught it, so this is a genuine bug |
| 3 | **Accessibility problems** (colour, contrast, screen readers, bandwidth) | Issue labelled `accessibility` |
| 4 | **Adoption reports** ("I taught this to N students; here is what broke") | Issue labelled `adoption` |
| 5 | New lessons, practicals, translations | Discuss in an issue *before* writing; see below |

## Before you write a lesson

Open an issue with the title `proposal: <module/lesson title>` containing:
1. the learning objective(s), stated as measurable outcomes;
2. what already exists (with links) and why it is insufficient — this project
   is not allowed to duplicate good existing material;
3. the dataset, with licence and accession;
4. how a learner can verify their answer.

We will respond with a scope decision. This prevents the most common form of
wasted effort in OER: two people writing the same mediocre lesson.

## Standards every PR must meet

- `pytest -q` passes; new code has tests with hand-computed expectations where
  arithmetic is involved.
- Notebooks execute: `jupyter nbconvert --execute` or CI's notebook job.
- New datasets: <5 MB shipped, with `datasets/metadata/<name>.yml` (source,
  licence, accession, sha256) and a generator script if simulated.
- Claims are cited: every scientific statement that is not common knowledge has
  a reference that resolves via Crossref/Europe PMC, added to `docs/references.md`.
- No fabricated data, text, or references. Ever. This will be caught and it
  ends the contribution.
- Synthetic data is labelled synthetic in the data file *and* every figure.
- Commit messages: imperative mood, one logical change.

## Licensing of contributions

By submitting a PR you agree your code contribution is MIT and your content
contribution is CC BY 4.0 (inbound = outbound). You retain copyright; you grant
the project the right to distribute under those licences.

## Review process

- One maintainer review minimum; scientific content requires a second reviewer
  with relevant expertise.
- Reviewers check: correctness, reproducibility, citation validity, accessibility,
  and whether the material duplicates existing resources.
- Reviewers are named in the PR. We do not add reviewers as authors for
  reviewing alone.

## Recognition

Contributors are listed in `docs/contributors.md` (once the first external
contribution lands) with the contribution type. Authorship on any future
publication is decided by the criteria in the initiative's authorship policy —
substantial intellectual contribution, not volume of commits.

## Code of conduct

Participation is governed by `CODE_OF_CONDUCT.md`. Reports go to the contact
address in that file; do not open a public issue for a conduct report.
