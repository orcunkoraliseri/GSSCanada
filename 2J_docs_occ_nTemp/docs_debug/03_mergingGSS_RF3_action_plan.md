# RED FLAG 3 — NaN Activity Codes: Action Plan

**Date**: 2026-03-10
**Severity**: 🟠 Important — Blocker for 2022 data quality
**Status**: ✅ **RESOLVED** (Investigation & Fix COMPLETE).

---

## 0. Plain Language Summary (Read This First)

### ❓ What is the problem?

Every respondent's diary episode contains an **activity code** (`occACT`) that records what the person was doing during that time-slot (e.g., "Sleep", "Paid Work", "Eating"). This code is assigned by a **crosswalk table** stored in an Excel file that maps raw GSS activity codes to 14 unified internal categories.

After Step 2 harmonization, **2,395 episodes** — belonging to **1,829 out of 12,336 respondents (14.8%) in the 2022 cycle** — could not be mapped to any category, because 3 raw GSS codes were simply missing from the crosswalk table. These episodes were written with `occACT = NaN`.

A smaller number of 2010 episodes also have this problem (325 respondents, 0.2% of 2010 episodes), due to 3 other unmapped codes.

---

### ⚠️ Why does this matter?

#### Connection to Phase F — HETUS Conversion

This is where the NaN values directly cause harm. In **Phase F** of `03_mergingGSS.py`, each respondent's episodes are spread across 144 fixed 10-minute time slots. The slot assignment algorithm writes `occACT` into the slot array. If an episode has `occACT = NaN`, the corresponding time slots get `NaN` values instead of a valid activity code:

```
Episode (respondent A, 2022):
  start=0800, duration=60, occACT=NaN   ← unmapped code
  → slot_025 to slot_030 all filled with NaN
```

The current code then applies a **forward-fill (`ffill`)** to patch these gaps silently:
```python
df_act = df_act.ffill(axis=1).bfill(axis=1)
```

This carries the *previous* activity code forward over the missing slots. While `ffill` is standard time-use practice for brief recording gaps, it is **scientifically wrong here** because the NaN slots represent real episodes with real activities that simply were not mapped — not gaps in recording. For example:
- A 60-minute slot for "Doing nothing" (TUI_01=1303) gets silently replaced by whatever the person was doing before it.
- A 60-minute slot for "Arts/hobbies/crafting" (TUI_01=1105) gets silently replaced with a prior activity.

The end result is that **14.8% of 2022 respondents have synthetic, inferred activity codes in some of their time slots**, which biases the 2022 activity distribution used to train the Step 4 Conditional Transformer.

---

### ✅ How to solve it?

The root cause is 3 raw GSS codes missing from the crosswalk Excel file. The fix is to add those 3 codes with their correct category assignments. This requires:

1. **Identify the 3 unmapped codes** (done — see Section 1 below).
2. **Determine their correct categories** from the 2022 GSSP codebook (done — see Section 2 below).
3. **Add 3 rows to the `2022codebook` sheet** in the Excel crosswalk file.
4. **Re-run Step 2** to regenerate `episode_2022.csv` with no NaN `occACT` values.
5. **Re-run Step 3** to regenerate `merged_episodes.csv` and `hetus_wide.csv` with clean slot assignments.

---

## 1. Verified Findings (Post-Investigation)

### 1.1 NaN occACT Breakdown by Cycle

| Cycle | NaN episodes | % of episodes | Respondents affected | % of cycle |
|-------|-------------|---------------|----------------------|------------|
| 2005 | 0 | 0.0% | 0 | 0.0% |
| 2010 | 425 | 0.2% | 325 | 2.1% |
| 2015 | 0 | 0.0% | 0 | 0.0% |
| 2022 | 2,395 | 1.4% | 1,829 | **14.8%** |

### 1.2 The 3 Unmapped 2022 Codes

These are the **only** 3 codes out of 121 total `TUI_01` codes in the 2022 GSSP that are missing from the crosswalk:

| TUI_01 Code | Description (from 2022 GSSP codebook) | Episodes | % of 2022 | Proposed Category |
|-------------|---------------------------------------|----------|-----------|-------------------|
| **1105** | Arts, hobbies or playing games (drawing, painting, crafting) | 1,236 | 0.74% | `11` — Active Leisure |
| **1303** | Doing nothing | 977 | 0.58% | `14` — Miscellaneous / Idle |
| **1304** | Other activity | 182 | 0.11% | `14` — Miscellaneous / Idle |

**Total unmapped episodes: 2,395 (1.43% of all 2022 episodes)**

### 1.3 The 3 Unmapped 2010 Codes

| Raw Code | Description (from 2010 episode file) | Episodes | Proposed Category |
|----------|--------------------------------------|----------|-------------------|
| **2.0** | Appears as a bare numeric code (likely a parsing/float issue with the crosswalk) | 309 | Investigate — may be a rounding artefact |
| **712.0** | Passive leisure / watching (unconfirmed) | 100 | `10` — Passive Leisure |
| **713.0** | Passive leisure / listening (unconfirmed) | 16 | `10` — Passive Leisure |

> [!NOTE]
> The 2010 issue (425 episodes, 2.1% of respondents) is much smaller in scale than 2022. The `2.0` code is suspicious — it may be a float parsing side-effect rather than a true GSS code 2. This should be verified against the 2010 ACTCODE codebook.

---

## 2. How This Happened — Root Cause

### Step 2 Activity Crosswalk Process

In `02_harmonizeGSS.py`, the function `apply_activity_crosswalk()` maps raw episode activity codes to the unified 14-category scheme using a lookup dictionary built from the Excel file:

```python
def apply_activity_crosswalk(df, cycle, crosswalk):
    raw_col = "ACTCODE" if cycle in (2005, 2010) else "TUI_01"
    df["occACT"] = pd.to_numeric(df[raw_col], errors="coerce").map(crosswalk)
    # → Any code NOT in crosswalk.keys() maps to NaN
```

The crosswalk dictionary is built from the Excel sheet. If a code is not in the sheet, `.map()` returns `NaN` for that episode with **no warning or error**. The NaN simply passes silently through Step 2.

### Phase F HETUS Slot Assignment — Where NaN Propagates

In `03_mergingGSS.py`, `_build_slot_arrays()` writes the `occACT` value directly into the slot array:

```python
for _, ep in group.iterrows():
    act = ep["occACT"]   # ← this is NaN for the 3 unmapped codes
    for s in range(slot_start, min(slot_end, 144)):
        act_slots[f"slot_{s+1:03d}"] = act   # ← NaN written into slot
```

Later, `ffill` silently patches all NaN slots with the preceding valid activity:

```python
df_act = df_act.ffill(axis=1).bfill(axis=1)
```

The pipeline logs `NaN-slot respondents before ffill: 1988`, but does not flag this as a data quality issue — it is treated as a normal gap to fill. This is the silent failure mode of RED FLAG 3.

---

## 3. Proposed Fix

### Step 1 — Add the 3 Missing 2022 Codes to the Excel Crosswalk

Open the file:
```
references_activityCodes/Data Harmonization_activityCategories - execution.xlsx
```

Go to the `2022codebook` sheet and add the following 3 rows (columns: `Edited Main Category`, `Main Activity`):

| Edited Main Category | Main Activity | Explanation |
|----------------------|---------------|-------------|
| **11** | **1105** | Arts, hobbies or playing games (drawing, painting, crafting) → Active Leisure |
| **14** | **1303** | Doing nothing → Miscellaneous / Idle |
| **14** | **1304** | Other activity → Miscellaneous / Idle |

> [!IMPORTANT]
> The `1105` assignment to category 11 (Active Leisure) is consistent with adjacent codes such as `1106` (Leisure / outdoor activities: fishing, hunting, camping) and `1104` (Museums, zoos, etc.), which are mapped to `11` or `10`. The "arts, hobbies, games" description is an active engagement, so category `11` is the appropriate assignment.

> [!TIP]
> Cross-check with the 2022 GSSP codebook (`codebooks/Codebook_2022/TU_2022_Episode_PUMF.pdf`, page listing TUI_01 codes around 1100-1199) to confirm the exact descriptions before committing.

### Step 2 — Add Validation Logging to `02_harmonizeGSS.py`

After `apply_activity_crosswalk()`, add a check that logs any remaining unmapped codes **with frequencies**, so future crosswalk gaps are caught immediately:

```python
def validate_activity_crosswalk(
    df: pd.DataFrame, cycle: int, raw_col: str
) -> None:
    """Log unmapped raw activity codes with their frequencies.

    Args:
        df: Episode DataFrame after crosswalk application.
        cycle: Survey cycle year.
        raw_col: Name of the raw activity code column (e.g., 'TUI_01').
    """
    nan_mask = df["occACT"].isna() & df[raw_col].notna()
    if not nan_mask.any():
        print(f"  [{cycle}] All activity codes mapped. ✅")
        return

    unmapped = df.loc[nan_mask, raw_col].value_counts()
    n_eps = nan_mask.sum()
    n_resp = df.loc[nan_mask, "occID"].nunique()
    print(f"  [{cycle}] ⚠️  {n_eps} unmapped episodes in {n_resp} respondents:")
    for code, count in unmapped.items():
        pct = count / len(df) * 100
        print(f"    {raw_col}={code}: {count} episodes ({pct:.2f}%)")
```

Call this function in `harmonize_episode()` after `apply_activity_crosswalk()`:
```python
def harmonize_episode(df, cycle, act_crosswalk, pre_crosswalk):
    ...
    df = apply_activity_crosswalk(df, cycle, act_crosswalk)
    validate_activity_crosswalk(df, cycle, raw_col="ACTCODE" if cycle in (2005, 2010) else "TUI_01")
    ...
```

### Step 3 — Investigate 2010 Code `2.0`

Before modifying the 2010 crosswalk, verify whether `2.0` is a real ACTCODE or a float parsing artefact:

```python
# Quick diagnostic: what does ACTCODE=2.0 look like in raw Step 1 episode files?
df_raw_2010 = pd.read_csv("outputs/episode_2010.csv", low_memory=False)
print(df_raw_2010[df_raw_2010["ACTCODE"].astype(str).str.startswith("2.")][["ACTCODE"]].value_counts())
```

If `2.0` is indeed a real ACTCODE, look it up in the 2010 episode codebook (`codebooks/Codebook_2010/Episode_File_Data_Dictionary.txt`) and assign the appropriate category.

### Step 4 — Re-run Step 2

```bash
python 02_harmonizeGSS.py
```

Expected result: `validate_activity_crosswalk` logs `All activity codes mapped. ✅` for all cycles.

Post-run check:
```python
df2022 = pd.read_csv("outputs_step2/episode_2022.csv", low_memory=False)
assert df2022["occACT"].isna().sum() == 0, "Still unmapped codes!"
print("All 2022 episodes mapped. ✅")
```

### Step 5 — Re-run Step 3

```bash
python 03_mergingGSS.py
```

Expected result in Phase F log:
```
NaN-slot respondents before ffill: 0, after: 0
```

The `ffill` line can remain as a safety net for future genuine gaps, but it should now have nothing to fill.

---

## 4. Summary of Files Modified

| File | Change |
|------|--------|
| `references_activityCodes/Data Harmonization_activityCategories - execution.xlsx` | Add 3 rows to `2022codebook` sheet (codes 1105, 1303, 1304) |
| `02_harmonizeGSS.py` | Add `validate_activity_crosswalk()` function and call it in `harmonize_episode()` |
| `outputs_step2/episode_2022.csv` | Re-generated: 0 NaN `occACT` values |
| `outputs_step3/merged_episodes.csv` | Re-generated: no ffill artefacts |
| `outputs_step3/merged_episodes.parquet` | Re-generated |
| `outputs_step3/hetus_wide.csv` | Re-generated: no NaN-slot respondents before ffill |

---

## 5. Priority and Effort Estimate

| Task | Effort |
|------|--------|
| Add 3 rows to Excel crosswalk | 5 min |
| Add validation logger to `02_harmonizeGSS.py` | 20 min |
| Investigate 2010 code `2.0` | 15 min |
| Re-run Step 2 | ~3 min |
| Re-run Step 3 | ~10 min |
| Verify outputs | 10 min |
| **Total** | **~1 hour** |
