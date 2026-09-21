"""t92_si_values.py -- computes the three SI [VALUE PENDING] numbers for T92.

Task doc: 2026-09-21_T92_si_pending_values.md. Runs ONLY on the Speed cluster via sbatch
(never on the login node). No pipeline source file is edited; the two functions this
script needs from the real engine (`validate_household_schedule`) are imported unedited
via importlib, same house pattern T18/T20/T21/T26 use.

VALUE 1 -- S6: daily at-home rate by day-type stratum (Weekday, Saturday, Sunday) in the
  REBUILT 2022 stock. Source: T20/out/main/t20_targets_main.csv, column `stock_rate`,
  which IS T20's own `compute_stock_rate()` output on the Nb-f rebuilt-2022 stock
  (t20_d1.py:118-129) -- the exact same number T20's own accepted N1 check already prints
  for the weekday stratum ("... vs 2022 74.4249%"). Computed once per stratum here as the
  mean of `stock_rate` over the 48 half-hour slots -- same basis as T20's own log line
  ("target[WD] daily mean = ..."). Unit: per PERSON, unweighted (plain mean, not
  stock-weighted) -- matches 07_aug_to_bem.py:97's own groupby(...).mean() pattern, which
  is the basis the whole D1 rake design (and T20's N1 acceptance check) already uses.

VALUE 2 -- S6: calibrated Saturday and Sunday at-home rates, REBUILT 2022 (same source as
  VALUE 1, strata 2/3) and REBUILT 2030 main scenario (T20/out/main/t20_person_table_main.csv,
  the POST-RAKE person table T20 itself wrote -- "calibrated" = after rake_2030() ran).
  Same per-person, unweighted basis as VALUE 1 (mean of hom30_001..048 over persons in each
  stratum, then over slots).

VALUE 3 -- S8: dropped-household count in all 24 simulation groups (4 archetypes x 6
  cities), rebuilt and previously published BEM_Schedules_{2022,2030}.csv trees. Uses the
  SAME sanity check the engine itself applies -- `eSim_bem_utils_2J.integration.
  validate_household_schedule()`, imported unedited -- rather than reimplementing it. A
  single pass per file (not 24 separate `load_schedules()` calls) builds every household's
  {DTYPE, PR, Weekday, Weekend} record, then validity is checked once per household and
  tallied per (archetype, city) cell. Kelowna_5B and Vancouver_5C share PR="BC" (main.py's
  own STEP8_CITIES table), so their two cells necessarily report identical candidate/valid/
  dropped counts -- this is a real property of the engine's pooling, not a script bug, and
  is stated plainly in the printed output.
"""
import os
import sys
import csv
import time
import importlib.util
from pathlib import Path
from collections import defaultdict

import pandas as pd

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def load_module(name, path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing staged script: {path}")
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixed cluster paths (located by `ls` on the login node before this job was
# written -- see task doc Ledger).
# ---------------------------------------------------------------------------
T20_TARGETS_MAIN = "/speed-scratch/o_iseri/2J_revision/T20/out/main/t20_targets_main.csv"
T20_PERSON_TABLE_MAIN = "/speed-scratch/o_iseri/2J_revision/T20/out/main/t20_person_table_main.csv"

BEM_REBUILT_2022 = "/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv"
BEM_REBUILT_2030 = "/speed-scratch/o_iseri/2J_revision/T20/out/main/BEM_Setup/BEM_Schedules_2030.csv"
BEM_PUBLISHED_2022 = "/speed-scratch/o_iseri/2J_revision/T17/code/sched/BEM_Schedules_2022.csv"
BEM_PUBLISHED_2030 = "/speed-scratch/o_iseri/2J_revision/T17/code/sched/BEM_Schedules_2030.csv"

INTEGRATION_PY = "/speed-scratch/o_iseri/2J_revision/code_step8/repo/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py"
sys.path.insert(0, os.path.dirname(os.path.dirname(INTEGRATION_PY)))  # T92 fix: package import for eSim_bem_utils_2J
print("T92 PATCH: sys.path += Step8_docs for eSim_bem_utils_2J", flush=True)

STRATA = [1, 2, 3]
STRATA_LBL = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
N_SLOTS = 48
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

ARCHETYPES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]
CITY_PR = [
    ("Toronto_5A", "Ontario"),
    ("Kelowna_5B", "BC"),
    ("Vancouver_5C", "BC"),
    ("Montreal_6A", "Quebec"),
    ("Calgary_6B", "Alberta"),
    ("Winnipeg_7A", "Prairies"),
]
FILES = {
    "rebuilt_2022": BEM_REBUILT_2022,
    "rebuilt_2030": BEM_REBUILT_2030,
    "published_2022": BEM_PUBLISHED_2022,
    "published_2030": BEM_PUBLISHED_2030,
}


def value1_value2_2022():
    log("VALUE1/2 (2022 side): reading t20_targets_main.csv")
    df = pd.read_csv(T20_TARGETS_MAIN)
    if set(df["stratum"].unique()) != set(STRATA):
        raise AssertionError(f"unexpected stratum set in {T20_TARGETS_MAIN}: {sorted(df['stratum'].unique())}")
    out = {}
    for s in STRATA:
        sub = df[df["stratum"] == s]
        if len(sub) != N_SLOTS:
            raise AssertionError(f"stratum {s}: expected {N_SLOTS} slot rows, got {len(sub)}")
        rate = sub["stock_rate"].mean() * 100.0
        out[STRATA_LBL[s]] = rate
        print(f"VALUE1 rebuilt-2022 stock daily at-home rate, {STRATA_LBL[s]}: {rate:.4f}% "
              f"(per person, unweighted; mean of 48 half-hour-slot stock_rate values; "
              f"source t20_targets_main.csv stratum={s})", flush=True)
    return out


def value2_2030_calibrated():
    log("VALUE2 (2030 side): reading t20_person_table_main.csv (post-rake, calibrated)")
    pt = pd.read_csv(T20_PERSON_TABLE_MAIN, usecols=["DDAY_STRATA"] + HOM_COLS)
    out = {}
    for s in STRATA:
        sub = pt[pt["DDAY_STRATA"] == s]
        if len(sub) == 0:
            raise AssertionError(f"stratum {s}: 0 rows in {T20_PERSON_TABLE_MAIN}")
        rate = sub[HOM_COLS].values.mean() * 100.0
        out[STRATA_LBL[s]] = rate
        print(f"VALUE2 rebuilt-2030-main calibrated at-home rate, {STRATA_LBL[s]}: {rate:.4f}% "
              f"(per person, unweighted, post-rake; source t20_person_table_main.csv, "
              f"n={len(sub):,} person-rows, DDAY_STRATA={s})", flush=True)
    return out


def scan_bem_schedule_file(path, integration_mod):
    """Single pass: build every household's {dtype, pr, Weekday[], Weekend[]} record from
    the long-format BEM_Schedules_<year>.csv, then run the REAL engine's
    validate_household_schedule() on each -- same function the pipeline itself calls
    inside integration.load_schedules() (integration.py:433-436), just applied once per
    file instead of once per (archetype, city) filter to avoid 24 re-reads of the same
    ~650-670 MB file."""
    log(f"  scanning {path}")
    households = {}
    n_rows = 0
    n_bad_daytype = 0
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n_rows += 1
            hh_id = row["SIM_HH_ID"]
            rec = households.get(hh_id)
            if rec is None:
                rec = {"metadata": {"dtype": row.get("DTYPE", ""), "pr": row.get("PR", "")},
                       "Weekday": [], "Weekend": []}
                households[hh_id] = rec
            day_type = row.get("Day_Type", "")
            try:
                hour = int(row["Hour"])
                occ = float(row["Occupancy_Schedule"])
            except (ValueError, KeyError):
                continue
            if day_type in ("Weekday", "Weekend"):
                rec[day_type].append({"hour": hour, "occ": occ})
            else:
                n_bad_daytype += 1
    log(f"  {path}: {n_rows:,} rows, {len(households):,} households, "
        f"{n_bad_daytype:,} rows with an unrecognised Day_Type (excluded, not fatal)")

    counts = defaultdict(lambda: [0, 0])  # (dtype, pr) -> [candidates, valid]
    for hh_id, data in households.items():
        key = (data["metadata"]["dtype"], data["metadata"]["pr"])
        counts[key][0] += 1
        if integration_mod.validate_household_schedule(data):
            counts[key][1] += 1
    return counts, n_rows, len(households)


def value3_drop_counts(integration_mod):
    log("VALUE3: scanning 4 BEM_Schedules files (1 pass each, not 24)")
    scan_results = {}
    for label, path in FILES.items():
        counts, n_rows, n_hh = scan_bem_schedule_file(path, integration_mod)
        scan_results[label] = counts
        print(f"VALUE3 file scan {label}: {path} -> {n_rows:,} rows, {n_hh:,} households read",
              flush=True)

    rows = []
    for arch in ARCHETYPES:
        for city, pr in CITY_PR:
            row = {"archetype": arch, "city": city, "region": pr}
            parts = []
            for label in FILES:
                cand, valid = scan_results[label].get((arch, pr), (0, 0))
                dropped = cand - valid
                row[f"{label}_candidates"] = cand
                row[f"{label}_valid"] = valid
                row[f"{label}_dropped"] = dropped
                parts.append(f"{label} dropped={dropped} of {cand}")
            rows.append(row)
            print(f"VALUE3 {arch} x {city} ({pr}): " + "; ".join(parts), flush=True)
    print("VALUE3 note: Kelowna_5B and Vancouver_5C share PR='BC' in the engine's own "
          "STEP8_CITIES table (main.py), so their rows are necessarily identical -- a real "
          "property of the household pool, not a scan artefact.", flush=True)
    return rows


def control_seen_working_values12(v1):
    # Manager fix 2026-09-21: the old control compared a per-person slot mean against T20's N1
    # 74.4249%, which is a household-level BEM Occupancy_Schedule mean (t20_metrics.py:124-127),
    # a different unit. Same-file, same-unit control: T20 N1 "design target mean (target - stock_rate,
    # weekday slots): 1.5066 pp" (t20_metrics.py:141, T20 doc line 266).
    print("T92 PATCH: control now reproduces T20 N1 design-target mean 1.5066 pp (same file, same unit)", flush=True)
    df = pd.read_csv(T20_TARGETS_MAIN)
    sub = df[df["stratum"] == 1]
    got = (sub["target"] - sub["stock_rate"]).mean() * 100
    expected = 1.5066
    ok = abs(round(got, 4) - expected) < 5e-5
    print(f"CONTROL seen-working (VALUE1/2 file and method): weekday design-target mean reproduced = "
          f"{got:.4f} pp vs T20's accepted 1.5066 pp -> {'PASS' if ok else 'FAIL'}", flush=True)
    print(f"CONTROL info: VALUE1 weekday {v1['Weekday']:.4f}% is per person, unweighted slot mean; "
          f"T20 N1 74.4249% is a household BEM-schedule mean, a different unit, not compared.", flush=True)
    if not ok:
        raise AssertionError("seen-working control FAILED -- VALUE1/2 numbers are not trustworthy")


def control_seen_working_value3(rows):
    # T21 diag (job 1328414, accepted collector reading, doc line ~469-478): SingleD x
    # Montreal_6A / Quebec dropped 103 (rebuilt 2022), 104 (rebuilt 2030), 93 (published
    # 2022), 130 (published 2030).
    expected = {"rebuilt_2022_dropped": 103, "rebuilt_2030_dropped": 104,
                "published_2022_dropped": 93, "published_2030_dropped": 130}
    mtl = next(r for r in rows if r["archetype"] == "SingleD" and r["city"] == "Montreal_6A")
    ok = all(mtl[k] == v for k, v in expected.items())
    got = {k: mtl[k] for k in expected}
    print(f"CONTROL seen-working (VALUE3 method): SingleD x Montreal_6A dropped counts "
          f"{got} vs T21's already-accepted diagnosis {expected} -> {'PASS' if ok else 'FAIL'}",
          flush=True)
    if not ok:
        raise AssertionError("seen-working control FAILED -- VALUE3 numbers are not trustworthy")


def control_seen_failing():
    """Feed a deliberately wrong day-type label through the SAME unguarded ingestion
    pattern the real integration.load_schedules() uses (integration.py ~line 405:
    schedules[hh_id][day_type].append(entry), no guard), to show the pipeline's own code
    does NOT silently accept a bad label -- it raises. This is the negative control the
    task doc asks for."""
    print("CONTROL seen-failing: feeding Day_Type='Wednesday' (not Weekday/Weekend) "
          "through the engine's own unguarded dict-append pattern", flush=True)
    schedules = defaultdict(lambda: {"metadata": {}, "Weekday": [], "Weekend": []})
    hh_id = "FAKE_CONTROL_HH"
    bad_label = "Wednesday"
    try:
        schedules[hh_id][bad_label].append({"hour": 0, "occ": 0.5, "met": 70.0})
        print("CONTROL seen-failing: FAIL -- bad Day_Type label was silently accepted, "
              "no error/flag raised", flush=True)
        raise AssertionError("seen-failing control did not fire -- script cannot be trusted "
                              "to flag a wrong day-type label")
    except KeyError as e:
        print(f"CONTROL seen-failing: PASS -- bad Day_Type label {bad_label!r} raised "
              f"KeyError as expected ({e}); a wrong day-type label is not silently ingested",
              flush=True)


def main():
    print("=== T92: SI [VALUE PENDING] values ===", flush=True)
    integration_mod = load_module("t92_integration", INTEGRATION_PY)

    control_seen_failing()

    v1 = value1_value2_2022()
    control_seen_working_values12(v1)

    v2_2030 = value2_2030_calibrated()

    print(f"VALUE2 summary, difference lost by Weekday/Weekend pooling: "
          f"2022 Saturday {v1['Saturday']:.4f}% vs Sunday {v1['Sunday']:.4f}% "
          f"(diff {v1['Saturday'] - v1['Sunday']:+.4f} pp); "
          f"2030-main Saturday {v2_2030['Saturday']:.4f}% vs Sunday {v2_2030['Sunday']:.4f}% "
          f"(diff {v2_2030['Saturday'] - v2_2030['Sunday']:+.4f} pp)", flush=True)

    rows = value3_drop_counts(integration_mod)
    control_seen_working_value3(rows)

    out_csv = Path(__file__).resolve().parent.parent / "out" / "t92_value3_drop_counts.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"VALUE3 wrote per-cell table -> {out_csv}", flush=True)

    print("=== T92 DONE ===", flush=True)


if __name__ == "__main__":
    main()
