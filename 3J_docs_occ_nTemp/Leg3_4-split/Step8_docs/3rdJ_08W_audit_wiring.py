"""3rdJ_08W_audit_wiring.py -- Step 8 (3J Leg-3 4-split) armament: AUDIT-W against the real
v24.2 mixed-use tower IDF.

Proves that inject_mixed_use() (eSim_bem_utils/commercial_integration.py) wires the modulated
office/retail/hotel schedules onto the CORRECT field (W2) and that the modulated series
actually DIFFER from the baseline (W3) -- the exact Leg-2 hard-wiring-gate lesson: 7 office
scenarios once simulated byte-identical in silence because the modulation never touched the
schedule field that mattered. W-FAIL blocks Step 8 unconditionally (see runbook 3rdJ_08_
simulation_4split.md Sec 8B / 3rdJ_08W prompt 2026-07-28).

Runs on the cluster only, via sbatch (PYTHONPATH=.../upload, EPLUS_IDD pre-set in env). This
script does NOT modify commercial_integration.py: W3 (baseline-vs-modulated numeric diff) is
NOT implemented in that module (its assert_wiring() docstring advertises W3 but the code only
does W2) -- W3 is implemented here, locally, as instructed.

Output: a single compact text report to stdout (redirected by the sbatch --wrap to a log
file). No IDF dumps. Every block is wrapped in try/except so a failure in one block does not
prevent the rest of the report from being produced -- the scorecard must always be complete.

2026-07-28 built (B1 of the Step-8 armament handoff).
"""
from __future__ import annotations

import os
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Paths (Linux, cluster-only; grouped here per runbook convention)
# ---------------------------------------------------------------------------
SCRATCH8 = "/speed-scratch/o_iseri/step8_4split"
UPLOAD = SCRATCH8 + "/upload"
IDF_V242 = (
    "/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/"
    "Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL/"
    "TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf"
)
STEP7_OUT = UPLOAD + "/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7"
OUT_IDF = SCRATCH8 + "/audit_w/TallBuilding_Z6_v242_injected.idf"

OFFICE_CSV = STEP7_OUT + "/office_presence_multiplier_2022.csv"
RETAIL_CSV = STEP7_OUT + "/retail_presence_multiplier_2022.csv"
HOTEL_CSV = STEP7_OUT + "/hotel_schedule_multiplier_2022.csv"

CHANNELS = {
    "office": {"csv": OFFICE_CSV, "archetype": "Office_Knowledge", "band": "observed"},
    "retail": {"csv": RETAIL_CSV, "pr": "QC"},
    "hotel": {"csv": HOTEL_CSV, "pr": "QC"},
}
BUILDING_META = {"building": "Tall", "city": "MTL", "cz": "Z6", "purpose": "W-audit"}

# Space census expectation is informative only -- NEVER used to force a PASS/FAIL.
EXPECTED_CENSUS = {"residential": 30, "office": 33, "retail": 9, "hotel": 25, "service_mep": 63,
                   "total": 164}

# ---------------------------------------------------------------------------
# Scorecard accumulator
# ---------------------------------------------------------------------------
RESULTS = []  # list of {"status": "PASS"/"WARN"/"FAIL", "check": str, "detail": str}


def report(status, check, detail):
    RESULTS.append({"status": status, "check": check, "detail": detail})


# ---------------------------------------------------------------------------
# Block 1 -- setup / imports / EPLUS_IDD check (immediate FAIL, nothing else can run without it)
# ---------------------------------------------------------------------------
sys.path.insert(0, UPLOAD)  # fallback in case PYTHONPATH wasn't propagated to the job env

EPLUS_IDD = os.environ.get("EPLUS_IDD", "")
if not EPLUS_IDD or not os.path.isfile(EPLUS_IDD):
    print(f"[FAIL] EPLUS_IDD not set or file missing: '{EPLUS_IDD}'")
    sys.exit(1)

try:
    from eppy.modeleditor import IDF
except ImportError as e:
    print(f"[FAIL] eppy not importable: {e}")
    sys.exit(1)

try:
    from eSim_bem_utils.commercial_integration import (
        classify_tag2, inject_mixed_use, assert_wiring, _get_zone_name,
        _PRE_V242_FIELD_NAMES, TAG2_OFFICE, TAG2_RETAIL, TAG2_HOTEL_GUESTROOM,
    )
except ImportError as e:
    print(f"[FAIL] cannot import eSim_bem_utils.commercial_integration: {e}")
    sys.exit(1)

IDF.setiddname(EPLUS_IDD)
print(f"[setup] EPLUS_IDD={EPLUS_IDD}")
print(f"[setup] source IDF={IDF_V242}")

# Tag-2 field on a SPACE object -- VERIFIED EMPIRICALLY against the real IDF (2026-07-28,
# manager check on the cluster copy of TallBuilding_..._Z6_v242.idf, L13682):
#   Space,
#     Basement_Corridor,     !- Name
#     Basement_Corridor ZN,  !- Zone Name
#     autocalculate,         !- Ceiling Height {m}
#     autocalculate,         !- Volume {m3}
#     ,                      !- Floor Area {m2}
#     ,                      !- Space Type      <- EMPTY in this stock
#     ,                      !- Tag 1
#     Corridor;              !- Tag 2           <- the Tag-2 string lives HERE
# -> eppy attribute `Tag_2`. "Space Type" is blank throughout, and the Space `Name` carries a
# floor-prefixed variant (Basement_Corridor), NOT the exact-match Tag-2 token -- so both would
# silently census every Space as "unknown". `Tag_2` first, the rest kept only as fallbacks.
_SPACE_TAG2_FIELDS = ("Tag_2", "Space_Type_Name", "Space_Type", "Name")


def _get_space_tag2(space_obj):
    for f in _SPACE_TAG2_FIELDS:
        v = getattr(space_obj, f, "")
        if v:
            return str(v).strip()
    return ""


def _schedule_by_name(idf, name):
    for obj in idf.idfobjects.get("SCHEDULE:COMPACT", []):
        if getattr(obj, "Name", "") == name:
            return obj
    return None


def _schedule_profile(sch_obj):
    """Flatten a Schedule:Compact object to its ordered numeric fraction values, skipping the
    non-numeric control fields (Through:/For:/Until: strings) and the class name + Name."""
    vals = []
    for v in list(sch_obj.obj)[2:]:
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            continue
    return vals


def _representative_baseline_name(source_idf, tag2_set):
    """Representative Number_of_People_Schedule_Name among source PEOPLE objects whose Tag-2
    falls in tag2_set (i.e. the schedule the injection is REPLACING for that channel)."""
    names = []
    for obj in source_idf.idfobjects.get("PEOPLE", []):
        tag2 = getattr(obj, "Space_Type_Name", "") or _get_zone_name(obj)
        if str(tag2).strip() in tag2_set:
            nm = getattr(obj, "Number_of_People_Schedule_Name", "")
            if nm:
                names.append(nm)
    if not names:
        return None, 0, 0
    c = Counter(names)
    top_name, _ = c.most_common(1)[0]
    return top_name, len(names), len(c)


# ---------------------------------------------------------------------------
# Block 2 -- Tag-2 census on the SOURCE (non-injected) v242 IDF
# ---------------------------------------------------------------------------
source_idf = None
try:
    source_idf = IDF(IDF_V242)
    counts = Counter()
    unknown_tags = Counter()
    for sp in source_idf.idfobjects.get("SPACE", []):
        tag2 = _get_space_tag2(sp)
        ch = classify_tag2(tag2)
        counts[ch] += 1
        if ch == "unknown":
            unknown_tags[tag2] += 1

    agg = {
        "residential": counts["residential"] + counts["residential_common"],
        "office": counts["office"] + counts["office_support"],
        "retail": counts["retail"],
        "hotel": counts["hotel"] + counts["hotel_support"],
        "service_mep": counts["service_mep"],
    }
    total = sum(counts.values())
    detail = (f"observed residential={agg['residential']} office={agg['office']} "
              f"retail={agg['retail']} hotel={agg['hotel']} service_mep={agg['service_mep']} "
              f"total={total} unknown={counts['unknown']} | expected {EXPECTED_CENSUS}")
    report("PASS", "Tag-2 census", detail)

    if counts["unknown"] > 0:
        top10 = list(unknown_tags.most_common(10))
        report("WARN", "Tag-2 unknown tags", f"{counts['unknown']} unknown Spaces; distinct(<=10)={top10}")
except Exception as e:
    report("FAIL", "Tag-2 census", f"exception: {e}")

# ---------------------------------------------------------------------------
# Block 2b -- load-object Tag-2 RECOVERY census (diagnostic, non-blocking)
#
# inject_mixed_use() L373 does NOT read the Space object's Tag_2 field: it recovers Tag-2 off
# each load object as `getattr(obj, "Space_Type_Name", "") or _get_zone_name(obj)`. PEOPLE has
# no Space_Type_Name attribute, so in practice the zone/space/zonelist reference is what gets
# exact-matched by classify_tag2(). In this stock that reference is a ZoneList name (e.g.
# PEOPLE "Corridor People" -> "Corridor"), which HAPPENS to equal the Tag-2 token -- but that
# equality is an empirical property of the DOE prototype, not a guarantee. This block measures
# it so that a 0-injection outcome downstream is immediately diagnosable instead of mysterious.
# ---------------------------------------------------------------------------
if source_idf is not None:
    try:
        rec = Counter()
        unresolved = Counter()
        for obj in source_idf.idfobjects.get("PEOPLE", []):
            tag2 = getattr(obj, "Space_Type_Name", "") or _get_zone_name(obj)  # module's own logic
            ch = classify_tag2(tag2)
            rec[ch] += 1
            if ch == "unknown":
                unresolved[str(tag2).strip()] += 1
        n_people = sum(rec.values())
        detail = (f"{n_people} PEOPLE objs -> " + " ".join(f"{k}={v}" for k, v in sorted(rec.items()))
                  + f" | unresolved(<=10)={list(unresolved.most_common(10))}")
        status = "PASS" if (rec["office"] + rec["retail"] + rec["hotel"]) > 0 else "FAIL"
        report(status, "Tag-2 recovery on PEOPLE (module logic)", detail)
    except Exception as e:
        report("FAIL", "Tag-2 recovery on PEOPLE (module logic)", f"exception: {e}")

# ---------------------------------------------------------------------------
# Block 3 -- injection via inject_mixed_use()
# ---------------------------------------------------------------------------
inj_result = None
try:
    inj_result = inject_mixed_use(IDF_V242, OUT_IDF, CHANNELS, BUILDING_META, verbose=True)
    n_off = inj_result["office"]["n_spaces"]
    n_ret = inj_result["retail"]["n_spaces"]
    n_hot = inj_result["hotel"]["n_spaces"]
    fb = inj_result["fallback"]
    amb = sorted(set(inj_result["ambiguous"]))
    detail = (f"n_spaces office={n_off} retail={n_ret} hotel={n_hot}; fallback={fb}; "
              f"ambiguous(<=10)={amb[:10]} (n_ambiguous_distinct={len(amb)})")
    if fb:
        report("FAIL", "Injection fallback", detail + " -- silent fallback is the W5/P4 trap")
    else:
        report("PASS", "Injection", detail)
except Exception as e:
    report("FAIL", "Injection", f"exception: {e}")

# ---------------------------------------------------------------------------
# Block 4 -- W2: field-wiring assertion on the re-opened injected IDF
# ---------------------------------------------------------------------------
idf_inj = None
if inj_result is not None and not inj_result.get("fallback"):
    try:
        idf_inj = IDF(OUT_IDF)
        expected_channels = {f"ch{i}": nm for i, nm in enumerate(inj_result["modulated_schedule_names"])}
        try:
            w2 = assert_wiring(idf_inj, expected_channels, verbose=True)
            report("PASS", "W2 field-wiring", f"{w2['n_audited']} PEOPLE objects audited, 0 violations")
        except AssertionError as e:
            report("FAIL", "W2 field-wiring", str(e)[:400])
    except Exception as e:
        report("FAIL", "W2 field-wiring", f"exception reopening/auditing injected IDF: {e}")
else:
    report("FAIL", "W2 field-wiring", "skipped -- no injected IDF available (prior block failed)")

# ---------------------------------------------------------------------------
# Block 4b -- W7: LIGHTS / ELECTRICEQUIPMENT wiring coverage.
# Neither W2 nor W3 looks at anything but PEOPLE, so before 2026-07-28 the commercial
# LIGHTS/ELECTRICEQUIPMENT wiring sat under NO gate at all. Verified independently of the
# module's own counters: re-classify every load object off the saved IDF and require that each
# one landing on a commercial channel actually references the MXU schedule for that channel.
# ---------------------------------------------------------------------------
if idf_inj is not None:
    try:
        # schedule names are built as MXU_Office_People_{tag} / MXU_Retail_People_{tag} /
        # MXU_Hotel_GuestRoom_{tag} (commercial_integration.py L344-363) -> match on the channel token
        by_ch = {}
        for nm in inj_result["modulated_schedule_names"]:
            for c in ("office", "retail", "hotel"):
                if nm.lower().startswith(f"mxu_{c}_"):
                    by_ch[c] = nm
        miss, cov = [], {}
        for obj_class in ("LIGHTS", "ELECTRICEQUIPMENT"):
            for obj in idf_inj.idfobjects.get(obj_class, []):
                tag2 = getattr(obj, "Space_Type_Name", "") or _get_zone_name(obj)
                ch = classify_tag2(tag2)
                if ch not in ("office", "retail", "hotel") or ch not in by_ch:
                    continue
                got = getattr(obj, "Schedule_Name", "")
                key = f"{ch}/{obj_class}"
                cov[key] = cov.get(key, 0) + 1
                if got != by_ch[ch]:
                    miss.append(f"{obj_class}:{tag2}->'{got}' (want '{by_ch[ch]}')")
        detail = f"coverage={dict(sorted(cov.items()))}; mismatches={len(miss)}"
        if miss:
            report("FAIL", "W7 LIGHTS/EQUIP wiring", detail + f"; first(<=5)={miss[:5]}")
        elif not cov:
            report("FAIL", "W7 LIGHTS/EQUIP wiring",
                   "0 commercial LIGHTS/ELECTRICEQUIPMENT objects reached -- nothing was wired")
        else:
            report("PASS", "W7 LIGHTS/EQUIP wiring", detail)
    except Exception as e:
        report("FAIL", "W7 LIGHTS/EQUIP wiring", f"exception: {e}")
else:
    report("FAIL", "W7 LIGHTS/EQUIP wiring", "skipped -- injected IDF unavailable")

# ---------------------------------------------------------------------------
# Block 5 -- W3: modulated series != baseline (implemented here, NOT in commercial_integration.py
# -- its assert_wiring() docstring advertises W3 but only W2 is coded there; see module L436-461).
# ---------------------------------------------------------------------------
CHANNEL_TAG2_SOURCE = {"office": TAG2_OFFICE, "retail": TAG2_RETAIL, "hotel": TAG2_HOTEL_GUESTROOM}
tag_label = BUILDING_META.get("scenario_label", "scenario")
EXPECTED_SCH_NAMES = {
    "office": f"MXU_Office_People_{tag_label}",
    "retail": f"MXU_Retail_People_{tag_label}",
    "hotel": f"MXU_Hotel_GuestRoom_{tag_label}",
}

if idf_inj is not None and source_idf is not None and inj_result is not None:
    for channel, sch_name in EXPECTED_SCH_NAMES.items():
        if sch_name not in inj_result.get("modulated_schedule_names", []):
            continue  # channel fell back or wasn't requested; not a W3 case
        try:
            inj_sch = _schedule_by_name(idf_inj, sch_name)
            if inj_sch is None:
                report("FAIL", f"W3 {channel}", f"injected schedule '{sch_name}' not found in output IDF")
                continue
            profile_inj = _schedule_profile(inj_sch)

            # Baseline candidate 1: a Schedule:Compact of the SAME name already in the source
            # (would mean it isn't actually new -- essentially impossible given the MXU_ prefix,
            # but checked first per the "same name" wording of the spec).
            base_sch = _schedule_by_name(source_idf, sch_name)
            base_label = f"same-name '{sch_name}'"
            if base_sch is None:
                # Baseline candidate 2: the schedule this channel's Spaces referenced BEFORE
                # injection (the baseline it replaces).
                base_name, n_matched, n_distinct = _representative_baseline_name(
                    source_idf, CHANNEL_TAG2_SOURCE[channel])
                if base_name is None:
                    report("PASS", f"W3 {channel}", f"NEW schedule '{sch_name}', no baseline found in "
                                                       f"source (no matching Tag-2 PEOPLE objects) -- legitimate NEW case")
                    continue
                base_sch = _schedule_by_name(source_idf, base_name)
                base_label = f"replaced baseline '{base_name}' ({n_matched} source PEOPLE objs, {n_distinct} distinct names)"
                if base_sch is None:
                    report("WARN", f"W3 {channel}", f"baseline ref '{base_name}' is not a Schedule:Compact "
                                                       f"(cannot flatten-compare) -- treating as NEW, PASS")
                    continue

            profile_base = _schedule_profile(base_sch)
            n = min(len(profile_base), len(profile_inj))
            if n == 0:
                report("FAIL", f"W3 {channel}", f"empty numeric profile (base={len(profile_base)}, "
                                                   f"inj={len(profile_inj)}) vs {base_label}")
                continue
            n_diff = sum(1 for a, b in zip(profile_base[:n], profile_inj[:n]) if abs(a - b) > 1e-6)
            max_delta = max((abs(a - b) for a, b in zip(profile_base[:n], profile_inj[:n])), default=0.0)
            len_note = "" if len(profile_base) == len(profile_inj) else \
                f" (length mismatch base={len(profile_base)} inj={len(profile_inj)}, compared first {n})"
            detail = f"{n_diff}/{n} slots differ, max|delta|={max_delta:.4f} vs {base_label}{len_note}"
            if n_diff == 0:
                report("FAIL", f"W3 {channel}", detail + " -- 0 slots differ (Leg-2 byte-identical bug pattern)")
            else:
                report("PASS", f"W3 {channel}", detail)
        except Exception as e:
            report("FAIL", f"W3 {channel}", f"exception: {e}")
else:
    report("FAIL", "W3", "skipped -- injected/source IDF unavailable (prior block failed)")

# ---------------------------------------------------------------------------
# Block 6 -- W6: pre-v24.2 field-name usage on touched objects (non-blocking, bonus)
# ---------------------------------------------------------------------------
if idf_inj is not None:
    try:
        n_hits = 0
        for obj_class in ("PEOPLE", "LIGHTS", "ELECTRICEQUIPMENT"):
            for obj in idf_inj.idfobjects.get(obj_class, []):
                for f in _PRE_V242_FIELD_NAMES:
                    if getattr(obj, f, ""):
                        n_hits += 1
        status = "PASS" if n_hits == 0 else "WARN"
        report(status, "W6 pre-v242 fields", f"{n_hits} occurrences of {sorted(_PRE_V242_FIELD_NAMES)} (expected 0)")
    except Exception as e:
        report("FAIL", "W6 pre-v242 fields", f"exception: {e}")
else:
    report("WARN", "W6 pre-v242 fields", "skipped -- injected IDF unavailable")

# ---------------------------------------------------------------------------
# Block 7 -- final scorecard
# ---------------------------------------------------------------------------
print("\n=== AUDIT-W SCORECARD ===")
nP = nW = nF = 0
for r in RESULTS:
    print(f"[{r['status']}] {r['check']} -- {r['detail']}")
    if r["status"] == "PASS":
        nP += 1
    elif r["status"] == "WARN":
        nW += 1
    else:
        nF += 1

print(f"\nTOTAL: {nP}P / {nW}W / {nF}F")
sys.exit(1 if nF > 0 else 0)
