"""
F-1J-8: measure how much the census age code 88 ("not available", mapped by every
alignment.py into the 75+ group) changes the occupancy result.

READ-ONLY. This script never writes to any pipeline input and never modifies any
alignment/matcher/aggregation/occToBEM file. It only reads three files per census
year and writes its own small summary files under its own output directory.

Real schemas (confirmed on the cluster 2026-09-19 with `head -1`, not guessed):
  raw census  cen{06,11,16,21}_filtered.csv :
      HH_ID,EF_ID,CF_ID,PP_ID,CMA,AGEGRP,... (raw AGEGRP codes 1-13, 88=not available)
  person-level matched file
      Outputs_<YEARTAG>/ProfileMatching/<YEARTAG>_Matched_Keys_sample25pct.csv :
      HH_ID,...,PP_ID,AGEGRP(harmonized 1-7),...,SIM_HH_ID,MATCH_ID_WD,...
      (one row per matched census person; PP_ID here holds the SAME values as raw
      census PP_ID -- confirmed by sampling both files -- so PP_ID is the shared key.)
  grid file
      Outputs_<YEARTAG>/occToBEM/<YEARTAG>_BEM_Schedules_sample25pct_grid.csv :
      SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,
      Occupancy_Schedule,Metabolic_Rate

Link (M2): raw census PP_ID -> person-level file PP_ID -> person-level file
SIM_HH_ID -> grid file SIM_HH_ID. If PP_ID is missing from either the raw census
file or the person-level file, or SIM_HH_ID is missing from the person-level file,
we print `LINK: NOT AVAILABLE -- <what was tried>` and skip M2/M3/M4 for that year
(never invent a link).

Decisions (documented, do not move without updating the task doc's Decisions
section too):
  - M1 denominator ("survive into matching") = raw AGEGRP > 2 (task doc: "after the
    children drop, AGEGRP <= 2"). No further filtering.
  - "weekday 09-16" / "weekend 09-16" = Hour in 9..16 inclusive (8 hourly slots) on
    the named Day_Type.
  - "night hour 3" = Hour == 3, BOTH Day_Type rows pooled (the task doc does not say
    weekday-only or weekend-only for this one metric; grid file gives one row per
    (SIM_HH_ID, Day_Type, Hour), so pooling both day types is the reading that does
    not silently drop half the data).
  - M4 "recomputed" = same weekday 09-16 slice restricted to unaffected households
    (this equals the "unaffected" mean already computed for M3's first metric).
"""

import argparse
import csv
import json
import os
import sys

import pandas as pd


def log(msg):
    print(msg, flush=True)


def header_cols(path):
    return list(pd.read_csv(path, nrows=0).columns)


def measure_year(year_label, census_path, person_path, grid_path):
    """Run M1-M4 for one census year. Returns a dict result. Never raises --
    any failure is captured into the result dict so the caller can keep going
    and the script can still exit 0."""
    result = {
        "year": year_label,
        "census_path": census_path,
        "person_path": person_path,
        "grid_path": grid_path,
        "m1": None,
        "m2": None,
        "m3": None,
        "m4": None,
        "link_status": None,
        "errors": [],
    }

    # ---- M1: raw census AGEGRP == 88 share ----
    if not os.path.isfile(census_path):
        result["errors"].append(f"census file not found: {census_path}")
        log(f"YEAR {year_label}: CENSUS FILE NOT FOUND -- {census_path}")
        return result

    cen_cols = header_cols(census_path)
    if "AGEGRP" not in cen_cols or "PP_ID" not in cen_cols:
        result["errors"].append(
            f"raw census file missing AGEGRP or PP_ID; columns={cen_cols}"
        )
        log(f"YEAR {year_label}: M1 SKIPPED -- raw census missing AGEGRP/PP_ID")
        return result

    df_cen = pd.read_csv(census_path, usecols=["PP_ID", "AGEGRP"])
    agegrp_raw = pd.to_numeric(df_cen["AGEGRP"], errors="coerce")
    survive_mask = agegrp_raw > 2
    n_survive = int(survive_mask.sum())
    n_88 = int((agegrp_raw == 88).sum())
    share_88 = (n_88 / n_survive) if n_survive > 0 else float("nan")

    result["m1"] = {"count_88": n_88, "n_survive": n_survive, "share_88": share_88}
    log(
        f"YEAR {year_label}: M1 count_88={n_88} n_survive={n_survive} "
        f"share_88={share_88:.6f}"
    )

    affected_pp_ids = set(df_cen.loc[agegrp_raw == 88, "PP_ID"])
    del df_cen, agegrp_raw, survive_mask

    # ---- M2: link to person-level file, then to the grid file, via PP_ID -> SIM_HH_ID ----
    if not os.path.isfile(person_path):
        result["link_status"] = f"NOT AVAILABLE -- person-level file not found: {person_path}"
        log(f"YEAR {year_label}: LINK: NOT AVAILABLE -- person-level file not found: {person_path}")
        return result

    person_cols = header_cols(person_path)
    tried = []
    if "PP_ID" not in person_cols:
        tried.append("PP_ID not in person-level file columns")
    if "SIM_HH_ID" not in person_cols:
        tried.append("SIM_HH_ID not in person-level file columns")
    if tried:
        msg = "; ".join(tried) + f"; person-level columns={person_cols}"
        result["link_status"] = f"NOT AVAILABLE -- {msg}"
        log(f"YEAR {year_label}: LINK: NOT AVAILABLE -- {msg}")
        return result

    df_person = pd.read_csv(person_path, usecols=["PP_ID", "SIM_HH_ID"]).drop_duplicates()
    matched = df_person[df_person["PP_ID"].isin(affected_pp_ids)]
    n_affected_pp_matched = matched["PP_ID"].nunique()
    n_affected_pp_unmatched = len(affected_pp_ids) - n_affected_pp_matched
    affected_hh_ids_all = set(matched["SIM_HH_ID"].dropna())
    result["link_status"] = "OK"
    log(
        f"YEAR {year_label}: LINK: OK via PP_ID -> SIM_HH_ID "
        f"(affected persons matched={n_affected_pp_matched}, unmatched={n_affected_pp_unmatched})"
    )

    if not os.path.isfile(grid_path):
        result["errors"].append(f"grid file not found: {grid_path}")
        log(f"YEAR {year_label}: M2/M3/M4 SKIPPED -- grid file not found: {grid_path}")
        return result

    grid_cols = header_cols(grid_path)
    need_grid_cols = ["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"]
    missing_grid_cols = [c for c in need_grid_cols if c not in grid_cols]
    if missing_grid_cols:
        result["errors"].append(f"grid file missing columns {missing_grid_cols}; has {grid_cols}")
        log(f"YEAR {year_label}: M2/M3/M4 SKIPPED -- grid file missing columns {missing_grid_cols}")
        return result

    df_grid = pd.read_csv(grid_path, usecols=need_grid_cols)
    all_hh_ids = set(df_grid["SIM_HH_ID"].dropna())
    affected_hh_ids = affected_hh_ids_all & all_hh_ids

    n_all_hh = len(all_hh_ids)
    n_affected_hh = len(affected_hh_ids)
    share_hh = (n_affected_hh / n_all_hh) if n_all_hh > 0 else float("nan")
    result["m2"] = {
        "n_affected_hh": n_affected_hh,
        "n_all_hh": n_all_hh,
        "share_hh": share_hh,
        "n_affected_hh_in_person_file_not_in_grid": len(affected_hh_ids_all - all_hh_ids),
    }
    log(
        f"YEAR {year_label}: M2 n_affected_hh={n_affected_hh} n_all_hh={n_all_hh} "
        f"share_hh={share_hh:.6f}"
    )
    affected_hh_sorted = sorted(affected_hh_ids, key=lambda x: str(x))
    if len(affected_hh_sorted) <= 50:
        log(f"YEAR {year_label}: M2 affected households = {affected_hh_sorted}")
    else:
        log(
            f"YEAR {year_label}: M2 affected households (first 20 of {len(affected_hh_sorted)}) "
            f"= {affected_hh_sorted[:20]}"
        )
    result["m2"]["affected_hh_ids_sample"] = affected_hh_sorted[:50]

    is_affected = df_grid["SIM_HH_ID"].isin(affected_hh_ids)

    def slice_mean_and_n(mask):
        sub = df_grid.loc[mask]
        n_hh = sub["SIM_HH_ID"].nunique()
        mean_val = sub["Occupancy_Schedule"].mean()
        return mean_val, n_hh

    wd916_mask = (df_grid["Day_Type"] == "Weekday") & df_grid["Hour"].between(9, 16)
    we916_mask = (df_grid["Day_Type"] == "Weekend") & df_grid["Hour"].between(9, 16)
    h3_mask = df_grid["Hour"] == 3

    wd916_aff_mean, wd916_aff_n = slice_mean_and_n(wd916_mask & is_affected)
    wd916_unaff_mean, wd916_unaff_n = slice_mean_and_n(wd916_mask & ~is_affected)
    we916_aff_mean, we916_aff_n = slice_mean_and_n(we916_mask & is_affected)
    we916_unaff_mean, we916_unaff_n = slice_mean_and_n(we916_mask & ~is_affected)
    h3_aff_mean, h3_aff_n = slice_mean_and_n(h3_mask & is_affected)
    h3_unaff_mean, h3_unaff_n = slice_mean_and_n(h3_mask & ~is_affected)

    result["m3"] = {
        "weekday_09_16": {
            "affected_mean": wd916_aff_mean, "affected_n_hh": wd916_aff_n,
            "unaffected_mean": wd916_unaff_mean, "unaffected_n_hh": wd916_unaff_n,
        },
        "weekend_09_16": {
            "affected_mean": we916_aff_mean, "affected_n_hh": we916_aff_n,
            "unaffected_mean": we916_unaff_mean, "unaffected_n_hh": we916_unaff_n,
        },
        "night_hour_3": {
            "affected_mean": h3_aff_mean, "affected_n_hh": h3_aff_n,
            "unaffected_mean": h3_unaff_mean, "unaffected_n_hh": h3_unaff_n,
        },
    }
    log(
        f"YEAR {year_label}: M3 weekday09-16 affected_mean={wd916_aff_mean:.6f} (n={wd916_aff_n}) "
        f"unaffected_mean={wd916_unaff_mean:.6f} (n={wd916_unaff_n})"
    )
    log(
        f"YEAR {year_label}: M3 weekend09-16 affected_mean={we916_aff_mean:.6f} (n={we916_aff_n}) "
        f"unaffected_mean={we916_unaff_mean:.6f} (n={we916_unaff_n})"
    )
    log(
        f"YEAR {year_label}: M3 night_hour3 affected_mean={h3_aff_mean:.6f} (n={h3_aff_n}) "
        f"unaffected_mean={h3_unaff_mean:.6f} (n={h3_unaff_n})"
    )

    # ---- M4: headline sensitivity ----
    overall_mean, overall_n = slice_mean_and_n(wd916_mask)
    recomputed_mean = wd916_unaff_mean  # same slice, affected households removed
    diff = recomputed_mean - overall_mean
    result["m4"] = {
        "overall_weekday_09_16_mean": overall_mean,
        "overall_n_hh": overall_n,
        "recomputed_weekday_09_16_mean_no_affected": recomputed_mean,
        "diff_recomputed_minus_overall": diff,
    }
    log(
        f"YEAR {year_label}: M4 overall={overall_mean:.6f} recomputed_no_affected={recomputed_mean:.6f} "
        f"diff={diff:.6f}"
    )

    return result


CLUSTER_BASE = "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy"

REAL_YEARS = [
    {
        "year": "2006",
        "yeartag": "06CEN05GSS",
        "census": f"{CLUSTER_BASE}/Outputs_CENSUS/cen06_filtered.csv",
        "person": f"{CLUSTER_BASE}/Outputs_06CEN05GSS/ProfileMatching/06CEN05GSS_Matched_Keys_sample25pct.csv",
        "grid": f"{CLUSTER_BASE}/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv",
    },
    {
        "year": "2011",
        "yeartag": "11CEN10GSS",
        "census": f"{CLUSTER_BASE}/Outputs_CENSUS/cen11_filtered.csv",
        "person": f"{CLUSTER_BASE}/Outputs_11CEN10GSS/ProfileMatching/11CEN10GSS_Matched_Keys_sample25pct.csv",
        "grid": f"{CLUSTER_BASE}/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv",
    },
    {
        "year": "2016",
        "yeartag": "16CEN15GSS",
        "census": f"{CLUSTER_BASE}/Outputs_CENSUS/cen16_filtered.csv",
        "person": f"{CLUSTER_BASE}/Outputs_16CEN15GSS/ProfileMatching/16CEN15GSS_Matched_Keys_sample25pct.csv",
        "grid": f"{CLUSTER_BASE}/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv",
    },
    {
        "year": "2021",
        "yeartag": "21CEN22GSS",
        "census": f"{CLUSTER_BASE}/Outputs_CENSUS/cen21_filtered.csv",
        "person": f"{CLUSTER_BASE}/Outputs_21CEN22GSS/ProfileMatching/21CEN22GSS_Matched_Keys_sample25pct.csv",
        "grid": f"{CLUSTER_BASE}/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv",
    },
]


def apply_decision_rule(results):
    diffs = []
    for r in results:
        if r.get("m4") is not None:
            diffs.append((r["year"], r["m4"]["diff_recomputed_minus_overall"]))
        else:
            log(f"YEAR {r['year']}: NOT_EVALUABLE -- link failed or file missing, excluded from d")

    if not diffs:
        log("DECISION: NOT_EVALUABLE -- no year produced an M4 difference")
        return

    worst_year, d = max(diffs, key=lambda t: abs(t[1]))
    log(f"DECISION: d = largest |M4 diff| across evaluable years = {d:.6f} (year {worst_year})")
    if abs(d) <= 0.005:
        log("DECISION: recommendation = leave the code alone, name it as a limitation in the paper.")
    elif abs(d) > 0.010:
        log("DECISION: recommendation = fix the mapping and rebuild the affected years.")
    else:
        log("DECISION: no recommendation; the author decides.")


def run_real(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for cfg in REAL_YEARS:
        log("=" * 70)
        r = measure_year(cfg["year"], cfg["census"], cfg["person"], cfg["grid"])
        results.append(r)

    log("=" * 70)
    log("2025: NOT_EVALUABLE -- different pipeline")

    apply_decision_rule(results)

    out_json = os.path.join(out_dir, "age88_summary.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"Wrote summary: {out_json}")
    return results


def run_test(census_path, person_path, grid_path, year_label):
    """Local synthetic-file test entry point. Prints results, exits 0 always
    (a script crash here would not be a 'seen failing' result, it would just be
    a broken script)."""
    r = measure_year(year_label, census_path, person_path, grid_path)
    print(json.dumps(r, indent=2, default=str))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["real", "test"], default="real")
    ap.add_argument("--out-dir", default="/speed-scratch/o_iseri/1J_rerun/f1j8/results")
    ap.add_argument("--census")
    ap.add_argument("--person")
    ap.add_argument("--grid")
    ap.add_argument("--year", default="TEST")
    args = ap.parse_args()

    if args.mode == "real":
        run_real(args.out_dir)
    else:
        if not (args.census and args.person and args.grid):
            log("test mode requires --census --person --grid")
            sys.exit(2)
        run_test(args.census, args.person, args.grid, args.year)

    sys.exit(0)


if __name__ == "__main__":
    main()
