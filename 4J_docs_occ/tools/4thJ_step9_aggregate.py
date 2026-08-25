# -*- coding: utf-8 -*-
"""4J Step 9, work item 9.5 -- aggregate and compare, at STOCK SCALE ONLY.

    python 4thJ_step9_aggregate.py --root <4J_docs_occ> [--folds es,uk,it]

Writes `outputs_step9/agg_by_fold.csv`, `agg_diurnal.csv`, `agg_monthly.csv`,
`agg_by_household_size.csv`, `agg_by_appliance.csv` and `step9_aggregate.json`.

🔴 THE SCALE RULE IS ENFORCED IN CODE, NOT ASKED FOR IN PROSE. The source models
validate at 100-500 dwellings; single-dwelling prediction has high residual
variance by construction. So:

  * every quantity written here is a DISTRIBUTION or a MEAN over dwellings --
    there is no code path in this file that emits a single dwelling's series;
  * the tool REFUSES to write anything if a fold carries fewer than
    `MIN_DWELLINGS` dwellings, because an "aggregate" over a handful of
    dwellings is a per-dwelling result wearing an aggregate's name;
  * every distribution carries its spread beside its centre. `FINDING 134` is
    the precedent: an effect smaller than its own between-diary spread is not a
    result, and a mean printed without its spread invites the claim anyway.
"""
import argparse
import collections
import csv
import io
import json
import math
import os
import sys

MIN_DWELLINGS = 100          # the source models' own validation floor
DAYS = 365


class AggregateError(RuntimeError):
    pass


def quantiles(values, qs=(0.05, 0.25, 0.50, 0.75, 0.95)):
    if not values:
        return dict((("q%02d" % int(q * 100)), None) for q in qs)
    s = sorted(values)
    out = {}
    for q in qs:
        i = q * (len(s) - 1)
        lo = int(math.floor(i))
        hi = min(len(s) - 1, lo + 1)
        frac = i - lo
        out["q%02d" % int(q * 100)] = s[lo] * (1 - frac) + s[hi] * frac
    return out


def mean_sd(values):
    if not values:
        return None, None
    m = sum(values) / len(values)
    if len(values) < 2:
        return m, 0.0
    var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return m, math.sqrt(var)


def month_of_hour(h, year=2017):
    """Calendar month for hour `h` of a 365-day year starting 1 January."""
    lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = h // 24
    acc = 0
    for i, n in enumerate(lengths):
        acc += n
        if day < acc:
            return i + 1
    return 12


def load_fold(out_dir, fold):
    man_path = os.path.join(out_dir, "step9_manifest_%s.json" % fold)
    if not os.path.exists(man_path):
        raise AggregateError(
            "fold %s has no manifest. The aggregate refuses to average over a "
            "set it cannot enumerate." % fold)
    m = json.load(io.open(man_path, encoding="utf-8"))
    if not m.get("is_campaign_run"):
        raise AggregateError(
            "fold %s was produced by a PERTURBED run (%s). A perturbed cell "
            "must never reach an aggregate."
            % (fold, json.dumps(m.get("perturbations"))))
    if m["n_dwellings"] < MIN_DWELLINGS:
        raise AggregateError(
            "fold %s carries %d dwellings, fewer than the %d the source models "
            "validate at. An aggregate over that many is a per-dwelling result "
            "with an aggregate's name." % (fold, m["n_dwellings"], MIN_DWELLINGS))
    rows = list(csv.DictReader(io.open(
        os.path.join(out_dir, "enduse_by_dwelling_%s.csv" % fold),
        encoding="utf-8")))
    series = []
    with io.open(os.path.join(out_dir, "stock_series_%s.csv" % fold),
                 encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            series.append((float(r["electricity_w"]), float(r["dhw_l_per_min"])))
    return m, rows, series


def build(root, folds, out_dir):
    by_fold = []
    diurnal = []
    monthly = []
    by_size = []
    by_appliance = []
    summary = {}

    for fold in folds:
        m, rows, series = load_fold(out_dir, fold)
        ts = m["timestep_min"]
        per_day = 24 * 60 // ts
        n_dw = m["n_dwellings"]

        kwh = [float(r["elec_kwh_per_year"]) for r in rows]
        kwh_pp = [float(r["elec_kwh_per_year"]) / int(r["n_members"])
                  for r in rows]
        peak = [float(r["elec_peak_w"]) for r in rows]
        dhw_pd = [float(r["dhw_litres_per_day"]) for r in rows]
        dhw_pp = [float(r["dhw_litres_per_person_per_day"]) for r in rows]

        mk, sk = mean_sd(kwh)
        mp, sp = mean_sd(peak)
        md, sd_ = mean_sd(dhw_pd)
        mpp, spp = mean_sd(dhw_pp)
        row = {
            "fold": fold, "n_dwellings": n_dw, "n_people": m["n_people"],
            "elec_kwh_per_dwelling_year_mean": round(mk, 2),
            "elec_kwh_per_dwelling_year_sd": round(sk, 2),
            "elec_kwh_per_person_year_mean": round(mean_sd(kwh_pp)[0], 2),
            "elec_peak_w_mean": round(mp, 2),
            "elec_peak_w_sd": round(sp, 2),
            "dhw_l_per_dwelling_day_mean": round(md, 3),
            "dhw_l_per_dwelling_day_sd": round(sd_, 3),
            "dhw_l_per_person_day_mean": round(mpp, 3),
            "dhw_l_per_person_day_sd": round(spp, 3),
        }
        for k, v in quantiles(kwh).items():
            row["elec_kwh_" + k] = round(v, 2)
        for k, v in quantiles(dhw_pp).items():
            row["dhw_l_per_person_day_" + k] = round(v, 3)
        by_fold.append(row)

        acc_e = [0.0] * per_day
        acc_d = [0.0] * per_day
        cnt = [0] * per_day
        mon_e = collections.Counter()
        mon_d = collections.Counter()
        for i, (e, d) in enumerate(series):
            slot = i % per_day
            acc_e[slot] += e
            acc_d[slot] += d
            cnt[slot] += 1
            mo = month_of_hour(int(i * ts / 60.0))
            mon_e[mo] += e * ts / 60.0 / 1000.0
            mon_d[mo] += d * ts
        for slot in range(per_day):
            diurnal.append({
                "fold": fold, "slot": slot,
                "hour": round(slot * ts / 60.0, 3),
                "elec_w_per_dwelling": round(acc_e[slot] / cnt[slot] / n_dw, 4),
                "dhw_l_per_min_per_dwelling":
                    round(acc_d[slot] / cnt[slot] / n_dw, 6),
            })
        for mo in range(1, 13):
            monthly.append({
                "fold": fold, "month": mo,
                "elec_kwh_per_dwelling": round(mon_e[mo] / n_dw, 4),
                "dhw_l_per_dwelling": round(mon_d[mo] / n_dw, 3),
            })

        sizes = collections.defaultdict(list)
        for r in rows:
            sizes[int(r["n_members"])].append(float(r["elec_kwh_per_year"]))
        for size in sorted(sizes):
            mm, ss = mean_sd(sizes[size])
            by_size.append({
                "fold": fold, "household_size": size,
                "n_dwellings": len(sizes[size]),
                "elec_kwh_per_dwelling_year_mean": round(mm, 2),
                "elec_kwh_per_dwelling_year_sd": round(ss, 2),
            })

        for c in m["cycles"]:
            by_appliance.append({
                "fold": fold,
                "appliance_id": c["appliance_id"],
                "appliance_name": c["appliance_name"],
                "crest_profile": c["crest_profile"],
                "n_dwellings_owning": c["n_dwellings_owning"],
                "cycles_per_dwelling_year_modelled":
                    c["cycles_per_dwelling_year_modelled"],
                "cycles_per_year_published": c["cycles_per_year_published"],
                "ratio_modelled_over_published":
                    c["ratio_modelled_over_published"],
            })

        summary[fold] = {
            "n_dwellings": n_dw, "n_people": m["n_people"],
            "elec_kwh_per_dwelling_year": [round(mk, 2), round(sk, 2)],
            "dhw_l_per_dwelling_day": [round(md, 3), round(sd_, 3)],
            "dhw_l_per_person_day": [round(mpp, 3), round(spp, 3)],
            "map_md5": m["map_md5"],
            "calibration_saturated": sorted(set(
                a for t in (m.get("calibration_trace") or [])
                for a in (t.get("saturated") or []))),
        }

    def dump(name, rows_):
        if not rows_:
            return
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_[0].keys()),
                               lineterminator="\n")
            w.writeheader()
            w.writerows(rows_)

    dump("agg_by_fold.csv", by_fold)
    dump("agg_diurnal.csv", diurnal)
    dump("agg_monthly.csv", monthly)
    dump("agg_by_household_size.csv", by_size)
    dump("agg_by_appliance.csv", by_appliance)

    doc = {
        "scale": "stock",
        "min_dwellings_enforced": MIN_DWELLINGS,
        "folds": summary,
        "note": ("Every quantity here is a distribution or a mean over "
                 "dwellings, with its spread. No per-dwelling prediction is "
                 "made or implied; G9.13 searches these artefacts for such a "
                 "claim and V9.d refuses a verdict over a subset."),
    }
    io.open(os.path.join(out_dir, "step9_aggregate.json"), "w",
            encoding="utf-8", newline="").write(
        json.dumps(doc, indent=2, sort_keys=True))
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    out_dir = args.out or os.path.join(args.root, "Step9_docs", "outputs_step9")
    doc = build(args.root, [f for f in args.folds.split(",") if f], out_dir)
    for fold, v in sorted(doc["folds"].items()):
        print("%s  dwellings=%d people=%d  elec %.1f +/- %.1f kWh/dw.y  "
              "DHW %.2f +/- %.2f l/dw.day  %.2f +/- %.2f l/person.day"
              % (fold, v["n_dwellings"], v["n_people"],
                 v["elec_kwh_per_dwelling_year"][0],
                 v["elec_kwh_per_dwelling_year"][1],
                 v["dhw_l_per_dwelling_day"][0], v["dhw_l_per_dwelling_day"][1],
                 v["dhw_l_per_person_day"][0], v["dhw_l_per_person_day"][1]))
        if v["calibration_saturated"]:
            print("    saturated (corpus has too little driving activity): %s"
                  % ", ".join(v["calibration_saturated"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
