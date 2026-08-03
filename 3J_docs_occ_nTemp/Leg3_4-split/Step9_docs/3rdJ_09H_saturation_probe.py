#!/usr/bin/env python3
"""Why do BOTH remaining arm-H predictions miss LOW? Test the plant-saturation candidate.

Arm H scorecard, job 1171763: P3 hotel DHW **+5.21 %** against a predicted +12.4 +/- 2.0, and P4
residential **+7.70 %** against +8..+18. Arm E overshot both (+15.31 / +51.40); with FINDINGS 8 and 9
fixed, arm H undershoots both. The two misses have the same sign and the same shape: the DHW ENERGY
responds LESS than the `r` applied to the draw implies.

There is an obvious suspect already on file: the hotel DHW plant is undersized by construction in
every arm A-H (inherited from ARCH B). `Laundry 30.6gpm 180F` alone demands 577.1 kW against 447.6 kW
installed tower-wide across six hard-sized `WaterHeater:Mixed`; the Y2022 hotel delivered fraction is
36.8 %. If the plant is the binding constraint, scaling the DRAW up by `r` cannot scale DELIVERED
energy by `r`.

That is testable inside arm H alone, with no re-simulation and no reference to arm C, because arm H
is the first arm that reports BOTH quantities per cell:

    volume  <- dhw_volume_hourly.csv   (what T9-13 actually asks the plant for)
    energy  <- agg_annual.csv          (what the plant actually delivered)

Elasticity of each w.r.t. `r`, within (geometry, city) groups so climate and envelope are held fixed.

PRE-REGISTERED, before running:

  S1  VOLUME elasticity w.r.t. r is ~ 1.0 (in [0.90, 1.10]). This is a control, not a finding:
      T9-13's whole specification is that daily volume scales by r. If S1 fails, the saturation
      question is moot because T9-13 is not delivering the draw it claims and THAT is the story.
  S2  SATURATION CONFIRMED if energy elasticity < 0.70 while S1 holds -- the draw scales, the
      delivered energy does not.
  S3  SATURATION REFUTED if energy elasticity is within 0.10 of the volume elasticity. Then the
      plant is not the binding constraint and P3/P4's misses need a different explanation.

S2 and S3 are mutually exclusive and between them cover the outcome space; the gap 0.70..0.90 is
deliberately left as "partial / inconclusive" rather than being assigned to whichever answer is
convenient.

    python 3rdJ_09H_saturation_probe.py <campaign_dir> <agg_annual.csv>
"""
import os
import re
import sys

import numpy as np
import pandas as pd


def hotel_r(prov_path):
    """Effective annual r for the hotel channel: (5*r_wd + 2*r_we)/7, or 1.0 if never injected.

    A cell with no `t9_13 hotel` line did not have hotel injected (Y2005/10/15 have no hotel
    channel, Default_NECB has none at all), so its hotel schedules are the untouched prototype --
    which is r = 1.0 exactly, by definition, not a missing value.
    """
    if not os.path.isfile(prov_path):
        return None
    wds, wes = [], []
    for line in open(prov_path, errors="replace"):
        if not line.startswith("t9_13 hotel "):
            continue
        m = re.search(r"r_wd=([0-9.]+)\s+r_we=([0-9.]+)", line)
        if m:
            wds.append(float(m.group(1)))
            wes.append(float(m.group(2)))
    if not wds:
        return 1.0
    return (5 * np.mean(wds) + 2 * np.mean(wes)) / 7.0


def elasticity(x, y):
    """d log y / d log x by OLS. Returns (slope, n, r2)."""
    lx, ly = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    ok = np.isfinite(lx) & np.isfinite(ly)
    lx, ly = lx[ok], ly[ok]
    if len(lx) < 3 or lx.std() < 1e-9:
        return float("nan"), len(lx), float("nan")
    b, a = np.polyfit(lx, ly, 1)
    pred = a + b * lx
    ss = ((ly - ly.mean()) ** 2).sum()
    r2 = 1.0 - ((ly - pred) ** 2).sum() / ss if ss > 0 else float("nan")
    return float(b), len(lx), float(r2)


def main():
    camp, agg_p = sys.argv[1], sys.argv[2]
    agg = pd.read_csv(agg_p)
    agg["energy_GJ"] = agg["energy_J"] / 1e9
    e_hotel = (agg[(agg.channel == "hotel") & (agg.end_use == "dhw")]
               .groupby("cell_tag")["energy_GJ"].sum())

    rows = []
    for d in sorted(os.listdir(camp)):
        cell = os.path.join(camp, d)
        if not os.path.isdir(cell):
            continue
        r = hotel_r(os.path.join(cell, "injected.idf.provenance.txt"))
        vp = os.path.join(cell, "dhw_volume_hourly.csv")
        if r is None or not os.path.isfile(vp):
            continue
        v = pd.read_csv(vp)
        if "dhwvol_hotel" not in v.columns:
            continue
        vol = float(np.nansum(v["dhwvol_hotel"].to_numpy()))
        if vol <= 0 or d not in e_hotel.index:
            continue
        parts = d.split("__")
        rows.append({"cell": d, "scenario": parts[0],
                     "group": "%s__%s" % (parts[1], parts[2]) if len(parts) > 2 else "?",
                     "r": r, "volume_m3": vol, "energy_GJ": float(e_hotel[d])})
    df = pd.DataFrame(rows)
    print("cells with hotel volume + energy + r: %d" % len(df))
    if df.empty:
        sys.exit(2)

    print("\n  r_hotel range %.4f .. %.4f over %d distinct values"
          % (df.r.min(), df.r.max(), df.r.nunique()))
    print("\n  %-22s %4s %8s %8s %10s %10s" % ("group", "n", "r_min", "r_max", "vol_elast", "eng_elast"))
    ve_all, ee_all = [], []
    for g, sub in df.groupby("group"):
        bv, nv, r2v = elasticity(sub.r, sub.volume_m3)
        be, ne, r2e = elasticity(sub.r, sub.energy_GJ)
        ve_all.append(bv)
        ee_all.append(be)
        print("  %-22s %4d %8.4f %8.4f %10.4f %10.4f   (R2 vol %.3f / eng %.3f)"
              % (g, len(sub), sub.r.min(), sub.r.max(), bv, be, r2v, r2e))

    # Pooled: de-mean within group so the group fixed effect cannot drive the slope.
    d2 = df.copy()
    for col in ("r", "volume_m3", "energy_GJ"):
        d2["l" + col] = np.log(d2[col])
        d2["l" + col] -= d2.groupby("group")["l" + col].transform("mean")
    bv = np.polyfit(d2.lr, d2.lvolume_m3, 1)[0]
    be = np.polyfit(d2.lr, d2.lenergy_GJ, 1)[0]
    print("\n  POOLED (within-group de-meaned, n=%d):  volume elasticity %.4f   energy elasticity %.4f"
          % (len(d2), bv, be))

    s1 = 0.90 <= bv <= 1.10
    s2 = (be < 0.70) and s1
    s3 = abs(be - bv) <= 0.10
    print("")
    print("  [%s] S1  volume elasticity w.r.t. r is ~1.0 (control: T9-13 delivers the draw). got %.4f"
          % ("PASS" if s1 else "FAIL", bv))
    print("  [%s] S2  SATURATION CONFIRMED -- energy elasticity < 0.70 while volume scales. got %.4f"
          % ("CONFIRMED" if s2 else "not met", be))
    print("  [%s] S3  SATURATION REFUTED -- energy tracks volume within 0.10. gap %.4f"
          % ("REFUTED" if s3 else "not met", abs(be - bv)))
    if not s2 and not s3:
        print("  [INCONCLUSIVE] energy elasticity %.4f sits in the pre-declared 0.70..0.90 grey band"
              % be)

    print("\n  implied delivered fraction of the marginal draw: %.3f" % (be / bv if bv else float("nan")))
    print("\n  per-cell detail, sorted by r:")
    print("  %-34s %8s %12s %11s %10s" % ("cell", "r", "volume_m3", "energy_GJ", "GJ per m3"))
    for _, r_ in df.sort_values("r").iterrows():
        print("  %-34s %8.4f %12.1f %11.1f %10.5f"
              % (r_.cell, r_.r, r_.volume_m3, r_.energy_GJ, r_.energy_GJ / r_.volume_m3))
    sys.exit(0)


if __name__ == "__main__":
    main()
