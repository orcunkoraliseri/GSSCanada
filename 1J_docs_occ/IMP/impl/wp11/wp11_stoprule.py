"""
WP11 item 5: stopping-rule scorer. Implements plan log (ar)/section 7.1 verbatim --
this script changes nothing in the rule itself, only pins down its arithmetic.

Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 5.

Cells = 6 neighbourhoods x 5 years (2005,2010,2015,2022,2025) x {Heating, Cooling} =
60 cells. Default is not a cell.

--mode real --block b:
  1. Every contributing task's log (blocks 1..b, all 6 neighbourhoods -> 6*b tasks)
     must contain "WP11 EXTRACT VERDICT: VERIFIED". Any missing/absent log -> NOT_EVALUABLE.
  2. All 60 cells must have exactly draws 1..5b, one value each (from
     draws/block_<j>/<nu>/per_draw_eui.csv, j=1..b). Any missing/duplicate draw ->
     NOT_EVALUABLE naming it.
  3. Control C1 (block 1 only, checked on every run since block 1 always contributes):
     draw 1 of every cell must equal the value extracted the same way from
     stage4/default/draw_1/<nu>/iter_1/<year>/eplusout.sql within 0.00051. If block 1's
     own sql was already gzipped (post-cleanup), its draw-1 value is read back from
     block 1's own per_draw_eui.csv instead of re-extracting. Any mismatch -> NOT_EVALUABLE
     (nondeterminism).
  4. Any cell with mean <= 0 -> the whole block is NOT_EVALUABLE (the 1% criterion is
     undefined against a non-positive mean; this also matches the item-7 selftest,
     which expects a mean-0 cell to yield block-level NOT_EVALUABLE, not just one
     cell dropped from the count).
  5. Otherwise, per cell: n=5b; mean; s = sample SD (ddof=1); half = t(0.975,n-1)*s/sqrt(n);
     met iff half <= 0.01*mean. cells_met = count(met). STOP iff cells_met==60; else
     CAP_REACHED_TARGET_UNMET if b==6; else CONTINUE.
  Writes stage4/draws/stoprule_block_<b>.csv (cell,n,mean,sd,half,half_pct,met) --
  only when the block is evaluable. Prints
  "STOPRULE SUMMARY: block=b n=5b cells_met=X/60 VERDICT=..." always.
  On STOP only: scancels the LIGHT/HEAVY array tasks of blocks b+1..6 and the SCORER
  jobs of blocks b+1..6, reading job ids from stage4/draws/job_ids.txt (manager-written:
  "LIGHT <id>", "HEAVY <id>", "SCORER <b> <id>" lines); prints every scancel issued.

--mode selftest: synthetic numbers only, no cluster files -- runs locally with `py` too.
  Seen failing first: (i) all 60 cells ~0.5% -> STOP; (ii) one cell at 1.2%, rest ~0.5%
  -> CONTINUE; (iii) one draw missing for one cell -> NOT_EVALUABLE; (iv) one cell mean
  0 -> NOT_EVALUABLE; (v) b=6 with cells unmet -> CAP_REACHED_TARGET_UNMET; (vi) a
  hand-computed cell (values 10,11,9,10.5,9.5 -> mean 10, s=0.790569, half=0.981625,
  9.82%) matches to 1e-5 -- catches a ddof=0 slip; (vii) a C1 mismatch -> NOT_EVALUABLE.
  Prints "STOPRULE SELFTEST SUMMARY: 7 checks, 0 unexpected".
"""
import argparse
import csv
import os
import subprocess
import sys
from collections import defaultdict

YEARS = ("2005", "2010", "2015", "2022", "2025")
END_USES = ("Heating", "Cooling")
NEIGHBOURHOODS = ("NUS_RC1", "NUS_RC2", "NUS_RC3", "NUS_RC4", "NUS_RC5", "NUS_RC6")
ALL_CELLS = tuple((nu, y, eu) for nu in NEIGHBOURHOODS for y in YEARS for eu in END_USES)

TOL_C1 = 0.00051
MET_FRACTION = 0.01

# Pinned t(0.975, df) table -- df = n-1 = 5b-1 for b=1..6, i.e. this table is complete
# for every real block this scorer ever runs. scipy.stats.t.ppf is used when available
# and cross-checked against this table to 1e-5; the table is the fallback (and, for
# b=1..6, an equally valid primary source) when scipy is absent.
TTABLE = {4: 2.776445, 9: 2.262157, 14: 2.144787, 19: 2.093024, 24: 2.063899, 29: 2.045230}

DRAWS_ROOT = "/speed-scratch/o_iseri/1J_rerun/stage4/draws"
DEFAULT_ROOT = "/speed-scratch/o_iseri/1J_rerun/stage4/default/draw_1"
LOGS_ROOT = "/speed-scratch/o_iseri/1J_rerun/logs"
JOB_IDS_PATH = "/speed-scratch/o_iseri/1J_rerun/stage4/draws/job_ids.txt"
WP11_DIR = "/speed-scratch/o_iseri/1J_rerun/stage4/wp11"


def eprint(*a, **kw):
    print(*a, **kw)
    sys.stdout.flush()


def t_critical(df):
    """t(0.975, df). Uses scipy.stats.t.ppf if importable, cross-checked against
    TTABLE to 1e-5 when df is one of the pinned entries; otherwise falls back to
    TTABLE. Raises if scipy is absent and df is not pinned."""
    try:
        from scipy import stats  # noqa: E402
        val = float(stats.t.ppf(0.975, df))
        if df in TTABLE and abs(val - TTABLE[df]) > 1e-5:
            raise RuntimeError(
                f"scipy t.ppf(0.975,{df})={val} disagrees with the pinned table "
                f"value {TTABLE[df]} by more than 1e-5 -- stopping rather than trusting either."
            )
        return val
    except ImportError:
        if df not in TTABLE:
            raise RuntimeError(
                f"scipy unavailable and df={df} is not in the pinned table "
                f"(only {sorted(TTABLE)} are covered, i.e. b=1..6)."
            )
        return TTABLE[df]


# ---------------------------------------------------------------------------
# Pure scoring (no file I/O) -- shared by real mode and selftest.
# ---------------------------------------------------------------------------

def validate_cell_counts(cell_draw_map, b):
    """cell_draw_map: {(nu,year,eu): {draw: [values]}}. Returns (cell_values, problems)
    where cell_values is {(nu,year,eu): [v_draw1..v_draw_5b]} ordered by draw, or
    (None, problems) if any of the 60 cells is missing a draw or has a duplicate."""
    expected_n = 5 * b
    problems = []
    cell_values = {}
    for key in ALL_CELLS:
        per_draw = cell_draw_map.get(key, {})
        vals = []
        for d in range(1, expected_n + 1):
            entries = per_draw.get(d, [])
            if len(entries) == 0:
                problems.append((key, d, "MISSING"))
            elif len(entries) > 1:
                problems.append((key, d, f"DUPLICATE x{len(entries)}"))
                vals.append(entries[0])
            else:
                vals.append(entries[0])
        cell_values[key] = vals
    if problems:
        return None, problems
    return cell_values, []


def cell_stats(values):
    """(mean, sd, half, half_pct, met) for one cell's list of values, or
    (mean, None, None, None, None) if mean <= 0 (NOT_EVALUABLE)."""
    n = len(values)
    mean = sum(values) / n
    if mean <= 0:
        return mean, None, None, None, None
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    sd = var ** 0.5
    tcrit = t_critical(n - 1)
    half = tcrit * sd / (n ** 0.5)
    half_pct = half / mean * 100.0
    met = half <= MET_FRACTION * mean
    return mean, sd, half, half_pct, met


def score_block(cell_values, b):
    """cell_values: {(nu,year,eu): [n=5b values]} for all 60 cells, already validated
    by validate_cell_counts. Returns (rows, cells_met, verdict) or
    (None, None, "NOT_EVALUABLE") if any cell's mean <= 0."""
    rows = []
    any_not_evaluable = False
    for key in ALL_CELLS:
        vals = cell_values[key]
        mean, sd, half, half_pct, met = cell_stats(vals)
        if met is None:
            any_not_evaluable = True
        rows.append({
            "cell": f"{key[0]}/{key[1]}/{key[2]}", "n": len(vals), "mean": mean,
            "sd": sd, "half": half, "half_pct": half_pct, "met": met,
        })
    if any_not_evaluable:
        return None, None, "NOT_EVALUABLE"
    cells_met = sum(1 for r in rows if r["met"] is True)
    if cells_met == len(ALL_CELLS):
        verdict = "STOP"
    elif b >= 6:
        verdict = "CAP_REACHED_TARGET_UNMET"
    else:
        verdict = "CONTINUE"
    return rows, cells_met, verdict


def check_c1(ref_vals, block1_vals, tol=TOL_C1):
    """ref_vals, block1_vals: {(nu,year,eu): value}. Returns (verdict, problems)."""
    problems = []
    for key in ALL_CELLS:
        r = ref_vals.get(key)
        b1 = block1_vals.get(key)
        if r is None or b1 is None:
            problems.append((key, "MISSING", r, b1))
            continue
        diff = abs(r - b1)
        if diff > tol:
            problems.append((key, f"ref={r} block1={b1} diff={diff:.6f}"))
    if problems:
        return "NOT_EVALUABLE", problems
    return "OK", []


def write_stoprule_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cell", "n", "mean", "sd", "half", "half_pct", "met"])
        for r in rows:
            w.writerow([r["cell"], r["n"], r["mean"], r["sd"], r["half"], r["half_pct"], r["met"]])


# ---------------------------------------------------------------------------
# real mode -- file I/O
# ---------------------------------------------------------------------------

def read_per_draw_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append((row["neighbourhood"], int(row["draw"]), row["year"], row["end_use"], float(row["value"])))
    return rows


def read_job_ids(path):
    ids = {"LIGHT": None, "HEAVY": None, "SCORER": {}}
    if not os.path.isfile(path):
        return ids
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "LIGHT" and len(parts) >= 2:
                ids["LIGHT"] = parts[1]
            elif parts[0] == "HEAVY" and len(parts) >= 2:
                ids["HEAVY"] = parts[1]
            elif parts[0] == "SCORER" and len(parts) >= 3:
                ids["SCORER"][int(parts[1])] = parts[2]
    return ids


def light_task_ids_for_block(block):
    return [(block - 1) * 4 + i for i in range(4)]


def heavy_task_ids_for_block(block):
    return [(block - 1) * 2 + i for i in range(2)]


def nu_task_id(nu, block):
    if nu in ("NUS_RC1", "NUS_RC2", "NUS_RC3", "NUS_RC4"):
        rc_num = int(nu[-1])
        return "LIGHT", (block - 1) * 4 + (rc_num - 1)
    if nu in ("NUS_RC5", "NUS_RC6"):
        return "HEAVY", (block - 1) * 2 + (0 if nu == "NUS_RC5" else 1)
    raise ValueError(f"unknown neighbourhood {nu}")


def task_log_path(job_ids, nu, block):
    kind, task_id = nu_task_id(nu, block)
    job_id = job_ids.get(kind)
    if not job_id:
        return None
    return os.path.join(LOGS_ROOT, f"wp11_draw_{job_id}_{task_id}.out")


def check_all_verified(job_ids, b):
    problems = []
    for block in range(1, b + 1):
        for nu in NEIGHBOURHOODS:
            log_path = task_log_path(job_ids, nu, block)
            if not log_path or not os.path.isfile(log_path):
                problems.append((block, nu, "LOG_MISSING", log_path))
                continue
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            if "WP11 EXTRACT VERDICT: VERIFIED" not in text:
                problems.append((block, nu, "NOT_VERIFIED", log_path))
    return problems


def build_ref_vals(default_root):
    """{(nu,year,eu): value} extracted fresh from default/draw_1/<nu>/iter_1/<year>/eplusout.sql."""
    wp11_extract = _import_wp11_extract()
    vals = {}
    for nu in NEIGHBOURHOODS:
        for year in YEARS:
            sql_path = os.path.join(default_root, nu, "iter_1", year, "eplusout.sql")
            if not os.path.isfile(sql_path):
                continue
            end_uses = wp11_extract.extract_eui(sql_path)
            for eu in END_USES:
                if eu in end_uses:
                    vals[(nu, year, eu)] = end_uses[eu]
    return vals


def build_block1_draw1_vals(block1_dir):
    """{(nu,year,eu): value} for draw=1, re-extracted the same way when the sql is
    still there, falling back to block 1's own per_draw_eui.csv once it is gzipped."""
    wp11_extract = _import_wp11_extract()
    vals = {}
    for nu in NEIGHBOURHOODS:
        per_draw_path = os.path.join(block1_dir, nu, "per_draw_eui.csv")
        csv_rows = read_per_draw_csv(per_draw_path) if os.path.isfile(per_draw_path) else []
        for year in YEARS:
            sql_path = os.path.join(block1_dir, nu, "iter_1", year, "eplusout.sql")
            if os.path.isfile(sql_path):
                end_uses = wp11_extract.extract_eui(sql_path)
                for eu in END_USES:
                    if eu in end_uses:
                        vals[(nu, year, eu)] = end_uses[eu]
            else:
                for (_nu, d, y, eu, v) in csv_rows:
                    if d == 1 and y == year and eu in END_USES:
                        vals[(nu, year, eu)] = v
    return vals


def _import_wp11_extract():
    if WP11_DIR not in sys.path:
        sys.path.insert(0, WP11_DIR)
    import wp11_extract  # noqa: E402
    return wp11_extract


def do_scancel(job_ids, b):
    issued = []
    for block in range(b + 1, 7):
        light_id = job_ids.get("LIGHT")
        if light_id:
            for task_id in light_task_ids_for_block(block):
                target = f"{light_id}_{task_id}"
                issued.append(target)
        heavy_id = job_ids.get("HEAVY")
        if heavy_id:
            for task_id in heavy_task_ids_for_block(block):
                target = f"{heavy_id}_{task_id}"
                issued.append(target)
        scorer_id = job_ids.get("SCORER", {}).get(block)
        if scorer_id:
            issued.append(scorer_id)
    for target in issued:
        eprint(f"STOPRULE SCANCEL: scancel {target}")
        subprocess.run(["scancel", target], check=False)
    return issued


def run_real(args):
    b = args.block
    job_ids = read_job_ids(args.job_ids_file)

    verify_problems = check_all_verified(job_ids, b)
    if verify_problems:
        eprint(f"STOPRULE: {len(verify_problems)} unverified/missing contributing task log(s): {verify_problems}")
        eprint(f"STOPRULE SUMMARY: block={b} n={5*b} cells_met=NA/60 VERDICT=NOT_EVALUABLE")
        return 0

    rows_all = []
    for block in range(1, b + 1):
        for nu in NEIGHBOURHOODS:
            per_draw_path = os.path.join(DRAWS_ROOT, f"block_{block}", nu, "per_draw_eui.csv")
            if not os.path.isfile(per_draw_path):
                eprint(f"STOPRULE: missing {per_draw_path}")
                eprint(f"STOPRULE SUMMARY: block={b} n={5*b} cells_met=NA/60 VERDICT=NOT_EVALUABLE")
                return 0
            rows_all.extend(read_per_draw_csv(per_draw_path))

    cell_draw_map = defaultdict(lambda: defaultdict(list))
    for (nu, d, y, eu, v) in rows_all:
        if d == 0 or y == "Default" or eu not in END_USES:
            continue
        cell_draw_map[(nu, y, eu)][d].append(v)

    cell_values, count_problems = validate_cell_counts(cell_draw_map, b)
    if count_problems:
        eprint(f"STOPRULE: {len(count_problems)} draw-count problem(s): {count_problems[:20]}")
        eprint(f"STOPRULE SUMMARY: block={b} n={5*b} cells_met=NA/60 VERDICT=NOT_EVALUABLE")
        return 0

    ref_vals = build_ref_vals(args.default_root)
    block1_vals = build_block1_draw1_vals(os.path.join(DRAWS_ROOT, "block_1"))
    c1_verdict, c1_problems = check_c1(ref_vals, block1_vals)
    if c1_verdict != "OK":
        eprint(f"STOPRULE C1: NOT_EVALUABLE -- {len(c1_problems)} mismatch(es): {c1_problems[:20]}")
        eprint(f"STOPRULE SUMMARY: block={b} n={5*b} cells_met=NA/60 VERDICT=NOT_EVALUABLE")
        return 0
    eprint(f"STOPRULE C1: OK -- draw 1 matches default/draw_1 for all {len(ALL_CELLS)} cells within {TOL_C1}")

    rows, cells_met, verdict = score_block(cell_values, b)
    if verdict == "NOT_EVALUABLE":
        eprint("STOPRULE: at least one cell has mean <= 0 -- block is NOT_EVALUABLE")
        eprint(f"STOPRULE SUMMARY: block={b} n={5*b} cells_met=NA/60 VERDICT=NOT_EVALUABLE")
        return 0

    out_path = args.out or os.path.join(DRAWS_ROOT, f"stoprule_block_{b}.csv")
    write_stoprule_csv(out_path, rows)
    eprint(f"STOPRULE: wrote {out_path}")
    eprint(f"STOPRULE SUMMARY: block={b} n={5*b} cells_met={cells_met}/{len(ALL_CELLS)} VERDICT={verdict}")

    if verdict == "STOP":
        do_scancel(job_ids, b)
    return 0


# ---------------------------------------------------------------------------
# selftest mode -- synthetic numbers only, seen failing first
# ---------------------------------------------------------------------------

def _make_cell_values(n, mean, rel_half_target):
    """n values around `mean` whose t-based half-width is close to rel_half_target
    (fraction of mean) -- used only for the STOP/CONTINUE/CAP fixtures, which just
    need to land clearly under or over the 1% line. The exact-number check (vi) uses
    the doc's own fixed values instead."""
    tcrit = t_critical(n - 1)
    target_half = rel_half_target * mean
    if n % 2 == 0:
        d = target_half * (n - 1) ** 0.5 / tcrit
        half_count = n // 2
        return [mean + d] * half_count + [mean - d] * half_count
    d = target_half * (n ** 0.5) / tcrit
    half_count = (n - 1) // 2
    return [mean + d] * half_count + [mean - d] * half_count + [mean]


def _uniform_cell_values(b, rel_half_target, mean=100.0):
    n = 5 * b
    return {key: _make_cell_values(n, mean, rel_half_target) for key in ALL_CELLS}


def run_selftest(args):
    results = []

    def record(name, ok, detail):
        results.append((name, ok))
        eprint(f"[SELFTEST {'PASS' if ok else 'FAIL'}] {name}: {detail}")

    # (i) all 60 cells ~0.5% -> STOP
    b = 2
    cv = _uniform_cell_values(b, 0.005)
    rows, cells_met, verdict = score_block(cv, b)
    record("(i) all cells ~0.5% -> STOP", verdict == "STOP" and cells_met == 60,
           f"verdict={verdict} cells_met={cells_met}")

    # (ii) one cell at 1.2%, rest ~0.5% -> CONTINUE
    b = 2
    cv = _uniform_cell_values(b, 0.005)
    bad_key = ALL_CELLS[0]
    cv[bad_key] = _make_cell_values(5 * b, 100.0, 0.012)
    rows, cells_met, verdict = score_block(cv, b)
    record("(ii) one cell at 1.2%, rest ~0.5% -> CONTINUE", verdict == "CONTINUE" and cells_met == 59,
           f"verdict={verdict} cells_met={cells_met}")

    # (iii) one draw missing for one cell -> NOT_EVALUABLE (validate_cell_counts)
    b = 1
    cell_draw_map = defaultdict(lambda: defaultdict(list))
    for key in ALL_CELLS:
        for d in range(1, 5 * b + 1):
            cell_draw_map[key][d].append(100.0)
    del cell_draw_map[ALL_CELLS[0]][3]  # drop draw 3 for the first cell
    cell_values, problems = validate_cell_counts(cell_draw_map, b)
    record("(iii) one draw missing -> NOT_EVALUABLE", cell_values is None and len(problems) >= 1,
           f"cell_values is None={cell_values is None} problems={problems}")

    # (iv) a cell with mean 0 -> NOT_EVALUABLE (block-level)
    b = 1
    cv = _uniform_cell_values(b, 0.005)
    cv[ALL_CELLS[0]] = [0.0] * (5 * b)
    rows, cells_met, verdict = score_block(cv, b)
    record("(iv) a cell with mean 0 -> NOT_EVALUABLE", verdict == "NOT_EVALUABLE",
           f"verdict={verdict}")

    # (v) b=6 with cells unmet -> CAP_REACHED_TARGET_UNMET
    b = 6
    cv = _uniform_cell_values(b, 0.005)
    cv[ALL_CELLS[0]] = _make_cell_values(5 * b, 100.0, 0.03)
    rows, cells_met, verdict = score_block(cv, b)
    record("(v) b=6 with cells unmet -> CAP_REACHED_TARGET_UNMET", verdict == "CAP_REACHED_TARGET_UNMET",
           f"verdict={verdict} cells_met={cells_met}")

    # (vi) hand-computed cell, ddof=0 slip catcher
    values = [10, 11, 9, 10.5, 9.5]
    mean, sd, half, half_pct, met = cell_stats(values)
    ok = (abs(mean - 10.0) < 1e-9 and abs(sd - 0.790569) < 1e-5
          and abs(half - 0.981625) < 1e-5 and abs(half_pct - 9.82) < 1e-2)
    record("(vi) hand-computed cell matches to 1e-5 (ddof=1)", ok,
           f"mean={mean} sd={sd} half={half} half_pct={half_pct}")

    # (vii) C1 mismatch -> NOT_EVALUABLE
    ref_vals = {key: 100.0 for key in ALL_CELLS}
    block1_vals = dict(ref_vals)
    block1_vals[ALL_CELLS[0]] = 105.0  # far outside TOL_C1
    v, problems = check_c1(ref_vals, block1_vals)
    record("(vii) C1 mismatch -> NOT_EVALUABLE", v == "NOT_EVALUABLE" and len(problems) == 1,
           f"verdict={v} problems={problems}")

    n_fail = sum(1 for _, ok in results if not ok)
    eprint(f"STOPRULE SELFTEST SUMMARY: {len(results)} checks, {n_fail} unexpected")
    return 1 if n_fail else 0


# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="WP11 stopping-rule scorer")
    p.add_argument("--mode", choices=["real", "selftest"], required=True)
    p.add_argument("--block", type=int)
    p.add_argument("--draws-root", default=DRAWS_ROOT)
    p.add_argument("--default-root", default=DEFAULT_ROOT)
    p.add_argument("--job-ids-file", default=JOB_IDS_PATH)
    p.add_argument("--out")
    return p


def main(argv=None):
    global DRAWS_ROOT
    args = build_parser().parse_args(argv)
    if args.draws_root:
        DRAWS_ROOT = args.draws_root
    if args.mode == "selftest":
        return run_selftest(args)
    if args.block is None:
        eprint("FATAL: --mode real requires --block")
        return 2
    return run_real(args)


if __name__ == "__main__":
    sys.exit(main())
