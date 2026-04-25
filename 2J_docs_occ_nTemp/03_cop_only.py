"""
03_cop_only.py — Re-generate copresence_30min.csv without re-running full Step 3.

Imports tile_copresence_to_30min() and validate_copresence_30min_export()
from 03_mergingGSS.py and runs only those functions.

Reads:  outputs_step3/merged_episodes.csv
        outputs_step3/hetus_30min.csv  (for occID order)
Writes: outputs_step3/copresence_30min.csv  (64061 rows × 433 cols)
"""

import importlib.util
import pandas as pd

spec = importlib.util.spec_from_file_location("mergingGSS", "03_mergingGSS.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
tile_copresence_to_30min = mod.tile_copresence_to_30min
validate_copresence_30min_export = mod.validate_copresence_30min_export

print("── Re-generating copresence_30min.csv ──────────────────────")
copresence_30min = tile_copresence_to_30min()

print(f"\n  Rows    : {copresence_30min.shape[0]:,}")
print(f"  Columns : {copresence_30min.shape[1]}")
print(f"  Sample cols: {list(copresence_30min.columns[:5])}")

ref_df = pd.read_csv(
    "outputs_step3/hetus_30min.csv", usecols=["occID", "CYCLE_YEAR"], low_memory=False
)
occ_cyc = list(zip(ref_df["occID"], ref_df["CYCLE_YEAR"]))
validate_copresence_30min_export(copresence_30min, occ_cyc)

print("\nDone — copresence_30min.csv written to outputs_step3/")
