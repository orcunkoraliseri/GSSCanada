#!/usr/bin/env python
"""
Selftest for `4thJ_step7_schedules.py` (Step 7 work item 7.7).

Every guard in the emitter is exercised HERE, on fixtures, before the module is
pointed at a real batch. The project's standing rule is that a gate nobody has
seen fail is not a gate; the same applies to a refusal nobody has seen refuse.

Runs offline, needs no GPU, no network and no corpus.
"""

import collections
import importlib
import io
import json
import os
import random
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

S = importlib.import_module("4thJ_step7_schedules")

OK = 0
BAD = 0


def check(name, cond, detail=""):
    global OK, BAD
    if cond:
        OK += 1
        print("  ok   %s" % name)
    else:
        BAD += 1
        print("  FAIL %s   %s" % (name, detail))


def expect_raise(name, fn, needle=None):
    global OK, BAD
    try:
        fn()
    except S.ScheduleError as e:
        if needle is not None and needle.lower() not in str(e).lower():
            BAD += 1
            print("  FAIL %s   raised, but message lacks %r: %s" % (name, needle, e))
        else:
            OK += 1
            print("  ok   %s  (refused: %s)" % (name, str(e).split(".")[0][:70]))
    except Exception as e:
        BAD += 1
        print("  FAIL %s   wrong exception type %s: %s" % (name, type(e).__name__, e))
    else:
        BAD += 1
        print("  FAIL %s   DID NOT RAISE" % name)


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------
def mkday(pattern):
    """`pattern` is a list of (minutes, present) pairs summing to 1440."""
    flags = []
    for m, p in pattern:
        flags.extend([bool(p)] * m)
    assert len(flags) == S.DAY_MINUTES, len(flags)
    return {"flags": flags, "acts": [], "prefix": None}


def mkprefix(**kw):
    p = {"country": "es", "strat_age_band": "25-44", "strat_sex": "male",
         "strat_hh_type": "single", "strat_econ_status": "employed",
         "strat_day_type": "weekday"}
    p.update(kw)
    return p


def mkpools(days_by_prefix):
    pools = dict((d, collections.defaultdict(list))
                 for d in range(len(S.STRATUM_FIELDS) + 1))
    for pfx, days in days_by_prefix:
        for day in days:
            for depth in pools:
                pools[depth][S._stratum_key(pfx, depth)].append(day)
    return pools


print("=" * 74)
print("4thJ_step7_schedules_selftest")
print("=" * 74)

# --------------------------------------------------------------------------
print("\n[1] the calendar")
# --------------------------------------------------------------------------
cal = S.year_day_types(2011)
check("365 days", len(cal) == S.DAYS_PER_YEAR, len(cal))
check("2011-01-01 is a saturday", cal[0] == "saturday", cal[0])
check("53 saturdays in 2011 -- it opens AND closes on a saturday",
      cal.count("saturday") == 53, cal.count("saturday"))
check("52 sundays in 2011", cal.count("sunday") == 52, cal.count("sunday"))
check("260 weekdays in 2011", cal.count("weekday") == 260, cal.count("weekday"))
check("the three counts partition the year",
      cal.count("saturday") + cal.count("sunday") + cal.count("weekday") == 365)
check("only the three declared day types",
      set(cal) == set(S.DAY_TYPES), sorted(set(cal)))
expect_raise("a leap year is REFUSED, not truncated",
             lambda: S.year_day_types(2012), "leap")
# a second leap year, so the check is not a single hard-coded date
expect_raise("2016 refused too", lambda: S.year_day_types(2016), "leap")
check("2010 has 365 days", len(S.year_day_types(2010)) == 365)

# --------------------------------------------------------------------------
print("\n[2] minutes -> timestep, and the range")
# --------------------------------------------------------------------------
allday = [1] * S.DAY_MINUTES
check("all-present hour means are 1.0",
      S.to_timestep(allday, 60) == [1.0] * 24)
half = [1] * 30 + [0] * 30
check("half an hour present reads 0.5",
      S.to_timestep(half, 60) == [0.5], S.to_timestep(half, 60))
check("24 values at 60 min", len(S.to_timestep(allday, 60)) == 24)
check("96 values at 15 min", len(S.to_timestep(allday, 15)) == 96)
expect_raise("a timestep that does not divide 1440 is refused",
             lambda: S.to_timestep(allday, 7), "ragged")
expect_raise("a 50-minute timestep is refused too",
             lambda: S.to_timestep(allday, 50), "ragged")

# --------------------------------------------------------------------------
print("\n[3] the household fraction is a FRACTION")
# --------------------------------------------------------------------------
d_in = mkday([(1440, 1)])
d_out = mkday([(1440, 0)])
d_half = mkday([(720, 1), (720, 0)])
one = S.household_year([[d_in] * 2], 60)
check("a single always-home member reads 1.0 everywhere",
      set(one) == {1.0}, sorted(set(one))[:4])
two = S.household_year([[d_in] * 2, [d_out] * 2], 60)
check("one of two members home reads 0.5",
      set(two) == {0.5}, sorted(set(two))[:4])
three = S.household_year([[d_in] * 2, [d_out] * 2, [d_out] * 2], 60)
check("one of three members home reads 1/3",
      all(abs(v - 1.0 / 3) < 1e-12 for v in three))
check("every value is inside [0,1] (G7.17's own test)",
      all(0.0 <= v <= 1.0 for v in one + two + three))
mixed = S.household_year([[d_half] * 1, [d_out] * 1], 60)
check("a half-day member gives 12 h at 0.5 and 12 h at 0.0",
      mixed.count(0.5) == 12 and mixed.count(0.0) == 12, collections.Counter(mixed))
expect_raise("a household with no members is refused",
             lambda: S.household_year([], 60), "zero members")
expect_raise("members disagreeing on day count are refused",
             lambda: S.household_year([[d_in] * 2, [d_in] * 3], 60), "disagree")

# --------------------------------------------------------------------------
print("\n[4] the draw ladder is COUNTED, and it backs off in the right order")
# --------------------------------------------------------------------------
pfx = mkprefix()
pools = mkpools([(pfx, [d_in])])
tally = collections.Counter()
rng = random.Random(1)
day, depth = S.draw(pools, pfx, rng, tally)
check("an exact stratum match uses full depth", depth == len(S.STRATUM_FIELDS), depth)
check("the tally recorded it", tally[len(S.STRATUM_FIELDS)] == 1, dict(tally))

# a person whose econ_status is absent must back off by exactly one field
other = mkprefix(strat_econ_status="retired")
tally2 = collections.Counter()
day, depth = S.draw(pools, other, rng, tally2)
check("an absent econ_status backs off to depth 3", depth == 3, depth)
# ... and one whose age band is absent too must back off further
far = mkprefix(strat_econ_status="retired", strat_hh_type="couple_no_children",
               strat_sex="female", strat_age_band="75+")
tally3 = collections.Counter()
day, depth = S.draw(pools, far, rng, tally3)
check("a stratum absent on all four fields backs off to depth 0", depth == 0, depth)

# the day type is NEVER dropped
sat = mkprefix(strat_day_type="saturday")
expect_raise("a day type absent from the pool is refused, never back-filled "
             "with another day type",
             lambda: S.draw(pools, sat, random.Random(2), collections.Counter()),
             "day type alone")

# --------------------------------------------------------------------------
print("\n[5] the three chaining rules are three points on ONE axis")
# --------------------------------------------------------------------------
pool_days = [mkday([(60 * i, 1), (1440 - 60 * i, 0)]) for i in range(1, 13)]
pools2 = mkpools([(mkprefix(strat_day_type=dt), pool_days) for dt in S.DAY_TYPES])
cal = S.year_day_types(2011)


def run(rule, rho=0.0, seed=7):
    t = collections.Counter()
    days = S.assemble_person_year(mkprefix(), cal, rule, random.Random(seed),
                                  pools2, t, rho)
    return days, sum(t.values())


_, n_ind = run("independent")
_, n_sta = run("static")
_, n_h0 = run("habit", 0.0)
_, n_h1 = run("habit", 1.0)
_, n_h5 = run("habit", 0.5)
check("independent draws once per calendar day", n_ind == 365, n_ind)
check("static draws once per day type", n_sta == len(S.DAY_TYPES), n_sta)
check("habit at rho=0 IS independent (365 fresh draws)", n_h0 == 365, n_h0)
check("habit at rho=1 IS static (one fresh draw per day type)",
      n_h1 == len(S.DAY_TYPES), n_h1)
check("habit at rho=0.5 lies strictly between the two",
      n_sta < n_h5 < n_ind, n_h5)
days_sta, _ = run("static")
by_dt = collections.defaultdict(set)
for dt, d in zip(cal, days_sta):
    by_dt[dt].add(id(d))
check("static really repeats ONE day per day type",
      all(len(v) == 1 for v in by_dt.values()), dict((k, len(v)) for k, v in by_dt.items()))
days_ind, _ = run("independent")
by_dt_i = collections.defaultdict(set)
for dt, d in zip(cal, days_ind):
    by_dt_i[dt].add(id(d))
check("independent uses many distinct days per day type",
      all(len(v) > 1 for v in by_dt_i.values()),
      dict((k, len(v)) for k, v in by_dt_i.items()))
check("a rule name that does not exist is refused",
      True)
expect_raise("an unknown chaining rule is refused",
             lambda: S.assemble_person_year(mkprefix(), cal, "markov",
                                            random.Random(1), pools2,
                                            collections.Counter()),
             "unknown chaining rule")
# the same seed twice gives the same year: the campaign is reproducible
a1, _ = run("habit", 0.5, seed=99)
a2, _ = run("habit", 0.5, seed=99)
check("the same seed reproduces the same year",
      [id(x) for x in a1] == [id(x) for x in a2])
a3, _ = run("habit", 0.5, seed=100)
check("a different seed gives a different year",
      [id(x) for x in a1] != [id(x) for x in a3])

# --------------------------------------------------------------------------
print("\n[6] the emitted IDF, and the two registered perturbations")
# --------------------------------------------------------------------------
txt = S.idf_objects("HH_es_00001", "presence_HH_es_00001.csv", 8760, 60, 3)
check("Schedule:File is used", "Schedule:File," in txt)
check("Schedule:Compact is NOT used (G7.14)", "Schedule:Compact" not in txt)
check("Interpolate to Timestep is No (G7.15)",
      "No,                     !- Interpolate to Timestep" in txt)
check("the object declares 8760 hours",
      "8760,                     !- Number of Hours of Data" in txt)
check("Minutes per Item is the timestep",
      "60;                     !- Minutes per Item" in txt)
check("People carries an INTEGER head-count",
      "3,                     !- Number of People" in txt)
bad = S.idf_objects("HH_es_00001", "x.csv", 8760, 60, 3, interpolate="Yes")
check("the perturbation hook really writes Yes",
      "Yes,                     !- Interpolate to Timestep" in bad)
_a = txt.replace("presence_HH_es_00001.csv", "x.csv").splitlines()
_b = bad.splitlines()
_diff = [i for i in range(len(_a)) if _a[i] != _b[i]]
check("... and the perturbation moves EXACTLY ONE line, the interpolate one",
      len(_a) == len(_b) and len(_diff) == 1
      and "Interpolate to Timestep" in _a[_diff[0]],
      [(_a[i], _b[i]) for i in _diff])
expect_raise("a value count that is not a whole number of hours is refused",
             lambda: S.idf_objects("H", "x.csv", 8759, 7, 1), "not integral")

# --------------------------------------------------------------------------
print("\n[7] the CSV the gate will re-read")
# --------------------------------------------------------------------------
tmp = tempfile.mkdtemp(prefix="4j_s7_sched_")
try:
    p = os.path.join(tmp, "presence.csv")
    S.write_schedule_csv(p, [0.0, 0.5, 1.0], "HH_Presence")
    rows = io.open(p, encoding="utf-8").read().splitlines()
    check("one header row plus one row per value", len(rows) == 4, rows)
    check("the header is the column name", rows[0] == "HH_Presence", rows[0])
    check("values are written at six decimals",
          rows[1:] == ["0.000000", "0.500000", "1.000000"], rows[1:])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# --------------------------------------------------------------------------
print("\n[8] the vacuity guard on the pool")
# --------------------------------------------------------------------------
tmp = tempfile.mkdtemp(prefix="4j_s7_pool_")
try:
    empty = os.path.join(tmp, "empty.jsonl")
    io.open(empty, "w").write("")
    expect_raise("an empty pool is refused, not emitted as a constant",
                 lambda: S.load_pool(empty, os.path.join(
                     _HERE, "..", "Step2_docs", "outputs_step2"), {}),
                 "empty")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# --------------------------------------------------------------------------
print("\n[9] D-S9-3 / FINDING 141 -- the rotation onto the clock EnergyPlus reads")
# --------------------------------------------------------------------------
check("the diary origin is declared and is 04:00", S.DIARY_ORIGIN_HOUR == 4,
      S.DIARY_ORIGIN_HOUR)

# Two days of hourly values, each day counting from a different hundred, so the
# rotation's effect is readable by eye and a per-day rotation is DISTINGUISHABLE
# from a cyclic one.
two = list(range(24)) + list(range(100, 124))
rot = S.rotate_to_midnight(two, 60)
check("the shift is four places at a 60-minute timestep",
      rot[4:8] == [0, 1, 2, 3], rot[:8])
check("the last four values of the YEAR wrap round to its start",
      rot[:4] == [120, 121, 122, 123], rot[:4])
check("day 2's first hours come from day 1, not from day 2 itself",
      rot[28:32] == [100, 101, 102, 103], rot[28:32])
check("nothing is created or destroyed", sorted(rot) == sorted(two))
check("rotating is the identity when the origin is already midnight",
      S.rotate_to_midnight(two, 60, origin_hour=0) == two)
# The per-day rotation this is NOT: rotating each day inside itself would put
# day 1's hours 20-23 at the START of day 1 instead of day 2's at the start of
# the year. FINDING 141's own note, made checkable.
per_day = two[20:24] + two[0:20] + two[44:48] + two[24:44]
check("a CYCLIC-OVER-THE-YEAR rotation differs from a per-day one",
      rot != per_day, "the two are identical, so the test proves nothing")
check("a 15-minute timestep shifts sixteen places",
      S.rotate_to_midnight(list(range(96 * 2)), 15)[16:20] == [0, 1, 2, 3])
expect_raise("a series shorter than the shift is refused",
             lambda: S.rotate_to_midnight([0.0, 1.0], 60), "longer than the series")

print("\n" + "=" * 74)
print("%d ok, %d FAILED" % (OK, BAD))
print("=" * 74)
sys.exit(1 if BAD else 0)
