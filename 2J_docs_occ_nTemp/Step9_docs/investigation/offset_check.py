"""offset_check.py — manager verification of the 4-hour diary->clock injection offset.
Compares weekday population-mean Occupancy_Schedule by Hour across:
  - BEM_Schedules_2022.csv                       (current, 07_aug_to_bem.py / Step 9 build)
  - BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv (classic 21CEN22GSS_occToBEM.py, datetime-resampled)
  - BEM_Schedules_2022_PRE_STEP8_BAK.csv          (what Step 8 likely ran on)
If 07_aug_to_bem.py dropped the slot->clock rotation, current vs classic differ by a 4h circular shift.
Read-only. py launcher, pandas.
"""
import numpy as np, pandas as pd
from pathlib import Path

BEMS = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup")
FILES = {
    "CURRENT(07_aug/Step9)": "BEM_Schedules_2022.csv",
    "CLASSIC_BAK(real-clock)": "BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv",
    "PRE_STEP8_BAK": "BEM_Schedules_2022_PRE_STEP8_BAK.csv",
}

def wd_occ_curve(path):
    df = pd.read_csv(path, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
    wd = df[df["Day_Type"] == "Weekday"]
    c = wd.groupby("Hour")["Occupancy_Schedule"].mean().reindex(range(24)).values
    return c

curves = {}
for label, fn in FILES.items():
    p = BEMS / fn
    if p.exists():
        curves[label] = wd_occ_curve(p)
    else:
        print(f"MISSING: {fn}")

print("\nWeekday population-mean Occupancy_Schedule by Hour")
print("Hour | " + " | ".join(f"{l:>22s}" for l in curves))
for h in range(24):
    print(f"{h:4d} | " + " | ".join(f"{curves[l][h]:22.3f}" for l in curves))

# Best circular shift to align CURRENT onto CLASSIC
if "CURRENT(07_aug/Step9)" in curves and "CLASSIC_BAK(real-clock)" in curves:
    cur = curves["CURRENT(07_aug/Step9)"]; cls = curves["CLASSIC_BAK(real-clock)"]
    sse = [(s, float(np.mean((np.roll(cur, s) - cls) ** 2))) for s in range(24)]
    best = min(sse, key=lambda x: x[1])
    print(f"\nBest circular shift to align CURRENT onto CLASSIC: roll CURRENT by +{best[0]} h (SSE={best[1]:.5f})")
    print("  (shift of 4 or 20 == a 4-hour rotation; shift 0 would mean NO offset)")
    print(f"  SSE at shift 0 = {dict(sse)[0]:.5f}  vs  SSE at best = {best[1]:.5f}")
