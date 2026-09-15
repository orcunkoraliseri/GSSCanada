#!/usr/bin/env python3
"""
run_fixed_manifest.py -- T29 Phase B "fixed manifest" wrapper (built from a
COPY of Step8_docs/run_paired_mc.py; NO edits to any repo file). Task doc:
2026-09-15_T29_wp2_scenario_step8_runs.md, "Manager addendum 2" (2026-09-15).

Why this exists. The phase-A premise ("`--years 2030` alone reproduces T21's
households") is FALSE on the rebuilt scenario files. run_step8_paired_mc()'s
own candidate pool is the set of households that PASS
integration.load_schedules()'s internal validate_household_schedule() sanity
check (integration.py:432-438) -- this depends on SCHEDULE CONTENT, not only
on which household IDs exist. Each S-Partial/S-Revert scenario file changes
schedule content, so its own sanity-passed pool differs from T21's 2022+2030
pool (T21 diagnosis 1328414: SingleD Montreal 2022 alone 16,327, 2030 alone
16,326, paired 16,326 -- one household of difference already changes the
seed-42 draw). A fresh `rng.sample()` draw on a scenario file would therefore
sample OTHER households than T21 did, and P1 (pairing) would fail by
construction. The WP2 spec (Sec 4) requires "the same 1,200 households as
T21's 2030 runs" -- so this wrapper never draws. It takes an explicit
`--manifest <T21 Step-8 cell_manifest.csv>` and simulates EXACTLY those
(sample, sim_hh_id) rows, in the same order, on the scenario schedule file,
for year 2030 only.

What is reused verbatim from the engine (no reimplementation): resolve_cell,
integration.load_schedules (same sanity-check filtering path
run_paired_mc.py itself relies on), integration.inject_schedules,
_run_simulations_with_fallback, _step8_job_succeeded, plotting.
get_hourly_meter_data -- the SAME functions main.py's own
run_step8_paired_mc() calls (main.py:2025-2027, 2064-2115). This script's own
code is only the top-level loop: iterate the FIXED manifest instead of
main.py's own `rng.sample(pool, n)`, and write the same output layout
(cell_manifest.csv at the output-dir root, sample_NNN_HH<id>/2030/
hourly_meters.csv per household) plus a new undelivered.csv.

Import path (no repo edits, no need to sit next to the driver). Uses the
SAME mechanism as T30_scripts/run_avg_arm.py's own _import_step8(): a
`--code-root` argument + sys.path.insert(0, <code_root>/2J_docs_occ_nTemp/
Step8_docs). This works without co-locating this file next to
run_paired_mc.py because eSim_bem_utils_2J.main.BASE_DIR is derived from
main.py's OWN __file__ location -- the 4th dirname() up
(main.py:38: `os.path.dirname(...dirname(...dirname(...dirname(abspath(
__file__)))))`) -- not from this script's location or the process cwd. As
long as <code_root>/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/main.py
exists (true for the shared code_step8/repo tree T21/T29/T30 already use
read-only), BASE_DIR resolves to <code_root> regardless of where this
wrapper itself is staged. No chdir is performed (run_avg_arm.py does not
chdir either, and it works -- confirmed by that script's own precedent,
JobID 1328399 COMPLETED).

Households in the fixed manifest that are ABSENT from the scenario file's
sanity-checked pool go to `undelivered.csv` (columns: sample, sim_hh_id,
reason) and are NEVER replaced with another household (task doc: "not
replaced").

Usage:
  python run_fixed_manifest.py --archetype SingleD --city Montreal_6A \
      --manifest /speed-scratch/o_iseri/2J_revision/T21/out/step8/SingleD__Montreal_6A/cell_manifest.csv \
      --sim-mode standard \
      --sched-dir /speed-scratch/o_iseri/2J_revision/T29/sched_lambda_0.0 \
      --output-dir /speed-scratch/o_iseri/2J_revision/T29/out/lambda_0.0/SingleD__Montreal_6A \
      --code-root /speed-scratch/o_iseri/2J_revision/code_step8/repo

Exit codes: 0 = at least one household delivered ok (n_run_ok > 0);
            1 = zero households delivered (all undelivered, all injects
                failed, or all E+ runs failed);
            2 = setup/arg error (bad cell, missing schedule file).
"""
import argparse
import csv
import os
import sqlite3
import sys

YEAR = "2030"  # task doc / addendum 2: "year 2030 only" -- this wrapper never runs 2022.


def _import_step8(code_root):
    """Same import mechanism as T30_scripts/run_avg_arm.py's _import_step8()
    (see that script's own docstring, which cites the same main.py:38
    4th-dirname BASE_DIR rule). code_root must be the T17/T21-style staged
    layout: <code_root>/2J_docs_occ_nTemp/Step8_docs/{run_bem.py,
    eSim_bem_utils_2J/} + <code_root>/BEM_Setup/WeatherFile/ +
    <code_root>/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/. No chdir is
    needed -- BASE_DIR resolves from eSim_bem_utils_2J/main.py's own file
    location once that path exists on disk."""
    step8_dir = os.path.join(code_root, "2J_docs_occ_nTemp", "Step8_docs")
    if step8_dir not in sys.path:
        sys.path.insert(0, step8_dir)
    from eSim_bem_utils_2J import integration, plotting
    from eSim_bem_utils_2J.main import (
        _run_simulations_with_fallback,
        _step8_job_succeeded,
        ENERGYPLUS_EXE,
    )
    from run_bem import resolve_cell

    class _Step8NS:
        pass

    ns = _Step8NS()
    ns.integration = integration
    ns.plotting = plotting
    ns.resolve_cell = resolve_cell
    ns.run_simulations_with_fallback = _run_simulations_with_fallback
    ns.job_succeeded = _step8_job_succeeded
    ns.ENERGYPLUS_EXE = ENERGYPLUS_EXE
    return ns


def read_fixed_manifest(path):
    """Reads a cell_manifest.csv in the SAME shape main.py:2055-2058 writes
    (and T21's Step-8 array produces): header
    sample,sim_hh_id,hhsize,dtype,pr. Only 'sample' and 'sim_hh_id' are used;
    other columns are ignored (they are provenance metadata this wrapper
    re-derives itself from the loaded pool for delivered households).
    Returns an ORDER-PRESERVING list of (sample:int, hh_id:str)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append((int(row["sample"]), str(row["sim_hh_id"])))
    return rows


def main():
    p = argparse.ArgumentParser(
        description="T29 fixed-manifest Step-8 single-cell run (headless, year 2030 only)."
    )
    p.add_argument("--archetype", required=True)
    p.add_argument("--city", required=True)
    p.add_argument("--manifest", required=True, help="T21 Step-8 cell_manifest.csv for this cell")
    p.add_argument("--sim-mode", default="standard", choices=["standard", "weekly", "comparison"])
    p.add_argument("--sched-dir", required=True, help="dir containing BEM_Schedules_2030.csv (the scenario file)")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--code-root", required=True, help="staged repo root, T17/T21-style layout")
    args = p.parse_args()

    step8 = _import_step8(args.code_root)

    cell = step8.resolve_cell(args.archetype, args.city)
    if not cell:
        print(f"ERROR: could not resolve cell {args.archetype} x {args.city} (missing IDF or EPW?).", flush=True)
        sys.exit(2)
    idf_path, epw_path, region, dtype, label = cell

    csv_path = os.path.join(args.sched_dir, f"BEM_Schedules_{YEAR}.csv")
    if not os.path.exists(csv_path):
        print(f"ERROR: missing {csv_path}", flush=True)
        sys.exit(2)
    print(f"  Loading BEM_Schedules_{YEAR}.csv from {args.sched_dir}", flush=True)
    pool = step8.integration.load_schedules(csv_path, dwelling_type=dtype, region=region)
    print(f"  Scenario pool (post sanity-check, dtype={dtype} region={region}) size={len(pool)}", flush=True)

    if not os.path.exists(args.manifest):
        print(f"ERROR: missing manifest {args.manifest}", flush=True)
        sys.exit(2)
    manifest_rows = read_fixed_manifest(args.manifest)
    print(f"  Manifest rows requested: {len(manifest_rows)} (from {args.manifest})", flush=True)

    os.makedirs(args.output_dir, exist_ok=True)

    delivered_manifest_rows = []
    undelivered_rows = []
    jobs = []
    for sample, hh_id in manifest_rows:
        if hh_id not in pool:
            undelivered_rows.append({
                "sample": sample,
                "sim_hh_id": hh_id,
                "reason": "not in scenario pool (absent from schedule file, or dropped by "
                          "validate_household_schedule -- integration.py:432-438; same "
                          "mechanism T21 diagnosis 1328414 identified)",
            })
            continue
        meta = pool[hh_id].get("metadata", {})
        delivered_manifest_rows.append({
            "sample": sample, "sim_hh_id": hh_id, "hhsize": meta.get("hhsize", ""),
            "dtype": meta.get("dtype", ""), "pr": meta.get("pr", ""),
        })
        sample_tag = f"sample_{sample:03d}_HH{hh_id}"
        sc_dir = os.path.join(args.output_dir, sample_tag, YEAR)
        os.makedirs(sc_dir, exist_ok=True)
        idf_out = os.path.join(sc_dir, f"Scenario_{YEAR}.idf")
        try:
            step8.integration.inject_schedules(
                idf_path, idf_out, hh_id, pool[hh_id],
                epw_path=epw_path, sim_results_dir=args.output_dir,
                batch_name=label, run_period_mode=args.sim_mode,
                output_frequency="Hourly",
            )
            jobs.append({"idf": idf_out, "epw": epw_path, "output_dir": sc_dir,
                         "name": f"{sample_tag}|{YEAR}"})
        except Exception as e:
            # Delivered from the manifest/pool standpoint but the driver's own
            # inject step failed -- still undelivered, still never replaced.
            undelivered_rows.append({
                "sample": sample, "sim_hh_id": hh_id,
                "reason": f"inject_schedules FAILED: {e}",
            })
            delivered_manifest_rows.pop()  # do not claim this row as delivered

    # Manifest written up front (same reason as main.py:2076-2081: provenance
    # survives even if E+ crashes mid-run) -- ONLY the rows that actually got
    # an injected IDF, in the order the fixed manifest gave them.
    man_path = os.path.join(args.output_dir, "cell_manifest.csv")
    with open(man_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sample", "sim_hh_id", "hhsize", "dtype", "pr"])
        w.writeheader()
        w.writerows(delivered_manifest_rows)

    undel_path = os.path.join(args.output_dir, "undelivered.csv")
    with open(undel_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sample", "sim_hh_id", "reason"])
        w.writeheader()
        w.writerows(undelivered_rows)
    print(f"  Delivered manifest rows: {len(delivered_manifest_rows)}  "
          f"Undelivered: {len(undelivered_rows)} -> {undel_path}", flush=True)

    if not jobs:
        print(f"\nFAILED {label}: no jobs built (0/{len(manifest_rows)} households resolved).", flush=True)
        sys.exit(1)

    print(f"  Running {len(jobs)} EnergyPlus jobs ({len(jobs)} HH x 1 yr)...", flush=True)
    step8.run_simulations_with_fallback(jobs, step8.ENERGYPLUS_EXE)

    n_run_ok = sum(1 for j in jobs if step8.job_succeeded(j["output_dir"]))

    n_ok = 0
    for job in jobs:
        sql_path = os.path.join(job["output_dir"], "eplusout.sql")
        if not os.path.exists(sql_path):
            continue
        try:
            conn = sqlite3.connect(sql_path)
            hourly = step8.plotting.get_hourly_meter_data(conn)
            conn.close()
            if hourly:
                meters = list(hourly.keys())
                nrows = max(len(v) for v in hourly.values())
                out_csv = os.path.join(job["output_dir"], "hourly_meters.csv")
                with open(out_csv, "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["hour"] + meters)
                    for h in range(nrows):
                        w.writerow([h] + [hourly[m][h] if h < len(hourly[m]) else "" for m in meters])
                n_ok += 1
        except Exception as e:
            print(f"  [parse WARN] {job['name']}: {e}", flush=True)

    if n_run_ok == len(jobs):
        status = "ok"
    elif n_run_ok > 0:
        status = "partial"
    else:
        status = "error"

    print(f"\nDONE {label}: E+ {n_run_ok}/{len(jobs)} ok, {n_ok} hourly -> {args.output_dir}", flush=True)
    print(f"  status={status}  requested={len(manifest_rows)}  "
          f"delivered_manifest_rows={len(delivered_manifest_rows)}  undelivered={len(undelivered_rows)}",
          flush=True)
    sys.exit(0 if n_run_ok > 0 else 1)


if __name__ == "__main__":
    main()
