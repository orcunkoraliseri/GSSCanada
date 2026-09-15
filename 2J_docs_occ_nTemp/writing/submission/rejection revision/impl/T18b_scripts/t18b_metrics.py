"""t18b_metrics.py -- reported items + B2/B3/B5 checks for one T18b build.

Task doc: 2026-09-15_T18b_wp1_linkage_lever_and_frozen_frame.md, Brief step 2.
Run after t18b_pipeline.py for the same --build in t18b_job.sh. Reads only
files that build's own pipeline run wrote (plus, for N-f, Arm N's read-only
Matched_Keys.csv from T18, since N-f does not relink). Writes CSV/JSON under
T18b/out/<build>/. Never writes into T18 or T18/reference (N3).

B2/B3/B5 here are REPORTED VERDICTS for the collector to read and re-derive
from, per feedback_verify_progress_log_claims.md -- this script does not
gate or stop the job; the choice rule itself is applied by the collector
per the task doc's Next section.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

T18_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18")
T18B_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18b")

N_ROWS_EXPECTED = 6_934_320  # published BEM_Schedules_2022.csv row count (design B2)
ARM_N_TIER1_N = 85_256       # Arm N's own Tier-1 count (T18 doc Verified), for B3


def build_paths(build):
    build_dir = T18B_ROOT / build
    out_dir = build_dir / "repo" / "outputs" / "aug_pipeline"
    bems_dir = build_dir / "repo" / "outputs" / "BEM_Setup"
    metrics_out = T18B_ROOT / "out" / build
    metrics_out.mkdir(parents=True, exist_ok=True)
    return build_dir, out_dir, bems_dir, metrics_out


def matched_keys_path(build, out_dir):
    if build == "nf":
        # N-f does not relink -- its tier shares ARE Arm N's tier shares.
        # Read-only reuse of T18's own output (never written by T18b).
        return T18_ROOT / "arm_N" / "repo" / "outputs" / "aug_pipeline" / "21CEN22GSS_aug_Matched_Keys.csv"
    return out_dir / "21CEN22GSS_aug_Matched_Keys.csv"


def frame_input_path(build, out_dir):
    """The (pre-filter) Full_Aggregated_excl.csv used as frame_filter()'s input,
    for the donor-type at-home split (Check 3.5 addendum)."""
    if build == "nf":
        return T18_ROOT / "arm_N" / "repo" / "outputs" / "aug_pipeline" / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
    return out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv"


def tier_shares(mk_path):
    mk = pd.read_csv(mk_path, usecols=["MATCH_TIER"])
    n = len(mk)
    counts = mk["MATCH_TIER"].value_counts()
    rows = [{"tier": t, "n": int(c), "pct_of_all": 100.0 * c / n}
            for t, c in counts.items()]
    return rows, n, int(counts.get("1_Perfect", 0))


def donor_reuse(mk_path):
    mk = pd.read_csv(mk_path, usecols=["occID", "DDAY_STRATA"])
    reuse = mk.groupby(["occID", "DDAY_STRATA"]).size()
    return {
        "n_distinct_donor_tuples": int(reuse.shape[0]),
        "max_uses": float(reuse.max()),
        "p99_uses": float(np.percentile(reuse.values, 99)),
    }


def hh_at_home(bem_path):
    bdf = pd.read_csv(bem_path, usecols=["SIM_HH_ID", "Day_Type", "DTYPE",
                                          "Occupancy_Schedule"], low_memory=False)
    rows = []
    for dt_label, dt_key in (("weekday", "Weekday"), ("weekend", "Weekend")):
        sub = bdf[bdf.Day_Type == dt_key]
        rows.append({"day_type": dt_label, "cell": "national",
                     "at_home_pct": sub.Occupancy_Schedule.mean() * 100.0,
                     "n_hh": int(sub.SIM_HH_ID.nunique())})
        for arch, g in sub.groupby("DTYPE"):
            rows.append({"day_type": dt_label, "cell": str(arch),
                         "at_home_pct": g.Occupancy_Schedule.mean() * 100.0,
                         "n_hh": int(g.SIM_HH_ID.nunique())})
    return rows, bdf["SIM_HH_ID"].nunique()


def donor_type_split(agg_excl_path):
    """Check 3.5 addendum: stock at-home by donor type (real vs synthetic),
    and weighted real-2022 at-home if a survey weight column exists."""
    header = pd.read_csv(agg_excl_path, nrows=0).columns.tolist()
    hom_cols = [c for c in header if c.startswith("hom30_")]
    base_cols = [c for c in ["PP_ID", "CYCLE_YEAR", "IS_SYNTHETIC", "WGHT_PER",
                              "DDAY_STRATA"] if c in header]
    usecols = base_cols + hom_cols
    df = pd.read_csv(agg_excl_path, usecols=usecols, low_memory=False)
    if not hom_cols or "IS_SYNTHETIC" not in df.columns:
        return {"status": "NOT AVAILABLE", "reason": "hom30_* or IS_SYNTHETIC column absent"}

    df["row_home_pct"] = df[hom_cols].mean(axis=1, skipna=True) * 100.0
    out = {}
    for is_syn, label in ((0, "real"), (1, "synthetic")):
        sub = df[df["IS_SYNTHETIC"] == is_syn]
        out[f"{label}_unweighted_pct"] = float(sub["row_home_pct"].mean()) if len(sub) else None
        out[f"{label}_n"] = int(len(sub))

    if "WGHT_PER" in df.columns and "CYCLE_YEAR" in df.columns:
        real22 = df[(df["IS_SYNTHETIC"] == 0) & (df["CYCLE_YEAR"] == 2022)]
        if len(real22) and real22["WGHT_PER"].notna().any():
            w = real22["WGHT_PER"].astype(float)
            v = real22["row_home_pct"].astype(float)
            out["weighted_real_2022_pct"] = float(np.sum(v * w) / np.sum(w))
            out["weighted_real_2022_n"] = int(len(real22))
        else:
            out["weighted_real_2022_pct"] = "NOT AVAILABLE"
            out["weighted_real_2022_reason"] = "no non-null WGHT_PER on real-2022 rows"
    else:
        out["weighted_real_2022_pct"] = "NOT AVAILABLE"
        out["weighted_real_2022_reason"] = "no WGHT_PER/CYCLE_YEAR column in this file"
    return out


def load_json(p):
    if p.exists():
        return json.loads(p.read_text())
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", choices=["nf", "nbf"], required=True)
    args = ap.parse_args()
    build = args.build

    build_dir, out_dir, bems_dir, metrics_out = build_paths(build)
    report = {"build": build}

    # --- reported: tier shares + donor reuse -------------------------------
    mk_path = matched_keys_path(build, out_dir)
    tiers, n_total_tier, n_tier1 = tier_shares(mk_path)
    report["tier_shares"] = tiers
    report["n_total_agents"] = n_total_tier
    report["n_tier1"] = n_tier1
    report["tier1_pct"] = 100.0 * n_tier1 / n_total_tier if n_total_tier else None
    report["donor_reuse"] = donor_reuse(mk_path)

    # --- reported: 7-key-equivalent share (Nb-f only; written by pipeline) --
    seven_key_path = (T18B_ROOT / "out" / "nbf" / "tier1_7key_equivalent.json")
    report["tier1_7key_equivalent"] = load_json(seven_key_path) if build == "nbf" else "n/a (N-f does not relink)"

    # --- reported: household weekday/weekend at-home, national + archetype -
    bem_path = bems_dir / "BEM_Schedules_2022.csv"
    if bem_path.exists():
        hh_rows, n_hh_final = hh_at_home(bem_path)
        report["hh_at_home"] = hh_rows
        report["n_hh_final"] = n_hh_final
        report["bem_row_count"] = int(sum(1 for _ in open(bem_path, "rb")) - 1)
    else:
        report["hh_at_home"] = "MISSING: BEM_Schedules_2022.csv not found"
        report["n_hh_final"] = None
        report["bem_row_count"] = None

    # --- reported: Check 3.5 addendum, donor-type at-home split -------------
    frame_in = frame_input_path(build, out_dir)
    if frame_in.exists():
        report["donor_type_at_home_split"] = donor_type_split(frame_in)
    else:
        report["donor_type_at_home_split"] = {"status": "NOT AVAILABLE",
                                                "reason": f"{frame_in} not found"}

    # --- reported: validator pass/warn/fail counts --------------------------
    validator_json = load_json(out_dir / "validator_result.json")
    report["validator"] = validator_json["counts"] if validator_json else "MISSING"

    # --- B2: frame filter correctness ---------------------------------------
    ff = load_json(out_dir / "frame_filter_result.json")
    b2 = {"frame_filter_result": ff}
    if ff:
        b2["missing_and_extra_both_zero"] = (ff["missing_n"] == 0 and ff["extra_n"] == 0)
    b2["bem_row_count_expected"] = N_ROWS_EXPECTED
    b2["bem_row_count_actual"] = report["bem_row_count"]
    b2["row_count_match"] = (report["bem_row_count"] == N_ROWS_EXPECTED
                              if report["bem_row_count"] is not None else None)
    if validator_json:
        hh_count_msgs = [m for lvl in ("pass", "fail") for m in validator_json["results"].get(lvl, [])
                          if ("Households" in m or "Row count" in m or "MATCH_TIER" in m
                              or "DTYPE" in m or "PR " in m)]
        hh_fail_msgs = [m for m in validator_json["results"].get("fail", [])
                        if ("Households" in m or "Row count" in m or "MATCH_TIER" in m
                            or "DTYPE" in m or "PR " in m)]
        b2["household_count_checks_seen"] = hh_count_msgs
        b2["household_count_checks_pass"] = (len(hh_fail_msgs) == 0)
    else:
        b2["household_count_checks_pass"] = None
    report["B2"] = b2

    # --- B3: lever took effect (Nb-f only) -----------------------------------
    if build == "nbf":
        report["B3"] = {
            "arm_n_tier1_n": ARM_N_TIER1_N,
            "nbf_tier1_n": n_tier1,
            "differs": (n_tier1 != ARM_N_TIER1_N),
        }
    else:
        report["B3"] = "n/a (N-f does not relink)"

    # --- B5: no leakage (this job never writes into T18/) -------------------
    report["B5"] = {
        "note": ("t18b_pipeline.py/t18b_metrics.py write only under "
                 f"{T18B_ROOT} and read T18/* read-only; no md5 recomputation "
                 "of T18/reference/* performed here -- collector re-verifies "
                 "against the Ledger's before-md5s per N3, same as T18.")
    }

    out_json = metrics_out / f"t18b_metrics_{build}.json"
    out_json.write_text(json.dumps(report, indent=2, default=str))
    print(f"[t18b_metrics] wrote {out_json}")

    # flat CSV for the tier shares (convenience, per B4's "tier ... numbers")
    pd.DataFrame(tiers).to_csv(metrics_out / f"t18b_tier_shares_{build}.csv", index=False)
    if isinstance(report["hh_at_home"], list):
        pd.DataFrame(report["hh_at_home"]).to_csv(
            metrics_out / f"t18b_hh_at_home_{build}.csv", index=False)

    print(f"[t18b_metrics] DONE build={build}")


if __name__ == "__main__":
    main()
