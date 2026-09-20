# =============================================================================
# wp9_1c_2025_rebuild.py
# WP9 Stage 1c staging-only driver: rebuilds the 2025 occupancy/BEM file with
# Ruling A (grid denominator), reproducing patches P2/P3 (and evaluating P5)
# from 2026-09-19_WP9_stage1b_rebuild.md as RUN-TIME overrides only.
#
# NEVER edits previous/eSim_dynamicML_mHead.py (a never-modify file, CLAUDE.md).
# It imports that module UNCHANGED and monkey-patches two of its methods at
# runtime, on the class objects, after import:
#   - HouseholdAggregator._aggregate_household   (P2, always installed)
#   - BEMConverter.process_households             (P3; installed only for
#                                                    --convert grid/hhsize, NOT
#                                                    for --convert original; P5
#                                                    evaluated, NOT applied --
#                                                    see docstring below)
#
# This module does NOT import previous.eSim_dynamicML_mHead (and therefore does
# NOT import TensorFlow) at module load time -- only inside install_overrides(),
# which the caller invokes explicitly. This lets a lightweight local smoke test
# (wp9_1c_smoke_test.py) import and exercise the two override functions directly
# without pulling in TensorFlow/sklearn/matplotlib/seaborn.
#
# Ruling D-1J-A3 (manager, 2026-09-19, see task doc "Manager ruling after
# BLOCKED"): the 2025 rebuild starts from the April Matched_Population_Keys.csv
# (matching itself is NOT re-run -- MatchProfiler._find_best_match() calls
# matches.sample(1) with no fixed seed, previous/eSim_dynamicML_mHead.py:1462-
# 1485, and is therefore not reproducible). Two entry points:
#   --from-keys              expansion -> refinement -> aggregation (P2)
#   --convert {original,grid,hhsize}   BEM conversion only, reads Full_data.csv
#     "original" = the unedited process_households (P3 override NOT installed;
#       used only for the reproduction check against the April file).
#     "grid"/"hhsize" = P3 override installed, OCC_DENOM set accordingly.
#
# Task doc: 1J_docs_occ/IMP/impl/2026-09-19_WP9_stage1c_2025.md
# =============================================================================

from __future__ import annotations

import os
import sys
import pathlib

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Module-level state: P2's "active" line is printed once, on first real
# invocation, not on every household (process_all calls _aggregate_household
# once per SIM_HH_ID x Day_Type group -- often tens of thousands of times per
# run; printing every time would flood the job log with no new information).
# -----------------------------------------------------------------------------
_override_state = {"p2_announced": False}


def aggregate_household_override(self, people_grids):
    """
    Verbatim copy of HouseholdAggregator._aggregate_household
    (previous/eSim_dynamicML_mHead.py:2066-2130) plus WP9 Stage 1c P2: keep the
    raw per-slot headcount (`occCount`) and the number of member presence grids
    (`nGrid`) -- the Ruling A (OCC_DENOM=grid) denominator input -- exactly as
    P2 did for the four census years (2026-09-19_WP9_stage1b_rebuild.md
    Patches section, e.g. 21CEN22GSS_HH_aggregation.py: occCount/nGrid added
    right after `occupancy_count = presence_binary.sum(axis=0)`, and set to 0
    in the early-return / empty-household branch).

    Only the lines marked "# P2:" below are new; everything else is the
    original body unchanged.
    """
    if not _override_state["p2_announced"]:
        print("P2-2025 aggregation override: active")
        _override_state["p2_announced"] = True

    # Create Time Index (00:00, 00:05, ... 23:55)
    time_slots = pd.date_range("00:00", "23:55", freq=f"{self.res}min").strftime('%H:%M')

    # Dataframe to store final household results
    hh_df = pd.DataFrame({'Time_Slot': time_slots})

    if not people_grids:
        hh_df['occPre'] = 0
        hh_df['occDensity'] = 0
        hh_df['occActivity'] = ""
        hh_df['occCount'] = 0   # P2: 0/0 in the early-return branch
        hh_df['nGrid'] = 0      # P2
        return hh_df

    # --- STEP B: Aggregated Presence (Binary) -> occPre ---
    # 1. Stack location arrays (using 'ind_occPRE')
    loc_stack = np.vstack([p['ind_occPRE'].values for p in people_grids])

    # 2. Convert to Binary Presence (1=Home, 0=Outside)
    presence_binary = (loc_stack == 1).astype(int)

    # 3. Sum vertically (How many people home?)
    occupancy_count = presence_binary.sum(axis=0)

    # 4. Household Binary Status (1 if anyone is home, else 0)
    hh_df['occPre'] = (occupancy_count >= 1).astype(int)

    # P2: keep the raw per-slot headcount (Ruling A denominator input)
    hh_df['occCount'] = occupancy_count
    hh_df['nGrid'] = len(people_grids)

    # --- STEP C: Social Density -> occDensity ---
    # 1. Stack density arrays (using 'ind_density')
    dens_stack = np.vstack([p['ind_density'].values for p in people_grids])

    # 2. Sum vertically
    hh_df['occDensity'] = dens_stack.sum(axis=0)

    # --- STEP D: Aggregated Activity Sets -> occActivity ---
    # 1. Stack activity arrays (using 'ind_occACT')
    act_stack = np.vstack([p['ind_occACT'].values for p in people_grids])

    activity_sets = []

    # Iterate through each time slot (column)
    for t in range(self.slots):
        # Get activities and presence for this moment
        acts_at_t = act_stack[:, t]
        pres_at_t = presence_binary[:, t]  # Only consider people AT HOME

        # Filter: Keep activities only for people who are PRESENT (1)
        valid_acts = acts_at_t[pres_at_t == 1]

        # Get Unique, Sort, Convert to String
        if len(valid_acts) > 0:
            unique_acts = sorted(np.unique(valid_acts))
            # Remove 0 or NaNs if any slipped in
            unique_acts = [str(a) for a in unique_acts if a > 0]
            act_str = ",".join(unique_acts)
        else:
            act_str = "0"  # "0" indicates Unoccupied/No Activity

        activity_sets.append(act_str)

    hh_df['occActivity'] = activity_sets

    return hh_df


def process_households_override(self, df_full):
    """
    Verbatim copy of BEMConverter.process_households
    (previous/eSim_dynamicML_mHead.py:2344-2423) plus WP9 Stage 1c P3: an
    OCC_DENOM environment-variable switch (Ruling A: members at home /
    denominator; NO silent default), exactly as P3 did for the four census
    years (2026-09-19_WP9_stage1b_rebuild.md Patches section). Only the block
    marked "# P3:" replaces the original two formula lines
    (`estimated_count = ...` / `occupancy_sched = (estimated_count / hh_size)...`);
    everything else is the original body unchanged, plus 'occCount': 'mean' and
    'nGrid': 'first' added to the hourly .agg() dict (also P3).

    P5 (tier NaN-safe, from stage1b) is NOT applied here. Read at T1: the 2025
    process_households body (previous/eSim_dynamicML_mHead.py:2344-2423) has NO
    `wd_tier` / `we_tier` / `match_tier = max(wd_tier, we_tier)` line -- 2025's
    converter carries no MATCH_TIER column at all (unlike the four census-year
    *_occToBEM.py converters). There is nothing for P5 to guard against, so no
    P5 override is installed and no P5 line is ever printed for 2025 -- its
    absence in the job log is expected, not a sign the patch failed to run.
    """
    _occ_denom_mode = os.environ.get('OCC_DENOM')
    print(f"P3-2025 converter override: active, OCC_DENOM={_occ_denom_mode}")

    print(f"\n\U0001F680 Starting BEM Conversion (Hourly Resampling)...")

    # 1. Prepare Time Index
    # We need a dummy date to enable resampling
    df_full['datetime'] = pd.to_datetime(df_full['Time_Slot'], format='%H:%M')

    # 2. Map Activities to Watts (Vectorized)
    print("   Mapping metabolic rates...")
    df_full['watts_5min'] = df_full['occActivity'].apply(self._calculate_watts)

    # 3. Group by Household & DayType
    groups = df_full.groupby(['SIM_HH_ID', 'Day_Type'])

    bem_schedules = []

    # List of residential variables to carry over (Added PR)
    target_res_cols = ['DTYPE', 'BEDRM', 'CONDO', 'ROOM', 'REPAIR', 'PR']

    for (hh_id, day_type), group in groups:
        # Get Static Attributes (First row of the group)
        hh_size = group['HHSIZE'].iloc[0]

        # Extract residential vars safely (handle if missing)
        res_data = {}
        for col in target_res_cols:
            val = group[col].iloc[0] if col in group.columns else "Unknown"

            # Apply Mappings
            if col == 'DTYPE':
                val_str = str(int(val)) if pd.notnull(val) and val != "Unknown" else str(val)
                res_data[col] = self.dtype_map.get(val_str, val)
            elif col == 'PR':
                # Map StatCan province code (int) -> census label string.
                try:
                    region_key = str(int(float(val)))
                except (ValueError, TypeError):
                    region_key = "99"
                res_data[col] = self.pr_map.get(region_key, "Others")
            else:
                res_data[col] = val

        # --- HOURLY RESAMPLING ---
        g_indexed = group.set_index('datetime')

        # Resample 5min -> 60min (Mean)
        hourly = g_indexed.resample('60min').agg({
            'occPre': 'mean',       # Fraction of hour home (0.0 - 1.0)
            'occDensity': 'mean',   # Avg social density
            'occCount': 'mean',     # P3: mean per-slot headcount at home
            'nGrid': 'first',       # P3: number of donor grids (people) in this household
            'watts_5min': 'mean'    # Avg metabolic rate
        }).reset_index()

        # --- BEM FORMULAS (P3, Ruling A: members at home / denominator) ---
        # OCC_DENOM selects the denominator; no silent default.
        if _occ_denom_mode == 'grid':
            occupancy_sched = (
                hourly['occCount'] / hourly['nGrid'].replace(0, np.nan)
            ).clip(upper=1.0).fillna(0.0)
        elif _occ_denom_mode == 'hhsize':
            occupancy_sched = (hourly['occCount'] / hh_size).clip(upper=1.0)
        else:
            raise ValueError(
                "OCC_DENOM environment variable must be set to 'grid' or 'hhsize' "
                f"(WP9 Stage 1c P3); got {_occ_denom_mode!r}"
            )

        # 3. Create Result DataFrame
        data_dict = {
            'SIM_HH_ID': hh_id,
            'Day_Type': day_type,
            'Hour': hourly['datetime'].dt.hour,
            'HHSIZE': hh_size,
            **res_data,
            'Occupancy_Schedule': occupancy_sched.round(3),  # 0 to 1
            'Metabolic_Rate': hourly['watts_5min'].round(1)  # Watts
        }

        hourly_df = pd.DataFrame(data_dict)
        bem_schedules.append(hourly_df)

    # Combine
    return pd.concat(bem_schedules, ignore_index=True)


def install_overrides(install_p3=True):
    """
    Imports previous.eSim_dynamicML_mHead UNCHANGED (this is the only place in
    this driver that does so) and monkey-patches HouseholdAggregator's method
    onto it at runtime (always -- P2 only ADDS occCount/nGrid columns; it never
    changes occPre/occDensity/occActivity, so it is harmless for the "original"
    convert path too). BEMConverter.process_households is patched only when
    install_p3=True (--convert grid/hhsize); for --convert original it is left
    completely unedited, on purpose. Never writes to the file on disk. Returns
    the imported module.
    """
    from previous import eSim_dynamicML_mHead as _mh  # noqa: E402  (deferred, deliberate)

    _mh.HouseholdAggregator._aggregate_household = aggregate_household_override
    if install_p3:
        _mh.BEMConverter.process_households = process_households_override
    return _mh


def _add_repo_dirs_to_path():
    # This file is expected to sit directly inside 25CEN22GSS_classification/,
    # beside run_step2.py / run_step3.py / previous/, so that `from previous...`
    # (a namespace package, no __init__.py) resolves exactly as it does when
    # run_step2.py / run_step3.py are run directly from that same directory.
    here = pathlib.Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    sys.path.insert(0, str(here.parent))
    # Job 1339869 (exit 4): `from eSim_occ_utils.occ_config` needs the folder
    # ABOVE eSim_occ_utils on sys.path; run_step2.py:34 / run_step3.py:22 only
    # insert eSim_occ_utils itself. Fixed here, no repo file edited.
    sys.path.insert(0, str(here.parent.parent))
    import eSim_occ_utils.occ_config as _cfg  # noqa: E402
    print(f"IMPORT PATH FIX: occ_config from {_cfg.__file__}; BASE_DIR={_cfg.BASE_DIR}")


def run_from_keys():
    """
    Ruling D-1J-A3 (task doc, "Manager ruling after BLOCKED"): rebuild 2025
    from the April Matched_Population_Keys.csv instead of re-running the
    matcher (MatchProfiler._find_best_match() draws matches.sample(1) with NO
    fixed seed -- previous/eSim_dynamicML_mHead.py:1462-1485 -- so re-matching
    would NOT reproduce the April population).

    Steps, all deterministic downstream of the keys (per the ruling):
      1. read Matched_Population_Keys.csv + Aligned_GSS_2022.csv from
         OUTPUT_DIR_ALIGNED (both uploaded unchanged by T7);
      2. build ScheduleExpander(df_gss, id_col="occID") and call
         generate_full_expansion(df_matched, expander, ...) directly -- exactly
         what run_step2.py:113-117 (run_profile_matcher) does right after its
         own (here skipped) matching call -- to (re)produce
         Full_Expanded_Schedules.csv;
      3. run_step2.run_postprocessing() -- DTypeRefiner, RandomForestClassifier
         (random_state=42, previous/eSim_dynamicML_mHead.py:1779,1791) trained
         on cen06_filtered.csv/cen11_filtered.csv -- produces
         Full_Expanded_Schedules_Refined.csv;
      4. run_step2.run_household_aggregation() (P2 override installed) --
         produces Full_data.csv.
    verify_sample() and the validation plots (run_validate_profile_matcher,
    run_validate_household_aggregation) are skipped -- they are optional
    diagnostics, not on this data path, and skipping them requires no edit to
    any repo file.
    """
    _add_repo_dirs_to_path()
    install_overrides(install_p3=False)  # P2 only; conversion is a separate step

    import run_step2  # noqa: E402

    keys_path = run_step2.OUTPUT_DIR_ALIGNED / "Matched_Population_Keys.csv"
    gss_path = run_step2.OUTPUT_DIR_ALIGNED / "Aligned_GSS_2022.csv"

    print(f"--from-keys: reading matched keys (April, NOT re-matched) from {keys_path}")
    df_matched = pd.read_csv(keys_path, low_memory=False)
    print(f"--from-keys: {len(df_matched):,} matched agents loaded")

    print(f"--from-keys: reading Aligned_GSS_2022.csv from {gss_path}")
    df_gss = pd.read_csv(gss_path, low_memory=False)

    expander = run_step2.ScheduleExpander(df_gss, id_col="occID")
    expanded_path = run_step2.OUTPUT_DIR / "Full_Expanded_Schedules.csv"
    run_step2.generate_full_expansion(df_matched, expander, expanded_path)

    print("--from-keys: running Step 2d postprocessing (DTYPE refinement)...")
    run_step2.run_postprocessing()

    print("--from-keys: running Step 2e household aggregation (P2 override active)...")
    run_step2.run_household_aggregation()

    print("--from-keys: complete (expansion -> refinement -> aggregation)")


def run_convert(mode):
    """
    mode in {"original", "grid", "hhsize"}. Reads Full_data.csv (produced by
    run_from_keys()) and runs run_step3.run_bem_conversion() ONCE per call --
    this function is invoked up to three times by the T8 job script, once per
    mode, each as a separate driver invocation (fresh interpreter, fresh
    class-method state).

    "original": BEMConverter.process_households is left completely UNMODIFIED
    (P3 override NOT installed) -- reproduces the exact formula that produced
    the April BEM_Schedules_2025.csv, used only for the T6 reproduction check.
    "grid"/"hhsize": P3 override installed, OCC_DENOM env var set to `mode`
    before the converter runs (Ruling A grid denominator / hhsize sensitivity
    check).
    """
    if mode not in ("original", "grid", "hhsize"):
        raise ValueError(f"unknown --convert mode {mode!r}; expected original/grid/hhsize")

    _add_repo_dirs_to_path()

    if mode == "original":
        print("P3-2025 converter override: NOT installed (original formula)")
        install_overrides(install_p3=False)
    else:
        os.environ['OCC_DENOM'] = mode
        install_overrides(install_p3=True)

    import run_step3  # noqa: E402
    run_step3.run_bem_conversion()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="WP9 Stage 1c 2025 driver (Ruling D-1J-A3: rebuild from the April keys)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--from-keys', action='store_true',
        help="expansion -> refinement -> aggregation from the April Matched_Population_Keys.csv"
    )
    group.add_argument(
        '--convert', choices=['original', 'grid', 'hhsize'], default=None,
        help="BEM conversion only (reads Full_data.csv); original = unedited formula (repro check), grid/hhsize = Ruling A / sensitivity"
    )
    args = parser.parse_args()

    # Fixed seed so any hidden random draw left in the deterministic downstream
    # path (there should be none besides the RF's own random_state=42) is at
    # least repeatable run to run.
    np.random.seed(20260919)
    print("SEED set: 20260919")

    if args.from_keys:
        run_from_keys()
    else:
        run_convert(args.convert)


if __name__ == "__main__":
    main()
