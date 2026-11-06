"""bioflow — a small, auditable pipeline runner and sequence-QC toolkit.

The point of this package is not to replace Snakemake, Nextflow or nf-core.
It exists so that a learner can *read the entire implementation*, understand
how a workflow manager decides what to run and in which order, and then use a
real workflow manager with informed expectations.

Public API
----------
``bioflow.seqio``    sequence record parsing (FASTA / FASTQ / gzip)
``bioflow.stats``    sequence statistics (GC%, N50, length distribution, Phred)
``bioflow.pipeline`` declarative YAML pipelines: validation, DAG, execution
``bioflow.cli``      command-line entry point (``bioflow``)
"""

__version__ = "0.1.0"
__all__ = ["seqio", "stats", "pipeline", "cli"]
