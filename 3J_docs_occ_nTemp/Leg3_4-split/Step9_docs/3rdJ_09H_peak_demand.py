#!/usr/bin/env python3
"""How much DHW capacity does this tower actually need? Measured from arm H's own hourly volumes.

Context: autosizing the six `WaterHeater:Mixed` is NOT a flag. EnergyPlus refuses outright --
`SizeTankForSupplySide: ... requested sizing for max capacity but entered Recovery Time is zero`
(job 1171802, all 3 cells, fatal in 20 s). `WaterHeater:Sizing` mode is `PeakDraw` with
`Time for Tank Recovery = 0`, and under PeakDraw that field is what sizes the burner. So a recovery
time has to be CHOSEN, which is a design decision, not a mechanical fix.

This script prices that decision. It reports what the plant is actually being asked for, so the
options can be compared against a measurement instead of a convention.

Reported per cell:
  * peak HOURLY delivered volume (m3/h), tower-wide and per channel
  * the continuous power that volume implies at the two target rises present in the IDF
    (140F -> 49.2 K and 180F -> 71.4 K over 10.81 C mains)
  * the same at the 99th and 95th percentile hour, because sizing to the single worst hour of 8760
    is a different design stance from sizing to the busy season
  * installed capacity for comparison: 5 x 87,921.3 W + 7,999.96 W = 447,606.6 W

No gate, no verdict -- this is an input to a decision.

    python 3rdJ_09H_peak_demand.py <cell_dir> [<cell_dir> ...]
"""
import os
import sys

import numpy as np
import pandas as pd

RHO_C = 4.184e6            # J per m3 per K
INSTALLED_W = 5 * 87921.3210516667 + 7999.96100249115
DT_140 = 49.2
DT_180 = 71.4
CHANNELS = ["office", "retail", "hotel", "residential",
            "residential_common", "service_MEP", "unassigned"]


def kw(vol_m3_per_h, dt):
    """Continuous kW to raise vol m3 by dt K over one hour."""
    return vol_m3_per_h * RHO_C * dt / 3600.0 / 1000.0


def run(cell):
    name = os.path.basename(cell.rstrip("/"))
    p = os.path.join(cell, "dhw_volume_hourly.csv")
    if not os.path.isfile(p):
        print("  SKIP %s (no dhw_volume_hourly.csv)" % name)
        return
    v = pd.read_csv(p)
    cols = ["dhwvol_" + c for c in CHANNELS if "dhwvol_" + c in v.columns]
    tot = v[cols].sum(axis=1).to_numpy(dtype=float)

    print("=" * 88)
    print("CELL %s" % name)
    print("=" * 88)
    print("  annual volume %.1f m3 over %d hours" % (np.nansum(tot), len(tot)))
    print("\n  %-14s %12s %14s %14s" % ("hour basis", "vol m3/h", "kW @ 49.2K", "kW @ 71.4K"))
    for label, val in (("peak (max)", np.nanmax(tot)),
                       ("99th pct", float(np.nanpercentile(tot, 99))),
                       ("95th pct", float(np.nanpercentile(tot, 95))),
                       ("mean", float(np.nanmean(tot)))):
        print("  %-14s %12.4f %14.1f %14.1f" % (label, val, kw(val, DT_140), kw(val, DT_180)))

    print("\n  installed capacity: %.1f kW  (5 x 87.9 + 8.0)" % (INSTALLED_W / 1000.0))
    pk = float(np.nanmax(tot))
    print("  peak-hour requirement / installed:  %.2f x  (at 49.2 K)   %.2f x  (at 71.4 K)"
          % (kw(pk, DT_140) / (INSTALLED_W / 1000.0), kw(pk, DT_180) / (INSTALLED_W / 1000.0)))
    p99 = float(np.nanpercentile(tot, 99))
    print("  99th-pct requirement / installed:   %.2f x  (at 49.2 K)   %.2f x  (at 71.4 K)"
          % (kw(p99, DT_140) / (INSTALLED_W / 1000.0), kw(p99, DT_180) / (INSTALLED_W / 1000.0)))

    print("\n  peak hourly volume by channel (m3/h), and each channel's share of the tower peak:")
    ih = int(np.nanargmax(tot))
    for c in CHANNELS:
        col = "dhwvol_" + c
        if col not in v.columns:
            continue
        arr = v[col].to_numpy(dtype=float)
        if np.nansum(arr) <= 0:
            continue
        print("    %-20s own peak %8.4f   at the tower peak hour %8.4f  (%5.1f %%)"
              % (c, np.nanmax(arr), arr[ih], 100.0 * arr[ih] / tot[ih] if tot[ih] else 0.0))
    print("")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    for d in sys.argv[1:]:
        run(d)


if __name__ == "__main__":
    main()
