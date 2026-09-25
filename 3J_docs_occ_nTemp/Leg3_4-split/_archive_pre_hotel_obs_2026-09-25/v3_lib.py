"""V3 (3J IMP validation track) -- shared library.

Builds the IDF for one V3 task, runs EnergyPlus, and post-processes with the campaign's OWN writers
(`3rdJ_08P_probe_driver._do_postprocess`). Nothing here re-implements an extractor.

Pipeline for an INJECTED task (V3b arms N/X, V3a) -- the deliverable's own chain, V2-E5 "Method":
    base Leg-2 IDF -> inject_mixed_use(preserve_load_standby_floor=False, lighting_model=None,
    dhw_model=None)  [= the pre-T9-9 behaviour the frozen campaign_cf69d508 cells ran with]
    -> probe._ensure_output_objects -> V2-D9 retail converter (convert + verify)
    -> V2-D10 per-object resize (K=1.0, "Laundry Service Water Use 30.6gpm 180F=8.5") -> E+.

Pipeline for a FROZEN task (V3b arm U/U2): the frozen deliverable's own injected_resized.idf, copied
byte-for-byte, -> E+.   R: see v3_build_R.py (independent text edit of the frozen IDF).

Layout: REPO = repo root (local: GSSCanada-main; Speed: /speed-scratch/o_iseri/3J_V3/repo).
The injector package lives at REPO/eSim/eSim_bem_utils (same as the local tree).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from importlib.machinery import SourceFileLoader

HERE = os.path.dirname(os.path.abspath(__file__))
# scripts/V3 -> scripts -> IMP -> implementation -> writing -> 3J_docs_occ_nTemp -> REPO
_DEFAULT_REPO = os.path.abspath(os.path.join(HERE, *([".."] * 6)))
REPO = os.environ.get("REPO") or _DEFAULT_REPO
J3 = os.path.join(REPO, "3J_docs_occ_nTemp")
S8 = os.path.join(J3, "Leg3_4-split", "Step8_docs")
S9 = os.path.join(J3, "Leg3_4-split", "Step9_docs")
S7O = os.path.join(J3, "Leg3_4-split", "Step7_docs", "outputs_step7")
FROZEN = os.path.join(S8, "campaign_local_deliverable")
FIXTURES = os.path.join(HERE, "fixtures")
INJ_ROOT = os.path.join(REPO, "eSim")

IS_WIN = sys.platform == "win32"
IDD = os.environ.get("EPLUS_IDD") or (r"C:\EnergyPlusV24-2-0\Energy+.idd" if IS_WIN else
      "/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd")
LOCAL_EXE = r"C:\EnergyPlusV24-2-0\energyplus.exe"
SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF_EXE = "/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus"

RESIZE_K = 1.0
RESIZE_SPEC = "Laundry Service Water Use 30.6gpm 180F=8.5"      # V2-G1 "resize spec"

CITIES = {
    "MTL": {"idf_dir": "CAN_MTL", "tag": "Z6", "pr": "QC", "cz": "Z6",
            "epw": "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"},
    "CLG": {"idf_dir": "CAN_CLG", "tag": "Z7A", "pr": "AB", "cz": "Z7A",
            "epw": "CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw"},
}

# ---- P10R switch (2026-09-25, V3a local run; backup v3_lib.py.pre_P10R_2026-09-25.bak) ----------
# V3a now reads the P10R sibling arm (IMP/P10R_fix.md), the arm the paper reports:
#   products  Step7_docs/outputs_step7_P10R/  (md5s = campaign_local_P10R/<scenario>__*__*/manifest.json
#             INPUTS_HASH_DETAIL = P10R_products_registry.json, all 8 cells, verified on disk 2026-09-25)
#   injector  preserve_load_standby_floor=True (T9-9 fix ON, as 3rdJ_08D_campaign_cell_P10R.py runs it)
#   reference campaign_local_P10R/<cell>/injected_resized.idf (seed-42 static check, arm S)
# The frozen-arm table is kept as PRODUCTS_FROZEN for the record; V3b (arms U/U2/R/N/X) is unchanged
# and still uses FROZEN + standby floor OFF.
S7O_FROZEN = S7O
S7O = os.path.join(J3, "Leg3_4-split", "Step7_docs", "outputs_step7_P10R")
P10R_CAMPAIGN = os.path.join(S8, "campaign_local_P10R")
P10R_STANDBY_FLOOR = True
PRODUCTS_FROZEN = {
    "Y2022": {
        "office": ("office_presence_multiplier_2022.csv", "ff0fc98704042f79c66e993e0400a7bb", "observed"),
        "retail": ("retail_presence_multiplier_2022.csv", "e31f528e26bd74286a90c425921fd32b"),
        "hotel": ("hotel_schedule_multiplier_2022.csv", "7b62a8854381fd93859d988f3852e2af"),
        "residential": ("BEM_Schedules_4split_2022.csv", "281d96c06b25432336149c854ac1b2e2"),
    },
    "B_central": {
        "office": ("office_presence_multiplier_2030_BAK_2026-08-02.csv", "1536c98c5358ece477290d45f0505e4f", "hybrid"),
        "retail": ("retail_presence_multiplier_2030_central_BAK_2026-08-02.csv", "cf8721c62030fc7c1f23b999f85056d0"),
        "hotel": ("hotel_schedule_multiplier_2030_central.csv", "4b3d3a4603cc0cccc6a1bf42139d69ee"),
        "residential": ("BEM_Schedules_4split_2030_central.csv", "d36388c8958f4f3ac72f5e9ae508c711"),
    },
}
PRODUCTS = {
    "Y2022": {
        "office": ("office_presence_multiplier_2022.csv", "d94d86554bd2c3713128dbb074da4265", "observed"),
        "retail": ("retail_presence_multiplier_2022.csv", "33708341dacabf4d32e786a2bdd6d9ee"),
        "hotel": ("hotel_schedule_multiplier_2022.csv", "7b62a8854381fd93859d988f3852e2af"),
        "residential": ("BEM_Schedules_4split_2022.csv", "bdb9b506911922646bca6f06f065b516"),
    },
    "B_central": {
        "office": ("office_presence_multiplier_2030.csv", "d78650c0922b48978f3ff736adbb0e5b", "hybrid"),
        "retail": ("retail_presence_multiplier_2030_central.csv", "0ec541ae0d0e9da206db486086df79a2"),
        "hotel": ("hotel_schedule_multiplier_2030_central.csv", "4b3d3a4603cc0cccc6a1bf42139d69ee"),
        "residential": ("BEM_Schedules_4split_2030_central.csv", "65a078b798862f42c4e32f2656d28e48"),
    },
}


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(name, path):
    if not os.path.isfile(path):
        raise SystemExit("REFUSING: cannot find %s at %s" % (name, path))
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cell_tag(scenario, building, city):
    return "%s__%s__%s" % (scenario, building, city)


def base_idf(building, city):
    c = CITIES[city]
    return os.path.join(J3, "Leg2_2-split", "Step8_docs", "outputs_step8", "office_idfs_v242",
                        c["idf_dir"], "%sBuilding_90.1-2019_6A_Buffalo_NECB17_%s_v242.idf"
                        % (building, c["tag"]))


def epw_path(city):
    return os.path.join(REPO, "BEM_Setup", "WeatherFile", CITIES[city]["epw"])


def frozen_idf(scenario, building, city):
    return os.path.join(FROZEN, cell_tag(scenario, building, city), "injected_resized.idf")


def p10r_idf(scenario, building, city):
    """P10R patch: the V3a seed-42 static reference (read only)."""
    p = os.path.join(P10R_CAMPAIGN, cell_tag(scenario, building, city), "injected_resized.idf")
    print("[patch P10R] static reference = %s" % p)
    return p


class Tools:
    """Loads the campaign modules once, and makes sure the injector resolves from INJ_ROOT
    (the probe driver inserts a stale Speed upload tree into sys.path at import time -- the same
    shadowing the campaign driver guards against, 3rdJ_08D_campaign_driver.py:153-176)."""

    def __init__(self):
        os.environ.setdefault("EPLUS_IDD", IDD)
        os.environ["REPO"] = REPO
        self.probe = _load("v3_probe_driver", os.path.join(S8, "3rdJ_08P_probe_driver.py"))
        while INJ_ROOT in sys.path:
            sys.path.remove(INJ_ROOT)
        sys.path.insert(0, INJ_ROOT)
        for m in [m for m in list(sys.modules) if m == "eSim_bem_utils" or m.startswith("eSim_bem_utils.")]:
            del sys.modules[m]
        import eSim_bem_utils.commercial_integration as ci
        if os.path.realpath(INJ_ROOT) not in os.path.realpath(ci.__file__):
            raise SystemExit("REFUSING: injector resolved outside INJ_ROOT: %s" % ci.__file__)
        self.ci = ci
        self.d9 = _load("v3_d9", os.path.join(S9, "3rdJ_09J_retail_necb_c.py"))
        self.rprobe = _load("v3_resize_probe", os.path.join(S9, "3rdJ_09H_plant_resize_probe.py"))
        self.topo = _load("v3_topo", os.path.join(S9, "3rdJ_09H_dhw_plant_topology.py"))
        self.rcell = _load("v3_resize_cell", os.path.join(S9, "3rdJ_09H_resize_campaign_cell.py"))
        self.code_md5 = {
            "commercial_integration.py": md5_file(ci.__file__),
            "3rdJ_08P_probe_driver.py": md5_file(os.path.join(S8, "3rdJ_08P_probe_driver.py")),
            "3rdJ_09J_retail_necb_c.py": md5_file(os.path.join(S9, "3rdJ_09J_retail_necb_c.py")),
            "3rdJ_09H_plant_resize_probe.py": md5_file(os.path.join(S9, "3rdJ_09H_plant_resize_probe.py")),
            "3rdJ_09H_resize_campaign_cell.py": md5_file(os.path.join(S9, "3rdJ_09H_resize_campaign_cell.py")),
            "3rdJ_09H_dhw_plant_topology.py": md5_file(os.path.join(S9, "3rdJ_09H_dhw_plant_topology.py")),
            "v3_lib.py": md5_file(os.path.abspath(__file__)),
        }
        print("[tools] injector:", ci.__file__, self.code_md5["commercial_integration.py"])


def set_runperiod_days(idf_path, days):
    """Smoke only: truncate every RunPeriod to Jan 1..days (text edit, eppy-free)."""
    txt = open(idf_path, errors="replace").read()
    n = 0

    def _fix(m):
        nonlocal n
        body = m.group(0)
        body = re.sub(r"(?m)^(\s*)[^,;!\n]*(\s*[,;]\s*!-\s*End Month)", r"\g<1>1\g<2>", body)
        body = re.sub(r"(?m)^(\s*)[^,;!\n]*(\s*[,;]\s*!-\s*End Day of Month)",
                      lambda mm: "%s%d%s" % (mm.group(1), days, mm.group(2)), body)
        n += 1
        return body
    txt = re.sub(r"(?ims)^RunPeriod,.*?;", _fix, txt)
    if n == 0:
        raise SystemExit("REFUSING: no RunPeriod found to truncate in %s" % idf_path)
    # verify
    got = re.findall(r"(?m)^\s*([^,;!\n]*)\s*[,;]\s*!-\s*End Day of Month", txt)
    if not got or any(g.strip() != str(days) for g in got):
        raise SystemExit("REFUSING: RunPeriod truncation did not land (%r)" % got)
    open(idf_path, "w").write(txt)
    return n


def build_injected(tools, building, city, channels, tag, work, smoke_days=None, standby_floor=False):
    """Deliverable chain on the base IDF. Returns (final_idf, info).
    standby_floor=False = frozen-arm wiring (V3b N/X); True = P10R wiring (V3a arm S, T9-9 fix ON)."""
    print("[patch P10R] build_injected preserve_load_standby_floor=%s (%s)" % (standby_floor, tag))
    os.makedirs(work, exist_ok=True)
    src = base_idf(building, city)
    pre = os.path.join(work, "injected.idf")
    meta = {"building": building, "city": city, "cz": CITIES[city]["cz"], "purpose": "V3",
            "scenario_label": tag}
    res = tools.ci.inject_mixed_use(src, pre, channels, meta, verbose=True,
                                    preserve_load_standby_floor=bool(standby_floor), lighting_model=None,
                                    dhw_model=None)
    from eppy.modeleditor import IDF
    IDF.setiddname(os.environ["EPLUS_IDD"])
    idf = IDF(pre)
    tools.probe._ensure_output_objects(idf, verbose=True)
    idf.saveas(pre)
    d9_idf = os.path.join(work, "injected_d9.idf")
    rep, n_swap = tools.d9.convert(pre, d9_idf, True, True)
    if not tools.d9.verify(pre, d9_idf, True, True, n_swap):
        raise SystemExit("REFUSING: V2-D9 verify failed on %s" % d9_idf)
    per_object, spec_report = tools.rcell.resolve_equip_spec(RESIZE_SPEC, d9_idf, tools.topo)
    final = os.path.join(work, "injected_resized.idf")
    seen, base_kW, new_kW = tools.rprobe.resize_idf(d9_idf, final, RESIZE_K, per_object or None)
    if smoke_days:
        set_runperiod_days(final, smoke_days)
    info = {"inject_mixed_use_result": res, "d9_swaps": n_swap, "resize_per_object": per_object,
            "plant_kW_base": base_kW, "plant_kW_resized": new_kW, "base_idf": src,
            "preserve_load_standby_floor": bool(standby_floor),
            "base_idf_md5": md5_file(src)}
    return final, info


def eplus_cmd(work):
    if IS_WIN:
        return [LOCAL_EXE]
    wrap = os.path.join(work, "energyplus_sif.sh")
    with open(wrap, "w") as f:
        f.write("#!/bin/bash\nexec singularity exec --bind /speed-scratch --bind /nfs/speed-scratch "
                "%s %s \"$@\"\n" % (SIF, SIF_EXE))
    os.chmod(wrap, 0o755)
    return [wrap]


def run_eplus(idf, epw, run_dir, work):
    os.makedirs(run_dir, exist_ok=True)
    cmd = eplus_cmd(work)
    ver = subprocess.run(cmd + ["--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         universal_newlines=True).stdout.strip()
    print("[sim]", ver)
    rc = subprocess.run(cmd + ["-w", epw, "-d", run_dir, idf], stdout=subprocess.DEVNULL).returncode
    print("[sim] EnergyPlus exit=%d" % rc)
    return rc, ver


def postprocess(tools, run_dir, idf, outdir, manifest):
    sql = os.path.join(run_dir, "eplusout.sql")
    rows_h, rows_c = tools.probe._do_postprocess(sql, idf, os.environ["EPLUS_IDD"], outdir, manifest)
    return rows_h, rows_c


def err_summary(run_dir):
    p = os.path.join(run_dir, "eplusout.err")
    if not os.path.isfile(p):
        return {"err_file": False}
    t = open(p, errors="replace").read()
    m = re.search(r"(\d+) Warning;\s*(\d+) Severe Errors", t)
    return {"err_file": True, "completed": "EnergyPlus Completed Successfully" in t,
            "warnings": int(m.group(1)) if m else None, "severe": int(m.group(2)) if m else None,
            "err_md5": md5_file(p)}


def cleanup_run(run_dir, keep=("eplusout.err", "eplusout.end", "eplustbl.htm", "eplusout.eio",
                                "eplusout.sql")):
    """Delete bulky E+ outputs but KEEP eplusout.sql: the Step-8E aggregator reads it."""
    freed = 0
    for fn in os.listdir(run_dir):
        if fn in keep:
            continue
        p = os.path.join(run_dir, fn)
        if os.path.isfile(p):
            freed += os.path.getsize(p)
            os.remove(p)
    return freed


def fixture_channels(city, negative=False):
    pr = CITIES[city]["pr"]
    off = "v3_office_necb_shift3h.csv" if negative else "v3_office_necb.csv"
    return {
        "office": {"csv": os.path.join(FIXTURES, off), "archetype": "Office_Knowledge", "band": "observed"},
        "retail": {"csv": os.path.join(FIXTURES, "v3_retail_necb.csv"), "pr": pr},
        "hotel": {"csv": os.path.join(FIXTURES, "v3_hotel_necb.csv"), "pr": pr},
        "residential": {"csv": os.path.join(FIXTURES, "v3_residential_necb.csv"), "seed": 42},
    }


def product_channels(scenario, city, seed, check_md5=True):
    """The P10R arm's product files for `scenario`, residential draw re-seeded to `seed`."""
    pr = CITIES[city]["pr"]
    P = PRODUCTS[scenario]
    print("[patch P10R] products dir=%s scenario=%s" % (S7O, scenario))
    paths = {ch: os.path.join(S7O, P[ch][0]) for ch in P}
    if check_md5:
        for ch in P:
            got = md5_file(paths[ch])
            if got != P[ch][1]:
                raise SystemExit("REFUSING: %s product md5 %s != P10R %s (%s)" % (ch, got, P[ch][1], paths[ch]))
            print("[patch P10R] md5 ok %s %s %s" % (ch, P[ch][0], got))
    return {
        "office": {"csv": paths["office"], "archetype": "Office_Knowledge", "band": P["office"][2]},
        "retail": {"csv": paths["retail"], "pr": pr},
        "hotel": {"csv": paths["hotel"], "pr": pr},
        "residential": {"csv": paths["residential"], "seed": int(seed)},
    }
