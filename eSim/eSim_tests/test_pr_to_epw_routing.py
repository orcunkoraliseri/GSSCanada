"""
Task 27 Step 4 — Unit tests for PR-to-EPW routing.

Tests config.resolve_epw_path() for all six PR keys, an unmapped region,
an empty string, and that the CSV contains all six expected PR values.

Usage:
    py -3 eSim_tests/test_pr_to_epw_routing.py
"""
import os
import sys
import warnings

# Make project root importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from eSim_bem_utils import config

# ---------------------------------------------------------------------------
# Locate weather directory (same logic as main.py)
# ---------------------------------------------------------------------------
BEM_SETUP_DIR = os.path.join(PROJECT_ROOT, "BEM_Setup")
WEATHER_DIR = os.path.join(BEM_SETUP_DIR, "WeatherFile")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def check(description, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{status}] {description}{suffix}")
    return condition


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_all_six_pr_keys():
    """All six canonical PR keys must resolve to an existing EPW file."""
    print("\n-- test_all_six_pr_keys --")
    keys = ["Quebec", "Ontario", "Alberta", "BC", "Prairies", "Atlantic"]
    all_pass = True
    for pr in keys:
        try:
            epw = config.resolve_epw_path(pr, WEATHER_DIR)
            ok = os.path.isfile(epw)
            city = config.PR_REGION_TO_EPW_CITY.get(pr, "")
            all_pass &= check(
                f"PR='{pr}' -> {os.path.basename(epw)}",
                ok and city.upper() in os.path.basename(epw).upper(),
                "file exists and city keyword matches" if ok else "FILE MISSING",
            )
        except Exception as exc:
            check(f"PR='{pr}' raised exception", False, str(exc))
            all_pass = False
    return all_pass


def test_unmapped_region_falls_back():
    """An unknown PR string (not in config dict) must fall back silently to first EPW.

    resolve_epw_path only warns when a *known* PR city keyword can't find its file.
    For a completely unknown key (no city mapping), it falls back to first EPW without
    warning — that is the specified behavior.
    """
    print("\n-- test_unmapped_region_falls_back --")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            epw = config.resolve_epw_path("UNKNOWN_REGION", WEATHER_DIR)
            no_warn = not any("UNKNOWN_REGION" in str(w.message) for w in caught)
            ok = os.path.isfile(epw)
            return (
                check("Fallback EPW exists", ok, os.path.basename(epw))
                & check("No spurious warning for fully unknown PR", no_warn)
            )
        except FileNotFoundError as exc:
            return check("WeatherDir exists", False, str(exc))


def test_empty_string_falls_back():
    """An empty PR string must fall back gracefully (no crash, no warning)."""
    print("\n-- test_empty_string_falls_back --")
    try:
        epw = config.resolve_epw_path("", WEATHER_DIR)
        ok = os.path.isfile(epw)
        return check("Empty PR falls back to first EPW", ok, os.path.basename(epw))
    except Exception as exc:
        return check("Empty PR — no exception", False, str(exc))


def test_csv_pr_distribution():
    """The 2022 BEM schedule CSV must contain all six expected PR values."""
    print("\n-- test_csv_pr_distribution --")
    import glob
    import csv

    csv_files = sorted(glob.glob(os.path.join(BEM_SETUP_DIR, "BEM_Schedules_*.csv")))
    if not csv_files:
        return check("At least one BEM_Schedules CSV exists", False)

    expected_prs = set(config.PR_REGION_TO_EPW_CITY.keys())
    all_pass = True
    for csv_path in csv_files:
        year_tag = os.path.basename(csv_path).replace(".csv", "")
        found_prs = set()
        try:
            with open(csv_path, encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                fieldnames_lower = [f.lower() for f in (reader.fieldnames or [])]
                if "pr" not in fieldnames_lower:
                    all_pass &= check(
                        f"{year_tag}: 'PR' column present", False, "column missing"
                    )
                    continue
                # Find actual column name (could be 'PR', 'pr', etc.)
                pr_col = next(
                    f for f in (reader.fieldnames or []) if f.lower() == "pr"
                )
                for row in reader:
                    pr_val = (row.get(pr_col) or "").strip()
                    if pr_val:
                        found_prs.add(pr_val)
        except Exception as exc:
            all_pass &= check(f"{year_tag}: readable", False, str(exc))
            continue

        missing = expected_prs - found_prs
        extra   = found_prs - expected_prs
        all_pass &= check(
            f"{year_tag}: all 6 PR values present",
            not missing,
            f"found={sorted(found_prs)}" + (f"  MISSING={sorted(missing)}" if missing else ""),
        )
        if extra:
            print(f"    Note: extra PR values in CSV (not in config): {sorted(extra)}")
    return all_pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Task 27 — PR-to-EPW routing tests")
    print(f"WeatherDir: {WEATHER_DIR}")
    print("=" * 60)

    results = [
        test_all_six_pr_keys(),
        test_unmapped_region_falls_back(),
        test_empty_string_falls_back(),
        test_csv_pr_distribution(),
    ]

    n_pass = sum(results)
    n_fail = len(results) - n_pass
    print(f"\n{'='*60}")
    print(f"Result: {n_pass}/{len(results)} test groups passed, {n_fail} failed.")
    sys.exit(0 if n_fail == 0 else 1)
