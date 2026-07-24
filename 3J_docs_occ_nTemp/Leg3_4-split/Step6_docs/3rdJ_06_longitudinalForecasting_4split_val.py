"""
3rdJ_06_longitudinalForecasting_4split_val.py
Step 6 (Leg-3 4-split) -- Four-Channel Longitudinal Forecasting + Hotel SARIMA:
Validation & Report Generator.

Ports LongitudinalForecastingValidator2Split (Leg-2) -> ...Validator4Split, per
3J_docs_occ_nTemp/Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split_val.md
(Sections 1-7 ported 3-channel, Section 8 hotel SARIMA NEW).

Sections 1-2 (training convergence, True Future Test): INFO-only prose, never
scored PASS/FAIL/WARN -- per the manager's explicit instruction (no per-epoch
CSV artifact to score against a threshold), even though this leg's cluster
.out log happens to carry real per-epoch loss/val_js numbers (richer than
Leg-2 had); those numbers are transcribed as INFO evidence, not gated.

Section 4 (2022 backcast) is scored on the PRODUCTION
reconstructed_2022_diaries_4split.csv from job 1133427 using the
profile-shape-JS + level-MAD metric (never raw flattened-binary JS). That
file carries NO DDAY_STRATA/LFTAG/PR of its own (confirmed: only
act30_/hom30_/wrk30_/ret30_ + CYCLE_YEAR + IS_SYNTHETIC). Leg-2 solved this
by row-order-aligning against a locally-available copy of the SAME training
pool the backcast was conditioned on; that pool (Leg-3's 418MB
seed_3_g3fix/augmented_diaries.csv) is cluster-only and explicitly OUT OF
SCOPE for this session's local staging (Step-0 downloaded only the 3 raw
per-band files, the backcast CSV, and the 3 DRIFT matrices -- not the raw
training pool). So Section 4's PRIMARY per-stratum evidence is the build's
OWN already-computed gate table, transcribed verbatim from the production
job's own stdout (job 1133427, lines 140-151 of the .out log) -- this is the
authoritative source: it was computed by the exact production code, on the
exact backcast file under test, with correct DDAY_STRATA labels available
in-process before the CSV was ever written (the CSV write happens to omit
that column). A SECONDARY, clearly-labeled pooled cross-check is computed
directly from the on-disk files here for corroboration only.

Usage:
    py -3 -X utf8 3rdJ_06_longitudinalForecasting_4split_val.py
"""

from __future__ import annotations

import argparse
import base64
import io
import sys
import warnings
from datetime import datetime
from pathlib import Path

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
from scipy.spatial.distance import jensenshannon  # noqa: F401 (kept for parity w/ Leg-2 imports)
from scipy.stats import wasserstein_distance, ks_2samp, entropy

warnings.filterwarnings("ignore")

# ── Constants ─────────────────────────────────────────────────────────────────
N_SLOTS = 48
ACT_COLS = [f"act30_{i:03d}" for i in range(1, N_SLOTS + 1)]
HOM_COLS = [f"hom30_{i:03d}" for i in range(1, N_SLOTS + 1)]
WRK_COLS = [f"wrk30_{i:03d}" for i in range(1, N_SLOTS + 1)]
RET_COLS = [f"ret30_{i:03d}" for i in range(1, N_SLOTS + 1)]
STRATUM_LABEL = {1: "WD", 2: "Sat", 3: "Sun"}
BANDS = ["conservative", "hybrid", "fullyhybrid"]
BAND_LABEL = {"conservative": "A (conservative)", "hybrid": "B (hybrid)", "fullyhybrid": "C (fullyhybrid)"}
BIZ_SLOTS_0IDX = list(range(10, 26))
SLEEP_CODE = 5       # act30 raw code 5 = Sleep & Rest (ACT_LABELS, confirmed via BEM_PRIORITY)
WORK_ACT_CODE = 1    # act30 raw code 1 = Work

WFH_TARGET = {"conservative": (0.15, 0.20), "hybrid": (0.25, 0.35), "fullyhybrid": (0.35, 0.45)}
RETAIL_LEVERS = {"plateau": 0.97, "shift": 0.90, "renaissance": 1.05}
QC_PR, AB_PR = 24, 48

# ── Build-log transcription (job 1133427, .out lines 140-151 -- see module
#    docstring for why this is Section 4's PRIMARY per-stratum evidence) ──────
BUILD_BACKCAST_GATE_TABLE = {
    # stratum: (JSact, JShome, JSwork, JSret, MADhome, MADwork, MADret, dHome_pp, dWork_pp, dRet_pp)
    1: dict(JSact=0.0303, JShome=0.0016, JSwork=0.0261, JSret=0.0255,
            MADhome=0.0996, MADwork=0.1132, MADret=0.0039,
            dHome_pp=8.91, dWork_pp=10.99, dRet_pp=0.10, build_verdict="FAIL"),
    2: dict(JSact=0.0112, JShome=0.0004, JSwork=0.0043, JSret=0.0117,
            MADhome=0.0309, MADwork=0.0047, MADret=0.0127,
            dHome_pp=0.46, dWork_pp=0.37, dRet_pp=1.04, build_verdict="PASS"),
    3: dict(JSact=0.0217, JShome=0.0001, JSwork=0.0046, JSret=0.0104,
            MADhome=0.0176, MADwork=0.0042, MADret=0.0041,
            dHome_pp=0.12, dWork_pp=0.28, dRet_pp=0.29, build_verdict="PASS"),
}
BUILD_WFH_RATE = dict(observed=0.7314, reconstructed=0.7520, delta_pp=2.07)

# COVID triple-signal (job 1133427, .out line 74; matches DRIFT_MATRIX_1522_4split.csv WD row)
BUILD_COVID_1522_WD = dict(AT_HOME_drift=-0.145314, AT_WORK_drift=0.176595, AT_RETAIL_drift=0.000153)


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


# ── Validator ──────────────────────────────────────────────────────────────────

class LongitudinalForecastingValidator4Split:

    def __init__(self, forecast_dir: str, step5_obs_dir: str, hotel_dir: str,
                 hotel_processed_dir: str, outputs_dir: str):
        self.forecast_dir = Path(forecast_dir)
        self.step5_obs_dir = Path(step5_obs_dir)
        self.hotel_dir = Path(hotel_dir)
        self.hotel_processed_dir = Path(hotel_processed_dir)
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

        p = self.forecast_dir / "2030_synthetic_diaries_4split_calibrated_mindwell_C.csv"
        self.synth_2030 = pd.read_csv(p) if p.exists() else None
        print(f"  {'Loaded' if self.synth_2030 is not None else '[WARN] missing'} {p.name}"
              + (f" ({len(self.synth_2030):,} rows)" if self.synth_2030 is not None else ""))

        p = self.forecast_dir / "reconstructed_2022_diaries_4split.csv"
        self.recon_2022 = pd.read_csv(p) if p.exists() else None
        print(f"  {'Loaded' if self.recon_2022 is not None else '[WARN] missing'} {p.name}"
              + (f" ({len(self.recon_2022):,} rows, no DDAY_STRATA)" if self.recon_2022 is not None else ""))

        self.dm = {}
        for name in ("DRIFT_MATRIX_0510_4split", "DRIFT_MATRIX_1015_4split", "DRIFT_MATRIX_1522_4split"):
            p = self.forecast_dir / f"{name}.csv"
            if p.exists():
                self.dm[name] = pd.read_csv(p)
                print(f"  Loaded {name}.csv ({len(self.dm[name])} rows)")
            else:
                print(f"  [WARN] {p} not found")

        # Raw per-band 2030 (PR-conditioned retail checks + cross-band evidence)
        self.raw_bands = {}
        for band in BANDS:
            p = self.forecast_dir / f"2030_diaries_{band}_raw.csv"
            if p.exists():
                self.raw_bands[band] = pd.read_csv(p, low_memory=False)
                print(f"  Loaded 2030_diaries_{band}_raw.csv ({len(self.raw_bands[band]):,} rows)")
            else:
                print(f"  [WARN] {p} not found")

        # Retail lever files
        self.retail_levers = {}
        for scen in RETAIL_LEVERS:
            p = self.forecast_dir / f"at_retail_fraction_2030_{scen}.csv"
            if p.exists():
                self.retail_levers[scen] = pd.read_csv(p)
                print(f"  Loaded at_retail_fraction_2030_{scen}.csv ({len(self.retail_levers[scen])} rows)")
        p = self.forecast_dir / "at_retail_fraction_2030_renaissance_qcSundayDereg.csv"
        self.retail_dereg = pd.read_csv(p) if p.exists() else None
        if self.retail_dereg is not None:
            print(f"  Loaded {p.name} ({len(self.retail_dereg)} rows)")

        # Observed 2022 baseline (Step5 aggregated_excl.csv -- small, 2022 subset only)
        p = self.step5_obs_dir / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
        if p.exists():
            usecols = HOM_COLS + WRK_COLS + RET_COLS + ACT_COLS + ["CYCLE_YEAR", "DDAY_STRATA", "LFTAG", "PR"]
            usecols = list(dict.fromkeys(usecols))
            full = pd.read_csv(p, usecols=lambda c: c in usecols, low_memory=False)
            self.obs_2022 = full[full["CYCLE_YEAR"] == 2022].reset_index(drop=True)
            print(f"  Loaded observed 2022 from {p.name} ({len(full):,} all-cycle rows, "
                  f"{len(self.obs_2022):,} 2022 rows)")
        else:
            self.obs_2022 = None
            print(f"  [WARN] {p} not found")

        # Hotel Section-8 scorecard (already computed by Track B)
        p = self.hotel_dir / "section8_hotel_gate_scorecard.csv"
        self.hotel_scorecard = pd.read_csv(p) if p.exists() else None
        print(f"  {'Loaded' if self.hotel_scorecard is not None else '[WARN] missing'} {p.name}"
              + (f" ({len(self.hotel_scorecard)} rows)" if self.hotel_scorecard is not None else ""))

        p = self.hotel_processed_dir / "hotel_multiplier_2030.csv"
        self.hotel_mult_2030 = pd.read_csv(p) if p.exists() else None
        p2 = self.hotel_processed_dir / "hotel_multiplier_lookup.csv"
        self.hotel_lookup = pd.read_csv(p2) if p2.exists() else None
        p3 = self.hotel_processed_dir / "hotel_diurnal_shape_st.csv"
        self.hotel_st = pd.read_csv(p3) if p3.exists() else None
        for nm, obj in (("hotel_multiplier_2030.csv", self.hotel_mult_2030),
                        ("hotel_multiplier_lookup.csv", self.hotel_lookup),
                        ("hotel_diurnal_shape_st.csv", self.hotel_st)):
            print(f"  {'Loaded' if obj is not None else '[WARN] missing'} {nm}"
                  + (f" ({len(obj)} rows)" if obj is not None else ""))

    # ══════════════════════════════════════════════════════════════════════
    # Section 1 -- Training Convergence (INFO only, per manager instruction)
    # ══════════════════════════════════════════════════════════════════════

    def validate_training_convergence(self) -> None:
        print("\n[Section 1] Training convergence (INFO -- transcribed from job 1133427 .out log) ...")
        rows = [
            ("Stage A (base, cycle 2005) epoch-1 gate", "val_js=0.145647 loss=0.152584",
             "n/a", "PASS per build-log [Gate 3]; early-stopped epoch 12/30, final val_js=0.0230."),
            ("Stage B (fine-tune on 2010) epoch-1 gate", "val_js=0.069598 loss=0.127721",
             "n/a", "PASS per build-log; early-stopped epoch 15/30, final val_js=0.0126."),
            ("Stage C (fine-tune on 2015) epoch-1 gate", "val_js=0.068201 loss=0.148528",
             "n/a", "PASS per build-log; early-stopped epoch 10/30, final val_js=0.0271. "
             "COVID triple-signal check ran here (see Section 3.5-3.7)."),
            ("Stage D (fine-tune on 2022) epoch-1 gate", "val_js=0.070414 loss=0.167152",
             "n/a", "PASS per build-log; early-stopped epoch 29/30, final val_js=0.0229."),
            ("Stage E (pooled 2030 recency-weighted) epoch-1 gate", "val_js=0.028679 loss=0.137301",
             "n/a", "PASS per build-log; early-stopped epoch 14/30, final val_js=0.0233."),
            ("Fixed-alpha loss (1.0:0.5:0.3) + PCGrad across 3 task groups "
             "(resid=act+home+cop, work, retail)", "confirmed applied (code-level, per the "
             "2026-07-22 build session's own port notes)", "both present",
             "Checkpoints store weights only, no embedded loss-schedule metadata -- "
             "confirmed by the port diff, not a runtime introspection."),
            ("No catastrophic forgetting: final-stage (pooled 2030) val_js vs Stage-A val_js",
             "0.0233 vs 0.0230 (ratio 1.01x)", "< 1.5x Stage-A val_js",
             "INFO cross-reference only (per-stage val_js is a POOLED aggregate across all "
             "3 channels + both old/new heads, not the strict per-old-head decomposition "
             "the val-plan gate specifies) -- shown because the number happens to be "
             "available and reassuring, not scored as the literal gate."),
        ]
        for desc, val, thr, note in rows:
            self.add("s1", "1.x", desc, "all", "n/a", val, thr, "INFO", note)

    # ══════════════════════════════════════════════════════════════════════
    # Section 2 -- True Future Test (INFO only)
    # ══════════════════════════════════════════════════════════════════════

    def validate_true_future_test(self) -> None:
        print("\n[Section 2] True Future Test (INFO -- no per-phase JS transcribed to a scoreable gate) ...")
        self.add("s2", "2.x",
                  "True Future Test JS per phase (W_2005-on-2010 / W_2010_ft-on-2015 / "
                  "W_2015_ft-on-2022 / W_2022_ft-on-pooled-2030) x DDAY_STRATA x channel",
                  "all", "n/a", "n/a -- see per-stage epoch-1 val_js in Section 1", "n/a", "INFO",
                  "Per-phase fine-tune early-stop val_js (Section 1) is the nearest available "
                  "proxy -- it is the model's loss on its OWN held-out validation split at each "
                  "transition, not a strict True-Future-Test (which additionally requires a "
                  "uniform-baseline comparison and channel split). No such decomposition was "
                  "logged for the full-corpus run.")
        if self.dm:
            proxy = []
            for name, dm in self.dm.items():
                wd = dm[dm["stratum"] == 1]
                if len(wd) > 0:
                    proxy.append(f"{name.replace('DRIFT_MATRIX_', '').replace('_4split','')}: "
                                 f"aggregate_JS(WD)={float(wd['aggregate_JS'].iloc[0]):.4f}")
            self.add("s2", "2.y",
                      "Nearest available proxy: DRIFT_MATRIX aggregate_JS at WD stratum (model "
                      "applied to the NEXT cycle's held-out data)", "all", "n/a",
                      "; ".join(proxy), "n/a (informational)", "INFO", "")

    # ══════════════════════════════════════════════════════════════════════
    # Section 3 -- DRIFT_MATRIX plausibility (+ retail axis)
    # ══════════════════════════════════════════════════════════════════════

    def validate_drift_matrices(self) -> None:
        print("\n[Section 3] DRIFT_MATRIX plausibility (+ retail axis) ...")
        if not self.dm:
            print("  [SKIP] no DRIFT_MATRIX files loaded")
            return

        for name, dm in self.dm.items():
            act_cols = [c for c in dm.columns if c.startswith("JS_act")]
            wd = dm[dm["stratum"] == 1]
            if len(wd) == 0:
                continue
            n_act_gt = int((wd[act_cols].values.flatten() > 0.01).sum())
            self.add("s3", f"3.{name}-home", f"{name} non-trivial (home, count of 14 JS_actNN "
                      "cols > 0.01 at WD row)", "home", "n/a", n_act_gt, ">= 3",
                      "PASS" if n_act_gt >= 3 else "WARN")
            at_work_wd = float(wd["AT_WORK_drift"].iloc[0])
            self.add("s3", f"3.{name}-work", f"{name} non-trivial (work, |AT_WORK_drift| at WD)",
                      "work", "n/a", abs(at_work_wd), ">= 0.01",
                      "PASS" if abs(at_work_wd) >= 0.01 else "WARN")
            # 3.8 -- non-trivial retail activity count [Leg-3 NEW]
            at_ret_wd = float(wd["AT_RETAIL_drift"].iloc[0])
            self.add("s3", f"3.8.{name}", f"{name} non-trivial retail (|AT_RETAIL_drift| at WD row)",
                      "retail", "n/a", abs(at_ret_wd), ">= 0.001 (retail is a small-magnitude channel)",
                      "PASS" if abs(at_ret_wd) >= 0.001 else "WARN",
                      "Retail is the smallest channel (~2% positive); threshold set an order of "
                      "magnitude below home/work's 0.01 for that reason, project-chosen.")

        # 3.5-3.7 -- COVID triple signal in DRIFT_MATRIX_1522 (home UP, work DOWN, retail DOWN)
        if "DRIFT_MATRIX_1522_4split" in self.dm:
            wd1522 = self.dm["DRIFT_MATRIX_1522_4split"]
            wd_row = wd1522[wd1522["stratum"] == 1].iloc[0]
            h = float(wd_row["AT_HOME_drift"])
            w = float(wd_row["AT_WORK_drift"])
            r = float(wd_row["AT_RETAIL_drift"])
            covid_note = (
                f"Build-log [COVID triple-signal check] transcribed verbatim (job 1133427): "
                f"WD AT_HOME_drift={h:+.4f}  AT_WORK_drift={w:+.4f}  AT_RETAIL_drift={r:+.4f}. "
                f"The build's own script flagged all 3 WARN and concluded 'NOT all 3 legs "
                f"confirmed -- soft blocker, investigate' (val plan SS3: soft blocker, does not "
                f"hard-fail). Direction check: expected home INCREASE (>=+5pp), work DECREASE, "
                f"retail DECREASE through the COVID-era 2015->2022 transition."
            )
            self.add("s3", "3.5", "1522 COVID home signal: AT_HOME_drift >= +5pp (WD)", "home",
                      "n/a", h, ">= +0.05", "PASS" if h >= 0.05 else "WARN", covid_note)
            self.add("s3", "3.6", "1522 COVID work signal: AT_WORK_drift directional decrease (WD)",
                      "work", "n/a", w, "< 0 (decrease)", "PASS" if w < 0 else "WARN",
                      "AT_WORK_drift is POSITIVE (generated work > observed at temp=0), the "
                      "wrong direction for a WFH-surge signal.")
            self.add("s3", "3.7", "1522 COVID retail signal: AT_RETAIL_drift directional decrease "
                      "(WD) [Leg-3 NEW]", "retail", "n/a", r, "< 0 (decrease)",
                      "PASS" if r < 0 else "WARN",
                      "AT_RETAIL_drift is ~0 (+0.00015), essentially flat -- the in-store-shopping "
                      "COVID collapse is not captured at temp=0.0 greedy decode. Consistent with "
                      "the home/work legs also failing direction -- this looks like a shared "
                      "temp=0.0 greedy-decode limitation (the deliverable itself uses T=0.7 + "
                      "nucleus + min-dwell, never greedy -- see Section 4/5 for the metric that "
                      "actually matters for the shipped deliverable).")
            all3 = (h >= 0.05) and (w < 0) and (r < 0)
            self.add("s3", "3.5-3.7-summary", "COVID triple-signal: all 3 legs confirmed "
                      "co-occurring", "all", "n/a", f"home={h>=0.05} work={w<0} retail={r<0}",
                      "all True", "WARN" if not all3 else "PASS",
                      "Soft blocker per val plan SS3 -- does not hard-fail Step 6. Build-log's own "
                      "verdict transcribed verbatim, not re-derived independently.")

        n_nan = n_inf = 0
        for dm in self.dm.values():
            numeric = dm.select_dtypes(include=[np.number]).values
            n_nan += int(np.isnan(numeric).sum())
            n_inf += int(np.isinf(numeric).sum())
        self.add("s3", "3.NaNInf", "All matrices complete: NaN/Inf count across all 3 matrices",
                  "all", "n/a", n_nan + n_inf, "0", "PASS" if (n_nan + n_inf) == 0 else "FAIL")

        shapes = {name: dm.shape for name, dm in self.dm.items()}
        consistent = len(set(shapes.values())) <= 1
        self.add("s3", "3.shapes", "Matrix dimensions consistent across all 3 matrices", "all",
                  "n/a", str(shapes), "all equal", "PASS" if consistent else "FAIL")

        try:
            fig, axes = plt.subplots(3, 3, figsize=(13, 8), sharey="row")
            for col, (name, dm) in enumerate(self.dm.items()):
                ax_h, ax_w, ax_r = axes[0, col], axes[1, col], axes[2, col]
                strata = [STRATUM_LABEL[s] for s in dm["stratum"]]
                for ax, colname, color, lbl in [(ax_h, "AT_HOME_drift", "#1976d2", "home"),
                                                  (ax_w, "AT_WORK_drift", "#e65100", "work"),
                                                  (ax_r, "AT_RETAIL_drift", "#7b1fa2", "retail")]:
                    ax.bar(strata, dm[colname], color=color)
                    ax.axhline(0, color="#333", linewidth=0.8)
                    if col == 0:
                        ax.set_ylabel(lbl)
                ax_h.set_title(name.replace("DRIFT_MATRIX_", "").replace("_4split", ""), fontsize=9)
            fig.suptitle("DRIFT_MATRIX signed mean-shift per stratum (home/work/retail)", fontsize=10)
            plt.tight_layout()
            self.charts["s3_bars"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s3_bars failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 4 -- 2022 backcast (joint gate, profile metric)
    # ══════════════════════════════════════════════════════════════════════

    def validate_backcasting_2022(self) -> None:
        print("\n[Section 4] 2022 backcasting reconstruction (joint, profile metric) ...")
        if self.recon_2022 is None:
            print("  [SKIP] reconstructed_2022_diaries_4split.csv unavailable")
            return

        # ── PRIMARY: build's own per-stratum gate table (see module docstring) ──
        primary_note = (
            "PRIMARY evidence: transcribed VERBATIM from job 1133427's own stdout "
            "(.out lines 140-151) -- the production D1-backcast stage computed this "
            "gate table in-process, with correct DDAY_STRATA labels available BEFORE "
            "the CSV write dropped that column. reconstructed_2022_diaries_4split.csv "
            "as delivered has NO DDAY_STRATA/LFTAG/PR of its own (confirmed by reading "
            "its header), so an independent per-stratum recomputation would require "
            "row-order-aligning against the Step-4 raw training pool the backcast was "
            "conditioned on (seed_3_g3fix/augmented_diaries.csv, 418MB, cluster-only) "
            "-- explicitly out of this session's local staging scope (Step-0 downloaded "
            "only the files the manager listed, not the raw training pool). The build-log "
            "table is therefore treated as authoritative, not re-derived from a smaller "
            "or misaligned local proxy that would silently misrepresent it."
        )
        gate_mad = 0.10
        for s in (1, 2, 3):
            g = BUILD_BACKCAST_GATE_TABLE[s]
            lbl = STRATUM_LABEL[s]
            home_pass = (g["MADhome"] < gate_mad) and (g["dHome_pp"] <= 2.0)
            self.add("s4", f"4.{s}.home", f"Reconstruction {lbl} (home): shape-JS={g['JShome']:.4f} "
                      f"MAD={g['MADhome']:.4f} level={g['dHome_pp']:.2f}pp", "home", "n/a",
                      g["dHome_pp"], "MAD<0.10 AND level<=2pp",
                      "PASS" if home_pass else "FAIL", primary_note if s == 1 else "")
            work_pass = (g["MADwork"] < gate_mad) and (g["dWork_pp"] <= 3.0)
            self.add("s4", f"4.{s}.work", f"Reconstruction {lbl} (work): shape-JS={g['JSwork']:.4f} "
                      f"MAD={g['MADwork']:.4f} level={g['dWork_pp']:.2f}pp", "work", "n/a",
                      g["dWork_pp"], "MAD<0.10 AND level<=3pp",
                      "PASS" if work_pass else "FAIL")
            ret_pass = (g["MADret"] < gate_mad) and (g["dRet_pp"] <= 1.5)
            self.add("s4", f"4.{s}.retail", f"Reconstruction {lbl} (retail): shape-JS={g['JSret']:.4f} "
                      f"MAD={g['MADret']:.4f} level={g['dRet_pp']:.2f}pp [Leg-3 NEW]", "retail",
                      "n/a", g["dRet_pp"], "MAD<0.10 AND level<=1.5pp",
                      "PASS" if ret_pass else "FAIL")
            self.add("s4", f"4.{s}.act", f"Reconstruction {lbl}: activity-marginal JS", "activity",
                      "n/a", g["JSact"], "< 0.05 (project-chosen)",
                      "PASS" if g["JSact"] < 0.05 else "WARN")

        # ── Stratum-1 characterization (task-mandated: real failure or artifact?) ──
        s1 = BUILD_BACKCAST_GATE_TABLE[1]
        characterization = (
            "STRATUM-1 (WEEKDAY) CHARACTERIZATION -- REAL BACKCAST GAP, NOT A SMALL-CHANNEL "
            "METRIC ARTIFACT. Evidence: the profile-MAD+level metric was specifically adopted "
            "(runbook SS6F, val plan SS4) because raw flattened-binary JS saturates near ln(2) "
            "on SPARSE channels -- retail (~2% positive) was flagged as the worst case for that "
            "artifact. But here retail is the channel that PASSES CLEANLY on stratum 1 "
            f"(MAD={s1['MADret']:.4f}, level={s1['dRet_pp']:.2f}pp, both well inside gate), while "
            f"the DENSE, well-populated home ({s1['MADhome']:.4f} MAD / {s1['dHome_pp']:.2f}pp "
            f"level) and work ({s1['MADwork']:.4f} MAD / {s1['dWork_pp']:.2f}pp level) channels "
            "are the ones that fail -- the OPPOSITE of the sparse-channel-artifact pattern the "
            "metric was designed to guard against. Sat/Sun (strata 2/3) pass cleanly on ALL "
            "three channels with small residuals (<1.1pp level everywhere), so this is not a "
            "systemic backcast failure either -- it is specific to weekday home/work structure. "
            "Plausible mechanism (not independently re-derivable without a per-respondent join, "
            "flagged as a hypothesis, not a proven cause): the reconstructed WFH_RATE "
            f"({BUILD_WFH_RATE['reconstructed']:.4f}) sits {BUILD_WFH_RATE['delta_pp']:.2f}pp "
            "above observed 2022 -- itself within its own +/-5pp gate (PASS) -- but a small "
            "population-level WFH-rate shift, concentrated onto specific business-hours slots, "
            "is consistent with home/work per-slot LEVEL residuals an order of magnitude larger "
            "than the aggregate WFH_RATE gate alone would suggest. VERDICT: real, weekday-"
            "specific home/work generalization gap in the backcast -- documented and scored "
            "FAIL, not downgraded to WARN/INFO (no equally strong evidence exists that it is an "
            "artifact; the task instruction 'do NOT paper it over' governs here)."
        )
        # NOTE status=INFO (not FAIL): this row is the disposition/evidence NARRATIVE for the
        # SAME finding already independently scored FAIL twice above (4.1.home, 4.1.work) --
        # counting it a 3rd time would double-count one underlying issue in the tally.
        self.add("s4", "4.1.characterization", "Stratum-1 backcast gap: real failure vs "
                  "small-channel-metric artifact", "home+work", "n/a",
                  "REAL (weekday-specific), not a sparse-channel artifact", "n/a (evidence-based)",
                  "INFO", characterization)

        self.add("s4", "4.WFH_RATE", "WFH_RATE reconstruction (employed, biz-hours slots 11-26)",
                  "all", "n/a", BUILD_WFH_RATE["delta_pp"], "<= 5pp",
                  "PASS" if BUILD_WFH_RATE["delta_pp"] <= 5.0 else "FAIL",
                  f"observed={BUILD_WFH_RATE['observed']:.4f} reconstructed="
                  f"{BUILD_WFH_RATE['reconstructed']:.4f} (build-log, job 1133427)")

        # ── SECONDARY: pooled independent cross-check from on-disk files ────────
        if self.obs_2022 is not None and len(self.obs_2022) > 0:
            n_rec = len(self.recon_2022)
            gh = self.recon_2022[HOM_COLS].values.astype(float)
            gw = self.recon_2022[WRK_COLS].values.astype(float)
            gr = self.recon_2022[RET_COLS].values.astype(float)
            ga = self.recon_2022[ACT_COLS].values.astype(int)
            oh = self.obs_2022[HOM_COLS].values.astype(float)
            ow = self.obs_2022[WRK_COLS].values.astype(float)
            orr = self.obs_2022[RET_COLS].values.astype(float)

            secondary_note = (
                f"SECONDARY cross-check only -- NOT the authoritative gate (see 4.1.characterization "
                f"note for why). Pools the FULL {n_rec:,}-row backcast (all strata, unlabelled) "
                f"against the Step5 census-linked observed-2022 subset (n={len(self.obs_2022):,}, "
                "a DIFFERENT, smaller, differently-sourced population -- NOT row-aligned to the "
                "backcast). Shown for shape-sanity corroboration only."
            )
            js_h_pool = js_divergence(oh.mean(0), gh.mean(0))
            js_w_pool = js_divergence(ow.mean(0), gw.mean(0))
            js_r_pool = js_divergence(orr.mean(0), gr.mean(0))
            mad_h_pool = float(np.abs(oh.mean(0) - gh.mean(0)).mean())
            mad_w_pool = float(np.abs(ow.mean(0) - gw.mean(0)).mean())
            mad_r_pool = float(np.abs(orr.mean(0) - gr.mean(0)).mean())
            self.add("s4", "4.secondary.home", "Pooled cross-check (home): shape-JS / MAD",
                      "home", "n/a", f"JS={js_h_pool:.4f} MAD={mad_h_pool:.4f}", "n/a (secondary)",
                      "INFO", secondary_note)
            self.add("s4", "4.secondary.work", "Pooled cross-check (work): shape-JS / MAD",
                      "work", "n/a", f"JS={js_w_pool:.4f} MAD={mad_w_pool:.4f}", "n/a (secondary)",
                      "INFO", "")
            self.add("s4", "4.secondary.retail", "Pooled cross-check (retail): shape-JS / MAD",
                      "retail", "n/a", f"JS={js_r_pool:.4f} MAD={mad_r_pool:.4f}", "n/a (secondary)",
                      "INFO", "")

            # anti-copy sanity
            disagree_home = float(np.mean(np.abs((oh[:n_rec].clip(0, 1) > 0.5).astype(int)
                                                   - (gh > 0.5).astype(int)))) if len(oh) >= n_rec else float("nan")

            top5 = top5_activities(self.obs_2022[ACT_COLS].values.flatten())
            for code, share in top5.items():
                gen_share = float((ga.flatten() == code).mean())
                diff = abs(gen_share - share) * 100
                self.add("s4", f"4.top5-act{int(code)}", f"Top-5 activity (pooled): code {int(code)} "
                          f"(obs share {share*100:.2f}%)", "activity", "n/a", diff, "n/a (secondary)",
                          "INFO", f"obs={share*100:.2f}% recon={gen_share*100:.2f}%")

            try:
                fig, axs = plt.subplots(1, 3, figsize=(15, 4))
                slots = np.arange(1, 49)
                axs[0].plot(slots, oh.mean(0) * 100, color="k", lw=1.3, ls=":", label="Obs 2022 (pooled)")
                axs[0].plot(slots, gh.mean(0) * 100, color="#1976d2", lw=1.6, label="Recon 2022 (pooled)")
                axs[1].plot(slots, ow.mean(0) * 100, color="k", lw=1.3, ls=":", label="Obs 2022 (pooled)")
                axs[1].plot(slots, gw.mean(0) * 100, color="#e65100", lw=1.6, label="Recon 2022 (pooled)")
                axs[2].plot(slots, orr.mean(0) * 100, color="k", lw=1.3, ls=":", label="Obs 2022 (pooled)")
                axs[2].plot(slots, gr.mean(0) * 100, color="#7b1fa2", lw=1.6, label="Recon 2022 (pooled)")
                for ax, t in zip(axs, ["AT_HOME", "AT_WORK", "AT_RETAIL"]):
                    ax.set_title(f"{t}: Observed vs. Reconstructed 2022 (pooled, secondary)")
                    ax.set_xlabel("30-min slot (1=04:00)"); ax.set_ylabel("%")
                    ax.legend(fontsize=7); ax.set_xlim(1, 48)
                plt.tight_layout()
                self.charts["s4_overlay"] = _fig_to_b64(fig)
            except Exception as e:
                print(f"  [chart WARN] s4_overlay failed: {e}")

        # per-stratum build-log bar chart
        try:
            fig, axs = plt.subplots(1, 3, figsize=(13, 4))
            strata = [1, 2, 3]
            labels = [STRATUM_LABEL[s] for s in strata]
            for ax, key, title in [(axs[0], "dHome_pp", "Home level gap (pp)"),
                                    (axs[1], "dWork_pp", "Work level gap (pp)"),
                                    (axs[2], "dRet_pp", "Retail level gap (pp)")]:
                vals = [BUILD_BACKCAST_GATE_TABLE[s][key] for s in strata]
                colors = ["#c62828" if BUILD_BACKCAST_GATE_TABLE[s]["build_verdict"] == "FAIL"
                          else "#2e7d32" for s in strata]
                ax.bar(labels, vals, color=colors)
                ax.set_title(title); ax.axhline(0, color="#333", lw=0.5)
            fig.suptitle("Build-log backcast level gaps per stratum (job 1133427, PRIMARY evidence)")
            plt.tight_layout()
            self.charts["s4_buildlog_bars"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s4_buildlog_bars failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 5 -- 2030 schedule plausibility (per band, + retail block)
    # ══════════════════════════════════════════════════════════════════════

    def validate_2030_schedule_plausibility(self) -> None:
        print("\n[Section 5] 2030 schedule plausibility (per band + retail block) ...")
        if self.synth_2030 is None:
            print("  [SKIP] 2030 deliverable not available")
            return
        df = self.synth_2030

        wd_at_home_2022 = wd_at_work_2022 = wfh_day_2022_obs = None
        if self.obs_2022 is not None and len(self.obs_2022) > 0:
            wd22 = self.obs_2022[self.obs_2022["DDAY_STRATA"] == 1]
            wd_at_home_2022 = float(wd22[HOM_COLS].values.mean()) * 100
            wd_at_work_2022 = float(wd22[WRK_COLS].values.mean()) * 100
            wfh_day_2022_obs = compute_wfh_day_share(wd22)

        wfh_day_share_by_band = {}
        for band in BANDS:
            sub = df[df["BAND"] == band]
            if len(sub) == 0:
                continue
            blabel = BAND_LABEL[band]

            at_home_overall = float(sub[HOM_COLS].values.mean()) * 100
            self.add("s5", "5.1", "2030 AT_HOME overall mean", "home", blabel, at_home_overall,
                      "in [40,90]", "PASS" if 40 <= at_home_overall <= 90 else "FAIL")

            wd = sub[sub["DDAY_STRATA"] == 1]
            we = sub[sub["DDAY_STRATA"] != 1]
            wd_at = float(wd[HOM_COLS].values.mean()) * 100 if len(wd) else float("nan")
            we_at = float(we[HOM_COLS].values.mean()) * 100 if len(we) else float("nan")
            self.add("s5", "5.2", "WD AT_HOME < WE AT_HOME (structural)", "home", blabel,
                      f"WD={wd_at:.2f}% WE={we_at:.2f}%", "WD < WE",
                      "PASS" if wd_at < we_at else "FAIL")

            night_acts = sub[ACT_COLS[:8]].values.flatten()
            sleep_pct = float((night_acts == SLEEP_CODE).mean()) * 100
            self.add("s5", "5.3", "Night sleep (slots 1-8, code 5)", "activity", blabel,
                      sleep_pct, ">= 60%", "PASS" if sleep_pct >= 60 else "WARN")

            wfh_day_share = compute_wfh_day_share(wd)
            wfh_day_share_by_band[band] = wfh_day_share
            lo, hi = WFH_TARGET[band]
            self.add("s5", "5.17-19", f"Band {blabel} WFH-day share target", "home", blabel,
                      wfh_day_share, f"in [{lo},{hi}]", "PASS" if lo <= wfh_day_share <= hi else "WARN")

            wd_at_work = float(wd[WRK_COLS].values.mean()) * 100 if len(wd) else float("nan")
            morning = wd[[f"wrk30_{i:03d}" for i in range(12, 17)]].values.mean() if len(wd) else np.nan
            afternoon = wd[[f"wrk30_{i:03d}" for i in range(22, 27)]].values.mean() if len(wd) else np.nan
            lunch = wd[[f"wrk30_{i:03d}" for i in range(17, 20)]].values.mean() if len(wd) else np.nan
            morning_thr = {"conservative": 0.30, "hybrid": 0.20, "fullyhybrid": 0.15}[band]
            self.add("s5", "5.8", "Office diurnal: WD morning peak (slots 12-16)", "work", blabel,
                      float(morning), f">= {morning_thr}", "PASS" if morning >= morning_thr else "WARN")
            peak = max(morning, afternoon) if not (np.isnan(morning) or np.isnan(afternoon)) else np.nan
            if not np.isnan(peak) and peak > 0:
                self.add("s5", "5.10", "Office diurnal: WD lunch dip (slots 17-19)", "work", blabel,
                          float(lunch), f"< peak*0.70 ({peak*0.70:.4f})",
                          "PASS" if lunch < peak * 0.70 else "WARN")

            we_wrk = float(we[WRK_COLS].values.mean()) if len(we) else np.nan
            self.add("s5", "5.14", "WD > WE AT_WORK structural (office side)", "work", blabel,
                      f"WD={wd_at_work/100:.4f} WE={we_wrk:.4f}", "WD > WE",
                      "PASS" if (wd_at_work / 100) > we_wrk else "FAIL")

        if len(wfh_day_share_by_band) == 3:
            cd, hd, fd = (wfh_day_share_by_band["conservative"], wfh_day_share_by_band["hybrid"],
                          wfh_day_share_by_band["fullyhybrid"])
            monotone_d = fd > hd > cd
            self.add("s5", "5.16", "Monotone WFH-day share: fullyhybrid > hybrid > conservative",
                      "home", "all", f"C={cd:.4f} H={hd:.4f} F={fd:.4f}", "strict monotone",
                      "PASS" if monotone_d else "FAIL")

        self.add("s5", "5.2.characterization", "5.2 WD>=WE finding: genuine small-magnitude "
                  "scenario effect vs calibration defect", "home", "all",
                  "small (0.33-1.27pp), shrinks as WFH intensity rises -- not obviously a defect",
                  "n/a (evidence-based)", "INFO",
                  "5.2 FAILs by a SMALL margin in all 3 bands: conservative +1.27pp, hybrid "
                  "+1.00pp, fullyhybrid +0.33pp (WD minus WE). Two candidate mechanisms: (a) the "
                  "calibration chain anchors weekend home (Stage C1) to the FIXED observed-2022 "
                  "weekend level, independent of office-WFH band, while weekday home is shaped by "
                  "Stage B's weekday-work-tail trim PLUS the band-specific WFH-day reweight -- "
                  "there was never a cross-stratum WD<WE ordering constraint enforced anywhere in "
                  "the chain, only within-stratum fidelity to real 2022 anchors; (b) a genuinely "
                  "emergent 2030 scenario feature where elevated WFH narrows or erases the "
                  "historical weekday<weekend home-occupancy gap. The band pattern argues AGAINST "
                  "a naive 'more WFH pushes weekday home up' story though -- the gap actually "
                  "SHRINKS from conservative (lowest WFH) to fullyhybrid (highest WFH), the "
                  "opposite of what that story predicts; more consistent with (a): the fixed "
                  "weekend-2022 anchor simply sits a small, roughly constant amount below "
                  "whatever the band-specific weekday level lands on. Scored FAIL per the literal "
                  "gate (not silently relaxed), but this is a design consequence of two "
                  "independently-anchored stages, not an obvious pipeline bug -- worth a "
                  "cross-stratum consistency constraint in a future calibration revision if the "
                  "manager wants WD<WE enforced as a hard invariant.")

        # ═══════════════════════════════════════════════════════════════════
        # 5.20-5.27 -- Retail block [Leg-3 NEW]
        # ═══════════════════════════════════════════════════════════════════
        print("  -- Retail block (5.20-5.27) --")

        # Use the pooled base retail profile from the lever files (day-type x slot),
        # PR_GROUP=ALL rows, and PR_GROUP=QC/AB rows for the province-conditioned checks.
        if "plateau" in self.retail_levers:

            def prof(lev_df, day_type: str, pr_group: str, slot_lo: int, slot_hi: int,
                     col="at_retail_fraction_2030_base"):
                sub = lev_df[(lev_df["day_type"] == day_type) & (lev_df["PR_GROUP"] == pr_group)
                             & (lev_df["slot"] >= slot_lo) & (lev_df["slot"] <= slot_hi)]
                return float(sub[col].mean()) if len(sub) else float("nan")

            for scen, mult in RETAIL_LEVERS.items():
                if scen not in self.retail_levers:
                    continue
                lev = self.retail_levers[scen]   # BUG FIX: must be scenario-specific, not fixed to plateau
                lever_col = "at_retail_fraction_2030_levered"
                wd_midday = prof(lev, "weekday", "ALL", 17, 20, lever_col)
                lo_b, hi_b = 0.06 * mult, 0.10 * mult
                self.add("s5", "5.20", f"[{scen}] Weekday midday (12-14h, slots 17-20) retail",
                          "retail", scen, wd_midday, f"in [{lo_b:.4f},{hi_b:.4f}] (0.06-0.10 x lever)",
                          "PASS" if lo_b <= wd_midday <= hi_b else "WARN")

                sat_peak = prof(lev, "saturday", "ALL", 19, 24, lever_col)
                lo_s, hi_s = 0.09 * mult, 0.12 * mult
                self.add("s5", "5.21", f"[{scen}] Saturday peak (13-16h, slots 19-24) retail", "retail",
                          scen, sat_peak, f"in [{lo_s:.4f},{hi_s:.4f}] (0.09-0.12 x lever)",
                          "PASS" if lo_s <= sat_peak <= hi_s else "WARN")
                wd_all = prof(lev, "weekday", "ALL", 1, 48, lever_col)
                self.add("s5", "5.21b", f"[{scen}] Saturday peak > weekday midday (reverse of office)",
                          "retail", scen, f"Sat={sat_peak:.4f} WDmid={wd_midday:.4f}", "Sat > WDmid",
                          "PASS" if sat_peak > wd_midday else "WARN")

                night = prof(lev, "weekday", "ALL", 1, 8, lever_col)
                self.add("s5", "5.23", f"[{scen}] Night retail (slots 1-8) ~0", "retail", scen, night,
                          "in [0.000,0.003]", "PASS" if night <= 0.003 else "WARN")

                # 5.24 -- lever exactness (already self-checked at lever-generation time;
                # re-verify here from the on-disk file, band ratio = levered/base)
                sub = lev[(lev["PR_GROUP"] == "ALL") & (lev["at_retail_fraction_2030_base"] > 0)]
                ratios = sub["at_retail_fraction_2030_levered"] / sub["at_retail_fraction_2030_base"]
                max_dev = float((ratios - mult).abs().max()) if len(ratios) else float("nan")
                self.add("s5", "5.24", f"[{scen}] Lever exactness: levered/base == {mult} +/- 0.01",
                          "retail", scen, max_dev, "<= 0.01", "PASS" if max_dev <= 0.01 else "FAIL",
                          "Exact by construction (Stage=multiply base by scalar) -- any deviation "
                          "would mean the lever leaked through a downstream normalization step. "
                          f"(retail_lever script re-loaded from disk: {self.retail_levers[scen]['multiplier'].iloc[0] if scen in self.retail_levers else 'n/a'})")

            # 5.22 -- Sunday QC/AB level (respondent-PR subset, from RAW per-band files, pooled bands)
            if self.raw_bands:
                pooled_raw = pd.concat(self.raw_bands.values(), ignore_index=True)
                for pr_code, pr_name, lo, hi in [(QC_PR, "QC", 0.04, 0.07), (AB_PR, "AB", 0.06, 0.10)]:
                    sub = pooled_raw[(pooled_raw["PR"] == pr_code) & (pooled_raw["DDAY_STRATA"] == 3)]
                    v = float(sub[RET_COLS].values.mean()) if len(sub) else float("nan")
                    self.add("s5", "5.22", f"Sunday retail level, {pr_name} respondents (raw "
                              "pre-calibration base, respondent-PR subset)", "retail", pr_name, v,
                              f"in [{lo},{hi}]", "PASS" if lo <= v <= hi else "WARN",
                              f"n={len(sub):,} respondent-slot rows.")

                # 5.25 -- QC-Sunday restricted-default ratio check
                qc_sun = pooled_raw[(pooled_raw["PR"] == QC_PR) & (pooled_raw["DDAY_STRATA"] == 3)][RET_COLS].values.mean(0)
                qc_sat = pooled_raw[(pooled_raw["PR"] == QC_PR) & (pooled_raw["DDAY_STRATA"] == 2)][RET_COLS].values.mean(0)
                ratio = float(qc_sun.max() / qc_sat.max()) if qc_sat.max() > 0 else float("nan")
                self.add("s5", "5.25", "QC-Sunday restricted-default: Sun/Sat peak ratio (natural, "
                          "no manual file)", "retail", "QC", ratio, "in [0.60,0.75]",
                          "PASS" if 0.60 <= ratio <= 0.75 else "WARN",
                          "FINDING (not papered over): the runbook's assumption that the historical "
                          "QC trading-hours restriction 'naturally encodes through QC respondents "
                          "in training data, no manual adjustment needed' does NOT clearly survive "
                          f"into the pooled 2030 generation -- observed ratio {ratio:.4f} is well "
                          "above the expected 0.60-0.75 window (Sunday nearly as busy as Saturday, "
                          "rather than restricted). Two candidate explanations, NOT independently "
                          "adjudicated here: (a) the retail head's resolution at the doubly-"
                          "conditioned PR=QC x DDAY_STRATA=Sunday x channel=retail cell is one of "
                          "the sparsest slices in the whole schema, so the PEAK-slot estimate may "
                          "be noisy; (b) a genuine generation-fidelity limitation where the "
                          "province x day-type x channel interaction is under-resolved relative to "
                          "the main-effect signals. Scored WARN (diurnal-shape-check severity, "
                          "consistent with the office 5.8-5.13 precedent), not FAIL -- but flagged "
                          "for Step-7/manager attention before relying on the QC-restricted-default "
                          "assumption downstream.")

                # 5.27 -- no retail-WFH cross-contamination (per-band retail day-mean spread)
                per_band_mean = {b: float(self.raw_bands[b][RET_COLS].values.mean()) for b in BANDS}
                spread = max(per_band_mean.values()) - min(per_band_mean.values())
                self.add("s5", "5.27", "No retail-WFH cross-contamination: office-band spread in "
                          "retail day-mean", "retail", "all", spread, "<= 0.001 (float tolerance)",
                          "PASS" if spread <= 0.001 else ("WARN" if spread <= 0.01 else "FAIL"),
                          f"Per-band retail day-mean: " + ", ".join(f"{b}={v:.5f}" for b, v in per_band_mean.items())
                          + f". Spread={spread:.5f} ({spread/np.mean(list(per_band_mean.values()))*100:.1f}% "
                          "relative). Plausible mechanism: the build-log's own D2-phase WARN "
                          "messages document band-specific 'resampling with replacement' when the "
                          "WFH-day / office-day candidate pools are smaller than the target count "
                          "(office pool 11,466 < target 15,226 for conservative; WFH pool 6,990 < "
                          "target 7,382 for fullyhybrid) -- this changes the exact respondent MIX "
                          "per band, which can move retail by a small residual amount even though "
                          "retail itself isn't targeted by the reweight. Small in absolute terms, "
                          "not zero -- scored per the graduated tolerance above, not silently passed.")

                # 5.25b -- deregulated QC-Sunday extra file check
                if self.retail_dereg is not None:
                    dereg_base_peak = float(self.retail_dereg["at_retail_fraction_2030_base"].max())
                    dereg_ratio = dereg_base_peak / qc_sat.max() if qc_sat.max() > 0 else float("nan")
                    self.add("s5", "5.25b", "QC-Sunday deregulated (extra file) shows uplift vs "
                              "restricted default", "retail", "QC_DEREG", dereg_ratio,
                              f"> restricted-default ratio ({ratio:.4f})",
                              "PASS" if dereg_ratio > ratio else "WARN",
                              "Deregulated variant rescales QC's Sunday shape to AB's own empirical "
                              "Sun/Sat ratio (AB deregulated since 1985) -- exact by construction, "
                              "so this checks internal consistency of the extra file, not a new "
                              "independent signal.")

            # 5.26 -- continuity vs 2022 (retail level, WD)
            if self.obs_2022 is not None and len(self.obs_2022) > 0:
                wd22_ret = float(self.obs_2022[self.obs_2022["DDAY_STRATA"] == 1][RET_COLS].values.mean())
                wd30_ret_plateau = prof(self.retail_levers["plateau"], "weekday", "ALL", 1, 48,
                                         "at_retail_fraction_2030_levered")
                cont = abs(wd30_ret_plateau - wd22_ret) * 100
                self.add("s5", "5.26", "2030 WD retail continuity vs 2022 (plateau/default scenario)",
                          "retail", "plateau", cont, "<= 10pp",
                          "PASS" if cont <= 10 else "WARN",
                          f"2030(plateau)={wd30_ret_plateau:.4f} 2022={wd22_ret:.4f}")

        # Charts
        try:
            fig, axs = plt.subplots(1, 3, figsize=(15, 4))
            slots = np.arange(1, 49)
            colors = {"conservative": "#1976d2", "hybrid": "#388e3c", "fullyhybrid": "#e65100"}
            for band in BANDS:
                sub = df[(df["BAND"] == band) & (df["DDAY_STRATA"] == 1)]
                if len(sub) == 0:
                    continue
                axs[0].plot(slots, sub[HOM_COLS].values.mean(0) * 100, color=colors[band], lw=1.8, label=BAND_LABEL[band])
                axs[1].plot(slots, sub[WRK_COLS].values.mean(0) * 100, color=colors[band], lw=1.8, label=BAND_LABEL[band])
                axs[2].plot(slots, sub[RET_COLS].values.mean(0) * 100, color=colors[band], lw=1.8, label=BAND_LABEL[band])
            axs[0].set_title("hom30 WD: 2030 bands"); axs[0].set_ylabel("%")
            axs[1].set_title("wrk30 WD: 2030 bands")
            axs[2].set_title("ret30 WD: 2030 bands (should be ~band-invariant, gate 5.27)")
            for ax in axs:
                ax.set_xlabel("30-min slot (1=04:00)"); ax.legend(fontsize=7); ax.set_xlim(1, 48)
            plt.tight_layout()
            self.charts["s5_overlay"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s5_overlay failed: {e}")

        try:
            if self.retail_levers:
                fig, ax = plt.subplots(figsize=(9, 4))
                slots = np.arange(1, 49)
                colors_l = {"shift": "#c62828", "plateau": "#1565c0", "renaissance": "#2e7d32"}
                for scen, lev in self.retail_levers.items():
                    sub = lev[(lev["day_type"] == "weekday") & (lev["PR_GROUP"] == "ALL")].sort_values("slot")
                    ax.plot(slots, sub["at_retail_fraction_2030_levered"].values, color=colors_l.get(scen, "k"),
                            lw=1.8, label=f"{scen} ({RETAIL_LEVERS[scen]})")
                ax.set_title("Retail lever: weekday levered profile per scenario")
                ax.set_xlabel("30-min slot (1=04:00)"); ax.set_ylabel("at_retail_fraction_2030")
                ax.legend(fontsize=8)
                plt.tight_layout()
                self.charts["s5_retail_lever"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s5_retail_lever failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 6 -- BEM output readiness (3-way)
    # ══════════════════════════════════════════════════════════════════════

    def validate_bem_readiness(self) -> None:
        print("\n[Section 6] BEM output readiness (3-way mutex) ...")
        if self.synth_2030 is None:
            print("  [SKIP] 2030 deliverable not available")
            return
        df = self.synth_2030

        act_ok = all(c in df.columns for c in ACT_COLS)
        hom_ok = all(c in df.columns for c in HOM_COLS)
        wrk_ok = all(c in df.columns for c in WRK_COLS)
        ret_ok = all(c in df.columns for c in RET_COLS)
        self.add("s6", "6.1", "Schema: act30 columns present", "activity", "all",
                  "yes" if act_ok else "no", "100%", "PASS" if act_ok else "FAIL")
        self.add("s6", "6.2", "Schema: hom30 columns present", "home", "all",
                  "yes" if hom_ok else "no", "100%", "PASS" if hom_ok else "FAIL")
        self.add("s6", "6.3", "Schema: wrk30 columns present", "work", "all",
                  "yes" if wrk_ok else "no", "100%", "PASS" if wrk_ok else "FAIL")
        self.add("s6", "6.3b", "Schema: ret30 columns present [Leg-3 NEW]", "retail", "all",
                  "yes" if ret_ok else "no", "100%", "PASS" if ret_ok else "FAIL")

        act_vals = df[ACT_COLS].values
        act_rng = int(act_vals.min()) >= 1 and int(act_vals.max()) <= 14
        self.add("s6", "6.4", "act30 range", "activity", "all",
                  f"[{int(act_vals.min())},{int(act_vals.max())}]", "[1,14]",
                  "PASS" if act_rng else "FAIL")
        for name, cols in [("hom30", HOM_COLS), ("wrk30", WRK_COLS), ("ret30", RET_COLS)]:
            vals = set(np.unique(df[cols].values))
            self.add("s6", f"6.range.{name}", f"{name} range", name.replace("30", ""), "all",
                      str(sorted(vals)), "{0,1}", "PASS" if vals <= {0, 1} else "FAIL")

        hom_arr = df[HOM_COLS].values
        wrk_arr = df[WRK_COLS].values
        ret_arr = df[RET_COLS].values
        hw = int(((hom_arr == 1) & (wrk_arr == 1)).sum())
        hr = int(((hom_arr == 1) & (ret_arr == 1)).sum())
        wr = int(((wrk_arr == 1) & (ret_arr == 1)).sum())
        n_conflict = hw + hr + wr
        self.add("s6", "6.7", "3-way mutual exclusion (home&work + home&retail + work&retail) "
                  "[generalized 3-way]", "all", "all", n_conflict,
                  "0 (hard gate, post-6H cleanup)", "PASS" if n_conflict == 0 else "FAIL",
                  f"home&work={hw} home&retail={hr} work&retail={wr}")

        band_counts = df["BAND"].value_counts()
        for band in BANDS:
            n = int(band_counts.get(band, 0))
            self.add("s6", "6.8", f"Row count for band {band}", "all", BAND_LABEL[band], n,
                      ">= 37,000", "PASS" if n >= 37000 else "FAIL")

        band_ok = set(df["BAND"].unique()) == set(BANDS)
        self.add("s6", "6.9", "BAND column completeness", "all", "all",
                  str(sorted(df["BAND"].unique())), "{conservative,hybrid,fullyhybrid}",
                  "PASS" if band_ok else "FAIL")

        strata_ok_all = all(set(df[df["BAND"] == b]["DDAY_STRATA"].unique()) == {1, 2, 3} for b in BANDS)
        self.add("s6", "6.10", "DDAY_STRATA completeness (per band)", "all", "all",
                  str(sorted(df["DDAY_STRATA"].unique())), "{1,2,3} in each band",
                  "PASS" if strata_ok_all else "FAIL")

        cy_ok = (df["CYCLE_YEAR"] == 2030).all()
        self.add("s6", "6.11", "CYCLE_YEAR tag", "all", "all",
                  str(sorted(df["CYCLE_YEAR"].unique())), "{2030}", "PASS" if cy_ok else "FAIL")

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

    # ══════════════════════════════════════════════════════════════════════
    # Section 8 -- Hotel SARIMA (NEW, non-GSS, wired from Track B)
    # ══════════════════════════════════════════════════════════════════════

    def validate_hotel_sarima(self) -> None:
        print("\n[Section 8] Hotel SARIMA (Track B, wired in) ...")
        if self.hotel_scorecard is None:
            print("  [SKIP] section8_hotel_gate_scorecard.csv not found")
            return

        for _, r in self.hotel_scorecard.iterrows():
            # Normalize "FAIL (PARTIAL)" etc. to the 4 canonical tally buckets (PASS/WARN/FAIL/INFO);
            # the original nuance ("PARTIAL") is preserved verbatim in the note/detail text, not lost.
            raw_status = str(r["status"])
            norm_status = "FAIL" if raw_status.startswith("FAIL") else raw_status
            self.add("s8", str(r["gate"]), f"{r['check']} [{r['PR']}]", "hotel", str(r["PR"]),
                      str(r["detail"])[:180], str(r["threshold"]), norm_status,
                      f"raw_status={raw_status}; severity={r['severity_class']}; full detail: {r['detail']}")

        # Schema/integrity re-checks against the locally-staged Track B output files
        if self.hotel_mult_2030 is not None:
            n = len(self.hotel_mult_2030)
            rates_ok = self.hotel_mult_2030["occupancy_rate"].between(0, 1, inclusive="right").all() \
                if "occupancy_rate" in self.hotel_mult_2030.columns else None
            self.add("s8", "8.9-local", "hotel_multiplier_2030.csv local re-check: rows=72, rates in (0,1]",
                      "hotel", "ALL", f"rows={n} rates_ok={rates_ok}", "rows=72, rates in (0,1]",
                      "PASS" if (n == 72 and rates_ok) else "WARN")
        if self.hotel_st is not None:
            n = len(self.hotel_st)
            self.add("s8", "8.10-local", "hotel_diurnal_shape_st.csv local re-check: 48x2=96 rows",
                      "hotel", "ALL", n, "96", "PASS" if n == 96 else "WARN")

        try:
            if self.hotel_mult_2030 is not None and {"MONTH", "PR", "BAND", "occupancy_rate"}.issubset(self.hotel_mult_2030.columns):
                fig, ax = plt.subplots(figsize=(9, 4))
                for pr in self.hotel_mult_2030["PR"].unique():
                    for band in self.hotel_mult_2030["BAND"].unique():
                        sub = self.hotel_mult_2030[(self.hotel_mult_2030["PR"] == pr)
                                                     & (self.hotel_mult_2030["BAND"] == band)].sort_values("MONTH")
                        if len(sub):
                            ax.plot(sub["MONTH"], sub["occupancy_rate"], marker="o", ms=3,
                                    label=f"{pr}-{band}")
                ax.set_xlabel("Month"); ax.set_ylabel("Occupancy rate")
                ax.set_title("Hotel 2030 monthly occupancy by PR x band")
                ax.legend(fontsize=6, ncol=3)
                plt.tight_layout()
                self.charts["s8_hotel_2030"] = _fig_to_b64(fig)
        except Exception as e:
            print(f"  [chart WARN] s8_hotel_2030 failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Section 7 -- Summary scorecard
    # ══════════════════════════════════════════════════════════════════════

    def generate_summary_table(self) -> dict:
        print("\n[Section 7] Summary scorecard ...")
        tally = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
        tally_gss = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
        tally_hotel = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
        for section, rows in self.checks.items():
            for r in rows:
                tally[r["status"]] += 1
                if section == "s8":
                    tally_hotel[r["status"]] += 1
                else:
                    tally_gss[r["status"]] += 1
        print(f"  OVERALL   PASS={tally['PASS']}  WARN={tally['WARN']}  FAIL={tally['FAIL']}  INFO={tally['INFO']}")
        print(f"  GSS(1-6)  PASS={tally_gss['PASS']}  WARN={tally_gss['WARN']}  FAIL={tally_gss['FAIL']}  INFO={tally_gss['INFO']}")
        print(f"  HOTEL(8)  PASS={tally_hotel['PASS']}  WARN={tally_hotel['WARN']}  FAIL={tally_hotel['FAIL']}  INFO={tally_hotel['INFO']}")
        print(f"  Non-closure discipline: Step 6 {'CAN' if tally_gss['FAIL'] == 0 else 'CANNOT'} be "
              f"declared done on GSS channels ({tally_gss['FAIL']} FAIL). Per the additive-safety "
              "principle, hotel-channel FAILs never block GSS/Track-A sign-off.")
        self._tally_gss = tally_gss
        self._tally_hotel = tally_hotel
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
        summary_color = "#2e7d32" if self._tally_gss["FAIL"] == 0 else "#c62828"

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
            "Per the manager's instruction: no on-disk per-epoch metric artifact exists to "
            "score against a threshold, so all rows are INFO -- but this leg's job 1133427 "
            ".out log happens to carry real per-epoch loss/val_js numbers (richer evidence "
            "than Leg-2 had), transcribed here as INFO context, never gated.")
        body += section_html("2 &mdash; True Future Test (INFO only)", "s2", ())
        body += section_html("3 &mdash; DRIFT_MATRIX Plausibility (+ retail axis)", "s3", ("s3_bars",),
            "COVID triple-signal (3.5-3.7) is a soft blocker per the val plan -- WARN, not FAIL. "
            "Build-log's own verdict ('NOT all 3 legs confirmed') transcribed verbatim.")
        body += section_html("4 &mdash; 2022 Backcasting Reconstruction (joint gate, profile metric)",
            "s4", ("s4_buildlog_bars", "s4_overlay"),
            "PRIMARY evidence = the production job's own per-stratum gate table (job 1133427 "
            ".out, transcribed verbatim -- see 4.1.characterization for the full stratum-1 "
            "real-vs-artifact analysis). SECONDARY rows are an independent pooled cross-check "
            "against a different, smaller, non-row-aligned observed population, for shape-"
            "sanity corroboration only.")
        body += section_html("5 &mdash; 2030 Schedule Plausibility (per band + retail block)", "s5",
            ("s5_overlay", "s5_retail_lever"),
            "Retail block (5.20-5.27) is NEW for Leg-3. Gate 5.25 surfaces a genuine finding: "
            "the QC-Sunday restricted-trading-hours ratio does not clearly survive into the "
            "pooled 2030 generation -- flagged, not papered over.")
        body += section_html("6 &mdash; BEM Output Readiness (3-way mutex)", "s6", ("s6_strata",))
        body += section_html("8 &mdash; Hotel SARIMA (Track B, non-GSS)", "s8", ("s8_hotel_2030",),
            "Additive-safety principle: hotel FAILs never block GSS/Track-A sign-off, but do "
            "block Step-7 hotel injection for the affected province until resolved or accepted "
            "with caveat.")

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Step 6 (Leg-3 4-split) Validation Report</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1300px;margin:40px auto;padding:0 20px;color:#222}}
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
<h1>Step 6 (Leg-3 4-split) &mdash; Four-Channel Longitudinal Forecasting + Hotel SARIMA Validation Report</h1>
<div class="summary">
  <strong>GSS channels (Sections 1-6, scored gates only; excludes hotel Section 8):</strong>
  <span style="color:{summary_color};font-weight:bold">{self._tally_gss['PASS']}/{self._tally_gss['PASS']+self._tally_gss['WARN']+self._tally_gss['FAIL']} PASS,
  {self._tally_gss['FAIL']} FAIL</span>
  &nbsp;|&nbsp; Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
  <div class="scorecard">
    <div class="card pass">PASS<br>{tally['PASS']}</div>
    <div class="card warn">WARN<br>{tally['WARN']}</div>
    <div class="card fail">FAIL<br>{tally['FAIL']}</div>
    <div class="card info">INFO<br>{tally['INFO']}</div>
  </div>
  <p style="font-size:12.5px;margin-top:8px">Hotel (Section 8) tallies separately:
  PASS={self._tally_hotel['PASS']} WARN={self._tally_hotel['WARN']} FAIL={self._tally_hotel['FAIL']} --
  per the additive-safety principle a hotel FAIL never blocks GSS/Track-A sign-off.</p>
  <p style="font-size:12.5px;font-weight:bold;color:{summary_color}">
  Non-closure discipline: Step 6 {'CAN' if self._tally_gss['FAIL']==0 else 'is NOT'} declared done
  on GSS channels ({self._tally_gss['FAIL']} FAIL on Sections 1-6).</p>
</div>
{body}
<hr/><p style="font-size:11px;color:#888">
Step 6 (Leg-3 4-split) GSSCanada Occupancy Pipeline &mdash; Concordia University postdoc project.<br>
Report generated by 3rdJ_06_longitudinalForecasting_4split_val.py.<br>
Inputs: 2030_synthetic_diaries_4split_calibrated_mindwell_C.csv, reconstructed_2022_diaries_4split.csv,
DRIFT_MATRIX_{{0510,1015,1522}}_4split.csv, 2030_diaries_{{band}}_raw.csv x3,
at_retail_fraction_2030_*.csv (all under Step6_docs/outputs_step6/), Step5_docs/outputs_step5/
3rdJ_25CEN_aug_Full_Aggregated_excl.csv (observed 2022 baseline), and Track B's
outputs_step6_hotel/section8_hotel_gate_scorecard.csv + 0_Occupancy/{{forecasts,processed}}/hotel_*.csv.<br>
Threshold provenance: (1) ASHRAE Guideline 14 (NMBE/CV(RMSE), same-period-only), (2) literature-
confirmed (C2ST~0.50, dwell-KS), (3) project-chosen (KL&lt;0.05, EMD&lt;0.05, presence-RMS&le;5pp,
MAD&lt;0.10, hotel MAE&lt;0.05, band bars) &mdash; see the val plan's Threshold Provenance Note.
</p></body></html>"""
        return html

    def run_all(self) -> None:
        self.validate_training_convergence()
        self.validate_true_future_test()
        self.validate_drift_matrices()
        self.validate_backcasting_2022()
        self.validate_2030_schedule_plausibility()
        self.validate_bem_readiness()
        self.validate_hotel_sarima()
        tally = self.generate_summary_table()

        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.outputs_dir / "step6_validation_report.html"
        report_html = self.build_html_report()
        report_path.write_text(report_html, encoding="utf-8")
        print(f"\nReport saved: {report_path}")
        print(f"Final scorecard: OVERALL PASS={tally['PASS']} WARN={tally['WARN']} FAIL={tally['FAIL']} INFO={tally['INFO']}")
        print(f"  GSS(1-6): PASS={self._tally_gss['PASS']} WARN={self._tally_gss['WARN']} "
              f"FAIL={self._tally_gss['FAIL']} INFO={self._tally_gss['INFO']}")
        print(f"  HOTEL(8): PASS={self._tally_hotel['PASS']} WARN={self._tally_hotel['WARN']} "
              f"FAIL={self._tally_hotel['FAIL']} INFO={self._tally_hotel['INFO']}")


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Step 6 (Leg-3 4-split) validation report generator")
    ap.add_argument("--forecast_dir", default=str(here / "outputs_step6"))
    ap.add_argument("--step5_obs_dir",
                     default=str(here.parents[0] / "Step5_docs" / "outputs_step5"))
    ap.add_argument("--hotel_dir", default=str(here / "outputs_step6_hotel"))
    ap.add_argument("--hotel_processed_dir",
                     default=str(here.parents[2] / "0_Occupancy" / "processed"))
    ap.add_argument("--outputs_dir", default=str(here / "outputs_step6"))
    args = ap.parse_args()

    # hotel_multiplier_2030.csv lives in 0_Occupancy/forecasts/, not processed/ -- patch dir resolution
    validator = LongitudinalForecastingValidator4Split(
        forecast_dir=args.forecast_dir,
        step5_obs_dir=args.step5_obs_dir,
        hotel_dir=args.hotel_dir,
        hotel_processed_dir=args.hotel_processed_dir,
        outputs_dir=args.outputs_dir,
    )
    # hotel_multiplier_2030.csv actually lives in 0_Occupancy/forecasts/ per the runbook --
    # reload it from there if the processed/ dir didn't have it.
    if validator.hotel_mult_2030 is None:
        forecasts_dir = Path(args.hotel_processed_dir).parent / "forecasts"
        p = forecasts_dir / "hotel_multiplier_2030.csv"
        if p.exists():
            validator.hotel_mult_2030 = pd.read_csv(p)
            print(f"  Loaded hotel_multiplier_2030.csv from {p} ({len(validator.hotel_mult_2030)} rows)")

    validator.run_all()


if __name__ == "__main__":
    main()
