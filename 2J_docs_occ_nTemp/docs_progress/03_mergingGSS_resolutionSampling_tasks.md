# Step 3E — Resolution Downsampling: Task List for Implementation

**Script to modify:** `2J_docs_occ_nTemp/03_mergingGSS.py`
**Input file:** `2J_docs_occ_nTemp/outputs_step3/hetus_wide.csv`
**Output file:** `2J_docs_occ_nTemp/outputs_step3/hetus_30min.csv`

---

## Background (read before implementing)

`hetus_wide.csv` has **64,061 rows** (one per respondent) and **288+ columns**:
- `slot_001` … `slot_144` — activity code (one of 14 integer codes) per 10-min slot
- `home_001` … `home_144` — AT_HOME binary (0 or 1) per 10-min slot
- All other columns — identity/demographic (occID, CYCLE_YEAR, AGEGRP, SEX, etc.)

The goal is to produce `hetus_30min.csv` with the same 64,061 rows but only **96 new columns**:
- `act30_001` … `act30_048` — activity code per **30-min** slot
- `hom30_001` … `hom30_048` — AT_HOME binary per **30-min** slot

Each 30-min slot is computed from 3 consecutive 10-min source slots:
- slot s covers source slots `[3*(s-1)+1, 3*(s-1)+2, 3*s]`
- e.g. `act30_001` ← majority of `slot_001, slot_002, slot_003`
- e.g. `act30_002` ← majority of `slot_004, slot_005, slot_006`
- …
- e.g. `act30_048` ← majority of `slot_142, slot_143, slot_144`

**All code goes into `03_mergingGSS.py` as a new Phase H**, added after the existing Phase G export block. Also call the new function from `main()` after Phase G.

---

## Task List

Tasks must be done in order within each group. Groups marked as "parallel" can be done simultaneously.

---

### GROUP 0 — Setup (do first, these unblock everything else)

---

**Task #1 — Add Phase H function skeleton**

In `03_mergingGSS.py`, after the Phase G block, add:

```python
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
    pass  # implementation added in subsequent tasks
```

Also add the call in `main()` after Phase G:

```python
# Phase H: Resolution downsampling
hetus_30min = downsample_to_30min(hetus_wide)
```

---

**Task #2 — Define BEM_PRIORITY constant**

At the top of the Phase H section (before the function), add the priority dict. Lower number = higher priority (more important for BEM energy modeling).

You need to find the exact integer codes used in the `slot_NNN` columns. Check `02_harmonizeGSS.py` or open `hetus_wide.csv` and look at unique values in `slot_001`. The 14 categories from the TUI_01 crosswalk are mapped to integers 1–14 (or similar). Confirm the exact codes and map them like this:

```python
# BEM priority order for 3-way tie resolution (lower rank = higher priority)
# Key = occACT integer code as used in slot_NNN columns
# Adjust codes to match actual values found in hetus_wide.csv
BEM_PRIORITY: dict[int, int] = {
    # <sleep_code>:          1,
    # <personal_care_code>:  2,
    # <paid_work_code>:      3,
    # <education_code>:      4,
    # <domestic_work_code>:  5,
    # <care_others_code>:    6,
    # <restaurant_code>:     7,
    # <social_leisure_code>: 8,
    # <active_leisure_code>: 9,
    # <volunteer_code>:      10,
    # <other_code>:          11,
    # <travel_code>:         12,
    # <missing_code>:        13,
    # ... add all 14 codes
}
```

---

### GROUP 1 — Load and split columns (H.1, sequential)

---

**Task #3 — H.1a: Load hetus_wide.csv and verify row count**

Inside `downsample_to_30min()`, replace `pass` with:

```python
print("\n── Phase H: Resolution Downsampling 144→48 slots ───────────")
input_path = Path("outputs_step3") / "hetus_wide.csv"
df = pd.read_csv(input_path, low_memory=False)
print(f"  Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
assert df.shape[0] == 64_061, f"Expected 64,061 rows, got {df.shape[0]}"
```

---

**Task #4 — H.1b: Separate identity columns from slot columns**

After the load, identify which columns are slot columns and which are identity/demographic:

```python
SLOT_ACT_COLS  = [f"slot_{i:03d}" for i in range(1, 145)]
SLOT_HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]
META_COLS = [c for c in df.columns if c not in SLOT_ACT_COLS + SLOT_HOME_COLS]

print(f"  Activity slot cols : {len(SLOT_ACT_COLS)}")   # expect 144
print(f"  AT_HOME slot cols  : {len(SLOT_HOME_COLS)}")   # expect 144
print(f"  Meta/identity cols : {len(META_COLS)}")
```

---

**Task #5 — H.1c: Extract activity matrix as numpy array**

```python
act_arr = df[SLOT_ACT_COLS].to_numpy(dtype=float)  # shape (64061, 144)
print(f"  Activity matrix shape: {act_arr.shape}")
```

---

**Task #6 — H.1d: Extract AT_HOME matrix as numpy array**

```python
hom_arr = df[SLOT_HOME_COLS].to_numpy(dtype=float)  # shape (64061, 144)
print(f"  AT_HOME matrix shape: {hom_arr.shape}")
```

---

### GROUP 2a — Activity majority vote (H.2, sequential)

---

**Task #7 — H.2a: Reshape activity array to (n × 48 × 3)**

```python
n = act_arr.shape[0]
act_3d = act_arr.reshape(n, 48, 3)  # each [i, j, :] = 3 source slots for slot j
print(f"  Activity 3D shape: {act_3d.shape}")  # expect (64061, 48, 3)
```

---

**Task #8 — H.2b: Write _nanmode_axis2() helper function**

Add this as a module-level helper function (outside `downsample_to_30min`, before it):

```python
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
```

Note: this double loop is slow but correct. If performance is needed, vectorize with numpy later.

---

**Task #9 — H.2c: Apply nanmode to get act_30 with tie sentinels**

```python
print("  Computing activity majority vote (may take ~1 min)...")
act_30 = _nanmode_axis2(act_3d)  # shape (64061, 48)
n_ties = int(np.isnan(act_30).sum())
print(f"  3-way ties detected: {n_ties:,} ({100*n_ties/(n*48):.2f}% of all cells)")
```

---

### GROUP 2b — AT_HOME binary vote (H.3, sequential, can run in parallel with GROUP 2a)

---

**Task #10 — H.3a: Reshape AT_HOME array to (n × 48 × 3)**

```python
hom_3d = hom_arr.reshape(n, 48, 3)  # shape (64061, 48, 3)
print(f"  AT_HOME 3D shape: {hom_3d.shape}")
```

---

**Task #11 — H.3b: Compute AT_HOME binary majority vote**

No scipy needed — binary over 3 slots always has a majority (can't tie with odd count):

```python
valid_count = np.sum(~np.isnan(hom_3d), axis=2)  # how many non-NaN per window
sum_home    = np.nansum(hom_3d, axis=2)           # sum of 1s per window

hom_30 = np.where(valid_count == 0, np.nan,
         np.where(sum_home >= 2, 1.0, 0.0))       # shape (64061, 48)

n_home_nan = int(np.isnan(hom_30).sum())
print(f"  AT_HOME NaNs after vote: {n_home_nan}")  # expect 0
```

---

### GROUP 3 — Tie resolution (H.4, sequential, needs GROUP 2a to finish)

---

**Task #12 — H.4a: Detect 3-way tie positions**

```python
tie_mask = np.isnan(act_30)  # True where 3-way tie sentinel
tie_positions = list(zip(*np.where(tie_mask)))  # list of (row_idx, slot_idx) tuples
print(f"  Tie positions to resolve: {len(tie_positions):,}")
```

---

**Task #13 — H.4b: Resolve ties using BEM priority order**

```python
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
```

---

### GROUP 4 — Assemble output DataFrame (H.5, sequential, needs H.4 + H.3 to finish)

---

**Task #14 — H.5a: Build act30 DataFrame with Int16 dtype**

```python
act30_cols = [f"act30_{i:03d}" for i in range(1, 49)]
act30_df = pd.DataFrame(act_30, columns=act30_cols).astype(pd.Int16Dtype())
print(f"  act30_df shape: {act30_df.shape}")  # expect (64061, 48)
```

---

**Task #15 — H.5b: Build hom30 DataFrame with Int8 dtype**

```python
hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
hom30_df = pd.DataFrame(hom_30, columns=hom30_cols).astype(pd.Int8Dtype())
print(f"  hom30_df shape: {hom30_df.shape}")  # expect (64061, 48)
```

---

**Task #16 — H.5c: Concatenate meta + act30 + hom30**

```python
hetus_30min = pd.concat(
    [df[META_COLS].reset_index(drop=True), act30_df, hom30_df],
    axis=1
)
print(f"  hetus_30min shape: {hetus_30min.shape}")
# Expected: (64061, len(META_COLS) + 96)
```

---

### GROUP 5 — Export (H.6, sequential, needs GROUP 4)

---

**Task #17 — H.6a: Write hetus_30min.csv**

```python
output_path = Path("outputs_step3") / "hetus_30min.csv"
print(f"\n  Writing {output_path} ...")
hetus_30min.to_csv(output_path, index=False)
size_mb = output_path.stat().st_size / 1e6
print(f"  Done. File size: {size_mb:.1f} MB")
return hetus_30min
```

---

**Task #18 — H.6b: Print post-export summary**

After the `downsample_to_30min()` call in `main()`, add:

```python
print(f"\n── Phase H Summary ──────────────────────────────────────────")
print(f"  Rows            : {hetus_30min.shape[0]:,}")
print(f"  Total columns   : {hetus_30min.shape[1]}")
print(f"  act30 columns   : {len([c for c in hetus_30min.columns if c.startswith('act30_')])}")
print(f"  hom30 columns   : {len([c for c in hetus_30min.columns if c.startswith('hom30_')])}")
print(f"  NaN in act30    : {hetus_30min[[c for c in hetus_30min.columns if c.startswith('act30_')]].isna().sum().sum()}")
print(f"  NaN in hom30    : {hetus_30min[[c for c in hetus_30min.columns if c.startswith('hom30_')]].isna().sum().sum()}")
```

---

### GROUP 6 — Validation checks (all need Task #17 to be done first)

All checks below can be run in any order after the file is written. Add them as a `validate_30min()` function called from `main()` after Phase H, or append to `03_mergingGSS_val.py`.

---

**Task #19 — V1: Shape check**

```python
assert hetus_30min.shape[0] == 64_061, f"Row count wrong: {hetus_30min.shape[0]}"
act30_count = len([c for c in hetus_30min.columns if c.startswith("act30_")])
hom30_count = len([c for c in hetus_30min.columns if c.startswith("hom30_")])
assert act30_count == 48, f"Expected 48 act30 cols, got {act30_count}"
assert hom30_count == 48, f"Expected 48 hom30 cols, got {hom30_count}"
print("V1 PASS — shape (64061, 96 act/home cols)")
```

---

**Task #20 — V2: Zero NaN in act30 and hom30**

```python
act30_cols = [c for c in hetus_30min.columns if c.startswith("act30_")]
hom30_cols = [c for c in hetus_30min.columns if c.startswith("hom30_")]
nan_act = hetus_30min[act30_cols].isna().sum().sum()
nan_hom = hetus_30min[hom30_cols].isna().sum().sum()
assert nan_act == 0, f"NaN in act30: {nan_act}"
assert nan_hom == 0, f"NaN in hom30: {nan_hom}"
print(f"V2 PASS — NaN act30={nan_act}, hom30={nan_hom}")
```

---

**Task #21 — V3: Activity distribution vs hetus_wide within ±1 pp**

```python
hetus_wide = pd.read_csv("outputs_step3/hetus_wide.csv", low_memory=False)
slot_cols  = [f"slot_{i:03d}" for i in range(1, 145)]
act30_cols = [f"act30_{i:03d}" for i in range(1, 49)]

wide_vals = hetus_wide[slot_cols].to_numpy().flatten()
new_vals  = hetus_30min[act30_cols].to_numpy().flatten()

print("\nV3 — Activity distribution comparison:")
print(f"  {'Code':>6} | {'hetus_wide%':>12} | {'hetus_30min%':>12} | {'diff_pp':>8} | Status")
all_pass = True
for code in sorted(pd.Series(wide_vals).dropna().unique()):
    pct_wide = 100 * (wide_vals == code).mean()
    pct_new  = 100 * (new_vals  == code).mean()
    diff     = abs(pct_wide - pct_new)
    status   = "PASS" if diff <= 1.0 else "FAIL"
    if status == "FAIL": all_pass = False
    print(f"  {int(code):>6} | {pct_wide:>11.2f}% | {pct_new:>11.2f}% | {diff:>7.2f}pp | {status}")
print(f"V3 {'PASS' if all_pass else 'FAIL'} — all categories within ±1 pp: {all_pass}")
```

---

**Task #22 — V4: Weighted AT_HOME rate per cycle within ±1 pp**

```python
expected = {2005: 62.7, 2010: 62.3, 2015: 64.5, 2022: 70.6}
hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
print("\nV4 — Weighted AT_HOME rate per cycle:")
print(f"  {'Cycle':>6} | {'Expected%':>10} | {'Actual%':>10} | {'diff_pp':>8} | Status")
for cycle, exp_pct in expected.items():
    mask = hetus_30min["CYCLE_YEAR"] == cycle
    sub  = hetus_30min[mask]
    w    = sub["WGHT_PER"]
    home_vals = sub[hom30_cols].to_numpy(dtype=float)
    wtd_rate  = 100 * np.average(home_vals.flatten(), weights=np.repeat(w.values, 48))
    diff = abs(wtd_rate - exp_pct)
    status = "PASS" if diff <= 1.0 else "FAIL"
    print(f"  {cycle:>6} | {exp_pct:>9.1f}% | {wtd_rate:>9.2f}% | {diff:>7.2f}pp | {status}")
```

---

**Task #23 — V5: Night slot plausibility (slots 1–8)**

Slots 1–8 correspond to 04:00–07:59 AM. Sleep should dominate.

```python
# Find the integer code for Sleep in BEM_PRIORITY (rank 1)
sleep_code = [k for k, v in BEM_PRIORITY.items() if v == 1][0]

night_act_cols = [f"act30_{i:03d}" for i in range(1, 9)]
night_hom_cols = [f"hom30_{i:03d}" for i in range(1, 9)]

night_act_vals = hetus_30min[night_act_cols].to_numpy().flatten()
night_hom_vals = hetus_30min[night_hom_cols].to_numpy(dtype=float).flatten()

sleep_pct  = 100 * (night_act_vals == sleep_code).mean()
athome_pct = 100 * np.nanmean(night_hom_vals)

print(f"\nV5 — Night slots (1–8, 04:00–07:59):")
print(f"  Sleep rate  : {sleep_pct:.1f}%  (threshold ≥ 70%)  → {'PASS' if sleep_pct  >= 70 else 'FAIL'}")
print(f"  AT_HOME rate: {athome_pct:.1f}% (threshold ≥ 85%)  → {'PASS' if athome_pct >= 85 else 'FAIL'}")
```

---

**Task #24 — V6: 3-way tie rate < 5%**

This reuses the `n_ties` variable computed in Task #9. Add an assertion and final print:

```python
total_cells = n * 48
tie_rate_pct = 100 * n_ties / total_cells
print(f"\nV6 — 3-way tie rate: {n_ties:,} / {total_cells:,} = {tie_rate_pct:.2f}%")
assert tie_rate_pct < 5.0, f"Tie rate {tie_rate_pct:.2f}% exceeds 5% threshold"
print(f"V6 PASS — tie rate < 5%")
```

---

**Task #25 — V7: DDAY_STRATA distribution unchanged**

```python
dist_wide = hetus_wide["DDAY_STRATA"].value_counts().sort_index()
dist_30   = hetus_30min["DDAY_STRATA"].value_counts().sort_index()
match = dist_wide.equals(dist_30)
print(f"\nV7 — DDAY_STRATA distribution match: {'PASS' if match else 'FAIL'}")
print(pd.DataFrame({"hetus_wide": dist_wide, "hetus_30min": dist_30}))
```

---

**Task #26 — V8: Manual spot-check 5 random respondents**

```python
import random
random.seed(42)
sample_indices = random.sample(range(n), 5)
slot_cols = [f"slot_{i:03d}" for i in range(1, 145)]

print("\nV8 — Manual spot-check (5 random respondents, first 6 slots shown):")
for idx in sample_indices:
    occ_id = hetus_30min.iloc[idx]["occID"]
    print(f"\n  occID={occ_id} (row {idx})")
    print(f"  {'30min_slot':>12} | {'src_A':>6} | {'src_B':>6} | {'src_C':>6} | {'act30':>6} | {'hom30':>6}")
    for s in range(1, 7):  # check first 6 of 48 slots
        src_a = hetus_wide.iloc[idx][f"slot_{3*(s-1)+1:03d}"]
        src_b = hetus_wide.iloc[idx][f"slot_{3*(s-1)+2:03d}"]
        src_c = hetus_wide.iloc[idx][f"slot_{3*s:03d}"]
        act30_val = hetus_30min.iloc[idx][f"act30_{s:03d}"]
        hom30_val = hetus_30min.iloc[idx][f"hom30_{s:03d}"]
        print(f"  act30_{s:03d}    | {src_a!s:>6} | {src_b!s:>6} | {src_c!s:>6} | {act30_val!s:>6} | {hom30_val!s:>6}")
print("\nV8 — Review the table above manually to confirm majority vote is correct.")
```

---

## Execution Order Summary

```
#1 (skeleton) ──────────────────────────────────────────────────────┐
#2 (BEM_PRIORITY)                                                   │
  │                                                                  │
  ├── #3 (load) → #4 (split cols)                                   │
  │                   ├── #5 (act matrix) → #7 (reshape) ──┐        │
  │                   │                                     ├── #8 (nanmode helper, from #1)
  │                   │                                     └── #9 (apply nanmode)
  │                   │                                           └── #12 (detect ties)
  │                   │                                                 └── #13 (resolve ties, needs #2)
  │                   │                                                       └── #14 (act30_df)
  │                   │                                                              └──┐
  │                   └── #6 (home matrix) → #10 (reshape) → #11 (binary vote)         │
  │                                                               └── #15 (hom30_df) ──┘
  │                                                                         └── #16 (concat)
  │                                                                               └── #17 (write CSV)
  │                                                                                     └── #18 (summary)
  │                                                                                     └── V1–V8 (#19–#26)
```

---

## Quick Reference: Key Variable Names

| Variable | Shape | Description |
|----------|-------|-------------|
| `act_arr` | (64061, 144) | Raw activity matrix from hetus_wide |
| `hom_arr` | (64061, 144) | Raw AT_HOME matrix from hetus_wide |
| `act_3d` | (64061, 48, 3) | Activity reshaped for majority vote |
| `hom_3d` | (64061, 48, 3) | AT_HOME reshaped for majority vote |
| `act_30` | (64061, 48) | Activity after majority vote + tie resolution |
| `hom_30` | (64061, 48) | AT_HOME after binary majority |
| `act30_df` | (64061, 48) | DataFrame, cols `act30_001`–`act30_048`, Int16 |
| `hom30_df` | (64061, 48) | DataFrame, cols `hom30_001`–`hom30_048`, Int8 |
| `hetus_30min` | (64061, meta+96) | Final output DataFrame |
| `tie_mask` | (64061, 48) | Boolean mask of 3-way tie positions |
| `BEM_PRIORITY` | dict[int, int] | Activity code → priority rank (1=highest) |

---

---

# Phase I — Co-Presence Tiling: Task List for Implementation

**Script to modify:** `2J_docs_occ_nTemp/03_mergingGSS.py`
**Input files:**
- `2J_docs_occ_nTemp/outputs_step3/merged_episodes.csv`
- `2J_docs_occ_nTemp/outputs_step3/hetus_30min.csv` (for occID order reference)

**Output file:** `2J_docs_occ_nTemp/outputs_step3/copresence_30min.csv`

---

## Background (read before implementing)

`merged_episodes.csv` has ~**1,049,480 rows** (one per episode) and includes 9 co-presence columns:
`Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues`

Values: **1 = present/Yes**, **2 = absent/No**, **NaN = not applicable or missing**
Special case: `colleagues` is entirely NaN for 2005/2010 respondents (variable not measured in those cycles).

Timing columns: `startMin` (episode start in minutes from 4:00 AM, 0-based) and `endMin` (exclusive end in minutes from 4:00 AM).

The goal is to produce `copresence_30min.csv` with **64,061 rows** (one per respondent) and **433 columns**:
- `occID`
- `Alone30_001` … `Alone30_048` (48 slots)
- `Spouse30_001` … `Spouse30_048`
- `Children30_001` … `Children30_048`
- `parents30_001` … `parents30_048`
- `otherInFAMs30_001` … `otherInFAMs30_048`
- `otherHHs30_001` … `otherHHs30_048`
- `friends30_001` … `friends30_048`
- `others30_001` … `others30_048`
- `colleagues30_001` … `colleagues30_048` (NaN for 2005/2010 rows)

**Two-stage approach:**
1. Episode → 144 × 10-min slots (same tiling logic as Phase F for activity/AT_HOME)
2. 144-slot → 48-slot downsampling (same binary majority logic as Phase H for hom30)

**All Phase I code goes into `03_mergingGSS.py` as a new `tile_copresence_to_30min()` function**, added after Phase H. Also call it from `main()` after Phase H.

---

## Task List

Tasks must be done in order within each group.

---

### GROUP 7 — Setup (do first)

---

**Task #27 — Add Phase I function skeleton**

In `03_mergingGSS.py`, after the Phase H block, add:

```python
# ── Phase I — Co-Presence Tiling (episode → 48-slot 30-min format) ───────────

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
    pass  # implementation added in subsequent tasks
```

Also add the call in `main()` after Phase H:

```python
# Phase I: Co-presence tiling
copresence_30min = tile_copresence_to_30min()
```

---

**Task #28 — Define COP_COLS constant**

At the top of the Phase I section, add:

```python
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues"
]
```

Confirm these match the exact column headers in `merged_episodes.csv` before proceeding.

---

### GROUP 8 — Load inputs (I.1 + I.2, sequential)

---

**Task #29 — I.1: Load merged_episodes.csv and verify**

Inside `tile_copresence_to_30min()`, replace `pass` with:

```python
print("\n── Phase I: Co-Presence Tiling (episode → 30-min slots) ──────")
ep_path = Path("outputs_step3") / "merged_episodes.csv"
episodes = pd.read_csv(ep_path, low_memory=False)
print(f"  Loaded: {len(episodes):,} episode rows")

# Verify required columns
required_cols = ["occID", "startMin", "endMin", "CYCLE_YEAR"] + COP_COLS
missing = [c for c in required_cols if c not in episodes.columns]
assert not missing, f"Missing columns: {missing}"

n_unique_occ = episodes["occID"].nunique()
print(f"  Unique occIDs in episodes: {n_unique_occ:,}")  # expect 64,061
```

---

**Task #30 — I.2: Load hetus_30min.csv for occID order**

```python
ref_path = Path("outputs_step3") / "hetus_30min.csv"
ref_df = pd.read_csv(ref_path, usecols=["occID", "CYCLE_YEAR"], low_memory=False)
occid_order = ref_df["occID"].tolist()         # ordered list of 64,061 occIDs
occid_to_idx = {oid: i for i, oid in enumerate(occid_order)}
n = len(occid_order)
print(f"  Reference occID order loaded: {n:,} respondents")
assert n == 64_061, f"Expected 64,061, got {n}"
```

---

### GROUP 9 — Tiling loop: episode → 144-slot 10-min arrays (I.3, sequential)

---

**Task #31 — I.3a: Pre-allocate 9 × (64,061 × 144) NaN arrays**

```python
# One float64 array per co-presence column
cop_10min = {col: np.full((n, 144), np.nan, dtype=float) for col in COP_COLS}
print(f"  Pre-allocated 9 arrays of shape ({n}, 144)")
```

---

**Task #32 — I.3b: Sort episodes and build group index**

```python
# Sort by occID for sequential group access (faster than groupby)
episodes_sorted = episodes.sort_values("occID").reset_index(drop=True)

# Build group boundary index: occid → (start_row, end_row)
grp = episodes_sorted.groupby("occID", sort=False)
grp_indices = {oid: (grp.indices[oid].min(), grp.indices[oid].max() + 1)
               for oid in grp.groups}
print(f"  Episode group index built for {len(grp_indices):,} occIDs")
```

---

**Task #33 — I.3c: Tiling loop — fill 10-min slot arrays**

```python
# Extract needed arrays for speed
occ_ids_ep   = episodes_sorted["occID"].to_numpy()
start_mins   = episodes_sorted["startMin"].to_numpy(dtype=float)
end_mins     = episodes_sorted["endMin"].to_numpy(dtype=float)
cop_vals     = {col: episodes_sorted[col].to_numpy(dtype=float) for col in COP_COLS}

print("  Tiling episodes to 10-min slots...")
for resp_idx, occ_id in enumerate(occid_order):
    if resp_idx % 10_000 == 0:
        print(f"    {resp_idx:,} / {n:,}")
    if occ_id not in grp_indices:
        continue  # no episodes (should not occur; log if it does)
    row_start, row_end = grp_indices[occ_id]
    for ep_row in range(row_start, row_end):
        s_min = start_mins[ep_row]
        e_min = end_mins[ep_row]
        # Handle endMin=0 wrap (episode ends at/after midnight)
        if e_min == 0 or (e_min < s_min):
            e_min = 1440.0
        slot_s = int(s_min) // 10        # 0-indexed start slot
        slot_e = int(e_min) // 10        # 0-indexed exclusive end slot
        slot_e = min(slot_e, 144)        # clamp to array bounds
        for col in COP_COLS:
            val = cop_vals[col][ep_row]
            if not np.isnan(val):
                cop_10min[col][resp_idx, slot_s:slot_e] = val

print("  Tiling complete.")
```

> **Performance note:** If the Python loop is too slow (>10 min), vectorise using numpy advanced indexing: pre-build a (n_episodes × 144) boolean mask and use `np.where` with broadcast. Discuss with the implementation agent if needed.

---

### GROUP 10 — Downsample 144 → 48 slots (I.4, runs after GROUP 9)

---

**Task #34 — I.4a: Reshape each (64,061 × 144) array to (64,061 × 48 × 3)**

```python
cop_3d = {}
for col in COP_COLS:
    cop_3d[col] = cop_10min[col].reshape(n, 48, 3)
    # Shape check
    assert cop_3d[col].shape == (n, 48, 3), f"Reshape failed for {col}"
print("  Reshaped all 9 arrays to (64061, 48, 3)")
```

---

**Task #35 — I.4b: Binary majority vote → (64,061 × 48) per column**

For co-presence values {1=present, 2=absent}: majority is 1 if ≥2 slots are 1, else 2.

```python
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
```

Expected: `colleagues` NaN count ≈ (19,221 + 15,114) × 48 = ~1,648,080 (2005/2010 rows all-NaN).

---

### GROUP 11 — Assemble output DataFrame (I.5, runs after GROUP 10)

---

**Task #36 — I.5a: Build {ColName}30_NNN DataFrames with Int8 dtype**

```python
cop30_dfs = []
for col in COP_COLS:
    slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
    df_col = pd.DataFrame(cop_30[col], columns=slot_cols)
    # Cast to nullable Int8 (supports NaN)
    for c in slot_cols:
        df_col[c] = df_col[c].astype(pd.Int8Dtype())
    cop30_dfs.append(df_col)
    print(f"  {col}: built DataFrame {df_col.shape}")
```

---

**Task #37 — I.5b: Concatenate occID + all 9 DataFrames**

```python
occid_col = pd.DataFrame({"occID": occid_order})
copresence_30min = pd.concat([occid_col] + cop30_dfs, axis=1)
print(f"  copresence_30min shape: {copresence_30min.shape}")
# Expected: (64061, 433) — 1 occID + 9×48 = 433
assert copresence_30min.shape == (64_061, 433), f"Shape mismatch: {copresence_30min.shape}"
```

---

### GROUP 12 — Export (I.6, sequential, needs GROUP 11)

---

**Task #38 — I.6a: Write copresence_30min.csv**

```python
out_path = Path("outputs_step3") / "copresence_30min.csv"
print(f"\n  Writing {out_path} ...")
copresence_30min.to_csv(out_path, index=False)
size_mb = out_path.stat().st_size / 1e6
print(f"  Done. File size: {size_mb:.1f} MB")
return copresence_30min
```

---

**Task #39 — I.6b: Print post-export summary**

After the `tile_copresence_to_30min()` call in `main()`, add:

```python
print(f"\n── Phase I Summary ──────────────────────────────────────────")
print(f"  Rows             : {copresence_30min.shape[0]:,}")
print(f"  Total columns    : {copresence_30min.shape[1]}")
for col in COP_COLS:
    slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
    nan_total = copresence_30min[slot_cols].isna().sum().sum()
    print(f"  {col:>14}: NaN slots = {nan_total:,}")
```

---

### GROUP 13 — Validation checks (all need Task #38 to be done first)

All checks can be added as a `validate_copresence_30min()` function called from `main()` after Phase I.

---

**Task #40 — VI-1: Shape check**

```python
assert copresence_30min.shape[0] == 64_061, f"Row count: {copresence_30min.shape[0]}"
assert copresence_30min.shape[1] == 433, f"Col count: {copresence_30min.shape[1]}"
print("VI-1 PASS — shape (64061, 433)")
```

---

**Task #41 — VI-2: occID alignment with hetus_30min**

```python
hetus_occids = pd.read_csv("outputs_step3/hetus_30min.csv", usecols=["occID"])["occID"]
match = copresence_30min["occID"].equals(hetus_occids)
assert match, "occID mismatch between copresence_30min and hetus_30min"
print("VI-2 PASS — occID order matches hetus_30min exactly")
```

---

**Task #42 — VI-3: No all-NaN respondents for primary 8 columns**

```python
primary_cols = [c for c in COP_COLS if c != "colleagues"]
for col in primary_cols:
    slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
    all_nan_mask = copresence_30min[slot_cols].isna().all(axis=1)
    n_all_nan = all_nan_mask.sum()
    assert n_all_nan == 0, f"{col}: {n_all_nan} respondents have all-NaN across 48 slots"
print("VI-3 PASS — no all-NaN respondents for primary 8 co-presence columns")
```

---

**Task #43 — VI-4: colleagues NaN pattern by cycle**

```python
# Reload cycle info from hetus_30min for cycle filtering
ref_df = pd.read_csv("outputs_step3/hetus_30min.csv", usecols=["occID", "CYCLE_YEAR"])
coll_slots = [f"colleagues30_{i:03d}" for i in range(1, 49)]

# Merge cycle year into copresence_30min for this check
merged_check = copresence_30min[["occID"] + coll_slots].merge(ref_df, on="occID")

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
```

---

**Task #44 — VI-5: Value range check**

```python
all_slot_cols = [f"{col}30_{i:03d}" for col in COP_COLS for i in range(1, 49)]
vals = copresence_30min[all_slot_cols].stack().dropna().unique()
invalid = set(vals) - {1, 2}
assert not invalid, f"Unexpected values in co-presence slots: {invalid}"
print(f"VI-5 PASS — all non-NaN values ∈ {{1, 2}}")
```

---

**Task #45 — VI-6: Co-presence prevalence plausibility**

```python
for col, low, high in [("Alone", 30, 60), ("Spouse", 15, 45)]:
    slot_cols = [f"{col}30_{i:03d}" for i in range(1, 49)]
    vals = copresence_30min[slot_cols].to_numpy(dtype=float)
    pct_present = 100 * np.nanmean(vals == 1)
    status = "PASS" if low <= pct_present <= high else "WARN"
    print(f"VI-6 {col}: {pct_present:.1f}% present (expected {low}–{high}%) → {status}")
```

---

**Task #46 — VI-7: Manual spot-check 5 random respondents**

```python
import random
random.seed(42)
episodes_chk = pd.read_csv("outputs_step3/merged_episodes.csv", low_memory=False)
sample_ids = random.sample(occid_order, 5)
print("\nVI-7 — Manual spot-check (Alone30_001, slot 1 = 04:00–04:29 = 10-min slots 0,1,2)")
for occ_id in sample_ids:
    ep_sub = episodes_chk[episodes_chk["occID"] == occ_id].copy()
    # Get episode rows covering 10-min slots 0–2 (startMin 0–29)
    covering = ep_sub[(ep_sub["startMin"] < 30) | (ep_sub["endMin"] > 0)]
    src_vals = covering["Alone"].tolist()
    alone30_001 = copresence_30min.loc[copresence_30min["occID"] == occ_id, "Alone30_001"].values[0]
    print(f"  occID={occ_id}: source episode Alone vals near slot 1 = {src_vals} → Alone30_001 = {alone30_001}")
print("VI-7 — Review output above manually to confirm majority vote is correct.")
```

---

## Execution Order Summary (Phase I)

```
#27 (skeleton) ─────────────────────────────────────────────────────────┐
#28 (COP_COLS constant)                                                  │
  │                                                                       │
  ├── #29 (load episodes) ──────────────────────────────────────────┐    │
  ├── #30 (load occID order)                                        │    │
  │                                                                  │    │
  └── #31 (pre-allocate arrays)                                     │    │
       └── #32 (sort + group index) → #33 (tiling loop) ───────────┘    │
                                          └── #34 (reshape 3D)          │
                                               └── #35 (majority vote)  │
                                                    └── #36 (DataFrames) │
                                                         └── #37 (concat)│
                                                              └── #38 (write CSV)
                                                                   └── #39 (summary)
                                                                   └── VI-1–7 (#40–#46)
```

---

---

### GROUP 14 — Co-Presence Before/After Plot in `03_mergingGSS_val.py` (needs Task #38 to be done first)

---

**Task #47 — Add Section 8a: Co-Presence Prevalence Before vs. After 30-Min Tiling**

Add a new `validate_copresence_30min()` method to the `Step3Validator` class in `03_mergingGSS_val.py`, and register its output plot in `build_html_report()`.

**What the plot shows:**
- **Before** (episode level, from `merged_episodes.csv`): the prevalence of each co-presence column as a proportion of episodes where the person is present — this is the same signal as Plot 6b, but recomputed here for side-by-side comparison.
- **After** (30-min slot level, from `outputs_step3/copresence_30min.csv`): the proportion of 30-min slots where the column = 1, aggregated across all respondents per cycle.

The comparison reveals whether the majority-vote tiling preserves the prevalence signal or introduces systematic shifts (e.g., short solo-activity episodes being absorbed into adjacent co-presence episodes).

**Figure layout:** 2-row × 4-column grid.
- **Row 1:** one grouped bar per cycle (4 panels, one per cycle year: 2005 / 2010 / 2015 / 2022). Each panel shows 9 grouped bars (one per co-presence column), with two bars per column: blue = episode-level prevalence, orange = 30-min slot prevalence.
- **Row 2:** a single-panel delta plot (9 columns on x-axis, 4 lines one per cycle on y-axis) showing `slot_prevalence − episode_prevalence` in percentage points. A horizontal dashed line at 0 marks no change. Positive = more presence in tiled slots; negative = less.

**Plot key:** `"8a_copre_before_after"`

**Implementation steps inside `validate_copresence_30min()`:**

```python
def validate_copresence_30min(self) -> None:
    """Section 8a — Co-Presence Prevalence: Episode Level vs. 30-Min Slot Level."""
    print("\n--- Section 8: Co-Presence Before/After 30-Min Tiling ---")

    # 1. Load copresence_30min.csv
    cop_path = Path("outputs_step3") / "copresence_30min.csv"
    if not cop_path.exists():
        print("  [SKIP] copresence_30min.csv not found — run Phase I first.")
        return
    cop30 = pd.read_csv(cop_path, low_memory=False)

    # Need CYCLE_YEAR from hetus_30min to filter by cycle
    ref = pd.read_csv(Path("outputs_step3") / "hetus_30min.csv",
                      usecols=["occID", "CYCLE_YEAR"], low_memory=False)
    cop30 = cop30.merge(ref, on="occID", how="left")

    df = self.merged  # episode-level (merged_episodes.csv)

    # 2. Compute prevalence for each (col × cycle) pair — episode level and slot level
    episode_prev = {}   # {col: {cycle: pct}}
    slot_prev    = {}   # {col: {cycle: pct}}

    for col in COPRE_COLS:
        episode_prev[col] = {}
        slot_prev[col]    = {}
        slot_cols_30 = [f"{col}30_{i:03d}" for i in range(1, 49)]
        # Filter to only the slot columns that actually exist
        slot_cols_30 = [c for c in slot_cols_30 if c in cop30.columns]

        for cycle in CYCLES:
            # --- episode level ---
            sub_ep = df[(df["CYCLE_YEAR"] == cycle) & df[col].notna()] if col in df.columns else None
            if sub_ep is not None and len(sub_ep) > 0:
                episode_prev[col][cycle] = 100.0 * (sub_ep[col] == 1).mean()
            else:
                episode_prev[col][cycle] = float("nan")

            # --- slot level ---
            sub_sl = cop30[cop30["CYCLE_YEAR"] == cycle]
            if slot_cols_30 and len(sub_sl) > 0:
                vals = sub_sl[slot_cols_30].to_numpy(dtype=float)
                slot_prev[col][cycle] = 100.0 * float(
                    (vals == 1).sum() / (~np.isnan(vals)).sum()
                ) if (~np.isnan(vals)).sum() > 0 else float("nan")
            else:
                slot_prev[col][cycle] = float("nan")

    # 3. Build figure: 2 rows
    _apply_dark()
    fig8a = plt.figure(figsize=(22, 10))
    fig8a.suptitle(
        "Section 8a — Co-Presence Prevalence: Episode Level vs. 30-Min Slot Level\n"
        "Blue = episode prevalence (before tiling)  |  Orange = slot prevalence (after tiling)",
        fontsize=13, fontweight="bold"
    )
    gs = fig8a.add_gridspec(2, 4, hspace=0.45, wspace=0.3,
                             top=0.88, bottom=0.08, left=0.05, right=0.97)

    x = np.arange(len(COPRE_COLS))
    BAR_W = 0.35
    BLUE   = "#89b4fa"
    ORANGE = "#fab387"

    # Row 1: one panel per cycle
    for ci, cycle in enumerate(CYCLES):
        ax = fig8a.add_subplot(gs[0, ci])
        ep_vals  = [episode_prev[col].get(cycle, float("nan")) for col in COPRE_COLS]
        sl_vals  = [slot_prev[col].get(cycle, float("nan"))    for col in COPRE_COLS]

        ax.bar(x - BAR_W / 2, ep_vals, BAR_W, label="Episode (before)",
               color=BLUE,   edgecolor="#1e1e2e", linewidth=0.5)
        ax.bar(x + BAR_W / 2, sl_vals, BAR_W, label="Slot 30min (after)",
               color=ORANGE, edgecolor="#1e1e2e", linewidth=0.5)

        ax.set_title(str(cycle), fontsize=11, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(COPRE_COLS, rotation=40, ha="right", fontsize=7.5)
        ax.set_ylim(0, 100)
        ax.set_ylabel("% present (= 1)" if ci == 0 else "")
        ax.yaxis.grid(True, linestyle="--", alpha=0.25)
        if ci == 0:
            ax.legend(fontsize=8, loc="upper right")

    # Row 2: delta plot (slot − episode) all cycles on one panel
    ax_delta = fig8a.add_subplot(gs[1, :])  # spans all 4 columns
    CYCLE_COLORS_DELTA = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
    for ci, cycle in enumerate(CYCLES):
        deltas = [
            slot_prev[col].get(cycle, float("nan")) - episode_prev[col].get(cycle, float("nan"))
            for col in COPRE_COLS
        ]
        ax_delta.plot(x, deltas, marker="o", linewidth=2, markersize=6,
                      label=str(cycle), color=CYCLE_COLORS_DELTA[ci])

    ax_delta.axhline(0, color="#cdd6f4", linewidth=1.2, linestyle="--", alpha=0.6)
    ax_delta.set_xticks(x)
    ax_delta.set_xticklabels(COPRE_COLS, rotation=30, ha="right", fontsize=9)
    ax_delta.set_ylabel("Δ prevalence (slot − episode, pp)")
    ax_delta.set_title(
        "Δ Co-Presence Prevalence: 30-min slot − episode level  "
        "(values near 0 = tiling preserved the signal)",
        fontsize=11
    )
    ax_delta.yaxis.grid(True, linestyle="--", alpha=0.25)
    ax_delta.legend(title="Cycle", fontsize=9, ncol=4, loc="upper right")

    self.plots_b64["8a_copre_before_after"] = _b64(fig8a)
    print("  ✅ 8a: Co-presence before/after 30-min tiling chart generated.")
```

**Wiring into the report:**

1. Call the new method from `run()` (after `validate_copresence()` and the Section 7 block):

```python
self.validate_copresence_30min()
```

2. Add to `chart_sections` list in `build_html_report()` — append after the last `"6c_..."` entry:

```python
("8a_copre_before_after",
 "Section 8a — Co-Presence Prevalence: Episode Level vs. 30-Min Slot Level"),
```

**Validation checks to add (inline print statements):**

After computing `episode_prev` and `slot_prev`, print a pass/warn table:

```python
print(f"\n  {'Column':>14} | {'Cycle':>4} | {'Ep%':>6} | {'Slot%':>6} | {'Δpp':>6} | Status")
for col in COPRE_COLS:
    for cycle in CYCLES:
        ep  = episode_prev[col].get(cycle, float("nan"))
        sl  = slot_prev[col].get(cycle, float("nan"))
        if np.isnan(ep) or np.isnan(sl):
            continue
        delta = sl - ep
        status = "PASS" if abs(delta) <= 5.0 else "WARN"
        print(f"  {col:>14} | {cycle} | {ep:>5.1f}% | {sl:>5.1f}% | {delta:>+5.1f} | {status}")
```

Pass criterion: `|slot_prevalence − episode_prevalence| ≤ 5 percentage points` per column per cycle. Larger deltas suggest the majority-vote tiling is systematically shifting presence signals and warrant investigation.

**Dependencies:** Needs `copresence_30min.csv` (Task #38) and `hetus_30min.csv` (Phase H output).

---

## Quick Reference: Key Variable Names (Phase I)

| Variable | Shape / Type | Description |
|----------|-------------|-------------|
| `COP_COLS` | list[str], len=9 | Co-presence column names (unified GSS naming) |
| `episodes` | (~1,049,480 × 49) | Raw episode DataFrame from merged_episodes.csv |
| `occid_order` | list[int], len=64,061 | Ordered occID list from hetus_30min.csv |
| `occid_to_idx` | dict[int, int] | occID → row index in output arrays |
| `cop_10min` | dict[col → (64061, 144) float] | 10-min slot arrays per co-presence column |
| `cop_3d` | dict[col → (64061, 48, 3) float] | Reshaped for majority vote |
| `cop_30` | dict[col → (64061, 48) float] | After majority vote (values: 1.0, 2.0, NaN) |
| `cop30_dfs` | list[DataFrame (64061, 48)] | Per-column DataFrames before concatenation |
| `copresence_30min` | (64061, 433) | Final output DataFrame |
