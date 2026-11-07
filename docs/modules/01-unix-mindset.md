# Module 1 — The Unix mindset: files, pipes and biological text

> **Level:** beginner · **Time:** 3–4 hours · **Dataset:** `datasets/sample/reads.fastq` (200 simulated reads), `datasets/sample/proteins.fasta`, `datasets/sample/contigs.fasta`
> **Executable companion:** [`notebooks/01_unix_mindset.ipynb`](https://github.com/CLS-Open/linux-git-for-bioinformatics/blob/main/notebooks/01_unix_mindset.ipynb) — every number below is reproduced there by CI.

## 1. Scientific background

Almost every file you will touch as a computational biologist is a **line-oriented text file**: FASTA, FASTQ, GFF3, VCF, SAM, BED, Newick, PDB. The format families differ, but they share a design decision made in the 1970s: *one record per line, or a fixed number of lines per record, delimited by characters rather than length fields*. That decision is why a 40 GB FASTQ can be inspected with `head` and filtered with `grep` in constant memory, and why the Unix toolkit remains, fifty years later, the most reliable interface to biological data.

This matters scientifically rather than aesthetically. The reproducibility literature names **compute-environment and process control** as a pillar of reproducible research (Pillar 3 and Pillar 5 in Naylor et al.'s "five pillars", *Briefings in Bioinformatics* 2023, doi:10.1093/bib/bbad375). A result produced by commands typed into a terminal and never recorded is not reproducible — even when the numbers are right. So the goal of this module is not "learn 30 commands". It is: **be able to state, in a file you can re-run, exactly how a number was produced.**

## 2. Learning objectives

By the end of this module you can:

1. Explain the difference between a file, a stream and a pipe, and predict when a command will stream rather than load data into memory.
2. Compose `head`, `wc`, `grep`, `sort`, `uniq`, `cut` and `awk` into a one-line quality check, and say what each component does.
3. **Identify and demonstrate a specific class of counting error** (heuristic line arithmetic vs parsing) and justify which you used.
4. Write a command whose output you can validate against a second, independent implementation.
5. Explain why a pipeline should be a *file describing required outputs* rather than a shell history, and read a `bioflow plan` DAG.

## 3. Required software

```bash
# from the repository root
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
bioflow --version        # expect: bioflow 0.1.0
```

POSIX tools (`head`, `wc`, `grep`, `awk`, `sort`) are present on Linux and macOS. On Windows use WSL2 — not Git Bash, and not "install GNU tools and hope". Module 1 assumes a POSIX shell; pretending otherwise causes exactly the silent failures described in §9.

## 4. Conceptual explanation

### 4.1 Files, streams, pipes

A program started from a shell receives three open channels: **stdin** (fd 0), **stdout** (fd 1), **stderr** (fd 2). A pipe `|` connects one program's stdout to the next program's stdin.

```text
head -400 reads.fastq | wc -l        # 400 lines pass through, nothing is written to disk
```

The scientific consequence is *scale independence of your attention*: you can profile a dataset you cannot fit in RAM, and you can stop a computation early (`head`) without paying for it.

Two operators you must distinguish:

| Operator | Meaning | Failure mode if confused |
|---|---|---|
| `>` | redirect stdout to a file, **truncating** it first | `grep x big.txt > big.txt` destroys `big.txt` before `grep` reads it |
| `>>` | append | repeated runs silently duplicate results |

### 4.2 Why line structure is a contract

FASTQ is exactly four lines per record:

```text
@header            <- '@' + identifier + optional description
SEQUENCE           <- A/C/G/T/N, no spaces
+                  <- separator, optionally repeating the header
QUALITY            <- one ASCII character per base
```

Because it is four lines, `wc -l / 4` gives the record count. Because the quality alphabet (Phred+33, ASCII 33–126) can *contain* `@`, counting lines beginning with `@` **over-counts**. This is not a theoretical worry: in our own 200-read simulated dataset, `grep -c '^@'` returns **204** — four quality lines begin with `@`. The notebook demonstrates it.

The general principle is worth stating explicitly, because it recurs in every module:

> A **heuristic** (line arithmetic, filename conventions, "it usually looks like this") is fast and usually right. A **parser** (a stated grammar, validated case by case) is slower and sometimes right in ways the heuristic is not. Never mix the two without saying which you used.

### 4.3 Composition and quality, defined rather than assumed

- **GC content** here is `(G + C) / (A + T + G + C)`. Ambiguous symbols (`N`, `R`, `Y`, …) are excluded from *both* numerator and denominator. Including them silently deflates GC content in draft assemblies — a classic source of irreproducible QC numbers.
- **Phred score** `Q` maps to per-base error probability `P = 10^(−Q/10)`: Q20 = 1%, Q30 = 0.1%. A "Q30 filter" is therefore a statement about *expected errors*, not a magic number.

### 4.4 From commands to a pipeline

A shell history answers "what did I type?". A pipeline answers "what must exist, and what produces it?". `bioflow` reads YAML where each step declares `inputs` and `outputs`; the execution order is *derived* from those paths, and up-to-date steps are skipped using SHA-256 of inputs plus the command string.

```yaml
steps:
  - name: qc_reads
    command: bioflow stats {inputs} --json > {outputs}
    inputs: [datasets/sample/reads.fastq]
    outputs: [results/qc/reads.json]
```

## 5. Mathematical and computational foundations

Record count from line count, for a well-formed single-line FASTQ:

$$
n_\text{records} = \frac{L}{4}, \qquad L = \text{number of newline-terminated lines}
$$

Mean per-position quality over `n` reads at position `i`:

$$
\bar{Q}_i = \frac{1}{n_i}\sum_{k=1}^{n_i} Q_{k,i}, \qquad n_i = \#\{\text{reads with length} > i\}
$$

Expected number of erroneous bases in a read of length `m`:

$$
E[\text{errors}] = \sum_{j=1}^{m} 10^{-Q_j/10}
$$

That last formula is why two reads with the same *mean* Q can have different error counts — mean quality is not a sufficient statistic. We return to this in Module 7 and in the capstone.

**Cost model of a pipe:** each stage adds one process and one copy through a 64 KiB kernel buffer. `xargs -P` or a workflow manager buys parallelism; a longer pipe does not.

## 6. Practical demonstration

```bash
cd /path/to/linux-git-for-bioinformatics

# 1. What is in the file?
head -4 datasets/sample/reads.fastq

# 2. How many records? (two ways — they will disagree, deliberately)
wc -l < datasets/sample/reads.fastq        # 800 -> 200 records
grep -c '^@' datasets/sample/reads.fastq   # 204  <- over-counts: quality lines can start with '@'

# 3. Composition, computed by an independent implementation
awk 'NR%4==2 {n+=length($0); g+=gsub(/[Gg]/,""); c+=gsub(/[Cc]/,"")} END {printf "%.4f\n", (g+c)/n}' \
    datasets/sample/reads.fastq            # 0.6040

# 4. The library, for comparison
bioflow stats datasets/sample/reads.fastq

# 5. A pipeline you can re-run
bioflow plan examples/pipeline.yml
bioflow run  examples/pipeline.yml         # 4 executed
bioflow run  examples/pipeline.yml         # 0 executed, 4 skipped
```

## 7. Expected output

```text
$ bioflow stats datasets/sample/reads.fastq
file            : datasets/sample/reads.fastq
records         : 200
total bases     : 12000
GC              : 60.4%  (ambiguous bases excluded)
length min/mean/max : 60 / 60.0 / 60
N50             : 60
mean Phred      : 30.46
```

```text
$ bioflow run examples/pipeline.yml
run : qc_reads
run : qc_contigs
run : contig_lengths
run : combine
ok: 4 executed, 0 skipped
```

and `results/contig_lengths.txt`:

```text
>contig_1 synthetic=True
47
>contig_2 synthetic=True
56
>contig_3 synthetic=True
120
```

## 8. Interpretation of results

- **GC = 60.4%** matches the simulation parameters (a GC-rich synthetic "genome"), which is the *only* thing it can legitimately be checked against. On real data you would compare against the reference genome's GC and against a negative control — a 60% GC in a species whose genome is 41% GC is a contamination signal, not a curiosity.
- **Mean Phred 30.46** means roughly three expected errors per 60 bp read by `E[errors] = Σ 10^(−Q/10)` — not "30.46 correct bases per 100".
- **The two record counts differ (200 vs 204)** and *that difference is the lesson*: the heuristic over-counts by exactly the number of quality lines beginning with `@`. If you cannot explain a discrepancy, you have not finished the analysis.
- **`0 executed, 4 skipped` on the second run** is a reproducibility signal: the pipeline knows its outputs are current because it fingerprints its inputs. If it re-ran everything, either an input changed or your tool is not checking the right thing.

## 9. Common errors and troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `grep -c '^@'` ≠ `wc -l / 4` | Quality lines starting with `@` (or wrapped FASTQ) | Use a parser; treat the discrepancy as information |
| GC > 100% | `gsub()` mutates `$0`, so `length($0)` afterwards excludes G/C | Compute lengths *before* substitutions — this exact bug was found while building this lesson |
| `bioflow: command not found` | Package not installed in the active environment | `pip install -e .` inside the venv; check `which python` |
| Pipeline re-runs everything each time | Inputs are regenerated with a new timestamp/hash upstream | Fingerprint content, not mtime; check `.bioflow/stamps/` |
| `bioflow run` fails with "unsatisfiable inputs" | A step names an input nothing produces and which does not exist | Fix the path, or add the producing step; run `bioflow plan` first |
| `awk: syntax error` inside a pipeline | Shell quoting: the command is passed to `sh`, so single-quote the awk program | Use `'{...}'`; see `docs/limitations.md` on brace handling |
| Windows: tools missing | No POSIX shell | Use WSL2 (recommended) or a container |

## 10. Exercises

See [`docs/practicals/practical-01-counting-and-composition.md`](../practicals/practical-01-counting-and-composition.md) and [`practical-02-pipes-and-streams.md`](../practicals/practical-02-pipes-and-streams.md) for the guided versions; independent work is in [`docs/assessments/`](https://github.com/CLS-Open/linux-git-for-bioinformatics/blob/main/docs/assessments/).

Quick self-check (answers in the notebook, not here):
1. Why is `sort | uniq -c` preferred to a Python `Counter` for a 40 GB file?
2. What does `wc -l` count if the last line has no trailing newline?
3. Which of the two record counts would you report to a collaborator, and how would you justify it?

## 11. Further reading and references

- Cock, P.J.A. et al. (2010) "The Sanger FASTQ file format for sequences with quality scores, and the Solexa/Illumina FASTQ variants." *Nucleic Acids Research* 38(6):1767–1771. doi:10.1093/nar/gkp1137 — the normative FASTQ description used above.
- Naylor, B. et al. (2023) "The five pillars of computational reproducibility: bioinformatics and beyond." *Briefings in Bioinformatics* 24(6):bbad375. doi:10.1093/bib/bbad375 — the reproducibility framework this repository enforces.
- GNU Coreutils manual — `head`, `wc`, `sort`, `uniq`, `cut` semantics and edge cases.
- POSIX `awk` specification (The Open Group Base Specifications) — `gsub`, `NR`, field splitting.
- Software Carpentry *The Unix Shell* lesson — an excellent, longer treatment of the same fundamentals; this module assumes its existence and does not duplicate it.
- Waskom, M. (2021) "seaborn: statistical data visualization." *JOSS* 6(60):3021. doi:10.21105/joss.03021 — for Module 3's figures (listed here because the quality plot is your first QC figure).

*All references verified against Crossref on 2026-11-06; see `docs/references.md` for the verification log.*
