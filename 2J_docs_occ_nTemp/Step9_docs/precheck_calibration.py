"""precheck_calibration.py — Step 9 analytic SHEU calibration pre-check (NO EnergyPlus).

Parses a *resolved* IDF and sums the annual kWh of every ElectricEquipment and Lights
object directly from its Design Level x schedule fractions (261 weekday / 104 weekend
days, matching activity_loads.annual_kwh), then compares the totals to the SHEU 2019
per-dwelling targets in activity_loads.SHEU_BY_DTYPE.

Purpose: run on the FIXED resolved IDFs *before* the E+ array to confirm the Step 9
consolidation wired correctly. If both totals land within +-tol of target AND no
Watts/Area object still carries a nonzero density, the calibration is sound. Otherwise
it pinpoints the leak (un-neutralized object, no-op Design_Level override under
Watts/Area, or a surviving double-count) per object, WITHOUT burning an E+ run.

This is the exact two-faced bug it guards against:
  * SF (EquipmentLevel): many appliance objects kept original watts + got the activity
    schedule  -> double-count  -> shows up as several big-kWh objects in the printout.
  * NECB apartments (Watts/Area): Design_Level override is a no-op  -> the object is
    flagged "LEAK ... density still ACTIVE".

Usage (on the cluster, via salloc/sbatch -- NEVER the login node):
    python precheck_calibration.py <resolved.idf> --dtype SingleD [--tol 0.05]

If imports fail, set PYTHONPATH (tcsh) to the staged dirs, e.g.:
    setenv PYTHONPATH /speed-scratch/o_iseri/step9_run:/speed-scratch/o_iseri/step9_run/Step8_docs
(the first must contain activity_loads.py; the second must contain the
 eSim_bem_utils_2J package).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Convenience: add likely staging roots so the script runs without manual PYTHONPATH
# in the repo layout (activity_loads.py in 2J_docs_occ_nTemp/, package in Step8_docs/).
for _p in (HERE,
           os.path.abspath(os.path.join(HERE, '..')),
           os.path.abspath(os.path.join(HERE, '..', 'Step8_docs')),
           os.getcwd()):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from eppy.modeleditor import IDF
    from eSim_bem_utils_2J import config
    from eSim_bem_utils_2J.integration import parse_schedule_values
    import activity_loads as AL
except ImportError as e:
    sys.exit(
        "ImportError: %s\n"
        "Set PYTHONPATH to include (a) the dir holding activity_loads.py and (b) the\n"
        "Step8_docs dir holding the eSim_bem_utils_2J package, e.g. (tcsh):\n"
        "  setenv PYTHONPATH "
        "/speed-scratch/o_iseri/step9_run:/speed-scratch/o_iseri/step9_run/Step8_docs\n"
        % e
    )

N_WD, N_WE = AL.N_WEEKDAY, AL.N_WEEKEND   # 261 / 104 days/yr

# EnergyPlus built-in always-on schedules (not in IDF as Schedule:Compact objects).
_ALWAYS_ON = {'always on discrete', 'always on', 'alwayson'}


def annual_frac_hours(idf, sched_name):
    """261*sum(weekday 24h) + 104*sum(weekend 24h) for any schedule type, or None."""
    if not sched_name:
        return None
    if sched_name.strip().lower() in _ALWAYS_ON:
        return N_WD * 24.0 + N_WE * 24.0  # 8760 frac-hours at value 1.0
    parsed = parse_schedule_values(idf, sched_name)
    if not parsed:
        return None
    wd = parsed.get('Weekday') or [0.0] * 24
    we = parsed.get('Weekend') or wd
    return N_WD * sum(wd) + N_WE * sum(we)


def object_kwh(idf, obj, level_field):
    """Annual kWh for one Lights/ElectricEquipment object.

    Returns (kwh, is_leak, note). A 'leak' is an object that still carries a nonzero
    Watts/Area (or Watts/Person) density -- i.e. the Step 9 fix failed to neutralize or
    convert it, so E+ will silently use that density and break calibration -- or an
    object whose schedule cannot be parsed.
    """
    method = (getattr(obj, 'Design_Level_Calculation_Method', '') or '').strip()
    sched = getattr(obj, 'Schedule_Name', '')
    fh = annual_frac_hours(idf, sched)
    if fh is None:
        return 0.0, True, f"{obj.Name}: schedule '{sched}' unparseable"

    if method in ('EquipmentLevel', 'LightingLevel', ''):
        level = float(getattr(obj, level_field, 0.0) or 0.0)
        return level * fh / 1000.0, False, ''

    # Watts/Area or Watts/Person still active => the consolidation missed this object.
    wpa = float(getattr(obj, 'Watts_per_Zone_Floor_Area', 0.0) or 0.0)
    wpp = float(getattr(obj, 'Watts_per_Person', 0.0) or 0.0)
    if wpa > 0 or wpp > 0:
        return 0.0, True, (
            f"{obj.Name}: method='{method}' density still ACTIVE "
            f"(W/m2={wpa}, W/person={wpp}); E+ will use it -- neutralize to 0 or "
            f"convert to EquipmentLevel/LightingLevel"
        )
    return 0.0, False, ''   # zeroed density => contributes nothing, not a leak


def _sum_objects(idf, obj_type, level_field, label):
    total, leaks = 0.0, []
    print(f"{label}:")
    objs = idf.idfobjects.get(obj_type, [])
    if not objs:
        print("  (none)")
    for obj in objs:
        kwh, leak, note = object_kwh(idf, obj, level_field)
        total += kwh
        tag = '   <-- LEAK' if leak else ''
        print(f"  {str(obj.Name):34s} {kwh:10.1f} kWh{tag}")
        if note:
            print(f"      {note}")
        if leak:
            leaks.append(note)
    return total, leaks


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('idf', help='path to a resolved IDF')
    ap.add_argument('--dtype', required=True, choices=sorted(AL.SHEU_BY_DTYPE),
                    help='dwelling type key (selects the SHEU target)')
    ap.add_argument('--tol', type=float, default=0.05,
                    help='fractional tolerance for the pre-check (default 0.05 = +-5%%)')
    args = ap.parse_args()

    if not IDF.getiddname():
        IDF.setiddname(config.resolve_idd_path())
    idf = IDF(args.idf)

    equip_net_target, light_target = AL.SHEU_BY_DTYPE[args.dtype]
    # IDF carries the activity carrier (net) PLUS the always-on fridge object (~448 kWh),
    # so the IDF equipment total should equal the gross SHEU appliance figure.
    equip_gross_target = equip_net_target + AL.FRIDGE_KWH_IDF

    print(f"\n=== {os.path.basename(args.idf)}   [{args.dtype}] ===")
    equip_kwh, equip_leaks = _sum_objects(idf, 'ELECTRICEQUIPMENT', 'Design_Level',
                                          'ElectricEquipment')
    light_kwh, light_leaks = _sum_objects(idf, 'LIGHTS', 'Lighting_Level', 'Lights')

    # D8 correction: OtherDwelling IDFs have N_units named fridges, but the SHEU target
    # and validate both account for only 1. Subtract the excess fridges before gating.
    if args.dtype == 'OtherDwelling':
        fridge_objs = [o for o in idf.idfobjects.get('ELECTRICEQUIPMENT', [])
                       if 'refrigerator' in (o.Name or '').lower()]
        n_fridges = len(fridge_objs)
        if n_fridges > 1:
            excess = (n_fridges - 1) * AL.FRIDGE_KWH_IDF
            print(f"  [D8 correction] {n_fridges} named fridges; subtracting "
                  f"{n_fridges - 1} x {AL.FRIDGE_KWH_IDF:.1f} = {excess:.1f} kWh excess")
            equip_kwh -= excess

    def verdict(label, got, target):
        dev = (got - target) / target if target else float('inf')
        ok = abs(dev) <= args.tol
        print(f"  {label:24s} {got:9.1f} kWh  vs target {target:9.1f}  "
              f"({dev:+6.1%})  {'PASS' if ok else 'FAIL'}")
        return ok

    print("-" * 64)
    e_ok = verdict('Equipment (incl fridge)', equip_kwh, equip_gross_target)
    l_ok = verdict('Lighting', light_kwh, light_target)

    leaks = equip_leaks + light_leaks
    if leaks:
        print(f"\n{len(leaks)} LEAK(S) -- objects E+ will count that the fix should have "
              f"neutralized/converted:")
        for n in leaks:
            print(f"  - {n}")

    ok = e_ok and l_ok and not leaks
    print("\nRESULT: " + ("PASS -- wiring sound, safe to run E+"
                          if ok else "FAIL -- fix wiring BEFORE the E+ array"))
    print()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
