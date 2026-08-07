import os
import platform
import sys

# Platform Detection
SYSTEM_PLATFORM = platform.system()

# EnergyPlus Paths
if SYSTEM_PLATFORM == 'Darwin':  # macOS
    DEFAULT_ENERGYPLUS_DIR = '/Applications/EnergyPlus-24-2-0'
elif SYSTEM_PLATFORM == 'Windows':
    DEFAULT_ENERGYPLUS_DIR = r'C:\EnergyPlusV24-2-0'
else:
    DEFAULT_ENERGYPLUS_DIR = '/usr/local/EnergyPlus-24-2-0'

# Allow Override via Environment Variable
ENERGYPLUS_DIR = os.environ.get('ENERGYPLUS_DIR', DEFAULT_ENERGYPLUS_DIR)

# Executable
_exe_ext = '.exe' if SYSTEM_PLATFORM == 'Windows' else ''
ENERGYPLUS_EXE = os.path.join(ENERGYPLUS_DIR, f'energyplus{_exe_ext}')

# IDD File
IDD_FILE = os.path.join(ENERGYPLUS_DIR, 'Energy+.idd')


# ---------------------------------------------------------------------------
# Multi-region weather routing
# ---------------------------------------------------------------------------

# Maps the PR region string stored in BEM_Schedules_*.csv (produced by
# *_occToBEM.py via self.pr_map) to a substring that uniquely identifies
# the correct EPW file in the WeatherFile directory.
# Keys must match the values produced by occToBEM pr_map exactly.
# Cities with no representative EPW are mapped to the nearest proxy.
PR_REGION_TO_EPW_CITY = {
    "Quebec":   "Montreal",   # CAN_QC_Montreal …
    "Ontario":  "Toronto",    # CAN_ON_Toronto …
    "Alberta":  "Calgary",    # CAN_AB_Calgary …
    "BC":       "Vancouver",  # CAN_BC_Vancouver … (coastal proxy for whole province)
    "Prairies": "Winnipeg",   # CAN_MB_Winnipeg … (covers MB + SK)
    "Atlantic": "Montreal",   # No Atlantic city in catalog; Montreal is nearest proxy
}


def resolve_epw_path(pr_region: str, weather_dir: str) -> str:
    """
    Return the EPW file path for a given PR region string.

    Searches *weather_dir* for a file whose name contains the mapped city
    keyword (case-insensitive).  Falls back to the first .epw file found if
    no match exists for the region.

    Args:
        pr_region:   Region string from the BEM CSV PR column
                     (e.g. "Quebec", "Ontario", "BC").
        weather_dir: Absolute path to the WeatherFile directory.

    Returns:
        Absolute path to the best-matching EPW file.

    Raises:
        FileNotFoundError: If *weather_dir* contains no .epw files at all.
    """
    import glob as _glob

    all_epws = sorted(_glob.glob(os.path.join(weather_dir, "*.epw")))
    if not all_epws:
        raise FileNotFoundError(
            f"No .epw files found in weather directory: {weather_dir}"
        )

    city_keyword = PR_REGION_TO_EPW_CITY.get(pr_region, "")
    if city_keyword:
        for epw in all_epws:
            if city_keyword.upper() in os.path.basename(epw).upper():
                return epw
        # City keyword not matched — fall through to first EPW with a warning
        import warnings
        warnings.warn(
            f"No EPW found for region '{pr_region}' (city='{city_keyword}') "
            f"in {weather_dir}. Using first available: {os.path.basename(all_epws[0])}"
        )

    return all_epws[0]


def resolve_idd_path() -> str:
    """
    Returns a validated path to the EnergyPlus IDD file.

    Resolution order:
      1. IDD_FILE env var (if set and the file exists)
      2. ENERGYPLUS_DIR / Energy+.idd (derived from config)

    Raises FileNotFoundError if the resolved path does not exist on disk.
    Raises RuntimeError if the IDD version string does not contain '24.2'.
    """
    # 1. Env-var override
    env_path = os.environ.get('IDD_FILE', '').strip()
    candidate = env_path if env_path else IDD_FILE

    if not os.path.isfile(candidate):
        raise FileNotFoundError(
            f"IDD file not found at '{candidate}'. "
            "Set the IDD_FILE env var or install EnergyPlus 24.2 in ENERGYPLUS_DIR."
        )

    # Version check: first ~10 lines of a valid IDD contain the version number
    try:
        with open(candidate, 'r', encoding='utf-8', errors='ignore') as f:
            header = ''.join(f.readline() for _ in range(10))
        if '24.2' not in header:
            raise RuntimeError(
                f"IDD file at '{candidate}' does not appear to be EnergyPlus 24.2 "
                f"(version string '24.2' not found in first 10 lines). "
                "Install EnergyPlus 24.2 or set IDD_FILE to the correct path."
            )
    except (RuntimeError, FileNotFoundError):
        raise
    except Exception:
        pass  # If the read fails for any other reason, skip the version check

    return candidate


# Global Environment Setup
def setup_environment():
    """Sets environment variables required for Eppy and other tools."""
    if 'IDD_FILE' not in os.environ:
        os.environ["IDD_FILE"] = IDD_FILE

# Auto-configure on import
setup_environment()
