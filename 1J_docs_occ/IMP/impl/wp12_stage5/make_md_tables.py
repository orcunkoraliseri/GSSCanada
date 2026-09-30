"""Markdown tables for the R1 manuscript from out/*.csv (no value typed by hand)."""
import os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
c = pd.read_csv(os.path.join(HERE, "out", "cells_all_enduses.csv"), dtype={"year": str})
NUS = ["RC-R", "RC-D", "RC-T", "RC-MR2", "RC-MR3", "RC-HR2"]
YEARS = ["2005", "2010", "2015", "2022", "2025"]
out = []
out.append("| NU | Default heating (kWh/m²) | Default cooling (kWh/m²) | " + " | ".join(f"Heating {y}" for y in YEARS) + " |")
out.append("|" + "---|" * (3 + len(YEARS)))
def cell(r):
    return f"{r.dev_pct:+.1f} ({r.dev_lo:+.1f}, {r.dev_hi:+.1f})"
for eu in ["Heating", "Cooling"]:
    pass
rows = []
hdr = "| NU | End use | Default (kWh/m²) | " + " | ".join(YEARS) + " |"
rows.append(hdr)
rows.append("|:--|:--|--:|" + "--:|" * len(YEARS))
for nu in NUS:
    for eu in ["Heating", "Cooling"]:
        s = c[(c.nu == nu) & (c.end_use == eu)].set_index("year")
        rows.append(f"| {nu} | {eu} | {s['default'].iloc[0]:.1f} | " + " | ".join(cell(s.loc[y]) for y in YEARS) + " |")
open(os.path.join(HERE, "out", "table_deviation.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
# absolute means with half-width, appendix table
rows = ["| NU | End use | Default | " + " | ".join(YEARS) + " |", "|:--|:--|--:|" + "--:|" * len(YEARS)]
for nu in NUS:
    for eu in ["Heating", "Cooling", "Electric Equipment", "Water Systems", "Interior Lighting"]:
        s = c[(c.nu == nu) & (c.end_use == eu)].set_index("year")
        rows.append(f"| {nu} | {eu} | {s['default'].iloc[0]:.2f} | " + " | ".join(f"{s.loc[y,'mean']:.2f} ± {s.loc[y,'half']:.2f}" for y in YEARS) + " |")
open(os.path.join(HERE, "out", "table_absolute_appendix.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
# summary numbers for prose
hc = c[c.end_use.isin(["Heating", "Cooling"])]
houses = hc[hc.nu.isin(NUS[:3])]; apts = hc[hc.nu.isin(NUS[3:])]
for name, g in [("houses", houses), ("apartments", apts)]:
    for eu in ["Heating", "Cooling"]:
        s = g[g.end_use == eu]
        print(name, eu, f"{s.dev_pct.min():+.1f} to {s.dev_pct.max():+.1f}", "excl0", int(s.dev_excl0.sum()), "/", len(s))
        for y in YEARS:
            t = s[s.year == y]
            print("   ", y, f"{t.dev_pct.min():+.1f} to {t.dev_pct.max():+.1f}")
print(open(os.path.join(HERE, "out", "table_deviation.md"), encoding="utf-8").read())
# peak cooling table (peaks_tables.py must have run)
pk = pd.read_csv(os.path.join(HERE, "out", "peak_cooling.csv"), dtype={"year": str})
rows = ["| NU | Default peak (W/m²) | Time of Default peak | " + " | ".join(YEARS) + " |", "|:--|--:|:--|" + "--:|" * len(YEARS)]
for nu in NUS:
    s = pk[pk.nu == nu].set_index("year")
    t = s["default_time"].iloc[0].replace("-", " ", 1).title().replace("-", ", ")
    rows.append(f"| {nu} | {s['default'].iloc[0]:.1f} | {t} | " + " | ".join(cell(s.loc[y]) for y in YEARS) + " |")
open(os.path.join(HERE, "out", "table_peak.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
print(open(os.path.join(HERE, "out", "table_peak.md"), encoding="utf-8").read())
