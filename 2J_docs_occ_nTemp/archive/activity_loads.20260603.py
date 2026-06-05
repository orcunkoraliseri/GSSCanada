"""activity_loads.py — Step 9: activity-driven equipment + lighting schedule builder.

Translates 30-min GSS activity sequences (act30_001..048) into hourly
EnergyPlus-ready equipment (fractional 0-1) and lighting fraction (0-1) schedules,
calibrated to NRCan SHEU 2019 SingleD targets.

Called from 07_aug_to_bem.py to extend BEM_Schedules_<year>.csv with two new columns:
  Equipment_Fraction  — activity-driven equipment (fraction of equip_design_W)
  Lighting_Fraction   — activity-driven lighting (fraction of light_design_W)

Fixed vs prototype (PROTOTYPE_VERDICT.md 2026-06-02):
  RF1 — dishwasher de-bounce: per-trigger cooldown prevents re-fire on consecutive eating slots
  RF2 — fridge/baseload double-zero: FRIDGE_KWH_IDF subtracted from calibration target so
         the IDF's refrigerator1 object and the STEP9 baseload are not double-counted

Deferred (cluster E+ run):
  RF3 — n>=20 statistical validity: architecture already supports any n
  RF4 — kWh-comparable baseline: zero gas_mels1/IECC_Adj1 on baseline side (E+ run step)

Refs: Richardson/CREST 2010; DR-2 Activity-Based Load Modeling Numbers.md;
      DR-1 Calibration Dataset Canadian Residential Electricity End-Use.md
"""
import numpy as np

# ---------------------------------------------------------------------------
# Activity → end-use weight matrix  (DR-2 Table)
# Keys: GSS activity codes 0–14.  Missing entry → all weights 0.
# AWAY {0,4,12,13} and SLEEP {5}: no active loads (baseload only).
# ---------------------------------------------------------------------------
WEIGHT = {
    0:  {},
    1:  {'cooking': 0.05, 'pc': 0.90,  'lighting': 1.0},
    2:  {'cooking': 0.10, 'dishwasher': 0.20, 'washer': 0.30, 'dryer': 0.20, 'lighting': 1.0},
    3:  {'cooking': 0.10, 'tv': 0.30,  'lighting': 1.0},
    4:  {},
    5:  {},
    6:  {'cooking': 0.85, 'dishwasher': 0.15, 'lighting': 1.0},
    7:  {'lighting': 1.0},
    8:  {'cooking': 0.05, 'pc': 0.85,  'lighting': 1.0},
    9:  {'cooking': 0.15, 'tv': 0.40,  'lighting': 1.0},
    10: {'tv': 0.85,      'pc': 0.15,  'lighting': 1.0},
    11: {'tv': 0.20,      'lighting': 1.0},
    12: {},
    13: {},
    14: {'washer': 0.10,  'tv': 0.10,  'pc': 0.10, 'lighting': 1.0},
}

SHARED_BUCKETS   = {'cooking', 'dishwasher', 'washer', 'dryer', 'tv'}
PERSONAL_BUCKETS = {'pc'}

# Effective co-occupancy for SHARED devices (DR-2 / Richardson 2008)
_EFF = {0: 0.0, 1: 1.0, 2: 1.4, 3: 1.7, 4: 1.9}
def eff(n):
    if n <= 0: return 0.0
    if n >= 5: return 2.0
    return _EFF.get(n, 2.0)

# Appliance active power (W), with short-cycle proration where applicable
# Cooking composite: range 3000 W × 0.45 × 0.50-duty + micro 1500 W × (10/30) × 0.35
#                    + small 1200 W × (10/30) × 0.20  ≈ 930 W per active slot
_COOKING_W = (0.45 * 3000 * 0.50
            + 0.35 * 1500 * (10 / 30)
            + 0.20 * 1200 * (10 / 30))

APPLIANCE_W = {
    'cooking':    _COOKING_W,  # ≈ 930 W
    'dishwasher': 930,          # 930 W; 90-120 min cycle → queue 3 slots
    'washer':     470,
    'dryer':      2100,
    'tv':         100,
    'pc':         150,          # desktop + monitor
}

# Always-on baseload: fridge + freezer + standby (DR-1 Table D)
# ≈ 51W (fridge) + 23W (freezer×0.60 saturation) + 49W (standby) = 123 W ≈ 130 W
BASELOAD_W = 130.0

# NRCan SHEU 2019, SingleD, DR-1 Table B
SHEU_EQUIP_KWH = 3700.0   # kWh/yr appliances (total, including fridge)
SHEU_LIGHT_KWH = 1262.0   # kWh/yr lighting

# RF2: IDF's refrigerator1 annual kWh (DR-1 Table C, SHEU fridge UEC, SingleD).
# Subtract from SHEU target so STEP9 + refrigerator1 don't double-count the fridge.
FRIDGE_KWH_IDF     = 448.0
SHEU_EQUIP_KWH_NET = SHEU_EQUIP_KWH - FRIDGE_KWH_IDF  # 3700 - 448 = 3252 kWh

N_WEEKDAY = 261   # days/yr
N_WEEKEND = 104   # days/yr


# ---------------------------------------------------------------------------
# Schedule computation
# ---------------------------------------------------------------------------

def compute_48slot_loads(member_rows_by_daytype: dict) -> dict:
    """Compute 48-slot equipment_W and lighting_frac for one household.

    Parameters
    ----------
    member_rows_by_daytype : {'Weekday': [row_dicts], 'Weekend': [row_dicts]}
        Each row_dict has act30_001..048 and hom30_001..048 columns.

    Returns
    -------
    {'Weekday': {'equipment_W': np.ndarray(48), 'lighting_frac': np.ndarray(48)},
     'Weekend': {'equipment_W': np.ndarray(48), 'lighting_frac': np.ndarray(48)}}

    Red-flag fixes applied here:
      RF1 — dw_cooldown: dishwasher cannot re-trigger while running or in cooldown (6-slot
            post-run gap ≈ 3h, preventing consecutive eating slots from extending queue).
    """
    result = {}
    for day_type, member_rows in member_rows_by_daytype.items():
        equip_W    = np.full(48, BASELOAD_W, dtype=float)
        light_frac = np.zeros(48, dtype=float)
        dw_queue    = 0   # dishwasher slots remaining
        dw_cooldown = 0   # RF1: slots until re-trigger allowed

        for t in range(48):
            slot_key = f'{t + 1:03d}'
            home_acts = []
            for row in member_rows:
                a = int(row.get(f'act30_{slot_key}') or 0)
                h = int(row.get(f'hom30_{slot_key}') or 0)
                if h > 0:
                    home_acts.append(a)

            n_present = len(home_acts)
            eff_n     = eff(n_present)

            if n_present > 0:
                for bucket in SHARED_BUCKETS - {'dishwasher'}:
                    max_wt = max((WEIGHT.get(a, {}).get(bucket, 0.0)
                                  for a in home_acts), default=0.0)
                    equip_W[t] += max_wt * APPLIANCE_W[bucket] * eff_n

                # RF1: trigger only when not already running AND cooldown expired
                if dw_queue == 0 and dw_cooldown == 0:
                    if any(WEIGHT.get(a, {}).get('dishwasher', 0.0) > 0 for a in home_acts):
                        dw_queue = 3

                for bucket in PERSONAL_BUCKETS:
                    sum_wt = sum(WEIGHT.get(a, {}).get(bucket, 0.0) for a in home_acts)
                    equip_W[t] += sum_wt * APPLIANCE_W[bucket]

                if any(WEIGHT.get(a, {}).get('lighting', 0.0) > 0 for a in home_acts):
                    light_frac[t] = 1.0

            # Dishwasher queue and cooldown run regardless of current activity
            if dw_queue > 0:
                equip_W[t] += APPLIANCE_W['dishwasher'] * eff_n
                dw_queue -= 1
                if dw_queue == 0:
                    dw_cooldown = 6  # 3h minimum gap before next run
            elif dw_cooldown > 0:
                dw_cooldown -= 1

        result[day_type] = {'equipment_W': equip_W, 'lighting_frac': light_frac}
    return result


def slots_to_hours(arr48: np.ndarray) -> np.ndarray:
    """Average adjacent 30-min slots into 24 hourly values."""
    a = np.array(arr48, dtype=float)
    return (a[0::2] + a[1::2]) / 2.0


def annual_kwh(wd_24h: np.ndarray, we_24h: np.ndarray) -> float:
    """Annual kWh from weekday and weekend hourly W arrays."""
    return (N_WEEKDAY * float(np.sum(wd_24h)) +
            N_WEEKEND * float(np.sum(we_24h))) / 1000.0


def calibrate_schedules(raw: dict) -> dict:
    """Scale 48-slot raw schedules to SHEU SingleD targets.

    RF2 fix: calibration target for equipment is SHEU_EQUIP_KWH_NET = 3252 kWh
    (SHEU 3700 minus FRIDGE_KWH_IDF 448), so the IDF's refrigerator1 object and
    the STEP9 BASELOAD_W are not double-counted.

    Parameters
    ----------
    raw : {'Weekday': {'equipment_W': arr48, 'lighting_frac': arr48},
           'Weekend': {'equipment_W': arr48, 'lighting_frac': arr48}}

    Returns
    -------
    {
      'equip_frac_wd'    : np.ndarray(24),  # 0-1 fraction for E+ schedule
      'equip_frac_we'    : np.ndarray(24),
      'equip_design_W'   : float,           # E+ DesignLevel (W); max(wd, we) * scale
      'equip_kwh_raw'    : float,           # raw annual kWh before calibration
      'equip_scale'      : float,           # calibration scalar f_e
      'light_frac_wd'    : np.ndarray(24),  # 0-1 lighting fraction
      'light_frac_we'    : np.ndarray(24),
      'light_design_W'   : float,           # E+ Lighting_Level (W)
      'light_kwh_raw_at1W': float,          # annual frac-hours (kWh at 1W design level)
    }
    """
    eq_wd = slots_to_hours(raw['Weekday']['equipment_W'])
    eq_we = slots_to_hours(raw['Weekend']['equipment_W'])
    lt_wd = slots_to_hours(raw['Weekday']['lighting_frac'])
    lt_we = slots_to_hours(raw['Weekend']['lighting_frac'])

    # Equipment calibration (RF2: use net target, fridge already in IDF)
    equip_kwh_raw = annual_kwh(eq_wd, eq_we)
    peak_equip    = max(float(np.max(eq_wd)), float(np.max(eq_we)), 1.0)

    if equip_kwh_raw > 0:
        equip_scale    = SHEU_EQUIP_KWH_NET / equip_kwh_raw
        equip_design_W = peak_equip * equip_scale
        equip_frac_wd  = eq_wd / peak_equip
        equip_frac_we  = eq_we / peak_equip
    else:
        equip_scale    = 1.0
        equip_design_W = BASELOAD_W
        equip_frac_wd  = np.ones(24)
        equip_frac_we  = np.ones(24)

    # Lighting calibration: D_light * total_frac_hours/yr / 1000 = SHEU_LIGHT_KWH
    total_frac_h = (N_WEEKDAY * float(np.sum(lt_wd)) +
                    N_WEEKEND * float(np.sum(lt_we)))
    light_kwh_raw_at_1W = total_frac_h / 1000.0
    if total_frac_h > 0:
        light_design_W = SHEU_LIGHT_KWH * 1000.0 / total_frac_h
    else:
        light_design_W = 0.0

    return {
        'equip_frac_wd':      equip_frac_wd,
        'equip_frac_we':      equip_frac_we,
        'equip_design_W':     equip_design_W,
        'equip_kwh_raw':      equip_kwh_raw,
        'equip_scale':        equip_scale,
        'light_frac_wd':      lt_wd,
        'light_frac_we':      lt_we,
        'light_design_W':     light_design_W,
        'light_kwh_raw_at1W': light_kwh_raw_at_1W,
    }
