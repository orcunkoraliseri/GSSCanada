"""_activate_2030_canonical.py — OP2: activate the calibrated (structural-break) 2030
diary file into the canonical path downstream reads. Casts hom30 float->int for schema
parity. Run from any directory. Never touches the side file or any backup."""
import os
from pathlib import Path
import numpy as np
import pandas as pd

HERE  = Path(__file__).resolve().parent          # 2J_docs_occ_nTemp/
BASE  = HERE.parent                              # GSSCanada-main/
RAKED = HERE / "2030_synthetic_diaries_raked.csv"
CANON = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030" / "2030_synthetic_diaries.csv"
HOM   = [f"hom30_{s:03d}" for s in range(1, 49)]
LBL   = {1: "WD", 2: "Sat", 3: "Sun"}
EXP   = {1: 78.44, 2: 79.15, 3: 81.48}           # structural-break p=1 daily AT_HOME %

df = pd.read_csv(RAKED, low_memory=False)
assert len(df) == 37008, f"row count {len(df)} != 37008"
assert set(df["DDAY_STRATA"].unique()) == {1, 2, 3}, "DDAY_STRATA not {1,2,3}"
assert set(df["CYCLE_YEAR"].unique()) == {2030}, "CYCLE_YEAR not {2030}"

# Confirm this is the STRUCTURAL-BREAK deliverable, not the older linear (79.47) one.
for s in (1, 2, 3):
    daily = df.loc[df["DDAY_STRATA"] == s, HOM].values.astype(float).mean() * 100
    print(f"  {LBL[s]} daily AT_HOME = {daily:.2f}%  (expect ~{EXP[s]})", flush=True)
    assert abs(daily - EXP[s]) < 0.20, f"{LBL[s]} {daily:.2f} != ~{EXP[s]} -- NOT the structural file; STOP"

# Cast hom30 float -> int (lossless: all values in {0,1}).
hv = df[HOM].values.astype(float)
assert set(np.unique(hv[~np.isnan(hv)])).issubset({0.0, 1.0}), "hom30 not hard 0/1"
df[HOM] = hv.astype(int)

# Column parity vs the (still-unraked) canonical header.
canon_cols = pd.read_csv(CANON, nrows=0).columns.tolist()
assert list(df.columns) == canon_cols, f"column mismatch vs canonical: {set(df.columns) ^ set(canon_cols)}"

# Atomic overwrite of canonical.
tmp = str(CANON) + ".tmp"
df.to_csv(tmp, index=False)
n = sum(1 for _ in open(tmp, encoding="utf-8")) - 1
assert n == 37008, f"written {n} != 37008"
os.replace(tmp, str(CANON))
print(f"ACTIVATED: {n:,} rows -> {CANON}", flush=True)
