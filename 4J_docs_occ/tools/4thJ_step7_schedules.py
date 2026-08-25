#!/usr/bin/env python
"""
4J Step 7, work item 7.7 -- EMIT SCHEDULES.

    a generated diary  ->  a presence signal  ->  a `Schedule:File` EnergyPlus
                                                  believes for 8,760 hours

WHAT THIS MODULE IS FOR
-----------------------
`G7.14`-`G7.17` have never been scored, for the plainest possible reason: the
artefact they score did not exist. This module produces it. It is deliberately
the LAST link in Step 7 and the FIRST in Step 8, and the parent validation
document says the interface between the two "is where 3J's most expensive bug
lived".

Four things are therefore refused rather than defaulted:

  1. an activity->watts mapping (there is none that is admissible -- see below);
  2. a leap year (8,784 hours is not 8,760 and the gate would catch it late);
  3. a calendar year the caller did not name;
  4. a household whose members' strata are absent from the pool with no record
     of the back-off that was used instead.

THE PRESENCE SIGNAL IS THE RULED INTERFACE. ACTIVITY-RESOLVED GAINS ARE NOT.
----------------------------------------------------------------------------
RULED: `D-S7-7` (a), 2026-08-22. Internal gains are OCCUPANCY-REDISTRIBUTED,
not activity-resolved. `4thJ_07_constrainedGeneration.md` used to say the
opposite -- schedules carry "activity-resolved internal gains, which is the
part a presence fraction throws away" -- and that line has been corrected.
`D-S8-2` item 5, ruled 2026-08-21, fixes the Step 8 interface as

    phi_int(t) = (1 - f) * 3.0  +  f * 3.0 * g(t) / mean_year(g(t))

where `g(t)` is *"the generated presence signal from `G7.13`"* -- a fraction, not
a watt. This module implements the RULED interface, and since 2026-08-22 the
step document agrees with it. It does not invent the other: `RL25` was commissioned precisely to supply an
activity-to-appliance mapping and its Part C numbers were REJECTED as unsourced,
so there is no admissible table to resolve a 3-digit HETUS activity code into a
power. Writing one here would put an invented number between our diaries and
every load in the paper.

What this module does instead is emit the presence signal AND keep each day's
activity codes in the pool, so that if the author reinstates activity-resolved
gains the mapping can be applied without regenerating anything.

THE OCCUPANT COUNT IS AN INTEGER AND THE SCHEDULE IS A FRACTION
---------------------------------------------------------------
`People` takes a design occupancy and multiplies it by a 0-1 schedule. So the
dwelling-level signal written here is

    presence_fraction(t) = (number of members present at t) / (household size)

which is in [0, 1] by construction, and `Number of People` is the integral
household size. `G7.17` checks both halves. Emitting a signal that already had
the head-count baked in would double-count it inside EnergyPlus.

`Interpolate to Timestep = No`
------------------------------
Inherited from 3J and confirmed by `RL13`. A step-wise presence signal
interpolated linearly invents fractional occupants and smears appliance peaks.
The field is written by this module and asserted by `G7.15`; it is a constant in
the code, not a parameter, because a parameter is a thing somebody eventually
sets to `Yes`.
"""

import argparse
import calendar as _calendar
import collections
import csv
import hashlib
import importlib
import io
import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

indoor = importlib.import_module("4thJ_step7_indoor")
import decoder as dec
from encoder import load_bit_positions

DAY_MINUTES = 1440
HOURS_PER_YEAR = 8760
DAYS_PER_YEAR = 365

#: The three serialised day types. Measured on the corpus: es/uk/it all carry
#: exactly these three and nothing else.
DAY_TYPES = ("weekday", "saturday", "sunday")

#: `Interpolate to Timestep`. A constant. See the module docstring.
INTERPOLATE_TO_TIMESTEP = "No"

#: The strata fields of the six-field prefix, minus `country`, most specific
#: first. The back-off ladder drops them from the RIGHT of this tuple, so
#: `strat_day_type` is never dropped -- a Saturday diary served on a Tuesday is
#: not a back-off, it is a different signal.
STRATUM_FIELDS = ("strat_age_band", "strat_sex", "strat_hh_type",
                  "strat_econ_status")

CHAINING_RULES = ("independent", "static", "habit")


class ScheduleError(ValueError):
    pass


# --------------------------------------------------------------------------
# calendar
# --------------------------------------------------------------------------
def year_day_types(year):
    """The 365 day types of `year`, in order, starting 1 January.

    Leap years are REFUSED, not truncated. 8,760 is the number `G7.16` and every
    EnergyPlus `Schedule:File` in this project expect, and a February with 29
    days silently shifts every weekend after it by one day for the rest of the
    year -- exactly the kind of error that produces a plausible signal.
    """
    if _calendar.isleap(year):
        raise ScheduleError(
            "%d is a leap year: 366 days = 8,784 hours, not %d. Refused rather "
            "than truncated -- dropping 29 February would shift every weekend "
            "after it by one day and the schedule would still look plausible."
            % (year, HOURS_PER_YEAR))
    out = []
    for month in range(1, 13):
        for day in range(1, _calendar.monthrange(year, month)[1] + 1):
            wd = _calendar.weekday(year, month, day)      # Mon=0 .. Sun=6
            out.append("saturday" if wd == 5 else "sunday" if wd == 6 else "weekday")
    if len(out) != DAYS_PER_YEAR:
        raise ScheduleError("calendar produced %d days" % len(out))
    return out


# --------------------------------------------------------------------------
# the pool of generated days
# --------------------------------------------------------------------------
def _stratum_key(prefix, depth):
    """`depth` fields of `STRATUM_FIELDS`, plus the day type, always."""
    return tuple(prefix[f] for f in STRATUM_FIELDS[:depth]) + (prefix["strat_day_type"],)


def load_pool(path, step2_dir, bitpos, limit=None, outdoor_override=None):
    """Decode a generated batch and turn each record into a day of presence.

    Returns `(pools, meta)`. `pools` is `{depth: {key: [day, ...]}}` for every
    back-off depth, so a look-up never has to re-bucket. A `day` carries its
    minute-resolution presence flags AND its activity codes, because the second
    is what an activity-resolved gains mapping would need and regenerating to get
    it back would cost a GPU run.
    """
    shipped, outdoor_md5 = indoor.load_outdoor_at_home(step2_dir)
    # PERTURBATION ONLY. `V7.c`: the gate re-reads the shipped file itself and
    # refuses a caller set that differs by one code, in either direction.
    outdoor = shipped if outdoor_override is None else frozenset(outdoor_override)
    pools = dict((d, collections.defaultdict(list)) for d in range(len(STRATUM_FIELDS) + 1))
    n_read = 0
    n_bad = 0
    provenance = None
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if limit is not None and n_read >= limit:
                break
            rec = json.loads(line)
            provenance = rec.get("provenance", provenance)
            try:
                decoded = dec.decode_record(rec["text"], bitpos)
                flags = indoor.presence_minutes(decoded, outdoor)
            except Exception:
                # Counted, never silently skipped: `G7.11` exists because
                # attrition is population bias.
                n_bad += 1
                continue
            day = {
                "flags": flags,
                "acts": [(e["duration_min"], e["act"]) for e in decoded["episodes"]],
                "prefix": decoded["prefix"],
            }
            for depth in pools:
                pools[depth][_stratum_key(decoded["prefix"], depth)].append(day)
            n_read += 1
    meta = {
        "pool_file": os.path.basename(path),
        "pool_md5": hashlib.md5(open(path, "rb").read()).hexdigest(),
        "provenance": provenance,
        "n_days": n_read,
        "n_undecodable": n_bad,
        "outdoor_at_home_md5": outdoor_md5,
        "outdoor_at_home_used": sorted(outdoor),
        "outdoor_at_home_is_shipped": outdoor == shipped,
        "n_keys_full_depth": len(pools[len(STRATUM_FIELDS)]),
    }
    if n_read == 0:
        raise ScheduleError(
            "the pool is empty: %s. A schedule assembled from no days is a "
            "constant, which is FINDING 42's signature." % path)
    return pools, meta


def draw(pools, prefix, rng, backoff_tally):
    """One day for one person, with the back-off ladder recorded.

    The ladder is COUNTED. A campaign that quietly served every 13-year-old a day
    drawn from "any weekday" would produce a perfectly valid schedule set and a
    meaningless one, and nothing downstream would ever see it.
    """
    for depth in range(len(STRATUM_FIELDS), -1, -1):
        key = _stratum_key(prefix, depth)
        bucket = pools[depth].get(key)
        if bucket:
            backoff_tally[depth] += 1
            return rng.choice(bucket), depth
    raise ScheduleError(
        "no day in the pool matches even on day type alone for %r. That means "
        "the pool has no %s at all." % (prefix, prefix["strat_day_type"]))


# --------------------------------------------------------------------------
# chaining
# --------------------------------------------------------------------------
def assemble_person_year(prefix, cal, rule, rng, pools, backoff_tally, rho=0.0):
    """365 days for one person under one chaining rule.

    * `independent` -- a fresh draw every day.
    * `static`      -- one draw per DAY TYPE, repeated all year. Not one draw
                       per year: a person whose only diary is a Sunday would
                       otherwise be at leisure for 365 days.
    * `habit`       -- keep the held day with probability `rho`, else draw
                       fresh; the held day is per DAY TYPE, for the same reason.

    `rho = 0` must reproduce `independent` and `rho = 1` must reproduce `static`,
    given the same seed and the same draw order. The selftest asserts both. That
    is the only cheap way to know the three rules are three points on one axis
    rather than three different pieces of code.
    """
    if rule not in CHAINING_RULES:
        raise ScheduleError("unknown chaining rule %r" % (rule,))
    days = []
    held = {}
    for dt in cal:
        p = dict(prefix)
        p["strat_day_type"] = dt
        if rule == "independent":
            day, _ = draw(pools, p, rng, backoff_tally)
        elif rule == "static":
            if dt not in held:
                held[dt], _ = draw(pools, p, rng, backoff_tally)
            day = held[dt]
        else:
            if dt in held and rng.random() < rho:
                day = held[dt]
            else:
                day, _ = draw(pools, p, rng, backoff_tally)
                held[dt] = day
        days.append(day)
    return days


# --------------------------------------------------------------------------
# minutes -> timestep
# --------------------------------------------------------------------------
def to_timestep(minute_values, timestep_min):
    """Mean over each timestep bin."""
    if DAY_MINUTES % timestep_min:
        raise ScheduleError(
            "timestep %d min does not divide the %d-minute day. A ragged final "
            "bin is a schedule whose last value covers a different span from "
            "every other value." % (timestep_min, DAY_MINUTES))
    out = []
    for i in range(0, len(minute_values), timestep_min):
        chunk = minute_values[i:i + timestep_min]
        out.append(float(sum(chunk)) / len(chunk))
    return out


def household_year(members_days, timestep_min):
    """Dwelling presence fraction, per timestep, for a whole year.

    `members_days` is `[days_of_member_0, days_of_member_1, ...]`, each a list of
    365 days. The fraction is (members present) / (household size), so it is in
    [0, 1] and `People.Number of People` carries the head-count.
    """
    n = len(members_days)
    if n == 0:
        raise ScheduleError("a household with zero members has no schedule")
    n_days = len(members_days[0])
    if any(len(m) != n_days for m in members_days):
        raise ScheduleError("members disagree on the number of days")
    # Each distinct day object is expanded to per-timestep present-minute counts
    # ONCE and cached on the object. A pool day is reused hundreds of times
    # across a year and across households, and re-walking 1,440 flags each time
    # is what made the first version too slow to run five seeds.
    series = []
    for d in range(n_days):
        acc = None
        for m in members_days:
            day = m[d]
            ts = day.get("_ts_%d" % timestep_min)
            if ts is None:
                ts = to_timestep([1 if f else 0 for f in day["flags"]], timestep_min)
                day["_ts_%d" % timestep_min] = ts
            if acc is None:
                acc = list(ts)
            else:
                for i, v in enumerate(ts):
                    acc[i] += v
        series.extend([v / float(n) for v in acc])
    return series


# --------------------------------------------------------------------------
# emission
# --------------------------------------------------------------------------
def write_schedule_csv(path, values, column_name):
    """One column, one header row. `Rows to Skip at Top` is 1 and says so."""
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow([column_name])
        for v in values:
            w.writerow(["%.6f" % v])


def compact_objects(name, values, n_people):
    """PERTURBATION ONLY -- a `Schedule:Compact` in place of a `Schedule:File`.

    The Step 7 validation document registers no perturbation that fells `G7.14`,
    so `G7.14` would have passed for ever without once being seen to fall. This
    is the missing falsifier, and it is deliberately faithful: a real
    `Schedule:Compact` of 8,760 hourly values is what the step document warns
    "bloats the IDF past twenty thousand lines per schedule", which is why it is
    truncated to the first day here. It is never emitted by a baseline run.
    """
    L = ["Schedule:Compact,", "  %s_Presence," % name, "  Fraction,",
         "  Through: 12/31,", "  For: AllDays,"]
    for h, v in enumerate(values[:24]):
        L.append("  Until: %02d:00,  %.6f," % (h + 1, v))
    L[-1] = L[-1][:-1] + ";"
    L.append("")
    L.append("People,")
    L.append("  %s_People," % name)
    L.append("  %s_Zone," % name)
    L.append("  %s_Presence," % name)
    L.append("  People,")
    L.append("  %d," % n_people)
    L.append("  ,")
    L.append("  ,")
    L.append("  0.3,")
    L.append("  ,")
    L.append("  Activity_Level;")
    return "\n".join(L) + "\n"


def idf_objects(name, csv_name, n_values, timestep_min, n_people,
                interpolate=None):
    """The `Schedule:File` and `People` pair, as IDF text.

    `interpolate` exists only so the registered perturbation has something to
    perturb; it defaults to the module constant.
    """
    hours = n_values * timestep_min / 60.0
    if abs(hours - round(hours)) > 1e-9:
        raise ScheduleError("%d values at %d min is %.4f hours, not integral"
                            % (n_values, timestep_min, hours))
    interp = INTERPOLATE_TO_TIMESTEP if interpolate is None else interpolate
    return (
        "Schedule:File,\n"
        "  %s_Presence,            !- Name\n"
        "  Fraction,               !- Schedule Type Limits Name\n"
        "  %s,                     !- File Name\n"
        "  1,                      !- Column Number\n"
        "  1,                      !- Rows to Skip at Top\n"
        "  %d,                     !- Number of Hours of Data\n"
        "  Comma,                  !- Column Separator\n"
        "  %s,                     !- Interpolate to Timestep\n"
        "  %d;                     !- Minutes per Item\n"
        "\n"
        "People,\n"
        "  %s_People,              !- Name\n"
        "  %s_Zone,                !- Zone or ZoneList Name\n"
        "  %s_Presence,            !- Number of People Schedule Name\n"
        "  People,                 !- Number of People Calculation Method\n"
        "  %d,                     !- Number of People\n"
        "  ,                       !- People per Zone Floor Area\n"
        "  ,                       !- Zone Floor Area per Person\n"
        "  0.3,                    !- Fraction Radiant\n"
        "  ,                       !- Sensible Heat Fraction\n"
        "  Activity_Level;         !- Activity Level Schedule Name\n"
        % (name, csv_name, int(round(hours)), interp, timestep_min,
           name, name, name, n_people))


# --------------------------------------------------------------------------
# households
# --------------------------------------------------------------------------
def load_households(corpus_path, country, n_households, rng, min_size=1):
    """Household composition from the REAL corpus.

    WHY THE REAL CORPUS AND NOT THE STEP 5 POPULATION. The Step 5 population is a
    PERSON table -- `country, strat_age_band, strat_sex, strat_hh_type,
    strat_econ_status, strat_day_type` -- with no household identifier, because
    `D-S5-9` settled household TYPE on a person basis and never needed to
    assemble a dwelling. Work item 7.6 asks for "100 households", which that
    table cannot supply without inventing a grouping.

    The corpus can: it carries `hid` and `pid`. So the composition here is DATA
    (real households, real member strata) and only the DAYS are generated. This
    is recorded as a limitation rather than presented as the design: it makes the
    chaining experiment's households a sample of SURVEYED households, not a
    sample of the synthetic population, and those are not the same object.
    """
    hh = collections.OrderedDict()
    with io.open(corpus_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["country"] != country:
                continue
            prefix_str = r["text"].split("|", 1)[0]
            pfx = dec.decode_prefix(prefix_str)
            hh.setdefault(r["hid"], collections.OrderedDict())
            # One person can hold two diary days (UK only). The prefix strata
            # differ only in `strat_day_type`, which the assembler overrides per
            # calendar day anyway; keep the first.
            hh[r["hid"]].setdefault(r["pid"], pfx)
    keys = [k for k, v in hh.items() if len(v) >= min_size]
    if len(keys) < n_households:
        raise ScheduleError(
            "country %s has %d households of size >= %d, fewer than the %d asked "
            "for" % (country, len(keys), min_size, n_households))
    chosen = rng.sample(keys, n_households)
    return [(k, list(hh[k].values())) for k in chosen]


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------
def build(gen_dir, fold, step2_dir, crosswalk, corpus, out_dir, year,
          timestep_min, rule, seed, n_households, rho=0.0, arm="constrained",
          min_size=1, pool_limit=None, interpolate=None, n_hours_override=None,
          keep_series=False, outdoor_override=None, use_compact=False,
          presence_offset=0.0, leg="leg4"):
    """Emit one campaign cell. Returns the manifest dict.

    `interpolate` and `n_hours_override` exist ONLY so the two registered
    perturbations ("set Interpolate to Timestep = Yes", "emit 8,759 hours") have
    something to perturb. They default to the correct values and any non-default
    is stamped into the manifest.
    """
    bitpos = load_bit_positions(crosswalk)
    # `leg` defaults to leg4 so every invocation written before this argument
    # existed reproduces byte-for-byte.  It is an argument at all because the
    # leg was hard-coded here, which is why every schedule on disk came from the
    # 600-diary pool whose own records stamp themselves NOT REPORTABLE while the
    # 5,200-diary Leg-5 pools sat beside them unreachable.
    pool_path = os.path.join(gen_dir, "generated_%s_%s_%s.jsonl" % (leg, fold, arm))
    pools, pool_meta = load_pool(pool_path, step2_dir, bitpos, limit=pool_limit,
                                 outdoor_override=outdoor_override)
    cal = year_day_types(year)
    rng = random.Random(seed)
    households = load_households(corpus, fold, n_households, rng, min_size=min_size)
    backoff = collections.Counter()

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    idf = []
    sizes = []
    per_hh = []
    series_out = []
    member_acts = []
    n_values_expected = DAYS_PER_YEAR * (DAY_MINUTES // timestep_min)
    for hid, members in households:
        member_days = [assemble_person_year(p, cal, rule, rng, pools, backoff, rho)
                       for p in members]
        series = household_year(member_days, timestep_min)
        if n_hours_override is not None:
            series = series[:int(n_hours_override * 60 / timestep_min)]
        if presence_offset:
            # PERTURBATION ONLY -- pushes values out of [0, 1] so `G7.17` has a
            # falsifier. The registered table has none.
            series = [v + presence_offset for v in series]
        name = "HH_%s_%s" % (fold, hid)
        csv_name = "presence_%s.csv" % name
        write_schedule_csv(os.path.join(out_dir, csv_name), series, name + "_Presence")
        if use_compact:
            idf.append(compact_objects(name, series, len(members)))
        else:
            idf.append(idf_objects(name, csv_name, len(series), timestep_min,
                                   len(members), interpolate))
        sizes.append(len(members))
        per_hh.append({"hid": hid, "n_members": len(members),
                       "n_values": len(series),
                       "mean_presence": sum(series) / float(len(series))})
        if keep_series:
            series_out.append(series)
            member_acts.append([[d["acts"] for d in m] for m in member_days])

    with io.open(os.path.join(out_dir, "schedules.idf"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write("! 4J Step 7 work item 7.7 -- generated schedules\n")
        fh.write("! %s\n" % pool_meta["provenance"])
        fh.write("! fold=%s rule=%s rho=%.3f seed=%d year=%d timestep=%dmin\n\n"
                 % (fold, rule, rho, seed, year, timestep_min))
        fh.write("\n".join(idf))

    manifest = {
        "fold": fold,
        "arm": arm,
        "rule": rule,
        "rho": rho,
        "seed": seed,
        "year": year,
        "timestep_min": timestep_min,
        "n_households": len(households),
        "household_sizes": sizes,
        "n_values_per_schedule_expected": n_values_expected,
        "interpolate_to_timestep": interpolate or INTERPOLATE_TO_TIMESTEP,
        "n_hours_override": n_hours_override,
        "perturbations": {
            "interpolate": interpolate,
            "n_hours_override": n_hours_override,
            "outdoor_override": (sorted(outdoor_override)
                                 if outdoor_override is not None else None),
            "use_compact": bool(use_compact),
            "presence_offset": presence_offset,
        },
        "backoff_depth_counts": dict(backoff),
        "backoff_full_depth_share": (
            backoff[len(STRATUM_FIELDS)] / float(sum(backoff.values()))
            if backoff else None),
        "households": per_hh,
        "pool": pool_meta,
        "provenance": pool_meta["provenance"],
        "leg": leg,
    }
    with io.open(os.path.join(out_dir, "manifest.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(manifest, indent=2, sort_keys=True))
    if keep_series:
        manifest["_series"] = series_out
        manifest["_member_acts"] = member_acts
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description="4J Step 7 item 7.7 -- emit schedules")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--fold", required=True, choices=("es", "uk", "it"))
    ap.add_argument("--arm", default="constrained")
    ap.add_argument("--step2", required=True)
    ap.add_argument("--crosswalk", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--year", type=int, required=True,
                    help="calendar year; leap years are refused")
    ap.add_argument("--timestep", type=int, default=60)
    ap.add_argument("--rule", default="independent", choices=CHAINING_RULES)
    ap.add_argument("--rho", type=float, default=0.0)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--leg", default="leg4",
                    help="which generation leg's pool to draw days from. "
                         "Default leg4 so existing invocations reproduce.")
    ap.add_argument("--households", type=int, default=100)
    ap.add_argument("--min-size", type=int, default=1)
    ap.add_argument("--interpolate", default=None,
                    help="PERTURBATION ONLY. Overrides Interpolate to Timestep.")
    ap.add_argument("--hours", type=float, default=None,
                    help="PERTURBATION ONLY. Truncates every schedule to N hours.")
    ap.add_argument("--drop-outdoor-code", default=None,
                    help="PERTURBATION ONLY. Derive presence with a LOCAL COPY "
                         "of OUTDOOR_AT_HOME missing this code (V7.c).")
    ap.add_argument("--compact", action="store_true",
                    help="PERTURBATION ONLY. Emit Schedule:Compact.")
    ap.add_argument("--presence-offset", type=float, default=0.0,
                    help="PERTURBATION ONLY. Shifts every value out of [0,1].")
    a = ap.parse_args(argv)
    outdoor_override = None
    if a.drop_outdoor_code:
        shipped, _ = indoor.load_outdoor_at_home(a.step2)
        if a.drop_outdoor_code not in shipped:
            raise ScheduleError(
                "%r is not in the shipped list %s, so dropping it would perturb "
                "nothing and the perturbation would silently be a null one."
                % (a.drop_outdoor_code, sorted(shipped)))
        outdoor_override = shipped - {a.drop_outdoor_code}
    m = build(a.gen, a.fold, a.step2, a.crosswalk, a.corpus, a.out, a.year,
              a.timestep, a.rule, a.seed, a.households, a.rho, a.arm,
              a.min_size, None, a.interpolate, a.hours, False,
              outdoor_override, a.compact, a.presence_offset, a.leg)
    print("emitted %d schedules -> %s" % (m["n_households"], a.out))
    print("  leg                 %s" % m["leg"])
    print("  provenance          %s" % m["provenance"])
    print("  pool                %s  %d days  md5 %s"
          % (m["pool"]["pool_file"], m["pool"]["n_days"], m["pool"]["pool_md5"]))
    print("  back-off depths     %s  (full-depth share %.4f)"
          % (m["backoff_depth_counts"], m["backoff_full_depth_share"]))
    print("  values/schedule     %d expected %d"
          % (m["households"][0]["n_values"], m["n_values_per_schedule_expected"]))
    print("  interpolate         %s" % m["interpolate_to_timestep"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
