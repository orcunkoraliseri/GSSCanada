"""V3b reference arm R: the frozen uninjected IDF, edited BY HAND-RULE (no injector code) to what the
injection contract says a code-schedule injection must produce.

Contract as it ran for the frozen deliverable (injector with preserve_load_standby_floor=False, i.e.
before T9-9; commercial_integration.py docstring Tag-2 table :27-46 and the S9D-8 block :386-395):
  * office Space types (OpenOffice, ClosedOffice, Conference, Classroom, Dining, Restroom),
    retail (Retail Retail, Retail Back_Space, Retail Point_of_Sale, Retail Entry) and hotel guest
    rooms (LargeHotel GuestRoom5/6/7): PEOPLE, LIGHTS and ELECTRICEQUIPMENT all carry the channel's
    ONE occupancy schedule. Densities untouched. GasEquipment untouched.
    -> here: LIGHTS/ELECTRICEQUIPMENT of those Space types are re-pointed to the schedule their own
       People object already carries (NECB-A-Occupancy; NECB-C-Occupancy for retail after V2-D9).
  * residential apartments (Tag 2 = "HighriseApartment Apartment"): the SpaceList People carrier is
    neutralised (Number of People = 0) and one People object per apartment Space carries
    Number of People = K on the carrier's own occupancy + activity schedules.
Everything else is byte-identical to the frozen file (verified at the end: changed-object count).

    py -3 v3_build_R.py <frozen_injected_resized.idf> <out.idf> [K=2]
"""
import re
import sys

OFFICE = {"OpenOffice", "ClosedOffice", "Conference", "Classroom", "Dining", "Restroom"}
RETAIL = {"Retail Retail", "Retail Back_Space", "Retail Point_of_Sale", "Retail Entry"}
HOTEL = {"LargeHotel GuestRoom5", "LargeHotel GuestRoom6", "LargeHotel GuestRoom7"}
RESID = "HighriseApartment Apartment"


def objects(txt):
    """[(start, end, class, [field values])] -- ';'-terminated IDF objects, comments stripped."""
    out = []
    for m in re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9:]*),[ \t]*(?:!.*)?$", txt):
        end = txt.find(";", m.end())
        eol = txt.find("\n", end)
        eol = len(txt) if eol < 0 else eol + 1
        raw = txt[m.end():end]
        vals = [re.sub(r"!.*", "", l) for l in raw.split("\n")]
        joined = "".join(vals)
        fields = [f.strip() for f in joined.split(",")]
        out.append((m.start(), eol, m.group(1), fields))
    return out


def fmt(cls, fields):
    return cls + ",\n" + "".join("    %s,\n" % f for f in fields[:-1]) + "    %s;\n" % fields[-1]


def build(src, dst, K=2):
    txt = open(src, errors="replace").read()
    objs = objects(txt)
    people_sched = {}
    carrier = None
    for s, e, cls, f in objs:
        if cls.upper() == "PEOPLE":
            people_sched[f[1]] = f[2]
            if f[1] == RESID:
                carrier = (s, e, cls, f)
    retail_sched = people_sched["Retail Retail"]
    edits = []                                   # (start, end, new_text)
    n_rep = {"office": 0, "retail": 0, "hotel": 0}
    for s, e, cls, f in objs:
        if cls.upper() not in ("LIGHTS", "ELECTRICEQUIPMENT"):
            continue
        z = f[1]
        ch = "office" if z in OFFICE else "retail" if z in RETAIL else "hotel" if z in HOTEL else None
        if ch is None:
            continue
        target = retail_sched if ch == "retail" else people_sched[z]
        nf = list(f)
        nf[2] = target
        edits.append((s, e, fmt(cls, nf)))
        n_rep[ch] += 1
    # residential split
    if carrier is None:
        raise SystemExit("REFUSING: no People carrier on %r" % RESID)
    s, e, cls, f = carrier
    # People fields: 0 Name,1 Zone/SpaceList,2 Sched,3 Method,4 N,5 per area,6 area per person,
    # 7 frac radiant,8 SHF,9 activity sched,10 CO2,11 comfort warn,12 MRT type, ...
    nf = list(f)
    nf[3], nf[4], nf[5], nf[6] = "People", "0", "", ""
    edits.append((s, e, fmt(cls, nf)))
    spaces = []
    for _s, _e, c2, f2 in objs:
        if c2.upper() == "SPACE":
            # Space: 0 Name,1 Zone,2 Ceiling,3 Volume,4 Floor Area,5 Space Type,6 Tag1,7 Tag2 ...
            if len(f2) > 7 and f2[7] == RESID:          # Tag 2, exact match (as the injector)
                spaces.append(f2[0])
    spaces = sorted(spaces)
    if not spaces:
        raise SystemExit("REFUSING: 0 apartment Spaces found")
    add = []
    for sp in spaces:
        pf = list(f)
        pf[0], pf[1], pf[3], pf[4], pf[5], pf[6] = "%s People" % sp, sp, "People", str(K), "", ""
        add.append(fmt("PEOPLE", pf))
    for s, e, new in sorted(edits, key=lambda x: -x[0]):
        txt = txt[:s] + new + txt[e:]
    txt = txt.rstrip("\n") + "\n\n" + "\n".join(add)
    open(dst, "w").write(txt)
    rep = {"relinked_lights_equip": n_rep, "carrier_neutralised": 1, "apartment_people_added": len(spaces),
           "K": K, "retail_schedule": retail_sched,
           "office_schedules": sorted({people_sched[z] for z in OFFICE}),
           "hotel_schedules": sorted({people_sched[z] for z in HOTEL})}
    # self-check: re-parse and confirm only the intended objects changed
    o2 = objects(open(dst, errors="replace").read())
    a = [(c.upper(), tuple(x)) for _, _, c, x in objs]
    b = [(c.upper(), tuple(x)) for _, _, c, x in o2]
    changed = sum(1 for x, y in zip(a, b[:len(a)]) if x != y)
    rep["objects_changed"] = changed
    rep["objects_added"] = len(b) - len(a)
    exp = sum(n_rep.values()) + 1
    if changed != exp or len(b) - len(a) != len(spaces):
        raise SystemExit("REFUSING: R edit touched %d objects (+%d), expected %d (+%d)"
                         % (changed, len(b) - len(a), exp, len(spaces)))
    return rep


if __name__ == "__main__":
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    print(build(sys.argv[1], sys.argv[2], K))
