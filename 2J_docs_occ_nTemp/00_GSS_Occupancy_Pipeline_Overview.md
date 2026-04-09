# Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM
### Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)
#### Full Pipeline Overview — Updated with Steps 1–3 Validation + 30-Min Resolution

---

## AIM
Construct a comprehensive, annually-representative synthetic occupancy dataset — covering all temporal strata per occupant archetype — from GSS Canada Time Use cycles (2005–2022), augmented via deep learning and forecast to 2030, for direct integration into BEM/UBEM residential energy simulations.

> **Confirmed temporal stratum structure (Step 3):** `SURVMNTH` is absent (NaN) for 2005/2010; available for 2015/2022. `DDAY` grouped into **3 `DDAY_STRATA`** (1=Weekday, 2=Saturday, 3=Sunday) as cross-cycle temporal denominator.
>
> **Resolution design:** Raw episodes are first tiled to HETUS 10-min slots (144 per day), then **downsampled to 30-min slots (48 per day)** before Transformer training. This matches BEM/UBEM schedule granularity and reduces Transformer sequence length by 3×.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  STEP 1 — DATA COLLECTION & COLUMN SELECTION                                ║
║  Status: COMPLETE — 100% pass rate (39/39 checks)                           ║
║                                                                              ║
║  GSS MAIN: occID, SURVYEAR, SURVMNTH*, PR, HHSIZE, AGEGRP, SEX, MARSTH,    ║
║            KOL, ATTSCH, NOCS, LFTAG, COW, HRSWRK, CMA,                     ║
║            POWST, TOTINC, WGHT_PER, WTBS_001-500                           ║
║  * SURVMNTH: NaN for 2005/2010 (correct); has values for 2015/2022          ║
║                                                                              ║
║  GSS EPISODE: occID, EPINO, DDAY, start/end (HHMM), startMin/endMin,       ║
║               duration, occACT (->14 grouped categories),                  ║
║               occPRE (->AT_HOME),                                           ║
║               Co-presence [9 unified cols, OR-merged in Step 2]:           ║
║               Alone, Spouse, Children, parents, otherInFAMs,               ║
║               otherHHs, friends, others,                                   ║
║               colleagues (TUI_06I; 2015/22 only — NaN for 2005/2010),     ║
║               techUse (TUI_07), wellbeing (TUI_10: 2015/22 only),          ║
║               WGHT_EPI, WTBS_EPI_001-500                                    ║
║                                                                              ║
║  CENSUS PUMF (2006/2011/2016/2021 — Step 5 linkage only):                  ║
║  BUILTH, DTYPE, BEDRM, ROOM, CONDO, REPAIR, VALUE, + family/income vars    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — DATA HARMONIZATION                                                ║
║  Status: COMPLETE — 100% pass rate (54/54 checks)                           ║
║                                                                              ║
║  Confirmed results:                                                          ║
║    SURVMNTH: NaN for 2005/2010 (correct); values for 2015/2022              ║
║    TUI_01 crosswalk -> 14 grouped categories: 0.00% unmapped all cycles     ║
║    AT_HOME rates: 2005=63.5%, 2010=63.5%, 2015=66.1%, 2022=72.3%           ║
║      (2022 spike = COVID-19 stay-at-home / remote work behavioral shift)    ║
║    DIARY_VALID pass: 2005=98.3%, 2010=98.5%, 2015=100%, 2022=100%          ║
║    COLLECT_MODE: 2005/2010=0 (CATI), 2022=1 (EQ)                           ║
║    TUI_10_AVAIL: 2005/2010=0, 2015/2022=1                                  ║
║    Co-presence OR-merge: NHSDCL15→Children, NHSDPAR→parents,               ║
║      NHSDC15P→otherInFAMs (2005/2010); TUI_06F→otherInFAMs (2015/2022)    ║
║    colleagues: TUI_06I (2015/2022); NaN for 2005/2010 (not measured)       ║
║    TOTINC regime: self-reported (2005-2015) / CRA-linked (2022)             ║
║    Bootstrap: MEAN_BS (2005/2010) / STANDARD_BS (2015/2022)                ║
║    CYCLE_YEAR + SURVYEAR appended; weight delta-mean = 0.0000               ║
║                                                                              ║
║  SOLVED FAILURES:                                                            ║
║    POWST naming mismatch across cycles (CTW_Q140 vs CTW_140x variants)      ║
║    Episode column mismatch across cycles                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — MERGE & TEMPORAL FEATURE DERIVATION + RESOLUTION DOWNSAMPLING    ║
║  Status: COMPLETE — 99% pass rate (81/82 checks)                            ║
║                                                                              ║
║  LEFT JOIN: Episode <- Main on occID  |  0 orphan episodes                 ║
║                                                                              ║
║  Derived columns:                                                            ║
║    DDAY_STRATA: 1=Weekday / 2=Saturday / 3=Sunday (confirmed [1,2,3])      ║
║    DAYTYPE: Mon-Fri=Weekday / Sat-Sun=Weekend                               ║
║    HOUR_OF_DAY, TIMESLOT_10, AT_HOME, DIARY_VALID                           ║
║    (SEASON dropped — seasonal JS <0.001, AT_HOME lift <2pp on weekdays)     ║
║                                                                              ║
║  Sub-step 3C — HETUS 144-slot intermediate (10-min resolution):            ║
║    144 activity slots (14 categories) + 144 AT_HOME slots = 288 col/person ║
║    Slot completeness: 100% all cycles                                        ║
║    Night checks: sleep 83.7%, AT_HOME 93.4%                                 ║
║                                                                              ║
║  Sub-step 3E — Downsample to 48 slots (30-min resolution) for BEM/UBEM:   ║
║    Rule: majority vote across 3 consecutive 10-min slots per 30-min window ║
║    Tie-breaking: AT_HOME 1 > 0; activity ties -> longest continuous run     ║
║    Output: 48 activity + 48 AT_HOME tokens = 96 columns per respondent     ║
║    File: hetus_30min.csv  (64,061 rows x 96 columns)                        ║
║    Computational benefit vs 10-min: ~9x reduction in attention operations  ║
║                                                                              ║
║  Confirmed respondent counts (post DIARY_VALID filter):                     ║
║  +------------+------------+------------+------------+------------+         ║
║  | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 GSSP  |  TOTAL     |         ║
║  |   19,221   |   15,114   |   17,390   |   12,336   |   64,061   |         ║
║  | excl 1.92% | excl 1.79% | excl 0.00% | excl 0.00% | excl 1.01% |         ║
║  | wtd 62.7%  | wtd 62.3%  | wtd 64.5%  | wtd 70.6%  | (AT_HOME)  |         ║
║  +------------+------------+------------+------------+------------+         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: CONDITIONAL TRANSFORMER (Augmentation)                  ║
║  Status: PENDING (ready to start)                                           ║
║                                                                              ║
║  Input: hetus_30min.csv (96 tokens per respondent: 48 activity + 48 home)  ║
║         + co-presence [9 cols x 48 slots] from merged_episodes.csv         ║
║  Problem: Each respondent has 1 of 3 DDAY_STRATA observed                  ║
║  Goal:    Generate synthetic schedules for the other 2 DDAY_STRATA         ║
║                                                                              ║
║  Architecture: Conditional Transformer Encoder-Decoder                      ║
║    Encoder input:                                                            ║
║      48 slots × 11 features per slot (multivariate token):                 ║
║        [occACT (14-cat), AT_HOME (binary),                                  ║
║         Alone, Spouse, Children, parents, otherInFAMs,                      ║
║         otherHHs, friends, others, colleagues]                              ║
║      colleagues masked to 0 for 2005/2010 (not measured)                   ║
║      Conditioning: [demog. profile + DDAY_STRATA +                          ║
║                     CYCLE_YEAR + COLLECT_MODE]                              ║
║      (SURVMNTH/SEASON dropped — see W3 decision)                            ║
║    Decoder input: target DDAY_STRATA + cross-attention over encoder         ║
║    Output per target stratum:                                               ║
║      48 activity tokens (14 categories)                                     ║
║      + 48 AT_HOME tokens (binary)                                           ║
║      + 9 × 48 co-presence tokens (binary per column per slot)              ║
║                                                                              ║
║  Training:                                                                   ║
║    Cross-entropy over 14 categories x 48 slots (activity)                  ║
║    + BCE over AT_HOME x 48 slots                                            ║
║    + BCE over co-presence x 9 cols x 48 slots                              ║
║      (colleagues loss masked out for 2005/2010 rows)                        ║
║    Validation: JS divergence per stratum                                    ║
║                                                                              ║
║  Output: 64,061 x 3 = ~192,183 synthetic diary-days (all cycles)           ║
║  HPC cost: ~1.5-3 hrs on 1x GPU node (vs ~4-8 hrs at 144 slots)            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 5 — CENSUS-GSS PROBABILISTIC LINKAGE (Classical ML)                  ║
║  Status: PENDING                                                             ║
║                                                                              ║
║  Stage A: K-means archetype clustering on GSS augmented data (K=20-50)     ║
║  Stage B: Random Forest -> assign Census records to GSS archetypes          ║
║  Stage C: Aggregate building vars per archetype (BUILTH, DTYPE, BEDRM...)  ║
║  Output: Building profile lookup table per occupant archetype               ║
║  Cost: negligible (classical ML, minutes on CPU)                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 6 — MODEL 2: PROGRESSIVE FINE-TUNING + FORECASTING (2030)            ║
║  Status: PENDING                                                             ║
║                                                                              ║
║  Anchors (confirmed x3 strata): 2005=57K, 2010=45K, 2015=52K, 2022=37K    ║
║  Total: ~192,183 augmented diary-days                                        ║
║                                                                              ║
║  Sub-A: Base training on 2005 (70%) -> W_2005                              ║
║         True future test: 10'GSS unseen                                     ║
║                                                                              ║
║  Sub-B: Progressive fine-tuning with weight inheritance                     ║
║    W_2005 -> 05'+10' -> DRIFT_MATRIX_0510 -> W_2010_ft                     ║
║             (true future test: 15'GSS unseen)                               ║
║    W_2010_ft -> 05'+10'+15' -> DRIFT_MATRIX_1015 -> W_2015_ft              ║
║             (true future test: 22'GSS unseen)                               ║
║    W_2015_ft -> all cycles -> W_2022_ft                                     ║
║    * DRIFT_MATRIX_1522 captures COVID-19 AT_HOME shift: 63% -> 70.6%       ║
║                                                                              ║
║  Sub-C: Pooled training with recency weights                                ║
║    loss weights: 2005=0.10 / 2010=0.20 / 2015=0.30 / 2022=0.40            ║
║    Trend Encoder -> 2030 projected activity distributions                   ║
║                                                                              ║
║  Sub-D: 2030 forecasting                                                    ║
║    Scenario features: age distribution, WFH rates, commute mode share      ║
║    Output: 96-token (30-min) diaries per archetype x DDAY_STRATA           ║
║                                                                              ║
║  Validation: True Future Test per phase                                     ║
║  HPC cost: ~8-13 hrs on 1x GPU node                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 7 — BEM/UBEM INTEGRATION                                              ║
║  Status: PENDING                                                             ║
║                                                                              ║
║  Input: 2030 synthetic schedules at 30-min resolution (Step 6)             ║
║         + building profiles (Step 5)                                        ║
║                                                                              ║
║  Per archetype x building type:                                             ║
║    1. Hourly occupancy probability (AT_HOME, 0.0-1.0) per 30-min slot      ║
║    2. Activity-specific metabolic gain (W/person, ASHRAE 55/ISO 7730)      ║
║    3. Stratify: DDAY_STRATA (Weekday / Saturday / Sunday)                  ║
║    4. Province (PR) -> ASHRAE climate zone mapping                         ║
║                                                                              ║
║  Output formats:                                                             ║
║    EnergyPlus Schedule:Compact (30-min timestep, weekday/Sat/Sun)           ║
║    CSV: hourly probability x archetype x climate zone x DDAY_STRATA        ║
║    UBEM-ready: compatible with CityGML-linked building stock models         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Two separate DL models (Step 4 + Step 6) | Decomposes complexity; Model 1 learns schedule structure, Model 2 learns temporal trends |
| Conditional Transformer over C-VAE | Superior long-range dependency capture; better scaling for multi-stratum conditioning |
| HETUS 10-min (144 slots) as intermediate format (Step 3C) | Preserves full GSS temporal granularity and HETUS compatibility; used as archival intermediate before downsampling |
| **30-min downsampling to 48 slots before training (Step 3E)** | EnergyPlus/BEM operate at 30-min or hourly timesteps — 10-min adds no useful information for energy simulation. Reduces Transformer sequence length 3x, cutting attention cost ~9x. Training time: ~1.5-3 hrs vs ~4-8 hrs |
| Majority-vote for 30-min aggregation (Step 3E) | Each 30-min slot inherits the most frequent activity across its 3 source slots. AT_HOME: 1 takes precedence over 0; activity ties resolved by longest continuous run |
| Census linkage via classical ML (Step 5) | Avoids joint DL complexity; building variables suit archetype-level probabilistic matching |
| SURVYEAR as explicit variable (Step 1A) | Required for longitudinal pooling; primary indexing axis for Model 2 trend encoding |
| TOTINC harmonized as two regimes (Step 2) | Pre-2022 = self-reported; 2022 = CRA T1FF. Confirmed pass |
| TUI_01 -> 14 grouped categories (Step 2) | 0.00% unmapped rate confirmed all cycles; appropriate granularity for BEM occupancy states |
| Co-presence OR-merged into 9 unified columns (Step 2) | NHSDCL15/NHSDPAR/NHSDC15P (2005/2010) and TUI_06F (2015/2022) OR-merged into existing columns rather than dropped; `colleagues` (TUI_06I) new column, NaN for 2005/2010 — no equivalent measured |
| Co-presence as per-slot encoder features + decoder output (Step 4) | 9 binary co-presence cols embedded in each 30-min slot token; synthetic diaries include predicted co-presence; `colleagues` BCE loss masked for 2005/2010 |
| COLLECT_MODE as model covariate (Steps 2 + 4) | Disentangles behavioral change from CATI vs. EQ collection artefacts |
| DIARY_VALID QA filter (Step 3) | Confirmed exclusion: 2005=1.92%, 2010=1.79%, 2015/2022=0.00% |
| TUI_10 as auxiliary variable only (Steps 1B + 4) | Absent 2005/2010; excluded from cross-cycle model inputs |
| DDAY_STRATA = 3 categories (Step 3) | SURVMNTH confirmed NaN for 2005/2010. Cross-cycle temporal denominator is Weekday/Saturday/Sunday |
| SEASON dropped (Step 3) | Seasonal JS divergence <0.001 across all activity pairs; AT_HOME lift <2 pp on weekdays — sub-noise-floor signal (see docs_debug/02_W3_season_lift.md) |
| 2022 AT_HOME = 70.6% vs ~63% baseline (Step 2) | COVID-19 behavioral shift confirmed; DRIFT_MATRIX_1522 documents this explicitly |
| Progressive fine-tuning with weight inheritance (Step 6) | Encodes temporal ordering; reduces per-phase training time |
| DRIFT_MATRIX at each cycle transition (Step 6) | 3 publishable drift outputs: per-activity, per-stratum, per-archetype JS divergence |
| True Future Test validation (Step 6) | Next unseen cycle as holdout simulates the forecasting task |
| Recency weighting: 2022=0.40 to 2005=0.10 (Step 6) | Correct prior for 2030; recent patterns are stronger predictors |
| POWST + Episode column mismatches — solved issues (Step 2) | Confirmed pass before full-fidelity pooling and Step 4 training |
