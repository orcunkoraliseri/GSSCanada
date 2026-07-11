"""
_validate_joint_raked_2030.py
Step-6 Improvement 2 driver — LOCAL, one-shot.

Swaps 2030_synthetic_diaries_joint_raked.csv (calibrated, hom30+act30 joint-raked)
into the validator's hardcoded 2030_synthetic_diaries.csv path, runs
06_longitudinalForecastingGSS_val.py exactly once, then restores the base file
byte-identical. Archives the pre-existing base-forecast report to previous/
BEFORE the run (so nothing is lost if anything goes wrong).

Does NOT modify 06_forecast_rake.py, the validator, or any eSim_*.py file.
Run once: py 2J_docs_occ_nTemp/outputs_step6/improvement/_validate_joint_raked_2030.py
"""

from pathlib import Path
import shutil
import subprocess
import sys
import os
import hashlib

BASE = Path(r"C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main")
FC = BASE / "0_Occupancy/Outputs_21CEN22GSS/forecast_2030"
ORIG = FC / "2030_synthetic_diaries.csv"                 # base filename the validator reads
JOINT = FC / "2030_synthetic_diaries_joint_raked.csv"
BAK = FC / "2030_synthetic_diaries_ORIG_BAK.csv"
VAL = BASE / "eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecastingGSS_val.py"
STEP6 = BASE / "2J_docs_occ_nTemp/outputs_step6"
PREV = STEP6 / "previous"
PREV.mkdir(exist_ok=True)
REPORT = STEP6 / "step6_validation_report.html"
ARCHIVED_REPORT = PREV / "step6_validation_report_base_20260709.html"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    # 0. sanity: both files exist, validator exists
    assert ORIG.exists(), f"missing base file: {ORIG}"
    assert JOINT.exists(), f"missing joint-raked file: {JOINT}"
    assert VAL.exists(), f"missing validator: {VAL}"
    assert not BAK.exists(), f"stale backup already present, investigate first: {BAK}"

    orig_sha = sha256(ORIG)  # to verify byte-identical restore afterward
    print(f"[0] base file sha256: {orig_sha}")
    print(f"[0] base rows/size: {ORIG.stat().st_size:,} bytes")
    print(f"[0] joint-raked rows/size: {JOINT.stat().st_size:,} bytes")

    # 1. ARCHIVE the current base-forecast report FIRST (reversible, before any swap)
    if REPORT.exists() and not ARCHIVED_REPORT.exists():
        shutil.copy2(REPORT, ARCHIVED_REPORT)
        print(f"[1] archived current report -> {ARCHIVED_REPORT}")
    elif ARCHIVED_REPORT.exists():
        print(f"[1] archived report already present, leaving as-is -> {ARCHIVED_REPORT}")
    else:
        print("[1] WARNING: no existing report found to archive")

    # 2. back up base 2030 csv, swap joint-raked in
    shutil.copy2(ORIG, BAK)
    print(f"[2] backed up base -> {BAK}")

    validator_ok = False
    result = None
    try:
        shutil.copy2(JOINT, ORIG)  # validator will now read joint-raked under the base filename
        print(f"[2] joint-raked file swapped into {ORIG.name}")

        # 3. run validator ONCE
        print("[3] running validator (this reads a 530MB augmented_diaries.csv, expect a wait)...")
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run(
            [sys.executable, str(VAL)],
            capture_output=True, text=True, encoding="utf-8", timeout=900,
            env=env,
        )
        print("----- validator stdout -----")
        # Windows console default codepage (cp1252) can't encode some chars the
        # validator prints (e.g. U+2264 '<='); replace instead of crashing here --
        # this is purely a display concern, the report file itself is unaffected.
        print(result.stdout.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))
        if result.stderr and result.stderr.strip():
            print("----- validator stderr (tail) -----")
            print(result.stderr[-4000:].encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))
        validator_ok = (result.returncode == 0)
        print(f"[3] validator returncode = {result.returncode}")
    finally:
        # 4. ALWAYS restore the base file
        shutil.copy2(BAK, ORIG)
        BAK.unlink(missing_ok=True)
        print("[4] base file restored from backup, backup removed")

    # 5. verify base restored byte-identical
    restored_sha = sha256(ORIG)
    match = restored_sha == orig_sha
    print(f"[5] base restored byte-identical: {match} (sha256={restored_sha})")
    if not match:
        print("[5] !!!! BASE FILE NOT RESTORED BYTE-IDENTICAL — INVESTIGATE !!!!")
        return 1

    if not validator_ok:
        print("[FAIL] validator did not exit 0 -- STOP, do not promote report")
        return 1

    print("[DONE] validator ran successfully against joint-raked population; "
          f"report should now be at {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
