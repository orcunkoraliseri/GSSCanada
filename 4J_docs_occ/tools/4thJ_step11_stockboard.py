# -*- coding: utf-8 -*-
"""4J Step 11, work item 11.6 -- STOCK-SCALE INPUTS FOR `G11.6`, `G11.8`, `G11.18`.

    python 4thJ_step11_stockboard.py --root <4J_docs_occ> --c2-out <dir>
        --diary-diversity reseed [--district it] [--limit N] [--out path.json]

WHAT THIS TOOL DOES, AND WHAT IT DOES NOT
------------------------------------------
`4thJ_11_stockEndUseLoads.md` section 4, work item 11.6: "Gate board, mutation
battery, dossier -- every `G11.x` seen failing its designated mutation". Three
of the still-unscored gates need a stock-scale quantity that no earlier tool
persisted: `G11.6` (per-appliance annual activation counts vs CREST's published
range), `G11.8` (DHW four-event volume mix) and `G11.18` (stock mean litres per
dwelling per day vs Jordan & Vajen's own 200 l/day). `4thJ_step11_aggregate.py`
(work item 11.5, CLOSED) computes `G11.12` only, by design (`S11` in that file);
re-opening it to do more would move a closed work item's own boundary. This
tool exists beside it, for exactly the three quantities 11.5 does not touch.

Like 11.3 and 11.5, this tool IMPORTS the same per-flat trigger loop --
`4thJ_step11_trigger_campaign.py`'s `run_flat` / `prepare_fold` / preflight
chain, never re-implemented -- and runs it over the SAME `C2` population under
the SAME `--diary-diversity` ruling. `run_flat` already returns, per flat:
`cycles` (a per-appliance activation count), `dhw_litres_by_category` and
`dhw_events_by_category`, and `dhw_litres` (the flat's annual DHW total).
`4thJ_step9_trigger.py` lines 1160-1181 show exactly how Step 9's OWN
aggregation turns per-dwelling `cycles` into the
`{appliance_id, n_dwellings_owning, cycles_per_dwelling_year_modelled,
cycles_per_year_published, ratio_modelled_over_published}` row `G9.6`/`G11.6`
score -- this tool reproduces that SAME arithmetic, over flats instead of
Step 9's 100 dwellings, so the downstream gate code need not change at all.

WHAT IT DOES NOT DO
--------------------
It scores nothing. `4thJ_gates_step11.py` (work item 11.6's own gate board)
imports `g9_6`, `g9_8` and `g9_15` from `4thJ_gates_step9.py` UNCHANGED and
feeds them the manifest and per-flat CSV this tool writes -- the same
separation `V11.g` already draws between a tool that produces numbers and the
runner that grades them (11.3's `--scored` refusal, 11.5's `S11`). Restated
here as `S13`: this tool has no `--scored` flag.

It does NOT re-run `G11.12` -- that is already scored, for real, for both
`uk` and `it`, in `outputs_step11/c2_{uk,it}/step11_11-5_{uk,it}_reseed.json`.
This tool never touches the 8,760-length per-timestep series at all (neither
electricity nor DHW): it only needs three SCALAR quantities per flat --
`cycles` (a small per-appliance counter), `dhw_litres_by_category` (four
numbers) and `dhw_litres` (one number) -- so it is cheaper than 11.5's own run,
not more expensive, despite covering three gates instead of one.

WHAT IT COSTS
--------------
No EnergyPlus, no cluster job -- the same per-flat trigger loop 11.3 and 11.5
already ran, at the same order of magnitude of wall-clock (population size,
not model size, `4thJ_11_stockEndUseLoads.md` line 309-310). `--limit` exists
for a smoke run before committing to the full population.
"""
import argparse
import collections
import csv
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
        description="Step 11 work item 11.6: stock-scale inputs for "
                    "G11.6, G11.8 and G11.18. Scores nothing itself.")
    ap.add_argument("--root", required=True, help="the 4J_docs_occ directory")
    ap.add_argument("--c2-out", required=True,
                    help="the (possibly filtered) directory 11.3/11.5 ran on")
    ap.add_argument("--diary-diversity", choices=("replicate", "reseed"),
                    default=None,
                    help="THE AUTHOR'S RULING. No default; same as 11.3/11.5.")
    ap.add_argument("--district", default=None)
    ap.add_argument("--limit", type=int, default=None,
                    help="cap the flat count (a smoke run, never a "
                         "population -- nothing here may be scored from it)")
    ap.add_argument("--out-dir", required=True,
                    help="where enduse_by_dwelling_<fold>.csv and "
                         "step11_stockboard_<fold>.json are written")
    args = ap.parse_args(argv)

    t11 = load_step11_trigger()

    try:
        if args.diary_diversity is None:
            raise t11.Refusal(
                "S9 --diary-diversity is unset and has NO DEFAULT, same as "
                "11.3/11.5. The author ruled %r on %s (%r)."
                % (t11.DIARY_DIVERSITY_RULED, t11.DIARY_DIVERSITY_RULING_DATE,
                   t11.DIARY_DIVERSITY_RULING_SENTENCE))
        if args.diary_diversity != t11.DIARY_DIVERSITY_RULED:
            raise t11.Refusal(
                "S9b --diary-diversity=%s contradicts the ruling on record. "
                "The author ruled %r on %s (%r)."
                % (args.diary_diversity, t11.DIARY_DIVERSITY_RULED,
                   t11.DIARY_DIVERSITY_RULING_DATE,
                   t11.DIARY_DIVERSITY_RULING_SENTENCE))

        trigger = t11.load_trigger()
        assign_mod = t11._load("step10_assign", "4thJ_step10_assign.py")

        cells, cell_paths = t11.read_c2_cells(args.c2_out)
        fold = t11.check_cells(cells, cell_paths)
        district = args.district or (cells[0].get("district")
                                     or cells[0].get("cell_id", "").split("__")[0])
        flats = t11.flats_from_cells(cells)
        if not flats:
            raise t11.Refusal("S3 the `C2` cells carry no drawn flats; there "
                              "is nothing to aggregate")

        t11.check_seam(t11.STEP11_END_USES)

        print("PREFLIGHT (work item 11.6)")
        print("  `C2` cells      : %d from %s" % (len(cells), args.c2_out))
        print("  fold / district : %s / %s" % (fold, district))
        print("  drawn flats     : %d over %d buildings"
              % (len(flats), len(set(f["building_id"] for f in flats))))

        ctx = t11.prepare_fold(args.root, fold, trigger)
        wanted, present = t11.check_runtime_columns(args.root, fold, ctx["mapping"])
        used = t11.check_diary_identity(flats, ctx["by_hid"], fold, assign_mod)
        print("  diary identity  : %d flats bound to %d distinct households "
              "of the %d shipped" % (len(flats), len(used),
                                     t11.STEP7_HOUSEHOLDS_PER_FOLD))

        todo = flats if args.limit is None else flats[:args.limit]

        owners = collections.Counter()
        cycles_sum = collections.Counter()
        dhw_by_cat = collections.Counter()
        ev_by_cat = collections.Counter()
        per_flat_rows = []

        started = time.time()
        for i, flat in enumerate(todo, 1):
            rec = t11.run_flat(flat, ctx, trigger, args.diary_diversity)
            for aid in rec["appliances"]:
                owners[aid] += 1
                cycles_sum[aid] += rec["cycles"].get(aid, 0)
            for k, v in rec.get("dhw_litres_by_category", {}).items():
                dhw_by_cat[k] += v
            for k, v in rec.get("dhw_events_by_category", {}).items():
                ev_by_cat[k] += v
            per_flat_rows.append({
                "hid": rec["hid"],
                "building_id": flat["building_id"],
                "unit_index": flat["unit_index"],
                "n_members": rec["n_members"],
                "n_appliances": len(rec["appliances"]),
                "dhw_litres_per_day": round(rec["dhw_litres"] / 365.0, 3),
                "dhw_litres_per_person_per_day":
                    round(rec["dhw_litres"] / 365.0 / rec["n_members"], 3),
            })
            if i % 1000 == 0 or i == len(todo):
                print("  %d/%d flats aggregated (%.1f s)"
                      % (i, len(todo), time.time() - started))

        n_flats_run = len(todo)

        cycle_table = []
        for aid, app in ctx["mapping"].appliances.items():
            if not owners[aid]:
                continue
            published = app["cycles_per_year"]
            cycle_table.append({
                "appliance_id": aid,
                "appliance_name": app["name"],
                "crest_profile": app["profile"],
                "n_dwellings_owning": owners[aid],
                "cycles_per_dwelling_year_modelled":
                    round(cycles_sum[aid] / float(owners[aid]), 3),
                "cycles_per_year_published": published,
                "ratio_modelled_over_published":
                    round(cycles_sum[aid] / float(owners[aid]) / published, 5)
                    if published else "",
            })

        os.makedirs(args.out_dir, exist_ok=True)
        enduse_path = os.path.join(args.out_dir,
                                   "enduse_by_dwelling_%s.csv" % fold)
        with io.open(enduse_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(per_flat_rows[0].keys()),
                               lineterminator="\n")
            w.writeheader()
            w.writerows(per_flat_rows)
        print("WROTE %s (%d rows)" % (enduse_path, len(per_flat_rows)))

        decl = t11.population_declaration(fold, district, todo, cells, used,
                                          args.diary_diversity, args.c2_out,
                                          cell_paths)

        manifest = {
            "work_item": "11.6",
            "gates_fed": ["G11.6", "G11.8", "G11.18"],
            "campaign": "C2",
            "tool": os.path.basename(__file__),
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "fold": fold,
            "declaration": decl,
            "diary_diversity": args.diary_diversity,
            "n_flats_aggregated": n_flats_run,
            "n_flats_enumerated": len(flats),
            "smoke_run": args.limit is not None,
            "runtime_input_columns_wanted": wanted,
            "runtime_input_columns_present": present,
            "cycles": cycle_table,
            "dhw_litres_by_category": dict(dhw_by_cat),
            "dhw_events_by_category": dict(ev_by_cat),
            "calibration_trace": ctx.get("calib_trace"),
            "enduse_by_dwelling_csv": os.path.basename(enduse_path),
        }
        man_path = os.path.join(args.out_dir,
                                "step11_stockboard_%s%s.json"
                                % (fold, "_smoke" if args.limit else ""))
        with io.open(man_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(manifest, indent=2, sort_keys=True))
        print("WROTE %s" % man_path)
        print("n_flats=%d n_appliances_owned=%d dhw_categories=%d"
              % (n_flats_run, len(cycle_table), len(dhw_by_cat)))
        if args.limit:
            print("!! SMOKE RUN -- --limit was set, this is NOT a population "
                  "and nothing here may be scored from it.")
        return 0
    except t11.Refusal as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
