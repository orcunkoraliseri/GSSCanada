"""Ad-hoc D5.2 context check: per-cycle weekday paid-work% (obs vs syn) on the
final population, to confirm the 2005 Section-7 bar moved toward the other
cycles (not just check its absolute level against a remembered ~22%)."""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.dirname(ROOT)
CAL = os.path.join(BASE, "0_Occupancy", "Outputs_21CEN22GSS", "aug_pipeline",
                   "21CEN22GSS_aug_Full_Schedules_excl.csv")
OBS = os.path.join(ROOT, "outputs_step3", "hetus_30min.csv")

ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
NEED = set(ACT_COLS + ["DDAY_STRATA", "CYCLE_YEAR", "IS_SYNTHETIC"])

obs = pd.read_csv(OBS, usecols=lambda c: c in NEED, low_memory=False)
aug = pd.read_csv(CAL, usecols=lambda c: c in NEED, low_memory=False)
syn = aug[aug["IS_SYNTHETIC"] == 1]

for cy in sorted(obs["CYCLE_YEAR"].unique()):
    o = obs[(obs["CYCLE_YEAR"] == cy) & (obs["DDAY_STRATA"] == 1)]
    s = syn[(syn["CYCLE_YEAR"] == cy) & (syn["DDAY_STRATA"] == 1)]
    o_pw = (o[ACT_COLS].values == 1).mean() * 100 if len(o) else float("nan")
    s_pw = (s[ACT_COLS].values == 1).mean() * 100 if len(s) else float("nan")
    print(f"{cy}: obs {o_pw:.2f}% (n={len(o):,}) | syn {s_pw:.2f}% (n={len(s):,})", flush=True)
