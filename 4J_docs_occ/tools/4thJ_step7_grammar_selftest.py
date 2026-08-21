#!/usr/bin/env python
"""Self-test for `4thJ_step7_grammar.py`.

🔴 Every rejection branch below is EXERCISED, not asserted. A recogniser whose
reject paths were never taken is a recogniser that accepts everything, and it
would look identical in a summary line. This is the same discipline the gate
batteries use: each check is seen firing on a case built to fire it.

Runs locally. No cluster, no model, no corpus file. Pure string cases.
"""

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = importlib.import_module("4thJ_step7_grammar")

STEP2 = os.path.join(os.path.dirname(HERE), "Step2_docs", "outputs_step2")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


PREFIX = "es,35-44,female,couple_with_children,employed,monday"


def rec(episodes):
    return PREFIX + "|" + episodes + "<eor>"


def ep(dur, act="011", act2="", loc="at_home", cop="0"):
    return "%s,%s,%s,%s,%s;" % (dur, act, act2, loc, cop)


def main():
    print("\n== 1. alphabets, read live from the shipped Step 2 crosswalks ==")
    A = G.build_alphabets(STEP2)
    check("158 shipped ACT codes", A["act_n_shipped"] == 158, str(A["act_n_shipped"]))
    check("000 admitted -> 159 total (FINDING 43)", len(A["act"]) == 159, str(len(A["act"])))
    check("000 is in the alphabet", "000" in A["act"])
    check("43 ACT2 codes", len(A["act2"]) == 43, str(len(A["act2"])))
    check("5 LOC classes", len(A["loc"]) == 5)
    check("COP 0..64 = 65 values", len(A["cop"]) == 65)
    check("4 outdoor-at-home codes, all inside ACT",
          sorted(A["outdoor_at_home"]) == ["322", "341", "342", "344"])

    print("\n== 2. the 145-state tally automaton ==")
    M = G.tally_automaton()
    check("145 states", len(M["states"]) == 145, str(len(M["states"])))
    check("exactly one accepting state", M["accepting"] == {144})
    check("start is 0", M["start"] == 0)
    check("delta is finite and complete", len(M["delta"]) == 144 * 145 // 2, str(len(M["delta"])))
    check("tally_step rejects 15 min (not a multiple of 10)", G.tally_step(0, 15) is None)
    check("tally_step rejects 0", G.tally_step(0, 0) is None)
    check("tally_step rejects overshoot", G.tally_step(140, 100) is None)
    check("tally_step accepts a full day in one episode", G.tally_step(0, 1440) == 144)

    print("\n== 3. a well-formed record is ACCEPTED ==")
    good = rec(ep("600") + ep("240", act="111", loc="other_place")
               + ep("60", act="960", loc="private_transport")
               + ep("540", act="011"))
    ok, why = G.validate_record(good, A, G.TransitionPolicy.PERMISSIVE)
    check("baseline record accepted", ok, why)

    print("\n== 4. every rejection branch, SEEN FIRING ==")
    cases = [
        ("whitespace anywhere (V3.c)", rec(ep("1440")).replace("|", " |"), "whitespace"),
        ("missing <eor>", rec(ep("1440"))[:-5], "<eor>"),
        ("no prefix/body separator", PREFIX + ep("1440") + "<eor>", "separating"),
        ("prefix has 5 fields", "es,35-44,female,employed,monday|" + ep("1440") + "<eor>", "prefix has"),
        ("prefix has 7 fields", PREFIX + ",summer|" + ep("1440") + "<eor>", "prefix has"),
        ("empty prefix field", "es,,female,couple_with_children,employed,monday|" + ep("1440") + "<eor>", "empty field"),
        ("zero episodes", PREFIX + "|<eor>", "zero episodes"),
        ("missing terminal semicolon", rec(ep("1440"))[:-6] + "<eor>", "terminal"),
        ("episode with 4 fields", rec("1440,011,at_home,0;"), "fields, expected 5"),
        ("episode with 6 fields", rec("1440,011,,at_home,0,9;"), "fields, expected 5"),
        ("duration not a multiple of 10", rec(ep("725") + ep("715")), "multiple"),
        ("duration with a leading zero", rec("0600,011,,at_home,0;" + ep("840")), "leading-zero-free"),
        ("durations sum to 1430", rec(ep("1430")), "sum to 1430"),
        ("durations sum to 1450", rec(ep("1450")), "passed 1440"),
        ("ACT not in the alphabet", rec(ep("1440", act="120")), "ACT"),
        ("ACT2 not in the alphabet", rec(ep("1440", act2="10")), "ACT2"),
        ("LOC not in the alphabet", rec(ep("1440", loc="at_work")), "LOC"),
        ("COP above 64", rec(ep("1440", cop="65")), "outside"),
        ("COP with a leading zero", rec(ep("1440", cop="00")), "leading-zero-free"),
        ("not a string", 12345, "not a string"),
    ]
    for name, text, expect in cases:
        ok, why = G.validate_record(text, A, G.TransitionPolicy.PERMISSIVE)
        check(name, (not ok) and (expect in why), why or "ACCEPTED -- branch never fired")

    print("\n== 5. 000 is accepted, because the corpus contains it (FINDING 43) ==")
    ok, why = G.validate_record(rec(ep("1440", act="000")), A, G.TransitionPolicy.PERMISSIVE)
    check("a 000 episode is accepted", ok, why)

    print("\n== 6. FINDING 45 / D-S7-2: the transition policy ==")
    try:
        G.validate_record(good, A, "whatever")
        check("unknown policy raises", False, "did not raise")
    except G.GrammarError as e:
        check("unknown policy raises", True, str(e)[:60])
    try:
        G.validate_record(good, A, G.TransitionPolicy.REQUIRE_TRAVEL)
        check("REQUIRE_TRAVEL refuses without acknowledgement", False, "did not raise")
    except G.GrammarError as e:
        check("REQUIRE_TRAVEL refuses without acknowledgement", True, str(e)[:70])

    # The pattern measured in 28.95 % of real diaries: other_place -> at_home,
    # no travel episode in between.
    direct = rec(ep("600") + ep("300", act="111", loc="other_place") + ep("540"))
    ok_p, _ = G.validate_record(direct, A, G.TransitionPolicy.PERMISSIVE)
    ok_r, why_r = G.validate_record(direct, A, G.TransitionPolicy.REQUIRE_TRAVEL,
                                    acknowledge_finding_45=True)
    check("corpus-shaped direct transition ACCEPTED under PERMISSIVE", ok_p)
    check("same record REJECTED under REQUIRE_TRAVEL", (not ok_r) and "direct other_place" in why_r,
          why_r)

    travelled = rec(ep("600") + ep("290", act="111", loc="other_place")
                    + ep("10", act="960", loc="public_transport") + ep("540"))
    ok_t, why_t = G.validate_record(travelled, A, G.TransitionPolicy.REQUIRE_TRAVEL,
                                    acknowledge_finding_45=True)
    check("with an intervening travel episode it is accepted", ok_t, why_t)

    print("\n== 7. the measured FINDING 45 rates carried in the module ==")
    for k in ("all", "es", "uk", "it"):
        n, d = G.FINDING_45_MEASURED[k]
        print("     %-4s %6d / %6d = %5.2f %%" % (k, n, d, 100.0 * n / d))
    check("counts sum: es+uk+it == all",
          sum(G.FINDING_45_MEASURED[c][0] for c in ("es", "uk", "it")) == G.FINDING_45_MEASURED["all"][0])
    check("denominators sum to 73,254",
          sum(G.FINDING_45_MEASURED[c][1] for c in ("es", "uk", "it")) == 73254)

    print("\n%d passed, %d FAILED" % (len(PASS), len(FAIL)))
    if FAIL:
        print("FAILED:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
