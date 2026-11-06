# Level-1 knowledge quiz — Module 1 (with answer key)

Instructor note: this quiz is diagnostic, not gatekeeping. 12 questions, 15 minutes, closed-book. Answer key at the end — remove it before distributing.

1. What are the three standard streams, and which file descriptor numbers are they?
2. Explain the difference between `>` and `>>` in one sentence each.
3. A FASTQ record consists of how many lines, and what is each line?
4. Why can `grep -c '^@'` over-count FASTQ records?
5. Give the Phred score corresponding to a per-base error probability of 1 in 1000.
6. Define N50 in words, then as an algorithm.
7. In `awk 'NR%4==2 {…}'`, what does `NR%4==2` select, and why is this only valid for single-line FASTQ?
8. What does `gsub(/G/,"")` do to `$0`, and what consequence does that have for `length($0)`?
9. Why is a pipe's memory use independent of file size, but a `sort` in the middle of the pipe is not?
10. Name three properties a workflow file should record that a shell history does not.
11. What is the scientific problem with reporting a GC content that includes ambiguous bases in the denominator?
12. Your pipeline reports "0 executed, 4 skipped" on a re-run. Give one benign and one worrying explanation.

## Answer key

1. stdin (0), stdout (1), stderr (2).
2. `>` truncates the destination *before* running the command; `>>` appends.
3. Four: header (`@id description`), sequence, `+` separator, quality string (one ASCII char per base).
4. Because quality characters use Phred+33 over ASCII 33–126, which includes `@` (ASCII 64); a quality line may therefore begin with `@`.
5. Q30 (10^(−30/10) = 10⁻³).
6. In words: the length such that contigs of at least that length cover ≥50% of the assembly. As an algorithm: sort lengths descending; accumulate; the first length at which the cumulative sum reaches ≥ half the total is the N50.
7. Selects lines 2, 6, 10, … — the sequence lines of consecutive 4-line records. Valid only when no record wraps.
8. It deletes all G characters from the current record, so a later `length($0)` measures the line *after* deletion — under-counting the denominator (our buggy GC = 152%).
9. A pipe moves data through a fixed kernel buffer; `sort` must hold (essentially) all input before emitting the first line, so its memory scales with input.
10. Any three of: tool versions; declared inputs and outputs; checksums of inputs; parameters; environment; derived dependency order; provenance log.
11. Including N in the denominator dilutes GC%, so a high-N draft assembly looks AT-rich — biasing exactly the QC decision you are making.
12. Benign: nothing changed since the last run, so caching is correct. Worrying: outputs were deleted or an input path changed silently (e.g. a symlink), so the pipeline believes it is up to date when it is not — verify with `ls`/hashes.

## Marking

1 point each; 10–12 pass, 7–9 needs review of §4 of the module, ≤6 re-read the module before attempting Practical 02.

## Alignment

Each question maps to a learning objective: 1–3, 9 → LO1/L2; 4, 7, 8 → LO3; 5, 6, 11 → LO2/L4; 10, 12 → LO5. Questions 6, 11, 12 are deliberately the ones that separate "remembered commands" from "understands data".
