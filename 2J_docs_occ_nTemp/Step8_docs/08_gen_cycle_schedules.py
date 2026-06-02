"""08_gen_cycle_schedules.py — Step 8 / Prereq P1: historical-cycle BEM schedules.

Generates BEM_Setup/BEM_Schedules_{2005,2010,2015}.csv so the Step-8 longitudinal
simulation has all five years (2005/2010/2015/2022/2030) on ONE consistent method.

Per cycle:
  1. Pull that cycle's diaries from augmented_diaries.csv (filter CYCLE_YEAR).
  2. Phase-8B rake: flip SYNTHETIC hom30 per (DDAY_STRATA x slot) to the cycle's own
     OBSERVED (IS_SYNTHETIC==0) within-stratum marginal (minimal-flip, boundary-preferred,
     seed=42). hom30 only; act30 untouched. (synthetic WD AT_HOME runs 5-10 pp low.)
  3. Assemble onto the FROZEN 2022 dwelling frame (aug_Full_Aggregated_excl): swap each
     stock person's hom30/act30 for a stratum-matched draw from the raked cycle pool
     (seed=42) -> "freeze stock, evolve occupancy" (same as assemble_2030).
  4. Donor-draw day-completion + convert -> 13-col hourly BEM file.

Reuses convert / complete_day_types / maps from 07_aug_to_bem.py and
_rake_binary_slot / _boundary_mask from 06_forecast_rake.py (replicated here so the
script is self-contained under Step8_docs/). Run-from-anywhere, seed=42, reversible.
  py 08_gen_cycle_schedules.py --year 2015 | --year all
"""
import os, sys, argparse, shutil
from pathlib import Path
import numpy as np, pandas as pd
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Paths ───────────────────────────────────────────────────────────────────────
HERE  = Path(__file__).resolve().parent          # 2J_docs_occ_nTemp/Step8_docs/
J2    = HERE.parent                               # 2J_docs_occ_nTemp/
BASE  = J2.parent                                 # GSSCanada-main/
AUGD  = J2 / "outputs_step4" / "augmented_diaries.csv"
STOCK = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline" / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
D2030 = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030" / "2030_synthetic_diaries.csv"
BEMS  = BASE / "BEM_Setup"

# ── Constants (mirror 07_aug_to_bem.py) ─────────────────────────────────────────
N = 48
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
STAT = ["HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER"]
OUT_COLS = ["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "DTYPE", "BEDRM", "CONDO",
            "ROOM", "REPAIR", "PR", "MATCH_TIER", "Occupancy_Schedule", "Metabolic_Rate"]
MET = {0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105, 7: 170,
       8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135}
PR_LBL = {10: "Atlantic", 11: "Atlantic", 12: "Atlantic", 13: "Atlantic", 24: "Quebec",
          35: "Ontario", 46: "Prairies", 47: "Prairies", 48: "Alberta", 59: "BC", 70: "Northern Canada"}
DAYTYPE = {1: "Weekday", 2: "Weekend", 3: "Weekend"}
STRATA = [1, 2, 3]
LBL = {1: "WD", 2: "Sat", 3: "Sun"}
CYCLES = [2005, 2010, 2015]

# Demographic-matched assembly (option B). Geography (PR/CMA) dropped from the OCCUPANCY match so
# every cycle matches on the SAME demographic keys (2005's geography coding differs pre-harmonization
# → uneven tiers); geography is a weak occupancy driver and the frame keeps its own PR for weather.
KEYS  = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG"]
TIERS = [KEYS,                            # T1 all 5 demographic keys + strata
         ["AGEGRP", "SEX", "LFTAG"],      # T2 main occupancy drivers
         ["AGEGRP", "SEX"],               # T3 age+sex (catches LFTAG coding gaps)
         []]                              # T4 FailSafe (stratum-only)


# ── rake helpers (from 06_forecast_rake.py) ─────────────────────────────────────
def _boundary_mask(arr, t):
    val_t = arr[:, t]
    left  = (arr[:, t - 1] != val_t) if t > 0 else np.ones(len(arr), dtype=bool)
    right = (arr[:, t + 1] != val_t) if t < arr.shape[1] - 1 else np.ones(len(arr), dtype=bool)
    return left | right


def _rake_binary_slot(arr_col, target_count, boundary, rng):
    n_cur = int(np.sum(arr_col == 1.0))
    delta = target_count - n_cur
    if delta == 0:
        return 0
    if delta > 0:
        cand = np.where(arr_col == 0.0)[0]; n_flip = min(delta, len(cand))
    else:
        cand = np.where(arr_col == 1.0)[0]; n_flip = min(-delta, len(cand))
    if n_flip == 0:
        return 0
    order = np.lexsort((rng.random(len(cand)), -boundary[cand].astype(np.int8)))
    chosen = cand[order[:n_flip]]
    arr_col[chosen] = 1.0 - arr_col[chosen]
    return n_flip


# ── convert / complete_day_types / dtype_label (from 07_aug_to_bem.py) ──────────
def dtype_label(code, bedrm):
    if int(code) == 2:
        try: b = int(float(bedrm))
        except (ValueError, TypeError): b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(int(code), str(int(code)))


def convert(df):
    df = df.rename(columns={"HH_ID": "SIM_HH_ID"}).copy()
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)
    keys = ["SIM_HH_ID", "Day_Type"]
    occ48 = df.groupby(keys, sort=True)[HOM].mean()
    wdf = df[keys].copy()
    for c in ACT: wdf[c] = df[c].map(MET).fillna(100.0)
    met48 = wdf.groupby(keys, sort=True)[ACT].mean().reindex(occ48.index)
    stat  = df.groupby(keys, sort=True)[STAT].first().reindex(occ48.index)
    G = len(occ48.index)
    occ24 = occ48.values.reshape(G, 24, 2).mean(axis=2)
    met24 = met48.values.reshape(G, 24, 2).mean(axis=2)
    out = pd.DataFrame({
        "SIM_HH_ID": occ48.index.get_level_values("SIM_HH_ID").repeat(24),
        "Day_Type":  occ48.index.get_level_values("Day_Type").repeat(24),
        "Hour":      np.tile(np.arange(24), G),
        "Occupancy_Schedule": np.round(occ24.reshape(-1), 3),
        "Metabolic_Rate":     np.round(met24.reshape(-1), 1),
    })
    for col in ["HHSIZE", "BEDRM", "CONDO", "ROOM", "REPAIR", "MATCH_TIER"]:
        out[col] = np.repeat(stat[col].values, 24)
    dt = np.repeat(stat["DTYPE"].values, 24); bd = np.repeat(stat["BEDRM"].values, 24)
    out["DTYPE"] = [dtype_label(c, b) for c, b in zip(dt, bd)]
    pr = np.repeat(stat["PR"].values, 24)
    out["PR"] = [PR_LBL.get(int(p), str(int(p))) for p in pr]
    return out[OUT_COLS]


def complete_day_types(df):
    rng = np.random.default_rng(42)
    hh_strata = df.groupby('HH_ID')['DDAY_STRATA'].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])
    wd_pool = df[df['DDAY_STRATA'] == 1]
    we_pool = df[df['DDAY_STRATA'].isin([2, 3])]
    extra = []
    if wd_only:
        sub = df[df['HH_ID'].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[ACT + HOM] = we_pool.iloc[pick][ACT + HOM].values
        sub['DDAY_STRATA'] = 2
        extra.append(sub)
        print(f"  donor-draw {len(wd_only):,} WD-only HHs -> Weekend ({len(sub):,} rows)", flush=True)
    if we_only:
        sub = df[df['HH_ID'].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[ACT + HOM] = wd_pool.iloc[pick][ACT + HOM].values
        sub['DDAY_STRATA'] = 1
        extra.append(sub)
        print(f"  donor-draw {len(we_only):,} WE-only HHs -> Weekday ({len(sub):,} rows)", flush=True)
    return pd.concat([df] + extra, ignore_index=True) if extra else df


# ── per-cycle Phase-8B rake (synthetic -> observed within-stratum marginal) ──────
def rake_cycle(pool):
    """Flip IS_SYNTHETIC==1 hom30 per (stratum x slot) to the cycle's observed marginal."""
    rng = np.random.default_rng(42)
    hom = pool[HOM].values.astype(float)
    assert set(np.unique(hom[~np.isnan(hom)])).issubset({0.0, 1.0}), "hom30 not 0/1"
    syn = (pool["IS_SYNTHETIC"].values == 1)
    strata = pool["DDAY_STRATA"].values
    flips = 0
    for s in STRATA:
        obs_m = hom[(~syn) & (strata == s)].mean(axis=0)          # observed (48,)
        idx = np.where(syn & (strata == s))[0]
        if len(idx) == 0:
            continue
        sub = hom[idx]
        for t in range(N):
            tgt = max(0, min(len(idx), int(round(obs_m[t] * len(idx)))))
            flips += _rake_binary_slot(sub[:, t], tgt, _boundary_mask(sub, t), rng)
        hom[idx] = sub
        wd_pre = pool.loc[pool.index[idx], HOM].values.mean() * 100
        print(f"    rake {LBL[s]}: {len(idx):,} syn rows -> obs marginal "
              f"(syn {wd_pre:.2f}% -> {sub.mean()*100:.2f}%, obs {obs_m.mean()*100:.2f}%)", flush=True)
    pool = pool.copy()
    pool[HOM] = hom
    print(f"    total hom30 flips: {flips:,}", flush=True)
    return pool


def _canon(df, cols):
    """Canonical string per key: nullable-int repr so 1 (frame int) and 1.0 (pool float w/ NaN)
    match; NaN -> '<NA>' (never equals the frame's clean keys, correctly forcing a coarser tier)."""
    return {k: pd.to_numeric(df[k], errors="coerce").astype("Int64").astype(str).values for k in cols}


def demo_assemble(stock, pool):
    """Option B: match each frame person to a cycle diary by TIERED demographics + stratum,
    then swap in that diary's act30/hom30. Keeps the frame's demographics/dwelling; only the
    occupancy time-series changes — so the same SIM_HH_ID is comparable across cycles (paired)."""
    from collections import defaultdict
    rng = np.random.default_rng(42)
    pool = pool.reset_index(drop=True)
    allk = KEYS + ["DDAY_STRATA"]
    sc, pc = _canon(stock, allk), _canon(pool, allk)

    def ck(canon, gk):
        out = canon[gk[0]].astype(object)
        for k in gk[1:]:
            out = out + "|" + canon[k]
        return out

    n = len(stock)
    chosen = np.full(n, -1, np.int64)
    tier_of = np.zeros(n, np.int8)
    remaining = np.ones(n, bool)
    for ti, ks in enumerate(TIERS, 1):
        gk = ks + ["DDAY_STRATA"]
        grp = defaultdict(list)
        for pos, key in enumerate(ck(pc, gk)):
            grp[key].append(pos)
        grp = {k: np.asarray(v) for k, v in grp.items()}
        sck = ck(sc, gk)
        for j in np.where(remaining)[0]:
            arr = grp.get(sck[j])
            if arr is not None and len(arr):
                chosen[j] = arr[rng.integers(len(arr))]
                tier_of[j] = ti
                remaining[j] = False
        lbl = ",".join(ks) if ks else "strata-only"
        print(f"    tier {ti} ({lbl}): matched {int((tier_of == ti).sum()):,}, "
              f"remaining {int(remaining.sum()):,}", flush=True)
        if not remaining.any():
            break
    assert chosen.min() >= 0, "unmatched frame rows remain"
    out = stock.copy()
    out[ACT + HOM] = pool.iloc[chosen][ACT + HOM].values
    return out


def finalize(year, assembled):
    """Shared tail: day-completion + convert + gates + backup + atomic write + summary."""
    bem = convert(complete_day_types(assembled))
    assert set(bem["Day_Type"].unique()) <= {"Weekday", "Weekend"}
    assert bem["Hour"].between(0, 23).all()
    assert bem["Occupancy_Schedule"].between(0, 1).all()
    assert (bem["Metabolic_Rate"] >= 0).all()
    cov = bem.groupby("SIM_HH_ID")["Day_Type"].nunique()
    assert (cov == 2).all(), f"{int((cov<2).sum())} HHs missing a day-type"
    target = BEMS / f"BEM_Schedules_{year}.csv"
    if target.exists():
        bak = BEMS / f"BEM_Schedules_{year}_PRE_STEP8_BAK.csv"
        if not bak.exists():
            shutil.copy2(target, bak); print(f"  backed up -> {bak.name}", flush=True)
    tmp = str(target) + ".tmp"
    bem.to_csv(tmp, index=False, float_format="%.3f")
    os.replace(tmp, str(target))
    nhh = bem["SIM_HH_ID"].nunique()
    print(f"  WROTE {target.name}: {len(bem):,} rows, {nhh:,} HH", flush=True)
    for d in ("Weekday", "Weekend"):
        sub = bem[bem.Day_Type == d]
        print(f"    {d}: occ {sub.Occupancy_Schedule.mean():.3f}, met {sub.Metabolic_Rate.mean():.1f}", flush=True)


def gen_cycle(year, aug, stock):
    print(f"\n{'='*64}\n  CYCLE {year}\n{'='*64}", flush=True)
    pool = aug[aug["CYCLE_YEAR"] == year]
    print(f"  pool: {len(pool):,} rows "
          f"(obs {(pool.IS_SYNTHETIC==0).sum():,} / syn {(pool.IS_SYNTHETIC==1).sum():,})", flush=True)
    raked = rake_cycle(pool)
    print("  demographic-matched assembly (option B):", flush=True)
    finalize(year, demo_assemble(stock, raked))


def gen_2030(aug, stock):
    """2030 path: forecast diaries are already raked (structural-break) but carry no demographics.
    Join 2022 demographics via occID, then demographic-match-assemble onto the frame (option B)."""
    print(f"\n{'='*64}\n  CYCLE 2030\n{'='*64}", flush=True)
    d30 = pd.read_csv(D2030, usecols=lambda c: c in ({"occID", "DDAY_STRATA"} | set(ACT) | set(HOM)),
                      low_memory=False)
    print(f"  2030 diaries: {len(d30):,} rows (pre-raked structural-break forecast)", flush=True)
    demo = (aug[(aug["CYCLE_YEAR"] == 2022) & (aug["IS_SYNTHETIC"] == 0)][["occID"] + KEYS]
            .drop_duplicates("occID"))
    d30 = d30.merge(demo, on="occID", how="left")
    miss = int(d30[KEYS[0]].isna().sum())
    print(f"  demo join via occID: {len(demo):,} 2022 respondents; {miss:,} unmatched 2030 rows", flush=True)
    print("  demographic-matched assembly (option B):", flush=True)
    finalize(2030, demo_assemble(stock, d30))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", choices=["2005", "2010", "2015", "2022", "2030", "all"], default="all")
    arg = ap.parse_args().year
    years = (CYCLES + [2022, 2030]) if arg == "all" else [int(arg)]
    print(f"Loading augmented_diaries.csv (cycles) ...", flush=True)
    aug = pd.read_csv(AUGD, usecols=lambda c: c in ({"occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"} | set(KEYS) | set(HOM) | set(ACT)),
                      low_memory=False)
    print(f"  {len(aug):,} rows; cycles {sorted(aug.CYCLE_YEAR.unique())}", flush=True)
    print(f"Loading frozen 2022 stock frame ...", flush=True)
    stock = pd.read_csv(STOCK, usecols=lambda c: c in ({"HH_ID", "DDAY_STRATA"} | set(KEYS) | set(STAT) | set(ACT) | set(HOM)),
                        low_memory=False)
    print(f"  {len(stock):,} rows, {stock.HH_ID.nunique():,} HH", flush=True)
    for y in years:
        if y == 2030:
            gen_2030(aug, stock)
        else:
            gen_cycle(y, aug, stock)
    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
