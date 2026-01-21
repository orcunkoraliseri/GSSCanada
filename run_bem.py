#!/usr/bin/env python3
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bem_utils.main import main
except ImportError as e:
    print(f"Error importing bem_utils: {e}")
    print("Make sure you are running this script from the project root.")
    sys.exit(1)

if __name__ == "__main__":
    main()
