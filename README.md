# Docking

A Jupyter pipeline for generating curcumin derivatives, profiling molecular properties, selecting a diverse ligand set, checking PubChem, and docking against the TLR-4–MD-2 structure in `3FXI.pdb`.

Docking scores are computational predictions and do not establish biological activity.

## Setup

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), and [AutoDock Vina](https://github.com/ccsb-scripps/AutoDock-Vina/releases). Python dependencies are defined in `pyproject.toml` and pinned in `uv.lock`.

From the repository root:

```sh
uv sync --locked
uv run jupyter lab
```

Select the project's `.venv` interpreter for notebooks. Place the Windows Vina executable at `tools/bin/vina.exe`, or make `vina` available on PATH. The local executable takes precedence. Vina is an external program; `uv sync` does not install it. The development build was Vina 1.2.7 and is excluded from Git.

## Workflow

Run all cells from top to bottom in each notebook, in order:

| Notebook | Task | Main output |
| --- | --- | --- |
| `00_scaffold.ipynb` | Prepare substitution sites | `curcumin_scaffold.smi` |
| `01_generation.ipynb` | Generate curcumin derivatives | `generated_ligands.smi` |
| `02_lipinski.ipynb` | Apply the Rule of Five filter | `lipinski_passed.smi` |
| `03_profiling.ipynb` | Calculate descriptors and PAINS/Brenk alerts | `molecular_profiles.csv`, `profiled_ligands.smi` |
| `04_selection.ipynb` | Select a diverse, stratified sample | `selected_ligands.csv` |
| `05_pubchem.ipynb` | Query PubChem | `pubchem_results.csv`, `pubchem_unmatched_ligands.csv` |
| `06_preparation.ipynb` | Prepare receptor and ligand PDBQT files | `receptor.pdbqt`, `preparation_results.csv`, `ligands/` |
| `07_docking.ipynb` | Run Vina and sort scores | `docking_scores.csv`, `poses/`, `vina_logs/` |

Notebooks support a working directory of the repository root or `notebooks/`. Configure parameters in their settings cells. Stage 05 needs internet access; failed queries are recorded as errors, not as structures absent from PubChem. PubChem results can change over time.

Selection currently requests 100 molecules with seed 42. Docking uses exhaustiveness 16, seed 42, center `(28.249, 0.618, 18.996)`, and box size `(22.904, 17.276, 22.017)` Angstrom. CPU allocation is configured in notebook 07.

## Data, logs, and archives

```text
data/
├── raw/                         # Original inputs tracked in Git
│   ├── curcumin.sdf
│   └── 3FXI.pdb
├── interim/                     # Current stage outputs
│   ├── 00_scaffold/
│   ├── 01_generation/
│   ├── 02_lipinski/
│   ├── 03_profiling/
│   ├── 04_selection/
│   └── 05_pubchem/
├── processed/
│   ├── 06_preparation/
│   └── 07_docking/
├── logs/<stage>/pipeline.log
└── archive/<stage>/<run_id>/
    ├── results/
    └── logs/
```

Each output directory contains `run.json` with the run identifier, parameters, input SHA-256 fingerprints, and status. Before a stage writes new outputs, its previous results and log move to the archive. Original raw inputs are preserved. Subsequent stages reject unfinished or unverified runs and runs whose recorded inputs changed; rerun affected stages in order.

The final CSV is `data/processed/07_docking/docking_scores.csv`. There is no separate `data/results/` directory. `LigandID` links scores and poses to preparation records and original molecular properties. Per-ligand Vina stdout/stderr is stored in `data/processed/07_docking/vina_logs/`.

Generated data, logs, archives, environments, and Vina binaries are ignored by Git. For reproducibility, use the committed raw inputs and lockfile, execute the notebooks sequentially, and retain run manifests and the external Vina version. Reproducing an earlier PubChem lookup requires its saved query results.

## Utilities and known limitations

`utils/` provides paths, run management, Loguru configuration, OpenBabel preparation, molecular drawing, and the synthetic accessibility scorer. `notebooks_old/` preserves historical notebooks and is outside the current workflow.

OpenBabel resource paths are configured by `utils/babel.py`. Isolated magnesium ions retain Mg2+ charges without artificial hydrogens; other atoms receive Gasteiger charges. OpenBabel diagnostics are forwarded to the stage log. The current receptor still produces an aromatic bond perception warning; its bond typing requires inspection before interpreting docking results. Prepared PDBQT files passed a Vina compatibility check, which does not validate chemical typing or the full pipeline scientifically.
