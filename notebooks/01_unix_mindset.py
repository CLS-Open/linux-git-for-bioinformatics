# %% [markdown]
# # Module 1 — The Unix mindset: files, pipes and biological text
#
# **Repository:** `linux-git-for-bioinformatics` · **Module 1, Lesson 1** · **Level:** beginner
#
# This notebook is the executable companion to `docs/modules/01-unix-mindset.md`.
# Every number printed below is computed from the files in `datasets/sample/`.
#
# > **Data notice.** All sequences in `datasets/sample/` are **simulated** by
# > `scripts/make_sample_data.py` with a fixed seed. They are not experimental
# > measurements. This matters: QC thresholds are usually calibrated against real
# > instruments, and nothing here can tell you how good your sequencer is.
#
# ## Learning objectives
# By the end you should be able to:
# 1. Explain the difference between a *file*, a *stream* and a *pipe*.
# 2. Compose `head`, `grep`, `wc`, `sort` and `awk` into a one-line QC check.
# 3. State why `grep -c '>'` is a **wrong** way to count FASTA records (and what to do instead).
# 4. Reproduce the same result in pure Python and see where each approach is appropriate.

# %%
# Setup: locate the repository root robustly, then work relative to it.
#
# Why not just assert on the current directory? Because Jupyter may launch a kernel
# with cwd = the notebook's own directory (notebooks/), while `jupyter nbconvert`
# launches it elsewhere. A notebook that only works from one directory is a notebook
# that will fail in CI -- and did, until this was fixed.
import os, subprocess, sys, pathlib

ROOT = pathlib.Path.cwd()
while not (ROOT / "pyproject.toml").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
assert (ROOT / "datasets" / "sample" / "reads.fastq").exists(), (
    "Could not locate the repository root (no pyproject.toml above this directory). "
    "See docs/installation.md."
)
os.chdir(ROOT)  # all relative paths below are relative to the repository root
print("python:", sys.version.split()[0])
print("files:", sorted(p.name for p in (ROOT / "datasets" / "sample").iterdir()))

# %% [markdown]
# ## 1. A file is just bytes; a stream is a moving view of them
#
# The shell gives you three standard streams: **stdin (0)**, **stdout (1)**,
# **stderr (2)**. A pipe (`|`) connects one program's stdout to the next
# program's stdin *without* writing an intermediate file.
#
# The practical consequence: you can inspect a 40 GB FASTQ without ever loading
# it into memory. That is not a trick — it is the reason bioinformatics is done
# on the command line.

# %%
def sh(cmd: str) -> str:
    """Run a shell command and return stdout (raises on failure)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {cmd}\n{result.stderr}")
    return result.stdout

print("--- first 8 lines of the FASTQ (1 record = 4 lines) ---")
print(sh("head -8 datasets/sample/reads.fastq"))

# %% [markdown]
# ## 2. Counting: the first thing you will ever need to do
#
# A FASTQ record is **four lines**: header, sequence, `+`, quality. So the
# number of records is `total_lines / 4`. Both of these are correct:

# %%
lines = int(sh("wc -l < datasets/sample/reads.fastq").strip())
print("lines:", lines, "-> records:", lines // 4)
print("headers:", sh("grep -c '^@' datasets/sample/reads.fastq").strip())

# %% [markdown]
# ### A trap worth learning now
#
# Quality strings can also start with `@` (Phred+33 code 31 is `?`, but 64 is `@`).
# So `grep -c '^@'` over-counts on real data, while `wc -l / 4` stays correct as long
# as the file is well formed. Under-counting is also possible if a FASTQ has
# wrapped lines (rare, but legal in some pipelines).
#
# **Lesson:** line-count arithmetic is a heuristic; parsing is a guarantee. Use the
# heuristic for speed, the parser for truth — and be able to say which you did.

# %%
from bioflow.seqio import read_records
from bioflow.stats import summarise

stats = summarise(read_records("datasets/sample/reads.fastq"))
print("parsed records:", stats.n_records)
print("parsed bases  :", stats.total_bases)
assert stats.n_records == lines // 4, "heuristic and parser disagree — investigate before trusting either"

# %% [markdown]
# ## 3. Composition and quality, computed two ways
#
# We compute GC content with a one-liner, then with the library, and require
# agreement. Agreement between two independent implementations is the cheapest
# form of validation available to you — it catches typos, not systematic
# conceptual errors, so you still need the definitions to be right.

# %%
# One-liner: count G and C, divide by the number of unambiguous bases (A,C,G,T).
#
# ORDER MATTERS. `gsub()` *mutates* $0, so `length($0)` must be taken BEFORE the
# substitutions. Getting this wrong produced GC = 1.53 (152%) the first time this
# notebook was executed — a number above 100% is impossible, which is exactly why
# we assert against an independent implementation instead of eyeballing output.
BAD_AWK = (
    r"""awk 'NR%4==2 {g+=gsub(/[Gg]/,""); c+=gsub(/[Cc]/,""); n+=length($0)} """
    r"""END {printf "%.4f\n", (g+c)/n}' datasets/sample/reads.fastq"""
)
GOOD_AWK = (
    r"""awk 'NR%4==2 {n+=length($0); g+=gsub(/[Gg]/,""); c+=gsub(/[Cc]/,"")} """
    r"""END {printf "%.4f\n", (g+c)/n}' datasets/sample/reads.fastq"""
)
print("buggy one-liner ->", sh(BAD_AWK).strip(), "(impossible: GC > 100%)")
awk_gc = sh(GOOD_AWK).strip()
print("fixed one-liner ->", awk_gc)
print("bioflow          ->", round(stats.gc_fraction, 4))
assert abs(float(awk_gc) - stats.gc_fraction) < 1e-4

# %% [markdown]
# ## 4. Quality control is a *decision*, not a number
#
# Phred score `Q` maps to per-base error probability `P = 10^(-Q/10)`.
# Q20 = 1 in 100, Q30 = 1 in 1000. The table below is computed, not asserted:

# %%
for q in (10, 20, 30, 40):
    print(f"Q{q:>2} -> error probability {10 ** (-q / 10):.5f}  ({10 ** (-q / 10) * 100:.3f}%)")

per_pos = stats.per_position_mean_quality
print("\nfirst 5 positions:", [round(q, 2) for q in per_pos[:5]])
print("last  5 positions:", [round(q, 2) for q in per_pos[-5:]])
print("positions below Q30:", sum(1 for q in per_pos if q < 30), "of", len(per_pos))

# %% [markdown]
# In the simulated data quality declines along the read — as it does on real
# Illumina instruments. A trimming decision (where to cut) should follow from
# *your* quality profile and *your* downstream analysis, not from a default
# someone copied from a tutorial. We revisit this in Module 7.

# %% [markdown]
# ## 5. From one-liners to a pipeline you can re-run
#
# A pipeline is a file describing **what** must exist, not a shell history of
# **what you typed**. `examples/pipeline.yml` declares four steps with explicit
# inputs and outputs; `bioflow` derives the order from those paths.

# %%
print(sh("bioflow plan examples/pipeline.yml"))

# %%
# Start from a clean slate so the demonstration is deterministic for everyone.
sh("rm -rf results .bioflow bioflow_run.log")
print(sh("bioflow run examples/pipeline.yml"))
print(sh("cat results/contig_lengths.txt"))

# %% [markdown]
# Run it a second time. Nothing is recomputed, because the inputs have not
# changed (SHA-256 of every input plus the command string is recorded in
# `.bioflow/stamps/`). This is what "reproducible" looks like in practice.

# %%
print(sh("bioflow run examples/pipeline.yml"))

# %% [markdown]
# ## Exercises
#
# 1. **Warm-up.** Write a one-liner that prints the number of sequences in
#    `datasets/sample/proteins.fasta` *and* their mean length. Verify with
#    `bioflow stats --json`.
# 2. **Trap.** Construct a 1-record FASTQ whose quality string contains `@`, then
#    show that `grep -c '^@'` over-counts while `wc -l / 4` does not.
# 3. **Judgement.** At which position does the simulated read quality cross Q30?
#    Give the number and the command that produced it.
# 4. **Extension.** Add a fifth step to `examples/pipeline.yml` that writes the
#    mean length of the contigs to `results/mean_length.txt`, then prove that only
#    the new step runs when you re-run the pipeline.
#
# ## References
# - FASTQ format specification (Cock et al., 2010, *Nucleic Acids Research*, doi:10.1093/nar/gkp1137)
# - Illumina quality-score encoding (Phred+33), Illumina technical note
# - GNU Coreutils manual: `head`, `wc`, `sort`, `grep`
# - `awk` POSIX specification; see `docs/references.md` for verification status
