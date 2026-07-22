"""
investigate_3fails.py — Diagnostic-only investigation of the 3 residual FAILs
(Step-5, 3J Leg-3 4-split, MIN_POOL=15 winner chain). READ-ONLY on all
production artifacts; writes nothing except stdout (redirect to a log).

FAIL 1: Gate 2.2 AT_HOME within-day-type (WD 3.66pp, 6 slots >3pp)
FAIL 2: Gate R1 AT_RETAIL matched-vs-pool by cycle x stratum (4.796pp, 2005-d2)
FAIL 3: Gate 0.1 PR census-subset-of-pool (PR=6 Territories missing from pool)

Run locally:  py -3 -X utf8 investigate_3fails.py > INVESTIGATION_run.log
"""
from __future__ import annotations

import importlib.util as ilu
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
STEP5 = HERE.parents[2]                      # Step5_docs/
OUT = STEP5 / "outputs_step5"
BASE = STEP5.parents[2]                      # GSSCanada-main/

# Import the live matcher module (defs only at top level; no side effects).
_spec = ilu.spec_from_file_location("_m", STEP5 / "3rdJ_05_censusLinkage_4split.py")
M = ilu.module_from_spec(_spec)
_spec.loader.exec_module(M)

POOL_FILE = M.FULL_POOL
CENSUS_FILE = M.CENSUS_FILE
SCHED_FILE = OUT / "3rdJ_25CEN_aug_Full_Schedules.csv"
EXCL_FILE = OUT / "3rdJ_25CEN_aug_excluded_pids.csv"

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
RET = [f"ret30_{i:03d}" for i in range(1, 49)]

T1K = M._T1_KEYS      # AGEGRP SEX MARSTH HHSIZE LFTAG PR CMA DDAY_STRATA
T2K = M._T2_KEYS      # AGEGRP SEX LFTAG PR DDAY_STRATA
T3K = M._T3_KEYS      # AGEGRP SEX DDAY_STRATA
MIN_POOL = 15

RNG = np.random.default_rng(12345)


def clock(slot_1based: int) -> str:
    """04:00-origin 48x30min diary: slot 1 = 04:00-04:30."""
    start_min = (4 * 60 + (slot_1based - 1) * 30) % (24 * 60)
    end_min = (start_min + 30) % (24 * 60)
    return f"{start_min // 60:02d}:{start_min % 60:02d}-{end_min // 60:02d}:{end_min % 60:02d}"


def hr(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ── Load data (usecols only — pool is 418 MB) ────────────────────────────────
hr("LOAD")
sched_cols = set(["PID", "occID", "MATCH_TIER", "DDAY_STRATA", "IS_SYNTHETIC",
                  "CYCLE_YEAR", "AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG",
                  "PR", "CMA"]) | set(HOM) | set(RET)
sched = pd.read_csv(SCHED_FILE, usecols=lambda c: c in sched_cols, low_memory=False)
print(f"Full_Schedules: {len(sched):,} rows x {sched.shape[1]} cols")
print(f"  CMA domain in matched frame: {sorted(sched['CMA'].dropna().unique())}")
print(f"  PR  domain in matched frame: {sorted(sched['PR'].dropna().unique())}")

pool_cols = set(["occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC",
                 "AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA"]) \
            | set(HOM) | set(RET)
pool = pd.read_csv(POOL_FILE, usecols=lambda c: c in pool_cols, low_memory=False)
print(f"Pool: {len(pool):,} rows x {pool.shape[1]} cols")

# Replicate the matcher's pool-side harmonization (PR province->region, CMA binary)
pool["PR_raw"] = pool["PR"]
pool["PR"] = pool["PR"].map(M._PROVINCE_TO_REGION).astype(int)
pool["CMA_raw"] = pool["CMA"]
pool["CMA"] = pool["CMA"].map(M._CMA_POOL_TO_METRO).astype(int)

census = pd.read_csv(CENSUS_FILE, usecols=["PID", "PR"], low_memory=False)
census = census.drop_duplicates(subset="PID").reset_index(drop=True)
print(f"Census (deduped PIDs): {len(census):,} rows")

excl = pd.read_csv(EXCL_FILE, low_memory=False)
print(f"excluded_pids: {len(excl):,} rows")


# ═════════════════════════════════════════════════════════════════════════════
# FAIL 1 — Gate 2.2 AT_HOME, weekday (WD) within-day-type
# ═════════════════════════════════════════════════════════════════════════════
hr("FAIL 1 - Gate 2.2 AT_HOME (WD within-day-type)")

wd = sched[sched["DDAY_STRATA"] == 1]
syn_wd = wd[wd["IS_SYNTHETIC"] == 1]
obs_wd = wd[wd["IS_SYNTHETIC"] == 0]
we = sched[sched["DDAY_STRATA"].isin([2, 3])]
syn_we = we[we["IS_SYNTHETIC"] == 1]
obs_we = we[we["IS_SYNTHETIC"] == 0]

m_syn = syn_wd[HOM].mean().values * 100
m_obs = obs_wd[HOM].mean().values * 100
d_wd = m_syn - m_obs
d_we = (syn_we[HOM].mean().values - obs_we[HOM].mean().values) * 100

print(f"[replication] 2.2-WD syn={len(syn_wd)}, obs={len(obs_wd)}, "
      f"max|diff|={np.abs(d_wd).max():.2f}pp, slots>3pp={int((np.abs(d_wd) > 3).sum())}"
      f"   (frozen ref: syn=6052 obs=15506 3.66pp / 6 slots)")
print(f"[replication] 2.2-WE syn={len(syn_we)}, obs={len(obs_we)}, "
      f"max|diff|={np.abs(d_we).max():.2f}pp, slots>3pp={int((np.abs(d_we) > 3).sum())}"
      f"   (frozen ref: syn=7448 obs=1267 2.17pp / 0 slots)")

fail_idx = np.where(np.abs(d_wd) > 3)[0]        # 0-based
fail_slots = [i + 1 for i in fail_idx]           # 1-based

print("\n[1.1] Failing WD slot table (syn - obs, signed):")
print(f"  {'slot':>4} {'clock':>13} {'syn%':>7} {'obs%':>7} {'d_pp':>7}")
for i in fail_idx:
    print(f"  {i+1:>4} {clock(i+1):>13} {m_syn[i]:>7.2f} {m_obs[i]:>7.2f} {d_wd[i]:>+7.2f}")

# ── 1.2 Intrinsic-vs-matcher decomposition:
#     gate gap = (matched_syn - pool_syn) - (matched_obs - pool_obs) + (pool_syn - pool_obs)
pool_wd = pool[pool["DDAY_STRATA"] == 1]
p_syn = pool_wd[pool_wd["IS_SYNTHETIC"] == 1][HOM].mean().values * 100
p_obs = pool_wd[pool_wd["IS_SYNTHETIC"] == 0][HOM].mean().values * 100
d_pool = p_syn - p_obs

print(f"\n[1.2] POOL WD intrinsic syn-vs-obs: max|diff|={np.abs(d_pool).max():.2f}pp, "
      f"slots>3pp={int((np.abs(d_pool) > 3).sum())} "
      f"(n_syn={int((pool_wd['IS_SYNTHETIC'] == 1).sum()):,}, "
      f"n_obs={int((pool_wd['IS_SYNTHETIC'] == 0).sum()):,})")
print("  Decomposition at the failing slots (all pp, signed):")
print(f"  {'slot':>4} {'clock':>13} {'gate_gap':>9} {'pool_intrinsic':>15} "
      f"{'match_syn_shift':>16} {'match_obs_shift':>16}")
for i in fail_idx:
    ms_shift = m_syn[i] - p_syn[i]
    mo_shift = m_obs[i] - p_obs[i]
    print(f"  {i+1:>4} {clock(i+1):>13} {d_wd[i]:>+9.2f} {d_pool[i]:>+15.2f} "
          f"{ms_shift:>+16.2f} {mo_shift:>+16.2f}")
print("  (gate_gap = pool_intrinsic + match_syn_shift - match_obs_shift; if "
      "pool_intrinsic dominates, no Step-5 matcher change can fix 2.2.)")

# ── 1.3 Thin-cell / tier attribution for the WD matched rows
# Pool cell sizes at each tier (post-harmonization, dropna like _build_index)
def cell_sizes(keys: list[str]) -> pd.DataFrame:
    v = pool.dropna(subset=keys)
    return v.groupby(keys, sort=False).size().reset_index(name="_n")

sz1 = cell_sizes(T1K).rename(columns={"_n": "n_t1"})
sz2 = cell_sizes(T2K).rename(columns={"_n": "n_t2"})
sz3 = cell_sizes(T3K).rename(columns={"_n": "n_t3"})

wdk = wd[["PID", "MATCH_TIER", "IS_SYNTHETIC"] + T1K].copy()
wdk = wdk.merge(sz1, on=T1K, how="left").merge(sz2, on=T2K, how="left") \
         .merge(sz3, on=T3K, how="left")

tier_to_size = {"1_Perfect": "n_t1", "2_Core": "n_t2", "3_Constraints": "n_t3"}
wdk["resolved_n"] = np.nan
for t, col in tier_to_size.items():
    m = wdk["MATCH_TIER"] == t
    wdk.loc[m, "resolved_n"] = wdk.loc[m, col]
wdk["broadened"] = wdk["resolved_n"] < MIN_POOL

print(f"\n[1.3] WD matched rows by tier / thin-cell (resolved cell < {MIN_POOL} donors "
      f"=> broadened):")
tt = wdk.groupby("MATCH_TIER").agg(n=("PID", "size"),
                                   n_broadened=("broadened", "sum"),
                                   med_cell=("resolved_n", "median"))
print(tt.to_string())
print(f"  WD rows total={len(wdk)}, broadened={int(wdk['broadened'].sum())} "
      f"({100 * wdk['broadened'].mean():.2f}%)")

# Does thin-cell membership actually depress morning AT_HOME (failing slots)?
fail_cols = [HOM[i] for i in fail_idx]
wd_sched = wd.set_index("PID")
wdk = wdk.set_index("PID")
wdk["fail_hom"] = wd_sched.loc[wdk.index, fail_cols].mean(axis=1)

print("\n[1.4] Mean AT_HOME over the failing slots, by origin x thin-cell:")
g = wdk.groupby(["IS_SYNTHETIC", "broadened"])["fail_hom"].agg(["size", "mean"])
g["mean"] = g["mean"] * 100
print(g.to_string(float_format=lambda x: f"{x:.2f}"))

# ── 1.5 Tier-2 cell contribution table (signed, sums to the gap)
wdk2 = wdk.reset_index()
cell_cols = ["AGEGRP", "SEX", "LFTAG", "PR"]
wdk2["_cell"] = wdk2[cell_cols].fillna(-1).astype(float).astype(int).astype(str).agg("|".join, axis=1)
wdk2["fail_hom"] = wdk2["fail_hom"].astype(float)

syn_c = wdk2[wdk2["IS_SYNTHETIC"] == 1]
obs_c = wdk2[wdk2["IS_SYNTHETIC"] == 0]
Ns, No = len(syn_c), len(obs_c)

agg_s = syn_c.groupby("_cell").agg(n_syn=("fail_hom", "size"), m_syn=("fail_hom", "mean"))
agg_o = obs_c.groupby("_cell").agg(n_obs=("fail_hom", "size"), m_obs=("fail_hom", "mean"))
cells = agg_s.join(agg_o, how="outer").fillna({"n_syn": 0, "n_obs": 0})
cells["w_syn"] = cells["n_syn"] / Ns
cells["w_obs"] = cells["n_obs"] / No
m_obs_overall = obs_c["fail_hom"].mean()
cells["m_obs_f"] = cells["m_obs"].fillna(m_obs_overall)
cells["m_syn_f"] = cells["m_syn"].fillna(0)
cells["contrib_pp"] = (cells["w_syn"] * cells["m_syn_f"] - cells["w_obs"] * cells["m_obs_f"]) * 100
cells["within_pp"] = (cells["w_syn"] * (cells["m_syn_f"] - cells["m_obs_f"])) * 100
cells["comp_pp"] = cells["contrib_pp"] - cells["within_pp"]

gap_check = cells["contrib_pp"].sum()
gap_direct = (syn_c["fail_hom"].mean() - obs_c["fail_hom"].mean()) * 100
print(f"\n[1.5] Tier-2-cell decomposition of the mean gap over failing slots: "
      f"gap={gap_direct:+.2f}pp (cell-sum check {gap_check:+.2f}pp)")
print(f"  within-cell (syn diaries differ inside same cell): "
      f"{cells['within_pp'].sum():+.2f}pp")
print(f"  composition (syn rows sit in different cells):     "
      f"{cells['comp_pp'].sum():+.2f}pp")

# attach pool T2 sizes for the top cells
sz2k = sz2[sz2["DDAY_STRATA"] == 1].copy()
sz2k["_cell"] = sz2k[cell_cols].fillna(-1).astype(float).astype(int).astype(str).agg("|".join, axis=1)
sz2k = sz2k.set_index("_cell")["n_t2"]
cells["pool_t2_n"] = cells.index.map(sz2k)

top = cells.reindex(cells["contrib_pp"].abs().sort_values(ascending=False).index).head(10)
print("\n  Top-10 contributing Tier-2 cells (AGEGRP|SEX|LFTAG|PR, -1=NaN), signed pp:")
print(f"  {'cell':>14} {'n_syn':>6} {'n_obs':>6} {'m_syn%':>7} {'m_obs%':>7} "
      f"{'contrib':>8} {'within':>8} {'comp':>8} {'poolT2n':>8}")
for c, r in top.iterrows():
    msn = r["m_syn"] * 100 if pd.notna(r["m_syn"]) else float("nan")
    mob = r["m_obs"] * 100 if pd.notna(r["m_obs"]) else float("nan")
    print(f"  {c:>14} {int(r['n_syn']):>6} {int(r['n_obs']):>6} {msn:>7.1f} {mob:>7.1f} "
          f"{r['contrib_pp']:>+8.3f} {r['within_pp']:>+8.3f} {r['comp_pp']:>+8.3f} "
          f"{str(int(r['pool_t2_n'])) if pd.notna(r['pool_t2_n']) else 'n/a':>8}")

neg = cells[(cells["contrib_pp"] * np.sign(gap_direct) > 0)]
thin5 = neg[pd.notna(neg["pool_t2_n"])].nsmallest(5, "pool_t2_n")
print("\n  Top-5 THINNEST cells contributing in the gap direction (by pool T2 size):")
for c, r in thin5.iterrows():
    print(f"    cell={c}  pool_t2_n={int(r['pool_t2_n'])}  n_syn={int(r['n_syn'])} "
          f"n_obs={int(r['n_obs'])}  contrib={r['contrib_pp']:+.3f}pp")


# ═════════════════════════════════════════════════════════════════════════════
# FAIL 2 — Gate R1 AT_RETAIL matched vs pool, by cycle x stratum
# ═════════════════════════════════════════════════════════════════════════════
hr("FAIL 2 - Gate R1 AT_RETAIL (matched vs pool, cycle x stratum)")

groups = []
for (cyc, dday), g_out in sched.groupby(["CYCLE_YEAR", "DDAY_STRATA"]):
    g_pool = pool[(pool["CYCLE_YEAR"] == cyc) & (pool["DDAY_STRATA"] == dday)]
    if len(g_out) == 0 or len(g_pool) == 0:
        continue
    d = (g_out[RET].mean().values - g_pool[RET].mean().values) * 100
    groups.append((cyc, dday, len(g_out), len(g_pool), d, g_out, g_pool))

print("[replication] R1 per-group max|dev| (frozen: 2005-d2 = 4.796 max):")
for cyc, dday, n_out, n_pool, d, *_ in groups:
    print(f"  {int(cyc)} d{int(dday)}: n_out={n_out:>6} n_pool={n_pool:>6} "
          f"max|dev|={np.abs(d).max():.3f}pp {'<-- FAIL(>3)' if np.abs(d).max() > 3 else ''}")

worst = max(groups, key=lambda t: np.abs(t[4]).max())
cyc_w, dday_w, n_out_w, n_pool_w, d_w, g_out_w, g_pool_w = worst
print(f"\n[2.1] Worst group {int(cyc_w)}-d{int(dday_w)}: per-slot signed dev "
      f"(matched - pool), pp:")
print(f"  {'slot':>4} {'clock':>13} {'match%':>8} {'pool%':>8} {'d_pp':>7}")
mo = g_out_w[RET].mean().values * 100
po = g_pool_w[RET].mean().values * 100
for i in range(48):
    flag = "  <-- >3pp" if abs(d_w[i]) > 3 else ("  <" if abs(d_w[i]) > 1.0 else "")
    if abs(d_w[i]) > 1.0:
        print(f"  {i+1:>4} {clock(i+1):>13} {mo[i]:>8.3f} {po[i]:>8.3f} {d_w[i]:>+7.3f}{flag}")
print(f"  (only slots with |dev|>1pp printed; {int((np.abs(d_w) > 1).sum())} such slots)")

mean_offset = d_w.mean()
resid = d_w - mean_offset
daily_m, daily_p = mo.mean(), po.mean()
corr = np.corrcoef(mo, po)[0, 1]
print(f"\n[2.2] Magnitude-vs-shape: daily mean matched={daily_m:.3f}% pool={daily_p:.3f}% "
      f"(offset {daily_m - daily_p:+.3f}pp); mean per-slot offset={mean_offset:+.3f}pp; "
      f"max|shape residual after removing offset|={np.abs(resid).max():.3f}pp; "
      f"diurnal corr={corr:.3f}")

# Bootstrap null: draw n_out i.i.d. from the pool group -> distribution of max|dev|
def null_maxdev(g_pool: pd.DataFrame, n_out: int, B: int = 1000) -> np.ndarray:
    P = g_pool[RET].to_numpy(dtype=np.float32)
    mu = P.mean(axis=0)
    out = np.empty(B)
    for b in range(B):
        idx = RNG.integers(0, len(P), size=n_out)
        out[b] = np.abs(P[idx].mean(axis=0) - mu).max() * 100
    return out

print("\n[2.3] Null test per group: if the matched group were a RANDOM n_out draw "
      "from its pool group, how often is max|dev| >= 3.0 (the FAIL line)?")
print(f"  {'group':>9} {'n_out':>6} {'obs_max':>8} {'null_p50':>9} {'null_p95':>9} "
      f"{'P(>=3.0)':>9} {'P(>=obs)':>9}")
for cyc, dday, n_out, n_pool, d, g_out, g_pool in groups:
    nd = null_maxdev(g_pool, n_out, B=1000)
    obs_max = np.abs(d).max()
    print(f"  {int(cyc)}-d{int(dday):<2} {n_out:>6} {obs_max:>8.3f} "
          f"{np.percentile(nd, 50):>9.3f} {np.percentile(nd, 95):>9.3f} "
          f"{np.mean(nd >= 3.0):>9.3f} {np.mean(nd >= obs_max):>9.3f}")

# Matched-side bootstrap CI at the worst slot of the worst group
worst_slot = int(np.abs(d_w).argmax())
Mx = g_out_w[RET].to_numpy(dtype=np.float32)
boot = np.empty((2000,))
boot_max = np.empty((2000,))
pool_mu = po / 100
for b in range(2000):
    idx = RNG.integers(0, len(Mx), size=len(Mx))
    mb = Mx[idx].mean(axis=0)
    boot[b] = mb[worst_slot]
    boot_max[b] = np.abs(mb - pool_mu).max() * 100
ci = np.percentile(boot, [2.5, 97.5]) * 100
ci_max = np.percentile(boot_max, [2.5, 97.5])
print(f"\n[2.4] Worst slot {worst_slot+1} ({clock(worst_slot+1)}) of "
      f"{int(cyc_w)}-d{int(dday_w)}: matched={mo[worst_slot]:.3f}% "
      f"95%CI [{ci[0]:.3f}, {ci[1]:.3f}], pool={po[worst_slot]:.3f}% "
      f"({'inside' if ci[0] <= po[worst_slot] <= ci[1] else 'OUTSIDE'} CI)")
print(f"      Bootstrap 95%CI of the group max|dev| statistic: "
      f"[{ci_max[0]:.3f}, {ci_max[1]:.3f}] pp (3.0 line "
      f"{'inside' if ci_max[0] <= 3.0 <= ci_max[1] else 'outside'})")
uniq = g_out_w["occID"].nunique()
freq = g_out_w["occID"].value_counts(normalize=True).to_numpy()
n_eff = 1.0 / np.sum(freq ** 2)
print(f"      Donor reuse in {int(cyc_w)}-d{int(dday_w)}: n_out={n_out_w}, "
      f"unique donors={uniq}, effective n={n_eff:.0f}")

# R2a context: is the pool itself inside the 0.06-0.10 midday band?
mid = RET[16:20]
wd_s = sched[sched["DDAY_STRATA"] == 1]
wd_p = pool[pool["DDAY_STRATA"] == 1]
r2a_m = float(wd_s[mid].mean().mean())
r2a_p = float(wd_p[mid].mean().mean())
print(f"\n[2.5] R2a context - weekday 12:00-14:00 AT_RETAIL rate: matched={r2a_m:.4f}, "
      f"POOL ITSELF={r2a_p:.4f} (expected band 0.06-0.10). If the pool is below "
      f"band, R2a is a pool/Step-4 property, not a matching loss.")
obs_p = pool[(pool["DDAY_STRATA"] == 1) & (pool["IS_SYNTHETIC"] == 0)]
syn_p = pool[(pool["DDAY_STRATA"] == 1) & (pool["IS_SYNTHETIC"] == 1)]
print(f"      Pool WD split: obs-GSS={float(obs_p[mid].mean().mean()):.4f}, "
      f"synthetic={float(syn_p[mid].mean().mean()):.4f}")


# ═════════════════════════════════════════════════════════════════════════════
# FAIL 3 — Gate 0.1 PR=6 (Territories) census not in pool
# ═════════════════════════════════════════════════════════════════════════════
hr("FAIL 3 - Gate 0.1 PR=6 (Territories) frame gap")

print("[3.1] Census PR distribution (deduped PIDs):")
for v, c in census["PR"].value_counts(dropna=False).sort_index().items():
    print(f"  PR={v}: {c}")
n_pr6_census = int((census["PR"] == 6).sum())

pr6 = sched[sched["PR"] == 6]
print(f"\n[3.2] PR=6 rows in matched frame (Full_Schedules): {len(pr6)} "
      f"(census PR=6 total: {n_pr6_census})")
print("  MATCH_TIER distribution:")
for t, c in pr6["MATCH_TIER"].value_counts().sort_index().items():
    print(f"    {t}: {c} ({100 * c / len(pr6):.1f}%)")
print("  DDAY distribution: " + ", ".join(
    f"d{int(v)}={c}" for v, c in pr6["DDAY_STRATA"].value_counts().sort_index().items()))

# excluded overlap
excl_pr = excl.merge(census, on="PID", how="left")
n_pr6_excl = int((excl_pr["PR"] == 6).sum())
print(f"  PR=6 among the 771 excluded_pids: {n_pr6_excl}")

# Donor province via occID join (check uniqueness first)
dup = pool["occID"].duplicated().sum()
print(f"\n[3.3] Donor-PR audit via occID (pool occID duplicates: {dup})")
pool_don = pool.drop_duplicates(subset="occID")[["occID", "PR", "PR_raw", "IS_SYNTHETIC", "CYCLE_YEAR"]]
pr6d = pr6[["PID", "occID", "MATCH_TIER"]].merge(
    pool_don, on="occID", how="left", suffixes=("", "_donor"))
region_lbl = {1: "Atlantic", 2: "Quebec", 3: "Ontario", 4: "Prairies", 5: "BC", 6: "North"}
print("  Donor region (pool PR after province->region remap) for PR=6 census agents:")
for v, c in pr6d["PR"].value_counts(dropna=False).sort_index().items():
    lbl = region_lbl.get(int(v), "?") if pd.notna(v) else "UNMATCHED-JOIN"
    print(f"    region={v} ({lbl}): {c} ({100 * c / len(pr6d):.1f}%)")
print("  Donor raw province codes:")
for v, c in pr6d["PR_raw"].value_counts(dropna=False).sort_index().items():
    print(f"    PR_raw={v}: {c}")
print("  Donor IS_SYNTHETIC: " + ", ".join(
    f"{int(v)}={c}" for v, c in pr6d["IS_SYNTHETIC"].value_counts(dropna=False).sort_index().items()))

print(f"\n[3.4] If PR=6 were excluded: Full_Schedules {len(sched):,} -> "
      f"{len(sched) - len(pr6):,} rows; excluded_pids {len(excl):,} -> "
      f"{len(excl) + len(pr6):,}")

print("\nDONE.")
