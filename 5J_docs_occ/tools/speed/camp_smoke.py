# -*- coding: utf-8 -*-
"""5J campaign smoke job (ONE Speed job). Works in a scratch tree R/smoke/ (CAMP_ROOT), never touches R/done.
Every item prints one line: SMOKE_ITEM <n> PASS|FAIL <what>; ends with SMOKE SUMMARY pass=.. fail=..; exit 1 on any FAIL or crash.
"""
import csv, hashlib, io, json, os, re, shutil, subprocess, sys, traceback, platform
import camp_common as cc

R = cc.R
S = R + "smoke/"
PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN_DESIGN_MD5 = "2594867b0fe6cf24191c00e0c83d91a7"
TABLE_MD5 = {"es": "b4d5b42eb6220b25daef7f2a7cff18d1", "it": "e9ddcf105c2aca2958439e70cd8e3dfb"}
SMOKE_ES = ["es_madrid_B01_dev_1", "es_madrid_B21_dev_1", "es_madrid_B01_b0_1", "es_madrid_B01_dev_1_rep1"]
SMOKE_IT = ["it_bologna_B01_dev_1"]
RES = []


def item(ok, what):
    RES.append(bool(ok))
    print("SMOKE_ITEM %d %s %s" % (len(RES), "PASS" if ok else "FAIL", what))
    sys.stdout.flush()


def sh(args, env_extra):
    env = dict(os.environ)
    env.update(env_extra)
    p = subprocess.run([PY, "-u"] + args, cwd=HERE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout


def main():
    print("python", sys.version.split()[0], "host", platform.node(), "start", cc.now())
    # ---- 0. frozen inputs
    d = cc.md5(R + "in/campaign_design.md")
    item(d == FROZEN_DESIGN_MD5, "frozen design md5 %s (expected %s)" % (d, FROZEN_DESIGN_MD5))
    for c in ("es", "it"):
        m = cc.md5(R + "in/campaign_runs_%s.csv" % c)
        item(m == TABLE_MD5[c], "run table %s md5 %s (expected %s)" % (c, m, TABLE_MD5[c]))
    bad = []
    for arr in cc.ARRAYS:
        got = cc.md5(cc.epw_path(arr))
        if got != cc.epw_expected_md5(arr):
            bad.append((arr, got))
    item(not bad, "six EPW md5 equal climates.csv (mismatches=%s)" % bad)
    st = cc.static()
    item(all(r["country"] in ("es", "it") for r in st["bt"].values()) and len(st["bt"]) == 80 and len(st["cl"]) == 6,
         "staged buildings rows=%d (es+it only), climates rows=%d" % (len(st["bt"]), len(st["cl"])))

    # ---- 1. mini tables from the real tables
    if os.path.exists(S):
        shutil.rmtree(S)
    os.makedirs(S + "in")
    for c, ids in (("es", SMOKE_ES), ("it", SMOKE_IT)):
        rows = cc.read_csv(R + "in/campaign_runs_%s.csv" % c)
        pick = [r for r in rows if r["run_id"] in ids]
        item(sorted(r["run_id"] for r in pick) == sorted(ids), "smoke runs found in the real %s table: %s" % (c, [r["run_id"] for r in pick]))
        with io.open(S + "in/campaign_runs_%s.csv" % c, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(pick)
    env = {"CAMP_ROOT": S, "CAMP_TABLES": S + "in/"}

    # ---- 2. plan, tasks
    rc, out = sh(["camp_plan.py"], env)
    print(out)
    m = re.search(r"PLAN total=(\d+) done=(\d+) todo=(\d+)", out)
    item(rc == 0 and m and m.groups() == ("5", "0", "5"), "smoke plan before any run: %s" % (m.group(0) if m else "NO PLAN LINE"))
    summ = {}
    for arr in ("es_madrid_2010", "it_bologna_2014"):
        rc, out = sh(["camp_task.py", arr, "1"], env)
        print(out)
        m = re.search(r"SUMMARY array=(\S+) block=(\d+) planned=(\d+) not_run=(\d+) ran_failed=(\d+) ran_passed=(\d+)", out)
        summ[arr] = m
        exp = ("4" if arr.startswith("es") else "1")
        item(rc == 0 and m and m.group(3) == exp and m.group(4) == "0" and m.group(5) == "0" and m.group(6) == exp,
             "camp_task %s block 1 end to end: %s (rc=%s)" % (arr, m.group(0) if m else "NO SUMMARY", rc))

    # ---- 3. what the done files say
    alls = SMOKE_ES + SMOKE_IT
    okj = True
    notes = []
    for rid in alls:
        arr = "es_madrid_2010" if rid.startswith("es") else "it_bologna_2014"
        jp = S + "done/%s.json" % rid
        if not os.path.exists(jp):
            okj = False
            notes.append("%s no done json" % rid)
            continue
        j = json.load(io.open(jp, encoding="utf-8"))
        if j["status"] != "pass" or not all(c["ok"] for c in j["checks"]):
            okj = False
            notes.append("%s status %s" % (rid, j["status"]))
        for k in ("csv_gz", "dwellings_csv"):
            f = S + "extracted/" + j["extracted"][k]["file"]
            if cc.md5(f) != j["extracted"][k]["md5"] or os.path.getsize(f) != j["extracted"][k]["bytes"]:
                okj = False
                notes.append("%s %s md5/bytes differ from the recount" % (rid, k))
        for key in ("run_id", "status", "seconds", "max_rss_kb", "cache_key", "idf_md5", "epw_md5", "household_md5s", "extracted",
                    "energyplus_version", "clock_origin"):
            if key not in j:
                okj = False
                notes.append("%s missing field %s" % (rid, key))
        if os.path.exists(S + "runs/%s" % rid):
            okj = False
            notes.append("%s raw run folder still there after pass" % rid)
    item(okj, "done json for all 5 runs: status pass, every check ok, all required fields, md5+bytes equal a recount inside this job, raw folder deleted (%s)" % notes)
    j0 = json.load(io.open(S + "done/es_madrid_B21_dev_1.json", encoding="utf-8"))
    print("INFO MFH run checks:", [(c["name"], c["ok"]) for c in j0["checks"]])
    a = json.load(io.open(S + "done/es_madrid_B01_dev_1.json", encoding="utf-8"))
    b = json.load(io.open(S + "done/es_madrid_B01_dev_1_rep1.json", encoding="utf-8"))
    print("INFO replicate vs its original: extracted md5 equal = %s (%s vs %s)" % (
        a["extracted"]["csv_gz"]["md5"] == b["extracted"]["csv_gz"]["md5"], a["extracted"]["csv_gz"]["md5"], b["extracted"]["csv_gz"]["md5"]))
    print("INFO seconds per run:", {r: json.load(io.open(S + "done/%s.json" % r))["seconds"] for r in alls})

    # ---- 4. rerun the plan: the 5 must count as DONE
    rc, out = sh(["camp_plan.py"], env)
    m = re.search(r"PLAN total=(\d+) done=(\d+) todo=(\d+)", out)
    item(rc == 0 and m and m.groups() == ("5", "5", "0"), "plan after the runs counts all 5 as DONE: %s" % (m.group(0) if m else "NO PLAN LINE"))

    # ---- 5. cache key seen failing: scratch copy of the household folders, one byte changed
    hs = set()
    by_cc = {}
    for rid in alls:
        row = [r for r in cc.read_csv(S + "in/campaign_runs_%s.csv" % rid[:2]) if r["run_id"] == rid][0]
        for t in cc.parse_placement(row["placement"]).values():
            hs.add(cc.hh_folder(t, rid[:2]))
    sc = S + "hh_scratch/"
    os.makedirs(sc)
    for f in sorted(hs):
        shutil.copytree(f.rstrip("/"), sc + os.path.basename(f.rstrip("/")))
    env2 = {"CAMP_ROOT": S, "CAMP_TABLES": S + "in/", "CAMP_HH": sc, "CAMP_PLAN": S + "plan_scratch/"}
    rc, out = sh(["camp_plan.py"], env2)
    m = re.search(r"PLAN total=(\d+) done=(\d+) todo=(\d+)", out)
    item(rc == 0 and m and m.groups() == ("5", "5", "0"), "control: unchanged scratch copy of the household folders is a cache HIT (all 5 DONE): %s" % (m.group(0) if m else out[-300:]))
    # change one byte of one household file used by the MFH run
    row = [r for r in cc.read_csv(S + "in/campaign_runs_es.csv") if r["run_id"] == "es_madrid_B21_dev_1"][0]
    tok = list(cc.parse_placement(row["placement"]).values())[3]
    target = sc + "es_" + tok + "/elec_HH_es_%s.csv" % tok
    bts = bytearray(open(target, "rb").read())
    pos = len(bts) // 2
    while not (48 <= bts[pos] <= 56):
        pos += 1
    old = bts[pos]
    bts[pos] = old + 1
    open(target, "wb").write(bytes(bts))
    print("INFO changed one byte of %s at offset %d: %r -> %r" % (target, pos, chr(old), chr(old + 1)))
    rc, out = sh(["camp_plan.py"], env2)
    m = re.search(r"PLAN total=(\d+) done=(\d+) todo=(\d+)", out)
    todo = io.open(S + "plan_scratch/todo_ids.txt").read().split()
    item(rc == 0 and m and m.groups() == ("5", "4", "1") and todo == ["es_madrid_B21_dev_1"],
         "one household byte changed: that run is NOT done (cache MISS seen): %s todo=%s" % (m.group(0) if m else out[-300:], todo))

    # ---- 6. Severe line planted in a scratch copy of an err file must FAIL the check
    errt = io.open(S + "done/es_madrid_B21_dev_1.err", encoding="utf-8").read()
    ok0, w0 = cc.check_err(errt)
    bad_txt = errt + "\n   ** Severe  ** planted line for the seen-failing test\n   **  ~~~   ** more\n"
    ok1, w1 = cc.check_err(bad_txt)
    item(ok0 and not ok1, "check_err: real err file passes (%s), err file with a planted Severe line FAILS (%s)" % (ok0, w1))
    ok2, w2 = cc.check_err(errt.replace("EnergyPlus Completed Successfully", "EnergyPlus Terminated"))
    item(ok0 and not ok2, "check_err: err file without 'Completed Successfully' FAILS (%s)" % w2)

    nf = RES.count(False)
    print("SMOKE SUMMARY pass=%d fail=%d end=%s" % (RES.count(True), nf, cc.now()))
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print("SMOKE CRASH (not a pass)")
        traceback.print_exc()
        print("SMOKE SUMMARY pass=%d fail=%d crashed=1" % (RES.count(True), RES.count(False)))
        sys.exit(1)
