# -*- coding: utf-8 -*-
"""5J pilot part 1 (Spain only): build the portable pilot inputs, the run manifest, the md5 list.

Reads  Step2_docs/outputs_step2/{pilot_runs,buildings,climates}.csv
       _5J_data/surrogate/wp1_hids/es_60/{presence/, enduse_profiles/es/, enduse_by_dwelling_es.csv,
                                          step9_objects_es.idf}
Writes _5J_data/surrogate/pilot/{inputs/<input_id>/, abs_idf/, meta/, run_manifest.csv, md5_local.txt}

One folder per UNIQUE input (building x household); replicates point at the same folder.
`File Name` lines of the IDF are rewritten to bare basenames (PATCH relative_paths).
Imports tools/5thJ_idf.py (not edited) and 4J tools/4thJ_step8_idf.py (not edited).
Usage: python 5thJ_pilot_build.py
"""
import csv
import hashlib
import importlib
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
idf = importlib.import_module("5thJ_idf")
_s8 = idf._s8

ROOT = r"C:\Users\o_iseri\Desktop\GSSCanada"
OUT2 = os.path.join(ROOT, r"GSSCanada-main\5J_docs_occ\Step2_docs\outputs_step2")
S8 = os.path.join(ROOT, r"GSSCanada-main\4J_docs_occ\Step8_docs\outputs_step8")
H60 = os.path.join(ROOT, r"_5J_data\surrogate\wp1_hids\es_60")
PILOT = os.path.join(ROOT, r"_5J_data\surrogate\pilot")
EPW_EXPECT = "110b364912226ee4d2a5b5411eab81da"
EP_VERSION = "23.1.0-87ed9199d4"


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def read_csv(path):
    return list(csv.DictReader(io.open(path, encoding="utf-8")))


FILE_NAME_RE = re.compile(r"^(\s*)(\S[^\n]*?)(,\s+!- File Name)$", re.M)


def relativise(text):
    """Rewrite every Schedule:File `File Name` value to its basename. Returns (text, n)."""
    n = [0]

    def sub(m):
        n[0] += 1
        return "%s%s%s" % (m.group(1), m.group(2).replace("\\", "/").split("/")[-1], m.group(3))
    return FILE_NAME_RE.sub(sub, text), n[0]


def main():
    runs = read_csv(os.path.join(OUT2, "pilot_runs.csv"))
    bld = {r["building_id"]: r for r in read_csv(os.path.join(OUT2, "buildings.csv"))}
    clim = {r["climate_id"]: r for r in read_csv(os.path.join(OUT2, "climates.csv"))}
    by_dw = {r["hid"]: r for r in read_csv(os.path.join(H60, "enduse_by_dwelling_es.csv"))}
    rows, _ = _s8.load_rows(S8, "es")
    by_code = {}
    for r in rows:
        by_code.setdefault(r["Code_Building"], []).append(r)
    idf_h60 = os.path.join(H60, "step9_objects_es.idf")
    assert len(runs) == 50, len(runs)

    epw_path = clim["es_madrid_2010"]["path"]
    epw_md5 = md5(epw_path)
    assert epw_md5 == EPW_EXPECT == clim["es_madrid_2010"]["md5"], epw_md5
    print("EPW md5 OK %s" % epw_md5)

    for d in ("inputs", "abs_idf", "meta"):
        os.makedirs(os.path.join(PILOT, d), exist_ok=True)

    inputs = {}          # input_id -> dict(idf_md5, sched_md5)
    total_patched = 0
    for r in runs:
        iid = "%s__%s" % (r["building_id"], r["household_id"])
        if iid in inputs:
            continue
        b = bld[r["building_id"]]
        cand = by_code[b["archetype_code"]]
        assert len(cand) == 1, (b["archetype_code"], len(cand))
        hid = r["household_id"].split("_", 1)[1]
        pres = os.path.join(H60, "presence", "presence_HH_es_%s.csv" % hid)
        app = os.path.join(H60, "enduse_profiles", "es", "elec_HH_es_%s.csv" % hid)
        peak_idf = idf._design_level_from_idf(idf_h60, hid)
        peak_csv = float(by_dw[hid]["elec_peak_w"])
        assert abs(peak_idf - peak_csv) < 0.005, (hid, peak_idf, peak_csv)
        hh = {"hid": hid, "fold": "es", "n_members": int(by_dw[hid]["n_members"]),
              "presence_csv": pres, "appliance_csv": app, "appliance_peak_w": peak_idf,
              "peak_w_source": idf_h60}
        print("== input %s (archetype %s, ach %s, north %s)" % (iid, b["archetype_code"],
                                                              b["infiltration_ach"], b["north_axis_deg"]))
        text, meta = idf.build(cand[0], hh, infiltration_ach=float(b["infiltration_ach"]),
                               north_axis_deg=float(b["north_axis_deg"]))
        chk = idf.check_patches(text, meta["patch_lines"])
        assert chk[0] == "PASS", (iid, chk)
        # absolute-path copy (for the relative = absolute gate only)
        io.open(os.path.join(PILOT, "abs_idf", iid + ".idf"), "w", encoding="utf-8", newline="\n").write(text)
        rel, n = relativise(text)
        assert n == 2, (iid, n)
        assert not re.search(r"!- File Name", re.sub(r"^\s*[A-Za-z0-9_.\-]+,\s+!- File Name$", "", rel, flags=re.M)), iid
        total_patched += n
        print("PATCH relative_paths OK n=%d input=%s" % (n, iid))
        d = os.path.join(PILOT, "inputs", iid)
        os.makedirs(d, exist_ok=True)
        io.open(os.path.join(d, "in.idf"), "w", encoding="utf-8", newline="\n").write(rel)
        shutil.copyfile(pres, os.path.join(d, os.path.basename(pres)))
        shutil.copyfile(app, os.path.join(d, os.path.basename(app)))
        meta["idf_md5_relative"] = md5(os.path.join(d, "in.idf"))
        io.open(os.path.join(PILOT, "meta", iid + ".json"), "w", encoding="utf-8").write(
            json.dumps(meta, indent=2, default=str))
        inputs[iid] = {"idf_md5": md5(os.path.join(d, "in.idf")),
                       "sched_md5": "%s;%s" % (md5(os.path.join(d, os.path.basename(pres))),
                                               md5(os.path.join(d, os.path.basename(app))))}
    print("SUMMARY unique inputs=%d relative_paths total n=%d" % (len(inputs), total_patched))
    assert len(inputs) == 42 and total_patched == 84

    # manifest ------------------------------------------------------------------------------
    cols = ["run_id", "country", "climate", "building_id", "household_id", "replicate", "input_id",
            "schedule_md5", "idf_md5", "epw_md5", "energyplus_version", "clock_origin"]
    with io.open(os.path.join(PILOT, "run_manifest.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        for r in runs:
            iid = "%s__%s" % (r["building_id"], r["household_id"])
            w.writerow([r["run_id"], "es", r["climate"], r["building_id"], r["household_id"],
                        r["replicate"], iid, inputs[iid]["sched_md5"], inputs[iid]["idf_md5"],
                        epw_md5, EP_VERSION, "midnight"])
    print("manifest rows=%d" % len(runs))

    # md5 list: every file under inputs/ + the EPW, paths relative to pilot/ ----------------
    os.makedirs(os.path.join(PILOT, "epw"), exist_ok=True)
    epw_copy = os.path.join(PILOT, "epw", os.path.basename(epw_path))
    shutil.copyfile(epw_path, epw_copy)
    assert md5(epw_copy) == epw_md5
    files = []
    for iid in sorted(inputs):
        d = os.path.join(PILOT, "inputs", iid)
        for fn in sorted(os.listdir(d)):
            files.append("inputs/%s/%s" % (iid, fn))
    files.append("epw/" + os.path.basename(epw_path))
    with io.open(os.path.join(PILOT, "md5_local.txt"), "w", encoding="utf-8", newline="\n") as fh:
        for rel in files:
            fh.write("%s  %s\n" % (md5(os.path.join(PILOT, *rel.split("/"))), rel))
    print("md5_local.txt lines=%d" % len(files))


if __name__ == "__main__":
    main()
