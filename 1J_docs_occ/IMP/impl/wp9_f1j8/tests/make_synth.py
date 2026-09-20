"""
Build tiny synthetic fixtures for local testing of wp9_f1j8_age88.py.
Never touches real project data. Writes everything under tests/data/.

Households: HH1..HH5.
  HH1: PP1001 (AGEGRP=88, affected) + PP1002 (AGEGRP=5)      -> affected household
  HH2: PP1003 (AGEGRP=6)                                     -> unaffected
  HH3: PP1004 (AGEGRP=88, affected)                          -> affected household
  HH4: PP1005 (AGEGRP=1, a child -- dropped from "survive")  -> unaffected
  HH5: PP1006 (AGEGRP=7)                                     -> unaffected

So M1: count_88=2, n_survive=5 (all but PP1005), share_88=0.4.
M2: 2 affected households of 5 total -> share_hh=0.4.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

PERSONS = [
    # PP_ID, HH raw id, AGEGRP raw, SIM_HH_ID
    (1001, "HH1", 88, "HH1"),
    (1002, "HH1", 5, "HH1"),
    (1003, "HH2", 6, "HH2"),
    (1004, "HH3", 88, "HH3"),
    (1005, "HH4", 1, "HH4"),
    (1006, "HH5", 7, "HH5"),
]

PERSONS_NO88 = [
    (1001, "HH1", 5, "HH1"),
    (1002, "HH1", 5, "HH1"),
    (1003, "HH2", 6, "HH2"),
    (1004, "HH3", 6, "HH3"),
    (1005, "HH4", 1, "HH4"),
    (1006, "HH5", 7, "HH5"),
]

CENSUS_FIELDS = ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "HHSIZE"]
PERSON_FIELDS_FULL = ["HH_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "SIM_HH_ID", "MATCH_TIER_WD"]
PERSON_FIELDS_NO_SIMHHID = ["HH_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "MATCH_TIER_WD"]
GRID_FIELDS = [
    "SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM",
    "REPAIR", "PR", "MATCH_TIER", "Occupancy_Schedule", "Metabolic_Rate",
]

AFFECTED_HH = {"HH1", "HH3"}
ALL_HH = ["HH1", "HH2", "HH3", "HH4", "HH5"]


def write_census(path, persons):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CENSUS_FIELDS)
        w.writeheader()
        for pp_id, hh_id, agegrp, sim_hh in persons:
            w.writerow({
                "HH_ID": hh_id, "EF_ID": hh_id + "E", "CF_ID": hh_id + "C",
                "PP_ID": pp_id, "CMA": 1, "AGEGRP": agegrp, "SEX": 1, "HHSIZE": 2,
            })


def write_person(path, persons, with_sim_hh_id=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = PERSON_FIELDS_FULL if with_sim_hh_id else PERSON_FIELDS_NO_SIMHHID
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for pp_id, hh_id, agegrp_raw, sim_hh in persons:
            # person-level file carries the HARMONIZED AGEGRP (1-7), matching the
            # real pipeline (raw 88 -> harmonized 7). Not used by the script but
            # kept realistic.
            harmonized = 7 if agegrp_raw >= 13 or agegrp_raw == 88 else agegrp_raw
            row = {
                "HH_ID": hh_id, "PP_ID": pp_id, "CMA": 1, "AGEGRP": harmonized,
                "SEX": 1, "MATCH_TIER_WD": "1",
            }
            if with_sim_hh_id:
                row["SIM_HH_ID"] = sim_hh
            w.writerow(row)


def write_grid(path, affected_value, unaffected_value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    for hh in ALL_HH:
        val = affected_value if hh in AFFECTED_HH else unaffected_value
        for day_type in ("Weekday", "Weekend"):
            for h in range(24):
                rows.append({
                    "SIM_HH_ID": hh, "Day_Type": day_type, "Hour": h,
                    "HHSIZE": 2, "DTYPE": "SingleD", "BEDRM": 2, "CONDO": 0,
                    "ROOM": 5, "REPAIR": 1, "PR": "Quebec", "MATCH_TIER": "1",
                    "Occupancy_Schedule": val, "Metabolic_Rate": 100.0,
                })
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=GRID_FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Test 1: affected households forced occupied all day (1.0) vs unaffected at 0.2
    write_census(os.path.join(DATA_DIR, "t1_census.csv"), PERSONS)
    write_person(os.path.join(DATA_DIR, "t1_person.csv"), PERSONS, with_sim_hh_id=True)
    write_grid(os.path.join(DATA_DIR, "t1_grid.csv"), affected_value=1.0, unaffected_value=0.2)

    # Test 2: no person coded 88 -> M1 count 0, M4 diff exactly 0
    write_census(os.path.join(DATA_DIR, "t2_census.csv"), PERSONS_NO88)
    write_person(os.path.join(DATA_DIR, "t2_person.csv"), PERSONS_NO88, with_sim_hh_id=True)
    write_grid(os.path.join(DATA_DIR, "t2_grid.csv"), affected_value=0.6, unaffected_value=0.6)

    # Test 3: person-level file has no SIM_HH_ID column -> LINK: NOT AVAILABLE
    write_census(os.path.join(DATA_DIR, "t3_census.csv"), PERSONS)
    write_person(os.path.join(DATA_DIR, "t3_person.csv"), PERSONS, with_sim_hh_id=False)
    write_grid(os.path.join(DATA_DIR, "t3_grid.csv"), affected_value=1.0, unaffected_value=0.2)

    print("Synthetic fixtures written to", DATA_DIR)


if __name__ == "__main__":
    main()
