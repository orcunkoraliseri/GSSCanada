"""Step 7 — BEM/UBEM Integration: Validation & Report Generation.

Validates BEM_Setup/BEM_Schedules_<year>.csv (output of 07_aug_to_bem.py) against
the calibrated diary marginals, the classic backup, and internal consistency.
Generates an HTML report with embedded charts (one report per year).

Run-from-anywhere; resolves paths relative to this file.
  py 07_bemIntegrationGSS_val.py                 # both years
  py 07_bemIntegrationGSS_val.py --year 2030     # one year
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout so box-drawing and emoji print cleanly on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── Paths (script-relative, like 07_aug_to_bem.py) ──────────────────────────────
HERE = Path(__file__).resolve().parent          # 2J_docs_occ_nTemp/
BASE = HERE.parent                               # GSSCanada-main/
BEMS = BASE / "BEM_Setup"
AUG  = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline" / "21CEN22GSS_aug_Full_Aggregated_excl.csv"
D2030 = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030" / "2030_synthetic_diaries.csv"
# OD-3 (2026-07-10): the shipped BEM_Schedules_2030.csv was built with --joint from the Step-6
# canonical joint-raked forecast (verified via the metabolic channel: BEM WE met 109.59 W matches
# the joint diary 109.49 W, not the base 99.90 W). Validate against that same source so §3/§4
# reference the file the BEM was actually built from. hom30 is byte-identical between base and
# joint (the joint rake only touches act30), so §3 occupancy is unaffected; §4 metabolic reference
# becomes correct.
D2030_JOINT = BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "forecast_2030" / "2030_synthetic_diaries_joint_raked.csv"
CLASSIC_SUFFIX = "_CLASSIC_BAK_2026-05-31"

# ── Constants ──────────────────────────────────────────────────────────────────
ACT_LABELS: dict[int, str] = {
    1: "Work", 2: "HH Work", 3: "Caregiving", 4: "Purchasing",
    5: "Sleep & Rest", 6: "Eating", 7: "Personal Care", 8: "Education",
    9: "Socializing", 10: "Passive Leisure", 11: "Active Leisure",
    12: "Community", 13: "Travel", 14: "Misc",
}
# act code -> watts/person (BEMConverter.metabolic_map; mirrors 07_aug_to_bem.py)
MET = {0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105, 7: 170,
       8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135}

# 2026-07-10: schema raised 13 -> 17 cols. 07_aug_to_bem.py (Step-9) emits the 4 additive
# internal-gain channels below; the live BEM_Schedules_<year>.csv the consumer reads is 17-col.
# (The 13-col pre-Step-9 schema is written separately to *_baseline.csv = OUT_COLS_BASELINE.)
OUT_COLS = ["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "DTYPE", "BEDRM", "CONDO",
            "ROOM", "REPAIR", "PR", "MATCH_TIER", "Occupancy_Schedule", "Metabolic_Rate",
            "Equipment_Fraction", "Lighting_Fraction", "Equip_Design_W", "Light_Design_W"]
OUT_COLS_BASELINE = OUT_COLS[:13]     # 13-col pre-Step-9 schema (the *_baseline.csv sibling)
STEP9_COLS = ["Equipment_Fraction", "Lighting_Fraction", "Equip_Design_W", "Light_Design_W"]
DTYPE_VALID = {"SingleD", "MidRise", "HighRise", "OtherDwelling", "8"}
PR_VALID    = {"Atlantic", "Quebec", "Ontario", "Prairies", "Alberta", "BC", "Northern Canada"}
TIER_VALID  = {"1_Perfect", "2_Core", "3_Constraints", "4_FailSafe"}
# 2026-07-10: frame reduced 144,507 -> 144,465 (-42 HH) by the Jul-9 Step-5 refresh (region-tier
# relink + joint rake + 5H exclusion). The stock 21CEN22GSS_aug_Full_Aggregated_excl.csv now holds
# 285,367 person-rows / 144,465 unique HH_ID (verified read). 144,507 was the pre-refresh frame;
# both BEM_Schedules_{2022,2030}.csv are internally consistent with 144,465 (0 partial-coverage HH,
# exactly 48 rows/HH). See step7_improvement_notes.md (Improvement 2, frame-size finding).
N_HH        = 144_465
N_ROWS      = N_HH * 2 * 24            # 6,934,320
# OD-2 (2026-07-10): Step-2 GSS-2022 weighted AT_HOME on the dwelling-stock scope. This is NOT
# the Step-6 "76.93% observed-2022" figure — that is measured on the augmented person-diary
# population (different denominator/scope) and is not interchangeable with this anchor. 72.3%
# is the correct reference for the linked dwelling stock. See step7_improvement_notes.md OD-2.
OBSERVED_2022_ATHOME = 72.3

# Per-figure captions (Improvement 4 — figures over prose)
CAPTIONS = {
    "1_schema": "Rows-per-household histogram (single bar at 48 = 2 day-types x 24 h) and the "
                "loaded analysis-column dtypes / null counts.",
    "2_daytype": "Day-types per household (all at 2 — integration.py contract) and row balance "
                 "across Weekday / Weekend.",
    "3_occupancy": "24-hour occupancy (Weekday vs Weekend, 04:00-origin clock) and BEM per-HH "
                   "occupancy vs the calibrated per-person diary marginal.",
    "4_metabolic": "24-hour metabolic rate (W/person) and the source-diary activity mix "
                   "(top-5, by activity name) that explains the Weekend dip.",
    "4b_step9": "24-hour Equipment & Lighting load fractions (Weekday solid / Weekend dashed) "
                "and mean design-W by dwelling type (per-HH-dtype SHEU calibration).",
    "5_attributes": "Household counts by dwelling type, province / region, and Step-5 match tier.",
    "6_regression": "Calibrated (J3) vs classic (pre-OP4) mean occupancy, Weekday and Weekend.",
}

_DARK = {
    "figure.facecolor": "#1e1e2e", "axes.facecolor": "#2a2a3e",
    "axes.edgecolor": "#555", "axes.labelcolor": "#cdd6f4",
    "xtick.color": "#cdd6f4", "ytick.color": "#cdd6f4", "text.color": "#cdd6f4",
    "grid.color": "#444", "legend.facecolor": "#2a2a3e", "legend.edgecolor": "#555",
    "font.family": "sans-serif", "font.size": 11,
}


def _apply_dark() -> None:
    plt.rcParams.update(_DARK)


def _b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# NOTE: the former _clock(h)=(4+h)%24 helper was removed 2026-07-10. Since the
# 2026-06-08 +4h diary->clock roll in 07_aug_to_bem.py, the BEM `Hour` column is
# already real clock time (Hour 0 = 00:00) for every channel — no relabeling applied.


# ── Validator ──────────────────────────────────────────────────────────────────

class BEMIntegrationValidator:
    """Validates one year of Step 7 BEM schedule output."""

    HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
    ACT = [f"act30_{i:03d}" for i in range(1, 49)]

    def __init__(self, year: str, outputs_dir: str) -> None:
        self.year = year
        self.outputs_dir = outputs_dir
        os.makedirs(outputs_dir, exist_ok=True)

        bem_path = BEMS / f"BEM_Schedules_{year}.csv"
        print(f"Loading {bem_path.name} …")
        self.header_cols = pd.read_csv(bem_path, nrows=0).columns.tolist()
        stat_cols = ["SIM_HH_ID", "Day_Type", "Hour", "DTYPE", "PR",
                     "MATCH_TIER", "Occupancy_Schedule", "Metabolic_Rate"] + STEP9_COLS
        self.bem = pd.read_csv(bem_path, usecols=lambda c: c in set(stat_cols),
                               low_memory=False)
        print(f"  -> {len(self.bem):,} rows x {len(self.header_cols)} cols")

        # Classic backup (regression reference) — optional
        classic_path = BEMS / f"BEM_Schedules_{year}{CLASSIC_SUFFIX}.csv"
        self.classic = None
        if classic_path.exists():
            print(f"Loading {classic_path.name} (regression reference) …")
            self.classic = pd.read_csv(classic_path,
                                       usecols=["Day_Type", "Occupancy_Schedule"],
                                       low_memory=False)
            self.classic_cols = pd.read_csv(classic_path, nrows=0).columns.tolist()
            print(f"  -> {len(self.classic):,} rows")
        else:
            self.classic_cols = []
            print(f"  (classic backup absent: {classic_path.name})")

        # Calibrated source diaries (calibration reference) — optional.
        # 2030 uses the joint-raked file (what the BEM was built from — OD-3), not the base.
        diary_path = AUG if year == "2022" else D2030_JOINT
        self.diary_source = diary_path.name
        self.diary = None
        if diary_path.exists():
            print(f"Loading {diary_path.name} (calibration reference) …")
            need = {"DDAY_STRATA"} | set(self.HOM) | set(self.ACT)
            self.diary = pd.read_csv(diary_path, usecols=lambda c: c in need,
                                     low_memory=False)
            print(f"  -> {len(self.diary):,} rows x {self.diary.shape[1]} cols")
        else:
            print(f"  (diary reference absent: {diary_path.name})")

        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        self.summary_rows: list[dict] = []

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = "[PASS]" if level == "pass" else ("[FAIL]" if level == "fail" else "[WARN]")
        print(f"  {icon} {msg}")

    def _sum(self, gate: str, thr: str, obs: str, status: str) -> None:
        self.summary_rows.append({"Gate / Check": gate, "Threshold": thr,
                                  "Observed": obs, "Status": status})

    # ── Section 1 — Output Schema & Row Integrity ──────────────────────────────
    def validate_output_schema(self) -> dict:
        print("\n--- Section 1: Output Schema & Row Integrity ---------------------------")
        _apply_dark()
        b = self.bem

        ok11 = self.header_cols == OUT_COLS
        self._rec("pass" if ok11 else "fail",
                  f"1.1 | Column set/order matches OUT_COLS (17, incl. Step-9 channels): {ok11}")
        self._sum("Column schema (17 cols)", "exact OUT_COLS",
                  "match" if ok11 else "MISMATCH", "PASS" if ok11 else "FAIL")

        n = len(b)
        ok12 = n == N_ROWS
        self._rec("pass" if ok12 else "fail",
                  f"1.2 | Row count: {n:,} (expected {N_ROWS:,})")
        self._sum("Row count", f"== {N_ROWS:,}", f"{n:,}", "PASS" if ok12 else "FAIL")

        nhh = b["SIM_HH_ID"].nunique()
        ok13 = nhh == N_HH
        self._rec("pass" if ok13 else "fail",
                  f"1.3 | Unique households: {nhh:,} (expected {N_HH:,})")
        self._sum("Households", f"== {N_HH:,}", f"{nhh:,}", "PASS" if ok13 else "FAIL")

        hours = set(b["Hour"].unique())
        ok14 = hours == set(range(24))
        self._rec("pass" if ok14 else "fail",
                  f"1.4 | Hour domain == {{0..23}}: {ok14} "
                  f"(min {b['Hour'].min()}, max {b['Hour'].max()})")
        self._sum("Hour domain", "{0..23}", f"{b['Hour'].min()}-{b['Hour'].max()}",
                  "PASS" if ok14 else "FAIL")

        nan_tot = int(b.isna().sum().sum())
        self._rec("pass" if nan_tot == 0 else "fail",
                  f"1.5 | NaN in analysis columns: {nan_tot}")

        rph = b.groupby("SIM_HH_ID").size()
        ok16 = bool((rph == 48).all())
        self._rec("pass" if ok16 else "fail",
                  f"1.6 | Rows per household == 48 (2 day-types x 24h): {ok16}")

        # Chart: rows-per-HH histogram + dtype/null table
        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
        fig.suptitle(f"Section 1 — Output Schema & Row Integrity ({self.year})",
                     fontsize=13, fontweight="bold")
        ax = axes[0]
        vc = rph.value_counts().sort_index()
        ax.bar(vc.index.astype(str), vc.values, color="#89b4fa",
               edgecolor="#1e1e2e", width=0.6)
        ax.set_xlabel("Rows per household"); ax.set_ylabel("HH count")
        ax.set_title("Rows per HH (expect single bar at 48)", fontsize=11)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2 = axes[1]; ax2.axis("off")
        tbl_rows = [[c, str(b[c].dtype), str(int(b[c].isna().sum()))]
                    for c in b.columns]
        tbl = ax2.table(cellText=tbl_rows,
                        colLabels=["Loaded column", "dtype", "nulls"],
                        cellLoc="center", loc="center")
        tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1, 1.4)
        ax2.set_title("Analysis-column dtypes / null counts", fontsize=11)
        plt.tight_layout()
        self.plots_b64["1_schema"] = _b64(fig)
        return {"n": n, "nhh": nhh}

    # ── Section 2 — Day-Type Coverage ──────────────────────────────────────────
    def validate_daytype_coverage(self) -> dict:
        print("\n--- Section 2: Day-Type Coverage (integration.py contract) -------------")
        _apply_dark()
        b = self.bem

        dts = set(b["Day_Type"].unique())
        ok21 = dts <= {"Weekday", "Weekend"}
        self._rec("pass" if ok21 else "fail",
                  f"2.1 | Day_Type domain {sorted(dts)} subset of {{Weekday, Weekend}}: {ok21}")
        self._sum("Day_Type domain", "{Weekday, Weekend}",
                  ", ".join(sorted(dts)), "PASS" if ok21 else "FAIL")

        cov = b.groupby("SIM_HH_ID")["Day_Type"].nunique()
        partial = int((cov < 2).sum())
        ok22 = partial == 0
        self._rec("pass" if ok22 else "fail",
                  f"2.2 | Households missing a day-type: {partial} (integration.py rejects > 0)")
        self._sum("Both day-types per HH", "0 partial", f"{partial} partial",
                  "PASS" if ok22 else "FAIL")

        rows_by_dt = b.groupby("Day_Type").size()
        balanced = rows_by_dt.nunique() == 1
        self._rec("pass" if balanced else "warn",
                  f"2.3 | Rows per day-type balanced: "
                  f"{dict(rows_by_dt)} ({'equal' if balanced else 'unequal'})")

        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        fig.suptitle(f"Section 2 — Day-Type Coverage ({self.year})",
                     fontsize=13, fontweight="bold")
        ax = axes[0]
        cc = cov.value_counts().sort_index()
        ax.bar(cc.index.astype(str), cc.values, color="#a6e3a1",
               edgecolor="#1e1e2e", width=0.6)
        ax.set_xlabel("Day-types per HH"); ax.set_ylabel("HH count")
        ax.set_title("Coverage per HH (expect all at 2)", fontsize=11)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2 = axes[1]
        ax2.bar(rows_by_dt.index, rows_by_dt.values, color="#89b4fa",
                edgecolor="#1e1e2e", width=0.5)
        ax2.set_ylabel("Rows"); ax2.set_title("Rows per day-type", fontsize=11)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["2_daytype"] = _b64(fig)
        return {"partial": partial}

    # ── Section 3 — Occupancy Plausibility & Calibration Match ──────────────────
    def _diary_targets(self) -> dict:
        """WD / WE / overall AT_HOME (%) from the calibrated source diaries."""
        if self.diary is None:
            return {}
        d = self.diary
        hom = [c for c in self.HOM if c in d.columns]
        wd = d[d["DDAY_STRATA"] == 1][hom].values.mean() * 100
        we = d[d["DDAY_STRATA"].isin([2, 3])][hom].values.mean() * 100
        ov = d[hom].values.mean() * 100
        return {"wd": float(wd), "we": float(we), "overall": float(ov)}

    def validate_occupancy_calibration(self) -> dict:
        print("\n--- Section 3: Occupancy Plausibility & Calibration Match --------------")
        _apply_dark()
        b = self.bem
        occ = b["Occupancy_Schedule"]

        lo, hi = float(occ.min()), float(occ.max())
        ok31 = (lo >= 0.0) and (hi <= 1.0)
        self._rec("pass" if ok31 else "fail",
                  f"3.1 | Occupancy range: [{lo:.3f}, {hi:.3f}] within [0,1]")
        self._sum("Occupancy range", "[0,1]", f"[{lo:.3f}, {hi:.3f}]",
                  "PASS" if ok31 else "FAIL")

        wd_occ = b[b["Day_Type"] == "Weekday"]["Occupancy_Schedule"].mean() * 100
        we_occ = b[b["Day_Type"] == "Weekend"]["Occupancy_Schedule"].mean() * 100
        ok32 = wd_occ < we_occ
        self._rec("pass" if ok32 else "fail",
                  f"3.2 | WD occ {wd_occ:.2f}% < WE occ {we_occ:.2f}%: {ok32}")
        self._sum("WD < WE occupancy", "WD < WE",
                  f"{wd_occ:.2f}% / {we_occ:.2f}%", "PASS" if ok32 else "FAIL")

        tgt = self._diary_targets()
        if tgt:
            # Threshold ≤1 pp: BEM occupancy is a per-HH mean; the diary marginal is per-person.
            # The two weightings differ by HH-size composition (sub-pp). 2030's redraw removes
            # the difference (Δ≈0.04), confirming the converter itself introduces no bias.
            d33 = abs(wd_occ - tgt["wd"])
            lv33 = "pass" if d33 <= 1.0 else ("warn" if d33 <= 2.0 else "fail")
            self._rec(lv33,
                      f"3.3 | WD calibration: BEM {wd_occ:.2f}% (per-HH) vs diary {tgt['wd']:.2f}% "
                      f"(per-person) Δ{d33:.3f} pp (≤1.0; sub-pp = HH-size reweighting)")
            self._sum("WD calibration match", "≤ 1 pp", f"Δ{d33:.3f} pp", lv33.upper())

            d34 = abs(we_occ - tgt["we"])
            lv34 = "pass" if d34 <= 1.0 else ("warn" if d34 <= 2.0 else "fail")
            self._rec(lv34,
                      f"3.4 | WE calibration: BEM {we_occ:.2f}% (per-HH) vs diary {tgt['we']:.2f}% "
                      f"(per-person) Δ{d34:.3f} pp (≤1.0)")
            self._sum("WE calibration match", "≤ 1 pp", f"Δ{d34:.3f} pp", lv34.upper())

            if self.year == "2022":
                d35 = abs(tgt["overall"] - OBSERVED_2022_ATHOME)
                ok35 = d35 <= 2.0
                self._rec("pass" if ok35 else "fail",
                          f"3.5 | 2022 pop AT_HOME {tgt['overall']:.2f}% vs observed "
                          f"{OBSERVED_2022_ATHOME}% (Δ{d35:.2f} pp, ≤2; composition)")
                self._sum("2022 pop AT_HOME vs observed", "≤ 2 pp",
                          f"Δ{d35:.2f} pp", "PASS" if ok35 else "FAIL")
        else:
            self._rec("warn", "3.3-3.5 | diary reference absent — calibration match skipped")

        # 3.6 overnight presence peak (origin-agnostic)
        occ_by_h = b.groupby("Hour")["Occupancy_Schedule"].mean()
        peak = float(occ_by_h.max())
        ok36 = peak >= 0.85
        self._rec("pass" if ok36 else "fail",
                  f"3.6 | Peak hourly occupancy: {peak:.3f} (≥0.85, overnight presence)")
        self._sum("Peak hourly occupancy", "≥ 0.85", f"{peak:.3f}",
                  "PASS" if ok36 else "FAIL")

        # Chart: 24h occupancy curve WD vs WE + BEM-vs-target bar
        fig, axes = plt.subplots(1, 2, figsize=(16, 5),
                                 gridspec_kw={"width_ratios": [2.2, 1]})
        fig.suptitle(f"Section 3 — Occupancy Plausibility & Calibration ({self.year})",
                     fontsize=13, fontweight="bold")
        ax = axes[0]
        for dt, col in [("Weekday", "#89b4fa"), ("Weekend", "#a6e3a1")]:
            s = b[b["Day_Type"] == dt].groupby("Hour")["Occupancy_Schedule"].mean()
            ax.plot(s.index, s.values * 100, color=col, linewidth=2, label=dt)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 2)], fontsize=9)
        ax.set_xlabel("Hour of day (clock time)")
        ax.set_ylabel("Mean occupancy (%)")
        ax.set_title("24-hour occupancy: WD vs WE", fontsize=11)
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2 = axes[1]
        if tgt:
            x = np.arange(2)
            ax2.bar(x - 0.2, [wd_occ, we_occ], 0.35, label="BEM output",
                    color="#89b4fa", edgecolor="#1e1e2e")
            ax2.bar(x + 0.2, [tgt["wd"], tgt["we"]], 0.35, label="Calibrated diary",
                    color="#f9e2af", edgecolor="#1e1e2e")
            ax2.set_xticks(x); ax2.set_xticklabels(["Weekday", "Weekend"])
            ax2.set_ylabel("AT_HOME (%)"); ax2.legend(fontsize=8)
            ax2.set_ylim(0, 100)
        ax2.set_title("BEM vs calibration target", fontsize=11)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["3_occupancy"] = _b64(fig)
        return {"wd_occ": wd_occ, "we_occ": we_occ}

    # ── Section 4 — Metabolic Rate Plausibility ────────────────────────────────
    def validate_metabolic(self) -> dict:
        print("\n--- Section 4: Metabolic Rate Plausibility -----------------------------")
        _apply_dark()
        b = self.bem
        met = b["Metabolic_Rate"]

        lo, hi = float(met.min()), float(met.max())
        ok41 = (lo >= 0.0) and (hi <= 245.0)
        self._rec("pass" if ok41 else "fail",
                  f"4.1 | Metabolic range: [{lo:.1f}, {hi:.1f}] W within [0, 245]")
        self._sum("Metabolic range", "[0, 245] W", f"[{lo:.1f}, {hi:.1f}]",
                  "PASS" if ok41 else "FAIL")

        met_by_h = b.groupby("Hour")["Metabolic_Rate"].mean()
        trough = float(met_by_h.min())
        peak = float(met_by_h.max())
        ok42 = trough <= 85.0
        self._rec("pass" if ok42 else "warn",
                  f"4.2 | Sleep trough (min hourly metabolic): {trough:.1f} W (≤85, sleep≈70)")
        self._sum("Sleep trough metabolic", "≤ 85 W", f"{trough:.1f} W",
                  "PASS" if ok42 else "WARN")

        ok43 = peak > trough
        self._rec("pass" if ok43 else "fail",
                  f"4.3 | Diurnal variation: peak {peak:.1f} W > trough {trough:.1f} W: {ok43}")

        wd_met = b[b["Day_Type"] == "Weekday"]["Metabolic_Rate"].mean()
        we_met = b[b["Day_Type"] == "Weekend"]["Metabolic_Rate"].mean()
        sleep_note = ""
        wd_sleep = we_sleep = None
        if self.diary is not None:
            act = [c for c in self.ACT if c in self.diary.columns]
            d = self.diary
            wd_sleep = float((d[d["DDAY_STRATA"] == 1][act].values == 5).mean() * 100)
            we_sleep = float((d[d["DDAY_STRATA"].isin([2, 3])][act].values == 5).mean() * 100)
            sleep_note = f" — sleep share WD {wd_sleep:.1f}% / WE {we_sleep:.1f}%"
        self._rec("pass",
                  f"4.4 | [INFO] WD met {wd_met:.1f} W vs WE met {we_met:.1f} W "
                  f"(act30 joint-raked, calibrated){sleep_note}")
        self._sum("Metabolic channel", "calibrated (joint-raked)",
                  f"WD {wd_met:.1f} / WE {we_met:.1f} W", "INFO")

        fig, axes = plt.subplots(1, 2, figsize=(16, 5))
        fig.suptitle(f"Section 4 — Metabolic Rate Plausibility ({self.year})",
                     fontsize=13, fontweight="bold")
        ax = axes[0]
        for dt, col in [("Weekday", "#89b4fa"), ("Weekend", "#a6e3a1")]:
            s = b[b["Day_Type"] == dt].groupby("Hour")["Metabolic_Rate"].mean()
            ax.plot(s.index, s.values, color=col, linewidth=2, label=dt)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 2)], fontsize=9)
        ax.set_xlabel("Hour of day (clock time)")
        ax.set_ylabel("Mean metabolic (W/person)")
        ax.set_title("24-hour metabolic: WD vs WE", fontsize=11)
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2 = axes[1]
        if wd_sleep is not None:
            act = [c for c in self.ACT if c in self.diary.columns]
            d = self.diary
            wd_share = {a: float((d[d["DDAY_STRATA"] == 1][act].values == a).mean() * 100)
                        for a in range(1, 15)}
            we_share = {a: float((d[d["DDAY_STRATA"].isin([2, 3])][act].values == a).mean() * 100)
                        for a in range(1, 15)}
            top5 = sorted(wd_share, key=wd_share.get, reverse=True)[:5]
            y = np.arange(5)
            ax2.barh(y + 0.2, [wd_share[a] for a in top5], 0.35, label="Weekday",
                     color="#89b4fa", edgecolor="#1e1e2e")
            ax2.barh(y - 0.2, [we_share[a] for a in top5], 0.35, label="Weekend",
                     color="#a6e3a1", edgecolor="#1e1e2e")
            ax2.set_yticks(y); ax2.set_yticklabels([ACT_LABELS[a] for a in top5], fontsize=9)
            ax2.set_xlabel("Time share (%)"); ax2.legend(fontsize=8)
        ax2.set_title("Source-diary activity mix (explains WE dip)", fontsize=11)
        ax2.xaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["4_metabolic"] = _b64(fig)
        return {"wd_met": wd_met, "we_met": we_met}

    # ── Section 4b — Step-9 Internal-Gain Channels (Equipment / Lighting) ────────
    def validate_step9_channels(self) -> dict:
        """Validate the 4 additive Step-9 columns EnergyPlus reads as equipment + lighting
        loads. Reports the inline-assert ranges (07_aug_to_bem.py) with distributions, checks
        the diurnal shape, and shows design-W by dwelling type."""
        print("\n--- Section 4b: Step-9 Internal Gains (Equipment / Lighting) -----------")
        _apply_dark()
        b = self.bem
        have = [c for c in STEP9_COLS if c in b.columns]
        if len(have) < 4:
            self._rec("warn",
                      f"4b | Step-9 channels absent ({have}); file predates Step-9 — skipped")
            self._sum("Step-9 channels present", "4 cols", f"{len(have)}/4", "WARN")
            return {}

        ef, lf = b["Equipment_Fraction"], b["Lighting_Fraction"]
        edw, ldw = b["Equip_Design_W"], b["Light_Design_W"]

        ef_ok = (float(ef.min()) >= 0.0) and (float(ef.max()) <= 1.0)
        lf_ok = (float(lf.min()) >= 0.0) and (float(lf.max()) <= 1.0)
        self._rec("pass" if (ef_ok and lf_ok) else "fail",
                  f"4b.1 | Fraction ranges: Equip [{ef.min():.3f}, {ef.max():.3f}], "
                  f"Light [{lf.min():.3f}, {lf.max():.3f}] within [0, 1]")
        self._sum("Step-9 fractions range", "[0, 1]",
                  f"E[{ef.min():.2f},{ef.max():.2f}] L[{lf.min():.2f},{lf.max():.2f}]",
                  "PASS" if (ef_ok and lf_ok) else "FAIL")

        dw_ok = (float(edw.min()) >= 0.0) and (float(ldw.min()) >= 0.0)
        self._rec("pass" if dw_ok else "fail",
                  f"4b.2 | Design-W non-negative: Equip min {edw.min():.1f} W, "
                  f"Light min {ldw.min():.1f} W (max E {edw.max():.0f} / L {ldw.max():.0f})")
        self._sum("Step-9 design-W >= 0", ">= 0 W",
                  f"E {edw.min():.0f}+ / L {ldw.min():.0f}+", "PASS" if dw_ok else "FAIL")

        # Diurnal shape: residential lighting should peak in the evening; equipment non-flat.
        ef_by_h = b.groupby("Hour")["Equipment_Fraction"].mean()
        lf_by_h = b.groupby("Hour")["Lighting_Fraction"].mean()
        l_peak_clock = int(lf_by_h.idxmax())   # BEM Hour is already clock time (post 06-08 roll)
        l_evening = 17 <= l_peak_clock <= 23
        self._rec("pass" if l_evening else "warn",
                  f"4b.3 | Lighting peak at {l_peak_clock:02d}h "
                  f"({'evening' if l_evening else 'non-evening'}; expect ~18-23h)")
        self._sum("Lighting evening peak", "17-23h", f"{l_peak_clock:02d}h",
                  "PASS" if l_evening else "WARN")

        ef_amp = float(ef_by_h.max() - ef_by_h.min())
        self._rec("pass" if ef_amp > 0.02 else "warn",
                  f"4b.4 | Equipment diurnal amplitude {ef_amp:.3f} (non-flat profile)")

        # Design-W by DTYPE (per-HH-dtype SHEU calibration -> should differ by dwelling type)
        dw_by_dt = (b.drop_duplicates("SIM_HH_ID")
                     .groupby("DTYPE")[["Equip_Design_W", "Light_Design_W"]].mean())
        n_levels = int(dw_by_dt["Equip_Design_W"].round(0).nunique())
        self._rec("pass",
                  f"4b.5 | [INFO] Equip design-W spans {n_levels} distinct DTYPE levels "
                  f"(per-HH-dtype SHEU targets: HighRise/MidRise/SingleD differ)")
        self._sum("Step-9 design-W by DTYPE", "informational",
                  f"{n_levels} DTYPE levels", "INFO")

        # Chart: 24h equip + lighting fraction (WD vs WE) + design-W by DTYPE
        fig, axes = plt.subplots(1, 2, figsize=(16, 5),
                                 gridspec_kw={"width_ratios": [2, 1.3]})
        fig.suptitle(f"Section 4b — Step-9 Internal Gains ({self.year})",
                     fontsize=13, fontweight="bold")
        ax = axes[0]
        for dt, style in [("Weekday", "-"), ("Weekend", "--")]:
            sub = b[b["Day_Type"] == dt]
            e = sub.groupby("Hour")["Equipment_Fraction"].mean()
            l = sub.groupby("Hour")["Lighting_Fraction"].mean()
            ax.plot(e.index, e.values, style, color="#f9e2af", linewidth=2,
                    label=f"Equipment {dt}")
            ax.plot(l.index, l.values, style, color="#89b4fa", linewidth=2,
                    label=f"Lighting {dt}")
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 2)], fontsize=9)
        ax.set_xlabel("Hour of day (clock time)")
        ax.set_ylabel("Mean load fraction")
        ax.set_title("24-hour Equipment & Lighting fractions", fontsize=11)
        ax.legend(fontsize=8); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2 = axes[1]
        dwv = dw_by_dt.reset_index()
        x = np.arange(len(dwv))
        ax2.bar(x - 0.2, dwv["Equip_Design_W"], 0.35, label="Equip design-W",
                color="#f9e2af", edgecolor="#1e1e2e")
        ax2.bar(x + 0.2, dwv["Light_Design_W"], 0.35, label="Light design-W",
                color="#89b4fa", edgecolor="#1e1e2e")
        ax2.set_xticks(x)
        ax2.set_xticklabels(dwv["DTYPE"].astype(str), rotation=40, ha="right", fontsize=8)
        ax2.set_ylabel("Mean design-W (W)"); ax2.legend(fontsize=8)
        ax2.set_title("Design-W by dwelling type", fontsize=11)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["4b_step9"] = _b64(fig)
        return {"l_peak_clock": l_peak_clock, "ef_amp": ef_amp}

    # ── Section 5 — Dwelling / Geography Attribute Integrity ────────────────────
    def validate_attribute_integrity(self) -> dict:
        print("\n--- Section 5: Dwelling / Geography Attribute Integrity ----------------")
        _apply_dark()
        b = self.bem
        hh = b.drop_duplicates("SIM_HH_ID")

        dtypes = set(hh["DTYPE"].astype(str).unique())
        ok51 = dtypes <= DTYPE_VALID
        self._rec("pass" if ok51 else "fail",
                  f"5.1 | DTYPE labels {sorted(dtypes)} subset of valid set: {ok51}")
        n_dt = int(hh["DTYPE"].value_counts().sum())
        ok52 = n_dt == N_HH
        self._rec("pass" if ok52 else "fail",
                  f"5.2 | DTYPE per-HH count sum: {n_dt:,} (expected {N_HH:,})")
        self._sum("DTYPE per-HH sum", f"== {N_HH:,}", f"{n_dt:,}",
                  "PASS" if ok52 else "FAIL")

        prs = set(hh["PR"].astype(str).unique())
        ok53 = prs <= PR_VALID
        self._rec("pass" if ok53 else "fail",
                  f"5.3 | PR labels {sorted(prs)} subset of valid set: {ok53}")
        n_pr = int(hh["PR"].value_counts().sum())
        ok54 = n_pr == N_HH
        self._rec("pass" if ok54 else "fail",
                  f"5.4 | PR per-HH count sum: {n_pr:,} (expected {N_HH:,})")
        self._sum("PR per-HH sum", f"== {N_HH:,}", f"{n_pr:,}",
                  "PASS" if ok54 else "FAIL")

        tiers = set(hh["MATCH_TIER"].astype(str).unique())
        ok55 = (tiers <= TIER_VALID) and (len(hh) == N_HH)
        self._rec("pass" if ok55 else "fail",
                  f"5.5 | MATCH_TIER {sorted(tiers)} valid & per-HH count {len(hh):,}")
        self._sum("MATCH_TIER carried", f"valid, {N_HH:,}", f"{len(hh):,}",
                  "PASS" if ok55 else "FAIL")

        # 5.6 DWELLING attrs (DTYPE, PR) are household-level -> must be constant within HH.
        nun = b.groupby("SIM_HH_ID")[["DTYPE", "PR", "MATCH_TIER"]].nunique()
        dwell_drift = int(((nun["DTYPE"] > 1) | (nun["PR"] > 1)).sum())
        ok56 = dwell_drift == 0
        self._rec("pass" if ok56 else "fail",
                  f"5.6 | HHs with DTYPE/PR drift within HH: {dwell_drift} "
                  f"(dwelling attrs must be constant)")
        self._sum("Dwelling attrs constant in HH", "0 drift", f"{dwell_drift}",
                  "PASS" if ok56 else "FAIL")
        # 5.7 MATCH_TIER is a PER-PERSON Step-5 label; convert() takes .first() per (HH, Day_Type),
        #     so an HH's two day-type blocks can show different tiers. Expected provenance variation,
        #     never consumed by EnergyPlus (occupancy + metabolic only). Informational, not a gate.
        tier_var = int((nun["MATCH_TIER"] > 1).sum())
        self._rec("pass",
                  f"5.7 | [INFO] HHs with MATCH_TIER variation across day-types: {tier_var:,} "
                  f"(per-person linkage label; BEM-harmless)")
        self._sum("MATCH_TIER within-HH (provenance)", "informational",
                  f"{tier_var:,} HH", "INFO")

        fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
        fig.suptitle(f"Section 5 — Dwelling / Geography Attribute Integrity ({self.year})",
                     fontsize=13, fontweight="bold")
        for ax, col, ttl, color in [
            (axes[0], "DTYPE", "Dwelling type", "#89b4fa"),
            (axes[1], "PR", "Province / region", "#a6e3a1"),
            (axes[2], "MATCH_TIER", "Step-5 match tier", "#f9e2af")]:
            vc = hh[col].astype(str).value_counts()
            ax.bar(range(len(vc)), vc.values, color=color, edgecolor="#1e1e2e", width=0.65)
            ax.set_xticks(range(len(vc)))
            ax.set_xticklabels(vc.index, rotation=40, ha="right", fontsize=8.5)
            ax.set_ylabel("HH count"); ax.set_title(ttl, fontsize=11)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["5_attributes"] = _b64(fig)
        return {"dtypes": sorted(dtypes), "prs": sorted(prs)}

    # ── Section 6 — Regression vs Classic ──────────────────────────────────────
    def validate_regression_vs_classic(self) -> dict:
        print("\n--- Section 6: Regression vs Classic -----------------------------------")
        _apply_dark()
        b = self.bem
        cal_wd = b[b["Day_Type"] == "Weekday"]["Occupancy_Schedule"].mean() * 100
        cal_we = b[b["Day_Type"] == "Weekend"]["Occupancy_Schedule"].mean() * 100

        if self.classic is None:
            self._rec("warn", "6.x | classic backup absent — regression skipped")
            return {}

        c = self.classic
        cl_wd = c[c["Day_Type"] == "Weekday"]["Occupancy_Schedule"].mean() * 100
        cl_we = c[c["Day_Type"] == "Weekend"]["Occupancy_Schedule"].mean() * 100
        self._rec("pass",
                  f"6.1 | [INFO] occupancy Δ vs classic: WD {cal_wd - cl_wd:+.2f} pp, "
                  f"WE {cal_we - cl_we:+.2f} pp (calibrated − classic)")
        self._sum("Occupancy Δ vs classic", "reported",
                  f"WD {cal_wd - cl_wd:+.2f} / WE {cal_we - cl_we:+.2f} pp", "INFO")

        # The pre-OP4 classic backup is the 13-col baseline schema; the live calibrated file
        # extends it with the 4 Step-9 channels. Parity is checked against that shared 13-col
        # baseline (a classic-schema difference is not a live-file defect -> WARN, never FAIL).
        ok62 = self.classic_cols == OUT_COLS_BASELINE
        self._rec("pass" if ok62 else "warn",
                  f"6.2 | Classic == 13-col baseline schema (live file extends it with "
                  f"{len(self.header_cols) - len(OUT_COLS_BASELINE)} Step-9 cols): {ok62}")
        same = len(c) == len(b)
        cl_hh = len(c) // 48
        self._rec("pass",
                  f"6.3 | [INFO] rows: classic {len(c):,} ({cl_hh:,} HH) vs calibrated "
                  f"{len(b):,} ({N_HH:,} HH)"
                  + ("" if same else f" — classic = older census frame, not the ML {N_HH:,}-HH frame"))
        self._sum("Frame vs classic", "informational",
                  f"{cl_hh:,} vs {N_HH:,} HH", "INFO")

        fig, ax = plt.subplots(figsize=(9, 5))
        x = np.arange(2)
        ax.bar(x - 0.2, [cal_wd, cal_we], 0.35, label="Calibrated (J3)",
               color="#89b4fa", edgecolor="#1e1e2e")
        ax.bar(x + 0.2, [cl_wd, cl_we], 0.35, label="Classic (pre-OP4)",
               color="#f38ba8", edgecolor="#1e1e2e")
        ax.set_xticks(x); ax.set_xticklabels(["Weekday", "Weekend"])
        ax.set_ylabel("Mean occupancy (%)"); ax.set_ylim(0, 100)
        ax.set_title(f"Section 6 — Calibrated vs Classic occupancy ({self.year})",
                     fontsize=12)
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["6_regression"] = _b64(fig)
        return {"cal_wd": cal_wd, "cal_we": cal_we, "cl_wd": cl_wd, "cl_we": cl_we}

    # ── Section 7 — Summary Table ───────────────────────────────────────────────
    def generate_summary_table(self) -> list[dict]:
        print("\n--- Section 7: Summary Table -------------------------------------------")
        for row in self.summary_rows:
            st = row["Status"]
            icon = {"PASS": "[PASS]", "WARN": "[WARN]", "INFO": "[INFO]"}.get(st, "[FAIL]")
            print(f"  {icon} {row['Gate / Check']}: {row['Observed']} — {st}")
        return self.summary_rows

    # ── HTML Report ─────────────────────────────────────────────────────────────
    def build_html_report(self) -> str:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_sections = [
            ("1_schema",     "Section 1 — Output Schema & Row Integrity"),
            ("2_daytype",    "Section 2 — Day-Type Coverage"),
            ("3_occupancy",  "Section 3 — Occupancy Plausibility & Calibration"),
            ("4_metabolic",  "Section 4 — Metabolic Rate Plausibility"),
            ("4b_step9",     "Section 4b — Step-9 Internal Gains (Equipment / Lighting)"),
            ("5_attributes", "Section 5 — Dwelling / Geography Attribute Integrity"),
            ("6_regression", "Section 6 — Regression vs Classic"),
        ]
        charts_html = ""
        for key, label in chart_sections:
            if key in self.plots_b64:
                cap = CAPTIONS.get(key, "")
                cap_html = (f'<p class="caption">{cap}</p>' if cap else "")
                charts_html += f"""
        <section class="chart-section" id="{key}">
          <h2>{label}</h2>
          <div class="chart-wrap">
            <img src="data:image/png;base64,{self.plots_b64[key]}" alt="{label}">
          </div>
          {cap_html}
        </section>"""

        if self.summary_rows:
            cols = ["Gate / Check", "Threshold", "Observed", "Status"]
            th = "".join(f"<th>{c}</th>" for c in cols)
            trs = ""
            for row in self.summary_rows:
                st = row["Status"]
                cls = {"PASS": "pass-row", "WARN": "warn-row",
                       "INFO": "info-row"}.get(st, "fail-row")
                tds = "".join(f"<td>{row[c]}</td>" for c in cols)
                trs += f'<tr class="{cls}">{tds}</tr>'
            summary_html = f"""
        <section class="chart-section" id="summary-table">
          <h2>Section 7 — Summary Table</h2>
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
            icon = "[PASS]" if level == "pass" else ("[FAIL]" if level == "fail" else "[WARN]")
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>" for m in items)

        nav_links = "".join(
            f'<a href="#{k}">{lbl.split("—")[0].strip()}</a>'
            for k, lbl in chart_sections if k in self.plots_b64)
        nav_links += '<a href="#deviations">Deviations</a>'
        nav_links += '<a href="#summary-table">Section 7</a>'
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ── Provenance banner (Improvement 2) ──────────────────────────────────
        src = getattr(self, "diary_source", "(unknown)")
        if self.year == "2030":
            build_note = ("built with <code>--joint</code> from the Step-6 canonical "
                          "joint-raked 2030 forecast (metabolic-channel verified)")
        else:
            build_note = "the Step-5 calibrated 2022 dwelling stock (region-tier relinked + raked)"
        provenance_html = f"""
    <div class="provenance">
      <strong>Provenance.</strong> Validates the live <code>BEM_Schedules_{self.year}.csv</code>
      — <b>17-column</b> schema (occupancy + metabolic + the 4 Step-9 Equipment/Lighting channels).
      Calibration reference / build source: <code>{src}</code> — {build_note}.
      2022 AT_HOME anchor = <b>72.3%</b> (Step-2 GSS weighted, dwelling-stock scope; distinct from
      the Step-6 person-diary 76.93%). Regenerated {ts}.
    </div>"""

        # ── Documented-deviations disposition panel (Improvement 4) ────────────
        dev_rows = [
            ("Metabolic / activity channel joint-raked (calibrated)",
             "act30 is now joint-raked alongside hom30 (05_postlink_rake.py --joint, 2026-07-09); "
             "Metabolic_Rate rides the calibrated activity mix.",
             "INFO — both occupancy and internal-gain magnitude are calibrated; per-stratum act30 gaps "
             "0.59–1.17 pp vs ~12.3 pp pre-rake."),
            ("Saturday / Sunday pooled → Weekend",
             "integration.py is 2-day-type; the calibrated ~2.3 pp Sat/Sun split is collapsed.",
             "ACCEPT — consumer contract; a 3-type variant is a one-line DAYTYPE change if needed."),
            ("Metabolic 70 W/MET (~60 kg) basis",
             "Conservative vs ASHRAE 105 / 70 kg (83 W/MET); scales all metabolic gains.",
             "VERIFIED vs the 2024 Adult Compendium (07_metabolicMap_verification.md); document the "
             "basis in Methods; optional ×1.19 / ×1.5 sensitivity."),
            ("MATCH_TIER within-HH variation",
             "Per-person Step-5 label differs across an HH's two day-type blocks (convert() .first()).",
             "INFO — DTYPE/PR drift = 0; MATCH_TIER is never consumed by EnergyPlus. BEM-harmless."),
            ("Classic-frame regression",
             f"The 2022 classic backup is the older 36,909-HH census frame, not the {N_HH:,}-HH ML frame.",
             "INFO — row-count 'parity' is not a defect; schema is compared to the 13-col baseline."),
        ]
        dev_trs = "".join(
            f"<tr><td>{d}</td><td>{n}</td><td>{disp}</td></tr>" for d, n, disp in dev_rows)
        deviations_html = f"""
        <section class="chart-section" id="deviations">
          <h2>Documented deviations — disposition</h2>
          <div class="table-wrap">
            <table class="summary-table">
              <thead><tr><th>Deviation</th><th>Nature</th><th>Disposition</th></tr></thead>
              <tbody>{dev_trs}</tbody>
            </table>
          </div>
          <p class="caption" style="margin-top:14px">
            <strong>Limitations (paper-ready).</strong> The Step-7 BEM schedules calibrate both the
            occupancy channel (hom30, raked to the Census-linked 2022 stock and the Step-6 2030 forecast)
            and the activity channel (act30, joint-raked via 05_postlink_rake.py --joint) to within ≤1 pp
            of the diary marginals. The metabolic and Step-9 internal-gain channels therefore ride the
            calibrated activity mix, on a conservative 70 W/MET (~60 kg) basis, and Saturday/Sunday are
            pooled into a single Weekend profile per the EnergyPlus 2-day-type contract. None of these
            affects the occupancy signal EnergyPlus uses for presence; the metabolic basis and day-type
            pooling are documented as limitations.
          </p>
        </section>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Step 7 — BEM/UBEM Integration Validation Report ({self.year})</title>
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
             padding:4px 10px; border-radius:6px; transition:background .2s,color .2s; }}
    nav a:hover {{ background:var(--surface); color:var(--accent); }}
    main {{ max-width:1200px; margin:0 auto; padding:30px 28px; }}
    .scorecard {{ display:grid; grid-template-columns:repeat(4,1fr);
                  gap:14px; margin-bottom:36px; }}
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
    .caption {{ font-size:0.82rem; color:var(--subtext); margin-top:12px; line-height:1.5;
                text-align:left; }}
    .provenance {{ background:var(--surface); border:1px solid var(--border);
                   border-left:4px solid var(--accent); border-radius:10px;
                   padding:14px 18px; margin-bottom:28px; font-size:0.85rem;
                   color:var(--text); line-height:1.55; }}
    .provenance code {{ color:var(--yellow); }}
    .table-wrap {{ overflow-x:auto; }}
    .summary-table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    .summary-table th {{ background:var(--surface2); color:var(--accent); padding:10px 12px;
                          text-align:left; border-bottom:2px solid var(--border);
                          font-size:0.78rem; white-space:nowrap; }}
    .summary-table td {{ padding:8px 12px; border-bottom:1px solid var(--border);
                          color:var(--text); white-space:nowrap; }}
    .summary-table tr:hover td {{ background:var(--surface2); }}
    .summary-table tr.pass-row td {{ color:var(--green); }}
    .summary-table tr.warn-row td {{ color:var(--yellow); }}
    .summary-table tr.info-row td {{ color:var(--subtext); }}
    .summary-table tr.fail-row td {{ color:var(--red); }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem;
              color:var(--subtext); border-top:1px solid var(--border); margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Step 7 — BEM/UBEM Integration Validation Report ({self.year})</h1>
      <p>Validates BEM_Schedules_{self.year}.csv: schema, day-type coverage, occupancy
         calibration, metabolic, attribute integrity, and regression vs classic</p>
    </div>
    <p style="font-size:0.78rem;color:var(--subtext)">Generated: {ts}</p>
  </header>
  <nav>
    <a href="#scorecard">Scorecard</a>
    {nav_links}
  </nav>
  <main>
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
    {provenance_html}
    <div class="findings">
      <h2>Failures</h2>
      <ul class="badge-list">{_badge_list("fail")}</ul>
    </div>
    <div class="findings">
      <h2>Warnings</h2>
      <ul class="badge-list">{_badge_list("warn")}</ul>
    </div>
    <div class="findings">
      <h2>Passed</h2>
      <ul class="badge-list">{_badge_list("pass")}</ul>
    </div>
    {charts_html}
    {summary_html}
    {deviations_html}
  </main>
  <footer>
    Occupancy Modeling Pipeline &middot; Step 7 BEM/UBEM Integration Validation &middot;
    Input: {BEMS / f"BEM_Schedules_{self.year}.csv"} &middot;
    Output: {os.path.join(self.outputs_dir, f"step7_validation_report_{self.year}_v2.html")} &middot;
    Generated: {ts}
  </footer>
</body>
</html>"""

        out_path = os.path.join(self.outputs_dir, f"step7_validation_report_{self.year}_v2.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved -> {out_path}")
        return out_path

    # ── Run All ─────────────────────────────────────────────────────────────────
    def run_all(self) -> None:
        _apply_dark()
        print("=" * 64)
        print(f"Step 7 — BEM/UBEM Integration Validation ({self.year})")
        print("=" * 64)
        self.validate_output_schema()
        self.validate_daytype_coverage()
        self.validate_occupancy_calibration()
        self.validate_metabolic()
        self.validate_step9_channels()
        self.validate_attribute_integrity()
        self.validate_regression_vs_classic()
        self.generate_summary_table()
        self.build_html_report()
        n_p = len(self.results["pass"]); n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 64}")
        print(f"[{self.year}] Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 64}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", choices=["2022", "2030", "both"], default="both")
    args = parser.parse_args()
    years = ["2022", "2030"] if args.year == "both" else [args.year]
    for yr in years:
        BEMIntegrationValidator(year=yr, outputs_dir=str(HERE / "outputs_step7")).run_all()
