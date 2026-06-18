# -*- coding: utf-8 -*-
"""
3rdJ_04_augmentationGSS_2split_val.py

Step 4 Validator for Leg-2 (Residential + Office / AT_WORK) Occupancy Pipeline.

Ported from:  2J_docs_occ_nTemp/04F_validation.py  (Leg-1)
Companion gate spec: Step4_docs/3rdJ_04_augmentationGSS_val.md

Validates Step-4 augmented diaries for BOTH occupancy channels:
  - Residential (AT_HOME)  -> Leg-1 gates G1-G4 (ported, production thresholds)
  - Office      (AT_WORK)  -> Leg-2 NEW gates OW1-OW6

Three populations are compared inside augmented_diaries.csv:
  observed  (IS_SYNTHETIC == 0)
  synthetic (IS_SYNTHETIC == 1)
  vs Step-3 reference marginals (hetus_30min / copresence_30min / work_30min).

Gates per (cycle x stratum) unless noted. DDAY_STRATA: 1=weekday, 2=Saturday, 3=Sunday.
Slot grid = 48 x 30-min, 04:00 origin (as Step-3).

Report sections (mirror the val.md):
  1 Training health      (loss / val_js / home_gap / work_gap / sigma curves)
  2 Activity JS heatmap  (G1)
  3 AT_HOME marginals + rhythm  (G2)
  4 Activity temporal    (G4)
  5 Co-presence prevalence (G3)
  6 AT_WORK marginals + diurnal [NEW headline]  (OW1/OW2/OW3)
  7 AT_WORK sanity       (OW4/OW5/OW6)
  8 Secondary distributional (KL/EMD/transition/dwell/ACF; both channels; not gated)
  9 Scorecard summary

Output:
  outputs_step4/step4_validation_report.html  (dark theme, base64 PNG, scorecard)
  outputs_step4/step4_validation_report.txt   (PASS/WARN/FAIL lines for cluster log)

Run locally:
    cd Step4_docs
    py -3 -X utf8 3rdJ_04_augmentationGSS_2split_val.py            # full / production
    py -3 -X utf8 3rdJ_04_augmentationGSS_2split_val.py --sample   # smoke, relaxed thresholds
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import platform
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import seaborn as sns  # noqa: F401  (imported for parity; styling done manually)
except Exception:
    sns = None

try:
    from scipy.spatial.distance import jensenshannon
    from scipy.stats import wasserstein_distance, ks_2samp, pearsonr
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False


# ── Platform-detection path block ─────────────────────────────────────────────
_SYSTEM = platform.system()

if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.join(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main",
        r"3J_docs_occ_nTemp\Leg2_2-split",
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"), "GSSCanada", "GSSCanada-main",
        "3J_docs_occ_nTemp", "Leg2_2-split",
    )

STEP3_DIR_DEFAULT = os.path.join(_LEG2_BASE, "Step3_docs", "outputs_step3")
STEP4_DIR_DEFAULT = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")


# ── Constants ──────────────────────────────────────────────────────────────────

N_SLOTS = 48
N_ACT = 14
CYCLES = [2005, 2010, 2015, 2022]
STRATA_LABELS = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
STRATA_COLORS = {1: "#89b4fa", 2: "#f38ba8", 3: "#a6e3a1"}
CYCLE_COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]

COP_COLS = [
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others", "colleagues",
]

ACT_LABELS = {
    1: "Work & Related", 2: "Household Work", 3: "Caregiving", 4: "Purchasing",
    5: "Sleep & Rest", 6: "Eating & Drinking", 7: "Personal Care", 8: "Education",
    9: "Socializing", 10: "Passive Leisure", 11: "Active Leisure", 12: "Community",
    13: "Travel", 14: "Misc / Idle",
}

# Night slots in 04:00-origin 48-grid.
# 00:00 = slot index 40 (0-indexed); 05:00 = slot index 2 (0-indexed).
# 00:00-05:00 night window => 0-indexed slots {40..47} U {0,1} (i.e. 1-indexed 41..48, 1..2).
NIGHT_SLOTS = list(range(40, 48)) + [0, 1]
# General "night" used in temporal section (deep sleep window): early AM + late PM
SLEEP_NIGHT_SLOTS = list(range(0, 4)) + list(range(40, 48))
WORK_PEAK_SLOTS = list(range(8, 20))   # 0-indexed ~ 12:00-22:00 in 04:00 origin; legacy Leg-1 window

RAW_SLEEP_CAT = 5   # Sleep & Rest
RAW_WORK_CAT = 1    # Work & Related

_DARK = {
    "figure.facecolor": "#1e1e2e",
    "axes.facecolor": "#2a2a3e",
    "axes.edgecolor": "#555",
    "axes.labelcolor": "#cdd6f4",
    "xtick.color": "#cdd6f4",
    "ytick.color": "#cdd6f4",
    "text.color": "#cdd6f4",
    "grid.color": "#444",
    "legend.facecolor": "#2a2a3e",
    "legend.edgecolor": "#555",
    "font.family": "sans-serif",
    "font.size": 11,
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _apply_dark() -> None:
    plt.rcParams.update(_DARK)


def _b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def js_div(p, q) -> float:
    """Squared Jensen-Shannon divergence between two distributions."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / (p.sum() + 1e-12)
    q = q / (q.sum() + 1e-12)
    if _HAVE_SCIPY:
        return float(jensenshannon(p, q) ** 2)
    # manual fallback
    m = 0.5 * (p + q)
    def _kl(a, b):
        a = np.clip(a, 1e-12, None); b = np.clip(b, 1e-12, None)
        return float(np.sum(a * np.log(a / b)))
    return float(0.5 * _kl(p, m) + 0.5 * _kl(q, m))


def activity_dist(df_sub, n_act=N_ACT) -> np.ndarray:
    """Mean activity distribution over 48 slots for a set of rows."""
    act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    cols = [c for c in act_cols if c in df_sub.columns]
    if not cols or len(df_sub) == 0:
        return np.ones(n_act) / n_act
    acts = df_sub[cols].values.flatten().astype(float)
    acts = acts[~np.isnan(acts)].astype(int)
    if acts.size == 0:
        return np.ones(n_act) / n_act
    dist = np.bincount(np.clip(acts - 1, 0, n_act - 1), minlength=n_act).astype(float)
    return dist / (dist.sum() + 1e-12)


def present_cols(df, prefix):
    """Slot columns of the form <prefix>_001..048 (e.g. act30_, hom30_, wrk30_)."""
    return [c for c in (f"{prefix}_{s:03d}" for s in range(1, N_SLOTS + 1)) if c in df.columns]


def cop_cols(df, channel):
    """Co-presence slot columns of the form <channel>30_001..048 (e.g. Alone30_)."""
    return [c for c in (f"{channel}30_{s:03d}" for s in range(1, N_SLOTS + 1)) if c in df.columns]


# ── Validator ─────────────────────────────────────────────────────────────────

class AugmentationValidator2Split:

    def __init__(self, step3_dir: str, step4_dir: str, sample_mode: bool = False):
        self.step3_dir = step3_dir
        self.step4_dir = step4_dir
        self.sample_mode = sample_mode
        self.thr = self._thresholds()
        self.results = {"pass": [], "warn": [], "fail": []}  # PASS/WARN/FAIL lines
        self.plots_b64 = {}   # key -> base64 PNG
        self.summary_rows = []
        self._load_data()

    # ── thresholds ────────────────────────────────────────────────────────────

    def _thresholds(self) -> dict:
        """PASS/WARN gate thresholds. --sample relaxes them (undertrained model)."""
        if self.sample_mode:
            return {
                # residential
                "g1_js_pass": 0.20, "g1_js_warn": 0.30, "g1_overall": 0.20,
                "g2_home_pass": 10.0, "g2_home_warn": 15.0,
                "g3_cop_pass": 10.0, "g3_cop_warn": 15.0,
                "g4_trans_pass": 50.0, "g4_trans_warn": 80.0,
                "g4_slot_pp_pass": 10.0, "g4_slot_pp_warn": 15.0,
                # office
                "ow1_pass": 12.0, "ow1_warn": 18.0,
                "ow2_pass": 0.70, "ow2_warn": 0.50,
                "ow3_pass": 6, "ow3_warn": 10,
                "ow4_pass": 12.0, "ow4_warn": 18.0,
                "ow5_pass": 70.0, "ow5_warn": 50.0,
                "ow6_pass": 5.0, "ow6_warn": 15.0,
            }
        return {
            # residential
            "g1_js_pass": 0.05, "g1_js_warn": 0.10, "g1_overall": 0.03,
            "g2_home_pass": 2.0, "g2_home_warn": 4.0,
            "g3_cop_pass": 3.0, "g3_cop_warn": 6.0,
            "g4_trans_pass": 20.0, "g4_trans_warn": 40.0,
            "g4_slot_pp_pass": 3.0, "g4_slot_pp_warn": 6.0,
            # office
            "ow1_pass": 5.0, "ow1_warn": 8.0,
            "ow2_pass": 0.95, "ow2_warn": 0.90,
            "ow3_pass": 2, "ow3_warn": 4,
            "ow4_pass": 5.0, "ow4_warn": 8.0,
            "ow5_pass": 90.0, "ow5_warn": 80.0,
            "ow6_pass": 1.0, "ow6_warn": 5.0,
        }

    # ── data loading ──────────────────────────────────────────────────────────

    def _load_data(self):
        sfx = "_SAMPLE" if self.sample_mode else ""
        print("  Loading augmented diaries (Step 4)...")
        aug_path = os.path.join(self.step4_dir, f"augmented_diaries{sfx}.csv")
        if not os.path.exists(aug_path):
            aug_path = os.path.join(self.step4_dir, "augmented_diaries.csv")
        self.aug_path = aug_path
        if not os.path.exists(aug_path):
            raise FileNotFoundError(f"augmented_diaries.csv not found at {aug_path}")
        self.aug = pd.read_csv(aug_path, low_memory=False)
        if "IS_SYNTHETIC" in self.aug.columns:
            self.syn = self.aug[self.aug["IS_SYNTHETIC"] == 1].copy()
            self.obs = self.aug[self.aug["IS_SYNTHETIC"] == 0].copy()
        else:
            self.syn = self.aug.copy()
            self.obs = self.aug.iloc[0:0].copy()
        print(f"    Augmented rows: {len(self.aug):,} | "
              f"observed: {len(self.obs):,} | synthetic: {len(self.syn):,}")

        # Training log
        log_path = os.path.join(self.step4_dir, "step4_training_log.csv")
        self.train_log = pd.read_csv(log_path) if os.path.exists(log_path) else None

        # Feature config (optional)
        cfg_path = os.path.join(self.step4_dir, "step4_feature_config.json")
        self.feat_cfg = None
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    self.feat_cfg = json.load(f)
            except Exception:
                self.feat_cfg = None

        # Step-3 reference marginals (optional; for sanity overlay)
        def _try(name):
            p = os.path.join(self.step3_dir, name)
            if os.path.exists(p):
                try:
                    return pd.read_csv(p, low_memory=False)
                except Exception:
                    return None
            return None
        print("  Loading Step-3 reference marginals (optional)...")
        self.ref_hetus = _try("hetus_30min.csv")
        self.ref_cop = _try("copresence_30min.csv")
        self.ref_work = _try("work_30min.csv")

        self.cycles = (sorted(int(c) for c in self.aug["CYCLE_YEAR"].dropna().unique())
                       if "CYCLE_YEAR" in self.aug.columns else CYCLES)

    # ── recorder ──────────────────────────────────────────────────────────────

    def _rec(self, level: str, gate: str, msg: str) -> None:
        line = f"{gate} | {msg}"
        self.results[level].append(line)
        icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[level]
        print(f"  [{icon}] {line}")

    def _grade(self, value, pass_thr, warn_thr, direction="lower"):
        """Return 'pass'/'warn'/'fail' for a value against thresholds.
        Robust to NaN -> 'fail'."""
        try:
            if value is None or (isinstance(value, float) and np.isnan(value)):
                return "fail"
            if direction == "lower":
                if value <= pass_thr:
                    return "pass"
                if value <= warn_thr:
                    return "warn"
                return "fail"
            else:  # higher better
                if value >= pass_thr:
                    return "pass"
                if value >= warn_thr:
                    return "warn"
                return "fail"
        except Exception:
            return "fail"

    # ── Section 1: Training health ─────────────────────────────────────────────

    def validate_training_health(self):
        print("\n--- Section 1: Training health ---")
        _apply_dark()
        log = self.train_log
        if log is None or len(log) == 0:
            self._rec("warn", "1.0", "step4_training_log.csv not found -- Section 1 skipped")
            return

        n = len(log)
        # 1.1 No NaN/Inf in train loss
        if "train_loss" in log.columns:
            bad = int(log["train_loss"].isna().sum()
                      + np.isinf(log["train_loss"].to_numpy(dtype=float)).sum())
            self._rec("pass" if bad == 0 else "fail", "1.1",
                      f"NaN/Inf in train_loss: {bad}")
        # 1.2 train loss decreasing in first 10 epochs
        if "train_loss" in log.columns:
            first = log.head(min(10, n))["train_loss"].to_numpy(dtype=float)
            mono = all(first[i] >= first[i + 1] for i in range(len(first) - 1)) if len(first) > 1 else True
            self._rec("pass" if mono else "warn", "1.2",
                      f"train_loss non-increasing over first {len(first)} epochs: {mono}")
        # 1.3 val_js best epoch
        if "val_js" in log.columns:
            best_ep = int(log["val_js"].idxmin()) + 1
            best_js = float(log["val_js"].min())
            self._rec("pass", "1.3",
                      f"best val_js={best_js:.4f} @ epoch {best_ep}/{n}")

        # Chart 1a: component losses
        fig, axes = plt.subplots(1, 3, figsize=(18, 4.5))
        fig.suptitle("Section 1 -- Training Health", color="#cdd6f4",
                     fontsize=13, fontweight="bold")
        x = log["epoch"] if "epoch" in log.columns else np.arange(1, n + 1)
        ax = axes[0]
        comp_map = [("train_loss", "total", "-"), ("act_loss", "act", "--"),
                    ("home_loss", "home", ":"), ("work_loss", "work", "-."),
                    ("cop_loss", "cop", (0, (3, 1, 1, 1))), ("div_loss", "div", (0, (1, 1)))]
        for col, lbl, ls in comp_map:
            if col in log.columns:
                ax.plot(x, log[col], label=lbl, linestyle=ls, linewidth=1.6)
        ax.set_title("Component losses"); ax.set_xlabel("Epoch")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[1]
        for col, color in [("val_js", "#f38ba8"), ("home_gap", "#89b4fa"),
                           ("work_gap", "#fab387")]:
            if col in log.columns:
                ax.plot(x, log[col], label=col, color=color, linewidth=1.8)
        ax.set_title("Validation metrics"); ax.set_xlabel("Epoch")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[2]
        for col, color in [("sigma_act", "#89b4fa"), ("sigma_home", "#a6e3a1"),
                           ("sigma_work", "#fab387"), ("sigma_cop", "#f38ba8")]:
            if col in log.columns:
                ax.plot(x, log[col], label=col, color=color, linewidth=1.6)
        if "grad_norm" in log.columns:
            ax2 = ax.twinx()
            ax2.plot(x, log["grad_norm"], color="#cba6f7", linewidth=1.0,
                     alpha=0.6, label="grad_norm")
            ax2.set_ylabel("grad_norm", color="#cba6f7")
        ax.set_title("Per-task sigma weights"); ax.set_xlabel("Epoch")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["1_training"] = _b64(fig)

    # ── Section 2: Activity JS heatmap (G1) ────────────────────────────────────

    def validate_activity_js(self):
        print("\n--- Section 2: Activity JS (G1) ---")
        _apply_dark()
        cyc = self.cycles
        js_matrix = np.full((len(cyc), 3), np.nan)
        for ci, cy in enumerate(cyc):
            for si, s in enumerate([1, 2, 3]):
                obs_sub = self.obs[(self.obs.get("CYCLE_YEAR") == cy)
                                   & (self.obs.get("DDAY_STRATA") == s)]
                syn_sub = self.syn[(self.syn.get("CYCLE_YEAR") == cy)
                                   & (self.syn.get("DDAY_STRATA") == s)]
                if len(obs_sub) == 0 or len(syn_sub) == 0:
                    continue
                v = js_div(activity_dist(obs_sub), activity_dist(syn_sub))
                js_matrix[ci, si] = v
                level = self._grade(v, self.thr["g1_js_pass"], self.thr["g1_js_warn"])
                self._rec(level, "G1",
                          f"Activity JS {cy} x {STRATA_LABELS[s]}: {v:.4f}")

        finite = js_matrix[np.isfinite(js_matrix)]
        overall = float(np.mean(finite)) if finite.size else float("nan")
        lvl = self._grade(overall, self.thr["g1_overall"], self.thr["g1_js_warn"])
        self._rec(lvl, "G1", f"Overall mean Activity JS: {overall:.4f}")

        # Heatmap
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        disp = np.nan_to_num(js_matrix, nan=0.0)
        vmax = max(0.10, self.thr["g1_js_warn"])
        im = ax.imshow(disp, vmin=0, vmax=vmax, cmap="RdYlGn_r", aspect="auto")
        ax.set_xticks(range(3)); ax.set_xticklabels(["Weekday", "Saturday", "Sunday"])
        ax.set_yticks(range(len(cyc))); ax.set_yticklabels([str(c) for c in cyc])
        ax.set_title("Activity JS Divergence (cycle x stratum)", color="#cdd6f4")
        for ci in range(len(cyc)):
            for si in range(3):
                txt = "n/a" if not np.isfinite(js_matrix[ci, si]) else f"{js_matrix[ci, si]:.3f}"
                ax.text(si, ci, txt, ha="center", va="center", fontsize=8, color="black")
        plt.colorbar(im, ax=ax, label="JS")
        plt.tight_layout()
        self.plots_b64["2_js_heatmap"] = _b64(fig)

        # Activity distribution bars per stratum
        fig2, axes = plt.subplots(1, 3, figsize=(18, 4.5))
        fig2.suptitle("Section 2 -- Activity Distribution (observed vs synthetic)",
                      color="#cdd6f4", fontsize=13)
        for ax, (s, lbl) in zip(axes, STRATA_LABELS.items()):
            obs_s = self.obs[self.obs.get("DDAY_STRATA") == s]
            syn_s = self.syn[self.syn.get("DDAY_STRATA") == s]
            p_obs = activity_dist(obs_s); p_syn = activity_dist(syn_s)
            x = np.arange(1, N_ACT + 1); w = 0.4
            ax.bar(x - w / 2, p_obs * 100, width=w, label="Observed", color="#89b4fa", alpha=0.85)
            ax.bar(x + w / 2, p_syn * 100, width=w, label="Synthetic", color="#fab387", alpha=0.85)
            ax.set_title(lbl); ax.set_xlabel("Activity"); ax.set_ylabel("%")
            ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["2_act_dist"] = _b64(fig2)

    # ── Section 3: AT_HOME marginals + rhythm (G2) ─────────────────────────────

    def validate_at_home(self):
        print("\n--- Section 3: AT_HOME (G2) ---")
        _apply_dark()
        hom_obs = present_cols(self.obs, "hom30")
        hom_syn = present_cols(self.syn, "hom30")
        if not hom_syn:
            self._rec("fail", "G2", "hom30_* columns missing in synthetic rows")
            return

        for cy in self.cycles:
            for s in [1, 2, 3]:
                osub = self.obs[(self.obs.get("CYCLE_YEAR") == cy) & (self.obs.get("DDAY_STRATA") == s)]
                ssub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                if len(osub) == 0 or len(ssub) == 0:
                    continue
                r_obs = np.nanmean(osub[hom_obs].to_numpy(dtype=float)) * 100
                r_syn = np.nanmean(ssub[hom_syn].to_numpy(dtype=float)) * 100
                delta = abs(r_obs - r_syn)
                level = self._grade(delta, self.thr["g2_home_pass"], self.thr["g2_home_warn"])
                self._rec(level, "G2",
                          f"|dAT_HOME| {cy} x {STRATA_LABELS[s]}: {delta:.2f} pp "
                          f"(obs {r_obs:.1f}% / syn {r_syn:.1f}%)")

        # Daily rhythm chart per stratum
        fig, axes = plt.subplots(1, 3, figsize=(18, 4))
        fig.suptitle("Section 3 -- AT_HOME Daily Rhythm (observed vs synthetic)",
                     color="#cdd6f4", fontsize=13)
        x = np.arange(N_SLOTS)
        for ax, (s, lbl) in zip(axes, STRATA_LABELS.items()):
            osub = self.obs[self.obs.get("DDAY_STRATA") == s]
            ssub = self.syn[self.syn.get("DDAY_STRATA") == s]
            if len(osub) and hom_obs:
                ax.plot(x, np.nanmean(osub[hom_obs].to_numpy(dtype=float), axis=0) * 100,
                        label="Observed", lw=2, color="#89b4fa")
            if len(ssub) and hom_syn:
                ax.plot(x, np.nanmean(ssub[hom_syn].to_numpy(dtype=float), axis=0) * 100,
                        label="Synthetic", lw=2, ls="--", color="#fab387")
            ax.set_title(lbl); ax.set_xlabel("Slot (30-min, 04:00 origin)")
            ax.set_ylabel("AT_HOME %"); ax.set_ylim(0, 100); ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["3_at_home_rhythm"] = _b64(fig)

    # ── Section 4: Activity temporal (G4) ──────────────────────────────────────

    def validate_temporal(self):
        print("\n--- Section 4: Activity temporal (G4) ---")
        _apply_dark()
        act_obs = present_cols(self.obs, "act30")
        act_syn = present_cols(self.syn, "act30")
        if not act_syn:
            self._rec("fail", "G4", "act30_* columns missing in synthetic rows")
            return

        def n_trans(arr):
            arr = np.asarray(arr, dtype=float)
            return np.array([np.sum(r[:-1] != r[1:]) for r in arr])

        obs_arr = self.obs[act_obs].to_numpy(dtype=float) if (len(self.obs) and act_obs) else np.zeros((0, N_SLOTS))
        syn_arr = self.syn[act_syn].to_numpy(dtype=float)

        if obs_arr.shape[0] > 0:
            obs_t = n_trans(obs_arr).mean()
            syn_t = n_trans(syn_arr).mean()
            ratio_dev = abs(syn_t / max(obs_t, 1e-6) - 1.0) * 100
            lvl = self._grade(ratio_dev, self.thr["g4_trans_pass"], self.thr["g4_trans_warn"])
            self._rec(lvl, "G4",
                      f"Transition-rate dev syn/obs: {ratio_dev:.1f}% "
                      f"(obs {obs_t:.2f} / syn {syn_t:.2f} transitions/day)")
        else:
            self._rec("warn", "G4", "no observed rows for transition-rate gate")

        # Sleep slot delta (raw cat 5) on night slots
        def slot_rate(arr, slots, cat):
            if arr.shape[0] == 0:
                return float("nan")
            idx = [i for i in slots if i < arr.shape[1]]
            return float(np.nanmean(arr[:, idx] == cat)) * 100

        if obs_arr.shape[0] > 0:
            d_sleep = abs(slot_rate(obs_arr, SLEEP_NIGHT_SLOTS, RAW_SLEEP_CAT)
                          - slot_rate(syn_arr, SLEEP_NIGHT_SLOTS, RAW_SLEEP_CAT))
            lvl = self._grade(d_sleep, self.thr["g4_slot_pp_pass"], self.thr["g4_slot_pp_warn"])
            self._rec(lvl, "G4", f"Night sleep-slot delta: {d_sleep:.2f} pp")

            d_work = abs(slot_rate(obs_arr, WORK_PEAK_SLOTS, RAW_WORK_CAT)
                         - slot_rate(syn_arr, WORK_PEAK_SLOTS, RAW_WORK_CAT))
            lvl = self._grade(d_work, self.thr["g4_slot_pp_pass"], self.thr["g4_slot_pp_warn"])
            self._rec(lvl, "G4", f"Work peak-slot delta: {d_work:.2f} pp")

        # Heatmaps obs vs syn (weekday)
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        fig.suptitle("Section 4 -- Activity Heatmap (Weekday: observed vs synthetic)",
                     color="#cdd6f4", fontsize=13)
        owd = self.obs[self.obs.get("DDAY_STRATA") == 1][act_obs].to_numpy(dtype=float) if (len(self.obs) and act_obs) else np.zeros((0, N_SLOTS))
        swd = self.syn[self.syn.get("DDAY_STRATA") == 1][act_syn].to_numpy(dtype=float)
        for ax, arr, title in zip(axes, [owd, swd], ["Observed", "Synthetic"]):
            hmap = np.zeros((N_ACT, N_SLOTS))
            if arr.shape[0] > 0:
                for cat in range(1, N_ACT + 1):
                    hmap[cat - 1] = np.nanmean(arr == cat, axis=0) * 100
            im = ax.imshow(hmap, aspect="auto", cmap="plasma", vmin=0, vmax=80)
            ax.set_title(title); ax.set_xlabel("Slot (30-min, 04:00 origin)")
            ax.set_yticks(range(N_ACT))
            ax.set_yticklabels([ACT_LABELS[i + 1] for i in range(N_ACT)], fontsize=7)
            plt.colorbar(im, ax=ax, label="% respondents")
        plt.tight_layout()
        self.plots_b64["4_act_heatmap"] = _b64(fig)

    # ── Section 5: Co-presence prevalence (G3) ─────────────────────────────────

    def validate_copresence(self):
        print("\n--- Section 5: Co-presence prevalence (G3) ---")
        _apply_dark()
        prev_obs, prev_syn, gaps = {}, {}, {}
        for cn in COP_COLS:
            ocols = cop_cols(self.obs, cn)
            scols = cop_cols(self.syn, cn)
            if not scols:
                continue
            if len(self.obs) and ocols:
                ov = self.obs[ocols].to_numpy(dtype=float)
                prev_obs[cn] = np.nanmean(ov == 1) * 100
            else:
                prev_obs[cn] = float("nan")
            sv = self.syn[scols].to_numpy(dtype=float)
            prev_syn[cn] = np.nanmean(sv >= 0.5) * 100
            if not np.isnan(prev_obs[cn]):
                gaps[cn] = abs(prev_obs[cn] - prev_syn[cn])

        if gaps:
            max_gap = max(gaps.values())
            worst = max(gaps, key=gaps.get)
            lvl = self._grade(max_gap, self.thr["g3_cop_pass"], self.thr["g3_cop_warn"])
            self._rec(lvl, "G3",
                      f"Max per-channel prevalence gap: {max_gap:.2f} pp (worst: {worst})")
            for cn, g in gaps.items():
                lvl = self._grade(g, self.thr["g3_cop_pass"], self.thr["g3_cop_warn"])
                self._rec(lvl, "G3",
                          f"|dprev| {cn}: {g:.2f} pp "
                          f"(obs {prev_obs[cn]:.1f}% / syn {prev_syn[cn]:.1f}%)")
        else:
            self._rec("warn", "G3", "no comparable co-presence channels (NaN-aware)")

        # Chart
        names = [cn for cn in COP_COLS if cn in prev_syn]
        if names:
            fig, ax = plt.subplots(figsize=(12, 4))
            x = np.arange(len(names)); w = 0.4
            ax.bar(x - w / 2, [prev_obs.get(cn, np.nan) for cn in names], width=w,
                   label="Observed", color="#89b4fa", alpha=0.85)
            ax.bar(x + w / 2, [prev_syn.get(cn, np.nan) for cn in names], width=w,
                   label="Synthetic", color="#fab387", alpha=0.85)
            ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right")
            ax.set_title("Section 5 -- Co-Presence Prevalence (observed vs synthetic)",
                         color="#cdd6f4")
            ax.set_ylabel("% slots present"); ax.legend(fontsize=9); ax.grid(alpha=0.3)
            plt.tight_layout()
            self.plots_b64["5_cop_prev"] = _b64(fig)

    # ── Section 6: AT_WORK marginals + diurnal (OW1/OW2/OW3) [NEW] ─────────────

    def _wrk_curve(self, df, cy=None, s=None):
        """Mean 48-slot AT_WORK curve (%) for a (cycle, stratum) subset."""
        wcols = present_cols(df, "wrk30")
        if not wcols:
            return None
        sub = df
        if cy is not None and "CYCLE_YEAR" in df.columns:
            sub = sub[sub["CYCLE_YEAR"] == cy]
        if s is not None and "DDAY_STRATA" in df.columns:
            sub = sub[sub["DDAY_STRATA"] == s]
        if len(sub) == 0:
            return None
        return np.nanmean(sub[wcols].to_numpy(dtype=float), axis=0) * 100

    def validate_at_work_marginals(self):
        print("\n--- Section 6: AT_WORK marginals + diurnal (OW1/OW2/OW3) [NEW] ---")
        _apply_dark()
        wrk_syn = present_cols(self.syn, "wrk30")
        if not wrk_syn:
            self._rec("fail", "OW1", "wrk30_* columns missing in synthetic rows -- office gates skipped")
            return False
        wrk_obs = present_cols(self.obs, "wrk30")

        # OW1: presence RMS per (cycle x stratum)
        for cy in self.cycles:
            for s in [1, 2, 3]:
                osub = self.obs[(self.obs.get("CYCLE_YEAR") == cy) & (self.obs.get("DDAY_STRATA") == s)]
                ssub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                if len(ssub) == 0:
                    continue
                r_syn = np.nanmean(ssub[wrk_syn].to_numpy(dtype=float)) * 100
                if len(osub) and wrk_obs:
                    r_obs = np.nanmean(osub[wrk_obs].to_numpy(dtype=float)) * 100
                else:
                    r_obs = float("nan")
                if np.isnan(r_obs):
                    self._rec("warn", "OW1",
                              f"AT_WORK rate {cy} x {STRATA_LABELS[s]}: syn {r_syn:.2f}% (no observed ref)")
                    continue
                delta = abs(r_obs - r_syn)
                lvl = self._grade(delta, self.thr["ow1_pass"], self.thr["ow1_warn"])
                self._rec(lvl, "OW1",
                          f"AT_WORK presence RMS {cy} x {STRATA_LABELS[s]}: {delta:.2f} pp "
                          f"(obs {r_obs:.1f}% / syn {r_syn:.1f}%)")

        # OW2 + OW3 on weekday (stratum 1) aggregate curve
        obs_wd = self._wrk_curve(self.obs, s=1)
        syn_wd = self._wrk_curve(self.syn, s=1)
        if obs_wd is not None and syn_wd is not None:
            if _HAVE_SCIPY and np.std(obs_wd) > 0 and np.std(syn_wd) > 0:
                r = float(pearsonr(obs_wd, syn_wd)[0])
            elif np.std(obs_wd) > 0 and np.std(syn_wd) > 0:
                r = float(np.corrcoef(obs_wd, syn_wd)[0, 1])
            else:
                r = 0.0
            lvl = self._grade(r, self.thr["ow2_pass"], self.thr["ow2_warn"], direction="higher")
            self._rec(lvl, "OW2", f"Diurnal-shape Pearson r (weekday): {r:.3f}")

            shift = int(abs(int(np.argmax(syn_wd)) - int(np.argmax(obs_wd))))
            lvl = self._grade(shift, self.thr["ow3_pass"], self.thr["ow3_warn"])
            self._rec(lvl, "OW3", f"Peak-timing shift (weekday): {shift} slots "
                                  f"(obs argmax {int(np.argmax(obs_wd))}, syn {int(np.argmax(syn_wd))})")
        else:
            self._rec("warn", "OW2", "weekday AT_WORK curves unavailable (need obs+syn) -- OW2/OW3 skipped")

        # HEADLINE: 4-cycle x 3-stratum mean AT_WORK curves obs vs syn
        x = np.arange(N_SLOTS)
        slot_lbls = []
        for i in range(N_SLOTS):
            tm = 4 * 60 + i * 30
            hh = (tm // 60) % 24; mm = tm % 60
            slot_lbls.append(f"{hh:02d}:{mm:02d}" if mm == 0 else "")
        fig, axes = plt.subplots(len(self.cycles), 3, figsize=(20, 4 * len(self.cycles)),
                                 squeeze=False, sharex=True)
        fig.suptitle("Section 6 (Leg-2 Headline) -- Mean AT_WORK Diurnal Curves "
                     "(cycle x stratum; observed vs synthetic)",
                     color="#cdd6f4", fontsize=14, fontweight="bold")
        for ci, cy in enumerate(self.cycles):
            for si, s in enumerate([1, 2, 3]):
                ax = axes[ci][si]
                oc = self._wrk_curve(self.obs, cy=cy, s=s)
                sc = self._wrk_curve(self.syn, cy=cy, s=s)
                if oc is not None:
                    ax.plot(x, oc, label="Observed", lw=1.8, color="#89b4fa")
                if sc is not None:
                    ax.plot(x, sc, label="Synthetic", lw=1.8, ls="--", color="#fab387")
                ax.set_title(f"{cy} - {STRATA_LABELS[s]}", fontsize=10)
                ax.grid(alpha=0.3); ax.set_ylim(0, None)
                if si == 0:
                    ax.set_ylabel("AT_WORK %")
                if ci == len(self.cycles) - 1:
                    ax.set_xticks(range(0, N_SLOTS, 4))
                    ax.set_xticklabels([slot_lbls[i] for i in range(0, N_SLOTS, 4)],
                                       rotation=45, fontsize=7)
                if ci == 0 and si == 2:
                    ax.legend(fontsize=8)
        plt.tight_layout()
        self.plots_b64["6_atwork_diurnal"] = _b64(fig)
        return True

    # ── Section 7: AT_WORK sanity (OW4/OW5/OW6) [NEW] ──────────────────────────

    def validate_at_work_sanity(self):
        print("\n--- Section 7: AT_WORK sanity (OW4/OW5/OW6) [NEW] ---")
        _apply_dark()
        wrk_syn = present_cols(self.syn, "wrk30")
        if not wrk_syn:
            self._rec("fail", "OW4", "wrk30_* columns missing -- OW4/OW5/OW6 skipped")
            return

        syn_arr = self.syn[wrk_syn].to_numpy(dtype=float)

        # OW4: night near-zero (00:00-05:00)
        night_idx = [i for i in NIGHT_SLOTS if i < syn_arr.shape[1]]
        night_rate = float(np.nanmean(syn_arr[:, night_idx])) * 100 if syn_arr.shape[0] else float("nan")
        # PASS <5%, WARN 5-8% : grade uses pass/warn thresholds (lower-is-better)
        lvl = self._grade(night_rate, self.thr["ow4_pass"], self.thr["ow4_warn"])
        self._rec(lvl, "OW4", f"Night AT_WORK rate (00:00-05:00): {night_rate:.2f}%")

        # OW5: day-type ordering weekday >= Sat >= Sun per respondent
        n_ok = n_tot = 0
        if "occID" in self.syn.columns and "DDAY_STRATA" in self.syn.columns:
            tmp = self.syn.copy()
            tmp["_wrate"] = np.nanmean(tmp[wrk_syn].to_numpy(dtype=float), axis=1)
            piv = tmp.pivot_table(index="occID", columns="DDAY_STRATA",
                                  values="_wrate", aggfunc="mean")
            have = [s for s in [1, 2, 3] if s in piv.columns]
            if set([1, 2, 3]).issubset(piv.columns):
                sub = piv.dropna(subset=[1, 2, 3])
                n_tot = len(sub)
                n_ok = int(((sub[1] >= sub[2]) & (sub[2] >= sub[3])).sum())
        pct_order = (n_ok / n_tot * 100) if n_tot else float("nan")
        if n_tot:
            lvl = self._grade(pct_order, self.thr["ow5_pass"], self.thr["ow5_warn"], direction="higher")
            self._rec(lvl, "OW5",
                      f"Day-type ordering wkdy>=Sat>=Sun: {pct_order:.1f}% of {n_tot} respondents")
        else:
            self._rec("warn", "OW5",
                      "Day-type ordering: insufficient per-respondent strata coverage")

        # OW6: channel exclusivity hom30==1 AND wrk30==1
        hom_syn = present_cols(self.syn, "hom30")
        if hom_syn:
            # align columns by slot index
            common = [i for i in range(1, N_SLOTS + 1)
                      if f"hom30_{i:03d}" in self.syn.columns and f"wrk30_{i:03d}" in self.syn.columns]
            hcols = [f"hom30_{i:03d}" for i in common]
            wcols = [f"wrk30_{i:03d}" for i in common]
            harr = self.syn[hcols].to_numpy(dtype=float)
            warr = self.syn[wcols].to_numpy(dtype=float)
            total = harr.size
            both = int(np.nansum((harr == 1) & (warr == 1)))
            pct_both = (both / total * 100) if total else float("nan")
            lvl = self._grade(pct_both, self.thr["ow6_pass"], self.thr["ow6_warn"])
            self._rec(lvl, "OW6",
                      f"Channel exclusivity hom30=1 AND wrk30=1: {both:,} cells ({pct_both:.3f}%)")
        else:
            self._rec("warn", "OW6", "hom30_* columns missing -- OW6 skipped")

        # Chart: AT_WORK rate per cycle x stratum (synthetic) + night marker
        fig, ax = plt.subplots(figsize=(11, 4.5))
        fig.suptitle("Section 7 -- Synthetic AT_WORK Rate by Cycle x Stratum",
                     color="#cdd6f4", fontsize=12)
        x = np.arange(len(self.cycles)); w = 0.25
        for si, s in enumerate([1, 2, 3]):
            vals = []
            for cy in self.cycles:
                ssub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                vals.append(np.nanmean(ssub[wrk_syn].to_numpy(dtype=float)) * 100 if len(ssub) else 0.0)
            ax.bar(x + (si - 1) * w, vals, w, label=STRATA_LABELS[s],
                   color=STRATA_COLORS[s], edgecolor="#1e1e2e")
        ax.set_xticks(x); ax.set_xticklabels([str(c) for c in self.cycles])
        ax.set_ylabel("Mean AT_WORK rate (%)"); ax.legend(fontsize=9); ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["7_atwork_rate"] = _b64(fig)

    # ── Section 8: Secondary distributional (not gated) ────────────────────────

    def validate_secondary(self):
        print("\n--- Section 8: Secondary distributional (reported, not gated) ---")
        _apply_dark()
        lines = []

        def channel_metrics(name, prefix):
            ocols = present_cols(self.obs, prefix)
            scols = present_cols(self.syn, prefix)
            if not scols:
                return
            # daily presence count distributions (per respondent)
            sarr = self.syn[scols].to_numpy(dtype=float)
            s_daily = np.nansum(sarr == 1, axis=1).astype(float)
            if len(self.obs) and ocols:
                oarr = self.obs[ocols].to_numpy(dtype=float)
                o_daily = np.nansum(oarr == 1, axis=1).astype(float)
            else:
                o_daily = None

            # EMD on daily-presence (1-Wasserstein)
            if o_daily is not None and _HAVE_SCIPY and o_daily.size and s_daily.size:
                emd = float(wasserstein_distance(o_daily, s_daily))
                lines.append(f"[{name}] EMD(daily-presence-count): {emd:.3f} slots")
            # KS dwell/daily
            if o_daily is not None and _HAVE_SCIPY and o_daily.size and s_daily.size:
                ks = float(ks_2samp(o_daily, s_daily).statistic)
                lines.append(f"[{name}] KS(daily-presence-count): {ks:.3f}")
            # transition-matrix MAE on the 48-slot mean curve
            if o_daily is not None and ocols:
                o_curve = np.nanmean(oarr == 1, axis=0)
                s_curve = np.nanmean(sarr == 1, axis=0)
                lines.append(f"[{name}] mean-curve MAE: {np.mean(np.abs(o_curve - s_curve)) * 100:.2f} pp")
                # ACF MAE lags 1..min(24,47)
                def acf(c, lag):
                    c = c - c.mean()
                    denom = np.sum(c * c) + 1e-12
                    return np.sum(c[:-lag] * c[lag:]) / denom
                lags = range(1, min(24, N_SLOTS - 1) + 1)
                acf_mae = np.mean([abs(acf(o_curve, L) - acf(s_curve, L)) for L in lags])
                lines.append(f"[{name}] ACF-MAE (lags 1-24): {acf_mae:.4f}")

            # Mean state transitions per day (detects flickering/chatter)
            s_trans = np.nansum(sarr[:, :-1] != sarr[:, 1:], axis=1).mean()
            if len(self.obs) and ocols:
                o_trans = np.nansum(oarr[:, :-1] != oarr[:, 1:], axis=1).mean()
                lines.append(f"[{name}] transitions/day: obs {o_trans:.3f} / syn {s_trans:.3f}")
            else:
                lines.append(f"[{name}] transitions/day: syn {s_trans:.3f}")

        channel_metrics("AT_HOME", "hom30")
        channel_metrics("AT_WORK", "wrk30")

        # Activity vs occupancy discordance (semantic consistency checks)
        act_obs = present_cols(self.obs, "act30")
        act_syn = present_cols(self.syn, "act30")
        hom_obs = present_cols(self.obs, "hom30")
        hom_syn = present_cols(self.syn, "hom30")
        wrk_obs = present_cols(self.obs, "wrk30")
        wrk_syn = present_cols(self.syn, "wrk30")

        if act_syn and wrk_syn:
            s_act = self.syn[act_syn].to_numpy(dtype=float)
            s_wrk = self.syn[wrk_syn].to_numpy(dtype=float)
            s_wact_mask = (s_act == 1)
            s_wviol = np.sum(s_wact_mask & (s_wrk == 0))
            s_wact_tot = np.sum(s_wact_mask)
            s_wrate = (s_wviol / s_wact_tot * 100) if s_wact_tot > 0 else 0.0
            if len(self.obs) and act_obs and wrk_obs:
                o_act = self.obs[act_obs].to_numpy(dtype=float)
                o_wrk = self.obs[wrk_obs].to_numpy(dtype=float)
                o_wact_mask = (o_act == 1)
                o_wviol = np.sum(o_wact_mask & (o_wrk == 0))
                o_wact_tot = np.sum(o_wact_mask)
                o_wrate = (o_wviol / o_wact_tot * 100) if o_wact_tot > 0 else 0.0
                lines.append(f"[Semantic] Work activity but AT_WORK=0: obs {o_wrate:.1f}% / syn {s_wrate:.1f}%")
            else:
                lines.append(f"[Semantic] Work activity but AT_WORK=0: syn {s_wrate:.1f}%")

        if act_syn and hom_syn:
            s_act = self.syn[act_syn].to_numpy(dtype=float)
            s_hom = self.syn[hom_syn].to_numpy(dtype=float)
            s_sact_mask = (s_act == 5)
            s_sviol = np.sum(s_sact_mask & (s_hom == 0))
            s_sact_tot = np.sum(s_sact_mask)
            s_srate = (s_sviol / s_sact_tot * 100) if s_sact_tot > 0 else 0.0
            if len(self.obs) and act_obs and hom_obs:
                o_act = self.obs[act_obs].to_numpy(dtype=float)
                o_hom = self.obs[hom_obs].to_numpy(dtype=float)
                o_sact_mask = (o_act == 5)
                o_sviol = np.sum(o_sact_mask & (o_hom == 0))
                o_sact_tot = np.sum(o_sact_mask)
                o_srate = (o_sviol / o_sact_tot * 100) if o_sact_tot > 0 else 0.0
                lines.append(f"[Semantic] Sleep activity but AT_HOME=0: obs {o_srate:.1f}% / syn {s_srate:.1f}%")
            else:
                lines.append(f"[Semantic] Sleep activity but AT_HOME=0: syn {s_srate:.1f}%")

        # Activity KL (obs||syn) overall
        if len(self.obs):
            p = activity_dist(self.obs); q = activity_dist(self.syn)
            p = np.clip(p, 1e-12, None); q = np.clip(q, 1e-12, None)
            kl = float(np.sum(p * np.log(p / q)))
            lines.append(f"[Activity] KL(obs||syn) 14-cat: {kl:.4f}")

        for ln in lines:
            self._rec("pass", "S8", ln)
        if not lines:
            self._rec("warn", "S8", "no secondary metrics computable")

    # ── Section 9 (summary table) ──────────────────────────────────────────────

    def build_summary_table(self):
        hom = present_cols(self.aug, "hom30")
        wrk = present_cols(self.aug, "wrk30")
        rows = []
        for cy in self.cycles:
            ocy = self.obs[self.obs.get("CYCLE_YEAR") == cy]
            scy = self.syn[self.syn.get("CYCLE_YEAR") == cy]
            mean_js = np.nanmean([
                js_div(activity_dist(ocy[ocy.get("DDAY_STRATA") == s]),
                       activity_dist(scy[scy.get("DDAY_STRATA") == s]))
                for s in [1, 2, 3]
                if len(ocy[ocy.get("DDAY_STRATA") == s]) and len(scy[scy.get("DDAY_STRATA") == s])
            ]) if len(scy) and len(ocy) else float("nan")
            o_home = np.nanmean(ocy[hom].to_numpy(dtype=float)) * 100 if (len(ocy) and hom) else float("nan")
            s_home = np.nanmean(scy[present_cols(scy, "hom30")].to_numpy(dtype=float)) * 100 if (len(scy) and present_cols(scy, "hom30")) else float("nan")
            s_work = np.nanmean(scy[present_cols(scy, "wrk30")].to_numpy(dtype=float)) * 100 if (len(scy) and present_cols(scy, "wrk30")) else float("nan")
            rows.append({
                "Cycle": str(cy),
                "Observed": f"{len(ocy):,}",
                "Synthetic": f"{len(scy):,}",
                "Mean JS": f"{mean_js:.4f}" if not np.isnan(mean_js) else "n/a",
                "AT_HOME obs%": f"{o_home:.1f}" if not np.isnan(o_home) else "n/a",
                "AT_HOME syn%": f"{s_home:.1f}" if not np.isnan(s_home) else "n/a",
                "AT_WORK syn%": f"{s_work:.1f}" if not np.isnan(s_work) else "n/a",
            })
        rows.append({
            "Cycle": "Total", "Observed": f"{len(self.obs):,}",
            "Synthetic": f"{len(self.syn):,}", "Mean JS": "--",
            "AT_HOME obs%": "--", "AT_HOME syn%": "--", "AT_WORK syn%": "--",
        })
        self.summary_rows = rows

    # ── HTML + TXT report ─────────────────────────────────────────────────────

    def build_report(self):
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mode = "SAMPLE (relaxed)" if self.sample_mode else "PRODUCTION"

        chart_order = [
            ("1_training", "Section 1 -- Training Health"),
            ("2_js_heatmap", "Section 2 -- Activity JS Heatmap (G1)"),
            ("2_act_dist", "Section 2 -- Activity Distribution by Stratum (G1)"),
            ("3_at_home_rhythm", "Section 3 -- AT_HOME Daily Rhythm (G2)"),
            ("4_act_heatmap", "Section 4 -- Activity Temporal Heatmap (G4)"),
            ("5_cop_prev", "Section 5 -- Co-Presence Prevalence (G3)"),
            ("6_atwork_diurnal", "Section 6 -- AT_WORK Diurnal Curves [Leg-2 Headline] (OW1/OW2/OW3)"),
            ("7_atwork_rate", "Section 7 -- AT_WORK Sanity (OW4/OW5/OW6)"),
        ]
        charts_html = ""
        for key, label in chart_order:
            if key in self.plots_b64:
                charts_html += f"""
        <section class="chart-section" id="{key}">
          <h2>{label}</h2>
          <div class="chart-wrap">
            <img src="data:image/png;base64,{self.plots_b64[key]}" alt="{label}">
          </div>
        </section>"""

        # summary table
        if self.summary_rows:
            cols = list(self.summary_rows[0].keys())
            th = "".join(f"<th>{c}</th>" for c in cols)
            trs = ""
            for r in self.summary_rows:
                cls = ' class="total-row"' if r["Cycle"] == "Total" else ""
                trs += "<tr%s>%s</tr>" % (cls, "".join(f"<td>{r[c]}</td>" for c in cols))
            summary_html = f"""
        <section class="chart-section" id="summary-table">
          <h2>Section 9 -- Scorecard Summary Table</h2>
          <div class="table-wrap">
            <table class="summary-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>
          </div>
        </section>"""
        else:
            summary_html = ""

        def _badge_list(level):
            icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[level]
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>" for m in items)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Step 4 (Leg-2) -- Augmentation Validation</title>
  <style>
    :root {{
      --bg:#1e1e2e; --surface:#2a2a3e; --surface2:#313244;
      --accent:#89b4fa; --green:#a6e3a1; --yellow:#f9e2af;
      --red:#f38ba8; --text:#cdd6f4; --subtext:#a6adc8; --border:#45475a;
    }}
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg);
            color:var(--text); min-height:100vh; }}
    header {{ background:var(--surface); border-bottom:1px solid var(--border);
              padding:18px 32px; display:flex; align-items:center;
              justify-content:space-between; position:sticky; top:0; z-index:100; }}
    header h1 {{ font-size:1.25rem; color:var(--accent); }}
    header p  {{ font-size:0.8rem; color:var(--subtext); }}
    nav {{ background:var(--surface2); border-bottom:1px solid var(--border);
           padding:8px 32px; display:flex; gap:20px; flex-wrap:wrap; }}
    nav a {{ color:var(--subtext); text-decoration:none; font-size:0.82rem;
             padding:4px 10px; border-radius:6px; }}
    nav a:hover {{ background:var(--surface); color:var(--accent); }}
    main {{ max-width:1200px; margin:0 auto; padding:30px 28px; }}
    .scorecard {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:36px; }}
    .score-card {{ background:var(--surface); border:1px solid var(--border);
                   border-radius:12px; padding:20px 16px; text-align:center; }}
    .score-card .number {{ font-size:2.4rem; font-weight:700; }}
    .score-card .label  {{ font-size:0.8rem; color:var(--subtext); margin-top:4px; }}
    .score-card.ok   .number {{ color:var(--green); }}
    .score-card.warn .number {{ color:var(--yellow); }}
    .score-card.fail .number {{ color:var(--red); }}
    .score-card.pct  .number {{ color:var(--accent); font-size:2.0rem; }}
    .findings {{ margin-bottom:36px; }}
    .findings h2 {{ font-size:1.05rem; margin-bottom:12px; color:var(--accent); }}
    .badge-list {{ list-style:none; display:flex; flex-direction:column; gap:6px; }}
    .badge {{ padding:8px 14px; border-radius:8px; font-size:0.85rem; line-height:1.4; }}
    .badge.pass {{ background:#1c2e22; border:1px solid #2d5a35; color:var(--green); }}
    .badge.warn {{ background:#2e2a1c; border:1px solid #5a4e1f; color:var(--yellow); }}
    .badge.fail {{ background:#2e1c1e; border:1px solid #5a2428; color:var(--red); }}
    .chart-section {{ background:var(--surface); border:1px solid var(--border);
                      border-radius:14px; padding:24px; margin-bottom:28px; }}
    .chart-section h2 {{ font-size:1.0rem; color:var(--accent); margin-bottom:16px;
                         padding-bottom:8px; border-bottom:1px solid var(--border); }}
    .chart-wrap {{ text-align:center; }}
    .chart-wrap img {{ max-width:100%; height:auto; border-radius:8px; }}
    .table-wrap {{ overflow-x:auto; }}
    .summary-table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    .summary-table th {{ background:var(--surface2); color:var(--accent); padding:10px 12px;
                          text-align:left; border-bottom:2px solid var(--border); white-space:nowrap; }}
    .summary-table td {{ padding:8px 12px; border-bottom:1px solid var(--border);
                          color:var(--text); white-space:nowrap; }}
    .summary-table tr.total-row td {{ font-weight:700; color:var(--accent);
                                       border-top:2px solid var(--border); }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem; color:var(--subtext);
              border-top:1px solid var(--border); margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GSS Step 4 (Leg-2) -- Augmentation Validation Report</h1>
      <p>Two-channel (AT_HOME + AT_WORK) | Residential gates G1-G4, Office gates OW1-OW6
         &middot; Cycles {", ".join(str(c) for c in self.cycles)} &middot; Mode: {mode}</p>
    </div>
    <p style="font-size:0.78rem;color:var(--subtext)">Generated: {ts}</p>
  </header>
  <nav>
    <a href="#scorecard">Scorecard</a>
    {"".join(f'<a href="#{k}">{lbl.split("--")[0].strip()}</a>' for k, lbl in chart_order if k in self.plots_b64)}
    <a href="#summary-table">Section 9</a>
  </nav>
  <main>
    <div class="scorecard" id="scorecard">
      <div class="score-card ok"><div class="number">{n_pass}</div><div class="label">Checks Passed</div></div>
      <div class="score-card warn"><div class="number">{n_warn}</div><div class="label">Warnings</div></div>
      <div class="score-card fail"><div class="number">{n_fail}</div><div class="label">Failures</div></div>
      <div class="score-card pct"><div class="number">{pct_ok}%</div><div class="label">Pass Rate</div></div>
    </div>
    <div class="findings"><h2>FAILURES</h2><ul class="badge-list">{_badge_list("fail")}</ul></div>
    <div class="findings"><h2>WARNINGS</h2><ul class="badge-list">{_badge_list("warn")}</ul></div>
    <div class="findings"><h2>PASSED</h2><ul class="badge-list">{_badge_list("pass")}</ul></div>
    {charts_html}
    {summary_html}
  </main>
  <footer>
    Leg-2 Occupancy Modeling Pipeline &middot; Step 4 Augmentation Validation &middot;
    Source: {os.path.basename(self.aug_path)} &middot; Generated: {ts}
  </footer>
</body>
</html>"""

        out_html = os.path.join(self.step4_dir, "step4_validation_report.html")
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML report saved -> {out_html}")

        out_txt = os.path.join(self.step4_dir, "step4_validation_report.txt")
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(f"Step 4 (Leg-2) Augmentation Validation Report -- {ts}\n")
            f.write(f"Mode: {mode}\n")
            f.write("=" * 60 + "\n")
            f.write(f"PASS: {n_pass}  WARN: {n_warn}  FAIL: {n_fail}  ({pct_ok}% pass rate)\n")
            f.write("=" * 60 + "\n\n")
            for level, icon in [("fail", "FAIL"), ("warn", "WARN"), ("pass", "PASS")]:
                for msg in self.results[level]:
                    f.write(f"[{icon}] {msg}\n")
        print(f"TXT report saved  -> {out_txt}")
        return out_html

    # ── run all ────────────────────────────────────────────────────────────────

    def run_all(self):
        _apply_dark()
        print("=" * 60)
        print(f"Step 4 (Leg-2) -- Augmentation Validation  "
              f"{'[SAMPLE MODE]' if self.sample_mode else ''}")
        print("=" * 60)

        def _safe(fn, name):
            try:
                fn()
            except Exception as e:
                self._rec("fail", name, f"section crashed: {type(e).__name__}: {e}")

        _safe(self.validate_training_health, "1.x")
        _safe(self.validate_activity_js, "G1")
        _safe(self.validate_at_home, "G2")
        _safe(self.validate_temporal, "G4")
        _safe(self.validate_copresence, "G3")
        _safe(self.validate_at_work_marginals, "OW1")
        _safe(self.validate_at_work_sanity, "OW4")
        _safe(self.validate_secondary, "S8")
        _safe(self.build_summary_table, "9")
        self.build_report()

        n_p = len(self.results["pass"])
        n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 60}")
        print(f"Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 60}")


def parse_args():
    p = argparse.ArgumentParser(description="Step 4 (Leg-2) augmentation validator")
    p.add_argument("--step3_dir", default=None, help="Step-3 reference outputs dir")
    p.add_argument("--step4_dir", default=None, help="Step-4 artifacts dir")
    p.add_argument("--sample", action="store_true",
                   help="Relaxed thresholds for an undertrained smoke-test model")
    return p.parse_args()


def main():
    args = parse_args()
    step3_dir = args.step3_dir or STEP3_DIR_DEFAULT
    step4_dir = args.step4_dir or STEP4_DIR_DEFAULT
    AugmentationValidator2Split(step3_dir, step4_dir, sample_mode=args.sample).run_all()


if __name__ == "__main__":
    main()
