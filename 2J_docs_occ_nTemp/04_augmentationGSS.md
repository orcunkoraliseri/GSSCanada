# Step 4 — Conditional Transformer Augmentation: Implementation Plan
### Model 1: Observed DDAY_STRATA → Complete 3-Strata Diary per Respondent
#### GSS Occupancy Pipeline — Detailed Implementation Specification

---

## GOAL

Each of 64,061 respondents has exactly **1 observed diary day** (one DDAY_STRATA: Weekday, Saturday, or Sunday). Step 4 trains a Conditional Transformer Encoder-Decoder to generate **synthetic schedules for the 2 unobserved DDAY_STRATA**, conditioned on the observed diary + demographic profile. Output: **~192,183 diary-days** (64,061 × 3 strata), each with 48 activity tokens + 48 AT_HOME tokens + 9×48 co-presence tokens at 30-min resolution.

---

## PREREQUISITES & INPUTS

### Input Files (from Step 3)

| File | Location | Content | Rows | Columns |
|---|---|---|---|---|
| `hetus_30min.csv` | `outputs_step3/` | 48 activity slots (`act30_001`–`act30_048`) + 48 AT_HOME slots (`hom30_001`–`hom30_048`) + 24 demographic/metadata columns | 64,061 | 120 |
| `copresence_30min.csv` | `outputs_step3/` | 9 co-presence columns tiled to 48 30-min slots each (`{ColName}30_001`–`{ColName}30_048`) + occID | 64,061 | 433 |

> **Note on `copresence_30min.csv`:** Produced by Phase I of `03_mergingGSS.py` (Step 3 extension). Values use original GSS coding: 1=present, 2=absent, pd.NA=missing. `colleagues30_*` is entirely NaN for 2005/2010 respondents (not measured in those cycles). Full spec in `docs_progress/03_mergingGSS_resolutionSampling.md` — Phase I section.
>
> **Important — Co-Presence NaN Rates:** The primary 8 co-presence columns (Alone through others) have non-trivial NaN rates at the episode level, which propagate to the 30-min slot level: **2005: ~20% NaN, 2010: ~19.3%, 2015: ~0.1%, 2022: ~6.8%** (overall ~12.5%). These NaNs represent episodes where co-presence was not recorded in the source GSS microdata. The availability mask in Sub-step 4A must account for this. Colleagues NaN: **2005/2010: 100%, 2015: ~0.1%, 2022: ~6.8%**.

### Confirmed Data Characteristics

| Property | Value |
|---|---|
| Total respondents | 64,061 (post DIARY_VALID filter) |
| Respondents per cycle | 2005: 19,221 / 2010: 15,114 / 2015: 17,390 / 2022: 12,336 |
| Slots per respondent | 48 (30-min, 4:00 AM to 3:50 AM next day) |
| Activity categories | 14 grouped (from TUI_01 crosswalk) |
| Co-presence columns | 9 binary (`colleagues` = NaN for 2005/2010) |
| DDAY_STRATA values | 1=Weekday, 2=Saturday, 3=Sunday |
| DDAY_STRATA distribution | ~72.8% Weekday, ~13.6% Saturday, ~13.6% Sunday |
| SURVMNTH | Not in Step 4 conditioning (dropped — see W3 decision); archived in Step 2 outputs only |

---

## IMPLEMENTATION SUB-STEPS

---

### Sub-step 4A — Unified Training Dataset Assembly

**Purpose:** Merge `hetus_30min.csv` and `copresence_30min.csv` into a single model-ready dataset, with all features encoded for Transformer input.

**Script:** `04A_dataset_assembly.py`

**Inputs:**
- `hetus_30min.csv` (demographic + activity + AT_HOME slots)
- `copresence_30min.csv` (co-presence slots from Step 3 Phase I)

**Operations:**

#### A1. Merge on occID
```python
df = hetus_30min.merge(copresence_30min, on='occID', how='inner', validate='1:1')
assert len(df) == 64061
```

#### A2. Feature Encoding — Demographic Conditioning Vector

| Column | Encoding | Dim |
|---|---|---|
| `AGEGRP` | One-hot | ~8 |
| `SEX` | One-hot | 2 |
| `MARSTH` | One-hot | ~5 |
| `HHSIZE` | One-hot | ~6 |
| `PR` | One-hot | ~13 |
| `CMA` | One-hot | ~4 |
| `KOL` | One-hot | ~4 |
| `LFTAG` | One-hot | ~5 |
| `TOTINC` | Continuous (standardized) | 1 |
| `HRSWRK` | One-hot | ~6 |
| `NOCS` | One-hot | ~10 |
| `COW` | One-hot | ~5 |
| `DDAY_STRATA` (observed) | One-hot | 3 |
| `CYCLE_YEAR` | Learned embedding | 4 (→ d_embed) |
| `COLLECT_MODE` | Binary flag | 1 |
| `TOTINC_SOURCE` | Binary flag (SELF/CRA) | 1 |
| **Total conditioning dim** | | **~78 raw → projected to d_model** |
| *(SURVMNTH dropped — see W3 decision)* | | — |

#### A3. Sequence Token Construction — Per-Slot Multivariate Token

Each of the 48 time slots becomes a single multivariate token with 11 features:

| Feature | Source Column | Type | Encoding |
|---|---|---|---|
| `occACT` | `act30_{s}` | Categorical (14) | Embedding lookup → d_act |
| `AT_HOME` | `hom30_{s}` | Binary | Scalar |
| `Alone` | `Alone30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `Spouse` | `Spouse30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `Children` | `Children30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `parents` | `parents30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `otherInFAMs` | `otherInFAMs30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `otherHHs` | `otherHHs30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `friends` | `friends30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `others` | `others30_{s}` | Binary | Scalar (recode: 1→1, 2→0) |
| `colleagues` | `colleagues30_{s}` | Binary | Scalar (recode: 1→1, 2→0; 0 for 2005/2010 NaN) |

> **Co-presence recoding:** GSS uses 1=Yes, 2=No. Recode to standard binary (1=present, 0=absent) before model input. NaN → 0 with a separate **availability mask** for loss computation.
>
> **NaN handling detail:** Co-presence NaN is not limited to colleagues — the primary 8 columns also have missing data (2005: ~20%, 2010: ~19.3%, 2015: ~0.1%, 2022: ~6.8% of slots). Build a per-slot boolean availability mask `cop_avail[respondent, slot, col]` = True where the source value was non-NaN. During training, the co-presence BCE loss must be multiplied by this mask so the model is not penalized for predicting values where no ground truth exists. During inference, generate all 9 co-presence values regardless of source availability.

#### A4. Train/Val/Test Split Strategy

```
Split by respondent (occID), stratified by CYCLE_YEAR × DDAY_STRATA:
  Train: 70%  (~44,843 respondents)
  Val:   15%  (~9,609 respondents)
  Test:  15%  (~9,609 respondents)

Stratification ensures each split has proportional representation of:
  - All 4 cycles
  - All 3 DDAY_STRATA
  - Balanced demographic coverage
```

> **Why not cross-cycle holdout here (unlike Step 6)?** Step 4's task is learning schedule structure *within* a cycle (observed stratum → unobserved strata). The temporal generalization test belongs to Step 6. Here we use standard stratified splitting.

**Output:**
- `step4_train.pt` / `step4_val.pt` / `step4_test.pt` (PyTorch tensor datasets)
- `step4_feature_config.json` (encoding dimensions, column mappings, masks)

**Validation checks (04A):**
- [ ] No data leakage: occID sets are disjoint across train/val/test
- [ ] Stratification check: CYCLE_YEAR × DDAY_STRATA proportions within ±2% across splits
- [ ] All demographic columns have no unexpected NaN (SURVMNTH not present — dropped from Step 3 output per W3 decision)
- [ ] Co-presence recoding verified: all non-NaN values ∈ {0, 1} after recode
- [ ] colleagues = 0 for all 2005/2010 rows (confirmed masked)
- [ ] Availability mask shape matches (n_respondents, 48, 9) — True where source co-presence was non-NaN
- [ ] NaN rate in availability mask matches expected: ~20% for 2005, ~19.3% for 2010, ~0.1% for 2015, ~6.8% for 2022 (primary 8 cols); 100% for colleagues 2005/2010
- [ ] Total conditioning vector dimension logged

---

### Sub-step 4B — Transformer Architecture Definition

**Script:** `04B_model.py`

#### Architecture: Conditional Transformer Encoder-Decoder

```
┌─────────────────────────────────────────────────────────┐
│                    ENCODER                               │
│                                                          │
│  Input: 48 slot tokens (each = 11 features embedded)    │
│       + 1 [CLS] token (demographic conditioning vector) │
│       + sinusoidal positional encoding (48 positions)    │
│                                                          │
│  Slot embedding:                                         │
│    occACT → Embedding(14, d_act=32) → concat with       │
│    [AT_HOME, 9×co-presence binary] → Linear → d_model   │
│                                                          │
│  Demographic conditioning:                               │
│    [one-hot demographics + continuous features]           │
│    → MLP(d_cond_raw, 256, d_model)                      │
│    → prepended as [CLS] token at position 0              │
│                                                          │
│  Transformer Encoder:                                    │
│    N_enc = 6 layers                                      │
│    d_model = 256                                         │
│    n_heads = 8                                           │
│    d_ff = 1024                                           │
│    dropout = 0.1                                         │
│    Activation: GELU                                      │
│                                                          │
│  Output: 49 encoded tokens (1 CLS + 48 slot states)     │
└─────────────────┬───────────────────────────────────────┘
                  │ cross-attention
┌─────────────────▼───────────────────────────────────────┐
│                    DECODER                               │
│                                                          │
│  Input: 48 target slot queries                           │
│       + target DDAY_STRATA embedding (one-hot 3 → d_model)│
│       + sinusoidal positional encoding (48 positions)    │
│                                                          │
│  Training mode (teacher forcing):                        │
│    Target = ground-truth slots from paired respondent    │
│    Causal mask: each slot attends to ≤ current position  │
│                                                          │
│  Inference mode (autoregressive):                        │
│    Start with [BOS] token + target DDAY_STRATA          │
│    Generate slot-by-slot with sampling/argmax            │
│                                                          │
│  Transformer Decoder:                                    │
│    N_dec = 6 layers                                      │
│    d_model = 256 (shared with encoder)                   │
│    n_heads = 8                                           │
│    d_ff = 1024                                           │
│    dropout = 0.1                                         │
│                                                          │
│  Output heads (per slot):                                │
│    Activity head: Linear(d_model, 14) → softmax         │
│    AT_HOME head:  Linear(d_model, 1)  → sigmoid         │
│    Co-pres head:  Linear(d_model, 9)  → sigmoid (×48)   │
└─────────────────────────────────────────────────────────┘
```

#### Hyperparameter Summary

| Parameter | Value | Notes |
|---|---|---|
| `d_model` | 256 | Encoder/decoder hidden dimension |
| `n_heads` | 8 | Multi-head attention |
| `d_ff` | 1024 | Feed-forward hidden dimension |
| `N_enc` | 6 | Encoder layers |
| `N_dec` | 6 | Decoder layers |
| `d_act` | 32 | Activity category embedding dimension |
| `dropout` | 0.1 | Applied to attention + FF layers |
| `max_seq_len` | 48 | 30-min slots per day |
| `n_activity_classes` | 14 | Grouped TUI_01 categories |
| `n_copresence` | 9 | Binary co-presence columns |
| `activation` | GELU | Standard for modern Transformers |

#### Positional Encoding
Standard sinusoidal encoding for 48 positions. Temporal semantics (time-of-day) are implicitly captured by position since all diaries start at 4:00 AM.

---

### Sub-step 4C — Training Pair Construction (Supervision Strategy)

**Purpose:** Transformers need paired (input, target) examples. Since each respondent has only 1 diary, we construct approximate supervision pairs from **demographically similar respondents observed on different DDAY_STRATA**.

**Script:** `04C_training_pairs.py`

#### Pair Construction Logic

```
For each respondent R_i with observed DDAY_STRATA = S_obs:
  For each target stratum S_target ∈ {1,2,3} \ {S_obs}:
    1. Find candidate pool: respondents in same CYCLE_YEAR with
       DDAY_STRATA = S_target
    2. Compute demographic similarity score using:
       - Exact match: AGEGRP, SEX, MARSTH, HHSIZE, LFTAG
       - Fuzzy match: PR, CMA, HRSWRK, NOCS, TOTINC (within ±1 bin)
    3. Select top-K nearest neighbors (K=5) as supervision targets
    4. During training: randomly sample 1 of K neighbors per epoch
       → provides stochastic diversity in supervision signal

Output per training example:
  encoder_input  = R_i's 48-slot diary (observed S_obs)
  decoder_target = neighbor's 48-slot diary (observed S_target)
  condition_obs  = S_obs one-hot
  condition_tgt  = S_target one-hot
  demographics   = R_i's demographic vector
```

#### Key Design Decisions

| Decision | Rationale |
|---|---|
| K=5 nearest neighbors | Avoids overfitting to a single target; stochastic sampling adds regularization |
| Exact match on core demographics | AGEGRP + SEX + MARSTH + HHSIZE + LFTAG are strongest predictors of schedule structure |
| Within-cycle matching only | Cross-cycle matching would conflate temporal trend with augmentation |
| Sample 1-of-K per epoch | Different neighbor each epoch → model learns distribution, not point estimate |

#### Pair Count Estimate

```
64,061 respondents × 2 target strata × 1 sampled pair = ~128,122 training pairs per epoch
With K=5 pool, effective unique pairs over training: ~640,000+
```

#### Imbalance Handling (DDAY_STRATA)

Weekday respondents (~72.8%) outnumber Saturday (~13.6%) and Sunday (~13.6%). This means:
- **Generating Saturday/Sunday from Weekday**: large encoder pool, small target pool → some target reuse
- **Generating Weekday from Saturday/Sunday**: small encoder pool, large target pool → abundant targets

Mitigation: oversample weekend-observed respondents as encoders during training (weighted sampler with inverse DDAY_STRATA frequency).

**Validation checks (04C):**
- [ ] Every respondent has exactly 2 target strata assigned
- [ ] All K neighbors share same CYCLE_YEAR as source respondent
- [ ] Demographic match quality: mean exact-match score ≥ 3 of 5 core attributes
- [ ] No self-pairing (R_i never paired with itself)
- [ ] Target pool coverage: log how many unique targets are reused and how often

---

### Sub-step 4D — Training Loop

**Script:** `04D_train.py`

#### Loss Function

```python
L_total = λ_act * L_activity + λ_home * L_at_home + λ_cop * L_copresence

Where:
  L_activity   = CrossEntropyLoss(pred_act, target_act)      # 14 classes × 48 slots
  L_at_home    = BCEWithLogitsLoss(pred_home, target_home)    # binary × 48 slots
  L_copresence = BCEWithLogitsLoss(pred_cop, target_cop)      # 9 cols × 48 slots
                 * copresence_mask                             # zero out colleagues for 2005/2010

Loss weights (initial):
  λ_act  = 1.0   (primary objective)
  λ_home = 0.5   (correlated with activity but distinct)
  λ_cop  = 0.3   (auxiliary; noisier signal)
```

#### Consistency Constraint (Post-Hoc or Soft)

AT_HOME must be logically consistent with occACT:
- Sleep (category 1) at night → AT_HOME should be 1
- Paid work (category 5) → AT_HOME should be 0 unless POWST indicates WFH

Implementation options:
1. **Soft constraint (recommended):** Add consistency penalty term to loss — penalize AT_HOME=0 when predicted activity is sleep/personal care
2. **Post-hoc correction:** After generation, enforce deterministic rules on AT_HOME based on activity

#### Training Configuration

| Parameter | Value |
|---|---|
| Optimizer | AdamW |
| Learning rate | 1e-4 (with warm-up) |
| LR schedule | Linear warm-up (2000 steps) → cosine decay |
| Batch size | 256 (pairs) |
| Max epochs | 100 |
| Early stopping | Patience = 10 epochs on val JS divergence |
| Gradient clipping | max_norm = 1.0 |
| Mixed precision | FP16 (AMP) on GPU |

#### Training Procedure

```
For each epoch:
  1. Shuffle training pairs; resample 1-of-K neighbor per respondent
  2. For each batch:
     a. Encode observed diary (encoder input)
     b. Decode target diary with teacher forcing (decoder input = shifted target)
     c. Compute L_total
     d. Backprop + optimizer step
  3. Validation pass (no teacher forcing):
     a. Generate synthetic diaries for val respondents (argmax decoding)
     b. Compute per-stratum JS divergence vs. observed val targets
     c. Compute co-presence prevalence match per column
  4. Log metrics; check early stopping criterion
  5. Save checkpoint if best val JS divergence
```

#### Co-Presence Availability Masking Detail

The co-presence loss uses a **per-slot availability mask** (not just a per-cycle colleagues mask), because the primary 8 columns also have NaN data (~12.5% overall):

```python
# cop_avail: boolean tensor (batch, 48, 9) — True where source co-presence was non-NaN
# Built during 04A dataset assembly from the raw copresence_30min.csv

# In loss computation:
# L_copresence = BCEWithLogitsLoss(pred_cop, target_cop, reduction='none')  # (batch, 48, 9)
# Apply availability mask: zero out loss for slots/columns with no ground truth
cop_loss_masked = cop_loss_raw * cop_avail.float()  # (batch, 48, 9)

# Colleagues is a special case: 100% NaN for 2005/2010 (already handled by cop_avail)
# but additionally enforce explicit zero for safety:
colleagues_mask = (cycle_year >= 2015).float()  # shape: (batch,)
cop_loss_masked[:, :, 8] *= colleagues_mask.unsqueeze(-1)

# Reduce: mean over available slots only
cop_loss = cop_loss_masked.sum() / cop_avail.float().sum().clamp(min=1)
```

**Validation checks (04D):**
- [ ] Training loss decreases monotonically over first 10 epochs
- [ ] Validation JS divergence improves for ≥20 epochs before plateau
- [ ] No NaN/Inf in loss values
- [ ] Gradient norm stays below clipping threshold after warm-up
- [ ] Colleagues loss = 0 for all 2005/2010 batches (masking verified)
- [ ] GPU memory usage within HPC node limits (log peak memory)

---

### Sub-step 4E — Inference & Synthetic Diary Generation

**Script:** `04E_inference.py`

#### Generation Procedure

```
For each respondent R_i (all 64,061):
  Load best checkpoint from 4D

  For S_target in {1, 2, 3}:
    If S_target == R_i.DDAY_STRATA:
      → Copy observed diary directly (no generation needed)
    Else:
      → Feed R_i's observed diary + demographics into encoder
      → Set decoder target condition = S_target
      → Generate 48 slots autoregressively:
          - Activity: sample from softmax (temperature τ = 0.8)
                      or argmax (for deterministic output)
          - AT_HOME: threshold sigmoid at 0.5
          - Co-presence: threshold each column's sigmoid at 0.5
      → Apply post-hoc consistency rules:
          - If activity = Sleep AND slot ∈ night range → force AT_HOME = 1
          - If activity = PaidWork AND no WFH flag → force AT_HOME = 0
      → Zero out colleagues for 2005/2010 respondents

  Output row for R_i × S_target:
    [occID, CYCLE_YEAR, DDAY_STRATA, demographics...,
     act30_001..act30_048, hom30_001..hom30_048,
     {col}30_001..{col}30_048 for each co-presence column,
     IS_SYNTHETIC flag (0=observed, 1=generated)]
```

#### Temperature Sampling Strategy

| Setting | τ | Use case |
|---|---|---|
| Deterministic | argmax | Single "most likely" schedule per respondent × stratum |
| Low temperature | 0.8 | Slight diversity while staying close to mode |
| Standard | 1.0 | Full model distribution (for ensemble/multiple samples) |

Default: **τ = 0.8** for a single pass. If diversity analysis is needed, generate N=5 samples per target stratum and report inter-sample variance.

**Output:** `augmented_diaries.csv`

```
~192,183 rows (64,061 respondents × 3 DDAY_STRATA)
Columns:
  - occID, CYCLE_YEAR, SURVYEAR, DDAY_STRATA, IS_SYNTHETIC
  - All demographic columns from hetus_30min.csv
  - act30_001..act30_048 (activity, 14 categories)
  - hom30_001..hom30_048 (AT_HOME, binary)
  - Alone30_001..Alone30_048 (binary)
  - Spouse30_001..Spouse30_048 (binary)
  - ... (all 9 co-presence × 48 slots)
  - colleagues30_001..colleagues30_048 (NaN for 2005/2010)
  - WGHT_PER (original survey weight, carried forward)

Total columns: ~24 metadata + 48 act + 48 hom + 432 copresence = ~552 columns
```

---

### Sub-step 4F — Validation & Quality Assurance

**Script:** `04F_validation.py`

> Full validation specification is in the separate document: **`04_augmentationGSS_val.md`**
>
> 8 validation sections covering: training curves, activity distribution JS divergence, AT_HOME rate consistency, temporal structure plausibility, co-presence prevalence match, demographic conditioning fidelity, cross-stratum consistency, and summary statistics.
>
> **Output:** `outputs_step4/step4_validation_report.html`

---

## OUTPUT FILES

| File | Location | Content |
|---|---|---|
| `step4_train.pt` | `outputs_step4/` | Training tensor dataset |
| `step4_val.pt` | `outputs_step4/` | Validation tensor dataset |
| `step4_test.pt` | `outputs_step4/` | Test tensor dataset |
| `step4_feature_config.json` | `outputs_step4/` | Feature encodings, dimensions, masks |
| `best_model.pt` | `outputs_step4/checkpoints/` | Best model checkpoint (lowest val JS) |
| `augmented_diaries.csv` | `outputs_step4/` | Full augmented dataset (~192,183 rows × ~552 cols) |
| `step4_validation_report.html` | `outputs_step4/` | Validation report with all Sections 1–8 checks |
| `step4_training_log.csv` | `outputs_step4/` | Per-epoch training metrics |

---

## SCRIPT EXECUTION ORDER

```
04A_dataset_assembly.py          # Merge hetus_30min + copresence_30min + encode → training-ready dataset
04B_model.py                     # Architecture definition (imported, not run)
04C_training_pairs.py            # Construct demographic-match supervision pairs
04D_train.py                     # Training loop (HPC GPU)
04E_inference.py                 # Generate synthetic diaries for all respondents
04F_validation.py                # Validation report
```

**Prerequisites from Step 3:**
- `outputs_step3/hetus_30min.csv` (Phase H)
- `outputs_step3/copresence_30min.csv` (Phase I)

**Dependencies:** 04A → (04B, 04C) → 04D → 04E → 04F

> **Python import note:** Script names beginning with a digit (e.g., `04B_model.py`) cannot be imported with a plain `import` statement. Use `importlib.import_module("04B_model")` to import them, or place shared code in a helper module with a letter-prefixed name (e.g., `step4_model.py`).

---

## HPC REQUIREMENTS (Concordia)

| Resource | Estimate |
|---|---|
| GPU | 1× A100 (40 GB) or V100 (32 GB) |
| GPU memory peak | ~8–12 GB (batch=256, seq_len=48, d_model=256) |
| Training time | ~1.5–3 hrs (100 epochs with early stopping) |
| Inference time | ~15–30 min (64K respondents × 2 target strata) |
| Storage | ~2 GB (augmented CSV) + ~500 MB (checkpoints) |
| Python dependencies | PyTorch ≥ 2.0, numpy, pandas, scikit-learn, matplotlib |

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|---|---|---|
| Demographic matching yields poor supervision pairs (sparse combinations) | Model learns noise | Relax matching: drop lowest-priority attributes; increase K to 10 |
| Weekend respondent scarcity (~13.6% each) limits target pool for Weekday generation | Target reuse/overfitting | Oversample weekend respondents; augment with noise injection |
| AT_HOME–activity inconsistency in generated diaries | Invalid BEM schedules | Post-hoc consistency correction (deterministic rules) |
| Colleagues column all-NaN for 2005/2010 leaks information about cycle | Model uses colleagues as cycle proxy | Masking in loss + set to 0 in encoder input; verify no leakage in validation |
| DDAY_STRATA imbalance (73/14/14) causes mode collapse toward weekday patterns | Poor weekend generation | Weighted sampler; per-stratum JS monitoring; stratum-balanced batches |

---

## CONNECTION TO DOWNSTREAM STEPS

- **Step 5 (Census Linkage):** Uses augmented demographic profiles (all 192K diary-days) for archetype clustering
- **Step 6 (Forecasting):** Uses augmented_diaries.csv as longitudinal anchors; the fine-tuned Model 1 decoder is reused in Step 6's schedule generation
- **Step 7 (BEM Integration):** Requires all 3 DDAY_STRATA per respondent for weekday/Saturday/Sunday schedule generation; AT_HOME + co-presence slots directly map to EnergyPlus occupancy schedules

---

## Progress Log

| Date | Script | Status | Notes |
|------|--------|--------|-------|
| 2026-04-10 | sample_for_testing.py | COMPLETE | Exact implementation from testing spec. Stratified 500-respondent sample by CYCLE_YEAR × DDAY_STRATA. |
| 2026-04-10 | 04A_dataset_assembly.py | COMPLETE | Merges hetus_30min + copresence_30min on occID. Encodes CAT_COLS (12 one-hot) + TOTINC (standardized) + COLLECT_MODE + TOTINC_SOURCE as conditioning vector. ATTSCH and POWST absent from Step 3 output — skipped without error. CYCLE_YEAR saved separately as integer index (0–3) for model's Embedding layer. cop_avail mask shape (n, 48, 9) built from ~isnan(). Saves step4_{train,val,test}.pt + step4_feature_config.json + metadata CSVs. |
| 2026-04-10 | 04B_model.py | COMPLETE | ConditionalTransformer with batch_first=True (requires PyTorch ≥ 2.0). Slot linear takes d_act + 10 (1 AT_HOME + 9 co-pres). CLS MLP: (d_cond + d_cycle) → 256 → d_model. Encoder: 49 positions (CLS + 48 slots). Decoder: 48 positions (BOS + 47 shifted GT slots). Target strata via Linear(3, d_model) added to all decoder positions. Autoregressive generate() included. DEFAULT_CONFIG and TEST_CONFIG exported. |
| 2026-04-10 | 04C_training_pairs.py | COMPLETE | K=5 neighbors per (source, target_strata). Exact match on AGEGRP/SEX/MARSTH/HHSIZE/LFTAG; fuzzy (±1 bin) on PR/CMA/HRSWRK/NOCS/TOTINC. TOTINC binned into 6 quantile bins per CYCLE_YEAR. Saves training_pairs.pt and val_pairs.pt. Deviations: also builds val_pairs (spec only mentioned training_pairs) to support validation in 04D. |
| 2026-04-10 | 04D_train.py | COMPLETE | Full training loop with teacher forcing, co-presence availability masking, colleagues defense-in-depth zero for 2005/2010. AdamW + linear warm-up → cosine decay. WeightedRandomSampler for DDAY_STRATA imbalance. FP16 via torch.amp.GradScaler. Validation samples 200 val respondents with argmax decoding and per-stratum JS. Saves best_model.pt, last_checkpoint.pt, step4_training_log.csv. |
| 2026-04-10 | 04E_inference.py | COMPLETE | Loads all three .pt splits and concatenates. Per-respondent × stratum: copies observed (IS_SYNTHETIC=0) or autoregressively generates (IS_SYNTHETIC=1). Post-hoc consistency: Sleep (cat 1 raw, night slots) → AT_HOME=1; PaidWork (cat 5 raw) → AT_HOME=0. Colleagues = NaN for 2005/2010 observed rows; 0 for 2005/2010 synthetic rows. Output: augmented_diaries.csv with all metadata merged. |
| 2026-04-10 | 04F_validation.py | COMPLETE | AugmentationValidator class with 8 sections. Uses scipy.spatial.distance.jensenshannon. Chart output embedded as base64 PNG in HTML. Sample mode uses relaxed thresholds (JS < 0.20 vs 0.05 full). Deviations: Section 4 uses raw activity category 5 for paid-work check (matches 1-indexed data); Section 1 relies on training log CSV being present. |
| 2026-04-10 | ALL SCRIPTS | COMPLETE | Full pipeline chain: sample_for_testing → 04A → (04B, 04C) → 04D → 04E → 04F. All scripts accept --sample flag. All use importlib for 04B import where needed. Activity stored as 0-indexed in tensors (shifted from 1-indexed raw values). |
| 2026-04-10 | SMOKE TESTS | COMPLETE | All 7 --sample smoke tests passed. Three bugs fixed during testing: (1) 04A: TOTINC_SOURCE is a string column ('SELF'/'CRA') — fixed with pd.factorize() before float cast. (2) 04E: metadata merge was on occID only, causing cartesian product for non-unique occIDs across cycles — fixed to merge on ["occID", "CYCLE_YEAR"]. (3) 04F: _load_data() was always loading full-dataset filenames — fixed to use _SAMPLE suffix when sample_mode=True. Results: 04D trained 5 epochs (val_JS=0.136); 04E produced 1500 rows (500×3, 500 observed + 1000 synthetic); 04F produced HTML report (28 PASS / 1 WARN / 17 FAIL — FAILs expected for 5-epoch undertrained model). |
