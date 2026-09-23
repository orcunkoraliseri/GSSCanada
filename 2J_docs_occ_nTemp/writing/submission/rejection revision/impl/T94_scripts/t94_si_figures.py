"""
T94 -- re-plot Supplementary Figures S1 and S2 with plain reader-facing labels (no task IDs, no
model nicknames, no source-file notes, no embedded figure numbers). Plotting only: every plotted value
is read from the already-accepted saved output of the original figure task; nothing is recomputed.

  Figure S1 <- T94_in/SI/fig08_n200_convergence.csv (T75's own plotted rows, copied from the cluster)
  Figure S2 <- T74_out/figures/fig09_threshold_sensitivity.csv (T74's own plotted rows)

Run locally:  py T94_scripts/t94_si_figures.py   (from impl/)
Writes:       T94_out/figS1_sample_size.png, T94_out/figS2_threshold_sensitivity.png,
              T94_out/t94_si_plotted_values.json
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.dirname(HERE)
OUT = os.path.join(IMPL, "T94_out")
DPI = 600
VALUES = {}


def save(fig, name):
    p = os.path.join(OUT, name + ".png")
    fig.savefig(p, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("saved", p)


# ---- Figure S1: confidence-interval half-width against sample size ----
def fig_s1():
    df = pd.read_csv(os.path.join(IMPL, "T94_in", "SI", "fig08_n200_convergence.csv"))
    assert len(df) == 144, len(df)
    cells = [("SingleD__Montreal_6A", "Single-detached", "#1b7837"),
             ("OtherDwelling__Montreal_6A", "Other dwelling", "#762a83"),
             ("MidRise__Montreal_6A", "Mid-rise", "#2166ac"),
             ("HighRise__Montreal_6A", "High-rise", "#b2182b")]
    metrics = [("elec_facility_kWh", "Annual electricity (kWh)"),
               ("mean_daily_peak_kW", "Mean daily peak demand (kW)"),
               ("mean_peak_hour", "Mean peak hour (h)"),
               ("load_factor", "Load factor (fraction)"),
               ("midday_share", "Midday share, 09:00 to 17:00 (fraction)"),
               ("evening_ramp_kW_mean", "Evening ramp, 14:00 to 17:00 (kW)")]
    fig, axes = plt.subplots(2, 3, figsize=(11, 6.6))
    for ax, (m, title) in zip(axes.flat, metrics):
        for cell, name, color in cells:
            sub = df[(df.cell == cell) & (df.metric == f"{m}_delta_2022to2030")].sort_values("N")
            assert len(sub) == 6, (cell, m, len(sub))
            boot = sub[sub.N < 200]
            assert (boot.ci_method == "bootstrap_subsample_percentile_1000draws").all()
            full = sub[sub.N == 200]
            assert (full.ci_method == "parametric_student_t_full_sample").all()
            ax.plot(boot.N, boot.halfwidth, "-o", color=color, markersize=3.5, linewidth=1.4)
            ax.plot(full.N, full.halfwidth, "*", color=color, markersize=10, markeredgecolor="black",
                    markeredgewidth=0.5)
            VALUES.setdefault("figS1", {})[f"{cell}|{m}"] = dict(zip(sub.N.astype(int).tolist(),
                                                                      sub.halfwidth.tolist()))
        ax.axvline(200, color="grey", linestyle="--", linewidth=0.8)
        ax.set_title(title, fontsize=9)
        ax.set_xticks([10, 50, 100, 150, 200])
        ax.set_xlabel("Sample size (households)", fontsize=8)
        ax.set_ylabel("95% CI half-width", fontsize=8)
        ax.tick_params(labelsize=7.5)
        ax.grid(alpha=0.3)
    handles = [Line2D([], [], color=c, marker="o", markersize=4, label=n) for _, n, c in cells]
    handles.append(Line2D([], [], color="grey", marker="*", linestyle="none", markersize=10,
                          markeredgecolor="black", label="200 households, parametric interval"))
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=8.5, frameon=False,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    save(fig, "figS1_sample_size")


# ---- Figure S2: model-selection stability under perturbed thresholds ----
def fig_s2():
    df = pd.read_csv(os.path.join(IMPL, "T74_out", "figures", "fig09_threshold_sensitivity.csv"))
    assert len(df) == 25, len(df)
    families = [("composite_max", "Composite score"),
                ("at_home_max", "At-home error"),
                ("spouse_abs_max", "Spousal co-presence gap"),
                ("act_js_max", "Activity-distribution distance"),
                ("all", "All four thresholds together")]
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.2))
    af = axes.flatten()
    for ax, (fam, title) in zip(af, families):
        sub = df[df.family == fam].sort_values("pct")
        assert len(sub) == 5, (fam, len(sub))
        ax.plot(sub.pct, sub.n_passing_4of4, color="grey", linewidth=1.2, zorder=1)
        for _, r in sub.iterrows():
            chosen = r.selected_model == "J3"
            ax.scatter(r.pct, r.n_passing_4of4, s=70, zorder=2, edgecolor="black",
                       marker="o" if chosen else "^", color="#2d7a3a" if chosen else "#c0392b")
        VALUES.setdefault("figS2", {})[fam] = {int(p): [int(n), s == "J3"] for p, n, s in
                                              zip(sub.pct, sub.n_passing_4of4, sub.selected_model)}
        ax.set_title(title, fontsize=9)
        ax.set_xticks([-20, -10, 0, 10, 20])
        ax.set_ylim(-0.3, 7.2)
        ax.axvline(0, color="grey", linewidth=0.6, alpha=0.5)
        ax.set_xlabel("Threshold change (%)", fontsize=8)
        ax.set_ylabel("Candidates meeting all four checks", fontsize=8)
        ax.tick_params(labelsize=7.5)
        ax.grid(alpha=0.3)
    af[5].axis("off")
    handles = [Line2D([], [], marker="o", linestyle="none", markersize=9, markerfacecolor="#2d7a3a",
                      markeredgecolor="black", label="Chosen model selected"),
               Line2D([], [], marker="^", linestyle="none", markersize=9, markerfacecolor="#c0392b",
                      markeredgecolor="black", label="Another candidate selected")]
    af[5].legend(handles=handles, loc="center", fontsize=9, frameon=False)
    fig.tight_layout()
    save(fig, "figS2_threshold_sensitivity")


if __name__ == "__main__":
    fig_s1()
    fig_s2()
    with open(os.path.join(OUT, "t94_si_plotted_values.json"), "w") as fh:
        json.dump(VALUES, fh, indent=1)
    print("done")
