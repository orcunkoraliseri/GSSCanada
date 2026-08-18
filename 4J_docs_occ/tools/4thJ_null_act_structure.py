#!/usr/bin/env python
"""
4J Step 3, D-S3-9: is null `act` a source fact (World A: act_raw also null/blank) or a Step 2
crosswalk miss (World B: act_raw carries a value but the crosswalk failed to map it)?

MEASURE ONLY. Read-only against harmonised.parquet and crosswalk_activity.csv. Does not impute,
does not encode with any sentinel, does not write harmonised.parquet or anything under
outputs_step2/, does not modify encoder.py/decoder.py/4thJ_step3_build.py, does not re-run the
Step 3 build, and does not apply or announce the pre-registered decision rule for D-S3-9.

Job 1255349 (Step 3 build) refused to emit the corpus: 5,248/73,254 diaries failed round-trip on
"act is null". Loader accounting in that run was clean (2,024,068 rows, 73,254 diaries, 0 dropped),
so the nulls are in the table, not in the reading of it. This script establishes, per country and
in counts, whether each null-`act` row is World A (act_raw itself null/blank/empty -- a Step 3
question) or World B (act_raw carries a value the Step 2 crosswalk did not map -- a Step 2 defect).

D-S2-16: the parquet's `country` column holds ES/UK/IT; crosswalk_activity.csv's `country` column
holds es/uk/it. Every crosswalk lookup below lowercases `country` before the join, and FAILS LOUD
(sys.exit(1)) on a zero-row crosswalk subset for any country -- never silently proceeds on an
empty result set.

pd.NA, not NaN: every null test is `pd.isna(x)` alone, checked before any `==` comparison. This
exact data has already cost four failed jobs to a null guard that missed pd.NA.

Run with sbatch. Never on the login node.
"""

import sys
import traceback

import numpy as np
import pandas as pd

HARMONISED = "/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet"
CW_ACT = "/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_activity.csv"

DIARY_KEY = ["country", "hid", "pid", "diary_day"]
SHARED_FLAGS = ["cop_alone", "cop_partner", "cop_children", "cop_parent",
                "cop_other_hh", "cop_other_persons"]

# Task doc's pre-registered totals (Part 1 confirmation), order ES / IT / UK.
EXPECTED_ROWS = {"ES": 446547, "IT": 1010140, "UK": 567381}
EXPECTED_DIA = {"ES": 19140, "IT": 38260, "UK": 15854}
EXPECTED_FAILING_DIARIES = 5248

RUN_LEN_BINS = [(1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 6, "4-6"), (7, None, "7+")]

TOP_N_RAW = 30
SENTINEL_CODES = ["000", "998", "999"]


def fail(msg):
    print("FATAL: %s" % msg)
    sys.exit(1)


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
    if "episode_index" in columns:
        return "episode_index"
    for cand in ("episode_seq", "ep_index", "ep_idx", "seq", "order", "episode_order"):
        if cand in columns:
            print("WARNING: 'episode_index' not found; using fallback ordering column '%s'" % cand)
            return cand
    fail("no ordering column found among candidates in columns: %s" % sorted(columns))


def find_duration_column(columns):
    if "duration_min" in columns:
        return "duration_min"
    for cand in ("dur_min", "duration", "dur"):
        if cand in columns:
            print("WARNING: 'duration_min' not found; using fallback duration column '%s'" % cand)
            return cand
    fail("no duration column found among candidates in columns: %s" % sorted(columns))


def load_activity_crosswalk(path):
    """Read crosswalk_activity.csv live. dtype=str, keep_default_na=False -- matches
    tools/4thJ_harmonise_step2.py's own load_crosswalks() convention exactly, so 'blank
    target_code' in the CSV reads as '' here too, not NaN, the same as it was read when the
    actual Step 2 join happened."""
    try:
        cw = pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception:
        print("FATAL: could not read crosswalk_activity.csv at %s" % path)
        traceback.print_exc()
        sys.exit(1)
    missing = [c for c in ("country", "source_code", "target_code") if c not in cw.columns]
    if missing:
        fail("crosswalk_activity.csv missing expected column(s): %s" % missing)
    return cw


def crosswalk_subset_for(cw, country_tag):
    sub = cw[cw["country"] == country_tag]
    if len(sub) == 0:
        fail("crosswalk_activity.csv has ZERO rows for country tag '%s' -- zero-match join, "
             "refusing to proceed on an empty result set (D-S2-16)." % country_tag)
    return sub


def classify_runs_worldA(null_mask, act_values):
    """null_mask: list[bool], True where the episode is raw_null (World A) -- the run-defining
    mask for Part 3, per the task doc's 'for the raw_null rows only'. act_values: list of `act`
    values (comparable, str or NA), same length and order, used ONLY for interior agree/disagree.

    Unlike the loc_class/cop_* precedent (tools/4thJ_null_structure.py), the run mask (raw_null)
    and the comparison field (act) are NOT the same field here: a neighbour that bounds a raw_null
    run can itself have a null `act` if that neighbour is World B (act_raw present, unmapped) --
    that neighbour is not raw_null so it is not part of the run, but its `act` is still null. The
    original script's precedent asserts the neighbour is non-null and crashes if not; that
    assertion does not hold here by construction, so a neighbour with a null `act` is handled
    explicitly as bucket 'interior_worldB_adjacent' rather than crashing or silently comparing
    NA==NA.
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
        s, e = i, j - 1
        run_len = e - s + 1
        if s == 0 and e == n - 1:
            bucket = "whole_diary"
        elif s == 0:
            bucket = "head"
        elif e == n - 1:
            bucket = "tail"
        else:
            pred = act_values[s - 1]
            succ = act_values[e + 1]
            if pd.isna(pred) or pd.isna(succ):
                bucket = "interior_worldB_adjacent"
            else:
                bucket = "interior_agree" if pred == succ else "interior_disagree"
        runs.append({"bucket": bucket, "run_len": run_len, "start": s, "end": e})
        i = j
    return runs


def main():
    print("4J D-S3-9: null `act` -- World A (raw_null) vs World B (raw_present_unmapped) measurement")
    print("=" * 78)
    print("pandas %s, numpy %s" % (pd.__version__, np.__version__))

    cols = DIARY_KEY + ["episode_index", "duration_min", "act", "act_raw", "act2",
                         "loc_class"] + SHARED_FLAGS
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
        fail("expected columns missing from harmonised.parquet: %s" % missing)
    df = df_full[cols].copy()
    del df_full
    print("rows read: %d, columns used: %s" % (len(df), cols))

    order_col = find_ordering_column(set(df.columns))
    dur_col = find_duration_column(set(df.columns))
    print("ordering column: %s ; duration column: %s" % (order_col, dur_col))

    countries_seen = sorted(df["country"].dropna().unique().tolist())
    print("distinct country values as stored: %s" % countries_seen)

    df["_act_null"] = df["act"].isna()
    df["_loc_null"] = df["loc_class"].isna()
    df["_cop_any_null"] = df[SHARED_FLAGS].isna().any(axis=1)
    df["_act2_present"] = df["act2"].notna() & (df["act2"] != "")

    # -----------------------------------------------------------------
    # PART 1 -- extent
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 1 -- extent, per country")
    print("%-8s %10s %10s %14s %14s %10s"
          % ("country", "rows", "diaries", "null_act_rows", "null_act_dia", "share_%"))

    diaries_by_country = df.drop_duplicates(subset=DIARY_KEY).groupby("country").size()
    part1_rows = {}
    part1_dia = {}
    disagreements = []
    for country in countries_seen:
        cmask = df["country"] == country
        rows = int(cmask.sum())
        dia = int(diaries_by_country.get(country, 0))
        act_null_rows = int((cmask & df["_act_null"]).sum())
        act_null_dia = int(df.loc[cmask & df["_act_null"]].drop_duplicates(subset=DIARY_KEY).shape[0])
        share = 100.0 * act_null_rows / rows if rows else float("nan")
        part1_rows[country] = rows
        part1_dia[country] = dia
        print("%-8s %10d %10d %14d %14d %9.3f%%" % (country, rows, dia, act_null_rows, act_null_dia, share))
        if country in EXPECTED_ROWS:
            if rows != EXPECTED_ROWS[country]:
                disagreements.append("rows for %s: measured %d, expected %d" % (country, rows, EXPECTED_ROWS[country]))
            if dia != EXPECTED_DIA[country]:
                disagreements.append("diaries for %s: measured %d, expected %d" % (country, dia, EXPECTED_DIA[country]))

    total_rows = len(df)
    total_dia = int(df.drop_duplicates(subset=DIARY_KEY).shape[0])
    total_act_null_rows = int(df["_act_null"].sum())
    total_act_null_dia = int(df.loc[df["_act_null"]].drop_duplicates(subset=DIARY_KEY).shape[0])
    print("%-8s %10d %10d %14d %14d %9.3f%%"
          % ("TOTAL", total_rows, total_dia, total_act_null_rows, total_act_null_dia,
             100.0 * total_act_null_rows / total_rows if total_rows else float("nan")))

    print()
    if disagreements:
        print("🔴 DISAGREEMENT with task doc's pre-registered totals -- STOPPING per instruction, "
              "not proceeding on either number:")
        for d in disagreements:
            print("  - %s" % d)
        sys.exit(1)
    print("CONFIRMED: per-country rows/diaries match task doc's pre-registered totals exactly "
          "(ES 446547/19140, IT 1010140/38260, UK 567381/15854).")

    if total_act_null_dia != EXPECTED_FAILING_DIARIES:
        print("🔴 DISAGREEMENT: measured null-act diary count (%d) does NOT reconcile to the "
              "expected failing-diary count (%d). Reporting the disagreement, not resolving it."
              % (total_act_null_dia, EXPECTED_FAILING_DIARIES))
    else:
        print("CONFIRMED: null-act diary count (%d) reconciles exactly to job 1255349's failing-diary "
              "count (%d)." % (total_act_null_dia, EXPECTED_FAILING_DIARIES))

    # -----------------------------------------------------------------
    # PART 2 -- WORLD A vs WORLD B
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 2 -- WORLD A (raw_null) vs WORLD B (raw_present_unmapped), per country")

    cw = load_activity_crosswalk(CW_ACT)

    # Determine, per country, whether act_raw ships at all (non-null anywhere in that country's rows).
    country_ships_raw = {}
    for country in countries_seen:
        cmask = df["country"] == country
        n_nonnull_raw_anywhere = int((~df.loc[cmask, "act_raw"].isna()).sum())
        country_ships_raw[country] = n_nonnull_raw_anywhere > 0
        print("country=%s: act_raw non-null anywhere in this country's rows = %d (%s)"
              % (country, n_nonnull_raw_anywhere, "ships act_raw" if country_ships_raw[country]
                 else "DOES NOT ship act_raw"))

    def is_blank_or_null(v):
        if pd.isna(v):
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False

    df["_raw_blank_or_null"] = df["act_raw"].apply(is_blank_or_null)

    bucket_col = pd.Series(index=df.index, dtype=object)
    null_act_mask = df["_act_null"]
    for country in countries_seen:
        cmask = (df["country"] == country) & null_act_mask
        if not country_ships_raw[country]:
            bucket_col.loc[cmask] = "raw_column_absent"
            continue
        raw_null_sub = cmask & df["_raw_blank_or_null"]
        raw_present_sub = cmask & (~df["_raw_blank_or_null"])
        bucket_col.loc[raw_null_sub] = "raw_null"
        bucket_col.loc[raw_present_sub] = "raw_present_unmapped"
    df["_act_null_bucket"] = bucket_col

    print()
    print("%-8s %14s %22s %18s %10s" % ("country", "raw_null", "raw_present_unmapped", "raw_column_absent", "total"))
    world_b_nonzero = False
    per_country_bucket_counts = {}
    for country in countries_seen:
        cmask = df["country"] == country
        sub = df.loc[cmask & null_act_mask, "_act_null_bucket"]
        n_raw_null = int((sub == "raw_null").sum())
        n_raw_present = int((sub == "raw_present_unmapped").sum())
        n_absent = int((sub == "raw_column_absent").sum())
        per_country_bucket_counts[country] = {
            "raw_null": n_raw_null, "raw_present_unmapped": n_raw_present, "raw_column_absent": n_absent,
        }
        if n_raw_present > 0:
            world_b_nonzero = True
        total = n_raw_null + n_raw_present + n_absent
        print("%-8s %14d %22d %18d %10d" % (country, n_raw_null, n_raw_present, n_absent, total))

    print()
    if world_b_nonzero:
        print("🔴 HEADLINE: raw_present_unmapped is NON-ZERO for at least one country. `act_raw` "
              "carries a value the Step 2 crosswalk failed to map. This is a Step 2 coverage hole, "
              "reported as measured; no repair proposed here.")
    else:
        print("raw_present_unmapped is ZERO for every country: every null `act` row has act_raw "
              "itself null/blank/empty (World A only).")

    # Top-30 distinct act_raw values by frequency, per country, for raw_present_unmapped, cross-checked
    # against the crosswalk.
    print()
    print("-- raw_present_unmapped: top %d distinct act_raw values by frequency, per country, "
          "cross-checked against crosswalk_activity.csv --" % TOP_N_RAW)
    for country in countries_seen:
        cw_tag = country.lower()
        sub_mask = (df["country"] == country) & (df["_act_null_bucket"] == "raw_present_unmapped")
        n_sub = int(sub_mask.sum())
        print()
        print("country=%s: raw_present_unmapped rows = %d" % (country, n_sub))
        if n_sub == 0:
            continue
        cw_sub = crosswalk_subset_for(cw, cw_tag)
        cw_source_codes = set(cw_sub["source_code"].tolist())
        # map source_code -> target_code, first row wins (load_crosswalks() itself asserts no dup
        # source_code per country; if it were duplicated here that assertion would already have
        # failed upstream, but we do not re-assert it -- read-only measurement, not a Step 2 gate).
        cw_target_map = dict(zip(cw_sub["source_code"], cw_sub["target_code"]))

        vc = df.loc[sub_mask, "act_raw"].value_counts().head(TOP_N_RAW)
        print("%-16s %10s %-24s" % ("act_raw", "count", "defect_type"))
        for val, cnt in vc.items():
            if val not in cw_source_codes:
                defect = "absent_from_crosswalk_entirely"
            else:
                tgt = cw_target_map[val]
                if tgt is None or (isinstance(tgt, str) and tgt.strip() == ""):
                    defect = "present_but_maps_to_null_target"
                else:
                    defect = "present_maps_to_%r_(unexpected:_should_have_joined)" % tgt
            print("%-16s %10d %-24s" % (repr(val), int(cnt), defect))

    # -----------------------------------------------------------------
    # PART 3 -- structure, only if World A is non-empty (raw_null rows only)
    # -----------------------------------------------------------------
    total_raw_null = int((df["_act_null_bucket"] == "raw_null").sum())
    print()
    print("=" * 78)
    print("PART 3 -- run structure for raw_null (World A) episodes only")
    print("total raw_null episodes across all countries: %d" % total_raw_null)

    if total_raw_null == 0:
        print("World A (raw_null) is EMPTY. Part 3 skipped per task doc instruction "
              "('structure, only if World A is non-empty').")
    else:
        df["_raw_null_mask"] = df["_act_null_bucket"] == "raw_null"
        touched_diary_mask = df.groupby(DIARY_KEY, sort=False)["_raw_null_mask"].transform("any")
        sub = df.loc[touched_diary_mask].copy()
        n_diaries_touched = sub.drop_duplicates(subset=DIARY_KEY).shape[0]
        print("diaries containing >=1 raw_null episode: %d (only these are iterated)" % n_diaries_touched)

        run_counts = {}
        ep_counts = {}
        durations = {}
        mixed_run_flag_count = 0

        for key, g in sub.groupby(DIARY_KEY, sort=False):
            country = key[0]
            g = g.sort_values(order_col)
            nmask = g["_raw_null_mask"].tolist()
            if not any(nmask):
                continue
            act_values = g["act"].tolist()
            durs = g[dur_col].tolist()
            runs = classify_runs_worldA(nmask, act_values)
            for r in runs:
                b = r["bucket"]
                lb = run_len_bin(r["run_len"])
                run_counts[(country, b, lb)] = run_counts.get((country, b, lb), 0) + 1
                ep_counts[(country, b, lb)] = ep_counts.get((country, b, lb), 0) + r["run_len"]
                key_d = (country, b)
                durations.setdefault(key_d, [])
                durations[key_d].extend(durs[r["start"]:r["end"] + 1])
                if b == "interior_worldB_adjacent":
                    mixed_run_flag_count += 1

        if mixed_run_flag_count:
            print("NOTE: %d raw_null run(s) are directly adjacent (on at least one side) to a "
                  "World B (raw_present_unmapped) episode -- bucketed as 'interior_worldB_adjacent', "
                  "not agree/disagree, since the neighbour's `act` is itself null and cannot be "
                  "compared." % mixed_run_flag_count)

        countries_here = sorted(set(k[0] for k in run_counts.keys()))
        buckets = ["whole_diary", "head", "tail", "interior_agree", "interior_disagree", "interior_worldB_adjacent"]
        len_bins = [b[2] for b in RUN_LEN_BINS]

        print()
        print("-- runs and episodes by bucket x run-length bin, per country --")
        print("%-8s %-24s %-6s %10s %10s" % ("country", "bucket", "len", "n_runs", "n_episodes"))
        for country in countries_here:
            for b in buckets:
                for lb in len_bins:
                    nr = run_counts.get((country, b, lb), 0)
                    ne = ep_counts.get((country, b, lb), 0)
                    if nr == 0:
                        continue
                    print("%-8s %-24s %-6s %10d %10d" % (country, b, lb, nr, ne))

        print()
        print("-- runs and episodes by bucket, TOTAL across countries --")
        tot_run = {}
        tot_ep = {}
        for (country, b, lb), nr in run_counts.items():
            tot_run[b] = tot_run.get(b, 0) + nr
            tot_ep[b] = tot_ep.get(b, 0) + ep_counts[(country, b, lb)]
        for b in buckets:
            print("%-24s n_runs=%8d  n_episodes=%8d" % (b, tot_run.get(b, 0), tot_ep.get(b, 0)))

        total_bucketed_ep = sum(tot_ep.get(b, 0) for b in buckets)
        if total_bucketed_ep != total_raw_null:
            fail("run-bucket accounting does not match the direct raw_null count: buckets sum to "
                 "%d, direct count is %d. Run-finding logic has a bug." % (total_bucketed_ep, total_raw_null))
        print("sanity check OK: bucketed raw_null episode count (%d) matches the direct count (%d)"
              % (total_bucketed_ep, total_raw_null))

        print()
        print("-- raw_null episode duration (minutes), per bucket, per country --")
        print("%-8s %-24s %8s %10s %10s %10s" % ("country", "bucket", "n", "median", "p90", "max"))
        for country in countries_here:
            for b in buckets:
                stats = pct_stats(durations.get((country, b), []))
                if stats is None:
                    continue
                print("%-8s %-24s %8d %10.1f %10.1f %10.1f"
                      % (country, b, stats["n"], stats["median"], stats["p90"], stats["max"]))

        print()
        print("-- raw_null episode duration (minutes), per bucket, TOTAL --")
        tot_durations = {}
        for (country, b), vals in durations.items():
            tot_durations.setdefault(b, [])
            tot_durations[b].extend(vals)
        for b in buckets:
            stats = pct_stats(tot_durations.get(b, []))
            if stats is None:
                continue
            print("%-24s n=%8d  median=%8.1f  p90=%8.1f  max=%8.1f"
                  % (b, stats["n"], stats["median"], stats["p90"], stats["max"]))

    # Minutes-share and per-diary minutes distribution: computed for ALL null-act episodes
    # (World A + World B combined), because G3.2's sum(DUR)==1440 invariant is threatened by a
    # dropped/null episode regardless of which world it belongs to. A raw_null-only breakdown is
    # printed alongside it, separately, since Part 3 is scoped to World A.
    print()
    print("-- null-act minutes as a share of total diary minutes, per country --")
    print("%-8s %14s %14s %10s   %14s %14s %10s"
          % ("country", "null_act_min", "total_min", "share_%", "rawNull_min", "rawNull_tot_min", "rawNull_%"))
    for country in countries_seen:
        cmask = df["country"] == country
        total_min = float(df.loc[cmask, dur_col].sum())
        null_act_min = float(df.loc[cmask & null_act_mask, dur_col].sum())
        share = 100.0 * null_act_min / total_min if total_min else float("nan")
        raw_null_min = float(df.loc[cmask & (df["_act_null_bucket"] == "raw_null"), dur_col].sum())
        raw_share = 100.0 * raw_null_min / total_min if total_min else float("nan")
        print("%-8s %14.0f %14.0f %9.3f%%   %14.0f %14.0f %9.3f%%"
              % (country, null_act_min, total_min, share, raw_null_min, total_min, raw_share))

    print()
    print("-- null-act minutes per affected diary (median, p90, max), per country --")
    print("(a diary is 'affected' if it has >=1 null-act episode, any world)")
    print("%-8s %8s %10s %10s %10s" % ("country", "n_dia", "median", "p90", "max"))
    per_diary_null_min = df.loc[null_act_mask].groupby(DIARY_KEY)[dur_col].sum().reset_index()
    for country in countries_seen:
        vals = per_diary_null_min.loc[per_diary_null_min["country"] == country, dur_col].tolist()
        stats = pct_stats(vals)
        if stats is None:
            print("%-8s %8d %10s %10s %10s" % (country, 0, "-", "-", "-"))
            continue
        print("%-8s %8d %10.1f %10.1f %10.1f" % (country, stats["n"], stats["median"], stats["p90"], stats["max"]))

    # -----------------------------------------------------------------
    # PART 4 -- overlap with the four fields already decided
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 4 -- overlap between null act and loc_class / cop_* / act2, per country")
    print("%-8s %14s %14s %14s" % ("country", "act&loc_null", "act&cop_null", "act&act2present"))
    for country in countries_seen:
        cmask = df["country"] == country
        n1 = int((cmask & null_act_mask & df["_loc_null"]).sum())
        n2 = int((cmask & null_act_mask & df["_cop_any_null"]).sum())
        n3 = int((cmask & null_act_mask & df["_act2_present"]).sum())
        print("%-8s %14d %14d %14d" % (country, n1, n2, n3))
    n1t = int((null_act_mask & df["_loc_null"]).sum())
    n2t = int((null_act_mask & df["_cop_any_null"]).sum())
    n3t = int((null_act_mask & df["_act2_present"]).sum())
    print("%-8s %14d %14d %14d" % ("TOTAL", n1t, n2t, n3t))

    null_act_diaries = set(map(tuple, df.loc[null_act_mask, DIARY_KEY].drop_duplicates().values.tolist()))
    null_loc_diaries = set(map(tuple, df.loc[df["_loc_null"], DIARY_KEY].drop_duplicates().values.tolist()))
    null_cop_diaries = set(map(tuple, df.loc[df["_cop_any_null"], DIARY_KEY].drop_duplicates().values.tolist()))
    print()
    print("null-act diaries total (re-derived here): %d" % len(null_act_diaries))
    print("null-loc_class diaries total (re-derived here): %d (task doc / 03b expected 8873)" % len(null_loc_diaries))
    print("null-cop_* diaries total (re-derived here): %d (task doc / 03b expected 9298)" % len(null_cop_diaries))
    print("of the %d null-act diaries: also null-loc_class diaries = %d ; also null-cop_* diaries = %d"
          % (len(null_act_diaries), len(null_act_diaries & null_loc_diaries), len(null_act_diaries & null_cop_diaries)))

    # -----------------------------------------------------------------
    # PART 5 -- is '000' (and '998', '999') free?
    # -----------------------------------------------------------------
    print()
    print("=" * 78)
    print("PART 5 -- sentinel-freedom check for '000' / '998' / '999' (check only, do not use)")
    cw_target_codes_all = set(cw["target_code"].tolist())
    act_values_seen = set(df["act"].dropna().unique().tolist())
    print("%-6s %-30s %-20s" % ("code", "legal_target_code_in_crosswalk?", "appears_in_act_column?"))
    for code in SENTINEL_CODES:
        in_cw = code in cw_target_codes_all
        in_act = code in act_values_seen
        print("%-6s %-30s %-20s" % (code, str(in_cw), str(in_act)))
        if in_cw or in_act:
            print("  -> NOT FREE: '%s' is %s%s%s -- a sentinel using this code would test nothing."
                  % (code,
                     "a legal target code in crosswalk_activity.csv" if in_cw else "",
                     " AND " if in_cw and in_act else "",
                     "a value already present in the act column" if in_act else ""))

    print()
    print("DONE. No imputation performed. No verdict announced on D-S3-9. Author decides.")


if __name__ == "__main__":
    main()
