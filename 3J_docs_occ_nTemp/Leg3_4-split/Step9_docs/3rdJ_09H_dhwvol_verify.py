#!/usr/bin/env python3
"""Arm H — verify that dhw_volume_hourly.csv is REAL, not a fail-soft silent nan.

Written 2026-08-03 BEFORE any arm-H cell had finished, so every threshold below is
pre-registered. Run against a downloaded cell directory:

    py -3 3rdJ_09H_dhwvol_verify.py <cell_dir> [<cell_dir> ...]

WHY THIS EXISTS
---------------
`_do_postprocess` writes dhw_volume_hourly.csv inside its own try/except, deliberately, so a new
reporting series can never take down a 56-cell campaign. The cost of that choice is that FAILURE IS
SILENT: an absent variable, a wrong variable name, or an empty join all leave the campaign looking
green. Fail-soft demands a loud external check, and this is it.

The volume series exists to be an INDEPENDENT reference for the T9-13 volume identity — independent
of `3rdJ_09E_dhw_identity_probe.py`, which derives volume by parsing the IDF with our own reader
(vacuous-gate kind #9: audited quantity and auditing reference both produced by our code). A volume
column that is silently nan would put us back there while appearing to have fixed it.

PRE-REGISTERED PREDICTIONS — what would make each one FAIL
----------------------------------------------------------
G1  file exists                     -> FAIL if the extraction raised (check manifest for the reason)
G2  8760 rows                       -> FAIL on a truncated RunPeriod or a design-day-only join
G3  all 7 dhwvol_* columns present  -> FAIL if the channel map changed shape
G4  total annual volume > 0 and finite
                                    -> FAIL on the silent-nan / empty-join mode this script exists
                                       for. THIS IS THE DISCRIMINATING CHECK.
G5  manifest carries no dhw_volume_hourly_exception, and its recorded row count agrees with the
    file actually on disk
                                    -> FAIL if postprocess swallowed an error, or if the manifest
                                       and the artefact disagree about what was written
G6  0 unresolved WaterUse:Equipment -> FAIL if an object could not be mapped to a channel (it would
                                       land in dhwvol_unassigned and quietly leave a channel short)
G7  IMPLIED DELTA-T, per channel with a non-zero draw, must land in [20, 80] K, where
        dT = E_annual / (rho * c * V_annual),  rho = 1000 kg/m3, c = 4186 J/(kg.K)
    E from dhw_hourly.csv (Water Use Equipment Heating Energy, J), V from this new file (m3).

    G7 is the reason this script is worth writing. G1-G6 only prove SOMETHING was written; G7 proves
    it is a VOLUME. The prototypes draw at 140 F (60 C) and 180 F (82 C) against mains water in the
    5-20 C range, so a genuine volume gives dT of roughly 40-70 K. The realistic failure modes all
    land far outside [20, 80]:
      * reporting the FLOW RATE (m3/s) instead of the integrated volume -> dT off by ~3600x
      * a units slip to litres                                          -> dT off by ~1000x
      * joining the wrong variable index                                -> arbitrary
    A check that merely asked "is it non-zero" would pass on every one of those.
"""
import sys
import os
import json

import numpy as np
import pandas as pd

RHO = 1000.0     # kg/m3
CP = 4186.0      # J/(kg.K)
DT_LO, DT_HI = 20.0, 80.0
EXPECTED_ROWS = 8760
CHANNELS = ["office", "retail", "hotel", "residential",
            "residential_common", "service_MEP", "unassigned"]


def verify(cell_dir):
    name = os.path.basename(cell_dir.rstrip("/\\"))
    print(f"\n{'=' * 78}\nCELL {name}\n{'=' * 78}")
    results = []

    def rec(gid, ok, msg):
        results.append((gid, bool(ok)))
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}  {msg}")

    vol_path = os.path.join(cell_dir, "dhw_volume_hourly.csv")
    eng_path = os.path.join(cell_dir, "dhw_hourly.csv")
    man_path = os.path.join(cell_dir, "manifest.json")

    # ---- G1
    if not os.path.isfile(vol_path):
        rec("G1", False, "dhw_volume_hourly.csv ABSENT -- extraction did not run or raised")
        man = json.load(open(man_path)) if os.path.isfile(man_path) else {}
        if "dhw_volume_hourly_exception" in man:
            print(f"         manifest reason: {man['dhw_volume_hourly_exception']}")
        return results
    rec("G1", True, "dhw_volume_hourly.csv present")

    vol = pd.read_csv(vol_path)

    # ---- G2
    rec("G2", len(vol) == EXPECTED_ROWS, f"{len(vol)} rows (require {EXPECTED_ROWS})")

    # ---- G3
    want = [f"dhwvol_{c}" for c in CHANNELS]
    missing = [c for c in want if c not in vol.columns]
    rec("G3", not missing, f"columns: {len(vol.columns)} present, missing={missing}")

    # ---- G4  THE DISCRIMINATING CHECK
    tot = float(np.nansum(vol[[c for c in want if c in vol.columns]].to_numpy()))
    allnan = vol[[c for c in want if c in vol.columns]].isna().all().all()
    rec("G4", (tot > 0) and np.isfinite(tot) and not allnan,
        f"total annual volume = {tot:.6g} m3  (all-nan={allnan})")

    # ---- G5
    man = json.load(open(man_path)) if os.path.isfile(man_path) else {}
    exc = man.get("dhw_volume_hourly_exception")
    rows_claimed = (man.get("dhw_volume_hourly_csv") or {}).get("rows")
    rec("G5", exc is None and rows_claimed == len(vol),
        f"manifest exception={exc!r}, manifest rows={rows_claimed} vs file rows={len(vol)}")

    # ---- G6
    unres = man.get("dhw_volume_unresolved_equipment")
    rec("G6", not unres, f"unresolved WaterUse:Equipment = {unres if unres else 0}")

    # ---- G7
    if not os.path.isfile(eng_path):
        rec("G7", False, "dhw_hourly.csv absent -- cannot form the energy/volume ratio")
        return results
    eng = pd.read_csv(eng_path)
    ok_all, lines = True, []
    for ch in CHANNELS:
        vc, ec = f"dhwvol_{ch}", f"dhw_{ch}"
        if vc not in vol.columns or ec not in eng.columns:
            continue
        V = float(np.nansum(vol[vc].to_numpy()))
        E = float(np.nansum(eng[ec].to_numpy()))
        if V <= 0 and E <= 0:
            lines.append(f"       {ch:<20} no draw (V=0, E=0) -- skipped")
            continue
        if V <= 0:
            ok_all = False
            lines.append(f"       {ch:<20} E={E:.4g} J but V=0 -- energy without water")
            continue
        dT = E / (RHO * CP * V)
        good = DT_LO <= dT <= DT_HI
        ok_all &= good
        lines.append(f"       {ch:<20} V={V:11.4g} m3  E={E:11.4g} J  implied dT={dT:8.2f} K"
                     f"  {'ok' if good else '<-- OUT OF BAND'}")
    rec("G7", ok_all, f"implied delta-T within [{DT_LO}, {DT_HI}] K for every drawing channel")
    for ln in lines:
        print(ln)

    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    allr = []
    for d in sys.argv[1:]:
        allr += verify(d)
    npass = sum(1 for _, ok in allr if ok)
    nfail = len(allr) - npass
    print(f"\n{'=' * 78}\nARM H DHW-VOLUME VERIFY: {npass} PASS / {nfail} FAIL\n{'=' * 78}")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
