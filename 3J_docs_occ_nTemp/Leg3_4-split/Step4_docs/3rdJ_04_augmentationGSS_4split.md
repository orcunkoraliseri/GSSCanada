# 3rdJ Step 4 — Occupancy Diary Augmentation (Leg-3 Four-Channel Split)
### Three-GSS-head conditional Transformer — add Head 3 (AT_RETAIL) to the locked Leg-2 backbone under the FROZEN dr_L3-08/11/12/13 regimen. Hotel never enters this model.

---

## Progress Checklist

- **Build**
  - [x] 04A assembly extended (aux_seq 11→12, retail_avail mask)
  - [x] 04B model: `retail_head` added (`JSeriesHybrid4Split`)
  - [x] 04D train: fixed-α scalarization + PCGrad + two-phase schedule
  - [x] 04E inference: −ln 49 logit shift + min-dwell decode + exclusivity projection
  - [ ] 04L rake: 3-channel exclusive joint rake
  - [ ] 04T act-rake: 4-way state (WORK/HOME/RETAIL/NEITHER)
  - [ ] Validator: RW gates + ISR + regression gates
- **Runs**
  - [x] Local smoke (all stages)
  - [x] Cluster: warmup (submitted, job 1127956 — awaiting manager review of .out)
  - [ ] Cluster: joint fine-tune (5 seeds) — BLOCKED on warmup .out review
  - [ ] Ablation (≤ 4 runs: shared / LoRA / semi-shared / reserve)
  - [ ] Gate-first selection → lexicographic (max retail F1) → LOCK
- **Post-hoc chain**
  - [ ] 04L 3-channel rake → 04M min-dwell → 04T 4-way act-rake → final pool + val report

### Task Tracker — G3-fix / W3 remediation (Step-4 reopen, 2026-07-21)

Colleague co-presence W3 gate FAIL (7.19pp WD vs ≤3.0pp; worst slot 16:30) traced to a global-quantile-only G3 binarization in `3rdJ_04E_inference_4split.py` — no day-type/slot shape control. Fix = per-(day-type×slot) threshold with min-support fallback (constants 200/20/50). Regen-fixable (04E→04L→04M→04T re-cascade), no retrain. **Baseline dirs `seed_3*`/`seed_3_raked3*` are PRESERVED; all fixed work lands in `_g3fix` dirs.**

- **Stage 1 — code fix + local smoke** ✅ DONE
  - [x] 04E G3 block → per-(day-type×slot) threshold, constants 200/20/50; predecessor archived
  - [x] `py_compile` clean; local smoke OK; only-cop-changed invariant `np.array_equal`=True; per-slot branch exercised; constants reverted to prod
- **Stage 2a — determinism probe** ✅ DONE (job 1128526, COMPLETED exit 0)
  - [x] Twice-over 04E on real `seed_3` checkpoint → act/hom/wrk/ret all **EQUAL** run-to-run → only-cop premise HOLDS
- **Stage 2b — full 04E re-run + rake re-cascade** ✅ DONE (W3 PASS 0.0030pp; cluster, prompt `prompt-manager/2026-07-21_leg3_step4_stage2b_04E_rerun_recascade.md`)
  - [x] Archive cluster 04E + scp patched 04E (constants 200/20/50 confirmed; md5 `cdf32d1…`)
  - [x] Full 04E on `seed_3/checkpoints/best_model.pt` → `outputs_step4/seed_3_g3fix/` (job 1128564, COMPLETED 00:37:15)
  - [x] **FULL-POOL determinism guard** → **NO-GO**: act30/hom30/ret30 **DIFF**, wrk30 EQUAL; cop 2.64% cells differ. Rake cascade NOT run (halted at gate, correct).
    - ⚠️ Guard measures patched-run-NOW vs historical `seed_3` (generated on a *different node/day*). G3 patch is post-hoc binarization (no RNG) → cannot shift act/hom/wrk/ret sampling → the DIFF is **cross-node GPU nondeterminism**, not the fix. Stage-2a probe (run-A vs run-B, same job) was EQUAL = within-node determinism only.
    - → Diagnostic job **1128576** (`ps`, COMPLETED) quantified the divergence: **act30 19 cells / hom30 5 / wrk30 0 / ret30 1 — ~25 cells out of 9.2M per channel, 4 rows / 192,183 total; NaN-mask identical; DDAY_STRATA + IS_SYNTHETIC positionally aligned 1:1.** Textbook cross-node `torch.multinomial` float-boundary noise, NOT the fix. Guard NO-GO = false alarm in substance.
    - **DECISION (user-confirmed 2026-07-21): accept the `seed_3_g3fix` pool WHOLESALE** (not copy-passthrough). Rationale = internally consistent (co-presence conditioned on its OWN activities, zero splice artifact), activities 99.9998% identical to `seed_3`, honest provenance = most-precise option. The exact-byte "only-cop-changed" premise is superseded by a documented ~0.0002% activity-noise reframe (evidence-based, gate not silently relaxed). Downstream activity re-validation is trivial.
  - [x] 04L → `sweep/seed_3_g3fix_raked3/` → 04M → `..._mindwell/` → 04T → `..._mindwell_actv/` — dependency chain **submitted** (jobs 1128577→1128578→1128579), co-presence passes through 04L/04M/04T untouched
  - [x] Step-4 validation + **W3 efficacy** — job **1128580** (COMPLETED). Step-4 validator = **147 PASS / 18 WARN / 1 FAIL** (the 1 FAIL = **OW5**, pre-existing in Leg-2 baseline; REG-4 PASS = no NEW fail → pool sound). **W3: 7.19pp → 4.8776pp WD — improved 2.3pp but STILL FAIL (>3.0pp).**
  - [x] **W3 residual diagnosed (job 1128599 decomp) — NOT a co-presence-shape problem; it is an EXPOSURE (NaN-structure) mismatch:**
    - `colleagues30` is coded NaN off-work in OBS but the synthetic head emits a value at EVERY slot. Decomp on the g3fix `_actv` pool: **SYN WD exposure(non-null)=100.0% vs OBS 46.4%**; **conditional-among-non-null SYN 9.101% vs OBS 9.096% (gap 0.005pp — the per-slot fix is PERFECT).** W3 `fillna(0)` marginal = exposure×conditional → 100/46.4 ≈ 2.15× inflation ⇒ 9.10% vs 4.22%.
    - Counterfactual: **if exposure matched, WD gap = 0.0022pp (clean PASS)**; if only conditional matched, 4.8729pp (no help). The 8 dense co-presence channels (Alone/Spouse/…) already match at aggregate (their obs exposure ≈100% too) — only `colleagues30` is sparse-observed.
    - Mask-rule check (job 1128601) **refuted the off-work-mask hypothesis**: OBS `colleagues30`-nonnull=46.4% but `wrk30==1`=15.2% (P(at-work|coded)=13.8%) → colleagues is *coded* whenever active/awake (~46%), NOT only at work. Masking by `wrk30` would over-mask. BUT it exposed the true root cause ↓.
    - **ROOT CAUSE (real fix): the per-slot binarization targeted the WRONG denominator.** 04E L590 used `p_obs_j = n_pos_j / n_obs_j` (**conditional** = positives/non-null), but the W3 gate measures `col.fillna(0).mean()` (**marginal** = positives/ALL rows). The dense synthetic head then fired at the 9.10% conditional rate across *all* slots → marginal 9.10% vs obs 4.22%. The same fix's pooled fallback (L562 `np.nanmean(obs==1)`) already used the marginal → per-slot & fallback were **inconsistent**. Only `colleagues` bit (sparse-observed); the 8 dense channels have non-null≈100% so marginal≡conditional (unaffected).
    - **FIX (user-approved "most-precise", 2026-07-21): 04E L590 denominator non-null → all-rows marginal** (`n_all_j = obs_col.shape[0]; p_obs_j = n_pos_j / n_all_j`). By construction syn marginal = obs marginal *per slot* → W3 → ~0 AND diurnal shape (16:30 peak) matches. One-line change; predecessor archived `archive/3rdJ_04E_inference_4split.py.20260721_perslot_conditional`; `py_compile` OK; scp'd (cluster L597). Requires 04E re-run (raw scores overwritten at binarization).
  - [x] **Re-run chain 2** (marginal-target): 04E **1128606** → 04L 1128607 → 04M 1128608 → 04T 1128609 → val+W3 **1128610** — all COMPLETED exit 0 (2026-07-21 13:44).
  - [x] **W3 efficacy — PASS.** BEFORE `seed_3_raked3_mindwell_actv`: WD 7.1862pp / WE 0.7540pp → **W3 7.1862pp FAIL**. AFTER `seed_3_g3fix_raked3_mindwell_actv`: WD syn=4.2261% vs obs=4.2232% = **0.0030pp** / WE syn=1.2740% vs obs=1.2723% = 0.0017pp → **W3 0.0030pp PASS** (gate ≤3.0pp). Marginal-denominator fix landed the per-slot target exactly as the decomp predicted (counterfactual said 0.0022pp; got 0.0030pp). Only `colleagues30` touched; 8 dense channels unchanged; diurnal shape preserved.
  - [x] Step-4 validator (job 1128610) = **147 PASS / 18 WARN / 1 FAIL**; sole FAIL = **OW5** (day-type ordering, pre-existing in Leg-2 baseline; **REG-4 PASS** = `current fails ['OW5'] == baseline fails ['OW5']` → no NEW fail introduced by g3fix).
  - [x] scp fixed pool artifacts local — W3_EFFICACY.txt + step4_validation_report.{html,txt} synced to `outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/`. **418 MB `augmented_diaries.csv` NOT yet pulled** (held for Stage-3 greenlight — Step-5 reads it locally).
- **Stage 3 — Step-5 re-run on fixed pool** ⏳ PENDING (manager-gated; do NOT auto-advance — awaiting user checkpoint)
  - [ ] Re-run Step-5 chain on `seed_3_g3fix_raked3_mindwell_actv/` with batched fixes (LFTAG census `99→NaN`; R1→WARN/documented; PR=6→documented frame gap)
  - [ ] Re-validate Step-4 AND Step-5 → target 0 new FAIL
- **Stage 4 — close Step 5** ⏳ PENDING
  - [ ] Progress Log with re-derived frame counts (HH-ID sets) + Cluster A/B/C dispositions; update auto-memory; report before Step 6

## Goal

Extend the locked Leg-2 two-head model to **three GSS heads** by grafting an AT_RETAIL binary head onto the shared encoder. The backbone verdict is **AUGMENT** (dr_L3-11): keep the multi-head conditional Transformer (J3 lineage); no 2023–2026 challenger (MDLM/SEDD discrete diffusion, decoder-only AR, SSM/Mamba, flow matching, non-AR iterative) passes our gates at our scale — the Leg-2 MDLM rejection stands (8–16× inference overhead + dwell-time decay flicker on a ~2 %-positive channel). Keep-*unchanged* is equally rejected: plain BCE would ship a **dead retail head** (an all-zeros head passes bare JS at 0.010 bits — the toothless-gate finding, dr_L3-08).

**Everything below is FROZEN by the 2026-07-02 design freeze (OD-10/13/14/15). This is a config-and-discipline change, not new machinery.** The hotel channel bypasses this model entirely (population-aggregate series, no respondents — Step 6 side-track).

## Reference

- Pipeline: `../3rdJ_00_4split_Occupancy_Pipeline.md` — STEP 4 (architecture, freeze blocks (a)–(d), retail diurnal targets)
- Deep research (all RESOLVED 2026-07-02): `../deepResearch/dr_L3-08_rare_head_extension_REPORT.md` (recipe), `dr_L3-11_architecture_pressure_test_REPORT.md` (AUGMENT), `dr_L3-12_output_representation_REPORT.md` (binary heads + projection), `dr_L3-13_training_regimen_REPORT.md` (regimen playbook), `dr_L3-06_retail_diurnal_targets_REPORT.md` (validation targets)
- Leg-2 counterpart (template + locked base): `../../Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS.md` + the 04A–04T script family
- Inputs: `../Step3_docs/outputs_step3/` (Leg-3: adds `retail_30min.csv`)

## Data Source Inventory

| Artifact | Key columns | Role |
|---|---|---|
| `hetus_30min.csv` | 48 act30 + 48 hom30 + conditioning + weights + DDAY_STRATA + PR | ✅ bit-identical to Leg 2 |
| `copresence_30min.csv` | 9 × 48 co-presence | ✅ bit-identical to Leg 2 |
| `work_30min.csv` | WORK30_001..048 | ✅ bit-identical to Leg 2 |
| `retail_30min.csv` | RETL30_001..048 | ⚠️ NEW (Leg-3 Step 3) |

Conditioning **unchanged from Leg 2** (dr_L3-13): demographics embeddings (AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, HRSWRK, NOCS, COW, ATTSCH, POWST, TOTINC), `DDAY_STRATA` `nn.Embedding(3, d_model)`, **CYCLE_YEAR continuous projection** `(year − 2005)/25 → nn.Linear(1, d_model)` (never categorical — 2030 must extrapolate), `COLLECT_MODE` low-capacity `nn.Embedding(2, 16)` (confound control, too small to leak), NAICS/TELEWORK/WORK_SCHEDULE office set. **No retail-specific conditioning is added** — retail presence is population-behavioural, not occupation-gated.

## Proposed Changes (Leg-3 Deltas)

### Delta A — Assembly (04A): third binary channel

- `aux_seq (n,48,11) → (n,48,12)` = `[AT_HOME | AT_WORK | AT_RETAIL | 9 × co-presence]`
- `retail_avail (n,48) bool` mask mirroring `work_avail`
- `step4_feature_config.json` records the new width; CONTRACT section below updated accordingly.

### Delta B — Model (04B): `retail_head`

`JSeriesHybrid4Split` = `JSeriesHybrid2Split` + `retail_head = Linear(d_model, d_model) → Tanh → Linear(d_model, 1)` off Arm-2's fused representation (mirrors `work_head`; the AR-arm `detach()` barrier is untouched). `generate()` gains `retail_sigmoid` in its extended return tuple (backward-compatible kwarg, as `return_hw_probs` was).

### Delta C — Loss (04D): logit-adjusted class-weighted BCE on Head 3

- `BCEWithLogitsLoss(pos_weight = 49)` (≈ N_neg/N_pos at ~2 % positive).
- **Inference logit shift**: `logit_calibrated = logit_raw − ln 49` (≈ 3.89), then sigmoid — mathematically exact calibration under imbalance (Menon et al. 2020). Applied in 04E, **never during training**.
- **No retail-diary oversampling** — it shifts the prior and silently invalidates the −ln 49 correction (double-correction risk, dr_L3-13).
- Auxiliary consistency loss (soft penalty on `P(home)+P(work)+P(retail) > 1`) — training-side support for the exclusivity projection; small weight, off by default in Phase 1, on in Phase 2 (env knob `LAMBDA_EXCL`, default 0.05, ablatable within the reserve run).

### Delta D — Loss balancing: FIXED α + PCGrad (⚠️ change vs Leg 2)

**Unitary scalarization, α_resid : α_work : α_retail = 1.0 : 0.5 : 0.3** + PCGrad pairwise across the task set + the diversity-preserving loss retained from Leg 2. **The Leg-2 dynamic weighter (`WEIGHT_MODE=uw`/SLAW) does NOT survive the third head** — dr_L3-13 Table 1: dynamic weighters destabilize when one task is ~2 %-positive (mostly-zero losses → near-zero loss variance → weight spikes → gradient noise into the shared encoder); well-tuned fixed weights match or beat them at 2–4 tasks (Kurin et al. 2022). Implement as `WEIGHT_MODE=fixed` with `ALPHAS=1.0,0.5,0.3` (cop folded under the resid group as in Leg 2). **Never SLAW / UW / GradNorm / DWA / CAGrad.**

### Delta E — Two-phase schedule (dr_L3-08, FROZEN)

| Phase | Epochs | Trainable | lr | Notes |
|---|---|---|---|---|
| 1 — Head-only warmup | **5** | Head 3 only (encoder + Heads 1–2 + cop head frozen) | **1e-3** AdamW | random-init retail head learns on a frozen representation |
| 2 — Joint fine-tune | **15** | all parameters | **1e-4** AdamW | PCGrad ON; fixed α; early stopping on the gate set (patience 10), never on training loss |

- **Warm-start source:** the Leg-2 production checkpoint behind the current locked pool (`R5_raked_mindwell_actv2` lineage — resolve the exact `best_model.pt` from the pool's provenance JSON at build time and record it here; rebuild the model from the checkpoint's stored `model_config`, the Leg-2 warm-start lesson).
- Stratified batch composition (50 % weekday / 25 % Sat / 25 % Sun) + inverse-cycle-frequency weighting during joint training (2022 has the fewest diaries).
- `WGHT_PER` inside the loss, clipped at the 99th percentile.
- Regularization: dropout 0.1 (attention/residual only — **never on output projections**), weight decay 1e-4 (AdamW). **Label smoothing = 0**; **no diary augmentation** (slot jitter / cyclic shifts corrupt circadian synchronization) — dr_L3-13 mistakes #3/#4.
- Scheduled sampling **dropped** (dr_L3-11 ranked it, dr_L3-13 rejects it at 48-slot length; flicker is handled at decode time).

### Delta F — Decoding (04E)

1. AR activity arm: **temperature 0.7 + nucleus p = 0.9** (dr_L3-13 frozen choice; note the Leg-2 sweep locked T = 0.8 without nucleus — if Heads-1/2 regression gates trip on the decode change alone, escalate to the user rather than silently reverting).
2. **Minimum-dwell constraint ≥ 2 slots (60 min) for work + retail events** — the flicker countermeasure (rare states must not be emitted as single-slot blips).
3. Retail logit shift **−ln 49** → calibrated sigmoid.
4. **Exclusivity projection** (Delta G).
5. Post-hoc raking chain (Delta H).

### Delta G — Decode-time exclusivity projection (dr_L3-12, FROZEN)

- Per-head decision thresholds **θ_home = 0.50, θ_work = 0.40, θ_retail = 0.15** (F1-derived on validation; recalibrate if 2030 scenario distributions drift).
- A slot with > 1 channel over threshold keeps only `c* = argmax_c p_c(t) / θ_c` (threshold-normalized argmax — lets the rare channel compete fairly).
- Calibration untouched: training never sees the constraint; conflicts are rare (< 5 % of slots); marginals stay individually calibrated (loss-penalty and grouped-softmax alternatives both bias marginals — dr_L3-12 Table 2).
- **ISR (Impossible-State Rate)** = share of generated slots with > 1 of {AT_HOME, AT_WORK, AT_RETAIL} active. Raw model outputs: **ISR ≤ 0.5 %** (hard gate — evidence the encoder learned the negative location correlation). Final injected schedules: **ISR = 0 %** by construction.
- The categorical-location-head alternative is **rejected** (softmax competition crushes the ~2 % class, couples calibration, breaks Head-1 bit-compatibility); hierarchical two-stage rejected on stage-1 error cascade. OD-1's gated OR-rule means `AT_HOME ∧ AT_RETAIL` is **not** a legitimate overlap → the projection covers the full three-channel set, no exemptions.

### Delta H — Post-hoc chain: 3-channel rake + min-dwell + 4-way act-rake

- **04L joint rake → 3-channel exclusive.** The greedy per-slot channel assignment generalizes from {home, work} to {home, work, retail} with a third priority tier in the `--floating_aware` sort-key mechanism; quota counts (`n_home`/`n_work`/`n_retail`) exact per (cycle × stratum) cell. Raking operates on the **calibrated** probabilities (dr_L3-08: rake after logit shift).
- **04M min-dwell**: extend to `ret30` (merge 1-slot blips) — same script, one more channel column.
- **04T act-rake → 4-way state**: the conditional act30 re-rake's state machine WORK/HOME/NEITHER becomes **WORK/HOME/RETAIL/NEITHER** (retail-positive slots map to the shopping-compatible activity categories). The GA (floating) and GB (flicker) gates extend to the 3-way occupancy set.
- Lock naming convention: `outputs_step4/sweep/<BASE>_raked3_mindwell_actv/` for the production pool.

### Delta I — Ablation budget: HARD CAP 4 runs (dr_L3-13)

Everything above is fixed by citation; the single ablation worth its cost is **shared-vs-separate backbone**:

| Run | Config |
|---|---|
| 1 | Fully shared 6-layer encoder (incumbent) |
| 2 | Frozen Leg-2 encoder + LoRA adapters (r = 8) + Head 3 (zero old-head degradation by construction) |
| 3 | Semi-shared (layers 1–5 shared, layer 6 split per task) |
| 4 | Reserve (seed/debug/`LAMBDA_EXCL` check) |

**No hyperparameter sweeps beyond this.** The Leg-1/Leg-2 lesson stands: calibration-not-architecture; 40+ topology trials bought nothing — post-hoc raking did.

### Checkpoint selection — gate-first → lexicographic (dr_L3-13, FROZEN)

Keep only checkpoints passing **every hard gate** (ΔJS ≤ 0.002 bits on Heads 1–2, ISR ≤ 0.5 %, PR-AUC ≥ 0.15 ∧ F1 ≥ 0.25, midday error ≤ 3.0 pp, transitions ≥ 0.05/day), then **maximize retail F1** among survivors. Early stopping on the gate set (patience 10). Report **mean ± sd over 5 seeds** (normal: 1–2 % sd on F1/PR-AUC, 0.001–0.002 bits on JS). Never a single composite score (the Leg-1 lesson; `val_score` retained only as a logging curiosity, not for selection).

> 🔴🔴 **THE SHIPPED ARTEFACT WAS NOT SELECTED BY THE RULE ABOVE — recorded 2026-08-06 (V3-H1, option C).**
> **The rule above is NOT amended. It stays the specification, and the Leg-1/Leg-2 "never a single
> composite score" lesson stays with it.** What is recorded here is that the shipped pool deviates
> from it, knowingly, with the reason — because rewriting the rule to describe what the code does
> would delete a principle that three documents carry (the Leg-1 lesson, `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md:262`
> *"Pareto model selection, never composite — the Leg-1 composite chose a 2/4-gate model"*, and
> dr_L3-13 here), and would do it at the moment it is inconvenient.
>
> **What actually selected the shipped weights.** `3rdJ_04D_train_4split.py:881` saves
> `best_model.pt` on `val_score = mean_js + 0.5·(home_gap + work_gap + retail_gap)/3` (`:499`) —
> a composite containing **neither `pr_auc` nor `f1`**. The two rules pick different epochs in **4 of
> 5 seeds**; seed 3 ships as the **argmin of the composite** (1st of 5 on `val_score`, 4th of 5 on
> the metric this section names). Gap to the documented rule's global winner (seed 0, epoch 15):
> **+0.0218 retail F1**, 5.6 % relative, **0.16 sd** of the cross-seed spread.
>
> **Why it was not re-selected (the reason, not the cost).** Both rules rank epochs on the
> **teacher-forced** `pr_auc`/`f1` columns of the training log, and **V2-E1 + V3-J1 showed those
> numbers are blind to person-level retail skill**: all ten RW/RETM gates are byte-identical on a
> pool whose retail vectors have been permuted between people, and the person-level gate RW9 reads
> **+0.0179** against a 0.10 bar on the shipped pool. Re-selecting would buy +0.0218 of a statistic
> already shown not to measure the thing. *Cost is the weaker argument and is not the one on record*
> — and it is smaller than v2 claimed: epoch 15 is the **final** epoch and `:876` writes
> `last_checkpoint.pt` every joint epoch, so "fix the code" is one inference + rake cascade, not five
> retrainings. The expensive part is the Step 5→9 re-cascade, which reopens a frozen deliverable.
>
> **Second reason, stated because it constrains any future attempt:** the documented rule was
> **never implementable as written**. Two of its five hard-gate families (midday error, transitions)
> are **pool-level** — computable only after inference + rake + validator, absent from all 21 training-log
> columns — so evaluating its own first clause costs **75 inference+rake cascades**. On this data the
> clause is also **inert**: over all 75 epochs min `pr_auc` **0.518213** (bar 0.15), min `f1`
> **0.282362** (bar 0.25), max `isr_raw` **0.014245 %** (bar 0.5), so *survivors → argmax F1* reduces
> to **global argmax F1**. Anyone implementing this rule must first make its first clause affordable
> or drop it explicitly.
>
> 🔴 **REOPEN TRIGGER (this is the operative half of option C).** This entry is superseded and the
> code fix is back on the table **if any one of these becomes true**:
> **(T1)** a **person-level** gate — RW9 or a successor — ranks the five seeds and the ranking
> disagrees with `val_score`'s; **(T2)** the retail F1 gap between the two rules exceeds **1 sd** of
> the cross-seed spread (today 0.16 sd); **(T3)** Steps 5→9 are reopened for any other reason, at
> which point the re-cascade is no longer a cost this decision has to carry.
> *A decision without a trigger is a decision that gets re-litigated in four weeks — which is what
> happened to R1 between 2026-07-21 and 2026-08-05.*
>
> Evidence and the per-seed table: `improvements/v3/3rdJ_L3_v3_implementation.md` §0.1 / §2.1,
> reproduction command in its appendix A1; the five training logs are in
> `improvements/v3/e4_seed_logs/`.

## CONTRACT — shared schema across Step-4 files (Leg-3 revision)

- `aux_seq (n,48,12) float32` = `[AT_HOME | AT_WORK | AT_RETAIL | 9 cop]`; `retail_avail (n,48) bool`
- Forward outputs: `act_logits (B,48,14)`, `home_logits (B,48)`, `work_logits (B,48)`, `retail_logits (B,48)`, `cop_logits (B,48,9)`
- Checkpoint dict adds `retail_gap`, gate-set metrics, and the frozen `alphas`
- Inference CSV (`augmented_diaries.csv`) adds `ret30_001..048` next to `hom30/wrk30` (naming: lowercase `ret30_*` for the diary pool — the Step-3 tiler columns stay `RETL30_*`; keep the Leg-2 naming-collision warning in mind: tiler vs pool prefixes are different namespaces)

## Retail diurnal targets (validation targets, NOT training inputs — dr_L3-06)

| Quantity | Target |
|---|---|
| Weekday 12:00–14:00 rate | **0.06–0.10 CONFIRMED** (central ≈ 0.079) |
| Saturday 13:00–16:00 peak | **0.09–0.12** |
| Sunday Calgary/AB | 0.06–0.10 · window 12:00–16:00 |
| Sunday Montreal/QC | 0.04–0.07 · compressed 12:00–17:00 (trading-hours regulation) |
| Night 00:00–05:00 | 0.000–0.003 |
| All-day episode-time share | ~2.1–2.3 %, stable across cycles |

## Module Structure Summary

```
3rdJ_04A_assembly_4split.py      (Delta A)
3rdJ_04C_pairs_4split.py         (port — K=5 pairing unchanged)
3rdJ_04B_model_4split.py         (Delta B — JSeriesHybrid4Split)
3rdJ_04D_train_4split.py         (Deltas C/D/E — fixed-α, PCGrad, two-phase; knobs:
                                  --phase {warmup,joint}, --alphas, --retail_pos_weight 49,
                                  --warm_start <leg2_ckpt>, --lambda_excl, --seed)
3rdJ_04E_inference_4split.py     (Deltas F/G — T0.7+nucleus0.9, min-dwell, −ln49, projection)
3rdJ_04L_joint_rake_4split.py    (Delta H — 3-channel exclusive, --floating_aware 3-tier)
3rdJ_04M_mindwell_4split.py      (Delta H — + ret30)
3rdJ_04T_act_rake_4split.py      (Delta H — 4-way state; fork the Leg-2 04T incl. its NaN-LFTAG
                                  pool-up + byte-identity RuntimeError guard) + _test.py
3rdJ_04P_discordance_4split.py   (diagnostic — 4-way decomposition AT-WORK / TELEWORK /
                                  RETAIL-incompatible / FLOATING; the GA-3 before/after evidence tool)
3rdJ_04_augmentationGSS_4split_val.py   (val doc's gate battery)
3rdJ_s4_4split_{train,valonly,warmup,joint,ablate_lora,ablate_semi,rake,seedN}.sh
outputs_step4/                   (tensors, checkpoints, sweep/<variant>/, final pool)
```

## Expected Result

- 5-seed joint fine-tune completes; ≥ 1 checkpoint survives the full hard-gate set.
- Locked pool `augmented_diaries.csv` with `ret30_*`: retail diurnal targets hit per cycle × day-type; Heads 1–2 within ΔJS ≤ 0.002 bits of the Leg-2 baseline; ISR = 0 % post-projection; GA/GB extended gates PASS.
- Scorecard target: all RW + regression gates PASS; OW5 remains the known non-blocking Leg-2 FAIL (unobservable-by-design) — do not chase it.

## Test Method

1. Local smoke each stage (`--smoke`): assembly shapes, one warmup epoch, one joint epoch, inference on a sample, projection ISR = 0.
2. Cluster (on the cluster, single line each; GPU partition): `sbatch -p pg --gres=gpu:1 --mem=32G -t 7-00:00:00 3rdJ_s4_4split_train.sh` — **sbatch only; 7-day walltime floor; never poll — read the .out after completion.**
3. Validator per candidate (`3rdJ_s4_4split_valonly.sh`), then the 04L→04M→04T chain on the winner, then final validator run on the locked pool.
4. The training wrapper does **not** auto-run the validator (Leg-2 gotcha) — every variant needs an explicit valsweep submit.

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description>`, job IDs, before/after tables; archive every edited script to `archive/<name>.<date>.py` first)*

### 2026-07-19 — 04A/04B/04C foundation built + smoked

Built the deterministic, non-GPU Step-4 foundation only (04D/04E/04L/04M/04T explicitly NOT touched). All three files are new (no archival needed). Leg-2 sources (`3rdJ_04{A,B,C}_*_2split.py`) were read-only templates, not modified.

**Files created** (`Leg3_4-split/Step4_docs/`):
- `3rdJ_04A_assembly_4split.py` — clone of Leg-2 04A + Delta A (retail_30min.csv read, `build_retail_track()` mirroring `build_work_track()`, `retail_avail` mask, `retail_pos_weight` in feature config, paths repointed to Leg-3 Step3/Step4 dirs).
- `3rdJ_04B_model_4split.py` — clone of Leg-2 04B + Delta B (`JSeriesHybrid4Split`: `retail_head` mirrors `home_head`/`work_head` off the same Arm-2 `arm2_feat`; encoder `slot_linear` widened to `d_act+12`; DETACH barrier untouched; encoder/act/home/work/cop heads unmodified beyond the aux-width bump).
- `3rdJ_04C_pairs_4split.py` — clone of Leg-2 04C, logic byte-for-byte unchanged (K=5 pairing frozen), only the path block repointed.

**04A smoke — run on the REAL Leg-3 Step-3 inputs (full 64,061 rows, not `--sample`):**
- `aux_seq` final shape: `(n, 48, 12)` for all three splits (train 44,843 / val 9,609 / test 9,609). Verified `AT_RETAIL` is plane index 2: per-plane means confirm ordering `[0]=AT_HOME (0.725) | [1]=AT_WORK (0.121) | [2]=AT_RETAIL (0.0196) | [3..11]=cop (Alone=0.355 ...)` — matches CONTRACT `[AT_HOME|AT_WORK|AT_RETAIL|9 cop]` exactly.
- `retail_avail (n,48) bool` present in the saved tensor dict alongside `work_avail`; True rate = 1.000 (retail_30min.csv has no NaNs in this Step-3 build, unlike work_30min which also read 1.000 here — both masks mechanically mirror the "non-NaN in source" rule per the runbook even though this cohort's rate is 100%).
- `step4_feature_config.json`: `n_aux = 12`, `aux_order = ["AT_HOME","AT_WORK","AT_RETAIL","Alone","Spouse","Children","parents","otherInFAMs","otherHHs","friends","others","colleagues"]`, `retail_pos_weight = 50.1056` (AT_RETAIL positive rate on train ≈ 1.96% → (1−f)/f ≈ 50.1, consistent with the runbook's Delta C citation of pos_weight≈49 at ~2% positive — close, not identical, since 49 was an a-priori estimate and this is the measured train-split value).
- Per-cycle AT_RETAIL rates (avail=1.000 all cycles): 2005=0.020, 2010=0.022, 2015=0.018, 2022=0.017 — broadly consistent with the runbook's "~2.1–2.3% all-day episode-time share" validation target (Delta content only; not a training input).

**04B smoke — model instantiated (TEST_CONFIG, d_cond=120 from the real feature config, n_aux=12) + forward/generate on a B=4 slice of the real train tensors:**
- Forward output shapes: `act_logits (4,48,14)`, `home_logits (4,48)`, `work_logits (4,48)`, `retail_logits (4,48)` [NEW], `cop_logits (4,48,9)` — no regression vs Leg-2 on the first four; retail head present with the contracted shape.
- `generate()` default call (no new kwargs) returns the original 5-tuple unchanged: `(gen_act(4,48), gen_home(4,48), gen_work(4,48), gen_cop(4,48,9), gen_cop_probs(4,48,9))` — fully backward-compatible.
- `generate(..., return_retail_probs=True)` returns a 6-tuple with `retail_sigmoid (4,48)` appended.
- `generate(..., return_hw_probs=True, return_retail_probs=True)` returns an 8-tuple (`..., home_sigmoid, work_sigmoid, retail_sigmoid`) — retail extension composes cleanly with the existing `return_hw_probs` extension, mirroring how `return_hw_probs` itself extended the base 5-tuple (per the runbook's "extended, backward-compatible kwarg, as return_hw_probs was").

**04C smoke — pairing run on the real 04A metadata outputs (train n=44,843 / val n=9,609):**
- Completed without error. Train pairs: 89,686 (≈2× respondents, as expected for 3-target-strata coverage minus same-stratum). Val pairs: 19,218. No self-pairing, no cross-cycle pairing (asserted on first 50 pairs, as in Leg-2). `strata_inv_freq.npy` saved. K=5 pairing logic confirmed untouched — occupancy channel count does not enter pair construction.

**Deviations from the runbook (none substantive; both are additive, non-breaking choices within the frozen contract):**
1. The runbook's Delta B says `generate()` gains `retail_sigmoid` "in its extended return tuple (backward-compatible kwarg, as `return_hw_probs` was)" without pinning the exact kwarg name/tuple layout. Implemented as a new `return_retail_probs: bool = False` kwarg (default off, preserves the exact Leg-2 5-tuple and 7-tuple shapes) that appends `retail_sigmoid` after whatever `return_hw_probs` already produces (6-tuple or 8-tuple). This composes both flags rather than picking one at the expense of the other; flagging in case 04E's inference wiring expects a different exact signature — reconcile there if so.
2. `04A_assembly_4split.py`'s conditioning block (`encode_demographics`) is verbatim Leg-2 per the runbook's explicit instruction ("No retail-specific conditioning is added"); confirmed d_cond=120 unchanged in structure (identical column list to Leg-2, only the underlying Leg-3 data differs).

No blockers. Foundation (04A/04B/04C) is built and smoke-verified end-to-end on the real Leg-3 Step-3 data; ready for 04D (training) to be picked up as a separate task.

### 2026-07-19 — 04D/04E train+inference built + smoked

Built `3rdJ_04D_train_4split.py`, `3rdJ_04E_inference_4split.py`, and the four sbatch wrappers (`3rdJ_s4_4split_{warmup,joint,valonly,train}.sh`). Deltas C/D/E applied in 04D; Deltas F/G applied in 04E. 04A/04B/04C and the whole `Leg2_2-split/` tree were read-only throughout — not modified. Both scripts smoke-tested locally on CPU (real Python at `C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe`, `-X utf8`).

**Step 0 — warm-start checkpoint inspection (BEFORE building — key finding, ESCALATE):**
Loaded `Leg2_2-split/Step4_docs/outputs_step4/checkpoints/best_model.pt` (1,515,970 bytes). Top-level keys: `{epoch, model_state, model_config, val_js, home_gap, work_gap, val_score}`. `model_config`: `d_model=64, n_heads=2, d_ff=256, N_enc=2, N_dec=2, d_act=16, d_cycle=16, n_aux=11, d_cond=119`. This is a **TEST_CONFIG-scale (`--sample`) checkpoint, epoch=4 of a 5-epoch run — NOT the Leg-2 production model.** Cross-checked: Leg-2's own `outputs_step4/step4_train.pt` currently holds only **896 rows** (not the real 44,843-row production split) and `step4_training_log.csv` shows exactly 5 epochs at ~6-8s each matching this checkpoint's `epoch=4` — i.e. someone re-ran `04A --sample`/`04D --sample` locally in that Leg-2 folder *after* the real production run that generated the 400MB `augmented_diaries.csv` (dated Jun 22, later than this checkpoint's Jun 15 timestamp), silently clobbering the shared `step4_train.pt`/`checkpoints/best_model.pt` filenames. The real production checkpoint was not found anywhere else locally (`sweep/` is empty). **This is a build-time finding for the manager to verify on the cluster before submitting `3rdJ_s4_4split_warmup.sh`** — flagged prominently in that wrapper's header comment.
Separately, and independent of the above: **Leg-2's `d_cond=119` vs Leg-3's `d_cond=120`** — diffed `feature_parts` between the two `step4_feature_config.json` files and found `MARSTH` grew from 6 categories (Leg-2, no missing-value bucket) to 7 (Leg-3, adds a `-1` missing-value category). This contradicts the runbook's "conditioning unchanged from Leg-2" framing — it's an independent Leg-3 data-pipeline fix, not something introduced by the retail delta.
**Resolution:** 04D's warm-start loader does NOT blindly adopt the checkpoint's `model_config` (Leg-2's own script hard-`raise`s on any `d_cond` mismatch, which would abort warm-start entirely given the above). Instead it rebuilds the architecture-family fields (`d_model/n_heads/d_ff/N_enc/N_dec/d_act/d_cycle/dropout`) from the checkpoint but always pins `d_cond`/`n_aux` to the CURRENT Leg-3 feature config, then loads weights by **name+shape match only** (manual filtering, `strict=False`), printing three lists — `loaded`, `shape_mismatch` (existing key, wrong shape → random-init), `missing_in_ckpt` (new key → random-init) — plus a `retail_head-ONLY-new confirmed: {bool}` line. Smoke result against the actual (smoke-scale, schema-drifted) Leg-2 checkpoint: **109/117 tensors loaded**; 4 shape-mismatches (`slot_linear.weight`, `cls_mlp.0.weight`, `arm1_decoder.proj_demo.weight`, `arm2_proj.weight` — all `d_cond`/`n_aux`-dependent) **in addition to** the 4 `retail_head.*` missing keys → `retail_head-ONLY-new confirmed: False` for THIS checkpoint. When 04D's own Phase-2 loads Phase-1's own output checkpoint (architecture-identical, no drift), the same mechanism reports **117/117 loaded, 0 mismatches, `retail_head-ONLY-new confirmed: True`** — i.e. the loader is honest and correct in both directions; the "only retail_head is new" invariant genuinely holds once a real, schema-matched production checkpoint is used.

**Delta D (fixed-α + PCGrad) — confirmed wired, no dynamic weighter remains:**
`WEIGHT_MODE=fixed` implemented as a literal 3-task grouping (`resid = act+home+cop`, `work`, `retail`) with `alphas={'resid':1.0,'work':0.5,'retail':0.3}` (CLI `--alphas`, parsed into this dict). `PCGrad` class ported near-verbatim from Leg-2 (task-agnostic — operates on whatever scalar-loss list it's given) and applied ONLY in `--phase joint`, over the three α-weighted task losses; diversity loss (home+work group-mean matching) retained unchanged from Leg-2, NOT extended to retail. No `UW`/`SLAW`/`equal`/`GradNorm`/`DWA`/`CAGrad` code path exists anywhere in the new file.

**Delta E (two-phase) — freezing verified in smoke:**
- `--phase warmup --smoke` (2 epochs, 400-pair CPU slice): printed `[PHASE=warmup] trainable tensors=4 (4,225 params) | frozen tensors=111` and `ONLY retail_head trainable confirmed: True`. Loss is noisy at this tiny scale (batch count ≈2/epoch) but the held-out retail PR-AUC/F1 trended up across 8 epochs of a longer smoke run (PR-AUC 0.058→0.067, F1 0.083→0.10), confirming genuine learning despite noisy raw loss. `warmup_checkpoint.pt` saved each epoch (no early-stop concept in phase 1, per spec).
- `--phase joint --smoke` (2 epochs, defaults to phase-1's own `warmup_checkpoint.pt`): printed `[PHASE=joint] trainable tensors=115 (367,610 params) | frozen tensors=0`, PCGrad ran without error, fixed α applied, exclusivity loss active (`excl=0.4326→0.4424`, nonzero only in this phase). Loss decreased cleanly (3.5868→3.4763), `val_score` 0.3598→0.2897, `val_js` 0.1867→0.1512 — `best_model.pt` saved both epochs. Checkpoint dict confirmed to carry `retail_gap`, `alphas`, `phase`, and the gate-set proxy metrics (`val_js/home_gap/work_gap/retail_gap/isr_raw/pr_auc/f1/val_score`).

**Delta C/F/G (04E) — smoke result (60 respondents, `--smoke --smoke_n 60`):**
`ret30_001..048` present (48/48). Nucleus decode (T=0.7, p=0.9) implemented as a **new function `generate_nucleus()` in 04E** that re-implements `JSeriesHybrid4Split._arm1_generate()`'s exact AR loop using only 04B's existing public methods (`_encode`, `_build_arm1_cond`, `arm1_decoder`, `act_head`, `_arm2_fuse`, the three occupancy heads) plus a top-p truncation step — **04B itself was NOT modified** (its own `generate()`/`_arm1_generate()` has no native nucleus support; see ESCALATE note below). −ln(49) shift implemented as the algebraically-equivalent probability transform `p_cal = p/(p + k·(1−p))` (avoids re-exposing raw logits through `generate()`). Min-dwell (≥2 slots) enforced on work+retail via a vectorized-per-row run-length merge, applied AFTER the exclusivity projection and the activity-based hard override (so it can only ever flip 1→0, never reintroducing a conflict). **ISR: raw=75.56%, post-projection=0.0%, post-pipeline=0.0%** — the projection mechanism is correct by construction (0% required), but the raw-ISR hard gate (≤0.5%) reported FAIL at this smoke scale, which is expected and non-diagnostic: the underlying checkpoint is a 2-epoch, 400-pair, 1-phase-cycle CPU smoke model, not a converged production model — the raw-ISR gate is a full-training-run target, not something a smoke checkpoint should be expected to pass. Final-CSV `>1-of-3-channel violations: 0` confirmed after the full pipeline (activity override + min-dwell applied on top of the projection). G3 co-presence rank-to-marginal binarization ported unchanged from Leg-2 (cop channels are unaffected by the retail delta).

**ESCALATE items (flagged, not silently resolved):**
1. **Warm-start checkpoint is smoke-scale, not production** (see Step 0 above) — manager/user must verify the cluster's copy before submitting `3rdJ_s4_4split_warmup.sh`; flagged in that wrapper's header.
2. **`d_cond` drift (119→120) between Leg-2 and Leg-3 feature configs**, traced to a `MARSTH` missing-value-category fix unrelated to retail — contradicts the runbook's "conditioning unchanged from Leg-2" framing. Handled generically by 04D's name+shape-match warm-start loader (not a blocker, but worth reconciling in the runbook text).
3. **`JSeriesHybrid4Split.generate()`/`_arm1_generate()` (04B) has no native nucleus (top-p) sampling** — Delta F requires it, but 04B was explicitly out of scope to modify. Resolved by adding a separate `generate_nucleus()` function in 04E that consumes 04B's public methods without touching the file. Flagging per the runbook's own escalation clause (T0.7+nucleus vs Leg-2's locked T0.8-no-nucleus) — if Heads-1/2 regression gates trip on the decode change alone once the validator exists, this is the mechanism to inspect first.
4. Retail PR-AUC/F1 in 04D's `validate()` is computed via **teacher-forced self-reconstruction on the observed day-type** (the only place real retail ground truth exists — AR-generated synthetic day-types have no ground truth to score against). This is an interpretive addition beyond the runbook's literal text (which doesn't specify how to compute the gate-set PR-AUC/F1 during training) — flagging the method choice for the record, not as a blocker.
5. `WGHT_PER`-in-the-loss and the 50/25/25 day-type + inverse-cycle-frequency sampler are both interpretive implementations (the runbook states the requirement but not the exact mechanism) — implemented as per-sample loss multipliers (clipped at train-split p99) and a combined `WeightedRandomSampler` weight respectively; documented in-code.

Smoke artifacts (checkpoints, CSVs, logs) moved to `outputs_step4/smoke_test_20260719/` so they are not mistaken for production outputs; `outputs_step4/checkpoints/` is empty pending the real cluster run.

Progress Checklist: `04D train` and `04E inference` build items ticked. Next: 04L/04M/04T post-hoc chain + validator (separate tasks), then cluster warmup+joint (5 seeds).

### 2026-07-19 — Leg-3 pushed to Speed + warmup job submitted

**Gate 1 — local end-to-end warm-start smoke (CPU, real Python 3.13, `-X utf8`), run against the CORRECT production checkpoint this time:**
`3rdJ_04D_train_4split.py --phase warmup --warm_start <local copy of Leg-2 R5_lr1e4/checkpoints/best_model.pt> --smoke`. Full stdout captured; exit code 0.
- `[WARM-START] NOTE: checkpoint n_aux=11 vs current n_aux=12 (expected — retail is a new aux plane); slot_linear will be random-init.`
- `loaded 256/261 tensors by name+shape match`
- `SHAPE-MISMATCH -> random-init (1): slot_linear.weight: ckpt(256, 43) -> model(256, 44)` — expected (n_aux 11→12).
- `MISSING-IN-CKPT -> random-init (4): ['retail_head.0.weight', 'retail_head.0.bias', 'retail_head.2.weight', 'retail_head.2.bias']` — the new head, as designed.
- 0 `UNUSED-IN-CKPT` lines printed → 0 unexpected/unused keys.
- `d_cond` matched exactly this time (120=120, unlike the earlier smoke-scale checkpoint's 119≠120) — so `proj_demo`/`cls_mlp` loaded clean; only `slot_linear` + `retail_head.*` fell back to random-init, i.e. the gate is materially cleaner against the real production checkpoint than against the smoke-scale one used in the 07-19 04D/04E build entry above.
- Phase-1 freeze: `[PHASE=warmup] trainable tensors=4 (66,049 params) | frozen tensors=255` and `ONLY retail_head trainable confirmed: True`.
- Smoke ran 2 epochs (smoke mode forces `max_epochs=2`, not 1 — script default, not a deviation), losses moved (0.8469→0.6493), `warmup_checkpoint.pt` saved each epoch. **GATE PASSED** — cleared to proceed to cluster push. Smoke artifacts relocated to `outputs_step4/smoke_test_20260719_warmstart_gate/` (kept separate from the earlier `smoke_test_20260719/` build-time smoke, which used the wrong checkpoint) so neither is mistaken for a production run.

**Resolution of the 07-19 build-time ESCALATE #1 (warm-start checkpoint was smoke-scale):** confirmed the correct source is Leg-2's real production sweep run — cluster path `Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt` (`d_model=256, d_cond=120, n_aux=11, val_js=0.0183`), verified present on the cluster (52,940,735 bytes, byte-identical to the local scratch copy). Updated `LEG2_CKPT` in both `3rdJ_s4_4split_warmup.sh` and `3rdJ_s4_4split_train.sh` from the old `outputs_step4/checkpoints/best_model.pt` (smoke-scale) to the `sweep/R5_lr1e4/...` path, and rewrote the stale ESCALATE header comments to RESOLVED with the new evidence. `3rdJ_s4_4split_joint.sh` needed no change (it warm-starts from Leg-3's own `warmup_checkpoint.pt` by default, per 04D's own fallback logic).

**Gate 2 — cluster env activation check (Leg-2 `.../Leg2_2-split/Step4_docs/3rdJ_s4_2split_train.sh`, `cat`'d read-only over ssh):** confirmed activation = `. /encs/pkg/modules-5.3.1/root/init/bash` (module init only, no explicit `module load`) + hardcoded venv interpreter `/speed-scratch/o_iseri/envs/step4/bin/python` (no conda). All four Leg-3 sbatch wrappers already used this exact pattern — no drift to fix there, only the `LEG2_CKPT` path (above).

**Push to Speed (scp, verified present on cluster afterward via `ls`):**
- Created `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/{Step3_docs/outputs_step3, Step4_docs}/` (did not exist before today).
- `Step3_docs/outputs_step3/`: `hetus_30min.csv` (21,222,851 B), `copresence_30min.csv` (48,885,407 B), `work_30min.csv` (6,696,191 B), `retail_30min.csv` (6,696,191 B) — sizes match local byte-for-byte.
- `Step4_docs/`: `3rdJ_04{A,B,C,D,E}_*_4split.py` + `3rdJ_s4_4split_{warmup,joint,valonly,train}.sh` — 9 files, sizes match local.
- Did NOT push local `outputs_step4/` tensors (04A/04C outputs) — 04A/04C regenerate them on the cluster per the warmup wrapper's own idempotent guard (`if [ ! -f step4_train.pt ]`).
- Created `/speed-scratch/o_iseri/logs/` (did not exist before today) for the sbatch `--output`/`--error` targets.

**Submitted — WARMUP ONLY (job 1127956):**
`sbatch -p pg --gres=gpu:1 --mem=32G -t 7-00:00:00 3rdJ_s4_4split_warmup.sh` from `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs` → `Submitted batch job 1127956`. `squeue -u o_iseri` (single check, no polling) showed `1127956  pg  3J_s4_wa  o_iseri  R  0:02  1  speed-01` — running. This one job runs 04A (assembly, idempotent) → 04C (pairs) → 04D `--phase warmup --warm_start <R5 cluster path> --fp16` (full 5-epoch run, not smoke) in a single batch script, per the frozen wrapper design. Did NOT submit `3rdJ_s4_4split_joint.sh`, the 5-seed sweep, or the validator — those wait on manager review of job 1127956's `.out` (`/speed-scratch/o_iseri/logs/3J_s4_4split_warmup_1127956.out`).

No blockers. Progress Checklist: "Local smoke (all stages)" and "Cluster: warmup" ticked; "Cluster: joint fine-tune (5 seeds)" explicitly left unticked/BLOCKED pending manager review, per instructions.

### 2026-07-21 — W3 colleague-co-presence 16:30 diagnostic (Step-4 reopen, read-only)

**Scope: read-only.** No script edited, no rake/retrain/pipeline stage re-run, no write to `outputs_step4/`. Only writes: a scratch script (outside the repo, in the session scratchpad) and this entry. `py -3 -X utf8` throughout; `augmented_diaries.csv` (192,183 rows, 644 cols) loaded with `usecols` only (never the whole file).

**T1 — W3's exact definition (traced from `3rdJ_05_censusLinkage_4split_val.py`, `validate_at_work_consistency`, lines 586-622).** Columns: `colleagues30_001..048` (`COL_COLS`, line 131). Formula (verbatim): for `DDAY_STRATA==1` (WD) and `DDAY_STRATA∈{2,3}` (WE) separately, `col_syn = df[syn_mask & dday][COL_COLS].fillna(0).mean().mean()*100` and same for `col_obs`; `diff = abs(col_syn - col_obs)`; **W3 = max(diff_WD, diff_WE)**, gate `<=3.0pp`. This is a **scalar mean-of-per-slot-means** (signed average collapsed across all 48 slots, then abs'd) — **not a per-slot max-deviation** the way W1/2.2 are (validator never computes a genuine per-slot array for W3; confirmed by code inspection, matches the caveat already on record in `3rdJ_05_censusLinkage_4split.md`'s Diagnostic-2 entry, footnote 1).

**T2 — Reproduced P2 (raw pool) statistic.** Official W3 on raw pool: **WD diff = 7.1862pp** (n_syn=18,423, n_obs=45,638; syn=11.41%, obs=4.22%), WE diff = 0.754pp → **max = 7.186pp ≈ claimed 7.19pp — CONFIRMED.** A genuine per-slot `|SYN%-OBS%|` array (added for localization only, mirroring Diagnostic 2's approach) on the 48 WD slots (anchor: GSS diary day starts 04:00, so slot *i* → `04:00+(i-1)*30min`; slot 26 → 16:30) confirms the **worst WD slot is slot 26 (16:30)**, identical to the matched-frame (P1) result — **CONFIRMED**, not a mapping artifact (initial midnight-anchor attempt mis-labelled slot 26 as 12:30; corrected against the doc's own 16:30 anchor and re-verified). Peak-region table (slots 22-30, 14:30-18:30; obs_n_total=45,638, obs_n_nonnull=21,189 constant across ALL 48 slots — this is a person-level "employed/eligible" flag, not a slot-varying at-work mask; syn_n_nonnull=18,423=100%):

| slot | time | SYN% | OBS% | delta(pp) |
|---|---|---|---|---|
| 22 | 14:30 | 23.03 | 9.82 | 13.20 |
| 23 | 15:00 | 23.01 | 9.18 | 13.83 |
| 24 | 15:30 | 22.70 | 8.41 | 14.29 |
| 25 | 16:00 | 21.70 | 6.94 | 14.76 |
| **26** | **16:30** | **20.19** | **5.42** | **14.77 (max)** |
| 27 | 17:00 | 17.14 | 3.63 | 13.51 |
| 28 | 17:30 | 13.48 | 2.89 | 10.59 |
| 29 | 18:00 | 10.02 | 2.16 | 7.86 |
| 30 | 18:30 | 8.36 | 1.86 | 6.51 |

WD per-slot daily-mean(|delta|)=7.24pp (≈ the official 7.19pp scalar, confirming the WD sign is consistent — no cancellation); 32/48 WD slots exceed 3pp. WE per-slot max=3.24pp (slot 16), daily-mean=0.93pp — WE is comparatively clean.

**T3 — Mechanism attribution.**
- **(a) SYN over-generation — DOMINANT.** At the peak (slot 26) SYN%=20.19% is ~3.7x OBS%=5.42%; the elevation is broad (slots ~17-30, 12:00-18:30), not a single-slot spike — a sustained WD-midday-to-evening over-generation of colleague co-presence in synthetic diaries.
- **(b) OBS-side thinness — RULED OUT for W3.** `obs_n_total`=45,638, `obs_n_nonnull`=21,189 (46.4%) at every WD slot — a large, stable sample, nothing like the n=1,311 thin OBS-weekend stratum that drove the W1/2.2 gates. Thinness is not the mechanism here.
- **(c) Threshold/generation-shape artifact — CONFIRMED, and is the root cause of (a).** Computed the GLOBAL (day-type-agnostic) scalar as a cross-check against `g3_copresence_thresholds.json`: global syn=3.3756%, global obs=3.3746%, **diff=0.0010pp — near-perfect match.** This is the smoking gun: the G3 calibration (see T4) hits the overall total almost exactly while the WD-stratified number is off by 7.19pp — proof the calibration has zero day-type/slot shape control, only a global-total constraint.

**T4 — Pivot answer.**
- **Is colleagues co-presence a rake margin? NO, confirmed in both rake scripts.** `3rdJ_04L_joint_rake_4split.py`: target columns are only `HOM_COLS/WRK_COLS/RET_COLS` (`hom30_*`, `wrk30_*`, `ret30_*`, lines 110-114); the only place "g3_copresence" appears is a straight file **copy** at lines 873-878 with the code's own comment: *"Copy G3 co-presence thresholds provenance from source (co-presence columns are unaffected by the retail rake)."* `3rdJ_04T_act_rake_4split.py`: touches only `act30_*` (14-way categorical), with its own header stating *"Only act30_* columns are ever written. hom30_*/wrk30_*/ret30_* are read-only inputs"* — zero mentions of colleagues/copresence anywhere in the file (grep-confirmed). **A re-rake of 04L or 04T literally cannot move a colleagues30 column — full stop.**
- **Correction to the manager's working hypothesis's code pointer:** co-presence generation is **not** in `3rdJ_04C_pairs_4split.py` (grep-confirmed zero hits for colleagues/copresence/threshold in that file — 04C is purely the K=5 demographic-neighbour training-pair construction, unrelated to co-presence values). The actual G3 generation + calibration lives in **`3rdJ_04E_inference_4split.py`**, the "G3 operating-point fix" block (lines 526-561), which is also the script that **writes** `g3_copresence_thresholds.json`. The manager's underlying hypothesis (co-presence is downstream-generated, not a rake margin) is CONFIRMED; only the file pointer needed correcting.
- **Mechanism (verified by code read):** for each of the 9 co-presence channels (incl. `colleagues`), 04E flattens **all 48 slots x all synthetic rows together**, takes `p_obs = nanmean(obs_vals==1)` (a single global scalar, no day-type/slot split), sets `q=1-p_obs`, computes one `t=quantile(flat, q)` over the flattened synthetic scores, and binarizes every synthetic (row,slot) cell against that **one threshold**. This guarantees the global marginal matches (confirmed: 0.0010pp) but exerts **zero control over the WD/WE split or slot-of-day shape** — whatever shape the model's raw continuous colleague-copresence score carries across time-of-day (here, a large midday/afternoon WD bulge peaking at 16:30) passes straight through the binarization unchanged.
- **Fixable? YES, in principle (regen-fixable, not re-rake-fixable, not irreducible).** Lever: re-stratify the G3 threshold-fix in 04E (lines 526-561) — compute `p_obs`/`t` separately per day-type (WD vs WE), or per-slot, instead of one flat global quantile per channel, then re-binarize. This requires the model's underlying continuous co-presence scores (already computed inside 04E's inference loop, before the fix block) — no retraining of 04B/04D needed. **Cost tier: moderate, not cheap-and-not-full-retrain** — patching 04E means every downstream consumer of its output (`04L→04T→04M→` Step-5) must re-run on the new `augmented_diaries.csv`, i.e. a partial Step-4 pipeline re-cascade from 04E forward, not a single-file edit-and-done. Well short of a full model retrain (04B/04D untouched), but not a zero-cost patch either.

**Pivot verdict:** re-rake **CANNOT** fix W3, because colleagues co-presence is never a rake margin in `04L_joint_rake` or `04T_act_rake` (grep- and header-comment-confirmed; only `hom30/wrk30/ret30` and `act30` are raked). It **IS** regen-fixable: the lever is re-stratifying the global quantile threshold in 04E's G3 fix block (lines 526-561) to WD/WE (or per-slot) granularity, at the cost of re-running the 04E→04L→04T→04M→Step-5 cascade (moderate cost — no model retrain required, but not a single-file fix either).

Deliverable complete; no edits proposed or applied. Awaiting manager adjudication.

### 2026-07-21 — Pool provenance + G3-fix landing-point recon (read-only)

**Scope: read-only.** No script edits, no re-rake/retrain/job submission, no writes to `outputs_step4/`. Local file-metadata peeks + login-node-safe cluster commands (`ls`/`cat`/`tail`/`squeue`/`sacct`) only; the 400 MB pool CSV was never opened.

**T1 — Provenance of the current `seed_3` pool.**
Local `.../sweep/seed_3_raked3_mindwell_actv/` holds exactly 3 files: `augmented_diaries.csv` (418,622,540 B, mtime Jul 20 18:20 local-clock), `step4_validation_report.html`/`.txt` (mtime Jul 20 15:36 local-clock; report's own internal header timestamp is `2026-07-20 13:45:34`, cluster-clock — the mtime skew is just the scp sync time, not a re-generation). No manifest/thresholds JSON is synced into this local dir. Cross-checked against `3rdJ_04_augmentationGSS_4split_val.md`'s Progress Log (lines 128-136), which names the exact producing chain: **04L rake job 1128036** (COMPLETED) → `sweep/seed_3_raked3/` → **04M min-dwell job 1128047** (COMPLETED) → `sweep/seed_3_raked3_mindwell/` → **04T act-rake job 1128070** (COMPLETED) → `sweep/seed_3_raked3_mindwell_actv/` → validator (final run **job 1128130**, ended 13:45:34 — matches the report header exactly, confirming 1128130 not 1128111 is the report of record). The producing checkpoint is `outputs_step4/seed_3/checkpoints/best_model.pt`, from **array task `1127957_3`** of the 5-seed joint fine-tune (`3rdJ_s4_4split_joint.sh --array=0-4`), COMPLETED 2026-07-19T18:12:02. That checkpoint **exists on the cluster** (`ls` confirmed, alongside `last_checkpoint.pt`, `step4_training_log_joint.csv`, `isr_summary.json`, `g3_copresence_thresholds.json`, `augmented_diaries.csv` — the raw pre-rake 04E output for seed 3) but does **NOT exist locally** (`outputs_step4/checkpoints/` and `outputs_step4/seed_3/` are both absent on the Windows side — only the final raked pool + reports were ever synced down).

**T2 — What job 1127956 (and downstream) produced.**
`squeue -u o_iseri` returned **empty — nothing queued or running.** `sacct` shows the ENTIRE cascade the prompt treats as "pending" already ran to completion, back-to-back, on 2026-07-19/20:
- `1127956` (`3J_s4_warmup`) COMPLETED 2026-07-19 17:06→17:20 (0:0) — warmup only, as the main doc's checklist says.
- `1127957_0..4` (`3J_s4_joint`, the `--array=0-4` 5-seed sweep) COMPLETED 2026-07-19 17:29→19:59 (0:0 all 5) — **this is the "Cluster: joint fine-tune (5 seeds)" step the main doc's checklist still shows unticked/BLOCKED "pending manager review" (line ~268) — that checklist line is STALE.** It was in fact submitted ~9 min after warmup finished (per the warmup `.out`'s own "Next: sbatch 3rdJ_s4_4split_joint.sh" line) and ran unattended to completion.
- `1128036`/`1128047`/`1128070` (04L/04M/04T) COMPLETED 2026-07-20, then validator `1128078`→`1128111`→`1128130` (3 successive runs, last one COMPLETED 13:44→13:45) produced the pool + report now sitting locally.
`3rdJ_s4_4split_joint.sh` (`cat`'d on cluster) confirms per-seed output isolation by design: `SEED_OUT="${SDIR}/outputs_step4/seed_${SEED}"`, 04D writes `--output_dir "$SEED_OUT" --checkpoint_dir "$SEED_OUT/checkpoints"`, 04E writes `--output "${SEED_OUT}/augmented_diaries.csv"` — never a shared/overwritten dir; `outputs_step4/seed_0..seed_4/` all exist independently on the cluster (`ls` confirmed). The 04L/04M/04T chain then wrote forward into new `sweep/seed_3_raked3[...]/` subdirs (never touching `seed_3/` itself), i.e. **the rake chain also does not overwrite** the raw seed_3 04E output.
**Plain answer: the pending run already happened and IS what produced `seed_3` — there is no future/still-running stage of this cascade left to "land a fix into."** T2's original three-way framing (new-pool-supersedes / in-place-seed_3 / not-wired-yet) collapses: it's neither "pending" nor "in-place-being-written-now" — it's **already-delivered and terminal**. Any further pool would require a **new** job submission, not something already in flight.

**T3 — Fix mechanics (cross-checked against `3rdJ_04E_inference_4split.py`, quoted verbatim).**
(a) **Persistence — CONFIRMED not persisted.** Line 548 `aug_df.loc[syn_mask, cols] = binarized` overwrites the co-presence columns in place inside the G3 fix block (530-561); `aug_df.to_csv(args.output, index=False)` happens at line 576, strictly after. The raw continuous scores never reach the CSV — matches the prompt's premise exactly.
(b) **Determinism — CONFIRMED, only-cop-changes.** `run_inference()` sets `torch.manual_seed(42)` (line 314) and `torch.cuda.manual_seed_all(42)` (line 316) as the first two statements in the function, before any batch loop. Grep for RNG calls across the whole file returns exactly one other hit: `torch.multinomial(probs, 1)` at line 195, inside the AR activity-token decode loop that `run_inference` drives — i.e. the only stochastic op in the file is downstream of, and covered by, the seed set at 314. No `DataLoader`/`shuffle`/`num_workers`/`cudnn`/second `manual_seed` call anywhere in the file (grep: 0 hits) — batches are iterated in the data's fixed on-disk order, not shuffled. **Re-running 04E on the same checkpoint + same input tensors should reproduce byte-identical act/hom/wrk/ret outputs; only the co-presence columns would change** (from the G3 fix edit itself). Residual, unaddressed risk: GPU/cudnn non-deterministic reduction order is not explicitly disabled (no `torch.backends.cudnn.deterministic=True`/`torch.use_deterministic_algorithms`) — a standard, low-probability caveat for float ops near a decision boundary, not a Python-level RNG gap.

**T4 — Recommended landing point: (B), with a corrected target dir.**
Because T2 shows the entire warmup→joint→rake→validate cascade behind job 1127956 already completed and delivered `seed_3` as its terminal output — there is no pending/future run for (A) to piggyback on — **(A) as literally stated in the prompt does not apply** (its premise, "the pending cluster run", is now historical, not pending). The live choice is: (B) **re-run 04E on the checkpoint that made `seed_3`**, i.e. `outputs_step4/seed_3/checkpoints/best_model.pt` on the cluster (confirmed present), with `--output outputs_step4/seed_3/augmented_diaries.csv` (or a fresh dir to avoid clobbering the seed_3 provenance files — recommend a new name, e.g. `seed_3_g3fix/`, so the pre-fix `seed_3/` is preserved for diff/audit), then re-run the 04L→04M→04T chain into a **new** `sweep/seed_3_g3fix_raked3_mindwell_actv/` (do not overwrite `seed_3_raked3_mindwell_actv/`, which stays as the pre-fix baseline for comparison), then re-validate, then Step-5 re-points at the new dir. Checkpoint-availability risk: **none found** — `best_model.pt` exists on the cluster at the exact path the joint wrapper wrote it to; only risk is it does **not** exist locally, so this must be a cluster-side `sbatch` job (04E alone, GPU, ~seconds-to-minutes based on the array task's own elapsed time), not a local run.

Deliverable complete; no edits proposed or applied. Awaiting manager adjudication.

### 2026-07-21 — 04E G3 per-slot co-presence fix (implemented + local smoke, cluster re-run pending)

**Predecessor archived first (discipline #1):** `Step4_docs/archive/3rdJ_04E_inference_4split.py.20260721_preG3perslot` (byte copy of the pre-fix file, 27,682 B), created before any edit.

**Block replaced.** Pre-fix line range **530–561** (the `print("\n[4b/4] Applying per-channel...")` header through the `# ── end G3 fix ──` comment, i.e. the single global-quantile loop lines 534–553 plus the summary-print lines 557–560 that necessarily changed too, since the new nested per-day-type `thresholds[cn]` schema breaks the old flat `v["obs_prev_pct"]` indexing — this follows directly from the prompt's own "Add a print: per channel, the day-type scalar..." bullet, not a scope creep). `syn_mask`/`obs_mask` defs and the `out_thresh` JSON write/path were kept structurally unchanged (same variable, same file name `g3_copresence_thresholds.json`), with two new masks added right after them (`wd_mask = DDAY_STRATA==1`, `we_mask = DDAY_STRATA.isin([2,3])`). New block spans post-fix lines **537–627** in the current file. No other file touched; no other block in 04E edited (AR generation, ISR pipeline, min-dwell, retail/home/work thresholding, column ordering, `to_csv`, CLI args all untouched — confirmed by re-reading the full diff before compiling).

**3 new module-level constants** (post-fix lines 114–116, placed right after `COLLEAGUES_IDX = 8`, before `NIGHT_SLOTS`):
```python
G3_MIN_OBS_CELL = 200   # min non-null observed rows in a (daytype, slot) cell
G3_MIN_POS_CELL = 20    # min observed positives in a (daytype, slot) cell
G3_MIN_SYN_CELL = 50    # min non-null synthetic scores in a (daytype, slot) cell
```

**New logic (summary):** for each `cn in COP_COLS` x `{WD, WE}`: compute a day-type-pooled fallback threshold (`p_obs_pool = nanmean(obs_d==1)`, `t_pool = quantile(syn_d_flat, clip(1-p_obs_pool,0,1))`); then per slot `j`, if `n_obs_j>=200 and n_pos_j>=20 and syn_valid.size>=50` use a per-(day-type,slot) threshold (`t_j` from that cell's own observed prevalence), else fall back to `t_pool`. Binarized cells written back via `aug_df.loc[syn_mask & d_mask, cols] = binarized`. NaN handling preserved (`score >= t` → `False` → `0.0` for NaN, unchanged from pre-fix). `thresholds[cn][dname]` now records `{obs_prev_pct, syn_prev_pct_after, n_per_slot_cells, n_fallback_cells, max_perslot_abs_gap_pp_after}`; `g3_copresence_thresholds.json` still written to the same path (04L file-copies it forward as provenance only — richer schema is safe per the prompt).

**`py_compile`:** clean (`py -3 -X utf8 -m py_compile 3rdJ_04E_inference_4split.py`, no output, exit 0).

**Smoke setup.** Reused the exact 2026-07-19 04E smoke inputs (documented above): `--data_dir outputs_step4` (the parent dir — `step4_{train,val,test}.pt`, `step4_all_meta.csv`, `step4_feature_config.json` all still present there) + `--checkpoint outputs_step4/smoke_test_20260719/best_model.pt` (epoch 1, phase=joint — same checkpoint that produced the 07-19 doc entry's `raw_isr=75.5556%`, confirming it's the correct reused artifact). Command:
```
py -3 -X utf8 3rdJ_04E_inference_4split.py --smoke --smoke_n 60 --data_dir outputs_step4 --checkpoint outputs_step4/smoke_test_20260719/best_model.pt --output outputs_step4/smoke_g3perslot_20260721/augmented_diaries_SMOKE.csv
```
Output written to **scratch** dir `outputs_step4/smoke_g3perslot_20260721/` (NOT `sweep/...`). Control run: the archived pre-fix script was transiently copied to `Step4_docs/_control_04E_preG3perslot.py` (co-located so it could `importlib.import_module("3rdJ_04B_model_4split")` from the same dir), run with identical args except `--output outputs_step4/smoke_g3perslot_20260721_control/augmented_diaries_SMOKE.csv`, then the transient copy was deleted immediately after the run (not left in the repo — only the two scratch output dirs + the true archive copy remain).

**Assertion (a) — only-cop-changed invariant: CONFIRMED.** `np.array_equal` on `act30_*`/`hom30_*`/`wrk30_*`/`ret30_*` (48 cols each, 180 rows) between patched and control CSVs: **all four = True**. OBS-row (`IS_SYNTHETIC==0`) co-presence columns (all 9 channels x 48 slots, NaN-safe compare): **True** (untouched, as expected — the G3 block never writes `obs_mask` rows in either version). Synthetic co-presence cells differing between patched vs. control: **1,845 / 51,840 (3.56%)** — nonzero, confirming the binarization rule itself did change (day-type-pooled vs. fully-global quantile), while everything upstream of it (AR generation, exclusivity projection, activity override, min-dwell) stayed byte-identical, exactly per the determinism argument in the "Why you exist" section. Also cross-checked at the console level: both runs printed identical `ISR summary: raw=75.5556% post-projection=0.0% post-pipeline=0.0%` and identical checkpoint metadata (`epoch=1 phase=joint val_JS=0.15124450183338514 work_gap=0.3939969639833561 retail_gap=0.3193371878349154`), consistent with the seed-42 determinism claim.

**Assertion (b) — fallback logic fires and is logged: CONFIRMED.** At smoke scale (60 respondents → ≤~40 synthetic rows per day-type cell), every one of the 9 channels x 2 day-types x 48 slots fell back (`n_per_slot_cells=0, n_fallback_cells=48` for all 18 channel/day-type combinations) — expected and stated as such in the prompt ("at smoke scale most cells will fallback — that's expected and fine; the point is the branch executes without error"). Both branches did execute without error (compile clean, run clean, exit 0, `>1-of-3-channel violations (final CSV): 0`, `Total rows: 180` matches `n*3`). This is a full only-fallback exercise of the branch, not a partial one — the per-slot branch's *code path* was not numerically exercised at this scale (min-support gates 200/20/50 are calibrated for the full production pool, not a 60-row smoke), which is disclosed per the prompt's "correctness gate, not efficacy" framing.

**Assertion (c) — construction sanity: PARTIAL / not directly exercised, but consistent.** No channel had any per-slot cells fire at smoke scale (see (b)), so the literal ask ("for at least the channels where per-slot cells were used...") has no populated case to check this run — noted honestly rather than glossed over. As a proxy, the fallback-branch day-type scalar `|obs−syn|` gaps (from `g3_copresence_thresholds.json`) were all small and near-zero-by-construction: max across all 18 channel/day-type cells = **0.1364 pp** (`otherHHs`, WD), all others ≤0.137 pp, most <0.1 pp — consistent with the pooled-quantile construction working correctly, though this does not substitute for a per-slot-cell check, which requires the full production pool (cluster run) to populate.

**Files touched:** `3rdJ_04E_inference_4split.py` (only file edited); `Step4_docs/archive/3rdJ_04E_inference_4split.py.20260721_preG3perslot` (new archive copy); `outputs_step4/smoke_g3perslot_20260721/` and `outputs_step4/smoke_g3perslot_20260721_control/` (new scratch smoke dirs, both outside `sweep/...`). `outputs_step4/sweep/...` untouched.

**Not claimed:** W3 efficacy (7.19 pp → ≤3 pp gate pass) is NOT verified by this smoke — per the prompt's scope boundary, that requires the cluster-only production checkpoint and full pool, deferred to the cluster re-run stage.

Progress Checklist: 04E G3-fix code edit + local smoke — DONE. Next (manager-authorized, NOT done here): cluster 04E re-run on the production `seed_3` checkpoint + rake re-cascade (04L→04M→04T) into a new sweep dir + re-validate for actual W3 efficacy.

**Follow-up (2026-07-21, same day) — forced-per-slot branch exercise (coordinator-requested; constants REVERTED after):** The `smoke_n=60` run above hit only the fallback branch (production guards 200/20/50 are too strict for a 60-row smoke), so the NEW per-slot code path was never numerically executed. To close that gap **locally** (still no cluster work), the guards were TEMPORARILY lowered to `G3_MIN_OBS_CELL=5, G3_MIN_POS_CELL=1, G3_MIN_SYN_CELL=2` and the same `--smoke --smoke_n 60` re-run to a fresh scratch dir `outputs_step4/smoke_g3perslot_20260721_forceperslot/`.
- **(a) per-slot branch EXECUTED and now dominates:** per-slot vs fallback cell counts flipped from all-fallback to mostly per-slot — e.g. `Alone/WD 48/0`, `Spouse/WD 48/0`, `otherInFAMs/WD 48/0`, `friends/WD 48/0`, `Children/WD 48/0`; thinner cells still fell back correctly (e.g. `otherInFAMs/WE 2/46`, `colleagues/WE 0/48` — WE colleagues has 0 observed positives at smoke scale, so the min-pos guard keeps it on fallback, exactly as designed).
- **(b) ran without error:** compile clean, exit 0, `>1-of-3-channel violations: 0`, `Total rows: 180`.
- **(c) construction sanity (per-cell, per-slot cells only):** spot-checked 192 per-slot cells across `Alone/Spouse/otherInFAMs/friends` (WD). Where OBS prevalence lands near an achievable synthetic-grid point the gap is <1 pp (e.g. `Alone/WD` slot 04: OBS 23.40% vs SYN 23.08% = 0.33 pp; slot 06: OBS 38.30% vs SYN 38.46% = 0.16 pp). Where it does not, the gap is bounded by the smoke-scale discretization grid: each cell has only ~13 synthetic scores, so achievable SYN prevalences are quantized to multiples of 1/13 ≈ 7.69% (mean|gap| 3.6 pp, max 6.87 pp across the 192 cells). This is the expected near-zero-by-construction behavior *up to* the per-cell sample-size grid — it is NOT a bug; at production cell sizes (hundreds–thousands of rows/cell, per the 200/20/50 guards) the grid is fine and the per-cell gap collapses toward zero. This is precisely why the production guards are 200/20/50, not 5/1/2.
- **(d) only-cop-changed invariant STILL holds with lowered constants:** `np.array_equal` on `act30_*`/`hom30_*`/`wrk30_*`/`ret30_*` (forceperslot vs. the pre-fix control CSV) = **True** on all four — the per-slot branch touches only co-presence columns, same as the fallback branch.
- **CONSTANTS REVERTED:** guards set back to the production values **`G3_MIN_OBS_CELL=200, G3_MIN_POS_CELL=20, G3_MIN_SYN_CELL=50`** (verified: file lines 114–116 read 200/20/50; `py_compile` clean). The 5/1/2 values were for this one-time branch-exercise ONLY and are NOT in the file that would ship to the cluster. The `_forceperslot` scratch dir is retained for audit; `outputs_step4/sweep/...` untouched throughout.
