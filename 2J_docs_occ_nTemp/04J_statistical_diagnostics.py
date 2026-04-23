"""
04J_statistical_diagnostics.py — Step 4J: Statistical Diagnostic Battery (CPU-only)

Augments 04H (AT_HOME marginals) and 04I (activity + co-presence marginals) with:
  T1. Bootstrap CIs (1000 resamples) on prevalence gaps per channel
  T2. Calibration curves per co-presence channel + AT_HOME
      (matched synthetic σ vs observed binary label from same respondent)
  T3. Joint distributions: (activity × AT_HOME), (activity × Alone), (Alone × AT_HOME)
      with χ²-of-independence Cramér's V
  T4. χ² / KS tests per (cycle × stratum × class) with Bonferroni-corrected α
  T5. Composite score S (lower = better); pinned weights from §10.4 of step4_training.md

Usage:
    python 04J_statistical_diagnostics.py \\
        --data_dir outputs_step4 \\
        --step3_dir outputs_step3 \\
        --output_json outputs_step4/diagnostics_v4_statistical.json \\
        --n_bootstrap 1000

Usage (sample / dry-run):
    python 04J_statistical_diagnostics.py --sample
"""

import argparse
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import scipy.stats as stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

N_SLOTS   = 48
CYCLES    = [2005, 2010, 2015, 2022]
STRATA    = [1, 2, 3]
STRATUM_LABEL = {1: "Weekday", 2: "Saturday", 3: "Sunday"}

ACT_COLS   = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_CODES  = list(range(1, 15))
HOM_COLS   = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

COP_NAMES = [
    "Alone", "Spouse", "Children", "parents",
    "friends", "others", "colleagues",
]

# Composite score weights (pinned — no post-hoc tuning; see §10.4)
# Each component normalized to comparable magnitude (see §10.4 formula).
W1_AT_HOME  = 0.20   # AT_HOME gap RMS (pp / 10)
W2_COP_GAP  = 0.35   # max co-presence gap (pp / 10)
W3_ACT_JS   = 0.35   # activity JS mean × 10
W4_CAL_MAE  = 0.10   # mean co-presence calibration MAE × 10


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",     default=None)
    p.add_argument("--step3_dir",    default=None)
    p.add_argument("--output_json",  default=None)
    p.add_argument("--n_bootstrap",  type=int, default=1000)
    p.add_argument("--sample",       action="store_true")
    p.add_argument("--no_plot",      action="store_true")
    return p.parse_args()


def _resolve_paths(args):
    sfx = "_test" if args.sample else ""
    data_dir  = args.data_dir  or os.path.join(SCRIPT_DIR, f"outputs_step4{sfx}")
    step3_dir = args.step3_dir or os.path.join(SCRIPT_DIR, "outputs_step3")
    out_json  = args.output_json or os.path.join(data_dir, "diagnostics_v4_statistical.json")
    return data_dir, step3_dir, out_json


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_frames(data_dir, step3_dir, sample):
    sfx = "_SAMPLE" if sample else ""
    aug_path = os.path.join(data_dir, f"augmented_diaries{sfx}.csv")
    aug = pd.read_csv(aug_path, low_memory=False)

    obs_aug = aug[aug["IS_SYNTHETIC"] == 0].copy()
    syn_aug = aug[aug["IS_SYNTHETIC"] == 1].copy()

    obs_ext_path = os.path.join(step3_dir, f"hetus_30min{sfx}.csv")
    obs_ext = pd.read_csv(obs_ext_path, low_memory=False) if os.path.exists(obs_ext_path) else None

    return aug, obs_aug, syn_aug, obs_ext


# ── T1: Bootstrap CIs ─────────────────────────────────────────────────────────

def _bootstrap_mean_ci(vals: np.ndarray, n_boot: int, rng):
    """Return (ci_lo, ci_hi, mean) via percentile bootstrap."""
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return (float("nan"), float("nan"), float("nan"))
    boot = rng.choice(vals, size=(n_boot, len(vals)), replace=True).mean(axis=1)
    return (float(np.percentile(boot, 2.5)),
            float(np.percentile(boot, 97.5)),
            float(vals.mean()))


def run_bootstrap_cis(obs_aug: pd.DataFrame, syn_aug: pd.DataFrame,
                      n_boot: int = 1000) -> dict:
    """T1: Bootstrap CIs on prevalence gaps for COP channels and AT_HOME."""
    rng = np.random.default_rng(42)
    results = {}

    # Co-presence channels
    cop_results = {}
    for cn in COP_NAMES:
        cols = [f"{cn}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
        cols_ok = [c for c in cols if c in obs_aug.columns and c in syn_aug.columns]
        if not cols_ok:
            continue

        # Use per-respondent row means to avoid allocating n_boot × n_slots arrays
        obs_vals = obs_aug[cols_ok].mean(axis=1).to_numpy().astype(float)
        syn_vals = syn_aug[cols_ok].mean(axis=1).to_numpy().astype(float)

        obs_lo, obs_hi, obs_mean = _bootstrap_mean_ci(obs_vals, n_boot, rng)
        syn_lo, syn_hi, syn_mean = _bootstrap_mean_ci(syn_vals, n_boot, rng)
        gap_pp = (syn_mean - obs_mean) * 100.0

        # Bootstrap CI on the gap itself
        obs_v = obs_vals[np.isfinite(obs_vals)]
        syn_v = syn_vals[np.isfinite(syn_vals)]
        n_min = min(len(obs_v), len(syn_v))
        if n_min > 0:
            boot_gap = (
                rng.choice(syn_v, size=(n_boot, n_min), replace=True).mean(axis=1) -
                rng.choice(obs_v, size=(n_boot, n_min), replace=True).mean(axis=1)
            ) * 100.0
            gap_lo = float(np.percentile(boot_gap, 2.5))
            gap_hi = float(np.percentile(boot_gap, 97.5))
            statistically_real = not (gap_lo <= 0 <= gap_hi)
        else:
            gap_lo, gap_hi, statistically_real = float("nan"), float("nan"), False

        cop_results[cn] = {
            "obs_mean": obs_mean,
            "syn_mean": syn_mean,
            "gap_pp": gap_pp,
            "gap_ci_lo_pp": gap_lo,
            "gap_ci_hi_pp": gap_hi,
            "statistically_real": statistically_real,
        }

    # AT_HOME
    hom_cols_ok = [c for c in HOM_COLS if c in obs_aug.columns and c in syn_aug.columns]
    if hom_cols_ok:
        obs_h = obs_aug[hom_cols_ok].mean(axis=1).to_numpy().astype(float)
        syn_h = syn_aug[hom_cols_ok].mean(axis=1).to_numpy().astype(float)
        obs_lo, obs_hi, obs_mean = _bootstrap_mean_ci(obs_h, n_boot, rng)
        syn_lo, syn_hi, syn_mean = _bootstrap_mean_ci(syn_h, n_boot, rng)
        gap_pp = (syn_mean - obs_mean) * 100.0
        obs_v = obs_h[np.isfinite(obs_h)]
        syn_v = syn_h[np.isfinite(syn_h)]
        n_min = min(len(obs_v), len(syn_v))
        if n_min > 0:
            boot_gap = (
                rng.choice(syn_v, size=(n_boot, n_min), replace=True).mean(axis=1) -
                rng.choice(obs_v, size=(n_boot, n_min), replace=True).mean(axis=1)
            ) * 100.0
            gap_lo = float(np.percentile(boot_gap, 2.5))
            gap_hi = float(np.percentile(boot_gap, 97.5))
            statistically_real = not (gap_lo <= 0 <= gap_hi)
        else:
            gap_lo, gap_hi, statistically_real = float("nan"), float("nan"), False

        at_home_result = {
            "obs_mean": obs_mean,
            "syn_mean": syn_mean,
            "gap_pp": gap_pp,
            "gap_ci_lo_pp": gap_lo,
            "gap_ci_hi_pp": gap_hi,
            "statistically_real": statistically_real,
        }
    else:
        at_home_result = {}

    return {"copresence": cop_results, "at_home": at_home_result}


def plot_bootstrap_cis(bootstrap_result: dict, out_path: str):
    cop = bootstrap_result.get("copresence", {})
    at_home = bootstrap_result.get("at_home", {})
    if not cop and not at_home:
        return

    names = list(cop.keys()) + (["AT_HOME"] if at_home else [])
    gaps  = [cop[n]["gap_pp"] for n in cop] + ([at_home.get("gap_pp", 0)] if at_home else [])
    lo    = [cop[n]["gap_ci_lo_pp"] for n in cop] + ([at_home.get("gap_ci_lo_pp", 0)] if at_home else [])
    hi    = [cop[n]["gap_ci_hi_pp"] for n in cop] + ([at_home.get("gap_ci_hi_pp", 0)] if at_home else [])

    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(names))
    colors = ["#C44E52" if abs(g) > 3.0 else "#4C72B0" for g in gaps]
    ax.bar(x, gaps, color=colors, alpha=0.8)
    ax.errorbar(x, gaps,
                yerr=[np.array(gaps) - np.array(lo), np.array(hi) - np.array(gaps)],
                fmt="none", color="black", capsize=4)
    ax.axhline(0, color="k", linewidth=0.8)
    ax.axhline(3.0, color="gray", linewidth=0.6, linestyle="--")
    ax.axhline(-3.0, color="gray", linewidth=0.6, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_ylabel("Syn − Obs gap (pp)  [95% bootstrap CI]")
    ax.set_title("T1: Bootstrap CIs on prevalence gaps")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# ── T2: Calibration curves ────────────────────────────────────────────────────

def _calibration_matched(aug: pd.DataFrame, col_prefix: str,
                         n_bins: int = 10) -> dict:
    """
    Matched calibration: for each synthetic row, join to the observed row of
    the same respondent (same occID × CYCLE_YEAR) and treat its binary values
    as ground-truth labels.

    Returns dict with bin_centers, bin_means_sigma, bin_means_label, mae, n_per_bin.
    """
    cols = [f"{col_prefix}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    cols_ok = [c for c in cols if c in aug.columns]
    if len(cols_ok) < N_SLOTS:
        return {}

    obs_frame = aug[aug["IS_SYNTHETIC"] == 0][["occID", "CYCLE_YEAR"] + cols_ok].copy()
    syn_frame = aug[aug["IS_SYNTHETIC"] == 1][["occID", "CYCLE_YEAR"] + cols_ok].copy()

    # Rename obs columns to avoid clash in merge
    obs_rename = {c: c + "_obs" for c in cols_ok}
    syn_rename = {c: c + "_syn" for c in cols_ok}
    obs_frame = obs_frame.rename(columns=obs_rename)
    syn_frame = syn_frame.rename(columns=syn_rename)

    merged = syn_frame.merge(obs_frame, on=["occID", "CYCLE_YEAR"], how="inner")
    if len(merged) == 0:
        return {}

    syn_mat = merged[[c + "_syn" for c in cols_ok]].to_numpy(dtype=float)  # (n, 48)
    obs_mat = merged[[c + "_obs" for c in cols_ok]].to_numpy(dtype=float)  # (n, 48)

    sigma_flat = syn_mat.flatten()
    label_flat = obs_mat.flatten()

    # Remove NaN
    mask = np.isfinite(sigma_flat) & np.isfinite(label_flat)
    sigma_flat = sigma_flat[mask]
    label_flat = label_flat[mask]

    if len(sigma_flat) == 0:
        return {}

    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_centers = 0.5 * (edges[:-1] + edges[1:])
    bin_means_sigma = []
    bin_means_label = []
    n_per_bin = []

    for lo, hi in zip(edges[:-1], edges[1:]):
        mask_bin = (sigma_flat >= lo) & (sigma_flat < hi)
        n = int(mask_bin.sum())
        if n == 0:
            bin_means_sigma.append(float((lo + hi) / 2))
            bin_means_label.append(float("nan"))
        else:
            bin_means_sigma.append(float(sigma_flat[mask_bin].mean()))
            bin_means_label.append(float(label_flat[mask_bin].mean()))
        n_per_bin.append(n)

    # MAE: mean |bin_σ̄ − empirical_prevalence| over populated bins
    diffs = [abs(s - l) for s, l in zip(bin_means_sigma, bin_means_label)
             if not (np.isnan(s) or np.isnan(l))]
    mae = float(np.mean(diffs)) if diffs else float("nan")

    return {
        "bin_centers": [float(x) for x in bin_centers],
        "bin_means_sigma": bin_means_sigma,
        "bin_means_label": bin_means_label,
        "n_per_bin": n_per_bin,
        "mae": mae,
    }


def run_calibration(aug: pd.DataFrame) -> dict:
    """T2: Calibration curves for co-presence channels + AT_HOME."""
    results = {}
    for cn in COP_NAMES:
        cal = _calibration_matched(aug, cn)
        if cal:
            results[cn] = cal
            print(f"  [{cn}]  calibration MAE = {cal['mae']:.4f}")

    # AT_HOME uses column prefix "hom"
    hom_cal = _calibration_matched(aug, "hom")
    if hom_cal:
        results["AT_HOME"] = hom_cal
        print(f"  [AT_HOME] calibration MAE = {hom_cal['mae']:.4f}")

    return results


def plot_calibration(calibration_result: dict, out_path: str):
    channels = list(calibration_result.keys())
    if not channels:
        return

    n_panels = len(channels)
    ncols = 4
    nrows = (n_panels + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows), squeeze=False)

    for idx, cn in enumerate(channels):
        ax = axes[idx // ncols][idx % ncols]
        cal = calibration_result[cn]
        xs = cal["bin_means_sigma"]
        ys = cal["bin_means_label"]

        xs_plot = [x for x, y in zip(xs, ys) if not np.isnan(y)]
        ys_plot = [y for x, y in zip(xs, ys) if not np.isnan(y)]

        ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="perfect")
        ax.plot(xs_plot, ys_plot, "o-", color="#C44E52", markersize=4, label="model")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f"{cn}  MAE={cal['mae']:.3f}", fontsize=9)
        ax.set_xlabel("σ̄ in bin", fontsize=8)
        ax.set_ylabel("Empirical prevalence", fontsize=8)

    # Hide unused panels
    for idx in range(len(channels), nrows * ncols):
        axes[idx // ncols][idx % ncols].set_axis_off()

    axes[0][0].legend(fontsize=7)
    fig.suptitle("T2: Calibration curves (matched syn σ vs observed binary label)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# ── T3: Joint distributions ───────────────────────────────────────────────────

def _activity_mode_per_slot(df, act_cols_ok):
    """Return (n_rows,) array of most-common activity code across their diary."""
    arr = df[act_cols_ok].to_numpy()
    # Modal activity per row
    from scipy.stats import mode as scipy_mode
    result = scipy_mode(arr, axis=1)
    # scipy mode returns a ModeResult; .mode may be (n, 1) or (n,) depending on version
    m = result.mode
    if hasattr(m, 'flatten'):
        return m.flatten()
    return np.array(m)


def _cramer_v(chi2, n, dof):
    """Cramér's V from chi² statistic."""
    if n == 0 or dof == 0:
        return 0.0
    return float(np.sqrt(chi2 / (n * max(dof, 1))))


def run_joint_distributions(obs_aug: pd.DataFrame, syn_aug: pd.DataFrame) -> dict:
    """T3: Joint distributions for (activity × AT_HOME), (activity × Alone), (Alone × AT_HOME)."""
    act_cols_ok = [c for c in ACT_COLS if c in obs_aug.columns]
    hom_cols_ok = [c for c in HOM_COLS if c in obs_aug.columns]
    alone_cols  = [f"Alone30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    alone_cols_ok = [c for c in alone_cols if c in obs_aug.columns]

    results = {}

    def _flatten_two_channels(df, cols_a, cols_b):
        a = df[cols_a].to_numpy().flatten()
        b = df[cols_b].to_numpy().flatten()
        mask = np.isfinite(a.astype(float)) & np.isfinite(b.astype(float))
        return a[mask], b[mask]

    if act_cols_ok and hom_cols_ok:
        for label, df in [("obs", obs_aug), ("syn", syn_aug)]:
            a, b = _flatten_two_channels(df, act_cols_ok, hom_cols_ok)
            ct = pd.crosstab(pd.Series(a.astype(int), name="activity"),
                             pd.Series(b.astype(int), name="at_home"))
            chi2_stat, p_val, dof, _ = stats.chi2_contingency(ct.to_numpy(), correction=False)
            n_tot = int(ct.values.sum())
            results.setdefault("activity_x_at_home", {})[label] = {
                "chi2": float(chi2_stat), "p_value": float(p_val),
                "dof": int(dof), "cramer_v": _cramer_v(chi2_stat, n_tot, dof),
                "n": n_tot,
            }

    if act_cols_ok and alone_cols_ok:
        for label, df in [("obs", obs_aug), ("syn", syn_aug)]:
            a, b = _flatten_two_channels(df, act_cols_ok, alone_cols_ok)
            b_bin = (b.astype(float) >= 0.5).astype(int)
            ct = pd.crosstab(pd.Series(a.astype(int), name="activity"),
                             pd.Series(b_bin, name="alone"))
            chi2_stat, p_val, dof, _ = stats.chi2_contingency(ct.to_numpy(), correction=False)
            n_tot = int(ct.values.sum())
            results.setdefault("activity_x_alone", {})[label] = {
                "chi2": float(chi2_stat), "p_value": float(p_val),
                "dof": int(dof), "cramer_v": _cramer_v(chi2_stat, n_tot, dof),
                "n": n_tot,
            }

    if alone_cols_ok and hom_cols_ok:
        for label, df in [("obs", obs_aug), ("syn", syn_aug)]:
            a, b = _flatten_two_channels(df, alone_cols_ok, hom_cols_ok)
            a_bin = (a.astype(float) >= 0.5).astype(int)
            ct = pd.crosstab(pd.Series(a_bin, name="alone"),
                             pd.Series(b.astype(int), name="at_home"))
            chi2_stat, p_val, dof, _ = stats.chi2_contingency(ct.to_numpy(), correction=False)
            n_tot = int(ct.values.sum())
            results.setdefault("alone_x_at_home", {})[label] = {
                "chi2": float(chi2_stat), "p_value": float(p_val),
                "dof": int(dof), "cramer_v": _cramer_v(chi2_stat, n_tot, dof),
                "n": n_tot,
            }

    return results


def plot_joint_distributions(obs_aug: pd.DataFrame, syn_aug: pd.DataFrame,
                             out_path: str):
    """Plot activity × AT_HOME joint heatmaps (obs vs syn)."""
    act_cols_ok = [c for c in ACT_COLS if c in obs_aug.columns]
    hom_cols_ok = [c for c in HOM_COLS if c in obs_aug.columns]
    if not act_cols_ok or not hom_cols_ok:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, (label, df) in zip(axes, [("Observed", obs_aug), ("Synthetic", syn_aug)]):
        act_flat = df[act_cols_ok].to_numpy().flatten().astype(int)
        hom_flat = df[hom_cols_ok].to_numpy().flatten().astype(float)
        hom_bin = (hom_flat >= 0.5).astype(int)

        ct = pd.crosstab(pd.Series(act_flat, name="activity"),
                         pd.Series(hom_bin, name="AT_HOME"),
                         normalize="index")
        im = ax.imshow(ct.to_numpy(), aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_title(f"{label}: Activity × AT_HOME (row-normalized)")
        ax.set_xlabel("AT_HOME (0=away, 1=home)")
        ax.set_ylabel("Activity code")
        ax.set_yticks(range(len(ct.index)))
        ax.set_yticklabels(ct.index.tolist(), fontsize=7)
        plt.colorbar(im, ax=ax)

    fig.suptitle("T3: Joint distribution — Activity × AT_HOME")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# ── T4: χ² / KS tests ────────────────────────────────────────────────────────

def run_chi2_ks(obs_aug: pd.DataFrame, syn_aug: pd.DataFrame) -> dict:
    """T4: χ² on activity counts + KS on AT_HOME / COP-sigma per (cycle × stratum)."""
    act_cols_ok = [c for c in ACT_COLS if c in obs_aug.columns]
    hom_cols_ok = [c for c in HOM_COLS if c in obs_aug.columns]
    alone_cols  = [f"Alone30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    alone_cols_ok = [c for c in alone_cols if c in obs_aug.columns]

    n_cells = len(CYCLES) * len(STRATA)
    n_act_classes = len(ACT_CODES)
    bonf_alpha_chi2 = 0.05 / max(n_cells * n_act_classes, 1)
    bonf_alpha_ks   = 0.05 / max(n_cells, 1)

    chi2_results = {}
    ks_results   = {}

    for cy in CYCLES:
        for s in STRATA:
            key = f"{cy}_{s}"
            obs_sub = obs_aug[(obs_aug["CYCLE_YEAR"] == cy) & (obs_aug["DDAY_STRATA"] == s)]
            syn_sub = syn_aug[(syn_aug["CYCLE_YEAR"] == cy) & (syn_aug["DDAY_STRATA"] == s)]
            if len(obs_sub) == 0 or len(syn_sub) == 0:
                continue

            # χ² on activity count distributions
            if act_cols_ok:
                obs_act = obs_sub[act_cols_ok].to_numpy().flatten().astype(int)
                syn_act = syn_sub[act_cols_ok].to_numpy().flatten().astype(int)
                obs_counts = np.bincount(obs_act, minlength=15)[1:15].astype(float)
                syn_counts = np.bincount(syn_act, minlength=15)[1:15].astype(float)
                # Scale syn_counts to match obs total
                if obs_counts.sum() > 0 and syn_counts.sum() > 0:
                    syn_scaled = syn_counts / syn_counts.sum() * obs_counts.sum()
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        chi2_stat, p_val = stats.chisquare(obs_counts, f_exp=syn_scaled)
                    chi2_results[key] = {
                        "chi2": float(chi2_stat),
                        "p_value": float(p_val),
                        "reject_H0": bool(p_val < bonf_alpha_chi2),
                        "bonf_alpha": bonf_alpha_chi2,
                    }

            # KS on AT_HOME continuous distribution (syn is float σ)
            if hom_cols_ok:
                obs_h = obs_sub[hom_cols_ok].to_numpy().flatten().astype(float)
                syn_h = syn_sub[hom_cols_ok].to_numpy().flatten().astype(float)
                obs_h = obs_h[np.isfinite(obs_h)]
                syn_h = syn_h[np.isfinite(syn_h)]
                if len(obs_h) > 0 and len(syn_h) > 0:
                    ks_stat, ks_p = stats.ks_2samp(obs_h, syn_h)
                    ks_results.setdefault(key, {})["at_home"] = {
                        "ks_statistic": float(ks_stat),
                        "p_value": float(ks_p),
                        "reject_H0": bool(ks_p < bonf_alpha_ks),
                    }

            # KS on Alone sigma
            if alone_cols_ok:
                obs_a = obs_sub[alone_cols_ok].to_numpy().flatten().astype(float)
                syn_a = syn_sub[alone_cols_ok].to_numpy().flatten().astype(float)
                obs_a = obs_a[np.isfinite(obs_a)]
                syn_a = syn_a[np.isfinite(syn_a)]
                if len(obs_a) > 0 and len(syn_a) > 0:
                    ks_stat, ks_p = stats.ks_2samp(obs_a, syn_a)
                    ks_results.setdefault(key, {})["alone"] = {
                        "ks_statistic": float(ks_stat),
                        "p_value": float(ks_p),
                        "reject_H0": bool(ks_p < bonf_alpha_ks),
                    }

    return {"chi2": chi2_results, "ks": ks_results,
            "bonf_alpha_chi2": bonf_alpha_chi2, "bonf_alpha_ks": bonf_alpha_ks}


# ── T5: Composite score ───────────────────────────────────────────────────────

def compute_composite_score(bootstrap_result: dict,
                            calibration_result: dict,
                            obs_aug: pd.DataFrame,
                            syn_aug: pd.DataFrame) -> dict:
    """
    T5: S = w1*AT_HOME_gap_rms/10 + w2*cop_max_gap_pp/10 + w3*act_JS_mean*10 + w4*cop_cal_MAE*10
    Lower = better.  All components normalized so a unit change ≈ 10 pp gap or 0.01 JS.
    """
    # AT_HOME gap RMS: iterate per (cycle × stratum)
    hom_cols_ok = [c for c in HOM_COLS if c in obs_aug.columns and c in syn_aug.columns]
    at_home_gaps = []
    for cy in CYCLES:
        for s in STRATA:
            o = obs_aug[(obs_aug["CYCLE_YEAR"] == cy) & (obs_aug["DDAY_STRATA"] == s)]
            sx = syn_aug[(syn_aug["CYCLE_YEAR"] == cy) & (syn_aug["DDAY_STRATA"] == s)]
            if len(o) == 0 or len(sx) == 0 or not hom_cols_ok:
                continue
            gap = float((sx[hom_cols_ok].mean(axis=0) - o[hom_cols_ok].mean(axis=0)).abs().mean() * 100.0)
            at_home_gaps.append(gap)

    at_home_rms = float(np.sqrt(np.mean(np.array(at_home_gaps) ** 2))) if at_home_gaps else float("nan")

    # COP max gap (from bootstrap result)
    cop_data = bootstrap_result.get("copresence", {})
    cop_gaps = [abs(v["gap_pp"]) for v in cop_data.values() if not np.isnan(v.get("gap_pp", float("nan")))]
    cop_max_gap = float(max(cop_gaps)) if cop_gaps else float("nan")

    # Activity JS mean (recompute directly)
    act_cols_ok = [c for c in ACT_COLS if c in obs_aug.columns and c in syn_aug.columns]
    js_vals = []
    if act_cols_ok:
        for cy in CYCLES:
            for s in STRATA:
                o = obs_aug[(obs_aug["CYCLE_YEAR"] == cy) & (obs_aug["DDAY_STRATA"] == s)]
                sx = syn_aug[(syn_aug["CYCLE_YEAR"] == cy) & (syn_aug["DDAY_STRATA"] == s)]
                if len(o) == 0 or len(sx) == 0:
                    continue
                obs_arr = o[act_cols_ok].to_numpy()
                syn_arr = sx[act_cols_ok].to_numpy()
                obs_share = np.array([(obs_arr == c).mean(axis=0) for c in ACT_CODES]).T  # (48, 14)
                syn_share = np.array([(syn_arr == c).mean(axis=0) for c in ACT_CODES]).T
                eps = 1e-12
                m = 0.5 * (obs_share + syn_share + eps)
                js_per_slot = 0.5 * (
                    (obs_share + eps) * np.log2((obs_share + eps) / m)
                    + (syn_share + eps) * np.log2((syn_share + eps) / m)
                ).sum(axis=1)
                js_vals.append(float(js_per_slot.mean()))
    act_js_mean = float(np.mean(js_vals)) if js_vals else float("nan")

    # COP calibration MAE mean
    cal_maes = [v["mae"] for v in calibration_result.values()
                if isinstance(v, dict) and not np.isnan(v.get("mae", float("nan")))
                and v != calibration_result.get("AT_HOME")]
    cop_cal_mae = float(np.mean(cal_maes)) if cal_maes else float("nan")

    # Composite
    def _s(val, scale):
        return float("nan") if np.isnan(val) else val / scale

    components = {
        "at_home_gap_rms_pp": at_home_rms,
        "cop_max_gap_pp": cop_max_gap,
        "act_js_mean": act_js_mean,
        "cop_cal_mae": cop_cal_mae,
    }

    if all(not np.isnan(v) for v in components.values()):
        score = (W1_AT_HOME * at_home_rms / 10.0 +
                 W2_COP_GAP * cop_max_gap / 10.0 +
                 W3_ACT_JS  * act_js_mean * 10.0 +
                 W4_CAL_MAE * cop_cal_mae * 10.0)
    else:
        score = float("nan")

    print(f"  AT_HOME gap RMS:   {at_home_rms:.2f} pp")
    print(f"  COP max gap:       {cop_max_gap:.2f} pp")
    print(f"  Activity JS mean:  {act_js_mean:.4f}")
    print(f"  COP cal MAE mean:  {cop_cal_mae:.4f}")
    print(f"  Composite score S: {score:.4f}  (lower=better)")

    return {"components": components, "composite_score": score,
            "weights": {"w1_at_home": W1_AT_HOME, "w2_cop_gap": W2_COP_GAP,
                        "w3_act_js": W3_ACT_JS, "w4_cal_mae": W4_CAL_MAE}}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    data_dir, step3_dir, out_json = _resolve_paths(args)

    print("=" * 60)
    print("Step 4J — Statistical Diagnostic Battery")
    print("=" * 60)
    print(f"  data_dir    = {data_dir}")
    print(f"  step3_dir   = {step3_dir}")
    print(f"  out_json    = {out_json}")
    print(f"  n_bootstrap = {args.n_bootstrap}")

    aug, obs_aug, syn_aug, obs_ext = _load_frames(data_dir, step3_dir, args.sample)
    print(f"  rows: aug={len(aug)}  obs={len(obs_aug)}  syn={len(syn_aug)}")

    out_dir = os.path.dirname(out_json)
    os.makedirs(out_dir, exist_ok=True)

    results = {}

    # T1: Bootstrap CIs
    print("\n[T1] Bootstrap CIs ...")
    results["bootstrap_cis"] = run_bootstrap_cis(obs_aug, syn_aug, n_boot=args.n_bootstrap)
    for cn, v in results["bootstrap_cis"]["copresence"].items():
        sig = "*" if v["statistically_real"] else " "
        print(f"  {sig} {cn:<12} gap={v['gap_pp']:+.1f} pp  "
              f"CI=[{v['gap_ci_lo_pp']:+.1f}, {v['gap_ci_hi_pp']:+.1f}]")
    if results["bootstrap_cis"].get("at_home"):
        v = results["bootstrap_cis"]["at_home"]
        sig = "*" if v.get("statistically_real") else " "
        print(f"  {sig} AT_HOME      gap={v['gap_pp']:+.1f} pp  "
              f"CI=[{v['gap_ci_lo_pp']:+.1f}, {v['gap_ci_hi_pp']:+.1f}]")

    # T2: Calibration
    print("\n[T2] Calibration curves ...")
    results["calibration"] = run_calibration(aug)

    # T3: Joint distributions
    print("\n[T3] Joint distributions ...")
    results["joint_distributions"] = run_joint_distributions(obs_aug, syn_aug)
    for pair, pair_data in results["joint_distributions"].items():
        for label in ["obs", "syn"]:
            d = pair_data.get(label, {})
            print(f"  {pair} [{label}]  V={d.get('cramer_v', float('nan')):.4f}")

    # T4: χ²/KS
    print("\n[T4] χ²/KS tests ...")
    results["chi2_ks"] = run_chi2_ks(obs_aug, syn_aug)
    n_chi2_reject = sum(v["reject_H0"] for v in results["chi2_ks"]["chi2"].values())
    n_ks_reject   = sum(
        any(t.get("reject_H0") for t in cell.values())
        for cell in results["chi2_ks"]["ks"].values()
    )
    n_chi2_total = len(results["chi2_ks"]["chi2"])
    print(f"  χ² (activity): {n_chi2_reject}/{n_chi2_total} cells reject H₀ at α={results['chi2_ks']['bonf_alpha_chi2']:.2e}")
    print(f"  KS (AT_HOME/Alone): {n_ks_reject}/{len(results['chi2_ks']['ks'])} cells reject H₀")

    # T5: Composite score
    print("\n[T5] Composite score ...")
    results["composite"] = compute_composite_score(
        results["bootstrap_cis"],
        results["calibration"],
        obs_aug, syn_aug,
    )

    # Write JSON
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, allow_nan=True)
    print(f"\n  wrote {out_json}")

    # Plots
    if not args.no_plot:
        pfx = out_json.replace("_statistical.json", "")
        plot_bootstrap_cis(results["bootstrap_cis"], pfx + "_bootstrap.png")
        print(f"  wrote {pfx}_bootstrap.png")
        plot_calibration(results["calibration"], pfx + "_calibration.png")
        print(f"  wrote {pfx}_calibration.png")
        plot_joint_distributions(obs_aug, syn_aug, pfx + "_joints.png")
        print(f"  wrote {pfx}_joints.png")

    print(f"\n✓ 04J complete.  Composite score S = {results['composite']['composite_score']:.4f}")


if __name__ == "__main__":
    main()
