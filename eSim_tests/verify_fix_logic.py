
import numpy as np
import pandas as pd

def simulate_grid_filling(start_hhmm, end_hhmm, label):
    res = 5
    slots = 288 # 1440 / 5
    
    # OLD INCORRECT LOGIC
    # s_idx = int(np.floor(start_hhmm / res)) # Directly dividing HHMM by 5
    s_idx_old = int(np.floor(start_hhmm / res))
    e_idx_old = int(np.floor(end_hhmm / res))
    
    # NEW CORRECT LOGIC
    s_min = (start_hhmm // 100) * 60 + (start_hhmm % 100)
    e_min = (end_hhmm // 100) * 60 + (end_hhmm % 100)
    
    s_idx_new = int(np.floor(s_min / res))
    e_idx_new = int(np.floor(e_min / res))
    
    print(f"\nActivity: {label} ({start_hhmm:04d} - {end_hhmm:04d})")
    print(f"  Real Time: {s_min//60:02d}:{s_min%60:02d} - {e_min//60:02d}:{e_min%60:02d}")
    print(f"  OLD Logic (Start): Slot {s_idx_old} -> {s_idx_old*5//60:02d}:{s_idx_old*5%60:02d}")
    print(f"  NEW Logic (Start): Slot {s_idx_new} -> {s_idx_new*5//60:02d}:{s_idx_new*5%60:02d}")
    
    shift = (s_idx_old - s_idx_new) * 5
    print(f"  SHIFT ERROR: {shift} minutes ({shift/60:.1f} hours)")

# Test Cases
simulate_grid_filling(400, 800, "Morning Sleep")
simulate_grid_filling(1200, 1300, "Lunch")
simulate_grid_filling(1700, 1800, "Commute Home")
simulate_grid_filling(2200, 2355, "Night Sleep")
