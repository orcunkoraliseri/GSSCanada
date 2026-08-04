#!/usr/bin/env python3
"""Score the 56-cell RESIZED campaign (K = 10, all-channel) against its pre-registration.

WRITTEN BEFORE THE CAMPAIGN RAN. The gate texts here are the same ones in the header of
`resize_campaign.sh`, and both were fixed before submission. If this file and that header ever
disagree, neither is a pre-registration and the run is not scoreable -- reconcile, do not choose.

THE INTERVENTION: every `WaterHeater:Mixed` in each arm-H cell has `Heater Maximum Capacity`
multiplied by K = 10; nothing else is touched and the injection is not re-run. The user's decision
of 2026-08-04 makes this ALL-CHANNEL, so it is a new arm for residential, office, retail AND hotel,
not a hotel-side correction to arm H. Every comparison below moves four channels at once.

GATES. `C1'`, `C2'` and `C3'` are re-specifications made on 2026-08-04, before submission, each
strictly stricter than what it replaced and each with a stated failure mode. `C3'` is further SPLIT
into two separately-numbered gates because bundling a measurement clause with a reconciliation
clause under one verdict is the defect this project recorded as vacuous-gate #13.

  C1'  CONTROL  -- DHW volume unchanged from arm H (<= 0.1 %) in all four channels, all 56 cells.
                   Widened from hotel-only: the resize touches every heater, so a hotel-only
                   control could not fail for three quarters of what the intervention touches.
                   FAILS IF: any channel's draw moves. The draw is schedule-driven and cannot see
                   the burner, so movement means the edit was not surgical in that cell.
  C2'  CONTROL  -- `injected_resized.idf` differs from arm H's `injected.idf` ONLY on
                   `!- Heater Maximum Capacity` lines (exactly PLANT_N_HEATERS of them, each
                   scaled by exactly K) plus the appended `Output:Variable` block.
                   FAILS IF: any other line differs. Replaces "INJ_HASH identical + area delta 0",
                   which was unscoreable: the resized manifest is a COPY of arm H's, so comparing
                   its INJ_HASH with arm H's compares a value with itself (vacuous-gate #9), and no
                   area key exists in the manifest at all. The line diff subsumes the area claim.
  C3a  DECISIVE -- in all 56 cells, every hotel `WaterUse:Equipment` type delivers its own design
                   rise: 140F types within 0.5 K of 49.19 K, 180F within 0.5 K of 71.40 K.
                   FAILS IF: any type is short of its design rise -- that is a throttle, and the
                   plant would still be mediating the occupancy signal somewhere in the grid.
                   Replaces C3 ("hotel dT constant across all 56 cells, across geometry groups"),
                   which was false by construction: the 180F volume share is a use-mix property
                   that varies with geometry (64.57 % vs 73.34 % between the measured grid
                   extremes), so C3 would have failed every run for a non-plant reason. C3a is
                   stricter -- C3 checked one aggregate per cell and could not tell a throttle from
                   a mix difference; C3a checks every object.
  C3b  CONTROL, and it is what stops C3a resting on an unchecked table -- the per-type table C3a is
                   scored on must reconcile with the driver's own hotel channel: volume to 0.01 %
                   of `dhwvol_hotel` and energy to 0.01 % of `dhw_hotel`.
                   FAILS IF: the breakdown is not the same quantity the rest of the campaign uses.
                   NOTE, stated rather than buried: the pre-registration's other C3' clause -- "the
                   per-cell aggregate equals its own 180F/140F volume-share reconstruction within
                   0.5 K" -- is ARITHMETICALLY IMPLIED by C3a (a weighted mean of values each
                   within 0.5 K of their design rise is within 0.5 K of the weighted design mean).
                   It therefore cannot fail once C3a passes, so it is PRINTED as a derived quantity
                   and NOT SCORED. C3b is the independent check that clause was reaching for.
  C4   DECISIVE -- hotel DHW energy elasticity w.r.t. r >= 0.90 within each (geometry, city) group,
                   4/4 groups. FAILS IF: the plant still mediates occupancy anywhere in the grid.
                   The estimator is IMPORTED from `3rdJ_09H_resize_elasticity.py`, so the 0.90
                   threshold is read against the estimator it was written for.
  C4c  CONTROL, and it is what stops C4 being vacuous -- arm H's own per-group elasticity must be
                   BELOW 0.90 in every group where C4 passes. FAILS IF: a group was already at
                   >= 0.90 before the resize, in which case C4's pass in that group discriminates
                   nothing. Arm H measured 0.5582 on Tall__MTL, so this is expected to pass -- but
                   expected is not measured.
  C5   INFO     -- all-fuel site energy shift vs arm H (Electricity:Facility + NaturalGas:Facility,
                   whole tower, the Leg-2 precedent). NOT a gate: the hotel EUI band is still open
                   with the user, and floor area is unchanged by construction (C2'), so the % shift
                   IS the EUI shift.
  C6   INFO     -- per-channel resized-minus-arm-H DHW energy and volume, four channels, 56 cells.
                   Owed by the all-channel decision. Stays INFO: there is no pre-registered
                   expectation for how far residential/office/retail should move, and a number
                   scored against an expectation invented after seeing it is not a test.

Read C3a first. C4 is only meaningful if C3a holds: an elasticity of 1.0 in a group whose plant is
still binding would be a coincidence, not a clean lever.

EVERY GATE ITEMISES WHAT IT COULD NOT READ. A reader that returns 0.0 for input it cannot parse
blames the simulation for its own gap -- that cost 16 spurious FAILs in job 1171607.

    python 3rdJ_09H_resize_campaign_score.py <armH_campaign_dir> <resized_dir>
"""
import importlib.util
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.environ.get("REPO", "."))

RHO_C = 4.184e6
CHANNELS = ("residential", "office", "retail", "hotel")
OTHER_CHANNELS = ("residential_common", "service_MEP", "unassigned")

C1_TOL_PCT = 0.1
C3_TOL_K = 0.5
C3B_TOL_PCT = 0.01
C4_THRESHOLD = 0.90
# H9/H10 measurement, job 1172033: 140F types read 49.17-49.23 K and 180F types 71.34-71.43 K in
# BOTH grid extremes and BOTH cities. These are the design rises the plant is supposed to deliver,
# not a tolerance chosen to make cells pass.
DESIGN_RISE_K = {140.0: 49.19, 180.0: 71.40}

FUEL_TOTALS = ["Electricity:Facility", "NaturalGas:Facility"]


def _load(name, relpath):
    path = os.path.join(os.environ.get("REPO", "."), relpath)
    if not os.path.isfile(path):
        raise SystemExit("REFUSING: cannot find %s at %s" % (name, path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _csv_sum(path, col):
    """Annual sum of one column, or None if the file/column is not there. Never 0.0 for absent."""
    if not os.path.isfile(path):
        return None
    df = pd.read_csv(path)
    return float(df[col].sum()) if col in df.columns else None


def _idf_diff(src, dst, K, n_heaters):
    """(ok, message). Only Heater Maximum Capacity lines and the appended block may differ."""
    a = open(src, errors="replace").read().splitlines()
    b = open(dst, errors="replace").read().splitlines()
    # The resize appends an Output:Variable block; everything before it must align 1:1.
    if len(b) < len(a):
        return False, "resized IDF is SHORTER than arm H's (%d < %d lines)" % (len(b), len(a))
    tail = [l for l in b[len(a):] if l.strip()]
    bad_tail = [l for l in tail if not l.strip().lower().startswith("output:variable")]
    if bad_tail:
        return False, "appended block contains non-Output:Variable lines: %s" % bad_tail[:3]

    pat = re.compile(r"^\s*([0-9.eE+-]+),\s*!- Heater Maximum Capacity\b")
    changed, bad, scale_bad = 0, [], []
    for i, (la, lb) in enumerate(zip(a, b[:len(a)]), start=1):
        if la == lb:
            continue
        ma, mb = pat.match(la), pat.match(lb)
        if not (ma and mb):
            bad.append("line %d: %r -> %r" % (i, la.strip()[:60], lb.strip()[:60]))
            continue
        changed += 1
        old, new = float(ma.group(1)), float(mb.group(1))
        if old <= 0 or abs(new / old - K) > 1e-6:
            scale_bad.append("line %d: %.4f -> %.4f (ratio %.6f, expected %.6f)"
                             % (i, old, new, (new / old if old else float('nan')), K))
    if bad:
        return False, "%d non-heater line(s) differ: %s" % (len(bad), bad[:3])
    if scale_bad:
        return False, "%d heater line(s) not scaled by exactly K: %s" % (len(scale_bad),
                                                                        scale_bad[:3])
    if changed != n_heaters:
        return False, ("%d heater lines changed but the manifest declares PLANT_N_HEATERS = %s"
                       % (changed, n_heaters))
    return True, "%d heater lines x %.4f, %d appended Output:Variable lines" % (changed, K,
                                                                               len(tail))


def _read_cell(armh_dir, res_dir, name):
    """Everything the gates need for one cell, or a dict with `missing` itemised."""
    out = {"name": name, "missing": []}
    need = [("armh_vol", os.path.join(armh_dir, "dhw_volume_hourly.csv")),
            ("armh_eng", os.path.join(armh_dir, "dhw_hourly.csv")),
            ("armh_met", os.path.join(armh_dir, "hourly_meters.csv")),
            ("armh_idf", os.path.join(armh_dir, "injected.idf")),
            ("res_vol", os.path.join(res_dir, "dhw_volume_hourly.csv")),
            ("res_eng", os.path.join(res_dir, "dhw_hourly.csv")),
            ("res_met", os.path.join(res_dir, "hourly_meters.csv")),
            ("res_idf", os.path.join(res_dir, "injected_resized.idf")),
            ("res_types", os.path.join(res_dir, "hotel_dT_by_type.csv")),
            ("res_manifest", os.path.join(res_dir, "manifest.json"))]
    for key, path in need:
        if os.path.isfile(path):
            out[key] = path
        else:
            out["missing"].append(os.path.relpath(path, os.path.dirname(armh_dir)))
    if out["missing"]:
        return out
    with open(out["res_manifest"], encoding="utf-8") as f:
        out["manifest"] = json.load(f)
    out["types"] = pd.read_csv(out["res_types"])
    for arm, volk, engk in (("H", "armh_vol", "armh_eng"), ("R", "res_vol", "res_eng")):
        for ch in CHANNELS + OTHER_CHANNELS:
            out["V%s_%s" % (arm, ch)] = _csv_sum(out[volk], "dhwvol_" + ch)
            out["E%s_%s" % (arm, ch)] = _csv_sum(out[engk], "dhw_" + ch)
    for arm, key in (("H", "armh_met"), ("R", "res_met")):
        tot, absent = 0.0, []
        for m in FUEL_TOTALS:
            v = _csv_sum(out[key], m)
            if v is None:
                absent.append(m)
            else:
                tot += v
        out["site_" + arm] = None if absent else tot
        out["site_absent_" + arm] = absent
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: %s <armH_campaign_dir> <resized_dir>" % sys.argv[0])
    armh_root, res_root = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/")
    el = _load("resize_elasticity",
               "3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_resize_elasticity.py")

    names = sorted(d for d in os.listdir(armh_root) if os.path.isdir(os.path.join(armh_root, d)))
    print("=" * 100)
    print("RESIZED CAMPAIGN SCORECARD -- %d arm-H cells found under %s" % (len(names), armh_root))
    print("=" * 100)

    cells, incomplete = [], []
    for n in names:
        c = _read_cell(os.path.join(armh_root, n), os.path.join(res_root, n), n)
        (incomplete if c["missing"] else cells).append(c)
    if incomplete:
        print("\n  %d of %d cells are INCOMPLETE and are excluded from every gate below:"
              % (len(incomplete), len(names)))
        for c in incomplete:
            print("      %-34s missing: %s" % (c["name"], ", ".join(c["missing"][:4])))
        print("  A gate scored on a subset is not the pre-registered gate. Read the verdicts as")
        print("  provisional until the missing cells are re-run.")
    if not cells:
        raise SystemExit("REFUSING: no complete cell -- nothing below would mean anything.")

    # ---- C1' -------------------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("C1' CONTROL -- DHW volume unchanged (<= %.1f %%) in ALL FOUR channels" % C1_TOL_PCT)
    c1_bad, c1_nodraw, c1_unread = [], [], []
    for c in cells:
        for ch in CHANNELS:
            vh, vr = c["VH_" + ch], c["VR_" + ch]
            if vh is None or vr is None:
                c1_unread.append("%s/%s" % (c["name"], ch))
            elif vh == 0 and vr == 0:
                c1_nodraw.append("%s/%s" % (c["name"], ch))
            elif vh == 0:
                c1_bad.append((c["name"], ch, float("inf")))
            else:
                d = 100.0 * (vr / vh - 1.0)
                if abs(d) > C1_TOL_PCT:
                    c1_bad.append((c["name"], ch, d))
    c1 = not c1_bad and not c1_unread
    for n, ch, d in c1_bad[:12]:
        print("      [XX] %-34s %-12s %+.4f %%" % (n, ch, d))
    if c1_unread:
        print("      [??] %d channel(s) could not be read: %s" % (len(c1_unread), c1_unread[:6]))
    if c1_nodraw:
        print("      [--] %d channel(s) have NO DRAW in either arm (not counted as agreement): %s"
              % (len(c1_nodraw), sorted(set(x.split("/")[1] for x in c1_nodraw))))
    print("  [%s] C1' -- %d cells x 4 channels, %d violation(s), %d unreadable"
          % ("PASS" if c1 else "FAIL", len(cells), len(c1_bad), len(c1_unread)))

    # ---- C2' -------------------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("C2' CONTROL -- resized IDF differs from arm H's ONLY on Heater Maximum Capacity lines")
    c2_bad = []
    for c in cells:
        K = c["manifest"].get("RESIZE_K")
        n_h = c["manifest"].get("PLANT_N_HEATERS")
        if K is None or n_h is None:
            c2_bad.append((c["name"], "manifest lacks RESIZE_K / PLANT_N_HEATERS"))
            continue
        ok, msg = _idf_diff(c["armh_idf"], c["res_idf"], float(K), int(n_h))
        if not ok:
            c2_bad.append((c["name"], msg))
    for n, m in c2_bad[:8]:
        print("      [XX] %-34s %s" % (n, m))
    print("  [%s] C2' -- %d cells checked, %d violation(s)"
          % ("PASS" if not c2_bad else "FAIL", len(cells), len(c2_bad)))

    # ---- C3a / C3b -------------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("C3a DECISIVE -- every hotel use-type delivers its design rise (140F %.2f K, 180F %.2f K,"
          " tol %.1f K)" % (DESIGN_RISE_K[140.0], DESIGN_RISE_K[180.0], C3_TOL_K))
    c3a_bad, c3a_unknown, c3b_bad, recon_worst = [], [], [], (0.0, None)
    for c in cells:
        t = c["types"]
        num = den = 0.0
        for row in t.itertuples():
            # 'MIXED' (one collapsed type carrying two design targets) and a blank both land here
            # and are itemised, never coerced to a number that would then be silently scored.
            try:
                f = None if pd.isna(row.design_F) else float(row.design_F)
            except (TypeError, ValueError):
                f = None
            if f not in DESIGN_RISE_K:
                c3a_unknown.append("%s/%s (design_F=%r)" % (c["name"], row.type, row.design_F))
                continue
            d = float(row.dT_K) - DESIGN_RISE_K[f]
            if abs(d) > C3_TOL_K:
                c3a_bad.append((c["name"], row.type, f, float(row.dT_K), d))
            num += DESIGN_RISE_K[f] * float(row.volume_m3)
            den += float(row.volume_m3)
        Vt = float(t["volume_m3"].sum())
        Et = float(t["energy_J"].sum())
        agg = (Et / Vt) / RHO_C if Vt else float("nan")
        if den:
            gap = abs(num / den - agg)
            if gap > recon_worst[0]:
                recon_worst = (gap, c["name"])
        for label, mine, ref in (("volume", Vt, c["VR_hotel"]), ("energy", Et, c["ER_hotel"])):
            if ref is None:
                c3b_bad.append((c["name"], "driver %s column unreadable" % label))
            elif ref == 0:
                c3b_bad.append((c["name"], "driver %s is zero" % label))
            else:
                dd = 100.0 * abs(mine - ref) / ref
                if dd > C3B_TOL_PCT:
                    c3b_bad.append((c["name"], "%s off by %.5f %% (table %.4f vs driver %.4f)"
                                    % (label, dd, mine, ref)))
    for n, t, f, dt, d in c3a_bad[:12]:
        print("      [XX] %-34s %-22s %.0fF  measured %6.2f K  (%+.2f K)" % (n, t, f, dt, d))
    if c3a_unknown:
        print("      [??] %d type(s) carry no readable design F and are NOT defaulted: %s"
              % (len(c3a_unknown), c3a_unknown[:5]))
    c3a = not c3a_bad and not c3a_unknown
    print("  [%s] C3a -- %d cells, %d type violation(s), %d unreadable design targets"
          % ("PASS" if c3a else "FAIL", len(cells), len(c3a_bad), len(c3a_unknown)))
    print("      derived, NOT scored (implied by C3a): worst |aggregate - mix reconstruction| = "
          "%.4f K on %s" % (recon_worst[0], recon_worst[1]))

    for n, m in c3b_bad[:8]:
        print("      [XX] %-34s %s" % (n, m))
    print("  [%s] C3b CONTROL -- per-type table reconciles with the driver's hotel channel "
          "(<= %.2f %%), %d violation(s)"
          % ("PASS" if not c3b_bad else "FAIL", C3B_TOL_PCT, len(c3b_bad)))

    # ---- C4 / C4c --------------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("C4 DECISIVE -- hotel DHW energy elasticity >= %.2f in each (geometry, city) group"
          % C4_THRESHOLD)
    groups = {}
    for c in cells:
        m = c["manifest"]
        key = (m.get("building", "?"), m.get("city", "?"))
        r = el.hotel_r(os.path.join(armh_root, c["name"]))
        groups.setdefault(key, []).append((r, c["EH_hotel"], c["ER_hotel"], c["name"]))
    c4_fail, c4c_fail, c4_undef = [], [], []
    print("      %-22s %5s %10s %10s   %s" % ("group", "n", "armH e", "resized e", "R2"))
    for key in sorted(groups):
        pts = groups[key]
        rs = [p[0] for p in pts]
        if len(set(rs)) < 2 or any(p[1] is None or p[2] is None for p in pts):
            c4_undef.append("%s__%s" % key)
            print("      %-22s %5d   UNDEFINED (r constant or hotel series unreadable)"
                  % ("%s__%s" % key, len(pts)))
            continue
        eH, _ = el.elasticity(rs, [p[1] for p in pts])
        eR, r2R = el.elasticity(rs, [p[2] for p in pts])
        ok = eR >= C4_THRESHOLD
        if not ok:
            c4_fail.append("%s__%s (%.4f)" % (key + (eR,)))
        if ok and eH >= C4_THRESHOLD:
            c4c_fail.append("%s__%s (armH %.4f)" % (key + (eH,)))
        print("      %-22s %5d %10.4f %10.4f   %.3f  %s"
              % ("%s__%s" % key, len(pts), eH, eR, r2R, "ok" if ok else "XX"))
    c4 = not c4_fail and not c4_undef
    print("  [%s] C4  -- %d group(s), %d below threshold, %d undefined"
          % ("PASS" if c4 else "FAIL", len(groups), len(c4_fail), len(c4_undef)))
    print("  [%s] C4c CONTROL -- no group passes C4 that was already >= %.2f in arm H%s"
          % ("PASS" if not c4c_fail else "FAIL", C4_THRESHOLD,
             ": " + ", ".join(c4c_fail) if c4c_fail else ""))

    # ---- C5 INFO ---------------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("C5 INFO -- all-fuel site energy shift vs arm H (whole tower). NOT a gate.")
    shifts, c5_unread = [], []
    for c in cells:
        if c["site_H"] is None or c["site_R"] is None or not c["site_H"]:
            c5_unread.append("%s (%s)" % (c["name"], c["site_absent_H"] + c["site_absent_R"]))
            continue
        shifts.append((100.0 * (c["site_R"] / c["site_H"] - 1.0), c["name"]))
    if shifts:
        shifts.sort()
        print("      min %+.2f %% (%s)   median %+.2f %%   max %+.2f %% (%s)"
              % (shifts[0][0], shifts[0][1], shifts[len(shifts) // 2][0],
                 shifts[-1][0], shifts[-1][1]))
    if c5_unread:
        print("      [??] %d cell(s) unreadable: %s" % (len(c5_unread), c5_unread[:4]))

    # ---- C6 INFO ---------------------------------------------------------------------------
    print("\n" + "-" * 100)
    print("C6 INFO -- per-channel resized minus arm H, DHW energy and volume. NOT a gate, and it")
    print("           must not become one: no expectation for the non-hotel channels was")
    print("           pre-registered, so these numbers are measured, not scored.")
    print("      %-20s %12s %12s %12s   %12s" % ("channel", "dE min %", "dE med %", "dE max %",
                                                 "dV max %"))
    for ch in CHANNELS:
        de = sorted(100.0 * (c["ER_" + ch] / c["EH_" + ch] - 1.0) for c in cells
                    if c["EH_" + ch] and c["ER_" + ch] is not None)
        dv = sorted(abs(100.0 * (c["VR_" + ch] / c["VH_" + ch] - 1.0)) for c in cells
                    if c["VH_" + ch] and c["VR_" + ch] is not None)
        if not de:
            print("      %-20s   no cell had a readable non-zero arm-H energy series" % ch)
            continue
        print("      %-20s %12.2f %12.2f %12.2f   %12.4f"
              % (ch, de[0], de[len(de) // 2], de[-1], dv[-1] if dv else float("nan")))
    csv_out = os.path.join(res_root, "C6_per_channel_delta.csv")
    rows = []
    for c in cells:
        row = {"cell": c["name"]}
        for ch in CHANNELS:
            row["E_H_" + ch], row["E_R_" + ch] = c["EH_" + ch], c["ER_" + ch]
            row["V_H_" + ch], row["V_R_" + ch] = c["VH_" + ch], c["VR_" + ch]
        row["site_H_J"], row["site_R_J"] = c["site_H"], c["site_R"]
        rows.append(row)
    pd.DataFrame(rows).to_csv(csv_out, index=False)
    print("      full table -> %s" % csv_out)

    # ---- summary ---------------------------------------------------------------------------
    verdicts = [("C1'", c1), ("C2'", not c2_bad), ("C3a", c3a), ("C3b", not c3b_bad),
                ("C4", c4), ("C4c", not c4c_fail)]
    print("\n" + "=" * 100)
    print("  SCORECARD  " + "   ".join("%s %s" % (k, "PASS" if v else "FAIL") for k, v in verdicts))
    print("  cells scored %d / %d%s" % (len(cells), len(names),
                                        "  (INCOMPLETE -- see above)" if incomplete else ""))
    print("=" * 100)
    if not c3a:
        print("  >>> C3a FAILED: an object is short of its design rise, so the plant is still")
        print("      binding somewhere. C4 below it is not readable as a clean occupancy lever.")
        print("      Do NOT widen the tolerance -- re-specify or record the FAIL.")
    sys.exit(0)


if __name__ == "__main__":
    main()
