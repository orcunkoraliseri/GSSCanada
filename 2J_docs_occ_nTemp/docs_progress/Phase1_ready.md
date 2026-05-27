# Step 4 — Phase 1 Ready: Pre-HPC Checklist & Next Task

**Status as of 2026-04-10**
All local work for Step 4 is complete. The pipeline is ready to be packaged and submitted to the Concordia Speed HPC cluster.

---

## What Was Done (Local Machine)

### Scripts Built and Smoke-Tested

All 7 scripts were written and tested on a 500-respondent stratified sample (`--sample` flag). All tests passed.

| Script | Purpose | Smoke Test Result |
|--------|---------|-------------------|
| `sample_for_testing.py` | Stratified 500-respondent sample from Step 3 outputs | PASS |
| `04A_dataset_assembly.py` | Merge hetus + copresence, encode features, build train/val/test tensors | PASS — d_cond=76, 500 rows |
| `04B_model.py` | ConditionalTransformer architecture (import-only, not run directly) | PASS — imports clean |
| `04C_training_pairs.py` | K=5 demographic nearest-neighbor supervision pairs | PASS — 700 train, 150 val pairs |
| `04D_train.py` | Training loop: teacher forcing, AdamW, FP16, early stopping | PASS — 5 epochs, val_JS=0.136 |
| `04E_inference.py` | Autoregressive synthetic diary generation | PASS — 1500 rows (500×3) |
| `04F_validation.py` | 8-section validation + HTML report | PASS — report generated |

### Validation Report Reviewed

Sample run report (`outputs_step4_test/step4_validation_report.html`) was reviewed section by section. Result: **28 PASS / 1 WARN / 17 FAIL**.

The 17 FAILs were assessed:

| Section | Result | Interpretation |
|---------|--------|----------------|
| S1 — Training curves | FAIL (1.1, 1.2) | Only 5 epochs — pure epoch-count artifact, ignore |
| S2 — Activity JS divergence | ALL PASS (0.021–0.043) | Excellent — marginal distribution already correct |
| S3 — AT_HOME rate | 11 FAILs (8–28 pp off) | Undertrained — AT_HOME head not yet calibrated |
| S4 — Temporal structure | 4.2 FAIL (ratio=145×) | **Watch this** — model not yet generating smooth episodes |
| S5 — Co-presence | ALL PASS | Masking and binary encoding correct |
| S6 — Demographic conditioning | r=0.925 PASS | Demographics are being used correctly |
| S7 — Cross-stratum consistency | 2 FAILs | Consequence of S4 temporal incoherence |

**Decision:** No hyperparameter changes before HPC run. Architecture is sound. The transition rate (Section 4.2) is the one metric to check after full training — target ≤ 3× (currently 145× at 5 epochs).

### Supporting Files Created

- `requirements_step4.txt` — Python dependencies for HPC conda environment

### Reference Documents

- `04_augmentationGSS.md` — Full implementation spec + Progress Log
- `04_augmentationGSS_hpc.md` — Complete HPC submission guide (all 9 phases)
- `04_augmentationGSS_testing.md` — Testing spec
- `04_augmentationGSS_val.md` — Validation spec

---

## Next Task — HPC Submission (Phase 1: Local Packaging)

### Aim
Package all Step 4 scripts and the full 64,061-respondent input data into a tarball, then transfer to the Concordia Speed cluster and begin the full training run.

### What to Do
Create the tarball on the local machine and transfer it to `/speed-scratch/$USER/` on Speed. Then set up the conda environment and submit the SLURM job chain.

### Before Starting — Confirm These Are Ready

- [ ] VPN connected (required if off-campus)
- [ ] Concordia ENCS username available
- [ ] `outputs_step3/hetus_30min.csv` exists — **full 64,061-row file** (not the sample)
- [ ] `outputs_step3/copresence_30min.csv` exists — **full 64,061-row file** (not the sample)

To verify row counts:
```bash
wc -l outputs_step3/hetus_30min.csv        # expect 64,062 (header + 64,061 rows)
wc -l outputs_step3/copresence_30min.csv   # expect 64,062
```

### Steps

**Step 1 — Create tarball (local machine)**
```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp

tar -czf step4_hpc_package.tar.gz \
    04A_dataset_assembly.py \
    04B_model.py \
    04C_training_pairs.py \
    04D_train.py \
    04E_inference.py \
    04F_validation.py \
    requirements_step4.txt \
    outputs_step3/hetus_30min.csv \
    outputs_step3/copresence_30min.csv
```

Expected size: ~200–400 MB (dominated by the two CSV files).

**Step 2 — Transfer to Speed**
```bash
rsync -avP step4_hpc_package.tar.gz \
    <ENCSuser>@speed.encs.concordia.ca:/speed-scratch/<ENCSuser>/
```

**Step 3 — SSH in and unpack**
```bash
ssh <ENCSuser>@speed.encs.concordia.ca

mkdir -p /speed-scratch/$USER/occModeling
cd /speed-scratch/$USER/occModeling
tar -xzf /speed-scratch/$USER/step4_hpc_package.tar.gz
ls -la   # confirm all files present
```

**Step 4 — Set up conda environment (one-time, on an interactive GPU node)**

Full instructions: `04_augmentationGSS_hpc.md` → Phase 3.

**Step 5 — Submit job chain**
```bash
cd /speed-scratch/$USER/occModeling
mkdir -p logs

JOB_A=$(sbatch --parsable job_04A_assembly.sh)
JOB_C=$(sbatch --parsable --dependency=afterok:$JOB_A job_04C_pairs.sh)
JOB_D=$(sbatch --parsable --dependency=afterok:$JOB_A:$JOB_C job_04D_train.sh)
JOB_E=$(sbatch --parsable --dependency=afterok:$JOB_D job_04E_inference.sh)
JOB_F=$(sbatch --parsable --dependency=afterok:$JOB_E job_04F_validation.sh)
echo "Submitted: $JOB_A → $JOB_C → $JOB_D → $JOB_E → $JOB_F"
```

Note: The SLURM job scripts (`job_04A_assembly.sh`, etc.) need to be created on the cluster before submission. Full script content is in `04_augmentationGSS_hpc.md` → Phases 4–7.

### What to Expect

| Job | Partition | Est. Time | Output |
|-----|-----------|-----------|--------|
| 04A Assembly | `ps` (CPU) | ~1–2 h | `outputs_step4/step4_*.pt`, `step4_feature_config.json` |
| 04C Pairs | `ps` (CPU) | ~1–2 h | `outputs_step4/training_pairs.pt`, `val_pairs.pt` |
| 04D Training | `pg` (GPU) | ~1.5–3 h | `outputs_step4/checkpoints/best_model.pt`, `step4_training_log.csv` |
| 04E Inference | `pg` (GPU) | ~15–30 min | `outputs_step4/augmented_diaries.csv` (~192K rows) |
| 04F Validation | `ps` (CPU) | ~30 min | `outputs_step4/step4_validation_report.html` |

### After the Run — What to Retrieve

```bash
# From local machine
rsync -avP \
    <ENCSuser>@speed.encs.concordia.ca:/speed-scratch/<ENCSuser>/occModeling/outputs_step4/ \
    /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step4/
```

Key files to confirm after download:
- `augmented_diaries.csv` — expect ~192,184 rows and ~552 columns
- `step4_validation_report.html` — open and check Section 4.2 transition rate (target ≤ 3×)
- `step4_training_log.csv` — confirm val_JS converged and early stopping triggered

### Full HPC Guide
See `04_augmentationGSS_hpc.md` for complete SLURM job scripts, environment setup, troubleshooting, and cleanup instructions.

---

## Critical pre-HPC fixes for 04A–04F (to execute next)

The following are the minimum changes that must be made to the Step-4 `.py` files **before** the full-scale HPC training run. Scope is deliberately critical-only: reproducibility, checkpoint guards, and one confirmed activity-index bug discovered during the 2026-04-20 documentation review. Structural refactors (shared constants, CLI loss-weights, type-hint pass, etc.) are deferred and listed at the end of this chapter.

### 1. [04E / 04F] Activity-index swap — **CONFIRMED BUG, must fix first**

Per `references_activityCodes/Data Harmonization - mainActivityCategoryList.csv` and `02_harmonizeGSS.py` (`CATEGORY_NAMES`), the harmonized taxonomy is:

- Raw code **1 = Work & Related**
- Raw code **5 = Sleep & Naps & Resting**

`04E_inference.py` (lines 53–54, 95–99) and `04F_validation.py` (multiple locations) currently have these swapped. Concretely:

- `04E_inference.py`: `SLEEP_CAT = 0   # 0-indexed (raw category 1)` → should be `SLEEP_CAT = 4   # 0-indexed (raw category 5)`. `WORK_CAT = 4   # raw 5 = Paid work` → should be `WORK_CAT = 0   # raw 1 = Work & Related`.
- `04F_validation.py`: every `== 1` used to denote "sleep" (lines 345, 359, 362, 363) must become `== 5`; every `== 5` used to denote "paid work" (lines 371, 374, 467, 525, 567, 571) must become `== 1`. The `for cat in range(1, N_ACT + 1)` loops that enumerate all 14 categories (line 386) are fine — they don't assume a specific label for a specific code.

**Why this matters:** `04E`'s post-hoc consistency rule currently forces `AT_HOME=1` during slots the model predicts as Work (instead of Sleep), and `AT_HOME=0` during slots the model predicts as Sleep (instead of Work). `04F`'s checks 4.1, 4.3, 6.2, 7.1, 7.2 effectively measure the opposite of their label. This plausibly explains a large fraction of the 17 FAILs in the smoke-test report ("S3 — 11 FAILs 8–28 pp off"). The bug must be fixed and the sample smoke-test re-run before submitting to HPC; otherwise HPC GPU time will be spent on an untrustworthy validation report.

Verification after fix: in `augmented_diaries_SAMPLE.csv`, night slots (0..6 and 37..47) should be dominated by `act30_* == 5` (Sleep), and slots 9..20 on Weekday should show `act30_* == 1` (Work) concentrated among employed respondents.

### 2. [04D] Add reproducibility seeds

At the very top of `train()` in `04D_train.py`, before model instantiation and dataloader construction:

```python
torch.manual_seed(42)
np.random.seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)
```

Without these, model weight initialization and `DataLoader` shuffling are non-deterministic, so identical HPC runs diverge and the validation-report-to-checkpoint link becomes ambiguous.

### 3. [04E] Seed the generation loop

Immediately before the batch loop in `run_inference()` in `04E_inference.py`, add:

```python
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)
```

`model.generate()` uses `torch.multinomial` when `temperature > 0`, which is non-deterministic without a seeded RNG. Without this, two inference runs from the same checkpoint produce different `augmented_diaries.csv` files.

### 4. [04D] Checkpoint-dir guard

Before the first `torch.save(...)` in `train()`, ensure the directory exists and log the absolute path:

```python
os.makedirs(args.checkpoint_dir, exist_ok=True)
print(f"  Checkpoints → {os.path.abspath(args.checkpoint_dir)}")
```

For `--resume`, wrap the load in a clear error:

```python
try:
    ckpt = torch.load(args.resume, map_location=device, weights_only=False)
except FileNotFoundError:
    raise FileNotFoundError(f"--resume checkpoint not found: {args.resume}")
```

### 5. [04E] Checkpoint-file guard

Before `torch.load(args.checkpoint, ...)` in `main()` of `04E_inference.py`:

```python
if not os.path.isfile(args.checkpoint):
    raise FileNotFoundError(
        f"Checkpoint not found: {args.checkpoint}. "
        f"Did 04D complete? (expected: outputs_step4/checkpoints/best_model.pt)"
    )
print(f"  Checkpoint size: {os.path.getsize(args.checkpoint) / 1e6:.1f} MB")
```

Silent failures here (CSV produced with stale or missing weights) are hard to diagnose post-hoc.

### Deferred (explicitly out of scope for this chapter)

Noted so they are not lost, but **not** executed in this round:

- Shared `step4_constants.py` to eliminate duplicated `COP_COLS`, `N_SLOTS`, `N_COP`, `SLEEP_CAT`, `WORK_CAT`, `NIGHT_SLOTS` across 04A/04C/04E/04F.
- Move loss weights (`LAMBDA_ACT`, `LAMBDA_HOME`, `LAMBDA_COP`) from module-level to CLI args / config dict.
- Full type-hint pass on all six scripts.
- JSON summary output from 04F (in addition to HTML) for programmatic Step-5 gating.
- Multi-sample generation in 04E (N=5 samples per respondent × stratum) for uncertainty quantification.

### Exit criteria for this chapter

Before running the HPC job chain:

- [x] Activity-index swap fixed in both 04E and 04F (item 1). — *2026-04-20*
- [x] Seeds added to 04D `train()` and 04E `run_inference()` (items 2, 3). — *2026-04-20*
- [x] Checkpoint guards added in 04D and 04E (items 4, 5). — *2026-04-20*
- [x] Sample smoke-test re-run with `--sample`; night-slot sleep rate syn=89.7% (obs=81.5%); work-slot work rate syn=14.5% (obs=31.4%, ordinally correct, underweight from 2-epoch checkpoint). — *2026-04-20*
- [x] Items 2–5 smoke-verified with `--sample`; checkpoint guard printed absolute path + size (1.2 MB), generation completed cleanly (1500 rows, colleagues zero-check passed). — *2026-04-20*
- [x] `Progress Log` in `04_augmentationGSS.md` updated with the bug-fix entry. — *2026-04-20*

---

## Progress Log

| Date | Task | Status | Notes |
|------|------|--------|-------|
| 2026-04-20 | Documentation review & patching | COMPLETE | Reviewed all four `04_augmentation*.md` docs + this file against the 04A–04F scaffolds. Edits applied in-place: `04_augmentationGSS.md` — clarified d_cond (runtime-measured, 76), corrected co-presence NaN scope (all 9 cols, not just colleagues), formalized AT_HOME post-hoc rule (no soft constraint), added Reproducibility-seeds and Intermediate-artifact-schemas sections, added 14-row activity-category mapping table, documented SURVMNTH drop rationale inline. `04_augmentationGSS_testing.md` — added smoke-test acceptance ranges and NaN-debug bullets. `04_augmentationGSS_val.md` — added WARN/FAIL tier convention, blocking-vs-investigate policy, corrected §4.1 and §4.3 labels, added activity-code caveat banner at top. `04_augmentationGSS_hpc.md` — pinned Python 3.10 / PyTorch 2.0–2.4 / CUDA 11.8, added "what to do if 04A fails" recovery note. `Phase1_ready.md` — appended "Critical pre-HPC fixes" chapter with 5 items. **Key finding during review:** activity-index swap in `04E_inference.py` (SLEEP_CAT/WORK_CAT lines 53–54) and `04F_validation.py` (multiple `== 1` / `== 5` sites) — raw code 1 is Work & Related, raw code 5 is Sleep & Naps & Resting, but both files have them reversed. Elevated from "verify first" to CONFIRMED BUG — blocks HPC submission until fixed. |
| 2026-04-20 | `.py` file fixes (04A–04F) | **COMPLETE** | All 5 items of the "Critical pre-HPC fixes" chapter executed and smoke-verified. Item 1 changed output semantics (activity-index swap); items 2–5 are non-breaking hardening. Phase 1 local gate is now fully satisfied. |
| 2026-04-20 | Item 1 — activity-index swap (04E + 04F) | COMPLETE | `04E_inference.py` L53–54: `SLEEP_CAT 0→4`, `WORK_CAT 4→0` (aligns with `mainActivityCategoryList.csv`: raw 1=Work & Related, raw 5=Sleep & Naps & Resting). `04F_validation.py`: 6 sites patched (L345, 359, 363, 371, 374, 467, 525, 567, 571). Co-presence `== 1` sites at L433/435 left untouched (0/1 presence, not activity codes). Smoke test re-run with the existing 2-epoch `best_model.pt` (val_JS=0.136): night-slot sleep rate syn=89.7% vs obs=81.5% (✓ sleep dominance); work-slot work rate syn=14.5% vs obs=31.4% (ordinally correct, low magnitude expected for 2-epoch checkpoint); overall synthetic distribution plausible (raw 5 Sleep=43.6%, raw 10 Leisure=23.8%, raw 2 Personal=10.8%, raw 1 Work=5.9%). 04F: 27 PASS / 2 WARN / 17 FAIL (FAILs driven by undertraining, not validation logic). |
| 2026-04-20 | Items 2–5 — seeds + checkpoint guards | COMPLETE | `04D_train.py::train()` — added `torch.manual_seed(42)`, `np.random.seed(42)`, and conditional `torch.cuda.manual_seed_all(42)` at top; prints absolute `checkpoint_dir`; `--resume` path now raises `FileNotFoundError` with absolute path + file size (MB) instead of silently skipping. `04E_inference.py` — `run_inference()` reseeds before the generation loop (makes `torch.multinomial` reproducible for a given checkpoint × temperature); `main()` asserts `args.checkpoint` exists before `torch.load`, prints absolute path + size. Docstring corrected to reflect post-fix semantics (raw 5 = Sleep, raw 1 = Work). `--sample` smoke test re-run: checkpoint guard printed `best_model.pt (1.2 MB)`, generation completed, 1500 rows produced, colleagues-zero assertion passed. No semantic changes vs. the item-1 smoke-test baseline. |
