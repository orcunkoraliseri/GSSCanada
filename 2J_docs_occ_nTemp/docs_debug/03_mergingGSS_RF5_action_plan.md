# RED FLAG 5 — COW (Class of Worker) Variable Missing from Outputs: Action Plan

**Date**: 2026-03-10
**Severity**: 🟡 Notable — Blocker for Step 4 model conditioning
**Status**: 🔍 Investigation COMPLETE. Fix **pending decision**.

---

## 0. Plain Language Summary (Read This First)

### ❓ What is the problem?

The pipeline overview (`00_GSS_Occupancy_Documentation.md`) identifies **COW (Class of Worker)** as a key demographic variable for conditioning the occupancy model — distinguishing self-employed respondents from salaried employees or people not in the labor force.

The Red Flags document (`03_mergingGSS_flags.md`) originally identified this as a simple rename problem: Step 2 collected employment-related columns but never unified them under a common `COW` name. The proposed fix was:

> *"Add a final rename step that maps `WKWE` → `COW` (2005/2010), `WET_110` → `COW` (2015), `WET_120` → `COW` (2022)."*

**This fix was incorrect.** A deeper investigation reveals that the variables are **not the same construct** across cycles, and the situation is more nuanced than a simple rename.

---

### ⚠️ Two Separate Problems (After Investigation)

The investigation (run on 2026-03-10) revealed two distinct sub-problems:

**Problem 1 — Wrong variable named as COW (all cycles)**
`WKWE` (2005/2010) and `WET_110` (2015) are **weeks worked per year** (values 1–52), not class of worker. Renaming them to `COW` would be a semantic error.

**Problem 2 — A true COW variable exists for 2015 and 2022, but was never harmonized**
`WHW_110` (2015) and `WET_120` (2022) are genuine class-of-worker variables. Both were correctly extracted by Step 1 and both survive into Step 2 outputs — but neither was ever mapped to a unified `COW` column in Step 2. They sit silently in the data, unused.

**Problem 3 — COW availability for 2005/2010 is unknown**
No class-of-worker variable appears in the 2005 or 2010 Step 1 raw outputs. It is unclear whether this is because (a) no such variable exists in those cycles' PUMF, or (b) the variable exists in the raw SAS files but was not added to `MAIN_COLS_2005`/`MAIN_COLS_2010` in `01_readingGSS.py`.

---

## 1. Investigation Findings

### 1.1 Variable Inventory: What Was Found Per Cycle

| Cycle | Variable | In Step 1 output? | In Step 2 output? | What it actually measures | Values |
|-------|----------|--------------------|--------------------|-----------------------------|--------|
| 2005 | `WKWE` | ✅ Yes | ✅ Yes (as-is) | **Weeks worked** per year | 1–52, 97/98/99 |
| 2010 | `WKWE` | ✅ Yes | ✅ Yes (as-is) | **Weeks worked** per year | 1–52, 97/98/99 |
| 2015 | `WET_110` | ✅ Yes | ✅ Yes (as-is) | **Weeks worked** per year | 1–52, 96/97/98/99 |
| 2015 | `WHW_110` | ✅ Yes | ✅ Yes (as-is) | **Class of Worker** | 1, 2, 6, 7/8/9 |
| 2022 | `WET_120` | ✅ Yes | ✅ Yes (as-is) | **Class of Worker** | 1, 2, 3, 6, 9 |
| 2005 | *COW equivalent* | ❌ Not found | ❌ Not found | Unknown — needs codebook check | — |
| 2010 | *COW equivalent* | ❌ Not found | ❌ Not found | Unknown — needs codebook check | — |

---

### 1.2 WHW_110 (2015) vs WET_120 (2022) — Value Distributions

```
2015 WHW_110 (Class of Worker at Main Job):
  1:    622  ( 3.6%)   ← Self-employed (with paid help)
  2:  7,863  (45.2%)   ← Employee / paid worker
  6:  8,853  (50.9%)   ← Not applicable (non-employed respondents)
  7:      2  ( 0.0%)   ← Valid skip
  8:      1  ( 0.0%)   ← Not stated
  9:     49  ( 0.3%)   ← Don't know / refusal

2022 WET_120 (Class of Worker at Main Job):
  1:  5,976  (48.4%)   ← Employee / paid worker
  2:  1,275  (10.3%)   ← Self-employed, with paid employees
  3:     28  ( 0.2%)   ← Self-employed, without paid employees
  6:  5,015  (40.7%)   ← Not applicable (non-employed respondents)
  9:     42  ( 0.3%)   ← Not stated
```

**Important**: The code values are **not consistent** across cycles. In 2015, code `1 = self-employed` and `2 = employee`. In 2022, `1 = employee` and `2 = self-employed (with employees)`. A direct merge without remapping would silently swap these categories.

---

### 1.3 What WHW_110 and WET_120 Measure (Unified Interpretation)

Both variables measure the respondent's **relationship to their employer** at their main job. Despite different coding schemes, they capture the same underlying distinction: **employee vs. self-employed vs. not employed**.

Proposed unified 3-category harmonized scheme (`COW`):

| COW | Meaning | 2015 `WHW_110` codes | 2022 `WET_120` codes |
|-----|---------|----------------------|----------------------|
| 1 | Employee (paid worker for someone else) | 2 | 1 |
| 2 | Self-employed (with or without paid help) | 1 | 2, 3 |
| 3 | Not applicable / not at paid work | 6 → NaN | 6 → NaN |
| NaN | Sentinel (not stated, skip, DK) | 7, 8, 9 | 9 |

---

### 1.4 What WKWE / WET_110 Actually Are

`WKWE` (2005/2010) and `WET_110` (2015) are **"Weeks Worked in Past 12 Months"** — a continuous/ordinal variable counting how many weeks of the previous year the respondent was employed. Valid values run 1–52; sentinel codes 96/97/98/99 indicate not applicable, not stated, or don't know.

These are separate, valid demographic variables for measuring **labour market attachment intensity** (how consistently the person worked). They should be retained under a corrected harmonized name `WKSWRK`.

---

### 1.5 COW Availability for 2005/2010: Still Unknown

No column with ≤ 10 unique values matching a class-of-worker pattern was found in the 2005 or 2010 Step 1 raw outputs. However, since Step 1 uses **explicit column selection lists** (`MAIN_COLS_2005`, `MAIN_COLS_2010`), a COW variable could exist in the raw SAS files but simply not have been added to those lists.

**This requires a codebook verification step** — see Section 3 below.

---

## 2. Root Cause Summary

| Error | Location | Description |
|-------|----------|-------------|
| Wrong variable named COW | `03_mergingGSS_flags.md` (original diagnosis) | `WKWE`/`WET_110` are weeks worked, not class of worker |
| True COW variables not harmonized | `02_harmonizeGSS.py` | `WHW_110` (2015) and `WET_120` (2022) exist in Step 2 outputs but are not renamed/recoded to a unified `COW` column |
| Code values differ across cycles | `WHW_110` vs `WET_120` | A direct rename without value remapping would swap employee/self-employed labels between 2015 and 2022 |
| 2005/2010 COW availability unknown | `01_readingGSS.py` | Step 1 extraction lists do not include any COW variable for those cycles; raw SAS files not yet verified |

---

## 3. Remaining Investigation: 2005 and 2010

### 3.1 Action

Check the raw SAS file column headers (or the published GSS PUMF codebooks) for 2005 and 2010 to determine whether a class-of-worker variable was included in the PUMF release.

In Statistics Canada's GSS naming conventions, the 2005/2010 variable would likely be named:
- `WHW_10A` or `WHW_10B` — "class of worker" or "type of employment arrangement"
- Or similar `WHW*` prefix following the 2015 `WHW_110` naming pattern

### 3.2 How to Check Without SAS

If the raw SAS-derived CSVs contain **all** columns from the original file (not filtered), run:

```python
import pandas as pd

for cycle in [2005, 2010]:
    df = pd.read_csv(f'outputs/main_{cycle}.csv', nrows=0)
    cols = [c for c in df.columns if c.startswith('WH') or c.startswith('WET')]
    print(f'{cycle}: {cols}')
```

If those CSVs only contain columns from `MAIN_COLS_2005`/`MAIN_COLS_2010`, the raw SAS files must be inspected directly, or the Statistics Canada PUMF codebooks for GSS Cycle 19 (2005) and GSS Cycle 24 (2010) must be consulted.

---

## 4. Options for Resolution

### Option A — Harmonize WHW_110 and WET_120 as COW for 2015/2022; Check 2005/2010

This is the most data-rich option.

**Sub-steps**:
1. Add a `recode_cow()` function in `02_harmonizeGSS.py` that remaps `WHW_110` (2015) and `WET_120` (2022) to the unified 3-category `COW` scheme
2. Add `WHW_110 → COW` to `MAIN_RENAME_MAP` for 2015 and `WET_120 → COW` for 2022
3. Null sentinel codes (7, 8, 9 for 2015; 9 for 2022)
4. If a COW variable is found for 2005/2010: add it to `MAIN_COLS_2005`/`MAIN_COLS_2010`, re-run Step 1 for those cycles, and add recode
5. If no COW variable for 2005/2010: leave `COW = NaN` for those cycles (with a documentation note)
6. Add `COW` to `MAIN_COMMON_COLS` and `PERSON_COLS` in Step 3

**Trade-off**: Requires re-running Step 1 for 2005/2010 only if a COW variable is discovered. Step 2 re-run is always required for 2015 and 2022.

---

### Option B — Use LFTAG as COW Substitute (Cross-Cycle Fallback)

`LFTAG` (Labour Force Status) is already harmonized across all four cycles:
- `1 = Working at paid job`
- `2 = Going to school`
- `3 = Not employed`

This does not distinguish self-employed from salaried, but separates **employed from non-employed** — the dominant conditioning split for occupancy patterns.

**Steps**:
1. Document that true COW is available only for 2015 and 2022, and that `LFTAG` serves as the cross-cycle substitute
2. Keep `WHW_110` and `WET_120` in outputs under their current names (as supplementary variables)
3. Use `LFTAG` as the conditioning variable in Step 4

**Trade-off**: Loses the self-employed/employee distinction. No Step 1/2 re-run required.

---

### Option D — Correct WKWE/WET_110 Naming (Always Apply, Independent of COW Decision)

Regardless of which COW option is chosen, `WKWE` and `WET_110` must be renamed correctly in Step 2. They should not be called `COW` or left under ambiguous names.

In `02_harmonizeGSS.py`, update `MAIN_RENAME_MAP`:

```python
2005: { ..., "WKWE": "WKSWRK", ... },
2010: { ..., "WKWE": "WKSWRK", ... },
2015: { ..., "WET_110": "WKSWRK", ... },
```

Add sentinel nulling in `SENTINEL_MAP`:
```python
"WKSWRK": {96, 97, 98, 99},
```

This fix is **independent** of the COW decision and corrects a naming error that exists in the current outputs.

---

## 5. Recommended Resolution Path (Awaiting Decision)

| Step | Action | Depends on |
|------|--------|------------|
| 1 | Check 2005/2010 raw SAS headers or codebooks for a COW variable | — |
| 2 | Choose Option A or Option B for COW (see above) | Result of Step 1 |
| 3 | Always: Rename `WKWE`/`WET_110` → `WKSWRK` in Step 2 | Independent |
| 4 | Add `COW` (or document unavailability) in Step 3 `MAIN_COMMON_COLS` | Option A or B |
| 5 | Re-run Step 2 (always) and Step 1 for 2005/2010 (if COW found) | Option A path |
| 6 | Re-export `merged_episodes.csv` and `hetus_wide.csv` | After Step 2 re-run |
| 7 | Update RF5 status in `03_mergingGSS_flags.md` | After fix is complete |

---

## 6. Effort Estimate

| Task | Effort |
|------|--------|
| Codebook check for 2005/2010 COW availability | 20–30 min |
| Rename WKWE/WET_110 → WKSWRK in Step 2 | 15 min |
| Add recode_cow() for 2015 + 2022 in Step 2 | 30 min |
| Re-run Step 1 for 2005/2010 (only if COW found) | 15 min |
| Re-run Step 2 (all cycles) | 15 min |
| Add COW to Step 3, re-run Step 3 | 30 min |
| **Total (Option A, COW found for 2005/2010)** | **~2 hrs** |
| **Total (Option A, COW not found for 2005/2010)** | **~1.5 hrs** |
| **Total (Option B, LFTAG fallback)** | **~45 min** |

---

## 7. Impact on Step 4

Regardless of which option is chosen, Step 4 must be updated to condition on the available variable:

| Scenario | Conditioning Variable | Notes |
|----------|-----------------------|-------|
| COW harmonized for all cycles | `COW` (3-cat: employee/self-employed/N-A) | Richest conditioning |
| COW available for 2015+2022 only, NaN for 2005/2010 | `COW` with cycle-specific coverage | Partial; requires handling NaN in model |
| LFTAG fallback | `LFTAG` (3-cat: working/student/not-employed) | Coarser but fully cross-cycle consistent |

The **LFTAG fallback is already in the data** for all cycles. Self-employed respondents have different at-home patterns than employees, but the primary occupancy signal is the employed/not-employed split — which LFTAG captures fully.
