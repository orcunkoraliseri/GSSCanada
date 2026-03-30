# =============================================================================
# run_step3.py
# Step 3 Runner: Occupancy to BEM Input
#
# This file wraps the "OCC to BEM input" block from eSim_dynamicML_mHead.py
# into a callable function. No existing file is modified.
# =============================================================================

from __future__ import annotations

import pathlib
import sys
from pathlib import Path

import pandas as pd

# --- Import only what is needed from the existing source file ---
from previous.eSim_dynamicML_mHead import BEMConverter, visualize_bem_distributions

# --- Path Configuration (same pattern used in eSim_dynamicML_mHead.py) ---
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from eSim_occ_utils.occ_config import (
    BASE_DIR,
    DATA_DIR,
    MODEL_DIR,
    OUTPUT_DIR,
    OUTPUT_DIR_ALIGNED,
)


def run_bem_conversion() -> None:
    """
    Converts household occupancy time-grid into hourly BEM-ready schedules.

    This function loads Full_data.csv, processes it through the BEMConverter,
    saves the resulting hourly schedules and metabolic rates, and generates
    validation visualizations.

    Inputs:
        OUTPUT_DIR / Full_data.csv (produced by run_step2.py)

    Outputs:
        OUTPUT_DIR / BEM_Schedules_2025.csv
        OUTPUT_DIR / BEM_Schedules_2025_temporals.png
        OUTPUT_DIR / BEM_Schedules_2025_non_temporals.png

    Returns:
        None
    """
    io_dir: Path = Path(OUTPUT_DIR)
    full_data_path: Path = io_dir / "Full_data.csv"
    output_path: Path = io_dir / "BEM_Schedules_2025.csv"
    output_path_vis: Path = io_dir

    if not full_data_path.exists():
        print("❌ Error: Full_data.csv not found.")
        print(f"   Expected location: {full_data_path}")
        print("   Please run run_step2.py (Household Aggregation) first.")
        return

    print("1. Loading Household Data...")
    df_full: pd.DataFrame = pd.read_csv(full_data_path, low_memory=False)

    # Initialize Converter
    converter: BEMConverter = BEMConverter(output_dir=io_dir)

    # Run conversion
    df_bem: pd.DataFrame = converter.process_households(df_full)

    # Save
    # float_format='%.3f' ensures 0.333 is written as "0.333" not ".333"
    print(f"2. Saving Hourly BEM Input to: {output_path.name}")
    df_bem.to_csv(output_path, index=False, float_format="%.3f")

    # Verify
    print("\n--- Verification: Sample Household ---")
    pd.options.display.float_format = "{:.3f}".format
    cols_to_show: list[str] = [
        "SIM_HH_ID",
        "Hour",
        "DTYPE",
        "BEDRM",
        "ROOM",
        "PR",
        "Occupancy_Schedule",
        "Metabolic_Rate",
    ]
    valid_cols: list[str] = [c for c in cols_to_show if c in df_bem.columns]
    print(df_bem[valid_cols].head(12).to_string(index=False))

    print("\n✅ Step 3 Complete. Ready for EnergyPlus/Honeybee.")
    visualize_bem_distributions(df_bem, output_dir=output_path_vis)


# =============================================================================
# CONTROL PANEL
# Set RUN_BEM_CONVERSION = True to execute when running this file directly.
# =============================================================================
if __name__ == "__main__":
    RUN_BEM_CONVERSION: bool = True

    if RUN_BEM_CONVERSION:
        run_bem_conversion()
