# Tutorial 01 — Your first pipeline (15 minutes)

**Goal:** turn three commands into a pipeline file, then prove it is reproducible.

## Step 1 — Do it by hand

```bash
mkdir -p results
bioflow stats datasets/sample/reads.fastq --json > results/reads.json
bioflow stats datasets/sample/contigs.fasta --json > results/contigs.json
```

Two files exist. Nothing about this is reproducible yet: the commands live in your shell history.

## Step 2 — Write the pipeline

Create `my_first_pipeline.yml`:

```yaml
steps:
  - name: qc_reads
    command: bioflow stats {inputs} --json > {outputs}
    inputs: [datasets/sample/reads.fastq]
    outputs: [results/reads.json]

  - name: qc_contigs
    command: bioflow stats {inputs} --json > {outputs}
    inputs: [datasets/sample/contigs.fasta]
    outputs: [results/contigs.json]
```

## Step 3 — Ask what it will do *before* it does it

```bash
bioflow plan my_first_pipeline.yml
```

Read the output. If the order surprises you, the bug is in your `inputs`/`outputs`, not in the tool.

## Step 4 — Run it, twice

```bash
bioflow run my_first_pipeline.yml
bioflow run my_first_pipeline.yml
```

Second run: `0 executed, 2 skipped`.

## Step 5 — Break it on purpose

Change one byte in `datasets/sample/contigs.fasta` (add a blank line at the end) and run again. Exactly one step should re-run. Now revert the file and run again — **both** steps re-run, because the content changed back and the stamp records the content it saw.

This is the whole idea: the pipeline's memory is a fingerprint of reality, not a timestamp.

## Step 6 — Inspect the provenance

```bash
cat bioflow_run.log
cat .bioflow/stamps/qc_reads.json
```

The stamp contains the command, the completion time, and a SHA-256 of every output. That file is what a reviewer would ask for.

## Next

- Practical 02 asks you to extend this with a dependent step.
- Challenge 01 asks you to make the statistics themselves memory-bounded.
