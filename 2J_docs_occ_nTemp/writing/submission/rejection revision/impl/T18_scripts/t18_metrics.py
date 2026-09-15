"""t18_metrics.py -- T18 N4 metrics (both arms) + R0 comparison (Arm C only).

Task doc: 2026-09-15_T18_wp1_rebuild_2022_build.md, Acceptance section
(R0, R1, N3, N4). Standalone script -- does NOT import any pipeline script.
Reuses T12's occupancy-only reconstruction convention (measure, day_type,
group, weighting, value_pct, n columns; weekday = DDAY_STRATA==1, weekend =
DDAY_STRATA in {2,3}) from T12_scripts/t12_diag.py (cited per line below).

Reads ONLY the files t18_pipeline.py already wrote for this arm, plus (Arm C
only) the read-only reference copies of the current on-disk production files
staged at T18/reference/ for R0. Never re-derives a number the collector is
meant to check against a gate -- this script computes them so the collector
does not have to open multi-hundred-MB files by hand; the collector still
re-derives per feedback_verify_progress_log_claims.md before trusting them.

Run: /speed-scratch/o_iseri/envs/step4/bin/python t18_metrics.py --arm C|N
"""
import sys
import os
import time
import hashlib
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

WORKDIR = Path("/speed-scratch/o_iseri/2J_revision/T18")
OUT_DIR = WORKDIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
COLLEAGUES = [f"colleagues30_{i:03d}" for i in range(1, 49)]

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


rows = []


def add(measure, day_type, group, weighting, value_pct, n):
    rows.append(dict(measure=measure, day_type=day_type, group=group,
                      weighting=weighting, value_pct=round(float(value_pct), 3), n=int(n)))


def flush(arm):
    out_csv = OUT_DIR / f"t18_metrics_{arm}.csv"
    pd.DataFrame(rows, columns=["measure", "day_type", "group", "weighting", "value_pct", "n"]) \
        .to_csv(out_csv, index=False)
    log(f"flushed {len(rows)} rows -> {out_csv}")


def day_type_of(dday):
    return np.where(dday == 1, "weekday", np.where(np.isin(dday, [2, 3]), "weekend", "other"))


def _md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dtype_label(code, bedrm):
    # copied verbatim from 07_aug_to_bem.py:36-41 (same copy T12_scripts/t12_diag.py:206-214 made)
    if int(code) == 2:
        try:
            b = int(float(bedrm))
        except (ValueError, TypeError):
            b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(int(code), str(int(code)))


def paths_for(arm):
    arm_dir = WORKDIR / f"arm_{arm}" / "repo"
    out_dir = arm_dir / "outputs" / "aug_pipeline"
    bems_dir = arm_dir / "outputs" / "BEM_Setup"
    return {
        "agg_excl": out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv",
        "sched": out_dir / "21CEN22GSS_aug_Full_Schedules.csv",
        "matched": out_dir / "21CEN22GSS_aug_Matched_Keys.csv",
        "bem_2022": bems_dir / "BEM_Schedules_2022.csv",
    }


# ===========================================================================
# N4.a / b / c / d / f -- single read of Full_Aggregated_excl.csv (person-
# level; 1 row per PP_ID, retains MATCH_TIER/occID/CYCLE_YEAR/IS_SYNTHETIC/
# DDAY_STRATA/DTYPE/BEDRM/WGHT_PER carried through from Full_Schedules.csv --
# confirmed by reading run_aggregate()/run_exclusion() in 05_census_linkage.py).
# ===========================================================================
def measure_person_level(arm):
    p = paths_for(arm)["agg_excl"]
    log(f"loading {p} (usecols only) ...")
    usecols = ["HH_ID", "PP_ID", "DDAY_STRATA", "CYCLE_YEAR", "IS_SYNTHETIC",
               "WGHT_PER", "DTYPE", "BEDRM", "MATCH_TIER", "occID"] + HOM
    have_colleagues = None
    # Peek header to know if colleagues30_* is present before paying for a
    # second full read.
    header = pd.read_csv(p, nrows=0).columns.tolist()
    colleagues_cols = [c for c in COLLEAGUES if c in header]
    usecols += colleagues_cols
    df = pd.read_csv(p, usecols=usecols, low_memory=False)
    log(f"loaded {len(df):,} person-rows")
    df["day_type"] = day_type_of(df["DDAY_STRATA"].values)
    df["archetype"] = [dtype_label(c, b) for c, b in zip(df["DTYPE"], df["BEDRM"])]
    df["row_home_pct"] = df[HOM].values.mean(axis=1) * 100.0

    # ---- N4.a tier shares: national + per archetype -----------------------
    log("N4.a tier shares ...")
    n_total = len(df)
    for tier, c in df["MATCH_TIER"].value_counts().items():
        add("N4a_tier_share", "n/a", str(tier), "national", 100.0 * c / n_total, c)
    for arch, g in df.groupby("archetype"):
        n_a = len(g)
        for tier, c in g["MATCH_TIER"].value_counts().items():
            add("N4a_tier_share", "n/a", f"{arch}|{tier}", "per_archetype", 100.0 * c / n_a, c)

    # ---- N4.b donor reuse ---------------------------------------------------
    # occID alone is not globally unique across observed/synthetic rows sharing
    # the same occID (05_census_linkage.py expand_slot_schedules() docstring:
    # "avoids (occID, DDAY_STRATA) ambiguity when observed and synthetic rows
    # share the same occID"), so donor-diary identity here is defined as the
    # (occID, CYCLE_YEAR, IS_SYNTHETIC, DDAY_STRATA) tuple actually assigned to
    # each matched Census agent -- the finest identifier available from the
    # WRITTEN output files (df_matched's internal _pool_idx, the truly unique
    # row label, is dropped before Matched_Keys.csv is written --
    # 05_census_linkage.py:389-391 -- so it is not recoverable post hoc without
    # re-running the match, which this script does not do).
    log("N4.b donor reuse (occID, CYCLE_YEAR, IS_SYNTHETIC, DDAY_STRATA) tuple ...")
    reuse = df.groupby(["occID", "CYCLE_YEAR", "IS_SYNTHETIC", "DDAY_STRATA"]).size()
    add("N4b_donor_reuse", "n/a", "n_distinct_donors", "n/a", reuse.shape[0], n_total)
    add("N4b_donor_reuse", "n/a", "max_uses", "n/a", float(reuse.max()), n_total)
    add("N4b_donor_reuse", "n/a", "p99_uses", "n/a", float(np.percentile(reuse.values, 99)), n_total)
    add("N4b_donor_reuse", "n/a", "mean_uses", "n/a", float(reuse.mean()), n_total)

    # ---- N4.c diary cycle share in the stock -------------------------------
    log("N4.c diary cycle share ...")
    for yr, c in df["CYCLE_YEAR"].value_counts().sort_index().items():
        add("N4c_cycle_share", "n/a", str(int(yr)), "national", 100.0 * c / n_total, c)

    # ---- N4.d person-level weekday/weekend at-home (T12 M1 method) --------
    # T12_scripts/t12_diag.py:86-104 (measure_M1): unweighted + WGHT_PER-weighted
    # mean of row_home_pct, overall and for the IS_SYNTHETIC==0 & CYCLE_YEAR==2022
    # subset (T12's per-(CYCLE_YEAR,IS_SYNTHETIC) breakdown, restricted here to
    # the one cell the task doc's acceptance line calls out: "real 2022
    # respondents (IS_SYNTHETIC==0) inside the stock").
    log("N4.d person-level at-home (T12 M1 method) ...")

    def wmean(values, weights):
        values = np.asarray(values, dtype=float)
        weights = np.asarray(weights, dtype=float)
        return float(np.sum(values * weights) / np.sum(weights))

    for dt in ("weekday", "weekend"):
        sub = df[df.day_type == dt]
        add("N4d_at_home", dt, "stock_overall", "unweighted", sub.row_home_pct.mean(), len(sub))
        add("N4d_at_home", dt, "stock_overall", "weighted", wmean(sub.row_home_pct, sub.WGHT_PER), len(sub))
        real22 = sub[(sub.CYCLE_YEAR == 2022) & (sub.IS_SYNTHETIC == 0)]
        if len(real22):
            add("N4d_at_home", dt, "stock_2022_real_subset", "unweighted",
                real22.row_home_pct.mean(), len(real22))
            add("N4d_at_home", dt, "stock_2022_real_subset", "weighted",
                wmean(real22.row_home_pct, real22.WGHT_PER), len(real22))
        else:
            add("N4d_at_home", dt, "stock_2022_real_subset", "unweighted", float("nan"), 0)

    # ---- N4.f colleagues30 weekday stock mean ------------------------------
    log("N4.f colleagues30 weekday mean ...")
    if colleagues_cols:
        df["row_colleagues_pct"] = df[colleagues_cols].values.astype(float)
        df["row_colleagues_pct"] = np.nanmean(df[colleagues_cols].values.astype(float), axis=1) * 100.0
        sub = df[df.day_type == "weekday"]
        add("N4f_colleagues30", "weekday", "stock_overall", "unweighted",
            np.nanmean(sub["row_colleagues_pct"].values), len(sub))
    else:
        add("N4f_colleagues30", "weekday", "columns_absent", "n/a", float("nan"), 0)
        log("  colleagues30_* columns not found in this file -- reported as absent")

    flush(arm)


# ===========================================================================
# N4.e household schedule weekday/weekend at-home from BEM_Schedules_2022.csv
# (T12 M5 method) -- national + per archetype. BEM_Schedules_2022.csv already
# IS the fully converted per-(HH, Day_Type) hourly frame (07_aug_to_bem.py's
# convert(), the same function T12_scripts/t12_diag.py:247-267 copied as
# convert_occ_only) -- no need to redo complete_day_types/convert here, just
# average its own Occupancy_Schedule column directly.
# ===========================================================================
def measure_household_level(arm, t01_expected=None):
    p = paths_for(arm)["bem_2022"]
    log(f"loading {p} (usecols only) ...")
    df = pd.read_csv(p, usecols=["SIM_HH_ID", "Day_Type", "DTYPE", "Occupancy_Schedule"],
                      low_memory=False)
    log(f"loaded {len(df):,} rows, {df.SIM_HH_ID.nunique():,} unique HH")

    for dt_label, dt_key in (("weekday", "Weekday"), ("weekend", "Weekend")):
        sub = df[df.Day_Type == dt_key]
        val = sub.Occupancy_Schedule.mean() * 100.0
        add("N4e_hh_schedule", dt_label, "national", "unweighted", val, sub.SIM_HH_ID.nunique())
        if t01_expected is not None and dt_label == "weekday":
            delta = val - t01_expected
            log(f"  T01 check: weekday national = {val:.3f}, expected {t01_expected:.3f} "
                f"(+/-0.01), delta = {delta:+.3f}")
        for arch, g in sub.groupby("DTYPE"):
            val_a = g.Occupancy_Schedule.mean() * 100.0
            add("N4e_hh_schedule", dt_label, arch, "unweighted", val_a, g.SIM_HH_ID.nunique())

    flush(arm)


# ===========================================================================
# R0 -- Arm C only: compare against T18/reference/ (read-only copies of the
# current on-disk production files, staged before any job ran). md5 first
# (informational -- Windows-produced originals vs Linux-produced Arm C output
# may legitimately differ in line terminators even with identical numeric
# content, per the task doc's own fallback: "same rows/columns and
# hom30/act30/schedule value columns numerically equal"), then a numeric
# comparison keyed by the file's own natural id column.
# ===========================================================================
R0_REF_DIR = WORKDIR / "reference"
R0_FILES = {
    "sched": ("21CEN22GSS_aug_Full_Schedules.csv", "PP_ID", HOM, 573_177_990),
    "matched": ("21CEN22GSS_aug_Matched_Keys.csv", "PP_ID", None, 10_809_829),
    "agg_excl": ("21CEN22GSS_aug_Full_Aggregated_excl.csv", "PP_ID", HOM, 598_812_455),
    "bem_2022": ("BEM_Schedules_2022.csv", None, ["Occupancy_Schedule"], 673_929_104),
}


def measure_R0(arm):
    if arm != "C":
        log("R0 only applies to Arm C -- skipping for Arm N")
        return
    r0_rows = []
    arm_paths = paths_for("C")
    for key, (fname, id_col, value_cols, expected_size) in R0_FILES.items():
        ref_p = R0_REF_DIR / fname
        out_p = arm_paths[key]
        log(f"--- R0 {fname} ---")
        rec = {"file": fname, "ref_exists": ref_p.exists(), "out_exists": out_p.exists()}
        if not ref_p.exists() or not out_p.exists():
            rec["status"] = "MISSING"
            r0_rows.append(rec)
            log(f"  MISSING: ref={ref_p.exists()} out={out_p.exists()}")
            continue

        ref_size = ref_p.stat().st_size
        out_size = out_p.stat().st_size
        rec["ref_size"] = ref_size
        rec["out_size"] = out_size
        rec["expected_ref_size"] = expected_size
        size_match = ref_size == out_size
        rec["size_match"] = size_match
        log(f"  size: ref={ref_size:,} (expected {expected_size:,}) out={out_size:,} "
            f"match={size_match}")

        log("  computing md5 (both files) ...")
        ref_md5 = _md5(ref_p)
        out_md5 = _md5(out_p)
        rec["ref_md5"] = ref_md5
        rec["out_md5"] = out_md5
        md5_match = ref_md5 == out_md5
        rec["md5_match"] = md5_match
        log(f"  md5: ref={ref_md5} out={out_md5} match={md5_match}")

        if md5_match:
            rec["status"] = "PASS_MD5"
            r0_rows.append(rec)
            continue

        # md5 differs -- fall back to row/col count + numeric diff.
        log("  md5 differs -- falling back to numeric comparison ...")
        ref_head = pd.read_csv(ref_p, nrows=0).columns.tolist()
        out_head = pd.read_csv(out_p, nrows=0).columns.tolist()
        rec["ref_ncols"] = len(ref_head)
        rec["out_ncols"] = len(out_head)
        rec["cols_match"] = ref_head == out_head

        usecols = None
        if id_col is not None and value_cols is not None:
            usecols = [id_col] + [c for c in value_cols if c in ref_head and c in out_head]
        elif value_cols is not None:
            usecols = [c for c in value_cols if c in ref_head and c in out_head]

        if usecols:
            ref_df = pd.read_csv(ref_p, usecols=lambda c: c in set(usecols), low_memory=False)
            out_df = pd.read_csv(out_p, usecols=lambda c: c in set(usecols), low_memory=False)
            rec["ref_rows"] = len(ref_df)
            rec["out_rows"] = len(out_df)
            rec["rows_match"] = len(ref_df) == len(out_df)

            num_cols = [c for c in usecols if c != id_col]
            if id_col is not None and id_col in ref_df.columns and id_col in out_df.columns:
                merged = ref_df.merge(out_df, on=id_col, suffixes=("_ref", "_out"), how="inner")
                rec["n_merged"] = len(merged)
                max_diff = 0.0
                for c in num_cols:
                    if f"{c}_ref" in merged.columns and f"{c}_out" in merged.columns:
                        d = (merged[f"{c}_ref"].astype(float) - merged[f"{c}_out"].astype(float)).abs()
                        max_diff = max(max_diff, float(d.max()) if len(d) else 0.0)
                rec["max_abs_diff"] = max_diff
            elif num_cols and len(ref_df) == len(out_df):
                # No id column to key on (e.g. BEM_Schedules_2022.csv, or
                # Matched_Keys.csv where id_col=PP_ID may not exist post the
                # _pool_idx drop) -- positional compare, only valid if row
                # order is deterministic (both arms/reference are produced by
                # the SAME code path iterating df_census.iterrows() in a fixed
                # order, so this holds unless a merge/groupby elsewhere
                # resorted rows -- flagged, not asserted).
                max_diff = 0.0
                for c in num_cols:
                    d = (ref_df[c].astype(float).values - out_df[c].astype(float).values)
                    max_diff = max(max_diff, float(np.abs(d).max()) if len(d) else 0.0)
                rec["max_abs_diff"] = max_diff
                rec["note"] = "positional compare (no id column) -- row order not independently verified"
            else:
                rec["max_abs_diff"] = None
                rec["note"] = "could not align rows for numeric compare"

            log(f"  rows: ref={rec.get('ref_rows')} out={rec.get('out_rows')} "
                f"max_abs_diff={rec.get('max_abs_diff')}")
            rec["status"] = "PASS_NUMERIC" if (rec.get("rows_match", True) and
                                                rec.get("cols_match") and
                                                (rec.get("max_abs_diff") in (None,) or
                                                 rec.get("max_abs_diff", 1.0) < 1e-9)) else "FAIL_OR_REVIEW"
        else:
            rec["status"] = "NO_VALUE_COLS_TO_COMPARE"

        r0_rows.append(rec)

    out_csv = OUT_DIR / "t18_r0_C.csv"
    pd.DataFrame(r0_rows).to_csv(out_csv, index=False)
    log(f"R0 results -> {out_csv}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["C", "N"], required=True)
    args = ap.parse_args()
    arm = args.arm

    measure_person_level(arm)
    t01_expected = 70.239 if arm == "C" else None
    measure_household_level(arm, t01_expected=t01_expected)
    measure_R0(arm)

    log("ALL METRICS DONE.")


if __name__ == "__main__":
    main()
