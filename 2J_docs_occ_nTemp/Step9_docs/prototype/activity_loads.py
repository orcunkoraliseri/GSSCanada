"""
Step 9 prototype — activity-driven equipment & lighting schedule builder.

Translates 30-min GSS activity sequences (act30_001..048) into hourly
EnergyPlus-ready equipment (W) and lighting fraction (0..1) schedules,
calibrated to NRCan SHEU 2019 SingleD targets.

Refs: Richardson/CREST 2010; DR-2 ("Activity-Based Load Modeling Numbers.md");
      DR-1 ("Calibration Dataset…").  Do NOT import from 07_aug_to_bem.py
      or any do-not-touch ML file — this module is standalone.
"""
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Activity → end-use weight matrix  (DR-2 Table / task prompt)
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

SHARED_BUCKETS  = {'cooking', 'dishwasher', 'washer', 'dryer', 'tv'}
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
_COOKING_W = (0.45 * 3000 * 0.50          # range, 50 % duty cycle
            + 0.35 * 1500 * (10 / 30)     # microwave, ~10-min burst
            + 0.20 * 1200 * (10 / 30))    # small appliance, ~10-min burst

APPLIANCE_W = {
    'cooking':    _COOKING_W,   # ≈ 930 W
    'dishwasher': 930,           # 930 W; 90-120 min cycle → queue 3 slots
    'washer':     470,
    'dryer':      2100,
    'tv':         100,
    'pc':         150,           # desktop + monitor
}

BASELOAD_W = 130.0   # fridge + standby, always-on floor (never zeroed)

# SHEU 2019, SingleD, DR-1 Table B
SHEU_EQUIP_KWH  = 3700.0   # kWh / yr
SHEU_LIGHT_KWH  = 1262.0   # kWh / yr

N_WEEKDAY = 261   # days / yr
N_WEEKEND = 104   # days / yr


# ---------------------------------------------------------------------------
# 2030 activity assembly (replicates 07_aug_to_bem.assemble_2030, same seed)
# ---------------------------------------------------------------------------
_ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
_HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]


def assemble_2030_df(aug_path: str, d2030_path: str) -> pd.DataFrame:
    """Replicate 07_aug_to_bem.assemble_2030() exactly (seed=42).

    Keeps the 2022 stock's HH_IDs / demographics but replaces act30/hom30
    with randomly drawn 2030 diaries — same logic as the production script.
    """
    rng   = np.random.default_rng(42)
    stock = pd.read_csv(aug_path,   low_memory=False)
    d30   = pd.read_csv(d2030_path, low_memory=False)
    out   = stock.copy()
    for k in (1, 2, 3):
        smask = (stock["DDAY_STRATA"].values == k)
        pool  = d30[d30["DDAY_STRATA"] == k]
        pick  = rng.integers(0, len(pool), size=int(smask.sum()))
        out.loc[smask, _ACT_COLS + _HOM_COLS] = pool.iloc[pick][_ACT_COLS + _HOM_COLS].values
    return out


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------

def load_hh_activity(hh_ids, aug_path: str, d2030_path: str) -> dict:
    """Load per-member activity rows for each HH in hh_ids, for 2022 and 2030.

    Returns
    -------
    {year: {hh_id: {'Weekday': [rows], 'Weekend': [rows], 'hhsize': int}}}
    where rows = list of row dicts (from the source DataFrame).
    """
    needed_cols = ['HH_ID', 'DDAY_STRATA', 'HHSIZE'] + _ACT_COLS + _HOM_COLS

    df22 = pd.read_csv(aug_path, low_memory=False, usecols=needed_cols)
    df30_full = assemble_2030_df(aug_path, d2030_path)

    out = {}
    for year, df in [('2022', df22), ('2030', df30_full)]:
        sub = df[df['HH_ID'].isin(hh_ids)][needed_cols].copy()
        year_dict = {}
        for hh_id in hh_ids:
            hh_df = sub[sub['HH_ID'] == hh_id]
            if hh_df.empty:
                print(f"  WARN: HH_ID={hh_id} not found in {year} source data.")
                year_dict[hh_id] = {'Weekday': [], 'Weekend': [], 'hhsize': 1}
                continue
            hhsize = int(hh_df['HHSIZE'].iloc[0])
            wd = hh_df[hh_df['DDAY_STRATA'] == 1].to_dict('records')
            we = hh_df[hh_df['DDAY_STRATA'].isin([2, 3])].to_dict('records')
            # Fallback: use whichever day type exists for the missing one
            if not wd and we:
                wd = we
                print(f"  INFO: HH {hh_id}/{year}: no Weekday rows; using Weekend as proxy.")
            if not we and wd:
                we = wd
                print(f"  INFO: HH {hh_id}/{year}: no Weekend rows; using Weekday as proxy.")
            year_dict[hh_id] = {'Weekday': wd, 'Weekend': we, 'hhsize': hhsize}
        out[year] = year_dict
    return out


# ---------------------------------------------------------------------------
# Schedule computation
# ---------------------------------------------------------------------------

def compute_48slot_loads(member_rows_by_daytype: dict) -> dict:
    """Compute 48-slot equipment_W and lighting_frac for one household.

    Parameters
    ----------
    member_rows_by_daytype : {'Weekday': [rows], 'Weekend': [rows]}

    Returns
    -------
    {'Weekday': {'equipment_W': np.ndarray(48), 'lighting_frac': np.ndarray(48)},
     'Weekend': {'equipment_W': np.ndarray(48), 'lighting_frac': np.ndarray(48)}}
    """
    result = {}
    for day_type, member_rows in member_rows_by_daytype.items():
        equip_W    = np.full(48, BASELOAD_W, dtype=float)
        light_frac = np.zeros(48, dtype=float)
        dw_queue   = 0   # dishwasher countdown (slots remaining)

        for t in range(48):
            slot_key = f'{t + 1:03d}'
            # Collect activities of home members this slot
            home_acts = []
            for row in member_rows:
                a = int(row.get(f'act30_{slot_key}') or 0)
                h = int(row.get(f'hom30_{slot_key}') or 0)
                if h > 0:
                    home_acts.append(a)

            n_present = len(home_acts)
            eff_n     = eff(n_present)

            if n_present > 0:
                # Shared buckets: max weight across present members, scale by EFF(n)
                for bucket in SHARED_BUCKETS - {'dishwasher'}:
                    max_wt = max((WEIGHT.get(a, {}).get(bucket, 0.0)
                                  for a in home_acts), default=0.0)
                    equip_W[t] += max_wt * APPLIANCE_W[bucket] * eff_n

                # Dishwasher trigger: start 3-slot queue if any member drives it
                if any(WEIGHT.get(a, {}).get('dishwasher', 0.0) > 0 for a in home_acts):
                    dw_queue = max(dw_queue, 3)

                # Personal buckets: sum across present members (linear scaling)
                for bucket in PERSONAL_BUCKETS:
                    sum_wt = sum(WEIGHT.get(a, {}).get(bucket, 0.0) for a in home_acts)
                    equip_W[t] += sum_wt * APPLIANCE_W[bucket]

                # Lighting: on if any present member is in an active-home state
                if any(WEIGHT.get(a, {}).get('lighting', 0.0) > 0 for a in home_acts):
                    light_frac[t] = 1.0

            # Dishwasher queue runs regardless of current activity
            if dw_queue > 0:
                equip_W[t] += APPLIANCE_W['dishwasher'] * eff_n
                dw_queue   -= 1

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

    Parameters
    ----------
    raw : {'Weekday': {'equipment_W': arr48, 'lighting_frac': arr48},
           'Weekend': {'equipment_W': arr48, 'lighting_frac': arr48}}

    Returns
    -------
    {
      'equip_frac_wd'  : np.ndarray(24),  # 0–1 fraction for E+ schedule
      'equip_frac_we'  : np.ndarray(24),
      'equip_design_W' : float,           # E+ DesignLevel (W)
      'equip_kwh_raw'  : float,
      'equip_scale'    : float,
      'light_frac_wd'  : np.ndarray(24),  # 0–1 lighting fraction
      'light_frac_we'  : np.ndarray(24),
      'light_design_W' : float,           # total calibrated lighting W
      'light_kwh_raw_at1W' : float,
    }
    """
    eq_wd = slots_to_hours(raw['Weekday']['equipment_W'])
    eq_we = slots_to_hours(raw['Weekend']['equipment_W'])
    lt_wd = slots_to_hours(raw['Weekday']['lighting_frac'])
    lt_we = slots_to_hours(raw['Weekend']['lighting_frac'])

    # Equipment calibration
    equip_kwh_raw = annual_kwh(eq_wd, eq_we)
    peak_equip    = max(float(np.max(eq_wd)), float(np.max(eq_we)), 1.0)

    if equip_kwh_raw > 0:
        equip_scale    = SHEU_EQUIP_KWH / equip_kwh_raw
        equip_design_W = peak_equip * equip_scale
        equip_frac_wd  = eq_wd / peak_equip
        equip_frac_we  = eq_we / peak_equip
    else:
        equip_scale    = 1.0
        equip_design_W = BASELOAD_W
        equip_frac_wd  = np.ones(24)
        equip_frac_we  = np.ones(24)

    # Lighting calibration
    # D_light * sum(frac_h * 1h) / 1000 = SHEU_LIGHT_KWH
    # → D_light = SHEU_LIGHT_KWH * 1000 / total_fraction_hours
    total_frac_h = (N_WEEKDAY * float(np.sum(lt_wd)) +
                    N_WEEKEND * float(np.sum(lt_we)))   # fraction·hours/yr
    light_kwh_raw_at_1W = total_frac_h / 1000.0
    if total_frac_h > 0:
        light_design_W = SHEU_LIGHT_KWH * 1000.0 / total_frac_h
    else:
        light_design_W = 0.0

    return {
        'equip_frac_wd':     equip_frac_wd,
        'equip_frac_we':     equip_frac_we,
        'equip_design_W':    equip_design_W,
        'equip_kwh_raw':     equip_kwh_raw,
        'equip_scale':       equip_scale,
        'light_frac_wd':     lt_wd,
        'light_frac_we':     lt_we,
        'light_design_W':    light_design_W,
        'light_kwh_raw_at1W': light_kwh_raw_at_1W,
    }
