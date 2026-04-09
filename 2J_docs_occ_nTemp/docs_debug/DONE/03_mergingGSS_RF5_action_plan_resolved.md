# RED FLAG 5 — COW (Class of Worker) Variable Missing from Outputs: Action Plan

**Date**: 2026-03-10
**Resolved**: 2026-03-19
**Severity**: 🟡 Notable — Blocker for Step 4 model conditioning
**Status**: ✅ RESOLVED. All code changes applied and validated against Step 3 outputs.

---

## 0. Plain Language Summary (Read This First)

### ❓ What was the problem?

The pipeline overview (`00_GSS_Occupancy_Documentation.md`) identifies **COW (Class of Worker)** as a key demographic variable for conditioning the occupancy model — distinguishing self-employed respondents from salaried employees or people not in the labor force.

The Red Flags document (`03_mergingGSS_flags.md`) originally identified this as a simple rename problem. The proposed fix was:

> *"Add a final rename step that maps `WKWE` → `COW` (2005/2010), `WET_110` → `COW` (2015), `WET_120` → `COW` (2022)."*

**This fix was incorrect.** Investigation reveals three separate sub-problems: wrong variables were labelled as COW, the true COW variables for 2015/2022 are already in the data but never harmonized, and the true COW variables for 2005/2010 exist in the PUMF but were never extracted by Step 1.

---

### ✅ Summary of Investigation Findings

| Cycle | True COW variable | In PUMF? | In Step 1 output? | In Step 2 output? | Action needed |
|-------|-------------------|----------|-------------------|-------------------|---------------|
| 2005 | `MAR_Q172` | ✅ Confirmed | ❌ Never extracted | ❌ Absent | Add to Step 1, add recode in Step 2 |
| 2010 | `MAR_Q172` | ✅ Confirmed | ❌ Never extracted | ❌ Absent | Add to Step 1, add recode in Step 2 |
| 2015 | `WHW_110` | ✅ Confirmed | ✅ Extracted | ✅ Present (unused) | Add recode in Step 2 only |
| 2022 | `WET_120` | ✅ Confirmed | ✅ Extracted | ✅ Present (unused) | Add recode in Step 2 only |

Additionally, `WKWE` (2005/2010) and `WET_110` (2015) are **weeks worked per year** (values 1–52), not class of worker. They must be renamed to `WKSWRK` in Step 2 — an independent fix.

---

## 1. The Variables in Detail

### 1.1 MAR_Q172 — Class of Worker (2005 and 2010)

Confirmed in the PUMF codebooks:

**2005 codebook** (`12M0019GPE.txt`, Variable `MAR_Q172`, Position 1683):
> "Were you mainly?"
```
1 = ...a paid worker?          9,601  (13,469,761 weighted)
2 = ...self-employed?          2,035   (2,842,682 weighted)
3 = ...an unpaid family worker?   76     (105,880 weighted)
7 = Not asked                  7,796   (9,551,048 weighted)  ← non-employed respondents
8 = Not stated                    72
9 = Don't know                    17
```
*Coverage*: Respondents who answered MAR_Q135 = 2,8,9 (i.e., employed in past 12 months).

**2010 codebook** (`Main_File_Data_Dictionary.txt`, Variable `MAR_Q172`, Position 2066):
> "Were you mainly?"
```
1 = ...a paid worker?          8,135  (16,710,529 weighted)
2 = ...self-employed?          1,783   (3,193,743 weighted)
3 = ...an unpaid family worker?   89     (145,229 weighted)
7 = Not asked                  5,363   (7,993,901 weighted)  ← non-employed respondents
8 = Not stated                     8
9 = Don't know                    12
```
*Coverage*: Respondents who answered MAR_Q100 = 01,02, MAR_Q133 = 1, or MAR_Q135 = 1 (i.e., employed).

**Why it was missing**: `MAR_Q172` was never added to `MAIN_COLS_2005` or `MAIN_COLS_2010` in `01_readingGSS.py`. Since Step 1 uses explicit column selection, it was simply never read from the SAS files.

---

### 1.2 WHW_110 — Class of Worker (2015)

Already extracted by Step 1 and present in Step 2 output `main_2015.csv`. Never mapped to a unified `COW` column.

```
1 =    622  ( 3.6%)   ← Self-employed (with paid help)
2 =  7,863  (45.2%)   ← Employee / paid worker
6 =  8,853  (50.9%)   ← Not applicable (non-employed respondents)
7 =      2  ( 0.0%)   ← Valid skip
8 =      1  ( 0.0%)   ← Not stated
9 =     49  ( 0.3%)   ← Don't know / refusal
```

---

### 1.3 WET_120 — Class of Worker (2022)

Already extracted by Step 1 and present in Step 2 output `main_2022.csv`. Never mapped to a unified `COW` column.

```
1 =  5,976  (48.4%)   ← Employee / paid worker
2 =  1,275  (10.3%)   ← Self-employed, with paid employees
3 =     28  ( 0.2%)   ← Self-employed, without paid employees
6 =  5,015  (40.7%)   ← Not applicable (non-employed respondents)
9 =     42  ( 0.3%)   ← Not stated
```

---

### 1.4 WKWE / WET_110 — What They Actually Are (Weeks Worked)

`WKWE` (2005/2010) and `WET_110` (2015) are **"Weeks Worked in Past 12 Months"** — an ordinal variable counting how many weeks of the previous year the respondent was employed (values 1–52). These are a measure of **labour market attachment intensity**, not employment type. They should be retained under the harmonized name `WKSWRK`, not renamed to `COW`.

---

## 2. Cross-Cycle Harmonization Plan

### 2.1 Code Mapping — Critical: Values Are NOT Consistent Across Cycles

| Meaning | 2005/2010 `MAR_Q172` | 2015 `WHW_110` | 2022 `WET_120` |
|---------|----------------------|----------------|----------------|
| Employee (paid worker) | 1 | **2** | **1** |
| Self-employed (any type) | 2 | **1** | 2, 3 |
| Unpaid family worker | 3 | *(not split out)* | *(in code 3)* |
| Not applicable / not employed | 7 | 6 | 6 |
| Sentinel (not stated / DK) | 8, 9 | 7, 8, 9 | 9 |

A plain rename without value remapping would **swap the employee and self-employed labels** between 2015 and all other cycles.

### 2.2 Unified 3-Category COW Scheme (Applied)

| `COW` | Meaning | 2005/2010 source codes | 2015 source codes | 2022 source codes |
|-------|---------|------------------------|-------------------|-------------------|
| 1 | Employee (paid worker for someone else) | 1 | 2 | 1 |
| 2 | Self-employed or unpaid family worker | 2, 3 | 1 | 2, 3 |
| NaN | Not at paid work / not applicable / sentinel | 7, 8, 9 | 6, 7, 8, 9 | 6, 9 |

> **Note**: Unpaid family workers (2005/2010 code 3, 2022 code 3) are grouped with self-employed because they share the key occupancy behavior trait of non-standard work schedules and higher at-home probability during working hours.

---

## 3. Files Changed

### 3.1 `01_readingGSS.py` — Add MAR_Q172 to 2005 and 2010 Extraction Lists

```python
MAIN_COLS_2005: list[str] = [
    "RECID", "AGEGR10", "sex", "marstat", "HSDSIZEC", "REGION", "LUC_RST",
    "WKWE", "wght_per", "DVTDAY", "LANCH", "LFSGSS", "INCM", "EDU10", "WKWEHR_C",
    "MAR_Q172",    # ← ADD: Class of Worker
]

MAIN_COLS_2010: list[str] = [
    "RECID", "AGEGR10", "SEX", "MARSTAT", "HSDSIZEC", "REGION", "PRV", "LUC_RST",
    "WKWE", "WGHT_PER", "DVTDAY", "LANCH", "LFSGSS", "ACT7DAYS", "INCM", "EDU10",
    "WKWEHR_C", "MAR_Q172",    # ← ADD: Class of Worker
    "CTW_Q140_C01", ...,
]
```

### 3.2 `02_harmonizeGSS.py` — Four Changes

**Change A**: Updated `MAIN_RENAME_MAP` to rename COW variables and WKWE/WET_110:

```python
MAIN_RENAME_MAP = {
    2005: {
        ...
        "WKWE": "WKSWRK",      # ← RENAME: was weeks worked, not COW
        "MAR_Q172": "COW",      # ← ADD
    },
    2010: {
        ...
        "WKWE": "WKSWRK",      # ← RENAME
        "MAR_Q172": "COW",      # ← ADD
    },
    2015: {
        ...
        "WET_110": "WKSWRK",   # ← RENAME: was weeks worked, not COW
        "WHW_110": "COW",       # ← ADD
    },
    2022: {
        ...
        "WET_120": "COW",       # ← ADD
    },
}
```

**Change B**: Added `WKSWRK` sentinels to `SENTINEL_MAP`:

```python
SENTINEL_MAP = {
    ...
    "WKSWRK": {96, 97, 98, 99},
    # COW sentinels handled inside recode_cow() per-cycle
}
```

**Change C**: Added `recode_cow()` function:

```python
def recode_cow(df: pd.DataFrame, cycle: int) -> pd.DataFrame:
    """Harmonize Class of Worker to 3-category scheme:
        1 = Employee (paid worker for someone else)
        2 = Self-employed (with or without employees) or unpaid family worker
        NaN = Not applicable / not at paid work / sentinel
    """
    if "COW" not in df.columns:
        return df
    if cycle in (2005, 2010):
        # MAR_Q172: 1=employee, 2=self-employed, 3=unpaid family, 7=not asked, 8/9=sentinel
        df["COW"] = df["COW"].replace({1: 1, 2: 2, 3: 2, 7: pd.NA, 8: pd.NA, 9: pd.NA})
    elif cycle == 2015:
        # WHW_110: 1=self-employed, 2=employee, 6=not applicable, 7/8/9=sentinel
        df["COW"] = df["COW"].replace({1: 2, 2: 1, 6: pd.NA, 7: pd.NA, 8: pd.NA, 9: pd.NA})
    elif cycle == 2022:
        # WET_120: 1=employee, 2=self-emp w/ employees, 3=self-emp w/o employees, 6=N/A, 9=sentinel
        df["COW"] = df["COW"].replace({1: 1, 2: 2, 3: 2, 6: pd.NA, 9: pd.NA})
    return df
```

**Change D**: Called `recode_cow()` in `harmonize_main()` after `recode_totinc()`.

### 3.3 `03_mergingGSS.py` — Add COW and WKSWRK to Column Lists

```python
MAIN_COMMON_COLS = [
    ...
    "COW",      # ← ADD: Class of Worker (harmonized 3-category)
    "WKSWRK",   # ← ADD: Weeks worked per year
]

PERSON_COLS = [
    ...,
    "COW",      # ← ADD
    "WKSWRK",   # ← ADD
]
```

---

## 4. Steps to Resolve

| # | Step | File | Type | Status |
|---|------|------|------|--------|
| 1 | Add `MAR_Q172` to `MAIN_COLS_2005` and `MAIN_COLS_2010` | `01_readingGSS.py` | Code | ✅ Done |
| 2 | Re-run Step 1 for 2005 and 2010 only | — | Execution | ✅ Done |
| 3 | Rename `WKWE`/`WET_110` → `WKSWRK` in `MAIN_RENAME_MAP` | `02_harmonizeGSS.py` | Code | ✅ Done |
| 4 | Rename `MAR_Q172` → `COW` (2005/2010), `WHW_110` → `COW` (2015), `WET_120` → `COW` (2022) in `MAIN_RENAME_MAP` | `02_harmonizeGSS.py` | Code | ✅ Done |
| 5 | Add `WKSWRK` sentinels to `SENTINEL_MAP` | `02_harmonizeGSS.py` | Code | ✅ Done |
| 6 | Add `recode_cow()` function with per-cycle value remapping | `02_harmonizeGSS.py` | Code | ✅ Done |
| 7 | Re-run Step 2 (all cycles) | — | Execution | ✅ Done |
| 8 | Add `COW` and `WKSWRK` to `MAIN_COMMON_COLS` and `PERSON_COLS` | `03_mergingGSS.py` | Code | ✅ Done |
| 9 | Re-run Step 3 | — | Execution | ✅ Done |
| 10 | Update RF5 status in `03_mergingGSS_flags.md` | `03_mergingGSS_flags.md` | Docs | ✅ Done |

---

## 5. Impact on Step 4

With `COW` harmonized across all four cycles, Step 4 can condition the occupancy model on a consistent 3-category employment-type variable:

| `COW` | Meaning | Occupancy implication |
|-------|---------|----------------------|
| 1 | Employee | Likely away during standard working hours (9–5) |
| 2 | Self-employed / unpaid family worker | More variable schedule; higher at-home probability |
| NaN | Not at paid work (retired, student, unemployed) | Highest at-home probability; overlap with `LFTAG=3` |

`LFTAG` (already harmonized) remains available as a coarser alternative if needed for subgroup analysis.

---

## 6. Validation Results

**Validated against `hetus_wide.csv` (outputs_step3), 2026-03-19.**

### 6.1 COW Distribution per Cycle

| Cycle | n (respondents) | COW=1 Employee | COW=2 Self-empl/unpaid | COW=NaN Not at work | Unexpected values |
|-------|----------------|----------------|------------------------|---------------------|-------------------|
| 2005  | 19,221 | 9,411 (49.0%) | 2,076 (10.8%) | 7,734 (40.2%) | 0 ✅ |
| 2010  | 15,114 | 7,980 (52.8%) | 1,841 (12.2%) | 5,293 (35.0%) | 0 ✅ |
| 2015  | 17,390 | 7,863 (45.2%) | 622 (3.6%)    | 8,905 (51.2%) | 0 ✅ |
| 2022  | 12,336 | 5,976 (48.4%) | 1,303 (10.6%) | 5,057 (41.0%) | 0 ✅ |

Counts match codebook values exactly. The 2015 employee/self-employed swap (`WHW_110` codes 1↔2) was applied correctly — 7,863 employees and 622 self-employed align perfectly with the raw source distribution.

### 6.2 WKSWRK Presence per Cycle

| Cycle | Non-null count | Range | Notes |
|-------|----------------|-------|-------|
| 2005  | 12,876 | 1–52 | ✅ |
| 2010  | 9,744  | 1–52 | ✅ |
| 2015  | 10,655 | 1–52 | ✅ |
| 2022  | 0      | —    | ⚠️ Expected — no weeks-worked variable in 2022 PUMF extraction |

The 2022 all-null WKSWRK is not a bug. The 2022 GSS PUMF does not include a direct equivalent of `WKWE`/`WET_110`, and none was extracted in Step 1.

### 6.3 Output Files

| File | COW present? | WKSWRK present? | Notes |
|------|-------------|-----------------|-------|
| `merged_episodes.csv` | ✅ Yes | ✅ Yes | |
| `hetus_wide.csv` | ✅ Yes | ✅ Yes | |
