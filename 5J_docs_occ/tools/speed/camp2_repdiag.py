import gzip, io, sys
import numpy as np, pandas as pd
R = "/speed-scratch/o_iseri/5J/campaign/extracted/es_madrid_2010/"
a = pd.read_csv(R + "es_madrid_B01_dev_1.csv.gz", comment="#")
b = pd.read_csv(R + "es_madrid_B01_dev_1_rep1.csv.gz", comment="#")
print("shape", a.shape, b.shape, "same columns", list(a.columns) == list(b.columns))
for c in a.columns:
    d = np.abs(a[c].to_numpy(dtype=float) - b[c].to_numpy(dtype=float))
    n = int((d > 0).sum())
    if n:
        i = int(np.argmax(d))
        print("DIFF col=%s rows_differing=%d max_abs=%.6g at row %d a=%.10g b=%.10g" % (c, n, d.max(), i, a[c][i], b[c][i]))
print("DIAG_DONE")
