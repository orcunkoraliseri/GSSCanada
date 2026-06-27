# Step 4 — Diary Augmentation: J2 (single-channel) vs J3 Leg-2 (two-channel)

*Scope: factual side-by-side of the Step-4 conditional generative model between J2 Leg-1 (`2J_docs_occ_nTemp/`) and J3 Leg-2 two-split (`3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/`). Numbers are cited to source documents where they appear.*

---

## 1. Purpose & Method Delta

| Dimension | J2 Leg-1 | J3 Leg-2 |
|---|---|---|
| **Objective** | Fill the two unobserved day-types (of Weekday/Sat/Sun) for each of 64,061 GSS respondents. Outputs residential occupancy only. | Same filling task, but now produces **two occupancy channels jointly**: residential AT_HOME **and** office AT_WORK. |
| **Production model name** | **Calibrated J3** (J3 Hybrid AR-Encoder + Phase 8B raking) | **R10_fast → 04L floataware rake → 04M** (J3 backbone ported as `JSeriesHybrid2Split`, winner from a 6-variant single-axis HPT sweep) |
| **Architecture** | Shared encoder trunk → AR activity arm (14-class) + non-autoregressive (NAT) binary arm (`AT_HOME` + 9 co-presence heads). `detach()` barrier separates the two arms. d_model=256, 8 heads, 6 layers, d_ff=1024. | Identical backbone (`JSeriesHybrid2Split`). **Single structural addition**: a third binary head (`AT_WORK`) bolted onto the NAT arm, mirroring `AT_HOME`. `detach()` barrier preserved unchanged. d_model=256 (baseline R0; d_model=384 R6 variant tested, R5/R10 at d_model=256 won). |
| **Multi-head training discipline** | Standard: fixed loss weights (act CE + AT_HOME BCE + COP BCE + `marg_loss`). No gradient surgery. | **New machinery (all ON by default, env-toggled):** (1) **Uncertainty weighting (UW/SLAW)** — one learnable log-variance `log σ²_t` per task `{act, home, work, cop}`; (2) **PCGrad gradient surgery** — de-conflicts per-task gradients before optimizer step; (3) **Diversity-preserving loss** — per-(cycle×stratum) marginal-matching term on home AND work diurnal curves. Source: `3rdJ_04_augmentationGSS.md` §Delta D. |
| **Work tiler** | n/a | `work_30min.csv` from Step-3 Leg-2 supplies the `WORK30_001..048` binary track. Source: `3rdJ_04_augmentationGSS.md` §Data Source Inventory. |
| **Research history** | 40+ trials across F/G/H/I/MDLM/J-series (sample-first progressive funnel, 2%→10%→100%); J3 was the first and only 4/4-gate model. Source: `04_augmentationGSS.md` §2–3. | Architecture search **skipped** — J3 topology already proven. Single-axis sweep of 6 hyperparameter variants (R0–R6) off the J3 baseline. R5_lr1e4 (LR=1e-4) selected as Pareto winner; R10_fast is the promoted production model. Source: `3rdJ_04_augmentationGSS.md` progress log 2026-06-16. |

---

## 2. Inputs

| Input | J2 Leg-1 | J3 Leg-2 |
|---|---|---|
| **Step-3 activity/occupancy** | `outputs_step3/hetus_30min.csv` — 64,061 rows × ~120 cols; `act30_001..048` (14-class) + `hom30_001..048` (binary) + demographics. | Same file from Leg-2 Step 3. |
| **Co-presence** | `outputs_step3/copresence_30min.csv` — 64,061 rows × ~433 cols; 9 channels × 48 slots. | Same. |
| **Office work track** | Not present. | **`work_30min.csv` [Leg-2 NEW]** — 64,061 rows, `WORK30_001..048` binary AT_WORK track. Source: `3rdJ_04_augmentationGSS.md` §Data Source Inventory. |
| **Conditioning vector (`cond_vec`)** | d_cond = **90**. Base columns: `AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, HRSWRK, NOCS, COW, ATTSCH, POWST, COLLECT_MODE, TOTINC` + cycle/strata. Source: `04_augmentationGSS_val.md` progress log 2026-05-22. | d_cond = **119**. Same base + **three office additions**: `NAICS` (industry bucket, one-hot), `TELEWORK` (binary flag + known-indicator), `WORK_SCHEDULE` (shift category, one-hot, 9 values). Source: `3rdJ_04_augmentationGSS.md` §Delta B. |
| **Tensor schema** | `aux_seq (n, 48, 10)` — `[AT_HOME(1) | 9 co-presence]`. | **`aux_seq (n, 48, 11)`** — `[AT_HOME(1) | AT_WORK(1) | 9 co-presence]`. Plus **`work_avail (n, 48) bool`** mask for AT_WORK NaN slots. Source: `3rdJ_04_augmentationGSS.md` §CONTRACT. |

---

## 3. Outputs

### 3.1 File names and schema

| Item | J2 Leg-1 | J3 Leg-2 |
|---|---|---|
| **Primary output file** | `outputs_step4/augmented_diaries.csv` | `outputs_step4/augmented_diaries.csv` (raw / pre-rake) |
| **Canonical final deliverable** | `outputs_step4/augmented_diaries.csv` after 04L Phase 8B raking + 04M min-dwell — "Calibrated J3". Local file is this calibrated version. | **`sweep/R10_fast/ → 04L floataware rake → 04M` — on Speed cluster** at `/speed-scratch/o_iseri/GSSCanada/.../sweep/R10_fast_floataware_raked_mindwell/`. Local `outputs_step4/augmented_diaries.csv` is the raw R5/R10_fast pre-rake version (~381 MB, 400,139,256 bytes). Source: `3rdJ_04_augmentationGSS_val.md` progress log 2026-06-22. |
| **Row count** | **192,183** (64,061 observed + 128,122 synthetic = 64,061 × 3 day-types). Confirmed: `04_augmentationGSS_val.md` progress log 2026-05-12. | **192,183** identical count (64,061 obs + 128,122 syn). Confirmed: `3rdJ_04_augmentationGSS.md` progress log 2026-06-15 (job 968495 written, and re-confirmed in job 968526 verified entry). |
| **Column count** | ~548 (header row read from `2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv`): `occID, CYCLE_YEAR, DDAY_STRATA, SURVYEAR` + 14 demo cols + `act30_001..048` (48) + `hom30_001..048` (48) + 9×48 co-presence cols (432) + `IS_SYNTHETIC`. | **596 columns** — same as J2 plus `wrk30_001..048` (48 new cols) + 3 new demo cols (`NAICS, TELEWORK, WORK_SCHEDULE`). Confirmed: `3rdJ_04_augmentationGSS.md` progress log 2026-06-15: "shape (192183, 596)". |
| **Key new columns** | — | `wrk30_001..048` (binary 0/1 AT_WORK per 30-min slot). Mutually exclusive with `hom30_*` (0 overlap enforced at inference and by 04L rake). |
| **Co-presence values** | Observed rows: binary 0/1 copied from Step 3. **Synthetic rows**: written as raw sigmoid probabilities (float [0,1]), not thresholded binary — a known design choice downstream for rank-to-marginal assignment. Source: `3rdJ_04_augmentationGSS.md` progress log 2026-06-16 (G3 root-cause entry). | Same convention inherited. |
| **Training log** | `step4_training_log.csv`: `epoch, train_loss, act_loss, home_loss, cop_loss, marg_loss, val_js, home_gap, val_score, lr, grad_norm, elapsed_s`. (Confirmed from file header.) | `step4_training_log.csv` adds: `work_loss, div_loss, sigma_act, sigma_home, sigma_work, sigma_cop, work_gap`. (Confirmed from file header.) |

---

## 4. Calibration / Post-Processing

| Stage | J2 Leg-1 | J3 Leg-2 |
|---|---|---|
| **Rake (04L)** | **Phase 8B per-(stratum×slot) marginal raking** — standard iterative proportional fitting targeting observed/projected AT_HOME marginals, applied to the post-linkage population the Step-5/6 validator scores. Predecessor: pool-level raking (8B-5) was diluted by Step-5 re-sampling; moved to post-linkage population (8B-5b). Source: `04_augmentationGSS.md` §4. | **`04L_joint_rake_2split.py` with `--floating_aware` flag (production).** Joint home+work rake that routes work-activity slots first (TELEWORK→home, else→work) before hitting marginal targets — prevents the classic rake from manufacturing "floating" records (act=work but neither hom30=1 nor wrk30=1). Predecessor `3rdJ_04L_joint_rake_2split.2026-06-20.py` archived before edit. Source: `3rdJ_04_augmentationGSS.md` progress log 2026-06-20. |
| **Floating artifact** | Not applicable (single-channel; no cross-channel coherence requirement). | Classic rake alone manufactured ~25–30% FLOATING slots (model pre-rake was 0.00% floating). Float-aware rake closes FLOATING → 0.00%. Source: `3rdJ_04_augmentationGSS.md` progress log 2026-06-20 ("FLOATING root-caused"). |
| **Min-dwell smoother (04M)** | `04M_mindwell.py` — merges 1-slot binary blips in hom30 (85,287 slots changed) and co-presence; brought transition-rate (GB gate) from 2.000× → 1.000×. Applied after 04L. Source: `3rdJ_04_augmentationGSS.md` progress log 2026-06-20 (04M validated job 981413). | Identical `3rdJ_04M_mindwell_2split.py` applied after 04L; extends blip-merging to **both** `hom30` and `wrk30`. Source: same. |
| **Peak-shaver (04N)** | Not built. | `3rdJ_04N_peak_shaver_2split.py` built and tested. Production diagnosis: FILL direction (syn under-fills work peak by 10.33 pp); sweep (w=2/3/4) moved G4 only **0.1 pp** (structural floor — GA coherence + exact-marginal constraints prevent enough mass relocation). **Dropped** from the final chain. Source: `3rdJ_04_augmentationGSS_val.md` progress log 2026-06-22. |
| **Post-processing chain** | raw J3 → 04L → 04M → Calibrated J3 | R10_fast → 04L (floataware) → 04M → production artifact |
| **2030 forecast calibration** | Phase 8B extended to 2030 (COVID-persists p=1); AT_HOME 79.70%; gates 5.1–5.6 PASS. Source: `04_augmentationGSS.md` §4. | Not yet run (Step 6 2030 forecast is the next stage). |

---

## 5. Validation — Gates and Scorecards

### 5.1 Gate definitions

| Gate | J2 Leg-1 threshold | J3 Leg-2 threshold | Notes |
|---|---|---|---|
| **G1 Activity JS** | JS < 0.05 per (cycle×stratum); overall < 0.03 | Same | Unchanged. |
| **G2 AT_HOME RMS** | ≤ 2.0 pp per cell (PASS); 2–4 pp WARN | Same | J2 model-gate used ≤5.3 pp (a looser gate in the model leaderboard); the validator gate is 2 pp. |
| **G3 Co-presence max gap** | ≤ 3.0 pp per channel | Same | J2 doc calls it "COP max gap ≤5.0 pp" in the four-gate leaderboard, but the validator threshold is 3 pp. Source: `04_augmentationGSS_val.md` §5.1, `3rdJ_04_augmentationGSS_val.md`. |
| **G4 Temporal** | Transition rate ±20%; work peak ≤3 pp; sleep continuity | Same | |
| **OW1 AT_WORK presence RMS** | n/a | ≤ 5.0 pp PASS; 5–8 pp WARN | **Leg-2 new.** |
| **OW2 Diurnal-shape r** | n/a | ≥ 0.95 PASS (weekday) | **Leg-2 new.** |
| **OW3 Peak-timing shift** | n/a | ≤ 2 slots (≤1 h) | **Leg-2 new.** |
| **OW4 Night near-zero** | n/a | < 5% AT_WORK rate, slots 41–48/1–4 | **Leg-2 new.** |
| **OW5 Day-type ordering** | n/a | ≥ 90% respondents with WD ≥ Sat ≥ Sun | **Leg-2 new.** |
| **OW6 Channel exclusivity** | n/a | < 1% cells with hom30=1 AND wrk30=1 | **Leg-2 new.** |

### 5.2 Validation scorecards — side by side

| Report | J2 v4 (raw Cond. Transformer, 2026-04-23) | J2 v5 (Calibrated J3, 2026-05-31) | J3 Leg-2 (R10_fast floataware rake + min-dwell, LOCKED 2026-06-22) |
|---|---|---|---|
| **PASS / WARN / FAIL** | 28 / 1 / **17** | **21 / 1 / 0** | **68 / 1 / 2** |
| Check inventory | 46 granular checks | 21 consolidated checks | 71 checks (G1–G4 + OW1–OW6 + secondaries) |
| AT_HOME gate (G2) | all 12 cells FAIL (2.95–9.69 pp) | per-(stratum×slot) EXACT | 0.65 pp grand mean — PASS |
| Activity JS (G1) | 0.0242 | **0.0191** | PASS (0.0160 for R5 pre-rake; post-rake not separately quoted) |
| Co-presence (G3) | PASS (5.2/5.4/5.5) | PASS | WARN — worst channel `others` 4.04 pp (8/9 channels PASS) |
| Temporal (G4) | FAIL — transition rate ratio 157.95× | PASS | **FAIL — work-peak delta 10.33 pp** (structural under-fill; gate ≤3 pp) |
| AT_WORK presence (OW1) | n/a | n/a | 0.03 pp — **PASS** (exact via rake) |
| AT_WORK diurnal r (OW2) | n/a | n/a | **PASS** |
| Peak-timing shift (OW3) | n/a | n/a | **PASS** (0 slots) |
| Night near-zero (OW4) | n/a | n/a | **PASS** (≤5%) |
| Day-type ordering (OW5) | n/a | n/a | **FAIL — 63%** (gate ≥90%; unobservable — 1 diary/person) |
| Channel exclusivity (OW6) | n/a | n/a | **PASS** (0 cells) |
| 4-model-gate verdict | n/a (pre-gate model) | **4/4 PASS** | n/a (different gate set; all calibratable gates PASS) |
| Work proxy / G4 | FAIL (swapped code bug, ignored) | "expected-FAIL" at 3.27 pp Work proxy — documented, not counted | FAIL at 10.33 pp (honest, code bug not present) |

Source: `04_augmentationGSS_val.md` progress log 2026-06-01 (v4 vs v5 comparison); `3rdJ_04_augmentationGSS_val.md` progress log 2026-06-22 (locked scorecard).

### 5.3 Key metric numbers

| Metric | J2 Calibrated J3 | J3 Leg-2 production |
|---|---|---|
| Activity JS (overall) | **0.0191** | **0.0160** (R5 gate-table; post-rake value not separately quoted) |
| AT_HOME RMS (aggregate) | 4.57 pp raw J3; **exact** per-(stratum×slot) after raking | **0.65 pp** after floataware rake |
| AT_HOME max gap (per-slot) | 15.37 pp raw J3 → 0 after raking | not separately quoted (0.65 pp is grand mean) |
| COP max gap | ~2.03 pp (raw J3 gate) | WARN, worst `others` 4.04 pp |
| Work-peak delta (G4) | 3.27 pp "expected-FAIL" (partly code-bug confounded) | **10.33 pp FAIL** (structural) |
| AT_WORK presence RMS | n/a | **0.03 pp** (exact via rake) |
| FLOATING rate (act=work, no location) | n/a | **0.00%** after floataware rake (was 25–30% from classic rake) |
| Training val_score (best checkpoint) | 0.0759 (R0 baseline) → **0.0357** (R5_lr1e4) in J3-Leg2 run | 0.0357 (R5/R10_fast) |

Sources: `04_augmentationGSS.md` §3–4; `3rdJ_04_augmentationGSS.md` progress log 2026-06-16 gate tables; `3rdJ_04_augmentationGSS_val.md` locked scorecard.

---

## 6. What Is Genuinely New in J3 vs Carried Over from J2

| Item | Status |
|---|---|
| J3 Hybrid AR-Encoder backbone | **Carried over** verbatim (clean port of `04B_model_J3.py`) |
| AT_HOME + co-presence generation | **Carried over** (same NAT arm, same `detach()` barrier) |
| Training pairs (K=5 demographic-match neighbour day-type pairs) | **Carried over** (`04C_pairs_2split.py` ported verbatim) |
| 04L marginal raking concept | **Carried over** (adapted from Leg-1 Phase 8B); raking logic extended to joint home+work + float-aware routing |
| 04M min-dwell smoother | **Carried over** (extended to `wrk30` channel) |
| **AT_WORK binary head** | **NEW** — third NAT head (`work_head = Linear → Tanh → Linear`), mirroring `home_head`. Source: `3rdJ_04_augmentationGSS.md` §Delta C. |
| **`work_30min.csv` input** | **NEW** — Step-3 Leg-2 office work track. |
| **d_cond = 119 (+29 vs J2's 90)** | **NEW** — adds `NAICS, TELEWORK, WORK_SCHEDULE` one-hot/binary conditioning. |
| **UW dynamic loss weighting** | **NEW** — learnable log-variance per task; prevents one head from dominating training. |
| **PCGrad gradient surgery** | **NEW** — eliminates negative gradient transfer across home/work/cop heads. |
| **Diversity-preserving loss** | **NEW** — marginal-matching penalty on diurnal shape for both home and work. |
| **Float-aware rake** | **NEW** — routes work-activity slots coherently before raking to prevent synthetic FLOATING artefacts (classic rake manufactured 100% of observed FLOATING). |
| **04N peak-shaver** | **NEW** (built, validated on sample, **dropped** from production chain — structural floor at 0.1 pp). |
| **OW1–OW6 office validation gates** | **NEW** — 6 additional gate checks for the AT_WORK channel. |
| Work-gap metric in training log | **NEW** — `work_gap` alongside `home_gap` in `step4_training_log.csv`. |
| Architecture search / HPT history | **Not repeated** — J3 architecture was locked; only single-axis hyperparameter sweep needed (6 variants, one cluster wave). |

---

## 7. Caveats and Risks for the Paper

1. **G4 work-peak (10.33 pp) is a documented FAIL.** The activity head under-produces work at peak slots (obs 28.72%, syn 18.39%) on the floataware-raked production base. The post-rake filler (04N) hit a structural floor of ~0.1 pp improvement — the exact-marginal constraints enforced by the rake prevent one-for-one slot swaps from redistributing enough work mass. This failure is on the `act30` channel only; `wrk30` marginals are exact. If the paper reports G4, it must note this gap and its cause. Source: `3rdJ_04_augmentationGSS_val.md` progress log 2026-06-22 (locked decision).

2. **OW5 day-type ordering (63% vs gate ≥90%) is unobservable — not a calibration failure.** GSS provides one diary day per respondent; there is no ground truth for whether a given respondent's synthetic weekday attendance ≥ Saturday ≥ Sunday. The 63% pass rate cannot be improved without assuming ordering from occupation/telework flags, which would be a modelling assumption. The paper should flag OW5 as a data-limitation caveat, not a model deficiency. Source: `3rdJ_04_augmentationGSS_val.md` progress log 2026-06-22.

3. **J2's "work-peak PASS" was partly confounded by a code bug.** The J2 validator `04F_validation.py` had Work/Sleep activity codes swapped in several places (raw code 1 = Work, raw code 5 = Sleep were inverted in gates 4.1, 4.3, 6.2, 7.1, 7.2). J2 v5 reported a "work proxy 3.27 pp expected-FAIL" in the known-bug region and documented it. J3 does not inherit this bug. A direct J2 v5 vs J3 work-peak comparison must note the confounding; the J3 10.33 pp gap is a more honest measurement. Source: `04_augmentationGSS_val.md` header caveat + progress log 2026-06-01.

4. **FLOATING artefact was discovered and closed, but the mechanism is worth noting.** Classic marginal raking on a post-hoc inference base (where 04E forced 100% AT-WORK for work-activity slots) manufactured 25–30% FLOATING records (act=work but hom30=0, wrk30=0 simultaneously). The float-aware rake was the correct fix. The paper should acknowledge that raking coherence constraints must be designed jointly with inference-level post-hoc rules when multiple location channels are present.

5. **Local `augmented_diaries.csv` in `Step4_docs/outputs_step4/` is the raw R5/R10_fast pre-rake version** (~381 MB, 192,183 rows, 596 cols). The canonical production artifact (R10_fast → 04L floataware → 04M) was produced on the Speed cluster and is not stored locally. Any downstream Step-5/6/7 pipeline must point to the cluster copy (or a downloaded version of it). Source: `3rdJ_04_augmentationGSS_val.md` progress log 2026-06-23 (04L2 local vs cluster determination note).

6. **Co-presence (G3) carries a WARN** — the `others` channel is 4.04 pp off (obs 7.7%, syn 3.7%). This is within the WARN band (3–6 pp) and 8/9 channels PASS. It is not blocking for Step 5/6/7 (BEM keys off `hom30`), but if co-presence channels are used in occupancy profiling, the `others` under-prediction should be mentioned. Source: `3rdJ_04_augmentationGSS.md` progress log 2026-06-16 (G3 fixed validator per-channel results for R5).

7. **The check inventory sizes differ (21 vs 71 checks)**, making raw PASS counts incompatible. J2 v5 consolidated to 21 higher-level checks; J3 runs 71 checks across G1–G4 + OW1–OW6 + secondary metrics. The meaningful comparators are: (a) hard FAIL counts (J2: 0; J3: 2), (b) the specific gate values listed in §5.3 above.

---

## Document Map

| Source document | What it covers |
|---|---|
| `2J_docs_occ_nTemp/04_augmentationGSS.md` | J2 model journey (40+ trials), leaderboard, calibration narrative |
| `2J_docs_occ_nTemp/04_augmentationGSS_val.md` | J2 gate definitions, v4 vs v5 scorecard comparison, code-bug caveat |
| `2J_docs_occ_nTemp/04_augmentationGSS_hpc.md` | J2 HPC submission procedures (Phase 1–9) |
| `2J_docs_occ_nTemp/04_augmentationGSS_testing.md` | J2 local testing plan and smoke-test ranges |
| `2J_docs_occ_nTemp/outputs_step4/step4_validation_report_v5.html` | J2 canonical validation report (Calibrated J3) |
| `3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS.md` | J3 architecture, delta specs, HPT sweep, calibration decisions, LOCKED chain |
| `3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS_val.md` | J3 gate definitions, scorecard, 04N investigation, LOCKED decision |
| `3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/augmented_diaries.csv` | J3 raw R5/R10_fast pre-rake diaries (local; 192,183 rows, 596 cols) |
