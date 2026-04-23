# Step 4 — AT_HOME Bias Stuck-State Investigation Plan

**Status:** Four training / calibration attempts have failed to close §3 AT_HOME bias. Baseline (pre-Option-B) is still the best result at PASS 29 / FAIL 17. No further training runs should be launched until the diagnostic plan below has isolated the root cause.

**Scope:** Diagnostic-only. This document does **not** propose retraining. It proposes a ranked set of cheap diagnostic tests, ordered so that the cheapest discriminating experiments run first, with an explicit decision tree for follow-up and a shortlist of candidate fixes tied to each hypothesis for the *next* planning cycle.

**Filename / report conventions (from user's brief):** next validation report download → `step4_validation_report_v4.html`. This plan is saved at `2J_docs_occ_nTemp/Speed-Cluster_docs/step4_training.md`.

**File-vs-log discrepancy to be aware of:** the disk file `step4_validation_report_v2.html` (mtime Apr 22 11:11) actually contains the **Option B epoch-11 `last_checkpoint.pt` validation** (PASS 15 / WARN 1 / FAIL 30 — per the grep above), not the "pre-Option-B baseline PASS 29 / FAIL 17" described in the brief. The true baseline HTML was restored to the non-suffixed `step4_validation_report.html` on the cluster but was **not** retained on local. All per-cycle × per-stratum baseline numbers used below come from the `04_augmentationGSS_hpc.md` Progress Log (job 901071, 2026-04-21), not from v2 on disk.

---

## 1. Summary of what was tried

| # | Run | Change vs. previous | Validation | §3 AT_HOME |ΔΔ̄| per cycle (pp) | §4.2 transition | §4.3 work peak | §2 JS |
|---|---|---|---|---|---|---|---|
| 1 | **Pre-Option-B baseline** (job 901055 + validation 901071, 2026-04-21) | inv-sqrt-freq CE weights + targeted Work×5 / Transit×3 / Social×2 boosts; pure val_JS checkpoint selection | **PASS 29 / FAIL 17** | 2005=15.71, 2010=15.59, 2015=14.54, 2022=10.92 (12–25 pp per stratum) | 2.5× ratio (ratio-1 = 153 pp) | 18.9 pp gap | all PASS (<0.016) |
| 2 | **Option A calibration sweep** (job 901177, 2026-04-21) | No retrain; 20-combo inference grid over T ∈ {0.5,0.6,0.7,0.8} × θ ∈ {0.50..0.70} | **FAILED** | Best (T=0.5, θ=0.7): max 26.27 pp; at T=0.6 θ-sweep produces *identical* metrics → **`home_head` σ outputs saturated > 0.70 for ~75–80 % of slots** | 88 % dev | — | — |
| 3 | **Option B v1** (job 901180, best_model.pt = epoch 1, 2026-04-22) | FiLM per decoder layer + BCE `pos_weight` from observed marginal + `LAMBDA_MARG=0.5` | **PASS 29 / FAIL 17** (same shape as #1) | 2005=15.71, 2010=15.59, 2015=14.54, 2022=10.92 (unchanged vs. #1) | similar | 0.49 pp (PASS) | all PASS |
| 3b | Option B v1 (`last_checkpoint.pt` = epoch 11, same job 901180) | epoch-11 weights (post val_JS regression) | **PASS 15 / WARN 1 / FAIL 30** | 2005 WD 16.65 / Sat 7.97 / Sun 5.19; 2010 WD 15.22 / Sat 7.69 / Sun 6.08; 2015 WD 14.50 / Sat 3.41 / Sun 0.66 (**only §3 PASS**); 2022 WD 10.45 / Sat 5.86 / Sun 4.90 | 35.27 % dev | 0.49 pp (PASS) | overall 0.0684 FAIL |
| 4 | **Option B v2 retrain** (job 901267 + validation 901370, 2026-04-22) | `LAMBDA_MARG 0.5 → 0.1`, lr `1e-4 → 5e-5`, patience `10 → 15`, combined `val_score = val_JS + 0.5·mean_|ΔAT_HOME|` checkpoint metric | **PASS 25 / WARN 2 / FAIL 19** — **regression** | 2005 WD 21.07 / Sat 16.62 / Sun 14.21; 2010 WD 20.49 / Sat 16.35 / Sun 14.99; 2015 WD 17.46 / Sat 13.70 / Sun 10.91; 2022 WD 22.86 / Sat 12.71 / Sun 11.07 (**uniformly worse** than #3) | 159.77 % dev | 5.91 pp (FAIL) | overall 0.0415 WARN |

**Key observations across the four runs:**

1. §3 AT_HOME bias is **always positive** (synthetic > observed) and **always 5–25 pp across every cycle × stratum**. It has not moved meaningfully under any intervention.
2. The direction of the bias is **uniform** — every cycle, every stratum, every run. This rules out a random / noise-driven cause and points at a systematic driver in the pipeline.
3. Option A's θ-sweep at T=0.6 produced *identical* metrics for θ ∈ {0.50..0.65} — directly proves **home_head sigmoid saturation**. Inference-time thresholding is therefore mechanically incapable of fixing §3 on the current weights.
4. Option B added pos_weight + marg_loss **and this made §3 worse on v2** (retrain) — the home head is responsive to the loss signal during training (home-BCE drops cleanly) but the batch-level `marg_loss` did not re-balance the autoregressive output distribution. This is evidence of a **teacher-forcing vs. autoregressive discrepancy** (classic exposure bias), not evidence that the loss is ineffective.
5. §4.2 (transition rate) and §7.1 (work ordering), §7.4 (weekend ≥ weekday AT_HOME) fail persistently across **every** run — suggesting the decoder is producing a corpus-average output that does not respect target stratum conditioning.

---

## 2. Hypotheses, ranked by evidence

For each hypothesis: mechanism, supporting evidence, how it would produce the observed bias sign and magnitude, and the single quickest test that would rule it in or out.

### H1 — Training-pair target-stratum sampling bias (rank: **strong, high prior**)

**Mechanism.** `04C_training_pairs.py` generates, for each training respondent, one pair per target stratum in {1,2,3} \ {observed}. The *source* is reweighted by inverse stratum frequency via `WeightedRandomSampler` (`04D_train.py:404-411`), so every batch has roughly balanced source strata. But the *target* mix depends on sources:

- Weekday (stratum 1) source → targets = {2 = Sat, 3 = Sun}: 100 % weekend targets.
- Saturday (stratum 2) source → targets = {1, 3}: 50/50 weekday/weekend.
- Sunday (stratum 3) source → targets = {1, 2}: 50/50 weekday/weekend.

**Under the balanced-source sampler, the mix of *targets* the decoder is trained to reproduce is ≈ (1×0 + 1×50 + 1×50)/3 weekday = 33 % weekday / 67 % weekend.** In the population, weekend is 2/7 ≈ 28.6 %. The decoder is trained on a diary distribution that is **~2.3× over-represented in weekends**, and weekends have higher AT_HOME rates. The model's corpus-average output is therefore biased toward weekend-style (high-AT_HOME) diaries.

**Why it explains the bias sign + magnitude.** Weekend AT_HOME rate is roughly 10–15 pp higher than weekday. A 2.3× over-representation easily shifts the corpus-average AT_HOME rate by 10–20 pp in the direction observed.

**Supporting evidence from runs.** Bias is uniform across cycles × strata — consistent with a structural corpus bias rather than a model-capacity or conditioning bug. §7.1 (work ordering Wkday ≥ Sat ≥ Sun) also fails → model does not discriminate target stratum → consistent with decoder mostly learning the corpus marginal.

**Single quickest test:** Test 1 (below) — pair-level target AT_HOME distribution.

### H2 — Post-hoc AT_HOME rule asymmetry: syn has `night∧Sleep ⇒ AT_HOME=1` applied; observed does not (rank: **medium; trivially testable**)

**Mechanism.** `04E_inference.py::apply_posthoc_consistency` (lines 86–105) forces `hom30_slot = 1` whenever the generated activity is Sleep (`SLEEP_CAT=4`) and the slot is in `NIGHT_SLOTS` (18 slots: 0–6 and 37–47). It also forces `hom30 = 0` when activity is Work. The observed `hom30_*` in `hetus_30min.csv` comes from Step 3 and is *not* post-hoc-reforced.

If observed data has (say) 95 % AT_HOME during night-Sleep slots but the model's raw output is lower (e.g., 80 %), then post-hoc forcing to 100 % inflates the synthetic AT_HOME rate by the difference, across ~18/48 = 37.5 % of slots.

**Why it could produce 5–10 pp of the gap.** If observed night-sleep-AT_HOME rate is 90 % (not 100 %), and post-hoc forces 100 %, the implied inflation on those 18 slots is (1 − 0.90) × (18/48) = 3.75 pp averaged across the full diary. That's 3–5 pp of the 10–25 pp gap — significant but not the whole story.

**Why it does not fully explain the bias.** If it were the dominant cause, removing the post-hoc rule would close most of the gap; given §3 fails by 10–25 pp, post-hoc alone can't account for all of it.

**Single quickest test:** Test 2 — compute the gap on augmented_diaries with the rule *excluded* in post-processing.

### H3 — Autoregressive feedback amplification (exposure bias) from saturated home_head (rank: **medium-strong, directly observed in job 901177**)

**Mechanism.** At training time, the decoder is teacher-forced: `dec_aux_seq` contains *observed* AT_HOME values at every slot. At inference (`04B_model.py::generate` lines 399–434), the *generated* `home_tok` is fed back as `aux_t` for the next slot via `self.slot_linear(cat([act_emb, aux_t]))`. Once `home_head` saturates (σ > 0.70 for the majority of slots, confirmed in job 901177), every feedback step puts AT_HOME=1 into the next-slot input, biasing the next slot's prediction toward "still at home". The error accumulates across the 48-slot diary.

Teacher-forcing at training time means the model never sees its own feedback — so even a well-calibrated home head at the first slot can cascade into a high AT_HOME rate later in the day.

**Why it explains magnitude.** If the first-slot sigmoid is just slightly > 0.5, saturation + feedback guarantees most subsequent slots stay at home. The job 901177 sweep showed that varying θ from 0.50 → 0.65 produced identical metrics — the feedback had already committed most slots to AT_HOME=1 before the threshold change could take effect.

**Why it could coexist with H1.** H1 (pair bias) supplies a mean-level push toward weekend-style at-home diaries; H3 amplifies small per-slot biases into large per-diary biases. The two are complementary, not competing.

**Single quickest test:** Test 3 (per-slot trajectory) + Test 4 (teacher-forced decode comparison on the same checkpoint). If teacher-forced AT_HOME rate is close to observed but autoregressive is not → H3 confirmed.

### H4 — Decoder ignores cond_vec / tgt_strata despite FiLM (rank: **medium, strongly suggested by §7.1 + §6.2**)

**Mechanism.** FiLM modules are zero-initialized (`04B_model.py:89-90`), so they begin as identity — the decoder's sensitivity to `cond_vec`, cycle, and target stratum is learned. If the CE / BCE gradient on the decoder body dominates the FiLM gradient, the decoder converges on a corpus-average output and FiLM never learns to branch by demographics or target stratum.

**Why it explains §7.1 + §6.2 + §4.3 failures.** If the decoder ignores target stratum, it will not produce different diaries for Weekday vs. Saturday vs. Sunday for the same respondent — violating §7.1 (work ordering) and §7.4 (weekend AT_HOME ≥ weekday). If it ignores LFTAG, it will not differentiate employed vs. NILF → §6.2 fail. If it ignores stratum, it falls back to the corpus average, which is weekend-biased (see H1) → §3 fail in the same direction.

**Why this hypothesis is partially *redundant* with H1.** A decoder that ignores stratum conditioning *on top of* a corpus over-representing weekends will produce weekend-style output regardless of tgt_strata. H4 and H1 multiply rather than substitute.

**Single quickest test:** Test 5 — conditioning probe: for a fixed source respondent, vary tgt_strata ∈ {1,2,3} and measure how much the generated diary's AT_HOME rate actually changes. If Δ < 2 pp across strata on a reasonable sample → decoder is not using the conditioning.

### H5 — Data-side bug in Step 3 `hetus_30min.csv` `hom30_*` definitions (rank: **low**)

**Mechanism.** If observed `hom30_*` systematically undercounts at-home status (e.g., a merge error in Step 3 treats missing-home as zero), then even a perfect model would show syn > obs.

**Why it's low-ranked.** §2 JS divergence was all PASS (< 0.016) in the baseline and Option B epoch-1 runs — activity marginals match. If Step 3 had a broad data bug, activity marginals should be affected too. Also, the bias sign + magnitude is consistent across all four GSS cycles (2005, 2010, 2015, 2022) — a cross-cycle data bug of identical magnitude would be a remarkable coincidence.

**Single quickest test:** Test 6 — sanity-check observed AT_HOME rates in hetus_30min.csv against published GSS aggregates or §2 cross-check.

### Explicitly *not* a hypothesis

- **Activity-index swap (SLEEP_CAT / WORK_CAT bug)** — already fixed on 2026-04-20 (`Phase1_ready.md` exit-criteria checked), so excluded.
- **Model capacity / d_model / layer count** — §2 activity JS passes cleanly at < 0.016, indicating the model has enough capacity to learn marginals. A capacity fix would not leave §2 PASS while §3 fails.

---

## 3. Diagnostic tests — cheapest first, designed to discriminate between hypotheses

All five primary tests (T1, T2, T3, T5, T6) are **CPU-only** and can be bundled into a single `ps`-partition job. T4 requires one ~30-min GPU job and is only needed if T1–T5 are inconclusive.

### Test 1 — Training-pair target-stratum distribution and target AT_HOME marginal (H1)

**Inputs (on the cluster, all already present in `/speed-scratch/o_iseri/occModeling/outputs_step4/`):**
- `step4_train.pt` — source tensor dict, keys `obs_strata`, `aux_seq` (channel 0 = AT_HOME), `cycle_year`.
- `training_pairs.pt` — `src_idx`, `tgt_k_indices` (n_pairs × K), `tgt_strata`.

**Resampling-logic note (per reviewer suggestion 5).** Confirmed by reading `04C_training_pairs.py` + `04D_train.py::Step4Dataset.resample()`: `training_pairs.pt` carries `tgt_k_indices` with shape (n_pairs, K=5), and `Step4Dataset.resample()` draws one of K neighbors uniformly at random each epoch. Over many epochs the effective target weight on each of the K columns is uniform, so T1 takes the **mean across all K columns** per pair (equal in expectation to averaging over random draws, but deterministic — no seeds to manage).

**What to compute.**
1. Marginal distribution of `tgt_strata` across all pairs; compare to (a) uniform {1: 1/3, 2: 1/3, 3: 1/3} and (b) population marginal `bincount(obs_strata) / N`.
2. For each pair, the target diary's AT_HOME rate = mean over the K neighbor indices of `aux_seq[t, :, 0].mean()`. Report three aggregations:
   - **T1a — scalar overall**: pairs' mean target AT_HOME rate minus population AT_HOME rate (the original check).
   - **T1b — 3 × N_cycles table** (per reviewer suggestion 1): mean target AT_HOME rate **per target stratum × cycle**, side-by-side with **observed** AT_HOME rate for that same target stratum × cycle (computed from `aux_seq[train_data where obs_strata==tgt_strata, :, 0]`). This is the decisive test for H1's framing: if per-(target-stratum × cycle) target means match observed per-(stratum × cycle) means within 2 pp, then the target-diary mix is *faithful* to the population per-stratum and the 67% weekend over-representation does NOT translate into a biased supervision signal. In that case H1's "corpus average" framing is wrong and the bias originates in the decoder, not the pairs.
   - **T1c — source × target stratum cross-tab** (per reviewer suggestion 4, one extra groupby): mean target AT_HOME grouped by (src_stratum, tgt_stratum). Expected signal if H1 holds: row (src=Wkday) columns (tgt=Sat, tgt=Sun) show AT_HOME ≈ 0.78–0.82 — exactly the weekend-style signal the decoder is trained to reproduce.
3. Compute the population-weighted AT_HOME rate: `mean(aux_seq[:, :, 0])` over all train respondents.

**Expected signal.**
- If **H1 holds (pair mix distorts the supervision signal)**: T1a gap ≥ 8 pp AND T1b shows target means tracking observed per-stratum means (so the per-pair targets *are* weekend-biased in aggregate purely because 67 % of pairs have weekend targets).
- If **H1 does not hold**: T1a gap ≤ 2 pp, OR T1b shows per-stratum target means matching population per-stratum means — meaning pair sampling faithfully reproduces the per-stratum distribution and the aggregate skew is benign.

**Pass/fail.**
- **H1 confirmed** (pair-mix biased supervision): T1a gap ≥ 8 pp AND T1b target stratum marginal is > 1.5× population-weekend share.
- **H1 rejected as root cause** (pair sampling is faithful): T1b per-(tgt_stratum × cycle) target AT_HOME matches observed per-(stratum × cycle) AT_HOME within 2 pp across all 12 cells — points to decoder-side bias (H3 / H4 amplified on a neutral corpus).
- **Partial support** otherwise.

**Cost.** CPU, < 2 min. Bundle into Test 1/2/3/5/6 job.

### Test 2 — Post-hoc rule contribution to §3 gap (H2)

**Inputs:**
- `augmented_diaries.csv` (current epoch-1 best_model.pt output, 192 183 × 545 columns).
- `hetus_30min.csv` (observed, 64 061 × 120 columns).

**What to compute (simplified per reviewer suggestion 2 — drop Bernoulli resampling, keep only the clean non-night ablation).**
1. For synthetic and observed rows: compute AT_HOME rate per (cycle × stratum) two ways:
   - (a) **All 48 slots** — the §3 gap as currently reported.
   - (b) **Non-night slots only** (slots ∉ `NIGHT_SLOTS` = slots ∉ {0..6, 37..47} → 30 slots, roughly daytime 7:30 AM – 22:00). The post-hoc rule only writes `hom30 = 1` when slot ∈ NIGHT_SLOTS and act=Sleep, so excluding night slots cleanly removes the rule's contribution without any estimation.
2. Report: per (cycle × stratum) × {all_slots, non_night_slots}, the observed rate, synthetic rate, gap.

**Expected signal.**
- If H2 is the dominant cause: gap on non-night slots < 5 pp, but gap on all slots is 10–25 pp.
- If H2 is small contributor: gap on non-night slots is also 8–20 pp → rule explains at most a few pp, rest is elsewhere.

**Pass/fail.**
- **H2 dominant** if gap closes by ≥ 10 pp when night slots are excluded.
- **H2 small** if gap closes by 2–5 pp → account for in final fix but not root cause.
- **H2 rejected** if gap closes by < 2 pp.

**Cost.** CPU, < 5 min.

### Test 3 — Per-slot AT_HOME trajectory (H3 diagnostic signature)

**Inputs:** same as Test 2.

**What to compute (scalars required, per reviewer suggestion 3 — decision tree must be programmatic).**
1. For each of 48 slots t: compute per-cycle × per-stratum synthetic AT_HOME rate minus observed AT_HOME rate → 48-slot gap trajectory.
2. Emit both a matplotlib PNG (optional, for human inspection) AND the following **scalars written into `diagnostics_v4.json`** so the next session can consume them without re-parsing a figure:
   - `morning_mean_gap_pp`: mean gap over slots 0–13 (~04:00–10:30, mostly at-home in obs).
   - `midday_mean_gap_pp`: mean gap over slots 14–27 (~11:00–17:30).
   - `evening_mean_gap_pp`: mean gap over slots 28–47 (~18:00–03:30, includes late-night back-at-home).
   - `afternoon_evening_mean_gap_pp`: combined 14–47 (contrast with morning).
   - `slot_of_max_gap`: argmax slot (0..47) of the gap.
   - `max_gap_pp`: value at argmax.
   - `night_mean_gap_pp`: mean over NIGHT_SLOTS (useful for H2 corroboration).
   - `gap_range_pp`: max − min across 48 slots (used to flag "flat" trajectories).
   - Each emitted per cycle × per stratum AND overall.

**Expected signal.**
- **H3 (feedback amplification)**: `afternoon_evening_mean_gap_pp ≥ 2 × morning_mean_gap_pp`; `slot_of_max_gap` ≥ 20.
- **H1 (corpus bias)**: `gap_range_pp < 5` (flat trajectory) and gap uniformly positive.
- **H2 (post-hoc rule)**: `night_mean_gap_pp` is substantially higher than the non-night mean; equivalently, T2(b) closes the gap.

**Pass/fail.**
- **H3 confirmed as major contributor** if `afternoon_evening_mean_gap_pp / max(morning_mean_gap_pp, 1) ≥ 2.0` AND `slot_of_max_gap ≥ 20`.
- **H1 confirmed as major contributor** if `gap_range_pp < 5` AND overall mean gap ≥ 8 pp.
- **H2 confirmed as contributor** if `night_mean_gap_pp − (midday_mean_gap_pp + evening_mean_gap_pp)/2 ≥ 5`.

**Cost.** CPU, < 5 min.

### Test 4 — Teacher-forced vs. autoregressive decode on val set (H3 confirmation, optional)

**Trigger.** Run only if Test 3 signals feedback amplification (gap grows across slots) and H1 does not fully account for the bias via Test 1. If Tests 1–3 fully resolve the attribution, skip.

**Inputs:**
- Current `best_model.pt` (job 901267 retrain; since we know the pre-retrain checkpoint is overwritten, accept that we are diagnosing the retrain model, not the baseline).
- `step4_val.pt`.

**What to compute.**
1. Write a one-off `04H_teacher_force_diag.py` that: for a random sample of 1000 val pairs, calls `model.decode(...)` in teacher-forcing mode (i.e., ground-truth shifted input) and extracts `sigmoid(home_logits)` per slot. Compute mean per-slot AT_HOME rate under teacher-forcing.
2. Compare to autoregressive-generated AT_HOME rate (which we already have from augmented_diaries.csv).

**Expected signal.**
- **H3 confirmed**: teacher-forced AT_HOME rate ≈ observed (within 2 pp), autoregressive AT_HOME rate ≫ observed. Gap between them is *entirely* due to exposure bias.
- **H3 not the whole story**: teacher-forced AT_HOME also > observed → training distribution itself is biased (points to H1).

**Pass/fail.**
- Δ(AR − TF) ≥ 8 pp → H3 confirmed.
- Δ(AR − TF) ≤ 2 pp → H3 ruled out, focus shifts to training data (H1).

**Cost.** GPU `pg` partition, ~30 min. One small custom diagnostic script; no retraining.

### Test 5 — Conditioning probe: does decoder use `tgt_strata` and `cond_vec`? (H4)

**Inputs:** current `best_model.pt`, `step4_val.pt`, a 200-respondent random subsample.

**What to compute.**
1. For each probed respondent: run `model.generate(...)` with the *same* `act_seq, aux_seq, cond_vec, cycle_idx` but varying `tgt_strata ∈ {1, 2, 3}`. Record the AT_HOME rate of each generated diary.
2. For each probed respondent: zero out `cond_vec` (test conditioning strength), run `generate()` for all three `tgt_strata`, compare to the un-zeroed version.
3. Report mean absolute AT_HOME-rate difference across strata (Δ_strata), and mean absolute difference between cond_vec-on vs cond_vec-zeroed (Δ_cond).

**Expected signal.**
- **H4 confirmed (conditioning failure)**: Δ_strata < 2 pp (decoder ignores stratum) AND Δ_cond < 1 pp (decoder ignores demographics).
- **H4 rejected**: Δ_strata ≥ 5 pp, with ordering Weekday < Sat < Sun in AT_HOME rate.
- **Partial**: Δ_strata in {2, 5} pp — weak conditioning but not zero.

**Pass/fail.** As above.

**Cost.** GPU, ~10 min (200 respondents × 6 variants via model.generate batched). Bundle into Test 4's GPU job if both are needed.

### Test 6 — Observed AT_HOME sanity check (H5, due diligence)

**Inputs:** `hetus_30min.csv` only.

**What to compute.**
1. Per cycle × stratum: mean AT_HOME rate across 48 slots.
2. Per cycle × stratum: night-slot AT_HOME rate (slots 0–6 and 37–47).
3. Cross-check against published GSS time-use summaries (user judgment call — whether the observed rates are plausible).

**Expected signal.**
- Weekday AT_HOME ~ 65–70 %, Saturday ~ 75–80 %, Sunday ~ 80–85 % in recent cycles → plausible → H5 rejected.
- If observed rates are wildly different from expectation → H5 becomes a candidate and Step 3 should be re-audited.

**Pass/fail.**
- **H5 rejected** if rates are within published-literature ranges.
- **H5 flagged** if any (cycle × stratum) AT_HOME rate is < 40 % or > 95 % → investigate Step 3.

**Cost.** CPU, < 1 min.

---

## 4. Decision tree

All commands are Speed `ps`-partition jobs unless otherwise noted. Tests 1, 2, 3, 5 (CPU-only part of 5: not yet, the cond_vec probe needs generate() → GPU), 6 bundle into one CPU job. Test 4 + Test 5 GPU part bundle into one follow-up GPU job if needed.

```
[RUN T1, T2, T3, T6 in a single CPU job — step4_diagnostics_cpu.sh]
           │
           ├── T6 flags observed AT_HOME implausible?
           │      ├── YES → stop, audit Step 3 (H5) — outside Step 4 scope
           │      └── NO  → continue
           │
           ├── T1 → target-strata skew ≥ 1.5× weekend AND target AT_HOME gap ≥ 8 pp?
           │      ├── YES → H1 is at least a major contributor. Goto T3 shape check.
           │      └── NO  → H1 rejected or weak. Goto H3/H4 branch.
           │
           ├── T2 → does excluding night slots close the §3 gap by ≥ 10 pp?
           │      ├── YES → H2 dominant. Design fix is trivial (tune or drop rule). Still confirm H1/H3 by T3.
           │      └── NO  → H2 is small contributor. Move on.
           │
           └── T3 → gap trajectory across slots?
                  ├── FLAT (constant) → H1 dominant. Skip T4.
                  │       → Go to Section 5 fixes, H1 shortlist.
                  ├── GROWING (morning OK, afternoon/evening bad) → H3 dominant.
                  │       → [RUN T4 on GPU — step4_diagnostics_gpu.sh]
                  │       → if Δ(AR − TF) ≥ 8 pp → H3 confirmed → Section 5 fixes, H3 shortlist.
                  │       → if Δ(AR − TF) ≤ 2 pp → data bias dominant → fall back to H1.
                  └── NIGHT-CONCENTRATED → H2 dominant. Already handled in T2.

[After first CPU job: if H1/H3 unresolved AND §7.1/§6.2 failures persist]
           → [RUN T5 GPU probe — can share the T4 GPU job]
           → if Δ_strata < 2 pp → H4 is an amplifier of H1/H3 → add conditioning
             strengthening to the fix shortlist.
           → if Δ_strata ≥ 5 pp → H4 rejected.
```

---

## 5. Candidate fixes — shortlist per hypothesis (DO NOT implement until diagnostics above complete)

These are *candidate* remedies. Each is tied to a hypothesis; none should be implemented until the diagnostic tests above identify which hypothesis (or combination) is dominant, because implementing the wrong one will cost another 1.5–2 h GPU run plus validation, and two such runs have already regressed §3.

### If H1 dominant (training-pair corpus bias)

- **F1a (preferred, cheap).** Rewrite `04C_training_pairs.py` so that target strata are sampled proportionally to the population (not uniformly across {1,2,3}\{observed}). For a Weekday source, instead of always generating both (→Sat, →Sun) pairs, emit fewer Weekend-target pairs per source so that aggregate pairs have target-stratum marginal matching the population.
- **F1b (alternative).** Keep pair generation uniform but add a **target-stratum-inverse-frequency weight** to the per-pair loss in `04D_train.py::compute_loss`, so rare-target pairs (Weekday targets) get higher gradient. This avoids regenerating `training_pairs.pt`.
- **F1c (complement to F1a/F1b).** Add a **marginal AT_HOME ref per (target_cycle, target_stratum)** computed from observed data, and reshape the `marg_loss` to penalize deviation from the per-stratum reference (not the global mean as it does now — `04D_train.py:140` uses `home_tgt.mean()`, which mixes strata).

### If H2 dominant (post-hoc rule)

- **F2a.** Delete the night-Sleep → AT_HOME=1 rule in `04E_inference.py::apply_posthoc_consistency`. Retain the Work → AT_HOME=0 rule (that one is semantically obvious: paid work usually means not at home, and syn Work% is already lower than obs so the rule only affects a small fraction).
- **F2b (alternative).** Soften the rule to a probabilistic version: during night+Sleep slots, draw `hom30` from the *observed* conditional rate `p(home | night, sleep, cycle, stratum)` from `hetus_30min`.

### If H3 dominant (exposure bias / feedback amplification)

- **F3a.** **Scheduled sampling** during training in `04D_train.py`: with probability p(epoch) (annealing from 0 to 0.3 across epochs), replace the teacher-forcing decoder input at each slot with the *model's own previous predicted slot* during the forward pass. Closes train-inference mismatch.
- **F3b (simpler).** **Slot-dropout** on teacher-forcing aux input: randomly zero out the AT_HOME channel of `dec_aux_seq` during training with p=0.2 per slot, forcing the decoder to not rely on the previous-slot AT_HOME feedback. Cheapest, one-line change.
- **F3c (orthogonal).** **Break saturation** by adding label smoothing to the BCE on `home_head` (e.g., map targets from {0, 1} to {0.05, 0.95}) so the sigmoid logits stay bounded. Directly addresses the observed saturation above σ > 0.70.

### If H4 dominant (conditioning ignored)

- **F4a.** Add a **conditioning auxiliary loss**: train a small MLP head on top of the decoder's first-layer output that predicts `tgt_strata` from the hidden state — gradient flows back through the decoder and forces it to retain stratum information. 3-way CE auxiliary term, small weight (λ ~ 0.1).
- **F4b.** Replace current additive `strata_linear` + FiLM with **cross-attention over a compact stratum/cond embedding** — gives the decoder explicit attention pointers to the conditioning signal rather than relying on residual + FiLM.
- **F4c.** Warm-start FiLM parameters away from zero-init so they're active from the start, at the cost of more noise in the first 1–2 epochs.

### Likely combinations (only to plan for, not implement yet)

- If diagnostics show H1 + H3 co-dominant (most plausible given the evidence): plan is (F1a or F1b) + (F3b or F3c). Both changes are cheap; F3b is a one-line dropout add.
- If H4 also contributes: layer F4a (auxiliary conditioning loss) on top, small weight. This is the cheapest conditioning intervention that does not require architectural change.

---

## 6. Constraints checklist (self-audit)

- [x] All proposed cluster commands are single physical lines, chained with ` ; ` (see Section 7).
- [x] No `2>/dev/null`, no `$(...)`, no `bash -c '...'` — tcsh/csh friendly.
- [x] Speed login-node only used for `sbatch` submission and `squeue` checks — all computation in CPU `ps` or GPU `pg` jobs.
- [x] Do **not** touch `eSim_occ_utils/25CEN22GSS_classification/eSim_{datapreprocessing,dynamicML_mHead,dynamicML_mHead_alignment}.py` (CLAUDE.md rule).
- [x] Do **not** touch MC array jobs 900550_5 / 900550_6 on `ps` (unrelated BEM workstream).
- [x] Pre-retrain `best_model.pt` is gone — diagnostics operate on the current (post-retrain) checkpoint. This affects what "raw" model outputs we can inspect; Tests 1, 2, 3, 6 don't need any checkpoint (they work on pairs + CSV). Tests 4, 5 use whatever `best_model.pt` is currently on the cluster.
- [x] Next validation HTML download → `step4_validation_report_v4.html` (noted for future retrain validation, not needed for diagnostics).

---

## 7. Next action — single diagnostic CPU job

Once you approve this plan, the first action is to stage a single CPU-only diagnostic job bundling Tests 1, 2, 3, 6 (and the CPU-only parts of any other tests). It reads only existing artifacts on the cluster:

- `outputs_step4/step4_train.pt`
- `outputs_step4/step4_val.pt`
- `outputs_step4/training_pairs.pt`
- `outputs_step4/augmented_diaries.csv`
- `outputs_step3/hetus_30min.csv`

and writes a single `outputs_step4/diagnostics_v4.json` + a short stdout summary. Then we decide whether to run the GPU job (Tests 4 + 5) based on Test 3's trajectory signal.

A follow-up document or code task will specify the exact Python script and `sbatch` wrapper — not included here per the brief's "do not write code yet" constraint.

**Job resource spec (per reviewer suggestion 6 — tightened):** `ps` partition, 8 G mem, 4 cores, 30 min wall. augmented_diaries.csv (222 MB) + step4_train.pt (few-hundred MB) easily fit in 8 G with pandas; 16 G was over-provisioned.

**Pre-submit checks (per reviewer suggestion 7):** before `sbatch`, on the cluster in a single line:
`cd /speed-scratch/o_iseri/occModeling ; sacct -u o_iseri --starttime=today --format=JobID,State,Partition ; ls -lh outputs_step4/training_pairs.pt outputs_step4/step4_train.pt outputs_step4/augmented_diaries.csv outputs_step3/hetus_30min.csv`

---

*End of investigation plan. Next step: user review. No sbatch submissions should occur until the diagnostic script for Tests 1/2/3/6 is written and reviewed.*

---

## 8. Task — Co-presence head collapse + activity head calibration (post-04I audit, 2026-04-23)

**Status:** proposed — diagnose before any retrain. Triggered by the F2-baseline 04I audit (patched run, `diagnostics_v4_actcop.json` 31 KB) that landed **after** code-organisation bundle. Follows the same "cheapest discriminating test first" pattern as §§2–4.

**Filename / report conventions:** artifacts this task reads live locally at `C:\Users\o_iseri\Desktop\GSSCanada\diagnostics_v4_actcop.json`, `diagnostics_v4_copresence.png`, `diagnostics_v4_activity.png`. On the cluster, source of truth is `outputs_step4/augmented_diaries.csv` + `outputs_step3/hetus_30min.csv` + the trained `best_model.pt`.

### 8.1 Aim

Identify the root cause of two 04I findings before scoping any fix:

1. **Co-presence head — catastrophic mode collapse.** Of the 7 observed channels, only Alone (syn 52.7 % vs obs 35.3 %, +17.4 pp) and Spouse (syn 3.4 % vs obs 22.4 %, −19.0 pp) have non-trivial synthetic mass. **Five channels (Children, parents, friends, others, colleagues) output exactly 0 with no slot variation** — gap ranges −1.9 to −7.7 pp. Worst-slot: Alone +54 pp at slot 1 (midnight); Spouse −33 pp at slot 33 (16:30). Collapse worsens with cycle recency (2022 Sunday Alone +31 pp).

2. **Activity head — systematic miscalibration (recoverable).** JS mean 0.056, max 0.068 (threshold 0.05) — 10/12 cells FAIL, 2 WARN. Syn over-predicts code 1 (~0.30 vs obs ~0.17) and under-predicts code 10 (leisure) and code 13 on weekends. Weekday top-1 slot agreement 82 %; weekend drops to ~50 %. 2022 cleanest (Sat/Sun JS 0.034–0.038 WARN).

This task is **diagnostic-only** — same scope contract as §3. No retraining, no head reweighting, no data regeneration until the dominant cause per head is isolated.

### 8.2 Hypotheses (co-presence)

#### HC1 — Inference-time hard thresholding on sigmoid outputs (rank: **top, trivially testable**)

**Mechanism.** Co-presence is a 7-way multi-label BCE head. If `04E_inference.py` (or a downstream augmenter step) applies `σ > 0.5` before writing to `augmented_diaries.csv`, minority classes whose logits never clear 0 — entirely plausible given their low observed marginals (1.9–7.7 %) — will deterministically write 0 for every slot. That matches the "exactly 0, no slot variation" signature perfectly. The two surviving channels (Alone 35.3 %, Spouse 22.4 %) are the only two with marginals high enough that their mean logit clears 0.

**Why it explains the sign + magnitude.** A hard threshold converts a soft probability distribution into the argmax of the 2 dominant logits. Alone absorbs mass that should have gone to "with someone" → +17.4 pp. Spouse is under-predicted because in "Alone vs Spouse" tie-breaks Alone wins slightly more often → −19.0 pp. Five minority channels never clear → exact zero.

**Single quickest test:** **Test 8.A** below — grep the inference + augmenter scripts for any threshold or zero-write operation on the co-presence columns.

#### HC2 — BCE without `pos_weight` on minority heads → "always 0" easy optimum (rank: **strong, requires checkpoint inspection**)

**Mechanism.** If the co-presence BCE in `04D_train.py` is unweighted, the gradient for rare classes (parents 1.9 %, friends 4.8 %) is dominated by the negative class. The easy optimum is "predict 0 always" → loss ≈ class marginal, which is low for rare classes. Head weights converge to a large negative bias, `σ(logit) < 0.5` for every slot, and even without a threshold the *expected* marginal approaches zero for those channels.

**Why it explains partial collapse.** Unlike HC1 (bright-line thresholding), HC2 predicts raw `σ` outputs that are low but not literally zero — the 04I JSON reports "~0 %" for "others" (not 0 %), consistent with a softly collapsed head. Children/friends/colleagues report exact 0 in the summary table, but the summary is rounded — HC1 and HC2 can coexist.

**Single quickest test:** **Test 8.B** — dump raw `σ` outputs from `best_model.pt` on a 200-row val slice and check whether minority-channel means are ≈ 0 (HC2-only) vs very small positives (HC2 partial, HC1 dominant).

#### HC3 — Augmenter post-processing writes hard zeros to minority columns (rank: **medium, discovered-only-by-grep**)

**Mechanism.** If the diary-assembly step downstream of inference drops or zero-writes co-presence columns for any reason (schema mismatch across cycles, a fillna(0) on a merge, deliberate cycle-2005 masking for `colleagues`), the head itself could be healthy but the output file would still show 5 zero columns.

**Why it's medium-ranked.** The `colleagues` column is already correctly NaN'd for 2005 (the field didn't exist in GSS 2005 — noted as expected in the 04I summary) — which proves the augmenter *does* touch these columns. That raises the prior that it also silently zeroes others.

**Single quickest test:** Subsumed by **Test 8.A** (same grep covers augmenter + inference).

### 8.3 Hypotheses (activity)

#### HA1 — Stratum/cycle conditioning weak on the activity head (rank: **top, matches weekday/weekend asymmetry**)

**Mechanism.** Weekday top-1 agreement 82 %, weekend drops to 50 %. Cycle 2022 cleanest (nearly-passing weekends), older cycles worst. This is the same stratum-conditional bias signature as §3 AT_HOME under HC4 from the §2 analysis — decoder responds to the *corpus average* and does not fully use DAYTYPE / CYCLE conditioning. If the corpus mix is weekday-heavy in older cycles, the weekend synthetic distributions inherit weekday activity proportions (over-sleep, under-leisure).

**Why it explains code 1 ↑ / code 10 ↓.** Corpus-average proportions are weekday-weighted → code 1 (sleep/personal care) is over-represented vs. weekend proportions → code 10 (leisure) under-represented. Identical pattern to the observed deltas.

**Single quickest test:** **Test 8.C** — run the §3-style conditioning probe (H4 / Test 5) on the activity head instead of AT_HOME: vary `tgt_strata ∈ {1,2,3}` for a fixed source, measure per-class activity-rate Δ.

#### HA2 — Class-frequency weighting drifted (rank: **medium, cheap scalar check**)

**Mechanism.** §1 reports activity CE uses "inv-sqrt-freq CE weights + targeted Work×5 / Transit×3 / Social×2 boosts". If the F2 training inherited these but the Work×5 boost overshoots given F2's other changes (LAMBDA_HOME escalation), the activity distribution could re-skew.

**Why it's medium.** 2022 is nearly passing → the head *can* calibrate when the data is rich. The failure is mostly on older/weekend cells → conditioning-path issue (HA1), not a global weighting issue. HA2 is a secondary amplifier.

**Single quickest test:** **Test 8.D** — compare F2 activity-head loss weights against F1 job 901399; if unchanged, HA2 rejected.

### 8.4 Diagnostic tests — cheapest first

All four are **local or CPU-only** and can run today against the existing F2 artifacts.

#### Test 8.A — Grep inference + augmenter for co-presence thresholding / zero-writes (HC1, HC3)

**Inputs (local read-only):**
- `2J_docs_occ_nTemp/04E_inference.py`
- `2J_docs_occ_nTemp/04B_model.py` (for the head definition — does forward() emit raw σ or thresholded binaries?)
- Any augmenter / diary-assembly script downstream of 04E (identify by following the call graph from 04E's entry point).

**What to compute.**
1. Grep for: `> 0.5`, `>= 0.5`, `threshold`, `.round()`, `astype(int)`, `> thresh`, on any variable tied to co-presence (names likely: `cop`, `copresence`, `coprés`, `with_`, or the 7 explicit column names).
2. Grep for hard zero writes on co-presence columns: `= 0`, `fillna(0)`, `.clip(lower=`, on any of the 7 channel names.
3. Locate where raw `σ(cop_logits)` is converted to the column values in `augmented_diaries.csv`. Is it `sigmoid → threshold → int` or `sigmoid → float`?

**Expected signal.**
- **HC1 confirmed** if a `σ > 0.5` (or any hard threshold) is applied before write. Fix is trivial: either (a) write raw probabilities (preferred — downstream BEM can threshold per-channel later) or (b) use per-channel thresholds tuned to observed marginals.
- **HC3 confirmed** if a zero-write / column-drop is found on one of the 5 collapsed channels.
- **Both rejected** → HC2 (training-side collapse) becomes dominant → task escalates to Test 8.B.

**Cost.** Local grep + read, ≤ 10 min. No cluster submission.

#### Test 8.B — Raw-σ dump from checkpoint on val slice (HC2)

**Trigger.** Only if Test 8.A finds no threshold / zero-write.

**Inputs (on the cluster):** current `best_model.pt`, `step4_val.pt`, 200-row random val sample.

**What to compute.** Small one-off script that runs `model.generate(...)` on the sample, extracts raw sigmoid outputs from the co-presence head (pre-any-postprocessing), and reports per-channel mean σ and per-channel fraction of slots with σ > 0.5.

**Expected signal.**
- **HC2 confirmed** if minority-channel mean σ ≈ 0.02–0.10 (collapsed but not zero) AND fraction(σ > 0.5) == 0.
- **HC2 rejected** if mean σ tracks observed marginal (e.g., parents ≈ 0.02, friends ≈ 0.05) but still clears threshold at some slots → inference-side masking elsewhere.

**Cost.** GPU `pg`, ~15 min. Bundle with Test 8.C if run.

#### Test 8.C — Activity-head conditioning probe (HA1)

**Trigger.** Run in same GPU job as 8.B.

**Inputs:** current `best_model.pt`, `step4_val.pt`, 200-respondent random subsample.

**What to compute.** For each probed respondent: run `model.generate(...)` with same source but varying `tgt_strata ∈ {1, 2, 3}`. Record per-class activity rates (14 classes) per generated diary. Report Δ per class across strata.

**Expected signal.**
- **HA1 confirmed** if code 1 (sleep) Δ_strata < 2 pp AND code 10 (leisure) Δ_strata < 2 pp (decoder ignores stratum for the classes where 04I shows weekend bias).
- **HA1 rejected** if both deltas ≥ 5 pp with expected ordering (code 1 higher on weekday, code 10 higher on weekend).

**Cost.** GPU, ~10 min. Piggyback on the same job as 8.B.

#### Test 8.D — F2 vs F1 activity-head weight diff (HA2)

**Inputs:** local copies of `04D_train.py` for F1 (job 901399 commit) and F2 (current checkpoint commit).

**What to compute.** Diff the two `04D_train.py` files restricted to activity-head loss definition + class-weight vector.

**Expected signal.**
- **HA2 rejected** if weights unchanged between F1 and F2 (given F1 activity passed §2 JS < 0.016 and F2 does not, the regression is from something else — most likely LAMBDA_HOME interaction).
- **HA2 confirmed** if weights differ → document the delta and tie to the miscalibration direction.

**Cost.** Local `git diff`, ≤ 2 min. No cluster.

### 8.5 Decision tree

```
[RUN Test 8.A (local grep)]
   │
   ├── Threshold / zero-write found? → HC1 or HC3 confirmed.
   │      → Goto 8.6 fix shortlist, F-COP-1 or F-COP-3.
   │      → No retrain needed — inference-side / augmenter-side fix only.
   │
   └── Nothing found?
          → Test 8.B + 8.C bundled in one GPU job.
          → HC2 likely confirmed → fix requires retrain with pos_weight.
          → HA1 probed in same job.

[RUN Test 8.D (local diff) — in parallel with 8.A, zero marginal cost]
   └── Confirms / rejects HA2 before any GPU time is spent.
```

### 8.6 Candidate fixes — shortlist per hypothesis (DO NOT implement until 8.4 complete)

#### If HC1 dominant (inference threshold)

- **F-COP-1a (preferred).** Remove hard threshold from 04E / augmenter. Write raw `σ` probabilities into `augmented_diaries.csv`. Downstream BEM multipliers already expect soft presence values per 04H contract.
- **F-COP-1b (alternative).** Replace `σ > 0.5` with per-channel thresholds calibrated to observed per-channel marginals (e.g., `θ_alone = 0.50`, `θ_parents = 0.03`). Preserves int output if a downstream consumer requires it.

#### If HC2 dominant (training-side collapse)

- **F-COP-2a.** Retrain with `pos_weight` on the co-presence BCE in `04D_train.py`, one weight per channel from `1/marginal`. Same mechanism as F1's AT_HOME `pos_weight`.
- **F-COP-2b (complement).** Add a per-channel marginal auxiliary loss (analogous to §5 F1c) penalising `E[σ_c] − p_obs_c` per channel × cycle × stratum.

#### If HC3 dominant (augmenter zero-write)

- **F-COP-3.** Remove the offending fillna / drop / mask. Keep the intentional `colleagues`=NaN-for-2005 mask — it is documented as correct. No retrain needed.

#### If HA1 dominant (activity stratum conditioning)

- **F-ACT-1.** Same intervention path as AT_HOME under §5 F4a — add a conditioning auxiliary loss predicting `tgt_strata` from decoder hidden state. Single intervention covers both heads.

#### If HA2 dominant (weight drift)

- **F-ACT-2.** Revert activity-head class weights to F1 values; rerun with F2's LAMBDA_HOME change but F1's activity loss.

### 8.7 Expected result

- Test 8.A produces a definitive yes/no on HC1+HC3 within 10 min of local work.
- If HC1 or HC3 confirmed → co-presence head fix is **inference-only**, no F3 retrain burden — a single re-run of 04E on the F2 checkpoint produces a corrected `augmented_diaries.csv`, which 04I re-validates on CPU in 30 min.
- If HC2 dominant → co-presence fix requires F3 retrain with pos_weight + per-channel marg_loss; activity head fix (HA1) can share the same retrain.
- **Decision gate:** F3 is only triggered if HC2 or HA1 is confirmed. Otherwise the F2 checkpoint stands and only inference + augmenter are touched.

### 8.8 Test method

- **8.A output:** a brief local note listing each grep hit with `file:line` and a one-line verdict per hit (is it the threshold we're looking for, or unrelated).
- **8.B / 8.C output:** one JSON (`diagnostics_v4_raw_sigma.json`) per channel with `mean_sigma`, `frac_over_05`, `per_strata_delta`, scp'd locally.
- **8.D output:** a 3-line git diff summary pasted into the progress log.
- **Cross-check:** 8.A verdict must be consistent with 8.B's raw σ distribution — if 8.A finds no threshold but 8.B shows `frac_over_05 = 0` for collapsed channels, HC2 is confirmed; if 8.B shows `frac_over_05 > 0` but the CSV has zeros, search harder for an augmenter-side mask (HC3).

### 8.9 Risks / fallback

- **Risk: F2 checkpoint may be the only viable baseline.** If HC2 + HA1 are both confirmed and F3 is triggered, F3 must not overwrite F2's `best_model.pt` before the retrain succeeds. Mitigation: on the cluster, `cp best_model.pt best_model_F2.pt` before F3 submission.
- **Risk: activity head improvements could regress §2 JS baseline.** F1's §2 activity JS was PASS < 0.016; F2 already regressed this to FAIL. Any F3 conditioning change (F-ACT-1) must re-validate §2 alongside §3 and the 04I audit.
- **Risk: over-fitting co-presence pos_weight.** F-COP-2a with `1/marginal` weights is aggressive for channels with marginals < 2 % (e.g., parents). If used, cap pos_weight at `1/0.05 = 20` to avoid gradient explosion on rare classes.
- **Fallback:** if Test 8.A exposes a cheap threshold/mask bug (HC1 or HC3), apply F-COP-1a or F-COP-3 on the F2 checkpoint, re-run 04E + 04I locally or on ps partition, and defer F3 entirely. Activity head (HA1) then waits for the next natural retrain cycle.

### 8.10 Progress Log

- **2026-04-23.** Task created after F2 04I audit (`diagnostics_v4_actcop.json`, patched cluster run 13:06). Findings: co-presence head collapsed to Alone/Spouse (5 channels exactly 0); activity head 10/12 FAIL with weekday/weekend asymmetry. Task scope: §8.4 diagnostics before any F3 retrain. Local Test 8.A is the first action — no cluster submission required until it completes.

- **2026-04-23 (Test 8.A — COMPLETE).** Local grep + read of `04E_inference.py`, `04B_model.py`, `04D_train.py`. No augmenter script downstream of 04E exists — `run_inference()` in 04E assembles `augmented_diaries.csv` directly. `augmented_diaries.csv` not present locally; column names inferred from 04E `COP_COLS` (9 entries). Findings:

  **Category A hits: 1 (the root cause)**
  - `04B_model.py:420` — `cop_tok = (torch.sigmoid(self.cop_head(out_t)) > 0.5).float()` — **YES, HC1 confirmed.** Hard `> 0.5` threshold on all 9 co-presence channels inside `generate()`, hardcoded (no argument). Contrast with `home_tok` at line 417 which uses the configurable `home_threshold` — co-presence never got the same treatment. Any channel whose mean logit is negative (σ < 0.5) fires 0 on every slot. Five minority channels (Children, parents, friends, others, colleagues) have low observed marginals (1.9–7.7 %); if their logits are biased negative after training, this threshold produces exact zeros with zero slot variation — which matches the 04I finding exactly.
  - `04E_inference.py:64–65, 109` — `--home_threshold` / `home_threshold: float = 0.5` — **NOT a COP hit.** AT_HOME head only, unrelated.

  **Category B hits: 1 (expected, not a bug)**
  - `04E_inference.py:173` — `cop_k[:, 8] = 0.0` for `cy in (2005, 2010)` — hard zero on colleagues (channel index 8) for old-cycle rows. This is documented expected behavior (GSS 2005 did not collect co-workers field). The `04I` corrected `COP_NAMES` list already accounts for this via NaN on 2005 observed rows (`04E_inference.py:214–216`). Not HC3.
  - No other zero-writes or `fillna(0)` found on any of the 7 audited COP channels.

  **Category C (raw σ → CSV path):**
  - `04B_model.py:420` — conversion happens inside `generate()`: `sigmoid → (> 0.5) → float (0.0 or 1.0)`. Raw σ is never preserved past this line.
  - `04E_inference.py:166` — `gen_cop = gen_cop.cpu().numpy()` — already binary float array at this point.
  - `04E_inference.py:218` — `row[f"{cn}30_{slot_str}"] = int(val)` — converts 0.0 / 1.0 to int 0 / 1. Type written to CSV: **int**. This `int()` call is not independently lossy now (values are already 0.0 or 1.0), but it **would truncate to 0** for any float in (0, 1) if the threshold were removed — so it must be changed alongside the threshold fix.

  **HC2 assessment (secondary):**
  - `04D_train.py:143–158` — co-presence BCE is `F.binary_cross_entropy_with_logits(cop_logits, cop_tgt, reduction="none")` with **no `pos_weight`**. AT_HOME gets `home_pos_weight`; co-presence does not. HC2 (training-side collapse due to unweighted minority BCE) is therefore likely co-present but is not the deciding factor: HC1 at inference time is sufficient to explain exact zeros regardless of whether the trained σ is 0.03 or 0.50 for minority channels.

  **Verdict:**
  - HC1 **confirmed** — `04B_model.py:420` is the root cause. Hard `> 0.5` on all 9 co-presence channels in autoregressive `generate()`. No per-channel tuning, no raw-probability path.
  - HC3 **rejected** — the only zero-write found (`04E_inference.py:173`) is the documented expected colleagues mask for 2005/2010. No other post-hoc masking.
  - HC2 **likely co-present** (no `pos_weight` on COP BCE), but dominated by HC1. Whether HC2 matters becomes visible only after F-COP-1a is applied and 04I re-validates on soft probabilities.

  **Next action: (a) Apply F-COP-1a — inference-side fix, no retrain.**
  Two-line change: (1) remove `> 0.5` from `04B_model.py:420` so `generate()` returns raw σ float; (2) change `04E_inference.py:218` from `int(val)` to `round(float(val), 4)` to preserve soft probabilities in the CSV. Then re-run 04E on the cluster + re-run 04I diagnostic. If 04I co-presence verdict improves to `copresence_ok` (max_gap_pp < 3.0 pp), HC2 is not material and F3 retrain is deferred. If minority channels remain collapsed (mean σ << obs marginal), escalate to Test 8.B.

- **2026-04-23 (F-COP-1a applied — split-output variant, inference-only, submitted).** Review of `04B_model.py:420–434` surfaced that `cop_tok` is consumed autoregressively at line 429 (`aux_t = torch.cat([home_tok.unsqueeze(-1), cop_tok], dim=-1)` → fed as next-step decoder input). Training used teacher-forced binary labels, so dropping the threshold naively would create a train/inference mismatch (floats fed where binaries were trained). **Revised patch: split-output.** Keep binary `cop_tok` internal for AR feedback; add a new list `gen_cop_probs` that carries raw σ; return as 4th tensor from `generate()`; 04E consumes the new tensor for CSV writing.

  Edits:
  - `04B_model.py:387–390` — added `gen_cop_probs = []` next to `gen_acts / gen_homes / gen_cops`.
  - `04B_model.py:419–426` — split: `cop_probs = σ(logits)` (raw), `cop_tok = (cop_probs > 0.5).float()` (binary, unchanged semantics for AR feedback); append both.
  - `04B_model.py:436–441` — return tuple extended to 4 tensors, 4th is `torch.stack(gen_cop_probs, dim=1)` (raw σ).
  - `04E_inference.py:158` — unpack 4 tensors instead of 3: `gen_act, gen_home, gen_cop, gen_cop_probs = model.generate(...)`.
  - `04E_inference.py:164–166` — drop `gen_cop.cpu().numpy()`; use `gen_cop_probs.cpu().numpy()` instead.
  - `04E_inference.py:171` — `cop_k = gen_cop_probs[k].copy()` (sourced from raw σ, not binary).
  - `04E_inference.py:218` — `int(val)` → `round(float(val), 4)`.

  Downstream caveat (not a regression; logged for F3 planning): `augmented_diaries.csv` co-presence columns are now float in [0, 1] instead of int 0/1. `04I` uses `np.nanmean` → schema-compatible. `04F` validation consumes AT_HOME / activity, not cop — also compatible. **`occToBEM` may assume binary 0/1 for room-level multipliers — must binarize at the BEM-conversion boundary before any downstream BEM run.** No edit to occToBEM in this cycle; flagged for when BEM-side work resumes.

  Cluster submission (bundled, per user "upload once" rule): `scp` of the two edited files to `/speed-scratch/o_iseri/occModeling/`, then three sbatches chained via `afterok` — no 04D (checkpoint unchanged):
  - `04E=901798` (partition `pg`, GPU, ~4h) — RUNNING on `cisr-1` at submission +2m.
  - `04H=901799` (partition `ps`, 8 G, 30 min, dep on 04E) — PENDING (Dependency).
  - `04I=901800` (partition `ps`, 8 G, 30 min, dep on 04E) — PENDING (Dependency).

  Chain wrapper (`submit_step4_chain.sh`) deferred — three-sbatch manual chain sufficient for inference-only cycles; wrapper design blocked until we know whether F3 retrain is needed (depends on 04I verdict here). Post-run plan: `scp -r outputs_step4/` local, read `diagnostics_v4_actcop.json`, decide HC2 retrain vs. case-closed.

---

*End of §8 task. No grep / sbatch / diff commands executed in this planning round. First action on approval: Test 8.A — local grep of `04E_inference.py`, `04B_model.py`, and the downstream augmenter for co-presence thresholding / zero-writes.*

- **2026-04-23 (F-COP-1a verdict — F3 trigger).** F-COP-1a chain (jobs 901798/901799/901800) completed. Pulled `outputs_step4/diagnostics_v4_actcop.json`. Findings:

  **Co-presence** (`copresence_fail`): 5 of 7 auditable channels outside ±3 pp threshold. Pattern is majority-class dominance (Alone over-produced, minority channels collapsed), not HC1-style binary-zeros — this rules out HC1 as sole cause and promotes **HC2 (no `pos_weight` on COP BCE)** as the leading remaining hypothesis.
  - Alone: +16.1 pp (syn σ̄ 0.514, obs 0.353)
  - Spouse: +6.5 pp
  - friends: +3.3 pp
  - parents: +3.1 pp
  - colleagues: −4.8 pp

  **Activity** (`activity_fail`): 10 of 12 cells FAIL, JS mean 0.056. **Code 1 (Work & Related, confirmed 2026-04-23 Task 0a)** over-produced 14–15 pp in weekday strata (2005_1 obs 18 % → syn 32 %; 2010_1 obs 16 % → syn 32 %). Regression vs. pre-F1 baseline. Root cause: the F1 manual **Work ×5 boost** at `04D_train.py:384` is the prime suspect.

  **Decision:** Single-variable patches exhausted. Three symptoms (co-presence Alone dominance, activity Work over-production, AT_HOME stratum split) require coordinated HP study + statistical diagnostic battery. Moving to 5-config HP sweep. → See §9 (F3 sweep) and §10 (04J diagnostics) below.

---

## §9 — F3 Hyper-Parameter Sweep

### 9.1 Aim

Run a structured 5-configuration sweep of the Step-4 Conditional Transformer. Vary loss balance, class weights, conditioning, and data-side sampling jointly (factorial-style, not grid) to isolate causes of the three co-existing failures and identify a single winning configuration for F4/production. Validated by a new statistical diagnostic battery (04J) with bootstrap CIs, calibration curves, joint distributions, and a composite score so the winner is selected on signal, not point estimates.

### 9.2 Context — three co-existing failures (as of F-COP-1a 2026-04-23)

| Symptom | Magnitude | Leading hypothesis | Fix in sweep |
|---|---|---|---|
| Co-presence Alone dominance (+16.1 pp) + minority collapse | 5/7 channels fail | HC2: unweighted minority BCE (no `pos_weight`) | F3-A: per-channel `pos_weight` |
| Activity Work & Related over-production (+14–15 pp weekday) | 10/12 cells JS FAIL | F1 manual Work ×5 boost blowback | F3-A: remove targeted boosts |
| AT_HOME stratum split (weekday-under / weekend-over 5–14 pp) | WARN, persistent since F1 | Target-stratum conditioning ignored | F3-B/F3-C/F3-D |

### 9.3 The 5 configurations

| Tag | Short name | Delta vs. F1 | Primary hypothesis | Cluster cost |
|---|---|---|---|---|
| **F3-A** | `baseline_balanced_bce` | + class-balanced `pos_weight` on co-presence BCE (inverse-freq, 7-way); remove manual activity boosts (Work ×5, Transit ×3, Social ×2) → pure inv-sqrt-freq only | HC2 co-presence + activity Work regression | 1× 04D on `pg`, ~2 d |
| **F3-B** | `+stratum_marg` | F3-A + per-(target_cycle × target_stratum) `marg_loss` instead of global | Stratum-conditional AT_HOME bias | 1× 04D on `pg`, ~2 d |
| **F3-C** | `+aux_stratum_head` | F3-B + auxiliary MLP head predicting `tgt_strata` from decoder layer-0 hidden, λ=0.1 | Decoder ignoring target-stratum conditioning (§7.1, §7.4 persistent fails) | 1× 04D on `pg`, ~2 d |
| **F3-D** | `+data_side_sampling` | F3-B + `WeightedRandomSampler` × (`wght_per` × `strata_inv_freq`) at pair-construction time | H1 stratum bias at data source; alternative to aux head | 1× 04D on `pg`, ~2 d |
| **F3-E** | `+inference_sweep` | No retrain; best post-sweep checkpoint × {T=0.7, 0.8, 1.0} × {top-k=off, 5} | Decouple training dynamics from sampling noise | 6× 04E, ~4 h each |

**Parallelism:** F3-A/B/C/D submit simultaneously (4-GPU budget = hard cap). F3-E runs after A–D winner identified.

### 9.4 Per-config code changes (exact file:line)

**F3-A** (all subsequent configs inherit these):
- `04A_dataset_assembly.py` ~line 212: compute + save per-channel co-presence class freqs (7-way, per COP_NAMES correction) and per-activity class freqs (14-way) into `step4_feature_config.json`. Assert `pos_weight > 1` per COP channel (sign-flip guardrail).
- `04D_train.py:143–158`: add `pos_weight` tensor (from 04A outputs) to `F.binary_cross_entropy_with_logits()` call on co-presence.
- `04D_train.py:384–386`: remove `class_weights_np[0] *= 5.0`, `[12] *= 3.0`, `[8] *= 2.0`. Keep pure inv-sqrt-freq normalization (lines 377–379).
- All flags gated by env var `F3_CONFIG` ∈ {A, B, C, D} so one script serves all configs; default env (no var / F1 config) produces identical behavior to F1.

**F3-B** (inherits F3-A):
- `04D_train.py:140`: reshape `marg_loss` from global `home_tgt.mean()` to per-(target_cycle × target_stratum) marginals. Activated when env `MARG_MODE=per_cs`.

**F3-C** (inherits F3-B):
- `04B_model.py`: add optional auxiliary stratum-prediction MLP head reading decoder layer-0 hidden. Gated by env `AUX_STRATUM_HEAD=1`.

**F3-D** (inherits F3-B, not F3-C):
- `04C_training_pairs.py:90–144`: confirm `strata_inv_freq` saved to disk (`np.save` at line 144 if missing).
- `04D_train.py:405–409`: extend `WeightedRandomSampler` to multiply by `wght_per × strata_inv_freq` when env `DATA_SIDE_SAMPLING=1`.

### 9.5 Sweep infrastructure

- `2J_docs_occ_nTemp/Speed_Cluster/submit_step4_F3_sweep.sh` — single-command entry. Submits 4 × `job_04D_train_F3<tag>.sh` in parallel; per-config chain: `04D → 04E → {04F, 04H, 04I, 04J}` (fan-out post-04E via `afterok`). After all 4 chains complete, submits `job_04Z_F3_compare.sh` (CPU, `ps`) → `F3_sweep_ranking.md`.
- `2J_docs_occ_nTemp/Speed_Cluster/job_04D_train_F3{A,B,C,D}.sh` — 4 files, each sets its env vars and calls `04D_train.py`.
- `2J_docs_occ_nTemp/Speed_Cluster/job_04Z_F3_compare.sh` — reads 4 × `diagnostics_v4_statistical.json` + F1 baseline, emits ranking + HTML.
- `2J_docs_occ_nTemp/04Z_F3_compare.py` — comparison logic.
- Outputs isolated under `deliveries/F3_sweep/<tag>/` — never write into shared `outputs_step4/` (Option-B-v2 clobber lesson). F1 `best_model.pt` must be copied to `deliveries/F1_baseline/checkpoints/best_model.pt` before submission.

### 9.6 Cluster constraints

- 4 GPUs max per user on `pg` partition; 7-day wall-time max. Submit all 4 retrains simultaneously as one `submit_step4_F3_sweep.sh` call so SLURM batches atomically.
- Login node (`speed-submit2`) is submission-only — no compute, no interactive builds.

### 9.7 Expected result

At least one config passes all three diagnostic verdicts simultaneously:
- `copresence_ok` (max_gap_pp < 3.0 pp across 7 channels)
- `activity_ok` (JS mean < 0.05 across all 12 cells)
- AT_HOME gap < 5 pp per stratum (weekday and weekend)
Composite score from 04J strictly better than F1 baseline on all four component metrics.

### 9.8 Test method (go/no-go gate)

1. **04J dry-run gate (before sweep submission):** Run 04J on existing F1 `augmented_diaries.csv`. Gate: Alone calibration curve must show σ̄ ≈ 0.51 in the σ∈[0.5, 0.6) bin with empirical prevalence ≈ 0.35 (confirming 04J reads the F-COP-1a soft probabilities correctly). If not, 04J is buggy — fix before submitting sweep.
2. **Per-config smoke test:** `python -c "import 04D_train"` under each env-var combo before submission; 1-epoch mini-train on CPU to confirm different loss logs per config (proves env-flag plumbing).
3. **Sweep verdict:** all 4 retrains `COMPLETED ExitCode=0:0` per `sacct`; `F3_sweep_ranking.md` present; winner identified by composite score.
4. **HTML-report sanity:** for each `<tag>/step4_validation_report.html`, `head -c 200` must start with `<!DOCTYPE html` or `<html` — if it starts with `{`, the known 04F HTML clobber bug hit; re-run 04F alone for that tag.

### 9.9 Risks

- **R1. Activity regression overshoots.** If removing Work ×5 under-produces Work in F3-A, fall back to Work ×2 in F4-A. Document threshold.
- **R2. F3-C and F3-D test the same axis.** If both pass, prefer F3-D (data-side) for interpretability; keep aux head as F4 backup.
- **R3. GPU budget contention.** 4-way parallel covers the hard cap; if a 5th config is needed, it queues behind.
- **R4. 04J bugs block sweep.** Dry-run-first is the containment. Budget 1 day for 04J debug before sweep submission.
- **R5. BEM binarization.** `augmented_diaries.csv` co-presence columns are float σ post-F-COP-1a. `occToBEM` likely assumes binary. Not addressed in F3; must binarize at BEM-conversion boundary when BEM-side work resumes.

### 9.10 Progress Log

---

## §10 — 04J Statistical Diagnostics

### 10.1 Aim

Implement `04J_statistical_diagnostics.py` — a CPU-only diagnostic layer that augments the existing 04H (AT_HOME) and 04I (activity + co-presence) marginal checks with **statistical significance tests, calibration analysis, and joint distribution checks**. Dry-run on F1 data to establish a reference baseline before any F3 retrain. Use 04J output as the primary sweep-ranking metric for F3.

### 10.2 Inputs / outputs

**Inputs (same as 04H/04I):**
- `outputs_step4/augmented_diaries.csv` — generated by 04E
- `outputs_step3/hetus_30min.csv` (or equivalent reference frame used by 04H/04I)
- `outputs_step4/step4_feature_config.json`

**Outputs:**
- `outputs_step4/diagnostics_v4_statistical.json` — all 5 test outputs, composite score, pass/fail per metric
- `outputs_step4/diagnostics_v4_calibration.png` — calibration curves per co-presence channel + AT_HOME (8 panels)
- `outputs_step4/diagnostics_v4_joints.png` — joint obs-vs-syn heatmaps for (activity × AT_HOME), (activity × Alone), (Alone × AT_HOME)
- `outputs_step4/diagnostics_v4_bootstrap.png` — bootstrap CI bar charts for co-presence and AT_HOME gaps

### 10.3 The 5 tests

| Test | Implementation | Output field |
|---|---|---|
| **T1: Bootstrap CIs** on every prevalence gap (co-presence, activity, AT_HOME) | 1000 bootstrap resamples via `np.random.choice`; 2.5/97.5 percentile CI; flag "statistically real" if CI excludes 0 | `bootstrap_cis` dict per channel per (cycle × stratum) |
| **T2: Calibration curves** per co-presence channel + AT_HOME | Bin raw σ into 10 equal-width bins [0, 0.1), …, [0.9, 1.0]; compute empirical prevalence per bin; mean absolute error vs. perfect calibration diagonal | `calibration_mae` per channel; PNGs |
| **T3: Joint distributions** (activity × AT_HOME), (activity × Alone), (Alone × AT_HOME) | `pd.crosstab(obs, syn)` normalized; χ² of independence between obs and syn joint; Cramér's V for effect size | `joint_chi2`, `joint_cramer_v` per pair |
| **T4: χ²/KS per (cycle × stratum × class)** | `scipy.stats.chisquare` on activity counts; `scipy.stats.ks_2samp` on continuous σ distributions; Bonferroni-corrected α = 0.05 / (n_cells × n_classes) | `chi2_results`, `ks_results` dicts |
| **T5: Composite score** `S` | Weighted sum (see §10.4); lower is better | `composite_score` scalar |

### 10.4 Composite score formula (pinned, no post-hoc tuning)

```
S = w1 * AT_HOME_gap_rms  +  w2 * cop_max_gap_pp  +  w3 * act_JS_mean  +  w4 * cop_calibration_MAE

w1 = 0.20   (AT_HOME gap RMS across (cycle × stratum), normalized to pp/10)
w2 = 0.35   (max co-presence gap in pp, normalized /10)
w3 = 0.35   (activity JS mean × 10, so 0.05 JS = 0.5 in normalized units)
w4 = 0.10   (mean co-presence calibration MAE across 7 channels, ×10)
```

All four components are scaled so a unit change represents a ~10 pp gap or ~0.01 JS movement — comparable magnitudes. The F1 baseline composite score (from dry-run) becomes the reference floor for sweep ranking.

### 10.5 CLI contract

```
python 04J_statistical_diagnostics.py \
    --data_dir outputs_step4 \
    --ref_csv outputs_step3/hetus_30min.csv \
    --output_json outputs_step4/diagnostics_v4_statistical.json \
    --n_bootstrap 1000
```

Default paths resolve relative to the script's `SCRIPT_DIR` (mirrors 04H/04I pattern). Partition: `ps` (CPU); 4 cores, 8 G, 30 min wall.

### 10.6 Gate (dry-run on F1 data)

Must pass before sweep submission: the Alone calibration curve must show σ̄ ≈ 0.51 bin (σ ∈ [0.5, 0.6)) with empirical prevalence ≈ 0.35. This confirms 04J is reading the F-COP-1a soft probabilities correctly. If the curve is flat or shows a binary spike at 0.0/1.0, 04J is reading pre-F-COP-1a binary co-presence columns — fix the CSV path or column dtype before proceeding.

### 10.7 Progress Log

---
