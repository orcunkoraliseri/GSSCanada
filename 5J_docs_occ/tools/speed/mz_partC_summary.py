# 5J multizone Part C, job 3: read the 16 runs, carry-over gate, sanity table, output-presence gate. Spain only.
import csv, io, json, os, re, statistics, sys, platform
R = "/speed-scratch/o_iseri/5J/multizone/"
sys.path.insert(0, R + "repo/5J_docs_occ/tools")
print("python", sys.version.split()[0], "host", platform.node())
import importlib
mz = importlib.import_module("5thJ_idf_mz")
J = 3.6e6
BUILDINGS = ["es_B07", "es_B16", "es_B21", "es_B33", "es_B37"]
lay = json.load(io.open(R + "building_layout.json"))
man = list(csv.DictReader(io.open(R + "run_manifest.csv")))


def status(rd):
    st = {}
    p = rd + "status.txt"
    if os.path.exists(p):
        for ln in io.open(p):
            if "=" in ln:
                a, b = ln.strip().split("=", 1)
                st[a] = b
    return st


PAT = re.compile(r"^(.*?):(Zone Ideal Loads Supply Air Total (Heating|Cooling) Energy|Electric Equipment Electricity Energy)"
                 r" \[J\]\(Hourly\)")


def read_run(rid):
    rd = R + "runs/%s/" % rid
    st = status(rd)
    out = {"run": rid, "status": st}
    err = rd + "eplus_out/eplusout.err"
    csvp = rd + "eplus_out/eplusout.csv"
    if not (os.path.exists(err) and os.path.exists(csvp)):
        out["error"] = "no eplusout.err/csv"
        return out
    e = io.open(err, encoding="utf-8", errors="replace").read()
    out["ok"] = "EnergyPlus Completed Successfully" in e
    out["severe"] = len(re.findall(r"\*\* Severe", e))
    sums = {}
    n = 0
    with io.open(csvp, encoding="utf-8") as fh:
        rdr = csv.reader(fh)
        hdr = next(rdr)
        cols = {}
        for j, h in enumerate(hdr):
            m = PAT.match(h)
            if m:
                cols[j] = (m.group(1), {"Heating": "heat", "Cooling": "cool"}.get(m.group(3), "elec"))
                sums[cols[j]] = 0.0
        for r in rdr:
            n += 1
            for j, key in cols.items():
                sums[key] += float(r[j])
    sums = {k: v / J for k, v in sums.items()}
    out["rows"] = n
    out["sums"] = sums
    for t in ("heat", "cool", "elec"):
        out[t] = sum(v for (k, tt), v in sums.items() if tt == t)
    return out


res = {m["run_id"]: read_run(m["run_id"]) for m in man}
print("== RUN TABLE ==")
secs_mz, secs_all = [], []
ok_runs = True
for m in man:
    r = res[m["run_id"]]
    st = r["status"]
    if "error" in r:
        print("RUN %s ERROR %s status=%s" % (m["run_id"], r["error"], st))
        ok_runs = False
        continue
    good = r["ok"] and r["severe"] == 0 and st.get("rc") == "0"
    ok_runs &= good
    print("RUN %s rc=%s completed=%s severe=%d rows=%d seconds=%s max_rss_kb=%s du_sk=%s eso_bytes=%s csv_bytes=%s "
          "heat=%.3f cool=%.3f elec=%.3f %s"
          % (m["run_id"], st.get("rc"), r["ok"], r["severe"], r["rows"], st.get("seconds"), st.get("max_rss_kb"),
             st.get("run_folder_du_sk"), st.get("eso_bytes"), st.get("csv_bytes"), r["heat"], r["cool"], r["elec"],
             "PASS" if good else "FAIL"))
    secs_all.append(float(st.get("seconds", 0)))
    if m["kind"] == "mz":
        secs_mz.append(float(st.get("seconds", 0)))
print("ALL_RUNS_COMPLETED_0_SEVERE", "PASS" if ok_runs else "FAIL")
if secs_mz:
    print("SECONDS mz median %.1f max %.1f | all runs median %.1f max %.1f"
          % (statistics.median(secs_mz), max(secs_mz), statistics.median(secs_all), max(secs_all)))
print("ZONES", json.dumps({b: lay[b]["zones"] for b in lay}))

print("== CARRY-OVER: collapse vs single-zone wrapper (same first household), tolerance 0.5 % ==")


def rel(a, b):
    return abs(a - b) / abs(b) if b else abs(a)


for b in BUILDINGS:
    c, s = res.get(b + "__collapse"), res.get(b + "__single")
    if not c or not s or "error" in c or "error" in s:
        print("FAIL carry_over %s cannot evaluate (run missing)" % b)
        continue
    for k in ("heat", "cool"):
        rr = rel(c[k], s[k])
        print("%s carry_over_%s %s collapse=%.4f single=%.4f rel=%.4g" % ("PASS" if rr <= 0.005 else "FAIL", k, b, c[k], s[k], rr))
c, s = res.get("es_B21__collapse_uwall110"), res.get("es_B21__single")
if c and s and "error" not in c and "error" not in s:
    for k in ("heat", "cool"):
        rr = rel(c[k], s[k])
        print("SEENFAIL3 %s carry_over_%s es_B21 (collapse with U_wall x1.10) collapse=%.4f single=%.4f rel=%.4g"
              % ("PASS" if rr <= 0.005 else "FAIL", k, c[k], s[k], rr))

print("== SANITY (INFO, no pass band) ==")
for b in BUILDINGS:
    r = res.get(b + "__mz")
    s = res.get(b + "__single")
    if not r or "error" in r:
        print("INFO %s mz run missing" % b)
        continue
    meta = json.load(io.open(R + "runs/%s__mz/meta.json" % b))
    F = meta["floors"]
    areas = meta["zone_floor_areas"]
    zf = {z: int(z[3:5]) for z in meta["zones"]}
    grp = {"ground": [], "middle": [], "top": []}
    for z in meta["zones"]:
        key = "IDEAL_" + z.upper()
        h = r["sums"].get((key, "heat"), 0.0)
        cl = r["sums"].get((key, "cool"), 0.0)
        g = "ground" if zf[z] == 0 else ("top" if zf[z] == F - 1 else "middle")
        grp[g].append((h / areas[z], cl / areas[z]))
    line = []
    for g in ("ground", "middle", "top"):
        if grp[g]:
            line.append("%s heat %.2f cool %.2f kWh/m2 (n=%d)" % (g, statistics.mean(x[0] for x in grp[g]),
                                                                  statistics.mean(x[1] for x in grp[g]), len(grp[g])))
        else:
            line.append("%s n/a" % g)
    print("INFO %s class=%s floors=%d zones=%d | %s" % (b, meta["cls"], F, len(meta["zones"]), " | ".join(line)))
    if s and "error" not in s:
        print("INFO %s whole building mz/single: heating %.1f / %.1f kWh ratio %.3f | cooling %.1f / %.1f kWh ratio %.3f"
              % (b, r["heat"], s["heat"], r["heat"] / s["heat"] if s["heat"] else float("nan"),
                 r["cool"], s["cool"], r["cool"] / s["cool"] if s["cool"] else float("nan")))

print("== OUTPUT PRESENCE (one multi-zone run: es_B21__mz; .rdd then .eso dictionary) ==")
rd = R + "runs/es_B21__mz/eplus_out/"
rdd = io.open(rd + "eplusout.rdd", encoding="utf-8", errors="replace").read() if os.path.exists(rd + "eplusout.rdd") else ""
mdd = io.open(rd + "eplusout.mdd", encoding="utf-8", errors="replace").read() if os.path.exists(rd + "eplusout.mdd") else ""
eso_dict = []
if os.path.exists(rd + "eplusout.eso"):
    with io.open(rd + "eplusout.eso", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if ln.startswith("End of Data Dictionary"):
                break
            eso_dict.append(ln)
eso_dict = "".join(eso_dict)
print("FILES rdd_bytes=%d mdd_bytes=%d eso_dict_bytes=%d" % (len(rdd), len(mdd), len(eso_dict)))
for v in mz.OUTPUT_VARIABLES:
    in_rdd = v in rdd
    in_eso = v in eso_dict
    if in_eso:
        print("PASS output_present %s (eso dictionary yes, rdd %s)" % (v, "yes" if in_rdd else "no"))
    elif v == "Lights Electricity Energy":
        print("INFO output_present %s absent (no Lights object written; rdd %s)" % (v, "yes" if in_rdd else "no"))
    else:
        print("FAIL output_present %s (eso dictionary no, rdd %s)" % (v, "yes" if in_rdd else "no"))
for mname in mz.OUTPUT_METERS:
    in_eso = (mname in eso_dict)
    if in_eso:
        print("PASS output_present meter %s (eso dictionary yes)" % mname)
    elif mname == "InteriorLights:Electricity":
        print("INFO output_present meter %s absent (no Lights object)" % mname)
    else:
        print("FAIL output_present meter %s" % mname)
