"""
3rdJ_06_longitudinalForecasting_2split_val.py
Step 6 (Leg-2 2-split) — Two-Channel Longitudinal Forecasting: Validation & Report Generator.

Validates the outputs of 3rdJ_06_longitudinalForecasting_2split.py: dual-channel
(AT_HOME + AT_WORK) 2022 backcasting reconstruction, DRIFT_MATRIX plausibility across
the three cycle-transition matrices, 2030 three-band (conservative/hybrid/fullyhybrid)
schedule plausibility on both channels, and BEM output readiness. Produces a
self-contained HTML report with embedded base64 PNG charts.

Modeled on eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecastingGSS_val.py
(class layout, base64-matplotlib embedding, section_html() builder, PASS/WARN/FAIL scorecard),
extended to two channels x three bands per
3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/3rdJ_06_longitudinalForecasting_2split_val.md.

Sections 1-2 (training convergence, True Future Test) have NO per-epoch CSV — only
prose numbers transcribed from the training Progress Log
(3rdJ_06_longitudinalForecasting_2split.md). Those sections are rendered as INFO-only
tables, never fabricated PASS/FAIL.

Sections 3-6 are computed directly from the on-disk CSV artifacts, per-channel and
per-band, honestly reporting whatever the data shows (including FAILs where the
training log's own diagnostics already document a known artifact).

Usage:
    py 3rdJ_06_longitudinalForecasting_2split_val.py
    py 3rdJ_06_longitudinalForecasting_2split_val.py --forecast_dir <dir> --step4_raked_dir <dir> --outputs_dir <dir>
"""

from __future__ import annotations

import argparse
import base64
import io
import sys
import warnings
from datetime import datetime
from pathlib import Path

# Windows consoles default to cp1252; this file's print() calls use em-dashes/arrows.
# Reconfigure stdout/stderr to UTF-8 so console output doesn't mangle (best-effort — the
# HTML report itself is always written with explicit encoding="utf-8" regardless).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance, ks_2samp, entropy

warnings.filterwarnings("ignore")

# ── Constants ─────────────────────────────────────────────────────────────────
ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK_COLS = [f"wrk30_{i:03d}" for i in range(1, 49)]
STRATUM_LABEL = {1: "WD", 2: "Sat", 3: "Sun"}
BANDS = ["conservative", "hybrid", "fullyhybrid"]
BAND_LABEL = {"conservative": "A (conservative)", "hybrid": "B (hybrid)", "fullyhybrid": "C (fullyhybrid)"}
BIZ_SLOTS_0IDX = list(range(10, 26))  # slots 11-26 1-indexed = 09:00-17:00
SLEEP_CODE = 5  # raw act30 code 5 = Sleep & Naps (confirmed empirically: dominates slots 1-9)
WORK_ACT_CODE = 1  # raw act30 code 1 = Work

# WFH_RATE thresholds per band (Section 5.17-5.19), from the spec doc
WFH_TARGET = {"conservative": (0.15, 0.20), "hybrid": (0.25, 0.35), "fullyhybrid": (0.35, 0.45)}


# ── Small helpers ──────────────────────────────────────────────────────────────

def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _status_html(status: str) -> str:
    colors = {"PASS": "#2e7d32", "WARN": "#e65100", "FAIL": "#c62828", "INFO": "#1565c0"}
    c = colors.get(status, "#555")
    return f"<span style='color:{c};font-weight:bold'>{status}</span>"


def js_divergence(p, q, eps=1e-12):
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = np.clip(p / (p.sum() + eps), eps, None)
    q = np.clip(q / (q.sum() + eps), eps, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def kl_divergence(p, q, eps=1e-12):
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = np.clip(p / (p.sum() + eps), eps, None)
    q = np.clip(q / (q.sum() + eps), eps, None)
    return float(entropy(p, q))


def compute_wfh_rate(df: pd.DataFrame) -> float:
    """
    Exact replica of compute_wfh_rate() in 3rdJ_06_longitudinalForecasting_2split.py:
    WFH_RATE = mean(hom30_k==1 OR act30_k==Work) over business-hours slots k in {11..26}
    (1-indexed), restricted to employed respondents (LFTAG == 1).
    """
    if "LFTAG" in df.columns:
        emp = df[df["LFTAG"] == 1]
    else:
        emp = df
    if len(emp) == 0:
        return float("nan")
    h_arr = emp[HOM_COLS].values.astype(float)
    a_arr = emp[ACT_COLS].values.astype(float)
    biz = BIZ_SLOTS_0IDX
    h_biz = h_arr[:, biz]
    a_biz = a_arr[:, biz]
    home_or_wact = (h_biz == 1) | (a_biz == WORK_ACT_CODE)
    return float(home_or_wact.mean())


def compute_wfh_day_share(df: pd.DataFrame) -> float:
    """
    Day-level WFH classifier used by the training script's `_posthoc_reweight()`
    (per the training Progress Log, 2026-06-24 Fix-B entry): a diary is a "WFH-day"
    if its business-hours (slots 11-26) mean AT_HOME >= 0.50. This is the metric the
    2030 bands were actually TARGETED to (~17.5/30/40%) and is DIFFERENT from
    compute_wfh_rate() (the literal Section 4.9/5.16-5.19 "WFH_RATE" gate formula,
    which the training log documents as "nearly flat... invariant by design").
    Restricted to employed (LFTAG==1) respondents, matching compute_wfh_rate().
    """
    if "LFTAG" in df.columns:
        emp = df[df["LFTAG"] == 1]
    else:
        emp = df
    if len(emp) == 0:
        return float("nan")
    h_arr = emp[HOM_COLS].values.astype(float)
    biz = BIZ_SLOTS_0IDX
    day_home_frac = h_arr[:, biz].mean(axis=1)
    return float((day_home_frac >= 0.50).mean())


def top5_activities(act_flat: np.ndarray) -> pd.Series:
    vc = pd.Series(act_flat).value_counts(normalize=True)
    return vc.sort_values(ascending=False).head(5)


def run_lengths(binary_seq: np.ndarray) -> list:
    """Contiguous run-lengths of 1s in a 1-D 0/1 array."""
    runs = []
    cur = 0
    for v in binary_seq:
        if v == 1:
            cur += 1
        else:
            if cur > 0:
                runs.append(cur)
            cur = 0
    if cur > 0:
        runs.append(cur)
    return runs


def transition_matrix_2x2(mat: np.ndarray) -> np.ndarray:
    """mat: (N,48) binary. Returns 2x2 row-normalized transition prob matrix pooled over rows."""
    counts = np.zeros((2, 2))
    for row in mat:
        for t in range(len(row) - 1):
            counts[int(row[t]), int(row[t + 1])] += 1
    rowsum = counts.sum(axis=1, keepdims=True)
    rowsum[rowsum == 0] = 1
    return counts / rowsum


def acf(series: np.ndarray, max_lag: int) -> np.ndarray:
    series = series - series.mean()
    n = len(series)
    denom = np.sum(series ** 2)
    out = []
    for lag in range(1, max_lag + 1):
        if denom == 0 or lag >= n:
            out.append(0.0)
            continue
        out.append(float(np.sum(series[:-lag] * series[lag:]) / denom))
    return np.array(out)


def manual_logreg_cv(X: np.ndarray, y: np.ndarray, n_folds: int = 5, epochs: int = 500,
                      lr: float = 0.1, l2: float = 1e-2, seed: int = 0) -> float:
    """
    Minimal numpy-only logistic regression with k-fold CV, standing in for a C2ST
    classifier (xgboost is outside this validator's allowed dependency list:
    pandas/numpy/scipy/matplotlib only). Returns mean held-out accuracy.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    idx = rng.permutation(n)
    folds = np.array_split(idx, n_folds)
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd[sd == 0] = 1.0
    Xn = (X - mu) / sd
    accs = []
    for k in range(n_folds):
        test_idx = folds[k]
        train_idx = np.concatenate([folds[j] for j in range(n_folds) if j != k])
        if len(test_idx) == 0 or len(train_idx) == 0:
            continue
        Xtr, ytr = Xn[train_idx], y[train_idx]
        Xte, yte = Xn[test_idx], y[test_idx]
        w = np.zeros(Xtr.shape[1])
        b = 0.0
        for _ in range(epochs):
            z = Xtr @ w + b
            p = 1.0 / (1.0 + np.exp(-z))
            grad_w = Xtr.T @ (p - ytr) / len(ytr) + l2 * w
            grad_b = np.mean(p - ytr)
            w -= lr * grad_w
            b -= lr * grad_b
        z = Xte @ w + b
        pred = (1.0 / (1.0 + np.exp(-z))) >= 0.5
        accs.append(float(np.mean(pred == yte)))
    return float(np.mean(accs)) if accs else float("nan")


def row_summary_features(df: pd.DataFrame) -> np.ndarray:
    """10 lightweight per-row summary features for the manual C2ST classifier."""
    hom = df[HOM_COLS].values.astype(float)
    wrk = df[WRK_COLS].values.astype(float)
    act = df[ACT_COLS].values.astype(float)
    biz = BIZ_SLOTS_0IDX
    night = list(range(0, 8))
    feats = np.column_stack([
        hom.mean(axis=1),
        wrk.mean(axis=1),
        hom[:, biz].mean(axis=1),
        wrk[:, biz].mean(axis=1),
        hom[:, night].mean(axis=1),
        wrk[:, night].mean(axis=1),
        (act == SLEEP_CODE)[:, night].mean(axis=1),
        (act == WORK_ACT_CODE).mean(axis=1),
        np.abs(np.diff(hom, axis=1)).sum(axis=1),
        np.abs(np.diff(wrk, axis=1)).sum(axis=1),
    ])
    return feats


# ── Validator ──────────────────────────────────────────────────────────────────

class LongitudinalForecastingValidator2Split:

    def __init__(self, forecast_dir: str, step4_raked_dir: str, outputs_dir: str):
        self.forecast_dir = Path(forecast_dir)
        self.step4_raked_dir = Path(step4_raked_dir)
        self.outputs_dir = Path(outputs_dir)
        self.checks: dict[str, list[dict]] = {}
        self.charts: dict[str, str] = {}
        self._load_data()

    # ── check bookkeeping ────────────────────────────────────────────────────

    def add(self, section: str, check_id: str, desc: str, channel: str, band: str,
            observed, threshold: str, status: str, note: str = "") -> None:
        self.checks.setdefault(section, []).append({
            "id": check_id, "desc": desc, "channel": channel, "band": band,
            "observed": observed, "threshold": threshold, "status": status, "note": note,
        })
        obs_str = f"{observed:.4f}" if isinstance(observed, float) else str(observed)
        print(f"  [{status}] {check_id} {desc} ({channel}/{band}): {obs_str} vs {threshold}")

    # ── data loading ──────────────────────────────────────────────────────────

    def _load_data(self) -> None:
        print("Loading data ...")

        # 2030 deliverable (Sections 5, 6) — ~70MB, OK to load fully
        p = self.forecast_dir / "2030_synthetic_diaries_2split_calibrated_mindwell_C.csv"
        self.synth_2030 = pd.read_csv(p) if p.exists() else None
        if self.synth_2030 is not None:
            print(f"  Loaded {p.name} ({len(self.synth_2030):,} rows)")
        else:
            print(f"  [WARN] {p} not found — Sections 5/6 will be skipped")

        # Reconstructed 2022 (Section 4) — 37 rows, no DDAY_STRATA of its own
        p = self.forecast_dir / "reconstructed_2022_diaries_2split.csv"
        self.recon_2022 = pd.read_csv(p) if p.exists() else None
        if self.recon_2022 is not None:
            print(f"  Loaded {p.name} ({len(self.recon_2022):,} rows, no DDAY_STRATA column)")
        else:
            print(f"  [WARN] {p} not found — Section 4 will be skipped")

        # DRIFT matrices (Section 3) — wide format, one row per stratum
        self.dm = {}
        for name in ("DRIFT_MATRIX_0510_2split", "DRIFT_MATRIX_1015_2split", "DRIFT_MATRIX_1522_2split"):
            p = self.forecast_dir / f"{name}.csv"
            if p.exists():
                self.dm[name] = pd.read_csv(p)
                print(f"  Loaded {name}.csv ({len(self.dm[name])} rows)")
            else:
                print(f"  [WARN] {p} not found — Section 3 checks for {name} skipped")

        # Observed 2022 baseline — 545MB, MUST be read in chunks
        p = self.step4_raked_dir / "augmented_diaries.csv"
        if p.exists():
            usecols = HOM_COLS + WRK_COLS + ACT_COLS + ["CYCLE_YEAR", "DDAY_STRATA", "LFTAG"]
            usecols = list(dict.fromkeys(usecols))
            chunks = []
            n_scanned = 0
            for chunk in pd.read_csv(p, usecols=lambda c: c in usecols, chunksize=20000):
                n_scanned += len(chunk)
                sub = chunk[chunk["CYCLE_YEAR"] == 2022]
                if len(sub) > 0:
                    chunks.append(sub)
            self.obs_2022 = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
            print(f"  Loaded observed 2022 from {p} via chunked read "
                  f"(scanned {n_scanned:,} rows total, kept {len(self.obs_2022):,} 2022 rows)")
        else:
            self.obs_2022 = None
            print(f"  [WARN] {p} not found — observed-2022 reference unavailable")

    # ══════════════════════════════════════════════════════════════════════
    # Section 1 — Training Convergence (INFO only — transcribed, not computed)
    # ══════════════════════════════════════════════════════════════════════

    def validate_training_convergence(self) -> None:
        print("\n[Section 1] Training convergence (INFO — transcribed from training log) ...")
        rows = [
            ("Anti-copy Gate 1: slot-disagreement fraction (job 987039, full 30.5h run)",
             "0.6693", "no fixed target — diagnostic vs. a near-0% copier baseline",
             "Confirms the cross-day KNN-pairing fix (Fix A) eliminated the self-pairing "
             "copier identified 2026-06-24; a copier would score near 0."),
            ("Anti-copy Gate 2: JS home/work sign & finiteness (job 987039)",
             "finite, non-degenerate (no -0.0000 artifact)", "must be finite and >= 0",
             "The pre-fix run had val_js=0.0000 at epoch 1 of every stage (mathematically "
             "impossible) — this is the corrected state."),
            ("Smoke-test epoch-1 task losses, home / work (--smoke --stage A, tiny SAMPLE.csv "
             "— NOT the full-corpus run)",
             "home=0.5019, work=1.0386", "n/a — smoke-test only, informational",
             "Full-corpus per-epoch losses were not persisted to any CSV."),
            ("Smoke-test anti-copy Gate 3: epoch-1 val_js range / loss range (smoke only)",
             "val_js 0.209-0.219, loss 0.640-0.643", "n/a — smoke-test only, informational", ""),
            ("PCGrad + uncertainty-weighting (uw) active on the full run",
             "confirmed applied (Fix bundle, job 987039): fp32 PCGrad path mirrors 04D "
             "exactly (task-loss backward, diversity-loss grad, UW log_var grad)",
             "both flags present", "WEIGHT_MODE='uw' / USE_PCGRAD=1 are code-level flags "
             "confirmed by the fix-bundle diff, not checkpoint metadata (checkpoints store "
             "only weights, no embedded metrics per this task's inventory)."),
            ("Per-checkpoint final val JS (W_2005 / W_2010_ft / W_2015_ft / W_pooled_2030), "
             "home & work, per DDAY_STRATA",
             "n/a &mdash; see training log", "n/a",
             "No per-checkpoint validation-JS table was transcribed to the Progress Log for "
             "the full-corpus run; only aggregate band-level 2030 outputs and the corrected "
             "backcast profile-JS (Section 4 of this report) were logged. Do NOT infer a "
             "PASS/FAIL from this — the number was never recorded, not merely omitted here."),
        ]
        for desc, val, thr, note in rows:
            self.add("s1", "1.x", desc, "both", "n/a", val, thr, "INFO", note)

    # ══════════════════════════════════════════════════════════════════════
    # Section 2 — True Future Test (INFO only — no per-phase JS was logged)
    # ══════════════════════════════════════════════════════════════════════

    def validate_true_future_test(self) -> None:
        print("\n[Section 2] True Future Test (INFO — no per-phase JS was transcribed) ...")
        self.add("s2", "2.x",
                  "True Future Test JS per phase (W_2005-on-2010 / W_2010_ft-on-2015 / "
                  "W_2015_ft-on-2022) x DDAY_STRATA x channel",
                  "both", "n/a", "n/a &mdash; see training log", "n/a", "INFO",
                  "The Section-2 design (Phase 1 apply W_2005_2split to 2010 held-out, "
                  "Phase 2 W_2010_ft on 2015 held-out, Phase 3 W_2015_ft on 2022 held-out) is "
                  "specified in 3rdJ_06_longitudinalForecasting_2split.md lines 180-482, but no "
                  "concrete per-phase JS numbers were transcribed into the Progress Log for the "
                  "full-corpus run — only the DRIFT_MATRIX files (Section 3 below) and the "
                  "final backcast (Section 4) were recorded as artifacts.")
        if self.dm:
            proxy = []
            for name in self.dm:
                wd = self.dm[name][self.dm[name]["stratum"] == 1]
                if len(wd) > 0:
                    proxy.append(f"{name.replace('DRIFT_MATRIX_', '').replace('_2split','')}: "
                                 f"aggregate_JS(WD)={float(wd['aggregate_JS'].iloc[0]):.4f}")
            self.add("s2", "2.y",
                      "Nearest available proxy: DRIFT_MATRIX aggregate_JS at WD stratum (model "
                      "applied to the NEXT cycle's held-out data at temperature=0.0) &mdash; "
                      "NOT the literal Section-2 TFT gate, shown for cross-reference only",
                      "both", "n/a", "; ".join(proxy), "n/a (informational)", "INFO",
                      "aggregate_JS here is a 14-activity JS divergence on greedy-decoded "
                      "generation vs. the next cycle's observed activities; it is conceptually "
                      "adjacent to a True Future Test but is not computed per the Section-2 "
                      "spec (which additionally requires a channel split and per-stratum uniform "
                      "baseline comparison). Reported only so the reader has SOME real number "
                      "in this section.")

    # ══════════════════════════════════════════════════════════════════════
    # Section 3 — DRIFT_MATRIX plausibility
    # ══════════════════════════════════════════════════════════════════════

    def validate_drift_matrices(self) -> None:
        print("\n[Section 3] DRIFT_MATRIX plausibility ...")
        note_schema = (
            "Schema note: each DRIFT_MATRIX_*_2split.csv is WIDE with exactly one row per "
            "DDAY_STRATA (3 rows total) — it carries ONE aggregate AT_HOME_drift / "
            "AT_WORK_drift SCALAR per stratum (signed: generated-at-temperature=0.0 minus "
            "observed mean), plus 14 per-activity JS_actNN columns (channel-agnostic, i.e. "
            "not separately split into home/work). This does not match a per-activity x "
            "per-channel matrix; gates 3.1-3.4 below are adapted accordingly: 'non-trivial "
            "(home)' uses the count of the 14 JS_actNN columns exceeding the threshold at the "
            "WD row (closest available per-activity signal), and 'non-trivial (work)' uses the "
            "single AT_WORK_drift scalar's magnitude at the WD row (no per-activity work split "
            "exists in this file)."
        )

        act_cols = None
        for name, dm in self.dm.items():
            act_cols = [c for c in dm.columns if c.startswith("JS_act")]
            wd = dm[dm["stratum"] == 1]
            if len(wd) == 0:
                continue
            n_act_gt = int((wd[act_cols].values.flatten() > 0.01).sum())
            self.add("s3", f"3.{name}-home", f"{name} non-trivial (home, adapted: count of 14 "
                      "JS_actNN cols > 0.01 at WD row)", "home", "n/a", n_act_gt, ">= 3",
                      "PASS" if n_act_gt >= 3 else "WARN", note_schema if name == list(self.dm)[0] else "")
            at_work_wd = float(wd["AT_WORK_drift"].iloc[0])
            self.add("s3", f"3.{name}-work", f"{name} non-trivial (work, adapted: "
                      "|AT_WORK_drift| at WD row)", "work", "n/a", abs(at_work_wd), ">= 0.01",
                      "PASS" if abs(at_work_wd) >= 0.01 else "WARN")

        # 3.5 / 3.6 — dual COVID signal in DRIFT_MATRIX_1522
        if "DRIFT_MATRIX_1015_2split" in self.dm and "DRIFT_MATRIX_1522_2split" in self.dm:
            wd1015 = self.dm["DRIFT_MATRIX_1015_2split"]
            wd1522 = self.dm["DRIFT_MATRIX_1522_2split"]
            h1015 = float(wd1015[wd1015["stratum"] == 1]["AT_HOME_drift"].iloc[0])
            h1522 = float(wd1522[wd1522["stratum"] == 1]["AT_HOME_drift"].iloc[0])
            w1522 = float(wd1522[wd1522["stratum"] == 1]["AT_WORK_drift"].iloc[0])
            delta_home = h1522 - h1015
            self.add("s3", "3.5", "DRIFT_MATRIX_1522 COVID home signal: WD AT_HOME_drift(1522) "
                      "- AT_HOME_drift(1015)", "home", "n/a", delta_home, ">= +0.05 (+5pp)",
                      "PASS" if delta_home >= 0.05 else "FAIL",
                      f"AT_HOME_drift WD: 1015={h1015:+.4f}, 1522={h1522:+.4f}. Both "
                      "AT_HOME_drift/AT_WORK_drift are computed with model.generate(..., "
                      "temperature=0.0) (line ~1015 of the training script) &mdash; the "
                      "training log (2026-06-26 entries) already diagnosed that greedy "
                      "(temp=0.0) decoding produces a work-channel latch / wrong-direction "
                      "signature that is NOT present in the temp=0.8 2030 deliverable (job "
                      "1005623 profiled the deliverable directly and found it healthy). This "
                      "gate is scored honestly against the on-disk DRIFT_MATRIX files; a FAIL "
                      "here reflects a known, already-investigated property of this internal "
                      "temp=0.0 diagnostic artifact, not a defect newly discovered in the "
                      "2030 deliverable (see Section 5 for the deliverable's own numbers).")
            self.add("s3", "3.6", "DRIFT_MATRIX_1522 COVID work signal: WD AT_WORK_drift(1522) "
                      "directional decrease (WFH surge mirror)", "work", "n/a", w1522,
                      "< 0 (decrease)", "PASS" if w1522 < 0 else "FAIL",
                      "Same temperature=0.0 caveat as 3.5 above.")

        # 3.7 — NaN/Inf across all 3 matrices
        n_nan = n_inf = 0
        for dm in self.dm.values():
            numeric = dm.select_dtypes(include=[np.number]).values
            n_nan += int(np.isnan(numeric).sum())
            n_inf += int(np.isinf(numeric).sum())
        self.add("s3", "3.7", "All matrices complete: NaN/Inf count across all 3 matrices",
                  "both", "n/a", n_nan + n_inf, "0", "PASS" if (n_nan + n_inf) == 0 else "FAIL")

        # 3.8 — shape consistency
        shapes = {name: dm.shape for name, dm in self.dm.items()}
        consistent = len(set(shapes.values())) <= 1
        self.add("s3", "3.8", "Matrix dimensions consistent across all 3 matrices", "both",
                  "n/a", str(shapes), "all equal", "PASS" if consistent else "FAIL")

        # Charts
        try:
            fig, axes = plt.subplots(2, 3, figsize=(13, 6), sharey="row")
            for col, (name, dm) in enumerate(self.dm.items()):
                ax_h, ax_w = axes[0, col], axes[1, col]
                strata = [STRATUM_LABEL[s] for s in dm["stratum"]]
                ax_h.bar(strata, dm["AT_HOME_drift"], color="#1976d2")
                ax_h.axhline(0, color="#333", linewidth=0.8)
                ax_h.set_title(name.replace("DRIFT_MATRIX_", "").replace("_2split", ""), fontsize=9)
                if col == 0:
                    ax_h.set_ylabel("AT_HOME_drift")
                ax_w.bar(strata, dm["AT_WORK_drift"], color="#e65100")
                ax_w.axhline(0, color="#333", linewidth=0.8)
                if col == 0:
                    ax_w.set_ylabel("AT_WORK_drift")
            fig.suptitle("DRIFT_MATRIX signed mean-shift (generated @temp=0.0 minus observed) "
                         "per stratum", fontsize=10)
            plt.tight_layout()
            self.charts["s3_bars"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s3_bars failed: {e}")

        try:
            fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)
            for ax, (name, dm) in zip(axes, self.dm.items()):
                act_cols_ = [c for c in dm.columns if c.startswith("JS_act")]
                mat = dm[act_cols_].values  # (3 strata, 14 acts)
                im = ax.imshow(mat.T, aspect="auto", cmap="YlOrRd", vmin=0, vmax=max(mat.max(), 1e-4))
                ax.set_xticks(range(3)); ax.set_xticklabels([STRATUM_LABEL[s] for s in dm["stratum"]])
                ax.set_yticks(range(len(act_cols_)))
                ax.set_yticklabels([c.split("_", 2)[-1] for c in act_cols_], fontsize=6)
                ax.set_title(name.replace("DRIFT_MATRIX_", "").replace("_2split", ""), fontsize=9)
                plt.colorbar(im, ax=ax, shrink=0.7)
            fig.suptitle("Per-activity JS divergence (14 activities x 3 strata)", fontsize=10)
            plt.tight_layout()
            self.charts["s3_heatmap"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s3_heatmap failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 4 — 2022 Backcasting Reconstruction (joint gate)
    # ══════════════════════════════════════════════════════════════════════

    def validate_backcasting_2022(self) -> None:
        print("\n[Section 4] 2022 backcasting reconstruction (joint) ...")
        if self.recon_2022 is None or self.obs_2022 is None or len(self.obs_2022) == 0:
            print("  [SKIP] reconstructed_2022_diaries_2split.csv or observed 2022 unavailable")
            return

        n_rec = len(self.recon_2022)
        # Row-order alignment convention (identical to verify_backcast_metric_2split.py):
        # reconstructed_2022_diaries_2split.csv has NO DDAY_STRATA of its own; it was written
        # in the row order of the observed-2022 subset. Filter observed 2022 to the SAME file
        # order, take the first n_rec rows, and borrow DDAY_STRATA/LFTAG from that subset.
        obs_aligned = self.obs_2022.iloc[:n_rec].reset_index(drop=True)
        rec = self.recon_2022.iloc[:len(obs_aligned)].reset_index(drop=True)
        align_note = (
            f"Row-order alignment: reconstructed_2022_diaries_2split.csv has no DDAY_STRATA "
            f"column of its own (confirmed: only act30_/hom30_/wrk30_ + CYCLE_YEAR + "
            f"IS_SYNTHETIC, {n_rec} rows). Per the convention already established by "
            f"verify_backcast_metric_2split.py ('reconstruction was written in the order of "
            f"df[CYCLE_YEAR==2022].reset_index'), stratum/LFTAG labels are borrowed from the "
            f"first {len(obs_aligned)} rows of the observed-2022 subset (R5_raked_mindwell_actv2, "
            f"file order preserved via chunked read). Resulting split: "
            f"{obs_aligned['DDAY_STRATA'].value_counts().sort_index().to_dict()}. This "
            f"validator's observed-2022 reference is the newer actv2 rake, which may differ "
            f"in row order from whatever augmented_diaries.csv snapshot was used when this "
            f"reconstruction was originally generated (2026-06-26) — results are reported "
            f"honestly as computed against the CURRENT canonical baseline, not re-derived "
            f"training-log numbers."
        )

        strata = obs_aligned["DDAY_STRATA"].values
        oh = obs_aligned[HOM_COLS].values.astype(float)
        ow = obs_aligned[WRK_COLS].values.astype(float)
        oa = rec_oa = obs_aligned[ACT_COLS].values.astype(int)
        gh = rec[HOM_COLS].values.astype(float)
        gw = rec[WRK_COLS].values.astype(float)
        ga = rec[ACT_COLS].values.astype(int)

        gate_home = {1: 0.10, 2: 0.10, 3: 0.10}
        gate_work = {1: 0.10, 2: 0.15, 3: 0.15}
        for s in [1, 2, 3]:
            m = (strata == s)
            if m.sum() == 0:
                continue
            lbl = STRATUM_LABEL[s]
            ohp, ghp = oh[m].mean(0), gh[m].mean(0)
            owp, gwp = ow[m].mean(0), gw[m].mean(0)
            js_h = js_divergence(ohp, ghp)
            js_w = js_divergence(owp, gwp)
            note = align_note if s == 1 else ""
            self.add("s4", f"4.{s}", f"Reconstruction JS {lbl} (home, marginal profile JS)",
                      "home", "n/a", js_h, f"< {gate_home[s]}",
                      "PASS" if js_h < gate_home[s] else "FAIL", note)
            self.add("s4", f"4.{s+3}", f"Reconstruction JS {lbl} (work, marginal profile JS)",
                      "work", "n/a", js_w, f"< {gate_work[s]}",
                      "PASS" if js_w < gate_work[s] else "FAIL")

        m1 = (strata == 1)
        if m1.sum() > 0:
            r_at = float(gh[m1].mean()) * 100
            o_at = float(oh[m1].mean()) * 100
            diff = abs(r_at - o_at)
            self.add("s4", "4.7", "WD AT_HOME reconstruction", "home", "n/a", diff, "<= 2pp",
                      "PASS" if diff <= 2.0 else ("WARN" if diff <= 4.0 else "FAIL"),
                      f"observed={o_at:.2f}%, reconstructed={r_at:.2f}%")
            r_at_w = float(gw[m1].mean()) * 100
            o_at_w = float(ow[m1].mean()) * 100
            diff_w = abs(r_at_w - o_at_w)
            self.add("s4", "4.8", "WD AT_WORK reconstruction", "work", "n/a", diff_w, "<= 3pp",
                      "PASS" if diff_w <= 3.0 else ("WARN" if diff_w <= 6.0 else "FAIL"),
                      f"observed={o_at_w:.2f}%, reconstructed={r_at_w:.2f}%")

            wfh_obs = compute_wfh_rate(obs_aligned[m1])
            wfh_rec_df = pd.concat([
                pd.DataFrame(gh[m1], columns=HOM_COLS).reset_index(drop=True),
                pd.DataFrame(ga[m1], columns=ACT_COLS).reset_index(drop=True),
                obs_aligned[m1][["LFTAG"]].reset_index(drop=True),
            ], axis=1)
            wfh_rec = compute_wfh_rate(wfh_rec_df)
            diff_wfh = abs(wfh_rec - wfh_obs) * 100
            self.add("s4", "4.9", "WFH_RATE reconstruction (employed, biz-hours slots 11-26)",
                      "both", "n/a", diff_wfh, "<= 5pp",
                      "PASS" if diff_wfh <= 5.0 else "FAIL",
                      f"observed={wfh_obs:.4f}, reconstructed={wfh_rec:.4f}")

        # 4.10 top-5 activities (pooled across all aligned rows)
        top5 = top5_activities(oa.flatten())
        for code, share in top5.items():
            gen_share = float((ga.flatten() == code).mean())
            diff = abs(gen_share - share) * 100
            self.add("s4", f"4.10-act{int(code)}", f"Top-5 activity reconstruction: act code "
                      f"{int(code)} (obs share {share*100:.2f}%)", "activity", "n/a", diff,
                      "<= 2pp", "PASS" if diff <= 2.0 else "FAIL",
                      f"obs={share*100:.2f}%, recon={gen_share*100:.2f}%")

        # 4.11 night sleep
        night_obs = (oa[:, :8] == SLEEP_CODE).mean() * 100
        night_gen = (ga[:, :8] == SLEEP_CODE).mean() * 100
        diff_sleep = abs(night_gen - night_obs)
        self.add("s4", "4.11", "Night sleep reconstruction (slots 1-8, raw code 5)", "activity",
                  "n/a", diff_sleep, "<= 2pp", "PASS" if diff_sleep <= 2.0 else "FAIL",
                  f"obs={night_obs:.2f}%, recon={night_gen:.2f}%")

        # Tier 1/2 office gates (WD only, work channel) — project-chosen thresholds
        if m1.sum() > 2:
            owp, gwp = ow[m1].mean(0), gw[m1].mean(0)
            kl_w = kl_divergence(owp + 1e-9, gwp + 1e-9)
            self.add("s4", "4.12", "KL(work, WD) profile", "work", "n/a", kl_w, "< 0.05",
                      "PASS" if kl_w < 0.05 else "WARN",
                      "Adapted: computed on the 48-slot mean presence profile (treated as a "
                      "distribution over slots), not a literal arrival/departure histogram "
                      "&mdash; the WD sample here is only n=13 rows, too small for a robust "
                      "arrival/departure histogram.")
            slots_pos = np.arange(48)
            emd_w = wasserstein_distance(slots_pos, slots_pos,
                                          u_weights=owp / owp.sum() if owp.sum() > 0 else None,
                                          v_weights=gwp / gwp.sum() if gwp.sum() > 0 else None)
            emd_w_norm = emd_w / 48.0
            self.add("s4", "4.13", "1-Wasserstein/EMD (work, WD), normalized by 48 slots",
                      "work", "n/a", emd_w_norm, "< 0.05",
                      "PASS" if emd_w_norm < 0.05 else "WARN")
            rms_w = float(np.sqrt(np.mean((owp - gwp) ** 2)))
            self.add("s4", "4.14", "Presence-rate RMS (work, WD)", "work", "n/a", rms_w,
                      "<= 0.05 (5pp)", "PASS" if rms_w <= 0.05 else "WARN")
            obs_tm = transition_matrix_2x2(ow[m1])
            gen_tm = transition_matrix_2x2(gw[m1])
            frob = float(np.sqrt(np.sum((obs_tm - gen_tm) ** 2)))
            self.add("s4", "4.15", "Transition-matrix Frobenius (work, WD, 2x2 on/off)", "work",
                      "n/a", frob, "< 0.05", "PASS" if frob < 0.05 else "WARN")
            obs_runs = run_lengths(ow[m1].flatten().astype(int))
            gen_runs = run_lengths(gw[m1].flatten().astype(int))
            if len(obs_runs) > 1 and len(gen_runs) > 1:
                ks_stat, ks_p = ks_2samp(obs_runs, gen_runs)
                self.add("s4", "4.16", "Dwell-time KS (work, WD run-lengths)", "work", "n/a",
                          ks_p, "p > 0.05 (fail to reject H0)", "PASS" if ks_p > 0.05 else "WARN",
                          f"KS stat={ks_stat:.4f}, n_obs_runs={len(obs_runs)}, n_gen_runs={len(gen_runs)}")
            else:
                self.add("s4", "4.16", "Dwell-time KS (work, WD run-lengths)", "work", "n/a",
                          "n/a", "p > 0.05", "INFO", "Too few runs for a KS test on this small sample.")
            max_lag = min(24, len(owp) - 1)
            acf_obs = acf(owp, max_lag)
            acf_gen = acf(gwp, max_lag)
            acf_mae = float(np.mean(np.abs(acf_obs - acf_gen)))
            self.add("s4", "4.17", "ACF-MAE (work, WD, lags 1..%d slots)" % max_lag, "work",
                      "n/a", acf_mae, "< 0.05", "PASS" if acf_mae < 0.05 else "WARN")

            # 4.18 C2ST (home+work joint) — manual numpy logistic regression, 5-fold CV
            try:
                X_obs = row_summary_features(obs_aligned)
                X_gen_df = pd.DataFrame(gh, columns=HOM_COLS)
                X_gen_df = pd.concat([X_gen_df, pd.DataFrame(gw, columns=WRK_COLS),
                                       pd.DataFrame(ga, columns=ACT_COLS)], axis=1)
                X_gen = row_summary_features(X_gen_df)
                X = np.vstack([X_obs, X_gen])
                y = np.concatenate([np.zeros(len(X_obs)), np.ones(len(X_gen))])
                acc = manual_logreg_cv(X, y, n_folds=5)
                self.add("s4", "4.18", "C2ST (home+work joint): real-2022 vs reconstructed-2022, "
                          "manual numpy logistic-regression classifier (5-fold CV), NOT XGBoost "
                          "(outside this validator's pandas/numpy/scipy/matplotlib dependency "
                          "list)", "both", "n/a", acc, "0.45 <= accuracy <= 0.55",
                          "PASS" if 0.45 <= acc <= 0.55 else "WARN")
            except Exception as e:
                print(f"  [4.18 WARN] C2ST failed: {e}")

        # Charts
        try:
            fig, axs = plt.subplots(1, 2, figsize=(13, 4))
            slots = np.arange(1, 49)
            for s, color, lbl in [(1, "#1976d2", "WD"), (2, "#388e3c", "Sat"), (3, "#e65100", "Sun")]:
                m = (strata == s)
                if m.sum() == 0:
                    continue
                axs[0].plot(slots, oh[m].mean(0) * 100, color=color, lw=1.5, label=f"Obs {lbl}")
                axs[0].plot(slots, gh[m].mean(0) * 100, color=color, lw=1.5, ls="--", label=f"Recon {lbl}")
                axs[1].plot(slots, ow[m].mean(0) * 100, color=color, lw=1.5, label=f"Obs {lbl}")
                axs[1].plot(slots, gw[m].mean(0) * 100, color=color, lw=1.5, ls="--", label=f"Recon {lbl}")
            axs[0].set_title("AT_HOME: Observed vs. Reconstructed 2022"); axs[0].set_ylabel("%")
            axs[1].set_title("AT_WORK: Observed vs. Reconstructed 2022")
            for ax in axs:
                ax.set_xlabel("30-min slot (1=04:00)"); ax.legend(fontsize=6, ncol=3); ax.set_xlim(1, 48)
            plt.tight_layout()
            self.charts["s4_overlay"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s4_overlay failed: {e}")

        try:
            top5_codes = top5.index.tolist()
            gen_shares = [float((ga.flatten() == c).mean()) * 100 for c in top5_codes]
            obs_shares = [float(v) * 100 for v in top5.values]
            fig, ax = plt.subplots(figsize=(7, 3.5))
            x = np.arange(len(top5_codes))
            ax.bar(x - 0.18, obs_shares, width=0.35, label="Observed 2022", color="#1976d2")
            ax.bar(x + 0.18, gen_shares, width=0.35, label="Reconstructed 2022", color="#e65100")
            ax.set_xticks(x); ax.set_xticklabels([f"code {int(c)}" for c in top5_codes])
            ax.set_ylabel("Share (%)"); ax.set_title("Top-5 activities: observed vs. reconstructed")
            ax.legend(fontsize=8)
            plt.tight_layout()
            self.charts["s4_activity_diff"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s4_activity_diff failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 5 — 2030 Schedule Plausibility (per band, both channels)
    # ══════════════════════════════════════════════════════════════════════

    def validate_2030_schedule_plausibility(self) -> None:
        print("\n[Section 5] 2030 schedule plausibility (per band) ...")
        if self.synth_2030 is None:
            print("  [SKIP] 2030 deliverable not available")
            return
        df = self.synth_2030

        wfh_2022_obs = None
        wd_at_home_2022 = wd_at_work_2022 = None
        if self.obs_2022 is not None and len(self.obs_2022) > 0:
            wd22 = self.obs_2022[self.obs_2022["DDAY_STRATA"] == 1]
            wd_at_home_2022 = float(wd22[HOM_COLS].values.mean()) * 100
            wd_at_work_2022 = float(wd22[WRK_COLS].values.mean()) * 100
            wfh_2022_obs = compute_wfh_rate(wd22)

        wfh_by_band = {}
        wfh_day_share_by_band = {}
        for band in BANDS:
            sub = df[df["BAND"] == band]
            if len(sub) == 0:
                continue
            blabel = BAND_LABEL[band]

            at_home_overall = float(sub[HOM_COLS].values.mean()) * 100
            self.add("s5", "5.1", "2030 AT_HOME overall mean", "home", blabel, at_home_overall,
                      "in [55,90]", "PASS" if 55 <= at_home_overall <= 90 else "FAIL")

            wd = sub[sub["DDAY_STRATA"] == 1]
            we = sub[sub["DDAY_STRATA"] != 1]
            wd_at = float(wd[HOM_COLS].values.mean()) * 100 if len(wd) else float("nan")
            we_at = float(we[HOM_COLS].values.mean()) * 100 if len(we) else float("nan")
            self.add("s5", "5.2", "WD AT_HOME < WE AT_HOME (structural)", "home", blabel,
                      f"WD={wd_at:.2f}% WE={we_at:.2f}%", "WD < WE",
                      "PASS" if wd_at < we_at else "FAIL")

            night_acts = sub[ACT_COLS[:8]].values.flatten()
            sleep_pct = float((night_acts == SLEEP_CODE).mean()) * 100
            self.add("s5", "5.3", "Night sleep (slots 1-8, raw code 5)", "activity", blabel,
                      sleep_pct, ">= 70%", "PASS" if sleep_pct >= 70 else "FAIL")

            all_acts = sub[ACT_COLS].values.flatten()
            act_counts = pd.Series(all_acts).value_counts(normalize=True)
            max_share = float(act_counts.max()) * 100
            self.add("s5", "5.4", "Activity distribution non-degenerate (max single-activity share)",
                      "activity", blabel, max_share, "< 60%", "PASS" if max_share < 60 else "FAIL")

            wfh_band = compute_wfh_rate(wd)
            wfh_by_band[band] = wfh_band
            wfh_day_share_by_band[band] = compute_wfh_day_share(wd)
            if wfh_2022_obs is not None:
                self.add("s5", "5.5", "WFH signal present (home): band WFH_RATE > observed-2022 "
                          "WFH_RATE (checked for hybrid/fullyhybrid only per spec)", "home",
                          blabel, wfh_band, f"> obs 2022 ({wfh_2022_obs:.4f})",
                          "PASS" if (band == "conservative" or wfh_band > wfh_2022_obs) else "FAIL",
                          "Spec only requires this for band B and C; conservative is reported "
                          "as INFO context." if band == "conservative" else "")

            if wd_at_home_2022 is not None:
                cont = abs(wd_at - wd_at_home_2022)
                self.add("s5", "5.6", "2030 WD AT_HOME continuity vs. 2022", "home", blabel,
                          cont, "<= 15pp", "PASS" if cont <= 15 else "FAIL",
                          f"2030 WD={wd_at:.2f}%, 2022 WD={wd_at_home_2022:.2f}%")

            # Office channel (wrk30), primarily WD (DDAY_STRATA=1)
            wd_at_work = float(wd[WRK_COLS].values.mean()) * 100 if len(wd) else float("nan")
            if band == "conservative":
                self.add("s5", "5.7", "2030 AT_WORK plausibility (band A)", "work", blabel,
                          wd_at_work, "in [25,55]", "PASS" if 25 <= wd_at_work <= 55 else "WARN")

            morning = wd[[f"wrk30_{i:03d}" for i in range(12, 17)]].values.mean() if len(wd) else np.nan
            afternoon = wd[[f"wrk30_{i:03d}" for i in range(22, 27)]].values.mean() if len(wd) else np.nan
            lunch = wd[[f"wrk30_{i:03d}" for i in range(17, 20)]].values.mean() if len(wd) else np.nan
            peak = max(morning, afternoon) if not (np.isnan(morning) or np.isnan(afternoon)) else np.nan
            morning_thr = {"conservative": 0.40, "hybrid": 0.30, "fullyhybrid": 0.20}[band]
            self.add("s5", "5.8", "Office diurnal: WD morning peak (slots 12-16, 09:30-11:30)",
                      "work", blabel, float(morning), f">= {morning_thr}",
                      "PASS" if morning >= morning_thr else "WARN",
                      "hybrid threshold (0.30) is linearly interpolated between the spec's "
                      "explicit A=0.40 / C=0.20 values — not a literal spec number."
                      if band == "hybrid" else "")
            afternoon_thr = morning_thr
            self.add("s5", "5.9", "Office diurnal: WD afternoon peak (slots 22-26, 14:30-16:30)",
                      "work", blabel, float(afternoon), f">= {afternoon_thr}",
                      "PASS" if afternoon >= afternoon_thr else "WARN")
            if not np.isnan(peak) and peak > 0:
                self.add("s5", "5.10", "Office diurnal: WD lunch dip (slots 17-19, 12:00-13:30)",
                          "work", blabel, float(lunch), f"< peak*0.70 ({peak*0.70:.4f})",
                          "PASS" if lunch < peak * 0.70 else "WARN")

            night_floor_cols = [f"wrk30_{i:03d}" for i in range(1, 9)] + [f"wrk30_{i:03d}" for i in range(38, 49)]
            night_floor = wd[night_floor_cols].values.mean() if len(wd) else np.nan
            if band == "conservative":
                self.add("s5", "5.11", "Office diurnal: night floor (slots 1-8, 38-48)", "work",
                          blabel, float(night_floor), "in [0.02,0.05]",
                          "PASS" if 0.02 <= night_floor <= 0.05 else "WARN")

            sat = sub[sub["DDAY_STRATA"] == 2]
            sun = sub[sub["DDAY_STRATA"] == 3]
            sat_wrk = float(sat[WRK_COLS].values.mean()) if len(sat) else np.nan
            sun_wrk = float(sun[WRK_COLS].values.mean()) if len(sun) else np.nan
            if band == "conservative":
                self.add("s5", "5.12", "WE office presence: Saturday mean wrk30", "work", blabel,
                          sat_wrk, "in [0.05,0.10]", "PASS" if 0.05 <= sat_wrk <= 0.10 else "WARN")
                self.add("s5", "5.13", "WE office presence: Sunday mean wrk30", "work", blabel,
                          sun_wrk, "< 0.05", "PASS" if sun_wrk < 0.05 else "WARN")

            we_wrk = float(we[WRK_COLS].values.mean()) if len(we) else np.nan
            self.add("s5", "5.14", "WD > WE AT_WORK structural (office side)", "work", blabel,
                      f"WD={wd_at_work/100:.4f} WE={we_wrk:.4f}", "WD > WE",
                      "PASS" if (wd_at_work / 100) > we_wrk else "FAIL")

            if band == "conservative" and wd_at_work_2022 is not None:
                cont_w = abs(wd_at_work - wd_at_work_2022)
                self.add("s5", "5.15", "2030 AT_WORK continuity vs. 2022 (band A)", "work",
                          blabel, cont_w, "<= 20pp", "PASS" if cont_w <= 20 else "FAIL",
                          f"2030 WD={wd_at_work:.2f}%, 2022 WD={wd_at_work_2022:.2f}%")

            if band == "conservative":
                peak_slots = wd[WRK_COLS].values.mean(axis=0)
                peak_mag_2030 = float(peak_slots.max())
                peak_slot_2030 = int(np.argmax(peak_slots)) + 1
                if self.obs_2022 is not None and len(self.obs_2022) > 0:
                    wd22_prof = wd22[WRK_COLS].values.mean(axis=0)
                    peak_mag_2022 = float(wd22_prof.max())
                    peak_slot_2022 = int(np.argmax(wd22_prof)) + 1
                    pct_diff = abs(peak_mag_2030 - peak_mag_2022) / peak_mag_2022 * 100 if peak_mag_2022 > 0 else np.nan
                    self.add("s5", "6.12", "Peak magnitude (work, band A vs. observed 2022)",
                              "work", blabel, pct_diff, "<= 15%",
                              "PASS" if pct_diff <= 15 else "WARN",
                              f"2030 peak={peak_mag_2030:.4f} @slot{peak_slot_2030}, "
                              f"2022 peak={peak_mag_2022:.4f} @slot{peak_slot_2022}")
                    slot_diff = abs(peak_slot_2030 - peak_slot_2022)
                    self.add("s5", "6.13", "Peak timing (work, band A vs. observed 2022)", "work",
                              blabel, slot_diff, "<= 2 slots (1h)",
                              "PASS" if slot_diff <= 2 else "WARN")

        # 5.16-5.19 WFH sensitivity — computed on the LITERAL spec formula (compute_wfh_rate:
        # employed, hom30==1 OR act30==Work, biz-hours slots 11-26).
        wfh_flat_note = ""
        if len(wfh_day_share_by_band) == 3:
            wfh_flat_note = (
                f"IMPORTANT DISCREPANCY (flagged per the task's sanity check, not silently "
                f"passed): the literal 'WFH_RATE' formula from compute_wfh_rate() in the "
                f"training script (hom30==1 OR act30==Work, employed, biz-hours) comes out "
                f"nearly IDENTICAL across all 3 bands ("
                f"{wfh_by_band.get('conservative', float('nan')):.4f} / "
                f"{wfh_by_band.get('hybrid', float('nan')):.4f} / "
                f"{wfh_by_band.get('fullyhybrid', float('nan')):.4f}) — this exact flatness is "
                f"already documented in the training Progress Log (2026-06-26 entry, job "
                f"987039): 'WFH_RATE per band nearly flat (0.8193/0.8140/0.8145) -> Monotone "
                f"sensitivity: FAIL (household any-occupant metric, ~invariant by design - "
                f"minor)'. It is a broad OR-combination (home-presence OR doing the Work "
                f"activity) that saturates near ~0.82 regardless of band. The metric that "
                f"actually differentiates the bands is the DAY-LEVEL WFH classifier used by "
                f"the post-hoc reweight ('WFH-day': business-hours mean AT_HOME >= 0.50), which "
                f"we compute here for cross-reference: conservative="
                f"{wfh_day_share_by_band.get('conservative', float('nan')):.4f}, hybrid="
                f"{wfh_day_share_by_band.get('hybrid', float('nan')):.4f}, fullyhybrid="
                f"{wfh_day_share_by_band.get('fullyhybrid', float('nan')):.4f} — these DO land "
                f"near the training log's target WFH-day shares (~0.170/0.292/0.388) and ARE "
                f"strictly monotone, confirming the bands are genuinely differentiated on the "
                f"metric that drives them; the spec's literal WFH_RATE gate is simply testing "
                f"a metric documented to be insensitive to the band mechanism."
            )
        if len(wfh_by_band) == 3:
            c, h, f_ = wfh_by_band["conservative"], wfh_by_band["hybrid"], wfh_by_band["fullyhybrid"]
            monotone = f_ > h > c
            self.add("s5", "5.16", "Monotone WFH_RATE: fullyhybrid > hybrid > conservative "
                      "(literal compute_wfh_rate() formula per spec)",
                      "both", "all", f"C={c:.4f} H={h:.4f} F={f_:.4f}", "strict monotone",
                      "PASS" if monotone else "FAIL", wfh_flat_note)
            for band, key in [("conservative", "5.17"), ("hybrid", "5.18"), ("fullyhybrid", "5.19")]:
                lo, hi = WFH_TARGET[band]
                v = wfh_by_band[band]
                self.add("s5", key, f"Band {BAND_LABEL[band]} WFH_RATE target", "both",
                          BAND_LABEL[band], v, f"in [{lo},{hi}]", "PASS" if lo <= v <= hi else "WARN")
        if len(wfh_day_share_by_band) == 3:
            cd, hd, fd = (wfh_day_share_by_band["conservative"], wfh_day_share_by_band["hybrid"],
                          wfh_day_share_by_band["fullyhybrid"])
            monotone_d = fd > hd > cd
            self.add("s5", "5.16-cross-ref", "Monotone WFH-DAY SHARE (cross-reference metric: "
                      "biz-hours mean AT_HOME >= 0.50, employed, WD) -- NOT the literal spec "
                      "gate, shown because it is the metric the bands were actually built to "
                      "hit", "both", "all", f"C={cd:.4f} H={hd:.4f} F={fd:.4f}",
                      "strict monotone (target ~0.170/0.292/0.388 per training log)",
                      "PASS" if monotone_d else "FAIL")

        # Charts
        try:
            fig, axs = plt.subplots(1, 2, figsize=(13, 4))
            slots = np.arange(1, 49)
            colors = {"conservative": "#1976d2", "hybrid": "#388e3c", "fullyhybrid": "#e65100"}
            for band in BANDS:
                sub = df[(df["BAND"] == band) & (df["DDAY_STRATA"] == 1)]
                if len(sub) == 0:
                    continue
                axs[0].plot(slots, sub[HOM_COLS].values.mean(0) * 100, color=colors[band], lw=1.8,
                             label=BAND_LABEL[band])
                axs[1].plot(slots, sub[WRK_COLS].values.mean(0) * 100, color=colors[band], lw=1.8,
                             label=BAND_LABEL[band])
            if self.obs_2022 is not None and len(self.obs_2022) > 0:
                wd22 = self.obs_2022[self.obs_2022["DDAY_STRATA"] == 1]
                axs[0].plot(slots, wd22[HOM_COLS].values.mean(0) * 100, color="k", lw=1.2, ls=":", label="Obs 2022")
                axs[1].plot(slots, wd22[WRK_COLS].values.mean(0) * 100, color="k", lw=1.2, ls=":", label="Obs 2022")
            axs[0].set_title("hom30 WD: 2030 bands vs. observed 2022"); axs[0].set_ylabel("%")
            axs[1].set_title("wrk30 WD: 2030 bands vs. observed 2022")
            for ax in axs:
                ax.set_xlabel("30-min slot (1=04:00)"); ax.legend(fontsize=7); ax.set_xlim(1, 48)
            plt.tight_layout()
            self.charts["s5_overlay"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s5_overlay failed: {e}")

        try:
            fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
            labels = ["conservative", "hybrid", "fullyhybrid"]
            colors_list = ["#1976d2", "#388e3c", "#e65100"]

            vals = [wfh_by_band.get(b, np.nan) for b in labels]
            bars = axs[0].bar([BAND_LABEL[b] for b in labels], vals, color=colors_list)
            if wfh_2022_obs is not None:
                axs[0].axhline(wfh_2022_obs, color="k", ls="--", lw=1, label=f"Obs 2022 ({wfh_2022_obs:.3f})")
            for bar, v in zip(bars, vals):
                if not np.isnan(v):
                    axs[0].text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
            axs[0].set_ylabel("WFH_RATE"); axs[0].set_title("Literal WFH_RATE (spec formula) — "
                              "known-flat by design"); axs[0].legend(fontsize=7)
            axs[0].tick_params(axis="x", labelrotation=12)

            vals_d = [wfh_day_share_by_band.get(b, np.nan) for b in labels]
            bars_d = axs[1].bar([BAND_LABEL[b] for b in labels], vals_d, color=colors_list)
            target_mid = [0.175, 0.30, 0.40]
            axs[1].scatter(range(3), target_mid, color="k", marker="x", s=60, label="training-log target")
            for bar, v in zip(bars_d, vals_d):
                if not np.isnan(v):
                    axs[1].text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
            axs[1].set_ylabel("WFH-day share"); axs[1].set_title("Cross-ref: day-level WFH "
                              "classifier (biz-hours home>=0.50) — the metric bands were built to hit")
            axs[1].legend(fontsize=7); axs[1].tick_params(axis="x", labelrotation=12)
            plt.tight_layout()
            self.charts["s5_wfh_bar"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s5_wfh_bar failed: {e}")

        self._wfh_by_band = wfh_by_band

    # ══════════════════════════════════════════════════════════════════════
    # Section 6 — BEM Output Readiness
    # ══════════════════════════════════════════════════════════════════════

    def validate_bem_readiness(self) -> None:
        print("\n[Section 6] BEM output readiness ...")
        if self.synth_2030 is None:
            print("  [SKIP] 2030 deliverable not available")
            return
        df = self.synth_2030

        act_ok = all(c in df.columns for c in ACT_COLS)
        hom_ok = all(c in df.columns for c in HOM_COLS)
        wrk_ok = all(c in df.columns for c in WRK_COLS)
        self.add("s6", "6.1", "Schema: act30 columns present", "activity", "all",
                  "yes" if act_ok else "no", "100%", "PASS" if act_ok else "FAIL")
        self.add("s6", "6.2", "Schema: hom30 columns present", "home", "all",
                  "yes" if hom_ok else "no", "100%", "PASS" if hom_ok else "FAIL")
        self.add("s6", "6.3", "Schema: wrk30 columns present", "work", "all",
                  "yes" if wrk_ok else "no", "100%", "PASS" if wrk_ok else "FAIL")

        act_vals = df[ACT_COLS].values
        act_rng = int(act_vals.min()) >= 1 and int(act_vals.max()) <= 14
        self.add("s6", "6.4", "act30 range", "activity", "all",
                  f"[{int(act_vals.min())},{int(act_vals.max())}]", "[1,14]",
                  "PASS" if act_rng else "FAIL")

        hom_vals = set(np.unique(df[HOM_COLS].values))
        self.add("s6", "6.5", "hom30 range", "home", "all", str(sorted(hom_vals)), "{0,1}",
                  "PASS" if hom_vals <= {0, 1} else "FAIL")

        wrk_vals = set(np.unique(df[WRK_COLS].values))
        self.add("s6", "6.6", "wrk30 range", "work", "all", str(sorted(wrk_vals)), "{0,1}",
                  "PASS" if wrk_vals <= {0, 1} else "FAIL")

        hom_arr = df[HOM_COLS].values
        wrk_arr = df[WRK_COLS].values
        conflict = (hom_arr == 1) & (wrk_arr == 1)
        n_conflict = int(conflict.sum())
        self.add("s6", "6.7", "Mutual exclusion: hom30==1 AND wrk30==1", "both", "all",
                  n_conflict, "0 (hard gate, post-6H cleanup)", "PASS" if n_conflict == 0 else "FAIL")

        band_counts = df["BAND"].value_counts()
        for band in BANDS:
            n = int(band_counts.get(band, 0))
            self.add("s6", "6.8", f"Row count for band {band}", "both", BAND_LABEL[band], n,
                      ">= 37,000", "PASS" if n >= 37000 else "FAIL")

        band_ok = set(df["BAND"].unique()) == set(BANDS)
        self.add("s6", "6.9", "BAND column completeness", "both", "all",
                  str(sorted(df["BAND"].unique())), "{conservative,hybrid,fullyhybrid}",
                  "PASS" if band_ok else "FAIL")

        strata_ok_all = all(set(df[df["BAND"] == b]["DDAY_STRATA"].unique()) == {1, 2, 3} for b in BANDS)
        self.add("s6", "6.10", "DDAY_STRATA completeness (per band)", "both", "all",
                  str(sorted(df["DDAY_STRATA"].unique())), "{1,2,3} in each band",
                  "PASS" if strata_ok_all else "FAIL")

        cy_ok = (df["CYCLE_YEAR"] == 2030).all()
        self.add("s6", "6.11", "CYCLE_YEAR tag", "both", "all",
                  str(sorted(df["CYCLE_YEAR"].unique())), "{2030}", "PASS" if cy_ok else "FAIL",
                  "SCENARIO column not present in this deliverable's schema — skipped, not silently passed.")

        # Charts
        try:
            fig, ax = plt.subplots(figsize=(9, 4))
            strata_pivot = df.groupby(["BAND", "DDAY_STRATA"]).size().unstack(fill_value=0)
            strata_pivot = strata_pivot.reindex(BANDS)
            strata_pivot.columns = [STRATUM_LABEL[c] for c in strata_pivot.columns]
            strata_pivot.plot(kind="bar", ax=ax, color=["#1976d2", "#388e3c", "#e65100"])
            ax.set_ylabel("Row count"); ax.set_title("DDAY_STRATA distribution per band (2030)")
            ax.set_xticklabels([BAND_LABEL[b] for b in BANDS], rotation=15)
            plt.tight_layout()
            self.charts["s6_strata"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s6_strata failed: {e}")

        try:
            per_slot_conflict = conflict.sum(axis=0)
            fig, ax = plt.subplots(figsize=(9, 3))
            ax.bar(range(1, 49), per_slot_conflict, color="#c62828")
            ax.set_xlabel("30-min slot (1=04:00)"); ax.set_ylabel("Conflict count")
            ax.set_title("Mutual-exclusion violations per slot (hom30==1 AND wrk30==1) — should be all-zero")
            plt.tight_layout()
            self.charts["s6_mutex"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s6_mutex failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 7 — Summary scorecard
    # ══════════════════════════════════════════════════════════════════════

    def generate_summary_table(self) -> dict:
        print("\n[Section 7] Summary scorecard ...")
        tally = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
        for section, rows in self.checks.items():
            for r in rows:
                tally[r["status"]] += 1
        print(f"  PASS={tally['PASS']}  WARN={tally['WARN']}  FAIL={tally['FAIL']}  INFO={tally['INFO']}")
        return tally

    # ══════════════════════════════════════════════════════════════════════
    # HTML report
    # ══════════════════════════════════════════════════════════════════════

    def _section_table(self, section: str) -> str:
        rows = self.checks.get(section, [])
        if not rows:
            return "<p style='color:#888'>No checks computed (input unavailable).</p>"
        body = ""
        for r in rows:
            obs = r["observed"]
            obs_str = f"{obs:.4f}" if isinstance(obs, float) else str(obs)
            note = f"<br><span style='font-size:11px;color:#666'>{r['note']}</span>" if r["note"] else ""
            body += (f"<tr><td>{r['id']}</td><td>{r['desc']}{note}</td><td>{r['channel']}</td>"
                     f"<td>{r['band']}</td><td>{obs_str}</td><td>{r['threshold']}</td>"
                     f"<td>{_status_html(r['status'])}</td></tr>")
        return (f"<table><thead><tr><th>Gate</th><th>Check</th><th>Channel</th><th>Band</th>"
                f"<th>Observed</th><th>Threshold</th><th>Status</th></tr></thead>"
                f"<tbody>{body}</tbody></table>")

    def _chart_block(self, *keys) -> str:
        out = ""
        for k in keys:
            if k in self.charts:
                out += f'<img src="data:image/png;base64,{self.charts[k]}" style="max-width:100%;margin:12px 0"/>'
        return out

    def build_html_report(self) -> str:
        tally = self.generate_summary_table()
        total_scored = tally["PASS"] + tally["WARN"] + tally["FAIL"]
        summary_color = "#2e7d32" if tally["FAIL"] == 0 else "#c62828"

        def section_html(title: str, section_key: str, chart_keys: tuple, notes: str = "") -> str:
            note_html = f'<p style="font-size:12px;color:#555;margin-top:6px">{notes}</p>' if notes else ""
            return f"""
            <div class="section">
              <h2>{title}</h2>
              {note_html}
              {self._section_table(section_key)}
              {self._chart_block(*chart_keys)}
            </div>"""

        body = section_html("1 &mdash; Training Convergence (INFO only)", "s1", (),
            "No per-epoch/per-checkpoint CSV was persisted for this run; all rows below are "
            "transcribed from the Progress Log in 3rdJ_06_longitudinalForecasting_2split.md and "
            "marked INFO, never scored PASS/FAIL/WARN.")
        body += section_html("2 &mdash; True Future Test (INFO only)", "s2", (),
            "No per-phase True Future Test JS values were transcribed to the Progress Log for "
            "the full-corpus run. A DRIFT_MATRIX-based proxy is shown for cross-reference, "
            "clearly labeled as not the literal Section-2 gate.")
        body += section_html("3 &mdash; DRIFT_MATRIX Plausibility", "s3", ("s3_bars", "s3_heatmap"),
            "Computed directly from the 3 on-disk DRIFT_MATRIX_*_2split.csv files (wide format, "
            "one row per DDAY_STRATA). Gates 3.5/3.6 (dual COVID signal) may FAIL due to a "
            "known temperature=0.0 greedy-decoding artifact already diagnosed in the training "
            "log (2026-06-26 entries) as NOT present in the temp=0.8 2030 deliverable &mdash; "
            "see the per-check note.")
        body += section_html("4 &mdash; 2022 Backcasting Reconstruction (joint gate)", "s4",
            ("s4_overlay", "s4_activity_diff"),
            "Computed against reconstructed_2022_diaries_2split.csv (37 rows, no DDAY_STRATA of "
            "its own) row-order-aligned to the first N rows of observed 2022 "
            "(R5_raked_mindwell_actv2/augmented_diaries.csv, chunked read) &mdash; see the 4.1 "
            "note for the alignment convention and its caveats. Metric is the marginal per-slot "
            "mean-occupancy profile JS (not raw flattened element-wise JS), per the corrected "
            "metric documented in the training log's 2026-06-26 entries.")
        body += section_html("5 &mdash; 2030 Schedule Plausibility (per band)", "s5",
            ("s5_overlay", "s5_wfh_bar"),
            "Computed per band (conservative/hybrid/fullyhybrid) directly from "
            "2030_synthetic_diaries_2split_calibrated_mindwell_C.csv, the current canonical "
            "Step-6 deliverable (post Calibration-B and Calibration-C).")
        body += section_html("6 &mdash; BEM Output Readiness", "s6", ("s6_strata", "s6_mutex"))

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Step 6 (Leg-2 2-split) Validation Report</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1200px;margin:40px auto;padding:0 20px;color:#222}}
h1{{color:#1a237e;border-bottom:2px solid #1a237e;padding-bottom:8px}}
h2{{color:#283593;margin-top:28px}}
.section{{background:#fafafa;border:1px solid #e0e0e0;border-radius:6px;padding:16px;margin:20px 0}}
table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:12.5px}}
th{{background:#283593;color:#fff;padding:7px 10px;text-align:left}}
td{{padding:6px 10px;border-bottom:1px solid #e0e0e0;vertical-align:top}}
tr:last-child td{{border-bottom:none}}
.summary{{background:#e8eaf6;border-radius:6px;padding:14px;margin:16px 0;font-size:15px}}
.scorecard{{display:flex;gap:14px;margin:14px 0;flex-wrap:wrap}}
.card{{flex:1;min-width:110px;text-align:center;padding:12px;border-radius:6px;font-weight:bold;color:#fff}}
.card.pass{{background:#2e7d32}} .card.warn{{background:#e65100}}
.card.fail{{background:#c62828}} .card.info{{background:#1565c0}}
</style></head><body>
<h1>Step 6 (Leg-2 2-split) &mdash; Two-Channel Longitudinal Forecasting Validation Report</h1>
<div class="summary">
  <strong>Overall (Sections 3-6, scored gates only; Sections 1-2 are INFO and excluded):</strong>
  <span style="color:{summary_color};font-weight:bold">{tally['PASS']}/{total_scored} PASS</span>
  &nbsp;|&nbsp; Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
  <div class="scorecard">
    <div class="card pass">PASS<br>{tally['PASS']}</div>
    <div class="card warn">WARN<br>{tally['WARN']}</div>
    <div class="card fail">FAIL<br>{tally['FAIL']}</div>
    <div class="card info">INFO<br>{tally['INFO']}</div>
  </div>
</div>
{body}
<hr/><p style="font-size:11px;color:#888">
Step 6 (Leg-2 2-split) GSSCanada Occupancy Pipeline &mdash; Concordia University postdoc project.<br>
Report generated by 3rdJ_06_longitudinalForecasting_2split_val.py.<br>
Inputs: 2030_synthetic_diaries_2split_calibrated_mindwell_C.csv,
reconstructed_2022_diaries_2split.csv, DRIFT_MATRIX_{{0510,1015,1522}}_2split.csv (all under
Step6_docs/outputs_step6/), and R5_raked_mindwell_actv2/augmented_diaries.csv (observed 2022
baseline, Step4_docs/outputs_step4/sweep/, read in 20,000-row chunks, 2022-only rows retained).<br>
Threshold provenance: gates come from (1) ASHRAE Guideline 14-2014 Section 4.1 (NMBE/CV(RMSE),
applied only to same-period 2022 backcast checks, NOT the 2030 cross-year forecast), (2)
literature-confirmed values (C2ST accuracy ~0.50, dwell-time KS p&gt;0.05), and (3)
project-chosen thresholds set before tuning (KL&lt;0.05, EMD&lt;0.05, presence-RMS&le;5pp,
transition-matrix Frobenius/MAE&lt;0.05, ACF-MAE&lt;0.05, peak magnitude &plusmn;15%, peak
timing &le;1h) &mdash; see 3rdJ_06_longitudinalForecasting_2split_val.md Threshold Provenance
Note for the full citation policy. Model-selection rule (hard, per spec): select on the
Pareto frontier of Wasserstein + ACF-MAE + downstream peak, never on a single composite score.
</p></body></html>"""
        return html

    # ── Run all ───────────────────────────────────────────────────────────────

    def run_all(self) -> None:
        self.validate_training_convergence()
        self.validate_true_future_test()
        self.validate_drift_matrices()
        self.validate_backcasting_2022()
        self.validate_2030_schedule_plausibility()
        self.validate_bem_readiness()
        tally = self.generate_summary_table()

        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.outputs_dir / "step6_validation_report.html"
        report_html = self.build_html_report()
        report_path.write_text(report_html, encoding="utf-8")
        print(f"\nReport saved: {report_path}")
        print(f"Final scorecard: PASS={tally['PASS']} WARN={tally['WARN']} "
              f"FAIL={tally['FAIL']} INFO={tally['INFO']}")


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Step 6 (Leg-2 2-split) validation report generator")
    ap.add_argument("--forecast_dir", default=str(here / "outputs_step6"))
    ap.add_argument("--step4_raked_dir",
                     default=str(here.parents[0] / "Step4_docs" / "outputs_step4" / "sweep" /
                                 "R5_raked_mindwell_actv2"))
    ap.add_argument("--outputs_dir", default=str(here / "outputs_step6"))
    args = ap.parse_args()

    validator = LongitudinalForecastingValidator2Split(
        forecast_dir=args.forecast_dir,
        step4_raked_dir=args.step4_raked_dir,
        outputs_dir=args.outputs_dir,
    )
    validator.run_all()


if __name__ == "__main__":
    main()
