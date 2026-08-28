#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""4J Step 10 -- emit the MVP §9.5 presence-series record as a per-bundle ADDENDUM.

WHY AN ADDENDUM AND NOT A RE-EMISSION. MVP §9.5 requires 13 fields per shipped
`g(t)`. Our Step 7 bundle manifests already carry eight of them; five are absent
(`schedule_sha256`, `held_out_country`, `diary_source_id`, `timezone` /
`local_time_basis`, `start_timestamp` / `end_timestamp`). Re-emitting the bundles
to add labels would move every series hash for a LABELLING fix, which is exactly
the trade the project refuses: additive only. So this writes a sidecar beside the
manifest and touches nothing that exists. OpenUBEM conceded this route
explicitly.

WHAT IS DERIVED AND WHAT IS ASSIGNED -- the distinction is kept in the output
itself, because a reader cannot otherwise tell which fields carry evidence:

  DERIVED (measured from the artefacts, reproducible):
    schedule_sha256      hashed from each CSV on disk
    held_out_country     IS the fold. `tools/4thJ_step4_shards.py:489` and
                         `4thJ_step4_diagnostics.py:538` both set
                         `held_out_country = fold`. 🔴 Load-bearing, not
                         bookkeeping: §9.5 makes the adapter REJECT a series
                         naming the wrong fold, and `G8.16` was scored on that.
    n_hours, start/end   from the bundle's own `year` and value count
    utc_offset_hours     read from the pinned EPW's own LOCATION header

  ASSIGNED (a convention we are choosing, defensible but not measured):
    diary_source_id      the archive identifier of the underlying delivery
    timezone             the IANA name. The EPW carries a UTC OFFSET, which is a
                         fact; the IANA name is a label placed on it here.

🔴 THE TIME BASIS IS THE DANGEROUS FIELD. `diary_origin_hour = 4` and
`rotated_to_midnight = true` must always be read TOGETHER (`FINDING 141`): the
series were generated on the diary's 04:00 origin and then ROTATED so that index
0 is midnight, which is the clock `Schedule:File` is read on (emitter, line 111).
Reading either flag alone gives a four-hour shift that no length check can see --
the `D-S9-3` failure class. So this file states the basis as one composed
sentence and never as two independent flags.

⚪ NO DST. EnergyPlus consumes the EPW on local standard time unless a daylight
saving period is declared, and none is. The offset recorded is the EPW's.

READ-ONLY on every input. Writes one JSON per bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys

#: ASSIGNED. Archive identifiers of the three underlying deliveries, as ruled in
#: the `D-S10-7`/`8`/`9` directives. These are OUR ids for the deliveries; they
#: are not variable names and not the depositor's own citation string.
#: 🔴 Never confuse with `RL27`'s column names, all three of which are WRONG and
#: are absent from the deliveries (`FINDING 174`).
DIARY_SOURCE_ID = {
    "es": "INE_EET_2009_2010",
    "uk": "UKDS_SN8128_UKTUS_2014_2015",
    "it": "ISTAT_UDT_2013_2014",
}

#: ASSIGNED. The IANA zone placed on the EPW's measured UTC offset.
TIMEZONE = {"es": "Europe/Madrid", "uk": "Europe/London", "it": "Europe/Rome"}

#: The pinned EPW per fold, for the offset read. `uk` is the `D-S10-7` (b) repin
#: target (`y2014`), NOT v1.0's `y2015` -- so an addendum generated before the
#: `v1.1` lands still describes the series we actually ship.
EPW_BASENAME = {
    "es": "es_madrid_2009_2010_y2010.epw",
    "uk": "uk_london_2014_2015_y2014.epw",
    "it": "it_bologna_2013_2014_y2014.epw",
}


def sha256_of(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def epw_utc_offset(epw_path):
    """Read the UTC offset from the EPW's own LOCATION line. Measured, not assumed."""
    with io.open(epw_path, encoding="latin-1") as fh:
        first = fh.readline().strip()
    parts = first.split(",")
    if not parts or parts[0].upper() != "LOCATION":
        raise SystemExit("%s: first line is not LOCATION" % epw_path)
    return float(parts[8]), first


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle-dir", required=True)
    ap.add_argument("--weather-root", required=True,
                    help="directory holding the pinned EPWs, for the offset read")
    ap.add_argument("--out", default=None,
                    help="default: <bundle-dir>/manifest_addendum_9_5.json")
    a = ap.parse_args(argv)

    man_path = os.path.join(a.bundle_dir, "manifest.json")
    with io.open(man_path, encoding="utf-8") as fh:
        man = json.load(fh)

    fold = man["fold"]
    year = int(man["year"])
    if fold not in DIARY_SOURCE_ID:
        raise SystemExit("unknown fold %r" % fold)

    epw_path = os.path.join(a.weather_root, EPW_BASENAME[fold])
    offset, location_line = epw_utc_offset(epw_path)

    series = []
    for h in man["households"]:
        name = "presence_HH_%s_%s.csv" % (fold, h["hid"])
        p = os.path.join(a.bundle_dir, name)
        if not os.path.exists(p):
            raise SystemExit("manifest names %s but it is not on disk" % name)
        series.append({
            "schedule_id": "HH_%s_%s_Presence" % (fold, h["hid"]),
            "schedule_path": name,
            "schedule_sha256": sha256_of(p),
            "hid": h["hid"],
            "n_members": h["n_members"],
            "n_values": h["n_values"],
        })

    n_hours = man["n_values_per_schedule_expected"]
    if n_hours != 8760:
        raise SystemExit("expected 8760 hours, manifest says %r" % n_hours)

    out = {
        "artefact": "MVP 9.5 presence-series record -- ADDENDUM to manifest.json",
        "addendum_to": "manifest.json",
        "addendum_to_sha256": sha256_of(man_path),
        "is_additive": True,
        "note": ("The bundle is NOT re-emitted by this file. No series hash moves. "
                 "Every field below is either derived from the artefacts or marked "
                 "assigned in field_provenance."),
        "ruling": "D-S10-7/8/9 directive 2, ruled 2026-08-27",

        "fold": fold,
        "held_out_country": fold,
        "held_out_country_basis": (
            "held_out_country IS the fold under LOCO. tools/4thJ_step4_shards.py:489 "
            "and tools/4thJ_step4_diagnostics.py:538. Load-bearing: MVP 9.5 makes the "
            "adapter reject a series naming the wrong fold; G8.16 scored on it."),

        "diary_source_id": DIARY_SOURCE_ID[fold],
        "chaining_rule": man["rule"],
        "rho": man["rho"],
        "random_seed": man["seed"],

        "timezone": TIMEZONE[fold],
        "utc_offset_hours": offset,
        "epw_location_line": location_line,
        "dst_applied": False,
        "local_time_basis": (
            "Local standard time, no daylight saving. Index 0 is 00:00 local on "
            "1 January of the stated year. The series were generated on the diary "
            "origin hour %d and then ROTATED to midnight (rotated_to_midnight=%s), "
            "which is the clock EnergyPlus Schedule:File is read on. These two facts "
            "must be read together -- either alone implies a four-hour shift that no "
            "length check can detect (FINDING 141, D-S9-3)."
            % (man["diary_origin_hour"], man["rotated_to_midnight"])),
        "diary_origin_hour": man["diary_origin_hour"],
        "rotated_to_midnight": man["rotated_to_midnight"],

        "year": year,
        "n_hours": n_hours,
        "timestep_min": man["timestep_min"],
        "interpolate_to_timestep": man["interpolate_to_timestep"],
        "start_timestamp": "%04d-01-01T00:00:00" % year,
        "end_timestamp": "%04d-12-31T23:00:00" % year,
        "timestamp_convention": (
            "hour-beginning; the stated end_timestamp is the START of the 8760th "
            "hour, not the end of the year"),

        "n_series": len(series),
        "series": series,

        "field_provenance": {
            "derived_from_artefacts": [
                "schedule_sha256", "held_out_country", "n_hours", "year",
                "start_timestamp", "end_timestamp", "utc_offset_hours",
                "chaining_rule", "rho", "random_seed", "timestep_min",
                "diary_origin_hour", "rotated_to_midnight"],
            "assigned_by_convention": ["diary_source_id", "timezone"],
            "why_the_split_is_recorded": (
                "A reader cannot otherwise tell which of these fields carries "
                "evidence. timezone in particular is an IANA label placed on the "
                "EPW's measured offset, not itself a measurement."),
        },
    }

    out_path = a.out or os.path.join(a.bundle_dir, "manifest_addendum_9_5.json")
    with io.open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %s  (fold %s, year %d, %d series)" % (out_path, fold, year, len(series)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
