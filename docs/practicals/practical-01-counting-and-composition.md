# Practical 01 — Counting and composition on real file structure

**Module:** 1 · **Level:** L2 (guided practical) · **Time:** 45 min · **Dataset:** `datasets/sample/reads.fastq`

## Aim

Produce three numbers about a FASTQ file — record count, GC fraction, mean read length — by **two independent routes** (POSIX tools, then `bioflow`), and reconcile any disagreement.

## Instructions

Work in a scratch directory. Keep a file `practical01.sh` containing every command you run, in order, with `set -euo pipefail` at the top. At the end, run `bash practical01.sh > practical01_output.txt 2>&1` — that file is what you submit.

1. **Inspect before computing.** Print the first four lines. State in one sentence what each line is.
2. **Count records two ways.** `wc -l` and `grep -c '^@'`. Record both numbers.
3. **Explain the difference.** Find *which* lines are being over-counted:
   ```bash
   awk 'NR%4==0 && /^@/ {print NR": "$0}' datasets/sample/reads.fastq | head
   ```
   Write one sentence explaining, in terms of the FASTQ specification, why this happens.
4. **GC fraction.** Compute with `awk` (see Module 1 §6). Then compute with `bioflow stats --json` and compare to 4 decimal places.
5. **Deliberately break it.** Run the buggy variant from the notebook (`length($0)` *after* the substitutions). Record the impossible value you get and explain the mechanism.
6. **Mean read length.** One-liner it. Confirm against `bioflow stats`.

## Deliverables

1. `practical01.sh` (re-runnable, no hard-coded absolute paths).
2. `practical01_output.txt`.
3. A 150–200 word note answering: which record count would you report, and what would you tell a collaborator who asked "why do I get 204?"

## Rubric (10 points)

| Criterion | Points | What earns full marks |
|---|---|---|
| Script runs end-to-end from a clean shell | 2 | `set -euo pipefail`; no absolute paths; idempotent |
| Both counting methods, with explanation | 2 | Correctly identifies Phred+33 `@` as the cause |
| GC cross-check | 2 | Agreement stated to 4 dp with the exact values |
| Bug reproduction + mechanism | 2 | Explains `gsub` mutating `$0`, not merely "it was wrong" |
| Written judgement | 2 | Clear, quantified, no hedging without a number |

## Common wrong answers (instructor note)

- "204 because of the `+` line" — no: check which lines are matched.
- Reporting `grep -c` as the record count without comment.
- Comparing GC by eye ("about 60%") instead of stating tolerance.

## Extension

Repeat for `proteins.fasta`. FASTA has no quality lines — predict whether the two methods agree, then test your prediction. If they disagree, why?
