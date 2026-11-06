# Mini-projects

Small, self-contained pieces of work (4–8 hours) that combine this module's skills
with one extra step. Each is specified with outputs, a rubric and an honest
statement of what "done" means.

## Mini-project 1 — Audit a public repository's reproducibility (6 h)

**Task.** Pick any public bioinformatics tutorial repository with ≥20 stars. Clone it.
Score it against the five pillars of computational reproducibility (literate programming,
version control, environment control, persistent data sharing, documentation). Attempt to
run one example end-to-end and record exactly where and why it fails, if it does.

**Deliverable.** `audit.md` (≤800 words) + `evidence/` (pinned commit hash, error logs,
versions file). Include one sentence on what the repository does *well* — an audit that
lists only failures is not credible.

**Rubric (15 points).** Pillar-by-pillar scoring with evidence (5) · attempted reproduction
with logs (5) · fairness and specificity (3) · writing (2).

**Ethics.** Write about the *repository*, not the people. No speculation about authors'
competence. If you open an upstream issue, be constructive and link your audit only if
the maintainers welcome it.

## Mini-project 2 — Your own reproducible analysis skeleton (8 h)

**Task.** Build a template repository from scratch (do not copy this one) that contains:
pinned environment, `pipeline.yml` or `Snakefile`, a data dictionary, a `run.sh` that
fails fast, a test that checks a known value, and CI that runs on push.

**Deliverable.** A public repository under your own account + a 300-word README explaining
each decision. Cite the CLS-Open release you learned from **if you used it** — not otherwise.

**Rubric (20 points).** Reproduces from clean clone (6) · tests something meaningful (5) ·
CI actually runs (4) · documentation explains *why*, not just *what* (5).
