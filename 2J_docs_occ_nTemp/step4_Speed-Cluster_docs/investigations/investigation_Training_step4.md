# Step-4 Training Investigation — F → G → H → I retrospective

This report consolidates the four architecture lineages of the Step-4 GSS Conditional Transformer (the model that produces 30-min household-occupancy diaries for BEM) into a single timeline with per-axis outcomes. Each lineage closed with at least one hard gate failing, and the per-series strengths are different — G-series carried AT_HOME / Spouse / act_JS, H-series cleaned binary-head calibration, and the I-series synthesis arm regressed instead of winning. The question this document answers: **why did I-series regress despite folding G + H wins onto a non-autoregressive trunk, and what does the consolidated record say about the next move?**

This document is intended to be self-contained for an outside reviewer (including external LLMs). The next section provides the project context, the dataset definitions, and the Step-4 task statement, so the F → G → H → I architectural narrative that follows can be read without opening any of the source files.

---

## 0. Project context (read this first if external)

### 0.1 What this project does

End-to-end pipeline name: **Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM** — *Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)*. Source overview: `00_GSS_Occupancy_Pipeline_Overview.md`.

The pipeline ingests Statistics Canada **General Social Survey (GSS) Time Use** microdata across four cycles (2005, 2010, 2015, 2022), harmonizes the activity / location / co-presence taxonomies into a single schema, augments the diaries with a Conditional Transformer to fill in missing day-types, links the augmented diaries to Census household archetypes, fine-tunes / forecasts to 2030, and emits 30-minute occupancy schedules for **EnergyPlus-class Building Energy Models (BEM)** and Urban BEM (UBEM). The end consumer is residential energy simulation — every output schedule must be 30-min, must distinguish Weekday / Saturday / Sunday, and must contain AT_HOME and per-activity occupancy probabilities.

Pipeline steps (Step 4 is the subject of this report):

| Step | Purpose | Status |
|---|---|---|
| 1 — Data Collection | Pull GSS Main + Episode files for the 4 cycles | COMPLETE |
| 2 — Harmonization | Crosswalk activity codes (→ 14 categories), location codes (→ 18 + AT_HOME binary), co-presence columns (→ 9 unified binary) | COMPLETE |
| 3 — Merge + Resolution | Episode → respondent-level wide format; tile to 144 × 10-min slots; downsample to 48 × 30-min slots | COMPLETE |
| **4 — Conditional Transformer Augmentation** | Generate the 2 missing DDAY_STRATA per respondent | **THIS REPORT** |
| 5 — Census Linkage | Classical ML to assign Census records to GSS archetypes | PENDING |
| 6 — Progressive Fine-Tuning + 2030 Forecast | Fine-tune across cycles, project forward | PENDING |
| 7 — BEM/UBEM Integration | Schedule:Compact for EnergyPlus, CSV per archetype × climate zone × DDAY_STRATA | PENDING |

### 0.2 The Step-4 problem statement

Source: `04_augmentationGSS.md`.

After Step 3, every respondent in the dataset has **exactly one observed diary day**, on one of three day-types (`DDAY_STRATA ∈ {1=Weekday, 2=Saturday, 3=Sunday}`). The respondent count is **64,061 post-`DIARY_VALID` filter** (2005: 19,221 / 2010: 15,114 / 2015: 17,390 / 2022: 12,336). Each diary is 48 × 30-min slots covering 04:00–03:50 next day.

Step 4 trains a **Conditional Transformer Encoder-Decoder** that takes one observed diary + the respondent's demographics and **generates synthetic schedules for the two unobserved day-types**. Final output: ~192,183 diary-days (64,061 × 3 strata), each carrying 48 activity tokens (14-class) + 48 AT_HOME tokens (binary) + 9 × 48 co-presence tokens (binary).

**Why this matters for BEM:** EnergyPlus needs Weekday / Saturday / Sunday schedules per building archetype. Real survey data only gives one day per respondent; without augmentation, every BEM run would be missing two-thirds of its occupancy schedule signal.

### 0.3 Datasets — inputs and outputs

**Source taxonomies** (from Step 2 harmonization):

- **Activity (`occACT`) — 14 unified categories** (`02_harmonizationGSS_actCodes.md`). Crosswalk built from a 4-sheet Excel workbook (one sheet per cycle), zero conflicts. The 14 categories: 1 Work & Related / 2 Household Work & Maintenance / 3 Caregiving & Help / 4 Purchasing Goods & Services / 5 Sleep & Naps & Resting / 6 Eating & Drinking / 7 Personal Care / 8 Education / 9 Socializing / 10 Passive Leisure / 11 Active Leisure / 12 Community & Volunteer / 13 Travel / 14 Miscellaneous / Idle. **Internal tensors are 0-indexed** (`raw - 1`); CSVs store the 1-indexed raw value.
- **Location → AT_HOME** (`02_harmonizationGSS_pre_coPre.md`, Part A). Location codes from the four cycles (PLACE for 2005/2010, LOCATION for 2015/2022) are mapped to an 18-category `occPRE` scheme. AT_HOME is derived as `(occPRE == 1)` (Home). All other locations including travel, work, school, restaurant, etc. are AT_HOME = 0.
- **Co-presence — 9 unified binary columns** (`02_harmonizationGSS_pre_coPre.md`, Part B): `Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`, `colleagues`. GSS encodes 1 = present / 2 = absent — recoded to 1 / 0 internally. **`colleagues` is 100% NaN for 2005/2010** (`TUI_06I` was not collected); the primary 8 columns also carry non-trivial NaN at the episode level (~20% in 2005, ~19.3% in 2010, ~0.1% in 2015, ~6.8% in 2022). NaN slots are masked out of the BCE loss via a per-slot availability mask `cop_avail[respondent, slot, col]` built during 04A dataset assembly.

**Step 3 outputs (Step 4 inputs)** — sourced from `03_mergingGSS.md`:

| File | Location | Rows × Cols | Content |
|---|---|---|---|
| `hetus_30min.csv` | `outputs_step3/` | 64,061 × 120 | 48 activity slots `act30_001..048` (1-indexed 1–14) + 48 AT_HOME slots `hom30_001..048` (binary) + ~24 demographic / metadata columns (occID, AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, TOTINC, HRSWRK, NOCS, COW, DDAY_STRATA, CYCLE_YEAR, COLLECT_MODE, TOTINC_SOURCE, WGHT_PER, …) |
| `copresence_30min.csv` | `outputs_step3/` | 64,061 × 433 | 9 co-presence columns × 48 30-min slots each (`{ColName}30_001..048`) + occID. Original GSS encoding: 1=present, 2=absent, NaN=missing. |

The 30-min slots come from majority-voting three consecutive 10-min HETUS slots; AT_HOME breaks ties as 1 > 0; activity ties resolve to the longest continuous run.

**Step 4 intermediate artifacts** (per `04_augmentationGSS.md` §"Intermediate artifact schemas"):

- `step4_train.pt` / `step4_val.pt` / `step4_test.pt` — PyTorch tensor dicts, stratified split (70/15/15) by occID across CYCLE_YEAR × DDAY_STRATA. Tensors:
  - `act_seq` `long(N, 48)` — 0-indexed activity tokens
  - `aux_seq` `float(N, 48, 10)` — per-slot AT_HOME + 9 co-presence binary
  - `cond_vec` `float(N, d_cond)` — encoded demographics (one-hot + continuous), `d_cond` measured at runtime (76 on the production dataset)
  - `cycle_idx` `long(N,)` — 0..3 for {2005, 2010, 2015, 2022}
  - `obs_strata` `long(N,)` — observed DDAY_STRATA
  - `cop_avail` `bool(N, 48, 9)` — availability mask for masked BCE
- `training_pairs.pt` / `val_pairs.pt` — for each respondent × target stratum, **K=5 demographic-nearest neighbors** observed on that target stratum (within the same CYCLE_YEAR). Exact match on AGEGRP / SEX / MARSTH / HHSIZE / LFTAG; fuzzy (±1 bin) on PR / CMA / HRSWRK / NOCS / TOTINC. At training time, one of the K neighbors is sampled per respondent per epoch as the supervision target — this is how a respondent with one observed day generates supervision for the two unobserved days.
- `step4_feature_config.json` — runtime encoding dimensions, used by 04B / 04D / 04E.

**Step 4 final outputs** (per `04_augmentationGSS.md` §"OUTPUT FILES"):

| File | Location | Content |
|---|---|---|
| `best_model.pt` | `outputs_step4_<TAG>/checkpoints/` | Best checkpoint by val score |
| `augmented_diaries.csv` | `outputs_step4_<TAG>/` | ~192,183 rows × ~552 cols. Columns: occID, CYCLE_YEAR, DDAY_STRATA, IS_SYNTHETIC (0=observed, 1=generated), full demographic passthrough, WGHT_PER, `act30_001..048` (1-indexed), `hom30_001..048`, all 9 × 48 co-presence columns. `colleagues30_*` is NaN for 2005/2010 observed rows and 0 for 2005/2010 synthetic rows. |
| `step4_validation_report.html` | `outputs_step4_<TAG>/` | 04F validation: 8 sections covering training curves, JS divergence per cycle × stratum, AT_HOME rates, temporal structure, co-presence prevalence, demographic conditioning, cross-stratum consistency, summary stats. |
| `diagnostics_J_<TAG>.json` | `outputs_step4_<TAG>/` | 04J statistical diagnostics — bootstrap CIs on AT_HOME / co-presence gaps, calibration curves, joint distributions, χ² / KS tests, **composite score** `S = 0.20·AT_HOME_rms/10 + 0.35·cop_max_gap_pp/10 + 0.35·act_JS·10 + 0.10·cop_cal_MAE·10`. The composite is the gate the F-series and onward optimize against. |

### 0.4 The Step-4 task as a learning problem

- **Input:** one observed 48-slot diary (activity + AT_HOME + 9 co-presence) + demographic conditioning vector + observed DDAY_STRATA + target DDAY_STRATA.
- **Output:** a 48-slot diary on the target DDAY_STRATA.
- **Supervision:** the diary of a demographically-similar same-cycle respondent who was actually observed on that target DDAY_STRATA (K=5 neighbors, one sampled per epoch).
- **Losses:**
  - 14-way Cross-Entropy on activity per slot (`λ_act`, default 1.0)
  - BCE on AT_HOME per slot (`λ_home`, 0.5–0.7 depending on series)
  - Masked BCE on co-presence per slot per channel (`λ_cop`, default 0.3) — masked by `cop_avail` AND by the colleagues-2005/2010 hard-zero
  - Optional marginal-bias term (`λ_marg`) and aux stratum-prediction head (`AUX_STRATUM_HEAD`, λ=0.1)
- **Evaluation:** Jensen-Shannon divergence per (cycle × stratum) on activity; ±pp gap on AT_HOME and per co-presence channel; the composite score above. All gates are evaluated on the **autoregressive generation path**, not teacher-forced.

### 0.5 Why this problem is hard (relevant for the F → G → H → I narrative below)

Three structural difficulties drive the entire architectural lineage that follows:

1. **DDAY_STRATA imbalance — 72.8% Weekday / 13.6% Saturday / 13.6% Sunday.** Generating Weekday from a Weekend source has abundant supervision; the reverse direction (which is the dominant inference task) has scarce supervision. This drives the H1 hypothesis in the F-series investigation and the proportional-sampling change in G1.
2. **Autoregressive feedback amplification.** The Step-4 spec uses an AR decoder (slot-by-slot generation, previous AT_HOME fed back). Once `home_head` saturates (σ > 0.70 for most slots, observed in F-series job 901177), every feedback step pushes the next slot toward AT_HOME=1 — small per-slot biases compound across the 48-slot diary. Tier-1.6 teacher-forced inference (2026-05-04) confirmed the AR cascade is the residual gate-blocker: composite drops 1.48 → **0.54** when the decoder is fed ground-truth AT_HOME instead of its own previous output.
3. **Conditioning collapse.** The decoder is supposed to use demographics + cycle + target DDAY_STRATA via FiLM modulation. FiLM modules are zero-initialized (start as identity); if the BCE / CE gradient on the decoder body dominates the FiLM gradient, the decoder converges on a corpus-average output and ignores the conditioning. The G3 cross-attention rewrite was the structural fix for this.

These three difficulties — H1 (data imbalance), H3 (AR feedback), H4 (conditioning collapse) — are the H-numbered hypotheses cited throughout the F-series investigation. The F → G → H → I lineage below is, in effect, the story of progressively addressing each of them.

---

## Hard gates

Inherited verbatim across F / G / H / I, evaluated on full validation set:

- composite < 1.045
- AT_HOME ≤ +5.3 pp
- Spouse ≤ +5 pp
- act_JS ≤ 0.05

The composite gate has **never** been cleared by any production run. Best-ever is G4 at 1.256. H-Tier-1.6 (zero-training falsification, teacher-forced inference on G4 / H_Tanh checkpoints) showed composite ≈ 0.54 is achievable when the AT_HOME channel is fed ground truth — the gate is not unreachable, the AR cascade is the residual blocker.

## Architecture lineage table

One row per architecturally-distinct snapshot. `Speed_Cluster/archive/` carries the frozen `04B_model.py` for each tag.

| Tag | Trunk | Decoder | Conditioning | PE | Heads | Loss / training notes | Archive file |
|---|---|---|---|---|---|---|---|
| F-final (F10a) | 6-layer encoder, AR | 6-layer `nn.TransformerDecoder` w/ FiLM per layer | additive `strata_linear` + FiLM(`cond_vec ‖ cycle_emb ‖ strata_oh`) | fixed sinusoidal | linear (sigmoid for binary) | fp16 on, hand-tuned λ, Work×5/Transit×3/Social×2 boosts, AUX_STRATUM_HEAD=1, SPOUSE_NEG_WEIGHT=0.45 | `04B_model_G1.py` (= F-final inherited by G1) |
| G1 | identical to F-final | identical | identical | identical | identical | **config-only**: proportional target sampling in `04C` (55.6 / 22.2 / 22.2 WD/Sat/Sun) | `04B_model_G1.py` |
| G2 | identical to G1 | identical | identical | identical | identical | + `SCHED_SAMPLE_P=0.2` slot-dropout on AT_HOME teacher-forcing channel + `HOME_LABEL_SMOOTH=0.05` on home BCE | `04B_model_G2.py` |
| G3 | 6-layer encoder, AR | rewritten `CrossAttnDecoder` (self-attn → cross-attn over enc memory → cross-attn over 3 cond tokens → FFN) | three separate cond tokens for cross-attn (no FiLM, no `strata_linear`) | fixed sinusoidal | linear | d_model 256→384, d_ff 1024→1536, sched_sample_p=0.2, label_smooth=0.05 | `04B_model_G3.py` |
| G4 | identical to G3 | identical to G3 | identical to G3 | identical | identical | **config-only**: `sched_sample_p=0.0`, `lambda_home=0.6` | `04B_model_G4.py` |
| H_Tanh | identical to G4 | identical to G4 | identical to G4 | identical | `Linear → Tanh → Linear → Sigmoid` on home + cop heads (env-var `H_TANH_HEADS=1`) | `lambda_home=0.7` | `04B_model_H_Tanh.py` |
| H_Time | identical to H_Tanh | identical to H_Tanh + `learnable_pe nn.Parameter(1,48,d_model)` and `cyclical_time` (sin/cos 2πt/48) buffer added to decoder input | identical | learnable PE replaces fixed sinusoidal in decoder; encoder PE untouched | identical to H_Tanh | env-var `H_TIME_PE=1`, `lambda_home=0.6` | `04B_model_H_Time.py` (= `pre_HNAT`) |
| H_NAT | G4 encoder (unchanged) | **2-layer non-causal `nn.TransformerEncoder` refinement** (no decoder, no AR loop, no `bos_token`) | encoder cond unchanged; no decoder cond | encoder PE unchanged | three parallel `Linear(d_model, K)` heads applied to all 48 refined slots in one shot | `model_type=H_NAT`, fp16 retained, no per-slot fusion folded back in | `04B_model_H_NAT.py` (= `pre_I1`) |
| I1 | **single 6-layer `nn.TransformerEncoder`** (port of `examples/cloud_computing/Transformer_pipeline.py`) | none — no decoder, no AR, no causal mask | **per-slot fusion** at every t∈[0,48): tod + dow + slot-idx embeds + source-diary act + broadcast `cond_vec` + cycle + strata_oh, projected to d_model | `nn.Embedding(48, d_model)` learnable | `Linear → Tanh → Linear → Sigmoid` on home + cop; `Linear → Softmax` on activity (14-class); single `model.infer()` returning all three in one pass | masked Spouse BCE (`reduction='none'` × `(home_target==1)`); fp16 OFF; `clip_grad_norm_(25)`; `ReduceLROnPlateau(factor=0.95, patience=5)`; `lambda_home=0.6`, `spouse_neg_weight=1.0`, `home_label_smooth=0.0` | `04B_model_pre_I1.py` |
| J1 | 6-layer encoder, **Hybrid AR-Encoder** | **Arm 1:** G4 `CrossAttnDecoder` reused (activity-only AR, no AT_HOME feedback). **Arm 2:** per-slot NAT fusion (memory + `act_seq.detach()` + cond_vec + cycle_emb + strata_oh) → `arm2_proj` → parallel binary heads | encoder cond unchanged; Arm 1 cond identical to G4; Arm 2 receives Arm-1 activity as a fixed (detached) feature | sinusoidal | `Linear → Tanh → Linear → Sigmoid` (parallel NAT) on home + cop; `Linear → CE (14)` AR on activity; clip-only Spouse at inference (revert I1's masked BCE) | fp16 OFF; `clip_grad_norm_(25)`; `ReduceLROnPlateau(factor=0.95, patience=5)`; `lambda_home=0.7`, `spouse_neg_weight=0.45`, `home_label_smooth=0.05`; `act_seq.detach()` between arms (softmax probs at train, one-hot at inference) | `04B_model_pre_J1.py` |

## Per-stage outcomes (timeline table)

One row per training run. Numbers from `results_index/results.csv` and the v2 / v3 progress logs. Tier-1.6 rows are inference-only on existing checkpoints (no training).

| Date | Tag | Composite | AT_HOME pp | Spouse pp | act_JS | cop_cal_MAE | Gates | Verdict |
|---|---|---|---|---|---|---|---|---|
| 2026-04-21 | F1 baseline | 1.045 (note: pre-composite-recalc reference; later F-rows use composite formula) | +5.3 | (Alone +16.1) | 0.056 | — | 0/4 | F-final baseline; structural §3 AT_HOME bias |
| 2026-04-25 | F7 | 1.364 | +11.14 | +20.27 | 0.041 | 0.340 | 0/4 | first valid post-NaN-fix run; Spouse explosion |
| 2026-04-26 | F8 | 1.376 | +1.41 ✅ | +19.36 | 0.066 | 0.330 | 1/4 | AUX_STRATUM_HEAD isolated; AT_HOME best-of-F |
| 2026-04-26 | F9b | 1.481 | — | −3.5 ✅ | — | — | partial | Spouse zero-crossing overshoot |
| 2026-04-28 | F10a | 1.306 | +6.98 | +1.60 ✅ | 0.069 | — | 1/4 | F-series CLOSED; structural floor |
| 2026-04-29 | G1 | 1.345 | +6.22 | +0.95 ✅ | 0.068 | — | 1/4 | proportional sampling; H1 not the driver |
| 2026-04-30 | G2 | 1.217 | +5.46 | +15.39 | 0.054 | 0.333 | 0/4 | sched_sample broke Spouse |
| 2026-05-01 | G3 | 1.228 | +6.06 | +19.77 | **0.024 ✅** | 0.331 | 1/4 | cross-attn first cleared act_JS |
| 2026-05-02 | G4 | **1.256** | +5.66 | **+1.71 ✅** | **0.030 ✅** | 0.320 | **2/4** | best composite to date; AT_HOME miss 0.36 pp |
| 2026-05-02 | H4 | 1.754 | +15.08 | −11.13 | 0.061 | — | 0/4 | equal λ regressed everything |
| 2026-05-02 | H6 | 1.977 | +20.22 | −5.32 | 0.056 | — | 0/4 | dropping activity boosts blew out AT_HOME |
| 2026-05-03 | H_Tanh | 1.319 | **+5.19 ✅** | **−3.07 ✅** | **0.029 ✅** | 0.324 | **3/4** | best-of-H; only 3/4 ever; composite +0.063 vs G4 |
| 2026-05-04 (TF) | G4 / Mode A | 1.480 | +6.45 | −3.52 | — | — | — | inference-only sanity, AR baseline |
| 2026-05-04 (TF) | **G4 / Mode B** | **0.540** | **−2.1 ✅** | **~0 ✅** | **~0.010 ✅** | — | **4/4 (ceiling)** | teacher-forced; composite ceiling proof |
| 2026-05-04 (TF) | G4 / Mode C | 1.361 | +2.23 | −2.5 | — | — | partial | oracle home only; cop AR cascade unmoved |
| 2026-05-04 (TF) | H_Tanh / Mode A | 1.540 | +5.29 | −7.82 | — | — | — | inference-only sanity |
| 2026-05-04 (TF) | H_Tanh / Mode B | 0.536 | −2.1 ✅ | ~0 ✅ | ~0.010 ✅ | — | 4/4 (ceiling) | identical pattern to G4 |
| 2026-05-04 | H_Time | 1.321 | +5.68 | +0.64 ✅ | 0.023 ✅ | 0.326 | 2/4 | learnable PE regressed AT_HOME |
| 2026-05-04 | H_NAT | (worst H run; act_JS 6–9× H_Tanh; val_score 0.106 vs H_Tanh 0.042) | noisy 0.09–0.13 | — | ≈0.055–0.069 | — | 0/4 | NAT trunk fidelity failure; fp16 grad explosions |
| 2026-05-05 | **I1 (official 04J)** | **1.192** | **+7.59 ✗** | **+9.16 ✗** | **0.135 ✗** | **0.247** | **0/4** | **synthesis arm REGRESSED; ship H_Tanh** |
| 2026-05-06 | **J1 (official 04J)** | **0.6927 ✅** | **+5.83 ✗ (RMS, fail by 0.53)** | **−1.9 ✅** | **0.0274 ✅** | **0.234** | **3/4** | **Hybrid AR-Encoder; AT_HOME sole miss; composite 45% better than H_Tanh; J2 triggered (lambda_home 0.7→0.90)** |

## Per-stage training-time loss / per-output proxy table

Companion to the gate table above. Source: `outputs_step4_<TAG>/step4_training_log.csv` best-epoch rows (pulled locally to `2J_docs_occ_nTemp/training_logs/<TAG>_training_log.csv`). Best epoch is the row with minimum `val_score` in the CSV. These are the **teacher-forced per-output training-time losses** the trainer wrote each epoch and used for checkpoint selection — they live on a different axis than the autoregressive gate pp/JS metrics in the previous table, and they routinely *disagree* with it (H_Tanh and H_Time have the best per-head training losses of any run but composite worse than G4 — see "Reading guide" below).

Column key. `act_loss` = activity-head Cross-Entropy (14-class softmax CE, per-slot mean over the val set, teacher-forced). `home_loss` = AT_HOME-head Binary Cross-Entropy (per-slot mean, teacher-forced; under `home_label_smooth=0.05` the BCE has a label-smoothed floor near ~0.20 — see caveat below). `cop_loss` = co-presence-head BCE (mean over 9 channels, teacher-forced, masked by `cop_avail`). `marg_loss` = marginal-bias auxiliary term `|σ(home_logits).mean() − home_tgt.mean()|` (G-series onward in `per_cs` mode). `val_JS` = activity Jensen-Shannon divergence on the val set (gate-axis equivalent: `act_JS`). `home_gap` = AT_HOME mean absolute fraction-of-slots gap (×100 ≈ pp; gate-axis equivalent: `AT_HOME pp`). `val_score` = combined checkpoint-selection metric (`val_JS + 0.5·home_gap`). "—" = no CSV available locally; "INVALID" = run saved an untrained / near-uniform checkpoint (FP16 NaN, warmup-trap, sign-flip pos_weight) so per-epoch values are non-diagnostic.

| Tag | Best ep | act_loss (CE) | home_loss (BCE) | cop_loss (BCE) | marg_loss | val_JS | home_gap | val_score |
|---|---|---|---|---|---|---|---|---|
| F1 (job 901055, production) | — | — | — | — | — | — | — | — |
| F-Option-B (sign-flip retrain, job 901399) | 1 (warmup-trap) | 2.298 | 0.559 | 0.419 | 0.0175 | 0.0756 | 0.113 | 0.132 |
| F-Option-B end of training (ep 16) | 16 | 0.838 | 0.143 | 0.097 | 0.0037 | 0.224 | 0.211 | 0.329 |
| F2–F6 | INVALID | — | — | — | — | — | — | — |
| F7 | 89 | 0.5996 | 0.1083 | 0.0894 | 0.0046 | 0.0627 | 0.1681 | 0.1468 |
| F8 | 93 | 0.5305 | 0.1072 | 0.0883 | 0.0018 | 0.0688 | 0.1171 | 0.1273 |
| F10a | 95 | 0.5243 | 0.1064 | 0.0820 | 0.0020 | 0.0643 | 0.1438 | 0.1362 |
| G1 | 65 | 0.5424 | 0.1129 | 0.0815 | 0.0017 | 0.0594 | 0.1434 | 0.1311 |
| G2 | 92 | 0.4824 | 0.1048 | 0.0862 | 0.0016 | 0.0387 | 0.1527 | 0.1151 |
| G3 | 60 | **0.1909** | **0.0505** | 0.0847 | 0.0017 | 0.0091 | 0.0771 | 0.0477 |
| G4 | 67 | **0.0715** | 0.2214 | 0.0645 | 0.0022 | 0.0097 | 0.0740 | 0.0467 |
| H_Tanh | 58 | 0.0851 | 0.2265 | 0.0675 | 0.0022 | **0.0080** | 0.0841 | **0.0508** |
| H_Time | 58 | 0.0770 | 0.2154 | **0.0624** | 0.0013 | 0.0079 | 0.0952 | 0.0555 |
| H_NAT | 34 | 1.5613 | 0.5007 | 0.2280 | 0.0118 | 0.0621 | 0.0878 | 0.1060 |
| I1 | 67 | 1.4118 | 0.4168 | 0.2369 | 0.0116 | 0.0558 | 0.0735 | 0.0925 |
| J1 | 60 | 0.1028 | 0.3596 | 0.1943 | 0.0089 | **0.0044** | **0.0256** | **0.0171** |

Reading guide / per-head observations.

- **Activity CE collapses dramatically at G3 onwards (G2 0.482 → G3 0.191 → G4 0.072 → H_Tanh 0.085 → H_Time 0.077)**, then explodes back to 1.41–1.56 in the NAT-trunk runs (H_NAT, I1). The cross-attention decoder (G3+) plus removal of scheduled sampling (G4+) drove activity CE down ~20× vs F-series; the encoder-only NAT trunk (H_NAT, I1) gave it all back. This is the same signal that the gate-axis `act_JS` metric reports (G4 0.030 ✅ → I1 0.135 ✗) but on a different scale.
- **Home BCE has a label-smoothed floor near ~0.20 from G4 onwards** (`home_label_smooth=0.05` makes targets {0.05, 0.95}, whose Bernoulli entropy is ~0.20 — even a perfect predictor cannot drive BCE below that). G4 / H_Tanh / H_Time (0.221 / 0.227 / 0.215) sit right at this floor — they are calibration-saturated. G3's anomalously low home_loss (0.0505) is because G3 still ran with `sched_sample_p=0.2`, which corrupts the AT_HOME teacher-forcing channel during training and shifts the effective loss target distribution; G3 home_loss is therefore not directly comparable to G4+. H_NAT (0.501) and I1 (0.417) are both well above the floor — the NAT trunk fails to learn AT_HOME calibration to the same standard as the AR decoder.
- **Cop BCE is roughly stable 0.06–0.09 across G/H runs**, then jumps to 0.23 under the NAT trunk (H_NAT, I1). Same architectural failure mode as the activity head — the encoder-only refinement has insufficient capacity to learn 9-channel co-presence BCE per slot in parallel.
- **Marg loss is consistently small** (0.001–0.012) and not the load-bearing signal for any decision; it tracks the AT_HOME marginal-rate calibration directly.

Reading guide / cross-table.

Lower `val_score` does **not** track lower composite. The H_Tanh / H_Time pair holds the best activity CE among the AR-trunk runs (0.085 / 0.077) and the best `val_JS` (~0.008), but their composites (1.319 / 1.321) are *worse* than G4's (1.256). I1 has a *better* `val_score` (0.0925) than F7 (0.1468) but a *worse* gate-axis composite (1.192 vs F7-era band) — the per-head training losses do not predict the autoregressive cascade error that dominates the gate composite. Tier-1.6 measured the same H_Tanh and G4 checkpoints under teacher-forced inference (Mode B) at composite **0.540** (G4) / **0.536** (H_Tanh), a ~3× spread vs Mode A — proving the per-head training proxies live on the teacher-forced axis (their cousin) and the gates live on the AR axis. For decisions about which checkpoint to ship, the per-stage *gate* table above is the load-bearing one; this table is the "what the optimizer thought it was doing" record, useful for diagnosing *where* the AR cascade diverges from teacher-forced (which output head saturates first, which trunk fails to descend, where the label-smoothing floor is hit).

## Per-stage architecture and training-config table

Source: `2J_docs_occ_nTemp/configs/<TAG>.yaml` (G/H/I-series), with F-series values reconstructed from `04_augmentationGSS_hpc.md` Progress Log (F-series predates the YAML refactor). Each row is the exact config the trainer ran, split into two sub-tables for readability: (A) trunk / capacity / head shape; (B) loss weights / training-loop knobs / regularization. Where a field was not yet introduced at a given stage (e.g. `sched_sample_p` before G2, `h_tanh_heads` before H_Tanh), the cell shows "n/a". Where a config knob was the **single delta** vs the predecessor row, it is **bolded** to make the per-stage axis visible at a glance.

### A. Trunk, capacity, decoder topology, heads, positional encoding

| Tag | Trunk / decoder | d_model | n_heads | d_ff | n_enc | n_dec | PE | Home/cop heads | Activity head | aux_stratum_head |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | 6-enc + FiLM AR decoder | 256 | 8 | 1024 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 0 |
| F7 | 6-enc + FiLM AR decoder | 256 | 8 | 1024 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | **1** |
| F8 | 6-enc + FiLM AR decoder | 256 | 8 | 1024 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 1 |
| F10a | 6-enc + FiLM AR decoder | 256 | 8 | 1024 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 1 |
| G1 | 6-enc + FiLM AR decoder | 256 | 8 | 1024 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 1 |
| G2 | 6-enc + FiLM AR decoder | 256 | 8 | 1024 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 1 |
| G3 | 6-enc + **CrossAttn AR decoder** | **384** | 8 | **1536** | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 1 |
| G4 | 6-enc + CrossAttn AR decoder | 384 | 8 | 1536 | 6 | 6 | sinusoidal | Linear → Sigmoid | Linear → CE (14) | 1 |
| H_Tanh | 6-enc + CrossAttn AR decoder | 384 | 8 | 1536 | 6 | 6 | sinusoidal | **Tanh → Linear → Sigmoid** | Linear → CE (14) | 1 |
| H_Time | 6-enc + CrossAttn AR decoder | 384 | 8 | 1536 | 6 | 6 | **learnable + cyclical sin/cos(2πt/48)** | Tanh → Linear → Sigmoid | Linear → CE (14) | 1 |
| H_NAT | 6-enc + **2-layer non-causal refinement** (no AR) | 384 | 8 | 1536 | 6 | **0** (refinement_layers=2) | sinusoidal (enc only) | Linear → Sigmoid (parallel) | Linear → CE (14, parallel) | **0** |
| I1 | **single 6-enc, no decoder** (per-slot fusion) | 384 | 8 | 1536 | 6 | **0** | **learnable nn.Embedding(48, d_model)** | Tanh → Linear → Sigmoid (parallel) | Linear → Softmax (14, parallel) | 0 |
| J1 | 6-enc + **CrossAttn AR (Arm 1)** + **per-slot NAT fusion (Arm 2)** | 384 | 8 | 1536 | 6 | **6** | **sinusoidal** (revert I1 learnable PE) | Tanh → Linear → Sigmoid (parallel NAT, Arm 2) | Linear → CE (14, AR, Arm 1) | 0 |

### B. Loss weights, training-loop knobs, regularization, precision

| Tag | λ_act | λ_home | λ_cop | λ_marg | marg_mode | spouse_neg_w | cop_pos_w | activity_boosts | sched_sample_p | home_label_smooth | aux_stratum_λ | precision | lr | batch | max_ep | patience |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | 1.0 | 0.5 | 0.3 | 0.1 | global | 1.0 | 0 | 1 (Work×5/Trans×3/Soc×2) | n/a | n/a | 0.1 | **fp16** | 5e-5 | 256 | 100 | 15 |
| F7 | 1.0 | 0.5 | 0.3 | 0.1 | **per_cs** | 1.0 | 0 | **0** | n/a | n/a | 0.1 | **fp32** | 5e-5 | 256 | 100 | 15 |
| F8 | 1.0 | 0.5 | 0.3 | 0.1 | global | 1.0 | 0 | 1 | n/a | n/a | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| F10a | 1.0 | 0.5 | 0.3 | 0.1 | global | **0.45** | 0 | 1 | n/a | n/a | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| G1 | 1.0 | 0.5 | 0.3 | 0.1 | global | 0.45 | 0 | 1 | 0.0 | 0.0 | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| G2 | 1.0 | 0.5 | 0.3 | 0.1 | global | 0.45 | 0 | 1 | **0.2** | **0.05** | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| G3 | 1.0 | 0.5 | 0.3 | 0.1 | global | 0.45 | 0 | 1 | 0.2 | 0.05 | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| G4 | 1.0 | **0.6** | 0.3 | 0.1 | global | 0.45 | 0 | 1 | **0.0** | 0.05 | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| H_Tanh | 1.0 | **0.7** | 0.3 | 0.1 | global | 0.45 | 0 | 1 | 0.0 | 0.05 | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| H_Time | 1.0 | **0.6** | 0.3 | 0.1 | global | 0.45 | 0 | 1 | 0.0 | 0.05 | 0.1 | fp32 | 5e-5 | 256 | 100 | 15 |
| H_NAT | 1.0 | 0.7 | 0.3 | 0.1 | global | 0.45 | 0 | 1 | 0.0 | 0.05 | 0.1 (unused) | fp32 | 5e-5 | 256 | 100 | 15 |
| I1 | 1.0 | **0.6** | 0.3 | 0.1 | global | **1.0** | 0 | 1 | 0.0 | **0.0** | 0.1 (unused) | fp32 + **clip_grad_norm=25**, **ReduceLROnPlateau(0.95, p=5)** | 5e-5 | 256 | 100 | 15 |
| J1 | 1.0 | **0.7** | 0.3 | 0.1 | global | **0.45** | 0 | 1 | 0.0 | **0.05** | 0.1 (unused) | fp32 + clip_grad_norm=25, ReduceLROnPlateau(0.95, p=5) | 5e-5 | 256 | 100 | 15 |

Reading guide.

- **Capacity bumps once** (G3: d_model 256→384, d_ff 1024→1536, ~2.4× decoder param count). All H/I runs inherit the 384/1536 capacity.
- **Trunk/decoder topology changes only three times** in the entire F→I lineage: G3 (FiLM → CrossAttn), H_NAT (CrossAttn AR → 2-layer non-causal refinement), I1 (refinement → single encoder, no decoder). Everything else is config-only.
- **Single-axis edits** are visible by the bolded cells: F1→F7 changes 3 axes (per_cs marg, no boosts, fp32) — that bundle is *why* F7 was hard to attribute; F8 isolated AUX_STRATUM_HEAD as the load-bearing axis. F10a → G1 is purely a `data_dir` change (proportional pairs); G1→G2 introduces sched_sample + label_smooth (single axis bundle, both target H3); G2→G3 is the CrossAttn rewrite; G3→G4 removes sched_sample and bumps λ_home; G4→H_Tanh is a 2-line head wrap (+ λ_home 0.6→0.7); H_Tanh→H_Time changes PE only.
- **I1 violated the one-axis-per-arm rule** — bundled three changes vs H_Tanh: trunk (CrossAttn AR → encoder-only NAT), Spouse loss formulation (clip-only → masked BCE with `spouse_neg_weight=1.0`), and label smoothing removal (`home_label_smooth=0.05 → 0.0`). This is the v3 doc's H-I-C hypothesis: we cannot disambiguate trunk-driven Spouse failure from loss-formulation-driven Spouse failure in the I1 result alone.
- **Field-introduction order** (the "n/a" cells): `sched_sample_p` and `home_label_smooth` were introduced at G2 (first two rows show "n/a"); `h_tanh_heads` was introduced at H_Tanh (rows above implicitly = 0); `h_time_pe` was introduced at H_Time. Default values (zero / off) are byte-for-byte equivalent to the absent field, so back-filling rows above with 0/0/0/0 is also valid — "n/a" is just more honest about *when each axis became part of the search space*.

## What each series contributed (the user's framing, refined)

The user's intuition is essentially correct — G-series carried AT_HOME / Spouse / act_JS, H-series cleaned binary-head calibration — but the precise allocation matters because it informs why I-series should have won and didn't.

- **G-series — closed the AT_HOME / Spouse / act_JS axis with cross-attention.** G3 was the first run in the entire history to clear act_JS (0.024 ≤ 0.05). G4 (G3 architecture + `sched_sample_p=0.0` + `lambda_home=0.6`) cleared **both Spouse (+1.71 pp ✅) AND act_JS (0.030 ✅)** and posted the best composite ever recorded (1.256). AT_HOME missed by only 0.357 pp. The load-bearing change is the cross-attention decoder over the three conditioning tokens `[cond_vec, cycle_emb, strata_oh]` — replacing the additive `strata_linear` + FiLM path. Removing scheduled sampling (which had blown Spouse from 0.95 pp at G1 to 19.77 pp at G3) was the second decisive move.
- **H-series — calibration on top of G's architecture.** H_Tanh wraps the home + cop heads with `Tanh` before the linear projection, on the G4 trunk, with `lambda_home=0.7`. Result: **3/4 gates** — AT_HOME +5.19 pp ✅, Spouse −3.07 pp ✅, act_JS 0.029 ✅, composite 1.319 (regressed by 0.063 vs G4). H-Tier-1.5 diagnostic refuted the bounding-artefact hypothesis: H_Tanh val BCE on home is **lower** than G4 (0.2209 vs 0.2284), and confidence regimes are nearly identical — so the composite regression is not a head-shape problem. H_Time (learnable PE + cyclical features) regressed AT_HOME back to 5.68 pp (2/4). H_NAT (NAT trunk replacement, parallel encoder + 2-layer non-causal refinement) failed catastrophically: act_JS 0.055–0.069 vs H_Tanh's 0.029, four `grad_norm=inf` events, val_score 2–2.5× worse than H_Time. Root cause was **fidelity, not concept** — the build kept fp16, omitted per-slot conditioning fusion, and stacked a non-causal refinement layer on top of an already-bidirectional encoder (functionally redundant).
- **I-series — synthesis arm, expected to win, regressed instead.** I1 ported `examples/cloud_computing/Transformer_pipeline.py` faithfully (per-slot fusion of tod/dow/slot/src-act/cond/cycle/strata, learnable PE `nn.Embedding(48, d_model)`, three parallel heads in one forward pass, single `model.infer()`) and folded in G4 (`lambda_home=0.6`) + H_Tanh (Tanh-bounded binary heads) + masked Spouse BCE (`reduction='none'` × `(home_target==1)`) + ReduceLROnPlateau + clip_grad_norm 25 + fp16 forced off. Smoke passed cleanly (act_loss 1.788 → 1.681 over 5 epochs, grad_norm finite throughout). Full train completed (early stop ep82, best val_score 0.0925, no NaN). Official 04J: **0/4** — composite 1.192, AT_HOME RMS 7.59 pp ✗, Spouse +9.16 pp ✗ (5.4× H_Tanh), act_JS 0.135 ✗ (4.5× H_Tanh). **Worse than H_NAT on the activity axis.**

## Why I1 regressed — hypotheses, ranked

Five hypotheses, ranked by evidence strength. Each names a falsification path.

### H-I-A: sequence-length / cross-architecture mismatch (rank: strongest)

**Mechanism.** Reference pipeline reshapes 5-min data into **24 slots**; GSS Step-4 is **48 slots**. Per-slot fusion at twice the sequence length under the same `d_model=384` may under-condition each position. Gemini reviewer flagged this as the #1 H_NAT regression risk on 2026-05-04; the same risk class applies to I1.

**Evidence.** I1 smoke act_loss DID descend (1.788 → 1.681 over 5 epochs), proving the architecture trains. But the floor at full train (val_JS 0.0558 at best epoch) sits in the same band as H_NAT's failure floor (0.055–0.069), not H_Tanh's 0.029. Both NAT-style trunks hit the same act_JS floor regardless of fidelity to the reference, suggesting an architectural ceiling for parallel heads at 48-slot sequence length.

**Falsification path.** Re-run I1 with the reference's 24-slot reshape (concatenate slot pairs). If act_JS recovers to ≤0.05 while keeping per-slot fusion, sequence-length is confirmed. If act_JS stays at 0.13, this hypothesis is rejected.

### H-I-B: loss of the joint-sequence prior (same root cause as H_NAT)

**Mechanism.** Encoder-only NAT eliminates the AR conditioning that enforces temporal consistency. Tier-1.6 Mode B proved AR cascade ERRORS hurt — but the AR conditioning STRUCTURE was implicitly carrying activity-sequence quality (sleeping at t→t+1, work blocks, commute transitions). Both H_NAT and I1 discarded the conditioning along with the cascade. Without an AR feedback channel, parallel-head prediction generates each slot from global encoder context only, with no explicit transition prior.

**Evidence.** I1 act_JS 0.135 vs H_Tanh 0.029 (4.5×) is the same magnitude as H_NAT's regression. Both NAT runs broke activity-sequence quality; both kept the binary heads functional.

**Falsification path.** Add a small step-to-step transition loss (predict `act_t+1 | act_t, encoder_output`) on top of the I1 trunk — closes part of the AR loop without re-introducing the cascade. If act_JS drops, this is the load-bearing failure.

### H-I-C: Spouse masked-loss formulation under-trains the rare class (axis-bundled with the trunk change)

**Mechanism.** I1 changed Spouse from clip-only at inference (`cop_pred *= (home_pred > 0.5)`) to **BCE-with-mask at training** (`F.binary_cross_entropy_with_logits(reduction='none')` × `(home_target == 1)`, mean over masked positions only). With `spouse_neg_weight=1.0` (vs 0.45 in G/H), the Spouse=0 | home=1 negative class may be under-weighted relative to the positive — predicting "spouse home" everywhere becomes locally optimal under a balanced BCE on the masked subset.

**Evidence.** Spouse gap exploded from +1.71 pp (G4) and −3.07 pp (H_Tanh) to +9.16 pp (I1). The masked-loss + `spouse_neg_weight=1.0` change was bundled with the architectural change, violating the one-axis-per-arm rule that the v2 doc set explicitly. We cannot disambiguate trunk-driven Spouse failure from loss-formulation-driven Spouse failure in the I1 result alone.

**Falsification path.** Run I1 once more with `spouse_neg_weight=0.45` and clip-only Spouse (drop the masked BCE), holding the trunk fixed. If Spouse recovers to ≤5 pp, this is the dominant cause and the Spouse loss formulation is the issue, not the trunk.

### H-I-D: lambda_home choice (0.6 vs 0.7) under the encoder-only trunk

**Mechanism.** I1 picked G4's `lambda_home=0.6` over H_Tanh's `lambda_home=0.7`. Tier-1.6 confounder analysis confirmed H_Tanh's 0.7 is part of why H_Tanh's AT_HOME passes the gate. Under a fundamentally different trunk (encoder-only NAT), the optimal `lambda_home` is unknown — copying G4's value was an assumption.

**Evidence.** I1 AT_HOME RMS 7.59 pp vs G4's 5.66 pp under the same `lambda_home=0.6`. Same scalar weight, worse AT_HOME → the trunk is more sensitive to home-loss weighting than the AR decoder was.

**Falsification path.** Repeat I1 with `lambda_home=0.7`, holding everything else fixed. If AT_HOME drops below 5.3 pp, the assumption is the issue.

### H-I-E: inference-path drift (audit candidate, weak)

**Mechanism.** 04E `hasattr(model, "infer")` dispatch was added pre-flight, but the masked Spouse loss + Tanh heads + softmax activity head + parallel inference path was assembled fresh — there is no equivalence test against G4 / H_Tanh on a fixed val batch. Possible silent metric-evaluation mismatch (e.g., act_JS computed over a different distribution shape than the AR reference).

**Evidence.** Weak — 04J ran the same statistical battery as H_Tanh, no schema mismatch surfaced, all six metrics populated. Treat as audit candidate, not primary cause.

**Falsification path.** Re-run 04E + 04J on H_Tanh under the same code revision used for I1. If H_Tanh's published numbers reproduce, drift is rejected.

## What we got at the end

**Production checkpoint:** `outputs_step4_H_Tanh/checkpoints/best_model.pt`.

**Gate row:** composite 1.319, AT_HOME +5.19 pp ✅, Spouse −3.07 pp ✅, act_JS 0.029 ✅, cop_cal_MAE 0.324. **3/4 gates** — the only run in the entire F → G → H → I record to clear three of four.

**Composite gap:** 1.319 vs gate 1.045, miss = 0.274. Tier-1.6 confirmed the AR cascade is the residual blocker; perfect-feedback ceiling is composite ≈ 0.54.

**State of Step-4 work:** F-series closed at F10a (2026-04-28), G-series closed at G4 (2026-05-02), H-series closed at H_NAT (2026-05-05), I-series closed at I1 (2026-05-05). Two-week H-series budget exhausted. **Step-4 ships H_Tanh with documented composite caveat. Step-5 (occToBEM + EnergyPlus) is unblocked.**

## Open questions / candidate next moves

1. **BEM impact of the composite caveat.** Composite 1.319 vs gate 1.045 may or may not matter once H_Tanh schedules drive EnergyPlus. The right next test is the Step-5 simulation with H_Tanh, not another Step-4 architectural arm. If BEM passes, the composite gap is academic.
2. **If a further architectural arm IS justified after Step-5,** the unexplored axes are:
   - **Hybrid AR-encoder.** Keep G4's AR decoder for activity (preserves the joint-sequence prior that I1 / H_NAT lost), bolt I1's per-slot fusion onto its inputs. Gains the conditioning fix without discarding temporal consistency.
   - **24-slot reshape under I1.** Direct test of H-I-A. Concatenate adjacent slot pairs to halve sequence length, re-run I1. Cheapest single experiment to falsify the architectural-floor hypothesis.
   - **Post-hoc cop AR refinement on G4.** Tier-1.6 Mode C showed oracle-home alone does NOT close cop_maxgap (25 pp → 25 pp). The cop AR cascade is the dominant residual. A small post-hoc `(home, act) → cop` refinement on G4's outputs targets the right axis.
3. **Spouse loss formulation isolation.** Masked-BCE vs. clip-only is unbenchmarked head-to-head on the same trunk. If a future arm runs, isolate this axis FIRST (one variable per arm, the rule that I1 violated).
4. **04E / 04J drift audit.** Re-run H_Tanh through the I1-revision code and confirm published numbers reproduce. Rules out H-I-E without spending GPU time.

## References

- F-series investigation: `Speed-Cluster_docs/DONE/DONE_step4_training.md`
- G-series + H-series record: `Speed-Cluster_docs/DONE/DONE_step4_training_v2.md`
- I-series record: `Speed-Cluster_docs/step4_training_v3.md`
- Operations log (F1 → F10a closure, infrastructure): `04_augmentationGSS_hpc.md`
- Frozen architecture snapshots (one `04B_model.py` per tag): `Speed_Cluster/archive/`
- Reference architecture (encoder-only proof-of-existence): `examples/cloud_computing/Transformer_pipeline.py`
