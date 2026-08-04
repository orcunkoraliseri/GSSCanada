#!/usr/bin/env python3
"""R3/R4 for the uniform plant resize: does the burner stop mediating the occupancy signal?

The 3-cell resize probe (job 1171807) printed TOWER-WIDE totals. R3's threshold was written against
a HOTEL-SCOPED elasticity (arm H: 0.5617, job 1171767), so the two are not comparable and R3 cannot
be read off that output. This script re-scopes both sides through the campaign's own channel mapping.

It does NOT re-implement that mapping. It imports `_write_dhw_hourly_csv` from the campaign driver,
which resolves every WaterUse:Equipment to a channel by two IDF-read rules (Space name -> Tag-2
census, then prototype token in the Flow Rate Fraction Schedule Name). Re-deriving it here would be
a second source of truth for the one quantity the verdict rests on.

PRE-REGISTERED, and R0 comes first for a reason:

  R0  CONTROL, MUST PASS BEFORE R3 IS QUOTED -- the hotel-scoped arm-H elasticity recomputed here
      reproduces the saturation probe's 0.5617 to within 0.02. If it does not, this script's
      estimator is not the one the 0.90 threshold was written against, and R3's number means
      nothing. A near-miss is recorded, not absorbed.
  R3  DECISIVE -- hotel DHW ENERGY elasticity w.r.t. r rises to >= 0.90 under the resized plant.
  R3v CONTROL on R3 -- hotel DHW VOLUME elasticity is ~1.0 in BOTH arms (the draw is
      schedule-driven and cannot know about the burner). If volume elasticity is not ~1.0, the
      energy elasticity is not measuring plant mediation at all.
  R4  The implied MARGINAL rise (OLS slope of hotel E on hotel V across the three cells, / rho*c)
      rises from arm H's 22.66 K toward the 49.2 K target.

Note on n: three cells is three points. The elasticity is a 2-parameter fit on 3 points, so it is
reported with its R^2 and the point-to-point slopes, not as a lone number.

    python 3rdJ_09H_resize_elasticity.py <armH_cell_dir> <resize_out_dir> [<pair> ...]
"""
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.environ.get("REPO", "."))

RHO_C = 4.184e6
ARM_H_ELASTICITY = 0.5617      # saturation probe, job 1171767 -- the number R0 must reproduce
ARM_H_MARGINAL_K = 22.66       # discriminator, job 1171767
R0_TOL = 0.02
R3_THRESHOLD = 0.90
TARGET_K = 49.2


def hotel_r(cell_dir):
    """Mean hotel draw multiplier r = (5*r_wd + 2*r_we)/7, read off the cell's own provenance.

    The first version of this function guessed three filenames, none of which was the real one
    (`injected.idf.provenance.txt`), and returned 1.0 when it found nothing -- so all three cells
    came back r = 1.0, the regressor had zero variance, and the fit blew up in LAPACK (job 1171812).
    That crash was luck. Had two cells matched and one not, the default would have produced a
    plausible wrong elasticity in silence. So there is NO default here any more: a cell whose r
    cannot be read is a hard refusal, not a 1.0.

    r is carried in the injected schedule names, `..._r{r_wd*1000:04d}w{r_we*1000:04d}_...`, which
    is the injector's own record of what it wrote rather than a second-hand table.
    """
    p = os.path.join(cell_dir, "injected.idf.provenance.txt")
    if not os.path.isfile(p):
        raise SystemExit("REFUSING: no provenance at %s -- cannot establish r" % p)
    txt = open(p, errors="replace").read()
    toks = set(re.findall(r"MXU_Hotel_DHWv2_\S*?_r(\d{4})w(\d{4})", txt))
    if not toks:
        raise SystemExit("REFUSING: no hotel r token in %s -- cannot establish r" % p)
    if len(toks) > 1:
        raise SystemExit("REFUSING: hotel schedules disagree on r in %s: %s" % (p, sorted(toks)))
    wd, we = (int(v) / 1000.0 for v in toks.pop())
    return (5.0 * wd + 2.0 * we) / 7.0


def hotel_series(sql_path, idf_path, idd, tmp_prefix):
    """(hotel annual volume m3, hotel annual energy J) via the driver's own channel resolution."""
    drv = _load_driver()
    out = {}
    for var, pref, col in ((drv.DHW_VOLUME_VARIABLE, "dhwvol", "dhwvol_hotel"),
                           (drv.DHW_VARIABLE, "dhw", "dhw_hotel")):
        csv = "%s_%s.csv" % (tmp_prefix, pref)
        drv._write_dhw_hourly_csv(sql_path, idf_path, idd, csv, variable=var, col_prefix=pref)
        out[pref] = float(pd.read_csv(csv)[col].sum())
    return out["dhwvol"], out["dhw"]


def _load_driver():
    import importlib.util
    repo = os.environ.get("REPO", ".")
    path = os.path.join(repo, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs",
                        "3rdJ_08P_probe_driver.py")
    spec = importlib.util.spec_from_file_location("probe_driver", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def elasticity(x, y):
    """d log y / d log x by OLS, with R^2. Returns (slope, r2)."""
    lx, ly = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    s, b = np.polyfit(lx, ly, 1)
    pred = s * lx + b
    ss_res = float(np.sum((ly - pred) ** 2))
    ss_tot = float(np.sum((ly - ly.mean()) ** 2))
    return float(s), (1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"))


def main():
    idd = os.environ["EPLUS_IDD"]
    tmp = os.environ.get("TMPDIR", ".")
    rows = []
    for pair in sys.argv[1:]:
        cell, rdir = pair.split(":", 1)
        name = os.path.basename(cell.rstrip("/"))
        r = hotel_r(cell)
        Vh, Eh = hotel_series(os.path.join(cell, "run", "eplusout.sql"),
                              os.path.join(cell, "injected.idf"), idd,
                              os.path.join(tmp, name + "_H"))
        Vr, Er = hotel_series(os.path.join(rdir, "run", "eplusout.sql"),
                              os.path.join(rdir, "injected_resized.idf"), idd,
                              os.path.join(tmp, name + "_R"))
        rows.append(dict(name=name, r=r, Vh=Vh, Eh=Eh, Vr=Vr, Er=Er))
        print("  %-24s r=%.4f | armH V=%9.1f E=%8.1f GJ dT=%6.2f K | resized V=%9.1f E=%8.1f GJ "
              "dT=%6.2f K" % (name, r, Vh, Eh / 1e9, (Eh / Vh) / RHO_C,
                              Vr, Er / 1e9, (Er / Vr) / RHO_C))

    rows.sort(key=lambda d: d["r"])
    r = [d["r"] for d in rows]
    # An elasticity w.r.t. a regressor that does not vary is not a weak estimate, it is undefined.
    # Job 1171812 reached LAPACK with three identical r values and died there; the guard belongs
    # here, in the script's own terms, not in a linear-algebra backend's error message.
    if len(set(r)) < 2:
        raise SystemExit("REFUSING: r is constant across the cells (%s) -- no elasticity exists. "
                         "Check the provenance reader before reading anything below." % r)
    eH, r2H = elasticity(r, [d["Eh"] for d in rows])
    eR, r2R = elasticity(r, [d["Er"] for d in rows])
    vH, _ = elasticity(r, [d["Vh"] for d in rows])
    vR, _ = elasticity(r, [d["Vr"] for d in rows])
    mH = np.polyfit([d["Vh"] for d in rows], [d["Eh"] for d in rows], 1)[0] / RHO_C
    mR = np.polyfit([d["Vr"] for d in rows], [d["Er"] for d in rows], 1)[0] / RHO_C

    print("\n" + "=" * 88)
    print("  hotel ENERGY elasticity   arm H %6.4f (R2 %.3f)   resized %6.4f (R2 %.3f)"
          % (eH, r2H, eR, r2R))
    print("  hotel VOLUME elasticity   arm H %6.4f              resized %6.4f" % (vH, vR))
    print("  marginal delivered rise   arm H %6.2f K            resized %6.2f K   (target %.1f K)"
          % (mH, mR, TARGET_K))
    print("=" * 88)

    r0 = abs(eH - ARM_H_ELASTICITY) <= R0_TOL
    print("\n  [%s] R0  CONTROL -- arm-H hotel elasticity reproduces the probe's %.4f: got %.4f "
          "(|d| = %.4f, tol %.2f)"
          % ("PASS" if r0 else "FAIL", ARM_H_ELASTICITY, eH, abs(eH - ARM_H_ELASTICITY), R0_TOL))
    r3v = abs(vH - 1.0) <= 0.05 and abs(vR - 1.0) <= 0.05
    print("  [%s] R3v CONTROL -- hotel VOLUME elasticity ~1.0 in both arms (%.4f / %.4f)"
          % ("PASS" if r3v else "FAIL", vH, vR))
    r3 = eR >= R3_THRESHOLD
    print("  [%s] R3  DECISIVE -- resized hotel ENERGY elasticity >= %.2f: got %.4f"
          % ("PASS" if r3 else "FAIL", R3_THRESHOLD, eR))
    r4 = mR > mH
    print("  [%s] R4  marginal delivered rise moves up: %.2f -> %.2f K (%.1f %% of target)"
          % ("PASS" if r4 else "FAIL", mH, mR, 100.0 * mR / TARGET_K))
    if not r0:
        print("\n  >>> R0 FAILED. The estimator here is NOT the one the 0.90 threshold was written")
        print("      against, so R3 above is not the pre-registered test. Reconcile before quoting.")
    if not r3:
        print("\n  >>> R3 FAILED at K = 3.0. The resize is insufficient; K must be revisited BEFORE")
        print("      any 56-cell campaign. Do NOT widen the threshold.")


if __name__ == "__main__":
    main()
