"""sample_for_testing.py — Run once to create 500-respondent stratified sample data.

Extracts a stratified sample from the full 64,061-respondent dataset,
preserving the CYCLE_YEAR × DDAY_STRATA distribution.

Usage:
    python sample_for_testing.py
"""

import os
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STEP3_DIR = os.path.join(SCRIPT_DIR, "outputs_step3")


def main():
    hetus_path = os.path.join(STEP3_DIR, "hetus_30min.csv")
    cop_path = os.path.join(STEP3_DIR, "copresence_30min.csv")

    print("Loading full datasets...")
    hetus = pd.read_csv(hetus_path, low_memory=False)
    cop = pd.read_csv(cop_path, low_memory=False)
    print(f"  hetus_30min:      {hetus.shape}")
    print(f"  copresence_30min: {cop.shape}")

    # Stratify by CYCLE_YEAR × DDAY_STRATA (12 cells)
    hetus["strat_key"] = (
        hetus["CYCLE_YEAR"].astype(str) + "_" + hetus["DDAY_STRATA"].astype(str)
    )

    sss = StratifiedShuffleSplit(n_splits=1, train_size=500, random_state=42)
    sample_idx, _ = next(sss.split(hetus, hetus["strat_key"]))

    hetus_sample = (
        hetus.iloc[sample_idx]
        .drop(columns=["strat_key"])
        .reset_index(drop=True)
    )
    # copresence_30min rows align positionally with hetus_30min (same row order,
    # occID not unique across cycles).  Use the same positional indices.
    cop_sample = cop.iloc[sample_idx].reset_index(drop=True)

    out_hetus = os.path.join(STEP3_DIR, "hetus_30min_SAMPLE.csv")
    out_cop = os.path.join(STEP3_DIR, "copresence_30min_SAMPLE.csv")

    hetus_sample.to_csv(out_hetus, index=False)
    cop_sample.to_csv(out_cop, index=False)

    print(f"\nSaved {out_hetus}")
    print(f"Saved {out_cop}")
    print(f"\nSample: {len(hetus_sample)} respondents")
    print(
        hetus_sample.groupby(["CYCLE_YEAR", "DDAY_STRATA"])
        .size()
        .unstack(fill_value=0)
    )


if __name__ == "__main__":
    main()
