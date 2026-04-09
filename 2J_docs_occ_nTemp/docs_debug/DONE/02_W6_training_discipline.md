# Training Discipline — Steps 4 and 6

**SWOT Item:** W6 — Two large DL models, no documented hyperparameter / reproducibility plan  
**Task:** TASK 5 in `00_SWOT_pipeline.md`  
**Date:** 2026-04-09  
**Applies to:** Step 4 (Conditional Transformer, Model 1) and Step 6 (progressive fine-tuning, Model 2)

> **How to use this block:** Copy the relevant sub-sections into the Step 4 and Step 6
> documentation when those specs are written. The values below are the declared defaults;
> adjust only with explicit justification recorded alongside the result.

---

## (a) Hyperparameter Search Budget

Before training begins, commit to a fixed grid. Do not add runs mid-experiment.

**Declared grid (6 runs):**

| Run | Learning rate | Batch size | Notes |
|-----|--------------|------------|-------|
| 1 | 1e-3 | 64 | High LR, small batch |
| 2 | 1e-3 | 256 | High LR, large batch |
| 3 | 3e-4 | 64 | Mid LR, small batch |
| 4 | 3e-4 | 256 | Mid LR, large batch ← **default start** |
| 5 | 1e-4 | 64 | Low LR, small batch |
| 6 | 1e-4 | 256 | Low LR, large batch |

All other hyperparameters (architecture depth, hidden size, dropout) are
**frozen** at their Step 4 spec values for the search. Only LR and batch size
vary. Six runs is the declared budget — stop here regardless of results.

**Selection rule:** Choose the run with the lowest validation loss on the
held-out 15% split (defined in Sub-step 4A). If two runs tie within 0.5%
relative, prefer the one with larger batch size (faster wall-clock time per
epoch on HPC).

**Why only 6 runs:** Model 1 trains in 1.5–3 hours per run on HPC. Six runs
= 9–18 hours of wall-clock time, which fits within a single HPC allocation
block. More combinations (e.g., adding dropout or hidden-size to the grid)
would require a second allocation and are not warranted given the signal levels
already established (AT_HOME baseline ≈ 68%).

---

## (b) Checkpointing Strategy

**Checkpoint on:** End of every epoch (not every N steps — epoch-level is
sufficient given run durations of 1.5–3 hours and typical 20–50 epoch counts).

**Folder:**

```
0_Occupancy/saved_models_cvae/step4_transformer/
    run_lr{LR}_bs{BS}_seed42/
        epoch_001.pt
        epoch_002.pt
        ...
        epoch_best.pt    ← symlink or copy of the best-val-loss checkpoint
        training_log.csv ← epoch, train_loss, val_loss, elapsed_sec
```

For Step 6 (progressive fine-tuning), use a sibling folder:

```
0_Occupancy/saved_models_cvae/step6_finetune/
    run_lr{LR}_bs{BS}_seed42_cycle{CYCLE}/
        epoch_001.pt
        ...
        epoch_best.pt
        training_log.csv
```

**Resume rule:** If a run crashes, restart from the last saved `.pt` file
using `torch.load()` + `model.load_state_dict()` + `optimizer.load_state_dict()`.
The training loop must log `epoch_start` at the top so it can be set to
`last_saved_epoch + 1` on resume.

**Retention:** Keep all epoch checkpoints until the best run is selected.
After selection, delete non-best epoch files from non-selected runs; keep only
`epoch_best.pt` and `training_log.csv` for archival. Best-run epoch files
may be kept if storage permits.

---

## (c) Reproducibility Seeds

Set the following at the top of every training script, before any model or
dataloader construction:

```python
import torch, numpy as np, random

SEED = 42

torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
np.random.seed(SEED)
random.seed(SEED)

# For deterministic cuDNN behaviour (may slow training ~10%)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**Record the seed in the output folder name** (e.g., `run_lr3e-4_bs256_seed42/`)
so that any result file is self-documenting about reproducibility.

**Paper reproducibility statement (draft):**

> All models were trained with `torch.manual_seed(42)`. Training used a
> pre-declared 6-run hyperparameter grid (3 learning rates × 2 batch sizes).
> Checkpoints were saved at the end of every epoch; the reported model is the
> checkpoint with minimum validation loss. Code and best-run checkpoints are
> archived at [repository].

**How to test before the long run:** Run 3 epochs on a 500-respondent
subsample with two identical seeds-42 calls. Confirm that `training_log.csv`
shows identical loss values in both runs to 4 decimal places. If they differ,
the seeding is incomplete (check DataLoader `worker_init_fn` and `generator`
parameters).

---

## Summary

| Concern | Decision | Where recorded |
|---------|----------|---------------|
| Hyperparameter search | 3 LR × 2 BS = 6 runs, stop at 6 | This doc + Step 4 spec |
| Checkpoint frequency | Every epoch | This doc + training script |
| Checkpoint location | `saved_models_cvae/step4_transformer/run_…/` | This doc + training script |
| Seed | `SEED = 42`, in folder name | This doc + training script header |
| Selection rule | Lowest val loss; tie → larger BS | This doc |
| Resuming a crash | Load last `.pt`, set `epoch_start` | This doc |

---

## Progress Log

**2026-04-09 — Task 5 executed (Sonnet)**

Document written. No source files modified. Ready to paste into Step 4 and
Step 6 documentation when those specs are drafted.
