#!/usr/bin/env python3
"""t21_check.py -- T21 collector script (A1-A4), run by the collector as its
own sbatch job -- NEVER on the login node: A2 (restated) loads the full
staged schedule CSVs via the engine's own eSim_bem_utils_2J calls.

Task doc: 2026-09-15_T21_wp1_step8_step9_rerun.md, Acceptance A1-A4, Ledger
"diagnosis 1328414 read + manager decision" (RESTATED A2).

A2 was originally "(sample, hh_id) equal to the published manifest". The
manager struck that basis 2026-09-15: the rebuilt schedules change which
households the engine's own sanity check drops, so the paired pool differs
from the published one by construction (Q2a/Q5a of t21_diag_sample.py:
16,326 new vs 16,208 published, symmetric diff 320) -- equality with the old
manifest is impossible regardless of correctness. A2 is RESTATED as:

  A2 (restated). Per cell and campaign, (sample, hh_id) in the run's own
  cell_manifest.csv must equal an INDEPENDENT re-draw computed with the
  engine's OWN calls on the staged files: eSim_bem_utils_2J.integration
  .load_schedules() (per-year pool + its sanity check),
  eSim_bem_utils_2J.main._step8_cell_seed(), random.Random(seed).sample().
  The 2022/2030 pool-intersection merge is copied verbatim from
  eSim_bem_utils_2J/main.py:2029-2034 (not its own callable function) --
  cited, not reimplemented differently -- exactly as t21_diag_sample.py did
  (same helper, same citation, reused here rather than duplicated logic).
  Step 8 and both Step 9 campaigns must also draw the SAME households per
  cell (A2X, cross-campaign consistency).

  A2-info (report only, no pass/fail band): new paired-pool size, published
  paired-pool size (computed the same way on the T17-staged published
  schedule CSVs -- this is Q4/Q4a of t21_diag_sample.py, generalised to all
  24 cells), and how many of the actual 50 sampled households also appear in
  the published reference manifest (staged copies under --step8-ref-dir /
  --step9-ref-dir). The paper states the rebuilt stock re-draws the sample
  (a limitation of the before/after comparison, not household-paired).

  The check must first be seen failing on a fake manifest (one id swapped)
  before its PASS is trusted -- see --selftest below.

Other checks (per campaign in {step8, step9_activity, step9_baseline}, per
cell), unchanged from the original script:
  A1 completeness -- delivered runs / planned runs (a "delivered" run =
     hourly_meters.csv with 8760 data rows present for a (sample, year)).
  A3 no fallback -- no "schedule.json not found" / "invalid" line in any
     task's stdout log under T21/logs/.
  A4 inputs unchanged -- md5 of the 4 staged schedule CSVs (sched_activity/
     sched_baseline, 2022+2030) still match T21/sched_md5_before.txt (written
     by t21_extract_baseline.sh before any array task ran). NOTE: a
     dedicated, cheap "A4 md5-after" job also runs this same comparison on
     its own (no engine import, no big CSV parse) so A4's answer does not
     wait on A2's much slower engine re-draw across 24 cells; this script's
     own A4 section is kept as a second, independent confirmation.

Usage (on Speed, inside an sbatch job -- never on the login node; A2 loads
the full 2022/2030 schedule CSVs per cell via the engine, so this is heavy):
  --selftest mode (run first, exit code is the selftest's own verdict, does
  NOT run the real A1-A4 check in the same invocation):
    python t21_check.py --selftest \
        --t21-root /speed-scratch/o_iseri/2J_revision/T21 \
        --code-root /speed-scratch/o_iseri/2J_revision/code_step8/repo

  Real check:
    python t21_check.py \
        --t21-root /speed-scratch/o_iseri/2J_revision/T21 \
        --code-root /speed-scratch/o_iseri/2J_revision/code_step8/repo \
        --pub-sched-dir /speed-scratch/o_iseri/2J_revision/T17/code/sched \
        --step8-ref-dir /speed-scratch/o_iseri/2J_revision/T21/ref/step8 \
        --step9-ref-dir /speed-scratch/o_iseri/2J_revision/T21/ref/step9 \
        --out /speed-scratch/o_iseri/2J_revision/T21/out/t21_check_report.csv
"""
import argparse
import csv
import glob
import hashlib
import os
import random
import re
import sys

ARCHS = (["SingleD"] * 6 + ["OtherDwelling"] * 6 + ["MidRise"] * 6 + ["HighRise"] * 6)
CITIES = (["Toronto_5A", "Kelowna_5B", "Vancouver_5C", "Montreal_6A", "Calgary_6B", "Winnipeg_7A"] * 4)
CELLS = [f"{a}__{c}" for a, c in zip(ARCHS, CITIES)]

CAMPAIGNS = ("step8", "step9_activity", "step9_baseline")

_SAMP_RE = re.compile(r"^sample_(\d+)_HH(.+)$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# A1 / A3 / A4 -- unchanged from the original Phase-A script
# ---------------------------------------------------------------------------
def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest_pairs(manifest_path):
    """Return {sample:int -> hh_id:str} from a cell_manifest.csv
    (header: sample,sim_hh_id,hhsize,dtype,pr)."""
    pairs = {}
    if not manifest_path or not os.path.exists(manifest_path):
        return pairs
    with open(manifest_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                pairs[int(row["sample"])] = str(row["sim_hh_id"])
            except (KeyError, ValueError):
                continue
    return pairs


def count_delivered(out_dir, years=("2022", "2030")):
    """Count (sample,year) pairs with a valid (8760 data-row) hourly_meters.csv
    under out_dir/sample_*_HH*/<year>/hourly_meters.csv. Returns
    (delivered, planned_samples, bad_row_count_list)."""
    delivered = 0
    bad = []
    samples = set()
    if not os.path.isdir(out_dir):
        return 0, 0, bad
    for name in sorted(os.listdir(out_dir)):
        m = _SAMP_RE.match(name)
        if not m:
            continue
        samples.add(name)
        for yr in years:
            hm = os.path.join(out_dir, name, yr, "hourly_meters.csv")
            if not os.path.exists(hm):
                continue
            with open(hm, encoding="utf-8", errors="replace") as f:
                nrows = sum(1 for _ in f) - 1
            if nrows == 8760:
                delivered += 1
            else:
                bad.append((name, yr, nrows))
    return delivered, len(samples), bad


def a3_fallback_scan(logs_dir, campaign):
    """Grep every t21 array/smoke log for this campaign for the two banned
    strings. Returns {log_path: [matching lines]}."""
    hits = {}
    if not os.path.isdir(logs_dir):
        return hits
    patt = f"t21_{campaign}_*.out" if campaign != "step8" else "t21_step8_*.out"
    for log_path in glob.glob(os.path.join(logs_dir, patt)):
        lines = []
        with open(log_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                low = line.lower()
                if "schedule.json not found" in low or "invalid" in low:
                    lines.append(line.rstrip("\n"))
        if lines:
            hits[log_path] = lines
    return hits


def a4_md5_check(t21_root):
    before_path = os.path.join(t21_root, "sched_md5_before.txt")
    if not os.path.exists(before_path):
        return "NO_BEFORE_FILE", {}
    before = {}
    with open(before_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                before[parts[1]] = parts[0]
    diffs = {}
    for path in before:
        if not os.path.exists(path):
            diffs[path] = "MISSING_NOW"
            continue
        now = md5_of(path)
        if now != before[path]:
            diffs[path] = f"before={before[path]} now={now}"
    return ("PASS" if not diffs else "FAIL"), diffs


# ---------------------------------------------------------------------------
# A2 (restated) -- engine's own calls, reused from t21_diag_sample.py
# (same functions, same citations; not reimplemented differently here).
# ---------------------------------------------------------------------------
def load_engine(code_root):
    driver_dir = os.path.join(code_root, "2J_docs_occ_nTemp", "Step8_docs")
    if driver_dir not in sys.path:
        sys.path.insert(0, driver_dir)
    os.chdir(driver_dir)
    import run_bem  # noqa: E402
    from eSim_bem_utils_2J import main as engine_main  # noqa: E402
    from eSim_bem_utils_2J import integration as engine_integ  # noqa: E402
    return run_bem, engine_main, engine_integ


def pair_pool(sched_a, sched_b):
    # Pool-intersection merge copied from eSim_bem_utils_2J/main.py:2029-2034
    # (run_step8_paired_mc), not its own callable function -- same citation,
    # same code, as t21_diag_sample.py's pair_pool().
    common = None
    for keys in (set(sched_a.keys()), set(sched_b.keys())):
        common = keys if common is None else (common & keys)
    return sorted(common or [])


def get_paired_pool(engine_integ_mod, run_bem_mod, sched_dir, arch, city, cache):
    """Returns (pool:list[str], label:str) for (sched_dir, arch, city).
    Cached by (sched_dir, dtype, region) -- several cities share a
    dtype/region (e.g. Kelowna_5B and Vancouver_5C are both BC), and
    load_schedules()'s own pool for a given dtype/region is identical
    regardless of which city asked for it; the per-cell SEED still differs
    (via _step8_cell_seed(seed, label)), so this caches only the expensive
    engine load, never the draw."""
    cell = run_bem_mod.resolve_cell(arch, city)
    if not cell:
        return None, None
    _idf, _epw, region, dtype, label = cell
    key = (sched_dir, dtype, region)
    if key not in cache:
        p2022 = os.path.join(sched_dir, "BEM_Schedules_2022.csv")
        p2030 = os.path.join(sched_dir, "BEM_Schedules_2030.csv")
        if not (os.path.isfile(p2022) and os.path.isfile(p2030)):
            cache[key] = None
        else:
            sched_2022 = engine_integ_mod.load_schedules(p2022, dwelling_type=dtype, region=region)
            sched_2030 = engine_integ_mod.load_schedules(p2030, dwelling_type=dtype, region=region)
            cache[key] = pair_pool(sched_2022, sched_2030)
    return cache[key], label


def redraw(engine_main_mod, pool, label, seed, n):
    """Engine's own _step8_cell_seed() + random.Random(seed).sample(), same
    call as t21_diag_sample.py Q3. Returns {sample_idx(1-based): hh_id} or
    None if the pool is smaller than n."""
    if pool is None or len(pool) < n:
        return None
    cell_seed = engine_main_mod._step8_cell_seed(seed, label)
    rng = random.Random(cell_seed)
    drawn = rng.sample(pool, n)
    return {i + 1: str(h) for i, h in enumerate(drawn)}


def a2_compare(got, ref):
    """got = read from the run's own cell_manifest.csv; ref = the
    independent re-draw (or, in --selftest, a known-good copy)."""
    if not ref:
        return "NO_REDRAW", {}
    if not got:
        return "NO_RUN_OUTPUT", {}
    mismatches = {s: (got.get(s), ref.get(s)) for s in set(got) | set(ref) if got.get(s) != ref.get(s)}
    return ("PASS" if not mismatches else f"FAIL:{len(mismatches)}_mismatch"), mismatches


def ref_manifest_path(step8_ref_dir, step9_ref_dir, campaign, cell):
    """Staged copy of the PUBLISHED manifest (T21/ref/..., staged by this
    same employee turn from the local repo's BEM_Setup/SimResults_Step{8,9}
    -- these are historical reference files, read-only, never regenerated
    here) -- used only for A2-info's overlap count, never for the A2
    pass/fail verdict itself (that basis was struck, see module docstring)."""
    if campaign == "step8":
        if not step8_ref_dir:
            return None
        return os.path.join(step8_ref_dir, cell, "cell_manifest.csv.new_2022_2030_20260711")
    if not step9_ref_dir:
        return None
    arm = "activity" if campaign == "step9_activity" else "baseline"
    return os.path.join(step9_ref_dir, cell, arm, "cell_manifest.csv")


# ---------------------------------------------------------------------------
# --selftest -- the check must be SEEN failing before its PASS is trusted
# ---------------------------------------------------------------------------
def write_manifest(path, pairs):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sample", "sim_hh_id", "hhsize", "dtype", "pr"])
        for s in sorted(pairs):
            w.writerow([s, pairs[s], "", "", ""])


def run_selftest(run_bem_mod, engine_main_mod, engine_integ_mod, args):
    """Compute one real engine re-draw (SingleD__Toronto_5A, sched_activity),
    write it out as a manifest, COPY it, swap one sample's hh_id in the copy,
    and confirm a2_compare() reports FAIL on the swapped copy and PASS on the
    unmodified one. This tests the CHECK's own logic, not the campaign data."""
    arch, city = ARCHS[0], CITIES[0]
    cell = f"{arch}__{city}"
    sched_dir = os.path.join(args.t21_root, "sched_activity")
    if not (os.path.isfile(os.path.join(sched_dir, "BEM_Schedules_2022.csv"))
            and os.path.isfile(os.path.join(sched_dir, "BEM_Schedules_2030.csv"))):
        print(f"[SELFTEST] ERROR: staged schedule files missing under {sched_dir}; cannot selftest.")
        return False

    pool_cache = {}
    pool, label = get_paired_pool(engine_integ_mod, run_bem_mod, sched_dir, arch, city, pool_cache)
    redrawn = redraw(engine_main_mod, pool, label, args.seed, args.n)
    if not redrawn:
        print(f"[SELFTEST] ERROR: pool too small ({0 if pool is None else len(pool)}) "
              f"for n={args.n} at {cell}.")
        return False

    selftest_dir = os.path.join(args.t21_root, "out", "_selftest")
    os.makedirs(selftest_dir, exist_ok=True)
    good_path = os.path.join(selftest_dir, "cell_manifest_good.csv")
    bad_path = os.path.join(selftest_dir, "cell_manifest_bad.csv")

    write_manifest(good_path, redrawn)          # "original" manifest
    got_good = read_manifest_pairs(good_path)   # copy #1: unmodified

    bad_pairs = dict(redrawn)                   # copy #2: swap one id
    swap_key = sorted(bad_pairs)[0]
    real_id = bad_pairs[swap_key]
    fake_id = "999999999" if real_id != "999999999" else "888888888"
    bad_pairs[swap_key] = fake_id
    write_manifest(bad_path, bad_pairs)
    got_bad = read_manifest_pairs(bad_path)

    status_good, _ = a2_compare(got_good, redrawn)
    status_bad, mism_bad = a2_compare(got_bad, redrawn)

    print(f"[SELFTEST] cell={cell} label={label} pool_size={0 if pool is None else len(pool)} "
          f"n={args.n} swap sample={swap_key} {real_id}->{fake_id}")
    print(f"[SELFTEST] unmodified-copy vs redraw: {status_good} (expect PASS)")
    print(f"[SELFTEST] swapped-copy    vs redraw: {status_bad} (expect FAIL) mismatches={mism_bad}")

    ok = status_good == "PASS" and str(status_bad).startswith("FAIL")
    print(f"[SELFTEST] RESULT: {'PASS -- A2 check correctly detects a swapped id' if ok else 'FAIL -- selftest did NOT behave as expected, A2 check logic is suspect, do NOT trust the real run'}")
    return ok


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t21-root", default="/speed-scratch/o_iseri/2J_revision/T21")
    ap.add_argument("--code-root", default="/speed-scratch/o_iseri/2J_revision/code_step8/repo",
                     help="shared driver tree (run_paired_mc.py + eSim_bem_utils_2J), same one the arrays use.")
    ap.add_argument("--pub-sched-dir", default="/speed-scratch/o_iseri/2J_revision/T17/code/sched",
                     help="published (pre-rebuild) 2022/2030 schedule CSVs, for A2-info's published-pool size.")
    ap.add_argument("--step8-ref-dir", default=None,
                     help="staged copy of the published Step8 campaign_N50 per-cell manifests (T21/ref/step8).")
    ap.add_argument("--step9-ref-dir", default=None,
                     help="staged copy of the published Step9 campaign per-cell manifests (T21/ref/step9).")
    ap.add_argument("--n", type=int, default=50, help="planned households/cell (A1 denominator x2 years; A2 draw size).")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True)
    ap.add_argument("--selftest", action="store_true",
                     help="Run the A2-logic selftest only (swap-one-id-in-a-copy), print PASS/FAIL, exit; does NOT run A1-A4.")
    args = ap.parse_args()
    out_abs = os.path.abspath(args.out)

    run_bem_mod, engine_main_mod, engine_integ_mod = load_engine(args.code_root)

    if args.selftest:
        ok = run_selftest(run_bem_mod, engine_main_mod, engine_integ_mod, args)
        sys.exit(0 if ok else 1)

    act_dir = os.path.join(args.t21_root, "sched_activity")
    base_dir = os.path.join(args.t21_root, "sched_baseline")
    pool_cache = {}

    rows = []
    a2x_fail_cells = []
    for arch, city in zip(ARCHS, CITIES):
        cell = f"{arch}__{city}"
        pool_act, label = get_paired_pool(engine_integ_mod, run_bem_mod, act_dir, arch, city, pool_cache)
        pool_base, _ = get_paired_pool(engine_integ_mod, run_bem_mod, base_dir, arch, city, pool_cache)
        pool_pub, _ = get_paired_pool(engine_integ_mod, run_bem_mod, args.pub_sched_dir, arch, city, pool_cache)

        redraw_act = redraw(engine_main_mod, pool_act, label, args.seed, args.n)
        redraw_base = redraw(engine_main_mod, pool_base, label, args.seed, args.n)

        got_by_campaign = {}
        for campaign in CAMPAIGNS:
            out_dir = os.path.join(args.t21_root, "out", campaign, cell)
            got = read_manifest_pairs(os.path.join(out_dir, "cell_manifest.csv"))
            got_by_campaign[campaign] = got

            redrawn = redraw_act if campaign in ("step8", "step9_activity") else redraw_base
            new_pool = pool_act if campaign in ("step8", "step9_activity") else pool_base
            a2_status, mism = a2_compare(got, redrawn)

            ref_path = ref_manifest_path(args.step8_ref_dir, args.step9_ref_dir, campaign, cell)
            ref_pairs = read_manifest_pairs(ref_path) if ref_path else {}
            pub_overlap_n = (len(set(got.values()) & set(ref_pairs.values()))
                              if got and ref_pairs else ("NO_REF" if not ref_pairs else 0))

            delivered, n_samples, bad = count_delivered(out_dir)
            planned = args.n * 2  # n households x 2 years

            rows.append({
                "campaign": campaign, "cell": cell,
                "a1_delivered": delivered, "a1_planned": planned,
                "a1_samples_found": n_samples,
                "a1_bad_rowcount_n": len(bad),
                "a2_pairing": a2_status,
                "a2_mismatch_n": len(mism),
                "a2info_new_pool_size": (0 if new_pool is None else len(new_pool)),
                "a2info_pub_pool_size": (0 if pool_pub is None else len(pool_pub)),
                "a2info_pub_overlap_n": pub_overlap_n,
            })

        # A2X: Step 8 and both Step 9 campaigns must draw the SAME households.
        g8, g9a, g9b = got_by_campaign["step8"], got_by_campaign["step9_activity"], got_by_campaign["step9_baseline"]
        if g8 and g9a and g9b:
            a2x_status = "PASS" if (g8 == g9a == g9b) else "FAIL_cross_campaign_mismatch"
        else:
            a2x_status = "NO_RUN_OUTPUT"
        if a2x_status != "PASS":
            a2x_fail_cells.append((cell, a2x_status))
        for r in rows[-3:]:
            r["a2x_cross_campaign"] = a2x_status

    with open(out_abs, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["campaign", "cell", "a1_delivered", "a1_planned",
                      "a1_samples_found", "a1_bad_rowcount_n",
                      "a2_pairing", "a2_mismatch_n",
                      "a2info_new_pool_size", "a2info_pub_pool_size", "a2info_pub_overlap_n",
                      "a2x_cross_campaign"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    logs_dir = os.path.join(args.t21_root, "logs")
    a3 = {c: a3_fallback_scan(logs_dir, c) for c in CAMPAIGNS}
    a4_status, a4_diffs = a4_md5_check(args.t21_root)

    total_delivered = sum(r["a1_delivered"] for r in rows)
    total_planned = sum(r["a1_planned"] for r in rows)
    a2_fail_n = sum(1 for r in rows if not str(r["a2_pairing"]).startswith("PASS"))
    a3_hit_n = sum(len(v) for v in a3.values())

    print(f"[A1] delivered {total_delivered}/{total_planned} across {len(rows)} (campaign,cell) rows")
    print(f"[A2 restated] pairing FAIL/NO_REDRAW/NO_RUN rows: {a2_fail_n}/{len(rows)}")
    print(f"[A2X] cross-campaign (step8==step9_activity==step9_baseline) FAIL/NO_RUN cells: "
          f"{len(a2x_fail_cells)}/{len(CELLS)}")
    for cell, status in a2x_fail_cells:
        print(f"  A2X HIT {cell}: {status}")
    print(f"[A3] logs with a fallback/invalid hit: {a3_hit_n}")
    for campaign, hits in a3.items():
        for log_path, lines in hits.items():
            print(f"  A3 HIT {campaign} {log_path}: {len(lines)} line(s), e.g. {lines[0]!r}")
    print(f"[A4] {a4_status}: {a4_diffs if a4_diffs else 'all 4 sched files unchanged'}")
    print(f"Report -> {out_abs}")

    if a2_fail_n or a2x_fail_cells or a3_hit_n or a4_status != "PASS":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
