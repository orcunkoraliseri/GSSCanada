"""_gen_v5_plots.py — render v4-style charts on the CALIBRATED J3 outputs and
inject them into step4_validation_report_v5.html via placeholder substitution.
Reuses AugmentationValidator from 04F_validation.py. Run:  py _gen_v5_plots.py
"""
import os, importlib.util
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))          # .../outputs_step4
ROOT = os.path.dirname(HERE)                                # .../2J_docs_occ_nTemp
BASE = os.path.dirname(ROOT)                                # .../GSSCanada-main

# import 04F_validation.py (leading digit -> importlib)
spec = importlib.util.spec_from_file_location("val04f", os.path.join(ROOT, "04F_validation.py"))
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
import matplotlib.pyplot as plt

CAL = os.path.join(BASE, "0_Occupancy", "Outputs_21CEN22GSS", "aug_pipeline",
                   "21CEN22GSS_aug_Full_Schedules_excl.csv")
OBS = os.path.join(ROOT, "outputs_step3", "hetus_30min.csv")
TRAINLOG = os.path.join(HERE, "outputs_step4_J3_PSB", "step4_training_log.csv")
HTML = os.path.join(HERE, "step4_validation_report_v5.html")

ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
NEED = set(ACT + HOM + ["DDAY_STRATA", "CYCLE_YEAR", "IS_SYNTHETIC", "LFTAG", "AGEGRP"])


class CalVal(V.AugmentationValidator):
    def _load_data(self):
        print("  loading observed GSS (hetus_30min)...", flush=True)
        self.obs = pd.read_csv(OBS, usecols=lambda c: c in NEED, low_memory=False)
        self.obs_cop = None
        print("  loading calibrated J3 (Full_Schedules_excl)...", flush=True)
        self.aug = pd.read_csv(CAL, usecols=lambda c: c in NEED, low_memory=False)
        self.syn = self.aug[self.aug["IS_SYNTHETIC"] == 1].copy()
        self.obs_aug = self.aug[self.aug["IS_SYNTHETIC"] == 0].copy()
        self.train_log = pd.read_csv(TRAINLOG) if os.path.exists(TRAINLOG) else None
        print(f"    obs {len(self.obs):,} | syn {len(self.syn):,} | aug {len(self.aug):,}", flush=True)

    def validate_cross_stratum_consistency(self):
        # chart-only (skip the O(n) per-respondent iterrows checks; not needed for the figure)
        cycles = sorted(self.obs["CYCLE_YEAR"].unique()); strata = [1, 2, 3]
        colors = list(V.CYCLE_COLORS.values())
        fig, ax = plt.subplots(figsize=(10, 4)); x = np.arange(len(cycles)); w = 0.25
        for si, s in enumerate(strata):
            obs_wp, syn_wp = [], []
            for cy in cycles:
                o = self.obs[(self.obs.CYCLE_YEAR == cy) & (self.obs.DDAY_STRATA == s)]
                sv = self.syn[(self.syn.CYCLE_YEAR == cy) & (self.syn.DDAY_STRATA == s)]
                obs_wp.append((o[ACT].values == 1).mean() * 100 if len(o) else 0)
                syn_wp.append((sv[ACT].values == 1).mean() * 100 if len(sv) else 0)
            ax.bar(x + si * w - w, obs_wp, w * 0.8, label=f"Obs {V.STRATA_LABELS[s]}",
                   alpha=0.8, color=colors[si])
            ax.bar(x + si * w - w + w * 0.4, syn_wp, w * 0.4, alpha=0.6,
                   color=colors[si], hatch="//")
        ax.set_xticks(x); ax.set_xticklabels(cycles)
        ax.set_title("Section 7 — Paid-Work by Stratum × Cycle (obs vs calibrated)")
        ax.set_ylabel("% slots in paid work"); ax.legend(fontsize=7)
        plt.tight_layout()
        self.charts.setdefault(7, []).append(("Work by Stratum", V.fig_to_b64(fig)))
        return {}


val = CalVal(step3_dir=os.path.join(ROOT, "outputs_step3"), step4_dir=HERE, sample_mode=False)

steps = [("training", val.validate_training_curves),
         ("activity", val.validate_activity_distribution),
         ("at_home", val.validate_at_home_rate),
         ("temporal", val.validate_temporal_structure),
         ("demographic", val.validate_demographic_conditioning),
         ("cross_stratum", val.validate_cross_stratum_consistency)]
for name, fn in steps:
    try:
        print(f"  chart: {name}...", flush=True); fn()
    except Exception as e:
        print(f"    !! {name} failed: {e!r}", flush=True)

charts = {}
for sec, lst in val.charts.items():
    for title, b64 in lst:
        charts[title] = b64
print("  generated charts:", list(charts.keys()), flush=True)

PLACE = {
    "{{CHART_TRAINING}}": "Training Curves",
    "{{CHART_ACTIVITY}}": "Activity Distribution by Stratum",
    "{{CHART_JSHEATMAP}}": "JS Heatmap",
    "{{CHART_ATHOME}}": "AT_HOME Daily Rhythm",
    "{{CHART_HEATMAP}}": "Activity Heatmap",
    "{{CHART_LFTAG}}": "Work Proportion by LFTAG",
    "{{CHART_STRATUM}}": "Work by Stratum",
}
html = open(HTML, encoding="utf-8").read()
missing = []
for token, title in PLACE.items():
    if title in charts:
        img = f'<img src="data:image/png;base64,{charts[title]}" alt="{title}"/>'
    else:
        img = f'<div class="note">Figure unavailable: {title}</div>'; missing.append(title)
    html = html.replace(token, img)
open(HTML, "w", encoding="utf-8").write(html)
print(f"\nWROTE {os.path.basename(HTML)}: {os.path.getsize(HTML)/1024:.0f} KB | "
      f"missing: {missing or 'none'} | remaining placeholders: {html.count('{{CHART_')}", flush=True)
