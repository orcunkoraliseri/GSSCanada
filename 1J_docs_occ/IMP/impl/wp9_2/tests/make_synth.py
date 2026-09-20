"""
Build tiny synthetic fixtures for local testing of wp9_2_manifest.py / wp9_2_gate2.py.

Never touches real project data. Writes everything under tests/data/.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

YEARS = ["2005", "2010", "2015", "2022", "2025"]

WORKER = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]  # total 15
HOME = [0.7] * 24  # total 16.8

GRID_FIELDS = [
    "SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule", "Metabolic_Rate",
    "HHSIZE", "DTYPE", "BEDRM", "CONDO", "PR", "MATCH_TIER",
]

# hh_id -> (dtype, hhsize, profile)
HOUSEHOLDS = {
    "HH1": ("SingleD", 2, WORKER),
    "HH2": ("SingleD", 2, WORKER),
    "HH3": ("SingleD", 2, WORKER),
    "HH4": ("SingleD", 3, WORKER),
    "HH5": ("SingleD", 3, WORKER),
    "HH6": ("MidRise", 4, HOME),
    "HH7": ("MidRise", 4, HOME),
}


def write_grid_csv(path, year, blank_pr_hh=None, incomplete_hh=None, two_dtype_hh=None):
    """
    Write one synthetic grid CSV.
      blank_pr_hh: hh_id whose PR is left blank (tests the blank-PR filter).
      incomplete_hh: hh_id that gets only 23 Weekday hours (tests the 24/24 filter).
      two_dtype_hh: hh_id whose rows carry two different DTYPE values (G2.0 FAIL case).
    """
    rows = []
    for hh_id, (dtype, hhsize, profile) in HOUSEHOLDS.items():
        pr = "Quebec"
        if blank_pr_hh and hh_id == blank_pr_hh:
            pr = ""
        this_dtype = dtype
        for day_type in ("Weekday", "Weekend"):
            hours = range(24)
            if incomplete_hh and hh_id == incomplete_hh and day_type == "Weekday":
                hours = range(23)  # drop hour 23 -> only 23 entries
            for h in hours:
                row_dtype = this_dtype
                if two_dtype_hh and hh_id == two_dtype_hh and day_type == "Weekend":
                    row_dtype = "MidRise" if this_dtype != "MidRise" else "SingleD"
                rows.append({
                    "SIM_HH_ID": hh_id,
                    "Day_Type": day_type,
                    "Hour": h,
                    "Occupancy_Schedule": profile[h],
                    "Metabolic_Rate": 100.0,
                    "HHSIZE": hhsize,
                    "DTYPE": row_dtype,
                    "BEDRM": hhsize,
                    "CONDO": 0,
                    "PR": pr,
                    "MATCH_TIER": "1",
                })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=GRID_FIELDS)
        w.writeheader()
        w.writerows(rows)


IDF_TEMPLATE = """\
Version,9.4;

SpaceList,
  Neighbourhood_Main, !- Name
  unit_living_unit1_aaaaaa_Space, !- Space 1 Name
  unit_living_unit2_bbbbbb_Space, !- Space 2 Name
  unit_apartment1_cccccc_Space; !- Space 3 Name
"""


def write_idf(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(IDF_TEMPLATE)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for year in YEARS:
        write_grid_csv(os.path.join(DATA_DIR, f"grid_{year}.csv"), year)

    # Same-shape grid but with one household's PR blank, for a sanity look (not required by
    # the formal seen-failing list, but cheap to keep for a future run).
    write_grid_csv(
        os.path.join(DATA_DIR, "grid_2025_blankpr.csv"), "2025", blank_pr_hh="HH1"
    )
    # Incomplete-hours variant.
    write_grid_csv(
        os.path.join(DATA_DIR, "grid_2025_incomplete.csv"), "2025", incomplete_hh="HH1"
    )
    # Two-DTYPE-per-household variant -- this is the G2.0 FAIL fixture.
    write_grid_csv(
        os.path.join(DATA_DIR, "grid_2025_twodtype.csv"), "2025", two_dtype_hh="HH1"
    )

    write_idf(os.path.join(DATA_DIR, "NUS_TINY1.idf"))
    print("Synthetic fixtures written to", DATA_DIR)


if __name__ == "__main__":
    main()
