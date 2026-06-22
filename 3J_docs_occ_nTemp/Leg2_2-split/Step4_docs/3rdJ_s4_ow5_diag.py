"""
3rdJ_s4_ow5_diag.py — OW5 failure characterisation diagnostic

Goal: determine whether the ~63% OW5 (weekday>=Sat>=Sun AT_WORK ordering)
failure is dominated by noise-level violations fixable with a cheap post-hoc
per-respondent clamp, or by genuine large violations that require model-level
day-type coupling.

OW5 replication mirrors 3rdJ_04_augmentationGSS_2split_val.py §7
(validate_at_work_sanity, lines ~734-750).

Build: 2026-06-21 (employee, Claude Sonnet 4.6)
Run: sbatch CPU job on Speed
Output: printed summary only (tight)
"""

from __future__ import annotations
import sys, os
import numpy as np
import pandas as pd

# ── paths ─────────────────────────────────────────────────────────────────────
STEP4_DIR = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
DATA_CSV = os.path.join(STEP4_DIR, "outputs_step4/sweep/R10_fast_floataware_raked/augmented_diaries.csv")

# confirm path
print(f"[diag] Data: {DATA_CSV}")
if not os.path.exists(DATA_CSV):
    # fallback: list sweep dir so we can see what's there
    sweep_dir = os.path.join(STEP4_DIR, "outputs_step4/sweep")
    print(f"[ERROR] CSV not found. sweep/ contents:")
    for item in sorted(os.listdir(sweep_dir)):
        sub = os.path.join(sweep_dir, item)
        for f in os.listdir(sub) if os.path.isdir(sub) else []:
            print(f"  {item}/{f}")
    sys.exit(1)

print("[diag] Loading CSV …")
df = pd.read_csv(DATA_CSV, low_memory=False)
print(f"[diag] Loaded: {len(df):,} rows  cols={len(df.columns)}")

# ── identify wrk30 columns ────────────────────────────────────────────────────
wrk_cols = [c for c in df.columns if c.startswith("wrk30_")]
if not wrk_cols:
    print("[ERROR] No wrk30_* columns found. Abort.")
    sys.exit(1)
print(f"[diag] wrk30 slots: {len(wrk_cols)}")

# ── keep only synthetic rows (IS_SYNTHETIC==1) — mirrors validator ─────────────
if "IS_SYNTHETIC" in df.columns:
    syn = df[df["IS_SYNTHETIC"] == 1].copy()
    print(f"[diag] Synthetic rows: {len(syn):,}")
else:
    print("[WARN] IS_SYNTHETIC not found; using all rows")
    syn = df.copy()

# ── per-row mean work rate ────────────────────────────────────────────────────
syn["_wrate"] = np.nanmean(syn[wrk_cols].to_numpy(dtype=float), axis=1)

# ── pivot: mean wrate per (occID, DDAY_STRATA) ───────────────────────────────
piv = syn.pivot_table(index="occID", columns="DDAY_STRATA",
                      values="_wrate", aggfunc="mean")
n_total_occ = len(piv)

# strata present
have_all = set([1, 2, 3]).issubset(piv.columns)
if have_all:
    sub = piv.dropna(subset=[1, 2, 3])
else:
    sub = piv.dropna()

n_counted = len(sub)
n_excluded = n_total_occ - n_counted

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM 1 — COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════
mask_ok = (sub[1] >= sub[2]) & (sub[2] >= sub[3])
n_ok = int(mask_ok.sum())
ow5_pct = n_ok / n_counted * 100 if n_counted else float("nan")

print("\n" + "="*60)
print("ITEM 1 — COVERAGE & OW5 REPRODUCTION")
print("="*60)
print(f"  Total unique occIDs (synthetic): {n_total_occ:,}")
print(f"  Have ALL 3 strata (counted):     {n_counted:,}")
print(f"  Excluded (<3 strata):            {n_excluded:,}")
print(f"  OW5 = {ow5_pct:.1f}%   ({n_ok}/{n_counted} pass wkdy>=Sat>=Sun)")

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM 2 — VIOLATION MAGNITUDE
# ═══════════════════════════════════════════════════════════════════════════════
fail = sub[~mask_ok].copy()
# violation = amount by which ordering is broken
fail["viol_sat_wkdy"] = np.maximum(0.0, fail[2] - fail[1])   # Sat > wkdy
fail["viol_sun_sat"]  = np.maximum(0.0, fail[3] - fail[2])   # Sun > Sat
fail["violation"]     = fail["viol_sat_wkdy"] + fail["viol_sun_sat"]

print("\n" + "="*60)
print(f"ITEM 2 — FAILURE MAGNITUDE  (N_fail={len(fail):,})")
print("="*60)
percs = [25, 50, 75, 90, 100]
vals  = np.nanpercentile(fail["violation"].to_numpy(), percs)
for p, v in zip(percs, vals):
    label = "MAX" if p == 100 else f"p{p:02d}"
    print(f"  violation {label}: {v:.4f}  (~{v*48:.1f} work-slots/48)")

# threshold: 1 slot out of 48 = 1/48 ~ 0.0208
slot1 = 1/48
tiny_frac = float((fail["violation"] < slot1).sum()) / len(fail) * 100
print(f"\n  Fraction with violation < 1 slot (< {slot1:.4f}): {tiny_frac:.1f}%")
print(f"  NOTE: <1-slot violations are noise-level (< 30 min difference)")

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM 3 — WORKER vs NON-WORKER SPLIT
# ═══════════════════════════════════════════════════════════════════════════════
fail["mean_work_overall"] = fail[[1, 2, 3]].mean(axis=1)
near_zero = fail["mean_work_overall"] < 0.02
n_near_zero = int(near_zero.sum())
n_genuine   = int((~near_zero).sum())

print("\n" + "="*60)
print("ITEM 3 — WORKER vs NON-WORKER among FAILURES")
print("="*60)
print(f"  Near-zero workers (mean_wrate < 0.02): {n_near_zero:,}  ({n_near_zero/len(fail)*100:.1f}%)")
print(f"  Genuine workers   (mean_wrate >= 0.02): {n_genuine:,}   ({n_genuine/len(fail)*100:.1f}%)")
print(f"  (Near-zero workers failing by noise = cheap-fix population)")

# among genuine workers, what's the typical violation?
if n_genuine > 0:
    gen_viol = fail.loc[~near_zero, "violation"]
    gv50 = float(np.nanmedian(gen_viol))
    gv90 = float(np.nanpercentile(gen_viol, 90))
    print(f"\n  Genuine-worker violation  median={gv50:.4f}  p90={gv90:.4f}  "
          f"(~{gv50*48:.1f} / ~{gv90*48:.1f} slots)")

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM 4 — DIRECTION OF VIOLATION
# ═══════════════════════════════════════════════════════════════════════════════
sat_over_wkdy = fail["viol_sat_wkdy"] > 0
sun_over_sat  = fail["viol_sun_sat"]  > 0
both          = sat_over_wkdy & sun_over_sat
sat_only      = sat_over_wkdy & ~sun_over_sat
sun_only      = ~sat_over_wkdy & sun_over_sat

print("\n" + "="*60)
print("ITEM 4 — DIRECTION OF VIOLATIONS")
print("="*60)
nf = len(fail)
print(f"  Sat>Wkdy only:     {int(sat_only.sum()):,}  ({int(sat_only.sum())/nf*100:.1f}%)")
print(f"  Sun>Sat only:      {int(sun_only.sum()):,}  ({int(sun_only.sum())/nf*100:.1f}%)")
print(f"  Both steps broken: {int(both.sum()):,}   ({int(both.sum())/nf*100:.1f}%)")
print(f"  (Sat>Wkdy violations = model failed to suppress weekend work vs weekday)")
print(f"  (Sun>Sat violations  = model failed to suppress Sunday vs Saturday)")

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM 5 — POST-HOC FIX SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ITEM 5 — POST-HOC MONOTONE CLAMP SIMULATION")
print("="*60)

# We need per-occID, per-slot wrk30 values to simulate the clamp.
# For each failing occID: compute scale factor per DDAY_STRATA so that
# mean(wrk30 * scale) = clamped_rate; apply proportional scaling to slots.
#
# Strategy: build a dict {occID -> {strata -> list_of_row_indices in syn}}
# then for each failing occID, get the original slot values, apply the clamp.

syn_indexed = syn.set_index("occID") if "occID" in syn.columns else None

# We need (occID, DDAY_STRATA) -> rows  so we can scale wrk30 slots
# Build a working copy of wrk30 values
wrk_arr = syn[wrk_cols].to_numpy(dtype=float)  # shape: (N_rows, 48)
occ_ids  = syn["occID"].to_numpy()
strata   = syn["DDAY_STRATA"].to_numpy()

# Pre-compute totals for marginal drift calculation
total_work_slots_wkdy = float(np.nansum(wrk_arr[strata == 1]))
total_work_slots_sat  = float(np.nansum(wrk_arr[strata == 2]))
total_work_slots_sun  = float(np.nansum(wrk_arr[strata == 3]))

# Build index: occID -> {strata_val -> row_indices}
from collections import defaultdict
occ_strata_idx = defaultdict(lambda: defaultdict(list))
for i, (oid, s) in enumerate(zip(occ_ids, strata)):
    occ_strata_idx[oid][s].append(i)

fail_occids = set(fail.index.tolist())

# For each failing occID: apply proportional clamp
removed_wkdy = removed_sat = removed_sun = 0.0
n_clamped = 0

# Make a mutable copy of the work array
wrk_sim = wrk_arr.copy()

for oid in fail_occids:
    if oid not in occ_strata_idx:
        continue
    od = occ_strata_idx[oid]
    if not (1 in od and 2 in od and 3 in od):
        continue

    # current mean rates (use sub[oid] values, not re-computing to be fast)
    wkdy_rate = float(sub.loc[oid, 1])
    sat_rate  = float(sub.loc[oid, 2])
    sun_rate  = float(sub.loc[oid, 3])

    # clamp: Sat' = min(Sat, Wkdy); Sun' = min(Sun, Sat')
    sat_rate_c = min(sat_rate, wkdy_rate)
    sun_rate_c = min(sun_rate, sat_rate_c)

    # scale Saturday rows proportionally
    if sat_rate > 0 and sat_rate_c < sat_rate:
        scale = sat_rate_c / sat_rate
        sat_rows = od[2]
        for r in sat_rows:
            old_vals = wrk_sim[r].copy()
            wrk_sim[r] = old_vals * scale
            removed_sat += float(np.nansum(old_vals - wrk_sim[r]))

    # scale Sunday rows proportionally (use sat_rate_c for Sun clamp)
    if sun_rate > 0 and sun_rate_c < sun_rate:
        scale = sun_rate_c / sun_rate
        sun_rows = od[3]
        for r in sun_rows:
            old_vals = wrk_sim[r].copy()
            wrk_sim[r] = old_vals * scale
            removed_sun += float(np.nansum(old_vals - wrk_sim[r]))

    n_clamped += 1

# Recalculate OW5 after clamp
syn["_wrate_sim"] = np.nanmean(wrk_sim, axis=1)
piv_sim = syn.pivot_table(index="occID", columns="DDAY_STRATA",
                          values="_wrate_sim", aggfunc="mean")
if set([1, 2, 3]).issubset(piv_sim.columns):
    sub_sim = piv_sim.dropna(subset=[1, 2, 3])
    ok_sim  = int(((sub_sim[1] >= sub_sim[2]) & (sub_sim[2] >= sub_sim[3])).sum())
    ow5_sim_pct = ok_sim / len(sub_sim) * 100
else:
    ow5_sim_pct = float("nan")

# Marginal drift as % of original work-slot totals
drift_sat = removed_sat / max(total_work_slots_sat, 1e-9) * 100
drift_sun = removed_sun / max(total_work_slots_sun, 1e-9) * 100

print(f"  OW5 BEFORE clamp: {ow5_pct:.1f}%")
print(f"  OW5 AFTER  clamp: {ow5_sim_pct:.1f}%   (target >= 90%)")
print(f"")
print(f"  AT_WORK marginal drift caused by clamp:")
print(f"    Weekday: 0 work-slots removed  (0.00%  of weekday work)")
print(f"    Saturday: {removed_sat:.0f} slot-units removed  ({drift_sat:.3f}% of Sat work)")
print(f"    Sunday:   {removed_sun:.0f} slot-units removed  ({drift_sun:.3f}% of Sun work)")
print(f"  n_occIDs clamped: {n_clamped:,} of {len(fail_occids):,} failing IDs")

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY READ
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("READ / VERDICT")
print("="*60)

noise_dominated = tiny_frac >= 50 and (vals[1] < slot1 * 3)  # median viol < 3 slots
near_zero_dom   = n_near_zero / max(len(fail), 1) >= 0.30
clamp_closes    = ow5_sim_pct >= 88.0
low_sat_drift   = drift_sat < 5.0
low_sun_drift   = drift_sun < 5.0

signals = []
if tiny_frac >= 50:
    signals.append(f"NOISE: {tiny_frac:.0f}% of fails have violation < 1 slot (noise)")
else:
    signals.append(f"GENUINE: only {tiny_frac:.0f}% of fails < 1 slot (genuine ordering)")
if near_zero_dom:
    signals.append(f"NOISE: {n_near_zero/len(fail)*100:.0f}% of fails are near-zero workers (marginal noise)")
if clamp_closes:
    signals.append(f"FIX-VIABLE: post-hoc clamp raises OW5 to {ow5_sim_pct:.1f}% (>= 88%)")
else:
    signals.append(f"FIX-PARTIAL: clamp only reaches {ow5_sim_pct:.1f}% — model-level fix needed too")
if low_sat_drift and low_sun_drift:
    signals.append(f"LOW-COST: marginal drift small (Sat {drift_sat:.2f}%, Sun {drift_sun:.2f}%)")
else:
    signals.append(f"HIGH-COST: marginal drift large (Sat {drift_sat:.2f}%, Sun {drift_sun:.2f}%)")

for s in signals:
    print(f"  {s}")

print("\n  VERDICT:", end=" ")
if clamp_closes and low_sat_drift and low_sun_drift and (noise_dominated or near_zero_dom):
    print("CHEAP POST-HOC FIX is viable — violations are mostly noise-level "
          "or near-zero-worker artefacts; clamp closes gate with small marginal drift.")
elif clamp_closes and not (low_sat_drift and low_sun_drift):
    print("FIX VIABLE but COSTLY — clamp closes OW5 but removes substantial "
          "weekend work mass; rake re-balance needed.")
elif not clamp_closes:
    print("MODEL-LEVEL FIX NEEDED — post-hoc clamp insufficient; genuine "
          "large ordering violations in true workers; aux L_order is the right lever.")
else:
    print("MIXED — see signals above.")

print("="*60)
print("[diag] Done.")
