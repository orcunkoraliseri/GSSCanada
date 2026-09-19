"""
Task 23 — MidRise vs IECC SF Detached robustness check.

Runs Option 3 Default for Baseline_6A_Montreal with both baselines
(midrise and sf_detached) and prints per-end-use EUI for each.

Usage:
    cd eSim_tests
    python run_task23_baseline_comparison.py

The midrise run reuses an existing SQL file if available;
the sf_detached run always produces a fresh simulation.
"""
import os
import sys
import shutil
import sqlite3
import subprocess
import tempfile
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import eSim_bem_utils.idf_optimizer as idf_optimizer
import eSim_bem_utils.simulation as simulation
from eSim_bem_utils.config import ENERGYPLUS_EXE

BASE = PROJECT_ROOT

# ── paths ──────────────────────────────────────────────────────────────────
IDF_SOURCE = os.path.join(
    BASE, 'BEM_Setup', 'Buildings',
    'Baseline_6A_Montreal_US+SF+CZ6A+gasfurnace+heatedbsmt+IECC_2021.idf'
)
EPW = os.path.join(
    BASE, 'BEM_Setup', 'WeatherFile',
    'CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw'
)
MIDRISE_SQL_EXISTING = os.path.join(
    BASE, 'BEM_Setup', 'SimResults',
    'Comparative_HH1p_1775735913', 'Default', 'eplusout.sql'
)
OUT_DIR = os.path.join(BASE, 'BEM_Setup', 'SimResults', 'Task23_Baseline_Comparison')

# ── helpers ────────────────────────────────────────────────────────────────
KBTU_TO_KWH = 0.293071
FT2_TO_M2   = 0.092903


def run_ep(label: str, idf_path: str, epw_path: str, out_dir: str) -> str:
    """Runs EnergyPlus (via simulation module, which handles ExpandObjects) and returns SQL path."""
    os.makedirs(out_dir, exist_ok=True)
    result = simulation.run_simulation(
        idf_path=idf_path,
        epw_path=epw_path,
        output_dir=out_dir,
        ep_path=ENERGYPLUS_EXE,
        quiet=False,
    )
    if not result.get('success'):
        raise RuntimeError(f"EnergyPlus failed for {label}: {result.get('message')}")
    sql = os.path.join(out_dir, 'eplusout.sql')
    if not os.path.exists(sql):
        raise FileNotFoundError(f"eplusout.sql not found in {out_dir}")
    return sql


def extract_eui(sql_path: str) -> dict:
    """
    Returns dict with keys: floor_area_m2, Heating, Cooling, Lighting,
    Equipment, Fans, DHW, each in kWh/m².
    """
    conn = sqlite3.connect(sql_path)
    cur = conn.cursor()

    # Floor area
    cur.execute("""
        SELECT Value, Units FROM TabularDataWithStrings
        WHERE TableName='Building Area'
          AND ReportName='AnnualBuildingUtilityPerformanceSummary'
          AND RowName='Net Conditioned Building Area'
    """)
    row = cur.fetchone()
    if row:
        area_val = float(row[0])
        if row[1] in ('ft2', 'ft²'):
            area_m2 = area_val * FT2_TO_M2
        else:
            area_m2 = area_val
    else:
        area_m2 = 1.0  # fallback

    # End uses
    cur.execute("""
        SELECT RowName, ColumnName, Value, Units FROM TabularDataWithStrings
        WHERE TableName='End Uses'
          AND ReportName='AnnualBuildingUtilityPerformanceSummary'
    """)
    rows = cur.fetchall()
    conn.close()

    raw = {}
    for row_name, col_name, val_str, units in rows:
        try:
            val = float(val_str)
        except (ValueError, TypeError):
            continue
        if val == 0.0:
            continue
        if units == 'kBtu':
            val_kwh = val * KBTU_TO_KWH
        elif units == 'kWh':
            val_kwh = val
        elif units == 'GJ':
            val_kwh = val * 277.778
        elif 'm3' in str(units) or units == 'gal':
            continue
        else:
            val_kwh = val
        raw[row_name] = raw.get(row_name, 0.0) + val_kwh

    def eui(key):
        return round(raw.get(key, 0.0) / area_m2, 2)

    return {
        'floor_area_m2': round(area_m2, 1),
        'Heating':   eui('Heating'),
        'Cooling':   eui('Cooling'),
        'Lighting':  eui('Interior Lighting'),
        'Equipment': eui('Interior Equipment'),
        'Fans':      eui('Fans'),
        'DHW':       eui('Water Systems'),
    }


# ── main ───────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # ── Run 1: MidRise ────────────────────────────────────────────────────
    midrise_sql = MIDRISE_SQL_EXISTING
    if os.path.exists(midrise_sql):
        print(f"[MidRise] Reusing existing SQL: {midrise_sql}")
        run_id_midrise = 'Comparative_HH1p_1775735913/Default'
    else:
        midrise_dir = os.path.join(OUT_DIR, 'midrise_default')
        midrise_idf = os.path.join(OUT_DIR, 'Scenario_Default_midrise.idf')
        print("[MidRise] Preparing IDF with midrise baseline...")
        idf_optimizer.prepare_idf_for_simulation(
            IDF_SOURCE, midrise_idf, verbose=True,
            run_period_mode='standard', baseline='midrise',
        )
        print("[MidRise] Running EnergyPlus...")
        midrise_sql = run_ep("midrise_default", midrise_idf, EPW, midrise_dir)
        run_id_midrise = midrise_dir

    # ── Run 2: SF Detached ────────────────────────────────────────────────
    sfdet_dir = os.path.join(OUT_DIR, 'sfdetached_default')
    sfdet_idf = os.path.join(OUT_DIR, 'Scenario_Default_sfdetached.idf')
    print("\n[SF Detached] Preparing IDF with sf_detached baseline...")
    idf_optimizer.prepare_idf_for_simulation(
        IDF_SOURCE, sfdet_idf, verbose=True,
        run_period_mode='standard', baseline='sf_detached',
    )
    print("[SF Detached] Running EnergyPlus...")
    sfdet_sql = run_ep("sf_detached_default", sfdet_idf, EPW, sfdet_dir)
    run_id_sfdet = sfdet_dir

    # ── Extract EUI ────────────────────────────────────────────────────────
    print("\nExtracting EUI results...")
    mr = extract_eui(midrise_sql)
    sf = extract_eui(sfdet_sql)

    print(f"\nFloor area (MidRise run): {mr['floor_area_m2']} m²")
    print(f"Floor area (SF Det run):  {sf['floor_area_m2']} m²")

    end_uses = ['Heating', 'Cooling', 'Lighting', 'Equipment', 'Fans', 'DHW']
    print("\n{:<12} {:>10} {:>10} {:>10} {:>8}".format(
        "End Use", "MidRise", "SFDet", "d_abs", "d_rel%"))
    print("-" * 56)
    for eu in end_uses:
        v_mr = mr[eu]
        v_sf = sf[eu]
        delta_abs = round(v_sf - v_mr, 2)
        mean_v = (v_mr + v_sf) / 2 if (v_mr + v_sf) > 0 else 1.0
        delta_rel = round(delta_abs / mean_v * 100, 1) if mean_v > 0 else 0.0
        flag = ""
        if abs(v_mr) > 20 or abs(v_sf) > 20:  # dominant end-use
            if abs(delta_rel) > 15:
                flag = " WARN >15% rel"
        else:  # small end-use
            if abs(delta_abs) > 2.0:
                flag = " WARN >2 kWh/m2"
        print("{:<12} {:>10.2f} {:>10.2f} {:>+10.2f} {:>+7.1f}%{}".format(
            eu, v_mr, v_sf, delta_abs, delta_rel, flag))

    # Return structured results for the report writer
    return {
        'run_id_midrise': run_id_midrise,
        'run_id_sfdet':   run_id_sfdet,
        'midrise': mr,
        'sfdet':   sf,
    }


if __name__ == '__main__':
    results = main()
