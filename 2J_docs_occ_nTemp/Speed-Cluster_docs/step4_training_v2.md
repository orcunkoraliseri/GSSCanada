# Step-4 Training v2 — G-series architectural rebuild

> **Supersedes** the F-series (F1 → F10), closed at F10a on 2026-04-28. F-series investigation record: `step4_training.md`. Operations entry-point (cross-cycle log): `../04_augmentationGSS_hpc.md`.

---

## Aim

Break the F-series structural floor (composite 1.306 at F10a, with AT_HOME, act_JS, and cop_cal_MAE gates still failing) by changing the model and training pipeline rather than running another single-axis hyperparameter trial. Three of the four failing gates were diagnosed in the F-series as architectural — autoregressive feedback amplification (H3), conditioning collapse (H4), and target-stratum sampling bias (H1) — not loss-weight tunable.

The five candidate fixes (consolidated from `step4_training.md` §5 and the external proposal in `newArchProposal.md`):

- **A. Cross-attention conditioning** over a `[cond_vec ‖ cycle_emb ‖ strata_oh]` embedding, replacing additive `strata_linear` + FiLM. Targets H4 (decoder ignores conditioning).
- **B. Scheduled sampling / slot-dropout** on the teacher-forced `dec_aux_seq` AT_HOME channel during training (p=0.2 per slot). Targets H3 (autoregressive stuck-at-home).
- **C. Label smoothing** on the home BCE ({0,1} → {0.05, 0.95}) to prevent sigmoid saturation. Targets H3 (sigmoid > 0.70 lock-in).
- **D. Proportional target sampling** in `04C_training_pairs.py` — sample target strata in proportion to the population, not uniformly. Targets H1 (~2.3× weekend over-representation).
- **E. Decoder capacity expansion** — raise `d_model` and `d_ff`. Cited in F10a closure as a structural ceiling.

**Decision: stage the fixes, do not bundle.** F4 demonstrated the failure mode of bundling unrelated changes (FP16 + new loss + new sampling collapsed into "INVALID, can't attribute"). G-series runs each axis or small bundle in isolation, with attribution gates between stages.

**Hard gates (inherited from F-series, evaluated per stage):** composite < 1.045 AND AT_HOME ≤ +5.3 pp AND Spouse ≤ +5 pp AND act_JS ≤ 0.05.

---

## Steps (task list)

### G1 — Proportional target sampling

- **Change scope:** `04C_training_pairs.py` only. No model change. No training-loop change.
- **Targets:** H1 (training-pair target-stratum sampling bias, ~2.3× weekend over-representation).
- **What it does NOT touch:** `04B_model.py`, `04D_train.py`, the F10a YAML config, env-var defaults.
- **Independence check:** running F10a's `configs/F10a.yaml` against the new pairs file with `seed=42` produces a single deterministic delta vs. F10a — only the supervision distribution changes.
- **Rationale:** cheapest, highest-confidence diagnosis. The 2.3× weekend over-representation is the most concrete documented cause of the AT_HOME baseline push. If G1 alone clears AT_HOME ≤ +5.3 pp and act_JS ≤ 0.05, no architectural rewrite is needed.
- **Advancement gate:** all four hard gates pass → ship as Step-4 production. Partial pass (any subset of gates closed but not all) → continue to G2.

### G2 — Training-loop interventions (B + C bundled)

- **Change scope:** `04D_train.py` only. (a) scheduled sampling on `dec_aux_seq` AT_HOME with p=0.2 per slot; (b) label smoothing on home-BCE targets {0,1} → {0.05, 0.95}.
- **Targets:** H3 (autoregressive feedback amplification, sigmoid saturation > 0.70).
- **What it does NOT touch:** model architecture (`04B_model.py`), data pipeline (`04C_training_pairs.py`), loss-weight env vars.
- **Why bundled:** B and C target the same failure mode (H3) via the same mechanism (break the train-inference feedback loop). Either succeeding individually still resolves H3. New env vars `SCHED_SAMPLE_P` and `HOME_LABEL_SMOOTH` (defaults 0.0 → backward-compatible with F-series). Setting both to zero must reproduce G1 behaviour exactly.
- **Advancement gate:** AT_HOME ≤ +5.3 pp (the H3 target). If G2 closes AT_HOME but Spouse / act_JS still fail, conditioning is the residual issue → G3.

### G3 — Cross-attention conditioning + decoder capacity expansion

- **Change scope:** `04B_model.py`. Replace `FiLMTransformerDecoder` with a cross-attention path over `dec_cond = [cond_vec ‖ cycle_emb ‖ strata_oh]`. Raise `d_model` (256 → 384) and `d_ff` (1024 → 1536).
- **Targets:** H4 (decoder ignores conditioning) plus the F10a-cited capacity ceiling.
- **What it does NOT touch:** `04C_training_pairs.py`, `04D_train.py` loss/sampling logic (G1 + G2 stay in effect).
- **Rationale:** F8 isolation showed AUX_STRATUM_HEAD=1 was the only knob that meaningfully moved AT_HOME (+5.3 → +1.41 pp), confirming stronger conditioning is the right axis — but the aux-head route distorts other channels (Spouse +19.4 pp, act_JS regressed). Cross-attention provides the conditioning signal without sharing trunk capacity. Single-GPU first; only escalate to DDP if the `pg` partition cannot fit.
- **Advancement gate:** all four hard gates pass.

---

## Expected result

- **G1:** ~60 % subjective probability of clearing AT_HOME on its own; lower for closing all four gates simultaneously. The `obs_home_rate` shift alone (toward population-weighted ~0.65 from uniform-stratum-weighted ~0.725) directly attacks the diagnosed cause.
- **G2:** independently closes the residual AT_HOME gap if G1 doesn't fully close it, by killing the autoregressive home-state lock-in.
- **G3:** primary mechanism for closing Spouse + act_JS simultaneously, since both are downstream of conditioning collapse (H4).

If all three stages run and the four gates remain unmet, the residual is a data-quality / target-definition issue, not an architecture issue, and Step-4 work pivots to revisiting the schema (e.g., is `obs_home_rate ≈ 0.725` realistic given the `IS_SYNTHETIC=0` AT_HOME column construction).

---

## Test method

1. **G1 reproducibility check.** Bit-identity against F10a is *not* expected (the training pairs change). Instead: `seed=42`, log `obs_home_rate` from the new pairs, confirm it shifts toward population-weighted ~0.65 from uniform-stratum-weighted ~0.725.
2. **Per-stage attribution.** Each stage produces its own `diagnostics_v4_statistical.json` under `outputs_step4_G{1,2,3}/`. Comparison row appended to `results_index/results.csv` via the existing `extract_metrics.py`. Side-by-side audit against F1, F8, F10a in the same CSV.
3. **Backward-compat.** Default env vars must reproduce F10a. `SCHED_SAMPLE_P=0`, `HOME_LABEL_SMOOTH=0`, and the unchanged `04C` output file must yield F10a's `step4_training_log.csv` byte-for-byte (modulo float noise).
4. **No bundling.** If G1 fails, do not jump to G3 with G1 still active. Decide G2 vs G3 from the residual gate pattern, not from impatience.
5. **Smoke first on every stage.** Use the existing `configs/sweep_smoke.yaml` pattern — 1 epoch, single GPU, ~5 min — before burning a full `pg` slot. The orchestration refactor validated this end-to-end.

---

## Status

`PLANNED — 2026-04-28`. Architectural diagnosis from `newArchProposal.md` accepted; F11 framing rejected in favour of staged G-series. G1 task spec to be drafted in a separate planning round.

---

## Progress Log

| Date | Note | Status |
|---|---|---|
| 2026-04-28 | **v2 doc opened.** F-series closed at F10a (composite 1.306, three of four hard gates failing structurally — AT_HOME 6.98 pp, act_JS 0.069, cop_cal_MAE outside target). External architectural proposal (`newArchProposal.md`) reviewed: diagnosis aligns with F-series H1/H3/H4 hypotheses; "F11 single trial" framing rejected because the proposal bundles five independent changes (cross-attention, scheduled sampling, label smoothing, proportional sampling, decoder capacity) — same anti-pattern that produced F4 INVALID. Adopted staged G1/G2/G3 plan: data-pipeline (proportional sampling) → training-loop (scheduled sampling + label smoothing bundled, both target H3) → architecture (cross-attention + capacity). Per-stage gates inherited from F-series hard gates. F10a is the comparison baseline. G1 task spec to be drafted next. | PLANNED |
| 2026-04-28 | **G1 implemented.** `04C_training_pairs.py`: added `--proportional` flag; per-source pair rows replicated by integer-rounded pop_freq ratio (WD src → Sat:1,Sun:1 unchanged; Sat src → WD:5,Sun:1; Sun src → WD:5,Sat:1; computed from actual strata counts {WD:31947,Sat:6175,Sun:6721}). Effective target-strata distribution as seen by 04D's source-stratum-equalized `WeightedRandomSampler` ≈ **55.6% WD / 22.2% Sat / 22.2% Sun** (vs uniform 33/33/33). Structural ceiling: WD-sourced respondents (71% of population) can't target WD, so true 71/14/15 proportional is unreachable under this scheme — 55.6 is the asymptote of integer replication + inverse-source-stratum sampling, and matches the diagnosed direction of fix. Expected obs_home_rate shift: ~0.725 → ~0.70 (toward pop-weighted ~0.65), confirmed at runtime by `--proportional` log line. Val pairs replicated under the same scheme. Output: `outputs_step4_G1/training_pairs.pt` (141,270 rows vs 89,686 baseline). Added `--output_dir` arg. Added `configs/G1.yaml` (F10a base + `data_dir: outputs_step4_G1`). Diff scope: `04C_training_pairs.py` + `configs/G1.yaml` only. | IMPLEMENTED — pending smoke |
| 2026-04-28 | **04C smoke PASS (job 906102); 04D smoke INVALID (job 906104).** 04C pair generation confirmed correct: 141,270 pairs, target-strata counts {WD:64480, Sat:38668, Sun:38122}, matching the expected replication scheme exactly. **Two findings from 04C output:** (1) `obs_home_rate = 0.7346` — moved UP from baseline 0.725, not down as expected. Back-calculation from the two equations (F10a 14.4%/85.6% WD/wkend split at 0.725; G1 45.6%/54.4% at 0.7346) gives R_WD ≈ 0.75, R_wkend ≈ 0.72 — WD-target diaries carry ~3 pp *higher* AT_HOME than weekend-target diaries in this dataset, contradicting the H1 assumption that weekend over-representation was pushing AT_HOME up. The sampler-weighted effective training obs_home_rate shifts from ~0.730 (F10a) to ~0.738 (G1), a +0.8 pp move in the *wrong* direction. (2) The `--proportional` log label "weighted: {1: 0.456, ...}" is the raw pair proportion, not the sampler-weighted effective distribution; 04D recomputes strata_inv_freq from replicated pair counts (line 484), so the effective distribution is correctly 55.6/22.2/22.2 as documented. **04D smoke INVALID:** sbatch --wrap command omitted the YAML-loading path; job ran with AUX_STRATUM_HEAD=False + SPOUSE_NEG_WEIGHT=1.0 (F1-baseline config, not F10a). Results discarded. **Fix:** added `configs/sweep_G1.yaml` (single-tag sweep driver) so the array machinery (`submit_step4_array.sh` → `job_04D_train_array.sh` → `config_to_env.sh`) correctly loads G1.yaml env vars (AUX_STRATUM_HEAD=1, SPOUSE_NEG_WEIGHT=0.45) and PY_ARGS. Symlinks (step4_train.pt, step4_val.pt, step4_feature_config.json) already exist in outputs_step4_G1/ from job 906104. **Low probability of closing AT_HOME gate** based on obs_home_rate direction — H3 (autoregressive feedback) more likely root cause. Proceeding with full G1 run as comparison data point; G2 prep should begin in parallel. | RESUBMIT PENDING |
| 2026-04-28 | **G1 proper training submitted (chain G1_20260428).** Array machinery used (`submit_step4_array.sh configs/sweep_G1.yaml`) — correctly loads `configs/G1.yaml` via `config_to_env.sh` → `AUX_STRATUM_HEAD=1`, `SPOUSE_NEG_WEIGHT=0.45`, all F10a-inherited env vars. Job chain: 04D 906116 (pg, 2-day wall) → 04E 906117 (afterok:906116_0) → {04F 906118, 04H 906119, 04I 906120, 04J 906121} → extract_metrics 906122. Results will appear in `results_index/results.csv` when 906122 completes. Low probability of closing AT_HOME gate based on obs_home_rate analysis — running as comparison data point; G2 prep (H3 fix) to proceed in parallel. | TRAINING |
