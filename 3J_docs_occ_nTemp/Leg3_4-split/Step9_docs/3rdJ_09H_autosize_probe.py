#!/usr/bin/env python3
"""Does autosizing the six `WaterHeater:Mixed` actually relieve the DHW plant? One cell answers it.

Arm H measured the plant as the binding constraint: the marginal cubic metre of hotel draw is served
at 22.66 K against a 49.2 K target (job 1171767). The obvious response is `Autosize`. Before running
56 cells on that assumption, one thing has to be checked, and it is visible in the IDF:

    WaterHeater:Sizing,
        300gal Natural Gas Water Heater - 300kBtu/hr 0.804 Therm Eff,
        PeakDraw,      !- Design Mode
        0.538503,      !- Time Storage Can Meet Peak Draw
        0,             !- Time for Tank Recovery          <-- ZERO
        1;             !- Nominal Tank Volume for Autosizing Plant Connections

Under `PeakDraw`, the TANK VOLUME is sized from the peak draw and `Time Storage Can Meet Peak Draw`,
while the HEATER CAPACITY is sized from `Time for Tank Recovery`. That field is 0. So flipping the
two capacity fields to `Autosize` may resize the storage and leave the burner where it was -- which
would be a silent no-op dressed as a fix, and we would only find out after 56 cells and four hours.

This probe reuses arm H's OWN injected IDFs, so the DHW schedules are byte-identical and the only
variable is plant sizing.

PRE-REGISTERED, before running:

  A1  CONTROL -- hotel DHW VOLUME is unchanged from arm H (<= 0.1 %) in every cell. Draw is
      schedule-driven; a plant resize must not touch it. If volume moves, the edit did something
      other than resize the plant and A2/A3 mean nothing.
  A2  The autosized `Heater Maximum Capacity` reported by EnergyPlus is > 87,921 W for the five
      140F heaters. IF IT COMES OUT <= 87,921 W (or 0), autosizing under `Time for Tank Recovery=0`
      is a no-op or worse, and the real fix is a DESIGN CHOICE (a recovery time), not a flag.
  A3  Conditional on A2: total DHW heating energy rises, and the volume-weighted delivered
      temperature rise moves UP toward the 49.2 K target (arm H: 41.65 K at r=1.0, 38.40 K at
      r=1.2031).

A2 is the one that decides whether a campaign is worth launching at all.

    python 3rdJ_09H_autosize_probe.py <arm_h_cell_dir> <out_dir> <epw> [--no-run]
"""
import os
import re
import shutil
import sqlite3
import subprocess
import sys

SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF_EXE = "/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus"
HARD_SIZED_W = 87921.3210516667
RHO_C = 4.184e6            # J per m3 per K

EXTRA_OUTPUTS = """
Output:Variable,*,Water Use Equipment Total Volume,Hourly;
Output:Variable,*,Water Use Equipment Heating Energy,Hourly;
Output:Variable,*,Water Use Equipment Target Water Temperature,Hourly;
Output:Variable,*,Water Use Equipment Mixed Water Temperature,Hourly;
"""


def autosize_idf(src, dst):
    """Copy `src` to `dst` with the six WaterHeater:Mixed capacity fields set to Autosize.

    Refuses (raises) unless exactly 6 of each field were replaced. A silent partial edit is the
    failure mode this project keeps paying for, so it is made loud here.
    """
    txt = open(src, errors="replace").read()
    n = {}
    for field in ("Tank Volume", "Heater Maximum Capacity"):
        pat = re.compile(r"([^,\n]+),(\s*!- %s\b)" % re.escape(field))
        txt, cnt = pat.subn(lambda m: "    Autosize,%s" % m.group(2), txt)
        n[field] = cnt
    if n["Tank Volume"] != 6 or n["Heater Maximum Capacity"] != 6:
        raise SystemExit("REFUSING: expected 6 replacements of each field, got %s" % n)
    txt += "\n" + EXTRA_OUTPUTS
    open(dst, "w").write(txt)
    print("  autosized: %s" % n)
    return n


def sized_capacities(eio_path):
    """(component, field, value) rows EnergyPlus reports for the water heaters."""
    out = []
    if not os.path.isfile(eio_path):
        return out
    for line in open(eio_path, errors="replace"):
        if "Component Sizing Information" not in line:
            continue
        if "WaterHeater" not in line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5:
            out.append((parts[1], parts[2], parts[3], parts[4]))
    return out


def sql_totals(sql_path):
    """{variable: {object: annual sum}} for the WaterUse variables."""
    if not os.path.isfile(sql_path):
        return {}
    con = sqlite3.connect(sql_path)
    cur = con.cursor()
    res = {}
    try:
        cur.execute("SELECT DISTINCT Name FROM ReportDataDictionary WHERE Name LIKE 'Water Use%'")
        names = [r[0] for r in cur.fetchall()]
        for nm in names:
            cur.execute(
                "SELECT d.KeyValue, SUM(r.Value) FROM ReportData r "
                "JOIN ReportDataDictionary d ON r.ReportDataDictionaryIndex = d.ReportDataDictionaryIndex "
                "WHERE d.Name = ? GROUP BY d.KeyValue", (nm,))
            res[nm] = {k: v for k, v in cur.fetchall()}
    finally:
        con.close()
    return res


def summarise(tag, sql_path):
    t = sql_totals(sql_path)
    vol = t.get("Water Use Equipment Total Volume", {})
    eng = t.get("Water Use Equipment Heating Energy", {})
    V = sum(vol.values())
    E = sum(eng.values())
    dT = (E / V) / RHO_C if V else float("nan")
    print("  [%s] objects=%d  total volume %.1f m3   heating energy %.1f GJ   implied dT %.2f K"
          % (tag, len(vol), V, E / 1e9, dT))
    lau = [k for k in vol if "LAUNDRY" in k.upper() and "30.6" in k]
    for k in lau:
        v, e = vol[k], eng.get(k, 0.0)
        print("      %-44s vol %9.1f m3  energy %8.1f GJ  dT %6.2f K"
              % (k[:44], v, e / 1e9, (e / v) / RHO_C if v else float("nan")))
    return V, E, dT


def main():
    cell, outdir, epw = sys.argv[1], sys.argv[2], sys.argv[3]
    no_run = "--no-run" in sys.argv
    os.makedirs(outdir, exist_ok=True)
    name = os.path.basename(cell.rstrip("/"))
    print("=" * 88)
    print("AUTOSIZE PROBE  cell=%s" % name)
    print("=" * 88)

    src = os.path.join(cell, "injected.idf")
    dst = os.path.join(outdir, "injected_autosize.idf")
    autosize_idf(src, dst)

    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    if not no_run:
        wrap = os.path.join(outdir, "energyplus")
        with open(wrap, "w") as f:
            f.write("#!/bin/bash\nsingularity exec --bind /speed-scratch --bind /nfs/speed-scratch "
                    "%s %s \"$@\"\n" % (SIF, SIF_EXE))
        os.chmod(wrap, 0o755)
        print("  running EnergyPlus ...")
        rc = subprocess.run([wrap, "-w", epw, "-d", run_dir, dst]).returncode
        print("  EnergyPlus exit=%d" % rc)
        if rc != 0:
            tail = os.path.join(run_dir, "eplusout.err")
            if os.path.isfile(tail):
                print("".join(open(tail, errors="replace").readlines()[-30:]))
            sys.exit(1)

    print("\n  --- A2: what EnergyPlus actually sized ---")
    rows = sized_capacities(os.path.join(run_dir, "eplusout.eio"))
    if not rows:
        print("  NO Component Sizing Information for WaterHeater -- autosize did not engage at all")
    a2 = True
    for comp, obj, field, val in rows:
        try:
            fv = float(val)
        except ValueError:
            fv = float("nan")
        flag = ""
        if "Capacity" in field:
            ok = fv > HARD_SIZED_W
            a2 &= ok
            flag = "   <-- %s the hard-sized %.1f W" % ("ABOVE" if ok else "NOT above", HARD_SIZED_W)
        print("    %-18s %-46s %-34s %s%s" % (comp, obj[:46], field[:34], val, flag))

    print("\n  --- A1 / A3: draw and delivery ---")
    Vh, Eh, dTh = summarise("arm H  (hard-sized)", os.path.join(cell, "run", "eplusout.sql"))
    Va, Ea, dTa = summarise("autosized         ", os.path.join(run_dir, "eplusout.sql"))

    dv = 100.0 * (Va / Vh - 1.0) if Vh else float("nan")
    de = 100.0 * (Ea / Eh - 1.0) if Eh else float("nan")
    a1 = abs(dv) <= 0.1
    a3 = dTa > dTh
    print("")
    print("  [%s] A1  CONTROL -- DHW volume unchanged by a plant resize: %+.4f %%"
          % ("PASS" if a1 else "FAIL", dv))
    print("  [%s] A2  autosized heater capacity exceeds the hard-sized 87,921 W"
          % ("PASS" if a2 and rows else "FAIL"))
    print("  [%s] A3  delivered temperature rise moves UP: %.2f -> %.2f K (energy %+.2f %%)"
          % ("PASS" if a3 else "FAIL", dTh, dTa, de))
    if not a2:
        print("\n  >>> A2 FAILED. Autosizing under `Time for Tank Recovery = 0` does not enlarge the")
        print("      burner. The fix is a DESIGN CHOICE -- pick a tank recovery time -- not a flag,")
        print("      and NO 56-cell campaign should be launched on the flag alone.")
    sys.exit(0)


if __name__ == "__main__":
    main()
