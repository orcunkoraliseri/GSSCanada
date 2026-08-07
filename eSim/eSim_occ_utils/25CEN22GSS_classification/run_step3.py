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

import numpy as np
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


def _assign_province_codes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Layer A1 fix: expand GSS region codes (1–6) in the PR column to StatCan
    province codes so that BEMConverter can write distinct 'Alberta' vs
    'Prairies' labels (and 'BC' vs 'British Columbia', 'Atlantic' vs 'Eastern
    Canada').

    Why this is needed: the CVAE was trained on harmonized census data where
    the PR column was already collapsed to 1-6 GSS codes (46/47/48 → 4, etc.).
    The forecasted synthetic population therefore carries only 1-6 codes.
    This function probabilistically disaggregates each GSS region back to its
    constituent province codes using 2021 Census PUMF proportions, assigned
    once per household (SIM_HH_ID) so every row of the same household gets a
    consistent province label.

    Province proportions from 0_Occupancy/Outputs_CENSUS/cen21_filtered.csv:
      GSS 1 (Eastern):  NL(10)=21.2%, PEI(11)=6.3%, NS(12)=40.4%, NB(13)=32.1%
      GSS 4 (Prairies): MB(46)=19.8%, SK(47)=16.8%, AB(48)=63.4%
    Single-province regions (2, 3, 5, 6) map 1:1 with no randomness.
    """
    # (province_codes, weights) per GSS region code
    province_splits: dict[int, tuple[list[int], list[float]]] = {
        1: ([10, 11, 12, 13], [0.2119, 0.0633, 0.4043, 0.3205]),
        2: ([24], [1.0]),
        3: ([35], [1.0]),
        4: ([46, 47, 48], [0.1978, 0.1678, 0.6344]),
        5: ([59], [1.0]),
        6: ([70], [1.0]),
    }

    rng = np.random.default_rng(42)  # fixed seed → reproducible output

    # Assign one province code per unique SIM_HH_ID
    hh_pr = df[["SIM_HH_ID", "PR"]].drop_duplicates("SIM_HH_ID").copy()

    def _pick(gss_code: int) -> int:
        entry = province_splits.get(int(gss_code))
        if entry is None:
            return int(gss_code)
        codes, weights = entry
        if len(codes) == 1:
            return codes[0]
        w = np.array(weights, dtype=float)
        return int(rng.choice(codes, p=w / w.sum()))

    hh_pr["PR_prov"] = hh_pr["PR"].apply(_pick)
    prov_lookup: dict[int | str, int] = dict(zip(hh_pr["SIM_HH_ID"], hh_pr["PR_prov"]))
    df = df.copy()
    df["PR"] = df["SIM_HH_ID"].map(prov_lookup)
    return df


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

    # Layer A1: expand GSS 1-6 PR codes → StatCan province codes so that
    # BEMConverter can write 'Alberta' separately from 'Prairies'.
    print("1b. Assigning StatCan province codes to PR column...")
    df_full = _assign_province_codes(df_full)

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
