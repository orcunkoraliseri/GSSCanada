# -*- coding: utf-8 -*-
"""
3rdJ_02_harmonizeGSS_2split_val.py

Leg-2 (Residential + Office two-channel split) -- Step-2 VALIDATOR.

Ported from 2J_docs_occ_nTemp/02_harmonizeGSS_val.py (Leg-1, verbatim),
with the following Leg-2 additions:
  - Method 6 (location): adds AT_WORK weighted presence rate + occPRE=2 share
  - Method 11 (NEW): TELEWORK rate per cycle with instrument annotations
  - Method 12 (NEW): NOCS and NAICS coverage after unification

Reads from outputs_step2/ (Step-2 harmonized CSVs).
Emits outputs_step2/step2_validation_report.html and .txt in the same visual
style as Step-1's step1_validation_report.html.

PASS/WARN/FAIL tally convention (same as Step 1):
  PASS = check is clean / within expected range
  WARN = plausible but needs attention (soft threshold breach, missing optional col)
  FAIL = concrete data integrity problem (missing required col, wrong row count)

WINDOWS ENCODING NOTE:
  Run with  py -3 -X utf8 3rdJ_02_harmonizeGSS_2split_val.py
"""

import io
import os
import sys
import base64
import platform
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------

_WIN_BASE = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split"
_SPEED_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
_MAC_BASE = "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/3J_docs_occ_nTemp/Leg2_2-split"

if platform.system() == "Darwin":
    _LEG2 = _MAC_BASE
elif os.path.isdir(_WIN_BASE):
    _LEG2 = _WIN_BASE
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2 = _SPEED_BASE
else:
    _LEG2 = _WIN_BASE

INPUT_DIR = os.path.join(_LEG2, "Step1_docs", "outputs_step1")
OUTPUT_DIR = os.path.join(_LEG2, "Step2_docs", "outputs_step2")

CYCLES = [2005, 2010, 2015, 2022]

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

COPRE_COLS = [
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others", "colleagues",
]

SENTINEL_MAP: dict = {
    "COW": {97, 98, 99},
    "KOL": {98, 99},
    "TOTINC": {98, 99},
    "ATTSCH": {98, 99},
    "HRSWRK": {96, 97, 98, 99},
    "NOCS": {96, 97, 98, 99},
    "LFTAG": {8, 9, 97, 98, 99},
    "MARSTH": {8, 9, 99},
}

IGNORE_COLS: set = {
    "MODE",
    "CTW_Q140_C01", "CTW_Q140_C02", "CTW_Q140_C03", "CTW_Q140_C04", "CTW_Q140_C05",
    "CTW_Q140_C06", "CTW_Q140_C07", "CTW_Q140_C08", "CTW_Q140_C09",
    "CTW_140A", "CTW_140B", "CTW_140C", "CTW_140D", "CTW_140E", "CTW_140F",
    "CTW_140G", "CTW_140H", "CTW_140I",
    "EHG_ALL", "EDU10", "EDC_10", "ATT_150C", "WKSWRK",
    # Leg-2 raw telework/NOC/NAICS columns (renamed at Step 2)
    "MAR_Q190", "MAR_Q193", "WTI_130", "TLWK_01A", "TLWK_01B", "TLWK_01C",
    "TLWK_01D", "TLWK_02G",
    "SOC91C10", "NOCS2006_C10", "NAIC12CY", "NAIC22CY",
    "NAICS2002_C16", "NAICS2007_C16",
    "MAR_Q100", "WKLTWE", "MRW_D40B", "EOR_Q320", "EDUSTAT", "ESC1_01",
}

HARM_VARS = {
    "SEX":   {"expected": {1, 2}},
    "AGEGRP":{"expected": set(range(1, 8))},
    "MARSTH":{"expected": set(range(1, 7))},
    "HHSIZE":{"expected": set(range(1, 6))},
    "CMA":   {"expected": {1, 2, 3}},
    "LFTAG": {"expected": set(range(1, 6))},
    "HRSWRK":{"expected": None},
    "KOL":   {"expected": None},
    "TOTINC":{"expected": None},
}

ACT_LABELS = {
    1: "Work & Related",
    2: "Household Work",
    3: "Caregiving",
    4: "Purchasing",
    5: "Sleep & Rest",
    6: "Eating & Drinking",
    7: "Personal Care",
    8: "Education",
    9: "Socializing",
    10: "Passive Leisure",
    11: "Active Leisure",
    12: "Community",
    13: "Travel",
    14: "Misc / Idle",
}

_DARK = {
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
}
CYCLE_COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]

STEP2_OVERVIEW = """\
 STEP 2 -- DATA HARMONIZATION (Leg-2 Two-Channel Split)
   Cycles: 2005 / 2010 / 2015 / 2022

   RESIDENTIAL (verbatim from Leg 1):
   * Category recoding: SEX, MARSTH, AGEGRP, LFTAG, HHSIZE, KOL, HRSWRK
   * Missing value alignment (96/97/98/99 -> NaN)
   * ATTSCH, POWST, MODE derived; COW, TOTINC harmonized
   * Activity crosswalk (14 categories); presence crosswalk (18 occPRE codes)
   * Co-presence OR-merge (9 unified columns)
   * Diary closure QA (sum(duration per occID) == 1440)
   * Metadata flags: CYCLE_YEAR, COLLECT_MODE, TUI_10_AVAIL, BS_TYPE

   LEG-2 ADDITIONS:
   * Delta B -- AT_WORK = (occPRE == 2).astype(int) on every episode row
       occPRE==2 = workplace (2005/10) / "at work or school" (2015/22)
       Work-vs-school gating deferred to Step 5 (archetype linkage)
       WFH (2022 LOCATION=3300 = home) correctly excluded from AT_WORK
   * Delta C -- NOCS unified: 2005 SOC91C10 -> NOCS, 2010 NOCS2006_C10 -> NOCS
   * Delta D -- NAICS unified: per-cycle raw -> NAICS; codes >=90 -> NaN
   * Delta E -- TELEWORK harmonized (Int8 {0,1,NaN}):
       2005: n/a (no instrument)
       2010: MAR_Q190 usual Y/N
       2015: WTI_130 diary-day (NOT a usual prevalence -- see flag below)
       2022: TLWK_01A usual Y/N

   WARNING flags:
   * TOTINC regime break: self-reported (2005-2015) / CRA-linked (2022)
   * 2015 TELEWORK is a DIARY-DAY measure, not a usual-prevalence instrument --
     treat the 2015 rate as diary-day incidence, NOT comparable to 2010/2022 rates
   * AT_WORK 2022 suppressed by WFH coding (LOCATION=3300=home != workplace)

   Output: 4 harmonized cycle pairs (Main + Episode), unified Leg-2 schema"""


def _apply_dark():
    plt.rcParams.update(_DARK)


def _b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# VALIDATOR CLASS
# ---------------------------------------------------------------------------

class GSSHarmonizationValidator2Split:
    """Step-2 validation for Leg-2 harmonized CSVs."""

    def __init__(self) -> None:
        self.main_s1: dict = {}
        self.epi_s1: dict = {}
        self.main_s2: dict = {}
        self.epi_s2: dict = {}
        self.results: dict = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict = {}
        self._console_lines: list = []

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = {"pass": "PASS", "fail": "FAIL", "warn": "WARN"}.get(level, "    ")
        line = f"[{icon}] {msg}"
        print(line)
        self._console_lines.append(line)

    def _section(self, title: str) -> None:
        line = f"\n--- {title} ---"
        print(line)
        self._console_lines.append(line)

    def load_data(self) -> None:
        self._section("Loading Data")
        for c in CYCLES:
            s1m = os.path.join(INPUT_DIR, f"main_{c}.csv")
            s1e = os.path.join(INPUT_DIR, f"episode_{c}.csv")
            s2m = os.path.join(OUTPUT_DIR, f"main_{c}.csv")
            s2e = os.path.join(OUTPUT_DIR, f"episode_{c}.csv")

            for path, store, key in [
                (s1m, self.main_s1, c),
                (s1e, self.epi_s1, c),
                (s2m, self.main_s2, c),
                (s2e, self.epi_s2, c),
            ]:
                if os.path.exists(path):
                    store[key] = pd.read_csv(path, low_memory=False)
                    print(f"  Loaded {os.path.basename(path)} -- {len(store[key]):,} rows")
                else:
                    store[key] = None
                    print(f"  MISSING: {path}")

    def run_all(self) -> None:
        _apply_dark()
        print("=== Step 2 Harmonization Validation (Leg-2 Two-Channel) ===\n")
        self.load_data()
        self.method1_schema()
        self.method2_rowcounts()
        self.method3_sentinels()
        self.method4_categories()
        self.method5_activity()
        self.method6_location()
        self.method7_metadata()
        self.method8_diary()
        self.method9_regression()
        self.method10_copresence()
        self.method11_telework()
        self.method12_nocs_naics()
        self.export_html()
        self.export_txt()

    # ---------------------------------------------------------------- Method 1
    def method1_schema(self) -> None:
        self._section("Method 1: Unified Schema Audit")
        main_cols = {c: set(self.main_s2[c].columns) if self.main_s2[c] is not None else set() for c in CYCLES}
        main_cols_f = {c: main_cols[c] - IGNORE_COLS for c in CYCLES}
        epi_cols = {c: set(self.epi_s2[c].columns) if self.epi_s2[c] is not None else set() for c in CYCLES}

        if all(main_cols_f[c] == main_cols_f[2005] for c in CYCLES):
            self._rec("pass", "All 4 Main files share identical (harmonized) column sets.")
        else:
            diffs = {c: main_cols_f[c].symmetric_difference(main_cols_f[2005]) for c in CYCLES}
            self._rec("warn", f"Main column differences (after ignoring raw/noise cols): {diffs}")

        if all(epi_cols[c] == epi_cols[2005] for c in CYCLES):
            self._rec("pass", "All 4 Episode files share identical column sets.")
        else:
            self._rec("warn", "Episode column mismatch across cycles -- check output.")

        # Residential expected columns
        expected_main = [
            "occID", "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR", "CMA",
            "LFTAG", "HRSWRK", "KOL", "TOTINC", "WGHT_PER", "DDAY", "SURVMNTH",
            "CYCLE_YEAR", "SURVYEAR", "COLLECT_MODE", "TUI_10_AVAIL", "BS_TYPE",
            "TOTINC_SOURCE", "ATTSCH", "POWST", "COW",
        ]
        # Leg-2 expected additions
        leg2_expected_main = ["NOCS", "NAICS", "TELEWORK", "WORK_SCHEDULE"]
        leg2_expected_epi  = ["AT_WORK", "AT_HOME", "occPRE"]

        if main_cols[2005]:
            missing = [c for c in expected_main if c not in main_cols[2005]]
            if not missing:
                self._rec("pass", f"All {len(expected_main)} residential Main columns present in 2005.")
            else:
                self._rec("fail", f"Missing residential columns in 2005 Main: {missing}")

            missing_l2 = [c for c in leg2_expected_main if c not in main_cols[2005]]
            if not missing_l2:
                self._rec("pass", "Leg-2 main columns (NOCS, NAICS, TELEWORK, WORK_SCHEDULE) all present.")
            else:
                self._rec("fail", f"Leg-2 Main columns missing: {missing_l2}")

        if epi_cols[2005]:
            missing_l2e = [c for c in leg2_expected_epi if c not in epi_cols[2005]]
            if not missing_l2e:
                self._rec("pass", "Leg-2 episode columns (AT_HOME, AT_WORK, occPRE) all present.")
            else:
                self._rec("fail", f"Leg-2 Episode columns missing: {missing_l2e}")

    # ---------------------------------------------------------------- Method 2
    def method2_rowcounts(self) -> None:
        self._section("Method 2: Row Count Preservation")
        for c in CYCLES:
            m1 = self.main_s1.get(c)
            m2 = self.main_s2.get(c)
            e1 = self.epi_s1.get(c)
            e2 = self.epi_s2.get(c)
            if m1 is not None and m2 is not None:
                if len(m1) == len(m2):
                    self._rec("pass", f"{c} Main rows preserved: {len(m2):,}")
                else:
                    self._rec("fail", f"{c} Main row count changed: {len(m1):,} -> {len(m2):,}")
            if e1 is not None and e2 is not None:
                if len(e1) == len(e2):
                    self._rec("pass", f"{c} Episode rows preserved: {len(e2):,}")
                else:
                    self._rec("fail", f"{c} Episode row count changed: {len(e1):,} -> {len(e2):,}")

    # ---------------------------------------------------------------- Method 3
    def method3_sentinels(self) -> None:
        self._section("Method 3: Sentinel Value Elimination")
        for c in CYCLES:
            df = self.main_s2.get(c)
            if df is None:
                continue
            found = [col for col, sentinels in SENTINEL_MAP.items()
                     if col in df.columns and df[col].isin(sentinels).any()]
            if not found:
                self._rec("pass", f"{c} -- no sentinel residuals found.")
            else:
                self._rec("fail", f"{c} -- sentinel values still present in: {found}")
            for key_col in ["WGHT_PER", "occID"]:
                if key_col in df.columns and df[key_col].isna().any():
                    self._rec("warn", f"{c} -- unexpected NaN in critical column '{key_col}'.")

    # ---------------------------------------------------------------- Method 4
    def method4_categories(self) -> None:
        self._section("Method 4: Category Recoding Verification")
        _apply_dark()
        n_vars = len(HARM_VARS)
        fig, axes = plt.subplots(n_vars, 4, figsize=(18, 3.0 * n_vars), sharey=False)
        fig.suptitle(
            "Harmonized Demographic Category Distributions (%) -- Step 2 Main Files",
            fontsize=14, fontweight="bold", y=1.005,
        )
        CAT_CMAP = "tab20"
        NA_COLOR = "#45475a"

        for row_i, (var_name, meta) in enumerate(HARM_VARS.items()):
            expected = meta["expected"]
            for col_i, (c, cyc_color) in enumerate(zip(CYCLES, CYCLE_COLORS)):
                ax = axes[row_i, col_i]
                df = self.main_s2.get(c)

                if df is None or var_name not in df.columns:
                    ax.bar([0], [1], color=NA_COLOR, hatch="///", edgecolor="#888", linewidth=0.6)
                    ax.text(0, 0.5, "N/A", ha="center", va="center", fontsize=12,
                            color="#cdd6f4", fontweight="bold")
                    ax.set_xlim(-0.5, 0.5); ax.set_ylim(0, 1)
                    ax.set_xticks([]); ax.set_yticks([])
                else:
                    series = (
                        df[var_name].dropna()
                        .pipe(lambda s: pd.to_numeric(s, errors="coerce"))
                        .dropna()
                        .value_counts(normalize=True)
                        .sort_index()
                    )
                    cats = series.index.tolist()
                    vals = series.values
                    cmap_ = plt.colormaps[CAT_CMAP].resampled(max(len(cats), 2))
                    colors = [cmap_(i) for i in range(len(cats))]
                    bottom = 0.0
                    for cat, val, color in zip(cats, vals, colors):
                        ax.bar([0], [val], bottom=[bottom], color=color,
                               edgecolor="#1e1e2e", linewidth=0.4, width=0.7)
                        if val >= 0.08:
                            ax.text(0, bottom + val / 2, f"{cat}\n{val:.0%}",
                                    ha="center", va="center", fontsize=7.5,
                                    color="white", fontweight="bold")
                        bottom += val
                    ax.set_xlim(-0.5, 0.5); ax.set_ylim(0, 1.0)
                    ax.set_xticks([])
                    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
                    ax.yaxis.grid(True, linestyle="--", alpha=0.25)
                    if expected is not None:
                        unexpected = {int(x) for x in cats} - expected
                        if unexpected:
                            self._rec("warn", f"{c} {var_name}: unexpected values {unexpected}")

                if row_i == 0:
                    ax.set_title(str(c), fontsize=13, fontweight="bold",
                                 color=cyc_color, pad=8)
                if col_i == 0:
                    ax.set_ylabel(var_name, fontsize=10, labelpad=8)

        plt.subplots_adjust(hspace=0.35, wspace=0.08)
        self.plots_b64["4_categories"] = _b64(fig)
        self._rec("pass", "Category distribution grid generated (all vars x 4 cycles).")

    # ---------------------------------------------------------------- Method 5
    def method5_activity(self) -> None:
        self._section("Method 5: Activity Crosswalk Verification")
        heatmap_rows = []
        for c in CYCLES:
            df = self.epi_s2.get(c)
            if df is None:
                continue
            unmapped = df["occACT"].isna().mean() * 100 if "occACT" in df.columns else 100
            level = "pass" if unmapped < 2.0 else "fail"
            self._rec(level, f"{c} -- unmapped occACT rate: {unmapped:.2f}%")
            if "occACT" in df.columns and "duration" in df.columns:
                dist = df.groupby("occACT")["duration"].sum() / df["duration"].sum() * 100
                dist.name = str(c)
                heatmap_rows.append(dist)

        if heatmap_rows:
            heat_df = pd.DataFrame(heatmap_rows).fillna(0).T
            heat_df.index = [ACT_LABELS.get(int(i), str(i)) for i in heat_df.index]
            _apply_dark()
            fig, ax = plt.subplots(figsize=(10, 7))
            sns.heatmap(heat_df, ax=ax, cmap="YlGnBu", annot=True, fmt=".1f",
                        linewidths=0.4, linecolor="#1e1e2e",
                        cbar_kws={"label": "% of total diary time"},
                        annot_kws={"size": 9})
            ax.set_title("Time-Weighted Activity Distribution (%) -- 14 Categories x 4 Cycles",
                         fontsize=13, pad=10)
            ax.set_xlabel("Survey Cycle"); ax.set_ylabel("")
            ax.tick_params(axis="y", rotation=0, labelsize=9)
            self.plots_b64["5_activity"] = _b64(fig)
            self._rec("pass", "Activity heatmap generated.")

    # ---------------------------------------------------------------- Method 6
    def method6_location(self) -> None:
        self._section("Method 6: Location & Co-Presence Verification (+ AT_WORK)")
        _apply_dark()
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        at_home_rates: list = []
        at_work_rates: list = []

        for c in CYCLES:
            df = self.epi_s2.get(c)
            if df is None:
                at_home_rates.append(0.0)
                at_work_rates.append(0.0)
                continue
            if "AT_HOME" in df.columns:
                r = df["AT_HOME"].mean() * 100
                at_home_rates.append(r)
                level = "pass" if 45 <= r <= 80 else "warn"
                self._rec(level, f"{c} -- AT_HOME rate: {r:.1f}% (episode-level)")
            else:
                at_home_rates.append(0.0)
                self._rec("fail", f"{c} -- AT_HOME column missing.")

            if "AT_WORK" in df.columns:
                rw = df["AT_WORK"].mean() * 100
                at_work_rates.append(rw)
                # Expect single-digit %; 2022 will look suppressed due to WFH coding
                level = "pass" if 2 <= rw <= 20 else "warn"
                wfh_note = "; suppressed by WFH coding (LOCATION=3300=home)" if c == 2022 else ""
                self._rec(level, f"{c} -- AT_WORK rate: {rw:.1f}% (episode-level{wfh_note})")
            else:
                at_work_rates.append(0.0)
                self._rec("fail", f"{c} -- AT_WORK column missing.")

        x = np.arange(len(CYCLES))
        # Left: AT_HOME
        ax = axes[0]
        bars = ax.bar(x, at_home_rates, color=CYCLE_COLORS, edgecolor="#1e1e2e", linewidth=0.8, width=0.55)
        ax.set_xticks(x); ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_ylim(0, 100); ax.set_ylabel("AT_HOME Rate (%)")
        ax.axhline(55, color="#89b4fa", linestyle="--", linewidth=1, label="~55% lower")
        ax.axhline(70, color="#a6e3a1", linestyle="--", linewidth=1, label="~70% upper")
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_title("AT_HOME Rate (%) per Cycle -- Expected 55-70%", fontsize=12)
        for bar, val in zip(bars, at_home_rates):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")

        # Right: AT_WORK
        ax2 = axes[1]
        bars2 = ax2.bar(x, at_work_rates, color=CYCLE_COLORS, edgecolor="#1e1e2e", linewidth=0.8, width=0.55)
        ax2.set_xticks(x); ax2.set_xticklabels([str(c) for c in CYCLES])
        ax2.set_ylim(0, 25); ax2.set_ylabel("AT_WORK Rate (%)")
        ax2.axhline(6, color="#89b4fa", linestyle="--", linewidth=1, label="~6% lower")
        ax2.axhline(12, color="#a6e3a1", linestyle="--", linewidth=1, label="~12% upper")
        ax2.legend(fontsize=8); ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2.set_title("AT_WORK Rate (%) per Cycle\n(2022 lower due to WFH coding)", fontsize=12)
        for bar, val in zip(bars2, at_work_rates):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                     f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")

        fig.suptitle("Location Channel Rates -- AT_HOME and AT_WORK", fontsize=13, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["6_location"] = _b64(fig)

        # occPRE=2 share on episode files (raw share before binary coercion)
        _apply_dark()
        fig2, ax3 = plt.subplots(figsize=(9, 4))
        occpre2_rates = []
        for c in CYCLES:
            df = self.epi_s2.get(c)
            if df is not None and "occPRE" in df.columns:
                r2 = (df["occPRE"] == 2).mean() * 100
                occpre2_rates.append(r2)
            else:
                occpre2_rates.append(0.0)
        bars3 = ax3.bar(x, occpre2_rates, color=CYCLE_COLORS, edgecolor="#1e1e2e", linewidth=0.8, width=0.55)
        ax3.set_xticks(x); ax3.set_xticklabels([str(c) for c in CYCLES])
        ax3.set_ylim(0, 20); ax3.set_ylabel("occPRE == 2 share (%)")
        ax3.set_title("occPRE = 2 (workplace) Episode Share per Cycle", fontsize=12)
        ax3.yaxis.grid(True, linestyle="--", alpha=0.3)
        for bar, val in zip(bars3, occpre2_rates):
            ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                     f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")
        self.plots_b64["6b_occpre2"] = _b64(fig2)

    # ---------------------------------------------------------------- Method 7
    def method7_metadata(self) -> None:
        self._section("Method 7: Metadata Flag Audit")
        expected_flags = {
            "CYCLE_YEAR":   {c: c for c in CYCLES},
            "COLLECT_MODE": {2005: 0, 2010: 0, 2015: 0, 2022: 1},
            "TUI_10_AVAIL": {2005: 0, 2010: 0, 2015: 1, 2022: 1},
        }
        for flag, expected_vals in expected_flags.items():
            for c in CYCLES:
                df = self.main_s2.get(c)
                if df is None or flag not in df.columns:
                    self._rec("fail", f"{c} -- missing flag column '{flag}'")
                    continue
                actual = df[flag].iloc[0]
                exp = expected_vals[c]
                if actual == exp:
                    self._rec("pass", f"{c} {flag} = {actual}")
                else:
                    self._rec("fail", f"{c} {flag}: expected {exp}, got {actual}")

        for c in CYCLES:
            df = self.main_s2.get(c)
            if df is None:
                continue
            if c in (2005, 2010):
                if "SURVMNTH" in df.columns and df["SURVMNTH"].isna().all():
                    self._rec("pass", f"{c} SURVMNTH is all NaN (correct).")
                elif "SURVMNTH" not in df.columns:
                    self._rec("warn", f"{c} SURVMNTH column absent.")
                else:
                    self._rec("fail", f"{c} SURVMNTH should be all NaN but has values.")
            else:
                if "SURVMNTH" in df.columns and df["SURVMNTH"].notna().any():
                    self._rec("pass", f"{c} SURVMNTH has values (correct).")
                else:
                    self._rec("warn", f"{c} SURVMNTH appears all NaN (check data).")

    # ---------------------------------------------------------------- Method 8
    def method8_diary(self) -> None:
        self._section("Method 8: Diary Closure QA")
        _apply_dark()
        fig, axes = plt.subplots(1, 2, figsize=(13, 4))
        pass_rates = []
        episode_counts_all = []

        for c in CYCLES:
            df = self.epi_s2.get(c)
            if df is None or "DIARY_VALID" not in df.columns:
                pass_rates.append(0.0)
                continue
            rate = df["DIARY_VALID"].mean() * 100
            pass_rates.append(rate)
            level = "pass" if rate >= 95 else "fail"
            self._rec(level, f"{c} -- DIARY_VALID pass rate: {rate:.1f}%")
            if "occID" in df.columns:
                ep_counts = df.groupby("occID").size().reset_index(name="n")
                ep_counts["Cycle"] = str(c)
                episode_counts_all.append(ep_counts)

        ax = axes[0]
        colors_dr = ["#a6e3a1" if r >= 95 else "#f38ba8" for r in pass_rates]
        bars = ax.bar([str(c) for c in CYCLES], pass_rates, color=colors_dr,
                      edgecolor="#1e1e2e", linewidth=0.8, width=0.55)
        ax.axhline(95, color="#89b4fa", linestyle="--", linewidth=1.2, label="95% threshold")
        ax.set_ylim(0, 105); ax.set_ylabel("DIARY_VALID Pass Rate (%)")
        ax.set_title("Diary Closure Pass Rate per Cycle", fontsize=12)
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        for bar, val in zip(bars, pass_rates):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 1, f"{val:.1f}%",
                    ha="center", fontsize=10, fontweight="bold")

        ax2 = axes[1]
        if episode_counts_all:
            combined = pd.concat(episode_counts_all, ignore_index=True)
            palette = {str(c): col for c, col in zip(CYCLES, CYCLE_COLORS)}
            sns.boxplot(data=combined, x="Cycle", y="n", hue="Cycle",
                        palette=palette, linewidth=1.2, fliersize=2,
                        legend=False, ax=ax2)
        ax2.set_title("Episodes per Respondent Distribution", fontsize=12)
        ax2.set_xlabel("Survey Cycle"); ax2.set_ylabel("Episode Count")
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        fig.suptitle("Diary Integrity QA", fontsize=14, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["8_diary"] = _b64(fig)

    # ---------------------------------------------------------------- Method 9
    def method9_regression(self) -> None:
        self._section("Method 9: Pre/Post Regression Check")
        _apply_dark()

        fig, axes = plt.subplots(1, 4, figsize=(14, 5), sharey=False)
        fig.suptitle("Survey Weight (WGHT_PER) -- Step 1 vs Step 2", fontsize=13, fontweight="bold")
        for idx, c in enumerate(CYCLES):
            ax = axes[idx]
            m1 = self.main_s1.get(c)
            m2 = self.main_s2.get(c)
            if m1 is None or m2 is None:
                continue
            wt_s1 = pd.to_numeric(m1["WGHT_PER"], errors="coerce").dropna() if "WGHT_PER" in m1.columns else pd.Series(dtype=float)
            wt_s2 = pd.to_numeric(m2["WGHT_PER"], errors="coerce").dropna() if "WGHT_PER" in m2.columns else pd.Series(dtype=float)
            data = pd.DataFrame({
                "Weight": pd.concat([wt_s1, wt_s2], ignore_index=True),
                "Source": ["Step 1"] * len(wt_s1) + ["Step 2"] * len(wt_s2),
            })
            sns.boxplot(data=data, x="Source", y="Weight", hue="Source",
                        palette={"Step 1": "#89b4fa", "Step 2": "#a6e3a1"},
                        linewidth=1.0, fliersize=2, legend=False, ax=ax)
            ax.set_title(str(c), fontsize=12, color=CYCLE_COLORS[idx])
            ax.set_xlabel(""); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
            if len(wt_s1) > 0 and len(wt_s2) > 0:
                mean_diff = abs(wt_s1.mean() - wt_s2.mean())
                ax.text(0.5, 0.97, f"dmean={mean_diff:.0f}", transform=ax.transAxes,
                        ha="center", va="top", fontsize=9, color="#cdd6f4",
                        bbox=dict(fc="#313244", ec="#555", pad=3))
                level = "pass" if mean_diff < 1.0 else "warn"
                self._rec(level, f"{c} Weight delta-mean = {mean_diff:.4f}")
        plt.tight_layout()
        self.plots_b64["9a_weights"] = _b64(fig)

        # NaN heatmap for key harmonized columns
        _apply_dark()
        key_cols = ["SEX", "AGEGRP", "MARSTH", "HHSIZE", "LFTAG", "KOL", "HRSWRK", "TOTINC", "NOCS", "NAICS"]
        nan_rows = []
        for c in CYCLES:
            m2 = self.main_s2.get(c)
            if m2 is None:
                continue
            for col in key_cols:
                if col in m2.columns:
                    nan_rows.append({"Cycle": str(c), "Column": col,
                                     "NaN%": round(m2[col].isna().mean() * 100, 1)})
        if nan_rows:
            pivot = pd.DataFrame(nan_rows).pivot(index="Column", columns="Cycle", values="NaN%").fillna(0)
            fig2, ax2 = plt.subplots(figsize=(9, 5))
            sns.heatmap(pivot, ax=ax2, cmap="YlOrRd", linewidths=0.4, linecolor="#1e1e2e",
                        annot=True, fmt=".1f", cbar_kws={"label": "% Missing"},
                        annot_kws={"size": 9})
            ax2.set_title("NaN % per Column x Cycle (Harmonized Step 2 Main Files)", fontsize=12, pad=10)
            ax2.set_xlabel("Survey Cycle"); ax2.set_ylabel("")
            ax2.tick_params(axis="x", rotation=0); ax2.tick_params(axis="y", rotation=0, labelsize=9)
            self.plots_b64["9b_nan_heatmap"] = _b64(fig2)
            self._rec("pass", "Regression NaN heatmap generated.")

    # --------------------------------------------------------------- Method 10
    def method10_copresence(self) -> None:
        self._section("Method 10: Co-Presence Quality Report")
        _apply_dark()

        fig, ax = plt.subplots(figsize=(13, 5))
        x = np.arange(len(COPRE_COLS))
        width = 0.18
        for i, c in enumerate(CYCLES):
            df = self.epi_s2.get(c)
            rates = []
            for col in COPRE_COLS:
                if df is not None and col in df.columns:
                    valid_mask = df[col].notna()
                    total_valid = valid_mask.sum()
                    rate = 100.0 * (df.loc[valid_mask, col] == 1).sum() / total_valid if total_valid else 0.0
                else:
                    rate = 0.0
                rates.append(rate)
            ax.bar(x + (i - 1.5) * width, rates, width, label=str(c),
                   color=CYCLE_COLORS[i], edgecolor="#1e1e2e", linewidth=0.5)
        ax.set_xticks(x); ax.set_xticklabels(COPRE_COLS, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("% of non-NaN episodes with presence = 1")
        ax.set_ylim(0, 100); ax.legend(title="Cycle", fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_title("Co-Presence Prevalence by Category and Cycle", fontsize=12)
        self.plots_b64["10a_copre_prevalence"] = _b64(fig)

        for c in CYCLES:
            df = self.epi_s2.get(c)
            if df is None or "Alone" not in df.columns:
                self._rec("warn", f"{c} -- 'Alone' column missing.")
                continue
            valid = df["Alone"].dropna()
            alone_pct = 100.0 * (valid == 1).mean()
            level = "pass" if 10 <= alone_pct <= 60 else "warn"
            self._rec(level, f"{c} -- Alone prevalence: {alone_pct:.1f}% (expected 10-60%)")

        for c in (2005, 2010):
            df = self.epi_s2.get(c)
            if df is not None and "colleagues" in df.columns:
                all_nan = df["colleagues"].isna().all()
                level = "pass" if all_nan else "fail"
                self._rec(level, f"{c} -- colleagues column all-NaN: {all_nan}")

    # --------------------------------------------------------------- Method 11 (NEW)
    def method11_telework(self) -> None:
        self._section("Method 11 (Leg-2): TELEWORK Rate per Cycle")
        _apply_dark()

        instruments = {
            2005: "MAR_Q190\nusual Y/N",
            2010: "MAR_Q190\nusual Y/N",
            2015: "WTI_130\ndiary-day*",
            2022: "TLWK_01A\nusual Y/N",
        }

        tw_rates = []
        tw_labels = []
        tw_colors_bar = []

        for c in CYCLES:
            df = self.main_s2.get(c)
            if df is not None and "TELEWORK" in df.columns:
                non_nan = df["TELEWORK"].notna().sum()
                if non_nan > 0:
                    rate = df["TELEWORK"].dropna().mean() * 100
                    tw_rates.append(rate)
                    tw_labels.append(f"{rate:.1f}%\n{instruments.get(c, '')}")
                    tw_colors_bar.append(CYCLE_COLORS[CYCLES.index(c)])
                    level = "warn" if c == 2015 else "pass"
                    note = " [DIARY-DAY measure -- not comparable to 2010/2022 usual Y/N]" if c == 2015 else ""
                    self._rec(level, f"{c} -- TELEWORK rate: {rate:.1f}% (n={non_nan:,}){note}")
                else:
                    tw_rates.append(0.0)
                    tw_labels.append("0.0%\n(all NaN)")
                    tw_colors_bar.append("#585b70")
                    self._rec("warn", f"{c} -- TELEWORK: all NaN (expected non-NaN for this cycle)")
            elif df is not None:
                tw_rates.append(0.0)
                tw_labels.append("col\nmissing")
                tw_colors_bar.append("#f38ba8")
                self._rec("fail", f"{c} -- TELEWORK column absent from Step-2 main file")
            else:
                tw_rates.append(0.0)
                tw_labels.append("no data")
                tw_colors_bar.append("#585b70")

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(CYCLES))
        bars = ax.bar(x, tw_rates, color=tw_colors_bar, edgecolor="#1e1e2e",
                      linewidth=0.8, width=0.55)
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_ylim(0, 55)
        ax.set_ylabel("TELEWORK rate (% of non-NaN respondents)")
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_title(
            "TELEWORK Rate per Cycle\n"
            "(* 2015 WTI_130 = diary-day measure; NOT comparable to 2010/2022 usual Y/N)",
            fontsize=12,
        )
        for bar, val, label in zip(bars, tw_rates, tw_labels):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    label, ha="center", fontsize=9, color="#cdd6f4")

        # Annotate 2015 diary-day flag
        ax.text(x[1], tw_rates[1] + 5 if len(tw_rates) > 1 else 5, "",
                ha="center", fontsize=9)

        self.plots_b64["11_telework"] = _b64(fig)

    # --------------------------------------------------------------- Method 12 (NEW)
    def method12_nocs_naics(self) -> None:
        self._section("Method 12 (Leg-2): NOCS and NAICS Coverage After Unification")
        _apply_dark()

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        nocs_cov = []
        naics_cov = []
        nocs_cats = []
        naics_cats = []

        for c in CYCLES:
            df = self.main_s2.get(c)
            if df is None:
                nocs_cov.append(0.0); naics_cov.append(0.0)
                nocs_cats.append(0); naics_cats.append(0)
                continue

            if "NOCS" in df.columns:
                cov = df["NOCS"].notna().mean() * 100
                n_cats = df["NOCS"].dropna().nunique()
                nocs_cov.append(cov); nocs_cats.append(n_cats)
                level = "pass" if cov > 10 and n_cats >= 3 else "warn"
                self._rec(level, f"{c} -- NOCS: {cov:.1f}% non-NaN, {n_cats} distinct buckets")
            else:
                nocs_cov.append(0.0); nocs_cats.append(0)
                self._rec("fail", f"{c} -- NOCS column absent after Step-2 unification")

            if "NAICS" in df.columns:
                cov = df["NAICS"].notna().mean() * 100
                n_cats = df["NAICS"].dropna().nunique()
                naics_cov.append(cov); naics_cats.append(n_cats)
                level = "pass" if cov > 10 and n_cats >= 5 else "warn"
                self._rec(level, f"{c} -- NAICS: {cov:.1f}% non-NaN, {n_cats} distinct buckets")
            else:
                naics_cov.append(0.0); naics_cats.append(0)
                self._rec("fail", f"{c} -- NAICS column absent after Step-2 unification")

            # [Leg-2 delta F] WORK_SCHEDULE coverage (shift type; 1-9 categories)
            if "WORK_SCHEDULE" in df.columns:
                ws_cov = df["WORK_SCHEDULE"].notna().mean() * 100
                ws_cats = df["WORK_SCHEDULE"].dropna().nunique()
                bad = df["WORK_SCHEDULE"].dropna()
                oor = int((~bad.isin(range(1, 10))).sum())
                level = "pass" if ws_cov > 10 and oor == 0 else "warn"
                self._rec(level, f"{c} -- WORK_SCHEDULE: {ws_cov:.1f}% non-NaN, {ws_cats} distinct (1-9), out-of-range={oor}")
            else:
                self._rec("fail", f"{c} -- WORK_SCHEDULE column absent after Step-2 harmonization")

        x = np.arange(len(CYCLES))

        # Left: NOCS coverage
        ax = axes[0]
        bars = ax.bar(x, nocs_cov, color=CYCLE_COLORS, edgecolor="#1e1e2e",
                      linewidth=0.8, width=0.55)
        ax.set_xticks(x); ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_ylim(0, 100); ax.set_ylabel("Non-NaN coverage (%)")
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_title("NOCS (Occupation) Coverage After Unification", fontsize=12)
        for bar, val, cats in zip(bars, nocs_cov, nocs_cats):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.1f}%\n({cats} cats)", ha="center", fontsize=9)

        # Right: NAICS coverage
        ax2 = axes[1]
        bars2 = ax2.bar(x, naics_cov, color=CYCLE_COLORS, edgecolor="#1e1e2e",
                        linewidth=0.8, width=0.55)
        ax2.set_xticks(x); ax2.set_xticklabels([str(c) for c in CYCLES])
        ax2.set_ylim(0, 100); ax2.set_ylabel("Non-NaN coverage (%)")
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2.set_title("NAICS (Industry) Coverage After Unification\n(>=90 sentinel codes set to NaN)", fontsize=12)
        for bar, val, cats in zip(bars2, naics_cov, naics_cats):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f"{val:.1f}%\n({cats} cats)", ha="center", fontsize=9)

        fig.suptitle("Leg-2 Office Column Coverage (NOCS + NAICS) -- Step 2 Main Files",
                     fontsize=13, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["12_nocs_naics"] = _b64(fig)

    # ---------------------------------------------------------------- HTML
    def export_html(self) -> None:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0
        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        chart_titles = {
            "4_categories":        "Chart 4 -- Demographic Category Distributions (all vars x 4 cycles)",
            "5_activity":          "Chart 5 -- Activity Code Crosswalk Heatmap (14 categories x 4 cycles)",
            "6_location":          "Chart 6 -- AT_HOME and AT_WORK Rates per Cycle",
            "6b_occpre2":          "Chart 6b -- occPRE = 2 Episode Share per Cycle",
            "8_diary":             "Chart 8 -- Diary Closure Pass Rate & Episode Distribution",
            "9a_weights":          "Chart 9a -- Survey Weight: Step 1 vs Step 2 Box Plots",
            "9b_nan_heatmap":      "Chart 9b -- NaN % per Harmonized Column",
            "10a_copre_prevalence":"Chart 10a -- Co-Presence Prevalence by Category and Cycle",
            "11_telework":         "Chart 11 -- TELEWORK Rate per Cycle (instrument-annotated)",
            "12_nocs_naics":       "Chart 12 -- NOCS and NAICS Coverage After Unification",
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

        def _badge_list(level):
            icon = "PASS" if level == "pass" else ("FAIL" if level == "fail" else "WARN")
            css_cls = level
            items = self.results[level]
            if not items:
                return f"<li class='badge {css_cls}'>[{icon}] None</li>"
            return "".join(f"<li class='badge {css_cls}'>[{icon}] {m}</li>" for m in items)

        nav_links = "".join(
            f'<a href="#{k}">{v.split("--")[0].strip()}</a>'
            for k, v in chart_titles.items()
            if k in self.plots_b64
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Step 2 Leg-2 -- Harmonization Validation Report</title>
  <style>
    :root {{
      --bg:#1e1e2e; --surface:#2a2a3e; --surface2:#313244;
      --accent:#89b4fa; --green:#a6e3a1; --yellow:#f9e2af;
      --red:#f38ba8; --text:#cdd6f4; --subtext:#a6adc8; --border:#45475a;
    }}
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }}
    header {{ background:var(--surface); border-bottom:1px solid var(--border); padding:18px 32px;
              display:flex; align-items:center; justify-content:space-between;
              position:sticky; top:0; z-index:100; }}
    header h1 {{ font-size:1.25rem; color:var(--accent); }}
    header p  {{ font-size:0.8rem; color:var(--subtext); }}
    nav {{ background:var(--surface2); border-bottom:1px solid var(--border);
           padding:8px 32px; display:flex; gap:20px; flex-wrap:wrap; }}
    nav a {{ color:var(--subtext); text-decoration:none; font-size:0.82rem;
             padding:4px 10px; border-radius:6px; transition:background 0.2s,color 0.2s; }}
    nav a:hover {{ background:var(--surface); color:var(--accent); }}
    main {{ max-width:1200px; margin:0 auto; padding:30px 28px; }}
    .scorecard {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:36px; }}
    .score-card {{ background:var(--surface); border:1px solid var(--border);
                   border-radius:12px; padding:20px 16px; text-align:center; }}
    .score-card .number {{ font-size:2.4rem; font-weight:700; }}
    .score-card .label  {{ font-size:0.8rem; color:var(--subtext); margin-top:4px; }}
    .score-card.ok   .number {{ color:var(--green); }}
    .score-card.warn .number {{ color:var(--yellow); }}
    .score-card.fail .number {{ color:var(--red); }}
    .score-card.pct  .number {{ color:var(--accent); font-size:2.0rem; }}
    .findings {{ margin-bottom:36px; }}
    .findings h2 {{ font-size:1.05rem; margin-bottom:12px; color:var(--accent); }}
    .badge-list {{ list-style:none; display:flex; flex-direction:column; gap:6px; }}
    .badge {{ padding:8px 14px; border-radius:8px; font-size:0.85rem; line-height:1.4; }}
    .badge.pass {{ background:#1c2e22; border:1px solid #2d5a35; color:var(--green); }}
    .badge.warn {{ background:#2e2a1c; border:1px solid #5a4e1f; color:var(--yellow); }}
    .badge.fail {{ background:#2e1c1e; border:1px solid #5a2428; color:var(--red); }}
    .chart-section {{ background:var(--surface); border:1px solid var(--border);
                      border-radius:14px; padding:24px; margin-bottom:28px; }}
    .chart-section h2 {{ font-size:1.0rem; color:var(--accent); margin-bottom:16px;
                         padding-bottom:8px; border-bottom:1px solid var(--border); }}
    .chart-wrap {{ text-align:center; }}
    .chart-wrap img {{ max-width:100%; height:auto; border-radius:8px; }}
    .pipeline-section {{ background:var(--surface); border:1px solid var(--border);
                         border-radius:14px; padding:24px; margin-bottom:28px; }}
    .pipeline-section h2 {{ font-size:1.0rem; color:var(--accent); margin-bottom:16px;
                             padding-bottom:8px; border-bottom:1px solid var(--border); }}
    .pipeline-pre {{ font-family:'Courier New',Consolas,monospace; font-size:0.78rem;
                     color:var(--subtext); white-space:pre; overflow-x:auto;
                     background:var(--surface2); padding:16px; border-radius:8px;
                     border:1px solid var(--border); line-height:1.5; }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem;
              color:var(--subtext); border-top:1px solid var(--border); margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GSS Step 2 Leg-2 -- Harmonization Validation Report</h1>
      <p>Post-harmonization quality check (Residential + Office channel) across cycles 2005/2010/2015/2022</p>
    </div>
  </header>
  <nav><a href="#pipeline-overview">Pipeline Overview</a>{nav_links}</nav>
  <main>
    <section class="pipeline-section" id="pipeline-overview">
      <h2>Pipeline Overview -- Step 2: Data Harmonization (Leg-2)</h2>
      <pre class="pipeline-pre">{STEP2_OVERVIEW}</pre>
    </section>

    <div class="scorecard">
      <div class="score-card ok"><div class="number">{n_pass}</div><div class="label">Checks Passed</div></div>
      <div class="score-card warn"><div class="number">{n_warn}</div><div class="label">Warnings</div></div>
      <div class="score-card fail"><div class="number">{n_fail}</div><div class="label">Failures</div></div>
      <div class="score-card pct"><div class="number">{pct_ok}%</div><div class="label">Pass Rate</div></div>
    </div>
    <div class="findings"><h2>Failures</h2><ul class="badge-list">{_badge_list("fail")}</ul></div>
    <div class="findings"><h2>Warnings</h2><ul class="badge-list">{_badge_list("warn")}</ul></div>
    <div class="findings"><h2>Passed</h2><ul class="badge-list">{_badge_list("pass")}</ul></div>
    {charts_html}
  </main>
  <footer>Occupancy Modeling Pipeline (Leg-2) · Step 2 Harmonization Validation · Generated {today}</footer>
</body>
</html>
"""
        out_path = os.path.join(OUTPUT_DIR, "step2_validation_report.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML report saved to: {out_path}")

    def export_txt(self) -> None:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0
        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            f"GSS Step 2 Leg-2 Harmonization Validation Report",
            f"Generated: {today}",
            f"",
            f"TALLY: PASS {n_pass} / WARN {n_warn} / FAIL {n_fail} / TOTAL {total} ({pct_ok}% pass rate)",
            f"",
        ] + self._console_lines

        out_path = os.path.join(OUTPUT_DIR, "step2_validation_report.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"TXT report saved to:  {out_path}")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    v = GSSHarmonizationValidator2Split()
    v.run_all()
    n_p = len(v.results["pass"])
    n_w = len(v.results["warn"])
    n_f = len(v.results["fail"])
    print(f"\n=== VALIDATION COMPLETE: PASS {n_p} / WARN {n_w} / FAIL {n_f} ===")
    if n_f > 0:
        sys.exit(1)
