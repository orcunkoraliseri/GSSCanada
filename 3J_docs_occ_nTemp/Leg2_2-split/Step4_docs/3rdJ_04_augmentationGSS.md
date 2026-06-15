# 3rdJ Step 4 — Occupancy Diary Augmentation (Leg-2 Two-Channel Split)

## Goal

Port the Leg-1 GSS Step-4 augmentation model (`2J_docs_occ_nTemp/04A…04F`) to the
Leg-2 **Residential + Office** two-channel pipeline. The shipped Leg-1 model is the
**J3 Hybrid AR-Encoder** (shared encoder trunk → autoregressive activity arm +
non-autoregressive binary arm for AT_HOME + 9 co-presence channels). Leg-2 keeps
that backbone and adds a **second binary occupancy head for AT_WORK**, the new
**office conditioning variables**, and the **mandatory multi-head training discipline**
(dynamic loss weighting + PCGrad + diversity-preserving loss) that the pipeline spec
requires to stop a naïve multi-head from collapsing the diurnal peaks.

> **One model, two channels.** A single shared encoder learns universal
> time-of-day / day-of-week structure; the activity arm and the binary arm are
> reused from J3; the only structural addition is a third binary head (AT_WORK)
> alongside AT_HOME and co-presence. The genuinely new *build* work is the
> multi-head loss machinery — not the wiring.

## Reference

- **Leg-1 templates (clean-port the J3 path ONLY; ignore the G/H/I/J5/J6/MDLM variants):**
  - `2J_docs_occ_nTemp/04A_dataset_assembly.py` (tensor assembly)
  - `2J_docs_occ_nTemp/04C_training_pairs.py` (day-type pair construction)
  - `2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_J3.py` (production J3 model)
  - `2J_docs_occ_nTemp/04D_train.py` (training loop)
  - `2J_docs_occ_nTemp/04E_inference.py` (autoregressive generation)
  - `2J_docs_occ_nTemp/04F_validation.py` (gates → HTML report)
- **Pipeline spec:** `3J_docs_occ_nTemp/Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` §STEP 4
- **Step-3 Leg-2 outputs (model inputs):** `Step3_docs/outputs_step3/`
- **Validation gates:** `3rdJ_04_augmentationGSS_val.md` (companion doc)

## Data Source Inventory

| Input | Source | Key columns consumed |
|-------|--------|----------------------|
| `hetus_30min.csv` | Step-3 | `occID, CYCLE_YEAR, DDAY_STRATA, WGHT_PER`, `act30_001..048`, `hom30_001..048`, conditioning cols below |
| `copresence_30min.csv` | Step-3 | `occID` + 9×48 co-presence slots `{Channel}30_001..048` |
| `work_30min.csv` | Step-3 **[Leg-2 NEW]** | `occID` + `WORK30_001..048` (binary 1/0 AT_WORK track) |

Co-presence channels (fixed order, 9): `Alone, Spouse, Children, parents, otherInFAMs, otherHHs, friends, others, colleagues`.

Conditioning columns read from `hetus_30min.csv`:
`AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, HRSWRK, NOCS, COW, ATTSCH, POWST, TOTINC, COLLECT_MODE`
**plus Leg-2 office additions** `NAICS, TELEWORK, WORK_SCHEDULE`.

---

## Proposed Changes (Leg-2 Deltas)

### Delta A — AT_WORK as the second occupancy channel
`aux_seq` width grows **10 → 11**: `[AT_HOME(1) | AT_WORK(1) | co-presence(9)]`.
AT_WORK is both an **encoder input** (observed day) and a **decoder target**
(the unobserved day-types we generate), exactly mirroring AT_HOME. A new
`work_avail` (B,48) bool mask carries AT_WORK availability (NaN slots in
`work_30min.csv` → masked out of the loss).

### Delta B — Office conditioning variables
`cond_vec` gains three office features (on top of the Leg-1 set, several of which —
`NOCS, COW, HRSWRK` — already exist):
- `WORK_SCHEDULE` — one-hot, 9 shift categories (1–9), NaN → all-zero
- `NAICS` — one-hot industry bucket, NaN → all-zero
- `TELEWORK` — binary flag, NaN → 0 (with a separate "telework-known" indicator bit)

### Delta C — Second NAT head (AT_WORK)
A dedicated head mirroring AT_HOME, attached to the Arm-2 (non-autoregressive)
fused representation: `work_head = Linear(d_model, d_model) → Tanh → Linear(d_model, 1)`,
producing `work_logits (B,48)`. The detach() barrier between the AR activity arm
and the NAT binary arm is preserved unchanged.

### Delta D — Multi-head training discipline (the new BUILD work, not tuning)
Naïve equal-weight multi-head training smooths the mean and collapses the diurnal
peaks (the COP peak-collapse failure mode from Leg-1). The Leg-2 trainer adds, as
non-optional machinery (each behind an env toggle, all ON by default):
- **Dynamic loss weighting** — homoscedastic **uncertainty weighting** (Kendall & Gal):
  one learnable log-variance `log σ²_t` per task `t ∈ {act, home, work, cop}`;
  `total = Σ_t [ exp(−log σ²_t)·L_t + log σ²_t ]`. SLAW selectable via `WEIGHT_MODE=slaw`.
- **PCGrad gradient surgery** — per-task gradients are de-conflicted (project away
  negative cosine components) before the optimizer step, killing home↔work↔cop
  negative transfer.
- **Diversity-preserving loss** — a per-(cycle×stratum) marginal-matching term on the
  predicted per-slot presence curves for home AND work (extends Leg-1's `marg_loss`),
  so the heads reproduce the diurnal *shape*, not just the daily mean.

### Delta E — Inference emits the office track
`augmented_diaries.csv` gains `wrk30_001..048` (binary 0/1) alongside `hom30_001..048`.
Post-hoc consistency rules extended: Work activity (raw cat 1) at a slot → `wrk30=1`,
`hom30=0`; Sleep at night → `hom30=1`, `wrk30=0`; AT_HOME and AT_WORK never both 1.

### Delta F — Platform-detection path block
Identical to Steps 1–3: `_WIN_BASE / _SPEED_BASE / _MAC_BASE` resolve `INPUT_DIR`
(`Step3_docs/outputs_step3`) and `OUTPUT_DIR` (`Step4_docs/outputs_step4`) at startup;
no hardcoded paths.

---

## CONTRACT — shared schema across all Step-4 files

> Every file below MUST adhere to these names/shapes exactly. Do not rename keys or columns.

**Tensor bundle** (`step4_{train,val,test}.pt`, dict of tensors):
```
act_seq    (n, 48)      int64    activity, 0-indexed (raw 1..14 → 0..13)
aux_seq    (n, 48, 11)  float32  [AT_HOME | AT_WORK | 9 co-presence], binary 0/1
cop_avail  (n, 48, 9)   bool     co-presence availability mask
work_avail (n, 48)      bool     AT_WORK availability mask (NaN slot → False)
cond_vec   (n, d_cond)  float32  demographics + office conditioning (no CYCLE_YEAR)
cycle_idx  (n,)         int64    CYCLE_YEAR → {2005:0,2010:1,2015:2,2022:3}
cycle_year (n,)         int64    raw CYCLE_YEAR
obs_strata (n,)         int64    DDAY_STRATA {1,2,3}
wght_per   (n,)         float32  survey weight
occ_ids    (n,)         int64    occID
```

**Feature config** (`step4_feature_config.json`):
`d_cond, n_activity_classes=14, n_copresence=9, n_slots=48, n_aux=11,
feature_parts{...}, act_class_freqs[14], cop_pos_weights{9}, home_pos_weight, work_pos_weight`.

**Pairs** (`training_pairs.pt`, `val_pairs.pt`): `{src_idx (P,), tgt_k_indices (P,K=5), tgt_strata (P,)}`; `strata_inv_freq.npy (4,)`.

**Model forward** — input `batch` dict adds `dec_act_seq (B,48) int64`,
`dec_aux_seq (B,48,11)`, `dec_cop_avail (B,48,9)`, `dec_work_avail (B,48)`, `tgt_strata (B,)`.
Returns: `{act_logits (B,48,14), home_logits (B,48), work_logits (B,48), cop_logits (B,48,9)}`.

**Checkpoint** (`checkpoints/best_model.pt`): `{epoch, model_state, model_config, val_js, home_gap, work_gap, val_score}`; `val_score = val_js + 0.5*(home_gap+work_gap)/2`.

**Inference output** (`augmented_diaries.csv`, N×3 = ~192,183 rows):
`occID, CYCLE_YEAR, DDAY_STRATA, IS_SYNTHETIC` + demographics +
`act30_001..048` (1-indexed 1–14) + `hom30_001..048` (0/1) +
`wrk30_001..048` (0/1) **[Leg-2 NEW]** + 9× `{Channel}30_001..048` (float [0,1]).

---

## Module Structure Summary

```
Step4_docs/
├── 3rdJ_04A_assembly_2split.py    reads Step-3 CSVs → step4_{train,val,test}.pt + feature_config.json
├── 3rdJ_04C_pairs_2split.py       builds training_pairs.pt / val_pairs.pt (K=5 neighbour day-type pairs)
├── 3rdJ_04B_model_2split.py       J3 two-channel model (act AR arm + home/work/cop NAT arm)
├── 3rdJ_04D_train_2split.py       training loop + UW/SLAW + PCGrad + diversity loss
├── 3rdJ_04E_inference_2split.py   AR generation → augmented_diaries.csv (+ wrk30_*)
├── 3rdJ_04_augmentationGSS_2split_val.py   gates → step4_validation_report.html/.txt
├── 3rdJ_s4_2split_train.sh        cluster: assembly→pairs→train→inference (GPU, pg partition)
├── 3rdJ_s4_2split_valonly.sh      cluster: validator only
└── outputs_step4/                 all artifacts + checkpoints/
```

## Expected Result

- `outputs_step4/step4_{train,val,test}.pt` + `step4_feature_config.json`
- `outputs_step4/training_pairs.pt`, `val_pairs.pt`, `strata_inv_freq.npy`
- `outputs_step4/checkpoints/best_model.pt` + `last_checkpoint.pt`
- `outputs_step4/step4_training_log.csv` (per-epoch: losses, val_js, home_gap, work_gap, σ_t weights, lr, grad_norm)
- `outputs_step4/augmented_diaries.csv` (~192,183 rows, both occupancy channels)
- `outputs_step4/step4_validation_report.html` + `.txt`

Residential gates should reproduce Leg-1 quality (act_JS, AT_HOME RMS, COP max gap);
the new AT_WORK channel should clear the office gates in `3rdJ_04_augmentationGSS_val.md`
(presence RMS ≤5 pp, diurnal-shape correlation, peak-timing ≤1 h, night near-zero).

## Test Method

1. **Local smoke test** (sample mode, tiny model, CPU): from `Step4_docs/`
   ```
   py -3 -X utf8 3rdJ_04A_assembly_2split.py --sample
   py -3 -X utf8 3rdJ_04C_pairs_2split.py --sample
   py -3 -X utf8 3rdJ_04D_train_2split.py --sample
   py -3 -X utf8 3rdJ_04E_inference_2split.py --sample
   py -3 -X utf8 3rdJ_04_augmentationGSS_2split_val.py --sample
   ```
   Confirms the chain runs end-to-end and the schema/contract holds (shapes, columns).
2. **Cluster full run** (GPU): bundle-upload `Step4_docs/`, then on the cluster
   `sbatch 3rdJ_s4_2split_train.sh` (assembly→pairs→train→inference), then
   `sbatch 3rdJ_s4_2split_valonly.sh`.
3. Inspect `step4_validation_report.html`: target 0 FAIL on the four residential
   hard gates + the office gates.

---

## Progress Log

### 2026-06-15 — Step 4 built + smoke-tested locally

**Deliverables created (10 files):**
- `3rdJ_04A_assembly_2split.py` — reads Step-3 CSVs (incl. `work_30min.csv`), builds tensors (aux width 11), `step4_feature_config.json` (**d_cond = 119**)
- `3rdJ_04C_pairs_2split.py` — K=5 neighbour day-type pairs (exact + fuzzy match, ported verbatim)
- `3rdJ_04B_model_2split.py` — `JSeriesHybrid2Split`: clean J3 port + new `work_head` (mirrors `home_head`); forward returns `{act,home,work,cop}_logits`; detach barrier preserved
- `3rdJ_04D_train_2split.py` — training loop + **UW dynamic weighting** (learnable log-var/task, default) + **PCGrad** + **diversity loss** (home & work per cycle×stratum); all ON by default, env-toggled
- `3rdJ_04E_inference_2split.py` — AR generation + post-hoc consistency; emits `wrk30_001..048`; channel exclusivity enforced
- `3rdJ_04_augmentationGSS_2split_val.py` — gates G1–G4 (residential) + OW1–OW6 (office), dark-theme HTML/TXT
- `3rdJ_04_augmentationGSS.md` (this) + `3rdJ_04_augmentationGSS_val.md`
- `3rdJ_s4_2split_train.sh` (GPU `pg`, assembly→pairs→train→inference) + `3rdJ_s4_2split_valonly.sh`

**Contract verified:** aux_seq width 11; tensor/config/pairs/checkpoint/CSV schemas all match. `augmented_diaries_SAMPLE.csv` = 3×N rows, 596 cols, 48 `wrk30_` present, **0 home∧work overlap**.

**Smoke test (sample mode, 5 epochs, tiny model, CPU):** chain runs end-to-end. PCGrad + UW + diversity all active. Sample scorecard 50 PASS / 9 WARN / 8 FAIL — FAILs are expected undertraining artifacts (synthetic co-presence collapsed to ~0; AT_WORK over-predicted), **not** wiring bugs: OW2 diurnal r = 0.961 PASS, OW3 peak shift = 1 slot PASS. Real model trains on the cluster GPU.

**Watch-items for the full run:** (1) co-presence head collapse — confirm it recovers with 100 epochs / consider `COP_POS_WEIGHT=1`; (2) AT_WORK presence calibration (OW1).

**Next:** bundle-upload source files to Speed, `sbatch 3rdJ_s4_2split_train.sh` (GPU), then `3rdJ_s4_2split_valonly.sh`.

### 2026-06-15 — Cluster run 1 (job 968495): COMPLETED but INVALID (early-stop bug)

Submitted `3rdJ_s4_2split_train.sh` on Speed (partition `pg`, GPU, node cisr-2). Job **968495 COMPLETED, exit 0:0, elapsed 01:26:21**, MaxRSS ~15.4 GB. All artifacts written (`best_model.pt`, `last_checkpoint.pt`, `step4_training_log.csv`, `augmented_diaries.csv` ~520 MB) and `augmented_diaries.csv` had **exactly 192,183 rows** (64,061 obs + 128,122 syn), 48 `wrk30_` cols, **0 home∧work overlap**. stderr clean.

**But the output is invalid.** Training early-stopped at **epoch 16 of 100** while the loss curve was still descending steeply (val_score 0.318 → 0.291 → 0.281), and inference then ran on a near-untrained checkpoint.

**Root cause.** Epoch 1 logged the *lowest* `val_score` (0.2146) of the entire run — a degenerate "predict-the-marginal" model fakes a good aggregate score (val_js 0.124, home_gap 0.084) precisely because it has no temporal structure. The best-tracker locked onto epoch 1, `patience=15` counted from there, and early-stop fired at epoch 16; `best_model.pt` was frozen at epoch ~1 (mtime 09:53, ~46 min before the last epoch). Inference (04E) loaded that checkpoint → garbage diaries.

**Not bugs / confirmed healthy:** co-presence did **not** collapse (sigma_cop ~0.87, in line with home/work; cop_loss 0.0073 → 0.0050); schema, row count, and channel exclusivity all correct. The architecture is sound — it simply never trained.

**Fix (`3rdJ_04D_train_2split.py`).** Added `--warmup-epochs` (default **20**; sample mode = 1). During warmup: `best_model.pt` is saved each epoch (so a checkpoint always exists) but `best_val_score`/`patience` are **not** engaged and the LR-plateau scheduler is **deferred** — so the degenerate early epochs can neither win best-selection nor trigger early-stop nor prematurely decay the LR. Edits: argparse (`--warmup-epochs`), sample-mode override, `plateau.step` guard, `in_warmup` save block, startup banner.

**Cluster run 2 (job 968526):** uploaded the single fixed `3rdJ_04D_train_2split.py`, resubmitted `3rdJ_s4_2split_train.sh` → **job 968526 RUNNING on cisr-1** (partition `pg`). Expect the full ~100 epochs (~9 h at ~180 s/epoch).

**Acceptance check before trusting run-2 output:** confirm the best checkpoint epoch is **late** (not 1), and that final `val_js` / `home_gap` land well below run-1's 0.22 / 0.18. Then submit `3rdJ_s4_2split_valonly.sh`.

### 2026-06-15 — HPT sweep prepared (single-axis variants off the baseline)

Architecture is inherited (J3 won in Leg-1), so the sweep is **one-factor-at-a-time** around the run-2 baseline (R0), not a full grid. New env hooks added to `3rdJ_04D_train_2split.py` (defaults preserve baseline exactly): `WORK_POS_WEIGHT` (override AT_WORK BCE pos_weight; was config-only) and `COP_POS_WEIGHT` (>0 applies per-channel `cop_pos_weights` from config in `cop_col_names` order, scaled — fights cop collapse; was hardcoded `None`). `LAMBDA_DIV` / `WEIGHT_MODE` (env) and `--lr` / `--d_model` (arg) already existed.

New wrapper `3rdJ_s4_2split_sweep.sh` (`pg`, GPU, 48 h): **REUSES** the baseline assembly (`step4_*.pt` + config + `training_pairs.pt` from `outputs_step4/`) — does NOT re-run 04A/04C — and re-trains (04D) + re-infers (04E) into `outputs_step4/sweep/$VARIANT/`. Knobs passed per job via `sbatch --export=ALL,VARIANT=…,KNOB=…`; an unset knob == baseline.

**6 variants** (submit lines in the wrapper header): R1_workpw5 (`WORK_POS_WEIGHT=5.0`→OW1), R2_div02 (`LAMBDA_DIV=0.2`→collapse), R3_slaw (`WEIGHT_MODE=slaw`), R4_cop1 (`COP_POS_WEIGHT=1.0`→G3), R5_lr1e4 (`LR=1e-4`→convergence), R6_d384 (`DMODEL=384`→capacity). Selection = validator gate table (G1–G4 + OW1–OW6) **Pareto**, not composite.

**Cluster capacity (2026-06-15 ~12:20):** `pg` = 6 GPU nodes / 25 GPUs; **~10 free** (mostly speed-01/-17), speed-05's 6 drained/offline, **0 jobs queued ahead**. → all 6 variants fit in **one parallel wave**. Files uploaded + env hooks verified on cluster. **Not launched yet** — variants depend on the baseline assembly (gated on 968526 finishing). Baseline 968526 RUNNING ~54 min at check.

### 2026-06-15 — HPT sweep LAUNCHED (6 variants, parallel with baseline 968526)

**Pre-flight checks (all PASS).** The 4 shared baseline tensors are on disk in `outputs_step4/` (written by 04A/04C at 11:28–11:29): `step4_train.pt` (156.6 MB), `step4_val.pt` (33.6 MB), `training_pairs.pt` (5.0 MB), `step4_feature_config.json` (5.1 KB). Wrapper `3rdJ_s4_2split_sweep.sh` (4436 B) + edited `3rdJ_04D_train_2split.py` (36186 B) both present (12:19). No re-upload needed. The variants **REUSE** this assembly (no 04A/04C re-run) and so launched immediately **in parallel with the still-running baseline 968526** — no need to wait for it.

**6 sweep jobs submitted** (`sbatch ... 3rdJ_s4_2split_sweep.sh`, partition `pg`, GPU, 48 h):

| Job ID | Variant | Knob (`--export=ALL,…`) |
|--------|---------|-------------------------|
| 968625 | R1_workpw5 | `WORK_POS_WEIGHT=5.0` |
| 968626 | R2_div02   | `LAMBDA_DIV=0.2` |
| 968627 | R3_slaw    | `WEIGHT_MODE=slaw` |
| 968628 | R4_cop1    | `COP_POS_WEIGHT=1.0` |
| 968629 | R5_lr1e4   | `LR=1e-4` |
| 968630 | R6_d384    | `DMODEL=384` |

**squeue snapshot (immediately post-submit):**
```
     JOBID               NAME    STATE       TIME NODELIST(REASON)
    968630            R6_d384  PENDING       0:00 (AssocGrpCpuLimit)
    968629           R5_lr1e4  PENDING       0:00 (AssocGrpCpuLimit)
    968628            R4_cop1  PENDING       0:00 (AssocGrpCpuLimit)
    968627            R3_slaw  RUNNING       0:06 speed-17
    968626           R2_div02  RUNNING       0:09 speed-17
    968625         R1_workpw5  RUNNING       0:11 speed-17
    968526        3J_s4_train  RUNNING    3:13:21 cisr-1
```
3 variants (R1/R2/R3) RUNNING on speed-17; R4/R5/R6 PENDING on `AssocGrpCpuLimit` (group CPU cap, not a node shortage) — they start as the running ones release slots. Each writes to `outputs_step4/sweep/$VARIANT/`. Baseline 968526 unaffected (3:13 elapsed on cisr-1).

**Next:** when all 6 finish, run `3rdJ_s4_2split_valonly.sh` per variant and compare the gate tables (G1–G4 + OW1–OW6) Pareto-style against R0.
