<p align="center" id="chem">
    <img style="width: 300px; height: auto;" src="https://github.com/user-attachments/assets/ef8d1641-9a50-4272-b9ad-aa8d68058855">
</p>
<h3 align="center">
    Chem
</h3>
<p align="center">
    Chemical data analysis and molecular modeling pipeline
</p>

## `🔱` Table of Contents

- [🔬┃Project](#-project-)
- [🥽┃Requirements](#-requirements-)
- [🔮┃Installation](#-installation-)
- [🎮┃Usage](#-usage-)
- [💽┃Structure](#-structure-)

## `🔬` Project [🔼](#chem)

### Modeling of Potential TLR-4 Inhibitors

**Goal**: Computer modeling of the interaction between curcumin derivatives and the **TLR-4–MD-2 complex** to evaluate their potential as inhibitors.

**Context**:
TLR-4 plays a key role in immune response; its overactivation is linked to sepsis and autoimmune diseases. Curcumin is a natural inhibitor but has limited bioavailability. This project explores chemical modifications to improve its efficacy.

**Key Findings**:
- **Binding**: All derivatives localize in the active center of MD-2.
- **Affinity**: Binding energies range from **–7.5 to –8.9 kcal/mol**.
- **Top Candidates**: Derivatives containing **sulfo-groups** showed the highest predicted affinity.
- **Mechanism**: Stabilization occurs via hydrophobic, π–π, and hydrogen interactions.

## `🥽` Requirements [🔼](#chem)

- [Python 3.11+](https://www.python.org/)
- [RDKit](https://www.rdkit.org/)
- [ADMET-AI](https://github.com/swansonk14/admet_ai)
- [OpenBabel](http://openbabel.org/)
- [Polars](https://pola.rs/)

## `🔮` Installation [🔼](#chem)

### `📦┃Project Setup`
This project relies on `uv` for modern dependency management.

```bash
# Clone the repository
git clone <repository_url>
cd chem

# Install dependencies using uv
uv sync
```

## `🎮` Usage [🔼](#chem)

The analysis pipeline is structured as a series of Jupyter notebooks.

### `📦┃Workflow`
Navigate to the `notebooks/` directory and run the notebooks in order:

1. `00_test.ipynb` - Environment test.
2. `01_generator.ipynb` - Data generation/loading.
3. `02_pre_admet.ipynb` - Pre-processing.
4. `03_admet.ipynb` - ADMET prediction.
5. ...and so on through the pipeline.

## `💽` Structure [🔼](#chem)

- `notebooks/` - Core analysis and modeling notebooks.
- `utils/` - Helper scripts and shared functions.
- `data/` - Dataset storage (ignored by git).

