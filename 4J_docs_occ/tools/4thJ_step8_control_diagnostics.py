# -*- coding: utf-8 -*-
"""4J Step 8 item 8.3 --- DIAGNOSTICS ON THE UNINJECTED CONTROL.

`G8.0` asks where the untreated control sits relative to every band.  It sits a
long way from TABULA's own published answer, and the sign is not the same in
every fold, so the next question is forced: **how much of that is the
occupancy-free physics we chose, and how much is a modelling convention nobody
ruled?**

This file measures four conventions, one at a time, against the campaign result
for the same cell.  🔴 None of them is a correction and none of them is applied
to anything: the 88 campaign IDFs and the campaign artefacts are not touched,
every run here happens in a temporary directory, and the output is a leverage
table.  Moving a band or a convention to close the gap is exactly what `G8.0`
forbids.

  D1  TIMESTEP        `Timestep, 6` -> `Timestep, 1`.  Run over ALL 88 cells,
                      because a convention that moves the answer by a few per
                      cent per fold is the same class of free parameter as the
                      weather station of `FINDING 120`, and a per-fold median is
                      the only way to see whether it is country-correlated.
  D2  SOLAR           the simple glazing SHGC 0.70 -> 0.001.  TABULA does not
                      use a bare SHGC: it applies frame and shading factors, so
                      our windows admit strictly more solar than TABULA's.  This
                      brackets that channel by removing it.
  D3  GROUND          EnergyPlus was left to its own default ground temperature
                      --- a constant 18.0 C, which every cell's error file
                      states out loud --- because no `Site:GroundTemperature`
                      object is written.  This replaces it with the EPW's own
                      monthly mean dry-bulb temperatures.
  D4  GAINS           `phi_int` 3.0 W/m2 -> 0.  The control's only load.  Its
                      leverage is the scale against which the whole `f`-sweep of
                      8.5 will be read: if switching the gain off moves heating
                      less than the conventions above do, then redistributing
                      that same gain in time cannot plausibly move it more.

Output: `Step8_docs/outputs_step8/control_diagnostics.json`.
"""
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
ARCH = os.path.join(BASE, "archetypes")
WEATHER = os.path.join(BASE, "weather")
ANNUAL = os.path.join(BASE, "control_annual.csv")
OUT = os.path.join(BASE, "control_diagnostics.json")
EPLUS = r"C:\EnergyPlusV24-2-0\energyplus.exe"

GJ_TO_KWH = 1000.0 / 3.6


def heating_gj(tbl):
    for ln in io.open(tbl, encoding="utf-8", errors="replace"):
        f = [x.strip() for x in ln.split(",")]
        if len(f) > 13 and f[1] == "Heating":
            try:
                return sum(float(x) for x in f[2:15] if x)
            except ValueError:
                continue
    return None


def run(idf_text, epw, d):
    os.makedirs(d)
    p = os.path.join(d, "in.idf")
    io.open(p, "w", encoding="utf-8", newline="").write(idf_text)
    r = subprocess.run([EPLUS, "-w", epw, "-d", d, p],
                       cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    tbl = os.path.join(d, "eplustbl.csv")
    if r.returncode != 0 or not os.path.exists(tbl):
        return None, None
    err = os.path.join(d, "eplusout.err")
    warn = 0
    if os.path.exists(err):
        warn = sum(1 for ln in io.open(err, encoding="utf-8", errors="replace")
                   if ln.strip().startswith("** Warning **"))
    return heating_gj(tbl), warn


def epw_monthly_means(path):
    tot = [0.0] * 12
    cnt = [0] * 12
    for ln in io.open(path, encoding="utf-8", errors="replace").read().split("\n")[8:]:
        f = ln.split(",")
        if len(f) < 10:
            continue
        try:
            m = int(f[1])
            t = float(f[6])
        except ValueError:
            continue
        if 1 <= m <= 12:
            tot[m - 1] += t
            cnt[m - 1] += 1
    return [tot[i] / cnt[i] for i in range(12)]


# ---- the four one-at-a-time edits, each applied to the CAMPAIGN IDF text ----

def k_timestep(txt, ctx):
    out = txt.replace("Timestep, 6;", "Timestep, 1;")
    return out if out != txt else None


def k_solar(txt, ctx):
    m = re.search(r"(WindowMaterial:SimpleGlazingSystem,.*?;)", txt, re.S)
    if not m:
        return None
    blk = m.group(1)
    parts = blk.rsplit(",", 1)
    new = parts[0] + ",\n  0.0010;"
    return txt.replace(blk, new, 1)


def k_ground(txt, ctx):
    vals = ",".join("%.2f" % v for v in ctx["monthly_means"])
    obj = "\nSite:GroundTemperature:BuildingSurface, %s;\n" % vals
    return txt.replace("\nRunPeriod,", obj + "\nRunPeriod,", 1)


def k_gains(txt, ctx):
    m = re.search(r"(OtherEquipment,.*?;)", txt, re.S)
    if not m:
        return None
    blk = m.group(1)
    new = re.sub(r"\n  [0-9.]+,( +)?(!- Design Level \{W\})",
                 lambda mo: "\n  0.0000,                    !- Design Level {W}", blk, count=1)
    if new == blk:
        return None
    return txt.replace(blk, new, 1)


KNOBS = [
    ("D1_timestep_1", k_timestep, "Timestep 6 -> 1", "all"),
    ("D2_solar_off", k_solar, "window SHGC 0.70 -> 0.001", "median"),
    ("D3_ground_epw_monthly", k_ground, "ground 18.0 C default -> EPW monthly means", "median"),
    ("D4_gains_off", k_gains, "phi_int 3.0 -> 0.0 W/m2", "median"),
]


def main():
    rows = list(csv.DictReader(io.open(ANNUAL, encoding="utf-8")))
    wx = {r["fold"]: r["epw"] for r in rows}
    monthly = {f: epw_monthly_means(os.path.join(WEATHER, e)) for f, e in wx.items()}

    # the median-EUI cell of each fold: one representative, named, not cherry-picked
    median_cell = {}
    for f in ("es", "uk", "it"):
        sel = sorted([r for r in rows if r["fold"] == f],
                     key=lambda r: float(r["eui_kwh_m2a"]))
        median_cell[f] = sel[len(sel) // 2]["cell"]

    res = {"note": "DIAGNOSTIC ONLY. No campaign artefact and no IDF on disk was "
                   "modified; nothing here is applied and no band is moved.",
           "median_cell": median_cell, "knobs": {}}
    tmp = tempfile.mkdtemp(prefix="4j_diag_")
    try:
        for name, fn, desc, scope in KNOBS:
            targets = rows if scope == "all" else \
                [r for r in rows if r["cell"] in median_cell.values()]
            per = []
            for k, r in enumerate(targets):
                src = os.path.join(ARCH, r["cell"] + ".idf")
                txt = io.open(src, encoding="utf-8", errors="replace").read()
                mod = fn(txt, {"monthly_means": monthly[r["fold"]]})
                if mod is None:
                    sys.exit("%s could not be applied to %s -- refusing to report a "
                             "no-op as a measurement" % (name, r["cell"]))
                if mod == txt:
                    sys.exit("%s left %s byte-identical -- that is a no-op"
                             % (name, r["cell"]))
                gj, warn = run(mod, os.path.join(WEATHER, wx[r["fold"]]),
                               os.path.join(tmp, "%s_%03d" % (name, k)))
                if gj is None:
                    sys.exit("%s failed to run on %s" % (name, r["cell"]))
                base_gj = float(r["heating_gj_eplustbl"])
                per.append({"cell": r["cell"], "fold": r["fold"],
                            "base_gj": base_gj, "knob_gj": gj,
                            "dev_pct": 100.0 * (gj - base_gj) / base_gj,
                            "warnings": warn})
            byfold = {}
            for f in ("es", "uk", "it"):
                s = sorted(x["dev_pct"] for x in per if x["fold"] == f)
                if s:
                    byfold[f] = {"n": len(s), "median_pct": s[len(s) // 2],
                                 "min_pct": s[0], "max_pct": s[-1]}
            res["knobs"][name] = {"description": desc, "scope": scope,
                                  "per_fold": byfold, "cells": per}
            print("%-22s %-42s" % (name, desc))
            for f, v in byfold.items():
                print("    %-3s n=%2d  median %+8.2f %%   range %+8.2f .. %+8.2f"
                      % (f, v["n"], v["median_pct"], v["min_pct"], v["max_pct"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=1, sort_keys=True))
    print("\nwritten: %s" % os.path.relpath(OUT, PROJ))


if __name__ == "__main__":
    main()
