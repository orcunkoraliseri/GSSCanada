"""P10R Speed-vs-local check: the local win32 test cell against the SAME cell run on Speed.

Per numeric column of channel_hourly.csv and hourly_meters.csv: annual sum relative difference and max
hourly |diff| / column max. PASS iff every annual |rel diff| <= --tol-annual AND every hourly value
<= --tol-hourly, where the tolerances are the cross-platform difference V3b measured (same IDF, linux
Speed vs win32 frozen: "U vs frozen", IMP/V3_design_and_runs.md). Without tolerances -> NOT_EVALUABLE.
Control: the same comparison of the local test cell against the FROZEN cell must FAIL (different inputs).

    py -3 p10r_speed_vs_local.py LOCAL_CELL SPEED_CELL [--tol-annual X --tol-hourly Y]
"""
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("local"); ap.add_argument("speed")
ap.add_argument("--tol-annual", type=float); ap.add_argument("--tol-hourly", type=float)
a = ap.parse_args()
worst_a = worst_h = 0.0
for f in ("channel_hourly.csv", "hourly_meters.csv"):
    x, y = pd.read_csv(Path(a.local) / f), pd.read_csv(Path(a.speed) / f)
    cols = [c for c in x.columns if c in y.columns and pd.api.types.is_numeric_dtype(x[c])]
    for c in cols:
        sx, sy = float(x[c].sum()), float(y[c].sum())
        ra = abs(sy - sx) / abs(sx) if sx else (0.0 if sy == 0 else float("inf"))
        mx = float(np.abs(x[c]).max())
        rh = float(np.abs(y[c].to_numpy() - x[c].to_numpy()).max() / mx) if mx else 0.0
        worst_a, worst_h = max(worst_a, ra), max(worst_h, rh)
        if ra > 1e-9 or rh > 1e-9:
            print(f"  {f}:{c}: annual rel {ra:.3e}  hourly rel max {rh:.3e}")
print(f"worst annual rel diff {worst_a:.3e}; worst hourly rel diff {worst_h:.3e}")
if a.tol_annual is None or a.tol_hourly is None:
    print("VERDICT: NOT_EVALUABLE (no V3b tolerance given)"); sys.exit(2)
ok = worst_a <= a.tol_annual and worst_h <= a.tol_hourly
print(f"VERDICT: {'PASS' if ok else 'FAIL'} (tol annual {a.tol_annual:g}, hourly {a.tol_hourly:g})")
sys.exit(0 if ok else 1)
