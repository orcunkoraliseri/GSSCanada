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

# --- STEP 1: CVAE Model Pipeline ---
# Prerequisites: cen06_filtered2.csv … cen21_filtered2.csv in OUTPUT_DIR
RUN_TRAINING: bool = False  # 1a — trains CVAE, saves encoder + decoder
RUN_TESTING: bool = False  # 1b — validates reconstruction quality
RUN_FORECASTING: bool = False  # 1c — generates forecasted_population_YYYY.csv
RUN_VISUAL_VALIDATION: bool = False  # 1d — plots latent-space validation figures

# --- STEP 2: Schedule Assignment ---
# Prerequisites: outputs from Step 1 + Aligned_Census_2025.csv + Aligned_GSS_2022.csv
RUN_ASSEMBLE_HH: bool = False  # 2a — links agents into households
RUN_PROFILE_MATCHER: bool = False  # 2b — matches census agents to GSS schedules
RUN_VALIDATE_PM: bool = False  # 2c — validates matching quality
RUN_POSTPROCESSING: bool = False  # 2d — refines DTYPE labels (1-3 → 1-8)
RUN_HH_AGGREGATION: bool = False  # 2e — aggregates to 5-min time-grid
RUN_VALIDATE_HH_AGG: bool = False  # 2f — validates household aggregation

# --- STEP 3: BEM Output ---
# Prerequisites: Full_data.csv from Step 2e
RUN_BEM_CONVERSION: bool = True  # 3a — converts to hourly BEM schedules

# =============================================================================
# EXECUTION — do not edit below this line
# =============================================================================
if __name__ == "__main__":
    if RUN_TRAINING:
        run_training()
    if RUN_TESTING:
        run_testing()
    if RUN_FORECASTING:
        run_forecasting()
    if RUN_VISUAL_VALIDATION:
        run_visual_validation()

    if RUN_ASSEMBLE_HH:
        run_assemble_household()
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
