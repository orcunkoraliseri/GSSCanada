#!/usr/bin/env python
"""
T18 collector verification job.
Written by the collector agent (not the employee) to:
  (A) N3 leakage check: md5 the 4 T18/reference/* files now, compare to the
      "before" md5s recorded in the task doc's Ledger (hardcoded below).
  (B) R0 fallback comparison: Arm C output vs T18/reference/*, for the three
      person-level files (join on PP_ID) and BEM_Schedules_2022.csv (join on
      the natural composite key SIM_HH_ID+Day_Type+Hour, which the file does
      carry -- more robust than a positional fallback).
  (C) N4.a/b/c/d/e/f metrics for Arm C and Arm N, fixed version of the
      employee's t18_metrics.py (bug: t18_metrics.py:179 assigned a
      (n,48)-shape array into one column before line 180 recomputed it
      correctly with nanmean -- line 179 is simply deleted here).
  (D) Addendum: Arm N's BEM_Schedules_2022.csv vs the current published 2022
      file (= T18/reference/BEM_Schedules_2022.csv, the same file used for R0):
      household ID set equality, Equip_Design_W/Light_Design_W per household
      equality, and the frame demographic columns (HHSIZE, DTYPE, BEDRM,
      CONDO, ROOM, REPAIR, PR) per household equality.

Never writes into T18/out or T18/reference. All outputs go under
T18/collector/out/.
"""
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

T18 = "/speed-scratch/o_iseri/2J_revision/T18"
OUT = f"{T18}/collector/out"
os.makedirs(OUT, exist_ok=True)

T0 = time.time()


def log(msg):
    print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)


def md5_file(path, bufsize=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# (A) N3 leakage check
# ===========================================================================
BEFORE_MD5 = {
    "21CEN22GSS_aug_Full_Aggregated_excl.csv": "d8f08217f5923c48de8b6849df715c11",
    "21CEN22GSS_aug_Full_Schedules.csv": "db7f738f8eba1cb9e9d23b28386ee27d",
    "21CEN22GSS_aug_Matched_Keys.csv": "4aa0814b7c2b954b228465c835bc6e42",
    "BEM_Schedules_2022.csv": "30fd815869942c1c292b6dfd26eaf8ad",
}


def n3_check():
    log("=== N3 leakage check: md5 of T18/reference/* now vs before ===")
    rows = []
    for fname, before in BEFORE_MD5.items():
        p = f"{T18}/reference/{fname}"
        now = md5_file(p)
        ok = (now == before)
        rows.append({"file": fname, "before_md5": before, "after_md5": now, "unchanged": ok})
        log(f"  {fname}: before={before} after={now} unchanged={ok}")
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/t18_collector_N3.csv", index=False)
    return df


# ===========================================================================
# (B) R0 fallback comparison, Arm C vs reference
# ===========================================================================
def r0_person_file(name, key="PP_ID"):
    log(f"=== R0 {name} (join on {key}) ===")
    ref_p = f"{T18}/reference/{name}"
    c_p = f"{T18}/arm_C/repo/outputs/aug_pipeline/{name}"
    ref = pd.read_csv(ref_p, low_memory=False)
    c = pd.read_csv(c_p, low_memory=False)
    log(f"  reference: {ref.shape}, arm_C: {c.shape}")
    same_cols = set(ref.columns) == set(c.columns)
    common_cols = [col for col in ref.columns if col in c.columns]
    m = ref.merge(c, on=key, how="outer", suffixes=("_ref", "_c"), indicator=True)
    only_ref = int((m["_merge"] == "left_only").sum())
    only_c = int((m["_merge"] == "right_only").sum())
    num_cols = [col for col in common_cols if col != key
                and pd.api.types.is_numeric_dtype(ref[col])]
    max_abs_diff = 0.0
    worst_col = None
    mismatched_cells = 0
    both = m[m["_merge"] == "both"]
    for col in num_cols:
        a = both.get(f"{col}_ref")
        b = both.get(f"{col}_c")
        if a is None or b is None:
            continue
        diff = (a.astype(float) - b.astype(float)).abs()
        d = float(np.nanmax(diff.values)) if len(diff) else 0.0
        mismatched_cells += int((diff > 1e-9).sum())
        if d > max_abs_diff:
            max_abs_diff = d
            worst_col = col
    result = {
        "file": name, "ref_rows": len(ref), "c_rows": len(c),
        "same_columns": same_cols, "n_common_numeric_cols": len(num_cols),
        "rows_only_in_ref": only_ref, "rows_only_in_c": only_c,
        "max_abs_diff": max_abs_diff, "worst_col": worst_col,
        "mismatched_cells": mismatched_cells,
    }
    log(f"  {result}")
    return result


def r0_bem_file():
    name = "BEM_Schedules_2022.csv"
    log(f"=== R0 {name} (join on SIM_HH_ID+Day_Type+Hour) ===")
    ref_p = f"{T18}/reference/{name}"
    c_p = f"{T18}/arm_C/repo/outputs/BEM_Setup/{name}"
    usecols = ["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule",
               "Metabolic_Rate", "Equipment_Fraction", "Lighting_Fraction",
               "Equip_Design_W", "Light_Design_W"]
    ref = pd.read_csv(ref_p, usecols=usecols, low_memory=False)
    c = pd.read_csv(c_p, usecols=usecols, low_memory=False)
    log(f"  reference: {ref.shape}, arm_C: {c.shape}")
    key = ["SIM_HH_ID", "Day_Type", "Hour"]
    m = ref.merge(c, on=key, how="outer", suffixes=("_ref", "_c"), indicator=True)
    only_ref = int((m["_merge"] == "left_only").sum())
    only_c = int((m["_merge"] == "right_only").sum())
    num_cols = ["Occupancy_Schedule", "Metabolic_Rate", "Equipment_Fraction",
                "Lighting_Fraction", "Equip_Design_W", "Light_Design_W"]
    both = m[m["_merge"] == "both"]
    max_abs_diff = 0.0
    worst_col = None
    mismatched_cells = 0
    for col in num_cols:
        a = both.get(f"{col}_ref")
        b = both.get(f"{col}_c")
        if a is None or b is None:
            continue
        diff = (a.astype(float) - b.astype(float)).abs()
        d = float(np.nanmax(diff.values)) if len(diff) else 0.0
        mismatched_cells += int((diff > 1e-9).sum())
        if d > max_abs_diff:
            max_abs_diff = d
            worst_col = col
    result = {
        "file": name, "ref_rows": len(ref), "c_rows": len(c),
        "join_key": "+".join(key), "n_numeric_cols": len(num_cols),
        "rows_only_in_ref": only_ref, "rows_only_in_c": only_c,
        "max_abs_diff": max_abs_diff, "worst_col": worst_col,
        "mismatched_cells": mismatched_cells,
    }
    log(f"  {result}")
    return result


def r0_check():
    rows = []
    rows.append(r0_person_file("21CEN22GSS_aug_Full_Schedules.csv", key="PP_ID"))
    rows.append(r0_person_file("21CEN22GSS_aug_Matched_Keys.csv", key="PP_ID"))
    rows.append(r0_person_file("21CEN22GSS_aug_Full_Aggregated_excl.csv", key="PP_ID"))
    rows.append(r0_bem_file())
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/t18_collector_R0.csv", index=False)
    return df


# ===========================================================================
# (C) N4 metrics, fixed, both arms
# ===========================================================================
def arm_paths(arm):
    base = f"{T18}/arm_{arm}/repo/outputs"
    return {
        "matched_keys": f"{base}/aug_pipeline/21CEN22GSS_aug_Matched_Keys.csv",
        "agg_excl": f"{base}/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv",
        "bem_2022": f"{base}/BEM_Setup/BEM_Schedules_2022.csv",
    }


def n4_metrics(arm):
    log(f"=== N4 metrics, arm {arm} ===")
    rows = []

    def add(metric, day_type, cell, kind, value, n):
        rows.append({"arm": arm, "metric": metric, "day_type": day_type,
                      "cell": cell, "kind": kind, "value": value, "n": n})

    # N4.a tier shares (from Matched_Keys.csv, cheap column)
    mk = pd.read_csv(arm_paths(arm)["matched_keys"], usecols=["MATCH_TIER"])
    n_total_tier = len(mk)
    tier_counts = mk["MATCH_TIER"].value_counts()
    for tier, cnt in tier_counts.items():
        add("N4a_tier_share", "n/a", tier, "national",
            100.0 * cnt / n_total_tier, int(cnt))
    log(f"  N4.a: {tier_counts.to_dict()}")

    # N4.b donor reuse proxy: (occID, CYCLE_YEAR, IS_SYNTHETIC, DDAY_STRATA)
    mk2 = pd.read_csv(arm_paths(arm)["matched_keys"],
                       usecols=["occID", "DDAY_STRATA"])
    reuse = mk2.groupby(["occID", "DDAY_STRATA"]).size()
    add("N4b_donor_reuse", "n/a", "n_distinct_donor_tuples", "n/a",
        reuse.shape[0], n_total_tier)
    add("N4b_donor_reuse", "n/a", "max_uses", "n/a", float(reuse.max()), n_total_tier)
    add("N4b_donor_reuse", "n/a", "p99_uses", "n/a",
        float(np.percentile(reuse.values, 99)), n_total_tier)
    log(f"  N4.b: n_distinct={reuse.shape[0]} max={reuse.max()} "
        f"p99={np.percentile(reuse.values, 99):.2f}")

    # N4.c/d/f from Full_Aggregated_excl.csv
    # NOTE: this file has NO "day_type" column (confirmed via header check on
    # Speed login node, single-file head/cut) -- one row per person, one
    # diary day. Weekday/weekend per T12_scripts/t12_diag.py:68-69 ("task doc
    # convention: weekday = DDAY_STRATA==1, weekend = 2 or 3") -- t18_metrics.py
    # had assumed a df.day_type column existed that in fact does not; using
    # the T12 M1 convention directly here instead.
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    coll_cols_guess = [f"colleagues30_{i:03d}" for i in range(1, 49)]
    header = pd.read_csv(arm_paths(arm)["agg_excl"], nrows=0).columns.tolist()
    colleagues_cols = [c for c in coll_cols_guess if c in header]
    base_cols = ["PP_ID", "CYCLE_YEAR", "IS_SYNTHETIC", "WGHT_PER", "DDAY_STRATA"]
    usecols = [c for c in base_cols if c in header] + \
        [c for c in hom_cols if c in header] + colleagues_cols
    df = pd.read_csv(arm_paths(arm)["agg_excl"], usecols=usecols, low_memory=False)
    n_total = len(df)
    log(f"  loaded {n_total:,} rows for N4.c/d/f, cols={len(usecols)}")

    def day_type_of(dday_strata):
        return np.where(dday_strata == 1, "weekday", "weekend")

    df["day_type"] = day_type_of(df["DDAY_STRATA"].values)

    # N4.c cycle share
    for yr, c in df["CYCLE_YEAR"].value_counts().sort_index().items():
        add("N4c_cycle_share", "n/a", str(int(yr)), "national",
            100.0 * c / n_total, int(c))

    present_hom = [c for c in hom_cols if c in df.columns]
    if present_hom:
        df["row_home_pct"] = df[present_hom].mean(axis=1, skipna=True) * 100.0

        def wmean(values, weights):
            values = np.asarray(values, dtype=float)
            weights = np.asarray(weights, dtype=float)
            return float(np.sum(values * weights) / np.sum(weights))

        for dt in ("weekday", "weekend"):
            sub = df[df.day_type == dt]
            add("N4d_at_home", dt, "stock_overall", "unweighted",
                sub["row_home_pct"].mean(), len(sub))
            if "WGHT_PER" in df.columns:
                add("N4d_at_home", dt, "stock_overall", "weighted",
                    wmean(sub["row_home_pct"], sub["WGHT_PER"]), len(sub))
            if "CYCLE_YEAR" in df.columns and "IS_SYNTHETIC" in df.columns:
                real22 = sub[(sub.CYCLE_YEAR == 2022) & (sub.IS_SYNTHETIC == 0)]
                if len(real22):
                    add("N4d_at_home", dt, "stock_2022_real_subset", "unweighted",
                        real22["row_home_pct"].mean(), len(real22))
    else:
        add("N4d_at_home", "n/a", "hom30_cols_absent", "n/a", float("nan"), 0)

    # N4.f colleagues30 weekday -- BUG FIX vs t18_metrics.py:179 (that line
    # assigned a (n,48)-shape array into a single column before line 180
    # recomputed it correctly with nanmean; here only the correct nanmean
    # assignment is kept).
    if colleagues_cols:
        df["row_colleagues_pct"] = np.nanmean(
            df[colleagues_cols].values.astype(float), axis=1) * 100.0
        sub = df[df.day_type == "weekday"]
        add("N4f_colleagues30", "weekday", "stock_overall", "unweighted",
            np.nanmean(sub["row_colleagues_pct"].values), len(sub))
        log(f"  N4.f colleagues30 weekday mean = "
            f"{np.nanmean(sub['row_colleagues_pct'].values):.3f}")
    else:
        add("N4f_colleagues30", "weekday", "columns_absent", "n/a", float("nan"), 0)
        log(f"  N4.f: colleagues30_* columns not found in {header[:5]}...")

    # N4.e household schedule at-home, from BEM_Schedules_2022.csv
    bp = arm_paths(arm)["bem_2022"]
    bdf = pd.read_csv(bp, usecols=["SIM_HH_ID", "Day_Type", "DTYPE",
                                    "Occupancy_Schedule"], low_memory=False)
    for dt_label, dt_key in (("weekday", "Weekday"), ("weekend", "Weekend")):
        sub = bdf[bdf.Day_Type == dt_key]
        val = sub.Occupancy_Schedule.mean() * 100.0
        add("N4e_hh_schedule", dt_label, "national", "unweighted",
            val, sub.SIM_HH_ID.nunique())
        for arch, g in sub.groupby("DTYPE"):
            val_a = g.Occupancy_Schedule.mean() * 100.0
            add("N4e_hh_schedule", dt_label, str(arch), "unweighted",
                val_a, g.SIM_HH_ID.nunique())
    log(f"  N4.e written")

    out = pd.DataFrame(rows)
    out.to_csv(f"{OUT}/t18_collector_metrics_{arm}.csv", index=False)
    return out


# ===========================================================================
# (D) Addendum: Arm N BEM_Schedules_2022.csv vs current published 2022 file
# ===========================================================================
def addendum_check():
    log("=== Addendum: Arm N vs current published 2022 file (T18/reference) ===")
    ref_p = f"{T18}/reference/BEM_Schedules_2022.csv"
    n_p = f"{T18}/arm_N/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv"
    demo_cols = ["HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR"]
    design_cols = ["Equip_Design_W", "Light_Design_W"]
    usecols = ["SIM_HH_ID"] + demo_cols + design_cols
    ref = pd.read_csv(ref_p, usecols=usecols, low_memory=False).drop_duplicates("SIM_HH_ID")
    n = pd.read_csv(n_p, usecols=usecols, low_memory=False).drop_duplicates("SIM_HH_ID")
    log(f"  reference unique HH: {len(ref):,}, Arm N unique HH: {len(n):,}")

    ref_ids = set(ref["SIM_HH_ID"])
    n_ids = set(n["SIM_HH_ID"])
    only_ref = len(ref_ids - n_ids)
    only_n = len(n_ids - ref_ids)
    common = len(ref_ids & n_ids)

    m = ref.merge(n, on="SIM_HH_ID", how="inner", suffixes=("_ref", "_n"))
    rows = [{
        "check": "household_id_set", "n_common_hh": common,
        "only_in_reference": only_ref, "only_in_arm_N": only_n,
        "ids_identical": (only_ref == 0 and only_n == 0),
    }]
    for col in demo_cols:
        mism = int((m[f"{col}_ref"].astype(str) != m[f"{col}_n"].astype(str)).sum())
        rows.append({"check": f"demographic_col:{col}", "n_common_hh": common,
                     "n_mismatched": mism, "identical": mism == 0})
    for col in design_cols:
        diff = (m[f"{col}_ref"].astype(float) - m[f"{col}_n"].astype(float)).abs()
        mism = int((diff > 1e-6).sum())
        rows.append({"check": f"design_col:{col}", "n_common_hh": common,
                     "n_mismatched": mism, "max_abs_diff": float(diff.max()),
                     "identical": mism == 0})
    for r in rows:
        log(f"  {r}")
    out = pd.DataFrame(rows)
    out.to_csv(f"{OUT}/t18_collector_addendum.csv", index=False)
    return out


def main():
    n3_check()
    r0_check()
    n4_metrics("C")
    n4_metrics("N")
    addendum_check()
    log("=== T18_COLLECTOR_VERIFY_COMPLETE ===")


if __name__ == "__main__":
    main()
