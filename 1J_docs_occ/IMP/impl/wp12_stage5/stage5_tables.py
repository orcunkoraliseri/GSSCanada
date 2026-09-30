"""Stage 5 (1J revision): reported energy numbers from the 30 random draws.

Reads raw/b{block}_RC{n}_per_draw.csv (copied from Speed stage4/draws/block_*/NUS_RC*/per_draw_eui.csv)
and raw/stoprule_block_6.csv (the scorer's own output). Rules applied (RESUME section 7.2):
  - every simulated number = mean over draws 1-30 with its 95 % t-interval;
  - Default numbers come from the Default run (draw 0), never from a draw;
  - a difference is called a difference only if its own 95 % interval excludes zero.
Year-to-year differences use Welch's interval (draws of different years are independent households).
Deviation from Default: Default is one deterministic run, so the interval of (mean - Default) is the
interval of the mean shifted by Default.
Gate S5.0: the heating/cooling means and half-widths here must equal the scorer's block-6 file.
"""
import glob
import itertools
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

LABEL = {"NUS_RC1": "RC-R", "NUS_RC2": "RC-D", "NUS_RC3": "RC-T",
         "NUS_RC4": "RC-MR2", "NUS_RC5": "RC-MR3", "NUS_RC6": "RC-HR2"}
YEARS = ["2005", "2010", "2015", "2022", "2025"]
END_USES = ["Heating", "Cooling", "Electric Equipment", "Water Systems", "Interior Lighting"]

# (bj) corrected annual energy from WP15 (peak-demand defect removed); the old per_draw files are contaminated.
df = pd.read_csv(os.path.join(HERE, "..", "wp15", "out", "annual_enduse_totals.csv"))
df = df[df.end_use.isin(END_USES)]
df["year"] = df["year"].astype(str)

default = (df[df.year == "Default"].drop_duplicates(["neighbourhood", "end_use"])
           .set_index(["neighbourhood", "end_use"])["value"])
# every block re-runs the Default; all copies must agree (deterministic run)
dspread = df[df.year == "Default"].groupby(["neighbourhood", "end_use"])["value"].agg(lambda v: v.max() - v.min())
print(f"S5.D Default copies max spread across blocks: {dspread.max():.6f}")

draws = df[(df.year != "Default") & (df.draw >= 1) & (df.draw <= 30)]
dup = draws.duplicated(["neighbourhood", "year", "end_use", "draw"]).sum()
print(f"S5.N duplicate draw rows: {dup}")


def tint(v):
    v = np.asarray(v, float)
    n = len(v)
    m = v.mean()
    sd = v.std(ddof=1)
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    return n, m, sd, half


rows = []
for (nb, yr, eu), g in draws.groupby(["neighbourhood", "year", "end_use"]):
    n, m, sd, half = tint(g["value"])
    d = default[(nb, eu)]
    rows.append(dict(nu=LABEL[nb], model=nb, year=yr, end_use=eu, n=n, mean=m, sd=sd, half=half,
                     half_pct=100 * half / m, default=d,
                     dev_pct=100 * (m - d) / d, dev_lo=100 * (m - half - d) / d, dev_hi=100 * (m + half - d) / d))
cells = pd.DataFrame(rows)
cells["dev_excl0"] = (cells.dev_lo > 0) | (cells.dev_hi < 0)
cells.to_csv(os.path.join(OUT, "cells_all_enduses.csv"), index=False)

# Gate S5.0: 30 draws in every cell (the scorer file holds contaminated values, so no value comparison)
assert (cells.n == 30).all() and len(cells) == 6 * 5 * len(END_USES), "S5.0 cell count"
print(f"S5.0 cells={len(cells)} all n=30 -> PASS")
# Old scorer file, for the record only: same cells, contaminated values
sc = pd.read_csv(os.path.join(RAW, "stoprule_block_6.csv"))
sc[["model", "year", "end_use"]] = sc["cell"].str.split("/", expand=True)
chk = sc.merge(cells, on=["model", "year", "end_use"], suffixes=("_sc", ""))
dm = (chk["mean_sc"] - chk["mean"]).abs().max()
dh = (chk["half_sc"] - chk["half"]).abs().max()
print(f"(record) old contaminated scorer vs corrected: max|dmean|={dm:.2f} kWh/m2 (expected large)")

# Year-to-year differences (heating, cooling), Welch interval
drows = []
for (nb, eu), g in draws[draws.end_use.isin(["Heating", "Cooling"])].groupby(["neighbourhood", "end_use"]):
    for a, b in itertools.combinations(YEARS, 2):
        va = g[g.year == a]["value"].to_numpy(float)
        vb = g[g.year == b]["value"].to_numpy(float)
        diff = vb.mean() - va.mean()
        sa, sb = va.var(ddof=1) / len(va), vb.var(ddof=1) / len(vb)
        dfw = (sa + sb) ** 2 / (sa ** 2 / (len(va) - 1) + sb ** 2 / (len(vb) - 1))
        half = stats.t.ppf(0.975, dfw) * np.sqrt(sa + sb)
        drows.append(dict(nu=LABEL[nb], end_use=eu, from_year=a, to_year=b, diff=diff, lo=diff - half,
                          hi=diff + half, diff_pct=100 * diff / va.mean(), excl0=(diff - half > 0) or (diff + half < 0)))
diffs = pd.DataFrame(drows)
diffs.to_csv(os.path.join(OUT, "year_differences.csv"), index=False)

# Compact tables for the paper
hc = cells[cells.end_use.isin(["Heating", "Cooling"])].copy()
order = list(LABEL.values())
hc["nu"] = pd.Categorical(hc["nu"], order, ordered=True)
hc = hc.sort_values(["end_use", "nu", "year"])
hc.to_csv(os.path.join(OUT, "heating_cooling_cells.csv"), index=False)

print("\n== Deviation from Default (%), mean [95% interval], heating and cooling")
for eu in ["Heating", "Cooling"]:
    sub = hc[hc.end_use == eu]
    print(f"-- {eu}")
    for nu in order:
        s = sub[sub.nu == nu]
        line = "  ".join(f"{r.year}:{r.dev_pct:+.1f}[{r.dev_lo:+.1f},{r.dev_hi:+.1f}]" for r in s.itertuples())
        print(f"{nu:7s} D={s['default'].iloc[0]:7.2f}  {line}")
    print(f"   range of mean deviation: {sub.dev_pct.min():+.1f} to {sub.dev_pct.max():+.1f}; "
          f"cells whose interval excludes 0: {sub.dev_excl0.sum()}/{len(sub)}")

print("\n== Achieved precision (half-width % of mean), heating/cooling")
print(f"max {hc.half_pct.max():.2f}  median {hc.half_pct.median():.2f}  cells <=1 %: {(hc.half_pct <= 1).sum()}/60")

print("\n== Year-to-year differences whose interval excludes zero (of 10 pairs x 6 NUs per end use)")
for eu in ["Heating", "Cooling"]:
    s = diffs[diffs.end_use == eu]
    print(f"{eu}: {s.excl0.sum()}/{len(s)}")
    print(s.groupby(["from_year", "to_year"]).excl0.sum().to_string())

print("\n== Other end uses: deviation from Default (%) range of means")
for eu in ["Electric Equipment", "Water Systems", "Interior Lighting"]:
    s = cells[cells.end_use == eu]
    print(f"{eu}: {s.dev_pct.min():+.1f} to {s.dev_pct.max():+.1f}; excl0 {s.dev_excl0.sum()}/{len(s)}")
