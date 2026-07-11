"""_gen_v7_plots.py -- Task D (Step-4 Improvements, Improvement 4): re-renders
the seven v5-inherited section charts on the FINAL Task-A+B corrected
population (21CEN22GSS_aug_Full_Schedules_excl.csv, rebuild 2026-07-09 20:47)
and injects them into step4_validation_report_v7.html.

Unlike _gen_v5_plots.py (token substitution, {{CHART_*}} placeholders exist)
or _gen_v6_plots.py (also token-based, additive figures), v7's seven charts
already carry rendered <img alt="..."/> tags copied verbatim from v6 -- the
{{CHART_*}} tokens were consumed when v5 was built. Replacement here is
alt-keyed: each of the seven exact inherited titles below is located via its
alt="..." attribute and its whole <img .../> tag is swapped. This protects the
three Task-C figures (different alts) automatically. Idempotent via a
data-regen="v7-20260709" token stamped onto each newly written tag.

Reuses AugmentationValidator from 04F_validation.py via the same CalVal
pattern as _gen_v5_plots.py (usecols-guarded load, lightweight
validate_cross_stratum_consistency override -- the base class's version does
an O(n) iterrows() over the whole aug population, too slow to rerun here).

Run:  py _gen_v7_plots.py
"""
import os, importlib.util
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))          # .../outputs_step4
ROOT = os.path.dirname(HERE)                                # .../2J_docs_occ_nTemp
BASE = os.path.dirname(ROOT)                                # .../GSSCanada-main

spec = importlib.util.spec_from_file_location("val04f", os.path.join(ROOT, "04F_validation.py"))
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
import matplotlib.pyplot as plt

CAL = os.path.join(BASE, "0_Occupancy", "Outputs_21CEN22GSS", "aug_pipeline",
                   "21CEN22GSS_aug_Full_Schedules_excl.csv")
OBS = os.path.join(ROOT, "outputs_step3", "hetus_30min.csv")
TRAINLOG = os.path.join(HERE, "outputs_step4_J3_PSB", "step4_training_log.csv")
HTML = os.path.join(HERE, "step4_validation_report_v7.html")
REGEN_TOKEN = "v7-20260709"

ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
NEED = set(ACT + HOM + ["DDAY_STRATA", "CYCLE_YEAR", "IS_SYNTHETIC", "LFTAG", "AGEGRP"])

ALT_TITLES = [
    "Training Curves",
    "Activity Distribution by Stratum",
    "JS Heatmap",
    "AT_HOME Daily Rhythm",
    "Activity Heatmap",
    "Work Proportion by LFTAG",
    "Work by Stratum",
]


class CalVal(V.AugmentationValidator):
    def _load_data(self):
        print("  loading observed GSS (hetus_30min)...", flush=True)
        self.obs = pd.read_csv(OBS, usecols=lambda c: c in NEED, low_memory=False)
        self.obs_cop = None
        print("  loading FINAL corrected population (Full_Schedules_excl, rebuild 20:47)...", flush=True)
        self.aug = pd.read_csv(CAL, usecols=lambda c: c in NEED, low_memory=False)
        self.syn = self.aug[self.aug["IS_SYNTHETIC"] == 1].copy()
        self.obs_aug = self.aug[self.aug["IS_SYNTHETIC"] == 0].copy()
        self.train_log = pd.read_csv(TRAINLOG) if os.path.exists(TRAINLOG) else None
        print(f"    obs {len(self.obs):,} | syn {len(self.syn):,} | aug {len(self.aug):,}", flush=True)

    def validate_cross_stratum_consistency(self):
        # chart-only override (base class's O(n) iterrows() pass is not needed for the figure)
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
        ax.set_title("Section 7 — Paid-Work by Stratum × Cycle (obs vs calibrated, final population)")
        ax.set_ylabel("% slots in paid work"); ax.legend(fontsize=7)
        plt.tight_layout()
        self.charts.setdefault(7, []).append(("Work by Stratum", V.fig_to_b64(fig)))
        return {}


val = CalVal(step3_dir=os.path.join(ROOT, "outputs_step3"), step4_dir=HERE, sample_mode=False)

# --- spot metrics captured from the same loaded final population, for D3/D5 ---
wd_obs = val.obs[val.obs["DDAY_STRATA"] == 1]
wd_syn = val.syn[val.syn["DDAY_STRATA"] == 1]
wd_obs_pw = (wd_obs[ACT].values == 1).mean() * 100
wd_syn_pw = (wd_syn[ACT].values == 1).mean() * 100
print(f"\n  >>> D3/D5 Weekday Paid-work %: observed {wd_obs_pw:.2f}% | synthetic (final, calibrated) {wd_syn_pw:.2f}% "
      f"(v6 prose claimed obs 13.3% / pre-fix synthetic 25.6%)", flush=True)

cy2005_syn = val.syn[(val.syn["CYCLE_YEAR"] == 2005) & (val.syn["DDAY_STRATA"] == 1)]
cy2005_pw = (cy2005_syn[ACT].values == 1).mean() * 100 if len(cy2005_syn) else float("nan")
print(f"  >>> D5.1c 2005 weekday synthetic Paid-work %: {cy2005_pw:.2f}% (old report showed ~22%)", flush=True)

steps = [("training", val.validate_training_curves),
         ("activity", val.validate_activity_distribution),
         ("at_home", val.validate_at_home_rate),
         ("temporal", val.validate_temporal_structure),
         ("demographic", val.validate_demographic_conditioning),
         ("cross_stratum", val.validate_cross_stratum_consistency)]
mean_js = None
for name, fn in steps:
    try:
        print(f"  chart: {name}...", flush=True)
        res = fn()
        if name == "activity" and isinstance(res, dict):
            mean_js = res.get("mean_js")
    except Exception as e:
        print(f"    !! {name} failed: {e!r}", flush=True)

if mean_js is not None:
    print(f"\n  >>> D3/D5 Fresh aggregate activity JS (final population): {mean_js:.4f}", flush=True)
else:
    print("\n  >>> Fresh aggregate activity JS: UNAVAILABLE (activity step failed)", flush=True)

charts = {}
for sec, lst in val.charts.items():
    for title, b64 in lst:
        charts[title] = b64
print("  generated charts:", list(charts.keys()), flush=True)


def swap_tag(html: str, title: str, new_b64: str, token: str):
    """Locate <img ... alt="{title}"/> by string search (base64 blobs can be
    huge; avoids running a regex over multi-MB lines) and swap it for a fresh
    tag stamped with the idempotency token. Returns (html, status)."""
    anchor = f'alt="{title}"'
    idx = html.find(anchor)
    if idx == -1:
        return html, "missing-alt"
    tag_start = html.rfind("<img", 0, idx)
    tag_end = html.find("/>", idx)
    if tag_start == -1 or tag_end == -1:
        return html, "missing-tag"
    tag = html[tag_start:tag_end + 2]
    if f'data-regen="{token}"' in tag:
        return html, "present"
    new_tag = f'<img src="data:image/png;base64,{new_b64}" alt="{title}" data-regen="{token}"/>'
    html = html[:tag_start] + new_tag + html[tag_end + 2:]
    return html, "replaced"


if not os.path.exists(HTML):
    raise SystemExit(f"{HTML} not found -- copy step4_validation_report_v6.html to "
                      f"step4_validation_report_v7.html first (v6 stays untouched).")
html = open(HTML, encoding="utf-8").read()

replaced, skipped_present, skipped_missing = [], [], []
for title in ALT_TITLES:
    if title not in charts:
        skipped_missing.append(title)
        continue
    html, status = swap_tag(html, title, charts[title], REGEN_TOKEN)
    if status == "replaced":
        replaced.append(title)
    elif status == "present":
        skipped_present.append(title)
    else:
        skipped_missing.append(f"{title} ({status})")

open(HTML, "w", encoding="utf-8").write(html)
print(f"\nWROTE {os.path.basename(HTML)}: {os.path.getsize(HTML)/1024:.0f} KB", flush=True)
print(f"  replaced: {replaced or 'none'}", flush=True)
print(f"  skipped (already present, idempotency guard): {skipped_present or 'none'}", flush=True)
print(f"  skipped (alt/tag not found): {skipped_missing or 'none'}", flush=True)
print(f"SUMMARY: {len(replaced)} replaced, {len(skipped_present)} skipped-present, "
      f"{len(skipped_missing)} skipped-missing", flush=True)
