"""Old-vs-new table for Section 4.1: every number the paper states (1st_Occ_Journal.md lines 173, 179, 183, 189,
193, 199, 203) beside the value recomputed here with the same definition. Reads only the CSVs of this job.
Usage: python build_old_vs_new.py --dir <outdir>"""
import argparse, os
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
a = ap.parse_args()
D = a.dir


def rd(f):
    p = os.path.join(D, f)
    if os.path.exists(p):
        return pd.read_csv(p)
    print("missing", f)
    return None


M, H, F13, ACT, MET = rd("metrics_by_year_region.csv"), rd("metrics_by_hhsize.csv"), rd("figs/fig13_summary.csv"), \
    rd("figs/activity_hours_by_year.csv"), rd("figs/metabolic_hourly_by_year.csv")
YEARS = ["2005", "2010", "2015", "2022", "2025"]


def mval(year, dt, col, region="Canada"):
    if M is None:
        return np.nan
    r = M[(M.year.astype(str) == year) & (M.region == region) & (M.day_type == dt)]
    return float(r[col].iloc[0]) if len(r) else np.nan


def hval(year, size, dt, col):
    if H is None:
        return np.nan
    r = H[(H.year.astype(str) == year) & (H.hhsize.astype(str) == size) & (H.day_type == dt)]
    return float(r[col].iloc[0]) if len(r) and col in r else np.nan


def fval(q):
    if F13 is None:
        return np.nan
    r = F13[F13.quantity == q]
    try:
        return float(r.value.iloc[0])
    except Exception:
        return np.nan


def aval(year, cat):
    if ACT is None:
        return np.nan
    r = ACT[ACT.year.astype(str) == year]
    return float(r[cat].iloc[0]) if len(r) and cat in r else np.nan


rows = []


def add(line, what, old, new, defn):
    rows.append((line, what, old, "n/a" if (isinstance(new, float) and np.isnan(new)) else (f"{new:.3f}" if isinstance(new, float) else new), defn))


old_wd = {"2005": 15.5, "2010": 11.9, "2015": 17.5, "2022": 15.9, "2025": 12.4}
for y in YEARS:
    add(173, f"weekday occupied hours {y}", old_wd[y], mval(y, "Weekday", "occupied_hours"), "sum of 24 hourly means, Weekday, Canada")
add(173, "daytime fraction 09-17, 2005", 0.60, mval("2005", "Weekday", "daytime_fraction"), "mean of hours 9-16, Weekday")
add(173, "daytime fraction 09-17, 2025", 0.30, mval("2025", "Weekday", "daytime_fraction"), "mean of hours 9-16, Weekday")
for y in YEARS:
    add(173, f"(extra) daytime fraction weekday {y}", "not stated", mval(y, "Weekday", "daytime_fraction"), "mean of hours 9-16, Weekday")
add(179, "Default occupied hours (weekday = weekend)", 16.4, mval("Default", "Weekday", "occupied_hours", "Default"), "sum of the 24 Default values (16.42)")
asy = [abs(mval(y, "Weekend", "occupied_hours") - mval(y, "Weekday", "occupied_hours")) for y in YEARS]
add(179, "weekday-weekend asymmetry, range over cycles (h)", "1.8 to 4.6", f"{np.nanmin(asy):.2f} to {np.nanmax(asy):.2f}" if not np.all(np.isnan(asy)) else "n/a", "abs(weekend hours - weekday hours) per year, all five years")
for y in YEARS:
    add(179, f"weekend occupied hours {y}", "range 13.7 to 16.5", mval(y, "Weekend", "occupied_hours"), "sum of 24 hourly means, Weekend")
add(179, "2022 weekend vs weekday (h)", "16.5 vs 15.9", f"{mval('2022','Weekend','occupied_hours'):.2f} vs {mval('2022','Weekday','occupied_hours'):.2f}", "same")
dv = mval("Default", "Weekday", "daytime_vacancy_pct", "Default")
for y in ["2005", "2015"]:
    add(179, f"Default vacancy minus cycle vacancy, {y} (pct points)", "~58", dv - mval(y, "Weekday", "daytime_vacancy_pct"),
        "Default 74.4 minus (100*(1 - daytime fraction)), Weekday; old definition of the 58 is not stated in the paper")
for cat, lab, oldv in [("Sleep", "sleep hours/day", "8.6 to 10.1, peak 2022"), ("Passive Leisure", "passive leisure hours/day", "4.1 (2005) to 3.0 (2022)"), ("Other", "'Other' hours/day", "3.5 to 4.4")]:
    for y in YEARS:
        add(183, f"{lab} {y}", oldv, aval(y, cat), "activity script: share of activity codes x 24 h (Figure 12)")
if MET is not None:
    for y in YEARS:
        if y in MET.columns:
            add(189, f"metabolic hourly mean, peak {y} (W)", "peak near 125 to 135 (2010, 2022)", float(MET[y].max()), "mean Metabolic_Rate by hour over rows with Metabolic_Rate > 1 (Figure 12 script filter)")
add(193, "night overestimate, Default vs 2025 (pct)", "+39", fval("night_h1_5_default_over_gss_pct"), "Default mean hours 1-5 / 2025 weekday mean hours 1-5 - 1 (definition inferred; old code hard-coded the text)")
add(193, "Default sleep-hour metabolic overprediction vs 70 W floor (pct)", "~36", 100 * (95 - 70) / 70, "(95-70)/70, definition-only, unchanged")
add(193, "midday: Default metabolic vs 2025 hours 10-14 (pct, + = Default higher)", "under 24 to 30 (text); +60 in old figure label", fval("midday_h10_14_met_default_over_gss_pct"), "95 / GSS mean hours 10-14 - 1")
add(193, "GSS metabolic midday value (W)", "125 to 135", fval("met_midday_h10_14_gss"), "2025 weekday mean Metabolic_Rate, hours 10-14, all rows")
add(199, "mean weekday occupancy, Default", 0.684, fval("mean_occ_default"), "mean of 24 Default values")
add(199, "mean weekday occupancy, 2025", 0.465, fval("mean_occ_gss_weekday"), "mean over 24 h, Weekday, Canada")
add(199, "mean weekend occupancy, 2025", 0.502, fval("mean_occ_gss_weekend"), "mean over 24 h, Weekend, Canada")
add(199, "weekday overestimate by Default (pct)", 32, fval("overest_weekday_pct"), "(Default - GSS)/Default")
add(199, "weekend overestimate by Default (pct)", 27, fval("overest_weekend_pct"), "(Default - GSS)/Default")
add(199, "mean metabolic rate 2025 (W), hourly-mean definition", 72.1, fval("met_mean_gss_weekday_hourly_all_rows"), "mean of 24 hourly means of Metabolic_Rate, Weekday, all rows (Figure 13 panel b line)")
add(199, "mean metabolic rate 2025 (W), occupied rows only", 72.1, fval("met_mean_gss_weekday_occ_pos_rows"), "mean of Metabolic_Rate over Weekday rows with Occupancy_Schedule > 0")
add(199, "Default metabolic overestimate (pct)", 24, fval("met_default_over_gss_mean_pct"), "(95 - GSS mean)/95, hourly-mean definition")
add(199, "daytime occupancy Default (%)", 25.6, fval("daytime_pct_default"), "mean Default hours 9-16 x 100")
add(199, "daytime occupancy 2025 (%)", 27.6, fval("daytime_pct_gss_weekday"), "mean Weekday hours 9-16 x 100")
old14 = {"1": (18.2, 56.1, 19.2, 63.8), "5+": (5.2, 12.4, 6.9, 21.7)}
for s, (wh, wd, eh, ed) in old14.items():
    add(203, f"2025 weekday occupied hours, size {s}", wh, hval("2025", s, "Weekday", "occupied_hours"), "sum of 24 hourly means, by HHSIZE (5+ = 5 or more)")
    add(203, f"2025 weekday daytime %, size {s}", wd, 100 * hval("2025", s, "Weekday", "daytime_fraction"), "mean hours 9-16 x 100")
    add(203, f"2025 weekend occupied hours, size {s}", eh, hval("2025", s, "Weekend", "occupied_hours"), "sum of 24 hourly means")
    add(203, f"2025 weekend daytime %, size {s}", ed, 100 * hval("2025", s, "Weekend", "daytime_fraction"), "mean hours 9-16 x 100")
w1, w5 = hval("2025", "1", "Weekday", "occupied_hours"), hval("2025", "5+", "Weekday", "occupied_hours")
add(203, "weekday hours reduction 1-person to 5+ (pct)", 71, 100 * (w1 - w5) / w1 if w1 == w1 and w5 == w5 else np.nan, "(size1 - size5+)/size1")

out = ["# Section 4.1: old paper numbers vs values recomputed from the rebuilt files (WP13)", "",
       "Definitions are the paper's own. New values are from the rebuilt grid files listed in the WP13 task doc.",
       "'Old' is copied from `1J_docs_occ/manuscript/1st_Occ_Journal.md` at the line given. No threshold is applied.", "",
       "| Line | Quantity | Old (paper) | New | Definition used for New |", "|---|---|---|---|---|"]
for r in rows:
    out.append("| " + " | ".join(str(x) for x in r) + " |")
open(os.path.join(D, "old_vs_new_section41.md"), "w", encoding="utf8").write("\n".join(out) + "\n")
print(f"wrote old_vs_new_section41.md with {len(rows)} rows")
print("OLD_VS_NEW DONE")
