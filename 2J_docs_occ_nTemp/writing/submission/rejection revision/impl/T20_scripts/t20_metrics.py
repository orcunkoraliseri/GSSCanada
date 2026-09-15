"""t20_metrics.py -- T20 acceptance metrics: N0 (null forecast), N1
(intended step), R-rake (achieved-vs-target after the rake), and an md5
helper for N3 (no-leakage).

Reads ONLY files t20_d1.py / t20_job.sh already wrote (or the T18-produced
Arm N references it is handed) -- never recomputes a number from scratch
that a job artifact already carries, per feedback_verify_progress_log_claims
in spirit: the collector should be able to re-derive every number in
t20_metrics_<mode>.csv straight from these inputs.

Usage:
  --action md5 --path <file>
      Prints the file's md5 hex to stdout (one line). Used by t20_job.sh
      for N3's before/after capture, on the Speed venv python (never on the
      login node).

  --action report --mode {null,main}
      --arm-n-2022-bem <ArmN BEM_Schedules_2022.csv, T18 output, read-only>
      --bem <this run's BEM_Setup/BEM_Schedules_2030.csv>
      --targets <this run's t20_targets_<mode>.csv>
      --person-table <this run's t20_person_table_<mode>.csv>
      --out <t20_metrics_<mode>.csv>
      Writes N0 (mode=null), N1 (mode=main), and R-rake (both modes) rows.

Column citations: HOM/ACT slot-column naming and dtype_label() are the same
convention as 07_aug_to_bem.py:24-25,36-41 (copied here per T12 t12_diag.py's
own precedent of copying the occupancy-only reconstruction pieces rather
than importing activity_loads, which this metrics script does not need).
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

N_SLOTS = 48
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
STRATA = [1, 2, 3]
STRATA_LBL = {1: "WD", 2: "Sat", 3: "Sun"}


def md5_file(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dtype_label(code, bedrm):
    # copied verbatim from 07_aug_to_bem.py:36-41 / t12_diag.py:206-214
    try:
        code = int(code)
    except (ValueError, TypeError):
        return str(code)
    if code == 2:
        try:
            b = int(float(bedrm))
        except (ValueError, TypeError):
            b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(code, str(code))


def rows(measure, day_type, group, value_pp, note=""):
    return dict(measure=measure, day_type=day_type, group=group,
                value_pp=round(float(value_pp), 4), note=note)


def load_bem(path):
    usecols = ["SIM_HH_ID", "Day_Type", "Hour", "DTYPE", "Occupancy_Schedule"]
    return pd.read_csv(path, usecols=usecols, low_memory=False)


def n0_null_forecast(out_rows, bem_null_path, arm_n_bem_2022_path):
    """N0: null BEM_Schedules_2030.csv occupancy columns equal Arm N
    BEM_Schedules_2022.csv occupancy columns -- household weekday/weekend
    at-home means within 0.05 pp, national and per archetype; share of
    cells exactly equal."""
    null_bem = load_bem(bem_null_path)
    ref_bem = load_bem(arm_n_bem_2022_path)

    for label, day_type in (("weekday", "Weekday"), ("weekend", "Weekend")):
        a = null_bem[null_bem.Day_Type == day_type]
        b = ref_bem[ref_bem.Day_Type == day_type]
        va = a.Occupancy_Schedule.mean() * 100
        vb = b.Occupancy_Schedule.mean() * 100
        out_rows.append(rows("N0_national", label, "null_vs_2022",
                              va - vb, f"null {va:.4f}% vs 2022 {vb:.4f}%"))
        for arch, ga in a.groupby("DTYPE"):
            gb = b[b.DTYPE == arch]
            if len(gb) == 0:
                continue
            va_a = ga.Occupancy_Schedule.mean() * 100
            vb_a = gb.Occupancy_Schedule.mean() * 100
            out_rows.append(rows("N0_archetype", label, arch, va_a - vb_a,
                                  f"null {va_a:.4f}% vs 2022 {vb_a:.4f}%"))

    merged = pd.merge(
        null_bem, ref_bem, on=["SIM_HH_ID", "Day_Type", "Hour"],
        suffixes=("_null", "_2022"), how="inner")
    n_common = len(merged)
    n_exact = int((merged.Occupancy_Schedule_null == merged.Occupancy_Schedule_2022).sum())
    share = (n_exact / n_common * 100) if n_common else float("nan")
    out_rows.append(rows("N0_cells_exact_equal", "both", "share_pct", share,
                          f"{n_exact:,}/{n_common:,} cells exactly equal "
                          f"(join on SIM_HH_ID+Day_Type+Hour)"))


def n1_intended_step(out_rows, bem_main_path, arm_n_bem_2022_path, targets_csv):
    """N1: main minus Arm N 2022, household weekday at-home change vs the
    mean over weekday slots of (target - stock_rate); Sat/Sun and per
    archetype too."""
    main_bem = load_bem(bem_main_path)
    ref_bem = load_bem(arm_n_bem_2022_path)
    tgt = pd.read_csv(targets_csv)

    for label, day_type in (("weekday", "Weekday"), ("weekend", "Weekend")):
        a = main_bem[main_bem.Day_Type == day_type]
        b = ref_bem[ref_bem.Day_Type == day_type]
        va = a.Occupancy_Schedule.mean() * 100
        vb = b.Occupancy_Schedule.mean() * 100
        out_rows.append(rows("N1_national", label, "main_minus_2022",
                              va - vb, f"main {va:.4f}% vs 2022 {vb:.4f}%"))
        for arch, ga in a.groupby("DTYPE"):
            gb = b[b.DTYPE == arch]
            if len(gb) == 0:
                continue
            va_a = ga.Occupancy_Schedule.mean() * 100
            vb_a = gb.Occupancy_Schedule.mean() * 100
            out_rows.append(rows("N1_archetype", label, f"{day_type}_{arch}",
                                  va_a - vb_a, f"main {va_a:.4f}% vs 2022 {vb_a:.4f}%"))

    for s in STRATA:
        sub = tgt[tgt.stratum == s]
        delta_pp = (sub.target - sub.stock_rate).mean() * 100
        out_rows.append(rows("N1_design_target", STRATA_LBL[s], "target_minus_stock_rate",
                              delta_pp, "mean over this stratum's 48 slots"))


def r_rake(out_rows, targets_csv, person_table_csv):
    """R-rake: per stratum and slot, achieved person rate after the rake
    vs target; max abs diff reported, flag any slot > 0.5 pp."""
    tgt = pd.read_csv(targets_csv)
    usecols = ["DDAY_STRATA"] + HOM_COLS
    person = pd.read_csv(person_table_csv, usecols=usecols, low_memory=False)

    for s in STRATA:
        sub = person[person.DDAY_STRATA == s]
        tgt_s = tgt[tgt.stratum == s].sort_values("slot")
        if len(sub) == 0 or len(tgt_s) != N_SLOTS:
            out_rows.append(rows("R_rake", STRATA_LBL[s], "max_abs_diff_pp",
                                  float("nan"), "no rows / target mismatch"))
            continue
        achieved = sub[HOM_COLS].values.astype(float).mean(axis=0)
        target = tgt_s["target"].values.astype(float)
        diff_pp = np.abs(achieved - target) * 100
        max_diff = float(diff_pp.max())
        n_flagged = int((diff_pp > 0.5).sum())
        out_rows.append(rows("R_rake", STRATA_LBL[s], "max_abs_diff_pp", max_diff,
                              f"{n_flagged}/{N_SLOTS} slots > 0.5 pp"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", choices=["md5", "report"], required=True)
    # md5
    ap.add_argument("--path")
    # report
    ap.add_argument("--mode", choices=["null", "main"])
    ap.add_argument("--arm-n-2022-bem")
    ap.add_argument("--bem")
    ap.add_argument("--targets")
    ap.add_argument("--person-table")
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.action == "md5":
        if not args.path:
            raise SystemExit("--action md5 requires --path")
        print(md5_file(args.path))
        return

    # --action report
    for req in ("mode", "arm_n_2022_bem", "bem", "targets", "person_table", "out"):
        if getattr(args, req) is None:
            raise SystemExit(f"--action report requires --{req.replace('_', '-')}")

    out_rows = []
    if args.mode == "null":
        n0_null_forecast(out_rows, args.bem, args.arm_n_2022_bem)
    else:
        n1_intended_step(out_rows, args.bem, args.arm_n_2022_bem, args.targets)
    r_rake(out_rows, args.targets, args.person_table)

    df = pd.DataFrame(out_rows, columns=["measure", "day_type", "group", "value_pp", "note"])
    df.to_csv(args.out, index=False)
    print(f"wrote {len(df)} metric rows -> {args.out}", flush=True)
    for _, r in df.iterrows():
        print(f"  [{r.measure}] {r.day_type}/{r.group}: {r.value_pp} pp -- {r.note}", flush=True)


if __name__ == "__main__":
    main()
