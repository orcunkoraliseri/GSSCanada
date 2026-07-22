"""
investigate_3fails_probe3.py — FAIL 3: exact donor attribution for the 24 PR=6
(Territories) census agents by deterministically reproducing the production
match (seed 42, MIN_POOL=15) in memory and verifying it against the saved
3rdJ_25CEN_aug_Matched_Keys.csv before reading off _pool_idx donors.

Read-only on production artifacts; writes nothing (stdout only).
Run:  py -3 -X utf8 investigate_3fails_probe3.py > INVESTIGATION_probe3.log
"""
from __future__ import annotations

import importlib.util as ilu
import os
from pathlib import Path

import numpy as np
import pandas as pd

assert os.environ.get("STEP5_MIN_POOL") in (None, "15"), "must run at MIN_POOL=15"

HERE = Path(__file__).resolve()
STEP5 = HERE.parents[2]
OUT = STEP5 / "outputs_step5"

_spec = ilu.spec_from_file_location("_m", STEP5 / "3rdJ_05_censusLinkage_4split.py")
M = ilu.module_from_spec(_spec)
_spec.loader.exec_module(M)

# ── Pool: replicate load_augmented_pool() with a slim column set (row order and
# indices are unaffected by usecols; run_slot_match touches only keys + occID).
KEEP = {"occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC",
        "AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA"}
df = pd.read_csv(M.FULL_POOL, usecols=lambda c: c in KEEP, low_memory=False)
df["PR_raw"] = df["PR"]
remapped = df["PR"].map(M._PROVINCE_TO_REGION)
assert not remapped.isna().any()
df["PR"] = remapped.astype(int)
df = M.harmonize_cma(df, side="pool")
wd_pool = df[df["DDAY_STRATA"] == 1].reset_index(drop=True)
we_pool = df[df["DDAY_STRATA"].isin([2, 3])].reset_index(drop=True)
df_pool = pd.concat([wd_pool, we_pool], ignore_index=True)
print(f"pool rows: {len(df_pool):,}")

# ── Census: replicate run_linkage_full()'s prep exactly (module functions).
df_census = pd.read_csv(M.CENSUS_FILE)
df_census = df_census.drop_duplicates(subset="PID").reset_index(drop=True)
df_census = M.harmonize_cma(df_census, side="census")
df_census = M.harmonize_lftag_census(df_census)
# build_office_archetype_lookup intentionally SKIPPED (writes a file; does not
# mutate the census frame and no RNG is consumed between here and the match).
df_census_dday = M._assign_dday(df_census, seed=42)
print(f"census agents: {len(df_census_dday):,}")

# ── Deterministic re-match (np.random.seed(42) inside run_slot_match).
df_matched = M.run_slot_match(df_census_dday, df_pool, M.MATCH_KEYS, M.DDAY_COL)

# ── Verify reproduction against the saved production Matched_Keys.
saved = pd.read_csv(OUT / "3rdJ_25CEN_aug_Matched_Keys.csv", low_memory=False)
cmp = saved.merge(df_matched, on="PID", suffixes=("_saved", "_repro"))
n_occ = int((cmp["occID_saved"] == cmp["occID_repro"]).sum())
n_tier = int((cmp["MATCH_TIER_saved"] == cmp["MATCH_TIER_repro"]).sum())
n_dday = int((cmp["DDAY_STRATA_saved"] == cmp["DDAY_STRATA_repro"]).sum())
print(f"\n[verify] rows compared: {len(cmp):,} / saved {len(saved):,}")
print(f"[verify] occID equal: {n_occ:,}  MATCH_TIER equal: {n_tier:,}  DDAY equal: {n_dday:,}")
exact = (len(cmp) == len(saved) == n_occ == n_tier == n_dday)
print(f"[verify] EXACT REPRODUCTION: {'YES' if exact else 'NO - do not trust donor table'}")

# ── PR=6 donor attribution from _pool_idx (only meaningful if exact).
pr6_pids = df_census_dday.loc[df_census_dday["PR"] == 6, "PID"]
m6 = df_matched[df_matched["PID"].isin(pr6_pids)].copy()
donors = df_pool.loc[m6["_pool_idx"].to_numpy()].reset_index(drop=True)
m6 = m6.reset_index(drop=True)
region_lbl = {1: "Atlantic", 2: "Quebec", 3: "Ontario", 4: "Prairies", 5: "BC", 6: "North"}

print(f"\n[PR6] n={len(m6)}; tier: "
      + ", ".join(f"{t}={c}" for t, c in m6["MATCH_TIER"].value_counts().items()))
print("[PR6] donor region distribution (exact, from _pool_idx):")
for v, c in donors["PR"].value_counts().sort_index().items():
    print(f"    region={v} ({region_lbl[int(v)]}): {c} ({100*c/len(donors):.1f}%)")
print("[PR6] donor raw PR codes: "
      + ", ".join(f"{v}={c}" for v, c in donors["PR_raw"].value_counts().sort_index().items()))
print("[PR6] donor IS_SYNTHETIC: "
      + ", ".join(f"{int(v)}={c}" for v, c in donors["IS_SYNTHETIC"].value_counts().sort_index().items()))
print("[PR6] donor CYCLE_YEAR: "
      + ", ".join(f"{int(v)}={c}" for v, c in donors["CYCLE_YEAR"].value_counts().sort_index().items()))
print("[PR6] unique donor occIDs: " + str(donors["occID"].nunique()))

# Cross-check IS_SYNTHETIC vs the carried column in Full_Schedules.
fs = pd.read_csv(OUT / "3rdJ_25CEN_aug_Full_Schedules.csv",
                 usecols=["PID", "IS_SYNTHETIC", "PR"], low_memory=False)
fs6 = fs[fs["PR"] == 6].merge(
    pd.concat([m6[["PID"]], donors[["IS_SYNTHETIC"]].rename(
        columns={"IS_SYNTHETIC": "IS_SYN_repro"})], axis=1), on="PID")
agree = int((fs6["IS_SYNTHETIC"] == fs6["IS_SYN_repro"]).sum())
print(f"[PR6] IS_SYNTHETIC agreement vs Full_Schedules carried col: {agree}/{len(fs6)}")
print("\nDONE.")
