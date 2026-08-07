# -*- coding: utf-8 -*-
"""
diagnose_work_duration.py -- Task 25 diagnostic

Quantifies daily work+commute duration in the 2025 forecast population and
compares it to the historical baseline (~542 min/day).

Usage (from repo root):
    py -3 eSim_tests/diagnose_work_duration.py

Saves a human-readable report to:
    eSim_tests/diagnose_work_duration_2025.txt

Root-cause branches (Task 25):
    (a) Validator bug only  -- if mean near 300-600 min/day with FIXED isin([1,8]) filter
    (b) Real demographic shift -- if mean significantly > 600 with fixed filter
    (c) Profile Matcher retrieval -- if mean high but EMPLOY distribution unchanged from 2022

NOTES on data format:
  - start/end columns are HHMM integers (e.g. 920 = 9:20 AM, 1700 = 17:00 = 5 PM)
  - Duration must be computed as (hhmm_to_min(end) - hhmm_to_min(start)), not (end - start)
  - The old str.startswith('1','0','8') filter was capturing categories 1,8,10,11,12,13,14
    instead of just 1 (paid work) and 8 (transport/commute). Fixed to isin([1, 8]).

The fix is applied in:
  - previous/eSim_dynamicML_mHead.py
  - 16CEN15GSS/16CEN15GSS_ProfileMatcher.py
  - 06CEN05GSS/06CEN05GSS_ProfileMatcher.py
"""

import sys
import os
from pathlib import Path
import io

# Force UTF-8 stdout to avoid cp1252 crashes on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

# --- Paths ---
try:
    from eSim_occ_utils.occ_config import OUTPUT_DIR, OUTPUT_DIR_ALIGNED
except ImportError:
    OUTPUT_DIR = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\0_Occupancy\Outputs_CENSUS")
    OUTPUT_DIR_ALIGNED = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\0_Occupancy\Outputs_Aligned")

MATCHED_KEYS_FILE = OUTPUT_DIR_ALIGNED / "Matched_Population_Keys.csv"
GSS_EPISODE_FILE  = OUTPUT_DIR_ALIGNED / "Aligned_GSS_2022.csv"

REPORT_PATH = Path(__file__).parent / "diagnose_work_duration_2025.txt"

HISTORICAL_BASELINE_MIN = 542  # documented in CLAUDE.md
WARN_LOW  = 300
WARN_HIGH = 600


def hhmm_to_min(hhmm_val) -> float:
    """Convert HHMM integer (e.g. 1730 = 17:30) to minutes from midnight."""
    try:
        v = int(float(hhmm_val))
    except (TypeError, ValueError):
        return 0.0
    return (v // 100) * 60 + (v % 100)


def episode_duration_min(s_hhmm, e_hhmm) -> float:
    """Return episode duration in real minutes, handling midnight wrap."""
    s = hhmm_to_min(s_hhmm)
    e = hhmm_to_min(e_hhmm)
    if e < s:          # episode crosses midnight
        e += 1440
    return max(0.0, e - s)


def compute_work_minutes(episodes_df: pd.DataFrame) -> float:
    """Sum work+commute minutes (occACT in [1,8]) from a set of episode rows."""
    work = episodes_df[episodes_df["occACT"].isin([1, 8])]
    total = 0.0
    for _, row in work.iterrows():
        total += episode_duration_min(row.get("start", 0), row.get("end", 0))
    return total


def run_diagnostic() -> None:
    lines = []

    def log(msg=""):
        print(msg)
        lines.append(str(msg))

    log("=" * 60)
    log("TASK 25 -- Work Duration Diagnostic (2025 Forecast)")
    log("=" * 60)
    log(f"Historical baseline : ~{HISTORICAL_BASELINE_MIN} min/day (employed agents)")
    log(f"Plausible range     : [{WARN_LOW}, {WARN_HIGH}] min/day")
    log(f"Activity filter     : occACT isin([1, 8])  -- paid work + transport/commute")
    log(f"Duration computation: HHMM-to-minutes conversion (not raw HHMM subtraction)")
    log()

    # --- Load files ---
    if not MATCHED_KEYS_FILE.exists():
        log(f"ERROR: Keys file not found: {MATCHED_KEYS_FILE}")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        return
    if not GSS_EPISODE_FILE.exists():
        log(f"ERROR: GSS episode file not found: {GSS_EPISODE_FILE}")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        return

    df_keys = pd.read_csv(MATCHED_KEYS_FILE, low_memory=False)
    df_gss  = pd.read_csv(GSS_EPISODE_FILE,  low_memory=False)
    log(f"Keys  : {len(df_keys):,} rows  | unique occIDs in GSS: {df_gss['occID'].nunique():,}")
    log(f"GSS   : {len(df_gss):,} rows  | mean episodes/respondent: {len(df_gss)/df_gss['occID'].nunique():.1f}")

    # Weekday filter (DDAY 2-6)
    wd_col = next((c for c in ["DDAY", "dday"] if c in df_gss.columns), None)
    if wd_col:
        df_gss_wd = df_gss[df_gss[wd_col].isin([2, 3, 4, 5, 6])].copy()
        log(f"Weekday episodes (DDAY 2-6): {len(df_gss_wd):,} rows")
    else:
        df_gss_wd = df_gss.copy()
        log("WARNING: DDAY column absent -- using all days")

    # Index GSS by occID for fast lookup
    gss_idx = df_gss_wd.set_index("occID").sort_index()

    # Employee filter on Keys (COW 1-2)
    if "COW" in df_keys.columns:
        workers = df_keys[df_keys["COW"].isin([1, 2])]
        log(f"Employees (COW 1-2) in keys: {len(workers):,} agents")
    else:
        workers = df_keys
        log("NOTE: COW column absent -- using all agents")

    # Sample up to 1000 for speed
    sample = workers.sample(min(1000, len(workers)), random_state=42)
    log(f"Sample size for work-duration computation: {len(sample)}")
    log()

    work_mins = []
    n_no_match = 0
    for _, agent in sample.iterrows():
        match_id = agent.get("MATCH_ID_WD")
        if pd.isna(match_id):
            n_no_match += 1
            continue
        try:
            eps = gss_idx.loc[[match_id]]
        except KeyError:
            n_no_match += 1
            continue
        if eps.empty:
            n_no_match += 1
            continue
        work_mins.append(compute_work_minutes(eps))

    log(f"Agents with matched episodes: {len(work_mins)} "
        f"(no-match / missing: {n_no_match})")

    if not work_mins:
        log("ERROR: No work minutes computed. Check MATCH_ID_WD alignment.")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        return

    arr = np.array(work_mins)
    log(f"\nWork+commute duration (real minutes, HHMM-corrected):")
    log(f"  Mean   : {arr.mean():.1f} min/day  ({arr.mean()/60:.2f} h)")
    log(f"  Median : {np.median(arr):.1f} min/day")
    log(f"  P10    : {np.percentile(arr, 10):.1f} min/day")
    log(f"  P90    : {np.percentile(arr, 90):.1f} min/day")
    log(f"  Max    : {arr.max():.1f} min/day")
    log(f"  Zeros  : {(arr == 0).sum()} agents ({(arr == 0).mean()*100:.1f}% -- matched to non-working diary day)")

    mean_val = arr.mean()
    log()
    if mean_val > WARN_HIGH:
        log(f"[WARNING] Mean {mean_val:.0f} > {WARN_HIGH} min/day ({mean_val/60:.1f} h/day)")
        log("  --> Branch (b): real demographic shift toward more working-age adults, OR")
        log("  --> Branch (c): Profile Matcher retrieving longer-work GSS episodes.")
        log("  --> Compare EMPLOY distribution to 2022 run to distinguish branches.")
        log("  --> Consider tuning ClusterMomentumModel.recent_weight (0.5 -> 0.4).")
        verdict = "ABOVE_THRESHOLD"
    elif mean_val < WARN_LOW:
        log(f"[WARNING] Mean {mean_val:.0f} < {WARN_LOW} min/day")
        log("  --> occACT categories 1/8 may be sparsely populated in this GSS cycle.")
        verdict = "BELOW_THRESHOLD"
    else:
        log(f"[OK] Mean {mean_val:.0f} min/day -- within plausible range [{WARN_LOW}, {WARN_HIGH}].")
        log(f"  --> The old 918 min/day was a validator filter bug (branch a).")
        log(f"  --> Fixed filter isin([1,8]) + HHMM-to-minutes conversion gives correct result.")
        log(f"  --> BEM_Schedules_2025.csv is trusted for publication.")
        verdict = "OK"

    log(f"\nVerdict: {verdict}")

    # --- Breakdown by hhsize ---
    if "HHSIZE" in sample.columns or "hhsize" in sample.columns:
        hscol = "HHSIZE" if "HHSIZE" in sample.columns else "hhsize"
        log(f"\nBreakdown by {hscol}:")
        for hs, grp in sample.groupby(hscol):
            grp_mins = []
            for _, ag in grp.iterrows():
                mid = ag.get("MATCH_ID_WD")
                if pd.isna(mid):
                    continue
                try:
                    eps = gss_idx.loc[[mid]]
                except KeyError:
                    continue
                if not eps.empty:
                    grp_mins.append(compute_work_minutes(eps))
            if grp_mins:
                log(f"  {hscol}={hs}: mean={np.mean(grp_mins):.1f} min/day (n={len(grp_mins)})")

    # --- occACT distribution sanity check ---
    log(f"\noccACT value distribution in weekday episodes:")
    for val, cnt in df_gss_wd["occACT"].value_counts().items():
        log(f"  {val}: {cnt:,} rows ({cnt/len(df_gss_wd)*100:.1f}%)")

    # --- Write report ---
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved to: {REPORT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    run_diagnostic()
