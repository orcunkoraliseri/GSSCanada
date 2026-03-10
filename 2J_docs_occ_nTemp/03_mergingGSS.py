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
    "MODE",
    "NOCS",          # 2015/2022 only → NaN for 2005/2010
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

    # HOUR_OF_DAY (0–23)
    df["HOUR_OF_DAY"] = (df["startMin"] // 60).astype(int)

    # TIMESLOT_10: HETUS 10-min slot (1–144, 4 AM origin)
    df["TIMESLOT_10"] = _hhmm_to_hetus_slot(df["start"])

    derived_cols = ["DAYTYPE", "startMin", "HOUR_OF_DAY", "TIMESLOT_10", "DDAY_STRATA"]
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
        "MODE", "NOCS", "TOTINC_SOURCE", "SURVYEAR",
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

    print("\n" + "=" * 60)
    print("Step 3 complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
