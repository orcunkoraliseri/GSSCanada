"""Peak cooling demand (District Cooling, Demand End Use Components Summary) per NU and year: mean over 30 draws
with 95 % t-interval, deviation from Default, and the time of peak. Source: ../wp15/out/peaks.csv."""
import os
import numpy as np
import pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
p = pd.read_csv(os.path.join(HERE, "..", "wp15", "out", "peaks.csv"))
LABEL = {"NUS_RC1": "RC-R", "NUS_RC2": "RC-D", "NUS_RC3": "RC-T", "NUS_RC4": "RC-MR2", "NUS_RC5": "RC-MR3", "NUS_RC6": "RC-HR2"}
c = p[p.fuel == "District Cooling"].copy()
c["hour"] = c.peak_time.str.slice(-5, -3).astype(int) + c.peak_time.str.slice(-2).astype(int) / 60
c["day"] = c.peak_time.str.slice(0, 6)
d = c[c.year == "Default"].drop_duplicates("neighbourhood").set_index("neighbourhood")
rows = []
for (nb, yr), g in c[(c.year != "Default") & (c.draw.between(1, 30))].groupby(["neighbourhood", "year"]):
    v = g.peak_w_m2.to_numpy(); n = len(v); m = v.mean(); h = stats.t.ppf(.975, n - 1) * v.std(ddof=1) / np.sqrt(n)
    D = d.loc[nb, "peak_w_m2"]
    rows.append(dict(nu=LABEL[nb], year=yr, n=n, peak_mean=m, half=h, default=D, dev_pct=100 * (m - D) / D,
                     dev_lo=100 * (m - h - D) / D, dev_hi=100 * (m + h - D) / D,
                     default_time=d.loc[nb, "peak_time"], modal_time=g.peak_time.mode().iloc[0],
                     share_modal=(g.peak_time == g.peak_time.mode().iloc[0]).mean(),
                     hour_mean=g.hour.mean(), days=";".join(sorted(g.day.unique()))))
t = pd.DataFrame(rows)
t.to_csv(os.path.join(HERE, "out", "peak_cooling.csv"), index=False)
pd.set_option("display.width", 250)
print(t[["nu", "year", "peak_mean", "half", "default", "dev_pct", "dev_lo", "dev_hi", "default_time", "modal_time", "share_modal", "hour_mean", "days"]].round(2).to_string())
print("dev range houses", t[t.nu.isin(["RC-R","RC-D","RC-T"])].dev_pct.agg(["min","max"]).round(1).tolist(),
      "apartments", t[~t.nu.isin(["RC-R","RC-D","RC-T"])].dev_pct.agg(["min","max"]).round(1).tolist())
