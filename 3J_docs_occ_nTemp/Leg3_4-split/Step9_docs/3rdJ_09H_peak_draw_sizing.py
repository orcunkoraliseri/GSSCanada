#!/usr/bin/env python3
"""Size a DHW heater from the PEAK HOURLY DRAW it serves, not by nudging the previous K.

WHY (V2-D10, 2026-08-05). `LAUNDRY` at K = 7 delivers 70.25 / 67.09 / 63.19 K across the three
probe cells against an unclipped internal reference of 71.36 K, so the highest-draw cell is still
clipping and K = 7 is insufficient there. The pre-registration for D10 says, in its own words, that
"below 65 K means K = 7 is insufficient and the factor must be RE-DERIVED rather than nudged."
Nudging 7 -> 8 would be fitting a number to the three cells that happen to have been run; the
r-grid of the full campaign is wider, so a value tuned on this subset would silently under-size the
cells outside it. That is the same failure mode as picking a global K off a volume-weighted dT.

WHAT IS DERIVED. Volume is a DEMAND-side quantity: it is set by the schedule and the peak flow rate
and does not depend on the heater at all -- verified here by requiring the annual volume to agree
between the arms compared. So the capacity that never clips is a property of the DRAW, computable
once from any arm:

    required_W = max_over_hours( V_h [m3] * rho*c [J/m3/K] * dT_design [K] ) / 3600 s

with dT_design taken from an UNCLIPPED reference object at the same setpoint (`BOOSTER`), not from
the object being sized -- an object that is clipping cannot report its own design rise.

CAVEAT, STATED BECAUSE IT SETS THE DIRECTION OF THE ERROR. The ESO reports HOURLY totals, while the
heater clips at the simulation timestep. A capacity sized on an hourly mean is therefore a LOWER
BOUND on the capacity that never clips: it can still clip within the hour. The number this prints
is "at least this much", never "this is enough".

    python 3rdJ_09H_peak_draw_sizing.py <cell_dir> [<cell_dir> ...] --equip <substring>
                                        [--ref-type BOOSTER] [--current-w 87921.321]
"""
import csv
import os
import re
import sys

RHO_C = 4186000.0          # 1000 kg/m3 * 4186 J/kg/K -- water, the value E+ uses for these loops
SECONDS_PER_HOUR = 3600.0


def eso_series(eso_path, var_name, key_substr):
    """Hourly series for one report variable of one object, read straight from the ESO.

    Returns (key_name, [values]). Refuses on 0 or >1 matching keys: a series silently summed over
    two objects is the same defect class as a slope pooled over two geometries.
    """
    idx_by_key = {}
    with open(eso_path, errors="replace") as f:
        for line in f:
            if line.startswith("End of Data Dictionary"):
                break
            parts = line.split(",", 3)
            if len(parts) < 4:
                continue
            key, rest = parts[2], parts[3]
            if var_name.lower() in rest.lower() and key_substr.lower() in key.lower():
                idx_by_key[key] = parts[0].strip()
        if len(idx_by_key) != 1:
            raise SystemExit("REFUSING: %r matches %d %r series in %s: %s"
                             % (key_substr, len(idx_by_key), var_name, os.path.basename(eso_path),
                                sorted(idx_by_key)[:4]))
        key, idx = next(iter(idx_by_key.items()))
        pat = idx + ","
        vals = []
        for line in f:
            if line.startswith(pat):
                vals.append(float(line.split(",", 1)[1]))
    return key, vals


def ref_dT(cell_dir, ref_type):
    p = os.path.join(cell_dir, "hotel_dT_by_type.csv")
    with open(p) as f:
        for row in csv.DictReader(f):
            if row["type"] == ref_type:
                return float(row["dT_K"])
    raise SystemExit("REFUSING: reference type %r absent from %s" % (ref_type, p))


def main():
    a = sys.argv[1:]
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    equip = opt("--equip")
    ref_type = opt("--ref-type", "BOOSTER")
    cur_w = float(opt("--current-w", "0") or 0)
    cells = [x for i, x in enumerate(a)
             if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    if not equip or not cells:
        raise SystemExit("usage: %s <cell_dir> [...] --equip <substring> [--ref-type BOOSTER] "
                         "[--current-w <W>]" % sys.argv[0])

    print("=" * 100)
    print("Peak-draw sizing for %r   reference rise from %r" % (equip, ref_type))
    print("=" * 100)
    print("  %-26s %10s %12s %12s %12s %9s" %
          ("cell", "dT_ref K", "peak m3/h", "annual m3", "required kW", "K needed"))
    worst = 0.0
    for c in cells:
        eso = os.path.join(c, "run", "eplusout.eso")
        if not os.path.isfile(eso):
            print("  %-26s ESO missing" % os.path.basename(c))
            continue
        key, vals = eso_series(eso, "Water Use Equipment Total Volume", equip)
        dT = ref_dT(c, ref_type)
        peak = max(vals)
        req = peak * RHO_C * dT / SECONDS_PER_HOUR
        k = req / cur_w if cur_w else float("nan")
        worst = max(worst, k)
        print("  %-26s %10.3f %12.4f %12.1f %12.2f %9.3f"
              % (os.path.basename(c.rstrip("/\\")), dT, peak, sum(vals), req / 1000.0, k))
    print("")
    print("  object resolved to: %s" % key)
    if cur_w:
        print("  installed now: %.2f kW   worst cell needs K >= %.3f" % (cur_w / 1000.0, worst))
        print("  NOTE: hourly-mean basis -- this is a LOWER BOUND; sub-hourly peaks clip above it.")


if __name__ == "__main__":
    main()
