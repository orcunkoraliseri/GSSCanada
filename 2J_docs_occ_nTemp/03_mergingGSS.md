# Step 3 — Merge & Temporal Feature Derivation: Implementation Plan

## Goal

Merge the eight harmonized Step 2 CSV files (4 Main + 4 Episode) into a single unified occupancy dataset, derive temporal features for downstream modeling, and convert variable-length episode data into the HETUS 144-slot wide format required by the Conditional Transformer (Step 4).

**Input directory**: `outputs_step2/`
**Output directory**: `outputs_step3/`

---

## Pre-Conditions (from Step 2)

### Available Harmonized Files

| File | Rows | Columns |
|------|------|---------|
| `main_2005.csv` | 19,597 | 25 |
| `main_2010.csv` | 15,390 | 36 |
| `main_2015.csv` | 17,390 | 36 |
| `main_2022.csv` | 12,336 | 32 |
| `episode_2005.csv` | 333,654 | 24 |
| `episode_2010.csv` | 283,287 | 24 |
| `episode_2015.csv` | 274,108 | 27 |
| `episode_2022.csv` | 168,078 | 25 |

Step 2 harmonized all four cycles into a unified schema: column names, category encodings, missing-value conventions, and metadata flags are consistent across cycles. Each cycle's file contains the harmonized core columns plus some cycle-specific extras (e.g., CTW checkbox columns, REGION in 2010) that are not needed for Step 3. Phase A below selects only the common harmonized columns and drops the extras.

---

## Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════╗
║  Phase A — Column Standardization                                    ║
║  Select harmonized common columns from each Main/Episode file       ║
║  Drop cycle-specific extras; ensure identical schemas for stacking  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Phase B — Vertical Stacking (Append All Cycles)                    ║
║  Stack 4 Main files → unified_main (~64,713 respondents)           ║
║  Stack 4 Episode files → unified_episode (~1.06M episodes)         ║
╠══════════════════════════════════════════════════════════════════════╣
║  Phase C — LEFT JOIN (Episode ← Main on occID + CYCLE_YEAR)        ║
║  Result: one row per episode, carrying full demographic context    ║
╠══════════════════════════════════════════════════════════════════════╣
║  Phase D — DIARY_VALID Filtering                                    ║
║  Remove respondents with DIARY_VALID == 0 (corrupted diaries)      ║
╠══════════════════════════════════════════════════════════════════════╣
║  Phase E — Temporal Feature Derivation                              ║
║  Derive: DAYTYPE, HOUR_OF_DAY, TIMESLOT_10                        ║
╠══════════════════════════════════════════════════════════════════════╣
║  Phase F — HETUS 144-Slot Wide Format Conversion                   ║
║  Variable-length episodes → 144 fixed 10-min slots per respondent  ║
║  Output: one row per respondent with slot_001–slot_144 columns     ║
╠══════════════════════════════════════════════════════════════════════╣
║  Phase G — Export                                                    ║
║  Save merged episode-level CSV + HETUS wide-format CSV             ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Phase A — Column Standardization

### A1. Define Common Main Columns

Select only the harmonized common columns that exist across all 4 cycles. Drop cycle-specific extras (CTW checkboxes, REGION, raw employment codes, etc.).

```python
MAIN_COMMON_COLS = [
    "occID", "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR", "CMA",
    "WGHT_PER", "DDAY", "KOL", "LFTAG", "TOTINC", "HRSWRK",
    "MODE", "NOCS",
    # Metadata flags
    "TOTINC_SOURCE", "CYCLE_YEAR", "SURVYEAR",
    "COLLECT_MODE", "TUI_10_AVAIL", "BS_TYPE"
]
```

> **Note**: `HRSWRK_RAW` and `TOTINC_RAW` are preserved-for-reference columns from Step 2. They should be **dropped** at this stage — the harmonized `HRSWRK` and `TOTINC` are the analysis-ready versions. `NOCS` is only available in 2015/2022 — fill with `NaN` for 2005/2010.

### A2. Define Common Episode Columns

```python
EPISODE_COMMON_COLS = [
    "occID", "EPINO", "WGHT_EPI",
    "start", "end", "duration",
    "occACT_raw", "occACT", "occACT_label",
    "occPRE_raw", "occPRE", "AT_HOME",
    # Co-presence
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others",
    # QA
    "DIARY_VALID", "CYCLE_YEAR"
]
```

> **Note**: `TUI_07` (tech use) and `TUI_10`/`TUI_15` (wellbeing) are only in 2015/2022 episode files. Per pipeline design, `TUI_10` is an auxiliary variable flagged by `TUI_10_AVAIL`. We include `TUI_07` as an optional column — present for 2015/2022, `NaN` for 2005/2010.

### A3. Handle Missing Columns Gracefully

For each cycle's file, select only columns that exist. Fill missing columns with `NaN`. This avoids errors when a column (e.g., `NOCS`, `TUI_07`) is absent from certain cycles.

```python
def standardize_columns(df, target_cols):
    """Select target_cols from df; add NaN for any missing."""
    for col in target_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df[target_cols]
```

---

## Phase B — Vertical Stacking

### B1. Stack Main Files

```python
main_dfs = []
for cycle in [2005, 2010, 2015, 2022]:
    df = pd.read_csv(f"outputs_step2/main_{cycle}.csv")
    df = standardize_columns(df, MAIN_COMMON_COLS)
    main_dfs.append(df)
unified_main = pd.concat(main_dfs, ignore_index=True)
```

**Expected result**: ~64,713 rows (19,597 + 15,390 + 17,390 + 12,336)

### B2. Stack Episode Files

```python
episode_dfs = []
for cycle in [2005, 2010, 2015, 2022]:
    df = pd.read_csv(f"outputs_step2/episode_{cycle}.csv")
    df = standardize_columns(df, EPISODE_COMMON_COLS)
    episode_dfs.append(df)
unified_episode = pd.concat(episode_dfs, ignore_index=True)
```

**Expected result**: ~1,059,128 rows (333,654 + 283,287 + 274,108 + 168,079)

### B3. Post-Stack Integrity Checks

- Assert no duplicate `(occID, CYCLE_YEAR)` pairs in `unified_main`
- Assert `unified_episode.CYCLE_YEAR.value_counts()` matches per-cycle row counts

> **occID collision note**: occIDs are unique *within* each cycle but may collide *across* cycles (e.g., respondent 1 in 2005 ≠ respondent 1 in 2010). The merge key must be `(occID, CYCLE_YEAR)`, not `occID` alone.

---

## Phase C — LEFT JOIN (Episode ← Main)

### C1. Merge Strategy

```python
merged = unified_episode.merge(
    unified_main,
    on=["occID", "CYCLE_YEAR"],
    how="left",
    validate="many_to_one"   # Many episodes per respondent
)
```

**Join key**: `(occID, CYCLE_YEAR)` — required because occIDs are only unique within a cycle.

**Expected result**: Same row count as `unified_episode` (~1.06M rows). Each episode row now carries the respondent's full demographic profile.

### C2. Post-Merge Checks

- Assert `len(merged) == len(unified_episode)` (no row gain/loss from LEFT JOIN)
- Assert `merged.WGHT_PER.notna().all()` — every episode matched a Main record
- If any episodes fail to match (orphan episodes), log them and investigate

### C3. Weight Column Clarity

After merge, both `WGHT_EPI` (episode-level) and `WGHT_PER` (person-level) are present on every row:
- **Episode-level analyses** (activity distributions, time allocation): use `WGHT_EPI`
- **Person-level analyses** (demographic summaries, archetype clustering): use `WGHT_PER`

No weight derivation needed — both are carried forward as-is from Statistics Canada.

---

## Phase D — DIARY_VALID Filtering

### D1. Filter Corrupted Diaries

```python
n_before = merged.occID.nunique()
merged = merged[merged["DIARY_VALID"] == 1]
n_after = merged.occID.nunique()
print(f"Removed {n_before - n_after} respondents with invalid diaries")
```

Per Statistics Canada QA rules, respondents whose episodes do not sum to exactly 1440 minutes cannot be validly converted to HETUS 144-slot format.

### D2. Log Exclusions

Record per-cycle counts of excluded respondents. Expected exclusion rate: <5% per cycle (most diaries close correctly under CATI/EQ collection protocols).

---

## Phase E — Temporal Feature Derivation

### E1. DAYTYPE (from DDAY)

```python
# GSS DDAY: 1=Sunday, 2=Monday, ..., 7=Saturday
DAYTYPE_MAP = {
    1: "Weekend",   # Sunday
    2: "Weekday",   # Monday
    3: "Weekday",   # Tuesday
    4: "Weekday",   # Wednesday
    5: "Weekday",   # Thursday
    6: "Weekday",   # Friday
    7: "Weekend"    # Saturday
}
merged["DAYTYPE"] = merged["DDAY"].map(DAYTYPE_MAP)
```

> **DDAY methodological note**: DDAY is the diary reference day (the day BEFORE the interview). The 24-hour diary reconstructs this completed prior day (4:00 AM to 4:00 AM next day). Each sequence is a complete, verified 1440-minute record.

### E2. HOUR_OF_DAY (from start time)

The `start` column is in HHMM 24-hour format (e.g., 0400, 1330, 2350).

```python
def parse_hhmm_to_minutes(hhmm_series):
    """Convert HHMM integers to minutes from midnight."""
    hh = hhmm_series // 100
    mm = hhmm_series % 100
    return hh * 60 + mm

merged["startMin"] = parse_hhmm_to_minutes(merged["start"])
merged["HOUR_OF_DAY"] = merged["startMin"] // 60  # 0–23
```

### E3. TIMESLOT_10 — HETUS 10-Minute Slot Index

The HETUS standard uses 144 ten-minute slots starting at 4:00 AM (slot 1 = 04:00–04:09, slot 144 = 03:50–03:59 next day).

```python
def hhmm_to_slot(hhmm_series):
    """Convert HHMM to HETUS slot index (1–144), 4:00 AM origin."""
    hh = hhmm_series // 100
    mm = hhmm_series % 100
    total_min = hh * 60 + mm
    # Shift origin to 4:00 AM (240 minutes from midnight)
    shifted = (total_min - 240) % 1440
    slot = shifted // 10 + 1   # 1-indexed
    return slot

merged["TIMESLOT_10"] = hhmm_to_slot(merged["start"])
```

### E4. DDAY_STRATA

A day-of-week stratum identifier for downstream modeling:

```python
merged["DDAY_STRATA"] = merged["DDAY"].astype(int)  # values 1–7
```

### E5. Summary of Derived Columns

| Column | Source | Logic | Range |
|--------|--------|-------|-------|
| `DAYTYPE` | `DDAY` | Day → Weekday/Weekend | Weekday/Weekend |
| `startMin` | `start` | HHMM → minutes from midnight | 0–1439 |
| `HOUR_OF_DAY` | `startMin` | Minutes → hour | 0–23 |
| `TIMESLOT_10` | `start` | HHMM → HETUS slot (4 AM origin) | 1–144 |
| `DDAY_STRATA` | `DDAY` | Day-of-week stratum | 1–7 |

---

## Phase F — HETUS 144-Slot Wide Format Conversion

### F1. Purpose

Each respondent's variable-length episode sequence is redistributed into 144 fixed 10-minute slots. This produces the fixed-length input sequence required by the Conditional Transformer in Step 4.

**Input**: Episode-level merged data (~1.06M rows, variable episodes per respondent)
**Output**: One row per respondent with columns `slot_001` through `slot_144`, each containing the `occACT` activity code for that 10-minute interval.

### F2. Slot Assignment Algorithm

```python
def episodes_to_144_slots(respondent_episodes):
    """
    Convert a respondent's episodes to 144 ten-minute activity slots.

    Diary day runs from 4:00 AM (slot 1) to 3:59 AM next day (slot 144).
    Each slot is assigned the occACT of the episode covering that interval.

    Args:
        respondent_episodes: DataFrame of episodes for one occID,
                            sorted by EPINO (episode order).

    Returns:
        dict: {slot_001: occACT, slot_002: occACT, ..., slot_144: occACT}
    """
    slots = {}
    for _, ep in respondent_episodes.iterrows():
        start_hhmm = ep["start"]
        end_hhmm = ep["end"]
        act = ep["occACT"]

        start_min = (start_hhmm // 100) * 60 + (start_hhmm % 100)

        # Shift start to 4:00 AM origin (HETUS standard)
        start_shifted = (start_min - 240) % 1440

        # Duration-based end: avoids double-wrap errors for episodes crossing
        # both midnight AND the 4:00 AM diary boundary (e.g., sleep 23:35->04:00).
        # end HHMM cannot be used directly because two consecutive modulo operations
        # collapse the shifted end time to a value less than start_shifted.
        end_shifted = min(start_shifted + ep["duration"], 1440)

        # Assign activity to each 10-min slot covered
        slot_start = start_shifted // 10  # 0-indexed
        slot_end = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0

        for s in range(slot_start, min(slot_end, 144)):
            slot_key = f"slot_{s+1:03d}"  # 1-indexed, zero-padded
            slots[slot_key] = act

    return slots
```

### F3. Build Wide-Format DataFrame

```python
hetus_rows = []
for (occ_id, cycle), group in merged.groupby(["occID", "CYCLE_YEAR"]):
    group_sorted = group.sort_values("EPINO")
    slot_dict = episodes_to_144_slots(group_sorted)
    slot_dict["occID"] = occ_id
    slot_dict["CYCLE_YEAR"] = cycle
    hetus_rows.append(slot_dict)

hetus_wide = pd.DataFrame(hetus_rows)
```

### F4. Attach Demographic & Temporal Context

Merge the respondent-level attributes back onto the wide-format rows:

```python
# Take one row per respondent from the merged episode data
respondent_attrs = merged.groupby(["occID", "CYCLE_YEAR"]).first().reset_index()

# Select person-level columns (not episode-level)
PERSON_COLS = [
    "occID", "CYCLE_YEAR", "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR",
    "CMA", "WGHT_PER", "DDAY", "KOL", "LFTAG", "TOTINC", "HRSWRK",
    "MODE", "NOCS", "TOTINC_SOURCE", "SURVYEAR",
    "COLLECT_MODE", "TUI_10_AVAIL", "BS_TYPE",
    # Derived temporal
    "DAYTYPE", "DDAY_STRATA"
]

hetus_final = hetus_wide.merge(
    respondent_attrs[PERSON_COLS],
    on=["occID", "CYCLE_YEAR"],
    how="left"
)
```

### F5. AT_HOME Slot Array (Parallel)

In addition to activity slots, create a parallel 144-slot array for home presence:

```python
def episodes_to_144_athome(respondent_episodes):
    """Same logic as episodes_to_144_slots but uses AT_HOME (0/1)."""
    slots = {}
    for _, ep in respondent_episodes.iterrows():
        # ... same time conversion ...
        for s in range(slot_start, min(slot_end, 144)):
            slot_key = f"home_{s+1:03d}"
            slots[slot_key] = ep["AT_HOME"]
    return slots
```

This produces columns `home_001`–`home_144` alongside `slot_001`–`slot_144`.

---

## Phase G — Export

### G1. Output Files

| File | Description | Approx Size |
|------|-------------|-------------|
| `outputs_step3/merged_episodes.csv` | Full episode-level merged dataset with derived features | ~228 MB |
| `outputs_step3/merged_episodes.parquet` | Same as above in Parquet for efficient downstream loading | ~15 MB |
| `outputs_step3/hetus_wide.csv` | 144-slot wide format + AT_HOME slots + demographics (one row per respondent) | ~83 MB |

> **Note**: The AT_HOME slot columns (`home_001`–`home_144`) are included in the same `hetus_wide.csv` file alongside `slot_001`–`slot_144`, rather than a separate file, to keep a single respondent-level output.

> **Note on file sizes**: Actual sizes depend on the post-`DIARY_VALID` respondent count (64,061 after 652 exclusions) and cycle-specific sample sizes (2022: 12,336 instead of the ~17,000 originally assumed). `merged_episodes.csv` is smaller than initially estimated because integer-coded categorical columns compress efficiently in CSV. `hetus_wide.csv` is larger than estimated because it carries 288+ columns (144 activity slots + 144 AT_HOME slots + demographics) per respondent row.

---

## Implementation Details

### File Structure

```
2J_docs_occ_nTemp/
├── 03_mergingGSS.py           # Main merge & feature derivation script
├── 03_mergingGSS_val.py       # Validation & HTML report generation
├── 03_mergingGSS.md           # This implementation plan
├── 03_mergingGSS_val.md       # Validation implementation plan
├── outputs_step2/             # Input (from Step 2)
│   ├── main_2005.csv
│   ├── main_2010.csv
│   ├── main_2015.csv
│   ├── main_2022.csv
│   ├── episode_2005.csv
│   ├── episode_2010.csv
│   ├── episode_2015.csv
│   └── episode_2022.csv
└── outputs_step3/             # Output
    ├── merged_episodes.csv
    ├── merged_episodes.parquet
    ├── hetus_wide.csv
    └── step3_validation_report.html
```

### Script Structure: `03_mergingGSS.py`

```python
"""Step 3 — Merge & Temporal Feature Derivation.

Merges harmonized Step 2 outputs (Main + Episode) into a unified dataset,
derives temporal features, and converts to HETUS 144-slot wide format.
"""

# ── Constants ────────────────────────────────────────────────
INPUT_DIR, OUTPUT_DIR, CYCLES
MAIN_COMMON_COLS, EPISODE_COMMON_COLS

# ── Helper Functions ─────────────────────────────────────────
standardize_columns(df, target_cols)
parse_hhmm_to_minutes(hhmm_series)
hhmm_to_slot(hhmm_series)

# ── Phase A+B: Load & Stack ─────────────────────────────────
load_and_stack_main(input_dir) → unified_main
load_and_stack_episodes(input_dir) → unified_episode

# ── Phase C: Merge ───────────────────────────────────────────
merge_main_episode(unified_main, unified_episode) → merged

# ── Phase D: Filter ──────────────────────────────────────────
filter_invalid_diaries(merged) → merged_valid, exclusion_report

# ── Phase E: Derive ──────────────────────────────────────────
derive_temporal_features(merged) → merged_with_features

# ── Phase F: HETUS Conversion ────────────────────────────────
episodes_to_144_slots(respondent_episodes) → slot_dict
episodes_to_144_athome(respondent_episodes) → home_dict
build_hetus_wide(merged) → hetus_wide

# ── Phase G: Export ──────────────────────────────────────────
export_all(merged, hetus_wide, output_dir)

# ── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
```

### Performance Considerations

The HETUS 144-slot conversion (Phase F) iterates over ~64K respondents, each with ~16 episodes on average. Naive row-by-row `iterrows()` will be slow.

**Optimization strategies**:
1. **Vectorized slot assignment**: Instead of iterating rows, compute slot indices for all episodes at once using vectorized operations, then pivot.
2. **GroupBy + apply**: Use `groupby(["occID", "CYCLE_YEAR"]).apply(episodes_to_144_slots)` with an optimized inner function.
3. **NumPy pre-allocation**: Pre-allocate a `(n_respondents, 144)` NumPy array and fill slots via index assignment.

Estimated runtime: ~2–5 minutes on a modern laptop (vectorized approach).

---

## Edge Cases & Known Issues

### 1. Midnight Wrap in Start/End Times
GSS diary days run from 4:00 AM to 3:59 AM. Episodes crossing midnight (e.g., sleep from 23:00 to 07:00) have `end < start` in HHMM format. The slot conversion must handle this wrap correctly by adding 1440 minutes to `end` when `end <= start`.

### 2. occID Collisions Across Cycles
Respondent IDs (occID) are assigned independently per survey cycle. The same integer ID may appear in multiple cycles referring to different people. All merge/groupby operations must use `(occID, CYCLE_YEAR)` as the composite key.

### 3. Episode Gaps in HETUS Slots
If an episode's start/end times don't perfectly tile the 10-minute grid, some slots may be assigned by the episode that *starts before* the slot boundary. The algorithm assigns based on which episode covers the slot's start time. This is standard HETUS practice.

### 4. Duration Column vs. HHMM Calculation
Duration is used as the **primary** input for end-slot computation, not `end` HHMM. The `end` HHMM column is not read during slot assignment. This decision was made to avoid double-wrap errors for episodes that cross both midnight (end < start in HHMM space) and the 4:00 AM diary boundary simultaneously. Using `end_shifted = min(start_shifted + duration, 1440)` is both correct and more robust.

---

## Dependency Diagram

```mermaid
graph TD
    A["Phase A: Column Standardization"] --> B["Phase B: Vertical Stacking"]
    B --> C["Phase C: LEFT JOIN (Episode ← Main)"]
    C --> D["Phase D: DIARY_VALID Filtering"]
    D --> E["Phase E: Temporal Feature Derivation"]
    D --> F["Phase F: HETUS 144-Slot Conversion"]
    E --> G["Phase G: Export"]
    F --> G
```

> **Note**: Phases E and F are independent of each other (both depend on D). They can be developed and tested in parallel.

---

## Checklist (for progress tracking)

### Phase A — Column Standardization
- [ ] A1. Define `MAIN_COMMON_COLS` constant
- [ ] A2. Define `EPISODE_COMMON_COLS` constant
- [ ] A3. Implement `standardize_columns()` helper

### Phase B — Vertical Stacking
- [ ] B1. Stack 4 Main files
- [ ] B2. Stack 4 Episode files
- [ ] B3. Post-stack integrity checks

### Phase C — LEFT JOIN
- [ ] C1. Merge on `(occID, CYCLE_YEAR)`
- [ ] C2. Post-merge checks (row count, orphan check)

### Phase D — DIARY_VALID Filtering
- [ ] D1. Filter `DIARY_VALID == 0` respondents
- [ ] D2. Log exclusion counts per cycle

### Phase E — Temporal Feature Derivation
- [ ] E1. Derive `DAYTYPE`
- [ ] E2. Derive `startMin` / `HOUR_OF_DAY`
- [ ] E3. Derive `TIMESLOT_10`
- [ ] E4. Derive `DDAY_STRATA`

### Phase F — HETUS 144-Slot Conversion
- [ ] F1. Implement `episodes_to_144_slots()`
- [ ] F2. Build wide-format DataFrame
- [ ] F3. Implement `episodes_to_144_athome()`
- [ ] F4. Attach demographic context to wide format

### Phase G — Export
- [ ] G1. Export `merged_episodes.csv` / `.parquet`
- [ ] G2. Export `hetus_wide.csv`
- [ ] G3. End-to-end dry run
