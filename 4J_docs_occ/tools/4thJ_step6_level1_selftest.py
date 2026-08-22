# -*- coding: utf-8 -*-
"""Unit tests for `4thJ_step6_level1.py`.

Every rejection branch is exercised rather than asserted, and the three
non-obvious crosswalk rules each have a test that FAILS if the rule is reverted:

  * `910` in `AC9A`, not `AC1_TR`
  * `995`-`999` in `AC99NSP`, not `AC9A`
  * `998` in `AC4-8`, not `AC99NSP`

plus the arithmetic identity that established the first one -- `AC9A`'s children
sum to its published parent in ES and IT and do NOT in the UK.
"""

import importlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
L1 = importlib.import_module("4thJ_step6_level1")

EURO = os.path.join(_HERE, "..", "Step6_docs", "outputs_step6", "eurostat_raw")

ok = fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print("  ok    %s" % name)
    else:
        fail += 1
        print("  FAIL  %s   %s" % (name, detail))


def rec(*pairs):
    """(duration, act) pairs -> a decoded-record-shaped dict."""
    return {"prefix": {}, "episodes": [{"duration_min": d, "act": a} for d, a in pairs]}


print("--- aggregate_of: the three non-obvious rules ---")
check("910 -> AC9A (NOT AC1_TR)", L1.aggregate_of("910") == "AC9A", L1.aggregate_of("910"))
check("111 -> AC1_TR", L1.aggregate_of("111") == "AC1_TR")
for c in ("995", "996", "997", "999"):
    check("%s -> AC99NSP (NOT AC9A)" % c, L1.aggregate_of(c) == "AC99NSP", L1.aggregate_of(c))
check("998 -> AC4-8 (NOT AC99NSP)", L1.aggregate_of("998") == "AC4-8", L1.aggregate_of("998"))
check("011 -> AC0", L1.aggregate_of("011") == "AC0")
check("212 -> AC2", L1.aggregate_of("212") == "AC2")
check("321 -> AC3", L1.aggregate_of("321") == "AC3")
for c, want in (("411", "AC4-8"), ("512", "AC4-8"), ("611", "AC4-8"),
                ("733", "AC4-8"), ("812", "AC4-8")):
    check("%s -> %s" % (c, want), L1.aggregate_of(c) == want)
check("000 -> null_000", L1.aggregate_of("000") == "null_000")
check("None -> null_000", L1.aggregate_of(None) == "null_000")

print("--- aggregate_of: refusals ---")
for bad in ("99", "1234", "abc", "9a9"):
    try:
        L1.aggregate_of(bad)
        check("refuses %r" % bad, False, "accepted it")
    except L1.Level1Error:
        check("refuses %r" % bad, True)

print("--- budget ---")
b = L1.budget([rec((480, "011"), (480, "111"), (480, "910"))])
check("one diary splits 480/480/480", abs(b["AC0"] - 480) < 1e-9 and
      abs(b["AC1_TR"] - 480) < 1e-9 and abs(b["AC9A"] - 480) < 1e-9,
      {k: b[k] for k in L1.AGGREGATES})
check("budget sums to 1440",
      abs(sum(b[k] for k in L1.AGGREGATES + L1.EXTRA) - 1440) < 1e-9)

b2 = L1.budget([rec((1440, "011")), rec((1440, "111"))], weights=[3.0, 1.0])
check("weights are honoured (3:1 -> 1080/360)",
      abs(b2["AC0"] - 1080) < 1e-9 and abs(b2["AC1_TR"] - 360) < 1e-9,
      (b2["AC0"], b2["AC1_TR"]))

try:
    L1.budget([rec((1430, "011"))])
    check("refuses a 1430-minute day", False, "accepted it")
except L1.Level1Error:
    check("refuses a 1430-minute day", True)

try:
    L1.budget([rec((1440, "011"))], weights=[float("nan")])
    check("refuses a NaN weight", False, "accepted it")
except L1.Level1Error:
    check("refuses a NaN weight", True)

try:
    L1.budget([])
    check("refuses an empty batch (V6.b)", False, "accepted it")
except L1.Level1Error:
    check("refuses an empty batch (V6.b)", True)

print("--- published: the AC9A parent-versus-children identity ---")
if not os.path.isdir(EURO):
    print("  SKIP  no eurostat_raw at %s" % EURO)
else:
    for c, expect_hole in (("ES", False), ("IT", False), ("UK", True)):
        p = L1.published(EURO, c)
        d = p["_ac9a_parent_minus_children"]
        check("%s AC9A parent-children = %+d %s"
              % (c, d, "(the published hole)" if expect_hole else "(clean)"),
              (abs(d) > 10) == expect_hole, d)
        check("%s AC9A used is the CHILDREN sum" % c,
              abs(p["AC9A"] - (p["_ac9a_parent"] - d)) < 1e-9)
        check("%s six aggregates are all published" % c,
              all(p[a] is not None for a in L1.AGGREGATES))
    for band in L1.SCOREABLE_BANDS:
        p = L1.published(EURO, "ES", age=band)
        check("ES %s is readable" % band, p["AC0"] is not None)
    try:
        L1.published(EURO, "ES", age="Y65-74")
        check("Y65-74 is absent (FINDING 55) -> refused", False, "it returned data")
    except L1.Level1Error:
        check("Y65-74 is absent (FINDING 55) -> refused", True)

    print("--- gate_g6_4 ---")
    pub = L1.published(EURO, "ES", age="Y25-44")
    perfect = dict((a, pub[a]) for a in L1.AGGREGATES)
    r = L1.gate_g6_4(perfect, pub, "Y25-44")
    check("a perfect budget PASSes with MAPE 0", r["passes"] and r["mape"] == 0.0, r["mape"])

    bad = dict(perfect)
    bad["AC0"] = perfect["AC0"] * 2.0
    r = L1.gate_g6_4(bad, pub, "Y25-44")
    check("doubling AC0 FAILs the gate", not r["passes"], r["mape"])

    # 🔴 The zero-cell branch. NO level-1 published cell is zero -- the smallest is
    # one minute -- so it is exercised on a synthetic table rather than pretended
    # into existence by calling 11 minutes "approximately zero", which is what the
    # first version of this rule did and which failed the real corpus.
    pub65 = L1.published(EURO, "ES", age="Y_GE65")
    p65 = dict((a, pub65[a]) for a in L1.AGGREGATES)
    r = L1.gate_g6_4(p65, pub65, "Y_GE65")
    check("no level-1 published cell is a zero cell", r["n_zero_cells"] == 0, r["n_zero_cells"])

    # 🔴 `D-S6-12` item 1, ruled 2026-08-22. This band USED to score all six on APE
    # and that is precisely `FINDING 90`: two of its published cells are 1-5 min/day
    # (Eurostat correctly publishes ~1 min/day of employment for the over-65s), and
    # those two carried all three of `G6.4`'s reported held-out MAPEs. Under the floor
    # they move to an absolute test and the percentage is taken over the four cells on
    # which a percentage is identifiable.
    check("Y_GE65 no longer scores all six on APE -- two cells are below the floor",
          r["n_scored"] == 4 and r["n_floor_cells"] == 2,
          (r["n_scored"], r["n_floor_cells"]))
    check("a perfect budget still PASSes on a band with floor cells",
          r["passes"] and r["mape"] == 0.0, (r["passes"], r["mape"]))
    small = sorted(r["floor_cells"], key=lambda z: z["published"])[0]["aggregate"]
    check("the smallest floor cell is below the pre-registered floor",
          pub65[small] < L1.PUBLISHED_FLOOR_MIN, (small, pub65[small]))

    # A floor cell inside the tolerance is a HIT and does NOT move the MAPE.
    m = dict(p65); m[small] = p65[small] + 14.0         # < 15.0 min/day -> a HIT
    r2 = L1.gate_g6_4(m, pub65, "Y_GE65")
    check("floor-cell +14 min = HIT, gate PASSes", r2["passes"], r2["reasons"])
    check("a floor cell does not move the MAPE", r2["mape"] == r["mape"],
          (r2["mape"], r["mape"]))
    # 🔴 The regression `FINDING 90` names: 14 minutes onto a 1-minute published cell
    # is a 1400 % APE. On the old basis that ALONE dragged the band's MAPE over 200 %
    # and made it the reported worst band. It must now be a pass at MAPE 0.
    check("the FINDING 90 artefact is gone: +14 min on a ~1 min cell no longer "
          "inflates the band's MAPE", r2["mape"] < 1.0, r2["mape"])

    # ... and outside the tolerance it is a MISS, with the MAPE still unmoved: the
    # cell is caught, and it is caught in minutes rather than in a percentage.
    m[small] = p65[small] + 40.0                        # > 15.0 min/day -> a MISS
    r3 = L1.gate_g6_4(m, pub65, "Y_GE65")
    check("floor-cell +40 min = MISS, gate FAILs", not r3["passes"], r3["reasons"])
    check("the MISS is reported in min/day, not as a percentage",
          any("min/day tolerance" in s for s in r3["reasons"]), r3["reasons"])
    check("a floor-cell MISS still does not move the MAPE", r3["mape"] == r["mape"],
          (r3["mape"], r["mape"]))

    synth = dict(pub65); synth["AC2"] = 0.0; synth["_source"] = "synthetic zero cell"
    m = dict(p65); m["AC2"] = 3.0                       # 0.21 % of the day -> a HIT
    r = L1.gate_g6_4(m, synth, "Y_GE65")
    check("published 0 + model 3 min = zero-cell HIT, gate PASSes",
          r["passes"] and r["n_zero_cells"] == 1, (r["passes"], r["reasons"]))
    m["AC2"] = 100.0                                    # 6.9 % of the day -> a MISS
    r = L1.gate_g6_4(m, synth, "Y_GE65")
    check("published 0 + model 100 min = zero-cell MISS, gate FAILs",
          not r["passes"], r["reasons"])

    print("--- mae ---")
    check("mae of a perfect budget is 0", L1.mae(perfect, pub) == 0.0)
    shifted = dict(perfect)
    shifted["AC3"] = perfect["AC3"] + 60.0
    check("a 60-minute shift in one of six gives mae 10",
          abs(L1.mae(shifted, pub) - 10.0) < 1e-9, L1.mae(shifted, pub))

print("\n%d ok, %d FAILED" % (ok, fail))
sys.exit(1 if fail else 0)
