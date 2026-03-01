# Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM
### Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)
#### Full Pipeline Overview

---

## AIM
Construct a comprehensive, annually-representative synthetic occupancy dataset — covering all 84 DDAY × SURVMNTH strata per occupant archetype — from GSS Canada Time Use cycles (2005–2022), augmented via deep learning and forecast to 2030, for direct integration into BEM/UBEM residential energy simulations.

---

```
╔══════════════════════════════════════════════════════════════════════════╗
║  STEP 1 — DATA COLLECTION & COLUMN SELECTION                            ║
║                                                                          ║
║  GSS MAIN FILE (Cycles 19/24/29/GSSP: 2005/2010/2015/2022)             ║
║  ┌─ Identity & Temporal ──────────────────────────────────────────────┐ ║
║  │  occID (PUMFID), SURVYEAR, SURVMNTH                                │ ║
║  ├─ Demographic ─────────────────────────────────────────────────────┤ ║
║  │  PR, HHSIZE, AGEGRP, SEX, MARSTH, KOL, ATTSCH, NOCS, LFTAG,      │ ║
║  │  COW, HRSWRK, MODE, POWST, CMA                                    │ ║
║  ├─ Socioeconomic ───────────────────────────────────────────────────┤ ║
║  │  TOTINC (self-reported 2005–2015 / CRA-linked 2022)               │ ║
║  └─ Weights ─────────────────────────────────────────────────────────┘ ║
║     WGHT_PER, WTBS_001–500                                              ║
║                                                                          ║
║  GSS EPISODE FILE (same cycles)                                         ║
║  ┌─ Identity & Temporal ──────────────────────────────────────────────┐ ║
║  │  occID, EPINO, DDAY, start/end (HHMM), startMin/endMin, duration  │ ║
║  ├─ Occupancy Content ───────────────────────────────────────────────┤ ║
║  │  occACT (TUI_01, 63 activity codes), occPRE (LOCATION→AT_HOME)    │ ║
║  ├─ Social Context ──────────────────────────────────────────────────┤ ║
║  │  Spouse, Children, Friends, otherHHs, Others (TUI_06A–J)         │ ║
║  ├─ Auxiliary (cycle-dependent) ────────────────────────────────────┤ ║
║  │  techUse (TUI_07), wellbeing (TUI_10: 2015/2022 only)            │ ║
║  └─ Weights ─────────────────────────────────────────────────────────┘ ║
║     WGHT_EPI, WTBS_EPI_001–500                                          ║
║                                                                          ║
║  CENSUS PUMF (2006/2011/2016/2021 — for Step 5 linkage only)           ║
║  BUILTH, DTYPE, BEDRM, ROOM, CONDO, REPAIR, VALUE,                     ║
║  GENSTAT, CITIZEN, CF_RP, CFSTAT, EFSIZE, CFSIZE, EMPIN, INCTAX, CIP  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — DATA HARMONIZATION (per cycle: 2005/2010/2015/2022)          ║
║                                                                          ║
║  Column renames → unified schema                                        ║
║  Category recoding (SEX, MARSTH, AGEGRP, LFTAG, ATTSCH, PR, CMA)      ║
║  Missing value alignment (96/97/98/99 → NaN)                           ║
║                                                                          ║
║  ⚠ Critical harmonization flags:                                        ║
║  • TOTINC regime break: self-reported (2005–2015) / CRA-linked (2022)  ║
║  • TUI_01 crosswalk: 2022 hierarchical tree → 63-code flat scheme      ║
║  • COLLECT_MODE flag: 0=CATI (2005/2010) / 1=EQ (2022)                ║
║  • TUI_10_AVAIL flag: 0=absent (2005/2010) / 1=present (2015/2022)    ║
║  • Bootstrap flag: MEAN_BS (2005/2010) / STANDARD_BS (2015/2022)      ║
║  • DIARY_VALID QA: assert sum(DURATION per occID) == 1440 min          ║
║  • CYCLE_YEAR + SURVYEAR appended as longitudinal labels               ║
║                                                                          ║
║  Output: 4 harmonized cycle pairs (Main + Episode), identical schema   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — MERGE & TEMPORAL FEATURE DERIVATION                          ║
║                                                                          ║
║  LEFT JOIN: Episode ← Main on occID                                    ║
║  Weight rule: WGHT_EPI (episode-level) / WGHT_PER (person-level)       ║
║                                                                          ║
║  Derived columns:                                                        ║
║  • SEASON       ← SURVMNTH (Dec/Jan/Feb=Winter … Sep/Oct/Nov=Fall)     ║
║  • DAYTYPE      ← DDAY (Mon–Fri=Weekday / Sat–Sun=Weekend)             ║
║  • HOUR_OF_DAY  ← startMin // 60  → 0–23                              ║
║  • TIMESLOT_10  ← startMin // 10 + 1  → slots 1–144 (HETUS format)    ║
║  • AT_HOME      ← LOCATION==300 → binary 1/0                          ║
║  • STRATA_ID    ← DDAY × SURVMNTH → integer 1–84                      ║
║                                                                          ║
║  HETUS 144-slot conversion:                                             ║
║  Variable-length episodes → 144 fixed 10-min activity tokens per person ║
║  (4:00 AM start; diary integrity: sum(duration)==1440 enforced)        ║
║                                                                          ║
║  Output: ~69,000 diary rows (each has 1 of 84 strata observed)         ║
║  ┌────────────┬────────────┬────────────┬────────────┬────────────┐    ║
║  │ 2005 (C19) │ 2010 (C24) │ 2015 (C29) │ 2022 GSSP  │  TOTAL     │    ║
║  │ ~19,600    │ ~15,390    │ ~17,390    │ ~17,000    │ ~69,000    │    ║
║  └────────────┴────────────┴────────────┴────────────┴────────────┘    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: CONDITIONAL TRANSFORMER (Augmentation)              ║
║                                                                          ║
║  Problem: Each respondent has 1 of 84 DDAY × SURVMNTH strata observed  ║
║  Goal:    Generate synthetic schedules for the other 83 strata          ║
║                                                                          ║
║  Architecture: Conditional Transformer Encoder-Decoder                  ║
║  ┌─ Encoder input ────────────────────────────────────────────────────┐ ║
║  │  144 activity tokens (observed diary)                              │ ║
║  │  Conditioning: [demog. profile + DDAY + SURVMNTH +                 │ ║
║  │                 CYCLE_YEAR + COLLECT_MODE]                         │ ║
║  ├─ Decoder input ────────────────────────────────────────────────────┤ ║
║  │  Target conditioning: [same demog. + target DDAY + SURVMNTH]      │ ║
║  │  Cross-attention over encoder output                               │ ║
║  └─ Output ───────────────────────────────────────────────────────────┘ ║
║     144 synthetic activity tokens for target stratum                    ║
║                                                                          ║
║  Training: Cross-entropy loss over 63 activity categories × 144 slots  ║
║  Constraint: sequence must sum to 144 slots (1440 min diary integrity) ║
║  Validation: JS divergence between synthetic & observed distributions  ║
║                                                                          ║
║  Output: ~69,000 × 84 ≈ 5.8M synthetic diary-days across all cycles   ║
║  HPC cost: ~4–8 hrs on 1× GPU node (Concordia)                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 5 — CENSUS–GSS PROBABILISTIC LINKAGE (Classical ML)              ║
║                                                                          ║
║  Purpose: Link building/dwelling variables (Census) to occupant         ║
║  archetypes (GSS) — no shared ID; matched via shared sociodemographics  ║
║                                                                          ║
║  Stage A — Archetype Clustering                                         ║
║  K-means on GSS augmented data (K=20–50 archetypes)                    ║
║  Features: PR × AGEGRP × SEX × MARSTH × HHSIZE × LFTAG × TOTINC × CMA ║
║                                                                          ║
║  Stage B — Census Classification                                        ║
║  Random Forest: assign each Census record to nearest GSS archetype      ║
║  Features: same shared sociodemographic variables                       ║
║                                                                          ║
║  Stage C — Building Profile Aggregation                                 ║
║  Per archetype_ID: aggregate BUILTH, DTYPE, BEDRM, ROOM, VALUE,        ║
║  REPAIR, CONDO → probability distribution of building characteristics   ║
║                                                                          ║
║  Output: Building profile lookup table per occupant archetype           ║
║  Cost: negligible (classical ML only; minutes on CPU)                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 6 — MODEL 2: PROGRESSIVE FINE-TUNING + FORECASTING (2030)        ║
║                                                                          ║
║  Sub-A — Base training on 2005 data                                     ║
║  Train on 05'GSS (70%) from random weights → save W_2005               ║
║  True future test: evaluate on 10'GSS (unseen)                         ║
║                                                                          ║
║  Sub-B — Progressive fine-tuning with weight inheritance                ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │  W_2005 → fine-tune on 05'+10' → MEASURE SHIFT 0510            │   ║
║  │         → save W_2010_ft  |  true future test: 15'GSS           │   ║
║  │                                                                  │   ║
║  │  W_2010_ft → fine-tune on 05'+10'+15' → MEASURE SHIFT 1015     │   ║
║  │           → save W_2015_ft  |  true future test: 22'GSS         │   ║
║  │                                                                  │   ║
║  │  W_2015_ft → fine-tune on all cycles → save W_2022_ft           │   ║
║  └─────────────────────────────────────────────────────────────────┘   ║
║  DRIFT_MATRIX (0510 / 1015 / 1522): per-activity, per-stratum,         ║
║  per-archetype JS divergence → 3 publishable drift outputs             ║
║                                                                          ║
║  Sub-C — Pooled training with recency weights                           ║
║  All 4 cycles | loss weights: 2005=0.10 / 2010=0.20 / 2015=0.30 /     ║
║  2022=0.40 | Trend Encoder → 2030 projected activity distributions     ║
║                                                                          ║
║  Sub-D — 2030 forecasting                                               ║
║  Scenario features (Stats Canada / UN): age, WFH rates, commute mode   ║
║  Output: 144-slot synthetic diaries per archetype × 84 strata          ║
║                                                                          ║
║  Validation: True Future Test (next unseen cycle as holdout per phase)  ║
║  HPC cost: ~8–13 hrs on 1× GPU node (2× original; vs. 5× full chart)  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  STEP 7 — BEM/UBEM INTEGRATION                                          ║
║                                                                          ║
║  Input: 2030 synthetic schedules (Step 6) + building profiles (Step 5) ║
║                                                                          ║
║  Per archetype × building type combination:                             ║
║  1. Hourly occupancy probability (AT_HOME, 0.0–1.0) per hour of day    ║
║  2. Activity-specific metabolic gain (W/person) per ASHRAE 55/ISO 7730 ║
║  3. Stratify: season × daytype → 3 types × 4 seasons = 12 variants     ║
║  4. Province (PR) → ASHRAE climate zone mapping                        ║
║                                                                          ║
║  Output formats:                                                         ║
║  • EnergyPlus Schedule:Compact (annual, weekday/weekend/holiday)        ║
║  • CSV lookup: hourly probability × archetype × climate zone × season  ║
║  • UBEM-ready: compatible with CityGML-linked building stock models     ║
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
| SURVYEAR as explicit variable (Step 1A) | Required for longitudinal pooling; primary indexing axis for Model 2 trend encoding |
| TOTINC harmonized as two regimes (Step 2) | Pre-2022 = self-reported categorical; 2022 = CRA T1FF continuous. Pooling without harmonization introduces systematic artefact |
| TUI_01 crosswalk mandatory for 2022 (Step 2) | 2022 hierarchical tree → 63-code flat scheme; required for cross-cycle occACT comparability |
| COLLECT_MODE as model covariate (Steps 2 + 4) | Disentangles true behavioral change from CATI vs. EQ collection mode artefacts |
| DIARY_VALID QA filter (Step 3) | Corrupted diaries (sum ≠ 1440 min) cannot produce valid 144-slot HETUS sequences |
| TUI_10 as auxiliary variable only (Steps 1B + 4) | Available only in 2015/2022; excluded from cross-cycle inputs to maintain consistent architecture |
| Progressive fine-tuning with weight inheritance (Step 6) | Encodes temporal ordering; reduces per-phase training time vs. random re-initialization |
| Measure Shift / DRIFT_MATRIX (Step 6) | Three publishable drift matrices (0510, 1015, 1522) quantifying behavioral change per activity, stratum, and archetype |
| True Future Test validation (Step 6) | Next unseen cycle as holdout simulates the actual forecasting task; stronger than within-cycle random splits |
| Recency weighting: 2022=0.40 → 2005=0.10 (Step 6) | Correct prior for 2030 forecasting; recent patterns are stronger predictors |
| Full five-column flowchart NOT adopted (Step 6) | ~90% methodological value at ~2× compute vs. ~5× for full structure |
