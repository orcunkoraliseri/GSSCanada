# -*- coding: utf-8 -*-
"""5J Step 5 part E, step D (GPU, one array task): validation predictions of a control / seed checkpoint (ckpt/<name>) into pred/<name>
through s5_predict.predict_runs. The checkpoint's own config decides the flags (blind). Refuses an existing output folder."""
import os, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, "/speed-scratch/o_iseri/5J/train")
import s5_predict as sp

T = "/speed-scratch/o_iseri/5J/train/"
NAMES = ["S_seed2", "S_seed3", "C_seed1", "C_seed2", "C_seed3"]
name = NAMES[int(sys.argv[1])]
out = T + "pred/" + name
print("PREDICT task=%s name=%s ckpt=%s out=%s" % (sys.argv[1], name, T + "ckpt/" + name, out), flush=True)
if os.path.exists(out):
    print("REFUSED: %s already exists" % out)
    sys.exit(4)
t0 = time.time()
info = sp.predict_runs(T + "ckpt/" + name, out)
print("PREDICT_DONE name=%s runs=%d rows_written=%d window_shapes=%s seconds=%.0f" %
      (name, len(info), sum(i["rows_written"] for i in info), sorted(set(str(i["window_shape"]) for i in info)), time.time() - t0), flush=True)
