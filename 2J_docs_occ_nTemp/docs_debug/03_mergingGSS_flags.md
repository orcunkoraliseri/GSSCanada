# Step 3 — Red Flags & Issues

**Date**: 2026-03-08
**Context**: Post-execution analysis comparing `03_mergingGSS.md` plan against actual execution of `03_mergingGSS.py`

---

## ✅ RED FLAG 1 — 2022 Respondent Count (RESOLVED)

> **Status**: Not a bug. Pipeline is correct. Documentation estimates need updating.

| Source | Expected | Actual | Verdict |
|--------|----------|--------|---------|
| Pipeline Overview (`00_GSS_Occupancy_Pipeline_Overview.md`) | ~17,000 | 12,336 | Estimate was wrong |
| Raw SAS file (`GSSMain_2022.sas7bdat`) | — | 12,336 | ✓ Published PUMF size |
| Step 1 output (`outputs/main_2022.csv`) | — | 12,336 | ✓ No rows lost |
| Step 2 output (`outputs_step2/main_2022.csv`) | — | 12,336 | ✓ No rows lost |
| Step 3 post-DIARY_VALID filter | — | 12,336 | ✓ 0 exclusions |

**Root cause**: The ~17,000 estimate in the pipeline overview was an unverified assumption. **12,336 is the actual published 2022 GSS PUMF sample size** — a smaller sample than previous cycles due to Statistics Canada's switch from CATI (phone-based) to EQ (self-administered web) collection mode.

**Why 2022 has fewer respondents**:
- Collection mode changed from CATI to EQ (dwelling-universe frame) — new modes typically launch with smaller sample sizes
- Data collection ran July 2022–July 2023, overlapping with post-pandemic reduced household survey response rates
- Statistics Canada calibrated survey weights to compensate: 2022 represents the **largest** implied population (~32.1M) despite the smallest unweighted n

**Weighted population confirmation**:

| Cycle | Unweighted n | Sum of WGHT_PER | Implied Population |
|-------|-------------|-----------------|-------------------|
| 2005 | 19,597 | ~26.1M | ~26.1M |
| 2010 | 15,390 | ~28.1M | ~28.1M |
| 2015 | 17,390 | ~29.8M | ~29.8M |
| 2022 | 12,336 | ~32.1M | ~32.1M ← largest |

**Documentation updates required**:
- [ ] Update `00_GSS_Occupancy_Pipeline_Overview.md` Step 3 table: `~17,000` → `12,336` for 2022; total `~69,000` → `~64,713`
- [ ] Update `00_GSS_Occupancy_Documentation.md` Step 3D table similarly
- [ ] Add note in pipeline overview explaining smaller 2022 sample (CATI → EQ transition)
- [ ] Update Step 4 augmented dataset estimate: `64,061 × 84 ≈ 5.38M` (was `~5.8M`)

---

## 🔴 RED FLAG 2 — DDAY Encoding Not Verified Against GSS Codebook

**Assumption in plan**:
```
DDAY encoding: 1=Sunday, 2=Monday, 3=Tuesday, 4=Wednesday, 5=Thursday, 6=Friday, 7=Saturday
→ DAYTYPE: {1,7}=Weekend, {2,3,4,5,6}=Weekday
```

**Verification status**: Not checked. The encoding is hardcoded in `03_mergingGSS.py` without reference to actual GSS codebook values.

**Risk**: Different cycles may use different DDAY encodings. For example:
- 2005/2010: might use 1=Monday (ISO standard)
- 2015/2022: might use 1=Sunday (US convention)

If the encoding differs by cycle, then DAYTYPE labels are systematically flipped per cycle, producing weekday schedules labeled Weekend and vice versa.

**Impact chain**:
1. DAYTYPE is used in Phase E to condition Step 4's Conditional Transformer
2. Step 4 generates synthetic diaries stratified by DAYTYPE
3. Step 6 uses DAYTYPE for BEM archetype assignment and schedule stratification
4. Step 7 generates hourly occupancy profiles stratified by weekday/weekend
5. **Wrong DAYTYPE → wrong BEM occupancy profiles → incorrect energy demand predictions**

This is a methodological error with direct downstream consequences.

**Investigation Required**:
- [ ] Check GSS Cycle 19 (2005) codebook for `DVTDAY` or `DDAY` encoding
- [ ] Check GSS Cycle 24 (2010) codebook for the same
- [ ] Check GSS Cycle 29 (2015) codebook
- [ ] Check GSS Cycle GSSP (2022) codebook
- [ ] Cross-validate with one known survey date: pick one respondent with a known interview date, check `DDAY` value, compute actual day of week, verify match

**Action**:
- [ ] Create a verification script: load raw GSS files, inspect DDAY distributions, compare to expected (should have ~14% Sunday, ~14% Monday, … per cycle if valid)
- [ ] If encoding differs by cycle, add a cycle-aware DDAY_REMAP in Step 3
- [ ] Document verified encoding in `03_mergingGSS.md` as a known-good assumption

---

## 🟠 RED FLAG 3 — 1,988 Respondents (14.8% of 2022) Had NaN Activity Codes

**Symptom**: During Phase F HETUS conversion, 1,988 respondents had at least one episode with `occACT=NaN` (unmapped activity code).

**Breakdown by cycle**:
| Cycle | NaN respondents | % of cycle | Cause |
|-------|-----------------|-----------|-------|
| 2005 | 0 | 0.0% | ✓ |
| 2010 | 162 | 1.1% | Step 2 crosswalk gap (minor) |
| 2015 | 0 | 0.0% | ✓ |
| 2022 | 1,826 | **14.8%** | 🚨 **HIGH** |

**What happened**: Forward-fill (ffill) was applied row-wise within each respondent's 144-slot sequence, carrying the preceding valid activity forward across the NaN slot. This is standard time-use practice for brief gaps but was applied silently without investigation.

**Root cause in Step 2**: The activity code crosswalks (TUI_01 → 14-category schema) had incomplete coverage for 2022. Specifically:
- 2022 TUI_01 has 121 unique codes (hierarchical structure: 101, 102, 231, …)
- Crosswalk maps only a subset to the 14-category flat schema
- **~1,826 respondents × ~16 episodes = ~29,000 unmapped episodes** (out of ~168,000 = **17.3%**)

**Impact**:
- 14.8% of 2022 respondents have synthetic activity codes (ffill'd) rather than observed. This biases the 2022 activity distribution and distorts Step 4's training data.
- The ffill silently assumes that activity codes are "sticky" across brief gaps, which is false for activity boundaries (e.g., sleep→wake transitions).

**Investigation Required**:
- [ ] Extract the 1,826 bad respondents' episode data from Step 3's merged CSV
- [ ] Identify which specific 2022 `TUI_01` codes failed the crosswalk
- [ ] Check the Step 2 activity crosswalk Excel file (`references_activityCodes/Data Harmonization_activityCategories - execution.xlsx`) for coverage gaps
- [ ] Cross-reference with Statistics Canada's 2022 GSSP activity code documentation

**Action**:
- [ ] Update `02_harmonizeGSS.py` to add validation: log unmapped TUI_01 codes with their frequencies per cycle
- [ ] Extend the 2022 crosswalk in the Excel file to cover all 121 codes (currently incomplete)
- [ ] Re-run Step 2 harmonization with complete crosswalk
- [ ] Re-run Step 3 (will reduce NaN respondents to near 0)
- [ ] Document in validation report: percent of episodes successfully mapped per cycle per activity code

---

## 🟠 RED FLAG 4 — Plan Pseudocode Is Contradicted by Actual Slot Algorithm

**Plan statement (Edge Case #4)**:
> "Use `duration` as a cross-check but compute slots from `start`/`end` times directly for accuracy."

**Plan pseudocode (Phase F2, lines 318–325)**:
```python
# Shift to 4:00 AM origin
start_shifted = (start_min - 240) % 1440
end_shifted = (end_min - 240) % 1440
if end_shifted == 0:
    end_shifted = 1440

# Assign activity to each 10-min slot covered
slot_start = start_shifted // 10  # 0-indexed
slot_end = (end_shifted - 1) // 10 + 1  # inclusive upper bound
```

**What actually happened**: During development, the end_HHMM approach was found to fail for episodes crossing **both midnight AND the 4:00 AM diary boundary**. Example:
- Episode: start=23:35, end=07:30, duration=265 min
- start_min = 1415, end_min = 450
- Midnight wrap: end_min → 1890
- Shift to 4 AM: end_shifted = (1890 - 240) % 1440 = 210 < start_shifted = 1175 ❌
- Result: empty slot range → missing slots 119–144

**Fix applied**: switched to `end_shifted = min(start_shifted + duration, 1440)`, which is **duration-based**, not end_HHMM-based.

**Actual code (03_mergingGSS.py, lines 385–390)**:
```python
# Compute end using duration -- avoids double-wrap errors from
# end HHMM times that cross both midnight and the 4 AM boundary.
# Cap at 1440 (diary ends at 3:59 AM next day).
end_shifted = min(start_shifted + dur, 1440)
```

**Why this matters**:
- The plan is **wrong** as written. Anyone reading it would implement the buggy version.
- The actual implementation (duration-based) is correct and more robust.
- But the plan and code are now **out of sync**, creating future maintenance confusion.

**Action**:
- [ ] Update `03_mergingGSS.md` Phase F2 pseudocode to use the duration-based approach
- [ ] Update Edge Case #4 to explain why duration-based is superior
- [ ] Add a note in Phase F2: "This approach handles episodes crossing the midnight/4AM boundary without risk of double-wrap errors."

---

## 🟡 RED FLAG 5 — COW (Class of Worker) Variable Missing from Outputs

**Pipeline overview expectation** (00_GSS_Occupancy_Documentation.md, Step 1A):
> COW (Class of Worker) is a key demographic variable for conditioning the model.

**What happened**:
1. Step 1 collected raw COW columns: `WKWE` (2005/2010), `WET_110` (2015), `WET_120` (2022)
2. Step 2 harmonized them but **did not rename to a common `COW` column** — they remain as cycle-specific names
3. Step 3 defined `MAIN_COMMON_COLS` without a `COW` entry (expected a harmonized column that doesn't exist)
4. Result: **COW is not in `merged_episodes.csv` or `hetus_wide.csv`**

**Impact**:
- Step 4's Conditional Transformer was designed to condition on COW for occupant archetypes (e.g., "employed vs. self-employed vs. not in labor force")
- Without COW, the model cannot stratify synthetic schedules by employment type
- Schedules for employed and unemployed respondents are mixed, reducing accuracy

**Root cause**: Step 2's harmonization was incomplete. The employment-related columns (`WKWE`, `WET_110`, `WET_120`) were recoded for category consistency but never unified under a single `COW` name.

**Investigation Required**:
- [ ] Check Step 2 harmonization plan (`02_harmonizationGSS.md`) for employment variable handling
- [ ] Review Step 2 code (`02_harmonizeGSS.py`) to see if `COW` was created or intended

**Action**:
- [ ] **Option A** (preferred): Fix in Step 2 — add a final rename step that maps `WKWE` → `COW` (2005/2010), `WET_110` → `COW` (2015), `WET_120` → `COW` (2022)
- [ ] **Option B**: Add in Step 3 — map cycle-specific employment columns to a common `COW` column before merging
- [ ] Add `COW` to `MAIN_COMMON_COLS` and `PERSON_COLS` in Step 3
- [ ] Re-export `merged_episodes.csv` and `hetus_wide.csv` with COW included

---

## 🟡 RED FLAG 6 — Output File Size Estimates in Plan Are Significantly Off

| File | Plan Estimate | Actual | Error |
|------|----------------|--------|-------|
| `merged_episodes.csv` | ~600 MB | 228 MB | -62% |
| `merged_episodes.parquet` | ~100 MB | 15.1 MB | -85% |
| `hetus_wide.csv` | ~50 MB | 82.6 MB | +65% |

**Why**:
- Plan assumed ~69,000 respondents; actual is ~64,061 (post-DIARY_VALID filter)
- Plan estimated 1.06M episodes; actual is 1.049M (same)
- Plan underestimated slot/home column overhead: 288 columns × 64K rows = large wide format

**Not a critical issue** (just estimation error), but indicates the plan was based on earlier assumptions that changed during implementation.

**Action**:
- [ ] Update plan section "Phase G — Export, G1. Output Files" with actual file sizes
- [ ] Add note: "Actual sizes depend on post-DIARY_VALID respondent count (652 exclusions) and cycle-specific sample sizes (2022: 12,336 instead of ~17,000)"

---

## Summary & Priority Queue

| # | Flag | Severity | Status | Blocker |
|---|------|----------|--------|---------|
| 1 | 2022 sample 27% smaller than expected | ✅ Resolved | Correct PUMF size; docs need updating | No |
| 2 | DDAY encoding unverified | 🔴 Critical | Requires codebook review | Yes — affects all downstream stratification |
| 3 | 14.8% 2022 NaN occACT | 🟠 Important | Requires Step 2 fix | Yes — affects 2022 data quality |
| 4 | Plan pseudocode wrong | 🟠 Important | Requires plan update | No — code is correct |
| 5 | COW variable missing | 🟡 Notable | Requires Step 2 fix or Step 3 addition | Yes — affects model conditioning |
| 6 | Size estimates off | 🟡 Minor | Requires plan update | No |

---

## Recommended Next Steps

1. **Before proceeding to Step 4**, resolve flags 2 and 3:
   - [ ] Verify DDAY encoding per cycle (codebook + data validation)
   - [ ] Fix 2022 activity code crosswalk in Step 2, re-run harmonization
   - [x] ~~Investigate 2022 sample shortfall~~ — Resolved: 12,336 is the correct published PUMF size

2. **Update Step 2 or Step 3** (flag 5):
   - [ ] Add COW harmonization (Step 2 preferred) or derivation (Step 3 fallback)
   - [ ] Re-export merged/HETUS files with COW included

3. **Update documentation** (flags 4, 6):
   - [ ] Correct `03_mergingGSS.md` pseudocode and Edge Case notes
   - [ ] Update file size estimates

4. **Add validation checks** (ongoing):
   - [ ] Extend `03_mergingGSS_val.py` to flag DDAY encoding issues
   - [ ] Add NaN occACT rate reporting per cycle
   - [ ] Add COW coverage check (currently always shows 100% NaN because column is missing)
