# Instructor pack — Linux, Git and Reproducible Workflows for Bioinformatics

This pack exists because the evidence says instructors — not students — are the bottleneck in bioinformatics education: lack of faculty training (24%) and lack of vetted teaching materials were the top two reported barriers in a 1,264-respondent survey (Williams et al., bioRxiv 204420). Everything here is designed so you can teach from it without having written it.

## What you can adopt, and how long it takes

| Format | Content | Contact hours | Prep (first delivery) | Marking load |
|---|---|---|---|---|
| **Workshop (12 h)** | Modules 1–2 + Practicals 1–2 | 12 | 2 h (run the notebook once) | none (formative) |
| **Short course (24 h)** | Modules 1–5 + Practicals 1–2 + Assignment 1 | 24 | 4 h | ~15 min/student |
| **Full course (36 h)** | Modules 1–9 + all assessment + capstone | 36 | 8 h | ~35 min/student |

Module 2–9 lessons are specified but not yet written (see `docs/roadmap.md`); before Module 1 ships in a 24-hour format, allow the dates in the roadmap to be checked.

## Session-by-session plan (12-hour workshop)

| Session | Duration | Content | Instructor activity | Learner activity |
|---|---|---|---|---|
| 1 | 60 min | Why the terminal, files vs streams | Live demo, deliberately break things | Predict-then-run worksheet |
| 2 | 60 min | Counting and composition | Walk through the 200 vs 204 discrepancy | Practical 01 (guided) |
| 3 | 90 min | Pipes, memory, `awk` | Demonstrate `/usr/bin/time -v` | Practical 02 |
| 4 | 60 min | Phred, QC decisions | Whiteboard error-probability table | Interpret a quality profile |
| 5 | 90 min | Pipelines as files | Build `pipeline.yml` live | Extend with a 5th step |
| 6 | 90 min | Reproducibility: stamps, hashes | Show a cache invalidation | Prove determinism |
| 7 | 120 min | Assignment 1 kick-off | Circulate, ask "where is your hash file?" | Independent work |
| 8 | 60 min | Debrief and error gallery | Collect anonymous failure stories | Present one finding each |

## Three things learners get wrong, every time

1. **Reporting a count without knowing its method.** They will run `grep -c '^@'` and report 204 confidently. Do not correct it immediately — ask them to reconcile with `wc -l / 4`. The reconciliation *is* the lesson.
2. **Believing that a pipeline that runs is a pipeline that is correct.** Introduce a step whose declared output it never writes; `bioflow` fails loudly (see `test_step_that_forgets_its_outputs_is_a_failure`). Ask why silent success is more dangerous than an error.
3. **Confusing "mean quality" (three different quantities).** Use the `per_position` vs `per_read` vs `overall` distinction in Practical 02. Make them say which one they mean, every time.

## Equipment and access notes

- **Minimum:** any laptop with Linux, macOS or WSL2, Python ≥3.10, no GPU, no admin rights beyond a venv. Everything runs offline after install.
- **Bandwidth:** the whole repository is under 1 MB; installed dependencies are ~50 MB. There is no large download in the graded path.
- **No account required** for any exercise. GitHub is used only in Module 6, where an account is necessary; that module must remain optional for grading.
- **CI alternative:** if local installs are impossible, `notebooks/01_unix_mindset.ipynb` runs in a free Colab instance.

## Assessment design

- Levels 1–2 are formative: quiz + guided practicals, self-marked with the answer key.
- Level 3 (assignment) is the first summative item; rubric in `docs/assessments/assignment-01-shell-audit.md`.
- Level 5 (capstone) requires a public repository; **grading must not require public posting** — accept a private repo export if a learner declines to publish.
- Academic-integrity note: the material is CC BY 4.0, so learners may reuse it. Ask them to cite the release they used; do not require a citation to this project in exchange for marks.

## Adapting the material

- Fork the repository and keep your changes in a branch per cohort; this keeps your teaching version stable.
- Replace the simulated datasets with your own instrument data — the notebooks read paths from `datasets/sample/`, so a new directory plus a `metadata/*.yml` file is enough.
- If your course is in another language, the content licence (CC BY 4.0) permits translation with attribution; please open an issue so we can link your version.

## Feedback to the maintainers

Content errors: use the "Content error" issue template, quoting the file and line. Adoption reports ("I taught this to N students, here is what broke") are the most valuable contribution you can make and are explicitly welcomed in `CONTRIBUTING.md`.
