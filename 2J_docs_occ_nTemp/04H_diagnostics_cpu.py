"""
04H_diagnostics_cpu.py — Step 4H: AT_HOME Bias Diagnostics (CPU-only)

Implements Tests T1 (H1 pair-sampling), T2 (H2 post-hoc rule),
T3 (H3 exposure-bias trajectory), and T6 (H5 observed sanity) per
`Speed-Cluster_docs/step4_training.md`. Emits a machine-readable JSON
summary and (unless --no_plot) a 3×4 trajectory PNG.

Usage:
    python 04H_diagnostics_cpu.py              # full run on cluster layout
    python 04H_diagnostics_cpu.py --sample     # local smoke test
"""

import argparse
import datetime as dt
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

N_SLOTS = 48
NIGHT_SLOTS = list(range(0, 7)) + list(range(37, 48))   # 18 slots, 0-indexed
DAY_SLOTS = [s for s in range(N_SLOTS) if s not in NIGHT_SLOTS]   # 30 slots
CYCLES = [2005, 2010, 2015, 2022]
STRATA = [1, 2, 3]

HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM_COLS_NIGHT = [HOM_COLS[s] for s in NIGHT_SLOTS]
HOM_COLS_DAY = [HOM_COLS[s] for s in DAY_SLOTS]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default=None,
                   help="Step-4 outputs dir (training_pairs.pt, step4_train.pt, "
                        "augmented_diaries.csv). Default: outputs_step4 or "
                        "outputs_step4_test with --sample.")
    p.add_argument("--step3_dir", default=None,
                   help="Step-3 outputs dir (hetus_30min.csv). Default: outputs_step3.")
    p.add_argument("--output_json", default=None,
                   help="JSON destination. Default: <data_dir>/diagnostics_v4.json.")
    p.add_argument("--sample", action="store_true",
                   help="Smoke-test mode — reads outputs_step4_test/ and "
                        "hetus_30min_SAMPLE.csv if present (falls back to full).")
    p.add_argument("--no_plot", action="store_true",
                   help="Skip trajectory PNG output.")
    return p.parse_args()


def _resolve_paths(args):
    if args.data_dir:
        data_dir = args.data_dir
    else:
        data_dir = os.path.join(
            SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4"
        )
    step3_dir = args.step3_dir or os.path.join(SCRIPT_DIR, "outputs_step3")
    out_json = args.output_json or os.path.join(data_dir, "diagnostics_v4.json")
    return data_dir, step3_dir, out_json


def _find_hetus(step3_dir, sample):
    sample_path = os.path.join(step3_dir, "hetus_30min_SAMPLE.csv")
    full_path = os.path.join(step3_dir, "hetus_30min.csv")
    if sample and os.path.exists(sample_path):
        return sample_path
    if os.path.exists(full_path):
        return full_path
    if os.path.exists(sample_path):
        return sample_path
    return None


# ─── Population AT_HOME from step4_train.pt ────────────────────────────────

def _load_train(data_dir):
    path = os.path.join(data_dir, "step4_train.pt")
    if not os.path.exists(path):
        return None
    return torch.load(path, map_location="cpu", weights_only=False)


def _population_at_home(train):
    aux = train["aux_seq"][:, :, 0].numpy()          # (n, 48)
    cycle_year = train["cycle_year"].numpy()
    obs_strata = train["obs_strata"].numpy()
    overall = float(aux.mean())
    per_cs = {}
    for cy in CYCLES:
        for s in STRATA:
            mask = (cycle_year == cy) & (obs_strata == s)
            if mask.any():
                per_cs[f"{cy}_{s}"] = float(aux[mask].mean())
    return aux, cycle_year, obs_strata, overall, per_cs


# ─── T1 — Training-pair target AT_HOME ─────────────────────────────────────

def run_T1(train, pairs, pop_at_home, pop_per_cs):
    aux = train["aux_seq"][:, :, 0].numpy()
    cycle_year = train["cycle_year"].numpy()
    obs_strata = train["obs_strata"].numpy()

    src_idx = pairs["src_idx"].numpy()
    tgt_k = pairs["tgt_k_indices"].numpy()       # (n_pairs, K)
    tgt_strata = pairs["tgt_strata"].numpy()
    n_pairs = len(src_idx)

    # Mean AT_HOME across K targets × 48 slots per pair
    # aux[tgt_k] has shape (n_pairs, K, 48)
    pair_tgt_rate = aux[tgt_k].mean(axis=(1, 2))

    pair_cycle = cycle_year[src_idx]
    src_stratum = obs_strata[src_idx]

    # T1a
    t1a_mean = float(pair_tgt_rate.mean())
    t1a_gap_pp = (t1a_mean - pop_at_home) * 100.0

    # T1b — per (cycle × tgt_stratum)
    t1b = {}
    for cy in CYCLES:
        for s in STRATA:
            mask = (pair_cycle == cy) & (tgt_strata == s)
            if not mask.any():
                continue
            tgt_rate = float(pair_tgt_rate[mask].mean())
            obs_rate = pop_per_cs.get(f"{cy}_{s}")
            if obs_rate is None:
                continue
            t1b[f"{cy}_{s}"] = {
                "target_at_home": tgt_rate,
                "observed_at_home": float(obs_rate),
                "delta_pp": (tgt_rate - float(obs_rate)) * 100.0,
                "n_pairs": int(mask.sum()),
            }

    # T1c — (src × tgt) cross-tab
    t1c = {}
    for ss in STRATA:
        for ts in STRATA:
            if ss == ts:
                continue
            mask = (src_stratum == ss) & (tgt_strata == ts)
            if not mask.any():
                continue
            t1c[f"{ss}_{ts}"] = {
                "target_at_home": float(pair_tgt_rate[mask].mean()),
                "n_pairs": int(mask.sum()),
            }

    # Marginals
    tgt_marg = {str(s): float((tgt_strata == s).mean()) for s in STRATA}
    pop_marg = {str(s): float((obs_strata == s).mean()) for s in STRATA}

    # Verdict
    weekend_tgt = tgt_marg["2"] + tgt_marg["3"]
    weekend_pop = pop_marg["2"] + pop_marg["3"]
    skew_ratio = weekend_tgt / max(weekend_pop, 1e-6)

    t1b_deltas_abs = [abs(v["delta_pp"]) for v in t1b.values()]
    t1b_all_close = len(t1b_deltas_abs) > 0 and max(t1b_deltas_abs) <= 2.0

    if t1b_all_close:
        verdict = "H1_rejected"        # target means match observed per (cy,s)
    elif t1a_gap_pp >= 8.0 and skew_ratio > 1.5:
        verdict = "H1_confirmed"
    elif t1a_gap_pp <= 2.0:
        verdict = "H1_rejected"
    else:
        verdict = "partial"

    return {
        "T1a": {
            "pair_target_at_home": t1a_mean,
            "population_at_home": float(pop_at_home),
            "gap_pp": float(t1a_gap_pp),
        },
        "T1b": t1b,
        "T1c": t1c,
        "tgt_strata_marginal": tgt_marg,
        "population_strata_marginal": pop_marg,
        "weekend_skew_ratio": float(skew_ratio),
        "n_pairs": int(n_pairs),
        "verdict": verdict,
    }, verdict


# ─── T2 — Post-hoc rule contribution ───────────────────────────────────────

def run_T2(syn, obs_df):
    t2 = {}
    gap_closures = []
    if syn is None or obs_df is None:
        return {"_skipped": "augmented_diaries.csv or hetus_30min.csv not available"}, None

    for cy in CYCLES:
        for s in STRATA:
            obs_sub = obs_df[(obs_df["CYCLE_YEAR"] == cy) & (obs_df["DDAY_STRATA"] == s)]
            syn_sub = syn[(syn["CYCLE_YEAR"] == cy) & (syn["DDAY_STRATA"] == s)]
            if len(obs_sub) == 0 or len(syn_sub) == 0:
                continue
            obs_all = float(obs_sub[HOM_COLS].values.mean() * 100)
            syn_all = float(syn_sub[HOM_COLS].values.mean() * 100)
            obs_nn = float(obs_sub[HOM_COLS_DAY].values.mean() * 100)
            syn_nn = float(syn_sub[HOM_COLS_DAY].values.mean() * 100)
            gap_all = syn_all - obs_all
            gap_nn = syn_nn - obs_nn
            gap_closed = gap_all - gap_nn
            gap_closures.append(gap_closed)
            t2[f"{cy}_{s}"] = {
                "obs_all": obs_all, "syn_all": syn_all, "gap_all_pp": gap_all,
                "obs_nonnight": obs_nn, "syn_nonnight": syn_nn, "gap_nonnight_pp": gap_nn,
                "gap_closed_pp": gap_closed,
                "n_obs": int(len(obs_sub)), "n_syn": int(len(syn_sub)),
            }

    mean_closure = float(np.mean(gap_closures)) if gap_closures else None
    t2["_mean_gap_closure_pp"] = mean_closure
    if mean_closure is None:
        verdict = "unknown"
    elif mean_closure >= 10.0:
        verdict = "H2_dominant"
    elif mean_closure >= 2.0:
        verdict = "H2_small_contributor"
    else:
        verdict = "H2_rejected"
    t2["verdict"] = verdict
    return t2, verdict


# ─── T3 — Per-slot trajectory ──────────────────────────────────────────────

def _traj_stats(gap):
    morning = float(gap[0:14].mean())
    midday = float(gap[14:28].mean())
    evening = float(gap[28:48].mean())
    ae = float(gap[14:48].mean())
    night = float(gap[NIGHT_SLOTS].mean())
    abs_gap = np.abs(gap)
    slot_max = int(abs_gap.argmax())
    max_gap = float(gap[slot_max])
    gap_range = float(gap.max() - gap.min())
    return {
        "morning_mean_gap_pp": morning,
        "midday_mean_gap_pp": midday,
        "evening_mean_gap_pp": evening,
        "afternoon_evening_mean_gap_pp": ae,
        "night_mean_gap_pp": night,
        "slot_of_max_gap": slot_max,
        "max_gap_pp": max_gap,
        "gap_range_pp": gap_range,
        "per_slot_gap_pp": [float(x) for x in gap.tolist()],
    }


def run_T3(syn, obs_df):
    if syn is None or obs_df is None:
        return {"_skipped": "augmented_diaries.csv or hetus_30min.csv not available"}, None, None, None

    obs_overall = obs_df[HOM_COLS].values.mean(axis=0) * 100
    syn_overall = syn[HOM_COLS].values.mean(axis=0) * 100
    gap_overall = syn_overall - obs_overall

    t3 = {"overall": _traj_stats(gap_overall)}
    cell_curves = {}   # (cy, s) -> (obs, syn)

    for cy in CYCLES:
        for s in STRATA:
            obs_sub = obs_df[(obs_df["CYCLE_YEAR"] == cy) & (obs_df["DDAY_STRATA"] == s)]
            syn_sub = syn[(syn["CYCLE_YEAR"] == cy) & (syn["DDAY_STRATA"] == s)]
            if len(obs_sub) == 0 or len(syn_sub) == 0:
                continue
            obs_ps = obs_sub[HOM_COLS].values.mean(axis=0) * 100
            syn_ps = syn_sub[HOM_COLS].values.mean(axis=0) * 100
            gap_ps = syn_ps - obs_ps
            t3[f"{cy}_{s}"] = _traj_stats(gap_ps)
            cell_curves[(cy, s)] = (obs_ps, syn_ps)

    ov = t3["overall"]
    ratio = ov["afternoon_evening_mean_gap_pp"] / max(ov["morning_mean_gap_pp"], 1.0)
    h3_major = (ratio >= 2.0) and (ov["slot_of_max_gap"] >= 20)
    verdict = "H3_major" if h3_major else "H3_not_dominant"
    t3["verdict"] = verdict
    t3["afternoon_evening_to_morning_ratio"] = float(ratio)
    return t3, verdict, cell_curves, gap_overall


# ─── T6 — Observed AT_HOME sanity ──────────────────────────────────────────

def run_T6(obs_df):
    if obs_df is None:
        return {"_skipped": "hetus_30min.csv not available", "any_implausible": False}, False

    out = {}
    any_imp = False
    for cy in CYCLES:
        for s in STRATA:
            sub = obs_df[(obs_df["CYCLE_YEAR"] == cy) & (obs_df["DDAY_STRATA"] == s)]
            if len(sub) == 0:
                continue
            all_r = float(sub[HOM_COLS].values.mean())
            night_r = float(sub[HOM_COLS_NIGHT].values.mean())
            day_r = float(sub[HOM_COLS_DAY].values.mean())
            imp = (all_r < 0.40) or (all_r > 0.95)
            if imp:
                any_imp = True
            out[f"{cy}_{s}"] = {
                "at_home_all": all_r,
                "at_home_night": night_r,
                "at_home_day": day_r,
                "n": int(len(sub)),
                "implausible": imp,
            }
    out["any_implausible"] = any_imp
    return out, any_imp


# ─── Plot ──────────────────────────────────────────────────────────────────

def _plot_trajectories(cell_curves, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(STRATA), len(CYCLES), figsize=(14, 8),
                             sharex=True, sharey=True)
    strata_labels = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
    x = np.arange(N_SLOTS)

    for i, s in enumerate(STRATA):
        for j, cy in enumerate(CYCLES):
            ax = axes[i, j] if len(STRATA) > 1 else axes[j]
            curves = cell_curves.get((cy, s))
            if curves is None:
                ax.text(0.5, 0.5, "no data", ha="center", va="center",
                        transform=ax.transAxes, fontsize=9, color="gray")
            else:
                obs_ps, syn_ps = curves
                ax.plot(x, obs_ps, label="obs", color="#1f77b4", linewidth=1.5)
                ax.plot(x, syn_ps, label="syn", color="#d62728",
                        linewidth=1.5, linestyle="--")
                ax.fill_between(x, obs_ps, syn_ps,
                                where=(syn_ps >= obs_ps), color="#d62728", alpha=0.15)
            if i == 0:
                ax.set_title(f"{cy}", fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{strata_labels[s]}\nAT_HOME %", fontsize=9)
            if i == len(STRATA) - 1:
                ax.set_xlabel("Slot (30-min, 0-indexed)", fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 105)

    handles, labels = axes[0, 0].get_legend_handles_labels() if curves else ([], [])
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=9)
    fig.suptitle("04H — AT_HOME per-slot trajectories (observed vs synthetic)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    data_dir, step3_dir, out_json = _resolve_paths(args)
    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)

    print("=" * 60)
    print(f"Step 4H — AT_HOME Bias Diagnostics  "
          f"{'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)
    print(f"  data_dir  : {data_dir}")
    print(f"  step3_dir : {step3_dir}")
    print(f"  output    : {out_json}")

    # Load inputs
    train = _load_train(data_dir)
    pairs_path = os.path.join(data_dir, "training_pairs.pt")
    pairs = (torch.load(pairs_path, map_location="cpu", weights_only=False)
             if os.path.exists(pairs_path) else None)

    aug_path = os.path.join(data_dir, "augmented_diaries.csv")
    if os.path.exists(aug_path):
        aug = pd.read_csv(aug_path, low_memory=False)
        syn = aug[aug["IS_SYNTHETIC"] == 1] if "IS_SYNTHETIC" in aug.columns else aug
        aug_rows = int(len(aug))
    else:
        print(f"  NOTE: {aug_path} not found — T2/T3 will be skipped.")
        aug = None
        syn = None
        aug_rows = 0

    hetus_path = _find_hetus(step3_dir, args.sample)
    if hetus_path is None:
        print(f"  NOTE: hetus_30min.csv not found in {step3_dir} — T2/T3/T6 skipped.")
        obs_df = None
    else:
        print(f"  hetus path: {hetus_path}")
        obs_df = pd.read_csv(hetus_path, low_memory=False)

    # Population
    if train is None or pairs is None:
        print(f"  ERROR: step4_train.pt or training_pairs.pt missing in {data_dir}")
        pop_overall = None
        pop_per_cs = {}
    else:
        _, _, _, pop_overall, pop_per_cs = _population_at_home(train)

    # T1
    print("\n[T1] Training-pair target AT_HOME...")
    if train is not None and pairs is not None:
        t1, t1_verdict = run_T1(train, pairs, pop_overall, pop_per_cs)
        print(f"     T1a gap = {t1['T1a']['gap_pp']:+.2f} pp "
              f"(pair mean {t1['T1a']['pair_target_at_home']*100:.2f}%, "
              f"pop {t1['T1a']['population_at_home']*100:.2f}%)")
        print(f"     tgt_strata_marg = {t1['tgt_strata_marginal']}")
        print(f"     pop_strata_marg = {t1['population_strata_marginal']}")
        print(f"     weekend skew ratio = {t1['weekend_skew_ratio']:.3f}")
        print(f"     verdict = {t1_verdict}")
    else:
        t1 = {"_skipped": "step4_train.pt or training_pairs.pt missing"}
        t1_verdict = "unknown"
        print("     SKIPPED — inputs missing")

    # T2
    print("\n[T2] Post-hoc rule contribution...")
    t2, t2_verdict = run_T2(syn, obs_df)
    if t2_verdict is not None:
        print(f"     mean gap closure (non-night vs all) = "
              f"{t2['_mean_gap_closure_pp']:+.2f} pp   verdict = {t2_verdict}")
    else:
        print("     SKIPPED — inputs missing")

    # T3
    print("\n[T3] Per-slot trajectory...")
    t3, t3_verdict, cell_curves, gap_overall = run_T3(syn, obs_df)
    if t3_verdict is not None:
        ov = t3["overall"]
        print(f"     morning = {ov['morning_mean_gap_pp']:+.2f} pp | "
              f"midday = {ov['midday_mean_gap_pp']:+.2f} | "
              f"evening = {ov['evening_mean_gap_pp']:+.2f}")
        print(f"     afternoon+evening = {ov['afternoon_evening_mean_gap_pp']:+.2f} pp | "
              f"night = {ov['night_mean_gap_pp']:+.2f}")
        print(f"     slot_of_max_gap = {ov['slot_of_max_gap']}  "
              f"max_gap = {ov['max_gap_pp']:+.2f} pp  range = {ov['gap_range_pp']:.2f}")
        print(f"     verdict = {t3_verdict}")
    else:
        print("     SKIPPED — inputs missing")

    # T6
    print("\n[T6] Observed AT_HOME sanity...")
    t6, t6_any_imp = run_T6(obs_df)
    if obs_df is not None:
        flagged = sum(1 for k, v in t6.items()
                      if k != "any_implausible" and isinstance(v, dict) and v.get("implausible"))
        print(f"     any_implausible = {t6_any_imp}  flagged cells = {flagged}")
    else:
        print("     SKIPPED — hetus_30min.csv missing")

    # Plot
    plot_path = None
    if (not args.no_plot) and cell_curves:
        plot_path = os.path.join(data_dir, "diagnostics_v4_trajectories.png")
        try:
            _plot_trajectories(cell_curves, plot_path)
            print(f"\n  Saved plot: {plot_path}")
        except Exception as e:
            print(f"  WARNING: plot failed ({e})")
            plot_path = None

    # Hypothesis verdicts + recommendation
    h1_accounts = (t1_verdict == "H1_confirmed")
    if t6_any_imp:
        rec = "AUDIT_STEP3"
    elif t3_verdict == "H3_major" and not h1_accounts:
        rec = "RUN_GPU_T4_T5"
    else:
        rec = "SKIP_GPU"

    hyp = {
        "H1": t1_verdict,
        "H2": t2_verdict if t2_verdict else "unknown",
        "H3": t3_verdict if t3_verdict else "unknown",
        "H5": "H5_flagged" if t6_any_imp else (
            "H5_rejected" if obs_df is not None else "unknown"),
    }

    n_pairs_val = (int(pairs["src_idx"].shape[0])
                   if (pairs is not None and "src_idx" in pairs) else 0)

    result = {
        "run_timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "inputs": {
            "data_dir": os.path.abspath(data_dir),
            "step3_dir": os.path.abspath(step3_dir),
            "augmented_diaries_rows": aug_rows,
            "train_pairs_count": n_pairs_val,
            "hetus_path": hetus_path,
            "plot_path": plot_path,
        },
        "population": {
            "at_home_rate_overall": pop_overall,
            "at_home_per_cycle_stratum": pop_per_cs,
        },
        "T1": t1,
        "T2": t2,
        "T3": t3,
        "T6": t6,
        "hypothesis_verdicts": hyp,
        "recommendation_next_test": rec,
    }

    with open(out_json, "w") as f:
        json.dump(result, f, indent=2, default=str)

    # ── Condensed summary (04F-style) ────────────────────────────────────
    print("\n" + "=" * 60)
    print("04H DIAGNOSTIC SUMMARY")
    print("=" * 60)
    for k, v in hyp.items():
        marker = "PASS" if v.endswith("_rejected") else (
            "WARN" if v in ("partial", "H2_small_contributor", "H3_not_dominant")
            else "FLAG")
        print(f"  {k:>3}: {v:<25} [{marker}]")
    print(f"\n  RECOMMENDATION -> {rec}")
    print(f"  JSON: {out_json}")
    print("=" * 60)


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    main()
