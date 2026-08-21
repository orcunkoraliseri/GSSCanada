"""
Coverage audit of the probability table BuildOcc v1.0.0 ships and samples from.

    pip install buildocc
    python 01_grounding_table_coverage.py

No LLM calls, no API key, no network. Runs in under a second.

What it does
------------
`occupant_agent/data/time_at_activity.csv` is the table the ActivityScheduler
turns into P(category | stratum, day_type, hour). Its `weighted_pct` column
should total 100.0 within every (stratum, day_type, hour) cell, because the
eight categories partition the day.

This script totals it, and cross-checks the result against the *other* shipped
table, `time_of_day_distributions.csv`, which describes the same respondents.
"""
import collections
import csv
from pathlib import Path

DATA = Path(__import__("occupant_agent").__file__).parent / "data"
CATS = ["sleeping", "work", "food_prep", "laundry", "tv", "eating", "exercise", "other"]


def coverage():
    rows = list(csv.DictReader(open(DATA / "time_at_activity.csv", encoding="utf-8")))
    tot = collections.defaultdict(float)
    for r in rows:
        tot[(r["stratum"], r["day_type"], int(r["hour"]))] += float(r["weighted_pct"])

    print("A. Coverage of time_at_activity.csv, the table the scheduler samples")
    print("   (sum of weighted_pct over the 8 categories; must be 100.0)\n")
    print("   hour |   O1 wkdy   O2 wkdy   O3 wkdy   O4 wkdy |  O1 wknd   O2 wknd")
    print("   " + "-" * 68)
    for h in range(24):
        v = [tot[(s, "weekday", h)] for s in ("O1", "O2", "O3", "O4")]
        w = [tot[(s, "weekend", h)] for s in ("O1", "O2")]
        flag = ""
        if max(v + w) == 0.0:
            flag = "   <-- NO DATA AT ALL"
        elif min(v + w) < 95.0:
            flag = "   <-- incomplete"
        print("   %4d | %8.2f %9.2f %9.2f %9.2f | %8.2f %9.2f%s"
              % (h, v[0], v[1], v[2], v[3], w[0], w[1], flag))
    return tot


def sleep_profile(tot):
    rows = [r for r in csv.DictReader(open(DATA / "time_at_activity.csv", encoding="utf-8"))
            if r["stratum"] == "O1" and r["day_type"] == "weekday"]
    t = collections.defaultdict(dict)
    for r in rows:
        t[int(r["hour"])][r["category"]] = float(r["weighted_pct"])

    print("\n\nB. P(sleeping | hour) for O1 weekday, after the scheduler renormalises")
    print("   each hour to sum to 1.0\n")
    print("   hour   coverage%   P(sleep)")
    print("   " + "-" * 32)
    for h in list(range(4, 9)) + list(range(18, 24)):
        cov = sum(t[h].values())
        raw = t[h].get("sleeping", 0.0)
        print("   %4d %10.2f %10.3f%s"
              % (h, cov, raw / cov if cov else 0.0,
                 "   <-- morning, coverage complete" if h == 4 else ""))
    print("\n   Morning falls 0.898 -> 0.207 as people wake, which is correct.")
    print("   Evening never rises above 0.08. Sleep onset is absent from the table.")


def cross_check():
    rows = [r for r in csv.DictReader(open(DATA / "time_of_day_distributions.csv", encoding="utf-8"))
            if r["stratum"] == "O1" and r["category"] == "sleeping"]
    print("\n\nC. The other shipped table, time_of_day_distributions.csv:")
    print("   P(hour | sleeping) for the same O1 respondents\n")
    print("   hour   pct_of_category")
    print("   " + "-" * 40)
    ev = 0.0
    for r in sorted(rows, key=lambda x: int(x["hour"])):
        h, p = int(r["hour"]), float(r["pct_of_category"])
        if h in (4,) or h >= 18:
            print("   %4d %10.2f  %s" % (h, p, "#" * int(p)))
        if h >= 20:
            ev += p
    print("\n   %.1f%% of all O1 sleeping time starts between 20:00 and 23:59." % ev)
    print("   The table in section A puts P(sleeping) at 0.02-0.08 across those")
    print("   same hours and has no data after midnight. The two disagree.")


if __name__ == "__main__":
    print(__doc__)
    t = coverage()
    sleep_profile(t)
    cross_check()
    print("\n\nD. What the scheduler does about hours 00:00-03:59")
    print("   grounding/scheduler.py::_sample_category returns the literal string")
    print("   'sleeping' for hours 0-3 when the table is empty, with the comment")
    print("   \"ATUS extended-hour encoding limitation\". Those four hours of every")
    print("   simulated day are a hard-coded constant, not ATUS grounding.")
    print("\n   ATUS diaries run 4 a.m. to 4 a.m. (BLS User's Guide, module S4).")
    print("   Wrapping the diary day at 04:00 rather than binning on the wall clock")
    print("   should recover both the missing hours and the evening sleep onset.")
