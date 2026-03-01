# Validation Plan — `01_readingGSS` Step 1 Extraction
## Ensuring Correct Reading Flow Before Step 2

---

## Goal

Validate that all GSS Main and Episode files were read correctly and completely before proceeding to harmonization. The validation script (`01_readingGSS_val.py`) will produce a console report and optionally an HTML summary.

---

## Validation Methods

Below are **5 alternative validation approaches**, ordered from lightweight to comprehensive. They can be used individually or combined.

---

### Method 1 — Schema & Shape Audit (Recommended — Fast)

**What it checks:** Column presence, data types, row counts, and NaN rates per cycle.

| Check | Logic | Pass Criteria |
|---|---|---|
| Column presence | Compare loaded columns vs. expected constants (`MAIN_COLS_*`, `EPISODE_COLS_*`) | All expected columns present |
| Row count sanity | Compare against known GSS respondent counts from documentation | Within ±5% of documented values |
| NaN rate per column | `df.isnull().mean()` | No column is 100% NaN (would indicate a misread) |
| Dtype consistency | Check numeric columns are numeric, not object/string | Weight columns (`WGHT_*`) must be float |

**Pros:** Very fast (<1 sec), no external data needed.
**Cons:** Does not verify *content* correctness.

---

### Method 2 — Cross-Cycle Category Comparison (Recommended — Content Check)

**What it checks:** Whether the unique categories in demographic columns are plausible and consistent across cycles.

```
For each shared variable (e.g., AGEGRP, SEX, MARSTH, HHSIZE, PR):
  1. Extract unique values per cycle
  2. Print side-by-side comparison table
  3. Flag unexpected values (e.g., negative numbers, values > 99)
  4. Flag cycles where a variable has drastically different category counts
```

| Variable | Expected Categories | Flag If |
|---|---|---|
| Age group | 5–8 bins (10-yr groups) | >15 categories or <3 |
| Sex | 2 values (1/2) | >3 categories |
| Marital status | 4–6 categories | >10 categories |
| Household size | 1–6+ categories | >20 or negative values |
| Province/Region | 5–13 codes | <3 or >15 |
| Urban/Rural (CMA) | 2–5 codes | >10 |
| Income | Varies by cycle regime | All NaN for any cycle |

**Pros:** Catches misaligned columns (e.g., wrong column extracted), encoding errors.
**Cons:** Requires manual interpretation of the output table.

---

### Method 3 — Episode Integrity Check (Recommended — Critical for Pipeline)

**What it checks:** Whether the episode file structure is valid for downstream HETUS conversion.

| Check | Logic | Pass Criteria |
|---|---|---|
| Diary completeness | `groupby(occID).duration.sum()` or infer from STARTIME/ENDTIME | Majority of respondents sum to 1440 min |
| Episode count per person | `groupby(occID).size()` | Typical range: 10–30 episodes per person |
| Activity code range | `unique()` on ACTCODE/TUI_01 | No values outside known code list |
| Time ordering | STARTIME < ENDTIME per episode | >99% of episodes pass |
| ID linkage | Check occID overlap between Main and Episode | >95% of Episode IDs appear in Main |

**Pros:** Directly validates the most critical assumption for Step 3 (merge + HETUS conversion).
**Cons:** Slightly slower (~5–10 sec per cycle due to groupby).

---

### Method 4 — Weight Distribution Sanity Check

**What it checks:** Whether survey weights look reasonable (not corrupted during read).

| Check | Logic | Pass Criteria |
|---|---|---|
| Weight range | `min()`, `max()`, `mean()` for WGHT_PER / WGHT_EPI | All positive; no extreme outliers (>10× mean) |
| Weight sum | `WGHT_PER.sum()` per cycle | Should approximate Canadian population (~25–38M depending on year) |
| Zero weights | Count of `WGHT == 0` | Should be 0 or very small |

**Pros:** Catches file truncation or format parsing errors.
**Cons:** Requires rough knowledge of expected population totals.

---

### Method 5 — Visual Summary Dashboard (Optional — Most Comprehensive)

**What it checks:** Everything above, presented as a visual HTML report with charts.

Components:
- Bar chart: row counts per cycle (Main vs Episode)
- Heatmap: NaN rates per column × cycle
- Box plots: weight distributions per cycle
- Category frequency tables: side-by-side for all demographic variables
- Episode density histogram: episodes per respondent per cycle

**Pros:** Single artifact to review; easy to share with collaborators.
**Cons:** Requires matplotlib/seaborn; longer to build and run.

---

## Recommended Combination

For a practical validation before Step 2, I recommend **Methods 1 + 2 + 3 + 5** combined into a single script:

1. **Schema & Shape Audit** → confirms nothing broke during reading
2. **Cross-Cycle Category Comparison** → confirms the right columns were extracted
3. **Episode Integrity Check** → confirms data is valid for the HETUS conversion in Step 3
4. **Visual Summary Dashboard** → produces an HTML report with charts for quick visual inspection.

---

## Proposed Output

### [NEW] [01_readingGSS_val.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/01_readingGSS_val.py)

A validation script that:
1. Loads the 8 CSV files from `outputs/` (4 Main + 4 Episode)
2. Runs the selected validation methods
3. Prints a structured console report with ✅/❌ per check
4. Optionally saves the report to `outputs/validation_report.txt`

---

## Verification

The validation script itself passes if:
- All 8 files load without error
- No check produces a ❌ (or ❌ results are explainable by known cross-cycle differences documented in the pipeline, e.g., 2010 Main having fewer columns due to syntax file limitations)
