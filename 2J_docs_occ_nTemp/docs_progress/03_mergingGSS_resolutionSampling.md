# Step 3E — Resolution Downsampling: 144-Slot → 48-Slot (30-Minute Interval)

**Status:** PLANNING
**Input:** `outputs_step3/hetus_wide.csv` (64,061 rows × 288+ columns, 10-min HETUS intermediate)
**Output:** `outputs_step3/hetus_30min.csv` (64,061 rows × 96 columns, 30-min BEM/UBEM format)
**Script location:** `03_mergingGSS.py` — new Phase H appended after Phase G export
**Added at:** 2026-03-20 (post-Step-3 completion, pre-Step-4 training)

---

## Context & Rationale

Step 3F (Phase F in `03_mergingGSS.py`) already produces `hetus_wide.csv`: one row per respondent, 144 activity slots (`slot_001`–`slot_144`) + 144 AT_HOME slots (`home_001`–`home_144`) at 10-minute resolution. This is kept as the **archival intermediate** (HETUS-compatible, full granularity).

Step 3E adds a **post-processing downsampling pass** that converts `hetus_wide.csv` → `hetus_30min.csv` at 30-minute resolution. This is the **direct input format for Model 1 (Step 4)** and all downstream BEM/UBEM integration (Steps 6–7).

**Why this step was not in the original plan:**
The 30-min resolution design decision was added after Step 3 was completed, motivated by:
- EnergyPlus and most BEM tools operate at hourly or 30-min timesteps; 10-min adds no useful simulation information.
- Transformer self-attention cost scales as O(L²): 144→48 tokens cuts attention operations ~9×.
- Estimated training time reduction: ~4–8 hrs → ~1.5–3 hrs on Concordia HPC.

---

## Algorithmic Design

### 1. Slot Grouping

Each 30-minute slot `s` (1–48) aggregates exactly 3 consecutive 10-minute source slots:

```
source_slots(s) = [3*(s-1)+1 : 3*s]   # e.g., s=1 → slots 1,2,3; s=2 → slots 4,5,6; …; s=48 → slots 142,143,144
```

The 48 slots cover the same 4:00 AM – 3:59 AM diary window:

| 30-min slot | 10-min source slots | Time window        | BEM hour |
|-------------|---------------------|--------------------|----------|
| 1           | 1, 2, 3             | 04:00–04:29        | Hour 4   |
| 2           | 4, 5, 6             | 04:30–04:59        | Hour 4   |
| 3           | 7, 8, 9             | 05:00–05:29        | Hour 5   |
| …           | …                   | …                  | …        |
| 40          | 118, 119, 120       | 23:30–23:59        | Hour 23  |
| 41          | 121, 122, 123       | 00:00–00:29        | Hour 0   |
| …           | …                   | …                  | …        |
| 48          | 142, 143, 144       | 03:30–03:59        | Hour 3   |

### 2. Activity Downsampling — Majority Vote

For each respondent and each 30-min slot `s`:

```
activity_30[s] = mode(slot_{3s-2}, slot_{3s-1}, slot_{3s})
```

- If one activity code appears in ≥ 2 of the 3 source slots: assign that code (strict majority).
- **Tie rule (all 3 slots carry different codes):** assign the code with the **longest continuous run** across the 3 source slots. If all durations are equal (all 1 slot each, i.e. genuine 3-way tie), assign by BEM priority (see §3).

### 3. AT_HOME Downsampling — Presence-Priority Vote

For each respondent and each 30-min slot `s`:

```
home_30[s] = mode(home_{3s-2}, home_{3s-1}, home_{3s})
```

- If ≥ 2 of the 3 source slots have AT_HOME = 1: assign 1 (present).
- If ≥ 2 of the 3 source slots have AT_HOME = 0: assign 0 (absent).
- **Tie rule (not applicable for binary):** with exactly 3 source slots, a 2-vs-1 majority always resolves. A true tie is impossible for binary values over an odd number of slots. *(Edge case: if any source slot is NaN, use majority of the remaining non-NaN slots; if all NaN, propagate NaN.)*

### 4. Activity Tie-Breaking Priority (BEM-motivated)

Applied only when all 3 source slots carry distinct activity codes (3-way tie — rare):

1. **Longest continuous run wins:** the code that spans the most *consecutive* 10-min slots within the window.
2. **BEM fallback order (if run lengths are equal):** Sleep > Personal care > Paid work > Education > Domestic work > Care for others > Restaurant/meals > Social/leisure > Active leisure > Volunteer > Other > Travel > Missing/unknown.

The BEM fallback ordering reflects which occupancy states have the highest energy-model impact (sleep = guaranteed at-home, low metabolic; paid work = probable absence).

### 5. Output Column Schema

Output columns, one row per respondent:

```
# Identity + demographic context (carried from hetus_wide.csv)
occID, CYCLE_YEAR, SURVYEAR, SURVMNTH, DDAY, DDAY_STRATA, DAYTYPE,
AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, TOTINC, HRSWRK, NOCS,
COW, WKSWRK, COLLECT_MODE, TUI_10_AVAIL, TOTINC_SOURCE, BS_TYPE, WGHT_PER,

# 48 activity slots (30-min, 4:00 AM origin)
act30_001, act30_002, …, act30_048,

# 48 AT_HOME slots (30-min, 4:00 AM origin)
hom30_001, hom30_002, …, hom30_048
```

Total: identity/demographic columns (from hetus_wide) + 96 activity/home columns.

**Column naming convention:** `act30_NNN` and `hom30_NNN` (to distinguish from 10-min `slot_NNN` / `home_NNN` in hetus_wide.csv).

---

## Implementation Plan

### Phase H — Resolution Downsampling (new function in `03_mergingGSS.py`)

#### H.1 — Load `hetus_wide.csv`

- Load `outputs_step3/hetus_wide.csv` with `pd.read_csv`.
- Identify identity/demographic columns (all columns that are not `slot_NNN` or `home_NNN`).
- Extract activity matrix: shape (64,061 × 144), columns `slot_001`–`slot_144`.
- Extract home matrix: shape (64,061 × 144), columns `home_001`–`home_144`.

#### H.2 — Vectorized Majority Vote (Activity)

- Reshape activity matrix into (64,061 × 48 × 3) using numpy:
  ```python
  act_arr = hetus_wide[[f"slot_{i:03d}" for i in range(1, 145)]].to_numpy(dtype=float)
  act_3d = act_arr.reshape(n_respondents, 48, 3)
  ```
- For each 30-min slot: compute mode across axis=2 using scipy.stats.mode (or a custom vectorized implementation).
- Handle NaN values: exclude NaNs from mode computation; if all 3 are NaN, output NaN.

#### H.3 — Vectorized Majority Vote (AT_HOME)

- Reshape home matrix into (64,061 × 48 × 3):
  ```python
  hom_arr = hetus_wide[[f"home_{i:03d}" for i in range(1, 145)]].to_numpy(dtype=float)
  hom_3d = hom_arr.reshape(n_respondents, 48, 3)
  ```
- Binary majority: compute `nansum` over axis=2; assign 1 if sum ≥ 2, else 0; NaN if all NaN.
- This avoids scipy.stats.mode overhead for the binary case.

#### H.4 — Tie Resolution for Activity (3-way ties)

- Detect 3-way ties: rows where all 3 source slots have distinct non-NaN values (i.e. no majority).
- For each tied (respondent, slot) pair:
  - Since all 3 slots each span exactly 10 min (equal run length), apply BEM fallback priority order directly.
  - Map each of the 3 codes to its BEM priority rank; assign the highest-priority (lowest rank) code.
- Expected frequency of 3-way ties: very low (~1–3% of slots, primarily during transition periods between activities).

#### H.5 — Assemble `hetus_30min` DataFrame

- Construct output DataFrame:
  - Identity/demographic columns: copied from `hetus_wide` (same row order).
  - Activity columns: `act30_001`–`act30_048` from H.2+H.4 results.
  - AT_HOME columns: `hom30_001`–`hom30_048` from H.3 results.
- Cast activity columns to `Int16` (nullable integer) to preserve NaN compatibility.
- Cast AT_HOME columns to `Int8` (nullable integer).

#### H.6 — Export

- Write `outputs_step3/hetus_30min.csv` (primary output for Step 4).
- Print summary statistics (see §Validation Checks below).

---

## Validation Checks (post-downsampling)

The following checks should be run immediately after `hetus_30min.csv` is written, either inline in Phase H or in `03_mergingGSS_val.py`.

### V1 — Shape Check
- `hetus_30min.shape[0]` == 64,061 (same respondent count as `hetus_wide`).
- `hetus_30min.shape[1]` == (number of identity/demographic cols) + 96.

### V2 — No Slot Completeness Regression
- NaN rate per `act30_NNN` column ≤ NaN rate of corresponding source `slot_NNN` columns.
- If hetus_wide had 0% NaN (confirmed), hetus_30min must also have 0% NaN (or only where all 3 sources were NaN, which should not occur given 100% slot completeness confirmed in Step 3).

### V3 — Activity Distribution Preservation
- For each of the 14 activity categories: compare weighted frequency in `hetus_wide` (10-min) vs. `hetus_30min` (30-min).
- Acceptable tolerance: ≤ 1 percentage point difference per category.
- Rationale: majority vote preserves dominant activities; small transitions may shift slightly toward dominant codes.

### V4 — AT_HOME Rate Preservation
- Compute weighted AT_HOME rate per cycle from `hom30_NNN` columns.
- Expected: match hetus_wide weighted AT_HOME rates (2005≈62.7%, 2010≈62.3%, 2015≈64.5%, 2022≈70.6%) within ±1 pp.

### V5 — Night Sleep / AT_HOME Plausibility
- Slots 1–8 (04:00–07:59 AM): weighted sleep rate ≥ 70% (from 83.7% in 10-min format; downsampling may shift slightly).
- Slots 1–8: weighted AT_HOME rate ≥ 85% (from 93.4% in 10-min format).

### V6 — Tie Rate Reporting
- Report: total (respondent, slot) pairs evaluated; number and % of 3-way ties encountered; number resolved by BEM fallback vs. longest-run rule.
- Flag if 3-way tie rate > 5% (would suggest a data anomaly).

### V7 — DDAY_STRATA Distribution Preserved
- DDAY_STRATA counts in `hetus_30min` must equal those in `hetus_wide` exactly (identity columns are copied, not recomputed).

### V8 — Cross-check Sample Rows
- For 5 randomly selected respondents: manually verify that each 30-min slot in `hetus_30min` matches the expected majority of its 3 source slots from `hetus_wide`.

---

## Output Files

| File | Location | Description |
|------|----------|-------------|
| `hetus_30min.csv` | `outputs_step3/` | **Primary output.** 64,061 × 96 columns (48 act + 48 home), 30-min resolution. Direct input for Step 4 (Model 1 Transformer). |
| `hetus_wide.csv` | `outputs_step3/` | **Archival intermediate.** Unchanged. 144-slot HETUS format kept for auditability and potential HETUS-standard reporting. |

---

## Implementation Notes & Edge Cases

| Issue | Handling |
|-------|----------|
| `scipy.stats.mode` default behavior changed in scipy ≥ 1.9 (returns first mode, not lowest) | Pin behavior explicitly: use `keepdims=True`, or implement custom nanmode with explicit tie-handling. |
| NaN in source slots | Confirmed 0% NaN in hetus_wide (100% slot completeness). Code should still guard against NaN propagation for robustness. |
| Integer dtype of occACT codes | Source `slot_NNN` columns may be stored as float64 after CSV round-trip. Cast to `Int16` before majority vote to avoid float mode artifacts. |
| Memory: (64,061 × 288) float64 array | ~148 MB. Acceptable for in-memory processing. No chunking needed. |
| Performance | Vectorized numpy reshape + nansum (for AT_HOME) + scipy mode (for activity) should run in < 60 seconds on a standard laptop. No HPC required for this step. |
| Tie-breaking BEM priority list | Must be defined as a constant dict `{occACT_code: priority_rank}` using the 14 confirmed category codes from the Step 2 TUI_01 crosswalk. |

---

## Integration Points

- **Feeds into:** `03_mergingGSS_val.py` (validation checks V1–V8 above should be added to the existing Step 3 validation script or a new `03_mergingGSS_resolutionSampling_val.py`).
- **Feeds into:** Step 4 (`04_transformerAugmentation.py`) — takes `hetus_30min.csv` as primary input.
- **Does NOT modify:** `hetus_wide.csv`, `merged_episodes.csv`, `merged_episodes.parquet`, or any Step 2 outputs.
- **Script:** Phase H is added to `03_mergingGSS.py` as a self-contained function `downsample_to_30min(hetus_wide_df) -> pd.DataFrame`, called after Phase G (export of hetus_wide). Alternatively, implement as a standalone `03E_resolutionDownsampling.py` script if Step 3 runtime becomes too long.

---

## Checklist

- [ ] H.1 — Load hetus_wide.csv and verify 64,061 rows, 288+ columns
- [ ] H.2 — Vectorized activity majority vote (numpy reshape + mode, axis=2)
- [ ] H.3 — Vectorized AT_HOME binary majority (nansum ≥ 2)
- [ ] H.4 — 3-way tie resolution via BEM priority order (define priority dict from TUI_01 crosswalk)
- [ ] H.5 — Assemble hetus_30min DataFrame (identity cols + act30_NNN + hom30_NNN)
- [ ] H.6 — Export hetus_30min.csv to outputs_step3/
- [ ] V1 — Shape check (64,061 × 96 + demographic cols)
- [ ] V2 — Slot completeness: 0% NaN in act30/hom30 columns
- [ ] V3 — Activity distribution match within ±1 pp vs. hetus_wide
- [ ] V4 — Weighted AT_HOME rates per cycle within ±1 pp
- [ ] V5 — Night sleep ≥ 70%, night AT_HOME ≥ 85% for slots 1–8
- [ ] V6 — 3-way tie rate < 5%; print tie resolution summary
- [ ] V7 — DDAY_STRATA distribution unchanged
- [ ] V8 — Manual spot-check 5 random respondents

---

---

# Phase I — Co-Presence Tiling to 30-Min Slot Format

**Status:** PLANNING
**Added at:** 2026-03-22 (pre-Step-4 training, identified as missing prerequisite for Model 1)
**Input:** `outputs_step3/merged_episodes.csv` (episode-level, ~1,049,480 rows, 9 co-presence columns)
**Output:** `outputs_step3/copresence_30min.csv` (64,061 rows × 433 columns: occID + 9×48 slots)
**Script location:** `03_mergingGSS.py` — new Phase I appended after Phase H export

---

## Context & Rationale

Phase H (Step 3E) produced `hetus_30min.csv` with 48 activity slots (`act30_NNN`) and 48 AT_HOME slots (`hom30_NNN`). However, the **9 co-presence columns** (`Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues`) exist only at episode level in `merged_episodes.csv`. They have not been tiled into per-slot wide format.

Phase I fills this gap. It applies the same two-stage tiling pipeline used in Phases F+H (episode → 144-slot HETUS intermediate → 48-slot 30-min) to all 9 co-presence columns, producing `copresence_30min.csv`. This file is a mandatory input for Step 4 (Conditional Transformer): the encoder requires **11 features per slot** (1 activity + 1 AT_HOME + 9 co-presence), so co-presence must be in slot format before training can begin.

**Why this was not in the original Step 3 plan:**
The original tiling logic (Phases F+H) focused on `occACT` and `AT_HOME` as the primary occupancy signals. Co-presence was planned as a model input in Step 4 but the tiling prerequisite was only identified when designing the detailed Step 4 implementation.

**Scope boundary:** Phase I produces a separate `copresence_30min.csv` rather than appending columns to `hetus_30min.csv`, to keep Phase H output stable and avoid re-running the full pipeline. Step 4 will merge the two files on `occID` during dataset assembly.

---

## Algorithmic Design

### 1. Two-Stage Pipeline (mirrors Phases F + H)

```
merged_episodes.csv  (episode-level)
        │
        ▼  Stage 1: Episode → 144-slot intermediate (10-min)
        │  Same tiling logic as Phase F (occACT/AT_HOME):
        │    For each respondent × co-presence column:
        │      Initialize cop_slots[1..144] = NaN
        │      For each episode row:
        │        slot_start = startMin // 10 + 1
        │        slot_end   = endMin   // 10 + 1   (exclusive: endMin slot not filled)
        │        cop_slots[slot_start : slot_end] = episode co-presence value
        │
        ▼  Stage 2: 144-slot → 48-slot downsampling (30-min)
        │  Same majority-vote logic as Phase H:
        │    For each respondent × co-presence column × 30-min slot s:
        │      source_slots = [3*(s-1)+1 : 3*s]
        │      cop_30[s] = majority vote of cop_slots[source_slots]
        │
        ▼  copresence_30min.csv
```

### 2. Co-Presence Value Space

GSS encodes co-presence as: **1 = Yes (present), 2 = No (absent), NaN = not applicable / missing**.

The majority vote operates on this {1, 2, NaN} space:
- If ≥2 of 3 source slots = 1 → assign 1 (present)
- If ≥2 of 3 source slots = 2 → assign 2 (absent)
- NaN propagation: if all 3 source slots are NaN → NaN (slot truly unresolvable)
- Binary {1, 2} over 3 non-NaN slots always produces a strict majority (no 3-way tie possible)

> **Note:** Recoding to {0=absent, 1=present} is deferred to Step 4 (dataset assembly). `copresence_30min.csv` retains the original GSS coding {1, 2} for auditability.

### 3. Special Handling: `colleagues`

- `colleagues` (TUI_06I) was **not measured** in 2005/2010 cycles. All episode rows for those cycles have `colleagues = NaN`.
- After tiling, all 48 `colleagues30_NNN` slots will be NaN for 2005/2010 respondents.
- This NaN pattern is **correct and expected** — it will be masked during Step 4 training loss computation (colleagues BCE loss zeroed out for 2005/2010 rows).

### 4. Episode Boundary Handling

The `endMin` column in `merged_episodes.csv` follows the GSS convention: episode end is **exclusive** — the end slot itself belongs to the next episode. Tiling uses:
```
slot_start = startMin // 10 + 1
slot_end   = endMin   // 10 + 1        # exclusive upper bound
cop_slots[slot_start : slot_end] = value
```
This is identical to the activity tiling logic in Phase F and ensures no overlap or gap between consecutive episodes.

### 5. Output Column Schema

```
# One row per respondent (64,061 rows)
occID,

# Alone: 48 slots
Alone30_001, Alone30_002, …, Alone30_048,

# Spouse: 48 slots
Spouse30_001, Spouse30_002, …, Spouse30_048,

# Children: 48 slots
Children30_001, …, Children30_048,

# parents: 48 slots
parents30_001, …, parents30_048,

# otherInFAMs: 48 slots
otherInFAMs30_001, …, otherInFAMs30_048,

# otherHHs: 48 slots
otherHHs30_001, …, otherHHs30_048,

# friends: 48 slots
friends30_001, …, friends30_048,

# others: 48 slots
others30_001, …, others30_048,

# colleagues: 48 slots (NaN for 2005/2010 respondents)
colleagues30_001, …, colleagues30_048
```

Total: 1 (occID) + 9×48 (co-presence slots) = **433 columns**, 64,061 rows.

**Column naming convention:** `{ColName}30_{NNN}` — capitalisation preserved from unified GSS names (e.g. `Alone30_001`, not `alone30_001`).

---

## Implementation Plan

### Phase I — Co-Presence Tiling (new function in `03_mergingGSS.py`)

#### I.1 — Load `merged_episodes.csv`

- Load `outputs_step3/merged_episodes.csv`.
- Verify expected columns present: `occID`, `startMin`, `endMin`, `CYCLE_YEAR`, and all 9 co-presence columns.
- Verify row count: ~1,049,480 episode rows.
- Identify the set of unique `occID` values and confirm count = 64,061.

#### I.2 — Load `hetus_30min.csv` for occID reference

- Load occID list from `outputs_step3/hetus_30min.csv` to use as the respondent index.
- This ensures Phase I output rows are in the same order as Phase H, simplifying the Step 4 merge.

#### I.3 — Tiling Loop: Episode → 144 10-Min Slots per Co-Presence Column

For each of the 9 co-presence columns:
```python
# Pre-allocate (64,061 × 144) float array, initialised to NaN
cop_10min = np.full((n_respondents, 144), np.nan)

# Group episodes by occID
grouped = merged_episodes.groupby("occID")

for row_idx, occ_id in enumerate(occid_order):
    episodes = grouped.get_group(occ_id)
    for _, ep in episodes.iterrows():
        slot_start = int(ep["startMin"]) // 10 + 1 - 1   # 0-indexed
        slot_end   = int(ep["endMin"])   // 10 + 1 - 1   # 0-indexed exclusive
        val = ep[cop_col]
        if pd.notna(val):
            cop_10min[row_idx, slot_start:slot_end] = val
```

Performance note: 9 columns × 64,061 respondents × episode iteration. For acceptable runtime (< 5 min), vectorise by pre-building a (respondents × 144) slot assignment matrix using numpy advanced indexing or a pre-sorted episode array.

#### I.4 — Downsample 144 → 48 Slots (Majority Vote)

Same reshape + binary majority logic as Phase H (H.3):
```python
cop_3d = cop_10min.reshape(n_respondents, 48, 3)   # (64061, 48, 3)

valid_count = np.sum(~np.isnan(cop_3d), axis=2)    # non-NaN count per window
sum_present = np.nansum(cop_3d == 1, axis=2)        # count of "present" slots

cop_30 = np.where(valid_count == 0, np.nan,
         np.where(sum_present >= 2, 1.0, 2.0))      # majority: 1 if ≥2 present, else 2
```

No 3-way tie is possible for binary {1, 2} values over 3 slots. The only NaN output is when all 3 source slots are NaN.

#### I.5 — Assemble Output DataFrame

- For each of the 9 columns: create DataFrame with 48 columns named `{ColName}30_{001..048}`.
- Concatenate all 9 DataFrames horizontally.
- Prepend `occID` column.
- Cast all co-presence slot columns to `pd.Int8Dtype()` (nullable int8: values {1, 2, NA}).

#### I.6 — Export

- Write `outputs_step3/copresence_30min.csv`.
- Print summary statistics.

---

## Validation Checks (post-tiling)

### VI-1 — Shape Check
- `copresence_30min.shape[0]` == 64,061
- `copresence_30min.shape[1]` == 433 (1 occID + 432 co-presence slot columns)

### VI-2 — occID Alignment
- `copresence_30min["occID"]` == `hetus_30min["occID"]` (identical order, no mismatches)

### VI-3 — Primary 8 Columns: No All-NaN Respondents
- For each of the 8 primary co-presence columns (all except `colleagues`): confirm no respondent has all-NaN across all 48 slots.
- Expected: every respondent has at least 1 non-NaN slot for primary columns.

### VI-4 — `colleagues` NaN Pattern
- For 2005/2010 respondents: all 48 `colleagues30_NNN` slots must be NaN (100%).
- For 2015/2022 respondents: NaN rate in `colleagues30_NNN` must be < 100% (i.e., at least some non-NaN values per respondent).

### VI-5 — Value Range
- All non-NaN values in co-presence slot columns ∈ {1, 2} (original GSS coding).
- No values outside this range.

### VI-6 — Co-Presence Prevalence Plausibility
- For `Alone30_NNN` columns: compute proportion of slots where value = 1 (present/alone). Expect ~30–50% across all cycles (plausible for solo activity time).
- For `Spouse30_NNN`: expect ~20–40%.
- These are rough sanity checks — compare to episode-level proportions in `merged_episodes.csv` for cross-validation.

### VI-7 — Cross-Validate Sample Rows
- For 5 randomly selected respondents: manually confirm that `Alone30_001` (slot 1 = 04:00–04:29) matches the majority of episode co-presence values covering 10-min slots 1–3 in `merged_episodes.csv`.

---

## Output Files

| File | Location | Description |
|------|----------|-------------|
| `copresence_30min.csv` | `outputs_step3/` | **Primary output.** 64,061 × 433 columns (occID + 9×48 co-presence slots), 30-min resolution. Direct input for Step 4 (merged with hetus_30min on occID). |

---

## Implementation Notes & Edge Cases

| Issue | Handling |
|-------|----------|
| Episode loop performance (9 cols × 64K respondents) | Vectorise using pre-sorted episode array and numpy advanced indexing. Target runtime < 5 min on laptop. |
| Episodes covering multiple 30-min windows | Handled naturally by the 10-min tiling stage — multi-slot episodes fill contiguous 10-min slots before downsampling. |
| endMin == 0 (midnight to 4:00 AM episodes that wrap) | Use same wrap handling as Phase F: endMin=0 → endMin=1440 if startMin > endMin. |
| Respondents with no episodes in a co-presence column (all NaN) | Valid only for `colleagues` in 2005/2010. All other columns should have at least some non-NaN episode rows. |
| Int8 dtype with NaN | Use `pd.Int8Dtype()` (nullable integer) — standard float NaN cannot be stored in int8. Same approach as Phase H for hom30 columns. |

---

## Integration Points

- **Feeds into:** Step 4 (`04B_dataset_assembly.py`) — merged with `hetus_30min.csv` on `occID` to build the full 11-feature-per-slot training dataset.
- **Does NOT modify:** `hetus_30min.csv`, `hetus_wide.csv`, `merged_episodes.csv`, or any Step 2 outputs.
- **Script:** Phase I added to `03_mergingGSS.py` as `tile_copresence_to_30min()` function, called after Phase H in `main()`.

---

## Checklist

- [ ] I.1 — Load merged_episodes.csv; verify columns and ~1,049,480 rows
- [ ] I.2 — Load hetus_30min.csv to fix occID order (64,061)
- [ ] I.3 — Tiling loop: episode → 144-slot 10-min arrays for all 9 co-presence columns
- [ ] I.4 — Downsample 144 → 48 slots via binary majority vote (reshape + nansum)
- [ ] I.5 — Assemble copresence_30min DataFrame (occID + {Col}30_001..048, Int8)
- [ ] I.6 — Export copresence_30min.csv to outputs_step3/
- [ ] VI-1 — Shape check (64,061 × 433)
- [ ] VI-2 — occID alignment with hetus_30min
- [ ] VI-3 — No all-NaN respondents for primary 8 columns
- [ ] VI-4 — colleagues NaN pattern: 100% NaN for 2005/2010, <100% for 2015/2022
- [ ] VI-5 — Value range: all non-NaN ∈ {1, 2}
- [ ] VI-6 — Co-presence prevalence plausibility (Alone ~30–50%, Spouse ~20–40%)
- [ ] VI-7 — Manual spot-check 5 random respondents

---

---

# Section 8 — Co-Presence Before/After 30-Min Tiling Plot (`03_mergingGSS_val.py`)

**Status:** PLANNING
**Added at:** 2026-03-22
**Depends on:** Phase I complete (`copresence_30min.csv` exists)
**Target:** New plot in `step3_validation_report.html` as Section 8a

---

## Purpose

The existing Section 6 plots (6a–6c) show co-presence at **episode level** from `merged_episodes.csv`. After Phase I produces `copresence_30min.csv`, it becomes possible to compare prevalence *before* and *after* the two-stage tiling (episode → 144-slot → 48-slot). Section 8a provides this comparison as a direct visual QA check on Phase I output quality.

**Key question answered:** Does the majority-vote tiling preserve the co-presence prevalence signal, or does it introduce systematic inflation/deflation?

---

## Plot Design: Section 8a

**Plot key:** `"8a_copre_before_after"`
**Figure size:** 22 × 10 inches

### Row 1 — Per-Cycle Grouped Bar Charts (4 panels)

One panel per cycle year (2005 / 2010 / 2015 / 2022). Each panel shows 9 grouped bar pairs, one per co-presence column:
- **Blue bar** = episode-level prevalence (`% of non-NaN episodes where column = 1`, from `merged_episodes.csv`)
- **Orange bar** = 30-min slot prevalence (`% of non-NaN slots where column = 1`, from `copresence_30min.csv`)

Same y-axis range (0–100%) across all panels for direct cross-cycle comparison.

### Row 2 — Delta Panel (single panel, full width)

One line per cycle (4 lines). X-axis: 9 co-presence column names. Y-axis: `slot_prevalence − episode_prevalence` in percentage points.

- Dashed horizontal line at Δ = 0 (no change reference)
- Values near 0 → tiling preserved the signal ✅
- Positive Δ → tiling inflated presence (short absent episodes absorbed into majority-present windows)
- Negative Δ → tiling deflated presence (short present episodes absorbed into majority-absent windows)

**Pass criterion:** |Δ| ≤ 5 pp per column per cycle. Deltas >5 pp are printed as WARN.

---

## Where to Add the Code

1. **New method** `validate_copresence_30min(self)` added to `Step3Validator` class in `03_mergingGSS_val.py`, after `validate_copresence()`.
2. **Call site** in `run()`: add `self.validate_copresence_30min()` after the existing `self.validate_copresence()` call.
3. **HTML report** in `build_html_report()`: add to `chart_sections` list:
   ```python
   ("8a_copre_before_after",
    "Section 8a — Co-Presence Prevalence: Episode Level vs. 30-Min Slot Level"),
   ```

---

## Checklist

- [ ] Task #47 — Add `validate_copresence_30min()` method; implement 2-row figure (4 per-cycle bar panels + delta line panel); wire into `run()` and `build_html_report()`
