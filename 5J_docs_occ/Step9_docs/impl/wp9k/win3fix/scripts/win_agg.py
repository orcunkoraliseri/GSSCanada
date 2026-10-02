# 5J Step 9k aggregator (fixed base _win_2026-10-03). Gates G-c1..G-c6 as before, plus G-c7 fast-setting check, G-c8 azimuth, timing.
# EXIT CODE MEANING: 0 = every section ran and the tables + GATE SUMMARY were written (the verdicts are the text, not the exit code);
#                    4 = the tables were written but at least one section CRASHED (its gate is NOT_EVALUABLE in the summary, never PASS);
#                    anything else (1, 2, ...) = the aggregator itself crashed before the summary = EVERY gate NOT_EVALUABLE.
# OUTCOMES per gate: NOT_RUN (did not run: input missing) | PASS (ran and passed) | FAIL (ran and failed) | NOT_EVALUABLE (section crashed).
# CONTROLS: a control line says FIRED (the planted fault was caught = the gate can see) or DID_NOT_FIRE (the gate is blind).
import csv, json, math, os, re, statistics, sys, traceback
B = os.environ.get("W9I_BASE", "/speed-scratch/o_iseri/5J/step9c/win3fix/")
man = list(csv.DictReader(open(B + "manifest.csv")))
R = {}
for r in man:
    try:
        R[(r["stem"], r["run"])] = json.load(open(B + "results/%s.json" % r["task"]))
    except Exception:
        pass
stems = []
for r in man:
    if r["stem"] not in [s for s, _ in stems]:
        stems.append((r["stem"], r))
GATES = {}
CRASH = []


def setg(name, outcome, detail=""):
    GATES[name] = (outcome, detail)


def g(s, k):
    return R.get((s, k))


GATE_OF = {"sec_c1": ["G-c1", "G-c1-control(P1)"], "sec_c2": ["G-c2", "G-c2-control(P2)"], "sec_c3": ["G-c3"], "sec_c4": ["G-c4"], "sec_c4s": ["G-c4s", "G-c4s-control(D-vs-R1-expectation)"],
           "sec_c5": ["G-c5", "G-c5-triangle-severe"], "sec_c7": ["G-c7", "G-c7-control(D-vs-O)", "G-c7-control(planted+5%)"],
           "sec_c8": ["G-c8", "G-c8-control(+180)", "G-c8-control(inward walls)"]}
for _l in GATE_OF.values():
    for _k in _l:
        GATES[_k] = ("NOT_RUN", "no result read")
GATES["G-c6"] = ("NOT_RUN", "zone-map gate was seen failing and passing on the desktop (P3, earlier state file); not part of this array")


def section(fn):
    def w():
        print("")
        try:
            fn()
        except Exception:
            CRASH.append(fn.__name__)
            print("SECTION CRASHED:", fn.__name__)
            traceback.print_exc(file=sys.stdout)
            for k in GATE_OF.get(fn.__name__, []):
                if GATES[k][0] in ("NOT_RUN", "PASS", "FIRED"):
                    setg(k, "NOT_EVALUABLE", "section crashed: " + fn.__name__)
    w.__name__ = fn.__name__
    return w


print("# step9k gate table (auto), fixed base _win_2026-10-03")
print("EXIT CODE MEANING: 0 = all sections ran, tables + GATE SUMMARY written (verdicts are the text); 4 = written but a section CRASHED (NOT_EVALUABLE); other = aggregator crashed = every gate NOT_EVALUABLE")


@section
def sec_c1():
    v1 = []
    print("## G-c1 reproduction (annual heating R1 vs R0, tolerance 0.1 %)")
    for s, r in stems:
        a, b = g(s, "R0"), g(s, "R1")
        if not a or not b or a.get("heat_kwh") is None or b.get("heat_kwh") is None:
            print(s, "NOT_EVALUABLE (missing run or column)")
            continue
        d = 100 * (b["heat_kwh"] - a["heat_kwh"]) / a["heat_kwh"]
        ok = abs(d) <= 0.1
        v1.append(ok)
        print(s, r["district"], "R0 %.3f R1 %.3f diff %.4f %% -> %s" % (a["heat_kwh"], b["heat_kwh"], d, "PASS" if ok else "FAIL"))
    print("unplanted verdict count: %d PASS of %d" % (sum(v1), len(v1)))
    if v1:
        GATES["G-c1"] = ("PASS" if all(v1) and len(v1) == len(stems) else "FAIL", "%d PASS of %d" % (sum(v1), len(v1)))
    for s, r in stems:
        p = g(s, "P1")
        if p:
            a = g(s, "R0")
            if not a or p.get("heat_kwh") is None:
                print("P1", s, "NOT_EVALUABLE")
                continue
            d = 100 * (p["heat_kwh"] - a["heat_kwh"]) / a["heat_kwh"]
            fired = abs(d) > 0.1
            print("P1 planted", s, "P1 %.3f R0 %.3f diff %.4f %% -> %s (planted fault: FAIL is the wanted outcome)"
                  % (p["heat_kwh"], a["heat_kwh"], d, "FAIL" if fired else "PASS = FAULT NOT SEEN"))
            GATES["G-c1-control(P1)"] = ("FIRED" if fired else "DID_NOT_FIRE", "diff %.4f %%" % d)


@section
def sec_c2():
    print("## G-c2 windows, read by EnergyPlus itself (tolerance 1 % against window_m2 of windows.csv; verdict on D and O; R0 has no table by design; R1, DF, OF, P2 shown as information)")
    W = {}
    for d in ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2"):
        for q in csv.DictReader(open(B + "windows_%s.csv" % d)):
            W[q["stem"]] = q
    v2 = []
    for s, r in stems:
        exp = float(W[s]["window_m2"])
        for k in ("R0", "R1", "D", "O", "DF", "OF", "P2"):
            x = g(s, k)
            if not x:
                continue
            for src in ("window_opening_area_m2", "fen_total_area_m2"):
                got = x.get(src)
                if got is None:
                    print(s, k, src, "NOT_EVALUABLE (no value parsed%s)" % ("; R0 = delivered file, no table by design" if k == "R0" else ""), x.get("tbl_error") or "")
                    continue
                d_ = 100 * (got - exp) / exp
                ok = abs(d_) <= 1.0
                tag = "PASS" if ok else "FAIL"
                if k == "P2":
                    tag += " (planted fault: FAIL is the wanted outcome)"
                if k in ("D", "O") and src == "window_opening_area_m2":
                    v2.append(ok)
                print(s, k, src, "EnergyPlus %.4f windows.csv %.4f diff %.4f %% -> %s" % (got, exp, d_, tag))
    print("unplanted verdict count (D and O, Window-Wall Ratio table): %d PASS of %d" % (sum(v2), len(v2)))
    if v2:
        GATES["G-c2"] = ("PASS" if all(v2) and len(v2) == 2 * len(stems) else "FAIL", "%d PASS of %d (wanted %d runs)" % (sum(v2), len(v2), 2 * len(stems)))
    p2 = [x for s_, _r in stems for x in [g(s_, "P2")] if x]
    if p2 and p2[0].get("window_opening_area_m2") is not None:
        s_ = p2[0]["stem"]
        e_ = float(W[s_]["window_m2"])
        pass2 = abs(100 * (p2[0]["window_opening_area_m2"] - e_) / e_) <= 1.0
        dd = g(s_, "D")
        d_ok = dd is not None and dd.get("window_opening_area_m2") is not None and abs(100 * (dd["window_opening_area_m2"] - e_) / e_) <= 1.0
        diff = int(d_ok) - int(pass2)
        print("planted run (P2 replaces D of its building): %d PASS of %d; differs from the unplanted count by %d (wanted: 1)" % (sum(v2) - int(d_ok) + int(pass2), len(v2), diff))
        GATES["G-c2-control(P2)"] = ("FIRED" if diff == 1 else "DID_NOT_FIRE", "count differs by %d (wanted 1)" % diff)


@section
def sec_c3():
    print("## G-c3 occupancy edits (run O; OF shown as information)")
    v = []
    for s, r in stems:
        for k in ("O", "OF"):
            o = g(s, k)
            if not o:
                print(s, k, "NOT_EVALUABLE")
                continue
            nf = int(r["n_flats"])
            okc = o["n_PEOPLE"] == nf and o["n_ELECTRICEQUIPMENT"] == nf and o["n_OTHEREQUIPMENT"] == 0
            dev = None if o.get("ee_kwh") is None or not o.get("ee_expected_kwh") else 100 * (o["ee_kwh"] - o["ee_expected_kwh"]) / o["ee_expected_kwh"]
            ok = okc and dev is not None and abs(dev) <= 0.5
            if k == "O":
                v.append(ok)
            print(s, k, "flats", nf, "People", o["n_PEOPLE"], "ElecEq", o["n_ELECTRICEQUIPMENT"], "OtherEq", o["n_OTHEREQUIPMENT"],
                  "ee_kwh", o.get("ee_kwh"), "expected", o.get("ee_expected_kwh"), "dev %", dev, "hourly max rel dev", o.get("ee_hourly_max_rel_dev"), "->", "PASS" if ok else "FAIL")
    if v:
        GATES["G-c3"] = ("PASS" if all(v) and len(v) == len(stems) else "FAIL", "%d PASS of %d" % (sum(v), len(v)))


@section
def sec_c4():
    print("## G-c4 cooling (kWh; D and O must be > 0 in at least one zone, R0 and R1 none)")
    v = []
    for s, r in stems:
        row = []
        for k in ("R0", "R1", "D", "O", "DF", "OF"):
            x = g(s, k)
            row.append("%s=%s(zones>0: %s)" % (k, None if not x else x.get("cool_kwh"), None if not x else x.get("cool_zones_positive")))
        d, o, r0, r1 = g(s, "D"), g(s, "O"), g(s, "R0"), g(s, "R1")
        if not (d and o and r0 and r1):
            print(s, " ".join(row), "-> NOT_EVALUABLE")
            continue
        ok = all((x.get("cool_zones_positive") or 0) > 0 for x in (d, o)) and all(not (x.get("cool_kwh") or 0) for x in (r0, r1))
        v.append(ok)
        print(s, " ".join(row), "->", "PASS" if ok else "FAIL")
    if v:
        GATES["G-c4"] = ("PASS" if all(v) and len(v) == len(stems) else "FAIL", "%d PASS of %d" % (sum(v), len(v)))


@section
def sec_c4s():
    print("## G-c4s structural cooling-off count (lines containing 'EU_CoolingOff,' in the IDF: R0 and R1 = zones + 1, D O DF OF = 1; zones = lines starting 'Zone,')")
    v = []
    ctl = []
    for r in man:
        if r["run"] not in ("R0", "R1", "D", "O", "DF", "OF"):
            continue
        p = B + "%s/idfs/%s_%s.idf" % (r["district"], r["stem"], r["run"])
        if not os.path.exists(p):
            print(r["stem"], r["run"], "NOT_EVALUABLE: IDF missing", p)
            continue
        tx = open(p, encoding="utf-8", errors="replace").read().split(chr(10))
        n_off = sum(1 for l in tx if "EU_CoolingOff," in l)
        n_z = sum(1 for l in tx if re.match(r"^ZONE,", l.strip(), re.I))
        want = n_z + 1 if r["run"] in ("R0", "R1") else 1
        ok = n_off == want
        v.append(ok)
        print(r["stem"], r["run"], "EU_CoolingOff lines", n_off, "zones", n_z, "expected", want, "->", "PASS" if ok else "FAIL")
        if r["run"] == "D":
            ctl.append((n_off, n_z + 1))
    print("unplanted verdict count: %d PASS of %d" % (sum(v), len(v)))
    if v:
        GATES["G-c4s"] = ("PASS" if all(v) and len(v) == 6 * len(stems) else "FAIL", "%d PASS of %d (wanted %d files)" % (sum(v), len(v), 6 * len(stems)))
    if ctl:
        bad = sum(1 for a, b in ctl if a != b)
        print("CONTROL D files read against the R1 expectation (zones + 1): rejected %d of %d (wanted: all)" % (bad, len(ctl)))
        GATES["G-c4s-control(D-vs-R1-expectation)"] = ("FIRED" if bad == len(ctl) else "DID_NOT_FIRE", "rejected %d of %d" % (bad, len(ctl)))


@section
def sec_c5():
    print("## G-c5 clean runs (exit 0, completed, zero severe, grep -i 'invalid|not found' empty). NO warning is whitelisted.")
    v = []
    for r in man:
        x = R.get((r["stem"], r["run"]))
        if not x:
            print(r["stem"], r["run"], "NOT_EVALUABLE (no result)")
            continue
        ok = x["rc"] == 0 and x["completed"] and x["severe"] == 0 and x["invalid_or_not_found"] == 0
        v.append(ok)
        print(r["stem"], r["run"], "rc", x["rc"], "completed", x["completed"], "severe", x["severe"], "warnings", x["warnings"],
              "invalid/not found", x["invalid_or_not_found"], x["invalid_or_not_found_first"], "->", "PASS" if ok else "FAIL")
        if x["severe"] > 0:
            print("   NOT CLEAN: %d Severe line(s); first lines:" % x["severe"])
            for l_ in (x.get("severe_text") or [])[:20]:
                print("     " + l_)
    if v:
        bad_runs = [r["stem"] + "_" + r["run"] for r in man if (r["stem"], r["run"]) in R and not (R[(r["stem"], r["run"])]["rc"] == 0 and R[(r["stem"], r["run"])]["completed"] and R[(r["stem"], r["run"])]["severe"] == 0 and R[(r["stem"], r["run"])]["invalid_or_not_found"] == 0)]
        GATES["G-c5"] = ("PASS" if all(v) and len(v) == len(man) else "FAIL", "%d PASS of %d runs (read %d); not clean: %s" % (sum(v), len(man), len(v), ",".join(bad_runs) or "none"))
    tri = [x for k in ("D", "O") for x in [g("1271cddbf6bd1e8a", k)] if x]
    if tri:
        seen = len(tri) == 2 and all(any("degenerate" in l.lower() for l in (x.get("severe_text") or [])) for x in tri)
        print("triangle building 1271cddbf6bd1e8a: Severe 'degenerate surfaces' line still shows in D and O: %s" % ("YES" if seen else "NO"))
        GATES["G-c5-triangle-severe"] = ("PASS" if seen else "FAIL", "degenerate Severe line present in D and O of 1271cddbf6bd1e8a: %s" % seen)


def pct(base, new):
    if base is None or new is None:
        return None
    if base == 0:
        return 0.0 if new == 0 else float("inf")
    return 100.0 * (new - base) / base


def equip(x):
    return (x.get("ee_kwh") or 0.0) + (x.get("oe_kwh") or 0.0)


def fast_comparator(pairs):
    """pairs: (label, base_json, new_json). PASS only if median |change| <= 1 % and worst <= 3 % for heating AND cooling,
    and equipment equal within 1e-6 relative in every pair."""
    h = [abs(pct(b["heat_kwh"], n["heat_kwh"])) for _, b, n in pairs]
    c = [abs(pct(b["cool_kwh"], n["cool_kwh"])) for _, b, n in pairs]
    eq = []
    for _, b, n in pairs:
        e0, e1 = equip(b), equip(n)
        eq.append(abs(e1 - e0) <= 1e-6 * max(abs(e0), 1e-12))
    ok = (statistics.median(h) <= 1.0 and max(h) <= 3.0 and statistics.median(c) <= 1.0 and max(c) <= 3.0 and all(eq))
    return ok, h, c, eq


@section
def sec_c7():
    print("## G-c7 fast-setting check: DF vs D and OF vs O (shadow update every 20 days + sizing off). PASS only if median |change| <= 1 % and worst <= 3 % for heating AND cooling, equipment equal within 1e-6 relative")
    pairs = []
    for s, r in stems:
        for b, n in (("D", "DF"), ("O", "OF")):
            xb, xn = g(s, b), g(s, n)
            if xb and xn and None not in (xb.get("heat_kwh"), xn.get("heat_kwh"), xb.get("cool_kwh"), xn.get("cool_kwh")):
                pairs.append(("%s %s vs %s" % (s, n, b), xb, xn))
                print(s, "%s vs %s" % (n, b), "heat %.3f -> %.3f (%.4f %%) cool %.3f -> %.3f (%.4f %%) equipment %.6f -> %.6f"
                      % (xb["heat_kwh"], xn["heat_kwh"], pct(xb["heat_kwh"], xn["heat_kwh"]), xb["cool_kwh"], xn["cool_kwh"], pct(xb["cool_kwh"], xn["cool_kwh"]), equip(xb), equip(xn)))
    if len(pairs) != 2 * len(stems):
        print("only %d of %d pairs available -> NOT_RUN" % (len(pairs), 2 * len(stems)))
        return
    ok, h, c, eq = fast_comparator(pairs)
    print("heating: median %.4f %% worst %.4f %% | cooling: median %.4f %% worst %.4f %% | equipment equal in %d of %d pairs -> %s"
          % (statistics.median(h), max(h), statistics.median(c), max(c), sum(eq), len(eq), "PASS" if ok else "FAIL"))
    GATES["G-c7"] = ("PASS" if ok else "FAIL", "heat median %.4f worst %.4f; cool median %.4f worst %.4f; equipment equal %d/%d"
                     % (statistics.median(h), max(h), statistics.median(c), max(c), sum(eq), len(eq)))
    cp = []
    for s, r in stems:
        d, o = g(s, "D"), g(s, "O")
        if d and o and None not in (d.get("cool_kwh"), o.get("cool_kwh")):
            cp.append(("%s O vs D" % s, d, o))
    if cp:
        ok2, h2, c2, eq2 = fast_comparator(cp)
        print("CONTROL same comparator on D vs O (%d pairs): heating median %.2f %% worst %.2f %%, cooling median %.2f %% worst %.2f %%, equipment equal %d of %d -> %s (wanted: FAIL)"
              % (len(cp), statistics.median(h2), max(h2), statistics.median(c2), max(c2), sum(eq2), len(eq2), "PASS = COMPARATOR BLIND" if ok2 else "FAIL"))
        GATES["G-c7-control(D-vs-O)"] = ("DID_NOT_FIRE" if ok2 else "FIRED", "D vs O comparator verdict %s" % ("PASS" if ok2 else "FAIL"))
    pl = [(a, b, dict(n)) for a, b, n in pairs]
    pl[0][2]["heat_kwh"] = pl[0][2]["heat_kwh"] * 1.05
    ok3, h3, _, _ = fast_comparator(pl)
    print("CONTROL planted +5 %% on heating of %s: worst %.4f %% -> %s (wanted: FAIL)" % (pl[0][0], max(h3), "PASS = COMPARATOR BLIND" if ok3 else "FAIL"))
    GATES["G-c7-control(planted+5%)"] = ("DID_NOT_FIRE" if ok3 else "FIRED", "worst %.4f %%" % max(h3))


def cdiff(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def newell_az(idf_text, name):
    m = re.search(r"BuildingSurface:Detailed,\s*" + re.escape(name) + r"\s*,(.*?);", idf_text, re.S | re.I)
    if not m:
        raise RuntimeError("wall %r not found in the IDF" % name)
    body = "".join(l.split("!")[0] for l in m.group(1).split("\n"))
    f = [x.strip() for x in body.split(",")]
    co = f[10:]
    if len(co) % 3 or len(co) < 9:
        raise RuntimeError("bad coordinate list for %r (%d values)" % (name, len(co)))
    v = [(float(co[i]), float(co[i + 1]), float(co[i + 2])) for i in range(0, len(co), 3)]
    sx = sy = 0.0
    for i in range(len(v)):
        x1, y1, z1 = v[i]
        x2, y2, z2 = v[(i + 1) % len(v)]
        sx += y1 * z2 - z1 * y2
        sy += z1 * x2 - x1 * z2
    return math.degrees(math.atan2(sx, sy)) % 360.0


def eplus_azimuths(tp):
    rows = list(csv.reader(open(tp, newline="", encoding="utf-8", errors="replace")))
    out = {}
    for k, r in enumerate(rows):
        if r and r[0].strip() == "Opaque Exterior":
            j = k + 1
            while j < len(rows) and not [x for x in rows[j] if x.strip()]:
                j += 1
            hdr = rows[j]
            ia = [i for i, h in enumerate(hdr) if h.strip().startswith("Azimuth")]
            if not ia:
                raise RuntimeError("no Azimuth column in Opaque Exterior of %s" % tp)
            for r2 in rows[j + 1:]:
                if len([x for x in r2 if x.strip()]) < 3:
                    break
                nm = (r2[1] if not r2[0].strip() else r2[0]).strip().upper()
                try:
                    out[nm] = float(r2[ia[0]])
                except (ValueError, IndexError):
                    pass
            break
    if not out:
        raise RuntimeError("no Opaque Exterior rows read from %s" % tp)
    return out


@section
def sec_c8():
    print("## G-c8 azimuth (FINDING 5J-5, item 6): one outdoor wall per building that the rebase check calls outward (point test and edge test agree): EnergyPlus azimuth in eplustbl.csv (Opaque Exterior, run D) vs the Newell azimuth from the vertices of the D IDF; tolerance 1 degree")
    az = list(csv.DictReader(open(B + "azcheck.csv")))
    mains, ctls, inward = [], [], []
    for a in az:
        s = a["stem"]
        row = [x for _s, x in stems if _s == s][0]
        idf = B + "%s/idfs/%s_D.idf" % (row["district"], s)
        tp = B + "runs/%s_D/eplustbl.csv" % s
        if not os.path.exists(tp):
            print(s, a["role"], "NOT_EVALUABLE: no eplustbl.csv for D")
            continue
        E = eplus_azimuths(tp)
        nm = a["wall_name"].upper()
        if nm not in E:
            raise RuntimeError("wall %s not in the EnergyPlus table of %s" % (a["wall_name"], s))
        text = open(idf, encoding="utf-8", errors="replace").read()
        nz = newell_az(text, a["wall_name"])
        geom = float(a["geom_outward_az"])
        if cdiff(nz, float(a["newell_az"])) > 0.01:
            raise RuntimeError("my Newell azimuth %.4f differs from the rebase table %.4f for %s" % (nz, float(a["newell_az"]), a["wall_name"]))
        if a["role"] == "main":
            d = cdiff(E[nm], nz)
            ok = d <= 1.0
            mains.append(ok)
            print(s, "main wall", a["wall_name"], "geometric outward %.4f Newell %.4f EnergyPlus %.4f diff %.4f deg -> %s" % (geom, nz, E[nm], d, "PASS" if ok else "FAIL"))
            ctls.append(cdiff(E[nm], (geom + 180.0) % 360.0) <= 1.0)
        else:
            dd = cdiff(E[nm], geom)
            inward.append(dd > 1.0)
            print(s, "control wall (still inward by both tests)", a["wall_name"], "geometric outward %.4f EnergyPlus %.4f diff %.1f deg -> %s (wanted: FAIL, about 180)" % (geom, E[nm], dd, "PASS = BLIND" if dd <= 1.0 else "FAIL"))
    if mains:
        GATES["G-c8"] = ("PASS" if all(mains) and len(mains) == len(stems) else "FAIL", "%d PASS of %d walls" % (sum(mains), len(mains)))
        print("CONTROL comparator against (outward + 180) on the same main walls: accepted %d of %d -> %s (wanted: FAIL for all)" % (sum(ctls), len(ctls), "FAIL" if not any(ctls) else "PASS = BLIND"))
        GATES["G-c8-control(+180)"] = ("FIRED" if not any(ctls) else "DID_NOT_FIRE", "accepted %d of %d" % (sum(ctls), len(ctls)))
    if not inward:
        GATES["G-c8-control(inward walls)"] = ("NOT_RUN", "no control_inward row in azcheck.csv: no wall of these 6 buildings is called inward by both tests on the final base (walls fixed); the +180 control above is the only G-c8 control")
        print("CONTROL inward walls: NOT_RUN (no still-inward wall in the six buildings; walls fixed)")
    if inward:
        GATES["G-c8-control(inward walls)"] = ("FIRED" if all(inward) else "DID_NOT_FIRE", "%d of %d still-inward walls rejected" % (sum(inward), len(inward)))


@section
def sec_t():
    print("## Timing: wall seconds per run type and building; speed-up D/DF and O/OF")
    for s, r in stems:
        w = {k: g(s, k)["wall_s"] for k in ("R0", "R1", "D", "O", "DF", "OF", "P1", "P2") if g(s, k)}
        sp = ""
        if "D" in w and "DF" in w and w["DF"] > 0:
            sp += " D/DF %.2fx" % (w["D"] / w["DF"])
        if "O" in w and "OF" in w and w["OF"] > 0:
            sp += " O/OF %.2fx" % (w["O"] / w["OF"])
        print(s, r["district"], r["cls"], "flats", r["n_flats"], " ".join("%s=%s" % (k, v) for k, v in w.items()) + sp)


sec_c1(); sec_c2(); sec_c3(); sec_c4(); sec_c4s(); sec_c5(); sec_c7(); sec_c8(); sec_t()
print("\n## GATE SUMMARY (NOT_RUN = did not run; PASS = ran and passed; FAIL = ran and failed; NOT_EVALUABLE = section crashed; control: FIRED = planted fault caught, DID_NOT_FIRE = gate blind)")
for k, (o, d) in GATES.items():
    print("GATE %-28s %-14s %s" % (k, o, d))
print("RESULT FILES READ: %d of %d" % (len(R), len(man)))
sys.exit(4 if CRASH else 0)
