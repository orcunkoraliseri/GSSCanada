"""
00_mainGSS.py

Master script to coordinate and run the Occupancy Modeling Pipeline steps.
Provides options to run the entire pipeline or individual steps.

Steps included:
- Step 1: Data Collection & Column Selection (01_readingGSS.py)
- Step 2: Data Harmonization (02_harmonizeGSS.py)
- Step 3: Merging & Derivations (03_mergingGSS.py)

Usage:
  # Interactively:
  python 00_mainGSS.py
  
  # Or via explicit flags:
  python 00_mainGSS.py --all
  python 00_mainGSS.py --step1 --step2
"""

import argparse
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name: str) -> None:
    """Run a Python script via subprocess and stream output."""
    print(f"\n{'='*55}")
    print(f"Executing: {script_name}")
    print(f"{'='*55}")
    
    script_path = os.path.join(SCRIPT_DIR, script_name)
    try:
        subprocess.run(["python", script_path], check=True, cwd=SCRIPT_DIR)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Pipeline failed during execution of {script_name}.")
        print(f"Exit code: {e.returncode}")
        sys.exit(1)
    print(f"✅ {script_name} completed successfully.\n")


def print_menu() -> str:
    """Print the interactive selection menu and get user choice."""
    print("\nOccupancy Modeling Pipeline - GSS")
    print("---------------------------------")
    print("1. Run Step 1 only (Reading/Extraction + Validation)")
    print("2. Run Step 2 only (Harmonization + Validation)")
    print("3. Run Step 3 only (Merging & Derivations)")
    print("A. Run All Steps sequentially")
    print("Q. Quit")
    choice = input("\nEnter your choice [1/2/3/A/Q]: ").strip().upper()
    return choice


def main() -> None:
    parser = argparse.ArgumentParser(description="Master script for GSS Pipeline.")
    parser.add_argument("--step1", action="store_true", help="Run Step 1 only")
    parser.add_argument("--step2", action="store_true", help="Run Step 2 only")
    parser.add_argument("--step3", action="store_true", help="Run Step 3 only")
    parser.add_argument("--all", action="store_true", help="Run all steps sequentially")
    
    args = parser.parse_args()
    
    # If arguments are passed, run in non-interactive mode
    if args.all or args.step1 or args.step2 or args.step3:
        if args.all:
            run_script("01_readingGSS.py")
            run_script("02_harmonizeGSS.py")
            run_script("03_mergingGSS.py")
            print("🚀 Full pipeline executed successfully.")
        else:
            if args.step1:
                run_script("01_readingGSS.py")
            if args.step2:
                run_script("02_harmonizeGSS.py")
            if args.step3:
                run_script("03_mergingGSS.py")
            print("🏁 Selected steps executed successfully.")
        return

    # If no flags provided, launch the interactive command line menu
    while True:
        choice = print_menu()
        if choice == '1':
            run_script("01_readingGSS.py")
            break
        elif choice == '2':
            run_script("02_harmonizeGSS.py")
            break
        elif choice == '3':
            run_script("03_mergingGSS.py")
            break
        elif choice == 'A':
            run_script("01_readingGSS.py")
            run_script("02_harmonizeGSS.py")
            run_script("03_mergingGSS.py")
            print("🚀 Full pipeline executed successfully.")
            break
        elif choice == 'Q':
            print("Exiting pipeline. Have a great day!")
            break
        else:
            print("Invalid choice. Please attempt entering 1, 2, 3, A, or Q.")


if __name__ == "__main__":
    main()
