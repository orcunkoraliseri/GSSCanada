import json, sys
sys.path.insert(0,"/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs")
sys.path.insert(0,"/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp")
from eSim_bem_utils_2J.integration import load_schedules
sched = load_schedules("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/BEM_Schedules_2022_activity.csv")
for hh in ["106602", "73127", "125954"]:
    if hh in sched:
        d = sched[hh]
        meta = d.get("metadata", {})
        wd = d.get("Weekday", [])
        equip_frac = wd[0].get("equip_frac", "MISSING") if wd else "NO_WD"
        light_frac = wd[0].get("light_frac", "MISSING") if wd else "NO_WD"
        equip_dw = meta.get("equip_design_w", "MISSING")
        light_dw = meta.get("light_design_w", "MISSING")
        dtype = meta.get("dtype", "?")
        print(f"HH {hh} [{dtype}]: equip_design_w={equip_dw}  light_design_w={light_dw}  equip_frac_hr0={equip_frac}  light_frac_hr0={light_frac}")
    else:
        print(f"HH {hh}: NOT FOUND")
