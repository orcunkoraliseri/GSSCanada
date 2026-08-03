"""FINDING 8 fix -- smoke test scorer. `Y2022__Tall__MTL` vs `Default_NECB__Tall__MTL`.

`Y2022` IS the T9-13 reference, so r = 1.000 for every channel and a correct T9-13 must be a
NO-OP on DHW. Every prediction below is transcribed from the Progress Log's pre-registered table
(2026-08-02 evening) BEFORE the fixed injector was run. They are constants in this file on purpose:
a miss is recorded, never repaired.

    object                                   arm E (broken)      required after fix
    LAUNDRY SERVICE WATER USE                2.7598e+12 J x3.028  ~9.1147e+11 J  x1.000
    F30 HOTEL_BOT_LAUNDRY SERVICE WATER USE  3.7251e+11 J x1.399  ~2.6625e+11 J  x1.000
    F31-F37 HOTEL_MID_*_GUESTRM (all 8)                   x1.136                 x1.000
    F38 HOTEL_TOP_KITCHEN                                 x0.998                 x1.000
    BOOSTER SERVICE WATER USE                             x0.995                 x1.000
    D7                                       did not exist        PASS, 0 violations

THE GUEST ROOMS ARE THE DISCRIMINATING CASE. Their x1.136 was recorded in the log as "the
legitimate r effect" -- but at r = 1.000 there is no legitimate r effect to have. If they do not
return to x1.000, the cache collision was not the whole mechanism, the correction is INCOMPLETE,
and this script says so instead of passing.

Usage:  python 3rdJ_09F_smoke_f8fix.py <injected_cell_dir> <necb_cell_dir>
"""
from __future__ import annotations

import os
import re
import sqlite3
import sys

# x1.000 means x1.000. The tolerance is for E+ reporting/rounding, not for a residual effect:
# a 1.136 ratio is 136x this band, so nothing that matters can hide inside it.
TOL_NOOP = 0.002

ENERGY_VAR = "WATER USE EQUIPMENT HEATING ENERGY"
VOLUME_VAR = "WATER USE EQUIPMENT TOTAL VOLUME"

# Pre-registered, from the log. The log's table abbreviates the object names (the real IDF names
# carry a flow-rate suffix, e.g. `Laundry Service Water Use 30.6gpm 180F`), so each prediction is
# matched by a PREFIX on the uppercased SQL KeyValue, and the resolved key is printed so the
# reader can confirm which object was actually scored. A prefix that matches 0 or >1 objects is a
# FAIL, not a quiet pick -- an ambiguous match would let the scorer grade the wrong object.
#   label -> (key prefix, armE_ratio, required_ratio, armE_abs_J, required_abs_J)
PREDICTED = [
    ("LAUNDRY SERVICE WATER USE",             "LAUNDRY SERVICE WATER USE",
     3.028, 1.000, 2.7598e+12, 9.1147e+11),
    ("F30 HOTEL_BOT_LAUNDRY SERVICE WATER USE", "F30 HOTEL_BOT_LAUNDRY SERVICE WATER USE",
     1.399, 1.000, 3.7251e+11, 2.6625e+11),
    ("F38 HOTEL_TOP_KITCHEN",                 "F38 HOTEL_TOP_KITCHEN",
     0.998, 1.000, None, None),
    ("BOOSTER SERVICE WATER USE",             "BOOSTER SERVICE WATER USE",
     0.995, 1.000, None, None),
]
GUESTROOM_RE = re.compile(r"^F31-F37\s+HOTEL_MID_.*GUESTRM", re.I)
GUESTROOM_ARME_RATIO = 1.136
GUESTROOM_N_EXPECTED = 8      # the log says "all 8"


def find_sql(d):
    for root, _dirs, files in os.walk(d):
        for n in files:
            if n.lower().endswith(".sql"):
                return os.path.join(root, n)
    return None


def per_object(path, varname):
    """{KeyValue: annual sum} for one output variable."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("SELECT ReportDataDictionaryIndex, KeyValue FROM ReportDataDictionary "
                "WHERE UPPER(Name) = ?", (varname,))
    idx = {i: (k or "").strip().upper() for i, k in cur.fetchall()}
    out = {}
    if idx:
        qs = ",".join("?" * len(idx))
        cur.execute(f"SELECT ReportDataDictionaryIndex, SUM(Value) FROM ReportData "
                    f"WHERE ReportDataDictionaryIndex IN ({qs}) "
                    f"GROUP BY ReportDataDictionaryIndex", tuple(idx))
        for i, s in cur.fetchall():
            out[idx[i]] = float(s or 0.0)
    con.close()
    return out


def provenance(cell_dir):
    p = os.path.join(cell_dir, "injected.idf.provenance.txt")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    inj_dir, ref_dir = sys.argv[1], sys.argv[2]
    inj_sql, ref_sql = find_sql(inj_dir), find_sql(ref_dir)
    if not inj_sql or not ref_sql:
        raise SystemExit(f"missing .sql (injected={inj_sql} necb={ref_sql})")
    print(f"injected : {inj_sql}")
    print(f"reference: {ref_sql}\n")

    E_i, E_r = per_object(inj_sql, ENERGY_VAR), per_object(ref_sql, ENERGY_VAR)
    V_i, V_r = per_object(inj_sql, VOLUME_VAR), per_object(ref_sql, VOLUME_VAR)
    if not E_i or not E_r:
        print(f"'{ENERGY_VAR}' not reported (injected n={len(E_i)} ref n={len(E_r)}).")
        print("Variables present that mention WATER USE EQUIPMENT (listed so the next run can be "
              "keyed correctly; NOT substituted automatically):")
        con = sqlite3.connect(f"file:{inj_sql}?mode=ro", uri=True)
        for n, k in con.execute("SELECT DISTINCT Name, KeyValue FROM ReportDataDictionary "
                                "WHERE UPPER(Name) LIKE '%WATER USE EQUIPMENT%' LIMIT 40"):
            print(f"    {n} | {k}")
        con.close()
        raise SystemExit("cannot score, and will not substitute a different variable")

    print(f"WaterUse:Equipment objects reporting '{ENERGY_VAR}': "
          f"injected={len(E_i)} reference={len(E_r)}\n")

    n_pass = n_fail = 0
    print("=== PRE-REGISTERED OBJECTS ===")
    print(f"  {'object (resolved SQL key)':<52}{'necb J':>13}{'injected J':>13}{'ratio':>9}"
          f"{'armE':>8}{'req':>7}  verdict")
    matched = set()
    for label, pref, arm_e, req, arm_e_abs, req_abs in PREDICTED:
        p = pref.upper()
        cands = sorted(k for k in E_i if k.startswith(p))
        if len(cands) != 1:
            print(f"  {label:<52}{'--':>13}{'--':>13}{'--':>9}{arm_e:>8.3f}{req:>7.3f}  "
                  f"FAIL (prefix matched {len(cands)} objects: {cands[:4]})")
            n_fail += 1
            continue
        k = cands[0]
        matched.add(k)
        if k not in E_r:
            print(f"  {k:<52}{'--':>13}{E_i[k]:>13.4e}{'--':>9}{arm_e:>8.3f}{req:>7.3f}  "
                  f"FAIL (absent from the reference cell)")
            n_fail += 1
            continue
        r = E_i[k] / E_r[k] if E_r[k] else float("nan")
        ok = abs(r - req) <= TOL_NOOP
        n_pass, n_fail = (n_pass + 1, n_fail) if ok else (n_pass, n_fail + 1)
        print(f"  {k:<52}{E_r[k]:>13.4e}{E_i[k]:>13.4e}{r:>9.3f}"
              f"{arm_e:>8.3f}{req:>7.3f}  {'PASS' if ok else 'FAIL'}")
        if arm_e_abs is not None:
            print(f"      absolute: log records arm E {arm_e_abs:.4e} J, requires "
                  f"~{req_abs:.4e} J after the fix; measured {E_i[k]:.4e} J")

    print("\n=== THE DISCRIMINATING CASE: F31-F37 guest rooms (arm E x1.136, required x1.000) ===")
    gr = sorted(k for k in E_i if GUESTROOM_RE.search(k))
    if len(gr) != GUESTROOM_N_EXPECTED:
        print(f"  FAIL: found {len(gr)} F31-F37 *GUESTRM objects, the log's prediction covers "
              f"{GUESTROOM_N_EXPECTED}. The discriminating case cannot be evaluated as written, "
              f"so this smoke test would be VACUOUS. Reporting FAIL, not a pass.")
        print(f"  keys found: {gr}")
        n_fail += 1
    if gr:
        worst = 0.0
        for k in gr:
            r = E_i[k] / E_r[k] if E_r.get(k) else float("nan")
            ok = abs(r - 1.000) <= TOL_NOOP
            worst = max(worst, abs(r - 1.000))
            n_pass, n_fail = (n_pass + 1, n_fail) if ok else (n_pass, n_fail + 1)
            print(f"  {k:<44}{E_r.get(k, 0):>13.4e}{E_i[k]:>13.4e}{r:>9.3f}"
                  f"{GUESTROOM_ARME_RATIO:>8.3f}{1.000:>7.3f}  {'PASS' if ok else 'FAIL'}")
        print(f"  n={len(gr)} guest-room objects, worst |ratio - 1| = {worst:.4f}")
        if worst > TOL_NOOP:
            print("  🔴 THE CACHE COLLISION WAS NOT THE WHOLE MECHANISM. The correction is "
                  "INCOMPLETE -- do not proceed to the campaign on this result.")

    others = sorted(set(E_i) - matched - set(gr))
    # Residential must be split out and NOT scored against the no-op requirement. Its `r` is per
    # HOUSEHOLD against the prototype household occupancy, not per channel against a Y2022
    # channel reference, so r != 1 at Y2022 is the designed behaviour (the log records the volume
    # identity at 0.9647). Grading it as an off-no-op would manufacture 27 fake failures and bury
    # the ones that mean something.
    resid = [k for k in others if ("RESI_" in k or "APARTMENT" in k)]
    comm = [k for k in others if k not in resid]

    print("\n=== EVERY OTHER COMMERCIAL WaterUse:Equipment OBJECT (no prediction was registered; "
          "at r=1.000 a correct T9-13 is a no-op on all of them) ===")
    n_off = 0
    for k in comm:
        r = E_i[k] / E_r[k] if E_r.get(k) else float("nan")
        vr = (V_i.get(k, 0) / V_r[k]) if V_r.get(k) else float("nan")
        flag = "ok      " if abs(r - 1.0) <= TOL_NOOP else "OFF-NOOP"
        if flag != "ok      ":
            n_off += 1
            n_fail += 1
        print(f"  {flag} {k:<46}{E_r.get(k, 0):>13.4e}{E_i[k]:>13.4e}"
              f"{r:>9.3f}  (volume ratio {vr:.3f})")
    _off_note = ("clean" if n_off == 0 else
                 "FAIL -- never predicted either way, and at r=1.000 there is nothing that "
                 "legitimately moves them")
    print(f"  {len(comm)} other commercial objects, {n_off} off no-op   ({_off_note})")

    print("\n=== RESIDENTIAL (INFO, not scored) -- r is PER HOUSEHOLD here, so r != 1 at Y2022 is "
          "the designed behaviour, not a defect. The log's volume identity is 0.9647. ===")
    tot_e_i = sum(E_i[k] for k in resid)
    tot_e_r = sum(E_r.get(k, 0.0) for k in resid)
    tot_v_i = sum(V_i.get(k, 0.0) for k in resid)
    tot_v_r = sum(V_r.get(k, 0.0) for k in resid)
    print(f"  {len(resid)} objects | energy {tot_e_r:.4e} -> {tot_e_i:.4e} J  "
          f"ratio {(tot_e_i / tot_e_r if tot_e_r else float('nan')):.4f}")
    print(f"  {'':>{len(str(len(resid)))}}{'':11} volume {tot_v_r:.6e} -> {tot_v_i:.6e}  "
          f"ratio {(tot_v_i / tot_v_r if tot_v_r else float('nan')):.4f}  "
          f"(log records 0.9647 for the volume identity)")

    print("\n=== AUDIT / D7 / SCHEDULE NAMES, from the injected cell's provenance ===")
    lines = provenance(inj_dir)
    if not lines:
        print("  FAIL: no provenance file")
        n_fail += 1
    else:
        d7_seen = False
        for ln in lines:
            if ln.startswith(("t9_13_audit_pass=", "t9_13_audit_verdict=", "t9_13_d7_pass=",
                              "n_dhw_applied=", "n_dhw_excluded=", "n_dhw_unresolved=",
                              "residential_dhw_objects=")):
                print(f"  {ln}")
                if ln.startswith("t9_13_d7_pass="):
                    d7_seen = True
                    if not ln.startswith("t9_13_d7_pass=True"):
                        n_fail += 1
            if ln.startswith("t9_13_VIOLATION"):
                print(f"  {ln}")
                n_fail += 1
        if not d7_seen:
            print("  FAIL: no t9_13_d7_pass line -- this cell was produced by the PRE-FIX injector")
            n_fail += 1
        names = sorted(ln.split(" ", 1)[1] for ln in lines
                       if ln.startswith("t9_13_derived_name "))
        print(f"\n  distinct MXU_*_DHWv2_* schedules created: {len(names)}")
        per_ch = {}
        for nm in names:
            ch = nm.split("_")[1] if nm.count("_") > 1 else "?"
            per_ch.setdefault(ch, []).append(nm)
            print(f"    {nm}")
        print("\n  per channel: " + ", ".join(f"{c}={len(v)}" for c, v in sorted(per_ch.items())))
        multi = [c for c, v in per_ch.items() if len(v) > 1]
        if not multi:
            print("  🔴 exactly ONE schedule per channel -- if any channel has objects on "
                  "different prototype schedules, THE FIX DID NOT TAKE.")
        else:
            print(f"  channels with >1 schedule (the fix took): {sorted(multi)}")

    print(f"\n=== SMOKE VERDICT: {n_pass} PASS / {n_fail} FAIL ===")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
