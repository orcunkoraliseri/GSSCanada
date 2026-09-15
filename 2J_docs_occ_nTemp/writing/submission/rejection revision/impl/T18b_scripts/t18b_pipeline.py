"""t18b_pipeline.py -- T18b chain orchestrator for ONE build (N-f or Nb-f).

Task doc: 2026-09-15_T18b_wp1_linkage_lever_and_frozen_frame.md.
Parent:   2026-09-15_T18_wp1_rebuild_2022_build.md (T18b reuses T18's staged
          trees under /speed-scratch/o_iseri/2J_revision/T18/ as READ-ONLY
          input; T18b writes only under
          /speed-scratch/o_iseri/2J_revision/T18b/).

Two builds (design, fixed):
  N-f  = existing Arm N excl stock (T18/arm_N, already computed, no relink)
         -> frame filter to the published HH_ID set -> 07_aug_to_bem.py
         --year 2022 -> validator.
  Nb-f = full T18 chain (linkage --full --region-tier -> rake --joint ->
         --aggregate -> --bem -> --exclusion) run fresh on Arm N's 2022-only
         diaries (T18/arm_N/repo/inputs/augmented_diaries.csv, read-only)
         WITH the CMA lever applied to Tier-1 -> frame filter -> a2b ->
         validator.

CMA lever (design, fixed): Tier-1 key set becomes AGEGRP, SEX, MARSTH,
HHSIZE, LFTAG, PR, DDAY_STRATA (CMA dropped). Implemented by replacing
run_slot_match on the freshly-loaded 05_census_linkage module with a thin
wrapper that strips "CMA" out of the match_keys argument and calls the
original function -- the module-level MATCH_KEYS constant itself is left
untouched, because _POOL_EXCLUDE (05_census_linkage.py:93) and
expand_slot_schedules()'s cen_demog list (:258) are both computed from
MATCH_KEYS and must keep excluding/including CMA as a CENSUS-side
demographic passthrough column regardless of the lever -- only the Tier-1
MATCH key set changes. This works because run_linkage_full() (:381) calls
`run_slot_match(...)` as a bare global name, resolved against the module's
own globals dict at call time (LOAD_GLOBAL), so patching
`linkage_mod.run_slot_match = wrapper` after the module is loaded but before
run_linkage_full() is invoked redirects that call without touching any
function body. Call site confirmed: 05_census_linkage.py:381
  `df_matched = run_slot_match(df_census_dday, df_pool, MATCH_KEYS,
                                DDAY_COL, region_tier=region_tier)`
-- MATCH_KEYS (05_census_linkage.py:75) is passed positionally as match_keys,
exactly as the design's wrapper text describes.

Frozen household frame (design, fixed): after each build's own stock is
ready (pre-filter Full_Aggregated_excl.csv), filter it to the published
144,465 HH_ID set from T18/reference/BEM_Schedules_2022.csv's SIM_HH_ID
column (07_aug_to_bem.py:94 renames HH_ID -> SIM_HH_ID, so the two columns
share one value space -- confirmed by reading 07_aug_to_bem.py directly).
If any published HH_ID is missing from the build's own stock, the job
writes the unfiltered stock plus missing_hh.csv and exits non-zero; nothing
is filled in (design, fixed).

Exclusion rule recorded (Decisions, task doc step 1): run_exclusion()
(05_census_linkage.py:639-698, Sub-step 5H) drops PP_IDs whose PER-HOUSEHOLD
mean AT_HOME across the 48 HH_hom30_* slots is < 0.30 (:650-658), then
propagates that same PP_ID exclusion set identically to Full_Schedules_excl,
Full_Aggregated_excl and BEM_Schedules_excl (:671-680). The 0.30 threshold
and the code are IDENTICAL between Arm C and Arm N -- there is no different
rule. What differs is which diary each household's members got matched to
upstream (run_slot_match), because Arm N's donor pool is 2022-only (and,
for Nb-f, additionally drops CMA from Tier-1); a different matched diary
gives a different per-household 48-slot at-home mean, so a different set of
households ends up on each side of the fixed 0.30 line. The "164 extra
households" in Arm N's published-stock comparison is this same mechanism,
not a second rule -- reported both directions by the frame-filter step
below (extra = arm HH not in the published set; missing = published HH not
in the arm's stock).
"""
import sys
import os
import json
import time
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

T18_SCRIPTS_DIR = Path("/speed-scratch/o_iseri/2J_revision/T18/T18_scripts")
sys.path.insert(0, str(T18_SCRIPTS_DIR))
import t18_pipeline as t18p  # reuse _load_module/_md5/_report_file/log/_step (T18, read-only)

T18_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18")
T18B_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18b")
PUBLISHED_HH_DEFAULT = T18_ROOT / "reference" / "BEM_Schedules_2022.csv"

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def _step(name, fn):
    log(f"--- STEP START: {name} ---")
    try:
        fn()
    except Exception:
        log(f"--- STEP FAILED: {name} ---")
        raise
    log(f"--- STEP OK: {name} ---")


# ---------------------------------------------------------------------------
# CMA lever: wrap run_slot_match on the loaded 05_census_linkage module.
# ---------------------------------------------------------------------------
def apply_cma_lever(linkage_mod, out_dir):
    """Replaces linkage_mod.run_slot_match with a wrapper that strips CMA
    from match_keys before calling the original. Also captures the
    7-key-equivalent Tier-1 donor-CMA-vs-census-CMA comparison (design,
    "Reported, not banded") while _pool_idx is still present on the
    wrapper's own return value -- run_linkage_full() drops _pool_idx before
    writing Matched_Keys.csv (05_census_linkage.py:389-391), so this is the
    only point in the chain where it is recoverable without re-matching.
    """
    original = linkage_mod.run_slot_match

    def run_slot_match_cma_lever(df_census, df_pool, match_keys,
                                  dday_col="DDAY_STRATA", region_tier=False):
        new_keys = [k for k in match_keys if k != "CMA"]
        log(f"  [lever=cma] Tier-1 match_keys: {match_keys} -> {new_keys}")
        df_matched = original(df_census, df_pool, new_keys, dday_col,
                               region_tier=region_tier)

        seven_key_path = out_dir / "tier1_7key_equivalent.json"
        try:
            if "CMA" in df_pool.columns and "CMA" in df_census.columns:
                tier1 = df_matched[df_matched["MATCH_TIER"] == "1_Perfect"]
                pool_cma = df_pool.loc[tier1["_pool_idx"].to_numpy(), "CMA"].to_numpy()
                census_cma = (
                    df_census.set_index("PP_ID")
                    .loc[tier1["PP_ID"], "CMA"].to_numpy()
                )
                match_mask = (pool_cma == census_cma)
                n_match = int(np.nansum(match_mask))
                n_tier1 = int(len(tier1))
                n_all = int(len(df_census))
                payload = {
                    "n_tier1": n_tier1, "n_donor_cma_eq_census_cma": n_match,
                    "n_all_agents": n_all,
                    "pct_of_tier1": 100.0 * n_match / n_tier1 if n_tier1 else None,
                    "pct_of_all_agents": 100.0 * n_match / n_all if n_all else None,
                    "note": ("comparable with Arm C's 44.94% Tier-1 share "
                             "(pct_of_all_agents is the 7-key-equivalent number)"),
                }
                out_dir.mkdir(parents=True, exist_ok=True)
                seven_key_path.write_text(json.dumps(payload, indent=2))
                log(f"  [7-key-equiv] {payload}")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                seven_key_path.write_text(json.dumps({"status": "NOT AVAILABLE",
                    "reason": "CMA column absent from pool and/or census frame"}, indent=2))
                log("  [7-key-equiv] CMA column missing -- NOT AVAILABLE")
        except Exception as e:
            log(f"  [7-key-equiv] FAILED to compute ({e!r}); not gating, continuing")

        return df_matched

    linkage_mod.run_slot_match = run_slot_match_cma_lever


# ---------------------------------------------------------------------------
# Frozen household frame filter.
# ---------------------------------------------------------------------------
def frame_filter(agg_excl_path, published_hh_path, out_path, missing_csv_path):
    log(f"=== Frame filter: {agg_excl_path.name} against published HH set ===")
    published = pd.read_csv(published_hh_path, usecols=["SIM_HH_ID"])
    published_hh = set(published["SIM_HH_ID"].unique())
    log(f"  published HH set: {len(published_hh):,} households (from {published_hh_path})")

    agg = pd.read_csv(agg_excl_path, low_memory=False)
    arm_hh = set(agg["HH_ID"].unique())
    log(f"  arm stock: {len(agg):,} rows, {len(arm_hh):,} unique HH_ID")

    missing = published_hh - arm_hh   # published HH_ID absent from this build's stock
    extra = arm_hh - published_hh     # this build's HH_ID not in the published set
    log(f"  missing (published not in build) = {len(missing):,}; "
        f"extra (build not in published) = {len(extra):,}")

    result = {
        "published_n": len(published_hh), "arm_n": len(arm_hh),
        "missing_n": len(missing), "extra_n": len(extra),
    }

    if missing:
        unfiltered_path = out_path.parent / (out_path.stem + "_UNFILTERED.csv")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        agg.to_csv(unfiltered_path, index=False)
        pd.DataFrame({"HH_ID": sorted(missing)}).to_csv(missing_csv_path, index=False)
        log(f"  [FRAME-FILTER FAIL] {len(missing)} published HH_IDs missing from this "
            f"build's stock. Wrote unfiltered stock -> {unfiltered_path} and "
            f"missing HH list -> {missing_csv_path}. Nothing filled in. Exiting non-zero.")
        result["status"] = "FAIL_MISSING_HH"
        result_path = out_path.parent / "frame_filter_result.json"
        result_path.write_text(json.dumps(result, indent=2))
        sys.exit(3)

    filtered = agg[agg["HH_ID"].isin(published_hh)].copy()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(out_path, index=False)
    result["status"] = "OK"
    result_path = out_path.parent / "frame_filter_result.json"
    result_path.write_text(json.dumps(result, indent=2))
    log(f"  frame-filtered stock written: {len(filtered):,} rows, "
        f"{filtered['HH_ID'].nunique():,} unique HH -> {out_path}")
    return result


# ---------------------------------------------------------------------------
# Shared tail: 07_aug_to_bem.py --year 2022 -> validator, on a given AUG file.
# ---------------------------------------------------------------------------
def run_a2b_and_validator(scripts_dir, aug_path, bems_dir, out_dir):
    a2b = t18p._load_module("t18b_a2b", scripts_dir / "07_aug_to_bem.py")
    a2b.AUG = aug_path
    a2b.BEMS = bems_dir

    def _run_a2b():
        old_argv = sys.argv
        sys.argv = ["07_aug_to_bem.py", "--year", "2022"]
        try:
            a2b.main()
        finally:
            sys.argv = old_argv

    _step("a2b.main() --year 2022", _run_a2b)

    bval = t18p._load_module("t18b_bval", scripts_dir / "07_bemIntegrationGSS_val.py")
    bval.BEMS = bems_dir
    bval.AUG = aug_path

    validator_holder = {}

    def _run_bval():
        validator = bval.BEMIntegrationValidator(
            year="2022", outputs_dir=str(out_dir / "outputs_step7"))
        validator.run_all()
        validator_holder["v"] = validator
        # results captured in-process (validator.results is not otherwise
        # dumped to a machine-readable file -- only printed to stdout and
        # baked into the HTML report), so write it out directly here rather
        # than re-parsing the HTML/log later.
        counts = {lvl: len(msgs) for lvl, msgs in validator.results.items()}
        payload = {"counts": counts, "results": validator.results}
        (out_dir / "validator_result.json").write_text(json.dumps(payload, indent=2))
        log(f"  validator counts: {counts}")

    _step("BEMIntegrationValidator(year=2022).run_all()", _run_bval)
    return validator_holder.get("v")


# ---------------------------------------------------------------------------
# Build N-f: existing Arm N excl stock, no relink.
# ---------------------------------------------------------------------------
def run_nf(published_hh_path):
    build_dir = T18B_ROOT / "nf"
    scripts_dir = build_dir / "repo" / "scripts"
    out_dir = build_dir / "repo" / "outputs" / "aug_pipeline"
    bems_dir = build_dir / "repo" / "outputs" / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    log("=========== BUILD N-f (no relink) ===========")
    source_agg_excl = (T18_ROOT / "arm_N" / "repo" / "outputs" / "aug_pipeline"
                        / "21CEN22GSS_aug_Full_Aggregated_excl.csv")
    log(f"Source (read-only, T18 output): {source_agg_excl}")

    filtered_path = out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
    missing_csv = out_dir / "missing_hh.csv"

    _step("frame_filter(Arm N excl stock)",
          lambda: frame_filter(source_agg_excl, published_hh_path,
                                filtered_path, missing_csv))

    _step("a2b + validator on frame-filtered Arm N stock",
          lambda: run_a2b_and_validator(scripts_dir, filtered_path, bems_dir, out_dir))

    log("=========== BUILD N-f COMPLETE ===========")


# ---------------------------------------------------------------------------
# Build Nb-f: full chain on Arm N's 2022-only diaries, with the CMA lever.
# ---------------------------------------------------------------------------
def run_nbf(published_hh_path):
    build_dir = T18B_ROOT / "nbf"
    scripts_dir = build_dir / "repo" / "scripts"
    out_dir = build_dir / "repo" / "outputs" / "aug_pipeline"
    bems_dir = build_dir / "repo" / "outputs" / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    log("=========== BUILD Nb-f (relink, CMA lever) ===========")
    diaries_path = T18_ROOT / "arm_N" / "repo" / "inputs" / "augmented_diaries.csv"
    census_path = T18_ROOT / "input" / "Aligned_Census_2022.csv"
    log("Input files (read-only, from T18):")
    t18p._report_file(diaries_path)
    t18p._report_file(census_path)

    linkage = t18p._load_module("t18b_linkage_nbf", scripts_dir / "05_census_linkage.py")
    linkage.AUGMENTED_DIARIES = diaries_path
    linkage.CENSUS_FILE = census_path
    linkage.OUT_DIR = out_dir
    apply_cma_lever(linkage, T18B_ROOT / "out" / "nbf")

    _step("linkage.run_linkage_full(region_tier=True) [CMA lever active]",
          lambda: linkage.run_linkage_full(region_tier=True))

    rake = t18p._load_module("t18b_rake_nbf", scripts_dir / "05_postlink_rake.py")
    rake._FULL_SCHED_PATH = out_dir / "21CEN22GSS_aug_Full_Schedules.csv"
    rake._MATCHED_KEYS_PATH = out_dir / "21CEN22GSS_aug_Matched_Keys.csv"
    _step("rake.main_joint()", rake.main_joint)

    _step("linkage.run_aggregate()", linkage.run_aggregate)
    _step("linkage.run_bem()", linkage.run_bem)
    _step("linkage.run_exclusion()", linkage.run_exclusion)

    log("Pre-filter output files (md5 + size):")
    for p in [
        out_dir / "21CEN22GSS_aug_Full_Schedules.csv",
        out_dir / "21CEN22GSS_aug_Matched_Keys.csv",
        out_dir / "21CEN22GSS_aug_Full_Aggregated.csv",
        out_dir / "21CEN22GSS_aug_BEM_Schedules.csv",
        out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv",
    ]:
        t18p._report_file(p)

    filtered_path = out_dir / "21CEN22GSS_aug_Full_Aggregated_excl_framefiltered.csv"
    missing_csv = out_dir / "missing_hh.csv"
    _step("frame_filter(Nb-f pre-filter stock)",
          lambda: frame_filter(out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv",
                                published_hh_path, filtered_path, missing_csv))

    _step("a2b + validator on frame-filtered Nb-f stock",
          lambda: run_a2b_and_validator(scripts_dir, filtered_path, bems_dir, out_dir))

    log("=========== BUILD Nb-f COMPLETE ===========")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", choices=["nf", "nbf"], required=True)
    ap.add_argument("--lever", choices=["none", "cma"], default=None,
                     help="nf ignores this (no relink); nbf defaults to cma")
    ap.add_argument("--frame-filter", default=str(PUBLISHED_HH_DEFAULT),
                     help="path to the published-HH source file (SIM_HH_ID column)")
    args = ap.parse_args()

    published_hh_path = Path(args.frame_filter)

    if args.build == "nf":
        if args.lever not in (None, "none"):
            log(f"[warn] --lever={args.lever} ignored: N-f does not relink")
        run_nf(published_hh_path)
    else:
        lever = args.lever or "cma"
        if lever != "cma":
            raise SystemExit(f"Nb-f requires --lever cma (design, fixed); got {lever!r}")
        run_nbf(published_hh_path)


if __name__ == "__main__":
    main()
