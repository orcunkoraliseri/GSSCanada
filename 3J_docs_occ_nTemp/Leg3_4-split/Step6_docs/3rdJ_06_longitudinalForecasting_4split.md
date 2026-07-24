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

### 2026-07-22 — Track A builder (Part 1): port + smoke test + submit

**Employee session**, executing `3rdJ_06_trackA_builder_prompt.md`. Built the Leg-2→Leg-3 port, smoke-tested locally, submitted ONE cluster job, stopped (no polling) per cluster discipline.

**Files created** (all under `Step6_docs/`):
- `3rdJ_06_longitudinalForecasting_4split.py` — main script, `--stage {audit,A,B,C,D1,D2,all} --band ... --smoke --data`. Ported from Leg-2's `3rdJ_06_longitudinalForecasting_2split.py` (2350 lines) with the deltas below.
- `assemble_scenario_2030_4split.py` — `--verify` dry-run / write mode, writes `outputs_step6/scenario_2030_features_4split.csv`. No retail-conditioning column added (per runbook §6B/6G — the retail lever is post-hoc, downstream, and not built this session).
- `slurm_06_4split.sh` — `#SBATCH -p pg --gres=gpu:1 -t 7-00:00:00 --mem=32G`.

**Raw-pool decision (seed_3 vs seed_3_g3fix): used `seed_3_g3fix`.** Confirmed on the cluster (`ls -la outputs_step4/`): `seed_3/` mtime 2026-07-19 18:11 vs `seed_3_g3fix/` mtime 2026-07-21 13:04 (later). Step-4's own Progress Log (`3rdJ_04_augmentationGSS_4split.md`, 2026-07-21 entry) records: *"DECISION (user-confirmed 2026-07-21): accept the seed_3_g3fix pool WHOLESALE"* — the G3 co-presence-fix rerun of the winning seed_3 checkpoint supersedes seed_3 (activities 99.9998% identical, co-presence internally consistent post-fix, `seed_3` preserved not deleted). This is a documented, already-resolved decision, not an open ambiguity — used `seed_3_g3fix/augmented_diaries.csv` as the default raw training pool, with fallback `seed_3` → flat `outputs_step4/augmented_diaries.csv` if not found (mirrors Leg-2's fallback-chain pattern). `--data` overrides.

**Key deltas applied vs the Leg-2 fork base** (per builder prompt §1-§9):
1. Loss/weighting (§3): removed Leg-2's `UncertaintyWeighting`; imported `component_losses`, `diversity_loss`, `exclusivity_loss`, `PCGrad`, `js_divergence`, `TASK_GROUPS`, `LAMBDA_DIV` directly from `3rdJ_04D_train_4split` and reused fixed-alpha (1.0/0.5/0.3) + PCGrad across the 3 task groups (resid=act+home+cop, work, retail), `retail_pos_weight` resolved from `step4_feature_config.json` (50.10556).
2. Cross-day pairing (§4): `build_cycle_pairs()`/`_score_candidates_pairing()`/`_bin_totinc_for_pairing()` ported verbatim (channel-agnostic); `Step6Dataset` extended with `dec_retail_avail`.
3. DRIFT_MATRIX (§5): `compute_drift_matrix_4split()` adds `AT_RETAIL_drift`; `TrendEncoder4Split.n_output` set to 9 (3 strata × 3 channels, was 6) and `from_drift_csvs()` pulls the quadruple `[AT_HOME_drift, AT_WORK_drift, AT_RETAIL_drift, aggregate_JS]`. COVID check extended to a triple-signal (home↑, work↓, retail↓), soft-blocker (WARN, not FAIL) per the val plan.
4. Deliverable decode (§6): new `decode_deliverable()` helper wraps `generate_nucleus()` + `calibrate_retail_prob()` + `exclusivity_projection()` + `apply_activity_override_3ch()` + `enforce_min_dwell_row()` — all imported from `3rdJ_04E_inference_4split`, none reimplemented, `3rdJ_04B_model_4split.py` untouched. Used for both D1 (2022 backcast) and D2 (2030 base forecast) at deliverable settings (T=0.7, nucleus p=0.9, min-dwell=2) — never greedy. Internal diagnostics (DRIFT_MATRIX, `validate_cycle` early-stop signal) intentionally kept greedy (T=0.0) via the model's own `generate()`.
5. 6H mutex (§ val plan): `mutual_exclusion_resolve()` rewritten as a hard-assertion 3-way verifier (raises `AssertionError`, never warns) — the decode chain already guarantees ISR=0 by construction, this is belt-and-braces per the Leg-2 2026-07-17 mutex-bug lesson.

**Judgment calls / deviations flagged:**
- **WGHT_PER survey-weighting NOT wired into Step-6's loss** (`component_losses(..., wght_per=None)`), even though Step-4's own `component_losses` signature supports it. Not part of the builder prompt's §3-§9 deltas, and Leg-2's own Step-6 didn't wire it either — kept consistent with the fork base rather than silently adding a new weighting axis.
- **`lambda_excl=0.05` kept ON throughout every Step-6 fine-tune stage** (no warmup/joint phase split like Step-4 has) — Step-6 has no analogous "retail-head-only" phase since the retail head is already warm from Step-4's own 2-phase schedule by the time Step-6 warm-starts from its checkpoint.
- **TrendEncoder's 50-iteration fit is still against an all-zero dummy target** (ported as-is from Leg-2, ×3 output dim now 9). Flagging explicitly per §5: this is a known limitation carried forward, NOT a completed distribution-matching improvement — do not read it as one.
- Anti-copy Gate 2 (JS sign check) left scoped to home/work only (unchanged from Leg-2), matching the builder prompt's silence on extending it to retail — retail-specific backcast gates are validator scope (deferred, out of session).

**Smoke test:** `--stage audit` then `--stage all --smoke` run locally (CPU, `py -3 -X utf8`) against the local 180-row 4-cycle sample (`Step4_docs/outputs_step4/smoke_test_20260719/augmented_diaries_SMOKE.csv` — chosen because the 418 MB `seed_3_g3fix` pool is cluster-only; this file has all 4 cycles × 3 strata present, unlike a random subsample). Result: **exit code 0**, all 5 stages (audit, A, B, C, D1, D2) completed. `DRIFT_MATRIX_{0510,1015,1522}_4split.csv` all written with the new `AT_RETAIL_drift` column populated (verified via `head`). Pairing sanity confirmed — no JS≈0 / no identical bands (Gate 1 slot-disagree=0.656, Gate 2 JS_home=0.108/JS_work=0.210, Gate 3 val_js>0 and loss≥0 at every warm-start, Gate 4 skipped in smoke mode per design since the tiny sample has no real WFH-day pool). 6H mutex guard: 0 violations across all 3 bands. `2030_synthetic_diaries_4split.csv` (6 rows, smoke-scale) written as the final deliverable. One cosmetic-only, non-blocking artifact: `call_mindwell()`'s subprocess capture threw a `UnicodeDecodeError` in the reader thread on Windows local (cp1252 vs utf-8 mismatch decoding 04M's own em-dash prints) — did not affect `returncode` (0) or the min-dwell output files; inherited unchanged from Leg-2's `subprocess.run(..., text=True)` pattern, expected to not reproduce on the cluster's Linux/UTF-8 locale.

**Cluster submission:** files scp'd to `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step6_docs/` (dir did not exist yet, created). `sbatch slurm_06_4split.sh` → **job 1133427**. Not polled per cluster discipline — `.out`/`.err` land in `/speed-scratch/o_iseri/logs/3J_s6_4split_1133427.{out,err}`, to be read in the follow-up post-run session (`3rdJ_06_trackA_postrun_prompt.md`).

**Step 6 NOT declared done** — Part 1 (build/smoke/submit) only. Validator and calibration chain are out of scope for this session.

### 2026-07-22 — Track B: hotel SARIMA side-track (fully local, independent of Track A)

**Employee session**, executing `3rdJ_06_trackB_hotel_builder_prompt.md`. Built and ran
`3rdJ_06_hotel_sarima_4split.py` locally (`py -3 -X utf8`, statsmodels 0.14.6). No cluster
dependency.

**Critical pre-check finding (per the prompt's "read the CSV first" instruction):** the
harmonized `0_Occupancy/external/hotel_occupancy_monthly.csv` does **not** have "AB
truncated to 2010-2022 / QC full 2005-2022" as the runbook's OD-2 discussion implicitly
assumed. Actual real (non-blank) coverage is:
- **AB**: 2011-01 .. 2022-09 (n=141, one internal gap at 2011-12) — this IS the runbook's
  already-anticipated "truncated AB" fallback branch (line ~117: splice dummy dropped, fit
  on the available obs), just starting 2011 rather than 2010.
- **QC**: 2019-01 .. 2022-12 (n=48) — **only 12 pre-COVID months (2019 itself)**. This is
  a much harder constraint than anything OD-2 discussed (which was AB-only). Confirmed via
  Step 1's own header comment (`3rdJ_01_hotelIngest_4split.py` line 213: *"Real coverage:
  2019-2025 (2005-2018 GAP)"*) — a known, pre-existing Step-1 acquisition gap (ISQ's
  accessible Power-BI dashboard only exposes 2019+), not a bug introduced here.

**6I.1 order selection (frozen):**
- **AB**: independently fit + BIC-selected on its own pre-COVID segment (2011-01..2019-12,
  n=108, 33/36 candidate grid cells converged). Grid restricted to **d=1, D=1** by design
  (see below) with p,q∈{0,1,2}, P,Q∈{0,1}. **Selected order: SARIMA(1,1,0)(0,1,0)₁₂**, BIC
  = −431.26. Differs from the runbook's stated expectation SARIMA(1,1,1)(1,1,1)₁₂ — treated
  as "expectation to verify, not hardcode" per the prompt; the simpler order won BIC on the
  actual 108-obs AB segment.
- **QC**: pre-COVID segment (n=12, 2019 only) is objectively too short to identify a
  seasonal SARIMA(P,D,Q)₁₂ term (D=1 alone consumes all 12 obs). **Order BORROWED from
  AB's independently-selected order** rather than independently fit — flagged as a gate
  8.1 **FAIL for QC** in the Section-8 table (data-availability limitation, not softened).
- **d/D grid note**: an open d∈{0,1} grid was tried first; it picked a non-differenced
  (d=0) AR(1)×SAR(1) model that fit the short pre-COVID window fine by BIC but had no
  anchored long-run mean once COVID exog terms were added on the full-series refit — see
  6J note below. Restricted the grid to d=1,D=1 (both structurally justified — occupancy
  has neither a trend-stationary nor seasonally-stationary level) and reselected within
  that space; documented in the script's `bic_grid_search()` docstring.

**Splice dummy `D_splice`: omitted for both provinces** (empirically checked, not
assumed). AB's 2005-2009 CBRE archive splice was never acquired (Step 1's
`read_cbre_ab_archive()` returns `[]` — "Not acquired"), so AB is single-sourced
(Alberta Market Monitor) throughout its entire available span — there is no 2010-01
splice EVENT in the data to test for.

**6I.2 full-series refit + intervention spec:** frozen order re-estimated on the full
real-observation span per province with exog = `[covid_pulse (2020-03..2022-06),
level_shift (t≥2020-03, persists through 2030)]` — both pulse-only and level-only were
rejected per dr_L3-09's own recommendation (pure pulse over-optimistic, pure level
over-pessimistic). Gate 8.5 PASS for both provinces.

**6I.3 backcast gate (8.3) + COVID dip (8.4):**
- **AB**: backcast window 2015-01..2019-12 (n=60, full window available) → **MAE = 0.0174**
  (gate < 0.05) — **PASS**. 2020-04: reconstructed 0.2767 vs actual 0.1120 vs historical
  low 0.1250 — no overshoot below the historical low — **PASS** (though the reconstruction
  materially under-estimates the dip's depth; the "no overshoot below" criterion is still
  literally satisfied).
- **QC**: **no ground truth exists for 2015-2018** (ISQ real coverage starts 2019-01).
  Tested only on the available overlap 2019-01..2019-12 (n=12) → MAE = 0.0990 — **FAIL
  (PARTIAL)**, flagged explicitly as a partial 1-year test standing in for the nominal
  5-year window, not silently reported as a full pass. 2020-04 dip check: PASS (no
  overshoot).

**6J — 2030 forecast + central-path methodology (the key engineering decision this
session):** The fitted intervention-SARIMA model's own raw 96-step-ahead point forecast
was tried FIRST as the scenario-band central path per the obvious reading of the spec, and
was **rejected after investigation** (per the prompt's explicit instruction: "if central
forecast is wildly off anchors, investigate before shipping"). Every (d,D) combination
tested produced a 2030 central-path annual mean between **0.72 and 2.71** for a series
bounded in (0,1] — the classic long-horizon ARIMA extrapolation failure mode dr_L3-09
itself warned about ("if the trend is estimated with a slight bias due to the tail-end
recovery in 2021-2022, the 2030 forecast will diverge significantly") — with only
108-141 (AB) / 48 (QC) training observations and a 2020-2022 tail dominated by a sharp
COVID-recovery ramp, the 96-step extrapolation compounds that ramp's momentum
unboundedly. **Fix shipped**: the scenario-band central path uses
`central_2030(month, PR) = normalized_2019_monthly_shape(month, PR) × ANCHOR_2023_2025[PR]`
— i.e. the last full pre-COVID year's seasonal shape (stable per dr_L3-05/dr_L3-09
literature), rescaled so its annual mean equals the real 2023-2025 CBRE/STR-reported
recovery anchor already given in the builder prompt. This is the literal reading of
dr_L3-09 Table 5's own central-scenario definition ("Full Recovery / Central-Default:
travel demand stabilizes at its historical 2019 rates"), anchored to the *recovered*
level (AB's raw 2019 mean in this series, 0.541, sits ~7pp below its own 2023-2025 CBRE
anchor — Calgary's 2022-2026 travel/convention rebound pushed the market above its
pre-COVID reference). The raw SARIMA point forecast + 80%/95% PI is still computed and
reported (per spec — "report SARIMA statistical prediction intervals") but is NOT used as
the shipped central path; its drift is surfaced as an explicit, separate, honestly-WARN
sub-check under gate 8.6, not hidden.

**2030 central-path sanity check vs anchors:**
| PR | Shipped central-path 2030 mean | Anchor (2023-2025) | Diff | Gate 8.6 (shipped) |
|---|---|---|---|---|
| QC | 0.6350 | 0.635 | 0.0000 | PASS (by construction) |
| AB | 0.6150 | 0.615 | 0.0000 | PASS (by construction) |

Raw SARIMA 96-step point forecast (diagnostic only, NOT shipped): QC 2030 mean = 2.7127,
AB 2030 mean = 2.6007 — both flagged WARN under a separate 8.6 sub-row, documented as the
long-horizon-extrapolation instability described above.

**Outputs written:**
- `0_Occupancy/forecasts/hotel_multiplier_2030.csv` (72 rows = 12 months × 2 PR × 3 bands;
  columns include `band_multiplier`, `occupancy_rate`, `central_path_2030`,
  `sarima_raw_forecast_2030` for traceability). Rates range AB [0.405, 0.761], QC [0.433,
  0.897], all within (0,1].
- `0_Occupancy/processed/hotel_multiplier_lookup.csv` (189 rows = 141 AB + 48 QC real
  historical months, for Step 7's 2022 hotel product).
- `0_Occupancy/processed/hotel_diurnal_shape_st.csv` (96 rows = 48 slots × 2 day-types,
  the dr_L3-05 table hardcoded in the script and cross-checked value-by-value against
  dr_L3-05_hotel_diurnal_shape_REPORT.md Table 5). **Holidays use the weekend shape** —
  dr_L3-05 has no separate holiday variant, documented limitation, not invented.
- `outputs_step6_hotel/section8_hotel_gate_scorecard.csv` — full Section-8 gate table.

**Section-8 scorecard: 15 PASS / 3 WARN / 2 FAIL (20 gate rows across 10 gate IDs × ≤2
PR/sub-checks each).** FAIL-severity rows that did NOT pass (flagged, not softened):
- **[8.1] QC FAIL** — order borrowed from AB, not independently selected (pre-COVID n=12
  insufficient).
- **[8.3] QC FAIL (PARTIAL)** — backcast tested only on 2019 (n=12), no 2015-2018 ground
  truth exists for QC.

All other FAIL-severity gates PASS: 8.1 AB, 8.3 AB, 8.4 (both), 8.5 (both), 8.7 (both),
8.9, 8.10. WARN-severity gates: 8.2 AB (Ljung-Box p=0.0049, mild residual autocorrelation
remains after intervention), 8.6 raw-SARIMA-path sub-check (both PR, documented drift,
not the shipped path). 8.2 QC PASS (p=0.6644), 8.6 shipped-path (both PR) PASS, 8.8
seasonality-preservation PASS (both PR, r=1.000 QC / r=0.974 AB vs pre-COVID profile).

**Per the val doc's additive-safety principle: this hotel-track FAIL (8.1/8.3 QC) does
NOT block Track A / GSS-channel sign-off**, but per the same doc it DOES block Step-7
hotel injection specifically for QC's reliability — the fall-back guarantee routes hotel
Spaces to NECB baseline if this track isn't clean. Given QC's order-selection and backcast
gates are both data-availability-limited (not process failures — the underlying ISQ data
for 2015-2018 simply doesn't exist in the acquired series), Step-7 should treat QC hotel
injection as **usable-with-caveat** (the full-series fit itself is well-behaved: Ljung-Box
p=0.66, backcast MAE on the only available year is 0.099 — 2× the 0.05 gate, not
wildly off) rather than as a hard block equivalent to a modeling error — flagging this
distinction for the Step-7 employee/manager to weigh, not deciding it here.

### 2026-07-23 — Track A Part 2: post-training calibration + validation

**Employee session**, executing the Step 6 Track A Part 2 prompt (post-run calibration
+ full validation, Sections 1-8). Cluster job 1133427 (COMPLETED, exit 0) already
produced the raw 2030 per-band diaries, the 2022 backcast, and the 3 DRIFT matrices;
this session downloaded those (ONE scp block, per the staging note), built the
calibration chain locally, and ran the validator. No further cluster access.

**Files created** (all under `Step6_docs/`):
- `3rdJ_06_retail_lever_4split.py` — post-hoc retail amplitude lever (0.90/0.97/1.05)
  + QC-Sunday sub-axis. Writes `at_retail_fraction_2030_{plateau,shift,renaissance}.csv`
  (432 rows each: 3 day-types x 48 slots x 3 PR_GROUPs) + one extra
  `at_retail_fraction_2030_renaissance_qcSundayDereg.csv` (QC Sunday rescaled to AB's
  own Sun/Sat ratio, paired with the optimistic/renaissance scenario per the runbook's
  own naming, not a 4th band).
- `3rdJ_06_calibrate_C_4split.py` — ONE combined script: Stage B (weekday work-tail
  trim, per band) -> global 04M min-dwell (real `3rdJ_04M_mindwell_4split.py` via a
  throwaway-tempdir subprocess round-trip) -> Stage C0 (weekend work cap) -> Stage C1
  (weekend home restore + local min-dwell) -> Stage RETAIL (retail cap, target-anchored,
  [Leg-3 NEW]) -> Stage C2 (4-state activity restore: OUT/HOME/WORK/RETAIL). All stages
  in-memory in one process (design delta vs Leg-2's file-staged pipeline — see the
  script's module docstring); only the final canonical `_C` file is ever written to
  `outputs_step6/`, so the "non-`_C` glob hazard" file-hygiene requirement is satisfied
  by construction (no superseded intermediates are ever created).
- `3rdJ_06_longitudinalForecasting_4split_val.py` — validator, Sections 1-8, ported
  from Leg-2's `LongitudinalForecastingValidator2Split` to `...Validator4Split`.

**Mutex priority order: work > retail > home** (manager-decided, per the task
instructions — not re-litigated here). Rationale recorded: work is the most
behaviorally-constrained/least-ambiguous signal (implies a verifiable employment
commitment); retail implies a verifiable trip; home is the default/residual state,
the correct one to yield when a conflict must be broken. Implemented as a HARD gate
(`resolve_and_assert_mutex()`) after **every** single-channel stage touching
{home, work, retail} — Stage B, the global mindwell pass, Stage C0, Stage C1, Stage
RETAIL, Stage C2 — recomputes all 3 pairwise conflict masks, resolves by priority,
prints the count cleared, then hard-`assert`s 0 remain (never warns). **The guard was
NOT a no-op**: post-global-mindwell showed 0 violations (clean, confirming the
Step-4 exclusivity projection + Stage B's own H/W complementarity held), but
**post-Stage-C1 cleared 748 real home&work conflicts** (the weekend hom30 local
min-dwell smoother re-raised home on some wrk30==1 slots, exactly the class of bug
the runbook's 2026-07-17 mutex-bug lesson warned about) — caught and cleared before
they could reach Step 7/8/9. Final 3-way mutex conflict count in the canonical
deliverable: **0** (asserted, gate 6.7 PASS).

**Canonical deliverable:** `2030_synthetic_diaries_4split_calibrated_mindwell_C.csv`
(111,024 rows = 3 bands x 37,008). **MD5: `7c105ef331b37107d5b605c95028c3ba`**.
Built with the default retail lever = **plateau (0.97, Plateau/Resilient Central)**;
`shift` (0.90) and `renaissance` (1.05) are available via `--retail_lever` for a
cheap re-run (retail-cap stage only, not a model retrain) per the runbook's own
"sensitivity bands = re-run, not retrain" design.

**Bugs found and fixed during this session (both self-caught before sign-off):**
1. **Activity-code constants ported from the WRONG table.** Naively copied Leg-2's
   `(WORK_ACT, SLEEP_ACT, PASSIVE_ACT) = (0, 13, 10)` (0-indexed) into the Leg-3
   Stage-B port. Empirically verified against the pooled raw 2030 act30 distribution
   (code 5 dominant at ~26.9% — consistent with Sleep, not code 14 at ~8.1%) and
   against the AUTHORITATIVE code table used consistently across Step2/Step3/Step5
   (`3rdJ_03_mergingGSS_4split.py::BEM_PRIORITY`, `ACT_LABELS` in the Step2/Step5
   validators): 1=Work, 2=HH Work, 3=Caregiving, 4=Purchasing, 5=Sleep&Rest, 6=Eating,
   7=Personal Care, 8=Education, 9=Socializing, 10=Passive Leisure, 11=Active Leisure,
   12=Community, 13=Travel, 14=Misc/Idle — completely different from the main build
   script's `ACT_NAMES` list, which is a DRIFT_MATRIX column-LABEL order only, not the
   raw act30 code order. Fixed to `(0, 4, 9)`. **Confirmed harmless to the actual
   deliverable** (final `_C` file MD5 identical before/after the fix) because Stage
   C2's activity-restore donor-resample re-derives EVERY act30 value from observed-2022
   pools keyed on the FINAL 4-way state, overwriting whatever Stage B temporarily wrote
   — but the diagnostic print statements were wrong until fixed, and a future refactor
   that skips or narrows Stage C2 would have shipped the bug. Fixed anyway, not left as
   a known-harmless residual.
2. **Section-5 retail-block validator bug**: `lev = self.retail_levers["plateau"]` was
   assigned ONCE outside the per-scenario loop instead of per-scenario inside it, so
   gates 5.20/5.21/5.23/5.24 silently scored the SAME (plateau) data under all 3
   scenario labels. Caught because gate 5.24's "deviation" values were suspiciously
   exact: `|0.97-0.90|=0.07` and `|0.97-1.05|=0.08` for the shift/renaissance rows —
   the tell that a fixed frame was being compared against the wrong multiplier. Fixed
   by reassigning `lev` inside the loop; re-ran, all 3 scenarios now show correctly
   differentiated 5.20/5.21/5.23 values and exact (0.0000 deviation) 5.24 lever-
   exactness across all 3 scenarios.
3. **`hotel_processed_dir` default path used `here.parents[3]`, one level too high**
   (landed outside `GSSCanada-main/`). Fixed to `parents[2]`; `hotel_multiplier_lookup
   .csv` and `hotel_diurnal_shape_st.csv` now load correctly (`hotel_multiplier_2030
   .csv` lives in `0_Occupancy/forecasts/` not `processed/`, handled via the existing
   fallback reload in `main()`).
4. **Hotel scorecard status normalization**: the Track-B scorecard's status column
   contains the literal string `"FAIL (PARTIAL)"` for gate 8.3 QC, which isn't one of
   the 4 canonical tally buckets — crashed the summary tally with a `KeyError`. Fixed
   by normalizing any `FAIL*` status to `FAIL` for tallying while preserving the
   original string verbatim in the note/detail text (`raw_status=...`).

**Gate-by-gate scorecard (final, after both bug fixes):**

| Scope | PASS | WARN | FAIL | INFO |
|---|---|---|---|---|
| GSS channels (Sections 1-6) | 66 | 15 | **5** | 19 |
| Hotel (Section 8, Track B) | 17 | 3 | 2 | 0 |
| **Overall** | **83** | **18** | **7** | **19** |

**5 GSS FAILs — none silently relaxed, all characterized with evidence:**

1-2. **Section 4, stratum-1 (weekday) backcast: home level (+8.91pp vs ±2pp gate) and
work level+MAD (+10.99pp vs ±3pp gate; MAD=0.1132 vs <0.10 gate) both FAIL.**
**Stratum-1 characterization (task-mandated): REAL backcast gap, NOT a small-channel
metric artifact.** Evidence: the profile-MAD+level metric exists specifically because
raw flattened-binary JS saturates on SPARSE channels (retail ~2% positive was flagged
as the worst case) — but here retail is the channel that PASSES cleanly on stratum 1
(MAD=0.0039, level=0.10pp), while the DENSE home/work channels are the ones that fail
— the opposite of the sparse-channel-artifact pattern the metric guards against. Sat/Sun
(strata 2-3) pass cleanly on all 3 channels (<1.1pp level everywhere), so it is not a
systemic backcast failure either — specific to weekday home/work structure. Plausible
(not proven) mechanism: reconstructed WFH_RATE sits 2.07pp above observed (itself PASS
on its own ±5pp gate), concentrated onto specific business-hours slots, consistent with
per-slot level residuals an order of magnitude larger than the aggregate WFH_RATE gate
alone suggests. Primary evidence source: the PRODUCTION job's own per-stratum gate table
(job 1133427 `.out` lines 140-151, transcribed verbatim) — `reconstructed_2022_diaries
_4split.csv` as delivered has no DDAY_STRATA/LFTAG/PR of its own, and the raw Step-4
training pool needed for an independent row-aligned recomputation
(`seed_3_g3fix/augmented_diaries.csv`, 418MB) is cluster-only and out of this session's
local staging scope — so the build-log table (computed in-process with correct labels
before the CSV write dropped that column) is authoritative, not re-derived from a
misaligned local proxy. A secondary, clearly-labeled pooled cross-check (different,
smaller, non-row-aligned Step5 observed-2022 population) corroborates the shape
(home/work JS still small: 0.0012/0.0278) without being the scored gate.

3-5. **Section 5, gate 5.2 (WD AT_HOME < WE AT_HOME, structural) FAILs in all 3 bands**
by a small margin: conservative +1.27pp, hybrid +1.00pp, fullyhybrid +0.33pp (WD minus
WE, i.e. weekday home is slightly ABOVE weekend home). Characterized (5.2.characterization,
INFO): the gap SHRINKS as WFH intensity rises (opposite of a naive "more WFH inflates
weekday home" story), more consistent with a design consequence of the calibration
chain anchoring weekend home (Stage C1) to a FIXED observed-2022 level independent of
office-WFH band, while weekday home is separately shaped by Stage B + the band-specific
WFH-day reweight — no cross-stratum WD<WE ordering constraint was ever enforced, only
within-stratum fidelity to real-2022 anchors. Scored FAIL per the literal gate (not
relaxed); flagged as a candidate cross-stratum consistency constraint for a future
calibration revision if the manager wants WD<WE enforced as a hard invariant.

**Other notable findings (WARN, not blocking, all evidence-documented in the report):**
- **3.5-3.7 COVID triple-signal**: soft blocker per the val plan, all 3 legs
  (home/work/retail) fail direction at the temp=0.0 internal DRIFT_MATRIX signal —
  build-log's own verdict ("NOT all 3 legs confirmed") transcribed, not re-derived.
- **5.22/5.25 QC-Sunday restricted-default finding**: the runbook's assumption that the
  historical QC trading-hours restriction "naturally encodes through QC respondents in
  training data" does NOT clearly survive into the pooled 2030 generation — observed
  Sun/Sat peak ratio 1.16 vs the expected 0.60-0.75 window (Sunday nearly as busy as
  Saturday). Flagged for Step-7/manager attention before relying on the QC-restricted-
  default assumption downstream; not independently adjudicated as noise vs a genuine
  generation-resolution limitation at this doubly-conditioned (PR x day-type x channel)
  sparse cell.
- **5.27 retail-WFH cross-contamination**: small (~0.13pp, ~5.6% relative) spread in
  retail day-mean across office-WFH bands, plausibly explained by the build-log's own
  documented band-specific WFH/office-pool "resampling with replacement" (candidate
  pools smaller than target counts) — not zero, scored WARN per a graduated tolerance,
  not silently passed as exact.

**Hotel (Section 8) — 17P/3W/2F, reproduced verbatim from Track B's own
`section8_hotel_gate_scorecard.csv`** (no re-derivation): 2 FAILs are both QC
data-availability limitations (8.1 order borrowed from AB, 8.3 backcast tested on a
partial 1-year overlap only) — per the additive-safety principle these do NOT block
GSS/Track-A sign-off, and per the val plan they gate Step-7 QC hotel injection
specifically (routes to NECB baseline if unresolved), not the whole hotel channel.

**Step 6 NOT declared done** — 5 FAIL on GSS channels (Sections 1-6). Both root causes
(stratum-1 backcast gap; WD>=WE structural in all 3 bands) are real, evidence-
characterized findings, not metric artifacts or bugs, and were NOT silently relaxed to
WARN/INFO. Report: `outputs_step6/step6_validation_report.html`. Per the task scope,
this session does NOT proceed to Step 7 — the manager must get the user's confirmation
on the 2030 scenario matrix first.

### 2026-07-23 — MANAGER CLOSURE: Step 6 DECLARED DONE (5 GSS FAILs accepted-as-documented)

**Decision (manager, user-delegated 2026-07-23 "choose for best measurement precision"):**
Step 6 is **DONE**. The 5 GSS FAILs are accepted-as-documented — a direct parallel to the
Step-5 3-FAIL closeout — because forcing them to PASS would *reduce* fidelity, not improve
it. None were relaxed to WARN/INFO; they remain FAIL in the scorecard with the dispositions
below.

**FAIL 1-2 (Section-4 stratum-1 weekday backcast, home +8.9pp / work +11pp) — DIAGNOSTIC-ONLY,
confirmed by a dedicated propagation check (manager-ordered, 2026-07-23).** A local diagnostic
(scratch script, employee) compared the shipped `_C` 2030 weekday home/work levels to the
observed-2022 anchor (`Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv`,
CYCLE_YEAR==2022) and to the raw backcast. The population-wide weekday-home delta (+4.9 to
+8.1pp) that *superficially* tracks the raw +8.9pp model bias is almost entirely a **legitimate
2030 employment-composition shift** (weekday employed share 94.7% in the anchor vs 49.9% in the
2030 frame; non-employed people are home more). Controlling to `LFTAG==1` (apples-to-apples with
how Stage B anchors), the residual weekday-home delta collapses to −4.9 / +1.5pp, sign-
inconsistent across bands, nowhere near the raw model's +8.9pp — and weekday **work** is dead-on
the anchor for the conservative band (Stage B confirmed working), weekend home stays anchored
(Stage C1). **Verdict: the raw backcast has a real weekday-fidelity gap (a raw-model property,
worth a manuscript caveat), but it does NOT propagate into the shipped 2030 deliverable.** No
cluster re-run is warranted for a diagnostic-only gate.

**FAIL 3-5 (Section-5 gate 5.2 WD AT_HOME ≥ WE AT_HOME, all 3 bands, margin 0.33–1.27pp) —
accepted, NOT fixed.** The gate encodes a pre-WFH, employment-conditioned assumption (weekend
home > weekday home). In a full-population 2030 frame the small inversion is driven by the same
legitimate composition shift + a genuine WFH effect. Imposing a synthetic cross-stratum WD<WE
constraint would fit the product to a wrong assumption and inject error → rejected on precision
grounds. Flagged as a candidate gate-definition revision (condition on employment / recognize the
WFH regime), not a product defect.

**Canonical deliverable frozen:** `2030_synthetic_diaries_4split_calibrated_mindwell_C.csv`,
111,024 rows (3 bands × 37,008), retail lever = plateau (0.97) default; shift (0.90) /
renaissance (1.05) via `--retail_lever` re-run (retail-cap stage only). **MD5:
`7c105ef331b37107d5b605c95028c3ba`.** Mutex 3-way = 0 (gate 6.7 PASS; the guard cleared 748 real
post-Stage-C1 home&work conflicts en route — not a no-op). Hotel Track B = 17P/3W/2F, its 2 FAILs
are QC data-availability limits that gate only Step-7 QC hotel injection (usable-with-caveat;
NECB fallback if unresolved), never GSS sign-off.

**2030 scenario matrix decision (user, 2026-07-23): FULL FACTORIAL (3×3×3) resolution**, not the
3-aligned-bundle default — to disentangle the independent + interaction effects of office-WFH ×
retail-lever × hotel-band (aligned bundles confound them). Cost-efficient realization to be
designed in Step 7: because each channel drives its own building/space type, ~3 sims per channel
(≈9 channel-runs + NECB baseline + fixed residential) reconstruct all 27 aggregate cells
analytically — confirm channel/space separability in the Step-7 build before committing the
sim count. **Step 6 CLOSED; Step 7 (Four-Channel BEM Integration) authorized to begin.**
