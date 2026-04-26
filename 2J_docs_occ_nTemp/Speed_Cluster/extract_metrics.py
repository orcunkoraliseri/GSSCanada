#!/usr/bin/env python3
"""
extract_metrics.py — Read diagnostics_v4_statistical.json, append one row to results.csv.
Usage: python extract_metrics.py <diag_json> <tag> <results_csv> <archive_dir>
Appends: tag, composite, at_home_gap_rms_pp, spouse_gap_pp, act_js, cop_cal_mae, timestamp
Uses file locking (fcntl) to avoid CSV corruption from parallel array-job appends.
Also copies the JSON into archive_dir for traceability.
"""
import fcntl
import json
import math
import os
import shutil
import sys
from datetime import datetime, timezone


def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <diag_json> <tag> <results_csv> <archive_dir>",
              file=sys.stderr)
        sys.exit(1)

    diag_json, tag, results_csv, archive_dir = (
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    )

    with open(diag_json) as f:
        d = json.load(f)

    composite     = d["composite"]["composite_score"]
    at_home_rms   = d["composite"]["components"]["at_home_gap_rms_pp"]
    act_js        = d["composite"]["components"]["act_js_mean"]
    cop_cal_mae   = d["composite"]["components"]["cop_cal_mae"]
    spouse_gap_pp = d["bootstrap_cis"]["copresence"]["Spouse"]["gap_pp"]

    ts  = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row = f"{tag},{composite:.6f},{at_home_rms:.6f},{spouse_gap_pp:.6f},{act_js:.6f},{cop_cal_mae:.6f},{ts}\n"
    hdr = "tag,composite,at_home_gap_rms_pp,spouse_gap_pp,act_js,cop_cal_mae,timestamp\n"

    # Archive the full JSON (for per-trial traceability)
    os.makedirs(archive_dir, exist_ok=True)
    shutil.copy(diag_json, os.path.join(archive_dir, "diagnostics_v4_statistical.json"))

    # Append row to results CSV with exclusive file lock (safe under parallel array jobs)
    os.makedirs(os.path.dirname(os.path.abspath(results_csv)), exist_ok=True)
    with open(results_csv, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            if f.tell() == 0:
                f.write(hdr)
            f.write(row)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

    print(f"  Appended to {results_csv}: {row.strip()}")

    gates_pass = (
        composite < 1.045
        and at_home_rms <= 5.3
        and spouse_gap_pp <= 10.0
        and act_js <= 0.05
    )
    print(f"  composite={composite:.3f}  at_home_rms={at_home_rms:.1f}pp  "
          f"spouse_gap={spouse_gap_pp:.1f}pp  act_js={act_js:.4f}  cop_cal_mae={cop_cal_mae:.3f}")
    print(f"  Gates {'PASS' if gates_pass else 'FAIL'} "
          f"(composite<1.045 AT_HOME<=5.3pp Spouse<=10pp act_JS<=0.05)")


if __name__ == "__main__":
    main()
