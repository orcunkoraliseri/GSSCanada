# -*- coding: utf-8 -*-
"""V4-B2, residential -- the SECOND defect, and what the published rows do when BOTH are corrected.

WHY THIS EXISTS, and it is not a re-run of `b2_resid_corrected.py`.

`b2_resid_corrected.py` scored the three pre-registered predictions against ONE definition of
"corrected": pin `ReportName` to the annual-energy report. That is the defect `V4-B2_defect_reach.md`
named, and P1/P2/P3 were scored against it and are NOT rescored here. P1 came out FALSIFIED.

Chasing WHY it was falsified turned up a second defect in the same function, and the two are
complementary -- each unit system triggers exactly one of them:

  defect 1  `ReportName` is never filtered, so the peak-demand copy of `End Uses By Subcategory`
            is summed with the annual one. In SI output the demand units are `W`; in IP output they
            are `kBtuh`, numerically ~1/1000 of the annual `kBtu` figure. **Large in SI, invisible
            in IP.**
  defect 2  the water guard is `if 'm3' in str(units): continue` -- an SI-only guard. In IP output
            the water rows are `gal` and `gal/min`, which pass the guard, hit the
            `else: val_kwh = val` branch, and are summed as kilowatt-hours. **Large in IP, absent
            in SI.** (`plotting.py:319` and `:342`.)

So a correction that fixes only defect 1 leaves the IP archetypes almost untouched -- which is
exactly what the first pass measured, and exactly why P1 failed on `OtherDwelling`.

🔴 This does NOT retroactively confirm P1. P1 was scored against the correction that existed when it
was written, and it failed. What follows is a SEPARATE, post-hoc measurement, labelled as post-hoc,
of what the rows do when both defects are corrected.

Input: `v4_b2_resid_units.jsonl` -- the (ReportName, Units) decomposition per run, so every variant
below is arithmetic on a stored record rather than another retrieval.
"""
import io
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "v4_b2_resid_units.jsonl")

ANNUAL = "AnnualBuildingUtilityPerformanceSummary"

# The shipped conversion table, reproduced exactly (plotting.py:328-345).
ENERGY = {"GJ": 277.778, "kWh": 1.0, "J": 1.0 / 3600000.0,
          "kBtu": 0.293071, "Btu": 0.000293071, "MJ": 0.277778}
# Units that are NOT energy and must never enter an energy sum, whatever the unit system.
VOLUME = {"m3", "m3/s", "gal", "gal/min", "ft3", "ft3/min", "L", "L/s"}
# POWER is not energy either. `W` and `kBtuh` are the units the peak-demand report writes in, and
# summing them into an annual total IS defect 1. They are named here rather than left to fall into
# the unknown branch: in THIS sample they appear only under DemandEndUseComponentsSummary, so pinning
# ReportName already excludes them -- but that is a property of the sample, checked below, not a
# property of the code. An unknown unit silently assumed harmless is how both defects happened.
POWER = {"W", "kW", "kBtuh", "Btu/h", "W/m2", "ton"}

# Bands and published values from LEG-2's OWN artefacts, not from my write-ups:
#   bands      Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:43-46
#   published  Leg2_2-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv rows 2-5  # FROZEN-INPUT-OK: LEG-2 path -- the freeze registry covers Leg3_4-split only, so this directory has no frozen counterpart and is not superseded; this is a provenance comment, not a read
ROWS = {
    "SingleD":       {"published": 211.7, "band": (130.6, 186.1)},
    "OtherDwelling": {"published": 140.0, "band": (136.1, 186.1)},
    "MidRise":       {"published": 177.5, "band": (111.1, 216.7)},
    "HighRise":      {"published": 143.0, "band": (113.9, 147.2)},
}


def verdict(x, band):
    return "IN" if band[0] <= x <= band[1] else ("BELOW" if x < band[0] else "ABOVE")


def median_ci(sorted_vals, conf=0.95):
    """Exact distribution-free CI for the median from order statistics (see b2_resid_corrected.py)."""
    from math import comb
    n = len(sorted_vals)
    if n < 6:
        return None
    tot, cum, k = 2.0 ** n, 0.0, 0
    while True:
        nxt = cum + comb(n, k) / tot
        if nxt > (1.0 - conf) / 2.0:
            break
        cum, k = nxt, k + 1
    if k == 0:
        return None
    return sorted_vals[k - 1], sorted_vals[n - k], k, n - k + 1, 1.0 - 2.0 * cum


def totals(parts):
    """Three sums per run, from the stored decomposition.

    shipped : reproduces calculate_eui() exactly -- every report, skip only units containing 'm3',
              unknown units passed through as kWh.
    corr1   : defect 1 only -- pin ReportName, otherwise identical to shipped.
    corr2   : both defects -- pin ReportName AND drop every volume/flow unit, whatever it is called.
    """
    shipped = corr1 = corr2 = 0.0
    unclassified = []
    for p in parts:
        u, s, rep = p["units"], p["sum"] or 0.0, p["report"]
        if u in ENERGY:
            kwh = s * ENERGY[u]
            shipped += kwh
            if rep == ANNUAL:
                corr1 += kwh
                corr2 += kwh
        elif u in VOLUME:
            if "m3" not in u:            # the shipped guard only catches m3; gal slips through
                shipped += s
                if rep == ANNUAL:
                    corr1 += s
            # corr2 never adds a volume
        elif u in POWER:
            # The shipped code has no power branch at all, so a watt is added as a kilowatt-hour.
            shipped += s
            if rep == ANNUAL:            # never true in this sample -- asserted, not assumed
                corr1 += s
        else:
            # An unknown unit is not silently assumed to be anything. It is reported, and if it
            # carries energy the caller must classify it before any corrected number is quoted.
            unclassified.append((rep, u, s))
            shipped += s
            if rep == ANNUAL:
                corr1 += s
                corr2 += s
    return shipped, corr1, corr2, unclassified


def main():
    with io.open(SRC, encoding="utf-8") as fh:
        recs = [json.loads(l) for l in fh if l.strip()]
    ok = list({r["run_dir"]: r for r in recs if not r.get("error")}.values())
    print("runs with a unit decomposition: %d" % len(ok))

    # ---- unit inventory, printed before any total is read --------------------------------------
    inv = {}
    for r in ok:
        for p in r["parts"]:
            inv.setdefault((p["report"], p["units"]), 0)
            inv[(p["report"], p["units"])] += 1
    print("\n=== every (report, unit) pair present in the sample ===")
    for (rep, u), n in sorted(inv.items()):
        kind = ("energy" if u in ENERGY else "volume/flow" if u in VOLUME
                else "power (NOT energy)" if u in POWER else "!! UNCLASSIFIED")
        print("  %-38s %-8s runs=%4d  %s" % (rep, u, n, kind))
    unk = [k for k in inv if k[1] not in ENERGY and k[1] not in VOLUME and k[1] not in POWER]
    if unk:
        print("\n!! %d unit(s) are unclassified. No corrected number below is trustworthy until "
              "they are classified." % len(unk))
    else:
        print("\n  every unit is classified; no total below rests on an unknown unit.")

    # The claim "pinning ReportName already removes every power row" is a property of THIS sample.
    # It is checked, not assumed -- if a future sample writes W under the annual report, defect 1's
    # correction stops being sufficient and this line says so instead of silently under-correcting.
    pw_annual = [k for k in inv if k[0] == ANNUAL and k[1] in POWER]
    print("  power units under %s: %s" % (ANNUAL, pw_annual or "none -- pinning ReportName suffices"))
    en_demand = [k for k in inv if k[0] != ANNUAL and k[1] in ENERGY]
    print("  energy units outside the annual report: %s"
          % (en_demand or "none -- no real energy is discarded by pinning ReportName"))

    g = {}
    for r in ok:
        g.setdefault(r["arch"], []).append(r)

    per = {}
    unclass_total = 0
    for a, rs in g.items():
        rows = []
        for r in rs:
            sh, c1, c2, un = totals(r["parts"])
            unclass_total += len(un)
            ar = r["area_m2"]
            if not ar:
                continue
            rows.append((sh / ar, c1 / ar, c2 / ar))
        per[a] = rows

    print("\n=== the two defects, separated (post-hoc; P1/P2/P3 are NOT rescored here) ===")
    print("%-15s %5s | %9s %9s | %9s %-7s | %9s %-7s | %s"
          % ("archetype", "n", "published", "shipped", "defect 1", "->", "both", "->", "band"))
    out = []
    for a in sorted(ROWS):
        rows = per.get(a) or []
        if not rows:
            print("%-15s %5s | NO RUNS -- row not computed" % (a, "-"))
            continue
        band, pub = ROWS[a]["band"], ROWS[a]["published"]
        sh = statistics.median(x[0] for x in rows)
        c1 = statistics.median(x[1] for x in rows)
        c2 = statistics.median(x[2] for x in rows)
        ci2 = median_ci(sorted(x[2] for x in rows))
        print("%-15s %5d | %9.1f %9.2f | %9.2f %-7s | %9.2f %-7s | [%.1f, %.1f]"
              % (a, len(rows), pub, sh, c1, verdict(c1, band), c2, verdict(c2, band),
                 band[0], band[1]))
        rec = {"row": a, "n": len(rows), "published": pub, "band": list(band),
               "shipped_median": round(sh, 2),
               "reproduces_published": abs(round(sh, 1) - pub) / pub <= 0.02,
               "corrected_defect1_only": round(c1, 2),
               "corrected_both_defects": round(c2, 2),
               "published_verdict": verdict(pub, band),
               "verdict_defect1_only": verdict(c1, band),
               "verdict_both_defects": verdict(c2, band),
               "water_share_of_defect1_total": round(100.0 * (c1 - c2) / c1, 2)}
        if ci2:
            rec["ci95_both_defects"] = [round(ci2[0], 2), round(ci2[1], 2)]
            rec["ci95_verdicts"] = [verdict(ci2[0], band), verdict(ci2[1], band)]
        out.append(rec)

    print("\n=== how much of each published row is water volume added as energy (defect 2) ===")
    for r in out:
        print("  %-15s %6.2f %% of the defect-1-corrected total"
              % (r["row"], r["water_share_of_defect1_total"]))

    print("\n=== verdict movement, published -> both defects corrected ===")
    for r in out:
        moved = r["published_verdict"] != r["verdict_both_defects"]
        print("  %-15s %-6s -> %-6s  %s  CI %s -> %s"
              % (r["row"], r["published_verdict"], r["verdict_both_defects"],
                 "MOVES" if moved else "same",
                 r.get("ci95_both_defects"), r.get("ci95_verdicts")))

    with io.open(os.path.join(HERE, "v4_b2_resid_two_defects.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"task": "V4-B2 residential, both defects", "date": "2026-08-06",
                             "n_runs": len(ok), "seed": 20260806,
                             "unclassified_units": sorted("%s / %s" % k for k in unk),
                             "post_hoc": True,
                             "note": "P1/P2/P3 were scored in b2_resid_corrected.py against the "
                                     "defect-1-only correction and are not rescored here",
                             "rows": out}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
