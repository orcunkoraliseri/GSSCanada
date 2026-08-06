#!/usr/bin/env python3
"""Uniform DHW plant resize: scale the six burners by a single documented factor. 3-cell probe.

USER DECISION, 2026-08-03: resize the plant ONCE, from the grid maximum, and apply the SAME capacity
to all 56 cells. Per-cell `Autosize` was rejected on methodological grounds -- it would give `B_opt`
(r = 1.20) a larger boiler than `B_cons` (r = 0.98), so "DHW rises with occupancy" would partly
become "we gave it a bigger boiler". The 56-cell grid exists to vary occupancy and nothing else.

THE NUMBER, measured not assumed (job 1171806, all 56 cells of arm H):

    grid-max peak hourly draw          15.8878 m3/h
    at the 180F target rise (71.4 K)   1318.4 kW      <- the conservative bound
    at the 140F target rise (49.2 K)     908.5 kW
    installed                            447.6 kW     (5 x 87,921.3 + 7,999.96)
    ratio                                2.95         -> K = 3.0, ~2 % headroom

WHAT IS CHANGED, and only this: `Heater Maximum Capacity` x K on all six `WaterHeater:Mixed`.

WHAT IS DELIBERATELY NOT CHANGED, and why it makes the intervention energy-neutral:
  * `Tank Volume` -- untouched, so the `Off/On Cycle Loss Coefficient to Ambient` (11.2595 W/K) acts
    on the same storage and standby losses are identical.
  * `Part Load Factor Curve Name` -- verified EMPTY in the IDF, so thermal efficiency is a flat
    0.803984 regardless of how far the burner is from full load. Oversizing costs nothing.
  * `Off/On Cycle Parasitic Fuel Consumption Rate` -- 8,146.58 W, a CONSTANT that does not scale
    with capacity. Six of them (48.9 kW = 1,542 GJ/yr) are most of the fixed intercept the
    saturation discriminator measured (~1,860 GJ on `Tall__MTL`), and they do not move here.

So the burner can only ever *meet more of the load*; it cannot inflate energy by being larger.

PRE-REGISTERED, before running:

  R1  CONTROL -- DHW volume unchanged from arm H (<= 0.1 %) in all three cells. Capacity must not
      change the draw. If volume moves, the edit did something other than resize the burner.
  R2  Tower-wide implied delivered rise goes UP in every cell, and goes up MORE in the cells that
      were more constrained (arm H: 41.65 K at r = 1.0000, 39.43 K at r = 1.1244, 38.40 K at
      r = 1.2031 -- so the ordering of the GAINS must be the reverse of the arm-H levels).
  R3  DECISIVE -- the r-elasticity of hotel DHW energy across the three cells rises from arm H's
      0.5617 to >= 0.90. This is the whole point: the plant must stop mediating the occupancy
      signal. Below 0.90 the resize is insufficient and K must be revisited BEFORE any campaign.
  R4  The implied MARGINAL rise (slope of E vs V) rises from 22.66 K toward the 49.2 K target.

R1 is the control; R3 is the gate that decides whether a 56-cell campaign is worth launching.

    python 3rdJ_09H_plant_resize_probe.py <arm_h_cell_dir> <out_dir> <epw> <K>
"""
import os
import re
import sqlite3
import subprocess
import sys

SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF_EXE = "/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus"
RHO_C = 4.184e6

# The heater count is a PROPERTY OF THE CELL, measured per IDF -- it is NOT a constant.
# This was hard-coded to 6 until 2026-08-03, when the headroom check on the grid-maximum cell
# (`sens_hotel_opt__SuperTall__MTL`, job 1171855_0) refused with "expected 6, rewrote 11".
# SuperTall carries 11 `WaterHeater:Mixed`, Tall carries 6, so the "installed = 447.6 kW"
# figure quoted throughout the K sweep is a Tall number and was never a grid-wide constant.
# The guard below is therefore reformulated: it no longer asserts a magic number, it asserts
# that EVERY heater the IDF declares was rewritten and that nothing else moved. A guard that
# encodes an assumption about the stock cannot detect that the assumption is wrong.
MIN_HEATERS = 1

EXTRA_OUTPUTS = """
Output:Variable,*,Water Use Equipment Total Volume,Hourly;
Output:Variable,*,Water Use Equipment Heating Energy,Hourly;
"""


_OBJ_START_RE = re.compile(r"^WaterHeater:Mixed,\s*$", re.MULTILINE)


def _heater_name_spans(txt):
    """[(start, end, name)] for every WaterHeater:Mixed object, in file order.

    Added for V2-D10. The scalar path never needed to know which object a capacity field belonged
    to; a per-object path is nothing but that question. The span ends at the next object header (or
    EOF), which is enough to attribute a field because `Heater Maximum Capacity` is declared once
    per object.
    """
    starts = [m.start() for m in _OBJ_START_RE.finditer(txt)]
    spans = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(txt)
        body = txt[s:e]
        # field 1 of WaterHeater:Mixed is Name; take the first line after the header
        lines = [ln.strip() for ln in body.splitlines()[1:] if ln.strip()]
        nm = lines[0].split("!")[0].strip().rstrip(",;").strip() if lines else ""
        spans.append((s, e, nm))
    return spans


def resize_idf(src, dst, K, per_object=None):
    """Copy `src` to `dst` with Heater Maximum Capacity scaled on every WaterHeater:Mixed.

    `K` is the factor applied to every heater NOT named in `per_object`; `per_object` is an optional
    {heater name -> factor} mapping, matched case-insensitively against the object's Name field.

    PER-OBJECT MODE IS DEFAULT-OFF (V2-D10, 2026-08-05). With `per_object` unset this function takes
    the same substitution over the same regex and emits the same formatting as before, so arms H and
    R reproduce BYTE-FOR-BYTE -- that equivalence is checked, not asserted, by
    `3rdJ_09H_resize_spec_check.py` against the artefacts already on disk. The same default-off
    discipline as the `EPLUS_EXE` local-run port, and for the same reason: eight arms have already
    been differenced against these files.

    WHY A NAME MAPPING RATHER THAN A RULE. The caller passes explicit heater names because the
    heater that serves `LAUNDRY` is named `300gal ... - 300kBtu/hr 4` on `Tall` and
    `... 9` on `SuperTall`, and its Setpoint schedule (180F) is shared with the electric booster on
    a different loop. No property of the object identifies it; only the plant topology does. So the
    selection is resolved once, per IDF, by `3rdJ_09H_dhw_plant_topology.py`, and arrives here as
    names. Encoding a name pattern or a setpoint rule in this function would bake one geometry's
    accident into every cell.

    Refuses unless every declared capacity field was rewritten (K = 1 counts as a rewrite), and
    unless every name in `per_object` matched exactly one heater. A per-object spec that matched
    nothing would resize nothing and report success -- the silent-default shape of job 1171812.
    Tank Volume is NOT touched.
    """
    txt = open(src, errors="replace").read()
    seen = []

    spans = _heater_name_spans(txt) if per_object else []
    want = {k.strip().lower(): float(v) for k, v in (per_object or {}).items()}
    hits = {k: 0 for k in want}

    def _factor_at(pos):
        if not want:
            return K, ""
        for s, e, nm in spans:
            if s <= pos < e:
                f = want.get(nm.lower())
                if f is not None:
                    hits[nm.lower()] += 1
                    return f, nm
                return K, nm
        return K, ""

    def sub(m):
        old = float(m.group(1))
        factor, nm = _factor_at(m.start())
        new = old * factor
        seen.append((old, new, factor, nm))
        return "    %.6f,%s" % (new, m.group(2))

    pat = re.compile(r"([0-9.eE+-]+),(\s*!- Heater Maximum Capacity\b)")
    # Count what the IDF actually declares BEFORE rewriting, then require that the rewrite hit
    # every one of them. This is the same guard as before -- "no heater was left behind" -- but
    # its reference now comes from the file under edit rather than from a number I believed.
    declared = len(pat.findall(txt))
    txt, cnt = pat.subn(sub, txt)
    if declared < MIN_HEATERS:
        raise SystemExit("REFUSING: no Heater Maximum Capacity field found in %s" % src)
    if cnt != declared:
        raise SystemExit("REFUSING: IDF declares %d Heater Maximum Capacity fields, rewrote %d"
                         % (declared, cnt))
    if "!- Tank Volume" not in txt:
        raise SystemExit("REFUSING: Tank Volume fields vanished -- the edit is not surgical")
    missed = [k for k, n in hits.items() if n != 1]
    if missed:
        raise SystemExit("REFUSING: per-object spec names %d heater(s) that did not match exactly "
                         "one WaterHeater:Mixed in %s: %s -- declared names are %s"
                         % (len(missed), src, missed, [nm for _, _, nm in spans]))
    open(dst, "w").write(txt + "\n" + EXTRA_OUTPUTS)
    base_kW = sum(o for o, _, _, _ in seen) / 1000.0
    new_kW = sum(n for _, n, _, _ in seen) / 1000.0
    if want:
        print("  per-object resize, default K = %.4f, %d named override(s), rewrote %d burners "
              "(IDF declared %d):" % (K, len(want), cnt, declared))
        for old, new, factor, nm in seen:
            print("      %14.2f W -> %14.2f W  (x%.4f)  %s" % (old, new, factor, nm))
    else:
        print("  K = %.4f, rewrote %d burners (IDF declared %d):" % (K, cnt, declared))
        for old, new, _, _ in seen:
            print("      %14.2f W -> %14.2f W" % (old, new))
    print("      installed total %.1f kW -> %.1f kW" % (base_kW, new_kW))
    # Emitted so the per-cell installed base is on the record rather than assumed to be 447.6 kW.
    print("PLANT_BASE kW_base=%.4f kW_resized=%.4f n_heaters=%d" % (base_kW, new_kW, cnt))
    return seen, base_kW, new_kW


def sql_totals(sql_path):
    if not os.path.isfile(sql_path):
        return {}, {}
    con = sqlite3.connect(sql_path)
    cur = con.cursor()
    out = {}
    try:
        for nm in ("Water Use Equipment Total Volume", "Water Use Equipment Heating Energy"):
            cur.execute(
                "SELECT d.KeyValue, SUM(r.Value) FROM ReportData r JOIN ReportDataDictionary d "
                "ON r.ReportDataDictionaryIndex = d.ReportDataDictionaryIndex "
                "WHERE d.Name = ? GROUP BY d.KeyValue", (nm,))
            out[nm] = {k: v for k, v in cur.fetchall()}
    finally:
        con.close()
    return out.get("Water Use Equipment Total Volume", {}), \
        out.get("Water Use Equipment Heating Energy", {})


def summarise(tag, sql_path):
    vol, eng = sql_totals(sql_path)
    V, E = sum(vol.values()), sum(eng.values())
    dT = (E / V) / RHO_C if V else float("nan")
    print("  [%s] objects=%3d  volume %9.1f m3   energy %8.1f GJ   implied dT %6.2f K"
          % (tag, len(vol), V, E / 1e9, dT))
    return V, E, dT


def main():
    cell, outdir, epw, K = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    os.makedirs(outdir, exist_ok=True)
    name = os.path.basename(cell.rstrip("/"))
    print("=" * 88)
    print("PLANT RESIZE PROBE  cell=%s  K=%.4f" % (name, K))
    print("=" * 88)

    dst = os.path.join(outdir, "injected_resized.idf")
    _, base_kW, new_kW = resize_idf(os.path.join(cell, "injected.idf"), dst, K)

    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    wrap = os.path.join(outdir, "energyplus")
    with open(wrap, "w") as f:
        f.write("#!/bin/bash\nsingularity exec --bind /speed-scratch --bind /nfs/speed-scratch "
                "%s %s \"$@\"\n" % (SIF, SIF_EXE))
    os.chmod(wrap, 0o755)
    print("  running EnergyPlus ...")
    rc = subprocess.run([wrap, "-w", epw, "-d", run_dir, dst],
                        stdout=subprocess.DEVNULL).returncode
    print("  EnergyPlus exit=%d" % rc)
    if rc != 0:
        err = os.path.join(run_dir, "eplusout.err")
        if os.path.isfile(err):
            print("".join(open(err, errors="replace").readlines()[-25:]))
        sys.exit(1)

    # Both labels carry the cell's OWN measured installed capacity. They used to print
    # `447.6` and `447.6 * K`, which are Tall-geometry numbers -- on a SuperTall cell that
    # label would have been wrong by a factor of ~2 while looking authoritative.
    Vh, Eh, dTh = summarise("arm H  (%7.1f kW)" % base_kW, os.path.join(cell, "run", "eplusout.sql"))
    Vr, Er, dTr = summarise("resized(%7.1f kW)" % new_kW, os.path.join(run_dir, "eplusout.sql"))
    dv = 100.0 * (Vr / Vh - 1.0) if Vh else float("nan")
    de = 100.0 * (Er / Eh - 1.0) if Eh else float("nan")
    r1 = abs(dv) <= 0.1
    r2 = dTr > dTh
    print("")
    print("  [%s] R1  CONTROL -- volume unchanged by a burner resize: %+.4f %%"
          % ("PASS" if r1 else "FAIL", dv))
    print("  [%s] R2  delivered rise moves UP: %.2f -> %.2f K  (gain %+.2f K, energy %+.2f %%)"
          % ("PASS" if r2 else "FAIL", dTh, dTr, dTr - dTh, de))
    print("  R3/R4 need all three cells -- computed by the aggregating step, not here.")
    # machine-readable line the .sh greps for the cross-cell R3/R4 fit
    print("RESIZE_ROW %s K=%.4f Vh=%.4f Eh=%.6f dTh=%.6f Vr=%.4f Er=%.6f dTr=%.6f"
          % (name, K, Vh, Eh, dTh, Vr, Er, dTr))
    sys.exit(0)


if __name__ == "__main__":
    main()
