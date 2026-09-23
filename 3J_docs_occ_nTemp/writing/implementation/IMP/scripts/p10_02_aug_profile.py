"""P10 step 2: profile the Step-5 stock (AUG) and the 2030 pools. Read-only."""
import hashlib
from pathlib import Path
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
AUG = J3 / "Leg3_4-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
S6 = J3 / "Leg3_4-split/Step6_docs/outputs_step6"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

print("AUG md5", md5(AUG))
a = pd.read_csv(AUG, low_memory=False)
print("AUG shape", a.shape)
print("non-slot columns:", [c for c in a.columns if not c[:5] in ("act30", "hom30", "wrk30", "ret30")])
for c in ["CYCLE_YEAR", "IS_SYNTHETIC", "DDAY_STRATA", "LFTAG"]:
    if c in a.columns:
        print(c, a[c].value_counts(dropna=False).sort_index().to_dict())
print(pd.crosstab(a["CYCLE_YEAR"], a["IS_SYNTHETIC"]))
print(pd.crosstab([a["CYCLE_YEAR"], a["DDAY_STRATA"]], a["IS_SYNTHETIC"]))
print("SIM_HH_ID unique", a["SIM_HH_ID"].nunique())

for f in ["2030_synthetic_diaries_4split_calibrated_mindwell_C.csv",
          "2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv"]:
    p = S6 / f
    print("\n==", f, md5(p))
    d = pd.read_csv(p, low_memory=False, nrows=5)
    print("columns (non-slot):", [c for c in d.columns if not c[:5] in ("act30", "hom30", "wrk30", "ret30")])
