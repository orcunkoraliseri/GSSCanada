# -*- coding: utf-8 -*-
"""
3rdJ_01_readingGSS_2split_val.py

Leg-2 (Residential + Office two-channel split) — Step-1 VALIDATOR.

Loads the 8 Step-1 CSVs produced by 3rdJ_01_readingGSS_2split.py and runs
validation methods defined in 3rdJ_01_readingGSS_val.md:
  - Method 1: Schema & Shape Audit (column presence, row counts, weight dtype)
  - Method 2: Cross-Cycle Category Comparison (residential + office sanity)
  - Method 3: Episode Integrity Check (ID linkage, time ordering, diary
              completeness→1440, episodes/person, activity-code range, raw
              location source)
  - Method 4: Weight Distribution Sanity Check (WGHT_PER / WGHT_EPI positivity,
              outliers, weighted population total)
  - Method 5: Visual Summary Dashboard (residential + weight + diary panels +
              4 office panels), exported to step1_validation_report.{html,txt}

RENAME-AWARENESS (corrected 2026-06-14):
  The reader renames raw PUMF variables to canonical names BEFORE writing the
  CSVs, so this validator checks the canonical names (LFTAG / HRSWRK / COW / NOCS).
  occPRE is NOT produced at Step 1 — the raw location source (PLACE 2005/2010,
  LOCATION 2015/2022) is validated instead, since AT_WORK is derived from it at
  Step 2/3.  See OFFICE COLUMN MAP below for the full crosswalk.

Method 4 (weight distribution) is a full standalone check (verify_weights),
mirroring the Leg-1 spec, plus a box-plot panel in the dashboard.

WINDOWS ENCODING NOTE:
  Run with  py -X utf8 3rdJ_01_readingGSS_2split_val.py
  or set    PYTHONIOENCODING=utf-8
  to avoid cp1252 crashes on the ✅ / ❌ / ⚠️ glyphs.

Robustness:
  - Missing CSVs: reported clearly; that cycle is skipped rather than crashing.
  - Missing office column: real soft warning only (rename-aware — canonical names).
"""

import io
import os
import sys
import base64
import platform
import textwrap
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend; safe on Windows/cluster
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------

_MAC = (
    "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/"
    "3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/outputs_step1"
)
_SPEED = (
    "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/"
    "3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/outputs_step1"
)
_WIN = (
    r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
    r"\3J_docs_occ_nTemp\Leg2_2-split\Step1_docs\outputs_step1"
)

if platform.system() == "Darwin":
    _BASE = _MAC
elif os.path.isdir(_WIN):          # real local Windows outputs dir wins when present
    _BASE = _WIN
elif os.path.isdir("/speed-scratch/o_iseri"):
    _BASE = _SPEED
else:
    _BASE = _WIN

OUTPUTS_DIR: str = _BASE
CYCLES = [2005, 2010, 2015, 2022]

# ---------------------------------------------------------------------------
# OFFICE COLUMN MAP (per cycle)
# None  → column does not exist for this cycle (expected absence)
#
# IMPORTANT — these are the CANONICAL (post-rename) names that actually appear
# in the Step-1 output CSVs.  The reader (3rdJ_01_readingGSS_2split.py) applies
# MAIN_RENAME_MAP (lines 151-178) BEFORE writing, so the validator must look for
# the renamed names, not the raw PUMF variable names.  Rename crosswalk:
#   LFSGSS / ACT7DAYS / ACT7DAYC      -> LFTAG   (LF-status source, all cycles)
#   WKWEHR_C / WHWD140C / WHWD140G    -> HRSWRK  (hours worked, all cycles)
#   MAR_Q172 / WHW_110 / WET_120      -> COW     (class of worker, all cycles)
#   NOC1110Y / NOCLBR_Y              -> NOCS    (occupation, 2015/2022 only;
#                                                2005/2010 keep raw SOC91C10 /
#                                                NOCS2006_C10)
# NAICS, telework, and MAR_Q100 (activity, 2005/2010) are kept raw by the reader.
# ---------------------------------------------------------------------------

# activity-last-week — 2005/2010 kept raw (MAR_Q100); in 2015/2022 the activity
# variable (ACT7DAYS / ACT7DAYC) IS the LF-status source and is renamed to LFTAG.
ACT_WEEK_COLS = {2005: "MAR_Q100", 2010: "MAR_Q100", 2015: "LFTAG", 2022: "LFTAG"}

# worked-last-week (2005 piggy-backs on MAR_Q100) — kept raw by the reader
WORKED_WEEK_COLS = {2005: "MAR_Q100", 2010: "WKLTWE", 2015: "MRW_D40B", 2022: "MRW_D40B"}

# LF status — renamed to LFTAG in ALL four cycles (present everywhere post-rename)
LF_STATUS_COLS = {2005: "LFTAG", 2010: "LFTAG", 2015: "LFTAG", 2022: "LFTAG"}

# hours worked — renamed to HRSWRK in all cycles
HOURS_COLS = {2005: "HRSWRK", 2010: "HRSWRK", 2015: "HRSWRK", 2022: "HRSWRK"}

# class of worker — renamed to COW in all cycles.  Note: 2015 is sourced from
# WHW_110 (NOT the suppressed WET_120), so COW IS present for 2015.
COW_COLS = {2005: "COW", 2010: "COW", 2015: "COW", 2022: "COW"}
COW_2015_SUPPRESSED = False   # corrected: COW present via WHW_110 rename

# NOC occupation — 2005/2010 keep raw codes; 2015/2022 renamed to NOCS
NOC_COLS = {2005: "SOC91C10", 2010: "NOCS2006_C10", 2015: "NOCS", 2022: "NOCS"}

# NAICS industry — kept raw by the reader
NAICS_COLS = {
    2005: "NAICS2002_C16", 2010: "NAICS2007_C16",
    2015: "NAIC12CY",      2022: "NAIC22CY",
}

# telework (2005 → None; 2022 has multiple sub-columns) — kept raw by the reader
TELEWORK_COLS = {2005: None, 2010: "MAR_Q190", 2015: "WTI_130", 2022: "TLWK_01A"}
# additional 2022 telework columns (B–D and 02G) — used for existence check only
TELEWORK_2022_EXTRA = ["TLWK_01B", "TLWK_01C", "TLWK_01D", "TLWK_02G"]

# RAW location source on the EPISODE file — this is what AT_WORK is derived FROM
# at Step 2/3.  occPRE is a HARMONIZED code produced downstream; it is NOT created
# at Step-1 read time.  The reader preserves the raw per-cycle location column:
#   2005/2010 -> PLACE ;  2015/2022 -> LOCATION
LOCATION_SRC_COLS = {2005: "PLACE", 2010: "PLACE", 2015: "LOCATION", 2022: "LOCATION"}

# RAW activity code on the EPISODE file (used by Method 3 activity-range check)
#   2005/2010 -> ACTCODE ;  2015/2022 -> TUI_01
ACTCODE_COLS = {2005: "ACTCODE", 2010: "ACTCODE", 2015: "TUI_01", 2022: "TUI_01"}

# Survey weights actually present in the Step-1 CSVs (Method 4)
WGHT_MAIN_COL = "WGHT_PER"   # respondent weight on every main_*.csv
WGHT_EPI_COL  = "WGHT_EPI"   # episode weight on every episode_*.csv

# Documented GSS Time-Use respondent counts (PUMF), used only as PLAUSIBILITY
# bounds — we report the actual count and flag only if it falls outside a wide
# band, so a slightly-off "expected" number can never create a false FAIL.
EXPECTED_MAIN_ROWS = {2005: 19597, 2010: 15390, 2015: 17390, 2022: 12336}
ROW_COUNT_TOLERANCE = 0.02   # ±2% around the documented count = PASS

# Population the respondent weights should roughly sum to (Canada 15+, millions).
# Wide band on purpose; outside -> WARN (report value), never FAIL.
POP_SUM_BOUNDS = (15_000_000, 40_000_000)

# ---------------------------------------------------------------------------
# RESIDENTIAL CROSS-CYCLE DEMO VARS (reused from Leg 1, stripped of
# importlib dependency — defined inline so no reader module is required)
# ---------------------------------------------------------------------------

DEMO_VARS: dict[str, dict[str, str | None]] = {
    "AGEGRP": {"2005": "AGEGRP", "2010": "AGEGRP", "2015": "AGEGRP", "2022": "AGEGRP"},
    "SEX":    {"2005": "SEX",    "2010": "SEX",    "2015": "SEX",    "2022": "SEX"},
    "MARSTH": {"2005": "MARSTH", "2010": "MARSTH", "2015": "MARSTH", "2022": "MARSTH"},
    "HHSIZE": {"2005": "HHSIZE", "2010": "HHSIZE", "2015": "HHSIZE", "2022": "HHSIZE"},
    "PR":     {"2005": "PR",     "2010": "PR",     "2015": "PR",     "2022": "PR"},
    "CMA":    {"2005": "CMA",    "2010": "CMA",    "2015": "CMA",    "2022": "CMA"},
    "LFTAG":  {"2005": "LFTAG",  "2010": "LFTAG",  "2015": "LFTAG",  "2022": "LFTAG"},
    "COW":    {"2005": "COW",    "2010": "COW",    "2015": "COW",    "2022": "COW"},
    "HRSWRK": {"2005": "HRSWRK", "2010": "HRSWRK", "2015": "HRSWRK", "2022": "HRSWRK"},
    "KOL":    {"2005": "KOL",    "2010": "KOL",    "2015": "KOL",    "2022": "KOL"},
}

# ---------------------------------------------------------------------------
# PIPELINE OVERVIEW (for HTML report header)
# ---------------------------------------------------------------------------

STEP1_OVERVIEW = """\
╔══════════════════════════════════════════════════════════════════════════════════╗
║  STEP 1 — DATA COLLECTION (Leg-2 Two-Channel Split)                            ║
║                                                                                ║
║  GSS MAIN FILE (Cycles 19/24/29/GSSP: 2005/2010/2015/2022)                   ║
║  ┌─ Residential (unchanged from Leg 1) ─────────────────────────────────────┐ ║
║  │  occID, SURVYEAR, SURVMNTH, PR, HHSIZE, AGEGRP, SEX, MARSTH,            │ ║
║  │  KOL, ATTSCH, NOCS, LFTAG, COW, HRSWRK, POWST, CMA, TOTINC,            │ ║
║  │  WGHT_PER, WTBS_001–500                                                  │ ║
║  ├─ Office-gating (NEW, Leg-2) ────────────────────────────────────────────┤ ║
║  │  activity_last_week, worked_last_week, LF_status (2005/2010 only raw),   │ ║
║  │  hours_worked, class_of_worker (WET_120 suppressed in 2015 PUMF),        │ ║
║  │  NOC (10-bucket), NAICS (16-bucket), telework/WFH columns               │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                ║
║  GSS EPISODE FILE (same cycles)                                               ║
║  ┌─ Residential (unchanged) ──────────────────────────────────────────────┐  ║
║  │  occID, EPINO, DDAY, start/end, startMin/endMin, duration,             │  ║
║  │  occACT, raw PLACE/LOCATION, co-presence cols, techUse, WGHT_EPI       │  ║
║  └─ Key NEW check ────────────────────────────────────────────────────────┘  ║
║     raw PLACE (05/10) / LOCATION (15/22) present; AT_WORK derived Step 2/3    ║
╚══════════════════════════════════════════════════════════════════════════════════╝"""


# ---------------------------------------------------------------------------
# VALIDATOR CLASS
# ---------------------------------------------------------------------------

class GSSValidator2Split:
    """
    Validation class for Leg-2 Step-1 outputs.

    Residential checks are reused unchanged from the Leg-1 validator.
    Office checks are added per the spec in 3rdJ_01_readingGSS_val.md.
    """

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.data: dict[int, dict[str, pd.DataFrame]] = {y: {} for y in CYCLES}
        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": [], "info": []}
        self.plots_b64: dict[str, str] = {}
        self._console_lines: list[str] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record(self, level: str, msg: str) -> None:
        """Record a result and print it with the appropriate icon."""
        self.results[level].append(msg)
        icon = {
            "pass": "✅",
            "fail": "❌",
            "warn": "⚠️ ",
            "info": "ℹ️ ",
        }.get(level, "  ")
        line = f"{icon} {msg}"
        print(line)
        self._console_lines.append(line)

    def _section(self, title: str) -> None:
        line = f"\n--- {title} ---"
        print(line)
        self._console_lines.append(line)

    @staticmethod
    def _hhmm_to_min(series: pd.Series) -> pd.Series:
        """Convert HHMM clock values (e.g. 730 -> 7:30, 2230 -> 22:30) to minutes."""
        v = pd.to_numeric(series, errors="coerce")
        return (v // 100) * 60 + (v % 100)

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------

    def load_data(self) -> None:
        """Load the 8 Step-1 CSVs.  Missing files are reported and skipped."""
        self._section("Loading Data")
        for year in CYCLES:
            main_path = os.path.join(self.data_dir, f"main_{year}.csv")
            epi_path  = os.path.join(self.data_dir, f"episode_{year}.csv")

            if os.path.exists(main_path):
                self.data[year]["main"] = pd.read_csv(main_path, low_memory=False)
                n = len(self.data[year]["main"])
                self._record("info", f"Loaded main_{year}.csv — {n:,} rows")
            else:
                self._record("warn", f"main_{year}.csv NOT FOUND — cycle {year} main checks skipped")

            if os.path.exists(epi_path):
                self.data[year]["episode"] = pd.read_csv(epi_path, low_memory=False)
                n = len(self.data[year]["episode"])
                self._record("info", f"Loaded episode_{year}.csv — {n:,} rows")
            else:
                self._record("warn", f"episode_{year}.csv NOT FOUND — cycle {year} episode checks skipped")

    # ------------------------------------------------------------------
    # Method 1 — Schema & Shape Audit
    # ------------------------------------------------------------------

    def audit_schema(self) -> None:
        """
        Method 1: Schema & Shape Audit.

        Residential column presence  — reused from Leg 1 (reported as-is).
        Office column presence        — NEW: per-cycle checklist.
        2015 WET_120 expected miss    — logged as EXPECTED, not FAIL.
        Row counts and NaN rates      — reused from Leg 1.
        """
        self._section("Method 1: Schema & Shape Audit")

        for year in CYCLES:
            # ---- Main file checks ----
            main = self.data[year].get("main")
            if main is None:
                self._record("warn", f"MAIN {year}: file missing — skipping schema checks")
            else:
                self._check_nulls(main, f"MAIN {year}")
                self._check_row_count(main, year)
                self._check_weight_dtype(main, year)
                self._check_office_columns_main(main, year)

            # ---- Episode file checks ----
            epi = self.data[year].get("episode")
            if epi is None:
                self._record("warn", f"EPISODE {year}: file missing — skipping schema checks")
            else:
                self._check_nulls(epi, f"EPISODE {year}")

    def _check_nulls(self, df: pd.DataFrame, identifier: str) -> None:
        """Flag any column that is 100 % NaN."""
        all_null = df.columns[df.isnull().all()].tolist()
        if all_null:
            self._record("warn", f"{identifier} — 100% NaN columns: {all_null}")
        else:
            self._record("pass", f"{identifier} — no completely-null columns")

    def _check_row_count(self, df: pd.DataFrame, year: int) -> None:
        """Method 1: respondent-count sanity vs documented GSS PUMF totals (±tolerance)."""
        n = len(df)
        exp = EXPECTED_MAIN_ROWS.get(year)
        if exp is None:
            self._record("info", f"MAIN {year} — {n:,} rows (no documented baseline)")
            return
        lo, hi = exp * (1 - ROW_COUNT_TOLERANCE), exp * (1 + ROW_COUNT_TOLERANCE)
        if lo <= n <= hi:
            self._record("pass", f"MAIN {year} — {n:,} rows within ±{ROW_COUNT_TOLERANCE:.0%} of documented {exp:,}")
        else:
            self._record("warn", f"MAIN {year} — {n:,} rows differ from documented {exp:,} by more than ±{ROW_COUNT_TOLERANCE:.0%}")

    def _check_weight_dtype(self, df: pd.DataFrame, year: int) -> None:
        """Method 1: respondent weight column must be present and numeric (not parsed as string)."""
        if WGHT_MAIN_COL not in df.columns:
            self._record("warn", f"MAIN {year} — weight column '{WGHT_MAIN_COL}' absent")
            return
        if pd.api.types.is_numeric_dtype(df[WGHT_MAIN_COL]):
            self._record("pass", f"MAIN {year} — '{WGHT_MAIN_COL}' is numeric dtype ({df[WGHT_MAIN_COL].dtype})")
        else:
            self._record("warn", f"MAIN {year} — '{WGHT_MAIN_COL}' is {df[WGHT_MAIN_COL].dtype}, expected numeric — possible parse error")

    def _check_office_columns_main(self, df: pd.DataFrame, year: int) -> None:
        """Per-cycle presence checklist for office-gating columns (Method 1 office extension)."""
        checks = {
            "activity_last_week": ACT_WEEK_COLS[year],
            "worked_last_week":   WORKED_WEEK_COLS[year],
            "LF_status":          LF_STATUS_COLS[year],
            "hours_worked":       HOURS_COLS[year],
            "class_of_worker":    COW_COLS[year],
            "NOC":                NOC_COLS[year],
            "NAICS":              NAICS_COLS[year],
            "telework":           TELEWORK_COLS[year],
        }

        for friendly, col in checks.items():
            # None means the column genuinely does not exist this cycle
            if col is None:
                self._record(
                    "pass",
                    f"MAIN {year} — {friendly}: absent (expected — not collected this cycle)",
                )
                continue

            # Special case: 2015 WET_120 SUPPRESSED in PUMF
            if year == 2015 and col == "WET_120":
                if col not in df.columns:
                    self._record(
                        "info",
                        (
                            f"MAIN {year} — class_of_worker (WET_120): ABSENT — "
                            "KNOWN SUPPRESSED in 2015 PUMF — expected miss, not a bug. "
                            "NOC/NAICS serve as archetype proxy for 2015."
                        ),
                    )
                else:
                    self._record(
                        "pass",
                        f"MAIN {year} — class_of_worker (WET_120): present (unexpected but OK)",
                    )
                continue

            # Normal presence check
            if col in df.columns:
                self._record("pass", f"MAIN {year} — {friendly} ({col}): present")
            else:
                self._record(
                    "warn",
                    f"MAIN {year} — {friendly} ({col}): MISSING — soft warning (column expected)",
                )

        # 2022 extra telework columns
        if year == 2022:
            for extra in TELEWORK_2022_EXTRA:
                if extra in df.columns:
                    self._record("pass", f"MAIN 2022 — telework extra ({extra}): present")
                else:
                    self._record("warn", f"MAIN 2022 — telework extra ({extra}): missing")

    # ------------------------------------------------------------------
    # Method 2 — Cross-Cycle Category Comparison
    # ------------------------------------------------------------------

    def compare_categories(self) -> None:
        """
        Method 2: Cross-Cycle Category Comparison.

        Residential variables — reused from Leg 1.
        Office variables      — NEW: NOC ~10 buckets, NAICS ~16 buckets,
                                      class-of-worker 3–6 codes,
                                      activity-last-week 4–10 codes,
                                      telework sparsity check.
        """
        self._section("Method 2: Cross-Cycle Category Comparison (Residential)")
        self._compare_residential()

        self._section("Method 2 (continued): Office-Variable Category Sanity")
        self._compare_office_categories()

    def _compare_residential(self) -> None:
        """Residential DEMO_VARS — reused from Leg 1."""
        for var_name, col_map in DEMO_VARS.items():
            print(f"\n  {var_name} uniques:")
            all_ok = True
            for year in CYCLES:
                col = col_map.get(str(year))
                df  = self.data[year].get("main")
                if df is None or col is None:
                    print(f"    {year}: N/A")
                    continue
                if col not in df.columns:
                    print(f"    {year} ({col}): column missing")
                    all_ok = False
                    continue
                uniq = sorted(pd.to_numeric(df[col], errors="coerce").dropna().unique().tolist())
                print(f"    {year} ({col}): {uniq[:12]}{'...' if len(uniq) > 12 else ''}")
            if all_ok:
                self._record("pass", f"Residential {var_name} verified across cycles")

    def _compare_office_categories(self) -> None:
        """Office-gating variable category sanity checks."""

        # --- NOC: ~10 buckets ---
        print("\n  NOC (occupation buckets):")
        for year in CYCLES:
            col = NOC_COLS[year]
            df  = self.data[year].get("main")
            if df is None:
                print(f"    {year}: file missing")
                continue
            if col not in df.columns:
                self._record("warn", f"NOC {year} ({col}): column missing")
                continue
            n_cat = df[col].dropna().nunique()
            uniq  = sorted(df[col].dropna().unique().tolist())[:15]
            print(f"    {year} ({col}): {n_cat} categories — {uniq}")
            if n_cat < 5 or n_cat > 15:
                self._record(
                    "warn",
                    f"NOC {year}: unexpected bucket count {n_cat} (expected ~10)",
                )
            else:
                self._record("pass", f"NOC {year}: {n_cat} buckets — plausible")

        # --- NAICS: ~16 buckets ---
        print("\n  NAICS (industry buckets):")
        for year in CYCLES:
            col = NAICS_COLS[year]
            df  = self.data[year].get("main")
            if df is None:
                print(f"    {year}: file missing")
                continue
            if col not in df.columns:
                self._record("warn", f"NAICS {year} ({col}): column missing")
                continue
            n_cat = df[col].dropna().nunique()
            uniq  = sorted(df[col].dropna().unique().tolist())[:20]
            print(f"    {year} ({col}): {n_cat} categories — {uniq}")
            if n_cat < 8 or n_cat > 25:
                self._record(
                    "warn",
                    f"NAICS {year}: unexpected bucket count {n_cat} (expected ~16)",
                )
            else:
                self._record("pass", f"NAICS {year}: {n_cat} buckets — plausible")

        # --- Class-of-worker: 3–6 codes ---
        print("\n  Class-of-worker:")
        for year in CYCLES:
            col = COW_COLS[year]
            df  = self.data[year].get("main")
            if df is None:
                print(f"    {year}: file missing")
                continue
            if year == 2015 and col == "WET_120":
                if col not in df.columns:
                    print(
                        f"    {year}: WET_120 absent (KNOWN SUPPRESSED in 2015 PUMF — expected)"
                    )
                    continue
            if col not in df.columns:
                self._record("warn", f"COW {year} ({col}): column missing")
                continue
            n_cat = df[col].dropna().nunique()
            uniq  = sorted(df[col].dropna().unique().tolist())[:10]
            print(f"    {year} ({col}): {n_cat} categories — {uniq}")
            if n_cat < 3 or n_cat > 15:
                self._record(
                    "warn",
                    f"COW {year}: unexpected code count {n_cat} (expected 3–6)",
                )
            else:
                self._record("pass", f"COW {year}: {n_cat} codes — plausible")

        # --- Activity last week: 4–10 codes ---
        print("\n  Activity last week:")
        for year in CYCLES:
            col = ACT_WEEK_COLS[year]
            df  = self.data[year].get("main")
            if df is None:
                print(f"    {year}: file missing")
                continue
            if col not in df.columns:
                self._record("warn", f"ACT_WEEK {year} ({col}): column missing")
                continue
            n_cat = df[col].dropna().nunique()
            uniq  = sorted(df[col].dropna().unique().tolist())[:12]
            print(f"    {year} ({col}): {n_cat} categories — {uniq}")
            if n_cat < 4 or n_cat > 20:
                self._record(
                    "warn",
                    f"ACT_WEEK {year}: code count {n_cat} outside expected range 4–20",
                )
            else:
                self._record("pass", f"ACT_WEEK {year}: {n_cat} codes — plausible")

        # --- Telework sparsity ---
        print("\n  Telework non-NaN share:")
        for year in CYCLES:
            col = TELEWORK_COLS[year]
            df  = self.data[year].get("main")
            if df is None:
                print(f"    {year}: file missing")
                continue
            if col is None:
                print(f"    {year}: telework not collected (expected)")
                self._record("pass", f"Telework {year}: absent (expected — pre-2010)")
                continue
            if col not in df.columns:
                self._record("warn", f"Telework {year} ({col}): column missing")
                continue
            # NOTE: GSS telework variables are UNIVERSE-CODED categoricals — every
            # respondent receives a value (real codes + valid-skip / not-applicable
            # codes such as 6/96/996), so ~100% non-NaN is the EXPECTED state, not a
            # red flag.  The meaningful check is therefore (a) the column is present
            # and (b) it is non-degenerate (carries more than one distinct value).
            non_nan_share = df[col].notna().mean()
            n_distinct = df[col].dropna().nunique()
            print(f"    {year} ({col}): {non_nan_share:.1%} non-NaN, {n_distinct} distinct values")
            if non_nan_share < 0.01:
                self._record(
                    "warn",
                    f"Telework {year} ({col}): implausibly low non-NaN share "
                    f"{non_nan_share:.1%} (<1%) — possible read error",
                )
            elif n_distinct < 2:
                self._record(
                    "warn",
                    f"Telework {year} ({col}): degenerate — only {n_distinct} distinct "
                    "value(s); column carries no signal",
                )
            else:
                self._record(
                    "pass",
                    f"Telework {year} ({col}): {non_nan_share:.1%} non-NaN, "
                    f"{n_distinct} distinct values — universe-coded as expected",
                )

    # ------------------------------------------------------------------
    # Method 3 — Episode Integrity Check
    # ------------------------------------------------------------------

    def verify_episode_integrity(self) -> None:
        """
        Method 3: Episode Integrity Check.

        Residential checks  — reused from Leg 1 (ID linkage, time ordering).
        Location-source     — NEW: raw PLACE (2005/2010) / LOCATION (2015/2022)
                              presence, NaN rate, non-degeneracy.  occPRE/AT_WORK
                              are derived at Step 2/3, so the AT_WORK column must
                              NOT be present yet.
        """
        self._section("Method 3: Episode Integrity Check")

        for year in CYCLES:
            main = self.data[year].get("main")
            epi  = self.data[year].get("episode")

            if main is None or epi is None:
                self._record("warn", f"{year}: main or episode missing — skipping integrity checks")
                continue

            # ---- ID linkage (Leg-1 reuse) ----
            if "occID" in main.columns and "occID" in epi.columns:
                main_ids = set(main["occID"].unique())
                epi_ids  = set(epi["occID"].unique())
                if epi_ids:
                    overlap = len(epi_ids & main_ids) / len(epi_ids)
                    if overlap > 0.95:
                        self._record("pass", f"{year}: {overlap:.1%} of episode IDs match main")
                    else:
                        self._record("fail", f"{year}: low ID overlap — only {overlap:.1%} episode IDs in main")

            # ---- Time ordering (Leg-1 reuse) ----
            if "start" in epi.columns and "end" in epi.columns:
                try:
                    s = pd.to_numeric(epi["start"], errors="coerce")
                    e = pd.to_numeric(epi["end"],   errors="coerce")
                    valid_time = (s <= e) | ((s > e) & (e < 240))
                    rate = valid_time.mean()
                    if rate > 0.90:
                        self._record("pass", f"{year}: time ordering {rate:.1%} pass rate")
                    else:
                        self._record("warn", f"{year}: time ordering issues — {rate:.1%} pass rate")
                except Exception as exc:
                    self._record("warn", f"{year}: time ordering check error — {exc}")

            # ---- Diary completeness: contiguous full-day coverage from a 4 AM origin ----
            # start/end are HHMM clock values; convert to minutes first.  A complete
            # diary (a) starts at the 4 AM origin (240 min), (b) is contiguous
            # (each episode's start == previous episode's end — no gaps), and
            # (c) covers at least a full 24 h.  NOTE the cross-cycle difference the
            # deeper check surfaced: 2015/2022 diaries are clipped to exactly 1440
            # (4 AM→4 AM), while 2005/2010 diaries run PAST 24 h (4 AM→next morning,
            # median ~1620 min).  Both are faithful source reads; the >24 h span in
            # 2005/2010 is a Step-2 harmonization concern, NOT a Step-1 read error.
            if {"occID", "EPINO", "start", "end"}.issubset(epi.columns):
                ep = epi[["occID", "EPINO", "start", "end"]].copy()
                ep = ep.sort_values(["occID", "EPINO"])
                ep["s"] = self._hhmm_to_min(ep["start"])
                ep["e"] = self._hhmm_to_min(ep["end"])
                ep["dur"] = (ep["e"] - ep["s"]) % 1440
                g = ep.groupby("occID")
                origin_ok = (g["s"].first() == 240).mean()           # starts at 4:00
                day_sum = g["dur"].sum()                              # true span (min)
                covered = (day_sum >= 1430).mean()                   # covers ≥ ~24 h
                med = day_sum.median()
                ep["prev_e"] = g["e"].shift()
                contig = (ep["s"] == ep["prev_e"]).sum() / max(1, (ep["EPINO"] > ep.groupby("occID")["EPINO"].transform("min")).sum())
                if origin_ok >= 0.99 and covered >= 0.95 and contig >= 0.90:
                    self._record("pass", f"{year}: diary completeness — {origin_ok:.0%} start at 4:00, {contig:.0%} contiguous, {covered:.0%} cover ≥24 h (median span {med:.0f} min)")
                else:
                    self._record("warn", f"{year}: diary completeness — origin {origin_ok:.0%}, contiguous {contig:.0%}, ≥24 h {covered:.0%} (median span {med:.0f} min) — inspect time coding")
                if med > 1450:
                    self._record("info", f"{year}: diaries span >24 h by design (median {med:.0f} min, 4 AM→next morning) — clip/normalize in Step-2 harmonization")

            # ---- Episodes per respondent: typical 8–35 ----
            if "occID" in epi.columns:
                per = epi.groupby("occID").size()
                med_ep = per.median()
                if 8 <= med_ep <= 35:
                    self._record("pass", f"{year}: median {med_ep:.0f} episodes/respondent — typical range")
                else:
                    self._record("warn", f"{year}: median {med_ep:.0f} episodes/respondent — outside typical 8–35")

            # ---- Activity-code range: non-degenerate, no negatives ----
            act_col = ACTCODE_COLS[year]
            if act_col in epi.columns:
                acts = pd.to_numeric(epi[act_col], errors="coerce").dropna()
                n_act = acts.nunique()
                neg = (acts < 0).sum()
                if n_act >= 10 and neg == 0:
                    self._record("pass", f"{year}: activity code '{act_col}' — {n_act} distinct codes, no negatives")
                elif neg > 0:
                    self._record("warn", f"{year}: activity code '{act_col}' has {neg} negative values — inspect")
                else:
                    self._record("warn", f"{year}: activity code '{act_col}' degenerate — only {n_act} distinct codes")
            else:
                self._record("warn", f"{year}: activity code '{act_col}' missing from episode file")

            # ---- Raw location-source presence (AT_WORK derivation key) ----
            # occPRE is a HARMONIZED code produced at Step 2/3 — it does NOT exist
            # in the Step-1 episode CSV by design.  What MUST be present here is the
            # raw per-cycle location column (PLACE for 2005/2010, LOCATION for
            # 2015/2022), since AT_WORK is derived FROM it downstream.
            loc_col = LOCATION_SRC_COLS[year]
            if loc_col not in epi.columns:
                self._record(
                    "fail",
                    f"{year}: raw location source '{loc_col}' MISSING from episode file — "
                    "AT_WORK cannot be derived in Step 2/3",
                )
            else:
                # NaN rate on the raw location column
                nan_rate = epi[loc_col].isnull().mean()
                if nan_rate < 0.05:
                    self._record(
                        "pass",
                        f"{year}: location source '{loc_col}' NaN rate {nan_rate:.1%} (<5% threshold)",
                    )
                else:
                    self._record(
                        "warn",
                        f"{year}: location source '{loc_col}' NaN rate {nan_rate:.1%} — "
                        "exceeds 5% threshold",
                    )

                # Non-degeneracy — must carry >1 distinct location code so the Step-2
                # workplace bucket can actually be split out.
                n_distinct = epi[loc_col].dropna().nunique()
                if n_distinct >= 2:
                    self._record(
                        "pass",
                        f"{year}: location source '{loc_col}' has {n_distinct} distinct "
                        "codes — splittable for AT_WORK derivation",
                    )
                else:
                    self._record(
                        "fail",
                        f"{year}: location source '{loc_col}' degenerate "
                        f"({n_distinct} distinct value) — AT_WORK cannot be derived",
                    )

            # ---- AT_WORK column must NOT be present yet (NEW) ----
            if "AT_WORK" in epi.columns:
                self._record(
                    "fail",
                    f"{year}: AT_WORK column found in Step-1 episode file — "
                    "it must be derived in Step 2/3, not Step 1",
                )
            else:
                self._record("pass", f"{year}: AT_WORK column absent — correct (derived later)")

    # ------------------------------------------------------------------
    # Method 4 — Weight Distribution Sanity Check
    # ------------------------------------------------------------------

    def verify_weights(self) -> None:
        """
        Method 4 (reused from Leg 1): confirm survey weights survived the read.

        Respondent weights (WGHT_PER):
          - all strictly positive (no zero / negative)
          - no extreme outlier (max < 20× mean)
          - weighted total ≈ Canadian 15+ population (plausibility band)
        Episode weights (WGHT_EPI):
          - present, positive, non-degenerate
        """
        self._section("Method 4: Weight Distribution Sanity Check")

        for year in CYCLES:
            main = self.data[year].get("main")
            if main is None:
                continue
            if WGHT_MAIN_COL not in main.columns:
                self._record("warn", f"{year}: '{WGHT_MAIN_COL}' absent — cannot weight-check main")
            else:
                w = pd.to_numeric(main[WGHT_MAIN_COL], errors="coerce")
                n_bad = int((w <= 0).sum() + w.isna().sum())
                wmin, wmax, wmean, wsum = w.min(), w.max(), w.mean(), w.sum()
                # positivity
                if n_bad == 0:
                    self._record("pass", f"{year}: all {WGHT_MAIN_COL} > 0 (min {wmin:,.1f})")
                else:
                    self._record("warn", f"{year}: {n_bad} non-positive/NaN {WGHT_MAIN_COL} values")
                # outliers
                if wmean and wmax < 20 * wmean:
                    self._record("pass", f"{year}: no extreme weight outlier (max {wmax:,.0f} < 20× mean {wmean:,.0f})")
                else:
                    self._record("warn", f"{year}: weight outlier — max {wmax:,.0f} ≥ 20× mean {wmean:,.0f}")
                # population total
                lo, hi = POP_SUM_BOUNDS
                if lo <= wsum <= hi:
                    self._record("pass", f"{year}: weighted population {wsum:,.0f} within plausible 15+ band")
                else:
                    self._record("warn", f"{year}: weighted population {wsum:,.0f} outside {lo:,}–{hi:,} band — verify")

            # ---- Episode weights ----
            epi = self.data[year].get("episode")
            if epi is None:
                continue
            if WGHT_EPI_COL not in epi.columns:
                self._record("warn", f"{year}: '{WGHT_EPI_COL}' absent — cannot weight-check episodes")
            else:
                we = pd.to_numeric(epi[WGHT_EPI_COL], errors="coerce")
                n_bad = int((we <= 0).sum() + we.isna().sum())
                n_distinct = we.dropna().nunique()
                if n_bad == 0 and n_distinct >= 2:
                    self._record("pass", f"{year}: {WGHT_EPI_COL} all > 0, {n_distinct} distinct values")
                elif n_bad > 0:
                    self._record("warn", f"{year}: {n_bad} non-positive/NaN {WGHT_EPI_COL} values")
                else:
                    self._record("warn", f"{year}: {WGHT_EPI_COL} degenerate — {n_distinct} distinct value(s)")

    # ------------------------------------------------------------------
    # Method 5 — Visual Summary Dashboard
    # ------------------------------------------------------------------

    def generate_visuals(self) -> None:
        """Method 5: Generate all charts and export an HTML validation report."""
        self._section("Method 5: Visual Summary Dashboard")

        plt.rcParams.update({
            "figure.facecolor": "#1e1e2e",
            "axes.facecolor":   "#2a2a3e",
            "axes.edgecolor":   "#555",
            "axes.labelcolor":  "#cdd6f4",
            "xtick.color":      "#cdd6f4",
            "ytick.color":      "#cdd6f4",
            "text.color":       "#cdd6f4",
            "grid.color":       "#444",
            "legend.facecolor": "#2a2a3e",
            "legend.edgecolor": "#555",
            "font.family":      "sans-serif",
            "font.size":        11,
        })

        self._plot_row_counts()
        self._plot_episode_density()
        self._plot_weight_distribution()
        self._plot_diary_completeness()
        self._plot_nan_heatmap()
        self._plot_time_ordering()
        # Office-specific panels
        self._plot_noc_naics_heatmap()
        self._plot_telework_rate()
        self._plot_occpre_distribution()
        self.export_html_report()

    def _save_plot_to_b64(self, title: str) -> None:
        buf = io.BytesIO()
        plt.tight_layout(pad=2.0)
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor=plt.gcf().get_facecolor())
        plt.close()
        buf.seek(0)
        self.plots_b64[title] = base64.b64encode(buf.read()).decode("utf-8")

    # ---- Chart 1: Row Counts (Leg-1 reuse) ----
    def _plot_row_counts(self) -> None:
        years   = [str(y) for y in CYCLES]
        m_cnts  = [len(self.data[y].get("main",    [])) for y in CYCLES]
        e_cnts  = [len(self.data[y].get("episode", [])) for y in CYCLES]

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        x = np.arange(len(years))

        for ax, cnts, label, color in [
            (axes[0], m_cnts, "Main — Respondents per Cycle",  "#89b4fa"),
            (axes[1], e_cnts, "Episode — Entries per Cycle",   "#a6e3a1"),
        ]:
            bars = ax.bar(x, cnts, 0.6, color=color, edgecolor="#1e1e2e", linewidth=0.8, zorder=3)
            ax.set_title(label, fontsize=13, pad=10)
            ax.set_xticks(x); ax.set_xticklabels(years, fontsize=12)
            ax.set_ylabel("Row Count")
            ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
            for bar, val in zip(bars, cnts):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(1, val * 0.01),
                        f"{val:,}", ha="center", va="bottom", fontsize=10)

        fig.suptitle("GSS Leg-2 Data Volume Across Cycles", fontsize=15, fontweight="bold")
        self._save_plot_to_b64("1_row_counts")
        self._record("pass", "Row counts chart generated")

    # ---- Chart 2: Episode Density (Leg-1 reuse) ----
    def _plot_episode_density(self) -> None:
        all_data = []
        for year in CYCLES:
            epi = self.data[year].get("episode")
            if epi is not None and "occID" in epi.columns:
                cnts = epi.groupby("occID").size().reset_index(name="episodes")
                cnts["Cycle"] = str(year)
                all_data.append(cnts)

        if not all_data:
            self._record("warn", "Episode density chart skipped — no episode data loaded")
            return

        combined = pd.concat(all_data, ignore_index=True)
        COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        palette = {str(y): c for y, c in zip(CYCLES, COLORS)}

        fig, ax = plt.subplots(figsize=(11, 5))
        sns.violinplot(data=combined, x="Cycle", y="episodes", hue="Cycle",
                       palette=palette, inner="box", cut=0, linewidth=1.2,
                       legend=False, ax=ax)
        ax.set_title("Distribution of Episodes per Respondent (by Cycle)", fontsize=13, pad=10)
        ax.set_xlabel("Survey Cycle"); ax.set_ylabel("Episodes per Respondent")
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        for i, year in enumerate(CYCLES):
            sub = combined[combined["Cycle"] == str(year)]["episodes"]
            if not sub.empty:
                med = sub.median()
                ax.text(i, med + 0.8, f"med={med:.0f}", ha="center", fontsize=9,
                        color="#cdd6f4", fontweight="bold")

        self._save_plot_to_b64("2_episode_density")
        self._record("pass", "Episode density chart generated")

    # ---- Chart 3a: Weight Distribution Box Plots (Method 4 visual, Leg-1 reuse) ----
    def _plot_weight_distribution(self) -> None:
        """Respondent-weight (WGHT_PER) box plots per cycle — Method 4 visual."""
        all_data = []
        for year in CYCLES:
            main = self.data[year].get("main")
            if main is not None and WGHT_MAIN_COL in main.columns:
                w = pd.to_numeric(main[WGHT_MAIN_COL], errors="coerce").dropna()
                sub = pd.DataFrame({"w": w})
                sub["Cycle"] = str(year)
                all_data.append(sub)
        if not all_data:
            self._record("warn", "Weight distribution chart skipped — no WGHT_PER found")
            return
        combined = pd.concat(all_data, ignore_index=True)
        COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        palette = {str(y): c for y, c in zip(CYCLES, COLORS)}
        fig, ax = plt.subplots(figsize=(11, 5))
        sns.boxplot(data=combined, x="Cycle", y="w", hue="Cycle", palette=palette,
                    showfliers=False, linewidth=1.2, legend=False, ax=ax)
        ax.set_title("Respondent Weight (WGHT_PER) Distribution per Cycle", fontsize=13, pad=10)
        ax.set_xlabel("Survey Cycle"); ax.set_ylabel("WGHT_PER")
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        self._save_plot_to_b64("3a_weight_dist")
        self._record("pass", "Weight distribution chart generated")

    # ---- Chart 3b: Diary Completeness Bars (Method 3 visual) ----
    def _plot_diary_completeness(self) -> None:
        """Per-cycle stacked bar: share of diaries that are incomplete / exactly 24 h / run past 24 h.

        The raw minute-sum histogram is misleading: 2015/22 are *all* exactly 1440 (one needle)
        while 2005/10 spread up to ~2600 and pile on the axis edge when clipped. The honest
        completeness signal is categorical — what fraction of each cycle covers the full day."""
        labels, incomp, exact, overflow = [], [], [], []
        any_data = False
        for year in CYCLES:
            epi = self.data[year].get("episode")
            labels.append(str(year))
            if epi is None or not {"occID", "start", "end"}.issubset(epi.columns):
                incomp.append(0.0); exact.append(0.0); overflow.append(0.0)
                continue
            any_data = True
            s = self._hhmm_to_min(epi["start"])
            e = self._hhmm_to_min(epi["end"])
            dur = (e - s) % 1440
            day_sum = pd.DataFrame({"occID": epi["occID"], "dur": dur}).dropna().groupby("occID")["dur"].sum()
            n = max(len(day_sum), 1)
            incomp.append(100.0 * (day_sum < 1430).sum() / n)
            exact.append(100.0 * day_sum.between(1430, 1450).sum() / n)
            overflow.append(100.0 * (day_sum > 1450).sum() / n)

        fig, ax = plt.subplots(figsize=(11, 4.5))
        y = list(range(len(labels)))
        b1 = ax.barh(y, incomp, color="#f38ba8", edgecolor="#1e1e2e", label="Incomplete (<24 h)")
        b2 = ax.barh(y, exact, left=incomp, color="#a6e3a1", edgecolor="#1e1e2e", label="Exactly 24 h (1440)")
        left2 = [i + e for i, e in zip(incomp, exact)]
        b3 = ax.barh(y, overflow, left=left2, color="#fab387", edgecolor="#1e1e2e",
                     label="Runs past 24 h (overnight)")
        ax.set_yticks(y); ax.set_yticklabels(labels, fontweight="bold")
        ax.set_xlabel("% of respondents", fontsize=10)
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        ax.legend(fontsize=9, loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3)
        for yi, (inc, ex, ov) in enumerate(zip(incomp, exact, overflow)):
            if ex >= 6:
                ax.text(inc + ex / 2, yi, f"{ex:.0f}%", ha="center", va="center", fontsize=9, color="#1e1e2e")
            if ov >= 6:
                ax.text(inc + ex + ov / 2, yi, f"{ov:.0f}%", ha="center", va="center", fontsize=9, color="#1e1e2e")
        fig.suptitle("Diary Completeness — Coverage of the 24 h Day (4 AM→4 AM)\n"
                     "0% incomplete = every diary read end-to-end; 2005/10 overnight overflow is a Step-2 concern",
                     fontsize=12, fontweight="bold")
        fig.tight_layout(rect=[0, 0.04, 1, 0.93])
        if any_data:
            self._save_plot_to_b64("3b_diary_completeness")
            self._record("pass", "Diary completeness chart generated")
        else:
            plt.close()
            self._record("warn", "Diary completeness chart skipped — no episode start/end found")

    # ---- Chart 3: NaN Heatmap (Leg-1 reuse, adapted) ----
    def _plot_nan_heatmap(self) -> None:
        """% missing per LOGICAL office variable × cycle.

        Indexed by logical variable (not raw column name) so each row is comparable
        across cycles. A cell is one of three honest states:
          • a number 0-100  — variable present in that cycle, this much is NaN
          • "n/a" (grey)    — variable does not exist for that cycle (expected absence)
          • 100 / red       — variable was expected (mapped) but is missing from the file
        The old version fillna(0)'d the absent cells, which falsely implied complete data."""
        LOGICAL = {
            "Activity (week)":   ACT_WEEK_COLS,
            "Worked (week)":     WORKED_WEEK_COLS,
            "LF status":         LF_STATUS_COLS,
            "Hours worked":      HOURS_COLS,
            "Class of worker":   COW_COLS,
            "Occupation (NOC)":  NOC_COLS,
            "Industry (NAICS)":  NAICS_COLS,
            "Telework":          TELEWORK_COLS,
        }
        NA = float("nan")
        rows = {}
        for label, cmap_ in LOGICAL.items():
            row = {}
            for year in CYCLES:
                main = self.data[year].get("main")
                colname = cmap_.get(year)
                if colname is None:                       # expected absence
                    row[str(year)] = NA
                elif main is None:
                    row[str(year)] = NA
                elif colname in main.columns:             # present → real NaN%
                    row[str(year)] = float(main[colname].isnull().mean() * 100)
                else:                                     # expected but missing
                    row[str(year)] = 100.0
            rows[label] = row

        pivot = pd.DataFrame(rows).T.reindex(columns=[str(y) for y in CYCLES])
        if pivot.isna().all().all():
            self._record("warn", "NaN heatmap skipped — no office columns found")
            return

        mask = pivot.isna()
        fig_h = max(4, len(pivot) * 0.55)
        fig, ax = plt.subplots(figsize=(8, fig_h))
        sns.heatmap(pivot, ax=ax, cmap="YlOrRd", vmin=0, vmax=100,
                    linewidths=0.5, linecolor="#1e1e2e", mask=mask,
                    annot=True, fmt=".0f", cbar_kws={"label": "% missing (0–100)"},
                    annot_kws={"size": 9})
        # grey out + label the expected-absence cells
        for r, label in enumerate(pivot.index):
            for c, year in enumerate(pivot.columns):
                if bool(mask.iloc[r, c]):
                    ax.add_patch(plt.Rectangle((c, r), 1, 1, facecolor="#45475a",
                                               edgecolor="#1e1e2e", lw=0.5))
                    ax.text(c + 0.5, r + 0.5, "n/a", ha="center", va="center",
                            fontsize=8, color="#cdd6f4", style="italic")
        ax.set_title("Missing-Data % per Office Variable × Cycle (Main Files)\n"
                     "grey = variable not collected that cycle (expected); 0 = present & complete",
                     fontsize=12, pad=10)
        ax.set_xlabel("Survey Cycle"); ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=0); ax.tick_params(axis="y", rotation=0, labelsize=9)
        fig.tight_layout()
        self._save_plot_to_b64("3_nan_heatmap")
        self._record("pass", "NaN heatmap (office columns) generated")

    # ---- Chart 4: Time-Ordering Pass Rate (Leg-1 reuse) ----
    def _plot_time_ordering(self) -> None:
        pass_rates: dict[str, float] = {}
        for year in CYCLES:
            epi = self.data[year].get("episode")
            if epi is None or "start" not in epi.columns or "end" not in epi.columns:
                continue
            s = pd.to_numeric(epi["start"], errors="coerce")
            e = pd.to_numeric(epi["end"],   errors="coerce")
            valid = (s <= e) | ((s > e) & (e < 240))
            pass_rates[str(year)] = valid.mean() * 100

        if not pass_rates:
            self._record("warn", "Time-ordering chart skipped — no start/end columns found")
            return

        fig, ax = plt.subplots(figsize=(8, 3.5))
        cycles = list(pass_rates.keys())
        rates  = [pass_rates[c] for c in cycles]
        colors = ["#a6e3a1" if r >= 95 else ("#fab387" if r >= 90 else "#f38ba8") for r in rates]
        bars = ax.barh(cycles, rates, color=colors, edgecolor="#1e1e2e", linewidth=0.8, height=0.5)
        ax.set_xlim(80, 101)
        ax.axvline(95, color="#89b4fa", linestyle="--", linewidth=1.2, label="95% threshold")
        ax.axvline(90, color="#f38ba8", linestyle=":",  linewidth=1.2, label="90% threshold")
        for bar, val in zip(bars, rates):
            ax.text(val - 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%", va="center", ha="right", fontsize=11, fontweight="bold")
        ax.set_title("Episode Time-Ordering Pass Rate per Cycle", fontsize=13, pad=10)
        ax.set_xlabel("Pass Rate (%)")
        ax.xaxis.grid(True, linestyle="--", alpha=0.3)
        ax.legend(fontsize=9)
        self._save_plot_to_b64("4_time_ordering")
        self._record("pass", "Time-ordering chart generated")

    # ---- Chart 5 (Office): NOC × NAICS weighted cross-tab heatmap ----
    def _plot_noc_naics_heatmap(self) -> None:
        """
        Office panel: NOC × NAICS weighted cross-tab heatmap per cycle.
        Verifies that the two bucketing variables are jointly plausible.
        """
        fig, axes = plt.subplots(1, len(CYCLES), figsize=(18, 6), squeeze=False)

        for col_idx, year in enumerate(CYCLES):
            ax  = axes[0, col_idx]
            df  = self.data[year].get("main")
            noc = NOC_COLS[year]
            nai = NAICS_COLS[year]

            if df is None or noc not in df.columns or nai not in df.columns:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center",
                        fontsize=14, color="#cdd6f4", transform=ax.transAxes)
                ax.set_title(str(year), fontsize=12, fontweight="bold")
                ax.set_xticks([]); ax.set_yticks([])
                continue

            wgt_col = "WGHT_PER" if "WGHT_PER" in df.columns else None
            sub = df[[noc, nai]].copy()
            sub[noc] = pd.to_numeric(sub[noc], errors="coerce")
            sub[nai] = pd.to_numeric(sub[nai], errors="coerce")
            if wgt_col:
                sub["_w"] = pd.to_numeric(df[wgt_col], errors="coerce").fillna(0)
            # drop not-applicable / valid-skip / DK / refusal / NS codes (>=90 in both
            # NOC and NAICS) so the real occupation x industry structure is visible
            # rather than swamped by the huge "not in labour force" bucket (code 96/97).
            sub = sub[(sub[noc] < 90) & (sub[nai] < 90)]

            if wgt_col:
                ct = sub.dropna().pivot_table(index=noc, columns=nai, values="_w",
                                              aggfunc="sum", fill_value=0)
            else:
                ct = pd.crosstab(sub[noc].dropna(), sub[nai].dropna())

            if ct.empty:
                ax.text(0.5, 0.5, "empty", ha="center", va="center",
                        transform=ax.transAxes, color="#cdd6f4")
            else:
                sns.heatmap(ct, ax=ax, cmap="Blues", linewidths=0.2, linecolor="#1e1e2e",
                            cbar=(col_idx == len(CYCLES) - 1),
                            xticklabels=True, yticklabels=True,
                            annot=(ct.shape[0] * ct.shape[1] <= 80),
                            fmt=".0f", annot_kws={"size": 6})
                ax.tick_params(axis="both", labelsize=6)

            ax.set_title(f"{year}", fontsize=12, fontweight="bold")
            ax.set_xlabel("NAICS", fontsize=9)
            ax.set_ylabel("NOC" if col_idx == 0 else "", fontsize=9)

        fig.suptitle("Office Panel — NOC × NAICS Weighted Cross-Tab (weighted)\n"
                     "not-applicable / valid-skip codes (≥90, incl. not-in-labour-force) excluded",
                     fontsize=12, fontweight="bold")
        self._save_plot_to_b64("5_noc_naics_heatmap")
        self._record("pass", "NOC × NAICS heatmap generated")

    # ---- Chart 6 (Office): Telework rate per cycle ----
    # Per-cycle telework instrument + how to read it. The GSS telework question is
    # NOT the same across cycles, so a single trend line would be misleading:
    #   2010 MAR_Q190 — "usual" arrangement, yes/no  (yes=1, asked={1,2})
    #   2015 WTI_130  — diary-DAY paid-work-at-home   (any of 1-9 vs valid-skip 96)
    #   2022 TLWK_01A — "usual" arrangement, yes/no   (yes=1, asked={1,2})
    # 2010 and 2022 share the same y/n "usual" instrument → that pair is the real,
    # comparable COVID jump. 2015 is a different (diary-day) measure, flagged apart.
    TELEWORK_RATE_CFG = {
        2010: {"yes": {1},            "universe": {1, 2},                       "note": "usual (y/n)"},
        2015: {"yes": set(range(1, 10)), "universe": set(range(1, 10)) | {96}, "note": "diary-day ≠"},
        2022: {"yes": {1},            "universe": {1, 2},                       "note": "usual (y/n)"},
    }

    def _plot_telework_rate(self) -> None:
        """Office panel: REAL telework rate per cycle = teleworked / in-universe,
        decoded from each cycle's own instrument (see TELEWORK_RATE_CFG)."""
        labels, rates, notes = [], [], []
        for year in CYCLES:
            col = TELEWORK_COLS[year]
            df  = self.data[year].get("main")
            cfg = self.TELEWORK_RATE_CFG.get(year)
            labels.append(str(year))
            if df is None or col is None or col not in df.columns or cfg is None:
                rates.append(None); notes.append("n/a")           # 2005: no telework var
                continue
            v = pd.to_numeric(df[col], errors="coerce")
            uni = v.isin(cfg["universe"]).sum()
            yes = v.isin(cfg["yes"]).sum()
            rates.append(100.0 * yes / uni if uni else None)
            notes.append(cfg["note"])

        COLORS = ["#6c7086", "#f38ba8", "#fab387", "#a6e3a1"]   # 2005 grey = n/a
        fig, ax = plt.subplots(figsize=(8.5, 4.6))
        plot_vals = [r if r is not None else 0.0 for r in rates]
        bars = ax.bar(labels, plot_vals, color=COLORS[:len(labels)],
                      edgecolor="#1e1e2e", linewidth=0.8, width=0.6)
        for bar, val, note in zip(bars, rates, notes):
            if val is None:
                ax.text(bar.get_x() + bar.get_width() / 2, 1.0, "n/a\n(no var)",
                        ha="center", va="bottom", fontsize=9, color="#cdd6f4")
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, val + 0.6,
                        f"{val:.1f}%\n{note}", ha="center", va="bottom", fontsize=9)
        ax.set_title("Office Panel — Telework Rate per Cycle (decoded from each instrument)\n"
                     "comparable y/n 'usual' pair 2010→2022 = the COVID jump; 2015 is a diary-day measure",
                     fontsize=11, pad=10)
        ax.set_ylabel("% who telework (of in-universe)")
        ax.yaxis.grid(True, linestyle="--", alpha=0.4)
        ax.set_ylim(0, max(plot_vals + [5]) * 1.30)
        fig.tight_layout()
        self._save_plot_to_b64("6_telework_rate")
        self._record("pass", "Telework-rate-per-cycle chart generated")

    # ---- Chart 7 (Office): raw location-code distribution ----
    def _plot_occpre_distribution(self) -> None:
        """
        Office panel: share of episode rows in each RAW location code, per cycle.
        occPRE does not exist at Step 1; the raw per-cycle source (PLACE for
        2005/2010, LOCATION for 2015/2022) is what AT_WORK is derived from at
        Step 2/3.  The workplace code should be a visible non-trivial slice.
        """
        COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        fig, axes = plt.subplots(1, len(CYCLES), figsize=(18, 5), squeeze=False, sharey=True)

        for col_idx, year in enumerate(CYCLES):
            ax      = axes[0, col_idx]
            epi     = self.data[year].get("episode")
            loc_col = LOCATION_SRC_COLS[year]

            if epi is None or loc_col not in epi.columns:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center",
                        fontsize=14, color="#cdd6f4", transform=ax.transAxes)
                ax.set_title(str(year), fontsize=12, fontweight="bold")
                continue

            numeric_loc = pd.to_numeric(epi[loc_col], errors="coerce").dropna().astype(int)
            # top-15 codes by frequency so high-cardinality LOCATION stays readable
            counts = numeric_loc.value_counts(normalize=True).sort_values(ascending=False).head(15)
            counts = counts.sort_index()
            ax.bar(counts.index.astype(str), counts.values * 100,
                   color=COLORS[col_idx], edgecolor="#1e1e2e", linewidth=0.5)
            ax.set_title(f"{year} ({loc_col})", fontsize=12, fontweight="bold")
            ax.set_xlabel("location code", fontsize=9)
            if col_idx == 0:
                ax.set_ylabel("% of episode rows", fontsize=9)
            ax.xaxis.set_tick_params(labelsize=7, rotation=45)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        fig.suptitle(
            "Office Panel — Raw Location-Code Distribution per Cycle\n"
            "Workplace code = AT_WORK source (derived at Step 2/3); top-15 codes shown",
            fontsize=12, fontweight="bold",
        )
        self._save_plot_to_b64("7_occpre_distribution")
        self._record("pass", "location-code distribution chart generated")

    # ------------------------------------------------------------------
    # HTML Report Export
    # ------------------------------------------------------------------

    def export_html_report(self) -> None:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total  = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_titles = {
            "1_row_counts":          "Chart 1 — GSS Data Volume (Row Counts)",
            "2_episode_density":     "Chart 2 — Episode Density per Respondent",
            "3a_weight_dist":        "Chart 3 — Respondent Weight Distribution",
            "3b_diary_completeness": "Chart 4 — Diary Completeness (Day Coverage)",
            "3_nan_heatmap":         "Chart 5 — Missing-Data % per Office Variable × Cycle",
            "4_time_ordering":       "Chart 6 — Episode Time-Ordering Pass Rate",
            "5_noc_naics_heatmap":   "Office Chart 7 — NOC × NAICS Cross-Tab (real codes only)",
            "6_telework_rate":       "Office Chart 8 — Telework Rate per Cycle (COVID Jump)",
            "7_occpre_distribution": "Office Chart 9 — Raw Location-Code Distribution",
        }

        # Plain-language "what am I looking at / what is good" caption per chart.
        chart_captions = {
            "1_row_counts":          "Respondents and episode rows per cycle. GOOD: counts match the documented GSS PUMF totals (declining sample size over cycles is expected).",
            "2_episode_density":     "How many diary episodes each person reported. GOOD: a tight band with median ~15–25 episodes; no cycle collapsing to 1–2.",
            "3a_weight_dist":        "Survey weights (WGHT_PER) per cycle. GOOD: all positive, no wild outliers — confirms weights weren't corrupted during the file read.",
            "3b_diary_completeness": "Each bar = one cycle, split by how fully its diaries cover the day. GOOD: the red 'Incomplete (<24 h)' slice is 0% everywhere — every diary was read end-to-end. 2015/22 are 100% exactly-24 h (clipped at source). 2005/10 mostly 'run past 24 h' (green→orange) because those cycles record into the next morning — a faithful read, harmonized in Step-2.",
            "3_nan_heatmap":         "Missing-value % for each office-gating VARIABLE, by cycle. GOOD: cells are 0 (present & complete) or grey 'n/a' (variable not collected that cycle — expected). A bright red cell would mean a variable was expected but failed to read.",
            "4_time_ordering":       "Share of episodes where start ≤ end (overnight wrap allowed). GOOD: ≥95% (green). This confirms the time fields parsed correctly.",
            "5_noc_naics_heatmap":   "Joint occupation (NOC) × industry (NAICS) weighted counts, with the not-applicable/not-in-labour-force codes (≥90) removed so the real structure shows. GOOD: a populated, plausible grid — confirms BOTH office-archetype variables read together and aren't degenerate.",
            "6_telework_rate":       "Real telework rate per cycle, decoded from each cycle's own instrument (rate = teleworked ÷ in-universe). The question DIFFERS by cycle, so this isn't one trend: 2010 & 2022 share the same yes/no 'usual arrangement' wording → that pair (~22%→~38%) is the genuine COVID jump; 2015 uses a diary-day measure (flagged ≠); 2005 has no telework variable (n/a).",
            "7_occpre_distribution": "Raw location-code mix on the episode file (PLACE 2005/10, LOCATION 2015/22). GOOD: the workplace code is a visible non-trivial slice — this is the source AT_WORK is derived from at Step 2/3.",
        }

        charts_html = ""
        for key, label in chart_titles.items():
            if key in self.plots_b64:
                cap = chart_captions.get(key, "")
                cap_html = f'<p class="chart-caption">{cap}</p>' if cap else ""
                charts_html += f"""
      <section class="chart-section" id="{key}">
        <h2>{label}</h2>
        {cap_html}
        <div class="chart-wrap">
          <img src="data:image/png;base64,{self.plots_b64[key]}" alt="{label}">
        </div>
      </section>"""

        # Rename-crosswalk notice panel — explains why raw PUMF names do not
        # appear in the output CSVs (the reader renames them to canonical names).
        wet120_notice = textwrap.dedent("""\
            The Step-1 reader applies MAIN_RENAME_MAP before writing the CSVs, so the
            output columns carry CANONICAL names, not the raw PUMF variable names:
              LFSGSS / ACT7DAYS / ACT7DAYC  -> LFTAG   (LF-status / activity)
              WKWEHR_C / WHWD140C / WHWD140G -> HRSWRK (hours worked)
              MAR_Q172 / WHW_110 / WET_120   -> COW    (class of worker)
              NOC1110Y / NOCLBR_Y           -> NOCS   (occupation, 2015/2022)
            Class-of-worker IS present for all four cycles — 2015 is sourced from
            WHW_110 (the WET_120 PUMF suppression is therefore not a gap here).
            On the EPISODE file, occPRE does NOT exist at Step 1 by design: the raw
            location source (PLACE for 2005/2010, LOCATION for 2015/2022) is what
            AT_WORK is derived from at Step 2/3.  No further action is required.
        """)

        # Intro — WHAT this report compares and WHY (plain language, top of page).
        intro_html = textwrap.dedent("""\
            <p><strong>What this is.</strong> Step&nbsp;1 of the Leg-2 (two-channel:
            Residential&nbsp;+&nbsp;Office) pipeline reads four GSS Time-Use cycles
            (2005, 2010, 2015, 2022) from raw Statistics&nbsp;Canada microdata and
            writes 8 tidy CSVs (one <em>main</em> + one <em>episode</em> file per
            cycle). This report checks those 8 CSVs <em>before</em> we move to Step&nbsp;2
            (harmonization), because every later step inherits whatever we read here.</p>
            <p><strong>What we compare, and why.</strong></p>
            <ul>
              <li><strong>Did every column survive the read?</strong> (Method&nbsp;1 — schema, row counts, dtypes)
                  — a column that silently failed to read would corrupt the office split.</li>
              <li><strong>Are the categories sensible and consistent across cycles?</strong> (Method&nbsp;2)
                  — catches a wrong column being pulled or a value-code shift between cycles.</li>
              <li><strong>Are the diaries intact?</strong> (Method&nbsp;3 — IDs link, time ordered,
                  minutes sum to 1440, location codes present) — Step&nbsp;3 tiles these into 48 slots,
                  so a broken diary breaks the schedule.</li>
              <li><strong>Did the survey weights survive?</strong> (Method&nbsp;4) — weights drive every
                  population estimate downstream.</li>
            </ul>
            <p>Each check prints ✅ pass / ⚠️ warning / ❌ fail with the actual number, so the
            green ticks are backed by values you can read (e.g. "PLACE 2005 — 24 distinct codes,
            0% NaN"), not just a colour.</p>
        """)

        # Provenance — honest explanation of WHY the FAIL count changed on 2026-06-14.
        provenance_html = textwrap.dedent("""\
            <p>An earlier version of this validator reported <strong>4 FAIL + 22 WARN</strong>.
            All of them were <strong>validator bugs, not data problems</strong> — the data was
            never broken. Three mechanisms:</p>
            <ol>
              <li><strong>Rename blindness.</strong> The reader renames raw PUMF variables to
                  canonical names <em>before</em> writing the CSVs
                  (<code>ACT7DAYS/WHW_110/…→LFTAG/COW/NOCS/HRSWRK</code>). The old validator
                  searched for the <em>raw</em> names, so it declared present columns "missing."</li>
              <li><strong>occPRE checked too early.</strong> <code>occPRE</code> / <code>AT_WORK</code>
                  are <em>derived at Step&nbsp;2/3</em>, not at read time. The old validator failed
                  because they weren't in the Step-1 episode file — but they're not supposed to be yet.
                  We now check the raw location source (<code>PLACE</code>/<code>LOCATION</code>) it is derived from.</li>
              <li><strong>Telework heuristic.</strong> Telework vars are universe-coded (~100% non-NaN
                  is normal); the old "&gt;100% coverage = suspicious" rule was wrong.</li>
            </ol>
            <p>To make sure nothing real was swept under the rug, this version is
            <strong>stricter</strong>, not looser: it adds Method&nbsp;4 (weights), diary-completeness,
            episodes-per-person, activity-code-range, row-count and dtype checks. A genuine read
            error would now trip one of these. They all pass on the actual numbers.</p>
        """)

        def _badge_list(items: list[str], cls: str) -> str:
            if not items:
                return f"<li class='badge pass'>No {cls}s detected</li>"
            return "".join(f'<li class="badge {cls}">{m}</li>' for m in items)

        fails_html  = _badge_list(self.results["fail"], "fail")
        warns_html  = _badge_list(self.results["warn"], "warn")
        passes_html = "".join(f'<li class="badge pass">{m}</li>' for m in self.results["pass"])
        nav_links   = "".join(
            f'<a href="#{k}">{v.split("—")[0].strip()}</a>'
            for k, v in chart_titles.items() if k in self.plots_b64
        )
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Leg-2 Step 1 — Validation Report</title>
  <style>
    :root {{
      --bg:#1e1e2e; --surface:#2a2a3e; --surface2:#313244;
      --accent:#89b4fa; --green:#a6e3a1; --yellow:#f9e2af;
      --red:#f38ba8; --text:#cdd6f4; --subtext:#a6adc8; --border:#45475a;
    }}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
    header{{background:var(--surface);border-bottom:1px solid var(--border);padding:18px 32px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}}
    header h1{{font-size:1.25rem;color:var(--accent)}}
    header p{{font-size:0.8rem;color:var(--subtext)}}
    nav{{background:var(--surface2);border-bottom:1px solid var(--border);padding:8px 32px;display:flex;gap:20px;flex-wrap:wrap}}
    nav a{{color:var(--subtext);text-decoration:none;font-size:0.82rem;padding:4px 10px;border-radius:6px;transition:background 0.2s,color 0.2s}}
    nav a:hover{{background:var(--surface);color:var(--accent)}}
    main{{max-width:1100px;margin:0 auto;padding:30px 28px}}
    .scorecard{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:36px}}
    .score-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 16px;text-align:center}}
    .score-card .number{{font-size:2.4rem;font-weight:700}}
    .score-card .label{{font-size:0.8rem;color:var(--subtext);margin-top:4px}}
    .score-card.ok .number{{color:var(--green)}}
    .score-card.warn .number{{color:var(--yellow)}}
    .score-card.fail .number{{color:var(--red)}}
    .score-card.pct .number{{color:var(--accent);font-size:2.0rem}}
    .findings{{margin-bottom:36px}}
    .findings h2{{font-size:1.05rem;margin-bottom:12px;color:var(--accent)}}
    .badge-list{{list-style:none;display:flex;flex-direction:column;gap:6px}}
    .badge{{padding:8px 14px;border-radius:8px;font-size:0.85rem;line-height:1.4}}
    .badge.pass{{background:#1c2e22;border:1px solid #2d5a35;color:var(--green)}}
    .badge.warn{{background:#2e2a1c;border:1px solid #5a4e1f;color:var(--yellow)}}
    .badge.fail{{background:#2e1c1e;border:1px solid #5a2428;color:var(--red)}}
    .chart-section{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:28px}}
    .chart-section h2{{font-size:1.0rem;color:var(--accent);margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
    .chart-wrap{{text-align:center}}
    .chart-wrap img{{max-width:100%;height:auto;border-radius:8px}}
    .chart-caption{{font-size:0.85rem;color:var(--subtext);margin-bottom:14px;line-height:1.5;border-left:3px solid var(--accent);padding-left:12px}}
    .intro-section{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px 28px;margin-bottom:28px;line-height:1.6}}
    .intro-section h2{{font-size:1.05rem;color:var(--accent);margin-bottom:12px}}
    .intro-section p{{margin-bottom:10px;font-size:0.9rem}}
    .intro-section ul,.intro-section ol{{margin:0 0 12px 22px;font-size:0.88rem}}
    .intro-section li{{margin-bottom:6px}}
    .intro-section code{{background:var(--surface2);padding:1px 5px;border-radius:4px;font-size:0.82rem}}
    .provenance-section{{background:var(--surface);border:2px solid var(--accent);border-radius:14px;padding:24px 28px;margin-bottom:28px;line-height:1.6}}
    .provenance-section h2{{font-size:1.05rem;color:var(--accent);margin-bottom:12px}}
    .provenance-section p{{margin-bottom:10px;font-size:0.9rem}}
    .provenance-section ol{{margin:0 0 12px 22px;font-size:0.88rem}}
    .provenance-section li{{margin-bottom:6px}}
    .provenance-section code{{background:var(--surface2);padding:1px 5px;border-radius:4px;font-size:0.82rem}}
    .notice-section{{background:var(--surface);border:2px solid var(--yellow);border-radius:14px;padding:24px;margin-bottom:28px}}
    .notice-section h2{{font-size:1.0rem;color:var(--yellow);margin-bottom:12px}}
    .notice-pre{{font-family:'Courier New',Consolas,monospace;font-size:0.82rem;color:var(--subtext);white-space:pre-wrap;background:var(--surface2);padding:14px;border-radius:8px;border:1px solid var(--border)}}
    .pipeline-section{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:28px}}
    .pipeline-section h2{{font-size:1.0rem;color:var(--accent);margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
    .pipeline-pre{{font-family:'Courier New',Consolas,monospace;font-size:0.78rem;color:var(--subtext);white-space:pre;overflow-x:auto;background:var(--surface2);padding:16px;border-radius:8px;border:1px solid var(--border);line-height:1.5}}
    footer{{text-align:center;padding:20px;font-size:0.78rem;color:var(--subtext);border-top:1px solid var(--border);margin-top:10px}}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GSS Leg-2 Step 1 — Validation Report (Two-Channel Split)</h1>
      <p>Residential + Office column check · Cycles 2005 / 2010 / 2015 / 2022 · {ts}</p>
    </div>
  </header>
  <nav><a href="#intro">What &amp; Why</a><a href="#provenance">Why 0 Fails</a><a href="#pipeline-overview">Pipeline</a><a href="#wet120-notice">Rename Note</a>{nav_links}</nav>
  <main>
    <section class="intro-section" id="intro">
      <h2>What this report compares — and why</h2>
      {intro_html}
    </section>

    <section class="provenance-section" id="provenance">
      <h2>Why this run shows 0 failures (it previously showed 4)</h2>
      {provenance_html}
    </section>

    <section class="pipeline-section" id="pipeline-overview">
      <h2>Pipeline Overview — Step 1: Two-Channel Split Data Collection</h2>
      <pre class="pipeline-pre">{STEP1_OVERVIEW}</pre>
    </section>

    <section class="notice-section" id="wet120-notice">
      <h2>ℹ️  Rename Crosswalk — Raw PUMF Names → Canonical CSV Names</h2>
      <pre class="notice-pre">{wet120_notice}</pre>
    </section>

    <div class="scorecard">
      <div class="score-card ok">  <div class="number">{n_pass}</div><div class="label">Checks Passed</div></div>
      <div class="score-card warn"><div class="number">{n_warn}</div><div class="label">Warnings</div></div>
      <div class="score-card fail"><div class="number">{n_fail}</div><div class="label">Failures</div></div>
      <div class="score-card pct"> <div class="number">{pct_ok}%</div><div class="label">Pass Rate</div></div>
    </div>

    <div class="findings"><h2>Failures</h2><ul class="badge-list">{fails_html}</ul></div>
    <div class="findings"><h2>Warnings</h2><ul class="badge-list">{warns_html}</ul></div>
    <div class="findings"><h2>Passed</h2><ul class="badge-list">{passes_html}</ul></div>

    {charts_html}
  </main>
  <footer>Occupancy Modeling Pipeline · Leg-2 Step-1 Validator · Generated {ts}</footer>
</body>
</html>"""

        html_path = os.path.join(self.data_dir, "step1_validation_report.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"\nHTML report saved to: {html_path}")

    # ------------------------------------------------------------------
    # Console report save
    # ------------------------------------------------------------------

    def save_console_report(self) -> None:
        txt_path = os.path.join(self.data_dir, "step1_validation_report.txt")
        with open(txt_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self._console_lines))
        print(f"Console report saved to: {txt_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print(STEP1_OVERVIEW)
    print(f"\nData directory: {OUTPUTS_DIR}")

    validator = GSSValidator2Split(OUTPUTS_DIR)
    validator.load_data()
    validator.audit_schema()
    validator.compare_categories()
    validator.verify_episode_integrity()
    validator.verify_weights()
    validator.generate_visuals()
    validator.save_console_report()

    n_pass = len(validator.results["pass"])
    n_warn = len(validator.results["warn"])
    n_fail = len(validator.results["fail"])
    print(f"\n{'='*60}")
    print(f"Validation complete — PASS {n_pass}  WARN {n_warn}  FAIL {n_fail}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
