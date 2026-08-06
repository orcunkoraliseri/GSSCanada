#!/usr/bin/env python3
"""P9 -- R5 must be SEEN failing. A gate nobody has watched fail is not evidence.

Three mutations of increasing size are pushed into the SYNTHETIC retail rows in memory (no file on
disk is touched), and R5's verdict is read back each time. The gate has to move PASS/WARN -> FAIL as
the corruption grows, and the shipped data has to come back WARN when nothing is corrupted.

F0 is the control: it runs the real data through the same harness. If F0 does not reproduce
1.615 pp, the harness is not measuring what the validator measures and nothing below it means
anything.
"""
import importlib.util as ilu
import io
import re
import sys
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S5 = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split"
          r"\Step5_docs")
VAL = S5 / "3rdJ_05_censusLinkage_4split_val.py"

spec = ilu.spec_from_file_location("_v", VAL)
mod = ilu.module_from_spec(spec)
spec.loader.exec_module(mod)
V = mod.CensusLinkageValidator4CH

print("=" * 88)
print("R5 falsifier -- the gate must be seen failing")
print("=" * 88)

v = V(aug_dir=str(mod.OUT_DIR), census_path=str(mod.CENSUS_FILE), outputs_dir=str(mod.OUT_DIR),
      file_suffix="", is_smoke=False, report_name_suffix="_falsify")
sched0 = v.sched.copy()
ret_p = [c for c in V.RET_COLS if c in sched0.columns]
syn = (sched0["IS_SYNTHETIC"] == 1)
print("\nretail slots=%d, synthetic rows=%d, observed rows=%d\n"
      % (len(ret_p), int(syn.sum()), int((~syn).sum())))


def run(label, mutate, expect):
    v.sched = sched0.copy()
    if mutate:
        mutate(v.sched)
    v.results = {"pass": [], "fail": [], "warn": [], "info": []}
    v.summary_rows = []
    buf, sys.stdout = sys.stdout, io.StringIO()
    try:
        v.validate_at_retail_consistency()
    finally:
        cap, sys.stdout = sys.stdout.getvalue(), buf
    line = [l for l in cap.split("\n") if " R5 |" in l]
    if not line:
        print("  %-28s NO R5 LINE EMITTED -- harness broken" % label)
        return None
    m = re.search(r"within-day-type\): ([\d.]+)pp", line[0])
    lvl = ("FAIL" if "[FAIL]" in line[0] else "WARN" if "[WARN]" in line[0] else "PASS")
    val = float(m.group(1)) if m else float("nan")
    ok = (lvl == expect)
    print("  %-28s R5 = %7.3f pp -> %-4s   expected %-4s   %s"
          % (label, val, lvl, expect, "OK" if ok else "*** MISMATCH ***"))
    return ok, val, lvl


results = []
results.append(run("F0 control (untouched)", None, "WARN"))


def bump(frac, slots):
    def _m(df):
        idx = df.index[df["IS_SYNTHETIC"] == 1]
        cols = [ret_p[i] for i in slots]
        for c in cols:
            df.loc[idx, c] = np.clip(df.loc[idx, c].values + frac, 0, 1)
    return _m


results.append(run("F1 +2 pp on 4 slots", bump(0.02, range(16, 20)), "WARN"))
results.append(run("F2 +5 pp on 4 slots", bump(0.05, range(16, 20)), "FAIL"))
results.append(run("F3 +20 pp on 8 slots", bump(0.20, range(14, 22)), "FAIL"))

print("\n" + "-" * 88)
good = [r for r in results if r]
n_ok = sum(1 for r in good if r[0])
print("%d/%d as predicted" % (n_ok, len(good)))
f0 = good[0] if good else None
if f0 and abs(f0[1] - 1.615) > 0.001:
    print("\U0001F534 F0 did NOT reproduce the shipped 1.615 pp -- everything above is suspect")
elif n_ok == len(good):
    print("FALSIFIER HOLDS -- R5 reports FAIL when retail generation is corrupted, and WARN when "
          "it is not")
else:
    print("\U0001F534 FALSIFIER BROKEN -- R5 did not respond as a gate should")
