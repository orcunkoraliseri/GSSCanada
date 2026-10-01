# -*- coding: utf-8 -*-
"""5J WP1 household input folders (Speed port of tools/5thJ_pilot_build.py, household part) + average households.

Runs on Speed only. Paths: R = /speed-scratch/o_iseri/5J/households.
Part C: for every hid of es and it write R/inputs/<country>_<hid>/ with
   presence_HH_<country>_<hid>.csv  (copy of R/<country>_60/presence/...; same file names as the pilot)
   elec_HH_<country>_<hid>.csv      (copy of R/<country>_60/enduse_profiles/<country>/elec_HH_...)
   household.json = {hid, country, n_members, appliance_peak_w, peak_w_source, presence_md5, elec_md5, ...}
 built as the pilot builder does: n_members from enduse_by_dwelling_<c>.csv, appliance_peak_w = Design Level {W}
 read from step9_objects_<c>.idf (checked against elec_peak_w of the csv, tolerance 0.005 W).
Part D: R/inputs/<country>_avg/ : unweighted mean over the 60 households (see household.json).
Gates are printed as `GATE <name> PASS|FAIL ...` ; SUMMARY line at the end; exit 1 if any FAIL.
"""
import csv, glob, hashlib, io, json, os, re, shutil, sys

R = "/speed-scratch/o_iseri/5J/households"
PILOT = "/speed-scratch/o_iseri/5J/pilot/inputs"
N = 8760
FAILS = []


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def gate(name, ok, msg):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(name)


def read_csv(path):
    return list(csv.DictReader(io.open(path, encoding="utf-8")))


def read_series(path):
    lines = [l.strip() for l in io.open(path, encoding="utf-8").read().splitlines() if l.strip()]
    return lines[0], [float(x) for x in lines[1:]]


def design_level_from_idf(path, fold, hid):
    txt = io.open(path, encoding="utf-8").read()
    m = re.search(r"HH_%s_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % (fold, hid), txt, re.S)
    if not m:
        raise RuntimeError("no ElectricEquipment for %s in %s" % (hid, path))
    return float(m.group(1))


def load_country(c):
    base = os.path.join(R, "%s_60" % c)
    hids = [r["hid"] for r in read_csv(os.path.join(R, "repo/5J_docs_occ/Step2_docs/outputs_step2/hids_%s60.csv" % c))]
    by_dw = {r["hid"]: r for r in read_csv(os.path.join(base, "enduse_by_dwelling_%s.csv" % c))}
    idf_path = os.path.join(base, "step9_objects_%s.idf" % c)
    hh = []
    for hid in hids:
        pres = os.path.join(base, "presence", "presence_HH_%s_%s.csv" % (c, hid))
        app = os.path.join(base, "enduse_profiles", c, "elec_HH_%s_%s.csv" % (c, hid))
        peak_idf = design_level_from_idf(idf_path, c, hid)
        peak_csv = float(by_dw[hid]["elec_peak_w"])
        assert abs(peak_idf - peak_csv) < 0.005, (hid, peak_idf, peak_csv)
        hh.append({"hid": hid, "country": c, "n_members": int(by_dw[hid]["n_members"]),
                   "appliance_peak_w": peak_idf, "pres": pres, "app": app, "idf": idf_path})
    return hids, hh


def write_household_folders(c, hh):
    for h in hh:
        d = os.path.join(R, "inputs", "%s_%s" % (c, h["hid"]))
        os.makedirs(d, exist_ok=True)
        pn, an = os.path.basename(h["pres"]), os.path.basename(h["app"])
        shutil.copyfile(h["pres"], os.path.join(d, pn))
        shutil.copyfile(h["app"], os.path.join(d, an))
        meta = {"hid": h["hid"], "country": c, "n_members": h["n_members"],
                "appliance_peak_w": h["appliance_peak_w"], "peak_w_source": h["idf"],
                "presence_file": pn, "presence_md5": md5(os.path.join(d, pn)),
                "elec_file": an, "elec_md5": md5(os.path.join(d, an)),
                "built_like": "tools/5thJ_pilot_build.py (household part)"}
        json.dump(meta, io.open(os.path.join(d, "household.json"), "w", encoding="utf-8"), indent=2)
    print("C wrote %d folders for %s" % (len(hh), c))


def average_series(loaded):
    """loaded: list of dicts with presence (list), frac (list), peak (float), n_members. Returns the average dict."""
    n = float(len(loaded))
    pres = [sum(x["presence"][t] for x in loaded) / n for t in range(N)]
    watts = [sum(x["frac"][t] * x["peak"] for x in loaded) / n for t in range(N)]
    peak = max(watts)
    frac = [w / peak for w in watts]
    return {"presence": pres, "frac": frac, "peak": peak, "n_members": sum(x["n_members"] for x in loaded) / n}


def write_avg(d, c, av, hids):
    os.makedirs(d, exist_ok=True)
    pn, an = "presence_HH_%s_avg.csv" % c, "elec_HH_%s_avg.csv" % c
    with io.open(os.path.join(d, pn), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(u"HH_%s_avg_Presence\n" % c)
        for v in av["presence"]:
            fh.write(u"%.12f\n" % v)
    with io.open(os.path.join(d, an), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(u"HH_%s_avg_ApplianceFraction\n" % c)
        for v in av["frac"]:
            fh.write(u"%.12f\n" % v)
    meta = {"hid": "avg", "country": c, "n_members": av["n_members"], "appliance_peak_w": av["peak"],
            "presence_file": pn, "presence_md5": md5(os.path.join(d, pn)),
            "elec_file": an, "elec_md5": md5(os.path.join(d, an)),
            "average_of": len(hids), "hids": hids,
            "weighting": "UNWEIGHTED mean over the 60 households (ASSUMED by the manager: the 60 were drawn with "
                         "the survey weights, so their plain mean is the stock estimate)",
            "presence": "hourly mean of the presence fraction",
            "appliance": "hourly mean of (fraction x design level) in W; appliance_peak_w = max of that mean; "
                         "elec fraction = mean W / appliance_peak_w",
            "n_members_note": "mean household size, a real number"}
    json.dump(meta, io.open(os.path.join(d, "household.json"), "w", encoding="utf-8"), indent=2)


def avg_gate(label, c, avdir, loaded_ref):
    """D gate: read the WRITTEN avg files back; annual kWh of avg = mean of the annual kWh of the 60 (from the original series)."""
    _, pres = read_series(os.path.join(avdir, "presence_HH_%s_avg.csv" % c))
    _, frac = read_series(os.path.join(avdir, "elec_HH_%s_avg.csv" % c))
    meta = json.load(io.open(os.path.join(avdir, "household.json"), encoding="utf-8"))
    kwh_avg = sum(f * meta["appliance_peak_w"] for f in frac) / 1000.0
    kwh_60 = [sum(f * x["peak"] for f in x["frac"]) / 1000.0 for x in loaded_ref]
    mean60 = sum(kwh_60) / len(kwh_60)
    rel = abs(kwh_avg - mean60) / mean60
    gate("D_%s_kwh" % label, rel < 1e-9, "avg_kwh=%.6f mean_of_60=%.6f rel=%.3e" % (kwh_avg, mean60, rel))
    gate("D_%s_presence_range" % label, min(pres) >= 0.0 and max(pres) <= 1.0,
         "min=%.6f max=%.6f" % (min(pres), max(pres)))
    gate("D_%s_rows" % label, len(pres) == N and len(frac) == N, "presence=%d elec=%d" % (len(pres), len(frac)))
    return rel, mean60, kwh_avg


def load_series(hh):
    out = []
    for h in hh:
        _, p = read_series(h["pres"])
        _, f = read_series(h["app"])
        assert len(p) == N and len(f) == N, (h["hid"], len(p), len(f))
        out.append({"presence": p, "frac": f, "peak": h["appliance_peak_w"], "n_members": h["n_members"]})
    return out


def main():
    import numpy, pandas
    print("python", sys.version.split()[0], "numpy", numpy.__version__, "pandas", pandas.__version__)
    for c in ("es", "it"):
        hids, hh = load_country(c)
        gate("C_%s_count" % c, len(hh) == 60 and len(set(hids)) == 60, "n=%d" % len(hh))
        write_household_folders(c, hh)
        loaded = load_series(hh)
        # ---- Part D
        avdir = os.path.join(R, "inputs", "%s_avg" % c)
        av = average_series(loaded)
        write_avg(avdir, c, av, hids)
        rel, mean60, kwh_avg = avg_gate(c, c, avdir, loaded)
        print("D %s avg: n_members=%.4f appliance_peak_w=%.4f annual_kwh=%.4f" % (c, av["n_members"], av["peak"], kwh_avg))
        # seen failing: one household scaled by 1.01 before averaging (scratch copy only)
        bad = [dict(x) for x in loaded]
        bad[0]["frac"] = [v * 1.01 for v in bad[0]["frac"]]
        sdir = os.path.join(R, "scratch_seenfail_D", "%s_avg" % c)
        write_avg(sdir, c, average_series(bad), hids)
        before = len(FAILS)
        avg_gate("SEENFAIL_%s" % c, c, sdir, loaded)
        fired = len(FAILS) > before
        print("SEENFAIL D %s: gate %s (must FAIL)" % (c, "FAILED as required" if fired else "DID NOT FIRE"))
        if fired:
            del FAILS[before:]          # the planted failure is expected, not a run failure
        else:
            FAILS.append("D_%s_seenfail_did_not_fire" % c)

    # ---- C1: ten Spanish pilot hids against the pilot inputs
    pil = [r["hid"] for r in read_csv(os.path.join(R, "repo/5J_docs_occ/Step2_docs/outputs_step2/pilot_hids_es.csv"))]
    gate("C1_pilot_count", len(pil) == 10, "n=%d" % len(pil))
    for hid in pil:
        cand = sorted(glob.glob(os.path.join(PILOT, "*__es_%s" % hid)))
        if not cand:
            gate("C1_%s" % hid, False, "no pilot folder")
            continue
        pd_ = cand[0]
        mine = os.path.join(R, "inputs", "es_%s" % hid)
        meta = json.load(io.open(os.path.join(mine, "household.json"), encoding="utf-8"))
        ok_files = all(md5(os.path.join(mine, n)) == md5(os.path.join(pd_, n))
                       for n in ("presence_HH_es_%s.csv" % hid, "elec_HH_es_%s.csv" % hid))
        txt = io.open(os.path.join(pd_, "in.idf"), encoding="utf-8").read()
        m_dl = re.search(r"HH_es_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % hid, txt, re.S)
        m_np = re.search(r"HH_es_%s_People,[^;]*?Number of People Calculation Method\s*\n\s+([0-9.]+),\s+!- Number of People\b" % hid, txt, re.S)
        dl = float(m_dl.group(1)) if m_dl else None
        npp = float(m_np.group(1)) if m_np else None
        ok = ok_files and dl is not None and npp is not None and abs(dl - meta["appliance_peak_w"]) < 5e-5 \
            and abs(npp - meta["n_members"]) < 1e-9
        gate("C1_%s" % hid, ok, "files_md5_equal=%s design_level idf=%s mine=%.4f n_people idf=%s mine=%s (%s)" % (
            ok_files, dl, meta["appliance_peak_w"], npp, meta["n_members"], os.path.basename(pd_)))
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


main()
