"""t18_pipeline.py -- T18 chain orchestrator for ONE arm (C or N).

Runs, without editing any pipeline source file:
  05_census_linkage.py --full --region-tier
  -> 05_postlink_rake.py --joint
  -> 05_census_linkage.py --aggregate
  -> 05_census_linkage.py --bem        (added -- see Decisions below)
  -> 05_census_linkage.py --exclusion
  -> 07_aug_to_bem.py --year 2022
  -> 07_bemIntegrationGSS_val.py --year 2022

Task doc: 2026-09-15_T18_wp1_rebuild_2022_build.md.
Reading doc: 2026-09-15_T13_wp1_rebuild_2022_reading.md (Q1-Q3 for the chain,
donor logic, and filter point).

METHOD (T13 Q3, option (a)): each pipeline script is loaded as a fresh module
via importlib.util.spec_from_file_location(), so its own
`if __name__ == "__main__":` CLI block never fires. The module's path
constants are then monkeypatched to point at THIS arm's staged tree BEFORE any
of its functions are called. Function bodies are byte-for-byte untouched --
only the module-global names they resolve at call time change (they are plain
module-level names, not function parameters, so this is safe: T13 Q3 confirmed
load_augmented_pool() is always called with `str(AUGMENTED_DIARIES)` re-read
from the module global, not a passed argument -- same pattern holds for every
other constant patched below).

DECISIONS (this task, recorded here and in the task doc's own Decisions
section -- read the doc for the full citations):

1. BASE-path bug found while reading 05_census_linkage.py. The file's own
   docstring (05_census_linkage.py:28-32) claims
   `BASE = Path(__file__).resolve().parents[2]` lands on the repo root
   ("parents[2] = GSSCanada-main/"), assuming the file sits TWO directories
   under the repo root. On the live repo it actually sits at
   eSim/eSim_occ_utils/25CEN22GSS_classification/05_census_linkage.py --
   THREE directories under the repo root -- so parents[2] resolves to
   GSSCanada-main/eSim/, not GSSCanada-main/. Verified directly: a plain
   existence check found `eSim/2J_docs_occ_nTemp/` does NOT exist on disk,
   while the file that constant is meant to reach
   (`2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv`, 530,141,993
   bytes) exists only at the true repo root. This means the script's own
   built-in path constants, AS CODED TODAY, cannot resolve correctly from
   their current on-disk location -- most likely the "eSim/" wrapper
   directory was added in a later reorg (every file under eSim/ carries the
   same Aug-13 mtime, well after the Jul-9 production run) and nobody re-ran
   the script afterwards to notice. This is exactly the scenario the task
   doc's own instruction anticipates ("If any script resolves paths outside
   its tree ... use a wrapper that sets the module path constants"), so this
   file monkeypatches every path constant explicitly and never relies on
   BASE at all -- sidesteps the bug entirely regardless of which directory
   depth is "correct".

2. run_bem() (05_census_linkage.py --bem, Sub-step 5F) is inserted between
   run_aggregate() and run_exclusion(). This is NOT in the task doc's headline
   chain summary, but run_exclusion() (05_census_linkage.py:678) reads
   `21CEN22GSS_aug_BEM_Schedules.csv`, which only run_bem() writes -- without
   it, run_exclusion() would raise FileNotFoundError on the first call, for
   BOTH arms. Order matches 2J_improvements_master_log.md:56's own stated
   rebuild order: "Full downstream rebuild run
   (--aggregate -> --bem -> --exclusion -> BEM 2022/2030)".

3. --region-tier: the current on-disk build used it. Evidence:
   2J_improvements_master_log.md:51 ("Real fix: merged the region-folded key
   into Tier-2 itself") logs 2005 matched share 9.03%->15.76%
   (25,863->45,164 rows); T13 Q4 independently reports the SAME number
   (2005 15.76%, 45,164 rows) as the CURRENT build's per-cycle tier share.
   Both numbers match exactly, and the flag defaults to False ("reproduces
   pre-region-tier behaviour bit-for-bit" -- 05_census_linkage.py:139-140),
   so the only way the current build shows 15.76% is if --region-tier was
   passed. Both arms here call run_linkage_full(region_tier=True) for this
   reason -- Arm C's whole purpose is to reproduce the current build (R0), so
   getting this flag wrong would make R0 fail for a reason unrelated to the
   staged-chain question the acceptance test is designed to isolate.

Per-arm tree layout (WORKDIR_ROOT/arm_<C|N>/repo/):
  scripts/   -- copies of 05_census_linkage.py, 05_postlink_rake.py,
                07_aug_to_bem.py, 07_bemIntegrationGSS_val.py, activity_loads.py
                (activity_loads.py MUST be co-located with 07_aug_to_bem.py:
                that script does `sys.path.insert(0, str(HERE))` then
                `import activity_loads` at module-import time, which cannot be
                monkeypatched after the fact -- HERE is fixed by wherever the
                .py file physically sits, not by any constant).
  inputs/    -- augmented_diaries.csv (arm-specific: full pool for C, 2022-only
                for N) and Aligned_Census_2022.csv (identical for both arms).
  outputs/aug_pipeline/  -- OUT_DIR equivalent (Full_Schedules/Matched_Keys/
                Full_Aggregated/BEM_Schedules[5F]/*_excl files).
  outputs/BEM_Setup/     -- BEMS equivalent (BEM_Schedules_2022.csv, the final
                Step-7 input, + outputs_step7/ validation report).
"""
import sys
import os
import time
import hashlib
import importlib.util
import argparse
from pathlib import Path

WORKDIR_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18")

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def _step(name, fn):
    log(f"--- STEP START: {name} ---")
    try:
        fn()
    except Exception:
        log(f"--- STEP FAILED: {name} ---")
        raise
    log(f"--- STEP OK: {name} ---")


def _load_module(name, path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing staged script: {path}")
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _report_file(p):
    if p.exists():
        log(f"  {p.name}: {p.stat().st_size:,} bytes, md5={_md5(p)}")
    else:
        log(f"  {p.name}: MISSING")


def run_arm(arm):
    assert arm in ("C", "N"), f"unknown arm: {arm}"
    arm_dir = WORKDIR_ROOT / f"arm_{arm}"
    scripts = arm_dir / "repo" / "scripts"
    out_dir = arm_dir / "repo" / "outputs" / "aug_pipeline"
    bems_dir = arm_dir / "repo" / "outputs" / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    # Arm C (control) reads the shared full-pool input directly -- no need to
    # duplicate a 530 MB file per arm. Arm N reads its own 2022-only filtered
    # copy (t18_filter.py's output), which is NOT staged from local -- it is
    # produced on a Speed compute node (task doc design: "filtered on a
    # compute node"). Aligned_Census_2022.csv is identical for both arms and
    # likewise not duplicated.
    if arm == "C":
        diaries_path = WORKDIR_ROOT / "input" / "augmented_diaries.csv"
    else:
        diaries_path = arm_dir / "repo" / "inputs" / "augmented_diaries.csv"
    census_path = WORKDIR_ROOT / "input" / "Aligned_Census_2022.csv"

    log(f"=========== ARM {arm} ===========")
    log("Input files (md5 recorded before any chain step runs):")
    _report_file(diaries_path)
    _report_file(census_path)

    # ---- Step 1: 05_census_linkage.py --full --region-tier -----------------
    linkage = _load_module(f"t18_linkage_{arm}", scripts / "05_census_linkage.py")
    linkage.AUGMENTED_DIARIES = diaries_path
    linkage.CENSUS_FILE = census_path
    linkage.OUT_DIR = out_dir

    _step("linkage.run_linkage_full(region_tier=True)",
          lambda: linkage.run_linkage_full(region_tier=True))

    # ---- Step 2: 05_postlink_rake.py --joint --------------------------------
    rake = _load_module(f"t18_rake_{arm}", scripts / "05_postlink_rake.py")
    rake._FULL_SCHED_PATH = out_dir / "21CEN22GSS_aug_Full_Schedules.csv"
    rake._MATCHED_KEYS_PATH = out_dir / "21CEN22GSS_aug_Matched_Keys.csv"

    _step("rake.main_joint()", rake.main_joint)

    # ---- Step 3: 05_census_linkage.py --aggregate ---------------------------
    _step("linkage.run_aggregate()", linkage.run_aggregate)

    # ---- Step 4: 05_census_linkage.py --bem (Decision 2: needed by --exclusion)
    _step("linkage.run_bem()", linkage.run_bem)

    # ---- Step 5: 05_census_linkage.py --exclusion ---------------------------
    _step("linkage.run_exclusion()", linkage.run_exclusion)

    # ---- Step 6: 07_aug_to_bem.py --year 2022 -------------------------------
    a2b = _load_module(f"t18_a2b_{arm}", scripts / "07_aug_to_bem.py")
    a2b.AUG = out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
    a2b.BEMS = bems_dir

    def _run_a2b():
        old_argv = sys.argv
        sys.argv = ["07_aug_to_bem.py", "--year", "2022"]
        try:
            a2b.main()
        finally:
            sys.argv = old_argv

    _step("a2b.main() --year 2022", _run_a2b)

    # ---- Step 7: 07_bemIntegrationGSS_val.py --year 2022 --------------------
    bval = _load_module(f"t18_bval_{arm}", scripts / "07_bemIntegrationGSS_val.py")
    bval.BEMS = bems_dir
    bval.AUG = out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv"

    def _run_bval():
        validator = bval.BEMIntegrationValidator(
            year="2022", outputs_dir=str(out_dir / "outputs_step7"))
        validator.run_all()

    _step("BEMIntegrationValidator(year=2022).run_all()", _run_bval)

    # ---- Final output inventory (md5 + size) --------------------------------
    log("Output files (md5 recorded after the full chain completed):")
    for p in [
        out_dir / "21CEN22GSS_aug_Full_Schedules.csv",
        out_dir / "21CEN22GSS_aug_Matched_Keys.csv",
        out_dir / "21CEN22GSS_aug_Full_Aggregated.csv",
        out_dir / "21CEN22GSS_aug_BEM_Schedules.csv",
        out_dir / "21CEN22GSS_aug_Full_Aggregated_excl.csv",
        out_dir / "21CEN22GSS_aug_Full_Schedules_excl.csv",
        out_dir / "21CEN22GSS_aug_BEM_Schedules_excl.csv",
        out_dir / "21CEN22GSS_aug_excluded_ppids.csv",
        bems_dir / "BEM_Schedules_2022.csv",
        bems_dir / "BEM_Schedules_2022_baseline.csv",
    ]:
        _report_file(p)

    log(f"=========== ARM {arm} CHAIN COMPLETE ===========")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["C", "N"], required=True)
    args = ap.parse_args()
    run_arm(args.arm)


if __name__ == "__main__":
    main()
