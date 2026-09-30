"""Runner for Figure 12 (plot_activity_metabolic_comparison.py copy). Runs its unchanged main() and records the
numbers it plots: activity_hours_by_year.csv (hours/day per category) and metabolic_hourly_by_year.csv
(hourly mean Metabolic_Rate over rows with Metabolic_Rate > 1, the script's own occupied filter)."""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot"))
import plot_activity_metabolic_comparison as m

acts, mets = {}, {}
_pa, _pb = m.process_activity_data_chunk, m.process_bem_profiles


def pa(fp, y, *a, **k):
    r = _pa(fp, y, *a, **k)
    if r:
        acts[y] = r
    return r


def pb(fp, y, *a, **k):
    r = _pb(fp, y, *a, **k)
    if r is not None:
        mets[y] = r
    return r


m.process_activity_data_chunk, m.process_bem_profiles = pa, pb
m.main()
outdir = os.environ.get("WP13_FIGS", ".")
pd.DataFrame(acts).T.to_csv(os.path.join(outdir, "activity_hours_by_year.csv"), index_label="year")
pd.DataFrame(mets).to_csv(os.path.join(outdir, "metabolic_hourly_by_year.csv"), index_label="hour")
print("activity years:", list(acts), "metabolic years:", list(mets))
print("FIG12 DONE")
