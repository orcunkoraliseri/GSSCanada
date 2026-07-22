# -*- coding: utf-8 -*-
"""
3rdJ_03_mergingGSS_4split.py

Step 3 of the Leg-3 (Four-Channel Split: Residential + Office + Retail) Occupancy
Modeling Pipeline: Merge & Tiling.

Ported from:  Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS_2split.py  (Leg-2, verbatim)
Leg-3 deltas (ONLY changes to the Leg-2 version — the retail channel is PURELY
ADDITIVE; every legacy output must remain bit-identical to Leg-2, see Delta D):

  A. Platform-detection path block — repointed so INPUT_DIR still resolves to
     the (read-only, unmodified) Leg-2 Step-2 outputs, but OUTPUT_DIR now
     resolves to this Leg-3 Step3_docs/outputs_step3/. A new LEG2_OUTPUT_DIR
     constant is added, pointing at the Leg-2 Step-3 outputs, used only for
     the Delta D bit-identity hash comparison.

  B. NEW episode-level AT_RETAIL derivation (FROZEN rule, OD-1), added right
     next to the existing AT_WORK derivation, inside tile_work_to_30min's
     sibling tile_retail_to_30min() — the merge phases themselves (A-I) are
     untouched; AT_RETAIL is derived from the already-merged episode columns
     occPRE/occACT at the point of tiling (mirrors how AT_WORK's episode
     column is read at Phase J, not re-derived per Delta C of the runbook):
         AT_RETAIL = ((occPRE == 5) |
                      ((occACT == 4) & occPRE.isin({5, 9}))).astype(float)

  C. NEW Phase K — tile_retail_to_30min(), cloned from tile_work_to_30min()
     (same 4 AM-origin slot math, same binary 1/0 majority vote scheme).
     BINARY_CHANNELS = ["AT_WORK", "AT_RETAIL"] documents both binary channels.
     Emits RETL30_001..RETL30_048 (Int8) + occID -> outputs_step3/retail_30min.csv,
     shape (N, 49), occID order identical to hetus_30min.csv.

  D. NEW Delta-D bit-identity hash gate. After the run, SHA-256 of the 6
     legacy outputs (merged_episodes.csv, merged_episodes.parquet,
     hetus_wide.csv, hetus_30min.csv, copresence_30min.csv, work_30min.csv)
     is computed and compared against the Leg-2 outputs_step3/ copies. ANY
     mismatch = loud FAIL (retail must be purely additive). Parquet is hashed
     first; if a hash mismatch occurs, falls back to column-wise value
     equality and records which comparison was used.

Everything else (Phases A-J, including the Leg-2-delta row-count WARN-not-abort
behaviour) is ported verbatim from Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS_2split.py.

Phases:
    A+B : Column standardization & vertical stacking
    C   : LEFT JOIN (Episode <- Main on occID + CYCLE_YEAR)
    D   : DIARY_VALID filtering
    E   : Temporal feature derivation
    F   : HETUS 144-slot wide format conversion  (residential, bit-identical)
    G   : Export
    H   : Resolution downsampling 144->48  (residential, bit-identical)
    I   : Co-Presence Tiling  (verbatim)
    J   : AT_WORK Tiling  (verbatim, Leg-2 delta)
    K   : AT_RETAIL Tiling  (NEW — Leg-3 delta)
    -   : Delta-D legacy bit-identity hash gate (NEW — Leg-3 delta)

Run locally:
    cd Step3_docs
    py -3 -X utf8 3rdJ_03_mergingGSS_4split.py

WINDOWS ENCODING NOTE:
    Run with  py -3 -X utf8 3rdJ_03_mergingGSS_4split.py
    to avoid cp1252 crashes on UTF-8 console output.
"""

from __future__ import annotations

import hashlib
import os
import platform
from pathlib import Path

import numpy as np
import pandas as pd

# ── Platform-detection path block ─────────────────────────────────────────────
_SYSTEM = platform.system()

if _SYSTEM == "Windows":
    _LEG2_BASE = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split")
    _LEG3_BASE = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split")
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = Path("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split")
    _LEG3_BASE = Path("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split")
else:
    _LEG2_BASE = Path.home() / "GSSCanada" / "GSSCanada-main" / "3J_docs_occ_nTemp" / "Leg2_2-split"
    _LEG3_BASE = Path.home() / "GSSCanada" / "GSSCanada-main" / "3J_docs_occ_nTemp" / "Leg3_4-split"

INPUT_DIR  = _LEG2_BASE / "Step2_docs" / "outputs_step2"      # read-only Leg-2 Step-2 outputs
OUTPUT_DIR = _LEG3_BASE / "Step3_docs" / "outputs_step3"      # Leg-3 Step-3 outputs (this build)
LEG2_OUTPUT_DIR = _LEG2_BASE / "Step3_docs" / "outputs_step3" # read-only Leg-2 Step-3 outputs (Delta D reference)

CYCLES = [2005, 2010, 2015, 2022]

# [Leg-3 delta C] BINARY_CHANNELS — one list entry per binary occupancy channel
# tiled via the majority-vote 1/0 scheme (as opposed to the 1/2 co-presence scheme).
BINARY_CHANNELS = ["AT_WORK", "AT_RETAIL"]   # restaurant (occPRE == 7) = one more entry, if ever

# [Leg-3 delta D] Legacy outputs whose bit-identity to Leg-2 must be preserved.
LEGACY_OUTPUTS = [
    "merged_episodes.csv",
    "merged_episodes.parquet",
    "hetus_wide.csv",
    "hetus_30min.csv",
    "copresence_30min.csv",
    "work_30min.csv",
]

# ── Phase A — Column Definitions ─────────────────────────────────────────────

# Leg-2 delta B: added "NAICS" and "TELEWORK" to MAIN_COMMON_COLS
MAIN_COMMON_COLS = [
    "occID",
    "AGEGRP",
    "SEX",
    "MARSTH",
    "HHSIZE",
    "PR",
    "CMA",
    "WGHT_PER",
    "DDAY",
    "KOL",
    "LFTAG",
    "TOTINC",
    "HRSWRK",
    "MODE",          # commute mode (2010/2015/2022); NaN for 2005
    "ATTSCH",        # school-attendance binary (all cycles)
    "POWST",         # works-from-home binary (all cycles; NaN for non-workers)
    "NOCS",          # 2015/2022 only -> NaN for 2005/2010
    "COW",           # Class of Worker (harmonized 3-category)
    "WKSWRK",        # Weeks worked per year
    "NAICS",         # [Leg-2 delta B] Industry code (harmonized across cycles)
    "TELEWORK",      # [Leg-2 delta B] Telework binary (all 4 cycles; 2005 now via MAR_Q190)
    "WORK_SCHEDULE", # [Leg-2 delta F] Usual work schedule / shift type (1-9; all 4 cycles)
    # Metadata flags
    "TOTINC_SOURCE",
    "CYCLE_YEAR",
    "SURVYEAR",
    "COLLECT_MODE",
    "TUI_10_AVAIL",
    "BS_TYPE",
]

# Leg-2 delta B: added "AT_WORK" to EPISODE_COMMON_COLS (right after AT_HOME)
EPISODE_COMMON_COLS = [
    "occID",
    "EPINO",
    "WGHT_EPI",
    "start",
    "end",
    "duration",
    "occACT_raw",
    "occACT",
    "occACT_label",
    "occPRE_raw",
    "occPRE",
    "AT_HOME",
    "AT_WORK",       # [Leg-2 delta B] Binary flag: occPRE==2
    # Co-presence
    "Alone",
    "Spouse",
    "Children",
    "parents",
    "otherInFAMs",
    "otherHHs",
    "friends",
    "others",
    "colleagues",    # TUI_06I (2015/2022 only) -> NaN for 2005/2010
    # Auxiliary (optional)
    "TUI_07",        # tech use: 2015/2022 only -> NaN for 2005/2010
    # QA flag
    "DIARY_VALID",
    "CYCLE_YEAR",
]

# ── Phase A — Helper: standardize_columns ────────────────────────────────────

def standardize_columns(df: pd.DataFrame, target_cols: list[str]) -> pd.DataFrame:
    """Select target_cols from df, adding NaN columns for any that are missing.

    Args:
        df: Input DataFrame (one cycle's raw harmonized file).
        target_cols: Ordered list of column names to keep.

    Returns:
        DataFrame with exactly the columns in target_cols, in that order.
        Missing columns are filled with pd.NA.
    """
    for col in target_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df[target_cols].copy()


# ── Phase B — Load & Stack ────────────────────────────────────────────────────

def load_and_stack_main(input_dir: Path) -> pd.DataFrame:
    """Load all four harmonized Main files and stack into one DataFrame.

    Applies column standardization (Phase A) to each cycle before stacking.

    Args:
        input_dir: Directory containing main_{year}.csv files.

    Returns:
        Unified Main DataFrame with ~64,713 rows and MAIN_COMMON_COLS columns.
    """
    dfs = []
    for cycle in CYCLES:
        path = input_dir / f"main_{cycle}.csv"
        df = pd.read_csv(path, low_memory=False)
        df = standardize_columns(df, MAIN_COMMON_COLS)
        n = len(df)
        print(f"  main_{cycle}.csv -> {n:>6,} rows | columns: {list(df.columns)[:5]}...")
        dfs.append(df)

    unified = pd.concat(dfs, ignore_index=True)
    print(f"\n  Unified Main: {len(unified):,} rows x {unified.shape[1]} columns")
    return unified


def load_and_stack_episodes(input_dir: Path) -> pd.DataFrame:
    """Load all four harmonized Episode files and stack into one DataFrame.

    Applies column standardization (Phase A) to each cycle before stacking.

    Args:
        input_dir: Directory containing episode_{year}.csv files.

    Returns:
        Unified Episode DataFrame with ~1.06M rows and EPISODE_COMMON_COLS columns.
    """
    dfs = []
    for cycle in CYCLES:
        path = input_dir / f"episode_{cycle}.csv"
        df = pd.read_csv(path, low_memory=False)
        df = standardize_columns(df, EPISODE_COMMON_COLS)
        n = len(df)
        print(f"  episode_{cycle}.csv -> {n:>8,} rows | columns: {list(df.columns)[:5]}...")
        dfs.append(df)

    unified = pd.concat(dfs, ignore_index=True)
    print(f"\n  Unified Episodes: {len(unified):,} rows x {unified.shape[1]} columns")
    return unified


def check_stack_integrity(unified_main: pd.DataFrame, unified_episode: pd.DataFrame) -> None:
    """Run post-stack integrity checks and print results.

    Checks:
        - No duplicate (occID, CYCLE_YEAR) pairs in unified Main.
        - Episode row counts per cycle match expected values.

    Args:
        unified_main: Stacked Main DataFrame.
        unified_episode: Stacked Episode DataFrame.
    """
    print("\n-- Stack integrity checks ------------------------------------------")

    # Check 1: No duplicate respondents in unified Main
    dupes = unified_main.duplicated(subset=["occID", "CYCLE_YEAR"]).sum()
    status = "PASS" if dupes == 0 else "FAIL"
    print(f"  [{status}] Duplicate (occID, CYCLE_YEAR) in Main: {dupes}")

    # Check 2: Per-cycle episode counts
    print("\n  Episode counts per cycle:")
    for cycle, count in unified_episode.groupby("CYCLE_YEAR").size().items():
        print(f"    {cycle}: {count:>8,}")

    # Check 3: Per-cycle respondent counts in Main
    print("\n  Respondent counts per cycle (Main):")
    for cycle, count in unified_main.groupby("CYCLE_YEAR").size().items():
        print(f"    {cycle}: {count:>6,}")


# ── Phase C — LEFT JOIN ───────────────────────────────────────────────────────

def merge_main_episode(
    unified_main: pd.DataFrame, unified_episode: pd.DataFrame
) -> pd.DataFrame:
    """LEFT JOIN Episode <- Main on (occID, CYCLE_YEAR).

    Each episode row carries the respondent's full demographic profile.
    Join key is composite because occIDs are only unique within a cycle.

    Args:
        unified_main: Stacked Main DataFrame.
        unified_episode: Stacked Episode DataFrame.

    Returns:
        Merged DataFrame; same row count as unified_episode.
    """
    print("\n-- Phase C: LEFT JOIN ----------------------------------------------")
    n_before = len(unified_episode)

    merged = unified_episode.merge(
        unified_main,
        on=["occID", "CYCLE_YEAR"],
        how="left",
        validate="many_to_one",
    )

    n_after = len(merged)
    assert n_after == n_before, (
        f"Row count changed after merge: {n_before} -> {n_after}"
    )

    orphans = merged["WGHT_PER"].isna().sum()
    status = "PASS" if orphans == 0 else "FAIL"
    print(f"  [{status}] Orphan episodes (no Main match): {orphans}")
    print(f"  Merged: {n_after:,} rows x {merged.shape[1]} columns")
    return merged


# ── Phase D — DIARY_VALID Filtering ──────────────────────────────────────────

def filter_invalid_diaries(merged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Remove respondents whose diary does not sum to 1440 minutes.

    Args:
        merged: Merged episode-level DataFrame.

    Returns:
        Tuple of (valid_merged, exclusion_log):
            valid_merged   : Episodes for respondents with DIARY_VALID == 1.
            exclusion_log  : DataFrame summarising excluded counts per cycle.
    """
    print("\n-- Phase D: DIARY_VALID Filtering ----------------------------------")

    rows: list[dict] = []
    for cycle in CYCLES:
        cycle_df = merged[merged["CYCLE_YEAR"] == cycle]
        valid_ids = cycle_df.loc[cycle_df["DIARY_VALID"] == 1, "occID"].unique()
        total_ids = cycle_df["occID"].nunique()
        excluded = total_ids - len(valid_ids)
        rate = excluded / total_ids * 100 if total_ids > 0 else 0.0
        rows.append(
            {
                "CYCLE_YEAR": cycle,
                "total_respondents": total_ids,
                "excluded": excluded,
                "exclusion_rate_%": round(rate, 2),
            }
        )
        print(
            f"  {cycle}: {total_ids:>6,} respondents -> {excluded:>4} excluded "
            f"({rate:.2f}%)"
        )

    exclusion_log = pd.DataFrame(rows)

    valid_merged = merged[merged["DIARY_VALID"] == 1].copy()
    n_respondents = valid_merged.groupby(["occID", "CYCLE_YEAR"]).ngroups
    print(
        f"\n  Post-filter: {n_respondents:,} respondents | "
        f"{len(valid_merged):,} episodes"
    )
    return valid_merged, exclusion_log


# ── Phase E — Temporal Feature Derivation ─────────────────────────────────────

# DDAY Encoding to 3-category stratum ({1=Weekday, 2=Saturday, 3=Sunday})
# 2005/2010/2015 already use this in DDAY. 2022 uses 1=Sunday...7=Saturday.
_DDAY_STRATAMAP_2022: dict[int, int] = {
    1: 3,  # Sunday   -> 3
    2: 1,  # Monday   -> 1
    3: 1,  # Tuesday  -> 1
    4: 1,  # Wednesday-> 1
    5: 1,  # Thursday -> 1
    6: 1,  # Friday   -> 1
    7: 2,  # Saturday -> 2
}

_DAYTYPE_MAP: dict[int, str] = {
    1: "Weekday",
    2: "Weekend",  # Saturday
    3: "Weekend",  # Sunday
}


def _parse_hhmm_to_minutes(hhmm: pd.Series) -> pd.Series:
    """Convert HHMM integer series to minutes from midnight (0-1439).

    Args:
        hhmm: Series of HHMM integers (e.g. 400 -> 4:00 AM, 1330 -> 1:30 PM).

    Returns:
        Series of integer minutes from midnight.
    """
    hhmm = hhmm.fillna(0).astype(int)
    return (hhmm // 100) * 60 + (hhmm % 100)


def _hhmm_to_hetus_slot(hhmm: pd.Series) -> pd.Series:
    """Convert HHMM series to HETUS slot index (1-144), 4:00 AM origin.

    HETUS slot 1 = 04:00-04:09, slot 144 = 03:50-03:59 next day.

    Args:
        hhmm: Series of HHMM integers.

    Returns:
        Series of integer slot indices (1-144).
    """
    total_min = _parse_hhmm_to_minutes(hhmm)
    shifted = (total_min - 240) % 1440   # shift 4 AM -> 0
    return (shifted // 10 + 1).astype(int)


def derive_temporal_features(merged: pd.DataFrame) -> pd.DataFrame:
    """Derive DAYTYPE, HOUR_OF_DAY, TIMESLOT_10, and DDAY_STRATA columns.

    Args:
        merged: Filtered merged DataFrame (DIARY_VALID == 1 only).

    Returns:
        DataFrame with five new columns appended.
    """
    print("\n-- Phase E: Temporal Feature Derivation ----------------------------")

    df = merged.copy()

    # DDAY_STRATA: 3-category day-of-week stratum (1=Weekday, 2=Saturday, 3=Sunday)
    # 2005/2010/2015 already hold this logic in DDAY. 2022 holds 1-7 and must be mapped.
    mask_2022 = df["CYCLE_YEAR"] == 2022
    df["DDAY_STRATA"] = df["DDAY"].astype(int)
    df.loc[mask_2022, "DDAY_STRATA"] = df.loc[mask_2022, "DDAY"].map(_DDAY_STRATAMAP_2022)

    # DAYTYPE: Weekday / Weekend derived from the 3-category DDAY_STRATA
    df["DAYTYPE"] = df["DDAY_STRATA"].map(_DAYTYPE_MAP)

    # Minutes from midnight for episode start
    df["startMin"] = _parse_hhmm_to_minutes(df["start"])
    df["endMin"] = _parse_hhmm_to_minutes(df["end"])

    # HOUR_OF_DAY (0-23)
    df["HOUR_OF_DAY"] = (df["startMin"] // 60).astype(int)

    # TIMESLOT_10: HETUS 10-min slot (1-144, 4 AM origin)
    df["TIMESLOT_10"] = _hhmm_to_hetus_slot(df["start"])

    derived_cols = ["DAYTYPE", "startMin", "endMin", "HOUR_OF_DAY", "TIMESLOT_10", "DDAY_STRATA"]
    print(f"  Derived columns added: {derived_cols}")
    for col in derived_cols:
        print(f"    {col}: {df[col].nunique()} unique values, "
              f"{df[col].isna().sum()} NaN")

    return df


# ── Phase F — HETUS 144-Slot Wide Format Conversion ──────────────────────────
# [Leg-2 delta C] Residential Phase F is BIT-IDENTICAL to Leg 1.
# AT_WORK is NOT added here — it stays episode-level for the Phase J tiler.
# Leg-2 delta B adds NAICS/TELEWORK to PERSON_COLS for model conditioning.

def _build_slot_arrays(
    group: pd.DataFrame,
) -> tuple[dict[str, int], dict[str, int]]:
    """Convert one respondent's episodes to two 144-element slot dicts.

    Slot assignment uses start time (shifted to 4:00 AM origin) combined with
    episode duration to compute the slot range.  This avoids double-wrap errors
    for episodes that cross midnight AND the 4:00 AM diary boundary.

    Args:
        group: Episodes for a single (occID, CYCLE_YEAR), sorted by EPINO.

    Returns:
        Tuple of (act_slots, home_slots):
            act_slots  : {slot_001: occACT, ..., slot_144: occACT}
            home_slots : {home_001: AT_HOME, ..., home_144: AT_HOME}
    """
    act_slots: dict[str, int] = {}
    home_slots: dict[str, int] = {}

    for _, ep in group.iterrows():
        start_hhmm = int(ep["start"]) if pd.notna(ep["start"]) else 0
        dur = int(ep["duration"]) if pd.notna(ep["duration"]) else 0
        act = ep["occACT"]
        home = ep["AT_HOME"]

        start_min = (start_hhmm // 100) * 60 + (start_hhmm % 100)

        # Shift start to 4:00 AM origin (HETUS standard)
        start_shifted = (start_min - 240) % 1440

        # Compute end using duration -- avoids double-wrap errors.
        # Cap at 1440 (diary ends at 3:59 AM next day).
        end_shifted = min(start_shifted + dur, 1440)

        # Assign activity to each 10-min slot covered (0-indexed internally)
        slot_start = start_shifted // 10
        slot_end = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0

        for s in range(slot_start, min(slot_end, 144)):
            key_act = f"slot_{s + 1:03d}"
            key_home = f"home_{s + 1:03d}"
            act_slots[key_act] = act
            home_slots[key_home] = home

    return act_slots, home_slots


def build_hetus_wide(merged: pd.DataFrame) -> pd.DataFrame:
    """Convert episode-level data to HETUS 144-slot wide format.

    One row per respondent containing:
        - slot_001 ... slot_144  : occACT activity code per 10-min slot
        - home_001 ... home_144  : AT_HOME binary flag per 10-min slot
        - Person-level demographic & temporal columns

    [Leg-2 delta B] PERSON_COLS now includes NAICS and TELEWORK for model
    conditioning (NOCS and COW were already present in Leg 1).
    AT_WORK is NOT tiled here — that is Phase J.

    Args:
        merged: Filtered, feature-enriched merged DataFrame.

    Returns:
        Wide-format DataFrame with one row per (occID, CYCLE_YEAR).
    """
    print("\n-- Phase F: HETUS 144-Slot Conversion ------------------------------")

    SLOT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
    HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]

    # [Leg-2 delta B] NAICS and TELEWORK added to PERSON_COLS
    PERSON_COLS = [
        "occID", "CYCLE_YEAR", "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR",
        "CMA", "WGHT_PER", "DDAY", "KOL", "LFTAG", "TOTINC", "HRSWRK",
        "MODE", "ATTSCH", "POWST",
        "NOCS", "COW", "WKSWRK", "NAICS", "TELEWORK", "WORK_SCHEDULE",  # Leg-2 additions
        "TOTINC_SOURCE", "SURVYEAR",
        "COLLECT_MODE", "TUI_10_AVAIL", "BS_TYPE",
        "DAYTYPE", "DDAY_STRATA",
    ]

    n_respondents = merged.groupby(["occID", "CYCLE_YEAR"]).ngroups
    print(f"  Building {n_respondents:,} respondent rows ...")

    # Pre-allocate arrays for speed
    act_array = np.full((n_respondents, 144), np.nan)
    home_array = np.full((n_respondents, 144), np.nan)
    person_records: list[dict] = []

    idx = 0
    groups = merged.sort_values("EPINO").groupby(["occID", "CYCLE_YEAR"], sort=False)
    for (occ_id, cycle), group in groups:
        act_slots, home_slots = _build_slot_arrays(group)

        for col, val in act_slots.items():
            s = int(col.split("_")[1]) - 1   # 0-indexed
            act_array[idx, s] = val

        for col, val in home_slots.items():
            s = int(col.split("_")[1]) - 1
            home_array[idx, s] = val

        # Take person-level attributes from first episode row
        person_row = group.iloc[0]
        rec = {c: person_row[c] for c in PERSON_COLS if c in person_row.index}
        person_records.append(rec)
        idx += 1

    # Forward-fill NaN slots within each respondent row
    df_act = pd.DataFrame(act_array, columns=SLOT_COLS)
    df_home = pd.DataFrame(home_array, columns=HOME_COLS)

    n_before = df_act.isna().any(axis=1).sum()
    df_act = df_act.ffill(axis=1).bfill(axis=1)
    df_home = df_home.ffill(axis=1).bfill(axis=1)
    n_after = df_act.isna().any(axis=1).sum()
    print(f"  NaN-slot respondents before ffill: {n_before}, after: {n_after}")

    df_person = pd.DataFrame(person_records)

    hetus_wide = pd.concat(
        [df_person.reset_index(drop=True),
         df_act.reset_index(drop=True),
         df_home.reset_index(drop=True)],
        axis=1,
    )

    print(f"  Done: {hetus_wide.shape[0]:,} rows x {hetus_wide.shape[1]} columns")
    return hetus_wide


# ── Phase G — Export ──────────────────────────────────────────────────────────

def export_all(
    merged: pd.DataFrame,
    hetus_wide: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Export Step 3 outputs to disk.

    Outputs:
        merged_episodes.csv     : Full episode-level dataset with derived features.
        merged_episodes.parquet : Same, in Parquet format for efficient downstream use.
        hetus_wide.csv          : 144-slot wide format (one row per respondent).

    Args:
        merged: Filtered, feature-enriched merged episode DataFrame.
        hetus_wide: HETUS wide-format DataFrame.
        output_dir: Directory to write outputs.
    """
    print("\n-- Phase G: Export --------------------------------------------------")
    output_dir.mkdir(parents=True, exist_ok=True)

    path_csv = output_dir / "merged_episodes.csv"
    path_pq = output_dir / "merged_episodes.parquet"
    path_hetus = output_dir / "hetus_wide.csv"

    print(f"  Writing {path_csv} ...")
    merged.to_csv(path_csv, index=False)

    print(f"  Writing {path_pq} ...")
    merged.to_parquet(path_pq, index=False)

    print(f"  Writing {path_hetus} ...")
    hetus_wide.to_csv(path_hetus, index=False)

    print("\n  Export complete.")
    print(f"    merged_episodes.csv     : {path_csv.stat().st_size / 1e6:.1f} MB")
    print(f"    merged_episodes.parquet : {path_pq.stat().st_size / 1e6:.1f} MB")
    print(f"    hetus_wide.csv          : {path_hetus.stat().st_size / 1e6:.1f} MB")


# BEM priority order for 3-way tie resolution (lower rank = higher priority).
BEM_PRIORITY: dict[int, int] = {
    5: 1,   # Sleep & Naps & Resting
    7: 2,   # Personal Care
    1: 3,   # Work & Related
    8: 4,   # Education
    2: 5,   # Household Work & Maintenance
    3: 6,   # Caregiving & Help
    6: 7,   # Eating & Drinking
    9: 8,   # Socializing
    10: 9,  # Passive Leisure
    11: 10, # Active Leisure
    12: 11, # Community & Volunteer
    4: 12,  # Purchasing Goods & Services
    13: 13, # Travel
    14: 14, # Miscellaneous / Idle
}


def _nanmode_axis2(arr3d: np.ndarray) -> np.ndarray:
    """Compute mode across axis=2 of a (n, 48, 3) array, ignoring NaNs.

    Returns:
        (n, 48) array. Value is the mode if a strict majority exists (count >= 2).
        np.nan sentinel if all 3 values are distinct (3-way tie) or all NaN.
    """
    n, m, k = arr3d.shape  # k == 3
    result = np.full((n, m), np.nan)

    for j in range(m):
        window = arr3d[:, j, :]  # shape (n, 3)
        for i in range(n):
            vals = window[i]
            non_nan = vals[~np.isnan(vals)]
            if len(non_nan) == 0:
                result[i, j] = np.nan  # all NaN
                continue
            unique, counts = np.unique(non_nan, return_counts=True)
            max_count = counts.max()
            if max_count >= 2:
                result[i, j] = unique[counts.argmax()]  # strict majority
            else:
                result[i, j] = np.nan  # 3-way tie sentinel
    return result


# ── Phase H — Resolution Downsampling (144-slot -> 48-slot) ──────────────────
# [Leg-2 delta C] BIT-IDENTICAL to Leg 1 — AT_WORK not touched here.

def downsample_to_30min(hetus_wide_df: pd.DataFrame, output_dir: Path, n_expected: int) -> tuple:
    """Downsample HETUS 144-slot (10-min) format to 48-slot (30-min) format.

    Each 30-min slot is the majority vote of 3 consecutive 10-min source slots.
    AT_HOME uses binary majority (nansum >= 2). Activity ties use BEM priority.

    [Leg-2 delta D] Row count assertion uses dynamically captured n_expected
    instead of the hardcoded 64,061.

    Args:
        hetus_wide_df: DataFrame from hetus_wide.csv.
        output_dir: Directory for output files.
        n_expected: Expected row count (captured from hetus_wide).

    Returns:
        Tuple of (hetus_30min DataFrame, n_ties int).
    """
    print("\n-- Phase H: Resolution Downsampling 144->48 slots ------------------")
    input_path = output_dir / "hetus_wide.csv"
    df = pd.read_csv(input_path, low_memory=False)
    print(f"  Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # [Leg-2 delta D] Dynamic row count check
    n = df.shape[0]
    if n != n_expected:
        print(f"  [WARNING] Expected {n_expected:,} rows (Leg-1 = 64,061), got {n:,}!")
    if n != 64_061:
        print(f"  [WARNING] Row count {n:,} differs from expected Leg-1 baseline 64,061!")
    else:
        print(f"  Row count {n:,} matches expected 64,061 (Leg-1 baseline).")

    # H.1b: Separate identity columns from slot columns
    SLOT_ACT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
    SLOT_HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]
    META_COLS = [c for c in df.columns if c not in SLOT_ACT_COLS + SLOT_HOME_COLS]

    print(f"  Activity slot cols : {len(SLOT_ACT_COLS)}")   # expect 144
    print(f"  AT_HOME slot cols  : {len(SLOT_HOME_COLS)}")   # expect 144
    print(f"  Meta/identity cols : {len(META_COLS)}")

    # H.1c: Extract activity matrix as numpy array
    act_arr = df[SLOT_ACT_COLS].to_numpy(dtype=float)
    print(f"  Activity matrix shape: {act_arr.shape}")

    # H.1d: Extract AT_HOME matrix as numpy array
    hom_arr = df[SLOT_HOME_COLS].to_numpy(dtype=float)
    print(f"  AT_HOME matrix shape: {hom_arr.shape}")

    # H.2a: Reshape activity array to (n x 48 x 3)
    act_3d = act_arr.reshape(n, 48, 3)
    print(f"  Activity 3D shape: {act_3d.shape}")

    # H.2c: Apply nanmode to get act_30 with tie sentinels
    print("  Computing activity majority vote (may take ~1 min)...")
    act_30 = _nanmode_axis2(act_3d)
    n_ties = int(np.isnan(act_30).sum())
    print(f"  3-way ties detected: {n_ties:,} ({100*n_ties/(n*48):.2f}% of all cells)")

    # H.3a: Reshape AT_HOME array to (n x 48 x 3)
    hom_3d = hom_arr.reshape(n, 48, 3)
    print(f"  AT_HOME 3D shape: {hom_3d.shape}")

    # H.3b: Compute AT_HOME binary majority vote
    valid_count = np.sum(~np.isnan(hom_3d), axis=2)
    sum_home = np.nansum(hom_3d, axis=2)

    hom_30 = np.where(valid_count == 0, np.nan,
                      np.where(sum_home >= 2, 1.0, 0.0))

    n_home_nan = int(np.isnan(hom_30).sum())
    print(f"  AT_HOME NaNs after vote: {n_home_nan}")

    # H.4a: Detect 3-way tie positions
    tie_mask = np.isnan(act_30)
    tie_positions = list(zip(*np.where(tie_mask)))
    print(f"  Tie positions to resolve: {len(tie_positions):,}")

    # H.4b: Resolve ties using BEM priority order
    for (i, j) in tie_positions:
        source_vals = act_3d[i, j, :]
        non_nan_vals = source_vals[~np.isnan(source_vals)]
        best_code = min(non_nan_vals, key=lambda v: BEM_PRIORITY.get(int(v), 999))
        act_30[i, j] = best_code

    # Confirm all ties resolved
    remaining_nan = int(np.isnan(act_30).sum())
    assert remaining_nan == 0, f"Still {remaining_nan} NaN in act_30 after tie resolution"
    print(f"  Ties resolved: {len(tie_positions):,} | Remaining NaN: {remaining_nan}")

    # H.5a: Build act30 DataFrame with Int16 dtype
    act30_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    act30_df = pd.DataFrame(act_30, columns=act30_cols).astype(pd.Int16Dtype())
    print(f"  act30_df shape: {act30_df.shape}")

    # H.5b: Build hom30 DataFrame with Int8 dtype
    hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    hom30_df = pd.DataFrame(hom_30, columns=hom30_cols).astype(pd.Int8Dtype())
    print(f"  hom30_df shape: {hom30_df.shape}")

    # H.5c: Concatenate meta + act30 + hom30
    hetus_30min = pd.concat(
        [df[META_COLS].reset_index(drop=True), act30_df, hom30_df],
        axis=1
    )
    print(f"  hetus_30min shape: {hetus_30min.shape}")

    # H.6a: Write hetus_30min.csv
    output_path = output_dir / "hetus_30min.csv"
    print(f"\n  Writing {output_path} ...")
    hetus_30min.to_csv(output_path, index=False)
    size_mb = output_path.stat().st_size / 1e6
    print(f"  Done. File size: {size_mb:.1f} MB")
    return hetus_30min, n_ties


def validate_30min(hetus_30min: pd.DataFrame, n_ties: int, output_dir: Path, n_expected: int) -> None:
    """Implement validation checks V1-V8 for the 30-min downsampled data.

    [Leg-2 delta D] Uses n_expected instead of hardcoded 64_061.

    Args:
        hetus_30min: Downsampled DataFrame.
        n_ties: Count of 3-way ties encountered during activity processing.
        output_dir: Output directory for reading reference files.
        n_expected: Expected row count.
    """
    import random
    print("\n-- Phase H Validation (V1-V8) ----------------------------------------")

    n = hetus_30min.shape[0]

    # V1 — Shape check
    if n != n_expected:
        print(f"V1 WARN -- Row count {n:,} != expected {n_expected:,}")
    else:
        print(f"V1 PASS -- shape ({n:,}, ... act/home cols)")

    act30_cols = [c for c in hetus_30min.columns if c.startswith("act30_")]
    hom30_cols = [c for c in hetus_30min.columns if c.startswith("hom30_")]
    assert len(act30_cols) == 48, f"Expected 48 act30 cols, got {len(act30_cols)}"
    assert len(hom30_cols) == 48, f"Expected 48 hom30 cols, got {len(hom30_cols)}"

    # V2 — Zero NaN in act30 and hom30
    nan_act = hetus_30min[act30_cols].isna().sum().sum()
    nan_hom = hetus_30min[hom30_cols].isna().sum().sum()
    assert nan_act == 0, f"NaN in act30: {nan_act}"
    assert nan_hom == 0, f"NaN in hom30: {nan_hom}"
    print(f"V2 PASS -- NaN act30={nan_act}, hom30={nan_hom}")

    # V3 — Activity distribution vs hetus_wide within +-1 pp
    hetus_wide = pd.read_csv(output_dir / "hetus_wide.csv", low_memory=False)
    slot_cols = [f"slot_{i:03d}" for i in range(1, 145)]
    wide_vals = hetus_wide[slot_cols].to_numpy().flatten()
    new_vals = hetus_30min[act30_cols].to_numpy().flatten()

    print("\nV3 -- Activity distribution comparison:")
    print(f"  {'Code':>6} | {'hetus_wide%':>12} | {'hetus_30min%':>12} | {'diff_pp':>8} | Status")
    all_pass = True
    for code in sorted(pd.Series(wide_vals).dropna().unique()):
        pct_wide = 100 * (wide_vals == code).mean()
        pct_new = 100 * (new_vals == code).mean()
        diff = abs(pct_wide - pct_new)
        status = "PASS" if diff <= 1.0 else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  {int(code):>6} | {pct_wide:>11.2f}% | {pct_new:>11.2f}% | {diff:>7.2f}pp | {status}")
    print(f"V3 {'PASS' if all_pass else 'FAIL'} -- all categories within +-1 pp: {all_pass}")

    # V4 — Weighted AT_HOME rate per cycle within +-1 pp
    hom30_cols2 = [f"hom30_{i:03d}" for i in range(1, 49)]
    hom144_cols = [f"home_{i:03d}" for i in range(1, 145)]
    print("\nV4 -- Weighted AT_HOME rate preservation vs hetus_wide:")
    print(f"  {'Cycle':>6} | {'wide%':>10} | {'30min%':>10} | {'diff_pp':>8} | Status")
    all_pass_v4 = True
    for cycle in sorted(hetus_30min["CYCLE_YEAR"].unique()):
        mask_30 = hetus_30min["CYCLE_YEAR"] == cycle
        sub_30 = hetus_30min[mask_30]
        w_30 = sub_30["WGHT_PER"]
        home_30_vals = sub_30[hom30_cols2].to_numpy(dtype=float)
        wtd_rate_30 = 100 * np.average(home_30_vals.flatten(), weights=np.repeat(w_30.values, 48))

        mask_w = hetus_wide["CYCLE_YEAR"] == cycle
        sub_w = hetus_wide[mask_w]
        w_w = sub_w["WGHT_PER"]
        home_w_vals = sub_w[hom144_cols].to_numpy(dtype=float)
        wtd_rate_w = 100 * np.average(home_w_vals.flatten(), weights=np.repeat(w_w.values, 144))

        diff = abs(wtd_rate_30 - wtd_rate_w)
        status = "PASS" if diff <= 1.0 else "FAIL"
        if status == "FAIL":
            all_pass_v4 = False
        print(f"  {cycle:>6} | {wtd_rate_w:>9.1f}% | {wtd_rate_30:>9.2f}% | {diff:>7.2f}pp | {status}")
    print(f"V4 {'PASS' if all_pass_v4 else 'FAIL'} -- AT_HOME rates within +-1 pp vs wide: {all_pass_v4}")

    # V5 — Night slot plausibility (slots 1-8: 04:00-07:59 AM)
    sleep_code = [k for k, v in BEM_PRIORITY.items() if v == 1][0]
    night_act_cols = [f"act30_{i:03d}" for i in range(1, 9)]
    night_hom_cols = [f"hom30_{i:03d}" for i in range(1, 9)]
    night_act_vals = hetus_30min[night_act_cols].to_numpy().flatten()
    night_hom_vals = hetus_30min[night_hom_cols].to_numpy(dtype=float).flatten()
    sleep_pct = 100 * (night_act_vals == sleep_code).mean()
    athome_pct = 100 * np.nanmean(night_hom_vals)

    print(f"\nV5 -- Night slots (1-8, 04:00-07:59):")
    print(f"  Sleep rate  : {sleep_pct:.1f}%  (threshold >= 70%)  -> {'PASS' if sleep_pct >= 70 else 'FAIL'}")
    print(f"  AT_HOME rate: {athome_pct:.1f}% (threshold >= 85%)  -> {'PASS' if athome_pct >= 85 else 'FAIL'}")

    # V6 — 3-way tie rate < 5%
    total_cells = n * 48
    tie_rate_pct = 100 * n_ties / total_cells
    print(f"\nV6 -- 3-way tie rate: {n_ties:,} / {total_cells:,} = {tie_rate_pct:.2f}%")
    assert tie_rate_pct < 5.0, f"Tie rate {tie_rate_pct:.2f}% exceeds 5% threshold"
    print(f"V6 PASS -- tie rate < 5%")

    # V7 — DDAY_STRATA distribution unchanged
    dist_wide = hetus_wide["DDAY_STRATA"].value_counts().sort_index()
    dist_30 = hetus_30min["DDAY_STRATA"].value_counts().sort_index()
    match = dist_wide.equals(dist_30)
    print(f"\nV7 -- DDAY_STRATA distribution match: {'PASS' if match else 'FAIL'}")

    # V8 — Manual spot-check 5 random respondents
    random.seed(42)
    sample_indices = random.sample(range(n), 5)
    print("\nV8 -- Manual spot-check (5 random respondents, first 6 slots shown):")
    for idx in sample_indices:
        occ_id = hetus_30min.iloc[idx]["occID"]
        print(f"\n  occID={occ_id} (row {idx})")
        print(f"  {'30min_slot':>12} | {'src_A':>6} | {'src_B':>6} | {'src_C':>6} | {'act30':>6} | {'hom30':>6}")
        for s in range(1, 7):
            src_a = hetus_wide.iloc[idx][f"slot_{3*(s-1)+1:03d}"]
            src_b = hetus_wide.iloc[idx][f"slot_{3*(s-1)+2:03d}"]
            src_c = hetus_wide.iloc[idx][f"slot_{3*s:03d}"]
            act30_val = hetus_30min.iloc[idx][f"act30_{s:03d}"]
            hom30_val = hetus_30min.iloc[idx][f"hom30_{s:03d}"]
            print(f"  act30_{s:03d}    | {src_a!s:>6} | {src_b!s:>6} | {src_c!s:>6} | {act30_val!s:>6} | {hom30_val!s:>6}")
    print("\nV8 Selection Complete.")


# ── Phase I — Co-Presence Tiling (episode -> 48-slot 30-min format) ──────────
# [Leg-2 delta C/D] Verbatim from Leg 1 with:
# - Path("outputs_step3") replaced with output_dir parameter
# - Dynamic n_expected instead of hardcoded 64_061

COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues"
]

def tile_copresence_to_30min(output_dir: Path, n_expected: int) -> pd.DataFrame:
    """Tile episode-level co-presence columns to 30-min slot wide format.

    Reads merged_episodes.csv and hetus_30min.csv (for occID order).
    Applies the same two-stage tiling as Phase F+H: episode -> 144-slot 10-min
    intermediate -> 48-slot 30-min via binary majority vote.

    [Leg-2 delta D] Uses n_expected instead of hardcoded 64_061.

    Returns:
        DataFrame: N rows x 433 cols (occID + 9x48 co-presence slots).
        Values: 1=present, 2=absent, pd.NA for NaN slots.
        Output: outputs_step3/copresence_30min.csv
    """
    print("\n-- Phase I: Co-Presence Tiling (episode -> 30-min slots) ------------")
    ep_path = output_dir / "merged_episodes.csv"
    episodes = pd.read_csv(ep_path, low_memory=False)
    print(f"  Loaded: {len(episodes):,} episode rows")

    # Verify required columns
    required_cols = ["occID", "startMin", "endMin", "CYCLE_YEAR"] + COP_COLS
    missing = [c for c in required_cols if c not in episodes.columns]
    assert not missing, f"Missing columns: {missing}"

    n_unique_occ = episodes.groupby(["occID", "CYCLE_YEAR"]).ngroups
    print(f"  Unique (occID, CYCLE_YEAR) in episodes: {n_unique_occ:,}")

    ref_path = output_dir / "hetus_30min.csv"
    ref_df = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    occid_order = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
    occid_to_idx = {oid_cyc: i for i, oid_cyc in enumerate(occid_order)}
    n = len(occid_order)
    print(f"  Reference order loaded: {n:,} respondents")

    if n != n_expected:
        print(f"  [WARNING] Expected {n_expected:,}, got {n:,}!")

    # One float64 array per co-presence column
    cop_10min = {col: np.full((n, 144), np.nan, dtype=float) for col in COP_COLS}
    print(f"  Pre-allocated 9 arrays of shape ({n}, 144)")

    episodes_sorted = episodes.sort_values(["CYCLE_YEAR", "occID"]).reset_index(drop=True)

    grp = episodes_sorted.groupby(["occID", "CYCLE_YEAR"], sort=False)
    grp_indices = {k: (grp.indices[k].min(), grp.indices[k].max() + 1)
                   for k in grp.groups}
    print(f"  Episode group index built for {len(grp_indices):,} respondents")

    start_mins   = episodes_sorted["startMin"].to_numpy(dtype=float)
    durations    = episodes_sorted["duration"].to_numpy(dtype=float)
    cop_vals     = {col: episodes_sorted[col].to_numpy(dtype=float) for col in COP_COLS}

    print("  Tiling episodes to 10-min slots...")
    for resp_idx, key in enumerate(occid_order):
        if resp_idx > 0 and resp_idx % 10_000 == 0:
            print(f"    {resp_idx:,} / {n:,}")
        if key not in grp_indices:
            continue
        row_start, row_end = grp_indices[key]
        for ep_row in range(row_start, row_end):
            s_min = start_mins[ep_row]
            dur = durations[ep_row]

            start_shifted = (int(s_min) - 240) % 1440
            end_shifted = min(start_shifted + int(dur), 1440)

            slot_s = start_shifted // 10
            slot_e = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0
            slot_e = min(slot_e, 144)

            for col in COP_COLS:
                val = cop_vals[col][ep_row]
                if not np.isnan(val):
                    cop_10min[col][resp_idx, slot_s:slot_e] = val

    print("  Tiling complete.")

    cop_3d = {}
    for col in COP_COLS:
        cop_3d[col] = cop_10min[col].reshape(n, 48, 3)
        assert cop_3d[col].shape == (n, 48, 3), f"Reshape failed for {col}"
    print(f"  Reshaped all 9 arrays to ({n}, 48, 3)")

    cop_30 = {}
    for col in COP_COLS:
        arr = cop_3d[col]
        valid_count = np.sum(~np.isnan(arr), axis=2)
        sum_present = np.nansum(arr == 1.0, axis=2).astype(float)

        result = np.where(valid_count == 0, np.nan,
                 np.where(sum_present >= 2, 1.0, 2.0))
        cop_30[col] = result

        nan_count = int(np.isnan(result).sum())
        print(f"  {col}: NaN slots = {nan_count:,} ({100*nan_count/(n*48):.2f}%)")

    cop30_dfs = []
    for col in COP_COLS:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        df_col = pd.DataFrame(cop_30[col], columns=slot_cols)
        for c in slot_cols:
            df_col[c] = df_col[c].astype(pd.Int8Dtype())
        cop30_dfs.append(df_col)
        print(f"  {col}: built DataFrame {df_col.shape}")

    occid_col = pd.DataFrame({"occID": [k[0] for k in occid_order]})
    copresence_30min = pd.concat([occid_col] + cop30_dfs, axis=1)
    print(f"  copresence_30min shape: {copresence_30min.shape}")
    expected_cols = 1 + 9 * 48  # 433
    assert copresence_30min.shape == (n, expected_cols), (
        f"Shape mismatch: {copresence_30min.shape} (expected ({n}, {expected_cols}))"
    )

    out_path = output_dir / "copresence_30min.csv"
    print(f"\n  Writing {out_path} ...")
    copresence_30min.to_csv(out_path, index=False)
    size_mb = out_path.stat().st_size / 1e6
    print(f"  Done. File size: {size_mb:.1f} MB")
    return copresence_30min


def validate_copresence_30min_export(
    copresence_30min: pd.DataFrame, occid_order: list, output_dir: Path, n_expected: int
) -> None:
    """[Leg-2 delta D] Verbatim from Leg 1 with dynamic n_expected."""
    print("\n-- Phase I Validation (VI-1-7) ----------------------------------------")

    n = n_expected

    # VI-1: Shape check
    if copresence_30min.shape[0] != n:
        print(f"VI-1 WARN -- Row count {copresence_30min.shape[0]:,} != expected {n:,}")
    else:
        print(f"VI-1 PASS -- shape ({n}, {copresence_30min.shape[1]})")

    expected_cols = 1 + 9 * 48
    assert copresence_30min.shape[1] == expected_cols, (
        f"Col count: {copresence_30min.shape[1]}, expected {expected_cols}"
    )

    # VI-2: occID alignment with hetus_30min
    hetus_occids = pd.read_csv(output_dir / "hetus_30min.csv", usecols=["occID"])["occID"]
    match = copresence_30min["occID"].equals(hetus_occids)
    assert match, "occID mismatch between copresence_30min and hetus_30min"
    print("VI-2 PASS -- occID order matches hetus_30min exactly")

    # VI-3: No all-NaN respondents for primary 8 columns
    primary_cols = [c for c in COP_COLS if c != "colleagues"]
    for col in primary_cols:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        all_nan_mask = copresence_30min[slot_cols].isna().all(axis=1)
        n_all_nan = all_nan_mask.sum()
        if n_all_nan > 0:
            print(f"VI-3 WARN -- {col}: {n_all_nan} respondents have all-NaN across 48 slots")
        else:
            print(f"VI-3 PASS -- {col}: no all-NaN respondents")

    # VI-4: colleagues NaN pattern by cycle
    ref_df = pd.read_csv(output_dir / "hetus_30min.csv", usecols=["occID", "CYCLE_YEAR"])
    coll_slots = [f"colleagues30_{i:03d}" for i in range(1, 49)]

    merged_check = copresence_30min[["occID"] + coll_slots].copy()
    merged_check["CYCLE_YEAR"] = ref_df["CYCLE_YEAR"].values

    for cycle in [2005, 2010, 2015, 2022]:
        sub = merged_check[merged_check["CYCLE_YEAR"] == cycle][coll_slots]
        nan_rate = sub.isna().sum().sum() / sub.size
        if cycle in [2005, 2010]:
            assert nan_rate == 1.0, f"Cycle {cycle}: colleagues NaN rate = {nan_rate:.4f}, expected 1.0"
            status = "PASS (100% NaN as expected)"
        else:
            assert nan_rate < 1.0, f"Cycle {cycle}: colleagues NaN rate = {nan_rate:.4f}, expected <1.0"
            status = f"PASS ({100*nan_rate:.1f}% NaN)"
        print(f"VI-4 colleagues {cycle}: {status}")

    # VI-5: Value range check
    all_slot_cols = [f"{col}30_{i:03d}" for col in COP_COLS for i in range(1, 49)]
    vals = copresence_30min[all_slot_cols].stack().dropna().unique()
    invalid = set(vals) - {1, 2}
    assert not invalid, f"Unexpected values in co-presence slots: {invalid}"
    print(f"VI-5 PASS -- all non-NaN values in {{1, 2}}")

    # VI-6: Co-presence prevalence plausibility
    for col, low, high in [("Alone", 30, 60), ("Spouse", 15, 45)]:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        vals = copresence_30min[slot_cols].to_numpy(dtype=float, na_value=np.nan)
        pct_present = 100 * np.nanmean(vals == 1)
        status = "PASS" if low <= pct_present <= high else "WARN"
        print(f"VI-6 {col}: {pct_present:.1f}% present (expected {low}-{high}%) -> {status}")

    # VI-7: Manual spot-check 5 random respondents
    import random
    random.seed(42)
    episodes_chk = pd.read_csv(output_dir / "merged_episodes.csv", low_memory=False)
    sample_ids = random.sample(occid_order, 5)
    print("\nVI-7 -- Manual spot-check (Alone30_001, slot 1 = 04:00-04:29)")
    for key in sample_ids:
        occ_id, cycle = key
        ep_sub = episodes_chk[
            (episodes_chk["occID"] == occ_id) & (episodes_chk["CYCLE_YEAR"] == cycle)
        ].copy()
        covering = ep_sub[
            ((ep_sub["startMin"] <= 269) & (ep_sub["endMin"] > 240)) |
            (ep_sub["endMin"] <= 30)
        ]
        src_vals = covering["Alone"].tolist()
        idx = occid_order.index(key)
        alone30_001 = copresence_30min.iloc[idx]["Alone30_001"]
        print(f"  occID={occ_id}, CYCLE={cycle}: source Alone vals near 04:00 = {src_vals} -> Alone30_001 = {alone30_001}")
    print("VI-7 -- Review output above manually to confirm majority vote is correct.")


# ── Phase J — AT_WORK Tiling (NEW — Leg-2 delta E) ────────────────────────────

def tile_work_to_30min(output_dir: Path, n_expected: int) -> pd.DataFrame:
    """Tile episode-level AT_WORK column to 30-min slot wide format.

    [Leg-2 delta E] Cloned from tile_copresence_to_30min; differences:
      - Single binary channel (AT_WORK), not 9 co-presence channels
      - Majority vote uses BINARY 1/0 (sum_work >= 2), NOT co-presence 1/2
      - Output columns: WORK30_001..WORK30_048 (Int8)
      - Separate CSV: outputs_step3/work_30min.csv
      - The residential Phase F/H path is NOT touched — purely additive

    Same 4 AM-origin slot math as co-presence tiler:
      start_shifted = (startMin - 240) % 1440
      end_shifted   = min(start_shifted + duration, 1440)

    Args:
        output_dir: Output directory (for reading merged_episodes.csv, hetus_30min.csv).
        n_expected: Expected row count captured from hetus_wide.

    Returns:
        DataFrame: N rows x 49 cols (occID + WORK30_001..WORK30_048).
        Values: 1=at work, 0=not at work, pd.NA for empty slots.
        Output: outputs_step3/work_30min.csv
    """
    print("\n-- Phase J: AT_WORK Tiling (episode -> 30-min slots) [Leg-2 NEW] ----")
    ep_path = output_dir / "merged_episodes.csv"
    episodes = pd.read_csv(ep_path, low_memory=False)
    print(f"  Loaded: {len(episodes):,} episode rows")

    # Verify required columns
    required_cols = ["occID", "startMin", "duration", "AT_WORK", "CYCLE_YEAR"]
    missing = [c for c in required_cols if c not in episodes.columns]
    if missing:
        print(f"  [WARNING] Missing columns: {missing} — AT_WORK tiling skipped!")
        return pd.DataFrame()

    # Build reference order from hetus_30min (ensures exact occID alignment)
    ref_path = output_dir / "hetus_30min.csv"
    ref_df = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    occid_order = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
    n = len(occid_order)
    print(f"  Reference order loaded: {n:,} respondents")

    if n != n_expected:
        print(f"  [WARNING] Expected {n_expected:,}, got {n:,}!")

    # Pre-allocate 10-min work array (N x 144)
    work_10min = np.full((n, 144), np.nan, dtype=float)
    print(f"  Pre-allocated work array of shape ({n}, 144)")

    # Sort episodes for sequential group access
    episodes_sorted = episodes.sort_values(["CYCLE_YEAR", "occID"]).reset_index(drop=True)

    # Build group boundary index
    grp = episodes_sorted.groupby(["occID", "CYCLE_YEAR"], sort=False)
    grp_indices = {k: (grp.indices[k].min(), grp.indices[k].max() + 1)
                   for k in grp.groups}
    print(f"  Episode group index built for {len(grp_indices):,} respondents")

    # Extract arrays for speed
    start_mins = episodes_sorted["startMin"].to_numpy(dtype=float)
    durations  = episodes_sorted["duration"].to_numpy(dtype=float)
    work_vals  = episodes_sorted["AT_WORK"].to_numpy(dtype=float)

    print("  Tiling AT_WORK episodes to 10-min slots...")
    for resp_idx, key in enumerate(occid_order):
        if resp_idx > 0 and resp_idx % 10_000 == 0:
            print(f"    {resp_idx:,} / {n:,}")
        if key not in grp_indices:
            continue
        row_start, row_end = grp_indices[key]
        for ep_row in range(row_start, row_end):
            s_min  = start_mins[ep_row]
            dur    = durations[ep_row]
            wk_val = work_vals[ep_row]

            # Same 4 AM-origin slot math as co-presence tiler
            start_shifted = (int(s_min) - 240) % 1440
            end_shifted   = min(start_shifted + int(dur), 1440)

            slot_s = start_shifted // 10
            slot_e = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0
            slot_e = min(slot_e, 144)

            if not np.isnan(wk_val):
                work_10min[resp_idx, slot_s:slot_e] = wk_val

    print("  AT_WORK tiling complete.")

    # Reshape to (N, 48, 3) for 30-min majority vote
    work_3d = work_10min.reshape(n, 48, 3)
    print(f"  Reshaped to ({n}, 48, 3)")

    # Binary majority vote: sum_work >= 2 -> 1, else 0; empty window -> NaN
    valid_count = np.sum(~np.isnan(work_3d), axis=2)   # (N, 48)
    sum_work    = np.nansum(work_3d, axis=2)             # (N, 48)

    # 1/0 encoding — matches AT_HOME encoding (NOT co-presence 1/2)
    work_30 = np.where(valid_count == 0, np.nan,
                       np.where(sum_work >= 2, 1.0, 0.0))

    n_work_nan = int(np.isnan(work_30).sum())
    print(f"  AT_WORK NaNs after vote: {n_work_nan}")

    # Build output DataFrame: occID + WORK30_001..WORK30_048 (Int8)
    work30_cols = [f"WORK30_{i:03d}" for i in range(1, 49)]
    work30_df   = pd.DataFrame(work_30, columns=work30_cols)
    for c in work30_cols:
        work30_df[c] = work30_df[c].astype(pd.Int8Dtype())

    occid_col = pd.DataFrame({"occID": [k[0] for k in occid_order]})
    work_30min = pd.concat([occid_col, work30_df], axis=1)

    print(f"  work_30min shape: {work_30min.shape}")
    # Expected: (N, 49) — occID + 48 WORK30 cols
    assert work_30min.shape == (n, 49), (
        f"work_30min shape mismatch: {work_30min.shape} (expected ({n}, 49))"
    )

    # Per-cycle weighted AT_WORK presence rate
    print("\n  Per-cycle weighted AT_WORK presence rate:")
    ref_full = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR", "WGHT_PER"], low_memory=False)
    work_with_meta = pd.concat([ref_full.reset_index(drop=True), work30_df.reset_index(drop=True)], axis=1)
    for cycle in CYCLES:
        mask = work_with_meta["CYCLE_YEAR"] == cycle
        sub  = work_with_meta[mask]
        w    = sub["WGHT_PER"]
        work_arr = sub[work30_cols].to_numpy(dtype=float)
        # Weighted mean of work indicators
        valid_flat = ~np.isnan(work_arr)
        if valid_flat.any():
            w_rep = np.repeat(w.values, 48)
            work_flat = work_arr.flatten()
            valid_mask = ~np.isnan(work_flat)
            wtd_rate = 100 * np.average(work_flat[valid_mask], weights=w_rep[valid_mask])
        else:
            wtd_rate = 0.0
        print(f"    {cycle}: weighted AT_WORK rate = {wtd_rate:.2f}%")

    out_path = output_dir / "work_30min.csv"
    print(f"\n  Writing {out_path} ...")
    work_30min.to_csv(out_path, index=False)
    size_mb = out_path.stat().st_size / 1e6
    print(f"  Done. File size: {size_mb:.1f} MB")
    return work_30min


def validate_work_30min(work_30min: pd.DataFrame, output_dir: Path, n_expected: int) -> None:
    """Validate the AT_WORK 30-min tiled output.

    Checks:
        VW-1: Shape (N rows x 49 cols)
        VW-2: occID alignment with hetus_30min
        VW-3: Values in {0, 1} only (no NaN should remain after vote; allow small %)
        VW-4: Weighted AT_WORK presence rate per cycle (printed for sanity)
        VW-5: Night-slot near-zero sanity (slots 1-8 should be near 0)

    Args:
        work_30min: work_30min DataFrame from tile_work_to_30min().
        output_dir: Output directory (for reading hetus_30min.csv).
        n_expected: Expected row count.
    """
    print("\n-- Phase J Validation (VW-1-5) ----------------------------------------")

    n = n_expected
    work30_cols = [f"WORK30_{i:03d}" for i in range(1, 49)]

    # VW-1: Shape
    if work_30min.shape[0] != n or work_30min.shape[1] != 49:
        print(f"VW-1 WARN -- Shape {work_30min.shape} (expected ({n}, 49))")
    else:
        print(f"VW-1 PASS -- shape ({n}, 49)")

    # VW-2: occID alignment
    hetus_occids = pd.read_csv(output_dir / "hetus_30min.csv", usecols=["occID"])["occID"]
    match = work_30min["occID"].equals(hetus_occids)
    status = "PASS" if match else "FAIL"
    print(f"VW-2 {status} -- occID alignment with hetus_30min")

    # VW-3: Values in {0, 1} (Int8 nullables)
    work_arr = work_30min[work30_cols].to_numpy(dtype=float)
    nan_count = int(np.isnan(work_arr).sum())
    non_binary_mask = ~np.isnan(work_arr) & ~np.isin(work_arr, [0.0, 1.0])
    non_binary = int(non_binary_mask.sum())
    print(f"VW-3 -- NaN cells: {nan_count:,} ({100*nan_count/(n*48):.2f}%)")
    if non_binary == 0:
        print(f"VW-3 PASS -- all non-NaN values in {{0, 1}}")
    else:
        print(f"VW-3 FAIL -- {non_binary} values outside {{0, 1}}")

    # VW-4: Weighted AT_WORK presence rate per cycle
    ref_df = pd.read_csv(output_dir / "hetus_30min.csv",
                         usecols=["occID", "CYCLE_YEAR", "WGHT_PER"], low_memory=False)
    work_with_meta = pd.concat([ref_df.reset_index(drop=True),
                                 work_30min[work30_cols].reset_index(drop=True)], axis=1)
    print("\nVW-4 -- Weighted AT_WORK presence rate per cycle:")
    for cycle in CYCLES:
        mask = work_with_meta["CYCLE_YEAR"] == cycle
        sub  = work_with_meta[mask]
        w    = sub["WGHT_PER"].values
        arr  = sub[work30_cols].to_numpy(dtype=float)
        flat = arr.flatten()
        w_rep = np.repeat(w, 48)
        valid = ~np.isnan(flat)
        if valid.any():
            rate = 100 * np.average(flat[valid], weights=w_rep[valid])
        else:
            rate = 0.0
        status = "PASS" if 1 <= rate <= 25 else "WARN"
        print(f"    {cycle}: {rate:.2f}%  -> {status} (expected 1-25%)")

    # VW-5: Night slots 1-8 (04:00-07:59) near-zero AT_WORK
    night_work_cols = [f"WORK30_{i:03d}" for i in range(1, 9)]
    night_vals = work_30min[night_work_cols].to_numpy(dtype=float)
    night_rate = 100 * np.nanmean(night_vals)
    status = "PASS" if night_rate < 6.0 else "WARN"
    print(f"\nVW-5 -- Night slots (1-8, 04:00-07:59) AT_WORK rate: {night_rate:.2f}%")
    print(f"  (expected < 6%, early-shift workers)  -> {status}")


# ── Phase K — AT_RETAIL Tiling (NEW — Leg-3 delta B/C) ────────────────────────

def tile_retail_to_30min(output_dir: Path, n_expected: int) -> pd.DataFrame:
    """Tile episode-level AT_RETAIL column to 30-min slot wide format.

    [Leg-3 delta B/C] Cloned from tile_work_to_30min() — unchanged in shape.
    Differences from tile_work_to_30min:
      - AT_RETAIL is NOT already a column in merged_episodes.csv (unlike
        AT_WORK, which is carried through from Step 2). It is derived here,
        once, from the episode-level occPRE / occACT columns using the
        FROZEN gated rule (OD-1, 2026-07-02):
            AT_RETAIL = ((occPRE == 5) |
                         ((occACT == 4) & occPRE.isin({5, 9}))).astype(float)
      - Single binary channel (AT_RETAIL), 1/0 majority vote (sum_present >= 2),
        NOT the co-presence 1/2 scheme (matches AT_HOME / AT_WORK encoding).
      - Output columns: RETL30_001..RETL30_048 (Int8)
      - Separate CSV: outputs_step3/retail_30min.csv
      - Purely additive — does not touch merged_episodes.csv, hetus_wide.csv,
        hetus_30min.csv, copresence_30min.csv, or work_30min.csv.

    Same 4 AM-origin slot math as tile_work_to_30min / tile_copresence_to_30min:
      start_shifted = (startMin - 240) % 1440
      end_shifted   = min(start_shifted + duration, 1440)

    Args:
        output_dir: Output directory (for reading merged_episodes.csv, hetus_30min.csv).
        n_expected: Expected row count captured from hetus_wide.

    Returns:
        DataFrame: N rows x 49 cols (occID + RETL30_001..RETL30_048).
        Values: 1=at retail, 0=not at retail, pd.NA for empty slots.
        Output: outputs_step3/retail_30min.csv
    """
    print("\n-- Phase K: AT_RETAIL Tiling (episode -> 30-min slots) [Leg-3 NEW] ----")
    ep_path = output_dir / "merged_episodes.csv"
    episodes = pd.read_csv(ep_path, low_memory=False)
    print(f"  Loaded: {len(episodes):,} episode rows")

    # Verify required columns
    required_cols = ["occID", "startMin", "duration", "occPRE", "occACT", "CYCLE_YEAR"]
    missing = [c for c in required_cols if c not in episodes.columns]
    if missing:
        print(f"  [WARNING] Missing columns: {missing} — AT_RETAIL tiling skipped!")
        return pd.DataFrame()

    # [Leg-3 delta B] FROZEN AT_RETAIL derivation (OD-1, 2026-07-02) —
    # derived once, before the tiling loop, mirroring the existing AT_WORK
    # derivation pattern (AT_WORK = (occPRE == 2)).
    episodes["AT_RETAIL"] = (
        (episodes["occPRE"] == 5) |
        ((episodes["occACT"] == 4) & episodes["occPRE"].isin({5, 9}))
    ).astype(float)
    n_retail_episodes = int(episodes["AT_RETAIL"].sum())
    print(f"  AT_RETAIL derived: {n_retail_episodes:,} / {len(episodes):,} episodes flagged "
          f"({100 * n_retail_episodes / len(episodes):.2f}%)")

    # Build reference order from hetus_30min (ensures exact occID alignment)
    ref_path = output_dir / "hetus_30min.csv"
    ref_df = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    occid_order = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
    n = len(occid_order)
    print(f"  Reference order loaded: {n:,} respondents")

    if n != n_expected:
        print(f"  [WARNING] Expected {n_expected:,}, got {n:,}!")

    # Pre-allocate 10-min retail array (N x 144)
    retail_10min = np.full((n, 144), np.nan, dtype=float)
    print(f"  Pre-allocated retail array of shape ({n}, 144)")

    # Sort episodes for sequential group access
    episodes_sorted = episodes.sort_values(["CYCLE_YEAR", "occID"]).reset_index(drop=True)

    # Build group boundary index
    grp = episodes_sorted.groupby(["occID", "CYCLE_YEAR"], sort=False)
    grp_indices = {k: (grp.indices[k].min(), grp.indices[k].max() + 1)
                   for k in grp.groups}
    print(f"  Episode group index built for {len(grp_indices):,} respondents")

    # Extract arrays for speed
    start_mins  = episodes_sorted["startMin"].to_numpy(dtype=float)
    durations   = episodes_sorted["duration"].to_numpy(dtype=float)
    retail_vals = episodes_sorted["AT_RETAIL"].to_numpy(dtype=float)

    print("  Tiling AT_RETAIL episodes to 10-min slots...")
    for resp_idx, key in enumerate(occid_order):
        if resp_idx > 0 and resp_idx % 10_000 == 0:
            print(f"    {resp_idx:,} / {n:,}")
        if key not in grp_indices:
            continue
        row_start, row_end = grp_indices[key]
        for ep_row in range(row_start, row_end):
            s_min  = start_mins[ep_row]
            dur    = durations[ep_row]
            rt_val = retail_vals[ep_row]

            # Same 4 AM-origin slot math as co-presence / AT_WORK tilers
            start_shifted = (int(s_min) - 240) % 1440
            end_shifted   = min(start_shifted + int(dur), 1440)

            slot_s = start_shifted // 10
            slot_e = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0
            slot_e = min(slot_e, 144)

            if not np.isnan(rt_val):
                retail_10min[resp_idx, slot_s:slot_e] = rt_val

    print("  AT_RETAIL tiling complete.")

    # Reshape to (N, 48, 3) for 30-min majority vote
    retail_3d = retail_10min.reshape(n, 48, 3)
    print(f"  Reshaped to ({n}, 48, 3)")

    # Binary majority vote: sum_present >= 2 -> 1, else 0; empty window -> NaN
    valid_count = np.sum(~np.isnan(retail_3d), axis=2)   # (N, 48)
    sum_present = np.nansum(retail_3d, axis=2)             # (N, 48)

    # 1/0 encoding — matches AT_HOME / AT_WORK encoding (NOT co-presence 1/2)
    retail_30 = np.where(valid_count == 0, np.nan,
                         np.where(sum_present >= 2, 1.0, 0.0))

    n_retail_nan = int(np.isnan(retail_30).sum())
    print(f"  AT_RETAIL NaNs after vote: {n_retail_nan}")

    # Build output DataFrame: occID + RETL30_001..RETL30_048 (Int8)
    retail30_cols = [f"RETL30_{i:03d}" for i in range(1, 49)]
    retail30_df   = pd.DataFrame(retail_30, columns=retail30_cols)
    for c in retail30_cols:
        retail30_df[c] = retail30_df[c].astype(pd.Int8Dtype())

    occid_col = pd.DataFrame({"occID": [k[0] for k in occid_order]})
    retail_30min = pd.concat([occid_col, retail30_df], axis=1)

    print(f"  retail_30min shape: {retail_30min.shape}")
    # Expected: (N, 49) — occID + 48 RETL30 cols
    assert retail_30min.shape == (n, 49), (
        f"retail_30min shape mismatch: {retail_30min.shape} (expected ({n}, 49))"
    )

    # Per-cycle weighted AT_RETAIL presence rate
    print("\n  Per-cycle weighted AT_RETAIL presence rate:")
    ref_full = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR", "WGHT_PER"], low_memory=False)
    retail_with_meta = pd.concat([ref_full.reset_index(drop=True), retail30_df.reset_index(drop=True)], axis=1)
    for cycle in CYCLES:
        mask = retail_with_meta["CYCLE_YEAR"] == cycle
        sub  = retail_with_meta[mask]
        w    = sub["WGHT_PER"]
        retail_arr = sub[retail30_cols].to_numpy(dtype=float)
        valid_flat = ~np.isnan(retail_arr)
        if valid_flat.any():
            w_rep = np.repeat(w.values, 48)
            retail_flat = retail_arr.flatten()
            valid_mask = ~np.isnan(retail_flat)
            wtd_rate = 100 * np.average(retail_flat[valid_mask], weights=w_rep[valid_mask])
        else:
            wtd_rate = 0.0
        print(f"    {cycle}: weighted AT_RETAIL rate = {wtd_rate:.2f}%")

    out_path = output_dir / "retail_30min.csv"
    print(f"\n  Writing {out_path} ...")
    retail_30min.to_csv(out_path, index=False)
    size_mb = out_path.stat().st_size / 1e6
    print(f"  Done. File size: {size_mb:.1f} MB")
    return retail_30min


def validate_retail_30min(retail_30min: pd.DataFrame, output_dir: Path, n_expected: int) -> None:
    """Validate the AT_RETAIL 30-min tiled output.

    Checks:
        VR-1: Shape (N rows x 49 cols)
        VR-2: occID alignment with hetus_30min
        VR-3: Values in {0, 1} only (no NaN should remain after vote; allow small %)
        VR-4: Weighted AT_RETAIL presence rate per cycle (printed for sanity)
        VR-5: Night-slot near-zero sanity (slots 1-8 should be near 0)

    Args:
        retail_30min: retail_30min DataFrame from tile_retail_to_30min().
        output_dir: Output directory (for reading hetus_30min.csv).
        n_expected: Expected row count.
    """
    print("\n-- Phase K Validation (VR-1-5) ----------------------------------------")

    n = n_expected
    retail30_cols = [f"RETL30_{i:03d}" for i in range(1, 49)]

    # VR-1: Shape
    if retail_30min.shape[0] != n or retail_30min.shape[1] != 49:
        print(f"VR-1 WARN -- Shape {retail_30min.shape} (expected ({n}, 49))")
    else:
        print(f"VR-1 PASS -- shape ({n}, 49)")

    # VR-2: occID alignment
    hetus_occids = pd.read_csv(output_dir / "hetus_30min.csv", usecols=["occID"])["occID"]
    match = retail_30min["occID"].equals(hetus_occids)
    status = "PASS" if match else "FAIL"
    print(f"VR-2 {status} -- occID alignment with hetus_30min")

    # VR-3: Values in {0, 1} (Int8 nullables)
    retail_arr = retail_30min[retail30_cols].to_numpy(dtype=float)
    nan_count = int(np.isnan(retail_arr).sum())
    non_binary_mask = ~np.isnan(retail_arr) & ~np.isin(retail_arr, [0.0, 1.0])
    non_binary = int(non_binary_mask.sum())
    print(f"VR-3 -- NaN cells: {nan_count:,} ({100*nan_count/(n*48):.2f}%)")
    if non_binary == 0:
        print(f"VR-3 PASS -- all non-NaN values in {{0, 1}}")
    else:
        print(f"VR-3 FAIL -- {non_binary} values outside {{0, 1}}")

    # VR-4: Weighted AT_RETAIL presence rate per cycle
    ref_df = pd.read_csv(output_dir / "hetus_30min.csv",
                         usecols=["occID", "CYCLE_YEAR", "WGHT_PER"], low_memory=False)
    retail_with_meta = pd.concat([ref_df.reset_index(drop=True),
                                   retail_30min[retail30_cols].reset_index(drop=True)], axis=1)
    print("\nVR-4 -- Weighted AT_RETAIL presence rate per cycle:")
    for cycle in CYCLES:
        mask = retail_with_meta["CYCLE_YEAR"] == cycle
        sub  = retail_with_meta[mask]
        w    = sub["WGHT_PER"].values
        arr  = sub[retail30_cols].to_numpy(dtype=float)
        flat = arr.flatten()
        w_rep = np.repeat(w, 48)
        valid = ~np.isnan(flat)
        if valid.any():
            rate = 100 * np.average(flat[valid], weights=w_rep[valid])
        else:
            rate = 0.0
        status = "PASS" if 1 <= rate <= 12 else "WARN"
        print(f"    {cycle}: {rate:.2f}%  -> {status} (expected ~1-12%, provisional)")

    # VR-5: Night slots 1-8 (04:00-07:59) near-zero AT_RETAIL
    night_retail_cols = [f"RETL30_{i:03d}" for i in range(1, 9)]
    night_vals = retail_30min[night_retail_cols].to_numpy(dtype=float)
    night_rate = 100 * np.nanmean(night_vals)
    status = "PASS" if night_rate < 1.0 else "WARN"
    print(f"\nVR-5 -- Night slots (1-8, 04:00-07:59) AT_RETAIL rate: {night_rate:.2f}%")
    print(f"  (expected < 1%)  -> {status}")


# ── Delta D — Legacy Bit-Identity Hash Gate (NEW — Leg-3 delta D) ────────────

def _sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Compute SHA-256 hex digest of a file, reading in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_legacy_bit_identity(output_dir: Path, leg2_output_dir: Path) -> dict:
    """[Leg-3 delta D] SHA-256 the 6 legacy outputs and compare to Leg-2.

    The retail channel must be purely additive: none of the 6 legacy Step-3
    outputs may differ, byte-for-byte, from the shipped Leg-2 outputs_step3/
    copies. ANY mismatch on the 5 plain CSVs is a hard FAIL, printed loudly.
    The parquet file is hashed first; if pandas/pyarrow versions make the
    parquet byte layout non-deterministic (hash mismatch despite identical
    data), this falls back to column-wise value equality on
    merged_episodes.parquet and records which comparison was used.

    Args:
        output_dir: Leg-3 outputs_step3/ directory (this build's outputs).
        leg2_output_dir: Leg-2 outputs_step3/ directory (bit-identity reference).

    Returns:
        dict keyed by filename -> {"status": "PASS"/"FAIL", "method": str,
        "leg3_hash": str, "leg2_hash": str}
    """
    print("\n-- Delta D: Legacy Bit-Identity Hash Gate vs Leg-2 [Leg-3 NEW] --------")
    results: dict = {}
    csv_outputs = [f for f in LEGACY_OUTPUTS if f.endswith(".csv")]
    parquet_outputs = [f for f in LEGACY_OUTPUTS if f.endswith(".parquet")]

    any_fail = False

    for fname in csv_outputs:
        leg3_path = output_dir / fname
        leg2_path = leg2_output_dir / fname
        if not leg3_path.exists():
            print(f"  [FAIL] {fname}: Leg-3 output MISSING at {leg3_path}")
            results[fname] = {"status": "FAIL", "method": "sha256", "leg3_hash": None, "leg2_hash": None}
            any_fail = True
            continue
        if not leg2_path.exists():
            print(f"  [FAIL] {fname}: Leg-2 reference MISSING at {leg2_path}")
            results[fname] = {"status": "FAIL", "method": "sha256", "leg3_hash": None, "leg2_hash": None}
            any_fail = True
            continue
        h3 = _sha256_file(leg3_path)
        h2 = _sha256_file(leg2_path)
        if h3 == h2:
            print(f"  [PASS] {fname}: SHA-256 identical ({h3[:16]}...)")
            results[fname] = {"status": "PASS", "method": "sha256", "leg3_hash": h3, "leg2_hash": h2}
        else:
            print(f"  *** FAIL *** {fname}: SHA-256 MISMATCH")
            print(f"      Leg-3: {h3}")
            print(f"      Leg-2: {h2}")
            results[fname] = {"status": "FAIL", "method": "sha256", "leg3_hash": h3, "leg2_hash": h2}
            any_fail = True

    for fname in parquet_outputs:
        leg3_path = output_dir / fname
        leg2_path = leg2_output_dir / fname
        if not leg3_path.exists() or not leg2_path.exists():
            print(f"  [FAIL] {fname}: file missing (Leg-3 exists={leg3_path.exists()}, "
                  f"Leg-2 exists={leg2_path.exists()})")
            results[fname] = {"status": "FAIL", "method": "sha256", "leg3_hash": None, "leg2_hash": None}
            any_fail = True
            continue

        h3 = _sha256_file(leg3_path)
        h2 = _sha256_file(leg2_path)
        if h3 == h2:
            print(f"  [PASS] {fname}: SHA-256 identical ({h3[:16]}...)")
            results[fname] = {"status": "PASS", "method": "sha256", "leg3_hash": h3, "leg2_hash": h2}
            continue

        # Hash mismatch -- fall back to column-wise value equality, per the
        # runbook's Delta D fallback (parquet hashes can be non-deterministic
        # across pandas/pyarrow versions even for identical logical content).
        print(f"  [WARN] {fname}: SHA-256 mismatch -- falling back to column-wise "
              f"value equality (recording method='column_equality')")
        try:
            df3 = pd.read_parquet(leg3_path)
            df2 = pd.read_parquet(leg2_path)
            same_shape = df3.shape == df2.shape
            same_cols = list(df3.columns) == list(df2.columns)
            values_equal = same_shape and same_cols and df3.equals(df2)
            if values_equal:
                print(f"  [PASS] {fname}: column-wise value equality holds "
                      f"(hash differs -- non-deterministic parquet encoding)")
                results[fname] = {"status": "PASS", "method": "column_equality",
                                   "leg3_hash": h3, "leg2_hash": h2}
            else:
                print(f"  *** FAIL *** {fname}: column-wise value equality FAILED "
                      f"(shape match={same_shape}, cols match={same_cols})")
                results[fname] = {"status": "FAIL", "method": "column_equality",
                                   "leg3_hash": h3, "leg2_hash": h2}
                any_fail = True
        except Exception as e:
            print(f"  *** FAIL *** {fname}: column-equality check errored: {e}")
            results[fname] = {"status": "FAIL", "method": "column_equality_error",
                               "leg3_hash": h3, "leg2_hash": h2}
            any_fail = True

    print("\n" + "-" * 60)
    if any_fail:
        print("*** DELTA D GATE: FAIL *** -- one or more legacy outputs diverged from Leg-2.")
        print("*** The retail channel is NOT purely additive. STOP and investigate. ***")
    else:
        print("Delta D GATE: PASS -- all 6 legacy outputs bit-identical (or value-equal) to Leg-2.")
    print("-" * 60)

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the full Step 3 Leg-3 pipeline."""
    print("=" * 60)
    print("Step 3 (Leg-3) -- Merge, Tiling, AT_WORK & AT_RETAIL Channels")
    print("=" * 60)
    print(f"  INPUT_DIR       : {INPUT_DIR}")
    print(f"  OUTPUT_DIR      : {OUTPUT_DIR}")
    print(f"  LEG2_OUTPUT_DIR : {LEG2_OUTPUT_DIR}  (Delta D bit-identity reference)")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Phase A+B: Load & stack
    print("\n-- Phase A+B: Load & Stack -----------------------------------------")
    print("\nMain files:")
    unified_main = load_and_stack_main(INPUT_DIR)

    print("\nEpisode files:")
    unified_episode = load_and_stack_episodes(INPUT_DIR)

    check_stack_integrity(unified_main, unified_episode)

    # Phase C: Merge
    merged = merge_main_episode(unified_main, unified_episode)

    # Phase D: Filter
    merged_valid, exclusion_log = filter_invalid_diaries(merged)

    # Phase E: Temporal features
    merged_final = derive_temporal_features(merged_valid)

    # Phase F: HETUS conversion (residential, bit-identical to Leg 1)
    hetus_wide = build_hetus_wide(merged_final)

    # [Leg-2 delta D] Capture actual N for dynamic assertions
    N = hetus_wide.shape[0]
    print(f"\n  [Leg-2 note] Actual N = {N:,} (expected ~64,061 to match Leg 1)")
    if N != 64_061:
        print(f"  *** WARNING *** Actual N {N:,} differs from Leg-1 baseline 64,061!")
        print(f"  This should be investigated — residential diaries / DIARY_VALID logic unchanged.")
    else:
        print(f"  N matches Leg-1 baseline exactly.")

    # Phase G: Export
    export_all(merged_final, hetus_wide, OUTPUT_DIR)

    # Phase H: Resolution downsampling (residential, bit-identical)
    hetus_30min, n_ties = downsample_to_30min(hetus_wide, OUTPUT_DIR, N)

    print(f"\n-- Phase H Summary -------------------------------------------------")
    print(f"  Rows            : {hetus_30min.shape[0]:,}")
    print(f"  Total columns   : {hetus_30min.shape[1]}")
    print(f"  act30 columns   : {len([c for c in hetus_30min.columns if c.startswith('act30_')])}")
    print(f"  hom30 columns   : {len([c for c in hetus_30min.columns if c.startswith('hom30_')])}")
    print(f"  NaN in act30    : {hetus_30min[[c for c in hetus_30min.columns if c.startswith('act30_')]].isna().sum().sum()}")
    print(f"  NaN in hom30    : {hetus_30min[[c for c in hetus_30min.columns if c.startswith('hom30_')]].isna().sum().sum()}")

    # Phase H validation
    validate_30min(hetus_30min, n_ties, OUTPUT_DIR, N)

    # Phase I: Co-presence tiling (verbatim)
    copresence_30min = tile_copresence_to_30min(OUTPUT_DIR, N)

    print(f"\n-- Phase I Summary -------------------------------------------------")
    print(f"  Rows             : {copresence_30min.shape[0]:,}")
    print(f"  Total columns    : {copresence_30min.shape[1]}")
    for col in COP_COLS:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        nan_total = copresence_30min[slot_cols].isna().sum().sum()
        print(f"  {col:>14}: NaN slots = {nan_total:,}")

    # Validate Phase I
    ref_df = pd.read_csv(OUTPUT_DIR / "hetus_30min.csv",
                         usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    occ_cyc = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
    validate_copresence_30min_export(copresence_30min, occ_cyc, OUTPUT_DIR, N)

    # ── Phase J: AT_WORK Tiling [Leg-2 NEW] ───────────────────────────────
    work_30min = tile_work_to_30min(OUTPUT_DIR, N)

    if not work_30min.empty:
        print(f"\n-- Phase J Summary -------------------------------------------------")
        print(f"  Rows             : {work_30min.shape[0]:,}")
        print(f"  Total columns    : {work_30min.shape[1]}")
        work30_cols = [f"WORK30_{i:03d}" for i in range(1, 49)]
        work_arr = work_30min[work30_cols].to_numpy(dtype=float)
        n_ones  = int((work_arr == 1).sum())
        n_zeros = int((work_arr == 0).sum())
        n_nans  = int(np.isnan(work_arr).sum())
        print(f"  AT_WORK=1 cells  : {n_ones:,} ({100*n_ones/(N*48):.2f}%)")
        print(f"  AT_WORK=0 cells  : {n_zeros:,} ({100*n_zeros/(N*48):.2f}%)")
        print(f"  NaN cells        : {n_nans:,} ({100*n_nans/(N*48):.2f}%)")

        # [Leg-2 delta D] Assert all three wide outputs share same N and occID order
        h30_occids = pd.read_csv(OUTPUT_DIR / "hetus_30min.csv", usecols=["occID"])["occID"]
        cop_occids = copresence_30min["occID"]
        work_occids = work_30min["occID"]

        assert len(h30_occids) == N, f"hetus_30min N mismatch: {len(h30_occids)}"
        assert len(cop_occids) == N, f"copresence_30min N mismatch: {len(cop_occids)}"
        assert len(work_occids) == N, f"work_30min N mismatch: {len(work_occids)}"
        assert h30_occids.equals(cop_occids.reset_index(drop=True)), "hetus vs copresence occID mismatch"
        assert h30_occids.equals(work_occids.reset_index(drop=True)), "hetus vs work occID mismatch"
        print(f"\n  [PASS] All three wide outputs share N={N:,} and identical occID order.")

        # Phase J validation
        validate_work_30min(work_30min, OUTPUT_DIR, N)

    # AT_HOME / AT_WORK overlap note
    print("\n-- AT_HOME / AT_WORK overlap note ----------------------------------")
    if not work_30min.empty:
        hom30_cols_list = [f"hom30_{i:03d}" for i in range(1, 49)]
        h30_full = pd.read_csv(OUTPUT_DIR / "hetus_30min.csv",
                               usecols=["occID"] + hom30_cols_list, low_memory=False)
        hom_arr = h30_full[hom30_cols_list].to_numpy(dtype=float)
        wrk_arr = work_30min[work30_cols].to_numpy(dtype=float)

        both_one = ((hom_arr == 1) & (wrk_arr == 1)).sum()
        total_cells = N * 48
        pct_both = 100 * both_one / total_cells
        print(f"  Slots where AT_HOME=1 AND AT_WORK=1: {both_one:,} ({pct_both:.3f}% of all cells)")
        print(f"  (WFH workers coded as AT_HOME in 2022 — small overlap expected)")

    # ── Phase K: AT_RETAIL Tiling [Leg-3 NEW] ─────────────────────────────
    retail_30min = tile_retail_to_30min(OUTPUT_DIR, N)

    if not retail_30min.empty:
        print(f"\n-- Phase K Summary -------------------------------------------------")
        print(f"  Rows             : {retail_30min.shape[0]:,}")
        print(f"  Total columns    : {retail_30min.shape[1]}")
        retail30_cols = [f"RETL30_{i:03d}" for i in range(1, 49)]
        retail_arr = retail_30min[retail30_cols].to_numpy(dtype=float)
        n_ones  = int((retail_arr == 1).sum())
        n_zeros = int((retail_arr == 0).sum())
        n_nans  = int(np.isnan(retail_arr).sum())
        print(f"  AT_RETAIL=1 cells: {n_ones:,} ({100*n_ones/(N*48):.2f}%)")
        print(f"  AT_RETAIL=0 cells: {n_zeros:,} ({100*n_zeros/(N*48):.2f}%)")
        print(f"  NaN cells        : {n_nans:,} ({100*n_nans/(N*48):.2f}%)")

        # Assert retail_30min shares N and occID order with hetus_30min
        h30_occids = pd.read_csv(OUTPUT_DIR / "hetus_30min.csv", usecols=["occID"])["occID"]
        retail_occids = retail_30min["occID"]
        assert len(retail_occids) == N, f"retail_30min N mismatch: {len(retail_occids)}"
        assert h30_occids.equals(retail_occids.reset_index(drop=True)), "hetus vs retail occID mismatch"
        print(f"\n  [PASS] retail_30min shares N={N:,} and identical occID order with hetus_30min.")

        # Phase K validation
        validate_retail_30min(retail_30min, OUTPUT_DIR, N)

        # AT_HOME / AT_RETAIL and AT_WORK / AT_RETAIL exclusivity note
        print("\n-- AT_RETAIL exclusivity note ---------------------------------------")
        hom30_cols_list = [f"hom30_{i:03d}" for i in range(1, 49)]
        h30_full = pd.read_csv(OUTPUT_DIR / "hetus_30min.csv",
                               usecols=["occID"] + hom30_cols_list, low_memory=False)
        hom_arr2 = h30_full[hom30_cols_list].to_numpy(dtype=float)
        rtl_arr  = retail_30min[retail30_cols].to_numpy(dtype=float)
        both_home_retail = ((hom_arr2 == 1) & (rtl_arr == 1)).sum()
        pct_home_retail = 100 * both_home_retail / (N * 48)
        print(f"  Slots where AT_HOME=1 AND AT_RETAIL=1: {both_home_retail:,} ({pct_home_retail:.3f}% of all cells)")
        if not work_30min.empty:
            work30_cols_list = [f"WORK30_{i:03d}" for i in range(1, 49)]
            wrk_arr2 = work_30min[work30_cols_list].to_numpy(dtype=float)
            both_work_retail = ((wrk_arr2 == 1) & (rtl_arr == 1)).sum()
            pct_work_retail = 100 * both_work_retail / (N * 48)
            print(f"  Slots where AT_WORK=1 AND AT_RETAIL=1: {both_work_retail:,} ({pct_work_retail:.3f}% of all cells)")
        print(f"  (mutually exclusive occPRE at episode level; only majority-vote edge effects expected)")

    print("\n" + "=" * 60)
    print("Step 3 (Leg-3) complete.")
    print("=" * 60)

    # Print final output file list (6 legacy + retail_30min)
    print("\nOutput files:")
    for fname in LEGACY_OUTPUTS + ["retail_30min.csv"]:
        p = OUTPUT_DIR / fname
        if p.exists():
            print(f"  {p.stat().st_size / 1e6:.1f} MB  {fname}")
        else:
            print(f"  MISSING  {fname}")

    # ── Delta D: Legacy bit-identity hash gate vs Leg-2 [Leg-3 NEW] ────────
    verify_legacy_bit_identity(OUTPUT_DIR, LEG2_OUTPUT_DIR)


if __name__ == "__main__":
    main()
