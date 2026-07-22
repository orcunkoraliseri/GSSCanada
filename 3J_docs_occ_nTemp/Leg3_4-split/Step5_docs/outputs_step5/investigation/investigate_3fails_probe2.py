"""
investigate_3fails_probe2.py — Follow-up probes confirming the mechanisms found
by investigate_3fails.py. Diagnostic-only, read-only.

P1 (FAIL 1): Is the WD syn-vs-obs gap a POOL cell-conditional property?
    Predict the matched gap using pool cell-conditional syn/obs means with the
    matched frame's cell weights. If predicted ~= observed (-3.30pp), the
    residual is a Step-4 conditional-generation property, unfixable at Step 5.
P2 (FAIL 2): Does census demographic reweighting explain R1?
    For each (cycle x stratum) group, reweight pool retail diurnals by the
    matched frame's Tier-2 cell weights; compare max|dev| raw vs reweighted.
P3 (FAIL 2): Demographic composition matched vs pool (LFTAG / AGEGRP).
P4 (FAIL 3): occID -> region uniqueness; clean donor attribution for PR=6.

Run:  py -3 -X utf8 investigate_3fails_probe2.py > INVESTIGATION_probe2.log
"""
from __future__ import annotations

import importlib.util as ilu
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
STEP5 = HERE.parents[2]
OUT = STEP5 / "outputs_step5"

_spec = ilu.spec_from_file_location("_m", STEP5 / "3rdJ_05_censusLinkage_4split.py")
M = ilu.module_from_spec(_spec)
_spec.loader.exec_module(M)

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
RET = [f"ret30_{i:03d}" for i in range(1, 49)]
CELL = ["AGEGRP", "SEX", "LFTAG", "PR"]
FAIL_SLOTS_0B = [9, 10, 11, 16, 25, 26]   # slots 10,11,12,17,26,27 (1-based)

sched_cols = set(["PID", "occID", "MATCH_TIER", "DDAY_STRATA", "IS_SYNTHETIC",
                  "CYCLE_YEAR", "AGEGRP", "SEX", "LFTAG", "PR"]) | set(HOM) | set(RET)
sched = pd.read_csv(OUT / "3rdJ_25CEN_aug_Full_Schedules.csv",
                    usecols=lambda c: c in sched_cols, low_memory=False)
pool_cols = set(["occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC",
                 "AGEGRP", "SEX", "LFTAG", "PR"]) | set(HOM) | set(RET)
pool = pd.read_csv(M.FULL_POOL, usecols=lambda c: c in pool_cols, low_memory=False)
pool["PR_raw"] = pool["PR"]
pool["PR"] = pool["PR"].map(M._PROVINCE_TO_REGION).astype(int)
print(f"sched={len(sched):,}  pool={len(pool):,}")

for df in (sched, pool):
    df["_cell"] = df[CELL].fillna(-1).astype(float).astype(int).astype(str).agg("|".join, axis=1)

fail_cols = [HOM[i] for i in FAIL_SLOTS_0B]

# ── P1: pool cell-conditional prediction of the WD syn-vs-obs gap ────────────
print("\n" + "=" * 78)
print("P1 - FAIL 1: pool cell-conditional prediction of the matched WD gap")
print("=" * 78)
wd = sched[sched["DDAY_STRATA"] == 1]
pool_wd = pool[pool["DDAY_STRATA"] == 1]
syn_m = wd[wd["IS_SYNTHETIC"] == 1]
obs_m = wd[wd["IS_SYNTHETIC"] == 0]

pool_syn_c = pool_wd[pool_wd["IS_SYNTHETIC"] == 1].groupby("_cell")[fail_cols].mean().mean(axis=1)
pool_obs_c = pool_wd[pool_wd["IS_SYNTHETIC"] == 0].groupby("_cell")[fail_cols].mean().mean(axis=1)

w_syn = syn_m["_cell"].value_counts(normalize=True)
w_obs = obs_m["_cell"].value_counts(normalize=True)

cov_s = float(w_syn[w_syn.index.isin(pool_syn_c.index)].sum())
cov_o = float(w_obs[w_obs.index.isin(pool_obs_c.index)].sum())
pred_syn = float((w_syn * pool_syn_c.reindex(w_syn.index)).sum() /
                 w_syn[w_syn.index.isin(pool_syn_c.index)].sum())
pred_obs = float((w_obs * pool_obs_c.reindex(w_obs.index)).sum() /
                 w_obs[w_obs.index.isin(pool_obs_c.index)].sum())
act_syn = float(syn_m[fail_cols].mean(axis=1).mean())
act_obs = float(obs_m[fail_cols].mean(axis=1).mean())
print(f"  cell-weight coverage: syn {100*cov_s:.1f}%, obs {100*cov_o:.1f}%")
print(f"  PREDICTED from pool cell-conditional means: syn={100*pred_syn:.2f}% "
      f"obs={100*pred_obs:.2f}%  gap={100*(pred_syn-pred_obs):+.2f}pp")
print(f"  ACTUAL matched frame:                       syn={100*act_syn:.2f}% "
      f"obs={100*act_obs:.2f}%  gap={100*(act_syn-act_obs):+.2f}pp")
print("  -> If predicted ~= actual, the gap is the pool's own cell-conditional "
      "syn-vs-obs discrepancy (Step-4 property), reproduced faithfully by the matcher.")

# Largest cell-conditional pool discrepancies among high-weight cells
top_cells = w_syn.head(20).index
rows = []
for c in top_cells:
    if c in pool_syn_c.index and c in pool_obs_c.index:
        rows.append((c, float(w_syn[c]), 100 * float(pool_syn_c[c]),
                     100 * float(pool_obs_c[c]),
                     100 * float(pool_syn_c[c] - pool_obs_c[c])))
print("\n  Pool cell-conditional syn-vs-obs at failing slots, top matched-weight cells:")
print(f"  {'cell':>12} {'w_syn':>7} {'poolsyn%':>9} {'poolobs%':>9} {'gap_pp':>8}")
for c, w, s, o, g in rows[:12]:
    print(f"  {c:>12} {w:>7.3f} {s:>9.1f} {o:>9.1f} {g:>+8.1f}")

# ── P2: demographic reweighting explanation of R1 ────────────────────────────
print("\n" + "=" * 78)
print("P2 - FAIL 2: does census-demographic reweighting explain the R1 deviations?")
print("=" * 78)
print(f"  {'group':>9} {'raw_max':>8} {'rewgt_max':>10} {'cell_cov%':>10}")
for (cyc, dday), g_out in sched.groupby(["CYCLE_YEAR", "DDAY_STRATA"]):
    g_pool = pool[(pool["CYCLE_YEAR"] == cyc) & (pool["DDAY_STRATA"] == dday)]
    if len(g_out) == 0 or len(g_pool) == 0:
        continue
    mu_out = g_out[RET].mean().values
    mu_pool = g_pool[RET].mean().values
    raw_max = float(np.abs(mu_out - mu_pool).max() * 100)

    w = g_out["_cell"].value_counts(normalize=True)
    cell_mu = g_pool.groupby("_cell")[RET].mean()
    common = w.index.intersection(cell_mu.index)
    cov = float(w[common].sum())
    ww = w[common] / w[common].sum()
    pred = (cell_mu.loc[common].to_numpy() * ww.to_numpy()[:, None]).sum(axis=0)
    rew_max = float(np.abs(mu_out - pred).max() * 100)
    print(f"  {int(cyc)}-d{int(dday):<2} {raw_max:>8.3f} {rew_max:>10.3f} {100*cov:>10.1f}")
print("  (rewgt_max = max|matched - pool-reweighted-by-matched-cells|. If it "
      "collapses vs raw_max, the R1 deviation IS the demographic reweighting.)")

# ── P3: composition shift matched vs pool ────────────────────────────────────
print("\n" + "=" * 78)
print("P3 - composition: matched frame vs pool (drivers of the reweighting)")
print("=" * 78)
for name, dfm, dfp in [("WD", sched[sched["DDAY_STRATA"] == 1], pool[pool["DDAY_STRATA"] == 1]),
                       ("d2", sched[sched["DDAY_STRATA"] == 2], pool[pool["DDAY_STRATA"] == 2])]:
    lf_m = float((dfm["LFTAG"] == 1).mean())
    lf_p = float((dfp["LFTAG"] == 1).mean())
    print(f"  [{name}] LFTAG=1 (employed) share: matched={100*lf_m:.1f}%  pool={100*lf_p:.1f}%")
    am = dfm["AGEGRP"].value_counts(normalize=True).sort_index()
    ap = dfp["AGEGRP"].value_counts(normalize=True).sort_index()
    comp = pd.DataFrame({"matched%": am * 100, "pool%": ap * 100}).fillna(0)
    print(comp.to_string(float_format=lambda x: f"{x:.1f}"))

# ── P4: FAIL 3 donor attribution, done properly ──────────────────────────────
print("\n" + "=" * 78)
print("P4 - FAIL 3: occID uniqueness + clean donor-region attribution for PR=6")
print("=" * 78)
n_uniq = pool["occID"].nunique()
reg_per_occ = pool.groupby("occID")["PR"].nunique()
multi = int((reg_per_occ > 1).sum())
print(f"  pool rows={len(pool):,}, unique occIDs={n_uniq:,}, "
      f"occIDs mapping to >1 region: {multi}")
syn_per_occ = pool.groupby("occID")["IS_SYNTHETIC"].nunique()
print(f"  occIDs having both obs and syn rows: {int((syn_per_occ > 1).sum()):,} "
      f"(IS_SYNTHETIC attribution via occID join is only approximate)")

pr6 = sched[sched["PR"] == 6][["PID", "occID", "MATCH_TIER", "DDAY_STRATA", "IS_SYNTHETIC"]]
occ_region = pool.groupby("occID")["PR"].agg(lambda s: s.iloc[0] if s.nunique() == 1 else -9)
pr6 = pr6.merge(occ_region.rename("donor_region"), left_on="occID", right_index=True, how="left")
region_lbl = {1: "Atlantic", 2: "Quebec", 3: "Ontario", 4: "Prairies", 5: "BC",
              6: "North", -9: "AMBIGUOUS"}
print(f"\n  PR=6 agents: n={len(pr6)}; donor region (unique-per-occID, clean):")
for v, c in pr6["donor_region"].value_counts(dropna=False).sort_index().items():
    print(f"    region={v} ({region_lbl.get(int(v), '?') if pd.notna(v) else 'NO-JOIN'}): {c}")
print("  Donor IS_SYNTHETIC of the matched schedule rows themselves (carried col): "
      + ", ".join(f"{int(v)}={c}" for v, c in
                  pr6["IS_SYNTHETIC"].value_counts().sort_index().items()))
print("\nDONE.")
