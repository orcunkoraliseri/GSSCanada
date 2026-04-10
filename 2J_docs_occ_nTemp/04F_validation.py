"""
04F_validation.py — Step 4F: Augmentation Validation & Report Generation

Validates augmented_diaries.csv against observed hetus_30min.csv and
copresence_30min.csv across 8 sections:

  Section 1 — Training curves (from step4_training_log.csv)
  Section 2 — Activity distribution JS divergence
  Section 3 — AT_HOME rate consistency
  Section 4 — Temporal structure plausibility
  Section 5 — Co-presence prevalence match
  Section 6 — Demographic conditioning fidelity
  Section 7 — Cross-stratum consistency
  Section 8 — Dataset statistics summary

Outputs: outputs_step4/step4_validation_report.html (with embedded charts)

Usage:
    python 04F_validation.py
    python 04F_validation.py --sample    # relaxed thresholds for undertrained model
"""

import argparse
import base64
import io
import json
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

N_SLOTS  = 48
N_ACT    = 14
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
STRATA_LABELS  = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
CYCLE_COLORS   = {2005: "#4C72B0", 2010: "#DD8452", 2015: "#55A868", 2022: "#C44E52"}
NIGHT_SLOTS    = list(range(0, 7)) + list(range(37, 48))  # 0-indexed
WORK_SLOTS_IDX = list(range(8, 20))  # slots 9–20 (0-indexed 8–19) ≈ 08:00–14:00


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--step3_dir", default=None)
    p.add_argument("--step4_dir", default=None)
    p.add_argument("--sample", action="store_true",
                   help="Use relaxed thresholds for an undertrained sample model")
    return p.parse_args()


# ── Utilities ────────────────────────────────────────────────────────────────

def fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def js_div(p, q) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / (p.sum() + 1e-12)
    q = q / (q.sum() + 1e-12)
    return float(jensenshannon(p, q) ** 2)


def activity_dist(df_sub, n_act=N_ACT) -> np.ndarray:
    """Mean activity distribution over 48 slots for a set of rows."""
    act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    acts = df_sub[act_cols].values.flatten().astype(float)
    acts = acts[~np.isnan(acts)].astype(int)
    dist = np.bincount(np.clip(acts - 1, 0, n_act - 1), minlength=n_act).astype(float)
    return dist / (dist.sum() + 1e-12)


def status_badge(level: str) -> str:
    colors = {"PASS": "#2ecc71", "WARN": "#f39c12", "FAIL": "#e74c3c"}
    bg = colors.get(level, "#95a5a6")
    return f'<span style="background:{bg};color:white;padding:2px 8px;border-radius:3px;font-weight:bold">{level}</span>'


# ── Validator class ───────────────────────────────────────────────────────────

class AugmentationValidator:

    def __init__(self, step3_dir: str, step4_dir: str, sample_mode: bool = False):
        self.step3_dir   = step3_dir
        self.step4_dir   = step4_dir
        self.sample_mode = sample_mode
        self.thr = self._thresholds()
        self.checks  = []   # list of (section, check_id, description, result, level)
        self.charts  = {}   # section → list of (title, b64_png)
        self._load_data()

    def _thresholds(self) -> dict:
        """Pass/warn/fail thresholds — relaxed for undertrained sample model."""
        if self.sample_mode:
            return {
                "js_pass": 0.20, "js_warn": 0.30,
                "at_home_pp": 10.0,
                "cop_pp": 10.0,
                "transition_pct": 50.0,
                "work_pp": 10.0,
                "demo_r": 0.50,
            }
        return {
            "js_pass": 0.05, "js_warn": 0.05,
            "at_home_pp": 2.0,
            "cop_pp": 3.0,
            "transition_pct": 20.0,
            "work_pp": 3.0,
            "demo_r": 0.90,
        }

    def _load_data(self):
        sfx = "_SAMPLE" if self.sample_mode else ""
        print("  Loading reference data (Step 3)...")
        self.obs = pd.read_csv(
            os.path.join(self.step3_dir, f"hetus_30min{sfx}.csv"), low_memory=False
        )
        cop_path = os.path.join(self.step3_dir, f"copresence_30min{sfx}.csv")
        self.obs_cop = pd.read_csv(cop_path, low_memory=False)

        print("  Loading augmented data (Step 4)...")
        aug_path = os.path.join(self.step4_dir, f"augmented_diaries{sfx}.csv")
        self.aug = pd.read_csv(aug_path, low_memory=False)
        self.syn = self.aug[self.aug["IS_SYNTHETIC"] == 1].copy()
        self.obs_aug = self.aug[self.aug["IS_SYNTHETIC"] == 0].copy()

        log_path = os.path.join(self.step4_dir, "step4_training_log.csv")
        self.train_log = pd.read_csv(log_path) if os.path.exists(log_path) else None

        print(f"    Observed rows: {len(self.obs_aug)} | Synthetic rows: {len(self.syn)}")

    def _add_check(self, section: int, check_id: str, desc: str,
                   value, threshold_pass, threshold_warn=None, fmt=".4f",
                   direction="lower") -> str:
        """Record a check result and return PASS/WARN/FAIL."""
        if direction == "lower":
            if value <= threshold_pass:
                level = "PASS"
            elif threshold_warn is not None and value <= threshold_warn:
                level = "WARN"
            else:
                level = "FAIL"
        else:  # higher is better
            if value >= threshold_pass:
                level = "PASS"
            elif threshold_warn is not None and value >= threshold_warn:
                level = "WARN"
            else:
                level = "FAIL"
        self.checks.append((section, check_id, desc, f"{value:{fmt}}", level))
        return level

    # ── Section 1: Training Curves ───────────────────────────────────────────

    def validate_training_curves(self) -> dict:
        if self.train_log is None or len(self.train_log) == 0:
            self.checks.append((1, "1.0", "Training log available", "MISSING", "FAIL"))
            return {"status": "FAIL"}

        log = self.train_log
        n   = len(log)

        # 1.1 Loss convergence in first 10 epochs
        first10 = log.head(min(10, n))["train_loss"].values
        monotone = all(first10[i] >= first10[i+1] for i in range(len(first10)-1))
        self._add_check(1, "1.1", "Train loss decreasing in first 10 epochs",
                        0 if monotone else 1, 0, direction="lower", fmt=".0f")

        # 1.2 Validation JS improves for ≥20 epochs (check if min JS epoch > 20)
        min_js_epoch = log["val_js"].idxmin() + 1 if "val_js" in log.columns else 0
        self._add_check(1, "1.2", "Val JS improves for ≥20 epochs before plateau",
                        min_js_epoch, 20, direction="higher", fmt=".0f")

        # 1.3 No NaN/Inf in loss
        bad = log["train_loss"].isna().sum() + np.isinf(log["train_loss"].values).sum()
        self._add_check(1, "1.3", "No NaN/Inf in training loss",
                        int(bad), 0, direction="lower", fmt=".0f")

        # 1.4 Early stopping triggered (training stopped before max_epochs=100)
        stopped_early = n < 100
        self._add_check(1, "1.4", "Early stopping triggered (< 100 epochs)",
                        0 if stopped_early else 1, 0, direction="lower", fmt=".0f")

        # Chart 1a: loss curves
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        fig.suptitle("Section 1 — Training Curves", fontsize=13)
        axes[0].plot(log["epoch"], log["train_loss"], label="total")
        if "act_loss" in log.columns:
            axes[0].plot(log["epoch"], log["act_loss"],  label="act  (×1.0)", ls="--")
            axes[0].plot(log["epoch"], log["home_loss"], label="home (×0.5)", ls=":")
            axes[0].plot(log["epoch"], log["cop_loss"],  label="cop  (×0.3)", ls="-.")
        axes[0].set_title("Training Loss")
        axes[0].set_xlabel("Epoch"); axes[0].legend(fontsize=8)

        if "val_js" in log.columns:
            axes[1].plot(log["epoch"], log["val_js"], color="crimson")
        axes[1].set_title("Validation JS Divergence"); axes[1].set_xlabel("Epoch")

        if "grad_norm" in log.columns:
            axes[2].plot(log["epoch"], log["grad_norm"], color="purple")
            axes[2].axhline(1.0, color="red", ls="--", label="clip=1.0")
        axes[2].set_title("Gradient Norm"); axes[2].set_xlabel("Epoch")
        axes[2].legend(fontsize=8)

        plt.tight_layout()
        self.charts.setdefault(1, []).append(("Training Curves", fig_to_b64(fig)))
        return {"n_epochs": n, "min_val_js_epoch": min_js_epoch}

    # ── Section 2: Activity Distribution Fidelity ────────────────────────────

    def validate_activity_distribution(self) -> dict:
        thr = self.thr
        all_js = []

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle("Section 2 — Activity Distribution (observed vs. synthetic)", fontsize=13)

        for ax, (s, label) in zip(axes, STRATA_LABELS.items()):
            obs_s = self.obs[self.obs["DDAY_STRATA"] == s]
            syn_s = self.syn[self.syn["DDAY_STRATA"] == s]
            p_obs = activity_dist(obs_s)
            p_syn = activity_dist(syn_s)
            x = np.arange(1, N_ACT + 1)
            w = 0.35
            ax.bar(x - w/2, p_obs * 100, width=w, label="Observed", alpha=0.8)
            ax.bar(x + w/2, p_syn * 100, width=w, label="Synthetic", alpha=0.8)
            ax.set_title(label); ax.set_xlabel("Activity"); ax.set_ylabel("%")
            ax.legend(fontsize=8); ax.tick_params(labelsize=7)
            js = js_div(p_obs, p_syn)
            all_js.append(js)

        plt.tight_layout()
        self.charts.setdefault(2, []).append(("Activity Distribution by Stratum", fig_to_b64(fig)))

        # JS heatmap: 4 cycles × 3 strata
        cycles = sorted(self.obs["CYCLE_YEAR"].unique())
        js_matrix = np.zeros((len(cycles), 3))
        for ci, cy in enumerate(cycles):
            for si, s in enumerate([1, 2, 3]):
                obs_sub = self.obs[(self.obs["CYCLE_YEAR"] == cy) & (self.obs["DDAY_STRATA"] == s)]
                syn_sub = self.syn[(self.syn["CYCLE_YEAR"] == cy) & (self.syn["DDAY_STRATA"] == s)]
                if len(obs_sub) == 0 or len(syn_sub) == 0:
                    continue
                js_matrix[ci, si] = js_div(activity_dist(obs_sub), activity_dist(syn_sub))

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        im = ax2.imshow(js_matrix, vmin=0, vmax=0.10, cmap="RdYlGn_r", aspect="auto")
        ax2.set_xticks(range(3)); ax2.set_xticklabels(["Weekday", "Saturday", "Sunday"])
        ax2.set_yticks(range(len(cycles))); ax2.set_yticklabels(cycles)
        ax2.set_title("JS Divergence Heatmap (4 cycles × 3 strata)")
        plt.colorbar(im, ax=ax2, label="JS")
        for ci in range(len(cycles)):
            for si in range(3):
                ax2.text(si, ci, f"{js_matrix[ci, si]:.3f}", ha="center", va="center",
                         fontsize=8, color="black")
        plt.tight_layout()
        self.charts[2].append(("JS Heatmap", fig_to_b64(fig2)))

        # Record checks
        for ci, cy in enumerate(cycles):
            for si, s in enumerate([1, 2, 3]):
                v = js_matrix[ci, si]
                self._add_check(2, f"2.1_{cy}_{s}",
                                 f"JS div {cy} × {STRATA_LABELS[s]}",
                                 v, thr["js_pass"], thr["js_warn"])

        overall_js = np.mean(js_matrix[js_matrix > 0])
        self._add_check(2, "2.2", "Overall JS divergence (all strata)", overall_js,
                        0.03, 0.05)

        return {"mean_js": float(overall_js), "js_matrix": js_matrix}

    # ── Section 3: AT_HOME Rate Consistency ──────────────────────────────────

    def validate_at_home_rate(self) -> dict:
        thr = self.thr
        cycles = sorted(self.obs["CYCLE_YEAR"].unique())
        hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

        results = {}
        for cy in cycles:
            for s in [1, 2, 3]:
                obs_sub = self.obs[(self.obs["CYCLE_YEAR"] == cy) &
                                   (self.obs["DDAY_STRATA"] == s)]
                syn_sub = self.syn[(self.syn["CYCLE_YEAR"] == cy) &
                                   (self.syn["DDAY_STRATA"] == s)]
                if len(obs_sub) == 0 or len(syn_sub) == 0:
                    continue
                r_obs = obs_sub[hom_cols].values.mean() * 100
                r_syn = syn_sub[[c for c in hom_cols if c in syn_sub.columns]].values.mean() * 100
                delta = abs(r_obs - r_syn)
                results[(cy, s)] = {"obs": r_obs, "syn": r_syn, "delta": delta}
                self._add_check(3, f"3.1_{cy}_{s}",
                                 f"|ΔAT_HOME| {cy} × {STRATA_LABELS[s]}",
                                 delta, thr["at_home_pp"])

        # Chart: daily AT_HOME rhythm per stratum
        fig, axes = plt.subplots(1, 3, figsize=(18, 4))
        fig.suptitle("Section 3 — AT_HOME Daily Rhythm (observed vs. synthetic)", fontsize=13)
        slots_x = np.arange(N_SLOTS)
        for ax, (s, label) in zip(axes, STRATA_LABELS.items()):
            obs_s = self.obs[self.obs["DDAY_STRATA"] == s]
            syn_s = self.syn[self.syn["DDAY_STRATA"] == s]
            hcols = [f"hom30_{i:03d}" for i in range(1, N_SLOTS + 1)]
            hcols_ok = [c for c in hcols if c in syn_s.columns]
            if len(obs_s):
                ax.plot(slots_x, obs_s[hcols].mean(axis=0).values * 100,
                        label="Observed", lw=2)
            if len(syn_s):
                ax.plot(slots_x, syn_s[hcols_ok].mean(axis=0).values * 100,
                        label="Synthetic", lw=2, ls="--")
            ax.set_title(label); ax.set_xlabel("Slot (30-min)"); ax.set_ylabel("AT_HOME %")
            ax.legend(fontsize=8); ax.set_ylim(0, 100)
        plt.tight_layout()
        self.charts.setdefault(3, []).append(("AT_HOME Daily Rhythm", fig_to_b64(fig)))

        return results

    # ── Section 4: Temporal Structure Plausibility ────────────────────────────

    def validate_temporal_structure(self) -> dict:
        thr = self.thr
        act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]

        def count_transitions(row_acts):
            return sum(row_acts[i] != row_acts[i+1] for i in range(len(row_acts)-1))

        def sleep_transitions(row_acts):
            night = [row_acts[i] for i in NIGHT_SLOTS]
            return sum(1 for i in range(len(night)-1) if
                       (night[i] == 1) != (night[i+1] == 1))  # raw cat 1 = sleep

        # 4.2 Transition rate
        obs_acts = self.obs[act_cols].values
        syn_acts = self.syn[[c for c in act_cols if c in self.syn.columns]].values

        obs_trans = np.array([count_transitions(row) for row in obs_acts])
        syn_trans = np.array([count_transitions(row) for row in syn_acts])

        ratio = syn_trans.mean() / max(obs_trans.mean(), 1e-6)
        self._add_check(4, "4.2", "Activity transition rate ratio (syn/obs)",
                        abs(ratio - 1.0) * 100, thr["transition_pct"])

        # 4.1 Sleep continuity (slots in NIGHT_SLOTS should be mostly sleep)
        night_sleep_rate = np.mean(obs_acts[:, NIGHT_SLOTS] == 1)
        syn_night_cols = [f"act30_{s+1:03d}" for s in NIGHT_SLOTS
                          if f"act30_{s+1:03d}" in self.syn.columns]
        syn_night_sleep = np.mean(
            self.syn[syn_night_cols].values == 1 if syn_night_cols else [[0.5]]
        )
        self._add_check(4, "4.1", "Night-slot sleep rate (synthetic)",
                        abs(night_sleep_rate - syn_night_sleep) * 100,
                        thr["transition_pct"])

        # 4.3 Work peak hours (slots 9–20, raw category 5 = paid work)
        obs_work_slots = obs_acts[:, 8:20]
        obs_work_rate  = (obs_work_slots == 5).mean() * 100
        syn_work_cols  = [f"act30_{s+1:03d}" for s in range(8, 20)
                          if f"act30_{s+1:03d}" in self.syn.columns]
        syn_work_rate  = (self.syn[syn_work_cols].values == 5).mean() * 100 if syn_work_cols else 0
        self._add_check(4, "4.3", "Work peak rate delta (slots 9–20)",
                        abs(obs_work_rate - syn_work_rate), thr["work_pp"])

        # Chart: activity heatmap obs vs syn (Weekday only for brevity)
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle("Section 4 — Activity Heatmap (Weekday: observed vs. synthetic)", fontsize=13)
        obs_wd = self.obs[self.obs["DDAY_STRATA"] == 1][act_cols].values
        syn_wd = self.syn[self.syn["DDAY_STRATA"] == 1][[c for c in act_cols
                          if c in self.syn.columns]].values
        for ax, arr, title in zip(axes, [obs_wd, syn_wd], ["Observed", "Synthetic"]):
            hmap = np.zeros((N_ACT, N_SLOTS))
            for cat in range(1, N_ACT + 1):
                hmap[cat-1] = (arr == cat).mean(axis=0) * 100
            im = ax.imshow(hmap, aspect="auto", cmap="YlOrRd", vmin=0, vmax=80)
            ax.set_title(title); ax.set_xlabel("Slot (30-min)")
            ax.set_ylabel("Activity category")
            ax.set_yticks(range(N_ACT)); ax.set_yticklabels(range(1, N_ACT+1), fontsize=7)
            plt.colorbar(im, ax=ax, label="% respondents")
        plt.tight_layout()
        self.charts.setdefault(4, []).append(("Activity Heatmap", fig_to_b64(fig)))

        return {"obs_trans_mean": obs_trans.mean(), "syn_trans_mean": syn_trans.mean(),
                "ratio": ratio}

    # ── Section 5: Co-Presence Prevalence ────────────────────────────────────

    def validate_copresence_prevalence(self) -> dict:
        thr = self.thr
        cycles = sorted(self.obs["CYCLE_YEAR"].unique())

        # 5.2 Colleagues masking
        old_syn = self.syn[self.syn["CYCLE_YEAR"].isin([2005, 2010])]
        col_cols = [c for c in self.aug.columns if c.startswith("colleagues30_")]
        if len(old_syn) > 0 and col_cols:
            max_col = old_syn[col_cols].fillna(0).max().max()
            self._add_check(5, "5.2", "colleagues = 0 for 2005/2010 synthetic",
                            float(max_col), 0, direction="lower", fmt=".4f")

        # 5.4 Co-presence value range
        for cn in COP_COLS:
            cop_c = [c for c in self.aug.columns if c.startswith(f"{cn}30_")]
            if not cop_c:
                continue
            vals = self.syn[cop_c].dropna().values.flatten()
            out_range = ((vals < 0) | (vals > 1)).sum()
            self._add_check(5, f"5.4_{cn}", f"{cn} values in {{0,1}}",
                            int(out_range), 0, direction="lower", fmt=".0f")

        # 5.1 Per-column prevalence
        prev_obs = {}
        prev_syn = {}
        for cn in COP_COLS:
            cop_c = [f"{cn}30_{s:03d}" for s in range(1, N_SLOTS+1)]
            cop_ok = [c for c in cop_c if c in self.obs.columns]
            if not cop_ok:
                continue
            obs_vals = self.obs[cop_ok].values
            # Only count non-NaN (availability-aware)
            prev_obs[cn] = np.nanmean(obs_vals == 1) * 100
            syn_vals = self.syn[[c for c in cop_ok if c in self.syn.columns]].values
            prev_syn[cn] = np.nanmean(syn_vals == 1) * 100
            delta = abs(prev_obs[cn] - prev_syn[cn])
            self._add_check(5, f"5.1_{cn}", f"|Δprev| {cn}",
                            delta, thr["cop_pp"])

        # Chart 5a: prevalence grouped bars
        cop_names = [cn for cn in COP_COLS if cn in prev_obs]
        if cop_names:
            fig, ax = plt.subplots(figsize=(12, 4))
            x = np.arange(len(cop_names))
            w = 0.35
            ax.bar(x - w/2, [prev_obs[cn] for cn in cop_names], width=w, label="Observed")
            ax.bar(x + w/2, [prev_syn[cn] for cn in cop_names], width=w, label="Synthetic",
                   alpha=0.8)
            ax.set_xticks(x); ax.set_xticklabels(cop_names, rotation=30, ha="right")
            ax.set_title("Section 5 — Co-Presence Prevalence (observed vs. synthetic)")
            ax.set_ylabel("% slots present"); ax.legend()
            plt.tight_layout()
            self.charts.setdefault(5, []).append(("Co-Presence Prevalence", fig_to_b64(fig)))

        return {"prev_obs": prev_obs, "prev_syn": prev_syn}

    # ── Section 6: Demographic Conditioning Fidelity ─────────────────────────

    def validate_demographic_conditioning(self) -> dict:
        thr = self.thr

        # 6.2 LFTAG work hour separation
        act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS+1)]

        def work_prop(df):
            a = df[[c for c in act_cols if c in df.columns]].values
            return (a == 5).mean()  # raw category 5 = paid work

        if "LFTAG" in self.obs.columns and "LFTAG" in self.syn.columns:
            employed_obs = self.obs[self.obs["LFTAG"] == 1]   # LFTAG=1 typically employed
            nilf_obs     = self.obs[self.obs["LFTAG"] == 5]   # not-in-labour-force
            employed_syn = self.syn[self.syn["LFTAG"] == 1]
            nilf_syn     = self.syn[self.syn["LFTAG"] == 5]

            obs_sep  = work_prop(employed_obs) > work_prop(nilf_obs)
            syn_sep  = work_prop(employed_syn) > work_prop(nilf_syn)
            self._add_check(6, "6.2", "Employed > NILF work hours (synthetic)",
                            0 if syn_sep else 1, 0, direction="lower", fmt=".0f")

        # 6.1 AGEGRP activity correlation
        r_vals = []
        if "AGEGRP" in self.obs.columns and "AGEGRP" in self.syn.columns:
            for ag in self.obs["AGEGRP"].unique():
                obs_ag = self.obs[self.obs["AGEGRP"] == ag]
                syn_ag = self.syn[self.syn["AGEGRP"] == ag]
                if len(obs_ag) < 5 or len(syn_ag) < 5:
                    continue
                d_obs = activity_dist(obs_ag)
                d_syn = activity_dist(syn_ag)
                r = float(np.corrcoef(d_obs, d_syn)[0, 1]) if d_obs.std() > 0 else 0
                r_vals.append(r)
        mean_r = float(np.mean(r_vals)) if r_vals else 0.0
        self._add_check(6, "6.1", "Mean AGEGRP activity correlation (r)",
                        mean_r, thr["demo_r"], thr["demo_r"] * 0.9, direction="higher")

        # Chart 6b: work proportion by LFTAG
        if "LFTAG" in self.obs.columns and "LFTAG" in self.syn.columns:
            lftags = sorted(self.obs["LFTAG"].dropna().unique())
            obs_wp = [work_prop(self.obs[self.obs["LFTAG"] == l]) * 100 for l in lftags]
            syn_wp = [work_prop(self.syn[self.syn["LFTAG"] == l]) * 100 for l in lftags]
            fig, ax = plt.subplots(figsize=(8, 4))
            x = np.arange(len(lftags))
            ax.bar(x - 0.2, obs_wp, 0.4, label="Observed")
            ax.bar(x + 0.2, syn_wp, 0.4, label="Synthetic", alpha=0.8)
            ax.set_xticks(x); ax.set_xticklabels([f"LFTAG={l}" for l in lftags])
            ax.set_title("Section 6 — Paid-Work Proportion by LFTAG")
            ax.set_ylabel("% slots in paid work"); ax.legend()
            plt.tight_layout()
            self.charts.setdefault(6, []).append(("Work Proportion by LFTAG", fig_to_b64(fig)))

        return {"mean_agegrp_r": mean_r}

    # ── Section 7: Cross-Stratum Consistency ─────────────────────────────────

    def validate_cross_stratum_consistency(self) -> dict:
        act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS+1)]

        # For each respondent in aug, check ordering of work proportion across strata
        # Group by occID
        aug_work = {}
        for _, row in self.aug.iterrows():
            oid = row["occID"]
            s   = row["DDAY_STRATA"]
            a   = row[[c for c in act_cols if c in self.aug.columns]].values.astype(float)
            wp  = (a == 5).mean()
            aug_work.setdefault(oid, {})[s] = wp

        # 7.1 Weekday work > Saturday > Sunday for each respondent
        n_ok = 0
        n_tot = 0
        for oid, sw in aug_work.items():
            if 1 in sw and 2 in sw and 3 in sw:
                n_tot += 1
                if sw[1] >= sw[2] and sw[2] >= sw[3]:
                    n_ok += 1
        pct_order = (n_ok / max(n_tot, 1)) * 100
        self._add_check(7, "7.1", "Work ordering: Weekday ≥ Sat ≥ Sun (%)",
                        pct_order, 90, 80, direction="higher")

        # 7.4 Weekend AT_HOME ≥ Weekday for each respondent
        hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS+1)]
        aug_home = {}
        for _, row in self.aug.iterrows():
            oid = row["occID"]; s = row["DDAY_STRATA"]
            h = row[[c for c in hom_cols if c in self.aug.columns]].values.astype(float)
            aug_home.setdefault(oid, {})[s] = h.mean()
        n_ok_h = sum(1 for sw in aug_home.values()
                     if 1 in sw and 2 in sw and sw[2] >= sw[1])
        n_tot_h = sum(1 for sw in aug_home.values() if 1 in sw and 2 in sw)
        pct_home = (n_ok_h / max(n_tot_h, 1)) * 100
        self._add_check(7, "7.4", "Weekend AT_HOME ≥ Weekday (%)",
                        pct_home, 80, 70, direction="higher")

        # Chart 7b: work proportion by stratum
        cycles = sorted(self.obs["CYCLE_YEAR"].unique())
        strata = [1, 2, 3]
        fig, ax = plt.subplots(figsize=(10, 4))
        x = np.arange(len(cycles))
        w = 0.25
        for si, s in enumerate(strata):
            obs_wp = []
            syn_wp = []
            for cy in cycles:
                o = self.obs[(self.obs["CYCLE_YEAR"] == cy) & (self.obs["DDAY_STRATA"] == s)]
                sv = self.syn[(self.syn["CYCLE_YEAR"] == cy) & (self.syn["DDAY_STRATA"] == s)]
                obs_wp.append(
                    (o[[c for c in act_cols if c in o.columns]].values == 5).mean() * 100
                    if len(o) else 0
                )
                syn_wp.append(
                    (sv[[c for c in act_cols if c in sv.columns]].values == 5).mean() * 100
                    if len(sv) else 0
                )
            ax.bar(x + si * w - w, obs_wp, w * 0.8,
                   label=f"Obs {STRATA_LABELS[s]}", alpha=0.8,
                   color=list(CYCLE_COLORS.values())[si])
            ax.bar(x + si * w - w + w * 0.4, syn_wp, w * 0.4,
                   alpha=0.6, color=list(CYCLE_COLORS.values())[si], hatch="//")
        ax.set_xticks(x); ax.set_xticklabels(cycles)
        ax.set_title("Section 7 — Paid-Work by Stratum × Cycle")
        ax.set_ylabel("% slots in paid work"); ax.legend(fontsize=7)
        plt.tight_layout()
        self.charts.setdefault(7, []).append(("Work by Stratum", fig_to_b64(fig)))

        return {"pct_work_order": pct_order, "pct_home_order": pct_home}

    # ── Section 8: Summary Statistics ────────────────────────────────────────

    def generate_summary_table(self) -> dict:
        cycles = sorted(self.obs["CYCLE_YEAR"].unique())
        hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS+1)]
        act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS+1)]

        rows = []
        for cy in cycles:
            obs_cy  = self.obs[self.obs["CYCLE_YEAR"] == cy]
            syn_cy  = self.syn[self.syn["CYCLE_YEAR"] == cy]
            aug_cy  = self.aug[self.aug["CYCLE_YEAR"] == cy]

            mean_js = np.mean([
                js_div(activity_dist(obs_cy[obs_cy["DDAY_STRATA"] == s]),
                       activity_dist(syn_cy[syn_cy["DDAY_STRATA"] == s]))
                for s in [1, 2, 3]
                if len(obs_cy[obs_cy["DDAY_STRATA"] == s]) > 0
                   and len(syn_cy[syn_cy["DDAY_STRATA"] == s]) > 0
            ]) if len(syn_cy) > 0 else float("nan")

            obs_hom = obs_cy[hom_cols].values.mean() * 100 if len(obs_cy) else np.nan
            syn_hom_cols = [c for c in hom_cols if c in syn_cy.columns]
            syn_hom = syn_cy[syn_hom_cols].values.mean() * 100 if len(syn_cy) and syn_hom_cols else np.nan
            d_hom   = abs(obs_hom - syn_hom) if not np.isnan(obs_hom + syn_hom) else np.nan

            rows.append({
                "CYCLE_YEAR":             cy,
                "Observed diary-days":    len(obs_cy),
                "Synthetic diary-days":   len(syn_cy),
                "Total augmented (×3)":   len(aug_cy),
                "Mean JS divergence":     f"{mean_js:.4f}" if not np.isnan(mean_js) else "N/A",
                "|ΔAT_HOME| (pp)":        f"{d_hom:.2f}" if not np.isnan(d_hom) else "N/A",
            })

        total_row = {
            "CYCLE_YEAR":             "TOTAL",
            "Observed diary-days":    len(self.obs),
            "Synthetic diary-days":   len(self.syn),
            "Total augmented (×3)":   len(self.aug),
            "Mean JS divergence":     "—",
            "|ΔAT_HOME| (pp)":        "—",
        }
        rows.append(total_row)
        return rows

    # ── HTML Report ─────────────────────────────────────────────────────────

    def build_html_report(self, summary_table: list, checkpoint: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Severity counts
        n_pass = sum(1 for c in self.checks if c[4] == "PASS")
        n_warn = sum(1 for c in self.checks if c[4] == "WARN")
        n_fail = sum(1 for c in self.checks if c[4] == "FAIL")

        def check_rows():
            rows_html = ""
            for sec, cid, desc, val, level in self.checks:
                badge = status_badge(level)
                rows_html += (
                    f"<tr><td>{sec}</td><td>{cid}</td>"
                    f"<td>{desc}</td><td><code>{val}</code></td>"
                    f"<td>{badge}</td></tr>\n"
                )
            return rows_html

        def chart_sections():
            html = ""
            for sec in sorted(self.charts.keys()):
                sec_titles = {
                    1: "Section 1 — Training Curves",
                    2: "Section 2 — Activity Distribution Fidelity",
                    3: "Section 3 — AT_HOME Rate Consistency",
                    4: "Section 4 — Temporal Structure Plausibility",
                    5: "Section 5 — Co-Presence Prevalence",
                    6: "Section 6 — Demographic Conditioning",
                    7: "Section 7 — Cross-Stratum Consistency",
                }
                html += f"<h2>{sec_titles.get(sec, f'Section {sec}')}</h2>\n"
                for title, b64 in self.charts[sec]:
                    html += (f"<h3>{title}</h3>\n"
                             f'<img src="data:image/png;base64,{b64}" '
                             f'style="max-width:100%;margin:10px 0"/>\n')
            return html

        def summary_rows():
            if not summary_table:
                return "<tr><td colspan='6'>No data</td></tr>"
            cols = list(summary_table[0].keys())
            header = "".join(f"<th>{c}</th>" for c in cols)
            body = ""
            for row in summary_table:
                body += "<tr>" + "".join(f"<td>{row.get(c, '')}</td>" for c in cols) + "</tr>"
            return f"<thead><tr>{header}</tr></thead><tbody>{body}</tbody>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Step 4 Validation Report</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
  h1   {{ color: #2c3e50; }}
  h2   {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0 20px 0; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 13px; }}
  th {{ background: #f2f2f2; }}
  .summary-box {{ background: #ecf0f1; padding: 15px; border-radius: 6px; margin: 20px 0; }}
  code {{ background: #f8f8f8; padding: 1px 4px; border-radius: 3px; }}
</style>
</head>
<body>
<h1>Step 4 — Conditional Transformer Augmentation: Validation Report</h1>

<div class="summary-box">
  <strong>Generated:</strong> {now}<br>
  <strong>Checkpoint:</strong> {checkpoint}<br>
  <strong>Observed rows:</strong> {len(self.obs_aug):,} &nbsp;|&nbsp;
  <strong>Synthetic rows:</strong> {len(self.syn):,} &nbsp;|&nbsp;
  <strong>Total augmented:</strong> {len(self.aug):,}
  <br><br>
  <strong>Checks — PASS: {n_pass} &nbsp; WARN: {n_warn} &nbsp; FAIL: {n_fail}</strong>
</div>

<h2>All Checks Summary</h2>
<table>
<thead><tr><th>Sec</th><th>Check ID</th><th>Description</th><th>Value</th><th>Status</th></tr></thead>
<tbody>{check_rows()}</tbody>
</table>

{chart_sections()}

<h2>Section 8 — Dataset Statistics Summary</h2>
<table>{summary_rows()}</table>

<hr>
<p style="color:#999;font-size:12px">
  Step 4 — Conditional Transformer Augmentation | occModeling pipeline |
  Report generated: {now}
</p>
</body>
</html>"""
        return html

    # ── Run all ─────────────────────────────────────────────────────────────

    def run_all(self):
        print("Running validation...")

        print("  Section 1: Training curves...")
        self.validate_training_curves()

        print("  Section 2: Activity distribution fidelity...")
        self.validate_activity_distribution()

        print("  Section 3: AT_HOME rate consistency...")
        self.validate_at_home_rate()

        print("  Section 4: Temporal structure plausibility...")
        self.validate_temporal_structure()

        print("  Section 5: Co-presence prevalence...")
        self.validate_copresence_prevalence()

        print("  Section 6: Demographic conditioning fidelity...")
        self.validate_demographic_conditioning()

        print("  Section 7: Cross-stratum consistency...")
        self.validate_cross_stratum_consistency()

        print("  Section 8: Summary table...")
        summary = self.generate_summary_table()

        # Build and save HTML report
        ckpt_path = os.path.join(self.step4_dir, "checkpoints", "best_model.pt")
        html = self.build_html_report(summary, ckpt_path)

        report_path = os.path.join(self.step4_dir, "step4_validation_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Print summary to console
        n_pass = sum(1 for c in self.checks if c[4] == "PASS")
        n_warn = sum(1 for c in self.checks if c[4] == "WARN")
        n_fail = sum(1 for c in self.checks if c[4] == "FAIL")
        print(f"\n✓ Validation complete.")
        print(f"  PASS: {n_pass}  WARN: {n_warn}  FAIL: {n_fail}")
        print(f"  Report saved: {report_path}")


def main():
    args = parse_args()
    base_dir = os.path.join(
        SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4"
    )
    step3_dir = args.step3_dir or os.path.join(SCRIPT_DIR, "outputs_step3")
    step4_dir = args.step4_dir or base_dir

    print("=" * 60)
    print(f"Step 4F — Validation  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)

    AugmentationValidator(step3_dir, step4_dir, sample_mode=args.sample).run_all()


if __name__ == "__main__":
    main()
