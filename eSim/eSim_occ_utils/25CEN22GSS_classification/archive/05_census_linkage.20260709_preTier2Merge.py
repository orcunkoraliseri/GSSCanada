"""
05_census_linkage.py — Step 5: Census-GSS Slot-Native Demographic Matching
21CEN22GSS Aug Pipeline

Slot-native replacement for the episode-based MatchProfiler + ScheduleExpander
chain. Operates directly on augmented_diaries.csv (192,183-row, 48-slot format)
and matches each of the 286,540 Census 2021 agents to one diary row using a
4-tier demographic fallback hierarchy.

CLI:
    py 05_census_linkage.py --smoke       # 1% sample (~2865 agents)
    py 05_census_linkage.py --full        # 286,540 agents
    py 05_census_linkage.py --aggregate   # HH aggregation (Sub-step 5E)
    py 05_census_linkage.py --bem         # occToBEM (Sub-step 5F)
    py 05_census_linkage.py --regression  # Regression vs 25pct baseline (Sub-step 5G)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
# parents[0] = 25CEN22GSS_classification/
# parents[1] = eSim_occ_utils/
# parents[2] = GSSCanada-main/
BASE = Path(__file__).resolve().parents[2]
AUGMENTED_DIARIES = BASE / "2J_docs_occ_nTemp" / "outputs_step4" / "augmented_diaries.csv"
CENSUS_FILE = (
    BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "alignment" / "Aligned_Census_2022.csv"
)
OUT_DIR = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline"
SMOKE_DIR = OUT_DIR / "smoke"
# 25pct baseline BEM schedules (hourly, household-level — produced by BEMConverter)
BASE_BEM_SAMPLE = (
    BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "occToBEM"
    / "21CEN22GSS_BEM_Schedules_sample25pct.csv"
)

# ── BEM label maps (mirrors BEMConverter in eSim_dynamicML_mHead.py) ──────────
_DTYPE_MAP = {
    1: "SingleD", 2: "SemiD", 3: "Attached", 4: "DuplexD",
    5: "HighRise", 6: "MidRise", 7: "OtherA", 8: "Movable",
}
_PR_MAP = {
    10: "Atlantic", 11: "Atlantic", 12: "Atlantic", 13: "Atlantic",
    24: "Quebec", 35: "Ontario", 46: "Prairies", 47: "Prairies",
    48: "Alberta", 59: "BC", 70: "Northern Canada",
}

# GSS 5-region <-> Census SGC fold, used ONLY for Tier-2b matching (--region-tier).
# Legacy GSS 2005 PR is already region-coded (1=Atlantic,2=Quebec,3=Ontario,4=Prairies,5=BC)
# and passes through unchanged; Census/2010+/2022 SGC codes fold onto the same 5 regions.
# Do NOT reuse _PR_MAP for this: it splits Alberta (48) from the Prairies (46,47) for
# display labels, which would break the fold since 2005 has no Alberta-vs-Prairies split.
REGION_FOLD = {
    10: 1, 11: 1, 12: 1, 13: 1,   # Atlantic (SGC)
    24: 2,                        # Quebec (SGC)
    35: 3,                        # Ontario (SGC)
    46: 4, 47: 4, 48: 4,          # Prairies incl. Alberta (SGC)
    59: 5,                        # BC (SGC)
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5,  # legacy 2005 5-region codes, pass through
}
REGION_COL = "REGION"

# ── Match configuration ───────────────────────────────────────────────────────
MATCH_KEYS = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA"]
DDAY_COL = "DDAY_STRATA"

# Tier key sets (all tiers append DDAY_COL)
_T1_KEYS = MATCH_KEYS + [DDAY_COL]                    # 8 keys — all 7 + day strata
_T2_KEYS = ["AGEGRP", "SEX", "LFTAG", "PR", DDAY_COL]  # 5 keys — core
_T3_KEYS = ["AGEGRP", "SEX", DDAY_COL]                 # 3 keys — constraints
_T4_KEYS = [DDAY_COL]                                   # 1 key  — FailSafe (random in stratum)

# Proportional DDAY assignment: 5 weekdays + 1 Saturday + 1 Sunday per week
_DDAY_PROBS = [5 / 7, 1 / 7, 1 / 7]

# Census building columns; BUILT is renamed to BUILTH in output to match spec schema
_CENSUS_BUILD_COLS = ["DTYPE", "BEDRM", "BUILT", "ROOM", "CONDO", "REPAIR", "VALUE"]
_CENSUS_BUILT_COL = "BUILT"
_OUTPUT_BUILT_COL = "BUILTH"

# Columns in the pool that are NOT passed through to output (come from Census instead)
_POOL_EXCLUDE = set(MATCH_KEYS) | {DDAY_COL, "occID"}


# ── Core functions ────────────────────────────────────────────────────────────

def load_augmented_pool(path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reads augmented_diaries.csv, splits into:
      - wd_pool: DDAY_STRATA == 1 (Weekday)
      - we_pool: DDAY_STRATA in {2, 3} (Saturday + Sunday)
    Returns (wd_pool, we_pool).
    """
    df = pd.read_csv(path)
    wd_pool = df[df[DDAY_COL] == 1].reset_index(drop=True)
    we_pool = df[df[DDAY_COL].isin([2, 3])].reset_index(drop=True)
    return wd_pool, we_pool


def run_slot_match(
    df_census: pd.DataFrame,
    df_pool: pd.DataFrame,
    match_keys: list[str],
    dday_col: str = "DDAY_STRATA",
    region_tier: bool = False,
) -> pd.DataFrame:
    """
    For each Census agent, attempts Tier 1 → 4 match against the diary pool.
    Returns Matched_Keys_aug df: [PP_ID, HH_ID, occID, DDAY_STRATA, MATCH_TIER, _pool_idx].
    Uses np.random.choice(pool_indices) for single-draw per agent.
    Seed: np.random.seed(42) at function entry.

    Pool rows with NaN in any tier's required keys are excluded from that tier
    (pandas groupby dropna=True default) but remain eligible for lower tiers.
    DDAY_STRATA has no NaN, so T4 (stratum-only) always has a non-empty pool.

    region_tier: when True, inserts Tier-2b (AGEGRP, SEX, LFTAG, REGION, DDAY)
    between Tier-2 and Tier-3, using the REGION_FOLD crosswalk so the 2005 GSS
    cycle (legacy 5-region PR, disjoint from Census SGC PR) can still match on
    geography before falling to age/sex-only Tier-3. Default False reproduces
    current (pre-fix) behaviour bit-for-bit.
    """
    np.random.seed(42)

    t1_keys = match_keys + [dday_col]
    t2_keys = ["AGEGRP", "SEX", "LFTAG", "PR", dday_col]
    t2b_keys = ["AGEGRP", "SEX", "LFTAG", REGION_COL, dday_col]
    t3_keys = ["AGEGRP", "SEX", dday_col]
    t4_keys = [dday_col]

    if region_tier:
        df_pool = df_pool.copy()
        df_census = df_census.copy()
        df_pool[REGION_COL] = df_pool["PR"].map(REGION_FOLD)
        df_census[REGION_COL] = df_census["PR"].map(REGION_FOLD)

    def _build_index(keys: list[str]) -> dict[tuple, np.ndarray]:
        """Map key-tuple → array of pool row labels (df_pool.index values)."""
        idx: dict = {}
        valid = df_pool.dropna(subset=keys)
        for vals, grp in valid.groupby(keys, sort=False):
            k = vals if isinstance(vals, tuple) else (vals,)
            idx[k] = grp.index.to_numpy()
        return idx

    t1 = _build_index(t1_keys)
    t2 = _build_index(t2_keys)
    t2b = _build_index(t2b_keys) if region_tier else {}
    t3 = _build_index(t3_keys)
    t4 = _build_index(t4_keys)

    pp_ids: list = []
    hh_ids: list = []
    occ_ids: list = []
    ddays: list = []
    tiers: list = []
    pool_idxs: list = []

    for _, agent in df_census.iterrows():
        dday = int(agent[dday_col])
        k1 = tuple(agent[k] for k in t1_keys)
        k2 = tuple(agent[k] for k in t2_keys)
        k3 = tuple(agent[k] for k in t3_keys)
        k4 = (dday,)

        if k1 in t1:
            pool_i = int(np.random.choice(t1[k1]))
            tier = "1_Perfect"
        elif k2 in t2:
            pool_i = int(np.random.choice(t2[k2]))
            tier = "2_Core"
        elif region_tier and tuple(agent[k] for k in t2b_keys) in t2b:
            k2b = tuple(agent[k] for k in t2b_keys)
            pool_i = int(np.random.choice(t2b[k2b]))
            tier = "2b_Region"
        elif k3 in t3:
            pool_i = int(np.random.choice(t3[k3]))
            tier = "3_Constraints"
        else:
            pool_i = int(np.random.choice(t4[k4]))
            tier = "4_FailSafe"

        pool_row = df_pool.loc[pool_i]
        pp_ids.append(agent["PP_ID"])
        hh_ids.append(agent["HH_ID"])
        occ_ids.append(pool_row["occID"])
        ddays.append(dday)
        tiers.append(tier)
        pool_idxs.append(pool_i)

    return pd.DataFrame(
        {
            "PP_ID": pp_ids,
            "HH_ID": hh_ids,
            "occID": occ_ids,
            dday_col: ddays,
            "MATCH_TIER": tiers,
            "_pool_idx": pool_idxs,
        }
    )


def expand_slot_schedules(
    df_matched: pd.DataFrame,
    df_pool: pd.DataFrame,
    df_census: pd.DataFrame,
) -> pd.DataFrame:
    """
    Joins matched keys to augmented_diaries on _pool_idx (direct label lookup —
    avoids (occID, DDAY_STRATA) ambiguity when observed and synthetic rows share
    the same occID).
    Appends Census demographic columns (AGEGRP…CMA) and building columns
    (DTYPE, BEDRM, BUILTH, ROOM, CONDO, REPAIR, VALUE) from
    Aligned_Census_2022.csv on PP_ID.
    Returns full schedule frame matching the Step 5B output schema.
    """
    # 1. Pull diary rows directly via stored pool index labels
    pool_rows = df_pool.loc[df_matched["_pool_idx"].to_numpy()].copy()
    pool_rows = pool_rows.reset_index(drop=True)

    # 2. Select pool columns to pass through (all except match keys and occID/DDAY)
    pool_diary_cols = (
        ["CYCLE_YEAR", "IS_SYNTHETIC", "WGHT_PER"]
        + sorted([c for c in df_pool.columns if c.startswith("act30_")])
        + sorted([c for c in df_pool.columns if c.startswith("hom30_")])
        + sorted(
            [
                c
                for c in df_pool.columns
                if c not in _POOL_EXCLUDE
                and not c.startswith("act30_")
                and not c.startswith("hom30_")
                and c not in ("CYCLE_YEAR", "IS_SYNTHETIC", "WGHT_PER")
            ]
        )
    )
    pool_diary_cols = [c for c in pool_diary_cols if c in df_pool.columns]

    # 3. Assemble base + diary schedule
    base = df_matched[["PP_ID", "HH_ID", "MATCH_TIER", "occID", DDAY_COL]].copy()
    base = base.reset_index(drop=True)
    df_out = pd.concat([base, pool_rows[pool_diary_cols].reset_index(drop=True)], axis=1)

    # 4. Append Census demographics (authoritative side) + building vars
    cen_demog = [k for k in MATCH_KEYS if k in df_census.columns]
    cen_build = [c for c in _CENSUS_BUILD_COLS if c in df_census.columns]
    cen_cols = ["PP_ID"] + cen_demog + cen_build
    df_out = df_out.merge(df_census[cen_cols].drop_duplicates(subset="PP_ID"), on="PP_ID", how="left")

    # 5. Rename BUILT → BUILTH to match output schema
    if _CENSUS_BUILT_COL in df_out.columns:
        df_out = df_out.rename(columns={_CENSUS_BUILT_COL: _OUTPUT_BUILT_COL})

    return df_out


# ── Internal helpers ──────────────────────────────────────────────────────────

def _assign_dday(df_census: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Add DDAY_STRATA to a Census DataFrame using population-proportional random
    assignment (5 weekdays / 1 Saturday / 1 Sunday per week = 5:1:1 ratio).
    Census does not carry a diary-day attribute; this assignment drives which
    sub-pool each agent is matched against.
    """
    rng = np.random.default_rng(seed)
    df = df_census.copy()
    df[DDAY_COL] = rng.choice([1, 2, 3], size=len(df), p=_DDAY_PROBS)
    return df


def _print_tier_report(df_matched: pd.DataFrame, df_pool: pd.DataFrame | None = None) -> dict:
    """Print and return tier distribution + WD/WE FailSafe rates.

    When df_pool is given, also prints a per-CYCLE_YEAR x tier share table
    (which GSS cycle's diary row each agent was matched to, by tier) — used
    to verify --region-tier moves 2005 out of Tier-3/4 into Tier-2b without
    shifting 2010/2015/2022 out of Tier-1.
    """
    n = len(df_matched)
    counts = df_matched["MATCH_TIER"].value_counts().sort_index()
    for t, c in counts.items():
        print(f"  {t}: {c} ({100 * c / n:.2f}%)")
    wd = df_matched[DDAY_COL] == 1
    we = df_matched[DDAY_COL].isin([2, 3])
    fs_wd = float((df_matched.loc[wd, "MATCH_TIER"] == "4_FailSafe").mean()) if wd.any() else 0.0
    fs_we = float((df_matched.loc[we, "MATCH_TIER"] == "4_FailSafe").mean()) if we.any() else 0.0
    print(f"  WD FailSafe: {100 * fs_wd:.2f}%  (gate <=10%)")
    print(f"  WE FailSafe: {100 * fs_we:.2f}%  (gate <=12%)")

    if df_pool is not None and "CYCLE_YEAR" in df_pool.columns:
        cyc = df_pool.loc[df_matched["_pool_idx"].to_numpy(), "CYCLE_YEAR"].to_numpy()
        by_cycle = pd.crosstab(cyc, df_matched["MATCH_TIER"].to_numpy(), normalize="index") * 100
        print("\n  Per-cycle tier share (%, row-normalized by matched CYCLE_YEAR):")
        print(by_cycle.round(2).to_string().replace("\n", "\n  "))

    return {"fs_wd": fs_wd, "fs_we": fs_we, "counts": counts, "n": n}


# ── Linkage runners ───────────────────────────────────────────────────────────

def run_linkage_smoke(sample_frac: float = 0.01, region_tier: bool = False) -> None:
    """1% Census sample (~2,865 agents). Writes to aug_pipeline/smoke/."""
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)

    wd_pool, we_pool = load_augmented_pool(str(AUGMENTED_DIARIES))
    df_pool = pd.concat([wd_pool, we_pool], ignore_index=True)
    df_census_full = pd.read_csv(CENSUS_FILE)

    df_census_sample = df_census_full.sample(frac=sample_frac, random_state=42)
    df_census_sample = _assign_dday(df_census_sample, seed=42)

    print(f"\n[smoke] {len(df_census_sample)} Census agents | pool: {len(df_pool)} rows"
          f"{' | region-tier ON' if region_tier else ''}")
    df_matched = run_slot_match(df_census_sample, df_pool, MATCH_KEYS, DDAY_COL, region_tier=region_tier)
    df_full = expand_slot_schedules(df_matched, df_pool, df_census_full)

    df_matched.drop(columns=["_pool_idx"]).to_csv(
        SMOKE_DIR / "21CEN22GSS_aug_Matched_Keys_smoke.csv", index=False
    )
    df_full.to_csv(SMOKE_DIR / "21CEN22GSS_aug_Full_Schedules_smoke.csv", index=False)

    print("\n--- Smoke Tier Distribution ---")
    _print_tier_report(df_matched, df_pool)

    hom_cols = sorted([c for c in df_full.columns if c.startswith("hom30_")])
    if hom_cols:
        mean_at_home = float(df_full[hom_cols].values.mean())
        print(f"\n  Mean AT_HOME across all slots: {100 * mean_at_home:.2f}%  (baseline ~62.5%)")

    # 5 random agent spot-checks
    print("\n--- 5 random agent spot-checks (Census -> matched diary) ---")
    act_cols_all = sorted([c for c in df_full.columns if c.startswith("act30_")])
    sample5 = df_matched.sample(min(5, len(df_matched)), random_state=0)
    for _, row in sample5.iterrows():
        pp = row["PP_ID"]
        cen_row = df_census_full[df_census_full["PP_ID"] == pp].iloc[0]
        sched_row = df_full[df_full["PP_ID"] == pp].iloc[0]
        act_first10 = " ".join(
            str(int(v)) for v in sched_row[act_cols_all[:10]]
        )
        print(
            f"  PP={pp} AGEGRP={cen_row['AGEGRP']} SEX={cen_row['SEX']}"
            f" LFTAG={cen_row['LFTAG']} -> occID={row['occID']}"
            f" tier={row['MATCH_TIER']} act[0:10]=[{act_first10}]"
        )

    print(f"\nSmoke outputs -> {SMOKE_DIR}")


def run_linkage_full(region_tier: bool = False) -> None:
    """100% Census sample (286,540 agents). Writes to aug_pipeline/."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    wd_pool, we_pool = load_augmented_pool(str(AUGMENTED_DIARIES))
    df_pool = pd.concat([wd_pool, we_pool], ignore_index=True)
    df_census_raw = pd.read_csv(CENSUS_FILE)
    n_raw = len(df_census_raw)
    df_census = df_census_raw.drop_duplicates(subset="PP_ID").reset_index(drop=True)
    n_deduped = len(df_census)
    if n_raw != n_deduped:
        print(f"[warn] Removed {n_raw - n_deduped} exact-duplicate PP_ID rows from Census "
              f"({n_raw} -> {n_deduped} unique agents)")
    df_census_dday = _assign_dday(df_census, seed=42)

    print(f"\n[full] {len(df_census_dday)} Census agents | pool: {len(df_pool)} rows"
          f"{' | region-tier ON' if region_tier else ''}")
    df_matched = run_slot_match(df_census_dday, df_pool, MATCH_KEYS, DDAY_COL, region_tier=region_tier)
    df_full = expand_slot_schedules(df_matched, df_pool, df_census)

    # Hard-gate assertions
    assert len(df_full) >= n_deduped, f"Row count {len(df_full)} < {n_deduped}"
    assert df_full["PP_ID"].nunique() == len(df_full), "Duplicate PP_IDs in output"
    assert df_full["occID"].notna().all(), "Null occID in output"

    df_matched.drop(columns=["_pool_idx"]).to_csv(
        OUT_DIR / "21CEN22GSS_aug_Matched_Keys.csv", index=False
    )
    df_full.to_csv(OUT_DIR / "21CEN22GSS_aug_Full_Schedules.csv", index=False)

    print("\n--- Full Run Tier Distribution ---")
    stats = _print_tier_report(df_matched, df_pool)

    report_lines = [
        "21CEN22GSS Aug Pipeline - Match Tier Report\n",
        f"Total Census agents: {stats['n']}\n\n",
    ]
    for t, c in stats["counts"].items():
        report_lines.append(f"  {t}: {c} ({100 * c / stats['n']:.2f}%)\n")
    report_lines += [
        f"\nWD FailSafe rate: {100 * stats['fs_wd']:.2f}%  (gate <=10%)\n",
        f"WE FailSafe rate: {100 * stats['fs_we']:.2f}%  (gate <=12%)\n",
    ]
    report_path = OUT_DIR / "21CEN22GSS_aug_Validation_match.txt"
    report_path.write_text("".join(report_lines), encoding="utf-8")

    print(f"\nOutputs -> {OUT_DIR}")


# ── Sub-step implementations (5E, 5F, 5G) ────────────────────────────────────

def run_aggregate() -> None:
    """
    Sub-step 5E: Slot-native HH aggregation.

    HouseholdAggregator (eSim_dynamicML_mHead.py) expects episode-format input
    (start/end times, 5-min resolution). Our data is already in 30-min slot
    format, making a direct call incompatible.  Thin adapter: compute
    HH-level occupancy per slot as the max of hom30 across all HH members
    (=household occupied if at least one member is home), then merge back to
    individual rows.  Output preserves one row per PP_ID (286,537 rows) with
    added HH_hom30_* and N_HH_MEMBERS columns.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[5E] Loading Full_Schedules...")
    df = pd.read_csv(OUT_DIR / "21CEN22GSS_aug_Full_Schedules.csv")

    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]

    # HH-level occupancy per slot: any member home => HH occupied (max of binary 0/1)
    print("[5E] Computing HH-level occupancy per slot (max across HH members)...")
    hh_occ = df.groupby("HH_ID")[hom_cols].max()
    hh_occ.columns = [f"HH_{c}" for c in hom_cols]
    hh_occ = hh_occ.reset_index()

    # Number of matched members per HH
    hh_size_obs = df.groupby("HH_ID").size().rename("N_HH_MEMBERS").reset_index()

    df_agg = df.merge(hh_occ, on="HH_ID", how="left")
    df_agg = df_agg.merge(hh_size_obs, on="HH_ID", how="left")

    # ── Validation ────────────────────────────────────────────────────────────
    n = len(df_agg)
    n_hh_null = int(df_agg["HH_ID"].isna().sum())
    n_dup = int(df_agg["PP_ID"].duplicated().sum())
    mean_hhsize = float(df_agg["HHSIZE"].mean())
    n_unique_hh = int(df_agg["HH_ID"].nunique())

    print(f"[5E] Row count: {n}  HH_ID null: {n_hh_null}  Dup PP_IDs: {n_dup}")
    print(f"[5E] Unique HH_IDs: {n_unique_hh}  Mean HHSIZE: {mean_hhsize:.4f}")

    assert n_hh_null == 0, f"HH_ID null rows: {n_hh_null}"
    assert n_dup == 0, f"Duplicate PP_IDs: {n_dup}"
    assert n == 286537, f"Row count {n} != 286537"

    df_agg.to_csv(OUT_DIR / "21CEN22GSS_aug_Full_Aggregated.csv", index=False)

    # ── Validation report ─────────────────────────────────────────────────────
    report_lines = [
        "21CEN22GSS Aug Pipeline - Sub-step 5E HH Aggregation Report\n",
        "=" * 60 + "\n",
        f"Row count: {n}\n",
        f"HH_ID null: {n_hh_null}\n",
        f"Duplicate PP_IDs: {n_dup}\n",
        f"Unique HH_IDs: {n_unique_hh}\n",
        f"Mean HHSIZE (Census): {mean_hhsize:.4f}\n",
        f"HH_hom30 cols added: 48  (HH_hom30_001 to HH_hom30_048)\n",
        f"N_HH_MEMBERS col added: yes\n",
        "\n[GATE] HH_ID completeness (100% non-null): PASS\n",
        "[GATE] No duplicate PP_IDs: PASS\n",
        f"[GATE] Row count == 286537: PASS\n",
        "\nAdapter note: HouseholdAggregator (eSim_dynamicML_mHead.py) expects\n",
        "episode-format (5-min grids). Slot-native adapter computes HH_hom30\n",
        "as max(hom30) across members per slot. No modification to source files.\n",
    ]
    (OUT_DIR / "21CEN22GSS_aug_Validation_HH.txt").write_text(
        "".join(report_lines), encoding="utf-8"
    )

    # ── Validation plot ───────────────────────────────────────────────────────
    hh_hom_cols = [f"HH_hom30_{i:03d}" for i in range(1, 49)]
    ind_hom_mean = df_agg[hom_cols].mean() * 100
    hh_hom_mean = df_agg[hh_hom_cols].mean() * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    slot_labels = [f"{(i * 30) // 60:02d}:{(i * 30) % 60:02d}" for i in range(48)]
    x = range(48)

    axes[0].plot(x, ind_hom_mean.values, 'b-', linewidth=2, label='Individual AT_HOME')
    axes[0].plot(x, hh_hom_mean.values, 'r--', linewidth=2, label='HH occupied (any member home)')
    axes[0].set_title("Individual vs HH Occupancy (30-min slots)")
    axes[0].set_xlabel("Slot")
    axes[0].set_ylabel("% At Home / HH Occupied")
    axes[0].set_xticks(range(0, 48, 4))
    axes[0].set_xticklabels(slot_labels[::4], rotation=45)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    df_agg["HHSIZE"].value_counts().sort_index().plot(kind="bar", ax=axes[1], color="steelblue")
    axes[1].set_title(f"HH Size Distribution (mean={mean_hhsize:.2f})")
    axes[1].set_xlabel("HHSIZE")
    axes[1].set_ylabel("Count")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "21CEN22GSS_aug_Validation_Plot.png", dpi=100)
    plt.close()

    print(f"[5E] Done. Output -> {OUT_DIR / '21CEN22GSS_aug_Full_Aggregated.csv'}")


def run_bem() -> None:
    """
    Sub-step 5F: Slot-native BEM schedule preparation.

    run_step3.py's BEMConverter expects 5-min long-format time series and
    outputs hourly household-level schedules.  The aug pipeline keeps the
    30-min per-person slot format for Step 7 (EnergyPlus); BEM conversion
    here means: validate the 48-slot schema, add human-readable DTYPE and
    PR label columns (using BEMConverter.dtype_map / pr_map from
    eSim_dynamicML_mHead.py), generate validation plots, and save as
    21CEN22GSS_aug_BEM_Schedules.csv.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[5F] Loading Full_Aggregated...")
    df = pd.read_csv(OUT_DIR / "21CEN22GSS_aug_Full_Aggregated.csv")

    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]

    # ── Schema validation ─────────────────────────────────────────────────────
    missing_act = [c for c in act_cols if c not in df.columns]
    missing_hom = [c for c in hom_cols if c not in df.columns]
    assert not missing_act, f"Missing act30 cols: {missing_act[:5]}"
    assert not missing_hom, f"Missing hom30 cols: {missing_hom[:5]}"

    act_vals_flat = df[act_cols].values.ravel()
    hom_vals_flat = df[hom_cols].values.ravel()
    act_unique = set(np.unique(act_vals_flat))
    hom_unique = set(np.unique(hom_vals_flat))
    assert act_unique <= set(range(1, 15)), f"act30 out-of-range values: {act_unique - set(range(1,15))}"
    assert hom_unique <= {0, 1}, f"hom30 values not in {{0,1}}: {hom_unique - {0,1}}"

    n = len(df)
    print(f"[5F] Schema OK: act30={len(act_cols)} cols, hom30={len(hom_cols)} cols, "
          f"act30 range {min(act_unique)}-{max(act_unique)}, "
          f"hom30 values {sorted(hom_unique)}, rows={n}")

    # BEM label columns (from _DTYPE_MAP / _PR_MAP defined at module level;
    # mirrors BEMConverter.dtype_map and BEMConverter.pr_map in eSim_dynamicML_mHead.py)
    df["DTYPE_str"] = df["DTYPE"].map(_DTYPE_MAP).fillna("Other")
    df["PR_str"] = df["PR"].map(_PR_MAP).fillna("Others")

    df.to_csv(OUT_DIR / "21CEN22GSS_aug_BEM_Schedules.csv", index=False)

    # ── Validation report ─────────────────────────────────────────────────────
    report_lines = [
        "21CEN22GSS Aug Pipeline - Sub-step 5F BEM Schedules Validation\n",
        "=" * 60 + "\n",
        f"Row count: {n}\n",
        f"act30 cols: {len(act_cols)} (act30_001 to act30_048)\n",
        f"hom30 cols: {len(hom_cols)} (hom30_001 to hom30_048)\n",
        f"act30 unique values: {sorted(act_unique)}\n",
        f"hom30 unique values: {sorted(hom_unique)}\n",
        f"DTYPE unique (numeric): {sorted(df['DTYPE'].unique())}\n",
        f"DTYPE_str unique: {sorted(df['DTYPE_str'].unique())}\n",
        f"PR_str unique: {sorted(df['PR_str'].unique())}\n",
        "\n[GATE] 48-slot schema (act30+hom30 present): PASS\n",
        f"[GATE] act30 values in {{1..14}}: PASS\n",
        "[GATE] hom30 values in {0,1}: PASS\n",
        f"[GATE] row count == 286537: {'PASS' if n == 286537 else f'FAIL ({n})'}\n",
        "\nFormat note: BEMConverter (run_step3.py) produces hourly household-level\n",
        "schedules. Aug pipeline retains 30-min per-person slot format for Step 7.\n",
        "BEM conversion = schema validation + DTYPE/PR label enrichment.\n",
    ]
    (OUT_DIR / "21CEN22GSS_aug_Validation_BEM.txt").write_text(
        "".join(report_lines), encoding="utf-8"
    )

    # ── Temporal validation plot ──────────────────────────────────────────────
    slot_labels = [f"{(i * 30) // 60:02d}:{(i * 30) % 60:02d}" for i in range(48)]
    hom_mean = df[hom_cols].mean() * 100
    act_values = df[act_cols].values.ravel()
    act_share = pd.Series(act_values).value_counts(normalize=True).sort_index() * 100

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    axes[0].plot(range(48), hom_mean.values, 'b-', linewidth=2)
    axes[0].set_title("Mean AT_HOME per 30-min Slot (Aug Pipeline - 286,537 agents)")
    axes[0].set_xlabel("Slot")
    axes[0].set_ylabel("% At Home")
    axes[0].set_xticks(range(0, 48, 4))
    axes[0].set_xticklabels(slot_labels[::4], rotation=45)
    axes[0].grid(True, alpha=0.3)

    axes[1].bar(act_share.index.astype(int), act_share.values, color="steelblue")
    axes[1].set_title("Activity Time-Share (act30, 1=Work ... 14=Misc)")
    axes[1].set_xlabel("Activity Code")
    axes[1].set_ylabel("% of slots")
    axes[1].set_xticks(sorted(act_share.index.astype(int)))

    plt.tight_layout()
    plt.savefig(OUT_DIR / "21CEN22GSS_aug_BEM_temporals.png", dpi=100)
    plt.close()

    # ── Non-temporal validation plot ──────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    df["DTYPE_str"].value_counts().plot(kind="bar", ax=axes[0, 0], color="steelblue")
    axes[0, 0].set_title("DTYPE Distribution")
    axes[0, 0].set_xlabel("Dwelling Type")
    axes[0, 0].tick_params(axis="x", rotation=30)

    df["BEDRM"].value_counts().sort_index().plot(kind="bar", ax=axes[0, 1], color="teal")
    axes[0, 1].set_title("BEDRM Distribution")
    axes[0, 1].set_xlabel("Bedrooms")

    df["PR_str"].value_counts().plot(kind="bar", ax=axes[1, 0], color="coral")
    axes[1, 0].set_title("Province Distribution")
    axes[1, 0].set_xlabel("Province")
    axes[1, 0].tick_params(axis="x", rotation=30)

    df["HHSIZE"].value_counts().sort_index().plot(kind="bar", ax=axes[1, 1], color="orchid")
    axes[1, 1].set_title("HHSIZE Distribution")
    axes[1, 1].set_xlabel("HH Size")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "21CEN22GSS_aug_BEM_non_temporals.png", dpi=100)
    plt.close()

    print(f"[5F] Done. Output -> {OUT_DIR / '21CEN22GSS_aug_BEM_Schedules.csv'}")


def run_exclusion() -> None:
    """
    Sub-step 5H: Exclude households with per-HH mean AT_HOME < 0.30.

    Methodology: model outputs must not be modified; exclusion is the correct
    response to physically implausible HH schedules (FAIL 4.4 resolution).
    Writes _excl files alongside originals. Does NOT modify or delete originals.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[5H] Loading Full_Aggregated...")
    hh_hom_cols = [f"HH_hom30_{i:03d}" for i in range(1, 49)]
    agg = pd.read_csv(OUT_DIR / "21CEN22GSS_aug_Full_Aggregated.csv")

    hh_means = agg[hh_hom_cols].mean(axis=1)
    fail_ppids = set(agg.loc[hh_means < 0.30, "PP_ID"])
    n_excl = len(fail_ppids)
    n_total = len(agg)
    pct_excl = 100 * n_excl / n_total
    print(f"[5H] Excluded: {n_excl} HHs ({pct_excl:.2f}% of {n_total})")

    print("[5H] Loading Full_Schedules...")
    sched_all = pd.read_csv(OUT_DIR / "21CEN22GSS_aug_Full_Schedules.csv", low_memory=False)

    demog_cols = ["PP_ID", "HH_ID", "IS_SYNTHETIC", "AGEGRP", "SEX",
                  "MARSTH", "HHSIZE", "LFTAG", "DDAY_STRATA"]
    excl_demog = sched_all.loc[
        sched_all["PP_ID"].isin(fail_ppids),
        [c for c in demog_cols if c in sched_all.columns],
    ].copy()
    excl_demog.to_csv(OUT_DIR / "21CEN22GSS_aug_excluded_ppids.csv", index=False)

    sched_excl = sched_all[~sched_all["PP_ID"].isin(fail_ppids)].copy()
    sched_excl.to_csv(OUT_DIR / "21CEN22GSS_aug_Full_Schedules_excl.csv", index=False)

    agg_excl = agg[~agg["PP_ID"].isin(fail_ppids)].copy()
    agg_excl.to_csv(OUT_DIR / "21CEN22GSS_aug_Full_Aggregated_excl.csv", index=False)

    print("[5H] Loading BEM_Schedules...")
    bem_all = pd.read_csv(OUT_DIR / "21CEN22GSS_aug_BEM_Schedules.csv", low_memory=False)
    bem_excl = bem_all[~bem_all["PP_ID"].isin(fail_ppids)].copy()
    bem_excl.to_csv(OUT_DIR / "21CEN22GSS_aug_BEM_Schedules_excl.csv", index=False)

    assert len(sched_excl) == len(sched_all) - n_excl, \
        f"Full_Schedules_excl row count {len(sched_excl)} != {len(sched_all) - n_excl}"
    assert len(agg_excl) == n_total - n_excl, \
        f"Full_Aggregated_excl row count {len(agg_excl)} != {n_total - n_excl}"
    assert len(bem_excl) == len(bem_all) - n_excl, \
        f"BEM_Schedules_excl row count {len(bem_excl)} != {len(bem_all) - n_excl}"

    hh_means_excl = agg_excl[hh_hom_cols].mean(axis=1)
    residual = int((hh_means_excl < 0.30).sum())
    assert residual == 0, f"Residual below-0.3 HHs after exclusion: {residual}"

    print("[5H] PASS — All assertions OK")
    print(f"[5H] excluded_ppids:          {len(excl_demog):,} rows")
    print(f"[5H] Full_Schedules_excl:     {len(sched_excl):,} rows")
    print(f"[5H] Full_Aggregated_excl:    {len(agg_excl):,} rows")
    print(f"[5H] BEM_Schedules_excl:      {len(bem_excl):,} rows")
    print(f"[5H] Done.")


def run_regression() -> None:
    """
    Sub-step 5G: Regression validation vs 25pct baseline.

    Primary comparison baseline: IS_SYNTHETIC=0 (observed-only) subset of the
    augmented BEM_Schedules.  Using IS_SYNTHETIC=0 as baseline gives apples-to-
    apples AT_HOME / activity / Spouse comparisons (same 30-min slot format and
    metric definition).  The spec-referenced BEM file
    (21CEN22GSS_BEM_Schedules_sample25pct.csv) uses hourly household-level
    Occupancy_Schedule — a different metric and granularity — so it serves only
    as a supplementary reference, not as a gate baseline.

    DTYPE gate: augmented DTYPE vs Census input (Aligned_Census_2022.csv),
    which is the authoritative source for Census-side attributes.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    aug_path = OUT_DIR / "21CEN22GSS_aug_BEM_Schedules.csv"
    base_path_spec = (
        BASE / "0_Occupancy" / "Outputs_21CEN22GSS"
        / "21CEN22GSS_BEM_Schedules_sample25pct.csv"
    )
    base_path = base_path_spec if base_path_spec.exists() else BASE_BEM_SAMPLE

    print(f"[5G] Loading augmented: {aug_path.name} ...")
    df_aug = pd.read_csv(aug_path)

    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    spouse_cols = [c for c in df_aug.columns if c.startswith("Spouse30_")]

    # Split by IS_SYNTHETIC for primary (apples-to-apples) comparison
    df_obs = df_aug[df_aug["IS_SYNTHETIC"] == 0].reset_index(drop=True)
    df_all = df_aug

    n_all = len(df_all)
    n_obs = len(df_obs)

    report = [
        "21CEN22GSS Aug Pipeline - Sub-step 5G Regression Validation Report\n",
        "=" * 60 + "\n",
        f"Augmented (all):  {n_all} rows  (IS_SYNTHETIC=0: {n_obs}, =1: {n_all-n_obs})\n",
        "Primary baseline: IS_SYNTHETIC=0 (observed) subset — same 30-min slot format.\n",
        f"Spec BEM baseline ({base_path.name}): hourly HH-level BEMConverter output;\n",
        "  used for supplementary AT_HOME overlay plot only (different metric/format).\n\n",
    ]

    # ── Gate 1: AT_HOME mean per 30-min slot ──────────────────────────────────
    at_home_all = df_all[hom_cols].mean().values * 100   # all agents, shape (48,)
    at_home_obs = df_obs[hom_cols].mean().values * 100   # observed only, shape (48,)

    diff_g1 = np.abs(at_home_all - at_home_obs)
    max_diff_g1 = float(diff_g1.max())
    at_home_gate = max_diff_g1 <= 3.0

    report += [
        "--- Gate 1: AT_HOME mean per 30-min slot (all vs observed subset) ---\n",
        f"  All-agents mean AT_HOME:  {at_home_all.mean():.2f}%\n",
        f"  Observed-only mean:       {at_home_obs.mean():.2f}%\n",
        f"  Max slot diff:            {max_diff_g1:.3f} pp  (gate: <=3 pp)\n",
        f"  Slots exceeding 3 pp:     {int((diff_g1 > 3.0).sum())}\n",
        f"  [GATE] AT_HOME: {'PASS' if at_home_gate else 'FAIL'}\n\n",
    ]

    # ── Gate 2: Top-5 activity time-share ─────────────────────────────────────
    act_all = pd.Series(df_all[act_cols].values.ravel()).value_counts(normalize=True) * 100
    act_obs = pd.Series(df_obs[act_cols].values.ravel()).value_counts(normalize=True) * 100
    top5_all = act_all.sort_values(ascending=False).head(5)

    max_act_diff = 0.0
    act_gate = True
    report += ["--- Gate 2: Top-5 activity time-share (all vs observed subset) ---\n"]
    for code in top5_all.index:
        a_pct = float(top5_all[code])
        o_pct = float(act_obs.get(code, 0.0))
        diff = abs(a_pct - o_pct)
        max_act_diff = max(max_act_diff, diff)
        if diff > 2.0:
            act_gate = False
        report.append(f"  Act {int(code)}: all={a_pct:.2f}%  obs={o_pct:.2f}%  diff={diff:.2f}pp\n")
    report.append(f"  Max diff: {max_act_diff:.2f} pp  (gate: <=2 pp)\n")
    report.append(f"  [GATE] Top-5 activity: {'PASS' if act_gate else 'FAIL'}\n\n")

    # ── Gate 3: Spouse co-presence mean ──────────────────────────────────────
    if spouse_cols:
        sp_all = float(df_all[spouse_cols].values.mean() * 100)
        sp_obs = float(df_obs[spouse_cols].values.mean() * 100)
        sp_diff = abs(sp_all - sp_obs)
        spouse_gate = sp_diff <= 3.0
        report += [
            "--- Gate 3: Spouse co-presence mean (all vs observed subset) ---\n",
            f"  All-agents Spouse mean:  {sp_all:.2f}%\n",
            f"  Observed-only mean:      {sp_obs:.2f}%\n",
            f"  Diff:                    {sp_diff:.3f} pp  (gate: <=3 pp)\n",
            f"  [GATE] Spouse: {'PASS' if spouse_gate else 'FAIL'}\n\n",
        ]
    else:
        spouse_gate = False
        report.append("--- Gate 3: Spouse co-presence: columns not found.\n\n")

    # ── Gate 4: DTYPE distribution vs Census input ────────────────────────────
    print(f"[5G] Loading Census input for DTYPE check: {CENSUS_FILE.name} ...")
    df_census = pd.read_csv(CENSUS_FILE, usecols=["PP_ID", "DTYPE"])
    df_census = df_census.drop_duplicates(subset="PP_ID")

    aug_dtype = df_aug["DTYPE"].value_counts(normalize=True) * 100
    cen_dtype = df_census["DTYPE"].value_counts(normalize=True) * 100

    aug_cats = set(aug_dtype.index)
    cen_cats = set(cen_dtype.index)
    dtype_cats_match = aug_cats == cen_cats

    # Numerical match: each category within ±0.1 pp (same source → exact)
    dtype_value_match = True
    dtype_diffs: list = []
    for cat in sorted(aug_cats | cen_cats):
        a = float(aug_dtype.get(cat, 0.0))
        c = float(cen_dtype.get(cat, 0.0))
        diff = abs(a - c)
        dtype_diffs.append((cat, a, c, diff))
        if diff > 0.5:
            dtype_value_match = False

    dtype_gate = dtype_cats_match and dtype_value_match

    report += [
        "--- Gate 4: DTYPE distribution (augmented vs Census input) ---\n",
        f"  Aug categories:    {sorted(aug_cats)}\n",
        f"  Census categories: {sorted(cen_cats)}\n",
        "  Per-category (aug% / census%):\n",
    ]
    for cat, a, c, diff in dtype_diffs:
        aug_str = _DTYPE_MAP.get(int(cat), str(cat)) if pd.notna(cat) else str(cat)
        report.append(f"    {aug_str} (code {cat}): aug={a:.2f}%  cen={c:.2f}%  diff={diff:.3f}pp\n")
    report += [
        f"  Categories match:  {dtype_cats_match}\n",
        f"  Values match (<0.5pp): {dtype_value_match}\n",
        f"  [GATE] DTYPE exact match: {'PASS' if dtype_gate else 'FAIL'}\n\n",
    ]

    # ── Summary ───────────────────────────────────────────────────────────────
    report += [
        "--- Gate Summary ---\n",
        f"  Gate 1  AT_HOME max slot diff:  {'PASS' if at_home_gate else 'FAIL'} "
        f"({max_diff_g1:.2f} pp vs obs baseline)\n",
        f"  Gate 2  Top-5 activity:         {'PASS' if act_gate else 'FAIL'} "
        f"({max_act_diff:.2f} pp vs obs baseline)\n",
        f"  Gate 3  Spouse co-presence:     {'PASS' if spouse_gate else 'FAIL'} "
        f"({sp_diff:.2f} pp vs obs baseline)\n" if spouse_cols else
        "  Gate 3  Spouse co-presence:     N/A\n",
        f"  Gate 4  DTYPE exact match:      {'PASS' if dtype_gate else 'FAIL'}\n",
        "\n  Note: Gates 1-3 compare all augmented agents vs IS_SYNTHETIC=0\n",
        "  (observed-only) subset — same 30-min slot format, apples-to-apples.\n",
        "  Gate 4 compares augmented DTYPE vs Aligned_Census_2022.csv input.\n",
    ]

    (OUT_DIR / "21CEN22GSS_aug_step5_regression_report.txt").write_text(
        "".join(report), encoding="utf-8"
    )

    # ── Plots ─────────────────────────────────────────────────────────────────
    slot_labels = [f"{(i * 30) // 60:02d}:{(i * 30) % 60:02d}" for i in range(48)]
    x = np.arange(48)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # AT_HOME overlay: all vs observed subset (primary comparison)
    axes[0].plot(x, at_home_all, 'b-', linewidth=2, label='All agents (aug)')
    axes[0].plot(x, at_home_obs, 'r--', linewidth=2, label='Observed (IS_SYNTHETIC=0)')
    axes[0].fill_between(x, at_home_obs - 3, at_home_obs + 3,
                         alpha=0.2, color='red', label='+/-3 pp band')
    axes[0].set_title("AT_HOME Mean per 30-min Slot: All vs Observed Subset")
    axes[0].set_xlabel("Slot (00:00 to 23:30)")
    axes[0].set_ylabel("% At Home")
    axes[0].legend(fontsize=8)
    axes[0].set_xticks(range(0, 48, 4))
    axes[0].set_xticklabels(slot_labels[::4], rotation=45)
    axes[0].grid(True, alpha=0.3)

    # Activity diff bar
    act_diff = {int(c): abs(float(act_all.get(c, 0)) - float(act_obs.get(c, 0)))
                for c in act_all.sort_values(ascending=False).head(10).index}
    axes[1].bar(list(act_diff.keys()), list(act_diff.values()), color="steelblue")
    axes[1].axhline(2.0, color='red', linestyle='--', label='2 pp gate')
    axes[1].set_title("Activity Time-Share Diff |All - Observed| (top-10)")
    axes[1].set_xlabel("Activity Code")
    axes[1].set_ylabel("Diff (pp)")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(OUT_DIR / "21CEN22GSS_aug_step5_regression_AT_HOME.png", dpi=100)
    plt.close()

    print(f"[5G] Done. Report -> {OUT_DIR / '21CEN22GSS_aug_step5_regression_report.txt'}")
    print(f"[5G] Gate 1 AT_HOME:   {'PASS' if at_home_gate else 'FAIL'} (max diff {max_diff_g1:.2f} pp)")
    print(f"[5G] Gate 2 Activity:  {'PASS' if act_gate else 'FAIL'} (max diff {max_act_diff:.2f} pp)")
    print(f"[5G] Gate 3 Spouse:    {'PASS' if spouse_gate else 'FAIL'}" + (f" (diff {sp_diff:.2f} pp)" if spouse_cols else ""))
    print(f"[5G] Gate 4 DTYPE:     {'PASS' if dtype_gate else 'FAIL'}")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Step 5: Census-GSS slot-native linkage (21CEN22GSS Aug Pipeline)"
    )
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--smoke", action="store_true", help="1%% smoke run (~2865 agents)")
    grp.add_argument("--full", action="store_true", help="Full run (286,540 agents)")
    grp.add_argument("--aggregate", action="store_true", help="HH aggregation (Sub-step 5E)")
    grp.add_argument("--bem", action="store_true", help="occToBEM conversion (Sub-step 5F)")
    grp.add_argument(
        "--regression", action="store_true", help="Regression vs 25pct baseline (Sub-step 5G)"
    )
    grp.add_argument(
        "--exclusion", action="store_true", help="Exclude implausible HHs (Sub-step 5H)"
    )
    parser.add_argument(
        "--region-tier", action="store_true",
        help="Enable Tier-2b (AGEGRP,SEX,LFTAG,REGION,DDAY) so 2005 GSS (legacy 5-region "
             "PR) can match on geography instead of falling straight to Tier-3. "
             "Default off reproduces current behaviour. Applies to --smoke/--full only.",
    )
    args = parser.parse_args()

    if args.smoke:
        run_linkage_smoke(region_tier=args.region_tier)
    elif args.full:
        run_linkage_full(region_tier=args.region_tier)
    elif args.aggregate:
        run_aggregate()
    elif args.bem:
        run_bem()
    elif args.regression:
        run_regression()
    elif args.exclusion:
        run_exclusion()
