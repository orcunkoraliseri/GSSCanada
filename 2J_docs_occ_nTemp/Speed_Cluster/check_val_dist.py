import torch
import numpy as np

val = torch.load('outputs_step4/step4_val.pt', map_location='cpu', weights_only=False)
acts = val['act_seq'].numpy().flatten()
unique, counts = np.unique(acts, return_counts=True)
total = len(acts)

print("Activity distribution (val set):")
for u, c in zip(unique, counts):
    print(f"  class {u:2d}: {100*c/total:.1f}%")

print(f"\nn_val respondents: {len(val['act_seq'])}")

strata = val['obs_strata'].numpy()
su, sc = np.unique(strata, return_counts=True)
print("Stratum counts:", dict(zip(su.tolist(), sc.tolist())))

cycle = val['cycle_year'].numpy()
cu, cc = np.unique(cycle, return_counts=True)
print("Cycle years:", dict(zip(cu.tolist(), cc.tolist())))
