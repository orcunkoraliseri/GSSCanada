# Gate B for R/it_60: 60 presence files; hid set AND order of enduse_by_dwelling_it.csv = hids_it60.csv; log lines; mean kWh.
import csv, glob, io, os, sys
R = "/speed-scratch/o_iseri/5J/households"
LOG = sys.argv[1]
def hids_of(path, col="hid"):
    return [r[col] for r in csv.DictReader(io.open(path, encoding="utf-8"))]
def check(label, want, got):
    ok = want == got
    print("GATE B_%s %s n_want=%d n_got=%d same_set=%s same_order=%s" % (label, "PASS" if ok else "FAIL", len(want), len(got), set(want) == set(got), ok))
    return ok
want = hids_of(R + "/repo/5J_docs_occ/Step2_docs/outputs_step2/hids_it60.csv")
got = hids_of(R + "/it_60/enduse_by_dwelling_it.csv")
ok1 = check("hid_order", want, got)
sw = list(got); sw[0], sw[1] = sw[1], sw[0]
print("SEENFAIL B hid order with first two hids swapped:")
bad_fired = not check("SEENFAIL_swapped", want, sw)
print("SEENFAIL B gate %s (must FAIL)" % ("FAILED as required" if bad_fired else "DID NOT FIRE"))
n = len(glob.glob(R + "/it_60/presence/presence_HH_it_*.csv"))
print("GATE B_presence_files %s n=%d" % ("PASS" if n == 60 else "FAIL", n))
txt = io.open(LOG, encoding="utf-8").read()
for key in ("GUARD corpus OK", "HIDS OK", "PATCH act2 OK"):
    c = txt.count(key)
    print("GATE B_log_%s %s count=%d" % (key.replace(" ", "_"), "PASS" if c >= 1 else "FAIL", c))
for ln in txt.splitlines():
    if "electricity kWh/dwelling.y" in ln or ln.startswith("dwellings / people") or "Traceback" in ln:
        print("LOG", ln)
sys.exit(0 if (ok1 and bad_fired and n == 60) else 1)
