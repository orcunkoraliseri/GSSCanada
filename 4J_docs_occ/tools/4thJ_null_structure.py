#!/usr/bin/env python
"""
4J Step 3, D-S3-4 / D-S3-5: measure whether the null `loc_class` episodes and the null `cop_*`
episodes can be imputed from neighbouring episodes, or whether they need an explicit "unknown" /
"not reported" code.

MEASURE ONLY. Does not impute anything, does not write harmonised.parquet or any file under
outputs_step2/, does not decide D-S3-4 or D-S3-5. Read-only against harmonised.parquet.

Author's ruling (2026-08-17): assess whether imputation from neighbouring episodes is possible;
if not, fall back to an explicit `unknown` LOC class and an explicit out-of-range "not reported"
COP code. Both fallbacks are already approved. This script establishes only whether the
imputation branch is available.

🔴 pd.NA, not NaN. This exact data has already cost four failed jobs to a null guard written as
`isinstance(x, float) and pd.isna(x)`, which misses pd.NA. Every null test below is `pd.isna(x)`
alone, checked before any `==` comparison.

Run with sbatch. Never on the login node.
"""

import sys
import traceback

import numpy as np
import pandas as pd

HARMONISED = "/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet"

DIARY_KEY = ["country", "hid", "pid", "diary_day"]
SHARED_FLAGS = ["cop_alone", "cop_partner", "cop_children", "cop_parent",
                "cop_other_hh", "cop_other_persons"]

# Pre-registered decision rule (manager's rule; author confirms or overrides).
# Imputation is adopted only if it covers >= 99% of that field's null episodes under the strict
# rule (interior_agree, run length <= 2). This script prints the coverage number beside the
# threshold and does NOT apply the rule or announce a verdict.
STRICT_MAX_RUN_LEN = 2
DECISION_THRESHOLD_PCT = 99.0

RUN_LEN_BINS = [(1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 6, "4-6"), (7, None, "7+")]


def run_len_bin(n):
    for lo, hi, label in RUN_LEN_BINS:
        if hi is None:
            if n >= lo:
                return label
        elif lo <= n <= hi:
            return label
    return "?"


def pct_stats(vals):
    if not vals:
        return None
    arr = np.array(vals, dtype=float)
    return {
        "n": len(arr),
        "median": float(np.percentile(arr, 50, method="linear")),
        "p90": float(np.percentile(arr, 90, method="linear")),
        "max": float(arr.max()),
    }


def find_ordering_column(columns):
    """D-S3-4/5 task doc: 'read it, do not assume the name'."""
    if "episode_index" in columns:
        return "episode_index"
    for cand in ("episode_seq", "ep_index", "ep_idx", "seq", "order", "episode_order"):
        if cand in columns:
            print("WARNING: 'episode_index' not found; using fallback ordering column '%s'" % cand)
            return cand
    print("FATAL: no ordering column found among candidates in columns: %s" % sorted(columns))
    sys.exit(1)


def find_duration_column(columns):
    if "duration_min" in columns:
        return "duration_min"
    for cand in ("dur_min", "duration", "dur"):
        if cand in columns:
            print("WARNING: 'duration_min' not found; using fallback duration column '%s'" % cand)
            return cand
    print("FATAL: no duration column found among candidates in columns: %s" % sorted(columns))
    sys.exit(1)


def classify_runs(null_mask, values_for_compare):
    """null_mask: list[bool] for one diary, ordered.
    values_for_compare: list of comparable values (str for loc_class, tuple for cop), same length.
    Returns list of dicts: {bucket, run_len, start, end}.
    """
    n = len(null_mask)
    runs = []
    i = 0
    while i < n:
        if not null_mask[i]:
            i += 1
            continue
        j = i
        while j < n and null_mask[j]:
            j += 1
        # run is [i, j-1]
        s, e = i, j - 1
        run_len = e - s + 1
        if s == 0 and e == n - 1:
            bucket = "whole_diary"
        elif s == 0:
            bucket = "head"
        elif e == n - 1:
            bucket = "tail"
        else:
            pred = values_for_compare[s - 1]
            succ = values_for_compare[e + 1]
            # Defensive: predecessor/successor of a maximal null run must be non-null. Assert with
            # pd.isna(), checked before any equality comparison, per the mandated pattern.
            if pd.isna(pred) if not isinstance(pred, tuple) else False:
                print("FATAL: predecessor of an interior run is itself null -- run-finding bug.")
                sys.exit(1)
            if pd.isna(succ) if not isinstance(succ, tuple) else False:
                print("FATAL: successor of an interior run is itself null -- run-finding bug.")
                sys.exit(1)
            bucket = "interior_agree" if pred == succ else "interior_disagree"
        runs.append({"bucket": bucket, "run_len": run_len, "start": s, "end": e})
        i = j
    return runs


def measure_field(df, field_label, null_mask_col, compare_values_fn, dur_col, order_col):
    """
    null_mask_col: boolean Series over the full df, True where the field is null on that row.
    compare_values_fn: function(row) -> comparable value (str or tuple) used for interior
        agree/disagree comparison. Only called on non-null rows.
    Returns: dict with per-country run/episode counts by bucket, run-length-binned crosstab,
    duration stats per bucket, and the strict-rule coverage count -- all per country and total.
    """
    print()
    print("=" * 78)
    print("PART 2 -- run structure for %s" % field_label)

    touched_diary_mask = df.groupby(DIARY_KEY, sort=False)[null_mask_col.name].transform("any")
    sub = df.loc[touched_diary_mask].copy()
    n_diaries_touched = sub.drop_duplicates(subset=DIARY_KEY).shape[0]
    print("diaries containing >=1 null %s episode: %d (only these are iterated)"
          % (field_label, n_diaries_touched))

    # bucket counts: runs and episodes, per country, crossed by run-length bin
    run_counts = {}   # (country, bucket, len_bin) -> n_runs
    ep_counts = {}     # (country, bucket, len_bin) -> n_episodes
    durations = {}      # (country, bucket) -> list of duration_min for null episodes in that bucket

    n_groups = 0
    for key, g in sub.groupby(DIARY_KEY, sort=False):
        country = key[0]
        g = g.sort_values(order_col)
        nmask = g[null_mask_col.name].tolist()
        if not any(nmask):
            continue
        n_groups += 1
        values = [compare_values_fn(row) for _, row in g.iterrows()]
        durs = g[dur_col].tolist()
        runs = classify_runs(nmask, values)
        for r in runs:
            b = r["bucket"]
            lb = run_len_bin(r["run_len"])
            run_counts[(country, b, lb)] = run_counts.get((country, b, lb), 0) + 1
            ep_counts[(country, b, lb)] = ep_counts.get((country, b, lb), 0) + r["run_len"]
            key_d = (country, b)
            durations.setdefault(key_d, [])
            durations[key_d].extend(durs[r["start"]:r["end"] + 1])

    print("diaries actually iterated (had >=1 null episode found in the group): %d" % n_groups)

    countries = sorted(set(k[0] for k in run_counts.keys()))
    buckets = ["whole_diary", "head", "tail", "interior_agree", "interior_disagree"]
    len_bins = [b[2] for b in RUN_LEN_BINS]

    print()
    print("-- runs and episodes by bucket x run-length bin, per country --")
    print("%-8s %-18s %-6s %10s %10s" % ("country", "bucket", "len", "n_runs", "n_episodes"))
    for country in countries:
        for b in buckets:
            for lb in len_bins:
                nr = run_counts.get((country, b, lb), 0)
                ne = ep_counts.get((country, b, lb), 0)
                if nr == 0:
                    continue
                print("%-8s %-18s %-6s %10d %10d" % (country, b, lb, nr, ne))

    print()
    print("-- runs and episodes by bucket, TOTAL across countries --")
    tot_run = {}
    tot_ep = {}
    for (country, b, lb), nr in run_counts.items():
        tot_run[b] = tot_run.get(b, 0) + nr
        tot_ep[b] = tot_ep.get(b, 0) + ep_counts[(country, b, lb)]
    for b in buckets:
        print("%-18s n_runs=%8d  n_episodes=%8d" % (b, tot_run.get(b, 0), tot_ep.get(b, 0)))

    print()
    print("-- null-episode duration (minutes), per bucket, per country --")
    print("%-8s %-18s %8s %10s %10s %10s" % ("country", "bucket", "n", "median", "p90", "max"))
    for country in countries:
        for b in buckets:
            stats = pct_stats(durations.get((country, b), []))
            if stats is None:
                continue
            print("%-8s %-18s %8d %10.1f %10.1f %10.1f"
                  % (country, b, stats["n"], stats["median"], stats["p90"], stats["max"]))

    print()
    print("-- null-episode duration (minutes), per bucket, TOTAL --")
    tot_durations = {}
    for (country, b), vals in durations.items():
        tot_durations.setdefault(b, [])
        tot_durations[b].extend(vals)
    for b in buckets:
        stats = pct_stats(tot_durations.get(b, []))
        if stats is None:
            continue
        print("%-18s n=%8d  median=%8.1f  p90=%8.1f  max=%8.1f"
              % (b, stats["n"], stats["median"], stats["p90"], stats["max"]))

    # Part 4 -- strict-rule coverage: interior_agree with run length <= STRICT_MAX_RUN_LEN
    total_null_episodes = sum(tot_ep.get(b, 0) for b in buckets)
    expected_null_episodes = int(df[null_mask_col.name].sum())
    print()
    if total_null_episodes != expected_null_episodes:
        print("FATAL: run-bucket accounting does not match the direct null count for %s: "
              "buckets sum to %d, direct df null count is %d. Run-finding logic has a bug."
              % (field_label, total_null_episodes, expected_null_episodes))
        sys.exit(1)
    print("sanity check OK: bucketed null-episode count (%d) matches the direct null row count "
          "for %s (%d)" % (total_null_episodes, field_label, expected_null_episodes))
    imputable = 0
    for (country, b, lb), ne in ep_counts.items():
        if b != "interior_agree":
            continue
        lo_hi = next((lo, hi) for lo, hi, label in RUN_LEN_BINS if label == lb)
        # lb "1" and "2" are exactly run lengths 1 and 2; STRICT_MAX_RUN_LEN=2 means both qualify.
        if lb in ("1", "2") and lo_hi[0] <= STRICT_MAX_RUN_LEN:
            imputable += ne
    residual = total_null_episodes - imputable
    pct_cov = (100.0 * imputable / total_null_episodes) if total_null_episodes else float("nan")

    return {
        "total_null_episodes": total_null_episodes,
        "imputable": imputable,
        "residual": residual,
        "pct_cov": pct_cov,
    }


def main():
    print("4J D-S3-4 / D-S3-5: null LOC / COP run-structure measurement (measure only)")
    print("=" * 78)
    print("pandas %s, numpy %s" % (pd.__version__, np.__version__))

    cols = DIARY_KEY + ["episode_index", "duration_min", "act", "loc_class",
                         "strat_day_type", "strat_age_band"] + SHARED_FLAGS
    print("reading %s" % HARMONISED)
    try:
        df_full = pd.read_parquet(HARMONISED, columns=None)
    except Exception:
        print("FATAL: could not read harmonised.parquet at all.")
        traceback.print_exc()
        sys.exit(1)
    print("full column list (%d): %s" % (len(df_full.columns), sorted(df_full.columns.tolist())))

    missing = [c for c in cols if c not in df_full.columns]
    if missing:
        print("FATAL: expected columns missing from harmonised.parquet: %s" % missing)
        sys.exit(1)
    df = df_full[cols].copy()
    del df_full
    print("rows read: %d, columns used: %s" % (len(df), cols))

    order_col = find_ordering_column(set(df.columns))
    dur_col = find_duration_column(set(df.columns))
    print("ordering column: %s ; duration column: %s" % (order_col, dur_col))

    # Country lowercasing note (D-S2-16): this script performs no crosswalk join, so the
    # lowercase-before-join rule does not apply here. Stated, not silently skipped.
    print("distinct country values as stored: %s" % sorted(df["country"].dropna().unique().tolist()))
    print("NOTE: no crosswalk join is performed in this script; D-S2-16 lowercase-before-join rule "
          "is therefore not applicable here.")

    df["_loc_null"] = df["loc_class"].isna()
    df["_cop_any_null"] = df[SHARED_FLAGS].isna().any(axis=1)
    df["_cop_all_null"] = df[SHARED_FLAGS].isna().all(axis=1)
    df["_cop_some_not_all_null"] = df["_cop_any_null"] & (~df["_cop_all_null"])

    # -----------------------------------------------------------------
    # PART 1 -- extent, confirmed
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 1 -- extent, per country (confirm against task doc's four numbers)")
    print("%-8s %10s %10s %14s %14s %14s %14s %10s"
          % ("country", "rows", "diaries", "null_loc_rows", "null_loc_dia",
             "null_cop_rows", "null_cop_dia", "both_null"))

    diaries_by_country = df.drop_duplicates(subset=DIARY_KEY).groupby("country").size()
    for country in sorted(df["country"].dropna().unique().tolist()):
        cmask = df["country"] == country
        rows = int(cmask.sum())
        dia = int(diaries_by_country.get(country, 0))
        loc_null_rows = int((cmask & df["_loc_null"]).sum())
        loc_null_dia = int(df.loc[cmask & df["_loc_null"]].drop_duplicates(subset=DIARY_KEY).shape[0])
        cop_null_rows = int((cmask & df["_cop_any_null"]).sum())
        cop_null_dia = int(df.loc[cmask & df["_cop_any_null"]].drop_duplicates(subset=DIARY_KEY).shape[0])
        both_null = int((cmask & df["_loc_null"] & df["_cop_any_null"]).sum())
        print("%-8s %10d %10d %14d %14d %14d %14d %10d"
              % (country, rows, dia, loc_null_rows, loc_null_dia, cop_null_rows, cop_null_dia, both_null))

    total_rows = len(df)
    total_dia = int(df.drop_duplicates(subset=DIARY_KEY).shape[0])
    total_loc_null_rows = int(df["_loc_null"].sum())
    total_loc_null_dia = int(df.loc[df["_loc_null"]].drop_duplicates(subset=DIARY_KEY).shape[0])
    total_cop_null_rows = int(df["_cop_any_null"].sum())
    total_cop_null_dia = int(df.loc[df["_cop_any_null"]].drop_duplicates(subset=DIARY_KEY).shape[0])
    total_both_null = int((df["_loc_null"] & df["_cop_any_null"]).sum())
    print("%-8s %10d %10d %14d %14d %14d %14d %10d"
          % ("TOTAL", total_rows, total_dia, total_loc_null_rows, total_loc_null_dia,
             total_cop_null_rows, total_cop_null_dia, total_both_null))

    n_some_not_all = int(df["_cop_some_not_all_null"].sum())
    print()
    print("cop_* flags always null together? rows where SOME but NOT ALL six are null: %d"
          % n_some_not_all)
    if n_some_not_all != 0:
        print("🔴 NOT ZERO -- the six cop_* flags are NOT always null together. This changes the "
              "reading of D-S3-5; reported as measured, not smoothed over.")
    else:
        print("Confirmed zero: every cop_* null row has all six flags null, none partial.")

    print()
    print("CONFIRM-AGAINST-TASK-DOC: loc_class null rows=%d (expected 24800), loc diaries=%d "
          "(expected 8873); cop null rows=%d (expected 68464), cop diaries=%d (expected 9298)"
          % (total_loc_null_rows, total_loc_null_dia, total_cop_null_rows, total_cop_null_dia))

    # -----------------------------------------------------------------
    # PART 2 -- run structure, loc_class and cop_*
    # -----------------------------------------------------------------
    def loc_value(row):
        return row["loc_class"]

    def cop_value(row):
        vals = []
        for f in SHARED_FLAGS:
            v = row[f]
            if pd.isna(v):
                # Should not happen for a non-null neighbour; classify_runs asserts this too.
                vals.append(None)
            else:
                vals.append(int(v))
        return tuple(vals)

    loc_null_series = df["_loc_null"].rename("_loc_null")
    cop_null_series = df["_cop_any_null"].rename("_cop_any_null")

    loc_result = measure_field(df, "loc_class", loc_null_series, loc_value, dur_col, order_col)
    cop_result = measure_field(df, "cop_* (6-bit pattern)", cop_null_series, cop_value, dur_col, order_col)

    # -----------------------------------------------------------------
    # PART 3 -- is the missingness structured?
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 3 -- is the missingness structured? (by act, strat_day_type, strat_age_band)")

    for label, null_col in (("loc_class", "_loc_null"), ("cop_*", "_cop_any_null")):
        print()
        print("-- %s null prevalence by act (top 15 by null count) --" % label)
        total_null = int(df[null_col].sum())
        by_act_null = df.loc[df[null_col]].groupby("act").size().sort_values(ascending=False)
        by_act_total = df.groupby("act").size()
        print("%-10s %10s %10s %10s" % ("act", "null_n", "share_of_null", "null_rate_in_code"))
        for act_code, n_null in by_act_null.head(15).items():
            share = 100.0 * n_null / total_null if total_null else float("nan")
            act_total = int(by_act_total.get(act_code, 0))
            rate = 100.0 * n_null / act_total if act_total else float("nan")
            print("%-10s %10d %9.2f%% %9.2f%%" % (str(act_code), int(n_null), share, rate))

        for strat_col in ("strat_day_type", "strat_age_band"):
            print()
            print("-- %s null prevalence by %s --" % (label, strat_col))
            by_strat_null = df.loc[df[null_col]].groupby(strat_col).size().sort_values(ascending=False)
            by_strat_total = df.groupby(strat_col).size()
            print("%-16s %10s %10s %10s" % (strat_col, "null_n", "share_of_null", "null_rate_in_stratum"))
            for val, n_null in by_strat_null.items():
                share = 100.0 * n_null / total_null if total_null else float("nan")
                strat_total = int(by_strat_total.get(val, 0))
                rate = 100.0 * n_null / strat_total if strat_total else float("nan")
                print("%-16s %10d %9.2f%% %9.2f%%" % (str(val), int(n_null), share, rate))

    # -----------------------------------------------------------------
    # PART 4 -- coverage number, pre-registered strict rule
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 4 -- coverage under the PRE-REGISTERED strict rule "
          "(interior_agree, run length <= %d)" % STRICT_MAX_RUN_LEN)
    print("Decision rule (manager's, author confirms/overrides; NOT applied here): imputation "
          "adopted only if coverage >= %.0f%% of that field's null episodes; otherwise the "
          "explicit class covers 100%% of them." % DECISION_THRESHOLD_PCT)
    for label, res in (("loc_class", loc_result), ("cop_*", cop_result)):
        print("%s: episodes imputable under the strict rule = %d (%.2f%% of all null episodes); "
              "residual = %d  [threshold = %.0f%%]"
              % (label, res["imputable"], res["pct_cov"], res["residual"], DECISION_THRESHOLD_PCT))

    print()
    print("DONE. No imputation performed. No verdict announced. Author decides D-S3-4 / D-S3-5 "
          "from this output.")


if __name__ == "__main__":
    main()
