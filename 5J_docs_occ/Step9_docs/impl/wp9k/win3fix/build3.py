"""Step 9k item 2: build the 38-run pack on _win_2026-10-03 (same set as 9i). Run: py build3.py  (desktop, no UK path)."""
import os, subprocess, shutil, sys, csv, hashlib
os.environ["MODELA_VINTAGE"] = "win_2026-10-03"
TOOLS = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools"
EU = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/%s_win_2026-10-03"
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = HERE + "/pack"
SP = "/speed-scratch/o_iseri/5J/step9c/test_series/"
ES, IT = "ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2"
B = [(ES, "919761afea1827b3"), (ES, "1271cddbf6bd1e8a"), (ES, "0275c53572b2ff9f"), (IT, "504fa19567bbc2b7"), (IT, "1ef46361a8060ff9"), (IT, "13c60875a803e164")]
def run(args):
    r = subprocess.run([sys.executable, TOOLS + "/5thJ_modelA_idf.py"] + args, capture_output=True, text=True)
    print(r.stdout.strip()[-3000:]);
    if r.returncode: print(r.stderr); raise SystemExit("FAILED " + " ".join(args))
    return r.stdout
log = []
for d, s in B:
    os.makedirs("%s/%s/idfs" % (PACK, d), exist_ok=True)
    os.makedirs("%s/schedules/%s" % (PACK, s), exist_ok=True)
    src = EU % d + "/schedules/" + s
    for f in sorted(os.listdir(src)):
        shutil.copy2(src + "/" + f, "%s/schedules/%s/%s" % (PACK, s, f))
    shutil.copy2(EU % d + "/idfs/%s.idf" % s, "%s/%s/idfs/%s_R0.idf" % (PACK, d, s))
    pl = "%s/%s/placement_%s.csv" % (PACK, d, s)
    run(["placement", "--district", d, "--stem", s, "--presence", SP + "test_presence.csv", "--appliance", SP + "test_appliance.csv", "--out", pl])
    out = lambda r: "%s/%s/idfs/%s_%s.idf" % (PACK, d, s, r)
    run(["write", "--district", d, "--stem", s, "--mode", "reproduce", "--out", out("R1")])
    run(["write", "--district", d, "--stem", s, "--mode", "default", "--out", out("D")])
    run(["write", "--district", d, "--stem", s, "--mode", "occupancy", "--placement", pl, "--out", out("O")])
    run(["write", "--district", d, "--stem", s, "--mode", "default", "--fast", "--out", out("DF")])
    run(["write", "--district", d, "--stem", s, "--mode", "occupancy", "--placement", pl, "--fast", "--out", out("OF")])
    if s == "504fa19567bbc2b7":
        run(["write", "--district", d, "--stem", s, "--mode", "reproduce", "--plant-equip", s + "_F0_dwelling_0", "1.1", "--out", out("P1")])
    if s == "919761afea1827b3":
        run(["write", "--district", d, "--stem", s, "--mode", "default", "--plant-drop-window", "--out", out("P2")])
for d in (ES, IT):
    shutil.copy2(EU % d + "/windows.csv", "%s/windows_%s.csv" % (PACK, d))
    print("md5 windows_%s.csv" % d, hashlib.md5(open("%s/windows_%s.csv" % (PACK, d), "rb").read()).hexdigest())
# schedcheck on every written IDF (all but R0 byte copies get it too: R0 is a base copy and also needs its paths)
n = 0
for d, s in B:
    for r in ("R0", "R1", "D", "O", "DF", "OF", "P1", "P2"):
        p = "%s/%s/idfs/%s_%s.idf" % (PACK, d, s, r)
        if os.path.exists(p):
            o = run(["schedcheck", "--idf", p]); n += 1
            assert " 0 missing" in o, p
print("SCHEDCHECK files:", n)
