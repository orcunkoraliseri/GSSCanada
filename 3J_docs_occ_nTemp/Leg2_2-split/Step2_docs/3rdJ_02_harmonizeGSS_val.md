# 3rdJ Step 2 Validator — Data Harmonization (Leg-2 Two-Channel Split)

## Goal

Validate the Step-2 harmonized CSVs for both the Residential (Leg-1 verbatim) and
Office (Leg-2) channels. Emit `outputs_step2/step2_validation_report.html` + `.txt`
in the same visual style as the Step-1 validator.

## Reference

- **Leg-1 validator template:** `2J_docs_occ_nTemp/02_harmonizeGSS_val.py`
- **Step-1 Leg-2 validator style:** `Step1_docs/3rdJ_01_readingGSS_2split_val.py`
- **Harmonized outputs to validate:** `Step2_docs/outputs_step2/`
- **Step-1 outputs (regression baseline):** `Step1_docs/outputs_step1/`

## Validation Methods

| # | Method | Source | Notes |
|---|--------|--------|-------|
| 1 | Unified Schema Audit | Leg 1 | + Leg-2 cols: NOCS, NAICS, TELEWORK, AT_WORK |
| 2 | Row Count Preservation | Leg 1 | Step 1 = Step 2 rows per cycle |
| 3 | Sentinel Value Elimination | Leg 1 | 96–99 → NaN on SENTINEL_MAP cols |
| 4 | Category Recoding Verification | Leg 1 | 9 vars × 4 cycles grid chart |
| 5 | Activity Crosswalk Verification | Leg 1 | Heatmap: 14 cats × 4 cycles |
| 6 | Location & Co-Presence + AT_WORK | Leg 1 + NEW | AT_WORK rate chart; occPRE=2 share |
| 7 | Metadata Flag Audit | Leg 1 | CYCLE_YEAR, COLLECT_MODE, TUI_10_AVAIL |
| 8 | Diary Closure QA | Leg 1 | DIARY_VALID pass rate + episode box plot |
| 9 | Pre/Post Regression Check | Leg 1 | Weight delta; NaN heatmap |
| 10 | Co-Presence Quality | Leg 1 | Alone/Colleagues prevalence |
| 11 | TELEWORK Rate per Cycle | NEW | Instrument-annotated bar chart; 2015 flag |
| 12 | NOCS + NAICS Coverage | NEW | Coverage % + distinct bucket counts |

## Office-Channel Checks (New in Leg-2)

### Method 6 additions
- AT_WORK episode-weighted presence rate per cycle with sanity range (2–20%).
- Separate bar chart: occPRE==2 share per cycle showing raw workplace code prevalence.

### Method 11 — TELEWORK
- Bar chart with 4 cycles; 2005 bar annotated "n/a".
- Each bar annotated with instrument name (MAR_Q190 / WTI_130 / TLWK_01A).
- 2015 bar carries explicit flag: "diary-day (NOT comparable to 2010/2022 usual Y/N)".
- Title text repeats the diary-day incomparability warning.
- WARN (not FAIL) issued for 2015 to avoid masking the legitimate datum.

### Method 12 — NOCS and NAICS Coverage
- Two side-by-side bars per cycle: non-NaN coverage % and distinct bucket count.
- Expected: NOCS >10% non-NaN (working adults only) with ≥3 distinct values.
- Expected: NAICS >10% non-NaN with ≥5 distinct industry codes after sentinel removal.
- FAIL if column absent; WARN if coverage below thresholds.

## PASS/WARN/FAIL Convention

Follows Step-1 convention:
- **PASS** — clean check / within expected range.
- **WARN** — plausible but needs attention (soft threshold breach, diary-day mismatch,
  optional column missing, coverage below guideline but data present).
- **FAIL** — concrete data integrity problem (missing required column, wrong row count,
  sentinel residuals, mandatory flag mismatch).

## Expected Result

- 0 FAIL on a clean harmonized run.
- WARNs acceptable for: 2015 TELEWORK diary-day flag, AT_WORK 2022 WFH suppression,
  NOCS/NAICS coverage in cycles with many non-employed respondents.
- HTML report: dark-theme, base64 embedded charts, scorecard header.
- TXT report: same PASS/WARN/FAIL lines, human-readable for cluster log review.

## Test Method

```
py -3 -X utf8 3rdJ_02_harmonizeGSS_2split_val.py
```
Opens `outputs_step2/step2_validation_report.html` in browser to review charts.

---

## Progress Log

### 2026-06-14 — Validator Built and Run

**Deliverable:** `3rdJ_02_harmonizeGSS_2split_val.py` created with 12 methods
(10 ported from Leg-1 + Methods 11/12 new for Leg-2 office channel).

**New charts added:**
- Chart 6: AT_HOME and AT_WORK rate side-by-side per cycle.
- Chart 6b: occPRE==2 episode share per cycle.
- Chart 11: TELEWORK rate per cycle, instrument-annotated, 2015 diary-day flag.
- Chart 12: NOCS and NAICS coverage % + distinct bucket count per cycle.

**Reports emitted:**
- `outputs_step2/step2_validation_report.html` — dark-theme with base64 charts.
- `outputs_step2/step2_validation_report.txt` — PASS/WARN/FAIL tally for log review.

**PASS/WARN/FAIL tally (final run): PASS 73 / WARN 1 / FAIL 0.**

The single WARN is Method 11: 2015 TELEWORK = 7.8% flagged as diary-day measure
(WTI_130) — expected and documented. AT_WORK 2022 suppression (4.92%) does not
trigger a WARN because the 2-20% sanity range accepts it.

**Bug caught by validator on first run:** NOCS sentinel residuals (97/98/99) in
2005/2010. Fixed in `unify_nocs()` by adding sentinel nullification step after rename.
Second run: FAIL 0.

**No blockers.**
