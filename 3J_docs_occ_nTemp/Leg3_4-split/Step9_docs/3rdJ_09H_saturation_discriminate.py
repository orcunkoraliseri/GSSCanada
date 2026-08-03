#!/usr/bin/env python3
"""Separate PLANT SATURATION from a CONSTANT STANDBY LOSS. The first probe could not.

`3rdJ_09H_saturation_probe.py` measured hotel DHW volume elasticity 1.0000 (R2 1.000) against energy
elasticity 0.5617 and printed "SATURATION CONFIRMED". That conclusion is NOT established by that
measurement, and the branch is withdrawn: a constant standby/distribution loss produces an energy
elasticity below 1 with no capacity constraint whatsoever, because

    E = L + V * rho_c * dT          =>      d ln E / d ln V  =  1 / (1 + L/(V*rho_c*dT))  <  1

Both candidates predict the same sign and, over a volume range of only 0.98x..1.20x, very nearly the
same shape. A test that cannot tell its two candidate explanations apart is not evidence for either.

The discriminator is the MARGINAL energy per m3, not the average:

  * CONSTANT-LOSS model: the loss does not scale with draw, so the marginal cubic metre must still be
    served at the FULL target temperature rise. Slope b = rho_c * dT_target.
  * SATURATION model: the plant is already at its ceiling, so the marginal cubic metre is served at a
    REDUCED rise. Slope b << rho_c * dT_target.

PRE-REGISTERED, before running:

  D1  E vs V is linear within a (geometry, city) group, R2 >= 0.98 -- a control. If it is not linear,
      neither simple model applies and both are withdrawn.
  D2  CONSTANT-LOSS if the implied marginal rise dT_marg = b/rho_c is within 15 % of the smallest
      target rise available in the IDF (i.e. the marginal draw is served properly and the shortfall
      is a fixed overhead).
  D3  SATURATION if dT_marg is below 70 % of that smallest target rise -- the marginal draw is being
      served at a materially reduced temperature, which a fixed loss cannot cause.
  D4  Corroboration, independent of the fit: the AVERAGE rise dT_avg = (E/V)/rho_c must FALL as r
      rises under saturation, and must RISE under the constant-loss model (the fixed loss is spread
      over more volume, so measured energy per m3 falls -- but that is energy per m3 INCLUDING the
      loss; the delivered rise would be flat). Reported as the trend of dT_avg vs r.

D2 and D3 are mutually exclusive; the 70..85 % gap is left explicitly inconclusive rather than being
assigned to whichever answer is convenient.

    python 3rdJ_09H_saturation_discriminate.py <campaign_dir> <agg_annual.csv>
"""
import os
import re
import sys

import numpy as np
import pandas as pd

RHO_C = 4.184e6 / 1e9          # GJ per m3 per K
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "sat", os.path.join(HERE, "3rdJ_09H_saturation_probe.py"))
_sat = importlib.util.module_from_spec(_spec)
# import without running main()
_src = open(_spec.origin).read().replace('if __name__ == "__main__":\n    main()', "")
exec(compile(_src, _spec.origin, "exec"), _sat.__dict__)


def target_rises(idf_path, mains_c):
    """Target temperature rises (K) actually used by the hotel WaterUse:Equipment objects."""
    txt = open(idf_path, errors="replace").read()
    # target schedule names carry the setpoint in F, e.g. `Mixed Water At Faucet Temp - 140F`
    rises = {}
    for m in re.finditer(r"Mixed Water At Faucet Temp - (\d+)F", txt):
        f = float(m.group(1))
        rises[f] = (f - 32.0) * 5.0 / 9.0 - mains_c
    return rises


def main():
    camp, agg_p = sys.argv[1], sys.argv[2]
    agg = pd.read_csv(agg_p)
    agg["energy_GJ"] = agg["energy_J"] / 1e9
    e_hotel = (agg[(agg.channel == "hotel") & (agg.end_use == "dhw")]
               .groupby("cell_tag")["energy_GJ"].sum())

    rows = []
    idf_seen = None
    for d in sorted(os.listdir(camp)):
        cell = os.path.join(camp, d)
        if not os.path.isdir(cell):
            continue
        r = _sat.hotel_r(os.path.join(cell, "injected.idf.provenance.txt"))
        vp = os.path.join(cell, "dhw_volume_hourly.csv")
        if r is None or not os.path.isfile(vp) or d not in e_hotel.index:
            continue
        v = pd.read_csv(vp)
        if "dhwvol_hotel" not in v.columns:
            continue
        vol = float(np.nansum(v["dhwvol_hotel"].to_numpy()))
        if vol <= 0:
            continue
        idf_seen = idf_seen or os.path.join(cell, "injected.idf")
        p = d.split("__")
        rows.append({"cell": d, "group": "%s__%s" % (p[1], p[2]), "r": r,
                     "V": vol, "E": float(e_hotel[d])})
    df = pd.DataFrame(rows)
    print("cells: %d" % len(df))

    MAINS = 10.81          # inferred previously from the WaterUse mixing algebra
    rises = target_rises(idf_seen, MAINS)
    print("\n  mains %.2f C; target rises present in the IDF: %s"
          % (MAINS, ", ".join("%.0fF -> %.1f K" % (f, k) for f, k in sorted(rises.items()))))
    dt_min = min(rises.values())
    print("  smallest target rise dT_min = %.1f K  (the most generous benchmark for D2)" % dt_min)

    print("\n  %-18s %3s %10s %12s %8s %10s %10s"
          % ("group", "n", "slope b", "intercept a", "R2", "dT_marg K", "quad term"))
    marg, r2s = [], []
    for g, sub in df.groupby("group"):
        b, a = np.polyfit(sub.V, sub.E, 1)
        pred = a + b * sub.V
        ss = ((sub.E - sub.E.mean()) ** 2).sum()
        r2 = 1.0 - ((sub.E - pred) ** 2).sum() / ss if ss > 0 else float("nan")
        q = np.polyfit(sub.V, sub.E, 2)[0]
        dtm = b / RHO_C
        marg.append(dtm)
        r2s.append(r2)
        print("  %-18s %3d %10.6f %12.1f %8.4f %10.2f %10.2e"
              % (g, len(sub), b, a, r2, dtm, q))

    dt_marg = float(np.mean(marg))
    lin_ok = bool(min(r2s) >= 0.98)
    print("\n  mean implied MARGINAL rise across groups: %.2f K   (%.1f %% of dT_min = %.1f K)"
          % (dt_marg, 100 * dt_marg / dt_min, dt_min))

    print("\n  D4 -- AVERAGE rise vs r (E/V / rho_c):")
    d4 = df.assign(dT_avg=lambda x: (x.E / x.V) / RHO_C).groupby(
        df.r.round(4)).dT_avg.mean()
    for rr, dt in d4.items():
        print("      r = %.4f   dT_avg = %.2f K" % (rr, dt))
    trend = np.polyfit(np.log(df.r), (df.E / df.V) / RHO_C, 1)[0]
    print("      d(dT_avg)/d(ln r) = %.2f K   (negative = each extra m3 served cooler)" % trend)

    d2 = abs(dt_marg - dt_min) / dt_min <= 0.15
    d3 = dt_marg < 0.70 * dt_min
    print("")
    print("  [%s] D1  E vs V linear within group (R2 >= 0.98 in every group)"
          % ("PASS" if lin_ok else "FAIL"))
    print("  [%s] D2  CONSTANT-LOSS -- marginal m3 served at the full target rise"
          % ("CONSTANT-LOSS" if d2 else "not met"))
    print("  [%s] D3  SATURATION -- marginal m3 served at < 70 %% of the target rise"
          % ("SATURATION" if d3 else "not met"))
    if not d2 and not d3:
        print("  [INCONCLUSIVE] marginal rise sits in the declared 70..85 %% grey band")
    sys.exit(0)


if __name__ == "__main__":
    main()
