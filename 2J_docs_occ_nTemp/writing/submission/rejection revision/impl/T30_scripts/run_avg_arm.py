#!/usr/bin/env python3
"""
run_avg_arm.py -- T30 / WP3 second simple arm: one average survey profile per
cell and year, same for every household.

Built from a copy of T19/T22's run_static_arm.py (see that file's docstring
for the full schedule_data format background). Only the schedule-SOURCE line
changes: instead of substituting the DOE MidRise standard residential profile
(idf_optimizer.load_standard_residential_schedules()) for every household,
this wrapper substitutes the CELL POOL'S OWN unweighted mean hourly profile --
the mean, over every household integration.load_schedules() returns for this
archetype x province x year (the whole cell pool, not just the n sampled
households), of occ/equip_frac/light_frac/met, per day type (Weekday/Weekend)
and hour. Per-household SHEU design levels (equip_design_w, light_design_w)
and all other non-fraction metadata are kept exactly as in the real
BEM_Schedules_{year}.csv row for that household -- unchanged from the static
arm's own design (T27 Q4 item (3) in the swap-point answer).

No edits to pipeline source. Reuses eSim_bem_utils_2J.main.run_step8_paired_mc's
existing `schedules` extensibility point exactly as run_static_arm.py does --
passing schedules={f'avg_{year}': <dict>} with years=[f'avg_{year}'] makes
that loop's own {y} templating produce Scenario_avg_2022.idf / Scenario_avg_2030.idf
and land each year's output under its own directory.

Design (manager, 2026-09-15_T30_wp3_average_profile_arm.md):
  - Average PER CELL, not per archetype nationally: this keeps the province
    mix and removes only household-to-household differences, making it the
    strongest simple competitor to the full model.
  - Years: 2022 and 2030 only (no 2015 arm -- 2015 schedules were not rebuilt).
  - **Same households, PAIRED POOL (manager addendum, "V1 decided, phase B
    go", 2026-09-15).** The household sample is drawn ONCE per cell from the
    engine's own 2022-and-2030 INTERSECTION pool -- main.py:2029-2034's own
    candidate-pool rule (`common = schedules[y].keys() & ...` for y in both
    years), the SAME code path T21's run_step8_paired_mc() uses -- and that
    SAME draw is used for BOTH years, not a fresh per-year draw from each
    year's own pool. The average profile for each year is the mean over that
    SAME paired pool (not the year's whole pool). This makes the household
    sample match T21's Step-8 manifest exactly (T21 diagnosis 1328414, Q3a:
    130228/79252 for SingleD__Montreal_6A).

schedule_data format required by integration.load_schedules() / consumed by
integration.inject_schedules() -- see run_static_arm.py's docstring for the
full field-by-field citation (integration.py:323-430, idf_optimizer.py:570-624).
Recap only: {hh_id: {'metadata': {...}, 'Weekday': [24 entries], 'Weekend':
[24 entries]}}, each hourly entry {'hour': 0-23, 'occ', 'met', 'equip_frac',
'light_frac'}, hour 0-indexed, fractions 0-1, entry['hour']==0 covers 00:00-01:00
(create_compact_schedule(), integration.py:550-589).
"""
import argparse
import csv as _csv
import os
import random
import sys

DAY_TYPES = ("Weekday", "Weekend")
FRAC_KEYS = ("occ", "met", "equip_frac", "light_frac")

# WP3 V2 identity check weighting (see build_avg_schedules / _v2_identity docstring
# below): a fixed 5/7, 2/7 weekday/weekend proxy. This is NOT a claim about the
# real EnergyPlus RunPeriod calendar (statutory holidays, actual day-of-week of
# Jan 1, etc. are not modelled here) -- the identity being tested holds for ANY
# consistent weight applied to both sides, so the exact value cancels out and
# does not affect whether the check passes. Recorded, not silently assumed away.
WEEKDAY_WEIGHT = 5.0 / 7.0
WEEKEND_WEIGHT = 2.0 / 7.0


def _import_step8(code_root):
    """Point sys.path at the staged repo's Step8_docs dir and import what we need.

    code_root must be the T17-style staged layout: <code_root>/2J_docs_occ_nTemp/
    Step8_docs/{run_bem.py, eSim_bem_utils_2J/} + <code_root>/BEM_Setup/WeatherFile/
    + <code_root>/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/ -- main.py's own
    BASE_DIR is the 4th dirname() up from eSim_bem_utils_2J/main.py, not a CLI
    override, so this nesting is required (main.py:38-39; confirmed by T17/T19).
    """
    step8_dir = os.path.join(code_root, "2J_docs_occ_nTemp", "Step8_docs")
    if step8_dir not in sys.path:
        sys.path.insert(0, step8_dir)
    from eSim_bem_utils_2J import integration, idf_optimizer, config
    from eSim_bem_utils_2J.main import run_step8_paired_mc, _step8_cell_seed
    from run_bem import resolve_cell

    class _Step8NS:
        pass

    ns = _Step8NS()
    ns.integration = integration
    ns.idf_optimizer = idf_optimizer
    ns.config = config
    ns.run_step8_paired_mc = run_step8_paired_mc
    ns.step8_cell_seed = _step8_cell_seed
    ns.resolve_cell = resolve_cell
    return ns


def _load_year_pool(step8, sched_dir, year, dtype, region):
    """One year's integration.load_schedules() pool, or (None, csv_path) if the
    file is missing."""
    csv_path = os.path.join(sched_dir, f"BEM_Schedules_{year}.csv")
    if not os.path.exists(csv_path):
        return None, csv_path
    return step8.integration.load_schedules(csv_path, dwelling_type=dtype, region=region), csv_path


def build_avg_schedules(step8, sched_dir, year, dtype, region):
    """Real per-household metadata (SHEU design levels etc.) + the PAIRED
    POOL'S OWN unweighted mean hourly occ/equip_frac/light_frac/met profile
    substituted for every household's individual diary. This is the T30 swap
    point (T27 Q4: "swap run_static_arm.py's schedule-source line ... for this
    new averaging function"); everything else about the wrapper (sampling,
    injection, E+ run, manifest) is reused unchanged from the static arm's own
    design.

    **Phase-B paired-pool change (manager addendum, "V1 decided, phase B go",
    2026-09-15).** Loads BOTH years' schedule files unconditionally (even
    though this task only simulates ONE of them) and restricts to the
    INTERSECTION of the two years' household-id sets -- main.py:2029-2034's
    own candidate-pool rule, reproduced verbatim (not reimplemented
    differently): `common = keys(schedules[y]) & ...` for y in both years,
    `pool = sorted(common)`. Averaging every household's requested-year data
    that also lies in this SAME intersection means the dict of hh_ids handed
    to run_step8_paired_mc() under `schedules={year_label: avg_schedules}` is
    the SAME set whether this task is running year=2022 or year=2030 -- so
    that function's own internal `_step8_cell_seed(seed, cell_label)` +
    `rng.sample(pool, n)` draws the SAME households for both years, matching
    T21's own paired draw exactly (T21 diagnosis 1328414, Q3a: 130228/79252
    for SingleD__Montreal_6A).

    Returns (avg_dict, avg_profile, real_paired, pool):
      pool        -- sorted list of hh_ids present in BOTH years' pool.
      real_paired -- {hh_id: real[hh_id] for hh_id in pool}, for the
                     REQUESTED year only (V2's "direct" side and the averaging
                     input are both computed on this paired subset -- "the
                     average profile of each year is the mean over that same
                     paired pool", manager decision).
      avg_dict    -- {hh_id: {'metadata': ..., 'Weekday': [24], 'Weekend': [24]}}
                     in exactly the load_schedules() shape, one entry per
                     PAIRED-pool household, all mapped to the SAME averaged
                     'Weekday'/'Weekend' entries (same list object reused is
                     fine -- read-only downstream).
      avg_profile -- {'Weekday': [24 entries], 'Weekend': [24 entries]}, the
                     paired-pool mean itself (for --check-only printing / V2).
    """
    real_2022, csv_2022 = _load_year_pool(step8, sched_dir, "2022", dtype, region)
    real_2030, csv_2030 = _load_year_pool(step8, sched_dir, "2030", dtype, region)
    if not real_2022 or not real_2030:
        missing = csv_2022 if not real_2022 else csv_2030
        print(f"ERROR: missing or empty schedule file needed for the paired pool: {missing}", flush=True)
        return {}, {}, {}, []

    pool = sorted(set(real_2022.keys()) & set(real_2030.keys()))
    if not pool:
        return {}, {}, {}, []

    real_this_year = real_2022 if year == "2022" else real_2030
    real_paired = {hh_id: real_this_year[hh_id] for hh_id in pool}

    n_hh = len(real_paired)
    sums = {
        day_type: [{k: 0.0 for k in FRAC_KEYS} for _ in range(24)]
        for day_type in DAY_TYPES
    }
    for hh_data in real_paired.values():
        for day_type in DAY_TYPES:
            for entry in hh_data[day_type]:
                h = entry["hour"]
                bucket = sums[day_type][h]
                for k in FRAC_KEYS:
                    bucket[k] += entry[k]

    avg_profile = {
        day_type: [
            {"hour": h, **{k: sums[day_type][h][k] / n_hh for k in FRAC_KEYS}}
            for h in range(24)
        ]
        for day_type in DAY_TYPES
    }

    avg = {}
    for hh_id, hh_data in real_paired.items():
        avg[hh_id] = {
            "metadata": hh_data["metadata"],
            "Weekday": [dict(e) for e in avg_profile["Weekday"]],
            "Weekend": [dict(e) for e in avg_profile["Weekend"]],
        }
    return avg, avg_profile, real_paired, pool


def _v2_identity(avg_profile, real):
    """WP3 V2 test (plan): does the mean-over-injected-hours of the AVERAGED
    profile equal the cell-pool mean at-home share computed DIRECTLY from the
    schedule file? Both sides reduce, by linearity of the arithmetic mean, to
    the same grand mean of the underlying (household, day_type, hour) occ
    values -- averaging households first (avg_side) vs averaging each
    household's own weighted annual mean afterwards (direct_side) must agree
    to floating-point precision REGARDLESS of the weekday/weekend weight used,
    as long as the SAME weight is applied on both sides (see WEEKDAY_WEIGHT /
    WEEKEND_WEIGHT above). A non-zero delta beyond float noise means a bug in
    build_avg_schedules() (wrong hour index, swapped day-type key, wrong
    household subset) -- not a claim about the real EnergyPlus calendar.
    """

    def annual_mean_occ(entries_by_type):
        wd_mean = sum(e["occ"] for e in entries_by_type["Weekday"]) / 24.0
        we_mean = sum(e["occ"] for e in entries_by_type["Weekend"]) / 24.0
        return WEEKDAY_WEIGHT * wd_mean + WEEKEND_WEIGHT * we_mean

    avg_side = annual_mean_occ(avg_profile)
    direct_side = sum(annual_mean_occ(hh_data) for hh_data in real.values()) / len(real)
    return avg_side, direct_side, abs(avg_side - direct_side)


def _draw(pool, seed_int, n):
    """One independent draw, reproducing run_step8_paired_mc()'s own sampling
    (main.py:2040-2047): a FRESH random.Random(seed_int) per draw, rng.sample
    without replacement unless pool < n. Identical to run_static_arm.py's _draw
    (T30 Design: "same households ... T21's Step-8 manifest")."""
    rng = random.Random(seed_int)
    if len(pool) >= n:
        return rng.sample(pool, n), False
    return [rng.choice(pool) for _ in range(n)], True


def _check_only(step8, args, dtype, region, label, avg_schedules, avg_profile, real_paired, pool):
    """Prints ONLY what T30's brief asks for: (paired) pool size, the averaged
    profile's 24-hour weekday occupancy, and the V2 identity number -- no IDF
    is written (unlike T19's check-only, which also injected+read back one
    household; that readback happens in the full-run path here instead, for
    BOTH sampled households, giving V3 / design-levels-differ observability --
    see _readback_all). `pool` is the 2022-and-2030 INTERSECTION pool (paired,
    same for both year tasks), not this year's own whole pool."""
    seed_int = step8.step8_cell_seed(args.seed, label)
    sampled_n, repl_n = _draw(pool, seed_int, args.n)

    print(f"CHECK-ONLY cell={label} year={args.year} dtype={dtype} region={region} paired_pool={len(pool)}")
    print(f"Sampled household IDs (paired-pool draw, same for both years), n={args.n} seed={args.seed} "
          f"(with_replacement={repl_n}): {sampled_n}")

    print(f"Averaged profile, Weekday, hour 0-23, occ (fraction 0-1), paired_pool={len(real_paired)} households:")
    print("  " + ", ".join(f"{e['occ']:.6f}" for e in avg_profile["Weekday"]))
    print(f"Averaged profile, Weekend, hour 0-23, occ (fraction 0-1):")
    print("  " + ", ".join(f"{e['occ']:.6f}" for e in avg_profile["Weekend"]))

    avg_side, direct_side, delta = _v2_identity(avg_profile, real_paired)
    print(
        f"V2 identity (weekday/weekend weight={WEEKDAY_WEIGHT:.4f}/{WEEKEND_WEIGHT:.4f}, "
        f"a fixed proxy that cancels on both sides -- see module docstring): "
        f"avg_side={avg_side:.10f} direct_side={direct_side:.10f} delta={delta:.3e}"
    )

    hh0 = sampled_n[0]
    meta = avg_schedules[hh0]["metadata"]
    print(
        f"HH {hh0} design levels from BEM_Schedules_{args.year}.csv metadata (unchanged by "
        f"averaging): equip_design_w={meta.get('equip_design_w')} light_design_w={meta.get('light_design_w')} "
        f"hhsize={meta.get('hhsize')} dtype={meta.get('dtype')}"
    )


def _readback_all(step8, output_dir, year_label):
    """After a full run: read cell_manifest.csv, then for EVERY sampled
    household read back its injected IDF and print the Occ_Sch_HH_* schedule's
    raw fields plus equipment/lighting design levels. Gives a later collector
    everything needed for V3 (byte-identical Occ_Sch VALUES across households --
    strip the Name field, which embeds hh_id, before comparing) and "design
    levels differ" straight from this job's own log -- same pattern T19's
    collector used (reading back the ACTUAL injected IDF, not trusting intent).
    """
    from eppy.modeleditor import IDF

    IDF.setiddname(step8.config.resolve_idd_path())

    man_path = os.path.join(output_dir, "cell_manifest.csv")
    if not os.path.exists(man_path):
        print(f"READBACK WARNING: no cell_manifest.csv at {man_path}, skipping readback.")
        return
    with open(man_path, newline="") as f:
        rows = list(_csv.DictReader(f))

    for row in rows:
        sample = int(row["sample"])
        hh_id = row["sim_hh_id"]
        sample_tag = f"sample_{sample:03d}_HH{hh_id}"
        sample_dir = os.path.join(output_dir, sample_tag, year_label)
        idf_path = os.path.join(sample_dir, f"Scenario_{year_label}.idf")
        if not os.path.exists(idf_path):
            print(f"READBACK WARNING: missing {idf_path}")
            continue
        out_idf = IDF(idf_path)
        occ = [s for s in out_idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == f"Occ_Sch_HH_{hh_id}"]
        equip = [e for e in out_idf.idfobjects["ELECTRICEQUIPMENT"] if f"STEP9_Equip_{hh_id}_" in e.Name]
        light = [e for e in out_idf.idfobjects["LIGHTS"] if f"STEP9_Lights_{hh_id}_" in e.Name]
        print(
            f"READBACK sample={sample} hh_id={hh_id} year={year_label} "
            f"Occ_Sch_raw_fields={(occ[0].obj if occ else 'MISSING')}"
        )
        print(
            f"READBACK sample={sample} hh_id={hh_id} year={year_label} "
            f"equip_design_w={[getattr(e, 'Design_Level', None) for e in equip]} "
            f"light_design_w={[getattr(e, 'Lighting_Level', None) for e in light]}"
        )
        meters_path = os.path.join(sample_dir, "hourly_meters.csv")
        if os.path.exists(meters_path):
            with open(meters_path, newline="") as mf:
                n_rows = sum(1 for _ in mf) - 1  # minus header
            print(f"READBACK sample={sample} hh_id={hh_id} year={year_label} hourly_meters_rows={n_rows}")
        else:
            print(f"READBACK WARNING: missing {meters_path}")


def main():
    p = argparse.ArgumentParser(description="T30 WP3 average-profile arm (one profile per cell/year).")
    p.add_argument("--archetype", required=True)
    p.add_argument("--city", required=True)
    p.add_argument("--year", required=True, choices=["2022", "2030"])
    p.add_argument("--n", type=int, default=50)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--sched-dir", required=True, help="dir containing BEM_Schedules_{year}.csv")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--code-root", required=True, help="staged repo root, T17-style layout")
    p.add_argument(
        "--check-only",
        action="store_true",
        help="Print pool size, averaged Weekday/Weekend occupancy, and the V2 identity number; do not run EnergyPlus.",
    )
    args = p.parse_args()

    step8 = _import_step8(args.code_root)

    cell = step8.resolve_cell(args.archetype, args.city)
    if not cell:
        print(f"ERROR: could not resolve cell {args.archetype} x {args.city} (missing IDF or EPW?)", flush=True)
        sys.exit(2)
    idf_path, epw_path, region, dtype, label = cell

    avg_schedules, avg_profile, real_paired, pool = build_avg_schedules(
        step8, args.sched_dir, args.year, dtype, region
    )
    if not avg_schedules:
        print(f"ERROR: empty paired household pool for dtype={dtype} region={region}", flush=True)
        sys.exit(2)

    year_label = f"avg_{args.year}"

    if args.check_only:
        _check_only(step8, args, dtype, region, label, avg_schedules, avg_profile, real_paired, pool)
        sys.exit(0)

    # Full run: delegate the per-sample loop (sample -> inject -> E+ -> parse ->
    # manifest) to the existing, tested run_step8_paired_mc(), passing our averaged
    # schedule dict under a single synthetic "year" key (avg_2022 / avg_2030) so
    # output filenames fall out of its own {y} templating as Scenario_avg_2022.idf
    # / cell_manifest.csv, landing under their own directory per year.
    res = step8.run_step8_paired_mc(
        idf_path, epw_path, region, dtype,
        n=args.n, seed=args.seed, years=[year_label], sim_mode="standard",
        output_dir=args.output_dir, cell_label=label,
        schedules={year_label: avg_schedules},
    )
    status = res.get("status")
    if status == "ok":
        print(
            f"\nDONE {label} {year_label}: E+ {res['n_run_ok']}/{res['n_jobs']} ok, "
            f"{res['n_hourly_ok']} hourly -> {res['output_dir']}",
            flush=True,
        )
        _readback_all(step8, res["output_dir"], year_label)
        sys.exit(0)
    print(
        f"\nFAILED {label} {year_label}: status={status} | "
        f"E+ {res.get('n_run_ok', '?')}/{res.get('n_jobs', '?')} ok | {res.get('error', '')}",
        flush=True,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
