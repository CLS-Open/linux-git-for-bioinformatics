# Practical 02 — Pipes, streams and constant memory

**Module:** 1 · **Level:** L2 (guided practical) · **Time:** 45 min · **Dataset:** `datasets/sample/reads.fastq`

## Aim

Demonstrate — not assert — that a pipe processes data without loading it into memory, and that a pipeline file can replace a shell history.

## Instructions

1. **Measure, don't assume.** Compare peak memory of two ways to find the longest read:
   ```bash
   /usr/bin/time -v awk 'NR%4==2 {if (length($0)>m) m=length($0)} END{print m}' datasets/sample/reads.fastq 2>&1 | grep -E "Maximum resident|^[0-9]+"
   ```
   Then do the same with a Python list comprehension that materialises every read. Record both peak-RSS figures. (On macOS use `/usr/bin/time -l`; state which you used.)

2. **Build a stream.** Write a single pipeline that prints the number of reads whose mean Phred is below 30, using only POSIX tools (`awk`, no Python). Hint: compute per-read mean quality from line 4, compare, count.

3. **Verify against the library.** Confirm your number with `bioflow stats --json` (compute per-read means from `per_position_mean_quality`? No — that is *per position*; explain why your POSIX answer cannot be reproduced from that field, then write three lines of Python that compute the per-read means properly).

4. **Truncation hazards.** Create `test.txt` with three lines. Run `grep -v zzz test.txt > test.txt`. Explain what you observe and why (`>` truncates before the left side reads).

5. **Make it a pipeline.** Write `practical02.yml` with three steps:
   - `per_read_quality` → `results/per_read.txt`
   - `low_quality_count` → `results/low_quality_count.txt` (depends on the first)
   - `summary` → `results/summary.txt` (depends on both)
   Run `bioflow plan` before `bioflow run`, and run twice to prove caching.

## Deliverables

1. A markdown report with the two peak-RSS numbers, the pipeline one-liner, the verification numbers, and the truncation explanation.
2. `practical02.yml`, plus `bioflow plan` output.
3. One paragraph: *why* does the streaming version use less memory, in terms of the kernel buffer and process lifetimes?

## Rubric (10 points)

| Criterion | Points | What earns full marks |
|---|---|---|
| Memory measurement actually performed | 2 | Numbers reported, method and platform named |
| POSIX-only pipeline works | 2 | Correct handling of quality line; no Python |
| Verification, including the per-position vs per-read distinction | 3 | Recognises that `per_position_mean_quality` is a different quantity |
| Truncation behaviour explained | 1 | Mentions shell opening order |
| Pipeline YAML valid and cached on second run | 2 | `bioflow plan` clean; second run reports skips |

## Note on `per_position_mean_quality`

This is the most common conceptual error in FASTQ QC: `per_position_mean_quality[i]` is the mean over *reads* at *position i* — useful for trimming decisions. The mean of a *single read* is a different statistic, and the mean of all bases (what `bioflow stats` reports as `mean_quality`) is a third. Three quantities, three meanings, one ambiguous phrase ("mean quality"). Say which you mean.
