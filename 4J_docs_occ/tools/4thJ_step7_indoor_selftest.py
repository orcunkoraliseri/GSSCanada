#!/usr/bin/env python
"""Self-test for `4thJ_step7_indoor.py` -- `G7.13`, the indoor rule.

🔴 Every FAIL branch is EXERCISED, not asserted. The whole reason this gate
exists is `FINDING 42`, where a rule that was silently always-False looked
identical in a summary line to a rule that worked. A selftest that only ever
takes the accept path would reproduce exactly that blindness.

Runs locally. No cluster, no model, no generated batch. Pure decoded-record
dicts, plus the one real file the gate is required to import (`V7.c`).
"""

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
I = importlib.import_module("4thJ_step7_indoor")

STEP2 = os.path.join(os.path.dirname(HERE), "Step2_docs", "outputs_step2")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


def ep(dur, act="011", loc="at_home"):
    return {"duration_min": dur, "act": act, "loc_class": loc}


def rec(*eps):
    return {"episodes": list(eps)}


def day_at_home(act="011"):
    return rec(ep(1440, act, "at_home"))


def main():
    print("== 1. the shipped exclusion list is read from Step 2, not carried here ==")
    outdoor, digest = I.load_outdoor_at_home(STEP2)
    check("list loads from the shipped path", len(outdoor) > 0, repr(sorted(outdoor)))
    check("it is exactly the four D-S2-4 garden codes",
          sorted(outdoor) == ["322", "341", "342", "344"], repr(sorted(outdoor)))
    check("a digest is returned so the caller can record WHICH list it used",
          isinstance(digest, str) and len(digest) == 32, digest)
    src = open(os.path.join(HERE, "4thJ_step7_indoor.py"), encoding="utf-8").read()
    check("V7.c: the module carries no literal copy of the code set",
          '"322"' not in src and "'322'" not in src)
    missing = False
    try:
        I.load_outdoor_at_home(os.path.join(HERE, "no_such_dir"))
    except I.IndoorRuleError:
        missing = True
    check("a missing shipped list RAISES rather than falling back to a copy", missing)

    print("\n== 2. the rule itself, one episode at a time ==")
    check("at home, ordinary activity -> PRESENT",
          I.episode_present("011", "at_home", outdoor) is True)
    check("at home, gardening (341) -> ABSENT",
          I.episode_present("341", "at_home", outdoor) is False)
    for c in ("322", "342", "344"):
        check("at home, %s -> ABSENT" % c,
              I.episode_present(c, "at_home", outdoor) is False)
    check("other_place, ordinary activity -> ABSENT",
          I.episode_present("011", "other_place", outdoor) is False)
    for loc in ("private_transport", "public_transport"):
        check("%s -> ABSENT" % loc, I.episode_present("011", loc, outdoor) is False)
    check("LOC unknown (decoder None) -> ABSENT, never read as at home",
          I.episode_present("011", None, outdoor) is False)
    check("FINDING 42: the integer 11 is NOT at_home",
          I.episode_present("011", 11, outdoor) is False)

    print("\n== 3. the 000 reading, written down rather than left to `not in` ==")
    check("act None (the 000 slot) at home -> PRESENT",
          I.episode_present(None, "at_home", outdoor) is True)
    check("the literal string '000' at home -> PRESENT",
          I.episode_present("000", "at_home", outdoor) is True)
    check("act None NOT at home is still ABSENT",
          I.episode_present(None, "other_place", outdoor) is False)

    print("\n== 4. expanding a record to 1440 minutes ==")
    f = I.presence_minutes(day_at_home(), outdoor)
    check("a full at-home day is 1440 present minutes", len(f) == 1440 and all(f))
    f = I.presence_minutes(rec(ep(600, "011", "at_home"),
                               ep(240, "341", "at_home"),
                               ep(600, "011", "other_place")), outdoor)
    check("mixed day: 600 present, 840 absent",
          sum(1 for x in f if x) == 600, str(sum(1 for x in f if x)))
    short = False
    try:
        I.presence_minutes(rec(ep(1439, "011", "at_home")), outdoor)
    except I.IndoorRuleError:
        short = True
    check("a day that does not sum to 1440 is REFUSED, never padded", short)
    nonpos = False
    try:
        I.presence_minutes(rec(ep(0, "011", "at_home")), outdoor)
    except I.IndoorRuleError:
        nonpos = True
    check("a non-positive duration is refused", nonpos)

    print("\n== 5. the gate PASSES on a batch where the rule visibly binds ==")
    batch = [
        rec(ep(600, "011", "at_home"), ep(240, "341", "at_home"), ep(600, "011", "other_place")),
        rec(ep(720, "011", "at_home"), ep(720, "021", "other_place")),
        rec(ep(1380, "011", "at_home"), ep(60, "344", "at_home")),
        rec(ep(700, None, "at_home"), ep(740, "011", "public_transport")),
    ]
    res = I.gate_g7_13(batch, STEP2)
    print(I.report(res))
    check("baseline PASSES", res["passes"], repr(res["reasons"]))
    check("it used the shipped list", res["used_shipped_list"])
    check("the excluded episodes were counted", res["n_at_home_outdoor_episodes"] == 2,
          str(res["n_at_home_outdoor_episodes"]))
    check("341 and 344 are the ones counted",
          res["excluded_by_code"]["341"] == 1 and res["excluded_by_code"]["344"] == 1)
    check("the 000-at-home episode is counted separately",
          res["n_at_home_null_act_episodes"] == 1)
    check("presence share is neither 0 nor 1",
          0.0 < res["present_share"] < 1.0, "%.6f" % res["present_share"])

    print("\n== 6. THE PRE-REGISTERED PERTURBATION: a local copy differing by one code ==")
    for label, alt in (("one code REMOVED", frozenset(outdoor - {"341"})),
                       ("one code ADDED", frozenset(outdoor | {"999"}))):
        r = I.gate_g7_13(batch, STEP2, outdoor=alt)
        check("G7.13 FAILS when the list is a local copy with %s" % label,
              not r["passes"] and not r["used_shipped_list"],
              repr(r["reasons"])[:120])

    print("\n== 7. THE VACUITY GUARDS -- FINDING 42's signature, refused ==")
    r = I.gate_g7_13([rec(ep(1440, "011", "other_place"))], STEP2)
    check("presence identically ABSENT FAILS (this is FINDING 42's exact shape)",
          not r["passes"] and any("identically ABSENT" in x for x in r["reasons"]))
    check("...and it also names the unreached activity half",
          any("never reached" in x for x in r["reasons"]))
    r = I.gate_g7_13([day_at_home(), day_at_home()], STEP2)
    check("presence identically PRESENT FAILS (the rule excluded nothing)",
          not r["passes"] and any("identically PRESENT" in x for x in r["reasons"]))
    r = I.gate_g7_13([], STEP2)
    check("an empty batch FAILS rather than skipping",
          not r["passes"] and any("zero records" in x for x in r["reasons"]))

    print("\n== 8. the FINDING 42 regression, stated as a test ==")
    # Before D-S7-1 item 9 (a) the rule was `LOC == 11`. Reproduce it and show it
    # gives the all-absent signal that no other gate in Steps 4-9 would notice.
    old = [1 if (e["loc_class"] == 11) else 0
           for r_ in batch for e in r_["episodes"]]
    check("the OLD form `LOC == 11` matches zero episodes of a normal batch",
          sum(old) == 0, "%d of %d" % (sum(old), len(old)))
    check("the NEW form matches a non-zero number of the same episodes",
          sum(1 for r_ in batch for e in r_["episodes"]
              if I.episode_present(e.get("act"), e.get("loc_class"), outdoor)) > 0)

    print("\n%d passed, %d FAILED" % (len(PASS), len(FAIL)))
    if FAIL:
        print("FAILED:", FAIL)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
