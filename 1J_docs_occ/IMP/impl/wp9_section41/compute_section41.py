"""
WP9: recompute Section 4.1 occupancy numbers from the rebuilt grid files.
Read-only. Computes hourly/weekday/weekend/night occupancy means (overall and
split by HHSIZE bucket) from the five rebuilt *_grid.csv files, and prints them
side by side with the submitted paper's old (faulty-input) Section 4.1 numbers.

No threshold, no pass/fail -- this is a straight replacement of stale numbers.

Usage (on Speed, inside the sbatch job):
    /speed-scratch/o_iseri/GSSCanada/venv/bin/python compute_section41.py

Usage (local test, on a tiny synthetic file):
    py compute_section41.py --test-file <path-to-synthetic-csv>
"""
import sys
import argparse
import pandas as pd
import numpy as np

USECOLS = ["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "Occupancy_Schedule"]
DTYPES = {
    "SIM_HH_ID": str,
    "Day_Type": str,
    "Hour": "int64",
    "HHSIZE": "float64",  # cast to float first in case of NaN/odd values, bucket after
    "Occupancy_Schedule": "float64",
}

# Paper's Section 4.1 weekday occupied-hours numbers, from the old (faulty) input
# files -- read from 00_REVISION_PLAN.md:242, not re-derived here.
OLD_PAPER_WEEKDAY_OCCUPIED_HOURS = {
    "2005": 15.48,
    "2010": 11.89,
    "2015": 17.55,
    "2022": 15.90,
    # 2025 has no old paper number (new file, not in the submitted paper).
}

HHSIZE_BUCKETS = ["1", "2", "3", "4", "5+"]


def bucket_hhsize(series):
    """Bucket HHSIZE into '1','2','3','4','5+' string labels."""
    def _b(v):
        if pd.isna(v):
            return None
        v = int(round(v))
        if v >= 5:
            return "5+"
        if v <= 0:
            return None
        return str(v)
    return series.map(_b)


def mean_and_count(df, mask, value_col="Occupancy_Schedule", id_col="SIM_HH_ID"):
    """Mean of value_col over mask, plus unique-household count over mask.
    Returns (mean, hh_count, row_count). NaN mean / 0 counts if mask is empty."""
    sub = df.loc[mask]
    if len(sub) == 0:
        return (float("nan"), 0, 0)
    return (float(sub[value_col].mean()), int(sub[id_col].nunique()), int(len(sub)))


def compute_stats(df):
    """Compute all WP9 Section 4.1 statistics for one year's grid dataframe.
    Returns a dict of results (see task doc items 1-4)."""
    out = {}

    # Item 1: mean Occupancy_Schedule by Hour (0-23) x Day_Type (Weekday/Weekend),
    # with the row count ("household-day count") behind each cell.
    hourly = {}
    for day_type in ["Weekday", "Weekend"]:
        for hour in range(24):
            mask = (df["Day_Type"] == day_type) & (df["Hour"] == hour)
            mean_v, hh_n, row_n = mean_and_count(df, mask)
            hourly[(day_type, hour)] = (mean_v, row_n)
    out["hourly"] = hourly

    # Item 2: weekday 09-16 mean and weekend 09-16 mean (Hour 9..16 inclusive).
    wd_mask = (df["Day_Type"] == "Weekday") & (df["Hour"] >= 9) & (df["Hour"] <= 16)
    we_mask = (df["Day_Type"] == "Weekend") & (df["Hour"] >= 9) & (df["Hour"] <= 16)
    wd_mean, wd_hh, wd_rows = mean_and_count(df, wd_mask)
    we_mean, we_hh, we_rows = mean_and_count(df, we_mask)
    out["weekday_09_16"] = {"mean": wd_mean, "hh_count": wd_hh, "row_count": wd_rows}
    out["weekend_09_16"] = {"mean": we_mean, "hh_count": we_hh, "row_count": we_rows}

    # Item 3: night mean at Hour 3, both day types pooled (F-1J-8 convention).
    night_mask = (df["Hour"] == 3)
    night_mean, night_hh, night_rows = mean_and_count(df, night_mask)
    out["night_hour3"] = {"mean": night_mean, "hh_count": night_hh, "row_count": night_rows}

    # Item 4: items 2 and 3 again, split by HHSIZE bucket.
    hhsize_bucket = bucket_hhsize(df["HHSIZE"])
    by_size = {}
    for bucket in HHSIZE_BUCKETS:
        bmask = (hhsize_bucket == bucket)
        wd_b = (bmask & wd_mask)
        we_b = (bmask & we_mask)
        night_b = (bmask & night_mask)
        wd_m, wd_h, wd_r = mean_and_count(df, wd_b)
        we_m, we_h, we_r = mean_and_count(df, we_b)
        ni_m, ni_h, ni_r = mean_and_count(df, night_b)
        by_size[bucket] = {
            "weekday_09_16": {"mean": wd_m, "hh_count": wd_h, "row_count": wd_r},
            "weekend_09_16": {"mean": we_m, "hh_count": we_h, "row_count": we_r},
            "night_hour3": {"mean": ni_m, "hh_count": ni_h, "row_count": ni_r},
        }
    out["by_hhsize"] = by_size

    return out


def print_stats(year_label, stats):
    print("=" * 70)
    print(f"YEAR {year_label}")
    print("=" * 70)

    print("\n-- Item 1: mean Occupancy_Schedule by Hour x Day_Type (household-day count) --")
    for day_type in ["Weekday", "Weekend"]:
        for hour in range(24):
            mean_v, row_n = stats["hourly"][(day_type, hour)]
            print(f"  {day_type:8s} Hour={hour:2d}  mean={mean_v:.6f}  n={row_n}")

    print("\n-- Item 2: headline 09-16 means --")
    wd = stats["weekday_09_16"]
    we = stats["weekend_09_16"]
    print(f"  weekday_09_16_mean = {wd['mean']:.6f}  (hh_count={wd['hh_count']}, row_count={wd['row_count']})")
    print(f"  weekend_09_16_mean = {we['mean']:.6f}  (hh_count={we['hh_count']}, row_count={we['row_count']})")

    print("\n-- Item 3: night mean at Hour 3 (both day types pooled) --")
    ni = stats["night_hour3"]
    print(f"  night_hour3_mean = {ni['mean']:.6f}  (hh_count={ni['hh_count']}, row_count={ni['row_count']})")

    print("\n-- Item 4: items 2 and 3 split by HHSIZE bucket --")
    for bucket in HHSIZE_BUCKETS:
        b = stats["by_hhsize"][bucket]
        print(f"  HHSIZE={bucket}:")
        print(f"    weekday_09_16_mean = {b['weekday_09_16']['mean']:.6f}  (hh_count={b['weekday_09_16']['hh_count']}, row_count={b['weekday_09_16']['row_count']})")
        print(f"    weekend_09_16_mean = {b['weekend_09_16']['mean']:.6f}  (hh_count={b['weekend_09_16']['hh_count']}, row_count={b['weekend_09_16']['row_count']})")
        print(f"    night_hour3_mean   = {b['night_hour3']['mean']:.6f}  (hh_count={b['night_hour3']['hh_count']}, row_count={b['night_hour3']['row_count']})")

    old_v = OLD_PAPER_WEEKDAY_OCCUPIED_HOURS.get(year_label)
    print("\n-- Comparison with submitted paper Section 4.1 (no threshold, replacement only) --")
    if old_v is None:
        print(f"  paper_weekday_occupied_hours = N/A (no old-paper number for {year_label})")
    else:
        diff = wd["mean"] - old_v
        print(f"  paper_weekday_occupied_hours (old, faulty files) = {old_v}")
        print(f"  new_weekday_09_16_mean (this run)                = {wd['mean']:.6f}")
        print(f"  difference (new - old)                           = {diff:.6f}")
    print()


YEARS = [
    ("2005", "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv"),
    ("2010", "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv"),
    ("2015", "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv"),
    ("2022", "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv"),
    ("2025", "/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv"),
]


def load_grid(path):
    df = pd.read_csv(path, usecols=USECOLS, dtype=DTYPES)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-file", default=None, help="local synthetic CSV for the seen-failing-first hand check")
    parser.add_argument("--test-year-label", default="TEST", help="label to print for --test-file mode")
    args = parser.parse_args()

    if args.test_file:
        df = load_grid(args.test_file)
        stats = compute_stats(df)
        print_stats(args.test_year_label, stats)
        return

    print("WP9 Section 4.1 recompute -- reading the five rebuilt grid files")
    for year_label, path in YEARS:
        print(f"\nLoading {year_label}: {path}")
        df = load_grid(path)
        print(f"  rows={len(df)}  unique_households={df['SIM_HH_ID'].nunique()}")
        stats = compute_stats(df)
        print_stats(year_label, stats)

    print("JOB DONE")


if __name__ == "__main__":
    main()
