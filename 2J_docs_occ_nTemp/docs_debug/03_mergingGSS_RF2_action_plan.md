# RED FLAG 2 — DDAY Encoding: Action Plan

**Date**: 2026-03-10
**Severity**: 🔴 Critical — Blocker for Step 4
**Status**: Investigation & Fix **COMPLETE**. 

---

## 0. Plain Language Summary

### ❓ What was the problem?

The pipeline needs to know, for each respondent, whether their diary day was a **weekday or weekend**. This is stored in the raw GSS data as two different variables:

| Variable | Categories | Meaning |
|----------|------------|---------|
| `DDAY` | 7 values (1=Sunday, 2=Monday, …, 7=Saturday) | Exact day of the week |
| `DVTDAY` | 3 values (1=Weekday, 2=Saturday, 3=Sunday) | Collapsed day type |

**Where each variable lives in the raw data (before any processing):**

| File | 2005/2010/2015 | 2022 |
|------|----------------|------|
| **Main file** | `DVTDAY` only (3 categories) | `DDAY` only (7 categories) |
| **Episode file** | ❌ Neither variable extracted by Step 1 | ❌ Neither variable extracted by Step 1 |

Step 2 (`02_harmonizeGSS.py`) mistakenly renamed `DVTDAY → DDAY` for **all four cycles**. The intent was to produce a unified `DDAY` column, but the content of that column fundamentally differed by cycle:

- For **2005/2010/2015**: the `DDAY` column in Step 2 outputs actually contained `DVTDAY` values `{1, 2, 3}`.
- For **2022**: the `DDAY` column contained the real 7-category day-of-week values `{1, 2, 3, 4, 5, 6, 7}`.

Then Step 3 (`03_mergingGSS.py`) mistakenly applied a 7-day mapping to derive `DAYTYPE` across all cycles, treating 1 and 7 as Weekend, and 2-6 as Weekday. Because 2005/2010/2015 contained 1, 2, 3 representing Weekday, Saturday, Sunday respectively, this mapping resulted in:

- **Weekday (DVTDAY=1)** → mapped to `Weekend` ❌
- **Saturday (DVTDAY=2)** → mapped to `Weekday` ❌
- **Sunday (DVTDAY=3)** → mapped to `Weekday` ❌

**Every single Weekday diary was labelled Weekend, and every Saturday/Sunday diary was labelled Weekday — for 81.7% of the total dataset.**

---

### ✅ How was it solved?

The 3-category `DVTDAY` variable is sufficient to accurately derive whether a day is a Weekday or Weekend. The fix was placed entirely in **Step 3 (`03_mergingGSS.py`)** without needing to alter Step 1 or Step 2.

We made the `DAYTYPE` derivation cycle-aware by standardizing the 2022 data into the 3-category format `DDAY_STRATA` ({1: Weekday, 2: Saturday, 3: Sunday}), aligning it with the other cycles. 

---

## 1. Verified Findings (Post-Investigation)

### 1.1 Codebook Verification

All four GSS codebooks confirm that `DVTDAY` represents Type of Day, and `DDAY` represents Day of Week. However, Step 1 did not pull `DDAY` from the episode files for the older cycles.

### 1.2 Data-Level Confirmation

**Step 1 output files — which day variable is present:**

| File | 2005 | 2010 | 2015 | 2022 |
|------|------|------|------|------|
| main | `DVTDAY` {1,2,3} | `DVTDAY` {1,2,3} | `DVTDAY` {1,2,3} | `DDAY` {1..7} |
| episode | ❌ none | ❌ none | ❌ none | ❌ none |

**Step 2 "DDAY" output distributions (post-rename):**

```text
main_2005 "DDAY":  {1: 13882 (70.8%), 2: 2735 (14.0%), 3: 2980 (15.2%)}  ← DVTDAY!
main_2010 "DDAY":  {1: 11023 (71.6%), 2: 2111 (13.7%), 3: 2256 (14.7%)}  ← DVTDAY!
main_2015 "DDAY":  {1: 12295 (70.7%), 2: 2476 (14.2%), 3: 2619 (15.1%)}  ← DVTDAY!
main_2022  DDAY:   {1: 1823, 2: 1931, 3: 1782, 4: 1712, 5: 1789, 6: 1680, 7: 1619}  ✅ Real DDAY
```

The three-value pattern with ~70% in category 1 is the explicit fingerprint of `DVTDAY`.

---

## 2. Implemented Code Fixes

**File**: `03_mergingGSS.py`

**Phase E Logic Modified:** 
Standardized temporal features using `_DDAY_STRATAMAP_2022` to convert 2022's 7-category DDAY to the 3-category stratum ({1=Weekday, 2=Saturday, 3=Sunday}):
```python
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
```

Implementation applied only to 2022 because older cycles already exist in the 3-category format:
```python
    # DDAY_STRATA: 3-category day-of-week stratum (1=Weekday, 2=Saturday, 3=Sunday)
    mask_2022 = df["CYCLE_YEAR"] == 2022
    df["DDAY_STRATA"] = df["DDAY"].astype(int)
    df.loc[mask_2022, "DDAY_STRATA"] = df.loc[mask_2022, "DDAY"].map(_DDAY_STRATAMAP_2022)

    # DAYTYPE: Weekday / Weekend derived from the 3-category DDAY_STRATA
    df["DAYTYPE"] = df["DDAY_STRATA"].map(_DAYTYPE_MAP)
```

---

## 3. Verification & Results

A python verification script confirmed proper distributions for both `DAYTYPE` and `DDAY_STRATA` across all 4 cycles inside `merged_episodes.csv` post-fix.

**Results:**
- **2005**: Weekday (70.9%), Weekend (29.1%)
- **2010**: Weekday (71.7%), Weekend (28.3%)
- **2015**: Weekday (70.7%), Weekend (29.3%)
- **2022**: Weekday (72.1%), Weekend (27.9%)

The bug has been thoroughly resolved and `DAYTYPE` is now a safe variable to be used conditionally downstream by the Generative Model in Step 4.
