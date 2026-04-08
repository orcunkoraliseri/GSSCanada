# =============================================================================
# main_classification.py
# Master Control Panel — Occupancy Classification Pipeline
#
# This is the single entry point for running the full pipeline or any
# individual sub-step. Edit the True/False flags below, then run:
#
#   python main_classification.py
#
# All flags default to False — the file is safe to run without changes.
# No existing source file is modified by this file.
# =============================================================================

import pathlib, sys as _sys

# Ensure the project root (GSSCanada-main) is on the path so that
# `eSim_occ_utils` is importable as a package.
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_PROJECT_ROOT))

# Also ensure this script's own directory is on the path so that the
# sibling modules run_step1, run_step2, run_step3 can be imported.
_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in _sys.path:
    _sys.path.insert(0, str(_SCRIPT_DIR))

from eSim_dynamicML_mHead_alignment import data_alignment
from eSim_occ_utils.occ_config import OUTPUT_DIR, OUTPUT_DIR_ALIGNED, OUTPUT_DIR_GSS

from run_step1 import (
    run_forecasting,
    run_testing,
    run_training,
    run_visual_validation,
)
from run_step2 import (
    run_assemble_household,
    run_household_aggregation,
    run_postprocessing,
    run_profile_matcher,
    run_validate_household_aggregation,
    run_validate_profile_matcher,
)
from run_step3 import run_bem_conversion

# =============================================================================
# GLOBAL CONTROL PANEL
# Set a flag to True to run that sub-step. Set it to False to skip.
# Sub-steps within each stage must be run in order (top to bottom).
# =============================================================================

# --- SAMPLING CONFIGURATION ---
SAMPLE_PCT: int = 100    # 1 to 100 — % of census data to use for modeling
SAMPLE_SIZE: int = 250_000  # Total individuals to generate in forecasting

# --- STEP 1: CVAE Model Pipeline ---
# Prerequisites: cen06_filtered2.csv … cen21_filtered2.csv in OUTPUT_DIR
RUN_TRAINING: bool = False  # 1a — trains CVAE, saves encoder + decoder  [skip: model already trained]
RUN_TESTING: bool = False  # 1b — validates reconstruction quality          [skip: no retraining done]
RUN_FORECASTING: bool = True  # 1c — generates forecasted_population_YYYY.csv
RUN_VISUAL_VALIDATION: bool = True  # 1d — plots latent-space validation figures

# --- STEP 2: Schedule Assignment ---
# Prerequisites: outputs from Step 1 + Aligned_Census_2025.csv + Aligned_GSS_2022.csv
RUN_ASSEMBLE_HH: bool = True      # 2a — links agents into households
RUN_ALIGNMENT: bool = True        # 2a.5 — re-aligns LINKED census to GSS after assemble
RUN_PROFILE_MATCHER: bool = True  # 2b — matches census agents to GSS schedules
RUN_VALIDATE_PM: bool = True  # 2c — validates matching quality
RUN_POSTPROCESSING: bool = True  # 2d — refines DTYPE labels (1-3 → 1-8)
RUN_HH_AGGREGATION: bool = True  # 2e — aggregates to 5-min time-grid
RUN_VALIDATE_HH_AGG: bool = True  # 2f — validates household aggregation

# --- STEP 3: BEM Output ---
# Prerequisites: Full_data.csv from Step 2e
RUN_BEM_CONVERSION: bool = True  # 3a — converts to hourly BEM schedules

# =============================================================================
# EXECUTION — do not edit below this line
# =============================================================================
if __name__ == "__main__":
    _FRAC = SAMPLE_PCT / 100.0

    if RUN_TRAINING:
        run_training(sample_frac=_FRAC)
    if RUN_TESTING:
        run_testing(sample_frac=_FRAC)
    if RUN_FORECASTING:
        run_forecasting(n_samples=SAMPLE_SIZE)
    if RUN_VISUAL_VALIDATION:
        run_visual_validation(sample_frac=_FRAC)

    if RUN_ASSEMBLE_HH:
        run_assemble_household()
    if RUN_ALIGNMENT:
        from pathlib import Path
        _linked = Path(OUTPUT_DIR) / "forecasted_population_2025_LINKED.csv"
        _gss    = Path(OUTPUT_DIR_GSS) / "GSS_2022_Merged_Episodes.csv"
        _out    = Path(OUTPUT_DIR_ALIGNED)
        data_alignment(_linked, _gss, output_dir=_out)
    if RUN_PROFILE_MATCHER:
        run_profile_matcher()
    if RUN_VALIDATE_PM:
        run_validate_profile_matcher()
    if RUN_POSTPROCESSING:
        run_postprocessing()
    if RUN_HH_AGGREGATION:
        run_household_aggregation()
    if RUN_VALIDATE_HH_AGG:
        run_validate_household_aggregation()

    if RUN_BEM_CONVERSION:
        run_bem_conversion()
