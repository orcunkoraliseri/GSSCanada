# -*- coding: utf-8 -*-
"""5J Step 9d: Model A households from own-country, own-split real diary days (Spain + Italy only).

Task: Step9_docs/impl/2026-10-01_wp9d_households_TASK.md.  State: Step9_docs/impl/2026-10-01_wp9d_households.md.
Runs on Speed only (sbatch).  UK licence: nothing UK is named, opened or passed here; the countries are es and it.

Reused, never copy-edited (file:line in the state file):
  tools/5thJ_design_tables.py : read_household_sizes, read_household_weights, rng_for, alloc (weighted key as draw_households)
  tools/5thJ_step9_trigger_act2.py (the 5J copy of 4J step 9 trigger, act2 rule prefix2_major): Mapping, build_act2_map,
      sample_ownership, count_eligible, count_eligible_dhw, calibrate_all, calibrate_to_published, simulate_dwelling,
      rotate_to_midnight, write_series_csv, check_corpus_guard, _import_step7
  4J tools/4thJ_step7_schedules.py (through _import_step7): year_day_types, draw, assemble_person_year, household_year,
      write_schedule_csv, _stratum_key, dec.decode_record, dec.decode_prefix, indoor.presence_minutes, load_bit_positions

Sub-commands: all (the whole task: split, pools, calibration, test).
"""
import argparse
import collections
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
import random
import re
import sys
import time

sys.dont_write_bytecode = True

R = "/speed-scratch/o_iseri/5J/households/repo"
OUT = "/speed-scratch/o_iseri/5J/modelA/households"
CORPUS = R + "/4J_step3_corpus_es_it.jsonl"
CORPUS_MD5 = "1a5163445291b54114832e192b0d9a05"
ROOT4 = R + "/4J_docs_occ"
TRIG = R + "/5J_docs_occ/tools/5thJ_step9_trigger_act2.py"
PARQ = {"es": "/speed-scratch/o_iseri/4J/outputs_step1/episodes_spain.parquet",
        "it": "/speed-scratch/o_iseri/4J/outputs_step1/episodes_italy.parquet"}
COUNTRIES = ("es", "it")
YEAR = {"es": 2010, "it": 2014}                 # Madrid, Bologna weather years (9B)
DISTRICT = {"ES-MAD-BERRUGUETE": "es", "IT-BOL-GALVANI2": "it"}
SPLITS = ("dev", "val", "test")
SEED_SPLIT, SEED_CALIB, SEED_CALSIM, SEED_FLAT = 9101, 9103, 9104, 9105
N_CALIB = 100
N = 8760
FAILS = []
NOTES = []


def gate(name, ok, msg=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", msg), flush=True)
    if not ok:
        FAILS.append(name)


def stamp(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


# ------------------------------------------------------------------------------------------------ guards
_BAD = re.compile(r"(^|[^a-z])(uk|gb|ldn)([^a-z]|$)|london|stdunstans", re.I)


def assert_not_uk(*things):
    """Refuses any path/argument that names the UK. Looks at the strings only; opens nothing."""
    for t in things:
        if _BAD.search(str(t)):
            sys.exit("STOP: argument or path names the UK: %r" % (t,))


def md5_file(path):
    h = hashlib.md5()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(name, path, extra_path=None):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    if extra_path:
        sys.path.insert(0, extra_path)
    spec.loader.exec_module(mod)
    return mod


def write_csv(path, header, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def read_csv(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------------------------------------------ modules
HERE = os.path.dirname(os.path.abspath(__file__))
dt = load_module("dt5j", os.path.join(HERE, "5thJ_design_tables.py"))
trig = None
s7 = None


def setup_modules():
    global trig, s7
    trig = load_module("trig5j", TRIG)
    s7 = trig._import_step7(os.path.join(ROOT4, "tools"))


# ------------------------------------------------------------------------------------------------ corpus
def read_corpus(path):
    """rows per country: list of (pid, hid, text).  Stops if any row is not es / it (the copy has none)."""
    trig.check_corpus_guard(path)
    assert_not_uk(path)
    rows = dict((c, []) for c in COUNTRIES)
    other = collections.Counter()
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            c = r["country"]
            if c not in rows:
                other[c] += 1
                continue
            rows[c].append((r["pid"], r["hid"], r["text"]))
    if other:
        sys.exit("STOP: the corpus copy holds rows of another country (%s); nothing more is read" % dict(other))
    return rows


def split_hids(country, sizes, weights):
    """Stratified 70/15/15 by size (1,2,3,4,5+), seed 9101. Returns (hid->split, dropped_no_weight)."""
    by = collections.defaultdict(list)
    dropped = 0
    for hid, s in sizes.items():
        w = weights.get(hid)
        if w is None or not w > 0:
            dropped += 1
            continue
        by[min(s, 5)].append(hid)
    out = {}
    per = {}
    for b in sorted(by):
        hs = sorted(by[b])
        rng = dt.rng_for(SEED_SPLIT, "split", country, b)
        rng.shuffle(hs)
        n = len(hs)
        nd, nv = int(round(0.70 * n)), int(round(0.15 * n))
        for h in hs[:nd]:
            out[h] = "dev"
        for h in hs[nd:nd + nv]:
            out[h] = "val"
        for h in hs[nd + nv:]:
            out[h] = "test"
        per[b] = (n, nd, nv, n - nd - nv)
    return out, dropped, per


class Ctx(object):
    pass


def build_ctx(country, rows, bitpos, outdoor):
    ctx = Ctx()
    ctx.country = country
    ctx.sizes = dt.read_household_sizes(CORPUS, country)                 # reused function
    ctx.weights = dt.read_household_weights(PARQ[country], "weight_ind")  # reused function
    # household members in file order, first row per pid (as load_households_by_hids)
    members = collections.OrderedDict()
    for pid, hid, text in rows:
        pfx = s7.dec.decode_prefix(text.split("|", 1)[0])
        members.setdefault(hid, collections.OrderedDict()).setdefault(pid, pfx)
    ctx.members = dict((h, list(v.items())) for h, v in members.items())
    mine = dict((h, len(v)) for h, v in ctx.members.items())
    gate("%s_sizes_equal_distinct_pid_count" % country, mine == dict(ctx.sizes), "households=%d" % len(mine))
    ctx.split_of_hid, dropped, per = split_hids(country, ctx.sizes, ctx.weights)
    ctx.split_per_size = per
    ctx.dropped = dropped
    ctx.hids_by_split = dict((s, sorted(h for h, v in ctx.split_of_hid.items() if v == s)) for s in SPLITS)
    ctx.split_of_pid = {}
    ctx.pools = dict((s, dict((d, collections.defaultdict(list)) for d in range(len(s7.STRATUM_FIELDS) + 1))) for s in SPLITS)
    n_bad = 0
    no_split = 0
    for pid, hid, text in rows:
        sp = ctx.split_of_hid.get(hid)
        if sp is None:
            no_split += 1
            continue
        try:
            decoded = s7.dec.decode_record(text, bitpos)
            flags = s7.indoor.presence_minutes(decoded, outdoor)
        except Exception:
            n_bad += 1
            continue
        day = {"flags": flags,
               "acts": [(e["duration_min"], e["act"]) for e in decoded["episodes"]],
               "acts2": [(e["duration_min"], e["act2"]) for e in decoded["episodes"]],
               "prefix": decoded["prefix"], "pid": pid, "hid": hid}
        ctx.split_of_pid[pid] = sp
        for d in ctx.pools[sp]:
            ctx.pools[sp][d][s7._stratum_key(decoded["prefix"], d)].append(day)
    ctx.n_undecodable, ctx.n_no_split = n_bad, no_split
    ctx.acl_to_profile = None
    return ctx


def pool_stats(ctx):
    for sp in SPLITS:
        pools = ctx.pools[sp]
        full = pools[len(s7.STRATUM_FIELDS)]
        by_dt = collections.Counter()
        resp = set()
        for key, days in pools[0].items():
            by_dt[key[-1]] += len(days)
            for d in days:
                resp.add(d["pid"])
        ge5 = sum(1 for v in full.values() if len(v) >= 5)
        one = sum(1 for v in full.values() if len(v) == 1)
        print("POOL %s %s households=%d respondents=%d days_by_daytype=%s full_buckets=%d with>=5_days=%d with_1_day=%d"
              % (ctx.country, sp, len(ctx.hids_by_split[sp]), len(resp), dict(sorted(by_dt.items())), len(full), ge5, one),
              flush=True)


def write_splits(ctx):
    d = OUT + "/splits"
    os.makedirs(d, exist_ok=True)
    c = ctx.country
    md5s = {}
    for sp in SPLITS:
        p = "%s/hids_%s_%s.csv" % (d, c, sp)
        write_csv(p, ["hid", "size", "weight"], [[h, ctx.sizes[h], "%.6f" % ctx.weights[h]] for h in ctx.hids_by_split[sp]])
        md5s[sp] = md5_file(p)
        print("SPLIT_LIST %s %s n=%d md5=%s %s" % (c, sp, len(ctx.hids_by_split[sp]), md5s[sp], p), flush=True)
    p = "%s/respondents_%s.csv" % (d, c)
    write_csv(p, ["country", "pid", "hid", "split"],
              [[c, pid, ctx.members_pid_hid[pid], sp] for pid, sp in sorted(ctx.split_of_pid.items())])
    md5s["respondents"] = md5_file(p)
    print("SPLIT_RESPONDENTS %s n=%d md5=%s %s" % (c, len(ctx.split_of_pid), md5s["respondents"], p), flush=True)
    ctx.split_md5 = md5s
    for b, (n, nd, nv, nt) in sorted(ctx.split_per_size.items()):
        print("SPLIT_COUNTS %s size=%s households=%d dev=%d val=%d test=%d" % (c, "5+" if b == 5 else b, n, nd, nv, nt))


# ------------------------------------------------------------------------------------------------ calibration
def activate(ctx):
    """Point the (module-global) act2 switch of the trigger at this country's own dev pool minutes."""
    trig.ACT2["on"] = True
    trig.ACT2["match"] = "prefix2_major"
    trig.ACT2["n_used"] = 0
    trig.ACT2["pool_minutes"] = ctx.pool_minutes
    trig.ACT2["map"], trig.ACT2["ambiguous"] = trig.build_act2_map(ctx.acl_to_profile, "prefix2_major", ctx.pool_minutes)


def calibrate(ctx):
    map_path = ROOT4 + "/Step9_docs/outputs_step9/activity_appliance_map.csv"
    ctx.mapping = trig.Mapping(map_path)
    ctx.acl_to_profile = dict(ctx.mapping.acl_to_profile)
    pm = collections.Counter()                           # primary-episode minutes over the DEV pool only
    for bucket in ctx.pools["dev"][0].values():
        for day in bucket:
            for dur, a in day["acts"]:
                pm[a] += dur
    ctx.pool_minutes = dict(pm)
    activate(ctx)
    cache = "%s/hazards_%s.json" % (OUT, ctx.country)
    # calibration stock: 100 dev households by survey weight (key log(1-u)/w), dev pool only
    rng = dt.rng_for(SEED_CALIB, "calib", ctx.country)
    keyed = sorted(((math.log(1.0 - rng.random()) / ctx.weights[h], h) for h in ctx.hids_by_split["dev"]), reverse=True)
    chosen = [h for _, h in keyed[:N_CALIB]]
    chosen_md5 = hashlib.md5(",".join(chosen).encode()).hexdigest()
    key = {"split_md5": ctx.split_md5, "calib_hids_md5": chosen_md5, "map_md5": ctx.mapping.md5}
    if os.path.exists(cache):
        j = json.load(io.open(cache, encoding="utf-8"))
        if j.get("key") == key:
            ctx.hazards, ctx.dhw_haz = j["hazards"], j["dhw_haz"]
            print("CALIB %s reused %s" % (ctx.country, cache), flush=True)
            return
    cal = s7.year_day_types(YEAR[ctx.country])
    r2 = random.Random(SEED_CALSIM)
    tally = collections.Counter()
    dw = []
    for hid in chosen:
        md = [s7.assemble_person_year(p, cal, "independent", r2, ctx.pools["dev"], tally, 0.0) for _, p in ctx.members[hid]]
        dw.append({"hid": hid, "members": md, "presence": s7.household_year(md, 60), "n_members": len(md)})
    n_days = len(cal)
    mean_elig = trig.count_eligible(dw, ctx.acl_to_profile, n_days)
    mean_elig.update(trig.count_eligible_dhw(dw, ctx.mapping, ctx.acl_to_profile, n_days))
    hazards, dhw_haz, _diag = trig.calibrate_all(ctx.mapping, mean_elig, 200.0 / 200.0)
    owned = trig.sample_ownership(ctx.mapping, dw, random.Random("A9d-calib-own|%d" % SEED_CALSIM))
    hazards, trace = trig.calibrate_to_published(dw, ctx.mapping, owned, hazards, ctx.acl_to_profile, n_days, SEED_CALSIM,
                                                 max_passes=6)
    ctx.hazards, ctx.dhw_haz = hazards, dhw_haz
    worst = trace[-1]["worst_abs_dev"] if trace else None
    print("CALIB %s households=%d passes=%d worst_abs_dev_last=%s saturated=%s backoff_depths=%s"
          % (ctx.country, len(dw), len(trace), worst, trace[-1]["saturated"] if trace else None, dict(tally)), flush=True)
    json.dump({"key": key, "hazards": hazards, "dhw_haz": dhw_haz, "n_passes": len(trace), "worst_abs_dev_last": worst,
               "calib_hids": chosen}, io.open(cache, "w", encoding="utf-8"), indent=1)


# ------------------------------------------------------------------------------------------------ builder
def draw_year(pools, prefix, cal, rng):
    """The `independent` branch of s7.assemble_person_year, with the (respondent, depth) of every draw kept."""
    days, recs = [], []
    for i, dtype in enumerate(cal):
        p = dict(prefix)
        p["strat_day_type"] = dtype
        day, depth = s7.draw(pools, p, rng, collections.Counter())
        days.append(day)
        recs.append((i, day["pid"], depth))
    return days, recs


def household_year(ctx, split, hid, run_seed, pools=None, draw_only=False):
    """One household-year.  Returns dict(records, [presence, appliance_frac, peak_w, n_members])."""
    cal = s7.year_day_types(YEAR[ctx.country])
    pools = pools if pools is not None else ctx.pools[split]
    member_days, recs = [], []
    for mi, (_pid, pfx) in enumerate(ctx.members[hid]):
        rng = random.Random("A9d|%d|%s|%s|m%d" % (run_seed, ctx.country, hid, mi))
        days, rc = draw_year(pools, pfx, cal, rng)
        member_days.append(days)
        recs.extend((hid, mi, di, rpid, depth) for di, rpid, depth in rc)
    if draw_only:
        return {"records": recs}
    activate(ctx)
    series = s7.household_year(member_days, 60)
    presence = trig.rotate_to_midnight(series, 60)
    d = {"hid": hid, "members": member_days, "presence": series, "n_members": len(member_days)}
    owned = trig.sample_ownership(ctx.mapping, [d], random.Random("A9d-own|%d|%s|%s" % (run_seed, ctx.country, hid)))
    rec = trig.simulate_dwelling(d, owned[hid], ctx.mapping, ctx.hazards, ctx.dhw_haz, ctx.acl_to_profile, len(cal), 60,
                                 run_seed, rng=random.Random("A9d-sim|%d|%s|%s" % (run_seed, ctx.country, hid)))
    elec = rec["elec_ts"]
    peak = max(elec) if elec else 0.0
    frac = [v / peak if peak else 0.0 for v in elec]
    return {"records": recs, "presence": presence, "appliance_frac": frac, "peak_w": float("%.4f" % peak),
            "n_members": len(member_days), "owned": len(owned[hid])}


def write_household(outdir, country, hid, hy):
    os.makedirs(outdir, exist_ok=True)
    name = "HH_%s_%s" % (country, hid)
    pp = "%s/presence_%s.csv" % (outdir, name)
    ap = "%s/elec_%s.csv" % (outdir, name)
    s7.write_schedule_csv(pp, hy["presence"], name + "_Presence")
    trig.write_series_csv(ap, name + "_ApplianceFraction", hy["appliance_frac"])
    return pp, ap


def write_draws(path, records):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["hid", "member", "day", "pid", "depth"])
        w.writerows(records)


def assign_flats(ctx, split, run_id, zones, exclude=None):
    """Distinct households of the split into the flats, by survey weight without replacement (key log(1-u)/w, the pilot's
    key).  exclude: zone -> set of hids that flat may not get again (same flat, same pool, earlier run)."""
    rng = dt.rng_for(SEED_FLAT, "flats", run_id)
    keyed = [h for _, h in sorted(((math.log(1.0 - rng.random()) / ctx.weights[h], h) for h in ctx.hids_by_split[split]),
                                  reverse=True)]
    used, out = set(), []
    for z in zones:
        ban = (exclude or {}).get(z, ())
        for h in keyed:
            if h not in used and h not in ban:
                used.add(h)
                out.append((z, h))
                break
        else:
            raise RuntimeError("pool of %s too small for %d flats" % (split, len(zones)))
    return out


# ------------------------------------------------------------------------------------------------ checks (read back from disk)
def check_series(pp, ap, members):
    bad = []
    def rd(p):
        with io.open(p, encoding="utf-8") as fh:
            ls = [l.strip() for l in fh.read().splitlines() if l.strip()]
        return [float(x) for x in ls[1:]]
    p, a = rd(pp), rd(ap)
    if len(p) != N or len(a) != N:
        bad.append("length presence=%d appliance=%d" % (len(p), len(a)))
    if not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in p):
        bad.append("presence fraction outside [0,1]")
    if not all(math.isfinite(v) and v * members >= 0.0 and v * members <= members + 1e-9 for v in p):
        bad.append("presence people outside [0, members]")
    if not all(math.isfinite(v) and v >= 0.0 for v in a):
        bad.append("appliance negative or not finite")
    return bad


def purity(draw_path, run_split, split_of_pid):
    """records whose respondent is not of the run's split (read back from the written draw file)."""
    viol, n = [], 0
    with io.open(draw_path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            n += 1
            if split_of_pid.get(r["pid"]) != run_split:
                viol.append((r["hid"], r["member"], r["day"], r["pid"]))
    return viol, n


def read_resp_table(country):
    return dict((r["pid"], r["split"]) for r in read_csv("%s/splits/respondents_%s.csv" % (OUT, country)))


# ------------------------------------------------------------------------------------------------ test
def pick_buildings(zone_map_path):
    by = collections.OrderedDict()
    with io.open(zone_map_path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["district"] not in DISTRICT:
                sys.exit("STOP: zone map holds a district that is not Madrid or Bologna: %r" % r["district"])
            by.setdefault((r["district"], r["stem"]), []).append(r["zone"])
    pick = {}
    for (dist, stem), zones in by.items():
        n = len(zones)
        if 5 <= n <= 25:
            k = (abs(n - 15), stem)
            c = DISTRICT[dist]
            if c not in pick or k < pick[c][0]:
                pick[c] = (k, dist, stem, zones)
    return dict((c, {"district": v[1], "stem": v[2], "zones": v[3]}) for c, v in pick.items())


def run_seed_of(run_id):
    return int(hashlib.md5(run_id.encode()).hexdigest()[:8], 16) % 2147483647


def plant_pools(pools_dev, day):
    """Shallow copy of the dev pools with one extra day (touched buckets copied)."""
    out = {}
    for d, buckets in pools_dev.items():
        nb = dict(buckets)
        k = s7._stratum_key(day["prefix"], d)
        nb[k] = list(buckets.get(k, [])) + [day]
        out[d] = nb
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone-map", default=OUT + "/inputs/zone_map_win.csv")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    assert args.out == OUT
    assert_not_uk(args.zone_map, args.out)
    os.makedirs(OUT + "/test", exist_ok=True)
    stamp("start")
    setup_modules()
    gate("corpus_md5", md5_file(CORPUS) == CORPUS_MD5, md5_file(CORPUS))
    rows = read_corpus(CORPUS)
    print("CORPUS rows es=%d it=%d" % (len(rows["es"]), len(rows["it"])), flush=True)
    step2 = ROOT4 + "/Step2_docs/outputs_step2"
    bitpos = s7.load_bit_positions(step2 + "/crosswalk_copresence.csv")
    outdoor, _md5 = s7.indoor.load_outdoor_at_home(step2)
    ctxs = {}
    for c in COUNTRIES:
        ctx = build_ctx(c, rows[c], bitpos, outdoor)
        ctx.members_pid_hid = dict((pid, hid) for pid, hid, _t in rows[c])
        ctxs[c] = ctx
        print("COUNTRY %s households=%d no_weight_dropped=%d respondents_in_pools=%d undecodable=%d outside_split=%d"
              % (c, len(ctx.sizes), ctx.dropped, len(ctx.split_of_pid), ctx.n_undecodable, ctx.n_no_split), flush=True)
        write_splits(ctx)
        pool_stats(ctx)
        # day belongs to exactly one split; a hid belongs to exactly one split
        tot = sum(len(ctx.hids_by_split[s]) for s in SPLITS)
        gate("%s_each_hid_in_one_split" % c, tot == len(ctx.split_of_hid) == len(set().union(*[set(ctx.hids_by_split[s]) for s in SPLITS])),
             "total=%d" % tot)
        resp_sets = [set(d["pid"] for b in ctx.pools[s][0].values() for d in b) for s in SPLITS]
        gate("%s_each_respondent_in_one_pool" % c,
             not (resp_sets[0] & resp_sets[1]) and not (resp_sets[0] & resp_sets[2]) and not (resp_sets[1] & resp_sets[2]),
             "respondents=%d" % sum(len(x) for x in resp_sets))
        stamp("country %s pools built" % c)
    for c in COUNTRIES:
        calibrate(ctxs[c])
        stamp("country %s calibrated" % c)
    pick = pick_buildings(args.zone_map)
    gate("two_buildings_found", sorted(pick) == ["es", "it"], "es=%s it=%s" % (
        (pick.get("es") or {}).get("stem"), (pick.get("it") or {}).get("stem")))
    # selfcheck of the series checker (seen failing)
    good = [0.5] * N
    tmp = OUT + "/test/_selfcheck"
    os.makedirs(tmp, exist_ok=True)
    def wr(p, vals, hdr="x"):
        with io.open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(hdr + "\n" + "".join("%.6f\n" % v for v in vals))
    wr(tmp + "/p_ok.csv", good); wr(tmp + "/a_ok.csv", good)
    gate("selfcheck_series_ok_accepted", not check_series(tmp + "/p_ok.csv", tmp + "/a_ok.csv", 2))
    for lab, pv, av in (("presence_1.2", [1.2] + good[1:], good), ("rows_8759", good[:-1], good), ("appliance_negative", good, [-0.1] + good[1:])):
        wr(tmp + "/p_b.csv", pv); wr(tmp + "/a_b.csv", av)
        gate("selfcheck_series_flags_%s (seen failing)" % lab, bool(check_series(tmp + "/p_b.csv", tmp + "/a_b.csv", 2)))
    # ------------------------------------------------------------------ the six runs
    resp_tab = dict((c, read_resp_table(c)) for c in COUNTRIES)
    runs = []
    timing, disk = [], []
    depth_tab = dict(((c, s), collections.Counter()) for c in COUNTRIES for s in SPLITS)
    for c in COUNTRIES:
        ctx = ctxs[c]
        b = pick[c]
        for sp in SPLITS:
            run_id = "%s_%s_%s_r1" % (c, b["stem"], sp)
            seed = run_seed_of(run_id)
            flats = assign_flats(ctx, sp, run_id, b["zones"])
            gate("%s_flats_distinct_households_of_split" % run_id,
                 len(set(h for _, h in flats)) == len(flats) and all(ctx.split_of_hid[h] == sp for _, h in flats),
                 "flats=%d" % len(flats))
            sdir = "%s/test/series/%s" % (OUT, run_id)
            recs, place, tot_t = [], [], 0.0
            first3 = []
            for z, h in flats:
                t0 = time.time()
                hy = household_year(ctx, sp, h, seed)
                pp, apth = write_household(sdir, c, h, hy)
                dtm = time.time() - t0
                tot_t += dtm
                timing.append(dtm)
                disk.append(os.path.getsize(pp) + os.path.getsize(apth))
                recs.extend(hy["records"])
                place.append([z, h, pp, apth, hy["n_members"], "%.4f" % hy["peak_w"]])
                if len(first3) < 3:
                    first3.append((h, hy, pp, apth))
            write_csv("%s/test/placement_%s.csv" % (OUT, run_id),
                      ["dwelling_zone", "hid", "presence_csv", "appliance_csv", "n_members", "appliance_peak_w"], place)
            dpath = "%s/test/draws_%s.csv" % (OUT, run_id)
            write_draws(dpath, recs)
            for r in recs:
                depth_tab[(c, sp)][r[4]] += 1
            # ---- read-back checks
            viol, nrec = purity(dpath, sp, resp_tab[c])
            gate("%s_purity" % run_id, not viol and nrec > 0, "records=%d violations=%d" % (nrec, len(viol)))
            badser = []
            for z, h, pp, apth, nm, pk in place:
                bs = check_series(pp, apth, int(nm))
                if bs:
                    badser.append((h, bs))
            gate("%s_series_8760_presence_appliance" % run_id, not badser, "households=%d bad=%d %s" % (len(place), len(badser), badser[:2]))
            # ---- determinism: first 3 households again, byte for byte
            ddir = "%s/test/det/%s" % (OUT, run_id)
            same = True
            for h, hy0, pp0, ap0 in first3:
                hy1 = household_year(ctx, sp, h, seed)
                pp1, ap1 = write_household(ddir, c, h, hy1)
                same = same and md5_file(pp0) == md5_file(pp1) and md5_file(ap0) == md5_file(ap1) and hy0["records"] == hy1["records"]
            gate("%s_determinism_same_seed_byte_identical" % run_id, same, "households=%d" % len(first3))
            runs.append({"run_id": run_id, "country": c, "split": sp, "seed": seed, "flats": flats, "stem": b["stem"],
                         "seconds": tot_t})
            print("RUN %s flats=%d seed=%d seconds=%.1f draws=%d" % (run_id, len(flats), seed, tot_t, len(recs)), flush=True)
            stamp("run %s done" % run_id)
    # a different seed must differ (the determinism comparison can fail)
    r0 = runs[0]
    c0 = r0["country"]
    h0 = r0["flats"][0][1]
    ya = household_year(ctxs[c0], r0["split"], h0, r0["seed"])
    yb = household_year(ctxs[c0], r0["split"], h0, r0["seed"] + 1)
    gate("determinism_check_can_fail_different_seed_differs (seen failing)", ya["presence"] != yb["presence"] or ya["appliance_frac"] != yb["appliance_frac"])
    # ---- equivalence of my draw loop with s7.assemble_person_year (same seed -> same days)
    ctx = ctxs[c0]
    cal = s7.year_day_types(YEAR[c0])
    pools0 = ctx.pools[r0["split"]]
    ok = True
    for mi, (_pid, pfx) in enumerate(ctx.members[h0]):
        seedstr = "A9d|%d|%s|%s|m%d" % (r0["seed"], c0, h0, mi)
        mine, _ = draw_year(pools0, pfx, cal, random.Random(seedstr))
        ref = s7.assemble_person_year(pfx, cal, "independent", random.Random(seedstr), pools0, collections.Counter(), 0.0)
        ok = ok and all(a is b for a, b in zip(mine, ref)) and len(mine) == len(ref)
    gate("draw_loop_equals_s7_assemble_person_year", ok, "household=%s" % h0)
    # ---- back-off depth table
    for c in COUNTRIES:
        for sp in SPLITS:
            t = depth_tab[(c, sp)]
            tot = float(sum(t.values()))
            print("DEPTH %s %s total=%d %s" % (c, sp, tot, " ".join("d%d=%d(%.1f%%)" % (k, t[k], 100.0 * t[k] / tot) for k in sorted(t, reverse=True))), flush=True)
    # ---- planted fault P1 (Madrid): one test respondent's day goes into the dev pool copy
    c = "es"
    ctx = ctxs[c]
    es_runs = [r for r in runs if r["country"] == c]
    dev_run = [r for r in es_runs if r["split"] == "dev"][0]
    cal = s7.year_day_types(YEAR[c])
    cands = []
    for z, h in dev_run["flats"]:
        for mi, (_pid, pfx) in enumerate(ctx.members[h]):
            for dtype in s7.DAY_TYPES:
                p = dict(pfx)
                p["strat_day_type"] = dtype
                k4 = s7._stratum_key(p, len(s7.STRATUM_FIELDS))
                tb = ctx.pools["test"][len(s7.STRATUM_FIELDS)].get(k4)
                if tb:
                    cands.append((len(ctx.pools["dev"][len(s7.STRATUM_FIELDS)].get(k4, [])), h, mi, dtype, tb[0]))
    cands.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    print("P1 candidates=%d (smallest dev buckets first)" % len(cands), flush=True)
    p1_done = False
    for ci, (nb, h, mi, dtype, day) in enumerate(cands[:5]):
        planted = day["pid"]
        pdev = plant_pools(ctx.pools["dev"], day)
        os.makedirs(OUT + "/test/p1", exist_ok=True)
        verdict, expect_fail, counts = {}, set(), {}
        for r in es_runs:
            pools = pdev if r["split"] == "dev" else ctx.pools[r["split"]]
            recs = []
            for z, hh in r["flats"]:
                recs.extend(household_year(ctx, r["split"], hh, r["seed"], pools=pools, draw_only=True)["records"])
            dpath = "%s/test/p1/draws_%s_try%d.csv" % (OUT, r["run_id"], ci)
            write_draws(dpath, recs)
            viol, nrec = purity(dpath, r["split"], resp_tab[c])
            counts[r["run_id"]] = sum(1 for x in recs if str(x[3]) == str(planted))     # independent count
            verdict[r["run_id"]] = (len(viol), nrec)
        print("P1 try %d planted_respondent=%s (test split; dev bucket size before=%d) draws_by_run=%s violations_by_run=%s"
              % (ci, planted, nb, counts, dict((k, v[0]) for k, v in verdict.items())), flush=True)
        drew = sum(counts.values()) > 0
        if drew:
            fail_set = set(k for k, v in verdict.items() if v[0] > 0)
            drew_set = set(k for k, v in counts.items() if v > 0)
            gate("P1_purity_fails_on_exactly_the_runs_that_drew_it", fail_set == drew_set and all(verdict[k][0] == counts[k] for k in drew_set),
                 "fail_runs=%s drew_runs=%s" % (sorted(fail_set), sorted(drew_set)))
            p1_done = True
            break
    if not p1_done:
        print("P1 NOT_EVALUABLE: none of %d plants was drawn by any Madrid run" % min(5, len(cands)), flush=True)
        FAILS.append("P1_not_evaluable")
    # ---- timing and disk
    n = float(len(timing))
    print("TIMING household_years=%d mean_seconds=%.2f max_seconds=%.2f ; disk_per_household_year_bytes mean=%.0f (two series files; "
          "draw records excluded)" % (n, sum(timing) / n, max(timing), sum(disk) / float(len(disk))), flush=True)
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS), flush=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
