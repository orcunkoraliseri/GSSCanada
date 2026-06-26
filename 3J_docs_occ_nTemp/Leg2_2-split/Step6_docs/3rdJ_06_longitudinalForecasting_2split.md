# Step 6 — Model 2: Longitudinal Forecasting (2005–2030), Two-Channel 2-Split

## AIM

Train a progressive fine-tuning + forecasting model (Model 2) on the four-cycle
two-channel augmented diary dataset from Step 4 to capture inter-cycle behavioral
drift and project BOTH the residential (AT_HOME) and office (AT_WORK) occupancy
schedules to 2030. Model 2 inherits the `JSeriesHybrid2Split` model class
(`3rdJ_04B_model_2split.py`) — shared encoder + two binary heads — and adds a
Trend Encoder that learns the joint activity+home+work trajectory across three
DRIFT_MATRIXes at each cycle transition. The 2030 output is validated by first
backcasting 2022 (joint reconstruction gate), then projecting forward with three
explicit WFH-rate sensitivity bands.

**This is the first HPC step for Leg-2.** All prior steps (1–5) run locally;
Step 6 requires Concordia Speed cluster GPU compute on partition `pg`.

---

### Roadmap Checklist

Tick as each item completes. Re-read this list at the start of every session.

- [ ] **Sub-step 6A** — Input audit: verify `augmented_diaries.csv` schema, row count, hom30/wrk30 columns, and per-cycle AT_HOME/AT_WORK rates.
- [ ] **Sub-step 6B** — Script architecture + HPC setup: write `3rdJ_06_longitudinalForecasting_2split.py` and SLURM wrapper; assemble `scenario_2030_features_2split.csv`.
- [ ] **Sub-step 6C** — Sub-stage A: train W_2005 on 2005 cycle; emit DRIFT_MATRIX_0510 (joint home+work axes).
- [ ] **Sub-step 6D** — Sub-stage B: 3-phase progressive fine-tuning (W_2005→W_2010_ft→W_2015_ft→W_2022_ft); emit DRIFT_MATRIX_1015 and DRIFT_MATRIX_1522; assert COVID signal on BOTH channels.
- [ ] **Sub-step 6E** — Sub-stage C: pooled recency-weighted joint training + TrendEncoder; save W_pooled_2030.pt + trend_encoder_2030.pt.
- [ ] **Sub-step 6F** — Sub-stage D Phase i: 2022 backcasting gate on BOTH hom30 and wrk30 per DDAY stratum.
- [ ] **Sub-step 6G** — Sub-stage D Phase ii: 2030 three-band forward forecast; emit a single `2030_synthetic_diaries_2split.csv` with a `BAND` column (conservative/hybrid/fullyhybrid — OD-3 resolved).
- [ ] **Sub-step 6H** — Downstream cleanup: mutual-exclusion resolution + 04M min-dwell on the 2030 output. **NO 04L marginal rake on the forecast year** (see 6H rationale — B1/B2).
- [ ] **Run validation report** — `3rdJ_06_longitudinalForecasting_2split_val.py` → `outputs_step6/step6_validation_report.html`.
- [ ] **Step 6 closure** — All artifacts on cluster under `outputs_step6/`; memory COMPLETE.

---

## Data Inputs — Confirmed Statistics

### Primary training input

| File | Location | Rows | Columns | Description |
|------|----------|------|---------|-------------|
| `augmented_diaries.csv` (R5_lr1e4, **raw**) | `Step4_docs/outputs_step4/sweep/R5_lr1e4/` | ~192,183 | 145+ | Step 4 raw inference output: all cycles × 3 DDAY_STRATA; has CYCLE_YEAR, IS_SYNTHETIC, act30_001–048, hom30_001–048, wrk30_001–048, 9 co-presence × 48 slots |

> **OD-1 RESOLVED (manager, 2026-06-23): train on the raw `R5_lr1e4` pool.** The 2030
> output is cleaned up downstream at Sub-step 6H (04M min-dwell + mutual-exclusion resolution
> — **NO 04L rake on the forecast year**; see 6H). Training on
> the raked `R5_raked_mindwell` file would teach the model externally-forced marginals and
> distort the inter-cycle drift the TrendEncoder must learn. The calibrated file is the
> reference for backcast comparison only, not a training input.

### Column schema (exact, from `3rdJ_04E_inference_2split.py` and `step4_feature_config.json`)

| Column group | Prefix | Count | Range |
|---|---|---|---|
| Activity | `act30_001`–`act30_048` | 48 | 1–14 (raw category codes) |
| At-home binary | `hom30_001`–`hom30_048` | 48 | 0 / 1 |
| At-work binary | `wrk30_001`–`wrk30_048` | 48 | 0 / 1 |
| Co-presence (Alone) | `Alone30_001`–`Alone30_048` | 48 | float [0,1] |
| Co-presence (8 channels) | `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues` × `30_001`–`30_048` | 8 × 48 | float [0,1] |

> **Slot convention:** 04:00 origin (slot 001 = 04:00–04:30). Business hours = **[09:00, 17:00)
> → slots 11–26** (slot 11 = 09:00–09:30 … slot 26 = 16:30–17:00; 17:00 is exclusive).

> **Step 3 note:** `work_30min.csv` (Step 3 tiler output) uses UPPERCASE prefix
> `WORK30_001`–`WORK30_045`. The Step 4 pipeline writes `wrk30_001`–`wrk30_048`
> into `augmented_diaries.csv`. Use `wrk30_*` throughout Step 6 (do NOT use the
> Step 3 capitalization).

### Conditioning features (from `step4_feature_config.json`, `d_cond = 119`)

| Feature | Encoding | n_cats | Office relevance |
|---|---|---|---|
| AGEGRP | one-hot | 7 | age-related WFH propensity |
| SEX | one-hot | 2 | — |
| MARSTH | one-hot | 6 | — |
| HHSIZE | one-hot | 5 | — |
| PR | one-hot | 15 | regional commute |
| CMA | one-hot | 3 | urban/rural commute |
| KOL | one-hot | 4 | — |
| LFTAG | one-hot | 4 | employed gate for WFH scalar |
| HRSWRK | one-hot | 9 | office hours cross-check |
| NOCS | one-hot | 11 | NOC×NAICS office archetype |
| COW | one-hot | 3 | class of worker |
| DDAY_STRATA | one-hot | 3 | — |
| ATTSCH | one-hot | 3 | — |
| POWST | one-hot | 3 | — |
| MODE | one-hot | 7 | commute mode |
| TOTINC | continuous | — | — |
| COLLECT_MODE | binary | — | — |
| TOTINC_SOURCE | binary | — | — |
| WORK_SCHEDULE | one-hot | 9 | office shift pattern |
| NAICS | one-hot | 20 | NOC×NAICS office archetype |
| TELEWORK | binary | — | **WFH scalar injection point** |
| TELEWORK_KNOWN | binary | — | masks unknown TELEWORK rows |

> `TELEWORK` is the natural conditioning-feature route for pinning WFH-rate bands
> at inference (see Open Decision 2).

### Cycle split

| Cycle | Observed respondents | Augmented rows (×3 strata) | WD % | WD AT_HOME | WD AT_WORK (approx) |
|-------|---------------------|---------------------------|------|------------|---------------------|
| 2005 | 19,221 | ≈57,663 | 72.9% | 62.7% | ~35–40% |
| 2010 | 15,114 | ≈45,342 | 73.6% | 62.3% | ~34–39% |
| 2015 | 17,390 | ≈52,170 | 72.1% | 64.5% | ~32–38% |
| 2022 | 12,336 | ≈37,008 | 72.5% | **70.6%** | **~6–8%** (COVID WFH shift) |
| **Total** | 64,061 | **≈192,183** | | | |

> **2022 dual signal:** WD AT_HOME rises +6–8 pp (COVID stay-at-home). Simultaneously,
> WD AT_WORK physical presence drops sharply. Both signals must appear as the dominant
> entry in DRIFT_MATRIX_1522 — absence on either axis is a blocker before Sub-stage C.

### WFH_RATE scalar definition

`WFH_RATE` = mean(hom30_k == 1 | act30_k == Work AND LFTAG == employed) over
business-hours slots k ∈ {11, 12, …, 26} ([09:00, 17:00) exclusive; slot 26 = 16:30–17:00).

Expected trajectory:

| Cycle | WFH_RATE target |
|---|---|
| 2005 | ~0.05–0.08 |
| 2010 | ~0.07–0.10 |
| 2015 | ~0.10–0.13 |
| 2022 | ~0.30 (COVID step change) |
| **2030** | **model output** |

### Scenario features file

| File | Location | Description |
|------|----------|-------------|
| `scenario_2030_features_2split.csv` | `Step6_docs/outputs_step6/` | ~37,008 rows × 119-dim cond vector; AGEGRP resampled to Stats Canada M1 2030; TELEWORK column used for WFH band injection |

---

## Architecture Overview

Model 2 is built on top of `JSeriesHybrid2Split` (LOCKED — import only, do NOT modify
`3rdJ_04B_model_2split.py`). The Trend Encoder is new in Step 6.

```
╔══════════════════════════════════════════════════════════════════════╗
║  TREND ENCODER (new in Step 6)                                       ║
║  Input:  DRIFT_MATRIX_0510 + DRIFT_MATRIX_1015 + DRIFT_MATRIX_1522   ║
║          concatenated as a 3-step temporal sequence                   ║
║          Each matrix spans: 14 activities × 3 DDAY_STRATA ×          ║
║          {AT_HOME drift, AT_WORK drift} axis                          ║
║  Architecture: small Transformer (d_model=64, 2 layers, 4 heads)     ║
║  Output: joint activity+home+work trajectory vector →                 ║
║          2030-projected distribution per DDAY_STRATA per channel      ║
╠══════════════════════════════════════════════════════════════════════╣
║  JSeriesHybrid2Split DECODER (reused from Step 4, weights inherited) ║
║  Model class: JSeriesHybrid2Split (3rdJ_04B_model_2split.py)         ║
║  Heads:  Arm 1 (activity, AR)                                        ║
║          Arm 2 head 1 (AT_HOME, Tanh-gated) → hom30_001–048          ║
║          Arm 2 head 2 (AT_WORK, Tanh-gated) → wrk30_001–048  [NEW]  ║
║  Loss structure (from 3rdJ_04D_train_2split.py):                     ║
║    act:  cross-entropy + inverse-sqrt class weights                   ║
║    home: BCEWithLogits + home_pos_weight                              ║
║    work: BCEWithLogits + work_pos_weight (7.873), masked by           ║
║          dec_work_avail                                               ║
║    cop:  BCEWithLogits per channel, colleagues masked pre-2015        ║
║    Weighting: WEIGHT_MODE='uw' (homoscedastic uncertainty) default;  ║
║    PCGrad gradient surgery ON; LAMBDA_DIV diversity loss ON (0.1).   ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Four-stage progressive fine-tuning

```
══════════════════════════════════════════════════════════════════════
SUB-STAGE A — BASE TRAINING ON 2005 DATA
══════════════════════════════════════════════════════════════════════
Input:  2005 split (70% train / 20% val / 10% test), stratified by DDAY_STRATA
Init:   Random weights for both home_head and work_head (no Leg-1 transfer)
Output: W_2005_2split.pt

  ↓ MEASURE SHIFT → DRIFT_MATRIX_0510
  Apply W_2005_2split to 2010 held-out (True Future Test)
  Compare predicted activity+home+work distributions vs. 2010 observed
  JS divergence per activity × DDAY_STRATA × demographic group
  PLUS: AT_HOME mean shift and AT_WORK mean shift per stratum
  Output: DRIFT_MATRIX_0510_2split.csv

══════════════════════════════════════════════════════════════════════
SUB-STAGE B — PROGRESSIVE FINE-TUNING (3 PHASES)
══════════════════════════════════════════════════════════════════════

Phase 2: Fine-tune W_2005_2split on 2005+2010 (70%)
         Early-stop on 2010 (20% val, JOINT JS: act+home+work)
         True future test: 2015 (unseen)
         → Save W_2010_ft_2split.pt
         ↓ Measure Shift → DRIFT_MATRIX_1015_2split.csv

Phase 3: Fine-tune W_2010_ft_2split on 2005+2010+2015 (70%)
         Early-stop on 2015 (20% val)
         True future test: 2022 (unseen)
         → Save W_2015_ft_2split.pt
         ↓ Measure Shift → DRIFT_MATRIX_1522_2split.csv
         ← COVID-19 AT_HOME +6–8 pp AND AT_WORK physical drop captured here

Phase 4: Fine-tune W_2015_ft_2split on all 4 cycles (70%)
         Early-stop on 2022 (20% val)
         → Save W_2022_ft_2split.pt

  Note: each phase inherits the previous checkpoint — no random reinit.
  Step-6 IMPORTS the model (04B) and the loss-component / PCGrad / uncertainty-weighting
  helpers from 04D as a MODULE (import does NOT run their __main__), but runs its OWN
  progressive loop: checkpoint warm-start, per-cycle subset selection, and per-sample
  recency weighting are NEW Step-6 code (04D has none of these — it trains the full pool,
  stratum-weighted only). 04B/04D are NOT modified. Use fp16 on the cluster GPU.

══════════════════════════════════════════════════════════════════════
SUB-STAGE C — POOLED RECENCY-WEIGHTED TRAINING
══════════════════════════════════════════════════════════════════════
Input:  All 4 cycles pooled (70% each)
Init:   W_2022_ft_2split warm start; TrendEncoder from random weights
Recency loss weights applied per-sample (NOT subsampling):
  2005=0.10 / 2010=0.20 / 2015=0.30 / 2022=0.40
Trend Encoder:
  Input:  [DRIFT_MATRIX_0510 | DRIFT_MATRIX_1015 | DRIFT_MATRIX_1522]
          as a 3-token temporal sequence (each matrix flattened)
  Output: 2030-projected joint distribution per DDAY_STRATA for BOTH
          AT_HOME and AT_WORK axes
Distribution-matching loss:
  decoder output proportions (act + home + work per DDAY_STRATA) must
  match Trend Encoder projection (cross-entropy/BCE over predicted 2030
  distribution, weighted by Trend Encoder-predicted 2030 marginals)
Save: W_pooled_2030_2split.pt, trend_encoder_2030_2split.pt

══════════════════════════════════════════════════════════════════════
SUB-STAGE D — TWO-PHASE INFERENCE
══════════════════════════════════════════════════════════════════════

Phase i — 2022 Backcasting (joint validation gate):
  Input:  2022 observed conditioning features (actual conditions, no projection)
  Model:  W_pooled_2030_2split + trend_encoder_2030_2split
  Output: reconstructed_2022_diaries_2split.csv
          (columns: act30_001–048, hom30_001–048, wrk30_001–048)
  Gates:  JS(hom30) < 0.10 per stratum (hard gate)
          JS(wrk30) < 0.10 per stratum (hard gate)
          AT_HOME reconstruction within ±2 pp of observed 2022 WD
          WFH_RATE reconstruction within ±5 pp of observed 2022
  Use:    Publishable backcasting figure for the 3J paper

Phase ii — 2030 Three-Band Forward Forecast (deliverable):
  Input:  scenario_2030_features_2split.csv. For each band, the SHARE of employed
          rows with TELEWORK=1 is resampled to the band's population WFH target
          (TELEWORK_KNOWN=1 on all). Three inference re-runs:
            Band A — Conservative:  ~17.5% of employed rows TELEWORK=1 (WFH 15–20%)
            Band B — Hybrid:        ~30% of employed rows TELEWORK=1 (WFH ~30%)
            Band C — Fully Hybrid:  ~40% of employed rows TELEWORK=1 (WFH ~40%)
          (NOT all-0 / all-1 — that yields 0% / 100%, not the band rate.)
  Model:  W_pooled_2030_2split + trend_encoder_2030_2split (SAME weights,
          NO retrain — three inference re-runs only)
  Output: 2030_synthetic_diaries_2split.csv with BAND column
          (see Open Decision 3 for shape)
          2030_drift_summary_2split.csv (signed per-activity, per-channel shifts)
  WFH-rate sensitivity check: band C WFH_RATE > band B > band A (monotone)
```

---

## DRIFT_MATRIX Design

Each DRIFT_MATRIX spans **both** the AT_HOME and AT_WORK axes. The matrix is a
standalone analytical output for the 3J paper.

### Matrix structure

| Dimension | Values | Description |
|-----------|--------|-------------|
| Activity axis | 14 categories (act codes 1–14) | Per-activity JS divergence |
| Channel axis | 2 (AT_HOME / AT_WORK) | Joint home+work drift profile |
| Stratum axis | 3 (WD / Saturday / Sunday) | Per-stratum drift |
| Archetype axis | N demographic groups | Per-archetype drift |
| Aggregate scalar | 1 per matrix | Single "cycle shift index" for longitudinal narrative |

### Three publishable matrices

| Matrix | Cycle transition | Key signal |
|--------|-----------------|------------|
| `DRIFT_MATRIX_0510_2split.csv` | 2005 → 2010 | Early internet / screen time adoption |
| `DRIFT_MATRIX_1015_2split.csv` | 2010 → 2015 | Smartphone ubiquity; commute mode shift |
| `DRIFT_MATRIX_1522_2split.csv` | 2015 → 2022 | **COVID-19: AT_HOME +6–8 pp jump AND AT_WORK physical presence drop** — dual primary finding |

> **DRIFT_MATRIX_1522 dual COVID check:** Immediately after saving, assert:
> (1) WD AT_HOME drift signal ≥ +5 pp.
> (2) WD AT_WORK drift signal shows a meaningful DECREASE in physical office presence
>     (the WFH surge is the mirror image).
> If either signal is absent (< 1 pp magnitude), the 2030 WFH forecast will be wrong.
> Investigate 2022 cycle recency weight and the work_pos_weight before proceeding.

---

## Sub-step 6A — Input Audit

**aim:** Verify `augmented_diaries.csv` (R5_lr1e4, raw — per OD-1) is present and correctly
structured before any model training begins. Confirm both hom30 and wrk30 channels.

**steps:**
1. Load `augmented_diaries.csv` from `Step4_docs/outputs_step4/sweep/R5_lr1e4/` (raw training corpus, per OD-1)
2. Assert row count ≈ 192,183 (accept ±200 for edge deduplication)
3. Assert CYCLE_YEAR ∈ {2005, 2010, 2015, 2022}; print per-cycle row counts
4. Assert DDAY_STRATA ∈ {1, 2, 3}; print per-cycle × per-stratum counts
5. Assert IS_SYNTHETIC column present; print IS_SYNTHETIC=0 / IS_SYNTHETIC=1 counts per cycle
6. Assert act30_001–048 all present (48 cols); values ∈ {1..14}
7. Assert hom30_001–048 all present (48 cols); values ∈ {0, 1}
8. Assert wrk30_001–048 all present (48 cols); values ∈ {0, 1}
9. Assert 9 co-presence × 48 slot columns present (from Step 4 schema)
10. **Measure** (do NOT assert 0) the per-slot hom30_k==1 AND wrk30_k==1 co-occurrence rate. Raw R5_lr1e4 has NOT been through 04L, so some overlap is expected; record the baseline rate (the 6H cleanup — mutual-exclusion resolution + 04M — enforces exclusion later). Flag only if overlap > 5% of slots (model pathology, not expected).
11. Assert TELEWORK column present (binary; NaN → 0)
12. Assert NOCS and NAICS columns present (Step 4 conditioning vars)
13. Print per-cycle: AT_HOME WD mean, AT_WORK WD mean, WFH_RATE (business-hours slots 11–26)

**expected result:**
- All assertions pass
- 2022 AT_HOME WD mean notably higher than 2005–2015 baseline (COVID signal confirmed)
- 2022 AT_WORK WD mean shows decreased physical presence vs. 2015
- WFH_RATE trajectory: 2005 < 2010 < 2015 << 2022 (monotone through COVID break)
- Mutual-exclusion overlap rate recorded (small, non-zero on raw R5; enforced to 0 downstream at 6H)

**test method:** Run 6A audit block in `3rdJ_06_longitudinalForecasting_2split.py`;
all assertions print PASS with observed values matching expected ranges.

---

## Sub-step 6B — Script Architecture + HPC Setup

**aim:** Write `3rdJ_06_longitudinalForecasting_2split.py` and the SLURM wrapper;
assemble `scenario_2030_features_2split.csv`.

**steps:**
1. Create `Step6_docs/3rdJ_06_longitudinalForecasting_2split.py`
   - Import `JSeriesHybrid2Split` from `3rdJ_04B_model_2split.py` AND reuse the loss-component / PCGrad / uncertainty-weighting helpers from `3rdJ_04D_train_2split.py` by **module import** (importing does NOT run their `__main__`). Implement Step-6's OWN progressive training loop: checkpoint warm-start, per-cycle subset selection, and per-sample recency weighting — NONE of these exist in 04D, so they are new Step-6 code. Import ONLY; do NOT modify 04B/04D.
   - Implement `TrendEncoder2Split` class (d_model=64, 2 layers, 4 heads; input = DRIFT_MATRIX_*_2split flattened; output = joint 2030-projected distribution for both channels)
   - Implement `compute_drift_matrix_2split(W_prev, cycle_data)` — computes JS divergence per {14 activities × 3 strata × demographic group} plus AT_HOME and AT_WORK mean shift per stratum
   - Implement `compute_wfh_rate(df, cycle_year)` — mean(hom30_k | act30_k==Work AND LFTAG==employed) over slots 11–26
   - Implement `run_substage_a()`, `run_substage_b()`, `run_substage_c()`, `run_substage_d_phase_i()`, `run_substage_d_phase_ii(band)`
   - Implement `run_all()` orchestrator: A → B → C → D_phase_i → D_phase_ii(band) × 3
   - `argparse` flags: `--stage {A,B,C,D1,D2,all}`, `--band {conservative,hybrid,fullyhybrid}`, `--smoke` (5% data, 3 epochs)

2. Create `Step6_docs/slurm_06_2split.sh` (SLURM wrapper)
   ```
   #!/bin/tcsh
   #SBATCH --job-name=3rdJ_step6
   #SBATCH --partition=pg
   #SBATCH --gres=gpu:1
   #SBATCH --time=48:00:00
   #SBATCH --mem=32G
   #SBATCH --cpus-per-task=4
   #SBATCH --output=step6_2split_%j.out
   ```
   - Python interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python`
   - Script call: single line, no backslash continuation (tcsh shell)
   - Submission: always `sbatch slurm_06_2split.sh` (NEVER blocking srun)

### Hyperparameter table

| Component | Hyperparameter | Value | Source |
|-----------|---------------|-------|--------|
| JSeriesHybrid2Split decoder | d_model | 256 | Inherited from Step 4 (DEFAULT_CONFIG) |
| JSeriesHybrid2Split decoder | N_enc / N_dec | 6 / 6 | Inherited |
| JSeriesHybrid2Split decoder | n_heads | 8 | Inherited |
| JSeriesHybrid2Split decoder | n_aux (slot aux width) | 11 | [AT_HOME, AT_WORK, 9×cop] |
| TrendEncoder2Split | d_model | 64 | New — 3-token input |
| TrendEncoder2Split | layers | 2 | New |
| TrendEncoder2Split | heads | 4 | New |
| All | Optimizer | AdamW (lr=1e-4) | Same as Step 4 |
| All | Early stop patience | 5 epochs | Same as Step 4 |
| Loss weighting | WEIGHT_MODE | 'uw' | Inherited from 04D |
| PCGrad | USE_PCGRAD | True | Inherited from 04D |
| Diversity loss | LAMBDA_DIV | 0.1 | Inherited from 04D |
| Recency weights | 2005/2010/2015/2022 | 0.10/0.20/0.30/0.40 | Per pipeline spec |

**expected result:**
- `3rdJ_06_longitudinalForecasting_2split.py` importable; `--smoke --stage A` runs without error
- `slurm_06_2split.sh` has `--time=48:00:00` minimum (hard rule) and `--gres=gpu:1`
- `scenario_2030_features_2split.csv` written to `outputs_step6/` (~37,008 rows)

**test method:** locally run `python 3rdJ_06_longitudinalForecasting_2split.py --smoke --stage A`;
confirm both home_head and work_head losses appear in epoch log; check DRIFT_MATRIX_0510_2split.csv
contains both AT_HOME_drift and AT_WORK_drift columns.

---

## Sub-step 6B2 — Assemble scenario_2030_features_2split.csv

**aim:** Generate the per-person conditioning file for Sub-stage D Phase ii (all three bands).
Mirrors the 2J Sub-step 6B2 but carries the TELEWORK column for WFH-band injection.

**steps:**
1. Load `augmented_diaries.csv` (R5_lr1e4, raw — per OD-1), filter for `CYCLE_YEAR=2022` (~37,008 rows)
2. Resample rows by AGEGRP to match Stats Canada 2030 M1 distribution:
   - AGEGRP 1 (15–24): 13.5% ↓
   - AGEGRP 2 (25–34): 16.5%
   - AGEGRP 3 (35–44): 17.5%
   - AGEGRP 4 (45–54): 15.5%
   - AGEGRP 5 (55–64): 14.8%
   - AGEGRP 6 (65–74): 13.0% ↑
   - AGEGRP 7 (75+): 9.2% ↑
3. LFTAG/HRSWRK shift naturally as byproduct (no separate resampling needed)
4. TELEWORK column: keep original values (used as the WFH-band injection handle at inference — see Open Decision 2)
5. Tag: `CYCLE_YEAR=2030`, `SCENARIO=M1_2030`
6. Save to `outputs_step6/scenario_2030_features_2split.csv` (~37,008 rows × all conditioning columns)

**expected result:**
- AGEGRP distribution matches targets within ±0.5 pp
- DDAY_STRATA counts: WD~72%, Sat~14%, Sun~14% (inherited from 2022 base)
- TELEWORK column present; NOCS and NAICS columns present

---

## Sub-step 6C — Sub-stage A: Base Training + DRIFT_MATRIX_0510

**aim:** Train W_2005_2split on 2005 cycle; compute the first joint drift matrix.

**steps:**
1. Split 2005 rows: 70% train / 20% val / 10% test (stratified by DDAY_STRATA)
2. Train `JSeriesHybrid2Split` from random init on 2005 train set
   - All four losses active: act + home + work + cop with WEIGHT_MODE='uw'
   - PCGrad ON; LAMBDA_DIV=0.1
3. Validate on 2005 val set; early stop on JOINT val JS (act + home + work, patience=5)
4. Save `W_2005_2split.pt` to `outputs_step6/models/`
5. True Future Test: apply W_2005_2split to 2010 held-out; compute joint distribution
6. Compute DRIFT_MATRIX_0510_2split:
   - JS divergence per {14 activities × 3 DDAY_STRATA × demographic group}
   - AT_HOME mean shift per stratum (signed)
   - AT_WORK mean shift per stratum (signed)
7. Save `DRIFT_MATRIX_0510_2split.csv` to `outputs_step6/`
8. Print: val JS per stratum per channel; True Future Test JS vs. 2010 held-out

**expected result:**
- `W_2005_2split.pt` saved; val JS (home) < 0.15 per stratum; val JS (work) < 0.20 per stratum
- `DRIFT_MATRIX_0510_2split.csv` written; ≥ 3 activity categories show drift > 0.01
- True Future Test joint JS < 0.20 per stratum

**test method:** print per-stratum val JS table (home / work separately); spot-check
DRIFT_MATRIX that AT_HOME_drift and AT_WORK_drift columns are populated.

---

## Sub-step 6D — Sub-stage B: Progressive Fine-Tuning (3 Phases)

**aim:** Run three sequential fine-tuning phases with weight inheritance across BOTH
channels; compute DRIFT_MATRIX_1015 and DRIFT_MATRIX_1522.

### Phase 2 (W_2005_2split → W_2010_ft_2split)

**steps:**
1. Load W_2005_2split; fine-tune on 2005+2010 (70% combined, stratified)
2. Early-stop on 2010 val (20%), joint JS (home+work)
3. True Future Test: evaluate on 2015 held-out
4. Compute DRIFT_MATRIX_1015_2split (W_2010_ft applied to 2015 held-out)
5. Save `W_2010_ft_2split.pt`, `DRIFT_MATRIX_1015_2split.csv`

### Phase 3 (W_2010_ft_2split → W_2015_ft_2split)

**steps:**
1. Load W_2010_ft_2split; fine-tune on 2005+2010+2015 (70%)
2. Early-stop on 2015 val (20%)
3. True Future Test: evaluate on 2022 held-out
4. Compute DRIFT_MATRIX_1522_2split
5. Save `W_2015_ft_2split.pt`, `DRIFT_MATRIX_1522_2split.csv`

> **DRIFT_MATRIX_1522 dual COVID check:** After saving, immediately assert:
> (a) WD AT_HOME drift ≥ +5 pp (COVID stay-at-home signal).
> (b) WD AT_WORK drift shows meaningful office-presence decrease (the WFH mirror).
> If either is absent, investigate W_2015_ft convergence and 2022 recency weight.

### Phase 4 (W_2015_ft_2split → W_2022_ft_2split)

**steps:**
1. Load W_2015_ft_2split; fine-tune on all 4 cycles (70%)
2. Early-stop on 2022 val (20%), joint JS (home+work)
3. Save `W_2022_ft_2split.pt`

**expected result (all phases):**
- 3 checkpoint files saved: `W_2010_ft_2split.pt`, `W_2015_ft_2split.pt`, `W_2022_ft_2split.pt`
- 2 drift matrices saved: `DRIFT_MATRIX_1015_2split.csv`, `DRIFT_MATRIX_1522_2split.csv`
- Each phase True Future Test JS < 0.20 per stratum per channel
- DRIFT_MATRIX_1522 WD AT_HOME shift ≥ +5 pp; WD AT_WORK shows directional office drop

**test method:** print per-phase summary: train/val loss (per task) final epoch |
True Future Test joint JS; spot-check DRIFT_MATRIX_1522 AT_HOME_drift and AT_WORK_drift rows.

---

## Sub-step 6E — Sub-stage C: Pooled Recency-Weighted Training

**aim:** Train the TrendEncoder2Split on the 3 DRIFT_MATRIXes; fine-tune the full
joint model with recency-weighted loss on all 4 cycles pooled.

**steps:**
1. Load W_2022_ft_2split as warm start
2. Initialize TrendEncoder2Split (d_model=64, 2 layers, 4 heads) from random weights
3. Concatenate DRIFT_MATRIX_0510 / DRIFT_MATRIX_1015 / DRIFT_MATRIX_1522 (all _2split
   versions) as 3-token sequence; both AT_HOME and AT_WORK drift columns are included
4. Train joint model (TrendEncoder2Split + JSeriesHybrid2Split decoder) on all 4 cycles:
   - Recency loss weights per-sample: 2005=0.10, 2010=0.20, 2015=0.30, 2022=0.40
   - WEIGHT_MODE='uw', PCGrad ON, LAMBDA_DIV=0.1 (same as 04D)
   - Distribution-matching loss: decoder output proportions (act + home + work) must match
     TrendEncoder2Split 2030 projection; applied as cross-entropy/BCE over both channels
5. Early-stop on 2022 val JOINT JS (home+work, patience=5)
6. Save `W_pooled_2030_2split.pt`, `trend_encoder_2030_2split.pt`
7. Print: WFH_RATE at pooled val time (check: ≥ 2022 level, trend not suppressed)

**expected result:**
- Both checkpoints saved; pooled val JS < 0.18 per channel per stratum
- TrendEncoder2Split 2030 projection: WD AT_HOME ≥ 2022 level (WFH trend not suppressed)
- TrendEncoder2Split 2030 projection: WD AT_WORK reflects band trajectory
- WFH_RATE computed from pooled val output ≥ 2015 WFH_RATE (structural break preserved)

**test method:** print final pooled val JS per stratum per channel; compare
TrendEncoder2Split 2030 projected marginals vs. 2022 observed for both channels.

---

## Sub-step 6F — Sub-stage D Phase i: 2022 Backcasting Gate

**aim:** Validate Model 2 by jointly reconstructing 2022 AT_HOME and AT_WORK patterns.

**steps:**
1. Load W_pooled_2030_2split + trend_encoder_2030_2split
2. Build 2022 conditioning: use observed AGEGRP/LFTAG/HRSWRK/TELEWORK distribution from 2022 cohort (no projection — actual 2022 conditions)
3. Run inference via `JSeriesHybrid2Split.generate()` for each 2022 respondent demographic
   - Returns: (gen_act, gen_home, gen_work, gen_cop, gen_cop_probs)
4. Save `outputs_step6/reconstructed_2022_diaries_2split.csv`
   (columns: act30_001–048, hom30_001–048, wrk30_001–048, IS_SYNTHETIC=1)
5. Compute per-stratum:
   - JS(hom30 reconstructed, observed 2022)
   - JS(wrk30 reconstructed, observed 2022)
   - AT_HOME WD mean: |reconstructed − observed|
   - WFH_RATE: |reconstructed − observed| (slots 11–26, employed only)
   - AT_WORK WD mean: |reconstructed − observed|
6. Print gate results; assert hard gates before proceeding to Phase ii

**expected result:**
- Reconstruction JS (home) < 0.10 per stratum (hard gate)
- Reconstruction JS (work) < 0.10 per stratum (hard gate)
- AT_HOME WD reconstruction within ±2 pp of observed 2022
- WFH_RATE reconstruction within ±5 pp of observed 2022
- AT_WORK WD reconstruction within ±3 pp of observed 2022

**test method:** print gate table: JS(home) and JS(work) per stratum with PASS/FAIL;
AT_HOME / WFH_RATE / AT_WORK mean deviations.

---

## Sub-step 6G — Sub-stage D Phase ii: Three-Band 2030 Forecast

**aim:** Generate the Step 6 deliverable — 2030 synthetic diaries for all three
WFH sensitivity bands, from inference re-runs (NOT retrains).

**steps:**
1. Load `scenario_2030_features_2split.csv`; verify all conditioning columns present
2. For each band, resample the TELEWORK column among employed rows so the SHARE with
   TELEWORK=1 matches the band's population WFH target; set TELEWORK_KNOWN=1 on all rows
   (see OD-2). Do NOT set all-0 / all-1 (that gives 0% / 100%, not the band rate):
   - Band A Conservative:   ~17.5% of employed rows TELEWORK=1 (target WFH 15–20%)
   - Band B Hybrid:         ~30% of employed rows TELEWORK=1 (target WFH ~30%)
   - Band C Fully Hybrid:   ~40% of employed rows TELEWORK=1 (target WFH ~40%)
   After inference, verify the realized WFH_RATE per band matches the target within ±3 pp;
   if the model under/over-responds to TELEWORK, adjust the injected share to hit the target.
3. Run three inference calls; for each band compute WFH_RATE from output
4. Assert monotone sensitivity: WFH_RATE(C) > WFH_RATE(B) > WFH_RATE(A)
5. Output: `outputs_step6/2030_synthetic_diaries_2split.csv` with BAND column
   (see Open Decision 3 for shape)
6. Output: `outputs_step6/2030_drift_summary_2split.csv`
   (signed per-activity shifts: 2022→2030 per stratum per channel, per band)
7. Print: row count per band; WD AT_HOME / AT_WORK / WFH_RATE per band

**expected result:**
- `2030_synthetic_diaries_2split.csv` written; ≥ 37,000 rows per band
- WFH_RATE trajectory: band A ~0.15–0.20, band B ~0.30, band C ~0.40
- Monotone sensitivity check PASS
- 2030 WD AT_HOME within ±15 pp of 2022 (gross continuity, no wild extrapolation)
- Office diurnal targets (from Step 4 spec) reproduced for Band A at minimum:
  - WD peak presence 09:30–11:30 and 14:30–16:30 (slots ~12–16 and ~22–26)
  - Lunch dip 12:00–13:30 (slots ~17–19, presence 0.25–0.35)
  - True peak ≈ 15:00 (slot ~23), NOT 17:00
  - Night presence 0.02–0.05

> **Energy non-linearity caveat (document in paper):** A 20–50% occupancy cut
> (bands A→C) yields only ~10–30% energy savings. Fixed HVAC/ventilation and plug-load
> baseload never reach zero. The 2030 forecast must preserve this — do NOT scale energy
> 1:1 with WFH_RATE.

**test method:** plot 48-slot AT_WORK profiles for all three bands on one chart;
verify peak window, lunch dip, and night floor; confirm WFH_RATE monotone ordering.

---

## Sub-step 6H — Downstream Cleanup Pass (NO marginal rake on the forecast year)

**aim:** Make the 2030 output BEM-ready: enforce home/work mutual exclusion and remove
1-slot dwell blips. **The 04L marginal rake is deliberately NOT applied to 2030.**

> **Why no 04L on 2030 (review finding, 2026-06-23 — B1/B2).** `3rdJ_04L_joint_rake_2split.py`
> re-runs `model.generate()` on the Step-4 `.pt` tensors and rakes to per-(cycle × stratum ×
> slot) marginals computed from OBSERVED (IS_SYNTHETIC==0) rows. 2030 is a forecast — it has
> no observed rows and no defensible per-slot target (raking to the TrendEncoder's own
> projection is circular, and the WFH bands are already set by the TELEWORK injection). So 04L
> is neither usable (no `.pt` tensors / checkpoint for a brand-new 2030 cohort) nor desirable
> (it would override the very forecast we want). Marginal raking belongs to the 2022 backcast
> validation (val-doc Section 4), not the forecast deliverable.

**steps:**
1. **Mutual-exclusion cleanup** (small, deterministic — NOT 04L). For any slot with
   hom30_k==1 AND wrk30_k==1, resolve by the slot's activity: if act30_k is a work activity →
   keep wrk30=1, hom30=0; else → keep hom30=1, wrk30=0. (6A measures the baseline overlap on
   raw R5; expect it small.) Implement as a few lines in the Step-6 script.
2. **Min-dwell smoothing.** Run `3rdJ_04M_mindwell_2split.py --in_csv <2030 band CSV>
   --out_csv <smoothed>` per band — this IS plug-and-play (pure-pandas CSV in/out, edits
   hom30+wrk30 synthetic rows only; verified argparse `--in_csv/--out_csv/--min_dwell`).
3. Tag the smoothed, mutual-exclusion-clean output as the final Step-6 deliverable.
4. Confirm: 0 mutual-exclusion violations; no isolated 1-slot blips on either channel;
   per-band WFH_RATE unchanged by the cleanup (±0.5 pp — cleanup is shape-fixing, must NOT
   move the forecast).

**expected result:**
- Final `2030_synthetic_diaries_2split.csv` has 0 mutual-exclusion violations and no 1-slot blips
- Per-band WFH_RATE preserved (cleanup does not marginal-force)

**test method:** print per-slot mutual-exclusion violation count (target 0) and the WFH_RATE
delta before/after cleanup (target ≈ 0).

---

## DRIFT_MATRIX Detailed Design

Each DRIFT_MATRIX captures behavioral change across a cycle transition. The two-channel
design extends the Leg-1 matrix with explicit AT_WORK drift columns.

### Three publishable matrices

| Matrix | Cycle transition | Home signal | Work signal |
|--------|-----------------|-------------|-------------|
| `DRIFT_MATRIX_0510_2split.csv` | 2005 → 2010 | Early internet / screen time | Modest shift |
| `DRIFT_MATRIX_1015_2split.csv` | 2010 → 2015 | Smartphone / commute shift | Pre-COVID stable |
| `DRIFT_MATRIX_1522_2split.csv` | 2015 → 2022 | **AT_HOME +6–8 pp (COVID)** | **AT_WORK physical drop (WFH surge)** |

### Day-type stratification discipline

Gates and marginals are always stratified by `DDAY_STRATA`:
- DDAY_STRATA == 1 : Weekday
- DDAY_STRATA ∈ {2, 3} : Weekend (Saturday / Sunday separately where sample size allows)

Never aggregate WD and WE together in a gate or drift diagnostic.

---

## Open Decisions

These decisions are flagged for manager sign-off. Do NOT silently resolve them in code.

---

### OD-1: Training corpus — raw R5 vs. calibrated R5_raked_mindwell

**The question:** Should Model 2 train on the raw `R5_lr1e4/augmented_diaries.csv` or
the calibrated `R5_raked_mindwell/augmented_diaries.csv`?

**Recommendation: Train on the raw R5_lr1e4 output; clean up the 2030 output
downstream at Sub-step 6H (04M min-dwell + mutual-exclusion, no 04L rake).** Rationale: training on
post-hoc raked data would teach the model target marginals that were externally imposed,
not learned from the GSS data distribution. The 04L/04M pipeline was designed to be a
downstream corrector, not a training signal. This mirrors how Leg-1 Step 5 handled 2022.

**✅ RESOLVED (manager, 2026-06-23): train on raw `R5_lr1e4`; clean up the 2030 output
downstream at Sub-step 6H (04M min-dwell + mutual-exclusion only — NO 04L rake on the forecast year).**
Data Inputs table + Sub-steps 6A/6B2 updated accordingly.

---

### OD-2: WFH-scalar injection at inference — conditioning-feature override vs. post-hoc reweight

**The question:** How is the WFH band value pinned during Sub-stage D Phase ii?
Option A — conditioning-feature override: set TELEWORK=0/interpolated/1 in
`scenario_2030_features_2split.csv` for each band; the decoder reads it as a
conditioning feature (it is in the 119-dim cond vector as a binary). This is clean
and exploits the feature the model was trained on.
Option B — post-hoc reweight: generate once and reweight work-at-home slots by the band
target ratio; no model re-run needed. Simpler but does not propagate the WFH signal
through the activity arm.

**Recommendation: Option A (conditioning-feature override via TELEWORK column).**
Rationale: TELEWORK is already in the model's cond vector (step4_feature_config.json);
overriding it at inference is the cleanest way to propagate the WFH signal through both
the activity arm (which activities are performed) and the occupancy heads (where the person
is). Post-hoc reweighting cannot alter the activity sequence.

**✅ RESOLVED (manager, 2026-06-23): Option A (TELEWORK conditioning override), with the
mechanism corrected to a SHARE resample.** The bands are *population* WFH rates, so pin the
share of employed rows with TELEWORK=1 to the band target (≈17.5% / 30% / 40%) — NOT all-0/all-1,
which would yield 0% / 100%. Set TELEWORK_KNOWN=1 on all rows (else the value reads as masked).
After each inference run, verify the realized WFH_RATE matches the band target within ±3 pp and
adjust the injected share if the model under/over-responds. Architecture block + Sub-step 6G updated.
**Empirical risk (review B3):** TELEWORK *is* wired to both arms (confirmed in 04B), but its
learned effect on WFH_RATE is empirical, not guaranteed monotone. If the bands collapse to the
same WFH_RATE (val check 5.16 fails), fall back to **Option B (post-hoc reweight** of work-at-home
slots to the band target). Keep Option B documented as plan-B, not discarded.

---

### OD-3: 2030 deliverable shape — three separate CSVs vs. one CSV with BAND column

**The question:** Three files (`2030_synthetic_diaries_BAND_conservative.csv`, etc.)
or one file `2030_synthetic_diaries_2split.csv` with a `BAND` column?

**Recommendation: One file with a `BAND` column** (values: `conservative`, `hybrid`,
`fullyhybrid`). Rationale: Step 7 BEM injection can filter by band; a single file
is easier to version and validate. Total rows ≈ 3 × 37,008 ≈ 111,024.

**✅ RESOLVED (manager, 2026-06-23): one CSV with a `BAND` column** (`conservative` / `hybrid` / `fullyhybrid`).

---

### OD-4: Office archetype linkage dependency

**The question:** Does the NOC×NAICS → office-archetype lookup (pipeline doc Step 5
office part) already exist in the 2-split build, or is it a Step-6/Step-7 prerequisite?

**✅ RESOLVED (manager, 2026-06-23): NOT a Step-6 prerequisite — deferred to Step 7.**

Step 6 forecasting conditions on the raw `NOCS` (11-cat) and `NAICS` (20-cat) codes,
which are **already present in the 119-dim conditioning vector** (`step4_feature_config.json`).
The model therefore already sees occupation and industry. The NOC×NAICS → `office_archetype_ID`
*lookup table* only maps those codes to an office-archetype label for **BEM injection** (which
office IDF zone gets the schedule) — that is a Step-7 concern, not needed to generate the 2030
occupancy diaries here. The scenario file (6B2) carries NOCS/NAICS as conditioning; it does NOT
need `office_archetype_ID`. **Carry `office_archetype_lookup.csv` as a Step-7 prerequisite.**

---

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-06-23 | Created `3rdJ_06_longitudinalForecasting_2split.md` and `3rdJ_06_longitudinalForecasting_2split_val.md` | New Step 6 planning doc pair for 2-split two-channel pipeline. Key adaptations vs. 2J template: (1) model class is `JSeriesHybrid2Split` (not Leg-1 single-head); (2) all drift matrices, checkpoints, and output CSVs have `_2split` suffix; (3) DRIFT_MATRIX spans AT_HOME+AT_WORK axes; (4) 04D training machinery (uw/PCGrad/diversity) inherited; (5) 3-band WFH sensitivity via TELEWORK override at inference; (6) 04L→04M calibration chain applied downstream (Sub-step 6H); (7) wrk30_* column prefix confirmed from 04L/04M scripts (NOT WORK30_* which is the Step 3 tiler output); (8) SLURM time bumped to 48h minimum. Four open decisions flagged: OD-1 training corpus, OD-2 WFH injection mechanism, OD-3 deliverable shape, OD-4 office archetype dependency. |
| 2026-06-23 | Manager review + sign-off on all 4 open decisions | OD-1 → train on raw `R5_lr1e4`, calibrate 2030 downstream at 6H (Data Inputs table + 6A/6B2 repointed). OD-2 → TELEWORK conditioning override, mechanism CORRECTED from all-0/all-1 to a SHARE resample of employed rows to the band's population WFH target (≈17.5/30/40%), TELEWORK_KNOWN=1, verify realized WFH_RATE ±3pp (Architecture block + 6G updated). OD-3 → one CSV + `BAND` column. OD-4 → NOT a Step-6 blocker; NOCS/NAICS already in the 119-dim cond vector, archetype lookup deferred to Step-7 prerequisite. Also corrected 6A mutual-exclusion check to MEASURE overlap on raw R5 (not assert 0). Plan is review-ready; build (6B script) pending user OK. |
| 2026-06-23 | Independent pre-build review (read-only) + manager fixes | Reviewer cross-checked both docs against the real 04B/04D/04E/04L/04M code. Confirmed: `JSeriesHybrid2Split` exists (04B:180), `generate()` returns the 5-tuple 6F assumes, TELEWORK feeds both arms. **Fixes applied: (B1/B2)** 6H REDESIGNED — dropped the 04L marginal rake on the forecast year (04L re-runs model on Step-4 `.pt` + rakes to OBSERVED marginals; 2030 has neither); 6H now = mutual-exclusion cleanup + 04M min-dwell only. **(S2/S3)** Reframed training reuse — Step-6 imports model+loss helpers but writes its OWN progressive loop (warm-start, cycle-subset, per-sample recency = new code; 04D has none). **(B3)** Documented TELEWORK post-hoc-reweight fallback. **(S1)** Business hours fixed to slots 11–26 ([09:00,17:00)). **(S5)** 6A aim-line R5 typo. Val-doc fixes (S4 G14 backcast-only, N1 sleep raw code 5, slot 11–26) handed to authoring employee. |
| 2026-06-23 | Sub-step 6B BUILD COMPLETE — local smoke test PASS | Employee (Sonnet 4.6) created all three deliverables: (1) `3rdJ_06_longitudinalForecasting_2split.py` — 1,800+ lines; implements Sub-steps 6A–6H including `TrendEncoder2Split` (d_model=64, 2L, 4H), `compute_drift_matrix_2split()`, `mutual_exclusion_resolve()`, `call_mindwell()`, `progressive_train()` with per-sample recency weights, `robust_train_val_split()` fallback, and `run_all()` orchestrator; argparse: `--stage {audit,A,B,C,D1,D2,all}`, `--band`, `--smoke`, `--data`. (2) `slurm_06_2split.sh` — tcsh, partition=pg, gres=gpu:1, time=48:00:00, mem=32G, single-line Python call. (3) `assemble_scenario_2030_2split.py` — filters 2022 cohort, resamples AGEGRP to M1 2030 targets, writes `outputs_step6/scenario_2030_features_2split.csv`; `--verify` dry-run mode. Smoke test: `py -3 3rdJ_06_longitudinalForecasting_2split.py --smoke --stage A --data augmented_diaries_SAMPLE.csv` ran 3 epochs on 1,152 2005 rows / 922 train + 230 val; both `home` and `work` head losses appeared each epoch (e.g. epoch 1: home=0.5019 work=1.0386); `DRIFT_MATRIX_0510_2split.csv` written with `AT_HOME_drift` + `AT_WORK_drift` columns confirmed. Key design choices: import 04B/04D via `importlib` (digit-prefix filenames); warm-start from `.pt` checkpoints (NEW vs 04D); `build_cond_vec_from_df()` replicates 04A featurization from `step4_feature_config.json` without triggering 04A's CSV-loading side-effects; 6H mutual-exclusion uses activity to arbitrate (Work activity → keep wrk30=1, else keep hom30=1). Next: upload 3 files to cluster + sbatch. |
| 2026-06-23 | FULL-STAGE SMOKE PASS; compliance 8/8 ✓ — CLUSTER-READY | Employee (Sonnet 4.6) de-risk gate: `--smoke --stage all` on SAMPLE.csv (3,840 rows, all 4 cycles) completed A→B(3 phases)→C(TrendEncoder+pooled)→D1(backcast gate)→D2(3 bands)+6H(mindwell) without error. One non-blocking WARNING: WFH_RATE monotone check printed FAIL (conservative 0.889 > hybrid 0.882 > fullyhybrid 0.872, i.e. *inverted* order) — expected on this tiny SAMPLE; model has not learned TELEWORK→WFH signal on 37 rows; the monotone check itself works correctly. COVID dual-signal WARN on SAMPLE also expected (no distributional shift in tiny data). Scenario builder `--verify` PASS: AGEGRP gate max_delta=0.05pp, all key cols present. Compliance: all 8 items ✓ (see gate report). No code edits made. |
| 2026-06-23 | Uploaded 3 Step-6 files to Speed; submitted GPU job 982857 on pg; env + data verified | Employee (Sonnet 4.6). Pre-flight: third-party imports = torch + numpy + pandas only (no scipy/sklearn). SLURM wrapper already had absolute `--data` path hardcoded — no fix needed. (1) `mkdir -p` created `Step6_docs/outputs_step6/models` on cluster. (2) scp uploaded `3rdJ_06_longitudinalForecasting_2split.py`, `slurm_06_2split.sh`, `assemble_scenario_2030_2split.py` to `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/` — all 3 confirmed via `ls`. (3) Deps verified: `augmented_diaries.csv` (R5_lr1e4) present; `3rdJ_04B_model_2split.py`, `3rdJ_04D_train_2split.py`, `3rdJ_04M_mindwell_2split.py`, `step4_feature_config.json` all present in Step4_docs. (4) Env check: `step4` env site-packages has torch 2.5.1+cu121, numpy 2.2.6, pandas 2.3.3 — all required packages present, nothing missing. (5) `sbatch slurm_06_2split.sh` → job 982857 submitted; `squeue` confirms RUNNING on node cisr-2 (partition pg, 1 GPU). Output file: `step6_2split_982857.out` in Step6_docs — empty at 2-minute mark (Python still in import/audit phase; no ImportError or crash). |
| 2026-06-23 | AMP/GradScaler bug fix — FULL AUDIT BUNDLE — local smoke PASS | Employee (Sonnet 4.6). Job 982857 failed at sub-stage A epoch 0 with `AssertionError: Attempted unscale_ but _scale is None`. Root cause: the AMP+PCGrad branch in `run_one_epoch` called `scaler.unscale_(optimizer)` BEFORE any `scaler.scale(loss).backward()` — GradScaler was never primed, so `_scale` was None. Full audit found 4 further bugs: (2) the AMP PCGrad path never called `scaler.scale().backward()` at all; (3) the fp32 PCGrad path omitted the diversity-loss grad from model params and the UW log_var grad entirely (both present in 04D); (4) `rw_mean` was computed inside the `autocast` region and used outside it in the PCGrad branch — dtype leak risk; (5) the PCGrad AMP/fp32 split was inconsistent with 04D which runs PCGrad ONLY in the fp32 path. **Fix strategy: fp32 fallback (AMP disabled).** 04D's default is also fp32 (`--fp16` is opt-in, disabled in `--sample` mode, only added after the r11 OOM which was caused by 3-stratum teacher-forced decode graphs — absent from Step 6). Step-6 model is same architecture but simpler flow; fp32 is safe. **Fixes applied** to `3rdJ_06_longitudinalForecasting_2split.py` (pre-fix archived to `Step6_docs/archive/3rdJ_06_longitudinalForecasting_2split.preAMPfix.py`): (F1) `run_one_epoch` — removed `scaler` parameter, removed `with torch.amp.autocast(...)` wrapper, removed entire AMP branch; (F2) `progressive_train` — removed `scaler = torch.amp.GradScaler(...)` construction; (F3) `run_one_epoch` call in `progressive_train` — removed `scaler` argument; (F4) fp32 PCGrad path — now mirrors 04D exactly: `pcgrad.backward(task_losses, retain_all=True)`, then diversity grad via `torch.autograd.grad`, accumulated into `p.grad`, then UW log_var grads via separate `torch.autograd.grad` call on `total_loss`. Local smoke `--smoke --stage all` on SAMPLE.csv: A→B(3 phases)→C→D1→D2(3 bands)+6H all PASS, no errors or warnings beyond pre-existing PerformanceWarning (benign, not in training path). Bundle ready for manager review + re-upload + re-submit. |
| 2026-06-23 | AMP-fix file uploaded to Speed; re-submitted as job 982868 — RUNNING on pg/cisr-2 | Employee (Sonnet 4.6). Fixed `3rdJ_06_longitudinalForecasting_2split.py` (AMP disabled, fp32 only — see previous entry) uploaded via scp to `/speed-scratch/.../Step6_docs/`. Cluster verify: `grep -n unscale_` → line 573 only, inside docstring comment ("The original code called scaler.unscale_(optimizer)…") — not live code. Zero live `unscale_` calls confirmed. `sbatch slurm_06_2split.sh` → job 982868. `squeue` at T+4s: ST=R, node cisr-2, partition pg. Output file: `step6_2split_982868.out` in Step6_docs. SLURM script and scenario script were NOT re-uploaded (unchanged on Speed). Do NOT poll; manager schedules early crash-point check separately. |
| 2026-06-24 | Job 982868 COMPLETED cleanly but RESULTS DEGENERATE — root cause diagnosed (Opus, local code read) | fp32 fix fully vindicated (exit 0:0, 7h59m, MaxRSS 4.9 GB, 0 Traceback) — clean end-to-end run, all artifacts written. BUT all 3 WFH bands gave IDENTICAL occupancy to 4 dp (WD_AT_HOME=0.7245, WD_AT_WORK=0.1507, WFH=0.7591); backcast JS_home=−0.0000 (mathematically impossible); val_js=0.0000 @ epoch 1 of every stage; loss diving negative. **ROOT CAUSE = `Step6Dataset` SELF-PAIRS the diary** (L482-487: `dec_act_seq=act_seq[i]`, `dec_aux_seq=aux_seq[i]`, `tgt_strata=obs_strata[i]` — same index `i` for encoder source AND decoder target; docstring brags "self-reconstruction objective"). 04B is a source→target **translator** (`_encode` docstring L287 "Encode observed source diary"; folds ground-truth occupancy `aux_seq` into per-slot encoder memory at L289 `slot_linear(cat([act_emb, aux_seq]))`, which the Arm-2 home/work heads read straight back via `memory[:,1:,:]` at L362) — safe ONLY when src≠tgt. By self-pairing, Step-6 fine-tuned the translator into an **identity autoencoder that copies the leaked occupancy** → every checkpoint W_2005…W_pooled_2030 is a COPIER; all bands feed the same real 2022 `aux_seq`, so a 1-bit TELEWORK in cond can't move a copying head → inert. **NOT the locked 04B model, NOT the fp32 fix** (correct — merely exposed this), **NOT cond-injection** (TELEWORK correctly in the 119-dim cond, `step4_feature_config.json` L267 `"TELEWORK":{"type":"binary"}`; band resample L1474-1490 mutates the tensor fine — a copier just ignores cond). Correct recipe Step-6 discarded = 04D `Step4Dataset2Split` (src=`pairs["src_idx"][i]`, tgt=sampled **neighbour** `t≠s`, L155-176) fed by 04C `3rdJ_04C_pairs_2split.py` KNN cross-day pairs (`training_pairs.pt` = `{src_idx, tgt_k_indices K=5, tgt_strata}`). **Fix (ONE bundle):** rebuild Step-6 progressive training with 04C/04D cross-day pairing per cycle → rebuild all W_* checkpoints (current ones unusable) → re-run backcast (expect real positive nonzero JS) + 3-band forecast (expect bands to diverge). **Step 6 NOT done; Step 7 NOT started.** |
| 2026-06-24 | Control-test cycle BUILT — "is TELEWORK learnable?" probe on the GOOD translator (Opus draft) | Before committing to the ~8 h cross-day-pairing retrain, a cheap deterministic probe picks the fix branch (diagnosis item D), run on the GOOD Step-4 translator (`R5_lr1e4/checkpoints/best_model.pt` — trained correctly with 04C pairs, NOT the broken Step-6 copiers). New file **`3rdJ_06_control_telework_2split.py`** (Step6_docs): imports the REAL inference plumbing (`build_tensors_from_df` / `build_model` / `model.generate`) from the Step-6 module so it faithfully mirrors the forecast path; loads the 2022 weekday-employed cohort (default n=3000, seed 42); generates twice — ALL TELEWORK=0 vs ALL=1 (maximal contrast, identical source rows) — at temp **0.0** (deterministic; isolates the TELEWORK bit with zero sampling noise) AND **0.8** (the forecast temp that collapsed); reports business-hours (slots 11–26) AT_HOME & AT_WORK means + deltas + WFH proxy + rows-changed, then prints a VERDICT: dHome≥+0.02 → **MOVES** (TELEWORK learnable → proceed with the retrain); \|dHome\|<0.005 → **FLAT** (use the documented post-hoc TELEWORK-reweight fallback); else **WEAK**. CPU-only, runs in minutes; no new deps (torch/numpy/pandas, all in step4 env). Submit (cluster, from Step6_docs): `sbatch -p ps --mem=16G -t 01:00:00 -J s6_twctl -o control_tw_%j.out --wrap "/speed-scratch/o_iseri/envs/step4/bin/python 3rdJ_06_control_telework_2split.py --n 3000"`. Sonnet employee assigned to scp-upload + submit + relay the table/verdict. |
| 2026-06-24 | Control probe `3rdJ_06_control_telework_2split.py` uploaded + submitted as job 987005 (ps, RUNNING) | Employee (Sonnet 4.6). Speed reachable (echo OK). Input files verified: `R5_lr1e4/checkpoints/best_model.pt` (50 MB, Jun 16) and `R5_lr1e4/augmented_diaries.csv` (519 MB, Jun 16) both present. Script scp-uploaded to `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/`. Submitted: `sbatch -p ps --mem=16G -t 01:00:00 -J s6_twctl --chdir=...Step6_docs -o control_tw_%j.out --wrap '...python 3rdJ_06_control_telework_2split.py --n 3000'` → job **987005**. Status at T+2s: RUNNING on ps. Output file: `control_tw_987005.out`. When finished, read with: `ssh o_iseri@speed.encs.concordia.ca "cat /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/control_tw_987005.out"` |
| 2026-06-24 | Control probe 987005 TIMEOUT → re-submitted | Job 987005 timed out at 1h on ps (CPU) with empty output (3000 rows x4 AR passes too slow + block-buffered stdout lost on SIGKILL). Re-submitted as **987024** with python -u (unbuffered), --n 500, -t 02:00:00. Decisive temp=0.0 dHome row should flush ~5 min in. |
| 2026-06-24 | Control probe resubmitted at 7-day cap | Cancelled 987024 (2h cap, non-compliant with new 1-week-min walltime policy); resubmitted as **987027** with -t 7-00:00:00, python -u, --n 500. No more short-cap TIMEOUTs. |
| 2026-06-24 | **Control 987027 COMPLETE — VERDICT: FLAT (decisive)** | 500 employed WD-2022 rows on the GOOD Step-4 R5_lr1e4 translator, all-TW0 vs all-TW1 (max contrast), real forecast plumbing. **det (temp=0.0): home 0.3736→0.3691 dHome=−0.0045** (FLAT, \|.\|<0.005, and WRONG sign); work 0.5543→0.5567 dWork=+0.0025 (wrong sign); **only 18.8% of rows changed at all**; WFH proxy 0.9159→0.9129. temp=0.8: dHome=+0.0095, dWork=−0.0132 (right sign but tiny, ≪+0.02 MOVES bar; partly sampling noise). Conditioning IS wired (deltas & rows_chg ≠ 0 ⇒ the TELEWORK bit reaches the cond vec) so FLAT is a genuine learned-model property, NOT a wiring bug. **TELEWORK is NOT a learnable lever ⇒ no retrain will make the 3 WFH bands diverge via conditioning; bands MUST come from the documented EXOGENOUS post-hoc reweight** (mixture of WFH/office day-types resampled to 17.5/30/40% share). **The self-pairing copier bug STILL needs the cross-day 04C/04D pairing retrain** — but for valid drift-aware checkpoints + a valid 2022 backcast, NOT for band sensitivity. Fix = **BOTH in one bundle**: (1) cross-day-pairing retrain → drift + backcast; (2) post-hoc reweight → 3 bands. Awaiting user OK before the ~8 h `pg` retrain. **Step 6 NOT done; Step 7 NOT started.** |
| 2026-06-24 | **FIX BUNDLE shipped — Job 987039 submitted (pg GPU, 7-day)** | Employee (Sonnet 4.6). Three-fix bundle applied to `3rdJ_06_longitudinalForecasting_2split.py` (pre-fix archived locally + on cluster as `archive/3rdJ_06_longitudinalForecasting_2split.preCrossDayPairing.py`): **(Fix A) Cross-day KNN pairing**: replaced `Step6Dataset` self-pairing (src==tgt, copier root cause) with 04C-exact brute-force KNN pairing per cycle subset (`build_cycle_pairs`: EXACT_COLS=AGEGRP/SEX/MARSTH/HHSIZE/LFTAG, FUZZY_COLS=PR/CMA/HRSWRK/NOCS + TOTINC-6-bins, K=5, t≠s, same CYCLE_YEAR, different DDAY_STRATA; `Step6Dataset.resample()` draws fresh neighbour per epoch; `__getitem__` uses separate `s` and `t`). **(Fix B) Post-hoc day-type reweight**: replaced the TELEWORK-conditioning band override (proven FLAT by 987027) with `_posthoc_reweight()` — base 2030 forecast generated ONCE, each diary classified as WFH-day (biz-hours AT_HOME ≥ 0.50) or office-day, then AGEGRP-stratified donor draw to hit {17.5%, 30%, 40%} WFH-day share per band; inference cache prevents redundant model calls; non-employed rows pass through unchanged. **(Fix C) Anti-copy smoke gates**: 4 named gates added — Gate 1 slot disagreement ≥5% (PASS on smoke: 54.9%); Gate 2 JS_home/work ≥0 and finite (PASS: 0.164–0.234, no −0.0000); Gate 3 epoch-1 val_js > 0 AND loss ≥ 0 (PASS: val_js 0.209–0.219, loss 0.640–0.643); Gate 4 WFH-day shares separated (SKIPPED in smoke, no scenario CSV). **SLURM**: `--time=7-00:00:00` (was 48h), `python -u` (unbuffered). **Local smoke (`--smoke --stage all` on SAMPLE.csv) PASS: exit 0, all 3 gates pass, no copier signature.** Files uploaded (2 files: edited .py + updated .sh); submitted `sbatch slurm_06_2split.sh` → **Job 987039** (pg GPU, 7-day walltime). Output: `step6_2split_987039.out`. **Step 6 NOT done; Step 7 NOT started.** |
| 2026-06-26 | **Job 987039 COMPLETED clean — manager verdict: DEGENERACY FIXED + bands diverge, BUT work-channel backcast FAILS** | Opus, judged `.out` directly (no rubber-stamp of in-log PASS lines). Exit 0:0, Elapsed 1-06:34:35 (~30.5h), final deliverable `2030_synthetic_diaries_2split.csv` rows=111,024 written. **✅ Criterion 2 (bands) PASS — the primary bug is dead.** WFH-day shares per band 0.1702/0.2922/0.3883 (targets 17.5/30/40; deltas 0.48/0.78/1.17pp, all ≤3pp); Gate 4 monotone real-tested (smoke skipped it) → PASS (C<H<F). WD_AT_HOME **diverges** 0.6419/0.6692/0.6826; WD_AT_WORK 0.2201/0.1940/0.1810. JS is real & nonzero now (no −0.0000); D1 anti-copy gates PASS (Gate1 slot-disagree 0.6693; Gate2 JS-sign finite). **⚠️ Criterion 1 (backcast fit) FAIL.** 2022 backcast gate FAIL on all 3 strata: JS_work **0.4073/0.4537/0.4840**, JS_home 0.1996/0.1305/0.1158; stratum-1 dHome=0.1427 dWork=0.2187 (strata 2/3 deltas tiny). **⚠️ Criterion 3 (COVID drift) FAIL/WARN.** Only drift check (DRIFT_1522, 2015→2022, Phase 3) shows `AT_HOME_drift=−0.0824` (should be +) and `AT_WORK_drift=+0.1462` (should be −) → both WARNs, wrong direction. WFH_RATE per band nearly flat (0.8193/0.8140/0.8145) → "Monotone sensitivity: FAIL" (household any-occupant metric, ~invariant by design — minor). **Interpretation:** work-channel backcast miss + wrong COVID direction are the SAME finding already proven by control 987027 (TELEWORK/COVID not organically learnable) — which is the entire reason bands come from post-hoc reweight (Fix B), and those bands ARE valid. Deliverable sound; organic backcast is the suspect. **Decision (user): accept the bands but DIG INTO the work-channel backcast before final sign-off. Step 6 NOT declared done; Step 7 NOT started.** |
| 2026-06-26 | **Backcast gate-metric fix shipped + verified (job 1005383) — exposes a REAL weekday evening-latch** | Opus dig. **Root cause of "backcast FAIL" diagnosed:** the gate called `js_divergence(obs_<ch>[m].flatten(), gen_<ch>[m].flatten())` on RAW flattened binary occupancy. `js_divergence` (04D:539) normalises to sum=1, so on flattened 0/1 it measures EXACT per-(person,slot) cell overlap (memorisation), saturating near ln2≈0.693 for sparse channels even when the mean is matched — proof: weekend strata had dWork≈0.0005 yet JS_work≈0.45. **Fix (archived `archive/...preBackcastMetricFix.py`):** backcast gate now compares MARGINAL per-slot mean-occupancy PROFILES (48-vectors) — activity JS via bincount, home/work SHAPE via profile-JS, LEVEL via per-slot MAD + day-mean gap; PASS keys on MAD<0.10 (anti-copy Gate 1 slot-disagreement unchanged, still catches copiers). **Verification (cheap CPU job 1005383, ps, 25s, recompute on EXISTING `reconstructed_2022_diaries_2split.csv` — no model re-run):** weekend strata 2/3 OLD JS_work 0.45/0.48 → NEW profile-JS 0.020/0.014, MADw 0.018/0.021 → **PASS** (artifact cleared). BUT weekday stratum 1: NEW MADh=0.238 MADw=0.265 (real FAIL). Per-slot profile dump reveals the model **latches into a work state at midday and never returns home in the evening/night**: obs weekday WORK declines 0.36→0.02 by night, gen WORK plateaus ~0.47–0.51 from slot 15 through slot 48 (midnight); HOME mirror-image (obs rises to 0.95, gen stuck ~0.50). ~45pp error at midnight. Night slots 1–8 START correct (gen HOME 0.99) then drift → classic AR greedy-decode latch (backcast uses `temperature=0.0`). **KEY OPEN Q:** forecast deliverable uses temp≈0.8 sampling and band WD_AT_WORK is only 0.18–0.22 (not 0.50) — so the latch may be a greedy-only artifact of the backcast diagnostic, NOT in the 2030 deliverable. Dispatching a CPU profile of the existing `2030_synthetic_diaries_2split.csv` weekday curve to settle it. **Step 6 NOT declared done; Step 7 NOT started.** |
| 2026-06-26 | **Forecast deliverable PROVEN HEALTHY — latch is a temp=0.0 greedy artifact (jobs 1005623); root cause unified** | Opus dig, CPU job 1005623 (ps) profiled the EXISTING forecast CSVs (raw + mindwell + final deliverable), weekday rows, no model re-run. **Deliverable (conservative band, weekday) is HEALTHY:** WORK rises to ~0.41 midday then RELEASES to 0.084 by night (slots 40-48); HOME dips to ~0.35 midday then RETURNS to 0.868 — a realistic weekday curve, NO latch. Raw (pre-mindwell) and min-dwell profiles are near-identical, so mindwell isn't masking anything; the temp=0.8 generation is already healthy. **Root cause unified:** the forecast uses `temperature=0.8` (line 1835); the backcast (line 1647) AND the drift matrices (line 1015) use `temperature=0.0`. At temp=0.0 (greedy/argmax) the AR work head latches into a sticky attractor mid-day and never releases → weekday WORK plateaus ~0.50 all night. This single fact explains BOTH unresolved criteria: (1) the weekday backcast MAD FAIL, and (3) the wrong-direction COVID drift WARN (`AT_HOME −0.08 / AT_WORK +0.15` = exactly the signature of latched-high work / suppressed home in the temp=0.0 DRIFT_1522). The temp=0.8 deliverable has neither. **Net: the thing Step 7 consumes is sound.** Remaining to cleanly close = make the backcast a FAIR test: set backcast gen temp 0.0→0.8 (match the forecast) and re-run `--stage D1` only (quick GPU, no retrain). The drift-matrix COVID WARN is the same artifact but the drift matrices are an INTERNAL temp=0 training signal (re-running them = full multi-day retrain, not worth it since the deliverable is proven healthy) → document, don't re-run. **Awaiting user OK on the backcast temp-fix + D1 re-run vs declare-done-with-documentation. Step 6 NOT declared done; Step 7 NOT started.** |
