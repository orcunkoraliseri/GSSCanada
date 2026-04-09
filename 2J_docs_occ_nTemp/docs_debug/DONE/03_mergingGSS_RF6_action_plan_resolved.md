# RED FLAG 6 — Output File Size Estimates Significantly Off: Action Plan

**Date**: 2026-03-19
**Severity**: 🟡 Minor — Documentation accuracy issue only; no code or data correctness problem
**Status**: ✅ RESOLVED

---

## 0. Plain Language Summary (Read This First)

### ❓ What is the problem?

The Step 3 plan document (`03_mergingGSS.md`, Phase G — Export, Section G1) contains three file size estimates that are substantially wrong compared to what the pipeline actually produced:

| File | Plan Estimate | Actual | Direction | Error |
|------|--------------|--------|-----------|-------|
| `outputs_step3/merged_episodes.csv` | ~600 MB | 228 MB | Under-estimate of actual | −62% |
| `outputs_step3/merged_episodes.parquet` | ~100 MB | 15.1 MB | Under-estimate of actual | −85% |
| `outputs_step3/hetus_wide.csv` | ~50 MB | 82.6 MB | Over-estimate of actual | +65% |

The plan was written before the full pipeline ran and relied on early assumptions about respondent counts, episode counts, and output structure — several of which changed during implementation.

**This is not a data correctness issue.** The pipeline output files are correct; the estimates in the documentation are simply stale.

---

## 1. Root Cause Analysis

### 1.1 Why `merged_episodes.csv` is smaller than estimated (228 MB vs ~600 MB)

The ~600 MB estimate was likely calculated as:

> *~1.06M episodes × (some assumed bytes per row)*

Three factors converged to make the file much smaller:

**Factor A — Respondent count is smaller than assumed.**
The plan assumed ~69,000 respondents (using the rough pre-pipeline total). After the `DIARY_VALID` filter in Phase D, the actual count is **64,061** (652 exclusions). Additionally, the 2022 PUMF has only 12,336 respondents, not the ~17,000 that was assumed when the plan was written (see RF1).

**Factor B — Episode count is consistent with expectations, but bytes per row are lower.**
The actual episode count (~1.049M) is close to the plan's ~1.06M estimate. The size discrepancy therefore comes primarily from per-row byte cost, not row count. Many columns in `merged_episodes.csv` are short integer codes (e.g., `AGEGR10`, `REGION`, `occACT`, `DAYTYPE`) that compress extremely well as CSV text — much better than the floating-point or long-string columns the estimate may have assumed.

**Factor C — NaN / missing values.**
Columns that are missing for non-applicable respondents (e.g., `COW`, `WKSWRK` for non-workers; cycle-specific sentinel-replaced NaN fields) contribute empty CSV fields, which are very compact (just a comma).

### 1.2 Why `merged_episodes.parquet` is much smaller than estimated (15.1 MB vs ~100 MB)

The Parquet estimate was disproportionately optimistic about how much compression the format provides for this particular schema. Parquet with Snappy/gzip compression on categorical integer columns achieves extremely high compression ratios — often 15–20×. The actual 15.1 MB vs. the 228 MB CSV reflects a **15× compression ratio**, which is entirely normal for this type of data. The plan's ~100 MB estimate implied only a ~6× compression ratio from CSV, which was too conservative.

### 1.3 Why `hetus_wide.csv` is larger than estimated (82.6 MB vs ~50 MB)

The wide format file was underestimated because the plan did not account for the full column overhead:

- **144 `slot_001`–`slot_144` activity columns** per respondent
- **144 `home_001`–`home_144` AT_HOME columns** per respondent (added during implementation — the plan note in G1 confirms these were added to the same file rather than a separate file)
- **Demographic and temporal columns**: `RECID`, `occID`, `CYCLE_YEAR`, `WGHT_PER`, `AGE`, `SEX`, `MARSTAT`, `HSDSIZEC`, `REGION`, `LUC_RST`, `LANCH`, `LFSGSS`, `INCM`, `EDU10`, `WKWEHR_C`, `DAYTYPE`, `DDAY_STRATA`, `COW`, `WKSWRK` (added via RF5 resolution)

Total column count: **288+ columns** × 64,061 rows. The wide format is fundamentally column-count-dominated, and 288 columns of 1–2 digit integers add up faster than the ~50 MB estimate assumed.

---

## 2. Impact Assessment

**Severity: Minor.** This is a documentation accuracy issue only.

- The pipeline code is correct.
- The output files are correctly structured and contain the right data.
- No respondent rows, activity episodes, or demographic variables are missing or wrong.
- The only consequence is that anyone reading the plan before running the pipeline will have incorrect size expectations.

**Who is affected:**
- Future developers or collaborators reading `03_mergingGSS.md` to understand expected outputs.
- Any storage capacity planning based on the plan estimates.
- Any downstream scripts that might validate output file sizes against the plan (unlikely, but possible).

---

## 3. What Needs to Be Fixed

### 3.1 Primary Fix — Update `03_mergingGSS.md` Phase G, Section G1

The table in Phase G — Export, G1. Output Files currently reads:

```
| File | Description | Approx Size |
|------|-------------|-------------|
| outputs_step3/merged_episodes.csv | Full episode-level merged dataset with derived features | ~600 MB |
| outputs_step3/merged_episodes.parquet | Same as above in Parquet for efficient downstream loading | ~100 MB |
| outputs_step3/hetus_wide.csv | 144-slot wide format + AT_HOME slots + demographics (one row per respondent) | ~50 MB |
```

It should be updated to:

```
| File | Description | Approx Size |
|------|-------------|-------------|
| outputs_step3/merged_episodes.csv | Full episode-level merged dataset with derived features | ~228 MB |
| outputs_step3/merged_episodes.parquet | Same as above in Parquet for efficient downstream loading | ~15 MB |
| outputs_step3/hetus_wide.csv | 144-slot wide format + AT_HOME slots + demographics (one row per respondent) | ~83 MB |
```

A clarifying note should be added below the table explaining the actual drivers of these sizes.

### 3.2 Secondary Fix — Add Explanatory Note in `03_mergingGSS.md`

Below the updated G1 table, add a note:

> **Note on file sizes**: Actual sizes depend on the post-`DIARY_VALID` respondent count (64,061 after 652 exclusions) and cycle-specific sample sizes (2022: 12,336 instead of the ~17,000 originally assumed). `merged_episodes.csv` is smaller than initially estimated because integer-coded categorical columns compress efficiently in CSV. `hetus_wide.csv` is larger than estimated because it carries 288+ columns (144 activity slots + 144 AT_HOME slots + demographics) per respondent row.

### 3.3 Optional — Update Pipeline Overview Documents

If the size estimates appear in `00_GSS_Occupancy_Pipeline_Overview.md` or `00_GSS_Occupancy_Documentation.md`, those should be updated for consistency as well.

---

## 4. Steps to Resolve

| # | Step | File | Type | Status |
|---|------|------|------|--------|
| 1 | Update G1 table: `~600 MB` → `~228 MB` for `merged_episodes.csv` | `03_mergingGSS.md` | Docs | ✅ DONE |
| 2 | Update G1 table: `~100 MB` → `~15 MB` for `merged_episodes.parquet` | `03_mergingGSS.md` | Docs | ✅ DONE |
| 3 | Update G1 table: `~50 MB` → `~83 MB` for `hetus_wide.csv` | `03_mergingGSS.md` | Docs | ✅ DONE |
| 4 | Add explanatory note below G1 table (see Section 3.2 above) | `03_mergingGSS.md` | Docs | ✅ DONE |
| 5 | Check `00_GSS_Occupancy_Pipeline_Overview.md` for size estimates and update if present | `00_GSS_Occupancy_Pipeline_Overview.md` | Docs | ✅ DONE |
| 6 | Check `00_GSS_Occupancy_Documentation.md` for size estimates and update if present | `00_GSS_Occupancy_Documentation.md` | Docs | ✅ DONE |
| 7 | Update RF6 status in `03_mergingGSS_flags.md` to ✅ RESOLVED | `03_mergingGSS_flags.md` | Docs | ✅ DONE |

---

## 5. No Code Changes Required

This red flag requires **documentation updates only**. No changes to:
- `01_readingGSS.py`
- `02_harmonizeGSS.py`
- `03_mergingGSS.py`
- Any output CSV or Parquet files
- Step 2 or Step 3 validation scripts

---

## 6. Lessons Learned

- File size estimates made before pipeline execution should be explicitly labelled as **rough pre-run estimates** to distinguish them from post-run measurements.
- Wide-format outputs with hundreds of columns grow faster than intuition suggests — the column count, not just the row count, dominates size.
- Parquet compression ratios for integer-coded categorical data can be much higher than the typical 3–5× rule of thumb — 10–15× is common for this schema type.
- The `DIARY_VALID` filter and revised cycle sample sizes (RF1: 2022 = 12,336) should always be factored into any storage capacity planning for downstream steps.
