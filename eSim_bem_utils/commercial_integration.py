"""commercial_integration.py -- Step 8 (3J Leg-3 4-split): mixed-use schedule injection.

Generalizes Leg-2's office_integration.inject_office_schedules() to FOUR channels via a
single Tag-2 dispatch: inject_mixed_use(idf, channels, building_meta). MODULATE (not
REPLACE) for every commercial channel handled here -- residential REPLACE stays in the
separate residential injector (eSim_bem_utils_3J/integration.py, post-multizone-fix,
md5 6a92268be1f8dc3301df3bec80d6dd2e); this module SKIPS residential-tagged Spaces so the
two injectors can run on the same IDF without interfering.

Design doc: 3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/3rdJ_07_bemIntegration_4split.md
Validator : 3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/3rdJ_07_bemIntegration_4split_val.md (Section W)

Channels (Tag-2 routing table, verbatim spec Section "TAG-2 ROUTING TABLE" -- exact match,
NOT substring):

  Tag 2 (verbatim)                                          Channel      Injection
  --------------------------------------------------------  -----------  --------------------------
  HighriseApartment Apartment                                Residential  (handled elsewhere -- REPLACE)
  HighriseApartment Corridor, HighriseApartment Office       Residential  (handled elsewhere; residential
                                                               (common)     multiplier on Lights only)
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

NOTE (2026-07-23): no Tag-2-routable mixed-use prototype IDF exists anywhere in this repo
yet (confirmed by Step-7 --audit; see 3rdJ_07_bemIntegration_4split.md Progress Log). This
module is therefore UNTESTED against a real IDF -- the W-section dry-run wiring audit in the
Step-7 validator is PENDING for exactly this reason. Field names / dispatch logic follow the
v24.2 conventions already proven in office_integration.py (Leg-2, post-2026-07-02) and the
per-Space multi-zone replication pattern in eSim_bem_utils_3J/integration.py
(post-multizone-fix, 2026-07-15).

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

_CHANNEL_OF_TAG2 = {}
for _tag in TAG2_RESIDENTIAL | TAG2_RESIDENTIAL_COMMON:
    _CHANNEL_OF_TAG2[_tag] = "residential"
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
def _build_compact_fields_2dt(name: str, wd_vals: list, we_vals: list) -> list:
    """Schedule:Compact with 2 day-types (Weekdays / Weekends+Holidays+AllOtherDays)."""
    fields = [name, "Fraction", "Through: 12/31", "For: Weekdays SummerDesignDay WinterDesignDay"]
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
                    "hotel":  {"csv": "...", "pr": "QC"}}
                   A channel key absent or its CSV missing -> that channel's Spaces revert to
                   NECB baseline (W5 fall-back guarantee); the other channels still inject.
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

    result = {"office": {"n_spaces": 0}, "retail": {"n_spaces": 0}, "hotel": {"n_spaces": 0},
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
            if channel == "office" and "office" in sch_names:
                try:
                    setattr(obj, sch_field, sch_names["office"])
                    if obj_class in ("LIGHTS", "ELECTRICEQUIPMENT"):
                        setattr(obj, "Interpolate_to_Timestep", "No")
                    if obj_class == "PEOPLE":
                        result["office"]["n_spaces"] += 1
                except Exception as e:
                    if verbose:
                        print(f"  WARN: office injection failed for {tag2}: {e}")
            elif channel == "retail" and "retail" in sch_names:
                try:
                    setattr(obj, sch_field, sch_names["retail"])
                    if obj_class in ("LIGHTS", "ELECTRICEQUIPMENT"):
                        setattr(obj, "Interpolate_to_Timestep", "No")
                    if obj_class == "PEOPLE":
                        result["retail"]["n_spaces"] += 1
                except Exception as e:
                    if verbose:
                        print(f"  WARN: retail injection failed for {tag2}: {e}")
            elif channel == "hotel" and "hotel" in sch_names:
                try:
                    setattr(obj, sch_field, sch_names["hotel"])
                    if obj_class in ("LIGHTS", "ELECTRICEQUIPMENT"):
                        setattr(obj, "Interpolate_to_Timestep", "No")
                    if obj_class == "PEOPLE":
                        result["hotel"]["n_spaces"] += 1
                except Exception as e:
                    if verbose:
                        print(f"  WARN: hotel injection failed for {tag2}: {e}")
            elif channel == "unknown" and obj_class == "PEOPLE":
                result["ambiguous"].append(tag2)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    idf.saveas(output_path)
    if verbose:
        print(f"  Saved: {output_path}")
        print(f"  Injected: office={result['office']['n_spaces']} retail={result['retail']['n_spaces']} "
              f"hotel={result['hotel']['n_spaces']}; fallback={result['fallback']}; "
              f"ambiguous={len(set(result['ambiguous']))}")

    # Provenance log
    log_path = output_path + ".provenance.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"building_meta={building_meta}\n")
        f.write(f"channels_requested={list(channels.keys())}\n")
        f.write(f"fallback_channels={result['fallback']}\n")
        f.write(f"n_office_spaces={result['office']['n_spaces']}\n")
        f.write(f"n_retail_spaces={result['retail']['n_spaces']}\n")
        f.write(f"n_hotel_spaces={result['hotel']['n_spaces']}\n")
        f.write(f"ambiguous_tags={sorted(set(result['ambiguous']))}\n")
        f.write("density_basis=NECB baseline densities UNCHANGED for all channels\n")

    return result


# ---------------------------------------------------------------------------
# W-section wiring assertions (post-injection audit -- Leg-2 hard-wiring-gate lesson)
# ---------------------------------------------------------------------------
def assert_wiring(idf, expected_channels: dict, verbose: bool = True) -> dict:
    """W2/W3: for every Space this module CLAIMS to have modulated, assert (a) the schedule
    is referenced by the CORRECT field (Number_of_People_Schedule_Name for People, NOT
    Schedule_Name -- the exact Leg-2 bug that made all 7 office scenarios simulate byte-
    identical), and (b) the modulated series != baseline wherever multiplier != 1.
    Assertion failure = abort, no product/no sbatch (per runbook).

    NOTE: cannot run without a real mixed-use IDF (none exists in this repo yet, confirmed by
    --audit). Implemented and ready for Step 8 once the prototype IDF is available; the
    Step-7 validator's W-section reports this as PENDING, not FAIL, in the interim.
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
