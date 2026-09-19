"""
test_task9_simulation_validation.py

Post-run validation for Task 9: Option 7 Monte Carlo Comparative Neighbourhood
Simulation on NUS_RC4.idf (N=10 iterations, weekly mode).

Usage:
    py eSim_tests/test_task9_simulation_validation.py <batch_dir>

Where <batch_dir> is the full path to the MonteCarlo_Neighbourhood_N10_<timestamp>
directory that Option 7 produced.

Checks:
  a) DTYPE compliance   — iter_1 schedule CSVs cross-referenced against BEM_Schedules
  b) MC variation       — per-iteration EUI differs across iterations
  c) Simulation success — eplusout.sql exists in every expected directory
  d) EUI sanity         — all total-site EUI values in [50, 500] kWh/m2-year
  e) EUI spread         — mean/std per scenario across iterations (std > 0 expected)
"""

import sys
import os
import csv
import glob
import sqlite3
import statistics

# ── Config ────────────────────────────────────────────────────────────────────
SCENARIOS     = ('2005', '2010', '2015', '2022', '2025')
EUI_MIN       = 50.0    # kWh/m2-year lower bound (sanity)
EUI_MAX       = 500.0   # kWh/m2-year upper bound (sanity)
EUI_VARIATION_TOLERANCE = 0.5  # kWh/m2 — iterations closer than this are "same"
EXPECTED_DTYPE = 'MidRise'

PASS_TAG = 'PASS'
FAIL_TAG = 'FAIL'
WARN_TAG = 'WARN'

_failures = []

def _tag(ok, msg, warn=False):
    if ok:
        print(f"  {msg} ... {PASS_TAG}")
    elif warn:
        print(f"  {msg} ... {WARN_TAG}")
    else:
        print(f"  {msg} ... {FAIL_TAG}")
        _failures.append(msg)

def _info(msg):
    print(f"    {msg}")

# ── EUI helpers ───────────────────────────────────────────────────────────────

def _get_eui_from_sql(sql_path):
    """Return total site EUI (kWh/m2-year) from an eplusout.sql file.

    Uses 'Total Site Energy / Energy Per Conditioned Building Area' (MJ/m2)
    from the AnnualBuildingUtilityPerformanceSummary report, converting to kWh/m2.
    Falls back to summing End Uses rows if the summary row is missing.
    """
    try:
        conn = sqlite3.connect(sql_path)
        cur  = conn.cursor()

        # Primary path: pre-computed intensity from Site and Source Energy table
        cur.execute(
            "SELECT Value, Units FROM TabularDataWithStrings "
            "WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' "
            "AND TableName='Site and Source Energy' "
            "AND RowName='Total Site Energy' "
            "AND ColumnName='Energy Per Conditioned Building Area'"
        )
        row = cur.fetchone()
        if row and row[0]:
            try:
                val  = float(row[0])
                unit = row[1]
                conn.close()
                if unit == 'MJ/m2':
                    return val / 3.6          # MJ/m2 → kWh/m2
                elif unit == 'kWh/m2':
                    return val
                elif unit == 'GJ/m2':
                    return val * 277.778
            except (ValueError, TypeError):
                pass

        # Fallback: sum individual End Uses rows (skip empty and "Total End Uses")
        cur.execute(
            "SELECT Value, Units FROM TabularDataWithStrings "
            "WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' "
            "AND TableName='End Uses' "
            "AND RowName NOT IN ('', 'Total End Uses') "
            "AND Units NOT LIKE '%m3%'"
        )
        rows = cur.fetchall()

        # Floor area for normalisation
        cur.execute(
            "SELECT Value, Units FROM TabularDataWithStrings "
            "WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' "
            "AND TableName='Building Area' "
            "AND RowName='Net Conditioned Building Area' "
            "AND ColumnName='Area'"
        )
        area_row = cur.fetchone()
        conn.close()

        area = 1.0
        if area_row and area_row[0]:
            try:
                av = float(area_row[0])
                au = area_row[1]
                area = av * 0.092903 if au in ('ft2', 'ft²') else av
            except (ValueError, TypeError):
                pass

        total_kwh = 0.0
        for val_str, unit in rows:
            try:
                val = float(val_str)
            except (ValueError, TypeError):
                continue
            if val <= 0:
                continue
            if unit == 'GJ':        total_kwh += val * 277.778
            elif unit == 'kWh':     total_kwh += val
            elif unit == 'J':       total_kwh += val / 3_600_000.0
            elif unit == 'kBtu':    total_kwh += val * 0.293071
            elif unit == 'MJ':      total_kwh += val * 0.277778

        return (total_kwh / area) if area > 0 else 0.0

    except Exception as exc:
        return None


# ── DTYPE lookup helpers ──────────────────────────────────────────────────────

def _build_dtype_map(bem_schedules_csv):
    """Return {SIM_HH_ID: DTYPE} from a BEM_Schedules_<year>.csv."""
    dtype_map = {}
    if not os.path.isfile(bem_schedules_csv):
        return dtype_map
    with open(bem_schedules_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hh_id = row.get('SIM_HH_ID', '').strip()
            dtype = row.get('DTYPE', '').strip()
            if hh_id and dtype:
                dtype_map[hh_id] = dtype
    return dtype_map


def _load_dtype_maps(bem_setup_dir):
    """Pre-load DTYPE maps for all years that have a BEM_Schedules CSV."""
    maps = {}
    for year in SCENARIOS:
        path = os.path.join(bem_setup_dir, f'BEM_Schedules_{year}.csv')
        if os.path.isfile(path):
            maps[year] = _build_dtype_map(path)
    return maps


# ── Main validation ───────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: py eSim_tests/test_task9_simulation_validation.py <batch_dir>")
        sys.exit(1)

    batch_dir = os.path.normpath(sys.argv[1])
    if not os.path.isdir(batch_dir):
        print(f"Error: batch_dir not found: {batch_dir}")
        sys.exit(1)

    batch_name   = os.path.basename(batch_dir)
    bem_setup_dir = os.path.normpath(os.path.join(batch_dir, '..', '..'))  # .../BEM_Setup
    schedules_export_dir = os.path.join(bem_setup_dir, 'SimResults_Schedules', batch_name)

    # Detect iteration count from iter_* subdirectories
    iter_dirs = sorted(glob.glob(os.path.join(batch_dir, 'iter_*')))
    N = len(iter_dirs)
    if N == 0:
        print(f"Error: no iter_* directories found in {batch_dir}")
        sys.exit(1)

    print(f"\nBatch:       {batch_name}")
    print(f"Iterations:  {N}")
    print(f"Scenarios:   {SCENARIOS}")
    print(f"Expected DTYPE: {EXPECTED_DTYPE}")

    dtype_maps = _load_dtype_maps(bem_setup_dir)

    # ── (a) DTYPE compliance ──────────────────────────────────────────────────
    print("\n=== (a) DTYPE Compliance ===")
    print("(checking iter_1 exported schedule CSVs only — later iterations are not exported)")

    if not os.path.isdir(schedules_export_dir):
        _tag(False, f"Schedule export dir missing: {schedules_export_dir}")
    else:
        all_dtype_ok = True
        any_csv_found = False

        for year in SCENARIOS:
            year_dir = os.path.join(schedules_export_dir, f'{year}_Iter1')
            if not os.path.isdir(year_dir):
                _info(f"  Scenario {year}: export dir not found — skipping")
                continue

            csv_files = glob.glob(os.path.join(year_dir, 'schedule_HH*.csv'))
            if not csv_files:
                _info(f"  Scenario {year}: no schedule CSVs found")
                continue

            any_csv_found = True
            dtype_map = dtype_maps.get(year, {})
            hh_ids = []
            for csv_path in csv_files:
                # Extract HH ID from filename: schedule_HH<id>.csv
                fname = os.path.basename(csv_path)
                hh_id = fname.replace('schedule_HH', '').replace('.csv', '').strip()
                hh_ids.append(hh_id)

            dtypes = []
            unknown = []
            for hh_id in hh_ids:
                dt = dtype_map.get(hh_id)
                if dt is None:
                    unknown.append(hh_id)
                    dtypes.append('UNKNOWN')
                else:
                    dtypes.append(dt)

            wrong = [d for d in dtypes if d not in (EXPECTED_DTYPE, 'UNKNOWN')]
            ok = len(wrong) == 0 and len(unknown) == 0

            _tag(ok, f"Scenario {year}: {len(hh_ids)} HHs assigned — all {EXPECTED_DTYPE}")
            if wrong:
                all_dtype_ok = False
                _info(f"  Wrong DTYPE found: {set(wrong)}")
            if unknown:
                _info(f"  HH IDs not found in BEM_Schedules_{year}.csv: {unknown[:5]}...")
                all_dtype_ok = False

        if not any_csv_found:
            _tag(False, "No schedule CSVs found at all in export dir")

    # ── (c) Simulation success ────────────────────────────────────────────────
    # (Running before (b) so EUI data is collected in one pass)
    print("\n=== (c) Simulation Success ===")

    missing_sql = []
    iter_eui = {scenario: [] for scenario in SCENARIOS}  # per-scenario EUI list
    default_eui = None

    # Check Default
    default_sql = os.path.join(batch_dir, 'Default', 'eplusout.sql')
    _tag(os.path.isfile(default_sql), "Default: eplusout.sql exists")
    if os.path.isfile(default_sql):
        default_eui = _get_eui_from_sql(default_sql)

    # Check all iterations
    total_expected = N * len(SCENARIOS)
    found = 0
    for k in range(1, N + 1):
        for scenario in SCENARIOS:
            sql_path = os.path.join(batch_dir, f'iter_{k}', scenario, 'eplusout.sql')
            if os.path.isfile(sql_path):
                found += 1
                eui = _get_eui_from_sql(sql_path)
                if eui is not None:
                    iter_eui[scenario].append((k, eui))
            else:
                missing_sql.append(f"iter_{k}/{scenario}/eplusout.sql")

    _tag(found == total_expected,
         f"{found}/{total_expected} scenario runs have eplusout.sql")
    if missing_sql:
        for m in missing_sql[:5]:
            _info(f"  Missing: {m}")
        if len(missing_sql) > 5:
            _info(f"  ...and {len(missing_sql)-5} more")

    # ── (d) EUI sanity ────────────────────────────────────────────────────────
    print("\n=== (d) EUI Sanity [50–500 kWh/m2-year] ===")

    all_eui_values = []
    if default_eui is not None:
        all_eui_values.append(('Default', default_eui))

    for scenario, vals in iter_eui.items():
        for k, eui in vals:
            all_eui_values.append((f"iter_{k}/{scenario}", eui))

    if not all_eui_values:
        _tag(False, "No EUI values could be read from SQL files")
    else:
        out_of_range = [(label, eui) for label, eui in all_eui_values
                        if eui < EUI_MIN or eui > EUI_MAX]
        zeros = [(label, eui) for label, eui in all_eui_values if eui <= 0]

        _tag(len(zeros) == 0,
             f"No zero/negative EUI values ({len(zeros)} found)")
        _tag(len(out_of_range) == 0,
             f"All {len(all_eui_values)} EUI values within [{EUI_MIN}, {EUI_MAX}] kWh/m2-year")

        if out_of_range:
            for label, eui in out_of_range[:5]:
                _info(f"  Out of range: {label} = {eui:.1f}")

        if default_eui is not None:
            _info(f"Default EUI = {default_eui:.1f} kWh/m2-year")

    # ── (e) Cross-iteration EUI spread ───────────────────────────────────────
    print("\n=== (e) Cross-Iteration EUI Spread ===")

    scenario_stats = {}
    for scenario in SCENARIOS:
        vals = [eui for _, eui in iter_eui[scenario]]
        if len(vals) < 2:
            _info(f"  {scenario}: only {len(vals)} iteration(s) — cannot compute std")
            continue
        mean = statistics.mean(vals)
        std  = statistics.stdev(vals)
        scenario_stats[scenario] = (mean, std, vals)
        _info(f"  {scenario}: mean={mean:.2f}, std={std:.3f} kWh/m2-year  (N={len(vals)})")

    all_std_gt0 = all(s > 0 for _, (_, s, _) in scenario_stats.items())
    _tag(all_std_gt0, "std > 0 for all year scenarios (Monte Carlo producing EUI variation)")

    if default_eui is not None:
        _info(f"  Default: mean={default_eui:.2f}, std=0.000 kWh/m2-year (expected — deterministic)")

    # ── (b) Monte Carlo variation ─────────────────────────────────────────────
    print("\n=== (b) Monte Carlo Variation ===")
    print("(proxy: at least 2 iterations produce different EUI, implying different HH draws)")

    variation_found = False
    for scenario in SCENARIOS:
        if scenario not in scenario_stats:
            continue
        _, std, vals = scenario_stats[scenario]
        if std > EUI_VARIATION_TOLERANCE:
            variation_found = True
            _info(f"  {scenario}: std={std:.3f} > {EUI_VARIATION_TOLERANCE} — variation confirmed")
            break

    if not variation_found:
        # Check per-scenario: are any two iteration EUI values meaningfully different?
        for scenario in SCENARIOS:
            vals = [eui for _, eui in iter_eui.get(scenario, [])]
            if len(vals) >= 2:
                max_diff = max(vals) - min(vals)
                if max_diff > EUI_VARIATION_TOLERANCE:
                    variation_found = True
                    _info(f"  {scenario}: max EUI spread = {max_diff:.3f} kWh/m2")
                    break

    _tag(variation_found, "At least 2 iterations produce meaningfully different EUI")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if not _failures:
        print("All checks passed.")
    else:
        print(f"{len(_failures)} check(s) FAILED:")
        for f in _failures:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == '__main__':
    main()
