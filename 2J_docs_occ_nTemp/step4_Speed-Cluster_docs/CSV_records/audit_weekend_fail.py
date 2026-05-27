"""Audit Sub-stage D v4 weekend gate failure.

Compares observed 2022 ground truth vs reconstructed predictions on the
12,336 IS_SYNTHETIC=0 rows, stratified by DDAY_STRATA (1=WD, 2=Sat, 3=Sun).
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial.distance import jensenshannon

HERE = Path(__file__).parent
OBS = HERE / "obs_2022.csv"
PRED = HERE.parent.parent.parent / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030" / "reconstructed_2022_diaries.csv"

ACT_COLS = [f"act30_{i:03d}" for i in range(1, 49)]
HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]

print(f"Loading obs: {OBS}")
obs = pd.read_csv(OBS)
print(f"  rows={len(obs)} cols={obs.shape[1]}")
print(f"Loading pred: {PRED}")
pred = pd.read_csv(PRED)
print(f"  rows={len(pred)} cols={pred.shape[1]}")

# Join on occID + DDAY_STRATA (one row per respondent)
m = obs[["occID", "DDAY_STRATA"] + ACT_COLS + HOM_COLS].merge(
    pred[["occID", "DDAY_STRATA"] + ACT_COLS + HOM_COLS],
    on=["occID", "DDAY_STRATA"], suffixes=("_obs", "_pred"))
print(f"\nMerged rows: {len(m)}")

STRATUM_NAME = {1: "WD", 2: "Sat", 3: "Sun"}

print("\n" + "="*70)
print("PER-STRATUM ACTIVITY-CLASS DISTRIBUTION (obs vs pred, %)")
print("="*70)

for s in [1, 2, 3]:
    sub = m[m["DDAY_STRATA"] == s]
    if len(sub) == 0:
        continue
    obs_acts = sub[[c + "_obs" for c in ACT_COLS]].values.flatten()
    pred_acts = sub[[c + "_pred" for c in ACT_COLS]].values.flatten()

    n_classes = 14
    obs_dist = np.bincount(obs_acts.astype(int), minlength=n_classes + 1)[1:].astype(float)
    pred_dist = np.bincount(pred_acts.astype(int), minlength=n_classes + 1)[1:].astype(float)
    obs_dist /= obs_dist.sum()
    pred_dist /= pred_dist.sum()

    js = jensenshannon(obs_dist, pred_dist, base=2) ** 2  # squared for JS divergence
    js_dist = jensenshannon(obs_dist, pred_dist, base=2)  # JS distance (matches sklearn-style)

    print(f"\n  Stratum {s} ({STRATUM_NAME[s]}) | n={len(sub)} respondents | JS_dist={js_dist:.4f}")
    print(f"  {'class':>5} {'obs%':>7} {'pred%':>7} {'diff_pp':>8}")
    diffs = []
    for c in range(n_classes):
        diffs.append((c + 1, obs_dist[c] * 100, pred_dist[c] * 100, (pred_dist[c] - obs_dist[c]) * 100))
    # Sort by absolute diff descending
    diffs.sort(key=lambda x: -abs(x[3]))
    for cls, ob, pr, d in diffs:
        flag = " <<" if abs(d) > 1.0 else ""
        print(f"  {cls:>5d} {ob:>7.2f} {pr:>7.2f} {d:>+8.2f}{flag}")

print("\n" + "="*70)
print("AT_HOME PROPORTION PER STRATUM (obs vs pred)")
print("="*70)
for s in [1, 2, 3]:
    sub = m[m["DDAY_STRATA"] == s]
    if len(sub) == 0:
        continue
    obs_hom = sub[[c + "_obs" for c in HOM_COLS]].values.mean()
    pred_hom = sub[[c + "_pred" for c in HOM_COLS]].values.mean()
    print(f"  Stratum {s} ({STRATUM_NAME[s]}): obs={obs_hom*100:.2f}%  pred={pred_hom*100:.2f}%  diff={(pred_hom-obs_hom)*100:+.2f}pp")

print("\n" + "="*70)
print("PER-TIMESTEP AT_HOME (obs vs pred, weekend strata only)")
print("="*70)
for s in [2, 3]:
    sub = m[m["DDAY_STRATA"] == s]
    if len(sub) == 0:
        continue
    print(f"\n  Stratum {s} ({STRATUM_NAME[s]}): n={len(sub)}")
    obs_h = sub[[c + "_obs" for c in HOM_COLS]].values.mean(axis=0)
    pred_h = sub[[c + "_pred" for c in HOM_COLS]].values.mean(axis=0)
    max_diff_idx = int(np.argmax(np.abs(pred_h - obs_h)))
    print(f"    max-diff timestep idx={max_diff_idx:02d} (slot {max_diff_idx+1}/48, ~{(max_diff_idx+1)*0.5:.1f}h): obs={obs_h[max_diff_idx]*100:.1f}%  pred={pred_h[max_diff_idx]*100:.1f}%  diff={(pred_h[max_diff_idx]-obs_h[max_diff_idx])*100:+.1f}pp")
    # Show every 4th timestep (every 2h)
    print(f"    {'slot':>5} {'hour':>6} {'obs%':>7} {'pred%':>7} {'diff':>7}")
    for i in range(0, 48, 4):
        h = (i + 1) * 0.5
        d = (pred_h[i] - obs_h[i]) * 100
        flag = " <<" if abs(d) > 5 else ""
        print(f"    {i+1:>5d} {h:>6.1f} {obs_h[i]*100:>7.1f} {pred_h[i]*100:>7.1f} {d:>+7.1f}{flag}")

# =====================================================================
# Phase 2 — Is the gate reachable? Compare obs vs synth 2022 targets.
# =====================================================================
SYNTH = HERE / "synth_2022.csv"
print("\n" + "="*70)
print("PHASE 2 — obs-vs-synth + pred-vs-synth per stratum (gate composition)")
print("="*70)
print(f"\nLoading synth: {SYNTH}")
synth = pd.read_csv(SYNTH)
print(f"  rows={len(synth)} cols={synth.shape[1]}")

# Build pred frame restricted to synth occIDs
synth_keys = synth[["occID", "DDAY_STRATA"]]
pred_synth = pred.merge(synth_keys, on=["occID", "DDAY_STRATA"])
print(f"  pred rows matching synth occIDs: {len(pred_synth)}")

print("\nPer-stratum JS_distance (activity-class distribution):")
print(f"  {'stratum':>8} {'n_obs':>7} {'n_synth':>8} {'JS(obs,synth)':>14} {'JS(pred,synth)':>15} {'JS(obs,pred)':>13}")
for s in [1, 2, 3]:
    sub_obs = obs[obs["DDAY_STRATA"] == s]
    sub_synth = synth[synth["DDAY_STRATA"] == s]
    sub_pred_synth = pred_synth[pred_synth["DDAY_STRATA"] == s]
    sub_pred_obs = pred[(pred["DDAY_STRATA"] == s) & (pred["occID"].isin(sub_obs["occID"]))]

    def dist(df, cols):
        v = df[cols].values.flatten()
        d = np.bincount(v.astype(int), minlength=15)[1:].astype(float)
        return d / d.sum() if d.sum() > 0 else d

    obs_d = dist(sub_obs, ACT_COLS)
    synth_d = dist(sub_synth, ACT_COLS)
    pred_synth_d = dist(sub_pred_synth, ACT_COLS)
    pred_obs_d = dist(sub_pred_obs, ACT_COLS)

    j_os = jensenshannon(obs_d, synth_d, base=2)
    j_ps = jensenshannon(pred_synth_d, synth_d, base=2)
    j_op = jensenshannon(obs_d, pred_obs_d, base=2)
    print(f"  {STRATUM_NAME[s]:>8} {len(sub_obs):>7d} {len(sub_synth):>8d} {j_os:>14.4f} {j_ps:>15.4f} {j_op:>13.4f}")

print("\nAT_HOME proportion per stratum (obs / synth / pred-on-synth):")
print(f"  {'stratum':>8} {'obs%':>7} {'synth%':>8} {'pred_synth%':>13}")
for s in [1, 2, 3]:
    sub_obs = obs[obs["DDAY_STRATA"] == s]
    sub_synth = synth[synth["DDAY_STRATA"] == s]
    sub_pred_synth = pred_synth[pred_synth["DDAY_STRATA"] == s]
    o = sub_obs[HOM_COLS].values.mean() * 100
    syn = sub_synth[HOM_COLS].values.mean() * 100
    ps = sub_pred_synth[HOM_COLS].values.mean() * 100
    print(f"  {STRATUM_NAME[s]:>8} {o:>7.2f} {syn:>8.2f} {ps:>13.2f}")

print("\nClass-level obs-vs-synth diff (weekend strata, sorted by |diff|):")
for s in [2, 3]:
    sub_obs = obs[obs["DDAY_STRATA"] == s]
    sub_synth = synth[synth["DDAY_STRATA"] == s]
    obs_d = dist(sub_obs, ACT_COLS)
    synth_d = dist(sub_synth, ACT_COLS)
    print(f"\n  Stratum {s} ({STRATUM_NAME[s]}):")
    print(f"  {'class':>5} {'obs%':>7} {'synth%':>8} {'diff_pp':>9}")
    diffs = [(c+1, obs_d[c]*100, synth_d[c]*100, (synth_d[c]-obs_d[c])*100) for c in range(14)]
    diffs.sort(key=lambda x: -abs(x[3]))
    for cls, ob, sy, d in diffs:
        flag = " <<" if abs(d) > 1.0 else ""
        print(f"  {cls:>5d} {ob:>7.2f} {sy:>8.2f} {d:>+9.2f}{flag}")
