# Step 4 — Local Testing Plan: Sample Training & Data Inspection

## Goal

Manually test the full Step 4 pipeline on a small sample (500 respondents) on a local machine **before** HPC submission. The purpose is to:

1. **See** exactly what data goes into the model (tensor shapes, feature values, conditioning vectors)
2. **See** exactly what comes out (generated slot tokens, decoded schedules)
3. Verify the training loop runs without errors (loss decreases, no NaN)
4. Confirm the full pipeline chain works end-to-end: data assembly → pairs → train → infer → validate

This is a **manual inspection workflow**, not a performance benchmark. Use small data, few epochs, and print everything.

---

## Sample Data Preparation

### Create a 500-Respondent Sample

From the full 64,061 respondents, extract a stratified sample of ~500 that preserves the CYCLE_YEAR × DDAY_STRATA distribution.

```python
"""sample_for_testing.py — Run once to create sample data."""
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

# Load full data
hetus = pd.read_csv("outputs_step3/hetus_30min.csv", low_memory=False)
cop   = pd.read_csv("outputs_step3/copresence_30min.csv", low_memory=False)

# Stratify by CYCLE_YEAR × DDAY_STRATA (12 cells)
hetus["strat_key"] = hetus["CYCLE_YEAR"].astype(str) + "_" + hetus["DDAY_STRATA"].astype(str)

sss = StratifiedShuffleSplit(n_splits=1, train_size=500, random_state=42)
sample_idx, _ = next(sss.split(hetus, hetus["strat_key"]))

hetus_sample = hetus.iloc[sample_idx].drop(columns=["strat_key"]).reset_index(drop=True)
cop_sample   = cop[cop["occID"].isin(hetus_sample["occID"])].reset_index(drop=True)

# Save
hetus_sample.to_csv("outputs_step3/hetus_30min_SAMPLE.csv", index=False)
cop_sample.to_csv("outputs_step3/copresence_30min_SAMPLE.csv", index=False)

print(f"Sample: {len(hetus_sample)} respondents")
print(hetus_sample.groupby(["CYCLE_YEAR", "DDAY_STRATA"]).size().unstack(fill_value=0))
```

Expected output (~500 rows):

| DDAY_STRATA | 1 (Weekday) | 2 (Saturday) | 3 (Sunday) |
|---|---|---|---|
| 2005 | ~107 | ~21 | ~23 |
| 2010 | ~85 | ~16 | ~17 |
| 2015 | ~96 | ~19 | ~20 |
| 2022 | ~70 | ~13 | ~14 |

---

## Test 1 — Dataset Assembly (04A)

### What to inspect

Run `04A_dataset_assembly.py` with the sample files and print intermediate states.

### Inspection checklist

#### 1a. Merge result

```python
# After merging hetus_sample + cop_sample on occID:
print(f"Merged shape: {df.shape}")          # expect (500, 120 + 432 = 552)
print(f"occID unique: {df['occID'].nunique()}")  # expect 500
print(df.head(3))
```

#### 1b. Demographic conditioning vector (for one respondent)

```python
# Pick a single respondent and print their raw demographics:
row = df.iloc[0]
print("=== RAW DEMOGRAPHICS ===")
for col in ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR", "CMA", "KOL",
            "LFTAG", "TOTINC", "HRSWRK", "NOCS", "COW",
            "DDAY_STRATA", "SURVYEAR", "COLLECT_MODE", "TOTINC_SOURCE"]:
    print(f"  {col:>16}: {row[col]}")

# After one-hot encoding:
print(f"\n=== CONDITIONING VECTOR (encoded) ===")
print(f"  Shape: {cond_vector.shape}")       # expect (~91,) or (d_model,) after projection
print(f"  Non-zero entries: {(cond_vector != 0).sum()}")
print(f"  First 20 values: {cond_vector[:20]}")
```

#### 1c. Sequence tokens (for one respondent, one slot)

```python
# Print the 11-feature token for slot 1 (04:00–04:29):
print("=== SLOT 1 TOKEN (respondent 0) ===")
print(f"  occACT (raw):      {row['act30_001']}")  # integer 1-14
print(f"  AT_HOME (raw):     {row['hom30_001']}")  # 0 or 1
print(f"  Alone (raw→bin):   {row['Alone30_001']} → {1 if row['Alone30_001']==1 else 0}")
print(f"  Spouse (raw→bin):  {row['Spouse30_001']} → {1 if row['Spouse30_001']==1 else 0}")
print(f"  Children:          {row['Children30_001']} → ...")
print(f"  parents:           {row['parents30_001']} → ...")
print(f"  otherInFAMs:       {row['otherInFAMs30_001']} → ...")
print(f"  otherHHs:          {row['otherHHs30_001']} → ...")
print(f"  friends:           {row['friends30_001']} → ...")
print(f"  others:            {row['others30_001']} → ...")
print(f"  colleagues:        {row['colleagues30_001']} → ...")
# After encoding to tensor:
print(f"\n  Token tensor shape: {token_tensor.shape}")  # expect (11,) or (d_model,) after embedding
print(f"  Token tensor values: {token_tensor}")
```

#### 1d. Full sequence tensor (for one respondent)

```python
# Full 48-slot sequence:
print(f"=== FULL SEQUENCE TENSOR ===")
print(f"  Shape: {seq_tensor.shape}")        # expect (48, 11) raw or (48, d_model) after embedding
print(f"  Activity sequence: {seq_tensor[:, 0].tolist()}")  # 48 activity codes
print(f"  AT_HOME sequence:  {seq_tensor[:, 1].tolist()}")  # 48 binary values
```

#### 1e. Co-presence NaN and availability mask

```python
# Check NaN rates per cycle BEFORE recoding:
for cycle in [2005, 2010, 2015, 2022]:
    sub = df[df["CYCLE_YEAR"] == cycle]
    cop_cols_30 = [c for c in sub.columns if "Alone30_" in c]  # any primary co-pres
    nan_rate = sub[cop_cols_30].isna().mean().mean() * 100
    col_cols_30 = [c for c in sub.columns if "colleagues30_" in c]
    col_nan = sub[col_cols_30].isna().mean().mean() * 100
    print(f"  {cycle}: primary 8 NaN={nan_rate:.1f}%, colleagues NaN={col_nan:.1f}%")
# Expected: 2005 ~20%, 2010 ~19.3%, 2015 ~0.1%, 2022 ~6.8% (primary 8)
# Expected: 2005/2010 = 100% (colleagues), 2015/2022 ~same as primary

# After building availability mask:
print(f"  cop_avail shape: {cop_avail.shape}")  # (500, 48, 9)
print(f"  cop_avail True rate: {cop_avail.float().mean():.3f}")  # ~0.85 overall
```

#### 1f. Train/val/test split

```python
# With 500 respondents: ~350 train, ~75 val, ~75 test
print(f"Train: {len(train_ids)} | Val: {len(val_ids)} | Test: {len(test_ids)}")
print(f"Train DDAY_STRATA dist: {train_df['DDAY_STRATA'].value_counts().to_dict()}")
print(f"Val   DDAY_STRATA dist: {val_df['DDAY_STRATA'].value_counts().to_dict()}")

# Confirm no overlap
assert len(set(train_ids) & set(val_ids)) == 0, "LEAK!"
assert len(set(train_ids) & set(test_ids)) == 0, "LEAK!"
```

---

## Test 2 — Training Pairs (04C)

### What to inspect

#### 2a. Pair structure

```python
# For one respondent, print their matching pair:
print("=== SOURCE RESPONDENT ===")
print(f"  occID: {src['occID']}")
print(f"  CYCLE_YEAR: {src['CYCLE_YEAR']}")
print(f"  DDAY_STRATA (observed): {src['DDAY_STRATA']}")
print(f"  AGEGRP={src['AGEGRP']}, SEX={src['SEX']}, MARSTH={src['MARSTH']}")

print(f"\n=== TARGET STRATA: {target_strata} ===")
print(f"  Top-K=5 neighbor occIDs: {neighbor_ids}")
print(f"  Sampled neighbor: occID={neighbor['occID']}")
print(f"  Neighbor DDAY_STRATA: {neighbor['DDAY_STRATA']}")  # must == target_strata
print(f"  Neighbor CYCLE_YEAR: {neighbor['CYCLE_YEAR']}")     # must == source CYCLE_YEAR
print(f"  Demographic match score: {match_score}/5")
```

#### 2b. Pair count

```python
# With 500 respondents × 2 target strata = ~1000 pairs (sample 1 of K)
print(f"Total training pairs: {len(pairs)}")          # expect ~700 (70% of 1000)
print(f"Pairs per target strata: {pairs_per_strata}")  # expect ~350 each

# Check no self-pairing
for src_id, tgt_id in pairs:
    assert src_id != tgt_id
```

#### 2c. Imbalance check

```python
# How many unique targets are reused?
from collections import Counter
tgt_counts = Counter(tgt_id for _, tgt_id in pairs)
print(f"Unique targets: {len(tgt_counts)} / {len(pairs)} pairs")
print(f"Most reused target: occID={tgt_counts.most_common(1)[0]}")
```

---

## Test 3 — Model Forward Pass (04B + 04D)

### What to inspect

Run a single forward pass (1 batch) with no gradient, to see tensor shapes and output distributions.

#### 3a. Model architecture summary

```python
from 04B_model import ConditionalTransformer  # adjust import

model = ConditionalTransformer(config)
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")  # expect ~5–15M for d_model=256

# Print layer structure
print(model)
```

#### 3b. Single batch forward pass

```python
# Grab one batch from the data loader (batch_size=8 for testing)
batch = next(iter(train_loader))

print("=== ENCODER INPUT ===")
print(f"  Observed diary:     {batch['encoder_seq'].shape}")    # (8, 48, 11)
print(f"  Demographics:       {batch['demographics'].shape}")   # (8, ~91)
print(f"  Observed strata:    {batch['obs_strata'].shape}")     # (8, 3) one-hot

print("=== DECODER INPUT ===")
print(f"  Target diary:       {batch['decoder_target'].shape}") # (8, 48, 11)
print(f"  Target strata:      {batch['tgt_strata'].shape}")     # (8, 3) one-hot

# Forward pass
with torch.no_grad():
    output = model(batch)

print("\n=== MODEL OUTPUT ===")
print(f"  Activity logits:    {output['act_logits'].shape}")    # (8, 48, 14)
print(f"  AT_HOME logits:     {output['home_logits'].shape}")   # (8, 48, 1)
print(f"  Co-presence logits: {output['cop_logits'].shape}")    # (8, 48, 9)

# Check output distributions
act_probs = torch.softmax(output['act_logits'][0, 0, :], dim=0)
print(f"\n=== SLOT 1 ACTIVITY PROBABILITIES (before training) ===")
for i, p in enumerate(act_probs):
    print(f"  Category {i+1:2d}: {p:.4f}")
# Before training: expect roughly uniform (~0.07 each)
```

#### 3c. Loss computation

```python
loss_dict = compute_loss(output, batch)
print(f"\n=== LOSS (1 batch, untrained model) ===")
print(f"  L_activity:    {loss_dict['act_loss']:.4f}")
print(f"  L_at_home:     {loss_dict['home_loss']:.4f}")
print(f"  L_copresence:  {loss_dict['cop_loss']:.4f}")
print(f"  L_total:       {loss_dict['total_loss']:.4f}")

# Sanity: untrained CE loss for 14 classes ≈ -ln(1/14) ≈ 2.64
# If much higher or NaN, something is wrong
```

---

## Test 4 — Mini Training Loop (04D)

### Configuration for local testing

```python
# Override config for local sample run:
config_test = {
    "data_dir": "outputs_step4_test",      # sample tensor datasets
    "batch_size": 16,                       # small batch
    "max_epochs": 5,                        # just 5 epochs
    "patience": 3,
    "lr": 1e-4,
    "d_model": 64,                          # smaller model for speed
    "n_heads": 4,
    "n_enc_layers": 2,                      # fewer layers
    "n_dec_layers": 2,
    "d_ff": 256,
    "fp16": False,                          # no AMP on CPU
}
```

### What to inspect

#### 4a. Training progress (print every epoch)

```
Epoch 1/5: train_loss=3.12, val_JS=0.38, lr=0.000100
Epoch 2/5: train_loss=2.85, val_JS=0.32, lr=0.000098
Epoch 3/5: train_loss=2.61, val_JS=0.27, lr=0.000094
Epoch 4/5: train_loss=2.44, val_JS=0.24, lr=0.000088
Epoch 5/5: train_loss=2.31, val_JS=0.22, lr=0.000081
```

Expected: loss should decrease. If it doesn't after 5 epochs → something is wrong with data pipeline or loss computation.

#### 4b. Per-epoch component losses

```python
# After each epoch, print:
print(f"  act_loss={act:.4f}  home_loss={home:.4f}  cop_loss={cop:.4f}")
print(f"  colleagues_loss (2005/2010 rows): {cop_colleagues_loss:.6f}")  # should be ~0
```

#### 4c. Gradient health check

```python
# After first backward pass:
for name, param in model.named_parameters():
    if param.grad is not None:
        grad_norm = param.grad.norm().item()
        if grad_norm == 0:
            print(f"  WARN: zero gradient for {name}")
        if torch.isnan(param.grad).any():
            print(f"  FAIL: NaN gradient for {name}")
```

---

## Test 5 — Inference on Sample (04E)

### What to inspect

#### 5a. Generated diary for one respondent

```python
# Pick a respondent observed on Weekday (DDAY_STRATA=1)
# Generate for Saturday (target=2) and Sunday (target=3)

print("=== RESPONDENT ===")
print(f"  occID: {resp['occID']}, CYCLE_YEAR: {resp['CYCLE_YEAR']}")
print(f"  Observed DDAY_STRATA: 1 (Weekday)")
print(f"  AGEGRP={resp['AGEGRP']}, SEX={resp['SEX']}, LFTAG={resp['LFTAG']}")

print("\n=== OBSERVED DIARY (Weekday) ===")
print(f"  Activities: {observed_activities}")       # 48 integers
print(f"  AT_HOME:    {observed_home}")             # 48 binary values
print(f"  Work slots: {[s for s,a in enumerate(observed_activities) if a==1]}")

print("\n=== GENERATED: Saturday (DDAY_STRATA=2) ===")
print(f"  Activities: {gen_sat_activities}")
print(f"  AT_HOME:    {gen_sat_home}")
print(f"  Work slots: {[s for s,a in enumerate(gen_sat_activities) if a==1]}")

print("\n=== GENERATED: Sunday (DDAY_STRATA=3) ===")
print(f"  Activities: {gen_sun_activities}")
print(f"  AT_HOME:    {gen_sun_home}")
print(f"  Work slots: {[s for s,a in enumerate(gen_sun_activities) if a==1]}")
```

**What to look for (even with undertrained model):**
- Saturday/Sunday should have fewer work slots than Weekday
- Night slots (37–48, 1–8) should still be mostly Sleep
- Activities should be valid integers 1–14 (no out-of-range)
- AT_HOME should be binary 0/1

#### 5b. Co-presence output

```python
print("\n=== CO-PRESENCE: Saturday (respondent 0, first 10 slots) ===")
cop_cols = ["Alone", "Spouse", "Children", "parents", "otherInFAMs",
            "otherHHs", "friends", "others", "colleagues"]
for s in range(10):
    vals = [gen_cop_sat[col][s] for col in cop_cols]
    print(f"  Slot {s+1:2d}: {dict(zip(cop_cols, vals))}")

# Check: colleagues should be 0 for 2005/2010 respondents
if resp["CYCLE_YEAR"] in [2005, 2010]:
    assert all(gen_cop_sat["colleagues"][s] == 0 for s in range(48))
    print("  ✓ colleagues = 0 for 2005/2010 (masking OK)")
```

#### 5c. Co-presence availability mask verification

```python
# For a 2005 respondent: primary 8 co-presence should have ~20% NaN in source
# but synthetic output should have values for ALL slots (model generates regardless)
if resp["CYCLE_YEAR"] == 2005:
    obs_row = cop_sample[cop_sample["occID"] == resp["occID"]]
    alone_nan = obs_row[[f"Alone30_{s:03d}" for s in range(1,49)]].isna().mean(axis=1).values[0]
    print(f"  Source Alone NaN rate (2005): {alone_nan:.1%}")  # expect ~20%
    # Synthetic output should have 0% NaN (model generates for all slots)
    syn_alone_nan = gen_sat_cop["Alone"].isna().mean()
    print(f"  Synthetic Alone NaN rate: {syn_alone_nan:.1%}")  # expect 0%
```

#### 5d. IS_SYNTHETIC flag

```python
print("\n=== OUTPUT ROWS FOR THIS RESPONDENT ===")
for strata in [1, 2, 3]:
    row = output_df[(output_df["occID"] == resp["occID"]) &
                     (output_df["DDAY_STRATA"] == strata)]
    is_syn = row["IS_SYNTHETIC"].values[0]
    print(f"  DDAY_STRATA={strata}: IS_SYNTHETIC={is_syn}")
    # Strata 1 (observed): IS_SYNTHETIC=0
    # Strata 2, 3 (generated): IS_SYNTHETIC=1
```

#### 5e. Augmented output shape

```python
print(f"\n=== AUGMENTED OUTPUT ===")
print(f"  Shape: {output_df.shape}")            # expect (1500, ~552) for 500×3
print(f"  IS_SYNTHETIC=0: {(output_df['IS_SYNTHETIC']==0).sum()}")  # 500
print(f"  IS_SYNTHETIC=1: {(output_df['IS_SYNTHETIC']==1).sum()}")  # 1000
print(f"  Unique occIDs: {output_df['occID'].nunique()}")           # 500
print(f"  Rows per occID: {output_df.groupby('occID').size().unique()}")  # all 3
```

---

## Test 6 — Quick Validation Sanity (04F)

Not a full validation (model is undertrained), but verify the validation script runs.

```python
# Run 04F_validation.py on the sample output
# Expected: most checks will WARN or FAIL (undertrained model)
# Key thing: the script runs without errors and produces the HTML report

# Quick manual checks:
print("=== QUICK VALIDATION ===")

# JS divergence (will be high for undertrained model)
for strata in [1, 2, 3]:
    obs = observed_df[observed_df["DDAY_STRATA"] == strata]
    syn = output_df[(output_df["DDAY_STRATA"] == strata) & (output_df["IS_SYNTHETIC"] == 1)]
    # ... compute JS ...
    print(f"  Strata {strata} JS: {js:.4f}")  # expect > 0.05 (undertrained)

# AT_HOME rate
for cycle in [2005, 2010, 2015, 2022]:
    obs_rate = ...
    syn_rate = ...
    print(f"  {cycle} AT_HOME: obs={obs_rate:.1f}%, syn={syn_rate:.1f}%, Δ={syn_rate-obs_rate:+.1f}pp")
```

---

## Directory Structure for Local Testing

```
2J_docs_occ_nTemp/
├── outputs_step3/
│   ├── hetus_30min.csv               # full (64,061 rows)
│   ├── copresence_30min.csv          # full (64,061 rows)
│   ├── hetus_30min_SAMPLE.csv        # sample (500 rows) ← created by sample_for_testing.py
│   └── copresence_30min_SAMPLE.csv   # sample (500 rows) ← created by sample_for_testing.py
├── outputs_step4_test/                # all sample outputs go here (not outputs_step4/)
│   ├── step4_train.pt
│   ├── step4_val.pt
│   ├── step4_test.pt
│   ├── step4_feature_config.json
│   ├── checkpoints/
│   │   └── best_model.pt
│   ├── augmented_diaries_SAMPLE.csv
│   └── step4_validation_report.html
├── 04A_dataset_assembly.py
├── 04B_model.py
├── 04C_training_pairs.py
├── 04D_train.py
├── 04E_inference.py
├── 04F_validation.py
└── sample_for_testing.py
```

---

## Local Testing Configuration Summary

| Parameter | Full (HPC) | Local Test |
|---|---|---|
| Respondents | 64,061 | 500 |
| Batch size | 256 | 16 |
| d_model | 256 | 64 |
| n_heads | 8 | 4 |
| Encoder layers | 6 | 2 |
| Decoder layers | 6 | 2 |
| d_ff | 1024 | 256 |
| Max epochs | 100 | 5 |
| Patience | 10 | 3 |
| FP16 | Yes | No |
| Device | GPU (V100/A100) | CPU (or MPS on Apple Silicon) |
| Expected train time | 1.5–3 hrs | 2–5 min |
| Output rows | ~192,183 | ~1,500 |

---

## Checklist

- [ ] Run `sample_for_testing.py` → `hetus_30min_SAMPLE.csv` + `copresence_30min_SAMPLE.csv`
- [ ] Test 1: 04A dataset assembly — inspect merged shape, conditioning vector, slot tokens, NaN/availability mask, splits
- [ ] Test 2: 04C training pairs — inspect pair structure, match quality, imbalance
- [ ] Test 3: 04B+04D forward pass — inspect tensor shapes, output distributions, loss values
- [ ] Test 4: 04D mini training — confirm loss decreases over 5 epochs, no NaN
- [ ] Test 5: 04E inference — inspect generated diaries, co-presence, IS_SYNTHETIC flag
- [ ] Test 6: 04F validation — confirm script runs and produces HTML report
- [ ] All scripts accept `--sample` flag or config override to use sample data paths
