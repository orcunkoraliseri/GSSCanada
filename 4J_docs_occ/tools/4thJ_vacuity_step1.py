#!/usr/bin/env python3
"""
4J Step 1 vacuity guard V1.a, ROUND 2 (2026-08-16).

V1.b (inputs printed before any verdict), V1.c (status read from the
computing process) and V1.d (unrecognised code printed and refused) are
per-run properties of one country's own battery and stay scored inside each
country's own gate runner (4thJ_gates_step1_<country>.py) -- moving them
would make them unfalsifiable (manager decision, 2026-08-16).

Only V1.a moves here: it is a property of the ROUND (does the CORPUS -- all
three countries -- have an episodes_<country>.parquet present in the SAME
run-stamped output directory), scored once, after all three per-country jobs
have completed. Submit this job with --dependency=afterok:<es>:<it>:<uk> so
it cannot race a slow country the way round 1's unchained per-country V1.a
did (Spain takes ~18 minutes; IT and UK looked for the sibling parquets
before Spain had written its own -- a race, not a threshold regression).

FAIL below 3 of 3 countries (ES/UK/IT, decision 16, France excluded) having
their own episodes_<country>.parquet present in --out.

🔴 A guard satisfied by stale files from a previous run is not a guard: this
scan is restricted to THIS run's own --out dir, never a shared/leftover
outputs_step1/ directory.

Usage:
    python 4thJ_vacuity_step1.py --out <run-stamped outputs_step1 dir>
"""

import argparse
import os

SIBLING_FILES = {"ES": "episodes_spain.parquet", "UK": "episodes_uk.parquet",
                  "IT": "episodes_italy.parquet"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True,
                     help="the run-stamped outputs_step1/run_<stamp> dir "
                          "shared by all four jobs this round")
    args = ap.parse_args()
    out = args.out

    present = [c for c, f in SIBLING_FILES.items()
               if os.path.exists(os.path.join(out, f))]
    missing = sorted(set(SIBLING_FILES) - set(present))
    v1a = "FAIL" if len(present) < 3 else "PASS"

    lines = []
    lines.append("=" * 78)
    lines.append("V1.a -- ROUND-LEVEL VACUITY GUARD (scored ONCE per round, here, not")
    lines.append("inside any per-country gate runner)")
    lines.append("=" * 78)
    lines.append(f"  run dir   : {out}")
    lines.append(f"  countries with an episodes_<country>.parquet present: "
                 f"{sorted(present)} ({len(present)} of {len(SIBLING_FILES)})")
    lines.append(f"  missing   : {missing}")
    lines.append(f"  threshold : FAIL below 3 of 3 (decision 16, France excluded)")
    lines.append(f"  verdict   : {v1a}")
    lines.append("")
    lines.append("  Submitted with --dependency=afterok:<es>:<it>:<uk> so this check")
    lines.append("  cannot race a slow country the way round 1's unchained per-country")
    lines.append("  V1.a did. This scan is restricted to THIS run's own --out dir,")
    lines.append("  never a shared/leftover outputs_step1/ directory -- a guard")
    lines.append("  satisfied by stale files from a previous run is not a guard.")
    lines.append("")
    lines.append("  V1.b, V1.c, V1.d remain per-run properties of one country's own")
    lines.append("  battery and are scored, and printed, inside each country's own")
    lines.append("  4thJ_gates_step1_<country>.py; NOT re-scored here.")

    txt = "\n".join(lines) + "\n"
    with open(os.path.join(out, "vacuity_report_step1.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
