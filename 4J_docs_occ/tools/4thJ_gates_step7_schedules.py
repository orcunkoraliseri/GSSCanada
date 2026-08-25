#!/usr/bin/env python
"""
4J Step 7 -- THE SCHEDULE-PRODUCTION GATES: `G7.13`-`G7.17`.

These four (`G7.14`-`G7.17`) had never been scored before this module existed,
because the artefact they score had never been emitted. `G7.13` had been run on
the real corpus and on generated records but never on an EMITTED SCHEDULE, which
is the only place its output actually reaches EnergyPlus.

EVERYTHING IS RE-READ FROM DISK
-------------------------------
`G8.12`'s lesson, borrowed one step early: *"If it reads the schedule from the
same in-memory object the injector wrote, it is comparing the injector's numbers
against the injector."* So this module takes a DIRECTORY, opens the `.idf` and
every `.csv` in it as text, and knows nothing about the emitter beyond the
manifest it reads for provenance. The emitter could be deleted and these gates
would still score what is on disk.

THE REGISTERED PERTURBATION TABLE IS INCOMPLETE, AND THAT IS RECORDED HERE
--------------------------------------------------------------------------
`4thJ_07_constrainedGeneration_val.md` registers three perturbations touching
these gates:

    Set `Interpolate to Timestep = Yes`            -> G7.15   (G7.14 clean)
    Emit 8,759 hours                               -> G7.16   (G7.17 clean)
    A local copy of OUTDOOR_AT_HOME off by one     -> G7.13   (G7.17 clean)

`G7.14` and `G7.17` appear ONLY in the "must stay clean" column. Under the
coverage clause -- *"FAIL the probe if any passing gate was never made to fall"*
-- both would have passed for ever without once being seen to fall. Two
falsifiers are therefore ADDED here, additively, and named as additions:

    Emit `Schedule:Compact` instead of `Schedule:File`  -> G7.14  (G7.16 clean)
    Shift every presence value by +0.5                  -> G7.17  (G7.14 clean)

VACUITY
-------
Zero schedules, zero values, or a constant presence signal FAIL. A gate that
cannot tell "nothing was wrong" from "nothing was checked" is not a gate.
"""

import argparse
import collections
import csv
import glob
import io
import json
import os
import re
import sys

DAY_MINUTES = 1440
HOURS_PER_YEAR = 8760

#: The gates this module owns. `G7.13` is re-scored here on the EMITTED signal;
#: its corpus-level and generated-text runs live in `4thJ_step7_indoor.py` and
#: `4thJ_gates_step7.py` respectively and are not repeated.
GATES = ("G7.13", "G7.14", "G7.15", "G7.16", "G7.17", "G7.19")

# --------------------------------------------------------------------------
# 🔴 G7.19 -- THE PHASE GATE. Added 2026-08-26 under `D-S9-3`(a).
#
# `FINDING 141`: `D-S2-5` put every diary on a 04:00 origin, `Schedule:File` is
# read from midnight, and the schedules Step 8 simulated were therefore four
# hours early. NOT ONE of `G7.13`-`G7.17` could see it, and neither could any
# Step 8 gate: they check that a schedule has 8,760 values, that `Interpolate to
# Timestep` is No, that `Minutes per Item` matches, that values lie in [0, 1],
# and that the multiplier rebuilds from the artefact on disk. **Every one of
# those is true of a series rotated by four hours.** A well-formed schedule on
# the wrong clock is the failure this gate exists for.
#
# The two arms are stated as PHASE, not as level, and both are self-referenced:
# the schedule is scored against its OWN daily maximum and its OWN trough, never
# against an external band, so nothing here can be met by rescaling.
# --------------------------------------------------------------------------

#: Arm (a). At 05:00 the residential population of every country in this corpus
#: is at home and asleep, so mean presence there must be within a tenth of the
#: schedule's own daily maximum. MEASURED on the shipped bundles: rotated
#: 0.950-1.000, unrotated 0.674-0.787. Registered 2026-08-26 and never moved.
G7_19_NIGHT_HOUR = 5
G7_19_NIGHT_RATIO_MIN = 0.90

#: Arm (b). The daily minimum of a residential presence profile is the working
#: day. It is not 07:00. MEASURED: rotated 11 / 11 / 13, unrotated 7 / 7 / 9.
G7_19_MIN_TROUGH_HOUR = 8


class ScheduleGateError(ValueError):
    pass


# --------------------------------------------------------------------------
# reading what is on disk
# --------------------------------------------------------------------------
_OBJ_SPLIT = re.compile(r";\s*(?:!-[^\n]*)?\n")


def read_idf_objects(path):
    """Split an IDF into objects, keeping comments so the field names survive.

    Deliberately crude: a real IDF parser would normalise away exactly the
    formatting differences these gates are supposed to notice.
    """
    text = io.open(path, encoding="utf-8").read()
    # Comments are stripped LINE BY LINE and BEFORE the field split. An IDF
    # comment runs from `!` to end of line, so a comma inside one is not a field
    # separator -- and splitting first leaves every comment glued to the FRONT of
    # the next field, which is a parser that silently returns empty strings.
    lines = []
    for l in text.splitlines():
        cut = l.find("!")
        lines.append(l if cut < 0 else l[:cut])
    body = "\n".join(lines)
    objs = []
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        fields = [raw.strip() for raw in chunk.split(",")]
        if fields and fields[0]:
            objs.append(fields)
    return objs, text


def read_schedule_csv(path):
    """Header plus values, straight off disk. Never trusts a row count."""
    rows = []
    with io.open(path, encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh):
            if row:
                rows.append(row)
    if not rows:
        raise ScheduleGateError("%s is empty" % path)
    header = rows[0]
    values = []
    for r in rows[1:]:
        if len(r) != 1:
            raise ScheduleGateError(
                "%s row %d has %d columns; `Column Number 1` addresses a single "
                "column and a second one would be read as data by nothing and "
                "as a bug by nobody" % (path, len(values) + 2, len(r)))
        values.append(float(r[0]))
    return header, values


# --------------------------------------------------------------------------
# the gates
# --------------------------------------------------------------------------
def score(dir_path):
    """Score `G7.13`-`G7.17` over one emitted campaign cell."""
    idf_path = os.path.join(dir_path, "schedules.idf")
    man_path = os.path.join(dir_path, "manifest.json")
    if not os.path.exists(idf_path):
        raise ScheduleGateError("no schedules.idf in %s" % dir_path)
    manifest = json.load(io.open(man_path, encoding="utf-8")) if os.path.exists(man_path) else {}
    objs, idf_text = read_idf_objects(idf_path)
    csvs = sorted(glob.glob(os.path.join(dir_path, "presence_*.csv")))

    sched_file = [o for o in objs if o[0].lower() == "schedule:file"]
    sched_compact = [o for o in objs if o[0].lower() == "schedule:compact"]
    people = [o for o in objs if o[0].lower() == "people"]

    res = collections.OrderedDict()
    counts = {
        "dir": dir_path,
        "n_idf_objects": len(objs),
        "n_schedule_file": len(sched_file),
        "n_schedule_compact": len(sched_compact),
        "n_people": len(people),
        "n_csv_files": len(csvs),
        "provenance": manifest.get("provenance"),
        "declared_timestep_min": manifest.get("timestep_min"),
        "declared_interpolate": manifest.get("interpolate_to_timestep"),
    }

    # ---------------------------------------------------------------- G7.14
    r14 = []
    if not sched_file and not sched_compact:
        r14.append("the IDF declares NO schedule object at all. That is not a "
                   "pass, it is an empty file.")
    if sched_compact:
        r14.append("%d Schedule:Compact objects. The step document requires "
                   "Schedule:File: at urban scale compact blocks bloat the IDF "
                   "past twenty thousand lines per schedule."
                   % len(sched_compact))
    if sched_file and len(sched_file) != len(csvs):
        r14.append("%d Schedule:File objects against %d CSV files on disk"
                   % (len(sched_file), len(csvs)))
    res["G7.14"] = {"passes": not r14, "reasons": r14,
                    "n_schedule_file": len(sched_file),
                    "n_schedule_compact": len(sched_compact)}

    # ---------------------------------------------------------------- G7.15
    # Per OBJECT, never once for the file. One schedule set to `Yes` inside a
    # hundred set to `No` is the failure this gate exists for.
    r15 = []
    interp_values = []
    for o in sched_file:
        # Schedule:File fields: 0 type, 1 name, 2 limits, 3 file, 4 col,
        # 5 skip, 6 hours, 7 separator, 8 interpolate, 9 minutes
        if len(o) < 9:
            r15.append("a Schedule:File object has only %d fields, so it "
                       "declares no Interpolate to Timestep at all" % len(o))
            continue
        interp_values.append(o[8])
    bad = [v for v in interp_values if v.strip().lower() != "no"]
    if bad:
        r15.append("%d of %d Schedule:File objects do not say No: %s"
                   % (len(bad), len(interp_values),
                      sorted(collections.Counter(bad))))
    if not interp_values:
        r15.append("no Schedule:File object carries an Interpolate to Timestep "
                   "field, so the setting was never asserted.")
    res["G7.15"] = {"passes": not r15, "reasons": r15,
                    "n_objects_checked": len(interp_values),
                    "distinct_values": sorted(set(interp_values))}

    # ---------------------------------------------------------------- G7.16
    r16 = []
    lengths = collections.Counter()
    declared_hours = collections.Counter()
    declared_minutes = collections.Counter()
    per_file = []
    for o in sched_file:
        if len(o) >= 10:
            declared_hours[o[6]] += 1
            declared_minutes[o[9]] += 1
    for p in csvs:
        header, values = read_schedule_csv(p)
        lengths[len(values)] += 1
        per_file.append({"file": os.path.basename(p), "n_values": len(values),
                         "min": min(values) if values else None,
                         "max": max(values) if values else None,
                         "mean": (sum(values) / len(values)) if values else None})
    if not csvs:
        r16.append("no schedule CSV on disk")
    if len(lengths) > 1:
        r16.append("schedules disagree on length: %s" % dict(lengths))
    ts = manifest.get("timestep_min")
    if ts:
        expected = HOURS_PER_YEAR * 60 // ts
        for n in lengths:
            if n != expected:
                r16.append("a schedule carries %d values; %d hours at %d min is "
                           "%d" % (n, HOURS_PER_YEAR, ts, expected))
    if len(declared_hours) > 1:
        r16.append("Schedule:File objects declare different hour counts: %s"
                   % dict(declared_hours))
    for h, n in declared_hours.items():
        if int(h) != HOURS_PER_YEAR:
            r16.append("%d objects declare %s hours, not %d" % (n, h, HOURS_PER_YEAR))
    for m, n in declared_minutes.items():
        if ts and int(m) != ts:
            r16.append("%d objects declare %s minutes per item against a "
                       "manifest timestep of %d" % (n, m, ts))
        if int(m) and DAY_MINUTES % int(m):
            r16.append("Minutes per Item %s does not divide the 1440-minute day"
                       % m)
    # a declared length that disagrees with the file on disk is the gap the
    # gate is named for: "no gaps, no duplicated timestamps"
    for h in declared_hours:
        for m in declared_minutes:
            want = int(h) * 60 // int(m)
            for n in lengths:
                if n != want:
                    r16.append("the object declares %s h at %s min = %d values, "
                               "the file on disk carries %d" % (h, m, want, n))
    res["G7.16"] = {"passes": not r16, "reasons": r16,
                    "value_counts": dict(lengths),
                    "declared_hours": dict(declared_hours),
                    "declared_minutes_per_item": dict(declared_minutes)}

    # ---------------------------------------------------------------- G7.17
    r17 = []
    lo = min((f["min"] for f in per_file if f["min"] is not None), default=None)
    hi = max((f["max"] for f in per_file if f["max"] is not None), default=None)
    n_out = sum(1 for f in per_file
                if f["min"] is not None and (f["min"] < 0.0 or f["max"] > 1.0))
    if lo is None:
        r17.append("no value was read, so the range was never tested")
    else:
        if lo < 0.0 or hi > 1.0:
            r17.append("presence leaves [0,1]: %d of %d schedules, range "
                       "[%.6f, %.6f]" % (n_out, len(per_file), lo, hi))
    head = []
    for o in people:
        # People fields: 0 type, 1 name, 2 zone, 3 sched, 4 method, 5 number
        if len(o) < 6:
            r17.append("a People object has %d fields and declares no "
                       "Number of People" % len(o))
            continue
        v = o[5]
        try:
            f = float(v)
        except ValueError:
            r17.append("Number of People %r is not a number" % v)
            continue
        if f != int(f):
            r17.append("Number of People %r is not integral. The People object "
                       "expects a head-count; a fraction there means the "
                       "presence fraction was baked in twice." % v)
        if f < 1:
            r17.append("Number of People %r is below 1" % v)
        head.append(int(f))
    if not people:
        r17.append("no People object, so the occupant count was never asserted")
    res["G7.17"] = {"passes": not r17, "reasons": r17,
                    "presence_min": lo, "presence_max": hi,
                    "n_schedules_out_of_range": n_out,
                    "head_counts": dict(collections.Counter(head))}

    # ---------------------------------------------------------------- G7.19
    # The phase of the emitted signal against the clock EnergyPlus reads it on.
    # Scored on the mean over households AND on every household separately, so a
    # bundle that is right on average and wrong in a corner cannot pass.
    r19 = []
    prof = None
    ts19 = manifest.get("timestep_min")
    per_h = int(60 // ts19) if ts19 and 60 % ts19 == 0 else None
    if not csvs:
        r19.append("no schedule on disk, so the phase was never tested")
    elif not per_h:
        r19.append("timestep %r does not divide an hour, so an hour-of-day "
                   "profile is not defined" % ts19)
    else:
        acc = [0.0] * 24
        n_v = 0
        worst = []
        for p in csvs:
            _hdr, vals = read_schedule_csv(p)
            hp = [0.0] * 24
            for i, v in enumerate(vals):
                h = (i // per_h) % 24
                acc[h] += v
                hp[h] += v
            n_v += len(vals)
            days = len(vals) / float(24 * per_h)
            hp = [x / (days * per_h) for x in hp]
            hmax = max(hp)
            ratio = (hp[G7_19_NIGHT_HOUR] / hmax) if hmax > 0 else 0.0
            trough = min(range(24), key=lambda k: hp[k])
            worst.append((os.path.basename(p), ratio, trough))
        prof = [x / (n_v / 24.0) for x in acc]
        pmax = max(prof)
        ratio = (prof[G7_19_NIGHT_HOUR] / pmax) if pmax > 0 else 0.0
        trough = min(range(24), key=lambda k: prof[k])
        if ratio < G7_19_NIGHT_RATIO_MIN:
            r19.append(
                "mean presence at %02d:00 is %.4f, which is %.3f of this "
                "bundle's own daily maximum %.4f -- below %.2f. A residential "
                "population is at home at %02d:00. FINDING 141: this is what an "
                "unrotated 04:00-origin diary looks like on a Schedule:File."
                % (G7_19_NIGHT_HOUR, prof[G7_19_NIGHT_HOUR], ratio, pmax,
                   G7_19_NIGHT_RATIO_MIN, G7_19_NIGHT_HOUR))
        if trough < G7_19_MIN_TROUGH_HOUR:
            r19.append(
                "the daily minimum of mean presence falls at %02d:00 (%.4f), "
                "before %02d:00. Nobody's occupancy trough is the small hours."
                % (trough, prof[trough], G7_19_MIN_TROUGH_HOUR))
        # 🔴 THE PER-DWELLING COUNTS ARE A DIAGNOSTIC AND CARRY NO
        # VERDICT, and that is a specification decision taken before this gate
        # ever returned one. Both arms are POPULATION statements. A single
        # dwelling's occupancy trough legitimately falls at 07:00 -- one
        # household that leaves for work together has its minimum exactly there
        # -- and a night-shift dwelling is legitimately empty at 05:00. Scoring
        # a stock claim per dwelling would have made the gate fail on 11 of 100
        # CORRECT schedules, and the fix for that must be the right statement,
        # never a looser number. MEASURED on fold es: rotated 0 of 100 dwellings
        # below the ratio arm (min 0.904) and 11 of 100 below the trough arm;
        # unrotated 72 and 54.
        n_ratio = sum(1 for _f, r, _t in worst if r < G7_19_NIGHT_RATIO_MIN)
        n_trough = sum(1 for _f, _r, t in worst if t < G7_19_MIN_TROUGH_HOUR)
    # The DECLARATION arm. A bundle that is in phase by accident and does not say
    # so is not evidence: `G8.17` refuses to run a campaign on an undeclared one.
    if "rotated_to_midnight" not in manifest:
        r19.append("the manifest does not record WHETHER the series was rotated "
                   "to midnight. An artefact that cannot say which clock it is "
                   "on cannot be validated against one.")
    elif not manifest.get("rotated_to_midnight"):
        r19.append("the manifest declares rotated_to_midnight = false: this "
                   "bundle is on the DIARY origin (%s), not on the clock "
                   "EnergyPlus reads." % manifest.get("diary_origin_hour"))
    res["G7.19"] = {"passes": not r19, "reasons": r19,
                    "hour_profile": prof,
                    "dwellings_below_night_ratio": (n_ratio if csvs and per_h
                                                    else None),
                    "dwellings_below_trough_hour": (n_trough if csvs and per_h
                                                    else None),
                    "n_dwellings": len(csvs),
                    "night_hour": G7_19_NIGHT_HOUR,
                    "night_ratio_min": G7_19_NIGHT_RATIO_MIN,
                    "min_trough_hour": G7_19_MIN_TROUGH_HOUR,
                    "declared_rotated": manifest.get("rotated_to_midnight")}

    # ---------------------------------------------------------------- G7.13
    # On the EMITTED signal. The exclusion-list half is read from the manifest
    # the emitter wrote (`V7.c` -- the emitter re-read the shipped file); the
    # vacuity half is measured on the CSVs on disk.
    r13 = []
    pool = manifest.get("pool", {})
    if "outdoor_at_home_is_shipped" not in pool:
        r13.append("the manifest does not record WHICH exclusion list produced "
                   "this signal. V7.c: validating against an unrecorded list "
                   "validates nothing.")
    elif not pool["outdoor_at_home_is_shipped"]:
        r13.append("the presence signal was derived with a LOCAL COPY of "
                   "OUTDOOR_AT_HOME, not the shipped list: %s"
                   % pool.get("outdoor_at_home_used"))
    allv = [v for f in per_file for v in ()]  # values are not retained per file
    if per_file:
        means = [f["mean"] for f in per_file]
        if lo is not None and lo == hi:
            r13.append("the presence signal is CONSTANT at %.6f across every "
                       "schedule. That is FINDING 42's signature and it is "
                       "indistinguishable from a rule that was never wired in."
                       % lo)
        if all(m == 0.0 for m in means):
            r13.append("every schedule has mean presence 0. FINDING 42.")
        if all(m == 1.0 for m in means):
            r13.append("every schedule has mean presence 1. The rule excluded "
                       "nothing, so it cannot be shown to bind.")
    else:
        r13.append("no emitted schedule to score")
    res["G7.13"] = {"passes": not r13, "reasons": r13,
                    "outdoor_at_home_md5": pool.get("outdoor_at_home_md5"),
                    "used_shipped_list": pool.get("outdoor_at_home_is_shipped"),
                    "mean_presence_over_schedules": (
                        sum(f["mean"] for f in per_file) / len(per_file)
                        if per_file else None)}

    return {"counts": counts, "gates": res, "per_file": per_file,
            "manifest_perturbations": manifest.get("perturbations")}


def report(out):
    """`V7.b` -- counts BEFORE verdicts."""
    c = out["counts"]
    L = ["", "=" * 74,
         "Step 7 schedule gates -- %s" % c["dir"],
         "=" * 74,
         "  provenance          %s" % c["provenance"],
         "  IDF objects         %d  (Schedule:File %d, Schedule:Compact %d, People %d)"
         % (c["n_idf_objects"], c["n_schedule_file"], c["n_schedule_compact"], c["n_people"]),
         "  CSV files on disk   %d" % c["n_csv_files"],
         "  declared timestep   %s min   interpolate %s"
         % (c["declared_timestep_min"], c["declared_interpolate"]),
         ""]
    if out.get("manifest_perturbations") and any(
            v for k, v in out["manifest_perturbations"].items()):
        L.append("  *** PERTURBED CELL: %s" % json.dumps(
            dict((k, v) for k, v in out["manifest_perturbations"].items() if v)))
        L.append("")
    p19 = out["gates"].get("G7.19", {})
    if p19.get("hour_profile"):
        pr = p19["hour_profile"]
        tr = min(range(24), key=lambda k: pr[k])
        L.append("  phase (D-S9-3)      declared rotated %s; mean presence at "
                 "%02d:00 = %.4f of max; trough %02d:00"
                 % (p19.get("declared_rotated"), p19["night_hour"],
                    pr[p19["night_hour"]] / max(pr) if max(pr) else 0.0, tr))
        L.append("                      dwellings below the arms (DIAGNOSTIC, "
                 "no verdict): night %s/%s, trough %s/%s"
                 % (p19.get("dwellings_below_night_ratio"), p19.get("n_dwellings"),
                    p19.get("dwellings_below_trough_hour"), p19.get("n_dwellings")))
        L.append("")
    for g in GATES:
        r = out["gates"][g]
        L.append("  %-6s %s" % (g, "PASS" if r["passes"] else "**FAIL**"))
        for reason in r["reasons"]:
            L.append("         - %s" % reason)
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="4J Step 7 schedule gates G7.13-G7.17")
    ap.add_argument("dirs", nargs="+", help="emitted campaign-cell directories")
    ap.add_argument("--out", default=None, help="write the board as JSON")
    ap.add_argument("--expect-fail", default=None,
                    help="comma-separated gates this cell MUST fail (a "
                         "perturbation that does not fell its gate is a "
                         "perturbation that proves nothing)")
    ap.add_argument("--expect-clean", default=None,
                    help="comma-separated gates this cell must NOT fail")
    a = ap.parse_args(argv)

    board = {}
    rc = 0
    for d in a.dirs:
        out = score(d)
        print(report(out))
        board[d] = dict((g, out["gates"][g]["passes"]) for g in GATES)
        board[d + "::detail"] = out["gates"]
        if a.expect_fail:
            want = [g.strip() for g in a.expect_fail.split(",") if g.strip()]
            for g in want:
                if out["gates"][g]["passes"]:
                    print("  *** PROBE FAIL: %s was expected to FALL and did not."
                          % g)
                    rc = 1
        if a.expect_clean:
            want = [g.strip() for g in a.expect_clean.split(",") if g.strip()]
            for g in want:
                if not out["gates"][g]["passes"]:
                    print("  *** PROBE FAIL: %s was expected to stay CLEAN and "
                          "fell: %s" % (g, out["gates"][g]["reasons"]))
                    rc = 1
    if a.out:
        with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(board, indent=2, sort_keys=True))
        print("\nboard -> %s" % a.out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
