"""P10 step 8: prove the frame of the injected Y2022 residential and office products.
Re-run cmd_year_2022's own calls in memory on the FULL AUG (all four cycles, no filter) and
compare with the injected files byte-for-value. Negative control: the same calls on the
2022-only rows must NOT reproduce the injected files. Read-only.
"""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("s7", J3 / "Leg3_4-split/Step7_docs/3rdJ_07_aug_to_bem_4split.py")
s7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s7)
stock = pd.read_csv(s7.AUG, low_memory=False)
lookup = pd.read_csv(s7.LOOKUP_OFFICE)
res_f = pd.read_csv(s7.OUT_DIR / "BEM_Schedules_4split_2022.csv", usecols=["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"])
off_f = pd.read_csv(s7.OUT_DIR / "office_presence_multiplier_2022.csv")

for lbl, frame in (("FULL AUG (all cycles)", stock), ("NEG CTRL: CYCLE_YEAR==2022 rows only", stock[stock.CYCLE_YEAR == 2022])):
    bem = s7.convert(s7.complete_day_types(frame))
    m = res_f.merge(bem[["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"]], on=["SIM_HH_ID", "Day_Type", "Hour"], how="left", suffixes=("_f", "_c"))
    joined = m.Occupancy_Schedule_c.notna().sum()
    mx = np.nanmax(np.abs(m.Occupancy_Schedule_f - m.Occupancy_Schedule_c)) if joined else float("nan")
    off = s7.build_office_multiplier(frame, "observed", lookup)
    mo = off_f.merge(off, on=["office_archetype", "BAND", "Day_Type", "Hour"], suffixes=("_f", "_c"))
    print(f"{lbl}: residential rows joined {joined}/{len(res_f)}, max|diff|={mx:.4f}; "
          f"office max|AT_WORK diff|={np.abs(mo.AT_WORK_fraction_f - mo.AT_WORK_fraction_c).max():.4f}", flush=True)
