#!/usr/bin/env python3
"""t28_check.py -- T28 collector (Acceptance B0-B5), run LATER by the collector
as its own sbatch job (-c 4 --mem=16G, per the task doc's Brief step 2). Phase A
only writes this file, py_compiles it, and smoke-tests it against a tiny fake
tree built in the scratchpad (see Phase A Ledger entry) -- it is NOT executed
against real Speed output during Phase A, because no jobs have been submitted.

Task doc: 2026-09-15_T28_wp4_n200_montreal.md, "Acceptance (collector)" B0-B5.

Cells checked (fixed, the 4 Montreal cells, archetype order -- task doc Design):
  SingleD__Montreal_6A, OtherDwelling__Montreal_6A, MidRise__Montreal_6A,
  HighRise__Montreal_6A

Layout read (matches t28_array.sh / run_step8_paired_mc(), main.py:2009-2116):
  <t28-root>/out/<cell>/cell_manifest.csv                             (sample,sim_hh_id,hhsize,dtype,pr)
  <t28-root>/out/<cell>/sample_NNN_HH<id>/<year>/hourly_meters.csv    (hour, <meter names>..., J)
  <t28-root>/logs/t28_*.out                                           (one per array task; the
                                                                        "CELL=<cell>" header line
                                                                        t28_array.sh echoes identifies
                                                                        which cell a log belongs to)
T21's Step-8 output is the N=50 reference for B1/B2/B3 (task doc Brief step 2:
"The check script must read T21's Step-8 manifests and per-household annual kWh
from where t21_array.sh writes them" -- NOT the older published campaign_N50,
which is not staged on Speed for T28 to read):
  <t21-root>/out/step8/<cell>/cell_manifest.csv
  <t21-root>/out/step8/<cell>/sample_NNN_HH<id>/<year>/hourly_meters.csv

Metric formulas reproduced from Step8_docs/08_simulation_plots.py (T27 Q5, the
task doc's own metric list): FACILITY meter = "Electricity:Facility" (already
includes lights+equip+fan, :79-80). J/h -> kW: divide by 3.6e6 (:340). annual
kWh = grid.sum() (:361). mean_daily_peak_kW = daily_peak.mean() (:377).
mean_peak_hour = circular mean of the 365 daily-peak hours (_circular_mean_hour,
:278-285, :372/378/388). load_factor = mean24/max24 (:385). midday_share = hours
[9,17) / total (:387, MIDDAY at :114). evening_ramp_kW_mean = mean over 365 days
of (hour17 - hour14) facility kW (enduse_hour_2022_v2.py:302-304 -- built new
for WP6/WP3, not in the original 08_simulation_plots.py, per T27 Q5).
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

import numpy as np
from scipy import stats as _stats

FACILITY = "Electricity:Facility"
CELLS = ["SingleD__Montreal_6A", "OtherDwelling__Montreal_6A",
         "MidRise__Montreal_6A", "HighRise__Montreal_6A"]
METRICS = ["elec_facility_kWh", "mean_daily_peak_kW", "mean_peak_hour",
           "load_factor", "midday_share", "evening_ramp_kW_mean"]

_SAMP_RE = re.compile(r"^sample_(\d+)_HH(.+)$", re.IGNORECASE)
_POOL_RE = re.compile(r"Pool=(\d+)\s+sampled=(\d+)\s+replacement=(True|False)")
_CELL_HDR_RE = re.compile(r"CELL=(\S+)")


# ---------------------------------------------------------------------------
# Low-level readers
# ---------------------------------------------------------------------------

def read_manifest_pairs(path):
    """{sample:int -> sim_hh_id:str} from a cell_manifest.csv
    (header: sample,sim_hh_id,hhsize,dtype,pr -- main.py:2079)."""
    pairs = {}
    if not os.path.exists(path):
        return pairs
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                pairs[int(row["sample"])] = str(row["sim_hh_id"])
            except (KeyError, ValueError):
                continue
    return pairs


def _circular_mean_hour(hours):
    """Reproduces 08_simulation_plots.py:278-285 _circular_mean_hour."""
    if len(hours) == 0:
        return float("nan")
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    return float((np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0)


def household_metrics(hourly_csv_path):
    """Read one hourly_meters.csv. Returns (n_rows, metrics_dict_or_None).
    metrics is None if the FACILITY column is missing or the file is not a
    full 8760-row year (Acceptance B0's own definition of "delivered")."""
    if not os.path.exists(hourly_csv_path):
        return 0, None
    with open(hourly_csv_path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r, None)
        if not header or FACILITY not in header:
            return 0, None
        fi = header.index(FACILITY)
        vals = []
        n_rows = 0
        for row in r:
            n_rows += 1
            try:
                vals.append(float(row[fi]))
            except (IndexError, ValueError):
                vals.append(float("nan"))
    if n_rows != 8760 or len(vals) < 8760:
        return n_rows, None
    kw = np.asarray(vals[:8760], dtype=float) / 3.6e6  # J/h -> kW (08_simulation_plots.py:340)
    grid = kw.reshape(365, 24)
    daily_peak = grid.max(axis=1)
    daily_peak_hr = grid.argmax(axis=1)
    mean24, max24 = grid.mean(), grid.max()
    total = grid.sum()
    ramp = grid[:, 17] - grid[:, 14]
    metrics = {
        "elec_facility_kWh": float(total),
        "mean_daily_peak_kW": float(daily_peak.mean()),
        "mean_peak_hour": _circular_mean_hour(daily_peak_hr),
        "load_factor": float(mean24 / max24) if max24 else float("nan"),
        "midday_share": float(grid[:, 9:17].sum() / total) if total else float("nan"),
        "evening_ramp_kW_mean": float(ramp.mean()),
    }
    return n_rows, metrics


def load_cell(out_root, cell, years):
    """out_root is e.g. <t28-root>/out or <t21-root>/out/step8.
    Returns (manifest {sample:hh_id}, {(sample,year): (n_rows, metrics_or_None)})."""
    cell_dir = os.path.join(out_root, cell)
    manifest = read_manifest_pairs(os.path.join(cell_dir, "cell_manifest.csv"))
    runs = {}
    if os.path.isdir(cell_dir):
        for name in sorted(os.listdir(cell_dir)):
            m = _SAMP_RE.match(name)
            if not m:
                continue
            sample = int(m.group(1))
            for y in years:
                hm = os.path.join(cell_dir, name, y, "hourly_meters.csv")
                runs[(sample, y)] = household_metrics(hm)
    return manifest, runs


def _metric_series(runs, sample_ids, years, metric):
    """dict year -> np.array of metric values across sample_ids, same order,
    NaN where the household/year is missing or undelivered (paired series)."""
    out = {}
    for y in years:
        vals = []
        for s in sample_ids:
            _, m = runs.get((s, y), (0, None))
            vals.append(m[metric] if m else float("nan"))
        out[y] = np.array(vals, dtype=float)
    return out


# ---------------------------------------------------------------------------
# B0 -- completeness
# ---------------------------------------------------------------------------

def b0_completeness(t28_root, years, n_planned):
    rows = []
    for cell in CELLS:
        _, runs = load_cell(os.path.join(t28_root, "out"), cell, years)
        for y in years:
            delivered = sum(1 for (s, yy), (n, m) in runs.items() if yy == y and m is not None)
            bad = [{"sample": s, "n_rows": n} for (s, yy), (n, m) in runs.items()
                   if yy == y and m is None]
            rows.append({"cell": cell, "year": y, "delivered": delivered,
                         "planned": n_planned, "n_undelivered": len(bad),
                         "undelivered": bad})
    total_delivered = sum(r["delivered"] for r in rows)
    total_planned = sum(r["planned"] for r in rows)
    return rows, total_delivered, total_planned


# ---------------------------------------------------------------------------
# B1 -- pool size and 50-household prefix match against T21's Step-8 manifest
# ---------------------------------------------------------------------------

def _scan_logs_for_pool(logs_dir):
    """Map cell -> re.Match of the Pool=.. line, by first finding this log's
    own CELL=.. header line (t28_array.sh echoes both per task)."""
    pool_by_cell = {}
    if not os.path.isdir(logs_dir):
        return pool_by_cell
    for log_path in glob.glob(os.path.join(logs_dir, "t28_*.out")):
        cell, pool_match = None, None
        with open(log_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if cell is None:
                    m = _CELL_HDR_RE.search(line)
                    if m:
                        cell = m.group(1)
                m2 = _POOL_RE.search(line)
                if m2:
                    pool_match = m2
        if cell and pool_match:
            pool_by_cell[cell] = pool_match
    return pool_by_cell


def b1_pool_and_prefix(t28_root, t21_root, logs_dir, n_planned, n_prefix):
    pool_by_cell = _scan_logs_for_pool(logs_dir)
    results = []
    for cell in CELLS:
        entry = {"cell": cell, "pool_line": "MISSING", "pool_ok": False,
                  "prefix_ok": None, "prefix_mismatches": []}
        pm = pool_by_cell.get(cell)
        if pm:
            pool_n, sampled_n, repl = int(pm.group(1)), int(pm.group(2)), pm.group(3)
            entry["pool_line"] = f"Pool={pool_n} sampled={sampled_n} replacement={repl}"
            entry["pool_ok"] = bool(pool_n >= 1045 and sampled_n == n_planned and repl == "False")
        got_manifest, _ = load_cell(os.path.join(t28_root, "out"), cell, [])
        ref_manifest, _ = load_cell(os.path.join(t21_root, "out", "step8"), cell, [])
        if not ref_manifest or not got_manifest:
            entry["prefix_ok"] = None  # cannot check yet -- one side has no manifest
        else:
            mism = [{"sample": s, "t28_hh": got_manifest.get(s), "t21_hh": ref_manifest.get(s)}
                    for s in range(1, n_prefix + 1) if got_manifest.get(s) != ref_manifest.get(s)]
            entry["prefix_ok"] = not mism
            entry["prefix_mismatches"] = mism
        results.append(entry)
    return results


# ---------------------------------------------------------------------------
# B2 -- exact reproducibility of annual facility kWh for the shared 50
# ---------------------------------------------------------------------------

def b2_reproducibility(t28_root, t21_root, years, n_prefix, tol_pct):
    results = []
    for cell in CELLS:
        _, runs28 = load_cell(os.path.join(t28_root, "out"), cell, years)
        _, runs21 = load_cell(os.path.join(t21_root, "out", "step8"), cell, years)
        diffs, checked = [], 0
        for s in range(1, n_prefix + 1):
            for y in years:
                _, m28 = runs28.get((s, y), (0, None))
                _, m21 = runs21.get((s, y), (0, None))
                if m28 is None or m21 is None:
                    diffs.append({"sample": s, "year": y, "status": "MISSING"})
                    continue
                checked += 1
                v28, v21 = m28["elec_facility_kWh"], m21["elec_facility_kWh"]
                pct = (float("inf") if v28 != 0 else 0.0) if v21 == 0 else abs(v28 - v21) / abs(v21) * 100.0
                if pct > tol_pct:
                    diffs.append({"sample": s, "year": y, "status": "MISMATCH",
                                  "t28_kWh": v28, "t21_kWh": v21, "pct_diff": pct})
        results.append({"cell": cell, "checked": checked, "diffs": diffs,
                         "status": "PASS" if not diffs else f"FAIL:{len(diffs)}_of_{checked + len([d for d in diffs if d['status']=='MISSING'])}"})
    return results


# ---------------------------------------------------------------------------
# B3 -- is the N=50 mean inside the N=200 95% CI? (per cell x metric x year,
# plus the paired 2022->2030 delta of each)
# ---------------------------------------------------------------------------

def _paired_t_ci(values, conf=0.95):
    values = values[~np.isnan(values)]
    n = len(values)
    if n == 0:
        return float("nan"), float("nan")
    mean = float(values.mean())
    if n < 2:
        return mean, float("nan")
    sem = _stats.sem(values)
    if sem == 0:
        return mean, 0.0
    half = float(_stats.t.ppf((1 + conf) / 2, n - 1) * sem)
    return mean, half


def _bootstrap_ci(values, n_draws, seed, conf=0.95):
    values = values[~np.isnan(values)]
    n = len(values)
    if n == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_draws, n))
    draw_means = values[idx].mean(axis=1)
    lo = np.percentile(draw_means, (1 - conf) / 2 * 100)
    hi = np.percentile(draw_means, (1 + conf) / 2 * 100)
    return float(values.mean()), float((hi - lo) / 2)


def b3_wp4_test(t28_root, t21_root, years, n50, n_draws, seed):
    rows = []
    for cell in CELLS:
        _, runs200 = load_cell(os.path.join(t28_root, "out"), cell, years)
        _, runs50 = load_cell(os.path.join(t21_root, "out", "step8"), cell, years)
        ids200 = sorted({s for (s, _y) in runs200.keys()})
        ids50 = sorted({s for (s, _y) in runs50.keys()})
        for metric in METRICS:
            series200 = _metric_series(runs200, ids200, years, metric)
            series50 = _metric_series(runs50, ids50, years, metric)
            targets = {f"{metric}@{y}": (series200[y], series50[y]) for y in years}
            if len(years) == 2:
                targets[f"{metric}_delta_{years[0]}to{years[1]}"] = (
                    series200[years[1]] - series200[years[0]],
                    series50[years[1]] - series50[years[0]],
                )
            for label, (v200, v50) in targets.items():
                mean50, half50_t = _paired_t_ci(v50)
                mean200, half200_t = _paired_t_ci(v200)
                _, half200_boot = _bootstrap_ci(v200, n_draws=n_draws, seed=seed)
                ok = (not np.isnan(mean50)) and (not np.isnan(mean200))
                inside_t = bool(ok and not np.isnan(half200_t) and abs(mean50 - mean200) <= half200_t)
                inside_boot = bool(ok and not np.isnan(half200_boot) and abs(mean50 - mean200) <= half200_boot)
                rows.append({
                    "cell": cell, "metric": label,
                    "mean_n50": mean50, "mean_n200": mean200,
                    "halfwidth_t_n50": half50_t, "halfwidth_t_n200": half200_t,
                    "halfwidth_boot_n200": half200_boot,
                    "inside_t_ci": inside_t, "inside_boot_ci": inside_boot,
                })
    return rows


# ---------------------------------------------------------------------------
# B4 -- convergence curve: subsamples of the 200 at N=10,20,50,100,150
# ---------------------------------------------------------------------------

def b4_convergence(t28_root, years, sub_ns, n_draws, seed):
    rows = []
    rng_master = np.random.default_rng(seed)
    for cell in CELLS:
        _, runs200 = load_cell(os.path.join(t28_root, "out"), cell, years)
        ids = sorted({s for (s, _y) in runs200.keys()})
        full_n = len(ids)
        for metric in METRICS:
            series = _metric_series(runs200, ids, years, metric)
            targets = {f"{metric}@{y}": series[y] for y in years}
            if len(years) == 2:
                targets[f"{metric}_delta_{years[0]}to{years[1]}"] = series[years[1]] - series[years[0]]
            for label, vals in targets.items():
                mean_full, half_full = _paired_t_ci(vals)
                rows.append({"cell": cell, "metric": label, "N": full_n,
                             "mean": mean_full, "halfwidth": half_full})
                for n_hh in sub_ns:
                    if full_n == 0 or n_hh >= full_n:
                        continue
                    rng = np.random.default_rng(int(rng_master.integers(0, 2**31 - 1)))
                    idx_full = np.arange(full_n)
                    draw_idx = np.array([rng.choice(idx_full, size=n_hh, replace=False)
                                          for _ in range(n_draws)])
                    draw_means = np.nanmean(vals[draw_idx], axis=1)
                    lo, hi = np.percentile(draw_means, 2.5), np.percentile(draw_means, 97.5)
                    rows.append({"cell": cell, "metric": label, "N": n_hh,
                                 "mean": float(np.nanmean(draw_means)),
                                 "halfwidth": float((hi - lo) / 2)})
    return rows


# ---------------------------------------------------------------------------
# B5 -- no fallback / invalid lines in the four task logs
# ---------------------------------------------------------------------------

def b5_no_fallback(logs_dir):
    hits = {}
    if os.path.isdir(logs_dir):
        for log_path in glob.glob(os.path.join(logs_dir, "t28_*.out")):
            lines = []
            with open(log_path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    low = line.lower()
                    if "schedule.json not found" in low or "invalid" in low:
                        lines.append(line.rstrip("\n"))
            if lines:
                hits[log_path] = lines
    return hits


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t28-root", default="/speed-scratch/o_iseri/2J_revision/T28")
    ap.add_argument("--t21-root", default="/speed-scratch/o_iseri/2J_revision/T21")
    ap.add_argument("--years", default="2022,2030")
    ap.add_argument("--n", type=int, default=200, help="planned households/cell (B0, B1).")
    ap.add_argument("--n50", type=int, default=50, help="shared-prefix / reference size (B1, B2, B3).")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-draws-b3", type=int, default=2000)
    ap.add_argument("--n-draws-b4", type=int, default=1000)
    ap.add_argument("--sub-ns", default="10,20,50,100,150")
    ap.add_argument("--tol-pct", type=float, default=0.01, help="B2 tolerance, percent.")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-b3-csv", default=None)
    ap.add_argument("--out-b4-csv", default=None)
    args = ap.parse_args()

    years = args.years.split(",")
    sub_ns = [int(x) for x in args.sub_ns.split(",")]
    logs_dir = os.path.join(args.t28_root, "logs")
    out_json = args.out_json or os.path.join(args.t28_root, "out", "t28_check.json")
    out_b3 = args.out_b3_csv or os.path.join(args.t28_root, "out", "t28_b3_wp4_test.csv")
    out_b4 = args.out_b4_csv or os.path.join(args.t28_root, "out", "t28_b4_convergence.csv")

    b0_rows, b0_delivered, b0_planned = b0_completeness(args.t28_root, years, n_planned=args.n)
    b1_rows = b1_pool_and_prefix(args.t28_root, args.t21_root, logs_dir,
                                  n_planned=args.n, n_prefix=args.n50)
    b1_pass = all(r["pool_ok"] and r["prefix_ok"] for r in b1_rows if r["prefix_ok"] is not None) \
        and all(r["prefix_ok"] is not None for r in b1_rows)
    b2_rows = b2_reproducibility(args.t28_root, args.t21_root, years,
                                  n_prefix=args.n50, tol_pct=args.tol_pct)
    b2_pass = all(r["status"] == "PASS" for r in b2_rows)
    b3_rows = b3_wp4_test(args.t28_root, args.t21_root, years, n50=args.n50,
                           n_draws=args.n_draws_b3, seed=args.seed)
    b4_rows = b4_convergence(args.t28_root, years, sub_ns=sub_ns,
                              n_draws=args.n_draws_b4, seed=args.seed)
    b5_hits = b5_no_fallback(logs_dir)
    b5_pass = not b5_hits

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_b3, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["cell", "metric", "mean_n50", "mean_n200",
                                          "halfwidth_t_n50", "halfwidth_t_n200",
                                          "halfwidth_boot_n200", "inside_t_ci", "inside_boot_ci"])
        w.writeheader()
        w.writerows(b3_rows)
    with open(out_b4, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["cell", "metric", "N", "mean", "halfwidth"])
        w.writeheader()
        w.writerows(b4_rows)

    summary = {
        "b0_completeness": {"delivered": b0_delivered, "planned": b0_planned,
                              "pass": b0_delivered == b0_planned, "rows": b0_rows},
        "b1_pool_and_prefix": {"pass": b1_pass, "rows": b1_rows},
        "b2_reproducibility": {"pass": b2_pass, "rows": b2_rows,
                                 "note": "B2 FAIL is a finding (non-determinism); task doc says it "
                                          "stops B3 until the manager reads it -- B3 below is still "
                                          "computed for visibility, not gated in code."},
        "b3_wp4_test_csv": out_b3, "b3_n_rows": len(b3_rows),
        "b4_convergence_csv": out_b4, "b4_n_rows": len(b4_rows),
        "b5_no_fallback": {"pass": b5_pass, "hits": b5_hits},
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"[B0] delivered {b0_delivered}/{b0_planned}")
    print(f"[B1] pass={b1_pass}: " +
          ", ".join(f"{r['cell']}:pool_ok={r['pool_ok']},prefix_ok={r['prefix_ok']}" for r in b1_rows))
    print(f"[B2] pass={b2_pass}: " + ", ".join(f"{r['cell']}:{r['status']}" for r in b2_rows))
    print(f"[B3] wrote {len(b3_rows)} rows -> {out_b3}")
    print(f"[B4] wrote {len(b4_rows)} rows -> {out_b4}")
    print(f"[B5] pass={b5_pass}: {list(b5_hits.keys())}")
    print(f"Report -> {out_json}")

    sys.exit(0 if (b1_pass and b2_pass and b5_pass) else 1)


if __name__ == "__main__":
    main()
