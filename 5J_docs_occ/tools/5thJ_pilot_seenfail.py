#!/usr/bin/env python3
"""Seen-failing tests for 5thJ_pilot_check.py (val doc Section 6). RUNS ON SPEED via sbatch only.
Builds a scratch root under --scratch (symlinks to the real files, a real mutated COPY of the one file changed),
runs the checker on it and prints the gate lines it produced plus the exit code.
Cases:  3.1 (P001's hourly series copied onto P002, same building)
        2.2 (a '** Severe  **' line planted in a copy of P001's eplusout.err)
        2.4 (P001's facility_elec_J column x 1.01 in a copy of its extracted file)
        none (control: nothing changed, must give the same lines as the real run)
"""
import argparse, os, shutil, subprocess, sys


def build(root, scratch, case):
    if os.path.exists(scratch):
        shutil.rmtree(scratch)
    os.makedirs(os.path.join(scratch, "runs"))
    os.makedirs(os.path.join(scratch, "extracted"))
    for n in ("run_manifest.csv", "preflight.txt", "inputs", "logs"):
        os.symlink(os.path.join(root, n), os.path.join(scratch, n))
    ids = sorted(d for d in os.listdir(os.path.join(root, "runs")) if d.startswith("P") and len(d) == 4)
    for rid in ids:
        rd = os.path.join(scratch, "runs", rid)
        os.makedirs(os.path.join(rd, "eplus_out"))
        for f in os.listdir(os.path.join(root, "runs", rid)):
            if f != "eplus_out":
                os.symlink(os.path.join(root, "runs", rid, f), os.path.join(rd, f))
        for f in ("eplusout.err", "eplustbl.csv"):
            os.symlink(os.path.join(root, "runs", rid, "eplus_out", f), os.path.join(rd, "eplus_out", f))
        os.symlink(os.path.join(root, "extracted", rid + ".csv"), os.path.join(scratch, "extracted", rid + ".csv"))
    def unlink(p):
        os.remove(p)
    if case == "3.1":
        dst = os.path.join(scratch, "extracted", "P002.csv")
        unlink(dst)
        shutil.copy(os.path.join(root, "extracted", "P001.csv"), dst)
        return "P001 and P002 are on the same building (es_B07) with different households; P002 extracted file replaced by a copy of P001's"
    if case == "2.2":
        dst = os.path.join(scratch, "runs", "P001", "eplus_out", "eplusout.err")
        unlink(dst)
        shutil.copy(os.path.join(root, "runs", "P001", "eplus_out", "eplusout.err"), dst)
        with open(dst, "a") as f:
            f.write("   ** Severe  ** planted for the seen-failing test\n")
        return "one '** Severe  **' line appended to a copy of P001 eplusout.err"
    if case == "2.4":
        dst = os.path.join(scratch, "extracted", "P001.csv")
        unlink(dst)
        lines = open(os.path.join(root, "extracted", "P001.csv")).read().splitlines()
        out = [lines[0]]
        for ln in lines[1:]:
            c = ln.split(",")
            c[4] = repr(float(c[4]) * 1.01)
            out.append(",".join(c))
        open(dst, "w").write("\n".join(out) + "\n")
        return "facility_elec_J column of P001 extracted copy x 1.01"
    return "control, nothing changed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--checker", required=True)
    ap.add_argument("--buildings", required=True)
    ap.add_argument("--build-log", required=True)
    ap.add_argument("--today", required=True)
    a = ap.parse_args()
    for case in ("none", "3.1", "2.2", "2.4"):
        sc = os.path.join(a.scratch, "case_" + case.replace(".", "_"))
        what = build(a.root, sc, case)
        print("=== CASE %s: %s" % (case, what), flush=True)
        p = subprocess.run([sys.executable, a.checker, "--root", sc, "--buildings", a.buildings,
                            "--build-log", a.build_log, "--today", a.today],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for ln in p.stdout.splitlines():
            g = ln.split()[1] if len(ln.split()) > 1 else ""
            if ln.startswith(("FAIL", "NOT_EVALUABLE")) or ln.startswith("SUMMARY") or ln.startswith("FAIL-severity") \
               or (case in ("3.1", "2.2", "2.4") and g in (case, case + "b")):
                print(ln[:400])
        print("CHECKER EXIT=%d" % p.returncode, flush=True)


if __name__ == "__main__":
    main()
