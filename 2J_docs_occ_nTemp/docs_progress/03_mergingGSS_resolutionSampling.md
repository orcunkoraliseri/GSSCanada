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
occID, CYCLE_YEAR, SURVYEAR, SURVMNTH, DDAY, DDAY_STRATA, DAYTYPE, SEASON,
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
