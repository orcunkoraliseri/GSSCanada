#!/usr/bin/env python
"""Self-test for `4thJ_step6_rakeddonor.py`.

Every guard is SEEN FIRING on a case built to fire it. The headline case is
the `prereg` perturbation itself: score the raked-donor null against itself as if
it were the model, and confirm `G6.1` reports EXACTLY zero margin and FAILS --
because a `>=` comparison would have passed it (`V6.c`).

Runs locally. No cluster, no model, no corpus, no marginals file.
"""

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
R = importlib.import_module("4thJ_step6_rakeddonor")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


def raises(name, fn, expect):
    try:
        fn()
    except R.RakeError as e:
        check(name, expect in str(e), str(e)[:100])
        return
    check(name, False, "did NOT raise -- guard never fired")


# A donor pool from the N-1 countries (es, uk) with `it` held out.
def pool():
    out = []
    for c in ("es", "uk"):
        for sex in ("male", "female"):
            for day in ("weekday", "weekend"):
                for k in range(5):
                    out.append({"country": c, "strat_sex": sex, "strat_day_type": day,
                                "id": "%s-%s-%s-%d" % (c, sex, day, k)})
    return out


TARGET = {
    "strat_sex": {"male": 0.48, "female": 0.52},
    "strat_day_type": {"weekday": 0.7, "weekend": 0.3},
}
SRC = "outputs_step5/marginals_it.csv@2026-08-20"


def main():
    print("\n== 1. IPF converges and reproduces the target marginals ==")
    res = R.rake(pool(), TARGET, "it", SRC)
    check("converged", res["max_dev_pp"] <= R.MARGIN_TOL_PP,
          "%.6f pp in %d iterations" % (res["max_dev_pp"], res["iterations"]))
    w = res["weights"]
    tot = sum(w)
    for var, tgt in TARGET.items():
        for cat, want in tgt.items():
            got = sum(x for d, x in zip(pool(), w) if d[var] == cat) / tot
            check("  %s=%s -> %.4f (target %.4f)" % (var, cat, got, want), abs(got - want) < 5e-3)
    check("weights are all positive", all(x > 0 for x in w))
    check("provenance carried through", res["marginals_source"] == SRC)
    check("n_donors recorded", res["n_donors"] == 40, str(res["n_donors"]))

    print("\n== 2. every guard, SEEN FIRING ==")
    raises("empty donor pool refused", lambda: R.rake([], TARGET, "it", SRC), "empty donor pool")
    raises("no target marginals refused", lambda: R.rake(pool(), {}, "it", SRC), "no target marginals")
    raises("blank provenance refused", lambda: R.rake(pool(), TARGET, "it", "   "),
           "marginals_source is empty")
    raises("held-out country in the pool refused",
           lambda: R.rake(pool() + [{"country": "it", "strat_sex": "male",
                                     "strat_day_type": "weekday"}], TARGET, "it", SRC),
           "appears in the donor pool")
    raises("donor missing a stratum field refused",
           lambda: R.rake(pool() + [{"country": "es", "strat_sex": "male"}], TARGET, "it", SRC),
           "carry no")
    raises("marginal that does not sum to 1 refused",
           lambda: R.rake(pool(), {"strat_sex": {"male": 0.4, "female": 0.4}}, "it", SRC),
           "sums to")
    raises("target category no donor has refused",
           lambda: R.rake(pool(), {"strat_sex": {"male": 0.4, "female": 0.3, "other": 0.3}},
                          "it", SRC),
           "NO donor has")
    # A structurally infeasible case: in this pool sex and day type are perfectly
    # correlated (every male is a weekday, every female a weekend), so no set of
    # weights can hit male=0.48 AND weekday=0.70 at once. IPF oscillates.
    degenerate = ([{"country": "es", "strat_sex": "male", "strat_day_type": "weekday"}] * 10
                  + [{"country": "uk", "strat_sex": "female", "strat_day_type": "weekend"}] * 10)
    raises("structurally infeasible target: non-convergence reported as a FAILURE, not a result",
           lambda: R.rake(degenerate, TARGET, "it", SRC),
           "did not converge")

    print("\n== 3. THE prereg PERTURBATION: score the null against ITSELF ==")
    null_value = 12.34
    s = R.score_margin(null_value, null_value, lower_is_better=True,
                       model_source=SRC, null_source=SRC)
    check("margin is EXACTLY zero", s["margin"] == 0.0, repr(s["margin"]))
    check("and G6.1 FAILS on it (V6.c strict '>')", s["passes"] is False)
    check("a '>=' reading would have PASSED it", (s["margin"] >= 0.0) is True,
          "which is precisely why the comparison is strict")

    print("\n== 4. the comparison behaves in both directions ==")
    better = R.score_margin(10.0, 12.0, lower_is_better=True, model_source=SRC, null_source=SRC)
    worse = R.score_margin(14.0, 12.0, lower_is_better=True, model_source=SRC, null_source=SRC)
    check("model better than the null passes", better["passes"] and better["margin"] == 2.0)
    check("model worse than the null fails", (not worse["passes"]) and worse["margin"] == -2.0)
    hi = R.score_margin(0.9, 0.7, lower_is_better=False, model_source=SRC, null_source=SRC)
    check("higher-is-better metric handled", hi["passes"] and abs(hi["margin"] - 0.2) < 1e-9)

    print("\n== 5. the handicap guard: mismatched marginals are refused ==")
    raises("null raked onto different marginals refused",
           lambda: R.score_margin(10.0, 12.0, True, SRC, "outputs_step5/marginals_es.csv@2026-08-20"),
           "requires the same marginals")

    print("\n== 6. FINDING 52: a donor category the target never names is DELETED, silently ==")
    # The es fold after D-S5-4 (b) / FINDING 51: the Spanish census has no
    # `homemaker` band, so its published marginal has FIVE categories while the
    # uk+it donor pool carries SIX. Before Guard 5, rake() zeroed every
    # homemaker donor and still reported max_dev_pp = 5.6e-15.
    ES_SRC = "outputs_step5/marginals_es.csv@2026-08-20"
    ES5 = {"strat_econ_status": {"employed": 0.498007, "unemployed": 0.209115,
                                 "student": 0.055092, "retired": 0.149912,
                                 "other_inactive": 0.087874}}
    check("Spain's five published bands sum to 1",
          abs(sum(ES5["strat_econ_status"].values()) - 1.0) < 1e-9)
    six = [{"country": c, "strat_econ_status": e, "id": "%s-%s-%d" % (c, e, k)}
           for c in ("uk", "it")
           for e in ("employed", "unemployed", "student", "retired",
                     "homemaker", "other_inactive")
           for k in range(10)]
    n_home = sum(1 for d in six if d["strat_econ_status"] == "homemaker")
    check("donor pool carries homemaker, the target does not", n_home == 20)

    raises("Guard 5 fires on the uncollapsed pool",
           lambda: R.rake(six, ES5, "es", ES_SRC),
           "never names")

    coll = {"strat_econ_status": {"homemaker": "other_inactive"}}
    res6 = R.rake(six, ES5, "es", ES_SRC, collapse=coll)
    check("collapsed run converges", res6["max_dev_pp"] <= R.MARGIN_TOL_PP,
          "%.3g pp" % res6["max_dev_pp"])
    check("and it keeps the WHOLE pool -- 0 donors deleted",
          sum(1 for x in res6["weights"] if x > 0) == len(six),
          "%d of %d" % (sum(1 for x in res6["weights"] if x > 0), len(six)))
    check("the collapse is stamped on the provenance label",
          res6["marginals_source"].endswith("|collapse=strat_econ_status:homemaker>other_inactive"),
          res6["marginals_source"])
    check("and recorded in the result", res6["collapse"] == coll)

    # The point of stamping it: the existing handicap guard now refuses to
    # compare a five-band null with a six-band model, for free.
    raises("collapsed null vs uncollapsed model refused by the handicap guard",
           lambda: R.score_margin(10.0, 12.0, True, res6["marginals_source"], ES_SRC),
           "requires the same marginals")

    raises("collapsing INTO an unnamed category is refused too",
           lambda: R.rake(six, ES5, "es", ES_SRC,
                          collapse={"strat_econ_status": {"homemaker": "unknown"}}),
           "is not a category of target")
    raises("collapsing a variable nobody rakes on is refused",
           lambda: R.rake(six, ES5, "es", ES_SRC,
                          collapse={"strat_sex": {"male": "female"}}),
           "not among the target marginals")

    five = [d for d in six if d["strat_econ_status"] != "homemaker"]
    res6b = R.rake(five, ES5, "es", ES_SRC)
    check("callers that never needed a collapse are UNAFFECTED",
          res6b["collapse"] is None and res6b["marginals_source"] == ES_SRC)

    print("\n== 7. what this module still CANNOT do ==")
    print("     rake() needs the held-out country's PUBLISHED marginals.")
    print("     Step 5.1 has built uk and es (private-household frame); `it` is")
    print("     NOT BUILT -- every ISTAT route funnels into esploradati.istat.it,")
    print("     which refuses TCP 443. So G6.1's bar is computable for uk and es")
    print("     and for `it` not at all. Not a code gap.")

    print("\n%d passed, %d FAILED" % (len(PASS), len(FAIL)))
    if FAIL:
        print("FAILED:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
