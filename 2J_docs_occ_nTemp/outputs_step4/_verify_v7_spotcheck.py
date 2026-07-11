"""_verify_v7_spotcheck.py -- Task D, step D5.1: independent re-derivation of
three v7 figures, deliberately NOT reusing 04F_validation.py / _gen_v7_plots.py
(separate usecols set, separate code path -- catches a bug in the chart
generator itself rather than just reproducing it). Reads
21CEN22GSS_aug_Full_Schedules_excl.csv directly. Run:  py _verify_v7_spotcheck.py
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.dirname(ROOT)
CAL = os.path.join(BASE, "0_Occupancy", "Outputs_21CEN22GSS", "aug_pipeline",
                   "21CEN22GSS_aug_Full_Schedules_excl.csv")
OBS = os.path.join(ROOT, "outputs_step3", "hetus_30min.csv")

ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
NEED = set(ACT_COLS + ["DDAY_STRATA", "CYCLE_YEAR", "IS_SYNTHETIC", "LFTAG"])

print("loading obs...", flush=True)
obs = pd.read_csv(OBS, usecols=lambda c: c in NEED, low_memory=False)
print("loading final population (independent read)...", flush=True)
aug = pd.read_csv(CAL, usecols=lambda c: c in NEED, low_memory=False)
syn = aug[aug["IS_SYNTHETIC"] == 1]

# (a) weekday % of slots in Paid work (raw act30 category 1), obs vs syn
obs_wd = obs[obs["DDAY_STRATA"] == 1]
syn_wd = syn[syn["DDAY_STRATA"] == 1]
obs_pw = (obs_wd[ACT_COLS].values == 1).mean() * 100
syn_pw = (syn_wd[ACT_COLS].values == 1).mean() * 100
print(f"(a) Weekday paid-work%: obs {obs_pw:.2f}% | syn {syn_pw:.2f}%", flush=True)

# (b) one LFTAG level (LFTAG=1, employed) paid-work%, obs vs syn
obs_l1 = obs[obs["LFTAG"] == 1]
syn_l1 = syn[syn["LFTAG"] == 1]
obs_l1_pw = (obs_l1[ACT_COLS].values == 1).mean() * 100
syn_l1_pw = (syn_l1[ACT_COLS].values == 1).mean() * 100
print(f"(b) LFTAG=1 (Employed) paid-work%: obs {obs_l1_pw:.2f}% | syn {syn_l1_pw:.2f}%", flush=True)

# (c) 2005 weekday synthetic paid-work%
syn_2005_wd = syn[(syn["CYCLE_YEAR"] == 2005) & (syn["DDAY_STRATA"] == 1)]
pw_2005 = (syn_2005_wd[ACT_COLS].values == 1).mean() * 100 if len(syn_2005_wd) else float("nan")
print(f"(c) 2005 weekday synthetic paid-work%: {pw_2005:.2f}% (n={len(syn_2005_wd):,}; old report showed ~22%)", flush=True)
