# Prerequisites

## Required

- You can create, move and delete files in a graphical file manager.
- You know what DNA/RNA/protein are, and that DNA is double-stranded.
- You can read a table of numbers and say what a column means.

That is all. There is no programming prerequisite: this repository is the entry point of the CLS-Open pathway.

## Helpful but not required

- Any prior exposure to statistics (mean, median, standard deviation).
- Any prior use of a spreadsheet for scientific data.
- English reading proficiency (the material is English; translations are welcome under CC BY 4.0).

## Self-assessment (10 minutes)

Try these in a terminal. It is completely fine if you cannot do any of them.

```bash
pwd                 # where am I?
ls -la              # what is here, including hidden files?
cd /tmp && cd -     # move and return
echo "hello" > a.txt && cat a.txt
```

If you can do all four, you will finish Module 1 in ~2 hours. If none, budget 4–5 hours and do Practical 01 twice.

## Concepts you will meet that are *not* assumed

| Concept | Where it is introduced |
|---|---|
| Streams, pipes, file descriptors | Module 1 §4.1 |
| FASTQ/FASTA grammar | Module 1 §4.2 |
| Phred quality scores and error probability | Module 1 §4.3, §5 |
| N50 | Module 1 §5 |
| Hash functions and content fingerprints | Module 1 §4.4 (introduced), Module 7 (formalised) |
| Version control | Module 5 |
| Dependency environments | Module 4 |
| Workflow managers | Module 7 |

## What this repository does *not* teach

- Programming in Python (that is #1) or R (#3).
- Statistics choices for biological designs (that is #6).
- Any specific genomics pipeline biology (#11).

Stating this is itself a requirement of the course: knowing what a tool does not do is part of using it correctly.
