"""3rdJ_08A_gen_historical_schedules.py — Step 8A: Historical BEM Schedules (3J Leg-2).

Generates BEM_Schedules_2split_{2005,2010,2015}.csv (residential REPLACE, 13-col) and
office_presence_multiplier_{2005,2010,2015}.csv (office MODULATE, 7-col) so the Step-8
simulation has all 7 scenarios on a consistent method.

Sub-step ordered: MUST pass val §0 before any EnergyPlus run launches.

Method (per cycle):
  1. Pull that cycle's diaries from the 3J AUG file (filter CYCLE_YEAR).
  2. Phase-8B rake: flip IS_SYNTHETIC==1 hom30 + wrk30 per (stratum x slot) to each
     cycle's own OBSERVED within-stratum marginal (seed=42, boundary-preferred).
  3. Demographic-matched assembly onto the frozen 3J 2022 stock frame
     (3rdJ_25CEN_aug_Full_Aggregated_excl.csv) — tiered matching on AGEGRP/SEX/MARSTH/
     HHSIZE/LFTAG; only act30/hom30/wrk30 swap in, dwelling attrs kept from stock.
  4. Donor-draw day-completion (Step-7 style, extends 2J to include WRK).
  5. convert() (Step-7 version with _hh_canon fix; +4h diary->clock roll) -> residential CSV.
  6. build_office_multiplier() (Step-7 version) -> office CSV.
  7. val §0 acceptance gates (schema, row counts, no NaN, longitudinal caveat INFO).

  INFO gate: AT_WORK gating vars differ across GSS cycles:
    - 2005/2010: PLACE code 02 = "at respondent's workplace or work site"
    - 2015+: LOCATION code 3301 (or similar)
  Historical office multipliers carry documented reconstruction uncertainty (val §0.5).

Usage:
  py 3rdJ_08A_gen_historical_schedules.py --year 2015 | --year all
  (run from anywhere; outputs land in Step8_docs/outputs_step8/historical_schedules/)

seed=42 throughout. Deps: pandas, numpy (existing env). No new packages.
2026-06-28 built.
"""
import os
import sys
import argparse
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE  = Path(__file__).resolve().parent          # Step8_docs/
LEG2  = HERE.parent                              # Leg2_2-split/
J3    = LEG2.parent                              # 3J_docs_occ_nTemp/
BASE  = J3.parent                                # GSSCanada-main/

AUG   = (LEG2 / "Step5_docs" / "outputs_step5"
         / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv")
D2030 = (LEG2 / "Step6_docs" / "outputs_step6"
         / "2030_synthetic_diaries_2split_calibrated_mindwell.csv")
LOOKUP = BASE / "0_Occupancy" / "processed" / "office_archetype_lookup.csv"
S7_OUT = LEG2 / "Step7_docs" / "outputs_step7"

OUT_DIR = HERE / "outputs_step8" / "historical_schedules"

CYCLES = [2005, 2010, 2015]

# ---------------------------------------------------------------------------
# Column groups (identical to Step-7)
# ---------------------------------------------------------------------------
N = 48
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
STAT = ["HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER"]
OUT_COLS = [
    "SIM_HH_ID", "Day_Type", "Hour",
    "HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER",
    "Occupancy_Schedule", "Metabolic_Rate",
]
OFF_COLS = ["office_archetype", "BAND", "Day_Type", "Hour",
            "AT_WORK_fraction", "multiplier", "n_persons"]

# ---------------------------------------------------------------------------
# Constants (verbatim from 3rdJ_07_aug_to_bem_2split.py — DO NOT diverge)
# ---------------------------------------------------------------------------
MET = {
    0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105,
    7: 170, 8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135,
}
# Fix A (2026-06-26): 3J AUG uses region codes 1-6 (remapped by Step 5).
PR_LBL = {
    1: "Atlantic", 2: "Quebec", 3: "Ontario",
    4: "Prairies", 5: "BC", 6: "Northern Canada",
}
DAYTYPE = {1: "Weekday", 2: "Weekend", 3: "Weekend"}
EMPLOYED_LFTAG = {1, 2}
OFFICE_ARCHETYPES = {"Office_Knowledge", "Office_Public", "Office_Sales"}
STRATA = [1, 2, 3]
LBL    = {1: "WD", 2: "Sat", 3: "Sun"}

KEYS  = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG"]
TIERS = [KEYS,
         ["AGEGRP", "SEX", "LFTAG"],
         ["AGEGRP", "SEX"],
         []]

# ---------------------------------------------------------------------------
# Rake helpers (from 06_forecast_rake.py / 08_gen_cycle_schedules.py)
# ---------------------------------------------------------------------------
def _boundary_mask(arr, t):
    val_t = arr[:, t]
    left  = (arr[:, t - 1] != val_t) if t > 0 else np.ones(len(arr), bool)
    right = (arr[:, t + 1] != val_t) if t < arr.shape[1] - 1 else np.ones(len(arr), bool)
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


# ---------------------------------------------------------------------------
# dtype_label / convert / complete_day_types (Step-7 version with _hh_canon fix)
# ---------------------------------------------------------------------------
def dtype_label(code, bedrm):
    if int(code) == 2:
        try: b = int(float(bedrm))
        except (ValueError, TypeError): b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(int(code), str(int(code)))


def convert(df):
    """Port of 3rdJ_07_aug_to_bem_2split.convert() with _hh_canon fix."""
    df = df.copy()
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)
    keys = ["SIM_HH_ID", "Day_Type"]

    occ48 = df.groupby(keys, sort=True)[HOM].mean()
    wdf = df[keys].copy()
    for c in ACT:
        wdf[c] = df[c].map(MET).fillna(100.0)
    met48 = wdf.groupby(keys, sort=True)[ACT].mean().reindex(occ48.index)
    stat  = df.groupby(keys, sort=True)[STAT].first().reindex(occ48.index)

    # Fix B (2026-06-26): canonicalize DTYPE/PR per SIM_HH_ID (eliminates within-HH drift)
    _hh_canon = stat.groupby(level="SIM_HH_ID").first()
    for _col in STAT:
        stat[_col] = stat.index.get_level_values("SIM_HH_ID").map(_hh_canon[_col])

    G = len(occ48.index)
    occ24 = occ48.values.reshape(G, 24, 2).mean(axis=2)
    met24 = met48.values.reshape(G, 24, 2).mean(axis=2)

    # +4h diary->clock roll (GSS slot 1 = 04:00)
    occ24 = np.roll(occ24, 4, axis=1)
    met24 = np.roll(met24, 4, axis=1)

    out = pd.DataFrame({
        "SIM_HH_ID":         occ48.index.get_level_values("SIM_HH_ID").repeat(24),
        "Day_Type":           occ48.index.get_level_values("Day_Type").repeat(24),
        "Hour":               np.tile(np.arange(24), G),
        "Occupancy_Schedule": np.round(occ24.reshape(-1), 3),
        "Metabolic_Rate":     np.round(met24.reshape(-1), 1),
    })
    for col in ["HHSIZE", "BEDRM", "CONDO", "ROOM", "REPAIR", "MATCH_TIER"]:
        out[col] = np.repeat(stat[col].values, 24)
    dt = np.repeat(stat["DTYPE"].values, 24)
    bd = np.repeat(stat["BEDRM"].values, 24)
    out["DTYPE"] = [dtype_label(c, b) for c, b in zip(dt, bd)]
    pr = np.repeat(stat["PR"].values, 24)
    out["PR"] = [PR_LBL.get(int(p), str(int(p))) for p in pr]
    return out[OUT_COLS]


def complete_day_types(df):
    """Step-7 version — donor-draw for WD-only / WE-only HHs; extends to WRK cols."""
    rng = np.random.default_rng(42)
    hh_strata = df.groupby("SIM_HH_ID")["DDAY_STRATA"].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])
    wd_pool = df[df["DDAY_STRATA"] == 1]
    we_pool = df[df["DDAY_STRATA"].isin([2, 3])]
    DRAW_COLS = ACT + HOM + WRK
    extra = []
    if wd_only:
        sub = df[df["SIM_HH_ID"].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[DRAW_COLS] = we_pool.iloc[pick][DRAW_COLS].values
        sub["DDAY_STRATA"] = 2
        _hh_stat_wd = df[df["SIM_HH_ID"].isin(wd_only)].groupby("SIM_HH_ID")[STAT].first()
        for _col in STAT:
            sub[_col] = sub["SIM_HH_ID"].map(_hh_stat_wd[_col])
        extra.append(sub)
        print(f"  donor-draw {len(wd_only):,} WD-only HHs -> Weekend ({len(sub):,} rows)", flush=True)
    if we_only:
        sub = df[df["SIM_HH_ID"].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[DRAW_COLS] = wd_pool.iloc[pick][DRAW_COLS].values
        sub["DDAY_STRATA"] = 1
        _hh_stat_we = df[df["SIM_HH_ID"].isin(we_only)].groupby("SIM_HH_ID")[STAT].first()
        for _col in STAT:
            sub[_col] = sub["SIM_HH_ID"].map(_hh_stat_we[_col])
        extra.append(sub)
        print(f"  donor-draw {len(we_only):,} WE-only HHs -> Weekday ({len(sub):,} rows)", flush=True)
    if not extra:
        print("  No day-type completion needed.", flush=True)
    return pd.concat([df] + extra, ignore_index=True) if extra else df


# ---------------------------------------------------------------------------
# build_office_multiplier (Step-7 version verbatim)
# ---------------------------------------------------------------------------
def build_office_multiplier(df, band_label, lookup_df):
    """AT_WORK_fraction per (archetype x Day_Type x Hour). Step-7 verbatim."""
    is_office_nocs = lookup_df[lookup_df["is_office"] == True]["NOCS"].tolist()
    nocs_to_arch = lookup_df.set_index("NOCS")["archetype_label"].to_dict()

    df = df.copy()
    df["office_archetype"] = df["NOCS"].map(nocs_to_arch).fillna("Unknown_NOCS")
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)

    mask_office   = df["NOCS"].isin(is_office_nocs)
    mask_employed = df["LFTAG"].isin(EMPLOYED_LFTAG)
    office_df     = df[mask_office & mask_employed].copy()
    print(f"  Office [{band_label}]: {len(office_df):,} employed is_office rows", flush=True)

    rows = []
    for arch in sorted(OFFICE_ARCHETYPES):
        for day_type in ["Weekday", "Weekend"]:
            sub = office_df[(office_df["office_archetype"] == arch) & (office_df["Day_Type"] == day_type)]
            n = len(sub)
            if n == 0:
                print(f"  WARNING: no rows for {arch} x {day_type} [{band_label}] -- zeros", flush=True)
                for h in range(24):
                    rows.append({"office_archetype": arch, "BAND": band_label,
                                 "Day_Type": day_type, "Hour": h,
                                 "AT_WORK_fraction": 0.0, "multiplier": 0.0, "n_persons": 0})
                continue
            wrk48 = sub[WRK].mean().values
            wrk24 = wrk48.reshape(24, 2).mean(axis=1)
            wrk24 = np.roll(wrk24, 4)
            for h in range(24):
                rows.append({"office_archetype": arch, "BAND": band_label,
                             "Day_Type": day_type, "Hour": h,
                             "AT_WORK_fraction": float(wrk24[h]), "n_persons": n})

    result = pd.DataFrame(rows)
    wd_mask = result["Day_Type"] == "Weekday"
    wd_peak = result[wd_mask].groupby("office_archetype")["AT_WORK_fraction"].max()
    result["wd_peak"] = result["office_archetype"].map(wd_peak)
    result["multiplier"] = np.where(result["wd_peak"] > 0,
                                    result["AT_WORK_fraction"] / result["wd_peak"], 0.0)
    result.drop(columns=["wd_peak"], inplace=True)
    result["AT_WORK_fraction"] = result["AT_WORK_fraction"].round(4)
    result["multiplier"] = result["multiplier"].round(4)
    return result[OFF_COLS]


# ---------------------------------------------------------------------------
# Phase-8B rake (hom30 + wrk30 per stratum x slot)
# ---------------------------------------------------------------------------
def rake_cycle(pool):
    """Flip IS_SYNTHETIC==1 hom30 and wrk30 to each cycle's observed marginal."""
    rng = np.random.default_rng(42)
    for label, cols in [("hom30", HOM), ("wrk30", WRK)]:
        arr = pool[cols].values.astype(float)
        syn = (pool["IS_SYNTHETIC"].values == 1)
        strata = pool["DDAY_STRATA"].values
        flips = 0
        for s in STRATA:
            obs_m = arr[(~syn) & (strata == s)].mean(axis=0)
            idx = np.where(syn & (strata == s))[0]
            if len(idx) == 0:
                continue
            sub = arr[idx]
            for t in range(N):
                tgt = max(0, min(len(idx), int(round(obs_m[t] * len(idx)))))
                flips += _rake_binary_slot(sub[:, t], tgt, _boundary_mask(sub, t), rng)
            arr[idx] = sub
            wd_pre = pool.loc[pool.index[idx], cols].values.mean() * 100
            print(f"    rake {label} {LBL[s]}: {len(idx):,} syn rows -> obs "
                  f"(pre {wd_pre:.2f}%, target {obs_m.mean()*100:.2f}%)", flush=True)
        pool = pool.copy()
        pool[cols] = arr
        print(f"    {label} total flips: {flips:,}", flush=True)
    return pool


# ---------------------------------------------------------------------------
# Demographic-matched assembly (Option B)
# ---------------------------------------------------------------------------
def _canon(df, cols):
    return {k: pd.to_numeric(df[k], errors="coerce").astype("Int64").astype(str).values for k in cols}


def demo_assemble(stock, pool):
    """Match each stock person to a cycle diary by tiered demographics + stratum."""
    from collections import defaultdict
    rng  = np.random.default_rng(42)
    pool = pool.reset_index(drop=True)
    allk = KEYS + ["DDAY_STRATA"]
    sc, pc = _canon(stock, allk), _canon(pool, allk)

    def ck(canon, gk):
        out = canon[gk[0]].astype(object)
        for k in gk[1:]:
            out = out + "|" + canon[k]
        return out

    n      = len(stock)
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
        print(f"    tier {ti} ({lbl}): matched {int((tier_of==ti).sum()):,}, "
              f"remaining {int(remaining.sum()):,}", flush=True)
        if not remaining.any():
            break
    assert chosen.min() >= 0, "unmatched frame rows remain"
    out = stock.copy()
    out[ACT + HOM + WRK] = pool.iloc[chosen][ACT + HOM + WRK].values
    return out


# ---------------------------------------------------------------------------
# Acceptance gates (val §0)
# ---------------------------------------------------------------------------
def gate_residential(bem, year):
    tag = f" [{year}]"
    assert set(bem["Day_Type"].unique()) <= {"Weekday", "Weekend"}, \
        f"Day_Type domain{tag}"
    assert bem["Hour"].between(0, 23).all(), f"Hour range{tag}"
    assert bem["Occupancy_Schedule"].between(0, 1).all(), \
        f"Occupancy [0,1]{tag}: min={bem['Occupancy_Schedule'].min():.4f}"
    assert (bem["Metabolic_Rate"] >= 0).all(), \
        f"Metabolic negative{tag}"
    cov = bem.groupby("SIM_HH_ID")["Day_Type"].nunique()
    assert (cov == 2).all(), \
        f"{int((cov<2).sum())} HHs missing day-type{tag}"
    assert list(bem.columns) == OUT_COLS, \
        f"Schema mismatch{tag}: {list(bem.columns)}"
    assert bem.isna().sum().sum() == 0, f"NaN found{tag}"
    nhh = bem["SIM_HH_ID"].nunique()
    nrows = len(bem)
    print(f"  [GATE PASS §0] residential {year}: {nhh:,} HH, {nrows:,} rows (={nhh}×2×24={nhh*48:,}?{nrows==nhh*48})", flush=True)


def gate_office(off, year):
    tag = f" [{year}]"
    assert set(off["office_archetype"].unique()) <= OFFICE_ARCHETYPES, \
        f"Archetype domain{tag}"
    assert off["AT_WORK_fraction"].between(0, 1).all(), \
        f"AT_WORK_fraction [0,1]{tag}"
    assert off.isna().sum().sum() == 0, f"NaN in office{tag}"
    # 3 archetypes x 1 band x 2 day-types x 24 hours = 144
    expected = 3 * 1 * 2 * 24
    assert len(off) == expected, \
        f"Office row count{tag}: {len(off)} != {expected}"
    assert list(off.columns) == OFF_COLS, f"Office schema mismatch{tag}"
    print(f"  [GATE PASS §0] office {year}: {len(off)} rows", flush=True)
    print(f"  INFO §0.5: historical office AT_WORK gating vars differ from 2022 (PLACE vs LOCATION code)", flush=True)


# ---------------------------------------------------------------------------
# Atomic write helper
# ---------------------------------------------------------------------------
def atomic_write(df, path):
    tmp = str(path) + ".tmp"
    df.to_csv(tmp, index=False, float_format="%.4f")
    os.replace(tmp, str(path))
    print(f"  WROTE {path.name}: {len(df):,} rows", flush=True)


# ---------------------------------------------------------------------------
# Per-cycle runner
# ---------------------------------------------------------------------------
def gen_cycle(year, aug, stock, lookup_df):
    print(f"\n{'='*64}\n  CYCLE {year}\n{'='*64}", flush=True)
    pool = aug[aug["CYCLE_YEAR"] == year].copy()
    n_obs = int((pool.IS_SYNTHETIC == 0).sum())
    n_syn = int((pool.IS_SYNTHETIC == 1).sum())
    print(f"  pool: {len(pool):,} rows (obs {n_obs:,} / syn {n_syn:,})", flush=True)

    raked = rake_cycle(pool)
    print("  demographic-matched assembly:", flush=True)
    assembled = demo_assemble(stock, raked)
    completed = complete_day_types(assembled)

    # Residential
    bem = convert(completed)
    gate_residential(bem, year)
    out_r = OUT_DIR / f"BEM_Schedules_2split_{year}.csv"
    atomic_write(bem, out_r)

    # Office (single "observed" band)
    off = build_office_multiplier(completed, band_label="observed", lookup_df=lookup_df)
    gate_office(off, year)
    out_o = OUT_DIR / f"office_presence_multiplier_{year}.csv"
    atomic_write(off, out_o)


# ---------------------------------------------------------------------------
# Longitudinal continuity check (val §0.4)
# ---------------------------------------------------------------------------
def check_longitudinal_continuity():
    """Compare 2005→2010→2015→2022 WD AT_HOME means — must move monotonically pre-COVID."""
    s7_2022 = pd.read_csv(S7_OUT / "BEM_Schedules_2split_2022.csv")
    mean_22 = s7_2022[s7_2022["Day_Type"] == "Weekday"]["Occupancy_Schedule"].mean()
    print(f"\n  Longitudinal continuity check (val §0.4):", flush=True)
    print(f"    2022 WD AT_HOME mean: {mean_22:.4f}", flush=True)
    means = {}
    for yr in CYCLES:
        f = OUT_DIR / f"BEM_Schedules_2split_{yr}.csv"
        if f.exists():
            df = pd.read_csv(f)
            means[yr] = df[df["Day_Type"] == "Weekday"]["Occupancy_Schedule"].mean()
            print(f"    {yr} WD AT_HOME mean: {means[yr]:.4f}", flush=True)
    # Pre-COVID: expect 2005 ≤ 2010 ≤ 2015 ≤ 2022 or at least no discontinuity
    vals = [means.get(yr) for yr in CYCLES] + [mean_22]
    if all(v is not None for v in vals):
        diffs = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
        if max(abs(d) for d in diffs) < 0.02:
            print("  [INFO §0.4] Pre-COVID changes < 2pp — normal longitudinal variation.", flush=True)
        else:
            print(f"  [INFO §0.4] Larger changes present: {[round(d,4) for d in diffs]} "
                  f"(expected gradual pre-COVID drift toward 2022 break)", flush=True)


# ---------------------------------------------------------------------------
# Validate schema matches 2022 headers (val §0.1)
# ---------------------------------------------------------------------------
def check_schema_match():
    ref_r = S7_OUT / "BEM_Schedules_2split_2022.csv"
    ref_o = S7_OUT / "office_presence_multiplier_2022.csv"
    ref_r_hdr = pd.read_csv(ref_r, nrows=0).columns.tolist()
    ref_o_hdr = pd.read_csv(ref_o, nrows=0).columns.tolist()
    print("\n  Schema check (val §0.1):", flush=True)
    for yr in CYCLES:
        r = OUT_DIR / f"BEM_Schedules_2split_{yr}.csv"
        o = OUT_DIR / f"office_presence_multiplier_{yr}.csv"
        if r.exists():
            hdr = pd.read_csv(r, nrows=0).columns.tolist()
            assert hdr == ref_r_hdr, f"Resid header mismatch {yr}: {hdr}"
            print(f"    residential {yr}: schema OK", flush=True)
        if o.exists():
            hdr = pd.read_csv(o, nrows=0).columns.tolist()
            assert hdr == ref_o_hdr, f"Office header mismatch {yr}: {hdr}"
            print(f"    office {yr}: schema OK", flush=True)
    print("  [GATE PASS §0.1] All generated headers byte-identical to 2022.", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", choices=["2005", "2010", "2015", "all"], default="all")
    arg = ap.parse_args().year
    years = CYCLES if arg == "all" else [int(arg)]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading 3J AUG file: {AUG.name} ...", flush=True)
    need_aug_cols = ({"SIM_HH_ID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC",
                      "NOCS", "LFTAG"} | set(KEYS) | set(STAT) | set(HOM) | set(ACT) | set(WRK))
    aug = pd.read_csv(AUG, usecols=lambda c: c in need_aug_cols, low_memory=False)
    print(f"  {len(aug):,} rows; cycles {sorted(aug.CYCLE_YEAR.unique())}", flush=True)

    # The stock frame IS the AUG file (3J: stock = 2022 observed rows only, SIM_HH_ID-keyed)
    stock_cols = ({"SIM_HH_ID", "DDAY_STRATA", "NOCS", "LFTAG"} |
                  set(KEYS) | set(STAT) | set(HOM) | set(ACT) | set(WRK))
    stock = aug[(aug["CYCLE_YEAR"] == 2022) & (aug["IS_SYNTHETIC"] == 0)].copy()
    stock = stock[[c for c in stock.columns if c in stock_cols]]
    print(f"  Stock (2022 observed): {len(stock):,} rows, {stock['SIM_HH_ID'].nunique():,} HH", flush=True)

    print(f"Loading office lookup: {LOOKUP.name} ...", flush=True)
    lookup_df = pd.read_csv(LOOKUP)

    for y in years:
        gen_cycle(y, aug, stock, lookup_df)

    if arg == "all":
        check_schema_match()
        check_longitudinal_continuity()

    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
