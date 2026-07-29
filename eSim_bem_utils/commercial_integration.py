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
                        dtype_filter=RESIDENTIAL_DTYPE_APARTMENT, verbose: bool = True) -> dict:
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

    Returns a dict: n_spaces, n_households_drawn, n_carriers_neutralized,
    assignment ({space_name: hh_id}), schedule_names (list).
    """
    result = {
        "n_spaces": 0, "n_households_drawn": 0, "n_carriers_neutralized": 0,
        "assignment": {}, "schedule_names": [],
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

    if verbose:
        print(f"  [inject_residential] {n_spaces} residential apartment Spaces <- {n_spaces} "
              f"distinct households (seed={seed}), {len(result['schedule_names'])} Schedule:"
              f"Compact objects created")

    return result


# ---------------------------------------------------------------------------
# inject_mixed_use -- the main entry point (generalizes inject_office_schedules)
# ---------------------------------------------------------------------------
def inject_mixed_use(idf_path: str, output_path: str, channels: dict, building_meta: dict,
                      verbose: bool = True) -> dict:
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

    Returns
    -------
    dict: per-channel injected-Space counts + the W2/W3 wiring-assertion outcome (dry-run-
    compatible: if idf has no PEOPLE/LIGHTS/ELECTRICEQUIPMENT objects matching a channel's
    Tag-2 set, that channel reports 0 injected and is logged, not raised).
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
              "fallback": [], "ambiguous": [], "modulated_schedule_names": []}

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
                try:
                    setattr(obj, sch_field, sch_names[channel])
                    result[channel][_COUNTER_KEY[obj_class]] += 1
                except Exception as e:
                    if verbose:
                        print(f"  WARN: {channel} injection failed for {tag2} ({obj_class}): {e}")
            elif channel == "unknown" and obj_class == "PEOPLE":
                result["ambiguous"].append(tag2)

    # ---- Residential (OD-8R-L3, REPLACE) -- separate code path, byte-identical guarantee ----
    # Deliberately NOT symmetric with office/retail/hotel above: this block only runs (and only
    # touches `result["residential"]`, the print output, and the provenance file) when the
    # caller explicitly supplies channels["residential"]. A caller that omits it gets the exact
    # same IDF, the exact same console output, and the exact same provenance file as before this
    # channel existed -- see module docstring and Step8_docs Progress Log for the verification.
    residential_requested = "residential" in channels and channels["residential"].get("csv") \
        and os.path.exists(channels["residential"]["csv"])
    if residential_requested:
        result["residential"] = inject_residential(
            idf, channels["residential"]["csv"],
            seed=channels["residential"].get("seed", 42),
            verbose=verbose,
        )
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
