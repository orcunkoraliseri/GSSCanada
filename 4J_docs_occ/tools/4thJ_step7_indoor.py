#!/usr/bin/env python
"""
4J Step 7: `G7.13` -- THE INDOOR RULE, and the presence signal it produces.

    presence  <=>  (LOC == "at_home")  AND  (ACT not in OUTDOOR_AT_HOME)

WHY THIS GATE HAS A MODULE OF ITS OWN
-------------------------------------
`G7.13` is the seam between a diary and a building. Everything upstream is text;
everything downstream is a `Schedule:File` an EnergyPlus run believes. If the
rule is wrong the diaries can be perfect and every load in the paper is wrong,
and NOTHING else in Steps 4-9 is watching this particular arrow.

It has already been wrong once. `FINDING 42`: the gate was specified as
`LOC == 11`, comparing the serialised `LOC` -- a STRING, one of
`at_home / other_place / private_transport / public_transport / unknown` --
against an integer. The test was silently `False` for every episode ever
written, so **presence was identically zero for every occupant of every
dwelling, in every country**. A building with nobody in it never fails a
schedule gate; it fails the paper. `D-S7-1` item 9 (a) re-pointed the rule to
`LOC == "at_home"` on 2026-08-20 and this module is that ruling in code.

🔴 THE VACUITY GUARD IS THE POINT, NOT DECORATION
--------------------------------------------------
`FINDING 42`'s signature is a presence signal that is CONSTANT. So
`gate_g7_13()` FAILS on a constant signal -- all-absent or all-present -- rather
than reporting a clean pass over a dead rule. A gate that cannot tell "the rule
excluded nothing" from "the rule was never wired in" is not a check. `V5.a` says
the same thing about `G5.2`'s impossibility table, and it is the same failure.

🔴 `V7.c` -- THE LIST IS IMPORTED, NEVER COPIED
-----------------------------------------------
`OUTDOOR_AT_HOME` is read LIVE from `Step2_docs/outputs_step2/outdoor_at_home.csv`,
the file Step 2 shipped. The gate ALSO re-reads that file itself and refuses if
the caller's set differs from it by so much as one code. That is exactly the
pre-registered perturbation ("use a local copy that differs by one code -> G7.13
must fail"): a second copy of a list drifts invisibly, and validating against the
copy validates nothing.

THE FOUR EXCLUDED CODES, AND WHY A LOCATION CODE NEEDS AN ACTIVITY TEST AT ALL
------------------------------------------------------------------------------
`D-S2-4` merges the garden and the yard into location code 11 (ES) / 11-12 (IT),
which harmonises to `at_home`. So "at home" includes being outdoors on the
property, where a person heats and cools nothing. The shipped list excludes
`322` (cleaning the exterior of the dwelling), `341` (gardening), `342` (tending
yard/farmyard animals) and `344` (walking the dog). Measured on the corpus these
are 10,436 episodes -- small, and exactly the episodes a naive `LOC` test would
count as indoor.

🔴 `000` AT HOME COUNTS AS PRESENT, AND THAT IS A READING
---------------------------------------------------------
`D-S3-9` gives an unrecorded activity the code `000`, and `D-S7-1 (c)` made it a
state of its own. Per the Step 7 validation document's measurement of 2026-08-20
-- **quoted here, NOT re-derived by this module, which has never been run against
a corpus or a generated batch** -- the rule reproduces the shipped
`indoor_presence` column on all 2,022,141 episodes that carry an activity, and
differs on 1,927 at-home episodes whose `act` is NULL (ES 290 / IT 105 /
UK 1,532), where the shipped column is itself `NA`. A person at home doing an
unrecorded activity is present, so PRESENT is right -- **but it is a reading, not
an operator precedence accident**, and it is therefore written here explicitly,
counted separately in the report, and never left to `not in`.

⚪ WHAT THIS MODULE IS NOT
--------------------------
It does not emit an IDF, choose a timestep, or write a `Schedule:File`. Those are
`G7.14`-`G7.16`. It does not decide what a `000` episode contributes to an
internal-gains schedule -- only whether the person is inside the volume.
"""

import csv
import hashlib
import io
import os

DAY_MINUTES = 1440

#: The shipped list, by name. Step 2 owns the file; this module owns nothing but
#: the path to it.
OUTDOOR_AT_HOME_FILE = "outdoor_at_home.csv"

#: `D-S3-9`'s null-activity code. Present at home, per the docstring above.
ACT_NULL_CODE = "000"

#: The harmonised location value the indoor rule tests. `FINDING 42`: it is a
#: STRING and it is never the integer 11.
LOC_AT_HOME = "at_home"


class IndoorRuleError(ValueError):
    pass


# --------------------------------------------------------------------------
# the shipped exclusion list
# --------------------------------------------------------------------------
def load_outdoor_at_home(step2_dir):
    """Read `OUTDOOR_AT_HOME` from the file Step 2 shipped.

    Returns `(frozenset_of_codes, md5_of_the_file)`. The digest is returned so a
    caller can record WHICH list it validated against; a provenance field nobody
    fills is not provenance.
    """
    path = os.path.join(step2_dir, OUTDOOR_AT_HOME_FILE)
    if not os.path.exists(path):
        raise IndoorRuleError(
            "the shipped exclusion list is missing: %s. V7.c requires G7.13 import "
            "it from its shipped path; there is deliberately no fallback copy in "
            "this module to fall back to." % path)
    raw = open(path, 'rb').read()
    codes = []
    with io.open(path, encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            code = (row.get('target_code') or '').strip()
            if code:
                codes.append(code)
    if not codes:
        # `V5.b`'s argument, transplanted: a filter over an empty set excludes
        # nothing and passes for the wrong reason.
        raise IndoorRuleError(
            "%s parsed to ZERO codes. An empty exclusion list makes the activity "
            "half of the indoor rule a no-op, and G7.13 would then be testing "
            "LOC alone -- which is the shape FINDING 42 already produced once."
            % path)
    if len(set(codes)) != len(codes):
        raise IndoorRuleError("duplicate target_code in %s: %r" % (path, codes))
    return frozenset(codes), hashlib.md5(raw).hexdigest()


# --------------------------------------------------------------------------
# the rule
# --------------------------------------------------------------------------
def episode_present(act, loc_class, outdoor):
    """The indoor rule, on ONE episode. `act` and `loc_class` are the decoder's
    output, so `None` is a real value on both: `act is None` iff the ACT slot was
    `000`, `loc_class is None` iff the LOC slot was `unknown`.

    🔴 `loc_class is None` (LOC unknown) is NOT at home. An unknown location is
    not evidence of presence, and reading it as one would inflate every schedule
    in the direction that flatters the paper.
    """
    if loc_class != LOC_AT_HOME:
        return False
    if act is None or act == ACT_NULL_CODE:
        return True          # the declared reading -- see the module docstring
    return act not in outdoor


def presence_minutes(record, outdoor):
    """Expand one decoded record into `DAY_MINUTES` presence flags.

    `record` is `tools/decoder.decode_record()`'s output, or anything with an
    `episodes` list of dicts carrying `duration_min`, `act` and `loc_class`.

    🔴 The durations must sum to exactly 1440. They do in all 73,254 corpus
    diaries and the tally automaton enforces it at generation time, so a record
    arriving here that does not sum is a defect upstream and is refused rather
    than padded -- padding would turn a structural failure into a quiet dip in
    occupancy.
    """
    eps = record["episodes"] if isinstance(record, dict) else record
    flags = []
    for e in eps:
        d = int(e["duration_min"])
        if d <= 0:
            raise IndoorRuleError("non-positive episode duration %r" % d)
        flags.extend([episode_present(e.get("act"), e.get("loc_class"), outdoor)] * d)
    if len(flags) != DAY_MINUTES:
        raise IndoorRuleError(
            "episode durations sum to %d minutes, not %d. Refused rather than "
            "padded: a short diary padded to a day is an occupancy dip nobody "
            "would ever trace back to here." % (len(flags), DAY_MINUTES))
    return flags


# --------------------------------------------------------------------------
# the gate
# --------------------------------------------------------------------------
def gate_g7_13(records, step2_dir, outdoor=None):
    """`G7.13` -- was the indoor rule applied, with the SHIPPED exclusion list?

    `outdoor` is the set the caller derived presence with. Leaving it `None`
    means "use the shipped list", which passes trivially; the parameter exists so
    the pre-registered perturbation -- a local copy differing by one code -- has
    something to perturb.

    Returns a dict with `passes` and everything needed to read the verdict.
    """
    shipped, digest = load_outdoor_at_home(step2_dir)
    used = shipped if outdoor is None else frozenset(outdoor)

    reasons = []

    # `V7.c`. The pre-registered perturbation lands exactly here.
    if used != shipped:
        reasons.append(
            "the exclusion list used is not the shipped one: %d extra %s, %d "
            "missing %s. V7.c -- a second copy of a list drifts invisibly, and "
            "validating against the copy validates nothing."
            % (len(used - shipped), sorted(used - shipped),
               len(shipped - used), sorted(shipped - used)))

    n_records = 0
    minutes_total = 0
    minutes_present = 0
    n_ep = 0
    n_at_home = 0
    n_outdoor_at_home = 0
    n_null_act_at_home = 0
    by_code = dict((c, 0) for c in shipped)
    all_present = True
    all_absent = True

    for rec in records:
        n_records += 1
        flags = presence_minutes(rec, used)
        minutes_total += len(flags)
        p = sum(1 for f in flags if f)
        minutes_present += p
        if p != len(flags):
            all_present = False
        if p != 0:
            all_absent = False
        eps = rec["episodes"] if isinstance(rec, dict) else rec
        for e in eps:
            n_ep += 1
            if e.get("loc_class") != LOC_AT_HOME:
                continue
            n_at_home += 1
            a = e.get("act")
            if a is None or a == ACT_NULL_CODE:
                n_null_act_at_home += 1
            elif a in used:
                n_outdoor_at_home += 1
                if a in by_code:
                    by_code[a] += 1

    if n_records == 0:
        reasons.append(
            "zero records. A rule applied to nothing excluded nothing; this FAILs "
            "rather than skipping, for V5.b's reason.")
    else:
        # 🔴 `FINDING 42`'s signature, refused by construction.
        if all_absent:
            reasons.append(
                "presence is identically ABSENT across every record. That is the "
                "exact shape FINDING 42 produced when the rule compared a string "
                "LOC against the integer 11, and it is indistinguishable from a "
                "rule that was never wired in.")
        if all_present:
            reasons.append(
                "presence is identically PRESENT across every record. The rule "
                "excluded nothing, so it cannot be shown to bind.")
        if n_at_home == 0:
            reasons.append(
                "no episode in the batch is at_home, so the activity half of the "
                "rule was never reached.")

    return {
        "passes": not reasons,
        "reasons": reasons,
        "outdoor_at_home": sorted(shipped),
        "outdoor_at_home_md5": digest,
        "used_shipped_list": used == shipped,
        "n_records": n_records,
        "n_episodes": n_ep,
        "minutes_total": minutes_total,
        "minutes_present": minutes_present,
        "present_share": (float(minutes_present) / minutes_total) if minutes_total else None,
        "n_at_home_episodes": n_at_home,
        "n_at_home_outdoor_episodes": n_outdoor_at_home,
        "n_at_home_null_act_episodes": n_null_act_at_home,
        "excluded_by_code": by_code,
    }


def report(res):
    """One block of text, printed BEFORE any verdict is acted on (`V7.b`)."""
    L = []
    L.append("G7.13  indoor rule  (LOC == %r) AND (ACT not in OUTDOOR_AT_HOME)" % LOC_AT_HOME)
    L.append("  exclusion list      %s  md5 %s  %s"
             % (res["outdoor_at_home"], res["outdoor_at_home_md5"],
                "SHIPPED" if res["used_shipped_list"] else "*** NOT THE SHIPPED LIST ***"))
    L.append("  records             %d" % res["n_records"])
    L.append("  episodes            %d" % res["n_episodes"])
    L.append("  minutes present     %d / %d" % (res["minutes_present"], res["minutes_total"]))
    if res["present_share"] is not None:
        L.append("  presence share      %.4f %%" % (100.0 * res["present_share"]))
    L.append("  at_home episodes    %d" % res["n_at_home_episodes"])
    L.append("  ... excluded        %d  %s"
             % (res["n_at_home_outdoor_episodes"], res["excluded_by_code"]))
    L.append("  ... null act (000)  %d  counted PRESENT by declaration"
             % res["n_at_home_null_act_episodes"])
    L.append("  verdict             %s" % ("PASS" if res["passes"] else "FAIL"))
    for r in res["reasons"]:
        L.append("    - %s" % r)
    return "\n".join(L)


if __name__ == "__main__":
    import sys
    print("Library module. Run 4thJ_step7_indoor_selftest.py for its unit tests.",
          file=sys.stderr)
