# Step 2 Category Harmonization Fixes — Implementation Plan

Chart 4 of `step2_validation_report.html` exposed that 5 harmonized columns have **inconsistent category definitions across cycles**. This plan proposes fixes for all 5, organized by severity.

---

## Root Cause Summary

| Column | Root Cause | Severity |
|--------|-----------|----------|
| `COW` | **Wrong variable mapped.** `WKWE` (2005/2010/2015) = "Weeks Worked in past 12 months" (1–52). `WET_120` (2022) = actual "Class of Worker" (1–3). These are completely different concepts. | 🔴 Critical |
| `ATTSCH` | **Wrong variable mapped.** `EDU10` (2005/2010) = "Highest Level of Education" (1–10). `EHG_ALL` (2015) = similar. `EDC_10` (2022) = "Attending School" (1=Yes, 2=No). Different concepts. | 🔴 Critical |
| `TOTINC` | **Different granularity.** `INCM` (2005/2010) uses 12 brackets. `INCG1` (2015) uses 7 brackets. `INC_C` (2022) uses 5 coarse CRA brackets. Same concept, but incompatible codes. | 🟡 Moderate |
| `HRSWRK` | **Bin mismatch & Float sentinels.** 2005-2015 uses continuous hours which contained float sentinels (`97.0`, `99.7`) that bypassed integer sentinel checks. | 🔴 Critical |
| `KOL` | **Sentinel leakage + code drift.** `LANCH` (2005/2010) has cats 1–7 + sentinels 98/99. `LAN_01` (2015/2022) has cats 1–4 + sentinels 7/8/9. Additionally, code 3 means different things across cycles. | 🟡 Moderate |

---

## Proposed Changes

> [!IMPORTANT]
> **COW and ATTSCH require a decision:** The correct conceptual variables for "Class of Worker" and "School Attendance" may not exist in the 2005/2010 PUMF microdata at all (Statistics Canada often adds or removes variables between cycles). We have two options:
>
> **Option A — Drop these columns** from the harmonized schema entirely (they are **not** used in Step 5 archetype clustering features: `PR × AGEGRP × SEX × MARSTH × HHSIZE × LFTAG × TOTINC × CMA`).
>
> **Option B — Keep them but rename** to what they actually are (`WKWE` → `WEEKS_WORKED`, `EDU10` → `EDU_LEVEL`) and accept that they are cycle-specific descriptors rather than cross-cycle harmonized features.

---

### Fix 1: COW (Class of Worker) — 🔴 Critical

**Current state:**
- 2005/2010: `WKWE` = "Weeks Worked" (1–52, continuous integer)
- 2015: `WET_110` = "Class of Worker" (1–52 range in data, likely because `WET_110` might also be "Weeks Worked" — needs codebook verification)
- 2022: `WET_120` = "Class of Worker" (1=Employee, 2=Self-employed, 3=Unpaid family, 6=Not applicable, 9=Not stated)

**Proposed fix (Option A recommended):**
- Rename `COW` column to `WEEKS_WORKED` for 2005/2010/2015 (since all three actually contain weeks-worked data, range 1–52)
- Keep 2022's `WET_120` as `COW` with clean codes {1, 2, 3} + NaN
- Flag `COW` as "2022-only" in the schema documentation
- Or drop `COW` from the harmonized schema entirely since it's not in the Step 5 clustering features

#### [MODIFY] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)
- Update `MAIN_RENAME_MAP` to map `WKWE` → `WEEKS_WORKED` (not `COW`) for 2005/2010
- Similarly for 2015 `WET_110` (verify if it's weeks or class-of-worker)
- Update `recode_cow()` accordingly

---

### Fix 2: ATTSCH (Education / School Attendance) — 🔴 Critical

**Current state:**
- 2005: `EDU10` = "Highest Level of Education" (1–10, 10 categories)
- 2010: `EDU10` = same as 2005
- 2015: `EHG_ALL` = "Highest Level of Education" (1–7 + sentinels 97/98/99)
- 2022: `EDC_10` = "Attending School" (1=Yes, 2=No, 9=Not stated)

**Proposed fix (Option B recommended):**
- All four cycles actually have an "Education Level" variable (not "Attending School")
- Rename the column from `ATTSCH` to `EDU_LEVEL` across all cycles
- Collapse 2005/2010's 10-category scheme into a coarser 7-category scheme matching 2015
- Map 2022's `EDC_10` (1=Yes attending, 2=No) into a *separate* column `SCH_ATTEND` (since it's genuinely a different concept)
- Or drop `ATTSCH` from the harmonized schema since it's also not in Step 5 features

#### [MODIFY] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)
- Rename column to `EDU_LEVEL`
- Add a `recode_edu_level()` function that collapses to a common scheme

---

### Fix 3: TOTINC (Total Income) — 🟡 Moderate

**Current state (raw values from Step 1):**
- 2005/2010 `INCM`: 12 brackets (codes 1–12) + sentinels 98/99
- 2015 `INCG1`: 7 brackets (codes 1–7, no sentinels)
- 2022 `INC_C`: 5 coarse CRA brackets (codes 1–5)

**Proposed fix: Collapse all cycles to the 5 coarsest brackets (matching 2022)**

> [!IMPORTANT]
> We need to verify the actual dollar ranges behind each code before mapping. Based on typical Statistics Canada GSS income brackets:
>
> | Unified Code | Approx. Range | 2005/2010 `INCM` codes | 2015 `INCG1` codes |
> |---|---|---|---|
> | 1 | < $20,000 | 1, 2, 3 | 1 |
> | 2 | $20,000–$39,999 | 4, 5 | 2 |
> | 3 | $40,000–$59,999 | 6, 7 | 3 |
> | 4 | $60,000–$79,999 | 8, 9 | 4 |
> | 5 | $80,000+ | 10, 11, 12 | 5, 6, 7 |
>
> **This mapping needs your review.** Please confirm these bracket boundaries match the codebook definitions, or provide the correct ones.

#### [MODIFY] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)
- Update `recode_totinc()` to apply the collapse mapping for 2005/2010 and 2015

---

### Fix 4: HRSWRK (Hours Worked) — 🔴 Over-Inflation Bug

**Current state post-Fix 4 implementation:**
- Category 8 ("60+ hours") shows absurdly high figures for 2005 (47.4%), 2010 (49.6%), and 2015 (45.1%). 
- In contrast, 2022 shows a realistic 8.2%.

**Root Cause Analysis:**
The raw variables for 2005 (`WKWEHR_C`), 2010 (`WKWEHR_C`), and 2015 (`WHWD140C`) represent continuous hours. Statistics Canada embeds missing/skip sentinel values at the extreme top end of this continuous scale:
- 2005 uses `97.0`, `98.0`, `99.0`
- 2010 uses `99.7`, `99.8`, `99.9`
- 2015 uses `99.6`, `99.7`, `99.8`, `99.9`

The `SENTINEL_MAP` only checked for exact integers (`{96, 97, 98, 99}`). Additionally, because the `pd.cut` binning boundary simply capped at `200`, **all the missing sentinels (e.g., 99.7) were erroneously binned into Category 8 (60+ hours)**, artificially inflating it by ~40%. 

**Proposed fix: Intercept float sentinels before mapping**

Because realistic hours worked almost never exceed 95 hours/week, and any value $\ge 96$ is definitively a Statistics Canada missing/skip code in this context, we will filter them early.

#### [MODIFY] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)
- Update `recode_hrswrk()` to explicitly set all raw float values $\ge 96$ to `pd.NA` for cycles 2005, 2010, and 2015 *before* `pd.cut` is applied. This will naturally resolve the over-inflation in Category 8.

---

### Fix 5: KOL (Language) — 🔴 Confirmed Concept Mismatch — Resolved via 3-Category Collapse

**The Issue:**
Statistics Canada changed the type of language question they asked halfway through the cycles:
- **2005/2010:** Asked for "Mother Tongue" (`LANCH`). Very few "Both", many "Other" (Heritage language).
- **2015/2022:** Asked for "Knowledge of Official Languages" (`LAN_01`), meaning conversational ability. Huge numbers of "Both" (Bilingual), very few "Neither".
These measure two different concepts and no perfect equivalent exists in the PUMF microdata releases for earlier cycles.

**The Solution:**
To align them conceptually into a unified feature for downstream modeling, we **collapse all cycles down to a strict 3-category scheme**: 
1 = English, 2 = French, 3 = Other/Both/Neither/Multiple.

By grouping "Both" and "Neither/Other" into a single third category, the structural discrepancies between the "Mother Tongue" survey style and the "Conversational Ability" survey style balance out, resulting in a consistent distribution across all decades.

| Unified Code | Label | 2005/2010 `LANCH` codes | 2015/2022 `LAN_01` codes |
|---|---|---|---|
| 1 | English only | 1 | 1 |
| 2 | French only | 2 | 2 |
| 3 | Other / Both / Multiple | 3, 4, 5, 6, 7 | 3, 4 |

#### [MODIFY] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)
- Update `recode_kol()` to implement this 3-bucket mapping.
---

### Post-Fix: Validation Script Update

#### [MODIFY] [02_harmonizeGSS_val.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS_val.py)
- Update `HARM_VARS` dictionary to reflect the new expected categories
- Regenerate the validation report

---

## Verification Plan

### Automated — Re-run validation script
```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp
python 02_harmonizeGSS.py          # re-harmonize all 4 cycles
python 02_harmonizeGSS_val.py      # regenerate validation report
open outputs_step2/step2_validation_report.html
```

**Pass criteria for Chart 4:**
- Each variable row should show **identical category sets** across all 4 cycle columns
- No column should show > 20 unique categories (which would indicate an un-collapsed variable)
- `KOL`, `TOTINC`, `HRSWRK` should have the same number of bars in every cycle

### Manual — User review
- Review the updated `step2_validation_report.html` Chart 4
- Confirm that the income bracket mapping (`TOTINC`) matches your understanding of the Statistics Canada codebook definitions
