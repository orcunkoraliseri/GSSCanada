"""
04I_activity_copresence_diagnostics.py — Step 4I: Activity (14-way) + Co-presence (9-way) Diagnostics (CPU-only)

Audits the two output heads not covered by 04H (which focused on AT_HOME/H1-H5):
  * Activity head (14-way CE): per-cycle × stratum distribution fidelity,
    JS divergence per slot, top-1-per-slot agreement, max share gap (pp).
  * Co-presence head (9-way BCE): per-channel prevalence overall, per-cycle
    × stratum, per-slot trajectory gap.

Emits machine-readable JSON + PNGs. Mirrors 04H argparse / path conventions.

Usage:
    python 04I_activity_copresence_diagnostics.py              # full run on cluster layout
    python 04I_activity_copresence_diagnostics.py --sample     # smoke test
"""

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

N_SLOTS = 48
CYCLES = [2005, 2010, 2015, 2022]
STRATA = [1, 2, 3]
STRATUM_LABEL = {1: "Weekday", 2: "Saturday", 3: "Sunday"}

ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_CODES = list(range(1, 15))   # 14-way

COP_NAMES = [
    "Alone", "Spouse", "Children", "parents",
    "friends", "others", "colleagues",
]

ACT_JS_PASS_THRESHOLD = 0.05    # per (cycle,stratum) JS threshold
COP_PP_PASS_THRESHOLD = 3.0     # per-channel prevalence gap threshold (pp)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default=None)
    p.add_argument("--step3_dir", default=None)
    p.add_argument("--output_json", default=None)
    p.add_argument("--sample", action="store_true")
    p.add_argument("--no_plot", action="store_true")
    return p.parse_args()


def _resolve_paths(args):
    data_dir = args.data_dir or os.path.join(
        SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4"
    )
    step3_dir = args.step3_dir or os.path.join(SCRIPT_DIR, "outputs_step3")
    out_json = args.output_json or os.path.join(data_dir, "diagnostics_v4_actcop.json")
    return data_dir, step3_dir, out_json


def _load_frames(data_dir, step3_dir, sample):
    sfx = "_SAMPLE" if sample else ""
    aug_path = os.path.join(data_dir, f"augmented_diaries{sfx}.csv")
    aug = pd.read_csv(aug_path, low_memory=False)
    syn = aug[aug["IS_SYNTHETIC"] == 1].copy()

    obs_path = os.path.join(step3_dir, f"hetus_30min{sfx}.csv")
    obs = pd.read_csv(obs_path, low_memory=False)

    cop_path = os.path.join(step3_dir, f"copresence_30min{sfx}.csv")
    obs_cop = pd.read_csv(cop_path, low_memory=False) if os.path.exists(cop_path) else None

    return aug, syn, obs, obs_cop


# ─── Activity (14-way) ─────────────────────────────────────────────────────

def _activity_shares(df, act_cols):
    """Return (n_slots, 14) proportion array across rows."""
    arr = df[act_cols].to_numpy()
    n_rows, n_slots = arr.shape
    out = np.zeros((n_slots, len(ACT_CODES)), dtype=np.float64)
    for i, code in enumerate(ACT_CODES):
        out[:, i] = (arr == code).mean(axis=0)
    # Renormalize in case some rows carry codes outside 1..14
    row_sum = out.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1.0
    return out / row_sum


def _js_divergence(p, q, eps=1e-12):
    """Row-wise JS divergence, base-2."""
    p = np.asarray(p) + eps
    q = np.asarray(q) + eps
    p = p / p.sum(axis=-1, keepdims=True)
    q = q / q.sum(axis=-1, keepdims=True)
    m = 0.5 * (p + q)

    def _kl(a, b):
        return (a * (np.log(a) - np.log(b))).sum(axis=-1)

    return 0.5 * (_kl(p, m) + _kl(q, m)) / np.log(2)


def run_activity(syn, obs):
    act_cols_syn = [c for c in ACT_COLS if c in syn.columns]
    act_cols_obs = [c for c in ACT_COLS if c in obs.columns]
    act_cols = [c for c in act_cols_syn if c in act_cols_obs]
    if len(act_cols) < N_SLOTS:
        print(f"  [warn] only {len(act_cols)}/{N_SLOTS} activity columns present in both frames")

    per_cs = {}
    fail_pairs, warn_pairs = [], []
    for cy in CYCLES:
        for s in STRATA:
            obs_sub = obs[(obs["CYCLE_YEAR"] == cy) & (obs["DDAY_STRATA"] == s)]
            syn_sub = syn[(syn["CYCLE_YEAR"] == cy) & (syn["DDAY_STRATA"] == s)]
            if len(obs_sub) == 0 or len(syn_sub) == 0:
                continue
            share_obs = _activity_shares(obs_sub, act_cols)   # (n_slots, 14)
            share_syn = _activity_shares(syn_sub, act_cols)
            js_per_slot = _js_divergence(share_obs, share_syn)
            js_mean = float(js_per_slot.mean())
            js_max = float(js_per_slot.max())

            # top-1-per-slot agreement
            top_obs = share_obs.argmax(axis=1)
            top_syn = share_syn.argmax(axis=1)
            top1_agree = float((top_obs == top_syn).mean())

            # overall share gap (collapse slots)
            share_obs_flat = share_obs.mean(axis=0)
            share_syn_flat = share_syn.mean(axis=0)
            gap_pp_by_code = (share_syn_flat - share_obs_flat) * 100.0
            max_gap_pp = float(np.abs(gap_pp_by_code).max())
            max_gap_code = int(ACT_CODES[int(np.abs(gap_pp_by_code).argmax())])

            entry = {
                "n_obs": int(len(obs_sub)),
                "n_syn": int(len(syn_sub)),
                "js_mean": js_mean,
                "js_max": js_max,
                "top1_agreement": top1_agree,
                "max_share_gap_pp": max_gap_pp,
                "max_gap_activity_code": max_gap_code,
                "share_obs_overall": {str(ACT_CODES[i]): float(share_obs_flat[i])
                                      for i in range(len(ACT_CODES))},
                "share_syn_overall": {str(ACT_CODES[i]): float(share_syn_flat[i])
                                      for i in range(len(ACT_CODES))},
            }
            per_cs[f"{cy}_{s}"] = entry

            if js_mean > ACT_JS_PASS_THRESHOLD:
                fail_pairs.append(f"{cy}_{s}")
            elif js_mean > 0.5 * ACT_JS_PASS_THRESHOLD:
                warn_pairs.append(f"{cy}_{s}")

    # Overall roll-up
    if per_cs:
        js_all = [v["js_mean"] for v in per_cs.values()]
        top1_all = [v["top1_agreement"] for v in per_cs.values()]
        max_gap_all = [v["max_share_gap_pp"] for v in per_cs.values()]
        overall = {
            "js_mean_across_cs": float(np.mean(js_all)),
            "js_max_across_cs": float(np.max(js_all)),
            "top1_agree_mean": float(np.mean(top1_all)),
            "max_share_gap_pp_across_cs": float(np.max(max_gap_all)),
            "fail_cs_count": len(fail_pairs),
            "warn_cs_count": len(warn_pairs),
            "fail_cs": fail_pairs,
            "warn_cs": warn_pairs,
        }
    else:
        overall = {}

    if overall and overall["js_max_across_cs"] <= ACT_JS_PASS_THRESHOLD:
        verdict = "activity_ok"
    elif overall and len(fail_pairs) <= 2:
        verdict = "activity_partial"
    else:
        verdict = "activity_fail"

    return {"overall": overall, "per_cs": per_cs, "verdict": verdict}


# ─── Co-presence (9-way) ───────────────────────────────────────────────────

def _cop_prevalence(df, cop_name):
    cols = [f"{cop_name}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return None, None
    mat = df[cols].to_numpy()
    overall = float(np.nanmean(mat))             # scalar mean across rows × slots
    per_slot = np.nanmean(mat, axis=0)           # (n_slots,)
    return overall, per_slot


def run_copresence(syn, obs, obs_cop, aug=None):
    """Observed co-presence source selection:
    The COP columns (Alone30_*, Spouse30_*, ...) live in augmented_diaries.csv.
    Neither copresence_30min.csv nor hetus_30min.csv carries them, so prefer
    aug[IS_SYNTHETIC==0] when available.
    """
    def _has_cop(df):
        return df is not None and f"{COP_NAMES[0]}30_001" in df.columns

    if aug is not None and "IS_SYNTHETIC" in aug.columns and _has_cop(aug):
        obs_src = aug[aug["IS_SYNTHETIC"] == 0].copy()
    elif _has_cop(obs_cop):
        obs_src = obs_cop
    elif _has_cop(obs):
        obs_src = obs
    else:
        print("  [warn] no frame contains COP columns — skipping co-presence audit")
        return {"overall": {"per_channel_gap_pp_max": 0.0,
                            "per_channel_gap_pp_mean": 0.0,
                            "fail_channels_count": 0,
                            "fail_channels": [], "warn_channels": []},
                "per_channel": {}, "per_cs": {}, "verdict": "copresence_skipped"}

    overall_cop, per_cop, per_cs_cop = {}, {}, {}
    cop_fail, cop_warn = [], []

    for cn in COP_NAMES:
        obs_prev, obs_slot = _cop_prevalence(obs_src, cn)
        syn_prev, syn_slot = _cop_prevalence(syn, cn)
        if obs_prev is None or syn_prev is None:
            continue
        gap_pp = (syn_prev - obs_prev) * 100.0
        slot_gap_pp = (syn_slot - obs_slot) * 100.0 if obs_slot is not None else None
        per_cop[cn] = {
            "obs_prev": obs_prev,
            "syn_prev": syn_prev,
            "gap_pp": float(gap_pp),
            "max_abs_slot_gap_pp": float(np.abs(slot_gap_pp).max()) if slot_gap_pp is not None else None,
            "max_abs_slot": int(np.abs(slot_gap_pp).argmax()) if slot_gap_pp is not None else None,
        }
        if abs(gap_pp) > COP_PP_PASS_THRESHOLD:
            cop_fail.append(cn)
        elif abs(gap_pp) > 0.5 * COP_PP_PASS_THRESHOLD:
            cop_warn.append(cn)

    # Per cycle × stratum × channel
    for cy in CYCLES:
        for s in STRATA:
            syn_sub = syn[(syn["CYCLE_YEAR"] == cy) & (syn["DDAY_STRATA"] == s)]
            obs_sub = obs_src[(obs_src["CYCLE_YEAR"] == cy) & (obs_src["DDAY_STRATA"] == s)] \
                if "CYCLE_YEAR" in obs_src.columns and "DDAY_STRATA" in obs_src.columns else None
            if obs_sub is None or len(obs_sub) == 0 or len(syn_sub) == 0:
                continue
            row = {}
            for cn in COP_NAMES:
                op, _ = _cop_prevalence(obs_sub, cn)
                sp, _ = _cop_prevalence(syn_sub, cn)
                if op is None or sp is None:
                    continue
                row[cn] = {
                    "obs_prev": op,
                    "syn_prev": sp,
                    "gap_pp": float((sp - op) * 100.0),
                }
            if row:
                per_cs_cop[f"{cy}_{s}"] = row

    overall_cop = {
        "per_channel_gap_pp_max": float(max((abs(v["gap_pp"]) for v in per_cop.values()), default=0.0)),
        "per_channel_gap_pp_mean": float(np.mean([abs(v["gap_pp"]) for v in per_cop.values()])) if per_cop else 0.0,
        "fail_channels_count": len(cop_fail),
        "fail_channels": cop_fail,
        "warn_channels": cop_warn,
    }

    if overall_cop["per_channel_gap_pp_max"] <= COP_PP_PASS_THRESHOLD:
        verdict = "copresence_ok"
    elif len(cop_fail) <= 2:
        verdict = "copresence_partial"
    else:
        verdict = "copresence_fail"

    return {
        "overall": overall_cop,
        "per_channel": per_cop,
        "per_cs": per_cs_cop,
        "verdict": verdict,
    }


# ─── Plots ─────────────────────────────────────────────────────────────────

def plot_activity_shares(activity_result, out_path):
    per_cs = activity_result.get("per_cs", {})
    if not per_cs:
        return
    fig, axes = plt.subplots(len(STRATA), len(CYCLES), figsize=(14, 8), sharey=True)
    for si, s in enumerate(STRATA):
        for ci, cy in enumerate(CYCLES):
            ax = axes[si, ci]
            entry = per_cs.get(f"{cy}_{s}")
            if entry is None:
                ax.set_axis_off()
                continue
            codes = [int(k) for k in entry["share_obs_overall"].keys()]
            obs_v = [entry["share_obs_overall"][str(k)] for k in codes]
            syn_v = [entry["share_syn_overall"][str(k)] for k in codes]
            x = np.arange(len(codes))
            w = 0.4
            ax.bar(x - w/2, obs_v, width=w, label="obs", color="#4C72B0")
            ax.bar(x + w/2, syn_v, width=w, label="syn", color="#C44E52", alpha=0.8)
            ax.set_title(f"{cy} × {STRATUM_LABEL[s]}  JS={entry['js_mean']:.3f}")
            ax.set_xticks(x)
            ax.set_xticklabels(codes, fontsize=7)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Activity (14-way) share — observed vs synthetic")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def plot_copresence_prevalence(cop_result, out_path):
    per_channel = cop_result.get("per_channel", {})
    if not per_channel:
        return
    names = [n for n in COP_NAMES if n in per_channel]
    obs_v = [per_channel[n]["obs_prev"] for n in names]
    syn_v = [per_channel[n]["syn_prev"] for n in names]
    x = np.arange(len(names))
    w = 0.4
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x - w/2, obs_v, width=w, label="obs", color="#4C72B0")
    ax.bar(x + w/2, syn_v, width=w, label="syn", color="#C44E52", alpha=0.8)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=25, ha="right")
    ax.set_ylabel("Prevalence (fraction of slots×rows)")
    ax.set_title("Co-presence prevalence — observed vs synthetic")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    data_dir, step3_dir, out_json = _resolve_paths(args)
    print(f"  data_dir  = {data_dir}")
    print(f"  step3_dir = {step3_dir}")
    print(f"  out_json  = {out_json}")

    aug, syn, obs, obs_cop = _load_frames(data_dir, step3_dir, args.sample)
    print(f"  rows: aug={len(aug)}  syn={len(syn)}  obs={len(obs)}  obs_cop={len(obs_cop) if obs_cop is not None else 'n/a'}")

    print("  [activity] computing per-CS JS + top-1 agreement ...")
    activity_result = run_activity(syn, obs)
    print(f"    verdict = {activity_result['verdict']}  "
          f"overall_js_mean = {activity_result['overall'].get('js_mean_across_cs', 'n/a')}")

    print("  [copresence] computing per-channel prevalence gaps ...")
    cop_result = run_copresence(syn, obs, obs_cop, aug=aug)
    print(f"    verdict = {cop_result['verdict']}  "
          f"max_gap_pp = {cop_result['overall'].get('per_channel_gap_pp_max', 'n/a')}")

    payload = {
        "run_timestamp": dt.datetime.utcnow().isoformat(timespec="seconds"),
        "data_dir": data_dir,
        "step3_dir": step3_dir,
        "thresholds": {
            "act_js_pass": ACT_JS_PASS_THRESHOLD,
            "cop_pp_pass": COP_PP_PASS_THRESHOLD,
        },
        "activity": activity_result,
        "copresence": cop_result,
    }

    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  wrote {out_json}")

    if not args.no_plot:
        out_dir = os.path.dirname(out_json) or "."
        act_png = os.path.join(out_dir, "diagnostics_v4_activity.png")
        cop_png = os.path.join(out_dir, "diagnostics_v4_copresence.png")
        plot_activity_shares(activity_result, act_png)
        print(f"  wrote {act_png}")
        if cop_result.get("per_channel"):
            plot_copresence_prevalence(cop_result, cop_png)
            print(f"  wrote {cop_png}")
        else:
            print(f"  skipped {cop_png} (no per-channel data)")


if __name__ == "__main__":
    main()
