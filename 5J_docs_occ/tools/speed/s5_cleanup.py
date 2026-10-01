# -*- coding: utf-8 -*-
"""5J Step 5 part D, step F (CPU): delete train/pred/S<cfg>/ of the 5 non-winning shortlisted configs only (R7.6). Score files stay."""
import json, os, shutil, sys
T = "/speed-scratch/o_iseri/5J/train/"
W = json.load(open(T + "winner/winner.json"))
sl = json.load(open(T + "winner/shortlist.json"))["shortlist"]
win = W["config_index"]
n_del = 0
for r in sl:
    d = T + "pred/S%d" % r["idx"]
    if r["idx"] == win:
        print("KEEP winner S%d: %s (exists=%s)" % (win, d, os.path.isdir(d)))
        continue
    assert d == T + "pred/S%d" % int(r["idx"]) and r["idx"] != win
    if not os.path.isdir(d):
        print("ABSENT %s" % d)
        continue
    nf = sum(len(fs) for _, _, fs in os.walk(d))
    shutil.rmtree(d)
    n_del += 1
    print("DELETED %s (%d files)" % (d, nf))
print("score files kept: %s" % sorted(f for f in os.listdir(T + "score") if f.startswith("score_S")))
print("CLEANUP_DONE dirs_deleted=%d (expected 5)" % n_del)
sys.exit(0 if n_del == 5 else 1)
