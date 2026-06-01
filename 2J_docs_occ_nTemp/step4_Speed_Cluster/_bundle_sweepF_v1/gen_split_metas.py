"""Generate per-split meta CSVs from step4_all_meta.csv by sequential slicing.

The all_meta rows are ordered train, val, test (as written by 04A_dataset_assembly.py).
We slice by tensor sizes to produce the per-split CSVs the sample assembler expects.
"""
import os, sys
import pandas as pd
import torch

src = sys.argv[1] if len(sys.argv) > 1 else "/speed-scratch/o_iseri/occModeling/outputs_step4_G2"

meta = pd.read_csv(os.path.join(src, "step4_all_meta.csv"))
train_t = torch.load(os.path.join(src, "step4_train.pt"), map_location="cpu", weights_only=False)
val_t = torch.load(os.path.join(src, "step4_val.pt"), map_location="cpu", weights_only=False)
test_t = torch.load(os.path.join(src, "step4_test.pt"), map_location="cpu", weights_only=False)

n_train = next(iter(train_t.values())).shape[0]
n_val = next(iter(val_t.values())).shape[0]
n_test = next(iter(test_t.values())).shape[0]
n_total = len(meta)

print(f"Total meta: {n_total}, train: {n_train}, val: {n_val}, test: {n_test}")
assert n_train + n_val + n_test == n_total, f"Size mismatch: {n_train}+{n_val}+{n_test} != {n_total}"

meta.iloc[:n_train].to_csv(os.path.join(src, "step4_train_meta.csv"), index=False)
meta.iloc[n_train:n_train+n_val].to_csv(os.path.join(src, "step4_val_meta.csv"), index=False)
meta.iloc[n_train+n_val:].to_csv(os.path.join(src, "step4_test_meta.csv"), index=False)

print(f"Written: step4_train_meta.csv ({n_train}), step4_val_meta.csv ({n_val}), step4_test_meta.csv ({n_test})")
