"""
01_readingGSS_val.py

Validation script for Step 1 of the Occupancy Modeling Pipeline.
Performs:
1. Schema & Shape Audit
2. Cross-Cycle Category Comparison
3. Episode Integrity Check
5. Visual Summary Dashboard (HTML Report)
"""

import os
import io
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from typing import Any

# Import column constants from the reading script
import importlib.util

spec = importlib.util.spec_from_file_location("reading_gss", "01_readingGSS.py")
reading_gss = importlib.util.module_from_spec(spec)
if spec and spec.loader:
    spec.loader.exec_module(reading_gss)

# Constants
OUTPUTS_DIR = "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs"
CYCLES = [2005, 2010, 2015, 2022]

EXPECTED_MAIN_COLS = {
    2005: reading_gss.MAIN_COLS_2005,
    2010: reading_gss.MAIN_COLS_2010,
    2015: reading_gss.MAIN_COLS_2015,
    2022: reading_gss.MAIN_COLS_2022,
}

EXPECTED_EPISODE_COLS = {
    2005: reading_gss.EPISODE_COLS_2005,
    2010: reading_gss.EPISODE_COLS_2010,
    2015: reading_gss.EPISODE_COLS_2015,
    2022: reading_gss.EPISODE_COLS_2022,
}

# --- Cross-cycle demographic variable mapping (None = not available in that cycle) ---
# Each entry: friendly_name -> {cycle_str: column_name | None}
DEMO_VARS: dict[str, dict[str, str | None]] = {
    "Age Group": {
        "2005": "AGEGR10", "2010": "AGEGR10",
        "2015": "AGEGR10", "2022": "AGEGR10",
    },
    "Sex / Gender": {
        "2005": "sex", "2010": "SEX",
        "2015": "SEX",  "2022": "GENDER2",
    },
    "Marital Status": {
        "2005": "marstat", "2010": "MARSTAT",
        "2015": "MARSTAT", "2022": "MARSTAT",
    },
    "Household Size": {
        "2005": "HSDSIZEC", "2010": "HSDSIZEC",
        "2015": "HSDSIZEC",  "2022": "HSDSIZEC",
    },
    "Province / Region": {
        "2005": "REGION", "2010": "PRV",
        "2015": "PRV",    "2022": "PRV",
    },
    "Urban / Rural (CMA)": {
        "2005": "LUC_RST", "2010": "LUC_RST",
        "2015": "LUC_RST",  "2022": "LUC_RST",
    },
    "Labour Force Activity": {
        "2005": "LFSGSS",   "2010": "ACT7DAYS",
        "2015": "ACT7DAYS", "2022": "ACT7DAYC",
    },
    "Employment Type (COW)": {
        "2005": "WKWE",    "2010": "WKWE",
        "2015": "WET_110", "2022": "WET_120",
    },
    "Hours Worked": {
        "2005": "WKWEHR_C", "2010": "WKWEHR_C",
        "2015": "WHWD140C", "2022": "WHWD140G",
    },
    "Commute Mode": {
        "2005": None,              # Absent from 2005 GSS
        "2010": "__CTW_2010__",    # derived from CTW_Q140_C01–C09
        "2015": "__CTW_2015__",    # derived from CTW_140A–I
        "2022": "__CTW_2022__",    # derived from CTW_140A–I
    },
    "Language at Home": {
        "2005": "LANCH",   "2010": "LANCH",
        "2015": "LAN_01",  "2022": "LAN_01",
    },
}


# --- Helper constants / functions for derived Chart 3 variables ---

_HOURS_BINS = [0, 15, 30, 40, 50, 75, 999]
_HOURS_LABELS = ["<15h", "15–29h", "30–39h", "40–49h", "50–74h", "75h+"]

_CTW_COLS_2010 = [
    "CTW_Q140_C01", "CTW_Q140_C02", "CTW_Q140_C03", "CTW_Q140_C04",
    "CTW_Q140_C05", "CTW_Q140_C06", "CTW_Q140_C07", "CTW_Q140_C08", "CTW_Q140_C09",
]
_CTW_COLS_2015_2022 = [
    "CTW_140A", "CTW_140B", "CTW_140C", "CTW_140D",
    "CTW_140E", "CTW_140F", "CTW_140G", "CTW_140H", "CTW_140I",
]
_CTW_LABELS = [
    "Car (driver)", "Car (passenger)", "Public transit", "Walked",
    "Bicycle", "Motorcycle", "Taxicab", "Works from home", "Other",
]


def _bin_hours(series: pd.Series) -> pd.Series:
    """Bin continuous hours-worked values (WKWEHR_C / WHWD140C) into 6 groups."""
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric[numeric < 96]   # exclude ALL missing/skip codes (96–99, 99.6–99.9)
    return pd.cut(valid, bins=_HOURS_BINS, labels=_HOURS_LABELS, right=False)


def _derive_commute_mode(df: pd.DataFrame, cycle: int) -> pd.Series:
    """Derive a single 'primary commute mode' categorical from multi-select checkboxes.

    Priority order: Car driver wins over Car passenger, etc.
    Value 1 = Yes in the raw checkbox columns.
    """
    cols = _CTW_COLS_2010 if cycle == 2010 else _CTW_COLS_2015_2022
    result = pd.Series(pd.NA, index=df.index, dtype="object")
    # Iterate in reverse so higher-priority modes overwrite lower ones
    for col, lbl in zip(reversed(cols), reversed(_CTW_LABELS)):
        if col in df.columns:
            mask = pd.to_numeric(df[col], errors="coerce") == 1
            result[mask] = lbl
    return result


class GSSValidator:
    """Validator class to run verification checks on step 1 data."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.data: dict[int, dict[str, pd.DataFrame]] = {}
        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        
    def load_data(self) -> None:
        """Load all exported CSV files."""
        print("Loading data...")
        for year in CYCLES:
            self.data[year] = {}
            main_path = os.path.join(self.data_dir, f"main_{year}.csv")
            epi_path = os.path.join(self.data_dir, f"episode_{year}.csv")
            
            if os.path.exists(main_path):
                self.data[year]["main"] = pd.read_csv(main_path, low_memory=False)
            else:
                self._record("fail", f"Missing MAIN file for {year}")
                
            if os.path.exists(epi_path):
                self.data[year]["episode"] = pd.read_csv(epi_path, low_memory=False)
            else:
                self._record("fail", f"Missing EPISODE file for {year}")
                
    def _record(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = "✅" if level == "pass" else ("❌" if level == "fail" else "⚠️")
        print(f"{icon} {msg}")

    # --- Method 1: Schema & Shape Audit ---
    def audit_schema(self) -> None:
        print("\n--- Method 1: Schema & Shape Audit ---")
        for year in CYCLES:
            if "main" in self.data[year]:
                df = self.data[year]["main"]
                self._check_columns(df, EXPECTED_MAIN_COLS[year], f"MAIN {year}")
                self._check_nulls(df, f"MAIN {year}")
                
            if "episode" in self.data[year]:
                df = self.data[year]["episode"]
                self._check_columns(df, EXPECTED_EPISODE_COLS[year], f"EPISODE {year}")
                self._check_nulls(df, f"EPISODE {year}")

    def _check_columns(self, df: pd.DataFrame, expected: list[str], identifier: str) -> None:
        missing = set(expected) - set(df.columns)
        if missing:
            # We don't fail for columns we know might be absent (like LFACT in 2005)
            self._record("warn", f"{identifier} is missing expected columns: {missing}")
        else:
            self._record("pass", f"{identifier} has all expected columns.")

    def _check_nulls(self, df: pd.DataFrame, identifier: str) -> None:
        all_nulls = df.columns[df.isnull().all()].tolist()
        if all_nulls:
            self._record("warn", f"{identifier} has 100% NaN columns: {all_nulls}")
        else:
            self._record("pass", f"{identifier} no completely null columns.")

    # --- Method 2: Cross-Cycle Category Comparison ---
    def compare_categories(self) -> None:
        print("\n--- Method 2: Cross-Cycle Category Comparison ---")
        for category_name, col_mapping in DEMO_VARS.items():
            print(f"\n{category_name} Uniques:")
            valid = True
            for year in CYCLES:
                if "main" in self.data[year]:
                    df = self.data[year]["main"]
                    col = col_mapping[str(year)]
                    if col is None:
                        print(f"  {year} (None): Column missing")
                        valid = False
                    elif col.startswith("__CTW_"):
                        series = _derive_commute_mode(df, year).dropna()
                        uniques = sorted(series.unique().tolist())
                        print(f"  {year} (derived commute): {uniques}")
                    elif category_name == "Hours Worked":
                        if col not in df.columns:
                            print(f"  {year} ({col}): Column missing")
                            valid = False
                        else:
                            numeric = pd.to_numeric(df[col], errors="coerce")
                            v = numeric[numeric < 96]
                            if not v.empty and (v <= 10).all():
                                uniques = sorted(v.astype(int).unique().tolist())
                                print(f"  {year} ({col}, grouped codes): {uniques}")
                            else:
                                binned = _bin_hours(df[col]).dropna()
                                uniques = [str(lbl) for lbl in _HOURS_LABELS if lbl in binned.values]
                                print(f"  {year} ({col}, binned): {uniques}")
                    elif col in df.columns:
                        uniques = pd.Series(df[col].dropna().unique()).sort_values().tolist()
                        print(f"  {year} ({col}): {uniques[:10]}{'...' if len(uniques) > 10 else ''}")
                    else:
                        print(f"  {year} ({col}): Column missing")
                        valid = False
            if valid:
                self._record("pass", f"{category_name} verified across available cycles.")

    # --- Method 3: Episode Integrity Check ---
    def verify_episode_integrity(self) -> None:
        print("\n--- Method 3: Episode Integrity Check ---")
        for year in CYCLES:
            if "main" not in self.data[year] or "episode" not in self.data[year]:
                continue
            
            main_df = self.data[year]["main"]
            epi_df = self.data[year]["episode"]
            
            # Identify ID columns
            main_id = "RECID" if year <= 2010 else "PUMFID"
            epi_id = "RECID" if year <= 2010 else "PUMFID"
            
            # Check ID Linkage
            if main_id in main_df.columns and epi_id in epi_df.columns:
                main_ids = set(main_df[main_id].unique())
                epi_ids = set(epi_df[epi_id].unique())
                overlap = len(epi_ids.intersection(main_ids)) / len(epi_ids)
                if overlap > 0.95:
                    self._record("pass", f"{year}: {overlap:.1%} of Episode IDs exist in Main.")
                else:
                    self._record("fail", f"{year}: Low ID overlap! Only {overlap:.1%} Episode IDs match.")
            
            # Check Time Ordering constraints
            if "STARTIME" in epi_df.columns and "ENDTIME" in epi_df.columns:
                try:
                    # Clean potential string times before conversion if necessary
                    s_time = pd.to_numeric(epi_df["STARTIME"], errors="coerce")
                    e_time = pd.to_numeric(epi_df["ENDTIME"], errors="coerce")
                    valid_time = (s_time <= e_time) | ((s_time > e_time) & (e_time < 240)) # e.g. cross midnight
                    pass_rate = valid_time.mean()
                    if pass_rate > 0.90:
                        self._record("pass", f"{year}: Time ordering logic passes for {pass_rate:.1%} of episodes.")
                    else:
                        self._record("warn", f"{year}: Time ordering issues detected. Pass rate: {pass_rate:.1%}")
                except Exception as e:
                    self._record("warn", f"{year}: Could not verify time ordering - {e}")

    # --- Method 5: Visual Summary Dashboard ---
    def generate_visuals(self) -> None:
        """Generate all charts and export an HTML validation report."""
        print("\n--- Method 5: Generating Visual Summary Dashboard ---")
        plt.rcParams.update({
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
        })

        self._plot_row_counts()
        self._plot_episode_density()
        self._plot_demo_frequencies()
        self._plot_nan_heatmap()
        self._plot_time_ordering()
        self.export_html_report()

    def _save_plot_to_b64(self, title: str) -> None:
        """Save current matplotlib figure to base64 PNG string."""
        buf = io.BytesIO()
        plt.tight_layout(pad=2.0)
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor=plt.gcf().get_facecolor())
        plt.close()
        buf.seek(0)
        self.plots_b64[title] = base64.b64encode(buf.read()).decode("utf-8")

    # ---- Chart 1: Row Counts ----
    def _plot_row_counts(self) -> None:
        """Bar chart: respondent and episode counts per cycle."""
        years = [str(y) for y in CYCLES]
        m_counts = [len(self.data[y].get("main", [])) for y in CYCLES]
        e_counts = [len(self.data[y].get("episode", [])) for y in CYCLES]

        PALETTE_MAIN = "#89b4fa"
        PALETTE_EPI = "#a6e3a1"

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        x = np.arange(len(years))
        width = 0.6

        # Left: Main respondents
        bars1 = axes[0].bar(x, m_counts, width, color=PALETTE_MAIN, zorder=3,
                            edgecolor="#1e1e2e", linewidth=0.8)
        axes[0].set_title("Main File — Respondents per Cycle", fontsize=13, pad=10)
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(years, fontsize=12)
        axes[0].set_ylabel("Row Count")
        axes[0].yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
        for bar, val in zip(bars1, m_counts):
            axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                         f"{val:,}", ha="center", va="bottom", fontsize=10)

        # Right: Episode counts
        bars2 = axes[1].bar(x, e_counts, width, color=PALETTE_EPI, zorder=3,
                            edgecolor="#1e1e2e", linewidth=0.8)
        axes[1].set_title("Episode File — Entries per Cycle", fontsize=13, pad=10)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(years, fontsize=12)
        axes[1].set_ylabel("Row Count")
        axes[1].yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
        for bar, val in zip(bars2, e_counts):
            axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2000,
                         f"{val:,}", ha="center", va="bottom", fontsize=10)

        fig.suptitle("GSS Data Volume Across Cycles", fontsize=15, fontweight="bold", y=1.01)
        self._save_plot_to_b64("1_row_counts")
        self._record("pass", "Row counts chart generated.")

    # ---- Chart 2: Episode Density Violin ----
    def _plot_episode_density(self) -> None:
        """Violin + strip plot: episode count distribution per respondent."""
        all_data = []
        for year in CYCLES:
            if "episode" in self.data[year]:
                df = self.data[year]["episode"]
                epi_id = "RECID" if year <= 2010 else "PUMFID"
                if epi_id in df.columns:
                    counts = df.groupby(epi_id).size().reset_index(name="episodes")
                    counts["Cycle"] = str(year)
                    all_data.append(counts)

        if not all_data:
            return

        combined = pd.concat(all_data, ignore_index=True)
        COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        palette = {str(y): c for y, c in zip(CYCLES, COLORS)}

        fig, ax = plt.subplots(figsize=(11, 5))
        sns.violinplot(
            data=combined, x="Cycle", y="episodes", hue="Cycle",
            palette=palette, inner="box", cut=0, linewidth=1.2,
            legend=False, ax=ax
        )
        ax.set_title("Distribution of Episodes per Respondent (by Cycle)", fontsize=13, pad=10)
        ax.set_xlabel("Survey Cycle", fontsize=12)
        ax.set_ylabel("Episodes per Respondent", fontsize=12)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        # Overlay median label
        for i, year in enumerate(CYCLES):
            subset = combined[combined["Cycle"] == str(year)]["episodes"]
            if not subset.empty:
                med = subset.median()
                ax.text(i, med + 0.8, f"med={med:.0f}", ha="center", fontsize=9,
                        color="#cdd6f4", fontweight="bold")

        self._save_plot_to_b64("2_episode_density")
        self._record("pass", "Episode density violin chart generated.")

    # ---- Chart 3: Demographic Value Distributions (all variables) ----
    def _plot_demo_frequencies(self) -> None:
        """One figure per demographic variable: stacked % bars per cycle.

        Cycles where the variable is absent (None in DEMO_VARS or genuinely
        missing from the loaded data) show a hatched 'N/A' bar so the gap is
        explicit rather than silently omitted.
        """
        # Catppuccin-inspired palette for categories inside each bar
        CAT_CMAP = "tab20"
        CYCLE_COLORS = ["#89b4fa", "#f38ba8", "#fab387", "#a6e3a1"]
        NA_COLOR = "#45475a"
        cycle_strs = [str(y) for y in CYCLES]

        n_vars = len(DEMO_VARS)
        # One row per variable, 4 columns = one bar per cycle
        fig, axes = plt.subplots(
            n_vars, 4,
            figsize=(18, 3.2 * n_vars),
            sharey=False,
        )
        # axes shape: (n_vars, 4)
        fig.suptitle(
            "Demographic & Socioeconomic Distributions Across Cycles (%)",
            fontsize=15, fontweight="bold", y=1.005,
        )

        for row_idx, (var_name, col_map) in enumerate(DEMO_VARS.items()):
            for col_idx, cyc in enumerate(cycle_strs):
                ax = axes[row_idx, col_idx]
                year = int(cyc)

                mapped_col = col_map.get(cyc)  # None means explicitly N/A
                is_sentinel = isinstance(mapped_col, str) and mapped_col.startswith("__CTW_")
                df_main = self.data[year].get("main")
                data_available = (
                    mapped_col is not None
                    and df_main is not None
                    and (is_sentinel or mapped_col in df_main.columns)
                )

                if not data_available:
                    # Draw a hatched N/A placeholder
                    ax.bar(
                        [0], [1], color=NA_COLOR,
                        hatch="///", edgecolor="#888", linewidth=0.6
                    )
                    ax.text(0, 0.5, "N/A", ha="center", va="center",
                            fontsize=12, color="#cdd6f4", fontweight="bold")
                    ax.set_xlim(-0.5, 0.5)
                    ax.set_ylim(0, 1)
                    ax.set_xticks([])
                    ax.set_yticks([])
                else:
                    # --- resolve the series depending on variable type ---
                    if is_sentinel:
                        # Derived commute mode from checkbox columns
                        raw = _derive_commute_mode(df_main, year).dropna()
                        series = raw.value_counts(normalize=True).sort_index()
                    elif var_name == "Hours Worked":
                        # Bin continuous hours; 2022 WHWD140G uses group codes 1-8
                        raw_col = df_main[mapped_col]
                        numeric = pd.to_numeric(raw_col, errors="coerce")
                        valid = numeric[numeric < 96]   # strip missing/skip codes
                        if not valid.empty and (valid <= 10).all():
                            # Pre-grouped (2022 WHWD140G): codes are 1-8, keep as-is
                            series = (
                                valid.astype(int)
                                .value_counts(normalize=True).sort_index()
                            )
                        else:
                            # Continuous (2005, 2010, 2015): bin into hour bands
                            binned = _bin_hours(raw_col).dropna()
                            series = binned.value_counts(normalize=True).reindex(_HOURS_LABELS).dropna()
                    else:
                        series = (
                            df_main[mapped_col]
                            .dropna()
                            .pipe(lambda s: pd.to_numeric(s, errors="coerce"))
                            .dropna()
                            .astype(int)
                            .value_counts(normalize=True)
                            .sort_index()
                        )
                    cats = series.index.tolist()
                    vals = series.values

                    cmap = plt.colormaps[CAT_CMAP].resampled(max(len(cats), 2))
                    colors = [cmap(i) for i in range(len(cats))]

                    bottom = 0.0
                    for cat_i, (cat, val) in enumerate(zip(cats, vals)):
                        ax.bar(
                            [0], [val], bottom=[bottom],
                            color=colors[cat_i],
                            edgecolor="#1e1e2e", linewidth=0.4, width=0.7,
                            label=str(cat),
                        )
                        # Only annotate slices that are >=8% so text fits
                        if val >= 0.08:
                            ax.text(
                                0, bottom + val / 2,
                                f"{cat}\n{val:.0%}",
                                ha="center", va="center",
                                fontsize=7.5, color="white", fontweight="bold",
                            )
                        bottom += val

                    ax.set_xlim(-0.5, 0.5)
                    ax.set_ylim(0, 1.0)
                    ax.set_xticks([])
                    ax.yaxis.set_major_formatter(
                        plt.FuncFormatter(lambda v, _: f"{v:.0%}")
                    )
                    ax.yaxis.grid(True, linestyle="--", alpha=0.25)

                # Column header (cycle year) on first row only
                if row_idx == 0:
                    ax.set_title(
                        cyc, fontsize=13, fontweight="bold",
                        color=CYCLE_COLORS[col_idx], pad=8,
                    )

                # Row label (variable name) on leftmost column only
                if col_idx == 0:
                    ax.set_ylabel(var_name, fontsize=10, labelpad=8)

        plt.subplots_adjust(hspace=0.35, wspace=0.08)
        self._save_plot_to_b64("3_demographics")
        self._record("pass", "Demographic distribution chart generated (all variables).")


    # ---- Chart 4: NaN Heatmap ----
    def _plot_nan_heatmap(self) -> None:
        """Heatmap: % missing values per column × cycle (Main files only)."""
        records = []
        for year in CYCLES:
            if "main" in self.data[year]:
                df = self.data[year]["main"]
                nan_pct = df.isnull().mean() * 100
                for col, pct in nan_pct.items():
                    records.append({"Cycle": str(year), "Column": col, "NaN%": pct})

        if not records:
            return

        pivot = (
            pd.DataFrame(records)
            .pivot(index="Column", columns="Cycle", values="NaN%")
            .fillna(0)
        )

        fig_h = max(5, len(pivot) * 0.38)
        fig, ax = plt.subplots(figsize=(8, fig_h))
        sns.heatmap(
            pivot, ax=ax, cmap="YlOrRd", linewidths=0.4,
            linecolor="#1e1e2e", annot=True, fmt=".0f",
            cbar_kws={"label": "% Missing"},
            annot_kws={"size": 8}
        )
        ax.set_title("NaN % per Column × Cycle (Main Files)", fontsize=13, pad=10)
        ax.set_xlabel("Survey Cycle")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=0)
        ax.tick_params(axis="y", rotation=0, labelsize=8)
        self._save_plot_to_b64("4_nan_heatmap")
        self._record("pass", "NaN heatmap generated.")

    # ---- Chart 5: Time-Ordering Pass Rate ----
    def _plot_time_ordering(self) -> None:
        """Horizontal bar chart: episode time-ordering pass rate per cycle."""
        pass_rates: dict[str, float] = {}
        for year in CYCLES:
            if "episode" not in self.data[year]:
                continue
            df = self.data[year]["episode"]
            if "STARTIME" not in df.columns or "ENDTIME" not in df.columns:
                continue
            s = pd.to_numeric(df["STARTIME"], errors="coerce")
            e = pd.to_numeric(df["ENDTIME"], errors="coerce")
            valid = (s <= e) | ((s > e) & (e < 240))
            pass_rates[str(year)] = valid.mean() * 100

        if not pass_rates:
            return

        fig, ax = plt.subplots(figsize=(8, 3.5))
        cycles = list(pass_rates.keys())
        rates = [pass_rates[c] for c in cycles]
        colors = ["#a6e3a1" if r >= 95 else ("#fab387" if r >= 90 else "#f38ba8") for r in rates]

        bars = ax.barh(cycles, rates, color=colors, edgecolor="#1e1e2e", linewidth=0.8, height=0.5)
        ax.set_xlim(80, 101)
        ax.axvline(95, color="#89b4fa", linestyle="--", linewidth=1.2, label="95% threshold")
        ax.axvline(90, color="#f38ba8", linestyle=":", linewidth=1.2, label="90% threshold")

        for bar, val in zip(bars, rates):
            ax.text(val - 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%", va="center", ha="right", fontsize=11, fontweight="bold")

        ax.set_title("Episode Time-Ordering Pass Rate per Cycle", fontsize=13, pad=10)
        ax.set_xlabel("Pass Rate (%)")
        ax.xaxis.grid(True, linestyle="--", alpha=0.3)
        ax.legend(fontsize=9)
        self._save_plot_to_b64("5_time_ordering")
        self._record("pass", "Time-ordering pass rate chart generated.")

    # ---- HTML Export ----
    def export_html_report(self) -> None:
        """Build and save a styled HTML report embedding all charts."""
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_titles = {
            "1_row_counts":     "Chart 1 — GSS Data Volume (Row Counts)",
            "2_episode_density": "Chart 2 — Episode Density per Respondent",
            "3_demographics":   "Chart 3 — Demographic Category Distributions",
            "4_nan_heatmap":    "Chart 4 — Missing Data Heatmap (Main Files)",
            "5_time_ordering":  "Chart 5 — Episode Time-Ordering Pass Rate",
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

        fails_html = (
            "".join(f'<li class="badge fail">❌ {m}</li>' for m in self.results["fail"])
            or "<li class='badge pass'>No failures detected</li>"
        )
        warns_html = (
            "".join(f'<li class="badge warn">⚠️ {m}</li>' for m in self.results["warn"])
            or "<li class='badge pass'>No warnings</li>"
        )
        passes_html = "".join(
            f'<li class="badge pass">✅ {m}</li>' for m in self.results["pass"]
        )
        nav_links = "".join(
            f'<a href="#{k}">{v.split("—")[0].strip()}</a>'
            for k, v in chart_titles.items() if k in self.plots_b64
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Step 1 — Validation Report</title>
  <style>
    :root {{
      --bg: #1e1e2e; --surface: #2a2a3e; --surface2: #313244;
      --accent: #89b4fa; --green: #a6e3a1; --yellow: #f9e2af;
      --red: #f38ba8; --text: #cdd6f4; --subtext: #a6adc8;
      --border: #45475a;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg); color: var(--text);
      min-height: 100vh;
    }}
    header {{
      background: var(--surface); border-bottom: 1px solid var(--border);
      padding: 18px 32px; display: flex; align-items: center;
      justify-content: space-between; position: sticky; top: 0; z-index: 100;
    }}
    header h1 {{ font-size: 1.25rem; color: var(--accent); }}
    header p {{ font-size: 0.8rem; color: var(--subtext); }}
    nav {{
      background: var(--surface2); border-bottom: 1px solid var(--border);
      padding: 8px 32px; display: flex; gap: 20px; flex-wrap: wrap;
    }}
    nav a {{
      color: var(--subtext); text-decoration: none; font-size: 0.82rem;
      padding: 4px 10px; border-radius: 6px;
      transition: background 0.2s, color 0.2s;
    }}
    nav a:hover {{ background: var(--surface); color: var(--accent); }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 30px 28px; }}

    /* Scorecard */
    .scorecard {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
      margin-bottom: 36px;
    }}
    .score-card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 20px 16px; text-align: center;
    }}
    .score-card .number {{ font-size: 2.4rem; font-weight: 700; }}
    .score-card .label {{ font-size: 0.8rem; color: var(--subtext); margin-top: 4px; }}
    .score-card.ok   .number {{ color: var(--green); }}
    .score-card.warn .number {{ color: var(--yellow); }}
    .score-card.fail .number {{ color: var(--red); }}
    .score-card.pct  .number {{ color: var(--accent); font-size: 2.0rem; }}

    /* Findings */
    .findings {{ margin-bottom: 36px; }}
    .findings h2 {{ font-size: 1.05rem; margin-bottom: 12px; color: var(--accent); }}
    .badge-list {{ list-style: none; display: flex; flex-direction: column; gap: 6px; }}
    .badge {{
      padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; line-height: 1.4;
    }}
    .badge.pass {{ background: #1c2e22; border: 1px solid #2d5a35; color: var(--green); }}
    .badge.warn {{ background: #2e2a1c; border: 1px solid #5a4e1f; color: var(--yellow); }}
    .badge.fail {{ background: #2e1c1e; border: 1px solid #5a2428; color: var(--red); }}

    /* Charts */
    .chart-section {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 14px; padding: 24px; margin-bottom: 28px;
    }}
    .chart-section h2 {{
      font-size: 1.0rem; color: var(--accent); margin-bottom: 16px;
      padding-bottom: 8px; border-bottom: 1px solid var(--border);
    }}
    .chart-wrap {{ text-align: center; }}
    .chart-wrap img {{ max-width: 100%; height: auto; border-radius: 8px; }}

    footer {{
      text-align: center; padding: 20px; font-size: 0.78rem;
      color: var(--subtext); border-top: 1px solid var(--border); margin-top: 10px;
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GSS Step 1 — Data Collection Validation Report</h1>
      <p>Pre-harmonization quality check across cycles 2005, 2010, 2015, 2022</p>
    </div>
  </header>
  <nav>{nav_links}</nav>
  <main>
    <!-- Scorecard -->
    <div class="scorecard">
      <div class="score-card ok"><div class="number">{n_pass}</div><div class="label">Checks Passed</div></div>
      <div class="score-card warn"><div class="number">{n_warn}</div><div class="label">Warnings</div></div>
      <div class="score-card fail"><div class="number">{n_fail}</div><div class="label">Failures</div></div>
      <div class="score-card pct"><div class="number">{pct_ok}%</div><div class="label">Pass Rate</div></div>
    </div>

    <!-- Findings -->
    <div class="findings">
      <h2>❌ Failures</h2>
      <ul class="badge-list">{fails_html}</ul>
    </div>
    <div class="findings">
      <h2>⚠️ Warnings</h2>
      <ul class="badge-list">{warns_html}</ul>
    </div>
    <div class="findings">
      <h2>✅ Passed</h2>
      <ul class="badge-list">{passes_html}</ul>
    </div>

    <!-- Charts -->
    {charts_html}
  </main>
  <footer>Occupancy Modeling Pipeline · Step 1 Validation · Generated 2026-03-01</footer>
</body>
</html>
"""

        out_path = os.path.join(self.data_dir, "validation_report.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved to: {out_path}")


if __name__ == "__main__":
    validator = GSSValidator(OUTPUTS_DIR)
    validator.load_data()
    validator.audit_schema()
    validator.compare_categories()
    validator.verify_episode_integrity()
    validator.generate_visuals()

    print("\nValidation complete.")

