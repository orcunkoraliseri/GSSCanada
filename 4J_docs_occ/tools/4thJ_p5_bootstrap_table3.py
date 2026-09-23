# -*- coding: utf-8 -*-
"""
4J / P5 -- 95 % bootstrap intervals and sample sizes for Table 3.

Spec: `writing/submission/IMP/impl/P5_intervals_table3.md`. Implements the fixed
design there exactly. Does NOT re-derive the metric, the null, or the pass rule --
those are imported, never reimplemented:

    tools/4thJ_step6_level1.py       -- level-1 budget, MAE, published tables
    tools/4thJ_step6_rakeddonor.py   -- IPF raking, score_margin (V6.c)
    tools/4thJ_step6_g61_rake_folds.py -- the registered collapses, target-from-population
    tools/4thJ_step6_g61_score.py    -- build_null(), the exact G6.1 wiring

WHAT THIS ADDS ON TOP
======================
A nonparametric bootstrap around the already-frozen G6.1 pipeline:

  * model side  -- resample the fold's generated diaries WITHIN each age band,
                   same n as the original band, recompute the band budget/MAE.
  * null side   -- resample the WHOLE donor pool WITHIN each donor country (same
                   n per country as the original pool), RE-RAKE the resampled
                   pool with the SAME code/tolerance/target as G6.1, THEN slice
                   the raked pool to the band (raking happens before banding,
                   exactly as `4thJ_step6_g61_score.py` already insists it must).

The null-side resample is shared across the fold's three bands within one
replicate (one re-rake per fold per replicate, not three) -- it is the same
raked pool that G6.1 slices three ways, so bootstrapping it once and slicing
three ways is the same design, not a shortcut.

A replicate whose re-rake refuses (non-convergence, or a category the resample
happened to lose entirely) is counted and excluded from that fold's margin
distributions for that replicate -- never dropped silently, always counted
(`Step6_docs/outputs_step6/P5_table3_bootstrap.json` carries the count; the
printed table carries it too).

Seeds are ALWAYS string seeds, `random.Random("p5|<fold>|...|<rep>")`, never a
tuple -- see P3's reproducibility note.
"""

import argparse
import collections
import importlib
import json
import math
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
ROOT = os.path.dirname(_HERE)

L1 = importlib.import_module("4thJ_step6_level1")
rd = importlib.import_module("4thJ_step6_rakeddonor")
rf = importlib.import_module("4thJ_step6_g61_rake_folds")
g61 = importlib.import_module("4thJ_step6_g61_score")
import decoder as dec
from encoder import load_bit_positions

FOLDS = ("es", "uk", "it")
BANDS = L1.SCOREABLE_BANDS
LEG = 5
WAVE = "2010"
NUM_REPS = 2000        # B, the bootstrap replicate count (spec section "Method")
SEED_PREFIX = "p5"

# C2 control cell -- "the cell to watch" per the spec's "Expected result" section.
C2_FOLD = "uk"
C2_BAND = "Y_GE65"

DEFAULT_OUT = os.path.join(ROOT, "Step6_docs", "outputs_step6", "P5_table3_bootstrap.json")
DEFAULT_SCORED = os.path.join(ROOT, "Step6_docs", "outputs_step6", "g61_leg5_scored.json")
DEFAULT_EUROSTAT = os.path.join(ROOT, "Step6_docs", "outputs_step6", "eurostat_raw")
DEFAULT_GEN = os.path.join(ROOT, "Step7_docs", "outputs_step7")
DEFAULT_CROSSWALK = os.path.join(ROOT, "Step2_docs", "outputs_step2", "crosswalk_copresence.csv")
DEFAULT_CORPUS = rf.CORPUS


# ---------------------------------------------------------------------------
# small numeric helpers -- no numpy dependency, deliberately
# ---------------------------------------------------------------------------
def kish_ess(weights):
    """(sum w)^2 / sum w^2. 0.0 if the weights sum to nothing."""
    s1 = sum(weights)
    s2 = sum(w * w for w in weights)
    return (s1 * s1 / s2) if s2 > 0 else 0.0


def percentile(values, p):
    """Linear-interpolation percentile (numpy's default method), no numpy."""
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    if n == 1:
        return s[0]
    k = (n - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] * (c - k) + s[int(c)] * (k - f)


def resample_with_replacement(rng, idx_list):
    """`len(idx_list)` draws with replacement FROM `idx_list`, using a seeded rng."""
    n = len(idx_list)
    if n == 0:
        return []
    return [idx_list[rng.randrange(n)] for _ in range(n)]


# ---------------------------------------------------------------------------
# per-fold data loading -- reuses the Step 6 functions, never reimplements them
# ---------------------------------------------------------------------------
def load_fold_data(fold, bp, corpus_path, gen_dir, eurostat_dir):
    """Everything one fold needs, loaded once: donor pool, target marginals,
    the registered collapse, the generated batch, and the published tables."""
    tgt, n_pop = rf.target_from_population(fold)
    strata, recs = g61.load_donors(corpus_path, fold, bp)
    donor_bands = [L1.AGE_BAND_MAP.get(s["strat_age_band"]) for s in strata]

    by_country = collections.OrderedDict()
    for i, d in enumerate(strata):
        by_country.setdefault(d["country"], []).append(i)

    # The exact collapse G6.1 uses (`4thJ_step6_g61_score.build_null`), including
    # its "registered collapse" refusal -- never re-derived here.
    coll = {"strat_hh_type": {"unknown": "other_complex"}}
    if "homemaker" not in tgt["strat_econ_status"]:
        coll["strat_econ_status"] = {"homemaker": "other_inactive"}
    for cat in set(d["strat_econ_status"] for d in strata):
        if cat not in tgt["strat_econ_status"] and cat != "homemaker":
            coll.setdefault("strat_econ_status", {})[cat] = "other_inactive"
    unreg = rf.check_registered(coll)
    if unreg:
        raise SystemExit("REFUSED: collapse(s) not registered in %s: %s"
                          % (rf.ADDENDUM, "; ".join("%s: %s->%s" % t for t in unreg)))
    marginals_source = "population_%s.csv|D-S5-11b" % fold

    gp = os.path.join(gen_dir, "generated_leg%d_%s_constrained.jsonl" % (LEG, fold))
    gen_rows = [json.loads(l) for l in open(gp, encoding="utf-8") if l.strip()]
    gen_recs = [dec.decode_record(r["text"], bp) for r in gen_rows]
    gen_bands = [L1.AGE_BAND_MAP.get(r["strat_age_band"]) for r in gen_rows]

    pub = {band: L1.published(eurostat_dir, fold, age=band, wave=WAVE) for band in BANDS}

    return dict(fold=fold, tgt=tgt, n_pop=n_pop, strata=strata, recs=recs,
                donor_bands=donor_bands, by_country=by_country, collapse=coll,
                marginals_source=marginals_source, gen_rows=gen_rows,
                gen_recs=gen_recs, gen_bands=gen_bands, pub=pub)


def band_indices(bands_list, band):
    return [i for i, b in enumerate(bands_list) if b == band]


# ---------------------------------------------------------------------------
# point estimate -- "replicate 0 = original data" for the C1 reproduction check
# ---------------------------------------------------------------------------
def point_estimate(fd):
    """No resampling anywhere. Reuses `rd.rake` directly on the full donor pool,
    exactly as `4thJ_step6_g61_score.build_null` does (that function is not
    called here only because it re-reads the corpus from disk; the rake call
    and its inputs are identical)."""
    res = rd.rake(fd["strata"], fd["tgt"], fd["fold"],
                  marginals_source=fd["marginals_source"], collapse=fd["collapse"])
    weights = res["weights"]
    mi = {band: band_indices(fd["gen_bands"], band) for band in BANDS}
    ni = {band: band_indices(fd["donor_bands"], band) for band in BANDS}

    out = {}
    for band in BANDS:
        pub = fd["pub"][band]
        m_bud = L1.budget([fd["gen_recs"][i] for i in mi[band]])
        n_bud = L1.budget([fd["recs"][i] for i in ni[band]],
                          weights=[weights[i] for i in ni[band]])
        m_mae = L1.mae(m_bud, pub)
        n_mae = L1.mae(n_bud, pub)
        margin = n_mae - m_mae   # score_margin(lower_is_better=True): null - model
        by_country = collections.Counter(fd["strata"][i]["country"] for i in ni[band])
        out[band] = dict(
            model_mae0=m_mae, null_mae0=n_mae, margin0=margin,
            n_model=len(mi[band]),
            n_donor_by_country=dict(by_country),
            kish_ess0=kish_ess([weights[i] for i in ni[band]]),
        )
    return out, mi, ni, weights, res


# ---------------------------------------------------------------------------
# the bootstrap itself
# ---------------------------------------------------------------------------
def run_fold(fold, bp_path, corpus_path, gen_dir, eurostat_dir, num_reps, do_c2):
    """Everything for one fold: point estimate + B bootstrap replicates for its
    three bands, and (only for the C2 fold) the null-vs-itself control."""
    bp = load_bit_positions(bp_path)
    fd = load_fold_data(fold, bp, corpus_path, gen_dir, eurostat_dir)
    point, mi, ni, weights0, rake0 = point_estimate(fd)

    margins = {band: [] for band in BANDS}
    n_nonconverged = 0

    for rep in range(1, num_reps + 1):
        model_mae_rep = {}
        for band in BANDS:
            seed = "%s|%s|%s|model|%d" % (SEED_PREFIX, fold, band, rep)
            rng = random.Random(seed)
            idx = resample_with_replacement(rng, mi[band])
            bud = L1.budget([fd["gen_recs"][i] for i in idx])
            model_mae_rep[band] = L1.mae(bud, fd["pub"][band])

        seed = "%s|%s|null|%d" % (SEED_PREFIX, fold, rep)
        rng = random.Random(seed)
        resampled_idx = []
        for country, idxs in fd["by_country"].items():
            resampled_idx.extend(resample_with_replacement(rng, idxs))
        resampled_strata = [fd["strata"][i] for i in resampled_idx]

        try:
            res = rd.rake(resampled_strata, fd["tgt"], fold,
                          marginals_source=fd["marginals_source"], collapse=fd["collapse"])
        except rd.RakeError:
            n_nonconverged += 1
            continue

        w = res["weights"]
        resampled_bands = [fd["donor_bands"][i] for i in resampled_idx]
        for band in BANDS:
            bi = band_indices(resampled_bands, band)
            if not bi:
                continue
            bud = L1.budget([fd["recs"][resampled_idx[i]] for i in bi],
                            weights=[w[i] for i in bi])
            n_mae_rep = L1.mae(bud, fd["pub"][band])
            margins[band].append(n_mae_rep - model_mae_rep[band])

    cells = {}
    for band in BANDS:
        m = margins[band]
        cells[band] = dict(
            point[band],   # keep the point-estimate fields (model_mae0, margin0, ...)
            ci_lo=percentile(m, 2.5), ci_hi=percentile(m, 97.5),
            n_bootstrap_used=len(m), n_nonconverged=n_nonconverged,
        )

    c2 = None
    if do_c2:
        c2 = run_c2(fold, fd, num_reps)

    return fold, cells, n_nonconverged, c2


def run_c2(fold, fd, num_reps):
    """C2: bootstrap the NULL against a second, independent bootstrap of the
    NULL, for one cell (`C2_FOLD`/`C2_BAND`). The margin interval must contain
    0 -- proof the raking machinery does not manufacture a difference out of
    nothing when both sides ARE nothing but noise."""
    band = C2_BAND
    margins = []
    n_nonconverged = 0
    for rep in range(1, num_reps + 1):
        maes = []
        for tag in ("nullA", "nullB"):
            seed = "%s|%s|%s|%d" % (SEED_PREFIX, fold, tag, rep)
            rng = random.Random(seed)
            resampled_idx = []
            for country, idxs in fd["by_country"].items():
                resampled_idx.extend(resample_with_replacement(rng, idxs))
            resampled_strata = [fd["strata"][i] for i in resampled_idx]
            try:
                res = rd.rake(resampled_strata, fd["tgt"], fold,
                              marginals_source=fd["marginals_source"], collapse=fd["collapse"])
            except rd.RakeError:
                maes.append(None)
                continue
            w = res["weights"]
            resampled_bands = [fd["donor_bands"][i] for i in resampled_idx]
            bi = band_indices(resampled_bands, band)
            if not bi:
                maes.append(None)
                continue
            bud = L1.budget([fd["recs"][resampled_idx[i]] for i in bi],
                            weights=[w[i] for i in bi])
            maes.append(L1.mae(bud, fd["pub"][band]))
        if maes[0] is None or maes[1] is None:
            n_nonconverged += 1
            continue
        margins.append(maes[0] - maes[1])

    lo, hi = percentile(margins, 2.5), percentile(margins, 97.5)
    contains_zero = (lo is not None and hi is not None and lo <= 0.0 <= hi)
    return dict(fold=fold, band=band, ci_lo=lo, ci_hi=hi,
                n_bootstrap_used=len(margins), n_nonconverged=n_nonconverged,
                passes=contains_zero)


# ---------------------------------------------------------------------------
# controls C1 / C3, and the report
# ---------------------------------------------------------------------------
def check_c1(cells, scored_path, folds):
    """Reproduction: the no-resampling point estimate must equal Table 3 /
    `g61_leg5_scored.json` to the printed (4-decimal) precision, all nine cells."""
    if not os.path.exists(scored_path):
        return False, ["no scored file at %s" % scored_path]
    with open(scored_path, encoding="utf-8") as fh:
        scored = json.load(fh)
    mismatches = []
    for fold in folds:
        fold_scored = (scored.get("folds") or {}).get(fold) or {}
        bands_scored = fold_scored.get("bands") or {}
        for band in BANDS:
            ref = bands_scored.get(band)
            got = cells[fold][band]
            if ref is None or ref.get("blocked"):
                mismatches.append("%s/%s: no scored reference" % (fold, band))
                continue
            for key, ref_key in (("model_mae0", "model_mae"),
                                 ("null_mae0", "null_mae"),
                                 ("margin0", "margin")):
                got_v = round(got[key], 4)
                ref_v = ref.get(ref_key)
                if ref_v is None or abs(got_v - ref_v) > 1e-4 + 1e-9:
                    mismatches.append("%s/%s %s: got %r, table says %r"
                                      % (fold, band, key, got_v, ref_v))
    return (not mismatches), mismatches


def check_c3(cells, folds):
    """Every interval must contain its own point estimate."""
    failures = []
    for fold in folds:
        for band in BANDS:
            c = cells[fold][band]
            if c["ci_lo"] is None or c["ci_hi"] is None:
                failures.append("%s/%s: no interval (all replicates non-converged)" % (fold, band))
                continue
            if not (c["ci_lo"] <= c["margin0"] <= c["ci_hi"]):
                failures.append("%s/%s: point estimate %.4f outside [%.4f, %.4f]"
                                % (fold, band, c["margin0"], c["ci_lo"], c["ci_hi"]))
    return (not failures), failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--gen-dir", default=DEFAULT_GEN)
    ap.add_argument("--eurostat", default=DEFAULT_EUROSTAT)
    ap.add_argument("--crosswalk", default=DEFAULT_CROSSWALK)
    ap.add_argument("--scored", default=DEFAULT_SCORED)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--num-reps", type=int, default=NUM_REPS)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--folds", default=",".join(FOLDS))
    a = ap.parse_args(argv)

    folds = a.folds.split(",")
    t0 = time.time()
    print("=" * 78)
    print("P5 -- bootstrap 95%% intervals for Table 3, B=%d, leg=%d" % (a.num_reps, LEG))
    print("=" * 78)

    cells = {f: {} for f in folds}
    n_nonconverged = {}
    c2_result = None
    with ProcessPoolExecutor(max_workers=min(a.workers, len(folds))) as ex:
        futs = {}
        for fold in folds:
            do_c2 = (fold == C2_FOLD)
            fut = ex.submit(run_fold, fold, a.crosswalk, a.corpus, a.gen_dir,
                            a.eurostat, a.num_reps, do_c2)
            futs[fut] = fold
        for fut in as_completed(futs):
            fold, fold_cells, nn, c2 = fut.result()
            cells[fold] = fold_cells
            n_nonconverged[fold] = nn
            if c2 is not None:
                c2_result = c2
            print("  fold %s done (%.1f s elapsed)" % (fold, time.time() - t0))

    if C2_FOLD not in folds and c2_result is None:
        print("  !!! C2 fold %r was not run (folds=%s); C2 cannot be checked" % (C2_FOLD, a.folds))

    c1_ok, c1_msgs = check_c1(cells, a.scored, folds)
    print("\nC1 reproduction (no resampling matches Table 3, all nine cells): %s"
          % ("PASS" if c1_ok else "FAIL"))
    for m in c1_msgs[:20]:
        print("    - %s" % m)

    if not c1_ok:
        print("\nC1 FAILED -- stopping. No interval is reported (spec: 'If C1 fails, stop').")
        payload = dict(leg=LEG, wave=WAVE, num_reps=a.num_reps,
                       controls=dict(C1=dict(passes=False, messages=c1_msgs)),
                       folds=cells)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True, default=str)
        return 1

    c2_ok = bool(c2_result and c2_result["passes"])
    print("C2 null-vs-itself (margin interval contains 0, fold=%s band=%s): %s"
          % (C2_FOLD, C2_BAND, "PASS" if c2_ok else "FAIL"))
    if c2_result:
        print("    interval [%.4f, %.4f], %d/%d replicates converged"
              % (c2_result["ci_lo"], c2_result["ci_hi"],
                 c2_result["n_bootstrap_used"], a.num_reps))

    c3_ok, c3_msgs = check_c3(cells, folds)
    print("C3 coverage sanity (each interval contains its point estimate): %s"
          % ("PASS" if c3_ok else "FAIL"))
    for m in c3_msgs[:20]:
        print("    - %s" % m)

    print("\n" + "-" * 110)
    print("%-4s %-8s %10s %10s %9s %9s %9s %7s %-26s %8s %6s"
          % ("fold", "band", "MAE_model", "MAE_null", "margin", "2.5%", "97.5%",
             "n_mod", "n_donor(by country)", "KishESS", "nonconv"))
    print("-" * 110)
    rows = []
    for fold in folds:
        for band in BANDS:
            c = cells[fold][band]
            donor_str = ",".join("%s=%d" % (k, v) for k, v in sorted(c["n_donor_by_country"].items()))
            print("%-4s %-8s %10.3f %10.3f %+9.3f %9.3f %9.3f %7d %-26s %8.0f %6d"
                  % (fold, band, c["model_mae0"], c["null_mae0"], c["margin0"],
                     c["ci_lo"], c["ci_hi"], c["n_model"], donor_str,
                     c["kish_ess0"], c["n_nonconverged"]))
            rows.append(dict(fold=fold, band=band, **c))
    print("-" * 110)

    payload = dict(
        leg=LEG, wave=WAVE, num_reps=a.num_reps, seed_prefix=SEED_PREFIX,
        controls=dict(
            C1=dict(passes=c1_ok, messages=c1_msgs),
            C2=(c2_result if c2_result is not None
                else dict(passes=False, fold=C2_FOLD, band=C2_BAND,
                          note="C2 fold was not among --folds; not run")),
            C3=dict(passes=c3_ok, messages=c3_msgs),
        ),
        table3_rows=rows,
        folds=cells,
        elapsed_sec=round(time.time() - t0, 1),
    )
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    print("\nwritten: %s" % a.out)
    print("elapsed: %.1f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
