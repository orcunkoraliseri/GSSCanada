#!/usr/bin/env python3
"""5J WP1 pilot checker (Spain only). RUNS ON SPEED via sbatch, never on the login node or the local machine.

Output: one line per gate:  PASS|FAIL|WARN|INFO|NOT_EVALUABLE <gate> <numbers>
then:   SUMMARY PASS=.. FAIL=.. WARN=.. INFO=.. NOT_EVALUABLE=..

EXIT CODE MEANING (val doc severities):
  FAIL-severity gates = 2.1 2.2 2.3 2.4 2.5 3.1 3.4 4.2a 5.1 5.2 5.3 P.1 P.2
  exit 0 only when none of these is FAIL and none is NOT_EVALUABLE.
  exit 1 = at least one FAIL-severity gate FAIL or NOT_EVALUABLE.
  exit 2 = the checker itself crashed outside a gate (no SUMMARY printed).
  WARN gates (3.2, 4.1, 4.2b, 4.3) and INFO (3.3) never change the exit code.
A gate that raises is reported NOT_EVALUABLE with the exception text (it is never silently skipped).

Layout read under --root (the pilot folder):
  run_manifest.csv  extracted/<run>.csv  inputs/<input_id>/presence_HH_<hid>.csv
  runs/<run>/{status.txt,time.txt,model.idf,presence_*.csv,elec_*.csv,eplus_out/eplusout.err,eplus_out/eplustbl.csv}
  logs/task_<array>_<n>.out   preflight.txt
"""
import argparse, csv, datetime, glob, hashlib, math, os, re, statistics, sys

FAIL_GATES = {"2.1", "2.2", "2.3", "2.4", "2.5", "3.1", "3.4", "4.2a", "5.1", "5.2", "5.3", "P.1", "P.2"}
TARGETS = ["heating_J", "cooling_J", "appliance_J", "facility_elec_J"]
MANIFEST_FIELDS = ["run_id", "country", "climate", "building_id", "household_id", "replicate", "schedule_md5",
                   "idf_md5", "epw_md5", "energyplus_version", "clock_origin"]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]   # 2010 is not a leap year; eplusout.csv has 8,760 rows
PATCHES = ["version", "dual_setpoint", "meters", "infiltration", "north_axis", "phi_zero", "people",
           "appliances", "relative_paths"]
J_PER_KWH = 3.6e6

RESULTS = []


def emit(status, gate, text):
    RESULTS.append((status, gate))
    print("%s %s %s" % (status, gate, text), flush=True)


def gate(name):
    """decorator: run a gate, turn any exception into NOT_EVALUABLE"""
    def deco(fn):
        def run(*a, **k):
            try:
                return fn(*a, **k)
            except Exception as e:  # noqa
                emit("NOT_EVALUABLE", name, "gate raised %s: %s" % (type(e).__name__, e))
        run.__name__ = fn.__name__
        return run
    return deco


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_kv(p):
    d = {}
    with open(p) as f:
        for line in f:
            if "=" in line:
                k, v = line.rstrip("\n").split("=", 1)
                d[k.strip()] = v.strip()
    return d


def pct(xs, q):
    s = sorted(xs)
    if not s:
        return float("nan")
    k = (len(s) - 1) * q
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


class Pilot:
    def __init__(self, root):
        self.root = root
        with open(os.path.join(root, "run_manifest.csv"), newline="") as f:
            self.rows = list(csv.DictReader(f))
        self.ids = [r["run_id"] for r in self.rows]
        self.cache = {}

    def path(self, rid, *parts):
        return os.path.join(self.root, "runs", rid, *parts)

    def ext(self, rid):
        """extracted hourly series: dict target -> list of floats, plus hour list"""
        if rid in self.cache:
            return self.cache[rid]
        p = os.path.join(self.root, "extracted", rid + ".csv")
        out = {"hour": []}
        for t in TARGETS:
            out[t] = []
        with open(p, newline="") as f:
            rd = csv.reader(f)
            head = next(rd)
            if head != ["hour"] + TARGETS:
                raise ValueError("unexpected header %s in %s" % (head, p))
            for row in rd:
                out["hour"].append(int(row[0]))
                for i, t in enumerate(TARGETS):
                    out[t].append(float(row[i + 1]))
        self.cache[rid] = out
        return out

    def tbl(self, rid):
        """annual end-use table (GJ) from eplustbl.csv: first 'End Uses' table whose header carries [GJ]"""
        p = self.path(rid, "eplus_out", "eplustbl.csv")
        lines = open(p, newline="").read().splitlines()
        res = {"area": None}
        for i, ln in enumerate(lines):
            c = ln.split(",")
            if len(c) > 2 and c[1] == "Total Building Area" and res["area"] is None:
                res["area"] = float(c[2])
        start = None
        hdr_i = None
        for i, ln in enumerate(lines):
            if ln.strip() == "End Uses":
                # the header row is the next non-blank line; the [GJ] one is the energy table (the later one is [W] peak demand)
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and "Electricity [GJ]" in lines[j]:
                    start, hdr_i = i, j
                    break
        if start is None:
            raise ValueError("no End Uses [GJ] table in %s" % p)
        hdr = lines[hdr_i].split(",")
        col = {h.strip(): j for j, h in enumerate(hdr)}
        need = ["Electricity [GJ]", "District Cooling [GJ]", "District Heating [GJ]"]
        for n in need:
            if n not in col:
                raise ValueError("column %s missing in %s" % (n, p))
        rowv = {}
        for ln in lines[hdr_i + 1:hdr_i + 40]:
            c = ln.split(",")
            if len(c) < 3:
                break
            rowv[c[1]] = c
        res["heating_GJ"] = float(rowv["Heating"][col["District Heating [GJ]"]])
        res["cooling_GJ"] = float(rowv["Cooling"][col["District Cooling [GJ]"]])
        res["appliance_GJ"] = float(rowv["Interior Equipment"][col["Electricity [GJ]"]])
        res["facility_GJ"] = float(rowv["Total End Uses"][col["Electricity [GJ]"]])
        return res

    def err(self, rid):
        p = self.path(rid, "eplus_out", "eplusout.err")
        txt = open(p, errors="replace").read()
        completed = "EnergyPlus Completed Successfully" in txt
        severe = sum(1 for ln in txt.splitlines() if "** Severe" in ln)
        fatal = sum(1 for ln in txt.splitlines() if "**  Fatal" in ln)
        return completed, severe, fatal

    def status(self, rid):
        return read_kv(self.path(rid, "status.txt"))

    def time(self, rid):
        """user+sys CPU seconds, wall seconds, max rss kB from /usr/bin/time -v output"""
        txt = open(self.path(rid, "time.txt")).read()
        def num(pat):
            m = re.search(pat, txt)
            return m.group(1) if m else None
        user = float(num(r"User time \(seconds\): ([\d.]+)"))
        sysd = float(num(r"System time \(seconds\): ([\d.]+)"))
        el = num(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([\d:.]+)")
        parts = [float(x) for x in el.split(":")]
        wall = 0.0
        for x in parts:
            wall = wall * 60 + x
        rss = float(num(r"Maximum resident set size \(kbytes\): (\d+)"))
        return user + sysd, wall, rss


def rep1_rows(P):
    """one run per (building, household): the replicate-1 row"""
    return [r for r in P.rows if r["replicate"] == "1"]


@gate("2.1")
def g21(P):
    miss = []
    for r in P.rows:
        rid = r["run_id"]
        for p in (os.path.join(P.root, "extracted", rid + ".csv"), P.path(rid, "status.txt")):
            if not os.path.isfile(p):
                miss.append(p)
    n = len(P.rows)
    ok = (n == 50 and not miss)
    emit("PASS" if ok else "FAIL", "2.1", "manifest_rows=%d files_expected=%d files_missing=%d (extracted csv + status.txt per run) %s" % (
        n, 2 * n, len(miss), miss[:3]))


@gate("2.2")
def g22(P):
    bad = []
    dis = []
    tot_sev = 0
    for rid in P.ids:
        comp, sev, fat = P.err(rid)
        tot_sev += sev
        if not comp or sev != 0 or fat != 0:
            bad.append("%s(completed=%s severe=%d fatal=%d)" % (rid, comp, sev, fat))
        st = P.status(rid)
        if (st.get("completed_successfully") == "yes") != comp or st.get("severe_count") != str(sev):
            dis.append("%s(status: ok=%s sev=%s; err file: ok=%s sev=%d)" % (
                rid, st.get("completed_successfully"), st.get("severe_count"), comp, sev))
    emit("PASS" if not bad else "FAIL", "2.2", "runs_parsed=%d err_files_completed_and_0_severe=%d severe_lines_total=%d bad=%s" % (
        len(P.ids), len(P.ids) - len(bad), tot_sev, bad[:5]))
    emit("INFO" if not dis else "WARN", "2.2b", "status.txt_vs_err_file_disagreements=%d %s" % (len(dis), dis[:5]))


@gate("2.3")
def g23(P):
    bad = []
    nvals = 0
    for rid in P.ids:
        e = P.ext(rid)
        for t in TARGETS:
            if len(e[t]) != 8760:
                bad.append("%s:%s=%d" % (rid, t, len(e[t])))
            nvals += 1
        if e["hour"] != list(range(1, 8761)):
            bad.append("%s:hour_index" % rid)
        if any(math.isnan(v) for t in TARGETS for v in e[t]):
            bad.append("%s:nan" % rid)
    emit("PASS" if not bad else "FAIL", "2.3", "runs=%d target_series_checked=%d rows_each=8760 bad=%s" % (len(P.ids), nvals, bad[:5]))


@gate("2.4")
def g24(P):
    """annual (EnergyPlus annual End Uses table, GJ, 2 decimals) vs hourly sum; tolerance = 0.1 % of annual + 0.005 GJ
    (half a unit of the table's last printed digit)"""
    worst = {"heating_J": (0, None), "cooling_J": (0, None), "appliance_J": (0, None), "facility_elec_J": (0, None)}
    bad = []
    keymap = {"heating_J": "heating_GJ", "cooling_J": "cooling_GJ", "appliance_J": "appliance_GJ", "facility_elec_J": "facility_GJ"}
    for rid in P.ids:
        e = P.ext(rid)
        t = P.tbl(rid)
        for tg, k in keymap.items():
            hourly_gj = math.fsum(e[tg]) / 1e9
            ann = t[k]
            d = abs(hourly_gj - ann)
            tol = 0.001 * abs(ann) + 0.005
            rel = d / ann if ann else 0.0
            if d > tol:
                bad.append("%s:%s hourly=%.4f annual=%.2f GJ" % (rid, tg, hourly_gj, ann))
            if d > worst[tg][0]:
                worst[tg] = (d, (rid, hourly_gj, ann, rel))
    w = "; ".join("%s worst_abs_diff_GJ=%.4f%s" % (tg, v[0], (" (%s hourly %.4f annual %.2f rel %.4f%%)" % (v[1][0], v[1][1], v[1][2], 100 * v[1][3])) if v[1] else "") for tg, v in worst.items())
    emit("PASS" if not bad else "FAIL", "2.4", "runs=%d targets=4 fails=%d %s | %s" % (len(P.ids), len(bad), bad[:4], w))


@gate("2.5")
def g25(P):
    bad = []
    if not P.rows:
        raise ValueError("no manifest rows")
    missing_cols = [c for c in MANIFEST_FIELDS if c not in P.rows[0]]
    if missing_cols:
        bad.append("missing columns %s" % missing_cols)
    for r in P.rows:
        for c in MANIFEST_FIELDS:
            if c in r and (r[c] is None or r[c].strip() == ""):
                bad.append("%s empty %s" % (r.get("run_id"), c))
        if r.get("clock_origin") != "midnight":
            bad.append("%s clock_origin=%s" % (r.get("run_id"), r.get("clock_origin")))
    n_mid = sum(1 for r in P.rows if r.get("clock_origin") == "midnight")
    emit("PASS" if not bad else "FAIL", "2.5", "rows=%d fields=%d/%d clock_origin_midnight=%d bad=%s" % (
        len(P.rows), len(MANIFEST_FIELDS) - len(missing_cols), len(MANIFEST_FIELDS), n_mid, bad[:4]))
    # independent re-hash of what was actually run (manifest could be stale)
    bad2 = []
    for r in P.rows:
        rid = r["run_id"]
        got_idf = md5_file(P.path(rid, "model.idf"))
        if got_idf != r["idf_md5"]:
            bad2.append("%s idf manifest %s vs model.idf %s" % (rid, r["idf_md5"], got_idf))
        ph = glob.glob(P.path(rid, "presence_*.csv"))
        eh = glob.glob(P.path(rid, "elec_*.csv"))
        if len(ph) != 1 or len(eh) != 1:
            bad2.append("%s presence/elec file count %d/%d" % (rid, len(ph), len(eh)))
            continue
        got = sorted([md5_file(ph[0]), md5_file(eh[0])])
        want = sorted(r["schedule_md5"].split(";"))
        if got != want:
            bad2.append("%s schedule md5 manifest %s vs files %s" % (rid, want, got))
    emit("PASS" if not bad2 else "FAIL", "2.5b", "model.idf and schedule md5 re-hashed from the run folder equal the manifest for %d of %d runs %s" % (len(P.rows) - len(bad2), len(P.rows), bad2[:3]))


def groups_by_building(P):
    g = {}
    for r in rep1_rows(P):
        g.setdefault(r["building_id"], []).append(r)
    return g


@gate("3.1")
def g31(P):
    bad = []
    npairs = 0
    per_b = {}
    for b, rs in sorted(groups_by_building(P).items()):
        ser = {}
        for r in rs:
            ser[r["household_id"]] = tuple(round(v, 3) for v in P.ext(r["run_id"])["facility_elec_J"])
        hh = sorted(ser)
        k = 0
        for i in range(len(hh)):
            for j in range(i + 1, len(hh)):
                k += 1
                if ser[hh[i]] == ser[hh[j]]:
                    bad.append("%s:%s==%s" % (b, hh[i], hh[j]))
        npairs += k
        per_b[b] = (len(hh), k)
    emit("PASS" if not bad else "FAIL", "3.1", "buildings=%d pairs_compared=%d identical_pairs=%d %s per_building(households,pairs)=%s" % (
        len(per_b), npairs, len(bad), bad[:4], per_b))


def classes(P, buildings):
    return {b: buildings.get(b, "?") for b in set(r["building_id"] for r in P.rows)}


@gate("3.2")
def g32(P, bcls):
    per_class = {}
    for b, rs in sorted(groups_by_building(P).items()):
        heat_annual = [sum(P.ext(r["run_id"])["heating_J"]) for r in rs]
        tg = "heating_J" if min(heat_annual) > 0 else "cooling_J"
        ser = {}
        for r in rs:
            ser[r["household_id"]] = tuple(round(v, 3) for v in P.ext(r["run_id"])[tg])
        hh = sorted(ser)
        ident = sum(1 for i in range(len(hh)) for j in range(i + 1, len(hh)) if ser[hh[i]] == ser[hh[j]])
        pairs = len(hh) * (len(hh) - 1) // 2
        c = bcls.get(b, "?")
        d = per_class.setdefault(c, [0, 0, set()])
        d[0] += ident
        d[1] += pairs
        d[2].add(tg)
    anyid = any(v[0] for v in per_class.values())
    emit("WARN" if anyid else "PASS", "3.2", "identical_pairs/pairs per class (target used): %s" % (
        {c: "%d/%d (%s)" % (v[0], v[1], "+".join(sorted(v[2]))) for c, v in sorted(per_class.items())}))


@gate("3.3")
def g33(P):
    byin = {}
    for r in P.rows:
        byin.setdefault(r["input_id"], []).append(r["run_id"])
    parts = []
    for iid, rids in sorted(byin.items()):
        if len(rids) < 2:
            continue
        for tg in TARGETS:
            ser = [P.ext(x)[tg] for x in rids]
            spread = max(max(s[i] for s in ser) - min(s[i] for s in ser) for i in range(8760))
            ann = [sum(s) for s in ser]
            mean_ann = sum(ann) / len(ann)
            rel = (max(ann) - min(ann)) / mean_ann if mean_ann else 0.0
            peak = max(max(s) for s in ser)
            parts.append("%s %s repeats=%d max_abs_hourly_spread_J=%.6g annual_spread_rel=%.3g max_hourly_value_J=%.6g" % (iid, tg, len(rids), spread, rel, peak))
    emit("INFO", "3.3", "; ".join(parts))


@gate("3.4")
def g34(P):
    bad = []
    bb = {}
    for r in P.rows:
        bb.setdefault(r["input_id"], set()).add(r["schedule_md5"])
    for iid, s in bb.items():
        if len(s) != 1:
            bad.append("repeats of %s differ %s" % (iid, sorted(s)))
    for b in sorted(set(r["building_id"] for r in P.rows)):
        hh = {}
        for r in P.rows:
            if r["building_id"] == b:
                hh.setdefault(r["household_id"], set()).add(r["schedule_md5"])
        vals = [sorted(v)[0] for v in hh.values() if len(v) == 1]
        if len(set(vals)) != len(vals):
            bad.append("building %s: two households share a schedule md5" % b)
    emit("PASS" if not bad else "FAIL", "3.4", "inputs=%d repeated_inputs=%d bad=%s" % (
        len(bb), sum(1 for x in bb if sum(1 for r in P.rows if r["input_id"] == x) > 1), bad[:4]))


WRAP = [("H1 act2", 10752.104, 4841.148), ("H2 act2", 10462.696, 4886.567),
        ("H1 replicate act2", 10752.104, 4841.148), ("H1 no-act2", 10750.508, 4798.290)]
WRAP_AREA = 55.0   # 2026-09-29_wp1_wrapper.md: ES.ME.SFH.01.Gen.ReEx.001, 55 m2


@gate("4.1")
def g41(P, bcls):
    bycls = {}
    for r in rep1_rows(P):
        rid = r["run_id"]
        e = P.ext(rid)
        area = P.tbl(rid)["area"]
        hq = sum(e["heating_J"]) / J_PER_KWH / area
        cq = sum(e["cooling_J"]) / J_PER_KWH / area
        bycls.setdefault(bcls.get(r["building_id"], "?"), []).append((r["building_id"], area, hq, cq))
    wh = [w[1] / WRAP_AREA for w in WRAP]
    wc = [w[2] / WRAP_AREA for w in WRAP]
    wrap_txt = "; ".join("%s heat %.1f cool %.1f" % (w[0], w[1] / WRAP_AREA, w[2] / WRAP_AREA) for w in WRAP)
    far = []
    lines = []
    for c, v in sorted(bycls.items()):
        hs = [x[2] for x in v]
        cs = [x[3] for x in v]
        hm, cm = statistics.median(hs), statistics.median(cs)
        lines.append("%s n_runs=%d floor_m2=%s heating_kWh_m2 median %.1f [%.1f-%.1f] cooling_kWh_m2 median %.1f [%.1f-%.1f]" % (
            c, len(v), sorted(set(round(x[1], 1) for x in v)), hm, min(hs), max(hs), cm, min(cs), max(cs)))
        if not (0.5 * min(wh) <= hm <= 2 * max(wh)) or not (0.5 * min(wc) <= cm <= 2 * max(wc)):
            far.append(c)
    emit("WARN" if far else "PASS", "4.1", "far (median outside 0.5x..2x of the wrapper values): %s | wrapper kWh/m2 (55 m2 box): %s" % (far, wrap_txt))
    for ln in lines:
        emit("INFO", "4.1d", ln)
    # per building too
    bb = {}
    for c, v in bycls.items():
        for x in v:
            bb.setdefault(x[0], []).append(x)
    emit("INFO", "4.1e", "per building (building class floor_m2 heat cool, median over its households): " + "; ".join(
        "%s %s %.1f %.1f %.1f" % (b, bcls.get(b, "?"), v[0][1], statistics.median([y[2] for y in v]), statistics.median([y[3] for y in v])) for b, v in sorted(bb.items())))


def month_of_hour(h0):
    d = h0 // 24
    m = 0
    while m < 12 and d >= DAYS[m]:
        d -= DAYS[m]
        m += 1
    return m


MONTH_IDX = [month_of_hour(h) for h in range(8760)]


@gate("4.2a")
def g42a(P):
    bad = []
    mx = 0.0
    for r in P.rows:
        e = P.ext(r["run_id"])
        for h in range(8760):
            if MONTH_IDX[h] in (0, 1, 11) and e["cooling_J"][h] != 0.0:
                bad.append("%s" % r["run_id"])
                mx = max(mx, e["cooling_J"][h] / J_PER_KWH)
                break
    emit("PASS" if not bad else "FAIL", "4.2a", "runs_with_cooling_in_Jan_Feb_Dec=%d of %d max_hourly_kWh=%.3f %s" % (len(bad), len(P.rows), mx, bad))


@gate("4.2b")
def g42b(P):
    bad = []
    tot = {}
    for r in P.rows:
        e = P.ext(r["run_id"])
        s = sum(e["heating_J"][h] for h in range(8760) if MONTH_IDX[h] in (6, 7)) / J_PER_KWH
        if s > 0:
            bad.append(r["run_id"])
            tot[r["run_id"]] = round(s, 1)
    emit("WARN" if bad else "PASS", "4.2b", "runs_with_heating_in_Jul_Aug=%d of %d (kWh per run, first 6) %s" % (len(bad), len(P.rows), dict(list(tot.items())[:6])))


@gate("4.3")
def g43(P):
    ok = 0
    n = 0
    skipped = []
    bad = []
    for r in rep1_rows(P):
        iid = r["input_id"]
        pf = os.path.join(P.root, "inputs", iid, "presence_HH_%s.csv" % r["household_id"])
        vals = [float(x) for x in open(pf).read().split("\n")[1:] if x.strip() != ""]
        if len(vals) != 8760:
            raise ValueError("%s has %d presence rows" % (pf, len(vals)))
        el = P.ext(r["run_id"])["facility_elec_J"]
        pres = [el[i] for i in range(8760) if vals[i] > 0.5]
        absn = [el[i] for i in range(8760) if vals[i] <= 0.5]
        if not pres or not absn:
            skipped.append(iid)
            continue
        n += 1
        mp, ma = sum(pres) / len(pres), sum(absn) / len(absn)
        if mp > ma:
            ok += 1
        else:
            bad.append("%s(%.0f<=%.0f)" % (iid, mp, ma))
    frac = ok / n if n else float("nan")
    emit("PASS" if n and frac >= 0.9 else "WARN", "4.3", "inputs_with_presence_and_absence=%d mean_present>mean_absent=%d (%.1f%%) skipped_always_present_or_absent=%d %s failing=%s" % (
        n, ok, 100 * frac, len(skipped), skipped[:4], bad[:5]))


@gate("4.3b")
def g43b(P):
    """diagnostic only (INFO): same test as 4.3 with the presence series shifted by k hours, to show whether the
    electricity and presence files could be on different clocks. k=0 is the real 4.3."""
    rows = rep1_rows(P)
    out = []
    pres = {}
    for r in rows:
        pf = os.path.join(P.root, "inputs", r["input_id"], "presence_HH_%s.csv" % r["household_id"])
        pres[r["input_id"]] = [float(x) for x in open(pf).read().split("\n")[1:] if x.strip() != ""]
    for k in range(-12, 13):
        ok = n = 0
        ratios = []
        for r in rows:
            v = pres[r["input_id"]]
            el = P.ext(r["run_id"])["facility_elec_J"]
            pr = [el[i] for i in range(8760) if v[(i - k) % 8760] > 0.5]
            ab = [el[i] for i in range(8760) if v[(i - k) % 8760] <= 0.5]
            if pr and ab:
                n += 1
                mp, ma = sum(pr) / len(pr), sum(ab) / len(ab)
                ok += (mp > ma)
                ratios.append(mp / ma)
        out.append("k=%+d:%d/%d(ratio %.2f)" % (k, ok, n, statistics.median(ratios)))
    emit("INFO", "4.3b", "inputs passing the 4.3 test when presence is shifted by k hours: " + " ".join(out))


def parse_buildlog(path):
    cur = None
    cnt = {}
    for ln in open(path, encoding="utf-8-sig", errors="replace"):
        ln = ln.rstrip("\n")
        if ln.startswith("== input "):
            cur = ln.split()[2]
            cnt[cur] = {}
        elif ln.startswith("PATCH ") and cur:
            name = ln.split()[1]
            cnt[cur][name] = cnt[cur].get(name, 0) + 1
    return cnt


@gate("P.1")
def gp1(P, buildlog):
    cnt = parse_buildlog(buildlog)
    used = set(r["input_id"] for r in P.rows)
    bad = []
    total = 0
    for iid in sorted(used):
        c = cnt.get(iid)
        if not c:
            bad.append("%s no section in build log" % iid)
            continue
        for p in PATCHES:
            total += c.get(p, 0)
            if c.get(p, 0) != 1:
                bad.append("%s %s x%d" % (iid, p, c.get(p, 0)))
    emit("PASS" if not bad else "FAIL", "P.1", "build log: inputs_in_log=%d inputs_used=%d patch_names_required=%d PATCH_lines_counted=%d (expected %d) missing_or_duplicate=%s" % (
        len(cnt), len(used), len(PATCHES), total, len(used) * len(PATCHES), bad[:5]))


@gate("P.2")
def gp2(P, array_ids):
    n = 0
    bad = []
    for k, rid in enumerate(P.ids, start=1):
        found = False
        for a in array_ids:
            p = os.path.join(P.root, "logs", "task_%s_%d.out" % (a, k))
            if os.path.isfile(p):
                if "PATCH model_idf_rename OK" in open(p, errors="replace").read():
                    found = True
        if found:
            n += 1
        else:
            bad.append(k)
    emit("PASS" if not bad else "FAIL", "P.2", "array logs with 'PATCH model_idf_rename OK': %d of %d (arrays %s) missing_tasks=%s" % (n, len(P.ids), array_ids, bad[:6]))


def parse_sacct(path):
    secs = []
    for ln in open(path):
        m = re.match(r"\s*(\d+)_(\d+)\s+(\S+)\s+(\S+)\s+(\d+):(\d+):(\d+)", ln)
        if m and m.group(3) == "COMPLETED":
            secs.append(int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7)))
    return secs


def parse_size(tok):
    m = re.match(r"([\d.]+)([KMGT]?)", tok)
    mult = {"": 1, "K": 1e3, "M": 1e6, "G": 1e9, "T": 1e12}[m.group(2)]
    return float(m.group(1)) * mult


@gate("5.1")
def g51(P, sacct, n_camp):
    sec = [float(P.status(r)["seconds"]) for r in P.ids]
    cpu, wall, rss = [], [], []
    for r in P.ids:
        c, w, s = P.time(r)
        cpu.append(c); wall.append(w); rss.append(s)
    med = statistics.median(sec)
    p90 = pct(sec, 0.9)
    cpuh = n_camp * med / 3600.0
    txt = "status.txt seconds (whole-second, EnergyPlus only): median=%.1f p90=%.1f max=%.0f | time.txt wall s: median=%.2f p90=%.2f | CPU s (user+sys): median=%.2f p90=%.2f | max_rss_MB: median=%.0f max=%.0f | formula CPU-hours = runs x median_s / 3600 = %d x %.1f / 3600 = %.2f" % (
        med, p90, max(sec), statistics.median(wall), pct(wall, 0.9), statistics.median(cpu), pct(cpu, 0.9),
        statistics.median(rss) / 1024, max(rss) / 1024, n_camp, med, cpuh)
    emit("PASS", "5.1", txt)
    cpuh_wall = n_camp * statistics.median(wall) / 3600.0
    emit("INFO", "5.1b", "sensitivity with time.txt wall median %.2f s: %d x %.2f / 3600 = %.2f CPU-hours" % (statistics.median(wall), n_camp, statistics.median(wall), cpuh_wall))
    if sacct and os.path.isfile(sacct):
        ss = parse_sacct(sacct)
        if ss:
            cpuh_s = n_camp * statistics.median(ss) / 3600.0
            emit("INFO", "5.1c", "sensitivity with whole-task sacct Elapsed (includes copy and extraction; %d tasks) median=%.1f p90=%.1f max=%d s: %d x %.1f / 3600 = %.2f CPU-hours" % (
                len(ss), statistics.median(ss), pct(ss, 0.9), max(ss), n_camp, statistics.median(ss), cpuh_s))
    return cpuh


def preflight(path):
    free = quota_used = quota_limit = None
    for ln in open(path):
        f = ln.split()
        if ln.startswith("filer-speed") and len(f) >= 6:
            free = parse_size(f[3])
        if ln.startswith("/speed-scratch") and len(f) >= 6:
            quota_used, quota_limit = parse_size(f[1]), parse_size(f[3])
    return free, quota_used, quota_limit


@gate("5.2")
def g52(P, n_camp, cpus_list):
    raw = [float(P.status(r)["run_dir_bytes"]) for r in P.ids]
    ex = [float(P.status(r)["extracted_bytes"]) for r in P.ids]
    mraw, mex = statistics.median(raw), statistics.median(ex)
    free, qu, ql = preflight(os.path.join(P.root, "preflight.txt"))
    if free is None or qu is None:
        raise ValueError("could not read the filer-speed row or the /speed-scratch quota row of preflight.txt")
    head = ql - qu
    allruns = n_camp * mex
    txt = ["median raw run folder %.2f MB, median extracted %.3f MB; all runs x extracted = %d x %.3f MB = %.2f GB" % (mraw / 1e6, mex / 1e6, n_camp, mex / 1e6, allruns / 1e9)]
    okall = True
    for c in cpus_list:
        tot = c * mraw + allruns
        ok = tot < free and tot < head
        okall &= ok
        txt.append("%d in flight: %d x %.2f MB + %.2f GB = %.2f GB" % (c, c, mraw / 1e6, allruns / 1e9, tot / 1e9))
    txt.append("preflight (2026-09-29 21:51): filesystem free %.1f TB; user quota used %.1f TB of limit %.1f TB = headroom %.2f TB" % (free / 1e12, qu / 1e12, ql / 1e12, head / 1e12))
    emit("PASS" if okall else "FAIL", "5.2", " | ".join(txt))


@gate("5.3")
def g53(P, n_camp, cpuh, today, deadline):
    lines = []
    anyok = False
    for c in (8, 16, 32):
        wall_h = cpuh / c
        fin = today + datetime.timedelta(hours=wall_h)
        ok = fin.date() <= deadline
        anyok |= ok
        lines.append("%d CPUs: %.2f CPU-h / %d = %.2f h wall, finish %s, %s 11 Oct 2026" % (c, cpuh, c, wall_h, fin.strftime("%Y-%m-%d"), "MEETS" if ok else "MISSES"))
    cut = ""
    if not anyok:
        cut = " | none meets: apply the 2E cut order (computed by the report, not here)"
    emit("PASS" if anyok else "FAIL", "5.3", " | ".join(lines) + cut + " | (compute time only: no queue wait, no per-task start-up, no failed-run repeats)")


def load_buildings(path):
    d = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["building_id"].startswith("es_"):
                d[r["building_id"]] = r["class"]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--buildings", required=True, help="ES-only copy of buildings.csv")
    ap.add_argument("--build-log", required=True)
    ap.add_argument("--sacct", default="")
    ap.add_argument("--arrays", default="1403962,1403963")
    ap.add_argument("--campaign-runs", type=int, default=22160, help="draft run count from spec 2A")
    ap.add_argument("--today", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    print("python", sys.version.split()[0], "root", a.root, flush=True)
    P = Pilot(a.root)
    b = load_buildings(a.buildings)
    bcls = classes(P, b)
    today = datetime.datetime.strptime(a.today, "%Y-%m-%d")
    g21(P); g22(P); g23(P); g24(P); g25(P)
    g31(P); g32(P, bcls); g33(P); g34(P)
    g41(P, bcls); g42a(P); g42b(P); g43(P); g43b(P)
    gp1(P, a.build_log); gp2(P, a.arrays.split(","))
    cpuh = None
    try:
        cpuh = g51(P, a.sacct, a.campaign_runs)
    except Exception as e:  # noqa
        emit("NOT_EVALUABLE", "5.1", "gate raised %s: %s" % (type(e).__name__, e))
    g52(P, a.campaign_runs, [8, 16, 32])
    if cpuh is None:
        emit("NOT_EVALUABLE", "5.3", "no CPU-hours because 5.1 did not run")
    else:
        g53(P, a.campaign_runs, cpuh, today, datetime.date(2026, 10, 11))
    cnt = {}
    for s, g in RESULTS:
        cnt[s] = cnt.get(s, 0) + 1
    print("SUMMARY PASS=%d FAIL=%d WARN=%d INFO=%d NOT_EVALUABLE=%d" % (cnt.get("PASS", 0), cnt.get("FAIL", 0), cnt.get("WARN", 0), cnt.get("INFO", 0), cnt.get("NOT_EVALUABLE", 0)))
    bad = [g for s, g in RESULTS if g in FAIL_GATES and s in ("FAIL", "NOT_EVALUABLE")]
    print("FAIL-severity gates not passing: %s" % bad)
    # every FAIL-severity gate must have produced a line (a gate that printed nothing is not a pass)
    seen = set(g for s, g in RESULTS)
    silent = sorted(FAIL_GATES - seen)
    if silent:
        print("FAIL-severity gates that printed nothing: %s" % silent)
    sys.exit(1 if (bad or silent) else 0)


if __name__ == "__main__":
    main()
