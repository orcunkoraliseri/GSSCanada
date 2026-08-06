#!/usr/bin/env python3
"""Per-OBJECT elasticity of hotel DHW: does each equipment object's energy follow its own volume?

WHY PER OBJECT (V2-D10, 2026-08-05). The aggregate hotel-DHW elasticity is not admissible evidence
about a plant resize, and the reason is on the record: under the global K = 6 the aggregate moved to
0.334 while every individual object's slope stayed where it was. The whole move was share
re-weighting -- `LAUNDRY` went from 26.7 % to 65.4 % of hotel DHW -- so the aggregate reports a
change for an intervention that changed no physics. A gate scored on it cannot fail.

WHAT IS SCORED HERE. For each equipment TYPE, across the cells of one arm, the log-log slope of

    energy vs volume        d ln E / d ln V     0 = capacity-pinned, 1 = free-running
    delivered rise vs volume d ln dT / d ln V   -1 = capacity-pinned, 0 = free-running

The two are the same measurement: E = rho c V dT, so slope(E) = 1 + slope(dT), exactly. BOTH are
printed because the project's own notes quote the pinned signature in both forms -- "-0.98" is the
dT form and "E ~ V^0.02" is the energy form -- and quoting one number against the other convention
is how a passing result gets read as a failing one.

A pinned object is the signature to look for: its volume rises across the r-grid while its energy
does not, because the burner is already flat out. `LAUNDRY` reads 0.018 (K = 1) and 0.031 (K = 6):
six times the capacity moved it by 0.013, which is the measurement that refuted a global K.

    python 3rdJ_09H_laundry_slope.py <arm_dir> [<arm_dir> ...] [--ref <arm_dir>] [--geo Tall__MTL]
"""
import csv
import math
import os
import sys

FOCUS = "LAUNDRY"
REFERENCE_TYPE = "BOOSTER"      # same 180 F target, never clipped -> the internal design rise


def read_arm(arm, geo, only=()):
    """{type: [(volume, energy, dT, cell)]} over every cell of `arm` whose name ends with `geo`.

    `only` restricts to named cell prefixes. It exists because a slope compared across arms has to
    be computed over the SAME cells: the 56-cell arms carry seven `Tall__MTL` cells and this probe
    carries three, and a slope over a different r-range is a different quantity wearing the same
    label.
    """
    out = {}
    if not os.path.isdir(arm):
        return out
    for cell in sorted(os.listdir(arm)):
        # `__` + geo, NOT geo. Plain endswith("Tall__MTL") also matches
        # `B_central__SuperTall__MTL`, which silently pools two geometries into one slope -- caught
        # 2026-08-05 by the printed cell count reading 6 where the probe has 3.
        if geo and not cell.endswith("__" + geo.lstrip("_")):
            continue
        if only and not any(cell.startswith(p) for p in only):
            continue
        p = os.path.join(arm, cell, "hotel_dT_by_type.csv")
        if not os.path.isfile(p):
            continue
        with open(p) as f:
            for row in csv.DictReader(f):
                out.setdefault(row["type"], []).append(
                    (float(row["volume_m3"]), float(row["energy_J"]), float(row["dT_K"]), cell))
    return out


def slope(xs, ys):
    """OLS slope of ln y on ln x. None when x does not vary -- an undefined slope is not 0."""
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    n = len(lx)
    mx, my = sum(lx) / n, sum(ly) / n
    sxx = sum((a - mx) ** 2 for a in lx)
    if sxx <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sxx


def main():
    args = [a for a in sys.argv[1:]]
    geo = args[args.index("--geo") + 1] if "--geo" in args else "Tall__MTL"
    ref = args[args.index("--ref") + 1] if "--ref" in args else ""
    only = tuple(x for x in (args[args.index("--only") + 1].split(",") if "--only" in args else ())
                 if x)
    arms = [a for i, a in enumerate(args)
            if not a.startswith("--") and args[i - 1] not in ("--geo", "--ref", "--only")]
    if not arms:
        raise SystemExit("usage: %s <arm_dir> [...] [--ref <arm_dir>] [--geo Tall__MTL] "
                         "[--only B_cons,B_central,B_opt]" % sys.argv[0])

    ref_data = read_arm(ref, geo, only) if ref else {}

    for arm in arms:
        data = read_arm(arm, geo, only)
        if not data:
            print("REFUSING: no hotel_dT_by_type.csv under %s matching geo %r" % (arm, geo))
            sys.exit(2)
        n_cells = len(next(iter(data.values())))
        print("=" * 96)
        print("ARM %s   geo=%s   %d cells   %d equipment types"
              % (os.path.basename(arm.rstrip("/\\")), geo, n_cells, len(data)))
        print("=" * 96)
        if n_cells < 2:
            print("  REFUSING: a slope needs at least 2 cells, found %d" % n_cells)
            sys.exit(3)
        print("  %-14s %5s %11s %11s %9s %9s %9s"
              % ("type", "n", "slope lnE", "slope lndT", "dT mean", "dT min", "dT max"))
        rows = sorted(data.items(), key=lambda kv: -sum(v[0] for v in kv[1]))
        for t, vals in rows:
            V = [v[0] for v in vals]
            E = [v[1] for v in vals]
            D = [v[2] for v in vals]
            se, sd = slope(V, E), slope(V, D)
            mark = "  <<<" if t == FOCUS else ("  (ref)" if t == REFERENCE_TYPE else "")
            print("  %-14s %5d %11s %11s %9.3f %9.3f %9.3f%s"
                  % (t, len(vals),
                     "constant V" if se is None else "%.4f" % se,
                     "constant V" if sd is None else "%.4f" % sd,
                     sum(D) / len(D), min(D), max(D), mark))

        if ref_data:
            print("")
            print("  vs reference arm %s -- delivered rise, per type, mean over cells"
                  % os.path.basename(ref.rstrip("/\\")))
            worst_t, worst = None, 0.0
            for t, vals in rows:
                if t not in ref_data:
                    continue
                a = sum(v[2] for v in vals) / len(vals)
                b = sum(v[2] for v in ref_data[t]) / len(ref_data[t])
                pct = 100.0 * (a / b - 1.0) if b else float("nan")
                if t != FOCUS and abs(pct) > abs(worst):
                    worst, worst_t = pct, t
                print("    %-14s %9.3f -> %9.3f K   %+8.3f %%%s"
                      % (t, b, a, pct, "  <<<" if t == FOCUS else ""))
            print("")
            print("  CONTROL: largest move among the NON-%s types: %+.4f %% (%s)"
                  % (FOCUS, worst, worst_t))
        print("")


if __name__ == "__main__":
    main()
