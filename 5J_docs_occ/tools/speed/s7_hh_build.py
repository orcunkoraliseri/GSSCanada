# -*- coding: utf-8 -*-
"""5J Step 7 part C (Speed CPU job): household input folders from a trigger output, checked like households-v2.
usage: s7_hh_build.py <trigger_out_dir> <hids_csv> <out_pool_dir> [--pool]
For every hid of <hids_csv> write <out_pool_dir>/es_<hid>/{presence_HH_es_<hid>.csv, elec_HH_es_<hid>.csv, household.json}
(as tools/speed/hh_build.write_household_folders: n_members from enduse_by_dwelling_es.csv, appliance_peak_w = Design Level {W} read from
step9_objects_es.idf and equal to elec_peak_w of the csv within 0.005 W). Then READ BACK every written file and check:
8,760 rows, presence in [0,1], appliance fraction finite and >= 0, design level > 0, members >= 1, md5 in household.json = md5 of the file.
--pool : also assemble hh/pool/ (symlinks to the 60 campaign folders in households/inputs + the new folders, hh/pool.csv).
Self-test: the same checker is run on planted bad households (presence 1.2, 8,759 rows, design level 0, NaN) and must flag each."""
import csv, glob, hashlib, io, json, math, os, re, shutil, sys
import s7_common as s7

N = 8760
FAILS = []
CAMP_HH = "/speed-scratch/o_iseri/5J/households/inputs/"


def gate(name, ok, text=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def read_series(path):
    lines = [l.strip() for l in io.open(path, encoding="utf-8").read().splitlines() if l.strip()]
    return lines[0], [float(x) for x in lines[1:]]


def check_household(pres, frac, peak, members):
    """list of problems (empty = fine)"""
    bad = []
    if len(pres) != N:
        bad.append("presence rows %d" % len(pres))
    if len(frac) != N:
        bad.append("appliance rows %d" % len(frac))
    if pres and not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in pres):
        bad.append("presence outside [0,1] or not finite")
    if frac and not all(math.isfinite(v) and v >= 0.0 for v in frac):
        bad.append("appliance fraction negative or not finite")
    if not (peak > 0):
        bad.append("design level %s not > 0" % peak)
    if not (members >= 1):
        bad.append("members %s < 1" % members)
    return bad


def design_level_from_idf(txt, hid):
    m = re.search(r"HH_es_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % hid, txt, re.S)
    if not m:
        raise RuntimeError("no ElectricEquipment for %s" % hid)
    return float(m.group(1))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    trig, hidsf, outp = sys.argv[1].rstrip("/") + "/", sys.argv[2], sys.argv[3].rstrip("/") + "/"
    pool_mode = "--pool" in sys.argv
    s7.stamp("s7_hh_build start trig=%s hids=%s out=%s pool=%s" % (trig, hidsf, outp, pool_mode))
    # ---- self-test of the checker
    good = [0.5] * N
    gate("selftest_checker_accepts_a_good_household", not check_household(good, good, 100.0, 2))
    for label, args in (("presence_1.2", ([1.2] + good[1:], good, 100.0, 2)), ("8759_rows", (good[:-1], good, 100.0, 2)),
                        ("design_level_0", (good, good, 0.0, 2)), ("nan_fraction", (good, [float("nan")] + good[1:], 100.0, 2)),
                        ("members_0", (good, good, 100.0, 0))):
        gate("selftest_checker_flags_%s (seen failing)" % label, bool(check_household(*args)))
    hids = [r["hid"] for r in s7.read_csv(hidsf)]
    print("HIDS %d first %s" % (len(hids), hids[:3]))
    by_dw = {r["hid"]: r for r in s7.read_csv(trig + "enduse_by_dwelling_es.csv")}
    gate("trigger_output_holds_exactly_the_hids_in_order", [r["hid"] for r in s7.read_csv(trig + "enduse_by_dwelling_es.csv")] == hids,
         "hids=%d rows=%d" % (len(hids), len(by_dw)))
    idf_txt = io.open(trig + "step9_objects_es.idf", encoding="utf-8").read()
    os.makedirs(outp, exist_ok=True)
    nbytes = 0
    nbad = 0
    first_bad = []
    peaks, mem, ann = [], [], []
    for hid in hids:
        d = "%ses_%s/" % (outp, hid)
        os.makedirs(d, exist_ok=True)
        pres_src = "%spresence/presence_HH_es_%s.csv" % (trig, hid)
        app_src = "%senduse_profiles/es/elec_HH_es_%s.csv" % (trig, hid)
        pn, an = os.path.basename(pres_src), os.path.basename(app_src)
        shutil.copyfile(pres_src, d + pn)
        shutil.copyfile(app_src, d + an)
        peak = design_level_from_idf(idf_txt, hid)
        peak_csv = float(by_dw[hid]["elec_peak_w"])
        meta = {"hid": hid, "country": "es", "n_members": int(by_dw[hid]["n_members"]), "appliance_peak_w": peak, "peak_w_source": trig + "step9_objects_es.idf",
                "presence_file": pn, "presence_md5": md5(d + pn), "elec_file": an, "elec_md5": md5(d + an),
                "built_like": "tools/speed/hh_build.py (household part), Step 7 district pool"}
        json.dump(meta, io.open(d + "household.json", "w", encoding="utf-8"), indent=2)
        # ---- read everything back
        j = json.load(io.open(d + "household.json", encoding="utf-8"))
        _, pres = read_series(d + j["presence_file"])
        _, frac = read_series(d + j["elec_file"])
        bad = check_household(pres, frac, float(j["appliance_peak_w"]), float(j["n_members"]))
        if abs(peak - peak_csv) >= 0.005:
            bad.append("design level idf %.4f vs csv %.4f" % (peak, peak_csv))
        if md5(d + pn) != j["presence_md5"] or md5(d + an) != j["elec_md5"]:
            bad.append("md5 in household.json differs from the file")
        if bad:
            nbad += 1
            first_bad.append((hid, bad))
        nbytes += sum(os.path.getsize(d + f) for f in os.listdir(d))
        peaks.append(peak)
        mem.append(int(by_dw[hid]["n_members"]))
        ann.append(sum(f * peak for f in frac) / 1000.0)
    gate("every_household_checked_8760_rows_presence_0_1_design_level_pos", nbad == 0, "households=%d bad=%d first=%s" % (len(hids), nbad, first_bad[:2]))
    print("MB_PER_HOUSEHOLD %.3f (files written under %s ; %d households, %d bytes)" % (nbytes / 1e6 / max(1, len(hids)), outp, len(hids), nbytes))
    print("STATS design_level_w min=%.1f max=%.1f ; members mean=%.2f ; annual appliance kWh mean=%.1f" % (min(peaks), max(peaks), sum(mem) / float(len(mem)), sum(ann) / len(ann)))
    if pool_mode:
        os.makedirs(s7.POOL, exist_ok=True)
        hh60 = [r for r in s7.read_csv(s7.IN + "ref/households.csv") if r["country"] == "es"]
        spl = {r["household_id"]: r["split"] for r in s7.read_csv(s7.IN + "ref/splits_households.csv")}
        rows = []
        for r in hh60:
            link = s7.POOL + "es_%s" % r["hid"]
            if os.path.lexists(link):
                os.remove(link)
            os.symlink(CAMP_HH + "es_%s" % r["hid"], link)
            sp = spl["es_" + r["hid"]]
            j = json.load(io.open(CAMP_HH + "es_%s/household.json" % r["hid"], encoding="utf-8"))
            rows.append([r["hid"], r["weight"], "campaign", sp, "1" if sp == "dev" else "0", j["n_members"]])
        newroot = outp
        wmap = {r["hid"]: r["weight"] for r in s7.read_csv(hidsf)}
        for hid in hids:
            link = s7.POOL + "es_%s" % hid
            if os.path.lexists(link):
                os.remove(link)
            os.symlink("%ses_%s" % (newroot, hid), link)
            rows.append([hid, wmap[hid], "new", "none", "0", by_dw[hid]["n_members"]])
        s7.write_csv(s7.HH + "pool.csv", ["hid", "weight", "source", "split_draft", "trained_by_model", "n_members"], rows)
        nl = len([f for f in os.listdir(s7.POOL)])
        gate("pool_has_60_plus_new_folders_each_with_household_json", nl == 60 + len(hids) and all(os.path.exists(s7.POOL + f + "/household.json") for f in os.listdir(s7.POOL)),
             "folders=%d expected %d" % (nl, 60 + len(hids)))
        gate("pool_hids_distinct", len({r[0] for r in rows}) == len(rows), "rows=%d" % len(rows))
        print("POOL rows=%d (campaign %d, new %d; trained_by_model=%d) md5 pool.csv=%s" % (len(rows), len(hh60), len(hids), sum(int(r[4]) for r in rows), s7.md5(s7.HH + "pool.csv")))
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
