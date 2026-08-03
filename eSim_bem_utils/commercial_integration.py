"""commercial_integration.py -- Step 8 (3J Leg-3 4-split): mixed-use schedule injection.

Generalizes Leg-2's office_integration.inject_office_schedules() to FOUR channels via a
single Tag-2 dispatch: inject_mixed_use(idf_path, output_path, channels, building_meta).
MODULATE (not REPLACE) for office/retail/hotel.

Residential (OD-8R-L3, added 2026-07-28) is REPLACE and lives in THIS module as
inject_residential() / load_residential_pool() / draw_residential_households(), called from
inject_mixed_use() when channels["residential"] is supplied. It is a separate code path from
the office/retail/hotel MODULATE dispatch loop below (which still unconditionally `continue`s
on residential-tagged Spaces -- unchanged), so a caller that never passes a "residential" key
gets byte-identical behaviour to before this change (verified, see Step8_docs Progress Log).
The multi-zone-carrier-collapse fix (2J Bug A) pattern is ported from
Leg2_2-split/Step8_docs/eSim_bem_utils_3J/integration.py (md5 6a92268be1f8dc3301df3bec80d6dd2e,
Step-9 equipment/lighting consolidation block, ~L1576-1584) -- there the bug was ONE
occupancy-zone carrier serving N physical dwelling-unit zones; here the equivalent defect is
ONE SpaceList-level PEOPLE object serving all N residential Spaces (confirmed empirically,
see below) -- same family of bug (single carrier, multiple physical zones), same fix (per-zone
carrier, one object per Space, no shared carrier).

Design doc: 3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/3rdJ_07_bemIntegration_4split.md
Validator : 3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/3rdJ_07_bemIntegration_4split_val.md (Section W)

Channels (Tag-2 routing table, verbatim spec Section "TAG-2 ROUTING TABLE" -- exact match,
NOT substring):

  Tag 2 (verbatim)                                          Channel      Injection
  --------------------------------------------------------  -----------  --------------------------
  HighriseApartment Apartment                                Residential  inject_residential(), REPLACE
                                                                            (Number_of_People + Occupancy_
                                                                            Schedule + Metabolic_Rate only;
                                                                            Lights/Equip NOT touched, OD-7D)
  HighriseApartment Corridor, HighriseApartment Office       Residential  OUT OF SCOPE for OD-8R-L3 (no
                                                               (common)     household data applies to
                                                                            shared/common areas); still
                                                                            skipped untouched, as before.
  OpenOffice, ClosedOffice                                   Office       NECB baseline x AT_WORK_fraction(t)
  Conference, Classroom, Dining, Restroom                    Office(supp) same as Office
  Retail Retail, Retail Back_Space,                          Retail       0.95 x shape_c_d(t); staff-only
    Retail Point_of_Sale, Retail Entry                                    shoulder slots keep baseline
  LargeHotel GuestRoom5, GuestRoom6, GuestRoom7              Hotel        NECB baseline x hotel_multiplier(t,month,PR)
  LargeHotel Banquet, Cafe, Kitchen, Lobby, Laundry,         Hotel(supp)  NECB baseline only (v1, OD-6)
    Storage, Corridor, Retail
  Corridor, Storage, Elec/MechRoom, Elevator Shaft,           Service/MEP  NECB baseline, no modulation
    Elevator Lobby, Plenum Space Type, Main Electrical,
    Main Mechanical, Elevator Machine Room

UPDATE (2026-07-28): the claim below ("no Tag-2-routable mixed-use prototype IDF exists") is
STALE and FALSE -- corrected here because an earlier version of this note already misled one
agent (Step8_docs 3rdJ_08_implementation_improvements.md open item #4). A real v24.2 mixed-use
prototype IDF DOES exist in this repo: the TallBuilding/SuperTallBuilding v242 towers under
Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/ carry native Tag-2-tagged Spaces for
all four channels (AUDIT-W Tag-2 census, job 1169582/1169584: Tall = 164 Spaces total, 30
residential [27 "HighriseApartment Apartment" + 3 "HighriseApartment Corridor"/"HighriseApartment
Office" common-area] / 33 office / 9 retail / 25 hotel / 63 service_MEP / 4 unmapped plenum;
re-verified locally 2026-07-28 by direct Space-object count against the same file, see Step8_docs
Progress Log). This module has since been exercised against it (AUDIT-W 9P/1W/0F, PROBES
23P/0W/2F). The original (2026-07-23) note is preserved below for provenance only -- do not
trust its "no prototype" claim.

Original note (2026-07-23, STALE, see correction above): "no Tag-2-routable mixed-use prototype
IDF exists anywhere in this repo yet (confirmed by Step-7 --audit; see
3rdJ_07_bemIntegration_4split.md Progress Log). This module is therefore UNTESTED against a real
IDF -- the W-section dry-run wiring audit in the Step-7 validator is PENDING for exactly this
reason." Field names / dispatch logic follow the v24.2 conventions already proven in
office_integration.py (Leg-2, post-2026-07-02) and the per-Space multi-zone replication pattern
in eSim_bem_utils_3J/integration.py (post-multizone-fix, 2026-07-15).

2026-07-23 built.
"""
from __future__ import annotations
import hashlib
import os
import re
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_STAFF_SHOULDER_BASELINE_THRESHOLD = 0.10   # H3/R5

# v24.2 field names only (Leg-2 zone-field bug, OD lesson)
_ZONE_NAME_FIELDS = (
    "Zone_or_ZoneList_or_Space_or_SpaceList_Name",  # E+ v24.2+ (the ONLY correct field)
    "Zone_or_ZoneList_Name",                         # E+ <= 9.x (legacy fallback, flagged by W6)
    "Zone_Name",
)
_PRE_V242_FIELD_NAMES = {"Zone_or_ZoneList_Name", "Zone_Name"}  # W6 audit: must be 0 hits

# Tag-2 routing table (exact-match sets, verbatim from the runbook)
TAG2_RESIDENTIAL = {"HighriseApartment Apartment"}
TAG2_RESIDENTIAL_COMMON = {"HighriseApartment Corridor", "HighriseApartment Office"}
TAG2_OFFICE = {"OpenOffice", "ClosedOffice"}
TAG2_OFFICE_SUPPORT = {"Conference", "Classroom", "Dining", "Restroom"}
TAG2_RETAIL = {"Retail Retail", "Retail Back_Space", "Retail Point_of_Sale", "Retail Entry"}
TAG2_HOTEL_GUESTROOM = {"LargeHotel GuestRoom5", "LargeHotel GuestRoom6", "LargeHotel GuestRoom7"}
TAG2_HOTEL_SUPPORT = {"LargeHotel Banquet", "LargeHotel Cafe", "LargeHotel Kitchen",
                       "LargeHotel Lobby", "LargeHotel Laundry", "LargeHotel Storage",
                       "LargeHotel Corridor", "LargeHotel Retail"}
TAG2_SERVICE_MEP = {"Corridor", "Storage", "Elec/MechRoom", "Elevator Shaft",
                     "Elevator Lobby", "Plenum Space Type", "Main Electrical",
                     "Main Mechanical", "Elevator Machine Room"}

# ---------------------------------------------------------------------------
# OD-8R-L3 residential condo/apartment filter -- values READ FROM DATA, not guessed.
#
# BEM_Schedules_4split_2022.csv (23,115 unique SIM_HH_ID), value counts printed and verified
# 2026-07-28:
#   DTYPE  : SingleD=12,939  MidRise=4,836  OtherDwelling=3,001  HighRise=2,339
#   CONDO  : 0=19,909  1=3,206  (binary tenure flag)
#   crosstab DTYPE x CONDO: CONDO=1 rows exist under EVERY DTYPE, including SingleD (157) --
#     i.e. CONDO is a TENURE attribute (owned-as-condominium), cutting across building form; it
#     does NOT by itself identify apartment-BUILDING dwellings (a "condo" can be a townhouse).
#
# DTYPE provenance (3rdJ_07_aug_to_bem_4split.py::dtype_label): code 2 = Census "apartment
# building" dwelling structure, further split into HighRise/MidRise by BEDRM (<=1 bedroom ->
# HighRise proxy, >1 -> MidRise); code 1 = SingleD; code 3 = OtherDwelling (row house / duplex /
# mobile, NOT an apartment building).
#
# Adopted filter: DTYPE in {"HighRise", "MidRise"} -- both are the two BEDRM-driven subsets of
# the SAME underlying Census "apartment building" category, i.e. exactly "apartment dwellings"
# regardless of tenure. This is the correct population for a HighriseApartment tower archetype:
# it includes rented AND condo-owned apartment units (both are legitimate tower occupants) and
# excludes single-detached houses and row/duplex/mobile homes (physically the wrong building
# form for a tower). CONDO is deliberately NOT used as an additional AND/OR filter: ANDing would
# drop the majority of apartment dwellers who rent (no reason to exclude them); ORing would admit
# non-apartment condo dwellings (SingleD/OtherDwelling townhouse condos) into a highrise tower
# pool. Bedroom-count matching to the prototype mix is explicitly NOT adopted (locked, would be
# a new OD) -- BEDRM plays no role beyond having already produced the HighRise/MidRise label.
#
# Apartment pool size at this filter (2022 product): 4,836 + 2,339 = 7,175 households, far more
# than the largest known residential-Space count in any tower IDF (27, TallBuilding v24.2) --
# ample headroom for a no-replacement draw.
RESIDENTIAL_DTYPE_APARTMENT = ("HighRise", "MidRise")

_CHANNEL_OF_TAG2 = {}
for _tag in TAG2_RESIDENTIAL:
    _CHANNEL_OF_TAG2[_tag] = "residential"
for _tag in TAG2_RESIDENTIAL_COMMON:
    _CHANNEL_OF_TAG2[_tag] = "residential_common"
for _tag in TAG2_OFFICE | TAG2_OFFICE_SUPPORT:
    _CHANNEL_OF_TAG2[_tag] = "office"
for _tag in TAG2_RETAIL:
    _CHANNEL_OF_TAG2[_tag] = "retail"
for _tag in TAG2_HOTEL_GUESTROOM:
    _CHANNEL_OF_TAG2[_tag] = "hotel"
for _tag in TAG2_HOTEL_SUPPORT:
    _CHANNEL_OF_TAG2[_tag] = "hotel_support"
for _tag in TAG2_SERVICE_MEP:
    _CHANNEL_OF_TAG2[_tag] = "service_mep"


def classify_tag2(tag2: str) -> str:
    """Exact-match dispatch (NOT substring) -> one of residential/residential_common/office/
    office_support/retail/hotel/hotel_support/service_mep/unknown."""
    return _CHANNEL_OF_TAG2.get(str(tag2).strip(), "unknown")


def _get_zone_name(obj) -> str:
    for f in _ZONE_NAME_FIELDS:
        v = getattr(obj, f, "")
        if v:
            return str(v)
    return ""


def _find_idd(idf_path: str) -> str:
    env_idd = os.environ.get("EPLUS_IDD", "")
    if env_idd and os.path.exists(env_idd):
        return env_idd
    candidates = [
        os.path.join(os.path.dirname(idf_path), "Energy+.idd"),
        os.path.join(os.path.dirname(idf_path), "..", "Energy+.idd"),
        "Energy+.idd",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    try:
        import eppy
        bundled = os.path.join(os.path.dirname(eppy.__file__), "resources", "iddfiles",
                               "Energy+9-0-0.idd")
        if os.path.exists(bundled):
            return bundled
    except Exception:
        pass
    raise FileNotFoundError(
        "Energy+.idd not found near the IDF. Place the v24.2 Energy+.idd next to the IDF or "
        "export EPLUS_IDD=/path/Energy+.idd."
    )


# ---------------------------------------------------------------------------
# Schedule:Compact builders
# ---------------------------------------------------------------------------
def _build_compact_fields_2dt(name: str, wd_vals: list, we_vals: list, type_limit: str = "Fraction") -> list:
    """Schedule:Compact with 2 day-types (Weekdays / Weekends+Holidays+AllOtherDays).

    type_limit defaults to "Fraction" (office/retail/hotel multiplier semantics, unchanged
    behaviour for all existing callers that omit it). Residential passes "Any Number" for the
    Metabolic_Rate (Activity_Level_Schedule) carrier, whose units are W/person, not a 0-1
    fraction -- OD-8R-L3, added 2026-07-28.
    """
    fields = [name, type_limit, "Through: 12/31", "For: Weekdays SummerDesignDay WinterDesignDay"]
    for h, v in enumerate(wd_vals):
        fields += [f"Until: {h+1:02d}:00", f"{v:.4f}"]
    fields += ["For: Weekends Holidays AllOtherDays"]
    for h, v in enumerate(we_vals):
        fields += [f"Until: {h+1:02d}:00", f"{v:.4f}"]
    return fields


# ---------------------------------------------------------------------------
# FINDING 9 (2026-08-02): per-day-type profiles, read AND written
# ---------------------------------------------------------------------------
# DEFECT: `_week_profiles` took the weekend profile as `sun or sat` and `_schedule_daytype_profiles`
# as "first of Weekend/Saturday/Sunday wins", then `_build_compact_fields_2dt` wrote that ONE
# profile to "For: Weekends Holidays AllOtherDays". So whenever a prototype's Saturday and Sunday
# differ, Saturday silently received Sunday's curve -- and Holidays received it too. T9-13 is
# specified to carry the intra-day SHAPE through untouched and to be an exact no-op at r = 1, and
# it was neither for those prototypes.
#
# Measured on the real tower (smoke cells, job 1171438 + diagnosis 1171445), as annual DHW volume
# at r = 1.000 where the answer must be exactly 1.0000:
#     RetailStandalone BLDG_SWH_SCH   0.9234      OfficeLarge BLDG_SWH_SCH   0.9524
#     HotelLarge BLDG_SWH_SCH         0.9953      (Sat == Sun prototypes: 1.0000, unaffected)
# Predicted from the schedules alone, then confirmed against the simulated energy to three
# decimals -- so this is the mechanism, not a candidate for it.
#
# The fix keeps every day type distinct on the way in and on the way out. `wd`/`we` retain their
# exact former meaning so nothing outside T9-13 shifts; the new `by_daytype` key is additive.
_WEEKDAY_DAYTYPES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
_ALL_DAYTYPES = _WEEKDAY_DAYTYPES + ("Saturday", "Sunday", "Holidays")


def _daytypes_for_tokens(toks):
    """EnergyPlus `For:` tokens -> (concrete day types named, is_fill).

    `is_fill` marks AllDays / AllOtherDays: those fill day types no explicit block claimed and
    must never overwrite one that a specific block did. Design-day-ONLY blocks return ().
    """
    toks = [str(t).strip().upper() for t in toks if str(t).strip()]
    if not toks or all(t in _DESIGN_DAYTYPES for t in toks):
        return (), False
    j = " ".join(toks)
    if "ALLDAYS" in j or "ALLOTHERDAYS" in j:
        return tuple(_ALL_DAYTYPES), True
    out = set()
    if "WEEKDAY" in j:                       # WEEKDAY / WEEKDAYS
        out |= set(_WEEKDAY_DAYTYPES)
    if "WEEKEND" in j:                       # WEEKEND / WEEKENDS
        out |= {"Saturday", "Sunday"}
    if "HOLIDAY" in j:                       # HOLIDAY / HOLIDAYS
        out |= {"Holidays"}
    for d in _ALL_DAYTYPES:
        if d.upper() in j:
            out.add(d)
    return tuple(d for d in _ALL_DAYTYPES if d in out), False


def _fill_daytypes(by_daytype, wd_fallback=None, we_fallback=None):
    """Complete a partial {day type: [24]} map so every one of the 8 day types is present.

    Weekday-class gaps fall back to a resolved weekday, weekend/holiday gaps to a resolved
    weekend day. Returns (complete_map, filled_daytypes) -- the second element is reported in the
    provenance so a fallback is never invisible.
    """
    out = dict(by_daytype)
    wd = wd_fallback or out.get("Monday") or next(
        (out[d] for d in _WEEKDAY_DAYTYPES if d in out), None)
    we = we_fallback or out.get("Sunday") or out.get("Saturday") or wd
    if wd is None:
        wd = we
    if wd is None:
        return None, []
    filled = []
    for d in _ALL_DAYTYPES:
        if d not in out or out[d] is None:
            out[d] = list(wd if d in _WEEKDAY_DAYTYPES else we)
            filled.append(d)
    return out, filled


def _build_compact_fields_by_daytype(name: str, by_daytype: dict,
                                     type_limit: str = "Fraction") -> list:
    """Schedule:Compact carrying ONE block per DISTINCT day-type profile (FINDING 9).

    Day types whose profiles are identical are grouped onto a single `For:` line, so a prototype
    that genuinely has one weekday and one weekend curve still emits the same two blocks it always
    did -- the shape only multiplies when the source really does distinguish more days.
    Design days ride with the weekday group (the convention `_build_compact_fields_2dt` used), and
    the final block carries `AllOtherDays` so coverage is total.
    """
    missing = [d for d in _ALL_DAYTYPES if d not in by_daytype or by_daytype[d] is None]
    if missing:
        raise AssertionError(
            f"_build_compact_fields_by_daytype('{name}'): day types {missing} have no profile. "
            f"Every day type must be explicit -- falling back silently is FINDING 9.")

    groups = []                                   # [[daytypes], rounded vals]
    for d in _ALL_DAYTYPES:
        vals = [round(float(x), 4) for x in by_daytype[d]]
        for g in groups:
            if g[1] == vals:
                g[0].append(d)
                break
        else:
            groups.append([[d], vals])

    fields = [name, type_limit, "Through: 12/31"]
    for i, (dts, vals) in enumerate(groups):
        toks = (["Weekdays"] if set(dts) >= set(_WEEKDAY_DAYTYPES)
                else [d for d in dts if d in _WEEKDAY_DAYTYPES])
        toks += [d for d in dts if d not in _WEEKDAY_DAYTYPES]
        if any(d in _WEEKDAY_DAYTYPES for d in dts):
            toks += ["SummerDesignDay", "WinterDesignDay"]
        if i == len(groups) - 1:
            toks += ["AllOtherDays"]
        fields.append("For: " + " ".join(toks))
        for h, v in enumerate(vals):
            fields += [f"Until: {h+1:02d}:00", f"{v:.4f}"]
    return fields


def _build_compact_fields_3dt(name: str, wd_vals48: list, sat_vals48: list, sun_vals48: list) -> list:
    """Schedule:Compact with 3 day-types (Weekday / Saturday / Sunday+Holidays), 48 half-hour slots.
    Retail is the only channel needing 3 distinct day-types (Sunday load-bearing, dr_L3-06)."""
    def _half_hour_fields(vals48):
        f = []
        for i, v in enumerate(vals48):
            hh = (i + 1) // 2
            mm = 30 if (i + 1) % 2 == 1 else 0
            # "Until: HH:MM" marks the END of the interval that vals48[i] applies to
            end_h = hh if mm == 30 else hh
            end_m = 30 if (i % 2 == 0) else 0
            eh = i // 2
            em = 30 if i % 2 == 0 else 0
            if em == 30:
                f += [f"Until: {eh:02d}:30", f"{v:.4f}"]
            else:
                f += [f"Until: {eh+1:02d}:00", f"{v:.4f}"]
        return f

    fields = [name, "Fraction", "Through: 12/31", "For: Weekdays"]
    fields += _half_hour_fields(wd_vals48)
    fields += ["For: Saturday"]
    fields += _half_hour_fields(sat_vals48)
    fields += ["For: Sunday Holidays AllOtherDays"]
    fields += _half_hour_fields(sun_vals48)
    return fields


def _build_compact_fields_monthly(name: str, monthly_wd48: dict, monthly_we48: dict) -> list:
    """Hotel: 12 monthly blocks in ONE annual Schedule:Compact (Through: fields per month),
    each block carrying WD + WE 48-half-hour-slot day types. monthly_wd48/we48: {month(1-12): [48 floats]}."""
    import calendar
    fields = [name, "Fraction"]

    def _half_hour_fields(vals48):
        f = []
        for i, v in enumerate(vals48):
            eh = i // 2
            em = 30 if i % 2 == 0 else 0
            if em == 30:
                f += [f"Until: {eh:02d}:30", f"{v:.4f}"]
            else:
                f += [f"Until: {eh+1:02d}:00", f"{v:.4f}"]
        return f

    for month in range(1, 13):
        last_day = calendar.monthrange(2023, month)[1]  # non-leap reference year
        fields += [f"Through: {month:02d}/{last_day:02d}"]
        fields += ["For: Weekdays SummerDesignDay WinterDesignDay"]
        fields += _half_hour_fields(monthly_wd48[month])
        fields += ["For: Weekends Holidays AllOtherDays"]
        fields += _half_hour_fields(monthly_we48[month])
    return fields


# ---------------------------------------------------------------------------
# Standby-floor preservation for LIGHTS / ELECTRICEQUIPMENT  (T9-9, 2026-07-31)
# ---------------------------------------------------------------------------
# DEFECT (S9D-8, improvements/3rdJ_L3_improvements_step9.md): the dispatch loop below used to
# write the SAME occupancy Schedule:Compact to PEOPLE *and* LIGHTS *and* ELECTRICEQUIPMENT.
# People genuinely should follow occupancy; plug and lighting loads must not. Measured on
# campaign_local_v2/campaign_cf69d508, zone OpenOffice, weekday: the injection overwrote
# `NECB-A-Electric-Equipment` (mean 0.513, night floor 0.20) and `OfficeLarge
# BLDG_LIGHT_SCH_2013` (floor 0.0453) with MXU_Office_People_* (mean 0.187, floor 0.0031).
# Office equipment energy fell 59 % and lighting 45 % while occupancy fell only 48 %; office
# EUI fell 20 % and retail 23.5 %. The hotel channel was unharmed ONLY because hotel guest-room
# occupancy never drops below 0.20 by itself -- the injector applied no floor anywhere.
#
# FIX: keep the People wiring byte-identical, and give LIGHTS/ELECTRICEQUIPMENT a DERIVED
# schedule that re-imposes the standby floor of the prototype schedule it replaces:
#
#     f_load(t) = floor + (1 - floor) * occ(t)
#
# `floor` is READ FROM THE SCHEDULE BEING REPLACED (never hard-coded), so each load object
# keeps its own prototype's off-hours baseline: office equipment 0.200, office lights 0.0453,
# retail lights 0.05. occ(t) is the un-normalised GSS occupancy fraction, so the channel levers
# still move the result and G8o/G8r/G8h keep their signal.
#
# NOT chosen, and deliberately left to the user (open modelling question recorded in the
# improvements doc): whether LIGHTS should also keep its prototype PEAK. Open-plan lighting is
# largely zone-switched, so real offices at 45 % occupancy do not run 45 % of their lights; the
# prototype peaks at 0.815 regardless of occupancy. Re-imposing the floor alone leaves lighting
# still strongly occupancy-coupled. Encoding a lighting-diversity model is a research decision,
# not a bug fix, so it is NOT baked in here.
#
# `preserve_load_standby_floor=False` reproduces the pre-fix behaviour EXACTLY, so the closed
# campaign_cf69d508 artefacts stay reproducible.

_SCHED_CLASSES = ("SCHEDULE:COMPACT", "SCHEDULE:CONSTANT", "SCHEDULE:YEAR",
                  "SCHEDULE:WEEK:DAILY", "SCHEDULE:WEEK:COMPACT", "SCHEDULE:DAY:HOURLY",
                  "SCHEDULE:DAY:INTERVAL", "SCHEDULE:DAY:LIST", "SCHEDULE:FILE")

# Schedule:Week:Daily field order after Name: Sunday, Monday, ..., Saturday, Holiday,
# SummerDesignDay, WinterDesignDay, CustomDay1, CustomDay2. Indices into obj[] (obj[0]=class,
# obj[1]=Name) -> the two design-day slots are obj[10] and obj[11].
_WEEKDAILY_DESIGNDAY_IDX = (10, 11)


def _find_schedule(idf, name: str):
    """Return the schedule object called `name` (any Schedule:* class), or None."""
    if not name:
        return None
    tgt = str(name).strip().lower()
    for cls in _SCHED_CLASSES:
        for o in idf.idfobjects.get(cls, []):
            if len(o.obj) > 1 and str(o.obj[1]).strip().lower() == tgt:
                return o
    return None


def _floats(seq):
    out = []
    for v in seq:
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def _day_schedule_values(obj):
    """All values of a Schedule:Day:* object. Returns None if unparseable/empty."""
    cls = obj.obj[0].strip().lower()
    if cls == "schedule:day:hourly":
        vals = _floats(obj.obj[3:27])                       # 24 hourly values
    elif cls == "schedule:day:interval":
        vals = _floats(obj.obj[5::2])                       # Time_n / Value_n pairs from idx 4
    elif cls == "schedule:day:list":
        vals = _floats(obj.obj[5:])                         # values after Minutes_per_Item
    else:
        return None
    return vals or None


def _day_schedule_agg(obj, agg):
    """`agg` (min or max) over a Schedule:Day:* object's values. None if unparseable."""
    vals = _day_schedule_values(obj)
    return agg(vals) if vals else None


def _schedule_extremum(idf, name: str, agg, _depth: int = 0):
    """`agg` (min -> standby floor, max -> peak) over `name`'s values, EXCLUDING design days.

    Design days must be excluded or the floor fix silently no-ops: `OfficeLarge
    BLDG_LIGHT_SCH_2013 Winter Design Day` is a flat 0, so a naive global minimum returns 0.0 and
    floor + (1-floor)*occ collapses back to occ. Verified against the real prototype IDF. The
    same exclusion matters for the peak (T9-10): a design day pinned at 1.0 would report a peak
    the schedule never reaches in an ordinary week.

    Returns (value: float, provenance: str) or (None, reason: str).
    """
    if _depth > 6:
        return None, "schedule reference nesting too deep"
    if str(name).strip().upper().startswith("MXU_"):
        # already injected -- the prototype floor is no longer recoverable from this IDF
        return None, "schedule already injected (MXU_*), prototype floor unrecoverable"
    obj = _find_schedule(idf, name)
    if obj is None:
        return None, f"schedule '{name}' not found in IDF"
    cls = obj.obj[0].strip().lower()

    if cls == "schedule:constant":
        vals = _floats(obj.obj[3:4])
        return (agg(vals), f"{cls}") if vals else (None, "Schedule:Constant has no value")

    if cls == "schedule:file":
        return None, "Schedule:File -- values live outside the IDF, not resolvable"

    if cls == "schedule:compact":
        # walk "For: <daytypes>" blocks, skip any block naming a design day
        vals, skip = [], False
        for f in obj.obj[3:]:
            s = str(f).strip()
            low = s.lower()
            if low.startswith("for:"):
                skip = "designday" in low.replace(" ", "")
                continue
            if low.startswith(("through:", "until:", "interpolate")):
                continue
            if skip:
                continue
            try:
                vals.append(float(s))
            except ValueError:
                pass
        return (agg(vals), f"{cls} (design days excluded)") if vals else \
               (None, "Schedule:Compact yielded no non-design-day values")

    if cls in ("schedule:day:hourly", "schedule:day:interval", "schedule:day:list"):
        m = _day_schedule_agg(obj, agg)
        return (m, cls) if m is not None else (None, f"{cls} unparseable")

    if cls == "schedule:week:daily":
        vals = []
        for i, dayname in enumerate(obj.obj[2:14], start=2):
            if i in _WEEKDAILY_DESIGNDAY_IDX:
                continue
            d = _find_schedule(idf, dayname)
            if d is not None:
                m = _day_schedule_agg(d, agg)
                if m is not None:
                    vals.append(m)
        return (agg(vals), "schedule:week:daily (design days excluded)") if vals else \
               (None, "Schedule:Week:Daily resolved no day schedules")

    if cls == "schedule:week:compact":
        vals = []
        pairs = obj.obj[2:]
        for i in range(0, len(pairs) - 1, 2):
            daytypes, dayname = str(pairs[i]).lower(), pairs[i + 1]
            if "designday" in daytypes.replace(" ", ""):
                continue
            d = _find_schedule(idf, dayname)
            if d is not None:
                m = _day_schedule_agg(d, agg)
                if m is not None:
                    vals.append(m)
        return (agg(vals), "schedule:week:compact (design days excluded)") if vals else \
               (None, "Schedule:Week:Compact resolved no day schedules")

    if cls == "schedule:year":
        # Name, TypeLimits, then repeating (Week_Name, StartMonth, StartDay, EndMonth, EndDay)
        vals, prov = [], None
        for i in range(3, len(obj.obj), 5):
            f, p = _schedule_extremum(idf, obj.obj[i], agg, _depth + 1)
            if f is not None:
                vals.append(f)
                prov = p
        return (agg(vals), f"schedule:year -> {prov}") if vals else \
               (None, "Schedule:Year resolved no week schedules")

    return None, f"unsupported schedule class '{cls}'"


def _schedule_standby_floor(idf, name: str, _depth: int = 0):
    """Off-hours floor of `name`, design days excluded. (floor, provenance) | (None, reason)."""
    return _schedule_extremum(idf, name, min, _depth)


def _schedule_peak(idf, name: str, _depth: int = 0):
    """Peak of `name`, design days excluded. (peak, provenance) | (None, reason)."""
    return _schedule_extremum(idf, name, max, _depth)


# ---------------------------------------------------------------------------
# TIME-WEIGHTED day-type profiles  (T9-13, 2026-08-01)
# ---------------------------------------------------------------------------
# `_schedule_extremum` above collects a FLAT list of a schedule's values and applies min/max. That
# is exact for an extremum and WRONG for a mean: a Schedule:Compact `Until:` block holds its value
# for the whole span since the previous `Until:`, so a value covering 8 h and a value covering 1 h
# both appear exactly once in that flat list. Any mean taken over it is unweighted and therefore
# not the schedule's mean. T9-13 modulates DAILY VOLUME, which is a mean, so it needs a real
# time-weighted expansion. Hence this separate resolver rather than another `agg` passed to
# `_schedule_extremum` -- a mean cannot be retrofitted onto that collector.
_DESIGN_DAYTYPES = ("SUMMERDESIGNDAY", "WINTERDESIGNDAY", "CUSTOMDAY1", "CUSTOMDAY2")


def _expand_compact_daytypes(obj):
    """{(daytype tokens): [24 hourly values]} for a Schedule:Compact, design-day blocks skipped.

    Only the FIRST `Through:` period is expanded. Monthly schedules (hotel) therefore report their
    January block; T9-13 uses this for a day-type RATIO, and the ratio's reference and target are
    read the same way, so a consistent single-period read is sufficient and is recorded as such in
    the provenance. Returns {} if nothing parses.
    """
    out, cur, hour, until_h = {}, None, 0, None
    seen_through = 0
    for f in obj.obj[3:]:
        s = str(f).strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("through:"):
            seen_through += 1
            if seen_through > 1:
                break
            continue
        if low.startswith("interpolate"):
            continue
        if low.startswith("for:"):
            toks = [t for t in re.split(r"[\s,]+", s.split(":", 1)[1].strip().upper()) if t]
            # Skip a block only if it is design-day-ONLY. Prototypes routinely write
            # "For: Weekdays SummerDesignDay WinterDesignDay" as a single block: those values DO
            # apply on ordinary weekdays, so dropping the block on the mere presence of a
            # design-day token would discard the weekday profile entirely. (`_schedule_extremum`
            # uses the looser any-token rule; it is left exactly as is -- it is validated against
            # the prototypes for T9-9/T9-10 floors and peaks, and changing it would silently move
            # numbers in closed campaigns. The two rules differ deliberately.)
            cur = None if (toks and all(t in _DESIGN_DAYTYPES for t in toks)) else tuple(toks)
            if cur is not None:
                out.setdefault(cur, [None] * 24)
            hour, until_h = 0, None
            continue
        if low.startswith("until:"):
            t = s.split(":", 1)[1].strip()
            parts = t.split(":")
            try:
                hh = int(parts[0])
                mm = int(parts[1]) if len(parts) > 1 else 0
            except ValueError:
                until_h = None
                continue
            # "Until: HH:MM" ends the interval; round UP to whole hours for a 24-slot grid
            until_h = min(24, hh + (1 if mm > 0 else 0))
            continue
        if cur is None or until_h is None:
            continue
        try:
            v = float(s)
        except ValueError:
            continue
        for h in range(hour, until_h):
            out[cur][h] = v
        hour, until_h = until_h, None
    return {k: v for k, v in out.items() if all(x is not None for x in v)}


def _day_profile_24(obj):
    """A Schedule:Day:* object expanded to 24 TIME-WEIGHTED hourly values, or None.

    Needed because every DHW flow-fraction schedule in the tower resolves through
    Schedule:Year -> Schedule:Week:Daily -> Schedule:Day:Interval (measured on the real IDF,
    job 1171059: 27 residential + 18 commercial WaterUse:Equipment objects, ALL Schedule:Year).
    A Schedule:Day:Interval holds each value until its stated time, so, exactly as for
    Schedule:Compact, listing order is not time weighting.
    """
    cls = obj.obj[0].strip().lower()
    if cls == "schedule:day:hourly":
        v = _floats(obj.obj[3:27])
        return v if len(v) == 24 else None
    if cls == "schedule:day:list":
        v = _floats(obj.obj[5:])
        if not v:
            return None
        try:
            mpi = float(str(obj.obj[4]).strip() or 60.0)
        except (ValueError, IndexError):
            mpi = 60.0
        per_hour = max(1, int(round(60.0 / mpi))) if mpi > 0 else 1
        out = []
        for h in range(24):
            seg = v[h * per_hour:(h + 1) * per_hour]
            out.append(sum(seg) / len(seg) if seg else v[-1])
        return out
    if cls == "schedule:day:interval":
        times, vals = obj.obj[4::2], obj.obj[5::2]
        out, hour = [None] * 24, 0
        for t, val in zip(times, vals):
            s = str(t).strip().upper().replace("UNTIL:", "").strip()
            if not s:
                continue
            try:
                parts = s.split(":")
                end = min(24, int(parts[0]) + (1 if len(parts) > 1 and int(parts[1]) > 0 else 0))
                fv = float(str(val).strip())
            except (ValueError, IndexError):
                continue
            for h in range(hour, end):
                out[h] = fv
            hour = end
        if hour < 24 and hour > 0:
            for h in range(hour, 24):
                out[h] = out[hour - 1]
        return out if all(x is not None for x in out) else None
    return None


def _week_profiles(idf, wk_obj, _depth: int = 0):
    """({'wd': [24], 'we': [24]}, note) from a Schedule:Week:Daily / :Compact object, or (None, r).

    Schedule:Week:Daily field order is Sunday, Monday, ..., Saturday, Holiday, then the design
    days. Weekday is taken from MONDAY and weekend from SUNDAY (Saturday as fallback) -- the
    design-day slots are never read.
    """
    cls = wk_obj.obj[0].strip().lower()
    if cls == "schedule:week:daily":
        names = [str(x).strip() for x in wk_obj.obj[2:14]]
        if len(names) < 9:
            return None, "Schedule:Week:Daily has too few day fields"
        # Field order: Sunday, Monday..Friday, Saturday, Holiday, then the design/custom days.
        slots = {"Sunday": names[0], "Monday": names[1], "Tuesday": names[2],
                 "Wednesday": names[3], "Thursday": names[4], "Friday": names[5],
                 "Saturday": names[6], "Holidays": names[7]}
        by = {}
        for dt, dn in slots.items():
            d = _find_schedule(idf, dn) if dn else None
            p = _day_profile_24(d) if d is not None else None
            if p is not None:
                by[dt] = p
        if not by:
            return None, "no Sunday..Saturday/Holiday day schedule resolved"
        p_wd = by.get("Monday")
        p_we = by.get("Sunday") or by.get("Saturday")
        if p_wd is None and p_we is None:
            return None, "no Monday/Sunday day schedule resolved"
        by, filled = _fill_daytypes(by, p_wd, p_we)
        n_distinct = len({tuple(round(float(x), 6) for x in v) for v in by.values()})
        note = (f"week:daily(mon='{slots['Monday']}', sat='{slots['Saturday']}', "
                f"sun='{slots['Sunday']}', hol='{slots['Holidays']}'; "
                f"{n_distinct} distinct day profiles"
                + (f"; FILLED {filled}" if filled else "") + ")")
        return {"wd": p_wd or p_we, "we": p_we or p_wd, "by_daytype": by}, note
    if cls == "schedule:week:compact":
        wd = we = None
        by, claimed, fills = {}, set(), []
        i = 2
        flds = [str(x).strip() for x in wk_obj.obj[2:]]
        while i - 2 < len(flds) - 1:
            key, dayname = flds[i - 2].upper(), flds[i - 1]
            i += 2
            if not key.startswith("FOR"):
                continue
            toks = key.split(":", 1)[1] if ":" in key else key
            d = _find_schedule(idf, dayname)
            prof = _day_profile_24(d) if d is not None else None
            if prof is None:
                continue
            if any(t in toks for t in ("DESIGNDAY", "CUSTOMDAY")):
                continue
            dts, is_fill = _daytypes_for_tokens(re.split(r"[\s,]+", toks.strip()))
            if is_fill:
                fills.append((dts, prof))          # applied after every explicit block
            else:
                for dt in dts:
                    if dt not in claimed:
                        by[dt] = prof
                        claimed.add(dt)
            if "WEEKDAY" in toks or "ALLDAYS" in toks or "ALLOTHERDAYS" in toks:
                wd = wd or prof
            if any(t in toks for t in ("WEEKEND", "SUNDAY", "SATURDAY")) or "ALLDAYS" in toks \
                    or "ALLOTHERDAYS" in toks:
                we = we or prof
        for dts, prof in fills:                    # AllDays/AllOtherDays fill only the gaps
            for dt in dts:
                by.setdefault(dt, prof)
        if wd is None and we is None:
            return None, "Schedule:Week:Compact resolved no day profile"
        by, filled = _fill_daytypes(by, wd, we)
        n_distinct = len({tuple(round(float(x), 6) for x in v) for v in by.values()})
        return ({"wd": wd or we, "we": we or wd, "by_daytype": by},
                f"week:compact ({n_distinct} distinct day profiles"
                + (f"; FILLED {filled}" if filled else "") + ")")
    return None, f"unsupported week class '{cls}'"


def _compact_daytype_map(obj):
    """{day type: [24]} for a Schedule:Compact object, or None.

    Used by D9 to re-expand a schedule the injector WROTE, which `_schedule_daytype_profiles`
    deliberately refuses (its MXU_* guard exists so a prototype is never read back off an already
    injected schedule). D9 wants exactly that read, from the file, so it goes through here.
    """
    if obj is None or obj.obj[0].strip().lower() != "schedule:compact":
        return None
    blocks = _expand_compact_daytypes(obj)
    if not blocks:
        return None
    by, claimed, fills = {}, set(), []
    for toks, vals in blocks.items():
        dts, is_fill = _daytypes_for_tokens(toks)
        if is_fill:
            fills.append((dts, vals))
        else:
            for dt in dts:
                if dt not in claimed:
                    by[dt] = vals
                    claimed.add(dt)
    for dts, vals in fills:
        for dt in dts:
            by.setdefault(dt, vals)
    return by or None


def _schedule_daytype_profiles(idf, name: str, _depth: int = 0):
    """({'wd': [24], 'we': [24]}, provenance) | (None, reason) -- time-weighted, design days out.

    'wd' is the Weekdays block, 'we' the Weekends/AllOtherDays block; an AllDays block fills both.
    Supports Schedule:Compact, :Constant and the Year -> Week:Daily/:Compact -> Day:* chain, which
    is what the real prototype DHW schedules actually use.
    """
    if _depth > 6:
        return None, "schedule reference nesting too deep"
    if str(name).strip().upper().startswith("MXU_"):
        return None, "schedule already injected (MXU_*), prototype profile unrecoverable"
    obj = _find_schedule(idf, name)
    if obj is None:
        return None, f"schedule '{name}' not found in IDF"
    cls = obj.obj[0].strip().lower()
    if cls == "schedule:constant":
        vals = _floats(obj.obj[3:4])
        if not vals:
            return None, "Schedule:Constant has no value"
        flat = [vals[0]] * 24
        return ({"wd": flat, "we": list(flat),
                 "by_daytype": {d: list(flat) for d in _ALL_DAYTYPES}}, "schedule:constant")
    if cls == "schedule:file":
        return None, "Schedule:File -- values live outside the IDF, not resolvable"
    if cls in ("schedule:day:hourly", "schedule:day:interval", "schedule:day:list"):
        p = _day_profile_24(obj)
        if not p:
            return None, f"{cls} unparseable"
        return {"wd": p, "we": list(p),
                "by_daytype": {d: list(p) for d in _ALL_DAYTYPES}}, cls
    if cls in ("schedule:week:daily", "schedule:week:compact"):
        prof, note = _week_profiles(idf, obj, _depth + 1)
        return (prof, note) if prof else (None, note)
    if cls == "schedule:year":
        # Fields after (Name, TypeLimits) repeat in 5s: WeekName, StartMonth, StartDay, EndMonth,
        # EndDay. Take the FIRST period, the same single-period convention the compact reader uses;
        # the ratio's reference and target are both read this way, so the read stays consistent.
        flds = [str(x).strip() for x in obj.obj[3:]]
        for i in range(0, len(flds), 5):
            wk = _find_schedule(idf, flds[i]) if flds[i] else None
            if wk is None:
                continue
            prof, note = _week_profiles(idf, wk, _depth + 1)
            if prof:
                return prof, f"schedule:year -> '{flds[i]}' {note}"
        return None, "Schedule:Year resolved no usable week schedule"
    if cls != "schedule:compact":
        return None, f"class '{cls}' not supported by the time-weighted profile resolver"
    blocks = _expand_compact_daytypes(obj)
    if not blocks:
        return None, "Schedule:Compact yielded no complete non-design-day day-type block"
    wd = we = None
    by, claimed, fills = {}, set(), []
    for toks, vals in blocks.items():
        j = " ".join(toks)
        # FINDING 9: claim each named day type separately instead of collapsing to one weekend.
        dts, is_fill = _daytypes_for_tokens(toks)
        if is_fill:
            fills.append((dts, vals))
        else:
            for dt in dts:
                if dt not in claimed:
                    by[dt] = vals
                    claimed.add(dt)
        if "ALLDAYS" in j or "ALLOTHERDAYS" in j:
            wd = wd if wd is not None else vals
            we = we if we is not None else vals
        if "WEEKDAY" in j or "WEEKDAYS" in j:
            wd = vals
        if "WEEKEND" in j or "SATURDAY" in j or "SUNDAY" in j:
            we = we if we is not None else vals
    for dts, vals in fills:
        for dt in dts:
            by.setdefault(dt, vals)
    if wd is None and we is None:
        return None, "no Weekday/Weekend/AllDays block resolved"
    wd = wd if wd is not None else we
    we = we if we is not None else wd
    by, filled = _fill_daytypes(by, wd, we)
    n_distinct = len({tuple(round(float(x), 6) for x in v) for v in by.values()})
    return ({"wd": wd, "we": we, "by_daytype": by},
            f"schedule:compact (design days excluded, {len(blocks)} blocks, "
            f"{n_distinct} distinct day profiles"
            + (f"; FILLED {filled}" if filled else "") + ")")


def apply_standby_floor(occ_vals, floor: float):
    """f_load(t) = floor + (1 - floor) * occ(t), elementwise, clipped to [0, 1].

    occ_vals may be a flat list (office 24h / retail 48-slot) or a {month: [...]} dict (hotel).
    """
    if isinstance(occ_vals, dict):
        return {k: apply_standby_floor(v, floor) for k, v in occ_vals.items()}
    return [min(1.0, max(0.0, floor + (1.0 - floor) * float(v))) for v in occ_vals]


def _floor_key(floor: float) -> str:
    """Stable, filename-safe token for a floor value -> permille, e.g. 0.0453 -> '045'."""
    return f"{int(round(floor * 1000)):03d}"


# FINDING 8 CORRECTION (2026-08-02). The T9-13 derived-schedule cache was keyed on
# (channel, r_wd, r_we) only -- and r_wd/r_we are computed from the CHANNEL's occupancy against
# the CHANNEL's reference, so they are identical for every WaterUse:Equipment object in a
# channel. The SOURCE schedule was not in the key, so `new_wd`/`new_we` (the caller's per-object
# shape) were used only on a cache MISS: every object in a channel collapsed onto ONE schedule,
# built from whichever object the iteration happened to reach first. That is how
# 'Laundry Service Water Use 30.6gpm 180F' ended up carrying the hotel guest-room curve while its
# Peak_Flow_Rate (computed per object) stayed correct.
#
# The fix is to put the source schedule in the key AND in the generated name. The name is where
# it is verifiable after the fact -- D7 re-opens the saved IDF and reads the token back out, so a
# collision can no longer hide inside a dict nobody serialises.
_SCHED_TOKEN_MAXLEN = 40


def _sched_token(proto) -> str:
    """Stable, EnergyPlus-name-safe token identifying a SOURCE schedule.

    Upper-cased, [A-Z0-9] kept, everything else collapsed to '_', truncated to
    `_SCHED_TOKEN_MAXLEN`. Truncation can collide, and a truncation collision would silently
    recreate the exact bug this token exists to fix, so any name that is at risk of truncation
    gets a short deterministic hash of the FULL prototype string appended. The hash is of the
    normalised upper-cased string, i.e. of the same value the cache key uses, so token equality
    and key equality mean the same thing.
    """
    s = str(proto).strip().upper()
    keep = []
    prev_us = False
    for ch in s:
        if ("A" <= ch <= "Z") or ("0" <= ch <= "9"):
            keep.append(ch)
            prev_us = False
        elif not prev_us:
            keep.append("_")
            prev_us = True
    tok = "".join(keep).strip("_")
    if not tok:
        tok = "NOSCHED"
    if len(tok) <= _SCHED_TOKEN_MAXLEN:
        return tok
    h = hashlib.md5(s.encode("utf-8")).hexdigest()[:8].upper()
    return f"{tok[:_SCHED_TOKEN_MAXLEN - 9].rstrip('_')}_{h}"


# ---------------------------------------------------------------------------
# Lighting diversity  (T9-10, 2026-07-31) -- LIGHTS only, opt-in, off by default
# ---------------------------------------------------------------------------
# T9-9 (above) re-imposed the standby floor, which fixed a defect. It did NOT fix a modelling
# error that the defect was hiding: after T9-9 lighting is still `floor + (1-floor)*occ`, i.e.
# strictly proportional to head-count. Real lighting is not. Three channels, three different
# physics -- treating them uniformly is what produced S9D-8 in the first place:
#
#   office  ZONE-COINCIDENCE. Open-plan lighting is switched per ZONE, not per desk. If a
#           switched zone holds n workstations each occupied with probability occ(t), the
#           fraction of zones with >=1 occupant is 1 - (1 - occ)^n. This is derived, not fitted,
#           and the family contains both degenerate cases: n=1 IS the linear model, n->inf is
#           occupancy-insensitive lighting. n is a SENSITIVITY LEVER, defaulted to 1 so that
#           enabling the model changes nothing about office lighting until n is chosen
#           deliberately. ClosedOffice (private office, own switch) is physically n=1.
#
#   retail  OPEN/CLOSED *MIXED WITH* head-count -- see T9-12 below. The original T9-10 form was
#           pure open/closed: g = 1 - staff_shoulder_flag (3rdJ_07_aug_to_bem_4split.py:527,
#           flag=1 <=> NECB baseline <= 0.10 <=> closed/staff-only), loaded by
#           load_retail_series() into "<dt>_staff_shoulder". Its provenance was flagged at the
#           time: the flag comes from the NECB retail baseline PROXY, so the open window is fixed
#           across scenarios and eras, and retail lighting became scenario-invariant. That was
#           argued as an intended physical claim (WFH does not change store hours). THE CAMPAIGN
#           REFUTED IT -- see T9-12. Retained as `retail_mode="open_closed"` for reproducibility
#           of arm B only; it is NOT the model to use.
#
#   hotel   n=1 is already right. One guest room, one occupant, one switch.
#
# PEAK. All three now scale to the prototype's own peak instead of 1.0:
#     f_light(t) = floor + (peak - floor) * g(t)
# `peak` is read from the replaced schedule the same way `floor` is (design days excluded).
# This is a change even at n=1: `OfficeLarge BLDG_LIGHT_SCH_2013` peaks at 0.815, so the T9-9
# form `floor + (1-floor)*occ` lets a fully-occupied office draw MORE lighting power than the
# NECB prototype ever asks for. Because it is a change, the whole model is opt-in:
# `lighting_model=None` (the default) reproduces T9-9 exactly.
#
# ELECTRICEQUIPMENT is deliberately NOT touched by this: plug loads ARE per-person, so the T9-9
# floor form is the correct one there.
#
# EXPECTED CONSEQUENCE, recorded before any simulation so it can be wrong: with office n>1,
# office lighting becomes nearly insensitive to WFH (at occ=0.45, n=8 gives 1-0.55^8 = 0.99).
# That WEAKENS a "WFH cuts office lighting" reading and shifts the WFH signal onto plug loads.
# Post-COVID metered studies report exactly that asymmetry, so it is a finding, not a loss.

LIGHTING_MODEL_ZONE = {
    "office_n": 1,          # zone-coincidence exponent for OpenOffice; 1 == linear (no change)
    "hotel_n": 1,           # one room, one switch -- physically 1, do not raise without reason
    "retail_mode": "open_closed",   # "open_closed" | "open_hours_mix" (T9-12) | "occupancy"
    "retail_k_open": 1.0,   # only read when retail_mode == "open_hours_mix"; 1.0 == open_closed
}

# CALIBRATION of office_n (2026-07-31). n was NOT tuned to make an EUI gate pass -- it was fitted
# against the NECB prototype schedule itself, on data that predates the WFH bundles:
#
#   criterion: run the 2022 OBSERVED office occupancy (office_presence_multiplier_2022.csv,
#              Office_Knowledge / BAND=observed -- a pre-WFH year) through
#              floor + (peak - floor) * (1 - (1 - occ)^n) and ask which n reproduces
#              `OfficeLarge BLDG_LIGHT_SCH_2013`'s own weekday mean of 0.3976.
#
#     n = 1    0.2400   -39.6 %          n = 4    0.4350    +9.4 %
#     n = 2    0.3401   -14.5 %          n = 5    0.4622   +16.2 %
#     n = 3    0.3976    -0.0 %  <--     n = 8    0.5175   +30.2 %
#
# The mean match alone would be one scalar and could be coincidence, so the hourly shape was
# checked too: Pearson r vs the prototype 0.9743 (n=1: 0.9681), RMSE 0.0875 (n=1: 0.2263, a 61 %
# reduction), and the four largest residuals fall at hours 6, 7, 8 and 16 -- the shoulders, where
# a diary-derived arrival ramp is EXPECTED to differ from NECB's step from 0.27 to 0.815.
#
# COST, stated plainly: raising n shrinks the WFH lever on lighting. Span from the 2030
# conservative to the fullyhybrid band -- n=1 -14.7 %, n=2 -11.2 %, n=3 -7.8 %, n=4 -5.0 %,
# n=6 -1.5 %, n=8 +0.2 % (inverted, i.e. pure noise: the lever is gone). n=8, the textbook
# open-plan figure, ALSO overshoots the prototype by 30 % -- it is not usable here. n=3 keeps a
# real, signed WFH signal while matching the prototype. That the WFH response shrinks is the
# model's substantive claim, not a defect: lighting is switched per zone, so plug loads, not
# lights, should carry most of the WFH effect.
LIGHTING_MODEL_CALIBRATED = dict(LIGHTING_MODEL_ZONE, office_n=3)

# ---------------------------------------------------------------------------------------------
# T9-12 (2026-07-31): RETAIL RE-SPECIFICATION. The open/closed form above is WITHDRAWN.
#
# WHY. The 56-cell arm B campaign measured retail `interior_lighting` at 339.0211 GJ in ALL 13
# injected scenarios -- Y2005, Y2022 and every 2030 bundle and sensitivity lever, identical to
# 4 dp (arm A, pure occupancy, spread 80.6 % over the same set). Because `staff_shoulder_flag`
# is a binary flag off the NECB PROXY schedule and carries no occupancy, T9-10 made retail
# lighting invariant to occupancy, to era, and to every lever this study exists to move. It also
# sat +31.3 % above NECB's own retail lighting (339.02 vs 258.28 GJ), since "open" was held at
# full peak with none of NECB's ramps. The retail EUI gate flipped 38/56 -> 56/56 PASS on the
# back of that -- a gate passing because a signal was deleted, which is rejected on mechanism.
#
# THE FORM. One free scalar, and the two behaviours already simulated are its two endpoints:
#
#     g(t) = open(t) * [ k + (1 - k) * occ(t) ],        open(t) = 1 - staff_shoulder_flag(t)
#
# k is the share of retail lighting switched by STORE HOURS (ambient, merchandising, egress --
# lit whether or not a shopper is in the aisle); (1-k) is the share tracking activity (task,
# point-of-sale, back-of-house). k=1 IS the withdrawn open/closed form; k=0 is pure occupancy
# gated by opening hours. So k is an interpolation between two simulated arms, not a new degree
# of freedom invented to hit a target.
#
# CALIBRATION of k, on the SAME criterion used for office_n and NOT on any EUI gate: run the
# 2022 observed retail occupancy through the form and ask which k reproduces
# `RetailStandalone BLDG_LIGHT_SCH_2013`'s own weekday mean of 0.4521 (floor 0.05, peak 0.90).
#
#     k = 0.00   0.3139   -30.6 %        k = 0.60   0.4530    +0.2 %  <--
#     k = 0.25   0.3719   -17.7 %        k = 0.75   0.4878    +7.9 %
#     k = 0.50   0.4298    -4.9 %        k = 1.00   0.5458   +20.7 %  (the withdrawn form)
#
# Shape was checked too, because a mean match is one scalar: RMSE vs the prototype's hourly
# weekday profile is 0.1572 at k=0.60 against 0.2336 at k=0 and 0.2275 at k=1 -- a 31 % reduction
# on the withdrawn form, and k=0.60 beats BOTH endpoints. The RMSE optimum is k=0.50 (0.1543);
# k=0.60 is kept because matching the prototype mean was the PRE-REGISTERED criterion and the
# difference is 1.9 % on RMSE. Correlation r is NOT usable as evidence here and is recorded only
# to say so: it peaks at k~0.40 and spans just 0.870-0.918 across the whole family.
#
# WHAT IT COSTS AND WHAT IT BUYS: the retail sens_retail_cons -> sens_retail_opt lever comes back
# from +0.00 % (frozen) to +2.69 % on the schedule weekday mean. That is deliberately smaller
# than the k=0 value of +12.83 % -- store hours genuinely do damp the retail signal, which is the
# defensible half of the original T9-10 argument and is kept. What is not kept is the claim that
# the damping is total.
#
# OPEN ITEM, unchanged and now more load-bearing: `open(t)` still comes from the provisional NECB
# retail occupancy proxy at 3rdJ_07_aug_to_bem_4split.py:20-45. k mixes that proxy with a real
# occupancy series instead of substituting it, so the proxy's weight drops from 100 % to 60 % --
# reduced, not resolved.
LIGHTING_MODEL_CALIBRATED_V2 = dict(LIGHTING_MODEL_ZONE, office_n=3,
                                    retail_mode="open_hours_mix", retail_k_open=0.60)


def apply_lighting_diversity(occ_vals, floor: float, peak: float,
                             n_zone: int = 1, open_flags=None, k_open: float = 1.0):
    """f_light(t) = floor + (peak - floor) * g(t), elementwise, clipped to [0, 1].

    g(t) = open_flags[t] * (k_open + (1 - k_open) * occ(t))
                                       when open_flags is supplied (retail). k_open is the share
                                       of lighting switched by STORE HOURS; (1 - k_open) tracks
                                       activity. k_open=1.0 (the default) collapses to the
                                       withdrawn T9-10 form g == open_flags, so existing callers
                                       are bit-for-bit unaffected. See T9-12 above.
         = 1 - (1 - occ(t)) ** n_zone  otherwise (zone coincidence: probability that a switched
                                       zone of n_zone workstations holds >=1 occupant).
                                       n_zone=1 -> g == occ, the linear model.

    occ_vals may be a flat list (office 24h / retail 48-slot) or a {month: [...]} dict (hotel);
    open_flags, when given, must align elementwise with occ_vals.
    """
    if isinstance(occ_vals, dict):
        return {k: apply_lighting_diversity(v, floor, peak, n_zone=n_zone)
                for k, v in occ_vals.items()}
    n = max(1, int(n_zone))
    kk = min(1.0, max(0.0, float(k_open)))
    out = []
    for i, v in enumerate(occ_vals):
        occ = min(1.0, max(0.0, float(v)))
        if open_flags is not None:
            g = float(open_flags[i]) * (kk + (1.0 - kk) * occ)
        else:
            g = occ if n == 1 else 1.0 - (1.0 - occ) ** n
        out.append(min(1.0, max(0.0, floor + (peak - floor) * g)))
    return out


# ---------------------------------------------------------------------------
# Occupancy-driven service hot water  (T9-11, 2026-07-31) -- opt-in, off by default
# ---------------------------------------------------------------------------
# WHY. The arm-A end-use decomposition (improvements/3rdJ_L3_improvements_step9.md) measured
# `dhw` at 12.19 kWh/m2 in EVERY office scenario column to 2 dp -- identical for the NECB
# default, for 2005, for 2022 and for all three 2030 bundles. Checked across the 14 scenarios of
# Tall__MTL the spread is 0.008-0.014 %, which is the allocation denominator jittering, not a
# response. The injector modulated PEOPLE / LIGHTS / ELECTRICEQUIPMENT and never touched
# WATERUSE:EQUIPMENT, so the most canonically occupancy-driven load in the building was the one
# load that ignored occupancy. Its weight is not marginal: 47.6 % of the residential channel,
# 36.7 % of hotel, 15.2 % of office, 9.1 % of retail -- 26.8 % of whole-tower site energy. Every
# lever reported in Steps 8-9 was computed on a base a quarter of which could not move.
#
# THE MODEL. Service water draw is a per-capita event rate: unlike lighting (switched per zone,
# hence T9-10's coincidence exponent), a restroom or a shower serves one person at a time. So DHW
# takes the LINEAR form, and the same floor/peak discipline as T9-10:
#
#     f_dhw(t) = floor + (peak - floor) * occ(t)
#
# floor and peak are read from the prototype Flow Rate Fraction Schedule the object already
# carries, design days excluded, via the same `_schedule_extremum` resolver. Keeping the
# prototype's own peak matters here more than anywhere else: `Peak_Flow_Rate` was SIZED against
# that schedule's maximum, so a model that let the fraction reach 1.0 would silently inflate the
# plant's design draw. Floors are real too (circulation/trickle): OfficeLarge 0.00-0.57,
# RetailStandalone 0.00-0.62, HotelLarge BLDG 0.15-0.60, HotelLarge GuestRoom 0.15-0.80,
# ApartmentHighRise APT_DHW 0.01-1.00.
#
# LAUNDRY IS EXCLUDED, DELIBERATELY AND VISIBLY. Hotel laundry is 53.8 % of the tower's design
# DHW flow (`HotelLarge LAUNDRY_SWH_SCH` 49.6 % + `LaundryRoom_SWH_Sch_Post2004` 4.2 %) and it is
# NOT a per-capita instantaneous load: laundry VOLUME scales with guest-nights, but it is washed
# in batches whose intra-day shape is an operating decision, not a presence curve. Driving it by
# instantaneous guest presence would move the wash load to 03:00, when guests are in their rooms.
# The correct model scales the prototype's batch SHAPE by a daily/monthly occupancy factor
# against a FIXED cross-scenario reference -- a specification decision (what reference?), not a
# bug fix, so it is left open rather than guessed. Consequence, stated so nobody reads a
# partial fix as a complete one: after T9-11 roughly 54 % of design DHW flow -- concentrated in
# the hotel channel -- still does not respond to occupancy.
#
# EXPECTED CONSEQUENCE, recorded before any simulation so it can be wrong: DHW falls in every
# channel (our occupancy series run below the prototype schedules' own means), office and
# residential most, and for the FIRST TIME dhw differs between scenarios -- the sens_* levers
# should now move it. If dhw still comes back identical across scenarios, the model did not land.

DHW_MODEL_PER_CAPITA = {
    "channels": ("office", "retail", "hotel", "residential"),
    "exclude_schedule_tokens": ("LAUNDRY",),   # batch process -- see the block comment above
}


def _wateruse_channel_map(idf) -> dict:
    """{WATERUSE:EQUIPMENT name (upper) -> channel or None}.

    WaterUse:Equipment carries a blank `Zone Name`, so these objects cannot ride the
    zone->channel map. Two resolution rules, in order, both read off the IDF and never guessed:

      1. the equipment Name is "<SpaceName> Service Water Use <x>gpm <T>F" -- split at
         " SERVICE WATER USE" and classify the resulting Space through its Tag-2;
      2. plant-level units with no Space prefix ("Booster", "Laundry") are resolved by the
         prototype token in their Flow Rate Fraction Schedule Name.

    This is the SAME rule 3rdJ_08P_probe_driver.py:715-732 uses to attribute DHW energy per
    channel when reporting. It is duplicated rather than imported, deliberately: the reporting
    side must stay able to attribute a tree produced by any injector version, and the injector
    must not import a Step-8 driver. If the two ever disagree, injection and attribution would
    silently describe different buildings -- so the pairing is asserted by the T9-11 tests.
    """
    fine_to_agg = {"office": "office", "office_support": "office",
                   "retail": "retail", "hotel": "hotel", "hotel_support": "hotel",
                   "residential": "residential", "residential_common": "residential_common",
                   "service_mep": "service_MEP"}
    space_to_channel = {}
    for sp in idf.idfobjects.get("SPACE", []):
        agg = fine_to_agg.get(classify_tag2(str(getattr(sp, "Tag_2", "") or "").strip()))
        if agg:
            space_to_channel[str(sp.Name).strip().upper()] = agg
    sched_token = (("HOTELLARGE", "hotel"), ("OFFICELARGE", "office"),
                   ("RETAILSTANDALONE", "retail"), ("MIDRISEAPARTMENT", "residential"),
                   ("HIGHRISEAPARTMENT", "residential"))
    out = {}
    for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", []):
        key = str(we.Name).strip().upper()
        ch = space_to_channel.get(key.split(" SERVICE WATER USE")[0].strip())
        if ch is None:
            sched = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "").upper()
            ch = next((c for tok, c in sched_token if tok in sched), None)
        out[key] = ch
    return out


def _wateruse_space_of(we) -> str:
    """The Space name embedded in a WaterUse:Equipment name, upper-cased ('' if plant-level)."""
    key = str(we.Name).strip().upper()
    head = key.split(" SERVICE WATER USE")[0].strip()
    return head if head != key else ""


def _dhw_excluded(we, dhw_model) -> bool:
    """True if this object is on the documented exclusion list (batch processes)."""
    sched = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "").upper()
    return any(tok.upper() in sched for tok in dhw_model.get("exclude_schedule_tokens", ()))


# ---------------------------------------------------------------------------
# T9-13 (2026-08-01) -- DHW volume scaling. RE-SPECIFICATION of T9-11, which is REFUTED.
# ---------------------------------------------------------------------------
# WHY T9-11 IS WITHDRAWN. Measured on campaign 1170771 arm D vs arm C, from `dhw_hourly.csv`
# (8760 h, cell B_central__Tall__MTL), re-derived in improvements/3rdJ_L3_improvements_step9.md:
#
#     residential DHW  +36.5 % annual, hourly max UNCHANGED (-2.4 %)
#     night 00:00-05:00 share of the daily total   8.34 %  ->  32.86 %   (3.94x)
#     peak draw hour                                06:00  ->  04:00
#     diurnal peak-to-mean                          1.907  ->  1.359
#
# T9-11's own pre-recorded expectation ("DHW falls in every channel") was falsified by its own
# simulation. The form `f_dhw(t) = floor + (peak - floor) * occ(t)` makes the instantaneous draw
# RATE proportional to instantaneous PRESENCE. Showering, handwashing and cooking are scheduled
# behaviours: being home asleep at 04:00 is presence with no draw. So the residential draw profile
# flattened onto the occupancy curve and the annual mean rose with it, while office -- occupancy
# zero at night and weekends -- fell 41.7 % with its peak halved. This is exactly the failure the
# T9-11 block comment described when it excluded laundry ("would move the wash load to 03:00, when
# guests are in their rooms"); the argument was correct and its scope was too narrow. It applies to
# ALL of DHW, not only to batch processes.
#
# THE RE-SPECIFICATION. Occupancy sets HOW MUCH is drawn in a day, not WHEN within the day:
#
#     f_new(t) = s_proto(t) * r(d) / R          r(d) = mean(occ_d) / mean(occ_ref_d)
#     Peak_Flow_Rate' = Peak_Flow_Rate * R      R    = max_d r(d)
#
# s_proto is the prototype flow-fraction schedule's own time-weighted hourly profile, carried
# through UNTOUCHED -- so the intra-day shape, the peak hour and the night share are preserved by
# construction, and that is a testable identity, not a hope (see `audit_dhw_shape_preservation`).
# Daily volume scales exactly by r(d), because
#     volume(d) ~ Peak_Flow_Rate' * mean_t f_new = P*R * mean(s)*r(d)/R = P * mean(s) * r(d).
# Dividing by R and multiplying Peak_Flow_Rate by R keeps max(f_new) = max(s_proto), so the
# Fraction bound is never violated and the schedule never silently clips -- clipping would have
# truncated volume and broken the very promise of the model.
#
# NO-OP PROPERTY (the reason this form is safe): if our occupancy equals the reference occupancy
# then r == 1, R == 1, f_new == s_proto and Peak_Flow_Rate is unchanged, so the model reduces to
# the untouched prototype BIT-FOR-BIT. A model that cannot reproduce its own null case cannot be
# trusted to report a lever; this one can, and `audit_dhw_shape_preservation` asserts it.
#
# THE REFERENCE, and why it is the prototype's own PEOPLE schedule. The injector runs ONE scenario
# per IDF and has no cross-scenario view, so "relative to Default_NECB" is not computable in-run.
# Normalising to the injected series' own annual mean is degenerate -- it would force annual DHW to
# be scenario-invariant, which is the original T9-11 complaint restored. The prototype occupancy
# schedule is the one anchor that is fixed across scenarios, present in every IDF, and physically
# the right one: NECB sized this DHW volume against that many person-hours, our scenario supplies a
# different number of person-hours, and the ratio is per-capita daily volume done correctly.
# It must be captured BEFORE the PEOPLE rewiring, because afterwards the object carries an MXU_*
# schedule and `_schedule_daytype_profiles` correctly refuses it.
#
# TWO SPECIFICATION CHOICES ARE SURFACED, NOT BURIED:
#   `peak_policy="rescale"` (default) lets Peak_Flow_Rate rise with R when our occupancy exceeds
#       NECB's. Physically consistent: more person-hours really is a larger design draw. It DOES
#       change plant design flow, which T9-11 was rightly careful about -- so it is recorded per
#       object in the provenance and asserted by the audit.
#   `peak_policy="cap"` forbids R > 1 (design draw may fall, never rise), preserving the prototype
#       sizing at the cost of under-serving scenarios busier than NECB.
#   `r_max` bounds a runaway ratio; it is a guard, not a tuning knob, and any object that hits it
#       is reported as CLIPPED so a silent saturation cannot be read as a clean result.
# Neither is chosen by evidence -- both are recorded for the user's decision.
#
# LAUNDRY IS NO LONGER A SPECIAL CASE. T9-11 excluded it because a presence-driven rate would move
# the wash to 03:00. T9-13 never touches intra-day shape, so the batch shape survives untouched and
# only its daily volume scales with guest-nights -- which is precisely the "correct model" the
# T9-11 comment described but could not implement. `exclude_schedule_tokens` therefore defaults to
# EMPTY here. It is kept as a parameter so the exclusion can be reinstated for comparison.

# MEASURED BLOCKER on `reference="prototype_people"` (job 1171061, TallBuilding ... Z6_v242.idf,
# the PRE-injection tower). The resolver now reads all 7 prototype DHW schedules correctly
# (Schedule:Year -> Week:Daily -> Day:Interval), but the tower carries exactly ONE PEOPLE schedule
# for every channel:
#
#     NECB-A-Occupancy   mean_wd=0.3583  max_wd=0.9000  peak_h=9  night_share=0.0000
#                        mean_we=0.0000            <-- ZERO at the weekend
#
# Two independent reasons that reference cannot be used as specified:
#   1. `r_we = mean(occ_we) / 0` is undefined, so all 47 WaterUse:Equipment objects would come back
#      `dhw_unresolved` -- T9-13 would be a silent whole-building no-op.
#   2. It is not commensurate. Scaling RESIDENTIAL draw against an office-shaped NECB curve that is
#      zero on Saturdays compares "fraction of residents at home" with "NECB office occupancy".
#      Even with the zero patched, the ratio would not mean anything.
#
# So the reference must be the SAME SERIES as the target, measured in a designated baseline
# scenario: `reference="baseline_series"` with a per-channel weekly-mean occupancy supplied in
# `reference_occ_mean`. That is the "FIXED cross-scenario reference" the T9-11 comment named as a
# specification decision, and it is well-posed: same units, same construction, computed once
# offline from the baseline scenario's own Step-7 occupancy CSVs and then held constant, so the
# per-scenario injector never needs a cross-scenario view.
#
# CORRECTION (2026-08-02). An earlier draft of this comment said "Default_NECB then gets r == 1
# exactly (the no-op case)". That was WRONG, and wrong in a way that made a vacuous property look
# like an argument. `Default_NECB` is declared `{"tag": "Default_NECB", "channels": {}}` in
# `3rdJ_08D_campaign_cells.py:234` -- no injection AT ALL. The injector never runs in that cell, so
# it is a no-op under EVERY choice of reference, which means the property discriminates between
# zero candidates. Worse, Default_NECB cannot BE the baseline: `reference="baseline_series"` needs
# a per-channel occupancy series of OUR construction, and Default_NECB has none by definition.
# The reference must therefore be one of the INJECTED scenarios. `Y2022` ("2022 observed cycle",
# `3rdJ_08D_campaign_cells.py:236-238`, all four channels present) is the defensible anchor: the
# prototype's DHW volume is a present-day engineering calibration, so the occupancy it is divided
# by should be the present-day occupancy from the same series. Every 2030 bundle then reads as
# "person-hours relative to today" -- the lever T9-11 was trying to create -- and the historical
# years read as change from today with the correct sign. Y2005/Y2010/Y2015 carry no hotel channel
# (`DELIBERATE_CHANNEL_EXCEPTIONS`), which is consistent: hotel is simply not injected there.
# This is still the user's call and is recorded as such; what changed is that the choice is now
# between injected scenarios, and the "uninjected cell stays exact" argument is struck.
#
# `reference_occ_mean` is deliberately EMPTY here. Any channel missing from it is reported
# `dhw_unresolved` with the reason, never silently defaulted to 1.0 -- a defaulted reference would
# fabricate a no-op and report it as a result.

# BASELINE = Y2022 ("2022 observed cycle", 3rdJ_08D_campaign_cells.py:236-238). User decision,
# 2026-08-02, recorded in 3rdJ_L3_improvements_step9.md. Values computed offline by
# t913_reference_table.py, which mirrors _channel_occ_24 and the three product loaders exactly
# (48->24 pair-average; retail weekend = mean(sat24, sun24); hotel = mean of the 12 monthly 24-h
# vectors; residential = pool mean over the 7175 DTYPE-filtered households, per day type).
#
# Retail and hotel are PR-dependent and these are the QC (Montreal) values. The AB (Calgary) means
# differ -- retail AB 0.3554/0.2618 vs QC 0.3104/0.2615, hotel AB 0.3624/0.3735 vs QC 0.3573/0.3682
# -- so the CLG cells do NOT get r == 1.000 in the baseline year; they get the AB/QC offset instead
# (retail AB r_wd = 1.145, hotel AB r_wd = 1.014 in Y2022). That is a KNOWN and DELIBERATE limitation
# of a single national reference per channel: `reference_occ_mean` is one map for the whole campaign,
# not one per city. It is left this way on purpose so the two cities share one denominator and the
# city axis stays comparable; the alternative (a per-PR reference) makes each city its own no-op but
# then r means something different in each. Stated here so nobody reads CLG's r != 1 as a bug.
DHW_MODEL_VOLUME_SCALED = {
    "channels": ("office", "retail", "hotel", "residential"),
    "exclude_schedule_tokens": (),      # laundry no longer needs excluding -- see above
    "reference": "baseline_series",
    # {channel: {"wd": mean weekday occupancy, "we": mean weekend occupancy}} of the BASELINE.
    # Per day type, NOT a scalar -- see FINDING 4 in the comment at the reference-builder site.
    "reference_occ_mean": {
        "office":      {"wd": 0.253013, "we": 0.065079},   # office_presence_multiplier_2022.csv
        "retail":      {"wd": 0.310422, "we": 0.261454},   # retail_presence_multiplier_2022.csv, PR=QC
        "hotel":       {"wd": 0.357275, "we": 0.368193},   # hotel_schedule_multiplier_2022.csv, PR=QC
        "residential": {"wd": 0.635497, "we": 0.732074},   # BEM_Schedules_4split_2022.csv, pool mean
    },
    "peak_policy": "rescale",           # "rescale" | "cap"
    "r_max": 3.0,
}

# Kept for the record: the form that the tower's own PEOPLE schedule cannot support. Selecting it
# is legal and will resolve on an IDF whose PEOPLE objects carry per-channel prototype occupancy;
# on this tower it will report every object unresolved, loudly, with the reason above.
DHW_MODEL_VOLUME_SCALED_PROTO_PEOPLE = dict(DHW_MODEL_VOLUME_SCALED,
                                            reference="prototype_people")


def apply_dhw_volume_scaling(proto_wd, proto_we, occ_wd, occ_we, ref_wd, ref_we,
                             peak_policy: str = "rescale", r_max: float = 3.0,
                             proto_by_daytype: dict = None):
    """T9-13. Scale DAILY VOLUME by occupancy; carry the intra-day SHAPE through untouched.

    Returns (new_wd, new_we, info). `info` carries every number the audit and the provenance need:
    r_wd, r_we, R, peak_multiplier, clipped, and the shape-preservation evidence.

    All six inputs are 24-slot (or equal-length) sequences. proto_* is the flow-fraction schedule
    being replaced; occ_* is our injected occupancy; ref_* is the prototype occupancy that the
    prototype flow schedule was sized against.

    FINDING 9 (2026-08-02): `proto_by_daytype` -- {day type: [24]} for all 8 day types -- carries
    the prototype's OWN Saturday, Sunday and Holiday curves instead of letting one weekend profile
    stand for all of them. Each day type is scaled by the ratio of its CLASS (weekdays r_wd,
    Saturday/Sunday/Holidays r_we), so the volume target is unchanged and only the shape stops
    being lost. `info["new_by_daytype"]` is the result and `info["daytype_ratio"]` is the achieved
    per-day-type volume ratio, which check D8 asserts against r(class)/R. Omitting the argument
    reproduces the previous two-day-type behaviour exactly.
    """
    def _mean(v):
        v = [float(x) for x in v]
        return sum(v) / len(v) if v else 0.0

    ref_m_wd, ref_m_we = _mean(ref_wd), _mean(ref_we)
    r_wd = (_mean(occ_wd) / ref_m_wd) if ref_m_wd > 1e-12 else None
    r_we = (_mean(occ_we) / ref_m_we) if ref_m_we > 1e-12 else None
    if r_wd is None or r_we is None:
        return None, None, {"error": "reference occupancy has zero mean -- ratio undefined",
                            "ref_mean_wd": ref_m_wd, "ref_mean_we": ref_m_we}
    clipped = bool(r_wd > r_max or r_we > r_max)
    r_wd, r_we = min(r_max, max(0.0, r_wd)), min(r_max, max(0.0, r_we))

    R = max(r_wd, r_we)
    if peak_policy == "cap":
        R = min(1.0, R) if R > 0 else 1.0
    if R <= 1e-12:
        R = 1.0
    # divide the shape by R so max(f_new) == max(s_proto); multiply design flow by R to restore
    # the volume. Under "cap", R is held at <=1 so the schedule may clip -- reported, not hidden.
    new_wd = [min(1.0, max(0.0, float(s) * r_wd / R)) for s in proto_wd]
    new_we = [min(1.0, max(0.0, float(s) * r_we / R)) for s in proto_we]

    # FINDING 9: scale each day type on its OWN prototype curve, by its class ratio.
    new_by_daytype, daytype_ratio, proto_daytype_mean = None, None, None
    if proto_by_daytype:
        missing = [d for d in _ALL_DAYTYPES if d not in proto_by_daytype]
        if missing:
            return None, None, {"error": f"proto_by_daytype is missing day types {missing} -- "
                                         f"an incomplete map is how FINDING 9 stayed invisible"}
        new_by_daytype, daytype_ratio, proto_daytype_mean = {}, {}, {}
        for d in _ALL_DAYTYPES:
            r_d = r_wd if d in _WEEKDAY_DAYTYPES else r_we
            src = [float(x) for x in proto_by_daytype[d]]
            new_by_daytype[d] = [min(1.0, max(0.0, s * r_d / R)) for s in src]
            m_p = sum(src) / len(src) if src else 0.0
            m_n = sum(new_by_daytype[d]) / len(new_by_daytype[d]) if new_by_daytype[d] else 0.0
            proto_daytype_mean[d] = round(m_p, 8)
            daytype_ratio[d] = round((m_n / m_p) if m_p > 1e-12 else float("nan"), 8)

    def _nightshare(v):
        t = sum(float(x) for x in v)
        return (sum(float(x) for x in v[0:6]) / t) if t > 1e-12 else float("nan")

    def _argmax(v):
        return max(range(len(v)), key=lambda i: float(v[i]))

    info = {
        "r_wd": round(r_wd, 6), "r_we": round(r_we, 6), "R": round(R, 6),
        "peak_multiplier": round(R, 6), "peak_policy": peak_policy,
        "r_clipped_at_r_max": clipped,
        "proto_mean_wd": round(_mean(proto_wd), 6), "new_mean_wd": round(_mean(new_wd), 6),
        "proto_max": round(max([float(x) for x in proto_wd] + [float(x) for x in proto_we]), 6),
        "new_max": round(max(new_wd + new_we), 6),
        "proto_nightshare_wd": round(_nightshare(proto_wd), 6),
        "new_nightshare_wd": round(_nightshare(new_wd), 6),
        "proto_peakhour_wd": _argmax(proto_wd), "new_peakhour_wd": _argmax(new_wd),
        "is_noop": bool(abs(r_wd - 1.0) < 1e-9 and abs(r_we - 1.0) < 1e-9),
        # FINDING 9 evidence. `n_distinct_daytypes` == 1 means the prototype really does have one
        # curve; > 1 with the old writer is exactly the case that lost volume.
        "daytype_ratio": daytype_ratio,
        "proto_daytype_mean": proto_daytype_mean,
        "n_distinct_daytypes": (
            len({tuple(round(float(x), 6) for x in v) for v in proto_by_daytype.values()})
            if proto_by_daytype else None),
    }
    if new_by_daytype is not None:
        info["new_max"] = round(max(max(v) for v in new_by_daytype.values()), 6)
        info["proto_max"] = round(max(max(float(x) for x in v)
                                      for v in proto_by_daytype.values()), 6)
    return new_wd, new_we, (info if new_by_daytype is None
                            else dict(info, new_by_daytype=new_by_daytype))


def audit_dhw_shape_preservation(applied: list, tol_share: float = 1e-6,
                                 verbose: bool = True, expect_channels=()) -> dict:
    """T9-13 gate. Shape preservation is an IDENTITY here, so it must be asserted, not assumed.

    This is the diagnostic that would have caught T9-11: it fails loudly on exactly the signature
    arm D produced -- night share moved and the peak hour moved. Checks, per applied object:

      D1 night-share (00:00-05:00 of the daily total) IDENTICAL to the prototype's
      D2 peak hour IDENTICAL to the prototype's
      D3 max(f_new) <= max(s_proto) + tol   (the Fraction bound was never restored by clipping)
      D4 volume ratio actually achieved == r(d) as intended
      D5 no object silently saturated at r_max
      D6 every channel in `expect_channels` actually contributed at least one audited object
      D8 EVERY day type's volume ratio == r(class)/R  (FINDING 9)

    D8 is D4 applied to the day types D4 could not see. D4 compares one weekday mean against
    r_wd, so it is blind to what happens on Saturday -- and Saturday was exactly where the volume
    was going missing: the reader kept `sun or sat` and the writer emitted that single curve to
    "For: Weekends", so a prototype with a busy Saturday and a quiet Sunday silently lost the
    difference. D8 requires mean(new_d)/mean(proto_d) == r(class of d)/R for all 8 day types, which
    the collapsing writer cannot satisfy whenever two day types differ. An object whose source
    resolved no per-day-type map reports D8 as unchecked (counted in `d8_unchecked`), never as a
    pass -- the T9-13 path records that same object in `t9_13_daytype_fallback`.

    D6 exists because D1-D5 can only speak about records that reached this list, and this list is
    filtered on `model == "T9-13_volume_scaled"` by the caller. A channel that quietly ran a
    DIFFERENT model is therefore invisible to D1-D5 and the gate would pass without it -- exactly
    what FINDING 3 (residential on the refuted T9-11 rate model) would have produced. Pass the
    requested channel tuple and the gate can no longer pass by omission.

    Returns {"pass": bool, "n": int, "violations": [...], "counts": {...}}. A `pass` on an EMPTY
    list is reported as a FAIL: a gate that never ran is not a gate that passed.
    """
    v, counts = [], {"D1": 0, "D2": 0, "D3": 0, "D4": 0, "D5": 0, "D6": 0, "D8": 0}
    d8_unchecked = []
    for rec in applied:
        i = rec.get("t9_13") or {}
        if not i or "error" in i:
            v.append({"obj": rec.get("name"), "check": "D0",
                      "detail": i.get("error", "no T9-13 info recorded")})
            continue
        ns_p, ns_n = i.get("proto_nightshare_wd"), i.get("new_nightshare_wd")
        if ns_p == ns_p and abs(float(ns_n) - float(ns_p)) > tol_share:   # NaN-safe
            counts["D1"] += 1
            v.append({"obj": rec.get("name"), "check": "D1",
                      "detail": f"night share {ns_p} -> {ns_n}"})
        if i.get("proto_peakhour_wd") != i.get("new_peakhour_wd"):
            counts["D2"] += 1
            v.append({"obj": rec.get("name"), "check": "D2",
                      "detail": f"peak hour {i.get('proto_peakhour_wd')} -> "
                                f"{i.get('new_peakhour_wd')}"})
        if float(i.get("new_max", 0)) > float(i.get("proto_max", 0)) + 1e-9:
            counts["D3"] += 1
            v.append({"obj": rec.get("name"), "check": "D3",
                      "detail": f"max {i.get('proto_max')} -> {i.get('new_max')}"})
        pm, nm, r_wd, R = (float(i.get("proto_mean_wd", 0)), float(i.get("new_mean_wd", 0)),
                           float(i.get("r_wd", 0)), float(i.get("R", 1)))
        if pm > 1e-12:
            achieved = (nm / pm) * float(i.get("peak_multiplier", 1.0))
            if abs(achieved - r_wd) > 1e-4:
                counts["D4"] += 1
                v.append({"obj": rec.get("name"), "check": "D4",
                          "detail": f"volume ratio achieved {achieved:.6f} != intended {r_wd:.6f}"
                                    f" (clipping?)"})
        if i.get("r_clipped_at_r_max"):
            counts["D5"] += 1
            v.append({"obj": rec.get("name"), "check": "D5", "detail": "r saturated at r_max"})
        # D8 (FINDING 9) -- every day type, not just the weekday D4 looks at.
        dr = i.get("daytype_ratio")
        if not dr:
            d8_unchecked.append(rec.get("name"))
        else:
            r_we_i = float(i.get("r_we", 0))
            for d, achieved in sorted(dr.items()):
                if achieved != achieved:          # NaN: prototype day is all-zero, ratio undefined
                    continue
                want = (float(i.get("r_wd", 0)) if d in _WEEKDAY_DAYTYPES else r_we_i) / R
                if abs(float(achieved) - want) > 1e-4:
                    counts["D8"] += 1
                    v.append({"obj": rec.get("name"), "check": "D8",
                              "detail": f"{d}: volume ratio achieved {float(achieved):.6f} != "
                                        f"intended {want:.6f} -- this day type is not carrying "
                                        f"its own prototype shape (FINDING 9)"})
    seen_channels = {rec.get("channel") for rec in applied}
    for ch in (expect_channels or ()):
        if ch not in seen_channels:
            counts["D6"] += 1
            v.append({"obj": f"<channel:{ch}>", "check": "D6",
                      "detail": f"channel '{ch}' was requested in dhw_model['channels'] but "
                                f"contributed 0 audited objects -- it did not run T9-13"})
    ok = (len(v) == 0) and (len(applied) > 0)
    if verbose:
        if not applied:
            print("  [T9-13 audit FAIL] 0 objects audited -- a gate that never ran is not a PASS")
        elif ok:
            print(f"  [T9-13 audit PASS] {len(applied)} objects: shape, peak hour, night share "
                  f"and Fraction bound all preserved; volume ratios achieved as intended, on "
                  f"every day type")
        else:
            print(f"  [T9-13 audit FAIL] {len(v)} violations over {len(applied)} objects: {counts}")
            for x in v[:8]:
                print(f"      {x['check']} {x['obj']}: {x['detail']}")
        if d8_unchecked:
            print(f"  [T9-13 audit] D8 UNCHECKED on {len(d8_unchecked)} object(s) -- no "
                  f"per-day-type map resolved; reported, not counted as a pass: "
                  f"{d8_unchecked[:5]}")
    return {"pass": ok, "n": len(applied), "violations": v, "counts": counts,
            "d8_unchecked": d8_unchecked}


# D7 name grammar. Both generators write `..._DHWv2_[HH<id>_]<TOKEN>_r####w####[_<tag>]`, and the
# token alphabet is [A-Z0-9_] while the r/w markers are lower-case, so `_r\d{4}w\d{4}` cannot occur
# inside a token. `.+` is greedy on purpose: it anchors on the LAST r/w marker, so a scenario tag
# that happens to look like one cannot steal the split point.
_DHWV2_NAME_RE = re.compile(
    r"^MXU_(?P<ch>[A-Za-z]+)_DHWv2_(?:HH(?P<hh>\d+)_)?(?P<tok>.+)_r(?P<r>\d{4})w(?P<w>\d{4})"
    r"(?:_(?P<tag>.*))?$")


def audit_dhw_assignment(saved_idf_path: str, applied: list, proto_before: dict,
                         verbose: bool = True, idd_path: str = None) -> dict:
    """D7 (FINDING 8, 2026-08-02). Per WaterUse:Equipment object in the SAVED IDF:

    > its `Flow_Rate_Fraction_Schedule_Name` is either UNCHANGED from the source IDF, or is the
    > T9-13 derivative OF ITS OWN ORIGINAL SCHEDULE -- never another object's.

    Read from the re-opened output IDF, deliberately. `rec["derived_schedule"]` in
    `result["dhw_applied"]` records the CACHED name, so a D7 built over `dhw_applied` would
    inherit exactly the blindness it exists to close: under the collision every record faithfully
    reported the name it was given, and the audit would have passed on arm E. The only artefact
    that cannot lie about the assignment is the file EnergyPlus will read.

    Parameters
    ----------
    saved_idf_path : the just-written output IDF.
    applied        : `result["dhw_applied"]` (used for the prototype each object CLAIMS, which is
                     cross-checked against `proto_before` -- a record that misreports its own
                     source is itself a D7 violation).
    proto_before   : {UPPER(object name): original Flow_Rate_Fraction_Schedule_Name}, snapshotted
                     from the source IDF before any DHW write.
    """
    from eppy.modeleditor import IDF
    if idd_path:
        IDF.setiddname(idd_path)
    idf2 = IDF(saved_idf_path)

    by_name = {str(r.get("name", "")).strip().upper(): r for r in applied}
    v, n_checked, n_derived, n_unchanged = [], 0, 0, 0
    names_seen = {}
    d9_unchecked = []
    for we in idf2.idfobjects.get("WATERUSE:EQUIPMENT", []):
        key = str(we.Name).strip().upper()
        assigned = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "").strip()
        before = str(proto_before.get(key, "")).strip()
        n_checked += 1
        rec = by_name.get(key)
        if rec is None:
            # Not touched by the injector -> must be byte-identical to the source IDF.
            if assigned.upper() != before.upper():
                v.append({"obj": we.Name, "check": "D7",
                          "detail": f"untouched object's schedule changed: '{before}' -> "
                                    f"'{assigned}'"})
            else:
                n_unchanged += 1
            continue
        claimed = str(rec.get("prototype_schedule", "")).strip()
        if claimed.upper() != before.upper():
            v.append({"obj": we.Name, "check": "D7",
                      "detail": f"dhw_applied claims prototype '{claimed}' but the source IDF "
                                f"had '{before}'"})
            continue
        m = _DHWV2_NAME_RE.match(assigned)
        if m is None:
            if assigned.upper() == before.upper():
                n_unchanged += 1
                continue
            v.append({"obj": we.Name, "check": "D7",
                      "detail": f"assigned '{assigned}' is neither unchanged from '{before}' nor "
                                f"a parseable MXU_*_DHWv2_* derivative"})
            continue
        expect_tok = _sched_token(before)
        got_tok = m.group("tok")
        if got_tok != expect_tok:
            v.append({"obj": we.Name, "check": "D7",
                      "detail": f"assigned '{assigned}' carries source token '{got_tok}' but this "
                                f"object's own schedule is '{before}' (token '{expect_tok}') -- "
                                f"it is on ANOTHER object's derived schedule"})
            continue
        n_derived += 1
        names_seen.setdefault(assigned, set()).add(before.upper())

        # ---- D9 (FINDING 9): per-day-type fidelity, read from the FILE ----
        # D8 compares the injector's own numbers against the injector's own reading of the
        # prototype, so a defect in the READER is invisible to it -- demonstrated: re-creating the
        # collapse in `_schedule_daytype_profiles` left D8 at 0 violations, because the corrupted
        # Saturday was both the reference and the target. That is the same shape as every other
        # vacuous gate on this project, and it is why D9 exists.
        #
        # D9 takes the two schedules out of the SAVED IDF -- the assigned MXU_* derivative and the
        # object's own prototype, which the injector never deletes -- and requires, for EVERY day
        # type, mean(assigned_d) / mean(prototype_d) == r(class of d) / R. Neither side is a number
        # the injector reported about itself.
        info = rec.get("t9_13") or {}
        if info and "error" not in info:
            src_prof, _sp = _schedule_daytype_profiles(idf2, before)
            got = _find_schedule(idf2, assigned)
            new_by = _compact_daytype_map(got) if got is not None else None
            if not (src_prof and src_prof.get("by_daytype")) or not new_by:
                d9_unchecked.append(we.Name)
            else:
                R_i = float(info.get("R", 1.0)) or 1.0
                for d in _ALL_DAYTYPES:
                    p, q = src_prof["by_daytype"].get(d), new_by.get(d)
                    if p is None or q is None:
                        d9_unchecked.append(f"{we.Name}/{d}")
                        continue
                    mp = sum(float(x) for x in p) / len(p)
                    mq = sum(float(x) for x in q) / len(q)
                    if mp <= 1e-12:
                        continue                       # all-zero prototype day: ratio undefined
                    want = (float(info.get("r_wd", 0)) if d in _WEEKDAY_DAYTYPES
                            else float(info.get("r_we", 0))) / R_i
                    if abs((mq / mp) - want) > 1e-3:
                        v.append({"obj": we.Name, "check": "D9",
                                  "detail": f"{d}: the SAVED schedule '{assigned}' has mean "
                                            f"{mq:.6f} against prototype '{before}' mean "
                                            f"{mp:.6f} = ratio {(mq / mp):.6f}, intended "
                                            f"{want:.6f} -- this day type is not carrying its own "
                                            f"prototype shape (FINDING 9)"})

    # One derived name must never serve two different source schedules. Redundant with the token
    # comparison above under the current name grammar, and kept anyway: it is the check that stays
    # true if the grammar is ever changed and the token parser silently stops matching.
    for nm, srcs in names_seen.items():
        if len(srcs) > 1:
            v.append({"obj": nm, "check": "D7",
                      "detail": f"one derived schedule serves {len(srcs)} distinct source "
                                f"schedules: {sorted(srcs)}"})

    ok = (len(v) == 0) and (n_checked > 0)
    n_d7 = sum(1 for x in v if x["check"] == "D7")
    n_d9 = sum(1 for x in v if x["check"] == "D9")
    if verbose:
        if not n_checked:
            print("  [D7 FAIL] 0 WaterUse:Equipment objects in the saved IDF -- nothing audited")
        elif ok:
            print(f"  [D7/D9 PASS] {n_checked} WaterUse:Equipment objects in the saved IDF: "
                  f"{n_derived} on a derivative of their OWN schedule, {n_unchanged} unchanged, "
                  f"0 pointing at another object's schedule; every day type of every derived "
                  f"schedule matches its own prototype at the intended ratio")
        else:
            print(f"  [D7/D9 FAIL] {len(v)} violations over {n_checked} objects "
                  f"(D7 {n_d7}, D9 {n_d9})")
            for x in v[:8]:
                print(f"      {x['check']} {x['obj']}: {x['detail']}")
        if d9_unchecked:
            print(f"  [D9 UNCHECKED] {len(d9_unchecked)} object/day-type(s) could not be "
                  f"re-expanded from the saved IDF; reported, never counted as a pass: "
                  f"{d9_unchecked[:5]}")
    return {"pass": ok, "n": n_checked, "n_derived": n_derived, "n_unchanged": n_unchanged,
            "violations": v, "derived_names": sorted(names_seen),
            "n_d7": n_d7, "n_d9": n_d9, "d9_unchecked": d9_unchecked}


# ---------------------------------------------------------------------------
# modulate_baseline / modulate_baseline_monthly
# ---------------------------------------------------------------------------
def modulate_baseline(idf, space_tag2: str, sch_name: str, wd_vals, we_vals,
                       sun_vals=None, sat_vals=None, verbose: bool = True) -> dict:
    """Create (or overwrite) a Schedule:Compact object encoding new(t) = baseline(t) x
    multiplier(t) for the given Space tag. Densities (People/Lights/Equipment per-m2) are
    NEVER touched here -- only the Schedule object + its field reference on the load object.

    2-day-type channels (office): pass wd_vals/we_vals only.
    3-day-type channels (retail): pass wd_vals/sat_vals/sun_vals (sat_vals != None triggers
    the 3-day-type builder).
    """
    if sat_vals is not None and sun_vals is not None:
        fields = _build_compact_fields_3dt(sch_name, wd_vals, sat_vals, sun_vals)
    else:
        fields = _build_compact_fields_2dt(sch_name, wd_vals, we_vals)
    s = idf.newidfobject("Schedule:Compact")
    s.obj = ["Schedule:Compact"] + fields
    if verbose:
        print(f"  [modulate_baseline] created {sch_name} for Tag-2={space_tag2}")
    return {"schedule_name": sch_name, "peak": float(max(wd_vals))}


def modulate_baseline_monthly(idf, space_tag2: str, sch_name: str, monthly_wd48: dict,
                               monthly_we48: dict, verbose: bool = True) -> dict:
    """Hotel guest-room MODULATE: 12 monthly blocks in ONE annual Schedule:Compact per
    guest-room Space (not 12 IDFs)."""
    fields = _build_compact_fields_monthly(sch_name, monthly_wd48, monthly_we48)
    s = idf.newidfobject("Schedule:Compact")
    s.obj = ["Schedule:Compact"] + fields
    if verbose:
        print(f"  [modulate_baseline_monthly] created {sch_name} for Tag-2={space_tag2} "
              f"(12 monthly blocks, 1 annual object)")
    return {"schedule_name": sch_name, "n_months": 12}


# ---------------------------------------------------------------------------
# Product loaders (thin wrappers over the Step-7 CSVs)
# ---------------------------------------------------------------------------
def load_office_series(csv_path: str, office_archetype: str, band: str) -> dict:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    sub = df[(df["office_archetype"] == office_archetype) & (df["BAND"] == band)]
    if sub.empty:
        raise ValueError(f"No office rows for archetype={office_archetype}, band={band}")
    wd = sub[sub["Day_Type"] == "Weekday"].sort_values("Hour")["AT_WORK_fraction"].tolist()
    we = sub[sub["Day_Type"] == "Weekend"].sort_values("Hour")["AT_WORK_fraction"].tolist()
    assert len(wd) == 24 and len(we) == 24, "office series must be 24h WD + 24h WE"
    return {"wd": wd, "we": we}


def load_retail_series(csv_path: str, pr: str) -> dict:
    df = pd.read_csv(csv_path)
    sub = df[df["PR"] == pr]
    if sub.empty:
        raise ValueError(f"No retail rows for PR={pr}")
    out = {}
    for dt, key in [("Weekday", "wd"), ("Saturday", "sat"), ("Sunday", "sun")]:
        s = sub[sub["Day_Type"] == dt].sort_values("slot")
        assert len(s) == 48, f"retail series [{dt}] must be 48 half-hour slots, got {len(s)}"
        out[key] = s["multiplier"].tolist()
        out[f"{key}_staff_shoulder"] = s["staff_shoulder_flag"].tolist()
    return out


def load_hotel_series(csv_path: str, pr: str) -> dict:
    df = pd.read_csv(csv_path)
    sub = df[df["PR"] == pr]
    if sub.empty:
        raise ValueError(f"No hotel rows for PR={pr}")
    monthly_wd, monthly_we = {}, {}
    for month in range(1, 13):
        wd = sub[(sub["MONTH"] == month) & (sub["Day_Type"] == "Weekday")].sort_values("slot")
        we = sub[(sub["MONTH"] == month) & (sub["Day_Type"] == "Weekend")].sort_values("slot")
        assert len(wd) == 48 and len(we) == 48, f"hotel series [month={month}] must be 48 slots each"
        monthly_wd[month] = wd["multiplier"].fillna(0.0).tolist()
        monthly_we[month] = we["multiplier"].fillna(0.0).tolist()
    return {"monthly_wd": monthly_wd, "monthly_we": monthly_we}


# ---------------------------------------------------------------------------
# Residential (OD-8R-L3, REPLACE) -- load_residential_pool / draw_residential_households /
# inject_residential. Added 2026-07-28. Consumes the Step-7 residential product
# (BEM_Schedules_4split_<year/bundle>.csv), the same file eSim_bem_utils/integration.py's
# load_schedules() reads (SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, CONDO, Occupancy_Schedule
# :379, Metabolic_Rate :380). Reimplemented here with pandas (the source file is ~1.1M rows;
# the csv.DictReader row-by-row loop in load_schedules() is easily fast enough for its own
# use case but there is no reason to import the heavier eSim_bem_utils.integration module here
# -- this module has never depended on it (idf_optimizer / schedule_generator /
# schedule_visualizer / config), and pulling in that chain would put the byte-identical
# office/retail/hotel paths at risk of a future unrelated import-time failure in that chain).
# Only the two CONSUMED columns feed Schedule:Compact (Occupancy_Schedule, Metabolic_Rate) --
# same "columns consumed, not md5" discipline as Defect 2 audit (Step8_docs
# 3rdJ_08_implementation_improvements.md).
# ---------------------------------------------------------------------------
def load_residential_pool(csv_path: str, dtype_filter=RESIDENTIAL_DTYPE_APARTMENT) -> dict:
    """Load the Step-7 residential REPLACE product and return one entry per distinct
    SIM_HH_ID passing the condo/apartment filter (RESIDENTIAL_DTYPE_APARTMENT, see the
    constant's docstring for the DTYPE/CONDO value counts this was read from).

    Returns {hh_id (str): {"hhsize": int, "dtype": str, "condo": int,
                            "occ_wd": [24 floats], "occ_we": [24 floats],
                            "met_wd": [24 floats], "met_we": [24 floats]}}
    Households with an incomplete 24h Weekday or Weekend record are dropped (mirrors the
    intent of load_schedules()'s validate_household_schedule() sanity check).
    """
    df = pd.read_csv(csv_path, usecols=["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "DTYPE",
                                         "CONDO", "Occupancy_Schedule", "Metabolic_Rate"])
    df = df[df["DTYPE"].isin(dtype_filter)]
    pool = {}
    n_incomplete = 0
    for hh_id, g in df.groupby("SIM_HH_ID", sort=True):
        wd = g[g["Day_Type"] == "Weekday"].sort_values("Hour")
        we = g[g["Day_Type"] == "Weekend"].sort_values("Hour")
        if len(wd) != 24 or len(we) != 24:
            n_incomplete += 1
            continue
        pool[str(hh_id)] = {
            "hhsize": int(wd["HHSIZE"].iloc[0]),
            "dtype": str(wd["DTYPE"].iloc[0]),
            "condo": int(wd["CONDO"].iloc[0]),
            "occ_wd": wd["Occupancy_Schedule"].to_numpy(dtype=float).tolist(),
            "occ_we": we["Occupancy_Schedule"].to_numpy(dtype=float).tolist(),
            "met_wd": wd["Metabolic_Rate"].to_numpy(dtype=float).tolist(),
            "met_we": we["Metabolic_Rate"].to_numpy(dtype=float).tolist(),
        }
    if n_incomplete:
        print(f"  [load_residential_pool] dropped {n_incomplete} household(s) with incomplete "
              f"24h Weekday/Weekend records")
    return pool


def draw_residential_households(pool: dict, n: int, seed: int = 42) -> list:
    """Deterministic draw of n DISTINCT households from pool, no replacement (OD-8R-L3: one
    distinct household per residential Space -- diversity of load SHAPE is the point, a
    building-average would flatten the coincident residential peak). Same seed -> same draw,
    every time (verified by running twice, see Step8_docs Progress Log).

    hh_ids are sorted (numeric SIM_HH_ID, ascending) before the draw so the input ordering of
    `pool` (a dict, insertion-ordered but not a guaranteed-stable sort key) never affects the
    result -- determinism must not depend on dict iteration order.
    """
    hh_ids = sorted(pool.keys(), key=lambda x: int(x))
    if len(hh_ids) < n:
        raise ValueError(
            f"residential pool has {len(hh_ids)} eligible (condo/apartment-filtered) "
            f"households, need {n} for a no-replacement draw"
        )
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(hh_ids), size=n, replace=False)
    return [hh_ids[i] for i in idx]


def inject_residential(idf, csv_path: str, seed: int = 42,
                        dtype_filter=RESIDENTIAL_DTYPE_APARTMENT, verbose: bool = True,
                        dhw_model: dict = None, dhw_reference: dict = None,
                        dhw_reference_prov: str = "") -> dict:
    """OD-8R-L3: inject one DISTINCT household's occupancy (Number_of_People = HHSIZE,
    Occupancy_Schedule, Metabolic_Rate) into EVERY residential apartment Space (Tag-2 exact
    match "HighriseApartment Apartment"), REPLACE semantics -- no baseline multiplication.

    2J Bug A fix (per-zone carrier): this v24.2 IDF's residential apartment Spaces are all
    referenced by a SINGLE building-wide PEOPLE object via a SpaceList named
    "HighriseApartment Apartment" (confirmed empirically 2026-07-28, TallBuilding tower: 27
    Spaces, 1 PEOPLE object, 1 SpaceList) -- exactly the "one carrier serves many physical
    zones" defect family documented for Leg-2 (module docstring). Fix: neutralize that
    SpaceList-level PEOPLE object to Number_of_People=0 (kept in the IDF, inert, auditable) and
    emit ONE NEW PEOPLE object per residential Space, each referencing its OWN drawn
    household's schedules directly by Space name (v24.2's unified
    Zone_or_ZoneList_or_Space_or_SpaceList_Name field accepts a Space name).

    Densities are never used here (People/Area is the ORIGINAL object's method; the new
    per-Space objects use the absolute People count method, Number_of_People = HHSIZE, per
    OD-8R-L3 -- this is a deliberate REPLACE of the count method, not a density edit).
    LIGHTS/ELECTRICEQUIPMENT for residential Spaces are NOT touched (OD-7D: no Step-9
    equipment/lighting columns exist in the Step-7 residential product; deferred).

    dhw_model (T9-11, 2026-07-31, opt-in): when supplied, each residential Space's
    WATERUSE:EQUIPMENT flow-fraction schedule is rebuilt from THAT SPACE'S OWN drawn household
    occupancy as `floor + (peak - floor) * occ(t)`. This is the only place in the codebase where
    the per-household series exist, which is why residential DHW is handled here and not in the
    commercial dispatch. Apartments are per-Space, so unlike office/retail/hotel the schedules
    cannot be shared across objects -- one derived Schedule:Compact per household, cached by
    (hh_id, floor, peak) so re-drawn duplicates do not multiply objects.

    Returns a dict: n_spaces, n_households_drawn, n_carriers_neutralized,
    assignment ({space_name: hh_id}), schedule_names (list), dhw_applied, dhw_unresolved.
    """
    result = {
        "n_spaces": 0, "n_households_drawn": 0, "n_carriers_neutralized": 0,
        "assignment": {}, "schedule_names": [], "dhw_applied": [], "dhw_unresolved": [],
        "dhw_excluded": [],
    }

    space_objs = idf.idfobjects.get("SPACE", [])
    resid_spaces = sorted(
        (s.Name for s in space_objs if str(getattr(s, "Tag_2", "") or "").strip() in TAG2_RESIDENTIAL),
        key=str,
    )
    n_spaces = len(resid_spaces)
    result["n_spaces"] = n_spaces
    if n_spaces == 0:
        if verbose:
            print("  [inject_residential] 0 residential apartment Spaces found (Tag-2 exact "
                  "'HighriseApartment Apartment') -- nothing to do")
        return result

    pool = load_residential_pool(csv_path, dtype_filter=dtype_filter)
    hh_ids = draw_residential_households(pool, n_spaces, seed=seed)
    result["n_households_drawn"] = len(hh_ids)

    # ---- Neutralize the existing SpaceList-level carrier(s) (2J Bug A fix, step 1) ----
    n_neut = 0
    for p in idf.idfobjects.get("PEOPLE", []):
        ref = _get_zone_name(p).strip()
        if ref in TAG2_RESIDENTIAL:
            try:
                p.Number_of_People_Calculation_Method = "People"
            except Exception:
                pass
            try:
                p.Number_of_People = 0
            except Exception:
                pass
            try:
                p.People_per_Floor_Area = ""
            except Exception:
                pass
            try:
                p.Floor_Area_per_Person = ""
            except Exception:
                pass
            n_neut += 1
    result["n_carriers_neutralized"] = n_neut
    if verbose:
        print(f"  [inject_residential] neutralized {n_neut} SpaceList-level carrier PEOPLE "
              f"object(s) referencing 'HighriseApartment Apartment' directly")

    # ---- Emit one PEOPLE object + 2 Schedule:Compact objects per Space (step 2) ----
    for space_name, hh_id in zip(resid_spaces, hh_ids):
        hh = pool[hh_id]
        occ_sch_name = f"MXU_Residential_Occ_HH{hh_id}"
        met_sch_name = f"MXU_Residential_Met_HH{hh_id}"

        # Idempotent: if this household's schedules were already created for a previous Space
        # in this same call (cannot happen with no-replacement draws, but guards re-entrant
        # calls / accidental double-invocation), don't duplicate the Schedule:Compact objects.
        if occ_sch_name not in result["schedule_names"]:
            occ_fields = _build_compact_fields_2dt(occ_sch_name, hh["occ_wd"], hh["occ_we"],
                                                     type_limit="Fraction")
            occ_obj = idf.newidfobject("Schedule:Compact")
            occ_obj.obj = ["Schedule:Compact"] + occ_fields

            met_fields = _build_compact_fields_2dt(met_sch_name, hh["met_wd"], hh["met_we"],
                                                     type_limit="Any Number")
            met_obj = idf.newidfobject("Schedule:Compact")
            met_obj.obj = ["Schedule:Compact"] + met_fields

            result["schedule_names"].append(occ_sch_name)
            result["schedule_names"].append(met_sch_name)

        p = idf.newidfobject("PEOPLE")
        p.Name = f"{space_name} People"
        p.Zone_or_ZoneList_or_Space_or_SpaceList_Name = space_name
        p.Number_of_People_Calculation_Method = "People"
        p.Number_of_People = hh["hhsize"]
        p.Number_of_People_Schedule_Name = occ_sch_name
        p.Activity_Level_Schedule_Name = met_sch_name
        p.Fraction_Radiant = 0.5
        p.Sensible_Heat_Fraction = "autocalculate"
        p.Carbon_Dioxide_Generation_Rate = 3.82e-08
        p.Enable_ASHRAE_55_Comfort_Warnings = "No"
        p.Mean_Radiant_Temperature_Calculation_Type = "EnclosureAveraged"

        result["assignment"][space_name] = hh_id

    # ---- T9-11: residential service hot water follows the SAME drawn household ----
    if dhw_model:
        hh_of_space = {str(k).strip().upper(): v for k, v in result["assignment"].items()}
        dhw_cache = {}                                   # (hh_id, floor_key, peak_key) -> name
        dhw_name_owner = {}                              # generated name -> key (uniqueness)
        # FINDING 8 measurement, not assumption: how many distinct (Space, prototype schedule)
        # pairs actually exist among the residential objects in THIS IDF. 1:1 means the
        # residential path was never colliding in practice; anything else means it was.
        _resid_space_proto = set()
        _resid_n_objects = 0
        for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", []):
            head = _wateruse_space_of(we)
            hh_id = hh_of_space.get(head)
            if hh_id is None:
                continue                                  # not a residential apartment object
            proto = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "")
            _resid_n_objects += 1
            _resid_space_proto.add((head, str(proto).strip().upper()))
            if _dhw_excluded(we, dhw_model):
                result["dhw_excluded"].append(
                    {"name": we.Name, "channel": "residential", "schedule": proto,
                     "reason": "batch process (exclude_schedule_tokens)"})
                continue

            if dhw_model.get("reference") in ("prototype_people", "baseline_series"):
                # T9-13: daily volume scaled by this household's occupancy against the prototype
                # occupancy the prototype DHW schedule was sized against; intra-day shape untouched.
                #
                # FINDING 3 (2026-08-02) -- this gate used to test `== "prototype_people"` only,
                # while the commercial path gates on BOTH values (see `_t9_13`, :1826-1827) and the
                # shipped DHW_MODEL_VOLUME_SCALED declares "baseline_series". So residential fell
                # through to the T9-11 rate model below (`apply_lighting_diversity(occ, ...)`) --
                # the model already refuted at +40.78 % -- while office/retail/hotel ran T9-13.
                # Silent, and invisible to the audit: `audit_dhw_shape_preservation` filters on
                # `model == "T9-13_volume_scaled"` and the T9-11 branch writes no `model` key, so
                # the gate would have PASSED on the commercial objects while the failing channel sat
                # outside its filter. A gate that passes because the broken objects are not in scope
                # is the seventh vacuous-test shape on this project. The `expect_channels` argument
                # added to the audit closes that hole from the other side.
                sprof, sprov = _schedule_daytype_profiles(idf, proto)
                if sprof is None or not dhw_reference:
                    result["dhw_unresolved"].append(
                        {"name": we.Name, "channel": "residential", "schedule": proto,
                         "reason": (f"shape: {sprov}" if sprof is None
                                    else "no prototype reference occupancy captured "
                                         "(PEOPLE already rewired?)")})
                    continue
                new_wd, new_we, info = apply_dhw_volume_scaling(
                    sprof["wd"], sprof["we"],
                    pool[hh_id]["occ_wd"], pool[hh_id]["occ_we"],
                    dhw_reference["wd"], dhw_reference["we"],
                    peak_policy=dhw_model.get("peak_policy", "rescale"),
                    r_max=float(dhw_model.get("r_max", 3.0)),
                    proto_by_daytype=sprof.get("by_daytype"))
                _new_dt = info.pop("new_by_daytype", None)   # kept out of the provenance
                if new_wd is None:
                    result["dhw_unresolved"].append(
                        {"name": we.Name, "channel": "residential", "schedule": proto,
                         "reason": info.get("error", "volume scaling failed")})
                    continue
                # FINDING 8 CORRECTION (2026-08-02): same defect class as the commercial path.
                # r_wd/r_we are functions of the HOUSEHOLD occupancy only, not of the object's
                # prototype schedule, so two WaterUse:Equipment objects in one apartment Space
                # carrying different prototype schedules collided onto the first one's shape.
                # hh_id narrowed the blast radius; it did not close the hole.
                key = (hh_id, str(proto).strip().upper(),
                       round(info["r_wd"], 4), round(info["r_we"], 4))
                nm = dhw_cache.get(key)
                if nm is None:
                    nm = (f"MXU_Residential_DHWv2_HH{hh_id}_{_sched_token(proto)}_"
                          f"r{int(round(key[2]*1000)):04d}w{int(round(key[3]*1000)):04d}")
                    if len(nm) > 100:
                        raise AssertionError(
                            f"T9-13 residential schedule name is {len(nm)} chars (>100, "
                            f"EnergyPlus alpha-field limit): '{nm}'")
                    prior = dhw_name_owner.get(nm)
                    if prior is not None and prior != key:
                        raise AssertionError(
                            f"T9-13 residential schedule-name collision: '{nm}' generated for "
                            f"BOTH {prior} and {key} -- _sched_token truncation re-created "
                            f"FINDING 8.")
                    dhw_name_owner[nm] = key
                    obj = idf.newidfobject("Schedule:Compact")
                    if _new_dt:          # FINDING 9: one block per distinct day-type profile
                        obj.obj = ["Schedule:Compact"] + _build_compact_fields_by_daytype(
                            nm, _new_dt, type_limit="Fraction")
                    else:
                        obj.obj = ["Schedule:Compact"] + _build_compact_fields_2dt(
                            nm, new_wd, new_we, type_limit="Fraction")
                        result.setdefault("t9_13_daytype_fallback", []).append(nm)
                    dhw_cache[key] = nm
                    result["schedule_names"].append(nm)
                we.Flow_Rate_Fraction_Schedule_Name = nm
                p_before = float(getattr(we, "Peak_Flow_Rate", 0.0) or 0.0)
                p_after = p_before * float(info["peak_multiplier"])
                we.Peak_Flow_Rate = p_after
                info["peak_flow_before"], info["peak_flow_after"] = p_before, p_after
                result["dhw_applied"].append(
                    {"name": we.Name, "channel": "residential", "prototype_schedule": proto,
                     "floor": None, "peak": None, "derived_schedule": nm,
                     "model": "T9-13_volume_scaled", "t9_13": info,
                     "provenance": f"shape: {sprov} | ref: {dhw_reference_prov}"})
                continue

            floor, fprov = _schedule_standby_floor(idf, proto)
            peak, pprov = _schedule_peak(idf, proto)
            if floor is None or peak is None:
                result["dhw_unresolved"].append(
                    {"name": we.Name, "channel": "residential", "schedule": proto,
                     "reason": f"floor: {fprov} | peak: {pprov}"})
                continue
            key = (hh_id, _floor_key(floor), _floor_key(peak))
            nm = dhw_cache.get(key)
            if nm is None:
                nm = f"MXU_Residential_DHW_HH{hh_id}_f{key[1]}p{key[2]}"
                fields = _build_compact_fields_2dt(
                    nm,
                    apply_lighting_diversity(pool[hh_id]["occ_wd"], floor, peak),
                    apply_lighting_diversity(pool[hh_id]["occ_we"], floor, peak),
                    type_limit="Fraction")
                obj = idf.newidfobject("Schedule:Compact")
                obj.obj = ["Schedule:Compact"] + fields
                dhw_cache[key] = nm
                result["schedule_names"].append(nm)
            we.Flow_Rate_Fraction_Schedule_Name = nm
            result["dhw_applied"].append(
                {"name": we.Name, "channel": "residential", "prototype_schedule": proto,
                 "floor": round(float(floor), 6), "peak": round(float(peak), 6),
                 "derived_schedule": nm, "provenance": f"{fprov} | peak: {pprov}"})
        result["dhw_space_proto_pairs"] = len(_resid_space_proto)
        result["dhw_n_objects_seen"] = _resid_n_objects
        if verbose:
            print(f"  [inject_residential] DHW: {len(result['dhw_applied'])} WaterUse:Equipment "
                  f"objects re-wired to their own household series, "
                  f"{len(result['dhw_unresolved'])} unresolved")
            print(f"  [FINDING 8 measure] residential objects={_resid_n_objects} "
                  f"distinct (Space, prototype schedule) pairs={len(_resid_space_proto)} "
                  f"-> {'1:1, this path was NOT colliding' if len(_resid_space_proto) == _resid_n_objects else 'NOT 1:1, this path WAS colliding'}")

    if verbose:
        print(f"  [inject_residential] {n_spaces} residential apartment Spaces <- {n_spaces} "
              f"distinct households (seed={seed}), {len(result['schedule_names'])} Schedule:"
              f"Compact objects created")

    return result


# ---------------------------------------------------------------------------
# inject_mixed_use -- the main entry point (generalizes inject_office_schedules)
# ---------------------------------------------------------------------------
def inject_mixed_use(idf_path: str, output_path: str, channels: dict, building_meta: dict,
                      verbose: bool = True, preserve_load_standby_floor: bool = True,
                      lighting_model: dict = None, dhw_model: dict = None) -> dict:
    """Inject office + retail + hotel MODULATE schedules into a mixed-use IDF, dispatched by
    exact Tag-2 match. Residential Spaces are left untouched (handled by the separate
    residential REPLACE injector). Densities (People/m2, LPD, plug W/m2) are NEVER scaled.

    Parameters
    ----------
    idf_path     : v24.2 mixed-use IDF (HighriseApartment tower + Office + Retail + LargeHotel).
    output_path  : destination IDF path.
    channels     : dict of per-channel config, e.g.
                   {"office": {"csv": "...", "archetype": "Office_Knowledge", "band": "hybrid"},
                    "retail": {"csv": "...", "pr": "QC"},
                    "hotel":  {"csv": "...", "pr": "QC"},
                    "residential": {"csv": "...", "seed": 42}}
                   A channel key absent or its CSV missing -> that channel's Spaces revert to
                   NECB baseline (W5 fall-back guarantee); the other channels still inject.
                   "residential" (OD-8R-L3, 2026-07-28) is REPLACE, not MODULATE: when absent,
                   residential apartment Spaces are left COMPLETELY untouched (no fallback entry
                   is appended for it, unlike office/retail/hotel) -- this keeps every existing
                   caller that never mentions "residential" byte-identical to before this key
                   existed (verified, see Step8_docs Progress Log).
    building_meta: free-form dict, echoed into the provenance log.
    preserve_load_standby_floor
                 : T9-9 (2026-07-31, defect S9D-8). When True (default), LIGHTS and
                   ELECTRICEQUIPMENT receive a DERIVED schedule
                   `floor + (1 - floor) * occ(t)`, where `floor` is read from the prototype
                   schedule that object currently carries. PEOPLE is unaffected. Set False to
                   reproduce the pre-fix behaviour exactly (one occupancy schedule written to
                   all three load classes) -- needed to regenerate the closed
                   campaign_cf69d508 artefacts. See the S9D-8 comment block above.
    lighting_model
                 : T9-10 (2026-07-31). LIGHTS-only diversity model, OFF by default.
                   None -> lighting keeps the T9-9 form `floor + (1 - floor) * occ`.
                   A dict (see LIGHTING_MODEL_ZONE) -> LIGHTS instead get
                   `floor + (peak - floor) * g(t)` with `peak` read from the replaced prototype
                   schedule, g = zone-coincidence `1 - (1 - occ)^office_n` for office, occ for
                   hotel, and for retail `open * (k + (1-k)*occ)` under
                   retail_mode="open_hours_mix" (T9-12, use LIGHTING_MODEL_CALIBRATED_V2) or the
                   WITHDRAWN pure `open` gate under retail_mode="open_closed", which produces
                   scenario-invariant retail lighting and exists only to reproduce arm B.
                   ELECTRICEQUIPMENT is never affected. Requires
                   preserve_load_standby_floor=True (floor and peak share one resolver);
                   ignored otherwise. See the T9-10 / T9-12 comment blocks above.
    dhw_model    : T9-11 (2026-07-31). WATERUSE:EQUIPMENT flow-fraction schedules, OFF by
                   default. None -> service hot water keeps its prototype schedule and stays
                   occupancy-invariant, exactly as before. A dict (see DHW_MODEL_PER_CAPITA) ->
                   every resolved object in `channels` gets `floor + (peak - floor) * occ(t)`,
                   floor and peak read from the prototype flow-fraction schedule it carries.
                   Objects whose schedule matches `exclude_schedule_tokens` (hotel laundry) are
                   left on the prototype and reported. Residential DHW rides each Space's own
                   drawn household series and therefore requires channels["residential"].
                   See the T9-11 comment block above.

    Returns
    -------
    dict: per-channel injected-Space counts + the W2/W3 wiring-assertion outcome (dry-run-
    compatible: if idf has no PEOPLE/LIGHTS/ELECTRICEQUIPMENT objects matching a channel's
    Tag-2 set, that channel reports 0 injected and is logged, not raised). Additionally
    `floor_applied` (one record per LIGHTS/EQUIP object re-floored, with its prototype
    schedule, resolved floor and provenance) and `floor_unresolved` (objects left on their
    prototype schedule because the floor could not be read -- these are NOT silently given the
    defective occupancy schedule).
    """
    try:
        from eppy.modeleditor import IDF
    except ImportError:
        raise ImportError("eppy not installed: pip install eppy")

    idd_path = _find_idd(idf_path)
    IDF.setiddname(idd_path)
    idf = IDF(idf_path)

    # D7 (FINDING 8) baseline: which flow-fraction schedule each WaterUse:Equipment object carried
    # BEFORE anything in this function ran. Taken here, at the top, because both DHW paths
    # (commercial below, residential inside inject_residential) overwrite the field in place and
    # there is no way to recover the original afterwards from `idf`.
    _we_proto_before = {
        str(we.Name).strip().upper():
            str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "").strip()
        for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", [])}

    result = {"office": {"n_spaces": 0, "n_lights": 0, "n_equip": 0},
              "retail": {"n_spaces": 0, "n_lights": 0, "n_equip": 0},
              "hotel":  {"n_spaces": 0, "n_lights": 0, "n_equip": 0},
              "residential": {"n_spaces": 0, "n_households_drawn": 0, "n_carriers_neutralized": 0},
              "fallback": [], "ambiguous": [], "modulated_schedule_names": [],
              "preserve_load_standby_floor": bool(preserve_load_standby_floor),
              "floor_applied": [], "floor_unresolved": [],
              "lighting_model": dict(lighting_model) if lighting_model else None,
              "light_diversity_applied": [],
              "dhw_model": dict(dhw_model) if dhw_model else None,
              "dhw_applied": [], "dhw_unresolved": [], "dhw_excluded": []}

    # ---- Load per-channel series (fall-back guarantee, W5) ----
    office_series = retail_series = hotel_series = None
    if "office" in channels and channels["office"].get("csv") and os.path.exists(channels["office"]["csv"]):
        office_series = load_office_series(channels["office"]["csv"], channels["office"]["archetype"],
                                            channels["office"]["band"])
    else:
        result["fallback"].append("office")
        if verbose:
            print("  [FALLBACK] office channel data missing -- Office Spaces revert to NECB baseline")

    if "retail" in channels and channels["retail"].get("csv") and os.path.exists(channels["retail"]["csv"]):
        retail_series = load_retail_series(channels["retail"]["csv"], channels["retail"]["pr"])
    else:
        result["fallback"].append("retail")
        if verbose:
            print("  [FALLBACK] retail channel data missing -- Retail Spaces revert to NECB baseline")

    if "hotel" in channels and channels["hotel"].get("csv") and os.path.exists(channels["hotel"]["csv"]):
        hotel_series = load_hotel_series(channels["hotel"]["csv"], channels["hotel"]["pr"])
    else:
        result["fallback"].append("hotel")
        if verbose:
            print("  [FALLBACK] hotel channel data missing -- Hotel guest-room Spaces revert to NECB baseline")

    # ---- Build Schedule:Compact objects up front (idempotent names) ----
    tag = f"{building_meta.get('scenario_label', 'scenario')}"
    sch_names = {}
    if office_series is not None:
        nm = f"MXU_Office_People_{tag}"
        modulate_baseline(idf, "OpenOffice", nm, office_series["wd"], office_series["we"], verbose=verbose)
        sch_names["office"] = nm
        result["modulated_schedule_names"].append(nm)
    if retail_series is not None:
        nm = f"MXU_Retail_People_{tag}"
        modulate_baseline(idf, "Retail Retail", nm, retail_series["wd"], None,
                           sun_vals=retail_series["sun"], sat_vals=retail_series["sat"], verbose=verbose)
        sch_names["retail"] = nm
        result["modulated_schedule_names"].append(nm)
    if hotel_series is not None:
        nm = f"MXU_Hotel_GuestRoom_{tag}"
        modulate_baseline_monthly(idf, "LargeHotel GuestRoom5", nm, hotel_series["monthly_wd"],
                                   hotel_series["monthly_we"], verbose=verbose)
        sch_names["hotel"] = nm
        result["modulated_schedule_names"].append(nm)

    # ---- Dispatch per Space: PEOPLE via Number_of_People_Schedule_Name (the Leg-2 field bug) ----
    # NOTE (2026-07-28, AUDIT-W job 1169582): the previous version also wrote
    # `Interpolate_to_Timestep="No"` on LIGHTS/ELECTRICEQUIPMENT. That field does NOT exist on
    # Lights/ElectricEquipment (it belongs to Schedule:Day:Interval), so eppy raised on every
    # commercial load object -- 26 spurious "injection failed" WARN lines per run. The schedule
    # assignment itself had already landed (it precedes the throw), so the wiring was correct, but
    # (a) the noise would mask a genuine failure across a 56-run campaign and (b) reordering the two
    # setattr calls would have silently dropped the LIGHTS/EQUIP wiring -- the Leg-2 bug again.
    # Removed. Per-class counters added so LIGHTS/EQUIP coverage is now measurable by the W-gates.
    # T9-9 (2026-07-31): PEOPLE still gets the raw occupancy schedule -- unchanged, byte-identical.
    # LIGHTS/ELECTRICEQUIPMENT now get a DERIVED schedule that re-imposes the standby floor of the
    # prototype schedule each object currently carries (see the S9D-8 block above). One derived
    # object per (channel, floor) -- object count stays small: distinct floors are few (office
    # equip 0.200, office lights 0.0453, retail lights 0.05, ...), not one per Space.
    _raw_series = {"office": office_series, "retail": retail_series, "hotel": hotel_series}
    _derived_cache = {}      # (channel, floor_key) -> schedule name

    def _derived_schedule_for(channel, floor):
        """Get-or-create the floor-preserving load schedule for (channel, floor)."""
        key = (channel, _floor_key(floor))
        if key in _derived_cache:
            return _derived_cache[key]
        series, nm = _raw_series[channel], f"MXU_{channel.capitalize()}_Load_f{_floor_key(floor)}_{tag}"
        if channel == "office":
            modulate_baseline(idf, "OpenOffice", nm,
                              apply_standby_floor(series["wd"], floor),
                              apply_standby_floor(series["we"], floor), verbose=False)
        elif channel == "retail":
            modulate_baseline(idf, "Retail Retail", nm,
                              apply_standby_floor(series["wd"], floor), None,
                              sun_vals=apply_standby_floor(series["sun"], floor),
                              sat_vals=apply_standby_floor(series["sat"], floor), verbose=False)
        else:  # hotel
            modulate_baseline_monthly(idf, "LargeHotel GuestRoom5", nm,
                                      apply_standby_floor(series["monthly_wd"], floor),
                                      apply_standby_floor(series["monthly_we"], floor), verbose=False)
        _derived_cache[key] = nm
        result["modulated_schedule_names"].append(nm)
        if verbose:
            print(f"  [standby-floor] {channel}: derived {nm} (floor={floor:.4f})")
        return nm

    # ---- T9-10 lighting diversity (LIGHTS only, opt-in) ----
    _light_cache = {}        # (channel, floor_key, peak_key) -> schedule name

    def _derived_light_schedule_for(channel, floor, peak):
        """Get-or-create the diversity-aware LIGHTS schedule for (channel, floor, peak)."""
        key = (channel, _floor_key(floor), _floor_key(peak))
        if key in _light_cache:
            return _light_cache[key]
        series = _raw_series[channel]
        nm = f"MXU_{channel.capitalize()}_Light_f{key[1]}p{key[2]}_{tag}"
        n_office = int(lighting_model.get("office_n", 1))
        n_hotel = int(lighting_model.get("hotel_n", 1))
        retail_mode = str(lighting_model.get("retail_mode", "open_closed"))
        k_open = float(lighting_model.get("retail_k_open", 1.0))
        if retail_mode not in ("open_closed", "open_hours_mix", "occupancy"):
            raise ValueError(f"lighting_model retail_mode={retail_mode!r} not understood "
                             f"(open_closed | open_hours_mix | occupancy)")
        if channel == "office":
            modulate_baseline(idf, "OpenOffice", nm,
                              apply_lighting_diversity(series["wd"], floor, peak, n_zone=n_office),
                              apply_lighting_diversity(series["we"], floor, peak, n_zone=n_office),
                              verbose=False)
        elif channel == "retail":
            if retail_mode in ("open_closed", "open_hours_mix"):
                # staff_shoulder_flag == 1 <=> closed/staff-only  =>  open = 1 - flag
                g = {dt: [1.0 - float(x) for x in series[f"{dt}_staff_shoulder"]]
                     for dt in ("wd", "sat", "sun")}
                # open_closed is the WITHDRAWN T9-10 form and is exactly k_open == 1.0
                kr = 1.0 if retail_mode == "open_closed" else k_open
            else:
                g = {dt: None for dt in ("wd", "sat", "sun")}
                kr = 1.0
            modulate_baseline(idf, "Retail Retail", nm,
                              apply_lighting_diversity(series["wd"], floor, peak,
                                                       open_flags=g["wd"], k_open=kr), None,
                              sun_vals=apply_lighting_diversity(series["sun"], floor, peak,
                                                                open_flags=g["sun"], k_open=kr),
                              sat_vals=apply_lighting_diversity(series["sat"], floor, peak,
                                                                open_flags=g["sat"], k_open=kr),
                              verbose=False)
        else:  # hotel
            modulate_baseline_monthly(idf, "LargeHotel GuestRoom5", nm,
                                      apply_lighting_diversity(series["monthly_wd"], floor, peak,
                                                               n_zone=n_hotel),
                                      apply_lighting_diversity(series["monthly_we"], floor, peak,
                                                               n_zone=n_hotel),
                                      verbose=False)
        _light_cache[key] = nm
        result["modulated_schedule_names"].append(nm)
        if verbose:
            print(f"  [light-diversity] {channel}: derived {nm} "
                  f"(floor={floor:.4f} peak={peak:.4f})")
        return nm

    # ---- T9-13: capture the REFERENCE occupancy BEFORE any PEOPLE rewiring happens ----
    # Ordering is load-bearing. The dispatch loop immediately below overwrites
    # Number_of_People_Schedule_Name with an MXU_* schedule, and `_schedule_daytype_profiles`
    # correctly refuses MXU_* (the prototype is no longer recoverable from the IDF). So the
    # reference must be read here or not at all. One representative PEOPLE object per channel --
    # the first that resolves -- and which object it was is recorded in the provenance.
    _t9_13 = bool(dhw_model) and dhw_model.get("reference") in ("prototype_people",
                                                                "baseline_series")
    _proto_occ, _proto_occ_prov = {}, {}
    if _t9_13 and dhw_model.get("reference") == "baseline_series":
        # Per-channel mean occupancy of the BASELINE scenario, PER DAY TYPE:
        #     {channel: {"wd": x, "we": y}}
        #
        # FINDING 4 (2026-08-02) -- this used to be one scalar held flat across both day types, and
        # that was wrong twice over. (a) The baseline scenario was then not a no-op: a no-op needs
        # r_wd == r_we == 1, i.e. mean(occ_wd) == mean(occ_we) == the scalar, which no scalar
        # satisfies when the two day-type means differ (office Y2022: 0.2530 vs 0.0651).
        # (b) Worse, with a common denominator r_we/r_wd collapses to mean(occ_we)/mean(occ_wd) --
        # OUR series' day-type asymmetry -- which then multiplies the PROTOTYPE schedule's own
        # asymmetry. Measured on this tower: prototype office we/wd = 0.311, our ratio = 0.257,
        # product = 0.080. Office weekend DHW would have collapsed to 8% of weekday instead of 31%
        # and been reported as an occupancy result. T9-13's whole premise is that SHAPE (including
        # the weekday/weekend split) comes from the prototype and only VOLUME comes from occupancy;
        # a scalar reference breaks that on the day-type axis.
        #
        # A bare scalar is still accepted and still means "flat across both day types", for an IDF
        # where that is genuinely what is wanted -- but it is no longer what this project ships.
        # Channels absent from the map stay unresolved; never defaulted to 1.0.
        for _ch, _v in (dhw_model.get("reference_occ_mean") or {}).items():
            if isinstance(_v, dict):
                try:
                    _wd, _we = float(_v["wd"]), float(_v["we"])
                except (TypeError, ValueError, KeyError):
                    continue
                if _wd > 1e-12 and _we > 1e-12:
                    _proto_occ[_ch] = {"wd": [_wd] * 24, "we": [_we] * 24}
                    _proto_occ_prov[_ch] = (f"baseline_series mean occupancy "
                                            f"wd={_wd:.6f} we={_we:.6f}")
                continue
            try:
                _fv = float(_v)
            except (TypeError, ValueError):
                continue
            if _fv > 1e-12:
                _proto_occ[_ch] = {"wd": [_fv] * 24, "we": [_fv] * 24}
                _proto_occ_prov[_ch] = (f"baseline_series FLAT weekly-mean occupancy = {_fv:.6f} "
                                        f"(scalar form -- see FINDING 4)")
        result["t9_13_reference"] = dict(_proto_occ_prov)
        if verbose:
            for _ch in sorted(_proto_occ_prov):
                print(f"  [T9-13 ref] {_ch}: {_proto_occ_prov[_ch]}")
            _missing = [c for c in dhw_model.get("channels", ()) if c not in _proto_occ]
            if _missing:
                print(f"  WARN: T9-13 baseline reference missing for {_missing} -- those channels "
                      f"stay on their prototype DHW schedule (recorded, never defaulted to 1.0)")
    elif _t9_13:
        _fine2agg = {"office": "office", "office_support": "office", "retail": "retail",
                     "hotel": "hotel", "hotel_support": "hotel", "residential": "residential"}
        for obj in idf.idfobjects.get("PEOPLE", []):
            tag2 = getattr(obj, "Space_Type_Name", "") or _get_zone_name(obj)
            ch = _fine2agg.get(classify_tag2(tag2))
            if ch is None or ch in _proto_occ:
                continue
            nm = str(getattr(obj, "Number_of_People_Schedule_Name", "") or "")
            prof, prov = _schedule_daytype_profiles(idf, nm)
            if prof is not None:
                _proto_occ[ch] = prof
                _proto_occ_prov[ch] = f"'{nm}' via {tag2}: {prov}"
        result["t9_13_reference"] = dict(_proto_occ_prov)
        if verbose:
            for ch in sorted(_proto_occ_prov):
                print(f"  [T9-13 ref] {ch}: {_proto_occ_prov[ch]}")
            missing = [c for c in dhw_model.get("channels", ()) if c not in _proto_occ]
            if missing:
                print(f"  WARN: T9-13 reference occupancy unresolved for {missing} -- those "
                      f"channels stay on their prototype DHW schedule (recorded, not silent)")

    _COUNTER_KEY = {"PEOPLE": "n_spaces", "LIGHTS": "n_lights", "ELECTRICEQUIPMENT": "n_equip"}
    for obj_class, sch_field in [
        ("PEOPLE", "Number_of_People_Schedule_Name"),
        ("LIGHTS", "Schedule_Name"),
        ("ELECTRICEQUIPMENT", "Schedule_Name"),
    ]:
        for obj in idf.idfobjects.get(obj_class, []):
            zone = _get_zone_name(obj)
            tag2 = getattr(obj, "Space_Type_Name", "") or zone  # best-effort Tag-2 recovery
            channel = classify_tag2(tag2)
            if channel in ("residential", "residential_common"):
                continue  # handled by the separate residential injector
            if channel in ("office", "retail", "hotel") and channel in sch_names:
                target_sch = sch_names[channel]
                if preserve_load_standby_floor and obj_class in ("LIGHTS", "ELECTRICEQUIPMENT"):
                    proto = getattr(obj, sch_field, "")
                    floor, prov = _schedule_standby_floor(idf, proto)
                    if floor is None:
                        # Never silently fall back to the defective behaviour: leave the object on
                        # its prototype schedule and record it, so a W-gate can count it.
                        result["floor_unresolved"].append(
                            {"channel": channel, "tag2": tag2, "obj_class": obj_class,
                             "schedule": str(proto), "reason": prov})
                        if verbose:
                            print(f"  WARN: standby floor unresolved for {tag2} ({obj_class}, "
                                  f"'{proto}'): {prov} -- left on prototype schedule")
                        continue
                    # T9-10: LIGHTS may additionally take the diversity model (opt-in). If the
                    # peak cannot be read we do NOT fall back to the linear form silently --
                    # the object is recorded as unresolved, same discipline as the floor.
                    peak = None
                    if lighting_model and obj_class == "LIGHTS":
                        peak, pprov = _schedule_peak(idf, proto)
                        if peak is None:
                            result["floor_unresolved"].append(
                                {"channel": channel, "tag2": tag2, "obj_class": obj_class,
                                 "schedule": str(proto), "reason": f"peak: {pprov}"})
                            if verbose:
                                print(f"  WARN: lighting peak unresolved for {tag2} "
                                      f"('{proto}'): {pprov} -- left on prototype schedule")
                            continue
                    if peak is not None:
                        target_sch = _derived_light_schedule_for(channel, floor, peak)
                        result["light_diversity_applied"].append(
                            {"channel": channel, "tag2": tag2,
                             "prototype_schedule": str(proto), "floor": round(float(floor), 6),
                             "peak": round(float(peak), 6), "derived_schedule": target_sch,
                             "provenance": f"{prov} | peak: {pprov}"})
                    else:
                        target_sch = _derived_schedule_for(channel, floor)
                    result["floor_applied"].append(
                        {"channel": channel, "tag2": tag2, "obj_class": obj_class,
                         "prototype_schedule": str(proto), "floor": round(float(floor), 6),
                         "derived_schedule": target_sch, "provenance": prov})
                try:
                    setattr(obj, sch_field, target_sch)
                    result[channel][_COUNTER_KEY[obj_class]] += 1
                except Exception as e:
                    if verbose:
                        print(f"  WARN: {channel} injection failed for {tag2} ({obj_class}): {e}")
            elif channel == "unknown" and obj_class == "PEOPLE":
                result["ambiguous"].append(tag2)

    # ---- T9-11: occupancy-driven service hot water (WATERUSE:EQUIPMENT), opt-in ----
    # office/retail/hotel only here; residential DHW rides the per-Space household series and is
    # handled inside inject_residential, which is the only place those series exist.
    _dhw_cache = {}          # (channel, floor_key, peak_key) -> schedule name

    def _derived_dhw_schedule_for(channel, floor, peak):
        """Get-or-create the occupancy-driven DHW flow-fraction schedule for (channel, floor, peak).

        n_zone=1 throughout: water draw is per-capita, so the linear form is the correct one --
        the zone-coincidence exponent is a LIGHTING concept and must not leak into DHW.
        """
        key = (channel, _floor_key(floor), _floor_key(peak))
        if key in _dhw_cache:
            return _dhw_cache[key]
        series = _raw_series[channel]
        nm = f"MXU_{channel.capitalize()}_DHW_f{key[1]}p{key[2]}_{tag}"
        if channel == "office":
            modulate_baseline(idf, "OpenOffice", nm,
                              apply_lighting_diversity(series["wd"], floor, peak),
                              apply_lighting_diversity(series["we"], floor, peak), verbose=False)
        elif channel == "retail":
            modulate_baseline(idf, "Retail Retail", nm,
                              apply_lighting_diversity(series["wd"], floor, peak), None,
                              sun_vals=apply_lighting_diversity(series["sun"], floor, peak),
                              sat_vals=apply_lighting_diversity(series["sat"], floor, peak),
                              verbose=False)
        else:  # hotel
            modulate_baseline_monthly(idf, "LargeHotel GuestRoom5", nm,
                                      apply_lighting_diversity(series["monthly_wd"], floor, peak),
                                      apply_lighting_diversity(series["monthly_we"], floor, peak),
                                      verbose=False)
        _dhw_cache[key] = nm
        result["modulated_schedule_names"].append(nm)
        if verbose:
            print(f"  [dhw] {channel}: derived {nm} (floor={floor:.4f} peak={peak:.4f})")
        return nm

    def _to24(vals):
        """Collapse a 24- or 48-slot series (or a {month: series} dict) to 24 hourly values."""
        if isinstance(vals, dict):
            months = [_to24(v) for v in vals.values()]
            if not months:
                return None
            return [sum(m[h] for m in months) / len(months) for h in range(24)]
        v = [float(x) for x in vals]
        if len(v) == 24:
            return v
        if len(v) == 48:
            return [(v[2 * h] + v[2 * h + 1]) / 2.0 for h in range(24)]
        if not v:
            return None
        return [v[min(len(v) - 1, int(h * len(v) / 24))] for h in range(24)]

    def _channel_occ_24(channel):
        """(occ_wd[24], occ_we[24]) of the INJECTED occupancy for a commercial channel."""
        s = _raw_series.get(channel)
        if not s:
            return None, None
        if channel == "hotel":
            return _to24(s.get("monthly_wd")), _to24(s.get("monthly_we"))
        if channel == "retail":
            sat, sun = s.get("sat"), s.get("sun")
            we = None
            if sat is not None and sun is not None:
                a, b = _to24(sat), _to24(sun)
                we = [(x + y) / 2.0 for x, y in zip(a, b)]
            elif s.get("we") is not None:
                we = _to24(s["we"])
            return _to24(s.get("wd")), we
        return _to24(s.get("wd")), _to24(s.get("we"))

    _t9_13_cache = {}
    _t9_13_name_owner = {}       # generated name -> key that created it (uniqueness assertion)

    def _t9_13_schedule_for(channel, proto, r_wd, r_we, new_wd, new_we, new_by_daytype=None):
        """Get-or-create the T9-13 volume-scaled flow-fraction schedule.

        FINDING 8 CORRECTION (2026-08-02): the key is (channel, SOURCE SCHEDULE, r_wd, r_we).
        The source schedule was previously absent, which made every object in a channel share the
        first object's shape -- see the _sched_token comment block. One schedule per
        (channel, source schedule, r) is the correct cardinality: r is channel-wide, the shape is
        per source schedule, and objects that genuinely share both genuinely share a schedule.
        """
        key = (channel, str(proto).strip().upper(),
               round(float(r_wd), 4), round(float(r_we), 4))
        if key in _t9_13_cache:
            return _t9_13_cache[key]
        nm = (f"MXU_{channel.capitalize()}_DHWv2_{_sched_token(proto)}_"
              f"r{int(round(key[2] * 1000)):04d}w{int(round(key[3] * 1000)):04d}_{tag}")
        # EnergyPlus alpha fields are 100 characters. A silently truncated Name would break the
        # reference (or, worse, merge two schedules), so refuse rather than emit one.
        if len(nm) > 100:
            raise AssertionError(
                f"T9-13 schedule name is {len(nm)} chars (>100, EnergyPlus alpha-field limit): "
                f"'{nm}'. Lower _SCHED_TOKEN_MAXLEN -- the hash-suffix form is already applied "
                f"above that length, so shortening it stays collision-safe.")
        # A truncation collision in _sched_token would silently recreate FINDING 8. Assert it.
        prior = _t9_13_name_owner.get(nm)
        if prior is not None and prior != key:
            raise AssertionError(
                f"T9-13 schedule-name collision: '{nm}' generated for BOTH {prior} and {key}. "
                f"_sched_token truncated two distinct prototype schedules to the same token -- "
                f"this is the FINDING 8 defect re-created by the fix for it.")
        _t9_13_name_owner[nm] = key
        obj = idf.newidfobject("Schedule:Compact")
        # FINDING 9: write one block per DISTINCT day-type profile. The 2-day-type writer is kept
        # only as the fallback for a source that genuinely resolved no per-day-type map, and that
        # case is recorded in the provenance rather than silently taking this path.
        if new_by_daytype:
            obj.obj = ["Schedule:Compact"] + _build_compact_fields_by_daytype(
                nm, new_by_daytype, type_limit="Fraction")
        else:
            obj.obj = ["Schedule:Compact"] + _build_compact_fields_2dt(nm, new_wd, new_we,
                                                                       type_limit="Fraction")
            result.setdefault("t9_13_daytype_fallback", []).append(nm)
        _t9_13_cache[key] = nm
        result["modulated_schedule_names"].append(nm)
        if verbose:
            print(f"  [T9-13] {channel}: derived {nm} (src='{proto}' r_wd={key[2]} r_we={key[3]})")
        return nm

    if dhw_model:
        _dhw_channels = tuple(dhw_model.get("channels", ()))
        _we_channel = _wateruse_channel_map(idf)
        for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", []):
            key = str(we.Name).strip().upper()
            channel = _we_channel.get(key)
            proto = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "")
            if channel is None:
                # Never silently leave an unattributed object looking like a success.
                result["dhw_unresolved"].append(
                    {"name": we.Name, "schedule": proto, "reason": "channel unresolved"})
                continue
            if channel not in _dhw_channels or channel not in sch_names:
                continue          # residential handled below; channels not requested are skipped
            if _dhw_excluded(we, dhw_model):
                result["dhw_excluded"].append(
                    {"name": we.Name, "channel": channel, "schedule": proto,
                     "reason": "batch process (exclude_schedule_tokens)"})
                continue
            if _t9_13:
                # T9-13: modulate DAILY VOLUME, carry the intra-day SHAPE through untouched.
                sprof, sprov = _schedule_daytype_profiles(idf, proto)
                ref = _proto_occ.get(channel)
                if sprof is None or ref is None:
                    result["dhw_unresolved"].append(
                        {"name": we.Name, "channel": channel, "schedule": proto,
                         "reason": (f"shape: {sprov}" if sprof is None
                                    else "no prototype reference occupancy for this channel")})
                    continue
                occ_wd, occ_we = _channel_occ_24(channel)
                if occ_wd is None:
                    result["dhw_unresolved"].append(
                        {"name": we.Name, "channel": channel, "schedule": proto,
                         "reason": "injected occupancy series unavailable for this channel"})
                    continue
                new_wd, new_we, info = apply_dhw_volume_scaling(
                    sprof["wd"], sprof["we"], occ_wd, occ_we, ref["wd"], ref["we"],
                    peak_policy=dhw_model.get("peak_policy", "rescale"),
                    r_max=float(dhw_model.get("r_max", 3.0)),
                    proto_by_daytype=sprof.get("by_daytype"))
                if new_wd is None:
                    result["dhw_unresolved"].append(
                        {"name": we.Name, "channel": channel, "schedule": proto,
                         "reason": info.get("error", "volume scaling failed")})
                    continue
                # 8 x 24 floats per object -- kept out of the provenance/manifest deliberately.
                _new_dt = info.pop("new_by_daytype", None)
                target_sch = _t9_13_schedule_for(channel, proto, info["r_wd"], info["r_we"],
                                                 new_wd, new_we, new_by_daytype=_new_dt)
                try:
                    we.Flow_Rate_Fraction_Schedule_Name = target_sch
                    # Restore the volume that dividing the shape by R removed. Peak_Flow_Rate is
                    # the ONLY sizing field touched, and its before/after pair is recorded.
                    p_before = float(getattr(we, "Peak_Flow_Rate", 0.0) or 0.0)
                    p_after = p_before * float(info["peak_multiplier"])
                    we.Peak_Flow_Rate = p_after
                    info["peak_flow_before"] = p_before
                    info["peak_flow_after"] = p_after
                    result["dhw_applied"].append(
                        {"name": we.Name, "channel": channel, "prototype_schedule": proto,
                         "floor": None, "peak": None, "derived_schedule": target_sch,
                         "model": "T9-13_volume_scaled", "t9_13": info,
                         "provenance": f"shape: {sprov} | ref: {_proto_occ_prov.get(channel, '')}"})
                except Exception as e:
                    result["dhw_unresolved"].append(
                        {"name": we.Name, "channel": channel, "schedule": proto,
                         "reason": f"setattr failed: {e}"})
                continue

            floor, fprov = _schedule_standby_floor(idf, proto)
            peak, pprov = _schedule_peak(idf, proto)
            if floor is None or peak is None:
                # Same discipline as T9-9/T9-10: leave it on the prototype, record it, never
                # fall back to a form nobody chose.
                result["dhw_unresolved"].append(
                    {"name": we.Name, "channel": channel, "schedule": proto,
                     "reason": f"floor: {fprov} | peak: {pprov}"})
                if verbose:
                    print(f"  WARN: DHW floor/peak unresolved for '{we.Name}' ('{proto}') "
                          f"-- left on prototype schedule")
                continue
            target_sch = _derived_dhw_schedule_for(channel, floor, peak)
            try:
                we.Flow_Rate_Fraction_Schedule_Name = target_sch
                result["dhw_applied"].append(
                    {"name": we.Name, "channel": channel, "prototype_schedule": proto,
                     "floor": round(float(floor), 6), "peak": round(float(peak), 6),
                     "derived_schedule": target_sch, "provenance": f"{fprov} | peak: {pprov}"})
            except Exception as e:
                result["dhw_unresolved"].append(
                    {"name": we.Name, "channel": channel, "schedule": proto,
                     "reason": f"setattr failed: {e}"})

    # ---- Residential (OD-8R-L3, REPLACE) -- separate code path, byte-identical guarantee ----
    # Deliberately NOT symmetric with office/retail/hotel above: this block only runs (and only
    # touches `result["residential"]`, the print output, and the provenance file) when the
    # caller explicitly supplies channels["residential"]. A caller that omits it gets the exact
    # same IDF, the exact same console output, and the exact same provenance file as before this
    # channel existed -- see module docstring and Step8_docs Progress Log for the verification.
    residential_requested = "residential" in channels and channels["residential"].get("csv") \
        and os.path.exists(channels["residential"]["csv"])
    if residential_requested:
        _resid_dhw = dhw_model if (dhw_model and "residential" in tuple(
            dhw_model.get("channels", ()))) else None
        result["residential"] = inject_residential(
            idf, channels["residential"]["csv"],
            seed=channels["residential"].get("seed", 42),
            verbose=verbose,
            dhw_model=_resid_dhw,
            dhw_reference=_proto_occ.get("residential"),
            dhw_reference_prov=_proto_occ_prov.get("residential", ""),
        )
        # Fold the residential DHW records into the top-level lists so one provenance block
        # describes the whole building rather than two half-buildings.
        result["dhw_applied"].extend(result["residential"].get("dhw_applied", []))
        result["dhw_unresolved"].extend(result["residential"].get("dhw_unresolved", []))
        result["dhw_excluded"].extend(result["residential"].get("dhw_excluded", []))
        # FINDING 9: the residential path has its own `result` dict, so its day-type fallback list
        # has to be lifted here or it never reaches the provenance -- a fallback nobody can see is
        # the same failure as no fallback report at all.
        _rf = result["residential"].get("t9_13_daytype_fallback")
        if _rf:
            result.setdefault("t9_13_daytype_fallback", []).extend(_rf)
    elif "residential" in channels and verbose:
        print("  [FALLBACK] residential channel data missing -- apartment Spaces revert to "
              "whatever the source IDF already had (untouched, REPLACE not applied)")

    # ---- T9-13 diagnostic gate: shape preservation is an identity, so ASSERT it ----
    # Run before the save so a violation is visible in the same console block as the injection,
    # and stored on `result` so the campaign driver and the W-gates can read a machine-checkable
    # verdict rather than re-deriving it from the IDF.
    if _t9_13:
        _t913_recs = [r for r in result["dhw_applied"] if r.get("model") == "T9-13_volume_scaled"]
        # `expect_channels` = the channels actually REQUESTED for this cell, i.e. the intersection
        # of dhw_model["channels"] with the channels this scenario injects at all. A channel the
        # scenario deliberately omits (hotel in Y2005/Y2010/Y2015, DELIBERATE_CHANNEL_EXCEPTIONS)
        # must not be demanded here -- that would turn a documented design decision into a FAIL.
        _expect = tuple(c for c in dhw_model.get("channels", ()) if c in channels)
        _audit = audit_dhw_shape_preservation(_t913_recs, verbose=verbose,
                                              expect_channels=_expect)
        # Open item 5 (2026-08-02): the 4 Default_NECB control cells request NO DHW channels at
        # all, inject nothing, and were reported `audit_pass=False, n_audited=0` -- a FAIL for
        # having correctly done nothing. That is N/A, not a failure. The FAIL-on-empty rule is
        # kept everywhere else: a cell that asked for channels and audited 0 objects is still a
        # FAIL, which is the case the rule exists for.
        if not _expect and _audit["n"] == 0 and not _audit["violations"]:
            _audit["pass"] = None
            _audit["verdict"] = "N/A"
            if verbose:
                print("  [T9-13 audit N/A] this cell requested no DHW channels -- nothing to "
                      "audit, and nothing was injected")
        else:
            _audit["verdict"] = "PASS" if _audit["pass"] else "FAIL"
        result["t9_13_audit"] = _audit

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    idf.saveas(output_path)

    # ---- D7: the ASSIGNMENT check, read back from the file that was just written ----
    # Must come after the save (that is the point -- see audit_dhw_assignment's docstring), so its
    # verdict is folded into the same `t9_13_audit` dict the campaign driver and W-gates read.
    if _t9_13:
        _d7 = audit_dhw_assignment(output_path, result["dhw_applied"], _we_proto_before,
                                   verbose=verbose, idd_path=idd_path)
        result["t9_13_d7"] = _d7
        _a = result["t9_13_audit"]
        _a["counts"]["D7"] = _d7["n_d7"]
        _a["counts"]["D9"] = _d7["n_d9"]
        _a["violations"].extend(_d7["violations"])
        _a["n_wateruse_objects"] = _d7["n"]
        _a["d7_derived_names"] = _d7["derived_names"]
        _a["d9_unchecked"] = _d7["d9_unchecked"]
        if _a.get("pass") is None:
            # N/A cell: D7 still ran over the untouched objects, and a change there is a real
            # failure even though there was nothing to inject.
            if _d7["violations"]:
                _a["pass"], _a["verdict"] = False, "FAIL"
        else:
            _a["pass"] = bool(_a["pass"]) and bool(_d7["pass"])
            _a["verdict"] = "PASS" if _a["pass"] else "FAIL"

    if verbose:
        print(f"  Saved: {output_path}")
        print(f"  Injected PEOPLE: office={result['office']['n_spaces']} retail={result['retail']['n_spaces']} "
              f"hotel={result['hotel']['n_spaces']}; fallback={result['fallback']}; "
              f"ambiguous={len(set(result['ambiguous']))}")
        print(f"  Injected LIGHTS: office={result['office']['n_lights']} retail={result['retail']['n_lights']} "
              f"hotel={result['hotel']['n_lights']} | ELECTRICEQUIPMENT: office={result['office']['n_equip']} "
              f"retail={result['retail']['n_equip']} hotel={result['hotel']['n_equip']}")
        if dhw_model:
            print(f"  Injected DHW: {len(result['dhw_applied'])} WaterUse:Equipment re-wired, "
                  f"{len(result['dhw_excluded'])} excluded (batch), "
                  f"{len(result['dhw_unresolved'])} unresolved")
        if residential_requested:
            print(f"  Injected residential: {result['residential']['n_spaces']} apartment Spaces, "
                  f"{result['residential']['n_households_drawn']} distinct households drawn, "
                  f"{result['residential']['n_carriers_neutralized']} SpaceList-level carrier(s) neutralized")

    # Provenance log
    log_path = output_path + ".provenance.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"building_meta={building_meta}\n")
        f.write(f"channels_requested={list(channels.keys())}\n")
        f.write(f"fallback_channels={result['fallback']}\n")
        f.write(f"n_office_spaces={result['office']['n_spaces']}\n")
        f.write(f"n_retail_spaces={result['retail']['n_spaces']}\n")
        f.write(f"n_hotel_spaces={result['hotel']['n_spaces']}\n")
        for _ch in ("office", "retail", "hotel"):
            f.write(f"n_{_ch}_lights={result[_ch]['n_lights']} n_{_ch}_equip={result[_ch]['n_equip']}\n")
        f.write(f"ambiguous_tags={sorted(set(result['ambiguous']))}\n")
        f.write("density_basis=NECB baseline densities UNCHANGED for all channels\n")
        # T9-9 / S9D-8: standby-floor preservation on LIGHTS + ELECTRICEQUIPMENT
        f.write(f"preserve_load_standby_floor={result['preserve_load_standby_floor']}\n")
        f.write(f"n_floor_applied={len(result['floor_applied'])} "
                f"n_floor_unresolved={len(result['floor_unresolved'])}\n")
        _floors = sorted({(r["channel"], r["obj_class"], r["prototype_schedule"], r["floor"])
                          for r in result["floor_applied"]})
        for _ch, _cls, _proto, _fl in _floors:
            f.write(f"standby_floor {_ch} {_cls} '{_proto}' -> {_fl}\n")
        for r in result["floor_unresolved"]:
            f.write(f"standby_floor_UNRESOLVED {r['channel']} {r['obj_class']} "
                    f"'{r['schedule']}' reason={r['reason']}\n")
        # T9-10: LIGHTS-only diversity model
        f.write(f"lighting_model={result['lighting_model']}\n")
        f.write(f"n_light_diversity_applied={len(result['light_diversity_applied'])}\n")
        _lights = sorted({(r["channel"], r["prototype_schedule"], r["floor"], r["peak"])
                          for r in result["light_diversity_applied"]})
        for _ch, _proto, _fl, _pk in _lights:
            f.write(f"light_diversity {_ch} '{_proto}' -> floor={_fl} peak={_pk}\n")
        # T9-11: occupancy-driven service hot water
        f.write(f"dhw_model={result['dhw_model']}\n")
        f.write(f"n_dhw_applied={len(result['dhw_applied'])}\n")
        f.write(f"n_dhw_excluded={len(result['dhw_excluded'])}\n")
        f.write(f"n_dhw_unresolved={len(result['dhw_unresolved'])}\n")
        # floor/peak are None under T9-13 (it uses no extremum); -1 keeps the tuple sortable if a
        # future run ever mixes the two models in one IDF.
        _dhw = sorted({(r["channel"], r["prototype_schedule"],
                        -1.0 if r["floor"] is None else r["floor"],
                        -1.0 if r["peak"] is None else r["peak"])
                       for r in result["dhw_applied"]})
        for _ch, _proto, _fl, _pk in _dhw:
            f.write(f"dhw {_ch} '{_proto}' -> floor={_fl} peak={_pk}\n")
        for r in result["dhw_excluded"]:
            f.write(f"dhw_EXCLUDED {r['channel']} '{r['name']}' ({r['schedule']}): {r['reason']}\n")
        for r in result["dhw_unresolved"]:
            f.write(f"dhw_UNRESOLVED '{r['name']}' ({r.get('schedule', '')}): {r['reason']}\n")
        # T9-13: volume-scaled DHW -- diagnostics, one line per (channel, r_wd, r_we) plus the gate
        if result.get("t9_13_audit") is not None:
            a = result["t9_13_audit"]
            f.write(f"t9_13_audit_pass={a['pass']} n_audited={a['n']} counts={a['counts']}\n")
            # verdict is the tri-state form: PASS / FAIL / N/A. `pass=None` <=> N/A (the cell
            # requested no DHW channels), which is NOT the same as pass=False.
            f.write(f"t9_13_audit_verdict={a.get('verdict', 'FAIL')}\n")
            if result.get("t9_13_d7") is not None:
                d7 = result["t9_13_d7"]
                f.write(f"t9_13_d7_pass={d7['pass']} n_wateruse={d7['n']} "
                        f"n_own_derivative={d7['n_derived']} n_unchanged={d7['n_unchanged']} "
                        f"n_violations={len(d7['violations'])} "
                        f"n_d7={d7['n_d7']} n_d9={d7['n_d9']} "
                        f"d9_unchecked={len(d7['d9_unchecked'])}\n")
                for _nm in d7["derived_names"]:
                    f.write(f"t9_13_derived_name {_nm}\n")
            # FINDING 9: any schedule that had to fall back to the 2-day-type writer, named.
            for _nm in sorted(set(result.get("t9_13_daytype_fallback") or [])):
                f.write(f"t9_13_daytype_FALLBACK {_nm}\n")
            for v in a["violations"]:
                f.write(f"t9_13_VIOLATION {v['check']} '{v['obj']}': {v['detail']}\n")
            for _ch, _p in sorted(result.get("t9_13_reference", {}).items()):
                f.write(f"t9_13_reference {_ch}: {_p}\n")
            _seen = set()
            for r in result["dhw_applied"]:
                i = r.get("t9_13")
                if not i or "error" in i:
                    continue
                k = (r["channel"], i["r_wd"], i["r_we"])
                if k in _seen:
                    continue
                _seen.add(k)
                f.write(f"t9_13 {r['channel']} '{r['prototype_schedule']}' "
                        f"r_wd={i['r_wd']} r_we={i['r_we']} R={i['R']} "
                        f"peak_policy={i['peak_policy']} peak_mult={i['peak_multiplier']} "
                        f"nightshare={i['proto_nightshare_wd']}->{i['new_nightshare_wd']} "
                        f"peakhour={i['proto_peakhour_wd']}->{i['new_peakhour_wd']} "
                        f"max={i['proto_max']}->{i['new_max']} noop={i['is_noop']} "
                        f"clipped={i['r_clipped_at_r_max']}\n")
        if residential_requested:
            f.write(f"n_residential_spaces={result['residential']['n_spaces']}\n")
            f.write(f"n_residential_households_drawn={result['residential']['n_households_drawn']}\n")
            f.write(f"n_residential_carriers_neutralized={result['residential']['n_carriers_neutralized']}\n")
            f.write(f"residential_seed={channels['residential'].get('seed', 42)}\n")
            # FINDING 8 measurement (1b): is the residential path 1:1 (Space, prototype schedule)?
            f.write(f"residential_dhw_objects={result['residential'].get('dhw_n_objects_seen')} "
                    f"residential_dhw_space_proto_pairs="
                    f"{result['residential'].get('dhw_space_proto_pairs')}\n")
            f.write(f"residential_assignment={result['residential']['assignment']}\n")

    return result


# ---------------------------------------------------------------------------
# W-section wiring assertions (post-injection audit -- Leg-2 hard-wiring-gate lesson)
# ---------------------------------------------------------------------------
def assert_wiring(idf, expected_channels: dict, verbose: bool = True) -> dict:
    """W2 ONLY: for every Space this module CLAIMS to have modulated, assert the schedule is
    referenced by the CORRECT field (Number_of_People_Schedule_Name for People, NOT
    Schedule_Name -- the exact Leg-2 bug that made all 7 office scenarios simulate byte-
    identical). Assertion failure = abort, no product/no sbatch (per runbook).

    W3 (the modulated series != baseline wherever multiplier != 1) is DELIBERATELY NOT
    implemented here -- corrected 2026-07-28 (Step8_docs 3rdJ_08_implementation_improvements.md
    open item #3; this docstring previously advertised W2+W3 and was stale). W3 is implemented,
    tested and PASS-proven in 3rdJ_08W_audit_wiring.py (Block 5, `_representative_baseline_name`
    / `_schedule_profile`): it needs BOTH the pre-injection source IDF (to recover the baseline
    schedule a channel's Spaces referenced before injection) and the post-injection IDF, which
    this function's single-IDF signature does not carry. Duplicating that logic here, against a
    signature that can't hold the source IDF, would risk exactly the kind of drift this repo's
    "docstring contradicts code" lesson (open item #4) warns about -- so the one working W3
    implementation stays where it already runs, and this docstring is corrected to match the
    code instead of the code being stretched to match a stale docstring.

    NOTE: this function is exercised against the real v242 mixed-use prototype IDF (see the
    module docstring's 2026-07-28 correction) -- the earlier "no prototype IDF exists yet" caveat
    here is likewise stale and removed.
    """
    violations = []
    people_objs = idf.idfobjects.get("PEOPLE", [])
    claimed_names = set(expected_channels.values())
    for obj in people_objs:
        sch = getattr(obj, "Number_of_People_Schedule_Name", "")
        legacy_sch = getattr(obj, "Schedule_Name", "")
        if legacy_sch in claimed_names and sch not in claimed_names:
            violations.append(
                f"W2 VIOLATION: {_get_zone_name(obj)} -- schedule '{legacy_sch}' wired to "
                f"Schedule_Name instead of Number_of_People_Schedule_Name (Leg-2 bug pattern)"
            )
    assert not violations, "\n".join(violations)
    if verbose:
        print(f"  [W2 PASS] {len(people_objs)} PEOPLE objects audited, 0 field-reference violations")
    return {"violations": violations, "n_audited": len(people_objs)}
