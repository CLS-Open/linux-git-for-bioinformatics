# Assignment 01 — Reproducibility audit of a shell-based analysis

**Level:** L3 (independent) · **Weight:** 15% of the course · **Time:** 3–4 hours · **Due:** end of Module 2

## Scenario

A collaborator sends you this, claiming they "did the QC":

```bash
fastqc *.fastq -o ~/qc
cat *.fastq | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -20 > duplicates.txt
multiqc ~/qc -o ~/qc/summary
```

They cannot reproduce their own `duplicates.txt` two weeks later.

## Task

Write `audit.md` (900–1100 words) plus any scripts, containing:

1. **Failure analysis.** Identify at least **five** distinct reproducibility or correctness defects in the snippet. For each: the defect, the concrete failure scenario, and the minimal fix. Candidates worth considering include wildcard expansion order, `cat` of gzipped files, `cut` on FASTQ header semantics, memory behaviour of `sort`, output paths outside the project, absence of pinned tool versions, missing checksums, and locale-dependent sorting.
2. **Corrected workflow.** Provide a `workflow/` directory with:
   - `pipeline.yml` (bioflow schema) or a `Snakefile` if you prefer — state which and why;
   - a `README.md` stating inputs, outputs and how to verify success;
   - `run.sh` that fails fast (`set -euo pipefail`) and logs tool versions to `versions.txt`.
3. **Verification.** Demonstrate that running your workflow twice produces identical outputs (hash them), and that changing one input changes exactly the expected outputs.
4. **Honest limits.** Two paragraphs on what your audit *cannot* detect (e.g. wrong biological assumptions, batch effects, contamination).

## Deliverables

```text
audit.md
workflow/{pipeline.yml|Snakefile, run.sh, README.md}
evidence/{hashes_before.txt, hashes_after.txt, versions.txt, rerun_diff.txt}
```

## Rubric (20 points)

| Criterion | Points |
|---|---|
| Five defects, each with scenario + fix (2 each) | 10 |
| Corrected workflow runs from clean state | 3 |
| Determinism evidenced by hashes | 3 |
| Tool-version capture | 1 |
| Honest limitations | 2 |
| Writing clarity (no unquantified claims) | 1 |

## Reproducibility requirement

Your submission must run on a machine that is not yours. Test it in a fresh directory or container before submitting; state in `audit.md` that you did so and what broke.

## Extension (bonus, 3 points)

Add a GitHub Actions workflow that runs your corrected pipeline on push and fails if outputs change unexpectedly. Include the badge.
