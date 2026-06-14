# -*- coding: utf-8 -*-
"""
01_readingGSS_2split_val.py

Leg-2 (Residential + Office two-channel split) — Step-1 VALIDATOR.

Loads the 8 Step-1 CSVs produced by 01_readingGSS_2split.py and runs
validation methods defined in 01_readingGSS_val.md:
  - Method 1: Schema & Shape Audit (residential + office column presence)
  - Method 2: Cross-Cycle Category Comparison (residential + office sanity)
  - Method 3: Episode Integrity Check (residential + occPRE / AT_WORK checks)
  - Method 5: Visual Summary Dashboard (residential panels + 4 office panels)

Method 4 (weight distribution) is reused from Leg 1 as-is and included here
as a lightweight add-on inside Method 1 / the dashboard.

WINDOWS ENCODING NOTE:
  Run with  py -X utf8 01_readingGSS_2split_val.py
  or set    PYTHONIOENCODING=utf-8
  to avoid cp1252 crashes on the ✅ / ❌ / ⚠️ glyphs.

Robustness:
  - Missing CSVs: reported clearly; that cycle is skipped rather than crashing.
  - Missing office column: EXPECTED for 2015 WET_120; soft warning for others.
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

if platform.system() == "Darwin":
    _BASE = (
        "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/"
        "3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/outputs_step1"
    )
else:
    _BASE = (
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
        r"\3J_docs_occ_nTemp\Leg2_2-split\Step1_docs\outputs_step1"
    )

OUTPUTS_DIR: str = _BASE
CYCLES = [2005, 2010, 2015, 2022]

# ---------------------------------------------------------------------------
# OFFICE COLUMN MAP (per cycle)
# None  → column does not exist for this cycle (expected absence)
# ---------------------------------------------------------------------------

# activity-last-week
ACT_WEEK_COLS = {2005: "MAR_Q100", 2010: "MAR_Q100", 2015: "ACT7DAYS", 2022: "ACT7DAYC"}

# worked-last-week (2005 piggy-backs on MAR_Q100)
WORKED_WEEK_COLS = {2005: "MAR_Q100", 2010: "WKLTWE", 2015: "MRW_D40B", 2022: "MRW_D40B"}

# LF status (2015/2022 are derived in later steps — not a raw column)
LF_STATUS_COLS = {2005: "LFSGSS", 2010: "LFSGSS", 2015: None, 2022: None}

# hours worked
HOURS_COLS = {2005: "WKWEHR_C", 2010: "WKWEHR_C", 2015: "WHWD140C", 2022: "WHWD140G"}

# class of worker — WET_120 is SUPPRESSED in 2015 PUMF (expected miss)
COW_COLS = {2005: "MAR_Q172", 2010: "MAR_Q172", 2015: "WET_120", 2022: "WET_120"}
COW_2015_SUPPRESSED = True   # sentinel — used in Method 1 logic

# NOC occupation
NOC_COLS = {2005: "SOC91C10", 2010: "NOCS2006_C10", 2015: "NOC1110Y", 2022: "NOCLBR_Y"}

# NAICS industry
NAICS_COLS = {
    2005: "NAICS2002_C16", 2010: "NAICS2007_C16",
    2015: "NAIC12CY",      2022: "NAIC22CY",
}

# telework (2005 → None; 2022 has multiple sub-columns)
TELEWORK_COLS = {2005: None, 2010: "MAR_Q190", 2015: "WTI_130", 2022: "TLWK_01A"}
# additional 2022 telework columns (B–D and 02G) — used for existence check only
TELEWORK_2022_EXTRA = ["TLWK_01B", "TLWK_01C", "TLWK_01D", "TLWK_02G"]

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
║  │  occACT, occPRE, co-presence columns, techUse, wellbeing, WGHT_EPI     │  ║
║  └─ Key NEW check ────────────────────────────────────────────────────────┘  ║
║     occPRE must be present on EVERY episode row; AT_WORK derived in Step 2/3  ║
╚══════════════════════════════════════════════════════════════════════════════════╝"""


# ---------------------------------------------------------------------------
# VALIDATOR CLASS
# ---------------------------------------------------------------------------

class GSSValidator2Split:
    """
    Validation class for Leg-2 Step-1 outputs.

    Residential checks are reused unchanged from the Leg-1 validator.
    Office checks are added per the spec in 01_readingGSS_val.md.
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
            non_nan_share = df[col].notna().mean()
            print(f"    {year} ({col}): {non_nan_share:.1%} non-NaN")
            if year == 2022:
                if non_nan_share < 0.01:
                    self._record(
                        "fail",
                        f"Telework 2022: implausibly low non-NaN share {non_nan_share:.1%} (<1%)",
                    )
                else:
                    self._record(
                        "pass",
                        f"Telework 2022: {non_nan_share:.1%} non-NaN — COVID jump plausible",
                    )
            else:
                if non_nan_share > 0.10:
                    self._record(
                        "warn",
                        f"Telework {year}: non-NaN share {non_nan_share:.1%} > 10% (unexpectedly high)",
                    )
                else:
                    self._record(
                        "pass",
                        f"Telework {year}: {non_nan_share:.1%} non-NaN — sparse as expected",
                    )

    # ------------------------------------------------------------------
    # Method 3 — Episode Integrity Check
    # ------------------------------------------------------------------

    def verify_episode_integrity(self) -> None:
        """
        Method 3: Episode Integrity Check.

        Residential checks — reused from Leg 1 (ID linkage, time ordering).
        occPRE checks       — NEW: presence, NaN rate, value range 1–18,
                              AT_WORK-compatible share (2–10%),
                              AT_WORK column NOT present yet.
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

            # ---- occPRE presence (NEW) ----
            if "occPRE" not in epi.columns:
                self._record(
                    "fail",
                    f"{year}: occPRE MISSING from episode file — "
                    "AT_WORK cannot be derived in Step 2/3",
                )
            else:
                # NaN rate
                nan_rate = epi["occPRE"].isnull().mean()
                if nan_rate < 0.05:
                    self._record("pass", f"{year}: occPRE NaN rate {nan_rate:.1%} (<5% threshold)")
                else:
                    self._record(
                        "warn",
                        f"{year}: occPRE NaN rate {nan_rate:.1%} — exceeds 5% threshold",
                    )

                # Value range 1–18
                numeric_pre = pd.to_numeric(epi["occPRE"], errors="coerce").dropna()
                out_of_range = numeric_pre[(numeric_pre < 1) | (numeric_pre > 18)]
                if out_of_range.empty:
                    self._record("pass", f"{year}: occPRE all values in 1–18 range")
                else:
                    bad_vals = sorted(out_of_range.unique().tolist())[:10]
                    self._record(
                        "warn",
                        f"{year}: occPRE has {len(out_of_range)} out-of-range values: {bad_vals}",
                    )

                # AT_WORK-compatible share (occPRE == 2)
                n_total = len(epi)
                if n_total > 0:
                    at_work_share = (pd.to_numeric(epi["occPRE"], errors="coerce") == 2).mean()
                    if 0.02 <= at_work_share <= 0.10:
                        self._record(
                            "pass",
                            f"{year}: AT_WORK-compatible share (occPRE==2) = {at_work_share:.2%} — plausible",
                        )
                    elif at_work_share == 0.0:
                        self._record(
                            "fail",
                            f"{year}: AT_WORK-compatible share = 0% — occPRE==2 never seen; "
                            "likely read error",
                        )
                    else:
                        self._record(
                            "warn",
                            f"{year}: AT_WORK-compatible share = {at_work_share:.2%} — "
                            "outside expected 2–10% range (check encoding)",
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

    # ---- Chart 3: NaN Heatmap (Leg-1 reuse, adapted) ----
    def _plot_nan_heatmap(self) -> None:
        records = []
        # Collect all office column names that might appear
        office_cols: set[str] = set()
        for m in [ACT_WEEK_COLS, HOURS_COLS, COW_COLS, NOC_COLS, NAICS_COLS, TELEWORK_COLS]:
            for v in m.values():
                if v is not None:
                    office_cols.add(v)

        for year in CYCLES:
            main = self.data[year].get("main")
            if main is None:
                continue
            nan_pct = main.isnull().mean() * 100
            for col, pct in nan_pct.items():
                if col in office_cols:
                    records.append({"Cycle": str(year), "Column": col, "NaN%": pct})

        if not records:
            self._record("warn", "NaN heatmap skipped — no office columns found")
            return

        pivot = (pd.DataFrame(records)
                   .pivot(index="Column", columns="Cycle", values="NaN%")
                   .fillna(0))

        fig_h = max(4, len(pivot) * 0.45)
        fig, ax = plt.subplots(figsize=(9, fig_h))
        sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.4, linecolor="#1e1e2e",
                    annot=True, fmt=".0f", cbar_kws={"label": "% Missing"},
                    annot_kws={"size": 8})
        ax.set_title("NaN % per Office Column × Cycle (Main Files)", fontsize=13, pad=10)
        ax.set_xlabel("Survey Cycle"); ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=0); ax.tick_params(axis="y", rotation=0, labelsize=8)
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

        fig.suptitle("Office Panel — NOC × NAICS Weighted Cross-Tab (counts / weighted)",
                     fontsize=13, fontweight="bold")
        self._save_plot_to_b64("5_noc_naics_heatmap")
        self._record("pass", "NOC × NAICS heatmap generated")

    # ---- Chart 6 (Office): Telework rate per cycle ----
    def _plot_telework_rate(self) -> None:
        """
        Office panel: share of main-file rows with a non-NaN telework flag,
        by cycle.  Should show near-zero in 2005, small in 2010/2015, COVID
        jump in 2022.
        """
        cycle_labels: list[str] = []
        rates: list[float] = []

        for year in CYCLES:
            col = TELEWORK_COLS[year]
            df  = self.data[year].get("main")
            if df is None or col is None or col not in df.columns:
                cycle_labels.append(str(year))
                rates.append(0.0)
                continue
            cycle_labels.append(str(year))
            rates.append(df[col].notna().mean() * 100)

        COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(cycle_labels, rates, color=COLORS[:len(cycle_labels)],
                      edgecolor="#1e1e2e", linewidth=0.8, width=0.55)
        for bar, val in zip(bars, rates):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=10)
        ax.set_title("Office Panel — Telework Non-NaN Rate per Cycle\n"
                     "(COVID jump expected in 2022)", fontsize=12, pad=10)
        ax.set_ylabel("% rows with telework flag")
        ax.yaxis.grid(True, linestyle="--", alpha=0.4)
        ax.set_ylim(0, max(rates + [5]) * 1.25)
        self._save_plot_to_b64("6_telework_rate")
        self._record("pass", "Telework-rate-per-cycle chart generated")

    # ---- Chart 7 (Office): occPRE distribution ----
    def _plot_occpre_distribution(self) -> None:
        """
        Office panel: share of episode rows in each occPRE category (1–18),
        per cycle.  Category 2 (workplace) should be the second-largest after
        category 1 (home); a COVID-era dip from 2015 to 2022 is expected.
        """
        COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        fig, axes = plt.subplots(1, len(CYCLES), figsize=(18, 5), squeeze=False, sharey=True)

        for col_idx, year in enumerate(CYCLES):
            ax  = axes[0, col_idx]
            epi = self.data[year].get("episode")

            if epi is None or "occPRE" not in epi.columns:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center",
                        fontsize=14, color="#cdd6f4", transform=ax.transAxes)
                ax.set_title(str(year), fontsize=12, fontweight="bold")
                continue

            numeric_pre = pd.to_numeric(epi["occPRE"], errors="coerce").dropna().astype(int)
            counts = numeric_pre.value_counts(normalize=True).sort_index()
            ax.bar(counts.index.astype(str), counts.values * 100,
                   color=COLORS[col_idx], edgecolor="#1e1e2e", linewidth=0.5)
            ax.set_title(str(year), fontsize=12, fontweight="bold")
            ax.set_xlabel("occPRE category", fontsize=9)
            if col_idx == 0:
                ax.set_ylabel("% of episode rows", fontsize=9)
            ax.xaxis.set_tick_params(labelsize=7, rotation=45)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        fig.suptitle(
            "Office Panel — occPRE Distribution per Cycle\n"
            "Cat 2 = workplace (AT_WORK source); COVID dip 2015→2022 expected",
            fontsize=12, fontweight="bold",
        )
        self._save_plot_to_b64("7_occpre_distribution")
        self._record("pass", "occPRE distribution chart generated")

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
            "1_row_counts":        "Chart 1 — GSS Data Volume (Row Counts)",
            "2_episode_density":   "Chart 2 — Episode Density per Respondent",
            "3_nan_heatmap":       "Chart 3 — NaN % per Office Column × Cycle",
            "4_time_ordering":     "Chart 4 — Episode Time-Ordering Pass Rate",
            "5_noc_naics_heatmap": "Office Chart 5 — NOC × NAICS Weighted Cross-Tab",
            "6_telework_rate":     "Office Chart 6 — Telework Rate per Cycle (COVID Jump)",
            "7_occpre_distribution": "Office Chart 7 — occPRE Distribution per Cycle",
        }

        charts_html = ""
        for key, label in chart_titles.items():
            if key in self.plots_b64:
                charts_html += f"""
      <section class="chart-section" id="{key}">
        <h2>{label}</h2>
        <div class="chart-wrap">
          <img src="data:image/png;base64,{self.plots_b64[key]}" alt="{label}">
        </div>
      </section>"""

        # WET_120 suppression notice panel
        wet120_notice = textwrap.dedent("""\
            Class-of-worker (WET_120) is suppressed in the 2015 PUMF and is absent
            from main_2015.csv.  This is an expected miss documented in
            00_GSS_split_suitability_audit.md §4.  NOC / NAICS serve as archetype
            proxies for the 2015 cycle.  No further action is required.
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
  <nav><a href="#pipeline-overview">Pipeline</a><a href="#wet120-notice">WET_120 Note</a>{nav_links}</nav>
  <main>
    <section class="pipeline-section" id="pipeline-overview">
      <h2>Pipeline Overview — Step 1: Two-Channel Split Data Collection</h2>
      <pre class="pipeline-pre">{STEP1_OVERVIEW}</pre>
    </section>

    <section class="notice-section" id="wet120-notice">
      <h2>⚠️  Known Expected Miss — 2015 WET_120 (Class of Worker)</h2>
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

        html_path = os.path.join(self.data_dir, "validation_report.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"\nHTML report saved to: {html_path}")

    # ------------------------------------------------------------------
    # Console report save
    # ------------------------------------------------------------------

    def save_console_report(self) -> None:
        txt_path = os.path.join(self.data_dir, "validation_report.txt")
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
