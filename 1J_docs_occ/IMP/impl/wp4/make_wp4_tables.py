"""WP4 (1J revision): paper tables and Figure A1 from the hindcast outputs copied from Speed.

Inputs (scp from /speed-scratch/o_iseri/1J_rerun/wp4/out/ to IMP/impl/wp4/out/):
  hindcast_scores.csv (method, K, decay, latent, seed, variable, metric, value), hindcast_summary.csv,
  pass_rule.txt, sens2025.csv.
Outputs: out/table_hindcast.md (Table 9), out/table_sensitivity.md (Table A1),
  1J_docs_occ/figures/FigA1_hindcast_R1.png.

Gate W4.P: the CBVM-vs-B0 count is recomputed here from the RAW per-seed scores (not from the summary) and must
equal the count printed in pass_rule.txt; a mismatch stops the script.
Usage: py make_wp4_tables.py [out_dir]   (out_dir defaults to ./out; a test directory can be passed)
"""
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
FIG = os.path.join(HERE, "..", "..", "..", "figures", "FigA1_hindcast_R1.png") if len(sys.argv) == 1 \
    else os.path.join(OUT, "FigA1_hindcast_TEST.png")

LABEL = {"AGEGRP": "Age group", "SEX": "Sex", "MARSTH": "Marital status", "HHSIZE": "Household size",
         "EFSIZE": "Economic family size", "CFSIZE": "Census family size", "CFSTAT": "Census family status",
         "CF_RP": "Census family role", "PR": "Province", "CMA": "Metropolitan area", "KOL": "Official languages",
         "CITIZEN": "Citizenship", "GENSTAT": "Generation status", "ATTSCH": "School attendance",
         "CIP": "Field of study", "LFTAG": "Labour force status", "COW": "Class of worker", "NOCS": "Occupation",
         "HRSWRK": "Hours worked", "POWST": "Place of work status", "MODE": "Commuting mode",
         "EMPIN": "Employment income", "TOTINC": "Total income", "INCTAX": "Income after tax"}
ORDER = list(LABEL)

sc = pd.read_csv(os.path.join(OUT, "hindcast_scores.csv"))
rule = open(os.path.join(OUT, "pass_rule.txt"), encoding="utf-8").read()
m = re.search(r"WP4 PASS RULE: CBVM beats B0 on (\d+) of (\d+) -> (MET|NOT MET)", rule)
assert m, "pass_rule.txt has no PASS RULE line (aggregate incomplete?)"
k_file, n_file, verdict_file = int(m.group(1)), int(m.group(2)), m.group(3)


def is_(col, val):
    return pd.to_numeric(sc[col], errors="coerce").sub(val).abs() < 1e-9


cb = sc[(sc.method == "CBVM") & is_("K", 8) & is_("decay", 0.95) & is_("latent", 128)]
per = cb.groupby("variable")["value"].agg(["mean", "min", "max", "count"])
assert (per["count"] == 5).all() and len(per) == 24, f"CBVM reference needs 5 seeds x 24 variables: {per['count'].to_dict()}"
b0 = sc[sc.method == "B0"].set_index("variable")["value"]
b1 = sc[sc.method == "B1"].set_index("variable")["value"]
b2 = sc[(sc.method == "B2") & is_("K", 1)].groupby("variable")["value"].mean()
metric = sc[sc.method == "B0"].set_index("variable")["metric"]
assert len(b0) == len(b1) == len(b2) == 24, (len(b0), len(b1), len(b2))

wins = [v for v in per.index if per.loc[v, "mean"] < b0[v]]
k, n = len(wins), len(per)
verdict = "MET" if 2 * k > n else "NOT MET"
print(f"W4.P recomputed from raw scores: CBVM beats B0 on {k} of {n} -> {verdict}; "
      f"pass_rule.txt: {k_file} of {n_file} -> {verdict_file}")
assert (k, n, verdict) == (k_file, n_file, verdict_file), "W4.P FAIL: recomputed count differs from pass_rule.txt"
print("W4.P PASS")
for name, o in [("B1", b1), ("B2", b2)]:
    print(f"(info) CBVM beats {name} on {sum(per.loc[v, 'mean'] < o[v] for v in per.index)} of {n}")
print(f"(info) mean over variables: B0 {b0.mean():.4f}, B1 {b1.mean():.4f}, B2 {b2.mean():.4f}, CBVM {per['mean'].mean():.4f}")

# Table 9
rows = ["| Variable | Metric | B0 carry-forward | B1 linear trend | B2 mean drift | CBVM (K = 8) mean [min–max, 5 seeds] | Closer to 2021: CBVM or B0 |",
        "|:--|:--|--:|--:|--:|--:|:--|"]
for v in ORDER:
    r = per.loc[v]
    rows.append(f"| {LABEL[v]} | {metric[v]} | {b0[v]:.3f} | {b1[v]:.3f} | {b2[v]:.3f} | "
                f"{r['mean']:.3f} [{r['min']:.3f}–{r['max']:.3f}] | {'CBVM' if v in wins else 'B0'} |")
rows.append(f"| Mean over the 24 variables | | {b0.mean():.3f} | {b1.mean():.3f} | {b2.mean():.3f} | "
            f"{per['mean'].mean():.3f} | CBVM closer on {k} of {n} |")
open(os.path.join(OUT, "table_hindcast.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")

# Table A1: hindcast sensitivity (mean over variables; K/decay over 5 seeds at latent 128; latent at seed 1)
cbv = sc[sc.method == "CBVM"].copy()
for c in ["K", "decay", "latent", "seed"]:
    cbv[c] = pd.to_numeric(cbv[c])
b0v = cbv["variable"].map(b0)
cbv["beats"] = cbv["value"] < b0v
srows = ["| Setting | Mean distance over the 24 variables | Variables closer than B0 (of 24) |", "|:--|--:|--:|"]
for (K, d), g in cbv[cbv.latent == 128].groupby(["K", "decay"]):
    pv = g.groupby("variable")["value"].mean()
    srows.append(f"| K = {K:.0f}, decay {d:.2f}, latent 128 (5 seeds) | {pv.mean():.4f} | "
                 f"{sum(pv[v] < b0[v] for v in pv.index)} |")
for L in [64, 128, 256]:
    g = cbv[(cbv.latent == L) & (cbv.seed == 1) & ((cbv.K - 8).abs() < 1e-9) & ((cbv.decay - 0.95).abs() < 1e-9)]
    assert len(g) == 24, f"latent {L} seed 1 rows: {len(g)}"
    srows.append(f"| K = 8, decay 0.95, latent {L} (seed 1) | {g['value'].mean():.4f} | {int(g['beats'].sum())} |")
sens_p = os.path.join(OUT, "sens2025.csv")
if os.path.exists(sens_p):
    s25 = pd.read_csv(sens_p)
    ctrl = s25[s25.variant.str.startswith("control")]["value"].max()
    print(f"sens2025 control (repeat of the reference) max distance = {ctrl:.6f} (expect 0)")
    assert ctrl < 1e-9, "sens2025 control FAIL: the reference does not reproduce"
    arows = ["| 2025 cohort variant | Mean distance from the reference cohort | Largest single variable |", "|:--|--:|:--|"]
    for var, g in s25[~s25.variant.str.startswith("control")].groupby("variant", sort=False):
        r0 = g.iloc[0]
        name = (f"K = {r0.K:.0f}, decay {r0.decay:.2f}" if var.startswith("K") else f"seed {r0.seed:.0f} (K = 8, decay 0.95)")
        arows.append(f"| {name} | {g['value'].mean():.4f} | {g['value'].max():.4f} ({LABEL[g.loc[g['value'].idxmax(), 'variable']]}) |")
    open(os.path.join(OUT, "table_sens2025.md"), "w", encoding="utf-8").write("\n".join(arows) + "\n")
open(os.path.join(OUT, "table_sensitivity.md"), "w", encoding="utf-8").write("\n".join(srows) + "\n")

# Figure A1: distance per variable and method
fig, ax = plt.subplots(figsize=(7.5, 8.5))
y = np.arange(len(ORDER))[::-1]
for off, (name, ser, mk, col) in zip([-0.27, -0.09, 0.09],
                                     [("B0 carry-forward", b0, "o", "#555555"), ("B1 linear trend", b1, "s", "#1f77b4"),
                                      ("B2 mean drift", b2, "^", "#2ca02c")]):
    ax.scatter([ser[v] for v in ORDER], y + off, marker=mk, s=22, color=col, label=name, zorder=3)
cm = np.array([per.loc[v, "mean"] for v in ORDER])
lo = cm - np.array([per.loc[v, "min"] for v in ORDER])
hi = np.array([per.loc[v, "max"] for v in ORDER]) - cm
ax.errorbar(cm, y + 0.27, xerr=[lo, hi], fmt="D", ms=4.5, color="#d62728", capsize=2, label="CBVM, K = 8 (5 seeds, min–max)", zorder=4)
ax.set_yticks(y)
ax.set_yticklabels([f"{LABEL[v]} ({metric[v]})" for v in ORDER], fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("Distance to the held-out 2021 Census (TVD or scaled W1, log scale)")
ax.grid(axis="x", alpha=0.3, which="both")
ax.set_ylim(-0.6, len(ORDER) - 0.4)
ax.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
fig.tight_layout()
fig.savefig(FIG, dpi=300)
print("written", os.path.join(OUT, "table_hindcast.md"), os.path.join(OUT, "table_sensitivity.md"), FIG)
