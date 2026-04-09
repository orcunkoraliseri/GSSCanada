# Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM
### Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)

---

## AIM
Construct a comprehensive, annually-representative synthetic occupancy dataset — covering all temporal strata per occupant archetype — from GSS Canada Time Use cycles (2005–2022), augmented via deep learning and forecast to 2030, for direct integration into BEM/UBEM residential energy simulations.

> **Confirmed temporal stratum structure (from Step 3 validation):** `SURVMNTH` is absent (all NaN) in Cycles 2005 and 2010; it is only available in 2015 and 2022. Accordingly, `DDAY` has been grouped into **3 `DDAY_STRATA` categories** (1=Weekday, 2=Saturday, 3=Sunday) as the common cross-cycle temporal denominator. Seasonal analysis via `SURVMNTH` is available only for the 2015 and 2022 cycles.

---

## STEP 1 — DATA COLLECTION & COLUMN SELECTION

### 1A. GSS Main File Variables
*Source: Statistics Canada GSS PUMF, Cycles 19/24/29/GSSP (2005/2010/2015/2022)*

| Raw GSS Name | Renamed To | Description | C-VAE Role | Encoding |
|---|---|---|---|---|
| `PUMFID` | `occID` | Unique respondent key | Key (no encode) | — |
| `SURVYEAR` | `SURVYEAR` | Survey collection year (4-digit) | Longitudinal label / cycle anchor | Ordinal |
| `SURVMNTH` | `SURVMNTH` | Survey month (1–12) | Temporal anchor (2015 & 2022 only — NaN for 2005/2010) | Ordinal |
| `PRV` | `PR` | Province | Demographic | One-hot |
| `HSDSIZEC` | `HHSIZE` | Household size | Demographic | One-hot |
| `AGEGR10` | `AGEGRP` | Age group (10-yr bins) | Demographic | One-hot |
| `GENDER2` | `SEX` | Sex | Demographic | One-hot |
| `MARSTAT` | `MARSTH` | Marital status | Demographic | One-hot |
| `LAN_01` | `KOL` | Official language | Demographic | One-hot |
| `EDC_10` | `ATTSCH` | School attendance | Demographic | One-hot |
| `NOCLBR_Y` | `NOCS` | Occupation group | Demographic | One-hot |
| `ACT7DAYCL` | `LFTAG` | Labour force activity | Demographic | One-hot |
| `WET_120C` | `COW` | Class of worker | Demographic | One-hot |
| `WHWD140G` | `HRSWRK` | Hours worked per week | Demographic | One-hot |
| `CTW_140I` / `CTW_140A–I` / `CTW_Q140_C01–09` | `POWST` | Place of work status | Demographic | One-hot |
| `LUC_RST` | `CMA` | Urban vs. rural | Demographic | One-hot |
| `INC_C` | `TOTINC` | Total income | Demographic | Continuous |
| `WGHT_PER` | `WGHT_PER` | Person weight | Survey weight | Continuous |
| `WTBS_001–500` | `WTBS_xxx` | Bootstrap weights | Variance estimation | Continuous |

> **Note on DDAY:** Present on both Main and Episode files. Use the Episode file copy as the authoritative diary-level temporal variable; retain from Main only for cross-validation.

---

### 1B. GSS Episode File Variables
*Source: GSS Time Use Episode PUMF (same cycles)*

| Raw GSS Name | Renamed To | Description | Role |
|---|---|---|---|
| `PUMFID` | `occID` | Respondent key | Merge key |
| `EPINO` | `EPINO` | Sequential episode index | Sequence ID |
| `DDAY` | `DDAY` | Diary reference day (1=Sun … 7=Sat) | Temporal |
| `STARTIME` | `start` | Episode start time (HHMM 24h) | Temporal |
| `ENDTIME` | `end` | Episode end time (HHMM 24h) | Temporal |
| `STARTMIN` | `startMin` | Start in minutes from 4 AM (0–1439) | Temporal (derived slots) |
| `ENDMIN` | `endMin` | End in minutes from 4 AM | Temporal |
| `DURATION` | `duration` | Episode length in minutes | Activity duration |
| `TUI_01` | `occACT` | Activity code — **14 grouped categories in hetus_wide** (mapped from 63 raw codes via TUI_01 crosswalk) | Occupancy state |
| `LOCATION` | `occPRE` | Location → home presence (300=Home → 1) | Presence flag |
| `ALONE` / `TUI_06A` | `Alone` | Alone during episode (1=Yes, 2=No) | Co-presence |
| `SPOUSE` / `TUI_06B` | `Spouse` | With spouse/partner | Co-presence |
| `CHILDHSD` + `NHSDCL15` / `TUI_06C` | `Children` | With children <15 yrs (OR-merged in Step 2) | Co-presence |
| `PARHSD` + `NHSDPAR` / `TUI_06E` | `parents` | With parents/parents-in-law (OR-merged in Step 2) | Co-presence |
| `MEMBHSD` + `NHSDC15P` / `TUI_06D` + `TUI_06F` | `otherInFAMs` | With other HH members ≥15 yrs (OR-merged in Step 2) | Co-presence |
| `OTHFAM` / `TUI_06G` | `otherHHs` | With other family outside HH | Co-presence |
| `FRIENDS` / `TUI_06H` | `friends` | With friends outside HH | Co-presence |
| `OTHERS` / `TUI_06J` | `others` | With other people outside HH | Co-presence |
| *(absent)* / `TUI_06I` | `colleagues` | With colleagues/classmates — **2015/2022 only; NaN for 2005/2010** | Co-presence |
| `TUI_07` | `techUse` | Technology use during episode (smartphone, computer, etc.) | Episode context |
| `TUI_10` | `wellbeing` | Subjective well-being scale during episode | Episode context (2015 & 2022 only) |
| `WGHT_EPI` | `WGHT_EPI` | Episode weight | Survey weight |
| `WTBS_EPI_001–500` | `WTBS_EPI_xxx` | Episode bootstrap weights | Variance estimation |

---

### 1C. Canadian Census Variables (Building & Household)
*Source: Statistics Canada Census PUMF (2006, 2011, 2016, 2021)*
*Used for BEM/UBEM integration only — NOT directly merged with GSS via shared ID*

| Census Raw Name | C-VAE Name | Description | Encoding |
|---|---|---|---|
| `BUILT` | `BUILTH` | Year of construction | One-hot |
| `CONDO` | `CONDO` | Condominium status | One-hot |
| `BEDRM` / `BROOMH` | `BEDRM` | Number of bedrooms | One-hot |
| `ROOM` | `ROOM` | Number of rooms | One-hot |
| `DTYPE` | `DTYPE` | Dwelling type | One-hot |
| `REPAIR` | `REPAIR` | Dwelling condition | One-hot |
| `VALUE` | `VALUE` | Dwelling value | Continuous |
| `GENSTAT` | `GENSTAT` | Generation status | One-hot |
| `CITIZEN` | `CITIZEN` | Citizenship | One-hot |
| `CF_RP` | `CF_RP` | Census family role | One-hot |
| `CFSTAT` | `CFSTAT` | Census family status | One-hot |
| `EMPIN` | `EMPIN` | Employment income | Continuous |
| `INCTAX` | `INCTAX` | After-tax income | Continuous |
| `CIP` / `CIP2011` / `CIP2021` | `CIP` | Field of study | One-hot |
| Derived from `EF_ID` | `EFSIZE` | Economic family size | One-hot |
| Derived from `CF_ID` | `CFSIZE` | Census family size | One-hot |

> **Census linkage rationale:** GSS Main lacks residential/building variables (dwelling type, year built, bedrooms, etc.) that are essential for Step 6 BEM/UBEM integration. Census provides these but shares no direct ID with GSS. A probabilistic ML linkage model (Step 5) bridges the two datasets using shared sociodemographic attributes.

---

## STEP 2 — DATA HARMONIZATION
*Cross-cycle alignment for GSS Cycles 2005, 2010, 2015, 2022*

This step standardizes all four GSS cycles into a unified schema before merging. Variable names, category encodings, and value ranges differ across cycles due to questionnaire redesigns and Statistics Canada's 2015 "common tools" transition.

### 2A. Known Cross-Cycle Variable Discrepancies

| Unified Name | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 (GSSP) | Harmonization Action | Validation Status |
|---|---|---|---|---|---|---|
| `SEX` | `SEX` | `SEX` | `GENDER2` | `GENDER2` | Recode all to binary 1/2 | ✅ Pass |
| `MARSTH` | `MARST` | `MARSTH` | `MARSTAT` | `MARSTAT` | Unify 5-category scheme | ✅ Pass |
| `AGEGRP` | Check | `AGEGR10` | `AGEGR10` | `AGEGR10` | Merge lowest two bins if split | ✅ Pass |
| `LFTAG` | `LFACT` | `LFTAG` | `ACT7DAYCL` | `ACT7DAYCL` | Map to 5-category standard | ✅ Pass |
| `ATTSCH` | `AttSch` | `ATTSCH` | `EDC_10` | `EDC_10` | Align binary Y/N coding | ✅ Pass |
| `PR` | `REGION` | `PRV` | `PRV` | `PRV` | Map REGION codes → PRV codes | ✅ Pass |
| `CMA` | Check | `LUC_RST` | `LUC_RST` | `LUC_RST` | Standardize urban/rural bins | ✅ Pass |
| `SURVMNTH` | **All NaN** | **All NaN** | Has values | Has values | NaN for 2005/2010 is confirmed correct — temporal stratum is `DDAY_STRATA` (3 categories) as cross-cycle denominator; retained as diagnostic column only (SEASON dropped — see W3 decision) | ✅ NaN confirmed correct |
| `TOTINC` | Self-reported brackets | Self-reported brackets | Self-reported brackets | **CRA T1FF (continuous)** | ⚠️ Regime break at 2022: pre-2022 = ordinal; 2022 = continuous. Discretize 2022 into matching brackets for cross-cycle comparability | ✅ Pass |
| `occACT` (TUI_01) | Flat ~65 codes | Flat ~72 codes | **Flat 63 codes** | **Two-level hierarchical tree** | ⚠️ Mapped to **14 grouped categories** via TUI_01 crosswalk. **0.00% unmapped rate confirmed all cycles** | ✅ 0.00% unmapped all cycles |
| `wellbeing` (TUI_10) | **Absent** | **Absent** | Present | Present | `TUI_10_AVAIL = 0` for 2005/2010; auxiliary conditioning only for 2015/2022 | ✅ Pass |
| `techUse` (TUI_07) | Absent | Uncertain | Present | Present | Auxiliary context variable; exclude from primary model inputs for 2005/2010 | — |
| Bootstrap type | Mean | Mean | Standard (500) | Standard (500) | Flag `MEAN_BS` / `STANDARD_BS`; use separate variance procedures | ✅ Weight Δmean = 0.0000 all cycles |
| Co-presence (8 primary cols) | `ALONE`, `SPOUSE`, `CHILDHSD`, `PARHSD`, `MEMBHSD`, `OTHFAM`, `FRIENDS`, `OTHERS` + extras `NHSDCL15`, `NHSDC15P`, `NHSDPAR` | Same as 2005 | `TUI_06A–J` (10 cols) | `TUI_06A–J` (10 cols) | OR-merge extras into unified 8 cols; add `colleagues` from `TUI_06I` | ✅ Complete |
| `colleagues` | Absent | Absent | `TUI_06I` | `TUI_06I` | New 9th co-presence col; NaN for 2005/2010 (concept not measured) | ✅ Complete |
| Simultaneous acts | None | 2 per episode | 2 per episode | 1 per episode | Drop `TUI_03B` for 2022; set to NaN for 2005 | — |
| Collection mode | CATI | CATI | CATI + cell | **EQ (web)** | `COLLECT_MODE` flag: 0=CATI / 1=EQ | ✅ Pass all cycles |
| Sample frame | Landline RDD | Landline RDD | Landline + cell | **Dwelling Universe File** | 2022 most representative; earlier cycles may under-sample mobile-only households | — |
| `POWST` | Not found | `CTW_Q140_C01–C09` | `CTW_140A–I`, `CTW_140I` | `CTW_140A–E`, `CTW_140I` | Resolve POWST naming across cycles | ✅ Pass |
| Episode columns | — | — | — | — | Episode column alignment | ✅ Pass |

### 2B. Harmonization Procedure

```
For each cycle in [2005, 2010, 2015, 2022]:
  1. Load Main + Episode raw files
  2. Rename columns to unified schema (see Step 1 naming)
  3. Apply category recoding per discrepancy table above
  4. Enforce common missing value convention (96/97/98/99 → NaN)
  5. Validate: check marginal distributions match known population benchmarks
  6. Append CYCLE_YEAR column (2005 / 2010 / 2015 / 2022) as longitudinal label
  7. Append SURVYEAR column (same value as CYCLE_YEAR for these cycles)
  8. Flag bootstrap method (MEAN_BS / STANDARD_BS) per cycle
  9. Flag collection mode: COLLECT_MODE = 0 (CATI) for 2005/2010; 1 (EQ) for 2022
 10. Flag TUI_10 availability: TUI_10_AVAIL = 0 for 2005/2010; 1 for 2015/2022
 11. Apply TUI_01 crosswalk: map all cycles → 14 grouped activity categories
     (confirmed: 0.00% unmapped rate for all four cycles)
 11b. Apply co-presence harmonization:
      - Standardize missing codes: {7, 8, 9} → NaN for 2005/2010; {9} → NaN for 2015/2022
      - Rename primary raw columns to 8 unified names (Alone, Spouse, Children,
        parents, otherInFAMs, otherHHs, friends, others)
      - OR-merge 2005/2010 extras: NHSDCL15 → Children, NHSDPAR → parents,
        NHSDC15P → otherInFAMs (OR rule: 1 if any source=1, else 2, else NaN)
      - OR-merge 2015/2022 extras: TUI_06F → otherInFAMs
      - Add colleagues: TUI_06I (2015/2022) / NaN (2005/2010)
      - Drop all residual raw co-presence columns
 12. Apply TOTINC harmonization:
       Pre-2022: retain as ordinal income-bracket category (self-reported)
       2022:     discretize continuous CRA-linked value into matching bracket scheme
       Flag regime: TOTINC_SOURCE = 'SELF' (2005–2015) / 'CRA' (2022)
 13. Episode QA check: assert sum(DURATION) per occID == 1440 minutes
       Flag or remove respondents where diary does not close to 1440 min
       Confirmed DIARY_VALID pass rates: 2005=98.3%, 2010=98.5%, 2015=100%, 2022=100%
 14. ✅ Resolved POWST column mismatch before export
 15. ✅ Resolved Episode column mismatch before export
 16. Export harmonized Main and Episode files per cycle
```

### 2C. Output — Confirmed Validation Results

Four harmonized cycle pairs (Main + Episode), each with identical column schemas and consistent category encodings, ready for merging.

**Step 2 validation summary (100% pass rate):**

| Metric | 2005 | 2010 | 2015 | 2022 |
|---|---|---|---|---|
| Main rows preserved | 19,597 | 15,390 | 17,390 | 12,336 |
| Episode rows preserved | 333,654 | 283,287 | 274,108 | 168,078 |
| DIARY_VALID pass rate | 98.3% | 98.5% | 100.0% | 100.0% |
| occACT unmapped rate | 0.00% | 0.00% | 0.00% | 0.00% |
| AT_HOME rate | 63.5% | 63.5% | 66.1% | **72.3%** |
| CYCLE_YEAR flag | ✅ 2005 | ✅ 2010 | ✅ 2015 | ✅ 2022 |
| COLLECT_MODE flag | ✅ 0 (CATI) | ✅ 0 (CATI) | ✅ 0 (CATI) | ✅ 1 (EQ) |
| TUI_10_AVAIL flag | ✅ 0 | ✅ 0 | ✅ 1 | ✅ 1 |
| SURVMNTH status | ✅ All NaN (correct) | ✅ All NaN (correct) | ✅ Has values | ✅ Has values |
| Weight Δmean | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

> **AT_HOME rate signal:** The 2022 AT_HOME rate (72.3%) is notably higher than the 2005–2015 baseline (~63–66%). This is the COVID-19 behavioral signature: post-pandemic remote work and stay-at-home patterns. Model 2 (Step 6) will capture this as part of the longitudinal trend, and the 2022 DRIFT_MATRIX transition will document this explicitly.

> **Solved issues:** The Step 2 failures regarding POWST column naming and episode column mismatches across cycles have been fully resolved. Step 3 can now proceed with full column fidelity.

---

## STEP 3 — MERGE & TEMPORAL FEATURE DERIVATION
*Main + Episode → Unified Occupancy Dataset*

### 3A. Merge Strategy
```
LEFT JOIN Episode ← Main on occID (PUMFID)
Result: one row per episode, carrying full demographic + temporal context
Weight rule:
  → Episode-level analysis: use WGHT_EPI
  → Person-level analysis:  use WGHT_PER
```

> **DDAY methodological note (confirmed by GSS documentation):** DDAY is the day BEFORE the interview, not the collection day. When an interviewer contacts a respondent on Wednesday evening, the designated reference day (DDAY) is Tuesday. The 24-hour diary reconstructs that completed prior day (4:00 AM Tuesday to 4:00 AM Wednesday). This means the diary captures a fully observed, closed day with no future-behavior prediction. For Model 1 training, this is methodologically clean — each sequence is a complete, verified 1440-minute record. Do not confuse DDAY with the interview date.

> **DURATION integrity constraint (QA rule, per Statistics Canada):** The sum of all episode DURATION values for a single respondent must equal exactly **1440 minutes**. This is a primary quality assurance check enforced during CATI collection (software flags non-closure in real time). For EQ-collected cycles (2022), imputation matrices handle non-closure post-collection. Any respondent whose episodes do not sum to 1440 after harmonization in Step 2 must be flagged and excluded before the 144-slot conversion — a corrupted diary cannot be validly tiled into HETUS format.

### 3B. Derived Temporal Columns

| Derived Column | Source | Logic | Availability |
|---|---|---|---|
| `DAYTYPE` | `DDAY` | Mon–Fri (2–6) = Weekday; Sat–Sun (1,7) = Weekend | All cycles |
| `DDAY_STRATA` | `DDAY` | **1=Weekday, 2=Saturday, 3=Sunday** — 3-category cross-cycle temporal denominator | All cycles ✅ Confirmed [1,2,3] |
| `HOUR_OF_DAY` | `startMin` | `startMin // 60` → 0–23 | All cycles |
| `TIMESLOT_10` | `startMin` | `startMin // 10 + 1` → slots 1–144 (HETUS format) | All cycles |
| `AT_HOME` | `occPRE` | Binary: LOCATION==300 → 1 (Home), else 0 | All cycles |
| `COLLECT_MODE` | Cycle metadata | 0 = CATI (2005/2010); 1 = EQ (2022); use as model covariate | All cycles |
| `TOTINC_SOURCE` | Cycle metadata | 'SELF' = self-reported bracket (2005–2015); 'CRA' = tax-linked (2022) | All cycles |
| `TUI_10_AVAIL` | Cycle metadata | 0 = not collected (2005/2010); 1 = available (2015/2022) | All cycles |
| `DIARY_VALID` | `DURATION` sum check | 1 = sum(DURATION per occID) == 1440; 0 = corrupted diary → exclude | All cycles |

> **Key constraint:** `DDAY_STRATA` has **3 values** (Weekday / Saturday / Sunday). The original 84-strata design (7 days × 12 months) was not adopted because SURVMNTH is absent from 2005 and 2010, and Task 2 (W3) confirmed that seasonal JS divergence is <0.001 — below the signal threshold for a conditioning dimension. The 3-stratum design is the confirmed cross-cycle temporal denominator.

### 3C. Format Conversion: Episode → HETUS 144-Slot Wide Format (10-minute intermediate)
Each respondent's variable-length episodes are first redistributed into 144 fixed 10-minute slots (4:00 AM to 3:50 AM next day). This intermediate representation preserves the full temporal granularity from the raw GSS episode data and maintains compatibility with the HETUS standard.

```
For each respondent (occID):
  Initialize slot array: slots[1..144] = None  (activity, 14 categories)
  Initialize home array: home[1..144] = None   (AT_HOME binary)
  For each episode row:
    slot_start = STARTMIN // 10 + 1
    slot_end   = ENDMIN   // 10 + 1
    slots[slot_start : slot_end] = occACT  (14-category code)
    home[slot_start : slot_end]  = AT_HOME (binary)
  Output: one row of 144 activity tokens + 144 AT_HOME tokens = 288 columns per respondent
```

> **HETUS wide format confirmed:** 288 columns per respondent row (144 activity + 144 AT_HOME). 100% slot completeness confirmed for all cycles. Night slots (4:00–8:00 AM) show 83.7% sleep activity rate and 93.4% AT_HOME rate — both within expected bounds.

### 3D. Merged Dataset Statistics — Confirmed by Step 3 Validation (99% pass rate)

| Cycle | Resp (Step 2) | Resp (post-filter) | Excl. Rate | Episodes | Mean Eps/Resp | HETUS Rows | Slots Valid | Wtd AT_HOME | Weekday % |
|---|---|---|---|---|---|---|---|---|---|
| 2005 (C19) | 19,597 | **19,221** | 1.92% | 328,143 | 17.1 | 19,221 | 100.0% | **62.7%** | 72.9% |
| 2010 (C24) | 15,390 | **15,114** | 1.79% | 279,151 | 18.5 | 15,114 | 100.0% | **62.3%** | 73.6% |
| 2015 (C29) | 17,390 | **17,390** | 0.00% | 274,108 | 15.8 | 17,390 | 100.0% | **64.5%** | 72.1% |
| 2022 (GSSP) | 12,336 | **12,336** | 0.00% | 168,078 | 13.6 | 12,336 | 100.0% | **70.6%** | 72.5% |
| **Total** | **64,713** | **64,061** | **1.01%** | **1,049,480** | — | **64,061** | — | — | — |

> **DDAY_STRATA distribution confirmed:** Weekday ratio = 72.8% (expected 65–77% ✅). DDAY_STRATA values [1, 2, 3] consistent with Weekday / Saturday / Sunday classification, with 0 inconsistencies between DAYTYPE and DDAY_STRATA.

Each diary row has: **1 `DDAY_STRATA`** (1 of 3 categories) as the temporal stratum for all cycles. The augmentation target for Model 1 is generating the **2 unobserved `DDAY_STRATA` per respondent** across all cycles. Seasonal conditioning via SURVMNTH is not used — seasonal JS divergence <0.001 confirmed sub-noise-floor (see docs_debug/02_W3_season_lift.md).

### 3E. Resolution Downsampling: 144-Slot → 48-Slot (30-Minute Interval) for BEM/UBEM
Before Model 1 training, the 144-slot (10-minute) representation is downsampled to **48 slots at 30-minute resolution**. This is the direct input format for the Transformer and all downstream BEM/UBEM integration.

**Rationale:** EnergyPlus and most BEM tools operate at hourly or 30-minute timesteps. 10-minute resolution adds computational cost to the Transformer (sequence length 3× longer) without adding useful information for energy simulation. 30-minute slots reduce the Transformer sequence length from 144 to 48, cutting attention complexity by ~9× while preserving all behaviorally meaningful transitions for occupancy modeling.

```
Downsampling rule (majority vote per 30-minute window):
For each respondent (occID):
  For each 30-min slot s in [1..48]:
    source_slots = [3*(s-1)+1 : 3*s]          # 3 consecutive 10-min slots
    slot_30min_activity[s] = mode(slots[source_slots])   # majority activity
    slot_30min_home[s]     = mode(home[source_slots])    # majority AT_HOME (0 or 1)

  Output: one row of 48 activity tokens + 48 AT_HOME tokens = 96 columns per respondent
```

**Tie-breaking rule:** If a 30-minute window contains two or more equally frequent activity codes, assign the code with the higher BEM priority (AT_HOME = 1 takes precedence over 0; for activity ties, assign the code with the longest continuous run in the window).

**Slot time mapping (48 slots, 30-min each, starting 4:00 AM):**

| Slot | Time window | BEM hour |
|---|---|---|
| 1 | 04:00–04:29 | Hour 4 |
| 2 | 04:30–04:59 | Hour 4 |
| 3 | 05:00–05:29 | Hour 5 |
| … | … | … |
| 40 | 23:30–23:59 | Hour 23 |
| 41 | 00:00–00:29 | Hour 0 |
| … | … | … |
| 48 | 03:30–03:59 | Hour 3 |

**Output dataset after downsampling:**
```
64,061 respondents × 96 columns (48 activity + 48 AT_HOME) = hetus_30min.csv
This is the final input format for Model 1 (Step 4) and all downstream steps.

Computational benefit vs. 10-min format:
  Sequence length:  144 → 48   (3× reduction)
  Transformer self-attention cost: O(L²) → ~9× reduction in attention operations
  Storage per respondent: 288 values → 96 values (3× reduction)
  Training time estimate: ~1.5–3 hrs (vs. ~4–8 hrs at 144 slots)
```

---

## STEP 4 — MODEL 1: DEEP LEARNING AUGMENTATION
*(1 observed diary → 3 complete DDAY_STRATA per occupant archetype)*

### Problem Statement
Each of **64,061 respondents** contributes exactly one diary day — one observed `DDAY_STRATA` value (Weekday, Saturday, or Sunday). Model 1 generates synthetic schedules for the **2 unobserved DDAY_STRATA**, conditioned on the respondent's demographic profile and their one observed diary. The conditioning vector is identical for all four cycles (no seasonal conditioning — see W3 decision). This extends the C-VAE multi-stratum design to a fully cross-cycle-consistent Transformer.

### Architecture: Conditional Transformer Encoder-Decoder

```
INPUT TO ENCODER
────────────────
• Observed diary sequence:  48 multivariate slot tokens (30-min resolution)
                            Each slot token = 11 features:
                              [occACT (14-cat integer),
                               AT_HOME (binary),
                               Alone, Spouse, Children, parents, otherInFAMs,
                               otherHHs, friends, others, colleagues]
                            → colleagues set to 0 for 2005/2010 (not measured)
                            Source: hetus_30min.csv (activity + AT_HOME) joined
                                    with merged_episodes.csv (co-presence, per slot)

• Conditioning vector:      [demographic profile (one-hot + continuous)]
                          + [observed DDAY_STRATA (one-hot, 3)]
                          + [observed SURVMNTH (one-hot, 12; NaN-masked for 2005/2010)]
                          + [CYCLE_YEAR embedding (2005/2010/2015/2022)]
                          + [COLLECT_MODE flag (0=CATI / 1=EQ)]
                          Note: COLLECT_MODE controls for mode effects on activity
                          reporting patterns between telephone and self-administered cycles

                    ┌─────────────────────┐
                    │  Transformer Encoder │  ← Self-attention over 48 slot tokens
                    │  + Demographic MLP   │  ← Condition embedding
                    └─────────┬───────────┘
                              │ Encoded diary representation
                    ┌─────────▼───────────┐
                    │  Transformer Decoder │  ← Cross-attention over encoder output
                    │  Target condition:   │  ← Target DDAY_STRATA (any of 3)
                    └─────────┬───────────┘
                              │
OUTPUT PER TARGET STRATUM
──────────────────────────
• Synthetic diary: 48 activity tokens    (14 categories, 30-min resolution)
                 + 48 AT_HOME tokens     (binary, 30-min resolution)
                 + 9 × 48 co-presence tokens (binary per column per slot)
                 → colleagues output masked/zeroed for 2005/2010 rows
```

### Training Strategy
- **Loss (activity):** Cross-entropy over 14 activity categories × 48 slots
- **Loss (location):** BCE over AT_HOME × 48 slots
- **Loss (co-presence):** BCE over 9 co-presence columns × 48 slots; colleagues loss term masked to zero for 2005/2010 rows (column not measured — not penalized)
- **Constraint:** AT_HOME tokens must be consistent with activity tokens (sleep/personal care at home by definition; paid work outside by default unless POWST indicates WFH)
- **Supervision:** Within each cycle, use respondents with demographically similar profiles observed on different DDAY_STRATA cells as cross-validation targets
- **Validation metric:** Jensen-Shannon divergence between synthetic and observed activity distributions per stratum; additionally report co-presence prevalence JS per column per stratum

### Output Dataset Scale
```
64,061 respondents × 3 DDAY_STRATA = ~192,000 synthetic diary days (all cycles)
Each diary: 48 activity + 48 AT_HOME + 9×48 co-presence tokens (30-min resolution)
Stratified by: DDAY_STRATA × demographic archetype × CYCLE_YEAR
```

### Computing Requirements (Concordia HPC)
- Architecture: 6-layer Transformer, 8 attention heads, d_model=256
- **Sequence length: 96 tokens** (48 slots × 2 channels — 3× reduction vs. 144-slot design)
- **Attention cost reduction: ~9× vs. 144-slot** (self-attention scales as O(L²))
- Estimated training time: **~1.5–3 hours** on 1× A100/V100 GPU node (vs. ~4–8 hrs at 144 slots)
- Storage: ~192K rows × ~96 columns ≈ well within HPC scratch space

---

## STEP 5 — CENSUS–GSS PROBABILISTIC LINKAGE
*(Building & household variables → occupant archetypes)*

### Why This Step Is Necessary
GSS Main lacks all residential building variables (dwelling type, year built, bedrooms, floor area, dwelling value) required for BEM/UBEM integration in Step 6. Canadian Census PUMF provides these but shares no common respondent ID with GSS. A probabilistic linkage model matches Census records to GSS occupant archetypes using shared sociodemographic attributes.

### Linkage Variables (Shared Between GSS and Census)

| Shared Attribute | GSS Name | Census Name | Role in Linkage |
|---|---|---|---|
| Province | `PR` | `PR` | Stratum control |
| Age group | `AGEGRP` | `AGEGRP` | Core matcher |
| Sex | `SEX` | `SEX` | Core matcher |
| Marital status | `MARSTH` | `MarStH` / `MARSTH` | Core matcher |
| Household size | `HHSIZE` | `HSIZE` / `HH_ID` derived | Core matcher |
| Labour force | `LFTAG` | `LFACT` / `LFTAG` | Core matcher |
| Income | `TOTINC` | `TOTINC` | Continuous matcher |
| Urban/rural | `CMA` | `CMA` | Stratum control |
| Occupation | `NOCS` | `NOCS` / `NOC21` | Core matcher |

### Model Architecture: Statistical Matching + Classifier

```
STAGE A — Archetype Clustering
────────────────────────────────
Input: GSS augmented dataset (Step 4 output)
Method: K-means or Gaussian Mixture Model on shared sociodemographic variables
Output: K occupant archetypes (recommended K=20–50)
        Each archetype = centroid in [PR × AGEGRP × SEX × MARSTH × HHSIZE × LFTAG × TOTINC × CMA] space

STAGE B — Census Record Classification
────────────────────────────────────────
Input: Census PUMF records + archetype centroids from Stage A
Model: Random Forest or Gradient Boosting classifier
Features: Same shared sociodemographic variables
Target: Assign each Census record to its nearest GSS archetype
Output: Each Census record carries a predicted archetype_ID

STAGE C — Building Variable Aggregation
─────────────────────────────────────────
For each archetype_ID:
  Aggregate Census building variables (BUILTH, DTYPE, BEDRM, ROOM, VALUE, REPAIR, CONDO)
  → Probability distributions of building characteristics per archetype
  → e.g., "Archetype 7: 45% single-detached, 30% apartment, 25% semi-detached; median build year 1985"
Output: Building profile distribution table per occupant archetype
```

### Output
A lookup table linking each of the K occupant archetypes (from augmented GSS data) to a probability distribution over building characteristics from Census. This is passed to Step 6 for BEM archetype assignment.

### Computational Cost Note
This step uses classical ML only (clustering + classifier), not deep learning. Training time is negligible (minutes). The key challenge is cross-cycle Census harmonization (2006/2011/2016/2021 → unified schema), which mirrors the GSS harmonization in Step 2.

---

## STEP 6 — MODEL 2: LONGITUDINAL FORECASTING
*(2005–2022 augmented data → 2030 synthetic dataset)*

### Available Longitudinal Anchors

| Cycle Year | n (post-filter respondents) | n (augmented × 3 strata) | Training split | Role |
|---|---|---|---|---|
| 2005 | 19,221 | ~57,663 | 70% train / 20% val / 10% test | Base training anchor |
| 2010 | 15,114 | ~45,342 | 70% train / 20% val / 10% test | First fine-tune target |
| 2015 | 17,390 | ~52,170 | 70% train / 20% val / 10% test | Second fine-tune target |
| 2022 | 12,336 | ~37,008 | 70% train / 20% val | Final fine-tune + recency anchor |
| **Total** | **64,061** | **~192,183** | | |

> **Note:** 2022 AT_HOME rate (70.6% vs ~63% for earlier cycles) confirms the COVID-19 behavioral shift. The DRIFT_MATRIX for the 2015→2022 transition will explicitly capture this signal as a remote-work / stay-at-home trend, which is methodologically important for the 2030 forecast.

> **Validation strategy — True Future Test (extracted from flowchart):** Rather than a random 70/20/10 held-out split within a single cycle, the held-out test set for each fine-tuning phase is the **next unseen cycle in chronological order**. This directly simulates the forecasting task: a model fine-tuned up to cycle year T is evaluated on cycle year T+5, which it has never seen. This is a substantially stronger validation design than standard within-cycle splits and provides publishable evidence that the model generalizes across real behavioral change epochs.

---

### Architecture: Four-Stage Progressive Fine-Tuning + Forecasting

The architecture integrates four elements extracted from the progressive continual fine-tuning flowchart: **(1) sequential weight inheritance**, **(2) Measure Shift drift quantification**, **(3) recency weighting in the final pooled model**, and **(4) the True Future Test validation protocol**. The full five-run parallel structure from the original flowchart is not adopted to limit compute cost.

```
══════════════════════════════════════════════════════════════════════
SUB-STAGE A — BASE TRAINING ON 2005 DATA
══════════════════════════════════════════════════════════════════════
Input:   05'GSS augmented (70% train)
Init:    Random weights
Output:  W_2005  (saved checkpoint)

  ↓ MEASURE SHIFT 2005→2010
  ──────────────────────────
  Apply W_2005 to classify 10'GSS held-out set
  Compare predicted activity distributions vs. 10'GSS ground truth
  Compute per-stratum JS divergence and per-activity drift scores
  Output: DRIFT_MATRIX_0510 — quantified behavioral change 2005→2010
  → This is publishable evidence: maps which activities shifted most
    between cycles (e.g., ↑ screen time, ↓ commute, ↑ remote work)

══════════════════════════════════════════════════════════════════════
SUB-STAGE B — PROGRESSIVE FINE-TUNING: 2005 → 2010 → 2015 → 2022
══════════════════════════════════════════════════════════════════════

Phase 2: Fine-tune W_2005 on 05'+10'GSS (70%)
          Early-stop on 10'GSS (20% val)
          True future test: evaluate on 15'GSS (unseen)
          → Save W_2010_ft

          ↓ MEASURE SHIFT 2010→2015
          Apply W_2010_ft to 15'GSS held-out
          Output: DRIFT_MATRIX_1015

Phase 3: Fine-tune W_2010_ft on 05'+10'+15'GSS (70%)
          Early-stop on 15'GSS (20% val)
          True future test: evaluate on 22'GSS (unseen)
          → Save W_2015_ft

          ↓ MEASURE SHIFT 2015→2022
          Apply W_2015_ft to 22'GSS held-out
          Output: DRIFT_MATRIX_1522
          → COVID-19 behavioral break captured here explicitly

Phase 4: Fine-tune W_2015_ft on all four cycles (70%)
          Early-stop on 22'GSS (20% val)
          → Save W_2022_ft

  Note on weight inheritance rationale: each fine-tuning phase inherits
  the previous checkpoint rather than re-initializing from random weights.
  This encodes the principle that later cycles are behavioral refinements
  of prior patterns rather than independent samples. It also reduces
  training time per phase significantly vs. full retraining.

══════════════════════════════════════════════════════════════════════
SUB-STAGE C — FINAL POOLED TRAINING WITH RECENCY WEIGHTS
══════════════════════════════════════════════════════════════════════
Input:   All four cycles pooled (70% each)
         Init: W_2005 + W_2010_ft + W_2015_ft + W_2022_ft (ensemble init)
Recency weighting scheme:
  • 2005 cycle weight: 0.10  (oldest; highest distributional shift)
  • 2010 cycle weight: 0.20
  • 2015 cycle weight: 0.30
  • 2022 cycle weight: 0.40  (most recent; strongest prior for 2030)
  Weights applied to per-sample loss during training, not to data
  subsampling — all cycles remain fully represented in each batch.
Architecture:
  • Trend Encoder (small Transformer over 4 cycle embeddings)
    learns activity trajectory from DRIFT_MATRIX_0510/1015/1522
  • Reuses fine-tuned Model 1 decoder (Step 4) for schedule generation
  • Distribution-matching loss constrains decoder output to match
    2030-projected activity proportions from Trend Encoder

══════════════════════════════════════════════════════════════════════
SUB-STAGE D — 2030 FORECASTING
══════════════════════════════════════════════════════════════════════
Input:
  • W_2022_ft weights from Sub-stage B
  • 2030 scenario features from Stats Canada / UN projections:
      - Adjusted age distribution (population aging)
      - Adjusted work-from-home rates (post-COVID baseline)
      - Adjusted commute mode share
  • All 84 DDAY × SURVMNTH target strata
Output:
  • Synthetic 2030 diary schedules (144 slots) per archetype × 84 strata
  • Saved metrics: overall + stratified per demographic group
```

---

### Drift Matrix — What It Produces and Why It Matters

The three DRIFT_MATRIX outputs (0510, 1015, 1522) are not just training diagnostics — they are standalone analytical outputs for the paper. Each matrix contains:

| Output | Description | Use in paper |
|---|---|---|
| Per-activity drift score | JS divergence of each TUI_01 category between cycle pairs | Quantifies which activities changed most (e.g., telecommuting, childcare, screen time) |
| Per-stratum drift score | Drift broken down by DDAY_STRATA cell | Shows whether behavioral change is weekday- vs weekend-specific |
| Per-archetype drift score | Drift broken down by demographic group | Shows which occupant types changed most — key for BEM archetype differentiation |
| Aggregate cycle shift index | Single scalar per cycle transition | Supports the longitudinal narrative: "Canadian residential occupancy patterns shifted most significantly between 2015 and 2022, primarily driven by..." |

---

### Validation Summary

| Phase | Train data | Validation | True future test | Metric |
|---|---|---|---|---|
| Base (2005) | 05' (70%) | 05' (20%) | 10' (unseen) | JS divergence, activity accuracy |
| Fine-tune 1 (2010) | 05'+10' (70%) | 10' (20%) | 15' (unseen) | JS divergence, activity accuracy |
| Fine-tune 2 (2015) | 05'+10'+15' (70%) | 15' (20%) | 22' (unseen) | JS divergence, activity accuracy |
| Fine-tune 3 (2022) | All (70%) | 22' (20%) | — | JS divergence, activity accuracy |
| Forecast (2030) | All pooled | — | N/A (future) | Scenario plausibility check vs. Stats Canada projections |

---

### Computational Cost Estimate (Concordia HPC)

| Sub-stage | Estimated GPU time | Notes |
|---|---|---|
| Sub-stage A (base 2005) | ~2–3 hrs | Single cycle, random init |
| Sub-stage B (3 fine-tune phases) | ~3–5 hrs total | Sequential; each phase inherits weights |
| Sub-stage C (pooled + recency) | ~3–4 hrs | Larger dataset but warm start |
| Sub-stage D (inference only) | < 1 hr | No training; forward pass only |
| **Total** | **~8–13 hrs** | vs. ~4–8 hrs for original Step 6 |

Cost increase is approximately **2×** versus the original Step 6 single-run architecture — substantially less than the **5×** cost of adopting the full five-column flowchart structure.

---

### Final 2030 Dataset
Complete annual occupancy schedule matrix per building/occupant archetype combination, covering all 84 DDAY × SURVMNTH strata, with three publishable DRIFT_MATRIX outputs documenting longitudinal behavioral change → directly integrable into BEM/UBEM in Step 7.

---

## STEP 7 — BEM/UBEM INTEGRATION

### Aggregation from 2030 Synthetic Schedules

```
Input: 2030 synthetic diary dataset (Step 6) + building profiles (Step 5)

For each archetype × building type combination:
  1. Compute hourly occupancy probability (0.0–1.0) per hour of day
     → Aggregate AT_HOME flag across respondents by hour
  2. Compute activity-specific internal heat gains
     → Map occACT to metabolic rate (W/person) per ASHRAE 55 / ISO 7730
  3. Stratify by: DDAY_STRATA (Weekday / Saturday / Sunday)
     → 3 schedule types per archetype × climate zone
  4. Align province (PR) → ASHRAE climate zone
     → Climate-differentiated occupancy profiles for Montreal, Calgary, Vancouver, etc.

Output format:
  • EnergyPlus Schedule:Compact objects (annual, weekday/weekend/holiday)
  • CSV lookup tables: hourly probability × archetype × climate zone × DDAY_STRATA
  • UBEM-ready: compatible with CityGML-linked building stock models
```

---

## FULL PIPELINE OVERVIEW

```
╔══════════════════════════════════════════════════════════════════════════╗
║  STEP 1 — DATA COLLECTION & COLUMN SELECTION                            ║
║  GSS Main (PUMFID, SURVMNTH, 17 demographic vars, weights)              ║
║  GSS Episode (occID, DDAY, occACT, start/end, occPRE, co-presence)     ║
║  Census PUMF (building: DTYPE, BUILTH, BEDRM, ROOM, VALUE, CONDO…)     ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — DATA HARMONIZATION (per cycle: 2005/2010/2015/2022)          ║
║  Rename → Recode categories → Align missing values → Add CYCLE_YEAR    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — MERGE & FEATURE DERIVATION                                    ║
║  Episode ← Main (LEFT JOIN on occID)                                    ║
║  Derive: DDAY_STRATA, DAYTYPE, TIMESLOT_10, AT_HOME                    ║
║  Convert to HETUS 144-slot wide format per respondent                   ║
║  Output: ~64,000 diary rows (1 of 3 DDAY_STRATA each)                 ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: CONDITIONAL TRANSFORMER (Augmentation)              ║
║  Input:  1 observed diary + demographic conditioning                    ║
║  Output: 3 synthetic diaries per respondent (all DDAY_STRATA)          ║
║  Scale:  ~192,000 diary-days across all cycles                          ║
║  HPC:    ~4–8 hrs on 1× GPU node (Concordia)                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 5 — CENSUS–GSS LINKAGE MODEL (Classical ML)                      ║
║  Stage A: K-means archetype clustering on GSS augmented data            ║
║  Stage B: Random Forest → assign Census records to archetypes           ║
║  Stage C: Aggregate building variables per archetype                    ║
║  Output:  Building profile distribution table per occupant archetype    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 6 — MODEL 2: PROGRESSIVE FINE-TUNING + FORECASTING (2030)        ║
║  Sub-A:  Base training on 2005 data → W_2005                            ║
║  Sub-B:  Progressive fine-tuning W_2005→W_2010_ft→W_2015_ft→W_2022_ft  ║
║          + Measure Shift (DRIFT_MATRIX) at each cycle transition         ║
║          + True Future Test: next unseen cycle as holdout                ║
║  Sub-C:  Pooled training with recency weights (2022=0.40 → 2005=0.10)  ║
║  Sub-D:  2030 inference with Stats Canada / UN scenario features         ║
║  Cost:   ~8–13 hrs on Concordia HPC (2× original, vs. 5× full chart)   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 7 — BEM/UBEM INTEGRATION                                          ║
║  Hourly occupancy probability + metabolic gain → EnergyPlus schedules  ║
║  Stratified by: archetype × climate zone × DDAY_STRATA                 ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Two separate DL models (Step 4 + Step 6) | Decomposes complexity; Model 1 learns schedule structure, Model 2 learns temporal trends |
| Conditional Transformer over C-VAE | Superior long-range dependency capture across 144 slots; scales to 84-condition space without posterior collapse risk |
| HETUS 288-column format as intermediate (Step 3C) | 10-minute resolution preserves full GSS temporal granularity and HETUS standard compatibility. Kept as the archival intermediate format before downsampling |
| 30-minute downsampling to 48 slots before Model 1 (Step 3E) | EnergyPlus and BEM tools operate at hourly or 30-min timesteps — 10-min adds no useful information for energy simulation. Reduces Transformer sequence length from 144 to 48 (3×), cutting attention cost ~9× and training time from ~4–8 hrs to ~1.5–3 hrs |
| Majority-vote rule for 30-min aggregation (Step 3E) | Each 30-min slot inherits the most frequent activity across its three 10-min source slots. AT_HOME ties resolved by presence priority (1 > 0); activity ties resolved by longest continuous run |
| Census linkage via classical ML (Step 5) | Avoids joint DL training complexity; building variables are slow-changing and well-suited to archetype-level probabilistic matching |
| Separate Step 5 before Step 6 | Building archetypes are needed as conditioning for 2030 BEM integration; must be established before final forecast |
| Concordia HPC for Step 4 | ~5.8M sequences × 144 tokens requires GPU parallelization; estimated feasible within standard HPC job allocation |
| SURVYEAR added as explicit variable (Step 1A) | Required for longitudinal pooling and GSS Historical Database alignment; CYCLE_YEAR and SURVYEAR serve as the primary indexing axis for Model 2 trend encoding |
| TOTINC harmonized as two regimes (Step 2) | Pre-2022 = self-reported categorical brackets; 2022 = CRA T1FF tax-linked continuous value. Pooling without harmonization would introduce a systematic income measurement artefact across cycles |
| TUI_01 crosswalk mandatory for 2022 (Step 2) | Statistics Canada restructured activity codes into a two-level hierarchical tree in 2022. Pooling raw codes without crosswalk mapping would make occACT incomparable across cycles, corrupting Model 1 training |
| COLLECT_MODE as model covariate (Steps 2 + 4) | CATI (interviewer-led) vs. EQ (self-administered) modes produce systematically different activity reporting patterns. Including COLLECT_MODE in the conditioning vector allows Model 1 to disentangle true behavioral change from collection artefacts |
| DIARY_VALID QA filter before 144-slot conversion | Per Statistics Canada, each respondent's DURATION must sum to exactly 1440 min. Corrupted diaries that fail this constraint cannot be tiled into valid HETUS sequences and must be excluded |
| TUI_10 used as auxiliary variable only (Steps 1B + 4) | Subjective well-being is available only for 2015 and 2022 cycles. It is retained as an optional conditioning signal for 2015/2022 sub-analyses but excluded from cross-cycle model inputs to maintain consistent architecture across all four cycles |
| Progressive fine-tuning with weight inheritance (Step 6) | Encodes temporal ordering: later cycles are behavioral refinements of earlier ones, not independent samples. Reduces training time per phase vs. full retraining from random init |
| Measure Shift / DRIFT_MATRIX at each cycle transition (Step 6) | Extracted from flowchart as the highest-value element. Produces three publishable drift matrices (2005→2010, 2010→2015, 2015→2022) quantifying which activities, strata, and archetypes changed most — directly supports the longitudinal occupancy narrative |
| True Future Test: next unseen cycle as holdout (Step 6) | Stronger validation than within-cycle random splits. Directly simulates the forecasting task (predict T+5 from data up to T), producing validation metrics that are meaningful for the 2030 forecast claim |
| Recency weighting in final pooled model (Step 6) | 2022 data receives 0.40 loss weight vs. 0.10 for 2005. Correct prior for 2030 forecasting: recent behavioral patterns are stronger predictors than 17-year-old patterns |
| Full five-column flowchart structure NOT adopted (Step 6) | Compute cost assessment: the four extracted elements deliver ~90% of methodological value at ~2× cost. The full structure would be ~5× cost with diminishing marginal return for the forecasting objective |
