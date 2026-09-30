# -*- coding: utf-8 -*-
"""Gate 'relative = absolute' for the 5J pilot inputs (Spain). Local EnergyPlus, one input.
 A  absolute-path IDF   (pilot/abs_idf/<id>.idf, cwd = its own folder)
 B  relative-path IDF   (copy of pilot/inputs/<id>/, cwd = that folder)
 C  seen-failing case   (copy of B, one schedule name points at a missing file)  -> must stop with severe error
 D  comparator planted  (one hourly value of A changed)                           -> comparator must say DIFFERENT
Writes pilot/gate/gate_report.txt. Exit 0 only if A==B, C fails with a severe error, D detected.
"""
import hashlib
import importlib
import io
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
idf = importlib.import_module("5thJ_idf")

PILOT = r"C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\pilot"
IID = "es_B16__es_00494"
G = os.path.join(PILOT, "gate")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def run(folder, name):
    d = os.path.join(G, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(folder, d)
    out = os.path.join(d, "out")
    os.makedirs(out)
    rc = idf.run_energyplus(os.path.join(d, "in.idf"), out)
    return d, out, rc


def same(a, b):
    return all(a["hourly"][k] == b["hourly"][k] for k in ("heating", "cooling", "appliance"))


def main():
    rep = []

    def say(s):
        print(s)
        rep.append(s)
    if os.path.isdir(G):
        shutil.rmtree(G)
    os.makedirs(G)
    # A: absolute
    a_src = os.path.join(G, "_abs_src")
    os.makedirs(a_src)
    shutil.copyfile(os.path.join(PILOT, "abs_idf", IID + ".idf"), os.path.join(a_src, "in.idf"))
    a_txt = open(os.path.join(a_src, "in.idf"), encoding="utf-8").read()
    n_abs = len(re.findall(r"[A-Za-z]:/[^\n]*!- File Name", a_txt))
    say("A idf has %d absolute File Name paths; idf_md5 %s" % (n_abs, md5(os.path.join(a_src, "in.idf"))))
    assert n_abs == 2
    da, oa, rca = run(a_src, "A_abs")
    # B: relative
    db, ob, rcb = run(os.path.join(PILOT, "inputs", IID), "B_rel")
    b_txt = open(os.path.join(db, "in.idf"), encoding="utf-8").read()
    say("B idf has %d relative File Name values, idf_md5 %s"
        % (len(re.findall(r"\n\s+[A-Za-z0-9_.\-]+\.csv,\s+!- File Name", b_txt)), md5(os.path.join(db, "in.idf"))))
    sa, sb = idf.summarise_run(oa), idf.summarise_run(ob)
    for tag, s, rc in (("A", sa, rca), ("B", sb, rcb)):
        say("%s rc=%s completed=%s severe=%s warnings=%s rows=%d/%d/%d kWh heat=%.3f cool=%.3f appl=%.3f"
            % (tag, rc, s["completed_successfully"], s["severe"], s["warnings"], s["rows_heating"],
               s["rows_cooling"], s["rows_appliance"], s["kwh_heating"], s["kwh_cooling"], s["kwh_appliance"]))
    maxd = max(abs(x - y) for k in ("heating", "cooling", "appliance")
               for x, y in zip(sa["hourly"][k], sb["hourly"][k]))
    ok_ab = same(sa, sb) and sa["rows_heating"] == 8760
    say("COMPARE A vs B: hourly heating, cooling, appliance identical=%s (max abs diff %.3g J, 8760 rows); "
        "eplusout.csv md5 A %s B %s" % (ok_ab, maxd, md5(os.path.join(oa, "eplusout.csv")),
                                         md5(os.path.join(ob, "eplusout.csv"))))
    # D: comparator seen failing
    bad = {"hourly": {k: list(v) for k, v in sa["hourly"].items()}}
    bad["hourly"]["appliance"][4000] += 1.0
    d_detect = not same(bad, sb)
    say("D planted difference (appliance hour 4000 + 1 J): comparator says identical=%s -> %s"
        % (not d_detect, "detected" if d_detect else "NOT DETECTED"))
    # C: missing file
    c_src = os.path.join(G, "_c_src")
    shutil.copytree(os.path.join(PILOT, "inputs", IID), c_src)
    t = open(os.path.join(c_src, "in.idf"), encoding="utf-8").read()
    t2, n = re.subn(r"presence_HH_es_00494\.csv(,\s+!- File Name)", r"missing_presence.csv\1", t)
    assert n == 1
    open(os.path.join(c_src, "in.idf"), "w", encoding="utf-8", newline="\n").write(t2)
    dc, oc, rcc = run(c_src, "C_missing")
    err = open(os.path.join(oc, "eplusout.err"), encoding="utf-8", errors="replace").read()
    sev = [ln.strip() for ln in err.splitlines() if "** Severe" in ln or "**  Fatal" in ln]
    c_ok = rcc != 0 and "EnergyPlus Completed Successfully" not in err and len(sev) > 0
    say("C missing schedule file: rc=%s completed_successfully=%s; err lines:" % (
        rcc, "EnergyPlus Completed Successfully" in err))
    for ln in sev[:4]:
        say("   " + ln)
    verdict = ok_ab and c_ok and d_detect and rca == 0 and rcb == 0
    say("GATE relative=absolute: %s (A==B %s; missing-file stops with severe %s; planted diff detected %s)"
        % ("PASS" if verdict else "FAIL", ok_ab, c_ok, d_detect))
    io.open(os.path.join(G, "gate_report.txt"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
