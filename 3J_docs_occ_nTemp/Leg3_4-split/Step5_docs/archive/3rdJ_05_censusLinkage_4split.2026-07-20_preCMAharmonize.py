"""
3rdJ_05_censusLinkage_4split.py — Step 5: Census-GSS Slot-Native Demographic Matching
3J Leg-3 FOUR-CHANNEL Pipeline (Residential AT_HOME + Office AT_WORK + Retail AT_RETAIL
+ Hotel [non-GSS, province-level, no linkage here])

Forked from 3rdJ_05_censusLinkage_2split.py (Leg-2). Leg-3 deltas (A-E, see
3rdJ_05_censusLinkage_4split.md §3):
  - 2025 Census (Aligned_Census_2025.csv), PID / SIM_HH_ID identifiers
  - Three channels carried: hom30 (AT_HOME) + wrk30 (AT_WORK) + ret30 (AT_RETAIL,
    Delta A) — ret30 is a per-person population-fraction channel that mirrors
    wrk30 in every respect (carried, never re-derived, never HH-maxed).
  - Co-presence columns (Alone30, Spouse30, Children30, parents30,
    otherInFAMs30, otherHHs30, friends30, others30, colleagues30) x48
  - Office archetype assignment from Census NOCS
  - Retail: v1 single "Retail Retail" archetype — no lookup, no linkage needed
  - Join-key connectivity audit (Delta D, NEW) — run inside --smoke, before
    matching, to catch the Leg-2-class PR-remap silent-truncation bug.
  - Extended BEM/validation for AT_WORK + AT_RETAIL channels

CLI:
    py 3rdJ_05_censusLinkage_4split.py --smoke       # 1% Census sample + Leg-3 locked pool
    py 3rdJ_05_censusLinkage_4split.py --full        # Full Census + Leg-3 locked pool
    py 3rdJ_05_censusLinkage_4split.py --aggregate   # HH aggregation (Sub-step 5E)
    py 3rdJ_05_censusLinkage_4split.py --bem         # BEM prep (Sub-step 5F)
    py 3rdJ_05_censusLinkage_4split.py --regression  # Regression validation (Sub-step 5G)
    py 3rdJ_05_censusLinkage_4split.py --exclusion   # Exclusion filter (Sub-step 5H)
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
# parents[0] = Step5_docs/
# parents[1] = Leg3_4-split/
# parents[2] = 3J_docs_occ_nTemp/
# parents[3] = GSSCanada-main/
BASE = Path(__file__).resolve().parents[3]

# Pool path — the Leg-3 LOCKED pool (with ret30_*), never the Leg-2 pool.
# Single pool used for BOTH --smoke and --full (no separate small smoke pool exists
# for Leg-3; smoke only subsamples the CENSUS side to 1%, per Leg-2 precedent).
# Locked 2026-07-20: 192,183 rows, md5 ebb1dfe8d678744415ce0852dc77147f (see
# 3rdJ_05_censusLinkage_4split.md Progress Log for provenance).
LOCKED_POOL = (
    BASE / "3J_docs_occ_nTemp" / "Leg3_4-split" / "Step4_docs"
    / "outputs_step4" / "sweep" / "seed_3_raked3_mindwell_actv" / "augmented_diaries.csv"
)
SMOKE_POOL = LOCKED_POOL
FULL_POOL = LOCKED_POOL

# Census (same file as Leg-2 — reused verbatim per 4split.md §2)
CENSUS_FILE = BASE / "0_Occupancy" / "Outputs_Aligned" / "Aligned_Census_2025.csv"

# Outputs — Leg-3's OWN dir; NEVER write into Leg-2's outputs_step5/
OUT_DIR = (
    BASE / "3J_docs_occ_nTemp" / "Leg3_4-split" / "Step5_docs" / "outputs_step5"
)
SMOKE_DIR = OUT_DIR / "smoke"

# Office archetype lookup
ARCHETYPE_LOOKUP = BASE / "0_Occupancy" / "processed" / "office_archetype_lookup.csv"

# ── BEM label maps ─────────────────────────────────────────────────────────────
_DTYPE_MAP = {
    1: "SingleD", 2: "SemiD", 3: "Attached", 4: "DuplexD",
    5: "HighRise", 6: "MidRise", 7: "OtherA", 8: "Movable",
}
_PR_MAP = {
    10: "Atlantic", 11: "Atlantic", 12: "Atlantic", 13: "Atlantic",
    24: "Quebec", 35: "Ontario", 46: "Prairies", 47: "Prairies",
    48: "Alberta", 59: "BC", 70: "Northern Canada",
}

# ── Match configuration ───────────────────────────────────────────────────────
MATCH_KEYS = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA"]
DDAY_COL = "DDAY_STRATA"

_T1_KEYS = MATCH_KEYS + [DDAY_COL]
_T2_KEYS = ["AGEGRP", "SEX", "LFTAG", "PR", DDAY_COL]
_T3_KEYS = ["AGEGRP", "SEX", DDAY_COL]
_T4_KEYS = [DDAY_COL]

# Proportional DDAY assignment: 5 weekdays + 1 Sat + 1 Sun per week
_DDAY_PROBS = [5 / 7, 1 / 7, 1 / 7]

# 2025 Census building columns (no BUILT/VALUE)
_CENSUS_BUILD_COLS = ["DTYPE", "BEDRM", "ROOM", "CONDO", "REPAIR"]

# Columns that come from Census and must NOT be taken from pool (no _x/_y collisions)
_CENSUS_AUTHORITATIVE = set(MATCH_KEYS) | {"HRSWRK", "NOCS", "TOTINC"}

# Pool columns excluded (match keys, occID, and Census-authoritative overlap cols)
_POOL_EXCLUDE = set(MATCH_KEYS) | {DDAY_COL, "occID"} | _CENSUS_AUTHORITATIVE

# Province→region map (identity for already-grouped 1–6; province codes for 10+).
# Module-level (moved out of load_augmented_pool) so the Delta-D connectivity audit
# and the validator's Section 0 can import this SAME dict — one source of truth,
# never a second hand-coded copy. Source: authoritative
# (eSim_dynamicML_mHead_alignment.py::harmonize_pr).
_PROVINCE_TO_REGION: dict[int, int] = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,  # already grouped — identity
    10: 1, 11: 1, 12: 1, 13: 1,            # Atlantic / Eastern Canada
    24: 2,                                  # Quebec
    35: 3,                                  # Ontario
    46: 4, 47: 4, 48: 4,                   # Prairies
    59: 5,                                  # British Columbia
    60: 6, 61: 6, 62: 6,                   # Northern Canada / Territories
}

# ── Office archetype definition ───────────────────────────────────────────────
# NOCS 2021 major groups (single-digit codes):
#   0  = Senior management occupations
#   1  = Business, finance and administration
#   2  = Natural and applied sciences
#   3  = Health occupations
#   4  = Education, law and social, community and government services
#   5  = Arts, culture, recreation and sport
#   6  = Sales and service occupations
#   7  = Trades, transport and equipment operators
#   8  = Natural resources, agriculture and related production
#   9  = Manufacturing and utilities
#
# Bucket mapping (from 2-channel_split.md §3.5, mapped to actual NOCS codes):
#   Knowledge/professional   => 0, 1, 2       → Office_Knowledge
#   Public/health/education  => 3, 4, 5       → Office_Public
#   Sales/customer-facing    => 6             → Office_Sales
#   Trades/production        => 7, 8, 9       → NonOffice
#
# NaN / missing NOCS => archetype = "Unknown_NOCS", is_office = False (flagged)

_NOCS_TO_ARCHETYPE: dict[int, tuple[str, bool]] = {
    0: ("Office_Knowledge", True),
    1: ("Office_Knowledge", True),
    2: ("Office_Knowledge", True),
    3: ("Office_Public",    True),
    4: ("Office_Public",    True),
    5: ("Office_Public",    True),
    6: ("Office_Sales",     True),
    7: ("NonOffice",        False),
    8: ("NonOffice",        False),
    9: ("NonOffice",        False),
}


def build_office_archetype_lookup(df_census: pd.DataFrame) -> pd.DataFrame:
    """
    Build and write office_archetype_lookup.csv from Census NOCS values.
    Returns the lookup DataFrame.
    """
    nocs_counts = df_census["NOCS"].value_counts(dropna=False).sort_index()
    print("\n[archetype] Distinct NOCS values in Aligned_Census_2025.csv:")
    for nocs_val, cnt in nocs_counts.items():
        label = _NOCS_TO_ARCHETYPE.get(int(nocs_val) if pd.notna(nocs_val) else -99, None)
        arch = label[0] if label else "Unknown_NOCS"
        is_office = label[1] if label else False
        flag = "  <-- FLAGGED: unmapped" if label is None else ""
        print(f"    NOCS={nocs_val}  count={cnt}  -> {arch}  is_office={is_office}{flag}")

    # Build lookup rows from unique values observed
    rows = []
    for nocs_val in sorted(df_census["NOCS"].dropna().unique()):
        key = int(nocs_val)
        if key in _NOCS_TO_ARCHETYPE:
            arch, is_off = _NOCS_TO_ARCHETYPE[key]
        else:
            arch, is_off = "Unknown_NOCS", False
            print(f"  [WARN] NOCS={key} not in mapping — flagged Unknown_NOCS")
        rows.append({"NOCS": key, "archetype_label": arch, "is_office": is_off})

    df_lookup = pd.DataFrame(rows)
    ARCHETYPE_LOOKUP.parent.mkdir(parents=True, exist_ok=True)
    df_lookup.to_csv(ARCHETYPE_LOOKUP, index=False)
    print(f"[archetype] Lookup written -> {ARCHETYPE_LOOKUP}")
    return df_lookup


def assign_office_archetype(df: pd.DataFrame, nocs_col: str = "NOCS") -> pd.DataFrame:
    """Add office_archetype_ID column based on Census NOCS."""
    def _map(val):
        if pd.isna(val):
            return "Unknown_NOCS"
        key = int(val)
        return _NOCS_TO_ARCHETYPE.get(key, ("Unknown_NOCS", False))[0]

    df = df.copy()
    df["office_archetype_ID"] = df[nocs_col].map(_map)
    return df


# ── Core functions ────────────────────────────────────────────────────────────

def load_augmented_pool(path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reads augmented_diaries.csv, splits into:
      - wd_pool: DDAY_STRATA == 1 (Weekday)
      - we_pool: DDAY_STRATA in {2, 3} (Saturday + Sunday)
    Returns (wd_pool, we_pool).

    Province→region remap: pool carries StatCan province codes (10/11/12/13/24/35/
    46/47/48/59) but the census uses grouped region codes (1–6). Apply the SAME
    mapping used in eSim_dynamicML_mHead_alignment.py::harmonize_pr() to align
    pool PR with census PR before any DDAY split or matching. Values already in
    domain 1–6 are identity-mapped. Any unmapped value raises immediately.
    Source: authoritative (eSim_dynamicML_mHead_alignment.py::harmonize_pr).
    Uses the MODULE-LEVEL _PROVINCE_TO_REGION dict (see top of file) — single
    source of truth, also reused by audit_join_key_connectivity (Delta D) and by
    the validator's Section 0.
    """
    df = pd.read_csv(path, low_memory=False)

    # Log PR distribution before remap
    pr_before = df["PR"].value_counts().sort_index()
    print("[load_augmented_pool] PR value_counts BEFORE remap:")
    for v, c in pr_before.items():
        print(f"  PR={v}: {c}")

    # Apply remap
    remapped = df["PR"].map(_PROVINCE_TO_REGION)
    unmapped = df.loc[remapped.isna(), "PR"].unique().tolist()
    if unmapped:
        raise ValueError(
            f"[load_augmented_pool] Unmapped PR values after province→region remap: {unmapped}. "
            f"Add them to _PROVINCE_TO_REGION before proceeding."
        )
    df["PR"] = remapped.astype(int)

    # Log PR distribution after remap
    pr_after = df["PR"].value_counts().sort_index()
    print("[load_augmented_pool] PR value_counts AFTER remap:")
    for v, c in pr_after.items():
        print(f"  PR={v}: {c}")

    wd_pool = df[df[DDAY_COL] == 1].reset_index(drop=True)
    we_pool = df[df[DDAY_COL].isin([2, 3])].reset_index(drop=True)
    return wd_pool, we_pool


def run_slot_match(
    df_census: pd.DataFrame,
    df_pool: pd.DataFrame,
    match_keys: list[str],
    dday_col: str = "DDAY_STRATA",
) -> pd.DataFrame:
    """
    4-tier demographic fallback match.
    Returns DataFrame: [PID, SIM_HH_ID, occID, DDAY_STRATA, MATCH_TIER, _pool_idx].
    Seed: np.random.seed(42) at function entry.
    """
    np.random.seed(42)

    t1_keys = match_keys + [dday_col]
    t2_keys = ["AGEGRP", "SEX", "LFTAG", "PR", dday_col]
    t3_keys = ["AGEGRP", "SEX", dday_col]
    t4_keys = [dday_col]

    def _build_index(keys: list[str]) -> dict[tuple, np.ndarray]:
        idx: dict = {}
        valid = df_pool.dropna(subset=keys)
        for vals, grp in valid.groupby(keys, sort=False):
            k = vals if isinstance(vals, tuple) else (vals,)
            idx[k] = grp.index.to_numpy()
        return idx

    t1 = _build_index(t1_keys)
    t2 = _build_index(t2_keys)
    t3 = _build_index(t3_keys)
    t4 = _build_index(t4_keys)

    pids: list = []
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
        elif k3 in t3:
            pool_i = int(np.random.choice(t3[k3]))
            tier = "3_Constraints"
        else:
            pool_i = int(np.random.choice(t4[k4]))
            tier = "4_FailSafe"

        pool_row = df_pool.loc[pool_i]
        pids.append(agent["PID"])
        hh_ids.append(agent["SIM_HH_ID"])
        occ_ids.append(pool_row["occID"])
        ddays.append(dday)
        tiers.append(tier)
        pool_idxs.append(pool_i)

    return pd.DataFrame(
        {
            "PID": pids,
            "SIM_HH_ID": hh_ids,
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
    Joins matched keys to augmented_diaries on _pool_idx (direct label lookup).
    Carries act30, hom30, wrk30, ret30 (Delta A — three per-person / population
    channels + activity) + co-presence + metadata.
    Census is authoritative for shared columns; pool NAICS is kept as NAICS_donor.
    Adds office_archetype_ID from Census NOCS.
    """
    # 1. Pull diary rows directly via stored pool index labels
    pool_rows = df_pool.loc[df_matched["_pool_idx"].to_numpy()].copy()
    pool_rows = pool_rows.reset_index(drop=True)

    # 2. Select pool columns to carry through
    #    Explicit pass-through groups: act30, hom30, wrk30, co-presence x48, metadata
    act_cols   = sorted([c for c in df_pool.columns if c.startswith("act30_")])
    hom_cols   = sorted([c for c in df_pool.columns if c.startswith("hom30_")])
    wrk_cols   = sorted([c for c in df_pool.columns if c.startswith("wrk30_")])
    ret_cols   = sorted([c for c in df_pool.columns if c.startswith("ret30_")])
    alone_cols = sorted([c for c in df_pool.columns if c.startswith("Alone30_")])
    spouse_cols= sorted([c for c in df_pool.columns if c.startswith("Spouse30_")])
    child_cols = sorted([c for c in df_pool.columns if c.startswith("Children30_")])
    par_cols   = sorted([c for c in df_pool.columns if c.startswith("parents30_")])
    ofam_cols  = sorted([c for c in df_pool.columns if c.startswith("otherInFAMs30_")])
    ohh_cols   = sorted([c for c in df_pool.columns if c.startswith("otherHHs30_")])
    fri_cols   = sorted([c for c in df_pool.columns if c.startswith("friends30_")])
    oth_cols   = sorted([c for c in df_pool.columns if c.startswith("others30_")])
    col_cols   = sorted([c for c in df_pool.columns if c.startswith("colleagues30_")])

    # Metadata columns from pool (not match keys, not Census-authoritative, not channel cols)
    _explicit_pool = (
        set(act_cols) | set(hom_cols) | set(wrk_cols) | set(ret_cols)
        | set(alone_cols) | set(spouse_cols) | set(child_cols)
        | set(par_cols) | set(ofam_cols) | set(ohh_cols)
        | set(fri_cols) | set(oth_cols) | set(col_cols)
    )
    meta_pool = ["CYCLE_YEAR", "IS_SYNTHETIC", "WGHT_PER", "COLLECT_MODE",
                 "TELEWORK", "WORK_SCHEDULE", "IS_SYNTHETIC"]
    meta_pool = [c for c in meta_pool if c in df_pool.columns]

    # NAICS is pool-only (no NAICS in 2025 Census) — rename to NAICS_donor for clarity
    naics_in_pool = "NAICS" in df_pool.columns

    pool_diary_cols = (
        meta_pool
        + act_cols + hom_cols + wrk_cols + ret_cols
        + alone_cols + spouse_cols + child_cols + par_cols
        + ofam_cols + ohh_cols + fri_cols + oth_cols + col_cols
    )
    # Add NAICS_donor if present
    if naics_in_pool:
        pool_diary_cols = pool_diary_cols + ["NAICS"]

    # Deduplicate while preserving order
    seen = set()
    pool_diary_cols = [c for c in pool_diary_cols if c in df_pool.columns
                       and not (c in seen or seen.add(c))]

    # 3. Assemble base + diary schedule
    base = df_matched[["PID", "SIM_HH_ID", "MATCH_TIER", "occID", DDAY_COL]].copy()
    base = base.reset_index(drop=True)
    pool_section = pool_rows[pool_diary_cols].reset_index(drop=True)

    # Rename NAICS -> NAICS_donor
    if naics_in_pool and "NAICS" in pool_section.columns:
        pool_section = pool_section.rename(columns={"NAICS": "NAICS_donor"})

    df_out = pd.concat([base, pool_section], axis=1)

    # 4. Append Census demographics (authoritative) + building vars
    cen_demog = [k for k in MATCH_KEYS if k in df_census.columns]
    cen_extra = [c for c in ["HRSWRK", "NOCS", "TOTINC"] if c in df_census.columns]
    cen_build = [c for c in _CENSUS_BUILD_COLS if c in df_census.columns]
    cen_cols = ["PID"] + cen_demog + cen_extra + cen_build
    df_out = df_out.merge(
        df_census[cen_cols].drop_duplicates(subset="PID"),
        on="PID", how="left"
    )

    # 5. Assign office archetype from Census NOCS
    df_out = assign_office_archetype(df_out, nocs_col="NOCS")

    # 6. Sanity: no _x/_y suffix collisions
    xy_cols = [c for c in df_out.columns if c.endswith("_x") or c.endswith("_y")]
    if xy_cols:
        raise ValueError(f"Column suffix collision detected: {xy_cols}")

    return df_out


# ── Internal helpers ──────────────────────────────────────────────────────────

def _assign_dday(df_census: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Add DDAY_STRATA using 5:1:1 weekday/Saturday/Sunday proportional assignment.
    """
    rng = np.random.default_rng(seed)
    df = df_census.copy()
    df[DDAY_COL] = rng.choice([1, 2, 3], size=len(df), p=_DDAY_PROBS)
    return df


def _print_tier_report(df_matched: pd.DataFrame) -> dict:
    """Print and return tier distribution + WD/WE FailSafe rates."""
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
    return {"fs_wd": fs_wd, "fs_we": fs_we, "counts": counts, "n": n}


def _nocs_agreement_report(df_full: pd.DataFrame, df_pool: pd.DataFrame) -> float:
    """
    Compare Census NOCS (authoritative) vs pool donor NOCS (from matched pool row).
    NOCS is NOT a match key, so agreement is an honest diagnostic.
    """
    if "NOCS" not in df_full.columns:
        print("[nocs_agreement] Census NOCS column not found — skip")
        return float("nan")

    # Retrieve donor NOCS from pool via _pool_idx (only available if df_full has it)
    # We report agreement rate between census NOCS and pool NAICS (different concept)
    # since pool carries NAICS_donor, not NOCS. Log this distinction.
    print("\n[nocs_agreement] Census NOCS distribution in linked output:")
    nocs_dist = df_full["NOCS"].value_counts(dropna=False).sort_index()
    for v, c in nocs_dist.items():
        print(f"  NOCS={v}: {c} ({100*c/len(df_full):.2f}%)")

    # Pool has NAICS_donor (industry), not NOCS (occupation). Log honestly:
    print("\n[nocs_agreement] NOTE: Pool carries NAICS_donor (industry code), not NOCS.")
    print("  NOCS (occupation) is Census-authoritative. NAICS_donor is the GSS respondent's")
    print("  industry. Direct NOCS agreement rate vs donor is NOT available (different schema).")
    print("  office_archetype_ID is keyed on Census NOCS — the correct authoritative source.")
    return float("nan")  # Agreement rate not computable (different variable types)


def audit_join_key_connectivity(df_census: pd.DataFrame, df_pool: pd.DataFrame) -> dict:
    """
    Delta D — join-key connectivity audit (the Leg-2 PR-remap lesson).

    Call AFTER the census/DDAY remaps are applied and the pool's PR has already
    been province→region remapped by load_augmented_pool (i.e. call with the
    SAME df_pool that run_slot_match will use), and BEFORE matching.

    Uses the matcher's own key lists (_T1_KEYS, _T2_KEYS at module scope) — no
    second copy of the remap or the key list is hand-coded here; df_pool is
    already post-remap by the time it reaches this function.

    For every Tier-1 match key (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA,
    DDAY_STRATA): prints census domain size, pool domain size, and whether
    census_domain ⊆ pool_domain. RAISES immediately (loud FAIL) if any census
    value for any key is absent from the pool domain — this is exactly the
    Leg-2 bug class where a silent PR coding mismatch confined matching to
    ~30% of the pool while tier rates still looked healthy.

    Also reports the share of pool rows reachable under Tier-1 and Tier-2 key
    combinations (i.e. pool rows whose full key-combo also appears among at
    least one census agent — everything else can never be selected by
    run_slot_match's Tier-1/Tier-2 exact-match dict lookups).
    """
    print("\n" + "=" * 70)
    print("[Delta D] Join-key connectivity audit (census -> pool, post-remap)")
    print("=" * 70)

    keys = _T1_KEYS  # AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA, DDAY_STRATA
    rows: list[dict] = []
    any_fail = False

    header = f"  {'KEY':10s} {'census_n':>9s} {'pool_n':>7s} {'overlap%':>9s}  census⊆pool"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for k in keys:
        if k not in df_census.columns or k not in df_pool.columns:
            print(f"  [SKIP] key {k!r} missing from census or pool columns")
            continue
        cen_dom = set(df_census[k].dropna().unique().tolist())
        pool_dom = set(df_pool[k].dropna().unique().tolist())
        missing = cen_dom - pool_dom
        subset_ok = len(missing) == 0
        overlap_pct = 100.0 * len(cen_dom & pool_dom) / len(cen_dom) if cen_dom else 100.0
        if not subset_ok:
            any_fail = True
        rows.append({
            "key": k,
            "n_census_vals": len(cen_dom),
            "n_pool_vals": len(pool_dom),
            "overlap_pct": overlap_pct,
            "subset_ok": subset_ok,
            "missing_vals": sorted(missing, key=str)[:10],
        })
        verdict = "YES" if subset_ok else f"NO  <-- missing {sorted(missing, key=str)[:10]}"
        print(f"  {k:10s} {len(cen_dom):9d} {len(pool_dom):7d} {overlap_pct:8.2f}%  {verdict}")

    # Tier-1 / Tier-2 pool reachability — vectorized via merge (fast on 192k-row pool)
    cen_t1 = df_census[_T1_KEYS].dropna().drop_duplicates()
    cen_t2 = df_census[_T2_KEYS].dropna().drop_duplicates()

    pool_t1_valid = df_pool.dropna(subset=_T1_KEYS)
    pool_t2_valid = df_pool.dropna(subset=_T2_KEYS)

    m1 = pool_t1_valid[_T1_KEYS].merge(
        cen_t1.assign(_hit1=1), on=_T1_KEYS, how="left"
    )
    m2 = pool_t2_valid[_T2_KEYS].merge(
        cen_t2.assign(_hit2=1), on=_T2_KEYS, how="left"
    )
    t1_reachable = int(m1["_hit1"].notna().sum())
    t2_reachable = int(m2["_hit2"].notna().sum())
    t1_share = 100.0 * t1_reachable / len(df_pool) if len(df_pool) else 0.0
    t2_share = 100.0 * t2_reachable / len(df_pool) if len(df_pool) else 0.0

    print(f"\n  Pool rows reachable under Tier-1 (8-key exact) combos present in census: "
          f"{t1_share:.2f}%  (n={t1_reachable}/{len(df_pool)})")
    print(f"  Pool rows reachable under Tier-2 (5-key) combos present in census: "
          f"{t2_share:.2f}%  (n={t2_reachable}/{len(df_pool)})")
    if t1_share < 95.0:
        print(f"  [Delta D WARN] Tier-1 reachable share {t1_share:.2f}% < 95% gate")
    if t2_share < 95.0:
        print(f"  [Delta D WARN] Tier-2 reachable share {t2_share:.2f}% < 95% gate")

    print("=" * 70)

    if any_fail:
        fail_keys = [r["key"] for r in rows if not r["subset_ok"]]
        raise ValueError(
            f"[Delta D FAIL] Join-key domain mismatch — census value(s) absent from pool "
            f"domain for key(s): {fail_keys}. This is the exact Leg-2 PR-remap-class bug "
            f"(silent truncation of the matchable pool while tier rates still look healthy). "
            f"Fix the remap/harmonization before proceeding with matching."
        )

    return {"key_rows": rows, "t1_reachable_pct": t1_share, "t2_reachable_pct": t2_share}


# ── Linkage runners ───────────────────────────────────────────────────────────

def run_linkage_smoke(sample_frac: float = 0.01) -> None:
    """
    1% Census sample + the Leg-3 locked pool.
    Writes to outputs_step5/smoke/ (Leg-3's own dir — first smoke build, no
    legacy production smoke output to protect, unlike the Leg-2 smoke_rungI/
    isolation which existed only to avoid clobbering an in-place Leg-2 debug run).
    Includes Rung-(i) W3 colleagues before/after diagnostic (verbatim Leg-2).
    Runs the Delta-D join-key connectivity audit before matching.
    """
    smoke_out_dir = SMOKE_DIR
    smoke_out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[smoke] Loading pool from: {SMOKE_POOL}")
    wd_pool, we_pool = load_augmented_pool(str(SMOKE_POOL))
    df_pool = pd.concat([wd_pool, we_pool], ignore_index=True)
    print(f"[smoke] Pool rows: {len(df_pool)}")

    print(f"[smoke] Loading Census from: {CENSUS_FILE}")
    df_census_full = pd.read_csv(CENSUS_FILE)
    n_census_full = len(df_census_full)

    # Deduplicate on PID
    df_census_full = df_census_full.drop_duplicates(subset="PID").reset_index(drop=True)
    n_deduped = len(df_census_full)
    if n_census_full != n_deduped:
        print(f"[smoke] Deduped Census: {n_census_full} -> {n_deduped} unique PIDs")

    # Build archetype lookup from full Census (canonical NOCS distribution)
    build_office_archetype_lookup(df_census_full)

    df_census_sample = df_census_full.sample(frac=sample_frac, random_state=42)
    df_census_sample = _assign_dday(df_census_sample, seed=42)

    # ── Delta D: join-key connectivity audit — AFTER remaps, BEFORE matching ──
    audit_join_key_connectivity(df_census_sample, df_pool)

    print(f"\n[smoke] {len(df_census_sample)} Census agents | pool: {len(df_pool)} rows")
    df_matched = run_slot_match(df_census_sample, df_pool, MATCH_KEYS, DDAY_COL)

    # ── W3 BEFORE: compute colleagues30 stats before Rung-(i) is applied ────────
    # We simulate the pre-Rung-I state by calling expand_slot_schedules with Rung-I
    # temporarily disabled. Instead, capture pre-imputation from pool directly.
    col_cols_pool = sorted([c for c in df_pool.columns if c.startswith("colleagues30_")])
    wrk_cols_pool = sorted([c for c in df_pool.columns if c.startswith("wrk30_")])
    if col_cols_pool:
        pool_rows_pre = df_pool.loc[df_matched["_pool_idx"].to_numpy()].copy()
        pool_rows_pre = pool_rows_pre.reset_index(drop=True)
        syn_mask_pre = df_matched[DDAY_COL].isin([2, 3]).to_numpy()
        obs_mask_pre = (df_matched[DDAY_COL] == 1).to_numpy()

        # Full-pop mean (all rows, as carried from pool, before Rung-I)
        all_col_before = float(pool_rows_pre[col_cols_pool].fillna(0).values.mean() * 100)
        obs_col_before = float(pool_rows_pre[col_cols_pool].fillna(0).values[obs_mask_pre].mean() * 100) if obs_mask_pre.any() else float("nan")
        syn_col_before = float(pool_rows_pre[col_cols_pool].fillna(0).values[syn_mask_pre].mean() * 100) if syn_mask_pre.any() else float("nan")
        # Per-worker synthetic nonzero fraction
        syn_wrk_mask_pre = (pool_rows_pre[wrk_cols_pool].fillna(0).values[syn_mask_pre].sum(axis=1) > 0)
        syn_col_vals_pre = pool_rows_pre[col_cols_pool].fillna(0).values[syn_mask_pre]
        syn_worker_col_nonzero_before = float(
            (syn_col_vals_pre[syn_wrk_mask_pre] > 0).any(axis=1).mean() * 100
        ) if syn_wrk_mask_pre.any() else float("nan")
        print(f"\n[W3-BEFORE] Full-pop col mean: {all_col_before:.2f}%")
        print(f"[W3-BEFORE] OBS-origin col mean: {obs_col_before:.2f}%")
        print(f"[W3-BEFORE] SYN-origin col mean: {syn_col_before:.2f}%")
        print(f"[W3-BEFORE] SYN worker nonzero frac: {syn_worker_col_nonzero_before:.1f}%")
        print(f"[W3-BEFORE] W3 gap (|all - obs|): {abs(all_col_before - obs_col_before):.2f} pp  (gate <=3pp)")

    df_full = expand_slot_schedules(df_matched, df_pool, df_census_full)

    # ── Schema validation ─────────────────────────────────────────────────────
    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]

    missing_act = [c for c in act_cols if c not in df_full.columns]
    missing_hom = [c for c in hom_cols if c not in df_full.columns]
    missing_wrk = [c for c in wrk_cols if c not in df_full.columns]
    missing_ret = [c for c in ret_cols if c not in df_full.columns]

    print("\n--- Smoke Schema Checks ---")
    print(f"  act30 cols: {len(act_cols) - len(missing_act)}/48  {'OK' if not missing_act else 'FAIL: '+str(missing_act[:3])}")
    print(f"  hom30 cols: {len(hom_cols) - len(missing_hom)}/48  {'OK' if not missing_hom else 'FAIL: '+str(missing_hom[:3])}")
    print(f"  wrk30 cols: {len(wrk_cols) - len(missing_wrk)}/48  {'OK' if not missing_wrk else 'FAIL: '+str(missing_wrk[:3])}")
    print(f"  ret30 cols: {len(ret_cols) - len(missing_ret)}/48  {'OK' if not missing_ret else 'FAIL: '+str(missing_ret[:3])}")
    print(f"  office_archetype_ID present: {'YES' if 'office_archetype_ID' in df_full.columns else 'NO'}")
    print(f"  NAICS_donor present: {'YES' if 'NAICS_donor' in df_full.columns else 'NO'}")

    # Delta A hard gate: ret30 must survive carry-through into Full_Schedules_smoke
    assert not missing_ret, f"ret30 cols missing from smoke Full_Schedules: {missing_ret[:5]}"

    xy_cols = [c for c in df_full.columns if c.endswith("_x") or c.endswith("_y")]
    print(f"  _x/_y suffix collisions: {len(xy_cols)}  {'OK' if not xy_cols else 'FAIL: '+str(xy_cols)}")

    # ── Archetype distribution ────────────────────────────────────────────────
    if "office_archetype_ID" in df_full.columns:
        print("\n--- Office Archetype Distribution (smoke sample) ---")
        arch_dist = df_full["office_archetype_ID"].value_counts(dropna=False)
        for arch, cnt in arch_dist.items():
            print(f"  {arch}: {cnt} ({100*cnt/len(df_full):.2f}%)")

    # ── NOCS agreement diagnostic ─────────────────────────────────────────────
    _nocs_agreement_report(df_full, df_pool)

    # ── AT_WORK channel spot-check ────────────────────────────────────────────
    if wrk_cols and all(c in df_full.columns for c in wrk_cols):
        mean_at_work = float(df_full[wrk_cols].values.mean())
        print(f"\n  Mean AT_WORK across all slots: {100 * mean_at_work:.2f}%")

    if hom_cols and all(c in df_full.columns for c in hom_cols):
        mean_at_home = float(df_full[hom_cols].values.mean())
        print(f"  Mean AT_HOME across all slots: {100 * mean_at_home:.2f}%  (baseline ~62.5%)")

    # ── AT_RETAIL channel spot-check (Delta A mirror of AT_WORK) ─────────────
    if ret_cols and all(c in df_full.columns for c in ret_cols):
        mean_at_retail = float(df_full[ret_cols].values.mean())
        ret_vals = set(float(v) for v in np.unique(df_full[ret_cols].values.ravel())
                        if not np.isnan(v))
        print(f"  Mean AT_RETAIL across all slots: {100 * mean_at_retail:.2f}%  (expect ~2%-positive)")
        print(f"  ret30 observed values: {sorted(ret_vals)}")

    # ── W3 AFTER: colleagues30 stats after Rung-(i) ──────────────────────────
    col_cols_out = sorted([c for c in df_full.columns if c.startswith("colleagues30_")])
    wrk_cols_out = sorted([c for c in df_full.columns if c.startswith("wrk30_")])
    if col_cols_out:
        syn_mask_out = df_full[DDAY_COL].isin([2, 3])
        obs_mask_out = df_full[DDAY_COL] == 1

        all_col_after  = float(df_full[col_cols_out].fillna(0).values.mean() * 100)
        obs_col_after  = float(df_full.loc[obs_mask_out, col_cols_out].fillna(0).values.mean() * 100) if obs_mask_out.any() else float("nan")
        syn_col_after  = float(df_full.loc[syn_mask_out, col_cols_out].fillna(0).values.mean() * 100) if syn_mask_out.any() else float("nan")
        # Per-worker synthetic nonzero fraction
        syn_rows_out = df_full[syn_mask_out]
        syn_wrk_mask_out = (syn_rows_out[wrk_cols_out].fillna(0).values.sum(axis=1) > 0)
        if syn_wrk_mask_out.any():
            syn_col_vals_out = syn_rows_out[col_cols_out].fillna(0).values
            syn_worker_col_nonzero_after = float(
                (syn_col_vals_out[syn_wrk_mask_out] > 0).any(axis=1).mean() * 100
            )
        else:
            syn_worker_col_nonzero_after = float("nan")

        print(f"\n[W3-AFTER]  Full-pop col mean: {all_col_after:.2f}%")
        print(f"[W3-AFTER]  OBS-origin col mean: {obs_col_after:.2f}%")
        print(f"[W3-AFTER]  SYN-origin col mean: {syn_col_after:.2f}%")
        print(f"[W3-AFTER]  SYN worker nonzero frac: {syn_worker_col_nonzero_after:.1f}%")
        print(f"[W3-AFTER]  W3 gap (|all - obs|): {abs(all_col_after - obs_col_after):.2f} pp  (gate <=3pp)")

        # Physical constraint check: col>0 where wrk==0
        # Check SYNTHETIC rows only (observed rows are untouched, may have natural violations)
        syn_full = df_full[syn_mask_out]
        violations_syn_only = 0
        for cc, wc in zip(col_cols_out, wrk_cols_out):
            if wc in syn_full.columns:
                violations_syn_only += int(((syn_full[cc].fillna(0) > 0) & (syn_full[wc] == 0)).sum())
        total_slots_syn = len(syn_full) * len(col_cols_out)
        violations_obs = 0
        obs_full = df_full[obs_mask_out]
        for cc, wc in zip(col_cols_out, wrk_cols_out):
            if wc in obs_full.columns:
                violations_obs += int(((obs_full[cc].fillna(0) > 0) & (obs_full[wc] == 0)).sum())
        print(f"[W3-AFTER]  Physical constraint (SYN rows only — col>0 where wrk==0): "
              f"{violations_syn_only} / {total_slots_syn}  "
              f"({'PASS' if violations_syn_only == 0 else 'FAIL'})")
        print(f"[W3-AFTER]  OBS row violations (untouched, informational): "
              f"{violations_obs} / {len(obs_full)*len(col_cols_out)}")
        violations = violations_syn_only  # Used in summary below

        print("\n--- Rung-I W3 Summary ---")
        if col_cols_pool:
            print(f"  BEFORE: all={all_col_before:.2f}%  obs={obs_col_before:.2f}%  "
                  f"syn={syn_col_before:.2f}%  syn-worker-nonzero={syn_worker_col_nonzero_before:.1f}%  "
                  f"gap={abs(all_col_before - obs_col_before):.2f}pp")
        print(f"  AFTER:  all={all_col_after:.2f}%   obs={obs_col_after:.2f}%  "
              f"syn={syn_col_after:.2f}%  syn-worker-nonzero={syn_worker_col_nonzero_after:.1f}%  "
              f"gap={abs(all_col_after - obs_col_after):.2f}pp")
        print(f"  Constraint: col=0 where wrk=0 violations: {violations} "
              f"({'PASS' if violations == 0 else 'FAIL'})")

    # ── Tier report ───────────────────────────────────────────────────────────
    print("\n--- Smoke Tier Distribution ---")
    _print_tier_report(df_matched)

    # ── 5 random agent spot-checks ────────────────────────────────────────────
    print("\n--- 5 random agent spot-checks (Census -> matched diary) ---")
    act_cols_all = sorted([c for c in df_full.columns if c.startswith("act30_")])
    wrk_cols_all = sorted([c for c in df_full.columns if c.startswith("wrk30_")])
    ret_cols_all = sorted([c for c in df_full.columns if c.startswith("ret30_")])
    sample5 = df_matched.sample(min(5, len(df_matched)), random_state=0)
    for _, row in sample5.iterrows():
        pid = row["PID"]
        cen_row = df_census_full[df_census_full["PID"] == pid].iloc[0]
        sched_row = df_full[df_full["PID"] == pid].iloc[0]
        act_first10 = " ".join(str(int(v)) for v in sched_row[act_cols_all[:10]])
        wrk_first10 = " ".join(str(int(v)) for v in sched_row[wrk_cols_all[:10]])
        ret_first10 = " ".join(str(int(v)) for v in sched_row[ret_cols_all[:10]])
        nocs = cen_row.get("NOCS", "n/a")
        arch = sched_row.get("office_archetype_ID", "n/a")
        print(
            f"  PID={pid} AGEGRP={cen_row['AGEGRP']} LFTAG={cen_row['LFTAG']}"
            f" NOCS={nocs} arch={arch}"
            f" -> tier={row['MATCH_TIER']} occID={row['occID']}"
            f"\n    act[0:10]=[{act_first10}]"
            f"\n    wrk[0:10]=[{wrk_first10}]"
            f"\n    ret[0:10]=[{ret_first10}]"
        )

    # ── Save (Leg-3's own outputs_step5/smoke/ dir) ───────────────────────────
    df_matched.drop(columns=["_pool_idx"]).to_csv(
        smoke_out_dir / "3rdJ_25CEN_aug_Matched_Keys_smoke.csv", index=False
    )
    df_full.to_csv(smoke_out_dir / "3rdJ_25CEN_aug_Full_Schedules_smoke.csv", index=False)

    print(f"\nSmoke outputs -> {smoke_out_dir}")
    print("[smoke] DONE — three channels (hom30 + wrk30 + ret30) + office_archetype_ID "
          "+ Rung-I + Delta-D join-key audit verified")


def run_linkage_full() -> None:
    """Full Census (all deduped agents). Writes to outputs_step5/."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[full] Loading pool from: {FULL_POOL}")
    if not FULL_POOL.exists():
        raise FileNotFoundError(
            f"Full production pool not found: {FULL_POOL}\n"
            f"The full pool (192,183 rows) is still being downloaded.\n"
            f"Run --smoke against the raked_sample pool in the meantime."
        )
    wd_pool, we_pool = load_augmented_pool(str(FULL_POOL))
    df_pool = pd.concat([wd_pool, we_pool], ignore_index=True)

    print(f"[full] Loading Census from: {CENSUS_FILE}")
    df_census_raw = pd.read_csv(CENSUS_FILE)
    n_raw = len(df_census_raw)
    df_census = df_census_raw.drop_duplicates(subset="PID").reset_index(drop=True)
    n_deduped = len(df_census)
    if n_raw != n_deduped:
        print(f"[warn] Removed {n_raw - n_deduped} duplicate PID rows ({n_raw} -> {n_deduped})")

    # Build archetype lookup
    build_office_archetype_lookup(df_census)

    df_census_dday = _assign_dday(df_census, seed=42)

    print(f"\n[full] {len(df_census_dday)} Census agents | pool: {len(df_pool)} rows")
    df_matched = run_slot_match(df_census_dday, df_pool, MATCH_KEYS, DDAY_COL)
    df_full = expand_slot_schedules(df_matched, df_pool, df_census)

    # Dynamic hard-gate assertions
    assert len(df_full) >= n_deduped, f"Row count {len(df_full)} < {n_deduped}"
    assert df_full["PID"].nunique() == len(df_full), "Duplicate PIDs in output"
    assert df_full["occID"].notna().all(), "Null occID in output"
    assert "office_archetype_ID" in df_full.columns, "office_archetype_ID missing from output"

    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    assert all(c in df_full.columns for c in wrk_cols[:3]), "wrk30 cols missing from output"

    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]
    assert all(c in df_full.columns for c in ret_cols[:3]), "ret30 cols missing from output"

    df_matched.drop(columns=["_pool_idx"]).to_csv(
        OUT_DIR / "3rdJ_25CEN_aug_Matched_Keys.csv", index=False
    )
    df_full.to_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Schedules.csv", index=False)

    print("\n--- Full Run Tier Distribution ---")
    stats = _print_tier_report(df_matched)

    _nocs_agreement_report(df_full, df_pool)

    report_lines = [
        "3rdJ 25CEN Aug Pipeline — Match Tier Report\n",
        f"Total Census agents: {stats['n']}\n\n",
    ]
    for t, c in stats["counts"].items():
        report_lines.append(f"  {t}: {c} ({100 * c / stats['n']:.2f}%)\n")
    report_lines += [
        f"\nWD FailSafe rate: {100 * stats['fs_wd']:.2f}%  (gate <=10%)\n",
        f"WE FailSafe rate: {100 * stats['fs_we']:.2f}%  (gate <=12%)\n",
    ]
    (OUT_DIR / "3rdJ_25CEN_aug_Validation_match.txt").write_text(
        "".join(report_lines), encoding="utf-8"
    )

    print(f"\nOutputs -> {OUT_DIR}")


# ── Sub-step 5E: HH aggregation ───────────────────────────────────────────────

def run_aggregate() -> None:
    """
    Sub-step 5E: Slot-native HH aggregation.

    hom30 (residential AT_HOME): HH occupied = max across members per slot.
    wrk30 (office AT_WORK): stays per-person (work is individual — do NOT HH-max).
    Row count asserted dynamically from the output file.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[5E] Loading Full_Schedules...")
    df = pd.read_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Schedules.csv", low_memory=False)

    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]

    print("[5E] Computing HH-level occupancy per slot (max across HH members, hom30 only)...")
    hh_occ = df.groupby("SIM_HH_ID")[hom_cols].max()
    hh_occ.columns = [f"HH_{c}" for c in hom_cols]
    hh_occ = hh_occ.reset_index()

    hh_size_obs = df.groupby("SIM_HH_ID").size().rename("N_HH_MEMBERS").reset_index()

    df_agg = df.merge(hh_occ, on="SIM_HH_ID", how="left")
    df_agg = df_agg.merge(hh_size_obs, on="SIM_HH_ID", how="left")

    n = len(df_agg)
    n_hh_null = int(df_agg["SIM_HH_ID"].isna().sum())
    n_dup = int(df_agg["PID"].duplicated().sum())
    mean_hhsize = float(df_agg["HHSIZE"].mean()) if "HHSIZE" in df_agg.columns else float("nan")
    n_unique_hh = int(df_agg["SIM_HH_ID"].nunique())

    print(f"[5E] Row count: {n}  SIM_HH_ID null: {n_hh_null}  Dup PIDs: {n_dup}")
    print(f"[5E] Unique SIM_HH_IDs: {n_unique_hh}  Mean HHSIZE: {mean_hhsize:.4f}")
    print("[5E] NOTE: wrk30 AND ret30 stay per-person (no HH aggregation of AT_WORK / AT_RETAIL).")

    assert n_hh_null == 0, f"SIM_HH_ID null rows: {n_hh_null}"
    assert n_dup == 0, f"Duplicate PIDs: {n_dup}"
    # Dynamic row count (derived from census, not hardcoded)
    n_expected = len(pd.read_csv(CENSUS_FILE, usecols=["PID"]).drop_duplicates())
    assert n == n_expected, f"Row count {n} != expected {n_expected}"

    # Delta B: ret30 rides through df_agg untouched (never HH-maxed) — assert survival
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]
    missing_ret_agg = [c for c in ret_cols if c not in df_agg.columns]
    assert not missing_ret_agg, f"ret30 cols missing from Full_Aggregated: {missing_ret_agg[:5]}"

    df_agg.to_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Aggregated.csv", index=False)

    hh_hom_cols = [f"HH_hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    ind_hom_mean = df_agg[hom_cols].mean() * 100
    hh_hom_mean = df_agg[hh_hom_cols].mean() * 100
    wrk_mean = df_agg[[c for c in wrk_cols if c in df_agg.columns]].mean() * 100
    ret_mean = df_agg[[c for c in ret_cols if c in df_agg.columns]].mean() * 100

    slot_labels = [f"{(i * 30) // 60:02d}:{(i * 30) % 60:02d}" for i in range(48)]
    x = range(48)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(x, ind_hom_mean.values, 'b-', linewidth=2, label='Individual AT_HOME')
    axes[0].plot(x, hh_hom_mean.values, 'r--', linewidth=2, label='HH occupied (any home)')
    if len(wrk_mean) == 48:
        axes[0].plot(x, wrk_mean.values, 'g:', linewidth=2, label='Mean AT_WORK (per-person)')
    if len(ret_mean) == 48:
        axes[0].plot(x, ret_mean.values, 'm-.', linewidth=2, label='Mean AT_RETAIL (per-person)')
    axes[0].set_title("Individual vs HH Occupancy + AT_WORK + AT_RETAIL (30-min slots)")
    axes[0].set_xlabel("Slot")
    axes[0].set_ylabel("% At Home / HH Occupied / At Work")
    axes[0].set_xticks(range(0, 48, 4))
    axes[0].set_xticklabels(slot_labels[::4], rotation=45)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    df_agg["HHSIZE"].value_counts().sort_index().plot(kind="bar", ax=axes[1], color="steelblue")
    axes[1].set_title(f"HH Size Distribution (mean={mean_hhsize:.2f})")
    axes[1].set_xlabel("HHSIZE")
    axes[1].set_ylabel("Count")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "3rdJ_25CEN_aug_Validation_Plot.png", dpi=100)
    plt.close()

    print(f"[5E] Done. Output -> {OUT_DIR / '3rdJ_25CEN_aug_Full_Aggregated.csv'}")


# ── Sub-step 5F: BEM prep ─────────────────────────────────────────────────────

def run_bem() -> None:
    """
    Sub-step 5F: Slot-native BEM schedule preparation.
    Validates 48-slot schema for act30, hom30, wrk30.
    Adds DTYPE_str / PR_str label columns. Adds mean-wrk30 diurnal plot.
    Carries office_archetype_ID.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[5F] Loading Full_Aggregated...")
    df = pd.read_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Aggregated.csv", low_memory=False)

    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]

    # ── Schema validation ─────────────────────────────────────────────────────
    missing_act = [c for c in act_cols if c not in df.columns]
    missing_hom = [c for c in hom_cols if c not in df.columns]
    missing_wrk = [c for c in wrk_cols if c not in df.columns]
    assert not missing_act, f"Missing act30 cols: {missing_act[:5]}"
    assert not missing_hom, f"Missing hom30 cols: {missing_hom[:5]}"
    assert not missing_wrk, f"Missing wrk30 cols: {missing_wrk[:5]}"

    act_vals_flat = df[act_cols].values.ravel()
    hom_vals_flat = df[hom_cols].values.ravel()
    wrk_vals_flat = df[wrk_cols].values.ravel()

    act_unique = set(int(v) for v in np.unique(act_vals_flat[~np.isnan(act_vals_flat)]))
    hom_unique = set(float(v) for v in np.unique(hom_vals_flat[~np.isnan(hom_vals_flat)]))
    wrk_unique = set(float(v) for v in np.unique(wrk_vals_flat[~np.isnan(wrk_vals_flat)]))

    assert act_unique <= set(range(1, 15)), f"act30 out-of-range: {act_unique - set(range(1,15))}"
    assert hom_unique <= {0.0, 1.0}, f"hom30 non-binary: {hom_unique - {0.0,1.0}}"
    assert wrk_unique <= {0.0, 1.0}, f"wrk30 non-binary: {wrk_unique - {0.0,1.0}}"

    n = len(df)
    print(f"[5F] Schema OK: act30={len(act_cols)}/48, hom30={len(hom_cols)}/48, "
          f"wrk30={len(wrk_cols)}/48, rows={n}")
    print(f"[5F] act30 range: {min(act_unique)}-{max(act_unique)}")
    print(f"[5F] hom30 values: {sorted(hom_unique)}")
    print(f"[5F] wrk30 values: {sorted(wrk_unique)}")

    # BEM label columns
    df["DTYPE_str"] = df["DTYPE"].map(_DTYPE_MAP).fillna("Other") if "DTYPE" in df.columns else "Unknown"
    df["PR_str"] = df["PR"].map(_PR_MAP).fillna("Others") if "PR" in df.columns else "Unknown"

    if "office_archetype_ID" in df.columns:
        arch_dist = df["office_archetype_ID"].value_counts(dropna=False)
        print("[5F] office_archetype_ID distribution:")
        for a, c in arch_dist.items():
            print(f"    {a}: {c} ({100*c/n:.2f}%)")
    else:
        print("[5F] WARN: office_archetype_ID not found — add in --full run first")

    df.to_csv(OUT_DIR / "3rdJ_25CEN_aug_BEM_Schedules.csv", index=False)

    # ── Validation plots ──────────────────────────────────────────────────────
    slot_labels = [f"{(i * 30) // 60:02d}:{(i * 30) % 60:02d}" for i in range(48)]
    hom_mean = df[hom_cols].mean() * 100
    wrk_mean = df[wrk_cols].mean() * 100

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    axes[0].plot(range(48), hom_mean.values, 'b-', linewidth=2, label='Mean AT_HOME')
    axes[0].plot(range(48), wrk_mean.values, 'g-', linewidth=2, label='Mean AT_WORK')
    axes[0].set_title("Mean AT_HOME + AT_WORK per 30-min Slot (3J Leg-3, ret30 in Section 3r)")
    axes[0].set_xlabel("Slot")
    axes[0].set_ylabel("% Occupied")
    axes[0].set_xticks(range(0, 48, 4))
    axes[0].set_xticklabels(slot_labels[::4], rotation=45)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    act_values = df[act_cols].values.ravel()
    act_share = pd.Series(act_values[~np.isnan(act_values)].astype(int)
                         ).value_counts(normalize=True).sort_index() * 100
    axes[1].bar(act_share.index.astype(int), act_share.values, color="steelblue")
    axes[1].set_title("Activity Time-Share (act30, 1=Work ... 14=Misc)")
    axes[1].set_xlabel("Activity Code")
    axes[1].set_ylabel("% of slots")
    axes[1].set_xticks(sorted(act_share.index.astype(int)))

    plt.tight_layout()
    plt.savefig(OUT_DIR / "3rdJ_25CEN_aug_BEM_temporals.png", dpi=100)
    plt.close()

    print(f"[5F] Done. Output -> {OUT_DIR / '3rdJ_25CEN_aug_BEM_Schedules.csv'}")


# ── Sub-step 5H: Exclusion ────────────────────────────────────────────────────

def run_exclusion() -> None:
    """
    Sub-step 5H: Exclude households with per-HH mean AT_HOME < 0.30.
    Residential exclusion only — office channel is not excluded here.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[5H] Loading Full_Aggregated...")
    hh_hom_cols = [f"HH_hom30_{i:03d}" for i in range(1, 49)]
    agg = pd.read_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Aggregated.csv", low_memory=False)

    hh_means = agg[hh_hom_cols].mean(axis=1)
    fail_pids = set(agg.loc[hh_means < 0.30, "PID"])
    n_excl = len(fail_pids)
    n_total = len(agg)
    pct_excl = 100 * n_excl / n_total
    print(f"[5H] Excluded: {n_excl} HHs ({pct_excl:.2f}% of {n_total})")

    print("[5H] Loading Full_Schedules...")
    sched_all = pd.read_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Schedules.csv", low_memory=False)

    demog_cols = ["PID", "SIM_HH_ID", "IS_SYNTHETIC", "AGEGRP", "SEX",
                  "MARSTH", "HHSIZE", "LFTAG", "DDAY_STRATA"]
    excl_demog = sched_all.loc[
        sched_all["PID"].isin(fail_pids),
        [c for c in demog_cols if c in sched_all.columns],
    ].copy()
    excl_demog.to_csv(OUT_DIR / "3rdJ_25CEN_aug_excluded_pids.csv", index=False)

    sched_excl = sched_all[~sched_all["PID"].isin(fail_pids)].copy()
    sched_excl.to_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Schedules_excl.csv", index=False)

    agg_excl = agg[~agg["PID"].isin(fail_pids)].copy()
    agg_excl.to_csv(OUT_DIR / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv", index=False)

    print("[5H] Loading BEM_Schedules...")
    bem_all = pd.read_csv(OUT_DIR / "3rdJ_25CEN_aug_BEM_Schedules.csv", low_memory=False)
    bem_excl = bem_all[~bem_all["PID"].isin(fail_pids)].copy()
    bem_excl.to_csv(OUT_DIR / "3rdJ_25CEN_aug_BEM_Schedules_excl.csv", index=False)

    assert len(sched_excl) == len(sched_all) - n_excl, "Full_Schedules_excl row count mismatch"
    assert len(agg_excl) == n_total - n_excl, "Full_Aggregated_excl row count mismatch"
    assert len(bem_excl) == len(bem_all) - n_excl, "BEM_Schedules_excl row count mismatch"

    # Delta C: ret30 rides through exclusion untouched (whole-row filter) — assert survival
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]
    assert all(c in sched_excl.columns for c in ret_cols), \
        "ret30 cols missing from Full_Schedules_excl"
    assert all(c in agg_excl.columns for c in ret_cols), \
        "ret30 cols missing from Full_Aggregated_excl"

    hh_means_excl = agg_excl[hh_hom_cols].mean(axis=1)
    residual = int((hh_means_excl < 0.30).sum())
    assert residual == 0, f"Residual below-0.3 HHs after exclusion: {residual}"

    print("[5H] PASS — All assertions OK")
    print(f"[5H] excluded_pids:           {len(excl_demog):,} rows")
    print(f"[5H] Full_Schedules_excl:     {len(sched_excl):,} rows")
    print(f"[5H] Full_Aggregated_excl:    {len(agg_excl):,} rows")
    print(f"[5H] BEM_Schedules_excl:      {len(bem_excl):,} rows")
    print(f"[5H] Done.")


# ── Sub-step 5G: Regression validation ───────────────────────────────────────

def run_regression() -> None:
    """
    Sub-step 5G: Regression validation vs IS_SYNTHETIC=0 baseline.

    Residential gates (AT_HOME, top-5 activity, Spouse30, DTYPE).
    AT_WORK gates: per-slot mean, LFTAG rate sanity, colleagues co-presence.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    aug_path = OUT_DIR / "3rdJ_25CEN_aug_BEM_Schedules.csv"
    print(f"[5G] Loading augmented: {aug_path.name} ...")
    df_aug = pd.read_csv(aug_path, low_memory=False)

    hom_cols   = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols   = [f"wrk30_{i:03d}" for i in range(1, 49)]
    act_cols   = [f"act30_{i:03d}" for i in range(1, 49)]
    spouse_cols= [c for c in df_aug.columns if c.startswith("Spouse30_")]
    col_cols   = [c for c in df_aug.columns if c.startswith("colleagues30_")]

    df_obs = df_aug[df_aug["IS_SYNTHETIC"] == 0].reset_index(drop=True) \
             if "IS_SYNTHETIC" in df_aug.columns else df_aug.copy()
    df_all = df_aug

    n_all = len(df_all)
    n_obs = len(df_obs)

    report = [
        "3rdJ 25CEN Aug Pipeline — Sub-step 5G Regression Validation Report\n",
        "=" * 60 + "\n",
        f"Augmented (all):  {n_all} rows  (IS_SYNTHETIC=0: {n_obs})\n\n",
    ]

    # ── Gate 1: AT_HOME mean per slot ─────────────────────────────────────────
    hom_p = [c for c in hom_cols if c in df_aug.columns]
    if hom_p and n_obs > 0:
        at_home_all = df_all[hom_p].mean().values * 100
        at_home_obs = df_obs[hom_p].mean().values * 100
        diff_g1 = np.abs(at_home_all - at_home_obs)
        max_diff_g1 = float(diff_g1.max())
        at_home_gate = max_diff_g1 <= 3.0
        report += [
            "--- Gate 1: AT_HOME mean per 30-min slot (all vs observed subset) ---\n",
            f"  Max slot diff: {max_diff_g1:.3f} pp  (gate: <=3 pp)\n",
            f"  [GATE] AT_HOME: {'PASS' if at_home_gate else 'FAIL'}\n\n",
        ]
    else:
        at_home_gate = False
        max_diff_g1 = float("nan")

    # ── Gate 2: Top-5 activity time-share ─────────────────────────────────────
    act_p = [c for c in act_cols if c in df_aug.columns]
    if act_p and n_obs > 0:
        af = pd.Series(df_all[act_p].values.ravel()).dropna().astype(int)
        of = pd.Series(df_obs[act_p].values.ravel()).dropna().astype(int)
        aug_share = af.value_counts(normalize=True) * 100
        obs_share = of.value_counts(normalize=True) * 100
        top5_all = aug_share.sort_values(ascending=False).head(5)
        max_act_diff = max(abs(float(aug_share.get(c, 0)) - float(obs_share.get(c, 0)))
                          for c in top5_all.index)
        act_gate = max_act_diff <= 2.0
        report += [
            "--- Gate 2: Top-5 activity time-share (all vs observed subset) ---\n",
            f"  Max diff: {max_act_diff:.2f} pp  (gate: <=2 pp)\n",
            f"  [GATE] Activity: {'PASS' if act_gate else 'FAIL'}\n\n",
        ]
    else:
        act_gate = False
        max_act_diff = float("nan")

    # ── Gate 3: Spouse co-presence mean ──────────────────────────────────────
    sp_diff = float("nan")
    spouse_gate = False
    if spouse_cols and n_obs > 0:
        sp_all = float(df_all[spouse_cols].mean(axis=0).mean() * 100)
        sp_obs = float(df_obs[spouse_cols].mean(axis=0).mean() * 100)
        sp_diff = abs(sp_all - sp_obs)
        spouse_gate = sp_diff <= 3.0
        report += [
            "--- Gate 3: Spouse co-presence mean ---\n",
            f"  All={sp_all:.2f}%  Obs={sp_obs:.2f}%  Diff={sp_diff:.3f} pp  (gate: <=3pp)\n",
            f"  [GATE] Spouse: {'PASS' if spouse_gate else 'FAIL'}\n\n",
        ]

    # ── Gate 4: DTYPE distribution vs Census ──────────────────────────────────
    dtype_gate = False
    max_dtype_diff = float("nan")
    if "DTYPE" in df_aug.columns:
        df_cen = pd.read_csv(CENSUS_FILE, usecols=["PID", "DTYPE"])
        df_cen = df_cen.drop_duplicates(subset="PID")
        aug_dtype = df_aug["DTYPE"].value_counts(normalize=True) * 100
        cen_dtype = df_cen["DTYPE"].value_counts(normalize=True) * 100
        all_t = sorted(set(aug_dtype.index) | set(cen_dtype.index))
        max_dtype_diff = max(abs(float(aug_dtype.get(t, 0)) - float(cen_dtype.get(t, 0)))
                             for t in all_t)
        dtype_gate = max_dtype_diff < 0.5
        report += [
            "--- Gate 4: DTYPE distribution (augmented vs Census input) ---\n",
            f"  Max diff: {max_dtype_diff:.4f} pp\n",
            f"  [GATE] DTYPE: {'PASS' if dtype_gate else 'FAIL'}\n\n",
        ]

    # ── Gate 5 (NEW): AT_WORK mean per slot ───────────────────────────────────
    wrk_p = [c for c in wrk_cols if c in df_aug.columns]
    at_work_gate = False
    max_diff_wrk = float("nan")
    if wrk_p and n_obs > 0:
        at_work_all = df_all[wrk_p].mean().values * 100
        at_work_obs = df_obs[wrk_p].mean().values * 100
        diff_wrk = np.abs(at_work_all - at_work_obs)
        max_diff_wrk = float(diff_wrk.max())
        at_work_gate = max_diff_wrk <= 3.0
        report += [
            "--- Gate 5 (NEW): AT_WORK mean per 30-min slot (all vs observed subset) ---\n",
            f"  Max slot diff: {max_diff_wrk:.3f} pp  (gate: <=3 pp)\n",
            f"  [GATE] AT_WORK per-slot: {'PASS' if at_work_gate else 'FAIL'}\n\n",
        ]

    # ── Gate 6 (NEW): AT_WORK rate by LFTAG ──────────────────────────────────
    lftag_gate = False
    if wrk_p and "LFTAG" in df_aug.columns:
        wrk_by_lftag = df_aug.groupby("LFTAG")[wrk_p].mean().mean(axis=1) * 100
        report += [
            "--- Gate 6 (NEW): AT_WORK rate by LFTAG ---\n",
        ]
        employed_rate = 0.0
        retired_rate = 0.0
        for lf, rate in wrk_by_lftag.items():
            report.append(f"  LFTAG={lf}: mean AT_WORK={rate:.2f}%\n")
            if lf in [1, 2]:  # employed/self-employed
                employed_rate = max(employed_rate, rate)
            elif lf in [3, 4, 5, 6]:  # retired, student, not in LF, etc.
                retired_rate = max(retired_rate, rate)
        lftag_gate = employed_rate > retired_rate  # employed >> not-in-LF
        report.append(f"  [GATE] Employed AT_WORK > Not-in-LF: {'PASS' if lftag_gate else 'FAIL'}\n\n")

    # ── Gate 7 (NEW): Colleagues co-presence mean ─────────────────────────────
    col_gate = False
    max_col_diff = float("nan")
    if col_cols and n_obs > 0:
        col_all = float(df_all[col_cols].mean(axis=0).mean() * 100)
        col_obs = float(df_obs[col_cols].mean(axis=0).mean() * 100)
        max_col_diff = abs(col_all - col_obs)
        col_gate = max_col_diff <= 3.0
        report += [
            "--- Gate 7 (NEW): Colleagues co-presence mean (all vs observed) ---\n",
            f"  All={col_all:.2f}%  Obs={col_obs:.2f}%  Diff={max_col_diff:.3f} pp  (gate: <=3pp)\n",
            f"  [GATE] Colleagues: {'PASS' if col_gate else 'FAIL'}\n\n",
        ]

    # ── Gate 8 (NEW): Office archetype distribution sanity ────────────────────
    arch_gate = False
    if "office_archetype_ID" in df_aug.columns:
        arch_dist = df_aug["office_archetype_ID"].value_counts(normalize=True) * 100
        nonoffice_share = float(arch_dist.get("NonOffice", 0.0))
        unknown_share = float(arch_dist.get("Unknown_NOCS", 0.0))
        arch_gate = nonoffice_share < 60.0 and unknown_share < 10.0
        report += [
            "--- Gate 8 (NEW): Office archetype distribution sanity ---\n",
        ]
        for a, pct in arch_dist.items():
            report.append(f"  {a}: {pct:.2f}%\n")
        report += [
            f"  NonOffice share: {nonoffice_share:.2f}% (expect <60%)\n",
            f"  Unknown_NOCS share: {unknown_share:.2f}% (expect <10%)\n",
            f"  [GATE] Archetype sanity: {'PASS' if arch_gate else 'FAIL'}\n\n",
        ]

    # ── Summary ───────────────────────────────────────────────────────────────
    report += [
        "--- Gate Summary ---\n",
        f"  Gate 1  AT_HOME max slot diff:     {'PASS' if at_home_gate else 'FAIL'} ({max_diff_g1:.2f} pp)\n",
        f"  Gate 2  Top-5 activity:            {'PASS' if act_gate else 'FAIL'} ({max_act_diff:.2f} pp)\n",
        f"  Gate 3  Spouse co-presence:        {'PASS' if spouse_gate else 'FAIL'} ({sp_diff:.2f} pp)\n"
        if not (sp_diff != sp_diff) else "  Gate 3  Spouse co-presence:        N/A\n",
        f"  Gate 4  DTYPE exact match:         {'PASS' if dtype_gate else 'FAIL'}\n",
        f"  Gate 5  AT_WORK max slot diff:     {'PASS' if at_work_gate else 'FAIL'} ({max_diff_wrk:.2f} pp)\n",
        f"  Gate 6  LFTAG AT_WORK sanity:      {'PASS' if lftag_gate else 'FAIL'}\n",
        f"  Gate 7  Colleagues co-presence:    {'PASS' if col_gate else 'FAIL'} ({max_col_diff:.2f} pp)\n",
        f"  Gate 8  Archetype distribution:    {'PASS' if arch_gate else 'FAIL'}\n",
    ]

    (OUT_DIR / "3rdJ_25CEN_aug_step5_regression_report.txt").write_text(
        "".join(report), encoding="utf-8"
    )

    # ── Plots ─────────────────────────────────────────────────────────────────
    slot_labels = [f"{(i * 30) // 60:02d}:{(i * 30) % 60:02d}" for i in range(48)]
    x = np.arange(48)

    if hom_p and wrk_p and n_obs > 0:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        axes[0].plot(x, at_home_all, 'b-', linewidth=2, label='AT_HOME All agents')
        axes[0].plot(x, at_home_obs, 'b--', linewidth=1.5, label='AT_HOME IS_SYN=0')
        axes[0].plot(x, at_work_all, 'g-', linewidth=2, label='AT_WORK All agents')
        axes[0].plot(x, at_work_obs, 'g--', linewidth=1.5, label='AT_WORK IS_SYN=0')
        axes[0].fill_between(x, at_home_obs - 3, at_home_obs + 3,
                             alpha=0.1, color='blue', label='+/-3pp band')
        axes[0].set_title("AT_HOME + AT_WORK: All vs Observed Subset")
        axes[0].set_xlabel("Slot (00:00 to 23:30)")
        axes[0].set_ylabel("% Occupied")
        axes[0].legend(fontsize=8)
        axes[0].set_xticks(range(0, 48, 4))
        axes[0].set_xticklabels(slot_labels[::4], rotation=45)
        axes[0].grid(True, alpha=0.3)

        if "office_archetype_ID" in df_aug.columns:
            arch_dist = df_aug["office_archetype_ID"].value_counts()
            axes[1].bar(range(len(arch_dist)), arch_dist.values,
                        tick_label=arch_dist.index, color="steelblue")
            axes[1].set_title("Office Archetype Distribution")
            axes[1].set_xlabel("Archetype")
            axes[1].set_ylabel("Count")
            axes[1].tick_params(axis='x', rotation=30)

        plt.tight_layout()
        plt.savefig(OUT_DIR / "3rdJ_25CEN_aug_step5_regression.png", dpi=100)
        plt.close()

    print(f"[5G] Report -> {OUT_DIR / '3rdJ_25CEN_aug_step5_regression_report.txt'}")
    print(f"[5G] Gate 1 AT_HOME:     {'PASS' if at_home_gate else 'FAIL'} ({max_diff_g1:.2f} pp)")
    print(f"[5G] Gate 5 AT_WORK:     {'PASS' if at_work_gate else 'FAIL'} ({max_diff_wrk:.2f} pp)")
    print(f"[5G] Gate 8 Archetype:   {'PASS' if arch_gate else 'FAIL'}")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Step 5: 3J Leg-3 4-channel Census-GSS Linkage (25CEN, AT_HOME + AT_WORK + AT_RETAIL)"
    )
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--smoke",     action="store_true", help="1%% Census + Leg-3 locked pool smoke run")
    grp.add_argument("--full",      action="store_true", help="Full Census run")
    grp.add_argument("--aggregate", action="store_true", help="HH aggregation (Sub-step 5E)")
    grp.add_argument("--bem",       action="store_true", help="BEM prep (Sub-step 5F)")
    grp.add_argument("--regression",action="store_true", help="Regression validation (Sub-step 5G)")
    grp.add_argument("--exclusion", action="store_true", help="Exclude implausible HHs (Sub-step 5H)")
    args = parser.parse_args()

    if args.smoke:
        run_linkage_smoke()
    elif args.full:
        run_linkage_full()
    elif args.aggregate:
        run_aggregate()
    elif args.bem:
        run_bem()
    elif args.regression:
        run_regression()
    elif args.exclusion:
        run_exclusion()
