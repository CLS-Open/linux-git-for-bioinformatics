#!/usr/bin/env python3
"""Regenerate every figure in ``figures/`` from the shipped data.

Rules this script obeys (they are part of the repository's reproducibility
contract, enforced in CI):

* no hard-coded numbers — every plotted value is computed from a file;
* deterministic — no random seeds without an explicit fixed seed;
* colour-blind safe palette (Okabe–Ito);
* every figure states what is plotted, in what units, and for how many records;
* the workflow diagram is generated from the actual pipeline YAML, not drawn by
  hand, so it cannot drift from the pipeline it illustrates.

Usage
-----
    python scripts/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml  # noqa: E402

from bioflow.pipeline import dependencies, load_pipeline, topological_order  # noqa: E402
from bioflow.seqio import read_records  # noqa: E402
from bioflow.stats import summarise  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "datasets" / "sample"

# Okabe-Ito colour-blind-safe palette
BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
GREY = "#666666"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def figure_quality_profile() -> None:
    stats = summarise(read_records(DATA / "reads.fastq"))
    per_pos = stats.per_position_mean_quality
    positions = range(1, len(per_pos) + 1)

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.plot(positions, per_pos, color=BLUE, lw=1.6, label="mean Phred score")
    ax.axhline(30, color=GREEN, ls="--", lw=1.0, label="Q30 (99.9% base-call accuracy)")
    ax.axhline(20, color=ORANGE, ls=":", lw=1.0, label="Q20 (99% base-call accuracy)")
    ax.set_xlabel("position in read (bp, 1-based)")
    ax.set_ylabel("mean Phred quality score (Q)")
    ax.set_title(
        f"Per-position mean quality, n = {stats.n_records} simulated reads "
        f"of {len(per_pos)} bp"
    )
    ax.set_ylim(0, 42)
    ax.legend(frameon=False, fontsize=8)
    ax.text(
        0.99,
        0.03,
        "SIMULATED DATA — synthetic reads, not experimental measurements",
        transform=ax.transAxes,
        ha="right",
        fontsize=6.5,
        color=GREY,
    )
    fig.savefig(FIG / "fig01_quality_profile.png")
    plt.close(fig)


def figure_length_distribution() -> None:
    stats = summarise(read_records(DATA / "proteins.fasta"))
    hist = stats.length_histogram
    lengths = sorted(hist)
    counts = [hist[k] for k in lengths]

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.bar([str(k) for k in lengths], counts, color=GREEN, width=0.7)
    ax.set_xlabel("protein length (amino acids)")
    ax.set_ylabel("number of sequences")
    ax.set_title(
        f"Length distribution of {stats.n_records} simulated proteins "
        f"(N50 not meaningful for proteins; shown: n={stats.n_records})"
    )
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.text(
        0.99,
        0.95,
        "SIMULATED DATA",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.5,
        color=GREY,
    )
    fig.savefig(FIG / "fig02_protein_lengths.png")
    plt.close(fig)


def figure_workflow_dag() -> None:
    """Draw the DAG of examples/pipeline.yml — derived from the YAML, not hand-drawn."""
    steps = load_pipeline(ROOT / "examples" / "pipeline.yml")
    order = topological_order(steps)
    deps = dependencies(steps)
    by_name = {s.name: s for s in steps}

    # Layered layout: layer = longest path length from a root
    layer: dict[str, int] = {}

    def depth(name: str, seen: tuple[str, ...] = ()) -> int:
        if name in layer:
            return layer[name]
        if not deps[name]:
            layer[name] = 0
            return 0
        layer[name] = 1 + max(depth(d, seen + (name,)) for d in deps[name])
        return layer[name]

    for s in steps:
        depth(s.name)

    by_layer: dict[int, list[str]] = {}
    for name, d in layer.items():
        by_layer.setdefault(d, []).append(name)

    positions: dict[str, tuple[float, float]] = {}
    max_layer = max(by_layer)
    for d in sorted(by_layer):
        names = by_layer[d]
        names_sorted = sorted(names)
        for i, name in enumerate(names_sorted):
            x = d * 2.6
            y = (len(names_sorted) - 1) / 2 - i
            positions[name] = (x, y + (max_layer - d) * 0.0)

    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for name, (x, y) in positions.items():
        step = by_name[name]
        label = f"{name}\nin: {len(step.inputs)}  out: {len(step.outputs)}"
        ax.add_patch(
            plt.Rectangle((x - 0.95, y - 0.30), 1.9, 0.60, color=BLUE, alpha=0.12, ec=BLUE, lw=1.0)
        )
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, color="#111111")
    # NOTE: `deps[name]` is a set. Iterating a set of strings gives an order that
    # varies with PYTHONHASHSEED between runs, which made this figure's bytes differ
    # on every run. Sorting makes the figure reproducible (and CI enforces it).
    for name in sorted(deps):
        for d in sorted(deps[name]):
            x0, y0 = positions[d]
            x1, y1 = positions[name]
            ax.annotate(
                "",
                xy=(x1 - 0.95, y1),
                xytext=(x0 + 0.95, y0),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0, shrinkA=0, shrinkB=0),
            )
    ax.set_xlim(-1.6, max(positions.values(), key=lambda p: p[0])[0] + 1.6)
    ax.set_ylim(-1.2, 1.4)
    ax.axis("off")
    ax.set_title(
        f"Dependency graph of examples/pipeline.yml ({len(order)} steps, "
        "layout computed from declared inputs/outputs)"
    )
    fig.savefig(FIG / "fig03_workflow_dag.png")
    plt.close(fig)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    figure_quality_profile()
    figure_length_distribution()
    figure_workflow_dag()
    for f in sorted(FIG.glob("*.png")):
        print(f"wrote {f.relative_to(ROOT)} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
