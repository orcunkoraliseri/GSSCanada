# -*- coding: utf-8 -*-
"""5J building wrapper (WP1). Spain only.

`build(row, household, infiltration_ach=0.5, north_axis_deg=0.0) -> (idf_text, meta)`

Imports `derive` and `build_idf` from 4J `tools/4thJ_step8_idf.py` (never copy-edited)
and applies eight text patches. Every patch prints one line `PATCH <name> OK <detail>` and
raises if its anchor is not found exactly once.

`household` is a dict:
    hid, fold ('es'), n_members, presence_csv (abs path, Step 7, 8,760 values + header),
    appliance_csv (abs path, Step 9 elec fraction file), appliance_peak_w (design level, W),
    peak_w_source (path the number was read from)

Self-test (Parts C and D of the task doc):  python 5thJ_idf.py --selftest
"""
import csv
import glob
import hashlib
import importlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys

TOOLS_4J = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\tools"
if TOOLS_4J not in sys.path:
    sys.path.insert(0, TOOLS_4J)
sys.dont_write_bytecode = True
_s8 = importlib.import_module("4thJ_step8_idf")
derive = _s8.derive
build_idf = _s8.build_idf

ZONE = "Z_DWELLING"          # the box zone name written by 4thJ_step8_idf.build_idf
HEAT_SP_C = 20.0             # D2-2
COOL_SP_C = 26.0             # D2-2
ACTIVITY_W = 120             # ASHRAE 55 sedentary; OpenUBEM base stub (DESIGN step3 line 212)
PATCH_NAMES = ["version", "dual_setpoint", "meters", "infiltration", "north_axis",
               "phi_zero", "people", "appliances"]


class PatchError(RuntimeError):
    pass


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def _once(text, needle, name):
    n = text.count(needle)
    if n != 1:
        raise PatchError("patch %s: anchor %r found %d times, expected 1" % (name, needle, n))


def _sub_once(text, pattern, repl, name, flags=0):
    found = re.findall(pattern, text, flags)
    if len(found) != 1:
        raise PatchError("patch %s: pattern %r matched %d times, expected 1"
                         % (name, pattern, len(found)))
    return re.sub(pattern, repl, text, count=1, flags=flags)


def _read_series(path, n_expected=8760):
    """One header row then n values in [0,1]. Returns the values."""
    with io.open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh.read().splitlines() if ln.strip()]
    vals = [float(x) for x in lines[1:]]
    if len(vals) != n_expected:
        raise PatchError("%s has %d data rows, expected %d" % (path, len(vals), n_expected))
    if min(vals) < -1e-9 or max(vals) > 1.0 + 1e-9:
        raise PatchError("%s has values outside [0,1]" % path)
    return vals


def _sched_file(name, path, n_values):
    """Same layout as 4thJ_step7_schedules.py:406-433 and 4thJ_step9_trigger.py:1077-1088, but
    with the schedule limits `Frac` (the name the box IDF defines) and an absolute path."""
    return ("Schedule:File,\n"
            "  %s,                     !- Name\n"
            "  Frac,                   !- Schedule Type Limits Name\n"
            "  %s,                     !- File Name\n"
            "  1,                      !- Column Number\n"
            "  1,                      !- Rows to Skip at Top\n"
            "  %d,                     !- Number of Hours of Data\n"
            "  Comma,                  !- Column Separator\n"
            "  No,                     !- Interpolate to Timestep\n"
            "  60;                     !- Minutes per Item\n\n"
            % (name, path.replace("\\", "/"), n_values))


def build(row, household, infiltration_ach=0.5, north_axis_deg=0.0):
    lines = []

    def say(name, detail):
        ln = "PATCH %s OK %s" % (name, detail)
        print(ln)
        lines.append(ln)

    d = derive(row)
    text, meta4 = build_idf(d)
    hid = household["hid"]
    fold = household.get("fold", "es")
    hh = "HH_%s_%s" % (fold, hid)

    # 1 version -------------------------------------------------------------------------
    _once(text, "Version, 24.2;", "version")
    text = text.replace("Version, 24.2;", "Version, 23.1;")
    say("version", "Version, 24.2; -> Version, 23.1;")

    # 2 dual setpoint -------------------------------------------------------------------
    _once(text, "ThermostatSetpoint:SingleHeating, T_SP, SCH_HEAT_SP;", "dual_setpoint")
    _once(text, "  ThermostatSetpoint:SingleHeating,\n  T_SP;", "dual_setpoint")
    _once(text, "Schedule:Constant, T_TYPE, CtrlType, 1;", "dual_setpoint")
    _once(text, "Schedule:Constant, SCH_HEAT_SP, Temp, %.1f;" % HEAT_SP_C, "dual_setpoint")
    text = text.replace("ThermostatSetpoint:SingleHeating, T_SP, SCH_HEAT_SP;",
                        "ThermostatSetpoint:DualSetpoint, T_SP, SCH_HEAT_SP, SCH_COOL_SP;")
    text = text.replace("  ThermostatSetpoint:SingleHeating,\n  T_SP;",
                        "  ThermostatSetpoint:DualSetpoint,\n  T_SP;")
    text = text.replace("Schedule:Constant, T_TYPE, CtrlType, 1;",
                        "Schedule:Constant, T_TYPE, CtrlType, 4;\n"
                        "Schedule:Constant, SCH_COOL_SP, Temp, %.1f;" % COOL_SP_C)
    say("dual_setpoint", "DualSetpoint heating %.1f C cooling %.1f C, T_TYPE=4 (SingleHeating removed)"
        % (HEAT_SP_C, COOL_SP_C))

    # 3 meters --------------------------------------------------------------------------
    anchor = "Output:Variable, *, Zone Ideal Loads Supply Air Total Heating Energy, Hourly;"
    _once(text, anchor, "meters")
    text = text.replace(anchor, anchor + "\n"
                        "Output:Variable,*,Zone Ideal Loads Supply Air Total Cooling Energy,Hourly;\n"
                        "Output:Meter,InteriorEquipment:Electricity,Hourly;\n"
                        "Output:Meter,Electricity:Facility,Hourly;")
    say("meters", "added cooling variable, InteriorEquipment:Electricity, Electricity:Facility "
        "(hourly; heating variable kept)")

    # 4 infiltration --------------------------------------------------------------------
    text = _sub_once(text, r"[0-9.]+(,\s+!- Air Changes per Hour)",
                     lambda m: "%.4f%s" % (infiltration_ach, m.group(1)), "infiltration")
    say("infiltration", "ZoneInfiltration:DesignFlowRate ACH = %.4f" % infiltration_ach)

    # 5 north axis ----------------------------------------------------------------------
    text = _sub_once(text, r"(Building,\n  [A-Za-z0-9_]+,\n  )[0-9.\-]+(,\n  City,)",
                     lambda m: "%s%.4f%s" % (m.group(1), north_axis_deg, m.group(2)), "north_axis")
    say("north_axis", "Building North Axis = %.4f deg" % north_axis_deg)

    # 6 phi zero ------------------------------------------------------------------------
    text = _sub_once(text, r"(E_PHI_INT,[^;]*?)[0-9.]+(,\s+!- Design Level \{W\})",
                     lambda m: "%s0.0000%s" % (m.group(1), m.group(2)), "phi_zero",
                     flags=re.S)
    say("phi_zero", "OtherEquipment E_PHI_INT kept, design level -> 0.0000 W (was phi_int*A_C_Ref = %.4f W)"
        % (d["phi_int"] * d["a_ref"]))

    # 7 people --------------------------------------------------------------------------
    pres = household["presence_csv"]
    pvals = _read_series(pres)
    n_people = int(household["n_members"])
    people = ("Schedule:Constant, Activity_Level, , %d;\n\n" % ACTIVITY_W
              + _sched_file(hh + "_Presence", pres, 8760)
              + "People,\n"
                "  %s_People,              !- Name\n"
                "  %s,                     !- Zone or ZoneList Name\n"
                "  %s_Presence,            !- Number of People Schedule Name\n"
                "  People,                 !- Number of People Calculation Method\n"
                "  %d,                     !- Number of People\n"
                "  ,                       !- People per Zone Floor Area\n"
                "  ,                       !- Zone Floor Area per Person\n"
                "  0.3,                    !- Fraction Radiant\n"
                "  ,                       !- Sensible Heat Fraction\n"
                "  Activity_Level;         !- Activity Level Schedule Name\n\n"
                % (hh, ZONE, hh, n_people))
    say("people", "Schedule:File %s_Presence (8760 rows, mean %.4f) + People %d, radiant 0.3, activity %d W"
        % (hh, sum(pvals) / len(pvals), n_people, ACTIVITY_W))

    # 8 appliances ----------------------------------------------------------------------
    app = household["appliance_csv"]
    avals = _read_series(app)
    peak_w = float(household["appliance_peak_w"])
    appl = (_sched_file(hh + "_Appliance", app, 8760)
            + "ElectricEquipment,\n"
              "  %s_Appliances,           !- Name\n"
              "  %s,                      !- Zone or ZoneList Name\n"
              "  %s_Appliance,            !- Schedule Name\n"
              "  EquipmentLevel,          !- Design Level Calculation Method\n"
              "  %.4f,                    !- Design Level {W}\n"
              "  ,                        !- Watts per Zone Floor Area\n"
              "  ,                        !- Watts per Person\n"
              "  0.0,                     !- Fraction Latent\n"
              "  1.0,                     !- Fraction Radiant\n"
              "  0.0;                     !- Fraction Lost\n\n"
              % (hh, ZONE, hh, peak_w))
    say("appliances", "Schedule:File %s_Appliance (8760 rows) + ElectricEquipment %.4f W in %s; "
        "no WaterUse:Equipment, no DHW schedule (D2-7)" % (hh, peak_w, ZONE))

    text = text.rstrip("\n") + "\n\n" + people + appl
    meta = {
        "row_code": d["code"],
        "arguments": {"infiltration_ach": infiltration_ach, "north_axis_deg": north_axis_deg,
                      "heat_sp_c": HEAT_SP_C, "cool_sp_c": COOL_SP_C, "activity_w": ACTIVITY_W},
        "household": {k: household[k] for k in household},
        "inputs": {
            "presence_csv": {"path": pres, "md5": md5(pres)},
            "appliance_csv": {"path": app, "md5": md5(app)},
            "step8_idf_tool": {"path": os.path.join(TOOLS_4J, "4thJ_step8_idf.py"),
                               "md5": md5(os.path.join(TOOLS_4J, "4thJ_step8_idf.py"))},
        },
        "patch_lines": lines,
        "step8_meta": {"clamped": meta4["clamped"], "wwr_over_limit": meta4["wwr_over_limit"]},
        "presence_annual_mean": sum(pvals) / len(pvals),
        "appliance_fraction_sum": sum(avals),
    }
    return text, meta


# ------------------------------------------------------------------------------------------
# Part D: the gate
# ------------------------------------------------------------------------------------------
_CHECK_ANCHORS = [
    ("Version, 23.1;", "version"),
    ("ThermostatSetpoint:DualSetpoint", "dual_setpoint"),
    ("Schedule:Constant, T_TYPE, CtrlType, 4;", "dual_setpoint"),
    ("Zone Ideal Loads Supply Air Total Cooling Energy", "meters"),
    ("Output:Meter,InteriorEquipment:Electricity,Hourly;", "meters"),
    ("Output:Meter,Electricity:Facility,Hourly;", "meters"),
    ("\nPeople,\n", "people"),
    ("_Presence,", "people"),
    ("ElectricEquipment,", "appliances"),
    ("_Appliance,", "appliances"),
    ("E_PHI_INT,", "phi_zero"),
]


def check_patches(idf_text, printed_lines):
    """Returns ('PASS'|'FAIL', [reasons]). FAIL if any of the 8 patch lines is absent or any
    anchor object is missing from the SAVED IDF."""
    reasons = []
    for name in PATCH_NAMES:
        if not any(ln.startswith("PATCH %s OK" % name) for ln in printed_lines):
            reasons.append("missing printed line PATCH %s" % name)
    for needle, name in _CHECK_ANCHORS:
        if needle not in idf_text:
            reasons.append("anchor for %s absent from IDF: %r" % (name, needle.strip()))
    if "Version, 24.2;" in idf_text or "ThermostatSetpoint:SingleHeating" in idf_text:
        reasons.append("an unpatched 4J object is still in the IDF")
    if "WaterUse:Equipment" in idf_text:
        reasons.append("WaterUse:Equipment present (D2-7 forbids it)")
    if not re.search(r"E_PHI_INT,[^;]*?0\.0000,\s+!- Design Level \{W\}", idf_text, re.S):
        reasons.append("E_PHI_INT design level is not 0")
    m = re.search(r"%s_People,.*?\n\s+(\d+),\s+!- Number of People\b" % "HH_[a-z]+_[0-9]+", idf_text, re.S)
    if not m:
        reasons.append("People object has no head-count")
    return ("FAIL" if reasons else "PASS"), reasons


# ------------------------------------------------------------------------------------------
# Part C: local EnergyPlus runs and the report
# ------------------------------------------------------------------------------------------
EPLUS = "C:/EnergyPlusV23-1-0/energyplus.exe"
EPW = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/es_madrid_2009_2010_y2010.epw"
J_PER_KWH = 3.6e6


def run_energyplus(idf_path, run_dir):
    os.makedirs(run_dir, exist_ok=True)
    cp = subprocess.run([EPLUS, "-w", EPW, "-d", run_dir, "-x", "-r", idf_path],
                        cwd=run_dir, capture_output=True, text=True)
    return cp.returncode


def summarise_run(run_dir):
    out = {"dir": run_dir}
    err = io.open(os.path.join(run_dir, "eplusout.err"), encoding="utf-8", errors="replace").read()
    out["completed_successfully"] = "EnergyPlus Completed Successfully" in err
    m = re.search(r"Completed Successfully-- (\d+) Warning; (\d+) Severe Errors", err)
    out["warnings"], out["severe"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    rows = list(csv.reader(io.open(os.path.join(run_dir, "eplusout.csv"), encoding="utf-8")))
    hdr, data = rows[0], rows[1:]

    def col(sub):
        idx = [i for i, h in enumerate(hdr) if sub in h]
        if len(idx) != 1:
            raise RuntimeError("column %r matched %d columns in %s" % (sub, len(idx), run_dir))
        return [float(r[idx[0]]) for r in data]
    series = {
        "heating": col("Zone Ideal Loads Supply Air Total Heating Energy"),
        "cooling": col("Zone Ideal Loads Supply Air Total Cooling Energy"),
        "appliance": col("InteriorEquipment:Electricity"),
        "facility_elec": col("Electricity:Facility"),
    }
    for k, v in series.items():
        out["rows_" + k] = len(v)
        out["kwh_" + k] = sum(v) / J_PER_KWH
    # annual sum = sum of the hourly values: recomputed a second, independent way (math.fsum)
    out["kwh_appliance_fsum"] = math.fsum(series["appliance"]) / J_PER_KWH
    out["hourly"] = series
    return out


def _by_dwelling(path, hid):
    for r in csv.DictReader(io.open(path, encoding="utf-8")):
        if r["hid"] == hid:
            return r
    raise RuntimeError("hid %s not in %s" % (hid, path))


def _design_level_from_idf(path, hid):
    txt = io.open(path, encoding="utf-8").read()
    m = re.search(r"HH_es_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % hid, txt, re.S)
    if not m:
        raise RuntimeError("no ElectricEquipment for %s in %s" % (hid, path))
    return float(m.group(1))


def _household(w, variant, hid):
    """Household dict from the wp1_test Step 9 output dir (`step9_<variant>`)."""
    s9 = os.path.join(w, "step9_" + variant)
    pres_src = os.path.join(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step7_docs\outputs_step7\schedules"
        r"\leg5_es_independent_seed1_cal2010", "presence_HH_es_%s.csv" % hid)
    inp = os.path.join(w, "inputs")
    os.makedirs(inp, exist_ok=True)
    pres = os.path.join(inp, os.path.basename(pres_src))
    if not os.path.exists(pres):
        shutil.copyfile(pres_src, pres)
    nm = int(_by_dwelling(os.path.join(s9, "enduse_by_dwelling_es.csv"), hid)["n_members"])
    peak = _design_level_from_idf(os.path.join(s9, "step9_objects_es.idf"), hid)
    return {"hid": hid, "fold": "es", "n_members": nm, "presence_csv": pres,
            "presence_src": pres_src,
            "appliance_csv": os.path.join(s9, "enduse_profiles", "es", "elec_HH_es_%s.csv" % hid),
            "appliance_peak_w": peak,
            "peak_w_source": os.path.join(s9, "step9_objects_es.idf")}


def selftest(w):
    T = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step8_docs\outputs_step8"
    rows, _ = _s8.load_rows(T, "es")
    row = [r for r in rows if ".SFH." in r["Code_Building"]][0]
    hids = sorted(n[len("presence_HH_es_"):-4] for n in os.listdir(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step7_docs\outputs_step7\schedules"
        r"\leg5_es_independent_seed1_cal2010") if n.startswith("presence_HH_es_"))[:2]
    h1, h2 = hids
    cases = [("H1_act2", "act2", h1), ("H2_act2", "act2", h2),
             ("H1_act2_rep", "act2", h1), ("H1_noact2", "no_act2", h1)]
    res = {}
    report = ["# wp1 test report (Spain, Madrid 2010 ERA5, building %s)\n" % row["Code_Building"],
              "EnergyPlus 23.1, EPW %s\nH1 = %s, H2 = %s\n" % (EPW, h1, h2)]
    for name, variant, hid in cases:
        hh = _household(w, variant, hid)
        idf, meta = build(row, hh)
        run_dir = os.path.join(w, "run_" + name)
        os.makedirs(run_dir, exist_ok=True)
        idf_path = os.path.join(w, name + ".idf")
        io.open(idf_path, "w", encoding="utf-8", newline="\n").write(idf)
        meta["idf_md5"] = md5(idf_path)
        io.open(os.path.join(w, name + ".meta.json"), "w", encoding="utf-8").write(
            json.dumps(meta, indent=2, default=str))
        rc = run_energyplus(idf_path, run_dir)
        s = summarise_run(run_dir)
        s["rc"] = rc
        s["design_w"] = hh["appliance_peak_w"]
        s["frac_sum"] = meta["appliance_fraction_sum"]
        s["rederived_kwh"] = s["design_w"] * s["frac_sum"] / 1000.0
        s["patch_lines"] = meta["patch_lines"]
        s["idf"] = idf_path
        s["check"] = check_patches(io.open(idf_path, encoding="utf-8").read(), meta["patch_lines"])
        res[name] = s
        report.append("## %s (hid %s, %s)\n- rc %s, Completed Successfully: %s, severe %s, warnings %s\n"
                      "- hourly rows: heating %d, cooling %d, appliance %d, facility %d\n"
                      "- annual kWh: heating %.3f, cooling %.3f, appliance %.3f (fsum %.3f), Electricity:Facility %.3f\n"
                      "- re-derivation: E+ appliance %.3f kWh vs peak %.4f W x sum(fraction) %.4f / 1000 = %.3f kWh\n"
                      "- gate check_patches: %s %s\n"
                      % (name, hid, variant, rc, s["completed_successfully"], s["severe"], s["warnings"],
                         s["rows_heating"], s["rows_cooling"], s["rows_appliance"], s["rows_facility_elec"],
                         s["kwh_heating"], s["kwh_cooling"], s["kwh_appliance"], s["kwh_appliance_fsum"],
                         s["kwh_facility_elec"], s["kwh_appliance"], s["design_w"], s["frac_sum"],
                         s["rederived_kwh"], s["check"][0], s["check"][1]))
    a, b, r_, n = res["H1_act2"], res["H2_act2"], res["H1_act2_rep"], res["H1_noact2"]
    must = []
    must.append(("heating>0 and cooling>0 (all four)",
                 all(x["kwh_heating"] > 0 and x["kwh_cooling"] > 0 for x in res.values())))
    must.append(("H1 and H2 differ in heating, cooling, appliance",
                 all(abs(a["kwh_" + k] - b["kwh_" + k]) > 1e-6 for k in ("heating", "cooling", "appliance"))))
    same = all(a["hourly"][k] == r_["hourly"][k] for k in ("heating", "cooling", "appliance"))
    maxd = max(abs(x - y) for k in ("heating", "cooling", "appliance")
               for x, y in zip(a["hourly"][k], r_["hourly"][k]))
    must.append(("H1 act2 and replicate identical (max abs hourly diff %.3g J)" % maxd, same))
    must.append(("H1 act2 appliance >= H1 no-act2 (%.3f vs %.3f kWh)" % (a["kwh_appliance"], n["kwh_appliance"]),
                 a["kwh_appliance"] >= n["kwh_appliance"]))
    must.append(("all runs Completed Successfully, 0 severe", all(x["completed_successfully"] and x["severe"] == 0
                                                                for x in res.values())))
    must.append(("all hourly rows = 8760", all(x["rows_" + k] == 8760 for x in res.values()
                                               for k in ("heating", "cooling", "appliance", "facility_elec"))))
    must.append(("sum of hourly = annual (two summations agree within 1e-6 kWh)",
                 all(abs(x["kwh_appliance"] - x["kwh_appliance_fsum"]) < 1e-6 for x in res.values())))
    must.append(("re-derivation within 0.5 % (E+ vs peak x sum(frac)/1000)",
                 all(abs(x["kwh_appliance"] - x["rederived_kwh"]) <= 0.005 * x["rederived_kwh"]
                     for x in res.values())))
    report.append("## Must hold\n" + "\n".join("- %s: %s" % ("PASS" if ok else "FAIL", t) for t, ok in must))

    # Part D: gate seen failing
    idf_text = io.open(res["H1_act2"]["idf"], encoding="utf-8").read()
    lines = res["H1_act2"]["patch_lines"]
    no_people = re.sub(r"\nPeople,\n.*?Activity_Level;[^\n]*\n", "\n", idf_text, flags=re.S)
    assert no_people != idf_text
    g1 = check_patches(no_people, lines)
    g2 = check_patches(idf_text, [ln for ln in lines if not ln.startswith("PATCH dual_setpoint")])
    g3 = check_patches(idf_text, lines)
    report.append("\n## Gate check_patches\n- (1) IDF with People deleted: %s %s\n"
                  "- (2) printed lines without PATCH dual_setpoint: %s %s\n- (3) real test IDF: %s %s"
                  % (g1[0], g1[1], g2[0], g2[1], g3[0], g3[1]))
    io.open(os.path.join(w, "test_report.md"), "w", encoding="utf-8").write("\n".join(report) + "\n")
    print("\n".join(report))
    print("GATE (1):", g1)
    print("GATE (2):", g2)
    print("GATE (3):", g3)
    return 0 if all(ok for _, ok in must) and g1[0] == "FAIL" and g2[0] == "FAIL" and g3[0] == "PASS" else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest(r"C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\wp1_test"))
    print(__doc__)
