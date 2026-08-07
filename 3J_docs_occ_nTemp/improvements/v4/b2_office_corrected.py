# -*- coding: utf-8 -*-
"""V4-B2, second half -- the CORRECTED Leg-2 office EUI, on all 252 published runs.

UNBLOCKED 2026-08-06 by the user's amendment to the Speed rule: *"tu peux obtenir ce que choses tu
veux sur le speed, mais tu ne peux pas utiliser pour des simulations."* Retrieval is permitted;
running anything on the cluster is not. Every `eplusout.sql` behind the four published office rows
was copied off Speed with `scp`, read with sqlite3 ON THIS MACHINE, and deleted before the next --
peak local disk one file. **No sbatch, no srun, no python on the login node, no simulation.**

Input: `v4_b2_office_factors.jsonl`, one record per published run, produced by the retrieval loop.
Per run it carries the shipped (contaminated) EUI, the corrected EUI with `ReportName` pinned to
`AnnualBuildingUtilityPerformanceSummary`, and their ratio.

This script does the arithmetic Step 9 does -- `build_eui()` takes the MEDIAN of `eui_kWh_m2` over
the office rows, once for `all` and once per subtype (Leg2_2-split/Step9_docs/
3rdJ_09_activityDrivenLoads_2split.py:140-156) -- and does it twice: on the shipped column, which
must reproduce the published numbers, and on the corrected one.

🔴 The first median is the check that matters. If the shipped medians do not come back as
172.7 / 172.6 / 172.5 / 172.7, this is not the same population as the published table and nothing
below it means anything.
"""
import io
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "v4_b2_office_factors.jsonl")

# Band and published values come from LEG-2's OWN artefacts, not from V4-B2_defect_reach.md --
# copying them out of my own write-up would be a consistency check whose two inputs share an
# ancestor, and could not catch a value that is wrong in both. Verified 2026-08-06 against:
#   band       Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:50
#              OFFICE_EUI_BAND = (135.0, 100.0, 200.0)  -> (central, lo, hi)
#   published  Leg2_2-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv rows 6-9,  # FROZEN-INPUT-OK: LEG-2 path -- the freeze registry covers Leg3_4-split only, so this directory has no frozen counterpart and is not superseded; this is a provenance comment, not a read
#              which also carry n = 252 / 84 / 84 / 84 -- the counts this retrieval independently hit.
BAND = (100.0, 200.0)
PUBLISHED = {"all": 172.7, "Office_Knowledge": 172.6,
             "Office_Public": 172.5, "Office_Sales": 172.7}
LABEL = {"all": "office all", "Office_Knowledge": "office Knowledge",
         "Office_Public": "office Public", "Office_Sales": "office Sales"}


def verdict(x):
    return "IN" if BAND[0] <= x <= BAND[1] else ("BELOW" if x < BAND[0] else "ABOVE")


def main():
    with io.open(SRC, encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    ok = [r for r in rows if not r.get("error") and r.get("factor")]
    got = {r["run_dir"] for r in ok}
    # The log is append-only, so a run that failed once and succeeded on the retry has BOTH records.
    # A failure that was later retrieved is a retry, not a hole -- only a run with no successful
    # record anywhere is genuinely missing, and that is what must be reported as missing.
    retried = [r for r in rows if r.get("error") and r["run_dir"] in got]
    bad = [r for r in rows if (r.get("error") or not r.get("factor")) and r["run_dir"] not in got]
    print("runs retrieved: %d   retried after a failed fetch: %d   still missing: %d"
          % (len(ok), len(retried), len(bad)))
    for r in bad:
        print("   !! %s %s -- %s" % (r["cell"], r["scenario"], r.get("error")))

    groups = {"all": ok}
    for r in ok:
        groups.setdefault(r["arch"], []).append(r)

    f = sorted(r["factor"] for r in ok)
    print("\nfactor over the %d published office runs: min %.4f  median %.4f  max %.4f"
          % (len(f), f[0], statistics.median(f), f[-1]))
    print("spread %.2f %% of the minimum -- UNIFORM? %s"
          % (100 * (f[-1] - f[0]) / f[0],
             "yes" if (f[-1] - f[0]) / f[0] < 0.005 else "NO, a single divisor is invalid"))

    print("\n%-18s %5s | %9s %9s %6s | %10s %8s | %s"
          % ("published row", "n", "shipped", "published", "match", "corrected", "verdict", "was"))
    out = []
    for key in ("all", "Office_Knowledge", "Office_Public", "Office_Sales"):
        g = groups.get(key)
        if not g:                        # a partial retrieval must say so, not crash or round down
            print("%-18s %5s | %s" % (LABEL[key], "-", "NO RUNS RETRIEVED -- row not computed"))
            out.append({"row": LABEL[key], "n": 0, "note": "no runs retrieved"})
            continue
        ship = statistics.median(r["eui_shipped"] for r in g)
        corr = statistics.median(r["eui_corrected"] for r in g)
        pub = PUBLISHED[key]
        agree = abs(round(ship, 1) - pub) <= 0.05
        print("%-18s %5d | %9.2f %9.1f %6s | %10.2f %8s | %s"
              % (LABEL[key], len(g), ship, pub, "OK" if agree else "MISMATCH",
                 corr, verdict(corr), verdict(pub)))
        out.append({"row": LABEL[key], "n": len(g),
                    "shipped_median": round(ship, 2), "published": pub,
                    "reproduces_published": bool(agree),
                    "corrected_median": round(corr, 2),
                    "published_verdict": verdict(pub), "corrected_verdict": verdict(corr),
                    "band": list(BAND)})

    # how far under the floor, and how many single runs cross it
    corr_all = sorted(r["eui_corrected"] for r in ok)
    below = sum(1 for v in corr_all if v < BAND[0])
    print("\ncorrected per-run range: %.2f - %.2f   (%d of %d runs below the %.0f floor, %.1f %%)"
          % (corr_all[0], corr_all[-1], below, len(corr_all), BAND[0],
             100.0 * below / len(corr_all)))

    with io.open(os.path.join(HERE, "v4_b2_office_corrected.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"task": "V4-B2 (corrected half)", "date": "2026-08-06",
                             "n_runs": len(ok), "n_retried": len(retried),
                             "n_missing": len(bad), "band": list(BAND),
                             "factor_min": round(f[0], 6),
                             "factor_median": round(statistics.median(f), 6),
                             "factor_max": round(f[-1], 6),
                             "corrected_run_range": [round(corr_all[0], 2), round(corr_all[-1], 2)],
                             "runs_below_floor": below,
                             "rows": out}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
