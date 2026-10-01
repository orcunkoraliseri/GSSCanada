# -*- coding: utf-8 -*-
"""5J Step 5 part D, step B (GPU, one array task): predictions of shortlisted config <task> for all validation runs via
s5_predict.predict_runs (the same function s5_predict.py main calls); prints the rows written. Validation only."""
import json, os, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, "/speed-scratch/o_iseri/5J/train")
import s5_predict as sp

T = "/speed-scratch/o_iseri/5J/train/"
task = int(sys.argv[1])
r = json.load(open(T + "winner/shortlist.json"))["shortlist"][task]
out = T + "pred/S%d" % r["idx"]
print("PREDICT task=%d config=S%d (%s w%d %s lam=%g) ckpt=%s out=%s" % (task, r["idx"], r["family"], r["width"], r["depth"], r["lam"], r["ckpt"], out), flush=True)
if os.path.exists(out):
    print("REFUSED: %s already exists" % out)
    sys.exit(4)
t0 = time.time()
info = sp.predict_runs(r["ckpt"], out)
print("PREDICT_DONE config=S%d runs=%d rows_written=%d window_shapes=%s seconds=%.0f" %
      (r["idx"], len(info), sum(i["rows_written"] for i in info), sorted(set(str(i["window_shape"]) for i in info)), time.time() - t0), flush=True)
