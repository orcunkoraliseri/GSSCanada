"""t26_metrics.py -- T26 acceptance metrics: SC0 (nesting), SC1 (intended
step), SC2 (order, cross-scenario), SC3 (jump sanity, reported), SC5
(rake achieved-vs-target). SC4 (md5 before/after) is done in bash inside
t26_job.sh (T20/T18 precedent: md5 goes inside the job, not python).

Usage:
  --action report --lam {1.0,0.5,0.0}
      --arm-n-2022-bem <ArmN BEM_Schedules_2022.csv, T18 output, read-only>
      --bem <this scenario's BEM_Setup/BEM_Schedules_2030.csv>
      --targets <this scenario's t26_targets_lambda_<lam>.csv>
      --person-table <this scenario's t26_person_table_lambda_<lam>.csv>
      --out <t26_metrics_lambda_<lam>.csv>
      [--t20-main-bem <T20 out/main/BEM_Setup/BEM_Schedules_2030.csv>]
          required only for --lam 1.0 (SC0 nesting check).
      Writes SC1, SC3, SC5 (all lam), plus SC0 when --lam 1.0.

  --action compare
      --persist-bem <lambda_1.0 BEM_Schedules_2030.csv>
      --partial-bem <lambda_0.5 BEM_Schedules_2030.csv>
      --revert-bem  <lambda_0.0 BEM_Schedules_2030.csv>
      --out <t26_compare_metrics.csv>
      Writes SC2 (weekday household at-home order: Revert < Partial <
      Persist, strict; national + per archetype). Run once, in the
      dependent compare job, AFTER all three array tasks (spec Sec 4/design:
      "SC2 ... after all three tasks, so run it in a final dependent job").
"""
import argparse

import numpy as np
import pandas as pd

N_SLOTS = 48
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
STRATA = [1, 2, 3]
STRATA_LBL = {1: "WD", 2: "Sat", 3: "Sun"}
SCEN_LABEL = {1.0: "S-Persist", 0.5: "S-Partial", 0.0: "S-Revert"}


def rows(measure, day_type, group, value_pp, note=""):
    return dict(measure=measure, day_type=day_type, group=group,
                value_pp=round(float(value_pp), 4), note=note)


def load_bem(path):
    usecols = ["SIM_HH_ID", "Day_Type", "Hour", "DTYPE", "Occupancy_Schedule"]
    return pd.read_csv(path, usecols=usecols, low_memory=False)


def sc1_intended_step(out_rows, bem_path, arm_n_2022_bem_path, targets_csv, label):
    """SC1: household weekday at-home change vs Arm N 2022, within 0.5pp of
    the mean over weekday slots of (target - stock_rate); Sat/Sun and per
    archetype reported."""
    main_bem = load_bem(bem_path)
    ref_bem = load_bem(arm_n_2022_bem_path)
    tgt = pd.read_csv(targets_csv)

    for lbl, day_type in (("weekday", "Weekday"), ("weekend", "Weekend")):
        a = main_bem[main_bem.Day_Type == day_type]
        b = ref_bem[ref_bem.Day_Type == day_type]
        va = a.Occupancy_Schedule.mean() * 100
        vb = b.Occupancy_Schedule.mean() * 100
        out_rows.append(rows("SC1_national", lbl, label, va - vb,
                              f"{label} {va:.4f}% vs ArmN2022 {vb:.4f}%"))
        for arch, ga in a.groupby("DTYPE"):
            gb = b[b.DTYPE == arch]
            if len(gb) == 0:
                continue
            va_a = ga.Occupancy_Schedule.mean() * 100
            vb_a = gb.Occupancy_Schedule.mean() * 100
            out_rows.append(rows("SC1_archetype", lbl, f"{label}_{arch}", va_a - vb_a,
                                  f"{label} {va_a:.4f}% vs 2022 {vb_a:.4f}%"))

    sub_wd = tgt[tgt.stratum == 1]
    design_delta_pp = (sub_wd.target - sub_wd.stock_rate).mean() * 100
    out_rows.append(rows("SC1_design_target", "WD", "target_minus_stock_rate",
                          design_delta_pp, "mean over WD 48 slots; SC1 bound = within 0.5pp of this"))


def sc3_jump_sanity(out_rows, targets_csv, bem_path, arm_n_2022_bem_path, label):
    """SC3 (reported, not banded): national weekday mean of jump, and the
    at-home change 2022->2030 under this scenario. S-Revert is expected
    negative if the jump exceeds the 8-year trend."""
    tgt = pd.read_csv(targets_csv)
    for s, lbl in STRATA_LBL.items():
        sub = tgt[tgt.stratum == s]
        jump_daily_pp = sub["jump"].mean() * 100
        out_rows.append(rows("SC3_jump", lbl, "national_daily_mean_pp", jump_daily_pp,
                              "reported, not banded"))

    main_bem = load_bem(bem_path)
    ref_bem = load_bem(arm_n_2022_bem_path)
    a = main_bem[main_bem.Day_Type == "Weekday"]
    b = ref_bem[ref_bem.Day_Type == "Weekday"]
    delta = a.Occupancy_Schedule.mean() * 100 - b.Occupancy_Schedule.mean() * 100
    out_rows.append(rows("SC3_athome_change_2022_2030", "WD", label, delta,
                          "S-Revert expected negative if jump > 8yr trend"))


def sc5_rake(out_rows, targets_csv, person_table_csv):
    """SC5: per stratum and slot, achieved person rate after rake vs
    target; max abs diff reported, flag > 0.5 pp. Same pattern as T20's
    R-rake (t20_metrics.py r_rake)."""
    tgt = pd.read_csv(targets_csv)
    usecols = ["DDAY_STRATA"] + HOM_COLS
    person = pd.read_csv(person_table_csv, usecols=usecols, low_memory=False)

    for s in STRATA:
        sub = person[person.DDAY_STRATA == s]
        tgt_s = tgt[tgt.stratum == s].sort_values("slot")
        if len(sub) == 0 or len(tgt_s) != N_SLOTS:
            out_rows.append(rows("SC5_rake", STRATA_LBL[s], "max_abs_diff_pp",
                                  float("nan"), "no rows / target mismatch"))
            continue
        achieved = sub[HOM_COLS].values.astype(float).mean(axis=0)
        target = tgt_s["target"].values.astype(float)
        diff_pp = np.abs(achieved - target) * 100
        max_diff = float(diff_pp.max())
        n_flagged = int((diff_pp > 0.5).sum())
        out_rows.append(rows("SC5_rake", STRATA_LBL[s], "max_abs_diff_pp", max_diff,
                              f"{n_flagged}/{N_SLOTS} slots > 0.5 pp"))


def sc0_nesting(out_rows, bem_lambda1_path, t20_main_bem_path):
    """SC0: the lambda=1.0 build equals T20 main's BEM_Schedules_2030.csv
    occupancy columns exactly (share of equal cells = 1.0), or the
    scenario builds are not used (spec Sec 3)."""
    a = load_bem(bem_lambda1_path)
    b = load_bem(t20_main_bem_path)
    merged = pd.merge(a, b, on=["SIM_HH_ID", "Day_Type", "Hour"],
                       suffixes=("_l1", "_t20"), how="inner")
    n_common = len(merged)
    n_exact = int((merged.Occupancy_Schedule_l1 == merged.Occupancy_Schedule_t20).sum())
    share = (n_exact / n_common * 100) if n_common else float("nan")
    out_rows.append(rows("SC0_nesting", "both", "share_pct", share,
                          f"{n_exact:,}/{n_common:,} cells exactly equal "
                          f"(lambda=1.0 vs T20 main; join on SIM_HH_ID+Day_Type+Hour)"))


def sc2_order(out_rows, bem_persist, bem_partial, bem_revert):
    """SC2: weekday household at-home, strict order Revert < Partial <
    Persist. Reported per archetype too."""
    persist = load_bem(bem_persist)
    partial = load_bem(bem_partial)
    revert = load_bem(bem_revert)

    def wd_mean(df):
        return df[df.Day_Type == "Weekday"].Occupancy_Schedule.mean() * 100

    vp, vpa, vr = wd_mean(persist), wd_mean(partial), wd_mean(revert)
    ok = (vr < vpa) and (vpa < vp)
    out_rows.append(rows("SC2_national", "weekday", "order_check", vp,
                          f"Revert {vr:.4f}% < Partial {vpa:.4f}% < Persist {vp:.4f}% "
                          f"-> {'PASS' if ok else 'FAIL'}"))

    archs = set(persist[persist.Day_Type == "Weekday"].DTYPE.unique())
    archs &= set(partial[partial.Day_Type == "Weekday"].DTYPE.unique())
    archs &= set(revert[revert.Day_Type == "Weekday"].DTYPE.unique())
    for arch in sorted(archs):
        def wd_mean_arch(df):
            sub = df[(df.Day_Type == "Weekday") & (df.DTYPE == arch)]
            return sub.Occupancy_Schedule.mean() * 100
        ap_, aq_, ar_ = wd_mean_arch(persist), wd_mean_arch(partial), wd_mean_arch(revert)
        ok_a = (ar_ < aq_) and (aq_ < ap_)
        out_rows.append(rows("SC2_archetype", "weekday", str(arch), ap_,
                              f"Revert {ar_:.4f}% < Partial {aq_:.4f}% < "
                              f"Persist {ap_:.4f}% -> {'PASS' if ok_a else 'FAIL'}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", choices=["report", "compare"], required=True)
    # report
    ap.add_argument("--lam", type=float, choices=[1.0, 0.5, 0.0])
    ap.add_argument("--arm-n-2022-bem")
    ap.add_argument("--bem")
    ap.add_argument("--targets")
    ap.add_argument("--person-table")
    ap.add_argument("--t20-main-bem", default=None)
    # compare
    ap.add_argument("--persist-bem")
    ap.add_argument("--partial-bem")
    ap.add_argument("--revert-bem")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_rows = []

    if args.action == "report":
        for req in ("lam", "arm_n_2022_bem", "bem", "targets", "person_table"):
            if getattr(args, req) is None:
                raise SystemExit(f"--action report requires --{req.replace('_', '-')}")
        label = SCEN_LABEL[args.lam]
        sc1_intended_step(out_rows, args.bem, args.arm_n_2022_bem, args.targets, label)
        sc3_jump_sanity(out_rows, args.targets, args.bem, args.arm_n_2022_bem, label)
        sc5_rake(out_rows, args.targets, args.person_table)
        if args.lam == 1.0:
            if not args.t20_main_bem:
                raise SystemExit("--lam 1.0 requires --t20-main-bem for SC0")
            sc0_nesting(out_rows, args.bem, args.t20_main_bem)
    else:  # compare
        for req in ("persist_bem", "partial_bem", "revert_bem"):
            if getattr(args, req) is None:
                raise SystemExit(f"--action compare requires --{req.replace('_', '-')}")
        sc2_order(out_rows, args.persist_bem, args.partial_bem, args.revert_bem)

    df = pd.DataFrame(out_rows, columns=["measure", "day_type", "group", "value_pp", "note"])
    df.to_csv(args.out, index=False)
    print(f"wrote {len(df)} metric rows -> {args.out}", flush=True)
    for _, r in df.iterrows():
        print(f"  [{r.measure}] {r.day_type}/{r.group}: {r.value_pp} pp -- {r.note}", flush=True)


if __name__ == "__main__":
    main()
