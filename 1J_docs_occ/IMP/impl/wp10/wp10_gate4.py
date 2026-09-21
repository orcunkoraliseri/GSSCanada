"""
WP10 Stage 4: Gate 4 (G4.0-G4.3) for the manifest-driven main.py patch.

Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md

- G4.0 every finished run's household ids equal the manifest's row for that
  (neighbourhood, draw, year, building) -- read from mc_manifest_echo.csv, the file
  the patched main.py writes itself each iteration (never re-parses IDFs/.sql).
- G4.1 the old chooser is never called -- source-level check that
  _run_mc_neighbourhood contains the guard install/restore lines and zero real
  random.choice( call sites, PLUS a log scan proving the guard never fired for real.
- G4.2 the expected number of result files exists and none is empty.
- G4.3 the six Default tasks still give Gate 3's numbers -- Default_mean
  Heating/Cooling from aggregated_eui.csv vs the April reference file, read fresh
  every run (never hardcoded).

Every check prints its own `G4.x: VERDICT -- detail` line. A check that cannot be
evaluated (missing input) prints NOT_EVALUABLE, never FAIL. The script always
exits 0 if it ran to completion; the verdict lives in the printed lines, not the
exit code (repo convention, see wp9_2_gate2.py).

Modes:
  --mode selftest   Build tiny synthetic fixtures (good + deliberately wrong) in a
                     temp dir and score them -- run this FIRST, locally, before
                     trusting --mode real on cluster data (repo rule: seen failing
                     first).
  --mode real       Score the real cluster run.
"""
import argparse
import csv
import glob
import inspect
import os
import shutil
import sys
import tempfile

YEARS = ("2005", "2010", "2015", "2022", "2025")


def eprint(*a, **kw):
    print(*a, **kw)
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Shared readers
# ---------------------------------------------------------------------------

def read_manifest_lookup(manifest_path):
    lookup = {}
    with open(manifest_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["neighbourhood"], int(row["draw"]), row["year"], int(row["building_index"]))
            lookup[key] = row["hh_id"]
    return lookup


def read_default_eui(path):
    """{'Heating': float, 'Cooling': float} from an aggregated_eui.csv Default_mean column."""
    vals = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("EndUse") in ("Heating", "Cooling") and "Default_mean" in row:
                vals[row["EndUse"]] = float(row["Default_mean"])
    return vals


# ---------------------------------------------------------------------------
# G4.0
# ---------------------------------------------------------------------------

def check_g4_0(echo_paths_by_nu, manifest_lookup):
    missing_echo = [nu for nu, p in echo_paths_by_nu.items() if not os.path.isfile(p)]
    if not echo_paths_by_nu:
        return "NOT_EVALUABLE", "no echo files given"
    if missing_echo:
        return "NOT_EVALUABLE", f"missing mc_manifest_echo.csv for: {missing_echo}"

    total_rows = 0
    mismatches = []
    for nu, path in echo_paths_by_nu.items():
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_rows += 1
                key = (row["neighbourhood"], int(row["draw"]), row["year"], int(row["building_index"]))
                expected = manifest_lookup.get(key)
                if expected is None:
                    mismatches.append((key, "NOT_IN_MANIFEST", row["hh_id"]))
                elif expected != row["hh_id"]:
                    mismatches.append((key, expected, row["hh_id"]))

    if total_rows == 0:
        return "NOT_EVALUABLE", "zero rows read from any echo file"
    if mismatches:
        return "FAIL", f"{len(mismatches)} of {total_rows} rows mismatch manifest, e.g. {mismatches[:5]}"
    return "PASS", f"{total_rows} rows across {len(echo_paths_by_nu)} neighbourhoods, all match the manifest"


# ---------------------------------------------------------------------------
# G4.1
# ---------------------------------------------------------------------------

def check_g4_1(run_mc_neighbourhood_func, log_texts):
    try:
        src = inspect.getsource(run_mc_neighbourhood_func)
    except Exception as e:
        return "NOT_EVALUABLE", f"could not read source of _run_mc_neighbourhood: {e}"

    has_install = "random.choice = _wp10_forbidden_random_choice" in src
    has_restore = "random.choice = _wp10_orig_random_choice" in src
    call_site_lines = [
        line for line in src.splitlines()
        if "random.choice(" in line
        and not line.strip().startswith("#")
        and "random.choice()" not in line  # the guard's own text is always zero-arg
    ]
    guard_fired_in = [i for i, t in enumerate(log_texts) if "WP10 GUARD" in t]

    if guard_fired_in:
        return "FAIL", f"WP10 GUARD text found in {len(guard_fired_in)} log(s) -- old chooser was reached"
    if not has_install or not has_restore or call_site_lines:
        return "FAIL", (
            f"has_install={has_install} has_restore={has_restore} "
            f"real_call_sites={call_site_lines}"
        )
    return "PASS", (
        "guard install+restore present, zero real random.choice( call sites, "
        f"guard never fired in {len(log_texts)} scanned log(s)"
    )


# ---------------------------------------------------------------------------
# G4.2
# ---------------------------------------------------------------------------

def check_g4_2(nu_dirs, years=YEARS):
    if not nu_dirs:
        return "NOT_EVALUABLE", "no neighbourhood dirs given"

    problems = []
    checked = 0
    for nu, nu_dir in nu_dirs.items():
        expected = [
            os.path.join(nu_dir, "aggregated_eui.csv"),
            os.path.join(nu_dir, "Default", "eplusout.sql"),
            os.path.join(nu_dir, "iter_1", "mc_manifest_echo.csv"),
        ]
        for year in years:
            expected.append(os.path.join(nu_dir, "iter_1", year, "eplusout.sql"))
        for p in expected:
            checked += 1
            if not os.path.isfile(p):
                problems.append(("MISSING", p))
            elif os.path.getsize(p) == 0:
                problems.append(("EMPTY", p))

    if problems:
        return "FAIL", f"{len(problems)} of {checked} expected files missing/empty: {problems[:10]}"
    return "PASS", f"{checked} expected files present and non-empty across {len(nu_dirs)} neighbourhoods"


# ---------------------------------------------------------------------------
# G4.3
# ---------------------------------------------------------------------------

def check_g4_3(run_paths_by_nu, reference_paths_by_nu, tolerance=0.001):
    if not run_paths_by_nu:
        return "NOT_EVALUABLE", "no run aggregated_eui.csv paths given"

    problems = []
    checked = []
    for nu in sorted(run_paths_by_nu):
        run_path = run_paths_by_nu[nu]
        ref_path = reference_paths_by_nu.get(nu)
        if not run_path or not os.path.isfile(run_path):
            problems.append((nu, "RUN_FILE_MISSING", run_path))
            continue
        if not ref_path or not os.path.isfile(ref_path):
            problems.append((nu, "REFERENCE_FILE_MISSING", ref_path))
            continue
        run_vals = read_default_eui(run_path)
        ref_vals = read_default_eui(ref_path)
        for cat in ("Heating", "Cooling"):
            if cat not in run_vals or cat not in ref_vals:
                problems.append((nu, cat, "MISSING_CATEGORY"))
                continue
            diff = abs(run_vals[cat] - ref_vals[cat])
            checked.append((nu, cat, run_vals[cat], ref_vals[cat], diff))
            if diff > tolerance:
                problems.append((nu, cat, f"run={run_vals[cat]} ref={ref_vals[cat]} diff={diff:.6f}"))

    if not checked and not problems:
        return "NOT_EVALUABLE", "nothing to check"
    detail_ok = "; ".join(f"{nu}/{cat}: run={r:.4f} ref={rf:.4f} diff={d:.6f}" for nu, cat, r, rf, d in checked)
    if problems:
        return "FAIL", f"{len(problems)} problem(s): {problems}; matched so far: {detail_ok}"
    return "PASS", detail_ok


# ---------------------------------------------------------------------------
# real mode
# ---------------------------------------------------------------------------

def run_real(args):
    nus = [x.strip() for x in args.neighbourhoods.split(",") if x.strip()]

    manifest_lookup = read_manifest_lookup(args.manifest)
    eprint(f"GATE4: manifest {args.manifest}, rows={len(manifest_lookup)}")

    nu_dirs = {nu: os.path.join(args.batch_dir, nu) for nu in nus}
    echo_paths = {nu: os.path.join(nu_dirs[nu], "iter_1", "mc_manifest_echo.csv") for nu in nus}
    run_agg_paths = {nu: os.path.join(nu_dirs[nu], "aggregated_eui.csv") for nu in nus}
    ref_paths = {nu: args.reference_dir_template.format(nu=nu) for nu in nus}

    log_texts = []
    for pattern in (args.log_glob or []):
        for p in glob.glob(pattern):
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    log_texts.append(f.read())
            except OSError as e:
                eprint(f"GATE4: could not read log {p}: {e}")

    sys.path.insert(0, args.code_dir)
    import eSim_bem_utils.main as staged_main  # noqa: E402

    v0, d0 = check_g4_0(echo_paths, manifest_lookup)
    eprint(f"G4.0: {v0} -- {d0}")

    v1, d1 = check_g4_1(staged_main._run_mc_neighbourhood, log_texts)
    eprint(f"G4.1: {v1} -- {d1}")

    v2, d2 = check_g4_2(nu_dirs)
    eprint(f"G4.2: {v2} -- {d2}")

    v3, d3 = check_g4_3(run_agg_paths, ref_paths, tolerance=args.tolerance)
    eprint(f"G4.3: {v3} -- {d3}")

    eprint(f"GATE4 SUMMARY: G4.0={v0} G4.1={v1} G4.2={v2} G4.3={v3}")
    return 0


# ---------------------------------------------------------------------------
# selftest mode -- synthetic fixtures, seen failing first (repo convention)
# ---------------------------------------------------------------------------

def _write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def _write_agg(path, heating_default, cooling_default):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("EndUse,2005_mean,2005_std,Default_mean,Default_std\n")
        f.write(f"Heating,1.0,0.0,{heating_default},0.0\n")
        f.write(f"Cooling,1.0,0.0,{cooling_default},0.0\n")


def run_selftest(args):
    results = []

    def record(name, verdict, expect_verdict, detail):
        ok = verdict == expect_verdict
        results.append((name, ok))
        status = "PASS" if ok else "FAIL"
        eprint(f"[SELFTEST {status}] {name}: got {verdict} (expected {expect_verdict}) -- {detail}")

    tmp = tempfile.mkdtemp(prefix="wp10_gate4_selftest_")
    eprint(f"GATE4 SELFTEST: scratch dir {tmp}")

    manifest_path = os.path.join(tmp, "draw_manifest.csv")
    _write_csv(
        manifest_path,
        ["seed", "draw", "neighbourhood", "building_index", "building_dtype",
         "stratum_hhsize", "year", "hh_id", "hh_dtype", "hh_hhsize", "hh_pr",
         "weekday_hours", "weekend_hours"],
        [
            ["s", 1, "NUS_T1", 0, "SingleD", 2, "2005", "111", "SingleD", 2, "Quebec", 10, 12],
            ["s", 1, "NUS_T1", 1, "SingleD", 2, "2005", "222", "SingleD", 2, "Quebec", 11, 13],
        ],
    )
    manifest_lookup = read_manifest_lookup(manifest_path)

    # --- G4.0 good case: echo matches manifest exactly.
    good_echo = os.path.join(tmp, "good", "NUS_T1", "iter_1", "mc_manifest_echo.csv")
    _write_csv(good_echo, ["neighbourhood", "draw", "year", "building_index", "hh_id"],
               [["NUS_T1", 1, "2005", 0, "111"], ["NUS_T1", 1, "2005", 1, "222"]])
    v, d = check_g4_0({"NUS_T1": good_echo}, manifest_lookup)
    record("G4.0 good echo matches manifest", v, "PASS", d)

    # --- G4.0 seen-failing-first: one row's echoed hh_id disagrees with the manifest.
    bad_echo = os.path.join(tmp, "bad", "NUS_T1", "iter_1", "mc_manifest_echo.csv")
    _write_csv(bad_echo, ["neighbourhood", "draw", "year", "building_index", "hh_id"],
               [["NUS_T1", 1, "2005", 0, "999_WRONG"], ["NUS_T1", 1, "2005", 1, "222"]])
    v, d = check_g4_0({"NUS_T1": bad_echo}, manifest_lookup)
    record("G4.0 seen-failing-first: wrong echoed household", v, "FAIL", d)

    # --- G4.0 NOT_EVALUABLE: echo file missing.
    v, d = check_g4_0({"NUS_T1": os.path.join(tmp, "does_not_exist.csv")}, manifest_lookup)
    record("G4.0 missing echo file -> NOT_EVALUABLE", v, "NOT_EVALUABLE", d)

    # --- G4.1: needs the real patched module -- import via --code-dir if given.
    if args.code_dir:
        sys.path.insert(0, args.code_dir)
        import eSim_bem_utils.main as staged_main  # noqa: E402

        v, d = check_g4_1(staged_main._run_mc_neighbourhood, log_texts=[])
        record("G4.1 real patched module, no guard-fired logs", v, "PASS", d)

        v, d = check_g4_1(staged_main._run_mc_neighbourhood, log_texts=["...WP10 GUARD: random.choice..."])
        record("G4.1 seen-failing-first: guard text present in a log", v, "FAIL", d)

        # Deliberately-broken control: a stand-in function that still calls random.choice.
        def _broken_run_mc_neighbourhood():
            import random
            random.choice = lambda *_a, **_k: None

            def inner():
                random.choice([1, 2, 3])  # a real call site, not the guard's own text
            inner()

        v, d = check_g4_1(_broken_run_mc_neighbourhood, log_texts=[])
        record("G4.1 seen-failing-first: function missing guard lines", v, "FAIL", d)
    else:
        eprint("GATE4 SELFTEST: --code-dir not given, skipping G4.1 sub-tests")

    # --- G4.2 good case: all expected files present and non-empty.
    good_nu_dir = os.path.join(tmp, "g42_good", "NUS_T1")
    with open(os.path.join(_ensure_dir(os.path.join(good_nu_dir)), "aggregated_eui.csv"), "w") as f:
        f.write("x")
    with open(_ensure_dir(os.path.join(good_nu_dir, "Default")) + os.sep + "eplusout.sql", "w") as f:
        f.write("x")
    with open(_ensure_dir(os.path.join(good_nu_dir, "iter_1")) + os.sep + "mc_manifest_echo.csv", "w") as f:
        f.write("x")
    for year in YEARS:
        with open(_ensure_dir(os.path.join(good_nu_dir, "iter_1", year)) + os.sep + "eplusout.sql", "w") as f:
            f.write("x")
    v, d = check_g4_2({"NUS_T1": good_nu_dir})
    record("G4.2 good case: all expected files present, non-empty", v, "PASS", d)

    # --- G4.2 seen-failing-first: one expected file missing.
    missing_nu_dir = os.path.join(tmp, "g42_missing", "NUS_T1")
    shutil.copytree(good_nu_dir, missing_nu_dir)
    os.remove(os.path.join(missing_nu_dir, "iter_1", "2022", "eplusout.sql"))
    v, d = check_g4_2({"NUS_T1": missing_nu_dir})
    record("G4.2 seen-failing-first: one result file missing", v, "FAIL", d)

    # --- G4.2 seen-failing-first: one expected file present but empty.
    empty_nu_dir = os.path.join(tmp, "g42_empty", "NUS_T1")
    shutil.copytree(good_nu_dir, empty_nu_dir)
    open(os.path.join(empty_nu_dir, "aggregated_eui.csv"), "w").close()
    v, d = check_g4_2({"NUS_T1": empty_nu_dir})
    record("G4.2 seen-failing-first: one result file present but empty", v, "FAIL", d)

    # --- G4.3 good case: run numbers equal reference numbers.
    run_path = os.path.join(tmp, "g43_run", "NUS_T1_aggregated_eui.csv")
    ref_path = os.path.join(tmp, "g43_ref", "NUS_T1_aggregated_eui.csv")
    _write_agg(run_path, 35.1170, 45.6120)
    _write_agg(ref_path, 35.1170, 45.6120)
    v, d = check_g4_3({"NUS_T1": run_path}, {"NUS_T1": ref_path})
    record("G4.3 good case: run matches reference exactly", v, "PASS", d)

    # --- G4.3 seen-failing-first: run disagrees with reference beyond tolerance.
    run_path_wrong = os.path.join(tmp, "g43_run_wrong", "NUS_T1_aggregated_eui.csv")
    _write_agg(run_path_wrong, 99.0000, 45.6120)
    v, d = check_g4_3({"NUS_T1": run_path_wrong}, {"NUS_T1": ref_path})
    record("G4.3 seen-failing-first: run heating disagrees with reference", v, "FAIL", d)

    # --- G4.3 NOT_EVALUABLE-adjacent: missing reference file -> FAIL (not silently PASS).
    v, d = check_g4_3({"NUS_T1": run_path}, {"NUS_T1": os.path.join(tmp, "no_such_ref.csv")})
    record("G4.3 missing reference file -> FAIL, not PASS", v, "FAIL", d)

    n_fail = sum(1 for _, ok in results if not ok)
    eprint(f"GATE4 SELFTEST SUMMARY: {len(results)} checks, {n_fail} unexpected result(s)")
    return 1 if n_fail else 0


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="WP10 Stage 4 Gate 4")
    p.add_argument("--mode", choices=["real", "selftest"], required=True)
    p.add_argument("--manifest", help="path to draw_manifest.csv to check echoed runs against")
    p.add_argument("--batch-dir", help="parent dir containing NUS_RC{1..6}/ output subdirs")
    p.add_argument("--neighbourhoods", default="NUS_RC1,NUS_RC2,NUS_RC3,NUS_RC4,NUS_RC5,NUS_RC6")
    p.add_argument("--reference-dir-template",
                    default="/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20_v2/{nu}/{nu}/aggregated_eui.csv")
    p.add_argument("--code-dir", help="dir directly containing eSim_bem_utils (the staged, patched copy)")
    p.add_argument("--log-glob", action="append", default=[], help="glob pattern of job logs to scan for G4.1; repeatable")
    p.add_argument("--tolerance", type=float, default=0.001)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.mode == "selftest":
        return run_selftest(args)
    if not args.manifest or not args.batch_dir:
        eprint("FATAL: --mode real requires --manifest and --batch-dir")
        return 2
    return run_real(args)


if __name__ == "__main__":
    sys.exit(main())
