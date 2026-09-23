"""P10R: weekday retail at_retail_fraction by clock hour (mean of the 2 half-hour slots), old vs new (M.2 context)."""
from pathlib import Path
import pandas as pd
J3 = Path(__file__).resolve().parents[4]
S = J3 / "Leg3_4-split/Step7_docs"
for lbl, p in (("OLD 2022", S / "outputs_step7/retail_presence_multiplier_2022.csv"),
               ("NEW 2022", S / "outputs_step7_P10R/retail_presence_multiplier_2022.csv"),
               ("OLD 2030c inj", S / "outputs_step7/retail_presence_multiplier_2030_central_BAK_2026-08-02.csv"),
               ("NEW 2030c", S / "outputs_step7_P10R/retail_presence_multiplier_2030_central.csv")):
    d = pd.read_csv(p); d = d[d.Day_Type == "Weekday"]
    for pr, g in d.groupby("PR"):
        h = g.groupby("Hour").at_retail_fraction.mean()
        print(f"{lbl:14s} {pr} argmax={h.idxmax():2d}  h10..18: " + " ".join(f"{h[i]:.4f}" for i in range(10, 19)))
