"""
3rdJ Step 4M -- G4 work-peak home-gated decomposition probe.

Question: the G4 "Work peak-slot delta" (act30==1 over slots 8-19) fails at 10.33 pp,
but downstream load consumers (07_aug_to_bem.py metabolic, activity_loads.py PC+lighting)
only fire on a work slot when the person is ALSO home (hom30==1). Away-worker slots
(act30==1, hom30==0) are filtered out before any load fires.

This probe decomposes the unconditional G4 gap into:
  - JOINT   P(act==1 AND hom==1)  -> the load-driving fraction (what Step7/9 actually see)
  - AWAY    P(act==1 AND hom==0)  -> filtered out downstream (irrelevant to loads)
  - COND    P(act==1 | hom==1)    -> telework activity accuracy given the person is home

Mirrors validator slot logic exactly: act30_001..048 / hom30_001..048, WORK_PEAK_SLOTS
= range(8,20) (0-indexed into the present_cols-ordered array), WORK_CAT = 1,
populations split on IS_SYNTHETIC (obs==0, syn==1).
"""
import sys
import numpy as np
import pandas as pd

N_SLOTS = 48
WORK_PEAK_SLOTS = list(range(8, 20))   # matches validator
WORK_CAT = 1                           # "Work & Related"

ACT = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def measure(d, name):
    a = d[ACT].to_numpy(dtype=float)[:, WORK_PEAK_SLOTS]
    h = d[HOM].to_numpy(dtype=float)[:, WORK_PEAK_SLOTS]
    work = (a == WORK_CAT)
    home = (h == 1)
    uncond = float(work.mean()) * 100
    joint = float((work & home).mean()) * 100
    away = float((work & ~home).mean()) * 100
    cond = float(work[home].mean()) * 100 if home.sum() > 0 else float("nan")
    print(f"[{name}] n={len(d):,}  uncond_work={uncond:6.2f}%  "
          f"joint(work&home)={joint:6.2f}%  away(work&~home)={away:6.2f}%  "
          f"cond(work|home)={cond:6.2f}%")
    return uncond, joint, away, cond


def main():
    path = sys.argv[1]
    df = pd.read_csv(path, low_memory=False)
    syn = df[df["IS_SYNTHETIC"] == 1]
    obs = df[df["IS_SYNTHETIC"] == 0]
    print("=== G4 work-peak home-gated decomposition (slots 8-19, act==1) ===")
    print(f"file: {path}")
    ou = measure(obs, "OBS")
    su = measure(syn, "SYN")
    print()
    print(f"UNCOND delta |obs-syn| = {abs(ou[0]-su[0]):5.2f} pp   (validator G4 work-peak = 10.33)")
    print(f"JOINT  delta (work&home) = {abs(ou[1]-su[1]):5.2f} pp   <- LOAD-DRIVING (Step7/9 fire here)")
    print(f"AWAY   delta (work&~home)= {abs(ou[2]-su[2]):5.2f} pp   <- filtered out downstream")
    print(f"COND   delta (work|home) = {abs(ou[3]-su[3]):5.2f} pp   <- telework activity accuracy")


if __name__ == "__main__":
    main()
