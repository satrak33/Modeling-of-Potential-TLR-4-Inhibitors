from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
STAGES = (
    "00_scaffold", "01_generation", "02_lipinski", "03_profiling",
    "04_selection", "05_pubchem", "06_preparation", "07_docking",
)


def stage_path(stage):
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    return DATA / ("processed" if stage in STAGES[6:] else "interim") / stage
