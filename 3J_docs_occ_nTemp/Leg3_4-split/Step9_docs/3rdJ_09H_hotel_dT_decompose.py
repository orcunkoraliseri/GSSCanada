#!/usr/bin/env python3
"""Why is the grid-max hotel ceiling 63.55 K when every other cell's is 65.50 K?

CONTEXT. H7/H8 established that the gap is NOT burner capacity: across K = 10, 20, 40 the grid-max
cell's hotel delivered rise is flat to 0.01 K while installed capacity goes up 4x. So either 63.55 K
IS that cell's unconstrained ceiling, or something non-capacity is throttling it.

`implied dT` is `E / (V*rho*c)` summed over the hotel channel -- a VOLUME-WEIGHTED AVERAGE of the
per-object rises. Two mechanisms produce a lower average and they have opposite consequences:

  (A) MIX.       Every object delivers its own full rise, but the grid-max cell carries more volume
                 in low-target uses (laundry, booster) and less in high-target ones. Then 63.55 K is
                 correct, there is no defect, and it is `C3` -- "hotel dT constant across all 56
                 cells" -- that is mis-specified, because a cross-geometry constant never existed.
  (B) THROTTLE.  Some object is individually short of its own target. Then a real constraint remains
                 (tank volume, use-side effectiveness, plant-loop flow) and the campaign stays
                 blocked until it is found.

These are distinguished by DECOMPOSITION, not by argument, and it takes two gates because either one
alone can be satisfied by the wrong mechanism.

PRE-REGISTERED, written before running:

  H9   PARTS      -- for every hotel WaterUse:Equipment TYPE present in both cells, the per-object
                     implied dT agrees between grid-max (K=40) and grid-min (K=20) within 0.5 K.
                     This is mechanism (A)'s necessary condition: no object is throttled.
  H10  WHOLE, and it is what stops H9 being vacuous -- take the grid-MIN cell's per-type dT values
                     and re-weight them by the grid-MAX cell's volume shares. That reconstruction
                     must land within 0.5 K of the grid-max cell's measured 63.55 K. H9 can pass
                     while H10 fails: if the types agree but the mix arithmetic does NOT reproduce
                     the 1.95 K gap, then the gap is coming from somewhere neither gate has looked,
                     and (A) is refuted despite matching parts. Only H9 AND H10 together license (A).
  H11  CONTROL    -- this script's own hotel-channel volume total must reproduce the driver's
                     `_write_dhw_hourly_csv` hotel column to within 0.01 % in both cells.

WHY H11 EXISTS. The channel-resolution rules below are a SECOND COPY of the two rules inside
`_write_dhw_hourly_csv` (driver lines 741-749); the driver builds that map as a local, so it cannot
be imported without refactoring a file the closed arm-H deliverable depends on. A second copy is a
second source of truth for the exact quantity the verdict rests on -- so it is made to check itself
against the original and REFUSE on disagreement, rather than print a plausible wrong breakdown. The
primitives (`_FINE_TO_AGG`, `_get_space_tag2`, `classify_tag2`, the variable names) are imported, not
retyped, so only the 8-line loop is duplicated.

    python 3rdJ_09H_hotel_dT_decompose.py <label>=<cell_dir>[:<idf_name>] ...
"""
import importlib.util
import os
import re
import sqlite3
import sys

import pandas as pd

sys.path.insert(0, os.environ.get("REPO", "."))

RHO_C = 4.184e6
TOL_PARTS_K = 0.5
TOL_WHOLE_K = 0.5
TOL_VOLUME_PCT = 0.01


def _load_driver():
    repo = os.environ.get("REPO", ".")
    path = os.path.join(repo, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs",
                        "3rdJ_08P_probe_driver.py")
    if not os.path.isfile(path):
        raise SystemExit("REFUSING: driver not found at %s" % path)
    spec = importlib.util.spec_from_file_location("probe_driver", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hotel_equipment(idf_path, idd, drv):
    """{EQUIPMENT NAME (upper): channel} restricted to hotel, by the driver's own two rules."""
    from eppy.modeleditor import IDF
    from eSim_bem_utils.commercial_integration import classify_tag2
    IDF.setiddname(idd)
    idf = IDF(idf_path)

    space_to_channel = {}
    for sp in idf.idfobjects.get("SPACE", []):
        agg = drv._FINE_TO_AGG.get(classify_tag2(drv._get_space_tag2(sp)))
        if agg:
            space_to_channel[str(sp.Name).strip().upper()] = agg
    SCHED_TOKEN = (("HOTELLARGE", "hotel"), ("OFFICELARGE", "office"),
                   ("RETAILSTANDALONE", "retail"), ("MIDRISEAPARTMENT", "residential"),
                   ("HIGHRISEAPARTMENT", "residential"))

    hotel, meta = {}, {}
    for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", []):
        key = str(we.Name).strip().upper()
        head = key.split(" SERVICE WATER USE")[0].strip()
        ch = space_to_channel.get(head)
        if ch is None:
            sched = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "").upper()
            ch = next((c for tok, c in SCHED_TOKEN if tok in sched), None)
        if ch == "hotel":
            hotel[key] = ch
            meta[key] = dict(
                target=str(getattr(we, "Target_Temperature_Schedule_Name", "") or ""),
                supply=str(getattr(we, "Hot_Water_Supply_Temperature_Schedule_Name", "") or ""),
                sched=str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or ""),
                peak=getattr(we, "Peak_Flow_Rate", None))
    if not hotel:
        raise SystemExit("REFUSING: no hotel WaterUse:Equipment resolved in %s" % idf_path)
    return hotel, meta


def per_object(sql_path, variable):
    """{KeyValue upper: annual sum} for one hourly output variable over the RunPeriod."""
    conn = sqlite3.connect(sql_path)
    try:
        meta = pd.read_sql_query(
            "SELECT ReportDataDictionaryIndex, KeyValue FROM ReportDataDictionary "
            "WHERE (ReportingFrequency = 'Hourly' OR ReportingFrequency = 3) AND Name = ?",
            conn, params=[variable])
        if meta.empty:
            raise SystemExit("REFUSING: no Hourly '%s' in %s" % (variable, sql_path))
        idx = meta["ReportDataDictionaryIndex"].tolist()
        ph = ",".join("?" * len(idx))
        data = pd.read_sql_query(
            "SELECT rd.ReportDataDictionaryIndex AS i, SUM(rd.Value) AS v FROM ReportData rd "
            "JOIN Time tm ON rd.TimeIndex = tm.TimeIndex "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            f"WHERE ep.EnvironmentType = 3 AND rd.ReportDataDictionaryIndex IN ({ph}) "
            "GROUP BY rd.ReportDataDictionaryIndex", conn, params=idx)
    finally:
        conn.close()
    m = meta.set_index("ReportDataDictionaryIndex")["KeyValue"].str.strip().str.upper()
    return {m[r.i]: float(r.v) for r in data.itertuples()}


def _type_of(name):
    """Collapse an equipment name to a TYPE comparable across towers.

    Names are '<SpaceName> SERVICE WATER USE <x>gpm <T>F', and SpaceName encodes floor/unit, which
    differs between a 6-heater Tall and an 11-heater SuperTall. The comparable part is the trailing
    '<x>gpm <T>F' signature plus, for the plant-level units, the leading BOOSTER/LAUNDRY token.
    A type that cannot be reduced keeps its full name and will simply not match -- reported as
    'only in one cell' rather than silently merged into a neighbour.
    """
    if name.startswith("BOOSTER") or name.startswith("LAUNDRY"):
        return name.split()[0]
    m = re.search(r"([0-9.]+\s*GPM\s+[0-9.]+\s*F)\s*$", name)
    return m.group(1).replace(" ", "") if m else name


def summarise(label, cell_dir, idf_name, idd, drv):
    sql = os.path.join(cell_dir, "run", "eplusout.sql")
    idf = os.path.join(cell_dir, idf_name)
    for p in (sql, idf):
        if not os.path.isfile(p):
            raise SystemExit("REFUSING: missing %s" % p)
    hotel, meta = hotel_equipment(idf, idd, drv)
    vol = per_object(sql, drv.DHW_VOLUME_VARIABLE)
    eng = per_object(sql, drv.DHW_VARIABLE)

    rows = {}
    for key in hotel:
        V, E = vol.get(key, 0.0), eng.get(key, 0.0)
        if V <= 0:
            continue
        t = _type_of(key)
        r = rows.setdefault(t, dict(V=0.0, E=0.0, n=0, target=meta[key]["target"]))
        r["V"] += V
        r["E"] += E
        r["n"] += 1
    Vtot = sum(r["V"] for r in rows.values())
    Etot = sum(r["E"] for r in rows.values())

    print("\n%s" % ("=" * 100))
    print("%s   %s" % (label, cell_dir))
    print("%s" % ("=" * 100))
    print("  %-26s %4s %14s %8s %10s   %s" % ("TYPE", "n", "V m3", "%V", "dT K", "target sched"))
    for t, r in sorted(rows.items(), key=lambda kv: -kv[1]["V"]):
        print("  %-26s %4d %14.1f %7.2f%% %10.2f   %s"
              % (t, r["n"], r["V"], 100.0 * r["V"] / Vtot, (r["E"] / r["V"]) / RHO_C,
                 r["target"][:40]))
    print("  %-26s %4d %14.1f %7.2f%% %10.2f   <- volume-weighted"
          % ("TOTAL", sum(r["n"] for r in rows.values()), Vtot, 100.0, (Etot / Vtot) / RHO_C))
    return rows, Vtot, (Etot / Vtot) / RHO_C


def main():
    idd = os.environ["EPLUS_IDD"]
    drv = _load_driver()
    tmp = os.environ.get("TMPDIR", ".")
    specs = []
    for a in sys.argv[1:]:
        label, rest = a.split("=", 1)
        cell, idf_name = (rest.split(":", 1) + ["injected_resized.idf"])[:2]
        specs.append((label, cell, idf_name))
    if len(specs) != 2:
        raise SystemExit("usage: %s MAX=<dir>[:<idf>] MIN=<dir>[:<idf>]" % sys.argv[0])

    out = {}
    for label, cell, idf_name in specs:
        out[label] = summarise(label, cell, idf_name, idd, drv) + (cell, idf_name)

    # --- H11 CONTROL: this script's hotel volume must equal the driver's own -------------------
    print("\n" + "=" * 100)
    ok11 = True
    for label, cell, idf_name in specs:
        csv = os.path.join(tmp, "h11_%s.csv" % label)
        drv._write_dhw_hourly_csv(os.path.join(cell, "run", "eplusout.sql"),
                                  os.path.join(cell, idf_name), idd, csv,
                                  variable=drv.DHW_VOLUME_VARIABLE, col_prefix="dhwvol")
        ref = float(pd.read_csv(csv)["dhwvol_hotel"].sum())
        mine = out[label][1]
        d = 100.0 * abs(mine - ref) / ref if ref else float("inf")
        good = d <= TOL_VOLUME_PCT
        ok11 &= good
        print("  [%s] H11 %-4s driver hotel V = %.1f, this script = %.1f  (|d| = %.5f %%)"
              % ("PASS" if good else "FAIL", label, ref, mine, d))
    if not ok11:
        raise SystemExit("REFUSING: the duplicated channel map disagrees with the driver's. "
                         "Nothing below is readable -- fix the map, do not read around it.")

    MAXr, MAXv, MAXdt = out["MAX"][0], out["MAX"][1], out["MAX"][2]
    MINr, MINv, MINdt = out["MIN"][0], out["MIN"][1], out["MIN"][2]

    # --- H9 PARTS -------------------------------------------------------------------------------
    print("\n  H9 PARTS -- per-type dT, grid MAX vs grid MIN (tol %.1f K)" % TOL_PARTS_K)
    shared = sorted(set(MAXr) & set(MINr))
    only_max = sorted(set(MAXr) - set(MINr))
    only_min = sorted(set(MINr) - set(MAXr))
    ok9 = bool(shared)
    for t in shared:
        a = (MAXr[t]["E"] / MAXr[t]["V"]) / RHO_C
        b = (MINr[t]["E"] / MINr[t]["V"]) / RHO_C
        good = abs(a - b) <= TOL_PARTS_K
        ok9 &= good
        print("      [%s] %-26s MAX %6.2f K   MIN %6.2f K   d = %+6.2f K"
              % ("ok" if good else "XX", t, a, b, a - b))
    for t in only_max:
        print("      [--] %-26s only in MAX (%.1f m3, %.2f %% of its hotel volume)"
              % (t, MAXr[t]["V"], 100.0 * MAXr[t]["V"] / MAXv))
    for t in only_min:
        print("      [--] %-26s only in MIN (%.1f m3, %.2f %% of its hotel volume)"
              % (t, MINr[t]["V"], 100.0 * MINr[t]["V"] / MINv))
    if only_max or only_min:
        print("      NOTE: unshared types are NOT counted in H9 -- H10 is what tests whether they")
        print("            (and the shares) actually account for the gap.")
    print("\n  [%s] H9  PARTS -- every shared hotel use-type delivers the same rise in both cells"
          % ("PASS" if ok9 else "FAIL"))

    # --- H10 WHOLE ------------------------------------------------------------------------------
    # Rebuild the MAX cell's average from the MIN cell's per-type rises and the MAX cell's shares.
    # Types absent from MIN keep their own MAX rise -- otherwise they would be silently dropped and
    # the reconstruction would be evaluated on a subset of the volume it claims to explain.
    recon_num, recon_den, borrowed = 0.0, 0.0, 0.0
    for t, r in MAXr.items():
        if t in MINr:
            dt = (MINr[t]["E"] / MINr[t]["V"]) / RHO_C
        else:
            dt = (r["E"] / r["V"]) / RHO_C
            borrowed += r["V"]
        recon_num += dt * r["V"]
        recon_den += r["V"]
    recon = recon_num / recon_den
    ok10 = abs(recon - MAXdt) <= TOL_WHOLE_K
    print("\n  [%s] H10 WHOLE -- MIN's per-type rises re-weighted by MAX's volume shares = %.2f K, "
          "measured MAX = %.2f K (|d| = %.2f K, tol %.1f)"
          % ("PASS" if ok10 else "FAIL", recon, MAXdt, abs(recon - MAXdt), TOL_WHOLE_K))
    if borrowed:
        print("      %.1f m3 (%.2f %%) of MAX volume had no MIN counterpart and used its own rise; "
              "that share cannot be evidence for the mix explanation."
              % (borrowed, 100.0 * borrowed / recon_den))

    print("\n  measured:  MAX %.2f K   MIN %.2f K   gap %+.2f K" % (MAXdt, MINdt, MAXdt - MINdt))
    print("\n  VERDICT INPUTS -- H9 %s, H10 %s. Mechanism (A) MIX requires BOTH."
          % ("PASS" if ok9 else "FAIL", "PASS" if ok10 else "FAIL"))
    if not (ok9 and ok10):
        print("  >>> Mechanism (A) is NOT established. Do not re-specify C3 on a mix story.")


if __name__ == "__main__":
    main()
