#!/usr/bin/env python3
"""Resolve WaterUse:Equipment -> PlantLoop -> WaterHeater:Mixed from the IDF's own topology.

WHY THIS EXISTS (V2-D10, 2026-08-05). V2-B4 decided the hotel DHW plant is resized PER OBJECT:
`LAUNDRY` alone at K ~ 7, every other heater at K = 1. That decision was taken against
`hotel_dT_by_type.csv`, whose rows are **WaterUse:Equipment types**. The thing `resize_idf()` edits is
**Heater Maximum Capacity on WaterHeater:Mixed**. Those are different objects and not even the same
count -- 16 equipment types against 6 heaters on `Tall` and 11 on `SuperTall`. So "LAUNDRY at K ~ 7"
names a row in a results table, not a field in the model, and something has to carry it across.

THE OBVIOUS SHORTCUT IS WRONG, AND THE EVIDENCE SAYS SO BEFORE THIS SCRIPT RUNS. The tempting selector
is "every heater whose Setpoint Temperature Schedule Name says 180F", because `LAUNDRY`'s target
schedule is `Mixed Water At Faucet Temp - 180F`. But that set differs 12x between the two geometries
(`Tall`: 87,921.32 + 7,999.96 = 95.92 kW; `SuperTall`: the 7,999.96 W booster ALONE, because all ten
300gal heaters sit on the 140F loop) -- while arm H's `LAUNDRY` energy is the SAME in both to 0.002 %
(913,520,381,430 J vs 913,539,008,832 J; at K = 6, 4,856,488,090,078 vs 4,856,496,565,814 J). A
capacity-pinned object cannot draw identical energy from two plants that differ 12x. So the selector
has to come from the topology the model actually solves, not from a temperature token in a name.

That is the same trap `_design_F()` in the campaign cell already documents: an equipment NAME carries
an F token but is a label, not an input. Here the Setpoint schedule is a real input -- it is just an
input to a different question (what the heater holds) than the one being asked (what serves LAUNDRY).

WHAT IT DOES. Parses the IDF with field labels intact, then walks:

    WaterUse:Equipment  --(named by)-->  WaterUse:Connections
                        --(its inlet/outlet nodes appear on)-->  Branch
                        --(that branch is in)-->  BranchList
                        --(named as Demand Side Branch List Name of)-->  PlantLoop
                        --(whose Plant Side Branch List Name lists)-->  Branch
                        --(whose components of type WaterHeater:Mixed are)-->  the serving heaters

and reports, per equipment object, the loop and the heater set with installed capacity.

REFUSALS, not defaults. Equipment that resolves to no loop, or a loop with no heater, is reported as
UNRESOLVED and the script exits non-zero. A topology mapper that silently returns an empty set would
hand `resize_idf()` a spec that quietly resizes nothing, which is the silent-default shape recorded at
job 1171812.

    python 3rdJ_09H_dhw_plant_topology.py <idf> [--json spec.json] [--equip SUBSTR]
"""
import json
import os
import sys


def iter_objects(text):
    """Yield each IDF object as a list of (value, field_label) pairs, type first.

    Field labels are kept because positional indexing into PlantLoop (17 fields before the demand
    branch list) is exactly the kind of assumption that breaks silently when a writer reorders or
    omits an optional field. The labels are in the file; using them costs nothing.
    """
    fields = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("!"):
            continue
        code, _, comment = s.partition("!")
        label = comment.lstrip("-").strip() if comment else ""
        code = code.strip()
        terminated = code.endswith(";")
        code = code.rstrip(";,")
        parts = [p.strip() for p in code.split(",")]
        for i, p in enumerate(parts):
            fields.append((p, label if i == len(parts) - 1 else ""))
        if terminated:
            if fields:
                yield fields
            fields = []


def load(idf_path):
    with open(idf_path, errors="replace") as f:
        text = f.read()
    by_type = {}
    for fields in iter_objects(text):
        t = fields[0][0]
        by_type.setdefault(t.lower(), []).append(fields)
    return by_type


def as_dict(fields):
    """label -> value for one object. Duplicate labels keep the first (IDF labels are unique)."""
    d = {}
    for value, label in fields[1:]:
        if label and label not in d:
            d[label] = value
    return d


def name_of(fields):
    return fields[1][0] if len(fields) > 1 else ""


def _numbered(d, prefix, suffix):
    """Collect 'Component 1 Object Type' / 'Equipment 3 Name' style repeated field groups."""
    out, i = [], 1
    while True:
        key = "%s %d %s" % (prefix, i, suffix)
        if key not in d:
            break
        out.append(d[key])
        i += 1
    return out


def build(by_type):
    heaters = {}
    for f in by_type.get("waterheater:mixed", []):
        d = as_dict(f)
        try:
            cap = float(d.get("Heater Maximum Capacity", "nan"))
        except ValueError:
            cap = float("nan")
        heaters[name_of(f).lower()] = {
            "name": name_of(f), "capacity_W": cap,
            "setpoint_schedule": d.get("Setpoint Temperature Schedule Name", ""),
            "fuel": d.get("Heater Fuel Type", ""),
        }

    # Branch -> component (type, name)
    branch_components = {}
    for f in by_type.get("branch", []):
        d = as_dict(f)
        types = _numbered(d, "Component", "Object Type")
        names = _numbered(d, "Component", "Name")
        branch_components[name_of(f).lower()] = list(zip(types, names))

    # BranchList -> [branch names]
    branchlists = {}
    for f in by_type.get("branchlist", []):
        d = as_dict(f)
        branchlists[name_of(f).lower()] = [v for v, lab in f[2:] if v]

    loops = {}
    for f in by_type.get("plantloop", []):
        d = as_dict(f)
        supply_bl = d.get("Plant Side Branch List Name", "")
        demand_bl = d.get("Demand Side Branch List Name", "")
        supply_heaters, demand_conns = [], []
        for b in branchlists.get(supply_bl.lower(), []):
            for ctype, cname in branch_components.get(b.lower(), []):
                if ctype.lower() == "waterheater:mixed":
                    supply_heaters.append(cname)
        for b in branchlists.get(demand_bl.lower(), []):
            for ctype, cname in branch_components.get(b.lower(), []):
                if ctype.lower() == "wateruse:connections":
                    demand_conns.append(cname)
        loops[name_of(f)] = {"heaters": supply_heaters, "connections": demand_conns}

    # WaterUse:Connections -> [equipment names]
    conn_equipment = {}
    for f in by_type.get("wateruse:connections", []):
        d = as_dict(f)
        conn_equipment[name_of(f).lower()] = _numbered(d, "Water Use Equipment", "Name")

    equipment = {}
    for f in by_type.get("wateruse:equipment", []):
        d = as_dict(f)
        equipment[name_of(f)] = {
            "target_schedule": d.get("Target Temperature Schedule Name", ""),
            "peak_flow_m3_s": d.get("Peak Flow Rate", ""),
        }

    # equipment -> loop, via the connections object that names it
    equip_loop = {}
    for loop, info in loops.items():
        for conn in info["connections"]:
            for eq in conn_equipment.get(conn.lower(), []):
                equip_loop[eq] = {"loop": loop, "connection": conn,
                                  "heaters": list(info["heaters"])}
    return heaters, loops, equipment, equip_loop


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: %s <idf> [--json spec.json] [--equip SUBSTR]" % sys.argv[0])
    idf = sys.argv[1]
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else ""
    want = sys.argv[sys.argv.index("--equip") + 1].lower() if "--equip" in sys.argv else ""
    if not os.path.isfile(idf):
        raise SystemExit("REFUSING: no such IDF: %s" % idf)

    heaters, loops, equipment, equip_loop = build(load(idf))
    print("=" * 92)
    print("DHW PLANT TOPOLOGY  %s" % os.path.basename(idf))
    print("=" * 92)
    print("  %d WaterHeater:Mixed, %d PlantLoop, %d WaterUse:Equipment"
          % (len(heaters), len(loops), len(equipment)))

    for loop, info in sorted(loops.items()):
        kw = sum(heaters[h.lower()]["capacity_W"] for h in info["heaters"]
                 if h.lower() in heaters) / 1000.0
        if not info["heaters"] and not info["connections"]:
            continue
        print("")
        print("  LOOP  %s" % loop)
        print("        supply: %d WaterHeater:Mixed, installed %.2f kW" % (len(info["heaters"]), kw))
        for h in info["heaters"]:
            m = heaters.get(h.lower(), {})
            print("           %10.2f W  [%s]  %s" % (m.get("capacity_W", float("nan")),
                                                     m.get("setpoint_schedule", "?"), h))
        print("        demand: %d WaterUse:Connections" % len(info["connections"]))

    unresolved = [e for e in equipment if e not in equip_loop]
    print("")
    print("  EQUIPMENT -> SERVING HEATERS")
    rows = sorted(equipment, key=lambda e: (0 if want and want in e.lower() else 1, e))
    for eq in rows:
        if want and want not in eq.lower():
            continue
        info = equip_loop.get(eq)
        if not info:
            print("    [UNRESOLVED] %s" % eq)
            continue
        kw = sum(heaters[h.lower()]["capacity_W"] for h in info["heaters"]
                 if h.lower() in heaters) / 1000.0
        print("    %s" % eq)
        print("        target %s" % equipment[eq]["target_schedule"])
        print("        loop   %s" % info["loop"])
        print("        served by %d heater(s), %.2f kW installed:" % (len(info["heaters"]), kw))
        for h in info["heaters"]:
            m = heaters.get(h.lower(), {})
            print("           %10.2f W  [%s]  %s" % (m.get("capacity_W", float("nan")),
                                                     m.get("setpoint_schedule", "?"), h))

    if out_json:
        with open(out_json, "w") as f:
            json.dump({"idf": os.path.abspath(idf), "heaters": heaters,
                       "loops": loops, "equipment": equipment, "equipment_to_loop": equip_loop},
                      f, indent=1, sort_keys=True)
        print("")
        print("  wrote %s" % out_json)

    if unresolved:
        print("")
        print("  REFUSING: %d WaterUse:Equipment resolved to no plant loop: %s"
              % (len(unresolved), unresolved[:5]))
        sys.exit(2)
    if any(not v["heaters"] for v in equip_loop.values()):
        print("")
        print("  REFUSING: at least one equipment object resolved to a loop with no WaterHeater:Mixed")
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
