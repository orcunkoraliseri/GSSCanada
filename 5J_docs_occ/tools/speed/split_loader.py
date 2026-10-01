# -*- coding: utf-8 -*-
"""5J sealed split lists. load_split(name) returns the sorted run_id list of /speed-scratch/o_iseri/5J/splits/<name>.txt.
Test lists (test_*, b0_test, unused: they hold test households or test buildings) are REFUSED unless the file
/speed-scratch/o_iseri/5J/gates_frozen.md5 exists (written by Step 4 when the gates are frozen; Step 3 never creates it).
The list file is also checked against splits.md5 (refuses a list that was changed after sealing).
"""
import hashlib, io, os, re

SPLIT_DIR = "/speed-scratch/o_iseri/5J/splits/"
GATE_FILE = "/speed-scratch/o_iseri/5J/gates_frozen.md5"
GATED = ("b0_test", "unused")
NAMES = ["development", "validation", "test_new_households", "test_new_buildings", "test_both_new", "unused",
         "b0_dev", "b0_val", "b0_test", "replicates", "loco_es", "loco_it"]


def _md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def is_gated(name):
    return name.startswith("test_") or name in GATED


def load_split(name):
    if not re.match(r"^[a-z0-9_]+$", name) or name not in NAMES:
        raise ValueError("unknown split list %r (known: %s)" % (name, NAMES))
    if is_gated(name) and not os.path.exists(GATE_FILE):
        raise PermissionError("REFUSED: split %r is a test list and %s does not exist (Step 4 freezes the gates first)" % (name, GATE_FILE))
    p = SPLIT_DIR + name + ".txt"
    sums = {}
    for ln in io.open(SPLIT_DIR + "splits.md5", encoding="utf-8"):
        if ln.strip():
            h, f = ln.split()
            sums[f.lstrip("*")] = h
    if sums.get(name + ".txt") != _md5(p):
        raise RuntimeError("split file %s does not match splits.md5 (changed after sealing?)" % p)
    return [ln.strip() for ln in io.open(p, encoding="utf-8") if ln.strip()]
