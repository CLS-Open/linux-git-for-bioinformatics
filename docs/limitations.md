# Limitations and known failure cases

This page is a requirement of the repository, not an afterthought. A tool without a limitations statement is a tool you cannot safely use.

## Software (`bioflow` 0.1.0)

| Limitation | Consequence | Workaround |
|---|---|---|
| **Sequential execution only** | `--jobs N` is accepted and ignored (with a warning on stderr) | Use Snakemake/Nextflow for parallelism; Module 7 explains why they exist |
| **`shell=True` execution** | Pipeline YAML is executable code; a malicious pipeline can do anything your user can | Only run pipelines you have read; treat pipeline files like source code |
| **No containers** | No isolation, no reproducible toolchain | Use Docker/Singularity; see Module 4 |
| **No wildcard/pattern rules** | You must enumerate every file | Snakemake's `expand`/`wildcards`; Module 7 |
| **Cache key = command string + input content** | Changing an *environment* (e.g. tool version) does not invalidate the cache | Also hash `versions.txt` as an input, or `rm -rf .bioflow` |
| **`stats` holds all lengths in memory** | N50/histogram memory grows with record count | Challenge 01 asks you to fix this properly |
| **FASTA/FASTQ only** | No GFF/VCF/BAM/SAM | Module 7+; or use `pysam`, `bcftools` |
| **Single-line FASTQ assumed for `NR%4` examples** | Wrapped FASTQ breaks the lesson's one-liners (the parser is fine) | Use `bioflow stats`; treat wrapping as an error |
| **No Windows-native support** | Paths and POSIX tools differ | WSL2 |
| **Phred+64 not auto-detected** | Old Solexa/Illumina data would be mis-scored | Out of scope; detect manually before use |

## Educational limitations

- Modules 2–9 are **specified, not written** (see [roadmap](roadmap.md)). Using this repository as a 24–36 hour course today means supplementing those modules yourself.
- The datasets are **simulated**; learners do not meet adapter contamination, index hopping, or batching.
- No cohort data exists yet: **learning gains are not measured**, and this repository makes no claim that it improves learning outcomes. Any such claim will require ethics approval, consent and pre/post instruments — see the publication strategy in the initiative's initiation report.
- English only (v0.1). Translation is permitted and encouraged under CC BY 4.0.
- Accessibility: colour-blind-safe palettes and alt text are used in figures; screen-reader testing of the docs site has **not** been done. Reports of accessibility problems are treated as high-priority bugs.

## Two bugs found while writing this material (kept as lessons)

1. **`str.format` and shell braces.** Rendering `{inputs}` with Python's `str.format` raised `KeyError` on `awk '{if (n) print n}'`. Fixed by explicit token replacement; regression test `test_awk_braces_survive_rendering`.
2. **`gsub` mutates `$0`.** The "obvious" GC one-liner computed lengths *after* substituting G/C out of the line, producing GC = 152%. Both versions are in the notebook, because the failure is more instructive than the fix.

Both are documented rather than quietly patched because a course that shows only working code teaches learners to distrust their own (correct) suspicion that something is wrong.
