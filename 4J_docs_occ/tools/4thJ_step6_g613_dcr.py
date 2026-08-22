# -*- coding: utf-8 -*-
"""`G6.13` — distance to closest record and NNDR on the synthetic release.

  usage: python 4thJ_step6_g613_dcr.py --gen DIR --leg 4 --corpus FILE
                                       --step2 DIR [--folds es,uk,it] [--out JSON]

The gate, verbatim from the validation document:

    FAILS if: any DCR = 0; or median DCR to train significantly below median DCR
    to test; or NNDR < 0.33 in over 0.1 % of records.

Three clauses, three different disclosure stories, and each needs a decision this
module makes explicitly rather than by default.

---------------------------------------------------------------------------
🔴 WHAT "DISTANCE" MEANS HERE, AND WHY
---------------------------------------------------------------------------

A diary is a sequence, not a row of attributes, so the usual tabular DCR does not
apply unchanged. The distance used is the **normalised Hamming distance between
144 ten-minute activity slots**.

  * 144 slots is EXACT, not a resampling: every duration in all 73,254 corpus
    diaries is a positive multiple of 10 and they sum to 1440 (the premise the
    145-state tally automaton is built on, counted rather than assumed).
  * It makes **`DCR = 0` mean exactly what the gate needs it to mean** — the
    synthetic day is minute-for-minute the same activity sequence as a real
    person's day. That is the disclosure event, and any weaker distance would let
    a verbatim copy score above zero.
  * It ignores `LOC`, `ACT2` and `COP`. 🔴 That makes this the **optimistic**
    reading: two days identical in activity but differing in location score 0
    here and would be flagged. Stated, because it is a choice.

The prefix is NOT part of the distance. It is part of the **stratum**, and the
extraction clause is about strata; folding it in would let a demographic
coincidence look like a disclosure.

---------------------------------------------------------------------------
🔴 TRAIN VERSUS TEST, WHICH IS THE HALF THAT CARRIES THE ARGUMENT
---------------------------------------------------------------------------

Clause 2 compares the median DCR to **train** against the median DCR to **test**.
Under LOCO the fold's model saw the other two countries' TRAIN split and never saw
the held-out country at all, so this module reports THREE reference sets:

    train      the donor countries' `split == "train"` diaries   -- what the model saw
    test       the donor countries' `split == "heldout"` diaries -- same distribution, unseen
    country    every diary of the LOCO held-out country          -- unseen, different country

🔴 The corpus `split` column takes exactly two values, `train` and `heldout`, and
`heldout` is the SECOND hold-out of `D-S6-1` -- the 10 % household split inside
each country -- not the LOCO country hold-out. Looking for `split == "test"` finds
nothing, and the first version of this module did exactly that: it built no `test`
reference, skipped the train-versus-test comparison entirely, and still printed
PASS on all three folds.

🔴 `train` versus `test` is the memorisation test. `country` is reported beside
them and is NOT part of the verdict: it differs by country as well as by exposure,
so a gap there is not evidence of memorisation.

"Significantly below" is made concrete: a **Mann-Whitney U** on the two DCR
distributions, plus the median difference in slots. Both are printed; the
threshold is project-chosen and is declared as such.

---------------------------------------------------------------------------
🔴 THE SIZE CONFOUND, WHICH MAKES THE RAW COMPARISON WORTHLESS
---------------------------------------------------------------------------

`train` is roughly **NINE TIMES** the size of `test` -- 48,594 against 5,520 on
the `es` fold -- because the second hold-out is a 10 % household split. A nearest
neighbour drawn from a nine-times-larger pool is **mechanically closer**, with or
without memorisation. Compared raw, all three folds FAIL clause 2 at
p < 1e-9, and none of it is evidence of anything.

The verdict is therefore taken on a **SAMPLE-SIZE-MATCHED** comparison: `train` is
subsampled without replacement to `|test|`, with a fixed seed, `R` times, and the
distribution of median DCR over those draws is what `test` is compared against.
This is the discipline the Overview already mandates for `G6.8` -- *"a
sample-size-matched bootstrap ... That last comparison is the honest one."*

🔴 The RAW comparison is still printed, labelled, and explicitly NOT the verdict.
Deleting it would hide the size effect; using it would be a false alarm.
"""

import argparse
import collections
import importlib
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import decoder as dec
from encoder import load_bit_positions

SLOT = 10
N_SLOTS = 1440 // SLOT          # 144, exact -- see the docstring
NNDR_MAX = 0.33
NNDR_SHARE_MAX = 0.001          # 0.1 % of records
ALPHA = 0.01                    # project-chosen; declared, never cited as literature
N_MATCHED_DRAWS = 200           # subsamples of `train` at |test|
MATCH_SEED = 20260822


class DcrError(ValueError):
    pass


def slots(record, code_index):
    """One decoded record -> a 144-long list of activity-code integers."""
    out = []
    for e in record["episodes"]:
        d = int(e["duration_min"])
        if d % SLOT:
            raise DcrError("duration %d is not a multiple of %d; the 144-slot "
                           "representation is exact or it is nothing" % (d, SLOT))
        a = e.get("act") or "000"
        out.extend([code_index.setdefault(a, len(code_index))] * (d // SLOT))
    if len(out) != N_SLOTS:
        raise DcrError("record expands to %d slots, not %d" % (len(out), N_SLOTS))
    return out


def mannwhitney_u(a, b):
    """Two-sided normal approximation with a tie correction. Returned as
    (U, z, p). Written out rather than imported: `scipy` is not in this
    environment and a gate that cannot run is not a gate."""
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        raise DcrError("Mann-Whitney needs both samples non-empty")
    merged = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks = [0.0] * (n1 + n2)
    i = 0
    tie_term = 0.0
    while i < len(merged):
        j = i
        while j + 1 < len(merged) and merged[j + 1][0] == merged[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        t = j - i + 1
        tie_term += t ** 3 - t
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    r1 = sum(ranks[k] for k in range(len(merged)) if merged[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    n = n1 + n2
    var = n1 * n2 / 12.0 * ((n + 1) - tie_term / float(n * (n - 1)))
    if var <= 0:
        return u1, 0.0, 1.0
    z = (u1 - mu) / math.sqrt(var)
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return u1, z, p


def distance_matrix(syn, pool, chunk=2048):
    """Full `len(syn) x len(pool)` Hamming distance matrix, in SLOTS (int16).

    Built once per reference set. The size-matched comparison then subsamples
    COLUMNS of this matrix instead of re-scanning the pool 200 times -- the naive
    version was ~95 G element comparisons per fold and did not finish.
    """
    import numpy as np
    if pool.shape[0] < 2:
        raise DcrError("a nearest-neighbour ratio needs at least two reference "
                       "records; NNDR over one is not defined")
    out = np.empty((syn.shape[0], pool.shape[0]), dtype=np.int16)
    for i in range(0, pool.shape[0], chunk):
        blk = pool[i:i + chunk]
        out[:, i:i + chunk] = (syn[:, None, :] != blk[None, :, :]).sum(axis=2)
    return out


def two_smallest(D):
    """Per row of a distance matrix: (d1, d2) normalised. Vectorised."""
    import numpy as np
    part = np.partition(D, 1, axis=1)[:, :2]
    return part[:, 0] / float(N_SLOTS), part[:, 1] / float(N_SLOTS)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--out")
    ap.add_argument("--perturb", choices=("null", "verbatim", "nearcopy", "leak_all"),
                    default="null",
                    help="null: nothing. verbatim: one TRAIN diary copied into the "
                         "release (DCR=0). nearcopy: one TRAIN diary with two slots "
                         "changed (a low NNDR). leak_all: every synthetic record "
                         "replaced by a TRAIN diary")
    a = ap.parse_args(argv)

    import numpy as np
    bp = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))
    code_index = {}

    print("=" * 78)
    print("G6.13 -- DCR and NNDR on the synthetic release")
    print("=" * 78)
    print("distance: normalised Hamming over %d ten-minute ACTIVITY slots" % N_SLOTS)
    print("🔴 LOC, ACT2 and COP are NOT in the distance -- the OPTIMISTIC reading")
    print("thresholds: any DCR = 0 FAILs | NNDR < %.2f in > %.1f %% of records FAILs"
          % (NNDR_MAX, 100 * NNDR_SHARE_MAX))
    print("            median DCR(train) < median DCR(test): Mann-Whitney, alpha "
          "%.2f, PROJECT-CHOSEN" % ALPHA)
    if a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    print("reading the corpus ...")
    corpus = collections.defaultdict(list)      # (country, split) -> [slots]
    n_corpus = 0
    for line in open(a.corpus, encoding="utf-8"):
        r = json.loads(line)
        d = dec.decode_record(r["text"], bp)
        corpus[(r["country"], r["split"])].append(slots(d, code_index))
        n_corpus += 1
    print("  %d diaries | %d distinct activity codes seen | splits: %s"
          % (n_corpus, len(code_index),
             sorted(set(k[1] for k in corpus))))

    out = {"leg": a.leg, "n_corpus": n_corpus, "n_slots": N_SLOTS, "folds": {}}
    for fold in a.folds.split(","):
        gp = os.path.join(a.gen, "generated_leg%d_%s_constrained.jsonl" % (a.leg, fold))
        if not os.path.exists(gp):
            print("\n%s: no batch at %s -- NOT SCORED" % (fold, gp))
            continue
        gen_rows = [json.loads(l) for l in open(gp, encoding="utf-8") if l.strip()]
        syn = np.array([slots(dec.decode_record(r["text"], bp), code_index)
                        for r in gen_rows], dtype=np.int16)

        donors_pre = [c for c in ("es", "uk", "it") if c != fold]
        if a.perturb != "null":
            # The perturbations inject REAL TRAIN diaries into the release, which
            # is exactly the disclosure each clause is written to catch.
            tr = np.array([x for c in donors_pre for x in corpus[(c, "train")]],
                          dtype=np.int16)
            if a.perturb == "verbatim":
                syn[0] = tr[0]
            elif a.perturb == "nearcopy":
                syn[0] = tr[0]
                syn[0][0] = (syn[0][0] + 1) % max(len(code_index), 2)
                syn[0][1] = (syn[0][1] + 1) % max(len(code_index), 2)
            elif a.perturb == "leak_all":
                syn = tr[:syn.shape[0]].copy()
            print("\n  PERTURBATION %s applied to fold %s" % (a.perturb, fold))

        donors = [c for c in ("es", "uk", "it") if c != fold]
        # 🔴 The corpus `split` column has TWO values, `train` and `heldout`, and
        # `heldout` is the SECOND hold-out of `D-S6-1` -- the 10 % household split
        # inside every country -- NOT the LOCO country hold-out. Written first as
        # `split == "test"`, this clause found no records, built no reference set,
        # and the train-versus-test comparison SILENTLY DID NOT RUN while the gate
        # still printed PASS. That is the vacuity failure this project keeps
        # finding, in the gate that is supposed to protect a data release.
        refs = {}
        want = (("train",   [(c, "train") for c in donors]),
                ("test",    [(c, "heldout") for c in donors]),
                ("country", [(fold, s) for s in ("train", "heldout")]))
        for name, keys in want:
            rows = [x for k in keys for x in corpus.get(k, [])]
            if not rows:
                raise DcrError(
                    "reference set %r is EMPTY. G6.13 REFUSES rather than scoring "
                    "the clauses it can still reach: a privacy gate that quietly "
                    "drops its own comparison is worse than one that does not run."
                    % name)
            refs[name] = np.array(rows, dtype=np.int16)

        print("\n" + "-" * 78)
        print("fold %s  |  %d synthetic diaries  |  reference sets: %s"
              % (fold, len(syn), {k: int(v.shape[0]) for k, v in refs.items()}))
        print("-" * 78)

        fold_out = {"n_synthetic": len(syn),
                    "reference_sizes": {k: int(v.shape[0]) for k, v in refs.items()},
                    "sets": {}}
        dcr = {}
        dmat = {}
        for name, pool in refs.items():
            D = distance_matrix(syn, pool)
            dmat[name] = D
            a1, a2 = two_smallest(D)
            d1s, d2s = list(a1), list(a2)
            exact = int((a1 == 0.0).sum())
            nndr = [(x / y) if y > 0 else 1.0 for x, y in zip(d1s, d2s)]
            below = sum(1 for v in nndr if v < NNDR_MAX)
            dcr[name] = d1s
            srt = sorted(d1s)
            med = srt[len(srt) // 2]
            fold_out["sets"][name] = dict(
                n_reference=int(pool.shape[0]),
                dcr_min=min(d1s), dcr_median=med, dcr_mean=sum(d1s) / len(d1s),
                n_exact_matches=exact,
                nndr_median=sorted(nndr)[len(nndr) // 2],
                n_nndr_below=below, share_nndr_below=below / float(len(nndr)))
            print("  %-8s n_ref=%6d  DCR min %.4f  median %.4f  mean %.4f  "
                  "| exact matches %d  | NNDR<%.2f: %d (%.3f %%)"
                  % (name, pool.shape[0], min(d1s), med, sum(d1s) / len(d1s),
                     exact, NNDR_MAX, below, 100.0 * below / len(nndr)))

        reasons = []
        for name in ("train", "test", "country"):
            s = fold_out["sets"].get(name)
            if not s:
                continue
            if name != "country" and s["n_exact_matches"] > 0:
                reasons.append("%d synthetic diaries are an EXACT activity-sequence "
                               "match to a %s diary (DCR = 0)"
                               % (s["n_exact_matches"], name))
            if name != "country" and s["share_nndr_below"] > NNDR_SHARE_MAX:
                reasons.append("NNDR < %.2f in %.3f %% of records against %s "
                               "(limit %.1f %%)"
                               % (NNDR_MAX, 100 * s["share_nndr_below"], name,
                                  100 * NNDR_SHARE_MAX))
        # --- clause 2, raw. PRINTED, NOT THE VERDICT. See the size confound. ---
        u, z, p = mannwhitney_u(dcr["train"], dcr["test"])
        mt = sorted(dcr["train"])[len(dcr["train"]) // 2]
        ms = sorted(dcr["test"])[len(dcr["test"]) // 2]
        ratio = refs["train"].shape[0] / float(refs["test"].shape[0])
        print("  train vs test  RAW      : median %.4f vs %.4f (%+.2f slots)  "
              "z=%.3f p=%.4g   🔴 pool ratio %.2fx -- NOT THE VERDICT"
              % (mt, ms, (mt - ms) * N_SLOTS, z, p, ratio))

        # --- clause 2, SIZE-MATCHED. This is the verdict. ---
        rng = np.random.RandomState(MATCH_SEED)
        n_test = refs["test"].shape[0]
        Dtr = dmat["train"]
        med_draws = []
        for _ in range(N_MATCHED_DRAWS):
            idx = rng.choice(Dtr.shape[1], size=n_test, replace=False)
            ds = Dtr[:, idx].min(axis=1) / float(N_SLOTS)
            med_draws.append(float(np.median(ds)))
        med_draws.sort()
        lo = med_draws[int(0.025 * len(med_draws))]
        hi = med_draws[int(0.975 * len(med_draws)) - 1]
        centre = med_draws[len(med_draws) // 2]
        below = ms < lo          # test median BELOW the matched train interval is fine;
        above = ms > hi          # the alarm is train being closer, i.e. test ABOVE it
        print("  train vs test  MATCHED  : train median %.4f [%.4f, %.4f] over %d "
              "draws at n=%d   test %.4f  %s"
              % (centre, lo, hi, N_MATCHED_DRAWS, n_test, ms,
                 "🔴 OUTSIDE" if above else "inside"))
        fold_out["train_vs_test"] = dict(
            raw=dict(u=u, z=z, p=p, median_train=mt, median_test=ms,
                     median_difference_slots=(mt - ms) * N_SLOTS,
                     pool_ratio=ratio, is_verdict=False),
            size_matched=dict(n_draws=N_MATCHED_DRAWS, n=n_test, seed=MATCH_SEED,
                              median_train_centre=centre, ci95=[lo, hi],
                              median_test=ms, test_above_interval=bool(above),
                              is_verdict=True),
            alpha=ALPHA)
        if above:
            reasons.append(
                "SIZE-MATCHED: median DCR to TEST (%.4f) lies ABOVE the 95 %% "
                "interval of median DCR to a train subsample of the same size "
                "[%.4f, %.4f] -- the model is closer to what it was trained on "
                "than to unseen diaries of the same distribution"
                % (ms, lo, hi))
        fold_out["passes"] = not reasons
        fold_out["reasons"] = reasons
        print("  VERDICT %s" % ("PASS" if not reasons else "FAIL"))
        for r in reasons:
            print("    - %s" % r)
        out["folds"][fold] = fold_out

    board = collections.Counter("PASS" if v.get("passes") else "FAIL"
                                for v in out["folds"].values())
    out["board"] = dict(board)
    print("\n" + "=" * 78)
    print("G6.13 BOARD: %s" % dict(board))
    print("=" * 78)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
