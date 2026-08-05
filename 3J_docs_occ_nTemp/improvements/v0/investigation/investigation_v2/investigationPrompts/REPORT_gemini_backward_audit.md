# Independent backward audit — 3J Leg-3 — GEMINI
**Date:** 2026-08-04 · **Auditor:** Gemini · **Basis:** claims, documents and provenance

> *Blindness declaration: inside `improvements/investigation/` I opened only my own prompt. I did not open the prior audit, its README, `deepResearch Prompts/`, or the other auditor's prompt or report. Contaminated passages encountered: none. Findings below were reached independently of any prior audit.*

---

## Method, and its limits

### Scope & Tracing Strategy
This audit performed an independent, backward-tracing evaluation of the 3J Leg-3 four-channel occupancy pipeline (`Residential`, `Office`, `Retail`, `Hotel`) and its predecessors (Leg 1 / 2J submitted manuscript, Leg 2 2-channel split). The primary focus was verifying the **provenance, mathematical consistency, document agreement, and empirical validity** of load-bearing claims, constants, citations, and validation gates across the codebase and documentation corpus.

The audit examined:
1. **Entry Documents**: [`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md) and [`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md).
2. **Submitted 2J Manuscript**: [`2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md).
3. **Deep-Research Foundation Reports**: `Leg3_4-split/deepResearch/dr_L3-01` through `dr_L3-13` and `deepResearch_v2/`.
4. **Step-by-Step Design & Validation Documents**: `Leg3_4-split/Step1_docs/` through `Step9_docs/`.
5. **Improvement Logs**: `improvements/3rdJ_L3_improvements_step9.md` and `3rdJ_L3_step9_READER_GUIDE.md` (steering strictly around contaminated §0.21.4 / §1.4 / §2 passages).

### Explicit Exclusions & Coverage Limits
- **Code Execution & Simulations**: In accordance with Section 6 constraints, no SLURM jobs, EnergyPlus simulations, or model re-trainings were executed. Code inspection was restricted to static analysis of scripts and configuration files.
- **Excluded Investigation Path**: All files under `improvements/investigation/` were excluded except for `PROMPT_gemini_backward_audit.md`.

---

## Verdict, up front

The 3J Leg-3 pipeline presents a sophisticated, rigorously documented multi-channel generative framework. However, a backward audit tracing load-bearing assertions to primary sources reveals **critical numerical contradictions, unviable validation gates, non-existent primary citations, and unverified inherited assumptions** that risk undermining both the forthcoming 3J paper and aspects of the already-submitted 2J manuscript.

### Severity Table

| ID | Finding Summary | Severity | Pipeline Step | Reaches submitted 2J paper? |
|---|---|---|---|---|
| **G-1** | Uncorrected floor area constants in entry doc text create a 2.7–3.3× EUI denominator mismatch | **High** | Step 8 / Overview | **No** (3J tower area specific) |
| **G-2** | Hotel As-Modelled PASS criterion (`180–300` kWh/m²/yr) is contradicted by PNNL prototype baseline data (`440–520` kWh/m²/yr) | **High** | Step 8 / dr_L3-03 | **No** (Leg 3 Hotel only) |
| **G-3** | Non-existent StatCan Table citation (`24-10-0048-01`) used as primary source for hotel occupancy | **Medium** | Step 1 / Step 2 / dr_L3-01 | **No** (Leg 3 Hotel only) |
| **G-4** | Zero intra-household presence diversity assumption (`HHSIZE × AT_HOME`) carried into submitted 2J paper without empirical validation | **High** | Step 5 / 2J Paper | **YES** |
| **G-5** | Architectural claim of "4 output heads" contradicts 3-head GSS Transformer implementation | **Low** | Step 4 / Overview | **No** |
| **G-6** | Service/MEP core load prorating by floor area introduces timing distortions across tenant channels | **Medium** | Step 8 / Step 9 / dr_L3-10 | **No** |

---

## The claim register

Below is the verified register of quantitative, structural, and attributed claims extracted from entry documents and primary reports:

| Claim Description | Source Location | Supposed Support | Openable / Verified? | Audit Verdict |
|---|---|---|---|---|
| SuperTall measured gross area = **135,857.6 m²**, Tall = **72,623.1 m²** | [`3rdJ_00_4split_Occupancy_Pipeline.md:30`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L30) | Parsed IDF surfaces & SQL `Zones` table | **YES** (verified in `agg_meta.csv`) | **SOUND** (Corrected on 2026-07-31) |
| Document text total building area = **40,846 m²** (SuperTall) / **26,750 m²** (Tall) | [`3rdJ_00_4split_Occupancy_Pipeline.md:320`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L320), [`Overview.md:125`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md#L125) | Legacy 2J/3J draft spec | **YES** | **BROKEN / CONTRADICTED** (2.7–3.3× too small; uncorrected in body text) |
| Service/MEP share of gross area = **20.6%** (SuperTall) / **21.4%** (Tall) | [`3rdJ_00_4split_Occupancy_Pipeline.md:32`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L32) | IDF parsed zone multiplier sum | **YES** | **SOUND** (Replaces legacy "~52%" claim) |
| Retail EUI As-Modelled Pass Band = **[80, 110, 155] kWh/m²/yr** | [`3rdJ_00_4split_Occupancy_Pipeline.md:328`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L328), [`dr_L3-02:74`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md#L74) | PNNL Standalone Retail 90.1-2004/2019 prototype simulations | **YES** | **SOUND** (Matches PNNL CZ 6A/7A outputs) |
| Retail EUI Empirical Info Band = **[150, 280, 380] kWh/m²/yr** | [`dr_L3-02:75`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md#L75) | NRCan SCIEU 2019 non-food retail median (1.01 GJ/m²) | **YES** | **SOUND** (Verified via NRCan SCIEU tables) |
| Hotel EUI As-Modelled Pass Band = **[180, 240, 300] kWh/m²/yr** | [`3rdJ_00_4split_Occupancy_Pipeline.md:329`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L329), [`dr_L3-03:13`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md#L13) | PNNL Small/Large Hotel prototypes | **YES** | **UNSOUND / CONTRADICTED** (PNNL Large Hotel 90.1-2016/2019 simulates at 441–521 kWh/m²/yr) |
| Hotel EUI Empirical Info Band = **[220, 350, 480] kWh/m²/yr** | [`dr_L3-03:14`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md#L14) | NRCan SCIEU 2019 lodging average (1.28 GJ/m²) | **YES** | **SOUND** (Verified via SCIEU 2019) |
| Statistics Canada Table 24-10-0048-01 as hotel data source | [`dr_L3-01:13`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md#L13) | StatCan catalogue | **NO** (Table does not exist) | **NON-EXISTENT CITATION** |
| GSS Weekday AT_RETAIL 12:00–14:00 presence rate gate = **0.06–0.10** | [`3rdJ_00_4split_Occupancy_Pipeline.md:231`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L231), [`dr_L3-06:66`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md#L66) | Storeforce / Avison Young footfall & GSS episode time | **YES** | **SOUND** (Derived central ~0.079) |
| GSS Saturday AT_RETAIL 13:00–16:00 peak rate gate = **0.09–0.12** | [`dr_L3-06:67`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md#L67) | Footfall traffic counter aggregates | **YES** | **SOUND** (Distinct Saturday super-peak) |
| Head 3 loss weight scalarization $\alpha_{resid}:\alpha_{work}:\alpha_{retail} = \mathbf{1.0 : 0.5 : 0.3}$ | [`3rdJ_00_4split_Occupancy_Pipeline.md:180`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L180), [`dr_L3-13:211`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-13_training_regimen_REPORT.md#L211) | Kurin et al. 2022 multi-task loss weighting benchmark | **YES** | **SOUND** (Replaces unstable dynamic balancers) |
| Inference Logit Shift = $-\ln(49) \approx -3.89$ for Head 3 | [`3rdJ_00_4split_Occupancy_Pipeline.md:196`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L196), [`dr_L3-08:432`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-08_rare_head_extension_REPORT.md#L432) | Menon et al. 2020 logit adjustment under class imbalance | **YES** | **SOUND** (Calibrates 2% positive head) |
| Threshold-Normalized Argmax thresholds $\theta_{home}=0.50, \theta_{work}=0.40, \theta_{retail}=0.15$ | [`3rdJ_00_4split_Occupancy_Pipeline.md:202`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L202), [`dr_L3-12:223`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-12_output_representation_REPORT.md#L223) | Validation set F1 optimization | **YES** | **SOUND** (Guarantees ISR=0% post-projection) |
| ASHRAE Guideline 14 calibration thresholds (NMBE monthly ±5%, hourly ±10%; CV(RMSE) monthly 15%, hourly 30%) | [`3rdJ_00_4split_Occupancy_Pipeline.md:371`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L371) | ASHRAE Guideline 14-2014 Standard | **YES** | **SOUND** (Accurately cited to standard) |
| 6,000 paired EnergyPlus runs across 50-household panels | [`readySubmission.md:10`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md#L10) | 2J Experimental design | **YES** | **SOUND** (Matches 2J execution matrix) |
| GSS valid diary count = **64,061** (2005: 19,221; 2010: 15,114; 2015: 17,390; 2022: 12,336) | [`readySubmission.md:131`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md#L131) | StatCan GSS Time-Use PUMF files | **YES** | **SOUND** (Verified across cycle summaries) |

---

## Findings

### G-1: Floor Area & EUI Denominator Contradiction across Pipeline Documents

- **The Evidence**:
  In [`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md:30`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L30) (Corrigé 2026-07-31 Défaut 7), actual measured floor areas parsed from EnergyPlus IDFs and the SQL `Zones` table are established as **135,857.6 m²** (SuperTall) and **72,623.1 m²** (Tall). However, in lines 30 and 320 of the same document, and in [`Overview.md:125`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md#L125), the body text still states:
  > `"SuperTall 40,846 m² / Tall 26,750 m² verified identical across cities"`
- **Why It Matters**:
  EUI is calculated as $\text{Total Energy} / \text{Floor Area}$. Using the legacy text areas (40,846 m² / 26,750 m²) instead of the true parsed model areas (135,858 m² / 72,623 m²) produces an EUI value **2.7 to 3.3× too large** (e.g., 269 kWh/m²/yr instead of 99 kWh/m²/yr for the same total building energy). While the blockquote note acknowledges this correction, the uncorrected body text in Section 8 and the Overview document continues to assert the outdated area values.
- **Magnitude**: **2.7× to 3.3× systematic error** in building floor area and EUI denominator.
- **Falsifier**: Check whether `Step8_docs/outputs_step8/agg/agg_meta.csv` or published 3J EUI summary tables divide total energy by 40,846 m² or 135,857.6 m². If divided by 40,846 m², the finding is confirmed active in the deliverable.
- **Recommended Action & Cost**: Update lines 320 and 125 in the entry docs to reflect `135,857.6 m²` and `72,623.1 m²`. Audit all script exports to guarantee `agg_meta.csv` area constants are used exclusively. (Cost: 1 hour documentation fix).

---

### G-2: Incompatible Hotel EUI As-Modelled PASS Criterion vs PNNL Prototype Baseline Data

- **The Evidence**:
  In [`3rdJ_00_4split_Occupancy_Pipeline.md:329`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L329) and [`dr_L3-03:13`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md#L13), the As-Modelled PASS criterion for Hotel EUI is defined as:
  > `[180.0, 240.0, 300.0] kWh/m²/yr`
  However, in [`dr_L3-03_hotel_eui_bands_REPORT.md` Table 2 (lines 62–65)](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md#L62), the PNNL Large Hotel prototype for ASHRAE 90.1-2016 and 90.1-2019 in Climate Zones 6A (Montreal) and 7A (Calgary) is reported to simulate at:
  > `441.6 to 521.2 kWh/m²/yr`
- **Why It Matters**:
  The PASS gate ceiling of 300 kWh/m²/yr is substantially below the simulated performance of the standard PNNL Large Hotel code prototype (441.6–521.2 kWh/m²/yr). Any valid, code-compliant simulation of a Large Hotel or high-rise hotel podium will automatically **FAIL** this gate, even when functioning exactly as intended by standard energy modeling guidelines.
- **Magnitude**: **1.5× to 1.7× mismatch** between prototype reference data and the defined acceptance gate.
- **Falsifier**: Run EnergyPlus on the PNNL Large Hotel prototype in CZ 6A; if Site EUI exceeds 300 kWh/m²/yr, the PASS gate is unviable.
- **Recommended Action & Cost**: Re-specify the Hotel As-Modelled PASS criterion in `dr_L3-03` and `3rdJ_00_4split_Occupancy_Pipeline.md` to split Small Hotel (`[140, 180, 240] kWh/m²/yr`) from Large Hotel / High-Rise Podium (`[280, 380, 480] kWh/m²/yr`). (Cost: 2 hours calibration update).

---

### G-3: Non-Existent Statistics Canada Table Citation (Table 24-10-0048-01)

- **The Evidence**:
  Early pipeline design notes cited Statistics Canada Table `24-10-0048-01` as the source for monthly hotel occupancy rates. [`dr_L3-01_statcan_hotel_data_REPORT.md:13`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md#L13) confirmed:
  > `"Statistics Canada Table 24-10-0048-01 does not exist and has never existed in the Statistics Canada catalogue. Furthermore, no table in the Statistics Canada CODR publishes monthly hotel occupancy rates... by province."`
- **Why It Matters**:
  Asserting Statistics Canada provenance for hotel occupancy rates is factually false and vulnerable to immediate rejection by reviewers. The pipeline actually relies on provincial third-party statistics (ISQ for QC, CBRE via Alberta Economic Dashboard for AB).
- **Magnitude**: Complete absence of cited primary source; switch to non-GSS third-party data.
- **Falsifier**: Search the Statistics Canada API or web catalogue for `24-10-0048-01`; returns 404 / Not Found.
- **Recommended Action & Cost**: Audit all text, figures, and manuscripts across the repository to purge any mention of `Table 24-10-0048-01` and replace with explicit citations to ISQ and CBRE/Travel Alberta. (Cost: 1 hour string audit).

---

### G-4: Zero Intra-Household Presence Diversity Assumption Reaching Submitted 2J Paper

- **The Evidence**:
  In [`readySubmission.md:10`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md#L10) and [`readySubmission.md:23`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md#L23), individual GSS respondent presence (`AT_HOME ∈ {0,1}`) is linked to 144,507 Census households. In the BEM schedule converter, occupant count is set to `Number_of_People = HHSIZE × AT_HOME`.
- **Why It Matters**:
  Multiplying a single respondent's binary presence flag by `HHSIZE` assumes that **all members of a household leave and arrive simultaneously with zero intra-household diversity**. In reality, household members (spouses, children, roommates) have staggered schedules. This assumption over-concentrates peak occupancy transitions, exaggerates morning departure and evening arrival load ramps, and artificially inflates peak internal heat gain step-changes.
- **Reaches Submitted 2J Paper?**: **YES** (Core assumption of the 2J simulation engine).
- **Magnitude**: Potential over-estimation of peak residential ramping rates and coincidental internal heat gains for multi-person households.
- **Falsifier**: Compare the `HHSIZE × AT_HOME` schedule against multi-person GSS episode co-presence data for multi-member households.
- **Recommended Action & Cost**: Add a clear, explicit limitations paragraph in `readySubmission.md` Section 7 acknowledging *perfectly synchronized intra-household presence* as a stated limitation of single-respondent TUS linkage, and propose multi-agent/co-presence weighting for future work. (Cost: 1 hour manuscript addition; no compute needed).

---

### G-5: Architectural Claim of "4 Output Heads" Contradicts 3-Head GSS Transformer Implementation

- **The Evidence**:
  The graphical abstract (`Residential-Office-Retail-Hotel_Pipeline.png`) and early overview texts describe the core generative engine as a "4-head conditional Transformer". However, [`3rdJ_00_4split_Occupancy_Pipeline.md:226`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L226) clarifies:
  > `"§3.5 is authoritative: three GSS heads + a non-GSS hotel side-track... The '4 heads' wording is the diagram's simplification."`
- **Why It Matters**:
  Claiming that a Transformer predicts 4 channels directly from GSS respondent microdata when the Hotel channel is actually an external monthly SARIMA time-series model represents a structural misdescription of the ML architecture.
- **Magnitude**: Minor nomenclature / schematic contradiction.
- **Falsifier**: Inspect PyTorch model code in Step 4 (`3rdJ_04_...py`); confirm only 3 output heads exist (`AT_HOME`, `AT_WORK`, `AT_RETAIL`).
- **Recommended Action & Cost**: Update all pipeline schematics and text captions to label the model as "3 GSS Transformer Heads + 1 SARIMA Hotel Side-Track". (Cost: 30 mins text/diagram caption update).

---

### G-6: Service/MEP Core Load Prorating by Floor Area Introduces Timing Distortions Across Tenant Channels

- **The Evidence**:
  In [`3rdJ_00_4split_Occupancy_Pipeline.md:47, 410`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L47), Service / MEP / Circulation spaces (20.6% SuperTall, 21.4% Tall) are kept on unmodulated NECB baseline schedules. In Step 8 reporting ([`dr_L3-10`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md)), central plant loads are allocated hourly by coil load, but core MEP floor area and baseline energy are prorated strictly by floor area across the four tenant channels for stock EUI comparisons.
- **Why It Matters**:
  Prorating core service energy (elevators, main mechanical fans, core lighting) strictly by floor area ignores temporal differences between commercial and residential demand (e.g. office elevator peaks at 09:00 and 17:00 vs residential elevator peaks in evening).
- **Magnitude**: Moderate reallocation shift across tenant channels in EUI reporting tables.
- **Falsifier**: Compare hourly load-weighted central plant allocation against floor-area prorated allocation on simulated core meter outputs.
- **Recommended Action & Cost**: Enforce dual-basis EUI reporting (CFA primary, occupiable GFA share secondary) exactly as specified in `dr_L3-10`. (Cost: 0 additional cost; already planned).

---

## Contradictions between documents

1. **Building Floor Area Mismatch**:
   - [`3rdJ_00_4split_Occupancy_Pipeline.md:30`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L30) (Corrigé 2026-07-31) establishes SuperTall = **135,857.6 m²** and Tall = **72,623.1 m²**.
   - [`3rdJ_00_4split_Occupancy_Pipeline.md:320`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L320) and [`Overview.md:125`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md#L125) state **40,846 m²** and **26,750 m²**.
   - *Judgement*: The parsed IDF values (135,858 m² / 72,623 m²) are correct. The body text in lines 320 and 125 inherited legacy unparsed values and must be updated.

2. **Hotel As-Modelled PASS Criterion vs PNNL Prototype Data**:
   - [`3rdJ_00_4split_Occupancy_Pipeline.md:329`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L329) specifies Hotel As-Modelled PASS band = **[180, 240, 300] kWh/m²/yr**.
   - [`dr_L3-03 Table 2`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md#L62) lists PNNL Large Hotel prototype 90.1-2016/2019 EUI = **441.6 to 521.2 kWh/m²/yr**.
   - *Judgement*: The PASS threshold of 300 kWh/m²/yr is unviable for Large Hotel prototypes. The threshold must be split by hotel archetype size.

3. **Number of Generator Output Heads**:
   - PNG schematics and Overview headers declare a **"4-head Transformer"**.
   - [`3rdJ_00_4split_Occupancy_Pipeline.md:226`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md#L226) confirms **3 GSS Transformer heads + 1 SARIMA Hotel side-track**.
   - *Judgement*: The 3-head + SARIMA description is authoritative.

---

## What is NOT wrong

The following components were audited and verified to be mathematically and methodologically sound:

1. **Retail Diurnal Presence Target (0.06–0.10 weekday midday)**:
   - Verified against independent Storeforce traffic counter data, Avison Young mobility indices, and ATUS shopping duration data in [`dr_L3-06`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md). Derived GSS central value (~0.079) sits solidly within the 0.06–0.10 window.
2. **Step 4 Loss Weighting & Imbalance Calibration**:
   - The selection of Unitary Scalarization ($\alpha = 1.0 : 0.5 : 0.3$) + PCGrad gradient surgery and logit adjustment ($pos\_weight = 49$, logit shift $-\ln(49) \approx -3.89$) in [`dr_L3-08`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-08_rare_head_extension_REPORT.md) and [`dr_L3-13`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-13_training_regimen_REPORT.md) is soundly supported by multi-task ML literature (Kurin et al. 2022; Menon et al. 2020) and avoids dynamic loss balancer instability on rare classes.
3. **Decode-Time Exclusivity Projection**:
   - The Threshold-Normalized Argmax Projection ($\theta_{home}=0.50, \theta_{work}=0.40, \theta_{retail}=0.15$) in [`dr_L3-12`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-12_output_representation_REPORT.md) mathematically guarantees zero physical co-presence violations (`ISR = 0%`) without corrupting individual head marginal calibrations.
4. **Office–Retail Lunch Coupling Materiality**:
   - The decision in [`dr_L3-07`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-07_crossuse_lunch_coupling_REPORT.md) to keep simulation channels independent while producing an offline diagnostic transition probability is well-supported by BEM literature (Feng et al. 2020), which demonstrates $< 1.5\%$ retail cooling load impact from explicit schedule coupling.

---

## Unsupported or unopenable citations

1. **StatCan Table 24-10-0048-01**:
   - Non-existent table ID cited in early specs for hotel occupancy rates. Verified non-existent by [`dr_L3-01`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md).
2. **NRCan CanmetENERGY Retail Archetype Report (Table 2 in `dr_L3-02`)**:
   - Cited URL `https://natural-resources.canada.ca/energy-efficiency/buildings/energy-codes/necb/17700` points to a general NECB portal page rather than a direct report PDF. The specific sub-archetype numbers (90–125 kWh/m²/yr) are internal project benchmarks.
3. **PNNL TSD Energy Savings Analysis 90.1-2016 / 2019 PDFs**:
   - Sourced via external web URLs (`https://www.energycodes.gov/sites/default/files/...`). Values were cross-checked against local CSV `DOE_non-residential_simulation_results_canadian.csv`, confirming accuracy of extracted numbers despite reliance on external URLs.

---

## Open questions I could not settle

1. **Empirical Submetered Proof of Retail Podium Density Sensitivity**:
   - Is retail podium HVAC cooling load in actual Canadian tall buildings sensitive to customer density fluctuations under modern demand-controlled ventilation (DCV)? Literature (Feng et al. 2020) assumes standard fixed minimum outdoor air rates, rendering load insensitive (< 1.5% delta). If DCV is active, real sensitivity could be higher.
2. **Spliced Alberta Hotel Occupancy (2005–2009)**:
   - Alberta Economic Dashboard data starts in 2008/2010. The 2005–2009 period requires splicing from CBRE National Market Report archives (`dr_L3-01`). The exact spliced CSV artifact was not physically verified in the local workspace.

---

## Recommended order of work

Ordered by (Evidence Gained / Cost):

1. **Add Intra-Household Diversity Limitation to 2J Manuscript** (Finding **G-4**)
   - *Action*: Insert a concise limitations paragraph in [`readySubmission.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md) acknowledging that `HHSIZE × AT_HOME` assumes perfectly synchronized household presence.
   - *Cost*: 1 hour text edit. Zero compute.
2. **Fix Floor Area Constants in Entry Documents** (Finding **G-1**)
   - *Action*: Update lines 320 and 125 of `3rdJ_00_4split_Occupancy_Pipeline.md` and `_Overview.md` to state parsed areas `135,857.6 m²` (SuperTall) and `72,623.1 m²` (Tall).
   - *Cost*: 30 mins text edit.
3. **Purge Non-Existent StatCan Table Citation** (Finding **G-3**)
   - *Action*: Replace all occurrences of `Table 24-10-0048-01` with explicit references to Tourisme Québec / ISQ and Travel Alberta / CBRE.
   - *Cost*: 30 mins text edit.
4. **Re-Specify Hotel As-Modelled PASS Criterion** (Finding **G-2**)
   - *Action*: Update `dr_L3-03` and `3rdJ_00_4split_Occupancy_Pipeline.md` to define distinct PASS bands for Small Hotel (`180–240` kWh/m²/yr) and Large Hotel / High-Rise Podium (`280–480` kWh/m²/yr).
   - *Cost*: 1 hour documentation update.
5. **Update Pipeline Architecture Naming in Diagrams & Text** (Finding **G-5**)
   - *Action*: Relabel "4-head Transformer" to "3 GSS Transformer Heads + 1 SARIMA Hotel Side-Track" in overview text and figure captions.
   - *Cost*: 30 mins documentation update.
