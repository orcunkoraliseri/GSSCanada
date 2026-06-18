# Residential + Office Two-Channel Occupancy Pipeline for BEM/UBEM
### Longitudinal Occupancy-Driven Energy Demand (2005–2030) — Leg 2 of 3
#### Full Pipeline Overview — 2-Channel Split (Residential reused + Office added)

---

## AIM
Extend the completed residential GSS → BEM pipeline into a **two-channel generator**: a **Residential (AT_HOME)** channel that *replaces* BEM baseline schedules, and a parallel **Office (AT_WORK)** channel that *modulates* code-compliant densities — both from the same GSS cycles, same Transformer backbone, forecast to 2030.

> **Three-leg roadmap.** Leg 1 = Residential (COMPLETE, 2nd Journal). **Leg 2 = Residential + Office (this doc).** Leg 3 = + Retail + Hotel (3rd-Journal target).
>
> **Status convention.** Residential portions = **COMPLETE (Leg 1, unchanged)**; Office portions = **PLANNED (Leg 2)**. The single real build delta is tiling AT_WORK into the 48-slot arrays (Step 3); everything else reuses or lightly extends Leg-1 machinery. Companion detail doc: `3rdJ_00_2split_Occupancy_Pipeline.md`.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  STEP 1 — DATA COLLECTION & COLUMN SELECTION                                ║
║  Residential: COMPLETE (Leg 1)   |   Office gating vars: PLANNED (Leg 2)    ║
║                                                                              ║
║  Reuse Leg-1 Main + Episode columns. ADD office employment-gating vars:     ║
║    activity-last-week  MAR_Q100 / ACT7DAYS / ACT7DAYC                       ║
║    worked-last-week    WKLTWE / MRW_D40B                                    ║
║    LF status           LFSGSS (derived 2015/22)                             ║
║    hours/week          WKWEHR_C / WHWD140C / WHWD140G                       ║
║    NOC / NAICS         SOC91C10·NOCS2006 / NAICS2002·2007 / NOC1110 etc.    ║
║    telework / WFH      MAR_Q190 / WTI_130 / TLWK_01A-D                      ║
║  KEY: occPRE already on every episode row, all 4 cycles                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — DATA HARMONIZATION                                                ║
║  Status: occPRE crosswalk COMPLETE (Leg 1)  |  AT_WORK confirm: PLANNED     ║
║                                                                              ║
║  AT_HOME = occPRE==1   (Leg 1)                                              ║
║  AT_WORK = occPRE==2   ← all 4 cycles                                       ║
║    2005/2010 PLACE=02  |  2015 LOCATION=301  |  2022 LOCATION=3301          ║
║    2015/22: gate work-vs-school via employment vars                         ║
║  WFH wrinkle: 2022 paid-work-at-home coded LOCATION=3300 (home) — CORRECT   ║
║    for office BEM (worker physically absent); WFH recovered via TLWK_01A    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — MERGE & TILING  ← THE ONE REAL BUILD DELTA                        ║
║  Status: PLANNED (Leg 2)                                                    ║
║                                                                              ║
║  GAP: Step-3C tiler expands only AT_HOME into the 48-slot arrays;           ║
║       occPRE/AT_WORK lives only at episode level                            ║
║                                                                              ║
║  FIX (Option B, list-driven — recommended, low-risk):                       ║
║    reuse tile_copresence_to_30min  (03_mergingGSS.py:821-944)               ║
║    AT_WORK = (occPRE==2).astype(float)                                      ║
║    same 4AM-origin slot math (startMin-240)%1440  : line 889               ║
║    same binary majority vote  sum>=2              : lines 903-918           ║
║    naming f"{col}30_{i:03d}" -> WORK30_001..048   : line 924               ║
║    CONSERVATIVE: clone to separate CSV; residential path bit-identical      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: MULTI-HEAD CONDITIONAL TRANSFORMER                       ║
║  Status: PLANNED (Leg 2) — shared encoder reuses J3                         ║
║                                                                              ║
║  ENCODER (shared): token = [occACT(14), AT_HOME, AT_WORK, 9 co-presence]    ║
║    conditioning += NOCS, COW, HRSWRK                                        ║
║  DECODER: Head 1 (existing: activity+home+co-presence)                      ║
║           Head 2 (NEW: 48 AT_WORK binary tokens)                           ║
║                                                                              ║
║  MANDATORY multi-head machinery (not tuning — build work):                  ║
║    SLAW / homoscedastic UW loss weighting (replaces equal weighting)       ║
║    PCGrad gradient surgery (kills negative transfer)                        ║
║    diversity-preserving loss (not MSE-only -> avoids COP peak collapse)     ║
║  Office target (verbatim from Empirical report, verified 2026-06-13):      ║
║    wkday peak 09:30-11:30 & 14:30-16:30 @0.50-0.55 priv/0.75-0.80 open;     ║
║    lunch dip 12-13:30 @0.25-0.35, true peak ~15h, night 0.02-0.05           ║
║    day-of-week: pre-COVID Mon highest; post-COVID hybrid Tue-Thu/Fri light  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 5 — ARCHETYPE LINKAGE                                                 ║
║  Residential (Census linkage): COMPLETE (Leg 1)                            ║
║  Office (NOC x NAICS lookup): PLANNED (Leg 2)                              ║
║                                                                              ║
║  knowledge/professional -> OpenOffice+ClosedOffice, 9-5                     ║
║  public/health/education -> +Classroom+Restroom                            ║
║  sales/customer-facing -> mixed hours, weekend non-zero                    ║
║  trades/production -> NOT office (excluded)                                 ║
║  output: per-respondent office_archetype_ID                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 6 — MODEL 2: FORECAST 2030 + WFH                                      ║
║  Status: progressive fine-tuning COMPLETE (Leg 1)  |  WFH scalar: PLANNED   ║
║                                                                              ║
║  reuse 4-stage progressive fine-tuning; DRIFT_MATRIX_1522 = COVID WFH jump  ║
║  WFH_RATE scalar:  2019 ~7% -> 2020 ~40% -> 2022 ~30% -> 2023 ~20%         ║
║  2030 = THREE sensitivity bands (this scalar dominates office EUI):         ║
║    Conservative 15-20% WFH | Hybrid ~30% | Fully Hybrid ~40%               ║
║  energy NON-LINEAR: 20-50% occ cut -> only ~10-30% energy savings          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 7 — BEM/UBEM INTEGRATION  ← THE CORE ASYMMETRY                        ║
║  Residential REPLACE: COMPLETE (Leg 1)  |  Office MODULATE: PLANNED         ║
║                                                                              ║
║  Residential: schedule = presence*default + (1-presence)*baseload;         ║
║               Number_of_People = HHSIZE                                     ║
║  Office:      schedule = code_baseline(t) * AT_WORK_fraction(t)             ║
║               keep code peak density (NO HHSIZE): NECB office 25 m2/person, ║
║               LPD 10 W/m2, plug 7.5 W/m2 | ASHRAE LPD 6.5, plug 8.0 W/m2    ║
║    lighting  L = max(Lmin, eta*O*D),  Lmin 0.10-0.20, auto-off 20min       ║
║    plug      P = Pbase + (1-Pbase)*O, Pbase 0.15-0.30 (never zero)         ║
║    Schedule:File @30-min; Interpolate-to-Timestep = deliberate choice       ║
║  Tag-2 routing: apartment->replace | office tags->modulate |                ║
║                 hotel/retail->skip(Leg3) | MEP/circulation->baseline        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 8 — BEM SIMULATION                                                    ║
║  Status: PLANNED (Leg 2)                                                    ║
║                                                                              ║
║  extend Leg-1 paired Monte-Carlo (frozen frame, hold IDF+TMY, vary occ)    ║
║  add PNNL Tall/SuperTall OFFICE zones (~30% SuperTall / ~24% Tall area)    ║
║  outputs: 8760 office load profiles + MC bands, peak-hour shift,            ║
║           load-shape metrics; annual EUI = secondary                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 9 — ACTIVITY-DRIVEN END-USE LOADS (equipment + lighting)              ║
║  Status: PLANNED (Leg 2)                                                    ║
║                                                                              ║
║  scale office equipment + lighting by AT_WORK presence (Lmin/Pbase floors)  ║
║  calibrate magnitude vs commercial benchmark (NRCan SCIEU / NECB)           ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## VALIDATION GATES (AT_WORK channel, per day-type)

| Tier | Metric | Threshold |
|---|---|---|
| 1 Distributional | KL (arrival/departure) | < 0.05 |
| 1 | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 |
| 1 | Presence-rate RMS | ≤ 5 pp per day-type |
| 2 Structural | Transition-matrix Frobenius/MAE | < 0.05 |
| 2 | Dwell-time KS test | p > 0.05 (fail to reject) |
| 2 | Autocorrelation MAE (lags 1–24 h) | < 0.05 |
| 3 Downstream (ASHRAE G14) | NMBE | monthly ±5%, hourly ±10% |
| 3 | CV(RMSE) | monthly 15%, hourly 30% |
| 3 | Peak demand + timing | magnitude ±15%; **timing ≤ 1 h** |

> Add **EMD/Wasserstein, transition-matrix, dwell-time KS, C2ST** (≈50% target) vs Leg 1. Select on the **Pareto frontier** (Wasserstein + ACF-MAE + downstream peak) — **never a single composite**.
>
> **⚠️ Threshold provenance (audited 2026-06-13).** NMBE ±5%/±10% and CV(RMSE) 15%/30% = **ASHRAE Guideline 14** (cite the standard — the source report's cells were blank). C2ST≈0.5, dwell-KS, Pareto, exposure-bias = confirmed in the report. The `< 0.05` / ±15% / ≤1 h gates are **project-chosen**, not literature — do not cite them to the source.

---

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Share the encoder between Residential and Office | Encoder learns universal time-of-day/day-of-week structure; only the output head is channel-specific — ~½ the parameters, consistent latent space. |
| Office **modulates**, Residential **replaces** | Preserves code-compliant peak densities (W/m², people/m²) for regulatory comparability while injecting the GSS *temporal* signal. |
| `Number_of_People = HHSIZE` does NOT apply to office | Office headcount = NECB17 per-m² density, not GSS household composition. |
| AT_HOME ⊕ AT_WORK mutual exclusion NOT enforced | Diary slots can legitimately be neither (commute, errands, third places). |
| SLAW/UW loss weighting + PCGrad are mandatory | Equal-weight MSE multi-head collapses peaks (COP failure mode); these are build work, not tuning. |
| Conservative tiling variant (separate CSV) | Residential Phase F/H stays bit-identical → zero risk to Leg-1 results; office is purely additive. |
| WFH exposed as an explicit model-output scalar | Single dominant lever for the 2030 office forecast; sensitivity bands are a re-run, not a retrain. |
| Pareto model selection, never composite | The Leg-1 composite chose a 2/4-gate model — lesson learned. |
| Residential pipeline unchanged | Leg 2 ships without re-running any Leg-1 residential figures. |

---

## OPEN DECISIONS (resolve before/within Leg 2)

1. MDLM vs multi-head Transformer — RESOLVED 2026-06-18 (Transformer baseline retained; MDLM rejected due to validation gate failures and computation overhead; see [dr_S4-03_architecture_choice_REPORT.md](file:///c:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/deepResearch/dr_S4-03_architecture_choice_REPORT.md)).
2. Interpolate-to-Timestep `Yes`/`No` in Step 7.
3. Model office→retail lunch transition, or treat channels independently.
4. Shared-vs-separate backbone ablation for reviewer defensibility.
5. Image-locked numbers RESOLVED 2026-06-13 (densities/LPD/diurnal verified from source PDFs). Remaining caveat: validation thresholds were blank in the source → cite ASHRAE G14 for NMBE/CV(RMSE); the 0.05/±15%/≤1h gates are project-chosen, not literature.

> Graphical abstract `Residential-Office_Pipeline.png` already exists in this folder and may be referenced for the two-track (residential teal / office orange) visual.
