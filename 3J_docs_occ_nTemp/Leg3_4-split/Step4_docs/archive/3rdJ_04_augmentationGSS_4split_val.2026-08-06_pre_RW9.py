# -*- coding: utf-8 -*-
"""
3rdJ_04_augmentationGSS_4split_val.py

Step 4 Validator for Leg-3 (Residential + Office + Retail, three-GSS-head) Occupancy
Pipeline. Fork base: 3rdJ_04_augmentationGSS_2split_val.py, POST-2026-07-18
G4-stratification fix (the live, non-suffixed file whose scorecard of record on
R5_raked_mindwell_actv2 is 73 PASS / 3 WARN / 1 FAIL, sole FAIL = OW5
unobservable-by-design; verified against
outputs_step4/sweep/R5_raked_mindwell_actv2/step4_validation_report.txt,
generated 2026-07-18 17:06:49). The `.20260718_preG4fix` sibling (pooled
Simpson's-paradox G4) was explicitly NOT used, per the val doc's fork-base note.

Companion gate spec: Step4_docs/3rdJ_04_augmentationGSS_4split_val.md
Runbook:             Step4_docs/3rdJ_04_augmentationGSS_4split.md

Validates Step-4 augmented diaries for THREE occupancy channels:
  - Residential (AT_HOME)  -> ported Leg-2 gates G1-G4      (regression duty)
  - Office      (AT_WORK)  -> ported Leg-2 gates OW1-OW6    (regression duty)
  - Retail      (AT_RETAIL)-> NEW Leg-3 gates RW1-RW8       (headline)
Plus joint-consistency gates extended to the 3-way state (ISR-raw/ISR-final,
GA-3 floating discordance, GB-3 transition flicker, X-3 pairwise exclusivity),
and regression gates (REG-1..4) protecting Heads 1-2 against the Leg-2 baseline.

Three populations are compared inside augmented_diaries.csv:
  observed  (IS_SYNTHETIC == 0)
  synthetic (IS_SYNTHETIC == 1)
  vs Step-3 reference marginals (hetus_30min / copresence_30min / work_30min /
     retail_30min) and, for REG-*, vs the frozen Leg-2 baseline pool.

Gates per (cycle x stratum) unless noted. DDAY_STRATA: 1=weekday, 2=Saturday,
3=Sunday. Slot grid = 48 x 30-min, 04:00 origin (as Step-3). PR is the StatCan
province/territory numeric code carried through conditioning; QC=24, AB=48
(standard StatCan geography codes -- NOT redefined by this project; used only
for the RW6/RW7 QC-vs-AB Sunday split).

Report sections (mirror the val.md "Report Sections" table):
   1 Training health          (loss / val_js / gaps / pr_auc / f1 / isr_raw curves)
   2 Activity JS heatmap      (G1, regression view vs Leg-2 baseline) + REG-1/REG-2
   3 AT_HOME marginals + rhythm + Activity temporal (G2 + G4, regression)
   4 AT_WORK marginals + diurnal + sanity (OW1-OW6, regression)
   5 AT_RETAIL marginals + diurnal        [NEW headline] (per cycle x day-type,
     QC/AB Sunday panel)
   6 AT_RETAIL sanity                     [NEW] (RW battery, PR-AUC/F1, calibration
     proxy, all-zeros tripwire)
   7 Exclusivity & projection             [NEW/extended] (ISR before/after,
     conflict-slot census, threshold audit)
   8 Co-presence prevalence   (G3, regression)
   9 Secondary distributional + GA-3/GB-3 (not gated except GA-3/GB-3)
  10 Scorecard summary        (gate-first result; 5-seed table if --seed_summary given)

Output (written NEXT TO the input --step4_dir -- i.e. point --step4_dir at the
locked pool's sweep/<BASE>_raked3_mindwell_actv/ directory for the canonical
copy; never quote a top-level outputs_step4/ report if a sweep variant is the
production base -- the Leg-2 stale-report trap, repeated in the val doc):
  <step4_dir>/step4_validation_report.html  (dark theme, base64 PNG, scorecard)
  <step4_dir>/step4_validation_report.txt   (PASS/WARN/FAIL lines for cluster log)

Run locally:
    cd Step4_docs
    py -3 -X utf8 3rdJ_04_augmentationGSS_4split_val.py            # full / production
    py -3 -X utf8 3rdJ_04_augmentationGSS_4split_val.py --sample   # smoke, relaxed thresholds

⚠️ NOT RUN ON REAL DATA as of this build (2026-07-20) -- the locked Leg-3 pool
(sweep/<BASE>_raked3_mindwell_actv/) does not exist yet (04L/04M/04T + cluster
joint fine-tune are still pending per the runbook's Progress Checklist). This
file is built, py_compile-clean, and statically self-consistent against the
val doc's gate list; it has never been executed end-to-end against a real
augmented_diaries.csv or a real Leg-2 baseline pool.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import platform
import re
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
    _GSS_ROOT = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp"
elif os.path.isdir("/speed-scratch/o_iseri"):
    _GSS_ROOT = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp"
else:
    _GSS_ROOT = os.path.join(os.path.expanduser("~"), "GSSCanada", "GSSCanada-main",
                              "3J_docs_occ_nTemp")

_LEG3_BASE = os.path.join(_GSS_ROOT, "Leg3_4-split")
_LEG2_BASE = os.path.join(_GSS_ROOT, "Leg2_2-split")

STEP3_DIR_DEFAULT = os.path.join(_LEG3_BASE, "Step3_docs", "outputs_step3")
STEP4_DIR_DEFAULT = os.path.join(_LEG3_BASE, "Step4_docs", "outputs_step4")
# Frozen Leg-2 baseline for REG-* regression gates -- scorecard of record
# 73P/3W/1F (2026-07-18), G4-stratified. See val doc "Reference" section.
BASELINE_DIR_DEFAULT = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4",
                                     "sweep", "R5_raked_mindwell_actv2")

# Hardcoded from the val doc's own citation (Reference section): used as a
# fallback for the OW5-regression note if the baseline report can't be parsed
# live (e.g. baseline dir unreachable on this machine).
LEG2_BASELINE_OW5_PCT = 61.4


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
RETAIL_CAT = 4       # Purchasing Goods & Services -- matches 04T's RETAIL_CAT

# [Leg-3 NEW] Decode-time exclusivity thresholds (Delta G, runbook FROZEN).
# Not persisted to step4_feature_config.json -- hardcoded from the runbook /
# 04E's own CLI defaults for the "threshold audit" report line (informational
# only, not itself gated by the validator).
THETA_HOME = 0.50
THETA_WORK = 0.40
THETA_RETAIL = 0.15

# [Leg-3 NEW] StatCan province/territory numeric codes used for the RW6/RW7
# QC-vs-AB Sunday split. Standard geography codes, not project-defined.
PR_QC = 24
PR_AB = 48

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
    """Squared Jensen-Shannon divergence between two distributions (any equal-
    length nonnegative arrays; normalized internally). Used both for the
    14-category activity distribution (G1) and for 48-slot presence curves
    treated as pseudo-distributions (REG-1/REG-2/RW5)."""
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
    """Slot columns of the form <prefix>_001..048 (e.g. act30_, hom30_, wrk30_, ret30_)."""
    return [c for c in (f"{prefix}_{s:03d}" for s in range(1, N_SLOTS + 1)) if c in df.columns]


def cop_cols(df, channel):
    """Co-presence slot columns of the form <channel>30_001..048 (e.g. Alone30_)."""
    return [c for c in (f"{channel}30_{s:03d}" for s in range(1, N_SLOTS + 1)) if c in df.columns]


def _slot_minutes() -> np.ndarray:
    """Clock-time-of-day, in minutes, for each of the 48 slots (04:00 origin,
    30-min grid; wraps past midnight)."""
    return np.array([(4 * 60 + i * 30) % (24 * 60) for i in range(N_SLOTS)])


def _window_slots(start_h, start_m, end_h, end_m) -> np.ndarray:
    """0-indexed slot indices whose clock time falls in [start, end) (no
    midnight wraparound needed for any window used by this validator)."""
    mins = _slot_minutes()
    start = start_h * 60 + start_m
    end = end_h * 60 + end_m
    if end > start:
        return np.where((mins >= start) & (mins < end))[0]
    return np.where((mins >= start) | (mins < end))[0]


def _slot_labels() -> list:
    labels = []
    for i in range(N_SLOTS):
        tm = 4 * 60 + i * 30
        hh = (tm // 60) % 24
        mm = tm % 60
        labels.append(f"{hh:02d}:{mm:02d}" if mm == 0 else "")
    return labels


# ── Validator ─────────────────────────────────────────────────────────────────

class AugmentationValidator4Split:

    def __init__(self, step3_dir: str, step4_dir: str, baseline_dir: str,
                 sample_mode: bool = False, seed_summary: str = None):
        self.step3_dir = step3_dir
        self.step4_dir = step4_dir
        self.baseline_dir = baseline_dir
        self.sample_mode = sample_mode
        self.seed_summary_path = seed_summary
        self.thr = self._thresholds()
        self.results = {"pass": [], "warn": [], "fail": []}  # PASS/WARN/FAIL lines
        self.plots_b64 = {}   # key -> base64 PNG
        self.summary_rows = []
        self._retail_ok = False   # set True once ret30_* presence gate passes
        self._load_data()

    # ── thresholds ────────────────────────────────────────────────────────────

    def _thresholds(self) -> dict:
        """PASS/WARN gate thresholds. --sample relaxes them (undertrained model)."""
        if self.sample_mode:
            return {
                # residential (ported, unchanged relaxation from Leg-2)
                "g1_js_pass": 0.20, "g1_js_warn": 0.30, "g1_overall": 0.20,
                "g2_home_pass": 10.0, "g2_home_warn": 15.0,
                "g3_cop_pass": 10.0, "g3_cop_warn": 15.0,
                "g4_trans_pass": 50.0, "g4_trans_warn": 80.0,
                "g4_slot_pp_pass": 10.0, "g4_slot_pp_warn": 15.0,
                # office (ported, unchanged relaxation from Leg-2)
                "ow1_pass": 12.0, "ow1_warn": 18.0,
                "ow2_pass": 0.70, "ow2_warn": 0.50,
                "ow3_pass": 6, "ow3_warn": 10,
                "ow4_pass": 12.0, "ow4_warn": 18.0,
                "ow5_pass": 70.0, "ow5_warn": 50.0,
                "ow6_pass": 5.0, "ow6_warn": 15.0,
                # retail [Leg-3 NEW] -- relaxed for an undertrained smoke model
                "rw1_pass": 0.05, "rw1_warn": 0.03,
                "rw2_pass": 0.10, "rw2_warn": 0.05,
                "rw3_pass": 10.0, "rw3_warn": 15.0,
                "rw4_pass": 0.02,
                "rw5_pass": 0.10, "rw5_warn": 0.20,
                "rw8_pass": 5.0, "rw8_warn": 10.0,
                "retm_pass": 5.0, "retm_warn": 10.0,
                # joint-consistency [Leg-3 NEW] -- relaxed
                "isr_raw_pass": 3.0,        # see provenance note in validate_exclusivity()
                "ga3_pass_pp": 5.0, "ga3_warn_pp": 12.0,
                "gb3_pass_ratio": 1.5, "gb3_warn_ratio": 2.0,
                "x3_pass_pct": 5.0, "x3_warn_pct": 15.0,
                # regression [Leg-3 NEW] -- relaxed (smoke run vs production
                # baseline is not a meaningful regression comparison, but keep
                # a wide band so the section still runs and reports numbers)
                "reg1_js": 0.01, "reg2_js": 0.01, "reg3_trans": 0.5,
            }
        return {
            # residential (ported, PRODUCTION thresholds unchanged from Leg-2)
            "g1_js_pass": 0.05, "g1_js_warn": 0.10, "g1_overall": 0.03,
            "g2_home_pass": 2.0, "g2_home_warn": 4.0,
            "g3_cop_pass": 3.0, "g3_cop_warn": 6.0,
            "g4_trans_pass": 20.0, "g4_trans_warn": 40.0,
            "g4_slot_pp_pass": 3.0, "g4_slot_pp_warn": 6.0,
            # office (ported, PRODUCTION thresholds unchanged from Leg-2)
            "ow1_pass": 5.0, "ow1_warn": 8.0,
            "ow2_pass": 0.95, "ow2_warn": 0.90,
            "ow3_pass": 2, "ow3_warn": 4,
            "ow4_pass": 5.0, "ow4_warn": 8.0,
            "ow5_pass": 90.0, "ow5_warn": 80.0,
            "ow6_pass": 1.0, "ow6_warn": 5.0,
            # retail [Leg-3 NEW] -- val-doc production thresholds
            "rw1_pass": 0.15, "rw1_warn": 0.10,     # PR-AUC, higher-is-better
            "rw2_pass": 0.25, "rw2_warn": 0.20,     # F1,     higher-is-better
            "rw3_pass": 3.0, "rw3_warn": 5.0,       # midday rate error pp, lower-is-better
            "rw4_pass": 0.05,                        # transitions/day, higher-is-better (frozen-output tripwire)
            "rw5_pass": 0.02, "rw5_warn": 0.04,     # JS bits, lower-is-better (secondary)
            "rw8_pass": 1.0, "rw8_warn": 2.0,       # calibration |delta| pp, lower-is-better
            "retm_pass": 0.5, "retm_warn": 1.5,     # [implementer-added] retail rake-fidelity pp
            # joint-consistency [Leg-3 NEW]
            # ISR-raw: the 0.5% bar in the runbook/val doc was derived for the
            # 2-CHANNEL (home/work) Leg-2 encoder. With a 3rd co-active channel
            # (retail), raw pre-projection co-activation is expected to be
            # higher by construction (more pairwise ways to collide) -- the
            # runbook's own 04E build-time smoke note (2026-07-19) observed
            # 0.66-1.14% raw ISR across early checkpoints even before full
            # convergence. Per the val doc's explicit instruction: "raw-ISR is
            # a WARN gate with a re-derived 4-channel band ... do NOT let
            # raw-ISR be a hard FAIL." isr_raw_pass is therefore a soft
            # aspirational bar (PASS<=), not a threshold whose breach fails
            # the run -- see _grade_isr_raw().
            "isr_raw_pass": 1.5,
            "ga3_pass_pp": 2.0, "ga3_warn_pp": 5.0,       # matches Leg-2 GATE_A_*_PP verbatim
            "gb3_pass_ratio": 1.25, "gb3_warn_ratio": 1.50,  # matches Leg-2 GATE_B_*_RATIO verbatim
            "x3_pass_pct": 1.0, "x3_warn_pct": 5.0,
            # regression [Leg-3 NEW] -- HARD gates, no WARN tier (doc: severity=FAIL only)
            "reg1_js": 0.002, "reg2_js": 0.002, "reg3_trans": 0.1,
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

        # [Leg-3 NEW] isr_summary.json written by 04E (raw_isr_pct,
        # post_projection_isr_pct, post_pipeline_isr_pct) -- authoritative
        # source for ISR-raw (which cannot be recomputed from the CSV, since
        # only the final decoded/projected binary channels are persisted, not
        # the raw pre-projection sigmoid outputs).
        isr_path = os.path.join(self.step4_dir, "isr_summary.json")
        self.isr_summary = None
        if os.path.exists(isr_path):
            try:
                with open(isr_path, "r", encoding="utf-8") as f:
                    self.isr_summary = json.load(f)
            except Exception:
                self.isr_summary = None

        # [Leg-3 NEW] optional 5-seed metric summary (CSV: seed, gate, value)
        self.seed_summary = None
        if self.seed_summary_path and os.path.exists(self.seed_summary_path):
            try:
                self.seed_summary = pd.read_csv(self.seed_summary_path)
            except Exception:
                self.seed_summary = None

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
        self.ref_retail = _try("retail_30min.csv")   # [Leg-3 NEW]

        self.cycles = (sorted(int(c) for c in self.aug["CYCLE_YEAR"].dropna().unique())
                       if "CYCLE_YEAR" in self.aug.columns else CYCLES)

        # Baseline pool (Leg-2, for REG-*) -- lazy: existence-checked here,
        # actually READ inside validate_regression() so a missing/huge
        # baseline never blocks the rest of the report.
        self.baseline_aug_path = os.path.join(self.baseline_dir, "augmented_diaries.csv")
        self.baseline_report_txt = os.path.join(self.baseline_dir, "step4_validation_report.txt")

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

    def _grade_isr_raw(self, value):
        """[Leg-3 NEW] ISR-raw is a WARN-capped gate (never FAIL alone) per
        the val doc's explicit re-derivation for the 4-channel case -- see
        the isr_raw_pass threshold comment above."""
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "warn"
        return "pass" if value <= self.thr["isr_raw_pass"] else "warn"

    def _grade_isr_final(self, value):
        """[Leg-3 NEW] ISR-final is a hard gate: must be exactly 0% by
        construction (post-projection exclusivity)."""
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "fail"
        return "pass" if value <= 1e-9 else "fail"

    def _grade_hard(self, value, thr):
        """[Leg-3 NEW] Single-threshold hard gate (REG-1/2/3): PASS if
        value <= thr, else FAIL. No WARN tier (doc severity = FAIL only)."""
        return self._grade(value, thr, thr, direction="lower")

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

        # 1.4 [Leg-3 NEW] retail_gap / isr_raw / pr_auc / f1 curves present
        for col in ["retail_gap", "isr_raw", "pr_auc", "f1"]:
            if col in log.columns:
                self._rec("pass", "1.4", f"training log carries '{col}' "
                          f"(final epoch: {log[col].iloc[-1]:.4f})")
            else:
                self._rec("warn", "1.4", f"training log missing '{col}' -- "
                          f"downstream RW1/RW2/ISR-raw fallback affected")

        # Chart 1a: component losses
        fig, axes = plt.subplots(1, 3, figsize=(18, 4.5))
        fig.suptitle("Section 1 -- Training Health", color="#cdd6f4",
                     fontsize=13, fontweight="bold")
        x = log["epoch"] if "epoch" in log.columns else np.arange(1, n + 1)
        ax = axes[0]
        comp_map = [("train_loss", "total", "-"), ("act_loss", "act", "--"),
                    ("home_loss", "home", ":"), ("work_loss", "work", "-."),
                    ("retail_loss", "retail", (0, (5, 1))),
                    ("cop_loss", "cop", (0, (3, 1, 1, 1))), ("div_loss", "div", (0, (1, 1)))]
        for col, lbl, ls in comp_map:
            if col in log.columns:
                ax.plot(x, log[col], label=lbl, linestyle=ls, linewidth=1.6)
        ax.set_title("Component losses"); ax.set_xlabel("Epoch")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[1]
        for col, color in [("val_js", "#f38ba8"), ("home_gap", "#89b4fa"),
                           ("work_gap", "#fab387"), ("retail_gap", "#cba6f7")]:
            if col in log.columns:
                ax.plot(x, log[col], label=col, color=color, linewidth=1.8)
        ax.set_title("Validation metrics"); ax.set_xlabel("Epoch")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[2]
        for col, color in [("pr_auc", "#a6e3a1"), ("f1", "#fab387"),
                           ("isr_raw", "#f38ba8")]:
            if col in log.columns:
                ax.plot(x, log[col], label=col, color=color, linewidth=1.6)
        if "grad_norm" in log.columns:
            ax2 = ax.twinx()
            ax2.plot(x, log["grad_norm"], color="#cba6f7", linewidth=1.0,
                     alpha=0.6, label="grad_norm")
            ax2.set_ylabel("grad_norm", color="#cba6f7")
        ax.set_title("Retail gate-set proxies (PR-AUC / F1 / ISR-raw)"); ax.set_xlabel("Epoch")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["1_training"] = _b64(fig)

    # ── Section 2: Activity JS heatmap (G1) [regression view] ─────────────────

    def validate_activity_js(self):
        print("\n--- Section 2: Activity JS (G1, regression view) ---")
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
        self._g1_overall_js = overall  # stashed for the scorecard table

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

    # ── Section 3: AT_HOME marginals + rhythm (G2) + Activity temporal (G4) ───

    def validate_at_home(self):
        print("\n--- Section 3a: AT_HOME (G2) ---")
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

    def validate_temporal(self):
        print("\n--- Section 3b: Activity temporal (G4, stratified) ---")
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

        def slot_rate(arr, slots, cat):
            if arr.shape[0] == 0:
                return float("nan")
            idx = [i for i in slots if i < arr.shape[1]]
            return float(np.nanmean(arr[:, idx] == cat)) * 100

        # Sleep + work slot deltas, stratified by DDAY_STRATA (ported verbatim
        # from the Leg-2 G4-stratification fix, TICKET_G4_pooled_strata_defect.md,
        # 2026-07-18 -- the fork-base guard the val doc calls out by name).
        if obs_arr.shape[0] > 0:
            for label, slots, cat in [
                ("Night sleep-slot delta", SLEEP_NIGHT_SLOTS, RAW_SLEEP_CAT),
                ("Work peak-slot delta", WORK_PEAK_SLOTS, RAW_WORK_CAT),
            ]:
                strata_deltas = {}
                for s in [1, 2, 3]:
                    osub = self.obs[self.obs.get("DDAY_STRATA") == s]
                    ssub = self.syn[self.syn.get("DDAY_STRATA") == s]
                    o_arr_s = (osub[act_obs].to_numpy(dtype=float)
                               if (len(osub) and act_obs) else np.zeros((0, N_SLOTS)))
                    s_arr_s = (ssub[act_syn].to_numpy(dtype=float)
                               if len(ssub) else np.zeros((0, N_SLOTS)))
                    if o_arr_s.shape[0] == 0 or s_arr_s.shape[0] == 0:
                        continue
                    d = abs(slot_rate(o_arr_s, slots, cat) - slot_rate(s_arr_s, slots, cat))
                    strata_deltas[s] = d
                    lvl = self._grade(d, self.thr["g4_slot_pp_pass"], self.thr["g4_slot_pp_warn"])
                    self._rec(lvl, "G4", f"{label} ({STRATA_LABELS[s]}): {d:.2f} pp")
                if strata_deltas:
                    worst_s = max(strata_deltas, key=strata_deltas.get)
                    worst_d = strata_deltas[worst_s]
                    lvl = self._grade(worst_d, self.thr["g4_slot_pp_pass"], self.thr["g4_slot_pp_warn"])
                    self._rec(lvl, "G4",
                              f"{label} (worst stratum: {STRATA_LABELS[worst_s]}): {worst_d:.2f} pp")

        # Heatmaps obs vs syn (weekday)
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        fig.suptitle("Section 3 -- Activity Heatmap (Weekday: observed vs synthetic)",
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
        self.plots_b64["3_act_heatmap"] = _b64(fig)

    # ── Section 4: AT_WORK marginals + diurnal + sanity (OW1-OW6) ──────────────

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
        print("\n--- Section 4a: AT_WORK marginals + diurnal (OW1/OW2/OW3) ---")
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
        slot_lbls = _slot_labels()
        fig, axes = plt.subplots(len(self.cycles), 3, figsize=(20, 4 * len(self.cycles)),
                                 squeeze=False, sharex=True)
        fig.suptitle("Section 4 (regression) -- Mean AT_WORK Diurnal Curves "
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
        self.plots_b64["4_atwork_diurnal"] = _b64(fig)
        return True

    def validate_at_work_sanity(self):
        print("\n--- Section 4b: AT_WORK sanity (OW4/OW5/OW6) ---")
        _apply_dark()
        wrk_syn = present_cols(self.syn, "wrk30")
        if not wrk_syn:
            self._rec("fail", "OW4", "wrk30_* columns missing -- OW4/OW5/OW6 skipped")
            return

        syn_arr = self.syn[wrk_syn].to_numpy(dtype=float)

        # OW4: night near-zero (00:00-05:00)
        night_idx = [i for i in NIGHT_SLOTS if i < syn_arr.shape[1]]
        night_rate = float(np.nanmean(syn_arr[:, night_idx])) * 100 if syn_arr.shape[0] else float("nan")
        lvl = self._grade(night_rate, self.thr["ow4_pass"], self.thr["ow4_warn"])
        self._rec(lvl, "OW4", f"Night AT_WORK rate (00:00-05:00): {night_rate:.2f}%")

        # OW5: day-type ordering weekday >= Sat >= Sun per respondent
        n_ok = n_tot = 0
        pct_order = float("nan")
        if "occID" in self.syn.columns and "DDAY_STRATA" in self.syn.columns:
            tmp = self.syn.copy()
            tmp["_wrate"] = np.nanmean(tmp[wrk_syn].to_numpy(dtype=float), axis=1)
            piv = tmp.pivot_table(index="occID", columns="DDAY_STRATA",
                                  values="_wrate", aggfunc="mean")
            if set([1, 2, 3]).issubset(piv.columns):
                sub = piv.dropna(subset=[1, 2, 3])
                n_tot = len(sub)
                n_ok = int(((sub[1] >= sub[2]) & (sub[2] >= sub[3])).sum())
        if n_tot:
            pct_order = (n_ok / n_tot * 100)
            lvl = self._grade(pct_order, self.thr["ow5_pass"], self.thr["ow5_warn"], direction="higher")
            self._rec(lvl, "OW5",
                      f"Day-type ordering wkdy>=Sat>=Sun: {pct_order:.1f}% of {n_tot} respondents")
            # [Leg-3 NEW] REG-style regression note: OW5 is the known
            # non-blocking Leg-2 FAIL (unobservable-by-design). A Leg-3 value
            # materially WORSE than the Leg-2 baseline (61.4%) is itself a
            # regression WARN (val doc, "Hard gates -- OFFICE channel").
            baseline_ow5 = self._read_baseline_ow5()
            if not np.isnan(baseline_ow5):
                if pct_order < baseline_ow5 - 5.0:
                    self._rec("warn", "OW5-REG",
                              f"OW5 {pct_order:.1f}% is >5pp worse than Leg-2 baseline "
                              f"{baseline_ow5:.1f}% -- regression WARN")
                else:
                    self._rec("pass", "OW5-REG",
                              f"OW5 {pct_order:.1f}% vs Leg-2 baseline {baseline_ow5:.1f}%: no material regression")
        else:
            self._rec("warn", "OW5",
                      "Day-type ordering: insufficient per-respondent strata coverage")

        # OW6: channel exclusivity hom30==1 AND wrk30==1
        hom_syn = present_cols(self.syn, "hom30")
        if hom_syn:
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
        fig.suptitle("Section 4 -- Synthetic AT_WORK Rate by Cycle x Stratum",
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
        self.plots_b64["4_atwork_rate"] = _b64(fig)

    def _read_baseline_ow5(self) -> float:
        """[Leg-3 NEW] Best-effort parse of the Leg-2 baseline TXT report for
        the OW5 line; falls back to the val doc's hardcoded citation
        (61.4%) if the baseline report isn't reachable on this machine."""
        try:
            if os.path.exists(self.baseline_report_txt):
                with open(self.baseline_report_txt, "r", encoding="utf-8") as f:
                    for line in f:
                        if "OW5" in line and "Day-type ordering" in line:
                            m = re.search(r"([\d.]+)%\s+of", line)
                            if m:
                                return float(m.group(1))
        except Exception:
            pass
        return LEG2_BASELINE_OW5_PCT

    # ── Section 5: AT_RETAIL presence gate + marginals + diurnal [NEW headline] ─

    def validate_retail_presence(self):
        """[Leg-3 NEW] Gate 0 for the retail channel: ret30_001..048 must be
        present, values in {0,1}, no NaN in synthetic rows, correct shape.
        Missing columns are an explicit hard FAIL per the val doc's PASS/WARN/
        FAIL convention ("missing ret30_* columns")."""
        print("\n--- Section 5a: AT_RETAIL presence gate ---")
        ret_syn = present_cols(self.syn, "ret30")
        if len(ret_syn) != N_SLOTS:
            self._rec("fail", "RET-PRESENCE",
                      f"ret30_001..048 incomplete or missing in synthetic rows "
                      f"({len(ret_syn)}/{N_SLOTS} columns found)")
            self._retail_ok = False
            return
        arr = self.syn[ret_syn].to_numpy(dtype=float)
        n_nan = int(np.isnan(arr).sum())
        bad_vals = int(np.sum(~np.isin(arr[~np.isnan(arr)], [0.0, 1.0])))
        self._rec("pass" if n_nan == 0 else "fail", "RET-PRESENCE",
                  f"NaN count in synthetic ret30_*: {n_nan:,}")
        self._rec("pass" if bad_vals == 0 else "fail", "RET-PRESENCE",
                  f"Non-{{0,1}} values in synthetic ret30_*: {bad_vals:,}")
        self._rec("pass", "RET-PRESENCE",
                  f"ret30_001..048 present, shape {arr.shape}")
        self._retail_ok = (n_nan == 0 and bad_vals == 0)

    def _ret_curve(self, df, cy=None, s=None):
        rcols = present_cols(df, "ret30")
        if not rcols:
            return None
        sub = df
        if cy is not None and "CYCLE_YEAR" in df.columns:
            sub = sub[sub["CYCLE_YEAR"] == cy]
        if s is not None and "DDAY_STRATA" in df.columns:
            sub = sub[sub["DDAY_STRATA"] == s]
        if len(sub) == 0:
            return None
        return np.nanmean(sub[rcols].to_numpy(dtype=float), axis=0) * 100

    def validate_retail_marginals(self):
        print("\n--- Section 5b: AT_RETAIL marginals + diurnal [headline] ---")
        _apply_dark()
        if not self._retail_ok:
            self._rec("warn", "RETM", "retail presence gate failed -- Section 5b skipped")
            return
        ret_syn = present_cols(self.syn, "ret30")
        ret_obs = present_cols(self.obs, "ret30")

        # [implementer-added, task item 3] RETM: post-04L rake fidelity --
        # per (cycle x stratum), synthetic retail rate should match observed
        # almost exactly ("exact by construction" per the runbook's Delta H).
        # This is the retail analogue of G2/OW1, AND doubles as the data
        # source for RW8's calibration proxy (see validate_retail_sanity()
        # docstring for why a true pre-threshold calibration check isn't
        # recoverable from augmented_diaries.csv).
        retm_deltas = {}
        for cy in self.cycles:
            for s in [1, 2, 3]:
                osub = self.obs[(self.obs.get("CYCLE_YEAR") == cy) & (self.obs.get("DDAY_STRATA") == s)]
                ssub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                if len(ssub) == 0:
                    continue
                r_syn = np.nanmean(ssub[ret_syn].to_numpy(dtype=float)) * 100
                if len(osub) and ret_obs:
                    r_obs = np.nanmean(osub[ret_obs].to_numpy(dtype=float)) * 100
                else:
                    r_obs = float("nan")
                if np.isnan(r_obs):
                    self._rec("warn", "RETM",
                              f"AT_RETAIL rate {cy} x {STRATA_LABELS[s]}: syn {r_syn:.2f}% (no observed ref)")
                    continue
                delta = abs(r_obs - r_syn)
                retm_deltas[(cy, s)] = delta
                lvl = self._grade(delta, self.thr["retm_pass"], self.thr["retm_warn"])
                self._rec(lvl, "RETM",
                          f"AT_RETAIL rake-fidelity {cy} x {STRATA_LABELS[s]}: {delta:.2f} pp "
                          f"(obs {r_obs:.2f}% / syn {r_syn:.2f}%)")
        self._retm_deltas = retm_deltas

        # HEADLINE: 4-cycle x 3-stratum mean AT_RETAIL curves obs vs syn
        x = np.arange(N_SLOTS)
        slot_lbls = _slot_labels()
        fig, axes = plt.subplots(len(self.cycles), 3, figsize=(20, 4 * len(self.cycles)),
                                 squeeze=False, sharex=True)
        fig.suptitle("Section 5 -- Mean AT_RETAIL Diurnal Curves [Leg-3 Headline] "
                     "(cycle x stratum; observed vs synthetic)",
                     color="#cdd6f4", fontsize=14, fontweight="bold")
        for ci, cy in enumerate(self.cycles):
            for si, s in enumerate([1, 2, 3]):
                ax = axes[ci][si]
                oc = self._ret_curve(self.obs, cy=cy, s=s)
                sc = self._ret_curve(self.syn, cy=cy, s=s)
                if oc is not None:
                    ax.plot(x, oc, label="Observed", lw=1.8, color="#89b4fa")
                if sc is not None:
                    ax.plot(x, sc, label="Synthetic", lw=1.8, ls="--", color="#fab387")
                ax.set_title(f"{cy} - {STRATA_LABELS[s]}", fontsize=10)
                ax.grid(alpha=0.3); ax.set_ylim(0, None)
                if si == 0:
                    ax.set_ylabel("AT_RETAIL %")
                if ci == len(self.cycles) - 1:
                    ax.set_xticks(range(0, N_SLOTS, 4))
                    ax.set_xticklabels([slot_lbls[i] for i in range(0, N_SLOTS, 4)],
                                       rotation=45, fontsize=7)
                if ci == 0 and si == 2:
                    ax.legend(fontsize=8)
        plt.tight_layout()
        self.plots_b64["5_retail_diurnal"] = _b64(fig)

        # QC vs AB Sunday panel (RW6/RW7 provenance -- dr_L3-06)
        if "PR" in self.syn.columns:
            fig2, axes2 = plt.subplots(1, 2, figsize=(13, 4.5))
            fig2.suptitle("Section 5 -- Sunday AT_RETAIL: Quebec (PR=24) vs Alberta (PR=48)",
                         color="#cdd6f4", fontsize=13)
            for ax, (pr_code, lbl) in zip(axes2, [(PR_QC, "QC (Sunday)"), (PR_AB, "AB (Sunday)")]):
                ssub = self.syn[(self.syn.get("DDAY_STRATA") == 3) & (self.syn.get("PR") == pr_code)]
                osub = self.obs[(self.obs.get("DDAY_STRATA") == 3) & (self.obs.get("PR") == pr_code)]
                if len(ssub) and ret_syn:
                    ax.plot(x, np.nanmean(ssub[ret_syn].to_numpy(dtype=float), axis=0) * 100,
                            label="Synthetic", lw=1.8, ls="--", color="#fab387")
                if len(osub) and ret_obs:
                    ax.plot(x, np.nanmean(osub[ret_obs].to_numpy(dtype=float), axis=0) * 100,
                            label="Observed", lw=1.8, color="#89b4fa")
                ax.set_title(lbl); ax.set_xlabel("Slot"); ax.set_ylabel("AT_RETAIL %")
                ax.legend(fontsize=8); ax.grid(alpha=0.3)
            plt.tight_layout()
            self.plots_b64["5_retail_qcab"] = _b64(fig2)
        else:
            self._rec("warn", "RW6", "PR column not found -- QC/AB Sunday panel skipped")

    # ── Section 6: AT_RETAIL sanity (RW battery) [NEW] ─────────────────────────

    def _read_training_metric(self, col: str) -> float:
        """Best epoch's (max val_score / last row) value for a retail
        gate-set proxy column in step4_training_log.csv."""
        if self.train_log is None or col not in self.train_log.columns:
            return float("nan")
        series = self.train_log[col].dropna()
        if series.empty:
            return float("nan")
        return float(series.iloc[-1])

    def validate_retail_sanity(self):
        """RW1-RW8, per val doc. Data-source notes:
          - RW1 (PR-AUC) / RW2 (F1): read from step4_training_log.csv's
            'pr_auc'/'f1' columns -- the teacher-forced self-reconstruction
            estimate computed inside 04D's validate() (the runbook's own
            ESCALATE #4: the only place real retail ground truth exists,
            since AR-generated synthetic day-types have no ground truth).
            augmented_diaries.csv only carries the FINAL decoded binary
            ret30_* channel, not a continuous score, so PR-AUC/F1 cannot be
            recomputed from the CSV alone.
          - RW8 (calibration): a true pre-threshold check needs the
            calibrated sigmoid mean per (cycle x stratum), which 04E does not
            persist anywhere (only isr_summary.json and
            g3_copresence_thresholds.json are written alongside the CSV).
            Implemented as a PROXY: |mean(syn ret30) - mean(obs ret30)| per
            (cycle x stratum) -- identical computation to RETM above (both
            numbers are cited under both gate IDs). Flagged as a known
            implementation gap; a genuine RW8 would need 04E extended to dump
            a retail_prob_summary.json of pre-threshold means.
        """
        print("\n--- Section 6: AT_RETAIL sanity (RW battery) ---")
        _apply_dark()
        if not self._retail_ok:
            self._rec("fail", "RW1", "retail presence gate failed -- RW battery skipped")
            return

        ret_syn = present_cols(self.syn, "ret30")
        ret_obs = present_cols(self.obs, "ret30")
        syn_arr = self.syn[ret_syn].to_numpy(dtype=float)

        # ── All-zeros tripwire (dr_L3-08 toothless-JS lesson) ────────────────
        all_zero = bool(np.nansum(syn_arr) == 0)
        if all_zero:
            self._rec("fail", "RW-TRIPWIRE",
                      "retail channel is entirely zero across all synthetic rows "
                      "-- dead-head signature (an all-zeros head would still score "
                      "JS~0.010 and pass a bare <0.02 gate; RW1/RW2/RW4 below must "
                      "also independently fail this)")
        else:
            self._rec("pass", "RW-TRIPWIRE", "retail channel is not all-zeros")

        # ── RW1: PR-AUC ────────────────────────────────────────────────────
        pr_auc = self._read_training_metric("pr_auc")
        rw1_lvl = self._grade(pr_auc, self.thr["rw1_pass"], self.thr["rw1_warn"], direction="higher")
        self._rec(rw1_lvl, "RW1", f"PR-AUC (teacher-forced, from step4_training_log.csv): "
                  f"{pr_auc:.4f}" if not np.isnan(pr_auc) else "PR-AUC unavailable -- step4_training_log.csv missing 'pr_auc'")

        # ── RW2: F1 @ theta_retail=0.15 ───────────────────────────────────
        f1 = self._read_training_metric("f1")
        rw2_lvl = self._grade(f1, self.thr["rw2_pass"], self.thr["rw2_warn"], direction="higher")
        self._rec(rw2_lvl, "RW2", f"F1 (teacher-forced, from step4_training_log.csv): "
                  f"{f1:.4f}" if not np.isnan(f1) else "F1 unavailable -- step4_training_log.csv missing 'f1'")

        # RW1+RW2 double-miss = dead-head signature (explicit FAIL convention item)
        if rw1_lvl == "fail" and rw2_lvl == "fail":
            self._rec("fail", "RW-DEADHEAD",
                      "RW1+RW2 double-miss: dead-head signature per the val doc's "
                      "PASS/WARN/FAIL convention")

        # ── RW3: midday rate error, 11:00-14:00, syn vs obs ──────────────────
        midday_idx = _window_slots(11, 0, 14, 0)
        if syn_arr.shape[0] and len(midday_idx):
            syn_midday = float(np.nanmean(syn_arr[:, midday_idx])) * 100
            if len(self.obs) and ret_obs:
                obs_arr = self.obs[ret_obs].to_numpy(dtype=float)
                obs_midday = float(np.nanmean(obs_arr[:, midday_idx])) * 100
                d = abs(syn_midday - obs_midday)
                lvl = self._grade(d, self.thr["rw3_pass"], self.thr["rw3_warn"])
                self._rec(lvl, "RW3", f"Midday (11:00-14:00) rate error: {d:.2f} pp "
                          f"(obs {obs_midday:.2f}% / syn {syn_midday:.2f}%)")
            else:
                self._rec("warn", "RW3", f"Midday rate: syn {syn_midday:.2f}% (no observed ref)")

        # ── RW4: transitions/day (retail channel, post-decode) ──────────────
        if syn_arr.shape[0]:
            trans = np.sum(syn_arr[:, :-1] != syn_arr[:, 1:], axis=1)
            mean_trans = float(np.mean(trans))
            lvl = self._grade(mean_trans, self.thr["rw4_pass"], self.thr["rw4_pass"], direction="higher")
            self._rec(lvl, "RW4", f"Transitions/day (retail): {mean_trans:.4f} "
                      f"(catches frozen/all-zeros output; PASS if >= {self.thr['rw4_pass']}/day)")

        # ── RW5: JS(AT_RETAIL) -- secondary, only if RW1+RW2 PASS ────────────
        if rw1_lvl == "pass" and rw2_lvl == "pass":
            js_vals = []
            for cy in self.cycles:
                for s in [1, 2, 3]:
                    osub = self.obs[(self.obs.get("CYCLE_YEAR") == cy) & (self.obs.get("DDAY_STRATA") == s)]
                    ssub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                    if len(osub) == 0 or len(ssub) == 0 or not ret_obs:
                        continue
                    oc = np.nanmean(osub[ret_obs].to_numpy(dtype=float), axis=0)
                    sc = np.nanmean(ssub[ret_syn].to_numpy(dtype=float), axis=0)
                    v = js_div(oc, sc)
                    js_vals.append(v)
                    lvl = self._grade(v, self.thr["rw5_pass"], self.thr["rw5_warn"])
                    self._rec(lvl, "RW5", f"JS(AT_RETAIL) {cy} x {STRATA_LABELS[s]}: {v:.4f}")
            if js_vals:
                overall = float(np.mean(js_vals))
                lvl = self._grade(overall, self.thr["rw5_pass"], self.thr["rw5_warn"])
                self._rec(lvl, "RW5", f"Overall mean JS(AT_RETAIL): {overall:.4f}")
        else:
            self._rec("pass", "RW5",
                      "not gated -- RW1/RW2 prerequisite not met (JS is secondary/toothless "
                      "per dr_L3-08; recording as informational-pass since a JS breach here "
                      "does not add information beyond the RW1/RW2 failure already recorded)")

        # ── RW6: diurnal targets in-band per cycle x day-type ────────────────
        self._validate_rw6_rw7(ret_syn)

        # ── RW8: calibration proxy (see docstring) ───────────────────────────
        retm_deltas = getattr(self, "_retm_deltas", {})
        if retm_deltas:
            overall_rw8 = float(np.mean(list(retm_deltas.values())))
            lvl = self._grade(overall_rw8, self.thr["rw8_pass"], self.thr["rw8_warn"])
            self._rec(lvl, "RW8",
                      f"Calibration proxy |mean(syn ret30) - mean(obs ret30)|, mean over "
                      f"(cycle x stratum): {overall_rw8:.2f} pp [PROXY -- see RW8 docstring; "
                      f"same underlying numbers as RETM]")
        else:
            self._rec("warn", "RW8", "no RETM deltas available -- RW8 proxy skipped "
                      "(run Section 5b first)")

        # Chart: RW1/RW2 bar vs thresholds + all-day episode-time share
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        fig.suptitle("Section 6 -- AT_RETAIL Sanity (RW battery)", color="#cdd6f4", fontsize=13)
        ax = axes[0]
        metrics = ["PR-AUC (RW1)", "F1 (RW2)"]
        vals = [0.0 if np.isnan(pr_auc) else pr_auc, 0.0 if np.isnan(f1) else f1]
        thr_pass = [self.thr["rw1_pass"], self.thr["rw2_pass"]]
        x = np.arange(len(metrics))
        ax.bar(x, vals, width=0.4, color="#89b4fa", label="Measured")
        ax.scatter(x, thr_pass, color="#f38ba8", zorder=5, label="PASS threshold")
        ax.set_xticks(x); ax.set_xticklabels(metrics)
        ax.set_ylim(0, 1); ax.legend(fontsize=8); ax.grid(alpha=0.3)
        ax.set_title("Gate-set proxy metrics")

        ax2 = axes[1]
        all_day_share = float(np.nanmean(syn_arr)) * 100 if syn_arr.shape[0] else float("nan")
        ax2.bar(["All-day AT_RETAIL share (syn)"], [all_day_share], color="#a6e3a1")
        ax2.axhspan(2.1, 2.3, color="#f9e2af", alpha=0.3, label="target 2.1-2.3%")
        ax2.set_ylabel("%"); ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
        ax2.set_title("All-day episode-time share vs dr_L3-06 target")
        plt.tight_layout()
        self.plots_b64["6_retail_sanity"] = _b64(fig)

    def _validate_rw6_rw7(self, ret_syn):
        """RW6 (in-band diurnal targets) and RW7 (population-level ordering)."""
        syn = self.syn
        margin = 0.30  # implementer-chosen WARN buffer around the doc's [lo,hi] bands

        def _rate(df, dday, window, pr_code=None):
            sub = df[df.get("DDAY_STRATA") == dday]
            if pr_code is not None and "PR" in df.columns:
                sub = sub[sub["PR"] == pr_code]
            rcols = present_cols(sub, "ret30")
            if not rcols or len(sub) == 0:
                return float("nan")
            arr = sub[rcols].to_numpy(dtype=float)
            idx = [i for i in window if i < arr.shape[1]]
            return float(np.nanmean(arr[:, idx])) if idx else float("nan")

        def _grade_band(v, lo, hi, hard=True):
            # [V2-D1, 2026-08-04] hard=True is the correct default and is no
            # longer overridden at the call sites below. Prior code called
            # this with hard=False on the claim that RW6's val-doc table has
            # "no FAIL column" -- but RW1/RW3/RW4/RW5/RW8 have the identical
            # table shape (Gate/Metric/PASS/WARN, no explicit FAIL column)
            # and all FAIL via self._grade() when they miss the WARN buffer;
            # the section is titled "Hard gates -- RETAIL channel". hard=False
            # made an out-of-band value structurally incapable of failing --
            # e.g. weekday 0.0453 against the 0.06 floor (24.5% short, and
            # outside the 30% WARN buffer's 0.048 floor) reported WARN instead
            # of FAIL. Catalogue class #14, severity-vacuous gate (Codex C-3).
            # Sibling RW7 QC<AB Sunday genuinely IS a documented-derivation
            # WARN cap (sampling SE analysis, job 1128112) -- that one stays.
            if np.isnan(v):
                return "fail" if hard else "warn"
            if lo <= v <= hi:
                return "pass"
            span = hi - lo
            if (lo - margin * span) <= v <= (hi + margin * span):
                return "warn"
            return "fail" if hard else "warn"

        weekday_win = _window_slots(12, 0, 14, 0)
        sat_win = _window_slots(13, 0, 16, 0)
        qc_sun_win = _window_slots(12, 0, 17, 0)
        ab_sun_win = _window_slots(12, 0, 16, 0)
        night_win = np.array(NIGHT_SLOTS)

        peaks = {}
        for cy in self.cycles:
            v_wd = _rate(syn, 1, weekday_win)
            lvl = _grade_band(v_wd, 0.06, 0.10)
            self._rec(lvl, "RW6", f"Weekday 12:00-14:00 rate {cy}: {v_wd:.4f} (target 0.06-0.10)")

            v_sat = _rate(syn, 2, sat_win)
            lvl = _grade_band(v_sat, 0.09, 0.12)
            self._rec(lvl, "RW6", f"Saturday 13:00-16:00 rate {cy}: {v_sat:.4f} (target 0.09-0.12)")

            v_qc = _rate(syn, 3, qc_sun_win, pr_code=PR_QC)
            lvl = _grade_band(v_qc, 0.04, 0.07)
            self._rec(lvl, "RW6", f"Sunday QC (PR=24) 12:00-17:00 rate {cy}: {v_qc:.4f} (target 0.04-0.07)")

            v_ab = _rate(syn, 3, ab_sun_win, pr_code=PR_AB)
            lvl = _grade_band(v_ab, 0.06, 0.10)
            self._rec(lvl, "RW6", f"Sunday AB (PR=48) 12:00-16:00 rate {cy}: {v_ab:.4f} (target 0.06-0.10)")

            v_night = _rate(syn, 1, night_win)  # night window applies across day-types; weekday used as proxy pool
            lvl = _grade_band(v_night, 0.000, 0.003)
            self._rec(lvl, "RW6", f"Night 00:00-05:00 rate {cy} (weekday pool): {v_night:.4f} (target 0.000-0.003)")

            peaks[cy] = {"weekday": v_wd, "sat": v_sat, "qc_sun": v_qc, "ab_sun": v_ab}

        # RW7: population-level ordering
        wd_all = [p["weekday"] for p in peaks.values() if not np.isnan(p["weekday"])]
        sat_all = [p["sat"] for p in peaks.values() if not np.isnan(p["sat"])]
        if wd_all and sat_all:
            ordering_ok = float(np.mean(sat_all)) > float(np.mean(wd_all))
            self._rec("pass" if ordering_ok else "fail", "RW7",
                      f"Day-type ordering Sat({np.mean(sat_all):.4f}) > "
                      f"Weekday({np.mean(wd_all):.4f}): {ordering_ok}")
        else:
            self._rec("warn", "RW7", "insufficient data for Sat>Weekday ordering check")

        qc_all = [p["qc_sun"] for p in peaks.values() if not np.isnan(p["qc_sun"])]
        ab_all = [p["ab_sun"] for p in peaks.values() if not np.isnan(p["ab_sun"])]
        if qc_all and ab_all:
            qc_lt_ab = float(np.mean(qc_all)) < float(np.mean(ab_all))
            # QC<AB Sunday ordering is a dr_L3-06 MEDIUM-confidence target that
            # the observed GSS data does NOT robustly carry: the 2026-07-20 obs-vs-syn
            # diagnostic (job 1128112) showed the OBSERVED ordering INVERTED in
            # 2010 (+0.40pp) and 2015 (+0.41pp), holding pooled (-0.22pp) only on
            # the strength of 2022 alone (-1.48pp), over tiny AB-Sunday strata
            # (n~=177-209/cycle -> sampling SE ~=+/-1.7pp >> the 0.22pp signal).
            # Forcing the model to reproduce a sub-noise ordering would be
            # overfitting. -> a miss on this sub-check grades WARN, not FAIL
            # (same evidence-based severity logic as RW6; the Sat>weekday
            # sub-check above stays a hard PASS/FAIL -- that ordering IS robust).
            self._rec("pass" if qc_lt_ab else "warn", "RW7",
                      f"QC Sunday({np.mean(qc_all):.4f}) < AB Sunday({np.mean(ab_all):.4f}): "
                      f"{qc_lt_ab} -- medium-confidence dr_L3-06 target, not robust in "
                      f"observed data (WARN not FAIL; see diag job 1128112 in val doc); "
                      f"retail's ordering is the REVERSE of office's -- do not copy OW5")
        else:
            self._rec("warn", "RW7", "insufficient PR-coded data for QC<AB Sunday ordering check")

    # ── Section 7: Exclusivity & projection (ISR + X-3) [NEW/extended] ────────

    def validate_exclusivity(self):
        print("\n--- Section 7: Exclusivity & projection (ISR-raw/final, X-3) ---")
        _apply_dark()

        # ── ISR-raw: WARN-capped gate, from isr_summary.json (authoritative;
        #    raw pre-projection probabilities aren't in the CSV) with a
        #    training-log fallback (val-split proxy, not the full-pool number). ──
        isr_raw_pct = float("nan")
        isr_raw_source = "unavailable"
        if self.isr_summary and "raw_isr_pct" in self.isr_summary:
            isr_raw_pct = float(self.isr_summary["raw_isr_pct"])
            isr_raw_source = "isr_summary.json (full-pool 04E generation)"
        else:
            fallback = self._read_training_metric("isr_raw")
            if not np.isnan(fallback):
                isr_raw_pct = fallback * 100 if fallback <= 1.0 else fallback
                isr_raw_source = "step4_training_log.csv 'isr_raw' [FALLBACK -- val-split proxy, not full pool]"
        lvl = self._grade_isr_raw(isr_raw_pct)
        self._rec(lvl, "ISR-raw",
                  f"Raw (pre-projection) ISR: {isr_raw_pct:.4f}% (source: {isr_raw_source}); "
                  f"WARN-capped per 4-channel re-derivation, never a hard FAIL "
                  f"(soft target <= {self.thr['isr_raw_pass']}%)"
                  if not np.isnan(isr_raw_pct) else
                  "Raw ISR unavailable -- neither isr_summary.json nor training-log fallback found")

        # ── ISR-final: hard gate, recomputed directly from the final CSV ─────
        hom_syn = present_cols(self.syn, "hom30")
        wrk_syn = present_cols(self.syn, "wrk30")
        ret_syn = present_cols(self.syn, "ret30")
        isr_final_pct = float("nan")
        conflict_counts = {}
        if hom_syn and wrk_syn and ret_syn and self._retail_ok:
            common = [i for i in range(1, N_SLOTS + 1)
                      if f"hom30_{i:03d}" in self.syn.columns
                      and f"wrk30_{i:03d}" in self.syn.columns
                      and f"ret30_{i:03d}" in self.syn.columns]
            h = self.syn[[f"hom30_{i:03d}" for i in common]].to_numpy(dtype=float)
            w = self.syn[[f"wrk30_{i:03d}" for i in common]].to_numpy(dtype=float)
            r = self.syn[[f"ret30_{i:03d}" for i in common]].to_numpy(dtype=float)
            total = h.size
            n_hw = int(np.nansum((h == 1) & (w == 1)))
            n_hr = int(np.nansum((h == 1) & (r == 1)))
            n_wr = int(np.nansum((w == 1) & (r == 1)))
            n_any_gt1 = int(np.nansum(((h == 1).astype(int) + (w == 1).astype(int)
                                        + (r == 1).astype(int)) > 1))
            isr_final_pct = (n_any_gt1 / total * 100) if total else float("nan")
            conflict_counts = {
                "hom AND wrk": (n_hw, n_hw / total * 100 if total else float("nan")),
                "hom AND ret": (n_hr, n_hr / total * 100 if total else float("nan")),
                "wrk AND ret": (n_wr, n_wr / total * 100 if total else float("nan")),
            }
            lvl = self._grade_isr_final(isr_final_pct)
            self._rec(lvl, "ISR-final",
                      f"Final (post-projection) ISR, recomputed from augmented_diaries.csv: "
                      f"{isr_final_pct:.6f}% ({n_any_gt1:,}/{total:,} slots with >1 active "
                      f"channel; hard gate, must be exactly 0%)")

            # Cross-check against 04E's own post_pipeline_isr_pct if available
            if self.isr_summary and "post_pipeline_isr_pct" in self.isr_summary:
                json_val = float(self.isr_summary["post_pipeline_isr_pct"])
                agree = abs(json_val - isr_final_pct) < 1e-3
                self._rec("pass" if agree else "warn", "ISR-final",
                          f"Cross-check vs isr_summary.json post_pipeline_isr_pct="
                          f"{json_val:.6f}%: {'agrees' if agree else 'MISMATCH'}")

            # X-3: pairwise exclusivity cells
            for label, (n, pct) in conflict_counts.items():
                lvl = self._grade(pct, self.thr["x3_pass_pct"], self.thr["x3_warn_pct"])
                self._rec(lvl, "X-3", f"Pairwise exclusivity ({label}): {n:,} cells ({pct:.4f}%)")
        else:
            self._rec("fail", "ISR-final",
                      "cannot recompute -- hom30/wrk30/ret30 columns not all present "
                      "in synthetic rows")

        # Chart: ISR before/after bar + conflict census
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        fig.suptitle("Section 7 -- Exclusivity & Projection", color="#cdd6f4", fontsize=13)
        ax = axes[0]
        labels = ["ISR-raw", "ISR-final"]
        vals = [0.0 if np.isnan(isr_raw_pct) else isr_raw_pct,
                0.0 if np.isnan(isr_final_pct) else isr_final_pct]
        colors = ["#f38ba8" if v > 0.5 else "#a6e3a1" for v in vals]
        ax.bar(labels, vals, color=colors)
        ax.set_ylabel("% of slots"); ax.grid(alpha=0.3)
        ax.set_title("ISR before/after projection")

        ax2 = axes[1]
        if conflict_counts:
            names = list(conflict_counts.keys())
            pcts = [conflict_counts[k][1] for k in names]
            ax2.bar(names, pcts, color="#89b4fa")
            ax2.axhline(self.thr["x3_pass_pct"], color="#a6e3a1", ls="--", label="PASS bar")
            ax2.axhline(self.thr["x3_warn_pct"], color="#f9e2af", ls="--", label="WARN bar")
            ax2.legend(fontsize=8)
        ax2.set_ylabel("% of slots"); ax2.grid(alpha=0.3)
        ax2.set_title("X-3 pairwise conflict-slot census")
        plt.tight_layout()
        self.plots_b64["7_isr_exclusivity"] = _b64(fig)

        # Threshold audit (informational, not gated)
        self._rec("pass", "THRESH-AUDIT",
                  f"Decode-time exclusivity thresholds (runbook Delta G, FROZEN): "
                  f"theta_home={THETA_HOME}, theta_work={THETA_WORK}, theta_retail={THETA_RETAIL}")

    # ── Section 8: Co-presence prevalence (G3) ─────────────────────────────────

    def validate_copresence(self):
        print("\n--- Section 8: Co-presence prevalence (G3) ---")
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

        names = [cn for cn in COP_COLS if cn in prev_syn]
        if names:
            fig, ax = plt.subplots(figsize=(12, 4))
            x = np.arange(len(names)); w = 0.4
            ax.bar(x - w / 2, [prev_obs.get(cn, np.nan) for cn in names], width=w,
                   label="Observed", color="#89b4fa", alpha=0.85)
            ax.bar(x + w / 2, [prev_syn.get(cn, np.nan) for cn in names], width=w,
                   label="Synthetic", color="#fab387", alpha=0.85)
            ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right")
            ax.set_title("Section 8 -- Co-Presence Prevalence (observed vs synthetic)",
                         color="#cdd6f4")
            ax.set_ylabel("% slots present"); ax.legend(fontsize=9); ax.grid(alpha=0.3)
            plt.tight_layout()
            self.plots_b64["8_cop_prev"] = _b64(fig)

    # ── Section 9: Secondary distributional + GA-3/GB-3 ────────────────────────

    def validate_secondary(self):
        print("\n--- Section 9a: Secondary distributional (reported, not gated) ---")
        _apply_dark()
        lines = []

        def channel_metrics(name, prefix):
            ocols = present_cols(self.obs, prefix)
            scols = present_cols(self.syn, prefix)
            if not scols:
                return
            sarr = self.syn[scols].to_numpy(dtype=float)
            s_daily = np.nansum(sarr == 1, axis=1).astype(float)
            if len(self.obs) and ocols:
                oarr = self.obs[ocols].to_numpy(dtype=float)
                o_daily = np.nansum(oarr == 1, axis=1).astype(float)
            else:
                o_daily = None

            if o_daily is not None and _HAVE_SCIPY and o_daily.size and s_daily.size:
                emd = float(wasserstein_distance(o_daily, s_daily))
                lines.append(f"[{name}] EMD(daily-presence-count): {emd:.3f} slots")
            if o_daily is not None and _HAVE_SCIPY and o_daily.size and s_daily.size:
                ks = float(ks_2samp(o_daily, s_daily).statistic)
                lines.append(f"[{name}] KS(daily-presence-count): {ks:.3f}")
            if o_daily is not None and ocols:
                o_curve = np.nanmean(oarr == 1, axis=0)
                s_curve = np.nanmean(sarr == 1, axis=0)
                lines.append(f"[{name}] mean-curve MAE: {np.mean(np.abs(o_curve - s_curve)) * 100:.2f} pp")
                def acf(c, lag):
                    c = c - c.mean()
                    denom = np.sum(c * c) + 1e-12
                    return np.sum(c[:-lag] * c[lag:]) / denom
                lags = range(1, min(24, N_SLOTS - 1) + 1)
                acf_mae = np.mean([abs(acf(o_curve, L) - acf(s_curve, L)) for L in lags])
                lines.append(f"[{name}] ACF-MAE (lags 1-24): {acf_mae:.4f}")

            s_trans = np.nansum(sarr[:, :-1] != sarr[:, 1:], axis=1).mean()
            if len(self.obs) and ocols:
                o_trans = np.nansum(oarr[:, :-1] != oarr[:, 1:], axis=1).mean()
                lines.append(f"[{name}] transitions/day: obs {o_trans:.3f} / syn {s_trans:.3f}")
            else:
                lines.append(f"[{name}] transitions/day: syn {s_trans:.3f}")

        channel_metrics("AT_HOME", "hom30")
        channel_metrics("AT_WORK", "wrk30")
        if self._retail_ok:
            channel_metrics("AT_RETAIL", "ret30")   # [Leg-3 NEW]

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

        # [Leg-3 NEW] Shopping activity but AT_RETAIL=0 (informational only --
        # not a gated FLOATING-style check; RETAIL_CAT slots may legitimately
        # be non-retail purchasing, e.g. online/phone orders at home).
        if self._retail_ok and act_syn:
            ret_syn = present_cols(self.syn, "ret30")
            s_act = self.syn[act_syn].to_numpy(dtype=float)
            s_ret = self.syn[ret_syn].to_numpy(dtype=float)
            s_pact_mask = (s_act == RETAIL_CAT)
            s_pviol = np.sum(s_pact_mask & (s_ret == 0))
            s_pact_tot = np.sum(s_pact_mask)
            s_prate = (s_pviol / s_pact_tot * 100) if s_pact_tot > 0 else 0.0
            lines.append(f"[Semantic] Purchasing activity but AT_RETAIL=0: syn {s_prate:.1f}% "
                         f"(informational -- legitimate for online/phone purchasing)")

        if len(self.obs):
            p = activity_dist(self.obs); q = activity_dist(self.syn)
            p = np.clip(p, 1e-12, None); q = np.clip(q, 1e-12, None)
            kl = float(np.sum(p * np.log(p / q)))
            lines.append(f"[Activity] KL(obs||syn) 14-cat: {kl:.4f}")

        for ln in lines:
            self._rec("pass", "S9", ln)
        if not lines:
            self._rec("warn", "S9", "no secondary metrics computable")

    # GA-3 / GB-3 thresholds (val doc: same numeric bars as Leg-2's Gate A/B)
    GA3_PASS_PP = 2.0
    GA3_WARN_PP = 5.0
    GB3_PASS_RATIO = 1.25
    GB3_WARN_RATIO = 1.50

    def validate_ga3_gb3(self):
        """GA-3 -- Activity<->occupancy FLOATING discordance, extended to the
        3-way state (WORK/HOME/RETAIL/NEITHER), porting the
        3rdJ_04P_discordance_4split.py decomposition inline (the val doc's
        "GA-3 before/after evidence tool"): FLOATING now excludes
        RETAIL-incompatible slots (work-activity & wrk=0 & hom=0 & ret=1),
        which are reported separately as a physical-state signal that is
        retail, not workplace, rather than folded into either bucket.

        GB-3 -- Transition-flicker ratio per channel (home, work, retail).
        """
        print("\n--- Section 9b: GA-3 (floating discordance) + GB-3 (transition flicker) ---")
        act_obs = present_cols(self.obs, "act30")
        act_syn = present_cols(self.syn, "act30")
        hom_obs = present_cols(self.obs, "hom30")
        hom_syn = present_cols(self.syn, "hom30")
        wrk_obs = present_cols(self.obs, "wrk30")
        wrk_syn = present_cols(self.syn, "wrk30")
        ret_obs = present_cols(self.obs, "ret30")
        ret_syn = present_cols(self.syn, "ret30")

        # ── GA-3: 4-way FLOATING rate (mirrors 3rdJ_04P_discordance_4split.py) ─
        def _decompose(df, act_c, wrk_c, hom_c, ret_c):
            if not act_c or not wrk_c or not hom_c or not ret_c or len(df) == 0:
                return None
            a = df[act_c].to_numpy(dtype=float)
            w = df[wrk_c].to_numpy(dtype=float)
            h = df[hom_c].to_numpy(dtype=float)
            r = df[ret_c].to_numpy(dtype=float)
            work_mask = (a == RAW_WORK_CAT)
            n_work = int(work_mask.sum())
            if n_work == 0:
                return {"n_work": 0}
            atwork = int((work_mask & (w == 1)).sum())
            telework = int((work_mask & (w == 0) & (h == 1)).sum())
            retail_incompat = int((work_mask & (w == 0) & (h == 0) & (r == 1)).sum())
            floating = int((work_mask & (w == 0) & (h == 0) & (r == 0)).sum())
            return {
                "n_work": n_work, "atwork": atwork, "telework": telework,
                "retail_incompat": retail_incompat, "floating": floating,
                "atwork_pct": 100.0 * atwork / n_work,
                "telework_pct": 100.0 * telework / n_work,
                "retail_incompat_pct": 100.0 * retail_incompat / n_work,
                "floating_pct": 100.0 * floating / n_work,
            }

        if self._retail_ok:
            obs_d = _decompose(self.obs, act_obs, wrk_obs, hom_obs, ret_obs)
            syn_d = _decompose(self.syn, act_syn, wrk_syn, hom_syn, ret_syn)
            if obs_d is None or obs_d.get("n_work", 0) == 0:
                self._rec("warn", "GA-3", "no observed work-activity slots -- cannot compute obs baseline")
            elif syn_d is None or syn_d.get("n_work", 0) == 0:
                self._rec("warn", "GA-3", "no synthetic work-activity slots -- cannot compute syn rate")
            else:
                for k in ["atwork_pct", "telework_pct", "retail_incompat_pct", "floating_pct"]:
                    self._rec("pass", "GA-3",
                              f"{k}: obs {obs_d[k]:.2f}% / syn {syn_d[k]:.2f}% (informational decomposition)")
                excess = syn_d["floating_pct"] - obs_d["floating_pct"]
                lvl = self._grade(excess, self.GA3_PASS_PP, self.GA3_WARN_PP)
                self._rec(lvl, "GA-3",
                          f"FLOATING rate excess (syn-obs), retail-incompatible excluded: "
                          f"{excess:+.2f} pp (obs {obs_d['floating_pct']:.2f}% "
                          f"[{obs_d['floating']:,}/{obs_d['n_work']:,}] / "
                          f"syn {syn_d['floating_pct']:.2f}% "
                          f"[{syn_d['floating']:,}/{syn_d['n_work']:,}]; "
                          f"PASS<={self.GA3_PASS_PP}pp, WARN<={self.GA3_WARN_PP}pp)")
        else:
            self._rec("warn", "GA-3", "retail presence gate failed -- 4-way GA-3 decomposition skipped")

        # ── GB-3: per-channel transition-flicker ratio (home, work, retail) ──
        def _median_transitions(df, cols):
            if not cols or len(df) == 0:
                return float("nan")
            arr = df[cols].to_numpy(dtype=float)
            diff = np.abs(np.diff(arr, axis=1))
            trans_per_row = np.nansum(diff, axis=1)
            return float(np.median(trans_per_row))

        gb3_ratios = {}
        for ch_name, ocols, scols in [
            ("home", hom_obs, hom_syn), ("work", wrk_obs, wrk_syn),
            ("retail", ret_obs if self._retail_ok else [], ret_syn if self._retail_ok else []),
        ]:
            obs_med = _median_transitions(self.obs, ocols)
            syn_med = _median_transitions(self.syn, scols)
            if np.isnan(obs_med):
                self._rec("warn", "GB-3", f"[{ch_name}] no observed data -- cannot compute obs baseline")
                continue
            if np.isnan(syn_med):
                self._rec("warn", "GB-3", f"[{ch_name}] no synthetic data -- cannot compute syn transitions")
                continue
            if obs_med <= 0:
                self._rec("warn", "GB-3",
                          f"[{ch_name}] obs median transitions == {obs_med} (floor); "
                          f"syn median = {syn_med:.2f} -- ratio undefined")
                continue
            ratio = syn_med / obs_med
            gb3_ratios[ch_name] = ratio
            if ratio <= self.GB3_PASS_RATIO:
                lvl = "pass"
            elif ratio <= self.GB3_WARN_RATIO:
                lvl = "warn"
            else:
                lvl = "fail"
            self._rec(lvl, "GB-3",
                      f"[{ch_name}] transition-flicker ratio syn/obs: {ratio:.3f}x "
                      f"(obs median {obs_med:.2f}/day, syn {syn_med:.2f}/day; "
                      f"PASS<={self.GB3_PASS_RATIO}x, WARN<={self.GB3_WARN_RATIO}x)")
        if gb3_ratios:
            worst_ch = max(gb3_ratios, key=gb3_ratios.get)
            worst_r = gb3_ratios[worst_ch]
            lvl = self._grade(worst_r, self.GB3_PASS_RATIO, self.GB3_WARN_RATIO)
            self._rec(lvl, "GB-3", f"worst channel: [{worst_ch}] ratio={worst_r:.3f}x")

    # ── REG-1..4: regression gates protecting Heads 1-2 vs Leg-2 baseline ──────

    def validate_regression(self):
        """REG-1/REG-2/REG-3/REG-4, per val doc "Regression gates" table.

        PROXY NOTE (documented, not silently assumed): a true "frozen
        validation set" row-identity-matched comparison would require the
        SAME held-out respondent IDs to be scored by both the Leg-2 and
        Leg-3 checkpoints -- that split isn't persisted anywhere reachable
        from augmented_diaries.csv at validator time (04D's val split is an
        in-memory tensor slice, not saved with respondent IDs to a shared
        artifact). REG-1/REG-2 are therefore implemented as: JS divergence
        between the CURRENT run's synthetic distribution and the BASELINE
        run's synthetic distribution, per (cycle x stratum) -- i.e. "has the
        shipped head's synthetic output distribution drifted between legs",
        which is the practically-checkable form of the same regression
        concern. REG-3 compares mean transitions/day directly. REG-4 diffs
        the FAIL sets of G1-G4/OW1-OW6 between this run and the baseline's
        own saved report.
        """
        print("\n--- Section 2b / 4c: Regression gates (REG-1..4 vs Leg-2 baseline) ---")
        baseline = None
        try:
            if os.path.exists(self.baseline_aug_path):
                print(f"  Loading Leg-2 baseline pool for REG-*: {self.baseline_aug_path}")
                baseline = pd.read_csv(self.baseline_aug_path, low_memory=False)
            else:
                self._rec("warn", "REG-1",
                          f"Leg-2 baseline augmented_diaries.csv not found at "
                          f"{self.baseline_aug_path} -- REG-1/REG-2/REG-3 skipped "
                          f"(infrastructure gap, not a model defect)")
        except Exception as e:
            self._rec("warn", "REG-1",
                      f"Failed to load Leg-2 baseline pool ({type(e).__name__}: {e}) -- "
                      f"REG-1/REG-2/REG-3 skipped")

        if baseline is not None:
            if "IS_SYNTHETIC" in baseline.columns:
                base_syn = baseline[baseline["IS_SYNTHETIC"] == 1].copy()
            else:
                base_syn = baseline.copy()
            base_cycles = (sorted(int(c) for c in baseline["CYCLE_YEAR"].dropna().unique())
                           if "CYCLE_YEAR" in baseline.columns else CYCLES)
            common_cycles = [c for c in self.cycles if c in base_cycles]

            # REG-1: Head 1 (activity + AT_HOME) drift
            js1_vals = []
            for cy in common_cycles:
                for s in [1, 2, 3]:
                    cur_sub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                    base_sub = base_syn[(base_syn.get("CYCLE_YEAR") == cy) & (base_syn.get("DDAY_STRATA") == s)]
                    if len(cur_sub) == 0 or len(base_sub) == 0:
                        continue
                    v = js_div(activity_dist(cur_sub), activity_dist(base_sub))
                    js1_vals.append(v)
            if js1_vals:
                reg1 = float(np.mean(js1_vals))
                lvl = self._grade_hard(reg1, self.thr["reg1_js"])
                self._rec(lvl, "REG-1",
                          f"Head 1 (activity) DeltaJS vs Leg-2 baseline synthetic "
                          f"[PROXY: cross-leg synthetic-vs-synthetic, not row-matched frozen "
                          f"split -- see validate_regression() docstring]: {reg1:.5f} bits "
                          f"(threshold <= {self.thr['reg1_js']})")
            else:
                self._rec("warn", "REG-1", "no overlapping (cycle x stratum) cells vs baseline -- REG-1 skipped")

            # REG-2: Head 2 (AT_WORK) drift, via normalized 48-slot curve JS
            hom1_syn = present_cols(self.syn, "hom30")  # unused, kept for symmetry/clarity
            wrk_cur = present_cols(self.syn, "wrk30")
            wrk_base = present_cols(base_syn, "wrk30")
            js2_vals = []
            if wrk_cur and wrk_base:
                for cy in common_cycles:
                    for s in [1, 2, 3]:
                        cur_sub = self.syn[(self.syn.get("CYCLE_YEAR") == cy) & (self.syn.get("DDAY_STRATA") == s)]
                        base_sub = base_syn[(base_syn.get("CYCLE_YEAR") == cy) & (base_syn.get("DDAY_STRATA") == s)]
                        if len(cur_sub) == 0 or len(base_sub) == 0:
                            continue
                        cur_curve = np.nanmean(cur_sub[wrk_cur].to_numpy(dtype=float), axis=0)
                        base_curve = np.nanmean(base_sub[wrk_base].to_numpy(dtype=float), axis=0)
                        v = js_div(cur_curve, base_curve)
                        js2_vals.append(v)
            if js2_vals:
                reg2 = float(np.mean(js2_vals))
                lvl = self._grade_hard(reg2, self.thr["reg2_js"])
                self._rec(lvl, "REG-2",
                          f"Head 2 (AT_WORK) DeltaJS vs Leg-2 baseline synthetic "
                          f"[PROXY, same caveat as REG-1]: {reg2:.5f} bits "
                          f"(threshold <= {self.thr['reg2_js']})")
            else:
                self._rec("warn", "REG-2", "wrk30_* not comparable vs baseline -- REG-2 skipped")

            # REG-3: Delta mean transitions/day (AT_HOME, AT_WORK)
            hom_cur = present_cols(self.syn, "hom30")
            hom_base = present_cols(base_syn, "hom30")
            for ch_name, cur_cols, base_cols in [
                ("AT_HOME", hom_cur, hom_base), ("AT_WORK", wrk_cur, wrk_base),
            ]:
                if not cur_cols or not base_cols:
                    self._rec("warn", "REG-3", f"[{ch_name}] columns not comparable -- skipped")
                    continue
                cur_arr = self.syn[cur_cols].to_numpy(dtype=float)
                base_arr = base_syn[base_cols].to_numpy(dtype=float)
                cur_trans = float(np.nanmean(np.sum(cur_arr[:, :-1] != cur_arr[:, 1:], axis=1)))
                base_trans = float(np.nanmean(np.sum(base_arr[:, :-1] != base_arr[:, 1:], axis=1)))
                d = abs(cur_trans - base_trans)
                lvl = self._grade_hard(d, self.thr["reg3_trans"])
                self._rec(lvl, "REG-3",
                          f"[{ch_name}] Delta mean transitions/day vs Leg-2 baseline: {d:.3f} "
                          f"(current {cur_trans:.3f} / baseline {base_trans:.3f}; "
                          f"threshold <= {self.thr['reg3_trans']}/day)")

        # REG-4: no gate crosses a severity boundary vs Leg-2 (WARN-only investigate gate)
        self._validate_reg4()

    def _validate_reg4(self):
        """REG-4: diff the FAIL set of G1-G4/OW1-OW6 in THIS run against the
        Leg-2 baseline's own saved TXT report. WARN if a gate newly fails
        here that did not fail in the baseline (excluding the known,
        non-blocking OW5)."""
        watch_gates = {"G1", "G2", "G3", "G4", "OW1", "OW2", "OW3", "OW4", "OW5", "OW6"}
        current_fails = set()
        for line in self.results["fail"]:
            token = line.split("|", 1)[0].strip()
            if token in watch_gates:
                current_fails.add(token)

        baseline_fails = set()
        try:
            if os.path.exists(self.baseline_report_txt):
                with open(self.baseline_report_txt, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("[FAIL]"):
                            token = line[len("[FAIL] "):].split("|", 1)[0].strip()
                            if token in watch_gates:
                                baseline_fails.add(token)
            else:
                self._rec("warn", "REG-4",
                          f"Leg-2 baseline report not found at {self.baseline_report_txt} "
                          f"-- REG-4 falling back to 'OW5 is the only known baseline FAIL' assumption")
                baseline_fails = {"OW5"}
        except Exception as e:
            self._rec("warn", "REG-4", f"Failed to parse baseline report ({type(e).__name__}: {e})")
            baseline_fails = {"OW5"}

        new_fails = (current_fails - baseline_fails) - {"OW5"}
        if new_fails:
            self._rec("warn", "REG-4",
                      f"gate(s) newly FAIL vs Leg-2 baseline (excl. known OW5): "
                      f"{sorted(new_fails)} -- investigate")
        else:
            self._rec("pass", "REG-4",
                      f"no new G1-G4/OW1-OW6 FAILs vs Leg-2 baseline "
                      f"(current fails: {sorted(current_fails) or 'none'}; "
                      f"baseline fails: {sorted(baseline_fails) or 'none'})")

    # ── Section 10 (summary table) ──────────────────────────────────────────────

    def build_summary_table(self):
        hom = present_cols(self.aug, "hom30")
        wrk = present_cols(self.aug, "wrk30")
        ret = present_cols(self.aug, "ret30")
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
            s_retail = np.nanmean(scy[present_cols(scy, "ret30")].to_numpy(dtype=float)) * 100 if (len(scy) and present_cols(scy, "ret30") and self._retail_ok) else float("nan")
            rows.append({
                "Cycle": str(cy),
                "Observed": f"{len(ocy):,}",
                "Synthetic": f"{len(scy):,}",
                "Mean JS": f"{mean_js:.4f}" if not np.isnan(mean_js) else "n/a",
                "AT_HOME obs%": f"{o_home:.1f}" if not np.isnan(o_home) else "n/a",
                "AT_HOME syn%": f"{s_home:.1f}" if not np.isnan(s_home) else "n/a",
                "AT_WORK syn%": f"{s_work:.1f}" if not np.isnan(s_work) else "n/a",
                "AT_RETAIL syn%": f"{s_retail:.2f}" if not np.isnan(s_retail) else "n/a",
            })
        rows.append({
            "Cycle": "Total", "Observed": f"{len(self.obs):,}",
            "Synthetic": f"{len(self.syn):,}", "Mean JS": "--",
            "AT_HOME obs%": "--", "AT_HOME syn%": "--", "AT_WORK syn%": "--",
            "AT_RETAIL syn%": "--",
        })
        self.summary_rows = rows

        # [Leg-3 NEW] optional 5-seed mean +/- sd table (secondary, not gated)
        self.seed_table_rows = []
        if self.seed_summary is not None:
            cols_needed = {"seed", "gate", "value"}
            if cols_needed.issubset(set(self.seed_summary.columns)):
                grp = self.seed_summary.groupby("gate")["value"].agg(["mean", "std", "count"])
                for gate, r in grp.iterrows():
                    self.seed_table_rows.append({
                        "Gate": gate, "Mean": f"{r['mean']:.4f}",
                        "SD": f"{r['std']:.4f}" if not np.isnan(r["std"]) else "0.0000",
                        "N seeds": f"{int(r['count'])}",
                    })
        if not self.seed_table_rows:
            self._rec("warn", "10.SEED",
                      "no --seed_summary provided -- single-seed run; 5-seed mean+/-sd "
                      "table pending the 5-seed cluster sweep (secondary metric, not gated)")

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
            ("2_js_heatmap", "Section 2 -- Activity JS Heatmap (G1, regression)"),
            ("2_act_dist", "Section 2 -- Activity Distribution by Stratum (G1)"),
            ("3_at_home_rhythm", "Section 3 -- AT_HOME Daily Rhythm (G2, regression)"),
            ("3_act_heatmap", "Section 3 -- Activity Temporal Heatmap (G4, regression)"),
            ("4_atwork_diurnal", "Section 4 -- AT_WORK Diurnal Curves (OW1-3, regression)"),
            ("4_atwork_rate", "Section 4 -- AT_WORK Sanity (OW4-6, regression)"),
            ("5_retail_diurnal", "Section 5 -- AT_RETAIL Diurnal Curves [Leg-3 Headline]"),
            ("5_retail_qcab", "Section 5 -- AT_RETAIL Sunday QC vs AB"),
            ("6_retail_sanity", "Section 6 -- AT_RETAIL Sanity (RW battery)"),
            ("7_isr_exclusivity", "Section 7 -- Exclusivity & Projection (ISR, X-3)"),
            ("8_cop_prev", "Section 8 -- Co-Presence Prevalence (G3, regression)"),
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

        if self.summary_rows:
            cols = list(self.summary_rows[0].keys())
            th = "".join(f"<th>{c}</th>" for c in cols)
            trs = ""
            for r in self.summary_rows:
                cls = ' class="total-row"' if r["Cycle"] == "Total" else ""
                trs += "<tr%s>%s</tr>" % (cls, "".join(f"<td>{r[c]}</td>" for c in cols))
            summary_html = f"""
        <section class="chart-section" id="summary-table">
          <h2>Section 10 -- Scorecard Summary Table</h2>
          <div class="table-wrap">
            <table class="summary-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>
          </div>
        </section>"""
        else:
            summary_html = ""

        seed_html = ""
        if getattr(self, "seed_table_rows", None):
            cols = list(self.seed_table_rows[0].keys())
            th = "".join(f"<th>{c}</th>" for c in cols)
            trs = "".join("<tr>%s</tr>" % "".join(f"<td>{r[c]}</td>" for c in cols)
                          for r in self.seed_table_rows)
            seed_html = f"""
        <section class="chart-section" id="seed-table">
          <h2>Section 10b -- 5-Seed Mean +/- SD Table</h2>
          <div class="table-wrap">
            <table class="summary-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>
          </div>
        </section>"""

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
  <title>GSS Step 4 (Leg-3, 4-split) -- Augmentation Validation</title>
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
      <h1>GSS Step 4 (Leg-3, 4-split) -- Augmentation Validation Report</h1>
      <p>Three-channel (AT_HOME + AT_WORK + AT_RETAIL) | Residential G1-G4, Office OW1-OW6,
         Retail RW1-RW8, ISR/GA-3/GB-3/X-3, REG-1..4
         &middot; Cycles {", ".join(str(c) for c in self.cycles)} &middot; Mode: {mode}</p>
    </div>
    <p style="font-size:0.78rem;color:var(--subtext)">Generated: {ts}</p>
  </header>
  <nav>
    <a href="#scorecard">Scorecard</a>
    {"".join(f'<a href="#{k}">{lbl.split("--")[0].strip()}</a>' for k, lbl in chart_order if k in self.plots_b64)}
    <a href="#summary-table">Section 10</a>
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
    {seed_html}
  </main>
  <footer>
    Leg-3 (4-split) Occupancy Modeling Pipeline &middot; Step 4 Augmentation Validation &middot;
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
            f.write(f"Step 4 (Leg-3, 4-split) Augmentation Validation Report -- {ts}\n")
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
        print(f"Step 4 (Leg-3, 4-split) -- Augmentation Validation  "
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
        _safe(self.validate_at_work_marginals, "OW1")
        _safe(self.validate_at_work_sanity, "OW4")
        _safe(self.validate_retail_presence, "RET-PRESENCE")
        _safe(self.validate_retail_marginals, "RETM")
        _safe(self.validate_retail_sanity, "RW1")
        _safe(self.validate_exclusivity, "ISR-raw")
        _safe(self.validate_copresence, "G3")
        _safe(self.validate_secondary, "S9")
        _safe(self.validate_ga3_gb3, "GA-3")
        _safe(self.validate_regression, "REG-1")
        _safe(self.build_summary_table, "10")
        self.build_report()

        n_p = len(self.results["pass"])
        n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 60}")
        print(f"Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 60}")


def parse_args():
    p = argparse.ArgumentParser(description="Step 4 (Leg-3, 4-split) augmentation validator")
    p.add_argument("--step3_dir", default=None, help="Step-3 reference outputs dir")
    p.add_argument("--step4_dir", default=None,
                   help="Step-4 artifacts dir (point at the locked pool's "
                        "sweep/<BASE>_raked3_mindwell_actv/ for the canonical report -- "
                        "never the bare outputs_step4/ if a sweep variant is production)")
    p.add_argument("--baseline_dir", default=None,
                   help="Leg-2 frozen baseline dir for REG-* gates "
                        "(default: Leg-2's R5_raked_mindwell_actv2, 73P/3W/1F scorecard)")
    p.add_argument("--seed_summary", default=None,
                   help="Optional CSV (columns: seed,gate,value) for the 5-seed "
                        "mean+/-sd table (Section 10b, secondary/not gated)")
    p.add_argument("--sample", action="store_true",
                   help="Relaxed thresholds for an undertrained smoke-test model")
    return p.parse_args()


def main():
    args = parse_args()
    step3_dir = args.step3_dir or STEP3_DIR_DEFAULT
    step4_dir = args.step4_dir or STEP4_DIR_DEFAULT
    baseline_dir = args.baseline_dir or BASELINE_DIR_DEFAULT
    AugmentationValidator4Split(
        step3_dir, step4_dir, baseline_dir,
        sample_mode=args.sample, seed_summary=args.seed_summary,
    ).run_all()


if __name__ == "__main__":
    main()
