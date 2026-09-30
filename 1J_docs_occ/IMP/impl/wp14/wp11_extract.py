"""
WP11 item 3: per-draw EUI extraction + verification (E1-E5) for one (neighbourhood,
draw block) task, run by wp11_draw_task.sh right after the runner.

Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 3.

For each draw d in [draw_start, draw_start+n_draws) and year in 2005/2010/2015/2022/2025,
opens <task-dir>/<nu>/iter_<d>/<year>/eplusout.sql with sqlite3, calls the pipeline's
own plotting.calculate_eui(conn), and takes end_uses_normalized (falling back to
end_uses exactly as main.py:_flush_aggregated_csv does). Same for the task's
Default/eplusout.sql (year="Default", draw=0). Writes
<task-dir>/<nu>/per_draw_eui.csv: neighbourhood,draw,year,end_use,value -- one row per
end use (every end use the sql produced, Heating and Cooling at minimum).

Checks (each prints its own "WP11 EXTRACT <name>: PASS|FAIL -- detail" line):
  E1  all draw-year sqls (n_draws x 5 years) present and non-empty.
  E2  for each year, the mean over the n_draws draws of Heating and of Cooling equals
      aggregated_eui.csv's <year>_mean within 0.00051.
  E3  each iter_<d>/mc_manifest_echo.csv equals the manifest rows for (nu, d) exactly
      -- reuses wp10_gate4.check_g4_0 (staged at stage4/wp10_gate4.py), one call per draw.
  E4  the extracted Default Heating/Cooling equal the April reference within 0.00051.
  E5  "WP11 DRAW START: <draw_start>" is present in the task log (--log).

"WP11 EXTRACT VERDICT: VERIFIED" only if E1-E5 all PASS -> exit 0, and (design
decision, see task doc Decisions) cleanup runs right here: every eplusout.eso under
<task-dir>/<nu>/ (iter dirs and Default) is deleted and every eplusout.sql there is
gzipped, in-place, unless --no-cleanup is given. Otherwise "NOT_VERIFIED" -> exit 1,
nothing is deleted. --no-cleanup is also used for the item-7 selftest, which points
this script at a real, already-finished directory under default/ that must never be
touched.

Modes:
  --mode real       the run above, against a real task directory.
  --mode selftest   item 7's E2 selftest: extract real per-draw values from a real,
                     already-finished directory (--nu/--task-dir/--draw-start/--n-draws
                     point at it, e.g. NUS_RC1 / stage4/default/draw_1 / 1 / 1), score
                     E2 against its own real aggregated_eui.csv (expect PASS), then
                     score E2 against a temp COPY of that csv with one mean perturbed
                     by 0.01 (expect FAIL -- seen failing first). Never calls cleanup.
"""
import argparse
import csv
import gzip
import os
import shutil
import sqlite3
import sys
import tempfile

YEARS = ("2005", "2010", "2015", "2022", "2025")
TOL = 0.00051

# April reference Heating/Cooling (kWh/m2), read fresh by the manager at 4c/4d design
# (plan log (at)/(au)) -- never re-derived from a different file.
APRIL_REF = {
    "NUS_RC1": (35.1170, 45.6120),
    "NUS_RC2": (38.1730, 44.0140),
    "NUS_RC3": (24.9740, 46.5260),
    "NUS_RC4": (156.4140, 18.2310),
    "NUS_RC5": (158.5250, 19.4240),
    "NUS_RC6": (150.7800, 26.2210),
}

CODE_DIR = "/speed-scratch/o_iseri/1J_rerun/code"
WP10_GATE4_DIR = "/speed-scratch/o_iseri/1J_rerun/stage4"
MANIFEST_PATH = "/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv"


def eprint(*a, **kw):
    print(*a, **kw)
    sys.stdout.flush()


def _import_wp10_gate4():
    if WP10_GATE4_DIR not in sys.path:
        sys.path.insert(0, WP10_GATE4_DIR)
    import wp10_gate4  # noqa: E402
    return wp10_gate4


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_eui(sql_path):
    """{end_use: value} from one eplusout.sql -- end_uses_normalized, falling back to
    end_uses, exactly as main.py:_flush_aggregated_csv does."""
    if CODE_DIR not in sys.path:
        sys.path.insert(0, CODE_DIR)
    from eSim_bem_utils import plotting  # noqa: E402
    conn = sqlite3.connect(sql_path)
    try:
        data = plotting.calculate_eui(conn)
    finally:
        conn.close()
    return data.get("end_uses_normalized") or data.get("end_uses") or {}


def do_extract(nu, task_dir, draw_start, n_draws):
    """Returns (rows, missing_sql_paths). rows = list of (nu, draw, year, end_use, value);
    draw=0/year="Default" for the Default sql."""
    nu_dir = os.path.join(task_dir, nu)
    rows = []
    missing = []
    for d in range(draw_start, draw_start + n_draws):
        for year in YEARS:
            sql_path = os.path.join(nu_dir, f"iter_{d}", year, "eplusout.sql")
            if not os.path.isfile(sql_path) or os.path.getsize(sql_path) == 0:
                missing.append(sql_path)
                continue
            for eu, val in extract_eui(sql_path).items():
                rows.append((nu, d, year, eu, val))
    default_sql = os.path.join(nu_dir, "Default", "eplusout.sql")
    if os.path.isfile(default_sql) and os.path.getsize(default_sql) > 0:
        for eu, val in extract_eui(default_sql).items():
            rows.append((nu, 0, "Default", eu, val))
    else:
        missing.append(default_sql)
    return rows, missing


def write_per_draw_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["neighbourhood", "draw", "year", "end_use", "value"])
        for r in rows:
            w.writerow(r)


def read_aggregated_means(path):
    """{scenario: {end_use: mean}} from an aggregated_eui.csv (scenario in
    2005..2025 or "Default"), read from the "<scenario>_mean" columns."""
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        scenarios = sorted({c[:-len("_mean")] for c in header if c.endswith("_mean")})
        for row in reader:
            eu = row.get("EndUse")
            if eu not in ("Heating", "Cooling"):
                continue
            for s in scenarios:
                col = f"{s}_mean"
                if col in row and row[col] not in (None, ""):
                    out.setdefault(s, {})[eu] = float(row[col])
    return out


# ---------------------------------------------------------------------------
# E1-E5
# ---------------------------------------------------------------------------

def check_e1(nu, task_dir, draw_start, n_draws, years=YEARS):
    nu_dir = os.path.join(task_dir, nu)
    problems = []
    checked = 0
    for d in range(draw_start, draw_start + n_draws):
        for year in years:
            p = os.path.join(nu_dir, f"iter_{d}", year, "eplusout.sql")
            checked += 1
            if not os.path.isfile(p):
                problems.append(("MISSING", p))
            elif os.path.getsize(p) == 0:
                problems.append(("EMPTY", p))
    if problems:
        return "FAIL", f"{len(problems)} of {checked} draw-year sqls missing/empty: {problems[:10]}"
    if checked == 0:
        return "NOT_EVALUABLE", "n_draws x years is zero"
    return "PASS", f"all {checked} draw-year sqls present and non-empty"


def check_e2(rows, agg_means, years=YEARS):
    problems = []
    checked = []
    for year in years:
        for eu in ("Heating", "Cooling"):
            vals = [v for (_nu, d, y, e, v) in rows if y == year and e == eu and d != 0]
            if not vals:
                problems.append((year, eu, "NO_EXTRACTED_VALUES"))
                continue
            mean_val = sum(vals) / len(vals)
            ref = agg_means.get(year, {}).get(eu)
            if ref is None:
                problems.append((year, eu, "NO_REFERENCE_IN_AGG_CSV"))
                continue
            diff = abs(mean_val - ref)
            checked.append((year, eu, mean_val, ref, diff))
            if diff > TOL:
                problems.append((year, eu, f"extracted_mean={mean_val:.6f} agg={ref:.6f} diff={diff:.6f}"))
    if not checked and not problems:
        return "NOT_EVALUABLE", "nothing to check"
    if problems:
        return "FAIL", f"{len(problems)} problem(s): {problems}"
    return "PASS", f"{len(checked)} (year,end_use) means match aggregated_eui.csv within {TOL}"


def check_e3(nu, task_dir, draw_start, n_draws, manifest_lookup, gate4_mod):
    nu_dir = os.path.join(task_dir, nu)
    problems = []
    checked_draws = 0
    for d in range(draw_start, draw_start + n_draws):
        echo_path = os.path.join(nu_dir, f"iter_{d}", "mc_manifest_echo.csv")
        v, detail = gate4_mod.check_g4_0({nu: echo_path}, manifest_lookup)
        checked_draws += 1
        if v != "PASS":
            problems.append((d, v, detail))
    if checked_draws == 0:
        return "NOT_EVALUABLE", "n_draws is zero"
    if problems:
        return "FAIL", f"{len(problems)} of {checked_draws} draw(s) mismatch/missing: {problems}"
    return "PASS", f"{checked_draws} draw(s)' mc_manifest_echo.csv all match the manifest exactly"


def check_e4(rows, nu, april_ref=APRIL_REF):
    ref = april_ref.get(nu)
    if not ref:
        return "NOT_EVALUABLE", f"no April reference for {nu}"
    ref_h, ref_c = ref
    got = {e: v for (_nu, d, y, e, v) in rows if y == "Default" and d == 0 and e in ("Heating", "Cooling")}
    if "Heating" not in got or "Cooling" not in got:
        return "NOT_EVALUABLE", f"Default Heating/Cooling not extracted: {got}"
    diff_h = abs(got["Heating"] - ref_h)
    diff_c = abs(got["Cooling"] - ref_c)
    if diff_h > TOL or diff_c > TOL:
        return "FAIL", (
            f"Heating: extracted={got['Heating']:.6f} ref={ref_h:.6f} diff={diff_h:.6f}; "
            f"Cooling: extracted={got['Cooling']:.6f} ref={ref_c:.6f} diff={diff_c:.6f} (tol {TOL})"
        )
    return "PASS", (
        f"Default Heating/Cooling match April reference within {TOL}: "
        f"Heating diff={diff_h:.6f}, Cooling diff={diff_c:.6f}"
    )


def check_e5(log_path, draw_start):
    if not log_path:
        return "NOT_EVALUABLE", "--log not given"
    if not os.path.isfile(log_path):
        return "NOT_EVALUABLE", f"log file not found: {log_path}"
    needle = f"WP11 DRAW START: {draw_start}"
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    if needle in text:
        return "PASS", f"'{needle}' present in {log_path}"
    return "FAIL", f"'{needle}' NOT present in {log_path}"


# ---------------------------------------------------------------------------
# Cleanup (only called from --mode real, only on VERIFIED, unless --no-cleanup)
# ---------------------------------------------------------------------------

def do_cleanup(nu, task_dir):
    nu_dir = os.path.join(task_dir, nu)
    deleted = 0
    gzipped = 0
    for root, _dirs, files in os.walk(nu_dir):
        for fn in files:
            p = os.path.join(root, fn)
            if fn == "eplusout.eso":
                os.remove(p)
                deleted += 1
            elif fn == "eplusout.sql":
                with open(p, "rb") as f_in, gzip.open(p + ".gz", "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                os.remove(p)
                gzipped += 1
    return deleted, gzipped


def _dir_size_bytes(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for fn in files:
            try:
                total += os.path.getsize(os.path.join(root, fn))
            except OSError:
                pass
    return total


# ---------------------------------------------------------------------------
# real mode
# ---------------------------------------------------------------------------

def run_real(args):
    if not (args.nu and args.task_dir and args.draw_start is not None and args.n_draws):
        eprint("FATAL: --mode real requires --nu --task-dir --draw-start --n-draws")
        return 2

    gate4_mod = _import_wp10_gate4()
    manifest_lookup = gate4_mod.read_manifest_lookup(MANIFEST_PATH)

    nu_dir = os.path.join(args.task_dir, args.nu)
    size_before = _dir_size_bytes(nu_dir)

    rows, missing_sql = do_extract(args.nu, args.task_dir, args.draw_start, args.n_draws)
    per_draw_path = os.path.join(nu_dir, "per_draw_eui.csv")
    write_per_draw_csv(per_draw_path, rows)
    eprint(f"WP11 EXTRACT: wrote {len(rows)} rows to {per_draw_path}, {len(missing_sql)} sql(s) missing/empty")
    if missing_sql:
        eprint(f"WP11 EXTRACT: missing/empty sqls: {missing_sql}")

    agg_path = os.path.join(nu_dir, "aggregated_eui.csv")
    agg_means = read_aggregated_means(agg_path) if os.path.isfile(agg_path) else {}
    if not os.path.isfile(agg_path):
        eprint(f"WP11 EXTRACT: WARNING aggregated_eui.csv not found at {agg_path}")

    v1, d1 = check_e1(args.nu, args.task_dir, args.draw_start, args.n_draws)
    eprint(f"WP11 EXTRACT E1: {v1} -- {d1}")
    v2, d2 = check_e2(rows, agg_means)
    eprint(f"WP11 EXTRACT E2: {v2} -- {d2}")
    v3, d3 = check_e3(args.nu, args.task_dir, args.draw_start, args.n_draws, manifest_lookup, gate4_mod)
    eprint(f"WP11 EXTRACT E3: {v3} -- {d3}")
    v4, d4 = check_e4(rows, args.nu)
    eprint(f"WP11 EXTRACT E4: {v4} -- {d4}")
    v5, d5 = check_e5(args.log, args.draw_start)
    eprint(f"WP11 EXTRACT E5: {v5} -- {d5}")

    verified = all(v == "PASS" for v in (v1, v2, v3, v4, v5))
    if verified:
        eprint("WP11 EXTRACT VERDICT: VERIFIED")
        if args.no_cleanup:
            eprint("WP11 EXTRACT CLEANUP: skipped (--no-cleanup)")
        else:
            deleted, gzipped = do_cleanup(args.nu, args.task_dir)
            size_after = _dir_size_bytes(nu_dir)
            eprint(
                f"WP11 EXTRACT CLEANUP: deleted {deleted} eplusout.eso, gzipped {gzipped} eplusout.sql "
                f"under {nu_dir}; size before={size_before} bytes after={size_after} bytes"
            )
        return 0
    else:
        eprint("WP11 EXTRACT VERDICT: NOT_VERIFIED")
        eprint("WP11 EXTRACT CLEANUP: skipped (not VERIFIED)")
        return 1


# ---------------------------------------------------------------------------
# selftest mode -- item 7's E2 check, seen failing first
# ---------------------------------------------------------------------------

def _perturb_one_mean(path, delta):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    for ci, col in enumerate(header):
        if col.endswith("_mean") and not col.startswith("Default"):
            for r in rows[1:]:
                if r and r[0] in ("Heating", "Cooling"):
                    r[ci] = f"{float(r[ci]) + delta:.4f}"
                    break
            break
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def run_selftest(args):
    if not (args.nu and args.task_dir and args.draw_start is not None and args.n_draws):
        eprint(
            "FATAL: --mode selftest requires --nu --task-dir --draw-start --n-draws "
            "pointing at a real, already-finished task directory"
        )
        return 2

    nu_dir = os.path.join(args.task_dir, args.nu)
    agg_path = os.path.join(nu_dir, "aggregated_eui.csv")
    if not os.path.isfile(agg_path):
        eprint(f"FATAL: real aggregated_eui.csv not found at {agg_path}")
        return 2

    eprint(
        f"WP11 EXTRACT SELFTEST: reading real per-draw values from {nu_dir} "
        f"(read-only, --no-cleanup={args.no_cleanup}, cleanup is never called in this mode)"
    )
    rows, missing_sql = do_extract(args.nu, args.task_dir, args.draw_start, args.n_draws)
    eprint(f"WP11 EXTRACT SELFTEST: extracted {len(rows)} rows, {len(missing_sql)} sql(s) missing/empty")

    results = []

    def record(name, verdict, expect, detail):
        ok = verdict == expect
        results.append((name, ok))
        eprint(f"[SELFTEST {'PASS' if ok else 'FAIL'}] {name}: got {verdict} (expected {expect}) -- {detail}")

    agg_means = read_aggregated_means(agg_path)
    v, d = check_e2(rows, agg_means)
    record("E2 against the real aggregated_eui.csv", v, "PASS", d)

    tmp_dir = tempfile.mkdtemp(prefix="wp11_extract_selftest_")
    bad_agg_path = os.path.join(tmp_dir, "aggregated_eui.csv")
    shutil.copyfile(agg_path, bad_agg_path)
    _perturb_one_mean(bad_agg_path, delta=0.01)
    bad_means = read_aggregated_means(bad_agg_path)
    v, d = check_e2(rows, bad_means)
    record("E2 seen-failing-first: one mean perturbed by 0.01 in a temp COPY", v, "FAIL", d)

    n_fail = sum(1 for _, ok in results if not ok)
    eprint(f"WP11 EXTRACT SELFTEST SUMMARY: {len(results)} checks, {n_fail} unexpected result(s)")
    return 1 if n_fail else 0


# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="WP11 per-draw EUI extraction + E1-E5")
    p.add_argument("--mode", choices=["real", "selftest"], default="real")
    p.add_argument("--nu")
    p.add_argument("--task-dir")
    p.add_argument("--draw-start", type=int)
    p.add_argument("--n-draws", type=int)
    p.add_argument("--log", help="task log path, read for E5 (real mode only)")
    p.add_argument("--no-cleanup", action="store_true", default=False,
                    help="never delete/gzip anything, even on VERIFIED -- used for the "
                         "item-7 selftest against a real directory under default/")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.mode == "selftest":
        return run_selftest(args)
    return run_real(args)


if __name__ == "__main__":
    sys.exit(main())
