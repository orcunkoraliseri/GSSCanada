# -*- coding: utf-8 -*-
"""5J Step 9c: Model A IDF writer. Edits COPIES of the OpenUBEM district IDFs; never rebuilds them.

Task: Step9_docs/impl/2026-10-01_wp9c_idf_writer_TASK.md (with AMENDMENT 1: no window insertion; any window object
already in the base IDF is kept untouched, counted before and after).

Districts: ES-MAD-BERRUGUETE and IT-BOL-GALVANI2 only (UK licence: nothing else may be named here).

Sub-commands
  tables  --out-walls CSV --out-zones CSV [--district D]   geometry only, no EnergyPlus: wall table + zone map
  write   --district D --stem S --mode reproduce|default|occupancy --out IDF [--placement CSV] [--plant-equip ZONE FACTOR]
  placement --district D --stem S --presence CSV --appliance CSV --out CSV   (synthetic test placement, same for every flat)
  zonecheck --idf IDF                                       zone-map verdict of one IDF (used for the P3 planted fault)

Modes (every edit prints one `PATCH <name> OK ...` line; `write` re-reads the written file and checks each edit is present)
  reproduce : base IDF + only the extra Output:Variable / Output:Meter / table lines.
  default   : + cooling available with cooling setpoint 26 C (heating 20 C as simulated), OtherEquipment lump kept.
  occupancy : default, OtherEquipment lump (and its gain Schedule:File objects) removed, People + ElectricEquipment per flat
              (one flat = one zone) with Schedule:File, object text and split as the pilot (5thJ_idf_mz.py lines 443-475).
"""
import argparse
import csv
import importlib
import io
import math
import os
import re
import sys

sys.dont_write_bytecode = True
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_mz = importlib.import_module("5thJ_idf_mz")
OUTPUT_VARIABLES = list(_mz.OUTPUT_VARIABLES)
OUTPUT_METERS = list(_mz.OUTPUT_METERS)
COOL_SP_C, HEAT_SP_C, ACTIVITY_W = _mz.COOL_SP_C, _mz.HEAT_SP_C, _mz.ACTIVITY_W
_sched_file, _read_series = _mz._sched_file, _mz._read_series

EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
DISTRICTS = {"ES-MAD-BERRUGUETE": "es", "IT-BOL-GALVANI2": "it"}
VINTAGE = os.environ.get("MODELA_VINTAGE", "fix_2026-10-01")   # AMENDMENT 2: set MODELA_VINTAGE=win_2026-10-01 for the windowed base
# extra outputs asked by the task (no infiltration object exists: air change is a ZoneVentilation object)
EXTRA_VARIABLES = ["Zone Ventilation Sensible Heat Loss Energy", "Zone Ventilation Sensible Heat Gain Energy",
                   "Zone Other Equipment Electricity Energy"]   # last one: carries the 3 W/m2 lump in R1/D (decision, state file)
SIZE_MIN_W, SIZE_MIN_H = 0.5, 1.0     # D9-5 smallest eligible wall (kept for the wall table)
# Step 9i (additive): the models have no Lights object, so the meter InteriorLights:Electricity is "invalid / not found" in eplusout.err.
# Old behaviour (meter written) stays reachable: MODELA_LIGHTS_METER=1. Default: written only for the two old bases, not for any later base.
LIGHTS_METER = os.environ.get("MODELA_LIGHTS_METER", "1" if VINTAGE in ("fix_2026-10-01", "win_2026-10-01") else "0") == "1"
FAST_EDIT_DESC = "ShadowCalculation update frequency 1 -> 20 and SimulationControl zone/system/plant sizing Yes -> No"


class WriterError(RuntimeError):
    pass


def fen_info(objs):
    """Window objects of the base IDF: list of (name, area_m2 incl. multiplier). Fields: name,type,cons,bsurf,bcobj,vf,frame,mult,nverts,x,y,z..."""
    out = []
    for o in objs:
        if o["kw"].startswith("FENESTRATIONSURFACE"):
            f = o["fields"]
            c = f[9:]
            v = [(float(c[i]), float(c[i + 1]), float(c[i + 2])) for i in range(0, len(c) - 2, 3)]
            out.append((f[0], area3(v) * float(f[7] or 1)))
    return out


def read_windows_csv(district):
    p = "%s/%s_%s/windows.csv" % (EU11, district, VINTAGE)
    with io.open(p, encoding="utf-8", newline="") as fh:
        return {r["stem"]: r for r in csv.DictReader(fh)}


FLEET_ROOT = os.environ.get("MODELA_FLEET_ROOT")   # Step 9l (additive): Speed copy of the base, <root>/EU11_<D>_<vintage>/idfs/<stem>.idf


def idf_path(district, stem):
    if district not in DISTRICTS:
        raise WriterError("district %r not allowed" % district)
    if FLEET_ROOT:
        return "%s/EU11_%s_%s/idfs/%s.idf" % (FLEET_ROOT, district, VINTAGE, stem)
    return "%s/%s_%s/idfs/%s.idf" % (EU11, district, VINTAGE, stem)


def read_text(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# -------------------------------------------------------------------------------------------- IDF parsing
def objects(text):
    """List of dict(kw, start, end, fields). Object = lines from a non-indented keyword line to the line holding ';'."""
    out = []
    pos = 0
    cur = None
    for line in text.splitlines(True):
        code = line.split("!")[0]
        stripped = code.strip()
        if cur is None:
            if stripped and not line[0].isspace():
                cur = {"start": pos, "code": []}
            else:
                pos += len(line)
                continue
        cur["code"].append(code)
        if ";" in code:
            body = "".join(cur["code"])
            fields = [f.strip() for f in re.split(r"[,;]", body.strip().rstrip(";"))]
            out.append({"kw": fields[0].upper(), "start": cur["start"], "end": pos + len(line), "fields": fields[1:]})
            cur = None
        pos += len(line)
    return out


def eol_of(text):
    return "\r\n" if "\r\n" in text[:20000] else "\n"


def newell(v):
    sx = sy = sz = 0.0
    n = len(v)
    for i in range(n):
        x1, y1, z1 = v[i]
        x2, y2, z2 = v[(i + 1) % n]
        sx += y1 * z2 - z1 * y2
        sy += z1 * x2 - x1 * z2
        sz += x1 * y2 - y1 * x2
    return sx, sy, sz


def area3(v):
    sx, sy, sz = newell(v)
    return 0.5 * math.sqrt(sx * sx + sy * sy + sz * sz)


def surface_of(o):
    f = o["fields"]
    # fields: name,type,cons,zone,space,bc,bcobj,sun,wind,vf,nverts(autocalc or number),x,y,z...
    coords = f[11:]
    verts = [(float(coords[i]), float(coords[i + 1]), float(coords[i + 2])) for i in range(0, len(coords) - 2, 3)]
    return {"name": f[0], "type": f[1].lower(), "cons": f[2], "zone": f[3], "bc": f[5].lower(), "bcobj": f[6],
            "verts": verts}


def classify_wall(verts):
    """eligible_rectangle | too_small | triangle | other_shape (D9-5 wording; used for the wall table only)."""
    n = len(verts)
    if n == 3:
        return "triangle"
    if n != 4:
        return "other_shape"
    sx, sy, sz = newell(verts)
    nn = math.sqrt(sx * sx + sy * sy + sz * sz)
    if nn <= 0 or abs(sz) / nn > 1e-3:
        return "other_shape"                                   # not vertical
    e = [tuple(verts[(i + 1) % 4][k] - verts[i][k] for k in range(3)) for i in range(4)]
    ln = [math.sqrt(sum(c * c for c in x)) for x in e]
    tol = 0.02
    if any(abs(e[0][k] + e[2][k]) > tol for k in range(3)) or any(abs(e[1][k] + e[3][k]) > tol for k in range(3)):
        return "other_shape"                                   # not a parallelogram
    if ln[0] < 1e-6 or ln[1] < 1e-6:
        return "other_shape"
    cosang = sum(e[0][k] * e[1][k] for k in range(3)) / (ln[0] * ln[1])
    if abs(cosang) > 5e-3:
        return "other_shape"                                   # not a rectangle
    vert = [i for i in range(4) if math.hypot(e[i][0], e[i][1]) < 0.02 and abs(e[i][2]) > 0.5 * ln[i]]
    if not vert:
        return "other_shape"                                   # rectangle tilted inside its vertical plane
    h = ln[vert[0]]
    w = ln[(vert[0] + 1) % 4]
    return "too_small" if (w < SIZE_MIN_W or h < SIZE_MIN_H) else "eligible_rectangle"


# -------------------------------------------------------------------------------------------- zone map
FLAT = re.compile(r"^(?P<stem>.+)_F(?P<k>\d+)_dwelling_(?P<n>\d+)$")


def zone_map(text, stem, objs=None):
    """Return (rows, reason). rows: zone, floor_k, dwelling_n, floor_area_m2 (sum of Floor-type surfaces as simulated).
    reason is '' when every conditioned zone matches <stem>_F<k>_dwelling_<n>, else 'not_one_zone_per_dwelling'."""
    objs = objs if objs is not None else objects(text)
    zones = [o["fields"][0] for o in objs if o["kw"] == "ZONE"]
    cond = {o["fields"][0] for o in objs if o["kw"] == "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM"}
    floor_area = {}
    for o in objs:
        if o["kw"] == "BUILDINGSURFACE:DETAILED" and o["fields"][1].lower() == "floor":
            s = surface_of(o)
            floor_area[s["zone"]] = floor_area.get(s["zone"], 0.0) + area3(s["verts"])
    rows, bad = [], 0
    for z in zones:
        if z not in cond:
            continue
        m = FLAT.match(z)
        if m and m.group("stem") == stem:
            rows.append({"zone": z, "floor_k": int(m.group("k")), "dwelling_n": int(m.group("n")),
                         "floor_area_m2": round(floor_area.get(z, 0.0), 4)})
        else:
            bad += 1
    reason = "not_one_zone_per_dwelling" if (bad or not rows) else ""
    return rows, reason, len(zones), len(cond)


# -------------------------------------------------------------------------------------------- tables
def read_prepared(district):
    p = "%s/%s_%s/prepared_buildings.csv" % (EU11, district, VINTAGE)
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def cmd_tables(args):
    dists = [args.district] if args.district else list(DISTRICTS)
    wcols = ["district", "building_id", "stem", "archetype_id", "building_type", "geometry_outcome",
             "outdoor_eligible_rectangle", "outdoor_too_small", "outdoor_triangle", "outdoor_other_shape",
             "adiabatic_walls", "eligible_wall_area_m2", "existing_window_objects", "window_area_m2_idf", "window_m2_windows_csv", "window_area_diff_pct", "source_tree", "n_flats", "zone_map_reason"]
    zcols = ["district", "stem", "zone", "floor_k", "dwelling_n", "floor_area_m2"]
    tot = {}
    with io.open(args.out_walls, "w", encoding="utf-8", newline="") as fw, \
            io.open(args.out_zones, "w", encoding="utf-8", newline="") as fz:
        ww = csv.writer(fw, lineterminator="\n")
        wz = csv.writer(fz, lineterminator="\n")
        ww.writerow(wcols)
        wz.writerow(zcols)
        for d in dists:
            t = tot.setdefault(d, {"eligible_rectangle": 0, "too_small": 0, "triangle": 0, "other_shape": 0,
                                   "adiabatic": 0, "buildings": 0, "windows": 0, "flat_ok": 0, "left_out": 0})
            wcsv = read_windows_csv(d) if "win" in VINTAGE else {}
            for r in read_prepared(d):
                text = read_text(idf_path(d, r["stem"]))
                objs = objects(text)
                kinds = {"eligible_rectangle": 0, "too_small": 0, "triangle": 0, "other_shape": 0}
                adi = 0
                elig_area = 0.0
                for o in objs:
                    if o["kw"] != "BUILDINGSURFACE:DETAILED" or o["fields"][1].lower() != "wall":
                        continue
                    s = surface_of(o)
                    if s["bc"] == "adiabatic":
                        adi += 1
                    elif s["bc"] == "outdoors":
                        k = classify_wall(s["verts"])
                        kinds[k] += 1
                        if k == "eligible_rectangle":
                            elig_area += area3(s["verts"])
                fen = fen_info(objs)
                nwin = len(fen)
                warea = sum(a for _, a in fen)
                wc = wcsv.get(r["stem"])
                wcm = float(wc["window_m2"]) if wc and wc.get("window_m2") else None
                wdiff = ("%.4f" % (100.0 * (warea - wcm) / wcm)) if wcm else ""
                t["warea"] = t.get("warea", 0.0) + warea
                rows, reason, nz, nc = zone_map(text, r["stem"], objs)
                ww.writerow([d, r["building_id"], r["stem"], r["archetype_id"], r["building_type"], r["geometry_outcome"],
                             kinds["eligible_rectangle"], kinds["too_small"], kinds["triangle"], kinds["other_shape"],
                             adi, "%.3f" % elig_area, nwin, "%.4f" % warea,
                             "" if wcm is None else "%.4f" % wcm, wdiff, r.get("source_tree", ""), len(rows), reason])
                for z in rows:
                    wz.writerow([d, r["stem"], z["zone"], z["floor_k"], z["dwelling_n"], z["floor_area_m2"]])
                for k in kinds:
                    t[k] += kinds[k]
                t["adiabatic"] += adi
                t["buildings"] += 1
                t["windows"] += nwin
                t["flat_ok" if not reason else "left_out"] += 1
    for d, t in tot.items():
        print("TOTAL %s buildings=%d rectangles(eligible+too_small)=%d (eligible %d, too_small %d) triangles=%d other=%d "
              "adiabatic=%d existing_window_objects=%d window_area_idf=%.2f zone_map_pass=%d left_out=%d"
              % (d, t["buildings"], t["eligible_rectangle"] + t["too_small"], t["eligible_rectangle"], t["too_small"],
                 t["triangle"], t["other_shape"], t["adiabatic"], t["windows"], t.get("warea", 0.0), t["flat_ok"], t["left_out"]))


# -------------------------------------------------------------------------------------------- text builders
def _eqtext(zone, tag, lvl):
    # identical to 5thJ_idf_mz.py lines 468-473 (checked against the pilot source by `selftest`)
    return ("ElectricEquipment,\n  EQ_%s,  !- Name\n  %s,  !- Zone or ZoneList Name\n"
            "  %s_Appliance,  !- Schedule Name\n  EquipmentLevel,  !- Design Level Calculation Method\n"
            "  %.4f,  !- Design Level {W}\n  ,  !- Watts per Zone Floor Area\n  ,  !- Watts per Person\n"
            "  0.0,  !- Fraction Latent\n  1.0,  !- Fraction Radiant\n  0.0;  !- Fraction Lost\n"
            % (zone, zone, tag, lvl))


def _peopletext(zone, tag, npeople):
    # identical to 5thJ_idf_mz.py lines 457-464
    return ("People,\n  PE_%s,  !- Name\n  %s,  !- Zone or ZoneList Name\n"
            "  %s_Presence,  !- Number of People Schedule Name\n  People,  !- Number of People Calculation Method\n"
            "  %.6f,  !- Number of People\n  ,  !- People per Zone Floor Area\n"
            "  ,  !- Zone Floor Area per Person\n  0.3,  !- Fraction Radiant\n"
            "  ,  !- Sensible Heat Fraction\n  Activity_Level;  !- Activity Level Schedule Name\n"
            % (zone, zone, tag, npeople))


PILOT_FRAGMENTS = [
    "People,\\n  PE_%s,  !- Name\\n  %s,  !- Zone or ZoneList Name\\n",
    "  %s_Presence,  !- Number of People Schedule Name\\n  People,  !- Number of People Calculation Method\\n",
    "  %.6f,  !- Number of People\\n  ,  !- People per Zone Floor Area\\n",
    "  ,  !- Zone Floor Area per Person\\n  0.3,  !- Fraction Radiant\\n",
    "  ,  !- Sensible Heat Fraction\\n  Activity_Level;  !- Activity Level Schedule Name\\n",
    "ElectricEquipment,\\n  EQ_%s,  !- Name\\n  %s,  !- Zone or ZoneList Name\\n",
    "  %s_Appliance,  !- Schedule Name\\n  EquipmentLevel,  !- Design Level Calculation Method\\n",
    "  %.4f,  !- Design Level {W}\\n  ,  !- Watts per Zone Floor Area\\n  ,  !- Watts per Person\\n",
    "  0.0,  !- Fraction Latent\\n  1.0,  !- Fraction Radiant\\n  0.0;  !- Fraction Lost\\n",
    "Schedule:Constant, Activity_Level, , %d;",
]


def selftest():
    src = read_text(os.path.join(_HERE, "5thJ_idf_mz.py"))
    miss = [f for f in PILOT_FRAGMENTS if f not in src]
    if miss:
        raise WriterError("People/ElectricEquipment text differs from the pilot source: %r" % miss)
    # the writer's own functions must contain the same fragments (compare their output with the fragments)
    p = _peopletext("Z", "T", 1.5).replace("\n", "\\n")
    e = _eqtext("Z", "T", 2.0).replace("\n", "\\n")
    for f, got in ((PILOT_FRAGMENTS[0], p), (PILOT_FRAGMENTS[5], e)):
        if (f % ("Z", "Z")) not in got:
            raise WriterError("writer text differs from pilot fragment %r" % f)
    print("PATCH selftest OK %d People/ElectricEquipment text fragments found verbatim in 5thJ_idf_mz.py" % len(PILOT_FRAGMENTS))


# -------------------------------------------------------------------------------------------- the writer
def remove_objects(text, spans):
    for s, e in sorted(spans, reverse=True):
        # drop one trailing blank line as well
        tail = text[e:e + 4]
        if tail.startswith("\r\n"):
            e += 2
        elif tail.startswith("\n"):
            e += 1
        text = text[:s] + text[e:]
    return text


def read_placement(path, zones):
    with io.open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    by = {r["dwelling_zone"]: r for r in rows}
    if len(by) != len(rows):
        raise WriterError("placement has duplicate dwelling_zone")
    if set(by) != set(zones):
        raise WriterError("placement zones differ from the flat zones: only in placement %s, only in building %s"
                          % (sorted(set(by) - set(zones))[:3], sorted(set(zones) - set(by))[:3]))
    return by


def build(text, district, stem, mode, placement_path=None, plant_equip=None, plant_drop_window=False):
    """Return (new_text, patch_lines, expect). `expect` lists checks run on the re-read file."""
    if mode not in ("reproduce", "default", "occupancy"):
        raise WriterError("mode %r" % mode)
    eol = eol_of(text)
    lines, expect = [], []

    def say(name, msg):
        lines.append("PATCH %s OK %s" % (name, msg))
        print(lines[-1])

    objs = objects(text)
    rows, reason, nz, nc = zone_map(text, stem, objs)
    if reason:
        raise WriterError("building %s is left out of Model A: %s" % (stem, reason))
    zones = [r["zone"] for r in rows]
    nflat = len(zones)
    fen0 = fen_info(objs)
    win_before = len(fen0)
    area_before = sum(a for _, a in fen0)
    if plant_drop_window:
        # planted fault P2 (G-c2): remove the LARGEST window object of this building from the copy
        big = max(fen0, key=lambda x: x[1])
        hit = [o for o in objs if o["kw"].startswith("FENESTRATIONSURFACE") and o["fields"][0] == big[0]]
        if len(hit) != 1:
            raise WriterError("plant window: %d objects named %s" % (len(hit), big[0]))
        text = remove_objects(text, [(hit[0]["start"], hit[0]["end"])])
        objs = objects(text)
        win_before -= 1
        area_before -= big[1]
        say("PLANTED_window_removed", "window %s (%.3f m2) removed from this copy; windows %d -> %d, area %.3f -> %.3f m2"
            % (big[0], big[1], len(fen0), win_before, sum(a for _, a in fen0), area_before))
    say("windows_untouched", "no window code in this writer; window objects in base copy = %d, area %.4f m2 (checked equal after)"
        % (win_before, area_before))
    expect.append(("count_kw", "FENESTRATIONSURFACE:DETAILED", win_before))
    expect.append(("win_area", area_before, None))

    # ---- planted fault P1 (reproduce): one zone's OtherEquipment W/m2 x factor ---------------------------------
    if plant_equip:
        pz, fac = plant_equip[0], float(plant_equip[1])
        hit = [o for o in objs if o["kw"] == "OTHEREQUIPMENT" and o["fields"][2] == pz]
        if len(hit) != 1:
            raise WriterError("plant: %d OtherEquipment objects for zone %s" % (len(hit), pz))
        o = hit[0]
        raw = text[o["start"]:o["end"]]
        old = float(o["fields"][6])
        new_raw, n = re.subn(r"^(\s*)[^,;!\s]+(,[ \t]*!- Power per Zone Floor Area)",
                             lambda m: "%s%s%s" % (m.group(1), repr(old * fac), m.group(2)), raw, count=1, flags=re.M)
        if n != 1:
            raise WriterError("plant: Power per Zone Floor Area line not found")
        text = text[:o["start"]] + new_raw + text[o["end"]:]
        objs = objects(text)
        say("PLANTED_equip", "zone %s OtherEquipment Power per Zone Floor Area %g -> %g (x%g; x gain 3 = %.2f W/m2)"
            % (pz, old, old * fac, fac, 3 * old * fac))
        expect.append(("oe_value", pz, old * fac))

    # ---- cooling (default, occupancy) ---------------------------------------------------------------------------
    if mode in ("default", "occupancy"):
        text, n1 = re.subn(r"EU_CoolingOff(,[ \t]*!- Cooling Availability Schedule Name)", r"EU_AlwaysOn\1", text)
        nthermo = sum(1 for o in objs if o["kw"] == "HVACTEMPLATE:THERMOSTAT")
        text, n2 = re.subn(r"^(\s*)50(;[ \t]*!- Constant Cooling Setpoint)", r"\g<1>%g\2" % COOL_SP_C, text, flags=re.M)
        if n1 != nflat or n2 != nthermo or nthermo != nflat:
            raise WriterError("cooling edit counts: availability %d (zones %d), setpoint %d (thermostats %d)"
                              % (n1, nflat, n2, nthermo))
        say("cooling_available", "%d of %d ideal-loads cooling availability EU_CoolingOff -> EU_AlwaysOn" % (n1, nflat))
        say("cooling_setpoint", "%d of %d thermostats constant cooling setpoint 50 -> %g C (heating stays 20 C)"
            % (n2, nthermo, COOL_SP_C))
        expect.append(("count_regex", r"EU_CoolingOff,[ \t]*!- Cooling Availability Schedule Name", 0))
        expect.append(("count_regex", r"%g;[ \t]*!- Constant Cooling Setpoint" % COOL_SP_C, nthermo))
        expect.append(("count_regex", r"^\s*50;[ \t]*!- Constant Cooling Setpoint", 0))
        objs = objects(text)
    else:
        say("cooling_unchanged", "cooling availability and setpoint left as simulated (heating only)")
        expect.append(("count_regex", r"EU_CoolingOff,[ \t]*!- Cooling Availability Schedule Name", nflat))

    # ---- OtherEquipment lump ------------------------------------------------------------------------------------
    n_oe = sum(1 for o in objs if o["kw"] == "OTHEREQUIPMENT")
    if mode == "occupancy":
        spans = [(o["start"], o["end"]) for o in objs if o["kw"] == "OTHEREQUIPMENT"]
        gain = [o for o in objs if o["kw"] == "SCHEDULE:FILE" and o["fields"][0].startswith("EU_Step8_GainSchedule_")]
        gain_names = [o["fields"][0] for o in gain]
        spans += [(o["start"], o["end"]) for o in gain]
        text = remove_objects(text, spans)
        left = sum(1 for nme in gain_names if nme in text)
        if left:
            raise WriterError("%d removed gain schedule names are still referenced" % left)
        say("lump_removed", "%d OtherEquipment objects and %d gain Schedule:File objects removed (no reference left)"
            % (n_oe, len(gain)))
        expect.append(("count_kw", "OTHEREQUIPMENT", 0))
        expect.append(("contains_none", "EU_Step8_GainSchedule_", None))
        objs = objects(text)
    else:
        say("lump_kept", "%d OtherEquipment objects kept (constant gain schedule, 3 W/m2)" % n_oe)
        expect.append(("count_kw", "OTHEREQUIPMENT", n_oe))

    # ---- People + ElectricEquipment -----------------------------------------------------------------------------
    add = []
    if mode == "occupancy":
        if not placement_path:
            raise WriterError("occupancy mode needs --placement")
        pl = read_placement(placement_path, zones)
        fold = DISTRICTS[district]
        area = {r["zone"]: r["floor_area_m2"] for r in rows}
        add.append("ScheduleTypeLimits, Frac, 0.0, 1.0, Continuous;\n")
        add.append("Schedule:Constant, Activity_Level, , %d;\n" % ACTIVITY_W)
        done, p_txt, a_txt = set(), [], []
        n_people, design = 0.0, 0.0
        for z in zones:
            hh = pl[z]
            tag = "HH_%s_%s" % (fold, hh["hid"])
            if tag not in done:
                if os.path.exists(hh["presence_csv"]):          # local check only; on Speed the run script checks the paths
                    _read_series(hh["presence_csv"])
                    _read_series(hh["appliance_csv"])
                p_txt.append(_sched_file(tag + "_Presence", hh["presence_csv"], 8760))
                a_txt.append(_sched_file(tag + "_Appliance", hh["appliance_csv"], 8760))
                done.add(tag)
            share = area[z] / area[z]            # one flat = one zone, so the floor-area share is 1 (pilot split rule)
            npeople = float(hh["n_members"]) * share
            lvl = float(hh["appliance_peak_w"]) * share
            n_people += npeople
            design += lvl
            p_txt.append(_peopletext(z, tag, npeople))
            a_txt.append(_eqtext(z, tag, lvl))
        add.extend(p_txt)
        add.extend(a_txt)
        say("people", "%d People objects (one per flat), total_people=%.4f, activity %d W, radiant 0.3, %d distinct households"
            % (nflat, n_people, ACTIVITY_W, len(done)))
        say("appliances", "%d ElectricEquipment objects, total_design_level=%.4f W, radiant 1.0" % (nflat, design))
        expect.append(("count_kw", "PEOPLE", nflat))
        expect.append(("count_kw", "ELECTRICEQUIPMENT", nflat))
        expect.append(("count_kw", "SCHEDULE:FILE", 2 * len(done)))
    else:
        expect.append(("count_kw", "PEOPLE", 0))
        expect.append(("count_kw", "ELECTRICEQUIPMENT", 0))

    # ---- outputs (all modes) --------------------------------------------------------------------------------------
    have = {o["fields"][1].lower() for o in objs if o["kw"] == "OUTPUT:VARIABLE"}
    want = [v for v in OUTPUT_VARIABLES + EXTRA_VARIABLES if v.lower() not in have]
    for v in want:
        add.append("Output:Variable,*,%s,Hourly;\n" % v)
    have_m = {o["fields"][0].lower() for o in objs if o["kw"] == "OUTPUT:METER"}
    want_m = [m for m in OUTPUT_METERS if m.lower() not in have_m and (LIGHTS_METER or not m.lower().startswith("interiorlights:"))]
    for m in want_m:
        add.append("Output:Meter,%s,Hourly;\n" % m)
    add.append("Output:VariableDictionary, Regular;\n")
    has_style = any(o["kw"] == "OUTPUTCONTROL:TABLE:STYLE" for o in objs)
    has_sum = any(o["kw"] == "OUTPUT:TABLE:SUMMARYREPORTS" for o in objs)
    if not has_style:
        add.append("OutputControl:Table:Style, CommaAndHTML;\n")
    if not has_sum:
        add.append("Output:Table:SummaryReports, AllSummary;\n")
    say("outputs", "+%d Output:Variable (%d skipped, already in the file) +%d Output:Meter, VariableDictionary, "
        "table style %s, summary reports %s" % (len(want), len(OUTPUT_VARIABLES + EXTRA_VARIABLES) - len(want), len(want_m),
                                                "kept" if has_style else "added", "kept" if has_sum else "AllSummary added"))
    expect.append(("count_kw", "OUTPUT:VARIABLE", len(have) + len(want)))
    expect.append(("count_kw", "OUTPUT:METER", len(have_m) + len(want_m)))
    if not LIGHTS_METER:
        expect.append(("count_regex", r"^\s*Output:Meter,\s*InteriorLights:Electricity", 0))
    expect.append(("count_kw", "OUTPUT:TABLE:SUMMARYREPORTS", 1))
    if not text.endswith(("\n", "\r\n")):
        text += eol
    block = ("!- 5J Step 9c Model A writer (mode %s) edits follow" % mode) + eol + eol.join(a.replace("\n", eol).rstrip("\r\n") + eol for a in add)
    text += eol + block
    return text, lines, expect


def verify_written(path, expect):
    """Re-read the file from disk and check every edit is PRESENT (a gate must be seen failing: see seenfail in state)."""
    text = read_text(path)
    objs = objects(text)
    res = []
    for kind, a, b in expect:
        if kind == "count_kw":
            got = sum(1 for o in objs if o["kw"] == a)
            ok = got == b
            res.append((ok, "count %s = %d (expected %d)" % (a, got, b)))
        elif kind == "count_regex":
            got = len(re.findall(a, text, flags=re.M))
            ok = got == b
            res.append((ok, "regex %r count = %d (expected %d)" % (a, got, b)))
        elif kind == "oe_value":
            vals = [float(o["fields"][6]) for o in objs if o["kw"] == "OTHEREQUIPMENT" and o["fields"][2] == a]
            ok = len(vals) == 1 and abs(vals[0] - b) < 1e-12
            res.append((ok, "OtherEquipment of %s Power per Zone Floor Area = %s (expected %g)" % (a, vals, b)))
        elif kind == "win_area":
            got = sum(x for _, x in fen_info(objs))
            ok = abs(got - a) <= 1e-6 * max(1.0, a)
            res.append((ok, "window area %.6f m2 (expected %.6f)" % (got, a)))
        elif kind == "contains_none":
            ok = a not in text
            res.append((ok, "text has no %r" % a))
    for ok, msg in res:
        print("CHECK %s %s" % ("PRESENT" if ok else "MISSING", msg))
    if not all(ok for ok, _ in res):
        raise WriterError("written file %s fails %d presence checks" % (path, sum(1 for ok, _ in res if not ok)))
    return res


def verify_schedule_paths(path):
    """AMENDMENT 3: resolve every relative '../../schedules/...csv' path of a written IDF the way the task script does
    (from the folder that holds the IDF) and print CHECK PRESENT / MISSING. Raises if any file is missing."""
    text = read_text(path)
    base = os.path.dirname(os.path.abspath(path))
    paths = sorted(set(re.findall(r"\.\./\.\./schedules/[^, ;\r\n]*\.csv", text)))
    bad = 0
    for q in paths:
        ok = os.path.isfile(os.path.normpath(os.path.join(base, q)))
        bad += (not ok)
        print("CHECK %s schedule path %s resolved from %s" % ("PRESENT" if ok else "MISSING", q, base))
    print("SCHEDCHECK %s: %d paths, %d missing" % (path, len(paths), bad))
    if bad:
        raise WriterError("%d schedule paths of %s do not resolve from its own folder" % (bad, path))
    return len(paths)


def cmd_schedcheck(args):
    verify_schedule_paths(args.idf)


def fast_edit(text):
    """Step 9i (additive; used by `write --fast`): the timing probe's V2 edit. ShadowCalculation Periodic update frequency 1 -> 20 and
    SimulationControl Do Zone / System / Plant Sizing Calculation Yes -> No. The replacement counts are asserted (shadow 1 of 1,
    sizing block 1 of 1 = 3 fields) and every edit is re-checked on the re-read file (returned `expect`)."""
    text, n1 = re.subn(r"(ShadowCalculation,\s*\n\s*PolygonClipping,[^\n]*\n\s*Periodic,[^\n]*\n\s*)1(;[ \t]*!- Shading Calculation Update Frequency\b)",
                       r"\g<1>20\2", text)
    text, n2 = re.subn(r"(SimulationControl,\s*\n\s*)Yes(,[ \t]*!- Do Zone Sizing Calculation\s*\n\s*)Yes(,[ \t]*!- Do System Sizing Calculation\s*\n\s*)Yes(,[ \t]*!- Do Plant Sizing Calculation)",
                       r"\g<1>No\2No\3No\4", text)
    if n1 != 1 or n2 != 1:
        raise WriterError("fast edit: shadow replaced %d (expected 1), sizing block replaced %d (expected 1)" % (n1, n2))
    lines = ["PATCH fast_shadow OK ShadowCalculation Periodic update frequency 1 -> 20 (1 of 1)",
             "PATCH fast_sizing OK SimulationControl zone, system, plant sizing Yes -> No (3 of 3)"]
    for l in lines:
        print(l)
    expect = [("count_regex", r"^\s*20;[ \t]*!- Shading Calculation Update Frequency\b", 1),
              ("count_regex", r"^\s*1;[ \t]*!- Shading Calculation Update Frequency\b", 0),
              ("count_regex", r"^\s*No,[ \t]*!- Do (Zone|System|Plant) Sizing Calculation", 3),
              ("count_regex", r"^\s*Yes,[ \t]*!- Do (Zone|System|Plant) Sizing Calculation", 0)]
    return text, lines, expect


def cmd_write(args):
    selftest()
    path = idf_path(args.district, args.stem)
    text = read_text(path)
    new, lines, expect = build(text, args.district, args.stem, args.mode, args.placement, args.plant_equip, args.plant_drop_window)
    if getattr(args, "fast", False):
        new, fl, fe = fast_edit(new)
        lines += fl
        expect += fe
    write_text(args.out, new)
    verify_written(args.out, expect)
    print("WROTE %s mode=%s bytes=%d" % (args.out, args.mode, len(new.encode("utf-8"))))


def cmd_placement(args):
    text = read_text(idf_path(args.district, args.stem))
    rows, reason, _, _ = zone_map(text, args.stem)
    if reason:
        raise WriterError("building left out: " + reason)
    with io.open(args.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["dwelling_zone", "hid", "presence_csv", "appliance_csv", "n_members", "appliance_peak_w"])
        for r in rows:
            w.writerow([r["zone"], "TEST", args.presence, args.appliance, 2, 500])
    print("PATCH placement OK %d flats, same synthetic household TEST (2 members, 500 W peak)" % len(rows))


def cmd_zonecheck(args):
    text = read_text(args.idf)
    stem = os.path.basename(args.idf).split(".")[0].split("_")[0] if not args.stem else args.stem
    rows, reason, nz, nc = zone_map(text, stem)
    print("ZONECHECK stem=%s zones=%d conditioned=%d flats=%d reason=%s" % (stem, nz, nc, len(rows), reason or "none"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tables")
    t.add_argument("--out-walls", required=True)
    t.add_argument("--out-zones", required=True)
    t.add_argument("--district")
    w = sub.add_parser("write")
    w.add_argument("--district", required=True)
    w.add_argument("--stem", required=True)
    w.add_argument("--mode", required=True)
    w.add_argument("--out", required=True)
    w.add_argument("--placement")
    w.add_argument("--plant-equip", nargs=2, metavar=("ZONE", "FACTOR"))
    w.add_argument("--fast", action="store_true", help="Step 9i: DF/OF variant, shadow update every 20 days and sizing off")
    w.add_argument("--plant-drop-window", action="store_true", help="planted fault P2: remove the largest window object from the copy")
    p = sub.add_parser("placement")
    p.add_argument("--district", required=True)
    p.add_argument("--stem", required=True)
    p.add_argument("--presence", required=True)
    p.add_argument("--appliance", required=True)
    p.add_argument("--out", required=True)
    z = sub.add_parser("zonecheck")
    z.add_argument("--idf", required=True)
    z.add_argument("--stem")
    sc = sub.add_parser("schedcheck", help="resolve ../../schedules paths of a written IDF from its own folder")
    sc.add_argument("--idf", required=True)
    sub.add_parser("selftest")
    a = ap.parse_args()
    selftest() if a.cmd == "selftest" else None
    {"tables": cmd_tables, "write": cmd_write, "placement": cmd_placement, "zonecheck": cmd_zonecheck,
     "schedcheck": cmd_schedcheck, "selftest": lambda _: None}[a.cmd](a)


if __name__ == "__main__":
    main()
