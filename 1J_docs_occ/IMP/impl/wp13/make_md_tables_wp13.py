"""Markdown tables for the R1 manuscript from WP13 outputs (no value typed by hand)."""
import os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
q = pd.read_csv(os.path.join(OUT, "quebec_vs_canada.csv"))
rows = ["| Cycle | Day | Occupied hours, Canada | Quebec | Quebec − Canada (95 % interval) | Daytime fraction, Canada | Quebec | Quebec − Canada (95 % interval) |",
        "|:--|:--|--:|--:|--:|--:|--:|--:|"]
for r in q.itertuples():
    rows.append(f"| {r.year} | {r.day_type} | {r.canada_occupied_hours:.2f} | {r.quebec_occupied_hours:.2f} | {r.diff_occupied_hours:+.2f} ({r.boot_lo_hours:+.2f}, {r.boot_hi_hours:+.2f}) | "
                f"{r.canada_daytime_fraction:.3f} | {r.quebec_daytime_fraction:.3f} | {r.diff_daytime_fraction:+.3f} ({r.boot_lo_daytime:+.3f}, {r.boot_hi_daytime:+.3f}) |")
open(os.path.join(OUT, "table_quebec.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
t = pd.read_csv(os.path.join(OUT, "tier_shares.csv"))
t["tn"] = t.tier.str.slice(0, 1).astype(int)
rows = ["| Cycle | Weekday: Tier 1 | Tier 2 | Tier 3 | Tier 4 | Weekend: Tier 1 | Tier 2 | Tier 3 | Tier 4 | Persons |", "|:--|" + "--:|" * 9]
for y in [2005, 2010, 2015, 2022, 2025]:
    cells = []
    for a in ["weekday", "weekend"]:
        s = t[(t.year == y) & (t.assignment == a)].set_index("tn").share_pct
        cells += [f"{s.get(i, 0):.1f}" for i in [1, 2, 3, 4]]
    n = t[(t.year == y) & (t.assignment == "weekday")].n_total.iloc[0]
    rows.append(f"| {y} | " + " | ".join(cells) + f" | {n:,} |")
open(os.path.join(OUT, "table_tiers.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
m = pd.read_csv(os.path.join(OUT, "metrics_by_year_region.csv"), dtype={"year": str})
m = m[m.region.isin(["Canada", "Default"])]
rows = ["| | Default | 2005 | 2010 | 2015 | 2022 | 2025 |", "|:--|--:|--:|--:|--:|--:|--:|"]
Y = ["Default", "2005", "2010", "2015", "2022", "2025"]
def g(col, dt, fmt):
    s = m[m.day_type == dt].set_index("year")[col]
    return " | ".join(fmt.format(s[y]) if pd.notna(s[y]) else "—" for y in Y)
rows.append("| Occupied hours, weekday (h) | " + g("occupied_hours", "Weekday", "{:.1f}") + " |")
rows.append("| Occupied hours, weekend (h) | " + g("occupied_hours", "Weekend", "{:.1f}") + " |")
rows.append("| Daytime fraction 09:00–17:00, weekday | " + g("daytime_fraction", "Weekday", "{:.2f}") + " |")
rows.append("| Daytime fraction 09:00–17:00, weekend | " + g("daytime_fraction", "Weekend", "{:.2f}") + " |")
rows.append("| Mean metabolic rate per person at home, weekday (W) | 95 | " + " | ".join(f"{v:.0f}" for v in m[(m.day_type == 'Weekday') & (m.year != 'Default')].set_index('year').loc[Y[1:], 'met_mean_occ_pos']) + " |")
rows.append("| Households | — | " + " | ".join(f"{int(v):,}" for v in m[(m.day_type == 'Weekday') & (m.year != 'Default')].set_index('year').loc[Y[1:], 'n_households']) + " |")
open(os.path.join(OUT, "table_occupancy.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
for f in ["table_occupancy.md", "table_quebec.md", "table_tiers.md"]:
    print(open(os.path.join(OUT, f), encoding="utf-8").read())
