# Step 4 Training Improvement Plan — Phase 7

Continues from `04_augmentationGSS_IMP.md` (Phases 1–6 CLOSED). J3 confirmed as the only model passing all 4 hard gates across 40+ trials.

---

## Lessons from Phase 6

1. **J3 is the confirmed winner** — 4/4 gates (composite 0.6355, AT_HOME RMS 4.57 pp, COP max gap ~2.03 pp, act_JS 0.0191).
2. **Composite score is misleading.** MDLM_G1 scored best composite (0.5592) but fails 2/4 hard gates. The composite formula is dominated by cop_cal_MAE (copresence calibration), which is not a hard gate. Always evaluate individual gates.
3. **Loss-weight HPT is exhausted.** Stages D–F tuned every loss knob on MDLM. J3's loss weights were tuned in J3-HPT bundle (T/L/S_lo/S_hi/R_lo/R_hi). No further gains expected.
4. **Architecture-level HPT was never done on J3.** All J3 variants changed routing (J5_X1) or loss (J3_CLEAN), not core architecture knobs (enc depth, dec depth, width, heads).
5. **J3 never saw Phase 2 demographics.** Trained on d_cond=76; ATTSCH/POWST/MODE (d_cond=90) are available in `outputs_step4_G2` but untested on J3's architecture.
6. **Low training loss ≠ good generation quality.** The model practiced only with cheat sheets, so it scores perfectly on homework but fails the real exam. Training loss measures prediction accuracy under teacher forcing (model always sees correct previous values). At inference, the model uses its own predictions — mistakes snowball. Example: H_Time has cop_loss=0.062 (best in class) but COP max gap=22.86 pp at inference (catastrophic). Always evaluate with full diagnostic gates, never trust training loss alone.

---

## Phase 7: J3 Demographics + Architecture HPT (6 parallel trials)

### Goal

Improve AT_HOME RMS (lower = better) while maintaining all other gates. NOT optimizing composite score.

### Current J3 gate scores (the bar to beat)

| Gate | J3 value | Target | Margin |
|---|---|---|---|
| AT_HOME RMS | 4.57 pp | ≤ 5.3 pp | 0.73 pp headroom |
| COP max gap | ~2.03 pp | ≤ 5.0 pp | ~3.0 pp headroom |
| act_JS | 0.0191 | ≤ 0.05 | 0.031 headroom |
| composite | 0.6355 | < 1.045 | 0.41 headroom |

### Design

All 6 trials share:
- `data_dir = outputs_step4_G2` (d_cond=90, Phase 2 demographics)
- Identical loss weights: lambda_home=0.7, lambda_act=1.0, lambda_cop=0.3, lambda_marg=0.1
- 100 epochs, patience 15, lr=5e-5, batch_size=256
- Full diagnostics pipeline (04H + 04I + 04J)

One architecture knob changed per trial (single-axis design).

| # | Tag | Change | d_model | heads | d_head | enc | dec | dropout | ~Params | Target gate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | J3_D2_CTRL | Demographics only (control) | 384 | 8 | 48 | 6 | 6 | 0.10 | ~29M | Baseline |
| 2 | J3_D2_ENC8 | Deeper encoder | 384 | 8 | 48 | **8** | 6 | 0.10 | ~33M | AT_HOME |
| 3 | J3_D2_DEC8 | Deeper decoder | 384 | 8 | 48 | 6 | **8** | 0.10 | ~35M | act_JS |
| 4 | J3_D2_H16 | More attention heads | 384 | **16** | **24** | 6 | 6 | 0.10 | ~29M | AT_HOME, COP |
| 5 | J3_D2_W512 | Wider model | **512** | 8 | **64** | 6 | 6 | 0.10 | ~50M | AT_HOME |
| 6 | J3_D2_D15 | Stronger regularization | 384 | 8 | 48 | 6 | 6 | **0.15** | ~29M | AT_HOME, COP |

### Trial rationales

**T1 (CTRL):** Mandatory control — isolates the effect of d_cond 76→90. Prior J3_DEMO (Phase 2) was cancelled at ep 41 prematurely. POWST directly indexes AT_HOME patterns; ATTSCH indexes transit/activity patterns.

**T2 (ENC8):** Encoder is the shared trunk feeding both arms. More depth = better integration of richer d_cond=90 with 48 time slots. Never tried on J-series.

**T3 (DEC8):** CrossAttnDecoder generates activities via AR loop with 3 conditioning tokens (demo, cycle, strata). More decoder layers = more refined re-attendance to richer demographics. Better activity → better arm2_act_proj → better binary heads.

**T4 (H16):** Zero parameter change — only partitions attention differently. 16 heads × d_head=24 lets attention specialize in more diverse patterns. Never tested on J-series.

**T5 (W512):** Biggest capacity increase (~50M). If J3 is capacity-limited with d_cond=90, this reveals it. d_ff auto-scales to 2048. home/cop heads get 33% richer arm2_feat input.

**T6 (D15):** Tests the overfitting hypothesis. Phase 2 J3_DEMO showed binary-loss flatline from ep 11 — classic overfit signal. dropout 0.10→0.15 is a modest increase.

### Early monitoring strategy

J3 reference trajectory at epoch 20 (~4.5h in):
- val_JS = 0.058
- home_gap = 0.089
- val_score = 0.102

**Decision rules at ep 20-25:**
- home_gap > 0.12 → trial likely worse than J3 on AT_HOME (flag but let run)
- val_JS > 0.10 → activity arm struggling (except T5/W512 which converges slower)
- home_loss flatline at ~0.51 → demographics not helping binary heads

### Bundle

`_bundle_J3_D2_v1/` — 6 YAML configs, 6 SLURM wrappers, 1 deploy script, patched 04D for dropout env var.

---

## Phase 8: CrossAttn COP Rescue — Inference Fixes + Training Proposals

### Premise

G4/H_Time have much better training losses than J3 (cop_loss 0.062–0.064 vs 0.192, act_loss 0.071–0.077 vs 0.088). The encoder representations are genuinely superior. The failure is purely COP decoding at inference — cascading errors across 7 binary channels × 48 slots (exposure bias). Worth investigating whether inference-side or training-side fixes can rescue these architectures before abandoning them.

### Supporting documents

- `step4_Speed-Cluster_docs/comparision.md` — full architecture comparison (Tables 1–3, training losses + inference gate results)
- `step4_Speed-Cluster_docs/investigations/SWOT_architecture_analysis.md` — SWOT analysis of architecture families, P1–P6 proposals (invalidated), Phase B/C options

### Current gate scores (CrossAttn vs J3)

| Model | AT_HOME RMS | COP max gap | act_JS | Composite | Gates |
|---|---|---|---|---|---|
| **J3** | **4.57 pp** | **~2.03 pp** | **0.0191** | **0.6355** | **4/4** |
| G4 | 5.66 pp | 20.55 pp | 0.0296 | 1.2564 | 1/4 |
| H_Time | 5.68 pp | 22.86 pp | 0.0233 | 1.3214 | 1/4 |
| G3 | 6.06 pp | 19.77 pp | 0.0241 | 1.2284 | 1/4 |

### Phase 8A — No retraining needed (test first)

| # | Method | Idea | Cost |
|---|---|---|---|
| A1 | Multi-sample selection | Generate 50–100 samples per respondent from G4, score each for COP consistency, keep the best. The AR decoder sometimes gets COP right; you just need to find those samples. | ~1 GPU-hour (existing checkpoint) |
| A2 | Beam search on COP channels | Instead of greedy slot-by-slot, keep top-K partial COP sequences and prune bad paths early via cumulative log-prob. | ~2 GPU-hours (modify generate only) |

**Test script:** `04E_cop_rescue_test.py` — runs 3 sub-tests on 5000-respondent subset:
1. Seed variance (10 seeds) — is COP gap systematic or random?
2. COP feedback threshold sweep (0.3–0.7) — does binarization threshold matter?
3. Per-respondent Bernoulli multi-sample (K=10) — does cherry-picking fix aggregate?

**Phase 8A RESULTS (job 936884, 2026-05-26) — FAILED, all tests above gate:**

| Test | Best result (pp) | Gate (pp) | Ratio | Verdict |
|---|---|---|---|---|
| 1. Seed variance (10 seeds) | 20.65 (min), std=0.12 | 5.0 | 4.1× | SYSTEMATIC_BIAS |
| 2. Threshold sweep (best=0.70) | 12.88 (Spouse flips) | 5.0 | 2.6× | Alone↔Spouse trade-off |
| 3. Multi-sample K=10 (cherry-pick) | 14.89 (per-respondent) | 5.0 | 3.0× | No cherry-pick escape |

**Test 1 detail:** All 10 seeds land at 20.65–21.02 pp (Alone always worst channel). Zero variance — not random noise, pure systematic over-generation of "Alone" states.

**Test 2 detail:** Raising threshold from 0.50→0.70 suppresses Alone (20.95→11.51 pp) but creates symmetric Spouse deficit (1.58→−12.88 pp). The model learned a biased Alone/Spouse trade-off — you can shift the bias but not eliminate it.

**Test 3 detail:** 10 Bernoulli COP samples per respondent, best-per-respondent selection: 14.89 pp. Samples nearly uniform in selection distribution (952–1049 per seed) — no "lucky" seeds exist.

**Conclusion:** COP bias is structural in the G4 decoder. Inference-only fixes cannot bring COP max gap below ~12.88 pp (2.6× above gate). Phase 8A is CLOSED. Proceed to Phase 8B (retraining).

### Phase 8B — Retraining required

**Key insight from 8A:** The COP bias is not high-variance noise — it's a learned systematic over-generation of "Alone" states (+21 pp) and under-generation of social copresence channels. The AR decoder feedback loop at lines 423–424 of G4 (`cop_probs > 0.5` → binary → fed back as `aux_t`) locks in the bias slot-by-slot. Any fix must break this feedback loop during training, inference, or both.

**Why J3 alone isn't enough:** J3 passes 4/4 gates (composite 0.6355) but its binary outputs (home_loss=0.351, cop_loss=0.192) cause snowball errors in Steps 5–7 (census linkage, longitudinal forecasting, BEM schedule injection). The downstream pipeline amplifies AT_HOME and COP inaccuracies — J3's composite score masks binary weakness that compounds through the full pipeline. We returned to Step 4 specifically because of this.

**Why B2 is the path:** G4/H_Time encoders learn far superior binary representations (home_loss=0.22, cop_loss=0.064) but the AR decoder destroys COP at inference. The fix: keep G4's encoder + AR decoder for activity+home, replace COP with NAT parallel prediction. This is NOT J3 rebranded — key differences:
- AR decoder feeds back activity + AT_HOME (G4 achieves home_loss 0.22 vs J3's 0.35 — home stays in AR where it's stronger)
- Only COP moves to NAT (the 7-channel cascading problem)
- G4's encoder, trained against a single-decoder objective, may produce different/better features than J3's encoder

**Triage decisions (post-8A):**
- **B1 SKIP:** COP dropout is a softer version of what 8A already disproved. Dropout makes the model more robust to imperfect context but doesn't eliminate the AR feedback loop at inference. 8A proved the bias is structural, not a robustness problem.
- **B2 BUILD:** The whole bet. G4 encoder + AR decoder (activity + AT_HOME) + NAT branch (COP only). Targets exactly the binary weakness that blocks Steps 5–7.
- **B3 SKIP:** Scheduled sampling at p=0.2 already failed in G3. Heavier doses would likely degrade activity quality without fixing COP.
- **Phase 8C SKIP:** All 6 options keep AR COP — they cannot fix the structural cascading problem. Irrelevant once B2 exists.

#### B2 Architecture: G4_NAT_COP

**Tag:** `G4_NAT_COP`

**Structure:**
```
Encoder (shared, identical to G4):
  6-layer TransformerEncoder, d_model=384, n_heads=8, d_ff=1536
  CLS token = MLP(cond_vec ∥ cycle_emb)
  Input: [CLS, slot_0, ..., slot_47] → (B, 49, d_model)

AR Decoder (Arm 1 — activity + AT_HOME):
  6-layer CrossAttnDecoder, causal mask
  Input per slot: act_emb ∥ home_tok (d_act + 1, NO COP feedback)
  Heads: act_head(d_model → 14), home_head(d_model → 1)
  Shift-right with BOS token, sinusoidal PE

NAT Branch (Arm 2 — COP only):
  Input: encoder_slots ∥ act_proj(act_probs.detach()) ∥ home_proj(home_probs.detach()) ∥ cond_vec ∥ cycle_emb ∥ strata_oh
  arm2_proj: Linear(d_model + d_model + d_model + d_cond + d_cycle + 3, d_model)
  Head: cop_head = Tanh → Linear(d_model → 9)
  All 48 slots predicted in parallel (no cascading)
```

**Training forward():**
1. `memory = encode(act_seq, aux_seq, cond_vec, cycle_idx)` — shared encoder
2. `act_logits, home_logits = decode(dec_act_seq, dec_home_seq, tgt_strata, memory, ...)` — AR decoder, teacher-forcing with ground-truth activity + home
3. `act_probs = softmax(act_logits.detach())` — soft activity for Arm-2
4. `home_probs = sigmoid(home_logits.detach())` — soft home for Arm-2
5. `arm2_feat = _arm2_fuse(memory, act_probs, home_probs, cond_vec, cycle_idx, tgt_strata)` — NAT fusion
6. `cop_logits = cop_head(arm2_feat)` — parallel COP, (B, 48, 9)

**Inference generate():**
1. Encode source diary
2. AR loop (48 steps): predict activity + home, feed back act_emb + home_tok (NO COP)
3. After loop: `act_probs = one_hot(gen_acts)`, `home_preds = gen_homes`
4. NAT: `arm2_feat = _arm2_fuse(memory, act_probs, home_preds, ...)` → `cop_head(arm2_feat)`
5. Return gen_acts, gen_homes, cop_binary — COP predicted in one shot, zero cascading

**Training config:**
- lambda_act=1.0, lambda_home=0.6, lambda_cop=0.3, lambda_marg=0.1
- label_smooth=0.05, sched_sample_p=0.0
- d_cond=76 (G1 data, no demographics expansion — Phase 7 showed d_cond=90 hurts)
- Optimizer: AdamW, lr=5e-5, ReduceLROnPlateau(factor=0.95, patience=5), clip_grad_norm=25
- max_epochs=100, patience=15, batch_size=256

### ~~Phase 8C — Training proposals (G4/H_Time hyperparameter variants)~~

**SKIPPED.** All 6 options (C1–C6) keep AR COP decoding — they cannot fix the structural cascading problem. Phase 8C is irrelevant once B2 addresses the root cause directly.

### Execution plan

1. ~~Run Phase 8A (A1+A2 via `04E_cop_rescue_test.py`)~~ — **DONE. FAILED.** Best result 12.88 pp (2.6× above gate). COP bias is structural.
2. **Phase 8B = B2 only.** Build G4_NAT_COP architecture, train from scratch with G4 hyperparameters, run full diagnostics (04E→04H→04I→04J). B1/B3 skipped.
3. If B2 passes 4/4 gates → scale capacity (deeper enc/dec, wider d_model) → re-run Steps 5–7.
4. If B2 fails → reassess whether the problem is encoder quality or loss recipe; compare B2 training losses against G4 and J3.

---

## Progress Log

### 2026-05-26 — Phase 7 planned + submitted

- Phase 6 (MDLM sweep Stages A–H) CLOSED. J3 confirmed as sole 4/4 gate winner.
- Composite score decomposition revealed cop_cal_MAE bias; future evaluation uses individual gates only.
- Phase 7 designed: 6 parallel J3 trials (demographics + architecture HPT).
- Bundle `_bundle_J3_D2_v1/` built: 6 configs, 6 wrappers, patched 04D (DROPOUT env var), patched config_to_env.sh.
- Code changes: `04D_train.py` — added `DROPOUT` env var (default 0.1), J-series model_config uses it. `config_to_env.sh` — added `[dropout]=DROPOUT` mapping.

**Submitted 2026-05-26 (6 jobs):**

| Job ID | Tag | Architecture change |
|---|---|---|
| 936802 | J3_D2_CTRL | Demographics only (control) |
| 936803 | J3_D2_ENC8 | Deeper encoder (n_enc=8) |
| 936804 | J3_D2_DEC8 | Deeper decoder (n_dec=8) |
| 936805 | J3_D2_H16 | More heads (n_heads=16) |
| 936806 | J3_D2_W512 | Wider (d_model=512) |
| 936807 | J3_D2_D15 | Dropout 0.15 |

All on `outputs_step4_G2` (d_cond=90). ~6h per trial (T5/W512 may be slower). Check training logs at ep 20-25 (~4.5h in).

### 2026-05-26 — Early monitoring (~3h 41m in): capacity hypothesis emerges

**Cluster status:** 4 running (CTRL on cisr-1, ENC8 on cisr-2, DEC8 on speed-01, H16 on speed-01), 2 pending (W512, D15 — waiting on GPU allocation).

**Epoch 20 early signals vs J3 baseline (d_cond=76):**

| Model | Epoch reached | val_js (ep20) | home_gap (ep20) | Flags |
|---|---|---|---|---|
| J3 baseline (d76) | 87 (final) | 0.0694 | 0.0812 | reference |
| CTRL (d90) | 23 | 0.1235 | 0.1945 | val_js > 0.10, home_gap > 0.12 |
| ENC8 (d90) | 21 | 0.1203 | 0.1213 | val_js > 0.10, home_gap > 0.12 |
| DEC8 (d90) | 24 | **0.0902** | **0.0686** | both clear |
| H16 (d90) | 28 | **0.0965** | 0.1444 | home_gap > 0.12 |

**Latest-epoch comparison (D2 variant → J3 at same epoch):**

| Model | Epoch | val_js (D2 → J3) | home_gap (D2 → J3) |
|---|---|---|---|
| CTRL | 23 | 0.092 → 0.047 (2x behind) | 0.103 → 0.095 (close) |
| ENC8 | 21 | 0.066 → 0.043 (1.5x behind) | **0.051 → 0.064 (better!)** |
| DEC8 | 24 | 0.059 → 0.032 (1.8x behind) | 0.088 → 0.079 (close) |
| H16 | 28 | 0.038 → 0.019 (2x behind) | 0.081 → 0.078 (nearly identical) |

**Key finding — CTRL is weakest, capacity is the bottleneck:**

J3_D2_CTRL (same J3 architecture, only demographics added) is the worst performer across both val_js and home_gap. Meanwhile, architecture variants with more parameters (DEC8, ENC8, H16) are converging better. This means the 14 extra demographic features (d_cond 76→90) are useful, but **only if the model has enough capacity to absorb them**. Demographics alone without capacity = worse, not better.

This reframes the entire Phase 6 investigation: 40+ trials of topology search (J5-X2, J5-A/B, J5-F, J5-C, J_old) all failed to beat J3 — not because J3's topology was perfect and done, but because **topology was never the problem**. J3's wiring (AR + detach + Arm-2 NAT) was correct all along. What was missing was parameter capacity to exploit richer inputs.

**Implication for Round 2:** After single-axis results finish, combine winning capacity axes into multi-axis configs (e.g. DEC8+W512, DEC8+ENC8+H16, full MAX). Pair high-capacity with dropout=0.15 to prevent overfitting. Stop searching for the right architecture — start scaling the right one.

**Early rankings (preliminary, training ongoing):**
1. DEC8 — only variant clearing both ep20 thresholds
2. ENC8 — flagged at ep20 but home_gap beat J3 by ep21 (0.051 vs 0.064)
3. H16 — steady convergence, home_gap nearly matches J3 at ep28
4. CTRL — weakest, both metrics lagging

**Binary gate detail — all architecture variants beat CTRL:**

| Model | Epoch | home_gap | vs CTRL |
|---|---|---|---|
| CTRL | 23 | 0.103 | — (floor) |
| ENC8 | 21 | **0.051** | 2x better |
| DEC8 | 24 | 0.088 | 17% better |
| H16 | 28 | 0.081 | 21% better |

Every capacity increase improves the binary AT_HOME arm. CTRL is the floor — the binary head needs deeper architecture to translate d_cond=90 into AT_HOME predictions.

**Round 2 planning notes (pending single-axis completion):**

ENC8 is the priority axis for Round 2. The encoder is the shared trunk feeding both arms — deeper encoder = better feature extraction from 90 demographic inputs before the arm split. ENC8 already has the best binary performance (home_gap 0.051, half of CTRL). Proposed ENC8-based Round 2 variants:

| Tag | Changes | Est. params | Rationale |
|---|---|---|---|
| J3_D2_ENC10 | n_enc=10 | ~37M | Push encoder depth further — if 8 > 6, does 10 > 8? |
| J3_D2_ENC8_W512 | n_enc=8, d_model=512 | ~58M | Best binary arm + width for feature absorption |
| J3_D2_ENC8_DEC8 | n_enc=8, n_dec=8 | ~37M | Full depth both sides |
| J3_D2_ENC8_H16 | n_enc=8, n_heads=16 | ~33M | Deeper trunk + finer attention specialization |

Also test CTRL with added capacity (e.g. CTRL+W512) to confirm demographics need capacity, not just depth.

**Full gate comparison across all D2 variants (ep 21, same-epoch):**

| Model | val_js (activity) | home_gap (AT_HOME) | cop_loss (COP proxy) | val_score (composite) | home_loss |
|---|---|---|---|---|---|
| CTRL | 0.0894 | 0.1186 | 0.2125 | 0.1487 | 0.4048 |
| ENC8 | **0.0658** | **0.0506** | 0.2126 | **0.0911** | **0.4035** |
| DEC8 | **0.0720** | 0.1110 | 0.2127 | 0.1275 | **0.4017** |
| H16 | 0.1066 | 0.1870 | 0.2126 | 0.2001 | 0.4049 |

**Full gate comparison (each model's latest epoch):**

| Model | Epoch | val_js | home_gap | cop_loss | val_score | home_loss |
|---|---|---|---|---|---|---|
| CTRL | 23 | 0.0921 | 0.1025 | 0.2115 | 0.1433 | 0.4013 |
| ENC8 | 21 | 0.0658 | 0.0506 | 0.2126 | 0.0911 | 0.4035 |
| DEC8 | 24 | 0.0593 | 0.0876 | 0.2115 | 0.1031 | 0.3983 |
| H16 | 28 | 0.0383 | 0.0807 | 0.2093 | 0.0786 | 0.3951 |

**Gate-by-gate observations:**
- **Activity (val_js):** ENC8 and DEC8 beat CTRL at same epoch. H16 best overall (0.038) but 7 epochs ahead.
- **AT_HOME (home_gap):** ENC8 dominates — 0.051 vs CTRL's 0.119 at ep21 (2.3x improvement).
- **Copresence (cop_loss):** Nearly identical across all (~0.212). COP differentiation typically happens later (ep 50+).
- **home_loss:** Tiny differences. DEC8 and H16 slightly lower = better binary head fitting.
- **At ep21, ENC8 beats CTRL on every single metric.** H16 is a slow starter (behind CTRL at ep21) but converging fastest (ahead of everyone by ep28).

---

### 2026-05-26 — CTRL killed at ep38, W512 started (~5h 50m in)

**Decision:** J3_D2_CTRL (job 936802) cancelled to free GPU slot for pending W512.

**Rationale:** CTRL was the weakest D2 variant on every metric at every epoch. Its scientific purpose — isolating the effect of demographics from capacity — is fulfilled. The capacity hypothesis is confirmed: extra features (d_cond 76→90) without architecture capacity increase yields worse convergence than any capacity-expanded variant.

**CTRL final state (best checkpoint ep35):**

| Metric | ep35 (best) | ep38 (final) | J3 baseline @ep35 |
|---|---|---|---|
| val_js | 0.0227 | 0.0255 | 0.0131 |
| home_gap | 0.0538 | 0.0927 | 0.0429 |
| val_score | 0.0496 | 0.0718 | 0.0345 |

CTRL's best val_score (0.0496) is 1.4x worse than J3's at the same epoch (0.0345). No diagnostics run (killed pre-convergence). Training log archived to `CSV_records/J3_D2_CTRL_training_log.csv`. Rows added to `architecture_investigation.csv`, `training_config_investigation.csv`, `loss_values_trainings_investigation.csv`.

**Cluster state after kill:**

| Job | Status | Epoch | Note |
|---|---|---|---|
| J3_D2_ENC8 (936803) | RUNNING | ~34 | Priority axis for Round 2 |
| J3_D2_DEC8 (936804) | RUNNING | ~38 | 2nd best composite |
| J3_D2_H16 (936805) | RUNNING | ~44 | Best val_js, fastest convergence |
| J3_D2_W512 (936806) | RUNNING | ~0 | Just started (freed CTRL slot) |
| J3_D2_D15 (936807) | PENDING | — | Will start when next slot opens |

---

### 2026-05-26 — Phase 7 TERMINATED: all D2 jobs cancelled

**Decision:** All remaining jobs (ENC8, DEC8, H16, W512, D15) cancelled. Phase 7 single-axis capacity HPT is CLOSED without proceeding to diagnostics.

**Rationale:** Training loss analysis revealed a fundamental problem. All D2 variants have **home_loss flatlined at ~0.384–0.389** regardless of capacity axis. For comparison:
- J3 at ep47: home_loss = **0.367**, act_loss = 0.166, cop_loss = 0.196
- H16 at ep47: home_loss = **0.384**, act_loss = 0.281, cop_loss = 0.207

The d_cond=90 demographics are **hurting** convergence across the board. Capacity increases (deeper enc/dec, more heads) improved act_loss convergence rate but did NOT move the home_loss floor. The Arm-2 NAT binary heads cannot absorb the expanded demographics regardless of trunk capacity.

**Final state all D2 variants (at kill):**

| Variant | Final ep | Best ep | act_loss | home_loss | cop_loss | val_score |
|---|---|---|---|---|---|---|
| CTRL | 38 | 35 | 0.3908 | 0.3893 | 0.2082 | 0.0496 |
| ENC8 | 38 | 38 | 0.3598 | 0.3884 | 0.2065 | 0.0536 |
| DEC8 | 42 | 42 | 0.2961 | 0.3847 | 0.2065 | 0.0424 |
| H16 | 49 | 47 | 0.2806 | 0.3844 | 0.2065 | 0.0411 |
| W512 | 11 | 1 | 1.8757 | 0.5392 | 0.2865 | 0.1699 |
| D15 | — | — | — | — | — | — |

**Key finding:** The home_loss column is essentially flat (~0.384–0.389) across ALL variants including CTRL. Compare with historical architectures:
- G4/H_Tanh/H_Time achieved home_loss 0.21–0.23 (single-decoder CrossAttn)
- J5_X1b/J5_A achieved home_loss 0.22–0.24 (cross-arm gradient flow)
- J3 achieved home_loss 0.351 at best (Arm-2 NAT, d_cond=76)
- All D2 variants: home_loss 0.384–0.389 (Arm-2 NAT, d_cond=90)

**Diagnosis:** The problem is NOT capacity. It's that d_cond=90 makes the binary prediction task harder without the right architectural mechanism to exploit it. The Arm-2 NAT fusion receives the demographic conditioning but has no gradient path strong enough to learn the new features. Models with cross-arm gradient (J5_X1b) or single-decoder designs (G4/H) achieved much lower home_loss.

**Conclusion — Phase 7 SHELVED.** Next investigation should focus on:
1. The home_loss floor problem — why does d_cond=90 hurt binary heads?
2. Revisit architectures that achieved low home_loss (G4: 0.064 cop, J5_X1b: 0.158 cop) 
3. Consider whether the Arm-2 NAT design is the bottleneck for demographic absorption

All training logs archived to `CSV_records/`. Full comparison table at `step4_Speed-Cluster_docs/comparision.md`.

---

### 2026-05-26 — G3/G4 diagnostic results: CrossAttn AR is a dead end for COP

**Context:** Ran inference diagnostics (04E→04H→04I→04J) on G3 (job 936845) and G4 (job 936846) to evaluate whether CrossAttn decoder models could pass the 4 hard gates. These were the best-training-loss candidates from the G/H architecture family.

**Results:**

| Model | AT_HOME RMS (pp) | COP max gap (pp) | act_JS | Composite | Gates |
|---|---|---|---|---|---|
| G3 | 6.06 (FAIL) | 19.77 (FAIL, Spouse) | 0.0241 (PASS) | 1.2284 (FAIL) | 1/4 |
| G4 | 5.66 (FAIL) | 20.55 (FAIL, Alone) | 0.0296 (PASS) | 1.2564 (FAIL) | 1/4 |
| H_Time | 5.68 (FAIL) | 22.86 (FAIL, Alone) | 0.0233 (PASS) | 1.3214 (FAIL) | 1/4 |
| **J3** | **4.57 (PASS)** | **~2.03 (PASS)** | **0.0191 (PASS)** | **0.6355 (PASS)** | **4/4** |

**Critical finding: ALL CrossAttn AR decoders catastrophically fail COP at inference.** COP max gap ranges 19–23 pp vs threshold of 5.0 pp. This is not marginal — it's 4x the threshold. Meanwhile, J3 (Arm-2 NAT) achieves 2.03 pp on the same metric.

**Why scheduled sampling didn't help:** G3 used sched_sample_p=0.2, which successfully improved activity robustness (act_JS=0.024, best among CrossAttn models). But copresence cascading errors are a deeper problem than activity errors — copresence involves 7 channels of binary co-occurrence that compound multiplicatively across 48 time slots. Scheduled sampling helps activity (single categorical variable) but cannot fix multi-channel binary cascading.

**What this means for proposals P1–P6:** All 6 proposed architectures in the SWOT analysis were based on CrossAttn AR decoder (G4/H_Time variants). These proposals are now **invalidated** — no hyperparameter change (label_smooth removal, sched_sample tuning, learnable PE) can overcome the structural COP limitation.

**J3 is the only viable path.** Despite worse training losses (cop_loss=0.192 vs G4's 0.064), J3's Arm-2 NAT per-slot parallel fusion avoids cascading errors entirely. Each slot predicts independently from encoder features, not from previous predictions.

**Updated documents:**
- `step4_Speed-Cluster_docs/comparision.md` — Table 3 updated with G3/G4 results
- `step4_Speed-Cluster_docs/investigations/SWOT_architecture_analysis.md` — Table 3, diagnostic status, execution plan, and bottom-line all updated

**Next steps:** Pivot back to J3. The investigation should focus on improving J3's weaknesses (act_loss=0.088, home_loss=0.351) through capacity experiments or hybrid designs that pair NAT copresence with stronger activity/binary mechanisms.

---

### 2026-05-26 — CrossAttn rescue plan: inference fixes + training proposals

**Premise:** G4/H_Time have much better training losses than J3 (cop_loss 0.062–0.064 vs 0.192, act_loss 0.071–0.077 vs 0.088). The encoder representations are genuinely superior. The failure is purely COP decoding at inference — cascading errors across 7 binary channels × 48 slots. Worth investigating whether inference-side or training-side fixes can rescue these architectures.

**Phase A — No retraining needed (test first):**

| # | Method | Idea | Cost |
|---|---|---|---|
| A1 | Multi-sample selection | Generate 50–100 samples per respondent from G4, score each for COP quality, keep the best | ~1 GPU-hour (existing checkpoint) |
| A2 | Beam search on COP channels | Keep top-K partial COP sequences per slot, prune bad paths early via cumulative log-prob | ~2 GPU-hours (modify generate only) |

**Phase B — Retraining required (keep G4/H encoder):**

| # | Method | Idea | Cost |
|---|---|---|---|
| B1 | COP channel dropout | Randomly zero COP history 30–50% during training — forces model to not rely on perfect COP context | 1 training run (~6h) |
| B2 | Hybrid decode | CrossAttn AR for activity+home, parallel NAT head for COP only | Architecture change + 1 training run |
| B3 | Heavier scheduled sampling | G3 used p=0.2 (didn't fix COP). Try p=0.5 with curriculum 0→0.5 over 30 epochs | 1 training run |

**Phase C — Training proposals (G4/H_Time hyperparameter variants):**

| # | Tag | Change | Rationale |
|---|---|---|---|
| C1 | G4 no label smoothing | Remove label_smooth=0.05 | F-series proved home_loss=0.10 reachable without it |
| C2 | G4 tiny sched sampling (0.05) | Light scheduled sampling | G3's p=0.2 hurt activity but helped binary; try lighter dose |
| C3 | H_Time no label smoothing | Same as C1 on H_Time | H_Time has best overall training balance |
| C4 | G4 moderate sched sampling (0.10) | Midpoint between G4 (none) and G3 (0.2) | Second data point for dose sweep |
| C5 | G4 no smooth + Tanh heads | Remove smoothing, add Tanh safety net | Prevent instability that smoothing was designed to avoid |
| C6 | H_Time tiny sched sampling (0.05) | Combine H_Time's time encoding + light binary boost | Best architecture + best lightweight fix |

**Decision:** Test A1 + A2 first (cheap, no retraining). If results show variance in COP samples → multi-sample selection viable. If systematic bias → proceed to B1/B2. Phase C deferred until A/B outcomes known.

---

### 2026-05-26 — Phase 8A COMPLETE: inference fixes FAILED, COP bias is structural

**Job 936884** (cop_rescue on G4 checkpoint, 5000-respondent subset, ~2h runtime on cisr-1).

**Test 1 — Seed Variance (10 seeds, greedy COP):**
All 10 seeds produce 20.65–21.02 pp max gap (mean=20.85, std=0.12). "Alone" is always the worst channel. Verdict: **SYSTEMATIC_BIAS** — zero meaningful variance across random seeds.

**Test 2 — COP Threshold Sweep (0.30–0.70):**

| Threshold | Max gap (pp) | Worst channel | Alone gap | Spouse gap |
|---|---|---|---|---|
| 0.30 | 21.12 | Alone | +21.12 | +9.68 |
| 0.50 (default) | 20.95 | Alone | +20.95 | +1.58 |
| 0.60 | 17.74 | Alone | +17.74 | −6.93 |
| 0.65 | 15.08 | Alone | +15.08 | −10.65 |
| **0.70** | **12.88** | **Spouse** | +11.51 | **−12.88** |

Best result: 12.88 pp at threshold=0.70 — but the improvement comes from trading Alone over-generation for Spouse under-generation. The model learned a biased Alone↔Spouse seesaw that no threshold can fix.

**Test 3 — Per-Respondent Multi-Sample (K=10 Bernoulli):**
Individual samples: 16.90–17.86 pp (all Alone). Per-respondent cherry-pick: 14.89 pp. Selection distribution nearly uniform across seeds (952–1049) — no "lucky" draws exist.

**Summary vs gates:**

| Method | Best COP gap (pp) | Gate (5.0 pp) | J3 ref (2.03 pp) |
|---|---|---|---|
| Baseline (greedy, seed=42) | 20.55 | 4.1× above | 10.1× worse |
| Best seed (Test 1) | 20.65 | 4.1× above | 10.2× worse |
| Threshold=0.70 (Test 2) | 12.88 | 2.6× above | 6.3× worse |
| Cherry-pick K=10 (Test 3) | 14.89 | 3.0× above | 7.3× worse |

**Conclusion:** Phase 8A is CLOSED. Inference-side fixes reduce COP max gap from ~21 pp to ~13 pp at best — still 2.6× above the 5.0 pp gate. The COP bias is structural in the AR decoder: the model systematically over-generates "Alone" states and under-generates "Spouse" states, with no inference trick able to correct this without creating a symmetric opposite bias.

**Next:** Phase 8B (retraining with tricks). Priority options: B1 (COP channel dropout) and B2 (hybrid AR-activity + NAT-copresence).

---

### 2026-05-26 — Phase 8B-2 (G4_NAT_COP) submitted

**Architecture:** G4 encoder + CrossAttn AR decoder (activity + AT_HOME) + NAT branch (COP only).

**Key design decisions:**
- AR decoder feeds back `act_emb + home_tok` (d_act + 1) — NO COP in feedback loop
- Encoder slot embedding uses full context (act + AT_HOME + 9 COP) — same as G4
- Decoder slot embedding uses activity + home only — new `dec_slot_linear(d_act + 1, d_model)`
- NAT COP branch: `arm2_act_proj(act_probs.detach())` + `arm2_home_proj(home_probs.detach())` + encoder slots + conditioning → `arm2_proj → cop_head(Tanh→Linear→9)`
- `infer()` method: AR loop for activity+home, then one-shot NAT for all 48 COP slots

**Triage:**
- B1 SKIP: COP dropout is a softer version of what 8A already disproved — dropout reduces reliance on COP context but doesn't eliminate the AR feedback loop at inference
- B2 BUILD: Directly addresses the root cause — removes COP from AR cascading entirely
- B3 SKIP: G3's sched_sample p=0.2 already failed; heavier dose would hurt activity
- Phase 8C SKIP: All 6 options keep AR COP — irrelevant once B2 exists

**Files:**
- `04B_model_B2.py` — new `G4NATCopHybrid` class
- `04B_model.py` — added `G4NATCopHybrid` import via `_import_optional`
- `04D_train.py` — added `MODEL_TYPE == "G4_NAT_COP"` config, instantiation, and training hygiene
- `jobs/train_B2.sh` — SLURM wrapper
- `archive/04B_model_pre_B2.py` — predecessor archived

**Training config:** lambda_act=1.0, lambda_home=0.6, lambda_cop=0.3, lambda_marg=0.1, label_smooth=0.05, sched_sample=0.0, d_model=384, n_heads=8, 6-enc/6-dec, d_cond=76 (G1 data), batch=256, lr=5e-5, patience=15, max_epochs=100.

**Submitted:** job 936923, `outputs_step4_B2/`. ~6h expected. Check training logs at ep 20–25 (~4.5h in).

### 2026-05-28 — Phase 8B-2 (G4_NAT_COP) RESULTS: 2/4 gates, COP halved but still fails

**Training (job 936923):** early-stopped ep 81, best val_score 0.0341 (ep 66). 29.25M params. Final losses act=0.071 (= G4), home=0.221 (= G4), cop=0.183 (J3-level, expected for the NAT branch). AR side hit G4 quality exactly.

**Inference gates (job 937549, eval chain 04E→04H→04I→04J):**

| Gate | Threshold | B2 | Pass |
|---|---|---|---|
| composite | < 1.045 | **0.801** | ✓ |
| act_JS | ≤ 0.05 | **0.0202** | ✓ |
| AT_HOME RMS (pp) | ≤ 5.3 | **5.75** | ✗ (by 0.45) |
| COP max gap (pp) | ≤ 5.0 | **10.21** | ✗ (2.0×) |

**The bet half-worked.** NAT cut COP from G4's 20.55 pp to **10.2 pp** — roughly halved, cascading shape gone. But it lands halfway to J3 (2.03 pp), not at it.

**Failure mode = Spouse↓ / Alone↑ (not cascading):**
- COP max gap channel = **Alone** (+10.2 pp overall; worst slot = slot 1 / 00:30 night, **+30.6 pp**).
- **Spouse** systematically undershoots: −2.9 pp overall, −14 pp in 2015_2/3, −9 pp in 2022_2/3. Undershoot scales with the true spouse rate (worst in high-spouse 2015/2022 cohorts).
- `colleagues` overall gap (−6.0 pp) is a pooling artifact — the channel is absent in 2005–2010 surveys; per-cs 2015/2022 colleagues is fine (<1.5 pp).

**Root-cause diagnosis (`04B_model_B2.py`):**
1. **Not the safety multiply.** Alone's worst error is at night (slot 1) where `gen_home=1`, so `cop_prob[:,:,SPOUSE_IDX] *= gen_home` (line 337) is inactive. The `cop_head` itself fails to assign spouse co-presence when people are home asleep and defaults to Alone.
2. **The NAT cop_head regresses to the marginal.** 9 independent sigmoids (lines 156–158) over (encoder memory + detached act one-hot + binary home + cond_vec). "Married & home at night" vs "single & home at night" are identical in act+home space; the only discriminator (household/marital latent) reaches the head only faintly via cond_vec. Loss-minimizing bet = predict the population marginal (low Spouse, high Alone).
3. **Independent sigmoids = no mass conservation.** Nothing couples Alone to the company channels, so the mass Spouse loses inflates Alone freely. Spouse↓ and Alone↑ are one failure seen from two unconstrained heads.
4. **Inherited biased home generation.** B2's AT_HOME generation overshoots (+6.8 pp, RMS 5.75, fails gate) despite G4-level *training* home_loss (0.221). The NAT COP branch consumes that biased `gen_home`, so home generation error propagates into COP. J3 (clean home, RMS 4.57) → clean COP (2.03); B2 (biased home, 5.75) → degraded COP (10.2).
5. The hard binary `*= gen_home` is a secondary aggravator at daytime/away slots (Spouse worst slot 28 / 14:00) — clips real out-of-home couple time, asymmetric downward bias on the already-undershooting channel.

**Cross-architecture context (comparision.md):** training cop_loss does NOT predict inference COP gap. G4 cop_loss=0.064 → 20.55 pp; J3 cop_loss=0.192 (3× worse) → 2.03 pp. B2 cop_loss=0.183 (≈ J3) but COP gap 10.2 (≈ 5× J3) — the gap is explained by B2's biased home generation feeding the COP branch + the marginal-regression on Spouse, NOT by COP training fit.

**Verdict:** B2 does not pass. Premise that "G4's home is better" held only in *training loss*; in *generation* G4/B2 home (5.66/5.75 RMS) is worse than J3 (4.57). Next: fix directions under discussion — (1) feed household composition explicitly into `_arm2_fuse`, (2) replace hard `*= gen_home` with a soft/learned gate, (3) couple COP channels (Alone = 1 − P(any company)). Do NOT re-couple COP into the AR trunk (that is the G4/H_Time → 20 pp path).

---

### 2026-05-28 — Phase 8B-3: four single-axis B2 variants BUILT

**V1 cond_vec finding:** MARSTH (dims 9:15, 6 dims) and HHSIZE (dims 15:20, 5 dims) ARE present in `cond_vec` (d_cond=76, `outputs_step4_G1`, `step4_feature_config.json`). V1 is **BUILT** (not BLOCKED).

**Four variants, each exactly one change vs B2 (`G4NATCopHybrid`):**

| Tag | model_type | Class | File | Change |
|-----|-----------|-------|------|--------|
| B2a | G4_NAT_COP_HH | G4NATCopHH | 04B_model_B2a.py | `arm2_hh_proj(11→d_model)` for MARSTH+HHSIZE; dedicated per-slot HH embedding appended to arm2 fusion |
| B2b | G4_NAT_COP_MC | G4NATCopMC | 04B_model_B2b.py | Mass-coupled COP: z[0]→g=any-company; P(Alone)=1−g; P(company_i)=g·σ(z[i]); BCE on derived probs |
| B2c | G4_NAT_COP_SG | G4NATCopSG | 04B_model_B2c.py | Soft gate: cop_head input d_model+1 (appends continuous home_prob); inference uses sigmoid not binary; removes hard multiply |
| B2d | G4_NAT_COP_NATH | G4NATCopNATH | 04B_model_B2d.py | AT_HOME to NAT Arm-2: activity-only AR; dec_slot_linear d_act→d_model; home_head reads arm2_feat parallel to cop_head |

**Files created/modified (all in `step4_Speed_Cluster/`):**

New model files:
- `04B_model_B2a.py` — G4NATCopHH (V1 HH conditioning)
- `04B_model_B2b.py` — G4NATCopMC (V2 mass coupling)
- `04B_model_B2c.py` — G4NATCopSG (V3 soft gate)
- `04B_model_B2d.py` — G4NATCopNATH (V4 NAT home)

Edited:
- `04B_model.py` — added 4 `_import_optional` calls for B2a–d classes
- `04D_train.py` — added imports, `G4_NAT_COP_MC` loss branch in `compute_loss`, config block for all 4 types, 4 hygiene list updates (ReduceLROnPlateau, clip_norm=25, plateau step, past_warmup), 4 instantiation branches
- `04E_inference.py` — added 4 `getattr` imports + 4 `elif _mtype == ...` dispatch branches

New configs: `configs/B2a.yaml`, `configs/B2b.yaml`, `configs/B2c.yaml`, `configs/B2d.yaml`

New train jobs: `jobs/train_B2a.sh`, `jobs/train_B2b.sh`, `jobs/train_B2c.sh`, `jobs/train_B2d.sh`

New eval jobs: `job_step4_B2a_eval.sh`, `job_step4_B2b_eval.sh`, `job_step4_B2c_eval.sh`, `job_step4_B2d_eval.sh`

Archived (before edits): `archive/04B_model_pre_8B3.py`, `archive/04D_train_pre_8B3.py`, `archive/04E_inference_pre_8B3.py`

**Module pre-flight check:** All imports (torch, torch.nn, torch.nn.functional, math, os) are stdlib or PyTorch — no new deps beyond what B2 already uses. No yaml/eppy/joblib needed. Cluster env `/speed-scratch/o_iseri/envs/step4` already covers these.

**4 train sbatch commands (submit in parallel locally):**
```
sbatch /speed-scratch/o_iseri/occModeling/jobs/train_B2a.sh
sbatch /speed-scratch/o_iseri/occModeling/jobs/train_B2b.sh
sbatch /speed-scratch/o_iseri/occModeling/jobs/train_B2c.sh
sbatch /speed-scratch/o_iseri/occModeling/jobs/train_B2d.sh
```

**4 eval sbatch commands (after training completes):**
```
sbatch /speed-scratch/o_iseri/occModeling/job_step4_B2a_eval.sh
sbatch /speed-scratch/o_iseri/occModeling/job_step4_B2b_eval.sh
sbatch /speed-scratch/o_iseri/occModeling/job_step4_B2c_eval.sh
sbatch /speed-scratch/o_iseri/occModeling/job_step4_B2d_eval.sh
```

**No blockers.** All 4 variants built and ready for upload + submission.

---

### 2026-05-28 — Phase 8B-3: four variants TRAINING IN PROGRESS (results PENDING)

**Status:** all 4 submitted and RUNNING on `speed-17`.

| Job | Tag | model_type | State | Elapsed | ETA |
|-----|-----|-----------|-------|---------|-----|
| 937597 | B2a | G4_NAT_COP_HH | RUNNING | 4:33 | ~14 h |
| 937598 | B2b | G4_NAT_COP_MC | RUNNING | 4:33 | ~14 h |
| 937599 | B2c | G4_NAT_COP_SG | RUNNING | 4:33 | ~14 h |
| 937600 | B2d | G4_NAT_COP_NATH | RUNNING | 4:33 | ~14 h |

ETA from B2 baseline (936923 = 18h24m wall). At 4h33m in → ~14 h remaining; finish expected early **2026-05-29**.

**Mid-training snapshot (ep ~24, ~4.5 h, ~700 s/epoch — TRAINING losses + val proxies, NOT inference gates):**

| Variant | ep | act | home | cop | marg | val_JS | home_gap | best val_score (ep) |
|---------|----|-----|------|-----|------|--------|----------|---------------------|
| B2a HH | 23 | 0.419 | 0.267 | 0.192 | 0.004 | 0.024 | 0.148 | 0.0948 (21) |
| B2b MC | 24 | 0.413 | 0.266 | 0.193 | 0.004 | 0.020 | 0.140 | 0.0746 (23) |
| B2c SG | 24 | 0.420 | 0.267 | 0.194 | 0.004 | 0.025 | 0.152 | 0.0890 (23) |
| B2d NATH | 24 | 0.427 | **0.397** | 0.202 | 0.011 | 0.030 | **0.075** | **0.0674 (24)** |

Read of the snapshot:
- **~1/3 through.** act_loss still falling steeply; none converged (B2 baseline best ep66, stopped ep81). Expect best checkpoints ~ep 60–80.
- **cop ≈ 0.19** for B2a/b/c = J3-level, exactly as designed for the NAT branch. B2d cop ≈ 0.20.
- **B2d home ≈ 0.40 is NOT a regression** — moving AT_HOME into NAT Arm-2 shifts home_loss into the J-series regime (~0.35, see comparision.md key obs), which measures something different from the G4-regime ~0.27 in a/b/c.
- **Early proxy tell:** B2d (NATH) leads val_score (0.067) and home_gap (0.075); B2b (MC) second (0.075 / 0.140). Consistent with the "clean home → clean COP" thesis (NATH = highest leverage). **But these are losses + val proxies, not gates** — B2 had val_score 0.034 yet failed COP at 10.2 pp. No gate verdict until the eval chain runs.

**Results table (FILLED 2026-05-29, all 4 `EVAL COMPLETE`).** Lead with COP max gap and AT_HOME RMS. Bar to beat = J3 (4/4). B2 baseline = 2/4.

| Variant | COP max gap (≤5.0) | AT_HOME RMS (≤5.3) | act_JS (≤0.05) | composite (<1.045) | Gates | Targets which failure |
|---------|--------------------|--------------------|----------------|--------------------|-------|-----------------------|
| **J3** (bar) | 2.03 ✓ | 4.57 ✓ | 0.0191 ✓ | 0.6355 ✓ | 4/4 | — (reference) |
| **B2** (base) | 10.21 ✗ | 5.75 ✗ | 0.0202 ✓ | 0.801 ✓ | 2/4 | — (reference) |
| B2a HH | 7.99 ✗ | 7.78 ✗ | 0.0697 ✗ | 0.923 ✓ | **1/4** | Spouse marginal-regression (explicit MARSTH/HHSIZE → cop_head) |
| B2b MC | 10.50 ✗ | 7.63 ✗ | 0.0659 ✗ | 0.983 ✓ | **1/4** | Alone overshoot (mass coupling: Alone=1−g, no free inflation) |
| B2c SG | 9.67 ✗ | 6.14 ✗ | 0.0279 ✓ | 0.802 ✓ | **2/4** | Spouse daytime clip (soft gate replaces hard `*= gen_home`) |
| B2d NATH | 7.07 ✗ | **4.94 ✓** | 0.0238 ✓ | **0.670 ✓** | **3/4** | Biased home feeding COP (AT_HOME→NAT, J3-style; highest leverage) |

**Next:** when all 4 leave the queue, submit the 4 eval jobs (commands above), scp down `diagnostics_{H,I,J}_B2{a,b,c,d}.json`, fill this table, compare to J3, write the RESULTS verdict.

### 2026-05-29 — Phase 8B-3: all 4 trainings COMPLETE; eval chain SUBMITTED + RUNNING

All 4 jobs left the queue cleanly — every log shows `TRAINING COMPLETE` with a best checkpoint (`outputs_step4_B2{a,b,c,d}/checkpoints/best_model.pt`, ~117 MB each, written May 28–29).

**Final training scores — at the BEST checkpoint** (the model that gets evaluated; pulled from each `step4_training_log.csv`, NOT the last epoch, which is ~15 ep past it and overfit). Format `best ep (stop ep)`:

| Variant | model_type | best ep (stop) | val_score | act | home | cop | home_gap |
|---------|-----------|----------------|-----------|-----|------|-----|----------|
| B2a HH | G4_NAT_COP_HH | 33 (48) | 0.0549 | 0.251 | 0.253 | 0.189 | 0.0895 |
| B2b MC | G4_NAT_COP_MC | 35 (50) | 0.0444 | 0.245 | 0.252 | 0.189 | 0.0728 |
| B2c SG | G4_NAT_COP_SG | 66 (81) | 0.0391 | 0.094 | 0.231 | 0.185 | 0.0685 |
| **B2d NATH** | G4_NAT_COP_NATH | 62 (77) | **0.0138** | 0.099 | 0.371 | 0.194 | **0.0200** |

Reference (comparision.md, best ckpt): **J3** ep72 — act 0.088, home 0.351, cop 0.192, val_score 0.0166 (4/4). **B2** base ep66 — val_score 0.0341 (2/4, COP 10.2 pp).

Read:
- **B2d NATH is a J3-twin in training space** — act 0.099 (≈ J3 0.088), home 0.371 (≈ J3 0.351), cop 0.194 (= J3 0.192) — but with a *better* val_score (0.0138 < 0.0166) and the tightest home_gap (0.020). Expected: NATH moves AT_HOME into NAT Arm-2, replicating J3's topology. Strongest proxy of the four.
- **B2c SG**: best activity fit (act 0.094) but home stays G4-regime (0.231) — it keeps the CrossAttn home path, only softening the gate. The home_loss regime is the AT_HOME-gate risk to watch.
- **B2a HH / B2b MC stalled early** (best ep 33/35) with activity badly under-fit (act ≈ 0.25, ~3× J3). The added structure (HH proj / mass-coupling reparam) made optimization harder — val_score stopped improving while train act was still falling (overfit). Weakest pair on training.
- **cop ≈ 0.19 across all four** (NAT branch, by design); B2d home ≈ 0.37 = J-series regime, not a regression.
- **Caveat that has burned us every cycle:** training scores do NOT predict the gates. G4 had the best training losses in the whole table and failed COP at 20 pp; B2 had val_score 0.034 and failed COP at 10.2 pp. The eval chain (running) is the only verdict.

**Eval chain submitted** (verified scripts + checkpoints present first):

| Eval job | Variant | State | Node |
|----------|---------|-------|------|
| 939105 | B2a | RUNNING | cisr-1 |
| 939106 | B2b | RUNNING | cisr-2 |
| 939107 | B2c | RUNNING | speed-01 |
| 939108 | B2d | RUNNING | speed-01 |

Each runs 04E (inference) → 04H (AT_HOME) → 04I (activity + COP) → 04J (composite), writing `diagnostics_{H,I,J}_B2<x>.json` into the variant's output dir. **Next:** on queue-empty, confirm each eval log reached `EVAL COMPLETE` (queue-empty alone doesn't prove success), scp the 12 JSONs down, fill the PENDING table above (lead with COP max gap + AT_HOME RMS), and write the verdict vs J3.

### 2026-05-29 — Phase 8B-3 RESULTS: B2d NATH best at 3/4, none beats J3; COP still open

All 4 evals reached `EVAL COMPLETE` (logs `logs/B2{a,b,c,d}_eval_<jobid>.out`); 12 diagnostics JSONs pulled to `step4_Speed_Cluster/`. Gates scored from each `diagnostics_J_B2<x>.json` → `composite.components`. See the now-filled results table above.

**Headline: no variant passes 4/4 — J3 still stands alone. Best is B2d NATH at 3/4** (passes AT_HOME, act_JS, composite; **only COP max gap fails, 7.07 > 5.0**).

**Per-variant verdict:**
- **B2d NATH (3/4) — the one to build on.** Moving AT_HOME out of the AR trunk into NAT Arm-2 (J3's topology) did exactly what the training proxy predicted: **AT_HOME RMS 5.75 → 4.94 (now PASSES**, near J3's 4.57), composite 0.801 → **0.670** (best of all four, near J3's 0.6355), and COP dragged down 10.21 → **7.07** as a *side effect* of cleaner home feeding the COP head. Crucially this was achieved **without re-coupling COP into the AR trunk** — so the NAT-split direction is validated, not the dead end. But COP 7.07 still misses the ≤5.0 gate: moving AT_HOME alone does not fully fix Spouse-collapse.
- **B2c SG (2/4) — flat.** Soft home gate held activity (act_JS 0.0279 ✓) and composite (0.802, = baseline) but did **not** fix COP (9.67, barely off 10.21) or AT_HOME (6.14 ✗). Softening the gate alone is insufficient; it keeps the CrossAttn home path (G4-regime home_loss 0.231), which is the AT_HOME risk we flagged.
- **B2a HH (1/4) and B2b MC (1/4) — regressions.** Both **broke act_JS** (0.070 / 0.066, was 0.0202 ✓ at baseline) — the training under-fit (best ep 33/35, act ≈ 0.25) showed up directly as activity-distribution failure at inference. B2b mass-coupling didn't even dent COP (10.50, *worse* than baseline). Added structure (HH proj / Alone=1−g reparam) made optimization harder for no gate gain.

**What this confirms:** the training-space proxy held this cycle — B2d (the J3-twin: act 0.099 / home 0.371 / cop 0.194, val_score 0.0138) was the clear inference winner; the under-fit pair (B2a/B2b) were the clear losers. AT_HOME genuinely *wants* to live in the NAT arm (J3 and now B2d both confirm). COP improves when home is clean but is **not** solved by it — the residual 7.07 pp is a COP-head problem, to be closed on top of the NATH base **without** AR coupling.

**Decision: next direction under discussion.** B2d NATH is the new working base. Open options to close COP 7.07 → ≤5.0 (all keep AT_HOME in NAT, none touch the AR trunk): stack a COP-specific fix onto NATH — e.g. (a) household/marital conditioning *inside the NAT Arm-2 COP path* (B2a's idea, but on the NATH topology where activity isn't starved), (b) Spouse-channel reweighting / focal loss on the cop_head, (c) mass-coupling applied *only* at the NAT COP head. Do **not** revisit B2b's global reparam or any AR-trunk COP coupling.

---

## Phase 8B-4: J6 — J3 trunk + COP-path conditioning

### 2026-05-29 — J6 family BUILT; smoke PASS; awaiting cluster submission

**Aim:** Test whether demographic + home conditioning injected at the cop_head input (Arm-2 NAT path) closes the residual COP gap (7.07 pp → ≤5.0) on top of J3's 4/4 topology. Base = `JSeriesHybrid` in `04B_model.py`; J3 wiring untouched.

#### Edits made

**Archive:** `step4_Speed_Cluster/archive/04B_model_preJ6_20260529.py` (predecessor copy per archive rule).

**04B_model.py — JSeriesHybrid:**
1. `__init__`: added `self.enable_hh_cop_cond = config.get("enable_hh_cop_cond", False)`. Added `self.arm2_hh_proj = nn.Linear(11, d_model)` when True. Added `"J6"` to the `arm2_act_proj` model-type tuple (line ~900) so J6 gets the d_model-projected activity input. Updated `_cop_in` formula: `d_model + (1 if enable_hierarchical_cop else 0) + (d_model if enable_hh_cop_cond else 0)`.
2. `forward` (standard AR-Arm1 → NAT-Arm2 path): replaced the single `if self.enable_hierarchical_cop` block with a unified `if self.enable_hierarchical_cop or self.enable_hh_cop_cond` builder; appends `home_probs.detach().unsqueeze(-1)` when hierarchical, appends `self.arm2_hh_proj(batch["cond_vec"][:, 9:20]).unsqueeze(1).expand(-1, T, -1)` when hh_cop_cond.
3. `infer` (standard path): same unified builder using `cond_vec[:, 9:20]`.
4. J_old / J5_F / J5_C / J5_X1 special branches left untouched.

**04D_train.py:**
- New `elif MODEL_TYPE == "J6":` branch (mirrors J3 config: d_model=args.d_model, d_ff=d_model×4, N_enc/dec=args.n_enc/dec_layers, dropout=DROPOUT, d_cond=d_cond). Reads `ENABLE_HIERARCHICAL_COP` and `ENABLE_HH_COP_COND` from env and injects into model_config.
- Added `"J6"` to model-dispatch tuple (line ~1016), scheduler-bypass tuple (line ~1062), and per-batch scheduler-skip guard (line ~1213).

**Scripts created:**
- `jobs/train_J6_HHC.sh` — ENABLE_HH_COP_COND=1, ENABLE_HIERARCHICAL_COP=0 (HH conditioning only)
- `jobs/train_J6_HC.sh`  — ENABLE_HH_COP_COND=0, ENABLE_HIERARCHICAL_COP=1 (home hierarchical only)
- `jobs/train_J6_HCHH.sh` — both flags 1 (combined)
- All 3: MODEL_TYPE=J6, LAMBDA_HOME=0.7, LAMBDA_ACT=1.0, LAMBDA_COP=0.3, LAMBDA_MARG=0.1, SPOUSE_NEG_WEIGHT=0.45, HOME_LABEL_SMOOTH=0.05, SCHED_SAMPLE_P=0.0, DROPOUT=0.1, --batch_size 256 --max_epochs 100 --patience 15 --lr 5e-5 --d_model 384 --n_heads 8 --n_enc_layers 6 --n_dec_layers 6, data_dir=outputs_step4_G1, #SBATCH --time=48:00:00.
- `job_step4_J6_HHC_eval.sh`, `job_step4_J6_HC_eval.sh`, `job_step4_J6_HCHH_eval.sh` — each runs 04E → 04H → 04I → 04J, writing `diagnostics_{H,I,J}_J6_<v>.json` into the variant output dir.

#### Smoke test results (--sample, CPU, 10 epochs each)

All 3 flag combos ran to completion with no concat-dim errors:

| Variant | Flags | cop_head[0] input dim | arm2_hh_proj | 10-ep best val_score |
|---------|-------|-----------------------|--------------|----------------------|
| J6_HHC  | HH=1, HC=0 | 128 (64+64) | Linear(11→64) ✓ | 0.2321 |
| J6_HC   | HH=0, HC=1 | 65  (64+1)  | None ✓         | 0.2077 |
| J6_HCHH | HH=1, HC=1 | 129 (64+1+64)| Linear(11→64) ✓ | 0.2602 |

- All 3 variants trained without errors through forward + infer (validate uses infer at every epoch).
- `arm2_act_proj` (J3 dim-balance fix) present in all 3 ✓.
- J_old / J5_F / J5_C branches confirmed untouched (only the final `elif ... or ...` block changed).

#### Config parity vs J3

J6 config equals J3 except the two new flags. Confirmed by reading the J3 branch (lines 671–698) vs the new J6 branch: same d_model×4 d_ff, same N_enc/N_dec, same d_act/d_cycle, same aux_stratum_head=False. The two flags default False → J6 with both flags off is byte-identical to J3 forward/infer.

#### Blockers
None. Manager to submit 3 sbatch jobs when ready.

#### 2026-05-29 — Manager review + cluster upload

Manager audited the build before committing GPU time:
- `04B_model.py` forward (lines 1268–1282) and infer (1383–1396) build `cop_input` by the **same** concat order `[binary_input, home_probs.detach()?, hh_emb?]`, so trained weights map correctly at inference. `home_head` reads `binary_input` only — home path untouched → AT_HOME-safe by construction. `home_probs` detached before the COP path (no backprop into home via the prob input).
- `04D_train.py` J6 branch (822–856) config = J3 except the two flags; full-run `d_ff=d_model×4=1536`, `d_act/d_cycle=32`. J6 in dispatch/scheduler/skip tuples.
- No new deps (`arm2_hh_proj` is pure-torch `nn.Linear`); same `envs/step4` that ran B2d.

Uploaded to `/speed-scratch/o_iseri/occModeling/` (2 edited `.py` + 3 eval to BASE, 3 train to `jobs/`); presence verified by `ls`. Success criterion: hold J3's 4/4 gates (AT_HOME guardrail) while tightening COP below J3's 2.03 margin.

**8B-4 SUBMITTED 2026-05-29** — 3 parallel J6 trainings RUNNING:

| Job ID | Variant | Flags | Node |
|--------|---------|-------|------|
| 939524 | J6_HHC  | HH=1, HC=0 | cisr-1 |
| 939525 | J6_HC   | HH=0, HC=1 | cisr-2 |
| 939526 | J6_HCHH | HH=1, HC=1 | speed-01 |

All got nodes immediately. Next: on training completion submit the 3 `job_step4_J6_*_eval.sh` chains, then scp `diagnostics_{H,I,J}_J6_*.json` and score vs gates.

---

### 2026-05-29 — J6_HT (4th variant) BUILT + SUBMITTED

**Aim:** Add a 4th J6 axis — `ENABLE_HOME_TEMPORAL` — a residual depthwise temporal Conv1d on the Arm-2 features before `home_head`, so the AT_HOME prediction can learn transition timing and midday level. COP and activity paths untouched. Single-axis isolation: only the new flag is set; the two existing COP flags are off.

#### Archive

`archive/04B_model_preJ6HT_20260529.py` — predecessor copy taken before edits (per architecture-edit rule).

#### Edits made

**04B_model.py — JSeriesHybrid:**

1. `__init__` flag (after `enable_hh_cop_cond`):
   ```python
   self.enable_home_temporal = config.get("enable_home_temporal", False)
   ```
2. Layer construction (immediately after `home_head` block, before `cop_head`):
   ```python
   if self.enable_home_temporal:
       self.home_temporal = nn.Conv1d(d_model, d_model, kernel_size=5, padding=2, groups=d_model)
       nn.init.zeros_(self.home_temporal.weight)
       nn.init.zeros_(self.home_temporal.bias)
   ```
   **Zero-init rationale:** depthwise conv with all-zero weights is the identity map (output = 0 added to binary_input residual), so J6_HT at init is byte-identical to J3's home path. Training can specialise the temporal filter without a cold-start regression.
3. Helper method `_home_feat` added after `_arm2_fuse` (before CRF helpers section):
   ```python
   def _home_feat(self, binary_input):
       if self.enable_home_temporal:
           t = self.home_temporal(binary_input.transpose(1, 2)).transpose(1, 2)
           return binary_input + t
       return binary_input
   ```
4. `forward` (standard AR → NAT path, line ~1278): `home_logits = self.home_head(self._home_feat(binary_input)).squeeze(-1)`
5. `infer` (standard path, line ~1380): `home_logits_inf = self.home_head(self._home_feat(binary_input)).squeeze(-1)`
6. **COP path verified untouched:** `cop_parts = [binary_input]` (not `_home_feat(binary_input)`) in both forward and infer — raw `binary_input` feeds cop_head as before.

**04D_train.py — J6 branch:**

Added alongside the two existing flags:
```python
_j6_ht = os.environ.get("ENABLE_HOME_TEMPORAL", "0") == "1"
```
And `"enable_home_temporal": _j6_ht,` in both the `--sample` and full `model_config` dicts.

**Scripts created:**

- `jobs/train_J6_HT.sh` — cloned from `train_J6_HHC.sh`; changes: job-name/logs → `J6_HT`; mkdir → `outputs_step4_J6_HT/checkpoints`; `ENABLE_HIERARCHICAL_COP=0`, `ENABLE_HH_COP_COND=0`, `ENABLE_HOME_TEMPORAL=1`; `--output_dir`/`--checkpoint_dir` → `outputs_step4_J6_HT`. J3 recipe identical: LAMBDA_HOME=0.7, LAMBDA_ACT=1.0, LAMBDA_COP=0.3, LAMBDA_MARG=0.1, SPOUSE_NEG_WEIGHT=0.45, HOME_LABEL_SMOOTH=0.05, SCHED_SAMPLE_P=0.0, DROPOUT=0.1, --batch_size 256 --max_epochs 100 --patience 15 --lr 5e-5 --d_model 384 --n_heads 8 --n_enc_layers 6 --n_dec_layers 6, `#SBATCH --time=48:00:00`.
- `job_step4_J6_HT_eval.sh` — cloned from `job_step4_J6_HHC_eval.sh`; `OUT=outputs_step4_J6_HT`; diagnostics written as `diagnostics_{H,I,J}_J6_HT.json`; job-name `J6_HT_eval`.
- `jobs/smoke_J6_HT.sh` — 15-min compute-node smoke (no local Python/data available); `--sample` flag, MODEL_TYPE=J6, ENABLE_HOME_TEMPORAL=1, 10 epochs.

#### Smoke test

No local `envs/step4` or `outputs_step4_G1`; smoke submitted to a compute node.

- **Smoke job ID: 939535** (`smoke_J6_HT`) — submitted 2026-05-29; RUNNING on speed-03 at submission confirmation. Expected: 10 epochs, no shape error, home output (B,48), cop output (B,48,9), `self.home_temporal = Conv1d(64,64,k=5,groups=64)` under d_model=64 --sample. With flag off the home path is byte-identical to J3.

#### Upload confirmation

Uploaded in one bundle (locally):
```
"04B_model.py","04D_train.py","job_step4_J6_HT_eval.sh" | ForEach-Object { scp GSSCanada-main\...\$_ o_iseri@speed:occModeling/ }
"train_J6_HT.sh","smoke_J6_HT.sh" | ForEach-Object { scp ... o_iseri@speed:occModeling/jobs/ }
```

#### Training submission

**J6_HT job ID: 939536** — submitted 2026-05-29 alongside 939524–26; PENDING (AssocGrpGRES) at submission — normal GPU queue behaviour, will start when a slot opens.

| Job ID | Variant  | Key flag              | Status at submission |
|--------|----------|-----------------------|----------------------|
| 939524 | J6_HHC   | HH_COP_COND=1         | RUNNING cisr-1       |
| 939525 | J6_HC    | HIERARCHICAL_COP=1    | RUNNING cisr-2       |
| 939526 | J6_HCHH  | both COP flags=1      | RUNNING speed-01     |
| 939536 | J6_HT    | HOME_TEMPORAL=1       | PENDING (queue)      |

**Eval deferred** — manager will submit all 4 eval chains (`job_step4_J6_{HC,HHC,HCHH,HT}_eval.sh`) together once all trainings complete, then compare `diagnostics_J_J6_*.json` composite scores vs gates.

#### Progress Log — 2026-05-29 (manager): J6_HT training done; eval cycle-1 bug + fix

**Training (939536):** COMPLETED clean (exit `0:0`, elapsed 03:10:34). Early-stopped at epoch 65 (patience 15; best = epoch 50). Best `val_score=0.0148` (`val_JS=0.0048`, home-gap proxy `0.0201`). Checkpoint contains `home_temporal` Conv1d → training wiring correct. Finished ~2 h before its siblings because it converged, not a crash.

**Eval cycle-1 (939677) — INVALID, not a gate result:** SLURM reported COMPLETED in 34 s, but `04E_inference.py` crashed at `load_state_dict`:
`RuntimeError: Error(s) in loading state_dict for ConditionalTransformer` (missing `decoder.*`/`home_head.weight`/`cop_head.weight`; unexpected `arm1_decoder.*`/`arm2_proj.*`/`home_temporal.*`/`home_head.0.*`/`cop_head.0.*`). Root cause: the model-dispatch tuple at `04E_inference.py:324-325` listed `J1…J5_C` but **not `"J6"`**, so the `model_type="J6"` checkpoint fell through to the `else: ConditionalTransformer` branch (line 359). 04E therefore wrote no `augmented_diaries.csv`; 04H/I/J then ran on missing data and each exited 0 (script has no `set -e`) → false-positive COMPLETED. The T6 values in `diagnostics_H_J6_HT.json` are observed HETUS reference only.

**Fix (one line, full-chain):** added `"J6"` to the `JSeriesHybrid` dispatch tuple at `04E_inference.py:325`, mirroring 04D's known-good line `04D_train.py:1053-1054`. Checkpoint and eval script left untouched (both valid). Uploaded patched 04E (`scp` → SCP_OK) and verified on cluster (`grep` shows `…"J5_C", "J6"):`). **This single fix covers all four J6 evals** — J6_HHC/HC/HCHH evals will now load correctly with the same patched 04E. Re-running J6_HT eval via `sbatch job_step4_J6_HT_eval.sh`; gate scorecard pending.

#### Progress Log — 2026-05-29 (manager): J6_HT eval cycle-2 — GATE SCORECARD (FAIL, 2/4)

**Eval cycle-2 (939686) — VALID:** COMPLETED `0:0`, elapsed **16:36** (vs the 34 s false-positive), `augmented_diaries.csv` = **192,183 rows**, all three `diagnostics_{H,I,J}_J6_HT.json` written. Canonical roll-up from `04J` `composite.components`:

| Gate | Threshold | J6_HT | J3 baseline | Pass? | vs J3 |
|------|-----------|-------|-------------|-------|-------|
| Composite | < 1.045 | **0.6866** | 0.6355 | ✅ | +0.051 worse |
| AT_HOME RMS | ≤ 5.3 pp | **6.10** | 4.57 | ❌ | **+1.53 pp worse** |
| COP max gap | ≤ 5.0 pp | **5.83** | 2.03 | ❌ | +3.80 pp worse |
| act_JS | ≤ 0.05 | **0.0351** | 0.0191 | ✅ | +0.016 worse |

**Verdict: 2/4 — FAILS. J6_HT does not beat J3 on any metric.** The residual depthwise temporal home head **regressed the exact metric it was designed to improve** (AT_HOME RMS 6.10 vs J3 4.57 — the hypothesis is falsified, not just unconfirmed). COP also degraded (5.83 vs 2.03) even though the COP heads read raw `binary_input` and the temporal residual feeds only `home_head`: the home loss back-propagates through `home_temporal` into the **shared trunk**, perturbing the trunk features the COP heads depend on. So the temporal head is net-harmful to the trunk. **Recommendation: shelve J6_HT.** Whether the temporal idea is worth salvaging (e.g. detach the trunk from the temporal residual, or apply it post-trunk only) is deferred until the other three J6 variants (HHC/HC/HCHH) report — full J6 row needed before next-step prompts.
