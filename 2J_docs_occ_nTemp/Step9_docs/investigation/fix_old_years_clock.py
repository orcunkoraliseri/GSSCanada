"""fix_old_years_clock.py — put the older Step-8 census years on the real clock.
2005/2010/2015 BEM_Schedules are 4 h-early (verified: best circular-shift +4 vs corrected-2022).
They do NOT come from 07_aug_to_bem.py, so the code fix there didn't reach them. Correct them at
the artifact level: relabel each row's Hour to its true clock hour (Hour -> (Hour+4) % 24), which is
exactly the +4 roll the 07_aug edit applies at generation. The occupancy/metabolic DATA is unchanged
— only the hour LABEL is corrected. Originals backed up first. py launcher, pandas.
"""
import pandas as pd, shutil
from pathlib import Path

BEMS = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup")
for y in ["2005", "2010", "2015"]:
    f = BEMS / f"BEM_Schedules_{y}.csv"
    bak = BEMS / f"BEM_Schedules_{y}_BUG4H_BAK_2026-06-08.csv"
    if not bak.exists():
        shutil.copy2(f, bak)
    df = pd.read_csv(f)
    df["Hour"] = (df["Hour"].astype(int) + 4) % 24
    idcol = "SIM_HH_ID" if "SIM_HH_ID" in df.columns else ("HH_ID" if "HH_ID" in df.columns else None)
    if idcol:
        df = df.sort_values([idcol, "Day_Type", "Hour"]).reset_index(drop=True)
    df.to_csv(f, index=False)
    print(f"{y}: Hour relabeled +4h, backup -> {bak.name}, rows={len(df):,}")
print("done.")
