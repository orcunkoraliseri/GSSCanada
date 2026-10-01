# -*- coding: utf-8 -*-
"""5J Step 4 Part G (val 4.2 first half): the test reader must refuse now. Speed job only. Opens NO run file."""
import sys, os
sys.path.insert(0, "/speed-scratch/o_iseri/5J/freeze")
import split_loader as sl
print("gates_frozen.md5 exists:", os.path.exists(sl.GATE_FILE), "(must be False before the freeze)")
for n in ("test_new_households", "test_new_buildings", "test_both_new", "b0_test", "unused"):
    try:
        ids = sl.load_split(n)
        print("REFUSAL_TEST %s: NOT REFUSED (%d ids read)  -> FAIL" % (n, len(ids)))
    except PermissionError as e:
        print("REFUSAL_TEST %s: refused -> PASS | %s" % (n, e))
for n in ("development", "validation"):
    print("LOAD_OK %s %d ids" % (n, len(sl.load_split(n))))
