#!/usr/bin/env python3
"""
Test script to run Option 4 (Monte Carlo Comparative Simulation) with 5 iterations
"""
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bem_utils.main import option_kfold_comparative_simulation

# Mock user inputs for testing
# We'll need to modify the function to accept parameters or use environment variables
# For now, let's just call it and provide inputs when prompted

if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING OPTION 4: Monte Carlo Comparative Simulation with 5 iterations")
    print("=" * 80)

    # Note: This will still require interactive input
    # The user will need to:
    # 1. Select a building IDF
    # 2. Select a weather file
    # 3. Enter iter_count=5

    option_kfold_comparative_simulation()
