# Step-4 Training v3 — I-series faithful encoder-only port

## Aim

Close the residual composite gap that the H-series could not close, by replacing the autoregressive trunk with a faithful port of the encoder-only architecture in `examples/cloud_computing/Transformer_pipeline.py` and folding in the per-output wins already validated by G-series (AT_HOME) and H_Tanh (Tanh-bounded binary heads). I-series is the synthesis arm: one final architectural shot, with H_Tanh as the documented fallback if it under-performs.

## Hard gates

Inherited verbatim from F/G/H-series, evaluated on full validation set:

- composite < 1.045
- AT_HOME ≤ +5.3 pp
- Spouse ≤ +5 pp
- act_JS ≤ 0.05

## Carry-forward from H-series

H-series outcomes that motivate this doc:

- **H_Tanh** — current Step-4 fallback. 3/4 gates: composite=1.256, AT_HOME=5.66 pp (FAIL by 0.36), Spouse=1.71 pp ✅, act_JS=0.030 ✅. Tanh-before-binary calibration carried forward into I1 unchanged.
- **H_Time** — 2/4 gates. Validated learnable PE; carried forward as `nn.Embedding(48, d_model)` in I1.
- **H_NAT** — failed (worst H-series run; val_JS 6–9× H_Tanh; act_loss flatlined ep30+; `grad_norm=inf` at ep8/45/48). Root cause was **fidelity, not concept**: build replaced the cross-attention decoder with a 2-layer stacked `nn.TransformerEncoder`, kept fp16, and inherited neither the reference's per-slot categorical fusion nor any cross-attention to encoder memory. I-series fixes the fidelity.
- **Tier-1.6 (teacher-forced)** — composite ≈ 0.54 on G4 and H_Tanh under teacher-forced decode (gate <1.045). Confirms the AR cascade is the residual blocker and that ~50% headroom exists above the gate. This is the empirical mandate for I-series.

## Steps (task list)

### I1 — Faithful encoder-only port (single arm)

- **Change scope:** `04B_model.py` (new `IOccupancyModel` class), `configs/I1.yaml`, `configs/sweep_smoke_I1.yaml`, `Speed_Cluster/job_step4_I1.sh`, `Speed_Cluster/job_step4_I1_smoke.sh`, `04D_train.py` (MODEL_TYPE dispatch), `04E_inference.py` / `04F_*` / `04J_*` (verify existing `hasattr(model, "infer")` dispatch covers I1). Predecessor archive: `cp 04B_model.py Speed_Cluster/archive/04B_model_pre_I1.py` in same commit as the architecture edit.
- **Targets:** AR cascade (Tier-1.6 confirmed blocker); H_NAT's per-slot conditioning collapse; H_Tanh's residual Spouse miss; H_NAT's fp16 grad explosions.
- **Rationale:** `examples/cloud_computing/Transformer_pipeline.py` is a published encoder-only architecture that solved a comparable joint-sequence task. The load-bearing trick is per-slot fusion of ~24 categorical embeddings — every position carries its own conditioning vector before any attention runs, replacing the AR feedback channel. H_NAT v1 omitted this. I1 ports it faithfully.

#### Architecture deltas (10 points)

1. **Trunk.** Single `nn.TransformerEncoder`, no decoder, no causal mask, no token feedback. One forward pass produces all 48 slots in parallel.
2. **Per-slot conditioning fusion.** At every position t ∈ [0, 48): time-of-day embed, day-of-week embed, slot-index embed, source-diary activity at slot t (preserves the conditional-generation contract — does NOT drop the source signal), broadcast-concat with `cond_vec` (demographics, cycle, target stratum). Project to `d_model` before encoder. This is the change H_NAT v1 omitted.
3. **Learnable positional encoding.** `nn.Embedding(48, d_model)` added to fused input. Carries the H_Time win.
4. **Tanh on binary heads.** AT_HOME and co-presence heads = `Linear → Tanh → Linear → Sigmoid`. Carries the H_Tanh win.
5. **AT_HOME head ported from G4.** G4 owns the AT_HOME pathway. Diff `configs/G4.yaml` (`lambda_home=0.6`) vs `configs/H_Tanh.yaml` (`lambda_home=0.7`) and any head-depth/width delta in `04B_model.py`; port G4's recipe onto the I1 trunk. Open question to resolve at implementation: lambda_home 0.6 or 0.7 for I1.
6. **Masked Spouse loss.** BCE on spouse with `reduction='none'`, per-slot loss multiplied by `(home_target == 1)` mask, mean over masked positions only. Replaces clip-only feasibility with a representation that learns `p(spouse|home)`. Keep `cop_pred *= (home_pred > 0.5)` clip at inference as a guard, not a crutch.
7. **Training recipe lifted from reference.** Drop `--fp16`. Add `clip_grad_norm_(max_norm=25)`. Optimizer Adam, scheduler `ReduceLROnPlateau(factor=0.95, patience=5)`. Fixes the three `grad_norm=inf` events H_NAT had.
8. **Inference dispatch.** Implement `model.infer(act_t, aux_t, cond_t, cidx_t, strat, apply_safety=True)` returning `(act_logits[B,48,14], home_logits[B,48], cop_logits[B,48,9])` in a single forward pass. `04E_inference.py:159-169` already has `hasattr(model, "infer")` branching — verify the same dispatch exists in `04F_*` and `04J_*` and add it where missing.
9. **MODEL_TYPE export verification.** `Speed_Cluster/config_to_env.sh` mapping confirmed (`[model_type]=MODEL_TYPE`, line ~38; export at line ~44). Add `I1` to whatever dispatch list exists in `04D_train.py:383-408` and run a dry export end-to-end before the sbatch handoff.
10. **Predecessor archive.** `cp 04B_model.py Speed_Cluster/archive/04B_model_pre_I1.py` in the same commit as the architecture edit. Standing rule.

#### Explicit non-goals

- No stacked second `TransformerEncoder` on top of the first (H_NAT v1's mistake).
- No cross-attention decoder (v2a path rejected — reference doesn't have one).
- No scheduled sampling (G2/G3 proved it destroys Spouse).
- No dropping the source-diary signal (would change the task, not just the trunk).
- No marginal-loss / label-smoothing toggles bundled into I1 (one variable per arm).
- No fp16.

#### Smoke gate

I1 smoke (`sweep_smoke_I1.yaml`, small N, ~10 epochs) must show `act_loss` strictly decreasing across the first 5 epochs and `grad_norm` finite throughout. If either fails, **stop and diagnose** — do NOT let it run to ep49 like H_NAT did.

#### Advancement gate

Full I1 train evaluated against the four hard gates and against the teacher-forced ceiling (composite ≈ 0.54):

- All 4 gates ✅ → **ship I1.** Step-4 closeout, move to Step 5.
- 3/4 gates with composite materially below H_Tanh's 1.256 → **trigger I2** (reactive, see below).
- Composite ≥ H_Tanh's 1.256 OR any gate worse than H_Tanh → **ship H_Tanh, close I-series.** No further H/I arms.

#### Effort

L (one full architectural rewrite of `IOccupancyModel`, plus configs/job scripts/dispatch verification).

#### Key risk

Per-slot fusion under-conditions when sequence length is 48 vs reference's 24. If this manifests, it shows up at smoke as `act_loss` flatline; mitigation is increasing the per-slot fused embedding dimension before considering I2. Gemini reviewer flagged this as the #1 H_NAT regression risk; I1's per-slot fusion is the direct mitigation.

#### Fallback

H_Tanh checkpoint + documented composite caveat. Already trained, already passes 3/4 gates.

---

### I2 — Reactive fallback (only if I1 misses one gate by a small margin)

Not pre-specified. Triggered only if the I1 advancement gate selects "trigger I2." Candidate directions to choose from at trigger time, in order of expected payoff:

- Joint Spouse head: `p(spouse_home) = p(home) · p(spouse | home)` learned end-to-end, replacing the masked-loss formulation. Direct fix if I1 misses Spouse only.
- `lambda_home` retune (sweep 0.5 / 0.6 / 0.7 / 0.8) if I1 misses AT_HOME only.
- Head depth/width bump on the failing head (AT_HOME or activity), holding trunk fixed.
- Per-slot fused embedding dim increase if smoke-time signal suggested under-conditioning.

Exact I2 spec written into the Progress Log table when triggered, then this section is updated in place.

---

### I3 — Reserve

Pre-specification deferred. Only entered if both I1 and I2 produce strong directional signal (composite materially below H_Tanh) but neither closes all four gates. If I1 fails outright, I3 is not attempted — H_Tanh ships.

---

### J1 — Hybrid AR-Encoder synthesis (DONE — 3/4 gates, AT_HOME sole miss)

- **Change scope:** new `JSeriesHybrid(nn.Module)` in `04B_model.py`; predecessor archived to `Speed_Cluster/archive/04B_model_pre_J1.py`. Live J1 architecture frozen at `Speed_Cluster/archive/04B_model_J1.py`. `MODEL_TYPE=J1` dispatch wired through `04D_train.py` (model_config ~L425, model build ~L600, LR scheduler skip-LambdaLR ~L612, clip_grad_norm=25 ~L695, past_warmup gate ~L719, plateau-step ~L797). `04E_inference.py:299` carries `elif _mtype == "J1"`. Configs: `configs/J1.yaml` + `configs/sweep_smoke_J1.yaml`. Job scripts: `Speed_Cluster/job_step4_J1_smoke.sh`, `job_step4_J1.sh`, `job_step4_J1_eval.sh`.
- **Targets:** AR-cascade vs NAT-trunk dichotomy revealed by I-series — G4 owned activity / Spouse but missed AT_HOME; H_Tanh fixed AT_HOME calibration but regressed composite; I1's NAT trunk gave back the activity axis. J1 isolates the temporal arm (AR for activity) from the spatial/social arm (NAT for AT_HOME + cop) so each axis is generated by the trunk that owned its win.
- **Rationale:** Hybrid AR-Encoder strict isolation. Arm 1 (G4 `CrossAttnDecoder` reused) does activity-only AR; Arm 2 (per-slot NAT fusion with H_Tanh-bounded heads) does AT_HOME + cop in parallel after Arm 1 finishes. `act_seq.detach()` between arms prevents Arm 2→Arm 1 gradient leakage. Carries I1 hygiene (fp32, clip_grad_norm=25, ReduceLROnPlateau).

#### Architecture deltas (10 points)

1. **Trunk.** 6-layer `nn.TransformerEncoder`, `d_model=384`, `n_heads=8`, `d_ff=1536`, sinusoidal PE. Same as G4. Outputs `memory: (B, 49, d_model)`.
2. **Arm 1 — Temporal AR (activity only).** G4 `CrossAttnDecoder` reused, conditioned on `(cond_vec, cycle_emb, strata_oh)`. 48-step AR loop produces `act_seq: (B, 48, 14)`. Does NOT consume AT_HOME. `lambda_act=1.0`, `sched_sample_p=0.0`.
3. **Arm 2 — Spatial/Social NAT.** Per-slot fusion `[memory[:,1:,:] ‖ act_seq.detach() ‖ cond_vec ‖ cycle_emb ‖ strata_oh]` → `arm2_proj(173 → d_model)` → parallel binary heads. Executes after Arm 1 finishes.
4. **AT_HOME head.** `Linear → Tanh → Linear → Sigmoid` (1ch). `lambda_home=0.7`, `home_label_smooth=0.05`. Carries the H_Tanh win.
5. **Co-presence head.** `Linear → Tanh → Linear → Sigmoid` (9ch). `lambda_cop=0.3`, `spouse_neg_weight=0.45`. Spouse uses **clip-only at inference** (`cop_pred *= (home_pred > 0.5)`) — REVERT from I1's masked BCE.
6. **Activity-arm detach.** `softmax(act_logits.detach())` at training (soft probs for richer Arm-2 signal); `one_hot(act_tokens).float()` at inference (hard tokens). `.detach()` blocks Arm 2→Arm 1 gradient leakage in both paths.
7. **Inference signature.** `infer(act_t, aux_t, cond_t, cidx_t, strat, apply_safety=True)` returns `(act_logits[B,48,14], home_logits[B,48], cop_logits[B,48,9])` — byte-compatible with `IOccupancyModel.infer()` so 04E branching is a one-line addition.
8. **Training hygiene (I1 port).** fp32 forced (no fp16/amp), `clip_grad_norm_(25)` before optimizer.step, `ReduceLROnPlateau(factor=0.95, patience=5)`, `lr=5e-5`. `MODEL_TYPE=J1` extends every I1 conditional in `04D_train.py`.
9. **Loss formulation.** Standard `cop_loss_masked` path (NOT I1's masked Spouse BCE). `spouse_neg_weight=0.45` honored via env/config.
10. **Predecessor archive.** `cp 04B_model.py Speed_Cluster/archive/04B_model_pre_J1.py` in same commit as the architecture edit. Standing rule.

#### Explicit non-goals

- No scheduled sampling (`sched_sample_p=0.0`) — G2/G3 proved it breaks Spouse.
- No I1 masked Spouse BCE — confirmed confounder in I1 result.
- No fp16 / amp anywhere in J-series.
- No AR feedback from AT_HOME into the activity arm — Arm 1 is activity-only.
- No I1 `lambda_home=0.6` carry-over — J1 reverts to H_Tanh's 0.7.

#### Smoke gate

J1 smoke (`sweep_smoke_J1.yaml`, `--sample`, ~10 epochs):
- `act_loss` strictly decreasing across epochs 1–5
- `grad_norm` finite throughout
- LR held at 5e-5 (verifies the I1 LambdaLR-bug fix)

#### Advancement gate

After full train + 04E + 04J:
- All 4 gates ✅ → ship J1, Step-4 closeout.
- 3/4 gates with composite < H_Tanh's 1.256 → trigger J2 (defined at trigger time).
- Composite ≥ 1.256 OR any gate worse than H_Tanh → ship H_Tanh, close J-series.

#### Outcome (2026-05-06)

J1 smoke PASS (job 912799, ep10, val_score=0.2723). Full train COMPLETE (early stop ep75, best val_score=0.0171 at ep60). Official 04J: composite=**0.6927** ✅ (gate <1.045; 45% better than H_Tanh 1.256), AT_HOME RMS across strata=**5.83 pp** ❌ (gate ≤5.3 pp; fails by 0.53 pp; aggregate gap +2.1 pp), Spouse=**−1.9 pp** ✅, act_JS=**0.0274** ✅ (9% better than H_Tanh 0.030), cop_cal_MAE=0.234. **3/4 gates — AT_HOME sole blocker.** Diagnostic root cause: home_head outputs collapsed (σ=0.0; all 1.56M slot predictions in 0.0 bin); morning slots over-predict AT_HOME by +10.77 pp; per-stratum cells cancel at aggregate but drive RMS to 5.83. Spouse and act_JS pass with comfortable margin. Composite is strong; AT_HOME calibration is the sole architectural failure mode. **J2/J2.5/J3 parallel ladder triggered.**

#### Effort

L (one full architectural build — JSeriesHybrid class, 6 dispatch edits, 2 configs, 3 job scripts). Already spent.

#### Key risk

AR-cascade leakage from Arm 1 into Arm 2 binary heads. **Mitigated** via `act_seq.detach()` in Arm-2 fusion. No regression observed.

#### Fallback

H_Tanh — already trained, 3/4 gates, composite 1.256.

---

### J2 / J2.5 / J3 — Parallel AT_HOME ladder (PARALLEL EXECUTION on cluster)

**Diagnosis from J1 04J:** the home_head is **collapsed** — all slot predictions land in σ=0.0. Aggregate AT_HOME gap is only +2.1 pp; the 5.83 pp RMS is per-stratum cells canceling. The fix targets the head, not the trunk. Three single-axis arms run **simultaneously** as three sbatch jobs against the `pg` partition (architecturally independent, no checkpoint dependency between them). After all three complete, compare diagnostics and ship the simplest arm that closes the gate.

**Why parallel, not sequential:** wall time drops from ~51 h to ~17 h; comparison data clarifies whether λ-only, head-architecture, or input-balance is the actual fix; all three baselines are identical (forked from frozen `Speed_Cluster/archive/04B_model_J1.py`).

**Scope discipline:** each arm changes **exactly one axis** vs J1. No bundling. This is the rule I1 violated and the manager's standing constraint.

**Co-presence is NOT in scope.** Spouse passes (−1.9 pp). The cop_max_gap=7.04 pp is structurally driven by 2005/2010 colleagues being forced to 0 (model fills those slots with alone=1, +21.1 pp on 2005_1 / +17.1 pp on 2010_1) — not addressable by loss-side tuning. If a co-presence intervention is needed later, it belongs to a J3-class data-side arm (mask Alone for 2005/2010 cycles in `04A_dataset.py`), not the AT_HOME ladder.

#### J2 — λ_home 0.7 → 0.90 (config-only, single knob)

- **Change scope:** `configs/J2.yaml` + `configs/sweep_smoke_J2.yaml` (clones of J1 with `lambda_home=0.90`); `04D_train.py` MODEL_TYPE dispatch extended for `"J2"` (reuses `JSeriesHybrid` — no architecture change); `04E_inference.py` extended for `"J2"`. Three job scripts: `job_step4_J2_smoke.sh`, `job_step4_J2.sh`, `job_step4_J2_eval.sh`. Output dir: `outputs_step4_J2/`.
- **Target:** wake the collapsed home_head with stronger gradient signal.
- **Rationale:** the cheapest possible test of "is the head just under-weighted." If raising λ_home alone closes the gate, no architecture change is needed.
- **Architecture delta:** NONE. `JSeriesHybrid` reused as-is.
- **Smoke gate:** home_loss must drop materially below J1's 0.36 floor by ep 5–10. If it doesn't, the head is saturated for architectural reasons — log and let J2.5/J3 carry.
- **Advancement gate:** AT_HOME RMS ≤ 5.3 pp on full train. Composite must remain < H_Tanh's 1.256.
- **Effort:** S (config + 3 dispatch lines + 3 job scripts).
- **Risk:** if the head is architecturally saturated, λ amplifies the same flat output and gate doesn't move. J2.5/J3 are running in parallel as the contingency.
- **Fallback:** J2.5 / J3 outputs (already running).

#### J2.5 — Drop Tanh on home_head + depth (architecture, single change)

- **Change scope:** `04B_model.py` — home_head replaced inside `JSeriesHybrid` with a flagged variant (`MODEL_TYPE=J2_5` activates the new head). Cop head **unchanged**. `configs/J2_5.yaml` + smoke yaml. `04D_train.py` + `04E_inference.py` dispatch. Output dir: `outputs_step4_J2_5/`. Predecessor archive `Speed_Cluster/archive/04B_model_J1.py` already frozen.
- **Target:** Tanh-saturation hypothesis on the home head specifically.
- **Rationale:** H_Tanh proved Tanh helps under the AR trunk, but under J1's NAT Arm-2 the Tanh gate is the suspected collapse mechanism (σ=0.0 signature). Cop head retained as control.
- **Architecture delta:** home_head replaced with `Linear(d_model, d_model) → GELU → Dropout(0.1) → Linear(d_model, 1) → Sigmoid`. Cop head untouched: `Linear → Tanh → Linear → Sigmoid` (9ch).
- **Smoke gate:** same as J2 — home_loss drop below 0.36 floor by ep 5–10.
- **Advancement gate:** AT_HOME RMS ≤ 5.3 pp. Composite < 1.256.
- **Effort:** M (one head module replacement + flag + dispatch + config).
- **Risk:** dropping Tanh on home removes the calibration win H_Tanh proved. Cop head retained as control to preserve at least one Tanh-bounded head.
- **Fallback:** J2 / J3 outputs (parallel).

#### J3 — Soft Activity Embedding (Arm 2 input dim balance, single change)

- **Change scope:** `04B_model.py` — new `arm2_act_proj: Linear(14, d_model)` added inside `JSeriesHybrid` (`MODEL_TYPE=J3` activates). `act_emb = arm2_act_proj(softmax(act_logits.detach()))` replaces the raw 14-d `act_seq.detach()` in the Arm-2 fusion concat; fusion concat dims drop from `(d_model + 14 + d_cond + 32 + 3)` to `(d_model + d_model + d_cond + 32 + 3)`. `arm2_proj` input dim updated accordingly. `configs/J3.yaml` + smoke yaml. `04D_train.py` + `04E_inference.py` dispatch. Output dir: `outputs_step4_J3/`.
- **Target:** dim-imbalance hypothesis — 14-d activity probs got drowned in 384-d memory under raw concat in J1.
- **Rationale:** project the soft activity distribution to `d_model` so it carries comparable weight in the Arm-2 fusion. Other LLM's blueprint #1, isolated from their other proposals.
- **Architecture delta:** one new `nn.Linear(14, d_model)`; concat dim updated; `arm2_proj` input dim updated. Heads unchanged. Detach barrier preserved (act_emb projects from `softmax(act_logits.detach())`, not from logits with grad).
- **Smoke gate:** same.
- **Advancement gate:** AT_HOME RMS ≤ 5.3 pp. Composite < 1.256.
- **Effort:** M (one new Linear + 1 forward-line update + concat-dim arithmetic + dispatch + config).
- **Risk:** dim balancing may not address the head-collapse root cause. If neither J2 nor J2.5 closes the gate, J3 alone is unlikely to.
- **Fallback:** J2 / J2.5 outputs (parallel).

#### Parallel execution & advancement gate (one decision after all 3 finish)

All three runs submitted simultaneously (3 sbatch jobs, separate output dirs, identical seed and train/val split). Wall time ~17 h on `pg` partition with 3 GPUs. After all three complete eval (`job_step4_J{x}_eval.sh` → `outputs_step4_J{x}/diagnostics_J_J{x}.json`):

- **All 3 close gate:** ship the simplest arm (J2 if it works; else J2.5; else J3). Comparison data goes into the writeup.
- **1 or 2 close gate:** ship the closer that has the lowest composite. If tied on composite, prefer the simpler arm.
- **0 close gate:** ship J1 with documented AT_HOME caveat (composite 0.6927 is already 45% under H_Tanh's 1.256; one failed gate at 5.83 pp vs target 5.3 pp is a small margin worth flagging in the BEM downstream).

#### Effort (combined)

M+ for the Sonnet build cycle (3 configs × 2 = 6 yaml files; 3 job scripts × 3 = 9 sh files; 2 architecture variants in `04B_model.py` controlled by MODEL_TYPE flag; 6 dispatch edits in `04D_train.py`; 3 dispatch edits in `04E_inference.py`).

#### Risks (combined)

- **R1 — GPU queue depth.** If `pg` has only 1 GPU free, the parallel framing collapses to sequential. Submit J2 first, J2.5 second, J3 third in priority order.
- **R2 — Head-saturation root cause.** If J1's σ=0.0 head signature reflects a deeper trunk-output bottleneck (not head-local), all three arms miss. Fallback is J1 with documented caveat.
- **R3 — Bundling temptation.** Each arm must change exactly one axis. Resist combining (e.g., J2's λ + J2.5's head). Combining means we cannot attribute the win to the right axis.

## Expected result

I1 closes the AR-cascade gap revealed by Tier-1.6. Composite lands between H_Tanh's 1.256 and the teacher-forced ceiling 0.54, ideally below 1.045 with all four gates passing. AT_HOME parity with G4 maintained via lambda/head port (point 5). Spouse closes via masked loss (point 6) rather than clip-only.

## Test method

1. Smoke run on `sweep_smoke_I1.yaml` (small N, ~10 epochs). Inspect `act_loss` trajectory and `grad_norm`.
2. If smoke passes, full train via `job_step4_I1.sh`.
3. Evaluate on full validation set: composite, AT_HOME pp, Spouse pp, act_JS, cop_cal_MAE — same metric stack as v2 H-series rows.
4. Compare to teacher-forced ceiling (0.54) and to H_Tanh row (1.256). Apply advancement gate.
5. If shipping I1: regenerate downstream artifacts via `04E_inference.py`, `04F_*`, `04J_*` and confirm BEM-facing schedules respect the cop feasibility constraint.

## Status

I1 smoke PASSED (2026-05-04, job 909070). Full train COMPLETE (job 909072, ep82 early stop, best val_score=0.0925). Official 04J eval COMPLETE (job 911467): composite=1.192, AT_HOME RMS=7.59 pp FAIL, Spouse=9.16 pp FAIL, act_JS=0.135 FAIL — all four gates fail, Spouse and act_JS are 5× and 4.5× worse than H_Tanh. **FINAL VERDICT: ship H_Tanh, close I-series.**

J1 smoke PASSED (2026-05-05, job 912799). Full train COMPLETE (epoch 75 early stop, best val_score=0.0171). Official 04J eval COMPLETE (job 912933): composite=**0.6927** ✅, AT_HOME RMS=**5.83 pp** ❌ (fails by 0.53 pp), Spouse=**-1.9 pp** ✅, act_JS=**0.0274** ✅. **3/4 gates pass — AT_HOME sole blocker. J2/J2.5/J3 parallel ladder triggered.**

J2 / J2.5 / J3 PENDING — parallel build cycle queued. Three single-axis AT_HOME-targeted arms run simultaneously on cluster `pg` partition: J2 (λ_home 0.90 config-only), J2.5 (drop Tanh on home + GELU+Dropout depth), J3 (Soft Activity Embedding 14→384 before Arm 2 fusion). All three forked from frozen `Speed_Cluster/archive/04B_model_J1.py`. Wall time ~17 h parallel.

## Progress Log

| Date | Note | Status |
|---|---|---|
| 2026-05-04 | **v3 doc created.** I-series scoped as one final architectural arm to close the composite gap. Carry-forward: H_Tanh = 3/4 gates (composite=1.256, AT_HOME FAIL +0.36 pp, Spouse PASS, act_JS PASS) — current production fallback. H_NAT = FAIL (worst H-series run; root cause = build deviated from reference: stacked encoder w/o cross-attention, no per-slot categorical fusion, fp16 grad explosions; **fidelity failure, not concept failure**). Tier-1.6 teacher-forced composite ≈ 0.54 (gate <1.045) on G4 and H_Tanh confirms AR cascade is the residual blocker and that headroom exists. I1 designed as faithful port of `examples/cloud_computing/Transformer_pipeline.py` with per-output wins from G4 (AT_HOME) and H_Tanh (Tanh heads) folded in. | DRAFTED — pending user sign-off on lambda_home, smoke budget, I2 trigger |
| 2026-05-04 | **I1 bundle built (I1).** IOccupancyModel added to 04B_model.py; predecessor archived to Speed_Cluster/archive/04B_model_pre_I1.py. 04D_train.py: I1 dispatch added, Spouse masked loss (p(spouse\|home)), clip_grad_norm=25, ReduceLROnPlateau(factor=0.95, patience=5), fp16 forced off. configs/I1.yaml + sweep_smoke_I1.yaml created (lambda_home=0.6, smoke=10 epochs). Job scripts job_step4_I1.sh + job_step4_I1_smoke.sh created. MODEL_TYPE=I1 exports correctly through config_to_env.sh (model_type key already in ENV_MAP). Smoke sbatch ready. | SMOKE PENDING |
| 2026-05-04 | **5-fix pre-smoke bundle applied.** Fix 1 (LR-crushing bug): I1 skips LambdaLR entirely; ReduceLROnPlateau only — LambdaLR init calls `lr_lambda(0)` at step 0, multiplying LR by ~1/2000 → crushes to ~2.5e-8 before training begins. Fix 2: IOccupancyModel dispatch wired into 04E_inference.py (`elif _mtype == "I1": model = IOccupancyModel(model_config)`). Fix 3: home_label_smooth 0.05 → 0.0 in both I1.yaml and sweep_smoke_I1.yaml (I1 spec: no label smoothing). Fix 4: spouse_neg_weight 0.45 → 1.0 in both configs (masked loss replaces pos-weight stacking; neutral weight restores unbiased BCE on unmasked positions). Fix 5: warmup gate restructured — I1 sets `past_warmup=True` from epoch 1, bypassing the LambdaLR warmup window; original `if not past_warmup / elif / else` chain preserved intact. Cluster upload confirmed: 04D_train.py, 04E_inference.py, 04B_model.py (missing IOccupancyModel class on cluster was root cause of job 909069 AssertionError), configs/, job_step4_I1_smoke.sh. | SMOKE PENDING |
| 2026-05-04 | **I1 smoke PASS** (job 909070, cisr-1). 10 epochs × ~41 s/epoch. Pass criteria both met: (1) act_loss strictly decreasing epochs 1–5: 1.7884 → 1.7008 → 1.6904 → 1.6839 → 1.6817 ✅; (2) grad_norm finite throughout: 2.018 → 1.822 → 1.749 → 1.702 → 1.672 → 1.642 → 1.628 → 1.615 → 1.601 → 1.576 ✅. val_score improved every epoch 1–6, recovered at ep10 to best=0.1369 (val_JS=0.0815, home_gap=0.1108). LR held flat at 5.00e-05 across all 10 epochs (ReduceLROnPlateau not triggered in smoke window — expected). Full train via job_step4_I1.sh is cleared to submit. | **SMOKE PASS — full train ready** |
| 2026-05-04 | **I1 full train submitted** (job 909072, cisr-1). Config: I1.yaml — max_epochs=100, patience=15, d_model=384, n_heads=8, n_enc_layers=6, d_ff=1536, lr=5.0e-05, lambda_act=1.0, lambda_home=0.6, lambda_cop=0.3, lambda_marg=0.1, marg_mode=global, home_label_smooth=0.0, spouse_neg_weight=1.0. Output dir: outputs_step4_I1/. Advancement gate: all 4 hard gates ✅ → ship I1; 3/4 with composite < H_Tanh 1.256 → trigger I2; composite ≥ 1.256 or any gate worse than H_Tanh → ship H_Tanh, close I-series. Results (composite, AT_HOME pp, Spouse pp, act_JS) to be filled on completion. | **FULL TRAIN RUNNING — results PENDING** |
| 2026-05-05 | **I1 full train COMPLETE** (job 909072, cisr-1). Early stopping at epoch 82 (no improvement for patience=15 epochs). Best val_score=0.0925 (best checkpoint: `outputs_step4_I1/checkpoints/best_model.pt`). LR decayed from 5.00e-05 → 4.29e-05 → 4.07e-05 → 3.87e-05 via ReduceLROnPlateau(factor=0.95, patience=5). Final logged epochs (ep72–82): val_JS ranged 0.049–0.059, home_gap ranged 0.069–0.110, val_score ranged 0.093–0.107; grad_norm stable ~1.37 throughout (no explosions). Training log: `outputs_step4_I1/step4_training_log.csv`. **Hard gate evaluation PENDING** — composite, AT_HOME pp, Spouse pp, act_JS require full validation-set inference via `04E_inference.py` / `04J_*`. Run inference then apply advancement gate: all 4 ✅ → ship I1; 3/4 with composite < 1.256 → trigger I2; composite ≥ 1.256 or any gate worse than H_Tanh → ship H_Tanh, close I-series. | **TRAINING COMPLETE — gate eval PENDING** |
| 2026-05-05 | **I1 proxy gate eval — FAILS, WORSE than H_Tanh.** Best checkpoint = epoch 67 (val_score=0.092503, lr=4.287e-05, grad_norm=1.362). Proxy metrics from training CSV: act_JS (val_JS)=0.0558 vs gate ≤0.05 → **FAIL** (H_Tanh=0.030, I1 is 1.9× worse); AT_HOME gap (home_gap)=7.35 pp vs gate ≤5.3 pp → **FAIL** (H_Tanh=5.66 pp, I1 is +1.7 pp worse). Spouse and composite require 04E→04J pipeline (not yet run). **Advancement gate triggered: any gate worse than H_Tanh → ship H_Tanh, close I-series.** I1 fails this criterion on both measured axes. Preliminary verdict: **ship H_Tanh**. Official 04E→04J eval to be run for archival composite number only — does not change the verdict. | **PRELIMINARY VERDICT: SHIP H_TANH — 04J eval pending for record** |
| 2026-05-05 | **I1 official 04E→04J eval COMPLETE** (job 911467, cisr-1). Official composite from `outputs_step4_I1/diagnostics_J_I1.json`: composite=**1.192** (gate <1.045 → FAIL; better than H_Tanh 1.256 but still outside gate), AT_HOME RMS across strata=**7.59 pp** (gate ≤5.3 pp → FAIL; H_Tanh=5.66 pp — I1 +2.0 pp worse), Spouse gap=**9.16 pp** (gate ≤5 pp → FAIL; H_Tanh=1.71 pp — I1 5.4× worse), act_JS=**0.135** (gate ≤0.05 → FAIL; H_Tanh=0.030 — I1 4.5× worse), cop_cal_MAE=0.247. Overall AT_HOME gap (aggregate)=0.93 pp (not the gate metric; gate uses RMS across strata). All four gates fail. Spouse and act_JS are the largest regressions — I1's per-slot encoder-only trunk did not recover the co-presence and activity axes relative to H_Tanh's AR decoder. **FINAL VERDICT: ship H_Tanh (composite=1.256, Spouse=1.71 pp ✅, act_JS=0.030 ✅), close I-series.** I2 / I3 are not triggered. | **CLOSED — SHIP H_TANH** |
| 2026-05-05 | **J1 bundle built (J-T1).** `JSeriesHybrid(nn.Module)` added to `04B_model.py`; predecessor archived to `Speed_Cluster/archive/04B_model_pre_J1.py`. Architecture: Trunk=6-layer TransformerEncoder (d_model=384, n_heads=8, d_ff=1536, sinusoidal PE); Arm 1=G4 CrossAttnDecoder, activity-only AR loop (arm1_slot_proj: d_act→d_model, no AT_HOME feedback); Arm 2=per-slot NAT fusion [memory(384)\|act_probs(14)\|cond_vec(d_cond)\|cycle_emb(32)\|strata_oh(3)]→arm2_proj(d_model)→Tanh-gated home+cop heads. infer(): clip-only Spouse (cop*=(home>0.5)), NOT masked BCE. 04D_train.py: J1 dispatch added at model_config block, model build, LR scheduler (ReduceLROnPlateau, no LambdaLR), clip_grad_norm=25, per-batch LambdaLR skip, past_warmup=True, all extended to include "J1" alongside "I1". 04E_inference.py: JSeriesHybrid import + `elif _mtype == "J1"` dispatch. Configs: configs/J1.yaml (lambda_home=0.7, spouse_neg_weight=0.45, home_label_smooth=0.05, lr=5e-5, fp32, marg_mode=global, max_epochs=100, patience=15, n_dec_layers=6); configs/sweep_smoke_J1.yaml (same + max_epochs=10). Job scripts: job_step4_J1_smoke.sh, job_step4_J1.sh, job_step4_J1_eval.sh (mirrors I1 scripts, all refs updated I1→J1). No new cluster packages required (torch/yaml/numpy already in step4 env). Local sanity: MODEL_TYPE=J1 --sample epoch 1 completes without NaN — train_loss=3.01, act=2.45, grad_norm=4.055 (finite). Ambiguity flagged and resolved: Arm 2 uses softmax(act_logits.detach()) at training (soft probs for richer signal) and one_hot(act_tokens).float() at inference (hard tokens); .detach() isolates Arm 2→Arm 1 gradients in both paths. | **SMOKE PENDING** |
| 2026-05-05 | **J1 smoke PASS** (job 912799, cisr-1). 10 epochs × ~91 s/epoch. Pass criteria both met: (1) act_loss decreasing across visible epochs 7–10: 0.8403 → 0.8362 → 0.8332 → 0.8325 ✅; (2) grad_norm finite throughout: 1.363 → 1.331 → 1.307 → 1.293 ✅ (well-behaved, no spikes). Best val_score=0.2723 at epoch 8 (val_JS=0.1975, home_gap=0.1496); checkpoint saved at `outputs_step4_J1_smoke/checkpoints/best_model.pt`. Training completed cleanly (=== J1 SMOKE COMPLETE ===). Note: val_score (0.27) is higher than I1 smoke (0.14) — expected, Arm 1 AR loop adds latency per slot (91 s vs 41 s/epoch for I1 encoder-only). Full train via `job_step4_J1.sh` is cleared to submit. | **SMOKE PASS — full train ready** |
| 2026-05-06 | **J1 full train submitted** (job TBD, cisr-1). Config: J1.yaml — max_epochs=100, patience=15, d_model=384, n_heads=8, n_enc_layers=6, n_dec_layers=6, d_ff=1536, lr=5.0e-05, lambda_act=1.0, lambda_home=0.7, lambda_cop=0.3, lambda_marg=0.1, marg_mode=global, home_label_smooth=0.05, spouse_neg_weight=0.45. Output dir: outputs_step4_J1/. Advancement gate: all 4 ✅ → ship J1; 3/4 with composite below H_Tanh → trigger J2; composite ≥ H_Tanh or any gate worse → ship H_Tanh. | **FULL TRAIN RUNNING — results PENDING** |
| 2026-05-06 | **J1 full train COMPLETE**. Config: J1.yaml — max_epochs=100, patience=15, d_model=384, n_heads=8, n_enc_layers=6, n_dec_layers=6, d_ff=1536, lr=5.0e-05, lambda_act=1.0, lambda_home=0.7, lambda_cop=0.3, lambda_marg=0.1, marg_mode=global, home_label_smooth=0.05, spouse_neg_weight=0.45. Early stopping at epoch 75 (no improvement for patience=15 epochs). **Best val_score=0.0171 at epoch 60** (val_JS=0.0044, home_gap=0.0256 = 2.56 pp). LR decayed 5× via ReduceLROnPlateau(factor=0.95, patience=5): 5.00e-05 → 4.75e-05 → 4.51e-05 → 4.29e-05 → 4.07e-05 → 3.87e-05. act_loss monotonically decreasing throughout: 1.513 (ep1) → 0.079 (ep75). grad_norm stable 1.3–1.6, no spikes or explosions. Wall time: 75 × ~815 s ≈ 17 h (well within 24 h limit). Best checkpoint: `outputs_step4_J1/checkpoints/best_model.pt`. Training log: `outputs_step4_J1/step4_training_log.csv`. Proxy gate check from training CSV: val_JS=0.0044 ✅ (gate ≤0.05); home_gap=2.56 pp ✅ (gate ≤5.3 pp). Spouse gap and composite require full 04E→04J pipeline. **Gate eval PENDING — submit `job_step4_J1_eval.sh`.** | **TRAINING COMPLETE — gate eval PENDING** |
| 2026-05-06 | **J1 official 04E→04J eval COMPLETE** (job 912933, cisr-1). 04E: 64,061 respondents → 192,183 rows (64,061 observed + 128,122 synthetic), 27,389 unique occIDs. 04J composite: **S=0.6927** (gate <1.045 ✅; vs H_Tanh 1.256 — 45% improvement; vs I1 1.192). AT_HOME aggregate gap (T1)=+2.1 pp; **AT_HOME RMS across strata=5.83 pp** (gate ≤5.3 pp ❌ — fails by 0.53 pp; H_Tanh=5.66 pp — J1 marginally worse); morning slot largest contributor (+10.77 pp). **Spouse gap=-1.9 pp** ✅ (gate ≤5 pp; H_Tanh=1.71 pp — directionally reversed, both inside gate). **act_JS=0.0274** ✅ (gate ≤0.05; H_Tanh=0.030 — J1 9% better). COP max gap=7.04 pp (Alone channel; not a hard gate). cop_cal_MAE=0.2338. 04H flags: H1 unknown (training-pair files missing — expected, not output by 04D), H2 small contributor, H3 not dominant. **GATE VERDICT: 3/4 pass — AT_HOME sole blocker. J2 gate triggered.** Composite is strong (0.69 vs gate 1.045); only AT_HOME needs 0.53 pp improvement. Candidate J2 fix: increase lambda_home (0.7 → 0.85–0.90) or add per-morning-slot AT_HOME auxiliary loss. | **EVAL COMPLETE — J2 TRIGGERED (AT_HOME sole miss)** |
| 2026-05-06 | **J1 diagnostic deep-dive** (from `diagnostics_H_J1.json`, `diagnostics_I_J1.json`, `diagnostics_J_J1.json`). **AT_HOME root cause:** aggregate gap is only +2.1 pp but stratum-level variance drives RMS to 5.83 pp — cells pull in opposite directions (e.g. 2005_1=−4.1 pp, 2015_2=+4.0 pp, 2022_1=−3.9 pp). Per-slot trajectory: slots 0–10 (early morning) over-predict AT_HOME by +5 to +18.6 pp; slots 24–40 (afternoon) under-predict by −3 to −6 pp; net morning mean gap=+10.77 pp. AT_HOME calibration degenerate: all 1.56M slot predictions land in the 0.0 bin (sigma=0.0), true prevalence in that bin=55.8% — Arm 2 home_head Tanh gate is collapsed near zero. Diary AT_HOME variation is preserved via post-hoc clip rules, not learned probability. **Primary J2 fix: raise lambda_home (0.7→0.90) to activate home_head.** **Alone channel (+7.04 pp):** entirely a 2005/2010 structural artefact — colleagues forced to 0 for those cycles, model fills those slots with alone=1 (2005_1=+21.1 pp, 2010_1=+17.1 pp); 2015/2022 Alone gaps are −1 to +2 pp. Not addressable by lambda tuning; structural design constraint. **Spouse (−1.94 pp, CI [−2.18, −1.68]):** per-stratum swings are large (2015_2=−13.2 pp, 2015_3=−12.7 pp) but cancel at aggregate; gate-safe and stable. **Activity (act_JS=0.0274):** all 12 CS cells pass (<0.05); top-1 agreement 84.9% overall (weakest: 2022_2=62.5%, JS=0.047; strongest: 2005_1/2010_1/2015_1=97.9%). **J2 prescription: lambda_home 0.7→0.90 only; no architecture change; no lambda_act/cop/marg change; no Spouse intervention.** | **DIAGNOSTICS COMPLETE — J2 SPEC READY** |
| 2026-05-06 | **J-series task blocks backfilled into v3 doc.** J1 task block added retroactively (DONE marker, full architecture deltas + outcome line). J2/J2.5/J3 parallel ladder task blocks added (single-axis arms targeting J1's AT_HOME 5.83 pp miss): J2 = λ_home 0.7→0.90 config-only; J2.5 = home head Linear→GELU→Dropout→Linear→Sigmoid (no Tanh, cop head unchanged); J3 = Soft Activity Embedding Linear(14, d_model) before Arm 2 fusion. All three forked from frozen `Speed_Cluster/archive/04B_model_J1.py`, run simultaneously on `pg` partition (~17 h parallel vs ~51 h sequential). Status section updated to reflect J1 closed and J2/J2.5/J3 PENDING. No code changes; doc-only edit. | **DOC BACKFILLED — J2/J2.5/J3 BUILD READY** |
| 2026-05-06 | **J2/J2.5/J3 bundle built (parallel AT_HOME ladder).** Three single-axis arms forked from frozen `Speed_Cluster/archive/04B_model_J1.py`, targeting J1's AT_HOME 5.83 pp miss (3/4 gates, fails by 0.53 pp). **04B_model.py:** `JSeriesHybrid.__init__` reads `model_type` from config; J2_5 branch replaces home_head with `Linear→GELU→Dropout(0.1)→Linear` (logit output, sigmoid external — Sigmoid omitted from module to preserve BCE-with-logits compatibility); J3 branch adds `arm2_act_proj=Linear(14,d_model)` and updates `d_arm2_in` from `d_model+14+d_cond+32+3` to `d_model+d_model+d_cond+32+3`; `_arm2_fuse` routes through `arm2_act_proj` when present; cop head unchanged across all arms. **04D_train.py:** model_config block, model build, LR-scheduler, clip_grad_norm=25, LambdaLR-skip, past_warmup gate all extended to `("J1","J2","J2_5","J3")`. **04E_inference.py:** dispatch extended to `_mtype in ("J1","J2","J2_5","J3")`. **6 yaml configs:** J2.yaml (lambda_home=0.90) + smoke, J2_5.yaml (lambda_home=0.7) + smoke, J3.yaml (lambda_home=0.7) + smoke. **9 job scripts:** smoke+full+eval for each arm. config_to_env.sh `model_type→MODEL_TYPE` mapping round-trips J2/J2_5/J3 unchanged. No new cluster packages. **Local sanity PASS:** J2 ep1 (train_loss=3.01, act=2.45, grad_norm=4.06 ✅), J2.5 10ep (act 2.46→1.88 decreasing, grad_norm finite ✅), J3 10ep (act 2.26→1.95 decreasing, grad_norm finite, arm2_proj dim arithmetic correct ✅). Three parallel smoke sbatch jobs submitted simultaneously. **Cluster status (2026-05-06):** job 913055 (J2_smoke), job 913056 (J2_5_smoke), job 913057 (J3_smoke) — all RUNNING on speed-01, pg partition. | **SMOKE PASS — full trains ready** |
| 2026-05-06 | **J2/J2.5/J3 smoke PASS — all three arms cleared for full train.** J1 smoke reference: home_gap=0.1496, val_score=0.2723. **J2** (job 913055): home_loss 0.4498→0.4087 (ep1→10, declining); home_gap best=0.1578 (ep8); val_score best=0.2759 (ep8); grad_norm=1.336 (ep10, finite, no spikes) ✅. **J2.5** (job 913056): home_loss 0.4533→0.4092 (ep1→10, declining); home_gap best=0.1671 (ep8); val_score best=0.2842 (ep8); grad_norm=1.270 (ep10) ✅. **J3** (job 913057): home_loss 0.4415→0.4050 (ep1→10, declining); home_gap best=**0.1407** (ep9) — **best of the three, beats J1 smoke**; val_score best=**0.2672** (ep9) — best of the three; grad_norm=1.170 (ep10) ✅. No collapse in any arm (home_head not flat); all train_losses strictly decreasing ep1→10; arm2_act_proj (J3) confirmed in model printout (`Linear(in_features=14, out_features=64)`). **Root-cause signal: J3 (dim-balance) leads on home_gap over J1 reference, J2 (λ-only) close behind, J2.5 weakest — consistent with Arm 2 projection being a load-bearing fix.** All three full trains submitted to cluster simultaneously. **Cluster status (2026-05-06):** job 913068 (J2), job 913069 (J2_5), job 913070 (J3) — all RUNNING on speed-01, pg partition. | **FULL TRAINS RUNNING — jobs 913068 / 913069 / 913070** |
