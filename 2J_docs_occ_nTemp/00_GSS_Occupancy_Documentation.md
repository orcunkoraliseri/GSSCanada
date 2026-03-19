# Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM
### Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)

---

## AIM
Construct a comprehensive, annually-representative synthetic occupancy dataset — covering all 84 DDAY × SURVMNTH strata per occupant archetype — from GSS Canada Time Use cycles (2005–2022), augmented via deep learning and forecast to 2030, for direct integration into BEM/UBEM residential energy simulations.

---

## STEP 1 — DATA COLLECTION & COLUMN SELECTION

### 1A. GSS Main File Variables
*Source: Statistics Canada GSS PUMF, Cycles 19/24/29/GSSP (2005/2010/2015/2022)*
*(Note: Variables are read using raw names but are actively renamed to the unified 'Renamed To' schema during Step 1 read/export)*

| Raw GSS Name | Renamed To | Description | C-VAE Role | Encoding |
|---|---|---|---|---|
| `PUMFID` | `occID` | Unique respondent key | Key (no encode) | — |
| `SURVYEAR` | `SURVYEAR` | Survey collection year (4-digit) | Longitudinal label / cycle anchor | Ordinal |
| `SURVMNTH` | `SURVMNTH` | Survey month (1–12) | Temporal anchor | Ordinal |
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
| `ATT_150C` | `MODE` | Commuting mode | Demographic | One-hot |
| `CTW_140I` | `POWST` | Place of work status | Demographic | One-hot |
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
| `TUI_01` | `occACT` | Activity code (63 categories) | Occupancy state |
| `LOCATION` | `occPRE` | Location → home presence (300=Home → 1) | Presence flag |
| `TUI_06B` | `Spouse` | With spouse/partner | Co-presence |
| `TUI_06C/D` | `Children` | With household children | Co-presence |
| `TUI_06H` | `Friends` | With friends | Co-presence |
| `TUI_06G` | `otherHHs` | With other household adults | Co-presence |
| `TUI_06J` | `Others` | With other people | Co-presence |
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

This step takes the unified schema exports from Step 1 and applies category recodings and missing value alignment. Variable category encodings and value ranges differ across cycles due to questionnaire redesigns and Statistics Canada's 2015 "common tools" transition.

### 2A. Known Cross-Cycle Variable Discrepancies

| Unified Name | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 (GSSP) | Harmonization Action |
|---|---|---|---|---|---|
| `SEX` | `SEX` | `SEX` | `GENDER2` | `GENDER2` | Recode all to binary 1/2 |
| `MARSTH` | `MARST` | `MARSTH` | `MARSTAT` | `MARSTAT` | Unify 5-category scheme |
| `AGEGRP` | Check | `AGEGR10` | `AGEGR10` | `AGEGR10` | Merge lowest two bins if split |
| `LFTAG` | `LFACT` | `LFTAG` | `ACT7DAYCL` | `ACT7DAYCL` | Map to 5-category standard |
| `ATTSCH` | `AttSch` | `ATTSCH` | `EDC_10` | `EDC_10` | Align binary Y/N coding |
| `PR` | `REGION` | `PRV` | `PRV` | `PRV` | Map REGION codes → PRV codes |
| `CMA` | Check | `LUC_RST` | `LUC_RST` | `LUC_RST` | Standardize urban/rural bins |
| `TOTINC` | Self-reported categorical brackets | Self-reported categorical brackets | Self-reported categorical brackets | **CRA T1FF administrative tax data (continuous)** | ⚠️ **Regime break at 2022**: pre-2022 = ordinal income groups; 2022 = continuous tax-derived income. Treat as two separate variables or discretize 2022 into matching brackets for cross-cycle comparability |
| `occACT` (TUI_01) | Flat ~65 codes | Flat ~72 codes | **Flat 63 codes** | **Two-level hierarchical tree** | ⚠️ **Structural change in 2022**: map 2022 hierarchical codes → 63-code flat scheme using Statistics Canada's published crosswalk before pooling cycles |
| `wellbeing` (TUI_10) | **Absent** | **Absent** | Present | Present | Flag availability: set `TUI_10_AVAIL = 0` for 2005/2010; use only in 2015/2022 sub-analyses or as auxiliary conditioning variable |
| `techUse` (TUI_07) | Absent | Uncertain | Present | Present | Treat as auxiliary context variable; do not use as primary conditioning input for 2005/2010 |
| Bootstrap type | Mean | Mean | Standard (500) | Standard (500) | Flag; use separate variance procedures |
| Simultaneous acts | None | 2 per episode | 2 per episode | 1 per episode | Drop `TUI_03B` for 2022; set to NaN for 2005 |
| Collection mode | CATI (landline RDD) | CATI (landline RDD) | CATI (landline + cellular) | **EQ (self-administered web)** | Add `COLLECT_MODE` flag (0=CATI / 1=EQ); use as covariate in Model 1 to control for mode effects on activity reporting patterns |
| Sample frame | Landline RDD | Landline RDD | Combined landline + cell | **Dwelling Universe File** | Note: 2022 frame is most representative; earlier cycles may under-sample mobile-only households |

### 2B. Harmonization Procedure

```
For each cycle in [2005, 2010, 2015, 2022]:
  1. Load Main + Episode Step 1 exports
  2. Columns already renamed to unified schema by Step 1 — verify schema before recoding
  3. Apply category recoding per discrepancy table above
  4. Enforce common missing value convention (96/97/98/99 → NaN)
  5. Validate: check marginal distributions match known population benchmarks
  6. Append CYCLE_YEAR column (2005 / 2010 / 2015 / 2022) as longitudinal label
  7. Append SURVYEAR column (same value as CYCLE_YEAR for these cycles)
  8. Flag bootstrap method (MEAN_BS / STANDARD_BS) per cycle
  9. Flag collection mode: COLLECT_MODE = 0 (CATI) for 2005/2010; 1 (EQ) for 2022
 10. Flag TUI_10 availability: TUI_10_AVAIL = 0 for 2005/2010; 1 for 2015/2022
 11. Apply TUI_01 crosswalk for 2022: map hierarchical tree codes → unified 63-code flat scheme
 12. Apply TOTINC harmonization:
       Pre-2022: retain as ordinal income-bracket category (self-reported)
       2022:     discretize continuous CRA-linked value into matching bracket scheme
       Flag regime: TOTINC_SOURCE = 'SELF' (2005–2015) / 'CRA' (2022)
 13. Episode QA check: assert sum(DURATION) per occID == 1440 minutes
       Flag or remove respondents where diary does not close to 1440 min
 14. Export harmonized Main and Episode files per cycle
```

### 2C. Output
Four harmonized cycle pairs (Main + Episode), each with identical column schemas and consistent category encodings, ready for merging.

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

| Derived Column | Source | Logic |
|---|---|---|
| `SEASON` | `SURVMNTH` | Dec/Jan/Feb=Winter, Mar/Apr/May=Spring, Jun/Jul/Aug=Summer, Sep/Oct/Nov=Fall |
| `DAYTYPE` | `DDAY` | Mon–Fri (2–6) = Weekday; Sat–Sun (1,7) = Weekend |
| `HOUR_OF_DAY` | `startMin` | `startMin // 60` → 0–23 |
| `TIMESLOT_10` | `startMin` | `startMin // 10 + 1` → slots 1–144 (HETUS format) |
| `AT_HOME` | `occPRE` | Binary: LOCATION==300 → 1 (Home), else 0 |
| `STRATA_ID` | `DDAY × SURVMNTH` | Integer 1–84 identifying each temporal stratum |
| `COLLECT_MODE` | Cycle metadata | 0 = CATI (2005/2010); 1 = EQ (2022); use as model covariate |
| `TOTINC_SOURCE` | Cycle metadata | 'SELF' = self-reported bracket (2005–2015); 'CRA' = tax-linked (2022) |
| `TUI_10_AVAIL` | Cycle metadata | 0 = not collected (2005/2010); 1 = available (2015/2022) |
| `DIARY_VALID` | `DURATION` sum check | 1 = sum(DURATION per occID) == 1440; 0 = corrupted diary → exclude |

### 3C. Format Conversion: Episode → HETUS 144-Slot Wide Format
Each respondent's variable-length episodes are redistributed into 144 fixed 10-minute slots (4:00 AM to 3:50 AM next day). This is the standard input unit for Model 1 (augmentation).

```
For each respondent (occID):
  Initialize slot array: slots[1..144] = None
  For each episode row:
    slot_start = STARTMIN // 10 + 1
    slot_end   = ENDMIN   // 10 + 1
    slots[slot_start : slot_end] = occACT
  Output: one row of 144 activity tokens per respondent
```

### 3D. Merged Dataset Statistics (approximate)

| Cycle | Respondents | Episodes | After 144-slot conversion |
|---|---|---|---|
| 2005 (C19) | ~19,600 | ~320,000 | 19,600 diary rows |
| 2010 (C24) | 15,390 | 283,287 | 15,390 diary rows |
| 2015 (C29) | 17,390 | 274,108 | 17,390 diary rows |
| 2022 (GSSP) | ~17,000 | ~270,000 | ~17,000 diary rows |
| **Total** | **~69,000** | **~1.15M** | **~69,000 diary rows** |

Each diary row has: 1 `DDAY` × 1 `SURVMNTH` → **1 of 84 strata observed per respondent**. The remaining 83 strata are unobserved targets for Model 1.

---

## STEP 4 — MODEL 1: DEEP LEARNING AUGMENTATION
*(1 observed diary → 84 complete strata per occupant archetype)*

### Problem Statement
Each of ~69,000 respondents contributes exactly one diary day — one observed cell in an 84-cell DDAY × SURVMNTH matrix. Model 1 generates synthetic schedules for the 83 unobserved cells, conditioned on the respondent's demographic profile and their one observed diary. This extends your previous 12-strata Italian TUS C-VAE work to the full 84-strata annual resolution.

### Architecture: Conditional Transformer Encoder-Decoder

```
INPUT TO ENCODER
────────────────
• Observed diary sequence:  144 activity tokens (occACT per slot)
• Conditioning vector:      [demographic profile (one-hot + continuous)]
                          + [observed DDAY (one-hot, 7)]
                          + [observed SURVMNTH (one-hot, 12)]
                          + [CYCLE_YEAR embedding (2005/2010/2015/2022)]
                          + [COLLECT_MODE flag (0=CATI / 1=EQ)]
                          Note: COLLECT_MODE controls for mode effects on activity
                          reporting patterns between telephone and self-administered cycles

                    ┌─────────────────────┐
                    │  Transformer Encoder │  ← Self-attention over 144 slots
                    │  + Demographic MLP   │  ← Condition embedding
                    └─────────┬───────────┘
                              │ Encoded diary representation
                    ┌─────────▼───────────┐
                    │  Transformer Decoder │  ← Cross-attention over encoder output
                    │  Target condition:   │  ← Target DDAY × SURVMNTH (any of 84)
                    └─────────┬───────────┘
                              │
OUTPUT PER TARGET STRATUM
──────────────────────────
• Synthetic diary: 144 activity tokens (occACT per slot)
• Simultaneous: AT_HOME flag per slot (derived from occACT mapping)
```

### Training Strategy
- **Loss:** Cross-entropy over 63 activity categories × 144 slots
- **Constraint:** Total occupied slots must sum to 144 (1440 min diary integrity)
- **Supervision:** Within each cycle, use respondents with demographically similar profiles observed on different DDAY × SURVMNTH cells as cross-validation targets
- **Validation metric:** Jensen-Shannon divergence between synthetic and observed activity distributions per stratum

### Output Dataset Scale
```
~69,000 respondents × 84 strata = ~5.8 million synthetic diary days
Stratified by: DDAY × SURVMNTH × demographic archetype × CYCLE_YEAR
```

### Computing Requirements (Concordia HPC)
- Architecture: 6-layer Transformer, 8 attention heads, d_model=256
- Sequence length: 144 tokens (well within Transformer capacity)
- Estimated training time: 4–8 hours on 1× A100/V100 GPU node
- Storage: ~5.8M rows × ~50 columns ≈ manageable on HPC scratch space

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

| Cycle Year | n (augmented diaries) | Training split | Role |
|---|---|---|---|
| 2005 | ~19,600 × 84 ≈ 1.65M | 70% train / 20% val / 10% test | Base training anchor |
| 2010 | ~15,390 × 84 ≈ 1.29M | 70% train / 20% val / 10% test | First fine-tune target |
| 2015 | ~17,390 × 84 ≈ 1.46M | 70% train / 20% val / 10% test | Second fine-tune target |
| 2022 | ~17,000 × 84 ≈ 1.43M | 70% train / 20% val | Final fine-tune + recency anchor |
| **Total** | **~5.83M diary days** | | |

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
| Per-stratum drift score | Drift broken down by DDAY × SURVMNTH cell | Shows whether behavioral change is season-specific or day-specific |
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
  3. Stratify by: season × daytype (weekday / Saturday / Sunday)
     → 3 schedule types × 4 seasons = 12 annual schedule variants
  4. Align province (PR) → ASHRAE climate zone
     → Climate-differentiated occupancy profiles for Montreal, Calgary, Vancouver, etc.

Output format:
  • EnergyPlus Schedule:Compact objects (annual, weekday/weekend/holiday)
  • CSV lookup tables: hourly probability × archetype × climate zone × season
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
║  * Note: GSS Columns are renamed to unified schema during export       ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — DATA HARMONIZATION (per cycle: 2005/2010/2015/2022)          ║
║  Recode categories → Align missing values → Add CYCLE_YEAR              ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — MERGE & FEATURE DERIVATION                                    ║
║  Episode ← Main (LEFT JOIN on occID)                                    ║
║  Derive: SEASON, DAYTYPE, TIMESLOT_10, AT_HOME, STRATA_ID              ║
║  Convert to HETUS 144-slot wide format per respondent                   ║
║  Output: ~69,000 diary rows (1 of 84 strata each)                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: CONDITIONAL TRANSFORMER (Augmentation)              ║
║  Input:  1 observed diary + demographic conditioning                    ║
║  Output: 84 synthetic diaries per respondent                            ║
║  Scale:  ~5.8M diary-days across all cycles                             ║
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
║  Stratified by: archetype × climate zone × season × daytype            ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Two separate DL models (Step 4 + Step 6) | Decomposes complexity; Model 1 learns schedule structure, Model 2 learns temporal trends |
| Conditional Transformer over C-VAE | Superior long-range dependency capture across 144 slots; scales to 84-condition space without posterior collapse risk |
| HETUS 144-slot format for DL input | Fixed sequence length enables standard Transformer training; compatible with European TUS comparisons |
| Census linkage via classical ML (Step 5) | Avoids joint DL training complexity; building variables are slow-changing and well-suited to archetype-level probabilistic matching |
| Separate Step 5 before Step 6 | Building archetypes are needed as conditioning for 2030 BEM integration; must be established before final forecast |
| Concordia HPC for Step 4 | ~5.8M sequences × 144 tokens requires GPU parallelization; estimated feasible within standard HPC job allocation |
| Renaming applied at read time (Step 1) | Unifies schema early so both raw output and harmonized output share semantic columns—Step 2 handles *values* rather than names. |
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
