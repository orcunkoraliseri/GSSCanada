"""WP14: hourly-derived tables from eplusout.mtr (hourly meters) for the stage-4 runs.
Read-only on stage4/. Task doc: 1J_docs_occ/IMP/impl/2026-09-29_WP14_hourly_energy_extract.md
Modes:  --mode run --nb RC1 ...   (151 runs)   |   --mode selftest --mtr F --htm F --ref-csv F ...
Units: mtr is Joules per hour. kWh/m2 = J/3.6e6/area. Peak power W/m2 = J_per_hour/3600/area.
Hour-of-day h = mtr hour field - 1 (hour ending 1..24 -> interval-start 0..23).
Day type = DayType field of the mtr (the simulation calendar of the weather year the run used);
weekend = Saturday, Sunday (no Holiday day types occur).
Floor area = eplustbl.htm "Net Conditioned Building Area" (else Total), same preference as
plotting.calculate_eui, which produced per_draw_eui.csv.
"""
import argparse, csv, os, re, sys
import numpy as np

ROOT = "/speed-scratch/o_iseri/1J_rerun/stage4/draws"
OUT = "/speed-scratch/o_iseri/1J_rerun/wp14/out"
YEARS = ["2005", "2010", "2015", "2022", "2025"]
# hourly meter -> (end-use label, per_draw_eui.csv end_use name)
METERS = {"Heating:EnergyTransfer": ("heating", "Heating"),
          "Cooling:EnergyTransfer": ("cooling", "Cooling"),
          "InteriorEquipment:Electricity": ("equipment", "Electric Equipment"),
          "InteriorLights:Electricity": ("lights", "Interior Lighting"),
          "WaterSystems:EnergyTransfer": ("water", "Water Systems")}
USES = [v[0] for v in METERS.values()]
TOL = 0.01
J_KWH = 3.6e6


def parse_area(htm):
    net = tot = None
    with open(htm, "r", errors="replace") as f:
        for line in f:
            if "Net Conditioned Building Area" in line and net is None:
                net = float(re.sub(r"<[^>]+>", "", next(f)).strip())
            elif "Total Building Area" in line and tot is None and "Per" not in line:
                tot = float(re.sub(r"<[^>]+>", "", next(f)).strip())
            if net is not None and tot is not None:
                break
    a = net or tot
    if not a:
        raise ValueError("no floor area in " + htm)
    return a


def parse_mtr(path):
    ids = {}
    ser = {}
    cal = []
    in_dict = True
    cur = None
    with open(path, "r", errors="replace") as f:
        for line in f:
            if in_dict:
                if line.startswith("End of Data Dictionary"):
                    in_dict = False
                    continue
                p = line.split(",", 2)
                if len(p) == 3 and "!Hourly" in line:
                    name = p[2].split("[")[0].strip()
                    if name in METERS:
                        ids[p[0]] = METERS[name][0]
                        ser[METERS[name][0]] = []
                continue
            p = line.rstrip("\n").split(",")
            if p[0] == "2":
                cur = True
                cal.append((int(p[2]), int(p[5]), p[-1].strip()))
            elif p[0] == "1":
                cur = None
                if not p[1].strip().startswith("RUN PERIOD"):
                    raise ValueError("unexpected environment: " + line)
            elif p[0] in ids and cur:
                ser[ids[p[0]]].append(float(p[1]))
    n = len(cal)
    for u in USES:
        if len(ser.get(u, [])) != n:
            raise ValueError("meter %s has %d values for %d hours" % (u, len(ser.get(u, [])), n))
    if n != 8760:
        raise ValueError("expected 8760 hours, got %d" % n)
    d = {u: np.array(ser[u]) for u in USES}
    month = np.array([c[0] for c in cal])
    hour = np.array([c[1] for c in cal]) - 1
    dt = np.array([c[2] for c in cal])
    wk = np.isin(dt, ["Saturday", "Sunday"])
    return d, month, hour, wk


def annual_kwh_m2(d, area):
    return {u: d[u].sum() / J_KWH / area for u in USES}


def tables(d, month, hour, wk, area, key):
    nb, yr, dr = key
    annual = annual_kwh_m2(d, area)
    pk = {}
    for u in ("cooling", "heating"):
        w = d[u] / 3600.0 / area  # W/m2 (hourly mean power)
        i = int(np.argmax(w))
        pk[u] = (w[i], i)
    top10 = np.argsort(-d["cooling"], kind="stable")[:10]
    ci = pk["cooling"][1]
    hi = pk["heating"][1]
    peaks = [nb, yr, dr, "%.4f" % pk["cooling"][0], ci // 24 + 1, month[ci], hour[ci],
             "%.4f" % pk["heating"][0], hi // 24 + 1, month[hi], hour[hi],
             "%.3f" % hour[top10].mean()]
    diurnal = []
    for gname, months, wkend in (("winter_weekday", (12, 1, 2), False), ("winter_weekend", (12, 1, 2), True),
                                 ("summer_weekday", (6, 7, 8), False), ("summer_weekend", (6, 7, 8), True)):
        m = np.isin(month, months) & (wk == wkend)
        for h in range(24):
            s = m & (hour == h)
            diurnal.append([nb, yr, dr, gname, h, int(s.sum())] +
                           ["%.5f" % (d[u][s].mean() / 3600.0 / area) for u in USES])  # W/m2
    monthly = []
    for mo in range(1, 13):
        s = month == mo
        monthly.append([nb, yr, dr, mo] + ["%.5f" % (d[u][s].sum() / J_KWH / area) for u in USES])
    return annual, peaks, diurnal, monthly


def read_ref(path):
    ref = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ref[(r["year"], int(r["draw"]), r["end_use"])] = float(r["value"])
    return ref


def check(annual, ref, yr, dr):
    out = []
    for m, (u, eu) in METERS.items():
        r = ref.get((yr, dr, eu))
        out.append((u, annual[u], r, abs(annual[u] - r) if r is not None else float("nan")))
    return out


def selftest(a):
    d, mo, hr, wk = parse_mtr(a.mtr)
    area = parse_area(a.htm)
    ref = read_ref(a.ref_csv)
    print("W14 SELFTEST area=%.4f m2 hours=%d" % (area, len(mo)))
    bad = 0
    for label, ar, expect in (("WRONG area (x1.05)", area * 1.05, "FAIL"), ("correct area", area, "PASS")):
        rows = check(annual_kwh_m2(d, ar), ref, a.year, a.draw)
        hc = [r for r in rows if r[0] in ("heating", "cooling")]
        mx = max(r[3] for r in hc)
        verdict = "PASS" if mx <= TOL else "FAIL"
        for r in rows:
            print("   %-18s %-10s hourly=%.4f ref=%s absdiff=%.5f" % (label, r[0], r[1], r[2], r[3]))
        print("[SELFTEST %s] W14.1 with %s: got %s expected %s max_abs_diff(heat,cool)=%.5f" %
              ("OK" if verdict == expect else "BAD", label, verdict, expect, mx))
        bad += verdict != expect
    t = tables(d, mo, hr, wk, area, ("SELF", a.year, a.draw))
    print("W14 SELFTEST peaks:", t[1])
    print("W14 SELFTEST diurnal rows=%d monthly rows=%d" % (len(t[2]), len(t[3])))
    print("W14 SELFTEST SUMMARY unexpected=%d" % bad)
    return 1 if bad else 0


def run(a):
    nb = a.nb
    os.makedirs(OUT, exist_ok=True)
    Hdr = {"annual_check": ["neighbourhood", "year", "draw", "area_m2", "heating_hourly", "heating_ref", "heating_absdiff",
                            "cooling_hourly", "cooling_ref", "cooling_absdiff", "equipment_hourly", "equipment_ref",
                            "equipment_absdiff", "lights_hourly", "lights_ref", "lights_absdiff", "water_hourly",
                            "water_ref", "water_absdiff", "gate_W14_1"],
           "peaks": ["neighbourhood", "year", "draw", "cool_peak_W_m2", "cool_peak_doy", "cool_peak_month", "cool_peak_hour",
                     "heat_peak_W_m2", "heat_peak_doy", "heat_peak_month", "heat_peak_hour", "cool_top10_mean_hour"],
           "diurnal": ["neighbourhood", "year", "draw", "group", "hour", "n_hours"] + [u + "_W_m2" for u in USES],
           "monthly": ["neighbourhood", "year", "draw", "month"] + [u + "_kWh_m2" for u in USES]}
    W = {k: open(os.path.join(OUT, "%s_%s.csv" % (k, nb)), "w", newline="") for k in Hdr}
    cw = {k: csv.writer(W[k]) for k in W}
    for k in Hdr:
        cw[k].writerow(Hdr[k])
    n = 0
    nerr = 0
    mx = 0.0
    todo = [("Default", 0, os.path.join(ROOT, "block_1", "NUS_" + nb, "Default"), os.path.join(ROOT, "block_1", "NUS_" + nb))]
    for dr in range(1, 31):
        b = (dr - 1) // 5 + 1
        base = os.path.join(ROOT, "block_%d" % b, "NUS_" + nb)
        for yr in YEARS:
            todo.append((yr, dr, os.path.join(base, "iter_%d" % dr, yr), base))
    refs = {}
    for yr, dr, folder, base in todo:
        try:
            if base not in refs:
                refs[base] = read_ref(os.path.join(base, "per_draw_eui.csv"))
            area = parse_area(os.path.join(folder, "eplustbl.htm"))
            d, mo, hr, wk = parse_mtr(os.path.join(folder, "eplusout.mtr"))
            annual, peaks, diu, mon = tables(d, mo, hr, wk, area, (nb, yr, dr))
            rows = check(annual, refs[base], yr, dr)
            hc = max(r[3] for r in rows if r[0] in ("heating", "cooling"))
            if hc != hc:
                raise ValueError("no reference row in per_draw_eui.csv")
            mx = max(mx, hc)
            ac = [nb, yr, dr, "%.4f" % area]
            for r in rows:
                ac += ["%.4f" % r[1], "" if r[2] is None else "%.4f" % r[2], "%.5f" % r[3]]
            ac.append("PASS" if hc <= TOL else "FAIL")
            cw["annual_check"].writerow(ac)
            cw["peaks"].writerow(peaks)
            cw["diurnal"].writerows(diu)
            cw["monthly"].writerows(mon)
            print("W14 RUN %s %s %d OK%s" % (nb, yr, dr, "" if hc <= TOL else " GATE_FAIL diff=%.5f" % hc))
            sys.stdout.flush()
            n += 1
        except Exception as e:
            nerr += 1
            print("W14 RUN %s %s %d ERROR %s" % (nb, yr, dr, e))
            sys.stdout.flush()
    for f in W.values():
        f.close()
    print("W14 SUMMARY runs=%d errors=%d annual_check_max_abs_diff=%.5f" % (n, nerr, mx))
    ok = n == 151 and nerr == 0 and mx <= TOL
    print("W14 VERDICT %s %s" % (nb, "VERIFIED" if ok else "NOT_VERIFIED"))
    return 0 if ok else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["run", "selftest"], required=True)
    p.add_argument("--nb")
    p.add_argument("--mtr")
    p.add_argument("--htm")
    p.add_argument("--ref-csv")
    p.add_argument("--year", default="2005")
    p.add_argument("--draw", type=int, default=1)
    a = p.parse_args()
    sys.exit(selftest(a) if a.mode == "selftest" else run(a))
