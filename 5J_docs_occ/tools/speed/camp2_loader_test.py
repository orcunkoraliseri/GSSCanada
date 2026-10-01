import os, sys
import split_loader as sl
assert not os.path.exists(sl.GATE_FILE), "gates_frozen.md5 exists: this test expects it absent"
for n in ("test_new_households", "test_new_buildings", "test_both_new", "b0_test", "unused"):
    try:
        sl.load_split(n)
        print("LOADER_TEST %s NOT REFUSED (FAIL)" % n)
    except PermissionError as e:
        print("LOADER_TEST %s refused: %s" % (n, e))
d = sl.load_split("development")
print("LOADER_TEST development allowed, %d run ids, first %s" % (len(d), d[0]))
for n in ("validation", "b0_dev", "replicates", "loco_es"):
    print("LOADER_TEST %s allowed, %d run ids" % (n, len(sl.load_split(n))))
# allow path with a SCRATCH gate file (the real gates_frozen.md5 is never created here)
scratch = "/speed-scratch/o_iseri/5J/campaign/integrity/scratch_gate_test.md5"
open(scratch, "w").write("scratch\n")
sl.GATE_FILE = scratch
print("LOADER_TEST with a scratch gate file: test_both_new ->", len(sl.load_split("test_both_new")), "run ids")
os.remove(scratch)
try:
    sl.load_split("../etc/passwd")
except ValueError as e:
    print("LOADER_TEST bad name refused:", e)
