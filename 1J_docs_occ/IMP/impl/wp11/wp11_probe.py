"""
WP11 swap probe: verifies the draw-start patch (main_wp11.py, swapped in by
wp11_swap_probe.sh as the staged eSim_bem_utils/main.py) is wired correctly, with
no EnergyPlus binary invoked.

Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 2.

Method: import the swapped main module the same way the WP10 probe does
(wp10_stage4_probe.py), then monkeypatch m.simulation.run_simulations_parallel to a
no-op INSIDE THIS PROBE ONLY (main.py itself is not touched again) and call the real,
patched m._run_mc_neighbourhood for NUS_RC1 into stage4/wp11/probe/<case>/ for three
cases. _run_mc_neighbourhood's own top-level try/except always returns a result dict
(status "ok"/"failed") rather than raising, so every case is read back from the
returned dict plus the echo files it wrote before any later stage failed.

Cases (each into its own fresh directory, so "no iter_1" in start6 is automatic --
still asserted explicitly):
  unset   : WP11_DRAW_START unset, iter_count=1 -> iter_1/mc_manifest_echo.csv, draw
            column all 1, hh_ids = manifest row for (NUS_RC1, draw=1, year, bi).
            Expect PASS.
  start6  : WP11_DRAW_START=6, iter_count=2 -> iter_6 and iter_7 exist, echo draws are
            6 and 7 respectively and match the manifest; iter_1 must not exist.
            Expect PASS.
  start30 : WP11_DRAW_START=30, iter_count=2 (**seen failing first**) -> draw 30
            (k=0) succeeds like any other draw; draw 31 (k=1) is not in the manifest
            (draws only go 1..30), so _wp10_select_households_for_draw must raise
            "MANIFEST MISS", which _run_mc_neighbourhood's own try/except turns into
            status="failed". iter_31's directory may exist (os.makedirs runs before
            the raise) but must NOT contain mc_manifest_echo.csv. Expect FAIL-as-designed.

Prints `WP11 PROBE SUMMARY: unset=.. start6=.. start30=..` and
`WP11 PROBE VERDICT: PASS` only if all three outcomes are exactly as expected.
"""
import csv
import os
import shutil
import sys

CODE_DIR = "/speed-scratch/o_iseri/1J_rerun/code"
MANIFEST_PATH = "/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv"
PROBE_ROOT = "/speed-scratch/o_iseri/1J_rerun/stage4/wp11/probe"
NU = "NUS_RC1"
IDF_PATH = f"{CODE_DIR}/BEM_Setup/Neighbourhoods/{NU}.idf"
YEARS = ("2005", "2010", "2015", "2022", "2025")

sys.path.insert(0, CODE_DIR)
import eSim_bem_utils.main as m  # noqa: E402
from eSim_bem_utils import config, neighbourhood  # noqa: E402

# WP11 probe only -- main.py/main_wp11.py is never modified again. This just keeps
# EnergyPlus from being invoked so the probe stays cheap.
m.simulation.run_simulations_parallel = lambda *a, **k: None


def eprint(*a, **kw):
    print(*a, **kw)
    sys.stdout.flush()


def read_manifest():
    lookup = {}
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["neighbourhood"], int(row["draw"]), row["year"], int(row["building_index"]))
            lookup[key] = row["hh_id"]
    return lookup


def read_echo(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({
                "neighbourhood": row["neighbourhood"],
                "draw": int(row["draw"]),
                "year": row["year"],
                "building_index": int(row["building_index"]),
                "hh_id": row["hh_id"],
            })
    return rows


def run_case(name, draw_start_env, iter_count):
    case_dir = os.path.join(PROBE_ROOT, name)
    if os.path.isdir(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir, exist_ok=True)

    if draw_start_env is None:
        os.environ.pop("WP11_DRAW_START", None)
    else:
        os.environ["WP11_DRAW_START"] = draw_start_env

    epw_path = config.resolve_epw_path("Quebec", m.WEATHER_DIR)
    n_buildings = neighbourhood.get_num_buildings_from_idf(IDF_PATH)
    building_dtypes = neighbourhood.get_building_dtypes_from_idf(IDF_PATH)

    result = m._run_mc_neighbourhood(
        IDF_PATH, epw_path, "Quebec", "standard", iter_count, case_dir, n_buildings, building_dtypes,
    )
    eprint(f"WP11 PROBE {name}: raw status={result.get('status')} error={result.get('error')}")
    nu_dir = os.path.join(case_dir, NU)
    return nu_dir


def check_echo_matches_manifest(echo_path, manifest, draw):
    if not os.path.isfile(echo_path):
        return False, f"missing echo file {echo_path}"
    rows = read_echo(echo_path)
    if not rows:
        return False, f"echo file {echo_path} has zero rows"
    problems = []
    for row in rows:
        if row["draw"] != draw:
            problems.append(("WRONG_DRAW", row))
            continue
        key = (row["neighbourhood"], row["draw"], row["year"], row["building_index"])
        expected = manifest.get(key)
        if expected is None:
            problems.append(("NOT_IN_MANIFEST", row))
        elif expected != row["hh_id"]:
            problems.append(("HH_MISMATCH", row, expected))
    if problems:
        return False, f"{len(problems)} problem(s) in {echo_path}: {problems[:5]}"
    return True, f"{len(rows)} rows in {echo_path}, all draw={draw} and match manifest"


def verify_unset(nu_dir, manifest):
    echo_path = os.path.join(nu_dir, "iter_1", "mc_manifest_echo.csv")
    ok, detail = check_echo_matches_manifest(echo_path, manifest, draw=1)
    return ok, detail


def verify_start6(nu_dir, manifest):
    iter1 = os.path.join(nu_dir, "iter_1")
    if os.path.exists(iter1):
        return False, f"iter_1 must not exist for start6 but found {iter1}"
    ok6, d6 = check_echo_matches_manifest(os.path.join(nu_dir, "iter_6", "mc_manifest_echo.csv"), manifest, draw=6)
    ok7, d7 = check_echo_matches_manifest(os.path.join(nu_dir, "iter_7", "mc_manifest_echo.csv"), manifest, draw=7)
    ok = ok6 and ok7
    return ok, f"iter_6: {d6} | iter_7: {d7}"


def verify_start30(nu_dir, manifest):
    ok30, d30 = check_echo_matches_manifest(os.path.join(nu_dir, "iter_30", "mc_manifest_echo.csv"), manifest, draw=30)
    echo31 = os.path.join(nu_dir, "iter_31", "mc_manifest_echo.csv")
    no_echo31 = not os.path.isfile(echo31)
    detail = f"iter_30: ok={ok30} ({d30}); iter_31 echo absent (expected)={no_echo31}"
    return (ok30 and no_echo31), detail


def main():
    manifest = read_manifest()
    eprint(f"WP11 PROBE: manifest rows={len(manifest)} from {MANIFEST_PATH}")

    outcomes = {}

    nu_dir = run_case("unset", None, 1)
    ok, detail = verify_unset(nu_dir, manifest)
    outcomes["unset"] = ok
    eprint(f"WP11 PROBE unset: {'PASS' if ok else 'FAIL'} -- {detail}")

    nu_dir = run_case("start6", "6", 2)
    ok, detail = verify_start6(nu_dir, manifest)
    outcomes["start6"] = ok
    eprint(f"WP11 PROBE start6: {'PASS' if ok else 'FAIL'} -- {detail}")

    # start30 is seen failing first: draw 31 has no manifest row (draws only go 1..30),
    # so this case is expected to raise MANIFEST MISS and is scored as PASS only when
    # that failure is exactly what happened.
    nu_dir = run_case("start30", "30", 2)
    ok, detail = verify_start30(nu_dir, manifest)
    outcomes["start30"] = ok
    eprint(f"WP11 PROBE start30 (seen failing first, expect FAIL-as-designed): {'PASS' if ok else 'FAIL'} -- {detail}")

    eprint(
        "WP11 PROBE SUMMARY: "
        f"unset={'PASS' if outcomes['unset'] else 'FAIL'} "
        f"start6={'PASS' if outcomes['start6'] else 'FAIL'} "
        f"start30={'PASS' if outcomes['start30'] else 'FAIL'}"
    )
    verdict = "PASS" if all(outcomes.values()) else "FAIL"
    eprint(f"WP11 PROBE VERDICT: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
