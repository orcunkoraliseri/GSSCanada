"""t20_d1.py -- T20 wrapper: build the 2030 person table by D1 (structural-
break pre-slope forecast) on the T18 Arm N rebuilt-2022 stock, then run the
UNCHANGED 07_aug_to_bem.py complete_day_types()+convert() path to produce
BEM_Schedules_2030.csv, optionally followed by the Step-7 validator.

Task doc: 2026-09-15_T20_wp1_d1_2030_build.md.
Method precedent: T18 t18_pipeline.py's importlib+monkeypatch house pattern
-- load each pipeline script via importlib.util.spec_from_file_location() so
its own `if __name__ == "__main__":` block never fires, then set the
freshly-loaded module's own path/behaviour globals BEFORE calling its
functions. Function bodies stay byte-for-byte untouched; only module-level
names they resolve at call time change (T18 t18_pipeline.py:16-25 confirms
this is safe -- constants are re-read from the module global, not passed as
arguments). This file reuses that exact technique for the same reason T18
needed it: 05_census_linkage.py's own BASE-path computation cannot resolve
correctly from the live eSim/ directory depth (T18 Verified section), and
07_aug_to_bem.py / 06_forecast_rake.py / 07_bemIntegrationGSS_val.py have the
same "script-relative BASE" pattern, so every path this file needs is set
explicitly rather than relied upon.

T12 t12_diag.py M4 (pre_slope) / M5 (household reconstruction) established
the standalone reconstruction pattern this design is built on, but T12's own
copy is occupancy-only (it deliberately does not import activity_loads).
T20 needs the FULL 17-col BEM_Schedules_2030.csv (metabolic + Step-9
equipment/lighting) so the Step-7 validator can run against it -- so unlike
t12_diag.py, this file imports 07_aug_to_bem.py FOR REAL (with
activity_loads.py staged alongside it, per T18's own note that
activity_loads.py must be co-located: 07_aug_to_bem.py does
`sys.path.insert(0, str(HERE)); import activity_loads`, executed at module-
import time, which cannot be monkeypatched after the fact).

Design (2026-09-15_T20_wp1_d1_2030_build.md, "Design" section), as built:

  Persons: the T18 Arm N stock (`21CEN22GSS_aug_Full_Aggregated_excl.csv`).
    Each person keeps their own 2022 diary -- 07_aug_to_bem.py's own
    assemble_2030() (:182-193, random redraw from a 2030 pool) is NEVER
    called. Instead, the module attribute `a2b.assemble_2030` itself is
    monkeypatched to a closure returning the ALREADY-COMPUTED 2030 person
    table below, so a2b.main() (unedited) drives everything downstream of
    person-table construction -- exactly "a wrapper replaces only the step
    that builds the 2030 person table."

  Targets: target[s,t] = clip(stock_rate[s,t] + 8*pre_slope[s,t], 0, 1).
    stock_rate[s,t] = plain (unweighted) person mean of hom30_t over stock
      persons in stratum s -- same "plain mean" pattern as
      07_aug_to_bem.py:97 (`df.groupby(keys, sort=True)[HOM].mean()`),
      computed here per DDAY_STRATA stratum instead of per household.
    pre_slope[s,t] = EXACTLY 06_forecast_rake.py:138-165's project_to_2030()
      slope computation (per-(stratum x slot) OLS on real IS_SYNTHETIC==0
      2005/2010/2015 respondents), fed by compute_observed_marginals()
      (06_forecast_rake.py:100-123) -- both imported unedited via
      importlib, called on the FULL (all-cycle) augmented_diaries.csv
      (--diaries; the T18-staged read-only copy), never the 2022-only Arm N
      filter file. project_to_2030()'s OWN target/report return values (its
      2022-observed-jump target) are discarded here -- only its `pre_slopes`
      return value (the OLS slope itself) feeds the T20 formula above.
    null mode: pre_slope forced to an all-zero (3,48) array before the
      target computation -- same code path, zero forecast signal (N0).

  Rake: 06_forecast_rake.py's own rake_2030(df, target) (seed 42, boundary-
    preferred binary flip, imported unedited) applied directly to the stock
    person rows, with T20's own target array (not the module's own
    project_to_2030 target -- only the RAKE MECHANISM is reused, matching
    the task doc's "Import the function ... called on the stock person rows
    per stratum"). Then 06_forecast_rake.py's own --joint act30-conditional
    step (_joint_act30_rake_2030(), which itself asserts hom30 is left
    byte-unchanged) is applied so act30 stays internally consistent with
    whichever hom30 bits the rake flipped -- its target is the 2022 OBSERVED
    marginals from the module's own `_AUG_PATH` global, monkeypatched here
    to --diaries (same technique as above) so it reads the FULL diaries
    file rather than whatever path the module's own file-relative BASE
    would otherwise compute.

No pipeline source file is edited. Every path a called function resolves is
set as an explicit attribute on the freshly loaded module object before that
function is invoked (T18 precedent, T13 Q3 option (a)).
"""
import sys
import time
import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def _step(name, fn):
    log(f"--- STEP START: {name} ---")
    try:
        result = fn()
    except Exception:
        log(f"--- STEP FAILED: {name} ---")
        raise
    log(f"--- STEP OK: {name} ---")
    return result


def _require(path, label):
    """Fail loudly, with the step name, if a required input is missing.
    Extra points requirement: the Arm N inputs do not exist until T18's
    array (1328301) finishes -- this is the defense-in-depth check beyond
    the sbatch --dependency=afterok gate."""
    p = Path(path)
    step = f"input check ({label})"
    if not p.exists():
        log(f"--- STEP FAILED: {step} --- missing required input: {p}")
        raise FileNotFoundError(f"[{step}] missing required input: {p}")
    log(f"--- STEP OK: {step} --- found: {p} ({p.stat().st_size:,} bytes)")
    return p


def _load_module(name, path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing staged script: {path}")
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


STRATA = [1, 2, 3]
STRATA_LBL = {1: "WD", 2: "Sat", 3: "Sun"}
N_SLOTS = 48
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def compute_stock_rate(stock_df):
    """stock_rate[s,t] = plain (unweighted) person mean of hom30_t over
    stock persons in stratum s. Design doc: 'plain mean, as
    07_aug_to_bem.py:97' (df.groupby(...)[HOM].mean() pattern, per stratum
    here instead of per household)."""
    rate = np.zeros((3, N_SLOTS))
    for si, s in enumerate(STRATA):
        sub = stock_df[stock_df["DDAY_STRATA"] == s]
        if len(sub) == 0:
            log(f"  [WARN] stratum {s}: 0 stock rows")
            continue
        rate[si] = sub[HOM_COLS].values.astype(float).mean(axis=0)
    return rate


def compute_pre_slope(forecast_rake_mod, diaries_path):
    """Exactly 06_forecast_rake.py:138-165's project_to_2030() slope
    computation, called on the FULL (all-cycle) augmented_diaries.csv.
    Its own target/report return values are the module's OWN 2022-jump
    target -- discarded; only pre_slopes (the OLS slope) is reused."""
    obs_rates = forecast_rake_mod.compute_observed_marginals(str(diaries_path))
    _target_unused, pre_slopes, _intercepts_unused, _reports_unused = \
        forecast_rake_mod.project_to_2030(obs_rates)
    return pre_slopes  # (3, 48)


def build_2030_table(mode, stock_df, forecast_rake_mod, postlink_rake_mod,
                      diaries_path):
    """The ONE step this wrapper replaces: builds the 2030 person table from
    the stock. Each person keeps their own 2022 diary; no random redraw
    (assemble_2030 is never called)."""
    stock_rate = _step("compute stock_rate[s,t] (07_aug_to_bem.py:97 pattern)",
                        lambda: compute_stock_rate(stock_df))

    if mode == "null":
        pre_slope = np.zeros((3, N_SLOTS))
        log("null mode: pre_slope forced to 0 (N0 acceptance test)")
    else:
        pre_slope = _step(
            "compute pre_slope[s,t] (06_forecast_rake.py:138-165, full diaries)",
            lambda: compute_pre_slope(forecast_rake_mod, diaries_path))

    target = np.clip(stock_rate + 8.0 * pre_slope, 0.0, 1.0)
    for si, s in enumerate(STRATA):
        log(f"  target[{STRATA_LBL[s]}] daily mean = {target[si].mean()*100:.3f}% "
            f"(stock_rate {stock_rate[si].mean()*100:.3f}%, "
            f"8*pre_slope mean {8*pre_slope[si].mean()*100:+.3f} pp)")

    df_raked, total_flips, n_1to0, n_0to1, incoherence = _step(
        "rake_2030(stock, target) [06_forecast_rake.py binary-flip rake, seed 42]",
        lambda: forecast_rake_mod.rake_2030(stock_df, target))
    log(f"  rake: {total_flips:,} hom30 flips ({n_1to0:,} 1->0, {n_0to1:,} 0->1), "
        f"{incoherence:,} act/hom incoherences pre-act30-rake")

    # R-rake (also reported by t20_metrics.py from the persisted artifacts;
    # logged here too so it lands in the job log even if metrics fails).
    max_abs_diff = 0.0
    for si, s in enumerate(STRATA):
        sub = df_raked[df_raked["DDAY_STRATA"] == s]
        if len(sub) == 0:
            continue
        achieved = sub[HOM_COLS].values.astype(float).mean(axis=0)
        d = np.abs(achieved - target[si]) * 100
        max_abs_diff = max(max_abs_diff, float(d.max()))
    log(f"  R-rake: max |achieved - target| across strata/slots = {max_abs_diff:.4f} pp")

    # Joint act30-conditional step: keeps act30 consistent with whichever
    # hom30 bits the binary rake flipped. Monkeypatch the module's own
    # _AUG_PATH global (T18-style) so its internal 2022-observed reference
    # reads the FULL diaries file, not whatever its file-relative BASE
    # would otherwise resolve to.
    forecast_rake_mod._AUG_PATH = diaries_path
    df_final, act_diag = _step(
        "_joint_act30_rake_2030(df_raked) [act30 consistency, hom30 read-only]",
        lambda: forecast_rake_mod._joint_act30_rake_2030(df_raked, postlink_rake_mod))

    return df_final, stock_rate, pre_slope, target


def write_targets_csv(path, stock_rate, pre_slope, target):
    rows = []
    for si, s in enumerate(STRATA):
        for t in range(N_SLOTS):
            rows.append(dict(stratum=s, slot=t + 1,
                              stock_rate=float(stock_rate[si, t]),
                              pre_slope=float(pre_slope[si, t]),
                              target=float(target[si, t])))
    pd.DataFrame(rows).to_csv(path, index=False)
    log(f"  wrote targets -> {path}")


def write_person_table_csv(path, df_final):
    cols = [c for c in ["HH_ID", "DDAY_STRATA", "DTYPE", "BEDRM"] if c in df_final.columns]
    cols = cols + ACT_COLS + HOM_COLS
    df_final[cols].to_csv(path, index=False)
    log(f"  wrote 2030 person table -> {path} ({len(df_final):,} rows)")


def run_validator(scripts_dir, bems_dir, person_table_path, out_dir):
    """07_bemIntegrationGSS_val.py --year 2030, called directly (bypasses its
    CLI entirely, same as t18_pipeline.py's _run_bval pattern -- the module
    has no main() to redirect via sys.argv for this class-based entry
    point). BEMS is monkeypatched to this job's own out dir. D2030_JOINT
    (the module's optional "calibrated source diaries" comparison target,
    self.diary in __init__) is monkeypatched to THIS run's own persisted
    2030 person table -- decision, see task doc Decisions: T20 has no
    separate "2030 forecast pool" file the way the real pipeline does (the
    stock persons ARE the pool here), so the faithful analogue of "the file
    the BEM was built from" is this run's own t20_person_table_main.csv.
    Without this monkeypatch, self.diary stays None and Section 3 checks
    3.3-3.5 collapse into a single WARN instead of up to 3 PASS lines,
    which would make the acceptance test's "28/28" unreachable for a reason
    unrelated to whether the build is actually correct."""
    bval = _load_module("t20_bval", scripts_dir / "07_bemIntegrationGSS_val.py")
    bval.BEMS = bems_dir
    bval.D2030_JOINT = Path(person_table_path)

    def _run():
        validator = bval.BEMIntegrationValidator(
            year="2030", outputs_dir=str(out_dir / "outputs_step7"))
        validator.run_all()

    _step("BEMIntegrationValidator(year=2030).run_all()", _run)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["null", "main"], required=True)
    ap.add_argument("--stock", required=True,
                     help="Arm N 21CEN22GSS_aug_Full_Aggregated_excl.csv (T18 output)")
    ap.add_argument("--diaries", required=True,
                     help="FULL all-cycle augmented_diaries.csv (T18-staged read-only copy)")
    ap.add_argument("--scripts-dir", required=True,
                     help="dir holding copies of 06_forecast_rake.py, "
                          "05_postlink_rake.py, 07_aug_to_bem.py, "
                          "07_bemIntegrationGSS_val.py, activity_loads.py")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--validate", action="store_true",
                     help="also run 07_bemIntegrationGSS_val.py --year 2030 "
                          "after writing BEM_Schedules_2030.csv (task doc: "
                          "'validator on task 1' -- mode main only)")
    args = ap.parse_args()

    stock_path = _require(args.stock, "Arm N stock (21CEN22GSS_aug_Full_Aggregated_excl.csv)")
    diaries_path = _require(args.diaries, "full augmented_diaries.csv")
    scripts_dir = Path(args.scripts_dir)
    out_dir = Path(args.out_dir)
    bems_dir = out_dir / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    log(f"mode={args.mode} stock={stock_path} diaries={diaries_path} out_dir={out_dir}")

    forecast_rake_mod = _step(
        "load 06_forecast_rake.py",
        lambda: _load_module("t20_forecast_rake", scripts_dir / "06_forecast_rake.py"))
    postlink_rake_mod = _step(
        "load 05_postlink_rake.py (via forecast_rake's own loader)",
        lambda: forecast_rake_mod._load_postlink_rake_module())

    stock_df = _step("read stock", lambda: pd.read_csv(stock_path, low_memory=False))
    log(f"  stock: {len(stock_df):,} person-rows")

    df_final, stock_rate, pre_slope, target = build_2030_table(
        args.mode, stock_df, forecast_rake_mod, postlink_rake_mod, diaries_path)

    targets_csv = out_dir / f"t20_targets_{args.mode}.csv"
    person_table_csv = out_dir / f"t20_person_table_{args.mode}.csv"
    _step("write targets CSV", lambda: write_targets_csv(targets_csv, stock_rate, pre_slope, target))
    _step("write 2030 person table CSV", lambda: write_person_table_csv(person_table_csv, df_final))

    a2b = _step(
        "load 07_aug_to_bem.py",
        lambda: _load_module("t20_a2b", scripts_dir / "07_aug_to_bem.py"))
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
        run_validator(scripts_dir, bems_dir, person_table_csv, out_dir)

    log(f"=========== MODE {args.mode} DONE ===========")


if __name__ == "__main__":
    main()
