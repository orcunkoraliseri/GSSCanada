"""t18c_pipeline.py -- T18c Frame v2 chain for ONE build (nf or nbf).

Task doc: 2026-09-15_T18c_wp1_frame_v2.md.
Parents:  2026-09-15_T18b_wp1_linkage_lever_and_frozen_frame.md (Design +
          Manager addendum 1 = Frame v2 spec, addendum 2), 2026-09-15_T18_
          wp1_rebuild_2022_build.md (paths). T18c reuses T18's and T18b's
          already-staged trees as READ-ONLY input; T18c writes only under
          /speed-scratch/o_iseri/2J_revision/T18c/.

Why Frame v2 (addendum 1): job 1328333's frame_filter() ran on each build's
POST-exclusion stock (*_Full_Aggregated_excl.csv) and found 849 (nf) / 869
(nbf) published households missing -- the 0.30 household at-home exclusion
(05_census_linkage.py:639-698) drops different households under a new donor
pool than it dropped for the published build. Frame v2 filters the
PRE-exclusion stock (*_Full_Aggregated.csv, run_exclusion()'s own input)
instead: "freeze the stock" means the 0.30 cut is not re-applied to a stock
that is frozen by design. The 0.30 cut itself is never removed from the
pipeline -- it is simply not the household-membership decision for the
frozen frame; the households it *would* have dropped are reported as a
limitation by t18c_metrics.py, not silently kept without comment.

Two builds (design, fixed):
  nf  = pre-exclusion stock is Arm N's own T18 output (no relink) ->
        Frame-v2 filter to the published 144,465 HH_ID set ->
        07_aug_to_bem.py --year 2022 -> validator.
  nbf = pre-exclusion stock is the Nb-f relink T18b already ran (job
        1328333 task 1 reached "STEP OK" through run_exclusion() before
        dying on the old frame_filter(); its Full_Aggregated.csv is already
        on disk) -> Frame-v2 filter -> a2b -> validator. NO SECOND RELINK.

Reused, read-only, not restaged (no edits, per task-doc rule):
  - t18_pipeline._load_module / _md5 / _report_file / log / _step
    (/speed-scratch/o_iseri/2J_revision/T18/T18_scripts/t18_pipeline.py)
  - t18b_pipeline.frame_filter() (generic: filters any HH_ID-keyed CSV to a
    published SIM_HH_ID set; only the INPUT path changes for Frame v2 --
    the function itself needs no changes) and
    t18b_pipeline.run_a2b_and_validator() (a2b.main() --year 2022 then
    BEMIntegrationValidator.run_all(), writes validator_result.json)
    (/speed-scratch/o_iseri/2J_revision/T18b/T18b_scripts/t18b_pipeline.py)
  - The a2b/validator script trio (07_aug_to_bem.py, activity_loads.py,
    07_bemIntegrationGSS_val.py) already staged read-only under
    T18b/<build>/repo/scripts/ by the T18b employee -- T18c does not
    restage or duplicate them (no repo-file edits, no new copies needed).

B5 (no writes to T18/ or T18b/ inputs): md5 of the pre-exclusion source file
and of the published-HH reference file are recorded before and after this
job's own run, inside this script (never on the login node), and written to
b5_source_md5.json under this build's own T18c output dir.
"""
import sys
import json
import time
import argparse
from pathlib import Path

T18_SCRIPTS_DIR = Path("/speed-scratch/o_iseri/2J_revision/T18/T18_scripts")
T18B_SCRIPTS_DIR = Path("/speed-scratch/o_iseri/2J_revision/T18b/T18b_scripts")
sys.path.insert(0, str(T18_SCRIPTS_DIR))
sys.path.insert(0, str(T18B_SCRIPTS_DIR))
import t18_pipeline as t18p     # _load_module, _md5, _report_file, log, _step (T18, read-only)
import t18b_pipeline as t18bp   # frame_filter(), run_a2b_and_validator() (T18b, read-only)

T18_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18")
T18B_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18b")
T18C_ROOT = Path("/speed-scratch/o_iseri/2J_revision/T18c")
PUBLISHED_HH_DEFAULT = T18_ROOT / "reference" / "BEM_Schedules_2022.csv"

t0 = time.time()


def log(msg):
    print(f"[T18C {time.time() - t0:7.1f}s] {msg}", flush=True)


def source_preexcl_path(build):
    """Frame v2's input: each build's PRE-exclusion aggregated stock
    (design item 1, task doc). Both files already exist on disk -- neither
    build relinks a second time."""
    if build == "nf":
        return (T18_ROOT / "arm_N" / "repo" / "outputs" / "aug_pipeline"
                 / "21CEN22GSS_aug_Full_Aggregated.csv")
    return (T18B_ROOT / "nbf" / "repo" / "outputs" / "aug_pipeline"
            / "21CEN22GSS_aug_Full_Aggregated.csv")


def scripts_dir_for(build):
    """a2b/validator scripts, reused read-only from T18b's own staging
    (both builds' T18b script dirs contain 07_aug_to_bem.py,
    activity_loads.py, 07_bemIntegrationGSS_val.py -- confirmed in the T18b
    doc Ledger; nbf's dir additionally has the linkage/rake scripts, unused
    here since Frame v2 does not relink)."""
    return T18B_ROOT / build / "repo" / "scripts"


def run_build(build, published_hh_path):
    src = source_preexcl_path(build)
    out_dir = T18C_ROOT / build / "repo" / "outputs" / "aug_pipeline"
    bems_dir = T18C_ROOT / build / "repo" / "outputs" / "BEM_Setup"
    out_dir.mkdir(parents=True, exist_ok=True)
    bems_dir.mkdir(parents=True, exist_ok=True)

    log(f"=========== T18c FRAME V2, build {build} ===========")
    log(f"Pre-exclusion source stock (read-only, from {'T18' if build == 'nf' else 'T18b'}): {src}")

    # ---- B5: md5 of the two read-only inputs, before -----------------------
    md5_src_before = t18p._md5(src)
    md5_pub_before = t18p._md5(published_hh_path)
    log(f"  B5 md5 before: src={md5_src_before}  published_hh={md5_pub_before}")

    filtered_path = out_dir / "21CEN22GSS_aug_Full_Aggregated_framev2.csv"
    missing_csv = out_dir / "missing_hh.csv"

    t18p._step(
        f"frame_filter v2 ({build}, pre-exclusion stock)",
        lambda: t18bp.frame_filter(src, published_hh_path, filtered_path, missing_csv),
    )

    scripts_dir = scripts_dir_for(build)
    t18p._step(
        f"a2b + validator on Frame-v2-filtered {build} stock",
        lambda: t18bp.run_a2b_and_validator(scripts_dir, filtered_path, bems_dir, out_dir),
    )

    # ---- B5: md5 of the two read-only inputs, after (never written to) -----
    md5_src_after = t18p._md5(src)
    md5_pub_after = t18p._md5(published_hh_path)
    b5 = {
        "source_stock": {"path": str(src), "md5_before": md5_src_before,
                          "md5_after": md5_src_after,
                          "unchanged": md5_src_after == md5_src_before},
        "published_hh_reference": {"path": str(published_hh_path),
                                    "md5_before": md5_pub_before,
                                    "md5_after": md5_pub_after,
                                    "unchanged": md5_pub_after == md5_pub_before},
    }
    (out_dir / "b5_source_md5.json").write_text(json.dumps(b5, indent=2))
    log(f"  B5 md5 after:  src={md5_src_after}  published_hh={md5_pub_after}")
    log(f"  B5 unchanged: source_stock={b5['source_stock']['unchanged']}  "
        f"published_hh={b5['published_hh_reference']['unchanged']}")

    log(f"=========== T18c FRAME V2, build {build} COMPLETE ===========")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", choices=["nf", "nbf"], required=True)
    ap.add_argument("--frame-filter", default=str(PUBLISHED_HH_DEFAULT),
                     help="path to the published-HH source file (SIM_HH_ID column)")
    args = ap.parse_args()
    run_build(args.build, Path(args.frame_filter))


if __name__ == "__main__":
    main()
