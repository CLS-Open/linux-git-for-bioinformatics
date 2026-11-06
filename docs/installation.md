# Installation

## Requirements

| Item | Minimum | Why |
|---|---|---|
| Python | 3.10 | dataclasses/slots, `str | None` typing |
| Shell | POSIX (`sh`, `bash`) | The course assumes POSIX tools; Windows users need WSL2 |
| Disk | ~80 MB (mostly numpy/pandas for the figures) | — |
| GPU / cluster | **none** | Everything here runs on a laptop, offline |
| Account anywhere | **none** | No cloud, no login, no licence key |

## Standard install (5 minutes)

```bash
git clone https://github.com/cls-open/linux-git-for-bioinformatics.git
cd linux-git-for-bioinformatics

python -m venv .venv
source .venv/bin/activate          # Windows (WSL2): source .venv/bin/activate

pip install -e ".[dev]"
bioflow --version
python -m pytest -q                # expect: 65 passed
```

## Verify your install (do not skip)

```bash
python scripts/make_sample_data.py   # regenerates the simulated datasets (deterministic)
bioflow stats datasets/sample/reads.fastq
```

Expected:

```text
records         : 200
total bases     : 12000
GC              : 60.4%  (ambiguous bases excluded)
N50             : 60
mean Phred      : 30.46
```

If those five numbers match, your environment is correct. If they do not, stop and fix it — every later lesson depends on them.

## Windows

Use **WSL2** (`wsl --install` then `sudo apt install python3-venv build-essential`). Git Bash is not sufficient: `awk`, `sort` and `grep` behave differently enough to produce confusing results, and `/usr/bin/time` is absent.

## No-install route

- `notebooks/01_unix_mindset.ipynb` runs in a free Colab/JupyterHub instance. Upload the repository (it is <1 MB), then run the notebook from the repository root.
- A container recipe is in `docs/limitations.md` §containers (Docker/Podman) — **not** required for any graded exercise.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `bioflow: command not found` | venv not active, or package not installed | `source .venv/bin/activate && pip install -e .` |
| `ModuleNotFoundError: yaml` | dependency not installed | `pip install PyYAML` or reinstall with `-e .` |
| `pytest` reports failures on parsing | Python <3.10 | Check `python -V` |
| Notebook says "run from repository root" | wrong working directory | `cd` to the repository root; the assert message tells you |
| `make_figures.py` fails on fonts | minimal matplotlib install | `pip install matplotlib>=3.8` |
| Figures look different from the repository | you are on a different matplotlib version | use the pinned verions in `pyproject.toml`; fonts/metrics vary slightly across versions |

## Uninstall

```bash
deactivate && rm -rf .venv
```
