# J-4 Task List — J-4.1 / J-4.2 / J-4.3 parallel precision ladder beyond J3

This file is the buildable spec that turns the **J-4 Blueprint** (`investigations/J-4 Blueprint.md`) into three single-axis architecture arms, **all branching from the frozen J3 baseline and all running simultaneously on the cluster** — the same parallel-ladder pattern used for J2 / J2.5 / J3. Each arm tests one of the Blueprint's three hypotheses in isolation.

It is **not** a debate of whether J-4.x is worth running. The investigation v2 doc (`investigations/investigation_Training_setp4v2.md`) recommended Step-4 closeout after J3; the user has decided to push for absolute precision regardless. This task list reflects that decision.

---

## §0. Context

**Status as of 2026-05-07.** J3 (Hybrid AR-Encoder + Soft Activity Embedding) is the production Step-4 checkpoint, passing all four hard gates: composite=0.6355 ✅, AT_HOME RMS=4.57 pp ✅ (margin +0.73), Spouse=−2.03 pp ✅, act_JS=0.0191 ✅. Two residuals remain that are not blocked by hard gates but are the focus of J-4.x:

- Per-stratum AT_HOME RMS still above 4 pp (margin small; J-4.1 targets this).
- Alone-channel cop_max_gap on 2005_1 (+21.1 pp) and 2010_1 (+17.1 pp), structurally caused by the missing `colleagues` column in those cycles. J-4.2 attempts a model-side fix via hierarchical conditioning; J-4.3 attempts a loss-side fix via PINN logic loss. The data-side alternative is K-cop-A (v2 §7).

**Linked documents.**
- Hypothesis-level proposal: `investigations/J-4 Blueprint.md` (drafted 2026-05-07 with a separate LLM).
- Closure rationale for J3: `investigations/investigation_Training_setp4v2.md`.
- Running progress log: `step4_training_v3.md` — every completed J-4.x leg appends a Progress Log row there using the same format as J1 / J2 / J2.5 / J3.
- Style precedent for parallel-ladder task blocks: `step4_training_v3.md` §"J2 / J2.5 / J3 — Parallel AT_HOME ladder."

---

## §1. Codebase anchors (cheat-sheet for the J3 baseline)

Sonnet should treat these as the authoritative pointers; do not re-grep before editing.

| Anchor | File | Class / Function | Lines |
|---|---|---|---|
| J3 model class | `Speed_Cluster/04B_model.py` | `JSeriesHybrid` | 787–899 |
| Arm-2 fusion (concat → arm2_proj) | `Speed_Cluster/04B_model.py` | `JSeriesHybrid._arm2_fuse()` | 995–1024 |
| `arm2_act_proj` (J3 dim-balance) | `Speed_Cluster/04B_model.py` | `JSeriesHybrid.__init__()` | 875–880 |
| `home_head` (Linear→Tanh→Linear(1)) | `Speed_Cluster/04B_model.py` | `JSeriesHybrid.__init__()` | 885–893 |
| `cop_head` (Linear→Tanh→Linear(9)) | `Speed_Cluster/04B_model.py` | `JSeriesHybrid.__init__()` | 895–897 |
| `forward()` (returns dict) | `Speed_Cluster/04B_model.py` | `JSeriesHybrid.forward()` | 1028–1050 |
| `generate()` (inference loop) | `Speed_Cluster/04B_model.py` | `JSeriesHybrid.generate()` | 1052–1084 |
| Loss assembly | `Speed_Cluster/04D_train.py` | `compute_loss()` | 120–239 (formula 224–230) |
| Lambda env-var defaults | `Speed_Cluster/04D_train.py` | module-level | 51–56 |
| H_Time learnable PE + cyclical-time precedent | `Speed_Cluster/archive/04B_model_H_Time.py` | `ConditionalTransformer` | 188–196, 318–320, 428–430 |

**Three structural notes that change how the Blueprint reads against the actual code.**

1. **There is no `arm2_refiner` in J3.** The Blueprint's "fused_seq → arm2_refiner → heads" assumes a non-causal refinement layer that the J3 production code does not have. Current path is `_arm2_fuse()` → heads directly. J-4.1 therefore injects `tod_emb + dow_emb` directly into the fused tensor right before the heads — no refiner is added.
2. **DDAY_STRATA enters Arm-2 only as a one-hot broadcast** in `_arm2_fuse()` (lines 1007–1013), not as an embedding. J-4.1's `dow_emb` is **additive on top of** the existing one-hot — the one-hot is *not* removed.
3. **H_Time precedent for J-4.1 exists but is not directly portable.** `archive/04B_model_H_Time.py` implements learnable PE `(1, 48, d_model)` and cyclical sin/cos time features, but on a different base class (`ConditionalTransformer`, not `JSeriesHybrid`). The pattern is validated; J-4.1 re-implements it inside `JSeriesHybrid._arm2_fuse()`.

**Lambda-block sanity check.** Before editing, Sonnet **must read the actual J3 config file** to confirm the lambda values it uses (sources disagree on whether J3 uses λ_home=0.7 or 0.9). All three J-4.x arms must inherit J3's lambda block byte-for-byte (single-axis discipline); do not assert from memory.

---

## §2. Parallel-ladder discipline

The three legs run as a **parallel ladder, all forked from frozen J3** — the same execution shape used for the J2 / J2.5 / J3 cycle. Three rules govern this:

- **Single-axis-vs-J3 rule.** Each arm changes exactly one thing relative to J3. **None** of the three arms layers on top of another. J-4.2 does **not** include J-4.1's temporal injection; J-4.3 does **not** include J-4.2's hierarchical heads. This produces three independent attribution signals — exactly the structure that let us identify `arm2_act_proj` as the load-bearing fix in the J2 / J2.5 / J3 ladder. Stacked combinations (e.g. J-4.1+4.2) are out of scope here and are deferred to a possible follow-up J-4-stack arm only if multiple individual arms pass.
- **Hard-gate non-regression rule.** The four passing gates from J3 are the floor: composite < 1.045, AT_HOME RMS ≤ 5.3 pp, |Spouse| ≤ 5 pp, act_JS ≤ 0.05. Any arm that breaks one of these is excluded from the ship-candidate pool, regardless of how well it improved its target metric. Each arm is evaluated independently against this floor (no rollback chain — there is no chain).
- **Pre-build archive rule** (memory `feedback_archive_predecessor`). The frozen J3 baseline is archived **once**: copy `04B_model.py` → `archive/04B_model_J3.py` and `04D_train.py` → `archive/04D_train_J3.py` before the first J-4.x edit. All three arms fork from these frozen copies. Three-arm parallel cycle = one archive event, not three.

**Cluster execution shape.** Submit three sbatch jobs simultaneously to the `pg` partition (separate output dirs `outputs_step4_J4_1/`, `outputs_step4_J4_2/`, `outputs_step4_J4_3/`; identical seed and train/val split). Wall time ~17 h (parallel) instead of ~51 h (serial). After all three eval jobs complete, compare diagnostics and apply the advancement rule in §6.

**Task-doc convention.** Each leg below uses the CLAUDE.md task format (aim / single-axis delta / spec / training touchpoints / config / pre-build hygiene / expected gate movement / pass criterion / risk / cluster cost). After each cluster cycle, the leg's row is appended to `step4_training_v3.md` Progress Log.

---

## §3. Task J-4.1 — Explicit Temporal Context Injection

### Aim

Tighten per-stratum AT_HOME variance further than J3's 4.57 pp by giving Arm 2 explicit absolute time-of-day and day-of-week anchors. Blueprint hypothesis: J3's positional encoding from the trunk is diluted by the time it reaches Arm 2's fused tensor; activity context alone cannot disambiguate "Sleep at 2 AM" from "Sleep at 2 PM" with respect to AT_HOME probability.

### Single-axis delta vs J3

Two `nn.Embedding` modules + two add-into-fused-tensor lines. **Nothing else changes**: same loss, same lambdas, same heads, same Arm 1, same `arm2_act_proj`, same training schedule, same epochs, same seed, same lr, same warmup.

### Architecture spec

In **`Speed_Cluster/04B_model.py`** (relative to frozen J3):

- `JSeriesHybrid.__init__()` — alongside `arm2_act_proj` (lines 875–880), add:
  - `self.tod_emb = nn.Embedding(48, d_model)` — slot index 0..47.
  - `self.dow_emb = nn.Embedding(3, d_model)` — DDAY_STRATA mapped to {0,1,2} for {Weekday, Saturday, Sunday}.
  - Initialize both with `nn.init.normal_(weight, std=0.02)` to match the trunk's existing embedding init style.
  - Gate behind `enable_temporal_injection: bool = False` constructor flag so J1/J2/J2.5/J3 instances are byte-for-byte unaffected.
- `JSeriesHybrid._arm2_fuse()` (lines 995–1024) — after the existing concat + `arm2_proj` produces `fused_seq` of shape `(B, 48, d_model)`, conditionally add:
  - `slot_idx = torch.arange(48, device=fused_seq.device).unsqueeze(0).expand(B, -1)` — shape `(B, 48)`.
  - `dow_idx = strata_long.unsqueeze(-1).expand(-1, 48)` — shape `(B, 48)`. `strata_long` is the existing tensor of values 0/1/2 derived from DDAY_STRATA already used in the one-hot broadcast at lines 1007–1013.
  - `fused_seq = fused_seq + self.tod_emb(slot_idx) + self.dow_emb(dow_idx)`.
- The existing one-hot DDAY_STRATA broadcast (lines 1007–1013) is **kept in place**; both signals reach Arm 2.
- `forward()` (1028–1050) and `generate()` (1052–1084) need **no edits**.

### Training touchpoints

None. `04D_train.py compute_loss()` is unchanged. New parameter count: `48 × 384 + 3 × 384 ≈ 19,584` — a rounding error against J3's 29.25M trainable parameters.

### Config

- New file `Speed_Cluster/configs/J4_1.yaml` (and `sweep_smoke_J4_1.yaml`). Inherits from `J3.yaml` byte-for-byte (lambdas, lr, scheduler, epochs, dropout, seed). Sonnet must read the actual J3.yaml first and copy it.
- Single new flag: `enable_temporal_injection: true`. Default in code is `false`.
- `model_type: J4_1` for `04D_train.py` / `04E_inference.py` dispatch.

### Pre-build hygiene

Single archive event (shared with J-4.2 / J-4.3):

```
cp Speed_Cluster/04B_model.py Speed_Cluster/archive/04B_model_J3.py
cp Speed_Cluster/04D_train.py Speed_Cluster/archive/04D_train_J3.py
```

### Expected gate movement

- **AT_HOME RMS:** 4.57 pp → ~3.5–4.0 pp expected (per-cell variance reduction in the morning slot 0–10 region).
- **Spouse, act_JS, cop_max_gap:** unchanged ±noise.
- **Composite:** modest improvement.

### Pass criterion (J-4.1 ships if)

ALL of:
- All four hard gates still pass.
- AT_HOME RMS ≤ 4.57 pp (no regression vs J3) AND ∆AT_HOME RMS ≥ 0.5 pp improvement.

### Risk

Low. Two small embeddings, no path through the loss function. Worst case: zero net effect — gate stays at 4.57 pp and J-4.1 fails its pass criterion (∆ < 0.5 pp) without breaking anything.

### Cluster cost

~17 h end-to-end (full 04D train + 04E inference + 04J diagnostics + 04F validation). Same wall-time as J1/J2/J2.5/J3.

---

## §4. Task J-4.2 — Hierarchical State Dependency (home → cop)

### Aim

Reduce per-channel cop residuals — primarily the Spouse |gap| and the Alone +21 pp / +17 pp blow-out on 2005_1 / 2010_1 — by letting the cop head condition on the home prediction the model already makes. Blueprint hypothesis: P(colleagues | home=1) ≈ 0; P(spouse | home=1) >> P(spouse | home=0); the parallel head structure inherited from J3 cannot exploit these couplings without explicit hookup.

### Single-axis delta vs J3

Re-order Arm 2's head computation so cop reads `cat([fused_seq, sigmoid(home_logits).detach()], dim=-1)` instead of `fused_seq` alone. The detach is mandatory — it isolates the cop-BCE gradient from the home head, mirroring the existing Arm-1 ↔ Arm-2 detach pattern. **Nothing else changes**: no temporal injection (that's J-4.1's axis), all lambdas unchanged, no loss-function change.

### Architecture spec

In **`Speed_Cluster/04B_model.py`** (relative to frozen J3):

- `JSeriesHybrid.__init__()` — when `model_type == "J4_2"`, change `cop_head` input dim from `d_model` to `d_model + 1`. New shape: `Linear(d_model + 1) → Tanh → Linear(9)`. (Alternative considered: a small `cop_proj = Linear(d_model + 1, d_model)` + the existing head — Blueprint-faithful but adds a layer. Recommend the simpler input-dim widen first.) Gate behind `enable_hierarchical_cop: bool = False` constructor flag.
- `JSeriesHybrid.forward()` (lines 1028–1050) — when `enable_hierarchical_cop` is true, re-order:
  1. `home_logits = self.home_head(fused_seq)`.
  2. `home_probs = torch.sigmoid(home_logits).detach()` — `detach()` is critical.
  3. `cop_input = torch.cat([fused_seq, home_probs], dim=-1)`.
  4. `cop_logits = self.cop_head(cop_input)`.
  5. Returned dict shape unchanged: `{"act_logits", "home_logits", "cop_logits", "aux_logits"}`.
- `JSeriesHybrid.generate()` (lines 1052–1084) — identical reorder under the same flag. The safety mask already in `generate()` is re-applied unchanged at the end of the function.
- When the flag is false, behavior is byte-for-byte J3.

### Training touchpoints

None. The detach guarantees gradient isolation; `04D_train.py compute_loss()` does not see the change.

### Config

- New file `Speed_Cluster/configs/J4_2.yaml` (and `sweep_smoke_J4_2.yaml`). Inherits from `J3.yaml` directly (NOT from J4_1.yaml — these are parallel arms).
- New flag: `enable_hierarchical_cop: true`. `enable_temporal_injection` is **NOT** set (J-4.2 does not include J-4.1's axis).
- `model_type: J4_2` for dispatch.

### Pre-build hygiene

Shared with J-4.1 — one archive event covers all three arms.

### Expected gate movement

- **Spouse:** −2.03 pp → likely closer to 0 pp (channel benefits most from explicit P(spouse | home=1) lift).
- **Alone cop_max_gap on 2005_1 / 2010_1:** partial improvement, ~30–50% reduction (the *structural* `colleagues=NaN` cause is not removed by this leg).
- **AT_HOME, act_JS:** unchanged ±noise.
- **Composite:** minor improvement.

### Pass criterion (J-4.2 ships if)

ALL of:
- All four hard gates still pass.
- |Spouse| ≤ 2.03 pp (no regression vs J3) AND cop_max_gap ≤ J3's value.

### Risk

Medium. Hierarchical conditioning can destabilize training if `home_logits` saturate early (cop sees a near-constant input → degenerate cop predictions). **Mitigation:** monitor `val_score` and `home_loss` in epochs 1–10. If `home_loss` collapses below 0.30 before epoch 10 (vs J3's plateau of ~0.35), abort and add a warmup that ramps the conditioning from 0 to 1 over epochs 1–10 (mix `cat([fused_seq, alpha * home_probs])` with `alpha = min(1, epoch/10)`).

### Cluster cost

~17 h (parallel with J-4.1 and J-4.3).

---

## §5. Task J-4.3 — Differentiable Logic Loss (PINN)

### Aim

Force mutual-exclusivity between Alone and the 8 non-Alone cop channels at training time, so the network learns the rule "if Alone=1 then all others ≈ 0" in its weights — eliminating the need for any post-hoc Step-4.5 cleanup script and addressing the structural 2005/2010 Alone asymmetry from the loss side instead of the data side. This is the Step-4-internal alternative to v2 §7's K-cop-A.

### Single-axis delta vs J3

Add one term to `04D_train.py compute_loss()`. **No model changes** at all — `04B_model.py` is untouched (frozen J3 binary). No temporal injection, no hierarchical heads.

### Loss spec

In **`Speed_Cluster/04D_train.py compute_loss()`** (lines 120–239):

- Just after `cop_logits = output["cop_logits"]` (line 138): compute `cop_probs = torch.sigmoid(cop_logits)` — shape `(B, 48, 9)`.
- Identify `alone_idx` from the cop-channel ordering in the dataset (verify against the channel names used in `diagnostics_J_J3.json`; **do not hardcode index 0 without checking**).
- `p_alone = cop_probs[..., alone_idx]` — shape `(B, 48)`.
- `p_others = cop_probs.sum(dim=-1) - p_alone` — shape `(B, 48)`.
- `loss_logic = (p_alone * p_others).mean()`.
- In the loss-formula block (lines 224–230), add `+ LAMBDA_LOGIC * loss_logic`.
- Add a new env-var read in the module-level lambda block (lines 51–56): `LAMBDA_LOGIC = float(os.getenv("LAMBDA_LOGIC", "0.0"))`. Default 0.0 keeps J1/J2/J2.5/J3 unaffected.

### Architecture touchpoints

None. Frozen J3 `04B_model.py`. Dispatch in `04D_train.py` / `04E_inference.py` sees `model_type: J4_3` but routes to the same `JSeriesHybrid` build as J3 — no model-side branching.

### Config

- New file `Speed_Cluster/configs/J4_3.yaml` (and `sweep_smoke_J4_3.yaml`). Inherits from `J3.yaml` directly.
- Adds `LAMBDA_LOGIC: 0.1` (Blueprint default; tunable downward to 0.05 / 0.01 if degenerate behavior appears).
- `model_type: J4_3` for dispatch (model build identical to J3; the dispatch label distinguishes output dirs / config selection only).

### Pre-build hygiene

Shared with J-4.1 / J-4.2 — one archive event covers all three arms.

### Expected gate movement

- **Alone cop_max_gap on 2005_1 / 2010_1:** drop toward ≤ 3 pp.
- **marg_loss (mass-conservation auxiliary):** may also drop; the logic term is a soft mass-balance prior.
- **AT_HOME, Spouse, act_JS, composite:** unchanged ±noise.

### Pass criterion (J-4.3 ships if)

ALL of:
- All four hard gates still pass.
- Alone cop_max_gap on each of 2005_1 and 2010_1 ≤ J3's value.
- No other cop channel regresses by more than 2 pp.

### Risk

Medium-low. Logic loss with `lambda_logic=0.1` is a soft constraint and cannot dominate the BCE. **Failure mode:** model learns to predict `p_alone ≈ 0.5, p_others_individually ≈ small` everywhere — this would *break* the gates by collapsing per-channel calibration. **Mitigation:** monitor per-channel cop calibration MAE during validation; if any channel's calibration MAE jumps by >5× vs J3, abort and try `LAMBDA_LOGIC=0.05` or `0.01`. Schedule of `LAMBDA_LOGIC` ramping from 0 to 0.1 over epochs 1–20 is a fallback.

### Cluster cost

~17 h (parallel with J-4.1 and J-4.2).

---

## §6. Advancement gate and decision matrix (one decision after all 3 finish)

All three eval jobs complete → compare diagnostics → ship the simplest arm that closes its target metric without breaking any of the four hard gates. Same pattern as J2 / J2.5 / J3.

| Arm | Target metric | Pass condition | If only this one passes |
|---|---|---|---|
| **J-4.1** | AT_HOME RMS ↓ from 4.57 pp | All 4 gates ✅ AND ∆AT_HOME RMS ≥ 0.5 pp improvement | Ship J-4.1 |
| **J-4.2** | Spouse \|gap\| ↓ AND Alone cop_max_gap ↓ | All 4 gates ✅ AND \|Spouse\| ≤ 2.03 pp AND cop_max_gap ≤ J3's | Ship J-4.2 |
| **J-4.3** | Alone cop_max_gap ↓ | All 4 gates ✅ AND Alone gap on 2005_1 / 2010_1 ≤ J3's AND no other cop channel −2 pp | Ship J-4.3 |

**Aggregate decision rule** (after all three eval jobs complete):

- **0 of 3 pass:** ship J3 (current production); document residual axes; consider K-cop-A (v2 §7) for the Alone gap as a data-side fallback.
- **1 of 3 passes:** ship that arm. Document the other two as failed hypotheses.
- **2 or 3 of 3 pass:** ship whichever arm has the lowest composite among the passing arms. The remaining passing arms become candidates for a **follow-up J-4-stack arm** that combines them on a single architecture (e.g. if J-4.1 and J-4.2 both pass, a J-4-stack arm = J3 + temporal injection + hierarchical heads, run as a single sequel cycle). The stack arm is **out of scope for this cycle** — it is a separate decision after the parallel ladder lands.

---

## §7. Out of scope

- Any AT_HOME-targeted change *not* described in the J-4 Blueprint — no new K-arms, no new auxiliary heads, no λ_home retunes.
- **Stacked combinations** (J-4.1 + J-4.2, J-4.1 + J-4.3, J-4.2 + J-4.3, all three) — these are deferred to a possible J-4-stack follow-up cycle conditional on multiple arms passing in §6.
- **K-cop-A** (the data-side Alone-mask cleanup from v2 §7) — fallback if 0 of 3 J-4 arms pass; not built in this task list.
- Step 5 (Census Linkage). Step 5 remains unblocked off the current J3 production checkpoint and proceeds in parallel; J-4.x results retroactively replace J3 in Step 5's input only if a J-4.x arm ships and Step 5 is re-run.
- Modifying H_Tanh / H_Time / I1 / earlier J-arm checkpoints. J-4.x branches off J3 only.
- Re-running J3 itself. J3 numbers stand.
- Bundling λ retunes, new auxiliary heads, or loss-function changes outside of J-4.3 — explicitly forbidden by the single-axis-vs-J3 rule in §2.

---

## References

- J-4 Blueprint (hypothesis-level proposal): `Speed-Cluster_docs/investigations/J-4 Blueprint.md`
- J3 closeout / v2 investigation: `Speed-Cluster_docs/investigations/investigation_Training_setp4v2.md`
- Step-4 training progress log: `Speed-Cluster_docs/step4_training_v3.md`
- J2 / J2.5 / J3 ladder (style precedent for parallel execution): `Speed-Cluster_docs/step4_training_v3.md` §"J2 / J2.5 / J3 — Parallel AT_HOME ladder"
- Architecture / config / loss CSVs: `Speed-Cluster_docs/CSV_records/`
- Frozen architectures: `Speed_Cluster/archive/04B_model_*.py`
- Production J3 model + train: `Speed_Cluster/04B_model.py`, `Speed_Cluster/04D_train.py`
