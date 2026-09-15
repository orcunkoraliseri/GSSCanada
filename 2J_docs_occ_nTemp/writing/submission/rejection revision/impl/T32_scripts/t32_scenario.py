"""t32_scenario.py -- T32: build S-Revert-std (spec addendum Sec 5) plus a
primary-basis regression guard, on the T18c Nb-f stock. Adds
--jump-basis {primary,std} to T26's S-Revert build; lambda is fixed at 0
(the jump is fully removed either way -- only WHICH jump/slope differs).

Task doc:  2026-09-15_T32_wp2_srevert_std_build.md.
Spec:      2026-09-15_WP2_scenario_spec.md Sec 2 (trigger) and Sec 5
           (S-Revert-std definition, acceptance).
Code base: T26_scripts/t26_scenario.py (imported, not copied), which itself
           imports T20_scripts/t20_d1.py the same importlib way. This file
           reuses BOTH via the same house pattern -- no pipeline source
           file, and no line of t26_scenario.py or t20_d1.py, is edited.

target_primary[s,t] = clip(stock_rate[s,t] + 8*pre_slope[s,t] - jump[s,t], 0, 1)
    -- lambda=0 fixed; IDENTICAL formula and inputs to T26's own lambda=0.0
    (S-Revert) build (t26_scenario.compute_pre_slope_and_jump, unstandardized).
    This is Array task 0, the regression guard (G0, task doc Design): its
    output must reproduce
    T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv exactly (share of
    equal occupancy cells = 1.0). If it does not, task 1's output is not
    used (task doc Design/G0).

target_std[s,t] = clip(stock_rate[s,t] + 8*pre_slope_std[s,t] - jump_std[s,t], 0, 1)
    -- spec Sec 5: pre_slope_std/jump_std are t26_scenario.py's own
    compute_standardized_jump() arrays (real respondents of all four
    cycles reweighted to the rebuilt stock's AGEGRP x SEX x LFTAG counts,
    line refit), used for BOTH the slope and the jump this time -- unlike
    T26's own --std-jump flag, which only ever reported jump_std/pre_slope_std
    (never fed them into a target). This is Array task 1 (S-Revert-std).
"""
import sys
import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jump-basis", dest="basis", required=True, choices=["primary", "std"])
    ap.add_argument("--stock", required=True,
                     help="T18c Nb-f 21CEN22GSS_aug_Full_Aggregated_framev2.csv (same stock as T26)")
    ap.add_argument("--diaries", required=True,
                     help="FULL all-cycle augmented_diaries.csv (T18-staged read-only copy)")
    ap.add_argument("--scripts-dir", required=True,
                     help="T26_scripts/ dir: t26_scenario.py, t20_d1.py, plus copies of "
                          "06_forecast_rake.py, 05_postlink_rake.py, 07_aug_to_bem.py, "
                          "07_bemIntegrationGSS_val.py, activity_loads.py (read-only, T26 dir)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--validate", action="store_true",
                     help="run 07_bemIntegrationGSS_val.py --year 2030 on this output "
                          "(task doc: validator on each output, as t26_job.sh does)")
    args = ap.parse_args()

    scripts_dir = Path(args.scripts_dir)
    out_dir = Path(args.out_dir)
    bems_dir = out_dir / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    # Load t26_scenario.py itself (task doc Design: "imports t26_scenario.py"),
    # which in turn loads t20_d1.py the same importlib way when ITS OWN main()
    # runs -- but here we only call t26's module-level helper functions, so we
    # load t20_d1.py ourselves too, for the functions t26_scenario.py's own
    # main() would otherwise wire up (compute_stock_rate, write_person_table_csv,
    # run_validator, _step, log, _require, _load_module). Neither script's own
    # `if __name__=="__main__":` fires via this load path.
    t26 = _load("t32_t26_scenario", scripts_dir / "t26_scenario.py")
    t20 = _load("t32_t20_d1", scripts_dir / "t20_d1.py")

    log = t20.log
    _step = t20._step

    stock_path = t20._require(args.stock, "Nb-f stock (21CEN22GSS_aug_Full_Aggregated_framev2.csv)")
    diaries_path = t20._require(args.diaries, "full augmented_diaries.csv")

    log(f"jump_basis={args.basis} stock={stock_path} diaries={diaries_path} out_dir={out_dir}")

    forecast_rake_mod = _step(
        "load 06_forecast_rake.py",
        lambda: t20._load_module("t32_forecast_rake", scripts_dir / "06_forecast_rake.py"))
    postlink_rake_mod = _step(
        "load 05_postlink_rake.py (via forecast_rake's own loader)",
        lambda: forecast_rake_mod._load_postlink_rake_module())

    stock_df = _step("read stock", lambda: pd.read_csv(stock_path, low_memory=False))
    log(f"  stock: {len(stock_df):,} person-rows")

    stock_rate = _step(
        "compute stock_rate[s,t] (t20_d1.compute_stock_rate, imported unmodified)",
        lambda: t20.compute_stock_rate(stock_df))

    if args.basis == "primary":
        pre_slope, jump, _obs_rates = _step(
            "compute pre_slope[s,t] + jump[s,t] "
            "(t26_scenario.compute_pre_slope_and_jump, unstandardized/primary)",
            lambda: t26.compute_pre_slope_and_jump(forecast_rake_mod, diaries_path))
    else:
        jump, pre_slope, collapse_report = _step(
            "compute pre_slope_std[s,t] + jump_std[s,t] "
            "(t26_scenario.compute_standardized_jump, spec Sec 5)",
            lambda: t26.compute_standardized_jump(stock_df, diaries_path))
        log(f"  standardized-jump collapse report: {collapse_report}")

    # lambda fixed at 0: target = clip(stock_rate + 8*pre_slope - jump, 0, 1).
    # For basis=primary this is byte-for-byte T26's own lambda=0.0 formula
    # (same stock_rate function, same pre_slope/jump computation) -- the
    # mechanical basis for the G0 regression guard.
    target = np.clip(stock_rate + 8.0 * pre_slope - jump, 0.0, 1.0)
    for si, s in enumerate(t26.STRATA):
        log(f"  target[{t26.STRATA_LBL[s]}] daily mean = {target[si].mean()*100:.3f}% "
            f"(stock_rate {stock_rate[si].mean()*100:.3f}%, "
            f"8*pre_slope {8*pre_slope[si].mean()*100:+.3f}pp, "
            f"jump {jump[si].mean()*100:+.3f}pp)")

    df_raked, total_flips, n_1to0, n_0to1, incoherence = _step(
        "rake_2030(stock, target) [06_forecast_rake.py binary-flip rake, seed 42]",
        lambda: forecast_rake_mod.rake_2030(stock_df, target))
    log(f"  rake: {total_flips:,} hom30 flips ({n_1to0:,} 1->0, {n_0to1:,} 0->1), "
        f"{incoherence:,} act/hom incoherences pre-act30-rake")

    forecast_rake_mod._AUG_PATH = diaries_path
    df_final, act_diag = _step(
        "_joint_act30_rake_2030(df_raked) [act30 consistency, hom30 read-only]",
        lambda: forecast_rake_mod._joint_act30_rake_2030(df_raked, postlink_rake_mod))

    targets_csv = out_dir / f"t32_targets_{args.basis}.csv"
    person_table_csv = out_dir / f"t32_person_table_{args.basis}.csv"
    _step("write targets CSV (t26_scenario.write_targets_csv, imported unmodified)",
          lambda: t26.write_targets_csv(targets_csv, stock_rate, pre_slope, jump, 0.0, target, log))
    _step("write 2030 person table CSV",
          lambda: t20.write_person_table_csv(person_table_csv, df_final))

    a2b = _step("load 07_aug_to_bem.py",
                lambda: t20._load_module("t32_a2b", scripts_dir / "07_aug_to_bem.py"))
    a2b.BEMS = bems_dir
    a2b.assemble_2030 = lambda joint=False: df_final  # the ONE step this wrapper replaces

    def _run_a2b():
        old_argv = sys.argv
        sys.argv = ["07_aug_to_bem.py", "--year", "2030"]
        try:
            a2b.main()
        finally:
            sys.argv = old_argv

    _step("a2b.main() --year 2030 [complete_day_types + convert, unedited]", _run_a2b)

    if args.validate:
        _step("run validator (t20_d1.run_validator, imported unmodified)",
              lambda: t20.run_validator(scripts_dir, bems_dir, person_table_csv, out_dir))

    log(f"=========== JUMP-BASIS {args.basis} DONE ===========")


if __name__ == "__main__":
    main()
