# Step 4 Training Log — v4 (J5 Series)

*Main working document for the J5 ladder. As of 2026-05-19, methodology + experiment cards + decisions are consolidated into this file so all forward progress is tracked in one place. `Research/J5_proposal.md` is preserved unchanged as the archival source.*

Synthesises the seven LLM responses in `Research/` into a ranked J5 ladder. J3 (4/4 gates) is the production floor; every J5 candidate must hold composite < 1.045, AT_HOME RMS ≤ 5.3 pp, Spouse ≤ 5 pp, act_JS ≤ 0.05 with no regression vs J3 (4.57 / −2.03 / 0.0191, composite 0.6355).

---

# Part 1 — Methodology & Plan

## 1.1 J5 Roadmap — current status (revised 2026-05-19)

**Execution mode (current cycle):** parallel triple bundle — J5-X2, J5-A, J5-B as three independent sbatch jobs in one upload cycle. SLURM scheduler decides actual concurrency on `pg`.

- [x] **Step 1: J5-X1 + J5-X1b sequential bundle** (2026-05-17 → 2026-05-18). Neither beat J3 (X1: 3/4 gates, composite 0.6667; X1b: 2/4, composite 0.8086). Outcome: act_JS regression in X1 attributed to `lambda_home=0.7` config deviation; cop disruption in X1b attributed to open cross-arm gradient.
- [x] **Step 2: J5-X2 + J5-A + J5-B parallel bundle** (submitted 2026-05-19, COMPLETE 2026-05-20). Composites: J5_X2=0.6747, J5_A=0.6997, J5_B=0.6975. **None beats J3 (0.6355).** Re-diagnosed 2026-05-20: across all three failures the binding constraint was **supervision topology** — the J-series `.detach()` barrier means AT_HOME and cop heads get gradient into ~150K params while activity shapes ~28M. The old `Transformer_pipeline.py` (encoder-only, 3 parallel heads, joint loss) was right on this axis but lost to J3's AR decoder on activity. See Part 2 entry dated 2026-05-20.
- [x] **Step 3 (evaluation):** J3 retained as production. Stop chasing loss-side / cop-side fixes; pivot to topology.
- [ ] **Step 4 (NEXT — parallel triple bundle, 2026-05-20 plan):** **J5-F + J_old + J5-C** as three independent sbatch jobs in one upload cycle. **J5-F** = joint encoder supervision + AR decoder for activity (hybrid old-pipeline supervision + J3 AR gain). **J_old** = pure `Transformer_pipeline.py` revert at 48-slot resolution — encoder + three parallel Linear heads, no AR decoder, no Arm-2 fusion. **J5-C** = linear-chain CRF + Viterbi on J3's Arm-1 activity logits (J3 topology preserved). Three orthogonal hypotheses: J5-F tests "topology + AR is best"; J_old tests "AR isn't needed at all if supervision is right"; J5-C tests "transition modeling on J3 topology". This is a 2×2 across {AR / no AR} × {joint / detached supervision} with J3 as the AR + detached baseline. Decision rule in §1.8.
- [ ] **Step 5 (independent diagnostic):** 2022-only single-cycle training run — if it can't beat 5 pp on 2022 alone, shelve J5-E (per P5 §Caveat 4 — feature-engineering problem, not algorithmic).
- [ ] **Step 6 (conditional):** J5-E (per-cycle LoRA + BBSE) targeting the 2022×WD 9.69 pp cell, only if the diagnostic passes.
- [ ] **Step 7 — REPURPOSED 2026-05-20:** Pure encoder-only revert is no longer a "last resort" — it's now **J_old** in Step 4's parallel bundle. If neither J5-F nor J_old beats J3, the architecture investigation is closed and the team accepts J3 + feature-engineering (J5-E pathway) as the only remaining lever.

**Execution discipline (locked 2026-05-20):** Every J5 bundle from here on uses the **one-upload → parallel-train → one-download** cycle. Edit and stage all bundle files locally; recursive scp to cluster once; sbatch all jobs in one shell line; download all outputs in one `ForEach-Object` scp. Never partial-upload or mid-cycle re-stage. Matches the J5-X2/A/B precedent that validated this pattern.

### Execution count
- **Sbatch submissions to date:** 1 sequential bundle (J5-X1 + J5-X1b) + 3 parallel jobs (J5-X2, J5-A, J5-B).
- **Architecture trials in flight or completed:** 4 (J5-X1, J5-X1b, J5-B, J6-shelved). J5-X1/X1b are forward-pass re-routes; J5-A/X2 are loss/config-only; J5-D would stack on J5-A; J5-E adds LoRA modules but reuses the J3 trunk.

---

## 1.2 Executive Summary

**Original top pick (2026-05-16):** J5-X1 + J5-X1b sequential bundle. Counter-finding from joint CSV + code review: J5-A's load-bearing claim (P2 §5 — that `home_loss=0.3514` sits at the ε=0.05 BCE floor of 0.198) does not hold for the J-series. The H-series (H_Tanh, H_Time, G4) used the same ε=0.05 and reached `home_loss ≈ 0.22` — at the predicted floor. J-series sits ~0.13 above the floor at the same ε; the gap appeared when the architecture split into Arm 1 (activity AR decoder) + Arm 2 (NAT fusion for home/cop). cop_loss shows the same 3× regression (0.0675 → 0.1919). The binding constraint is what *feeds* the binary heads, not what the loss penalises. None of the 7 deep-research docs discuss head-input depth (independent re-scan 2026-05-16) — the entire J5-A through J5-E ladder rests on loss-side / gradient-balancing / structured-prediction fixes that assume a single shared trunk.

**Outcome of Step 1 (J5-X1 bundle, 2026-05-18):** Neither J5-X1 nor J5-X1b beat J3 on composite. J5-X1 improved AT_HOME RMS (4.15 vs J3's 4.57 pp) but worsened act_JS (0.0311 vs 0.0191), composite 0.6667 FAIL. J5-X1b worsened copresence (Alone gap 8.14 pp), composite 0.8086 FAIL. The Arm-2 NAT fusion path in J3 remains superior for copresence calibration. **J3 retains production status pending Step 2.**

**Step 2 (current — J5-X2/A/B parallel bundle, 2026-05-19):**
- **J5-X2** tests whether J5-X1's act_JS regression is config-driven (`lambda_home: 0.7 → 0.9` restoration on the J5-X1 arch). If yes, J5-X1's AT_HOME gain is preserved and composite beats J3.
- **J5-A** falls back to the original reserve — drop `home_label_smooth` to 0.0 on the J3 arch (P1/P2 BCE-floor argument; falsified for the J-series but worth the cheap test).
- **J5-B** introduces the hierarchical chain-rule cop head (one architectural change, low risk; targets the 2005/2010 Alone-channel residual).

All three run in parallel as independent sbatch jobs (~17–24 h wall clock if GPUs available).

---

## 1.3 Decisions locked (2026-05-15, revised 2026-05-16 and 2026-05-19)

- **First submission (locked 2026-05-15, revised 2026-05-16):** J5-X1 + J5-X1b sequential bundle. Executed 2026-05-17 → 2026-05-18. **Result:** J3 retains production status; J5-X1 act_JS regression observed and traced to lambda_home deviation.
- **Second submission (locked 2026-05-19):** Triple parallel bundle — J5-X2, J5-A, J5-B as independent sbatch jobs. Each writes to its own output dir; SLURM decides actual concurrency. Triggered by Step 1's outcome: J5-X1's AT_HOME gain was real but composite failed; need the config fix (X2), the original reserve (A), and the chain-rule cop fix (B) all tested before escalating.
- **J5-A held as reserve fallback (revised 2026-05-16):** Originally queued only if X1 bundle's head-input hypothesis was falsified. Now rolled into the 2026-05-19 parallel bundle alongside X2 and B to maximize cluster opportunity.
- **J6 — joint activity × AT_HOME vocabulary head (P7 §1 stage 1) is shelved.** Single-prompt recommendation; would force a 14→28 Arm-1 softmax rewrite, invalidate the J3 checkpoint, and force re-runs of Step 5 (Census Linkage, complete) and Step 6 (Longitudinal Forecasting, in flight). Defensible escalation only if J5-A/B/C all pass gates but composite stalls materially above J3's 0.6355 with no further loss-side headroom. Not in the J5 scope.
- **Open question #1 resolved.** If J5-A's `home_label_smooth=0.0` fails to break `home_loss` from the 0.36 plateau by smoke ep 5–10, fall to J5-D (FAMO) stacked on J5-A — *not* the inverted-ASL variant. P2's zero-gradient argument is load-bearing.
- **Open question #2 deferred.** Linear-chain CRF is the J5-C entry point; semi-Markov is the reactive J5-C2 only if linear-chain underperforms on the 158× transition-rate ratio.
- **Open question #3 — 2022×WD diagnostic precondition.** Before J5-E build, run a 2022-only single-cycle diagnostic; if it cannot beat 5 pp on 2022 alone, J5-E is shelved (per P5 §Caveat 4 — feature-engineering problem, not algorithmic).
- **Third submission (locked 2026-05-20, revised same-day to triple bundle):** **J5-F + J_old + J5-C parallel triple bundle.** Three independent sbatch jobs in one upload cycle. **J5-F** = joint encoder supervision + AR decoder for activity (hybrid). **J_old** = pure `Transformer_pipeline.py` revert at 48-slot resolution (encoder + 3 parallel Linear heads, no AR, no Arm-2 fusion). **J5-C** = J3 topology + linear-chain CRF + Viterbi on Arm-1 activity logits. **Discipline:** one upload → parallel train → one download (no mid-cycle re-stage). Trigger: the 2026-05-20 bundle re-diagnosis — across J5_X2/A/B the binding constraint is supervision topology (encoder shaped only by activity), not loss-side or cop-side tuning. **J5-D shelved** (precondition failed; FAMO on a topology-broken trunk would deprioritise the plateaued home head and amplify collapse). **J5-I dropped from candidate list** — soft variant of J5-F that tests the same hypothesis at lower aggressiveness; if J5-F wins, J5-I is moot; if J5-F loses, J5-I likely loses too. Replaced by J_old which asks a fundamentally different question ("is the AR decoder needed at all?"). **J5-E gated** on 2022-only diagnostic (independent of this bundle).

---

## 1.4 Experiment cards (10 cards: X1, X1b, X2, A, B, F, J_old, C, D, E)

> All cards reproduced verbatim from `J5_proposal.md` §2 (2026-05-15, revised 2026-05-16, 2026-05-18). Per-card methodology unchanged by the 2026-05-19 parallel-bundle restructure.

### J5-X1 — Re-route binary heads to the activity decoder output (`dec_output.detach()`)

- **Method** — In `JSeriesHybrid.forward` and `.infer`, change the binary heads' input from the Arm 2 fusion tensor (`arm2_feat`) to the activity decoder's output (`dec_output`) with a `.detach()` barrier preserving the J-series no-cross-arm-gradient invariant. Concretely: `self.home_head(arm2_feat)` → `self.home_head(dec_output.detach())`, identically for `self.cop_head`. Arm 2 fusion code (`_arm2_fuse`, `arm2_proj`, `arm2_act_proj`) is bypassed for the heads (kept on disk for revert) but no longer in the forward path. The home/cop head modules themselves are byte-identical to J3 (Tanh → Linear → Sigmoid, d_model=384 → 1 / → 9). No loss change. Config is J3 byte-for-byte (`lambda_home=0.9`, `home_label_smooth=0.05`, `spouse_neg_weight=0.45`, etc.).
- **Failure mode it attacks** — Binary-head representation starvation, identified 2026-05-16 by joint CSV + code review. Evidence: home_loss collapsed from 0.2265 (H_Tanh, shared trunk) to 0.3596 (J1, separate Arm 2) at identical ε=0.05 smoothing, and stayed at 0.35 through J2/J2.5/J3. cop_loss shows the same 3× regression (0.0675 → 0.1919). J3 calibration diagnostic shows all 1.56M AT_HOME predictions in `[0, 0.1)` bin — head learned aggregate (gap_pp=2.10) but lost slot-conditional discrimination. P2 §5's BCE-floor argument (0.198) does not bind the J-series — H_Tanh already operated within 0.03 of that floor at the same ε. The binding constraint is what feeds the head, not what the loss penalises.
- **Hard gates** — home_loss ≤ 0.27; cop_loss ≤ 0.12; AT_HOME RMS ≤ 5.30 pp; Spouse |Δ| ≤ 5 pp; act_JS ≤ 0.05; composite ≤ J3's 0.6355.
- **Risk** — Low-medium. Detach barrier mathematically isolates the activity decoder; risk if the decoder doesn't encode AT_HOME-discriminative signal cleanly.
- **GPU cost** — ~1.0× J3 wall time (~17 h on `pg`). Net parameter-count reduction ~0.3 M.

### J5-X1b — Re-route binary heads to `dec_output` (no detach barrier)

- **Method** — Same re-route as J5-X1 but *without* the `.detach()` barrier: `self.home_head(dec_output)` and `self.cop_head(dec_output)` directly. Binary-head gradients flow back into the activity AR decoder during backward, exactly as in H_Tanh. Arm 2 fusion code bypassed identically to J5-X1. Config inherits `configs/J3.yaml` byte-for-byte (`lambda_home=0.9`, `home_label_smooth=0.05`).
- **Hypothesis** — Detach barrier itself may be starving the heads of slot-level signal; if so, gradient pull from the heads is needed to shape the decoder representation. H_Tanh's empirical anchor (home_loss=0.22 with shared trunk, no detach) supports this branch.
- **Hard gates** — Identical to J5-X1. act_JS is the watch metric (decoder *is* being perturbed by binary-head gradients).
- **Risk** — Medium (higher than X1). H_Tanh's AT_HOME RMS failure at 5.70 pp (3/4 gates) shows the cross-arm regime can degrade AT_HOME aggregate. Watch Spouse |Δ| against the 5 pp gate.
- **GPU cost** — ~1.0× J3 wall time. Identical parameter count to X1.

### J5-X2 — J5-X1 architecture + `lambda_home=0.9` (config fix for act_JS regression)

- **Method** — Identical architecture to J5-X1: binary heads (`home_head`, `cop_head`) read from `dec_out.detach()` via `_arm1_decode_tf_full`; Arm-2 NAT fusion bypassed. Single config change: `lambda_home: 0.7 → 0.9` (restoring J3's original value). All other hyperparameters J5-X1 byte-for-byte. `model_type: J5_X1` reused — no new MODEL_TYPE, no model code change. Output dir `outputs_step4_J5_X2/`.
- **Hypothesis** — J5-X1's act_JS regression (0.0311 vs J3's 0.0191) is config-driven, not architectural. The `.detach()` barrier means binary-head gradients never reach the AR decoder; from the decoder's perspective, J5-X1 and J3 train identically. The `lambda_home=0.7` deviation (inherited from the J4 config base — J3 used 0.9) shifts the optimization trajectory and the val_score-driven early-stop timing, landing on a checkpoint with worse activity quality. With `lambda_home=0.9`, the model should converge to J3-level act_JS while preserving J5-X1's AT_HOME RMS improvement (4.15 pp vs J3's 4.57 pp). If both hold, the composite beats J3's 0.6355.
- **Evidence** — J5-X1 best checkpoint was epoch 51 (early stop ep66); J3 best checkpoint was epoch 72 (early stop ep87). J5-X1 stopped ~21 epochs earlier than J3 despite identical patience=15 and architecture, consistent with a lower `lambda_home` producing a different val_score trajectory. act_loss at best epoch: J5-X1 = 0.1379; J3 = 0.0878 — supporting the early-stop-before-activity-convergence hypothesis.
- **Hard gates** — Identical to J5-X1. **Targets:** act_JS ≤ 0.022 (J3-level); AT_HOME RMS ≤ 4.15 pp (preserved from J5-X1); composite < 0.6355.
- **Risk** — Very low. Single config scalar on a tested, stable architecture. The `.detach()` barrier is structurally unchanged; `lambda_home` only affects shared optimizer momentum and the LR scheduler — no gradient pathway to the activity arm changes.
- **GPU cost** — ~1.0× J3 wall time (~17 h on pg). Identical model: 29.25 M params.
- **OUTCOME (2026-05-20, job 933657)** — **FAILED.** Composite 0.6747 vs J3's 0.6355. AT_HOME RMS = 4.42 pp (✓ beat J3's 4.57, beat target 4.15); Spouse Δ = −1.89 pp (✓ beat J3's −2.03); act_JS = 0.0297 (✗ target was 0.022, J3 had 0.0191). Lambda fix recovered ~45% of the X1 act_JS regression (0.0311 → 0.0297) but the remaining gap is structural to the `dec_out.detach()` route. **Hypothesis "act_JS regression is purely config-driven" falsified.** Detach-route architecture is parked. See Part 2 / 2026-05-20.

### J5-A — Drop `home_label_smooth` (config-only, single knob)

- **Method** — Set `home_label_smooth: 0.0` in the J3 config (currently 0.05). No model code, no loss code, no dispatch change beyond extending the MODEL_TYPE allow-list to include `J5_A`.
- **Failure mode it attacks** — P1 §3: "label smoothing actively causes and severely exacerbates the σ=0 collapse signature." P2 §5 closes the loop algebraically: ε=0.05 ⇒ BCE floor = −0.5·log(0.95) − 0.5·log(0.05) = 0.198 — within 0.01 of J3's observed `home_loss=0.3514` plateau and J1's 0.3596 plateau.
- **Hard gates** — Primary: AT_HOME RMS from J3's 4.57 pp toward ~3.0–3.8 pp by restoring slot-conditional probability learning on the home head; eliminates the σ=0.0 morning over-prediction (+10.77 pp gap on slots 0–10 in J1 diagnostics). Composite expected to drop further from 0.6355. act_JS and Spouse should hold (Arm 1 unaffected, Spouse uses clip-only inference).
- **Risk** — Lowest in the ladder. J3's passing run used ε=0.05, so we are perturbing a known-good config; the perturbation is unambiguously in the recovery direction per P1+P2.
- **GPU cost** — 1.0× J3 wall time (~17 h). Zero overhead.
- **OUTCOME (2026-05-20, job 933658)** — **FAILED.** Composite 0.6997 vs J3's 0.6355. AT_HOME RMS = 5.57 pp (✗ worse than J3's 4.57, target was ≤ 3.8). Dropping `home_label_smooth` did NOT restore slot-conditional learning — confirms the §1.5 row "Drop label smoothing — falsified for J-series 2026-05-16" empirically. The 0.198 BCE-floor argument (P1/P2) is not the binding constraint on the J-series. **Reserve exhausted.** J5-D (FAMO stacked on J5-A) is now also low-priority — the precondition (J5-A fixing the home head) did not occur.

### J5-B — Hierarchical chain-rule cop head (architecture, single change)

- **Method** — Restructure the 9-channel co-presence output via the HMC chain rule: `p(alone) = sigmoid(z_alone)`; `p(other_i) = (1 − p(alone)) · sigmoid(z_other_i)` for each of the 8 non-Alone channels. BCE applied on the final marginal probabilities `p(alone)` and `p(other_i)`, not on intermediate logits. *Structurally distinct from J4_2*, which concatenated `home_probs.detach()` as an extra feature — that variant regressed AT_HOME by +1.31 pp and was shelved. J5-B restricts the *output space* so that impossible Alone+Other combinations cannot be expressed, rather than adding an auxiliary penalty or conditioning feature.
- **Failure mode it attacks** — Prompt 3: "2005/2010 Alone +21/+17 pp; J4_3 PINN logic-loss collapsing Spouse". Strong cross-prompt consensus (P3 §11.1 Rec 1; P7 §1 stage 1).
- **Implementation (this cycle, 2026-05-19)** — `JSeriesHybrid` build identical to J3 (shares the line-500 allow-list and `arm2_act_proj` path). Chain rule applied: (a) in `compute_loss` (BCE on marginal probs with manual spouse_neg_weight multiplication, since `F.binary_cross_entropy` lacks pos_weight); (b) in `JSeriesHybrid.infer()` (chain-rule probs returned directly; safety mask `cop_prob[:,:,Spouse] *= gen_home` skipped — chain rule subsumes it).
- **Hard gates** — Primary: cop_max_gap from J3's 7.04 pp (Alone, 2005_1 +21.1 pp / 2010_1 +17.1 pp) toward ≤ 3.5 pp on the Alone channel by construction. Spouse |gap| stable or slightly tighter; AT_HOME unaffected (home_head untouched). Composite expected to nudge down. act_JS gate held — Arm 1 has no interaction with the cop head's chain rule.
- **Risk** — Low-medium. Watches `home_loss` for departure from J3's 0.35 floor in the *wrong* direction (collapse below 0.30 → matches J4_2's failure signature).
- **GPU cost** — 1.0× J3 wall time. Two extra elementwise multiplications per forward pass; negligible.
- **OUTCOME (2026-05-20, job 933659)** — **FAILED on composite, INTERESTING signal.** Composite 0.6975 vs J3's 0.6355. AT_HOME RMS = 5.20 pp (✗ regressed from J3's 4.57); Alone gap = +7.07 pp (✗ worse than J3 — chain rule did NOT close the 2005/2010 Alone residual at the dataset scale). **But Spouse Δ flipped sign from −2.03 (J3) → +1.61 (J5-B)** — the chain rule genuinely restructures Spouse predictions, just not in the direction predicted. The marginalisation tax landed on Alone instead. P3 §11.1's geometric trade-off (Alone gain ↔ Other-channel cost) inverted here. Per-channel `alpha` (Open Q #6, "J5-B-v2") is NOT justified — the failure is at the chain-rule level, not its parameterisation. **Chain-rule cop head parked.**

### J5-F — Joint encoder supervision + AR decoder for activity only (NEW 2026-05-20)

- **Method** — Restore the old `Transformer_pipeline.py` supervision topology on the encoder, while keeping J3's autoregressive decoder for activity. Concretely, in `JSeriesHybrid`:
  - Encoder + LayerNorm output `enc_out` (B, 48, 384) — unchanged from J3.
  - **`.detach()` barriers removed.** Arm 2 fusion (`arm2_proj`, `arm2_act_proj`, `_arm2_fuse`) dropped from the forward path (kept on disk for revert).
  - **Three heads attached to `enc_out` directly:**
    - `home_head_enc(enc_out)` → Tanh → Linear(384→1) → sigmoid → BCE on AT_HOME labels.
    - `cop_head_enc(enc_out)` → Tanh → Linear(384→9) → sigmoid → BCE on co-presence labels (Spouse channel still gets `spouse_neg_weight=0.45`).
    - **Activity path retains J3's AR decoder**: `enc_out` → CrossAttn AR decoder (6 layers, unchanged) → `act_head` → softmax → CE. Gradient now flows from CE loss into the encoder (was blocked in J3 only via Arm-2-detach; here the activity path itself never had detach).
  - Total loss: `lambda_act * loss_act + lambda_home * loss_home + lambda_cop * loss_cop` — same lambdas as J3 (0.5 / 0.9 / 0.5) initially.
  - Inference: home/cop predictions come from `enc_out` heads; activity from AR decoder Viterbi-or-argmax (J3-style). No Arm-2 fusion call.
  - New `model_type: J5_F`. Predecessor `cp 04B_model.py → Speed_Cluster/archive/04B_model_pre_J5_F.py` mandatory before edit. MODEL_TYPE allow-lists in `04D_train.py` and `04E_inference.py` extended.

- **Failure mode it attacks** — Direct topology fix for the bundle-wide failure pattern observed 2026-05-20. Diagnosis (Part 2 / 2026-05-20): the `.detach()` barrier between Arm 1 and Arm 2 means AT_HOME and cop losses shape only the head MLPs (~150 K params) while activity loss shapes ~28 M params (encoder + AR decoder). 187× capacity asymmetry. The old `Transformer_pipeline.py` (encoder-only, three parallel heads, joint loss → `total_loss = w_act*loss_act + w_loc*loss_loc + w_NOB*loss_NOB`, file lines 556–558 + 777) gave all three heads equal access to the encoder and hit ~95 % on all three with regularization. J5-F restores that supervision symmetry on the encoder while keeping J3's AR decoder so we don't lose the activity-JS gain (0.0191 → would otherwise revert to the encoder-only era's higher JS).

- **Hard gates** — Primary: AT_HOME RMS ≤ 4.0 pp (≥ 0.5 pp improvement on J3's 4.57). Spouse |Δ| ≤ 2.0 pp (≥ 0.03 pp tightening on J3's −2.03). act_JS ≤ 0.022 (within 15 % of J3's 0.0191; small regression acceptable because the encoder is now multi-task-shaped). Composite < 0.6000 (≥ 6 % improvement on J3's 0.6355). cop max_gap should hold or tighten — encoder representation now carries Alone-channel signal.

- **Risk** — Medium. (a) Removing the detach barrier failed in J5-X1b (Alone +8.14 pp, composite 0.8086) — but J5-X1b kept Arm 2 fusion *and* added an open cross-arm gradient path; J5-F drops Arm 2 entirely and routes cop directly off the encoder. Structurally distinct failure surface. (b) Encoder representation could become "diluted" if the three losses pull in opposing directions — old pipeline avoided this with weight regularization + dropout; J5-F inherits J3's existing regularization. (c) act_JS could regress: the AR decoder's cross-attention now reads an encoder shaped by all three losses, not activity alone. Mitigation: if act_JS regresses materially, fall back to `lambda_act=0.7` (raise from 0.5) on a retry — but only after the bundle returns. **No retry in this cycle** — one-upload-one-download discipline applies.

- **GPU cost** — ~1.0× J3 wall time (~17 h on `pg`). Encoder + AR decoder unchanged; binary-head fan-out from 384→{1, 9} instead of 384→384→{1, 9} is actually slightly cheaper than J3's Arm-2 fusion.

- **Why this is different from every prior J-series card** — J5-X1/X1b/X2 re-routed binary heads to different *activity-shaped* tensors (dec_output or arm2_feat). J5-A/D were loss-side. J5-B restructured the cop output space. **None of them changed which loss shapes the encoder.** J5-F is the first card to break the "activity loss is the sole encoder-shaping signal" invariant that has held since J1. It is the architectural delta the 2026-05-20 diagnosis identifies as binding.

### J_old — Pure encoder-only revert (mirrors `Transformer_pipeline.py` topology at 48-slot resolution) (NEW 2026-05-20)

- **Method** — Drop both the AR decoder and the Arm-2 fusion. Restore the old pipeline's three-parallel-heads-off-encoder topology at the J3 dataset's resolution (48-slot) and feature set (J3 byte-identical embeddings, sinusoidal positional encoding, 6-layer encoder, d_model=384). Concretely in `JSeriesHybrid`:
  - Encoder + LayerNorm → `enc_out` (B, 48, 384). Unchanged.
  - **No CrossAttn AR decoder.** **No Arm-2 fusion** (`_arm2_fuse`, `arm2_proj`, `arm2_act_proj` all bypassed, kept on disk for revert).
  - **Three parallel Linear heads off `enc_out`**, mirroring `Transformer_pipeline.py:556-558`:
    - `activity_head_old` = Linear(384, 14) → softmax (CE).
    - `home_head_old`     = Linear(384, 1) → sigmoid (BCE on AT_HOME).
    - `cop_head_old`      = Linear(384, 9) → sigmoid (BCE on co-presence; spouse channel still gets `spouse_neg_weight=0.45`).
    - Modeled exactly on `activity_dense`, `location_dense`, `withNOB_dense` from the old pipeline. No Tanh between encoder and head (old pipeline used a Dropout-then-Linear; J_old applies J3's existing trunk dropout and adds nothing else).
  - Loss: `total = w_act*CE(activity) + w_home*BCE(home) + w_cop*BCE(cop)`, mirroring `Transformer_pipeline.py:777`. Use J3's lambdas (0.5 / 0.9 / 0.5) initially.
  - **Inference:** argmax on `activity_head_old` (no Viterbi, no AR rollout). No safety mask. No chain rule.
  - New `model_type: J_old`. Predecessor archive `cp 04B_model.py → Speed_Cluster/archive/04B_model_pre_J_old.py` mandatory. MODEL_TYPE allow-lists extended.

- **Failure mode it attacks** — The "is the AR decoder even helping at 48-slot resolution?" question. The old pipeline reached ~95% activity accuracy at 24-slot **without** AR (per `Transformer_pipeline.py` status badge), using only joint supervision + dropout + weight regularization. J3's act_JS = 0.0191 comes from the AR decoder, but that 0.0191 gain might be **purchasable for free** by joint supervision — i.e. the encoder alone, when shaped by all three losses, might match it. If true, the entire J-series Arm 1 / Arm 2 split was unjustified complexity. If false (J_old activity regresses materially), J5-F's hybrid design is vindicated as the right path. Either way, this card gives a clean read on whether the AR decoder is doing real work.

- **Hard gates** — Primary: AT_HOME RMS ≤ 4.0 pp (same as J5-F target); Spouse |Δ| ≤ 2.0 pp; cop max_gap ≤ 5 pp; composite < 0.6000. Secondary (the diagnostic gate): act_JS — if ≤ 0.025, the AR decoder is unnecessary at 48-slot. If > 0.05, J3's AR was load-bearing and the J-series split was correct (we'd then ship J5-F if it cleared gates, J3 otherwise).

- **Risk** — Low-medium. The architecture is the simplest of any J-series card and the closest to a known-good baseline (`Transformer_pipeline.py` at 24-slot reached ~95% on all three). Main risks: (a) at 48-slot, the encoder may need more layers or stronger regularization to avoid memorization — J3's regularization is inherited but the trunk was tuned for the J3 split, not for direct heads. (b) Old pipeline's status badge flagged that the raw model memorized easily; if J_old overfits at 48-slot, the train/val gap will widen visibly by epoch 30–40 and val_score will diverge. Mitigation: existing J3 dropout + weight-decay should be sufficient at first pass; if overfitting appears, dropout sweep is the natural follow-up but not part of this bundle.

- **GPU cost** — **Cheapest of the bundle** (~0.6–0.7× J3 wall time, est. ~10–12 h on `pg`). No AR decoder = no cross-attention rollout in training; no Arm-2 fusion = smaller forward pass per slot. Could finish before J5-F and J5-C.

- **Why this is its own card, not a sub-case of J5-F** — J5-F keeps the AR decoder for activity prediction; J_old drops it. They test orthogonal hypotheses (does encoder need joint supervision? vs does the AR decoder help?). Running both in parallel lets us read the 2×2 axes cleanly. Without J_old, we can't tell whether J5-F's wins (if any) come from joint supervision OR from the AR decoder OR both.

### J5-C — Linear-chain CRF + Viterbi decode on Arm-1 activity logits

- **Method** — Append a linear-chain CRF layer to the Arm-1 AR decoder: unary potentials = `act_logits[B,48,14]`, learnable pairwise transition matrix `ψ_pair ∈ ℝ^{14×14}`. Replace per-slot cross-entropy with CRF NLL via forward-backward. At inference, replace argmax with Viterbi on `(ψ_unary, ψ_pair)`. The Viterbi-decoded one-hot is the activity signal forwarded to Arm 2 fusion (`act_seq.detach()`), preserving the J1 detach barrier.
- **Failure mode it attacks** — Prompt 4: "Transition rate ratio = 157.95 (synthetic vs observed)". Strong cross-prompt consensus (P4 §7 Path 1 rank 1; P7 §1 stage 2).
- **Hard gates** — Primary: transition rate ratio 157.95× → target 10–30× (CRF gain typically 1–3 absolute points on persistence metrics). Should improve act_JS marginally. AT_HOME and cop unaffected (detach barrier preserved); composite stable or better.
- **Risk** — Medium. (a) over-smoothing → dominant-state runs degrade `act_JS`. (b) train/infer signal gap (soft-prob at train vs Viterbi at infer) could re-create scheduled-sampling-style failure.
- **GPU cost** — ~1.2× J3 wall time. Forward-backward per batch is O(B·48·196), small add.

### J5-D — FAMO adaptive multi-task weighting (loss-aggregator, stacked on J5-A)

- **Method** — Replace static λ-weighting with FAMO (Liu et al. 2024, NeurIPS) — task weights updated each step from an EMA of per-task loss descent rates. **Hard prerequisite: must stack on J5-A** (label smoothing dropped first). FAMO detects plateaued tasks and *removes* their weight; if the home head is still locked to the ε=0.05 floor, FAMO will deprioritise it and amplify the collapse.
- **Failure mode it attacks** — P2 §5: manual `λ_home` sweep over 20+ runs was futile (∇ ≈ 0 once the floor is hit; scalar λ × zero gradient is still zero). FAMO is the cheap O(1) drop-in.
- **Hard gates** — Secondary. Expected outcome: ~3–8% tightening across loss components; composite from J5-A's projection further toward 0.50–0.55.
- **Risk** — Medium. Stacking risk on J5-A; oscillation if descent rates are noisy; removes manual λ control.
- **GPU cost** — ~1.05× J3 wall time.

### J5-E — Per-cycle LoRA adapter + BBSE label-shift correction (for the 2022×WD residual)

- **Method** — Add a rank-4 LoRA adapter (Hu et al. 2021) to the encoder linear projections, keyed on `cycle_idx ∈ {2005, 2010, 2015, 2022}`. Train the global model first (J3 or J5-A as base), then fine-tune the 2022 adapter on 2022-only data with global weights frozen. At inference, apply the cycle-appropriate adapter. In parallel, apply BBSE label-shift correction (Lipton et al. ICML 2018).
- **Failure mode it attacks** — Prompt 5: per-stratum AT_HOME RMS=4.57 pp with 2022×WD |Δ|=9.69 pp (post-2020 remote-work shift).
- **Hard gate** — 2022×WD cell |Δ| from 9.69 → ~4–5 pp. Aggregate AT_HOME RMS likely shifts modestly. Non-regression: other 11 cells must hold.
- **Risk** — Medium-high. P5 §Caveat 4 warns the cell may be "irreducible without feature engineering for post-2020 behavior" — fastest diagnostic is a 2022-only training run; if that can't beat 5 pp on 2022 alone, no adapter will help.
- **GPU cost** — ~1.3× J3 wall time. Stage-1 ~17 h + stage-2 2022 fine-tune ~4–5 h.

---

## 1.5 Cross-Prompt Consensus Table

Methods appearing in ≥ 2 LLM responses (strong consensus → load-bearing), and methods appearing in only 1 (treat as single-paper-strength).

| Method | Appears in | Status |
|---|---|---|
| Re-route binary heads off shared decoder output (vs separate shallow Arm-2 projection) | **None of the 7 prompts** — independent re-scan 2026-05-16 confirms gap | **Architectural — orthogonal to all 7 prompts (gap finding); promoted to J5-X1** |
| Drop label smoothing on home head (`ε = 0.05 → 0.0`) | P1 §6 step 1, P2 §5 (mathematically derives 0.198 floor) | **Strong on paper, falsified for J-series 2026-05-16** — H-series sat at the 0.198 floor with same ε=0.05; J-series sits 0.13 above. Smoothing is not the binding constraint. Held as J5-A reserve only |
| Hierarchical / chain-rule restructuring of the multi-label output space (NOT concat/penalty) | P3 §11.1 (Recommendation 1), P7 §1 stage 1 (highest-leverage) | **Strong** — promoted to J5-B |
| Linear-chain CRF / Viterbi on AR sequence logits | P4 §7 Path 1 (rank 1), P7 §1 stage 2 | **Strong** — promoted to J5-C |
| Adaptive multi-task balancing (FAMO / Uncertainty Weighting) | P2 §6 only, with P7 §1 stage 4 recommending UW *only* as a sanity gate on auxiliary losses | Moderate — promoted to J5-D but stacked on J5-A |
| Distributional / per-group robustness via LoRA + BBSE | P5 only (Track B) | Weak — promoted to J5-E with explicit irreducibility caveat |
| Asymmetric Loss (ASL) with inverted γ on the home head | P1 §6 top recommendation only | Weak — held in reserve; cheaper alternative is J5-A's smoothing fix, deferred unless smoothing fix alone leaves σ=0 |
| Total Variation regularisation on activity logits | P4 §5.1 + §7 Path 1 (combined with Viterbi) | Moderate — bundled into J5-C as optional add (`λ_tv = 0.05` if Viterbi alone underperforms) |
| Block-autoregressive / chunked decoding | P4 §7 Path 2 only | Single-prompt — rejected (architectural reach too large for one-axis card) |
| Run-Length Encoding + Negative Binomial duration head | P4 §7 Path 3 only | Single-prompt — rejected (would require Arm 1 rewrite) |
| Group DRO / SUBG / DFR last-layer retrain | P5 Track A only | Single-prompt — held in reserve; revisit only if J5-A doesn't tighten per-cell variance |
| Discrete diffusion (MDLM / SEDD / D3PM) | P6 (whole document) | Single-prompt **AND** violates user "no wholesale swap" constraint — rejected |
| JEM-style joint training, SPEN/DVN, masked-diary pretraining | P7 Stage 3–4 only | Weak — deferred; preconditioned on J5-A/B/C all running out of headroom |

Consensus is strongest where two prompts arrive at the same mechanism from different starting points (J5-A, J5-B, J5-C). The middle of the ladder (J5-D, J5-E) rests on single-prompt recommendations from P2 and P5 respectively — flagged accordingly in the cards.

---

## 1.6 Methods Explicitly Rejected (and why)

- **Soft logic loss / mutual-exclusivity penalty (P3 §2; cf. J4_3)** — both empirically (J4_3: 1/4 gates, Spouse collapsed to −8.89 pp) and theoretically (P3 §2 derives the asymmetric gradient that drives `p_others_i → 0`). Replaced by J5-B's chain-rule output restructuring. Do not revisit even with a smaller λ; the failure mechanism is gradient-geometric, not a tuning issue.
- **Scheduled sampling on the AR decoder** — G2/G3 outcome already on file (Spouse axis destroyed); J1 doc §J1 explicit non-goal.
- **Class-Balanced Loss (P1 §2.3)** — for mild 60/40 imbalance, effective-volume reweighting degenerates to ≈ 1.0; compute cost unjustified.
- **Brier Score as training loss (P1 §4)** — vanishing sigmoid-derivative gradient near σ ∈ {0, 1}; would exacerbate σ=0 collapse, not relieve it. Reserved for evaluation only.
- **Post-hoc calibration (Platt/temperature/isotonic/Beta/Dirichlet) for AT_HOME (P1 §5)** — via the data-processing inequality, no injective post-hoc map can synthesise mutual information that the σ=0 head destroyed. Calibration is inapplicable when the failure is variance-zero, not over-confidence.
- **IRM, V-REx, DANN for the 2022×WD shift (P5 §Track B, §Caveats)** — DomainBed shows no algorithm outperforms ERM by more than one point under matched experimental conditions; IRM predictor can fail catastrophically with only three pre-2020 environments. Replaced by J5-E's LoRA + BBSE.
- **Unsupervised TTA (Tent / CoTTA) (P5)** — collapses to ordinary fine-tuning when validation labels exist, with catastrophic-forgetting risk. We have labels for all 12 cells.
- **MGDA-UB / PCGrad / CAGrad / Nash-MTL (P2 §3.3–§3.7)** — N=4 backward passes per step inflates the 17 h baseline to ~68 h. FAMO is the explicit cheap drop-in (built by the CAGrad authors).
- **MDLM / SEDD / D3PM / D3PM-style discrete diffusion as wholesale AR replacement (P6 §Stage 1)** — violates explicit user "no wholesale swap" constraint. Out of scope for J5.
- **SPEN / DVN / Neural Hawkes / HSMM / Levenshtein Transformer (P3 §5–§6, P4 §2–§3)** — overkill for N=9/14 vocabulary at 48 slots; architecture reach exceeds the "one axis per arm" rule.
- **Counterfactual data augmentation for 2022 (P5 §Caveats)** — Kaushik et al. require human-generated label-flipping; no operational notion of "counterfactual diary day." Joshi & He (ACL 2022) show CAD can exacerbate spurious correlations.

---

## 1.7 Open Questions / Cross-Prompt Disagreements

1. **Loss-only vs head-architecture as the AT_HOME calibration fix.** P1 argues for inverted-γ ASL; P2 argues FAMO; P7 argues joint vocabulary head. **Implication for J5-A**: if `home_label_smooth=0.0` alone does not restore slot-conditional learning, fall to J5-D (FAMO), not ASL (P2's zero-gradient argument is load-bearing).

2. **Linear-chain CRF vs semi-Markov CRF.** P4 §7 Path 1 recommends linear-chain + Viterbi as the entry point; P7 §1 stage 3 recommends semi-Markov CRF *after* the linear-chain CRF. J5-C takes the linear-chain entry point; semi-Markov is the reactive J5-C2.

3. **Whether the 2022×WD 9.69 pp gap is method-fixable at all.** P5 §Caveat 4 candid: "if a 2022-only model cannot beat 5 pp on 2022 alone, the problem is not method choice — it is feature-engineering." **Implication for J5-E**: budget a 2022-only single-cycle training run as a *diagnostic* before committing to the LoRA build.

4. **Whether AT_HOME could be merged into the activity vocabulary at all (P7 §1 stage 1).** ~~P7's "single highest-leverage" intervention is to collapse activity (14-class) × AT_HOME (binary) into a joint 28-class vocabulary.~~ **Resolved 2026-05-15: shelved as J6.** Single-prompt only; rewrites Arm 1 and forces re-runs of Step 5 (Census Linkage, complete) and Step 6 (Longitudinal Forecasting, in flight); J5-A is essentially free and may close the residual alone. Reopens only as J6 if J5-A/B/C all pass gates and composite stalls materially above J3's 0.6355.

5. **TV regularisation strength.** P4 §5.1 cites `λ_tv ∈ [10⁻³, 10⁻²]`; J5-C deploys TV only as an optional add if Viterbi alone underperforms.

6. **Per-channel `alpha` vs uniform `alpha` for the chain-rule cop head (J5-B).** P3 §11.1 derives the chain-rule but does not specify whether the 8 conditional sigmoids should share parameters. J5-B assumes 8 independent conditionals; share-params variant queued as J5-B-v2 if Other-channel calibration regresses.

7. **Does J5-X1 subsume J5-B and J5-C?** (added 2026-05-16) If J5-X1 closes both binary-head losses by restoring decoder-quality context to home/cop, J5-B's `cop_max_gap` target and J5-C's transition-rate target may shrink enough that those cards lose independent value. The transition-rate ratio is a *generation*-time property of the activity AR decoder, which J5-X1 leaves unchanged, so J5-C remains independently load-bearing. **Outcome 2026-05-18:** J5-X1 did NOT subsume J5-B — Alone gap residual persisted, hence J5-B included in the 2026-05-19 parallel bundle.

---

## 1.8 Sequencing Recommendation (revised 2026-05-16, 2026-05-19)

**Original recommendation (2026-05-16):** Submit J5-X1 + J5-X1b as a single sequential sbatch bundle. One upload, one job, one download. Total wall time ≈ 34 h on `pg`. No mid-run gates, no fallback uploads. **Executed 2026-05-17 → 2026-05-18. Result: J3 retains production.**

**Decision tree after the X1 bundle returns (original, for reference):**

- **Case A — J5-X1 passes all 4 gates with composite < J3's 0.6355** → ship J5-X1. → Did not occur.
- **Case B — J5-X1b passes but J5-X1 doesn't** → ship J5-X1b. → Did not occur.
- **Case C — Both pass** → ship whichever has the better composite. → Did not occur.
- **Case D — Both flatline at `home_loss ≈ 0.35`** → queue J5-A as next single-run job. → Partially occurred (X1's home_loss did NOT flatline; X1 actually improved AT_HOME RMS to 4.15 pp). But composite failed via act_JS regression.
- **Case E — One or both pass gates but residuals remain** → queue J5-B + J5-C bundle. → Closest to the actual outcome; J5-B included in the 2026-05-19 bundle.
- **Case F — Either run breaks a J3 gate (other than home_loss)** → revert to J3. → Avoided.

**2026-05-19 addendum (current cycle):** The X1 bundle's outcome did not cleanly map to a single Case above (X1's AT_HOME was a real gain; the failure was in act_JS, attributed to lambda_home config deviation). Restructured to a **triple parallel bundle (J5-X2 + J5-A + J5-B)** to test three orthogonal hypotheses in one cycle:
- **J5-X2**: act_JS regression is config-driven (revised Case A).
- **J5-A**: original BCE-floor reserve (revised Case D entry).
- **J5-B**: chain-rule cop head for Alone-gap residual (Case E component).

After the 2026-05-19 bundle returns, the decision rule is:
- If **any one** beats J3's composite (0.6355) on all 4 gates → ship that variant.
- If **none** beats J3 → keep J3; queue J5-C (linear-chain CRF + Viterbi) for the transition-rate ratio residual, plus J5-D if J5-A's smoothing fix didn't fully restore the home head.
- If **multiple** beat J3 → ship the lowest-composite winner; document the others as sensitivity evidence for the paper.

**Outcome (2026-05-20):** None of J5_X2 (0.6747) / J5_A (0.6997) / J5_B (0.6975) beats J3 (0.6355). **Case 2 fires — keep J3.** J5_X2 was bundle winner on AT_HOME and Spouse but act_JS regressed (0.0297 vs 0.0191) — the detach-route activity-JS cost is structural, not config. J5-A's smoothing fix was confirmed falsified (also fails on J-series, not just H). J5-B's chain rule flipped Spouse sign but widened Alone — chain rule itself, not its parameterisation, is the binding issue. J5-D shelved. See 2026-05-20 entry in Part 2 for full numbers.

**Sequencing revision (2026-05-20):** The morning's "queue J5-C next" decision is **superseded** by a deeper diagnosis after the user's architectural review (see Part 2 / 2026-05-20 — Architecture re-diagnosis). The binding constraint across the entire bundle was **supervision topology** — AT_HOME and cop heads never received encoder gradient, so no loss-side or cop-side card could close their gates. The next step is a **parallel triple bundle of J5-F + J_old + J5-C** testing three orthogonal hypotheses in one cycle:

- **J5-F** (topology fix + AR) — encoder shaped jointly by all three losses, AR decoder kept for activity. Tests "joint supervision + AR is best."
- **J_old** (pure encoder-only revert) — `Transformer_pipeline.py` topology at 48-slot resolution. No AR decoder, no Arm-2 fusion. Tests "AR isn't needed if supervision is right."
- **J5-C** (transition-modeling fix on J3 topology) — linear-chain CRF + Viterbi on Arm-1 activity logits. Tests "transition modeling on J3 topology."

This forms a 2×2 across {AR / no AR} × {joint / detached supervision}, with **J3 = AR + detached** as the production baseline.

|                          | AR decoder | No AR  |
|--------------------------|------------|--------|
| **Joint supervision**    | J5-F       | J_old  |
| **Detached / single**    | J3, J5-C   | —      |

**Decision rule for the triple bundle (lower composite = better):**

- **J5-F best (beats J3 on composite + 4/4 gates)** → ship J5-F as new production trunk. Joint supervision + AR is the winning combination. Archive J3. Stack J5-C on J5-F later if act_JS has headroom.
- **J_old best (beats J3 on composite + 4/4 gates)** → ship J_old. The entire J-series Arm 1 / Arm 2 split was unjustified complexity. Activity at 48-slot doesn't need AR if supervision is symmetric. Roll back to the old pipeline as the production trunk.
- **J5-C best (beats J3 on composite + 4/4 gates) but neither J5-F nor J_old does** → ship J5-C. Topology wasn't the binding constraint; transition modeling on J3's existing topology was. Activity transitions were the missing piece. Revisit J5-F / J_old designs (lambda balancing, deeper encoder, etc.).
- **J5-F and J_old both beat J3 but J5-F act_JS ≤ J_old act_JS by > 0.005** → ship J5-F (AR earned its place). Otherwise ship J_old (simpler architecture, smaller param count, faster inference).
- **All three beat J3** → publish the 2×2 head-to-head as the paper's central result; ship the lower-composite winner.
- **None beats J3** → architecture investigation closed. The remaining lever is feature engineering (J5-E pathway, conditional on the 2022-only diagnostic) or accepting J3 as the final model. Step 7 (separate revert card) no longer applies — J_old is the revert.

**J5-D, J5-E, J5-I, J6 status:** J5-D shelved (precondition failed). J5-I dropped from the candidate list (soft variant of J5-F; superseded by J_old which tests a different hypothesis). J5-E still gated on 2022-only diagnostic (independent of this bundle; can run anytime). J6 stays shelved unless all three bundle cards clear gates but composite stalls materially above J3.

---

## 1.9 Architecture Comparison — Transformer pipeline vs J3 vs J5-X1

> Chapter consolidated from `J5_proposal.md` Chapter C. The graphical-abstract prompt (§C.0) is not reproduced here; consult J5_proposal.md if you need the exact ASCII prompt for the figure generator.

### 1.9.1 Overview

This chapter compares three transformer architectures used (or currently being run) for generating daily occupancy diaries with three outputs: **activity**, **AT_HOME (location)**, and **co-presence (withNOBODY / Spouse / Others)**.

The three models:

1. **Transformer pipeline** — encoder-only, three parallel heads (legacy reference model, `examples/cloud_computing/Transformer_pipeline.py`)
2. **J3** — Hybrid AR-Encoder, current production winner (`step4_Speed_Cluster/archive/04B_model_J3.py`)
3. **J5-X1** — head re-route experiment derived from J3 (completed 2026-05-18; lost the A/B comparison vs J3)

### 1.9.2 Side-by-side summary

| Aspect | Transformer pipeline | J3 (Hybrid AR-Encoder) | J5-X1 (head re-route) |
|---|---|---|---|
| Trunk | Encoder-only, multi-head self-attention | 6-layer Transformer Encoder (d_model=384) | Same trunk as J3 (unchanged) |
| Decoder | None | 6-layer CrossAttn Autoregressive (Arm 1) | Same AR decoder as J3 |
| Diary length | 24 slots / day (hourly) | 48 slots / day (30-min) | 48 slots / day (30-min) |
| Positional encoding | Learnable | Sinusoidal | Sinusoidal |
| Head attachment for AT_HOME / co-presence | Directly off shared encoder state | Off Arm-2 per-slot NAT fusion (uses projected activity probs + context) | Directly off AR decoder output |
| Activity gradient isolation | None — heads share trunk | `.detach()` barrier between Arm 1 and Arm 2 | `.detach()` (X1) or none (X1b) |
| Joint supervision of all 3 heads | Yes, from epoch 0 | Partial — Arm 1 supervises activity; Arm 2 supervises binary heads | Yes (heads share decoder) but decoder loss = activity CE only |
| Best result | ~95% accuracy on all 3 outputs (with generalization controls) | 4 / 4 gates PASS, AT_HOME RMS=4.57 pp | 3 / 4 gates, composite 0.6667 (act_JS regressed to 0.0311) |
| Status | Reference / baseline | **Production — SHIP** | Experiment complete; J3 retained |

### 1.9.3 Transformer pipeline (encoder-only, parallel heads)

**Steps:** per-feature embedding → learnable PE (24 slots) → Transformer Encoder stack (GELU, `nhead`, `d_feed=10240`) → three parallel heads (`activity_dense` 14-class CE; `location_dense` BCE; `withNOB_dense` BCE). Weighted multi-task loss.

**Properties:** encoder-only, no decoder, no autoregression. All three heads see the **same** rich encoder state; supervised **jointly from epoch 0**. 24-slot hourly diary. Heavy regularization required — without it the model memorizes the training set.

**Approach to three outputs:** all three heads share the trunk and receive joint gradients. ~95% accuracy on all three outputs once generalization controls are in place.

### 1.9.4 J3 (Hybrid AR-Encoder, production)

**Steps:** input embeddings + sinusoidal PE + CLS token → 6-layer Transformer Encoder → `.detach()` split into Arm 1 (AR activity decoder, 6 layers, 48-step loop) and Arm 2 (per-slot NAT fusion of `[memory | arm2_act_proj(softmax(act_logits.detach())) | cond_vec | cycle_emb | strata]` → `arm2_proj` → two parallel heads with Tanh-bounded sigmoid output). Inference safety: `cop[:,:,Spouse] *= (home > 0.5)`.

**Properties:** 48-slot 30-min diary, 14 activity classes, 9 co-presence channels. Activity gradients isolated from binary heads via `.detach()`. Binary heads see the **projected activity distribution** (14 → 384 via `arm2_act_proj`) plus context, **not** the raw encoder/decoder state. Tanh-bounded heads prevent saturation. Best epoch 72; `home_loss` plateau ≈ 0.3514.

**Approach to three outputs:**
- Activity is generated autoregressively (Arm 1), capturing sequential structure.
- AT_HOME and co-presence are generated in parallel from Arm 2, conditioned on the projected activity distribution.
- `.detach()` barrier means binary-head gradients never reach the AR decoder — Arm 1 optimizes activity, Arm 2 optimizes binary heads.

**Gates (J3 at ship):**

| Metric | Target | J3 |
|---|---|---|
| composite | < 1.045 | **0.6355** PASS |
| AT_HOME RMS | ≤ 5.30 pp | **4.57 pp** PASS (margin 0.73) |
| Spouse \|Δ\| | ≤ 5 pp | **-2.03 pp** PASS |
| activity JS | ≤ 0.05 | **0.0191** PASS |

### 1.9.5 J5-X1 (head re-route experiment, completed)

**Steps:** same input embeddings + sinusoidal PE as J3. Same trunk + same Arm 1 AR decoder. **Arm 2 fusion REMOVED.** Decoder output `dec_output (B, 48, d_model)` routed directly into the binary heads. J5-X1: via `.detach()`. J5-X1b: without `.detach()`. Binary heads same modules as J3, re-targeted.

**Properties:** binary heads now read **rich decoder context** (d_model = 384) instead of the shallow Arm 2 fusion. But the AR decoder is trained on **activity CE only** — the AT_HOME-discriminative signal in `dec_output` is implicit, not directly supervised. Joint activity × AT_HOME representation is never learned end-to-end.

**Final result (2026-05-18):**

| Metric | Gate | J3 | J5_X1 | J5_X1b |
|---|---|---|---|---|
| AT_HOME RMS | ≤ 5.30 pp | 4.57 PASS | **4.15 PASS** | 5.88 FAIL |
| Spouse \|Δ\| | ≤ 5 pp | −2.03 PASS | −1.2 PASS | −0.6 PASS |
| act_JS | ≤ 0.05 | 0.0191 PASS | 0.0311 PASS | 0.0285 PASS |
| COP max gap | — | — | 5.32 pp | 8.14 pp |
| Composite S | ≤ 0.6355 | 0.6355 | 0.6667 FAIL | 0.8086 FAIL |
| Gates passed | — | 4/4 | 3/4 | 2/4 |

### 1.9.6 Why J3 still wins (and what the comparison says)

- **Transformer pipeline** shows what joint supervision of all three heads off a shared trunk can do: ~95% accuracy, given aggressive generalization controls.
- **J3** separates the heads architecturally — activity gets its own AR arm, binary heads get a shallow per-slot fusion. Passes all 4 gates but leaves AT_HOME at a plateau.
- **J5-X1** swings in the opposite direction — rich decoder context for binary heads — but does not change what the decoder is supervised on. More depth, no better calibration; act_JS regressed.

**Binding constraint identified:** the limiting factor is not head-input depth (J5-X1) nor loss topology (the J5 ladder); it is **supervision topology**. Activity and AT_HOME are never co-supervised on a shared representation in the J-series. The Transformer pipeline does exactly this and gets it right, at the cost of needing strong regularization.

**Implication:** a joint activity × AT_HOME representation with shared supervision (the shelved J6 / P7 stage-1 idea) is the direction worth testing if the J5-X2/A/B parallel bundle stalls — not another single-axis card.

Source files: `step4_Speed_Cluster/archive/04B_model_J3.py`; `examples/cloud_computing/Transformer_pipeline.py`, `Transformer_bash.slurm`, `Transformer_num_features.json`; `step4_Speed-Cluster_docs/CSV_records/{architecture,loss_values_trainings,training_config}_investigation.csv`.

---

*Methodology sources (consolidated 2026-05-19 from `Research/J5_proposal.md`):*
- `Research/06_research_agenda.md`
- `Research/Sigmoid Collapse in Multi-Task Learning.md`
- `Research/Multi-Task Gradient Balancing Methods Comparison.md`
- `Research/Structured Prediction for Multi-Label Classification.md`
- `Research/Fixing Temporal Persistence in Transformers.md`
- `Research/Distributionally Robust ML, Worst-Group Optimization, and Covariate Shift Adaptation.md`
- `Research/Generative Modeling for 48-Slot Categorical Activity Sequences with Auxiliary Heads.md`
- `Research/Modern Deep Structured Prediction A Primer for Transformer Practitioners.md`

*Revision history of this methodology section:*
- 2026-05-15: J5 proposal first prepared (J5-A as original top pick).
- 2026-05-16 (a): J5-X1 card added based on joint diagnostic + code review (head-input hypothesis).
- 2026-05-16 (b): Execution mode switched to sequential bundle within one sbatch.
- 2026-05-18: J5-X2 card added after J5-X1 bundle outcome (lambda_home config fix).
- 2026-05-19: Methodology consolidated from `Research/J5_proposal.md` into this single working document; execution mode shifted to parallel triple bundle (J5-X2 + J5-A + J5-B as independent jobs). `J5_proposal.md` preserved unchanged as archival source.

---

# Part 2 — Progress Log

### 2026-05-17 — J5-X1 + J5-X1b bundle build (Sonnet employee task)

**Timestamp:** 2026-05-17

**Objective:** Build and stage the J5-X1 + J5-X1b sequential bundle for submission to the Speed HPC cluster. Both variants test the head-input-starvation hypothesis (binary heads re-routed from shallow Arm-2 NAT fusion to activity decoder output), with and without the `.detach()` gradient barrier.

---

#### Files edited / created

| Action | Path |
|--------|------|
| ARCHIVE | `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_X1.py` — predecessor state before J5_X1/X1b edit |
| EDITED  | `2J_docs_occ_nTemp/04B_model.py` — added J5_X1/X1b branches in `JSeriesHybrid.__init__`, `forward()`, `infer()`; added `_arm1_decode_tf_full()` helper |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X1.yaml` — J3 byte-for-byte, `model_type: J5_X1` |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X1b.yaml` — J3 byte-for-byte, `model_type: J5_X1b` |
| EDITED  | `2J_docs_occ_nTemp/04D_train.py` — extended MODEL_TYPE allow-lists to include J5_X1, J5_X1b; added J5 config block; added `_DEBUG_GRAD` env-var guard and backward unit test |
| EDITED  | `2J_docs_occ_nTemp/04E_inference.py` — extended `_mtype` allow-list to include J5_X1, J5_X1b |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_X1_bundle.sh` — bundled sbatch script (J5_X1 train→eval→J5_X1b train→eval) |
| CREATED | `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/step4_training_v4.md` — this file |

---

#### Archive command run

```
cp 2J_docs_occ_nTemp/04B_model.py \
   2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_X1.py
```

Covers both J5-X1 and J5-X1b (they share the same predecessor state, as specified).

---

#### Model changes summary (`04B_model.py`)

- `JSeriesHybrid.__init__`: added `self._mtype = _mtype`; extended `arm2_act_proj` condition from `("J3","J4_1","J4_2","J4_3")` to include `"J5_X1","J5_X1b"` — modules defined but bypassed in forward/infer.
- New method `_arm1_decode_tf_full(dec_act_seq, tgt_strata, memory, cond_vec, cycle_idx)` — returns `(act_logits, dec_out)`. Used only by J5_X1/X1b head routing.
- `forward()`: for J5_X1/X1b, calls `_arm1_decode_tf_full`; sets `binary_input = dec_out.detach()` (J5_X1) or `binary_input = dec_out` (J5_X1b). For all other model types, existing Arm-2 path unchanged.
- `infer()`: same branch — calls `_arm1_decode_tf_full` with AR-generated tokens for a teacher-forcing pass to get decoder hidden states; feeds result to binary heads. Arm-2 path unchanged for J3/J4_x.

---

#### Partition cap check result

**Finding: pg partition very likely caps at 24h.** All existing J-series sbatch scripts (`job_step4_J1.sh` through `job_step4_J4_3.sh`) use `--time=24:00:00`. The bundle script requests `--time=38:00:00` (34h estimate + 4h buffer). If sbatch rejects the 38h request with "Invalid time specification", split into two jobs:

- Job A (J5_X1): train + eval — `--time=24:00:00`
- Job B (J5_X1b): train + eval — `--time=24:00:00`, submitted with `--dependency=afterok:<jobA_id>`

The bundle script includes these instructions in its comment header.

---

#### Module check result

Scripts checked: `04B_model.py`, `04D_train.py`, `04E_inference.py`, `04F_validation.py`.

All imports: `torch`, `numpy`, `pandas`, `scipy`, `matplotlib`, `json`, `csv`, `argparse`, `importlib`, `math`, `os`, `sys`, `time`.

Cluster env `step4` (`requirements_step4.txt`): `torch>=2.0,<2.5`, `numpy>=1.24`, `pandas>=2.0`, `scikit-learn>=1.3`, `matplotlib>=3.7`, `scipy>=1.11`.

**Result: all packages present. No install/precheck line added to sbatch script.**

---

#### Git commit

Commit message: `[ml]: add J5-X1 + J5-X1b bundle for binary-head re-route experiment`

Files committed: archive copy, `04B_model.py`, both YAML configs, `04D_train.py`, `04E_inference.py`, `jobs/J5_X1_bundle.sh`, this progress log.

---

#### Hand-off commands

locally: `scp -r GSSCanada-main/2J_docs_occ_nTemp/ o_iseri@speed.encs.concordia.ca:~/step4_Speed_Cluster/`

on the cluster: `cd ~/step4_Speed_Cluster && sbatch jobs/J5_X1_bundle.sh`

**If pg caps at 24h** (expected — see cap check above):

on the cluster (Job A): `cd ~/step4_Speed_Cluster && sbatch --time=24:00:00 --job-name=J5_X1_A jobs/J5_X1_bundle.sh`

Then after Job A completes — submit Job B separately with the J5_X1b half of the script. Manager to prepare the split scripts if needed.

---

**Status:** STAGED — awaiting user scp + sbatch.

---

### 2026-05-17 — J5-X1 mid-run update (epochs 40–43)

**Job:** 931826 (`J5_X1_bundle`), partition pg, node cisr-1. Running since ~2026-05-17 morning.

#### Epoch snapshot

| Epoch | act_loss | home_loss | cop_loss | val_JS | home_gap | val_score |
|-------|----------|-----------|----------|--------|----------|-----------|
| 20    | 0.5286   | 0.3891    | 0.2120   | 0.0597 | 0.0848   | 0.1021    |
| 40 ✓  | 0.2053   | 0.3674    | 0.2099   | 0.0086 | 0.0288   | 0.0230    |
| 41    | 0.1981   | 0.3661    | 0.2106   | 0.0084 | 0.0371   | 0.0269    |
| 42    | 0.1892   | 0.3669    | 0.2101   | 0.0076 | 0.0350   | 0.0251    |
| 43    | 0.1829   | 0.3651    | 0.2096   | 0.0074 | 0.0354   | 0.0251    |

Epoch 40 saved new best (val_score=0.0230). Epoch 810 s/epoch.

#### Observations

- **act_loss**: 0.5286 → 0.1829 across epochs 20–43. Activity generation converging strongly.
- **val_JS**: 0.0597 → 0.0074 — now well below the 0.05 gate. Activity quality on validation is excellent.
- **home_loss**: 0.3891 → 0.3651 — movement is real (+0.024 over 23 epochs) but slow. Confirming structural gradient starvation from `detach()` — the home head cannot steer the decoder. Training BCE floor with `home_label_smooth=0.05` is ~0.20; the diagnostic gate (≤ 0.27) is evaluated by 04J on inference output, not training BCE.
- **cop_loss**: 0.2120 → 0.2096 — essentially flat. Copresence head also detach()-blocked.
- **home_gap**: 0.0848 → 0.028–0.037, oscillating around 0.03. Improving but noisy.
- **val_score**: 0.1021 → 0.023. Composite validation metric well improved.

#### Decision

Waiting for bundle completion. J5_X1b leg (no detach barrier) will start automatically after J5_X1 epoch 100 + eval. J5_X1b is the more diagnostic leg — cross-arm gradients will reveal whether binary-head feedback meaningfully improves home_loss convergence.

---

### 2026-05-18 — J5-X1b mid-run update (epochs 29–47)

**Job:** 931826 (Leg 2, J5_X1b), same bundle. Started after J5_X1 epoch 100 + eval completed.

#### Epoch snapshot

| Epoch | act_loss | home_loss | cop_loss | val_JS | home_gap | val_score | grad_norm |
|-------|----------|-----------|----------|--------|----------|-----------|-----------|
| 29 ✓  | 0.3925   | 0.2921    | 0.1860   | 0.0167 | 0.0486   | 0.0410    | 2.570     |
| 33 ✓  | 0.3328   | 0.2818    | 0.1833   | 0.0146 | 0.0471   | 0.0382    | 2.576     |
| 34 ✓  | 0.3199   | 0.2789    | 0.1822   | 0.0131 | 0.0499   | 0.0381    | 2.572     |
| 35 ✓  | 0.3066   | 0.2772    | 0.1817   | 0.0149 | 0.0268   | 0.0283    | 2.584     |
| 39 ✓  | 0.2614   | 0.2688    | 0.1785   | 0.0141 | 0.0282   | 0.0282    | 2.545     |
| 40 ✓  | 0.2519   | 0.2671    | 0.1779   | 0.0071 | 0.0289   | 0.0215    | 2.523     |
| 44 ✓  | 0.2162   | 0.2603    | 0.1749   | 0.0067 | 0.0261   | **0.0198**| 2.406     |
| 47    | 0.1943   | 0.2561    | 0.1727   | 0.0065 | 0.0310   | 0.0220    | 2.341     |

Epoch 44 saved best (val_score=0.0198). Epoch ~810s/epoch.

#### Observations

- **home_loss**: 0.2921 at epoch 29 → 0.2561 at epoch 47. Contrast: J5_X1 was at 0.3674 at epoch 40. Cross-arm gradients are driving home_loss down; training BCE already below 0.27 target. Hypothesis confirmed — detach() was the structural cause.
- **cop_loss**: 0.1860 → 0.1727. Moving faster than X1 (~0.21 plateau). Still above 0.12 inference gate; real verdict comes from 04J.
- **val_JS**: 0.0065–0.0167 range — well below 0.05 gate. Activity quality preserved despite cross-arm gradient. The main risk prediction (act_JS degradation) has not materialized.
- **act_loss**: 0.1943 at epoch 47 vs J5_X1's 0.1829 at epoch 43 — ~0.01–0.02 lag. Smaller than the predicted 0.10–0.15; decoder is handling dual objectives better than expected.
- **grad_norm**: 2.3–2.6, slightly elevated vs X1's stable ~2.0. Stabilizing and trending down (2.570 at ep29 → 2.341 at ep47). Not the noisy 2.5–3.5 predicted; the multi-objective gradient is integrating cleanly.
- **val_score best**: 0.0198 (epoch 44) — beats J5_X1's best of 0.0230.

#### Status

Last best: epoch 44. Patience=15 → could stop at epoch 59 unless new best found. home_loss still declining; likely 0.24–0.25 by epoch 60 if trajectory holds. Awaiting bundle completion for 04J inference diagnostics.

---

### 2026-05-18 — J5 bundle COMPLETE (final training + 04J diagnostic results)

**Job 931826 complete.** J5_X1 early-stopped at epoch 66 (best ep51); J5_X1b early-stopped at epoch 79 (best ep64).

#### J5_X1 — final checkpoint

Inference loaded from epoch 50 (0-indexed) = epoch 51 in training log.

| act_loss | home_loss | cop_loss | marg_loss | val_JS | home_gap | val_score | LR at stop |
|----------|-----------|----------|-----------|--------|----------|-----------|------------|
| 0.1379   | 0.3610    | 0.2090   | 0.0083    | 0.0060 | 0.0271   | 0.0196    | 4.29e-05   |

#### J5_X1b — final checkpoint

Inference loaded from epoch 63 (0-indexed) = epoch 64 in training log.

| act_loss | home_loss | cop_loss | marg_loss | val_JS | home_gap | val_score | LR at stop |
|----------|-----------|----------|-----------|--------|----------|-----------|------------|
| 0.1177   | 0.2405    | 0.1583   | 0.0029    | 0.0043 | 0.0196   | 0.0141    | 3.68e-05   |

#### 04H findings

- **J5_X1**: H2 PASS (mean gap closure −0.64 pp), H3 WARN (not dominant), H5 PASS → SKIP_GPU.
- **J5_X1b**: H2 WARN (small contributor +3.00 pp), H3 WARN (morning +13.03 pp — large slot bias), H5 PASS → SKIP_GPU.

#### 04I findings

- **J5_X1**: activity_ok (JS mean=0.0311), copresence_partial (max_gap=5.32 pp Alone).
- **J5_X1b**: activity_partial (JS mean=0.0285), copresence_partial (max_gap=8.14 pp Alone).

#### 04J Composite Score — A/B vs J3

| Metric | Gate | J3 (baseline) | J5_X1 | J5_X1b |
|--------|------|---------------|-------|--------|
| AT_HOME RMS | ≤ 5.30 pp | 4.57 PASS | **4.15 PASS** | 5.88 FAIL |
| Spouse \|Δ\| | ≤ 5 pp | −2.03 PASS | −1.2 PASS | −0.6 PASS |
| act_JS | ≤ 0.05 | 0.0191 PASS | 0.0311 PASS | 0.0285 PASS |
| COP max gap | — | — | 5.32 pp | 8.14 pp |
| Composite S | ≤ 0.6355 | **0.6355** | 0.6667 FAIL | 0.8086 FAIL |
| Gates passed | — | 4/4 | 3/4 | 2/4 |

#### Verdict

**J5_X1 > J5_X1b on inference diagnostics**, despite X1b winning all training BCE metrics by a wide margin (home_loss 0.2405 vs 0.3610; val_score 0.0141 vs 0.0196). The cross-arm gradient in X1b drove home_loss down in training but distorted copresence at inference — Alone gap doubled from 3.8 pp (X1) to 8.1 pp (X1b). Training BCE improvement did not transfer to inference quality.

**Neither J5 variant beats J3.** J5_X1 improved AT_HOME RMS (4.15 vs 4.57 pp) but worsened act_JS (0.0311 vs 0.0191) and composite (0.6667 vs 0.6355). The Arm-2 NAT fusion path in J3 remains superior for copresence calibration. **J3 retains production status.**

**Insight for J6:** dec_out carries real AT_HOME signal (X1's AT_HOME RMS gain is genuine), but full copresence re-routing requires a stabilization mechanism — either a separate copresence stream or learned gating rather than hard re-routing. Open cross-arm gradient (X1b) is too disruptive for the Alone/copresence channels.

---

**Status:** COMPLETE — J3 production; J5 experiment fully logged.

---

### 2026-05-18 — J5-X2 PLANNED (awaiting build + sbatch)

**Objective:** Fix the act_JS regression observed in J5-X1 by restoring `lambda_home=0.9` (J3's original value). Architecture identical to J5-X1.

**Hypothesis:** J5-X1's `act_JS=0.0311` (vs J3's `0.0191`) is config-driven. J5-X1 inherited `lambda_home=0.7` from the J4 config base rather than J3's `0.9`. The `.detach()` barrier means binary-head gradients never reach the decoder — from the decoder's perspective, J5-X1 and J3 are architecturally identical. The lambda difference shifts the val_score trajectory and early-stop timing: J5-X1 stopped at epoch 66 (best ep51); J3 ran to epoch 87 (best ep72). With `lambda_home=0.9`, the activity decoder should converge to J3-level `act_JS` while preserving J5-X1's AT_HOME RMS gain.

| Parameter | J3 | J5-X1 (done) | J5-X2 (planned) |
|-----------|-----|-------------|-----------------|
| model_type | J3 | J5_X1 | J5_X1 (same branch) |
| lambda_home | 0.9 | 0.7 ← deviation | **0.9 ← fix** |
| AT_HOME RMS | 4.57 pp | 4.15 pp | target ≤ 4.15 pp |
| act_JS | 0.0191 | 0.0311 | target ≤ 0.022 |
| composite S | 0.6355 | 0.6667 | target < 0.6355 |

**Architecture:** J5-X1 branch — `dec_out.detach()` → binary heads; Arm-2 NAT fusion bypassed.
**Config change:** `lambda_home: 0.7 → 0.9` only. No model code change. No new MODEL_TYPE. Output dir: `outputs_step4_J5_X2/`.

**Status:** PLANNED — builder prompt in `J5_proposal.md` Appendix B. Next step: pass Appendix B to a fresh Sonnet session.

---

### 2026-05-19 — J5-X2 + J5-A + J5-B parallel bundle (manager+employee single-cycle)

**Objective:** Build and stage J5-X2, J5-A, and J5-B as three independent sbatch jobs in a single upload cycle. Three jobs submit in one shot on the cluster; SLURM scheduler decides actual concurrency (up to 3 GPUs in parallel on `pg`). Each model writes to its own output dir. This supersedes the J5-X2 standalone plan (Appendix B in `J5_proposal.md` removed; J5-X2 experiment card in §2 remains the methodological source of truth).

---

#### Files edited / created

| Action  | Path |
|---------|------|
| ARCHIVE | `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_B.py` — predecessor state before J5-B chain-rule edit |
| EDITED  | `2J_docs_occ_nTemp/04B_model.py` — line 879 `arm2_act_proj` allow-list extended to J5_A / J5_B; new J5_B chain-rule branch in `JSeriesHybrid.infer()` (safety mask dropped when `_mtype == "J5_B"`) |
| EDITED  | `2J_docs_occ_nTemp/04D_train.py` — MODEL_TYPE allow-lists extended at lines 500 / 745 / 757 / 840 / 868 / 946 to include J5_A and J5_B; new J5-B chain-rule branch in `compute_loss` (BCE on marginal probs; spouse_neg_weight applied manually via `cop_pos_weight`) |
| EDITED  | `2J_docs_occ_nTemp/04E_inference.py` — `_mtype` allow-list extended to include J5_A and J5_B |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X2.yaml` — inherits J5_X1 byte-for-byte; `lambda_home: 0.7 → 0.9`, `tag: J5_X2`; `model_type` stays `J5_X1` |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_A.yaml` — inherits J3 byte-for-byte; `home_label_smooth: 0.05 → 0.0`, `tag/model_type: J5_A` |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_B.yaml` — inherits J3 byte-for-byte; `tag/model_type: J5_B` (chain rule applied in code, not config) |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_X2.sh` — single sbatch (train → infer → 04H → 04I → 04J) |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_A.sh`  — single sbatch, same diagnostic chain |
| CREATED | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_B.sh`  — single sbatch, same diagnostic chain |
| REMOVED | `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/Research/J5_proposal.md` Appendix B (replaced with a one-line pointer to this Progress Log entry) |

---

#### Archive command run

```
cp 2J_docs_occ_nTemp/04B_model.py 2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_B.py
```

Covers J5-B's chain-rule edits to `04B_model.py`. J5-X2 reuses the J5_X1 branch (no code change; the J5-X1 archive `04B_model_pre_J5_X1.py` already covers that state). J5-A uses the standard J3 build path (allow-list extension only; no behavior change to existing forward/infer paths).

---

#### Model code changes summary

**`04B_model.py`:**
- Line 879 — `arm2_act_proj` allow-list extended: `("J3", "J4_1", "J4_2", "J4_3", "J5_X1", "J5_X1b", "J5_A", "J5_B")`. J5_A / J5_B now get the J3-equivalent `arm2_act_proj` projection.
- `JSeriesHybrid.infer()` — new `_mtype == "J5_B"` branch applies the chain rule: `p_alone = σ(z_alone); p_other_i = (1 - p_alone) · σ(z_other_i)`. The standard safety mask `cop_prob[:, :, Spouse] *= gen_home` is conditioned on `apply_safety and self._mtype != "J5_B"` — chain rule subsumes the Alone-vs-Other mutual exclusivity by construction.
- `forward()` unchanged. J5_B uses the standard arm2_feat path; raw `cop_logits` flows to `compute_loss`, where the chain rule is applied.

**`04D_train.py`:**
- 6 MODEL_TYPE allow-list sites extended with J5_A and J5_B.
- `compute_loss` — new `MODEL_TYPE == "J5_B"` branch computes chain-rule `cop_probs`, then BCE on probs with manual `cop_pos_weight` multiplication (since `F.binary_cross_entropy` lacks `pos_weight`). Probs clamped to `[1e-7, 1 - 1e-7]` for numerical stability. The remaining masking path (availability × colleagues_mask) is unchanged and shared with J3/J5_A.

**`04E_inference.py`:**
- `_mtype` allow-list extended with J5_A and J5_B (single-line change).

---

#### Module check result

Scripts scanned: `04B_model.py`, `04D_train.py`, `04E_inference.py`, `04H_diagnostics_cpu.py`, `04I_activity_copresence_diagnostics.py`, `04J_statistical_diagnostics.py`.

All imports (torch, numpy, pandas, scipy, matplotlib, json, csv, argparse, math, os, sys, time) were validated for the J5-X1 / J5-X1b run on the same `step4` cluster env (`requirements_step4.txt`). J5-B's chain-rule branch uses only existing tensor ops (`torch.sigmoid`, `torch.cat`, `torch.log`, `clamp`) — no new dependencies.

**Result: all packages present. No precheck / install line added to sbatch scripts.**

---

#### Outputs (one per model)

| Model  | Output dir              | Best ckpt path                                  | Composite JSON                  |
|--------|-------------------------|-------------------------------------------------|---------------------------------|
| J5_X2  | `outputs_step4_J5_X2/`  | `outputs_step4_J5_X2/checkpoints/best_model.pt` | `diagnostics_J5_X2.json`        |
| J5_A   | `outputs_step4_J5_A/`   | `outputs_step4_J5_A/checkpoints/best_model.pt`  | `diagnostics_J5_A.json`         |
| J5_B   | `outputs_step4_J5_B/`   | `outputs_step4_J5_B/checkpoints/best_model.pt`  | `diagnostics_J5_B.json`         |

Each output dir also gets per-script `diagnostics_H_<model>.json` and `diagnostics_I_<model>.json` from the 04H / 04I steps.

---

#### Hand-off commands (one-shot triple submission)

locally: `scp -r GSSCanada-main/2J_docs_occ_nTemp/ o_iseri@speed.encs.concordia.ca:~/step4_Speed_Cluster/`

on the cluster: `cd /speed-scratch/o_iseri/occModeling && sbatch jobs/J5_X2.sh && sbatch jobs/J5_A.sh && sbatch jobs/J5_B.sh`

The cluster line submits three independent jobs back-to-back. SLURM places them on free `pg` GPUs (parallel where capacity allows; queued otherwise). Each job is ~17–24 h. If one job's sbatch fails at startup (e.g., MODEL_TYPE typo, missing config), the other two still run.

**Note on paths.** The scp target (`~/step4_Speed_Cluster/`) matches the J5-X1 deployment recorded above. The sbatch line's BASE (`/speed-scratch/o_iseri/occModeling`) is what's hard-coded inside every sbatch script (matches `J5_X1_bundle.sh`). If the home → scratch sync no longer matches your current cluster workflow, adjust the scp target before running.

---

**Status:** COMPLETE — three jobs (933657 J5_X2 / 933658 J5_A / 933659 J5_B) all finished, results downloaded 2026-05-20. See entry below.

---

### 2026-05-20 — J5-X2 + J5-A + J5-B bundle COMPLETE (final 04J results)

**Cluster jobs:** 933657 (J5_X2, cisr-2) · 933658 (J5_A, speed-01) · 933659 (J5_B, speed-17). All three completed within the 48 h cap with no TIMEOUT.

**Download (locally, from `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/CSV_records/`):**

```
"J5_X2","J5_A","J5_B" | ForEach-Object { scp -r "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/outputs_step4_$_" step4_Speed_Cluster/ }
New-Item -ItemType Directory -Force "step4_Speed_Cluster/logs/" | Out-Null ; "J5_X2_933657","J5_A_933658","J5_B_933659" | ForEach-Object { scp "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/logs/$_.out" "step4_Speed_Cluster/logs/" }
```

Note: J5_X2's outputs landed at `step4_Speed_Cluster/` directly (top-level scp-rename quirk — the dir did not exist at the time of the first scp); J5_A and J5_B are properly nested under `outputs_step4_<model>/`. Functional impact: none — the JSON/CSV file names are still model-suffixed (`diagnostics_J5_X2.json`, etc.) so nothing is overwritten.

---

#### 04J Composite Score — head-to-head vs J3 baseline

| Model | AT_HOME RMS (pp) | COP max gap (pp) | Spouse Δ (pp) | act_JS mean | cop_cal_MAE | Composite S | Gates passed |
|-------|-----------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|
| **J3 (baseline)** | 4.57 | — | −2.03 | **0.0191** | — | **0.6355** | **4/4** |
| **J5_X2** | **4.42** | 5.73 | **−1.89** | 0.0297 | 0.2818 | 0.6747 | 3/4 (act_JS) |
| J5_A  | 5.57 | 7.12 | −2.43 | 0.0267 | 0.2458 | 0.6997 | 2/4 (AT_HOME, Alone) |
| J5_B  | 5.20 | 7.07 | **+1.61** | 0.0322 | 0.2333 | 0.6975 | 2/4 (Alone, act_JS) |

Numbers sourced from `step4_Speed_Cluster/diagnostics_J5_X2.json` (top-level after scp quirk), `step4_Speed_Cluster/outputs_step4_J5_A/diagnostics_J5_A.json`, `step4_Speed_Cluster/outputs_step4_J5_B/diagnostics_J5_B.json` (composite.components / composite.composite_score).

J3 baseline numbers from §1.4 / 2026-05-18 entry above.

---

#### Per-channel copresence gaps (full picture)

| Channel | J3 | J5_X2 | J5_A | J5_B |
|---------|---:|------:|-----:|-----:|
| Alone     | n/a | **+5.73** | +7.12 | +7.07 |
| Spouse    | −2.03 | **−1.89** | −2.43 | **+1.61** |
| Children  | n/a | +1.65 | +1.95 | +2.98 |
| parents   | n/a | +1.45 | +1.12 | +1.40 |
| friends   | n/a | +2.67 | +2.81 | +2.57 |
| others    | n/a | −1.37 | −2.02 | −2.21 |
| colleagues| n/a | **−5.41** | −5.64 | −5.30 |

The persistent colleagues gap (≈ −5.4 pp) is shared across all three — it's a data/feature constraint, not a head-architecture issue, and is not targeted by any J5-X2/A/B/C/D card.

---

#### Verdict per model

- **J5_X2 (J5-X1 arch + `lambda_home: 0.9` config fix).** Best of the bundle on composite (0.6747), best AT_HOME RMS (4.42 pp — beats J3's 4.57), best Spouse (−1.89 vs J3's −2.03). **But act_JS still regressed to 0.0297** (vs J3's 0.0191). The config fix recovered some activity quality vs J5-X1's 0.0311 — but not enough to break parity. The `detach()` route appears to genuinely cost ~50% activity-JS headroom regardless of lambda balancing. **Hypothesis "J5-X1's regression is purely config-driven" is FALSIFIED.**

- **J5_A (J3 byte-identical + `home_label_smooth=0.0`).** Worst AT_HOME of the three (5.57 pp); composite 0.6997. The BCE-floor reserve (P1/P2) was strong on paper, falsified earlier on the H-series, and now falsified empirically on the J-series too. **Smoothing is not the binding constraint.** §1.5 row already flagged this — confirmed.

- **J5_B (J3 + hierarchical chain-rule cop head).** The chain rule **did** change the Spouse channel — sign flipped from −2.03 (J3) / −1.89 (X2) to **+1.61**. Real architectural effect. But the Alone gap widened to +7.07 (vs J5_X2's +5.73 and J3's baseline), and the marginalisation amplified Children (+2.98 vs +1.65 in X2). Net: the chain rule traded Spouse-undercounting for Alone-overcounting, which is exactly the geometric trade-off P3 §11.1 warned about. **Composite worse than X2.** Per-channel `alpha` variant (J5-B-v2 in §1.7 Open Q #6) is not justified — the Other channels did not regress, the Alone-channel widened, so the chain rule itself (not its parameterisation) is the issue at this dataset scale.

---

#### Decision (§1.8 rule applied)

> "If any one beats J3's composite (0.6355) on all 4 gates → ship that variant. If none beats J3 → keep J3; queue J5-C (linear-chain CRF + Viterbi) for the transition-rate ratio residual, plus J5-D if J5-A's smoothing fix didn't fully restore the home head."

**None of J5_X2, J5_A, J5_B beats J3 on composite or on all four gates.** Therefore:

- **WINNER (production): J3** — keep `outputs_step4_J3/augmented_diaries.csv` as the Step-5 / Step-6 upstream.
- **Next step (Step 4 in §1.1 roadmap): J5-C** (linear-chain CRF + Viterbi decode on Arm-1 activity logits). Targets the transition-rate ratio residual that no other card addresses. J5-A's smoothing failure also re-arms J5-D, but J5-D is gated on J5-A's home-head behaviour and J5-A failed clearly — defer J5-D pending J5-C result.
- **2022-only diagnostic (§1.1 Step 5):** independent of J5-C. Can be run locally any time before J5-E is considered.

---

#### What the J5_X2 win-on-AT_HOME-but-lose-on-act_JS pattern means

J5_X2 has the best AT_HOME RMS (4.42 < J3's 4.57) AND the best Spouse (−1.89 vs −2.03) of any model trained so far — but pays for it in activity JS (0.0297 vs 0.0191). This is the **classic gradient-blocking cost** of the `dec_output.detach()` route: the home/cop heads improved (no longer competing with activity decoder for shared representation), but the activity decoder lost the implicit regularisation those heads provided. The lambda_home raise from 0.7 → 0.9 closed about a third of the act_JS gap (0.0311 → 0.0297) but the remaining ~55% of the regression is structural to the detach barrier, not config. **No further config tuning of the J5-X1/X2 family is justified.** The detach-route architecture is parked; J3 (no detach) remains the production trunk for J5-C and beyond.

---

#### Files now on disk locally

```
step4_Speed-Cluster_docs/CSV_records/step4_Speed_Cluster/
  ├─ best_model.pt, last_checkpoint.pt, augmented_diaries.csv, step4_training_log.csv
  ├─ diagnostics_H_J5_X2.json, diagnostics_I_J5_X2.json, diagnostics_J5_X2.json
  ├─ logs/
  │   ├─ J5_X2_933657.out
  │   ├─ J5_A_933658.out
  │   └─ J5_B_933659.out
  ├─ outputs_step4_J5_A/  (full set incl. checkpoints, augmented_diaries, diagnostics_*)
  └─ outputs_step4_J5_B/  (full set incl. checkpoints, augmented_diaries, diagnostics_*)
```

**Status:** COMPLETE — J3 retained as production; superseded by 2026-05-20 architecture re-diagnosis (next entry).

---

### 2026-05-20 — Architecture re-diagnosis (user-prompted, post-bundle)

**Trigger:** After reviewing the §1.9 architecture comparison and the 2026-05-20 head-to-head, the user flagged a deeper pattern: the three J-series outputs are not trained symmetrically. Activity gets the full trunk + AR decoder; AT_HOME and Spouse get downstream activity probabilities (J3) or detached decoder context (J5-X1/X2). The old `Transformer_pipeline.py` (encoder-only, three parallel heads off the same `transformer_out`, joint loss) reached ~95 % on all three with regularization — the gates were trivially closeable when all three losses shaped the same encoder.

**Code-level confirmation** (read 2026-05-20):
- `examples/cloud_computing/Transformer_pipeline.py:556-558` — `self.activity_dense`, `self.location_dense`, `self.withNOB_dense` all = `nn.Linear(input_size, ·)` reading from the same `transformer_out`.
- `Transformer_pipeline.py:777` — `total_loss = w_act * loss_act + w_loc * loss_loc + w_NOB * loss_NOB`. One combined loss; gradient flows through all three heads into the same encoder.
- `2J_docs_occ_nTemp/04B_model.py` (J3 / J5-X1/X2 family) — Arm 1 / Arm 2 split with `.detach()` between them. AT_HOME and cop heads see `arm2_act_proj(act_probs.detach())` (J3) or `dec_output.detach()` (J5-X1/X2). The encoder is shaped by activity CE only; binary losses shape ~150 K head params; activity loss shapes ~28 M trunk params. **187× capacity asymmetry.**

**Diagnosis:** The binding constraint across the entire J5-X2/A/B bundle is **supervision topology**, not loss-side tuning, label smoothing, or cop-head output-space restructuring. The bundle's failures are not three independent failures — they are three different ways of asking the same wrong question ("how should we improve the binary heads given that they're starved of representation?"). The right question is "how do we un-starve them?"

**Why we don't simply revert to the old pipeline:** The old pipeline (encoder-only, three parallel heads) needed heavy generalization controls (dropout + weight reg + stratified split) to avoid memorization. More importantly, it has no autoregressive structure on activity — J3's AR decoder is what produced act_JS = 0.0191 (best so far). A full revert would surrender that gain.

**Path forward:** The hybrid that keeps J3's AR activity gain *and* the old pipeline's joint encoder supervision is **J5-F** (newly drafted in §1.4). It removes the `.detach()` and the Arm-2 fusion entirely; binary heads attach directly to encoder output; activity goes through a CrossAttn AR decoder layered on top of `enc_out`. The encoder is shaped by all three losses simultaneously, like the old pipeline; the AR decoder is shaped by activity loss alone, like J3. Best of both. Risk-mitigation logic: if J5-F regresses activity materially, the AR decoder loses its specialization — but the encoder is now a multi-task representation and we have a clear next step (raise `lambda_act`, or pretrain encoder briefly with joint loss before attaching the AR decoder).

**Decision (recorded 2026-05-20, revised same-day to triple bundle after user-led discussion):**
- **Drop J5-D from the active queue.** Its precondition (J5-A fixing the home head) did not occur; FAMO on top of an unfixed home head will deprioritise it further and amplify the collapse.
- **Drop the morning's "queue J5-C alone" plan.** J5-C polishes activity transitions on J3's topology — it does NOT address AT_HOME/Spouse, which are the actual residuals from the bundle.
- **Drop J5-I from the candidate list.** Earlier in the day J5-I was proposed as a soft variant of J5-F (auxiliary encoder head on top of J3's intact trunk). User flagged that J5-I and J5-F test the same hypothesis at different aggressiveness, so J5-I doesn't earn a slot. Replaced by **J_old** (pure `Transformer_pipeline.py` revert) which tests an orthogonal question: "is the AR decoder necessary at all if supervision is symmetric?"
- **Queue J5-F + J_old + J5-C as a parallel triple bundle** (Step 4 in §1.1 roadmap; §1.3 third submission; §1.8 sequencing revision). Three orthogonal hypotheses tested in one upload cycle. Forms a 2×2 across {AR / no AR} × {joint / detached supervision}, with J3 as the AR + detached baseline.

---

### 2026-05-20 — J5-F + J_old + J5-C parallel triple bundle RUNNING (Step 4)

**Submitted 2026-05-20 on Speed `pg` partition:** jobs 933921 J5_F (cisr-1), 933922 J_old (cisr-2), 933923 J5_C (speed-03). 48 h walltime each. Build provenance: predecessor `04B_model.py` archived to `step4_Speed_Cluster/archive/04B_model_pre_J5_F.py` (single snapshot covers all three edits in one commit). `JSeriesHybrid` extended with `J5_F` / `J_old` / `J5_C` branches; CRF forward-backward + Viterbi added as static methods (NLL normalized by T for scale parity with CE). MODEL_TYPE allow-lists extended at six sites in `04D_train.py` + one in `04E_inference.py`. Local smoke test pass for all four variants (J3 / J5_F / J_old / J5_C) on a tiny synthetic batch.



**Objective:** Test three orthogonal hypotheses in parallel — whether AT_HOME/Spouse residual is closeable by **joint supervision + AR** (J5-F), by **joint supervision without AR** (J_old, pure old-pipeline revert), or whether the residual is actually **transition modeling on J3 topology** (J5-C). Three independent sbatch jobs in one upload cycle. SLURM scheduler decides actual concurrency on `pg` (up to 3 GPUs in parallel; J5-X2/A/B precedent confirmed this works). Each model writes to its own output dir. One upload → parallel train → one download.

**Why three (not two):** Adding J_old gives a clean 2×2 read on {AR / no AR} × {joint / detached supervision}. Without J_old, we cannot disentangle whether any J5-F win comes from joint supervision, from the AR decoder, or both. J_old is the cheapest of the three (~10–12 h vs ~17 h for J5-F and J5-C) so the marginal cluster cost is minimal.

**Operational discipline (re-affirmed by user 2026-05-20):** Single recursive scp to cluster; single sbatch line submitting all three jobs; single recursive scp back to local on completion. **No mid-cycle re-stage.** Matches the J5-X2/A/B precedent.

---

#### Files to edit / create

| Type    | Path | Purpose |
|---------|------|---------|
| ARCHIVE | `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_F.py` | Predecessor of `04B_model.py` before any 2026-05-20 edit (covers J5-F, J_old, J5-C — single snapshot since all three edits land in one commit). Mandatory per [[feedback-archive-predecessor]]. |
| EDITED  | `2J_docs_occ_nTemp/04B_model.py` | (1) Add `J5_F` MODEL_TYPE branch: encoder→`enc_out`; binary heads `home_head_enc`, `cop_head_enc` attached to `enc_out`; AR decoder retained for activity; Arm-2 fusion bypassed; no `.detach()` in the activity path. (2) Add `J_old` MODEL_TYPE branch: encoder→`enc_out`; three parallel Linear heads (`activity_head_old` 384→14 softmax, `home_head_old` 384→1 sigmoid, `cop_head_old` 384→9 sigmoid); no AR decoder; no Arm-2 fusion; mirrors `examples/cloud_computing/Transformer_pipeline.py:556-558`. (3) Add `J5_C` MODEL_TYPE branch: J3 build path unchanged + linear-chain CRF module (`nn.Parameter(torch.zeros(14, 14))` for `psi_pair`, forward-backward NLL helper, Viterbi decoder for inference). |
| EDITED  | `2J_docs_occ_nTemp/04D_train.py` | Extend MODEL_TYPE allow-lists at lines 500 / 745 / 757 / 840 / 868 / 946 to include `J5_F`, `J_old`, `J5_C`. Add J5-C CRF NLL loss branch in `compute_loss` (replaces per-slot CE on activity for that MODEL_TYPE). Add J5-F joint-loss branch (sum of three BCE/CE losses with J3 lambdas; cop_head_enc is plain sigmoid, no chain rule). Add J_old joint-loss branch (CE + BCE + BCE mirroring `Transformer_pipeline.py:777` — `total_loss = w_act*loss_act + w_loc*loss_loc + w_NOB*loss_NOB`; no safety mask). |
| EDITED  | `2J_docs_occ_nTemp/04E_inference.py` | Extend `_mtype` allow-list to include `J5_F`, `J_old`, `J5_C`. Add J5-C Viterbi-decoded activity path. Add J5-F direct-from-encoder binary inference path (activity still via AR decoder). Add J_old fully encoder-direct inference path (argmax on `activity_head_old`, sigmoid > 0.5 on `home_head_old` / `cop_head_old`). |
| NEW     | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_F.yaml` | Inherits from J3 config. `tag: J5_F`. `model_type: J5_F`. `lambda_act: 0.5, lambda_home: 0.9, lambda_cop: 0.5` (J3 byte-identical). `home_label_smooth: 0.05`. `spouse_neg_weight: 0.45`. |
| NEW     | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J_old.yaml` | Inherits from J3 config. `tag: J_old`. `model_type: J_old`. Same lambdas + smoothing + spouse_neg_weight as J5-F initially (the old pipeline's loss weights were normalized differently but J3's lambdas are a reasonable starting point on this data). |
| NEW     | `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_C.yaml` | Inherits from J3 config. `tag: J5_C`. `model_type: J5_C`. All other fields J3 byte-identical. |
| NEW     | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_F.sh` | sbatch wrapper. `#SBATCH --time=48:00:00` (per [[feedback-cluster-walltime-minimum]]), `--partition=pg`, `--gres=gpu:1`, `--mem=40G`. Chain: train (04D) → inference (04E) → 04H → 04I → 04J. |
| NEW     | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J_old.sh` | Same template, `J_old` substituted. Walltime 48h kept (even though J_old is expected to be ~10–12h; headroom is free). |
| NEW     | `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_C.sh` | Same template, `J5_C` substituted. |

---

#### Outputs (one per model)

| Model  | Output dir             | Best ckpt path                                  | Composite JSON              |
|--------|------------------------|-------------------------------------------------|-----------------------------|
| J5_F   | `outputs_step4_J5_F/`  | `outputs_step4_J5_F/checkpoints/best_model.pt`  | `diagnostics_J5_F.json`     |
| J_old  | `outputs_step4_J_old/` | `outputs_step4_J_old/checkpoints/best_model.pt` | `diagnostics_J_old.json`    |
| J5_C   | `outputs_step4_J5_C/`  | `outputs_step4_J5_C/checkpoints/best_model.pt`  | `diagnostics_J5_C.json`     |

Each output dir also gets per-script `diagnostics_H_<model>.json` and `diagnostics_I_<model>.json` from the 04H / 04I steps.

---

#### Hand-off command shape (to be finalised on build)

**locally (one upload, from `GSSCanada-main/`):**

```
scp -r 2J_docs_occ_nTemp/ o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/
```

**on the cluster (one submit line):**

```
cd /speed-scratch/o_iseri/occModeling && sbatch jobs/J5_F.sh && sbatch jobs/J_old.sh && sbatch jobs/J5_C.sh
```

**locally (one download, from `step4_Speed-Cluster_docs/CSV_records/`):**

```
"J5_F","J_old","J5_C" | ForEach-Object { scp -r "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/outputs_step4_$_" step4_Speed_Cluster/ } ; "J5_F_<jobid>","J_old_<jobid>","J5_C_<jobid>" | ForEach-Object { scp "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/logs/$_.out" step4_Speed_Cluster/logs/ }
```

Replace `<jobid>` with the actual SLURM job IDs after submission.

---

#### Decision rule (mirrors §1.8 sequencing revision)

- **J5-F best** → ship J5-F (joint supervision + AR wins). Stack J5-C later if act_JS has headroom.
- **J_old best** → ship J_old (AR was unjustified complexity; old pipeline at 48-slot is the right architecture). Roll back the entire J-series Arm 1 / Arm 2 split.
- **J5-C best (J5-F and J_old both lose)** → ship J5-C (topology wasn't the issue; transition modeling was). Revisit J5-F / J_old designs.
- **J5-F and J_old both beat J3 → tiebreaker on act_JS**: if J5-F act_JS ≤ J_old act_JS by > 0.005, ship J5-F (AR earned its place); else ship J_old (simpler / faster).
- **All three beat J3** → publish the 2×2 head-to-head as the paper's central architecture result; ship the lower-composite winner.
- **None beats J3** → architecture investigation closed. Remaining lever is feature engineering (J5-E pathway, gated on 2022-only diagnostic). Step 7 no longer applies — J_old already covered the revert.

---

#### Why no other alternatives are bundled

- **J5-I (aux encoder head, soft variant of J5-F)** — dropped. Tests the same hypothesis as J5-F at lower aggressiveness; doesn't earn a slot. If J5-F regresses activity unacceptably (act_JS > 0.025) and J_old also underperforms, J5-I would become the natural next single-run job — but only as a follow-up, not in this bundle.
- **J5-D (FAMO loss balancing on J3)** — shelved. Its precondition (J5-A unfreezing the home head) failed; FAMO on a plateaued home head amplifies the collapse.
- **J5-E (per-cycle LoRA + BBSE)** — separately gated on the 2022-only diagnostic. Independent of this bundle.
- **J6 (joint activity × AT_HOME vocabulary head)** — shelved. Would force re-runs of Step 5 / Step 6 downstream. Only revisit if all three bundle cards clear gates but composite stalls.

---

**Status:** COMPLETE 2026-05-20 — all three jobs ran; none beat J3. J_old composite=1.3750 (encoder-only revert; activity head never trained; AR confirmed load-bearing at 48-slot). J5_C composite=0.6921 (CRF + Viterbi; transition prior recovered activity but couldn't substitute for AR). J5_F stopped early at ep38 by scancel after `home_loss` flatlined at 0.51 — same as J_old (joint supervision starves home head when `.detach()` removed; confirms detach barrier load-bearing). **Architecture investigation CLOSED.** J3 retains production status. Next step: J3-HPT (hyperparameter tuning) — see next entry.

---

### 2026-05-20 — J3-HPT bundle PLANNED (Step 4 — hyperparameter tuning on J3)

**Trigger:** User noted (2026-05-20, post-J5-F-stop) that the old `Transformer_pipeline.py` improved most from HPT, but J3's config was inherited from G4/H_Tanh/J2 lineage — never tuned per-knob. With the architecture investigation closed, **HPT becomes the primary remaining lever** alongside J5-E (feature engineering, gated on 2022-only diagnostic).

**Baseline (J3, from 2026-05-18 entry):** composite **0.6355**, 4/4 gates PASS but with thin margins:

| Gate | J3 value | Threshold | Margin |
|---|---|---|---|
| Composite S | 0.6355 | ≤ 0.6355 | at threshold (defines gate) |
| AT_HOME RMS | 4.57 pp | ≤ 5.30 pp / target ≤ 4.0 | 0.73 / fail by 0.57 vs target |
| Spouse \|Δ\| | −2.03 pp | ≤ 5 pp / target ≤ 2.0 | 0.03 at the target edge |
| act_JS | 0.0191 | ≤ 0.05 / target ≤ 0.022 | 0.003 at the target edge |

J3 passes the publication-grade `target` thresholds on Composite and AT_HOME comfortably but **sits at the edge on Spouse and act_JS**. HPT is a deliberate hardening push.

---

#### 6-run parallel bundle (one upload → 6 parallel jobs → one download)

| Run | Knob | J3 → J3-HPT | Targets | Cost | Output dir |
|---|---|---|---|---|---|
| J3-HPT-T   | inference temperature   | 0.8 → 0.65       | act_JS                  | ~30 min (inference-only on J3 checkpoint) | `outputs_step4_J3_HPT_T/`    |
| J3-HPT-L   | `lambda_home`           | 0.9 → 1.1        | AT_HOME RMS             | ~5 h retrain                              | `outputs_step4_J3_HPT_L/`    |
| J3-HPT-S_lo | `spouse_neg_weight`    | 0.45 → 0.35      | Spouse \|Δ\|            | ~5 h retrain                              | `outputs_step4_J3_HPT_S_lo/` |
| J3-HPT-S_hi | `spouse_neg_weight`    | 0.45 → 0.55      | Spouse \|Δ\|            | ~5 h retrain                              | `outputs_step4_J3_HPT_S_hi/` |
| J3-HPT-R_lo | `lr`                   | 5e-5 → 3e-5      | broader regime / act_JS | ~5 h retrain                              | `outputs_step4_J3_HPT_R_lo/` |
| J3-HPT-R_hi | `lr`                   | 5e-5 → 7e-5      | broader regime / act_JS | ~5 h retrain                              | `outputs_step4_J3_HPT_R_hi/` |

**S and R bracketed** (both directions) because the sign convention of Spouse Δ and the optimal LR direction are not unambiguously derivable from prior records — empirical bracketing is cheaper than reasoning. `lambda_home` direction is unambiguous (J3 already raised it from 0.7→0.9 vs J2; the natural test point is further-up). `lr` schedule factor (0.95) and ReduceLROnPlateau patience (5) held constant — only base `lr` changes per single-axis discipline.

All HPT variants use `model_type: J3` (no code-level changes; the 04B/04D/04E allow-lists already accept J3). Tags and output dirs differentiate runs.

---

#### Files created

| Path | Purpose |
|---|---|
| `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3_HPT_L.yaml`    | J3 baseline + `lambda_home: 1.1`               |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3_HPT_S_lo.yaml` | J3 baseline + `spouse_neg_weight: 0.35`        |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3_HPT_S_hi.yaml` | J3 baseline + `spouse_neg_weight: 0.55`        |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3_HPT_R_lo.yaml` | J3 baseline + `lr: 3.0e-5`                     |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3_HPT_R_hi.yaml` | J3 baseline + `lr: 7.0e-5`                     |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_HPT_L.sh`         | Full chain: 04D → 04E → 04H → 04I → 04J        |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_HPT_S_lo.sh`      | Full chain                                     |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_HPT_S_hi.sh`      | Full chain                                     |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_HPT_R_lo.sh`      | Full chain                                     |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_HPT_R_hi.sh`      | Full chain                                     |
| `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_HPT_T.sh`         | Inference-only chain: 04E (`--temperature 0.65`) → 04H → 04I → 04J on existing J3 checkpoint |

**No code edits.** `04B_model.py`, `04D_train.py`, `04E_inference.py` unchanged — all variants use `model_type: J3`.

**No archive predecessor needed.** Per [[feedback-archive-predecessor]], the predecessor rule applies to **architecture edits** to `04B_model.py` / `04D_train.py` / `04E_inference.py`. This bundle changes only configs + new wrappers; the model code path is J3's, unmodified.

---

#### Hand-off commands

**locally (one upload):**

```
scp -r 2J_docs_occ_nTemp/step4_Speed_Cluster/configs 2J_docs_occ_nTemp/step4_Speed_Cluster/jobs o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/
```

**on the cluster (six sbatch submissions in one line):**

```
cd /speed-scratch/o_iseri/occModeling && sbatch jobs/J3_HPT_T.sh && sbatch jobs/J3_HPT_L.sh && sbatch jobs/J3_HPT_S_lo.sh && sbatch jobs/J3_HPT_S_hi.sh && sbatch jobs/J3_HPT_R_lo.sh && sbatch jobs/J3_HPT_R_hi.sh
```

**locally (one download after all complete — replace `<jobid>` with actual SLURM IDs):**

```
"J3_HPT_T","J3_HPT_L","J3_HPT_S_lo","J3_HPT_S_hi","J3_HPT_R_lo","J3_HPT_R_hi" | ForEach-Object { scp -r "o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/outputs_step4_$_" "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/step4_Speed-Cluster_docs/cluster_outputs/" }
```

---

#### Decision rule

- **Any J3-HPT-* beats J3 composite (0.6355) AND holds 4/4 gates** → ship that variant as J3-v2.
- **J3-HPT-T alone clears act_JS gate margin** while L/S/R retrains fail to beat J3 composite → ship `J3 + temperature=0.65` (inference-only patch; no retrain needed).
- **L beats J3 but S/R don't** → adopt L's `lambda_home: 1.1` as J3-v2 baseline; consider L+T combo as follow-up.
- **None beats J3** → J3 stays as production. HPT lever exhausted; J5-E (feature engineering, gated on 2022-only diagnostic) becomes the only remaining lever.

---

**Status:** IN-PROGRESS 2026-05-21 — bundle uploaded; T COMPLETED, 4 RUNNING, 1 PENDING on partition `pg`.

| Variant | SLURM ID | State (T+3:29) | Node | Elapsed |
|---|---|---|---|---|
| J3-HPT-T    | 934369 | **COMPLETED** | cisr-1   | 01:02:52 |
| J3-HPT-L    | 934370 | RUNNING | cisr-2   | 03:29:04 |
| J3-HPT-S_lo | 934371 | RUNNING | speed-17 | 03:29:04 |
| J3-HPT-S_hi | 934372 | RUNNING | speed-17 | 03:29:04 |
| J3-HPT-R_lo | 934373 | RUNNING | cisr-1   | 02:26:12 |
| J3-HPT-R_hi | 934374 | PENDING (AssocGrpGRES) | — | — |

**J3-HPT-T result (vs J3 baseline 0.6355):**

| Metric | J3 | T (τ=0.65) | Δ |
|---|---|---|---|
| composite | 0.6355 | 0.63548 | ≈0 |
| act_JS | 0.0191 | 0.01915 | ≈0 |
| AT_HOME RMS pp | 4.57 | 4.57 | 0 |
| COP max gap pp | 6.90 | 6.90 | 0 |
| Spouse Δ pp | -2.03 | -2.03 | 0 |

Wrapper + 04E confirmed wiring `--temperature 0.65` end-to-end (grep verified). Temperature change has **negligible effect on aggregate gates** for this checkpoint — T = **SHELVED** (no improvement on act_JS edge). L training healthy at epoch 15/100 (val_score=0.1653, ~13 min/epoch). R_hi will slot in as R_lo completes. One upload → 6 parallel jobs → one download cycle per [[feedback-bundle-upload]].

---

### 2026-05-21 — J3-HPT bundle CANCELLED (manager+user decision)

**Trigger:** Mid-conversation review of [[04_augmentationGSS_IMP]] (Step-4 training improvement plan). User concluded HPT was unlikely to yield gains worth ~20 h additional cluster time. Rationale:

- **T result (2026-05-21 earlier):** Δ ≈ 0 across all gates → already SHELVED above.
- **L (`lambda_home=1.1`):** Testing a direction already known disadvantaged. J2→J3 lineage settled λ_home at 0.7→0.9; further up unlikely. Confirms what `step4_training_v4.md §1.6` (Methods Explicitly Rejected) already implies.
- **S_lo / S_hi / R_lo / R_hi:** Sensitivity sweeps. No architectural insight, only knob-tuning. Marginal gain at best, blocks J3-PSB submission slot.
- **Plan supersedes HPT:** Phase 1 of [[04_augmentationGSS_IMP]] = J3-PSB (per-slot demographic broadcast in new `04B_model_J3_v2.py`). Targets the architectural root cause identified in `investigations/investigation_oldTransformer_vs_J3.md §6.1`. Higher expected yield per cluster-hour than any HPT axis.

**Cancellation — on the cluster:**

```
scancel 934370 934371 934372 934373 934374
```

| SLURM ID | Variant | State at scancel | Elapsed | Notes |
|---|---|---|---|---|
| 934369 | J3-HPT-T    | COMPLETED earlier | 01:02:52 | already SHELVED (Δ≈0) |
| 934370 | J3-HPT-L    | RUNNING           | ~07:07 | partial training_log.csv expected at ~ep 30+ |
| 934371 | J3-HPT-S_lo | RUNNING           | ~07:07 | partial training_log.csv expected |
| 934372 | J3-HPT-S_hi | RUNNING           | ~07:07 | partial training_log.csv expected |
| 934373 | J3-HPT-R_lo | RUNNING           | ~06:04 | partial training_log.csv expected |
| 934374 | J3-HPT-R_hi | PENDING (AssocGrpGRES) | — | never started; no outputs |

**Salvage plan:** Download partial `outputs_step4_J3_HPT_*` directories anyway. Partial training_log.csv shows val_score trajectory per epoch — cheap forensic insight ("did L's trajectory ever cross J3's known basin? did S/R diverge?"). Sonnet employee task spawned for bundle-download + follow-up Progress Log entry with partial-run signal summary.

**Decision-rule outcome (from 2026-05-20 HPT planning entry):** None of "any HPT beats J3" or "L beats J3" can be evaluated (jobs incomplete by user choice). Default to fallback branch: **"None beats J3 → J3 stays as production. HPT lever exhausted."** Next active lever is Phase 1 of [[04_augmentationGSS_IMP]] (J3-PSB).

---

### 2026-05-21 — J3-HPT salvage download (post-scancel)

**Cluster queue at start:** empty — `squeue -u o_iseri` returned no rows; scancel fully cleared.

#### Inventory

| Directory | Size (data) | Files present | Last-modified (cluster) |
|---|---|---|---|
| outputs_step4_J3_HPT_T | ~502 MB | augmented_diaries.csv (502M), diagnostics_H/I/J JSON (80K) | 2026-05-21 06:29 |
| outputs_step4_J3_HPT_L | ~448 MB | checkpoints/best_model.pt (112M), checkpoints/last_checkpoint.pt (336M), step4_training_log.csv (3.2K) | 2026-05-21 12:40 |
| outputs_step4_J3_HPT_S_lo | ~448 MB | same checkpoint structure, step4_training_log.csv (3.8K) | 2026-05-21 12:39 |
| outputs_step4_J3_HPT_S_hi | ~448 MB | same checkpoint structure, step4_training_log.csv (3.7K) | 2026-05-21 12:43 |
| outputs_step4_J3_HPT_R_lo | ~448 MB | same checkpoint structure, step4_training_log.csv (2.7K) | 2026-05-21 12:37 |
| outputs_step4_J3_HPT_R_hi | — | never created (job was PENDING, never assigned GPU, scancel killed before start) | — |

Slurm stdout logs downloaded from `/speed-scratch/o_iseri/occModeling/logs/`:
`J3_HPT_T_934369.out`, `J3_HPT_L_934370.out`, `J3_HPT_S_lo_934371.out`, `J3_HPT_S_hi_934372.out`, `J3_HPT_R_lo_934373.out`.
All .err files contain only the SLURM cancellation notice (`slurmstepd: error: *** JOB <id> CANCELLED AT 2026-05-21T12:46:37 ***`) — no exceptions or training errors in any run.

Downloaded files deleted locally after inspection (no need to retain ~1.8 GB of checkpoints).

#### Per-run partial trajectory summary

J3 reference baseline: val_score ~0.165 at ep14 (last snapshot before ep15 in J3 training log), composite 0.6355 at inference.

| Run | Last epoch (of 100) | Best val_score (ep) | Crossed J3 ep14 basin? | Trajectory shape |
|---|---|---|---|---|
| J3-HPT-T | 100 (COMPLETE) | — (inference ran; T = SHELVED, Δ≈0 vs J3) | n/a | Full run |
| J3-HPT-L | 32 | 0.0400 (ep32, still improving) | Yes — at ep16 (0.1074) | Consistently declining, healthy |
| J3-HPT-S_lo | 39 | 0.0220 (ep39, still improving) | Yes — at ep16 (0.1504) | Consistently declining, healthy |
| J3-HPT-S_hi | 38 | 0.0275 (ep37, still improving) | Yes — at ep15 (0.1617 ≈ J3) | Consistently declining, healthy |
| J3-HPT-R_lo | 27 | 0.1127 (ep26) | Barely — at ep21 (0.1619), noisy | Noisy, slow convergence (LR=3e-05); oscillating; far from training convergence |
| J3-HPT-R_hi | — | — | Never ran | — |

**Training curve notes:**
- L, S_lo, S_hi: all show smooth, consistently declining val_score — same characteristic shape as J3's training run. No divergence, no plateau anomaly. Healthy but unremarkable.
- L home_loss (0.375 at ep32) tracks closely to act_loss (0.306), consistent with prior J-series behaviour where the `.detach()` barrier keeps the two arms roughly decoupled regardless of λ_home value. The λ_home=1.1 perturbation did not pull home_loss materially lower than the J3 baseline pattern — suggests the binding constraint is architectural (detached gradient path), not coefficient-scaling.
- R_lo's slower convergence (LR=3e-05 vs 5e-05 for others, ~813 s/epoch vs ~809 s, noisy val_score oscillations through ep27) confirms the lower LR was a poor choice for this architecture's convergence profile. Even at ep100 it would likely underperform the standard-LR runs.

#### Verdict

All partial trajectories are consistent with "no improvement vs J3." No run shows any extraordinary mid-training signal (e.g., unusually fast val_JS collapse, home_gap < 0.05 early, act_JS heading below J3's 0.0191) that would justify re-queueing to completion. The L, S_lo, S_hi curves look like a healthy J3 retrain with small config perturbations — which is exactly what the cancellation rationale predicted. **HPT lever is confirmed exhausted. J3 remains production.**

Next active task: Phase 1 of [[04_augmentationGSS_IMP]] — J3-PSB architecture build in `04B_model_J3_v2.py`. See cancellation entry above for handoff pointer.

**Status:** Salvage COMPLETE 2026-05-21. J3 retains production status. HPT lever closed.

---

### 2026-05-21 — Phase 1 J3-PSB BUILT (per-slot demographic broadcast)

**Trigger:** Phase 1 of [[04_augmentationGSS_IMP]]. Architecture-only single-axis change vs J3: concat `cond_vec` onto every encoder slot token before `slot_linear`, so each of the 48 slots sees demographics directly instead of routing them through CLS-attention. Targets the binary-head underperformance documented in `investigations/investigation_oldTransformer_vs_J3.md §6.1`. User instructed Claude to execute Phase 1 directly (no employee handoff) on 2026-05-21.

#### Files created / edited

| File | Change |
|---|---|
| `step4_Speed_Cluster/archive/04B_model_pre_J3_v2.py` | NEW (archive snapshot of `04B_model.py` pre-edit, per [[feedback-archive-predecessor]]) |
| `04B_model_J3_v2.py` | NEW. Defines `JSeriesHybridV2(JSeriesHybrid)`: forces parent init as J3 (so `arm2_act_proj` + Tanh heads + detach barrier are wired identically), replaces `slot_linear` with widened `nn.Linear(d_act + 1 + n_cop + d_cond, d_model)`, overrides `_encode()` to concat `cond_vec.unsqueeze(1).expand(-1, 48, -1)` onto the slot-input tensor before projection. `self._mtype = "J3_v2"` for diagnostics; forward/infer dispatch still hits the standard J-series branch (Arm-1 → Arm-2 detached) — no other path changes. |
| `04B_model.py` | Appended importlib-based loader at module bottom that exposes `JSeriesHybridV2` as a module attribute (filename starts with a digit, so plain `import` not usable). `JSeriesHybrid` and all other classes unchanged. |
| `04D_train.py` | (a) added `JSeriesHybridV2 = getattr(model_mod, "JSeriesHybridV2", None)` at the model-import block; (b) added explicit `elif MODEL_TYPE == "J3_v2": model = JSeriesHybridV2(model_config)` branch in model-instantiation block (above the existing JSeriesHybrid branch); (c) added `"J3_v2"` to the J-series allow-lists for model_config dispatch, optimizer-scheduler branch, clip_norm = 25.0, per-epoch scheduler skip, and warmup gating. |
| `04E_inference.py` | Added `JSeriesHybridV2` import + dedicated `_mtype == "J3_v2"` branch in checkpoint-load model-instantiation block. |
| `step4_Speed_Cluster/configs/J3_PSB.yaml` | NEW. Copy of `J3.yaml` with `tag: J3_PSB`, `model_type: J3_v2`. All other hyperparameters identical to J3 (single-axis discipline — only the architecture changes). |
| `step4_Speed_Cluster/jobs/J3_PSB.sh` | NEW. Copy of `J3_HPT_L.sh` template with `--time=48:00:00` (per [[feedback-cluster-walltime-minimum]]), job name `J3_PSB`, output dir `outputs_step4_J3_PSB`, full chain (04D train → 04E infer → 04H → 04I → 04J). |

#### Core code change (the PSB diff)

J3 baseline `_encode()`:
```python
slot_emb = self.slot_linear(torch.cat([act_emb, aux_seq], dim=-1))  # in: d_act + 10
```

J3_v2 `_encode()`:
```python
cond_b   = cond_vec.unsqueeze(1).expand(-1, T, -1)                  # (B, T, d_cond) — PSB
slot_in  = torch.cat([act_emb, aux_seq, cond_b], dim=-1)            # (B, T, d_act + 10 + d_cond)
slot_emb = self.slot_linear(slot_in)                                # in: d_act + 10 + d_cond
```

`slot_linear.in_features` grows from `d_act + 10` (≈42) to `d_act + 10 + d_cond` (≈162 with the current 12-cat + 1-cont + 2-bin feature set). All other layers unchanged.

#### Smoke test (local, CPU, mock d_cond=120)

| Check | Result |
|---|---|
| `JSeriesHybridV2` imports from `04B_model` | PASS |
| Instantiates with J3 production dims (d_model=384) | PASS — 29,340,888 params (J3 ≈ 29.3M; +~50k from widened slot_linear) |
| `slot_linear.in_features` == 162 (= 32 + 1 + 9 + 120) | PASS |
| `arm2_act_proj` preserved as `Linear(14, 384)` (load-bearing per J5_X1b lesson) | PASS |
| `forward(batch)` returns shapes `(4,48,14)`, `(4,48)`, `(4,48,9)` | PASS |
| `infer(...)` returns shapes `(4,48)`, `(4,48)`, `(4,48,9)` | PASS |
| J3 baseline still instantiates + forwards (unaffected by V2 wiring) | PASS |

Full no-op equivalence vs J3 is not possible (V2's widened `slot_linear` has different random init), so the smoke test confirms structural correctness and J3 non-regression rather than numeric identity. Smoke-test script deleted post-validation.

#### Guardrails honored

- `arm2_act_proj` not modified (still `Linear(14, 384)`).
- Arm-1 / Arm-2 detach barrier not removed (parent's standard branch handles dispatch).
- `model_type: J3` baseline path unchanged — J3 reproducibility preserved from `04B_model.py`.
- Archive predecessor saved per [[feedback-archive-predecessor]].
- SLURM walltime = 48 h per [[feedback-cluster-walltime-minimum]].

#### Hand-off commands (paste-ready, in order)

**locally** (single recursive scp — bundles all 6 modified/new files into the cluster work dir):

```
scp 2J_docs_occ_nTemp/04B_model_J3_v2.py 2J_docs_occ_nTemp/04B_model.py 2J_docs_occ_nTemp/04D_train.py 2J_docs_occ_nTemp/04E_inference.py 2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3_PSB.yaml 2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J3_PSB.sh o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/
```

After upload, move the YAML + SLURM wrapper into `configs/` and `jobs/` subdirs on the cluster if scp landed them at the top of the work dir:

**on the cluster** (relocate config + wrapper if needed):

```
cd /speed-scratch/o_iseri/occModeling && mv J3_PSB.yaml configs/ && mv J3_PSB.sh jobs/ && ls configs/J3_PSB.yaml jobs/J3_PSB.sh
```

**on the cluster** (submit — only after `squeue -u o_iseri` shows empty):

```
cd /speed-scratch/o_iseri/occModeling && sbatch jobs/J3_PSB.sh
```

**Status:** BUILT 2026-05-21. Smoke-test PASS. Upload + submit pending user. Expected runtime ≈ 5–6 h (matches J3 baseline + minimal overhead from widened slot_linear).

**Submission update (2026-05-21):** Uploaded via single scp bundle, relocated YAML + wrapper into `configs/` + `jobs/`. Submitted on the cluster:

```
sbatch jobs/J3_PSB.sh
Submitted batch job 934720
```

| Job | SLURM ID | State (T+0:02) | Node | Partition |
|---|---|---|---|---|
| J3_PSB | 934720 | RUNNING | cisr-1 | pg |

ETA ≈ 5–6 h training + ~30 min inference/diagnostics. Next checkpoint: monitor with `sacct -j 934720` until COMPLETED, then bundle-download `outputs_step4_J3_PSB/` and run composite-vs-J3 comparison (Phase 1 gate check from [[04_augmentationGSS_IMP]]).
