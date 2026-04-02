"""
Cross-platform configuration for eSim_occ_utils modules.

This module provides consistent base directory paths that work across
macOS and Windows systems. Import BASE_DIR from this module instead of
hardcoding paths.

Usage:
    from eSim_occ_utils.occ_config import BASE_DIR, DATA_DIR, OUTPUT_DIR
"""

import os
import platform
from pathlib import Path

# Platform Detection
SYSTEM_PLATFORM = platform.system()

# Default base directories by platform
if SYSTEM_PLATFORM == 'Darwin':  # macOS
    _DEFAULT_BASE_DIR = Path('/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/0_Occupancy')
elif SYSTEM_PLATFORM == 'Windows':
    _DEFAULT_BASE_DIR = Path(r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\0_Occupancy')
else:  # Linux or other
    _DEFAULT_BASE_DIR = Path.home() / 'GSSCanada' / 'Occupancy'

# Allow override via environment variable
# Set GSS_BASE_DIR environment variable to use a custom path
BASE_DIR = Path(os.environ.get('GSS_BASE_DIR', _DEFAULT_BASE_DIR))

# Common subdirectories
DATA_DIR = BASE_DIR / 'DataSources_CENSUS'
OUTPUT_DIR = BASE_DIR / 'Outputs_CENSUS'
OUTPUT_DIR_GSS = BASE_DIR / 'Outputs_GSS'
OUTPUT_DIR_ALIGNED = BASE_DIR / 'Outputs_Aligned'
MODEL_DIR = BASE_DIR / 'saved_models_cvae'

# Ensure output directories exist
for dir_path in [OUTPUT_DIR, OUTPUT_DIR_GSS, OUTPUT_DIR_ALIGNED, MODEL_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """
    Returns the project root directory (GSSCanada-main).
    This is useful for accessing BEM_Setup and other project-level resources.
    """
    return Path(__file__).resolve().parent.parent


# Project root for BEM-related paths
PROJECT_ROOT = get_project_root()
BEM_SETUP_DIR = PROJECT_ROOT / 'BEM_Setup'
