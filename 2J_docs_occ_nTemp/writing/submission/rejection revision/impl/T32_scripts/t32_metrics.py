"""t32_metrics.py -- T32 acceptance metrics: G0 (regression guard, task 0
[--jump-basis primary] vs T26's own lambda=0.0 S-Revert build), SC1/SC5
readout (task 1, S-Revert-std), and the final compare (G0 + SC1/SC5 readout
+ the weekday at-home change and its difference from S-Revert, -3.2081 pp,
T26 collector). Reuses t26_metrics.py's own sc0_nesting / sc1_intended_step
/ sc3_jump_sanity / sc5_rake / rows / load_bem (imported, not copied) --
same functions, T32's own file paths.

Usage:
  --action report --basis {primary,std}
      --arm-n-2022-bem <Nb-f BEM_Schedules_2022.csv, T18c output, read-only>
      --bem <this task's BEM_Setup/BEM_Schedules_2030.csv>
      --targets <this task's t32_targets_<basis>.csv>
      --person-table <this task's t32_person_table_<basis>.csv>
      --out <t32_metrics_<basis>.csv>
      [--t26-revert-bem <T26/out/lambda_0.0/.../BEM_Schedules_2030.csv>]
          required only for --basis primary (G0 regression guard).

  --action compare
      --bem <task 0's (guard_primary) BEM_Schedules_2030.csv>
      --t26-revert-bem <T26/out/lambda_0.0/.../BEM_Schedules_2030.csv>
      --std-bem <task 1's (std) BEM_Schedules_2030.csv>
      --arm-n-2022-bem <Nb-f BEM_Schedules_2022.csv>
      [--std-targets --std-person-table]  (SC5 readout on S-Revert-std)
      --out <t32_compare_metrics.csv>
      Writes G0 (task 0 vs T26 lambda=0.0), the S-Revert-std weekday
      at-home change 2022->2030 and its difference from S-Revert
      (-3.2081 pp, T26 collector), and SC5 readout when the std targets/
      person-table are given.
"""
import argparse
import importlib.util
from pathlib import Path

import pandas as pd

S_REVERT_WEEKDAY_ATHOME_CHANGE_PP = -3.2081  # T26 collector, spec Sec 5 addendum


def _load_t26_metrics(scripts_dir):
    spec = importlib.util.spec_from_file_location(
        "t32_t26_metrics", str(Path(scripts_dir) / "t26_metrics.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", choices=["report", "compare"], required=True)
    ap.add_argument("--scripts-dir", required=True,
                     help="T26_scripts/ dir holding t26_metrics.py (imported, not copied)")
    # report
    ap.add_argument("--basis", choices=["primary", "std"])
    ap.add_argument("--arm-n-2022-bem")
    ap.add_argument("--bem")
    ap.add_argument("--targets")
    ap.add_argument("--person-table")
    ap.add_argument("--t26-revert-bem", default=None)
    # compare (extra)
    ap.add_argument("--std-bem", default=None)
    ap.add_argument("--std-targets", default=None)
    ap.add_argument("--std-person-table", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t26m = _load_t26_metrics(args.scripts_dir)
    out_rows = []

    if args.action == "report":
        for req in ("basis", "arm_n_2022_bem", "bem", "targets", "person_table"):
            if getattr(args, req) is None:
                raise SystemExit(f"--action report requires --{req.replace('_', '-')}")
        label = "primary" if args.basis == "primary" else "S-Revert-std"
        t26m.sc1_intended_step(out_rows, args.bem, args.arm_n_2022_bem, args.targets, label)
        t26m.sc3_jump_sanity(out_rows, args.targets, args.bem, args.arm_n_2022_bem, label)
        t26m.sc5_rake(out_rows, args.targets, args.person_table)
        if args.basis == "primary":
            if not args.t26_revert_bem:
                raise SystemExit("--basis primary requires --t26-revert-bem for G0")
            n_before = len(out_rows)
            t26m.sc0_nesting(out_rows, args.bem, args.t26_revert_bem)
            # sc0_nesting appends exactly one row; relabel measure G0 (task
            # doc's own name) without touching t26_metrics.py itself.
            for i in range(n_before, len(out_rows)):
                out_rows[i] = dict(out_rows[i], measure="G0_regression_guard")
    else:  # compare
        for req in ("bem", "t26_revert_bem", "std_bem", "arm_n_2022_bem"):
            if getattr(args, req) is None:
                raise SystemExit(f"--action compare requires --{req.replace('_', '-')}")

        n_before = len(out_rows)
        t26m.sc0_nesting(out_rows, args.bem, args.t26_revert_bem)
        for i in range(n_before, len(out_rows)):
            out_rows[i] = dict(out_rows[i], measure="G0_regression_guard")

        # Weekday household at-home change 2022->2030 under S-Revert-std,
        # and its difference from S-Revert (-3.2081 pp, T26 collector).
        std_bem = t26m.load_bem(args.std_bem)
        ref_bem = t26m.load_bem(args.arm_n_2022_bem)
        a = std_bem[std_bem.Day_Type == "Weekday"]
        b = ref_bem[ref_bem.Day_Type == "Weekday"]
        delta_std = a.Occupancy_Schedule.mean() * 100 - b.Occupancy_Schedule.mean() * 100
        diff_from_s_revert = delta_std - S_REVERT_WEEKDAY_ATHOME_CHANGE_PP
        out_rows.append(t26m.rows(
            "SC_athome_change_2022_2030", "WD", "S-Revert-std", delta_std,
            f"S-Revert-std {delta_std:.4f}pp vs S-Revert {S_REVERT_WEEKDAY_ATHOME_CHANGE_PP:.4f}pp "
            f"(diff {diff_from_s_revert:+.4f}pp; S-Revert value from T26 collector, not recomputed here)"))

        if args.std_targets and args.std_person_table:
            t26m.sc5_rake(out_rows, args.std_targets, args.std_person_table)

    df = pd.DataFrame(out_rows, columns=["measure", "day_type", "group", "value_pp", "note"])
    df.to_csv(args.out, index=False)
    print(f"wrote {len(df)} metric rows -> {args.out}", flush=True)
    for _, r in df.iterrows():
        print(f"  [{r.measure}] {r.day_type}/{r.group}: {r.value_pp} pp -- {r.note}", flush=True)


if __name__ == "__main__":
    main()
