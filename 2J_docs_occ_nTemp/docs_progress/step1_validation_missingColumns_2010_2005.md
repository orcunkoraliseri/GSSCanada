# Validation Report — Missing Columns Fix (2005 & 2010)

**Date:** 2026-03-06
**Scope:** Step 1 — GSS Data Collection (`01_readingGSS.py` + `01_readingGSS_val.py`)
**Affected output:** `outputs_step1/validation_report.html` — Chart 3 (Demographic & Socioeconomic Distributions)

---

## Problem

Chart 3 in the validation report showed **empty / hatched "N/A" subplots** for the 2010 cycle across multiple demographic variables, and for 2005 and 2010 across two additional variables. Most of the affected variables existed in the 2005, 2015, and 2022 data but appeared missing for 2010 (and some for 2005).

---

## Root Cause Analysis

### Issue 1 — 2010 Missing Demographic Columns (Marital Status, Labour Force, Employment Type, Language)

**Cause:** `MAIN_COLS_2010` in `01_readingGSS.py` was set to only 7 columns with an incorrect comment claiming the columns were "genuinely absent from the raw source":

```python
# The original 2010 data file provided is a subset. Removed columns genuinely absent from the raw source.
MAIN_COLS_2010 = ["RECID", "PRV", "HSDSIZEC", "AGEGR10", "SEX", "LUC_RST", "WGHT_PER"]
```

**Investigation:** Inspecting `GSSMain_2010_syntax.SPS` directly confirmed all "missing" columns were present at their fixed-width positions:

| Column | SPS Position | Description |
|--------|-------------|-------------|
| `MARSTAT` | 00050 | Marital status |
| `REGION` | 00075 | Region of residence |
| `DVTDAY` | 00079 | Diary day type |
| `ACT7DAYS` | 02051 | Labour force activity (last 7 days) |
| `WKWE` | 02061 | Employment type (class of worker) |
| `LFSGSS` | 02092 | Labour force status |
| `LANCH` | 02522 | Language spoken at home |
| `INCM` | 02530 | Income |
| `EDU10` | 02139 | Education level |

The `DEMO_VARS` mapping in `01_readingGSS_val.py` had correspondingly set these to `None` for 2010, treating the gap as a data limitation rather than a selection oversight.

---

### Issue 2 — "Hours Worked" Absent for 2005 and 2010

**Cause:** `WKWEHR_C` ("Number of hours usually worked at all jobs in a week") was never added to `MAIN_COLS_2005` or `MAIN_COLS_2010`, even though it exists in both raw files.

**Investigation:**
- `GSSMain_2010_syntax.SPS` — `WKWEHR_C` confirmed at position 02095, value label: `75.0 = "75 or more hours"` → continuous decimal hours
- `GSSMain_2005.sas7bdat` — confirmed via `pyreadstat` metadata scan: `WKWEHR_C` and `WKWEHOHR_C` both present in the 2005 SAS file

The variable is continuous (decimal hours, capped at 75.0) in 2005/2010/2015 (`WHWD140C`), but pre-grouped (integer codes 1–8) in 2022 (`WHWD140G`). Direct comparison required a binning step for the continuous versions.

---

### Issue 3 — "Place of Work" Absent for 2005 and 2010; Incorrect for 2015/2022

**2005 — Genuinely absent:** The 2005 GSS survey did not collect commute-to-work data. No CTW variables exist in `GSSMain_2005.sas7bdat`.

**2010 — Variables exist but not selected:** Multi-select checkbox columns `CTW_Q140_C01` through `CTW_Q140_C09` exist in the 2010 DAT file (positions 02454–02462) but were never added to `MAIN_COLS_2010`.

**2015/2022 — Selection bug:** `MAIN_COLS_2015` and `MAIN_COLS_2022` only included `CTW_140I`, which is the **"Other" transport mode** checkbox — not a summary variable. The full set `CTW_140A`–`CTW_140I` was required. The `DEMO_VARS` label "Place of Work" was also misleading; the variables actually describe **commute transport mode**.

All cycles (2010, 2015, 2022) use the same binary checkbox schema (1=Yes, 2=No per mode): Car driver / Car passenger / Public transit / Walked / Bicycle / Motorcycle / Taxicab / Works from home / Other. A single "Primary Commute Mode" column needed to be derived for chart display.

Note: The 2022 GSS did not collect the Motorcycle, Taxicab, and Works-from-home transport options — those 3 columns (`CTW_140F`, `CTW_140G`, `CTW_140H`) are absent from the 2022 PUMF.

---

## Fix Applied

### `01_readingGSS.py` — Column Selection

**MAIN_COLS_2005** — added `WKWEHR_C`:
```python
MAIN_COLS_2005 = [
    "RECID", "AGEGR10", "sex", "marstat", "HSDSIZEC", "REGION", "LUC_RST",
    "WKWE", "wght_per", "DVTDAY", "LANCH", "LFSGSS", "INCM", "EDU10", "WKWEHR_C"
]
```

**MAIN_COLS_2010** — expanded from 7 to 26 columns (added 9 demographic + `WKWEHR_C` + 9 CTW checkboxes):
```python
MAIN_COLS_2010 = [
    "RECID", "AGEGR10", "SEX", "MARSTAT", "HSDSIZEC", "REGION", "PRV", "LUC_RST",
    "WKWE", "WGHT_PER", "DVTDAY", "LANCH", "LFSGSS", "ACT7DAYS", "INCM", "EDU10",
    "WKWEHR_C",
    "CTW_Q140_C01", "CTW_Q140_C02", "CTW_Q140_C03", "CTW_Q140_C04", "CTW_Q140_C05",
    "CTW_Q140_C06", "CTW_Q140_C07", "CTW_Q140_C08", "CTW_Q140_C09"
]
```

**MAIN_COLS_2015** — added `CTW_140A`–`CTW_140H` (CTW_140I was already present):
```python
MAIN_COLS_2015 = [
    "PUMFID", "SURVMNTH", "AGEGR10", "SEX", "MARSTAT", "HSDSIZEC", "PRV",
    "LUC_RST", "ACT7DAYS", "WET_110", "NOC1110Y", "WHW_110", "WHWD140C",
    "CTW_140A", "CTW_140B", "CTW_140C", "CTW_140D", "CTW_140E",
    "CTW_140F", "CTW_140G", "CTW_140H", "CTW_140I",
    "EHG_ALL", "LAN_01", "INCG1", "WGHT_PER", "DVTDAY"
]
```

**MAIN_COLS_2022** — added available CTW columns (`CTW_140F/G/H` absent from 2022 PUMF):
```python
MAIN_COLS_2022 = [
    "PUMFID", "SURVMNTH", "AGEGR10", "GENDER2", "MARSTAT", "HSDSIZEC", "PRV",
    "LUC_RST", "ACT7DAYC", "WET_120", "NOCLBR_Y", "WHWD140G",
    "CTW_140A", "CTW_140B", "CTW_140C", "CTW_140D", "CTW_140E", "CTW_140I",
    "ATT_150C", "EDC_10", "LAN_01", "INC_C", "WGHT_PER", "DDAY"
]
```

---

### `01_readingGSS_val.py` — DEMO_VARS and Chart Logic

**DEMO_VARS updates:**

```python
# Before (Issue 1 — 2010 missing demographic variables):
"Marital Status":       {"2010": None, ...}
"Labour Force Activity": {"2010": None, ...}
"Employment Type (COW)": {"2010": None, ...}
"Language at Home":     {"2010": None, ...}

# After:
"Marital Status":       {"2010": "MARSTAT", ...}
"Labour Force Activity": {"2010": "ACT7DAYS", ...}
"Employment Type (COW)": {"2010": "WKWE", ...}
"Language at Home":     {"2010": "LANCH", ...}

# Before (Issue 2 — Hours Worked):
"Hours Worked (grouped)": {"2005": None, "2010": None, "2015": "WHWD140C", "2022": "WHWD140G"}

# After:
"Hours Worked": {"2005": "WKWEHR_C", "2010": "WKWEHR_C", "2015": "WHWD140C", "2022": "WHWD140G"}

# Before (Issue 3 — Place of Work / Commute):
"Place of Work": {"2005": None, "2010": None, "2015": "CTW_140I", "2022": "CTW_140I"}

# After:
"Commute Mode": {
    "2005": None,           # genuinely absent from 2005 GSS
    "2010": "__CTW_2010__", # derived from CTW_Q140_C01–C09
    "2015": "__CTW_2015__", # derived from CTW_140A–I
    "2022": "__CTW_2022__", # derived from CTW_140A–I
}
```

**New helper functions added to `01_readingGSS_val.py`:**

`_bin_hours(series)` — bins continuous hours into 6 bands, excluding missing codes (≥96):
```
[0, 15) → "<15h"   [15, 30) → "15–29h"   [30, 40) → "30–39h"
[40, 50) → "40–49h"   [50, 75) → "50–74h"   [75+) → "75h+"
```

`_derive_commute_mode(df, cycle)` — derives a single "Primary Commute Mode" from the checkbox array using priority ordering (Car driver > Car passenger > Public transit > Walked > Bicycle > Motorcycle > Taxicab > Works from home > Other). First "Yes" (value == 1) in priority order wins.

**Chart 3 dispatch logic** — `_plot_demo_frequencies()` detects variable type before plotting:
- Sentinel `"__CTW_XXXX__"` → calls `_derive_commute_mode()`
- `"Hours Worked"` + continuous data (any value > 10 after stripping missing codes) → calls `_bin_hours()`
- `"Hours Worked"` + pre-grouped data (all valid values ≤ 10, i.e. 2022's WHWD140G codes 1–8) → displays group codes as-is
- All other variables → original numeric `value_counts()` path

---

## Outcome

| Chart 3 Variable | 2005 Before | 2005 After | 2010 Before | 2010 After |
|---|---|---|---|---|
| Marital Status | ✅ | ✅ | ❌ N/A | ✅ Populated |
| Labour Force Activity | ✅ | ✅ | ❌ N/A | ✅ Populated |
| Employment Type (COW) | ✅ | ✅ | ❌ N/A | ✅ Populated |
| Language at Home | ✅ | ✅ | ❌ N/A | ✅ Populated |
| Hours Worked | ❌ N/A | ✅ Binned | ❌ N/A | ✅ Binned |
| Commute Mode | ❌ N/A | ❌ N/A (expected — 2005 GSS has no CTW data) | ❌ N/A | ✅ Derived |

All 34 schema and integrity validation checks pass after the fix.

---

## Files Modified

| File | Change |
|------|--------|
| `01_readingGSS.py` | Expanded `MAIN_COLS_2005`, `MAIN_COLS_2010`, `MAIN_COLS_2015`, `MAIN_COLS_2022` |
| `01_readingGSS_val.py` | Updated `DEMO_VARS`; added `_bin_hours()`, `_derive_commute_mode()` helpers; updated `_plot_demo_frequencies()` and `compare_categories()` dispatch logic |
| `outputs_step1/main_2005.csv` | Regenerated — now 15 columns (was 14) |
| `outputs_step1/main_2010.csv` | Regenerated — now 26 columns (was 7, then 16) |
| `outputs_step1/main_2015.csv` | Regenerated — now 27 columns (was 19) |
| `outputs_step1/main_2022.csv` | Regenerated — now 24 columns (was 19) |
| `outputs_step1/validation_report.html` | Regenerated — Chart 3 fully populated |
