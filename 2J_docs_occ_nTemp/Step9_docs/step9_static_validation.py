"""
Step 9 static validation — no E+ required.
Tests: RF1 de-bounce, RF2 fridge subtraction, sleep/away zero lighting,
       calibration scalar arithmetic, presence/metabolic column stability.
Run: py Step9_docs/step9_static_validation.py   (from 2J_docs_occ_nTemp/)
"""
import sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import numpy as np
import activity_loads as al

PASS = "PASS"
FAIL = "FAIL"

results = []

# ---- 1. RF1 DE-BOUNCE: eating across 6 consecutive slots fires dishwasher ONCE --------
print("=== RF1: Dishwasher de-bounce ===")
eating_row = {'HH_ID': 1, 'DDAY_STRATA': 1}
for i in range(1, 49):
    eating_row[f'act30_{i:03d}'] = 6   # eating all day
    eating_row[f'hom30_{i:03d}'] = 1   # always home
member_rows = [eating_row]
raw_both = al.compute_48slot_loads({'Weekday': member_rows, 'Weekend': member_rows})
raw = raw_both['Weekday']
eq_W = raw['equipment_W']
dw_W = al.APPLIANCE_W['dishwasher']

# Detect dishwasher-active slots: eq_W must exceed cooking-only level by ~half a dishwasher load.
# All-eating (act=6): cooking = 0.85 * APPLIANCE_W['cooking'] * eff(1) = 0.85*930 = 790.5 W
# With dishwasher: += 930 W (total ~1850 W); without: ~921 W.  Threshold between them.
cooking_only_W = al.BASELOAD_W + 0.85 * al.APPLIANCE_W['cooking'] * al.eff(1)
dw_threshold   = cooking_only_W + dw_W * 0.9
dw_slots_active = np.where(eq_W > dw_threshold)[0]
# Cycle length = 3 (run) + 6 (cool) = 9 slots; 48 slots yields 6 triggers (t=0,9,18,27,36,45)
# 6 * 3 = 18 active dishwasher slots.
expected_dw_slots = 18
actual_dw_slots = len(dw_slots_active)
ok_rf1 = (actual_dw_slots == expected_dw_slots)
print(f"  cooking_only_W = {cooking_only_W:.1f}, threshold = {dw_threshold:.1f}")
print(f"  Dishwasher active slots (all-eating day): {actual_dw_slots} (expected {expected_dw_slots})")
print(f"  {PASS if ok_rf1 else FAIL}")
results.append(('RF1 de-bounce', ok_rf1))

# ---- 2. RF2: Fridge/baseload double-zero arithmetic check -------------------------
print("\n=== RF2: Fridge subtraction arithmetic ===")
expected_net = al.SHEU_EQUIP_KWH - al.FRIDGE_KWH_IDF
ok_rf2 = abs(al.SHEU_EQUIP_KWH_NET - expected_net) < 0.01
print(f"  SHEU_EQUIP_KWH       = {al.SHEU_EQUIP_KWH}")
print(f"  FRIDGE_KWH_IDF       = {al.FRIDGE_KWH_IDF}")
print(f"  SHEU_EQUIP_KWH_NET   = {al.SHEU_EQUIP_KWH_NET} (expected {expected_net})")
print(f"  {PASS if ok_rf2 else FAIL}")
results.append(('RF2 arithmetic', ok_rf2))

# ---- 3. Calibration scalar: for all-eating household, equip_scale = NET/raw -------
print("\n=== Calibration scalar math ===")
cal = al.calibrate_schedules(raw_both)
expected_scale = al.SHEU_EQUIP_KWH_NET / cal['equip_kwh_raw']
ok_scale = abs(cal['equip_scale'] - expected_scale) < 0.001
print(f"  equip_kwh_raw  = {cal['equip_kwh_raw']:.1f}")
print(f"  equip_scale    = {cal['equip_scale']:.4f} (expected {expected_scale:.4f})")
print(f"  equip_design_W = {cal['equip_design_W']:.2f}")
print(f"  {PASS if ok_scale else FAIL}")
results.append(('Calibration scalar', ok_scale))

# ---- 4. Sleep/Away → zero LIGHTING fraction, non-zero equipment (baseload) --------
print("\n=== Sleep/Away: zero Lighting check ===")
sleep_row = {'HH_ID': 2, 'DDAY_STRATA': 1}
for i in range(1, 49):
    sleep_row[f'act30_{i:03d}'] = 5   # sleep
    sleep_row[f'hom30_{i:03d}'] = 1   # home (asleep)
raw_sleep = al.compute_48slot_loads({'Weekday': [sleep_row], 'Weekend': [sleep_row]})['Weekday']
ok_light_zero = np.all(raw_sleep['lighting_frac'] == 0.0)
ok_equip_baseload = np.allclose(raw_sleep['equipment_W'], al.BASELOAD_W)
print(f"  Sleep: all lighting_frac == 0: {ok_light_zero}")
print(f"  Sleep: all equipment_W == {al.BASELOAD_W}W (baseload only): {ok_equip_baseload}")

away_row = {'HH_ID': 3, 'DDAY_STRATA': 1}
for i in range(1, 49):
    away_row[f'act30_{i:03d}'] = 4
    away_row[f'hom30_{i:03d}'] = 0   # away
raw_away = al.compute_48slot_loads({'Weekday': [away_row], 'Weekend': [away_row]})['Weekday']
ok_light_away = np.all(raw_away['lighting_frac'] == 0.0)
ok_equip_away = np.allclose(raw_away['equipment_W'], al.BASELOAD_W)
print(f"  Away:  all lighting_frac == 0: {ok_light_away}")
print(f"  Away:  all equipment_W == {al.BASELOAD_W}W (baseload only): {ok_equip_away}")
ok_sleep_away = ok_light_zero and ok_equip_baseload and ok_light_away and ok_equip_away
print(f"  {PASS if ok_sleep_away else FAIL}")
results.append(('Sleep/Away zero lighting', ok_sleep_away))

# ---- 5. Schema check: verify calibrate_schedules returns required keys  -----------
print("\n=== Output schema check ===")
required_keys = {'equip_frac_wd','equip_frac_we','equip_design_W','equip_kwh_raw',
                 'equip_scale','light_frac_wd','light_frac_we','light_design_W','light_kwh_raw_at1W'}
ok_schema = required_keys <= set(cal.keys())
ok_shapes = (len(cal['equip_frac_wd'])==24 and len(cal['light_frac_wd'])==24)
ok_range = (cal['equip_frac_wd'].max() <= 1.0 and cal['equip_frac_wd'].min() >= 0.0)
print(f"  Required keys present: {ok_schema}")
print(f"  Output arrays are 24h: {ok_shapes}")
print(f"  Fraction range [0,1]:  {ok_range}")
ok_full_schema = ok_schema and ok_shapes and ok_range
print(f"  {PASS if ok_full_schema else FAIL}")
results.append(('Output schema', ok_full_schema))

# ---- 6. 07_aug_to_bem.py import check (no E+ run, just import) --------------------
print("\n=== 07_aug_to_bem.py import + OUT_COLS check ===")
try:
    import importlib.util, types
    spec = importlib.util.spec_from_file_location("aug_to_bem", HERE / "07_aug_to_bem.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    new_cols = {'Equipment_Fraction','Lighting_Fraction','Equip_Design_W','Light_Design_W'}
    ok_cols = new_cols <= set(mod.OUT_COLS)
    ok_import = True
    print(f"  Import OK, new columns in OUT_COLS: {ok_cols}")
    print(f"  OUT_COLS has {len(mod.OUT_COLS)} columns: {mod.OUT_COLS}")
except Exception as e:
    ok_import, ok_cols = False, False
    print(f"  Import FAILED: {e}")
ok_aug = ok_import and ok_cols
print(f"  {PASS if ok_aug else FAIL}")
results.append(('07_aug_to_bem OUT_COLS', ok_aug))

# ---- Summary -------------------------------------------------------------------
print("\n=== SUMMARY ===")
all_pass = True
for name, ok in results:
    tag = PASS if ok else FAIL
    print(f"  {tag}  {name}")
    if not ok:
        all_pass = False
print(f"\n{'ALL CHECKS PASS' if all_pass else 'SOME CHECKS FAILED'}")
sys.exit(0 if all_pass else 1)
