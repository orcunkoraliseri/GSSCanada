"""
16CEN15GSS Main Controller

Unified controller for the occupancy modeling pipeline.
Controls all steps from Census 2016 / GSS 2015 integration through BEM output generation.

Pipeline Steps:
    1. Alignment: Harmonize Census 2016 with GSS 2015
    2. Profile Matching: Assign GSS schedules to Census agents
    3. DTYPE Expansion: Refine dwelling types (Apartment splits, etc.)
    4. HH Aggregation: Convert to 5-minute household grids
    5. BEM Conversion: Generate hourly schedules for EnergyPlus

Usage:
    python 16CEN15GSS_main.py              # Interactive menu
    python 16CEN15GSS_main.py --sample 10  # Set sample percentage
"""

import sys
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_SAMPLE_PCT = 10  # Default sample percentage for pipeline


# =============================================================================
# MENU DISPLAY
# =============================================================================

def print_header() -> None:
    """Print the application header."""
    print("\n" + "=" * 60)
    print("  16CEN15GSS OCCUPANCY MODELING PIPELINE")
    print("  Census 2016 + GSS 2015 Integration")
    print("=" * 60)


def print_menu(sample_pct: int) -> None:
    """Print the main menu options."""
    print(f"\n  Current Sample: {sample_pct}%")
    print("-" * 40)
    print("  PIPELINE STEPS:")
    print("    1. Step 1: Alignment (Census + GSS harmonization)")
    print("    2. Step 2: Profile Matching (assign schedules)")
    print("    3. Step 3: DTYPE Expansion (refine dwelling types)")
    print("    4. Step 4: HH Aggregation (5-min grids)")
    print("    5. Step 5: BEM Conversion (hourly schedules)")
    print("")
    print("  COMBO:")
    print("    6. Run Full Pipeline (Steps 1-5)")
    print("")
    print("  UTILITIES:")
    print("    7. Census DTYPE Analysis")
    print("    8. Change Sample Percentage")
    print("")
    print("    0. Exit")
    print("-" * 40)


# =============================================================================
# STEP FUNCTIONS
# =============================================================================

def run_alignment() -> bool:
    """
    Step 1: Run Census-GSS alignment.

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 50)
    print("  STEP 1: ALIGNMENT")
    print("=" * 50)

    try:
        from occ_utils import (
            alignment_module as alignment
        )
    except ImportError:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "alignment",
                Path(__file__).parent / "16CEN15GSS_alignment.py"
            )
            alignment = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(alignment)
        except Exception as e:
            print(f"  ❌ Could not import alignment module: {e}")
            return False

    try:
        alignment.main()
        print("  ✅ Alignment complete!")
        return True
    except Exception as e:
        print(f"  ❌ Alignment failed: {e}")
        return False


def run_profile_matching(sample_pct: int) -> bool:
    """
    Step 2: Run profile matching.

    Args:
        sample_pct: Sample percentage for matching.

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 50)
    print(f"  STEP 2: PROFILE MATCHING ({sample_pct}% sample)")
    print("=" * 50)

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "profile_matcher",
            Path(__file__).parent / "16CEN15GSS_ProfileMatcher.py"
        )
        profile_matcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(profile_matcher)
    except Exception as e:
        print(f"  ❌ Could not import ProfileMatcher module: {e}")
        return False

    try:
        profile_matcher.main(sample_pct=sample_pct)
        print("  ✅ Profile matching complete!")
        return True
    except Exception as e:
        print(f"  ❌ Profile matching failed: {e}")
        return False


def run_dtype_expansion(sample_pct: int) -> bool:
    """
    Step 3: Run DTYPE expansion and refinement.

    Args:
        sample_pct: Sample percentage.

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 50)
    print(f"  STEP 3: DTYPE EXPANSION ({sample_pct}% sample)")
    print("=" * 50)

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dtype_expansion",
            Path(__file__).parent / "16CEN15GSS_DTYPE_expansion.py"
        )
        dtype_expansion = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dtype_expansion)
    except Exception as e:
        print(f"  ❌ Could not import DTYPE_expansion module: {e}")
        return False

    try:
        dtype_expansion.main(sample_pct=sample_pct)
        print("  ✅ DTYPE expansion complete!")
        return True
    except Exception as e:
        print(f"  ❌ DTYPE expansion failed: {e}")
        return False


def run_hh_aggregation(sample_pct: int) -> bool:
    """
    Step 4: Run household aggregation.

    Args:
        sample_pct: Sample percentage (for file naming).

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 50)
    print(f"  STEP 4: HOUSEHOLD AGGREGATION ({sample_pct}% sample)")
    print("=" * 50)

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hh_aggregation",
            Path(__file__).parent / "16CEN15GSS_HH_aggregation.py"
        )
        hh_aggregation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hh_aggregation)
    except Exception as e:
        print(f"  ❌ Could not import HH_aggregation module: {e}")
        return False

    try:
        hh_aggregation.main(sample_pct=sample_pct)
        print("  ✅ Household aggregation complete!")
        return True
    except Exception as e:
        print(f"  ❌ Household aggregation failed: {e}")
        return False


def run_bem_conversion(sample_pct: int) -> bool:
    """
    Step 5: Run BEM conversion.

    Args:
        sample_pct: Sample percentage (for file naming).

    Returns:
        True if successful, False otherwise.
    """
    print("\n" + "=" * 50)
    print(f"  STEP 5: BEM CONVERSION ({sample_pct}% sample)")
    print("=" * 50)

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "bem_converter",
            Path(__file__).parent / "16CEN15GSS_occToBEM.py"
        )
        bem_converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bem_converter)
    except Exception as e:
        print(f"  ❌ Could not import occToBEM module: {e}")
        return False

    try:
        bem_converter.main(sample_pct=sample_pct)
        print("  ✅ BEM conversion complete!")
        return True
    except Exception as e:
        print(f"  ❌ BEM conversion failed: {e}")
        return False


def run_full_pipeline(sample_pct: int) -> bool:
    """
    Run the complete pipeline (Steps 1-5).

    Args:
        sample_pct: Sample percentage for the pipeline.

    Returns:
        True if all steps successful, False otherwise.
    """
    print("\n" + "=" * 60)
    print("  RUNNING FULL PIPELINE")
    print(f"  Sample: {sample_pct}%")
    print("=" * 60)

    steps = [
        ("Alignment", lambda: run_alignment()),
        ("Profile Matching", lambda: run_profile_matching(sample_pct)),
        ("DTYPE Expansion", lambda: run_dtype_expansion(sample_pct)),
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

    # Print summary
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
        print("\n  🎉 Full pipeline completed successfully!")
    else:
        print("\n  ⚠️ Pipeline completed with errors.")

    return all_success


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def run_census_analysis() -> None:
    """Run Census DTYPE analysis."""
    print("\n" + "=" * 50)
    print("  CENSUS DTYPE ANALYSIS")
    print("=" * 50)

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cen_reader",
            Path(__file__).parent.parent / "cen_reader.py"
        )
        cen_reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cen_reader)
        cen_reader.main()
    except Exception as e:
        print(f"  ❌ Census analysis failed: {e}")


def change_sample_pct(current: int) -> int:
    """
    Prompt user to change sample percentage.

    Args:
        current: Current sample percentage.

    Returns:
        New sample percentage.
    """
    print(f"\n  Current sample: {current}%")
    try:
        new_pct = int(input("  Enter new sample percentage (1-100): "))
        if 1 <= new_pct <= 100:
            print(f"  ✅ Sample changed to {new_pct}%")
            return new_pct
        else:
            print("  ⚠️ Invalid range. Keeping current value.")
            return current
    except ValueError:
        print("  ⚠️ Invalid input. Keeping current value.")
        return current


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> None:
    """Main controller with interactive menu."""
    import argparse

    parser = argparse.ArgumentParser(
        description="16CEN15GSS Occupancy Modeling Pipeline Controller"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=DEFAULT_SAMPLE_PCT,
        help=f"Sample percentage (default: {DEFAULT_SAMPLE_PCT})"
    )
    parser.add_argument(
        "--run",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Run specific option directly (1-6)"
    )
    args = parser.parse_args()

    sample_pct = args.sample

    # If --run specified, execute directly without menu
    if args.run:
        print_header()
        if args.run == 1:
            run_alignment()
        elif args.run == 2:
            run_profile_matching(sample_pct)
        elif args.run == 3:
            run_dtype_expansion(sample_pct)
        elif args.run == 4:
            run_hh_aggregation(sample_pct)
        elif args.run == 5:
            run_bem_conversion(sample_pct)
        elif args.run == 6:
            run_full_pipeline(sample_pct)
        return

    # Interactive menu loop
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
            run_dtype_expansion(sample_pct)
        elif choice == "4":
            run_hh_aggregation(sample_pct)
        elif choice == "5":
            run_bem_conversion(sample_pct)
        elif choice == "6":
            run_full_pipeline(sample_pct)
        elif choice == "7":
            run_census_analysis()
        elif choice == "8":
            sample_pct = change_sample_pct(sample_pct)
        elif choice == "0":
            print("\n  Goodbye!")
            break
        else:
            print("  ⚠️ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
