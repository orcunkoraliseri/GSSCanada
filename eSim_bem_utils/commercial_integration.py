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
import os
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
                        dhw_model: dict = None) -> dict:
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
        for we in idf.idfobjects.get("WATERUSE:EQUIPMENT", []):
            head = _wateruse_space_of(we)
            hh_id = hh_of_space.get(head)
            if hh_id is None:
                continue                                  # not a residential apartment object
            proto = str(getattr(we, "Flow_Rate_Fraction_Schedule_Name", "") or "")
            if _dhw_excluded(we, dhw_model):
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
        if verbose:
            print(f"  [inject_residential] DHW: {len(result['dhw_applied'])} WaterUse:Equipment "
                  f"objects re-wired to their own household series, "
                  f"{len(result['dhw_unresolved'])} unresolved")

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
        )
        # Fold the residential DHW records into the top-level lists so one provenance block
        # describes the whole building rather than two half-buildings.
        result["dhw_applied"].extend(result["residential"].get("dhw_applied", []))
        result["dhw_unresolved"].extend(result["residential"].get("dhw_unresolved", []))
    elif "residential" in channels and verbose:
        print("  [FALLBACK] residential channel data missing -- apartment Spaces revert to "
              "whatever the source IDF already had (untouched, REPLACE not applied)")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    idf.saveas(output_path)
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
        _dhw = sorted({(r["channel"], r["prototype_schedule"], r["floor"], r["peak"])
                       for r in result["dhw_applied"]})
        for _ch, _proto, _fl, _pk in _dhw:
            f.write(f"dhw {_ch} '{_proto}' -> floor={_fl} peak={_pk}\n")
        for r in result["dhw_excluded"]:
            f.write(f"dhw_EXCLUDED {r['channel']} '{r['name']}' ({r['schedule']}): {r['reason']}\n")
        for r in result["dhw_unresolved"]:
            f.write(f"dhw_UNRESOLVED '{r['name']}' ({r.get('schedule', '')}): {r['reason']}\n")
        if residential_requested:
            f.write(f"n_residential_spaces={result['residential']['n_spaces']}\n")
            f.write(f"n_residential_households_drawn={result['residential']['n_households_drawn']}\n")
            f.write(f"n_residential_carriers_neutralized={result['residential']['n_carriers_neutralized']}\n")
            f.write(f"residential_seed={channels['residential'].get('seed', 42)}\n")
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
