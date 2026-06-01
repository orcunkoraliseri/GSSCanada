# Step-4 J5 Ladder Proposal — Synthesis of 7 Deep-Research Prompts

Prepared 2026-05-15. Synthesises the seven LLM responses in `Research/` into a ranked J5 ladder. J3 (4/4 gates) is the production floor; every J5 candidate must hold composite < 1.045, AT_HOME RMS ≤ 5.3 pp, Spouse ≤ 5 pp, act_JS ≤ 0.05 with no regression vs J3 (4.57 / −2.03 / 0.0191, composite 0.6355).

---

## J5 roadmap — checklist (revised 2026-05-16, bundle execution)

**Execution mode: single sbatch bundle.** One upload, one job, one download. The job script trains J5-X1 to completion, then trains J5-X1b to completion, in sequence on the same GPU. Both checkpoints, both `04F` validation reports, and both diagnostic dumps come back in the same `outputs_step4_J5_X1_bundle/` directory. No mid-run decision gates — both runs go to full completion so you have a clean A/B comparison offline. Total wall time ≈ 34 h on `pg`.

- [x] **Step 1: Upload bundle** — DONE 2026-05-17. model code (J5-X1 + J5-X1b MODEL_TYPE branches), configs, training/inference scripts, and bundle sbatch script uploaded.
- [x] **Step 2: Submit one sbatch job** — DONE 2026-05-17. Job 931826, pg/cisr-1, 38h wall time accepted.
- [x] **Step 3: Download bundle** — DONE 2026-05-18. Training logs (`J5_X1_training_log.csv`, `J5_X1b_training_log.csv`) + diagnostic JSONs (04H/04I/04J for both) pulled to `step4_Speed_Cluster/outputs/`.
- [x] **Step 4: A/B compare offline** — DONE 2026-05-18. Outcome: **neither beats J3**. J5-X1 wins A/B (3/4 gates, composite 0.6667; AT_HOME RMS 4.15 pp ↑; act_JS 0.0311 ↓ regressed). J5-X1b worse (2/4 gates, composite 0.8086; cross-arm gradient distorted copresence — Alone gap 8.1 pp). act_JS regression in J5-X1 attributed to `lambda_home=0.7` config deviation (J3 used 0.9). Case: partial → **J5-X2 queued** (config fix before escalating to J5-A/B/C).
- [ ] **Step 4b: Build and stage J5-X2** — J5-X1 arch (`dec_out.detach()` → binary heads) + `lambda_home: 0.9` (restored to J3 value). Config-only fix; no new MODEL_TYPE; no model code change. Single sbatch job (~17 h on pg). See **Appendix B** builder prompt.
- [ ] **Step 5 (independent): 2022-only diagnostic run** — train on 2022 alone; if it can't beat 5 pp, shelve J5-E (not algorithm-fixable).
- [ ] **Step 6: If diagnostic passes → build J5-E** (per-cycle LoRA + BBSE) targeting the 2022×WD 9.69 pp cell.
- [ ] **Step 7 (only if J5-X1/B/C all pass but composite stalls) → escalate to J6** (joint activity × AT_HOME vocabulary head).

### Count (revised 2026-05-16, bundle execution)

- **Sbatch submissions (minimum case, J5-X1 or J5-X1b wins):** 1 bundle = 2 trainings, ~34 h.
- **Sbatch submissions (median case, J5-X1 wins → cop residuals trigger J5-B/C):** 2 bundles = 4 trainings, ~68 h.
- **Sbatch submissions (worst case, head-input hypothesis falsified):** 3+ bundles (X1+X1b bundle, J5-A solo, J5-D solo, J5-B+C bundle, optional J5-E + J6).
- **Architecture trials:** 4 (J5-X1, J5-B, J5-C, J6). J5-X1 and J5-X1b are both two-line forward-pass re-routes (`.detach()` on vs off); J5-A and J5-D are loss/config-only; J5-E adds LoRA modules but reuses the J3 trunk.

---

## 1. Executive Summary

**Top pick: J5-X1 + J5-X1b sequential bundle.** Counter-finding 2026-05-16 from joint CSV + code review: J5-A's load-bearing claim (P2 §5 — that `home_loss=0.3514` sits at the ε=0.05 BCE floor of 0.198) does not hold for the J-series. The H-series (H_Tanh, H_Time, G4) used the same `ε=0.05` and reached `home_loss ≈ 0.22` — i.e. *at* the predicted floor. J-series sits ~0.13 *above* the floor at the same ε, and the gap appeared the instant the architecture split into Arm 1 (activity AR decoder) + Arm 2 (NAT fusion for home/cop). cop_loss shows the same 3× regression (0.0675 → 0.1919). The binding constraint is what *feeds* the binary heads, not what the loss penalises. None of the 7 deep-research docs discuss head-input depth (independent re-scan 2026-05-16) — the entire J5-A through J5-E ladder rests on loss-side / gradient-balancing / structured-prediction fixes that assume a single shared trunk.

**Execution mode: single sbatch bundle, both cards trained sequentially to completion.** J5-X1 (re-route home/cop heads to `dec_output.detach()`) and J5-X1b (re-route without the detach barrier — accepts cross-arm gradient flow into the activity decoder) test the *same hypothesis* with vs without the gradient barrier. Bundling both into one job (~34 h total on `pg`) collapses the X1 → X1b → re-decide upload/download cycle into one upload, one sbatch, one download, with both checkpoints in hand for offline A/B comparison. **If either J5-X1 or J5-X1b beats J3, the head-input hypothesis is confirmed and the entire J5-A → D → E loss-side reserve becomes irrelevant. If both flatline at home_loss ≈ 0.35, the hypothesis is falsified and J5-A is queued next.**

**Original top pick: J5-A — set `home_label_smooth = 0.0`.** Held as the reserve fallback only if the X1 bundle falsifies the head-input hypothesis (both variants flatline). Cards 2–5 (HMC cop head, linear-chain CRF, FAMO weighting, per-cycle LoRA) target other residual axes but carry larger surgery footprints and weaker consensus.

## 1a. Decisions locked (2026-05-15, revised 2026-05-16)

- **First submission: J5-X1 + J5-X1b sequential bundle (revised 2026-05-16, bundle mode).** Single sbatch job; trains J5-X1 to completion (~17 h), then trains J5-X1b to completion (~17 h), back-to-back on the same GPU. Both checkpoints, both `04F` reports, both diagnostic dumps come back together. No mid-run gates, no fallback uploads. Total wall time ≈ 34 h on `pg` (verify against partition cap before submit). The J5-B/C parallel cadence is **not** triggered automatically — wait on the bundle's offline A/B comparison first.
- **J5-A held as reserve fallback (revised 2026-05-16).** Queued as a separate single-run job *only if* the X1 bundle shows both J5-X1 and J5-X1b flatline at `home_loss ≈ 0.35` (head-input hypothesis falsified). Original J5-A rationale (P1+P2 BCE-floor argument) is falsified for the J-series by the CSV record: H-series reached `home_loss ≈ 0.22` at the same `ε=0.05`, so smoothing is not the binding constraint for the J-series — but if the head-input fix doesn't work either, J5-A is the next-best loss-side reserve.
- **J6 — joint activity × AT_HOME vocabulary head (P7 §1 stage 1) is shelved.** Single-prompt recommendation; would force a 14→28 Arm-1 softmax rewrite, invalidate the J3 checkpoint, and force re-runs of Step 5 (Census Linkage, complete) and Step 6 (Longitudinal Forecasting, in flight). Defensible escalation only if J5-A/B/C all pass gates but composite stalls materially above J3's 0.6355 with no further loss-side headroom. Not in the J5 scope.
- **Open question #1 resolved.** If J5-A's `home_label_smooth=0.0` fails to break `home_loss` from the 0.36 plateau by smoke ep 5–10, fall to J5-D (FAMO) stacked on J5-A — *not* the inverted-ASL variant. P2's zero-gradient argument is load-bearing.
- **Open question #2 deferred.** Linear-chain CRF is the J5-C entry point; semi-Markov is the reactive J5-C2 only if linear-chain underperforms on the 158× transition-rate ratio.
- **Open question #3 — 2022×WD diagnostic precondition.** Before J5-E build, run a 2022-only single-cycle diagnostic; if it cannot beat 5 pp on 2022 alone, J5-E is shelved (per P5 §Caveat 4 — feature-engineering problem, not algorithmic).

---

## 2. The 7 Ranked Experiment Cards

> J5-X1 and J5-X1b are **bundled** — submitted as a single sequential sbatch job. They are listed as separate cards because the architectural decision (with vs without `.detach()` barrier) is independent enough to warrant its own gates and risk analysis, even though execution is collapsed into one upload/run/download cycle.

### J5-X1 — Re-route binary heads to the activity decoder output (`dec_output.detach()`)

- **Method** — In `JSeriesHybrid.forward` and `.infer`, change the binary heads' input from the Arm 2 fusion tensor (`arm2_feat`) to the activity decoder's output (`dec_output`) with a `.detach()` barrier preserving the J-series no-cross-arm-gradient invariant. Concretely: `self.home_head(arm2_feat)` → `self.home_head(dec_output.detach())`, identically for `self.cop_head`. Arm 2 fusion code (`_arm2_fuse`, `arm2_proj`, `arm2_act_proj`) is bypassed for the heads (kept on disk for revert) but no longer in the forward path. The home/cop head modules themselves are byte-identical to J3 (Tanh → Linear → Sigmoid, d_model=384 → 1 / → 9). No loss change. Config is J3 byte-for-byte (`lambda_home=0.9`, `home_label_smooth=0.05`, `spouse_neg_weight=0.45`, etc.).
- **Failure mode it attacks** — Binary-head representation starvation, identified 2026-05-16 by joint CSV + code review. Evidence: home_loss collapsed from 0.2265 (H_Tanh, shared trunk) to 0.3596 (J1, separate Arm 2) at identical ε=0.05 smoothing, and stayed at 0.35 through J2/J2.5/J3. cop_loss shows the same 3× regression (0.0675 → 0.1919). J3 calibration diagnostic (`diagnostics_history/J3_diagnostics.json`) shows all 1.56M AT_HOME predictions in `[0, 0.1)` bin — head learned aggregate (gap_pp=2.10) but lost slot-conditional discrimination. P2 §5's BCE-floor argument (0.198) does not bind the J-series — H_Tanh already operated within 0.03 of that floor at the same ε. The binding constraint is what feeds the head, not what the loss penalises.
- **Research consensus on the underlying mechanism** — **None of the 7 deep-research docs address it.** Independent re-scan 2026-05-16: all 7 assume a single shared trunk and focus loss-side / gradient-balancing / structured-prediction fixes. The closest acknowledgement is in `Research/Fixing Temporal Persistence in Transformers.md`: *"the NAR fusion arm relies heavily on the temporal stability and semantic accuracy of the hidden states produced by the AR trunk… gradients flowing back from the NAR heads become highly conflicted, collapsing the co-presence representation space"* — diagnoses our exact pathology from the gradient-conflict angle but never proposes head re-routing. J5-X1 therefore tests a hypothesis orthogonal to the entire ladder; if it succeeds, the J5-B/C/D/E loss-side cards become unnecessary first moves.
- **Architecture / loss change** — `configs/J5_X1.yaml` inherits `configs/J3.yaml` unchanged. `04B_model.py` (or new `04B_model_J5_X1.py`): in `JSeriesHybrid.forward()` (currently lines 1028–1048 of `archive/04B_model_J3.py`), after `dec_output` is computed by `self.decoder(...)`, set `binary_input = dec_output.detach()` and route `home_head` and `cop_head` off `binary_input`. Same swap in `.infer()` (currently lines 1063–1073). `_arm2_fuse`, `arm2_proj`, `arm2_act_proj`, and Arm 2 NAT-fusion plumbing remain defined but unused — flagged with a `# J5-X1: bypassed` comment, full removal deferred to a later cleanup pass. `04D_train.py` and `04E_inference.py` MODEL_TYPE dispatch lines extend `("J1","J2","J2_5","J3","J4_1","J4_2","J4_3")` → add `"J5_X1"`. Predecessor archive: `cp 04B_model.py Speed_Cluster/archive/04B_model_pre_J5_X1.py` in the same commit. Output dir `outputs_step4_J5_X1/`.
- **Hard gates to beat** —
  - **Primary**: home_loss from J3's 0.3514 toward H_Tanh's 0.2265 territory (target ≤ 0.27). Slot-level AT_HOME calibration restored: predicted-prob distribution must show ≥ 30% of mass outside `[0.0, 0.1)` bin in `04F` calibration block, vs J3's ~100% in that bin.
  - **Secondary**: cop_loss from 0.1919 toward H_Tanh's 0.0675 territory (target ≤ 0.12). cop_max_gap from J3's 7.04 pp toward ≤ 5.0 pp on the Alone channel — the chain rule J5-B would impose by construction may be partially achieved here through richer head context alone.
  - **4 hard gates (no regression vs J3)**: AT_HOME RMS ≤ 5.30 pp, Spouse |Δ| ≤ 5 pp, act_JS ≤ 0.05, composite < 1.045. **Target**: composite ≤ J3's 0.6355.
  - **act_JS non-regression** specifically: with the `.detach()` barrier, the activity decoder's training is mathematically unaffected. Smoke gate watches `act_loss` trajectory against J3's eps 1–10 — any divergence > 5% is a bug, not a J5-X1 effect.
- **Risk of regression** — Low-medium.
  - **(a) Cross-arm interference reintroduced if detach fails.** H_Tanh's 3/4-gate composite (AT_HOME RMS failed at 5.70 pp) was likely caused by binary-head gradients distorting the AR decoder. The `.detach()` barrier prevents this — `dec_output.detach()` strictly cuts gradient flow from home/cop loss back into the decoder. Verification: backward pass should leave `dec_output.grad` populated by activity loss only. Add a single-line unit test in `04D_train.py` smoke.
  - **(b) Activity-only decoder may not encode AT_HOME discriminative features.** The decoder is trained solely on activity CE; the question is whether its hidden states inherently encode "this slot looks AT_HOME" well enough for the binary heads to read off. Strong prior: activity and AT_HOME are tightly coupled (sleeping/eating ⇒ AT_HOME; commuting/working out ⇒ NOT_HOME), so a decoder that discriminates among 14 activities almost certainly encodes AT_HOME implicitly. Empirical anchor: H_Tanh's heads read off the same kind of decoder output (without detach) and reached home_loss=0.22. The detach is the only structural difference, and detach can only *reduce* representation quality at the margin since the heads can no longer shape it.
  - **(c) Risk that the marginal-gap improvement J-series achieved (home_gap 0.0841 → 0.0256) is given back.** J-series Arm 2 NAT fusion produced tighter aggregate matching despite worse slot calibration. J5-X1 may restore slot calibration but loosen aggregate match. Mitigation: AT_HOME RMS gate (per-stratum) is already the binding constraint, not aggregate gap; per-stratum RMS improving while aggregate gap loosens is a net win.
  - **(d) Smoke abort — superseded by bundle mode (2026-05-16).** Previously this card aborted to J5-X1b mid-run if `home_loss` failed to depart J3's 0.35 plateau by epoch 5–10. Under bundle execution, J5-X1 trains to full completion regardless; J5-X1b runs back-to-back automatically as the second leg of the same sbatch. Diagnosis happens offline after both finish.
- **GPU cost** — ~1.0× J3 wall time (~17 h on `pg`). Removing `arm2_proj` and `arm2_act_proj` from the forward path is a net parameter-count reduction (~0.3 M params); model size drops from 29.25 M to ~28.95 M. Negligible wall-time effect.

### J5-X1b — Re-route binary heads to `dec_output` (no detach barrier)

- **Method** — Same re-route as J5-X1 but *without* the `.detach()` barrier: `self.home_head(dec_output)` and `self.cop_head(dec_output)` directly. Binary-head gradients flow back into the activity AR decoder during backward, exactly as in H_Tanh. Arm 2 fusion code bypassed identically to J5-X1. Config inherits `configs/J3.yaml` byte-for-byte (`lambda_home=0.9`, `home_label_smooth=0.05`).
- **Failure mode it attacks** — Same as J5-X1 (binary-head representation starvation), but explicitly tests the dual hypothesis: that the detach barrier itself is starving the heads of slot-level signal. If J5-X1's hidden representation is too uniform because the activity-only decoder doesn't encode AT_HOME-discriminative features cleanly enough, the binary heads need *gradient pull* to shape that representation — which J5-X1b restores. H_Tanh's empirical anchor (home_loss=0.22 with shared trunk and no detach) supports this branch directly.
- **Research consensus** — Same gap finding as J5-X1: not addressed by the 7 docs. P4 (Temporal Persistence) gradient-conflict argument cuts both ways here — J5-X1 avoids the conflict; J5-X1b accepts it as the price for representation pressure.
- **Architecture / loss change** — `configs/J5_X1b.yaml` inherits `configs/J3.yaml`. `04B_model.py`: identical to J5-X1 except `binary_input = dec_output` (no `.detach()`). New MODEL_TYPE `"J5_X1b"` in `04D_train.py` / `04E_inference.py` dispatch. Predecessor archive: shares `04B_model_pre_J5_X1.py` (the X1 archive already captures pre-bundle state). Output dir `outputs_step4_J5_X1b/`.
- **Hard gates to beat** — Identical to J5-X1: home_loss ≤ 0.27, cop_loss ≤ 0.12, AT_HOME RMS ≤ 5.30 pp, Spouse |Δ| ≤ 5 pp, act_JS ≤ 0.05, composite ≤ J3's 0.6355. The 4 J3 non-regression gates are tighter here because activity decoder *is* being perturbed by binary-head gradients — `act_JS` is the watch metric.
- **Risk of regression** — Medium (higher than J5-X1).
  - **(a) Activity decoder distortion.** Binary-head gradients shape the AR decoder's hidden states during backward; this is the H_Tanh regime and the reason H_Tanh failed AT_HOME RMS at 5.70 pp (3/4 gates). Mitigation: `lambda_home=0.9` is already the J3-tuned weight; we are not re-introducing G4-era loss weighting that historically caused worse interference. Watch `act_JS` epoch-by-epoch against J3 — divergence > 5 % means the binary heads are eating activity capacity.
  - **(b) Spouse axis sensitivity.** G2's scheduled-sampling experience showed cross-arm coupling can collapse the Spouse channel. J5-X1b's coupling is gradient-only (not signal-substitution like scheduled sampling), but the risk axis is similar. Watch Spouse |Δ| in `04F` against the 5 pp gate.
  - **(c) Bundle-mode trade-off.** Because J5-X1b runs to full completion regardless of J5-X1's outcome, if J5-X1 already passes everything, the ~17 h spent on J5-X1b is a sensitivity check rather than a fallback. Worth it for the A/B evidence on the detach-barrier question; documented as an accepted cost of bundle execution.
- **GPU cost** — ~1.0× J3 wall time (~17 h on `pg`). Identical parameter count to J5-X1.

### J5-X2 — J5-X1 architecture + lambda_home=0.9 (config fix for act_JS regression)

- **Method** — Identical architecture to J5-X1: binary heads (`home_head`, `cop_head`) read from `dec_out.detach()` via `_arm1_decode_tf_full`; Arm-2 NAT fusion bypassed. Single config change: `lambda_home: 0.7 → 0.9` (restoring J3's original value). All other hyperparameters J5-X1 byte-for-byte. `model_type: J5_X1` reused — no new MODEL_TYPE, no model code change. Output dir `outputs_step4_J5_X2/`.
- **Hypothesis** — J5-X1's act_JS regression (0.0311 vs J3's 0.0191) is config-driven, not architectural. The `.detach()` barrier means binary-head gradients never reach the AR decoder; from the decoder's perspective, J5-X1 and J3 train identically. The `lambda_home=0.7` deviation (inherited from the J4 config base — J3 used 0.9) shifts the optimization trajectory and the val_score-driven early-stop timing, landing on a checkpoint with worse activity quality. With `lambda_home=0.9`, the model should converge to J3-level act_JS while preserving J5-X1's AT_HOME RMS improvement (4.15 pp vs J3's 4.57 pp). If both hold, the composite beats J3's 0.6355.
- **Evidence** — J5-X1 best checkpoint was epoch 51 (early stop ep66); J3 best checkpoint was epoch 72 (early stop ep87). J5-X1 stopped ~21 epochs earlier than J3 despite identical patience=15 and architecture, consistent with a lower `lambda_home` producing a different val_score trajectory. act_loss at best epoch: J5-X1 = 0.1379; J3 = 0.0878 — supporting the early-stop-before-activity-convergence hypothesis.
- **Config** — `configs/J5_X2.yaml`: `tag: J5_X2`, `model_type: J5_X1`, `lambda_home: 0.9`; all other fields from `J5_X1.yaml` unchanged. No dispatch extension in `04D_train.py` or `04E_inference.py`.
- **Hard gates** — Identical to J5-X1: AT_HOME RMS ≤ 5.30 pp, Spouse |Δ| ≤ 5 pp, act_JS ≤ 0.05, composite ≤ J3's 0.6355. **Targets**: act_JS ≤ 0.022 (J3-level); AT_HOME RMS ≤ 4.15 pp (preserved from J5-X1); composite < 0.6355.
- **Risk** — Very low. Single config scalar on a tested, stable architecture. The `.detach()` barrier is structurally unchanged; `lambda_home` only affects shared optimizer momentum and the LR scheduler — no gradient pathway to the activity arm changes.
- **GPU cost** — ~1.0× J3 wall time (~17 h on pg). Identical model: 29.25 M params.

### J5-A — Drop `home_label_smooth` (config-only, single knob)

- **Method** — Set `home_label_smooth: 0.0` in the J3 config (currently 0.05). No model code, no loss code, no dispatch.
- **Failure mode it attacks** — Prompt 1: "`home_head` σ=0.0 collapse; J2.5 GELU regression; label-smooth floor at ~0.20" (research agenda mapping). P1 §3: "label smoothing actively causes and severely exacerbates the σ=0 collapse signature." P2 §5 closes the loop algebraically: ε=0.05 ⇒ BCE floor = −0.5·log(0.95) − 0.5·log(0.05) = 0.198 — within 0.01 of J3's observed `home_loss=0.3514` plateau and J1's 0.3596 plateau. The head has perfectly minimised a *broken* objective.
- **Architecture / loss change** — `configs/J5_A.yaml` inherits `configs/J3.yaml`, override `home_label_smooth: 0.0`. `04D_train.py` MODEL_TYPE dispatch line extends `("J1","J2","J2_5","J3","J4_1","J4_2","J4_3")` → add `"J5_A"`. `04E_inference.py` dispatch likewise. `JSeriesHybrid` build is byte-identical to J3 (frozen `Speed_Cluster/archive/04B_model_J3.py`). Output dir `outputs_step4_J5_A/`.
- **Hard gate to beat** — Primary: AT_HOME RMS from J3's 4.57 pp toward ~3.0–3.8 pp by restoring slot-conditional probability learning on the home head; eliminates the σ=0.0 morning over-prediction (+10.77 pp gap on slots 0–10 in J1 diagnostics). Composite expected to drop further from 0.6355. act_JS and Spouse should hold (Arm 1 unaffected, Spouse uses clip-only inference).
- **Risk of regression** — Lowest in the ladder. Risk axis: J3's passing run used ε=0.05, so we are perturbing a known-good config. P1 §3 + P2 §5 both predict the perturbation is unambiguously in the *recovery* direction. Failure mode would be: home head escapes the floor but lands on a noisier slot-level signal that degrades aggregate AT_HOME — bounded by J1's pre-arm2_act_proj baseline (5.83 pp), well above the gate margin if J3's `arm2_act_proj` win still holds. Smoke gate as usual; abort if `home_loss` does not depart from 0.36 by ep 5–10.
- **GPU cost** — 1.0× J3 wall time (~17 h). Zero overhead — same model, same loss formula, single scalar in CE term changes value.

### J5-B — Hierarchical chain-rule cop head (architecture, single change)

- **Method** — Restructure the 9-channel co-presence output via the HMC chain rule: `p(alone) = sigmoid(z_alone)`; `p(other_i) = (1 − p(alone)) · sigmoid(z_other_i)` for each of the 8 non-Alone channels. BCE applied on the final marginal probabilities `p(alone)` and `p(other_i)`, not on intermediate logits. *This is structurally distinct from J4_2, which concatenated `home_probs.detach()` as an extra feature — that variant regressed AT_HOME by +1.31 pp and was shelved.* J5-B restricts the *output space* so that impossible Alone+Other combinations cannot be expressed, rather than adding an auxiliary penalty or conditioning feature.
- **Failure mode it attacks** — Prompt 3: "2005/2010 Alone +21/+17 pp; J4_3 PINN logic-loss collapsing Spouse" (research agenda mapping). Strong cross-prompt consensus: P3 §11.1 ranks Hierarchical Conditional Head as *Recommendation 1 (Optimal)*; P7 §1 stage 1 calls "collapse activity and AT_HOME into a single joint head with structurally-restricted vocabulary" the "single highest-leverage intervention" for the joints-wrong-marginals-right signature. Both describe the same mechanism: build the constraint into the output, not the loss.
- **Architecture / loss change** — In `JSeriesHybrid.forward` and `.generate`: after the two parallel cop sigmoids in `_arm2_fuse → cop_head`, split `cop_logits[..., 0]` (Alone) from `cop_logits[..., 1:]` (Others), compute `p_alone = sigmoid(z_alone)`, `p_others = (1 - p_alone).unsqueeze(-1) * sigmoid(z_others)`, return `cop_probs = cat([p_alone.unsqueeze(-1), p_others], dim=-1)`. Loss: BCE on `cop_probs` against ground-truth 9-channel one-hot (with `spouse_neg_weight=0.45` retained). Inference safety mask (`cop_pred *= (home_pred > 0.5)`) is **dropped** — the chain rule subsumes it. ~10 lines in `04B_model.py`. Tanh-bounded cop head retained; `arm2_act_proj` retained. New MODEL_TYPE `"J5_B"`; predecessor archive `cp 04B_model.py Speed_Cluster/archive/04B_model_pre_J5_B.py` in the same commit.
- **Hard gate to beat** — Primary: cop_max_gap from J3's 7.04 pp (Alone, 2005_1 +21.1 pp / 2010_1 +17.1 pp) toward ≤ 3.5 pp on the Alone channel by construction (the model can no longer emit `Alone=1` simultaneously with non-zero other channels). Spouse |gap| stable or slightly tighter; AT_HOME unaffected (home_head untouched). Composite expected to nudge down. **Hard non-regression check**: act_JS gate held — Arm 1 has no interaction with the cop head's chain rule.
- **Risk of regression** — Low-medium. J4_2's hierarchical-concat attempt did regress AT_HOME, but it conditioned the cop_head on `home_probs.detach()` as a feature — a fundamentally different mechanism. P3 §11.1 explicitly distinguishes the chain-rule output restructuring from the concat-conditioning failure mode. Genuine residual risk: if the 8 "Other" channels were absorbing gradient signal that was implicitly suppressing AT_HOME calibration in J3 (a coupling not predicted by any prompt), the change could perturb the home head indirectly. Smoke watches `home_loss` for departure from J3's 0.35 floor in the *wrong* direction (collapse below 0.30 → abort, matches J4_2's failure signature).
- **GPU cost** — 1.0× J3 wall time. Two extra elementwise multiplications per forward pass; negligible.

### J5-C — Linear-chain CRF + Viterbi decode on Arm-1 activity logits

- **Method** — Append a linear-chain CRF layer to the Arm-1 AR decoder: unary potentials = `act_logits[B,48,14]`, learnable pairwise transition matrix `ψ_pair ∈ ℝ^{14×14}`. Replace per-slot cross-entropy with CRF negative-log-likelihood (forward-backward gives exact `log Z`). At inference, replace argmax decoding with Viterbi on `(ψ_unary, ψ_pair)`. The Viterbi-decoded one-hot is the activity signal forwarded to Arm 2 fusion (`act_seq.detach()`), preserving the J1 detach barrier.
- **Failure mode it attacks** — Prompt 4: "Transition rate ratio = 157.95 (synthetic vs observed)" (research agenda mapping); flagged in 04F validation report 2026-05-12 as the §4 transition anomaly that triggered the temporal-persistence research prompt. Strong cross-prompt consensus: P4 §7 Path 1 ranks "HMM-Viterbi Smoothing + Persistence Regularization" as #1 ("Maximum Tractability"); P7 §1 stage 2 recommends a linear-chain CRF immediately after the Stage-1 joint head, with `pytorch-crf` / `torchcrf` or 30 lines of `torch.logsumexp` as the path. Both authors arrive at the same mechanism independently.
- **Architecture / loss change** — In `JSeriesHybrid.__init__` add `self.transitions = nn.Parameter(torch.zeros(14, 14))`. In `04D_train.py compute_loss`, replace `F.cross_entropy(act_logits, act_target)` with CRF NLL via forward-backward (~40 lines or one `torchcrf.CRF` call). In `.generate`/`.infer`, replace `act_logits.argmax(-1)` with Viterbi (~30 lines or `crf.decode()`). Arm-2 fusion still consumes `softmax(act_logits.detach())` at training and `one_hot(Viterbi(act_logits)).float()` at inference. New MODEL_TYPE `"J5_C"`. Predecessor archive in same commit.
- **Hard gate to beat** — Primary: transition rate ratio 157.95× → target 10–30× (P7: CRF gain typically 1–3 absolute points on persistence-flavoured metrics). Should improve act_JS marginally (cleaner per-slot decoding). 04F §4 limitation in the validation report would close out. AT_HOME and cop unaffected (detach barrier preserved); composite stable or better.
- **Risk of regression** — Medium. (a) If `ψ_pair` over-smooths, the model collapses to dominant-state runs — would degrade `act_JS` below the 0.05 gate (H_NAT-style flatlining). Mitigation: small learnable transitions, no `pytorch-crf` label smoothing on transitions, monitor per-slot entropy in smoke. (b) Viterbi decode at inference time changes the activity signal fed to Arm 2 vs. training (soft-prob detach); could re-create the train/infer gap that scheduled sampling caused. Smoke gate: `act_loss` strictly decreasing eps 1–10, per-slot entropy not collapsing below half of J3's value. P7 §10 caveat 4 also flags that CRF gains are 1–3 points typical, not 10 — set realistic expectations.
- **GPU cost** — ~1.2× J3 wall time. Forward-backward per batch is O(B·L·V²) = O(B·48·196), small absolute add on top of the 6-layer encoder + 6-layer decoder. Viterbi at inference negligible.

### J5-D — FAMO adaptive multi-task weighting (loss-aggregator, stacked on J5-A)

- **Method** — Replace static λ-weighting (`λ_act=1.0, λ_home=0.9, λ_cop=0.3, λ_marg=0.1`) with FAMO (Liu et al. 2024, NeurIPS) — task weights updated each step from an EMA of per-task loss descent rates. Reference impl: `github.com/Cranial-XIX/FAMO`. **Hard prerequisite: must stack on J5-A** (label smoothing dropped first). FAMO detects plateaued tasks and *removes* their weight; if the home head is still locked to the ε=0.05 floor, FAMO will deprioritise it and amplify the collapse — the opposite of what is wanted.
- **Failure mode it attacks** — Prompt 2: "Manual `λ_home` 0.5→0.9 sweeps over 20+ runs without convergence" (research agenda mapping). P2 §5 algebraically proves the manual sweep was futile (∇ ≈ 0 once the floor is hit; scalar λ multiplied by a zero gradient is still zero). FAMO is P2's #1 ranked deployment because its O(1) overhead is the only one that fits inside the 17 h GPU budget.
- **Architecture / loss change** — `04D_train.py compute_loss`: import FAMO from a vendored or pip-installed package, instantiate `FAMO(n_tasks=4, device=device)` once, replace the fixed scalarisation with `loss = famo.aggregate([act_loss, home_loss, cop_loss, marg_loss])`. FAMO maintains its own per-task weight params and EMA buffers in the optimizer state. New MODEL_TYPE `"J5_D"`. **Dependency: J5-A’s `home_label_smooth=0.0`** must be in the inherited config.
- **Hard gate to beat** — Secondary. FAMO is unlikely to single-handedly close any gate; the expected outcome is across-the-board ~3–8% tightening on each loss component and removal of the manual-λ tuning surface for downstream cycles (Step 5 / Step 6 retrains). Practical target: composite from J5-A's projection further toward 0.50–0.55; tightens AT_HOME and Spouse marginally.
- **Risk of regression** — Medium. (a) Stacking risk: if J5-A's smoothing-fix does not fully restore home head gradient, FAMO will lock the head out. Mitigation: smoke gate on `home_loss` trajectory before promoting to full train; abort + run J5-A standalone if home weight goes to zero within ep 5. (b) FAMO can oscillate if descent rates are highly noisy; J3's training is stable, so this is unlikely. (c) Removes manual λ control surface — for an investigation that has spent 6 months on λ sweeps, the user must be willing to cede that knob.
- **GPU cost** — ~1.05× J3 wall time. FAMO overhead is genuinely O(1); the 5% bump is bookkeeping. P2 §6 estimates 18–19 h for a 17 h baseline.

### J5-E — Per-cycle LoRA adapter + BBSE label-shift correction (for the 2022×WD residual)

- **Method** — Add a rank-4 LoRA adapter (Hu et al. 2021) to the encoder linear projections, keyed on `cycle_idx ∈ {2005, 2010, 2015, 2022}`. Train the global model first (J3 or J5-A as the base), then fine-tune the 2022 adapter on 2022-only data while the global weights are frozen. At inference, apply the cycle-appropriate adapter. In parallel, apply BBSE label-shift correction (Lipton, Wang, Smola, ICML 2018): estimate confusion matrix C on training labels, solve `C·w = μ` for the 2022 predicted marginals, post-multiply per-slot AT_HOME predictions by w.
- **Failure mode it attacks** — Prompt 5: "Per-stratum AT_HOME RMS=4.57 pp despite aggregate +2.1 pp; 2022×WD |Δ|=9.69 pp" (research agenda mapping). 04F validation report 2026-05-12 flags the 2022×Weekday cell at 9.69 pp as a known limitation tied to post-2020 remote-work shift (training cycles 2005–2015 weekday AT_HOME 62–65%; 2022 weekday ~70.6%).
- **Architecture / loss change** — Wrap `JSeriesHybrid` encoder linear layers with `LoRA(r=4)` modules; add a per-cycle adapter selector at `cond_vec` time. Two-stage training: stage 1 = full J3/J5-A train; stage 2 = 2022-only fine-tune of the 2022 LoRA only (`lr` ~ 1e-5, ~10 epochs). BBSE: post-hoc, separate script. New MODEL_TYPE `"J5_E"`. Adapter checkpoint stored alongside `best_model.pt`.
- **Hard gate to beat** — 2022×WD cell |Δ| from 9.69 → ~4–5 pp would close out 04F section 3's "all 12 cells FAIL vs 2 pp threshold". Aggregate AT_HOME RMS likely shifts modestly (the 2022×WD cell is one of 12; weight in RMS is moderate). **Non-regression check**: other 11 cells must hold — adapter switching at inference must not break the global model on pre-2020 cycles.
- **Risk of regression** — Medium-high. (a) P5 §Caveat 4 explicitly warns the 2022×WD cell may be "irreducible without feature engineering for post-2020 behavior" — the issue may be a missing covariate, not an algorithmic gap. The fastest diagnostic (per P5) is to train a 2022-only model and check whether it can beat 5 pp on 2022 alone; if not, no adapter will help. (b) P5 §Caveat 5 warns 2022 sample size may be < 200 per cell, making BBSE noisy. (c) Two-stage training violates Step-4's standing rule of one full pass per experiment — increases bookkeeping risk for Step-5 / Step-6 dependencies. (d) Per-period adapters add inference-time complexity to downstream Step 5 (Census Linkage already shipped off J3) and Step 6 (longitudinal forecasting, in flight) — the BEM pipeline currently consumes a single checkpoint, not a checkpoint+adapter switch.
- **GPU cost** — ~1.3× J3 wall time. Stage-1 train ~17 h + stage-2 2022 fine-tune ~4–5 h.

---

## 3. Cross-Prompt Consensus Table

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
| Group DRO / SUBG / DFR last-layer retrain | P5 Track A only | Single-prompt — held in reserve; the per-cell cancellation is already partially mitigated by `arm2_act_proj`; revisit only if J5-A doesn't tighten per-cell variance |
| Discrete diffusion (MDLM / SEDD / D3PM) | P6 (whole document) | Single-prompt **AND** violates user "no wholesale swap" constraint — rejected |
| JEM-style joint training, SPEN/DVN, masked-diary pretraining | P7 Stage 3–4 only | Weak — deferred; preconditioned on J5-A/B/C all running out of headroom |

Consensus is strongest where two prompts arrive at the same mechanism from different starting points (J5-A, J5-B, J5-C). The middle of the ladder (J5-D, J5-E) rests on single-prompt recommendations from P2 and P5 respectively — flagged accordingly in the cards.

---

## 4. Methods Explicitly Rejected (and why)

- **Soft logic loss / mutual-exclusivity penalty (P3 §2; cf. J4_3)** — both empirically (J4_3: 1/4 gates, Spouse collapsed to −8.89 pp) and theoretically (P3 §2 derives the asymmetric gradient that drives `p_others_i → 0`). Replaced by J5-B's chain-rule output restructuring. Do not revisit even with a smaller λ; the failure mechanism is gradient-geometric, not a tuning issue.
- **Scheduled sampling on the AR decoder** — G2/G3 outcome already on file (Spouse axis destroyed); J1 doc §J1 explicit non-goal. No prompt revisits.
- **Class-Balanced Loss (P1 §2.3)** — P1 derives that for mild 60/40 imbalance over millions of slot predictions, the effective-volume reweighting degenerates to ≈ 1.0 for both classes. Compute cost unjustified.
- **Brier Score as training loss (P1 §4)** — vanishing sigmoid-derivative gradient near σ ∈ {0, 1}; would exacerbate the σ=0 collapse, not relieve it. Reserved for evaluation only.
- **Post-hoc calibration (Platt/temperature/isotonic/Beta/Dirichlet) for AT_HOME (P1 §5)** — P1 §5 derives via the data-processing inequality that no injective post-hoc map can synthesise mutual information that the σ=0 head destroyed. Calibration is inapplicable when the failure is variance-zero, not over-confidence.
- **IRM, V-REx, DANN for the 2022×WD shift (P5 §Track B, §Caveats)** — P5 cites Gulrajani & Lopez-Paz (ICLR 2021): "no algorithm included in DomainBed outperforms ERM by more than one point when evaluated under the same experimental conditions." Rosenfeld et al. (ICLR 2021) further prove the IRM predictor can fail catastrophically with only three pre-2020 environments. Replaced by J5-E's LoRA + BBSE.
- **Unsupervised TTA (Tent / CoTTA) (P5)** — collapses to ordinary fine-tuning when validation labels exist, with catastrophic-forgetting risk. We have labels for all 12 cells.
- **MGDA-UB / PCGrad / CAGrad / Nash-MTL** (P2 §3.3–§3.7) — N=4 backward passes per step inflates the 17 h baseline to ~68 h, well outside budget. FAMO is the explicit cheap drop-in for these methods (built by the CAGrad authors).
- **MDLM / SEDD / D3PM / D3PM-style discrete diffusion as a wholesale AR replacement (P6 §Stage 1)** — violates the explicit user constraint. Consensus is single-prompt and the prompt itself (P6 §Recommendations §Pre-flight check) warns the AR ceiling may be conditioning saturation that diffusion will not fix. Out of scope for J5; revisit if J5-A/B/C all fail to move composite below 0.6.
- **SPEN / DVN / Neural Hawkes / HSMM / Levenshtein Transformer** (P3 §5–§6, P4 §2–§3) — overkill for N=9 / 14 vocabulary at 48 slots; architecture reach exceeds the "one axis per arm" rule.
- **Counterfactual data augmentation for 2022 (P5 §Caveats)** — Kaushik et al. require human-generated label-flipping; no operational notion of "counterfactual diary day." Joshi & He (ACL 2022) further show CAD can *exacerbate* spurious correlations.

---

## 5. Open Questions / Cross-Prompt Disagreements

1. **Loss-only vs head-architecture as the AT_HOME calibration fix.** P1 argues for inverted-γ ASL as the canonical loss-side rescue; P2 argues the manual-λ surface is the wrong knob entirely and FAMO is the right loss-aggregator-level fix; P7 argues the head should be folded into a joint vocabulary with the activity head. All three are loss-side or aggregator-side; none recommend touching the home_head module beyond the smoothing parameter. **Implication for J5-A**: if `home_label_smooth=0.0` alone does not restore slot-conditional learning (smoke shows `home_loss` stuck near 0.36 still), we have a choice point — ASL (P1) vs FAMO (P2). My read: P2's argument is the load-bearing one (the gradient is zero, scalar manipulations cannot escape) — fall to J5-D not the ASL variant.

2. **Linear-chain CRF vs semi-Markov CRF.** P4 §7 Path 1 recommends linear-chain + Viterbi as the lowest-surgery option; P7 §1 stage 3 recommends semi-Markov CRF with explicit segment durations (L ≈ 24 slots) as the "fix any residual persistence pathology" step *after* the linear-chain CRF. Disagreement is which one is the entry point, not which is the fix. J5-C takes the linear-chain entry point; semi-Markov is the reactive J5-C2 if needed.

3. **Whether the 2022×WD 9.69 pp gap is method-fixable at all.** P5 §Caveats 4 is unusually candid: "if a 2022-only model cannot beat 5 pp on 2022 alone, the problem is not method choice — it is a feature-engineering problem." No other prompt addresses this. **Implication for J5-E**: budget a 2022-only single-cycle training run as a *diagnostic* before committing to the LoRA build. If the diagnostic shows the gap persists with 2022-only data, J5-E is shelved and the 04F limitation note stays.

4. **Whether AT_HOME could be merged into the activity vocabulary at all (P7 §1 stage 1).** ~~P7's "single highest-leverage" intervention is to collapse activity (14-class) × AT_HOME (binary) into a joint 28-class vocabulary with impossible combinations excluded.~~ **Resolved 2026-05-15: shelved as J6.** Three reasons: (a) single-prompt only (P7 alone) — fails the "overwhelming consensus" threshold the user set for wholesale architectural changes; (b) 14→28 softmax change rewrites Arm 1 and forces re-runs of Step 5 (Census Linkage, complete) and Step 6 (Longitudinal Forecasting, in flight); (c) J5-A is essentially free and may close the AT_HOME calibration residual alone, in which case the joint head is wasted compute. Reopens only as J6 if J5-A/B/C all pass gates and composite stalls materially above J3's 0.6355.

5. **TV regularisation strength.** P4 §5.1 cites `λ_tv ∈ [10⁻³, 10⁻²]` as the typical range; P4 §7 Path 1 starts at `λ_tv = 10⁻³`. Single prompt only — light-evidence parameter. J5-C deploys TV only as an optional add if Viterbi alone underperforms.

6. **Per-channel `alpha` vs uniform `alpha` for the chain-rule cop head (J5-B).** P3 §11.1 derives the chain-rule but does not specify whether the 8 conditional sigmoids should share parameters or be independent. J5-B assumes 8 independent conditionals (current `cop_head` already produces 9 channels; trivial). If the Other-channel calibration regresses, share parameters across the 8 conditionals as J5-B-v2.

7. **Does J5-X1 subsume J5-B and J5-C?** (added 2026-05-16) If J5-X1 closes both binary-head losses by restoring decoder-quality context to home/cop, the residual signatures J5-B (HMC chain rule for cop_max_gap) and J5-C (CRF for transition-rate ratio) target may shrink enough that those cards lose independent value. The `cop_max_gap` Alone-channel pathology (7.04 pp) is partially attributable to the shallow Arm 2 fusion not being able to express "Alone is mutually exclusive with Others" — richer dec_output context may approximate the exclusion implicitly. The transition-rate ratio is a *generation*-time property of the activity AR decoder, which J5-X1 leaves unchanged, so J5-C remains independently load-bearing regardless of J5-X1's outcome. Decision: re-evaluate J5-B necessity from J5-X1's `04F` cop calibration; J5-C remains pre-locked.

---

## Sequencing Recommendation (revised 2026-05-16, bundle mode)

**Submit J5-X1 + J5-X1b as a single sequential sbatch bundle.** One upload, one job, one download. The job script runs J5-X1 to full completion (~17 h), then J5-X1b to full completion (~17 h) back-to-back on the same GPU. Both checkpoints, both `04F` validation reports, and both diagnostic dumps come back together for offline A/B comparison. Total wall time ≈ 34 h on `pg` — confirm against partition cap before submit. No mid-run gates, no fallback uploads, no decide-and-restart cycles. Rationale: J5-X1 and J5-X1b test the *same* head-input-starvation hypothesis with opposite detach choices; collapsing both into one job halves the wall-clock-to-decision and gives a clean A/B that decides the entire reserve path's fate.

**Decision tree after the X1 bundle returns:**

- **Case A — J5-X1 passes all 4 gates with composite < J3's 0.6355** → ship J5-X1, regenerate Step 5 / Step 6 downstreams. J5-X1b is archived as a sensitivity check; J5-A/B/C/D/E not triggered.
- **Case B — J5-X1b passes but J5-X1 doesn't** → ship J5-X1b, document the cross-arm coupling trade-off (watch Spouse axis in Step 6). The detach-barrier hypothesis is falsified; binary heads needed gradient pull to shape the decoder representation.
- **Case C — Both pass** → ship whichever has the better composite. The other run becomes the load-bearing evidence on whether the detach barrier is necessary; document for the paper.
- **Case D — Both flatline at `home_loss ≈ 0.35`** → head-input hypothesis falsified for the J-series; queue **J5-A** (original `home_label_smooth=0.0` reserve) as the next single-run job. If J5-A also fails → J5-D (FAMO stacked on J5-A).
- **Case E — One or both pass gates but residuals remain** (cop_max_gap > 5 pp on Alone, or transition-rate ratio unchanged) → queue **J5-B + J5-C** as the next bundle (orthogonal axes, forked from the winning X1 variant, ~34 h on `pg`). J5-C is independently load-bearing regardless of X1 outcome (transition-rate is an AR-decoder generation property).
- **Case F — Either run breaks a J3 gate (other than home_loss)** → revert to J3 (production), document, do not advance J5-B/C/D.
- **2022×WD residual specifically** → J5-E only after the 2022-only single-cycle diagnostic. Independent of the X1 bundle.

Handoff: this document is the investigator's deliverable. Execution (Sonnet build of J5-X1 + J5-X1b model edits + dispatch + single bundled sbatch script) is a separate step.

---

*Document prepared 2026-05-15. Sources: `Research/06_research_agenda.md`, `Research/Sigmoid Collapse in Multi-Task Learning.md`, `Research/Multi-Task Gradient Balancing Methods Comparison.md`, `Research/Structured Prediction for Multi-Label Classification.md`, `Research/Fixing Temporal Persistence in Transformers.md`, `Research/Distributionally Robust ML, Worst-Group Optimization, and Covariate Shift Adaptation An Applied Survey for a 12-Cell Occupancy Classifier.md`, `Research/Generative Modeling for 48-Slot Categorical Activity Sequences with Auxiliary Heads A Graduate-Level Technical Comparison.md`, `Research/Modern Deep Structured Prediction A Primer for Transformer Practitioners Facing Correct Marginals, Wrong Joint.md`. State of practice: J3 (4/4 gates) shipped 2026-05-07; J-4.1/2/3 shelved 2026-05-11; 04F validation report regenerated for J3 on 2026-05-12 with 2022×WD AT_HOME and transition-rate-ratio limitations noted.*

*Revision 2026-05-16 (a): J5-X1 card added as new first move based on joint diagnostic + code review. Evidence: `CSV_records/loss_values_trainings_investigation.csv` shows H-series (H_Tanh / H_Time / G4) reached home_loss ≈ 0.22 at `ε=0.05` smoothing (i.e. at the predicted BCE floor), while J-series (J1 → J3) sits at 0.35 at the same ε. The 0.13 gap appeared when the architecture split into Arm 1 (activity AR decoder) + Arm 2 (NAT fusion for home/cop), starving the binary heads of decoder-quality context. The J5-X1 hypothesis (re-route home/cop to `dec_output.detach()`) is orthogonal to all 7 deep-research prompts — independent re-scan 2026-05-16 confirms none of the 7 docs address head-input depth. J5-A's BCE-floor argument is preserved as reserve, falsified for the J-series but valid in principle.*

*Revision 2026-05-16 (b): execution mode switched to **bundle**. J5-X1 + J5-X1b are now submitted as one sequential sbatch job (~34 h total) instead of as separate upload/run/download cycles. Both variants train to completion regardless of intermediate signal; A/B comparison happens offline after the bundle returns. Eliminates the smoke-abort gate inside J5-X1's card (still documented for traceability but superseded). Rationale: J5-X1 and J5-X1b test the same head-input hypothesis with opposite detach choices; bundling halves wall-clock-to-decision, gives a clean A/B for the paper, and matches the user-preference pattern of "one upload, one run, one download" (CLAUDE.md feedback memory).*

---

## Appendix A — Sonnet Builder Prompt (paste-ready, prepared 2026-05-16)

> Paste the block below into a fresh Sonnet session when you're ready to execute the J5-X1 + J5-X1b bundle. The prompt is self-contained — Sonnet will read this proposal and the relevant code, perform the file edits locally, archive the predecessor, write the bundled sbatch script, run the local module check, and hand you the exact scp + sbatch commands to run. Sonnet does not execute cluster commands itself (login node is submission-only; manager owns handoff).

```
You are the employee. Execute the task below and append a Progress Log entry on completion under `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/step4_training_v4.md` (create the file if it does not exist).

## Task: Build and stage the J5-X1 + J5-X1b sequential bundle for Step-4 training on the Speed HPC cluster.

## Context to read first (in order)

1. `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/Research/J5_proposal.md` — the full proposal. Focus on §1, §1a, §2 (J5-X1 + J5-X1b cards), §Sequencing, and the roadmap checklist. This document is the source of truth for the methodology.
2. `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_J3.py` — frozen J3 model source. Lines 995–1024 (`_arm2_fuse`), 1028–1048 (`forward`), 1063–1073 (`infer`) are the diff points.
3. `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_H_Tanh.py:314–325` — H_Tanh forward pattern (the shared-trunk template J5-X1b restores).
4. `2J_docs_occ_nTemp/04B_model.py` — current production model. Confirm it matches J3 archive before editing.
5. `2J_docs_occ_nTemp/step4_Speed_Cluster/04D_train.py` — MODEL_TYPE dispatch (extend with `J5_X1` and `J5_X1b`).
6. `2J_docs_occ_nTemp/step4_Speed_Cluster/04E_inference.py` — MODEL_TYPE dispatch (same extension).
7. `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J3.yaml` — base config to inherit.
8. Most recent successful sbatch script for a J-series run (check `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/` or analogous directory). Use it as the template for the bundled script.

## Concrete deliverables

### 1. Archive predecessor (in same commit as the edits, per CLAUDE.md memory `feedback_archive_predecessor`)
- `cp 2J_docs_occ_nTemp/04B_model.py 2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_pre_J5_X1.py`
- This archive covers BOTH J5-X1 and J5-X1b (they share the same predecessor state).

### 2. `2J_docs_occ_nTemp/04B_model.py` — add J5_X1 and J5_X1b MODEL_TYPE branches
- In `JSeriesHybrid.forward()`: after `dec_output` is computed by `self.decoder(...)`, add a model-type switch.
  - For `J5_X1`: `binary_input = dec_output.detach()`
  - For `J5_X1b`: `binary_input = dec_output`
  - For all other J-series: keep `binary_input = arm2_feat` (compute via existing `_arm2_fuse`)
  - Route `self.home_head(binary_input)` and `self.cop_head(binary_input)` accordingly.
- In `.infer()`: mirror the same switch.
- Keep `_arm2_fuse`, `arm2_proj`, `arm2_act_proj` defined; they are bypassed for J5_X1 / J5_X1b but unchanged for J3/J4_*. Annotate the bypass with a `# J5-X1/X1b: bypassed, dec_output route active` comment near the switch.
- Single-line backward unit test for J5_X1: after `loss.backward()`, assert `dec_output.grad` is populated by activity-CE only (no contribution from home/cop BCE). Add as a `# DEBUG` block in `04D_train.py` smoke (gate behind an env var so it does not run in full training).

### 3. `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X1.yaml`
- Inherit `configs/J3.yaml` byte-for-byte. Override only `model_type: J5_X1`. All loss weights, optimizer, schedule, smoothing, spouse_neg_weight stay J3-identical.

### 4. `2J_docs_occ_nTemp/step4_Speed_Cluster/configs/J5_X1b.yaml`
- Inherit `configs/J3.yaml` byte-for-byte. Override only `model_type: J5_X1b`. Same: no other config diff vs J3.

### 5. Dispatch extensions
- `2J_docs_occ_nTemp/step4_Speed_Cluster/04D_train.py`: extend MODEL_TYPE allow-list `("J1","J2","J2_5","J3","J4_1","J4_2","J4_3")` → add `"J5_X1"`, `"J5_X1b"`.
- `2J_docs_occ_nTemp/step4_Speed_Cluster/04E_inference.py`: same extension.

### 6. Bundled sbatch script `2J_docs_occ_nTemp/step4_Speed_Cluster/jobs/J5_X1_bundle.sh`
- One job, one ID. Sequential execution: `J5_X1` train → `J5_X1` infer → `J5_X1` 04F validation → `J5_X1b` train → `J5_X1b` infer → `J5_X1b` 04F validation. Each segment writes to its own output dir (`outputs_step4_J5_X1/` and `outputs_step4_J5_X1b/`).
- Speed cluster shell is **tcsh** (per memory `reference_speed_cluster_shell`): no `2>&1` (use `>&` or omit); no `\` line continuation (every command on one short line).
- Request wall time = 38 h on `pg` (34 h estimate + 4 h buffer for inference/validation). **Before submitting, verify against the partition's MaxTime — if `pg` caps at 24 h, split into two jobs with `--dependency=afterok:<jobid1>` instead of a single bundle. Report the cap check result in your final message.**
- Each training step writes a per-epoch CSV (act_loss, home_loss, cop_loss) under its output dir; the validation step writes `04F_validation_report_J5_X1.html` and `04F_validation_report_J5_X1b.html` plus `diagnostics_J5_X1.json` and `diagnostics_J5_X1b.json` parallel to existing `J3_diagnostics.json`.
- Do NOT include any mid-run abort/decision logic. Both halves run to completion regardless of intermediate signal — that is the bundle-mode contract per §Sequencing.

### 7. Local module check (per memory `feedback_cluster_module_check`)
- Before handing the sbatch command to the user, scan all script imports across `04B_model.py`, `04D_train.py`, `04E_inference.py`, and the 04F validation script. Confirm every imported package (torch, numpy, pandas, yaml, scipy, etc.) is available in the cluster Python env Step-4 currently uses. If any package is missing, add an install/precheck line at the top of the sbatch script.

### 8. Hand-off to user (final message)
- Per memory `feedback_pair_scp_with_cluster` and `feedback_cluster_job_submission`: do NOT attempt to scp or sbatch yourself. Print the literal commands the user runs.
- Single recursive scp **locally** to push the bundle. Then the **on the cluster** sbatch submission line. Both on their own single line, no `\` continuation, no brace expansion.
- Use the exact label format: "locally:" and "on the cluster:" prefixes (per CLAUDE.md Speed HPC section and memory `feedback_cluster_commands`).
- Example shape (Sonnet must compute the actual paths):
  - locally: `scp -r 2J_docs_occ_nTemp/step4_Speed_Cluster/ o_iseri@speed.encs.concordia.ca:~/step4_Speed_Cluster/`
  - on the cluster: `cd ~/step4_Speed_Cluster && sbatch jobs/J5_X1_bundle.sh`
- Never claim a job is submitted; the user submits.

### 9. Progress Log entry
- Append a Progress Log entry to `2J_docs_occ_nTemp/step4_Speed-Cluster_docs/step4_training_v4.md` (create file if missing) with: timestamp, list of files edited, archive command run, partition cap check result, module check result, and the literal scp + sbatch commands handed to the user.

## Hard constraints

- **Manager owns planning; you own execution.** Do not propose alternative methodologies or extra cards — your job is to build J5-X1 + J5-X1b as specified in §2 of `J5_proposal.md` (lines 50–94 ish). Flag back to the user via plan blocker if you find the specification ambiguous; do not infer.
- **You are NOT on the cluster.** No `ssh`, no `sbatch`, no `squeue`. The login node `speed-submit2` is submission-only and the user runs all cluster commands (memory `feedback_cluster_job_submission`).
- **One commit for the bundle.** Archive copy, model edit, configs, dispatch extensions, sbatch script — all in a single commit with message `[ml]: add J5-X1 + J5-X1b bundle for binary-head re-route experiment`.
- **Do not modify** `J5_proposal.md`, `06_research_agenda.md`, or any file under `Research/`. Those are investigator deliverables.
- **Do not modify** any J3-or-earlier MODEL_TYPE code path. J5-X1 / J5-X1b are additive branches behind a model_type switch.
- **No fallback shims.** If you cannot reproduce the J3 forward exactly with `model_type=J3`, stop and flag — do not write a partial workaround.

Report on completion: file diff list, archive command, partition cap finding, module check finding, the two hand-off commands, and the Progress Log path.
```

*End of Appendix A. Prompt prepared 2026-05-16 by the manager. Update revision date here when the prompt is edited.*

---

*Appendix B (J5-X2 standalone builder prompt) removed 2026-05-19. J5-X2 is now part of the three-in-one parallel bundle (J5-X2 + J5-A + J5-B) built and staged directly by the manager+employee single-cycle dated 2026-05-19 in `step4_training_v4.md`. The J5-X2 experiment card in §2 above remains the methodological source of truth.*

---

# Chapter — Architecture Comparison: Transformer Pipeline vs J3 vs J5-X1

*Added 2026-05-17. This chapter consolidates the three-model architecture comparison and its graphical-abstract prompt into the J5 research document so all related material lives in one place.*

## C.0 Graphical abstract prompt (paste into web LLM image generator)

```
GRAPHICAL ABSTRACT — three transformer architectures for daily
occupancy diary generation (activity + AT_HOME + co-presence)

Layout: 16:9, flat vector style, sans-serif (Inter or Helvetica),
no 3D, no gradients, no clip-art. Three equal vertical panels.

Title bar: "Three transformer architectures, three outputs
(activity / AT_HOME / co-presence). Why the simple encoder-only
pipeline still beats the hybrid."

COMMON INPUT STRIP (top of each panel, identical):
   demographics + temporal context + sequence tokens
   -> embeddings -> positional encoding

────────────────────────────────────────────
PANEL 1 — Transformer pipeline (encoder-only, parallel heads)
   Status badge: GREEN — "~95% accuracy on all 3 outputs
   (with generalization controls; raw model memorized easily)"

   Steps:
     1. Per-feature embedding layer (one Linear per categorical
        input, concatenated)
     2. Learnable positional encoding (24 slots / day)
     3. Transformer Encoder stack (multi-head self-attention,
        d_feed = 10240)
     4. Three PARALLEL heads off the same encoder output:
          - Activity head    -> Softmax (CE)
          - Location head    -> Sigmoid (BCE, AT_HOME)
          - withNOBODY head  -> Sigmoid (BCE, co-presence)
     5. Weighted multi-task loss (w_act + w_loc + w_NOB)

   Result box:
     - Activity accuracy   : ~95%
     - Location accuracy   : ~95%
     - withNOBODY accuracy : ~95%
     - Generalization via dropout, weight regularization,
       stratified split (raw model memorized training set)

   Properties:
     - Encoder-only, no decoder, no autoregression
     - All heads see the SAME rich encoder state
     - Heads supervised jointly from epoch 0
     - 24-slot daily diary

────────────────────────────────────────────
PANEL 2 — J3 (Hybrid AR-Encoder, production)
   Status badge: AMBER — "4 / 4 gates PASS, AT_HOME plateaus"

   Steps:
     1. Input embeddings + sinusoidal PE
     2. 6-layer Transformer Encoder trunk (d_model=384)
     3. Split into TWO ARMS via .detach() barrier
     4. ARM 1 — CrossAttn Autoregressive Decoder (6 layers)
          -> Activity head (Softmax, CE)
     5. ARM 2 — Per-slot Non-Autoregressive fusion
          concat[memory | arm2_act_proj(act_probs.detach())
                 | demo | cycle | strata] -> arm2_proj
          -> AT_HOME head (Tanh -> Sigmoid)
          -> Co-presence head (Tanh -> Sigmoid)

   Gates box (target / J3):
     - composite     < 1.045   | 0.6355  PASS
     - AT_HOME RMS   ≤ 5.30 pp | 4.57 pp PASS (margin 0.73)
     - Spouse |Δ|    ≤ 5 pp    | -2.03   PASS
     - activity JS   ≤ 0.05    | 0.0191  PASS

   Properties:
     - 48-slot diary
     - Binary heads see PROJECTED activity probs, not encoder state
     - Activity gradients isolated from binary heads

────────────────────────────────────────────
PANEL 3 — J5-X1 (head re-route experiment)
   Status badge: RED — "gates not closed"

   Steps:
     1. Same trunk + Arm 1 as J3 (drawn light grey, "unchanged")
     2. Arm 2 fusion REMOVED (greyed-out, X through it)
     3. AR decoder output (dec_output, d_model=384)
        -> .detach() (X1) or no detach (X1b)
     4. Binary heads attached directly to dec_output:
          -> AT_HOME head (Tanh -> Sigmoid)
          -> Co-presence head (Tanh -> Sigmoid)

   Gates / training snapshot (ep 42/100):
     - train_loss    : 0.5099
     - act_loss      : 0.1892
     - home_loss     : 0.3669
     - cop_loss      : 0.2101
     - marg_loss     : 0.0087
     - val_JS        : 0.0076
     - home_gap      : 0.0350
     - val_score     : 0.0251
     - lr            : 5.00e-05
     - grad_norm     : 2.012
     Status: gates not yet closed vs J3

   Properties:
     - Binary heads now read RICH decoder context
     - But decoder is trained on ACTIVITY CE only
     - AT_HOME signal is implicit, not supervised
     - Joint representation never learned

────────────────────────────────────────────
BOTTOM TAKEAWAY:
   Joint supervision of all heads off a SHARED encoder (Panel 1,
   ~95% across all outputs with generalization controls)
   outperforms architectural separation (Panel 2, gates pass but
   AT_HOME plateaus) and head re-routing without joint
   supervision (Panel 3, training in progress, gates not yet
   closed). The binding constraint is the supervision topology,
   not depth.

STYLE
   - 5 colours: inputs (blue), encoder (purple), decoder/AR
     (crimson), NAT fusion (green), heads (orange)
   - Solid = forward; dashed = .detach(); grey = unchanged
   - 14 pt panel titles, 10 pt body, 18 pt main title
   - 8-px grid alignment
```

## C.1 Overview

This chapter compares three transformer architectures that have been used (or are currently being run) for generating daily occupancy diaries with three outputs: **activity**, **AT_HOME (location)**, and **co-presence (withNOBODY / Spouse / Others)**.

The three models:

1. **Transformer pipeline** — encoder-only, three parallel heads (legacy reference model, `examples/cloud_computing/Transformer_pipeline.py`)
2. **J3** — Hybrid AR-Encoder, current production winner (`step4_Speed_Cluster/archive/04B_model_J3.py`)
3. **J5-X1** — head re-route experiment derived from J3 (training in progress; the bundle whose hand-off prompt is in Appendix A above)

The graphical abstract prompt (Section C.0) and this narrative are paired — paste the prompt into a web-based image generator to produce the figure that the table below summarizes.

## C.2 Side-by-side summary

| Aspect | Transformer pipeline | J3 (Hybrid AR-Encoder) | J5-X1 (head re-route) |
|---|---|---|---|
| Trunk | Encoder-only, multi-head self-attention | 6-layer Transformer Encoder (d_model=384) | Same trunk as J3 (unchanged) |
| Decoder | None | 6-layer CrossAttn Autoregressive (Arm 1) | Same AR decoder as J3 |
| Diary length | 24 slots / day (hourly) | 48 slots / day (30-min) | 48 slots / day (30-min) |
| Positional encoding | Learnable | Sinusoidal | Sinusoidal |
| Head attachment for AT_HOME / co-presence | Directly off shared encoder state | Off Arm-2 per-slot NAT fusion (uses projected activity probs + context) | Directly off AR decoder output |
| Activity gradient isolation | None — heads share trunk | `.detach()` barrier between Arm 1 and Arm 2 | `.detach()` (X1) or none (X1b) |
| Joint supervision of all 3 heads | Yes, from epoch 0 | Partial — Arm 1 supervises activity; Arm 2 supervises binary heads | Yes (heads share decoder) but decoder loss = activity CE only |
| Best result | ~95% accuracy on all 3 outputs (with generalization controls) | 4 / 4 gates PASS, AT_HOME RMS=4.57 pp | Training in progress, gates not yet closed (ep 42/100) |
| Status | Reference / baseline | **Production — SHIP** | Experimental, hypothesis test |

## C.3 Transformer pipeline (encoder-only, parallel heads)

### Steps
1. Per-feature embedding layer — one `nn.Linear` per categorical input (education, employment, gender, family typology, region, age, etc.), then concatenated.
2. Learnable positional encoding for 24 slots / day.
3. Transformer Encoder stack — `TransformerEncoderLayer` with `nhead` heads, `d_feed=10240`, `num_hidden_layers` encoder blocks, GELU activations.
4. **Three parallel output heads** off the same encoder output (`transformer_out`):
   - `activity_dense` — `Linear → CE`, 14 classes
   - `location_dense` — `Linear → Sigmoid → BCE`, AT_HOME binary
   - `withNOB_dense` — `Linear → Sigmoid → BCE`, co-presence binary
5. Weighted multi-task loss: `w_act * loss_act + w_loc * loss_loc + w_NOB * loss_NOB`.

### Pipeline
`Transformer_bash.slurm` → `Transformer_pipeline.py` → Optuna hyperparameter tuning → trained model → per-head accuracies logged.

### Properties
- Encoder-only, no decoder, no autoregression.
- All three heads see the **same** rich encoder state.
- Heads are supervised **jointly from epoch 0**.
- 24-slot hourly diary.
- Heavy regularization (dropout per head, dropout in transformer, weight regularization) is required — without it the model **memorized the training set easily**.

### Approach to three outputs
All three heads share the trunk and receive joint gradients. The shared encoder learns a representation that is simultaneously useful for activity classification, AT_HOME, and co-presence. The result: **~95% accuracy on all three outputs** once generalization controls are in place.

## C.4 J3 (Hybrid AR-Encoder, production)

### Steps
1. Input embeddings (`act_emb ⊕ aux_seq`) + sinusoidal positional encoding, plus a CLS token carrying `cond_vec ⊕ cycle_emb`.
2. 6-layer Transformer Encoder trunk, d_model=384, n_heads=8, d_ff=1536 → `memory (B, 49, d_model)`.
3. **Split into two arms** via a `.detach()` barrier on `act_probs`.
4. **Arm 1 — Autoregressive Activity Decoder** (CrossAttn, 6 layers, 48-step loop): self-attn → cross-attn(memory) → cross-attn(demo, cycle, strata) → FFN → activity head (Linear → Softmax → CE).
5. **Arm 2 — Per-slot Non-Autoregressive fusion**: concatenate `[memory[:,1:,:] | arm2_act_proj(softmax(act_logits.detach())) | cond_vec broadcast | cycle_emb broadcast | strata one-hot]` → `arm2_proj (Linear → d_model)` → two parallel heads:
   - AT_HOME head: Linear → Tanh → Linear → Sigmoid → BCE
   - Co-presence head: Linear → Tanh → Linear → Sigmoid → BCE
6. Inference safety: `cop[:,:,Spouse] *= (home > 0.5)` clip-only rule.

### Pipeline
`step4_Speed_Cluster/04B_model_J3.py` → trained on Speed HPC (Slurm) → 4/4 gates evaluated post-hoc.

### Properties
- 48-slot 30-min diary, 14 activity classes, 9 co-presence channels.
- Activity gradients **isolated** from binary heads via `.detach()`.
- Binary heads see the **projected activity distribution** (14 → 384 via `arm2_act_proj`) plus context, **not** the raw encoder/decoder state.
- Tanh-bounded heads prevent saturation.
- Best epoch 72; `home_loss` plateau ≈ 0.3514.

### Approach to three outputs
- **Activity** is generated autoregressively (Arm 1), so it captures sequential structure.
- **AT_HOME** and **co-presence** are generated in parallel from Arm 2, conditioned on the projected activity distribution.
- The `.detach()` barrier means binary-head gradients never reach the AR decoder — Arm 1 optimizes activity, Arm 2 optimizes binary heads.

### Gates (J3 at ship)
| Metric | Target | J3 |
|---|---|---|
| composite | < 1.045 | **0.6355** PASS |
| AT_HOME RMS | ≤ 5.30 pp | **4.57 pp** PASS (margin 0.73) |
| Spouse \|Δ\| | ≤ 5 pp | **-2.03 pp** PASS |
| activity JS | ≤ 0.05 | **0.0191** PASS |

## C.5 J5-X1 (head re-route experiment)

### Steps
1. Same input embeddings + sinusoidal PE as J3.
2. Same 6-layer Transformer Encoder trunk as J3 (frozen architecture).
3. Same Arm 1 CrossAttn Autoregressive Decoder as J3.
4. **Arm 2 fusion REMOVED.** Instead:
   - Decoder output `dec_output (B, 48, d_model)` is routed directly into the binary heads.
   - **J5-X1**: routed through `.detach()` (preserves Arm 1 gradient isolation).
   - **J5-X1b**: routed without `.detach()` (binary-head gradients flow back into the AR decoder).
5. Binary heads (same modules as J3, re-targeted):
   - AT_HOME head: Linear → Tanh → Linear → Sigmoid
   - Co-presence head: Linear → Tanh → Linear → Sigmoid

### Pipeline
Built on top of J3 source as `04F_*`, staged 2026-05-17 per the hand-off prompt in Appendix A; currently running on the Speed HPC cluster.

### Properties
- Binary heads now read **rich decoder context** (d_model = 384) instead of the shallow Arm 2 fusion.
- But the AR decoder is trained on **activity CE only** — the AT_HOME-discriminative signal in `dec_output` is implicit, not directly supervised.
- The joint activity × AT_HOME representation is never learned end-to-end.

### Training snapshot (epoch 42 / 100, run in progress)
| Metric | Value |
|---|---|
| train_loss | 0.5099 |
| act_loss | 0.1892 |
| home_loss | 0.3669 |
| cop_loss | 0.2101 |
| marg_loss | 0.0087 |
| val_JS | 0.0076 |
| home_gap | 0.0350 |
| val_score | 0.0251 |
| lr | 5.00e-05 |
| grad_norm | 2.012 |

**Status:** training continues; gates not yet closed against J3 baseline.

### Approach to three outputs
- **Activity** — same as J3 (Arm 1 AR decoder).
- **AT_HOME / co-presence** — read off the AR decoder output, not the Arm 2 fusion. The hypothesis: richer head input depth will close the AT_HOME RMS gap. So far the depth is richer but supervision shape is wrong, so the gap is not closing.

## C.6 Why J3 still wins (and what the comparison says)

- **Transformer pipeline** shows what joint supervision of all three heads off a shared trunk can do: ~95% accuracy on every output, *given* aggressive generalization controls to fight memorization.
- **J3** separates the heads architecturally — activity gets its own AR arm, binary heads get a shallow per-slot fusion that sees only the projected activity probs. This is sufficient to pass all 4 gates but leaves AT_HOME at a plateau.
- **J5-X1** swings in the opposite direction — gives the binary heads the rich decoder context — but does not change what the decoder is supervised on. Result: more depth, no better calibration.

**Binding constraint identified:** the limiting factor is not head-input depth (J5-X1) nor loss topology (the J5 ladder, falsified earlier in this document); it is **supervision topology**. The two outputs that need joint shape (activity and AT_HOME) are never co-supervised on a shared representation in the J-series. The Transformer pipeline does exactly this and gets it right, at the cost of needing strong regularization.

**Implication for next step:** a joint activity × AT_HOME representation with shared supervision (the shelved J6 / P7 stage-1 idea) is the direction worth testing, not another single-axis card.

---

*End of Chapter. Source files:*
- `step4_Speed_Cluster/archive/04B_model_J3.py`
- `examples/cloud_computing/Transformer_pipeline.py`, `Transformer_bash.slurm`, `Transformer_num_features.json`
- `step4_Speed-Cluster_docs/CSV_records/{architecture,loss_values_trainings,training_config}_investigation.csv`
