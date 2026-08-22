# -*- coding: utf-8 -*-
"""Step 6 — the LEVEL-1 TIME BUDGET, and the crosswalk that makes it comparable.

`G6.4` is *"Level-1 time budgets vs published tables, MAPE ≤ 15.0 %"* and `G6.1`'s
`MAE` is taken on the same quantity. Neither can be computed until one question is
answered: **which of our 158 activity codes correspond to which Eurostat `acl00`
aggregate?** This module answers it, and every rule below is either forced by the
shipped `activity_target_list.csv` hierarchy or verified arithmetically against the
published table. Nothing here is inferred from a label alone.

---------------------------------------------------------------------------
🔴 THE THREE THINGS THAT ARE NOT OBVIOUS, EACH ESTABLISHED BY ARITHMETIC
---------------------------------------------------------------------------

**1. Our `level1` groups are NOT the Eurostat aggregates.** The obvious mapping —
leading digit `9` to `AC9A`, leading digit `1` to `AC1_TR` — is wrong in two places
and both are material:

  * `995`-`999` carry leading digit `9` but are *unspecified time*, not travel.
    In the UK they are **26.09 min/day** against 0.02 in Spain and 0.00 in Italy
    (`999` alone), a 1,300x country spread, and Eurostat reports them under
    `AC99NSP` — where the UK's own published figure is **49 min** against 1 and 1.
    Left in the travel bucket they would have inflated one country's travel budget
    by a third, on the fold that country is held out of.
  * `998` (*unspecified free time*) is Eurostat's `AC4-8NSP`, **inside** `AC4-8`.

**2. `910` (travel to/from work) STAYS IN `AC9A`.** This was got wrong first. The
`AC1_TR` label reads *"Employment, related activities and travel as part of/during
main and second job"* and `AC9A` reads *"Travel except travel related to jobs"*,
which together sound as though commuting belongs with employment. **The arithmetic
says otherwise:** `AC9A`'s seven children sum to the published `AC9A` **exactly** in
ES (70 = 70) and IT (79 = 79), and `AC913` *"Travel to/from work"* is one of those
seven. Moving `910` into `AC1_TR` cost 15 min/day in each direction and took the
travel category from a 5 % error to a 31 % one. The label was misleading; the
column total was not.

**3. 🔴 `AC9A`'s PUBLISHED PARENT IS UNUSABLE FOR THE UK.** Every other UK parent in
`tus_00age` sums to its children exactly. `AC9A` does not: parent **129**, children
**81**, a **48-minute hole** that matches the UK's anomalous `AC99NSP` of 49 almost
exactly. So this module takes `AC9A` as the **sum of its seven children** in every
country — identical to the parent in ES and IT, and the only defensible figure in
the UK. Using the published parent would charge the UK model a 58 % error for a
defect in the published table.

---------------------------------------------------------------------------
🔴 THE AGE BASE, WHICH IS A CHOICE AND IS DECLARED
---------------------------------------------------------------------------

Eurostat's `age` dimension offers `TOTAL, Y15-20, Y20-24, Y20-74, Y25-44, Y45-64,
Y65-74, Y_GE65`. Our eight frozen bands can reproduce **exactly three** of them with
no boundary straddling:

    Y25-44  =  25-34 + 35-44
    Y45-64  =  45-54 + 55-64
    Y_GE65  =  65-74 + 75+

`Y20-74` cannot be built (our `15-24` straddles 20) and `Y65-74` is absent from all
three countries (`FINDING 55`). `TOTAL`'s own population base is not stated in the
JSON-stat, and our corpus floor is age 11, so **`TOTAL` is a comparison between two
different populations** and is reported as context only. The three exact bands are
the scoreable ones.

---------------------------------------------------------------------------
Calibrated on the REAL corpus before ever being pointed at a model
---------------------------------------------------------------------------

Weighted by `weight_dia_cal` (`FINDING 53` — the unweighted mean is not calendar
representative and it cost Italy 42 min/day of employment), the real harmonised
corpus scores **MAPE 2.79 % – 13.53 %** against `tus_00age` 2010 across all three
countries and all four bands — inside `G6.4`'s 15 % band everywhere. A gate whose
own ground truth cannot pass it is not a gate, and this one can.
"""

import collections
import json
import math
import os

DAY = 1440
ACT_NULL = "000"

# The six comparable Eurostat aggregates, in reporting order.
AGGREGATES = ["AC0", "AC1_TR", "AC2", "AC3", "AC4-8", "AC9A"]
# Reported beside them, never inside the MAPE: unspecified time and our own null act.
EXTRA = ["AC99NSP", "null_000"]

# `AC9A`'s children. The parent is NOT read -- see reading 3 in the docstring.
AC9A_CHILDREN = ["AC9B", "AC9C", "AC9D", "AC913", "AC936", "AC938", "AC90NSP"]

# The two carve-outs that the leading digit gets wrong.
UNSPECIFIED_TIME = frozenset(["995", "996", "997", "999"])   # -> AC99NSP
UNSPECIFIED_LEISURE = "998"                                   # -> AC4-8, via AC4-8NSP

_BY_LEADING_DIGIT = {"0": "AC0", "1": "AC1_TR", "2": "AC2", "3": "AC3",
                     "4": "AC4-8", "5": "AC4-8", "6": "AC4-8", "7": "AC4-8",
                     "8": "AC4-8", "9": "AC9A"}

# The exactly-reproducible Eurostat age bands, and nothing else.
AGE_BAND_MAP = {"25-34": "Y25-44", "35-44": "Y25-44",
                "45-54": "Y45-64", "55-64": "Y45-64",
                "65-74": "Y_GE65", "75+": "Y_GE65"}
SCOREABLE_BANDS = ("Y25-44", "Y45-64", "Y_GE65")

# `D-S6-3` item 1, ruled 2026-08-20: MAPE on non-zero cells, with a pre-registered
# "approximately zero" tolerance. The author took the LOOSER option, `< 1.0 %`.
#
# 🔴 The tolerance governs THE MODEL'S value when the PUBLISHED cell is zero. It is
# not a rule for deciding which published cells count as zero. Written the other way
# round first, it classified Italy's published `AC2` of ELEVEN MINUTES (0.76 % of the
# day) as "approximately zero" and then failed the real corpus for putting 14.67
# minutes there -- a gate failing its own ground truth for a 3.7-minute difference.
ZERO_TOLERANCE_PCT = 1.0

# A published cell is ZERO when the table says zero. Two of the three units are
# `h:mm` strings (`FINDING 39`), so `0:00` means "under 30 seconds", not "exactly
# nothing"; the floor is half a minute and nothing below it is distinguishable.
PUBLISHED_ZERO_FLOOR_MIN = 0.5

# `D-S6-12` item 1 (a) + MAE, ruled 2026-08-22. `D-S6-3` covered published cells that
# are ZERO and left NEAR-ZERO uncovered, and near-zero is where the damage was:
#
#   🔴 `FINDING 90` -- all three of `G6.4`'s reported held-out MAPEs were the
#   `Y_GE65` band, and all three were driven by a published cell of 1-5 min/day
#   (Eurostat correctly publishes ~1 min/day of EMPLOYMENT for the over-65s). That
#   band is not the worst-fitting one: over `G6.6`'s eighteen cells MAPE and MAE are
#   NEGATIVELY rank-correlated, Spearman -0.5604, and Italy's `Y_GE65` MAE of 21.21
#   is the second-LOWEST of twelve rows while its `Y25-44` at MAE 77.75 -- four times
#   larger -- was reported as the milder 39.76 %. The headline number was selecting
#   on denominator smallness, not on fit.
#
#   With `FINDING 39`'s country-dependent rounding floor a cell PRINTED as `1` is
#   truly in [0.5, 1.5], so the UK's 630 % APE spans 387-1360 % on rounding noise
#   alone: not identified, and no verdict may rest on it.
#
# A cell is SCOREABLE ON APE only when its published value clears the floor. Below it
# the cell moves to an ABSOLUTE tolerance, by direct analogy with `SIGN_FLOOR_MIN =
# 2.0` (`D-S6-10` item 2) and the zero-cell hit/miss rule above. Both numbers are
# pre-registered here and neither is tuned to an observed result.
#
# 🔴 This does NOT weaken the bar: `MAPE_MAX = 15.0 %` stays binding, unchanged, on
# every substantive cell (>= 10 min/day). It removes cells on which a percentage is
# not identifiable, and replaces them with a test that is.
PUBLISHED_FLOOR_MIN = 10.0    # min/day a published cell must clear to be APE-scoreable
FLOOR_MAE_MAX = 15.0          # min/day absolute tolerance for cells below that floor


class Level1Error(ValueError):
    pass


def aggregate_of(code):
    """Our 3-digit activity code -> Eurostat aggregate. `None` for the null act."""
    if code is None or code == ACT_NULL:
        return "null_000"
    if not (len(code) == 3 and code.isdigit()):
        raise Level1Error("activity code %r is not three digits" % (code,))
    if code in UNSPECIFIED_TIME:
        return "AC99NSP"
    if code == UNSPECIFIED_LEISURE:
        return "AC4-8"
    try:
        return _BY_LEADING_DIGIT[code[0]]
    except KeyError:
        raise Level1Error("no aggregate for activity code %r" % (code,))


def budget(records, weights=None):
    """Minutes per day per aggregate, over decoded records.

    `records` are `tools/decoder.decode_record()` outputs. `weights` is a parallel
    sequence or `None` for an unweighted mean.

    🔴 A record whose durations do not sum to `DAY` is REFUSED, not scaled. A
    short diary averaged in is a silent dip in whichever aggregate it is short of.
    """
    num = collections.Counter()
    den = 0.0
    for i, rec in enumerate(records):
        w = 1.0 if weights is None else float(weights[i])
        if w != w:                      # NaN
            raise Level1Error(
                "record %d has a NaN weight. Refused: two null UK weights in "
                "73,254 silently turned every UK aggregate into NaN once already, "
                "and nothing warned." % i)
        total = sum(int(e["duration_min"]) for e in rec["episodes"])
        if total != DAY:
            raise Level1Error("record %d sums to %d minutes, not %d" % (i, total, DAY))
        den += w
        for e in rec["episodes"]:
            num[aggregate_of(e.get("act"))] += w * int(e["duration_min"])
    if den <= 0:
        raise Level1Error("no records, or all weights zero. A budget over nothing "
                          "is not a budget (V6.b).")
    out = {k: num[k] / den for k in AGGREGATES + EXTRA}
    out["_n"] = len(records)
    out["_weight_sum"] = den
    return out


# ---------------------------------------------------------------------------
# the published side
# ---------------------------------------------------------------------------
def _jsonstat(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    ids, size = d["id"], d["size"]
    idx = {k: d["dimension"][k]["category"]["index"] for k in ids}
    val = d["value"]

    def get(**sel):
        p = 0
        for k, s in zip(ids, size):
            if sel[k] not in idx[k]:
                raise Level1Error("%s=%r is not in this table" % (k, sel[k]))
            p = p * s + idx[k][sel[k]]
        v = val.get(str(p))
        if v is None:
            return None
        if isinstance(v, str) and ":" in v:
            # 🔴 `FINDING 39`: two of the three units are `h:mm` STRINGS and a
            # float cast truncates them silently. Parsed, never cast.
            h, m = v.split(":")
            return int(h) * 60 + int(m)
        return float(v)
    return get, idx


def published(eurostat_dir, country, age="TOTAL", wave="2010", unit="TIME_SP", sex="T"):
    """The published level-1 budget, in minutes/day.

    🔴 `AC9A` is the SUM OF ITS CHILDREN, never the published parent. See reading 3.
    The discrepancy is returned as `_ac9a_parent_minus_children` so a caller can see
    it rather than have it hidden.
    """
    C = country.upper()
    path = os.path.join(eurostat_dir, "tus_00age_%s.json" % C)
    if not os.path.exists(path):
        raise Level1Error("no published table at %s" % path)
    get, idx = _jsonstat(path)
    kw = dict(freq="A", unit=unit, sex=sex, age=age, geo=C, time=wave)

    kids = [get(acl00=a, **kw) for a in AC9A_CHILDREN]
    if any(v is None for v in kids):
        missing = [a for a, v in zip(AC9A_CHILDREN, kids) if v is None]
        raise Level1Error("AC9A children missing for %s/%s/%s: %s" % (C, age, wave, missing))
    out = {}
    for a in AGGREGATES:
        out[a] = sum(kids) if a == "AC9A" else get(acl00=a, **kw)
    for a in EXTRA:
        out[a] = get(acl00="AC99NSP", **kw) if a == "AC99NSP" else None
    parent = get(acl00="AC9A", **kw)
    out["_ac9a_parent"] = parent
    out["_ac9a_parent_minus_children"] = (parent - sum(kids)) if parent is not None else None
    out["_total"] = get(acl00="TOTAL", **kw)
    out["_source"] = "%s tus_00age %s %s %s sex=%s" % (C, age, wave, unit, sex)
    return out


# ---------------------------------------------------------------------------
# the gates
# ---------------------------------------------------------------------------
def gate_g6_4(model, pub, band, mape_max=15.0):
    """`G6.4` — MAPE of the level-1 budget against the published table.

    Three bases, chosen by the PUBLISHED value alone and never by the model's:

      * published `< 0.5` min/day — **zero cell**. Hit/miss against the pre-registered
        `< 1.0 %` of the day (`D-S6-3` item 1 (c), ruled 2026-08-20).
      * published `< 10.0` min/day — **floor cell**. Absolute tolerance,
        `|model − published| < 15.0` min/day (`D-S6-12` item 1, ruled 2026-08-22).
        A percentage on such a cell is not identifiable under `FINDING 39`'s rounding.
      * otherwise — **APE**, and these are the cells the MAPE is taken over.

    🔴 The basis is picked from the published side ONLY. Choosing it from the model's
    value, or from the error, would let a batch select the test that flatters it.

    `mae` is returned over ALL SIX aggregates on every band, whatever their basis
    (`D-S6-12` item 1 point 3): the percentage and the minutes disagree about which
    band is worst, so both are reported and neither is quoted alone.
    """
    rows, apes, zero_rows, floor_rows = [], [], [], []
    for a in AGGREGATES:
        e, g = pub.get(a), model.get(a)
        if e is None:
            raise Level1Error("published %s is absent -- G6.4 cannot score a cell "
                              "that was never published, and NOT PUBLISHED is not "
                              "a pass" % a)
        if e < PUBLISHED_ZERO_FLOOR_MIN:
            hit = g < ZERO_TOLERANCE_PCT / 100.0 * DAY
            zero_rows.append(dict(aggregate=a, published=e, model=g, hit=hit))
            rows.append(dict(aggregate=a, published=e, model=g, ape=None,
                             basis="zero-cell hit/miss"))
            continue
        if e < PUBLISHED_FLOOR_MIN:
            dev = abs(g - e)
            hit = dev < FLOOR_MAE_MAX
            floor_rows.append(dict(aggregate=a, published=e, model=g,
                                   abs_error=dev, hit=hit))
            rows.append(dict(aggregate=a, published=e, model=g, ape=None,
                             abs_error=dev, basis="floor-cell absolute"))
            continue
        ape = 100.0 * abs(g - e) / e
        apes.append(ape)
        rows.append(dict(aggregate=a, published=e, model=g, ape=ape, basis="APE"))
    if not apes:
        return dict(passes=False, blocked=True,
                    reason="every published cell is below the %.1f min/day APE floor, "
                           "so there is no identifiable MAPE to take. FAILs rather "
                           "than skipping (V6.b)." % PUBLISHED_FLOOR_MIN)
    mape = sum(apes) / len(apes)
    misses = [z for z in zero_rows if not z["hit"]]
    floor_misses = [z for z in floor_rows if not z["hit"]]
    reasons = []
    if mape > mape_max:
        reasons.append("MAPE %.2f %% exceeds %.1f %%" % (mape, mape_max))
    for z in misses:
        reasons.append("zero-cell %s: published %.2f min, model %.2f min, outside the "
                       "pre-registered %.1f %% tolerance"
                       % (z["aggregate"], z["published"], z["model"], ZERO_TOLERANCE_PCT))
    for z in floor_misses:
        reasons.append("floor-cell %s: published %.2f min/day is below the %.1f min/day "
                       "APE floor, model %.2f min, absolute error %.2f min/day exceeds "
                       "the pre-registered %.1f min/day tolerance"
                       % (z["aggregate"], z["published"], PUBLISHED_FLOOR_MIN,
                          z["model"], z["abs_error"], FLOOR_MAE_MAX))
    return dict(passes=not reasons, blocked=False, reasons=reasons, band=band,
                mape=round(mape, 4), mape_max=mape_max, n_scored=len(apes),
                n_zero_cells=len(zero_rows), n_floor_cells=len(floor_rows),
                published_floor_min=PUBLISHED_FLOOR_MIN, floor_mae_max=FLOOR_MAE_MAX,
                floor_cells=floor_rows, rows=rows,
                mae=round(sum(abs(r["model"] - r["published"]) for r in rows) / len(rows), 4),
                published_source=pub.get("_source"))


def mae(model, pub):
    """`G6.1`'s comparison quantity: mean absolute error in minutes/day over the six
    aggregates. Deliberately NOT a percentage -- `G6.1` compares two absolute errors
    against the same published table and a percentage would rescale each by its own
    denominator."""
    return sum(abs(model[a] - pub[a]) for a in AGGREGATES) / float(len(AGGREGATES))


if __name__ == "__main__":
    print("Library module. Run 4thJ_step6_level1_selftest.py for its unit tests.")
