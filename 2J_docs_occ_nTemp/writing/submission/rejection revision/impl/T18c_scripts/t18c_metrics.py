"""t18c_metrics.py -- Frame v2 reported metrics for one T18c build.

Task doc: 2026-09-15_T18c_wp1_frame_v2.md, Design step 4.
Run after t18c_pipeline.py for the same --build in t18c_job.sh.

Reuses, read-only, without copying code (per the task doc's own instruction
"reuse T18b_scripts/t18b_metrics.py and T18_scripts/collector/
t18_collector_verify.py, never the broken lines of t18_metrics.py"):
  - t18b_metrics.tier_shares / donor_reuse / hh_at_home / donor_type_split
    (import, not copy -- these four functions are generic over their input
    path and need no Frame-v2-specific change).
  - The T12/T18-collector convention for weekday/weekend from DDAY_STRATA
    (1=weekday, 2/3=weekend; t18_collector_verify.py:236-239) for the two
    NEW items this doc's Design section adds that neither t18b_metrics.py
    nor t18_collector_verify.py already compute: the <0.30 household count/
    share by archetype, and the two check-3.5 variants.

Writes CSV/JSON under T18c/out/<build>/. Never writes into T18/ or T18b/.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import sys
T18_SCRIPTS_DIR = Path("/speed-scratch/o_iseri/2J_revision/T18/T18_scripts")
T18B_SCRIPTS_DIR = Path("/speed-scratch/o_iseri/2J_revision/T18b/T18b_scripts")
sys.path.insert(0, str(T18_SCRIPTS_DIR))
sys.path.insert(0, str(T18B_SCRIPTS_DIR))
import t18b_metrics as t18bm  # tier_shares, donor_reuse, hh_at_home, donor_type_split (read-only reuse)

T18_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18")
T18B_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18b")
T18C_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18c")

N_ROWS_EXPECTED = 6_934_320  # published BEM_Schedules_2022.csv row count (design B2)
OBSERVED_2022_ATHOME = 72.3  # 07_bemIntegrationGSS_val.py:80, same anchor, band never moved
CHECK35_BAND_PP = 2.0        # 07_bemIntegrationGSS_val.py:352 ("<= 2")


def build_paths(build):
    out_dir = T18C_ROOT / build / "repo" / "outputs" / "aug_pipeline"
    bems_dir = T18C_ROOT / build / "repo" / "outputs" / "BEM_Setup"
    metrics_out = T18C_ROOT / "out" / build
    metrics_out.mkdir(parents=True, exist_ok=True)
    return out_dir, bems_dir, metrics_out


def matched_keys_path(build):
    """Tier shares (design step 4): 'nf reuses Arm N's Matched_Keys.csv'
    (task doc) -- nf never relinks, so its Tier-1/2/3/4 shares ARE Arm N's
    T18 shares. nbf reuses its own T18b relink output (job 1328333 task 1
    reached STEP OK through run_exclusion() before dying on the old
    frame_filter -- Matched_Keys.csv was already written and is unaffected
    by which frame-filter version runs downstream)."""
    if build == "nf":
        return T18_ROOT / "arm_N" / "repo" / "outputs" / "aug_pipeline" / "21CEN22GSS_aug_Matched_Keys.csv"
    return T18B_ROOT / "nbf" / "repo" / "outputs" / "aug_pipeline" / "21CEN22GSS_aug_Matched_Keys.csv"


def frame_v2_path(build, out_dir):
    return out_dir / "21CEN22GSS_aug_Full_Aggregated_framev2.csv"


def load_json(p):
    if p.exists():
        return json.loads(p.read_text())
    return None


def published_hh_set(published_hh_path=T18_ROOT / "reference" / "BEM_Schedules_2022.csv"):
    pub = pd.read_csv(published_hh_path, usecols=["SIM_HH_ID"])
    return set(pub["SIM_HH_ID"].unique())


def b2_household_set_check(bem_path, published_set):
    """B2 (design step 4): household set of the filtered BEM_Schedules_2022.csv
    equals the published set, both directions 0. Re-derived directly from the
    written BEM output rather than trusting frame_filter_result.json alone --
    that JSON describes the PRE-filter stock's missing/extra counts, not the
    post-filter BEM file this acceptance line actually names."""
    if not bem_path.exists():
        return {"status": "MISSING", "bem_path": str(bem_path)}
    bdf = pd.read_csv(bem_path, usecols=["SIM_HH_ID"], low_memory=False)
    bem_hh = set(bdf["SIM_HH_ID"].unique())
    only_ref = len(published_set - bem_hh)
    only_bem = len(bem_hh - published_set)
    return {
        "n_published": len(published_set), "n_bem_hh": len(bem_hh),
        "only_in_published": only_ref, "only_in_bem": only_bem,
        "both_directions_zero": (only_ref == 0 and only_bem == 0),
    }


def _load_frame_v2_for_athome(fv2_path):
    """Loads the columns needed for the <0.30 archetype breakdown and the
    check-3.5 variants in one pass: HH_ID, DTYPE (archetype, if present),
    the 48 HH_hom30_* (household-level, broadcast per member -- used for the
    per-household <0.30 decision, same formula as run_exclusion()'s own
    hh_means, 05_census_linkage.py:653) and the 48 hom30_* (person-level --
    used for check 3.5, same formula as the validator's own _diary_targets(),
    07_bemIntegrationGSS_val.py:300-308)."""
    header = pd.read_csv(fv2_path, nrows=0).columns.tolist()
    hh_hom_cols = [c for c in header if c.startswith("HH_hom30_")]
    hom_cols = [c for c in header if c.startswith("hom30_")]
    base_cols = [c for c in ["HH_ID", "DTYPE"] if c in header]
    usecols = base_cols + hh_hom_cols + hom_cols
    df = pd.read_csv(fv2_path, usecols=usecols, low_memory=False)
    return df, hh_hom_cols, hom_cols, ("DTYPE" in df.columns)


def at_home_below_030(fv2_path):
    """Count and share of published households (the frame-v2-filtered stock
    IS the 144,465 published households, by construction of frame_filter())
    whose new-diary household at-home mean is < 0.30, per archetype. Same
    threshold/formula as run_exclusion() (05_census_linkage.py:650-658), just
    not applied as an exclusion here -- Frame v2 freezes the stock instead
    (task-doc Why; T18b addendum 1)."""
    df, hh_hom_cols, hom_cols, has_dtype = _load_frame_v2_for_athome(fv2_path)
    if not hh_hom_cols or "HH_ID" not in df.columns:
        return {"status": "NOT AVAILABLE", "reason": "HH_hom30_* or HH_ID column absent from frame-v2 stock"}

    hh = df.drop_duplicates("HH_ID").copy()
    hh["hh_athome_mean"] = hh[hh_hom_cols].mean(axis=1, skipna=True)
    below = hh[hh["hh_athome_mean"] < 0.30]
    n_total = len(hh)
    n_below = len(below)
    out = {
        "n_published_households": n_total,
        "n_below_030": n_below,
        "share_below_030_pct": 100.0 * n_below / n_total if n_total else None,
    }
    if has_dtype:
        by_arch = []
        for arch, g in hh.groupby("DTYPE"):
            n_arch = len(g)
            n_arch_below = int((g["hh_athome_mean"] < 0.30).sum())
            by_arch.append({
                "archetype": str(arch), "n_households": n_arch,
                "n_below_030": n_arch_below,
                "share_below_030_pct": 100.0 * n_arch_below / n_arch if n_arch else None,
            })
        out["by_archetype"] = by_arch
    else:
        out["by_archetype"] = "NOT AVAILABLE: no DTYPE column in frame-v2 stock"
    return out


def check_3_5_variants(fv2_path):
    """Check 3.5 (07_bemIntegrationGSS_val.py:350-357) on two subsets of the
    Frame-v2-filtered stock: (a) the full frame -- this is the SAME AUG file
    t18c_pipeline.py's run_a2b_and_validator() already points the validator
    at, so this variant should numerically match Section 3.5 of
    validator_result.json (not cross-checked here, see WHAT I DID NOT
    VERIFY); (b) the frame minus households whose new-diary at-home mean is
    < 0.30 (the households that would have been excluded under a fresh
    build) -- computed here directly rather than by re-running a2b/validator
    a second time, since check 3.5 depends only on the diary AUG file's
    hom30_* columns, not on the BEM_Schedules_2022.csv the validator also
    loads (07_bemIntegrationGSS_val.py:161-171). Reported per the task doc's
    "never move the band" rule -- PASS/FAIL is informational, not gating."""
    df, hh_hom_cols, hom_cols, _ = _load_frame_v2_for_athome(fv2_path)
    if not hom_cols:
        return {"status": "NOT AVAILABLE", "reason": "hom30_* columns absent from frame-v2 stock"}

    def variant(sub_df, label):
        overall = float(sub_df[hom_cols].values.mean()) * 100.0
        delta = abs(overall - OBSERVED_2022_ATHOME)
        return {
            "variant": label, "n_rows": int(len(sub_df)),
            "pop_at_home_pct": overall, "anchor_pct": OBSERVED_2022_ATHOME,
            "delta_pp": delta, "band_pp": CHECK35_BAND_PP,
            "status": "PASS" if delta <= CHECK35_BAND_PP else "FAIL",
        }

    out = {"full_frame": variant(df, "full_frame")}

    if hh_hom_cols and "HH_ID" in df.columns:
        hh = df.drop_duplicates("HH_ID")[["HH_ID"] + hh_hom_cols].copy()
        hh["hh_athome_mean"] = hh[hh_hom_cols].mean(axis=1, skipna=True)
        below_ids = set(hh.loc[hh["hh_athome_mean"] < 0.30, "HH_ID"])
        minus_df = df[~df["HH_ID"].isin(below_ids)]
        out["minus_below_030"] = variant(minus_df, "minus_below_030")
        out["minus_below_030"]["n_households_excluded"] = len(below_ids)
    else:
        out["minus_below_030"] = {"status": "NOT AVAILABLE",
                                   "reason": "HH_hom30_* or HH_ID column absent"}
    return out


def validator_summary(out_dir):
    vj = load_json(out_dir / "validator_result.json")
    if not vj:
        return {"counts": "MISSING", "results": None}
    return {"counts": vj["counts"], "results": vj["results"]}


def b2_from_household_count_checks(validator_results):
    """Validator's own household-count checks (Section 1.2/1.3 etc), same
    message-substring filter t18b_metrics.py used."""
    if not validator_results:
        return None
    hh_fail = [m for m in validator_results.get("fail", [])
               if ("Households" in m or "Row count" in m or "MATCH_TIER" in m
                   or "DTYPE" in m or "PR " in m)]
    hh_seen = [m for lvl in ("pass", "fail") for m in validator_results.get(lvl, [])
               if ("Households" in m or "Row count" in m or "MATCH_TIER" in m
                   or "DTYPE" in m or "PR " in m)]
    return {"seen": hh_seen, "pass": (len(hh_fail) == 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", choices=["nf", "nbf"], required=True)
    args = ap.parse_args()
    build = args.build

    out_dir, bems_dir, metrics_out = build_paths(build)
    report = {"build": build, "frame_version": "v2 (pre-exclusion stock filtered to published HH set)"}

    published_set = published_hh_set()

    # --- tier shares + donor reuse (reused from t18b_metrics.py) ------------
    mk_path = matched_keys_path(build)
    tiers, n_total_tier, n_tier1 = t18bm.tier_shares(mk_path)
    report["tier_shares"] = tiers
    report["n_total_agents"] = n_total_tier
    report["n_tier1"] = n_tier1
    report["tier1_pct"] = 100.0 * n_tier1 / n_total_tier if n_total_tier else None
    report["donor_reuse"] = t18bm.donor_reuse(mk_path)

    # --- 7-key-equivalent share (nbf only; unchanged by Frame v2, reused
    #     read-only from the T18b run that already computed it) -------------
    seven_key_path = T18B_ROOT / "out" / "nbf" / "tier1_7key_equivalent.json"
    report["tier1_7key_equivalent"] = (
        load_json(seven_key_path) if build == "nbf" else "n/a (N-f does not relink)")

    # --- household weekday/weekend at-home, national + archetype (reused) --
    bem_path = bems_dir / "BEM_Schedules_2022.csv"
    if bem_path.exists():
        hh_rows, n_hh_final = t18bm.hh_at_home(bem_path)
        report["hh_at_home"] = hh_rows
        report["n_hh_final"] = n_hh_final
        report["bem_row_count"] = int(sum(1 for _ in open(bem_path, "rb")) - 1)
    else:
        report["hh_at_home"] = "MISSING: BEM_Schedules_2022.csv not found"
        report["n_hh_final"] = None
        report["bem_row_count"] = None

    # --- donor-type at-home split + weighted real-2022 (reused) -------------
    fv2 = frame_v2_path(build, out_dir)
    if fv2.exists():
        report["donor_type_at_home_split"] = t18bm.donor_type_split(fv2)
    else:
        report["donor_type_at_home_split"] = {"status": "NOT AVAILABLE", "reason": f"{fv2} not found"}

    # --- NEW: <0.30 household count/share by archetype ----------------------
    if fv2.exists():
        report["below_030_households"] = at_home_below_030(fv2)
    else:
        report["below_030_households"] = {"status": "NOT AVAILABLE", "reason": f"{fv2} not found"}

    # --- NEW: check 3.5, full frame and minus-below-0.30 ---------------------
    if fv2.exists():
        report["check_3_5"] = check_3_5_variants(fv2)
    else:
        report["check_3_5"] = {"status": "NOT AVAILABLE", "reason": f"{fv2} not found"}

    # --- validator pass/warn/fail counts -------------------------------------
    vsum = validator_summary(out_dir)
    report["validator"] = vsum["counts"]

    # --- B2: frame filter correctness + household-set equality --------------
    ff = load_json(out_dir / "frame_filter_result.json")
    b2 = {"frame_filter_result_v2": ff}  # pre-filter missing/extra on the raw source stock
    b2["household_set_check"] = b2_household_set_check(bem_path, published_set)
    b2["bem_row_count_expected"] = N_ROWS_EXPECTED
    b2["bem_row_count_actual"] = report["bem_row_count"]
    b2["row_count_match"] = (report["bem_row_count"] == N_ROWS_EXPECTED
                              if report["bem_row_count"] is not None else None)
    hh_checks = b2_from_household_count_checks(vsum["results"])
    b2["validator_household_count_checks"] = hh_checks
    report["B2"] = b2

    # --- B5: read back what t18c_pipeline.py recorded ------------------------
    b5 = load_json(out_dir / "b5_source_md5.json")
    report["B5"] = b5 if b5 else "MISSING: b5_source_md5.json not written (pipeline step may not have completed)"

    out_json = metrics_out / f"t18c_metrics_{build}.json"
    out_json.write_text(json.dumps(report, indent=2, default=str))
    print(f"[t18c_metrics] wrote {out_json}")

    pd.DataFrame(tiers).to_csv(metrics_out / f"t18c_tier_shares_{build}.csv", index=False)
    if isinstance(report["hh_at_home"], list):
        pd.DataFrame(report["hh_at_home"]).to_csv(
            metrics_out / f"t18c_hh_at_home_{build}.csv", index=False)
    if isinstance(report["below_030_households"], dict) and isinstance(
            report["below_030_households"].get("by_archetype"), list):
        pd.DataFrame(report["below_030_households"]["by_archetype"]).to_csv(
            metrics_out / f"t18c_below_030_by_archetype_{build}.csv", index=False)

    print(f"[t18c_metrics] DONE build={build}")


if __name__ == "__main__":
    main()
