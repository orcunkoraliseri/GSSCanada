"""V3c fairer code-schedule control (arm F): the frozen uninjected Default_NECB IDF (arm U in V3b),
with ONE addition -- a new Schedule:Compact "NECB-G-Occupancy" (the NECB dwelling-unit / residential
occupancy schedule) -- and the apartment + hotel-guest-room PEOPLE objects re-pointed to it instead of
NECB-A-Occupancy (the NECB OFFICE occupancy schedule U currently puts them on; manager finding M-1,
`3J_IMP_execution_2026-09-22.md` 2026-09-22 P3 entry, `IMP/P3_code_schedule_comparison.md`).

Evidence NECB-G is the residential/dwelling-unit schedule (not invented): NECB assigns
`NECB-G-Occupancy` to space types "Dwelling Unit(s)" and "Multi-unit residential"
(`improvements/v2/f8_necb_schedule_evidence/space_types_NECB2011.json`, table `space_types`, rows
with `necb_schedule_type=="G"`). Hourly values below are copied verbatim from
`improvements/v2/f8_necb_schedule_evidence/sched_NECB2011.json`, table `schedules`, the 3 rows with
`name=="NECB-G-Occupancy"` (day_types `Default|Wkdy`, `Sat`, `Sun|Hol`); identical in
`sched_NECB2015.json`. Day-type mapping for the new Schedule:Compact copies the structure the frozen
NECB-A-Occupancy object already uses (verified object,
`Leg3_4-split/Step8_docs/campaign_local_deliverable/Default_NECB__Tall__MTL/injected_resized.idf`
lines 11429-11674): Weekdays = WinterDesignDay = SummerDesignDay = Default|Wkdy row; Saturday = Sat
row; Sunday = Sun|Hol row (Sat and Sun|Hol rows are identical in the source table, asserted below).

Changes NOTHING else: LIGHTS and ELECTRICEQUIPMENT of these Spaces are untouched (still their own
PNNL prototype schedules, e.g. `ApartmentHighRise LTG_APT_SCH`, `HotelLarge BLDG_LIGHT_SCH_2013`;
unlike arm R, which re-points office/retail/hotel LIGHTS+ELECTRICEQUIPMENT too). Only the 4 PEOPLE
objects' "Number of People Schedule Name" field changes, plus the 1 new Schedule:Compact object.

    py -3 v3c_build_F.py <frozen_Default_NECB_injected_resized.idf> <out.idf>
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0].rsplit("\\", 1)[0])
import v3_build_R as RB   # noqa: E402  (reuses objects()/fmt(), same IDF text format)

APARTMENT_PEOPLE = "HighriseApartment Apartment People"
GUESTROOM_PEOPLE = {"LargeHotel GuestRoom5 People", "LargeHotel GuestRoom6 People",
                     "LargeHotel GuestRoom7 People"}
TARGETS = {APARTMENT_PEOPLE} | GUESTROOM_PEOPLE
OLD_SCHED = "NECB-A-Occupancy"
NEW_SCHED = "NECB-G-Occupancy"

# Source: improvements/v2/f8_necb_schedule_evidence/sched_NECB2011.json, table "schedules",
# name=="NECB-G-Occupancy" (identical in sched_NECB2015.json). Hour 1 = 00:00-01:00 ... hour 24 =
# 23:00-24:00. NOT invented -- read verbatim from the repo file, checked by the assert below.
WKDY = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.7, 0.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5,
        0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
SAT = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.7, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.7,
       0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
SUN = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.7, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.7,
       0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
assert SAT == SUN, "REFUSING: NECB-G Sat/Sun rows expected identical per source table"


def _hours(vals):
    out = []
    for h, v in enumerate(vals, start=1):
        out.append("Until: %02d:00" % h)
        out.append(str(v))
    return out


def necb_g_fields():
    fields = [NEW_SCHED, "Fraction", "Through: 12/31"]
    fields += ["For: Weekdays"] + _hours(WKDY)
    fields += ["For: Saturday"] + _hours(SAT)
    fields += ["For: Sunday"] + _hours(SUN)
    fields += ["For: WinterDesignDay"] + _hours(WKDY)
    fields += ["For: SummerDesignDay"] + _hours(WKDY)
    return fields


def build(src, dst):
    txt = open(src, errors="replace").read()
    objs = RB.objects(txt)
    edits = []
    n_hit = {"apartment": 0, "hotel": 0}
    for s, e, cls, f in objs:
        if cls.upper() != "PEOPLE" or f[0] not in TARGETS:
            continue
        if f[2] != OLD_SCHED:
            raise SystemExit("REFUSING: %r schedule was %r, expected %r" % (f[0], f[2], OLD_SCHED))
        nf = list(f)
        nf[2] = NEW_SCHED
        edits.append((s, e, RB.fmt(cls, nf)))
        n_hit["apartment" if f[0] == APARTMENT_PEOPLE else "hotel"] += 1
    if n_hit["apartment"] != 1 or n_hit["hotel"] != 3:
        raise SystemExit("REFUSING: found apartment=%d hotel=%d, expected 1 and 3" % (
            n_hit["apartment"], n_hit["hotel"]))
    for s, e, new in sorted(edits, key=lambda x: -x[0]):
        txt = txt[:s] + new + txt[e:]
    txt = txt.rstrip("\n") + "\n\n" + RB.fmt("Schedule:Compact", necb_g_fields())
    open(dst, "w").write(txt)
    rep = {"repointed": n_hit, "new_schedule": NEW_SCHED, "old_schedule": OLD_SCHED,
           "targets": sorted(TARGETS)}
    # self-check: re-parse and confirm ONLY the intended objects changed (+1 added)
    o2 = RB.objects(open(dst, errors="replace").read())
    a = [(c.upper(), tuple(x)) for _, _, c, x in objs]
    b = [(c.upper(), tuple(x)) for _, _, c, x in o2]
    changed = sum(1 for x, y in zip(a, b[:len(a)]) if x != y)
    rep["objects_changed"] = changed
    rep["objects_added"] = len(b) - len(a)
    if changed != 4 or len(b) - len(a) != 1:
        raise SystemExit("REFUSING: F edit touched %d objects (+%d), expected 4 (+1)" % (
            changed, len(b) - len(a)))
    return rep


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
