"""List the rows where the rebuilt 2025 original-formula file and the April file
disagree on DTYPE (job 1339873, R3 DTYPE mismatches = 24). Read-only diagnosis."""
import sys
import pandas as pd

cand, ref = sys.argv[1], sys.argv[2]
keys = ["SIM_HH_ID", "Day_Type", "Hour"]
cols = keys + ["HHSIZE", "DTYPE"]
a = pd.read_csv(cand, usecols=cols)
b = pd.read_csv(ref, usecols=cols)
m = a.merge(b, on=keys, suffixes=("_new", "_april"))
print(f"DIAG joined rows = {len(m):,}")
d = m[m["DTYPE_new"].astype(str) != m["DTYPE_april"].astype(str)]
print(f"DIAG DTYPE mismatch rows = {len(d):,}")
g = d.groupby(["SIM_HH_ID", "Day_Type", "HHSIZE_new", "DTYPE_new", "DTYPE_april"]).size()
print("DIAG mismatches by household/day type (last column = rows):")
print(g.to_string())
for hh in d["SIM_HH_ID"].unique():
    s = m[m["SIM_HH_ID"] == hh].groupby("Day_Type")[["DTYPE_new", "DTYPE_april"]].agg(lambda x: sorted(set(map(str, x))))
    print(f"DIAG household {hh} DTYPE per day type:\n{s.to_string()}")
print("DIAG DTYPE counts new:", a.drop_duplicates(["SIM_HH_ID", "Day_Type"])["DTYPE"].value_counts().to_dict())
print("DIAG DTYPE counts april:", b.drop_duplicates(["SIM_HH_ID", "Day_Type"])["DTYPE"].value_counts().to_dict())
print("DIAG DONE")
