"""R1 analysis: regenerate HH34299 from current aug CSV and compare to IDF.

Writes scratch CSVs to avoid touching any on-disk BEM_Schedules_*.csv.
Runs with: py r1_analysis_scratch.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # GSSCanada-main/
AUG  = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline" / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
SCRATCH = Path(__file__).resolve().parent / "scratch_r1"
SCRATCH.mkdir(exist_ok=True)

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
MET = {0:0,1:125,2:175,3:190,4:195,5:70,6:105,7:170,8:110,9:90,10:85,11:245,12:105,13:140,14:135}
DAYTYPE = {1:"Weekday",2:"Weekend",3:"Weekend"}

# IDF-parsed weekday profile for Occ_Sch_HH_34299 (from in.idf lines 1737-1784)
IDF_WD = [0.833, 0.667, 0.667, 0.667, 0.667, 0.500,
          0.333, 0.333, 0.333, 0.333, 0.333, 0.333,
          0.667, 1.000, 1.000, 1.000, 1.000, 1.000,
          1.000, 1.000, 1.000, 1.000, 1.000, 1.000]

# Current on-disk weekday profile for HH34299 (from BEM_Schedules_2022.csv)
DISK_WD = [1.000, 1.000, 1.000, 0.667, 0.333, 0.500,
           0.333, 0.333, 0.167, 0.000, 0.000, 0.500,
           0.500, 0.667, 0.667, 0.667, 0.667, 0.667,
           1.000, 1.000, 1.000, 1.000, 1.000, 1.000]

TARGET_HH = 34299

print("=== R1 ANALYSIS: Schedule provenance recovery for HH34299 ===\n")
print(f"Loading aug CSV from: {AUG}")
print(f"Aug CSV mtime: {pd.Timestamp(AUG.stat().st_mtime, unit='s')}\n")

aug = pd.read_csv(AUG, low_memory=False)

# Check HH34299 in aug CSV
hh_rows = aug[aug["HH_ID"] == TARGET_HH]
print(f"HH34299 rows in aug CSV: {len(hh_rows)}")
print(f"  HHSIZE values: {sorted(hh_rows['HHSIZE'].unique().tolist())}")
print(f"  DDAY_STRATA values: {sorted(hh_rows['DDAY_STRATA'].unique().tolist())}")
print(f"  Unique members (rows per strata): {hh_rows.groupby('DDAY_STRATA').size().to_dict()}")

# Compute occ profile following generator logic (complete_day_types then groupby)
def complete_day_types(df):
    rng = np.random.default_rng(42)
    hh_strata = df.groupby("HH_ID")["DDAY_STRATA"].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])
    wd_pool = df[df["DDAY_STRATA"] == 1]
    we_pool = df[df["DDAY_STRATA"].isin([2, 3])]
    extra = []
    if wd_only:
        sub = df[df["HH_ID"].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[ACT + HOM] = we_pool.iloc[pick][ACT + HOM].values
        sub["DDAY_STRATA"] = 2
        extra.append(sub)
        print(f"  complete_day_types: donor-draw {len(wd_only):,} WD-only HHs -> Weekend ({len(sub):,} rows)")
    if we_only:
        sub = df[df["HH_ID"].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[ACT + HOM] = wd_pool.iloc[pick][ACT + HOM].values
        sub["DDAY_STRATA"] = 1
        extra.append(sub)
        print(f"  complete_day_types: donor-draw {len(we_only):,} WE-only HHs -> Weekday ({len(sub):,} rows)")
    return pd.concat([df] + extra, ignore_index=True) if extra else df

print("\n--- Running complete_day_types (seed=42) ---")
aug2 = complete_day_types(aug)

# Extract HH34299 after donor-draw
hh_after = aug2[aug2["HH_ID"] == TARGET_HH].copy()
hh_after["Day_Type"] = hh_after["DDAY_STRATA"].map(DAYTYPE)
print(f"\nHH34299 rows after complete_day_types: {len(hh_after)}")
print(f"  By Day_Type: {hh_after.groupby('Day_Type').size().to_dict()}")

# Compute occ48 for HH34299 weekday
wd_rows = hh_after[hh_after["Day_Type"] == "Weekday"]
print(f"\n  Weekday rows used for occ computation: {len(wd_rows)}")

if len(wd_rows) > 0:
    occ48 = wd_rows[HOM].mean().values  # shape (48,)
    occ24 = occ48.reshape(24, 2).mean(axis=1)  # pair-average
    print("\n--- HH34299 weekday occ24 (from current aug CSV, seed=42) ---")
    print(f"  Hour | Scratch | Disk_CSV | IDF    | dScratch-IDF")
    for h in range(24):
        print(f"  h{h:02d}  | {occ24[h]:.3f}   | {DISK_WD[h]:.3f}    | {IDF_WD[h]:.3f}  | {occ24[h]-IDF_WD[h]:+.3f}")
    print(f"\n  Scratch mean: {np.mean(occ24):.4f}")
    print(f"  Disk CSV mean: {np.mean(DISK_WD):.4f}")
    print(f"  IDF mean:     {np.mean(IDF_WD):.4f}")
    scratch_match_disk = np.allclose(occ24, DISK_WD, atol=0.001)
    scratch_match_idf  = np.allclose(occ24, IDF_WD,  atol=0.001)
    print(f"\n  Scratch ≡ Disk CSV (|Δ|≤0.001): {scratch_match_disk}")
    print(f"  Scratch ≡ IDF      (|Δ|≤0.001): {scratch_match_idf}")
    # Save scratch profile
    pd.DataFrame({"hour": range(24), "scratch_occ": np.round(occ24, 3),
                  "disk_occ": DISK_WD, "idf_occ": IDF_WD}).to_csv(
        SCRATCH / "hh34299_wd_comparison.csv", index=False)
    print(f"\n  Comparison saved to: {SCRATCH/'hh34299_wd_comparison.csv'}")

# Also compute for ≥9 additional HHs to spot-check
print("\n--- Spot-check: first 10 SingleD Ontario HHs in current CSV vs regenerated ---")
disk_csv = pd.read_csv(BASE / "BEM_Setup" / "BEM_Schedules_2022.csv", low_memory=False)
disk_wd = disk_csv[(disk_csv["DTYPE"] == "SingleD") & (disk_csv["Day_Type"] == "Weekday") & (disk_csv["PR"] == "Ontario")]
sample_hhs = disk_wd["SIM_HH_ID"].drop_duplicates().head(10).tolist()

aug2["Day_Type_gen"] = aug2["DDAY_STRATA"].map(DAYTYPE)
hh_col = "HH_ID"
big_diffs = []
for hh_id in sample_hhs:
    wd_gen = aug2[(aug2[hh_col] == int(hh_id)) & (aug2["Day_Type_gen"] == "Weekday")]
    if len(wd_gen) == 0:
        continue
    gen_occ24 = wd_gen[HOM].mean().values.reshape(24, 2).mean(axis=1)
    disk_occ24 = disk_wd[disk_wd["SIM_HH_ID"].astype(str) == str(hh_id)].sort_values("Hour")["Occupancy_Schedule"].values
    if len(disk_occ24) < 24:
        continue
    max_diff = np.abs(gen_occ24 - disk_occ24).max()
    big_diffs.append((hh_id, max_diff, np.mean(gen_occ24), np.mean(disk_occ24)))
    status = "MATCH" if max_diff < 0.001 else "DIFF"
    print(f"  HH{hh_id}: gen_mean={np.mean(gen_occ24):.3f} disk_mean={np.mean(disk_occ24):.3f} max|Δ|={max_diff:.3f} {status}")

print("\n=== R1 CONCLUSION ===")
if len(wd_rows) > 0:
    if scratch_match_disk and not scratch_match_idf:
        print("OUTCOME B: Current aug CSV regenerates Disk CSV profile (0.653), NOT IDF profile (0.736).")
        print("  → As-built schedule UNRECOVERABLE from current code + input.")
        print("  → The IDF was built from a prior state of BEM_Schedules_2022.csv")
        print("    that no longer exists on disk (neither in PRE_STEP8_BAK nor any archive).")
    elif scratch_match_idf:
        print("OUTCOME A: Regeneration matches IDF → as-built schedule IS recoverable.")
    else:
        print("OUTCOME C: Scratch matches neither Disk CSV nor IDF — unexpected state.")
