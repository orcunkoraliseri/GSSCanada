"""t26_scenario.py -- T26: build ONE WP2 2030 work-from-home scenario
(S-Persist / S-Partial / S-Revert, indexed by --lambda) on the T18 Arm N
rebuilt-2022 stock.

Task doc:  2026-09-15_T26_wp2_scenario_builds.md.
Spec:      2026-09-15_WP2_scenario_spec.md (design, acceptance SC0-SC5).
Code base: T20_scripts/t20_d1.py (imported, not copied) + 06_forecast_rake.py
           / 05_postlink_rake.py / 07_aug_to_bem.py /
           07_bemIntegrationGSS_val.py (imported unedited, same importlib
           house pattern t20_d1.py itself uses).

target_lambda[s,t] = clip(stock_rate[s,t] + 8*pre_slope[s,t]
                            - (1 - lambda) * jump[s,t], 0, 1)
  lambda = 1.0 -> S-Persist (identical formula to T20 main; SC0 nesting:
                  (1-lambda)=0, so target_1.0 == T20's own
                  stock_rate + 8*pre_slope target, byte-for-byte, since
                  stock_rate comes from the SAME imported
                  t20_d1.compute_stock_rate() and pre_slope from the same
                  06_forecast_rake.py polyfit on the same --diaries file).
  lambda = 0.5 -> S-Partial (half the COVID jump survives to 2030).
  lambda = 0.0 -> S-Revert (the jump is fully gone; 2030 sits on the
                  pre-COVID trend, expressed as a shift on the stock).

jump[s,t] = obs_2022[s,t] - trend_st(2022), the SAME polyfit as
06_forecast_rake.py:150-161 (project_to_2030()) -- but project_to_2030()
itself only returns pre_slopes; its 3rd return value ("intercepts" by the
calling convention t20_d1.py itself uses) is a literal None
(06_forecast_rake.py:183: `return target, pre_slopes, None, reports`), so
the intercept needed for trend(2022) cannot be recovered from that
function's own return value. This file does NOT call project_to_2030();
it reruns the identical per-(stratum x slot) np.polyfit(pre_years, ..., 1)
loop itself (06_forecast_rake.py:150-161, same pre_years, same per-slot
call), computed ONCE here so both pre_slope (same value project_to_2030
would give) and jump come out of a single loop -- not a second, divergent
implementation of the slope, just the same computation with the intercept
kept instead of discarded.

Everything else this file needs -- compute_observed_marginals(),
rake_2030(), _joint_act30_rake_2030(), the a2b.main() drive, the Step-7
validator -- is the SAME unedited imported function t20_d1.py itself
calls, loaded via t20_d1.py's own _load_module() importlib house pattern
(re-used here, not re-implemented) so 06_forecast_rake.py's own
`if __name__ == "__main__":` block never fires.

t20_d1.py's own compute_stock_rate(), write_person_table_csv(),
run_validator(), _step(), log(), _require(), _load_module(), and the
STRATA/STRATA_LBL/N_SLOTS/HOM_COLS/ACT_COLS constants are imported and
called/used UNMODIFIED (t20_d1.py itself is loaded as a module via the
same importlib pattern it uses on the pipeline scripts, so its own
`if __name__ == "__main__":` guard never fires either) -- this is the
"imports t20_d1.py functions (no copy-paste drift)" the task doc asks
for. No pipeline source file, and no line of t20_d1.py, is edited.

Standardized-jump sensitivity (spec Sec 2): reported only, never used in
any target formula. Real respondents (all 4 cycles, IS_SYNTHETIC==0) are
reweighted to the rebuilt stock's AGEGRP x SEX x LFTAG cell counts
(post-stratification weights, collapsing to AGEGRP x SEX then AGEGRP
alone when a cycle's sample cell is empty), the same pre-COVID line is
refit on the reweighted rates, and the resulting jump_std is compared to
the primary (unstandardized) jump. Computed only when --std-jump is
passed (t26_job.sh passes it for the lambda=1.0 task only, since jump and
pre_slope do not depend on lambda -- see task doc Decisions).
"""
import sys
import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Small constants duplicated at module level (same precedent as t20_d1.py
# duplicating them from 06_forecast_rake.py's own STRATA/N_SLOTS/HOM_COLS):
# needed before t20_d1.py is importlib-loaded at runtime.
STRATA = [1, 2, 3]
STRATA_LBL = {1: "WD", 2: "Sat", 3: "Sun"}
N_SLOTS = 48
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

SCEN_LABEL = {1.0: "S-Persist", 0.5: "S-Partial", 0.0: "S-Revert"}
PRE_COVID_CYCLES = (2005, 2010, 2015)


def compute_pre_slope_and_jump(forecast_rake_mod, diaries_path):
    """pre_slope[s,t] (same value 06_forecast_rake.py's own
    project_to_2030() would return) and jump[s,t] = obs_2022[s,t] -
    trend_st(2022), from ONE pass of the :150-161 polyfit loop (kept the
    intercept project_to_2030() discards)."""
    obs_rates = forecast_rake_mod.compute_observed_marginals(str(diaries_path))
    pre_years = np.array(PRE_COVID_CYCLES, dtype=float)
    pre_slope = np.zeros((3, N_SLOTS))
    jump = np.zeros((3, N_SLOTS))
    for si, s in enumerate(STRATA):
        pre_matrix = np.stack([obs_rates[(yr, s)] for yr in PRE_COVID_CYCLES], axis=0)
        obs_2022 = obs_rates[(2022, s)]
        for t in range(N_SLOTS):
            coef = np.polyfit(pre_years, pre_matrix[:, t], 1)  # [slope, intercept], same call as :154
            slope, intercept = coef[0], coef[1]
            pre_slope[si, t] = slope
            jump[si, t] = obs_2022[t] - (slope * 2022.0 + intercept)
    return pre_slope, jump, obs_rates


def write_targets_csv(path, stock_rate, pre_slope, jump, lam, target, log):
    rows = []
    for si, s in enumerate(STRATA):
        for t in range(N_SLOTS):
            rows.append(dict(stratum=s, slot=t + 1, lam=lam,
                              stock_rate=float(stock_rate[si, t]),
                              pre_slope=float(pre_slope[si, t]),
                              jump=float(jump[si, t]),
                              target=float(target[si, t])))
    pd.DataFrame(rows).to_csv(path, index=False)
    log(f"  wrote targets (lambda={lam}) -> {path}")


# ── Standardized-jump sensitivity (spec Sec 2; reported only) ──────────────

def _standardized_weights(sub, stock_asl, stock_as, stock_a):
    """Post-stratification weights for one (cycle, stratum) real-respondent
    slice: AGEGRP x SEX x LFTAG target if the sample has that cell, else
    collapse to AGEGRP x SEX, else AGEGRP alone. Returns (weights,
    n_collapsed_to_AS, n_collapsed_to_A, n_no_stock_match)."""
    n = len(sub)
    samp_asl = sub.groupby(["AGEGRP", "SEX", "LFTAG"]).size().rename("m_asl")
    samp_as = sub.groupby(["AGEGRP", "SEX"]).size().rename("m_as")
    samp_a = sub.groupby(["AGEGRP"]).size().rename("m_a")
    j = sub[["AGEGRP", "SEX", "LFTAG"]].copy()
    j = j.join(samp_asl, on=["AGEGRP", "SEX", "LFTAG"])
    j = j.join(stock_asl, on=["AGEGRP", "SEX", "LFTAG"])
    j = j.join(samp_as, on=["AGEGRP", "SEX"])
    j = j.join(stock_as, on=["AGEGRP", "SEX"])
    j = j.join(samp_a, on=["AGEGRP"])
    j = j.join(stock_a, on=["AGEGRP"])
    use_asl = j["m_asl"].gt(0) & j["n_asl"].notna()
    use_as = (~use_asl) & j["m_as"].gt(0) & j["n_as"].notna()
    use_a = (~use_asl) & (~use_as) & j["m_a"].gt(0) & j["n_a"].notna()
    w = np.ones(n)
    w = np.where(use_asl, j["n_asl"] / j["m_asl"], w)
    w = np.where(use_as, j["n_as"] / j["m_as"], w)
    w = np.where(use_a, j["n_a"] / j["m_a"], w)
    n_no_match = int(n - int(use_asl.sum()) - int(use_as.sum()) - int(use_a.sum()))
    return w, int(use_as.sum()), int(use_a.sum()), n_no_match


def compute_standardized_jump(stock_df, diaries_path):
    usecols = ["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC", "AGEGRP", "SEX", "LFTAG"] + HOM_COLS
    diaries = pd.read_csv(str(diaries_path), usecols=usecols, low_memory=False)
    obs = diaries[diaries["IS_SYNTHETIC"] == 0].copy()

    stock_asl = stock_df.groupby(["AGEGRP", "SEX", "LFTAG"]).size().rename("n_asl")
    stock_as = stock_df.groupby(["AGEGRP", "SEX"]).size().rename("n_as")
    stock_a = stock_df.groupby(["AGEGRP"]).size().rename("n_a")

    rates_by_year = {}
    collapse_report = {}
    for yr in (2005, 2010, 2015, 2022):
        rates_by_year[yr] = np.zeros((3, N_SLOTS))
        for si, s in enumerate(STRATA):
            sub = obs[(obs["CYCLE_YEAR"] == yr) & (obs["DDAY_STRATA"] == s)].copy()
            key = f"{yr}_{STRATA_LBL[s]}"
            if len(sub) == 0:
                collapse_report[key] = dict(n_rows=0, collapsed_to_AS=0, collapsed_to_A=0, no_stock_match=0)
                continue
            w, n_as, n_a, n_none = _standardized_weights(sub, stock_asl, stock_as, stock_a)
            collapse_report[key] = dict(n_rows=len(sub), collapsed_to_AS=n_as,
                                         collapsed_to_A=n_a, no_stock_match=n_none)
            hom = sub[HOM_COLS].values.astype(float)
            wsum = w.sum()
            rates_by_year[yr][si] = ((hom * w[:, None]).sum(axis=0) / wsum) if wsum > 0 else hom.mean(axis=0)

    pre_years = np.array(PRE_COVID_CYCLES, dtype=float)
    pre_slope_std = np.zeros((3, N_SLOTS))
    jump_std = np.zeros((3, N_SLOTS))
    for si, s in enumerate(STRATA):
        pre_matrix = np.stack([rates_by_year[yr][si] for yr in PRE_COVID_CYCLES], axis=0)
        obs_2022_std = rates_by_year[2022][si]
        for t in range(N_SLOTS):
            coef = np.polyfit(pre_years, pre_matrix[:, t], 1)
            slope, intercept = coef[0], coef[1]
            pre_slope_std[si, t] = slope
            jump_std[si, t] = obs_2022_std[t] - (slope * 2022.0 + intercept)
    return jump_std, pre_slope_std, collapse_report


def write_std_jump_json(out_dir, stock_df, diaries_path, jump_primary, log):
    jump_std, pre_slope_std, collapse_report = compute_standardized_jump(stock_df, diaries_path)
    wd_primary = float(jump_primary[0].mean() * 100)   # stratum index 0 = WD
    wd_std = float(jump_std[0].mean() * 100)
    diff_pp = wd_std - wd_primary
    payload = dict(
        description=("Standardized-jump sensitivity (WP2 spec Sec 2): real "
                      "respondents reweighted to the rebuilt stock's AGEGRP x "
                      "SEX x LFTAG counts; reported only, not used in any "
                      "scenario target formula."),
        national_weekday_mean_pp=dict(primary=wd_primary, standardized=wd_std,
                                       diff_pp=diff_pp, flag_over_1pp=abs(diff_pp) > 1.0),
        per_stratum_daily_mean_pp={
            STRATA_LBL[s]: dict(primary=float(jump_primary[si].mean() * 100),
                                 standardized=float(jump_std[si].mean() * 100))
            for si, s in enumerate(STRATA)},
        collapse_report=collapse_report,
    )
    path = Path(out_dir) / "t26_std_jump_sensitivity.json"
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    log(f"  standardized jump: WD primary {wd_primary:.4f}pp vs standardized {wd_std:.4f}pp "
        f"(diff {diff_pp:+.4f}pp, flag>1.0pp={abs(diff_pp) > 1.0}) -> {path}")
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lambda", dest="lam", type=float, required=True, choices=[1.0, 0.5, 0.0])
    ap.add_argument("--stock", required=True,
                     help="T18 Arm N 21CEN22GSS_aug_Full_Aggregated_excl.csv")
    ap.add_argument("--diaries", required=True,
                     help="FULL all-cycle augmented_diaries.csv (T18-staged read-only copy)")
    ap.add_argument("--scripts-dir", required=True,
                     help="dir holding t20_d1.py plus copies of 06_forecast_rake.py, "
                          "05_postlink_rake.py, 07_aug_to_bem.py, "
                          "07_bemIntegrationGSS_val.py, activity_loads.py")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--validate", action="store_true",
                     help="run 07_bemIntegrationGSS_val.py --year 2030 on this "
                          "scenario's output (task doc: validator on each output)")
    ap.add_argument("--std-jump", action="store_true",
                     help="also compute+write the standardized-jump sensitivity "
                          "(spec Sec 2); lambda-independent, run once (task 0)")
    args = ap.parse_args()

    scripts_dir = Path(args.scripts_dir)
    out_dir = Path(args.out_dir)
    bems_dir = out_dir / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    # Load t20_d1.py itself as a module (same importlib house pattern it
    # uses on the pipeline scripts) so its own `if __name__=="__main__":`
    # never fires, then call its functions directly -- "imports t20_d1.py
    # functions (no copy-paste drift)".
    import importlib.util
    t20_path = scripts_dir / "t20_d1.py"
    spec = importlib.util.spec_from_file_location("t26_t20_d1", str(t20_path))
    t20 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t20)

    log = t20.log
    _step = t20._step

    stock_path = t20._require(args.stock, "Arm N stock (21CEN22GSS_aug_Full_Aggregated_excl.csv)")
    diaries_path = t20._require(args.diaries, "full augmented_diaries.csv")

    log(f"lambda={args.lam} ({SCEN_LABEL[args.lam]}) stock={stock_path} "
        f"diaries={diaries_path} out_dir={out_dir}")

    forecast_rake_mod = _step(
        "load 06_forecast_rake.py",
        lambda: t20._load_module("t26_forecast_rake", scripts_dir / "06_forecast_rake.py"))
    postlink_rake_mod = _step(
        "load 05_postlink_rake.py (via forecast_rake's own loader)",
        lambda: forecast_rake_mod._load_postlink_rake_module())

    stock_df = _step("read stock", lambda: pd.read_csv(stock_path, low_memory=False))
    log(f"  stock: {len(stock_df):,} person-rows")

    stock_rate = _step(
        "compute stock_rate[s,t] (t20_d1.compute_stock_rate, imported unmodified)",
        lambda: t20.compute_stock_rate(stock_df))

    pre_slope, jump, _obs_rates = _step(
        "compute pre_slope[s,t] + jump[s,t] (06_forecast_rake.py:150-161 polyfit, "
        "intercept kept)",
        lambda: compute_pre_slope_and_jump(forecast_rake_mod, diaries_path))

    target = np.clip(stock_rate + 8.0 * pre_slope - (1.0 - args.lam) * jump, 0.0, 1.0)
    for si, s in enumerate(STRATA):
        log(f"  target[{STRATA_LBL[s]}] daily mean = {target[si].mean()*100:.3f}% "
            f"(stock_rate {stock_rate[si].mean()*100:.3f}%, "
            f"8*pre_slope {8*pre_slope[si].mean()*100:+.3f}pp, "
            f"(1-lambda)*jump {((1.0-args.lam)*jump[si]).mean()*100:+.3f}pp)")

    df_raked, total_flips, n_1to0, n_0to1, incoherence = _step(
        "rake_2030(stock, target_lambda) [06_forecast_rake.py binary-flip rake, seed 42]",
        lambda: forecast_rake_mod.rake_2030(stock_df, target))
    log(f"  rake: {total_flips:,} hom30 flips ({n_1to0:,} 1->0, {n_0to1:,} 0->1), "
        f"{incoherence:,} act/hom incoherences pre-act30-rake")

    forecast_rake_mod._AUG_PATH = diaries_path
    df_final, act_diag = _step(
        "_joint_act30_rake_2030(df_raked) [act30 consistency, hom30 read-only]",
        lambda: forecast_rake_mod._joint_act30_rake_2030(df_raked, postlink_rake_mod))

    lam_tag = f"{args.lam}"
    targets_csv = out_dir / f"t26_targets_lambda_{lam_tag}.csv"
    person_table_csv = out_dir / f"t26_person_table_lambda_{lam_tag}.csv"
    _step("write targets CSV",
          lambda: write_targets_csv(targets_csv, stock_rate, pre_slope, jump, args.lam, target, log))
    _step("write 2030 person table CSV",
          lambda: t20.write_person_table_csv(person_table_csv, df_final))

    a2b = _step("load 07_aug_to_bem.py",
                lambda: t20._load_module("t26_a2b", scripts_dir / "07_aug_to_bem.py"))
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

    if args.std_jump:
        _step("standardized-jump sensitivity (spec Sec 2, reported only)",
              lambda: write_std_jump_json(out_dir, stock_df, diaries_path, jump, log))

    log(f"=========== LAMBDA {args.lam} ({SCEN_LABEL[args.lam]}) DONE ===========")


if __name__ == "__main__":
    main()
