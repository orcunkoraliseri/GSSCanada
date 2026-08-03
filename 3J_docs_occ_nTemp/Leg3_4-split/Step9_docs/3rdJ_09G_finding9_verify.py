"""FINDING 9 -- local verification. Injects, does NOT simulate.

The fix's claim is testable without EnergyPlus: at r = 1.000 (hotel/office/retail in the Y2022
cell) the rebuilt DHW schedule must reproduce the prototype's calendar-weighted annual mean
EXACTLY, on every day type. Before the fix the same measurement gave RetailStandalone 0.9234,
OfficeLarge 0.9524, HotelLarge BLDG 0.9953 -- and those numbers matched the simulated energy to
three decimals (jobs 1171438 / 1171445), so reproducing 1.0000 here is the same evidence one step
earlier and about 40 minutes cheaper.

It injects two cells with the SAME call the campaign driver makes -- `inject_mixed_use(...,
preserve_load_standby_floor=..., lighting_model=..., dhw_model=...)`, models resolved by the same
strings -- so this cannot pass by exercising a different code path than the campaign will.

Then it reports, per WaterUse:Equipment object:
    predicted = annual mean(rebuilt Schedule:Compact) / annual mean(source Schedule:Year)
using the same reader as `3rdJ_09F_daytype_loss.py`, and the T9-13 audit's own D8 verdict.

Usage (locally):  py -3 3rdJ_09G_finding9_verify.py [--outdir DIR]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
STEP8 = os.path.join(os.path.dirname(HERE), "Step8_docs")
sys.path.insert(0, REPO)

CELL_TAGS = ("Y2022__Tall__MTL", "Default_NECB__Tall__MTL")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def falsify(mod, cell, meta, out, models):
    """Re-create the OLD writer on the REAL tower and require D9 to catch it.

    A gate seen only passing is not evidence. FINDING 9 lived in the WRITE path: the scaler handed
    back one weekend profile and `_build_compact_fields_2dt` stamped it onto
    "For: Weekends Holidays AllOtherDays". Stripping `new_by_daytype` from the scaler's return
    puts the code back on exactly that path -- the documented fallback branch, which is the pre-fix
    behaviour byte for byte -- while leaving the reader correct.

    A first attempt patched the READER instead (Saturday := Sunday). Both D8 and D9 stayed at 0,
    because that corrupts the reference and the target together. Recorded rather than discarded:
    it marks the real boundary of these two gates. Neither can catch a defect in
    `_schedule_daytype_profiles` itself; the independent check for that is
    `3rdJ_09F_daytype_loss.py`, which parses the IDF with its own parser and is run above.

    PRE-REGISTERED, written before running: D9 must fire on exactly the objects whose prototype has
    Saturday != Sunday -- RetailStandalone BLDG_SWH_SCH (2), OfficeLarge BLDG_SWH_SCH (2) and
    HotelLarge BLDG_SWH_SCH (2: the booster and the kitchen) = 6 -- and NOT on the 12 guest rooms,
    the 2 laundries or the 27 apartments, whose prototypes have Saturday == Sunday.
    """
    orig = mod.apply_dhw_volume_scaling

    def patched(*a, **kw):
        new_wd, new_we, info = orig(*a, **kw)
        if isinstance(info, dict):
            info = {k: val for k, val in info.items() if k != "new_by_daytype"}
        return new_wd, new_we, info          # the pre-fix return -> the 2-day-type writer

    mod.apply_dhw_volume_scaling = patched
    try:
        res = mod.inject_mixed_use(cell["idf"], out, cell["channels"], meta, verbose=False,
                                   preserve_load_standby_floor=True, **models)
    finally:
        mod.apply_dhw_volume_scaling = orig
    assert mod.apply_dhw_volume_scaling is orig, "scaler not restored"
    print(f"  fallback path taken by {len(res.get('t9_13_daytype_fallback') or [])} schedules "
          f"(this is the pre-fix writer, and it is reported, not silent)")

    aud = res.get("t9_13_audit") or {}
    hits = sorted({x["obj"] for x in aud.get("violations", []) if x["check"] == "D9"})
    n_d8 = aud.get("counts", {}).get("D8")
    print(f"\n{'=' * 70}\n[FALSIFY] D9 against the FINDING 9 signature on the real tower\n{'=' * 70}")
    print(f"  verdict={aud.get('verdict')}  D9 violations={aud.get('counts', {}).get('D9')}  "
          f"objects flagged={len(hits)}")
    print(f"  D8 violations={n_d8}  <- RECORDED: D8 cannot see a READER defect, because the "
          f"corrupted Saturday is both its reference and its target. That is why D9 reads the "
          f"saved IDF instead, and why D8 is not credited with catching FINDING 9.")
    for h in hits:
        print(f"      {h}")
    ok = (len(hits) == 6
          and all(("RETAIL" in h.upper() or "OFFICE_RESTROOM" in h.upper()
                   or "BOOSTER" in h.upper() or "KITCHEN" in h.upper()) for h in hits))
    print(f"  PRE-REGISTERED: 6 objects, retail x2 + office restroom x2 + booster + kitchen "
          f"-> {'PASS' if ok else 'FAIL'}")
    print(f"  and the untouched prototypes stayed clean: "
          f"{'yes' if not any('GUESTRM' in h.upper() or 'LAUNDRY' in h.upper() or 'APARTMENT' in h.upper() for h in hits) else 'NO'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(HERE, "outputs_step9", "finding9_verify"))
    ap.add_argument("--falsify", action="store_true",
                    help="also re-create the old collapse and require D8 to catch it")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    from eSim_bem_utils.commercial_integration import (
        inject_mixed_use, DHW_MODEL_VOLUME_SCALED, LIGHTING_MODEL_CALIBRATED_V2)
    cells_mod = _load(os.path.join(STEP8, "3rdJ_08D_campaign_cells.py"), "camp_cells")
    dt = _load(os.path.join(HERE, "3rdJ_09F_daytype_loss.py"), "daytype_loss")

    cells = cells_mod.build_campaign_cells(repo_root=REPO)
    by_tag = {c["tag"]: c for c in cells}

    paths = {}
    for tag in CELL_TAGS:
        cell = by_tag.get(tag)
        if cell is None:
            raise SystemExit(f"cell {tag} not found; have {sorted(by_tag)[:6]}...")
        out = os.path.join(a.outdir, tag)
        os.makedirs(out, exist_ok=True)
        idf_out = os.path.join(out, "injected.idf")
        meta = {"building": cell.get("building"), "city": cell.get("city"),
                "cz": cell.get("cz"), "purpose": "finding9_verify", "scenario_label": tag}
        print(f"\n{'=' * 70}\n[inject] {tag}\n{'=' * 70}")
        res = inject_mixed_use(cell["idf"], idf_out, cell["channels"], meta, verbose=True,
                               preserve_load_standby_floor=True,
                               lighting_model=dict(LIGHTING_MODEL_CALIBRATED_V2),
                               dhw_model=dict(DHW_MODEL_VOLUME_SCALED))
        paths[tag] = idf_out
        aud = res.get("t9_13_audit") or {}
        print(f"  audit verdict={aud.get('verdict')} n={aud.get('n')} counts={aud.get('counts')}")
        print(f"  d8_unchecked={aud.get('d8_unchecked')}")
        print(f"  daytype fallback (should be empty): {res.get('t9_13_daytype_fallback')}")
        names = sorted(set(res.get("modulated_schedule_names", [])
                           + res.get("schedule_names", [])))
        dhwv2 = [n for n in names if "_DHWv2_" in n]
        print(f"  DHWv2 schedules: {len(dhwv2)}")
        for n in [x for x in dhwv2 if "_HH" not in x]:
            print(f"      {n}")

    print(f"\n{'=' * 70}\n[FINDING 9] predicted annual-mean ratio, schedules only\n{'=' * 70}")
    sys.argv = ["daytype_loss", paths[CELL_TAGS[0]], paths[CELL_TAGS[1]]]
    dt.main()

    if a.falsify:
        import eSim_bem_utils.commercial_integration as ci
        cell = by_tag[CELL_TAGS[0]]
        meta = {"building": cell.get("building"), "city": cell.get("city"),
                "cz": cell.get("cz"), "purpose": "finding9_falsify",
                "scenario_label": CELL_TAGS[0]}
        ok = falsify(ci, cell, meta,
                     os.path.join(a.outdir, "falsify_injected.idf"),
                     {"lighting_model": dict(LIGHTING_MODEL_CALIBRATED_V2),
                      "dhw_model": dict(DHW_MODEL_VOLUME_SCALED)})
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
