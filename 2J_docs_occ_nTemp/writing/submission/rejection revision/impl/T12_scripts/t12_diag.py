"""t12_diag.py -- T12 WP1 stage A diagnostic: where does 70% (2022) vs 78% (2030) come from.

Task doc: 2026-09-15_T12_wp1_stageA_diagnostic.md
Spec:     2026-09-15_WP1_step2_retargeting_spec.md sections 1, 4 (and 5, for the collector).

Standalone script -- does NOT import 07_aug_to_bem.py (it pulls in activity_loads, which this
diagnostic does not need). Instead it copies the specific lines needed for occupancy-only
reconstruction and cites the source file:line for each copy below. No pipeline script is
imported, edited, or run.

Inputs (read-only), expected under WORKDIR/input/:
  - 21CEN22GSS_aug_Full_Aggregated_excl.csv   (the 2022 stock; "stock")
  - augmented_diaries.csv                     (Step-4 diary pool; "aug")
  - 2030_synthetic_diaries_joint_raked.csv    (the 2030 pool; "pool2030")

Output: WORKDIR/T12_out/t12_diagnostic.csv, columns:
  measure, day_type, group, weighting, value_pct, n
plus stdout (captured by the slurm log) with T01 cross-checks and stage timings.

Run: /speed-scratch/o_iseri/envs/step4/bin/python t12_diag.py
"""
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

WORKDIR = Path("/speed-scratch/o_iseri/2J_revision/T12")
IN_DIR = WORKDIR / "input"
OUT_DIR = WORKDIR / "T12_out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STOCK_PATH = IN_DIR / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
AUG_PATH = IN_DIR / "augmented_diaries.csv"
POOL2030_PATH = IN_DIR / "2030_synthetic_diaries_joint_raked.csv"

OUT_CSV = OUT_DIR / "t12_diagnostic.csv"

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
PRE_COVID_CYCLES = [2005, 2010, 2015]
CYCLES_ALL = [2005, 2010, 2015, 2022]

t0 = time.time()


def log(msg):
    print(f"[{time.time()-t0:7.1f}s] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Output rows accumulate here and are flushed after every measure so a
# partial run still leaves something readable (long job on Speed).
# ---------------------------------------------------------------------------
rows = []


def add(measure, day_type, group, weighting, value_pct, n):
    rows.append(dict(measure=measure, day_type=day_type, group=group,
                      weighting=weighting, value_pct=round(float(value_pct), 3), n=int(n)))


def flush():
    pd.DataFrame(rows, columns=["measure", "day_type", "group", "weighting", "value_pct", "n"]) \
        .to_csv(OUT_CSV, index=False)
    log(f"flushed {len(rows)} rows -> {OUT_CSV}")


def day_type_of(dday_strata):
    # task doc convention: weekday = DDAY_STRATA==1, weekend = 2 or 3.
    return np.where(dday_strata == 1, "weekday",
                     np.where(np.isin(dday_strata, [2, 3]), "weekend", "other"))


def wmean(values, weights=None):
    if weights is None:
        return float(np.mean(values))
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    return float(np.sum(values * weights) / np.sum(weights))


# ===========================================================================
# M1 -- stock person-level hom30 mean (48 slots): unweighted and WGHT_PER-
# weighted; overall and by CYCLE_YEAR x IS_SYNTHETIC with person counts.
# ===========================================================================
def measure_M1():
    log("M1: loading stock (usecols only) ...")
    # DTYPE, BEDRM added 2026-09-15 (manager): job 1328275 failed in M5 with KeyError, M1 had not loaded them
    usecols = ["HH_ID", "DDAY_STRATA", "CYCLE_YEAR", "IS_SYNTHETIC", "WGHT_PER", "DTYPE", "BEDRM"] + HOM
    df = pd.read_csv(STOCK_PATH, usecols=usecols, low_memory=False)
    log(f"M1: stock loaded, {len(df):,} persons")
    df["day_type"] = day_type_of(df["DDAY_STRATA"].values)
    df["row_home_pct"] = df[HOM].values.mean(axis=1) * 100.0

    for dt in ("weekday", "weekend"):
        sub = df[df.day_type == dt]
        add("M1", dt, "overall", "unweighted", sub.row_home_pct.mean(), len(sub))
        add("M1", dt, "overall", "weighted", wmean(sub.row_home_pct, sub.WGHT_PER), len(sub))
        for (cy, syn), g in sub.groupby(["CYCLE_YEAR", "IS_SYNTHETIC"]):
            grp = f"{int(cy)}_synth{int(syn)}"
            add("M1", dt, grp, "unweighted", g.row_home_pct.mean(), len(g))
            add("M1", dt, grp, "weighted", wmean(g.row_home_pct, g.WGHT_PER), len(g))
    flush()
    return df  # reused by M5/M6/M7/M8


# ===========================================================================
# M2 -- augmented_diaries.csv, CYCLE_YEAR==2022 & IS_SYNTHETIC==0: unweighted
# and weighted (WGHT_PER exists in this file -- confirmed via header check).
# Expected unweighted weekday 76.93 (06_forecast_rake.py Step 1 logic,
# compute_observed_marginals(), 06_forecast_rake.py:100-123).
# ===========================================================================
def measure_M2():
    log("M2: loading augmented_diaries.csv 2022 real respondents (usecols only) ...")
    usecols = ["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC", "WGHT_PER"] + HOM
    df = pd.read_csv(AUG_PATH, usecols=usecols, low_memory=False)
    obs = df[(df.CYCLE_YEAR == 2022) & (df.IS_SYNTHETIC == 0)].copy()
    log(f"M2: 2022 IS_SYNTHETIC==0 rows: {len(obs):,}")
    obs["day_type"] = day_type_of(obs["DDAY_STRATA"].values)
    obs["row_home_pct"] = obs[HOM].values.mean(axis=1) * 100.0
    for dt in ("weekday", "weekend"):
        sub = obs[obs.day_type == dt]
        add("M2", dt, "2022_synth0", "unweighted", sub.row_home_pct.mean(), len(sub))
        add("M2", dt, "2022_synth0", "weighted (WGHT_PER)", wmean(sub.row_home_pct, sub.WGHT_PER), len(sub))
    log(f"M2 check: unweighted weekday = {obs[obs.day_type=='weekday'].row_home_pct.mean():.3f} "
        f"(expected 76.93)")
    flush()
    return df  # reused by M4 (needs CYCLE_YEAR 2005/2010/2015 too)


# ===========================================================================
# M3 -- joint-raked 2030 pool person-level mean by stratum.
# Expected weekday 78.44. No weight column in this file (confirmed via
# header check: occID, CYCLE_YEAR, DDAY_STRATA, act30_*, hom30_* only).
# ===========================================================================
def measure_M3():
    log("M3: loading 2030 joint-raked pool (usecols only) ...")
    usecols = ["DDAY_STRATA"] + HOM
    df = pd.read_csv(POOL2030_PATH, usecols=usecols, low_memory=False)
    log(f"M3: pool rows: {len(df):,}")
    df["day_type"] = day_type_of(df["DDAY_STRATA"].values)
    df["row_home_pct"] = df[HOM].values.mean(axis=1) * 100.0
    for dt in ("weekday", "weekend"):
        sub = df[df.day_type == dt]
        add("M3", dt, "pool2030", "unweighted (no weight col)", sub.row_home_pct.mean(), len(sub))
    log(f"M3 check: unweighted weekday = {df[df.day_type=='weekday'].row_home_pct.mean():.3f} "
        f"(expected 78.44)")
    flush()
    return df


# ===========================================================================
# M4 -- mean over weekday slots of 8 * pre_slope, and clamped target minus
# obs_2022 mean. Copies project_to_2030() (06_forecast_rake.py:138-165),
# which itself consumes obs_rates from compute_observed_marginals()
# (06_forecast_rake.py:100-123, "Step 1"). polyfit on 2005/2010/2015 real
# respondents (IS_SYNTHETIC==0) per (DDAY_STRATA x slot), same as the
# pipeline. Expected weekday delta ~= +1.51 pp.
# ===========================================================================
def measure_M4(aug_full):
    log("M4: computing obs_rates + pre_slope (06_forecast_rake.py:100-165 logic) ...")
    obs = aug_full[aug_full.IS_SYNTHETIC == 0]
    obs_rates = {}
    for yr in CYCLES_ALL:
        for s in (1, 2, 3):
            sub = obs[(obs.CYCLE_YEAR == yr) & (obs.DDAY_STRATA == s)]
            obs_rates[(yr, s)] = sub[HOM].values.astype(float).mean(axis=0) if len(sub) else np.zeros(48)

    pre_years = np.array(PRE_COVID_CYCLES, dtype=float)
    strata_label = {1: "weekday", 2: "weekend_sat", 3: "weekend_sun"}
    for s in (1, 2, 3):
        pre_matrix = np.stack([obs_rates[(yr, s)] for yr in PRE_COVID_CYCLES], axis=0)  # (3,48)
        obs_2022 = obs_rates[(2022, s)]
        slopes = np.array([np.polyfit(pre_years, pre_matrix[:, t], 1)[0] for t in range(48)])
        target = np.clip(obs_2022 + 8.0 * slopes, 0.0, 1.0)
        dt = strata_label[s]
        n_rows = int(((obs.CYCLE_YEAR == 2022) & (obs.DDAY_STRATA == s)).sum())
        add("M4", dt, "8x_pre_slope_mean", "n/a", (8.0 * slopes).mean() * 100.0, n_rows)
        add("M4", dt, "target_minus_obs2022", "n/a", (target.mean() - obs_2022.mean()) * 100.0, n_rows)

    # weekend pooled (Sat+Sun rows treated as one group) -- extension beyond the
    # pipeline's per-stratum WD/Sat/Sun split, done only for this diagnostic's
    # weekday/weekend reporting convention (see task doc header); NOT a change
    # to 06_forecast_rake.py itself.
    pre_matrix_we = np.stack(
        [obs[(obs.CYCLE_YEAR == yr) & (obs.DDAY_STRATA.isin([2, 3]))][HOM].values.astype(float).mean(axis=0)
         for yr in PRE_COVID_CYCLES], axis=0)
    obs_2022_we = obs[(obs.CYCLE_YEAR == 2022) & (obs.DDAY_STRATA.isin([2, 3]))][HOM].values.astype(float).mean(axis=0)
    slopes_we = np.array([np.polyfit(pre_years, pre_matrix_we[:, t], 1)[0] for t in range(48)])
    target_we = np.clip(obs_2022_we + 8.0 * slopes_we, 0.0, 1.0)
    n_we = int(((obs.CYCLE_YEAR == 2022) & (obs.DDAY_STRATA.isin([2, 3]))).sum())
    add("M4", "weekend", "8x_pre_slope_mean_pooled", "n/a", (8.0 * slopes_we).mean() * 100.0, n_we)
    add("M4", "weekend", "target_minus_obs2022_pooled", "n/a", (target_we.mean() - obs_2022_we.mean()) * 100.0, n_we)

    log(f"M4 check: weekday target_minus_obs2022 = "
        f"{[r['value_pct'] for r in rows if r['measure']=='M4' and r['day_type']=='weekday' and r['group']=='target_minus_obs2022'][0]:.3f} "
        f"(expected ~+1.51)")
    flush()


# ===========================================================================
# Occupancy-only reconstruction of 07_aug_to_bem.py, copied (not imported --
# avoids the activity_loads dependency, which this diagnostic does not need).
# ===========================================================================

def dtype_label(code, bedrm):
    # copied verbatim from 07_aug_to_bem.py:36-41
    if int(code) == 2:
        try:
            b = int(float(bedrm))
        except (ValueError, TypeError):
            b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(int(code), str(int(code)))


def complete_day_types_occ(df, seed=42):
    # copied from 07_aug_to_bem.py:148-180, restricted to HOM columns only
    # (the original also carries ACT_COLS through the donor-draw for the
    # metabolic/equipment/lighting side; this diagnostic needs occupancy
    # only, so ACT columns are not loaded and not touched -- the random
    # draw indices (rng.integers over the same pool sizes) are identical
    # either way, since which columns get copied does not affect which
    # rows are drawn).
    rng = np.random.default_rng(seed)
    hh_strata = df.groupby("HH_ID")["DDAY_STRATA"].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])
    wd_pool = df[df["DDAY_STRATA"] == 1]
    we_pool = df[df["DDAY_STRATA"].isin([2, 3])]
    extra = []
    if wd_only:
        sub = df[df["HH_ID"].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[HOM] = we_pool.iloc[pick][HOM].values
        sub["DDAY_STRATA"] = 2
        extra.append(sub)
    if we_only:
        sub = df[df["HH_ID"].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[HOM] = wd_pool.iloc[pick][HOM].values
        sub["DDAY_STRATA"] = 1
        extra.append(sub)
    return pd.concat([df] + extra, ignore_index=True) if extra else df


def convert_occ_only(df):
    # copied from 07_aug_to_bem.py:94-97,103,109 (occupancy part only,
    # metabolic/equipment/lighting omitted -- this diagnostic does not need
    # them and they require activity_loads, which is deliberately not
    # imported per the task doc).
    df = df.rename(columns={"HH_ID": "SIM_HH_ID"}).copy()
    df["Day_Type"] = df["DDAY_STRATA"].map({1: "Weekday", 2: "Weekend", 3: "Weekend"})
    keys = ["SIM_HH_ID", "Day_Type"]
    occ48 = df.groupby(keys, sort=True)[HOM].mean()                       # 07_aug_to_bem.py:97
    stat = df.groupby(keys, sort=True)[["DTYPE", "BEDRM"]].first().reindex(occ48.index)
    G = len(occ48.index)
    occ24 = occ48.values.reshape(G, 24, 2).mean(axis=2)                   # 07_aug_to_bem.py:103
    occ24 = np.roll(occ24, 4, axis=1)                                     # 07_aug_to_bem.py:109
    dtype_lbl = [dtype_label(c, b) for c, b in zip(stat["DTYPE"].values, stat["BEDRM"].values)]
    out = pd.DataFrame({
        "SIM_HH_ID": occ48.index.get_level_values("SIM_HH_ID").repeat(24),
        "Day_Type": occ48.index.get_level_values("Day_Type").repeat(24),
        "Occupancy_Schedule": occ24.reshape(-1),
        "DTYPE": np.repeat(dtype_lbl, 24),
    })
    return out


def report_household_level(measure_name, occ_df, t01_expected=None):
    for dt_label, dt_key in (("weekday", "Weekday"), ("weekend", "Weekend")):
        sub = occ_df[occ_df.Day_Type == dt_key]
        val = sub.Occupancy_Schedule.mean() * 100.0
        add(measure_name, dt_label, "national", "unweighted", val, sub.SIM_HH_ID.nunique())
        if t01_expected is not None and dt_label == "weekday":
            delta = val - t01_expected
            log(f"{measure_name} T01 check: weekday national = {val:.3f}, "
                f"expected {t01_expected:.3f} (+/-0.01), delta = {delta:+.3f}")
        for arch, g in sub.groupby("DTYPE"):
            val_a = g.Occupancy_Schedule.mean() * 100.0
            add(measure_name, dt_label, arch, "unweighted", val_a, g.SIM_HH_ID.nunique())


# ===========================================================================
# M5 -- household-level hourly schedule means from the stock as is.
# Must reproduce T01 weekday national 70.239 (+/-0.01).
# ===========================================================================
def measure_M5(stock_full):
    log("M5: complete_day_types_occ + convert_occ_only on stock as-is ...")
    df = stock_full[["HH_ID", "DDAY_STRATA", "DTYPE", "BEDRM"] + HOM].copy()
    df = complete_day_types_occ(df, seed=42)
    occ = convert_occ_only(df)
    report_household_level("M5", occ, t01_expected=70.239)
    flush()


# ===========================================================================
# M6 -- current draw with the 2030 pool: assemble_2030 logic
# (07_aug_to_bem.py:182-193, seed 42) -> same as M5.
# Must reproduce T01 weekday national 78.526 (+/-0.01).
# ===========================================================================
def assemble_from_pool(stock_full, pool_df, seed=42):
    # copied from 07_aug_to_bem.py:182-193, HOM columns only (ACT columns not
    # loaded for this diagnostic; the draw indices are unaffected by that,
    # see complete_day_types_occ comment above).
    rng = np.random.default_rng(seed)
    stock_dday = stock_full["DDAY_STRATA"].values
    out = stock_full[["HH_ID", "DDAY_STRATA", "DTYPE", "BEDRM"] + HOM].copy()
    for k in (1, 2, 3):
        smask = (stock_dday == k)
        pool = pool_df[pool_df["DDAY_STRATA"] == k]
        pick = rng.integers(0, len(pool), size=int(smask.sum()))
        out.loc[smask, HOM] = pool.iloc[pick][HOM].values
    return out


def measure_M6(stock_full, pool2030_df):
    log("M6: assemble_2030 logic with the joint-raked 2030 pool ...")
    df = assemble_from_pool(stock_full, pool2030_df, seed=42)
    df = complete_day_types_occ(df, seed=42)
    occ = convert_occ_only(df)
    report_household_level("M6", occ, t01_expected=78.526)
    flush()


# ===========================================================================
# M7 -- null test: assemble_2030 logic but pool = augmented_diaries.csv
# 2022 real respondents (zero-change forecast) -> same as M5.
# ===========================================================================
def measure_M7(stock_full, aug_full):
    log("M7: assemble_2030 logic with 2022 real-respondent pool (null test) ...")
    pool = aug_full[(aug_full.CYCLE_YEAR == 2022) & (aug_full.IS_SYNTHETIC == 0)][["DDAY_STRATA"] + HOM].copy()
    df = assemble_from_pool(stock_full, pool, seed=42)
    df = complete_day_types_occ(df, seed=42)
    occ = convert_occ_only(df)
    report_household_level("M7", occ)
    flush()


# ===========================================================================
# M8 -- composition check: M5 recomputed after per-person random re-draw
# from the stock's own weekday/weekend diaries (pool = stock, seed 42).
# ===========================================================================
def measure_M8(stock_full):
    log("M8: assemble_2030 logic with pool = stock itself (composition-only test) ...")
    pool = stock_full[["DDAY_STRATA"] + HOM].copy()
    df = assemble_from_pool(stock_full, pool, seed=42)
    df = complete_day_types_occ(df, seed=42)
    occ = convert_occ_only(df)
    report_household_level("M8", occ)
    flush()


def main():
    for p in (STOCK_PATH, AUG_PATH, POOL2030_PATH):
        if not p.exists():
            raise FileNotFoundError(f"Missing input: {p}")
        log(f"input OK: {p.name} ({p.stat().st_size:,} bytes)")

    stock_full = measure_M1()
    aug_full = measure_M2()
    pool2030_df = measure_M3()
    measure_M4(aug_full)
    measure_M5(stock_full)
    measure_M6(stock_full, pool2030_df)
    measure_M7(stock_full, aug_full)
    measure_M8(stock_full)

    flush()
    log("ALL MEASURES DONE.")


if __name__ == "__main__":
    main()
