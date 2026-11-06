# Challenge 01 — A streaming QC tool that survives real files

**Level:** L4 (challenge) · **Time:** 6–8 hours · **Prerequisites:** Modules 1–2, practicals 01–02

## Problem statement

`bioflow stats` currently loads one record at a time (good) but stores *all* lengths in a list to compute N50 and the length histogram (fine for teaching, wrong for 10⁹ reads). Your task: extend the tool so that it computes correct statistics on inputs it cannot hold in memory, **and prove it**.

## Requirements

1. **Streaming N50 without storing all lengths.** Implement an exact algorithm using a bounded-memory structure (e.g. a fixed-width histogram over log-spaced length bins *plus* an exact correction, or an external merge sort). State the memory bound as a function of bin count.
2. **Truth test.** Write a property-based or randomised test comparing your streaming N50 against the exact in-memory implementation on ≥1000 random length distributions, including heavy-tailed ones. Report the maximum absolute error (must be 0 for an exact algorithm).
3. **Robustness.** Handle correctly:
   - a file with no trailing newline;
   - a truncated final FASTQ record (must raise a clear error naming the record index);
   - a gzip file whose stream is truncated mid-record;
   - a file containing CRLF line endings.
4. **Performance evidence.** Generate a 500 MB synthetic FASTQ (`scripts/` may be extended) and report wall time and peak RSS for your implementation versus the current one. Peak RSS must not grow with input size — show the numbers.
5. **Integration.** Add `bioflow stats --streaming` (or a new subcommand) with the same JSON schema, and update `docs/modules/01-unix-mindset.md` §6 to mention it honestly.

## Deliverables

- `src/bioflow/<yourmodule>.py` with docstrings stating complexity and memory bounds.
- `tests/test_<yourmodule>.py` — must run in CI in <120 s.
- `CHALLENGE_01_REPORT.md`: design, memory bound derivation, error measurements, performance table, and a "what I would do differently at 10¹¹ reads" paragraph.
- A pull-request-style diff summary.

## Rubric (30 points)

| Criterion | Points |
|---|---|
| Algorithm correct and exact (verified by the 1000-case test) | 8 |
| Memory bound derived, not asserted | 5 |
| Robustness cases all handled with clear errors | 6 |
| Performance evidence measured (not estimated) | 5 |
| Integration quality: schema compatible, docs updated | 3 |
| Report honesty (limitations stated) | 3 |

## Hard constraints

- No new runtime dependency for the core algorithm (standard library only).
- No silent fallbacks: if the streaming path cannot be exact, it must say so and use the exact path.
- Any approximation must be labelled in the JSON output (e.g. `"n50_method": "exact" | "approximate"`).

## Why this is hard

The temptation is to check the length histogram rather than the cumulative distribution, which gives a subtly wrong N50 for heavy-tailed assemblies — exactly the case where N50 is used as a headline statistic. A wrong N50 is worse than an absent one, because it gets quoted in papers.
