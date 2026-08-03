"""FINDING 8 smoke -- diagnose the residuals. NOT a repair.

The attribution pass split the 7 misses into two groups, and one mechanism would explain both:

  T9-13 rebuilds every modulated schedule with `_build_compact_fields_2dt`, i.e. on TWO day types
  (weekday / weekend). Any prototype whose Saturday and Sunday profiles DIFFER cannot survive that
  reconstruction, even at r = 1.000, because two distinct source profiles are folded into one. If
  that is the mechanism, each object's residual is predictable from the SCHEDULES ALONE.

So this script predicts each object's ratio without ever reading the energy results:

  predicted = calendar-weighted annual mean(rebuilt DHWv2 Schedule:Compact)
            / calendar-weighted annual mean(source Schedule:Year)

and the caller compares that column against the measured energy ratios. If they disagree, the
hypothesis is wrong and is recorded as refuted -- this script has no way to make itself right.

The source prototypes are Schedule:Year -> Schedule:Week:Daily -> Schedule:Day:Interval (NOT
Schedule:Compact, which is what the injector writes), so both forms are parsed.

Usage (on the cluster, under sbatch):
    python 3rdJ_09F_daytype_loss.py <injected.idf> <source.idf>
"""
from __future__ import annotations

import calendar
import re
import sys
from collections import defaultdict

YEAR = 2006          # the run period the smoke cells simulated
DAYS = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")


def read_idf(path):
    """{OBJTYPE: {NAME_UPPER: [fields after the name]}}, comments stripped."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"!.*?$", "", txt, flags=re.M)
    out = defaultdict(dict)
    for chunk in txt.split(";"):
        fields = [f.strip() for f in chunk.split(",")]
        fields = [f for f in fields if f != ""]
        if len(fields) < 2:
            continue
        out[fields[0].upper()][fields[1].upper()] = fields[2:]
    return out


def day_interval_to_24(fields):
    """Schedule:Day:Interval fields (after Name) -> 24 hourly values.

    Fields: TypeLimits, Interpolate, then (Time, Value) pairs. `Until HH:MM` means the value holds
    up to and including that time, so it covers hours [prev_end, end).
    """
    pairs = fields[2:]
    arr = [None] * 24
    prev = 0
    for i in range(0, len(pairs) - 1, 2):
        m = re.match(r"(\d{1,2}):(\d{2})", pairs[i].strip())
        if not m:
            continue
        end = int(m.group(1)) + (1 if int(m.group(2)) > 0 else 0)
        val = float(pairs[i + 1])
        for h in range(prev, min(end, 24)):
            arr[h] = val
        prev = min(end, 24)
    last = 0.0
    for h in range(24):
        if arr[h] is None:
            arr[h] = last
        else:
            last = arr[h]
    return arr


def day_hourly_to_24(fields):
    vals = [float(x) for x in fields[1:25]]
    return vals + [vals[-1]] * (24 - len(vals))


def day_profile(idf, name):
    n = name.upper()
    if n in idf.get("SCHEDULE:DAY:INTERVAL", {}):
        return day_interval_to_24(idf["SCHEDULE:DAY:INTERVAL"][n])
    if n in idf.get("SCHEDULE:DAY:HOURLY", {}):
        return day_hourly_to_24(idf["SCHEDULE:DAY:HOURLY"][n])
    return None


def year_profiles(idf, sched_name):
    """Schedule:Year -> {weekday_index 0..6: [24 values]} using its FIRST week rule.

    Every prototype here uses one Jan1-Dec31 week rule; if a schedule had more, this reads the
    first and that limitation is printed rather than hidden.
    """
    y = idf.get("SCHEDULE:YEAR", {}).get(sched_name.upper())
    if y is None:
        return None, 0
    n_rules = max(0, (len(y) - 1) // 5)
    week = y[1] if len(y) > 1 else None
    w = idf.get("SCHEDULE:WEEK:DAILY", {}).get((week or "").upper())
    if w is None:
        return None, n_rules
    # Schedule:Week:Daily order: Sunday, Monday..Saturday, Holiday, SummerDD, WinterDD, CD1, CD2
    prof = {}
    for i, _d in enumerate(DAYS):
        p = day_profile(idf, w[i]) if i < len(w) else None
        if p is None:
            return None, n_rules
        prof[i] = p
    return prof, n_rules


def compact_profiles(fields):
    """Schedule:Compact fields (after Name) -> {weekday_index: [24 values]}."""
    blocks, cur = {}, []
    i = 0
    while i < len(fields):
        f = fields[i]
        low = f.lower()
        if low.startswith("through"):
            i += 1
            continue
        if low.startswith("for"):
            spec = f.split(":", 1)[1] if ":" in f else ""
            cur = [s.lower() for s in re.split(r"[\s,]+", spec) if s]
            for c in cur:
                blocks.setdefault(c, [None] * 24)
            i += 1
            continue
        if low.startswith("until"):
            m = re.match(r"(\d{1,2}):(\d{2})", f.split(":", 1)[1].strip())
            end = (int(m.group(1)) + (1 if int(m.group(2)) > 0 else 0)) if m else 24
            val = float(fields[i + 1])
            for c in cur:
                arr = blocks[c]
                for h in range(min(end, 24)):
                    if arr[h] is None:
                        arr[h] = val
            i += 2
            continue
        i += 1
    for arr in blocks.values():
        last = 0.0
        for h in range(24):
            if arr[h] is None:
                arr[h] = last
            else:
                last = arr[h]

    def pick(*names):
        for n in names:
            if n in blocks:
                return blocks[n]
        return blocks.get("alldays") or blocks.get("allotherdays")

    wd = pick("weekdays", "weekday")
    sat = pick("saturday", "weekends", "weekend")
    sun = pick("sunday", "weekends", "weekend")
    if wd is None or sat is None or sun is None:
        return None
    return {0: sun, 1: wd, 2: wd, 3: wd, 4: wd, 5: wd, 6: sat}


def annual_mean(prof):
    tot = s = 0
    for mth in range(1, 13):
        for day in range(1, calendar.monthrange(YEAR, mth)[1] + 1):
            idx = (calendar.weekday(YEAR, mth, day) + 1) % 7   # Mon=0 -> our Sunday=0 indexing
            s += sum(prof[idx]) / 24.0
            tot += 1
    return s / tot


def main():
    inj_path, src_path = sys.argv[1], sys.argv[2]
    inj, src = read_idf(inj_path), read_idf(src_path)
    print(f"injected : {inj_path}")
    print(f"source   : {src_path}")
    print(f"  source Schedule:Year={len(src.get('SCHEDULE:YEAR', {}))} "
          f"Week:Daily={len(src.get('SCHEDULE:WEEK:DAILY', {}))} "
          f"Day:Interval={len(src.get('SCHEDULE:DAY:INTERVAL', {}))}")

    inj_we, src_we = inj.get("WATERUSE:EQUIPMENT", {}), src.get("WATERUSE:EQUIPMENT", {})

    def sched_of(rec):
        # WaterUse:Equipment after Name: EndUseSubcat, PeakFlowRate, FlowRateFractionSchedule, ...
        return rec[2].strip() if len(rec) > 2 else ""

    print(f"\n{'object':<50}{'source prototype':<40}{'src':>8}{'new':>8}{'predicted':>11}  Sat==Sun?")
    rows = []
    for nm, rec in sorted(inj_we.items()):
        new_s = sched_of(rec)
        old_s = sched_of(src_we.get(nm, []))
        sp, n_rules = year_profiles(src, old_s)
        np_ = inj.get("SCHEDULE:COMPACT", {}).get(new_s.upper())
        npf = compact_profiles(np_) if np_ is not None else None
        if sp is None or npf is None:
            print(f"  {nm[:48]:<50}{old_s[:38]:<40}{'--':>8}{'--':>8}{'--':>11}  "
                  f"unparsed (src_year={sp is not None} new_compact={npf is not None})")
            continue
        sm, nmn = annual_mean(sp), annual_mean(npf)
        same = "YES" if [round(x, 6) for x in sp[6]] == [round(x, 6) for x in sp[0]] else "no"
        pred = (nmn / sm) if sm else float("nan")
        rows.append((nm, old_s, pred, same, n_rules))
        print(f"  {nm[:48]:<50}{old_s[:38]:<40}{sm:>8.4f}{nmn:>8.4f}{pred:>11.4f}  {same}"
              + ("" if n_rules <= 1 else f"  [{n_rules} week rules, only the first was read]"))

    print("\n--- by source prototype ---")
    by = defaultdict(list)
    for nm, s, pred, same, _ in rows:
        by[(s, same)].append(pred)
    for (s, same), preds in sorted(by.items()):
        print(f"  {s[:52]:<54} n={len(preds):>3}  predicted {min(preds):.4f}..{max(preds):.4f}"
              f"   Sat==Sun: {same}")

    print("\nCompare the `predicted` column against the measured energy ratios. Agreement means the "
          "residuals are the 2-day-type reconstruction and NOT FINDING 8; disagreement refutes "
          "this hypothesis and it is recorded as refuted.")


if __name__ == "__main__":
    main()
