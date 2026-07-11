"""measure_shape_gaps_v2_samebasis.py — Task B / B6: re-measure the 3-channel shape gap
on the SAME basis as step4_validation_report_v5.html's "Would raking all three heads..."
table (obs=hetus_30min.csv single-person diary-days vs calib=synthetic act30, single-
occupant activity_loads pass, dtype='SingleD' default, peak-normalized equipment shape).

Why v2: measure_shape_gaps.py (v1) compared post-census-link households against the
final BEM_Schedules_2022.csv — a DIFFERENT pipeline stage/population than the v5 report's
number (raw Step-4 model act30 fidelity, pre-rake, pre-BEM, single-person). v1's numbers
are real but not directly comparable to the v5 report's 14.9%/32%/3.8pp/+1.9% figures.
This script reproduces the v5 method exactly, run on three act30 sources:
  - obs            : outputs_step3/hetus_30min.csv (unchanged; ground truth)
  - calib_pre_rake : outputs_step4/augmented_diaries.csv, IS_SYNTHETIC==1 (raw Step-4
                     model output — should reproduce the v5 report's 14.9%/32%/3.8pp/+1.9%
                     as a self-check)
  - calib_post_rake: aug_pipeline/21CEN22GSS_aug_Full_Schedules.csv, IS_SYNTHETIC==1
                     (Task B's act30-conditional-raked synthetic population)
"""
import numpy as np
import pandas as pd
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEP4_ROOT = HERE.parents[1]
sys.path.insert(0, str(STEP4_ROOT))
import activity_loads as al

BASE = STEP4_ROOT.parent
OBS_PATH   = STEP4_ROOT / "outputs_step3" / "hetus_30min.csv"
PRE_PATH   = STEP4_ROOT / "outputs_step4" / "augmented_diaries.csv"
POST_PATH  = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline" / "21CEN22GSS_aug_Full_Schedules.csv"

ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
MET = {0:0,1:125,2:175,3:190,4:195,5:70,6:105,7:170,8:110,9:90,10:85,11:245,12:105,13:140,14:135}


def single_occupant_profile(df):
    """Peak-normalized equipment shape (24h), lighting frac (24h), mean metabolic W,
    averaged over all rows, treating each person's diary as a lone-occupant household
    (matches hetus_30min.csv's lack of household linkage)."""
    act = df[ACT].to_numpy()
    hom = df[HOM].to_numpy()
    n = len(df)
    equip_W = np.full((n, 48), al.BASELOAD_W)
    light_frac = np.zeros((n, 48))
    dw_queue = np.zeros(n, dtype=int)
    dw_cooldown = np.zeros(n, dtype=int)
    for t in range(48):
        a_t = act[:, t]
        h_t = hom[:, t] > 0
        for bucket in al.SHARED_BUCKETS - {"dishwasher"}:
            wt = np.array([al.WEIGHT.get(int(a), {}).get(bucket, 0.0) for a in a_t])
            equip_W[h_t, t] += wt[h_t] * al.APPLIANCE_W[bucket] * al.eff(1)
        trigger = np.array([al.WEIGHT.get(int(a), {}).get("dishwasher", 0.0) > 0 for a in a_t])
        can_trigger = h_t & (dw_queue == 0) & (dw_cooldown == 0) & trigger
        dw_queue[can_trigger] = 3
        for bucket in al.PERSONAL_BUCKETS:
            wt = np.array([al.WEIGHT.get(int(a), {}).get(bucket, 0.0) for a in a_t])
            equip_W[h_t, t] += wt[h_t] * al.APPLIANCE_W[bucket]
        light_on = h_t & np.array([al.WEIGHT.get(int(a), {}).get("lighting", 0.0) > 0 for a in a_t])
        light_frac[light_on, t] = 1.0
        running = dw_queue > 0
        equip_W[running, t] += al.APPLIANCE_W["dishwasher"] * al.eff(1)
        dw_queue[running] -= 1
        just_ended = running & (dw_queue == 0)
        dw_cooldown[just_ended] = 6
        cooling = (~running) & (dw_cooldown > 0)
        dw_cooldown[cooling] -= 1

    eq24 = al.slots_to_hours(equip_W.mean(axis=0))
    lt24 = al.slots_to_hours(light_frac.mean(axis=0))
    peak = max(float(eq24.max()), 1.0)
    eq_shape = eq24 / peak
    met = np.vectorize(lambda a: MET.get(int(a), 100.0))(act)
    met_mean = float(np.where(hom > 0, met, np.nan)[hom > 0].mean())
    return eq_shape, lt24, met_mean


def compare(label, obs_shape, obs_light, obs_met, cal_shape, cal_light, cal_met):
    d_eq = np.abs(cal_shape - obs_shape) * 100
    d_lt = np.abs(cal_light - obs_light) * 100
    print(f"\n-- {label} --")
    print(f"  Equipment (peak-normalized) shape: mean|Delta| {d_eq.mean():.1f}%, "
          f"peak {d_eq.max():.1f}% @ hour {int(d_eq.argmax())}")
    print(f"  Lighting shape: mean|Delta| {d_lt.mean():.1f} pp, "
          f"peak {d_lt.max():.1f} pp @ hour {int(d_lt.argmax())}")
    pct = (cal_met - obs_met) / obs_met * 100
    print(f"  Metabolic: obs={obs_met:.1f} W  calib={cal_met:.1f} W  "
          f"Delta={cal_met-obs_met:+.1f} W ({pct:+.1f}%)")


print("Loading obs (hetus_30min.csv)...", flush=True)
obs = pd.read_csv(OBS_PATH, usecols=ACT + HOM, low_memory=False)
print(f"  obs rows: {len(obs):,}", flush=True)
obs_shape, obs_light, obs_met = single_occupant_profile(obs)

print("Loading calib_pre_rake (augmented_diaries.csv, IS_SYNTHETIC==1)...", flush=True)
pre = pd.read_csv(PRE_PATH, usecols=ACT + HOM + ["IS_SYNTHETIC"], low_memory=False)
pre = pre[pre["IS_SYNTHETIC"] == 1]
print(f"  pre-rake synthetic rows: {len(pre):,}", flush=True)
pre_shape, pre_light, pre_met = single_occupant_profile(pre)
compare("calib_pre_rake vs obs  [self-check: should reproduce v5's 14.9% / 32% / 3.8pp / +1.9%]",
        obs_shape, obs_light, obs_met, pre_shape, pre_light, pre_met)

print("\nLoading calib_post_rake (Full_Schedules.csv, IS_SYNTHETIC==1, Task B raked)...", flush=True)
post = pd.read_csv(POST_PATH, usecols=ACT + HOM + ["IS_SYNTHETIC"], low_memory=False)
post = post[post["IS_SYNTHETIC"] == 1]
print(f"  post-rake synthetic rows: {len(post):,}", flush=True)
post_shape, post_light, post_met = single_occupant_profile(post)
compare("calib_post_rake vs obs  [Task B result]",
        obs_shape, obs_light, obs_met, post_shape, post_light, post_met)
