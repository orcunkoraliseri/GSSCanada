#!/usr/bin/env python3
"""t29_check.py -- T29 collector script (P0-P5), run LATER by the collector
as its own sbatch job (Phase A only writes + py_compiles this file and
smoke-tests the P1/P2 logic locally on a tiny fake tree; it is NOT executed
against real Speed output during Phase A).

Task doc: 2026-09-15_T29_wp2_scenario_step8_runs.md, Acceptance P0-P5.
Scenarios: LAMBDA in {0.5 (S-Partial), 0.0 (S-Revert)}. S-Persist
(lambda=1.0) is T21's own Step-8 2030 arm and is not rerun here (task doc
Design); it is read read-only for the P3 "next to T21's S-Persist deltas"
comparison.

Checks:
  P0 completeness  -- 1,200 delivered runs per scenario (24 cells x 50
      households x 1 year), each an 8760-data-row hourly_meters.csv;
      undelivered runs listed by (lambda, cell, sample_dir), never filled.
  P1 pairing       -- each cell's (sample, sim_hh_id) in this run's own
      cell_manifest.csv equals T21's Step-8 manifest for that cell (24/24,
      both scenarios). Reference source: --t21-step8-dir (T21/out/step8/
      <cell>/cell_manifest.csv, once T21 Phase B has produced it) or, if
      given, --step8-published-ref-dir (the local published
      cell_manifest.csv.new_2022_2030_20260711 tree, staged read-only, same
      precedent as t21_check.py's --step8-ref-dir).
  P2 target reached (plan WP2 test) -- injected weekday at-home mean of the
      SAMPLED households (from the staged BEM_Schedules_2030.csv actually
      fed to E+, SIM_HH_ID in the union of this scenario's 24 cell
      manifests, Day_Type=="Weekday"), against the T26 target for the same
      day-type stratum (t26_targets_lambda_<v>.csv, stratum==1 == "WD",
      mean of the `target` column across its 48 slots) -- within 0.5 pp;
      reported per archetype (DTYPE column) and stock-weighted
      (STOCK_WEIGHTS, 08_simulation_plots.py:74-77).
  P3 the chain responds (plan WP2 test, reported not banded) -- stock-
      weighted 2022->2030 deltas of midday share, load factor, mean peak
      hour and annual kWh, per scenario, next to T21's own S-Persist deltas
      (same metric definitions as 08_simulation_plots.py:340-392, T27 Q5).
      2022 values come from T21's own Step-8 output (shared by all three
      scenarios, task doc Design line 11); 2030 values from this
      scenario's own T29 output.
  P4 inputs unchanged -- md5 of the two staged BEM_Schedules_2030.csv files
      (T29/sched_md5_before.txt, written by t29_stage.sh) still match now.
  P5 no fallback -- no "schedule.json not found" and no "invalid" line in
      any T29 array/stage task log.

Usage (on Speed, inside an sbatch job -- never on the login node):
  python t29_check.py --t29-root /speed-scratch/o_iseri/2J_revision/T29 \
      --t26-root /speed-scratch/o_iseri/2J_revision/T26 \
      --t21-step8-dir /speed-scratch/o_iseri/2J_revision/T21/out/step8 \
      [--step8-published-ref-dir <staged published campaign_N50 tree>] \
      --out-json /speed-scratch/o_iseri/2J_revision/T29/out/t29_check.json \
      --out-p2-csv /speed-scratch/o_iseri/2J_revision/T29/out/t29_p2_target.csv \
      --out-p3-csv /speed-scratch/o_iseri/2J_revision/T29/out/t29_p3_deltas.csv

WHAT PHASE A DID NOT VERIFY (see task doc for the full list):
  - Never run against real T29/T21/T26 output (none exists yet).
  - P2/P3 both need `pandas` (not stdlib) -- same dependency as
    t20_metrics.py/t26_metrics.py, present in the step4 env used by every
    other T2x collector script; not re-confirmed importable on Speed here.
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import os
import re
import sys

try:
    import pandas as pd
    import numpy as np
except ImportError:  # pandas/numpy only needed for P2/P3 -- P0/P1/P4/P5 are pure stdlib
    pd = None
    np = None

ARCHS = (["SingleD"] * 6 + ["OtherDwelling"] * 6 + ["MidRise"] * 6 + ["HighRise"] * 6)
CITIES = (["Toronto_5A", "Kelowna_5B", "Vancouver_5C", "Montreal_6A", "Calgary_6B", "Winnipeg_7A"] * 4)
CELLS = [f"{a}__{c}" for a, c in zip(ARCHS, CITIES)]
ARCH_NAMES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]

LAMBDAS = ("0.5", "0.0")
SCEN_LABEL = {"0.5": "S-Partial", "0.0": "S-Revert", "1.0": "S-Persist"}

# Stock weights, same source as 08_simulation_plots.py:74-77 (T27 Q5).
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

FACILITY = "Electricity:Facility"   # 08_simulation_plots.py:80
MIDDAY = (9, 17)                    # 08_simulation_plots.py:114

_SAMP_RE = re.compile(r"^sample_(\d+)_HH(.+)$", re.IGNORECASE)


# ---------------------------------------------------------------- helpers --

def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest_pairs(manifest_path):
    """{sample:int -> sim_hh_id:str} from a cell_manifest.csv (header
    includes sample,sim_hh_id,... -- same shape t21_check.py reads)."""
    pairs = {}
    if not manifest_path or not os.path.exists(manifest_path):
        return pairs
    with open(manifest_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                pairs[int(row["sample"])] = str(row["sim_hh_id"])
            except (KeyError, ValueError):
                continue
    return pairs


# --------------------------------------------------------------------- P0 --

def p0_completeness(out_dir, year="2030"):
    """Return (delivered, samples_found, undelivered[list of (sample_dir,reason)])."""
    delivered = 0
    samples = []
    undelivered = []
    if not os.path.isdir(out_dir):
        return 0, 0, [("<out_dir missing>", "no such directory: " + out_dir)]
    for name in sorted(os.listdir(out_dir)):
        m = _SAMP_RE.match(name)
        if not m:
            continue
        samples.append(name)
        hm = os.path.join(out_dir, name, year, "hourly_meters.csv")
        if not os.path.exists(hm):
            undelivered.append((name, f"missing {year}/hourly_meters.csv"))
            continue
        with open(hm, encoding="utf-8", errors="replace") as f:
            nrows = sum(1 for _ in f) - 1
        if nrows == 8760:
            delivered += 1
        else:
            undelivered.append((name, f"{nrows} data rows, expected 8760"))
    return delivered, len(samples), undelivered


# --------------------------------------------------------------------- P1 --

def read_undelivered_samples(undelivered_path):
    """Sample numbers (ints) listed in this cell/scenario's own undelivered.csv,
    written by run_fixed_manifest.py (addendum 2: a manifest household absent
    from -- or dropped by the sanity check in -- the scenario file is written
    here and NEVER replaced). Used so P1 does not double-count an EXPLAINED
    gap as an unexplained pairing mismatch."""
    samples = set()
    if not undelivered_path or not os.path.exists(undelivered_path):
        return samples
    with open(undelivered_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                samples.add(int(row["sample"]))
            except (KeyError, ValueError):
                continue
    return samples


def p1_pairing(cell, out_dir, ref_manifest_path):
    """Addendum 2: "P1 stays as written (equality with T21's manifest) and
    now also counts undelivered households per cell." A sample present only
    in `ref` because run_fixed_manifest.py's own undelivered.csv lists it
    (household absent from, or failing the sanity check in, this scenario's
    schedule file) is an EXPLAINED gap, not a pairing bug -- it is P0's own
    completeness shortfall, reported separately. Only an UNEXPLAINED
    mismatch (a different hh_id for the same sample, or a sample missing
    from `got` that undelivered.csv does not account for) fails P1.
    Returns (status, got, ref, n_undelivered_this_cell)."""
    got = read_manifest_pairs(os.path.join(out_dir, "cell_manifest.csv"))
    ref = read_manifest_pairs(ref_manifest_path)
    undelivered = read_undelivered_samples(os.path.join(out_dir, "undelivered.csv"))
    if not ref:
        return "NO_REF", got, ref, len(undelivered)
    if not got and not undelivered:
        return "NO_RUN_OUTPUT", got, ref, len(undelivered)
    mismatches = {}
    for s in set(got) | set(ref):
        if got.get(s) == ref.get(s):
            continue
        if s not in got and s in undelivered:
            continue  # explained by undelivered.csv -- not a pairing bug
        mismatches[s] = (got.get(s), ref.get(s))
    status = "PASS" if not mismatches else f"FAIL:{len(mismatches)}_mismatch"
    return status, got, ref, len(undelivered)


def resolve_ref_manifest(cell, t21_step8_dir, published_ref_dir):
    """Prefer T21's own re-run Step-8 manifest for this cell (same code path,
    same seed -- the thing P1 actually needs to match); fall back to the
    published pre-rebuild manifest if T21's own output is not yet staged."""
    if t21_step8_dir:
        p = os.path.join(t21_step8_dir, cell, "cell_manifest.csv")
        if os.path.exists(p):
            return p
    if published_ref_dir:
        p = os.path.join(published_ref_dir, cell, "cell_manifest.csv.new_2022_2030_20260711")
        if os.path.exists(p):
            return p
    return None


# --------------------------------------------------------------------- P2 --

def p2_target_reached(t26_root, t29_root, lam_tag, sampled_ids_by_cell):
    """sampled_ids_by_cell: {cell: {sample:int -> sim_hh_id:str}} for this
    scenario's own 24 cells (from P1's `got`). Returns a dict report."""
    if pd is None:
        return {"status": "SKIPPED_NO_PANDAS"}

    targets_csv = os.path.join(t26_root, "out", f"lambda_{lam_tag}", f"t26_targets_lambda_{lam_tag}.csv")
    bem_csv = os.path.join(t29_root, f"sched_lambda_{lam_tag}", "BEM_Schedules_2030.csv")
    if not os.path.exists(targets_csv) or not os.path.exists(bem_csv):
        return {"status": "MISSING_INPUT", "targets_csv": targets_csv, "bem_csv": bem_csv,
                "targets_csv_exists": os.path.exists(targets_csv), "bem_csv_exists": os.path.exists(bem_csv)}

    tgt = pd.read_csv(targets_csv)
    target_wd_pp = float(tgt[tgt["stratum"] == 1]["target"].mean() * 100.0)

    all_ids = set()
    for cell, pairs in sampled_ids_by_cell.items():
        all_ids.update(str(v) for v in pairs.values())
    if not all_ids:
        return {"status": "NO_SAMPLED_IDS", "target_wd_pp": target_wd_pp}

    bem = pd.read_csv(bem_csv, usecols=["SIM_HH_ID", "Day_Type", "DTYPE", "Occupancy_Schedule"],
                       low_memory=False)
    bem["SIM_HH_ID"] = bem["SIM_HH_ID"].astype(str)
    wd = bem[(bem["Day_Type"] == "Weekday") & (bem["SIM_HH_ID"].isin(all_ids))]
    if wd.empty:
        return {"status": "NO_MATCHING_ROWS", "target_wd_pp": target_wd_pp, "n_sampled_ids": len(all_ids)}

    per_house = wd.groupby("SIM_HH_ID")["Occupancy_Schedule"].mean()
    dtype_of = wd.drop_duplicates("SIM_HH_ID").set_index("SIM_HH_ID")["DTYPE"]
    per_house_df = pd.DataFrame({"mean_occ": per_house, "DTYPE": dtype_of})

    per_archetype_pp = (per_house_df.groupby("DTYPE")["mean_occ"].mean() * 100.0).to_dict()
    stock_weighted_pp = sum(STOCK_WEIGHTS[a] * per_archetype_pp[a]
                             for a in ARCH_NAMES if a in per_archetype_pp)
    diff_pp = stock_weighted_pp - target_wd_pp
    return {
        "status": "OK",
        "target_wd_pp": target_wd_pp,
        "injected_stock_weighted_wd_pp": stock_weighted_pp,
        "diff_pp": diff_pp,
        "flag_over_0.5pp": abs(diff_pp) > 0.5,
        "per_archetype_wd_pp": per_archetype_pp,
        "n_sampled_ids_matched": int(wd["SIM_HH_ID"].nunique()),
        "n_sampled_ids_requested": len(all_ids),
    }


# --------------------------------------------------------------------- P3 --

def _circular_mean_hour(hours):
    """Same definition as 08_simulation_plots.py:278-285."""
    if len(hours) == 0:
        return float("nan"), float("nan"), float("nan")
    ang = 2 * math.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = float(np.sin(ang).mean()), float(np.cos(ang).mean())
    mean_h = (math.atan2(s, c) * 24.0 / (2 * math.pi)) % 24.0
    return mean_h, s, c


def _household_year_metrics(hourly_csv_path):
    """Annual kWh, load factor, midday share, mean-peak-hour (sin/cos) for
    one household-year, from its hourly_meters.csv Electricity:Facility
    column -- same computation as 08_simulation_plots.py:340,369-388
    (J/h -> kW via /3.6e6, reshape (365,24))."""
    if pd is None or not os.path.exists(hourly_csv_path):
        return None
    df = pd.read_csv(hourly_csv_path, usecols=lambda c: c == FACILITY, low_memory=False)
    if FACILITY not in df.columns or len(df) < 8760:
        return None
    kw = pd.to_numeric(df[FACILITY], errors="coerce").to_numpy()[:8760] / 3.6e6
    grid = kw.reshape(365, 24)
    flat = grid.reshape(-1)
    max24 = float(flat.max())
    mean24 = float(grid.mean())
    daily_peak_hr = grid.argmax(axis=1)
    mean_h, ssin, ccos = _circular_mean_hour(daily_peak_hr)
    return dict(
        annual_kWh=float(flat.sum()),
        load_factor=(mean24 / max24) if max24 else float("nan"),
        midday_share=(float(grid[:, MIDDAY[0]:MIDDAY[1]].sum() / grid.sum()) if grid.sum() else float("nan")),
        peak_hour_sin=ssin, peak_hour_cos=ccos,
    )


def _cell_delta(out_root_2022, out_root_2030, cell, sample_hh_ids):
    """Per cell, per sampled hh_id: metrics_2030 - metrics_2022 (paired by
    hh_id, same sample-dir naming as t21_check.py). Returns list of dicts
    (one per delivered, paired household)."""
    rows_ = []
    dir2022 = os.path.join(out_root_2022, cell)
    dir2030 = os.path.join(out_root_2030, cell)
    if not os.path.isdir(dir2022) or not os.path.isdir(dir2030):
        return rows_
    name_by_hh_2030 = {}
    if os.path.isdir(dir2030):
        for name in os.listdir(dir2030):
            m = _SAMP_RE.match(name)
            if m:
                name_by_hh_2030[m.group(2)] = name
    name_by_hh_2022 = {}
    for name in os.listdir(dir2022):
        m = _SAMP_RE.match(name)
        if m:
            name_by_hh_2022[m.group(2)] = name
    for hh_id in set(name_by_hh_2022) & set(name_by_hh_2030):
        m22 = _household_year_metrics(os.path.join(dir2022, name_by_hh_2022[hh_id], "2022", "hourly_meters.csv"))
        m30 = _household_year_metrics(os.path.join(dir2030, name_by_hh_2030[hh_id], "2030", "hourly_meters.csv"))
        if m22 is None or m30 is None:
            continue
        rows_.append(dict(hh_id=hh_id,
                           d_annual_kWh=m30["annual_kWh"] - m22["annual_kWh"],
                           d_load_factor=m30["load_factor"] - m22["load_factor"],
                           d_midday_share=m30["midday_share"] - m22["midday_share"],
                           sin22=m22["peak_hour_sin"], cos22=m22["peak_hour_cos"],
                           sin30=m30["peak_hour_sin"], cos30=m30["peak_hour_cos"]))
    return rows_


def _stock_weighted_scalar(per_cell_mean):
    """per_cell_mean: {cell -> value}. Same weighting scheme as
    08_simulation_plots.py:300-321 (_stock_weighted_circular_mean), applied
    to a plain scalar instead of a circular quantity: each archetype's
    STOCK_WEIGHTS share split equally across its (up to 6) cities."""
    acc = 0.0
    wacc = 0.0
    for arch in ARCH_NAMES:
        sub_cells = [c for c in CELLS if c.startswith(arch + "__") and c in per_cell_mean]
        if not sub_cells:
            continue
        w_each = STOCK_WEIGHTS[arch] / len([c for c in CELLS if c.startswith(arch + "__")])
        for c in sub_cells:
            acc += w_each * per_cell_mean[c]
            wacc += w_each
    return (acc / wacc) if wacc else float("nan")


def _stock_weighted_hour(per_cell_sincos):
    """per_cell_sincos: {cell -> (mean_sin, mean_cos)}. Same scheme as
    08_simulation_plots.py:300-321, exactly (circular quantity)."""
    s_acc = c_acc = w_acc = 0.0
    for arch in ARCH_NAMES:
        sub_cells = [c for c in CELLS if c.startswith(arch + "__") and c in per_cell_sincos]
        if not sub_cells:
            continue
        w_each = STOCK_WEIGHTS[arch] / len([c for c in CELLS if c.startswith(arch + "__")])
        for c in sub_cells:
            s, cc = per_cell_sincos[c]
            s_acc += w_each * s
            c_acc += w_each * cc
            w_acc += w_each
    if w_acc == 0:
        return float("nan")
    return (math.atan2(s_acc, c_acc) * 24.0 / (2 * math.pi)) % 24.0


def p3_chain_response(t21_step8_dir, t29_root, lam_tag, sampled_ids_by_cell):
    """Stock-weighted 2022->2030 deltas for this scenario (reported, not
    banded -- task doc P3)."""
    if pd is None:
        return {"status": "SKIPPED_NO_PANDAS"}
    out_root_2030 = os.path.join(t29_root, "out", f"lambda_{lam_tag}")
    per_cell_kwh, per_cell_lf, per_cell_mds, per_cell_sincos = {}, {}, {}, {}
    n_paired_total = 0
    for cell in CELLS:
        rows_ = _cell_delta(t21_step8_dir, out_root_2030, cell, sampled_ids_by_cell.get(cell, {}))
        if not rows_:
            continue
        n_paired_total += len(rows_)
        per_cell_kwh[cell] = sum(r["d_annual_kWh"] for r in rows_) / len(rows_)
        per_cell_lf[cell] = sum(r["d_load_factor"] for r in rows_) / len(rows_)
        per_cell_mds[cell] = sum(r["d_midday_share"] for r in rows_) / len(rows_)
        # circular delta: stock-weight the 2022 and 2030 mean sin/cos separately, then
        # take the wrap-aware hour difference of the two resulting circular means.
        per_cell_sincos[cell] = (
            (sum(r["sin22"] for r in rows_) / len(rows_), sum(r["cos22"] for r in rows_) / len(rows_)),
            (sum(r["sin30"] for r in rows_) / len(rows_), sum(r["cos30"] for r in rows_) / len(rows_)),
        )
    if n_paired_total == 0:
        return {"status": "NO_PAIRED_HOUSEHOLDS"}

    sw_kwh = _stock_weighted_scalar(per_cell_kwh)
    sw_lf = _stock_weighted_scalar(per_cell_lf)
    sw_mds = _stock_weighted_scalar(per_cell_mds)
    h22 = _stock_weighted_hour({c: v[0] for c, v in per_cell_sincos.items()})
    h30 = _stock_weighted_hour({c: v[1] for c, v in per_cell_sincos.items()})
    d_hour = ((h30 - h22 + 12.0) % 24.0) - 12.0  # wrap-aware, in (-12, 12]

    return dict(status="OK", n_cells_with_data=len(per_cell_kwh), n_paired_households=n_paired_total,
                d_annual_kWh_stock_weighted=sw_kwh, d_load_factor_stock_weighted=sw_lf,
                d_midday_share_stock_weighted=sw_mds, mean_peak_hour_2022=h22, mean_peak_hour_2030=h30,
                d_mean_peak_hour_stock_weighted=d_hour)


# --------------------------------------------------------------------- P4 --

def p4_md5_check(t29_root):
    before_path = os.path.join(t29_root, "sched_md5_before.txt")
    if not os.path.exists(before_path):
        return "NO_BEFORE_FILE", {}
    before = {}
    with open(before_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                before[parts[1]] = parts[0]
    diffs = {}
    for path in before:
        if not os.path.exists(path):
            diffs[path] = "MISSING_NOW"
            continue
        now = md5_of(path)
        if now != before[path]:
            diffs[path] = f"before={before[path]} now={now}"
    return ("PASS" if not diffs else "FAIL"), diffs


# --------------------------------------------------------------------- P5 --

def p5_fallback_scan(logs_dir):
    hits = {}
    if not os.path.isdir(logs_dir):
        return hits
    for log_path in glob.glob(os.path.join(logs_dir, "t29_*.out")):
        lines = []
        with open(log_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                low = line.lower()
                if "schedule.json not found" in low or "invalid" in low:
                    lines.append(line.rstrip("\n"))
        if lines:
            hits[log_path] = lines
    return hits


# -------------------------------------------------------------------- main --

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t29-root", default="/speed-scratch/o_iseri/2J_revision/T29")
    ap.add_argument("--t26-root", default="/speed-scratch/o_iseri/2J_revision/T26")
    ap.add_argument("--t21-step8-dir", default="/speed-scratch/o_iseri/2J_revision/T21/out/step8")
    ap.add_argument("--step8-published-ref-dir", default=None,
                     help="fallback P1 reference if T21's own step8 manifest is not yet staged")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-p2-csv", required=True)
    ap.add_argument("--out-p3-csv", required=True)
    args = ap.parse_args()

    report = {"P0": {}, "P1": {}, "P2": {}, "P3": {}, "P4": {}, "P5": {}}
    p2_rows_out = []
    p3_rows_out = []

    for lam in LAMBDAS:
        out_root = os.path.join(args.t29_root, "out", f"lambda_{lam}")
        sampled_ids_by_cell = {}

        p0_delivered_total, p0_planned_total, p0_undelivered_all = 0, 0, []
        p1_fail_n = 0
        p1_undelivered_manifest_total = 0
        p1_undelivered_by_cell = {}
        for cell in CELLS:
            out_dir = os.path.join(out_root, cell)
            delivered, n_samples, undelivered = p0_completeness(out_dir)
            p0_delivered_total += delivered
            p0_planned_total += 50
            for name, reason in undelivered:
                p0_undelivered_all.append(dict(lam=lam, cell=cell, sample_dir=name, reason=reason))

            ref_path = resolve_ref_manifest(cell, args.t21_step8_dir, args.step8_published_ref_dir)
            status, got, ref, n_undel_manifest = p1_pairing(cell, out_dir, ref_path)
            sampled_ids_by_cell[cell] = got
            p1_undelivered_manifest_total += n_undel_manifest
            if n_undel_manifest:
                p1_undelivered_by_cell[cell] = n_undel_manifest
            if not status.startswith("PASS"):
                p1_fail_n += 1

        report["P0"][lam] = dict(delivered=p0_delivered_total, planned=p0_planned_total,
                                  n_undelivered=len(p0_undelivered_all))
        report["P1"][lam] = dict(cells_failing=p1_fail_n, cells_total=len(CELLS),
                                  n_undelivered_manifest=p1_undelivered_manifest_total,
                                  undelivered_manifest_by_cell=p1_undelivered_by_cell)

        p2 = p2_target_reached(args.t26_root, args.t29_root, lam, sampled_ids_by_cell)
        report["P2"][lam] = p2
        if p2.get("status") == "OK":
            for arch, v in p2["per_archetype_wd_pp"].items():
                p2_rows_out.append(dict(scenario=SCEN_LABEL[lam], group=arch, injected_wd_pp=v,
                                         target_wd_pp=p2["target_wd_pp"], diff_pp=v - p2["target_wd_pp"]))
            p2_rows_out.append(dict(scenario=SCEN_LABEL[lam], group="stock_weighted",
                                     injected_wd_pp=p2["injected_stock_weighted_wd_pp"],
                                     target_wd_pp=p2["target_wd_pp"], diff_pp=p2["diff_pp"]))

        p3 = p3_chain_response(args.t21_step8_dir, args.t29_root, lam, sampled_ids_by_cell)
        report["P3"][lam] = p3
        if p3.get("status") == "OK":
            p3_rows_out.append(dict(scenario=SCEN_LABEL[lam], **{k: v for k, v in p3.items() if k != "status"}))

    p4_status, p4_diffs = p4_md5_check(args.t29_root)
    report["P4"] = dict(status=p4_status, diffs=p4_diffs)

    p5_hits = p5_fallback_scan(os.path.join(args.t29_root, "logs"))
    report["P5"] = dict(n_logs_with_hit=len(p5_hits),
                         logs=[dict(log=k, n_lines=len(v), example=v[0]) for k, v in p5_hits.items()])

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if p2_rows_out:
        with open(args.out_p2_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["scenario", "group", "injected_wd_pp", "target_wd_pp", "diff_pp"])
            w.writeheader()
            w.writerows(p2_rows_out)
    if p3_rows_out:
        with open(args.out_p3_csv, "w", newline="", encoding="utf-8") as f:
            fieldnames = sorted({k for r in p3_rows_out for k in r})
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(p3_rows_out)

    print(json.dumps(report, indent=2))

    fail = False
    for lam in LAMBDAS:
        if report["P0"][lam]["delivered"] < report["P0"][lam]["planned"]:
            fail = True
        if report["P1"][lam]["cells_failing"] > 0:
            fail = True
        if report["P2"][lam].get("flag_over_0.5pp"):
            fail = True
    if p4_status != "PASS" or p5_hits:
        fail = True
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
