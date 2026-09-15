#!/usr/bin/env python
"""
T02 / WP5 step 3a - measured Ontario & Toronto residential hourly profiles from IESO.

Runs ONLY on a Speed compute node via sbatch (outbound network required to fetch IESO zips).
Never run on the login node.

Metric definitions replicated from Step8_docs/08_simulation_plots.py (see task doc
2026-09-15_T02_wp5_ieso_measured_profiles.md, Verified section, for file:line citations):
  - MIDDAY window = array indices [9:17) of a 0-23 hour-of-day axis (08_simulation_plots.py:114,387).
    Under the hour-ending convention (array index i == hour-ending i+1, confirmed against the
    MIDDAY comment "WFH window 09:00-17:00" mapping to real clock 09:00-17:00), this is
    IESO HOUR (1-24, hour-ending) in {10,11,...,17} -- 8 hours. This is NOT the same window the
    prior (discarded) agent used (hour-ending 10-16, 7 hours) -- do not reuse that.
  - load_factor = mean of ALL hourly instances in the slice / max of ALL hourly instances
    (08_simulation_plots.py:383-385), NOT mean/max of the averaged 24h profile.
  - peak_to_avg = max / mean (line 386), the reciprocal of load_factor.
  - midday_share = sum(values at HOUR in midday window) / sum(all values), over all instances in
    the slice (line 387).
  - mean_peak_hour = circular mean (sin/cos, wrap at 24h) of the per-day argmax hour
    (_circular_mean_hour, 08_simulation_plots.py:278-285), reported on a 0-23 basis where
    0 == HOUR-ending 1 (i.e. value = HOUR - 1), to stay directly comparable to the simulated
    numbers, which are indexed the same way.

v2 CHANGE (2026-09-15, collector for JobID 1328239, FAILED exit 1 after 6m20s):
  Job 1328239 died in load_month_df() -> pd.read_csv(..., skiprows=3, usecols=USECOLS, ...) on
  2023-08 with "Usecols do not match columns, columns expected but not found: [all 6 USECOLS]".
  Root cause, confirmed by inspecting the exact cached zip bytes
  (T02/raw/PUB_HourlyConsumptionByFSA_202308_v1.zip, scp'd locally and read with zipfile+readline):
  the extracted CSV's first 4 lines were NOT the usual 3 IESO "\\..." comment lines, they were an
  application-error banner injected ahead of the real header:
      b'ERROR:\n'
      b'ORA-28002: the password will expire within 30 days\n'
      b'\n'
      b'\n'
  followed by the normal b'\\\\Hourly Consumption by Forward Sortation Area\n', b'\\\\Created at
  ...\n', b'\\\\For 2023-08\n', then the real header at line index 7 (0-based), not line index 3.
  This is an intermittent, transient server-side fault on the IESO reports host (an Oracle
  DB/APEX backend error page prepended to one response body), not a permanent schema or column
  change -- every other month in this same run (2019-01 .. 2023-07, i.e. 55 files) downloaded and
  parsed fine with the original fixed skiprows=3. v1's hardcoded `skiprows=3` had no way to detect
  this and silently misread the ERROR banner's blank line as the header row, so every USECOLS name
  came up missing.
  Fix in this v2: (1) locate the real header row dynamically per file (search decoded text for the
  line starting "FSA,DATE,HOUR" instead of assuming a fixed skiprows count) so a corrupted/garbled
  prefix no longer misaligns the parse; (2) if no such header line is found within the first 30
  lines, treat the cached/just-downloaded zip as corrupt, delete it, and re-download once before
  giving up loudly (RuntimeError) -- this also repairs the already-corrupt 202308 v1 zip left on
  disk in T02/raw/ from job 1328239's run, which v1's cache-reuse branch (`if not
  os.path.exists(zip_path): download() else: read from disk`) would otherwise silently reuse
  forever on any resubmit. No metric definition, column selection, scope, period, or output-file
  change vs v1 -- this is a download/parse robustness fix only.
"""
import csv
import hashlib
import io
import os
import sys
import time
import urllib.request
import zipfile
from collections import defaultdict

import numpy as np
import pandas as pd

print(f"[env] python={sys.version.split()[0]} pandas={pd.__version__} numpy={np.__version__}", flush=True)

BASE_URL = "https://reports-public.ieso.ca/public/HourlyConsumptionByFSA/"
WORK_DIR = "/speed-scratch/o_iseri/2J_revision/T02"
RAW_DIR = os.path.join(WORK_DIR, "raw")
OUT_DIR = os.path.join(WORK_DIR, "out")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

YEARS = [2019, 2020, 2021, 2022, 2023]
MONTHS = list(range(1, 13))
MAX_VERSION_PROBE = 5  # try _v1.._v5, keep the highest that exists
HEADER_SCAN_LINES = 30  # how many leading lines to search for the real CSV header row
HEADER_PREFIX = "FSA,DATE,HOUR"  # unambiguous start of the real IESO header row

# Ontario statutory holidays, actual calendar date (NOT substitute-day shifted), except Canada
# Day where the Ontario/federal rule moves the holiday to the following Monday when July 1 falls
# on a Saturday or Sunday. Dates hand-computed and cross-checked against known weekdays
# (see task doc Decisions section) -- not fetched from any calendar API (compute node has no
# guarantee such a package/API is available/allowed here; this is a fixed, auditable list).
HOLIDAYS = {
    2019: ["2019-01-01", "2019-02-18", "2019-04-19", "2019-05-20", "2019-07-01",
           "2019-09-02", "2019-10-14", "2019-12-25", "2019-12-26"],
    2020: ["2020-01-01", "2020-02-17", "2020-04-10", "2020-05-18", "2020-07-01",
           "2020-09-07", "2020-10-12", "2020-12-25", "2020-12-26"],
    2021: ["2021-01-01", "2021-02-15", "2021-04-02", "2021-05-24", "2021-07-01",
           "2021-09-06", "2021-10-11", "2021-12-25", "2021-12-26"],
    2022: ["2022-01-01", "2022-02-21", "2022-04-15", "2022-05-23", "2022-07-01",
           "2022-09-05", "2022-10-10", "2022-12-25", "2022-12-26"],
    2023: ["2023-01-01", "2023-02-20", "2023-04-07", "2023-05-22", "2023-07-03",
           "2023-09-04", "2023-10-09", "2023-12-25", "2023-12-26"],
}
HOLIDAY_SET = set(d for lst in HOLIDAYS.values() for d in lst)

# Period membership by month. "winter" of year Y = Dec(Y) + Jan(Y) + Feb(Y) (calendar-year
# grouping, NOT the meteorological Dec(Y)-Jan(Y+1)-Feb(Y+1) season -- a simplification decided
# here because the task's output is keyed by a single `year` column; see task doc Decisions).
# Mar and Nov are deliberately in no named seasonal period (matches task spec literally); they
# still appear in their own individual-month period and in full_year.
PERIOD_MONTHS = {
    "winter": {12, 1, 2},
    "shoulder": {4, 5, 9, 10},
    "summer": {6, 7, 8},
}

MIDDAY_HOURS_1TO24 = {10, 11, 12, 13, 14, 15, 16, 17}  # IESO HOUR values (hour-ending, 1-24)

USECOLS = ["FSA", "DATE", "HOUR", "CUSTOMER_TYPE", "TOTAL_CONSUMPTION", "PREMISE_COUNT"]
DTYPES = {"FSA": "string", "HOUR": "int16", "CUSTOMER_TYPE": "category",
          "TOTAL_CONSUMPTION": "float64", "PREMISE_COUNT": "float64"}


def head_ok(url):
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200, r
    except Exception:
        return False, None


def pick_highest_version(year, month):
    stem = f"PUB_HourlyConsumptionByFSA_{year:04d}{month:02d}"
    best = None
    for v in range(1, MAX_VERSION_PROBE + 1):
        url = f"{BASE_URL}{stem}_v{v}.zip"
        ok, _ = head_ok(url)
        if ok:
            best = (v, url)
        elif best is not None:
            break  # versions are sequential; stop once one fails after a hit
    return best  # (version, url) or None


def download(url, dest_path):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    with open(dest_path, "wb") as f:
        f.write(data)
    return data


def sha256_of_bytes(b):
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def _extract_csv_bytes(zip_bytes):
    """Returns (csv_bytes, csv_name) for the single CSV member inside a zip's bytes, or
    (None, None) if no CSV member is present."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            return None, None
        with zf.open(names[0]) as fh:
            return fh.read(), names[0]


def _locate_header_skiprows(csv_bytes):
    """Scans the first HEADER_SCAN_LINES lines of the extracted CSV for the real IESO header row
    (starts with 'FSA,DATE,HOUR'). Returns the 0-based line index to pass as pandas `skiprows`,
    or None if not found -- v1 assumed this was always exactly line index 3 (3 leading '\\...'
    comment lines), which job 1328239 showed is not always true: an intermittent server-side
    error banner can be prepended ahead of those comment lines (see module docstring)."""
    head = csv_bytes[:8192].decode("utf-8", errors="replace")
    for i, line in enumerate(head.splitlines()[:HEADER_SCAN_LINES]):
        if line.startswith(HEADER_PREFIX):
            return i
    return None


def load_month_df(year, month):
    """Downloads (if needed), extracts, reads one month's CSV, filters CUSTOMER_TYPE==Residential,
    and returns (df, manifest_row). df columns: FSA, DATE (str), HOUR (1-24 int), TOTAL_CONSUMPTION,
    PREMISE_COUNT, is_toronto (bool), daytype (str), month (int), year (int).

    v2: header row is located dynamically (see _locate_header_skiprows) instead of a hardcoded
    skiprows=3, and a cached-or-fresh zip whose CSV has no locatable header is deleted and
    re-downloaded once before failing loudly -- see module docstring for why (job 1328239)."""
    picked = pick_highest_version(year, month)
    if picked is None:
        print(f"[warn] no file found for {year}-{month:02d}", flush=True)
        return None, {"year": year, "month": month, "file_name": None, "version": None,
                       "bytes": None, "sha256": None, "rows_kept": 0, "status": "MISSING"}
    version, url = picked
    fname = url.rsplit("/", 1)[-1]
    zip_path = os.path.join(RAW_DIR, fname)

    csv_bytes = None
    skip = None
    data = None
    for attempt in (1, 2):
        if os.path.exists(zip_path):
            with open(zip_path, "rb") as f:
                data = f.read()
        else:
            print(f"[dl] {fname}", flush=True)
            data = download(url, zip_path)

        csv_bytes, csv_name = _extract_csv_bytes(data)
        if csv_bytes is None:
            print(f"[warn] no CSV inside {fname}", flush=True)
            return None, {"year": year, "month": month, "file_name": fname, "version": version,
                           "bytes": len(data), "sha256": sha256_of_bytes(data), "rows_kept": 0,
                           "status": "NO_CSV"}

        skip = _locate_header_skiprows(csv_bytes)
        if skip is not None:
            break
        # Corrupt response (e.g. a server-side error banner prepended instead of/ahead of the
        # real header, as seen for 2023-08 in job 1328239) -- drop the cached copy and retry the
        # download once before giving up.
        print(f"[warn] {fname}: no '{HEADER_PREFIX}' header found in first "
              f"{HEADER_SCAN_LINES} lines (attempt {attempt}); first bytes: "
              f"{csv_bytes[:200]!r}", flush=True)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    if skip is None:
        raise RuntimeError(
            f"{fname}: could not locate IESO header row ('{HEADER_PREFIX}...') after "
            f"{attempt} attempt(s) -- looks like a persistently corrupt server response, "
            f"not a transient one. Not a data-definition problem; needs a human look at this "
            f"specific file/month.")

    sha = sha256_of_bytes(data)
    nbytes = len(data)

    df = pd.read_csv(io.BytesIO(csv_bytes), skiprows=skip, usecols=USECOLS, dtype=DTYPES,
                      engine="c", low_memory=True)

    df = df[df["CUSTOMER_TYPE"] == "Residential"].copy()
    rows_kept = len(df)
    df["DATE"] = df["DATE"].astype(str)
    df["is_toronto"] = df["FSA"].str.startswith("M")
    df["month"] = month
    df["year"] = year

    dow = pd.to_datetime(df["DATE"]).dt.dayofweek  # 0=Mon .. 6=Sun
    daytype = np.where(df["DATE"].isin(HOLIDAY_SET), "holiday",
                        np.where(dow >= 5, "weekend", "weekday"))
    df["daytype"] = daytype

    manifest_row = {"year": year, "month": month, "file_name": fname, "version": version,
                     "bytes": nbytes, "sha256": sha, "rows_kept": rows_kept, "status": "OK"}
    return df, manifest_row


def scope_frames(df):
    """Yields (scope_name, sub_df) for Ontario (all Residential FSAs) and Toronto (FSA startswith M)."""
    yield "Ontario", df
    yield "Toronto", df[df["is_toronto"]]


def period_names_for_month(m):
    names = [f"month_{m:02d}"]
    for pname, months in PERIOD_MONTHS.items():
        if m in months:
            names.append(pname)
    return names  # + full_year handled separately by concatenating everything


def circular_mean_hour_idx(hour_idx_array):
    """hour_idx_array: 0-23 values. Returns circular mean (0-23, wraps at 24)."""
    if len(hour_idx_array) == 0:
        return np.nan
    ang = 2 * np.pi * np.asarray(hour_idx_array, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    return float((np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0)


def compute_slice_outputs(scope, year, period, daytype, sub):
    """sub: rows already filtered to this scope/year/period/daytype, columns DATE, HOUR,
    TOTAL_CONSUMPTION, PREMISE_COUNT. Returns (profile_rows, metric_row)."""
    if sub.empty:
        return [], None

    # Step A: per (DATE,HOUR) kwh-per-premise, summed over FSAs in scope.
    per_dh = sub.groupby(["DATE", "HOUR"], observed=True).agg(
        tot_cons=("TOTAL_CONSUMPTION", "sum"),
        tot_prem=("PREMISE_COUNT", "sum"),
    ).reset_index()
    per_dh = per_dh[per_dh["tot_prem"] > 0]
    if per_dh.empty:
        return [], None
    per_dh["kwh_per_premise"] = per_dh["tot_cons"] / per_dh["tot_prem"]

    n_days = per_dh["DATE"].nunique()
    mean_premises = float(per_dh.groupby("DATE")["tot_prem"].sum().mean())

    # Step B: mean 24h profile (mean over days, for each HOUR).
    prof = per_dh.groupby("HOUR")["kwh_per_premise"].mean().reindex(range(1, 25))
    prof_sum = prof.sum()
    share = prof / prof_sum if prof_sum else prof * np.nan

    profile_rows = []
    for h in range(1, 25):
        profile_rows.append({
            "scope": scope, "year": year, "period": period, "daytype": daytype,
            "hour_ending": h,
            "kwh_per_premise": float(prof.loc[h]) if pd.notna(prof.loc[h]) else np.nan,
            "share": float(share.loc[h]) if pd.notna(share.loc[h]) else np.nan,
            "n_days": int(n_days), "mean_premises": mean_premises,
        })

    # Metrics: computed over ALL (DATE,HOUR) instances in the slice, per original-code definition
    # (mean/max of the raw series, not of the averaged profile).
    vals = per_dh["kwh_per_premise"].to_numpy()
    mean_all = float(vals.mean())
    max_all = float(vals.max())
    load_factor = mean_all / max_all if max_all else np.nan
    peak_to_avg = max_all / mean_all if mean_all else np.nan
    midday_mask = per_dh["HOUR"].isin(MIDDAY_HOURS_1TO24)
    midday_sum = float(per_dh.loc[midday_mask, "kwh_per_premise"].sum())
    total_sum = float(per_dh["kwh_per_premise"].sum())
    midday_share = midday_sum / total_sum if total_sum else np.nan

    daily_peak_hour_idx = per_dh.loc[per_dh.groupby("DATE")["kwh_per_premise"].idxmax(), ["DATE", "HOUR"]]
    hour_idx0 = (daily_peak_hour_idx["HOUR"].to_numpy() - 1)  # HOUR(1-24) -> 0-23 idx
    mean_peak_hour = circular_mean_hour_idx(hour_idx0)

    metric_row = {
        "scope": scope, "year": year, "period": period, "daytype": daytype,
        "n_days": int(n_days), "mean_premises": mean_premises,
        "mean_kwh_per_premise": mean_all, "max_kwh_per_premise": max_all,
        "load_factor": load_factor, "peak_to_avg": peak_to_avg,
        "midday_share": midday_share, "mean_peak_hour": mean_peak_hour,
    }
    return profile_rows, metric_row


def main():
    t0 = time.time()
    manifest_rows = []
    monthly_dfs = defaultdict(list)  # year -> list of month df

    for year in YEARS:
        for month in MONTHS:
            df, mrow = load_month_df(year, month)
            manifest_rows.append(mrow)
            if df is not None:
                monthly_dfs[year].append(df)

    # Write manifest early (cheap, and survives even if later steps fail).
    manifest_path = os.path.join(OUT_DIR, "ieso_manifest.csv")
    with open(manifest_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "month", "file_name", "version", "bytes",
                                           "sha256", "rows_kept", "status"])
        w.writeheader()
        for r in manifest_rows:
            w.writerow(r)
    print(f"[manifest] wrote {manifest_path} ({len(manifest_rows)} rows)", flush=True)

    all_profile_rows = []
    all_metric_rows = []

    for year in YEARS:
        dfs = monthly_dfs.get(year, [])
        if not dfs:
            print(f"[warn] no data at all for {year}", flush=True)
            continue
        year_df = pd.concat(dfs, ignore_index=True)

        # Build period -> subset-of-months map for this year, including full_year and each month.
        periods = {"full_year": set(MONTHS)}
        for m in MONTHS:
            periods[f"month_{m:02d}"] = {m}
        for pname, months in PERIOD_MONTHS.items():
            periods[pname] = months

        for scope, scope_df in scope_frames(year_df):
            for period, months in periods.items():
                period_df = scope_df[scope_df["month"].isin(months)]
                if period_df.empty:
                    continue
                for daytype in ("weekday", "weekend", "holiday"):
                    sub = period_df[period_df["daytype"] == daytype]
                    prof_rows, metric_row = compute_slice_outputs(scope, year, period, daytype, sub)
                    all_profile_rows.extend(prof_rows)
                    if metric_row is not None:
                        all_metric_rows.append(metric_row)
        del year_df, dfs
        print(f"[year] {year} done, t={time.time()-t0:.0f}s", flush=True)

    profiles_path = os.path.join(OUT_DIR, "ieso_profiles_long.csv")
    pd.DataFrame(all_profile_rows).to_csv(profiles_path, index=False)
    print(f"[out] wrote {profiles_path} ({len(all_profile_rows)} rows)", flush=True)

    metrics_df = pd.DataFrame(all_metric_rows)

    # 2019 -> 2022 change, per (scope, period, daytype), appended as extra rows with
    # year="2019_to_2022_delta" holding (2022 value - 2019 value) for each metric column.
    delta_rows = []
    metric_cols = ["mean_kwh_per_premise", "max_kwh_per_premise", "load_factor", "peak_to_avg",
                   "midday_share", "mean_peak_hour"]
    if not metrics_df.empty:
        idx_cols = ["scope", "period", "daytype"]
        y19 = metrics_df[metrics_df["year"] == 2019].set_index(idx_cols)
        y22 = metrics_df[metrics_df["year"] == 2022].set_index(idx_cols)
        common = y19.index.intersection(y22.index)
        for key in common:
            row = {"scope": key[0], "year": "2019_to_2022_delta", "period": key[1], "daytype": key[2],
                   "n_days": np.nan, "mean_premises": np.nan}
            for c in metric_cols:
                row[c] = float(y22.loc[key, c] - y19.loc[key, c])
            delta_rows.append(row)

    metrics_out = pd.concat([metrics_df, pd.DataFrame(delta_rows)], ignore_index=True) if delta_rows else metrics_df
    metrics_path = os.path.join(OUT_DIR, "ieso_metrics.csv")
    metrics_out.to_csv(metrics_path, index=False)
    print(f"[out] wrote {metrics_path} ({len(metrics_out)} rows)", flush=True)

    print(f"[done] total wall time {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
