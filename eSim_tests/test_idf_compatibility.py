"""
Task 29 — IDF / dwelling-type compatibility check — test harness.

Runs 6 test cases against validate_idf_compatibility() and exits 0 on all-pass,
1 on any failure.  Output is also written to eSim_tests/test_idf_compatibility_output.txt.

Usage:
    py -3 eSim_tests/test_idf_compatibility.py
"""
import io
import os
import sys
import contextlib

# ── path setup ────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from eppy.modeleditor import IDF
from eSim_bem_utils.integration import validate_idf_compatibility
from eSim_bem_utils import config

BUILDINGS_DIR    = os.path.join(PROJECT_ROOT, "BEM_Setup", "Buildings")
NEIGH_DIR        = os.path.join(PROJECT_ROOT, "BEM_Setup", "Neighbourhoods")
MONTREAL_IDF     = os.path.join(BUILDINGS_DIR,
    "Baseline_6A_Montreal_US+SF+CZ6A+gasfurnace+heatedbsmt+IECC_2021.idf")
NEIGHBOURHOOD_IDF = os.path.join(NEIGH_DIR, "NUS_RC1.idf")

IDF.setiddname(config.resolve_idd_path())

# ── helpers ───────────────────────────────────────────────────────────────────

def capture_stdout(fn):
    """Call fn(); return (stdout_str, exception_or_None)."""
    buf = io.StringIO()
    exc = None
    with contextlib.redirect_stdout(buf):
        try:
            fn()
        except Exception as e:
            exc = e
    return buf.getvalue(), exc


def run_test(number, description, fn, expect_error=False, expect_warning=False):
    stdout, exc = capture_stdout(fn)
    if expect_error:
        ok = isinstance(exc, ValueError)
        result = "PASS" if ok else "FAIL"
        detail = "" if ok else f"  Expected ValueError, got: {exc!r}"
    elif expect_warning:
        ok = exc is None and "[Warning]" in stdout
        result = "PASS" if ok else "FAIL"
        if exc:
            detail = f"  Unexpected exception: {exc!r}"
        elif "[Warning]" not in stdout:
            detail = f"  Expected [Warning] in stdout, got: {stdout!r}"
        else:
            detail = ""
    else:
        ok = exc is None
        result = "PASS" if ok else "FAIL"
        detail = "" if ok else f"  Unexpected exception: {exc!r}"
        # Also check no warning printed for the dtype-silent-pass case
        if ok and expect_warning is False and "[Warning]" in stdout and number == 6:
            ok = False
            result = "FAIL"
            detail = f"  Expected NO [Warning] but got: {stdout!r}"

    print(f"  Test {number}: [{result}] {description}")
    if detail:
        print(detail)
    return ok


# ── test cases ────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Task 29 — IDF compatibility check — 6 test cases")
    print(f"  Montreal IDF    : {os.path.basename(MONTREAL_IDF)}")
    print(f"  Neighbourhood IDF: {os.path.basename(NEIGHBOURHOOD_IDF)}")
    print("=" * 70)

    results = []

    # 1. Happy path single: Montreal IDF in single mode — no exception
    results.append(run_test(
        1, "Happy path single (Montreal, mode='single', dtype='SingleD')",
        lambda: validate_idf_compatibility(MONTREAL_IDF, mode='single', dwelling_type='SingleD'),
    ))

    # 2. Happy path neighbourhood: NUS_RC1 in neighbourhood mode — no exception
    results.append(run_test(
        2, "Happy path neighbourhood (NUS_RC1, mode='neighbourhood')",
        lambda: validate_idf_compatibility(NEIGHBOURHOOD_IDF, mode='neighbourhood'),
    ))

    # 3. Mode mismatch — single IDF in neighbourhood mode — expect ValueError
    results.append(run_test(
        3, "Mode mismatch: single IDF in neighbourhood mode → ValueError",
        lambda: validate_idf_compatibility(MONTREAL_IDF, mode='neighbourhood'),
        expect_error=True,
    ))

    # 4. Mode mismatch — neighbourhood IDF in single mode — expect ValueError
    results.append(run_test(
        4, "Mode mismatch: neighbourhood IDF in single mode → ValueError",
        lambda: validate_idf_compatibility(NEIGHBOURHOOD_IDF, mode='single'),
        expect_error=True,
    ))

    # 5. Dtype warning: Montreal + mode='single' + dwelling_type='MidRise'
    #    IDF filename contains 'SF' which is incompatible with MidRise → [Warning]
    results.append(run_test(
        5, "Dtype warning: Montreal + dwelling_type='MidRise' → [Warning] printed",
        lambda: validate_idf_compatibility(MONTREAL_IDF, mode='single', dwelling_type='MidRise'),
        expect_warning=True,
    ))

    # 6. Dtype silent-pass: Montreal + mode='single' + dwelling_type='SingleD'
    #    IDF filename contains 'SF' → SingleD is compatible → no warning
    results.append(run_test(
        6, "Dtype silent-pass: Montreal + dwelling_type='SingleD' → no warning",
        lambda: validate_idf_compatibility(MONTREAL_IDF, mode='single', dwelling_type='SingleD'),
    ))

    print("=" * 70)
    passed = sum(results)
    total  = len(results)
    print(f"Result: {passed}/{total} tests passed.")

    out_path = os.path.join(os.path.dirname(__file__), "test_idf_compatibility_output.txt")
    return passed, total, out_path


if __name__ == "__main__":
    # Re-run capturing everything to the output file as well
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        passed, total, out_path = main()
    output = buf.getvalue()
    print(output, end="")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"\nOutput written to {out_path}")
    sys.exit(0 if passed == total else 1)
