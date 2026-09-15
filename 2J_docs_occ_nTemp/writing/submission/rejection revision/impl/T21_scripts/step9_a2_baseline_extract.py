#!/usr/bin/env python3
"""step9_a2_baseline_extract.py — Extract 13-col baseline CSVs from existing activity CSVs.

The 2022/2030 activity CSVs (17-col) are already on the cluster.
This script derives BEM_Schedules_{year}_baseline.csv (13-col, no Step-9 cols)
from the same run so baseline and activity share identical HH IDs.

Usage: python step9_a2_baseline_extract.py --bem_dir <BEM_Setup directory>
"""
import argparse
import os
import pandas as pd

BASE_COLS = [
    "SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "DTYPE", "BEDRM",
    "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER",
    "Occupancy_Schedule", "Metabolic_Rate",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bem_dir", required=True)
    args = ap.parse_args()

    for yr in ("2022", "2030"):
        act_path  = os.path.join(args.bem_dir, f"BEM_Schedules_{yr}.csv")
        base_path = os.path.join(args.bem_dir, f"BEM_Schedules_{yr}_baseline.csv")
        if not os.path.exists(act_path):
            print(f"ERROR: missing {act_path}")
            raise SystemExit(1)
        print(f"Reading {os.path.basename(act_path)} ...", flush=True)
        df = pd.read_csv(act_path, low_memory=False)
        missing = [c for c in BASE_COLS if c not in df.columns]
        if missing:
            print(f"ERROR: activity CSV missing columns: {missing}")
            raise SystemExit(1)
        base_df = df[BASE_COLS]
        tmp = base_path + ".tmp"
        base_df.to_csv(tmp, index=False, float_format="%.3f")
        os.replace(tmp, base_path)
        nhh = base_df["SIM_HH_ID"].nunique()
        print(f"WROTE {os.path.basename(base_path)}: {len(base_df):,} rows, {nhh:,} HH (13-col baseline)", flush=True)

if __name__ == "__main__":
    main()
