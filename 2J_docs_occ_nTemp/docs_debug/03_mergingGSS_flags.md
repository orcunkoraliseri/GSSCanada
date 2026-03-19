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

## ✅ RED FLAG 2 — DDAY Encoding Not Verified Against GSS Codebook (RESOLVED)

**Assumption in plan**:
```
DDAY encoding: 1=Sunday, 2=Monday, 3=Tuesday, 4=Wednesday, 5=Thursday, 6=Friday, 7=Saturday
→ DAYTYPE: {1,7}=Weekend, {2,3,4,5,6}=Weekday
```

**Verification status**: **RESOLVED**. The 1-7 encoding assumption is correct *in theory*, but the 2005/2010/2015 main files did **not contain the 7-day variable (`DDAY`)**, they contained the 3-day variable (`DVTDAY`), which was renamed to `DDAY` by Step 2.

**Root cause**: For 81.7% of the dataset (cycles 05/10/15), Step 3's 7-day `DAYTYPE` mapping was applied to a 3-category column `{1=Weekday, 2=Saturday, 3=Sunday}`. It effectively labelled every single Weekday diary as "Weekend", and every Weekend diary as "Weekday".

**The Fix**: In `03_mergingGSS.py`, 2022's true 7-category `DDAY` is now collapsed into the consistent 3-category format (`DDAY_STRATA={1: Weekday, 2: Saturday, 3: Sunday}`) matching the older cycles. Then this is mapped to Weekday vs Weekend.

**Docs Link**: See `03_mergingGSS_RF2_action_plan.md` (in the `docs_debug` folder) for full explanation and verified implementation.

---

## ✅ RED FLAG 3 — 1,988 Respondents (14.8% of 2022) Had NaN Activity Codes (RESOLVED)

**Symptom**: During Phase F HETUS conversion, 1,988 respondents had at least one episode with `occACT=NaN` (unmapped activity code).

**Breakdown by cycle (Before Fix)**:
| Cycle | NaN respondents | % of cycle | Root Cause |
|-------|-----------------|-----------|------------|
| 2005 | 0 | 0.0% | ✓ |
| 2010 | 325 | 2.1% | Missing code 2, 712, 713 |
| 2015 | 0 | 0.0% | ✓ |
| 2022 | 1,829 | 14.8% | Missing TUI_01 codes 1105, 1303, 1304 |

**Post-Fix Assessment (Currently in Data)**:
| Cycle | NaN respondents | % of cycle | Status |
|-------|-----------------|-----------|--------|
| 2005 | 0 | **0.0%** | ✅ Clean |
| 2010 | 0 | **0.0%** | ✅ Clean |
| 2015 | 0 | **0.0%** | ✅ Clean |
| 2022 | 0 | **0.0%** | ✅ Clean |

**The Fix**:
- The missing raw GSS activity codes were correctly identified from codebooks and incorporated into the `Data Harmonization_activityCategories - execution.xlsx` Excel file.
  - **2022 (Added)**: 1105 (Arts, hobbies) -> 11 Active Leisure; 1303 (Doing nothing) -> 14 Miscellaneous / Idle; 1304 (Other activity) -> 14 Miscellaneous / Idle.
  - **2010 (Added)**: 2 -> 1 Work-related; 712, 713 -> 10 Passive Leisure.
- In `02_harmonizeGSS.py`, a `validate_activity_crosswalk()` function was implemented to strictly prevent unmapped raw activity codes from failing silently during the merge in the future.
- Steps 2 and 3 were subsequently re-run cleanly (`NaN-slot respondents before ffill: 0, after: 0`).

**Docs Link**: See `03_mergingGSS_RF3_action_plan.md` (in the `docs_debug` folder).

---

## ✅ RED FLAG 4 — Plan Pseudocode Is Contradicted by Actual Slot Algorithm (RESOLVED)

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

**Fix applied**: The Python code was correctly written to use `end_shifted = min(start_shifted + duration, 1440)`. This handles all midnight boundaries safely because the diary perfectly spans exactly 1440 minutes, meaning episodes that cross midnight just continue filling slots without wrap errors.

**Action Taken**:
- Updated `03_mergingGSS.md` Phase F2 pseudocode to display the true duration-based implementation.
- Updated Edge Case #4 text to clearly state why duration-based slot end computation is robust and avoids double-wrap edge cases.
- **Docs Link**: See `03_mergingGSS_RF4_action_plan.md` (in the `docs_debug` folder).

---

## ✅ RED FLAG 5 — COW (Class of Worker) Variable Missing from Outputs (RESOLVED)

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

## ✅ RED FLAG 6 — Output File Size Estimates in Plan Are Significantly Off (RESOLVED)

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
- [x] Update plan section "Phase G — Export, G1. Output Files" with actual file sizes
- [x] Add note: "Actual sizes depend on post-DIARY_VALID respondent count (652 exclusions) and cycle-specific sample sizes (2022: 12,336 instead of ~17,000)"

---

## Summary & Priority Queue

| # | Flag | Severity | Status | Blocker |
|---|------|----------|--------|---------|
| 1 | 2022 sample 27% smaller than expected | ✅ Resolved | Correct PUMF size; docs need updating | No |
| 2 | DDAY encoding unverified | ✅ Resolved | DVTDAY mismatch fixed in Step 3 | No |
| 3 | 14.8% 2022 NaN occACT | ✅ Resolved | Complete mapping fixed in Step 2 Excel crosswalk | No |
| 4 | Plan pseudocode wrong | ✅ Resolved | Documentation corrected | No |
| 5 | COW variable missing | ✅ Resolved | Fixed in Steps 1/2/3 — see RF5 action plan | No |
| 6 | Size estimates off | ✅ Minor | Documentation updated | No |

---

## Recommended Next Steps

1. **Before proceeding to Step 4**:
   - [x] ~~Verify DDAY encoding per cycle (codebook + data validation)~~ — Resolved in `03_mergingGSS_RF2_action_plan.md`
   - [x] ~~Fix 2022 activity code crosswalk in Step 2, re-run harmonization~~ — Resolved in `03_mergingGSS_RF3_action_plan.md`
   - [x] ~~Investigate 2022 sample shortfall~~ — Resolved: 12,336 is the correct published PUMF size

2. **Update Step 2 or Step 3** (flag 5):
   - [ ] Add COW harmonization (Step 2 preferred) or derivation (Step 3 fallback)
   - [ ] Re-export merged/HETUS files with COW included

3. **Update documentation** (flag 6):
   - [x] ~~Correct `03_mergingGSS.md` pseudocode and Edge Case notes~~ — Resolved in `03_mergingGSS_RF4_action_plan.md`
   - [x] ~~Update file size estimates~~ — Resolved in `03_mergingGSS_RF6_action_plan_resolved.md`

4. **Add validation checks** (ongoing):
   - [ ] Extend `03_mergingGSS_val.py` to flag DDAY encoding issues
   - [ ] Add NaN occACT rate reporting per cycle
   - [ ] Add COW coverage check (currently always shows 100% NaN because column is missing)
