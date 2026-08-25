# -*- coding: utf-8 -*-
"""4J Step 8 --- OPEN DECISION 14, THE CHAINING RULE, ON A WATT.

    "Decision 14 therefore closes on the quantity its trigger is defined on,
     which is a WATT."                     (`D-S7-6` ruling, author, 2026-08-22)

    "item 2 -- aggregate coincident peak POWER and heating/cooling ENERGY are
     EnergyPlus outputs. Step 8. Nothing here is a watt."
                                           (`tools/4thJ_step7_chaining.py`)

Work item 7.6's CPU half ran in Step 7 and returned this project's own
pre-registered NULL on every coincidence metric a peak-demand screen is made of.
It could not evaluate `G7.18`, whose trigger is **25 % on peak demand**, because
nothing in Step 7 produces a watt.  This file produces the watts.

WHAT IS RUN, AND WHY EACH CHOICE IS FORCED RATHER THAN PREFERRED
------------------------------------------------------------------
  * **The rule axis** is `4thJ_step7_chaining.RULE_POINTS`, imported and not
    re-declared: `independent`, `habit` at rho = 0.25 / 0.50 / 0.75 / 0.90, and
    `static`.  The emitter's own selftest proves `rho = 0` IS `independent` and
    `rho = 1` IS `static`, so this is ONE axis sampled at six points, not six
    unrelated rules.
  * **Five seeds per rule point**, imported likewise.  The validation document
    pre-registers at least five: *"a single realisation per rule is a curve with
    no error bar, therefore no way to be wrong, therefore no way to fail."*
  * **100 dwellings**, the registered sizing, and they are the SAME 100
    households in every cell (`random.Random(1)`, the pre-screen's own draw), so
    what varies between cells is the chaining rule and the seed and nothing else.
  * **One archetype per fold**, and **one level of `f`**, exactly as the ruling
    sizes it.  The archetype is the fold's first cell by sorted name --- a rule,
    not a choice.  `f = 1.00` is the sweep's upper endpoint, which maximises the
    schedule's influence on the result and therefore makes the chaining
    sensitivity measured here an **upper bound**: conservative for a trigger of
    the form *"if it exceeds 25 %"*.

🔴 THE VERDICT IS WRITTEN BY THE NUMBERS, NOT BY WHOEVER READS THEM
--------------------------------------------------------------------
Pre-registered, and quoted in `4thJ_step7_chaining.py`: *"if the spread across
seeds within a rule exceeds the spread between rules, the experiment has told us
nothing about chaining, and the deliverable is that finding, not a chosen rule."*
Both spreads are computed for every metric and printed side by side, and the
ratio decides.

🔴 WHAT THIS FILE DOES NOT DO
------------------------------
It does not choose the rule.  Decision 14 is the author's; this supplies the
watt the ruling says it closes on, and says plainly which way the number points.

Outputs
-------
  chaining/<fold>/<rule>__seed<NN>/     one retained run per cell, for provenance
  chaining_step8_cells.csv              one row per (fold, rule point, seed)
  chaining_step8.json                   the spreads, the ratios and the verdicts
"""
import argparse
import collections
import csv
import datetime
import importlib
import importlib.util as _ilu
import io
import json
import os
import random
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
ARCH = os.path.join(BASE, "archetypes")
WEATHER = os.path.join(BASE, "weather")
OUT = os.path.join(BASE, "chaining")
IDF_MANIFEST = os.path.join(BASE, "archetype_idf_manifest.csv")
WX_MANIFEST = os.path.join(BASE, "weather_manifest.csv")
CELLS_CSV = os.path.join(BASE, "chaining_step8_cells.csv")
BOARD = os.path.join(BASE, "chaining_step8.json")

SCHED7 = os.path.join(PROJ, "Step7_docs", "outputs_step7")
STEP2 = os.path.join(PROJ, "Step2_docs", "outputs_step2")
CROSSWALK = os.path.join(STEP2, "crosswalk_copresence.csv")
CORPUS = os.path.join(PROJ, "Step3_docs", "outputs_step3", "4J_step3_corpus.jsonl")

S7 = importlib.import_module("4thJ_step7_schedules")
CH = importlib.import_module("4thJ_step7_chaining")
from encoder import load_bit_positions            # noqa: E402


def _load(name, mod):
    spec = _ilu.spec_from_file_location(mod, os.path.join(HERE, name))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SC = _load("4thJ_step8_scenario.py", "step8_scenario")
INJ = _load("4thJ_step8_injected.py", "step8_injected")
C = _load("4thJ_step8_control.py", "step8_control")

# The calendar the 8.1 IDFs declare.  Read from the model below, never assumed;
# this is only the year that satisfies it (V8.i).
SCHEDULE_YEAR = 2017
F_LEVEL = 1.00                 # the sweep's upper endpoint --- an UPPER bound
LEG = "leg5"
J_TO_KWH = 1.0 / 3.6e6
TRIGGER_PCT = 25.0             # G7.18, on peak demand. Not moved, not re-derived.


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def spread(v):
    return (max(v) - min(v)) if v else float("nan")


def run_one(idf_text, epw, outdir, a_ref):
    r = INJ.run_injected(idf_text, epw, outdir)
    errp = os.path.join(outdir, "eplusout.err")
    if r["returncode"] != 0 or not os.path.exists(errp):
        raise RuntimeError("%s failed rc=%s\n%s" % (outdir, r["returncode"],
                                                    r["stdout_tail"]))
    sev, warn, fatal, kinds = C.err_counts(errp)
    hourly, temps, months, mvar, present = C.read_series(
        os.path.join(outdir, "eplusout.csv"))
    return {"hourly_w": [x / 3600.0 for x in hourly], "severe": sev,
            "warnings": warn, "heating_j": sum(hourly),
            "eui": sum(hourly) * J_TO_KWH / a_ref}


def main():
    ap = argparse.ArgumentParser(description="4J Step 8 -- decision 14 on a watt")
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--households", type=int, default=100)
    ap.add_argument("--seeds", default=",".join(str(s) for s in CH.DEFAULT_SEEDS))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--rule-points", default="")
    a = ap.parse_args()

    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    if len(seeds) < 5:
        raise SystemExit(
            "REFUSED: %d seeds. The validation document pre-registers at least "
            "five per rule -- 'a single realisation per rule is a curve with no "
            "error bar, therefore no way to be wrong, therefore no way to "
            "fail'." % len(seeds))
    rule_points = list(CH.RULE_POINTS)
    if a.rule_points:
        want = set(a.rule_points.split(","))
        rule_points = [rp for rp in rule_points if CH._label(*rp) in want]
    if not os.path.exists(C.EPLUS):
        sys.exit("EnergyPlus not found at %s" % C.EPLUS)

    arch = list(csv.DictReader(io.open(IDF_MANIFEST, encoding="utf-8")))
    wx = {r["fold"]: r for r in csv.DictReader(io.open(WX_MANIFEST, encoding="utf-8"))}
    bitpos = load_bit_positions(CROSSWALK)
    cal = S7.year_day_types(SCHEDULE_YEAR)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    folds = [f.strip() for f in a.folds.split(",") if f.strip()]
    n_runs_declared = len(folds) * len(rule_points) * len(seeds) * a.households

    print("OPEN DECISION 14 --- THE CHAINING RULE, ON A WATT")
    print("rule points : %s" % ", ".join(CH._label(*rp) for rp in rule_points))
    print("seeds       : %s" % seeds)
    print("dwellings   : %d per cell, the SAME %d in every cell"
          % (a.households, a.households))
    print("f level     : %.2f  (the sweep's upper endpoint --- an UPPER bound on "
          "the sensitivity)" % F_LEVEL)
    print("runs        : %d EnergyPlus runs declared, %d workers"
          % (n_runs_declared, a.workers))
    print("")

    board = {"work_item": "7.6 / open decision 14, the EnergyPlus half",
             "generated_utc": utcnow(),
             "rule_points": [CH._label(*rp) for rp in rule_points],
             "seeds": seeds, "households": a.households,
             "f": F_LEVEL, "leg": LEG, "schedule_year": SCHEDULE_YEAR,
             "trigger_pct_on_peak_demand": TRIGGER_PCT,
             "sizing_basis": ("the D-S7-6 ruling: one archetype per fold, one f "
                              "level, the pre-registered rule axis x >= 5 seeds "
                              "x 100 dwellings"),
             "energyplus_exe_md5": SC.md5(C.EPLUS),
             "folds": {}, "cells": {}, "verdicts": {}}
    rows = []
    t0 = time.time()
    n_done = 0

    for fold in folds:
        cand = sorted((os.path.splitext(r["idf"])[0], r) for r in arch
                      if r["fold"] == fold)
        cell, arec = cand[0]                       # a rule, not a choice
        epw = os.path.join(WEATHER, wx[fold]["epw"])
        idf_src = os.path.join(ARCH, arec["idf"])
        base_idf = io.open(idf_src, encoding="utf-8").read()
        a_ref = float(arec["a_ref"])

        # V8.i, on the model itself
        want_day = INJ.runperiod_start_day(base_idf)
        got_day = datetime.date(SCHEDULE_YEAR, 1, 1).strftime("%A")
        if want_day != got_day:
            sys.exit("V8.i: schedule year %d starts on a %s, the IDF's RunPeriod "
                     "on a %s" % (SCHEDULE_YEAR, got_day, want_day))

        pool_path = os.path.join(SCHED7, "generated_%s_%s_constrained.jsonl"
                                 % (LEG, fold))
        pools, pool_meta = S7.load_pool(pool_path, STEP2, bitpos)
        prov = str(pool_meta.get("provenance") or "")
        if "NOT REPORTABLE" in prov.upper():
            sys.exit("pool %s carries provenance %r" % (pool_path, prov))
        households = S7.load_households(CORPUS, fold, a.households,
                                        random.Random(1))
        board["folds"][fold] = {
            "cell": cell, "code": arec["code"], "a_ref_m2": a_ref,
            "epw": wx[fold]["epw"], "epw_md5": wx[fold]["epw_md5"],
            "idf_md5": arec["idf_md5"],
            "pool": pool_meta["pool_file"], "pool_md5": pool_meta["pool_md5"],
            "pool_n_days": pool_meta["n_days"],
            "pool_provenance": pool_meta.get("provenance"),
            "n_households": len(households),
            "runperiod_start_day": want_day,
        }
        print("fold %s   cell %-20s  pool %s (%d days)  %d households"
              % (fold, cell, pool_meta["pool_file"], pool_meta["n_days"],
                 len(households)))

        cells = {}
        for rule, rho in rule_points:
            lab = CH._label(rule, rho)
            for seed in seeds:
                rng = random.Random(seed)
                backoff = collections.Counter()
                gseries = []
                for hid, members in households:
                    md = [S7.assemble_person_year(p, cal, rule, rng, pools,
                                                  backoff, rho)
                          for p in members]
                    gseries.append(S7.household_year(md, 60))
                cdir = os.path.join(OUT, fold, "%s__seed%02d" % (lab, seed))
                os.makedirs(cdir)

                # The multiplier files live BESIDE the run directories, never
                # inside them: `run_injected` clears its own directory before it
                # runs, so a schedule written there is deleted before
                # EnergyPlus can read it and the run dies on a Severe.
                sdir = os.path.join(cdir, "_sched")
                os.makedirs(sdir)
                tasks = []
                for k, g in enumerate(gseries):
                    m = SC.multiplier_series(g, F_LEVEL)
                    mcsv = os.path.join(sdir, "d%03d.csv" % k)
                    SC.write_multiplier_csv(mcsv, m, "phi_int_multiplier",
                                            decimals=INJ.MULTIPLIER_DECIMALS)
                    tasks.append({"idf": SC.inject(base_idf, mcsv),
                                  "dir": os.path.join(cdir, "d%03d" % k),
                                  "csv": mcsv, "k": k})

                def _go(t):
                    t["red"] = run_one(t["idf"], epw, t["dir"], a_ref)
                    return t

                with ThreadPoolExecutor(max_workers=a.workers) as ex:
                    list(ex.map(_go, tasks))
                n_done += len(tasks)

                agg = [0.0] * len(tasks[0]["red"]["hourly_w"])
                for t in tasks:
                    for i, x in enumerate(t["red"]["hourly_w"]):
                        agg[i] += x
                ramps = [abs(agg[i] - agg[i - 1]) for i in range(1, len(agg))]
                srt = sorted(agg)
                euis = [t["red"]["eui"] for t in tasks]
                sev = sum(t["red"]["severe"] for t in tasks)
                m = {
                    "fold": fold, "cell": cell, "rule": lab, "seed": seed,
                    "n_dwellings": len(tasks),
                    "peak_aggregate_w": max(agg),
                    "p99_aggregate_w": srt[int(0.99 * (len(srt) - 1))],
                    "trough_aggregate_w": min(agg),
                    "annual_mean_aggregate_w": sum(agg) / len(agg),
                    "max_ramp_w": max(ramps),
                    "p99_ramp_w": sorted(ramps)[int(0.99 * (len(ramps) - 1))],
                    "peak_hour_index": agg.index(max(agg)),
                    "annual_heating_kwh": sum(t["red"]["heating_j"] for t in tasks)
                                          * J_TO_KWH,
                    "eui_mean_kwh_m2a": sum(euis) / len(euis),
                    "severe": sev,
                    "backoff_full_depth_share":
                        backoff[len(S7.STRATUM_FIELDS)] / float(sum(backoff.values())),
                }
                cells[(lab, seed)] = m
                rows.append(m)
                # keep one dwelling's directory for provenance, drop the rest
                for t in tasks:
                    if t["k"] == 0:
                        INJ.thin(t["dir"], ("in.idf", "eplusout.err",
                                            "eplusout.end"))
                    else:
                        shutil.rmtree(t["dir"], ignore_errors=True)
                        os.remove(t["csv"])
                print("  %-16s seed %2d  peak %10.1f W  ramp %9.1f W  "
                      "annual %10.1f kWh  %s  [%d/%d, %.0f s]"
                      % (lab, seed, m["peak_aggregate_w"], m["max_ramp_w"],
                         m["annual_heating_kwh"],
                         "severe=%d" % sev if sev else "clean",
                         n_done, n_runs_declared, time.time() - t0))

        board["cells"][fold] = dict(("%s|%d" % k, v) for k, v in cells.items())

        # ---- the pre-registered spread test, on the watts ------------------
        print("")
        print("  %-26s %13s %13s %10s   %s"
              % ("metric", "seed spread", "rule spread", "ratio", "verdict"))
        verdicts = {}
        for metric in ("peak_aggregate_w", "p99_aggregate_w", "max_ramp_w",
                       "p99_ramp_w", "annual_heating_kwh", "eui_mean_kwh_m2a",
                       "trough_aggregate_w"):
            per_rule = collections.defaultdict(list)
            for (lab, seed), m in cells.items():
                per_rule[lab].append(m[metric])
            within = max(spread(v) for v in per_rule.values())
            means = [sum(v) / len(v) for v in per_rule.values()]
            between = spread(means)
            # A metric on which BOTH spreads are zero has not separated the
            # rules; it has failed to vary at all.  Calling that "RULE > NOISE"
            # because between/within is 0/0 is the vacuity class this project
            # keeps declaring rather than passing.
            if within == 0.0 and between == 0.0:
                ratio = float("nan")
                verdict = "DEGENERATE (no variation at all)"
            elif within == 0.0:
                ratio = float("inf")
                verdict = "RULE > NOISE"
            else:
                ratio = between / within
                verdict = "RULE > NOISE" if ratio > 1.0 else "NOISE DOMINATES"
            lo = min(means)
            pct = (100.0 * between / lo) if lo else float("nan")
            verdicts[metric] = {"seed_spread": within, "rule_spread": between,
                                "ratio": ratio, "verdict": verdict,
                                "rule_spread_pct_of_min": pct,
                                "per_rule_mean": {k: sum(v) / len(v)
                                                  for k, v in per_rule.items()}}
            print("  %-26s %13.4f %13.4f %10.3f   %s"
                  % (metric, within, between, ratio, verdict))
        pk = verdicts["peak_aggregate_w"]
        print("")
        print("  G7.18 trigger is %.0f %% on PEAK DEMAND. Measured rule spread: "
              "%.3f %% of the lowest rule mean --> %s"
              % (TRIGGER_PCT, pk["rule_spread_pct_of_min"],
                 "TRIGGERED" if pk["rule_spread_pct_of_min"] > TRIGGER_PCT
                 else "NOT triggered"))
        verdicts["G7.18"] = {
            "trigger_pct": TRIGGER_PCT,
            "measured_peak_spread_pct": pk["rule_spread_pct_of_min"],
            "triggered": bool(pk["rule_spread_pct_of_min"] > TRIGGER_PCT),
            "basis": ("aggregate coincident peak power over %d dwellings, "
                      "one archetype, f = %.2f (the sweep's upper endpoint, so "
                      "this is an upper bound on the sensitivity)"
                      % (a.households, F_LEVEL)),
        }
        board["verdicts"][fold] = verdicts
        print("")

    board["wall_s"] = round(time.time() - t0, 1)
    board["runs_executed"] = n_done
    board["runs_declared"] = n_runs_declared
    with io.open(CELLS_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with io.open(BOARD, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(board, indent=1, sort_keys=True))

    print("=" * 78)
    print("DECISION 14 --- WHAT THE WATTS SAY")
    print("=" * 78)
    print("%-5s %14s %14s %9s   %s"
          % ("fold", "peak spread %", "seed spread W", "ratio", "G7.18"))
    for fold in folds:
        v = board["verdicts"][fold]["peak_aggregate_w"]
        g = board["verdicts"][fold]["G7.18"]
        print("%-5s %14.3f %14.1f %9.3f   %s"
              % (fold, g["measured_peak_spread_pct"], v["seed_spread"],
                 v["ratio"], "TRIGGERED" if g["triggered"] else "not triggered"))
    print("")
    print("runs : %d executed / %d declared in %.0f s"
          % (n_done, n_runs_declared, board["wall_s"]))
    print("board: %s" % os.path.relpath(BOARD, PROJ))
    print("cells: %s" % os.path.relpath(CELLS_CSV, PROJ))


if __name__ == "__main__":
    main()
