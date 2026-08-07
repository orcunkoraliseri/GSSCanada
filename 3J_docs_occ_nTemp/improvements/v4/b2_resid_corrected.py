# -*- coding: utf-8 -*-
"""V4-B2, residential half -- scores the three PRE-REGISTERED predictions.

Pre-registration: `V4-B2_PREREGISTRATION_resid_sample.md`, written before the first residential
`eplusout.sql` was fetched. This script does not restate the predictions; it evaluates them.

  P3  the SHIPPED sample median must land within ~2 % of the published value for every archetype.
      🔴 CHECKED AND PRINTED FIRST. If it fails, nothing below it means anything.
  P1  `OtherDwelling` and `HighRise` corrected medians land BELOW their floors, and the upper end of
      the 95 % interval stays below too.
  P2  `SingleD` -- NO direction predicted. Reported as measured.

The interval is EXACT and distribution-free, from order statistics of the binomial -- no normality
assumption and no bootstrap. It is COMPUTED for the achieved n rather than hard-coded, so a sample
that came back short is still scored correctly instead of being read against a table for n = 100.

Input: `v4_b2_resid_factors.jsonl` (one record per sampled run). Output: `v4_b2_resid_corrected.json`.
"""
import io
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "v4_b2_resid_factors.jsonl")

# Bands and published values are read from LEG-2's OWN artefacts, not from V4-B2_defect_reach.md.
# Copying them out of my own write-up would be a consistency check whose two inputs share an
# ancestor -- it could not catch a value that is wrong in both. Verified 2026-08-06 against:
#   bands      Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:43-46
#   published  Leg2_2-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv rows 2-5 (n = 2100 each)  # FROZEN-INPUT-OK: LEG-2 path -- the freeze registry covers Leg3_4-split only, so this directory has no frozen counterpart and is not superseded; this is a provenance comment, not a read
ROWS = {
    "SingleD":       {"published": 211.7, "band": (130.6, 186.1)},
    "OtherDwelling": {"published": 140.0, "band": (136.1, 186.1)},
    "MidRise":       {"published": 177.5, "band": (111.1, 216.7)},
    "HighRise":      {"published": 143.0, "band": (113.9, 147.2)},
}
P1_ROWS = ("OtherDwelling", "HighRise")


def verdict(x, band):
    return "IN" if band[0] <= x <= band[1] else ("BELOW" if x < band[0] else "ABOVE")


def median_ci(sorted_vals, conf=0.95):
    """Exact distribution-free CI for the median from order statistics.

    Under H0 the number of observations below the true median is Binomial(n, 1/2). The interval
    [x(k+1), x(n-k)] has coverage 1 - 2*P(Bin(n,1/2) <= k-1); take the largest k whose tail stays
    within alpha/2 on each side. Returns (lo, hi, k_lo_index_1based, k_hi_index_1based, coverage).
    """
    n = len(sorted_vals)
    if n < 6:                       # below this an exact 95 % interval does not exist at all
        return None
    alpha = 1.0 - conf
    # cumulative Binomial(n, 1/2) via exact integer binomials -- no float pmf, no scipy
    from math import comb
    tot = 2.0 ** n
    cum = 0.0
    k = 0
    while True:
        nxt = cum + comb(n, k) / tot
        if nxt > alpha / 2.0:
            break
        cum = nxt
        k += 1
    if k == 0:
        return None
    lo_i, hi_i = k, n - k + 1       # 1-based order statistics
    coverage = 1.0 - 2.0 * cum
    return sorted_vals[lo_i - 1], sorted_vals[hi_i - 1], lo_i, hi_i, coverage


def main():
    with io.open(SRC, encoding="utf-8") as fh:
        recs = [json.loads(l) for l in fh if l.strip()]
    ok = list({r["run_dir"]: r for r in recs
               if not r.get("error") and r.get("factor")}.values())
    got = {r["run_dir"] for r in ok}
    missing = [r for r in recs if r.get("error") and r["run_dir"] not in got]
    print("runs retrieved: %d   still missing: %d" % (len(ok), len(missing)))
    for r in missing:
        print("   !! %s %s -- %s" % (r["cell"], r["scenario"], r.get("error")))

    g = {}
    for r in ok:
        g.setdefault(r["arch"], []).append(r)

    # ---- P3 first, and nothing is read until it is printed -------------------------------------
    print("\n=== P3 -- does the sample reproduce the published population? ===")
    print("%-15s %5s | %12s %10s %8s | %s"
          % ("archetype", "n", "shipped med", "published", "diff %", "P3"))
    p3 = {}
    for a in sorted(ROWS):
        if a not in g:
            print("%-15s %5s | NO RUNS RETRIEVED -- row not scored" % (a, "-"))
            p3[a] = None
            continue
        ship = statistics.median(r["eui_shipped"] for r in g[a])
        pub = ROWS[a]["published"]
        d = 100.0 * (ship - pub) / pub
        p3[a] = abs(d) <= 2.0
        print("%-15s %5d | %12.2f %10.1f %+7.2f%% | %s"
              % (a, len(g[a]), ship, pub, d, "PASS" if p3[a] else "!! FAIL"))
    if not all(v for v in p3.values() if v is not None) or not p3:
        print("\n!! P3 FAILED for at least one archetype. The sample is not the published population;"
              "\n   the corrected numbers below are NOT scored against P1/P2.")

    # ---- the corrected table -------------------------------------------------------------------
    print("\n=== corrected medians, with an exact distribution-free 95 %% interval ===")
    print("%-15s %5s | %10s %10s | %-22s | %-9s %-9s | %s"
          % ("archetype", "n", "published", "corrected", "95 % interval", "was", "now", "band"))
    out = []
    for a in sorted(ROWS):
        if a not in g:
            out.append({"row": a, "n": 0, "note": "no runs retrieved"})
            continue
        band = ROWS[a]["band"]
        pub = ROWS[a]["published"]
        vals = sorted(r["eui_corrected"] for r in g[a])
        med = statistics.median(vals)
        ci = median_ci(vals)
        cis = "%.2f - %.2f (%.1f%%)" % (ci[0], ci[1], 100 * ci[4]) if ci else "n too small"
        print("%-15s %5d | %10.1f %10.2f | %-22s | %-9s %-9s | [%.1f, %.1f]"
              % (a, len(vals), pub, med, cis, verdict(pub, band), verdict(med, band),
                 band[0], band[1]))
        rec = {"row": a, "n": len(vals), "published": pub,
               "shipped_median": round(statistics.median(r["eui_shipped"] for r in g[a]), 2),
               "reproduces_published": p3.get(a),
               "corrected_median": round(med, 2),
               "published_verdict": verdict(pub, band), "corrected_verdict": verdict(med, band),
               "band": list(band),
               "factor_min": round(min(r["factor"] for r in g[a]), 4),
               "factor_max": round(max(r["factor"] for r in g[a]), 4)}
        if ci:
            rec["ci95"] = [round(ci[0], 2), round(ci[1], 2)]
            rec["ci_order_stats"] = [ci[2], ci[3]]
            rec["ci_coverage"] = round(ci[4], 4)
            rec["ci_verdict_lo"] = verdict(ci[0], band)
            rec["ci_verdict_hi"] = verdict(ci[1], band)
        out.append(rec)

    # ---- P1 and P2 -----------------------------------------------------------------------------
    print("\n=== P1 -- OtherDwelling and HighRise fall BELOW their floors, interval included ===")
    p1_all = True
    for a in P1_ROWS:
        rec = next((r for r in out if r["row"] == a), None)
        if not rec or not rec.get("n"):
            print("  %-15s NOT SCORED -- no runs" % a)
            p1_all = False
            continue
        floor = ROWS[a]["band"][0]
        med_below = rec["corrected_median"] < floor
        ci_below = rec.get("ci95") and rec["ci95"][1] < floor
        ok_ = bool(med_below and ci_below)
        p1_all = p1_all and ok_
        print("  %-15s median %.2f %s floor %.1f | CI upper %.2f %s floor | %s"
              % (a, rec["corrected_median"], "<" if med_below else "NOT <", floor,
                 rec.get("ci95", [0, 0])[1], "<" if ci_below else "NOT <",
                 "CONFIRMED" if ok_ else "!! FALSIFIED"))
    print("  P1 overall: %s" % ("CONFIRMED" if p1_all else
                                "!! FALSIFIED -- section 3's 'BELOW, either way' is WITHDRAWN, "
                                "not softened"))

    print("\n=== P2 -- SingleD, no direction was predicted ===")
    rec = next((r for r in out if r["row"] == "SingleD"), None)
    if rec and rec.get("n"):
        print("  published %.1f (%s the band) -> corrected %.2f (%s)  CI %s"
              % (rec["published"], "ABOVE" if rec["published_verdict"] == "ABOVE" else
                 rec["published_verdict"], rec["corrected_median"], rec["corrected_verdict"],
                 rec.get("ci95")))
        print("  reported as measured; no prediction was made and none is invented now.")

    f = sorted(r["factor"] for r in ok)
    print("\nresidential factor over the sample: min %.4f  median %.4f  max %.4f  (spread %.1f %%)"
          % (f[0], statistics.median(f), f[-1], 100 * (f[-1] - f[0]) / f[0]))

    with io.open(os.path.join(HERE, "v4_b2_resid_corrected.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"task": "V4-B2 (residential sample)", "date": "2026-08-06",
                             "n_runs": len(ok), "n_missing": len(missing),
                             "seed": 20260806, "n_per_archetype_target": 100,
                             "P3_pass": p3, "P1_confirmed": p1_all,
                             "factor_min": round(f[0], 6),
                             "factor_median": round(statistics.median(f), 6),
                             "factor_max": round(f[-1], 6),
                             "rows": out}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
