# -*- coding: utf-8 -*-
"""5J WP1 design tables. One script, fixed seed, byte-identical reruns.

Usage:  5thJ_design_tables.py [--seed 5] [--out DIR]

Writes to Step2_docs/outputs_step2 (or --out): buildings.csv, households.csv, climates.csv,
pilot_runs.csv, design_md5.txt.

Licence rule (households v2): diary-derived files read = the Spain+Italy corpus copy (md5 checked,
refused otherwise) and the weight columns of the Spain and Italy episode parquets.  UK households are drawn by tools/5thJ_design_households_uk.py, run by the author.
Nothing is imported from 4J.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT5 = os.path.dirname(HERE)
OUT_DEFAULT = os.path.join(ROOT5, "Step2_docs", "outputs_step2")
DATA = r"C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate"
CORPUS_ES_IT = os.path.join(DATA, "inputs", "4J_step3_corpus_es_it.jsonl")
CORPUS_ES_IT_MD5 = "1a5163445291b54114832e192b0d9a05"
MANIFEST = os.path.join(os.path.dirname(ROOT5), "4J_docs_occ", "Step8_docs", "outputs_step8",
                        "archetype_idf_manifest.csv")
WEATHER_JSON = os.path.join(DATA, "weather", "epw", "weather_score_5J.json")
OPENUBEM_EPW = r"C:\Users\o_iseri\Desktop\OpenUBEM\openubem\data\weather"

CLASSES = ["SFH", "TH", "MFH", "AB"]
COUNTRIES = ["es", "uk", "it"]
PER_CLASS = 10
INFIL_RANGE = (0.3, 1.0)      # fallback: TABULA rows carry no range (see state file)
NORTH_RANGE = (0.0, 360.0)
N_HH = 60
N_VAL = 10
N_TEST = 10
NO_WEIGHT = {}   # 5J change (households v2): country -> hids dropped for lack of a weight

# nine climates: (country, city, year, site key in weather_score_5J.json or None, fixed path or None)
CLIMATES = [
    ("es", "Madrid", 2010, None, os.path.join(OPENUBEM_EPW, "es_madrid_2009_2010_y2010.epw")),
    ("es", "Valencia", 2010, "es_valencia", None),
    ("es", "Seville", 2010, "es_seville", None),
    ("uk", "London", 2014, None, os.path.join(OPENUBEM_EPW, "uk_london_2014_2015_y2014.epw")),
    ("uk", "Birmingham", 2014, "uk_birmingham", None),
    ("uk", "Manchester", 2014, "uk_manchester", None),
    ("it", "Bologna", 2014, None, os.path.join(OPENUBEM_EPW, "it_bologna_2013_2014_y2014.epw")),
    ("it", "Turin", 2014, "it_turin", None),
    ("it", "Milan", 2014, "it_milan", None),
]
# RMSE / GHI for the three OpenUBEM files, read from Step2_docs/impl/2026-09-29_wp1_weather.md
# (batch 1 table, scored with the 4J rule).  The score json holds only the 5J-made files.
OPENUBEM_SCORE = {"Madrid": (4.727, 1700), "London": (1.613, 1077), "Bologna": (3.666, 1377)}


def md5(path):
    h = hashlib.md5()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path, header, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def rng_for(seed, *parts):
    return random.Random("|".join([str(seed)] + [str(p) for p in parts]))


# ------------------------------------------------------------------ buildings
def lhs(rng, n, lo, hi, nd):
    perm = list(range(n))
    rng.shuffle(perm)
    return [round(lo + (perm[i] + rng.random()) / n * (hi - lo), nd) for i in range(n)]


def load_manifest(path=MANIFEST):
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build_buildings(seed, manifest):
    out = []
    for c in COUNTRIES:
        n = 0
        for cls in CLASSES:
            rows = [r for r in manifest if r["fold"] == c and r["cls"] == cls]
            periods = sorted(r["cell_period"] for r in rows)
            if len(set(periods)) != len(periods):
                raise ValueError("duplicate period in %s %s" % (c, cls))
            rng = rng_for(seed, "bld", c, cls)
            chosen = periods + rng.sample(periods, PER_CLASS - len(periods))
            chosen.sort()
            infil = lhs(rng, PER_CLASS, INFIL_RANGE[0], INFIL_RANGE[1], 4)
            north = lhs(rng, PER_CLASS, NORTH_RANGE[0], NORTH_RANGE[1], 2)
            code_of = dict((r["cell_period"], r["code"]) for r in rows)
            for i, p in enumerate(chosen):
                n += 1
                out.append({"building_id": "%s_B%02d" % (c, n), "country": c, "class": cls,
                            "archetype_code": code_of[p], "period": p,
                            "infiltration_ach": "%.4f" % infil[i],
                            "north_axis_deg": "%.2f" % north[i], "pilot": 0})
    return out


def pick_pilot_buildings(seed, buildings):
    """Spain: one per class plus one extra (a second one from a seeded class)."""
    rng = rng_for(seed, "pilot_bld")
    es = [b for b in buildings if b["country"] == "es"]
    pick = []
    for cls in CLASSES:
        pick.append(rng.choice([b for b in es if b["class"] == cls]))
    extra_cls = rng.choice(CLASSES)
    pool = [b for b in es if b["class"] == extra_cls and b not in pick]
    pick.append(rng.choice(pool))
    for b in pick:
        b["pilot"] = 1
    return [b["building_id"] for b in pick]


# ------------------------------------------------------------------ households
def read_household_sizes(corpus_path, country):
    """hid -> number of distinct pid in the corpus for that country (file order kept)."""
    hh = collections.OrderedDict()
    with io.open(corpus_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["country"] != country:
                continue
            hh.setdefault(r["hid"], set()).add(r["pid"])
    return collections.OrderedDict((k, len(v)) for k, v in hh.items())


def alloc(total, counts):
    """Largest-remainder allocation of `total` over strata proportional to `counts` (dict)."""
    n = float(sum(counts.values()))
    base, rem = {}, []
    for k in sorted(counts):
        q = total * counts[k] / n
        base[k] = int(q)
        rem.append((q - int(q), -k, k))
    left = total - sum(base.values())
    for _, _, k in sorted(rem, reverse=True)[:left]:
        base[k] += 1
    for k in base:
        if base[k] > counts[k]:
            raise ValueError("stratum %r asked %d of %d" % (k, base[k], counts[k]))
    return base


EPISODES = {   # 5J change (households v2): weight source, Spain and Italy only (not UK data)
    "es": os.path.join(os.path.dirname(ROOT5), "4J_docs_occ", "Step1_docs", "outputs_step1",
                       "episodes_spain.parquet"),
    "it": os.path.join(os.path.dirname(ROOT5), "4J_docs_occ", "Step1_docs", "outputs_step1",
                       "episodes_italy.parquet"),
}


def read_household_weights(parquet_path, weight_col="weight_ind", strict_constant=False):
    """5J change (households v2): hid -> weight of the member with the lowest pid (weight columns only).
    strict_constant: stop if a household has two different values (Italy coefin must be constant)."""
    import pandas as pd
    d = pd.read_parquet(parquet_path, columns=["hid", "pid", weight_col]).drop_duplicates()
    if strict_constant:
        bad = int((d.groupby("hid")[weight_col].nunique(dropna=False) > 1).sum())
        if bad:
            sys.exit("STOP: %d households have more than one %s value" % (bad, weight_col))
    d = d.sort_values(["hid", "pid"], kind="mergesort").drop_duplicates("hid", keep="first")
    return dict((str(h), (None if w != w else float(w))) for h, w in zip(d["hid"], d[weight_col]))


def draw_households(seed, country, sizes, weights):
    """60 households stratified by size (v1 counts), drawn without replacement with probability
    proportional to the survey weight (5J change (households v2)).  Key = log(u)/w, the same order as
    u**(1/w) without the precision loss for w ~ 1e4; the largest keys are taken.
    Hids without a weight (missing or <= 0) are dropped from the draw; their number is in NO_WEIGHT."""
    by_size = collections.defaultdict(list)
    dropped = 0
    for hid, s in sizes.items():
        w = weights.get(hid)
        if w is None or not w > 0:
            dropped += 1
            continue
        by_size[s].append(hid)
    NO_WEIGHT[country] = dropped
    take = alloc(N_HH, dict((s, len(v)) for s, v in by_size.items()))
    rng = rng_for(seed, "hh", country)
    drawn = []
    for s in sorted(take):
        keyed = sorted(((math.log(1.0 - rng.random()) / weights[hid], hid) for hid in by_size[s]),
                       reverse=True)
        for _, hid in keyed[:take[s]]:
            drawn.append((s, hid))
    rng.shuffle(drawn)
    counts = collections.Counter(s for s, _ in drawn)
    v_take = alloc(N_VAL, counts)
    rest = dict((s, counts[s] - v_take.get(s, 0)) for s in counts if counts[s] - v_take.get(s, 0) > 0)
    t_take = alloc(N_TEST, rest)
    seen_v, seen_t = collections.Counter(), collections.Counter()
    out = []
    for i, (s, hid) in enumerate(drawn, 1):
        if seen_v[s] < v_take.get(s, 0):
            sp = "val"
            seen_v[s] += 1
        elif seen_t[s] < t_take.get(s, 0):
            sp = "test"
            seen_t[s] += 1
        else:
            sp = "dev"
        out.append({"household_id": "%s_%s" % (country, hid), "country": country, "hid": hid,
                    "size": s, "weight": "%.6f" % weights[hid], "draw_order": i, "split_draft": sp, "pilot": 0})
    return out


HH_HEADER = ["household_id", "country", "hid", "size", "weight", "draw_order", "split_draft", "pilot"]


def households_rows(hh):
    return [[h[k] for k in HH_HEADER] for h in hh]


def pick_pilot_households(seed, hh_es):
    """10 of the 60 Spanish households, proportional to size; returned in draw order."""
    counts = collections.Counter(h["size"] for h in hh_es)
    take = alloc(10, counts)
    rng = rng_for(seed, "pilot_hh")
    for s in sorted(take):
        for h in rng.sample([x for x in hh_es if x["size"] == s], take[s]):
            h["pilot"] = 1
    return [h["household_id"] for h in hh_es if h["pilot"] == 1]


# ------------------------------------------------------------------ climates
CLIMATE_HEADER = ["climate_id", "country", "city", "year", "source", "path", "md5",
                  "rmse_theta_month_c", "ghi_year_kwh_m2", "status"]


def build_climates():
    sc = json.load(io.open(WEATHER_JSON, encoding="utf-8"))
    rows = []
    for c, city, year, key, path in CLIMATES:
        cid = "%s_%s_%d" % (c, city.lower(), year)
        rmse = ghi = sm = ""
        source = "ERA5 5J" if key else "ERA5 OpenUBEM"
        if key:
            path = os.path.join(DATA, "weather", "epw", "%s_%d.epw" % (key, year))
            if key in sc:
                rmse = "%.3f" % sc[key]["rmse_theta_month"]
                ghi = "%.0f" % sc[key]["ghi_year_kwh"]
        else:
            rmse = "%.3f" % OPENUBEM_SCORE[city][0]
            ghi = "%d" % OPENUBEM_SCORE[city][1]
        scored = (key is None) or (key in sc)
        if key in ("uk_manchester", "it_milan"):
            status = "pending"              # still downloading; md5 stays blank
        elif os.path.exists(path) and scored:
            sm, status = md5(path), "ok"
            if key and sm != sc[key]["md5"]:
                raise ValueError("md5 of %s differs from the score json" % path)
        elif os.path.exists(path):
            status = "on_disk_not_scored"   # file exists, no score/md5 in the json yet
        else:
            status = "pending"
        rows.append([cid, c, city, year, source, path, sm, rmse, ghi, status])
    return rows


# ------------------------------------------------------------------ pilot
def build_pilot(seed, pilot_b, pilot_h):
    """50 rows = 40 single runs + 2 further inputs run 5 times each (10 rows).
    The 5 x 10 grid has 50 (building, household) inputs.  Each building skips 2 households (the
    pattern (2b, 2b+1)), which leaves 40 pairs, each building with 8 households and each household
    on 4 buildings.  The 2 repeated inputs are taken from the 10 skipped pairs, on different buildings."""
    nb, nh = len(pilot_b), len(pilot_h)
    if nb != 5 or nh != 10:
        raise ValueError("pilot needs 5 buildings and 10 households")
    skipped = [(b, h) for b in range(nb) for h in (2 * b, 2 * b + 1)]
    singles = [(b, h) for b in range(nb) for h in range(nh) if (b, h) not in skipped]
    rng = rng_for(seed, "pilot_rep")
    rep_b = rng.sample(range(nb), 2)
    reps = [rng.choice([p for p in skipped if p[0] == b]) for b in rep_b]
    rows, n = [], 0
    for (b, h) in singles:
        n += 1
        rows.append(["P%03d" % n, pilot_b[b], pilot_h[h], "es_madrid_2010", 1])
    for (b, h) in reps:
        for r in range(1, 6):
            n += 1
            rows.append(["P%03d" % n, pilot_b[b], pilot_h[h], "es_madrid_2010", r])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--out", default=OUT_DEFAULT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if md5(CORPUS_ES_IT) != CORPUS_ES_IT_MD5:
        sys.exit("GUARD: corpus is not the Spain+Italy copy (md5 mismatch); refused")

    manifest = load_manifest()
    bld = build_buildings(a.seed, manifest)
    pilot_b = pick_pilot_buildings(a.seed, bld)

    hh = []
    for c in ("es", "it"):
        w = read_household_weights(EPISODES[c], strict_constant=(c == "it"))   # 5J change (households v2)
        hh += draw_households(a.seed, c, read_household_sizes(CORPUS_ES_IT, c), w)
        print("%s: hids without a positive weight (dropped from the draw): %d" % (c, NO_WEIGHT[c]))
    pilot_h = pick_pilot_households(a.seed, [h for h in hh if h["country"] == "es"])

    bcols = ["building_id", "country", "class", "archetype_code", "period", "infiltration_ach",
             "north_axis_deg", "pilot"]
    write_csv(os.path.join(a.out, "buildings.csv"), bcols, [[b[k] for k in bcols] for b in bld])
    write_csv(os.path.join(a.out, "households.csv"), HH_HEADER, households_rows(hh))
    write_csv(os.path.join(a.out, "climates.csv"), CLIMATE_HEADER, build_climates())
    pil = build_pilot(a.seed, pilot_b, pilot_h)
    write_csv(os.path.join(a.out, "pilot_runs.csv"),
              ["run_id", "building_id", "household_id", "climate", "replicate"], pil)

    lines = []
    for n in ("buildings.csv", "households.csv", "climates.csv", "pilot_runs.csv"):
        lines.append("%s  %s" % (md5(os.path.join(a.out, n)), n))
    lines.append("%s  %s" % (md5(CORPUS_ES_IT), "4J_step3_corpus_es_it.jsonl (copy)"))
    lines.append("%s  %s" % (md5(MANIFEST), "archetype_idf_manifest.csv"))
    lines.append("%s  %s" % (md5(os.path.abspath(__file__)), "5thJ_design_tables.py"))
    with io.open(os.path.join(a.out, "design_md5.txt"), "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines) + "\n")
    print("seed %d: buildings %d, households %d, climates %d, pilot rows %d"
          % (a.seed, len(bld), len(hh), len(CLIMATES), len(pil)))


if __name__ == "__main__":
    main()
