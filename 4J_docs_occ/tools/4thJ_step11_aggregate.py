# -*- coding: utf-8 -*-
"""4J Step 11, work item 11.5 -- STOCK-SCALE AGGREGATION, `G11.12` only.

    python 4thJ_step11_aggregate.py --root <4J_docs_occ> --c2-out <dir>
        --diary-diversity reseed [--district it] [--limit N] [--out path.json]

WHAT THIS TOOL DOES, AND WHY IT IS NOT A RE-IMPLEMENTATION
------------------------------------------------------------
`4thJ_11_stockEndUseLoads.md` section 4 defines work item 11.5 as "stock-scale
aggregation -- `G11.12` at real neighbourhood scale, with the population
declaration `G11.16` requires". `G11.12` inherits `G9.12` verbatim (section 2):
aggregate load shape over >= 100 dwellings against CREST's own published
activity statistics, R2 >= 0.85, band unmoved.

This tool re-runs 11.3's own trigger loop -- `4thJ_step11_trigger_campaign.py`,
IMPORTED, never re-implemented -- over the SAME `C2` population and the SAME
`--diary-diversity` ruling. `run_flat` already returns the two 8,760-long
per-timestep series (`elec_ts`, `dhw_ts`); 11.3's own manifest discards them
(`summarise()`) to keep a 30k-flat output file readable. This tool keeps them
only long enough to sum them ELEMENTWISE into one stock-scale series -- 8,760
numbers regardless of population size -- which is the only way to get a
diurnal load SHAPE at this scale without writing an unreadable per-flat
time-series file.

`G9.12`'s own scoring code -- `crest_expected_diurnal`, `r_squared`, `_rebin`,
`load_crest_activity_statistics`, `G9_12_R2_MIN` -- is IMPORTED from
`4thJ_gates_step9.py` and run UNCHANGED against the bigger denominator. Section
2's rule ("the mapping is not re-authored") applies equally to the scorer:
re-implementing CREST's expected-diurnal calculation here would be a second
opinion, not an inheritance -- the same argument `4thJ_gates_step11.py` makes
for importing `g9_1`-`g9_4`, and `4thJ_step11_trigger_campaign.py` makes for
importing `simulate_dwelling`.

WHAT IT DOES NOT DO
--------------------
It computes and reports ONLY `G11.12`. The full eighteen-gate `G11.x` board and
its mutation battery are work item 11.6, not this tool -- the same separation
11.3's `--scored` refusal (`S7`) draws. Restated here as `S11`: this tool has
no `--scored` flag and no path to score anything but `G11.12`.

WHAT IT COSTS
--------------
No EnergyPlus, no cluster job -- the same per-flat trigger loop 11.3 already
ran once, so the wall-clock cost is the same order of magnitude as 11.3's own
run for the same population (`4thJ_11_stockEndUseLoads.md` line 309-310:
population size, not model size, and Step 11 runs entirely locally). `--limit`
exists for a smoke run before committing to the full population, mirroring
11.3's own four-cell smoke that caught three harness defects before the real
campaign (`Step11_docs/docs/2026-09-08_work-item-11.3_trigger-campaign-runner-built.md`).
"""
import argparse
import importlib.util
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def load_step11_trigger():
    path = os.path.join(HERE, "4thJ_step11_trigger_campaign.py")
    spec = importlib.util.spec_from_file_location("step11_trigger_campaign", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step11_trigger_campaign"] = mod
    spec.loader.exec_module(mod)
    return mod


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Step 11 work item 11.5: stock-scale aggregation, "
                    "G11.12 only. Scores nothing else.")
    ap.add_argument("--root", required=True, help="the 4J_docs_occ directory")
    ap.add_argument("--c2-out", required=True,
                    help="the (possibly filtered) directory 11.3 ran on")
    ap.add_argument("--diary-diversity", choices=("replicate", "reseed"),
                    default=None,
                    help="THE AUTHOR'S RULING. No default; same as 11.3.")
    ap.add_argument("--district", default=None)
    ap.add_argument("--limit", type=int, default=None,
                    help="cap the flat count (a smoke run, never a "
                         "population -- G11.12 may not be reported from it)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    t11 = load_step11_trigger()

    try:
        if args.diary_diversity is None:
            raise t11.Refusal(
                "S9 --diary-diversity is unset and has NO DEFAULT, same as "
                "11.3. The author ruled %r on %s (%r)."
                % (t11.DIARY_DIVERSITY_RULED, t11.DIARY_DIVERSITY_RULING_DATE,
                   t11.DIARY_DIVERSITY_RULING_SENTENCE))
        if args.diary_diversity != t11.DIARY_DIVERSITY_RULED:
            raise t11.Refusal(
                "S9b --diary-diversity=%s contradicts the ruling on record. "
                "The author ruled %r on %s (%r). Running the other mode "
                "needs a second sentence, recorded beside the first."
                % (args.diary_diversity, t11.DIARY_DIVERSITY_RULED,
                   t11.DIARY_DIVERSITY_RULING_DATE,
                   t11.DIARY_DIVERSITY_RULING_SENTENCE))

        trigger = t11.load_trigger()
        assign_mod = t11._load("step10_assign", "4thJ_step10_assign.py")
        gates9 = t11.load_step9_gates()

        cells, cell_paths = t11.read_c2_cells(args.c2_out)
        fold = t11.check_cells(cells, cell_paths)
        district = args.district or (cells[0].get("district")
                                     or cells[0].get("cell_id", "").split("__")[0])
        flats = t11.flats_from_cells(cells)
        if not flats:
            raise t11.Refusal("S3 the `C2` cells carry no drawn flats; there "
                              "is nothing to aggregate")

        t11.check_seam(t11.STEP11_END_USES)

        stats_path = os.path.join(args.root, "Step9_docs", "outputs_step9",
                                  "sources", "crest_activity_statistics_wd.csv")
        if not os.path.exists(stats_path):
            raise t11.Refusal(
                "S11 CREST's published activity statistics are not on disk "
                "(%s); `G11.12` cannot be scored without the reference "
                "profile. NOT a pass, NOT a fail -- unscoreable." % stats_path)

        print("PREFLIGHT (work item 11.5)")
        print("  `C2` cells      : %d from %s" % (len(cells), args.c2_out))
        print("  fold / district : %s / %s" % (fold, district))
        print("  drawn flats     : %d over %d buildings"
              % (len(flats), len(set(f["building_id"] for f in flats))))

        ctx = t11.prepare_fold(args.root, fold, trigger)
        t11.check_runtime_columns(args.root, fold, ctx["mapping"])
        used = t11.check_diary_identity(flats, ctx["by_hid"], fold, assign_mod)
        print("  diary identity  : %d flats bound to %d distinct households "
              "of the %d shipped" % (len(flats), len(used),
                                     t11.STEP7_HOUSEHOLDS_PER_FOLD))

        stats = gates9.load_crest_activity_statistics(stats_path)

        todo = flats if args.limit is None else flats[:args.limit]
        per_day = 24 * 60 // t11.TIMESTEP_MIN

        stock_elec = None
        stock_dhw = None
        n_steps = None
        household_sizes = []

        started = time.time()
        for i, flat in enumerate(todo, 1):
            rec = t11.run_flat(flat, ctx, trigger, args.diary_diversity)
            elec_ts = rec["elec_ts"]
            dhw_ts = rec["dhw_ts"]
            if stock_elec is None:
                n_steps = len(elec_ts)
                stock_elec = [0.0] * n_steps
                stock_dhw = [0.0] * n_steps
            elif len(elec_ts) != n_steps:
                raise t11.Refusal(
                    "S12 flat %s/%s/u%s returned a %d-step series, not %d -- "
                    "the stock series cannot be summed elementwise across an "
                    "inconsistent length."
                    % (flat["building_id"], flat["case"], flat["unit_index"],
                       len(elec_ts), n_steps))
            for j in range(n_steps):
                stock_elec[j] += elec_ts[j]
                stock_dhw[j] += dhw_ts[j]
            household_sizes.append(rec["n_members"])
            if i % 1000 == 0 or i == len(todo):
                print("  %d/%d flats aggregated (%.1f s)"
                      % (i, len(todo), time.time() - started))

        n_flats_run = len(todo)

        acc = [0.0] * per_day
        cnt = [0] * per_day
        for j, e in enumerate(stock_elec):
            b = j % per_day
            acc[b] += e
            cnt[b] += 1
        ours = [acc[b] / cnt[b] / n_flats_run if cnt[b] else 0.0
                for b in range(per_day)]

        occ_dist = {}
        for s in household_sizes:
            key = min(5, s)
            occ_dist[key] = occ_dist.get(key, 0.0) + 1.0 / n_flats_run

        ref144 = gates9.crest_expected_diurnal(ctx["mapping"], stats,
                                               occ_dist, ctx["hazards"])
        ref = gates9._rebin(ref144, per_day)
        r2 = gates9.r_squared(ours, ref)

        if r2 is None:
            verdict, note = "NOT_EVALUABLE", (
                "one of the two diurnal profiles is constant -- R2 is "
                "undefined, which is not agreement")
        elif r2 >= gates9.G9_12_R2_MIN:
            verdict, note = "PASS", (
                "mean diurnal appliance power against CREST's own published "
                "activity statistics: R2=%.4f >= %.2f"
                % (r2, gates9.G9_12_R2_MIN))
        else:
            verdict, note = "FAIL", (
                "mean diurnal appliance power against CREST's own published "
                "activity statistics: R2=%.4f below %.2f"
                % (r2, gates9.G9_12_R2_MIN))

        decl = t11.population_declaration(fold, district, todo, cells, used,
                                          args.diary_diversity, args.c2_out,
                                          cell_paths)

        manifest = {
            "work_item": "11.5",
            "gate": "G11.12",
            "campaign": "C2",
            "tool": os.path.basename(__file__),
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "declaration": decl,
            "diary_diversity": args.diary_diversity,
            "n_flats_aggregated": n_flats_run,
            "n_flats_enumerated": len(flats),
            "smoke_run": args.limit is not None,
            "per_day_bins": per_day,
            "ours_mean_diurnal_w_per_dwelling": ours,
            "crest_reference_diurnal_w_per_dwelling": ref,
            "occupancy_distribution": occ_dist,
            "r_squared": r2,
            "r_squared_min": gates9.G9_12_R2_MIN,
            "G11.12": {"verdict": verdict, "n": n_flats_run, "note": note},
        }
        out_dir = os.path.join(args.root, "Step11_docs", "outputs_step11",
                               "c2_%s" % fold)
        os.makedirs(out_dir, exist_ok=True)
        name = "step11_11-5_%s_%s%s.json" % (
            fold, args.diary_diversity, "_smoke" if args.limit else "")
        path = args.out or os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(manifest, indent=2, sort_keys=True))
        print("WROTE %s" % path)
        print("G11.12: %s (R2=%s, n=%d)"
              % (verdict, ("%.4f" % r2) if r2 is not None else "undefined",
                 n_flats_run))
        if args.limit:
            print("!! SMOKE RUN -- --limit was set, this is NOT a population "
                  "and G11.12 may not be reported from it.")
        return 0
    except t11.Refusal as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
