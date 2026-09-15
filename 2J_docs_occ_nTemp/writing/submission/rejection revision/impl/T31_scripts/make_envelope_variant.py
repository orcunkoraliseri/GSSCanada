#!/usr/bin/env python3
"""
make_envelope_variant.py -- T31 WP7 step 3 envelope-variant builder.

Reads the SingleD source IDF (DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf)
and a JSON of target envelope parameters, writes a variant IDF plus a JSON
changelog of every field actually changed (object, field, old, new, line).
Any parameter whose JSON value is null (or key absent) is left COMPLETELY
UNTOUCHED -- no arithmetic, no rewrite, so a JSON of all-null values (see
envelope_current.json) reproduces the source IDF byte-for-byte except this
tool never rewrites comments either. This is the E0 identity guarantee.

Design (fixed in 2026-09-15_T31_wp7_existing_stock_envelope.md, "Design"
section -- do not deviate without the manager):
  - Wall, ceiling and optional foundation insulation: the insulation
    material's THICKNESS is changed at FIXED conductivity (never touched)
    so that the ASSEMBLY RSI (that layer's own material R, plus every
    other layer in the same Construction, plus standard air-film
    resistances -- see FILM_* constants below, computed and written down,
    not sourced from any survey) equals the target.
  - Window U-factor / SHGC: WindowMaterial:SimpleGlazingSystem fields on
    the material actually referenced by a real Window object in the IDF
    (see FINDING below -- this is NOT the material whose name suggests
    it, "NBC936 Z6 Window Glass").
  - Air-tightness: every AirflowNetwork:MultiZone:Surface:EffectiveLeakageArea
    object whose name starts with "ZoneLeak_" is scaled by one factor k
    (flow is linear in ELA). "AtticVent" / "CrawlVent" are excluded on
    purpose -- Design section: "attic and crawl vents left unchanged"
    (they vent the unconditioned attic/crawl to outdoors; they are not
    part of the conditioned house's own envelope leakage -- see the E2
    ACH50 write-up in the task doc's Verified section for why).
  - Geometry, HVAC, schedules, weather, and every other object are never
    touched -- this script only ever rewrites the exact numeric field(s)
    named above, in place, preserving every other character of the file.

FINDING (T31 phase A, recorded in the task doc under Decisions): the IDF
defines a construction+material pair named "NBC936_Z6_Window" /
"NBC936 Z6 Window Glass" (U=1.6 W/m2-K, SHGC=0.4), but grep confirms NO
Window object in the file references that construction -- every real
Window object uses construction "Exterior Window", whose one layer is
material "Glass" (WindowMaterial:SimpleGlazingSystem, U=1.590008,
SHGC=0.3344). "NBC936_Z6_Window"/"NBC936 Z6 Window Glass" is an orphaned
object the model never uses. This script therefore ALWAYS edits the
"Glass" material for window_u/window_shgc, never the orphaned one, and
never "fixes" the orphan (out of scope -- a model choice, not a bug this
task is allowed to touch).

Usage:
    python make_envelope_variant.py --source SOURCE.idf --targets targets.json \
        --out-idf VARIANT.idf --out-log changelog.json

Standard library only (re, json, argparse, math) -- runs under any
Python 3, local or the Speed step4 env.
"""
import argparse
import json
import math
import re
import sys

# ---------------------------------------------------------------------------
# Fixed model facts (T31 Decisions; from T27 Q3 + this task's own IDF reads).
# Material names as they appear in the IDF's own "!- Name" field.
# ---------------------------------------------------------------------------
WALL_INSULATION_MATERIAL = "NBC936 Z6 Wall Insulation"
WALL_OTHER_LAYERS = ["1IN Stucco", "8IN CONCRETE HW", "1/2IN Gypsum"]

ROOF_INSULATION_MATERIAL = "NBC936 Z6 Roof Insulation"
ROOF_OTHER_LAYERS = ["1/2IN Gypsum"]

FOUNDATION_WALL_INSULATION_MATERIAL = "NBC936 Z6 Foundation Insulation"
FOUNDATION_WALL_OTHER_LAYERS = ["8IN CONCRETE HW", "1/2IN Gypsum"]
SLAB_INSULATION_MATERIAL = "NBC936 Z6 Slab Insulation"
SLAB_OTHER_LAYERS = ["HW CONCRETE", "CP02 CARPET PAD"]

# The window material ACTUALLY referenced by real Window objects (see
# FINDING above) -- NOT "NBC936 Z6 Window Glass", which is orphaned.
WINDOW_MATERIAL = "Glass"

# ZoneLeak_* effective-leakage-area objects that make up the house's own
# envelope (conditioned-zone boundary). AtticVent / CrawlVent are the
# attic/crawl-to-outdoors ventilation paths and are excluded by design.
ZONE_LEAK_NAMES = [
    "ZoneLeak_LongWall",
    "ZoneLeak_ShortWall",
    "ZoneLeak_Ceiling",
    "ZoneLeak_Floor",
    "ZoneLeak_NonGarageWall",
]
# How many real surfaces reference each leakage object in this IDF (from
# grepping AirflowNetwork:MultiZone:Surface -- T31 Verified). Needed only
# for the ACH50 report, not for the k-scaling itself (k applies per-object
# regardless of how many surfaces share it).
ZONE_LEAK_SURFACE_COUNTS = {
    "ZoneLeak_LongWall": 4,
    "ZoneLeak_ShortWall": 4,
    "ZoneLeak_Ceiling": 1,
    "ZoneLeak_Floor": 1,
    "ZoneLeak_NonGarageWall": 1,
}
CONDITIONED_ZONE_NAME = "living_unit1"
RHO_AIR = 1.204  # kg/m3, per task doc

# Standard ASHRAE-Fundamentals "still air + standard wind" film
# resistances (m2-K/W), used ONLY as an arithmetic bookkeeping convention
# to report/derive assembly RSI -- these are generic physics constants,
# not a chosen envelope value, and are NOT sourced from dr_2J-09.
FILM_WALL = 0.15    # vertical surface: interior 0.12 + exterior 0.03
FILM_CEILING = 0.14  # heat-flow-up: interior 0.11 + exterior/attic-side 0.03
FILM_FOUNDATION = 0.0  # ground-coupled: no air-film convention applied (documented Decision)

NAME_LINE_RE = re.compile(r'^(?P<ws>\s*)(?P<name>[^,!]+?),(?P<rest>\s*!-\s*Name\s*)$')
NUMERIC_FIELD_RE = re.compile(r'^(?P<ws>\s*)(?P<num>[+-]?[0-9][0-9.eE+-]*)(?P<rest>\s*[,;].*)$')


class IdfError(Exception):
    pass


def load_idf(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.readlines()


def find_named_object(lines, name, start=0):
    """Return the index of the '<name>,   !- Name' line for an exact,
    unique object name. Raises if not found or found more than once."""
    hits = []
    for i in range(start, len(lines)):
        m = NAME_LINE_RE.match(lines[i])
        if m and m.group("name").strip() == name:
            hits.append(i)
    if not hits:
        raise IdfError(f"object named {name!r} not found (no '!- Name' line matches)")
    if len(hits) > 1:
        raise IdfError(f"object named {name!r} is not unique ({len(hits)} '!- Name' lines match)")
    return hits[0]


def find_field_by_comment(lines, start_idx, comment_substr, max_span=20):
    """Starting just after an object's Name line, scan forward (bounded)
    for the field whose trailing '!- ...' comment contains comment_substr
    (case-insensitive). Stops at the next blank line or next object Name
    line, whichever comes first, to avoid bleeding into a following
    object."""
    for i in range(start_idx + 1, min(start_idx + 1 + max_span, len(lines))):
        line = lines[i]
        if line.strip() == "":
            break
        if NAME_LINE_RE.match(line):
            break
        if "!-" in line:
            comment = line.split("!-", 1)[1]
            if comment_substr.lower() in comment.lower():
                return i
    raise IdfError(f"field with comment containing {comment_substr!r} not found within "
                    f"{max_span} lines of {lines[start_idx].strip()!r}")


def get_numeric_value(lines, idx):
    m = NUMERIC_FIELD_RE.match(lines[idx])
    if not m:
        raise IdfError(f"line {idx+1} is not a simple numeric field: {lines[idx]!r}")
    return float(m.group("num"))


def set_numeric_value(lines, idx, new_value, changelog, obj_label, field_label):
    old_line = lines[idx]
    m = NUMERIC_FIELD_RE.match(old_line)
    if not m:
        raise IdfError(f"line {idx+1} is not a simple numeric field: {old_line!r}")
    old_value = float(m.group("num"))
    new_str = repr(float(new_value))
    # NUMERIC_FIELD_RE's 'rest' group excludes the trailing line ending ('.'
    # does not match '\n'), so it must be re-appended explicitly here or the
    # rewritten line silently swallows its own newline (found + fixed in
    # T31 phase A local testing -- see task doc Decisions).
    line_ending = ""
    if old_line.endswith("\r\n"):
        line_ending = "\r\n"
    elif old_line.endswith("\n"):
        line_ending = "\n"
    rest = m.group("rest")
    if line_ending and rest.endswith(line_ending):
        rest = rest[: -len(line_ending)]
    new_line = f"{m.group('ws')}{new_str}{rest}{line_ending}"
    lines[idx] = new_line
    changelog.append({
        "object": obj_label,
        "field": field_label,
        "line_1based": idx + 1,
        "old_value": old_value,
        "new_value": float(new_value),
    })


def material_thickness_conductivity(lines, material_name):
    name_idx = find_named_object(lines, material_name)
    thick_idx = find_field_by_comment(lines, name_idx, "Thickness")
    cond_idx = find_field_by_comment(lines, name_idx, "Conductivity")
    return name_idx, thick_idx, cond_idx, get_numeric_value(lines, thick_idx), get_numeric_value(lines, cond_idx)


def layer_r_from_material(lines, material_name):
    """R-value (m2-K/W) of one opaque material layer. Handles both
    Material (thickness/conductivity) and Material:NoMass (direct
    Thermal Resistance) -- this IDF's insulation/structural layers are
    all Material, but WALL_OTHER_LAYERS/etc. are read generically."""
    name_idx = find_named_object(lines, material_name)
    obj_type_line = None
    for j in range(name_idx, -1, -1):
        s = lines[j].strip()
        if s.startswith("Material,") or s.startswith("Material:NoMass,") or s.startswith("Material:AirGap,"):
            obj_type_line = s
            break
    if obj_type_line is None:
        raise IdfError(f"could not find object-type line above {material_name!r}")
    if obj_type_line.startswith("Material:NoMass,") or obj_type_line.startswith("Material:AirGap,"):
        r_idx = find_field_by_comment(lines, name_idx, "Thermal Resistance")
        return get_numeric_value(lines, r_idx)
    else:
        thick_idx = find_field_by_comment(lines, name_idx, "Thickness")
        cond_idx = find_field_by_comment(lines, name_idx, "Conductivity")
        return get_numeric_value(lines, thick_idx) / get_numeric_value(lines, cond_idx)


def compute_current_ach50(lines):
    """Returns (ach50_house, ach50_all_incl_vents, ela_by_name, conditioned_volume).
    ach50_house uses ONLY the ZoneLeak_* objects (the house's own envelope
    -- T31 Decisions). ach50_all_incl_vents additionally includes AtticVent
    and CrawlVent, reported for transparency only, never used for k."""
    ela = {}
    cd = dpref = n = None
    for name in ZONE_LEAK_NAMES + ["AtticVent", "CrawlVent"]:
        idx = find_named_object(lines, name)
        ela_idx = find_field_by_comment(lines, idx, "Effective Leakage Area")
        cd_idx = find_field_by_comment(lines, idx, "Discharge Coefficient")
        dp_idx = find_field_by_comment(lines, idx, "Reference Pressure Difference")
        n_idx = find_field_by_comment(lines, idx, "Air Mass Flow Exponent")
        ela[name] = get_numeric_value(lines, ela_idx)
        this_cd = get_numeric_value(lines, cd_idx)
        this_dp = get_numeric_value(lines, dp_idx)
        this_n = get_numeric_value(lines, n_idx)
        if cd is None:
            cd, dpref, n = this_cd, this_dp, this_n
        elif (cd, dpref, n) != (this_cd, this_dp, this_n):
            raise IdfError(f"{name} has different Cd/dPref/n than the others -- "
                            f"formula assumed they are shared, re-check the IDF")

    v_ref = math.sqrt(2 * dpref / RHO_AIR)
    factor_50 = (50.0 / dpref) ** n

    def total_flow(names):
        total_ela = sum(ela[nm] * ZONE_LEAK_SURFACE_COUNTS.get(nm, 4 if nm in ("AtticVent", "CrawlVent") else 1)
                         for nm in names)
        return cd * total_ela * v_ref * factor_50, total_ela

    zone_idx = find_named_object(lines, CONDITIONED_ZONE_NAME)
    vol_idx = find_field_by_comment(lines, zone_idx, "Volume")
    conditioned_volume = get_numeric_value(lines, vol_idx)

    flow_house, tot_ela_house = total_flow(ZONE_LEAK_NAMES)
    flow_all, tot_ela_all = total_flow(ZONE_LEAK_NAMES + ["AtticVent", "CrawlVent"])
    ach50_house = flow_house * 3600.0 / conditioned_volume
    ach50_all = flow_all * 3600.0 / conditioned_volume
    return {
        "ach50_house_zoneleak_only": ach50_house,
        "ach50_all_incl_attic_crawl_vents": ach50_all,
        "flow_house_m3s_at_50Pa": flow_house,
        "total_ela_house_m2": tot_ela_house,
        "total_ela_all_m2": tot_ela_all,
        "conditioned_volume_m3": conditioned_volume,
        "cd": cd, "dPref": dpref, "n": n,
        "ela_by_name": ela,
    }


def apply_assembly_rsi_target(lines, insulation_material, other_layer_materials,
                               film_r, target_rsi, changelog, label):
    other_r = sum(layer_r_from_material(lines, m) for m in other_layer_materials)
    name_idx, thick_idx, cond_idx, cur_thick, conductivity = material_thickness_conductivity(lines, insulation_material)
    cur_ins_r = cur_thick / conductivity
    cur_assembly_rsi = other_r + cur_ins_r + film_r
    new_ins_r = target_rsi - other_r - film_r
    if new_ins_r <= 0:
        raise IdfError(f"{label}: target assembly RSI {target_rsi} is not achievable "
                        f"(other layers + film alone = {other_r + film_r:.4f} m2-K/W)")
    new_thick = new_ins_r * conductivity
    set_numeric_value(lines, thick_idx, new_thick, changelog,
                       obj_label=f"Material:{insulation_material}", field_label="Thickness")
    return {
        "label": label,
        "insulation_material": insulation_material,
        "other_layers_R": other_r,
        "film_R": film_r,
        "conductivity_fixed": conductivity,
        "current_assembly_rsi": cur_assembly_rsi,
        "current_insulation_thickness_m": cur_thick,
        "target_assembly_rsi": target_rsi,
        "new_insulation_thickness_m": new_thick,
    }


def build_variant(source_path, targets, out_idf_path, out_log_path):
    lines = load_idf(source_path)
    changelog = []
    report = {"label": targets.get("label", ""), "actions": []}

    ach50_info = compute_current_ach50(lines)
    report["current_ach50"] = ach50_info

    # --- Wall ---
    if targets.get("wall_rsi") is not None:
        report["actions"].append(apply_assembly_rsi_target(
            lines, WALL_INSULATION_MATERIAL, WALL_OTHER_LAYERS, FILM_WALL,
            float(targets["wall_rsi"]), changelog, "wall"))

    # --- Ceiling (shared construction w/ roof deck, see module docstring) ---
    if targets.get("ceiling_rsi") is not None:
        report["actions"].append(apply_assembly_rsi_target(
            lines, ROOF_INSULATION_MATERIAL, ROOF_OTHER_LAYERS, FILM_CEILING,
            float(targets["ceiling_rsi"]), changelog, "ceiling(=roof-deck, shared material)"))

    # --- Foundation (optional; only if dr_2J-09 gives a value) ---
    if targets.get("foundation_rsi") is not None:
        report["actions"].append(apply_assembly_rsi_target(
            lines, FOUNDATION_WALL_INSULATION_MATERIAL, FOUNDATION_WALL_OTHER_LAYERS, FILM_FOUNDATION,
            float(targets["foundation_rsi"]), changelog, "foundation_basement_wall"))
        report["actions"].append(apply_assembly_rsi_target(
            lines, SLAB_INSULATION_MATERIAL, SLAB_OTHER_LAYERS, FILM_FOUNDATION,
            float(targets["foundation_rsi"]), changelog, "foundation_slab"))

    # --- Window U / SHGC (the "Glass" material actually used, see FINDING) ---
    if targets.get("window_u") is not None or targets.get("window_shgc") is not None:
        name_idx = find_named_object(lines, WINDOW_MATERIAL)
        if targets.get("window_u") is not None:
            u_idx = find_field_by_comment(lines, name_idx, "U-Factor")
            set_numeric_value(lines, u_idx, float(targets["window_u"]), changelog,
                               obj_label=f"WindowMaterial:SimpleGlazingSystem:{WINDOW_MATERIAL}",
                               field_label="U-Factor")
        if targets.get("window_shgc") is not None:
            shgc_idx = find_field_by_comment(lines, name_idx, "Solar Heat Gain Coefficient")
            set_numeric_value(lines, shgc_idx, float(targets["window_shgc"]), changelog,
                               obj_label=f"WindowMaterial:SimpleGlazingSystem:{WINDOW_MATERIAL}",
                               field_label="Solar Heat Gain Coefficient")

    # --- Air-tightness: k on every ZoneLeak_* ELA ---
    k = targets.get("k")
    if k is None and targets.get("ach50") is not None:
        k = float(targets["ach50"]) / ach50_info["ach50_house_zoneleak_only"]
    if k is not None:
        k = float(k)
        for name in ZONE_LEAK_NAMES:
            name_idx = find_named_object(lines, name)
            ela_idx = find_field_by_comment(lines, name_idx, "Effective Leakage Area")
            cur_ela = get_numeric_value(lines, ela_idx)
            set_numeric_value(lines, ela_idx, cur_ela * k, changelog,
                               obj_label=f"AirflowNetwork:MultiZone:Surface:EffectiveLeakageArea:{name}",
                               field_label="Effective Leakage Area")
        report["actions"].append({
            "label": "airtightness",
            "k": k,
            "current_ach50_house": ach50_info["ach50_house_zoneleak_only"],
            "predicted_new_ach50_house": ach50_info["ach50_house_zoneleak_only"] * k,
        })

    report["changelog"] = changelog
    report["n_fields_changed"] = len(changelog)

    with open(out_idf_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)
    with open(out_log_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="source SingleD IDF")
    ap.add_argument("--targets", required=True, help="JSON of target envelope parameters")
    ap.add_argument("--out-idf", required=True, help="output variant IDF path")
    ap.add_argument("--out-log", required=True, help="output JSON changelog path")
    args = ap.parse_args()

    with open(args.targets, "r", encoding="utf-8") as f:
        targets = json.load(f)

    report = build_variant(args.source, targets, args.out_idf, args.out_log)
    print(f"[make_envelope_variant] label={report['label']!r} "
          f"fields_changed={report['n_fields_changed']} "
          f"current_ach50(house)={report['current_ach50']['ach50_house_zoneleak_only']:.6f}")
    for a in report["actions"]:
        print(f"  action: {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
