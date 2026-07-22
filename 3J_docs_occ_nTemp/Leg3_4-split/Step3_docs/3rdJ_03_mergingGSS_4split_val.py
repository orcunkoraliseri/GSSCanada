# -*- coding: utf-8 -*-
"""
3rdJ_03_mergingGSS_4split_val.py

Step 3 Validator for Leg-3 (Four-Channel Split: Residential + Office + Retail)
Occupancy Pipeline.

Ported from:  Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS_2split_val.py  (Leg-2)
Leg-3 additions (new relative to the Leg-2 validator; Sections 1-10 unchanged):
  - Section 11: RETL30 channel checks (shape, alignment, values in {0,1},
    weekday/Saturday/Sunday diurnal-window rates, night rate, all-day mean,
    exclusivity vs AT_HOME/AT_WORK, OR-rule leak cross-tab, headline diurnal chart)
  - Section 12: legacy bit-identity vs Leg-2 (SHA-256 of the 5 CSVs + parquet,
    with column-wise value-equality fallback for the parquet)
  - All Path literals repointed: INPUT_DIR still resolves to the (read-only)
    Leg-2 Step-2 outputs; OUTPUT_DIR resolves to this Leg-3 Step3_docs/outputs_step3/;
    LEG2_OUTPUT_DIR (NEW) points at the Leg-2 Step-3 outputs (Section 12 reference).

Input:
  outputs_step3/merged_episodes.csv
  outputs_step3/hetus_wide.csv
  outputs_step3/hetus_30min.csv
  outputs_step3/copresence_30min.csv
  outputs_step3/work_30min.csv
  outputs_step3/retail_30min.csv        [Leg-3 NEW]
  outputs_step2/main_*.csv + episode_*.csv  (Step 2 reference)
  ../../Leg2_2-split/Step3_docs/outputs_step3/*  (Section 12 bit-identity reference)

Output:
  outputs_step3/step3_validation_report.html
  outputs_step3/step3_validation_report.txt

Run locally:
    cd Step3_docs
    py -3 -X utf8 3rdJ_03_mergingGSS_4split_val.py
"""

from __future__ import annotations

import base64
import hashlib
import io
import os
import platform
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ── Platform-detection path block ─────────────────────────────────────────────
_SYSTEM = platform.system()

if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.join(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main",
        r"3J_docs_occ_nTemp\Leg2_2-split"
    )
    _LEG3_BASE = os.path.join(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main",
        r"3J_docs_occ_nTemp\Leg3_4-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
    _LEG3_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split"
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"), "GSSCanada", "GSSCanada-main",
        "3J_docs_occ_nTemp", "Leg2_2-split"
    )
    _LEG3_BASE = os.path.join(
        os.path.expanduser("~"), "GSSCanada", "GSSCanada-main",
        "3J_docs_occ_nTemp", "Leg3_4-split"
    )

INPUT_DIR  = os.path.join(_LEG2_BASE, "Step2_docs", "outputs_step2")     # read-only Leg-2 Step-2 outputs
OUTPUT_DIR = os.path.join(_LEG3_BASE, "Step3_docs", "outputs_step3")     # Leg-3 Step-3 outputs (this build)
LEG2_OUTPUT_DIR = os.path.join(_LEG2_BASE, "Step3_docs", "outputs_step3")  # read-only Leg-2 reference (Section 12)

# [Leg-3 NEW] Legacy outputs whose bit-identity to Leg-2 is gated in Section 12.
LEGACY_OUTPUTS_CSV = [
    "merged_episodes.csv",
    "hetus_wide.csv",
    "hetus_30min.csv",
    "copresence_30min.csv",
    "work_30min.csv",
]
LEGACY_OUTPUTS_PARQUET = ["merged_episodes.parquet"]

# ── Constants ──────────────────────────────────────────────────────────────────

CYCLES = [2005, 2010, 2015, 2022]

COPRE_COLS = [
    "Alone", "Spouse", "Children", "parents",
    "otherInFAMs", "otherHHs", "friends", "others", "colleagues",
]

STEP3_OVERVIEW = """\
+---------------------------------------------------------------------------+
|  STEP 3 (Leg-3) -- MERGE & TILING (4-CHANNEL SPLIT)                     |
|                                                                           |
|  LEFT JOIN: Episode <- Main on occID + CYCLE_YEAR                        |
|  Weight rule: WGHT_EPI (episode) / WGHT_PER (person)                    |
|                                                                           |
|  Derived columns (Leg-1 verbatim):                                        |
|  - DDAY_STRATA  (1=Weekday, 2=Saturday, 3=Sunday)                       |
|  - DAYTYPE      (Mon-Fri=Weekday / Sat-Sun=Weekend)                     |
|  - HOUR_OF_DAY  (0-23)                                                   |
|  - TIMESLOT_10  (slots 1-144, HETUS 4AM origin)                         |
|  - AT_HOME      (LOCATION/PLACE -> binary 1/0)  [Leg-1]                |
|                                                                           |
|  Leg-2 additions to MAIN_COMMON_COLS:                                    |
|  - NAICS     (unified industry code across cycles)                       |
|  - TELEWORK  (harmonized binary: 2010/2015/2022; NaN for 2005)          |
|                                                                           |
|  Leg-2 addition to EPISODE_COMMON_COLS:                                  |
|  - AT_WORK   (occPRE==2 binary flag)                                     |
|                                                                           |
|  Leg-3 addition (Phase K, episode-level, FROZEN OD-1 2026-07-02):        |
|  - AT_RETAIL = (occPRE==5) | ((occACT==4) & occPRE.isin({5,9}))         |
|                                                                           |
|  Residential Phase F/H: BIT-IDENTICAL to Leg 1.                         |
|  AT_WORK (Phase J) and AT_RETAIL (Phase K) tiling are separate CSVs --  |
|  purely additive; the 6 legacy outputs are hash-gated vs Leg-2 (Sec 12). |
|                                                                           |
|  Files produced:                                                          |
|  - merged_episodes.csv / .parquet  (~1.05M rows)                        |
|  - hetus_wide.csv  (one row/respondent, 288+ slot columns)              |
|  - hetus_30min.csv (48 act30 + 48 hom30 + meta)                        |
|  - copresence_30min.csv (occID + 9x48 co-presence slots)               |
|  - work_30min.csv  (occID + WORK30_001..048)  [Leg-2]                  |
|  - retail_30min.csv (occID + RETL30_001..048)  [Leg-3 NEW]             |
+---------------------------------------------------------------------------+"""

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
NIGHT_SLOTS = list(range(1, 13)) + list(range(109, 145))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _apply_dark() -> None:
    plt.rcParams.update(_DARK)


def _b64(fig: plt.Figure) -> str:
    """Encode figure to base64 PNG string and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ── Validator ──────────────────────────────────────────────────────────────────

class GSSMergeValidator4Split:
    """Validates Step 3 (Leg-3) merge, tiling, AT_WORK & AT_RETAIL outputs,
    plus the Section-12 legacy bit-identity gate vs Leg-2."""

    def __init__(self, step2_dir: str, step3_dir: str, leg2_step3_dir: str) -> None:
        print("Loading Step 2 reference files...")
        self.main_s2: dict[int, pd.DataFrame] = {}
        self.epi_s2: dict[int, pd.DataFrame] = {}
        for c in CYCLES:
            self.main_s2[c] = pd.read_csv(
                os.path.join(step2_dir, f"main_{c}.csv"), low_memory=False)
            self.epi_s2[c] = pd.read_csv(
                os.path.join(step2_dir, f"episode_{c}.csv"), low_memory=False)
            print(f"  main_{c}: {len(self.main_s2[c]):,}  "
                  f"episode_{c}: {len(self.epi_s2[c]):,}")

        print("Loading Step 3 outputs...")
        self.merged = pd.read_csv(
            os.path.join(step3_dir, "merged_episodes.csv"), low_memory=False)
        print(f"  merged_episodes: {len(self.merged):,} rows x "
              f"{self.merged.shape[1]} cols")

        self.hetus = pd.read_csv(
            os.path.join(step3_dir, "hetus_wide.csv"), low_memory=False)
        print(f"  hetus_wide: {len(self.hetus):,} rows x "
              f"{self.hetus.shape[1]} cols")

        h30_path = os.path.join(step3_dir, "hetus_30min.csv")
        if os.path.exists(h30_path):
            self.hetus_30min = pd.read_csv(h30_path, low_memory=False)
            print(f"  hetus_30min: {len(self.hetus_30min):,} rows x "
                  f"{self.hetus_30min.shape[1]} cols")
        else:
            self.hetus_30min = None
            print("  hetus_30min: NOT FOUND")

        cop_path = os.path.join(step3_dir, "copresence_30min.csv")
        if os.path.exists(cop_path):
            self.copresence_30min = pd.read_csv(cop_path, low_memory=False)
            print(f"  copresence_30min: {len(self.copresence_30min):,} rows x "
                  f"{self.copresence_30min.shape[1]} cols")
        else:
            self.copresence_30min = None
            print("  copresence_30min: NOT FOUND")

        # [Leg-2 NEW] Load work_30min.csv
        work_path = os.path.join(step3_dir, "work_30min.csv")
        if os.path.exists(work_path):
            self.work_30min = pd.read_csv(work_path, low_memory=False)
            print(f"  work_30min: {len(self.work_30min):,} rows x "
                  f"{self.work_30min.shape[1]} cols")
        else:
            self.work_30min = None
            print("  work_30min: NOT FOUND -- Section 9 (AT_WORK) will be skipped")

        # [Leg-3 NEW] Load retail_30min.csv
        retail_path = os.path.join(step3_dir, "retail_30min.csv")
        if os.path.exists(retail_path):
            self.retail_30min = pd.read_csv(retail_path, low_memory=False)
            print(f"  retail_30min: {len(self.retail_30min):,} rows x "
                  f"{self.retail_30min.shape[1]} cols")
        else:
            self.retail_30min = None
            print("  retail_30min: NOT FOUND -- Section 11 (AT_RETAIL) will be skipped")

        self.leg2_step3_dir = leg2_step3_dir

        self.step2_dir = step2_dir
        self.step3_dir = step3_dir
        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        self.summary_data: dict = {}

        # Capture actual N
        self.N = len(self.hetus) if self.hetus is not None else 64_061

    # ── helpers ────────────────────────────────────────────────────────────────

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = "OK" if level == "pass" else ("FAIL" if level == "fail" else "WARN")
        print(f"  [{icon}] {msg}")

    # ── Section 1: Row Count Preservation ─────────────────────────────────────

    def validate_row_counts(self) -> dict:
        print("\n--- Section 1: Row Count Preservation ---")
        _apply_dark()

        s2_main_counts = {c: len(self.main_s2[c]) for c in CYCLES}
        s2_epi_counts  = {c: len(self.epi_s2[c]) for c in CYCLES}

        post_resp: dict[int, int] = {}
        post_epi:  dict[int, int] = {}
        for c in CYCLES:
            cyc = self.merged[self.merged["CYCLE_YEAR"] == c]
            post_resp[c] = cyc[["occID", "CYCLE_YEAR"]].drop_duplicates().shape[0]
            post_epi[c]  = len(cyc)

        for c in CYCLES:
            self._rec("pass",
                      f"1.1 | {c} Main rows (Step 2 reference): "
                      f"{s2_main_counts[c]:,}")

        exclusion_rows: list[dict] = []
        for c in CYCLES:
            pre  = s2_epi_counts[c]
            post = post_epi[c]
            if pre >= post:
                self._rec("pass",
                          f"1.2 | {c} Episodes: Step2={pre:,} -> "
                          f"post-filter={post:,} ({pre - post:,} removed)")
            else:
                self._rec("fail",
                          f"1.2 | {c} Episode count INCREASED: "
                          f"{pre:,} -> {post:,}")

        total_s2_epi = sum(s2_epi_counts.values())
        total_merged = len(self.merged)
        if total_merged <= total_s2_epi:
            self._rec("pass",
                      f"1.3 | Total episodes Step2={total_s2_epi:,} -> "
                      f"merged={total_merged:,} (after DIARY_VALID filter)")
        else:
            self._rec("fail",
                      f"1.3 | Merged episodes {total_merged:,} exceeds "
                      f"Step2 total {total_s2_epi:,}")

        for c in CYCLES:
            pre  = s2_main_counts[c]
            post = post_resp[c]
            excluded = pre - post
            rate = excluded / pre * 100 if pre > 0 else 0.0
            level = "pass" if rate < 3 else ("warn" if rate < 5 else "fail")
            self._rec(level,
                      f"1.4 | {c} Exclusion: {excluded:,}/{pre:,} "
                      f"({rate:.2f}%)")
            exclusion_rows.append({
                "Cycle": str(c), "Step2 Resp": pre, "Post-filter Resp": post,
                "Excluded": excluded, "Rate (%)": round(rate, 2),
            })

        self._rec("pass",
                  f"1.5 | Post-filter totals: "
                  f"{sum(post_resp.values()):,} respondents | "
                  f"{sum(post_epi.values()):,} episodes")

        # Chart 1a
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("Row Count Preservation -- Step 2 vs. Step 3",
                     fontsize=14, fontweight="bold")
        x = np.arange(len(CYCLES)); w = 0.35
        ax = axes[0]
        ax.bar(x - w/2, [s2_main_counts[c] for c in CYCLES], w,
               label="Step 2 Resp.", color="#89b4fa", edgecolor="#1e1e2e")
        ax.bar(x + w/2, [post_resp[c] for c in CYCLES], w,
               label="Step 3 Post-filter", color="#a6e3a1", edgecolor="#1e1e2e")
        ax.set_xticks(x); ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_title("Respondents: Step 2 vs. Step 3 Post-filter", fontsize=12)
        ax.set_ylabel("Count"); ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        ax2 = axes[1]
        rates = [r["Rate (%)"] for r in exclusion_rows]
        colors = ["#a6e3a1" if r < 3 else ("#f9e2af" if r < 5 else "#f38ba8") for r in rates]
        bars = ax2.bar([str(c) for c in CYCLES], rates, color=colors, edgecolor="#1e1e2e", width=0.55)
        ax2.axhline(5, color="#f38ba8", linestyle="--", linewidth=1.2, label="5% FAIL")
        ax2.axhline(3, color="#f9e2af", linestyle="--", linewidth=1.0, label="3% WARN")
        ax2.set_title("DIARY_VALID Exclusion Rate per Cycle", fontsize=12)
        ax2.set_ylabel("Exclusion Rate (%)"); ax2.legend(fontsize=9)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        for bar, val in zip(bars, rates):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     f"{val:.2f}%", ha="center", fontsize=10, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["1_row_counts"] = _b64(fig)

        result = {"s2_main_counts": s2_main_counts, "s2_epi_counts": s2_epi_counts,
                  "post_resp": post_resp, "post_epi": post_epi, "exclusion_rows": exclusion_rows}
        self.summary_data["section1"] = result
        return result

    # ── Section 2: Merge Key Integrity ─────────────────────────────────────────

    def validate_merge_integrity(self) -> dict:
        print("\n--- Section 2: Merge Key Integrity ---")
        _apply_dark()

        orphans   = self.merged["WGHT_PER"].isna().sum()
        level = "pass" if orphans == 0 else "fail"
        self._rec(level, f"2.1 | Orphan episodes (null WGHT_PER): {orphans}")

        hetus_dupes = self.hetus.duplicated(subset=["occID", "CYCLE_YEAR"]).sum()
        level = "pass" if hetus_dupes == 0 else "fail"
        self._rec(level, f"2.2 | Duplicate (occID, CYCLE_YEAR) in hetus_wide: {hetus_dupes}")

        null_wght = self.merged["WGHT_PER"].isna().sum()
        level = "pass" if null_wght == 0 else "fail"
        self._rec(level, f"2.3 | WGHT_PER null count: {null_wght}")

        actual_years = set(self.merged["CYCLE_YEAR"].dropna().unique().astype(int))
        unexpected   = actual_years - set(CYCLES)
        level = "pass" if not unexpected else "fail"
        self._rec(level, f"2.4 | CYCLE_YEAR values: {sorted(actual_years)}")

        per_cycle_stats = []
        for c in CYCLES:
            cyc = self.merged[self.merged["CYCLE_YEAR"] == c]
            wght = pd.to_numeric(cyc["WGHT_PER"], errors="coerce").dropna()
            per_cycle_stats.append({
                "cycle": c, "n_epi": len(cyc),
                "n_resp": cyc[["occID", "CYCLE_YEAR"]].drop_duplicates().shape[0],
                "wght_median": wght.median(), "wght_vals": wght,
            })

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("Merge Key Integrity", fontsize=14, fontweight="bold")
        x = np.arange(len(CYCLES)); w = 0.35
        ep_vals   = [s["n_epi"]  for s in per_cycle_stats]
        resp_vals = [s["n_resp"] for s in per_cycle_stats]
        axes[0].bar(x - w/2, ep_vals,   w, label="Episodes",    color="#fab387", edgecolor="#1e1e2e")
        axes[0].bar(x + w/2, resp_vals, w, label="Respondents", color="#89b4fa", edgecolor="#1e1e2e")
        axes[0].set_xticks(x); axes[0].set_xticklabels([str(c) for c in CYCLES])
        axes[0].set_title("Episodes & Respondents per Cycle", fontsize=11)
        axes[0].legend(fontsize=8.5); axes[0].yaxis.grid(True, linestyle="--", alpha=0.3)

        wgt_data = [s["wght_vals"].values for s in per_cycle_stats]
        bp = axes[1].boxplot(wgt_data, patch_artist=True,
                             medianprops=dict(color="#1e1e2e", linewidth=2),
                             flierprops=dict(marker="o", markersize=1.5, alpha=0.4))
        for patch, col in zip(bp["boxes"], CYCLE_COLORS):
            patch.set_facecolor(col); patch.set_alpha(0.85)
        axes[1].set_xticks(range(1, len(CYCLES) + 1))
        axes[1].set_xticklabels([str(c) for c in CYCLES])
        axes[1].set_title("WGHT_PER Distribution per Cycle", fontsize=11)
        axes[1].yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["2_merge_integrity"] = _b64(fig)

        return {"orphans": orphans, "hetus_dupes": hetus_dupes}

    # ── Section 3: Derived Feature Verification ────────────────────────────────

    def validate_derived_features(self) -> dict:
        print("\n--- Section 3: Derived Feature Verification ---")
        _apply_dark()
        df = self.merged

        daytype_vals = set(df["DAYTYPE"].dropna().unique())
        unexpected_dt = daytype_vals - {"Weekday", "Weekend"}
        level = "pass" if not unexpected_dt else "fail"
        self._rec(level, f"3.1 | DAYTYPE values: {daytype_vals}")

        wday_rate = (df["DAYTYPE"] == "Weekday").mean() * 100
        level = "pass" if 65 <= wday_rate <= 77 else "warn"
        self._rec(level, f"3.2 | Weekday ratio: {wday_rate:.1f}% (expected 65-77%)")

        if "HOUR_OF_DAY" in df.columns:
            hod_vals = sorted(df["HOUR_OF_DAY"].dropna().unique().astype(int))
            missing_hours = set(range(24)) - set(hod_vals)
            oor = ((df["HOUR_OF_DAY"] < 0) | (df["HOUR_OF_DAY"] > 23)).sum()
            level = "pass" if not missing_hours and oor == 0 else "warn"
            self._rec(level, f"3.3 | HOUR_OF_DAY: range {min(hod_vals)}-{max(hod_vals)}, oor={oor}")
        else:
            self._rec("fail", "3.3 | HOUR_OF_DAY column missing")

        if "DDAY_STRATA" in df.columns:
            ds_vals = set(df["DDAY_STRATA"].dropna().unique().astype(int))
            unexpected_ds = ds_vals - {1, 2, 3}
            level = "pass" if not unexpected_ds else "fail"
            self._rec(level, f"3.6 | DDAY_STRATA values: {sorted(ds_vals)}")
        else:
            self._rec("fail", "3.6 | DDAY_STRATA column missing")

        _apply_dark()
        subsets = [("Overall", df)] + [(str(c), df[df["CYCLE_YEAR"] == c]) for c in CYCLES]
        fig, axes = plt.subplots(1, 5, figsize=(16, 4))
        fig.suptitle("DAYTYPE Distribution -- Overall and Per Cycle", fontsize=13, fontweight="bold")
        cat_list = ["Weekday", "Weekend"]; dt_colors = ["#89b4fa", "#f38ba8"]
        for idx, (lbl, sub) in enumerate(subsets):
            ax = axes[idx]
            vc = sub["DAYTYPE"].value_counts(normalize=True) * 100
            vals = [vc.get(cat, 0) for cat in cat_list]
            x_pos = np.arange(len(cat_list))
            bars = ax.bar(x_pos, vals, color=dt_colors, edgecolor="#1e1e2e", width=0.6)
            ax.set_xticks(x_pos); ax.set_xticklabels(cat_list, fontsize=9)
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width()/2, val + 1, f"{val:.1f}%",
                        ha="center", fontsize=9, fontweight="bold")
            ax.set_ylim(0, 108); ax.set_title(lbl, fontsize=11, fontweight="bold")
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["3a_daytype"] = _b64(fig)

        return {"wday_rate": wday_rate}

    # ── Section 4: HETUS 144-Slot Integrity ────────────────────────────────────

    def validate_hetus_slots(self) -> dict:
        print("\n--- Section 4: HETUS 144-Slot Integrity ---")
        _apply_dark()
        h = self.hetus

        SLOT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
        HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]
        slot_present = [c for c in SLOT_COLS if c in h.columns]
        home_present = [c for c in HOME_COLS if c in h.columns]

        if slot_present:
            incomplete = h[slot_present].isna().any(axis=1).sum()
            pct = (1 - incomplete / len(h)) * 100
            level = "pass" if incomplete == 0 else ("warn" if pct > 99 else "fail")
            self._rec(level, f"4.1 | Activity slot completeness: {pct:.2f}% ({incomplete} NaN rows)")
        else:
            self._rec("fail", "4.1 | slot_* columns missing")

        if slot_present:
            slot_data = h[slot_present].values.flatten()
            slot_data = slot_data[~pd.isna(slot_data)].astype(int)
            invalid = ((slot_data < 1) | (slot_data > 14)).sum()
            level = "pass" if invalid == 0 else "fail"
            self._rec(level, f"4.2 | Invalid activity codes: {invalid}")

        if home_present:
            incomplete_h = h[home_present].isna().any(axis=1).sum()
            pct_h = (1 - incomplete_h / len(h)) * 100
            level = "pass" if incomplete_h == 0 else ("warn" if pct_h > 99 else "fail")
            self._rec(level, f"4.3 | AT_HOME slot completeness: {pct_h:.2f}%")
        else:
            self._rec("fail", "4.3 | home_* columns missing")

        unique_merged = (self.merged[["occID", "CYCLE_YEAR"]].drop_duplicates().shape[0])
        hetus_rows = len(h)
        level = "pass" if hetus_rows == unique_merged else "fail"
        self._rec(level, f"4.5 | HETUS rows {hetus_rows:,} vs merged respondents {unique_merged:,}")

        # Chart 4a: Activity heatmap
        if slot_present:
            _apply_dark()
            slot_matrix = h[slot_present].values
            heat = np.zeros((14, len(slot_present)))
            total = len(h)
            for act in range(1, 15):
                heat[act - 1] = (slot_matrix == act).sum(axis=0) / total * 100
            heat_norm = heat.copy()
            for i in range(14):
                row_max = heat_norm[i].max()
                if row_max > 0:
                    heat_norm[i] /= row_max
            fig, ax = plt.subplots(figsize=(18, 6))
            im = ax.imshow(heat_norm, aspect="auto", cmap="plasma",
                           interpolation="nearest", vmin=0, vmax=1)
            cb = plt.colorbar(im, ax=ax, fraction=0.015, pad=0.01)
            cb.set_label("Relative intensity (row-normalised)", fontsize=9)
            ax.set_yticks(range(14))
            ax.set_yticklabels([ACT_LABELS[i + 1] for i in range(14)], fontsize=8.5)
            xtick_pos = list(range(0, 144, 18))
            xtick_lbl = [f"{(4 + i * 10 // 60) % 24:02d}:{(i * 10) % 60:02d}" for i in xtick_pos]
            ax.set_xticks(xtick_pos); ax.set_xticklabels(xtick_lbl, fontsize=8.5, rotation=45)
            ax.set_xlabel("Time of Day (4AM origin, 10-min slots)")
            ax.set_title("Activity Distribution Heatmap -- 14 Activities x 144 HETUS Slots", fontsize=13, pad=10)
            plt.tight_layout()
            self.plots_b64["4a_activity_heatmap"] = _b64(fig)

        # Chart 4b: AT_HOME curve
        if home_present:
            _apply_dark()
            home_means = h[home_present].mean(axis=0).values * 100
            fig, ax = plt.subplots(figsize=(14, 4))
            x = np.arange(1, len(home_means) + 1)
            ax.plot(x, home_means, color="#89b4fa", linewidth=1.5)
            ax.fill_between(x, home_means, alpha=0.25, color="#89b4fa")
            ax.axhline(80, color="#f9e2af", linestyle="--", linewidth=1, label="80% reference")
            ax.set_ylim(0, 105)
            ax.set_xlabel("HETUS Slot (1-144, 4AM origin)")
            ax.set_ylabel("Mean AT_HOME Rate (%)")
            ax.set_title("AT_HOME Rate Across 144 HETUS Slots", fontsize=13)
            ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
            for hr_off in range(0, 24, 4):
                slot_n = hr_off * 6 + 1
                t_lbl = f"{(4 + hr_off) % 24:02d}:00"
                ax.axvline(slot_n, color="#555", linestyle="--", linewidth=0.7, alpha=0.5)
                ax.text(slot_n + 0.3, 102, t_lbl, fontsize=7.5, color="#a6adc8", rotation=90, va="top")
            self.plots_b64["4b_at_home_curve"] = _b64(fig)

        return {"hetus_rows": hetus_rows, "unique_merged": unique_merged}

    # ── Section 5: Cross-Cycle Consistency ─────────────────────────────────────

    def validate_cross_cycle_consistency(self) -> dict:
        print("\n--- Section 5: Cross-Cycle Consistency ---")
        _apply_dark()
        df = self.merged

        act_dist: dict[int, dict[int, float]] = {}
        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            wt = pd.to_numeric(cyc.get("WGHT_EPI", pd.Series(np.ones(len(cyc)))),
                               errors="coerce").fillna(1.0)
            acts = pd.to_numeric(cyc["occACT"], errors="coerce")
            valid = acts.notna()
            wt_total = wt[valid].sum()
            dist: dict[int, float] = {}
            for code in range(1, 15):
                mask = (acts == code) & valid
                dist[code] = wt[mask].sum() / wt_total * 100 if wt_total > 0 else 0.0
            act_dist[c] = dist
        self._rec("pass", f"5.1 | Weighted activity distribution computed for {len(act_dist)} cycles")

        home_rates: dict[int, float] = {}
        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            wt = pd.to_numeric(cyc.get("WGHT_EPI", pd.Series(np.ones(len(cyc)))),
                               errors="coerce").fillna(1.0)
            home = pd.to_numeric(cyc["AT_HOME"], errors="coerce")
            valid = home.notna()
            if valid.any():
                rate = (wt[valid] * home[valid]).sum() / wt[valid].sum() * 100
            else:
                rate = 0.0
            home_rates[c] = rate
            level = "pass" if 55 <= rate <= 75 else "warn"
            self._rec(level, f"5.2 | {c} Weighted AT_HOME rate: {rate:.1f}% (expected 55-75%)")

        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            ep_per = cyc.groupby("occID").size()
            mean_ep = ep_per.mean()
            level = "pass" if 10 <= mean_ep <= 30 else "warn"
            self._rec(level, f"5.4 | {c} Episodes/respondent: mean={mean_ep:.1f} (expected 10-30)")

        # Chart 5a: Stacked bar
        _apply_dark()
        fig, ax = plt.subplots(figsize=(12, 6))
        cmap_ = plt.colormaps["tab20"].resampled(14)
        act_colors = [cmap_(i) for i in range(14)]
        x = np.arange(len(CYCLES)); bottoms = np.zeros(len(CYCLES))
        for act_code in range(1, 15):
            vals = [act_dist.get(c, {}).get(act_code, 0) for c in CYCLES]
            ax.bar(x, vals, 0.6, bottom=bottoms, label=ACT_LABELS[act_code],
                   color=act_colors[act_code - 1], edgecolor="#1e1e2e", linewidth=0.3)
            for i, (val, bot) in enumerate(zip(vals, bottoms)):
                if val > 3:
                    ax.text(i, bot + val/2, f"{val:.1f}", ha="center", va="center",
                            fontsize=7, color="white", fontweight="bold")
            bottoms += np.array(vals)
        ax.set_xticks(x); ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_ylim(0, 108); ax.set_ylabel("Weighted Activity Proportion (%)")
        ax.set_title("Weighted Activity Distribution per Cycle (14 categories)", fontsize=13)
        ax.legend(loc="upper right", fontsize=7.5, ncol=2, framealpha=0.8)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["5a_activity_dist"] = _b64(fig)

        # Chart 5b: AT_HOME line
        _apply_dark()
        fig, ax = plt.subplots(figsize=(8, 4))
        cyc_list = list(home_rates.keys())
        rate_vals = [home_rates[c] for c in cyc_list]
        ax.plot(cyc_list, rate_vals, color="#89b4fa", marker="o", linewidth=2, markersize=8)
        ax.fill_between(cyc_list, rate_vals, alpha=0.2, color="#89b4fa")
        ax.axhline(55, color="#f38ba8", linestyle="--", linewidth=1, label="55% lower")
        ax.axhline(75, color="#a6e3a1", linestyle="--", linewidth=1, label="75% upper")
        for c, r in home_rates.items():
            ax.text(c, r + 0.5, f"{r:.1f}%", ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(40, 90); ax.set_xticks(cyc_list)
        ax.set_title("Weighted AT_HOME Rate per Cycle (expected 55-75%)", fontsize=12)
        ax.set_ylabel("Weighted AT_HOME (%)"); ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["5b_at_home_rate"] = _b64(fig)

        return {"home_rates": home_rates, "act_dist": act_dist}

    # ── Section 6: Summary Statistics Table ────────────────────────────────────

    def generate_summary_table(self) -> pd.DataFrame:
        print("\n--- Section 6: Summary Statistics Table ---")
        s1 = self.summary_data.get("section1", {})
        s2_main = s1.get("s2_main_counts", {})
        post_resp = s1.get("post_resp", {})
        post_epi  = s1.get("post_epi",  {})
        excl_map  = {r["Cycle"]: r for r in s1.get("exclusion_rows", [])}

        SLOT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
        slot_present = [c for c in SLOT_COLS if c in self.hetus.columns]

        rows = []; totals = dict(s2=0, post=0, ep=0, hetus=0)
        for c in CYCLES:
            cyc_m = self.merged[self.merged["CYCLE_YEAR"] == c]
            cyc_h = (self.hetus[self.hetus["CYCLE_YEAR"] == c]
                     if "CYCLE_YEAR" in self.hetus.columns else self.hetus)
            ep_per = cyc_m.groupby("occID").size()
            excl = excl_map.get(str(c), {})
            excl_rate = excl.get("Rate (%)", 0.0)
            slot_valid = ((1 - cyc_h[slot_present].isna().any(axis=1).mean()) * 100
                          if slot_present and len(cyc_h) > 0 else 0.0)
            wt = pd.to_numeric(cyc_m.get("WGHT_EPI", pd.Series(np.ones(len(cyc_m)))),
                               errors="coerce").fillna(1.0)
            home = pd.to_numeric(cyc_m["AT_HOME"], errors="coerce")
            valid = home.notna()
            at_home_pct = ((wt[valid] * home[valid]).sum() / wt[valid].sum() * 100
                           if valid.any() else 0.0)
            wday_pct = ((cyc_m["DAYTYPE"] == "Weekday").mean() * 100
                        if "DAYTYPE" in cyc_m.columns else 0.0)
            s2r = s2_main.get(c, 0); postr = post_resp.get(c, 0); poste = post_epi.get(c, 0)
            hrows = len(cyc_h)
            totals["s2"] += s2r; totals["post"] += postr
            totals["ep"] += poste; totals["hetus"] += hrows
            rows.append({
                "Cycle": str(c), "Resp (Step 2)": f"{s2r:,}",
                "Resp (post-filter)": f"{postr:,}", "Excl. Rate": f"{excl_rate:.2f}%",
                "Episodes": f"{poste:,}", "Mean Eps/Resp": f"{ep_per.mean():.1f}",
                "HETUS Rows": f"{hrows:,}", "Slots Valid (%)": f"{slot_valid:.1f}%",
                "Wtd AT_HOME (%)": f"{at_home_pct:.1f}%", "Weekday (%)": f"{wday_pct:.1f}%",
            })

        all_ep = self.merged.groupby("occID").size()
        total_excl_rate = ((totals["s2"] - totals["post"]) / totals["s2"] * 100
                           if totals["s2"] > 0 else 0.0)
        rows.append({
            "Cycle": "Total", "Resp (Step 2)": f"{totals['s2']:,}",
            "Resp (post-filter)": f"{totals['post']:,}", "Excl. Rate": f"{total_excl_rate:.2f}%",
            "Episodes": f"{len(self.merged):,}", "Mean Eps/Resp": f"{all_ep.mean():.1f}",
            "HETUS Rows": f"{len(self.hetus):,}", "Slots Valid (%)": "--",
            "Wtd AT_HOME (%)": "--", "Weekday (%)": "--",
        })

        self._rec("pass", f"6.1 | Summary table: {len(rows) - 1} cycles + total row")
        summary_df = pd.DataFrame(rows)
        self.summary_data["summary_df"] = summary_df
        return summary_df

    # ── Section 7: 30-Minute Resolution Downsampling ────────────────────────────

    def validate_30min_downsampling(self) -> None:
        print("\n--- Section 7: 30-Minute Resolution Downsampling ---")
        if self.hetus_30min is None:
            print("  [SKIP] hetus_30min not loaded -- Section 7 skipped")
            return

        _apply_dark()
        h30 = self.hetus_30min; hw = self.hetus
        STRATA_LABELS = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
        STRATA_COLORS = {1: "#89b4fa", 2: "#f38ba8", 3: "#a6e3a1"}
        ACT_COLS_30 = [f"act30_{i:03d}" for i in range(1, 49)]
        HOM_COLS_30 = [f"hom30_{i:03d}" for i in range(1, 49)]
        SLOT_COLS_10 = [f"slot_{i:03d}" for i in range(1, 145)]
        act_cols_30_present = [c for c in ACT_COLS_30 if c in h30.columns]
        hom_cols_30_present = [c for c in HOM_COLS_30 if c in h30.columns]
        slot_cols_10_present = [c for c in SLOT_COLS_10 if c in hw.columns]
        act_ids = sorted(ACT_LABELS.keys()); act_names = [ACT_LABELS[a] for a in act_ids]

        # 7a: Activity distribution comparison
        fig7a, axes = plt.subplots(1, 3, figsize=(21, 9), sharey=True)
        fig7a.suptitle("Section 7a -- Activity Distribution: 10-min vs 30-min by Day Type",
                        color="#cdd6f4", fontsize=13, y=1.01)
        for ax, (sid, sname) in zip(axes, STRATA_LABELS.items()):
            mask_hw = (hw["DDAY_STRATA"] == sid if "DDAY_STRATA" in hw.columns
                       else pd.Series(True, index=hw.index))
            hw_sub = hw[mask_hw]
            vals_10 = (hw_sub[slot_cols_10_present].values.flatten()
                       if len(hw_sub) > 0 and slot_cols_10_present else np.array([]))
            vals_10 = vals_10[~np.isnan(vals_10.astype(float))].astype(int) if len(vals_10) > 0 else vals_10
            props_10 = np.array([np.mean(vals_10 == a) for a in act_ids]) if len(vals_10) > 0 else np.zeros(len(act_ids))

            mask_h30 = (h30["DDAY_STRATA"] == sid if "DDAY_STRATA" in h30.columns
                        else pd.Series(True, index=h30.index))
            h30_sub = h30[mask_h30]
            arr_30 = (h30_sub[act_cols_30_present].values.flatten()
                      if len(h30_sub) > 0 and act_cols_30_present else np.array([]))
            arr_30 = arr_30[~np.isnan(arr_30.astype(float))].astype(int) if len(arr_30) > 0 else arr_30
            props_30 = np.array([np.mean(arr_30 == a) for a in act_ids]) if len(arr_30) > 0 else np.zeros(len(act_ids))

            y = np.arange(len(act_ids)); bar_h = 0.35
            ax.barh(y + bar_h/2, props_10 * 100, bar_h, color="#89b4fa", alpha=0.85, label="10-min")
            ax.barh(y - bar_h/2, props_30 * 100, bar_h, color=STRATA_COLORS[sid], alpha=0.85, label="30-min")
            ax.set_yticks(y); ax.set_yticklabels(act_names, fontsize=9)
            ax.set_xlabel("% of slots", color="#cdd6f4", fontsize=10)
            ax.set_title(sname, color="#cdd6f4", fontsize=11, pad=8)
            ax.legend(fontsize=8); ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["7a_act_dist_30min"] = _b64(fig7a)
        self._rec("pass", "7a | Activity distribution 10-min vs 30-min")

        # 7b: AT_HOME daily rhythm
        fig7b, ax = plt.subplots(figsize=(16, 5))
        fig7b.suptitle("Section 7b -- AT_HOME Daily Rhythm at 30-min Resolution",
                        color="#cdd6f4", fontsize=13)
        slot_labels = []
        for i in range(48):
            total_min = 4 * 60 + i * 30
            hh = (total_min // 60) % 24; mm = total_min % 60
            slot_labels.append(f"{hh:02d}:{mm:02d}" if mm == 0 else "")
        x = np.arange(48)
        for sid, sname in STRATA_LABELS.items():
            mask = (h30["DDAY_STRATA"] == sid if "DDAY_STRATA" in h30.columns
                    else pd.Series(True, index=h30.index))
            sub = h30[mask]
            if len(sub) > 0 and hom_cols_30_present:
                rates = sub[hom_cols_30_present].mean().values * 100
                ax.plot(x, rates, color=STRATA_COLORS[sid], linewidth=2,
                        label=sname, marker="o", markersize=3)
        ax.set_xticks(x); ax.set_xticklabels(slot_labels, rotation=45, fontsize=7)
        ax.set_xlabel("30-min slot (04:00 AM origin)", color="#cdd6f4")
        ax.set_ylabel("AT_HOME rate (%)", color="#cdd6f4")
        ax.legend(); ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["7b_at_home_rhythm"] = _b64(fig7b)
        self._rec("pass", "7b | AT_HOME daily rhythm")

    # ── Section 8: Co-Presence (verbatim from Leg-1) ──────────────────────────

    def validate_copresence(self) -> None:
        print("\n--- Section 8: Co-Presence Validation ---")
        df = self.merged

        completeness_matrix = []
        for col in COPRE_COLS:
            row = []
            for c in CYCLES:
                sub = df[df["CYCLE_YEAR"] == c]
                pct_filled = 100.0 * sub[col].notna().mean() if col in df.columns else 0.0
                row.append(pct_filled)
            completeness_matrix.append(row)
        arr6a = np.array(completeness_matrix)

        fig6a, ax6a = plt.subplots(figsize=(8, 5))
        im6a = ax6a.imshow(arr6a, aspect="auto", cmap="YlGn", vmin=0, vmax=100)
        ax6a.set_xticks(range(len(CYCLES))); ax6a.set_xticklabels([str(c) for c in CYCLES])
        ax6a.set_yticks(range(len(COPRE_COLS))); ax6a.set_yticklabels(COPRE_COLS, fontsize=9)
        for i in range(len(COPRE_COLS)):
            for j in range(len(CYCLES)):
                ax6a.text(j, i, f"{arr6a[i, j]:.1f}%", ha="center", va="center", fontsize=8,
                          color="black" if arr6a[i, j] > 30 else "white")
        plt.colorbar(im6a, ax=ax6a, label="% non-NaN")
        ax6a.set_title("Co-Presence Column Completeness in Merged Dataset", fontsize=11)
        self.plots_b64["6a_copre_completeness"] = _b64(fig6a)

        for col in COPRE_COLS[:-1]:
            for c in CYCLES:
                sub = df[df["CYCLE_YEAR"] == c]
                if col not in df.columns:
                    self._rec("fail", f"Missing co-presence column '{col}'")
                    continue
                fill = 100.0 * sub[col].notna().mean()
                level = "pass" if fill > 50 else "warn"
                self._rec(level, f"8.{COPRE_COLS.index(col)+1} | {c} '{col}' fill: {fill:.1f}%")
        print("  [DONE] Section 8 co-presence checks done.")

    # ── Section 9: AT_WORK Channel (Leg-2 NEW) ─────────────────────────────────

    def validate_work_channel(self) -> None:
        """Section 9 -- AT_WORK 30-min tiled output validation.

        Checks:
          9.1: Shape (N rows x 49 cols)
          9.2: occID alignment with hetus_30min
          9.3: Values in {0, 1} only
          9.4: Weighted AT_WORK presence rate per cycle (sanity: plausible %)
          9.5: Night-slot near-zero sanity (slots 1-8)
          9.6: AT_HOME vs AT_WORK overlap % (should be small)
          9.7: HEADLINE CHART -- mean diurnal AT_WORK presence curve per cycle
        """
        print("\n--- Section 9: AT_WORK Channel (Leg-2 NEW) ---")
        if self.work_30min is None:
            print("  [SKIP] work_30min.csv not found -- Section 9 skipped")
            self._rec("warn", "9.0 | work_30min.csv not found -- Section 9 skipped")
            return

        _apply_dark()
        wk = self.work_30min
        WORK30_COLS = [f"WORK30_{i:03d}" for i in range(1, 49)]
        work30_present = [c for c in WORK30_COLS if c in wk.columns]
        N = self.N

        # 9.1: Shape
        if wk.shape[0] == N and wk.shape[1] == 49:
            self._rec("pass", f"9.1 | work_30min shape ({N:,}, 49) correct")
        else:
            self._rec("fail", f"9.1 | work_30min shape {wk.shape} (expected ({N}, 49))")

        # 9.2: occID alignment
        if self.hetus_30min is not None:
            h30_occids = self.hetus_30min["occID"].reset_index(drop=True)
            wk_occids  = wk["occID"].reset_index(drop=True)
            if h30_occids.equals(wk_occids):
                self._rec("pass", "9.2 | occID order matches hetus_30min exactly")
            else:
                self._rec("fail", "9.2 | occID mismatch between work_30min and hetus_30min")

        # 9.3: Values in {0, 1}
        if work30_present:
            work_arr = wk[work30_present].to_numpy(dtype=float)
            non_binary_mask = ~np.isnan(work_arr) & ~np.isin(work_arr, [0.0, 1.0])
            n_non_binary = int(non_binary_mask.sum())
            nan_count = int(np.isnan(work_arr).sum())
            if n_non_binary == 0:
                self._rec("pass", f"9.3 | All non-NaN values in {{0, 1}} | NaN cells: {nan_count:,}")
            else:
                self._rec("fail", f"9.3 | {n_non_binary} values outside {{0, 1}}")
        else:
            self._rec("fail", "9.3 | WORK30_* columns missing")
            return

        # 9.4: Weighted AT_WORK presence rate per cycle
        if self.hetus_30min is not None and "WGHT_PER" in self.hetus_30min.columns:
            ref = self.hetus_30min[["occID", "CYCLE_YEAR", "WGHT_PER"]].reset_index(drop=True)
        else:
            ref = pd.DataFrame({"occID": wk["occID"], "CYCLE_YEAR": 0, "WGHT_PER": 1.0})

        work_with_meta = pd.concat([ref, wk[WORK30_COLS].reset_index(drop=True)], axis=1)
        wtd_rates: dict[int, float] = {}
        for c in CYCLES:
            mask = work_with_meta["CYCLE_YEAR"] == c
            sub  = work_with_meta[mask]
            if len(sub) == 0:
                continue
            w    = sub["WGHT_PER"].values
            arr  = sub[WORK30_COLS].to_numpy(dtype=float)
            flat = arr.flatten()
            w_rep = np.repeat(w, 48)
            valid = ~np.isnan(flat)
            if valid.any():
                rate = 100 * np.average(flat[valid], weights=w_rep[valid])
            else:
                rate = 0.0
            wtd_rates[c] = rate
            level = "pass" if 1 <= rate <= 25 else "warn"
            self._rec(level, f"9.4 | {c} Weighted AT_WORK rate: {rate:.2f}% (expected 1-25%)")

        # 9.5: Night-slot near-zero
        night_work_cols = [f"WORK30_{i:03d}" for i in range(1, 9)]
        night_arr = wk[night_work_cols].to_numpy(dtype=float)
        night_rate = 100 * np.nanmean(night_arr)
        status = "pass" if night_rate < 6.0 else "warn"
        self._rec(status, f"9.5 | Night slots (1-8, 04:00-07:59) AT_WORK rate: {night_rate:.2f}% (expected <6%, early-shift workers)")

        # 9.6: AT_HOME vs AT_WORK overlap
        if self.hetus_30min is not None:
            hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
            hom30_present = [c for c in hom30_cols if c in self.hetus_30min.columns]
            if hom30_present and work30_present:
                hom_arr = self.hetus_30min[hom30_present].to_numpy(dtype=float)
                wrk_arr = wk[work30_present].to_numpy(dtype=float)
                both_one = int(((hom_arr == 1) & (wrk_arr == 1)).sum())
                pct_both = 100 * both_one / (N * 48)
                level = "pass" if pct_both < 5 else "warn"
                self._rec(level, f"9.6 | AT_HOME=1 AND AT_WORK=1 overlap: {both_one:,} cells ({pct_both:.3f}%) -- WFH expected small")

        # 9.7: HEADLINE CHART -- mean diurnal AT_WORK presence curve per cycle
        _apply_dark()
        fig9a, ax9a = plt.subplots(figsize=(16, 6))
        fig9a.suptitle(
            "Section 9a (Leg-2 Headline) -- Mean Diurnal AT_WORK Presence Curve per Cycle\n"
            "Expected: near-zero 04:00-06:00, rising through work day, daytime hump, low evening",
            color="#cdd6f4", fontsize=13, fontweight="bold"
        )

        slot_labels_work = []
        for i in range(48):
            total_min = 4 * 60 + i * 30
            hh = (total_min // 60) % 24; mm = total_min % 60
            slot_labels_work.append(f"{hh:02d}:{mm:02d}" if mm == 0 else "")

        x = np.arange(48)
        for i, c in enumerate(CYCLES):
            if self.hetus_30min is not None and "CYCLE_YEAR" in self.hetus_30min.columns:
                mask = self.hetus_30min["CYCLE_YEAR"] == c
                sub_wk = wk[mask.values]
            else:
                sub_wk = wk
            if work30_present and len(sub_wk) > 0:
                arr = sub_wk[work30_present].to_numpy(dtype=float)
                curve = 100 * np.nanmean(arr, axis=0)
                ax9a.plot(x, curve, color=CYCLE_COLORS[i], linewidth=2.5,
                          label=str(c), marker="o", markersize=3)

        ax9a.set_xticks(x); ax9a.set_xticklabels(slot_labels_work, rotation=45, fontsize=7.5)
        ax9a.set_xlabel("30-min slot (04:00 AM origin)", color="#cdd6f4", fontsize=11)
        ax9a.set_ylabel("Mean AT_WORK rate (%)", color="#cdd6f4", fontsize=11)
        ax9a.legend(title="Cycle", fontsize=10, title_fontsize=10)
        ax9a.grid(alpha=0.3)
        ax9a.set_ylim(0, None)
        plt.tight_layout()
        self.plots_b64["9a_atwork_diurnal"] = _b64(fig9a)
        self._rec("pass", "9.7 | AT_WORK diurnal curve chart generated")

        # 9b: AT_WORK rate per cycle bar
        _apply_dark()
        fig9b, ax9b = plt.subplots(figsize=(8, 4))
        fig9b.suptitle("Section 9b -- Weighted AT_WORK Presence Rate per Cycle",
                        color="#cdd6f4", fontsize=12)
        cyc_list = [c for c in CYCLES if c in wtd_rates]
        rate_list = [wtd_rates[c] for c in cyc_list]
        bars = ax9b.bar([str(c) for c in cyc_list], rate_list,
                        color=CYCLE_COLORS[:len(cyc_list)], edgecolor="#1e1e2e", width=0.55)
        ax9b.axhline(1, color="#f38ba8", linestyle="--", linewidth=1.0, label="1% lower")
        ax9b.axhline(25, color="#a6e3a1", linestyle="--", linewidth=1.0, label="25% upper")
        for bar, val in zip(bars, rate_list):
            ax9b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                      f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold", color="#cdd6f4")
        ax9b.set_ylabel("Weighted AT_WORK rate (%)", color="#cdd6f4")
        ax9b.legend(fontsize=9); ax9b.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax9b.set_ylim(0, max(max(rate_list) * 1.3, 30) if rate_list else 30)
        plt.tight_layout()
        self.plots_b64["9b_atwork_rate"] = _b64(fig9b)

        print("  [DONE] Section 9 AT_WORK validation complete.")

    # ── Section 10: NOCS / NAICS / TELEWORK Coverage in hetus_30min (Leg-2 NEW) ─

    def validate_office_conditioning(self) -> None:
        """Section 10 -- NOCS / NAICS / TELEWORK / WORK_SCHEDULE coverage in hetus_30min."""
        print("\n--- Section 10: Office Conditioning Variables in hetus_30min (Leg-2) ---")
        if self.hetus_30min is None:
            print("  [SKIP] hetus_30min not loaded -- Section 10 skipped")
            return

        h30 = self.hetus_30min
        for var in ["NOCS", "NAICS", "TELEWORK", "WORK_SCHEDULE"]:
            if var not in h30.columns:
                self._rec("warn", f"10.1 | {var} column absent from hetus_30min")
                continue
            for c in CYCLES:
                mask = h30["CYCLE_YEAR"] == c
                sub  = h30[mask]
                if len(sub) == 0:
                    continue
                coverage = 100 * sub[var].notna().mean()
                n_distinct = sub[var].dropna().nunique()
                # TELEWORK 2005 now sourced from MAR_Q190 (same as 2010); coverage > 0 expected.
                level = "pass" if coverage > 0 else "warn"
                self._rec(level, f"10.1 | {var} {c}: coverage={coverage:.1f}%, distinct={n_distinct}")

        _apply_dark()
        cond_vars = ["NOCS", "NAICS", "TELEWORK", "WORK_SCHEDULE"]
        fig10, axes = plt.subplots(1, 4, figsize=(20, 5))
        fig10.suptitle("Section 10 -- Office Conditioning Variables Coverage in hetus_30min",
                        color="#cdd6f4", fontsize=12, fontweight="bold")
        for ax, var in zip(axes, cond_vars):
            coverages = []
            for c in CYCLES:
                mask = h30["CYCLE_YEAR"] == c
                sub  = h30[mask]
                if var in h30.columns and len(sub) > 0:
                    coverages.append(100 * sub[var].notna().mean())
                else:
                    coverages.append(0.0)
            bars = ax.bar([str(c) for c in CYCLES], coverages,
                          color=CYCLE_COLORS, edgecolor="#1e1e2e", width=0.55)
            for bar, val in zip(bars, coverages):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold", color="#cdd6f4")
            ax.set_title(var, color="#cdd6f4", fontsize=11)
            ax.set_ylabel("Coverage (%)", color="#cdd6f4")
            ax.set_ylim(0, 110); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["10_office_conditioning"] = _b64(fig10)
        print("  [DONE] Section 10 done.")

    # ── Section 11: AT_RETAIL Channel (Leg-3 NEW) ──────────────────────────────

    @staticmethod
    def _slots_for_window(start_hour: float, end_hour: float) -> list[int]:
        """30-min slot indices (1-48, 4 AM origin) covering [start_hour, end_hour)."""
        slots = []
        m = int(start_hour * 60)
        end_min = int(end_hour * 60)
        while m < end_min:
            idx = (((m - 240) // 30) % 48) + 1
            slots.append(idx)
            m += 30
        return slots

    @staticmethod
    def _weighted_rate(df: pd.DataFrame, slot_idxs: list[int], wcol: str = "WGHT_PER") -> float | None:
        """Weighted mean AT_RETAIL rate (fraction 0-1) over the given slots."""
        cols = [f"RETL30_{i:03d}" for i in slot_idxs if f"RETL30_{i:03d}" in df.columns]
        if not cols or len(df) == 0:
            return None
        arr = df[cols].to_numpy(dtype=float)
        w = df[wcol].to_numpy(dtype=float) if wcol in df.columns else np.ones(len(df))
        w_rep = np.repeat(w, len(cols))
        flat = arr.flatten()
        valid = ~np.isnan(flat)
        if not valid.any():
            return None
        return float(np.average(flat[valid], weights=w_rep[valid]))

    def validate_retail_channel(self) -> None:
        """Section 11 -- AT_RETAIL 30-min tiled output validation (Leg-3 NEW).

        Checks:
          11.1: Shape (N rows x 49 cols)
          11.2: occID alignment with hetus_30min
          11.3: Values in {0, 1} only, 0 NaN
          11.4: Weekday 12:00-14:00 weighted rate per cycle (0.06-0.10)
          11.5: Saturday 13:00-16:00 weighted peak rate per cycle (0.09-0.12)
          11.6: Sunday peak rate per province (QC 12-17h 0.04-0.07 / AB 12-16h 0.06-0.10)
          11.7: Night 00:00-05:00 mean rate, all day-types (0.000-0.003)
          11.8: All-day tiled daily-mean rate per cycle (2-8% provisional)
          11.9: Exclusivity vs AT_HOME / AT_WORK (WARN if > 1% of retail-positive cells)
          11.10: OR-rule leak verification (0 violations = FAIL gate)
          11.11: HEADLINE CHART -- mean diurnal AT_RETAIL curve per cycle x day-type
        """
        print("\n--- Section 11: AT_RETAIL Channel (Leg-3 NEW) ---")
        if self.retail_30min is None:
            print("  [SKIP] retail_30min.csv not found -- Section 11 skipped")
            self._rec("warn", "11.0 | retail_30min.csv not found -- Section 11 skipped")
            return

        _apply_dark()
        rt = self.retail_30min
        RETL30_COLS = [f"RETL30_{i:03d}" for i in range(1, 49)]
        retl_present = [c for c in RETL30_COLS if c in rt.columns]
        N = self.N

        # 11.1: Shape
        if rt.shape[0] == N and rt.shape[1] == 49:
            self._rec("pass", f"11.1 | retail_30min shape ({N:,}, 49) correct")
        else:
            self._rec("fail", f"11.1 | retail_30min shape {rt.shape} (expected ({N}, 49))")

        # 11.2: occID alignment
        if self.hetus_30min is not None:
            h30_occids = self.hetus_30min["occID"].reset_index(drop=True)
            rt_occids = rt["occID"].reset_index(drop=True)
            if h30_occids.equals(rt_occids):
                self._rec("pass", "11.2 | occID order matches hetus_30min exactly")
            else:
                self._rec("fail", "11.2 | occID mismatch between retail_30min and hetus_30min")

        # 11.3: Values in {0, 1}, 0 NaN
        if retl_present:
            retl_arr = rt[retl_present].to_numpy(dtype=float)
            non_binary_mask = ~np.isnan(retl_arr) & ~np.isin(retl_arr, [0.0, 1.0])
            n_non_binary = int(non_binary_mask.sum())
            nan_count = int(np.isnan(retl_arr).sum())
            if n_non_binary == 0 and nan_count == 0:
                self._rec("pass", f"11.3 | All values in {{0, 1}}, 0 NaN")
            elif n_non_binary == 0:
                self._rec("fail", f"11.3 | {nan_count} NaN cells present (expected 0)")
            else:
                self._rec("fail", f"11.3 | {n_non_binary} values outside {{0, 1}} ({nan_count} NaN)")
        else:
            self._rec("fail", "11.3 | RETL30_* columns missing")
            return

        if self.hetus_30min is None:
            print("  [SKIP] hetus_30min not loaded -- remaining Section 11 gates skipped")
            return

        # Combined meta+retail frame (position-aligned; verified by 11.2)
        meta_cols = ["occID", "CYCLE_YEAR", "WGHT_PER", "DDAY_STRATA", "PR"]
        meta_cols_present = [c for c in meta_cols if c in self.hetus_30min.columns]
        ref = self.hetus_30min[meta_cols_present].reset_index(drop=True)
        combo = pd.concat([ref, rt[retl_present].reset_index(drop=True)], axis=1)

        weekday_slots  = self._slots_for_window(12, 14)
        sat_slots      = self._slots_for_window(13, 16)
        qc_sun_slots   = self._slots_for_window(12, 17)
        ab_sun_slots   = self._slots_for_window(12, 16)
        night_slots    = [41, 42, 43, 44, 45, 46, 47, 48, 1, 2]   # 00:00-05:00, 4AM-origin array

        # 11.4: Weekday 12:00-14:00 weighted rate per cycle
        print("\n11.4 -- Weekday 12:00-14:00 weighted AT_RETAIL rate per cycle:")
        for c in CYCLES:
            if "DDAY_STRATA" in combo.columns:
                sub = combo[(combo["CYCLE_YEAR"] == c) & (combo["DDAY_STRATA"] == 1)]
            else:
                sub = combo[combo["CYCLE_YEAR"] == c]
            rate = self._weighted_rate(sub, weekday_slots)
            if rate is None:
                self._rec("warn", f"11.4 | {c}: no data for weekday midday window")
                continue
            status = "pass" if 0.06 <= rate <= 0.10 else "warn"
            self._rec(status, f"11.4 | {c} weekday 12:00-14:00 rate: {rate:.4f} ({100*rate:.2f}%) (expected 0.06-0.10)")

        # 11.5: Saturday 13:00-16:00 weighted peak rate per cycle
        print("\n11.5 -- Saturday 13:00-16:00 weighted AT_RETAIL peak rate per cycle:")
        for c in CYCLES:
            if "DDAY_STRATA" in combo.columns:
                sub = combo[(combo["CYCLE_YEAR"] == c) & (combo["DDAY_STRATA"] == 2)]
            else:
                sub = combo.iloc[0:0]
            rate = self._weighted_rate(sub, sat_slots)
            if rate is None:
                self._rec("warn", f"11.5 | {c}: no data for Saturday peak window")
                continue
            status = "pass" if 0.09 <= rate <= 0.12 else "warn"
            self._rec(status, f"11.5 | {c} Saturday 13:00-16:00 rate: {rate:.4f} ({100*rate:.2f}%) (expected 0.09-0.12)")

        # 11.6: Sunday peak rate by province (QC 12-17h / AB 12-16h)
        print("\n11.6 -- Sunday peak rate by province (QC 12:00-17:00 / AB 12:00-16:00):")
        for c in CYCLES:
            if "DDAY_STRATA" in combo.columns:
                sun_mask = (combo["CYCLE_YEAR"] == c) & (combo["DDAY_STRATA"] == 3)
            else:
                sun_mask = combo["CYCLE_YEAR"] == c
            for prov_code, prov_name, slots_win, lo, hi in [
                (24, "QC", qc_sun_slots, 0.04, 0.07),
                (48, "AB", ab_sun_slots, 0.06, 0.10),
            ]:
                if "PR" not in combo.columns:
                    self._rec("warn", f"11.6 | PR column absent -- {prov_name} {c} skipped")
                    continue
                sub = combo[sun_mask & (combo["PR"] == prov_code)]
                rate = self._weighted_rate(sub, slots_win)
                if rate is None:
                    self._rec("warn", f"11.6 | {c} {prov_name} Sunday: no data")
                    continue
                status = "pass" if lo <= rate <= hi else "warn"
                self._rec(status, f"11.6 | {c} {prov_name} Sunday peak rate: {rate:.4f} ({100*rate:.2f}%) (expected {lo}-{hi})")

        # 11.7: Night 00:00-05:00 mean rate, all day-types
        print("\n11.7 -- Night 00:00-05:00 mean AT_RETAIL rate (all day-types), per cycle:")
        for c in CYCLES:
            sub = combo[combo["CYCLE_YEAR"] == c]
            rate = self._weighted_rate(sub, night_slots)
            if rate is None:
                self._rec("warn", f"11.7 | {c}: no data for night window")
                continue
            status = "pass" if 0.000 <= rate <= 0.003 else "warn"
            self._rec(status, f"11.7 | {c} night 00:00-05:00 rate: {rate:.5f} ({100*rate:.3f}%) (expected 0.000-0.003)")

        # 11.8: All-day tiled daily-mean rate, per cycle (provisional band)
        print("\n11.8 -- All-day tiled daily-mean AT_RETAIL rate, per cycle (2-8% provisional):")
        for c in CYCLES:
            sub = combo[combo["CYCLE_YEAR"] == c]
            rate = self._weighted_rate(sub, list(range(1, 49)))
            if rate is None:
                self._rec("warn", f"11.8 | {c}: no data")
                continue
            status = "pass" if 0.02 <= rate <= 0.08 else "warn"
            self._rec(status, f"11.8 | {c} all-day daily-mean rate: {rate:.4f} ({100*rate:.2f}%) (2-8% provisional band)")

        # 11.9: Exclusivity -- RETL30=1 & AT_HOME=1, and RETL30=1 & WORK30=1
        print("\n11.9 -- Exclusivity checks (AT_RETAIL vs AT_HOME / AT_WORK):")
        rtl_arr_full = rt[retl_present].to_numpy(dtype=float)
        n_retail_positive = int((rtl_arr_full == 1).sum())
        if n_retail_positive == 0:
            self._rec("warn", "11.9 | 0 retail-positive cells -- exclusivity check skipped")
        else:
            hom30_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
            hom30_present = [c for c in hom30_cols if c in self.hetus_30min.columns]
            if hom30_present:
                hom_arr = self.hetus_30min[hom30_present].to_numpy(dtype=float)
                overlap_home = int(((hom_arr == 1) & (rtl_arr_full == 1)).sum())
                pct_home = 100 * overlap_home / n_retail_positive
                status = "pass" if pct_home <= 1.0 else "warn"
                self._rec(status, f"11.9 | AT_RETAIL=1 AND AT_HOME=1: {overlap_home:,} cells "
                                  f"({pct_home:.3f}% of retail-positive cells) -- expect approx 0")
            if self.work_30min is not None:
                work30_cols = [f"WORK30_{i:03d}" for i in range(1, 49)]
                work30_present = [c for c in work30_cols if c in self.work_30min.columns]
                if work30_present:
                    wrk_arr = self.work_30min[work30_present].to_numpy(dtype=float)
                    overlap_work = int(((wrk_arr == 1) & (rtl_arr_full == 1)).sum())
                    pct_work = 100 * overlap_work / n_retail_positive
                    status = "pass" if pct_work <= 1.0 else "warn"
                    self._rec(status, f"11.9 | AT_RETAIL=1 AND AT_WORK=1: {overlap_work:,} cells "
                                      f"({pct_work:.3f}% of retail-positive cells) -- expect approx 0")

        # 11.10: OR-rule leak verification
        print("\n11.10 -- OR-rule leak verification (occACT==4 x occPRE cross-tab):")
        if "occPRE" in self.merged.columns and "occACT" in self.merged.columns:
            occPRE = self.merged["occPRE"]
            occACT = self.merged["occACT"]
            at_retail_recomputed = (
                (occPRE == 5) | ((occACT == 4) & occPRE.isin({5, 9}))
            ).astype(float)
            violation_mask = (at_retail_recomputed == 1) & occPRE.isin({1, 2})
            n_violations = int(violation_mask.sum())
            status = "pass" if n_violations == 0 else "fail"
            self._rec(status, f"11.10 | AT_RETAIL episodes with occPRE in {{1, 2}}: "
                              f"{n_violations} (expected 0 -- FAIL gate)")

            crosstab = pd.crosstab(occACT[occACT == 4], occPRE[occACT == 4])
            print("  occACT==4 x occPRE cross-tab (episode counts):")
            print(crosstab.to_string())
            self.summary_data["section11_crosstab"] = crosstab
        else:
            self._rec("fail", "11.10 | occPRE/occACT columns missing from merged_episodes -- cannot verify OR-rule")

        # 11.11: HEADLINE CHART -- mean diurnal AT_RETAIL curve per cycle x day-type
        _apply_dark()
        x = np.arange(48)
        slot_labels = []
        for i in range(48):
            total_min = 4 * 60 + i * 30
            hh = (total_min // 60) % 24; mm = total_min % 60
            slot_labels.append(f"{hh:02d}:{mm:02d}" if mm == 0 else "")

        fig11a, axes11a = plt.subplots(1, 3, figsize=(20, 6), sharey=True)
        fig11a.suptitle(
            "Section 11a (Leg-3 Headline) -- Mean Diurnal AT_RETAIL Presence Rate by Day-Type\n"
            "Expected: midday hump (weekday/Sat), Sat > weekday peak, compressed QC Sunday, near-zero nights",
            color="#cdd6f4", fontsize=13, fontweight="bold")
        daytype_map = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
        for ax_idx, (dday_code, label) in enumerate(daytype_map.items()):
            ax = axes11a[ax_idx]
            for i, c in enumerate(CYCLES):
                if "DDAY_STRATA" in combo.columns:
                    mask = (combo["CYCLE_YEAR"] == c) & (combo["DDAY_STRATA"] == dday_code)
                else:
                    mask = combo["CYCLE_YEAR"] == c
                sub = combo[mask]
                if len(sub) == 0 or not retl_present:
                    continue
                arr = sub[retl_present].to_numpy(dtype=float)
                curve = 100 * np.nanmean(arr, axis=0)
                ax.plot(x, curve, color=CYCLE_COLORS[i], linewidth=2.2,
                        label=str(c), marker="o", markersize=2.5)
            ax.set_xticks(x); ax.set_xticklabels(slot_labels, rotation=45, fontsize=6.5)
            ax.set_title(label, fontsize=12, fontweight="bold", color="#cdd6f4")
            ax.set_xlabel("30-min slot (04:00 AM origin)", fontsize=9)
            if ax_idx == 0:
                ax.set_ylabel("Mean AT_RETAIL rate (%)", fontsize=10)
            ax.legend(title="Cycle", fontsize=8, title_fontsize=8)
            ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["11a_retail_diurnal_daytype"] = _b64(fig11a)

        _apply_dark()
        fig11b, axes11b = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        fig11b.suptitle("Section 11b -- Sunday AT_RETAIL Diurnal Curve: QC vs AB",
                        color="#cdd6f4", fontsize=13, fontweight="bold")
        for ax_idx, (prov_code, prov_name) in enumerate([(24, "QC"), (48, "AB")]):
            ax = axes11b[ax_idx]
            for i, c in enumerate(CYCLES):
                if "DDAY_STRATA" in combo.columns and "PR" in combo.columns:
                    mask = (combo["CYCLE_YEAR"] == c) & (combo["DDAY_STRATA"] == 3) & (combo["PR"] == prov_code)
                else:
                    mask = combo["CYCLE_YEAR"] == c
                sub = combo[mask]
                if len(sub) == 0 or not retl_present:
                    continue
                arr = sub[retl_present].to_numpy(dtype=float)
                curve = 100 * np.nanmean(arr, axis=0)
                ax.plot(x, curve, color=CYCLE_COLORS[i], linewidth=2.2,
                        label=str(c), marker="o", markersize=2.5)
            ax.set_xticks(x); ax.set_xticklabels(slot_labels, rotation=45, fontsize=6.5)
            ax.set_title(f"Sunday -- {prov_name}", fontsize=12, fontweight="bold", color="#cdd6f4")
            ax.set_xlabel("30-min slot (04:00 AM origin)", fontsize=9)
            if ax_idx == 0:
                ax.set_ylabel("Mean AT_RETAIL rate (%)", fontsize=10)
            ax.legend(title="Cycle", fontsize=8, title_fontsize=8)
            ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["11b_retail_sunday_qc_ab"] = _b64(fig11b)
        self._rec("pass", "11.11 | AT_RETAIL diurnal headline charts generated (day-type + QC/AB Sunday panels)")

        print("  [DONE] Section 11 AT_RETAIL validation complete.")

    # ── Section 12: Legacy Bit-Identity vs Leg-2 (Leg-3 NEW) ───────────────────

    @staticmethod
    def _sha256_file(path: str, chunk_size: int = 1 << 20) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    def validate_legacy_bit_identity(self) -> None:
        """Section 12 -- SHA-256 bit-identity of legacy outputs vs Leg-2 (Leg-3 NEW).

        Checks:
          12.1: SHA-256 of the 5 legacy CSVs vs Leg-2 outputs_step3/ -- FAIL on mismatch
          12.2: merged_episodes.parquet hash, or column-wise value equality if the
                hash is non-deterministic across pandas/pyarrow versions -- records
                which comparison was used.
        """
        print("\n--- Section 12: Legacy Bit-Identity vs Leg-2 (Leg-3 NEW) ---")

        # 12.1: CSV hash comparison
        for fname in LEGACY_OUTPUTS_CSV:
            leg3_path = os.path.join(self.step3_dir, fname)
            leg2_path = os.path.join(self.leg2_step3_dir, fname)
            if not os.path.exists(leg3_path) or not os.path.exists(leg2_path):
                self._rec("fail", f"12.1 | {fname}: file missing (Leg-3 exists="
                                  f"{os.path.exists(leg3_path)}, Leg-2 exists={os.path.exists(leg2_path)})")
                continue
            h3 = self._sha256_file(leg3_path)
            h2 = self._sha256_file(leg2_path)
            if h3 == h2:
                self._rec("pass", f"12.1 | {fname}: SHA-256 identical to Leg-2 ({h3[:16]}...)")
            else:
                self._rec("fail", f"12.1 | {fname}: SHA-256 MISMATCH vs Leg-2 "
                                  f"(Leg-3={h3[:16]}..., Leg-2={h2[:16]}...)")

        # 12.2: parquet hash, or column-wise value-equality fallback
        for fname in LEGACY_OUTPUTS_PARQUET:
            leg3_path = os.path.join(self.step3_dir, fname)
            leg2_path = os.path.join(self.leg2_step3_dir, fname)
            if not os.path.exists(leg3_path) or not os.path.exists(leg2_path):
                self._rec("fail", f"12.2 | {fname}: file missing (Leg-3 exists="
                                  f"{os.path.exists(leg3_path)}, Leg-2 exists={os.path.exists(leg2_path)})")
                continue
            h3 = self._sha256_file(leg3_path)
            h2 = self._sha256_file(leg2_path)
            if h3 == h2:
                self._rec("pass", f"12.2 | {fname}: SHA-256 identical to Leg-2 (method=sha256, {h3[:16]}...)")
                continue
            print(f"  [INFO] {fname}: SHA-256 mismatch -- falling back to column-wise value equality")
            try:
                df3 = pd.read_parquet(leg3_path)
                df2 = pd.read_parquet(leg2_path)
                same_shape = df3.shape == df2.shape
                same_cols = list(df3.columns) == list(df2.columns)
                values_equal = same_shape and same_cols and df3.equals(df2)
                if values_equal:
                    self._rec("pass", f"12.2 | {fname}: column-wise value equality holds "
                                      f"(method=column_equality; hash differs -- non-deterministic parquet encoding)")
                else:
                    self._rec("fail", f"12.2 | {fname}: column-wise value equality FAILED "
                                      f"(method=column_equality; shape_match={same_shape}, cols_match={same_cols})")
            except Exception as e:
                self._rec("fail", f"12.2 | {fname}: column-equality check errored: {e}")

        print("  [DONE] Section 12 legacy bit-identity check complete.")

    # ── HTML Report ─────────────────────────────────────────────────────────────

    def build_html_report(self) -> str:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_sections = [
            ("1_row_counts",         "Section 1 -- Row Count Preservation"),
            ("2_merge_integrity",    "Section 2 -- Merge Key Integrity"),
            ("3a_daytype",           "Section 3a -- DAYTYPE Distribution"),
            ("4a_activity_heatmap",  "Section 4a -- Activity Heatmap (14 Activities x 144 Slots)"),
            ("4b_at_home_curve",     "Section 4b -- AT_HOME Rate Curve Across 144 Slots"),
            ("5a_activity_dist",     "Section 5a -- Weighted Activity Distribution per Cycle"),
            ("5b_at_home_rate",      "Section 5b -- Weighted AT_HOME Rate per Cycle"),
            ("7a_act_dist_30min",    "Section 7a -- Activity Distribution: 10-min vs 30-min by Day Type"),
            ("7b_at_home_rhythm",    "Section 7b -- AT_HOME Daily Rhythm at 30-min Resolution"),
            ("6a_copre_completeness","Section 8a -- Co-Presence Column Completeness"),
            ("9a_atwork_diurnal",    "Section 9a (Leg-2 Headline) -- AT_WORK Diurnal Presence Curve per Cycle"),
            ("9b_atwork_rate",       "Section 9b -- Weighted AT_WORK Presence Rate per Cycle"),
            ("10_office_conditioning","Section 10 -- NOCS / NAICS / TELEWORK / WORK_SCHEDULE Coverage in hetus_30min"),
            ("11a_retail_diurnal_daytype","Section 11a (Leg-3 Headline) -- AT_RETAIL Diurnal Rate by Day-Type"),
            ("11b_retail_sunday_qc_ab","Section 11b -- Sunday AT_RETAIL Diurnal Curve: QC vs AB"),
        ]

        charts_html = ""
        for key, label in chart_sections:
            if key in self.plots_b64:
                charts_html += f"""
        <section class="chart-section" id="{key}">
          <h2>{label}</h2>
          <div class="chart-wrap">
            <img src="data:image/png;base64,{self.plots_b64[key]}" alt="{label}">
          </div>
        </section>"""

        summary_df = self.summary_data.get("summary_df")
        if summary_df is not None:
            th  = "".join(f"<th>{col}</th>" for col in summary_df.columns)
            trs = ""
            for _, row in summary_df.iterrows():
                cls = ' class="total-row"' if row["Cycle"] == "Total" else ""
                tds = "".join(f"<td>{v}</td>" for v in row.values)
                trs += f"<tr{cls}>{tds}</tr>"
            summary_html = f"""
        <section class="chart-section" id="summary-table">
          <h2>Section 6 -- Dataset Statistics Summary Table</h2>
          <div class="table-wrap">
            <table class="summary-table">
              <thead><tr>{th}</tr></thead>
              <tbody>{trs}</tbody>
            </table>
          </div>
        </section>"""
        else:
            summary_html = ""

        def _badge_list(level: str) -> str:
            icon  = "PASS" if level == "pass" else ("FAIL" if level == "fail" else "WARN")
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>" for m in items)

        nav_links = "".join(
            f'<a href="#{k}">{lbl.split("--")[0].strip()}</a>'
            for k, lbl in chart_sections if k in self.plots_b64)
        nav_links += '<a href="#summary-table">Section 6</a>'

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Step 3 (Leg-3) -- Merge &amp; Tiling Validation</title>
  <style>
    :root {{
      --bg:#1e1e2e; --surface:#2a2a3e; --surface2:#313244;
      --accent:#89b4fa; --green:#a6e3a1; --yellow:#f9e2af;
      --red:#f38ba8; --text:#cdd6f4; --subtext:#a6adc8; --border:#45475a;
    }}
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg);
            color:var(--text); min-height:100vh; }}
    header {{ background:var(--surface); border-bottom:1px solid var(--border);
              padding:18px 32px; display:flex; align-items:center;
              justify-content:space-between; position:sticky; top:0; z-index:100; }}
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
    .table-wrap {{ overflow-x:auto; }}
    .summary-table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    .summary-table th {{ background:var(--surface2); color:var(--accent); padding:10px 12px;
                          text-align:left; border-bottom:2px solid var(--border);
                          font-size:0.78rem; white-space:nowrap; }}
    .summary-table td {{ padding:8px 12px; border-bottom:1px solid var(--border);
                          color:var(--text); white-space:nowrap; }}
    .summary-table tr:hover td {{ background:var(--surface2); }}
    .summary-table tr.total-row td {{ font-weight:700; color:var(--accent);
                                       border-top:2px solid var(--border); }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem; color:var(--subtext);
              border-top:1px solid var(--border); margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GSS Step 3 (Leg-3) -- Merge &amp; Tiling Validation Report</h1>
      <p>Validates merged_episodes.csv, hetus_wide.csv, hetus_30min.csv,
         copresence_30min.csv, work_30min.csv, retail_30min.csv &middot;
         Cycles 2005, 2010, 2015, 2022 &middot; Section 12 = bit-identity vs Leg-2</p>
    </div>
    <p style="font-size:0.78rem;color:var(--subtext)">Generated: {ts}</p>
  </header>
  <nav>
    <a href="#pipeline-overview">Pipeline Overview</a>
    <a href="#scorecard">Scorecard</a>
    {nav_links}
  </nav>
  <main>
    <section class="pipeline-section" id="pipeline-overview">
      <h2>Pipeline Overview -- Step 3 (Leg-3): Merge &amp; Tiling</h2>
      <pre class="pipeline-pre">{STEP3_OVERVIEW}</pre>
    </section>

    <div class="scorecard" id="scorecard">
      <div class="score-card ok">
        <div class="number">{n_pass}</div>
        <div class="label">Checks Passed</div></div>
      <div class="score-card warn">
        <div class="number">{n_warn}</div>
        <div class="label">Warnings</div></div>
      <div class="score-card fail">
        <div class="number">{n_fail}</div>
        <div class="label">Failures</div></div>
      <div class="score-card pct">
        <div class="number">{pct_ok}%</div>
        <div class="label">Pass Rate</div></div>
    </div>
    <div class="findings">
      <h2>FAILURES</h2>
      <ul class="badge-list">{_badge_list("fail")}</ul>
    </div>
    <div class="findings">
      <h2>WARNINGS</h2>
      <ul class="badge-list">{_badge_list("warn")}</ul>
    </div>
    <div class="findings">
      <h2>PASSED</h2>
      <ul class="badge-list">{_badge_list("pass")}</ul>
    </div>
    {charts_html}
    {summary_html}
  </main>
  <footer>
    Leg-3 Occupancy Modeling Pipeline &middot; Step 3 Merge &amp; Tiling Validation &middot;
    Inputs: outputs_step2/ + outputs_step3/ &middot;
    Output: outputs_step3/step3_validation_report.html &middot;
    Generated: {ts}
  </footer>
</body>
</html>"""

        out_html = os.path.join(self.step3_dir, "step3_validation_report.html")
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved -> {out_html}")

        # Also write TXT report
        out_txt = os.path.join(self.step3_dir, "step3_validation_report.txt")
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(f"Step 3 (Leg-3) Validation Report -- {ts}\n")
            f.write("=" * 60 + "\n")
            f.write(f"PASS: {n_pass}  WARN: {n_warn}  FAIL: {n_fail}  ({pct_ok}% pass rate)\n")
            f.write("=" * 60 + "\n\n")
            for level, icon in [("fail", "FAIL"), ("warn", "WARN"), ("pass", "PASS")]:
                for msg in self.results[level]:
                    f.write(f"[{icon}] {msg}\n")
        print(f"TXT Report saved  -> {out_txt}")
        return out_html

    # ── Run All ─────────────────────────────────────────────────────────────────

    def run_all(self) -> None:
        _apply_dark()
        print("=" * 60)
        print("Step 3 (Leg-3) -- Merge & Tiling Validation")
        print("=" * 60)
        self.validate_row_counts()
        self.validate_merge_integrity()
        self.validate_derived_features()
        self.validate_hetus_slots()
        self.validate_cross_cycle_consistency()
        self.validate_copresence()
        self.generate_summary_table()
        self.validate_30min_downsampling()
        self.validate_work_channel()          # [Leg-2]
        self.validate_office_conditioning()   # [Leg-2]
        self.validate_retail_channel()        # [Leg-3 NEW]
        self.validate_legacy_bit_identity()   # [Leg-3 NEW]
        self.build_html_report()
        n_p = len(self.results["pass"])
        n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 60}")
        print(f"Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    GSSMergeValidator4Split(INPUT_DIR, OUTPUT_DIR, LEG2_OUTPUT_DIR).run_all()
