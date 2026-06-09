"""year_clock_check.py — robust test: which Step-8 census years share the corrected real clock?
For each year, align its weekday occupancy-by-hour curve against the CORRECTED 2022 curve by
circular shift (same method as offset_check). best-shift ~0 => same clock (real-clock, clean);
best-shift ~4/20 => 4h-early (buggy). Behavioural year differences add noise but a true 4h
structural offset dominates the SSE landscape. Read-only. py launcher, pandas.
"""
import numpy as np, pandas as pd
from pathlib import Path

BEMS = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup")

def wd_curve(path):
    df = pd.read_csv(path, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
    wd = df[df["Day_Type"] == "Weekday"]
    return wd.groupby("Hour")["Occupancy_Schedule"].mean().reindex(range(24)).values

ref = wd_curve(BEMS / "BEM_Schedules_2022.csv")  # corrected 2022 = real-clock reference

def best_shift(c, ref):
    sse = [(s, float(np.mean((np.roll(c, s) - ref) ** 2))) for s in range(24)]
    b = min(sse, key=lambda x: x[1])
    return b[0], b[1], dict(sse)[0]

print("Full weekday occupancy curves (each year), then alignment vs CORRECTED-2022:\n")
files = {"2005": "BEM_Schedules_2005.csv", "2010": "BEM_Schedules_2010.csv",
         "2015": "BEM_Schedules_2015.csv", "2030": "BEM_Schedules_2030.csv",
         "2022CLASSIC": "BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv"}
curves = {y: wd_curve(BEMS / fn) for y, fn in files.items() if (BEMS / fn).exists()}

print("Hour | " + " | ".join(f"{y:>11s}" for y in curves) + " |  ref2022")
for h in range(24):
    print(f"{h:4d} | " + " | ".join(f"{curves[y][h]:11.3f}" for y in curves) + f" | {ref[h]:8.3f}")

print("\nAlignment vs corrected-2022 (shift to roll year ONTO 2022):")
for y, c in curves.items():
    s, sse_b, sse0 = best_shift(c, ref)
    tag = "SAME CLOCK (clean)" if s in (0, 1, 23) else (f"OFFSET {s}h  <-- CHECK")
    print(f"  {y:>11s}: best_shift=+{s:2d}h  SSE@best={sse_b:.4f}  SSE@0={sse0:.4f}   {tag}")
