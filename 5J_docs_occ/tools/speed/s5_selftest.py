# -*- coding: utf-8 -*-
"""5J Step 5 part A seen-failing job: (1) open_run refuses a locked run id; (2) check_features passes the real input list and
fails the list plus 'heating_kwh_lag24'. Speed job only. No list of locked runs is ever loaded: the locked id is taken from the
run table as a run that is NOT in the four allowed lists (and whose pool names a test pool when one exists)."""
import sys, os, io
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s5_common as c

fails = 0
allowed = c.allowed_ids()
print("allowed ids", len(allowed), {k: len(v) for k, v in c.lists().items()})
R = c.runs()
locked = sorted(r for r in R if r not in allowed)
pref = [r for r in locked if str(R[r]["pool"]).lower().startswith("test")]
pick = (pref or locked)[0]
print("locked pick:", pick, "pool=%s building_split=%s (from the run table; no locked list was loaded)" % (R[pick]["pool"], R[pick]["building_split"]))
log = []
try:
    c.open_run(pick, "seenfail", log)
    print("SEENFAIL open_run: NOT REFUSED (planted fault not caught)")
    fails += 1
except PermissionError as e:
    print("SEENFAIL open_run: REFUSED ->", e)
ok_log = (len(log) == 0)
print("CHECK open_run_refusal_logged_nothing %s log_lines=%d" % ("PASS" if ok_log else "FAIL", len(log)))
fails += 0 if ok_log else 1
good = sorted(allowed)[0]
p = c.open_run(good, "seenfail_control", log)
print("CHECK open_run_allowed_id %s %s log_lines=%d path=%s exists=%s" % ("PASS" if len(log) == 1 else "FAIL", good, len(log), p, os.path.exists(p)))
fails += 0 if len(log) == 1 else 1
# NOTE: this one allowed-id open is NOT flushed to any open log (selftest only)

names = c.all_input_names()
ok, bad = c.check_features(names)
print("CHECK check_features real_list n=%d %s bad=%s" % (len(names), "PASS" if ok else "FAIL", bad))
fails += 0 if ok else 1
ok2, bad2 = c.check_features(names + ["heating_kwh_lag24"])
print("CHECK check_features real_list+heating_kwh_lag24 %s bad=%s" % ("FAIL" if not ok2 else "PASS", bad2))
print("SEENFAIL check_features planted name caught: %s" % ("YES" if (not ok2 and bad2 == ["heating_kwh_lag24"]) else "NO"))
fails += 0 if (not ok2 and bad2 == ["heating_kwh_lag24"]) else 1
print("first 10 inputs:", names[:10], "last 3:", names[-3:])
print("SELFTEST", "PASS" if fails == 0 else "FAIL", "fails=%d" % fails)
sys.exit(1 if fails else 0)
