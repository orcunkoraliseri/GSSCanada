# RED FLAG 3 — NaN Activity Codes: Action Plan

**Date**: 2026-03-10
**Resolved**: 2026-03-19
**Severity**: 🟠 Important — Blocker for 2022 data quality
**Status**: ✅ RESOLVED. All activity codes mapped; validation logger added to pipeline.

---

## 0. Plain Language Summary (Read This First)

### ❓ What was the problem?

Every respondent's diary episode contains an **activity code** (`occACT`) that records what the person was doing during that time-slot (e.g., "Sleep", "Paid Work", "Eating"). This code is assigned by a **crosswalk table** stored in an Excel file that maps raw GSS activity codes to 14 unified internal categories.

After Step 2 harmonization, **2,395 episodes** — belonging to **1,829 out of 12,336 respondents (14.8%) in the 2022 cycle** — could not be mapped to any category, because 3 raw GSS codes were simply missing from the crosswalk table. These episodes were written with `occACT = NaN`.

A smaller number of 2010 episodes also had this problem (325 respondents, 2.1% of cycle), due to 3 other unmapped codes.

---

### ✅ How was it solved?

The root cause was 6 raw GSS codes (3 from 2022, 3 from 2010) missing from the crosswalk Excel file. The fix was placed in **Step 2 (`02_harmonizeGSS.py`)** and the activity crosswalk file.

We updated the Excel crosswalk to include these codes and implemented a validation check to catch future gaps.

---

## 1. Verified Findings (Post-Investigation)

### 1.1 NaN occACT Breakdown by Cycle (Pre-Fix)

| Cycle | NaN episodes | % of episodes | Respondents affected | % of cycle |
|-------|-------------|---------------|----------------------|------------|
| 2005 | 0 | 0.0% | 0 | 0.0% |
| 2010 | 425 | 0.2% | 325 | 2.1% |
| 2015 | 0 | 0.0% | 0 | 0.0% |
| 2022 | 2,395 | 1.4% | 1,829 | **14.8%** |

### 1.2 The Unmapped Codes

| Cycle | Code | Description | Proposed Category |
|-------|------|-------------|-------------------|
| 2022 | **1105** | Arts, hobbies or playing games | `11` — Active Leisure |
| 2022 | **1303** | Doing nothing | `14` — Miscellaneous / Idle |
| 2022 | **1304** | Other activity | `14` — Miscellaneous / Idle |
| 2010 | **2.0** | Work-related fallback | `1` — Work-related |
| 2010 | **712.0** | Passive leisure | `10` — Passive Leisure |
| 2010 | **713.0** | Passive leisure | `10` — Passive Leisure |

---

## 2. Implemented Fixes

### 2.1 Excel Crosswalk Update
The file `references_activityCodes/Data Harmonization_activityCategories - execution.xlsx` was updated:
- 3 rows added to `2022codebook` (1105, 1303, 1304).
- 3 rows added to `2010codebook` (2.0, 712.0, 713.0).

### 2.2 Validation Logging in `02_harmonizeGSS.py`
The `validate_activity_crosswalk()` function was added to catch unmapped codes:

```python
def validate_activity_crosswalk(
    df: pd.DataFrame, cycle: int, raw_col: str
) -> None:
    """Log unmapped raw activity codes with their frequencies."""
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

---

## 3. Steps to Resolve

| # | Step | File | Status |
|---|------|------|--------|
| 1 | Identify unmapped codes from Step 3 logs | — | ✅ Done |
| 2 | Look up descriptions in GSS codebooks | — | ✅ Done |
| 3 | Add missing codes to Excel crosswalk | Excel | ✅ Done |
| 4 | Add validation check to `02_harmonizeGSS.py` | Python | ✅ Done |
| 5 | Re-run Step 2 for all cycles | — | ✅ Done |
| 6 | Re-run Step 3 | — | ✅ Done |

---

## 4. Validation Results (Post-Fix)

**Validated against `merged_episodes.csv`, 2026-03-19.**

- **Cycle 2005**: 0 NaN respondents ✅
- **Cycle 2010**: 0 NaN respondents ✅
- **Cycle 2015**: 0 NaN respondents ✅
- **Cycle 2022**: 0 NaN respondents ✅

The HETUS slot assignment Phase F now logs:
`NaN-slot respondents before ffill: 0, after: 0`

The bug has been thoroughly resolved and synthetic ffill bias has been removed from the 2022 training data.
