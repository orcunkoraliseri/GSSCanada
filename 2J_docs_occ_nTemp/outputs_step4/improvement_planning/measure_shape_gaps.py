"""measure_shape_gaps.py — Task B / B6: re-measure the 3-channel (equipment/lighting/
metabolic) obs-vs-calibrated shape gaps on the post-Task-B population.

Method (mirrors the original v5-report comparison, adapted to reuse production code
for exact methodological consistency):
  - "obs"   side: pure-observed households (ALL members IS_SYNTHETIC==0) drawn from
    21CEN22GSS_aug_Full_Aggregated_excl.csv, run through 07_aug_to_bem.convert() —
    the SAME function that builds BEM_Schedules_2022.csv — so obs and calibrated
    sides get identical activity_loads weighting/calibration treatment.
  - "calibrated" side: the freshly rebuilt BEM_Schedules_2022.csv (Task B population).
  - Compared on Weekday only: the obs subset's Weekend sample is thin (~5.9k of
    80k pure-obs member-rows), so a Weekday-only comparison is the reliable read;
    Weekend obs is reported as INFO-only with a small-sample caveat.

This is a report-only diagnostic (step4_improvements_implementation.md line 114:
"report-only first, promote to gates once stable") — not a pass/fail gate.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STEP4_ROOT = HERE.parents[1]          # 2J_docs_occ_nTemp/
sys.path.insert(0, str(STEP4_ROOT))
import importlib
_a2b = importlib.import_module("07_aug_to_bem")

BASE = STEP4_ROOT.parent               # GSSCanada-main/
AUG_PATH = BASE/"0_Occupancy"/"Outputs_21CEN22GSS"/"aug_pipeline"/"21CEN22GSS_aug_Full_Aggregated_excl.csv"
CALIB_PATH = BASE/"BEM_Setup"/"BEM_Schedules_2022.csv"

print("Loading Full_Aggregated_excl.csv (obs side)...", flush=True)
agg = pd.read_csv(AUG_PATH, low_memory=False)

pure_obs_hh = agg.groupby("HH_ID")["IS_SYNTHETIC"].apply(lambda s: (s == 0).all())
pure_ids = set(pure_obs_hh.index[pure_obs_hh])
obs_df = agg[agg["HH_ID"].isin(pure_ids)].copy()
print(f"  pure-obs HHs: {len(pure_ids):,} / {agg['HH_ID'].nunique():,} total HHs "
      f"({len(obs_df):,} member-rows)", flush=True)

print("Running obs subset through 07_aug_to_bem.convert() (same code as production)...", flush=True)
obs_bem = _a2b.convert(obs_df)

print("Loading calibrated BEM_Schedules_2022.csv (Task B population)...", flush=True)
calib = pd.read_csv(CALIB_PATH, low_memory=False)

def hourly_profile(df, day_type, col):
    sub = df[df["Day_Type"] == day_type]
    return sub.groupby("Hour")[col].mean().reindex(range(24))

results = {}
for day_type in ("Weekday", "Weekend"):
    n_obs_hh = obs_bem.loc[obs_bem.Day_Type == day_type, "SIM_HH_ID"].nunique()
    n_calib_hh = calib.loc[calib.Day_Type == day_type, "SIM_HH_ID"].nunique()
    row = {"n_obs_hh": n_obs_hh, "n_calib_hh": n_calib_hh}
    for channel, col in (("equipment", "Equipment_Fraction"),
                          ("lighting", "Lighting_Fraction"),
                          ("occupancy", "Occupancy_Schedule")):
        o = hourly_profile(obs_bem, day_type, col)
        c = hourly_profile(calib, day_type, col)
        delta = (c - o).abs()
        row[f"{channel}_mean_abs_delta_pp"] = float(delta.mean()) * 100
        row[f"{channel}_peak_abs_delta_pp"] = float(delta.max()) * 100
        row[f"{channel}_peak_hour"] = int(delta.idxmax())
    o_met = obs_bem.loc[obs_bem.Day_Type == day_type, "Metabolic_Rate"].mean()
    c_met = calib.loc[calib.Day_Type == day_type, "Metabolic_Rate"].mean()
    row["metabolic_obs_mean_W"] = float(o_met)
    row["metabolic_calib_mean_W"] = float(c_met)
    row["metabolic_pct_delta"] = float((c_met - o_met) / o_met * 100)
    results[day_type] = row

print("\n=== 3-channel obs-vs-calibrated shape gaps (Task B population, 2022) ===")
for day_type, row in results.items():
    caveat = "  [INFO-ONLY, thin obs sample]" if day_type == "Weekend" else ""
    print(f"\n-- {day_type}{caveat} -- obs HHs={row['n_obs_hh']:,}  calib HHs={row['n_calib_hh']:,}")
    print(f"  Equipment shape: mean|Delta| {row['equipment_mean_abs_delta_pp']:.2f} pp, "
          f"peak {row['equipment_peak_abs_delta_pp']:.2f} pp @ hour {row['equipment_peak_hour']}")
    print(f"  Lighting  shape: mean|Delta| {row['lighting_mean_abs_delta_pp']:.2f} pp, "
          f"peak {row['lighting_peak_abs_delta_pp']:.2f} pp @ hour {row['lighting_peak_hour']}")
    print(f"  Occupancy shape: mean|Delta| {row['occupancy_mean_abs_delta_pp']:.2f} pp, "
          f"peak {row['occupancy_peak_abs_delta_pp']:.2f} pp @ hour {row['occupancy_peak_hour']}")
    print(f"  Metabolic: obs={row['metabolic_obs_mean_W']:.1f} W  calib={row['metabolic_calib_mean_W']:.1f} W  "
          f"%Delta={row['metabolic_pct_delta']:+.2f}%")
