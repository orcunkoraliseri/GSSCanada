# =============================================================================
# run_step2.py
# Step 2 Runner: Household Assembly, Schedule Matching & Aggregation
#
# This file wraps the six Step 2 blocks from eSim_dynamicML_mHead.py into
# callable functions. No existing file is modified.
# =============================================================================

from __future__ import annotations

import pathlib
import sys
from pathlib import Path

import pandas as pd

# --- Import everything needed from the existing source file ---
from previous.eSim_dynamicML_mHead import (
    DTypeRefiner,
    HouseholdAggregator,
    MatchProfiler,
    ScheduleExpander,
    assemble_households,
    generate_full_expansion,
    merge_keys_into_forecast,
    validate_household_aggregation,
    validate_matching_quality,
    validate_refinement_model,
    verify_sample,
    visualize_multiple_households,
)

# --- Path Configuration ---
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from eSim_occ_utils.occ_config import (
    BASE_DIR,
    DATA_DIR,
    MODEL_DIR,
    OUTPUT_DIR,
    OUTPUT_DIR_ALIGNED,
)

# --- Shared path variables (mirrors the DIRECTORIES block in eSim_dynamicML_mHead.py) ---
cen06_filtered: Path = OUTPUT_DIR / "cen06_filtered.csv"
cen11_filtered: Path = OUTPUT_DIR / "cen11_filtered.csv"
cen25: Path = OUTPUT_DIR / "Generated/forecasted_population_2025.csv"
aligned_CENSUS: Path = OUTPUT_DIR_ALIGNED / "Aligned_Census_2025.csv"
aligned_GSS: Path = OUTPUT_DIR_ALIGNED / "Aligned_GSS_2022.csv"
VALIDATION_PR_MATCH_DIR: Path = OUTPUT_DIR / "Validation_ProfileMatcher"
VALIDATION_HH_AGG_DIR: Path = OUTPUT_DIR / "Validation_HHaggregation"


# =============================================================================
# SUB-STEP 2a: ASSEMBLE HOUSEHOLD
# =============================================================================
def run_assemble_household(target_year: int = 2025) -> None:
    """
    Groups individual agents from forecasted population CSV into households.

    Uses the existing assemble_households function.

    Parameters:
        target_year: The year to assemble households for. Defaults to 2025.

    Inputs:
        OUTPUT_DIR/Generated/forecasted_population_2025.csv

    Outputs:
        OUTPUT_DIR/forecasted_population_2025_LINKED.csv

    Returns:
        None
    """
    assemble_households(cen25, target_year=target_year, output_dir=OUTPUT_DIR)
    print(f"✅ Household assembly complete for {target_year}.")


# =============================================================================
# SUB-STEP 2b: PROFILE MATCHER
# =============================================================================
def run_profile_matcher() -> None:
    """
    Matches each Census agent to a GSS time-use schedule.

    Uses demographic alignment keys and expands matched keys into full schedules.

    Inputs:
        OUTPUT_DIR_ALIGNED/Aligned_Census_2025.csv
        OUTPUT_DIR_ALIGNED/Aligned_GSS_2022.csv

    Outputs:
        OUTPUT_DIR_ALIGNED/Matched_Population_Keys.csv
        OUTPUT_DIR/Full_Expanded_Schedules.csv

    Returns:
        None
    """
    io_dir: Path = Path(OUTPUT_DIR)
    print("1. Loading Data...")
    df_census: pd.DataFrame = pd.read_csv(aligned_CENSUS)
    df_gss: pd.DataFrame = pd.read_csv(aligned_GSS, low_memory=False)

    # Run Matching
    matcher: MatchProfiler = MatchProfiler(
        df_census, df_gss, dday_col="DDAY", id_col="occID"
    )
    df_matched: pd.DataFrame = matcher.run_matching()

    # Save Matched Keys (Lightweight)
    df_matched.to_csv(OUTPUT_DIR_ALIGNED / "Matched_Population_Keys.csv", index=False)
    print("   Saved Keys: Matched_Population_Keys.csv")

    # Expand & Save Full Schedules (Heavyweight)
    expander: ScheduleExpander = ScheduleExpander(df_gss, id_col="occID")
    verify_sample(df_matched, expander)
    expanded_path: Path = io_dir / "Full_Expanded_Schedules.csv"
    generate_full_expansion(df_matched, expander, expanded_path)

    print("\n✅ Profile Matcher Workflow Complete.")


# =============================================================================
# SUB-STEP 2c: VALIDATION — PROFILE MATCHER
# =============================================================================
def run_validate_profile_matcher() -> None:
    """
    Validates quality of profile matching.

    Compares matched schedule distributions against expected values.

    Inputs:
        OUTPUT_DIR_ALIGNED/Matched_Population_Keys.csv
        OUTPUT_DIR_ALIGNED/Aligned_GSS_2022.csv

    Outputs:
        OUTPUT_DIR/Validation_ProfileMatcher/Validation_ProfileMatcher_2025.txt

    Returns:
        None
    """
    VALIDATION_PR_MATCH_DIR.mkdir(parents=True, exist_ok=True)
    io_dir_aligned: Path = Path(OUTPUT_DIR_ALIGNED)
    io_dir_valid: Path = Path(VALIDATION_PR_MATCH_DIR)

    df_matched: pd.DataFrame = pd.read_csv(io_dir_aligned / "Matched_Population_Keys.csv")
    df_gss: pd.DataFrame = pd.read_csv(
        io_dir_aligned / "Aligned_GSS_2022.csv", low_memory=False
    )

    expander: ScheduleExpander = ScheduleExpander(df_gss, id_col="occID")
    validate_matching_quality(
        df_matched,
        expander,
        save_path=(io_dir_valid / "Validation_ProfileMatcher_2025.txt"),
    )
    print("✅ Profile Matcher Validation Complete.")


# =============================================================================
# SUB-STEP 2d: POST-PROCESSING & VALIDATION OF POST-PROCESSING
# =============================================================================
def run_postprocessing() -> None:
    """
    Refines coarse dwelling-type (DTYPE 1-3) labels to detailed DTYPE (1-8).

    Uses a Random Forest trained on historic census data (2006 and 2011).

    Inputs:
        OUTPUT_DIR/Full_Expanded_Schedules.csv
        OUTPUT_DIR_ALIGNED/Matched_Population_Keys.csv
        OUTPUT_DIR/cen06_filtered.csv
        OUTPUT_DIR/cen11_filtered.csv

    Outputs:
        OUTPUT_DIR/Full_Expanded_Schedules_Refined.csv
        OUTPUT_DIR/Validation_ProfileMatcher_PostProcessing/Validation_Report_DTYPE.txt

    Returns:
        None
    """
    io_dir: Path = Path(OUTPUT_DIR)
    io_dir_aligned: Path = Path(OUTPUT_DIR_ALIGNED)

    historic_data_paths: list[Path] = [cen06_filtered, cen11_filtered]
    input_forecast_path: Path = io_dir / "Full_Expanded_Schedules.csv"
    input_keys_path: Path = io_dir_aligned / "Matched_Population_Keys.csv"
    output_refined_path: Path = io_dir / "Full_Expanded_Schedules_Refined.csv"
    validation_dir: Path = io_dir / "Validation_ProfileMatcher_PostProcessing"

    print("\n🚀 Starting Step 2d: DTYPE Refinement (Merged Strategy)...")

    if not input_forecast_path.exists():
        print(f"❌ Error: Forecast file not found at {input_forecast_path}")
        return
    df_forecast: pd.DataFrame = pd.read_csv(input_forecast_path, low_memory=False)

    # Merge Keys
    if Path(input_keys_path).exists():
        df_keys: pd.DataFrame = pd.read_csv(input_keys_path, low_memory=False)
        df_forecast = merge_keys_into_forecast(df_forecast, df_keys)
    else:
        print("⚠️ Keys file not found. Falling back to deriving CFSIZE/TOTINC.")

    # Load Historic Data for RF training
    print("Loading Historic Data...")
    historic_dfs: list[pd.DataFrame] = []
    for path in historic_data_paths:
        if path.exists():
            historic_dfs.append(pd.read_csv(path, low_memory=False))

    if historic_dfs:
        df_hist: pd.DataFrame = pd.concat(historic_dfs, ignore_index=True)

        refiner: DTypeRefiner = DTypeRefiner(io_dir)
        refiner.train_models(df_hist)

        df_refined: pd.DataFrame = refiner.apply_refinement(df_forecast)
        df_refined.to_csv(output_refined_path, index=False)
        print(f"✅ Saved Refined Data to: {output_refined_path}")

        validate_refinement_model(
            historic_data_paths, output_refined_path, validation_dir
        )
    else:
        print("❌ No historic data found for RF training.")


# =============================================================================
# SUB-STEP 2e: HOUSEHOLD AGGREGATION
# =============================================================================
def run_household_aggregation() -> None:
    """
    Aggregates individual episode-level schedules into a 5-minute time-grid.

    Produces the master time-series dataset.

    Inputs:
        OUTPUT_DIR/Full_Expanded_Schedules_Refined.csv

    Outputs:
        OUTPUT_DIR/Full_data.csv

    Returns:
        None
    """
    io_dir: Path = Path(OUTPUT_DIR)
    expanded_file: Path = io_dir / "Full_Expanded_Schedules_Refined.csv"
    output_full: Path = io_dir / "Full_data.csv"

    print("1. Loading Expanded Schedules...")
    if not expanded_file.exists():
        print(f"❌ Error: {expanded_file} not found. Run run_postprocessing() first.")
        return

    df_expanded: pd.DataFrame = pd.read_csv(expanded_file, low_memory=False)

    aggregator: HouseholdAggregator = HouseholdAggregator(resolution_min=5)

    print("2. Starting Process (Padding + Aggregation)...")
    df_final: pd.DataFrame = aggregator.process_all(df_expanded)

    print(f"3. Saving Full Integrated Data to: {output_full.name}...")
    df_final.to_csv(output_full, index=False)

    print("\n--- Verification: Columns in Output ---")
    print(f"Total Columns: {len(df_final.columns)}")
    print(
        f"Sample Columns: {list(df_final.columns[:10])} ... "
        f"{list(df_final.columns[-3:])}"
    )

    print("\n✅ Household Aggregation Complete.")


# =============================================================================
# SUB-STEP 2f: VALIDATION — HOUSEHOLD AGGREGATION
# =============================================================================
def run_validate_household_aggregation() -> None:
    """
    Validates the household aggregation output.

    Checks completeness, presence/density logic, and activity string correctness.

    Inputs:
        OUTPUT_DIR/Full_data.csv

    Outputs:
        OUTPUT_DIR/Validation_HHaggregation/Validation_Report_HH.txt
        OUTPUT_DIR/Validation_HHaggregation/Validation_Plot_Batch.png

    Returns:
        None
    """
    VALIDATION_HH_AGG_DIR.mkdir(parents=True, exist_ok=True)

    io_dir: Path = Path(OUTPUT_DIR)
    io_valid_hh_agg_dir: Path = Path(VALIDATION_HH_AGG_DIR)
    full_data_path: Path = io_dir / "Full_data.csv"
    plot_path: Path = io_valid_hh_agg_dir / "Validation_Plot_Batch.png"
    report_path: Path = io_valid_hh_agg_dir / "Validation_Report_HH.txt"

    if not full_data_path.exists():
        print(
            "❌ Error: Full_data.csv not found. Run run_household_aggregation() first."
        )
        return

    print("Loading data for validation...")
    df_full: pd.DataFrame = pd.read_csv(full_data_path, low_memory=False)

    validate_household_aggregation(df_full, report_path=report_path)
    visualize_multiple_households(
        df_full, n_samples=16, output_img_path=plot_path, report_path=report_path
    )

    print(f"\n✅ Full Validation Report saved to: {report_path.name}")


# =============================================================================
# CONTROL PANEL
# Set each flag to True to run that sub-step when executing this file directly.
# Run sub-steps in order — each one depends on the output of the previous.
# =============================================================================
if __name__ == "__main__":
    RUN_ASSEMBLE_HH: bool = False  # produces forecasted_population_2025_LINKED.csv
    RUN_PROFILE_MATCHER: bool = (
        False  # produces Matched_Population_Keys.csv + Full_Expanded_Schedules.csv
    )
    RUN_VALIDATE_PM: bool = False  # produces Validation_ProfileMatcher_2025.txt
    RUN_POSTPROCESSING: bool = False  # produces Full_Expanded_Schedules_Refined.csv
    RUN_HH_AGGREGATION: bool = False  # produces Full_data.csv
    RUN_VALIDATE_HH_AGG: bool = (
        False  # produces Validation_Report_HH.txt + Validation_Plot_Batch.png
    )

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
