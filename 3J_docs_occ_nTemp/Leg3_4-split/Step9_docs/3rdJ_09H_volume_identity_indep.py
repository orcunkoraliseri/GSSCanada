#!/usr/bin/env python3
"""Test the T9-13 volume identity against EnergyPlus's OWN reported volume.

Why this exists -- and why it is not the same test as 3rdJ_09E_dhw_identity_probe.py.

09E forms a RATIO of two numbers our own IDF reader produced (injected / uninjected). That is
vacuous-gate kind #9: if the reader misreads a `Schedule:Compact`, both sides move together and the
ratio still looks right. The 0.9647 identity figure -- the one number quoted as proof T9-13's
arithmetic is correct -- comes from exactly that construction.

Arm H requests `Water Use Equipment Total Volume`, so EnergyPlus now reports the volume it actually
integrated from the schedule it was actually handed: a reference our parser cannot corrupt. This
script compares an ABSOLUTE prediction against it, summed over ALL WaterUse:Equipment objects and
ALL channel columns (which removes the channel-attribution step, so a disagreement is the volume
arithmetic and not the aggregator's zone-prefix rules).

PRE-REGISTERED 2026-08-03, before the first run:
    PASS  |predicted/reported - 1| <= 3 %      FAIL  anything larger

RESULT, 2026-08-03: **FAIL** on both cells -- 09E-reader prediction came in at -36.9 %
(Y2022__Tall__MTL) and -38.5 % (B_opt__Tall__MTL). The FAIL stands in the record. The cause was
then located and it is **not** T9-13's arithmetic; it is 09E's `compact_profiles()`:

    For: Weekdays Saturday Sunday Holidays SummerDesignDay WinterDesignDay AllOtherDays

is ONE `For:` field naming SEVEN day types. 09E resolves it with a first-substring-match chain
(`if "WEEKEND"/"SATURDAY"/"SUNDAY" in up -> weekend, elif ... -> all, else -> weekday`), so the
whole field collapses onto the WEEKEND bucket and the weekday profile stays 0.0. The two hotel
laundry objects use exactly that form -- and `Laundry Service Water Use 30.6gpm 180F` is the single
largest DHW draw in the tower. 09E reads them at 2/7 of their true volume (mean 0.0833 vs 0.2917,
a factor 3.5). A milder face of the same bug: `For: Saturday` followed by `For: Sunday Holidays
AllOtherDays` -- the second block also matches the weekend test and OVERWRITES Saturday, so
post-FINDING-9 Sat != Sun weekends are read as Sunday everywhere (office/retail, a few per cent).

Scope of the damage, checked rather than assumed: 09E's `volume_table()` filters on RESID_TOKENS
("APARTMENT", "DWELL", "HIGHRISE", "RESI"), so it never reads a laundry or a restroom object, and
residential schedules reproduce EnergyPlus to 5 significant figures (see below). **The published
0.9647 residential figure is therefore unaffected.** What is unsafe is using 09E's reader on
commercial objects, which nothing had done until this script did.

This script therefore reports BOTH readers:
  * `09E reader`       -- the pre-registered gate, kept so the FAIL stays visible
  * `corrected reader` -- resolves a `For:` field into the FULL SET of day types it names, keeps
                          Saturday and Sunday apart, honours `AllOtherDays` as "every day type not
                          yet assigned in this Through period", and weights by the real 2022 day
                          counts (260 weekdays / 53 Saturdays / 52 Sundays) instead of 5/2.

    python 3rdJ_09H_volume_identity_indep.py <cell_dir> [<cell_dir> ...]
"""
import importlib.util
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.03
SEC_PER_YEAR = 8760 * 3600

# Day-type counts are READ FROM THE IDF's RunPeriod, not assumed. The first draft of this script
# hard-coded the 2022 calendar (Jan 1 = Saturday) because the cells are named `Y2022`; the RunPeriod
# in these IDFs is actually `2006 ... Day of Week for Start Day = Sunday`, which swaps the Saturday
# and Sunday counts. The error was worth well under the 3 % band, but a reader that guesses its own
# calendar is exactly the kind of thing this script exists to catch in other people's code.
DEFAULT_COUNTS = (260, 52, 53)     # 2006: starts Sunday -> 53 Sundays, 52 Saturdays

CHANNELS = ["office", "retail", "hotel", "residential",
            "residential_common", "service_MEP", "unassigned"]

# The 09E reader is imported, not re-implemented: the point is to test THAT reader against an
# external reference. Re-writing it here would test a different reader and prove nothing about
# 0.9647.
_spec = importlib.util.spec_from_file_location(
    "probe09e", os.path.join(HERE, "3rdJ_09E_dhw_identity_probe.py"))
_p09e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p09e)


# --------------------------------------------------------------------------------------------
# corrected Schedule:Compact reader
# --------------------------------------------------------------------------------------------
# The three keys that carry annual volume. Holidays are folded into their calendar day type:
# EnergyPlus only raises the `Holiday` day type when RunPeriodControl:SpecialDays exists, and these
# IDFs define none -- so a `For: Holidays` block is unreachable and must NOT be given a weight of
# its own, or it would dilute the mean.
DAY_KEYS = ("wd", "sat", "sun")


_DOW = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def day_counts(O):
    """(n_weekday, n_saturday, n_sunday) for the run period this IDF actually simulates.

    Also checks that no Holiday day type can occur: `Use Weather File Holidays and Special Days`
    and `Apply Weekend Holiday Rule` are both `No` in these IDFs and there is no
    RunPeriodControl:SpecialDays object, so a `For: Holidays` block is unreachable and must carry no
    weight of its own. Returns (counts, note).
    """
    rp = O.get("RUNPERIOD", [])
    if not rp:
        return DEFAULT_COUNTS, "no RunPeriod found -- using default 2006 calendar"
    f = rp[0]
    try:
        year = int(float(f[4]))
    except (ValueError, IndexError):
        year = 2006
    start = ""
    for tok in f[5:]:
        if str(tok).strip().upper() in _DOW:
            start = str(tok).strip().upper()
            break
    if not start:
        return DEFAULT_COUNTS, "RunPeriod names no start day -- using default"
    leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    ndays = 366 if leap else 365
    i0 = _DOW.index(start)
    n = [0, 0, 0]      # weekday, saturday, sunday
    for d in range(ndays):
        dow = (i0 + d) % 7
        n[0 if dow < 5 else (1 if dow == 5 else 2)] += 1
    holidays = "no holiday day type (SpecialDays absent)"
    if O.get("RUNPERIODCONTROL:SPECIALDAYS"):
        holidays = ("SpecialDays PRESENT -- a `For: Holidays` block would be reachable and this "
                    "reader does not weight it")
    return tuple(n), "RunPeriod %d starting %s, %d days; %s" % (year, start.title(), ndays, holidays)


def _for_targets(field, assigned):
    """Day-type keys named by one `For:` field. Scans EVERY token, unlike 09E's first-match chain.

    `assigned` is the set already covered earlier in this Through period, which is what makes
    `AllOtherDays` meaningful; it is also what makes the ORDER of For: blocks matter, exactly as it
    does in EnergyPlus.
    """
    up = field.upper()
    keys = set()
    if "ALLDAYS" in up or "ALL DAYS" in up:
        keys |= set(DAY_KEYS)
    if "WEEKDAY" in up:
        keys.add("wd")
    if "WEEKEND" in up:
        keys |= {"sat", "sun"}
    if "SATURDAY" in up:
        keys.add("sat")
    if "SUNDAY" in up:
        keys.add("sun")
    if "ALLOTHERDAY" in up:
        keys |= (set(DAY_KEYS) - assigned)
    # A bare `For: Holidays` / `For: SummerDesignDay` with no calendar day type names nothing that
    # occurs in the run period; returning an empty set is correct, not a parse failure.
    return keys


def compact_mean(fields, counts=DEFAULT_COUNTS):
    """Annual mean fraction of a Schedule:Compact, honouring every Through period.

    `counts` is (n_weekday, n_saturday, n_sunday) for the simulated run period -- read from the
    IDF's RunPeriod by day_counts(), never assumed from the cell name.

    Returns None if the object is not a Schedule:Compact form this reader understands.
    """
    n_wd, n_sat, n_sun = counts
    n_days = float(n_wd + n_sat + n_sun)
    # per Through period: {day key: 24h list}, plus the period's end day-of-year
    periods = []
    cur = None
    assigned = set()
    targets = []
    until = 0
    prev = 0
    for tok in fields[3:]:
        t = tok.strip()
        if not t:
            continue
        up = t.upper()
        if up.startswith("THROUGH"):
            m = re.search(r"(\d+)\s*/\s*(\d+)", t)
            cur = {"end": (int(m.group(1)), int(m.group(2))) if m else (12, 31),
                   "days": {}}
            periods.append(cur)
            assigned = set()
            targets = []
            continue
        if up.startswith("FOR"):
            if cur is None:
                return None
            targets = sorted(_for_targets(t, assigned))
            assigned |= set(targets)
            for k in targets:
                cur["days"].setdefault(k, [0.0] * 24)
            prev = 0
            continue
        m = re.match(r"UNTIL:\s*(\d+):(\d+)", up)
        if m:
            until = int(m.group(1)) * 60 + int(m.group(2))
            continue
        try:
            v = float(t)
        except ValueError:
            continue
        for k in targets:
            arr = cur["days"][k]
            for h in range(24):
                if prev <= h * 60 < until:
                    arr[h] = v
        prev = until

    if not periods:
        return None

    # Day-of-year weights. Within a Through period the weekday/Sat/Sun split is taken as the
    # whole-year split scaled by the period's length -- exact to well under the 3 % band and it
    # avoids pretending to a day-by-day calendar the schedule does not resolve.
    cum = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    total, wsum = 0.0, 0.0
    prev_doy = 0
    for per in periods:
        mth, dy = per["end"]
        doy = cum[max(0, min(11, mth - 1)) - 1] + dy if mth > 1 else dy
        ndays = max(0, doy - prev_doy)
        prev_doy = doy
        if ndays == 0:
            continue
        share = ndays / n_days
        for key, n in (("wd", n_wd), ("sat", n_sat), ("sun", n_sun)):
            arr = per["days"].get(key)
            if arr is None:
                continue          # this day type is genuinely unscheduled -> contributes 0
            w = n * share
            total += (sum(arr) / 24.0) * w
            wsum += w
    if wsum <= 0:
        return None
    # wsum is the number of days actually covered; dividing by n_days (not wsum) is deliberate --
    # an uncovered day type really does draw nothing and must pull the annual mean down.
    return total / n_days


def _compact_profiles_as_published(f):
    """VERBATIM copy of 09E's `compact_profiles` as it stood when the -36.89 % FAIL was recorded.

    09E itself has since been given a guard that REFUSES a multi-day-type `For:` field rather than
    mis-reading it. That guard is the right fix for 09E, but it would make the recorded FAIL
    irreproducible from this script -- the offending objects would be dropped instead of under-read,
    and the historical number is part of the record. So the as-published behaviour is frozen here,
    where its only job is to keep reproducing the miss beside the fix.
    """
    wd, we = [0.0] * 24, [0.0] * 24
    cur, prev, seen_through, until = None, 0, 0, 0
    for tok in f[3:]:
        t = tok.strip()
        if not t:
            continue
        up = t.upper()
        if up.startswith("THROUGH"):
            seen_through += 1
            if seen_through > 1:
                break
            continue
        if up.startswith("FOR"):
            prev = 0
            if "WEEKEND" in up or "SATURDAY" in up or "SUNDAY" in up:
                cur = "we"
            elif "ALLDAY" in up or "ALLOTHERDAY" in up or "ALL DAY" in up:
                cur = "all"
            else:
                cur = "wd"
            continue
        m = re.match(r"UNTIL:\s*(\d+):(\d+)", up)
        if m:
            until = int(m.group(1)) * 60 + int(m.group(2))
            continue
        try:
            v = float(t)
        except ValueError:
            continue
        for h in range(24):
            if prev <= h * 60 < until:
                if cur in ("wd", "all"):
                    wd[h] = v
                if cur in ("we", "all"):
                    we[h] = v
        prev = until
    return wd, we


def predict(idf_path):
    """Annual m3 predicted by the T9-13 identity, under both readers."""
    O = _p09e.parse(idf_path)
    resolve = _p09e.build_resolver(O)
    comp = {f[1].upper(): f for f in O.get("SCHEDULE:COMPACT", [])}
    counts, cal_note = day_counts(O)

    v09e, vfix, n_obj, n_unres, n_fallback = 0.0, 0.0, 0, 0, 0
    worst = []
    for f in O.get("WATERUSE:EQUIPMENT", []):
        n_obj += 1
        try:
            peak = float(f[3])
        except (ValueError, IndexError):
            peak = 0.0
        sch = (f[4] if len(f) > 4 else "").upper()
        cf = comp.get(sch)
        if cf is not None:
            wd, we = _compact_profiles_as_published(cf)
            mfix = compact_mean(cf, counts)
        else:
            # not a Schedule:Compact -- both readers fall back to 09E's Schedule:Year path
            wd, we, _prov = resolve(sch)
            mfix = None
        if wd is None:
            n_unres += 1
            continue
        m9 = (5 * sum(wd) / 24.0 + 2 * sum(we) / 24.0) / 7.0
        if mfix is None:
            n_fallback += 1
            mfix = m9
        v09e += peak * m9 * SEC_PER_YEAR
        vfix += peak * mfix * SEC_PER_YEAR
        if m9 > 0 and abs(mfix / m9 - 1.0) > 0.10:
            worst.append((f[1], m9, mfix, mfix / m9, peak * (mfix - m9) * SEC_PER_YEAR))
    worst.sort(key=lambda r: -abs(r[4]))
    return v09e, vfix, n_obj, n_unres, n_fallback, worst, cal_note


def run(cell_dir):
    name = os.path.basename(cell_dir.rstrip("/\\"))
    print("=" * 84)
    print("CELL %s" % name)
    print("=" * 84)

    vol_p = os.path.join(cell_dir, "dhw_volume_hourly.csv")
    idf = None
    for n in sorted(os.listdir(cell_dir)):
        if n.endswith(".idf") and "injected" in n:
            idf = os.path.join(cell_dir, n)
            break
    if not os.path.isfile(vol_p) or idf is None:
        print("  SKIP: need both dhw_volume_hourly.csv and an injected .idf")
        return None, None

    vol = pd.read_csv(vol_p)
    have = ["dhwvol_" + c for c in CHANNELS if "dhwvol_" + c in vol.columns]
    reported = float(np.nansum(vol[have].to_numpy()))

    v09e, vfix, n_obj, n_unres, n_fb, worst, cal_note = predict(idf)
    print("  calendar           : %s" % cal_note)
    print("  WaterUse:Equipment : %d objects, %d schedule-unresolved, %d not Schedule:Compact"
          % (n_obj, n_unres, n_fb))
    print("  reported  (E+)     : %12.1f m3" % reported)
    if reported <= 0:
        print("  FAIL: reported volume is zero -- cannot form a ratio")
        return False, False

    out = []
    for label, pred in (("09E reader      ", v09e), ("corrected reader", vfix)):
        rel = pred / reported - 1.0
        ok = abs(rel) <= TOL
        print("  predicted, %s: %12.1f m3   ratio %.4f   rel %+7.2f %%   [%s]"
              % (label, pred, pred / reported, 100 * rel, "PASS" if ok else "FAIL"))
        out.append(ok)

    if worst:
        print("\n  objects where the two readers disagree by >10 % (largest volume effect first):")
        print("    %-46s %9s %9s %7s %11s" % ("object", "mean_09E", "mean_fix", "ratio", "dV m3/yr"))
        for nm, m9, mf, r, dv in worst[:8]:
            print("    %-46s %9.4f %9.4f %7.3f %+11.1f" % (nm[:46], m9, mf, r, dv))

    print("\n  per-channel reported volume (informational -- attribution is our convention):")
    for c in CHANNELS:
        col = "dhwvol_" + c
        if col in vol.columns:
            v = float(np.nansum(vol[col].to_numpy()))
            if v > 0:
                print("    %-20s %12.1f m3" % (c, v))
    return out[0], out[1]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    rows = []
    for d in sys.argv[1:]:
        a, b = run(d)
        rows.append((os.path.basename(d.rstrip("/\\")), a, b))
        print("")
    print("=" * 84)
    print("T9-13 VOLUME IDENTITY vs ENERGYPLUS")
    print("  %-28s %-18s %s" % ("cell", "09E reader", "corrected reader"))
    for nm, a, b in rows:
        f = lambda v: "skipped" if v is None else ("PASS" if v else "FAIL")
        print("  %-28s %-18s %s" % (nm, f(a), f(b)))
    tested = [b for _, _, b in rows if b is not None]
    print("=" * 84)
    sys.exit(0 if tested and all(tested) else 1)


if __name__ == "__main__":
    main()
