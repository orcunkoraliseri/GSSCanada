"""Build clock-correct, schema-consistent Step 8 schedules in private dir.

2005/2010/2015: copy from BEM_Setup, apply (Hour+4)%24 correction (same fix as
  fix_old_years_clock.py / the 07_aug_to_bem np.roll+4 path for newer years).
2022/2030: copy from BEM_Setup (clock already correct), drop Equip_Design_W and
  Light_Design_W so integration.py uses the standard L&E path, not the S9 path.

Output: /speed-scratch/o_iseri/step8_run/sched/BEM_Schedules_{year}.csv
"""
import pandas as pd
from pathlib import Path

BEM_SETUP = Path("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup")
OUT_DIR   = Path("/speed-scratch/o_iseri/step8_run/sched")
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Output dir: {OUT_DIR}")

# 2005/2010/2015: apply (Hour+4)%24 correction
for yr in ["2005", "2010", "2015"]:
    src = BEM_SETUP / f"BEM_Schedules_{yr}.csv"
    dst = OUT_DIR / f"BEM_Schedules_{yr}.csv"
    print(f"\n{yr}: reading {src} ...", flush=True)
    df = pd.read_csv(src)
    orig_h0 = df[df["Day_Type"] == "Weekday"]["Hour"].iloc[0] if len(df) else "?"
    df["Hour"] = (df["Hour"].astype(int) + 4) % 24
    if "SIM_HH_ID" in df.columns:
        df = df.sort_values(["SIM_HH_ID", "Day_Type", "Hour"]).reset_index(drop=True)
    df.to_csv(dst, index=False)
    # Verify: check that a Weekday row that was hour X is now hour (X+4)%24
    new_min_h = df[df["Day_Type"] == "Weekday"]["Hour"].min()
    print(f"  rows={len(df):,}  cols={len(df.columns)}  sample_orig_h0={orig_h0}  new_min_wkday_h={new_min_h}")
    print(f"  -> {dst}")

# 2022/2030: clock is already correct; drop design-W columns only
DROP_COLS = ["Equip_Design_W", "Light_Design_W"]
for yr in ["2022", "2030"]:
    src = BEM_SETUP / f"BEM_Schedules_{yr}.csv"
    dst = OUT_DIR / f"BEM_Schedules_{yr}.csv"
    print(f"\n{yr}: reading {src} ...", flush=True)
    df = pd.read_csv(src)
    dropped = [c for c in DROP_COLS if c in df.columns]
    kept   = [c for c in DROP_COLS if c not in df.columns]
    df = df.drop(columns=dropped)
    df.to_csv(dst, index=False)
    print(f"  rows={len(df):,}  cols={len(df.columns)}  dropped={dropped}  already_absent={kept}")
    print(f"  remaining cols: {list(df.columns)}")
    print(f"  -> {dst}")

# Quick phase check on output files
print("\n=== Quick phase verification ===")
import csv as _csv
all_ok = True
for yr in ["2005", "2010", "2015", "2022", "2030"]:
    f = OUT_DIR / f"BEM_Schedules_{yr}.csv"
    by_h = {}
    with open(f) as fh:
        for row in _csv.DictReader(fh):
            if row.get("Day_Type") != "Weekday":
                continue
            h = int(row["Hour"])
            by_h.setdefault(h, []).append(float(row["Occupancy_Schedule"]))
    if not by_h:
        print(f"  {yr}: ERROR no Weekday rows"); all_ok = False; continue
    avg = {h: sum(v)/len(v) for h, v in by_h.items()}
    night_avg  = sum(avg.get(h, 0) for h in range(0, 6)) / 6
    midday_avg = sum(avg.get(h, 0) for h in range(11, 15)) / 4
    peak_h = max(avg, key=lambda k: avg[k])
    ok = night_avg > midday_avg
    status = "PASS" if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"  {yr}: night_avg={night_avg:.3f} midday_avg={midday_avg:.3f} peak_h=h{peak_h:02d} -> {status}")

if all_ok:
    print("\nBUILD DONE: all 5 years phase-OK")
else:
    print("\nBUILD WARNING: phase check failed for one or more years — review above")
    import sys; sys.exit(1)
