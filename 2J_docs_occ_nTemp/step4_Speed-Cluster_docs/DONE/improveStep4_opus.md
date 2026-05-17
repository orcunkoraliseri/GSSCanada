# improveStep4_opus.md — H-series proposal grounded in the prior-paper Transformer

**Aim.** Identify architectural simplifications, taken from the user's prior occupancy-modelling Transformer (Energy & Buildings, Sciencedirect S037877882600215X), that may close the residual hard-gate failures the G-series has plateaued on.

**Steps.**
1. Compare the prior-paper pipeline side-by-side against the current Step-4 G3 stack.
2. Surface the deltas that are likely load-bearing for performance vs. cosmetic.
3. Translate load-bearing deltas into discrete, ranked H-series experiment candidates.
4. Recommend a tier-ordered execution sequence that does not block on G3.

**Expected result.** A ranked list of six H-series candidates, each tied to a specific gate-failure mechanism, each scoped as a single-axis tag-edit, with explicit compatibility checks against the live G3 path.

**Test method.** Each H-series candidate succeeds when its `results_index/results.csv` row clears more of the four hard gates than the corresponding G-series baseline:
- composite (val_JS + 0.5·AT_HOME gap) < 1.045
- AT_HOME error ≤ +5.3 pp
- Spouse error ≤ +5 pp
- act_JS ≤ 0.05

---

## 1. Side-by-side comparison

| Axis | Prior paper (works) | Step-4 G3 (current) | Delta significance |
|---|---|---|---|
| Architecture | Transformer **encoder-only**, outputs the full 24-step sequence in one forward pass | **Encoder-decoder** (6+6 layers); decoder generates 48 slots autoregressively with teacher forcing | **HIGH** — creates the H3 problem class (autoregressive feedback) that G2 paid for |
| Encoder layers | 2 | 6 | MED |
| Decoder layers | n/a | 6 (FiLM in F-series → cross-attn in G3) | HIGH |
| d_model | Dynamic (sum of embedding dims + 4 cont; ~mid hundreds) | 256 (G1/G2) / 384 (G3) | LOW–MED |
| d_ff | **7168 / 8192 / 9216 / 10240** (tuned, very wide) | 1024 / 1536 (G3) | **HIGH** — ~5–10× per-layer width gap |
| n_heads | 4 | 8 | LOW |
| Dropout | 0% on transformer / embeddings; 25% on output heads | 0.1 encoder; 0.0 decoder (G3) | LOW |
| Conditioning | **Concatenation** of all categorical embeddings + cyclical time + 4 continuous features at encoder input | FiLM (F) → **cross-attention over 3 conditioning tokens** `[demo, cycle, strata]` (G3) | **HIGH** — the entire F→G arc has been chasing conditioning sophistication the prior paper showed wasn't necessary on a harder problem |
| Categorical embedding | **Per-feature `nn.Embedding(card, k)`**, k adaptive (`min(embed_size, card//2 + 1)`) — 23 separate embedding layers, gradients flow into each demographic axis | **Pre-computed one-hot** at dataset assembly time (`d_cond` features frozen as input vector) | **HIGH** — frozen one-hot is a major suspect for "decoder ignores conditioning" (H4) |
| Positional encoding | Learnable `nn.Parameter`, length 20000 | Sinusoidal, length 49 | LOW |
| Output heads | Activity (CE, 146 classes) + Location (BCE, binary) + WithNOBODY (BCE, binary) — three independent dense heads off encoder output | Activity (CE, 14) + AT_HOME (BCE) + Copresence (BCE, 9 slots, masked) + optional aux stratum (CE, 3) | MED — Step-4 has more heads but less class diversity |
| Optimizer | Adam | AdamW | LOW |
| LR | Tuned in {1e-3, 8e-4, 6e-4, 4e-4, 2e-4, 9e-5} (Optuna) | **5e-5 hardcoded** | **HIGH** — order-of-magnitude lower than the working baseline |
| Scheduler | `ReduceLROnPlateau(factor=0.95, patience=5)` (reactive) | Linear warmup (2000 steps) → cosine decay to 10% floor (proactive) | MED |
| Batch size | Tuned in {96, 128, 256} | 256 fixed | LOW |
| Max epochs | 150+, no hard cap | 100 | LOW |
| Early-stopping patience | **50 epochs** | 15 epochs | MED — Step-4 may early-stop before convergence |
| Early-stopping metric | Validation activity accuracy | Composite (val_JS + 0.5·AT_HOME gap) | LOW |
| AMP / mixed precision | No (fp32) | No (fp32, after F4 fp16 collapse) | LOW (matches) |
| Gradient clipping | `max_norm=25` (loose) | `max_norm=1.0` (tight) | LOW |
| Loss weighting | **Equal 1:1:1**, normalized per batch (`λ /= Σλ`) | Tuned static lambdas (1.0 / 0.5 / 0.3 / 0.1 / 0.1) | MED |
| Scheduled sampling | None (encoder-only doesn't need it) | `SCHED_SAMPLE_P=0.2` (G2/G3) — known Spouse-regression mechanism | **HIGH** — only exists because of the autoregressive decoder |
| Label smoothing | None | `HOME_LABEL_SMOOTH=0.05` (G2/G3) | LOW |
| Class-imbalance handling | None — model handles it organically | Inverse-sqrt-frequency activity weights + manual boosts (Work +5.0, Transit +3.0, Social +2.0) | MED — hand-tuning is a known F-series over-fit risk |
| Cluster | Single GPU, 3-day wall-clock, conda env, NVML disabled | Single GPU, 2-day wall-clock, array-driven multi-stage chain, env-var plumbing | LOW (matches) |

**Three deltas flagged HIGH:** encoder-only vs. enc-dec, conditioning mechanism (concat + per-feature embeddings vs. cross-attn over frozen one-hot), and d_ff width. Two more flagged HIGH for being symptoms of the encoder-decoder choice: scheduled sampling and the LR-magnitude gap.

---

## 2. Architectural philosophy: what the prior paper got right

### 2.1 Encoder-only beats encoder-decoder for fixed-length 24-hour prediction

The prior paper consumes a 24-timestep input window and emits the full 24-step output sequence in **one forward pass** from a transformer encoder. There is no teacher forcing, no autoregressive decoder, no BOS token, no causal mask, no slot-by-slot generation chain. The model treats occupancy prediction as a sequence-to-sequence-of-the-same-length problem and lets the encoder's self-attention handle all temporal coupling in parallel.

Step-4's encoder-decoder formulation is what *creates* the H3 problem (autoregressive feedback amplification — predicted slot t feeds back into slot t+1 input, locking AT_HOME into "stuck-at-home" attractors). G2's `SCHED_SAMPLE_P=0.2` was the band-aid: zero out 20% of AT_HOME slots in the decoder input to break the chain. Spouse co-presence — which is conditional on AT_HOME (you can only be with your spouse if you're home) — paid the price: zeroing AT_HOME slots zeros the Spouse gradient signal, and the Spouse error regressed from +0.95 pp (G1) to +15.39 pp (G2).

**Remove the decoder, remove the problem class.** No autoregressive chain, no need for scheduled sampling, no Spouse gradient corruption. The fix is structural, not a tunable.

### 2.2 Concatenation conditioning beat the FiLM/cross-attn arc

The F-series and G-series have spent five iterations refining the conditioning mechanism: F-series FiLM modulation → F8 aux-stratum head → G3 cross-attention over three semantic tokens `[demo, cycle, strata]`. Each step added complexity and learnable parameters; the gate landscape moved laterally (one gate closes, another opens) rather than monotonically.

The prior paper does the simplest possible thing: **concatenate** the 23 categorical demographic embeddings + the cyclical time encoding + the 4 continuous features into a single input vector at the encoder's first layer. No FiLM gating, no cross-attention over separate conditioning tokens, no auxiliary heads. The encoder's self-attention learns to weigh demographic vs. temporal signals through the standard Q/K/V mechanism over the full input.

This worked on a *harder* prediction problem: **146 activity classes** (vs. Step-4's 14) and **23 demographic features** (vs. Step-4's ~12). If concat-conditioning was sufficient there, it is at least worth treating as a baseline competitor here — not the architectural ceiling we already crossed and rejected.

### 2.3 Massive d_ff with shallow depth

Prior paper: 2 encoder layers with `d_ff` tuned in `{7168, 8192, 9216, 10240}`. Step-4: 6 encoder + 6 decoder layers with `d_ff` = 1024 (G2 baseline) or 1536 (G3, raised proportionally with d_model).

The per-layer feed-forward width is **5–10× larger** in the working pipeline. This is the standard "wide and shallow" trade in transformers: representational capacity per token is concentrated in the FFN block, not in attention depth. The Spouse channel is a *conditional* signal — Spouse depends on AT_HOME, which depends on activity, which depends on demographics. Joint distributions of conditional signals tend to want **width** (more nonlinear features per token) rather than **depth** (more sequential refinement).

Step-4 has invested in depth (12 layers total) and capped width. The prior paper's evidence is that this trade-off can run the other way without loss.

---

## 3. H-series candidates

Each candidate is a single-axis tag-edit, scoped to one or two source files, with explicit compatibility against the live G3 path. Diff-bundling is forbidden (F4 lesson); submission-bundling is allowed for independent tags via the existing array machinery.

### H1 — Encoder-only rewrite

- **Hypothesis.** H3 (autoregressive feedback amplification) and the Spouse-from-AT_HOME-zeroing regression are both symptoms of the encoder-decoder formulation. Encoder-only outputs all 48 slots in one pass; no chain to corrupt.
- **Scope.** New `EncoderOnlyOccupancyModel` in `04B_model.py` — replace decoder with a second 6-layer encoder block followed by per-slot output heads (activity / AT_HOME / copresence). `04D_train.py` drops scheduled-sampling and label-smoothing plumbing. Configs: new `H1.yaml` deriving from G1 (proportional sampling stays; G2 knobs are no-ops in encoder-only).
- **Effort.** L. Touches the model class top to bottom and the training loop's teacher-forcing path.
- **Expected gate impact.** Composite improves (no decoder noise floor); AT_HOME tractable; Spouse recovers vs. G2 (no slot-zeroing). Second-order risk: copresence may over-predict because there's no autoregressive smoothing — would surface in act_JS or a new failure mode.
- **Pre-flight check.** Throws out G3's cross-attention parameter investment. Do NOT run if G3 closes 3/4 gates — defer in favour of incremental G-fixes. Run if G3 closes ≤1/4 gates.

### H2 — Per-feature categorical embeddings

- **Hypothesis.** H4 (decoder ignores conditioning) is partly an embedding-side problem: the current pre-computed one-hot demographic vector has no learnable representation, so gradients into individual demographic axes are saturated/blocked. Per-feature `nn.Embedding(card, k)` gives gradients into each axis.
- **Scope.** `04A_data.py` (or whichever module assembles the dataset) — stop one-hot encoding categorical demographics at dataset-assembly time; keep them as integer codes. `04B_model.py` — add a `ModuleList` of `nn.Embedding` layers, one per categorical column, concatenate outputs, project to d_model. Configs: new `H2.yaml` flag.
- **Effort.** M. Two-file edit; data-pipeline change is the riskier half (validate train/val/test integer codes match across cycles).
- **Expected gate impact.** Cross-cuts all four gates by giving the conditioning signal a learnable representation. Most likely to move composite and Spouse (Spouse is the most demographics-conditional output).
- **Pre-flight check.** Compatible with both H1 (encoder-only) and the live G3 cross-attn path. Could even ship as a G4 modification on top of G3 if G3 closes 2–3 gates.

### H3 — Wider d_ff at lower depth

- **Hypothesis.** The prior paper's d_ff was 5–10× wider than Step-4's. Joint Spouse–AT_HOME–activity prediction is a width problem more than a depth problem.
- **Scope.** Sweep `(n_layers, d_ff)` in `{(2, 8192), (3, 4096), (4, 2048)}` at d_model=256. Configs: `configs/sweep_H3.yaml`. Requires the deferred `--d_ff` argparse edit to `04D_train.py` plus `D_FF` mapping in `config_to_env.{sh,py}` — currently `d_ff = d_model × 4` is hard-coded.
- **Effort.** S after the `--d_ff` plumbing lands (a one-evening edit; flagged in `step4_training_v2.md` as deferred).
- **Expected gate impact.** Most likely to move composite and act_JS (FFN width is where activity-class discrimination capacity lives). Less likely to move Spouse, which is more conditioning-driven than capacity-driven.
- **Pre-flight check.** Compatible with both H1 (encoder-only at wider d_ff) and G3 (cross-attn decoder at wider d_ff). Cheapest "more capacity" experiment available.

### H4 — Equal loss weights with per-batch normalization

- **Hypothesis.** Hand-tuned `(λ_act, λ_home, λ_cop, λ_marg)` weights have over-fit the F-series gate landscape. The prior paper used equal 1:1:1 weights and let the model handle it.
- **Scope.** `04D_train.py` only — set all lambdas to 1.0, normalize per batch (`λ /= Σλ`). Config: `H4.yaml` with `lambda_act=lambda_home=lambda_cop=lambda_marg=1.0`.
- **Effort.** S. Single-file, single-block edit. Can be a no-code config-only change if the training loop already reads lambdas from config.
- **Expected gate impact.** Cheap diagnostic. Either gates improve (current weighting was the bottleneck) or they don't (weighting wasn't the issue). Either result is informative.
- **Pre-flight check.** Compatible with everything. Run as a G3-comparison sanity ablation regardless of where H1/H2/H3 land.

### H5 — Higher LR + ReduceLROnPlateau

- **Hypothesis.** Step-4's LR (5e-5) is an order of magnitude below the prior paper's tuned range (1e-3 to 9e-5). Possible under-training; warmup-cosine schedule may be over-smoothed.
- **Scope.** Sweep `lr ∈ {1e-4, 4e-4, 8e-4}` with `ReduceLROnPlateau(factor=0.95, patience=5)` replacing the current schedule. Patience increased to 50. Files: `04D_train.py`, configs `H5*.yaml`.
- **Effort.** S. One scheduler swap + a 3-arm config sweep.
- **Expected gate impact.** Most likely to move composite (under-trained models leave composite high). Could surface fp32 instability at higher LR — keep gradient clipping at 1.0.
- **Pre-flight check.** Compatible with everything. Best run after H4 (decouple LR effect from loss-weight effect).

### H6 — Drop activity-class boosts and inverse-sqrt-frequency weighting

- **Hypothesis.** Hand-calibrated activity weights (Work +5.0, Transit +3.0, Social +2.0; inverse-sqrt-frequency on the rest) have entrenched a bias pattern the gates penalize. The prior paper used no class weighting and handled 146 classes successfully.
- **Scope.** `04D_train.py` — drop the `activity_boosts` block; set CrossEntropy weights to None. Config: `H6.yaml` with `activity_boosts=0`.
- **Effort.** S. Single-block deletion + config flag.
- **Expected gate impact.** Most likely to move act_JS (directly) and AT_HOME (indirectly, since stuck-at-home rates correlate with which activities the model favours). Cheap diagnostic.
- **Pre-flight check.** Compatible with everything.

---

## 4. Recommendation

**Three execution tiers.** All H-series experiments are independent of G3; the H-series is a parallel architectural fork, not a replacement for the G3 evaluation.

### Tier 1 — Cheap parallel ablations (run alongside G3 evaluation, on free `pg` slots)

1. **H4** (equal loss weights) — single config edit, results in <24h.
2. **H6** (drop activity boosts) — single config edit, results in <24h.
3. **H5** (LR sweep, single arm at 4e-4) — config edit + scheduler swap, results in ~24–36h.

Each produces a `results.csv` row that can be compared directly against the G3 row. Total cost: ~3 pg slots over ~3 days. If any of these closes more gates than G3, that's a meaningful signal that the F-series weight-tuning regime was over-fit.

### Tier 2 — Medium-effort architectural fork (run only if G3 closes ≤2/4 gates)

4. **H2** (per-feature categorical embeddings) on top of whichever path is least bad after G3 evaluation (G3 cross-attn or H1 encoder-only). This is the highest-impact / medium-effort move; gives the conditioning signal a learnable representation regardless of the architecture surrounding it.

### Tier 3 — High-effort structural rewrite (the reserve shot)

5. **H1** (encoder-only) — the prior paper's architecture, ported. Justified only if G3 + Tier 1 + H2 still leave gates open. Frame in the spec doc as "the prior paper's architecture, ported to GSS" — the credibility argument is that this exact approach worked on a harder problem in the same lab.
6. **H3** (wider d_ff, lower depth) — pairs with H1; once the encoder-only model class exists, the wide/shallow sweep is a config-only follow-up.

**G3 remains the next gate-decision.** When G3 lands its `results.csv` row, evaluate against the four hard gates. The H-series tier-1 ablations should already be in flight by then; the H-series tier-2/3 decisions are gated on the G3 result.

---

## 5. Risks and what this proposal does not claim

- **Domain transfer is not free.** The prior paper used 5-min resolution time-use sequences with 146 activity classes and 23 demographic features, evaluated on forecast accuracy. Step-4 uses 30-min × 48 slots, 14 activity classes, ~12 demographic features, evaluated on a four-gate composite. The prior architecture worked *there*; it is a hypothesis here, not a guarantee.
- **Evaluation criteria differ.** The prior paper optimized validation activity accuracy. Step-4 has hard gates that include AT_HOME and Spouse marginal-error constraints. An encoder-only model could close composite + act_JS but reveal new failure modes on AT_HOME or copresence (e.g., over-prediction from no autoregressive smoothing).
- **H1 discards G3's parameter investment.** Cross-attention over `[demo, cycle, strata]` is a custom architectural piece that took a planning round + a smoke debug cycle to land. If G3 closes 3/4 gates, H1 should be deferred — never throw away a near-pass for a hypothesis.
- **The prior paper's Optuna sweep was over a much wider hyperparameter space** than any single H-series tag would replicate. The H-series candidates here are individual hypothesis tests, not a full re-tuning.

---

## STATUS

`PROPOSED — 2026-05-01`. Manager-tier doc. Awaiting user direction on whether to:
- (a) Open a follow-up planning round to advance Tier-1 candidates (H4, H5, H6) as parallel ablations alongside G3 evaluation, or
- (b) Wait for G3's `results.csv` row, then decide based on which gates remain open, or
- (c) Shelve the proposal and continue with G3 evaluation alone.

The doc stands either way as the architectural-comparison record between the working prior-paper Transformer and the current Step-4 G-series stack.
