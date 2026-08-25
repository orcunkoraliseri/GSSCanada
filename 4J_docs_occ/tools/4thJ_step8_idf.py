#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4J Step 8, work item 8.1 --- build the archetype IDFs.

Reads `outputs_step8/archetype_parameters_{es,uk,it}.csv` (written by
`4thJ_step8_tabula.py`) and writes one EnergyPlus IDF per resolved archetype.

The geometry, the construction build-up and the archetype selection are NOT
choices made here.  They were ruled by the author on 2026-08-24 as
`D-S8-2` items 1, 3 and 4:

  1(a)  One equivalent box per archetype.  Footprint A_plate = A_C_Ref /
        n_Storey, height H = n_Storey * h_room.  The TOTAL glazed area is
        split EQUALLY over the four vertical facades.  Where the total-window
        column is zero the sum of the compass columns is used instead.
        AMENDED by `D-S8-3`(a), 2026-08-25 --- see below.
  3(a)  Two-layer equivalent per opaque surface: one mass-less resistive layer
        reproducing the TABULA U, plus one capacitive layer sized so that the
        areal heat capacity reproduces c_m = 45 Wh/(m^2.K).  No external
        construction assembly is invented.
  4a(a) Prefer the `.Gen.` row wherever one exists.
  4b(a) A merged-period row represents EVERY period its code declares.
        4a is applied AFTER 4b.

`D-S8-3`(a), ruled 2026-08-25, amends the OTHER half of 1(a) --- the fixed
1 : 1.5 aspect ratio --- and nothing else.  `FINDING 110` measured that the
1 : 1.5 box does not reproduce TABULA's published wall area, and that what it
loses is country-correlated: H_transmission box/TABULA had median 0.956 on
`uk` against 0.765 on `it`, a 19 pp spread sitting inside the LOCO channel.
The aspect ratio is therefore no longer a constant.  It is SOLVED per
archetype so that the box's GROSS vertical envelope reproduces TABULA's own:

      2 (W + D) H  =  A_Wall_TABULA + A_Window        (gross facade)
              W D  =  A_plate                          (1(a), untouched)

so that W and D are the roots of  t^2 - S t + A_plate = 0  with
S = (A_Wall_TABULA + A_Window) / (2 H).  The target is the GROSS facade, not
A_Wall alone, because the builder carves the glazing out of the facade
(`a_wall_box = 2(W+D)H - win_total`); targeting the gross is what makes the
modelled OPAQUE wall equal TABULA's published A_Wall exactly.  W >= D always,
so the long axis stays East-West as 1(a) has it.

TWO fallbacks to 1 : 1.5, both recorded per archetype in the manifest
(`aspect_source`, `aspect_fallback`), because a fallback nobody can count is
a fallback nobody will believe:

  `no_real_root`          S < 2 sqrt(A_plate): the published wall area is
                          below the minimum perimeter for that footprint, so
                          no real box exists.  26 of 88, and NOT random ---
                          19 of the 26 are terraced houses, whose TABULA wall
                          area excludes the party walls a free-standing box
                          has to have.
  `glazing_does_not_fit`  a real root exists, but the box is so elongated
                          that a quarter of the glazing will not fit on the
                          narrow facade (WWR > 0.94).  12 of 88, 10 of them
                          Italian.  1(a)'s EQUAL four-facade split is a strict
                          invariant and outranks the aspect ratio, so the
                          aspect gives way, not the split.

`FINDING 117` records what this leaves behind: the country-correlated residue
falls from 19.1 pp to 6.1 pp, it does NOT reach zero, and 17 of the 38
fallbacks are Italian.  Read it before quoting the medians.

Section 6 item 2 (ruled 2026-08-21) gives ONE THERMAL ZONE per archetype.

Everything TABULA does not give us is declared in ASSUMED[] and written into
the provenance file.  An assumed value that is not written down becomes a fact
the moment someone reads the code.
"""

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import os
import re
import sys

# --------------------------------------------------------------------------
# Ruled constants.  None of these is a free parameter of this script.
# --------------------------------------------------------------------------
ASPECT = 1.5                      # 1(a) as first ruled; D-S8-3(a) keeps it
                                  # ONLY as the documented fallback shape
WWR_CAP = 0.94                    # a facade cannot hold more glass than wall
C_M_WH_M2K = 45.0                 # 3(a): TABULA EU boundary condition, c_m
C_M_J_M2K = C_M_WH_M2K * 3600.0   # = 162 000 J/(m^2.K) of A_C_Ref
N_FACADES = 4                     # 1(a): equal split over four vertical faces

# EN ISO 6946 surface resistances.  TABULA's U is a thermal transmittance in
# the ISO 6946 sense and therefore INCLUDES the films; an EnergyPlus
# Construction's resistance EXCLUDES them and E+ adds them at run time.  The
# layer resistance is therefore 1/U - Rsi - Rse.  See FINDING 111 for the size
# of the error the other convention would have introduced, and for why it is
# not a wash: it is correlated with construction period.
R_SI = {"wall": 0.13, "roof": 0.10, "floor": 0.17}
R_SE = {"wall": 0.04, "roof": 0.04, "floor": 0.00}  # floor is ground-coupled

# Capacitive layer.  Thickness and specific heat are FIXED so that the only
# free quantity is density, which then carries the areal capacity exactly.
MASS_D = 0.05          # m
MASS_K = 5.00          # W/(m.K)  -> R = 0.01 m2K/W, subtracted from the
                       #             resistive layer so the total U is exact.
                       # 5.0 rather than 1.0 because ES.ME.SFH.01 has
                       # U_Roof = 5.56 + 0.15: at k = 1.0 the mass layer
                       # alone (R = 0.05) exceeded the whole available
                       # resistance (1/U - Rsi - Rse = 0.035) and the
                       # construction had to be clamped. Conductivity does
                       # not enter the areal capacity, so this changes the
                       # U of no archetype and the c_m of none.
MASS_CP = 1000.0       # J/(kg.K)

# --------------------------------------------------------------------------
# Values TABULA does not give us in the 44 columns we hold.
# Every one is UNIFORM across all archetypes and all three folds, deliberately:
# a constant cannot manufacture a country-correlated difference, and this study
# is LOCO.  Cf. FINDING 53, FINDING 60, FINDING 109.
# --------------------------------------------------------------------------
ASSUMED = [
    ("SHGC", 0.70, "-",
     "No g-value column exists in archetype_parameters_*.csv. Uniform across "
     "all archetypes so it cannot become a country effect."),
    ("infiltration_ach", 0.50, "1/h",
     "n_air_use is not among the 44 columns. Uniform, same reason."),
    ("heating_setpoint", 20.0, "degC",
     "The EU.* boundary-condition set point. Consistent with FINDING 57 "
     "(the archetypes carry EU, not national, boundary conditions)."),
    ("cooling", None, "-",
     "None. TABULA residential has no cooling demand; the model is "
     "heating-only (ThermostatSetpoint:SingleHeating)."),
    ("ground_temp", None, "-",
     "Not set here, and item 8.2 closing does NOT change that. The EPW named "
     "in weather_manifest.csv supplies the site, but EnergyPlus does not read "
     "the EPW header's ground temperatures unless a Site:GroundTemperature "
     "object points at them, and none is written. Still an E+ default."),
    ("window_frame", None, "-",
     "No frame fraction column. U_Window_1 is applied to the whole opening "
     "via WindowMaterial:SimpleGlazingSystem, whose U-factor is an NFRC "
     "whole-window value and therefore already film-inclusive."),
]

EPLUS_VERSION = "24.2"

# --------------------------------------------------------------------------
# Loading and archetype resolution
# --------------------------------------------------------------------------

# The period token sits inside Code_Building, not in a column of its own:
#   GB.ENG.AB.04-08.ApartmentBuildings.SyAv.005  -> class AB,      periods 04..08
#   IT.MidClim.MFH-AB.01-03.Gen.ReEx.001         -> class MFH-AB,  periods 01..03
#   ES.ME.AB.01.Gen.ReEx.001                     -> class AB,      period  01
CODE_RE = re.compile(r"\.(?P<cls>SFH|TH|MFH|AB|MFH-AB|SFH-TH)\."
                     r"(?P<a>\d{2})(?:-(?P<b>\d{2}))?\.")

SINGLE_CLASSES = ("SFH", "TH", "MFH", "AB")


def load_rows(base, fold):
    """Read one fold's parameter table.  The file carries three leading `#`
    comment lines, which are length-1 rows and are dropped here."""
    path = os.path.join(base, "archetype_parameters_%s.csv" % fold)
    raw = [r for r in csv.reader(io.open(path, encoding="utf-8")) if len(r) > 1]
    hdr = raw[0]
    return [dict(zip(hdr, r)) for r in raw[1:]], hdr


def parse_code(code):
    m = CODE_RE.search(code)
    if not m:
        return None
    a = int(m.group("a"))
    b = int(m.group("b") or m.group("a"))
    return m.group("cls"), a, b


def resolve(rows, fold):
    """Apply 4b(a) then 4a(a) and return {(class, period_code): row}.

    Returns (resolved, report).  `report` records every decision the two rules
    actually made, so the selftest can check them one by one rather than
    checking only the count.
    """
    country_token = {"es": "ES", "uk": "GB", "it": "IT"}[fold]
    periods = sorted({r["Code_ConstructionYearClass"] for r in rows})
    classes = sorted({r["Code_BuildingSizeClass"] for r in rows})

    cand = collections.defaultdict(list)
    combined = []          # rows whose class token names TWO classes
    unparsed = []
    expanded = 0
    for r in rows:
        p = parse_code(r["Code_Building"])
        if p is None:
            unparsed.append(r["Code_Building"])
            continue
        cls, a, b = p
        if cls not in SINGLE_CLASSES:
            # A row labelled `MFH-AB` is a row for the COMBINED class, not a
            # row for MFH and not a row for AB.  It is excluded here, and the
            # exclusion is reported rather than performed silently, because
            # 4a(a) cannot arbitrate it: both candidates carry `.Gen.`.
            combined.append(r["Code_Building"])
            continue
        if b > a:
            expanded += 1
        for k in range(a, b + 1):
            key = (cls, "%s.%02d" % (country_token, k))
            if key[1] in periods:            # 4b never invents a period
                cand[key].append(r)

    resolved = {}
    picks = []
    for key in sorted(cand):
        cands = cand[key]
        gens = [c for c in cands if ".Gen." in c["Code_Building"]]
        chosen = (gens or cands)[0]
        picks.append({
            "cell": "%s|%s" % key,
            "n_candidates": len(cands),
            "chosen": chosen["Code_Building"],
            "rule": "4a:Gen" if gens else "4a:no-Gen-exists",
            "rejected": [c["Code_Building"] for c in cands
                         if c["Code_Building"] != chosen["Code_Building"]],
        })
        resolved[key] = chosen

    report = {
        "fold": fold,
        "rows_in_table": len(rows),
        "classes": classes,
        "periods": periods,
        "cells_in_matrix": len(classes) * len(periods),
        "cells_resolved": len(resolved),
        "rows_expanded_by_4b": expanded,
        "combined_class_rows_excluded": sorted(combined),
        "unparsed": sorted(unparsed),
        "picks": picks,
        "missing": sorted("%s|%s" % (c, p) for c in classes for p in periods
                          if (c, p) not in resolved),
    }
    return resolved, report


# --------------------------------------------------------------------------
# Derivation
# --------------------------------------------------------------------------

def f(row, key):
    v = row.get(key, "")
    if v is None or v == "":
        return 0.0
    return float(v)


def derive(row):
    """Everything the IDF needs, derived from the ruled geometry."""
    a_ref = f(row, "A_C_Ref")
    n_st = f(row, "n_Storey")
    h_room = f(row, "h_room")
    if a_ref <= 0 or n_st <= 0 or h_room <= 0:
        raise ValueError("degenerate geometry in %s" % row["Code_Building"])

    a_plate = a_ref / n_st                      # 1(a), untouched
    height = n_st * h_room                      # 1(a), untouched
    # width/depth are no longer constants of the model.  D-S8-3(a) solves them
    # below, once TABULA's wall area and the glazed area are both known.

    # 1(a): total glazed area, with the compass-sum fallback.
    win_total = f(row, "A_Window_1") + f(row, "A_Window_2")
    compass = sum(f(row, "A_Window_" + d)
                  for d in ("East", "South", "West", "North", "Horizontal"))
    win_source = "A_Window_1+2"
    if win_total <= 0.0:
        win_total = compass
        win_source = "compass_sum"          # repairs ES.ME.MFH.05
    win_face = win_total / N_FACADES

    # Area-weighted opaque U per surface class, from TABULA's own areas.
    def wu(pairs):
        num = sum(a * u for a, u in pairs if a > 0)
        den = sum(a for a, u in pairs if a > 0)
        return (num / den if den > 0 else 0.0), den

    u_roof, a_roof_t = wu([(f(row, "A_Roof_1"), f(row, "U_Roof_1")),
                           (f(row, "A_Roof_2"), f(row, "U_Roof_2"))])
    u_wall, a_wall_t = wu([(f(row, "A_Wall_1"), f(row, "U_Wall_1")),
                           (f(row, "A_Wall_2"), f(row, "U_Wall_2")),
                           (f(row, "A_Wall_3"), f(row, "U_Wall_3"))])
    u_floor, a_floor_t = wu([(f(row, "A_Floor_1"), f(row, "U_Floor_1")),
                             (f(row, "A_Floor_2"), f(row, "U_Floor_2"))])
    u_win, a_win_t = wu([(f(row, "A_Window_1"), f(row, "U_Window_1")),
                         (f(row, "A_Window_2"), f(row, "U_Window_2"))])
    if u_win <= 0:
        u_win = f(row, "U_Window_1") or f(row, "U_Window_2")

    # ------------------------------------------------------------------
    # D-S8-3(a): the aspect ratio is an OUTPUT, solved from TABULA's own wall
    # area.  See the module docstring for the algebra and for both fallbacks.
    # Nothing here touches A_plate, the height, or the equal glazing split.
    # ------------------------------------------------------------------
    def fallback_box():
        return math.sqrt(ASPECT * a_plate), math.sqrt(a_plate / ASPECT)

    a_wall_gross_target = a_wall_t + win_total
    s_half = a_wall_gross_target / (2.0 * height)      # = W + D
    disc = s_half * s_half - 4.0 * a_plate
    if a_wall_gross_target <= 0.0 or disc < 0.0:
        # No real box has this footprint and that little wall.
        width, depth = fallback_box()
        aspect_source = "fallback"
        aspect_fallback = ("no_wall_area" if a_wall_gross_target <= 0.0
                           else "no_real_root")
    else:
        root = math.sqrt(disc)
        width = (s_half + root) / 2.0               # long axis, East-West
        depth = (s_half - root) / 2.0
        aspect_source, aspect_fallback = "tabula", ""
        # 1(a)'s equal split is a strict invariant and outranks the aspect.
        if depth <= 0.0 or (win_face / (depth * height)) > WWR_CAP:
            width, depth = fallback_box()
            aspect_source = "fallback"
            aspect_fallback = "glazing_does_not_fit"

    # The box's own envelope.
    a_wall_box = 2.0 * (width + depth) * height - win_total
    a_roof_box = a_plate
    a_floor_box = a_plate
    a_opaque_box = a_wall_box + a_roof_box + a_floor_box

    # 3(a): total capacity is c_m * A_C_Ref, distributed uniformly per m^2 of
    # the modelled OPAQUE envelope so that the total is conserved exactly.
    c_total_j = C_M_J_M2K * a_ref
    c_areal_j = c_total_j / a_opaque_box if a_opaque_box > 0 else 0.0
    mass_rho = c_areal_j / (MASS_D * MASS_CP)

    # H_transmission, as published vs as modelled.  The box conserves floor
    # area and volume, not envelope area, so these differ and the difference
    # is the honest cost of 1(a).
    dub = f(row, "delta_U_ThermalBridging_Original")
    h_tab = (a_roof_t * (u_roof + dub) + a_wall_t * (u_wall + dub) +
             a_floor_t * (u_floor + dub) + a_win_t * u_win)
    h_box = (a_roof_box * (u_roof + dub) + a_wall_box * (u_wall + dub) +
             a_floor_box * (u_floor + dub) + win_total * u_win)

    return {
        "code": row["Code_Building"],
        "variant": row["Code_BuildingVariant"],
        "country": row["Code_Country"],
        "cls": row["Code_BuildingSizeClass"],
        "period": row["Code_ConstructionYearClass"],
        "bc": row["Code_BoundaryCond"],
        "a_ref": a_ref, "n_storey": n_st, "h_room": h_room,
        "a_plate": a_plate, "width": width, "depth": depth, "height": height,
        "aspect": (width / depth) if depth > 0 else 0.0,
        "aspect_source": aspect_source, "aspect_fallback": aspect_fallback,
        "a_wall_gross_target": a_wall_gross_target,
        "win_total": win_total, "win_face": win_face, "win_source": win_source,
        "u_roof": u_roof, "u_wall": u_wall, "u_floor": u_floor, "u_win": u_win,
        "dub": dub,
        "a_roof_tabula": a_roof_t, "a_wall_tabula": a_wall_t,
        "a_floor_tabula": a_floor_t, "a_win_tabula": a_win_t,
        "a_roof_box": a_roof_box, "a_wall_box": a_wall_box,
        "a_floor_box": a_floor_box, "a_opaque_box": a_opaque_box,
        "c_total_j": c_total_j, "c_areal_j": c_areal_j, "mass_rho": mass_rho,
        "h_transmission_tabula": h_tab, "h_transmission_box": h_box,
        "phi_int": f(row, "phi_int"),
        "q_w_nd": f(row, "q_w_nd"),
    }


# --------------------------------------------------------------------------
# IDF emission
# --------------------------------------------------------------------------

def opaque_construction(name, u_total, kind, rho):
    """3(a): one mass-less resistive layer + one capacitive layer.

    The resistive layer carries  1/U - Rsi - Rse - R_mass,  so that the
    ISO 6946 transmittance of the finished construction is U exactly.
    """
    r_layers = 1.0 / u_total - R_SI[kind] - R_SE[kind]
    r_resist = r_layers - (MASS_D / MASS_K)
    if r_resist <= 0.001:
        # Only reachable for an absurdly high U; recorded, never silently
        # clamped without saying so in the manifest.
        r_resist = 0.001
        clamped = True
    else:
        clamped = False
    txt = []
    txt.append("Material:NoMass,\n"
               "  %s_R,                    !- Name\n"
               "  Rough,                   !- Roughness\n"
               "  %.6f,                    !- Thermal Resistance {m2-K/W}\n"
               "  0.90,                    !- Thermal Absorptance\n"
               "  0.60,                    !- Solar Absorptance\n"
               "  0.60;                    !- Visible Absorptance\n"
               % (name, r_resist))
    txt.append("Material,\n"
               "  %s_C,                    !- Name\n"
               "  Rough,                   !- Roughness\n"
               "  %.4f,                    !- Thickness {m}\n"
               "  %.4f,                    !- Conductivity {W/m-K}\n"
               "  %.4f,                    !- Density {kg/m3}\n"
               "  %.1f;                    !- Specific Heat {J/kg-K}\n"
               % (name, MASS_D, MASS_K, rho, MASS_CP))
    txt.append("Construction,\n"
               "  %s,                      !- Name\n"
               "  %s_R,                    !- Outside Layer\n"
               "  %s_C;                    !- Layer 2\n" % (name, name, name))
    return "\n".join(txt), r_resist, clamped


def wall_vertices(x0, y0, x1, y1, h):
    """Upper-left corner, counter-clockwise, world coordinates."""
    return [(x0, y0, h), (x0, y0, 0.0), (x1, y1, 0.0), (x1, y1, h)]


def inset_window(v, frac):
    """A window centred on a wall, covering `frac` of it, same plane."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz), (dx, dy, dz) = v
    s = math.sqrt(frac)
    m = (1.0 - s) / 2.0
    def lerp(p, q, t):
        return tuple(p[i] + (q[i] - p[i]) * t for i in range(3))
    top_l = lerp((ax, ay, az), (dx, dy, dz), m)
    top_r = lerp((ax, ay, az), (dx, dy, dz), 1.0 - m)
    bot_l = lerp((bx, by, bz), (cx, cy, cz), m)
    bot_r = lerp((bx, by, bz), (cx, cy, cz), 1.0 - m)
    zt = az - (az - bz) * m
    zb = bz + (az - bz) * m
    return [(top_l[0], top_l[1], zt), (bot_l[0], bot_l[1], zb),
            (bot_r[0], bot_r[1], zb), (top_r[0], top_r[1], zt)]


def vtx(name, verts):
    out = ["  %d,                       !- Number of Vertices" % len(verts)]
    for i, (x, y, z) in enumerate(verts):
        end = ";" if i == len(verts) - 1 else ","
        out.append("  %.4f, %.4f, %.4f%s" % (x, y, z, end))
    return "\n".join(out)


def build_idf(d):
    W, D, H = d["width"], d["depth"], d["height"]
    zone = "Z_DWELLING"
    name = d["code"].replace(".", "_")

    c_wall, r_wall, clamp_w = opaque_construction("C_WALL", d["u_wall"] + d["dub"], "wall", d["mass_rho"])
    c_roof, r_roof, clamp_r = opaque_construction("C_ROOF", d["u_roof"] + d["dub"], "roof", d["mass_rho"])
    c_floor, r_floor, clamp_f = opaque_construction("C_FLOOR", d["u_floor"] + d["dub"], "floor", d["mass_rho"])

    # Window-to-wall fraction, identical on every facade by 1(a).
    gross = {"North": W * H, "South": W * H, "East": D * H, "West": D * H}
    fr = {k: (d["win_face"] / v if v > 0 else 0.0) for k, v in gross.items()}
    over = {k: v for k, v in fr.items() if v >= 0.95}

    L = []
    L.append("!- 4J Step 8 item 8.1 --- archetype IDF, generated by tools/4thJ_step8_idf.py")
    L.append("!- Archetype   : %s" % d["code"])
    L.append("!- Fold        : %s   class %s   period %s   boundary %s"
             % (d["country"], d["cls"], d["period"], d["bc"]))
    L.append("!- Geometry    : D-S8-2 item 1(a) + D-S8-3(a), equal-facade box, long axis E-W")
    # D-S8-3(a).  A fallback box must NEVER read as if it reproduced TABULA's
    # wall area -- it is the one thing this header exists to make unmistakable.
    if d["aspect_source"] == "tabula":
        L.append("!- Aspect      : W/D = %.4f  (D-S8-3a, SOLVED: this box reproduces "
                 "A_Wall_TABULA exactly)" % (W / D))
    else:
        L.append("!- Aspect      : W/D = %.4f  (D-S8-3a FALLBACK: %s --- this box does "
                 "NOT reproduce A_Wall_TABULA)"
                 % (W / D if D > 0 else 0.0, d["aspect_fallback"]))
    L.append("!- Layers      : D-S8-2 item 3(a), two-layer equivalent, c_m = 45 Wh/(m2.K)")
    L.append("!- Zoning      : section 6 item 2, ONE thermal zone, no internal partition")
    L.append("!- NOTE        : no Site:Location by design. The EPW supplies the site --- "
             "item 8.2 is CLOSED (D-S8-4), see weather_manifest.csv.")
    L.append("")
    L.append("Version, %s;" % EPLUS_VERSION)
    L.append("")
    L.append("Building,\n  %s,\n  0.0,\n  City,\n  0.04,\n  0.4,\n  FullExterior,\n  25,\n  6;" % name)
    L.append("")
    L.append("Timestep, 6;")
    L.append("GlobalGeometryRules, UpperLeftCorner, CounterClockWise, World;")
    L.append("SimulationControl, No, No, No, No, Yes, No, 1;")
    L.append("ShadowCalculation, PolygonClipping, Periodic, 20;")
    L.append("")
    L.append("ScheduleTypeLimits, Frac, 0.0, 1.0, Continuous;")
    L.append("ScheduleTypeLimits, Temp, -60.0, 200.0, Continuous, Temperature;")
    L.append("ScheduleTypeLimits, CtrlType, 0, 4, Discrete, Control;")
    L.append("Schedule:Constant, SCH_ALWAYS_ON, Frac, 1.0;")
    L.append("Schedule:Constant, SCH_HEAT_SP, Temp, %.1f;" % ASSUMED[2][1])
    L.append("")
    L.append(c_wall); L.append(c_roof); L.append(c_floor)
    L.append("WindowMaterial:SimpleGlazingSystem,\n"
             "  G_WINDOW,                !- Name\n"
             "  %.4f,                    !- U-Factor {W/m2-K}\n"
             "  %.4f;                    !- Solar Heat Gain Coefficient\n"
             % (d["u_win"], ASSUMED[0][1]))
    L.append("Construction, C_WINDOW, G_WINDOW;")
    L.append("")
    L.append("Zone,\n"
             "  %s,                                    !- Name\n"
             "  0.0,                                   !- Direction of Relative North\n"
             "  0.0, 0.0, 0.0,                         !- X, Y, Z Origin\n"
             "  ,                                      !- Type\n"
             "  1,                                     !- Multiplier\n"
             "  ,                                      !- Ceiling Height\n"
             "  ,                                      !- Volume\n"
             "  ,                                      !- Floor Area\n"
             "  ,                                      !- Inside Convection Algorithm\n"
             "  ,                                      !- Outside Convection Algorithm\n"
             "  Yes;                                   !- Part of Total Floor Area" % zone)
    L.append("")

    # x runs East, y runs North.  The 1.5 side lies along x by construction.
    faces = [
        ("SOUTH", (0.0, 0.0), (W, 0.0)),
        ("EAST",  (W, 0.0),   (W, D)),
        ("NORTH", (W, D),     (0.0, D)),
        ("WEST",  (0.0, D),   (0.0, 0.0)),
    ]
    for fname, (x0, y0), (x1, y1) in faces:
        v = wall_vertices(x0, y0, x1, y1, H)
        L.append("BuildingSurface:Detailed,\n"
                 "  W_%s,                    !- Name\n"
                 "  Wall,                    !- Surface Type\n"
                 "  C_WALL,                  !- Construction Name\n"
                 "  %s,                      !- Zone Name\n"
                 "  ,                        !- Space Name\n"
                 "  Outdoors,                !- Outside Boundary Condition\n"
                 "  ,                        !- Outside Boundary Condition Object\n"
                 "  SunExposed,              !- Sun Exposure\n"
                 "  WindExposed,             !- Wind Exposure\n"
                 "  ,                        !- View Factor to Ground\n"
                 "%s" % (fname, zone, vtx("W_" + fname, v)))
        if d["win_face"] > 0.0:
            wv = inset_window(v, min(fr[fname.capitalize()] if fname.capitalize() in fr else 0.0, 0.94))
            L.append("FenestrationSurface:Detailed,\n"
                     "  F_%s,                    !- Name\n"
                     "  Window,                  !- Surface Type\n"
                     "  C_WINDOW,                !- Construction Name\n"
                     "  W_%s,                    !- Building Surface Name\n"
                     "  ,                        !- Outside Boundary Condition Object\n"
                     "  ,                        !- View Factor to Ground\n"
                     "  ,                        !- Frame and Divider Name\n"
                     "  1,                       !- Multiplier\n"
                     "%s" % (fname, fname, vtx("F_" + fname, wv)))

    L.append("BuildingSurface:Detailed,\n"
             "  S_ROOF,                  !- Name\n"
             "  Roof,                    !- Surface Type\n"
             "  C_ROOF,                  !- Construction Name\n"
             "  %s,                      !- Zone Name\n"
             "  ,                        !- Space Name\n"
             "  Outdoors,                !- Outside Boundary Condition\n"
             "  ,                        !- Outside Boundary Condition Object\n"
             "  SunExposed,              !- Sun Exposure\n"
             "  WindExposed,             !- Wind Exposure\n"
             "  ,                        !- View Factor to Ground\n"
             "%s" % (zone, vtx("S_ROOF", [(0.0, D, H), (0.0, 0.0, H),
                                          (W, 0.0, H), (W, D, H)])))
    L.append("BuildingSurface:Detailed,\n"
             "  S_FLOOR,                 !- Name\n"
             "  Floor,                   !- Surface Type\n"
             "  C_FLOOR,                 !- Construction Name\n"
             "  %s,                      !- Zone Name\n"
             "  ,                        !- Space Name\n"
             "  Ground,                  !- Outside Boundary Condition\n"
             "  ,                        !- Outside Boundary Condition Object\n"
             "  NoSun,                   !- Sun Exposure\n"
             "  NoWind,                  !- Wind Exposure\n"
             "  ,                        !- View Factor to Ground\n"
             "%s" % (zone, vtx("S_FLOOR", [(0.0, 0.0, 0.0), (0.0, D, 0.0),
                                           (W, D, 0.0), (W, 0.0, 0.0)])))
    L.append("")
    # Internal gains.  phi_int is per m^2 of A_C_Ref, and the zone floor is
    # A_plate, so the zone-level watt density is scaled to keep the TOTAL
    # right: item 8.5 replaces SCH_ALWAYS_ON with the Step 7 schedule and
    # applies the f sensitivity of D-S8-2 item 5.
    w_total = d["phi_int"] * d["a_ref"]
    L.append("OtherEquipment,\n"
             "  E_PHI_INT,               !- Name\n"
             "  None,                    !- Fuel Type\n"
             "  %s,                      !- Zone Name\n"
             "  SCH_ALWAYS_ON,           !- Schedule Name\n"
             "  EquipmentLevel,          !- Design Level Calculation Method\n"
             "  %.4f,                    !- Design Level {W}\n"
             "  ,                        !- Power per Floor Area\n"
             "  ,                        !- Power per Person\n"
             "  0.0,                     !- Fraction Latent\n"
             "  0.0,                     !- Fraction Radiant\n"
             "  0.0;                     !- Fraction Lost\n" % (zone, w_total))
    L.append("ZoneInfiltration:DesignFlowRate,\n"
             "  I_ZONE,                  !- Name\n"
             "  %s,                      !- Zone Name\n"
             "  SCH_ALWAYS_ON,           !- Schedule Name\n"
             "  AirChanges/Hour,         !- Design Flow Rate Calculation Method\n"
             "  ,                        !- Design Flow Rate\n"
             "  ,                        !- Flow per Zone Floor Area\n"
             "  ,                        !- Flow per Exterior Surface Area\n"
             "  %.4f,                    !- Air Changes per Hour\n"
             "  1.0, 0.0, 0.0, 0.0;\n" % (zone, ASSUMED[1][1]))
    L.append("ThermostatSetpoint:SingleHeating, T_SP, SCH_HEAT_SP;")
    L.append("ZoneControl:Thermostat,\n  T_CTRL,\n  %s,\n  T_TYPE,\n"
             "  ThermostatSetpoint:SingleHeating,\n  T_SP;" % zone)
    L.append("Schedule:Constant, T_TYPE, CtrlType, 1;")
    L.append("ZoneHVAC:IdealLoadsAirSystem,\n"
             "  IDEAL,                                 !- Name\n"
             "  ,                                      !- Availability Schedule Name\n"
             "  NODE_SUPPLY,                           !- Zone Supply Air Node Name\n"
             "  ,                                      !- Zone Exhaust Air Node Name\n"
             "  ,                                      !- System Inlet Air Node Name\n"
             "  50.0,                                  !- Maximum Heating Supply Air Temperature\n"
             "  13.0,                                  !- Minimum Cooling Supply Air Temperature\n"
             "  0.0156,                                !- Maximum Heating Supply Air Humidity Ratio\n"
             "  0.0077,                                !- Minimum Cooling Supply Air Humidity Ratio\n"
             "  NoLimit,                               !- Heating Limit\n"
             "  ,                                      !- Maximum Heating Air Flow Rate\n"
             "  ,                                      !- Maximum Sensible Heating Capacity\n"
             "  NoLimit,                               !- Cooling Limit\n"
             "  ,                                      !- Maximum Cooling Air Flow Rate\n"
             "  ,                                      !- Maximum Total Cooling Capacity\n"
             "  ,                                      !- Heating Availability Schedule Name\n"
             "  ,                                      !- Cooling Availability Schedule Name\n"
             "  ConstantSensibleHeatRatio,             !- Dehumidification Control Type\n"
             "  0.7,                                   !- Cooling Sensible Heat Ratio\n"
             "  None,                                  !- Humidification Control Type\n"
             "  ,                                      !- Design Specification Outdoor Air Object Name\n"
             "  ,                                      !- Outdoor Air Inlet Node Name\n"
             "  None,                                  !- Demand Controlled Ventilation Type\n"
             "  NoEconomizer,                          !- Outdoor Air Economizer Type\n"
             "  None,                                  !- Heat Recovery Type\n"
             "  0.70,                                  !- Sensible Heat Recovery Effectiveness\n"
             "  0.65;                                  !- Latent Heat Recovery Effectiveness")
    L.append("ZoneHVAC:EquipmentList,\n  EQLIST,\n  SequentialLoad,\n"
             "  ZoneHVAC:IdealLoadsAirSystem,\n  IDEAL,\n  1,\n  1,\n  ,\n  ;")
    L.append("ZoneHVAC:EquipmentConnections,\n  %s,\n  EQLIST,\n  NODELIST_IN,\n"
             "  ,\n  NODE_ZONE,\n  NODE_RETURN;" % zone)
    L.append("NodeList, NODELIST_IN, NODE_SUPPLY;")
    L.append("")
    L.append("RunPeriod,\n"
             "  ANNUAL,                  !- Name\n"
             "  1, 1, ,                  !- Begin month, day, year\n"
             "  12, 31, ,                !- End month, day, year\n"
             "  Sunday,                  !- Day of Week for Start Day\n"
             "  No, No, No, Yes, Yes;    !- Holidays, DST, rain, snow\n"
             "!- The RunPeriod is a CALENDAR, not a weather choice.\n"
             "!- The EPW supplies the weather and the site: item 8.2 is closed under\n"
             "!- D-S8-4 on a TMYx.2009-2023 basis, one station per fold, and the file\n"
             "!- for this fold is named in outputs_step8/weather_manifest.csv.")
    L.append("")
    L.append("Output:Variable, *, Zone Ideal Loads Supply Air Total Heating Energy, Hourly;")
    L.append("Output:Variable, *, Zone Mean Air Temperature, Hourly;")
    L.append("Output:Variable, *, Zone Ideal Loads Zone Total Heating Energy, Monthly;")
    L.append("OutputControl:Table:Style, CommaAndHTML;")
    L.append("Output:Table:SummaryReports, AllSummary;")
    L.append("")
    meta = {"clamped": [k for k, v in
                        (("wall", clamp_w), ("roof", clamp_r), ("floor", clamp_f)) if v],
            "r_resist": {"wall": r_wall, "roof": r_roof, "floor": r_floor},
            "wwr": fr, "wwr_over_limit": over}
    return "\n".join(L) + "\n", meta


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base", help="outputs_step8 directory")
    ap.add_argument("--out", default=None, help="default <base>/archetypes")
    args = ap.parse_args()
    base = args.base
    out = args.out or os.path.join(base, "archetypes")
    if not os.path.isdir(out):
        os.makedirs(out)

    manifest = []
    reports = []
    for fold in ("es", "uk", "it"):
        rows, _ = load_rows(base, fold)
        resolved, rep = resolve(rows, fold)
        reports.append(rep)
        print("%s | rows %-3d | matrix %-3d | resolved %-3d | 4b expansions %d "
              "| combined-class rows excluded %d"
              % (fold, rep["rows_in_table"], rep["cells_in_matrix"],
                 rep["cells_resolved"], rep["rows_expanded_by_4b"],
                 len(rep["combined_class_rows_excluded"])))
        if rep["missing"]:
            print("   !! MISSING CELLS:", rep["missing"])
        for (cls, per), row in sorted(resolved.items()):
            d = derive(row)
            # The cell a row was selected FOR is not always the period the row
            # declares for itself: 4b(a) expands merged spans. Record both.
            d["row_period"] = d["period"]
            d["cell_period"] = per
            d["expanded_by_4b"] = "yes" if per != d["row_period"] else ""
            idf, meta = build_idf(d)
            fn = "%s_%s_%s.idf" % (fold, cls, per.replace(".", ""))
            p = os.path.join(out, fn)
            io.open(p, "w", encoding="utf-8", newline="\n").write(idf)
            d["idf"] = fn
            d["idf_md5"] = hashlib.md5(idf.encode("utf-8")).hexdigest()
            d["clamped"] = ";".join(meta["clamped"])
            d["wwr_max"] = max(meta["wwr"].values()) if meta["wwr"] else 0.0
            d["wwr_over_limit"] = ";".join(sorted(meta["wwr_over_limit"]))
            d["fold"] = fold
            manifest.append(d)

    cols = ["fold", "cls", "cell_period", "row_period", "expanded_by_4b",
            "code", "idf", "idf_md5",
            "a_ref", "n_storey", "h_room", "a_plate", "width", "depth", "height",
            "aspect", "aspect_source", "aspect_fallback", "a_wall_gross_target",
            "win_total", "win_face", "win_source", "wwr_max", "wwr_over_limit",
            "u_wall", "u_roof", "u_floor", "u_win", "dub",
            "a_wall_tabula", "a_roof_tabula", "a_floor_tabula", "a_win_tabula",
            "a_wall_box", "a_roof_box", "a_floor_box", "a_opaque_box",
            "c_total_j", "c_areal_j", "mass_rho",
            "h_transmission_tabula", "h_transmission_box",
            "phi_int", "q_w_nd", "clamped"]
    mp = os.path.join(base, "archetype_idf_manifest.csv")
    with io.open(mp, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for d in manifest:
            w.writerow([d.get(c, "") for c in cols])

    rp = os.path.join(base, "archetype_selection_report.json")
    io.open(rp, "w", encoding="utf-8").write(
        json.dumps({"rulings": "D-S8-2 items 1(a) 3(a) 4a(a) 4b(a), 2026-08-24; "
                                "D-S8-3(a) aspect from A_Wall_TABULA, 2026-08-25",
                    "assumed": [{"name": a, "value": v, "unit": u, "why": w}
                                for a, v, u, w in ASSUMED],
                    "eplus_version": EPLUS_VERSION,
                    "folds": reports}, indent=2))

    print("\n%d archetype IDFs written to %s" % (len(manifest), out))
    print("manifest: %s" % mp)
    print("selection report: %s" % rp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
