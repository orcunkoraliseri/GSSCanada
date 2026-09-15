#!/usr/bin/env python3
"""
t30_check.py -- T30 / WP3 average-profile arm collector.

Runs the task doc's Acceptance checks (V0-V5) for THIS arm, plus the
household peak-hour spread metrics (Mardia circular SD + morning-leaning
share, Design section (a)+(b)) computed the SAME way for this arm (T30), the
static arm (T22) and the full model (T21 Step-8) -- read-only against all
three staged trees, writes nothing back into T21/ or T22/.

Intended to run as its OWN sbatch job (-c 4 --mem=32G, per the task doc),
with slurm `afterok` on this arm's array (t30_array.sh), T22's static-arm
array (1328310) and T21's Step-8 array, per the T30 task doc's Phase B
section -- run it only once all three trees hold their full output.

STATUS AS WRITTEN (2026-09-15, phase A): built and py_compile-clean, but NOT
YET RUN -- no full-array output exists yet (this is phase A: build/stage/
smoke only). A fresh collector must treat every number this script prints
the FIRST time it actually runs as unverified until spot-checked against a
couple of cells by hand (see the T30 task doc's WHAT I DID NOT VERIFY).

Known simplification, recorded not hidden: V2's "mean over the 8,760
injected hours" is approximated with a fixed 5/7 weekday, 2/7 weekend proxy
(same one run_avg_arm.py's --check-only uses -- see that file's
_v2_identity docstring) rather than reconstructing the real EnergyPlus
RunPeriod calendar (day-of-week-for-start-day, RunPeriodControl:SpecialDays
holidays). The identity being tested is invariant to the exact weight used
(it cancels on both sides), so this still catches an averaging-arithmetic
bug; it does not certify the literal annual number against the true
calendar. V4's "weekday midday" window follows 08_simulation_plots.py's own
MIDDAY=(9,17) constant (hours 9-17 inclusive), reused for occupancy fraction
here rather than facility kWh.
"""
import argparse
import csv
import hashlib
import os
import sys

import numpy as np
import pandas as pd

ARCHETYPES_24 = (
    ["SingleD"] * 6 + ["OtherDwelling"] * 6 + ["MidRise"] * 6 + ["HighRise"] * 6
)
CITIES_24 = [
    "Toronto_5A", "Kelowna_5B", "Vancouver_5C", "Montreal_6A", "Calgary_6B", "Winnipeg_7A"
] * 4
CELLS_24 = list(zip(ARCHETYPES_24, CITIES_24))

FACILITY_METER = "Electricity:Facility"
MIDDAY_HOURS = range(9, 18)  # 9-17 inclusive, 08_simulation_plots.py:114 MIDDAY=(9,17)


# --------------------------------------------------------------------------
# Generic per-cell/per-sample readers
# --------------------------------------------------------------------------

def _read_manifest(cell_dir):
    """cell_manifest.csv -> list of (sample:int, hh_id:str), or [] if missing."""
    path = os.path.join(cell_dir, "cell_manifest.csv")
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return [(int(r["sample"]), r["sim_hh_id"]) for r in rows]


def _hourly_rows(sample_dir, year_label):
    """(row_count, facility_series) from one sample's hourly_meters.csv, or
    (None, None) if the file is missing (an undelivered run -- V0's job to
    flag, never filled in here)."""
    path = os.path.join(sample_dir, year_label, "hourly_meters.csv")
    if not os.path.exists(path):
        return None, None
    df = pd.read_csv(path)
    return len(df), df.get(FACILITY_METER)


def _daily_peak_hours(facility_series):
    """8760-hour facility series -> 365 daily-peak-hour ints (argmax per 24h
    block). None if the series isn't exactly 8760 long."""
    if facility_series is None or len(facility_series) != 8760:
        return None
    vals = facility_series.to_numpy().reshape(365, 24)
    return vals.argmax(axis=1)


def _circular_mean_hour(hours):
    """Same as 08_simulation_plots.py:278-285 -- circular mean of hours-of-day."""
    if len(hours) == 0:
        return np.nan, np.nan, np.nan
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    mean_h = (np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0
    return mean_h, s, c


def _circular_sd_hours(s, c):
    """Same as 08_simulation_plots.py:288-297 -- Mardia's circular SD, sqrt(-2 ln R)."""
    R = float(np.hypot(s, c))
    if not np.isfinite(R) or R <= 0:
        return np.nan
    R = min(R, 1.0)
    return float(np.sqrt(-2.0 * np.log(R)) * 24.0 / (2 * np.pi))


def household_peak_spread(cell_dir, year_label):
    """Per cell/year: Mardia circular SD + morning-leaning share (fraction of
    households whose OWN circular-mean daily-peak hour falls in [0,12)),
    across every household with a complete 8760-row run. Computed identically
    for T30/T22/T21 by construction (same two functions, same formula)."""
    manifest = _read_manifest(cell_dir)
    hh_means = []
    incomplete = []
    for sample, hh_id in manifest:
        sample_dir = os.path.join(cell_dir, f"sample_{sample:03d}_HH{hh_id}")
        n_rows, facility = _hourly_rows(sample_dir, year_label)
        if n_rows != 8760:
            incomplete.append((sample, hh_id, n_rows))
            continue
        daily_peaks = _daily_peak_hours(facility)
        mean_h, _, _ = _circular_mean_hour(daily_peaks)
        hh_means.append(mean_h)
    if not hh_means:
        return {"n_households": 0, "circular_sd_hours": float("nan"),
                "morning_leaning_pct": float("nan"), "incomplete": incomplete}
    hh_means = np.asarray(hh_means)
    _, s, c = _circular_mean_hour(hh_means)
    sd = _circular_sd_hours(s, c)
    morning_pct = float(np.mean((hh_means >= 0) & (hh_means < 12))) * 100
    return {"n_households": len(hh_means), "circular_sd_hours": sd,
            "morning_leaning_pct": morning_pct, "incomplete": incomplete}


# --------------------------------------------------------------------------
# V0-V5
# --------------------------------------------------------------------------

def v0_completeness(t30_root):
    """2,400 planned (24 cells x 2 years x 50 households), delivered per cell x
    year, 8,760 rows each. Lists gaps, never fills them (T21's own warm-up-
    retry precedent: a separate Phase-B follow-up, not this collector)."""
    report = []
    for year in ("2022", "2030"):
        year_label = f"avg_{year}"
        for arch, city in CELLS_24:
            cell_dir = os.path.join(t30_root, "out", f"{arch}__{city}__{year}")
            manifest = _read_manifest(cell_dir)
            delivered, undelivered = 0, []
            for sample, hh_id in manifest:
                sample_dir = os.path.join(cell_dir, f"sample_{sample:03d}_HH{hh_id}")
                n_rows, _ = _hourly_rows(sample_dir, year_label)
                if n_rows == 8760:
                    delivered += 1
                else:
                    undelivered.append((sample, hh_id, n_rows))
            report.append({"cell": f"{arch}__{city}", "year": year, "planned": 50,
                            "manifest_rows": len(manifest), "delivered_8760": delivered,
                            "undelivered": undelivered})
    return report


def v1_same_households(t30_root, t21_root):
    """(sample, hh_id) per cell must equal T21's Step-8 manifest, for BOTH
    years. **Phase-B paired-pool change (manager, "V1 decided, phase B go",
    2026-09-15):** T30 now draws ONCE per cell from the SAME 2022-and-2030
    intersection pool T21 uses (main.py:2029-2034), and reuses that draw for
    both years -- there is no per-year sampling assumption left, so the two
    draws are expected to be IDENTICAL, not merely comparable. Any mismatch on
    ANY cell/year is a STOP (manager decision), not a reported difference to
    band or explain away."""
    mismatches = []
    for year in ("2022", "2030"):
        for arch, city in CELLS_24:
            t30_cell = os.path.join(t30_root, "out", f"{arch}__{city}__{year}")
            t21_cell = os.path.join(t21_root, "out", "step8", f"{arch}__{city}")
            t30_manifest = set(_read_manifest(t30_cell))
            t21_manifest = set(_read_manifest(t21_cell))
            if t30_manifest != t21_manifest:
                mismatches.append({"cell": f"{arch}__{city}", "year": year,
                                    "t30_only": sorted(t30_manifest - t21_manifest),
                                    "t21_only": sorted(t21_manifest - t30_manifest)})
    return mismatches


def v2_identity(step8, sched_dir):
    """Per cell/year: build_avg_schedules()'s own algebraic identity (see
    run_avg_arm.py's _v2_identity docstring for the weighting-cancels caveat
    and the 5/7,2/7 proxy noted at module top), PLUS -- 'also report it next
    to the full model's mean over the same 50 households' -- the PAIRED pool
    size, so a human can eyeball plausibility against T21's own numbers.
    **Phase-B paired-pool change:** build_avg_schedules() now takes sched_dir
    + year (not a single csv_path) and averages over the 2022-and-2030
    intersection pool, matching run_avg_arm.py's own signature exactly (no
    reimplementation)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from run_avg_arm import build_avg_schedules, _v2_identity

    report = []
    for arch, city in CELLS_24:
        cell = step8.resolve_cell(arch, city)
        if not cell:
            report.append({"cell": f"{arch}__{city}", "error": "resolve_cell failed"})
            continue
        _, _, region, dtype, label = cell
        for year in ("2022", "2030"):
            avg_schedules, avg_profile, real_paired, pool = build_avg_schedules(
                step8, sched_dir, year, dtype, region
            )
            if not avg_schedules:
                report.append({"cell": label, "year": year, "error": "empty paired pool"})
                continue
            avg_side, direct_side, delta = _v2_identity(avg_profile, real_paired)
            report.append({"cell": label, "year": year, "avg_side": avg_side,
                            "direct_side": direct_side, "delta": delta,
                            "pass_within_1e-6": delta < 1e-6, "paired_pool_size": len(pool)})
    return report


def v3_one_profile_per_cell(t30_root, idf_cls):
    """Within a cell/year: injected Occ_Sch VALUES (excluding the Name field,
    which embeds hh_id) byte-identical across every delivered household (md5
    of the fields tuple minus index 0); equip/light design levels must still
    differ across households (SHEU levels stay per household)."""
    report = []
    for year in ("2022", "2030"):
        year_label = f"avg_{year}"
        for arch, city in CELLS_24:
            cell_dir = os.path.join(t30_root, "out", f"{arch}__{city}__{year}")
            manifest = _read_manifest(cell_dir)
            hashes, equip_levels, light_levels, n_read = set(), set(), set(), 0
            for sample, hh_id in manifest:
                idf_path = os.path.join(cell_dir, f"sample_{sample:03d}_HH{hh_id}",
                                         year_label, f"Scenario_{year_label}.idf")
                if not os.path.exists(idf_path):
                    continue
                out_idf = idf_cls(idf_path)
                occ = [s for s in out_idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == f"Occ_Sch_HH_{hh_id}"]
                if not occ:
                    continue
                fields = tuple(occ[0].obj[1:])  # drop Name (index 0)
                hashes.add(hashlib.md5(repr(fields).encode()).hexdigest())
                equip = [e for e in out_idf.idfobjects["ELECTRICEQUIPMENT"] if f"STEP9_Equip_{hh_id}_" in e.Name]
                light = [e for e in out_idf.idfobjects["LIGHTS"] if f"STEP9_Lights_{hh_id}_" in e.Name]
                equip_levels.update(getattr(e, "Design_Level", None) for e in equip)
                light_levels.update(getattr(e, "Lighting_Level", None) for e in light)
                n_read += 1
            report.append({"cell": f"{arch}__{city}", "year": year, "n_read": n_read,
                            "n_distinct_occ_sch": len(hashes), "pass_v3_one_profile": len(hashes) <= 1,
                            "n_distinct_equip_levels": len(equip_levels),
                            "n_distinct_light_levels": len(light_levels),
                            "pass_design_levels_differ": len(equip_levels) > 1 or len(light_levels) > 1})
    return report


def v4_year_differs(step8, sched_dir):
    """2030 average profile must differ from 2022 in >=1 hour, every cell (the
    static arm's opposite check -- that arm is year-independent by design,
    this one must NOT be). Reports the weekday-midday (hours 9-17) mean
    at-home change per cell, 2030 minus 2022."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from run_avg_arm import build_avg_schedules

    report = []
    for arch, city in CELLS_24:
        cell = step8.resolve_cell(arch, city)
        if not cell:
            report.append({"cell": f"{arch}__{city}", "error": "resolve_cell failed"})
            continue
        _, _, region, dtype, label = cell
        profiles = {}
        for year in ("2022", "2030"):
            _, avg_profile, _, _ = build_avg_schedules(step8, sched_dir, year, dtype, region)
            profiles[year] = avg_profile
        wd22, wd30 = profiles["2022"]["Weekday"], profiles["2030"]["Weekday"]
        any_hour_differs = any(abs(wd22[h]["occ"] - wd30[h]["occ"]) > 1e-12 for h in range(24))
        midday_22 = float(np.mean([wd22[h]["occ"] for h in MIDDAY_HOURS]))
        midday_30 = float(np.mean([wd30[h]["occ"] for h in MIDDAY_HOURS]))
        report.append({"cell": label, "any_hour_differs": any_hour_differs,
                        "weekday_midday_occ_2022": midday_22, "weekday_midday_occ_2030": midday_30,
                        "weekday_midday_change": midday_30 - midday_22})
    return report


def v5_no_fallback(t30_root):
    """grep every task's .out/.err log for 'schedule.json not found' and
    'invalid' (case-insensitive) -- both expected zero (this arm never calls
    load_standard_residential_schedules(), so the schedule.json fallback bug
    T19/T27 found cannot trigger here, but the check is cheap and kept for
    parity with the other arms' V5)."""
    logs_dir = os.path.join(t30_root, "logs")
    hits = []
    if not os.path.isdir(logs_dir):
        return hits
    for name in sorted(os.listdir(logs_dir)):
        path = os.path.join(logs_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, errors="replace") as f:
                for i, line in enumerate(f, 1):
                    low = line.lower()
                    if "schedule.json not found" in low or "invalid" in low:
                        hits.append({"log": name, "line_no": i, "text": line.strip()})
        except OSError:
            continue
    return hits


def spread_metrics_all(t30_root, t22_root, t21_root):
    """Household peak-hour spread, computed the same way for all three arms
    (Design: 'Both computed the same way for the full model, the static arm
    and this arm')."""
    report = {"t30_avg_arm": [], "t22_static_arm": [], "t21_full_model": []}
    for year in ("2022", "2030"):
        for arch, city in CELLS_24:
            cell_dir = os.path.join(t30_root, "out", f"{arch}__{city}__{year}")
            m = household_peak_spread(cell_dir, f"avg_{year}")
            m.update({"cell": f"{arch}__{city}", "year": year})
            report["t30_avg_arm"].append(m)
    for arch, city in CELLS_24:
        cell_dir = os.path.join(t22_root, "out", f"{arch}__{city}")
        m = household_peak_spread(cell_dir, "static")
        m.update({"cell": f"{arch}__{city}", "year": "static"})
        report["t22_static_arm"].append(m)
    for year in ("2022", "2030"):
        for arch, city in CELLS_24:
            cell_dir = os.path.join(t21_root, "out", "step8", f"{arch}__{city}")
            m = household_peak_spread(cell_dir, year)
            m.update({"cell": f"{arch}__{city}", "year": year})
            report["t21_full_model"].append(m)
    return report


def main():
    p = argparse.ArgumentParser(description="T30 WP3 average-profile arm collector: V0-V5 + spread metrics.")
    p.add_argument("--t30-root", default="/speed-scratch/o_iseri/2J_revision/T30")
    p.add_argument("--t22-root", default="/speed-scratch/o_iseri/2J_revision/T22")
    p.add_argument("--t21-root", default="/speed-scratch/o_iseri/2J_revision/T21")
    p.add_argument("--code-root", default="/speed-scratch/o_iseri/2J_revision/code_step8/repo")
    p.add_argument("--sched-dir", default="/speed-scratch/o_iseri/2J_revision/T21/sched_activity")
    args = p.parse_args()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from run_avg_arm import _import_step8
    step8 = _import_step8(args.code_root)
    from eppy.modeleditor import IDF
    IDF.setiddname(step8.config.resolve_idd_path())

    print("=== V0 completeness ===")
    for row in v0_completeness(args.t30_root):
        print(row)

    print("\n=== V1 same households (vs T21 Step-8 manifest, BOTH years, paired-pool draw) ===")
    mism = v1_same_households(args.t30_root, args.t21_root)
    if not mism:
        print("V1 PASS -- 24/24 cells match for both years.")
    else:
        print(f"V1 FAIL -- STOP ({len(mism)} cell-year mismatches; any mismatch is a stop, "
              f"manager decision 2026-09-15):")
    for row in mism:
        print(row)

    print("\n=== V2 identity ===")
    for row in v2_identity(step8, args.sched_dir):
        print(row)

    print("\n=== V3 one profile per cell + design levels differ ===")
    for row in v3_one_profile_per_cell(args.t30_root, IDF):
        print(row)

    print("\n=== V4 year differs (weekday midday at-home change) ===")
    for row in v4_year_differs(step8, args.sched_dir):
        print(row)

    print("\n=== V5 no fallback / no invalid lines ===")
    hits = v5_no_fallback(args.t30_root)
    print(f"{len(hits)} hits (expect 0):")
    for h in hits:
        print(h)

    print("\n=== Household peak-hour spread (Mardia circular SD + morning-leaning %) ===")
    spread = spread_metrics_all(args.t30_root, args.t22_root, args.t21_root)
    for group, rows in spread.items():
        print(f"-- {group} --")
        for row in rows:
            print(row)


if __name__ == "__main__":
    main()
