# Step 6 — Model 2: Longitudinal Forecasting 2005–2030, Four-Channel Split
### GSS channels: 3-head progressive fine-tuning (machinery ✅ DONE, Leg 2) + retail scenario lever ⚠️ PLANNED · Hotel: SARIMA side-track, entirely outside the Transformer ⚠️ PLANNED (non-GSS)

---

## AIM

Two parallel tracks, one per data nature:

1. **GSS track (Transformer):** reuse the Leg-2 four-stage progressive fine-tuning (`W_2005 → W_2010_ft → W_2015_ft → W_2022_ft`, per-transition DRIFT_MATRIX, pooled recency-weighted 2030 inference) with the **3-head** Leg-3 model. The office channel keeps its WFH bands (conservative ~17.5 % / hybrid ~30 % / fullyhybrid ~40 %); the retail channel gains its own **in-store-share lever** (post-hoc amplitude multiplier — see 6B). This is the first HPC step of the leg (GPU `pg` partition).
2. **Hotel side-track (SARIMA, non-GSS):** classical seasonal time-series on the ISQ/CBRE monthly series — the Transformer conditions on individual respondents; hotel occupancy is a population aggregate with no respondents behind it. `hotel_multiplier(t, month, PR) = s(t) × monthly_occupancy_rate(month, PR)`.

### Roadmap Checklist

- [ ] 6A input audit (Leg-3 pool schema incl. `ret30`; hotel canonical CSV)
- [ ] 6B script port: `--stage {audit,A,B,C,D1,D2,all}` chain on the 3-head model
- [ ] 6B2 scenario features 2030 (port; no retail conditioning to assemble)
- [ ] 6C–6E sub-stages A/B/C: base + 3 fine-tune phases + pooled 2030 training, DRIFT_MATRIX ×3 (now with an AT_RETAIL axis)
- [ ] 6F 2022 backcast gate (3 channels, profile-MAD metric)
- [ ] 6G 2030 bands: office WFH reweight (ported) + retail lever applied post-hoc
- [ ] 6H cleanup: 3-way mutex + 04M min-dwell (NO 04L rake on 2030)
- [ ] 6I hotel SARIMA fit + backcast gate
- [ ] 6J hotel 2030 forecast + s(t) lookup build
- [ ] Validation report + closure

## Data Inputs

| Input | Path | Notes |
|---|---|---|
| Training corpus | Leg-3 Step-4 **raw** pool (pre-rake) | **OD-1 discipline kept: train on raw, never on raked** — raked data teaches externally-imposed marginals and distorts learned drift |
| Backcast reference | Leg-3 Step-4 **locked (raked) pool** | comparison only, never training |
| Scenario features 2030 | `outputs_step6/scenario_2030_features_4split.csv` | port of the Leg-2 assembler |
| Hotel canonical series | `0_Occupancy/external/hotel_occupancy_monthly.csv` | Step-2 Delta-D output |
| Hotel diurnal shape | dr_L3-05 48-slot table (weekday + weekend variants) | encoded as a constant in 6J |

> Slot convention: 04:00 origin, business hours = slots 11–26 (unchanged). Naming: pool channels are `hom30/wrk30/ret30_*`; the Step-3 tiler's `WORK30_/RETL30_*` are a different namespace (Leg-2 collision warning carried forward).

## GSS track — Leg-3 deltas on the Leg-2 machinery

### 6A–6E: 3-head chain

- Model import: `3rdJ_04B_model_4split.py::JSeriesHybrid4Split` (LOCKED); TrendEncoder port unchanged except the DRIFT_MATRIX token now includes the **AT_RETAIL axis** (matrix spans 14 activities × 3 DDAY_STRATA × archetypes × {AT_HOME, AT_WORK, AT_RETAIL}).
- Loss: **fixed α 1.0 : 0.5 : 0.3 + PCGrad** (dr_L3-13 — Leg-2's UW mode is not carried; same rationale as Step 4), retail `pos_weight = 49` + −ln 49 decode shift preserved through every fine-tune stage.
- **Cross-day pairing discipline:** never self-pair (the Leg-2 Step6Dataset copier bug — `src == tgt` produced an identity autoencoder whose three bands were identical to 4 dp; backcast JS = −0.0000 was the tell). Replicate the 04C KNN pairing.
- Fine-tune chain, recency weights (0.10/0.20/0.30/0.40), early-stop policies: verbatim Leg 2.
- COVID dual-signal check on `DRIFT_MATRIX_1522` extended: AT_HOME ≥ +5 pp, AT_WORK directional decrease, **AT_RETAIL directional decrease** (in-store shopping fell through COVID) — all three must co-occur or investigate.

### 6F: 2022 backcast gate (3 channels)

- Metric: **marginal per-slot mean-occupancy profile comparison (shape-JS + level-MAD < 0.10)** — the Leg-2 lesson stands: raw flattened-binary JS saturates near ln 2 on sparse channels (retail at ~2 % positive is *the* worst case; a raw-JS gate would be meaningless).
- Generation temperature for backcast = deliverable settings (T 0.7 + nucleus 0.9 + min-dwell) — never greedy T = 0.0 (the Leg-2 sticky-attractor artifact).
- Gates: AT_HOME recon ±2 pp, AT_WORK ±3 pp, **AT_RETAIL ±1.5 pp level / MAD < 0.10 shape** (small absolute band — the channel is small), WFH_RATE ±5 pp.

### 6B/6G: the retail scenario lever ⚠️ PLANNED (Leg 3) — post-hoc by design

The office lever needed model-side band injection (and the Leg-2 TELEWORK conditioning proved **FLAT/non-learnable** — the bands ship via post-hoc day-type reweight). The retail lever is **designed post-hoc from the start**, sidestepping that whole failure class:

- **Three named scenarios (dr_L3-04, OD-2 RESOLVED), relative to 2022 = 1.00:** Plateau/Resilient Central (Default) = **0.97** · Continued-Shift (Conservative) = **0.90** · In-Store Renaissance (Optimistic) = **1.05**.
- Mechanics: the scalar multiplies `at_retail_fraction_2030(t)` **before** the Step-7 peak-normalization, so amplitude scenarios survive the shape-only injection (dr_L3-06 §C.3). Sensitivity bands = re-run, not retrain.
- **Two-province Sunday sub-axis (dr_L3-06 §C.4):** the 2005–2022 QC Sunday shapes encode the trading-hours restriction naturally through QC respondents — no manual adjustment historically. For 2030 the lever gains a Quebec-Sunday option: **default = restricted (Sunday ≈ 0.60–0.75 × Saturday peak); optimistic = deregulated (Alberta-like uplift)**. (Context: QC pilot from 2026-03-11 extends eligible retailers to 21:00; AB deregulated since 1985.)
- Deliverable: `at_retail_fraction_2030_{plateau,shift,renaissance}[_qcSundayDereg].csv` per day-type — small files, generated by one lever script.

### 6H: cleanup — 3-way mutex + min-dwell, NO rake

- Mutual-exclusion arbitration generalizes pairwise → **3-way** {home, work, retail} (deterministic, activity-based; the Step-4 exclusivity projection already guarantees ISR = 0 on decode — 6H is the belt-and-braces final pass) + `3rdJ_04M_mindwell_4split.py`.
- **No 04L marginal rake on the forecast year** (Leg-2 rationale verbatim: no observed 2030 marginals; raking to the model's own projection is circular).
- Canonical deliverable: `2030_synthetic_diaries_4split_calibrated_mindwell[_C].csv` — the calibration-B/C ports (weekday work cap, weekend home restore, activity re-anchor) run against observed-2022 anchors exactly as in Leg 2, extended with a **retail cap stage**: cap 2030 per-slot retail at observed-2022 profile × lever value (target-anchored, never delta-subtraction — the Leg-2 over-correction lesson).
- **🔴 Mutex guard inside every calibration stage (the Leg-2 2026-07-17 mutex-bug lesson).** Leg-2's calibration-C weekend min-dwell smoother re-raised `hom30` on `wrk30==1` slots with no guard — 4,280 physically impossible cells reached Step 7/8/9 and forced a 72-task re-sim, because no downstream validator checked mutex either. The Leg-3 ports therefore: (a) **fork from the FIXED calibration-C** (post-`20260717_pre_mutexfix` archive — the archive itself is the WRONG base); (b) every stage that writes any occupancy channel runs a **hard assertion after it**: `(hom∧wrk) = (hom∧ret) = (wrk∧ret) = 0` — abort, never warn; (c) any smoother/min-dwell pass must check the *other two* channels before raising a slot.
- Non-`_C` glob hazard: superseded 2030 variants (`_BAK_*`, `.preRake_*`, the non-`_C` file) are moved to `outputs_step6/archive_pre_*/` at write time — never left beside the canonical deliverable (Leg-2 hygiene item C1); record the `_C` MD5 in the Progress Log at sign-off (the Leg-2 ledger gap).

## Hotel side-track ⚠️ PLANNED (Leg 3, non-GSS) — [NEW] `3rdJ_06_hotel_sarima_4split.py`

### 6I — Fit + backcast gate

1. **Order selection (dr_L3-09 recipe):** fit candidates on the **pre-COVID segment only (2005–2019)**; select (p,d,q)(P,D,Q)₁₂ by BIC/AICc (expected: **SARIMA(1,1,1)(1,1,1)₁₂**); verify Ljung-Box residual whiteness; **freeze orders**.
2. **Re-estimate on full 2005–2022** with intervention terms: **COVID pulse dummy (2020-03…2022-06) + permanent level-shift term** persisting past the window (dr_L3-09 rejects pure-pulse as over-optimistic — corporate travel stabilized 10–15 % below pre-COVID — and pure level-shift as over-pessimistic), plus the AB splice dummy `D_splice` (t ≥ 2010-01) if a level shift is detected at the splice.
3. **Backcast gate (spec §7):** reconstruct 2015–2019 QC + AB months → **MAE < 0.05** vs the historical series; the 2020-04 dip must be recovered **without overshoot**.

### 6J — 2030 forecast + multiplier build

- Forecast the monthly path to 2030; report SARIMA 80 %/95 % prediction intervals (statistical uncertainty) **and** the three named scenario bands (physical states, for the simulation campaign): **Low 0.92 / Central 1.00 / High 1.05** on the central path, with **provincial tilts: AB low = 0.90, QC high = 1.07** (dr_L3-09).
- Outputs: `0_Occupancy/forecasts/hotel_multiplier_2030.csv` (12 monthly values × PR × band) and `0_Occupancy/processed/hotel_multiplier_lookup.csv` (historical months × PR).
- **s(t):** the dr_L3-05 unit-normalized 48-slot guest-room shape, weekday + weekend variants (overnight plateau 1.00 22:00–06:00; day trough 0.200 weekday 09:00–15:00 / 0.308 weekend 09:00–17:00; evening return ramps; weekend evening spike 19:00–20:30). Encoded as a constant table; holidays = weekend shape (dr_L3-05 delivers no separate holiday variant — record as limitation).
- Sanity anchors for the central path: 2023–2025 actuals QC ~0.635 (Mtl ~0.666 in 2025), AB ~0.615 (Calgary ~0.63).

Hotel compute is negligible → runs **locally** (statsmodels); no cluster job.

## Module Structure Summary

```
3rdJ_06_longitudinalForecasting_4split.py   (--stage {audit,A,B,C,D1,D2,all} --band ... --smoke)
assemble_scenario_2030_4split.py            (--verify)
3rdJ_06_retail_lever_4split.py              (post-hoc amplitude lever + QC-Sunday sub-axis)
3rdJ_06_calibrate_C_4split.py               (calibration B/C ports + retail cap stage)
3rdJ_06_hotel_sarima_4split.py              (6I/6J — fit, backcast, forecast, lookup build)
3rdJ_06_longitudinalForecasting_4split_val.py
slurm_06_4split.sh                          (#SBATCH -p pg --gres=gpu:1 -t 7-00:00:00 --mem=32G)
outputs_step6/                              (checkpoints, DRIFT matrices, 2030 diaries, hotel CSVs)
```

## Expected Result

- `W_*.pt` chain + `trend_encoder_2030_4split.pt`; `DRIFT_MATRIX_{0510,1015,1522}_4split.csv` with the retail axis; COVID triple-signal present in `_1522`.
- 2022 backcast: 3 channels within gates on the profile metric.
- `2030_synthetic_diaries_4split_calibrated_mindwell[_C].csv` + retail lever files + `hotel_multiplier_2030.csv` + `hotel_multiplier_lookup.csv`.
- Band structure: office WFH monotone (fully > hybrid > cons on WFH-day share); retail lever exact by construction (0.90/0.97/1.05); hotel bands monotone (low < central < high).

## Test Method

1. `--smoke` locally end-to-end (tiny epochs), then hotel script locally in full (seconds).
2. Cluster (on the cluster, single line): `sbatch slurm_06_4split.sh` — **sbatch only; 7-day walltime; no polling** — read the `.out` afterwards.
3. Validator (`3rdJ_06_longitudinalForecasting_4split_val.py`) → target 0 FAIL; inspect the DRIFT triple-signal chart, backcast profile overlays, hotel backcast overlay + 2030 fan chart.

## Open Decisions

1. **Retail lever composition with the QC-Sunday sub-axis** — default = restricted; the deregulated variant is an optional extra file, not a 4th band. ✅ pre-resolved by dr_L3-06 §C.4 defaults; revisit only if the Step-8 scenario matrix needs trimming.
2. **Hotel AB series fallback** — if Step 1/2 shipped the truncated 2010–2022 AB series, 6I fits on 156 obs and the splice dummy is dropped. Decision inherited from the acquisition record; no new approval needed.

## Progress Log

*(append entries below — `| Date | Action | Notes |` table rows or dated `###` entries; job IDs; keep the non-closure discipline: "Step 6 NOT declared done" until the validator signs off)*
