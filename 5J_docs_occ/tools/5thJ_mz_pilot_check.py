# -*- coding: utf-8 -*-
"""5J multi-zone re-pilot checker (Spain only). Runs on Speed via sbatch (tools/speed/mzp_check.sbatch).

One line per gate:  PASS|FAIL|WARN|INFO|NOT_EVALUABLE <gate> <numbers>
then                SUMMARY PASS=.. FAIL=.. WARN=.. NOT_EVALUABLE=..

EXIT CODE MEANING (written first, 2026-09-30):
  exit 0  only when FAIL = 0 AND NOT_EVALUABLE = 0 among the FAIL-severity gates (2.1, 2.2, 2.3, 2.4, 2.4b, 3.1, 4.3 and
          the three seen-failing self-tests). WARN and INFO gates (3.3, 4.1, 5.1, 5.2, 5.3) never decide the exit code.
  exit 1  any FAIL, or any NOT_EVALUABLE among the FAIL-severity gates, or the script crashed (a crash is NOT a pass).
A gate that did not run is NOT_EVALUABLE, never silently absent. Lines starting SEENFAIL are the self-tests on scratch
copies; each must show FAIL (a seen-failing test that does NOT fail is itself counted as a FAIL gate).
"""
import csv, gzip, io, json, math, os, re, shutil, statistics, sys, traceback, platform
import numpy as np
import pandas as pd

R = "/speed-scratch/o_iseri/5J/mz_pilot/"
MZ0 = "/speed-scratch/o_iseri/5J/multizone/"
REPO = R + "repo/"
sys.path.insert(0, REPO + "5J_docs_occ/tools")
TARGETS = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]
KWH_PER_GJ = 1000.0 / 3.6

GATES = []          # (status, gate, sev)


def emit(status, gate, text, sev="FAIL"):
    print("%s %s %s" % (status, gate, text))
    GATES.append((status, gate, sev))


def seenfail(gate, status, text):
    print("SEENFAIL %s %s %s" % (gate, status, text))
    if status != "FAIL":
        emit("FAIL", "seenfail_%s_did_not_fail" % gate, "the planted defect was NOT caught: %s" % text)


def read_kv(p):
    d = {}
    if os.path.exists(p):
        for ln in io.open(p, encoding="utf-8", errors="replace"):
            if "=" in ln:
                a, b = ln.strip().split("=", 1)
                d[a] = b
    return d


def load_ext(p):
    return pd.read_csv(p, comment="#")


def tbl_enduse(p):
    """{'heating': GJ, 'cooling': GJ, 'equipment': GJ} from the End Uses table of eplustbl.csv (sum of the [GJ] columns)."""
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


# ---------------------------------------------------------------- gate functions (used by the seen-failing tests too)
def g22(err_path, status_kv):
    e = io.open(err_path, encoding="utf-8", errors="replace").read() if os.path.exists(err_path) else None
    if e is None:
        return "FAIL", "no err file", False
    ok = "EnergyPlus Completed Successfully" in e
    sev = len(re.findall(r"\*\* Severe  \*\*", e))
    agree = True
    if status_kv:
        agree = (status_kv.get("severe_count") == str(sev)) and ((status_kv.get("completed_successfully") == "yes") == ok)
    return ("PASS" if (ok and sev == 0) else "FAIL"), "completed=%s severe=%d status_txt_agrees=%s" % (ok, sev, agree), agree


def g31_within(df, hid_of):
    """Dwellings with different households must differ on equipment and on heating. Returns (pairs, identical list)."""
    dws = sorted(df["dwelling"].unique())
    ser = {}
    for j in dws:
        s = df[df["dwelling"] == j].sort_values("hour")
        ser[j] = (s["equipment_kwh"].to_numpy(), s["heating_kwh"].to_numpy())
    pairs, ident = 0, []
    for a in range(len(dws)):
        for b in range(a + 1, len(dws)):
            ja, jb = dws[a], dws[b]
            if hid_of[ja] == hid_of[jb]:
                continue
            pairs += 1
            for t, nm in ((0, "equipment"), (1, "heating")):
                if np.array_equal(ser[ja][t], ser[jb][t]):
                    ident.append((ja, jb, nm))
    return pairs, ident


def g24_facility(df, tbl):
    """Extracted facility sums (kWh -> GJ) against eplustbl End Uses. Tolerance: 0.1 % or the table's own rounding (0.005 GJ)."""
    hs = {"heating": df["heating_kwh"].sum() / KWH_PER_GJ, "cooling": df["cooling_kwh"].sum() / KWH_PER_GJ,
          "equipment": df["equipment_kwh"].sum() / KWH_PER_GJ}
    bad, txt = [], []
    for k in ("heating", "cooling", "equipment"):
        a, b = hs[k], tbl[k]
        rel = abs(a - b) / b if b else abs(a)
        ok = rel < 1e-3 or abs(a - b) <= 0.0051
        if not ok:
            bad.append(k)
        txt.append("%s hourly_sum=%.4f GJ tbl=%.2f GJ rel=%.2e" % (k, a, b, rel))
    a = hs["equipment"] + hs["heating"] / 3.0 + hs["cooling"] / 3.0
    b = tbl["equipment"] + tbl["heating"] / 3.0 + tbl["cooling"] / 3.0
    rel = abs(a - b) / b
    if not (rel < 1e-3 or abs(a - b) <= 0.0051):
        bad.append("total_elec")
    txt.append("total_elec hourly_sum=%.4f GJ tbl-derived=%.4f GJ rel=%.2e" % (a, b, rel))
    return ("PASS" if not bad else "FAIL"), "; ".join(txt)


def g24_dwelling(df, csvp, meta):
    """Per dwelling: extracted annual vs the sum of its zones' own columns in eplusout.csv (separate code path)."""
    raw = pd.read_csv(csvp)
    zone_dw = meta["zone_dwelling"]
    worst, bad = 0.0, []
    for j in sorted(set(zone_dw.values())):
        zs = [z for z in zone_dw if zone_dw[z] == j]
        for tgt, var, pre in (("heating_kwh", "Zone Ideal Loads Supply Air Total Heating Energy", "IDEAL_"),
                              ("cooling_kwh", "Zone Ideal Loads Supply Air Total Cooling Energy", "IDEAL_"),
                              ("equipment_kwh", "Electric Equipment Electricity Energy", "EQ_")):
            cols = [c for c in raw.columns if any(c.startswith("%s%s:%s [J]" % (pre, z, var)) for z in zs)]
            if len(cols) != len(zs):
                bad.append("dw%d %s cols=%d zones=%d" % (j, tgt, len(cols), len(zs)))
                continue
            ref = float(raw[cols].to_numpy().sum()) / 3.6e6
            got = float(df[df["dwelling"] == j][tgt].sum())
            rel = abs(got - ref) / ref if ref else abs(got)
            worst = max(worst, rel)
            if rel > 1e-6:
                bad.append("dw%d %s got=%.4f ref=%.4f rel=%.2e" % (j, tgt, got, ref, rel))
    return ("PASS" if not bad else "FAIL"), "worst_rel=%.2e %s" % (worst, "; ".join(bad[:4]))


def main():
    print("python", sys.version.split()[0], "pandas", pd.__version__, "host", platform.node())
    man = list(csv.DictReader(io.open(R + "run_manifest.csv", encoding="utf-8")))
    RUN = {m["run_id"]: m for m in man}
    META = {m["run_id"]: json.load(io.open(R + "runs/%s/meta.json" % m["run_id"], encoding="utf-8")) for m in man}
    os.makedirs(R + "report", exist_ok=True)
    os.makedirs(R + "seenfail_chk", exist_ok=True)
    hid_of = {}
    for m in man:
        hid_of[m["run_id"]] = {int(x.split(":")[0]): x.split(":")[1] for x in m["placement"].split(";")}

    # 2.1 ----------------------------------------------------------------------------------------
    miss = [m["run_id"] for m in man if not (os.path.exists(R + "extracted/%s.csv.gz" % m["run_id"])
                                              and os.path.exists(R + "extracted/%s.dwellings.csv" % m["run_id"]))]
    miss_st = [m["run_id"] for m in man if not os.path.exists(R + "runs/%s/status.txt" % m["run_id"])]
    emit("PASS" if (not miss and not miss_st and len(man) == 36) else "FAIL", "2.1",
         "extracted %d/%d, status files %d/%d missing_extracted=%s missing_status=%s"
         % (len(man) - len(miss), len(man), len(man) - len(miss_st), len(man), miss, miss_st))
    EXT = {m["run_id"]: load_ext(R + "extracted/%s.csv.gz" % m["run_id"]) for m in man if m["run_id"] not in miss}
    SIDE = {m["run_id"]: list(csv.DictReader(io.open(R + "extracted/%s.dwellings.csv" % m["run_id"], encoding="utf-8")))
            for m in man if m["run_id"] not in miss}
    ST = {m["run_id"]: read_kv(R + "runs/%s/status.txt" % m["run_id"]) for m in man}

    # 2.2 ----------------------------------------------------------------------------------------
    bad, disagree = [], []
    for m in man:
        rid = m["run_id"]
        s, t, agree = g22(R + "runs/%s/eplus_out/eplusout.err" % rid, ST[rid])
        if s != "PASS":
            bad.append((rid, t))
        if not agree:
            disagree.append(rid)
    emit("PASS" if not bad else "FAIL", "2.2", "err files parsed %d, bad=%s, status.txt disagrees with err in %s"
         % (len(man), bad[:5], disagree))

    # 2.3 ----------------------------------------------------------------------------------------
    bad, total_dw = [], 0
    for rid, df in EXT.items():
        for j, g in df.groupby("dwelling"):
            total_dw += 1
            for t in TARGETS:
                if g[t].notna().sum() != 8760 or len(g) != 8760 or sorted(g["hour"]) != list(range(1, 8761)):
                    bad.append((rid, int(j), t))
    emit("PASS" if not bad else "FAIL", "2.3", "dwelling series checked %d x 4 targets; rows != 8760 or NaN or hour gap in %d cases %s"
         % (total_dw, len(bad), bad[:4]))

    # 2.4 ----------------------------------------------------------------------------------------
    bad, worst = [], []
    for m in man:
        rid = m["run_id"]
        if rid not in EXT:
            continue
        tbl = tbl_enduse(R + "runs/%s/eplus_out/eplustbl.csv" % rid)
        s, t = g24_facility(EXT[rid], tbl)
        if s != "PASS":
            bad.append((rid, t))
    emit("PASS" if not bad else "FAIL", "2.4", "facility level: extracted hourly sums vs eplustbl.csv End Uses (tol 0.1 %% or the table rounding "
         "0.005 GJ), %d runs, failures=%s" % (len(EXT), bad[:3]))
    bad, worstrel = [], 0.0
    for m in man:
        rid = m["run_id"]
        if rid not in EXT:
            continue
        s, t = g24_dwelling(EXT[rid], R + "runs/%s/eplus_out/eplusout.csv" % rid, META[rid])
        if s != "PASS":
            bad.append((rid, t))
    emit("PASS" if not bad else "FAIL", "2.4b", "dwelling level: extracted annual vs the sum of the dwelling's own zone columns in "
         "eplusout.csv (tol 1e-6), %d runs, failures=%s" % (len(EXT), bad[:3]))

    # 3.1 ----------------------------------------------------------------------------------------
    per_class = {}
    for rid, df in EXT.items():
        if RUN[rid]["n_dwellings"] != "1":
            pr, idn = g31_within(df, hid_of[rid])
            c = per_class.setdefault(RUN[rid]["class"], [0, 0, 0])
            c[0] += 1
            c[1] += pr
            c[2] += len(idn)
    tot_ident = sum(v[2] for v in per_class.values())
    emit("PASS" if (per_class and tot_ident == 0) else ("FAIL" if per_class else "NOT_EVALUABLE"), "3.1a_within_run",
         "per class (runs, dwelling pairs with different households, identical pairs on equipment or heating): %s"
         % json.dumps(per_class, sort_keys=True))
    by_b = {}
    for rid, df in EXT.items():
        r = RUN[rid]
        if r["class"] in ("SFH", "TH") and r["replicate"] == "0":
            by_b.setdefault(r["building_id"], []).append((hid_of[rid][0], df))
    pairs = ident = 0
    for b, lst in by_b.items():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                if lst[a][0] == lst[c][0]:
                    continue
                pairs += 1
                for t in ("equipment_kwh", "heating_kwh"):
                    x = lst[a][1].sort_values("hour")[t].to_numpy()
                    y = lst[c][1].sort_values("hour")[t].to_numpy()
                    if np.array_equal(x, y):
                        ident += 1
    emit("PASS" if (pairs > 0 and ident == 0) else ("FAIL" if pairs else "NOT_EVALUABLE"), "3.1b_across_SFH_TH_runs",
         "buildings %s, run pairs with different households %d, identical (equipment or heating) %d" % (sorted(by_b), pairs, ident))

    # 3.3 replicates -------------------------------------------------------------------------------
    groups = {}
    for rid, r in RUN.items():
        if r["replicate"] != "0":
            groups.setdefault((r["building_id"], r["placement"]), []).append(rid)
    for (b, pl), rids in sorted(groups.items()):
        base = [rid for rid, r in RUN.items() if r["building_id"] == b and r["placement"] == pl and r["replicate"] == "0"]
        parts = []
        worst_abs = 0.0
        for t in TARGETS:
            arr = np.vstack([EXT[r_].sort_values(["dwelling", "hour"])[t].to_numpy() for r_ in rids if r_ in EXT])
            sp = arr.max(axis=0) - arr.min(axis=0)
            ann = arr.reshape(arr.shape[0], -1).sum(axis=1)
            rel = (ann.max() - ann.min()) / ann.mean() if ann.mean() else 0.0
            parts.append("%s max_abs_hourly_spread=%.3g kWh annual_rel_spread=%.3g" % (t, sp.max(), rel))
            worst_abs = max(worst_abs, float(sp.max()))
        allr = rids + base
        b_ok = True
        if base and base[0] in EXT:
            arr0 = EXT[base[0]].sort_values(["dwelling", "hour"])[TARGETS].to_numpy()
            for r_ in rids:
                if r_ in EXT and not np.array_equal(arr0, EXT[r_].sort_values(["dwelling", "hour"])[TARGETS].to_numpy()):
                    b_ok = False
        emit("PASS" if (worst_abs == 0.0 and b_ok) else "WARN", "3.3_replicates_%s" % b,
             "%d repeats (%s) %s; original run %s identical to repeats: %s" % (len(rids), ",".join(sorted(rids)), " | ".join(parts), base, b_ok),
             sev="WARN")

    # 4.1 ------------------------------------------------------------------------------------------
    dwrows = []
    for rid, side in SIDE.items():
        r = RUN[rid]
        if r["replicate"] != "0":
            continue
        df = EXT[rid]
        ann = df.groupby("dwelling")[TARGETS].sum()
        for s_ in side:
            j = int(s_["dwelling"])
            a = float(s_["floor_area_m2"])
            dwrows.append({"run_id": rid, "building_id": r["building_id"], "class": r["class"], "dwelling": j, "hid": s_["hid"],
                           "position": s_["position"], "floor_area_m2": a,
                           "heating_kwh": ann.loc[j, "heating_kwh"], "cooling_kwh": ann.loc[j, "cooling_kwh"],
                           "equipment_kwh": ann.loc[j, "equipment_kwh"], "total_elec_kwh": ann.loc[j, "total_elec_kwh"],
                           "heating_kwh_m2": ann.loc[j, "heating_kwh"] / a, "cooling_kwh_m2": ann.loc[j, "cooling_kwh"] / a})
    DW = pd.DataFrame(dwrows)
    DW.to_csv(R + "report/dwelling_table.csv", index=False)
    for (c, p), g in DW.groupby(["class", "position"]):
        emit("INFO", "4.1_%s_%s" % (c, p), "dwellings=%d heating kWh/m2 mean=%.1f min=%.1f max=%.1f | cooling kWh/m2 mean=%.1f min=%.1f max=%.1f"
             % (len(g), g["heating_kwh_m2"].mean(), g["heating_kwh_m2"].min(), g["heating_kwh_m2"].max(),
                g["cooling_kwh_m2"].mean(), g["cooling_kwh_m2"].min(), g["cooling_kwh_m2"].max()), sev="INFO")

    # 4.3 ------------------------------------------------------------------------------------------
    n_ok = n_ev = n_skip = 0
    worst_ratio = []
    for rid, side in SIDE.items():
        if RUN[rid]["replicate"] != "0":
            continue
        df = EXT[rid]
        for s_ in side:
            j = int(s_["dwelling"])
            pres = pd.read_csv(R + "hh/presence/presence_HH_es_%s.csv" % s_["hid"]).iloc[:, 0].to_numpy(dtype=float)
            eq = df[df["dwelling"] == j].sort_values("hour")["equipment_kwh"].to_numpy()
            if len(pres) != len(eq):
                n_skip += 1
                continue
            pm, am = pres > 0, pres == 0
            if pm.sum() == 0 or am.sum() == 0:
                n_skip += 1
                continue
            n_ev += 1
            if eq[pm].mean() > eq[am].mean():
                n_ok += 1
            worst_ratio.append(eq[pm].mean() / eq[am].mean() if eq[am].mean() else float("inf"))
    frac = n_ok / n_ev if n_ev else 0.0
    emit("PASS" if (n_ev and frac >= 0.9) else ("FAIL" if n_ev else "NOT_EVALUABLE"), "4.3_equipment_present_vs_absent",
         "dwellings evaluated %d (skipped, always present or always absent %d), equipment mean with presence>0 above mean with presence==0 in %d "
         "= %.1f %% (pass >= 90 %%); ratio present/absent median %.2f min %.2f"
         % (n_ev, n_skip, n_ok, 100 * frac, statistics.median(worst_ratio) if worst_ratio else float("nan"),
            min(worst_ratio) if worst_ratio else float("nan")))

    # 5.1 / 5.2 ------------------------------------------------------------------------------------
    rt = []
    for m in man:
        rid = m["run_id"]
        st = ST[rid]
        xb = 0
        for p in (R + "extracted/%s.csv.gz" % rid, R + "extracted/%s.dwellings.csv" % rid):
            if os.path.exists(p):
                xb += os.path.getsize(p)
        rt.append({"run_id": rid, "building_id": m["building_id"], "class": m["class"], "n_zones": int(m["n_zones"]), "n_dwellings": int(m["n_dwellings"]),
                   "seconds": float(st.get("seconds", "nan")), "max_rss_mb": float(st.get("max_rss_kb", "nan")) / 1024.0,
                   "raw_mb": float(st.get("run_folder_du_sk", "nan")) / 1024.0, "extracted_mb": xb / 1048576.0})
    RT = pd.DataFrame(rt)
    RT.to_csv(R + "report/run_table.csv", index=False)

    def q(s, p):
        return float(np.percentile(s, p))
    for key in ("class", "n_zones"):
        for v, g in RT.groupby(key):
            emit("INFO", "5.1_seconds_by_%s_%s" % (key, v), "runs=%d median=%.1f p90=%.1f max=%.1f s; max RSS median %.0f max %.0f MB"
                 % (len(g), g["seconds"].median(), q(g["seconds"], 90), g["seconds"].max(), g["max_rss_mb"].median(), g["max_rss_mb"].max()), sev="INFO")
    emit("INFO", "5.1_seconds_all", "runs=%d median=%.1f p90=%.1f max=%.1f s" % (len(RT), RT["seconds"].median(), q(RT["seconds"], 90), RT["seconds"].max()), sev="INFO")
    for c, g in RT.groupby("class"):
        emit("INFO", "5.2_disk_%s" % c, "runs=%d raw run folder median=%.1f max=%.1f MB; extracted (csv.gz + side table) median=%.2f max=%.2f MB"
             % (len(g), g["raw_mb"].median(), g["raw_mb"].max(), g["extracted_mb"].median(), g["extracted_mb"].max()), sev="INFO")
    emit("INFO", "5.2_disk_all", "raw median=%.1f max=%.1f MB; extracted median=%.2f max=%.2f MB" % (RT["raw_mb"].median(), RT["raw_mb"].max(),
         RT["extracted_mb"].median(), RT["extracted_mb"].max()), sev="INFO")

    # 5.3 draft campaign arithmetic ------------------------------------------------------------------
    try:
        campaign(RT)
    except Exception as ex:
        emit("NOT_EVALUABLE", "5.3", "campaign arithmetic crashed: %r" % (ex,), sev="INFO")
        traceback.print_exc()

    # SEEN FAILING (scratch copies) ---------------------------------------------------------------------
    sd = R + "seenfail_chk/"
    # 2.2: plant a Severe line
    src = R + "runs/MZ001/eplus_out/eplusout.err"
    shutil.copyfile(src, sd + "MZ001_eplusout.err")
    with io.open(sd + "MZ001_eplusout.err", "a", encoding="utf-8") as fh:
        fh.write("   ** Severe  ** planted line for the seen-failing test\n")
    s0, t0, _ = g22(src, ST["MZ001"])
    s, t, _ = g22(sd + "MZ001_eplusout.err", ST["MZ001"])
    seenfail("2.2", s, "planted '** Severe  **' in a copy of MZ001 eplusout.err: %s (control on the real file: %s)" % (t, s0))
    # 3.1: copy one dwelling's series onto another (MZ021 = es_B21 run 1, 12 flats)
    df = EXT["MZ021"].copy()
    hmap = hid_of["MZ021"]
    assert hmap[0] != hmap[1]
    for t_ in ("equipment_kwh", "heating_kwh"):
        df.loc[df["dwelling"] == 0, t_] = df.loc[df["dwelling"] == 1, t_].to_numpy()
    with gzip.open(sd + "MZ021_copied_series.csv.gz", "wt", encoding="utf-8") as fh:
        df.to_csv(fh, index=False)
    pr0, id0 = g31_within(EXT["MZ021"], hmap)
    pr1, id1 = g31_within(load_ext(sd + "MZ021_copied_series.csv.gz"), hmap)
    seenfail("3.1", "FAIL" if id1 else "PASS", "dwelling 1 series copied onto dwelling 0 in a copy of MZ021 (households %s vs %s): identical pairs found %d of %d "
             "(control on the real data: %d)" % (hmap[0], hmap[1], len(id1), pr1, len(id0)))
    # 2.4: scale one hourly series by 1.01 (facility level on a one-dwelling run; dwelling level on a 12-flat run)
    tbl1 = tbl_enduse(R + "runs/MZ001/eplus_out/eplustbl.csv")
    d1 = EXT["MZ001"].copy()
    d1["heating_kwh"] = EXT["MZ001"]["heating_kwh"] * 1.01                                           # the whole series x 1.01
    with gzip.open(sd + "MZ001_heating_x1.01.csv.gz", "wt", encoding="utf-8") as fh:
        d1.to_csv(fh, index=False)
    s, t = g24_facility(load_ext(sd + "MZ001_heating_x1.01.csv.gz"), tbl1)
    sc, tc = g24_facility(EXT["MZ001"], tbl1)
    seenfail("2.4_facility", s, "heating series of MZ001 (one dwelling) x 1.01 in a copy: %s (control on the real file: %s)" % (t.split(";")[0], sc))
    d2 = EXT["MZ021"].copy()
    d2.loc[d2["dwelling"] == 3, "heating_kwh"] = EXT["MZ021"].loc[EXT["MZ021"]["dwelling"] == 3, "heating_kwh"] * 1.01
    with gzip.open(sd + "MZ021_dwelling3_heating_x1.01.csv.gz", "wt", encoding="utf-8") as fh:
        d2.to_csv(fh, index=False)
    s, t = g24_dwelling(load_ext(sd + "MZ021_dwelling3_heating_x1.01.csv.gz"), R + "runs/MZ021/eplus_out/eplusout.csv", META["MZ021"])
    sc, tc = g24_dwelling(EXT["MZ021"], R + "runs/MZ021/eplus_out/eplusout.csv", META["MZ021"])
    seenfail("2.4b_dwelling", s, "heating series of one flat of MZ021 x 1.01 in a copy: %s (control on the real file: %s %s)" % (t, sc, tc))

    # SUMMARY --------------------------------------------------------------------------------------------
    n = lambda s_: sum(1 for g in GATES if g[0] == s_)
    fails = n("FAIL")
    ne_fail_sev = sum(1 for g in GATES if g[0] == "NOT_EVALUABLE" and g[2] == "FAIL")
    print("SUMMARY PASS=%d FAIL=%d WARN=%d NOT_EVALUABLE=%d (INFO=%d; NOT_EVALUABLE among FAIL-severity gates=%d)"
          % (n("PASS"), fails, n("WARN"), n("NOT_EVALUABLE"), n("INFO"), ne_fail_sev))
    rc = 0 if (fails == 0 and ne_fail_sev == 0) else 1
    print("EXIT_CODE %d" % rc)
    return rc


def campaign(RT):
    import importlib
    mz = importlib.import_module("5thJ_idf_mz")
    j5, s8 = mz._j5, mz._s8
    j5.TOOLS_4J = REPO + "4J_docs_occ/tools"
    bt = list(csv.DictReader(io.open(MZ0 + "repo/buildings.csv", encoding="utf-8")))
    assert all(b["building_id"].startswith("es_") for b in bt), "non-Spanish row in buildings.csv"
    rows, _ = s8.load_rows(MZ0 + "repo/", "es")
    rowby = {r["Code_Building"]: r for r in rows}
    TAB = R + "design_in/dwelling_count_es.csv"
    bl = []
    for b in bt:
        d = s8.derive(rowby[b["archetype_code"]])
        F = int(round(d["n_storey"]))
        k, _, _ = mz.k_from_tabula(TAB, d["code"], F)
        ndw = 1 if d["cls"] in ("SFH", "TH") else F * k
        zones = F if d["cls"] in ("SFH", "TH") else F * k
        bl.append({"id": b["building_id"], "cls": d["cls"], "F": F, "k": k, "n_dw": ndw, "zones": zones})
    cnt = {}
    for x in bl:
        cnt[x["cls"]] = cnt.get(x["cls"], 0) + 1
    emit("INFO", "5.3_buildings", "Spanish building rows %d, per class %s; zones per building (min/median/max) by class: %s"
         % (len(bl), json.dumps(cnt, sort_keys=True), json.dumps({c: [min(x["zones"] for x in bl if x["cls"] == c),
            statistics.median(x["zones"] for x in bl if x["cls"] == c), max(x["zones"] for x in bl if x["cls"] == c)] for c in cnt}, sort_keys=True)), sev="INFO")
    med_s = RT.groupby("class")["seconds"].median().to_dict()
    med_raw = RT.groupby("class")["raw_mb"].median().to_dict()
    med_x = RT.groupby("class")["extracted_mb"].median().to_dict()
    emit("INFO", "5.3_inputs", "class median seconds %s ; raw MB %s ; extracted MB %s (pilot medians; the class medians are over %s pilot runs)"
         % (json.dumps({k_: round(v, 1) for k_, v in med_s.items()}, sort_keys=True), json.dumps({k_: round(v, 1) for k_, v in med_raw.items()}, sort_keys=True),
            json.dumps({k_: round(v, 2) for k_, v in med_x.items()}, sort_keys=True), json.dumps(RT.groupby("class").size().to_dict(), sort_keys=True)), sev="INFO")
    emit("INFO", "5.3_assumption", "Italy and UK building rows are NOT opened in this task; each of them is assumed to have the same 40-building class and "
         "layout mix as the Spanish 40 (proxy). 9 climates = 3 per country x 3 countries (ES, IT, UK)", sev="INFO")
    for P in (1, 2, 3):
        runs = cpu_s = 0.0
        raw_w = x_tot = 0.0
        for x in bl:
            c = x["cls"]
            nr = 60 if c in ("SFH", "TH") else math.ceil(60.0 / x["n_dw"]) * P
            runs += nr
            cpu_s += nr * med_s[c]
            raw_w += nr * med_raw[c]
            x_tot += nr * med_x[c]
        per_clim = {"runs": runs, "cpu_h": cpu_s / 3600.0, "raw_avg_mb": raw_w / runs, "x_tot_mb": x_tot}
        for ncl, label in ((1, "1 country x 1 climate"), (9, "9 climates (3 countries x 3)")):
            R_ = runs * ncl
            cpuh = per_clim["cpu_h"] * ncl
            fin_h = cpuh / 30.0
            peak_gb = (30 * per_clim["raw_avg_mb"] + x_tot * ncl) / 1024.0
            emit("INFO", "5.3_P%d_%s" % (P, "1climate" if ncl == 1 else "9climates"),
                 "P=%d positions per household, %s: runs=%d CPU-hours=%.1f finish at 30 CPUs=%.1f h (%.2f days) disk at peak = 30 in flight x %.0f MB raw + all "
                 "extracted %.1f GB = %.1f GB" % (P, label, R_, cpuh, fin_h, fin_h / 24.0, per_clim["raw_avg_mb"], x_tot * ncl / 1024.0, peak_gb), sev="INFO")


if __name__ == "__main__":
    try:
        rc = main()
    except Exception:
        traceback.print_exc()
        print("CRASHED: the checker did not finish; this is NOT a pass. EXIT_CODE 1")
        rc = 1
    sys.exit(rc)
