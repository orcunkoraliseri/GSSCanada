#!/usr/bin/env python3
"""probe_winter_cooling.py — confirm Mechanism A of the resid heating/cooling
dominance investigation (step8_resid_heating_cooling_dominance_investigation.md).

Question: is apartment cooling happening IN WINTER (internal-gain-driven, frozen
24.0C setpoint), or is the huge annual cooling just summer load? Annual aggregates
can't distinguish; this reads raw hourly_meters.csv and breaks heating/cooling
EnergyTransfer down BY MONTH for CZ7A (Winnipeg) 2022 runs.

Reads N sample runs per archetype (MidRise, HighRise = suspects; SingleD = control)
from the campaign tree. Row 0 of hourly_meters.csv = Jan 1 hour 1 (standard E+
annual run, non-leap 365d). Values are J/h.

Run on a COMPUTE node via sbatch (never login). ~15 files, seconds of work.
"""
import os
import glob
import numpy as np
import pandas as pd

CAMP = os.environ.get("STEP8_CAMP_DIR", "/speed-scratch/o_iseri/step8_2split/campaign")
CITY = "Winnipeg_7A"
SCEN = "2022"
ARCHS = ["MidRise", "HighRise", "SingleD"]
N_SAMPLES = 5
J_PER_KWH = 3.6e6

# hour-of-year -> month (non-leap)
_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTH = np.repeat(np.arange(1, 13), np.array(_DAYS) * 24)  # (8760,)


def find_col(df, substr):
    hits = [c for c in df.columns if substr.lower() in c.lower()]
    return hits[0] if hits else None


def monthly_kwh(csv_path):
    df = pd.read_csv(csv_path)
    out = {}
    for label, sub in (("heat", "Heating:EnergyTransfer"), ("cool", "Cooling:EnergyTransfer")):
        col = find_col(df, sub)
        if col is None:
            print(f"    !! no column matching '{sub}' in {csv_path}")
            print(f"       columns: {list(df.columns)}")
            return None
        arr = pd.to_numeric(df[col], errors="coerce").to_numpy()[:8760] / J_PER_KWH
        out[label] = np.array([np.nansum(arr[MONTH == m]) for m in range(1, 13)])
    return out


def main():
    print(f"CAMP={CAMP}  city={CITY}  scenario={SCEN}  n<= {N_SAMPLES}/arch")
    for arch in ARCHS:
        cell_dir = os.path.join(CAMP, f"{arch}__{CITY}")
        runs = sorted(glob.glob(os.path.join(cell_dir, "sample_*", SCEN, "hourly_meters.csv")))
        if not runs:
            print(f"\n[{arch}] NO RUNS FOUND under {cell_dir} — check path")
            continue
        picked = runs[:N_SAMPLES]
        heat = np.zeros(12)
        cool = np.zeros(12)
        n = 0
        for p in picked:
            r = monthly_kwh(p)
            if r is None:
                continue
            heat += r["heat"]
            cool += r["cool"]
            n += 1
        if n == 0:
            print(f"\n[{arch}] no readable runs")
            continue
        heat /= n
        cool /= n
        print(f"\n[{arch}] mean monthly kWh over {n} runs ({os.path.basename(cell_dir)})")
        print("  month:   " + " ".join(f"{m:>8d}" for m in range(1, 13)))
        print("  heating: " + " ".join(f"{v:8.0f}" for v in heat))
        print("  cooling: " + " ".join(f"{v:8.0f}" for v in cool))
        djf = cool[[11, 0, 1]].sum()
        jja = cool[[5, 6, 7]].sum()
        print(f"  cooling DJF={djf:.0f} kWh | JJA={jja:.0f} kWh | DJF share of annual "
              f"cooling={djf / max(cool.sum(), 1e-9):.1%} | annual heat={heat.sum():.0f} "
              f"cool={cool.sum():.0f} kWh")
    print("\nInterpretation: DJF cooling >> 0 in MidRise/HighRise but ~0 in SingleD "
          "confirms Mechanism A (internal-gain-driven winter cooling under the frozen "
          "24.0C setpoint).")


if __name__ == "__main__":
    main()
