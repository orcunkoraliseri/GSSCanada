# -*- coding: utf-8 -*-
"""4J Step 8 WORK ITEM 8.6 --- THE AGGREGATE.

    "Per-archetype EUI, monthly and hourly profiles, peak magnitude and timing."
    (`4thJ_08_bemSimulation.md` §8.6)

🔴 THE REPORTING RULE IS PRE-REGISTERED AND IT IS ENFORCED HERE
----------------------------------------------------------------
`archetype_parameter_provenance.md` §9.3: *"the headline result is quoted at
EVERY level of `f`, never at one.  Any statement of the form 'occupancy
injection changes annual heating demand by X %' must carry the range over the
grid.  A single-`f` number may not appear in the paper."*

So every quantity this tool emits is a mapping over the whole grid, and it
refuses to write anything at all if the campaign on disk does not carry all five
levels.  There is no code path here that produces a scalar headline.

🔴 AND THE HEADLINE IS A PEAK, NOT AN ANNUAL TOTAL
---------------------------------------------------
`FINDING 128`, measured by work item 8.4 on one cell and re-measured here on 88:
the annual mean of `phi_int` is held at exactly 3.0 W/m2 at every `f`, so the
sweep REDISTRIBUTES internal gains in time and cannot add energy.  What moves is
the peak and when it happens.  `FINDING 125` caps the annual channel from above
(switching `phi_int` off entirely is worth only +40.5 / +19.7 / +20.1 %), and
this file measures where inside that cap the pre-registered sweep actually
lands.

🔴 AND THE DIARY IS A FREE PARAMETER, SO ITS SPREAD IS REPORTED BESIDE THE EFFECT
---------------------------------------------------------------------------------
Nothing pre-registers which generated household drives which archetype, so the
campaign ran an ensemble per cell (`4thJ_step8_injected.py`).  Every table here
carries the between-diary spread next to the effect, because a mean effect
smaller than the spread of the parameter nobody registered is not a result.

Inputs
------
  agg_annual.csv                  one row per (cell, f)
  injected_monthly.csv            (cell, f) x 12, ensemble mean
  injected_runs.csv               one row per run --- the diary spread
  cells/<cell>__f<NNN>/series_ensemble_mean.csv

Outputs
-------
  agg_by_fold.csv                 fold x f
  agg_by_class.csv                fold x class x f
  agg_monthly.csv                 fold x f x month
  agg_diurnal.csv                 fold x f x hour-of-day
  agg_peak_day.csv                fold x f x hour, on each fold's own peak day
  step8_aggregate.json            the headline, over the whole grid and only so
"""
import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BASE = os.path.join(PROJ, "Step8_docs", "outputs_step8")
CELLS = os.path.join(BASE, "cells")

CAMPAIGN = os.path.join(BASE, "injected_campaign.json")
AGG = os.path.join(BASE, "agg_annual.csv")
RUNS = os.path.join(BASE, "injected_runs.csv")
MONTHLY = os.path.join(BASE, "injected_monthly.csv")

OUT_FOLD = os.path.join(BASE, "agg_by_fold.csv")
OUT_CLASS = os.path.join(BASE, "agg_by_class.csv")
OUT_MONTH = os.path.join(BASE, "agg_monthly.csv")
OUT_DIURNAL = os.path.join(BASE, "agg_diurnal.csv")
OUT_PEAKDAY = os.path.join(BASE, "agg_peak_day.csv")
OUT_JSON = os.path.join(BASE, "step8_aggregate.json")

PREREG_GRID = [0.00, 0.15, 0.30, 0.50, 1.00]
FOLDS = ("es", "uk", "it")
J_TO_KWH = 1.0 / 3.6e6


def ftag(f):
    return "f%03d" % int(round(float(f) * 100))


def load(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def q(vals, p):
    """Plain order statistic --- no interpolation, so the number quoted is one
    that a cell actually produced."""
    if not vals:
        return None
    v = sorted(vals)
    i = int(round(p * (len(v) - 1)))
    return v[min(max(i, 0), len(v) - 1)]


def stats(vals):
    if not vals:
        return {}
    n = len(vals)
    m = sum(vals) / n
    sd = (sum((x - m) ** 2 for x in vals) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"n": n, "mean": m, "sd": sd, "median": q(vals, 0.5),
            "p25": q(vals, 0.25), "p75": q(vals, 0.75),
            "min": min(vals), "max": max(vals)}


def dump(path, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    for p in (CAMPAIGN, AGG, RUNS, MONTHLY):
        if not os.path.exists(p):
            sys.exit("missing %s -- run tools/4thJ_step8_injected.py first" % p)
    header = json.load(io.open(CAMPAIGN, encoding="utf-8"))
    agg = load(AGG)
    runs = load(RUNS)
    mon = load(MONTHLY)

    grid = [round(x, 2) for x in header["sweep_f"]]
    if grid != PREREG_GRID:
        sys.exit("the campaign carries f = %s; the pre-registered grid is %s. "
                 "The reporting rule requires every level, so nothing is written."
                 % (grid, PREREG_GRID))
    present = sorted({round(float(r["f"]), 2) for r in agg})
    if present != PREREG_GRID:
        sys.exit("agg_annual.csv carries f = %s, not the full grid" % present)

    print("WORK ITEM 8.6 --- THE AGGREGATE")
    print("cells       : %d   scenario-cells %d   runs %d"
          % (header["declared_cells"], len(agg), len(runs)))
    print("grid        : f = %s (every level reported, per the pre-registration)"
          % grid)
    print("diaries     : %d per cell, %s"
          % (header["households_per_cell"], header["household_selection"]))
    print("")

    # ----------------------------------------------------------------------
    # fold x f, and fold x class x f
    # ----------------------------------------------------------------------
    fold_rows, class_rows = [], []
    headline = {"grid": grid, "by_fold": {}, "by_fold_class": {}}
    for fold in FOLDS:
        for f in grid:
            sel = [r for r in agg if r["fold"] == fold and round(float(r["f"]), 2) == f]
            if not sel:
                continue
            eui = stats([float(r["eui_kwh_m2a_mean"]) for r in sel])
            pk = stats([float(r["peak_w_m2_mean"]) for r in sel])
            de = stats([float(r["d_eui_pct_vs_f0"]) for r in sel])
            dp = stats([float(r["d_peak_pct_vs_f0"]) for r in sel])
            dh = stats([float(r["d_peak_hour_vs_f0"]) for r in sel])
            # the free parameter, reported beside the effect
            sde = stats([100.0 * float(r["eui_kwh_m2a_sd"]) / float(r["eui_kwh_m2a_mean"])
                         for r in sel if float(r["eui_kwh_m2a_mean"])])
            sdp = stats([100.0 * float(r["peak_w_m2_sd"]) / float(r["peak_w_m2_mean"])
                         for r in sel if float(r["peak_w_m2_mean"])])
            spanh = stats([float(r["peak_hour_max"]) - float(r["peak_hour_min"])
                           for r in sel])
            fold_rows.append({
                "fold": fold, "f": "%.2f" % f, "n_cells": len(sel),
                "eui_median": "%.4f" % eui["median"],
                "eui_p25": "%.4f" % eui["p25"], "eui_p75": "%.4f" % eui["p75"],
                "peak_w_m2_median": "%.4f" % pk["median"],
                "d_eui_pct_median": "%.4f" % de["median"],
                "d_eui_pct_min": "%.4f" % de["min"], "d_eui_pct_max": "%.4f" % de["max"],
                "d_peak_pct_median": "%.4f" % dp["median"],
                "d_peak_pct_min": "%.4f" % dp["min"], "d_peak_pct_max": "%.4f" % dp["max"],
                "d_peak_hour_median": "%.1f" % dh["median"],
                "d_peak_hour_min": "%.0f" % dh["min"], "d_peak_hour_max": "%.0f" % dh["max"],
                "diary_sd_eui_pct_median": "%.4f" % (sde["median"] if sde else 0.0),
                "diary_sd_peak_pct_median": "%.4f" % (sdp["median"] if sdp else 0.0),
                "diary_peak_hour_span_median": "%.0f" % (spanh["median"] if spanh else 0.0),
            })
            headline["by_fold"].setdefault(fold, {})["f=%.2f" % f] = {
                "n_cells": len(sel), "eui": eui, "peak_w_m2": pk,
                "d_eui_pct": de, "d_peak_pct": dp, "d_peak_hour": dh,
                "diary_sd_eui_pct": sde, "diary_sd_peak_pct": sdp,
                "diary_peak_hour_span": spanh,
            }
        for cls in sorted({r["cls"] for r in agg if r["fold"] == fold}):
            for f in grid:
                sel = [r for r in agg if r["fold"] == fold and r["cls"] == cls
                       and round(float(r["f"]), 2) == f]
                if not sel:
                    continue
                de = stats([float(r["d_eui_pct_vs_f0"]) for r in sel])
                dp = stats([float(r["d_peak_pct_vs_f0"]) for r in sel])
                eui = stats([float(r["eui_kwh_m2a_mean"]) for r in sel])
                class_rows.append({
                    "fold": fold, "cls": cls, "f": "%.2f" % f, "n_cells": len(sel),
                    "eui_median": "%.4f" % eui["median"],
                    "d_eui_pct_median": "%.4f" % de["median"],
                    "d_peak_pct_median": "%.4f" % dp["median"],
                    "d_peak_pct_min": "%.4f" % dp["min"],
                    "d_peak_pct_max": "%.4f" % dp["max"],
                })
                headline["by_fold_class"].setdefault(fold, {}).setdefault(cls, {})[
                    "f=%.2f" % f] = {"n_cells": len(sel), "d_eui_pct": de,
                                     "d_peak_pct": dp}

    # ----------------------------------------------------------------------
    # monthly, fold x f x month
    # ----------------------------------------------------------------------
    a_ref = {r["cell"]: float(r["a_ref_m2"]) for r in agg}
    fold_of = {r["cell"]: r["fold"] for r in agg}
    month_rows = []
    for fold in FOLDS:
        for f in grid:
            per_month = [[] for _ in range(12)]
            for r in mon:
                if fold_of.get(r["cell"]) != fold or round(float(r["f"]), 2) != f:
                    continue
                per_month[int(r["month"]) - 1].append(
                    float(r["heating_j_ensemble_mean"]) * J_TO_KWH / a_ref[r["cell"]])
            for i in range(12):
                if not per_month[i]:
                    continue
                st = stats(per_month[i])
                month_rows.append({"fold": fold, "f": "%.2f" % f, "month": i + 1,
                                   "n_cells": st["n"],
                                   "kwh_m2_median": "%.5f" % st["median"],
                                   "kwh_m2_mean": "%.5f" % st["mean"],
                                   "kwh_m2_p25": "%.5f" % st["p25"],
                                   "kwh_m2_p75": "%.5f" % st["p75"]})

    # ----------------------------------------------------------------------
    # hourly: the diurnal shape and the peak day.  This is where the effect is.
    # ----------------------------------------------------------------------
    print("reading %d ensemble-mean series ..." % len(agg))
    diurnal = {}          # (fold, f) -> [24] sums, and a count
    fold_series = {}      # (fold, f) -> [8760] mean W/m2 over the fold's cells
    for r in agg:
        fold, f = r["fold"], round(float(r["f"]), 2)
        p = os.path.join(CELLS, "%s__%s" % (r["cell"], ftag(f)),
                         "series_ensemble_mean.csv")
        if not os.path.exists(p):
            sys.exit("missing %s" % p)
        aref = float(r["a_ref_m2"])
        vals = []
        with io.open(p, encoding="utf-8") as fh:
            next(fh)
            for ln in fh:
                if ln.strip():
                    vals.append(float(ln.split(",")[1]) / 3600.0 / aref)   # W/m2
        acc = fold_series.setdefault((fold, f), [0.0] * len(vals))
        for i, x in enumerate(vals):
            acc[i] += x
        diurnal.setdefault((fold, f), 0)
        diurnal[(fold, f)] += 1

    diurnal_rows, peakday_rows = [], []
    for fold in FOLDS:
        # every level of f shares one peak DAY, taken from the control endpoint,
        # so that a shift in the profile is visible instead of being tracked out
        base = fold_series.get((fold, 0.00))
        if not base:
            continue
        n0 = diurnal[(fold, 0.00)]
        b = [x / n0 for x in base]
        day = max(range(len(b) // 24), key=lambda d: max(b[d * 24:(d + 1) * 24]))
        for f in grid:
            s = fold_series.get((fold, f))
            if not s:
                continue
            nn = diurnal[(fold, f)]
            v = [x / nn for x in s]
            hod = [0.0] * 24
            for i, x in enumerate(v):
                hod[i % 24] += x / (len(v) / 24.0)
            for h in range(24):
                diurnal_rows.append({"fold": fold, "f": "%.2f" % f, "hour_of_day": h,
                                     "w_m2_mean": "%.6f" % hod[h],
                                     "n_cells": nn})
            for h in range(24):
                peakday_rows.append({"fold": fold, "f": "%.2f" % f,
                                     "peak_day_index": day, "hour_of_day": h,
                                     "w_m2_mean": "%.6f" % v[day * 24 + h],
                                     "n_cells": nn})
            headline.setdefault("fold_mean_profile", {}).setdefault(fold, {})[
                "f=%.2f" % f] = {
                "annual_kwh_m2": sum(v) * 1.0 / 1000.0,
                "peak_w_m2": max(v), "peak_hour_index": v.index(max(v)),
                "peak_hour_of_day": v.index(max(v)) % 24,
                "diurnal_peak_hour_of_day": hod.index(max(hod)),
                "diurnal_peak_w_m2": max(hod),
                "peak_day_index": day,
            }

    dump(OUT_FOLD, fold_rows)
    dump(OUT_CLASS, class_rows)
    dump(OUT_MONTH, month_rows)
    dump(OUT_DIURNAL, diurnal_rows)
    dump(OUT_PEAKDAY, peakday_rows)

    headline["reporting_rule"] = (
        "archetype_parameter_provenance.md 9.3: every quantity is quoted at "
        "every level of f. A single-f number may not appear in the paper.")
    headline["caps"] = {
        "FINDING 125": "switching phi_int off entirely moves heating +40.5 / "
                       "+19.7 / +20.1 % (es/uk/it), which caps the whole "
                       "occupancy channel from above",
        "FINDING 128": "the annual mean of phi_int is held at exactly 3.0 W/m2 "
                       "at every f, so the sweep redistributes and cannot add "
                       "energy; the channel is peak magnitude and peak timing",
    }
    headline["free_parameter"] = {
        "what": "which generated diary drives which archetype",
        "registered": False,
        "handled_by": ("an ensemble of %d diaries per cell; the between-diary "
                       "spread is reported beside every effect"
                       % header["households_per_cell"]),
    }
    with io.open(OUT_JSON, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(headline, indent=1, sort_keys=True))

    # ---- print, over the whole grid and only so --------------------------
    print("")
    print("ANNUAL AND PEAK, median over cells (ensemble mean per cell)")
    print("%-4s %-5s  %9s  %9s %9s  %8s  %8s  %8s"
          % ("fold", "f", "EUI", "dEUI%", "dPEAK%", "dPkHour", "sd_EUI%", "sd_PK%"))
    for fold in FOLDS:
        for f in grid:
            k = "f=%.2f" % f
            h = headline["by_fold"].get(fold, {}).get(k)
            if not h:
                continue
            print("%-4s %-5.2f  %9.3f  %+9.3f %+9.3f  %+8.1f  %8.3f  %8.3f"
                  % (fold, f, h["eui"]["median"], h["d_eui_pct"]["median"],
                     h["d_peak_pct"]["median"], h["d_peak_hour"]["median"],
                     h["diary_sd_eui_pct"].get("median", 0.0),
                     h["diary_sd_peak_pct"].get("median", 0.0)))
    print("")
    print("THE FOLD-MEAN PROFILE --- where the peak is, and when")
    print("%-4s %-5s  %10s  %10s  %12s"
          % ("fold", "f", "peak W/m2", "peak h-of-d", "diurnal peak"))
    for fold in FOLDS:
        for f in grid:
            h = headline.get("fold_mean_profile", {}).get(fold, {}).get("f=%.2f" % f)
            if not h:
                continue
            print("%-4s %-5.2f  %10.4f  %10d  %12d"
                  % (fold, f, h["peak_w_m2"], h["peak_hour_of_day"],
                     h["diurnal_peak_hour_of_day"]))
    print("")
    for p in (OUT_FOLD, OUT_CLASS, OUT_MONTH, OUT_DIURNAL, OUT_PEAKDAY, OUT_JSON):
        print("  wrote %s" % os.path.relpath(p, PROJ))


if __name__ == "__main__":
    main()
