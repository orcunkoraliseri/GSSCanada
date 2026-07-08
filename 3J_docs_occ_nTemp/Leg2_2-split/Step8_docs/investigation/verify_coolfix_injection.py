"""verify_coolfix_injection.py — Step 8 CoolFix v2 static injection check (3J Leg-2).

Generates one MidRise `in.idf` and one DetachedHouse `in.idf` through the normal
`integration.inject_schedules()` path (no EnergyPlus run) and asserts the injected
Schedule:Compact objects match what step8_coolfix_implementation_plan.md "Fix v2"
specifies. This is the check that would have caught fix v1 pre-sim (see
step8_resid_heating_cooling_dominance_investigation.md §9).

Usage: py investigation/verify_coolfix_injection.py
"""
import glob
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # Step8_docs/investigation/
STEP8_DOCS = HERE.parent                            # Step8_docs/
sys.path.insert(0, str(STEP8_DOCS))

from eSim_bem_utils_3J.main import (               # noqa: E402
    STEP8_BUILDINGS_DIR,
    WEATHER_DIR,
    SCHEDULE_FILE_MAP,
)
from eSim_bem_utils_3J import integration           # noqa: E402

OUT_DIR = os.path.join(STEP8_DOCS, "outputs_step8", "coolfix_verify")
os.makedirs(OUT_DIR, exist_ok=True)

WINTER_MONTHS = integration.COOLFIX_WINTER_MONTHS
SUMMER_MONTHS = tuple(m for m in
                      ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
                      if m not in WINTER_MONTHS)
EXPECTED_WINTER_SP = max(integration.COOLFIX_WINTER_COOL_SP, 27.0)  # 27.0 = cooling_setback default


def _find_one(folder, ext, substr):
    hits = [p for p in glob.glob(os.path.join(folder, f"*{ext}"))
            if substr.lower() in os.path.basename(p).lower()]
    return hits[0] if hits else None


def _inject_one(arch_label, idf_substr, dtype, epw_substr, out_name):
    idf_path = _find_one(STEP8_BUILDINGS_DIR, ".idf", idf_substr)
    epw_path = _find_one(WEATHER_DIR, ".epw", epw_substr)
    assert idf_path, f"IDF not found for {arch_label} (substr={idf_substr!r}) in {STEP8_BUILDINGS_DIR}"
    assert epw_path, f"EPW not found (substr={epw_substr!r}) in {WEATHER_DIR}"

    csv_path = SCHEDULE_FILE_MAP['2022']
    schedules = integration.load_schedules(csv_path, dwelling_type=dtype, region=None)
    assert schedules, f"No households loaded for dtype={dtype!r} from {csv_path}"
    hh_id = sorted(schedules.keys())[0]

    out_path = os.path.join(OUT_DIR, out_name)
    integration.inject_schedules(
        idf_path, out_path, hh_id, schedules[hh_id],
        epw_path=epw_path, sim_results_dir=OUT_DIR,
        batch_name=f"coolfix_verify_{arch_label}", run_period_mode='standard',
        output_frequency='Hourly', step8_occ_couple=True,
    )
    return out_path, hh_id


def _extract_schedule_object_fields(idf, sched_name):
    """Use eppy (already loaded IDF) to pull the raw field list for one Schedule:Compact."""
    matches = [s for s in idf.idfobjects['SCHEDULE:COMPACT'] if s.Name == sched_name]
    assert matches, f"Schedule:Compact '{sched_name}' not found via eppy"
    return list(matches[0].obj)


def _fields_to_month_blocks(fields):
    """Parse a Schedule:Compact eppy field list into {through_date: {(day_type, hour): value}}."""
    blocks = {}
    cur_through = None
    cur_day_type = None
    i = 0
    n = len(fields)
    while i < n:
        f = str(fields[i]).strip()
        if f.startswith("Through:"):
            cur_through = f.split(":", 1)[1].strip()
            blocks[cur_through] = {}
        elif f.startswith("For:"):
            cur_day_type = f.split(":", 1)[1].strip()
        elif f.startswith("Until:"):
            hour = f.split(":", 1)[1].strip()
            i += 1
            val = float(str(fields[i]).strip())
            blocks[cur_through][(cur_day_type, hour)] = val
        i += 1
    return blocks


def _load_idf(idf_path):
    from eppy.modeleditor import IDF
    from eSim_bem_utils_3J import config
    IDF.setiddname(config.resolve_idd_path())
    return IDF(idf_path)


def _month_of_through(through_date):
    month = int(through_date.split("/", 1)[0])
    names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return names[month - 1]


def check_midrise(out_path, hh_id):
    idf = _load_idf(out_path)
    cool_name = f"CoolSP_HH_{hh_id}"
    heat_name = f"HeatSP_HH_{hh_id}"

    cool_blocks = _fields_to_month_blocks(_extract_schedule_object_fields(idf, cool_name))
    ok = True
    if len(cool_blocks) < 2:
        print(f"  [FAIL] MidRise {cool_name}: expected multiple Through: blocks, got {len(cool_blocks)}")
        ok = False
    for through, values in cool_blocks.items():
        month = _month_of_through(through)
        vals = set(values.values())
        if month in WINTER_MONTHS:
            if vals != {EXPECTED_WINTER_SP}:
                print(f"  [FAIL] MidRise {cool_name} winter block {through} ({month}): "
                      f"expected all {EXPECTED_WINTER_SP}, got {vals}")
                ok = False
        elif month in SUMMER_MONTHS:
            if not vals.issubset({24.0, 27.0}):
                print(f"  [FAIL] MidRise {cool_name} summer block {through} ({month}): expected subset of {{24.0,27.0}}, got {vals}")
                ok = False
        else:
            print(f"  [FAIL] MidRise {cool_name}: unexpected month {month} in block {through}")
            ok = False
    if ok:
        print(f"  [PASS] MidRise {cool_name}: {len(cool_blocks)} monthly Through: blocks, "
              f"winter={EXPECTED_WINTER_SP} flat, summer subset of {{24.0,27.0}}")

    heat_blocks = _fields_to_month_blocks(_extract_schedule_object_fields(idf, heat_name))
    if len(heat_blocks) == 1 and "12/31" in heat_blocks:
        vals = sorted(set(heat_blocks["12/31"].values()))
        print(f"  [PASS] MidRise {heat_name}: single Through: 12/31 block, values={vals} (unchanged heating path)")
    else:
        print(f"  [FAIL] MidRise {heat_name}: expected single Through: 12/31 block, got {sorted(heat_blocks.keys())}")
        ok = False

    return ok


def check_detached_house(out_path, hh_id):
    idf = _load_idf(out_path)
    cool_name = f"CoolSP_HH_{hh_id}"
    cool_blocks = _fields_to_month_blocks(_extract_schedule_object_fields(idf, cool_name))
    ok = True
    if len(cool_blocks) == 1 and "12/31" in cool_blocks:
        vals = sorted(set(cool_blocks["12/31"].values()))
        if set(vals).issubset({24.0, 27.0}) or (len(vals) <= 2):
            print(f"  [PASS] DetachedHouse {cool_name}: flat single-block form, values={vals} (no-op confirmed)")
        else:
            print(f"  [FAIL] DetachedHouse {cool_name}: unexpected values {vals}")
            ok = False
    else:
        print(f"  [FAIL] DetachedHouse {cool_name}: expected single Through: 12/31 block, got {sorted(cool_blocks.keys())}")
        ok = False
    return ok


def main():
    print("=== CoolFix v2 static injection verification ===")

    print("\n-- MidRise --")
    mr_path, mr_hh = _inject_one("MidRise", "ApartmentMidRise", "MidRise", "Winnipeg", "MidRise_in.idf")
    mr_ok = check_midrise(mr_path, mr_hh)

    print("\n-- DetachedHouse (no-op control) --")
    dh_path, dh_hh = _inject_one("DetachedHouse", "DetachedHouse", "SingleD", "Winnipeg", "DetachedHouse_in.idf")
    dh_ok = check_detached_house(dh_path, dh_hh)

    print("\n=== Result ===")
    overall = mr_ok and dh_ok
    print("PASS — proceed to Phase C" if overall else "FAIL — fix Phase A before Phase C")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
