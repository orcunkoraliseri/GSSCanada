"""
02_harmonizeGSS_val.py

Validation script for Step 2 of the Occupancy Modeling Pipeline.
Mirrors the style and structure of 01_readingGSS_val.py.

Checks:
  1. Unified Schema Audit
  2. Row Count Preservation
  3. Sentinel Value Elimination
  4. Category Recoding Verification (with full stacked-bar grid, all variables × 4 cycles)
  5. Activity Crosswalk Verification
  6. Location & Co-Presence Verification
  7. Metadata Flag Audit
  8. Diary Closure QA
  9. Pre/Post Regression Check (with plots)
"""

import io
import os
import base64

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

INPUT_DIR = "outputs/"
OUTPUT_DIR = "outputs_step2/"
CYCLES = [2005, 2010, 2015, 2022]

SENTINEL_MAP: dict[str, set[int]] = {
    "COW": {97, 98, 99},
    "KOL": {98, 99},
    "TOTINC": {98, 99},
    "ATTSCH": {98, 99},
    "HRSWRK": {96, 97, 98, 99},
    "NOCS": {96, 97, 98, 99},
    "LFTAG": {8, 9, 97, 98, 99},
    "MARSTH": {8, 9, 99},
    "MODE": {99},
}

# Step-1 column names for pre-harmonization comparison
STEP1_WEIGHT_COL: dict[int, str] = {
    2005: "WGHT_PER",
    2010: "WGHT_PER",
    2015: "WGHT_PER",
    2022: "WGHT_PER",
}
STEP1_SEX_COL: dict[int, str] = {2005: "SEX", 2010: "SEX", 2015: "SEX", 2022: "SEX"}

# Harmonized Main variables to show in the stacked-bar grid
HARM_VARS: dict[str, dict] = {
    "SEX": {"expected": {1, 2}},
    "AGEGRP": {"expected": set(range(1, 8))},
    "MARSTH": {"expected": set(range(1, 7))},
    "HHSIZE": {"expected": set(range(1, 6))},
    "CMA": {"expected": {1, 2, 3}},
    "LFTAG": {"expected": set(range(1, 6))},
    "HRSWRK": {"expected": None},
    "KOL": {"expected": None},
    "MODE": {"expected": set(range(1, 7))},
    "TOTINC": {"expected": None},
}

ACT_LABELS: dict[int, str] = {
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
    "axes.facecolor": "#2a2a3e",
    "axes.edgecolor": "#555",
    "axes.labelcolor": "#cdd6f4",
    "xtick.color": "#cdd6f4",
    "ytick.color": "#cdd6f4",
    "text.color": "#cdd6f4",
    "grid.color": "#444",
    "legend.facecolor": "#2a2a3e",
    "legend.edgecolor": "#555",
    "font.family": "sans-serif",
    "font.size": 11,
}
CYCLE_COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]


def _apply_dark() -> None:
    """Apply dark-theme rcParams."""
    plt.rcParams.update(_DARK)


def _b64(fig: plt.Figure) -> str:
    """Save a figure to a base64 PNG string and close it."""
    buf = io.BytesIO()
    fig.savefig(
        buf, format="png", dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor()
    )
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


STEP2_OVERVIEW = """\
╔══════════════════════════════════════════════════════════════════════════╗
║  STEP 2 — DATA HARMONIZATION (per cycle: 2005/2010/2015/2022)          ║
║                                                                          ║
║  Category recoding (SEX, MARSTH, AGEGRP, LFTAG, ATTSCH, PR, CMA)      ║
║  Missing value alignment (96/97/98/99 → NaN)                           ║
║                                                                          ║
║  ⚠ Critical harmonization flags:                                        ║
║  • TOTINC regime break: self-reported (2005–2015) / CRA-linked (2022)  ║
║  • TUI_01 crosswalk: 2022 hierarchical tree → 63-code flat scheme      ║
║  • COLLECT_MODE flag: 0=CATI (2005/2010) / 1=EQ (2022)                ║
║  • TUI_10_AVAIL flag: 0=absent (2005/2010) / 1=present (2015/2022)    ║
║  • Bootstrap flag: MEAN_BS (2005/2010) / STANDARD_BS (2015/2022)      ║
║  • DIARY_VALID QA: assert sum(DURATION per occID) == 1440 min          ║
║  • CYCLE_YEAR + SURVYEAR appended as longitudinal labels               ║
║                                                                          ║
║  Output: 4 harmonized cycle pairs (Main + Episode), identical schema   ║
╚══════════════════════════════════════════════════════════════════════════╝"""


class GSSHarmonizationValidator:
    """Validation class mirroring Step 1's GSSValidator structure."""

    def __init__(self) -> None:
        """Load Step 1 and Step 2 CSVs for all cycles."""
        self.main_s1: dict[int, pd.DataFrame] = {}
        self.epi_s1: dict[int, pd.DataFrame] = {}
        self.main_s2: dict[int, pd.DataFrame] = {}
        self.epi_s2: dict[int, pd.DataFrame] = {}
        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}

        for c in CYCLES:
            self.main_s1[c] = pd.read_csv(f"{INPUT_DIR}main_{c}.csv", low_memory=False)
            self.epi_s1[c] = pd.read_csv(
                f"{INPUT_DIR}episode_{c}.csv", low_memory=False
            )
            self.main_s2[c] = pd.read_csv(f"{OUTPUT_DIR}main_{c}.csv", low_memory=False)
            self.epi_s2[c] = pd.read_csv(
                f"{OUTPUT_DIR}episode_{c}.csv", low_memory=False
            )

    # ------------------------------------------------------------------ helpers
    def _rec(self, level: str, msg: str) -> None:
        """Record and print a check result."""
        self.results[level].append(msg)
        icon = "✅" if level == "pass" else ("❌" if level == "fail" else "⚠️")
        print(f"{icon} {msg}")

    def run_all(self) -> None:
        """Execute all 9 validation methods and export HTML."""
        _apply_dark()
        print("=== Step 2 Harmonization Validation ===\n")
        self.method1_schema()
        self.method2_rowcounts()
        self.method3_sentinels()
        self.method4_categories()
        self.method5_activity()
        self.method6_location()
        self.method7_metadata()
        self.method8_diary()
        self.method9_regression()
        self.export_html()

    # ---------------------------------------------------------------- Method 1
    def method1_schema(self) -> None:
        """Unified Schema Audit."""
        print("\n--- Method 1: Unified Schema Audit ---")
        main_cols = {c: set(self.main_s2[c].columns) for c in CYCLES}
        epi_cols = {c: set(self.epi_s2[c].columns) for c in CYCLES}

        if all(main_cols[c] == main_cols[2005] for c in CYCLES):
            self._rec("pass", "All 4 Main files share identical column sets.")
        else:
            diffs = {
                c: main_cols[c].symmetric_difference(main_cols[2005]) for c in CYCLES
            }
            self._rec("fail", f"Main column mismatch detected: {diffs}")

        if all(epi_cols[c] == epi_cols[2005] for c in CYCLES):
            self._rec("pass", "All 4 Episode files share identical column sets.")
        else:
            self._rec("fail", "Episode column mismatch across cycles.")

        expected = [
            "occID",
            "AGEGRP",
            "SEX",
            "MARSTH",
            "HHSIZE",
            "PR",
            "CMA",
            "LFTAG",
            "HRSWRK",
            "KOL",
            "MODE",
            "TOTINC",
            "WGHT_PER",
            "DDAY",
            "SURVMNTH",
            "CYCLE_YEAR",
            "SURVYEAR",
            "COLLECT_MODE",
            "TUI_10_AVAIL",
            "BS_TYPE",
            "TOTINC_SOURCE",
        ]
        missing = [col for col in expected if col not in main_cols[2005]]
        if not missing:
            self._rec("pass", f"All {len(expected)} expected Main columns present.")
        else:
            self._rec("fail", f"Missing expected columns: {missing}")

    # ---------------------------------------------------------------- Method 2
    def method2_rowcounts(self) -> None:
        """Row Count Preservation."""
        print("\n--- Method 2: Row Count Preservation ---")
        for c in CYCLES:
            m1, m2 = len(self.main_s1[c]), len(self.main_s2[c])
            e1, e2 = len(self.epi_s1[c]), len(self.epi_s2[c])
            if m1 == m2:
                self._rec("pass", f"{c} Main rows preserved: {m2:,}")
            else:
                self._rec("fail", f"{c} Main row count changed: {m1:,} → {m2:,}")
            if e1 == e2:
                self._rec("pass", f"{c} Episode rows preserved: {e2:,}")
            else:
                self._rec("fail", f"{c} Episode row count changed: {e1:,} → {e2:,}")

    # ---------------------------------------------------------------- Method 3
    def method3_sentinels(self) -> None:
        """Sentinel Value Elimination."""
        print("\n--- Method 3: Sentinel Value Elimination ---")
        for c in CYCLES:
            df = self.main_s2[c]
            found = []
            for col, sentinels in SENTINEL_MAP.items():
                if col in df.columns and df[col].isin(sentinels).any():
                    found.append(col)
            if not found:
                self._rec("pass", f"{c} — no sentinel residuals found.")
            else:
                self._rec("fail", f"{c} — sentinel values still present in: {found}")
            # Verify no over-nullification on key columns
            for key_col in ["WGHT_PER", "occID"]:
                if df[key_col].isna().any():
                    self._rec(
                        "warn", f"{c} — unexpected NaN in critical column '{key_col}'."
                    )

    # ---------------------------------------------------------------- Method 4
    def method4_categories(self) -> None:
        """Category Recoding Verification — stacked-bar grid (vars × cycles)."""
        print("\n--- Method 4: Category Recoding Verification ---")
        _apply_dark()
        n_vars = len(HARM_VARS)
        fig, axes = plt.subplots(n_vars, 4, figsize=(18, 3.0 * n_vars), sharey=False)
        fig.suptitle(
            "Harmonized Demographic Category Distributions (%) — Step 2 Main Files",
            fontsize=14,
            fontweight="bold",
            y=1.005,
        )

        CAT_CMAP = "tab20"
        NA_COLOR = "#45475a"

        for row_i, (var_name, meta) in enumerate(HARM_VARS.items()):
            expected = meta["expected"]
            for col_i, (c, cyc_color) in enumerate(zip(CYCLES, CYCLE_COLORS)):
                ax = axes[row_i, col_i]
                df = self.main_s2[c]

                if var_name not in df.columns:
                    ax.bar(
                        [0],
                        [1],
                        color=NA_COLOR,
                        hatch="///",
                        edgecolor="#888",
                        linewidth=0.6,
                    )
                    ax.text(
                        0,
                        0.5,
                        "N/A",
                        ha="center",
                        va="center",
                        fontsize=12,
                        color="#cdd6f4",
                        fontweight="bold",
                    )
                    ax.set_xlim(-0.5, 0.5)
                    ax.set_ylim(0, 1)
                    ax.set_xticks([])
                    ax.set_yticks([])
                else:
                    series = (
                        df[var_name]
                        .dropna()
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
                        ax.bar(
                            [0],
                            [val],
                            bottom=[bottom],
                            color=color,
                            edgecolor="#1e1e2e",
                            linewidth=0.4,
                            width=0.7,
                            label=str(cat),
                        )
                        if val >= 0.08:
                            ax.text(
                                0,
                                bottom + val / 2,
                                f"{cat}\n{val:.0%}",
                                ha="center",
                                va="center",
                                fontsize=7.5,
                                color="white",
                                fontweight="bold",
                            )
                        bottom += val
                    ax.set_xlim(-0.5, 0.5)
                    ax.set_ylim(0, 1.0)
                    ax.set_xticks([])
                    ax.yaxis.set_major_formatter(
                        plt.FuncFormatter(lambda v, _: f"{v:.0%}")
                    )
                    ax.yaxis.grid(True, linestyle="--", alpha=0.25)

                    # Flag unexpected values
                    if expected is not None:
                        unexpected = set(int(c) for c in cats) - expected
                        if unexpected:
                            self._rec(
                                "warn",
                                f"{c} {var_name}: unexpected values {unexpected}",
                            )

                if row_i == 0:
                    ax.set_title(
                        str(c), fontsize=13, fontweight="bold", color=cyc_color, pad=8
                    )
                if col_i == 0:
                    ax.set_ylabel(var_name, fontsize=10, labelpad=8)

        plt.subplots_adjust(hspace=0.35, wspace=0.08)
        self.plots_b64["4_categories"] = _b64(fig)
        self._rec("pass", "Category distribution grid generated (all vars × 4 cycles).")

    # ---------------------------------------------------------------- Method 5
    def method5_activity(self) -> None:
        """Activity Crosswalk Verification — 14-category × 4-cycle heatmap."""
        print("\n--- Method 5: Activity Crosswalk Verification ---")
        heatmap_rows = []
        for c in CYCLES:
            df = self.epi_s2[c]
            unmapped = df["occACT"].isna().mean() * 100
            if unmapped < 2.0:
                self._rec("pass", f"{c} — unmapped occACT rate: {unmapped:.2f}%")
            else:
                self._rec("fail", f"{c} — HIGH unmapped occACT rate: {unmapped:.2f}%")

            dist = df.groupby("occACT")["duration"].sum() / df["duration"].sum() * 100
            dist.name = str(c)
            heatmap_rows.append(dist)

        heat_df = pd.DataFrame(heatmap_rows).fillna(0).T
        heat_df.index = [ACT_LABELS.get(int(i), str(i)) for i in heat_df.index]

        _apply_dark()
        fig, ax = plt.subplots(figsize=(10, 7))
        sns.heatmap(
            heat_df,
            ax=ax,
            cmap="YlGnBu",
            annot=True,
            fmt=".1f",
            linewidths=0.4,
            linecolor="#1e1e2e",
            cbar_kws={"label": "% of total diary time"},
            annot_kws={"size": 9},
        )
        ax.set_title(
            "Time-Weighted Activity Distribution (%) — 14 Categories × 4 Cycles",
            fontsize=13,
            pad=10,
        )
        ax.set_xlabel("Survey Cycle")
        ax.set_ylabel("")
        ax.tick_params(axis="y", rotation=0, labelsize=9)
        self.plots_b64["5_activity"] = _b64(fig)
        self._rec("pass", "Activity heatmap generated.")

    # ---------------------------------------------------------------- Method 6
    def method6_location(self) -> None:
        """Location & Co-Presence Verification."""
        print("\n--- Method 6: Location & Co-Presence Verification ---")
        _apply_dark()
        fig, ax = plt.subplots(figsize=(9, 4))
        rates: list[float] = []
        for c in CYCLES:
            df = self.epi_s2[c]
            if "AT_HOME" in df.columns:
                r = df["AT_HOME"].mean() * 100
                rates.append(r)
                level = "pass" if 45 <= r <= 80 else "warn"
                self._rec(level, f"{c} — AT_HOME rate: {r:.1f}%")
            else:
                rates.append(0)
                self._rec("fail", f"{c} — AT_HOME column missing.")

        x = np.arange(len(CYCLES))
        bars = ax.bar(
            x, rates, color=CYCLE_COLORS, edgecolor="#1e1e2e", linewidth=0.8, width=0.55
        )
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_ylim(0, 100)
        ax.set_ylabel("AT_HOME Rate (%)")
        ax.axhline(
            55, color="#89b4fa", linestyle="--", linewidth=1, label="~55% lower bound"
        )
        ax.axhline(
            70, color="#a6e3a1", linestyle="--", linewidth=1, label="~70% upper bound"
        )
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_title("AT_HOME Rate (%) per Cycle — Expected Range 55–70%", fontsize=13)
        for bar, val in zip(bars, rates):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{val:.1f}%",
                ha="center",
                fontsize=10,
                fontweight="bold",
            )
        self.plots_b64["6_location"] = _b64(fig)

    # ---------------------------------------------------------------- Method 7
    def method7_metadata(self) -> None:
        """Metadata Flag Audit."""
        print("\n--- Method 7: Metadata Flag Audit ---")
        expected_flags: dict[str, dict[int, object]] = {
            "CYCLE_YEAR": {c: c for c in CYCLES},
            "COLLECT_MODE": {2005: 0, 2010: 0, 2015: 0, 2022: 1},
            "TUI_10_AVAIL": {2005: 0, 2010: 0, 2015: 1, 2022: 1},
        }
        for flag, expected_vals in expected_flags.items():
            for c in CYCLES:
                df = self.main_s2[c]
                if flag not in df.columns:
                    self._rec("fail", f"{c} — missing flag column '{flag}'")
                    continue
                actual = df[flag].iloc[0]
                exp = expected_vals[c]
                if actual == exp:
                    self._rec("pass", f"{c} {flag} = {actual} ✓")
                else:
                    self._rec("fail", f"{c} {flag}: expected {exp}, got {actual}")

        # SURVMNTH
        for c in CYCLES:
            df = self.main_s2[c]
            if c in (2005, 2010):
                if df["SURVMNTH"].isna().all():
                    self._rec("pass", f"{c} SURVMNTH is all NaN (correct).")
                else:
                    self._rec("fail", f"{c} SURVMNTH should be all NaN but isn't.")
            else:
                if df["SURVMNTH"].notna().any():
                    self._rec("pass", f"{c} SURVMNTH has values (correct).")
                else:
                    self._rec("warn", f"{c} SURVMNTH appears all NaN (check data).")

    # ---------------------------------------------------------------- Method 8
    def method8_diary(self) -> None:
        """Diary Closure QA."""
        print("\n--- Method 8: Diary Closure QA ---")
        _apply_dark()
        fig, axes = plt.subplots(1, 2, figsize=(13, 4))

        pass_rates: list[float] = []
        episode_counts_all: list[pd.DataFrame] = []

        for c in CYCLES:
            df = self.epi_s2[c]
            rate = df["DIARY_VALID"].mean() * 100
            pass_rates.append(rate)
            level = "pass" if rate >= 95 else "fail"
            self._rec(level, f"{c} — DIARY_VALID pass rate: {rate:.1f}%")

            ep_counts = df.groupby("occID").size().reset_index(name="n")
            ep_counts["Cycle"] = str(c)
            episode_counts_all.append(ep_counts)

        # Left: pass rate bar
        ax = axes[0]
        colors_dr = ["#a6e3a1" if r >= 95 else "#f38ba8" for r in pass_rates]
        bars = ax.bar(
            [str(c) for c in CYCLES],
            pass_rates,
            color=colors_dr,
            edgecolor="#1e1e2e",
            linewidth=0.8,
            width=0.55,
        )
        ax.axhline(
            95, color="#89b4fa", linestyle="--", linewidth=1.2, label="95% threshold"
        )
        ax.set_ylim(0, 105)
        ax.set_ylabel("DIARY_VALID Pass Rate (%)")
        ax.set_title("Diary Closure Pass Rate per Cycle", fontsize=12)
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        for bar, val in zip(bars, pass_rates):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + 1,
                f"{val:.1f}%",
                ha="center",
                fontsize=10,
                fontweight="bold",
            )

        # Right: episode count box plot
        ax2 = axes[1]
        combined = pd.concat(episode_counts_all, ignore_index=True)
        palette = {str(c): col for c, col in zip(CYCLES, CYCLE_COLORS)}
        sns.boxplot(
            data=combined,
            x="Cycle",
            y="n",
            hue="Cycle",
            palette=palette,
            linewidth=1.2,
            fliersize=2,
            legend=False,
            ax=ax2,
        )
        ax2.set_title("Episodes per Respondent Distribution", fontsize=12)
        ax2.set_xlabel("Survey Cycle")
        ax2.set_ylabel("Episode Count")
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)

        fig.suptitle("Diary Integrity QA", fontsize=14, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["8_diary"] = _b64(fig)

    # ---------------------------------------------------------------- Method 9
    def method9_regression(self) -> None:
        """Pre/Post Regression Check — side-by-side box plots + delta table."""
        print("\n--- Method 9: Pre/Post Regression Check ---")
        _apply_dark()

        # -- Plot 1: Weight distributions before vs after
        fig, axes = plt.subplots(1, 4, figsize=(14, 5), sharey=False)
        fig.suptitle(
            "Survey Weight (WGHT_PER) — Step 1 vs Step 2 Side-by-Side Box Plots",
            fontsize=13,
            fontweight="bold",
        )

        for idx, c in enumerate(CYCLES):
            ax = axes[idx]
            w_col_s1 = STEP1_WEIGHT_COL[c]
            wt_s1 = pd.to_numeric(self.main_s1[c][w_col_s1], errors="coerce").dropna()
            wt_s2 = pd.to_numeric(self.main_s2[c]["WGHT_PER"], errors="coerce").dropna()

            data = pd.DataFrame(
                {
                    "Weight": pd.concat([wt_s1, wt_s2], ignore_index=True),
                    "Source": ["Step 1"] * len(wt_s1) + ["Step 2"] * len(wt_s2),
                }
            )
            sns.boxplot(
                data=data,
                x="Source",
                y="Weight",
                hue="Source",
                palette={"Step 1": "#89b4fa", "Step 2": "#a6e3a1"},
                linewidth=1.0,
                fliersize=2,
                legend=False,
                ax=ax,
            )
            ax.set_title(str(c), fontsize=12, color=CYCLE_COLORS[idx])
            ax.set_xlabel("")
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)

            mean_diff = abs(wt_s1.mean() - wt_s2.mean())
            ax.text(
                0.5,
                0.97,
                f"Δmean={mean_diff:.0f}",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=9,
                color="#cdd6f4",
                bbox=dict(fc="#313244", ec="#555", pad=3),
            )

            level = "pass" if mean_diff < 1.0 else "warn"
            self._rec(level, f"{c} Weight Δmean = {mean_diff:.4f}")

        plt.tight_layout()
        self.plots_b64["9a_weights"] = _b64(fig)

        # -- Plot 2: NaN rate comparison (key columns) Step 1 vs Step 2
        _apply_dark()
        key_cols_s2 = [
            "SEX",
            "AGEGRP",
            "MARSTH",
            "HHSIZE",
            "LFTAG",
            "KOL",
            "HRSWRK",
            "TOTINC",
            "MODE",
        ]

        delta_records = []
        for c in CYCLES:
            m1 = self.main_s1[c]
            m2 = self.main_s2[c]

            sex_col_s1 = STEP1_SEX_COL[c]
            age_col_s1 = "AGEGR10"

            s1_nan_sex = (
                m1[sex_col_s1].isna().mean() * 100
                if sex_col_s1 in m1.columns
                else np.nan
            )
            s2_nan_sex = m2["SEX"].isna().mean() * 100

            s1_nan_age = (
                m1[age_col_s1].isna().mean() * 100
                if age_col_s1 in m1.columns
                else np.nan
            )
            s2_nan_age = m2["AGEGRP"].isna().mean() * 100

            delta_records.append(
                {
                    "Cycle": str(c),
                    "SEX NaN% S1": round(s1_nan_sex, 2),
                    "SEX NaN% S2": round(s2_nan_sex, 2),
                    "SEX Δ": round(s2_nan_sex - s1_nan_sex, 2),
                    "AGEGRP NaN% S1": round(s1_nan_age, 2),
                    "AGEGRP NaN% S2": round(s2_nan_age, 2),
                    "AGEGRP Δ": round(s2_nan_age - s1_nan_age, 2),
                }
            )
            if abs(s2_nan_sex - s1_nan_sex) == 0:
                self._rec("pass", f"{c} SEX NaN % preserved identically.")
            if abs(s2_nan_age - s1_nan_age) == 0:
                self._rec("pass", f"{c} AGEGRP NaN % preserved identically.")

        # Plot the NaN delta heatmap for harmonized columns
        nan_rows = []
        for c in CYCLES:
            m2 = self.main_s2[c]
            for col in key_cols_s2:
                if col in m2.columns:
                    nan_rows.append(
                        {
                            "Cycle": str(c),
                            "Column": col,
                            "NaN%": round(m2[col].isna().mean() * 100, 1),
                        }
                    )

        pivot = (
            pd.DataFrame(nan_rows)
            .pivot(index="Column", columns="Cycle", values="NaN%")
            .fillna(0)
        )

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            pivot,
            ax=ax2,
            cmap="YlOrRd",
            linewidths=0.4,
            linecolor="#1e1e2e",
            annot=True,
            fmt=".1f",
            cbar_kws={"label": "% Missing"},
            annot_kws={"size": 9},
        )
        ax2.set_title(
            "NaN % per Column × Cycle (Harmonized Step 2 Main Files)",
            fontsize=12,
            pad=10,
        )
        ax2.set_xlabel("Survey Cycle")
        ax2.set_ylabel("")
        ax2.tick_params(axis="x", rotation=0)
        ax2.tick_params(axis="y", rotation=0, labelsize=9)
        self.plots_b64["9b_nan_heatmap"] = _b64(fig2)
        self._rec("pass", "Regression NaN heatmap generated.")

    # ---------------------------------------------------------------- HTML
    def export_html(self) -> None:
        """Build and export the styled HTML validation report."""
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_titles: dict[str, str] = {
            "4_categories": "Chart 4 — Demographic Category Distributions (all vars × 4 cycles)",
            "5_activity": "Chart 5 — Activity Code Crosswalk Heatmap (14 categories × 4 cycles)",
            "6_location": "Chart 6 — AT_HOME Rate per Cycle",
            "8_diary": "Chart 8 — Diary Closure Pass Rate & Episode Distribution",
            "9a_weights": "Chart 9a — Survey Weight: Step 1 vs Step 2 Box Plots",
            "9b_nan_heatmap": "Chart 9b — NaN % per Harmonized Column (Regression Check)",
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

        def _badge_list(level: str) -> str:
            icon = "✅" if level == "pass" else ("❌" if level == "fail" else "⚠️")
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>" for m in items)

        nav_links = "".join(
            f'<a href="#{k}">{v.split("—")[0].strip()}</a>'
            for k, v in chart_titles.items()
            if k in self.plots_b64
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Step 2 — Harmonization Validation Report</title>
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
      <h1>GSS Step 2 — Harmonization Validation Report</h1>
      <p>Post-harmonization quality check across cycles 2005, 2010, 2015, 2022</p>
    </div>
  </header>
  <nav><a href="#pipeline-overview">Pipeline Overview</a>{nav_links}</nav>
  <main>
    <!-- Pipeline Overview -->
    <section class="pipeline-section" id="pipeline-overview">
      <h2>Pipeline Overview — Step 2: Data Harmonization</h2>
      <pre class="pipeline-pre">{STEP2_OVERVIEW}</pre>
    </section>

    <div class="scorecard">
      <div class="score-card ok"><div class="number">{n_pass}</div><div class="label">Checks Passed</div></div>
      <div class="score-card warn"><div class="number">{n_warn}</div><div class="label">Warnings</div></div>
      <div class="score-card fail"><div class="number">{n_fail}</div><div class="label">Failures</div></div>
      <div class="score-card pct"><div class="number">{pct_ok}%</div><div class="label">Pass Rate</div></div>
    </div>
    <div class="findings"><h2>❌ Failures</h2><ul class="badge-list">{_badge_list("fail")}</ul></div>
    <div class="findings"><h2>⚠️ Warnings</h2><ul class="badge-list">{_badge_list("warn")}</ul></div>
    <div class="findings"><h2>✅ Passed</h2><ul class="badge-list">{_badge_list("pass")}</ul></div>
    {charts_html}
  </main>
  <footer>Occupancy Modeling Pipeline · Step 2 Harmonization Validation · Generated 2026-03-08</footer>
</body>
</html>
"""
        out_path = os.path.join(OUTPUT_DIR, "step2_validation_report.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved to: {out_path}")


if __name__ == "__main__":
    validator = GSSHarmonizationValidator()
    validator.run_all()
