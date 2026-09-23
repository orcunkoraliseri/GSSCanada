# -*- coding: utf-8 -*-
"""P3 (2026-09-23) -- run the Step 9 appliance model on generated, real and
raked-donor diaries for es/uk/it, and report the peak hour and peak power per
country per source.

Design doc: writing/submission/IMP/impl/P3_appliance_real_and_donor.md.
This is the ONE job the design asks for: "a single job with 1-4 CPUs that
runs the 9 runs serially is preferred." It:

  1. (Re)builds the real/raked pools via `4thJ_p3_build_pools.py` (idempotent).
  2. Runs `4thJ_step9_trigger.run_fold()` 9 times -- 3 folds x {generated,
     real, raked} -- writing each to its own
     `Step9_docs/outputs_step9_P3/<source>/<fold>/`.
  3. Computes, from each run's own `stock_series_<fold>.csv` and
     `step9_manifest_<fold>.json`, the SAME per-dwelling-mean diurnal peak
     that `4thJ_step9_aggregate.py` writes to `agg_diurnal.csv` (confirmed by
     reading that script; not re-derived independently).
  4. Prints the three controls (C-a, C-b, C-c), each its own PASS/FAIL line
     with the hashes/counts, BEFORE printing any real/raked result. If C-a
     fails, the real/raked numbers are still computed (so the failure can be
     diagnosed) but are printed under a line that says they must NOT be
     trusted.

    python 4thJ_p3_run_campaign.py --root <4J_docs_occ>
"""
import argparse
import csv
import hashlib
import importlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

s9 = importlib.import_module("4thJ_step9_trigger")
bp = importlib.import_module("4thJ_p3_build_pools")

FOLDS = ("es", "uk", "it")
SOURCES = ("generated", "real", "raked")


def md5_of(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def peak_hour_power(stock_series_path, manifest_path):
    """Per-dwelling-mean diurnal peak, exactly as `4thJ_step9_aggregate.py`
    computes `agg_diurnal.csv`'s `elec_w_per_dwelling` column (read that
    script's `build()` before trusting this; it is reproduced here, not
    imported, only because `build()` also demands `enduse_by_dwelling_<c>.csv`
    rows this driver has no other use for)."""
    m = json.load(io.open(manifest_path, encoding="utf-8"))
    ts = m["timestep_min"]
    n_dw = m["n_dwellings"]
    per_day = 24 * 60 // ts
    acc = [0.0] * per_day
    cnt = [0] * per_day
    with io.open(stock_series_path, encoding="utf-8") as fh:
        for i, row in enumerate(csv.DictReader(fh)):
            slot = i % per_day
            acc[slot] += float(row["electricity_w"])
            cnt[slot] += 1
    per_dwelling = [acc[s] / cnt[s] / n_dw for s in range(per_day)]
    peak_val = max(per_dwelling)
    peak_slot = per_dwelling.index(peak_val)
    return round(peak_slot * ts / 60.0, 3), round(peak_val, 4)


def run_one(root, fold, source, pool_path, out_dir, leg, year, seed,
           n_households, timestep_min, dhw_l_per_day):
    t0 = time.time()
    m = s9.run_fold(root, fold, leg, year, seed, n_households, timestep_min,
                    out_dir, dhw_l_per_day, pool_path=pool_path)
    dt = time.time() - t0
    enduse_path = os.path.join(out_dir, "enduse_by_dwelling_%s.csv" % fold)
    stock_path = os.path.join(out_dir, "stock_series_%s.csv" % fold)
    man_path = os.path.join(out_dir, "step9_manifest_%s.json" % fold)
    peak_hour, peak_w = peak_hour_power(stock_path, man_path)
    print("  run %s/%s done in %.1fs -- dwellings=%d, campaign=%s, "
          "peak %.2f W at %.2f:00, enduse hash=%s"
          % (source, fold, dt, m["n_dwellings"], m["is_campaign_run"],
             peak_w, peak_hour, md5_of(enduse_path)[:12]))
    return {
        "fold": fold, "source": source, "out_dir": out_dir,
        "enduse_path": enduse_path, "enduse_md5": md5_of(enduse_path),
        "stock_path": stock_path, "manifest_path": man_path,
        "peak_hour": peak_hour, "peak_w": peak_w,
        "n_dwellings": m["n_dwellings"], "is_campaign_run": m["is_campaign_run"],
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--leg", default="leg5")
    ap.add_argument("--year", type=int, default=2017)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--households", type=int, default=100)
    ap.add_argument("--timestep", type=int, default=60)
    ap.add_argument("--dhw-l-per-day", type=float, default=200.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    out_root = args.out or os.path.join(args.root, "Step9_docs",
                                        "outputs_step9_P3")
    pools_dir = os.path.join(out_root, "pools")

    print("=" * 78)
    print("P3 step 1/3 -- build real and raked-donor pools")
    print("=" * 78)
    rc = bp.main(["--root", args.root, "--leg", args.leg, "--out", pools_dir])
    if rc != 0:
        print("POOL BUILD FAILED (C-c). Stopping before any run.")
        return rc

    print("")
    print("=" * 78)
    print("P3 step 2/3 -- 9 runs (3 folds x generated/real/raked)")
    print("=" * 78)
    results = {}
    for fold in FOLDS:
        for source in SOURCES:
            if source == "generated":
                pool_path = None
            else:
                pool_path = os.path.join(pools_dir, "%s_%s.jsonl" % (source, fold))
                if not os.path.exists(pool_path):
                    raise SystemExit("missing pool file %s" % pool_path)
            out_dir = os.path.join(out_root, source, fold)
            results[(fold, source)] = run_one(
                args.root, fold, source, pool_path, out_dir, args.leg,
                args.year, args.seed, args.households, args.timestep,
                args.dhw_l_per_day)

    print("")
    print("=" * 78)
    print("P3 step 3/3 -- controls")
    print("=" * 78)

    shipped_dir = os.path.join(args.root, "Step9_docs", "outputs_step9")

    # -- C-a: --pool pointed at the generated file reproduces the SHIPPED
    #    Step9_docs/outputs_step9/enduse_by_dwelling_<c>.csv byte for byte.
    ca_hash_ok = True
    for fold in FOLDS:
        shipped_path = os.path.join(shipped_dir, "enduse_by_dwelling_%s.csv" % fold)
        new_md5 = results[(fold, "generated")]["enduse_md5"]
        shipped_md5 = md5_of(shipped_path) if os.path.exists(shipped_path) else None
        ok = (shipped_md5 is not None and new_md5 == shipped_md5)
        ca_hash_ok = ca_hash_ok and ok
        print("C-a hash  fold=%s  new=%s  shipped=%s  %s"
              % (fold, new_md5[:12], (shipped_md5 or "MISSING")[:12],
                 "PASS" if ok else "FAIL"))

    # C-a's Table-7 clause: Table 7 in the manuscript states Spain 14:00,
    # 518 W. The ACTUAL data behind Table 7 and Figure 6 -- read from
    # `Step9_docs/outputs_step9/agg_diurnal.csv` and from
    # `writing/submission/figures/scripts/generate_fig06.py`'s own hard-coded
    # `spain` series (both agree) -- is Spain 14:00, 502.8777 W, not 518 W.
    # The hour matches; the watt figure printed in the manuscript prose does
    # not match its own underlying data. This is a PRE-EXISTING manuscript
    # inconsistency, not something this P3 change caused, and it is not
    # fixed here (manuscript edits are out of scope). C-a is scored against
    # the ACTUAL shipped data (502.8777 W), and the mismatch is reported
    # separately, not folded into the PASS/FAIL.
    es_gen = results[("es", "generated")]
    table7_actual_w = 502.8777
    table7_actual_hour = 14.0
    peak_matches_actual = (abs(es_gen["peak_w"] - table7_actual_w) < 0.01
                           and abs(es_gen["peak_hour"] - table7_actual_hour) < 1e-6)
    print("C-a peak  es new=%.4f W at %.2f:00  actual-shipped=%.4f W at "
          "%.2f:00  %s"
          % (es_gen["peak_w"], es_gen["peak_hour"], table7_actual_w,
             table7_actual_hour, "PASS" if peak_matches_actual else "FAIL"))
    print("C-a NOTE  manuscript Table 7 prose states Spain 518 W; the actual "
          "shipped data (agg_diurnal.csv / generate_fig06.py) is 502.8777 W. "
          "Hour (14:00) matches. This is a pre-existing manuscript/data "
          "mismatch, unrelated to --pool, and is NOT corrected by this job.")

    ca_ok = ca_hash_ok and peak_matches_actual
    print("C-a OVERALL: %s" % ("PASS" if ca_ok else "FAIL"))

    # -- C-b: real and raked runs give output hashes DIFFERENT from generated.
    cb_ok = True
    for fold in FOLDS:
        gen_md5 = results[(fold, "generated")]["enduse_md5"]
        for source in ("real", "raked"):
            other_md5 = results[(fold, source)]["enduse_md5"]
            different = (other_md5 != gen_md5)
            cb_ok = cb_ok and different
            print("C-b non-identity  fold=%s  %s vs generated  %s"
                  % (fold, source, "PASS (differs)" if different
                    else "FAIL (identical -- --pool is not being read)"))
    print("C-b OVERALL: %s" % ("PASS" if cb_ok else "FAIL"))

    # -- C-c: raked_<c>.jsonl contains zero diaries whose ORIGINAL source
    #    country is c. Re-checked here directly from the pool file (belt and
    #    suspenders on top of `4thJ_p3_build_pools.py`'s own check).
    cc_ok = True
    for fold in FOLDS:
        raked_path = os.path.join(pools_dir, "raked_%s.jsonl" % fold)
        n_self = 0
        n_total = 0
        with io.open(raked_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                n_total += 1
                if r.get("donor_country") == fold:
                    n_self += 1
        ok = (n_self == 0)
        cc_ok = cc_ok and ok
        print("C-c no-self-donor  fold=%s  self-donor rows=%d of %d  %s"
              % (fold, n_self, n_total, "PASS" if ok else "FAIL"))
    print("C-c OVERALL: %s" % ("PASS" if cc_ok else "FAIL"))

    print("")
    print("=" * 78)
    if not ca_ok:
        print("C-a FAILED -- the real/raked numbers below are PRINTED FOR "
              "DIAGNOSIS ONLY and MUST NOT be reported as results.")
    else:
        print("C-a PASSED (against the actual shipped data) -- results below "
              "are trustworthy reproductions of the pipeline's own output.")
    print("=" * 78)
    print("")
    print("%-8s %-10s %10s %12s %s" % ("fold", "source", "peak_hour",
                                       "peak_W", "output_file"))
    for fold in FOLDS:
        for source in SOURCES:
            r = results[(fold, source)]
            print("%-8s %-10s %10.2f %12.4f %s"
                  % (fold, source, r["peak_hour"], r["peak_w"],
                     r["stock_path"]))

    summary = {
        "controls": {"C_a_hash_ok": ca_hash_ok,
                     "C_a_peak_matches_actual_shipped": peak_matches_actual,
                     "C_a_overall": ca_ok, "C_b_overall": cb_ok,
                     "C_c_overall": cc_ok},
        "table7_manuscript_vs_actual_mismatch": {
            "manuscript_es_14h_w": 518,
            "actual_shipped_es_14h_w": table7_actual_w,
            "note": "pre-existing, not caused by P3, not corrected here"},
        "results": dict(("%s|%s" % k, v) for k, v in results.items()),
    }
    summary_path = os.path.join(out_root, "P3_results_summary.json")
    io.open(summary_path, "w", encoding="utf-8", newline="").write(
        json.dumps(summary, indent=2, sort_keys=True))
    print("")
    print("summary written: %s" % summary_path)
    return 0 if (ca_ok and cb_ok and cc_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
