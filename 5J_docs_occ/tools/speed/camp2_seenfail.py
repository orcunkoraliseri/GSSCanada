# -*- coding: utf-8 -*-
"""Part 2, Part B seen-failing tests for camp_integrity.py on SCRATCH copies (Spain runs only). Speed job only.
Builds scratch trees under R/integrity/scratch/<test>/ from 4 real runs (+ 1 replicate), runs camp_integrity.py on each:
  control : unchanged copy                          -> must PASS (exit 0)
  T1      : one extracted file truncated by 100 bytes -> C03 must FAIL
  T2      : one done.json deleted                     -> C01 must FAIL
  T3      : one flat's equipment series copied onto another flat with a different household (done.json md5 updated so C03 passes) -> C09 must FAIL
  T4      : one byte of one household file changed    -> C02 (cache key) must FAIL
Prints SEENFAIL <test> expected=<check> got=<status> exit=<rc>.
"""
import gzip, io, json, os, shutil, subprocess, sys, hashlib
import pandas as pd

R = "/speed-scratch/o_iseri/5J/campaign/"
S = R + "integrity/scratch/"
HH = "/speed-scratch/o_iseri/5J/households/inputs/"
PY = "/speed-scratch/o_iseri/envs/step4/bin/python"
IDS = ["es_madrid_B01_dev_1", "es_madrid_B01_dev_1_rep1", "es_madrid_B01_b0_1", "es_madrid_B21_dev_1"]
ARR = "es_madrid_2010"
for i in IDS:
    assert i.startswith("es_"), "Spain only"


def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def placements():
    out = {}
    import csv
    for r in csv.DictReader(io.open(R + "in/campaign_runs_es.csv", encoding="utf-8")):
        if r["run_id"] in IDS:
            out[r["run_id"]] = r["placement"]
    return out


def build(tree):
    if os.path.exists(tree):
        shutil.rmtree(tree)
    for d in ("root/done", "root/extracted/" + ARR, "root/runs", "root/failed", "hh"):
        os.makedirs(tree + d)
    toks = set()
    for rid, pl in placements().items():
        for item in pl.split(";"):
            t = item.split(":", 1)[1]
            toks.add(t if t.startswith("es_") else "es_" + t)
    for t in sorted(toks):
        shutil.copytree(HH + t, tree + "hh/" + t)       # copytree keeps file contents; mtimes not needed (md5 is by content)
    for rid in IDS:
        for f in ("done/%s.json" % rid, "done/%s.err" % rid, "extracted/%s/%s.csv.gz" % (ARR, rid), "extracted/%s/%s.dwellings.csv" % (ARR, rid)):
            shutil.copy2(R + f, tree + "root/" + f)
    io.open(tree + "ids.txt", "w").write("\n".join(IDS) + "\n")


def run(tree):
    env = dict(os.environ, CAMP_ROOT=tree + "root", CAMP_HH=tree + "hh")
    p = subprocess.run([PY, "-u", R + "camp_integrity.py", "--ids", tree + "ids.txt", "--workers", "1"], env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=R, universal_newlines=True)
    return p.returncode, p.stdout


def report(name, expected, tree):
    rc, out = run(tree)
    lines = out.splitlines()
    got = "?"
    for ln in lines:
        if ln.startswith("CHECK %s " % expected[:3]) if expected != "none" else False:
            got = ln.split()[3]
    summ = [ln for ln in lines if ln.startswith("SUMMARY")]
    print("SEENFAIL %s expected=%s got=%s exit=%d %s" % (name, expected, got, rc, summ[-1] if summ else "NO SUMMARY LINE"))
    for ln in lines:
        if ln.startswith("CHECK") and (" FAIL " in ln or " NOT_EVALUABLE " in ln):
            print("   ", ln[:300])
    if not summ:
        print("\n".join(lines[-15:]))
    return rc, got


res = {}
# control
t = S + "control/"
build(t)
rc, got = report("control", "none", t)
res["control"] = (rc == 0)
# T1 truncate
t = S + "T1/"
build(t)
p = t + "root/extracted/%s/es_madrid_B21_dev_1.csv.gz" % ARR
sz = os.path.getsize(p)
with open(p, "r+b") as fh:
    fh.truncate(sz - 100)
print("T1 truncated", p, sz, "->", os.path.getsize(p))
rc, got = report("T1_truncate_100_bytes", "C03", t)
res["T1"] = (rc != 0 and got == "FAIL")
# T2 delete done.json
t = S + "T2/"
build(t)
os.remove(t + "root/done/es_madrid_B21_dev_1.json")
rc, got = report("T2_delete_done_json", "C01", t)
res["T2"] = (rc != 0 and got == "FAIL")
# T3 copy one flat's series onto another flat
t = S + "T3/"
build(t)
p = t + "root/extracted/%s/es_madrid_B21_dev_1.csv.gz" % ARR
raw = gzip.open(p, "rb").read().decode("utf-8")
hdr = [ln for ln in raw.splitlines() if ln.startswith("#")]
df = pd.read_csv(io.StringIO(raw), comment="#")
eq0 = df.loc[df["dwelling"] == 0, "equipment_kwh"].to_numpy().copy()
df.loc[df["dwelling"] == 1, "equipment_kwh"] = eq0
with open(p, "wb") as raw_fh:
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw_fh, mtime=0)
    txt = io.TextIOWrapper(gz, encoding="utf-8", newline="")
    txt.write("\n".join(hdr) + "\n")
    df.to_csv(txt, index=False, float_format="%.8g")
    txt.flush(); txt.detach(); gz.close()
jp = t + "root/done/es_madrid_B21_dev_1.json"
rec = json.load(io.open(jp, encoding="utf-8"))
rec["extracted"]["csv_gz"]["md5"] = md5f(p)
rec["extracted"]["csv_gz"]["bytes"] = os.path.getsize(p)
json.dump(rec, io.open(jp, "w", encoding="utf-8"), indent=1)
print("T3 flat 1 equipment series replaced by flat 0 series; done.json md5 and bytes updated")
rc, got = report("T3_copy_flat_series", "C09", t)
res["T3"] = (rc != 0 and got == "FAIL")
# T4 one byte of a household file
t = S + "T4/"
build(t)
hj = json.load(io.open(t + "hh/es_04065/household.json", encoding="utf-8")) if os.path.exists(t + "hh/es_04065/household.json") else None
target = None
if hj:
    target = t + "hh/es_04065/" + hj["elec_file"]
b = bytearray(open(target, "rb").read())
b[len(b) // 2] ^= 0x01
open(target, "wb").write(bytes(b))
print("T4 flipped one byte in", target)
rc, got = report("T4_household_byte", "C02", t)
res["T4"] = (rc != 0 and got == "FAIL")
print("SEENFAIL_ALL", res, "ALL_SEEN_FAILING" if all(res.values()) else "NOT_ALL")
sys.exit(0 if all(res.values()) else 1)
