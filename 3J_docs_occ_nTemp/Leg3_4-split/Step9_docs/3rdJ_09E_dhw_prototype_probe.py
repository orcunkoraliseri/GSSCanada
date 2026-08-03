# Is office DHW material, and is its weekend already near-zero in the PROTOTYPE?
# Plain-text IDF parse (no eppy) of the pre-injection tower.
import os, re, sys
from collections import defaultdict

IDF = (r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split"
       r"\Step8_docs\outputs_step8\office_idfs_v242\CAN_MTL"
       r"\TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf")


def parse(path):
    txt = open(path, "r", errors="replace").read()
    txt = re.sub(r"!.*", "", txt)                       # strip comments
    objs = defaultdict(list)
    for blk in txt.split(";"):
        f = [x.strip() for x in blk.split(",")]
        while f and f[0] == "":
            f.pop(0)                      # leading blank lines only -- keep INTERNAL blanks
        if not f:
            continue
        objs[f[0].upper()].append(f)
    return objs


O = parse(IDF)
print("object counts:", {k: len(v) for k, v in O.items()
                         if "WATERUSE" in k or k.startswith("SCHEDULE")})

# ---- schedule resolution: YEAR -> WEEK:DAILY -> DAY:INTERVAL/HOURLY ----
day_i = {f[1].upper(): f for f in O.get("SCHEDULE:DAY:INTERVAL", [])}
day_h = {f[1].upper(): f for f in O.get("SCHEDULE:DAY:HOURLY", [])}
wk_d = {f[1].upper(): f for f in O.get("SCHEDULE:WEEK:DAILY", [])}
yr = {f[1].upper(): f for f in O.get("SCHEDULE:YEAR", [])}


def day24(name):
    k = name.upper()
    if k in day_h:
        return [float(x) for x in day_h[k][3:27]]
    if k in day_i:
        f = day_i[k]
        vals, prev = [0.0] * 24, 0
        rest = f[4:]
        for i in range(0, len(rest) - 1, 2):
            t, v = rest[i], float(rest[i + 1])
            m = re.match(r"(?:Until:\s*)?(\d+):(\d+)", t, re.I)
            if not m:
                continue
            end = int(m.group(1)) * 60 + int(m.group(2))
            for h in range(24):
                if prev <= h * 60 < end:
                    vals[h] = v
            prev = end
        return vals
    return None


def week_profiles(name):
    f = wk_d.get(name.upper())
    if not f:
        return None
    # Schedule:Week:Daily field order: Name, Sunday, Monday..Saturday, Holiday, ...
    sun, mon, sat = f[2], f[3], f[8]
    return day24(mon), day24(sat), day24(sun)


def resolve(name):
    f = yr.get(name.upper())
    if not f:
        return None, "not a Schedule:Year"
    wk = f[3]                                   # first week schedule name
    p = week_profiles(wk)
    if p is None or p[0] is None:
        return None, f"week '{wk}' unresolved"
    mon, sat, sun = p
    we = [(a + b) / 2.0 for a, b in zip(sat, sun)]
    return {"wd": mon, "we": we, "sat": sat, "sun": sun}, f"Year->{wk}"


CH = [("office", ("OFFICE", "OPENOFFICE", "CONFERENCE", "BREAKROOM", "CORRIDOR_OFF")),
      ("retail", ("RETAIL", "CORE_RETAIL", "FRONT_RETAIL")),
      ("hotel", ("GUEST", "HOTEL", "LAUNDRY", "LOBBY", "BANQUET", "KITCHEN")),
      ("residential", ("APARTMENT", "DWELL", "HIGHRISE"))]


def classify(s):
    u = s.upper()
    for ch, toks in CH:
        if any(t in u for t in toks):
            return ch
    return "?"


print("\n%-42s %-10s %12s %10s %10s %10s" %
      ("WaterUse:Equipment", "channel", "Peak_m3/s", "mean_wd", "mean_we", "we/wd"))
tot = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
for f in O.get("WATERUSE:EQUIPMENT", []):
    # WaterUse:Equipment: 0=class 1=Name 2=EndUseSubcat 3=PeakFlowRate 4=FlowRateFractionSchedule
    nm = f[1]
    try:
        peak = float(f[3])
    except (ValueError, IndexError):
        peak = 0.0
    sch = f[4] if len(f) > 4 else ""
    ch = classify(nm)
    prof, prov = resolve(sch)
    if prof is None:
        print("%-42s %-10s %12s   UNRESOLVED (%s) sch=%s" % (nm[:42], ch, peak, prov, sch))
        continue
    mwd = sum(prof["wd"]) / 24.0
    mwe = sum(prof["we"]) / 24.0
    print("%-42s %-10s %12.6g %10.4f %10.4f %10.3f" %
          (nm[:42], ch, peak or 0, mwd, mwe, (mwe / mwd if mwd > 1e-12 else float('nan'))))
    t = tot[ch]
    t[0] += 1
    t[1] += (peak or 0)
    t[2] += (peak or 0) * mwd
    t[3] += (peak or 0) * mwe

print("\n%-14s %5s %14s %16s %16s %8s" %
      ("channel", "n", "sum Peak", "wd daily vol", "we daily vol", "we/wd"))
gwd = sum(v[2] for v in tot.values())
for ch, v in sorted(tot.items()):
    print("%-14s %5d %14.6g %16.6g %16.6g %8.3f   (%.1f%% of bldg weekday DHW volume)" %
          (ch, v[0], v[1], v[2] * 24 * 3600, v[3] * 24 * 3600,
           (v[3] / v[2] if v[2] > 1e-12 else float('nan')),
           100 * v[2] / gwd if gwd > 0 else 0))
