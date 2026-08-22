# -*- coding: utf-8 -*-
"""`G6.7` part 1 — build the FICTIONAL-COUNTRY prefix sets at K perturbation levels.

  usage: python 4thJ_step6_g67_prefixes.py --fold es --step5 DIR --corpus FILE
                                           --step2 DIR --out DIR [--n 600] [--levels 5]

---------------------------------------------------------------------------
WHAT `G6.7` IS FOR, IN ONE SENTENCE
---------------------------------------------------------------------------

*"It read about the country on the web."* If the model reproduces Spain because
`es` is a token it has seen a billion times in pre-training, it is not
transferring from a conditioning vector and the whole claim is hollow. So it is
asked to generate under a country token **that does not exist**, with the
demographic marginals **moved on purpose**, and its output must follow the
marginals rather than fall back on any national pattern.

---------------------------------------------------------------------------
🔴 THE FICTIONAL TOKEN
---------------------------------------------------------------------------

`x_zz`. `enc_country(allow_synthetic_controls=True)` accepts it and NOTHING else
in the pipeline does -- the keyword is per-call and the production whitelist is
untouched (`D-S9-1` item 5 (a), applied 2026-08-20). 🔴 The token is two
characters no ISO code uses behind an `x_` prefix no corpus value can collide
with, so a synthetic prefix that leaks into a scoring run is a hard error rather
than a silent row.

---------------------------------------------------------------------------
🔴 WHAT IS PERTURBED, AND WHY THAT AXIS -- A DECLARED CHOICE (`D-S6-11` item 1)
---------------------------------------------------------------------------

The **age-band mix**. Level `t` runs 0 -> 1 and interpolates the fold's own
synthetic population between its real age distribution (`t = 0`) and that same
distribution **reversed across the age ordering** (`t = 1`), holding every other
prefix field's within-age composition fixed.

  * Age is the axis with the largest and least ambiguous effect on the level-1
    budget: employment time collapses and `AC0` rises as the mix ages. A
    perturbation the model could follow only by accident is not a test.
  * Reversal rather than a random reweighting: it is deterministic, it is the
    largest move available inside the observed support, and it invents no
    stratum that the donor corpus cannot supply an expectation for.
  * 🔴 Every level uses the SAME strata, only different SHARES. Nothing is
    extrapolated outside the support, so the expectation below is an average of
    observed cell budgets and never a model of its own.

---------------------------------------------------------------------------
🔴 THE EXPECTATION IS BUILT FROM DONOR COUNTRIES ONLY
---------------------------------------------------------------------------

The expected level-1 budget at level `t` is

    E_t[a] = SUM_s  share_t(s) * budget_donor(s)[a]

where `budget_donor(s)` is the weighted mean budget of stratum `s` in the two
countries the fold's model was TRAINED on. Using the held-out country's own
diaries would leak the answer into the yardstick. Strata the donors cannot
supply are dropped from BOTH the shares and the expectation, renormalised, and
COUNTED in the manifest -- a silently dropped stratum is a silently changed
marginal.
"""

import argparse
import collections
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import importlib
L1 = importlib.import_module("4thJ_step6_level1")
import decoder as dec
from encoder import enc_country, load_bit_positions

FICTIONAL = "x_zz"
AGE_ORDER = ["11-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]
MIN_DONOR_RECORDS = 5      # a stratum budget over fewer than this is not a budget


def stratum(row):
    return (row["strat_age_band"], row["strat_sex"], row["strat_hh_type"],
            row["strat_econ_status"], row["strat_day_type"])


# 🟢 `D-S6-11` item 2 RULED (a), 2026-08-22: the FIXED five-rung ladder, with
# the share of each rung REPORTED per lambda level. 0 % of prefixes dropped, so
# no selection bias correlated with lambda is introduced.
# 🔴 THE BACKOFF LADDER (`D-S6-11` item 2). The first build priced a prefix only
# on its FULL six-field stratum and dropped the rest -- 24.6 % of the Spanish
# population, which is not a dropped row, it is a silently changed marginal. The
# expectation now backs off one field at a time, in a fixed order, and every level
# records how many of its draws were priced at which rung.
BACKOFF = [
    ("full", (0, 1, 2, 3, 4)),                 # age, sex, hh_type, econ, day_type
    ("no_econ", (0, 1, 2, 4)),
    ("no_econ_no_hh", (0, 1, 4)),
    ("age_day", (0, 4)),
    ("age", (0,)),
]


def donor_budgets(corpus, fold, bitpos, weights):
    """Per-stratum level-1 budget over the DONOR countries, weighted, at every
    rung of the backoff ladder."""
    donors = [c for c in ("es", "uk", "it") if c != fold]
    rows = collections.defaultdict(lambda: ([], []))
    for line in open(corpus, encoding="utf-8"):
        r = json.loads(line)
        if r["country"] not in donors:
            continue
        w = weights.get((r["country"], r["pid"], r["diary_day"]))
        if w is None or w != w:
            continue
        d = dec.decode_record(r["text"], bitpos)
        p = d["prefix"]
        k = (p["strat_age_band"], p["strat_sex"], p["strat_hh_type"],
             p["strat_econ_status"], p["strat_day_type"])
        rows[k][0].append(d)
        rows[k][1].append(w)
    ladder = []
    for name, fields in BACKOFF:
        agg = collections.defaultdict(lambda: ([], []))
        for k, (recs, ws) in rows.items():
            kk = tuple(k[i] for i in fields)
            agg[kk][0].extend(recs)
            agg[kk][1].extend(ws)
        rung = dict((kk, L1.budget(rc, ws)) for kk, (rc, ws) in agg.items()
                    if len(rc) >= MIN_DONOR_RECORDS)
        ladder.append((name, fields, rung))
    return ladder


def price(ladder, key):
    """Return (budget, rung_name). Raises if not even the coarsest rung has it."""
    for name, fields, rung in ladder:
        kk = tuple(key[i] for i in fields)
        if kk in rung:
            return rung[kk], name
    raise KeyError("no rung of the ladder prices %r. The donor corpus does not "
                   "contain this age band at all." % (key,))


def tilt_shares(base, lam):
    """The observed age mix re-tilted: `share(b) ~ base(b) * exp(lam * rank(b))`.

    🔴 `FINDING 90` is why this is not a reversal. The first build interpolated
    between the fold's age mix and that mix REVERSED across the age ordering, on
    the assumption that reversing an age distribution is a large move. Spain's is
    very nearly symmetric, so the reversal moved the expected `AC0` by **0.8
    min/day across the whole range** -- a perturbation with no amplitude, against
    which any slope at all is noise. The tilt is monotone in `lam`, keeps every
    observed band present with non-zero mass, extrapolates outside no support, and
    its amplitude is a parameter rather than an accident of the population.
    """
    present = [b for b in AGE_ORDER if base.get(b, 0.0) > 0.0]
    w = dict((b, base[b] * math.exp(lam * i)) for i, b in enumerate(present))
    tot = sum(w.values())
    return dict((b, v / tot) for b, v in w.items())


def mean_age_rank(share):
    present = [b for b in AGE_ORDER if b in share]
    return sum(share[b] * AGE_ORDER.index(b) for b in present)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=("es", "uk", "it"))
    ap.add_argument("--step5", required=True)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--harmonised", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--levels", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260822)
    ap.add_argument("--lam", type=float, default=0.6,
                    help="age-tilt amplitude; lam is swept -lam..+lam")
    a = ap.parse_args(argv)

    import random
    import math
    import pyarrow.parquet as pq

    rng = random.Random(a.seed)
    bitpos = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))

    df = pq.read_table(a.harmonised, columns=["country", "pid", "diary_day",
                                              "weight_dia_cal"]).to_pandas()
    df["country"] = df["country"].str.lower()
    df = df.drop_duplicates(subset=["country", "pid", "diary_day"])
    W = {(r.country, r.pid, r.diary_day): float(r.weight_dia_cal)
         for r in df.itertuples()}

    print("=" * 78)
    print("G6.7 -- fictional-country prefixes, fold %s, token %r" % (a.fold, FICTIONAL))
    print("=" * 78)
    assert enc_country(FICTIONAL, allow_synthetic_controls=True) == FICTIONAL
    try:
        enc_country(FICTIONAL)
        raise SystemExit("🔴 enc_country accepted %r WITHOUT the keyword. The "
                         "production guard is gone; stop." % FICTIONAL)
    except Exception:
        pass
    print("token guard: enc_country refuses %r without the keyword. OK" % FICTIONAL)

    pool = [json.loads(l) for l in
            open(os.path.join(a.step5, "prefixes_%s.jsonl" % a.fold), encoding="utf-8")
            if l.strip()]
    print("population: %d prefixes" % len(pool))

    ladder = donor_budgets(a.corpus, a.fold, bitpos, W)
    for name, fields, rung in ladder:
        print("donor ladder rung %-14s %5d cells" % (name, len(rung)))

    by_age = collections.defaultdict(list)
    for r in pool:
        by_age[r["strat_age_band"]].append(r)
    base = dict((b, len(v) / float(len(pool))) for b, v in by_age.items())

    lam_max = a.lam
    print("\nage tilt: lam from %+.2f to %+.2f over %d levels (D-S6-11 item 1)"
          % (-lam_max, lam_max, a.levels))

    manifest = {"fold": a.fold, "token": FICTIONAL, "n_per_level": a.n,
                "levels": a.levels, "seed": a.seed, "lam_max": lam_max,
                "n_population": len(pool),
                "backoff_ladder": [(n, len(r)) for n, _f, r in ladder],
                "age_mix_observed": base,
                "perturbed_axis": "strat_age_band, exponential tilt "
                                  "share(b) ~ base(b)*exp(lam*rank(b)), lam swept "
                                  "-lam_max..+lam_max (D-S6-11 item 1). NOT a "
                                  "reversal -- see FINDING 90.",
                "expectation_basis": "weighted per-stratum level-1 budgets over the "
                                     "TWO DONOR countries only, with a fixed backoff "
                                     "ladder so no prefix is dropped for being "
                                     "unpriced (D-S6-11 item 2)",
                "levels_detail": []}

    os.makedirs(a.out, exist_ok=True)
    for i in range(a.levels):
        t = i / float(a.levels - 1) if a.levels > 1 else 0.5
        lam = -lam_max + 2.0 * lam_max * t
        share = tilt_shares(base, lam)

        rows, exp_w = [], collections.Counter()
        for _ in range(a.n):
            b = _pick(rng, share)
            r = rng.choice(by_age[b])
            rows.append(r)
            exp_w[stratum(r)] += 1
        exp = dict((k, 0.0) for k in L1.AGGREGATES)
        rungs = collections.Counter()
        for k, c in exp_w.items():
            bud, rung = price(ladder, k)
            rungs[rung] += c
            for agg in L1.AGGREGATES:
                exp[agg] += c * bud[agg]
        for agg in exp:
            exp[agg] /= float(len(rows))

        p = os.path.join(a.out, "prefixes_g67_%s_t%02d.jsonl" % (a.fold, i))
        with open(p, "w", encoding="utf-8") as fh:
            for r in rows:
                out = dict(r)
                out["country"] = FICTIONAL
                out["prefix"] = ",".join([FICTIONAL] + r["prefix"].split(",")[1:])
                fh.write(json.dumps(out, sort_keys=True) + "\n")
        manifest["levels_detail"].append(
            {"level": i, "t": t, "lam": lam, "path": p, "n": len(rows),
             "age_mix": share, "mean_age_rank": mean_age_rank(share),
             "expected_budget": exp, "n_strata_drawn": len(exp_w),
             "priced_at_rung": dict(rungs)})
        print("  lam=%+.2f  mean age rank %.3f  expected AC0 %.1f  AC2 %.1f  "
              "AC1_TR %.1f  full-key %.0f %%"
              % (lam, mean_age_rank(share), exp["AC0"], exp["AC2"], exp["AC1_TR"],
                 100.0 * rungs.get("full", 0) / len(rows)))

    # 🔴 V6.g -- A PERTURBATION WITH NO AMPLITUDE IS NOT A PERTURBATION.
    rng_exp = {}
    for agg in L1.AGGREGATES:
        vals = [d["expected_budget"][agg] for d in manifest["levels_detail"]]
        rng_exp[agg] = max(vals) - min(vals)
    manifest["expected_range_min_per_day"] = rng_exp
    widest = max(rng_exp.values())
    manifest["amplitude_guard"] = {
        "widest_expected_range_min_per_day": widest, "min_required": 30.0,
        "passes": widest >= 30.0,
        "note": "FINDING 90: the first design moved the expected budget by 0.8 "
                "min/day end to end. A slope fitted across that is noise. G6.7 "
                "REFUSES to be scored below 30 min/day of expected movement."}
    print("\namplitude guard: widest expected range %.1f min/day "
          "(need >= 30) -> %s" % (widest, "OK" if widest >= 30.0 else "REFUSED"))

    mp = os.path.join(a.out, "g67_manifest_%s.json" % a.fold)
    with open(mp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True, default=str)
    print("\nwritten: %s" % mp)
    return 0


def _pick(rng, share):
    x = rng.random()
    c = 0.0
    for b, v in sorted(share.items()):
        c += v
        if x <= c:
            return b
    return sorted(share)[-1]


if __name__ == "__main__":
    sys.exit(main())
