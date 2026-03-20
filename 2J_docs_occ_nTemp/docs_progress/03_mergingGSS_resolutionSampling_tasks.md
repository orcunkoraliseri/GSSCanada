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
