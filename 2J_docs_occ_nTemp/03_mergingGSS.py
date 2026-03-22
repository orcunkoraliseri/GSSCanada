"""Step 3 — Merge & Temporal Feature Derivation.

Merges harmonized Step 2 outputs (Main + Episode) into a unified dataset,
derives temporal features, and converts to HETUS 144-slot wide format.

Phases:
    A+B : Column standardization & vertical stacking
    C   : LEFT JOIN (Episode ← Main on occID + CYCLE_YEAR)
    D   : DIARY_VALID filtering
    E   : Temporal feature derivation
    F   : HETUS 144-slot wide format conversion
    G   : Export
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
INPUT_DIR = Path("outputs_step2")
OUTPUT_DIR = Path("outputs_step3")

CYCLES = [2005, 2010, 2015, 2022]

# ── Phase A — Column Definitions ─────────────────────────────────────────────

# Harmonized common columns to select from each Main file.
# Cycle-specific extras (CTW checkboxes, REGION, raw employment codes,
# HRSWRK_RAW, TOTINC_RAW, SURVMNTH) are intentionally excluded.
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
    # "MODE",
    "NOCS",          # 2015/2022 only → NaN for 2005/2010
    "COW",           # Class of Worker (harmonized 3-category)
    "WKSWRK",        # Weeks worked per year
    # Metadata flags
    "TOTINC_SOURCE",
    "CYCLE_YEAR",
    "SURVYEAR",
    "COLLECT_MODE",
    "TUI_10_AVAIL",
    "BS_TYPE",
]

# Harmonized common columns to select from each Episode file.
# Raw source columns (ACTCODE, PLACE, TUI_01, LOCATION) and cycle-specific
# extras (TOTEPISO, TUI_10, TUI_15) are excluded.
# TUI_07 (tech use) included as optional: present for 2015/2022, NaN for 2005/2010.
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
    # Co-presence
    "Alone",
    "Spouse",
    "Children",
    "parents",
    "otherInFAMs",
    "otherHHs",
    "friends",
    "others",
    "colleagues",    # TUI_06I (2015/2022 only) → NaN for 2005/2010
    # Auxiliary (optional)
    "TUI_07",        # tech use: 2015/2022 only → NaN for 2005/2010
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
        print(f"  main_{cycle}.csv → {n:>6,} rows | columns: {list(df.columns)[:5]}…")
        dfs.append(df)

    unified = pd.concat(dfs, ignore_index=True)
    print(f"\n  Unified Main: {len(unified):,} rows × {unified.shape[1]} columns")
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
        print(f"  episode_{cycle}.csv → {n:>8,} rows | columns: {list(df.columns)[:5]}…")
        dfs.append(df)

    unified = pd.concat(dfs, ignore_index=True)
    print(f"\n  Unified Episodes: {len(unified):,} rows × {unified.shape[1]} columns")
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
    print("\n── Stack integrity checks ──────────────────────────────────")

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
    """LEFT JOIN Episode ← Main on (occID, CYCLE_YEAR).

    Each episode row carries the respondent's full demographic profile.
    Join key is composite because occIDs are only unique within a cycle.

    Args:
        unified_main: Stacked Main DataFrame.
        unified_episode: Stacked Episode DataFrame.

    Returns:
        Merged DataFrame; same row count as unified_episode.
    """
    print("\n── Phase C: LEFT JOIN ──────────────────────────────────────")
    n_before = len(unified_episode)

    merged = unified_episode.merge(
        unified_main,
        on=["occID", "CYCLE_YEAR"],
        how="left",
        validate="many_to_one",
    )

    n_after = len(merged)
    assert n_after == n_before, (
        f"Row count changed after merge: {n_before} → {n_after}"
    )

    orphans = merged["WGHT_PER"].isna().sum()
    status = "PASS" if orphans == 0 else "FAIL"
    print(f"  [{status}] Orphan episodes (no Main match): {orphans}")
    print(f"  Merged: {n_after:,} rows × {merged.shape[1]} columns")
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
    print("\n── Phase D: DIARY_VALID Filtering ──────────────────────────")

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
            f"  {cycle}: {total_ids:>6,} respondents → {excluded:>4} excluded "
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
    """Convert HHMM integer series to minutes from midnight (0–1439).

    Args:
        hhmm: Series of HHMM integers (e.g. 400 → 4:00 AM, 1330 → 1:30 PM).

    Returns:
        Series of integer minutes from midnight.
    """
    hhmm = hhmm.fillna(0).astype(int)
    return (hhmm // 100) * 60 + (hhmm % 100)


def _hhmm_to_hetus_slot(hhmm: pd.Series) -> pd.Series:
    """Convert HHMM series to HETUS slot index (1–144), 4:00 AM origin.

    HETUS slot 1 = 04:00–04:09, slot 144 = 03:50–03:59 next day.

    Args:
        hhmm: Series of HHMM integers.

    Returns:
        Series of integer slot indices (1–144).
    """
    total_min = _parse_hhmm_to_minutes(hhmm)
    shifted = (total_min - 240) % 1440   # shift 4 AM → 0
    return (shifted // 10 + 1).astype(int)


def derive_temporal_features(merged: pd.DataFrame) -> pd.DataFrame:
    """Derive DAYTYPE, HOUR_OF_DAY, TIMESLOT_10, and DDAY_STRATA columns.

    Args:
        merged: Filtered merged DataFrame (DIARY_VALID == 1 only).

    Returns:
        DataFrame with five new columns appended.
    """
    print("\n── Phase E: Temporal Feature Derivation ────────────────────")

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

    # HOUR_OF_DAY (0–23)
    df["HOUR_OF_DAY"] = (df["startMin"] // 60).astype(int)

    # TIMESLOT_10: HETUS 10-min slot (1–144, 4 AM origin)
    df["TIMESLOT_10"] = _hhmm_to_hetus_slot(df["start"])

    derived_cols = ["DAYTYPE", "startMin", "endMin", "HOUR_OF_DAY", "TIMESLOT_10", "DDAY_STRATA"]
    print(f"  Derived columns added: {derived_cols}")
    for col in derived_cols:
        print(f"    {col}: {df[col].nunique()} unique values, "
              f"{df[col].isna().sum()} NaN")

    return df


# ── Phase F — HETUS 144-Slot Wide Format Conversion ──────────────────────────

def _build_slot_arrays(
    group: pd.DataFrame,
) -> tuple[dict[str, int], dict[str, int]]:
    """Convert one respondent's episodes to two 144-element slot dicts.

    Slot assignment uses start time (shifted to 4:00 AM origin) combined with
    episode duration to compute the slot range.  This avoids double-wrap errors
    for episodes that cross midnight AND the 4:00 AM diary boundary (e.g.
    sleep starting at 23:35 with duration 265 min ending at 04:00 AM).

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

        # Compute end using duration -- avoids double-wrap errors from
        # end HHMM times that cross both midnight and the 4 AM boundary.
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
        - slot_001 … slot_144  : occACT activity code per 10-min slot
        - home_001 … home_144  : AT_HOME binary flag per 10-min slot
        - Person-level demographic & temporal columns

    Args:
        merged: Filtered, feature-enriched merged DataFrame.

    Returns:
        Wide-format DataFrame with one row per (occID, CYCLE_YEAR).
    """
    print("\n── Phase F: HETUS 144-Slot Conversion ──────────────────────")

    SLOT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
    HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]

    PERSON_COLS = [
        "occID", "CYCLE_YEAR", "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR",
        "CMA", "WGHT_PER", "DDAY", "KOL", "LFTAG", "TOTINC", "HRSWRK",
        # "MODE", 
        "NOCS", "COW", "WKSWRK", "TOTINC_SOURCE", "SURVYEAR",
        "COLLECT_MODE", "TUI_10_AVAIL", "BS_TYPE",
        "DAYTYPE", "DDAY_STRATA",
    ]

    n_respondents = merged.groupby(["occID", "CYCLE_YEAR"]).ngroups
    print(f"  Building {n_respondents:,} respondent rows …")

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

    # Forward-fill NaN slots within each respondent row (caused by episodes
    # with unmapped occACT codes).  This is standard time-use practice:
    # carry the preceding activity code forward across the brief gap.
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
    print("\n── Phase G: Export ──────────────────────────────────────────")
    output_dir.mkdir(parents=True, exist_ok=True)

    path_csv = output_dir / "merged_episodes.csv"
    path_pq = output_dir / "merged_episodes.parquet"
    path_hetus = output_dir / "hetus_wide.csv"

    print(f"  Writing {path_csv} …")
    merged.to_csv(path_csv, index=False)

    print(f"  Writing {path_pq} …")
    merged.to_parquet(path_pq, index=False)

    print(f"  Writing {path_hetus} …")
    hetus_wide.to_csv(path_hetus, index=False)

    print("\n  Export complete.")
    print(f"    merged_episodes.csv     : {path_csv.stat().st_size / 1e6:.1f} MB")
    print(f"    merged_episodes.parquet : {path_pq.stat().st_size / 1e6:.1f} MB")
    print(f"    hetus_wide.csv          : {path_hetus.stat().st_size / 1e6:.1f} MB")


# BEM priority order for 3-way tie resolution (lower rank = higher priority).
# Reflects energy-model impact: sleep/home-stays have highest priority.
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
    4: 12,  # Purchasing Goods & Services ("Other")
    13: 13, # Travel
    14: 14, # Miscellaneous / Idle ("Missing/unknown")
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
                result[i, j] = np.nan  # 3-way tie sentinel (resolved in H.4)
    return result


# ── Phase H — Resolution Downsampling (144-slot → 48-slot) ───────────────────

def downsample_to_30min(hetus_wide_df: pd.DataFrame) -> pd.DataFrame:
    """Downsample HETUS 144-slot (10-min) format to 48-slot (30-min) format.

    Each 30-min slot is the majority vote of 3 consecutive 10-min source slots.
    AT_HOME uses binary majority (nansum >= 2). Activity ties use BEM priority.

    Args:
        hetus_wide_df: DataFrame from hetus_wide.csv (64,061 rows x 288+ cols).

    Returns:
        DataFrame with identity/demographic cols + act30_001..048 + hom30_001..048.
        Shape: (64,061, n_meta_cols + 96).
    """
    print("\n── Phase H: Resolution Downsampling 144→48 slots ───────────")
    input_path = Path("outputs_step3") / "hetus_wide.csv"
    df = pd.read_csv(input_path, low_memory=False)
    print(f"  Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    assert df.shape[0] == 64_061, f"Expected 64,061 rows, got {df.shape[0]}"

    # H.1b: Separate identity columns from slot columns
    SLOT_ACT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
    SLOT_HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]
    META_COLS = [c for c in df.columns if c not in SLOT_ACT_COLS + SLOT_HOME_COLS]

    print(f"  Activity slot cols : {len(SLOT_ACT_COLS)}")   # expect 144
    print(f"  AT_HOME slot cols  : {len(SLOT_HOME_COLS)}")   # expect 144
    print(f"  Meta/identity cols : {len(META_COLS)}")

    # H.1c: Extract activity matrix as numpy array
    act_arr = df[SLOT_ACT_COLS].to_numpy(dtype=float)  # shape (64061, 144)
    print(f"  Activity matrix shape: {act_arr.shape}")

    # H.1d: Extract AT_HOME matrix as numpy array
    hom_arr = df[SLOT_HOME_COLS].to_numpy(dtype=float)  # shape (64061, 144)
    print(f"  AT_HOME matrix shape: {hom_arr.shape}")

    # H.2a: Reshape activity array to (n × 48 × 3)
    n = act_arr.shape[0]
    act_3d = act_arr.reshape(n, 48, 3)  # each [i, j, :] = 3 source slots for slot j
    print(f"  Activity 3D shape: {act_3d.shape}")  # expect (64061, 48, 3)

    # H.2c: Apply nanmode to get act_30 with tie sentinels
    print("  Computing activity majority vote (may take ~1 min)...")
    act_30 = _nanmode_axis2(act_3d)  # shape (64061, 48)
    n_ties = int(np.isnan(act_30).sum())
    print(f"  3-way ties detected: {n_ties:,} ({100*n_ties/(n*48):.2f}% of all cells)")

    # H.3a: Reshape AT_HOME array to (n × 48 × 3)
    hom_3d = hom_arr.reshape(n, 48, 3)  # shape (64061, 48, 3)
    print(f"  AT_HOME 3D shape: {hom_3d.shape}")

    # H.3b: Compute AT_HOME binary majority vote
    valid_count = np.sum(~np.isnan(hom_3d), axis=2)  # how many non-NaN per window
    sum_home = np.nansum(hom_3d, axis=2)           # sum of 1s per window

    hom_30 = np.where(valid_count == 0, np.nan,
                      np.where(sum_home >= 2, 1.0, 0.0))       # shape (64061, 48)

    n_home_nan = int(np.isnan(hom_30).sum())
    print(f"  AT_HOME NaNs after vote: {n_home_nan}")  # expect 0

    # H.4a: Detect 3-way tie positions
    tie_mask = np.isnan(act_30)  # True where 3-way tie sentinel
    tie_positions = list(zip(*np.where(tie_mask)))  # list of (row_idx, slot_idx) tuples
    print(f"  Tie positions to resolve: {len(tie_positions):,}")

    # H.4b: Resolve ties using BEM priority order
    for (i, j) in tie_positions:
        source_vals = act_3d[i, j, :]
        non_nan_vals = source_vals[~np.isnan(source_vals)]
        # Pick the code with the lowest BEM_PRIORITY rank (most important)
        best_code = min(non_nan_vals, key=lambda v: BEM_PRIORITY.get(int(v), 999))
        act_30[i, j] = best_code

    # Confirm all ties resolved
    remaining_nan = int(np.isnan(act_30).sum())
    assert remaining_nan == 0, f"Still {remaining_nan} NaN in act_30 after tie resolution"
    print(f"  Ties resolved: {len(tie_positions):,} | Remaining NaN: {remaining_nan}")

    # H.5a: Build act30 DataFrame with Int16 dtype
    act30_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    act30_df = pd.DataFrame(act_30, columns=act30_cols).astype(pd.Int16Dtype())
    print(f"  act30_df shape: {act30_df.shape}")  # expect (64061, 48)

    # H.5b: Build hom30 DataFrame with Int8 dtype
    hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    hom30_df = pd.DataFrame(hom_30, columns=hom30_cols).astype(pd.Int8Dtype())
    print(f"  hom30_df shape: {hom30_df.shape}")  # expect (64061, 48)

    # H.5c: Concatenate meta + act30 + hom30
    hetus_30min = pd.concat(
        [df[META_COLS].reset_index(drop=True), act30_df, hom30_df],
        axis=1
    )
    print(f"  hetus_30min shape: {hetus_30min.shape}")
    # Expected: (64061, len(META_COLS) + 96)

    # H.6a: Write hetus_30min.csv
    output_path = Path("outputs_step3") / "hetus_30min.csv"
    print(f"\n  Writing {output_path} ...")
    hetus_30min.to_csv(output_path, index=False)
    size_mb = output_path.stat().st_size / 1e6
    print(f"  Done. File size: {size_mb:.1f} MB")
    return hetus_30min, n_ties


def validate_30min(hetus_30min: pd.DataFrame, n_ties: int) -> None:
    """Implement validation checks V1–V8 for the 30-min downsampled data.

    Args:
        hetus_30min: Downsampled DataFrame.
        n_ties: Count of 3-way ties encountered during activity processing.
    """
    import random
    print("\n── Phase H Validation (V1–V8) ─────────────────────────────")

    n = hetus_30min.shape[0]

    # V1 — Shape check
    assert n == 64_061, f"Row count wrong: {n}"
    act30_cols = [c for c in hetus_30min.columns if c.startswith("act30_")]
    hom30_cols = [c for c in hetus_30min.columns if c.startswith("hom30_")]
    assert len(act30_cols) == 48, f"Expected 48 act30 cols, got {len(act30_cols)}"
    assert len(hom30_cols) == 48, f"Expected 48 hom30 cols, got {len(hom30_cols)}"
    print("V1 PASS — shape (64061, 96 act/home cols)")

    # V2 — Zero NaN in act30 and hom30
    nan_act = hetus_30min[act30_cols].isna().sum().sum()
    nan_hom = hetus_30min[hom30_cols].isna().sum().sum()
    assert nan_act == 0, f"NaN in act30: {nan_act}"
    assert nan_hom == 0, f"NaN in hom30: {nan_hom}"
    print(f"V2 PASS — NaN act30={nan_act}, hom30={nan_hom}")

    # V3 — Activity distribution vs hetus_wide within ±1 pp
    hetus_wide = pd.read_csv("outputs_step3/hetus_wide.csv", low_memory=False)
    slot_cols = [f"slot_{i:03d}" for i in range(1, 145)]
    wide_vals = hetus_wide[slot_cols].to_numpy().flatten()
    new_vals = hetus_30min[act30_cols].to_numpy().flatten()

    print("\nV3 — Activity distribution comparison:")
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
    print(f"V3 {'PASS' if all_pass else 'FAIL'} — all categories within ±1 pp: {all_pass}")

    # V4 — Weighted AT_HOME rate per cycle within ±1 pp
    # Compare against hetus_wide ground truth per cycle.
    hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    hom144_cols = [f"home_{i:03d}" for i in range(1, 145)]
    print("\nV4 — Weighted AT_HOME rate preservation vs hetus_wide:")
    print(f"  {'Cycle':>6} | {'wide%':>10} | {'30min%':>10} | {'diff_pp':>8} | Status")
    all_pass_v4 = True
    for cycle in sorted(hetus_30min["CYCLE_YEAR"].unique()):
        # 30-min rate
        mask_30 = hetus_30min["CYCLE_YEAR"] == cycle
        sub_30 = hetus_30min[mask_30]
        w_30 = sub_30["WGHT_PER"]
        home_30_vals = sub_30[hom30_cols].to_numpy(dtype=float)
        wtd_rate_30 = 100 * np.average(home_30_vals.flatten(), weights=np.repeat(w_30.values, 48))

        # 10-min rate (ground truth)
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
    print(f"V4 {'PASS' if all_pass_v4 else 'FAIL'} — AT_HOME rates within ±1 pp vs wide: {all_pass_v4}")

    # V5 — Night slot plausibility (slots 1–8: 04:00–07:59 AM)
    sleep_code = [k for k, v in BEM_PRIORITY.items() if v == 1][0]
    night_act_cols = [f"act30_{i:03d}" for i in range(1, 9)]
    night_hom_cols = [f"hom30_{i:03d}" for i in range(1, 9)]
    night_act_vals = hetus_30min[night_act_cols].to_numpy().flatten()
    night_hom_vals = hetus_30min[night_hom_cols].to_numpy(dtype=float).flatten()
    sleep_pct = 100 * (night_act_vals == sleep_code).mean()
    athome_pct = 100 * np.nanmean(night_hom_vals)

    print(f"\nV5 — Night slots (1–8, 04:00–07:59):")
    print(f"  Sleep rate  : {sleep_pct:.1f}%  (threshold ≥ 70%)  → {'PASS' if sleep_pct >= 70 else 'FAIL'}")
    print(f"  AT_HOME rate: {athome_pct:.1f}% (threshold ≥ 85%)  → {'PASS' if athome_pct >= 85 else 'FAIL'}")

    # V6 — 3-way tie rate < 5%
    total_cells = n * 48
    tie_rate_pct = 100 * n_ties / total_cells
    print(f"\nV6 — 3-way tie rate: {n_ties:,} / {total_cells:,} = {tie_rate_pct:.2f}%")
    assert tie_rate_pct < 5.0, f"Tie rate {tie_rate_pct:.2f}% exceeds 5% threshold"
    print(f"V6 PASS — tie rate < 5%")

    # V7 — DDAY_STRATA distribution unchanged
    dist_wide = hetus_wide["DDAY_STRATA"].value_counts().sort_index()
    dist_30 = hetus_30min["DDAY_STRATA"].value_counts().sort_index()
    match = dist_wide.equals(dist_30)
    print(f"\nV7 — DDAY_STRATA distribution match: {'PASS' if match else 'FAIL'}")

    # V8 — Manual spot-check 5 random respondents
    random.seed(42)
    sample_indices = random.sample(range(n), 5)
    print("\nV8 — Manual spot-check (5 random respondents, first 6 slots shown):")
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


# ── Phase I — Co-Presence Tiling (episode → 48-slot 30-min format) ───────────

COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues"
]

def tile_copresence_to_30min() -> pd.DataFrame:
    """Tile episode-level co-presence columns to 30-min slot wide format.

    Reads merged_episodes.csv and hetus_30min.csv (for occID order).
    Applies the same two-stage tiling as Phase F+H: episode → 144-slot 10-min
    intermediate → 48-slot 30-min via binary majority vote.

    Returns:
        DataFrame: 64,061 rows × 433 cols (occID + 9×48 co-presence slots).
        Values: 1=present, 2=absent, pd.NA for NaN slots.
        Output: outputs_step3/copresence_30min.csv
    """
    print("\n── Phase I: Co-Presence Tiling (episode → 30-min slots) ──────")
    ep_path = Path("outputs_step3") / "merged_episodes.csv"
    episodes = pd.read_csv(ep_path, low_memory=False)
    print(f"  Loaded: {len(episodes):,} episode rows")

    # Verify required columns
    required_cols = ["occID", "startMin", "endMin", "CYCLE_YEAR"] + COP_COLS
    missing = [c for c in required_cols if c not in episodes.columns]
    assert not missing, f"Missing columns: {missing}"

    n_unique_occ = episodes.groupby(["occID", "CYCLE_YEAR"]).ngroups
    print(f"  Unique (occID, CYCLE_YEAR) in episodes: {n_unique_occ:,}")  # expect 64,061

    ref_path = Path("outputs_step3") / "hetus_30min.csv"
    ref_df = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    occid_order = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
    occid_to_idx = {oid_cyc: i for i, oid_cyc in enumerate(occid_order)}
    n = len(occid_order)
    print(f"  Reference order loaded: {n:,} respondents")
    assert n == 64_061, f"Expected 64,061, got {n}"

    # One float64 array per co-presence column
    cop_10min = {col: np.full((n, 144), np.nan, dtype=float) for col in COP_COLS}
    print(f"  Pre-allocated 9 arrays of shape ({n}, 144)")

    # Sort by CYCLE_YEAR and occID for sequential group access
    episodes_sorted = episodes.sort_values(["CYCLE_YEAR", "occID"]).reset_index(drop=True)

    # Build group boundary index: (occid, cycle) → (start_row, end_row)
    grp = episodes_sorted.groupby(["occID", "CYCLE_YEAR"], sort=False)
    grp_indices = {k: (grp.indices[k].min(), grp.indices[k].max() + 1)
                   for k in grp.groups}
    print(f"  Episode group index built for {len(grp_indices):,} respondents")

    # Extract needed arrays for speed
    start_mins   = episodes_sorted["startMin"].to_numpy(dtype=float)
    durations    = episodes_sorted["duration"].to_numpy(dtype=float)
    cop_vals     = {col: episodes_sorted[col].to_numpy(dtype=float) for col in COP_COLS}

    print("  Tiling episodes to 10-min slots...")
    for resp_idx, key in enumerate(occid_order):
        if resp_idx > 0 and resp_idx % 10_000 == 0:
            print(f"    {resp_idx:,} / {n:,}")
        if key not in grp_indices:
            continue  # no episodes
        row_start, row_end = grp_indices[key]
        for ep_row in range(row_start, row_end):
            s_min = start_mins[ep_row]
            dur = durations[ep_row]
            
            # Shift to 4:00 AM origin
            start_shifted = (int(s_min) - 240) % 1440
            end_shifted = min(start_shifted + int(dur), 1440)
            
            slot_s = start_shifted // 10
            slot_e = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0
            
            slot_e = min(slot_e, 144)        # clamp to array bounds
            for col in COP_COLS:
                val = cop_vals[col][ep_row]
                if not np.isnan(val):
                    cop_10min[col][resp_idx, slot_s:slot_e] = val

    print("  Tiling complete.")

    cop_3d = {}
    for col in COP_COLS:
        cop_3d[col] = cop_10min[col].reshape(n, 48, 3)
        # Shape check
        assert cop_3d[col].shape == (n, 48, 3), f"Reshape failed for {col}"
    print("  Reshaped all 9 arrays to (64061, 48, 3)")

    cop_30 = {}
    for col in COP_COLS:
        arr = cop_3d[col]
        valid_count = np.sum(~np.isnan(arr), axis=2)         # (n, 48): non-NaN count
        sum_present = np.nansum(arr == 1.0, axis=2).astype(float)  # count of "1" per window

        result = np.where(valid_count == 0, np.nan,
                 np.where(sum_present >= 2, 1.0, 2.0))       # 1 if majority present, else 2
        cop_30[col] = result

        nan_count = int(np.isnan(result).sum())
        print(f"  {col}: NaN slots = {nan_count:,} ({100*nan_count/(n*48):.2f}%)")

    cop30_dfs = []
    for col in COP_COLS:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        df_col = pd.DataFrame(cop_30[col], columns=slot_cols)
        # Cast to nullable Int8 (supports NaN)
        for c in slot_cols:
            df_col[c] = df_col[c].astype(pd.Int8Dtype())
        cop30_dfs.append(df_col)
        print(f"  {col}: built DataFrame {df_col.shape}")

    occid_col = pd.DataFrame({"occID": [k[0] for k in occid_order]})
    copresence_30min = pd.concat([occid_col] + cop30_dfs, axis=1)
    print(f"  copresence_30min shape: {copresence_30min.shape}")
    # Expected: (64061, 433) — 1 occID + 9×48 = 433
    assert copresence_30min.shape == (64_061, 433), f"Shape mismatch: {copresence_30min.shape}"

    out_path = Path("outputs_step3") / "copresence_30min.csv"
    print(f"\n  Writing {out_path} ...")
    copresence_30min.to_csv(out_path, index=False)
    size_mb = out_path.stat().st_size / 1e6
    print(f"  Done. File size: {size_mb:.1f} MB")
    return copresence_30min

def validate_copresence_30min_export(copresence_30min: pd.DataFrame, occid_order: list[int]) -> None:
    print("\n── Phase I Validation (VI-1–7) ─────────────────────────────")
    # VI-1: Shape check
    assert copresence_30min.shape[0] == 64_061, f"Row count: {copresence_30min.shape[0]}"
    assert copresence_30min.shape[1] == 433, f"Col count: {copresence_30min.shape[1]}"
    print("VI-1 PASS — shape (64061, 433)")

    # VI-2: occID alignment with hetus_30min
    hetus_occids = pd.read_csv("outputs_step3/hetus_30min.csv", usecols=["occID"])["occID"]
    match = copresence_30min["occID"].equals(hetus_occids)
    assert match, "occID mismatch between copresence_30min and hetus_30min"
    print("VI-2 PASS — occID order matches hetus_30min exactly")

    # VI-3: No all-NaN respondents for primary 8 columns
    primary_cols = [c for c in COP_COLS if c != "colleagues"]
    for col in primary_cols:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        all_nan_mask = copresence_30min[slot_cols].isna().all(axis=1)
        n_all_nan = all_nan_mask.sum()
        if n_all_nan > 0:
            print(f"VI-3 WARN — {col}: {n_all_nan} respondents have all-NaN across 48 slots (reflects source data missingness)")
        else:
            print(f"VI-3 PASS — {col}: no all-NaN respondents")

    # VI-4: colleagues NaN pattern by cycle
    ref_df = pd.read_csv("outputs_step3/hetus_30min.csv", usecols=["occID", "CYCLE_YEAR"])
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
    print(f"VI-5 PASS — all non-NaN values ∈ {{1, 2}}")

    # VI-6: Co-presence prevalence plausibility
    for col, low, high in [("Alone", 30, 60), ("Spouse", 15, 45)]:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        vals = copresence_30min[slot_cols].to_numpy(dtype=float, na_value=np.nan)
        pct_present = 100 * np.nanmean(vals == 1)
        status = "PASS" if low <= pct_present <= high else "WARN"
        print(f"VI-6 {col}: {pct_present:.1f}% present (expected {low}–{high}%) → {status}")

    # VI-7: Manual spot-check 5 random respondents
    import random
    random.seed(42)
    episodes_chk = pd.read_csv("outputs_step3/merged_episodes.csv", low_memory=False)
    sample_ids = random.sample(occid_order, 5)
    print("\nVI-7 — Manual spot-check (Alone30_001, slot 1 = 04:00–04:29)")
    for key in sample_ids:
        occ_id, cycle = key
        ep_sub = episodes_chk[(episodes_chk["occID"] == occ_id) & (episodes_chk["CYCLE_YEAR"] == cycle)].copy()
        # Episodes overlapping 04:00-04:29 (minutes 240-269 from midnight)
        # Note: endMin=0 or <240 means it wrapped to next day
        covering = ep_sub[((ep_sub["startMin"] <= 269) & (ep_sub["endMin"] > 240)) | (ep_sub["endMin"] <= 30)]
        src_vals = covering["Alone"].tolist()
        idx = occid_order.index(key)
        alone30_001 = copresence_30min.iloc[idx]["Alone30_001"]
        print(f"  occID={occ_id}, CYCLE={cycle}: source episode Alone vals near 04:00 = {src_vals} → Alone30_001 = {alone30_001}")
    print("VI-7 — Review output above manually to confirm majority vote is correct.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the full Step 3 pipeline."""
    print("=" * 60)
    print("Step 3 — Merge & Temporal Feature Derivation")
    print("=" * 60)

    # Phase A+B: Load & stack
    print("\n── Phase A+B: Load & Stack ─────────────────────────────────")
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

    # Phase F: HETUS conversion
    hetus_wide = build_hetus_wide(merged_final)

    # Phase G: Export
    export_all(merged_final, hetus_wide, OUTPUT_DIR)

    # Phase H: Resolution downsampling
    hetus_30min, n_ties = downsample_to_30min(hetus_wide)

    # H.6b: Print post-export summary
    print(f"\n── Phase H Summary ──────────────────────────────────────────")
    print(f"  Rows            : {hetus_30min.shape[0]:,}")
    print(f"  Total columns   : {hetus_30min.shape[1]}")
    print(f"  act30 columns   : {len([c for c in hetus_30min.columns if c.startswith('act30_')])}")
    print(f"  hom30 columns   : {len([c for c in hetus_30min.columns if c.startswith('hom30_')])}")
    print(f"  NaN in act30    : {hetus_30min[[c for c in hetus_30min.columns if c.startswith('act30_')]].isna().sum().sum()}")
    print(f"  NaN in hom30    : {hetus_30min[[c for c in hetus_30min.columns if c.startswith('hom30_')]].isna().sum().sum()}")

    # Group 6: Validation
    validate_30min(hetus_30min, n_ties)

    # Phase I: Co-presence tiling
    copresence_30min = tile_copresence_to_30min()

    # H.6b / I.6b: Print post-export summary for co-presence
    print(f"\n── Phase I Summary ──────────────────────────────────────────")
    print(f"  Rows             : {copresence_30min.shape[0]:,}")
    print(f"  Total columns    : {copresence_30min.shape[1]}")
    for col in COP_COLS:
        slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
        nan_total = copresence_30min[slot_cols].isna().sum().sum()
        print(f"  {col:>14}: NaN slots = {nan_total:,}")

    # Validate Phase I
    ref_df = pd.read_csv("outputs_step3/hetus_30min.csv", usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    occ_cyc = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
    validate_copresence_30min_export(copresence_30min, occ_cyc)

    print("\n" + "=" * 60)
    print("Step 3 complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
