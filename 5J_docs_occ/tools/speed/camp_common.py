# -*- coding: utf-8 -*-
"""5J Step 3 campaign, shared code (Speed only; Spain + Italy only, never a UK file).

Paths (all overridable by environment, used by the smoke job to work in a scratch tree):
  CAMP_ROOT    outputs: plan/ done/ runs/ extracted/ failed/ logs/           default /speed-scratch/o_iseri/5J/campaign/
  CAMP_TABLES  folder holding campaign_runs_es.csv, campaign_runs_it.csv     default <R>/in/
  CAMP_HH      household input folders <cc>_<hid>/ and <cc>_avg/ (read-only) default /speed-scratch/o_iseri/5J/households/inputs/
  CAMP_PLAN    plan folder                                                    default <CAMP_ROOT>/plan/
Static inputs (always in R): in/buildings_es_it.csv, in/climates_es_it.csv, in/dwelling_count_<cc>.csv,
in/archetype_parameters_<cc>.csv, epw/*.epw, repo/ (builder copies).
"""
import csv, gzip, hashlib, io, json, os, re, subprocess, sys, time, traceback, platform
import numpy as np
import pandas as pd

R = "/speed-scratch/o_iseri/5J/campaign/"
ROOT = os.environ.get("CAMP_ROOT", R)
if not ROOT.endswith("/"):
    ROOT += "/"
TABLES = os.environ.get("CAMP_TABLES", R + "in/")
HHROOT = os.environ.get("CAMP_HH", "/speed-scratch/o_iseri/5J/households/inputs/")
if not HHROOT.endswith("/"):
    HHROOT += "/"
if not TABLES.endswith("/"):
    TABLES += "/"
PLAN = os.environ.get("CAMP_PLAN", ROOT + "plan/")
if not PLAN.endswith("/"):
    PLAN += "/"
REPO = R + "repo/"
EP = ("/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus")
EP_VERSION = "EnergyPlus-23.1.0-87ed9199d4"
J_PER_KWH = 3.6e6
COP_H = 3.0
COP_C = 3.0
TARGETS = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
KWH_PER_GJ = 1000.0 / 3.6
TARGET_BLOCK_S = 2400.0
ARRAYS = ["es_madrid_2010", "es_valencia_2010", "es_seville_2010", "it_bologna_2014", "it_turin_2014", "it_milan_2014"]
PATCH_NAMES = ["mz_geometry", "mz_areas", "mz_windows", "mz_mass", "mz_pairs", "mz_people", "mz_appliances", "mz_outputs", "mz_k"]
CLOCK_ORIGIN = "midnight"
BUILDER_FILES = [REPO + "5J_docs_occ/tools/5thJ_idf_mz.py", REPO + "5J_docs_occ/tools/5thJ_idf.py",
                 REPO + "4J_docs_occ/tools/4thJ_step8_idf.py"]


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


_MD5 = {}


def md5(p):
    st = os.stat(p)
    key = (p, st.st_size, st.st_mtime_ns)
    if key not in _MD5:
        h = hashlib.md5()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        _MD5[key] = h.hexdigest()
    return _MD5[key]


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


# ------------------------------------------------------------------------------------------------ tables
def read_csv(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def load_runs():
    """All runs of the two frozen tables, in table order. Spain and Italy only (asserted)."""
    runs = []
    for cc in ("es", "it"):
        p = TABLES + "campaign_runs_%s.csv" % cc
        if not os.path.exists(p):
            continue
        for r in read_csv(p):
            assert r["country"] == cc and r["run_id"].startswith(cc + "_"), ("not a %s row" % cc, r["run_id"])
            runs.append(r)
    return runs


_STATIC = {}


def static():
    if not _STATIC:
        bt = {}
        for r in read_csv(R + "in/buildings_es_it.csv"):
            assert r["country"] in ("es", "it"), r
            bt[r["building_id"]] = r
        cl = {}
        for r in read_csv(R + "in/climates_es_it.csv"):
            assert r["country"] in ("es", "it"), r
            cl[r["climate_id"]] = r
        _STATIC["bt"] = bt
        _STATIC["cl"] = cl
    return _STATIC


def epw_path(climate_id):
    c = static()["cl"][climate_id]
    return R + "epw/" + re.split(r"[\\/]", c["path"])[-1]


def epw_expected_md5(climate_id):
    return static()["cl"][climate_id]["md5"]


def est_seconds(run):
    """Per-run estimate, design section 7: class medians SFH 4, TH 4, MFH 14, AB 19 s; 1.0 s per zone above 18 zones."""
    nd = int(run["n_dwellings"])
    if run["class"] in ("SFH", "TH"):
        return 4.0
    if nd > 18:
        return 1.0 * nd
    return 14.0 if run["class"] == "MFH" else 19.0


# ------------------------------------------------------------------------------------------------ households
def hh_folder(token, cc):
    return HHROOT + (token if token.startswith(cc + "_") else "%s_%s" % (cc, token)) + "/"


def hh_dict(token, cc):
    fdir = hh_folder(token, cc)
    j = json.load(io.open(fdir + "household.json", encoding="utf-8"))
    return {"hid": j["hid"], "fold": cc, "n_members": float(j["n_members"]),
            "presence_csv": fdir + j["presence_file"], "appliance_csv": fdir + j["elec_file"],
            "appliance_peak_w": float(j["appliance_peak_w"]), "peak_w_source": fdir + "household.json"}


def hh_md5s(tokens, cc):
    out = {}
    for t in sorted(set(tokens)):
        fdir = hh_folder(t, cc)
        out[t] = {f: md5(fdir + f) for f in sorted(os.listdir(fdir))}
    return out


def parse_placement(s):
    d = {}
    for item in s.split(";"):
        j, t = item.split(":", 1)
        d[int(j)] = t
    return d


def cache_key(run):
    """md5 of: building row, k, placement, every household file, EPW, builder files, 4thJ_step8_idf.py, EnergyPlus version."""
    st = static()
    cc = run["country"]
    brow = st["bt"][run["building_id"]]
    plc = parse_placement(run["placement"])
    trow = None
    for r in _tabula_rows(cc):
        if r["Code_Building"] == brow["archetype_code"]:
            trow = r
    payload = {"building_row": brow, "tabula_row": trow, "k": run["k"], "n_floors": run["n_floors"],
               "placement": run["placement"], "households": hh_md5s(list(plc.values()), cc),
               "epw_md5": md5(epw_path(run["climate_id"])),
               "builder_md5": {os.path.basename(p): md5(p) for p in BUILDER_FILES}, "energyplus": EP_VERSION}
    return md5_bytes(json.dumps(payload, sort_keys=True).encode("utf-8"))


_TAB = {}


def _tabula_rows(cc):
    if cc not in _TAB:
        sys.path.insert(0, REPO + "5J_docs_occ/tools")
        import importlib
        mz = importlib.import_module("5thJ_idf_mz")
        _TAB[cc] = mz._s8.load_rows(R + "in/", cc)[0]
    return _TAB[cc]


def done_json(run_id):
    return ROOT + "done/%s.json" % run_id


def is_done(run_id, key):
    p = done_json(run_id)
    if not os.path.exists(p):
        return False
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return False
    return d.get("status") == "pass" and d.get("cache_key") == key


# ------------------------------------------------------------------------------------------------ build
_MZ = {}


def mzmod():
    if "mz" not in _MZ:
        sys.path.insert(0, REPO + "5J_docs_occ/tools")
        import importlib
        mz = importlib.import_module("5thJ_idf_mz")
        mz._j5.TOOLS_4J = REPO + "4J_docs_occ/tools"
        _MZ["mz"] = mz
    return _MZ["mz"]


def build_run(run):
    """Returns (idf_text, meta, patch_names_present, area_gate_failures)."""
    mz = mzmod()
    st = static()
    cc = run["country"]
    brow = st["bt"][run["building_id"]]
    rows = _tabula_rows(cc)
    row = {r["Code_Building"]: r for r in rows}[brow["archetype_code"]]
    F = int(run["n_floors"])
    k, _n, kline = mz.k_from_tabula(R + "in/dwelling_count_%s.csv" % cc, row["Code_Building"], F)
    if k != int(run["k"]):
        raise RuntimeError("k from TABULA %d != k in the run table %s" % (k, run["k"]))
    plc = parse_placement(run["placement"])
    cache = {}
    placement = {}
    for j, t in plc.items():
        if t not in cache:
            cache[t] = hh_dict(t, cc)
        placement[j] = cache[t]
    idf, meta = mz.build_mz(row, k, placement, float(brow["infiltration_ach"]), float(brow["north_axis_deg"]))
    got = [ln.split()[1] for ln in meta["patch_lines"]] + ["mz_k"]
    print(kline)
    for ln in meta["patch_lines"]:
        print(ln)
    res = mz.check_area_gates(idf, row)
    bad = ["%s %s" % (s, g) for s, g, _ in res if s != "PASS"]
    return idf, meta, got, bad


# ------------------------------------------------------------------------------------------------ checks
def check_err(text):
    """(ok, reasons) from the text of eplusout.err."""
    why = []
    if "EnergyPlus Completed Successfully" not in text:
        why.append("no 'EnergyPlus Completed Successfully'")
    nsev = len(re.findall(r"\*\* Severe", text))
    if nsev:
        why.append("%d Severe line(s)" % nsev)
    return (not why), why


def tbl_enduse(p):
    lines = io.open(p, encoding="utf-8", errors="replace").read().splitlines()
    i = [n for n, ln in enumerate(lines) if ln.strip() == "End Uses"]
    if not i:
        raise RuntimeError("no End Uses table in %s" % p)
    hdr = next(csv.reader([lines[i[0] + 2]]))
    gj = [c for c, h in enumerate(hdr) if "[GJ]" in h]
    out = {}
    for ln in lines[i[0] + 3:i[0] + 20]:
        r = next(csv.reader([ln]))
        if len(r) > 1 and r[1] in ("Heating", "Cooling", "Interior Equipment"):
            out[{"Heating": "heating", "Cooling": "cooling", "Interior Equipment": "equipment"}[r[1]]] = sum(float(r[c]) for c in gj)
    if sorted(out) != ["cooling", "equipment", "heating"]:
        raise RuntimeError("End Uses rows not found in %s: %s" % (p, sorted(out)))
    return out


def g24_facility(df, tbl):
    """Gate 2.4 as in 5thJ_mz_pilot_check.py: hourly sums vs the End Uses table, tol 0.1 % or the table rounding 0.005 GJ."""
    hs = {"heating": df["heating_kwh"].sum() / KWH_PER_GJ, "cooling": df["cooling_kwh"].sum() / KWH_PER_GJ,
          "equipment": df["equipment_kwh"].sum() / KWH_PER_GJ}
    bad, txt = [], []
    for k in ("heating", "cooling", "equipment"):
        a, b = hs[k], tbl[k]
        rel = abs(a - b) / b if b else abs(a)
        if not (rel < 1e-3 or abs(a - b) <= 0.0051):
            bad.append(k)
        txt.append("%s hourly_sum=%.4f GJ tbl=%.2f GJ rel=%.2e" % (k, a, b, rel))
    a = hs["equipment"] + hs["heating"] / COP_H + hs["cooling"] / COP_C
    b = tbl["equipment"] + tbl["heating"] / COP_H + tbl["cooling"] / COP_C
    rel = abs(a - b) / b if b else abs(a)
    if not (rel < 1e-3 or abs(a - b) <= 0.0051):
        bad.append("total_elec")
    txt.append("total_elec hourly_sum=%.4f GJ tbl-derived=%.4f GJ rel=%.2e" % (a, b, rel))
    return ("PASS" if not bad else "FAIL"), "; ".join(txt)


def g24_dwelling(df, raw, meta):
    """Gate 2.4b: each dwelling's annual = its own zone columns of eplusout.csv (tol 1e-6)."""
    zone_dw = meta["zone_dwelling"]
    worst, bad = 0.0, []
    cols_by = {}
    for c in raw.columns:
        cols_by.setdefault(c.split(":")[0], []).append(c)
    for j in sorted(set(zone_dw.values())):
        zs = [z for z in zone_dw if zone_dw[z] == j]
        sub = df[df["dwelling"] == j]
        for tgt, var, pre in (("heating_kwh", "Zone Ideal Loads Supply Air Total Heating Energy", "IDEAL_"),
                              ("cooling_kwh", "Zone Ideal Loads Supply Air Total Cooling Energy", "IDEAL_"),
                              ("equipment_kwh", "Electric Equipment Electricity Energy", "EQ_")):
            cols = []
            for z in zs:
                cols += [c for c in cols_by.get(pre + z, []) if c.startswith("%s%s:%s [J]" % (pre, z, var))]
            if len(cols) != len(zs):
                bad.append("dw%d %s cols=%d zones=%d" % (j, tgt, len(cols), len(zs)))
                continue
            ref = float(raw[cols].to_numpy().sum()) / J_PER_KWH
            got = float(sub[tgt].sum())
            rel = abs(got - ref) / ref if ref else abs(got)
            worst = max(worst, rel)
            if rel > 1e-6:
                bad.append("dw%d %s got=%.4f ref=%.4f rel=%.2e" % (j, tgt, got, ref, rel))
    return ("PASS" if not bad else "FAIL"), "worst_rel=%.2e %s" % (worst, "; ".join(bad[:4]))


def check_rows(df, n_dw):
    """8,760 rows per dwelling per target, hour 1..8760, no NaN."""
    bad = []
    dws = sorted(df["dwelling"].unique())
    if len(dws) != n_dw:
        bad.append("dwellings=%d expected %d" % (len(dws), n_dw))
    if len(df) != 8760 * len(dws):
        bad.append("rows=%d expected %d" % (len(df), 8760 * len(dws)))
    for j in dws:
        sub = df[df["dwelling"] == j]
        if len(sub) != 8760 or not np.array_equal(sub["hour"].to_numpy(), np.arange(1, 8761)):
            bad.append("dwelling %s rows=%d or hour gap" % (j, len(sub)))
            continue
        for t in TARGETS:
            v = sub[t].to_numpy(dtype=float)
            if len(v) != 8760 or not np.isfinite(v).all():
                bad.append("dwelling %s target %s not 8760 finite" % (j, t))
    return ("PASS" if not bad else "FAIL"), "dwellings=%d rows=%d %s" % (len(dws), len(df), "; ".join(bad[:4]))


# ------------------------------------------------------------------------------------------------ extraction (as mzp_extract.py)
VARS = [
    ("Zone Ideal Loads Supply Air Total Heating Energy", "heating_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Total Cooling Energy", "cooling_kwh", "sumJ"),
    ("Electric Equipment Electricity Energy", "equipment_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Sensible Heating Energy", "heating_sens_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Latent Heating Energy", "heating_lat_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Sensible Cooling Energy", "cooling_sens_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Latent Cooling Energy", "cooling_lat_kwh", "sumJ"),
    ("Zone Ideal Loads Zone Total Heating Energy", "zoneside_heating_kwh", "sumJ"),
    ("Zone Ideal Loads Zone Total Cooling Energy", "zoneside_cooling_kwh", "sumJ"),
    ("People Total Heating Energy", "people_heat_kwh", "sumJ"),
    ("Zone Infiltration Sensible Heat Gain Energy", "infil_gain_kwh", "sumJ"),
    ("Zone Infiltration Sensible Heat Loss Energy", "infil_loss_kwh", "sumJ"),
    ("Zone Windows Total Heat Gain Energy", "win_gain_kwh", "sumJ"),
    ("Zone Windows Total Heat Loss Energy", "win_loss_kwh", "sumJ"),
    ("Zone Windows Total Transmitted Solar Radiation Energy", "win_solar_kwh", "sumJ"),
    ("Zone Heating Setpoint Not Met Time", "unmet_heat_zone_h", "sum"),
    ("Zone Cooling Setpoint Not Met Time", "unmet_cool_zone_h", "sum"),
    ("Zone Mean Air Temperature", "t_air_c", "wmean"),
    ("Zone Operative Temperature", "t_op_c", "wmean"),
    ("Zone Air Relative Humidity", "rh_pct", "wmean"),
]
VMAP = {v[0]: v for v in VARS}
COLRE = re.compile(r"^(.*?):(.+?) \[([^\]]*)\]\(Hourly\)\s*$")
ZRE = re.compile(r"(Z_F\d\d_D\d\d)$")


def extract_run(raw, meta, run, csv_gz_path, dw_path):
    """Write <run_id>.csv.gz + <run_id>.dwellings.csv exactly as mzp_extract.py (content), gzip mtime 0. Returns the dataframe."""
    df = raw
    n = len(df)
    zone_dw = meta["zone_dwelling"]
    zarea = meta["zone_floor_areas"]
    dws = sorted(set(zone_dw.values()))
    acc = {j: {} for j in dws}
    wsum = {j: sum(zarea[z] for z in zone_dw if zone_dw[z] == j) for j in dws}
    for c in df.columns[1:]:
        mm = COLRE.match(c)
        if not mm:
            continue
        key, var, unit = mm.groups()
        if var not in VMAP:
            continue
        zm = ZRE.search(key)
        if not zm:
            continue
        z = zm.group(1)
        j = zone_dw[z]
        _, name, kind = VMAP[var]
        v = df[c].to_numpy(dtype=float)
        if kind == "sumJ":
            v = v / J_PER_KWH
        elif kind == "wmean":
            v = v * (zarea[z] / wsum[j])
        acc[j][name] = acc[j].get(name, 0.0) + v
    rid = run["run_id"]
    hdr = ["# 5J multi-zone campaign, run %s, building %s, extracted by camp_common.py (same content layout as mzp_extract.py)" % (rid, run["building_id"]),
           "# units: *_kwh = kWh per hour of that dwelling (sum of its zones); t_air_c, t_op_c degC and rh_pct %% are "
           "floor-area-weighted means over the dwelling's zones; unmet_*_zone_h = sum over zones of hours",
           "# total_elec_kwh = equipment_kwh + heating_kwh / %.1f + cooling_kwh / %.1f ; COP_H = COP_C = 3.0 ASSUMED "
           "(manager, pending the author's numbers)" % (COP_H, COP_C),
           "# heating_kwh / cooling_kwh = Zone Ideal Loads Supply Air Total Heating / Cooling Energy ; "
           "equipment_kwh = Electric Equipment Electricity Energy ; no Lights object exists, so no lighting column",
           "# hour = 1..%d of the year, hour 1 ends at 01:00 on 1 January (clock origin midnight)" % n]
    frames = []
    for j in dws:
        a = acc[j]
        d = {"dwelling": np.full(n, j, dtype=int), "hour": np.arange(1, n + 1)}
        d["heating_kwh"] = a["heating_kwh"]
        d["cooling_kwh"] = a["cooling_kwh"]
        d["equipment_kwh"] = a["equipment_kwh"]
        d["total_elec_kwh"] = a["equipment_kwh"] + a["heating_kwh"] / COP_H + a["cooling_kwh"] / COP_C
        for _, name, _k in VARS[3:]:
            if name in a:
                d[name] = a[name]
        frames.append(pd.DataFrame(d))
    out = pd.concat(frames, ignore_index=True)
    with open(csv_gz_path, "wb") as raw_fh:
        gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw_fh, mtime=0)
        txt = io.TextIOWrapper(gz, encoding="utf-8", newline="")
        txt.write("\n".join(hdr) + "\n")
        out.to_csv(txt, index=False, float_format="%.8g")
        txt.flush()
        txt.detach()
        gz.close()
    k = int(meta["k"])
    F = int(meta["floors"])
    spans = run["class"] in ("SFH", "TH")
    plc = parse_placement(run["placement"])
    with io.open(dw_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["dwelling", "hid", "floor_min", "floor_max", "position", "col", "end_dwelling", "floor_area_m2", "n_zones", "zones"])
        for j in dws:
            zs = sorted(z for z in zone_dw if zone_dw[z] == j)
            fl = sorted(int(z[3:5]) for z in zs)
            if spans:
                pos_, col, endd = "all", 0, 1
            else:
                f = fl[0]
                pos_ = "ground" if f == 0 else ("top" if f == F - 1 else "middle")
                col = j - f * k
                endd = 1 if (col == 0 or col == k - 1) else 0
            w.writerow([j, plc[j], fl[0], fl[-1], pos_, col, endd, "%.4f" % wsum[j], len(zs), ";".join(zs)])
    return out
