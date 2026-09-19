"""
21CEN22GSS Main Controller

Interactive controller for the Census 2021 + GSS 2022 occupancy pipeline.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


DEFAULT_SAMPLE_PCT = 10


def _load_module(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, Path(__file__).parent / filename)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def print_header() -> None:
    print("\n" + "=" * 60)
    print("  21CEN22GSS OCCUPANCY MODELING PIPELINE")
    print("  Census 2021 + GSS 2022 Integration")
    print("  Step 0 runs automatically on startup")
    print("=" * 60)


def print_menu(sample_pct: int) -> None:
    print(f"\n  Current Sample: {sample_pct}%")
    print("-" * 40)
    print("  PIPELINE STEPS:")
    print("    1. Step 1: Alignment (Census + GSS harmonization)")
    print("    2. Step 2: Profile Matching (assign schedules)")
    print("    3. Step 3: HH Aggregation (5-min grids)")
    print("    4. Step 4: BEM Conversion (hourly schedules)")
    print("")
    print("  COMBO:")
    print("    5. Run Full Pipeline (Steps 1-4)")
    print("")
    print("  UTILITIES:")
    print("    6. Change Sample Percentage")
    print("")
    print("    0. Exit")
    print("-" * 40)


def run_alignment() -> bool:
    print("\n" + "=" * 50)
    print("  STEP 1: ALIGNMENT")
    print("=" * 50)
    try:
        alignment = _load_module("alignment_21", "21CEN22GSS_alignment.py")
        alignment.main()
        print("  ✅ Alignment complete!")
        return True
    except Exception as e:
        print(f"  ❌ Alignment failed: {e}")
        return False


def run_profile_matching(sample_pct: int) -> bool:
    print("\n" + "=" * 50)
    print(f"  STEP 2: PROFILE MATCHING ({sample_pct}% sample)")
    print("=" * 50)
    try:
        profile_matcher = _load_module("profile_matcher_21", "21CEN22GSS_ProfileMatcher.py")
        profile_matcher.main(sample_pct=sample_pct)
        print("  ✅ Profile matching complete!")
        return True
    except Exception as e:
        print(f"  ❌ Profile matching failed: {e}")
        return False


def run_hh_aggregation(sample_pct: int) -> bool:
    print("\n" + "=" * 50)
    print(f"  STEP 3: HOUSEHOLD AGGREGATION ({sample_pct}% sample)")
    print("=" * 50)
    try:
        hh_aggregation = _load_module("hh_aggregation_21", "21CEN22GSS_HH_aggregation.py")
        hh_aggregation.main(sample_pct=sample_pct)
        print("  ✅ Household aggregation complete!")
        return True
    except Exception as e:
        print(f"  ❌ Household aggregation failed: {e}")
        return False


def run_bem_conversion(sample_pct: int) -> bool:
    print("\n" + "=" * 50)
    print(f"  STEP 4: BEM CONVERSION ({sample_pct}% sample)")
    print("=" * 50)
    try:
        bem_converter = _load_module("bem_converter_21", "21CEN22GSS_occToBEM.py")
        bem_converter.main(sample_pct=sample_pct)
        print("  ✅ BEM conversion complete!")
        return True
    except Exception as e:
        print(f"  ❌ BEM conversion failed: {e}")
        return False


def run_full_pipeline(sample_pct: int) -> bool:
    print("\n" + "=" * 60)
    print("  RUNNING FULL PIPELINE")
    print(f"  Sample: {sample_pct}%")
    print("=" * 60)

    steps = [
        ("Alignment", lambda: run_alignment()),
        ("Profile Matching", lambda: run_profile_matching(sample_pct)),
        ("HH Aggregation", lambda: run_hh_aggregation(sample_pct)),
        ("BEM Conversion", lambda: run_bem_conversion(sample_pct)),
    ]

    results = []
    for name, func in steps:
        success = func()
        results.append((name, success))
        if not success:
            print(f"\n  ⚠️ Pipeline stopped at: {name}")
            break

    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    all_success = True
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"    {status} {name}")
        if not success:
            all_success = False

    if all_success:
        print("\n  Full pipeline completed successfully!")
    else:
        print("\n  Pipeline completed with errors.")

    return all_success


def run_step0() -> bool:
    print("\n" + "=" * 50)
    print("  STEP 0: EPISODE PREPROCESSING")
    print("=" * 50)

    try:
        step0 = _load_module("step0_21", "21CEN22GSS_step0.py")
        step0.main(project_root=Path(__file__).resolve().parents[2])
        print("  ✅ Step 0 complete!")
        return True
    except Exception as e:
        print(f"  ❌ Step 0 failed: {e}")
        return False


def change_sample_pct(current: int) -> int:
    print(f"\n  Current sample: {current}%")
    try:
        new_pct = int(input("  Enter new sample percentage (1-100): "))
        if 1 <= new_pct <= 100:
            print(f"  ✅ Sample changed to {new_pct}%")
            return new_pct
        print("  ⚠️ Invalid range. Keeping current value.")
        return current
    except ValueError:
        print("  ⚠️ Invalid input. Keeping current value.")
        return current


def main() -> None:
    parser = argparse.ArgumentParser(
        description="21CEN22GSS Occupancy Modeling Pipeline Controller"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=DEFAULT_SAMPLE_PCT,
        help=f"Sample percentage (default: {DEFAULT_SAMPLE_PCT})",
    )
    parser.add_argument(
        "--run",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific option directly (1-5)",
    )
    args = parser.parse_args()

    sample_pct = args.sample

    if not run_step0():
        return

    if args.run:
        print_header()
        if args.run == 1:
            run_alignment()
        elif args.run == 2:
            run_profile_matching(sample_pct)
        elif args.run == 3:
            run_hh_aggregation(sample_pct)
        elif args.run == 4:
            run_bem_conversion(sample_pct)
        elif args.run == 5:
            run_full_pipeline(sample_pct)
        return

    print_header()

    while True:
        print_menu(sample_pct)
        try:
            choice = input("  Select option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye!")
            break

        if choice == "1":
            run_alignment()
        elif choice == "2":
            run_profile_matching(sample_pct)
        elif choice == "3":
            run_hh_aggregation(sample_pct)
        elif choice == "4":
            run_bem_conversion(sample_pct)
        elif choice == "5":
            run_full_pipeline(sample_pct)
        elif choice == "6":
            sample_pct = change_sample_pct(sample_pct)
        elif choice == "0":
            print("\n  Goodbye!")
            break
        else:
            print("  ⚠️ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
