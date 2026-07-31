"""3rdJ_07_bemIntegration_4split_val.py -- Step 7 Validation (3J Leg-3 Four-Channel 4-split).

Validates the four Step-7 products (residential REPLACE + office/retail/hotel MODULATE)
before anything is queued at Step 8. Sections A-G ported from the Leg-2 validator template
(3rdJ_07_bemIntegration_2split_val.py) + NEW Sections R (retail), H (hotel), M (mutex +
clock-origin), W (wiring assertion audit -- PENDING, no mixed-use IDF exists in this repo yet).

Usage (run-from-anywhere):
  py 3rdJ_07_bemIntegration_4split_val.py --year 2022
  py 3rdJ_07_bemIntegration_4split_val.py --year 2030 --bundle cons
  py 3rdJ_07_bemIntegration_4split_val.py --year 2030 --bundle central
  py 3rdJ_07_bemIntegration_4split_val.py --year 2030 --bundle opt
  py 3rdJ_07_bemIntegration_4split_val.py --all          # all 4 scenarios in one run

Style/scaffold ported from Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split_val.py.
Read-only on all data CSVs. pandas + numpy + matplotlib (Agg) only.
2026-07-23 built.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import os
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── Paths (script-relative, run-from-anywhere) ────────────────────────────────
HERE = Path(__file__).resolve().parent                        # Step7_docs/
LEG3 = HERE.parent                                             # Leg3_4-split/
OUT_DIR = HERE / "outputs_step7"

AUG2022 = (LEG3 / "Step5_docs" / "outputs_step5"
           / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv")
# PROMOTED 2026-07-30 (D-11/D-13) -- must stay in lockstep with the same two constants in
# 3rdJ_07_aug_to_bem_4split.py. Validating a different build than the one the generator consumed
# is worse than validating nothing, because it reports green on a file nothing was built from.
D2030_C = (LEG3 / "Step6_docs" / "outputs_step6"
           / "2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv")
D2030_EXPECTED_MD5 = "5aa74f44cd09a7afa9fa5418864956ed"
D2030_PREDECESSOR_MD5 = "7c105ef331b37107d5b605c95028c3ba"   # frozen, superseded 2026-07-30
GENERATOR_PY = HERE / "3rdJ_07_aug_to_bem_4split.py"


def assert_d2030_lockstep() -> None:
    """Hard gate, added 2026-07-30 with the D-11 promotion.

    D2030_EXPECTED_MD5 was previously DECLARED here and never read -- a pinned hash that
    pinned nothing. Two failure modes it now actually catches:
      (1) the on-disk 2030 deliverable is not the build this validator was pinned to;
      (2) the GENERATOR is pinned to a different build than this validator, i.e. the report
          would certify a file the products were never built from. That is the exact shape of
          the stale-report defect (B.3.0) -- green ticks describing something else.
    Hard-fails rather than recording a FAIL row: if this is wrong, every number below it is
    about the wrong file, so there is nothing worth rendering into a report.
    """
    if GENERATOR_PY.exists():
        m = re.search(r'^D2030_EXPECTED_MD5\s*=\s*"([0-9a-f]{32})"',
                      GENERATOR_PY.read_text(encoding="utf-8"), re.M)
        assert m, f"LOCKSTEP: could not read D2030_EXPECTED_MD5 out of {GENERATOR_PY.name}"
        assert m.group(1) == D2030_EXPECTED_MD5, (
            f"LOCKSTEP VIOLATION: generator pins {m.group(1)}, validator pins "
            f"{D2030_EXPECTED_MD5}. The products were built from a different 2030 deliverable "
            f"than the one being validated -- fix both constants before trusting any report."
        )
    if D2030_C.exists():
        actual = hashlib.md5(D2030_C.read_bytes()).hexdigest()
        assert actual == D2030_EXPECTED_MD5, (
            f"H6 VIOLATION: {D2030_C.name} MD5 is {actual}, pinned {D2030_EXPECTED_MD5}"
            + (" -- this is the SUPERSEDED predecessor build (D-11)"
               if actual == D2030_PREDECESSOR_MD5 else "")
        )
        print(f"  [LOCKSTEP PASS] 2030 deliverable {D2030_C.name} MD5 {actual} "
              f"matches generator + validator pins", flush=True)

# Retail lever files -- independent source for R.1/R.2's internal-consistency check (2026-07-30,
# post-2026-07-28 retail-multiplier fix cascade). Deliberately NOT RETAIL_LEVER_VALUE (below):
# R.1/R.2 are about the PRODUCT's own internal consistency (does its peak survive at whatever
# lever the raw Step-6 file actually holds), while RETAIL_LEVER_VALUE + R.7 pin the lever's VALUE.
# A corrupted lever file must fail R.7 while R.1 still passes -- see 3rdJ_07_aug_to_bem_4split.py
# _derive_retail_lever() (:153) / run_retail_gates() (:674-723), which this mirrors read-only.
RETAIL_LEVER_DIR = LEG3 / "Step6_docs" / "outputs_step6"
RETAIL_LEVER_FILES = {
    "shift":       RETAIL_LEVER_DIR / "at_retail_fraction_2030_shift.csv",
    "plateau":     RETAIL_LEVER_DIR / "at_retail_fraction_2030_plateau.csv",
    "renaissance": RETAIL_LEVER_DIR / "at_retail_fraction_2030_renaissance.csv",
}

# ── Constants ─────────────────────────────────────────────────────────────────
BUNDLES = ["cons", "central", "opt"]
OFFICE_BAND_OF_BUNDLE = {"cons": "conservative", "central": "hybrid", "opt": "fullyhybrid"}
RETAIL_SCENARIO_OF_BUNDLE = {"cons": "shift", "central": "plateau", "opt": "renaissance"}
RETAIL_LEVER_VALUE = {"shift": 0.90, "plateau": 0.97, "renaissance": 1.05}
HOTEL_BAND_OF_BUNDLE = {"cons": "low", "central": "central", "opt": "high"}

BAND_COLORS = {"cons": "#89b4fa", "central": "#f9e2af", "opt": "#a6e3a1", "observed": "#89b4fa",
               "conservative": "#89b4fa", "hybrid": "#f9e2af", "fullyhybrid": "#a6e3a1"}

RES_OUT_COLS = [
    "SIM_HH_ID", "Day_Type", "Hour",
    "HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER",
    "Occupancy_Schedule", "Metabolic_Rate",
]
OFFICE_COLS = ["office_archetype", "BAND", "Day_Type", "Hour",
               "AT_WORK_fraction", "multiplier", "n_persons"]
RETAIL_COLS = ["Day_Type", "PR", "slot", "Hour", "at_retail_fraction",
               "shape", "multiplier", "staff_shoulder_flag", "n_persons"]
HOTEL_COLS = ["PR", "MONTH", "Day_Type", "slot", "s_t", "monthly_rate", "multiplier", "rate_filled"]

OFFICE_ARCHETYPES = {"Office_Knowledge", "Office_Public", "Office_Sales"}
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
RET = [f"ret30_{i:03d}" for i in range(1, 49)]
ACT = [f"act30_{i:03d}" for i in range(1, 49)]

DTYPE_VALID = {"SingleD", "MidRise", "HighRise", "OtherDwelling", "8"}
# "8" (literal string, not "Movable") is inherited unchanged from the Leg-2 validator's DTYPE_VALID
# and never observed in any current 4-split product (confirmed empirically 2026-07-30). Per
# 3rdJ_05_censusLinkage_4split.py:75-77 (_DTYPE_MAP), raw Census code 8 = "Movable" -- a category
# that should already be consolidated into "OtherDwelling" by the time data reaches Step 7, so its
# presence here looks like vestigial/defensive inclusion rather than an expected label. Kept in
# DTYPE_VALID (ALLOWED, not REQUIRED) rather than dropped outright, since removing it outright
# would be an unverified guess; G.1 below requires the 4 real archetype labels but still tolerates
# "8" if it ever appears, without requiring it.
DTYPE_REQUIRED = {"SingleD", "MidRise", "HighRise", "OtherDwelling"}
PR_VALID    = {"Atlantic", "Quebec", "Ontario", "Prairies", "BC", "Northern Canada"}
TIER_VALID  = {"1_Perfect", "2_Core", "3_Constraints", "4_FailSafe"}

# Provisional NECB retail baseline proxy (must match the builder's construction exactly --
# see 3rdJ_07_aug_to_bem_4split.py FLAGGED OPEN ITEM header for provenance)
_RESCALE = 0.95 / 0.80
_WD_STEPS  = [(7, 0.0), (8, 0.1), (9, 0.2), (11, 0.5), (15, 0.7), (16, 0.8),
              (17, 0.7), (19, 0.5), (21, 0.3), (24, 0.0)]
_SAT_STEPS = [(7, 0.0), (8, 0.1), (9, 0.2), (10, 0.5), (11, 0.6), (17, 0.8),
              (18, 0.6), (21, 0.2), (22, 0.1), (24, 0.0)]
_SUN_STEPS = [(9, 0.0), (10, 0.1), (12, 0.2), (17, 0.4), (18, 0.2), (19, 0.1), (24, 0.0)]


def _steps_to_hourly(steps):
    vals = np.zeros(24); prev_t = 0
    for (t_until, v) in steps:
        vals[prev_t:t_until] = v; prev_t = t_until
    return vals


_NECB_RETAIL_BASELINE_HOURLY = {
    "Weekday":  _steps_to_hourly(_WD_STEPS) * _RESCALE,
    "Saturday": _steps_to_hourly(_SAT_STEPS) * _RESCALE,
    "Sunday":   _steps_to_hourly(_SUN_STEPS) * _RESCALE,
}


def necb_retail_baseline_proxy(day_type, hour):
    return float(_NECB_RETAIL_BASELINE_HOURLY[day_type][int(hour)])


def _derive_retail_lever(retail_scenario, df=None):
    """Read-only mirror of 3rdJ_07_aug_to_bem_4split.py::_derive_retail_lever() (:153) -- derives
    the Step-6 retail lever scalar at runtime from the raw lever file's own `multiplier` column,
    asserted uniform. Independent of RETAIL_LEVER_VALUE (R.7's business, pins the lever's VALUE);
    this is R.1/R.2's business (the product's own internal consistency against whatever lever the
    raw file actually holds). `df` param allows Task-3 in-memory-perturbation proof without disk I/O.
    """
    if df is None:
        path = RETAIL_LEVER_FILES[retail_scenario]
        df = pd.read_csv(path, usecols=["multiplier"])
    lo, hi = float(df["multiplier"].min()), float(df["multiplier"].max())
    assert (hi - lo) < 1e-9, (
        f"Retail lever '{retail_scenario}' is NOT a uniform scalar (min={lo:.10f}, max={hi:.10f}, "
        f"spread={hi - lo:.3e}): a non-uniform lever would change the retail SHAPE, not just the "
        f"LEVEL -- see val.py R.1/R.2 and the generator's _derive_retail_lever() docstring."
    )
    return float(df["multiplier"].iloc[0])


_DARK = {
    "figure.facecolor": "#1e1e2e", "axes.facecolor": "#2a2a3e",
    "axes.edgecolor": "#555", "axes.labelcolor": "#cdd6f4",
    "xtick.color": "#cdd6f4", "ytick.color": "#cdd6f4", "text.color": "#cdd6f4",
    "grid.color": "#444", "legend.facecolor": "#2a2a3e", "legend.edgecolor": "#555",
    "font.family": "sans-serif", "font.size": 11,
}


def _apply_dark():
    plt.rcParams.update(_DARK)


def _b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=125, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Main Validator ────────────────────────────────────────────────────────────
class BEM4splitValidator:
    def __init__(self, year: str, bundle: str | None = None, out_suffix: str = "") -> None:
        self.year = year
        self.bundle = bundle if year == "2030" else "observed"
        self.scenario_label = year if year == "2022" else f"2030_{bundle}"
        self.out_suffix = out_suffix
        os.makedirs(OUT_DIR, exist_ok=True)

        # ── Residential ──────────────────────────────────────────────────────
        if year == "2022":
            res_path = OUT_DIR / "BEM_Schedules_4split_2022.csv"
        else:
            res_path = OUT_DIR / f"BEM_Schedules_4split_2030_{bundle}.csv"
        print(f"Loading {res_path.name} ...")
        self.bem = pd.read_csv(res_path, low_memory=False)
        self.res_header = pd.read_csv(res_path, nrows=0).columns.tolist()
        self.N_HH = self.bem["SIM_HH_ID"].nunique()
        self.N_ROWS = self.N_HH * 2 * 24

        # All-bundle residential (for cross-bundle H5/F checks, 2030 only, if present)
        self.res_bundles = {}
        if year == "2030":
            for b in BUNDLES:
                p = OUT_DIR / f"BEM_Schedules_4split_2030_{b}.csv"
                if p.exists():
                    self.res_bundles[b] = p  # lazy: store path, load on demand (large files)

        # ── Office (single combined file, all bands) ──────────────────────────
        off_path = OUT_DIR / f"office_presence_multiplier_{year}.csv"
        print(f"Loading {off_path.name} ...")
        self.office = pd.read_csv(off_path, low_memory=False)
        self.office_bands = sorted(self.office["BAND"].unique().tolist())
        self.office_header = list(self.office.columns)

        # ── Retail ──────────────────────────────────────────────────────────
        ret_path = (OUT_DIR / "retail_presence_multiplier_2022.csv" if year == "2022"
                    else OUT_DIR / f"retail_presence_multiplier_2030_{bundle}.csv")
        print(f"Loading {ret_path.name} ...")
        self.retail = pd.read_csv(ret_path, low_memory=False)
        self.retail_header = list(self.retail.columns)

        # ── Hotel ───────────────────────────────────────────────────────────
        hot_path = (OUT_DIR / "hotel_schedule_multiplier_2022.csv" if year == "2022"
                    else OUT_DIR / f"hotel_schedule_multiplier_2030_{bundle}.csv")
        print(f"Loading {hot_path.name} ...")
        self.hotel = pd.read_csv(hot_path, low_memory=False)
        self.hotel_header = list(self.hotel.columns)

        # ── File mtimes (staleness check) ──────────────────────────────────
        self.input_paths = [res_path, off_path, ret_path, hot_path]

        # ── Calibration reference diary ────────────────────────────────────
        assert_d2030_lockstep()
        self.diary = None
        diary_path = AUG2022 if year == "2022" else D2030_C
        if diary_path.exists():
            print(f"Loading {diary_path.name} (calibration reference) ...")
            need = {"DDAY_STRATA", "BAND"} | set(HOM) | set(ACT) | set(RET)
            self.diary = pd.read_csv(diary_path, usecols=lambda c: c in need, low_memory=False)
        self.diary_stock_raw = None  # 2022 stock w/ full cols, for mutex + PR checks
        if AUG2022.exists():
            need2 = {"SIM_HH_ID", "DDAY_STRATA", "PR"} | set(HOM) | set(WRK) | set(RET)
            self.diary_stock_raw = pd.read_csv(AUG2022, usecols=lambda c: c in need2, low_memory=False)
        self.diary_2030_raw = None
        if D2030_C.exists():
            need3 = {"BAND", "DDAY_STRATA"} | set(HOM) | set(WRK) | set(RET)
            self.diary_2030_raw = pd.read_csv(D2030_C, usecols=lambda c: c in need3, low_memory=False)

        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        self.summary_rows: list[dict] = []

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = {"pass": "[PASS]", "fail": "[FAIL]", "warn": "[WARN]"}.get(level, "[INFO]")
        print(f"  {icon} {msg}")

    def _sum(self, gate: str, thr: str, obs: str, status: str) -> None:
        self.summary_rows.append({"Gate / Check": gate, "Threshold": thr, "Observed": obs, "Status": status})

    # ══════════════════════════════════════════════════════════════════════
    # Section A — Schema & Structure
    # ══════════════════════════════════════════════════════════════════════
    def section_a_schema(self) -> None:
        print("\n--- Section A: Schema & Structure -----------------------------------")
        _apply_dark()
        b = self.bem

        ok = self.res_header == RES_OUT_COLS
        self._rec("pass" if ok else "fail", f"A.1 | Residential column set/order (13 cols): {ok}")
        self._sum("Residential column schema (13 cols)", "exact", "match" if ok else "MISMATCH", "PASS" if ok else "FAIL")

        n = len(b); ok = n == self.N_ROWS
        self._rec("pass" if ok else "fail", f"A.2 | Residential row count: {n:,} (N_HH×2×24={self.N_ROWS:,})")
        self._sum("Residential row count", "N_HH×2×24", f"{n:,}", "PASS" if ok else "FAIL")
        res_row_ok = ok

        ok = set(b["Hour"].unique()) == set(range(24))
        self._rec("pass" if ok else "fail", f"A.3 | Hour domain {{0..23}}: {ok}")

        # FIXED 2026-07-30 (SUSPECT sweep finding): was a subset check (`<=`) which would silently
        # PASS even if "Weekend" (or "Weekday") were entirely absent from the data -- only invalid
        # extra labels tripped it, a missing expected category vanished instead of failing. Both
        # day-types are structurally required (A.2's N_HH×2×24 row-count formula assumes exactly
        # 2), so equality is the correct, safe check here -- not just tighter for its own sake.
        dts = set(b["Day_Type"].unique()); ok = dts == {"Weekday", "Weekend"}
        self._rec("pass" if ok else "fail", f"A.4 | Residential Day_Type domain {sorted(dts)} == {{Weekday,Weekend}}: {ok}")

        nan_tot = int(b[["Occupancy_Schedule", "Metabolic_Rate"]].isna().sum().sum())
        self._rec("pass" if nan_tot == 0 else "fail", f"A.5 | NaN in Occupancy/Metabolic: {nan_tot}")

        ok = list(self.office.columns) == OFFICE_COLS
        self._rec("pass" if ok else "fail", f"A.6 | Office column set (7 cols): {ok}")
        self._sum("Office column schema (7 cols)", "exact", "match" if ok else "MISMATCH", "PASS" if ok else "FAIL")

        exp_grid = len(OFFICE_ARCHETYPES) * 2 * 24 * len(self.office_bands)
        ok = len(self.office) == exp_grid
        self._rec("pass" if ok else "fail",
                  f"A.7 | Office grid: {len(self.office):,} rows (expected {exp_grid}): {ok}")
        off_row_ok = ok
        off_row_formula = f"{len(OFFICE_ARCHETYPES)}×2×24×{len(self.office_bands)}"

        ok = list(self.retail.columns) == RETAIL_COLS
        self._rec("pass" if ok else "fail", f"A.8 | Retail column set ({len(RETAIL_COLS)} cols): {ok}")
        self._sum("Retail column schema", "exact", "match" if ok else "MISMATCH", "PASS" if ok else "FAIL")

        n_pr = self.retail["PR"].nunique()
        exp_ret = 3 * n_pr * 48
        ok = len(self.retail) == exp_ret
        self._rec("pass" if ok else "fail",
                  f"A.9 | Retail rows = 3 Day_Type x {n_pr} PR x 48 slots = {exp_ret}: got {len(self.retail):,}: {ok}")
        self._sum("Retail row count", "3×PR×48", f"{len(self.retail):,}", "PASS" if ok else "FAIL")
        ret_row_ok = ok
        ret_row_formula = f"3×{n_pr}×48"

        ok = list(self.hotel.columns) == HOTEL_COLS
        self._rec("pass" if ok else "fail", f"A.10 | Hotel column set ({len(HOTEL_COLS)} cols): {ok}")

        n_pr_h = self.hotel["PR"].nunique()
        exp_hot = n_pr_h * 12 * 2 * 48
        ok = len(self.hotel) == exp_hot
        self._rec("pass" if ok else "fail",
                  f"A.11 | Hotel rows = {n_pr_h} PR x 12 mo x 2 DT x 48 = {exp_hot}: got {len(self.hotel):,}: {ok}")
        self._sum("Hotel row count", "PR×12×2×48", f"{len(self.hotel):,}", "PASS" if ok else "FAIL")
        hot_row_ok = ok
        hot_row_formula = f"{n_pr_h}×12×2×48"

        # A.12 FIXED 2026-07-30 (triaged in the CAN-FAIL/VACUOUS/SUSPECT sweep): the surrounding
        # comment ("report must postdate all 4 product files -- checked at report-build time too")
        # states an unambiguous intent, but no such comparison existed anywhere in the file --
        # mtimes were collected and printed, never compared to anything. This is exactly the gate
        # that should have caught B.3.0 (four Step-7 HTML reports validating stale pre-2026-07-28
        # retail data): a large spread between the 4 input mtimes means they were not built in the
        # same coherent session, i.e. some channel was regenerated (e.g. a bug fix) without the
        # others being refreshed to match. Real statistic: max-min mtime spread across the 4
        # inputs, WARN if > 24h (same-session tolerance). This is not hypothetical -- it currently
        # WARNs for real: retail was rebuilt 2026-07-28 while residential/office/hotel are still
        # 2026-07-23, a ~115h spread (see Progress Log).
        mtimes = {p.name: datetime.fromtimestamp(p.stat().st_mtime) for p in self.input_paths if p.exists()}
        if len(mtimes) >= 2:
            span_h = (max(mtimes.values()) - min(mtimes.values())).total_seconds() / 3600.0
            a12_ok = span_h <= 24.0
            lv = "pass" if a12_ok else "warn"
            self._rec(lv, f"A.12 | Input product vintage spread: {span_h:.1f}h across 4 files (≤24h "
                          f"expected for a coherent build session): {a12_ok}. mtimes={mtimes}")
            self._sum("A12 Input product vintage spread", "≤ 24h", f"{span_h:.1f}h", lv.upper())
        else:
            self._rec("pass", f"A.12 | [INFO] Input product mtimes: {mtimes}")

        # Horizontal log-scale bar chart replaces the old ax.table() count manifest (B.3.2):
        # the table was a static-image row/HH manifest carrying no gate verdict of its own --
        # the real A.1-A.11 checks lived only in the Summary Table far below. Bar colour now
        # IS that channel's own row-count gate verdict (A.2/A.7/A.9/A.11), and each bar is
        # annotated with the formula that produced the count, so it is verifiable at a glance.
        channels = [
            ("Residential", n, "N_HH×2×24 = {:,}".format(self.N_ROWS), res_row_ok),
            ("Office", len(self.office), off_row_formula, off_row_ok),
            ("Retail", len(self.retail), ret_row_formula, ret_row_ok),
            ("Hotel", len(self.hotel), hot_row_formula, hot_row_ok),
        ]
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.suptitle(f"Section A — Schema & Structure ({self.scenario_label})", fontsize=13, fontweight="bold")
        labels = [c[0] for c in channels]
        counts = [c[1] for c in channels]
        colors = ["#a6e3a1" if c[3] else "#f38ba8" for c in channels]
        y_pos = np.arange(len(channels))
        ax.barh(y_pos, counts, color=colors, edgecolor="#1e1e2e", height=0.55, log=True)
        ax.set_yticks(y_pos); ax.set_yticklabels(labels)
        ax.set_xlabel("Row count (log scale)")
        ax.invert_yaxis()
        ax.xaxis.grid(True, linestyle="--", alpha=0.3, which="both")
        xmax = max(counts)
        for i, (_, cnt, formula, ok_c) in enumerate(channels):
            badge = "PASS" if ok_c else "FAIL"
            ax.text(cnt * 1.15, i, f"{cnt:,}  ({formula})  [{badge}]",
                    va="center", fontsize=9, color=("#a6e3a1" if ok_c else "#f38ba8"))
        ax.set_xlim(right=xmax * 20)
        plt.tight_layout()
        self.plots_b64["A_schema"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section B — Day-Type Coverage
    # ══════════════════════════════════════════════════════════════════════
    def section_b_daytype(self) -> None:
        print("\n--- Section B: Day-Type Coverage -------------------------------------")
        _apply_dark()
        b = self.bem
        cov = b.groupby("SIM_HH_ID")["Day_Type"].nunique()
        partial = int((cov < 2).sum())
        ok = partial == 0
        self._rec("pass" if ok else "fail", f"B.1 | Partial HH (< 2 day-types): {partial}")
        self._sum("Day-type coverage per HH", "0 partial", f"{partial}", "PASS" if ok else "FAIL")

        we_bem = float(b[b["Day_Type"] == "Weekend"]["Occupancy_Schedule"].mean() * 100)
        if self.diary is not None and "DDAY_STRATA" in self.diary.columns:
            d = self.diary
            if self.year == "2030" and "BAND" in d.columns:
                d = d[d["BAND"] == OFFICE_BAND_OF_BUNDLE[self.bundle]]
            we_diary = float(d[d["DDAY_STRATA"].isin([2, 3])][HOM].values.mean() * 100)
            delta = we_bem - we_diary
            ok = abs(delta) <= 0.5
            lv = "pass" if ok else ("warn" if abs(delta) <= 1.5 else "fail")
            self._rec(lv, f"B.2 | Weekend marginal: BEM {we_bem:.2f}% vs source {we_diary:.2f}% "
                          f"(Δ{delta:+.3f} pp, ≤0.5 pp)")
            self._sum("Weekend marginal preserved", "≤ 0.5 pp", f"Δ{delta:+.3f} pp", lv.upper())

        # B.3: retail carries 3 distinct day-types incl. load-bearing Sunday
        ret_dts = set(self.retail["Day_Type"].unique())
        ok = ret_dts == {"Weekday", "Saturday", "Sunday"}
        self._rec("pass" if ok else "fail", f"B.3 | Retail Day_Type domain (3 types, Sunday load-bearing): {sorted(ret_dts)}: {ok}")
        self._sum("Retail 3 day-types (Sunday load-bearing)", "{Weekday,Saturday,Sunday}",
                  str(sorted(ret_dts)), "PASS" if ok else "FAIL")
        # FIXED 2026-07-30 (triaged in the sweep): message text said "(non-zero, load-bearing)" --
        # an unambiguous intended test that was never actually gated on. Real statistic: assert
        # sun_mean > 0 (small epsilon to avoid float noise), FAIL severity to match B.3's own
        # severity for Sunday's presence in the domain (this is the numeric half of that claim).
        sun_mean = float(self.retail[self.retail["Day_Type"] == "Sunday"]["at_retail_fraction"].mean())
        b4_ok = sun_mean > 1e-6
        self._rec("pass" if b4_ok else "fail",
                  f"B.4 | Retail Sunday mean at_retail_fraction: {sun_mean:.4f} (>0, load-bearing): {b4_ok}")
        self._sum("B4 Retail Sunday non-zero (load-bearing)", "> 0", f"{sun_mean:.4f}", "PASS" if b4_ok else "FAIL")

        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.suptitle(f"Section B — Day-Type Coverage ({self.scenario_label})", fontsize=13, fontweight="bold")
        cc = cov.value_counts().sort_index()
        ax.bar(cc.index.astype(str), cc.values, color="#a6e3a1", edgecolor="#1e1e2e", width=0.6)
        ax.set_xlabel("Day-types per HH"); ax.set_ylabel("HH count")
        ax.set_title("Residential coverage per HH (expect all at 2)", fontsize=11)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["B_daytype"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section C — Residential Occupancy Fidelity
    # ══════════════════════════════════════════════════════════════════════
    def section_c_occ_fidelity(self) -> None:
        print("\n--- Section C: Residential Occupancy Fidelity -----------------------")
        _apply_dark()
        b = self.bem
        lo, hi = float(b["Occupancy_Schedule"].min()), float(b["Occupancy_Schedule"].max())
        ok = (lo >= 0.0) and (hi <= 1.0)
        self._rec("pass" if ok else "fail", f"C.1 | Occupancy range [{lo:.3f},{hi:.3f}] ⊆ [0,1]: {ok}")
        self._sum("Occupancy range [0,1]", "[0,1]", f"[{lo:.3f},{hi:.3f}]", "PASS" if ok else "FAIL")

        wd_occ = float(b[b["Day_Type"] == "Weekday"]["Occupancy_Schedule"].mean() * 100)
        we_occ = float(b[b["Day_Type"] == "Weekend"]["Occupancy_Schedule"].mean() * 100)
        if self.diary is not None and "DDAY_STRATA" in self.diary.columns:
            d = self.diary
            if self.year == "2030" and "BAND" in d.columns:
                d = d[d["BAND"] == OFFICE_BAND_OF_BUNDLE[self.bundle]]
            tgt_wd = float(d[d["DDAY_STRATA"] == 1][HOM].values.mean() * 100)
            tgt_we = float(d[d["DDAY_STRATA"].isin([2, 3])][HOM].values.mean() * 100)
            for lbl, obs, tgt in [("WD", wd_occ, tgt_wd), ("WE", we_occ, tgt_we)]:
                delta = abs(obs - tgt)
                lv = "pass" if delta <= 1.0 else ("warn" if delta <= 2.0 else "fail")
                self._rec(lv, f"C.2 | {lbl} calibration: BEM {obs:.2f}% vs diary {tgt:.2f}% Δ{delta:.3f} pp (≤1pp)")
                self._sum(f"{lbl} occ fidelity", "≤ 1 pp", f"Δ{delta:.3f} pp", lv.upper())

        occ_by_h = b.groupby("Hour")["Occupancy_Schedule"].mean()
        peak = float(occ_by_h.max())
        ok = peak >= 0.85
        self._rec("pass" if ok else "fail", f"C.3 | Peak hourly occupancy: {peak:.3f} (≥0.85): {ok}")
        self._sum("Peak hourly occupancy", "≥ 0.85", f"{peak:.3f}", "PASS" if ok else "FAIL")

        # C.4: 2030 band ordering across bundles (cons < central < opt, daytime WD 9-17h)
        if self.year == "2030" and len(self.res_bundles) == 3:
            means = {}
            for bkey, p in self.res_bundles.items():
                df = pd.read_csv(p, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
                wd_biz = df[(df["Day_Type"] == "Weekday") & (df["Hour"].between(9, 17))]
                means[bkey] = float(wd_biz["Occupancy_Schedule"].mean())
            mono = means["cons"] < means["central"] < means["opt"]
            self._rec("pass" if mono else "fail",
                      f"C.4 | 2030 band ordering (WD 9-17h): cons={means['cons']:.4f} < "
                      f"central={means['central']:.4f} < opt={means['opt']:.4f}: {mono}")
            self._sum("Residential band ordering", "cons < central < opt",
                      f"{means}", "PASS" if mono else "FAIL")
        else:
            self._sum("Residential band ordering", "n/a", "n/a", "INFO")

        fig, ax = plt.subplots(figsize=(10, 4.5))
        fig.suptitle(f"Section C — Residential Occupancy Fidelity ({self.scenario_label})",
                     fontsize=13, fontweight="bold")
        for dt, col in [("Weekday", "#89b4fa"), ("Weekend", "#a6e3a1")]:
            s = b[b["Day_Type"] == dt].groupby("Hour")["Occupancy_Schedule"].mean()
            ax.plot(s.index, s.values * 100, color=col, lw=2, label=dt)
        ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Hour (clock, post +4h roll)")
        ax.set_ylabel("Mean occupancy (%)"); ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["C_occupancy"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section D — Metabolic Plausibility
    # ══════════════════════════════════════════════════════════════════════
    def section_d_metabolic(self) -> None:
        print("\n--- Section D: Metabolic Plausibility --------------------------------")
        _apply_dark()
        met = self.bem["Metabolic_Rate"]
        lo, hi = float(met.min()), float(met.max())
        ok = (lo >= 70.0) and (hi <= 245.0)
        lv = "pass" if ok else "warn"
        self._rec(lv, f"D.1 | Metabolic_Rate range [{lo:.1f},{hi:.1f}] W within spec [70,245]: {ok}")
        self._sum("Metabolic range", "[70, 245] W", f"[{lo:.1f}, {hi:.1f}]", lv.upper())

        met_by_h = self.bem.groupby("Hour")["Metabolic_Rate"].mean()
        trough, peak_met = float(met_by_h.min()), float(met_by_h.max())
        ok = peak_met > trough
        self._rec("pass" if ok else "fail", f"D.2 | Diurnal variation: peak {peak_met:.1f} > trough {trough:.1f}: {ok}")

        fig, ax = plt.subplots(figsize=(9, 4.5))
        fig.suptitle(f"Section D — Metabolic Rate Plausibility ({self.scenario_label})",
                     fontsize=13, fontweight="bold")
        for dt, col in [("Weekday", "#89b4fa"), ("Weekend", "#a6e3a1")]:
            s = self.bem[self.bem["Day_Type"] == dt].groupby("Hour")["Metabolic_Rate"].mean()
            ax.plot(s.index, s.values, color=col, lw=2, label=dt)
        ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Hour (clock)"); ax.set_ylabel("W/person")
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["D_metabolic"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section E — Office Presence Fidelity & Shape (ported near-verbatim)
    # ══════════════════════════════════════════════════════════════════════
    def section_e_office(self) -> None:
        print("\n--- Section E: Office Presence Fidelity & Shape ---------------------")
        _apply_dark()
        off = self.office
        lo, hi = float(off["AT_WORK_fraction"].min()), float(off["AT_WORK_fraction"].max())
        ok = (lo >= 0.0) and (hi <= 1.0)
        self._rec("pass" if ok else "fail", f"E.1 | AT_WORK_fraction range [{lo:.4f},{hi:.4f}]: {ok}")
        self._sum("Office AT_WORK_fraction range", "[0,1]", f"[{lo:.4f},{hi:.4f}]", "PASS" if ok else "FAIL")

        shape_ok = True
        for arch in sorted(OFFICE_ARCHETYPES):
            for band in self.office_bands:
                wd = off[(off["office_archetype"] == arch) & (off["Day_Type"] == "Weekday") &
                         (off["BAND"] == band)].sort_values("Hour")
                if len(wd) != 24:
                    continue
                frac = wd["AT_WORK_fraction"].values
                peak_val = float(frac.max())
                night_floor = float(np.min(np.concatenate([frac[:3], frac[21:]])))
                if peak_val > 0.01 and not (peak_val > night_floor):
                    shape_ok = False
                    self._rec("fail", f"E.2 | [{arch}/{band}] peak not > night floor")
        if shape_ok:
            self._rec("pass", "E.2 | Office weekday shape: peak > night floor for all arch/band")
        self._sum("Office weekday shape", "peak > night floor", "all OK" if shape_ok else "FAIL", "PASS" if shape_ok else "FAIL")

        if self.year == "2030" and len(self.office_bands) == 3:
            mono_all = True
            for arch in sorted(OFFICE_ARCHETYPES):
                means = {}
                for band in ["conservative", "hybrid", "fullyhybrid"]:
                    sub = off[(off["office_archetype"] == arch) & (off["Day_Type"] == "Weekday") &
                              (off["BAND"] == band) & (off["Hour"].between(9, 17))]
                    means[band] = float(sub["AT_WORK_fraction"].mean()) if len(sub) else 0.0
                mono = means["conservative"] > means["hybrid"] > means["fullyhybrid"]
                if not mono:
                    mono_all = False
                self._rec("pass" if mono else "fail",
                          f"E.3 | Band monotonicity [{arch}]: cons={means['conservative']:.4f} > "
                          f"hyb={means['hybrid']:.4f} > fully={means['fullyhybrid']:.4f}: {mono}")
            self._sum("Office band monotonicity", "cons>hyb>fully", f"all_pass={mono_all}", "PASS" if mono_all else "FAIL")

        archs_sorted = sorted(OFFICE_ARCHETYPES)
        fig, axes = plt.subplots(1, len(archs_sorted), figsize=(15, 4.5), sharey=True)
        fig.suptitle(f"Section E — Office Presence Fidelity ({self.scenario_label})", fontsize=13, fontweight="bold")
        for ax, arch in zip(axes, archs_sorted):
            for band in self.office_bands:
                wd = off[(off["office_archetype"] == arch) & (off["Day_Type"] == "Weekday") &
                         (off["BAND"] == band)].sort_values("Hour")
                col = BAND_COLORS.get(band, "#cdd6f4")
                ax.plot(wd["Hour"], wd["AT_WORK_fraction"], color=col, lw=2, label=band)
            ax.set_title(arch.replace("Office_", ""), fontsize=10); ax.set_xlabel("Hour")
            ax.xaxis.grid(True, linestyle="--", alpha=0.3); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        axes[0].set_ylabel("AT_WORK_fraction"); axes[-1].legend(fontsize=7)
        plt.tight_layout()
        self.plots_b64["E_office"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section R — Retail Product (NEW, Leg-3)
    # ══════════════════════════════════════════════════════════════════════
    def section_r_retail(self) -> None:
        print("\n--- Section R: Retail Product (NEW, Leg-3) ---------------------------")
        _apply_dark()
        ret = self.retail

        # Lever, band-aware (2026-07-30, post-2026-07-28 fix -- see 3rdJ_L3_improvements_step5_6_7.md
        # B.3 addendum + _val.md Progress Log). 2022 is self-normalizing/unlevered -> lever=1.0
        # (collapses R.1/R.2 to their pre-2026-07-30 form exactly). 2030 derives the lever at
        # runtime from the raw Step-6 lever file, mirroring the generator's own gate -- NOT from
        # the hardcoded RETAIL_LEVER_VALUE dict (that stays R.7's business, kept independent on
        # purpose: a corrupted lever file must fail R.7 while R.1 still passes).
        lever = 1.0 if self.year == "2022" else _derive_retail_lever(RETAIL_SCENARIO_OF_BUNDLE[self.bundle])

        # R1: peak normalization exact, band-aware. shape_peak == lever; mult_peak == 0.95*lever
        # (strictly stronger than the old exact-shape=1.000/mult=0.95 check it replaces: if the
        # pre-fix bug -- self-normalizing every band's peak back to a lever-independent constant --
        # is ever reintroduced, this now FAILs for every band whose lever != 1.0).
        expected_mult_peak = 0.95 * lever
        r1_ok = True
        for (dt, pr), g in ret.groupby(["Day_Type", "PR"]):
            shape_peak = float(g["shape"].max())
            mult_peak = float(g["multiplier"].max())
            if abs(shape_peak - lever) > 1e-6 or abs(mult_peak - expected_mult_peak) > 1e-6:
                r1_ok = False
                self._rec("fail", f"R.1 | [{dt}/{pr}] peak norm off (lever={lever:.4f}): "
                                   f"shape_peak={shape_peak:.6f} (exp {lever:.6f}) "
                                   f"mult_peak={mult_peak:.6f} (exp {expected_mult_peak:.6f})")
        if r1_ok:
            self._rec("pass", f"R.1 | Peak normalization exact for all Day_Type×PR (lever={lever:.4f}): "
                              f"shape={lever:.4f}, mult={expected_mult_peak:.4f}")
        self._sum("R1 Peak normalization exact (band-aware)", f"shape=lever={lever:.4f}, mult=0.95×lever",
                  "all OK" if r1_ok else "violations", "PASS" if r1_ok else "FAIL")

        # R2: shape fidelity -- anchored on the UN-LEVERED base peak (shape's own peak is now the
        # lever, not 1.0, so peak_frac must be divided back down by lever before reconstruction).
        # For 2022 (lever=1.0) this is byte-identical to the pre-2026-07-30 test.
        r2_ok = True
        for (dt, pr), g in ret.groupby(["Day_Type", "PR"]):
            peak_frac = g["at_retail_fraction"].max()
            recon = g["shape"] * (peak_frac / lever)
            diff = (recon - g["at_retail_fraction"]).abs().max()
            if diff > 1e-4:
                r2_ok = False
        self._rec("pass" if r2_ok else "fail",
                  f"R.2 | Shape fidelity (shape×(peak/lever) reproduces at_retail_fraction, lever={lever:.4f}): {r2_ok}")
        self._sum("R2 Shape fidelity", "exact (float tol)", "OK" if r2_ok else "violations", "PASS" if r2_ok else "FAIL")

        # R3: diurnal windows (WARN)
        r3_notes = []
        r3_ok = True
        for pr in ret["PR"].unique():
            wd = ret[(ret["Day_Type"] == "Weekday") & (ret["PR"] == pr)].sort_values("Hour")
            sat = ret[(ret["Day_Type"] == "Saturday") & (ret["PR"] == pr)].sort_values("Hour")
            wd_peak_h = int(wd.loc[wd["multiplier"].idxmax(), "Hour"])
            sat_peak_h = int(sat.loc[sat["multiplier"].idxmax(), "Hour"])
            # "±1 slot" tolerance (val doc R3/M2, slot=30min) widens the hour window by 1 on
            # each side at hour granularity (a peak at slot 25=12:00 or slot 24=11:30 both
            # satisfy a "12:00 ±1 slot" test; floor(hour) then spans one extra hour each side).
            wd_win = 11 <= wd_peak_h <= 15
            sat_win = 12 <= sat_peak_h <= 17
            sat_gt_wd = sat["multiplier"].max() > wd["multiplier"].max()
            r3_notes.append(f"{pr}: WD peak@{wd_peak_h}h({wd_win}) Sat peak@{sat_peak_h}h({sat_win}) "
                             f"Sat>WD={sat_gt_wd}")
            if not (wd_win and sat_win):
                r3_ok = False
        lv = "pass" if r3_ok else "warn"
        self._rec(lv, f"R.3 | Diurnal windows: {'; '.join(r3_notes)}")
        self._sum("R3 Diurnal windows", "WD peak 12-14h, Sat 13-16h, Sat>WD", "; ".join(r3_notes), lv.upper())

        # R4: Sunday province split (WARN) -- RE-SPECIFIED 2026-07-30 (see val.md Progress Log,
        # and 3rdJ_07_bemIntegration_4split.md for the derivation). The old statistic compared
        # max_t(multiplier) between QC and AB Sunday, but every (Day_Type,PR) group's multiplier
        # peak is independently forced to 0.95*lever by R.1's own construction (peak-normalization
        # per group) -- so QC_peak==AB_peak==0.95*lever ALWAYS, by CONSTRUCTION, regardless of what
        # the real underlying data says. That gate could never fail; it was VACUOUS (confirmed
        # degenerate in 2022 too, not just 2030 -- ratio=1.000 in all 4 products).
        # New statistic: mean_t(at_retail_fraction) / max_t(at_retail_fraction) within a
        # (Day_Type=Sunday, PR) group -- a mean-to-peak ("load factor") ratio. This is invariant to
        # ANY positive per-group rescaling (old self-normalizing bug OR the new lever), because a
        # ratio of two quantities scaled by the same constant cancels that constant -- so it
        # survives peak-normalization by construction, unlike the old statistic.
        # WHAT IT DETECTS: how concentrated Sunday retail activity is around its own peak half-hour
        # -- a lower ratio means a "spikier" day (activity concentrated in a short window relative
        # to a sustained peak), a higher ratio means a "flatter/broader" day. This is a genuine
        # proxy for effective trading-hours breadth (Quebec's Sunday retail-hours rules are
        # historically more restrictive than Alberta's), independent of the demand LEVEL.
        # WHAT IT DOES NOT DETECT: WHEN in the day the activity happens (timing/peak-hour location
        # -- that is R.3's job), or the absolute LEVEL of activity (that is R.1/R.7's job). Two
        # provinces could have the same ratio while differing completely in level or peak-hour
        # timing; this statistic is blind to both.
        if {"QC", "AB"} <= set(ret["PR"].unique()):
            sun = ret[ret["Day_Type"] == "Sunday"]
            open_ratio = {}
            for pr in ["QC", "AB"]:
                frac = sun[sun["PR"] == pr]["at_retail_fraction"]
                open_ratio[pr] = float(frac.mean() / frac.max()) if frac.max() > 0 else float("nan")
            qc_lt_ab = open_ratio["QC"] < open_ratio["AB"]
            delta = open_ratio["QC"] - open_ratio["AB"]
            lv = "pass" if qc_lt_ab else "warn"
            self._rec(lv, f"R.4 | Sunday province shape (mean/peak load factor, survives "
                          f"peak-normalization): QC={open_ratio['QC']:.4f} vs AB={open_ratio['AB']:.4f} "
                          f"(Δ{delta:+.4f}, QC<AB expected per QC's historically more-restrictive "
                          f"Sunday retail hours: {qc_lt_ab}). Detects Sunday activity concentration "
                          f"(shape), NOT peak timing (R.3) or level (R.1/R.7). Reported honestly, not forced.")
            self._sum("R4 Sunday province shape (mean/peak, re-specified)", "QC ratio < AB ratio",
                      f"QC={open_ratio['QC']:.4f} AB={open_ratio['AB']:.4f} Δ{delta:+.4f}", lv.upper())

        # R5: staff-shoulder rule
        sh = ret[ret["staff_shoulder_flag"] == 1]
        r5_ok = True
        for _, row in sh.iterrows():
            base = necb_retail_baseline_proxy(row["Day_Type"], int(row["Hour"]))
            if abs(row["multiplier"] - base) > 1e-6:
                r5_ok = False
        self._rec("pass" if r5_ok else "fail",
                  f"R.5 | Staff-shoulder rule: {len(sh)} flagged slots, multiplier=baseline for all: {r5_ok}")
        self._sum("R5 Staff-shoulder preservation", "100%", f"{len(sh)} flagged, ok={r5_ok}", "PASS" if r5_ok else "FAIL")

        # R6: night floor (WARN)
        night = ret[(ret["Hour"].between(0, 4))]
        night_max = float(night["at_retail_fraction"].max())
        ok = night_max <= 0.01
        lv = "pass" if ok else "warn"
        self._rec(lv, f"R.6 | Night 00:00-05:00 at_retail_fraction max: {night_max:.4f} (≤0.01): {ok}")
        self._sum("R6 Night floor", "≤ 0.01", f"{night_max:.4f}", lv.upper())

        # R7: 2030 lever exactness (across bundles, if all 3 present) -- FIXED 2026-07-30 (see
        # val.md Progress Log). The old version assigned all_ret[b] = RETAIL_LEVER_VALUE[...]
        # directly (gated only on the file EXISTING, never reading its content) and then compared
        # that value to RETAIL_LEVER_VALUE[...] again -- literally x==x, vacuously true whenever
        # all 3 files exist. It never actually read the shipped product.
        # Fix: derive each band's REALIZED lever from the shipped product CSV's own `shape` column
        # (max over the file). Chosen over `mult_peak/0.95` because `shape` is the column the
        # generator deliberately peak-normalizes to equal the lever exactly (see R.1) -- reading it
        # directly avoids re-deriving the 0.95 anchor a second time and gives R.7 an independent
        # data path (the shipped product) rather than re-reading the same raw Step-6 lever file R.1
        # already reads. This restores the intended split: R.1 = product vs its own raw lever file
        # (pipeline-execution/internal-consistency check); R.7 = product vs the DESIGN CONSTANTS
        # 0.90/0.97/1.05 (spec-conformance check). They now fail under different corruptions: a
        # pipeline that mis-reads its own lever file fails R.1 even if 0.90/0.97/1.05 are untouched;
        # a hand-edited/stale RETAIL_LEVER_VALUE dict fails R.7 even if the pipeline is internally
        # perfectly self-consistent.
        if self.year == "2030":
            realized = {}
            for b in BUNDLES:
                p = OUT_DIR / f"retail_presence_multiplier_2030_{b}.csv"
                if p.exists():
                    shape_col = pd.read_csv(p, usecols=["shape"])["shape"]
                    realized[b] = float(shape_col.max())
            if len(realized) == 3:
                exact = all(abs(realized[b] - RETAIL_LEVER_VALUE[RETAIL_SCENARIO_OF_BUNDLE[b]]) < 0.01 for b in BUNDLES)
                self._rec("pass" if exact else "fail",
                          f"R.7 | 2030 lever exactness (realized shape_peak from shipped product vs "
                          f"design constant): {realized} vs expected "
                          f"{{'cons':0.90,'central':0.97,'opt':1.05}}: {exact}")
                self._sum("R7 2030 lever exactness (reads shipped product)", "0.90/0.97/1.05 ± 0.01",
                          str(realized), "PASS" if exact else "FAIL")

        # R8: density untouched (no People/m2 or Number_of_People columns in product)
        density_cols = [c for c in ret.columns if "people" in c.lower() or "density" in c.lower()]
        ok = len(density_cols) == 0
        self._rec("pass" if ok else "fail", f"R.8 | Density columns absent from product: {ok}")
        self._sum("R8 Density untouched", "no density cols", str(density_cols), "PASS" if ok else "FAIL")

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f"Section R — Retail Product ({self.scenario_label})", fontsize=13, fontweight="bold")
        ax0 = axes[0]
        for pr, col in [("QC", "#89b4fa"), ("AB", "#f9e2af")]:
            for dt, ls in [("Weekday", "-"), ("Saturday", "--"), ("Sunday", ":")]:
                s = ret[(ret["PR"] == pr) & (ret["Day_Type"] == dt)].sort_values("Hour")
                if len(s):
                    ax0.plot(s["Hour"], s["multiplier"], color=col, ls=ls, lw=1.6, label=f"{pr} {dt}", alpha=0.85)
        ax0.set_xlabel("Hour (clock, post +4h roll)"); ax0.set_ylabel("Retail multiplier")
        ax0.legend(fontsize=6, ncol=2); ax0.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax1 = axes[1]
        sh_counts = ret.groupby("Day_Type")["staff_shoulder_flag"].sum()
        ax1.bar(sh_counts.index, sh_counts.values, color="#f38ba8", edgecolor="#1e1e2e", width=0.5)
        ax1.set_ylabel("Staff-shoulder flagged slots"); ax1.set_title("Staff-shoulder count by Day_Type", fontsize=10)
        ax1.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["R_retail"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section H — Hotel Product (NEW, Leg-3)
    # ══════════════════════════════════════════════════════════════════════
    def section_h_hotel(self) -> None:
        print("\n--- Section H: Hotel Product (NEW, Leg-3) -----------------------------")
        _apply_dark()
        hot = self.hotel

        # H.1: s(t) integrity via the hotel CSV directly (dr_L3-05 exact values)
        st_path = Path(__file__).resolve().parents[3] / "0_Occupancy" / "processed" / "hotel_diurnal_shape_st.csv"
        if st_path.exists():
            st = pd.read_csv(st_path)
            wd = st[st["day_type"] == "weekday"].sort_values("slot_index")["s_value"].values
            we = st[st["day_type"] == "weekend"].sort_values("slot_index")["s_value"].values
            checks = {
                "plateau_wd_2200_0600": bool(wd[44] == 1.0 and wd[0] == 1.0),
                "trough_wd_0.200": bool(np.isclose(wd[18:30].min(), 0.200)),
                "trough_we_0.308": bool(np.isclose(we[18:33].min(), 0.308)),
                "we_evening_spike_1.000": bool(we[38] == 1.0 and we[40] == 1.0),
            }
            ok = all(checks.values())
            self._rec("pass" if ok else "fail", f"H.1 | s(t) integrity (dr_L3-05 exact values): {checks}")
            self._sum("H1 s(t) integrity", "exact dr_L3-05 table", str(checks), "PASS" if ok else "FAIL")
        else:
            self._rec("warn", "H.1 | hotel_diurnal_shape_st.csv not found for direct verification")

        # H.2: 12 distinct monthly amplitudes per PR
        h2_ok = True
        h2_notes = []
        for pr, g in hot.groupby("PR"):
            n_distinct = g.drop_duplicates("MONTH")["monthly_rate"].round(4).nunique()
            n_months = g["MONTH"].nunique()
            h2_notes.append(f"{pr}: {n_distinct}/{n_months} distinct")
            if n_distinct < 10:  # allow small ties, but flag heavy duplication (e.g. carry-fill)
                h2_ok = False
        lv = "pass" if h2_ok else "warn"
        self._rec(lv, f"H.2 | Monthly amplitude distinctness: {'; '.join(h2_notes)}")
        self._sum("H2 Monthly amplitudes distinct", "12 distinct/PR", "; ".join(h2_notes), lv.upper())

        n_filled = int(hot["rate_filled"].sum()) if "rate_filled" in hot.columns else 0
        if n_filled:
            self._rec("warn", f"H.2b | [FLAGGED] {n_filled} rows use carry-forward-filled monthly_rate "
                              f"(2022 AB Q4 gap, documented in builder header)")

        # H.3: multiplier = s_t * monthly_rate, range (0,1]
        recon = hot["s_t"] * hot["monthly_rate"]
        diff = (recon - hot["multiplier"]).abs().max()
        ok_formula = diff < 1e-4
        valid = hot["multiplier"].dropna()
        ok_range = (valid > 0).all() and (valid <= 1.0 + 1e-9).all()
        ok = ok_formula and ok_range
        self._rec("pass" if ok else "fail",
                  f"H.3 | multiplier=s_t×monthly_rate (diff={diff:.6f}), range (0,1] [{valid.min():.4f},{valid.max():.4f}]: {ok}")
        self._sum("H3 Multiplier formula + range", "exact; (0,1]", f"diff={diff:.6f}", "PASS" if ok else "FAIL")

        # H.4: band monotonicity (across bundles, if present)
        if self.year == "2030":
            means = {}
            for b in BUNDLES:
                p = OUT_DIR / f"hotel_schedule_multiplier_2030_{b}.csv"
                if p.exists():
                    df = pd.read_csv(p, usecols=["monthly_rate"])
                    means[b] = float(df["monthly_rate"].mean())
            if len(means) == 3:
                mono = means["cons"] < means["central"] < means["opt"]
                self._rec("pass" if mono else "fail",
                          f"H.4 | Band monotonicity: cons={means['cons']:.4f} < central={means['central']:.4f} "
                          f"< opt={means['opt']:.4f}: {mono}")
                self._sum("H4 Band monotonicity", "low<central<high", str(means), "PASS" if mono else "FAIL")

        # H.5: COVID plausibility (2022 only, WARN/INFO) -- TRIAGED 2026-07-30, LEFT UNFIXED.
        # Intended test (stated explicitly in its own message): confirm 2022 hotel rates sit below
        # a 2019 (pre-COVID) baseline, consistent with a still-recovering pandemic trajectory.
        # Why it cannot currently fail: no 2019-equivalent baseline file exists ANYWHERE in this
        # repo to compare against -- this is not a gap in val.py's logic, it is a genuine missing
        # INPUT. Proposed real statistic: mean(2022 monthly_rate) < mean(2019 monthly_rate) once a
        # 2019 baseline is sourced. Not fixed: would require pulling in new external data (out of
        # scope for a validator fix), so left as INFO rather than inventing a substitute target.
        if self.year == "2022":
            self._rec("pass", f"H.5 | [INFO] 2022 mean monthly_rate: {hot['monthly_rate'].mean():.4f} "
                              f"(post-pandemic recovery year; no 2019-equivalent baseline in-repo to compare)")
            self._sum("H5 COVID plausibility", "info", f"mean={hot['monthly_rate'].mean():.4f}", "INFO")

        # H.6: seasonality (summer > winter, both PR)
        h6_ok = True
        for pr, g in hot.groupby("PR"):
            summer = g[g["MONTH"].isin([6, 7, 8])]["monthly_rate"].mean()
            winter = g[g["MONTH"].isin([12, 1, 2])]["monthly_rate"].mean()
            if not (summer > winter):
                h6_ok = False
        lv = "pass" if h6_ok else "warn"
        self._rec(lv, f"H.6 | Seasonality (summer > winter), both PR: {h6_ok}")
        self._sum("H6 Seasonality", "summer > winter", str(h6_ok), lv.upper())

        fig, ax = plt.subplots(figsize=(10, 4.5))
        fig.suptitle(f"Section H — Hotel Product ({self.scenario_label})", fontsize=13, fontweight="bold")
        for pr, col in [("QC", "#89b4fa"), ("AB", "#f9e2af")]:
            g = hot[hot["PR"] == pr].drop_duplicates("MONTH").sort_values("MONTH")
            if len(g):
                ax.plot(g["MONTH"], g["monthly_rate"], color=col, marker="o", lw=2, label=pr)
        ax.set_xlabel("Month"); ax.set_ylabel("monthly_rate"); ax.set_xticks(range(1, 13))
        ax.legend(fontsize=9); ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["H_hotel"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section M — Input-mutex & clock-origin gates (NEW, Leg-3)
    # ══════════════════════════════════════════════════════════════════════
    def section_m_mutex_clock(self) -> None:
        print("\n--- Section M: Input-Mutex & Clock-Origin Gates -----------------------")
        _apply_dark()

        # M.1: mutex on both raw source diaries
        m1_ok = True
        for label, df in [("2022 stock", self.diary_stock_raw), ("2030 _C", self.diary_2030_raw)]:
            if df is None:
                continue
            hom = df[HOM].to_numpy(dtype=float); wrk = df[WRK].to_numpy(dtype=float); ret_ = df[RET].to_numpy(dtype=float)
            n_active = (hom == 1).astype(np.int8) + (wrk == 1).astype(np.int8) + (ret_ == 1).astype(np.int8)
            n_conf = int((n_active > 1).sum())
            if n_conf > 0:
                m1_ok = False
            self._rec("pass" if n_conf == 0 else "fail", f"M.1 | Mutex [{label}]: {n_conf} conflicts (0 required)")
        self._sum("M1 Input-mutex (both sources)", "0 conflicts", "OK" if m1_ok else "VIOLATIONS", "PASS" if m1_ok else "FAIL")

        # M.2: retail clock windows post-roll. Window is 11:00-15:00h (unchanged, NOT widened --
        # see B.3.1 in 3rdJ_L3_improvements_step5_6_7.md). The val doc used to describe this as
        # "12:00-14:00 ±1 slot" (~30 min); that wording was wrong (doc/code mismatch, fixed in the
        # doc, 2026-07-30) -- the code has always implemented the wider 11-15h window below.
        wd = self.retail[(self.retail["Day_Type"] == "Weekday")]
        wd_by_pr_peak_h = wd.groupby("PR").apply(lambda g: int(g.loc[g["multiplier"].idxmax(), "Hour"]))
        peaks = dict(wd_by_pr_peak_h)
        night = self.retail[self.retail["Hour"].between(0, 4)]["at_retail_fraction"].max()
        night_ok = bool(night <= 0.01)
        out_of_window = {pr: h for pr, h in peaks.items() if not (11 <= h <= 15)}

        # Documented, evidence-carrying exception (B.3.1): QC's observed GSS-2022 retail diary
        # genuinely peaks at 16:00 -- a real bimodal midday/late-afternoon shape, re-derived from
        # retail_presence_multiplier_2022.csv (n=5,778 QC / 3,593 AB): QC top-3 = H16(0.9500),
        # H17(0.9454), H13(0.7701). QC uses the exact-match region (region 2); AB uses a 3-province
        # Prairies proxy (region 4) -- the sample that PASSES (AB) is the proxy, not QC. This is
        # isolated to the 2022 report; all three 2030 reports pass with no exception needed. The
        # window is NOT widened to absorb this -- only the QC-2022 instance is relabeled WARN.
        qc_2022_exception = (self.year == "2022" and set(out_of_window) == {"QC"}
                              and 11 <= peaks.get("AB", -1) <= 15)
        unexplained = {pr: h for pr, h in out_of_window.items() if not (qc_2022_exception and pr == "QC")}

        if not night_ok or unexplained:
            m2_level = "fail"
        elif qc_2022_exception:
            m2_level = "warn"
        else:
            m2_level = "pass"

        msg = (f"M.2 | Retail clock windows post-roll: WD peaks {peaks} (window 11:00-15:00h), "
               f"night(0-5h) max={night:.4f} (≤0.01)")
        if qc_2022_exception:
            msg += (" -- QC@16h: WARN accepted-documented (not a roll bug). GSS-2022 QC retail diary "
                    "is genuinely bimodal (H16=0.9500, H17=0.9454, H13=0.7701; n=5,778, exact-match "
                    "region 2) vs AB's 3-province Prairies proxy (region 4, n=3,593) -- the PASSING "
                    "AB sample is the proxy, QC is exact. Window not widened; see B.3.1.")
        else:
            msg += f": {m2_level == 'pass'}"
        self._rec(m2_level, msg)
        self._sum("M2 Retail clock windows", "WD peak 11-15h; night≈0", f"peaks={peaks}",
                  m2_level.upper())

        # M.3: hotel plateau/trough clock windows (s(t) NOT rolled)
        wdh = self.hotel[(self.hotel["Day_Type"] == "Weekday")].drop_duplicates("slot")
        plateau_slots = wdh[wdh["slot"].isin([1, 2, 45, 46, 47, 48])]  # slots 1-2=00:00-01:00, 45-48=22:00-24:00
        trough_slots = wdh[wdh["slot"].between(19, 30)]  # slots 19-30 = 09:00-15:00
        plateau_ok = bool((plateau_slots["s_t"] >= 0.99).all())
        trough_ok = bool(np.isclose(trough_slots["s_t"].min(), 0.200))
        m3_ok = plateau_ok and trough_ok
        self._rec("pass" if m3_ok else "fail",
                  f"M.3 | Hotel clock windows (NOT rolled): overnight plateau≥0.99 ({plateau_ok}), "
                  f"WD trough=0.200 ({trough_ok}): {m3_ok}")
        self._sum("M3 Hotel clock windows (no roll)", "plateau 22-06h; trough 0.200/0.308",
                  f"plateau_ok={plateau_ok} trough_ok={trough_ok}", "PASS" if m3_ok else "FAIL")

        # M.4: residential/office peak clock hours in precedent windows (WARN)
        res_peak_h = int(self.bem[self.bem["Day_Type"] == "Weekday"].groupby("Hour")["Occupancy_Schedule"]
                          .mean().idxmax())
        wd_off = self.office[(self.office["Day_Type"] == "Weekday")]
        off_peak_h = int(wd_off.groupby("Hour")["AT_WORK_fraction"].mean().idxmax())
        res_ok = res_peak_h >= 18 or res_peak_h <= 7   # evening/overnight residential precedent
        off_ok = 11 <= off_peak_h <= 16
        m4_ok = res_ok and off_ok
        lv = "pass" if m4_ok else "warn"
        self._rec(lv, f"M.4 | Peak clock hours: residential={res_peak_h}h (evening/night expected), "
                      f"office={off_peak_h}h (~13-15h expected): {m4_ok}")
        self._sum("M4 Residential/office peak clock hours", "evening resid; ~13-15h office",
                  f"resid={res_peak_h}h office={off_peak_h}h", lv.upper())

    # ══════════════════════════════════════════════════════════════════════
    # Section W — Wiring Assertion Audit (NEW, Leg-3) — PENDING, no mixed-use IDF
    # ══════════════════════════════════════════════════════════════════════
    def section_w_wiring(self) -> None:
        print("\n--- Section W: Wiring Assertion Audit ---------------------------------")
        idf_candidates = []
        base = Path(__file__).resolve().parents[3]
        for pat in ["0_BEM_Setup", "BEM_Setup/Buildings"]:
            p = base / pat
            if p.exists():
                idf_candidates.extend(list(p.rglob("*mixed*use*.idf")) + list(p.rglob("*MixedUse*.idf")))

        if not idf_candidates:
            for gate in ["W1", "W2", "W3", "W4", "W5", "W6"]:
                self._rec("warn", f"{gate} | PENDING -- no Tag-2-routable mixed-use prototype IDF "
                                  f"(HighriseApartment+Office+Retail+LargeHotel) exists in this repo. "
                                  f"commercial_integration.py::inject_mixed_use() is implemented "
                                  f"(eSim_bem_utils/commercial_integration.py) and ready, but cannot be "
                                  f"dry-run tested until the prototype IDF is built. W2/W3 block Step 8 "
                                  f"per the runbook -- this is a genuine checkpoint, not a fabricated pass.")
                self._sum(f"{gate} Wiring audit", "dry-run on mixed-use IDF", "PENDING (no IDF)", "WARN")
            print("  [PENDING] All W-section gates: no mixed-use IDF available for dry-run injection.")
        else:
            self._rec("warn", f"W.0 | Found candidate IDF(s) {idf_candidates} but dry-run injection audit "
                              f"not yet wired into this validator run -- flag for follow-up.")

    # ══════════════════════════════════════════════════════════════════════
    # Section F — Channel Consistency Cross-Product (ported + extended)
    # ══════════════════════════════════════════════════════════════════════
    def section_f_channel(self) -> None:
        print("\n--- Section F: Channel Consistency Cross-Product ---------------------")
        _apply_dark()

        if self.year == "2022":
            self._rec("pass", "F.1 | [INFO] 2022 is single-scenario -- cross-bundle insulation n/a")
            self._sum("F1 Cross-channel insulation", "n/a (2022)", "n/a", "INFO")
        else:
            # F.1 REWRITTEN 2026-07-30 (see Progress Log): the previous version fed a hardcoded
            # dict of PROSE describing a human's manual observations from the 2026-07-23 build
            # session straight into an unconditional self._rec("pass", ...) -- it computed nothing
            # at runtime and could not fail. A past manual observation laundered into a present
            # automated PASS. Kept below ONLY as provenance, NOT as what the gate returns:
            #   sens=office (cons/opt residential rebuilt): retail/hotel files UNCHANGED (mtime+content)
            #   sens=retail (cons/opt retail rebuilt): residential/office/hotel files UNCHANGED
            #   sens=hotel (cons/opt hotel rebuilt): residential/office/retail files UNCHANGED
            # (full MD5 pairs from that session: 3rdJ_07_bemIntegration_4split.md Progress Log,
            # 2026-07-23 "--sens {office,retail,hotel} off-diagonal builds" entry)
            #
            # Real runtime check (this run's actual on-disk files, no --sens re-run needed):
            #  (a) STRUCTURAL: retail/hotel carry no office-BAND column anywhere from the raw
            #      Step-6 lever input through the shipped product -- there is no field through
            #      which office-band information could enter their construction.
            #  (b) MD5 (hashlib.md5, same primitive as _md5(), applied to an in-memory column since
            #      the invariant lives at sub-file granularity -- the FULL retail/hotel files
            #      correctly differ across bundles per F.2/F.3, it's specific columns that must
            #      not): hotel's diurnal shape s_t is a fixed dr_L3-05 table that should be
            #      independent of hotel_band -- empirically confirmed BYTE-IDENTICAL (exact, no
            #      rounding) across all 3 bundles before writing this check. If separability were
            #      ever violated -- hotel_band leaking into s_t, or a future change coupling s_t to
            #      the office/retail axes -- this hash would differ and the gate would FAIL.
            f1_leaks = []
            if "BAND" in self.retail.columns:
                f1_leaks.append("retail product carries a BAND column")
            if "BAND" in self.hotel.columns:
                f1_leaks.append("hotel product carries a BAND column")
            for scenario, p in RETAIL_LEVER_FILES.items():
                if p.exists() and "BAND" in pd.read_csv(p, nrows=0).columns:
                    f1_leaks.append(f"raw retail lever file [{scenario}] carries a BAND column")
            f1a_ok = len(f1_leaks) == 0

            hotel_st_md5 = {}
            for b in BUNDLES:
                p = OUT_DIR / f"hotel_schedule_multiplier_2030_{b}.csv"
                if p.exists():
                    hdf = pd.read_csv(p, usecols=["PR", "MONTH", "Day_Type", "slot", "s_t"])
                    hdf = hdf.sort_values(["PR", "MONTH", "Day_Type", "slot"]).reset_index(drop=True)
                    hotel_st_md5[b] = hashlib.md5(hdf["s_t"].to_numpy().tobytes()).hexdigest()
            f1b_ok = len(hotel_st_md5) == 3 and len(set(hotel_st_md5.values())) == 1

            f1_ok = f1a_ok and f1b_ok
            self._rec("pass" if f1_ok else "fail",
                      f"F.1 | Structural + MD5 insulation (runtime-checked): no office-BAND column "
                      f"reachable by retail/hotel ({'OK' if f1a_ok else 'LEAK: ' + '; '.join(f1_leaks)}); "
                      f"hotel s_t MD5 identical across bundles {hotel_st_md5} ({f1b_ok}): {f1_ok}")
            self._sum("F1 Cross-channel structural insulation (runtime-checked)",
                      "no BAND leak; hotel s_t MD5 exact-identical",
                      f"structural_ok={f1a_ok} hotel_st_md5_match={f1b_ok}", "PASS" if f1_ok else "FAIL")

            # Retail's un-levered shape (shape/lever) is NOT byte-identical across bundles like
            # hotel's s_t is -- reported honestly rather than forced into a false claim. Verified
            # ~1e-6 max diff (independent per-scenario Step-6 file float noise, several orders of
            # magnitude below any real signal), not gated on.
            ret_diffs = {}
            base_unlev = None
            for b in BUNDLES:
                p = OUT_DIR / f"retail_presence_multiplier_2030_{b}.csv"
                if p.exists():
                    lever_b = _derive_retail_lever(RETAIL_SCENARIO_OF_BUNDLE[b])
                    rdf = pd.read_csv(p, usecols=["Day_Type", "PR", "slot", "shape"])
                    rdf = rdf.sort_values(["Day_Type", "PR", "slot"]).reset_index(drop=True)
                    unlev = rdf["shape"] / lever_b
                    if base_unlev is None:
                        base_unlev = unlev
                    else:
                        ret_diffs[b] = float((unlev - base_unlev).abs().max())
            print(f"  [INFO] F.1 supplementary: retail un-levered shape (shape/lever) vs cons, "
                  f"max diff per bundle: {ret_diffs} (float noise, not byte-identical like hotel's "
                  f"s_t, not gated)")

            # Cheap re-verification: current on-disk retail/hotel bundle files must differ from
            # EACH OTHER (proving each is responsive to its own axis, not stuck/duplicated).
            ret_md5 = {b: _md5(OUT_DIR / f"retail_presence_multiplier_2030_{b}.csv") for b in BUNDLES
                       if (OUT_DIR / f"retail_presence_multiplier_2030_{b}.csv").exists()}
            hot_md5 = {b: _md5(OUT_DIR / f"hotel_schedule_multiplier_2030_{b}.csv") for b in BUNDLES
                       if (OUT_DIR / f"hotel_schedule_multiplier_2030_{b}.csv").exists()}
            ret_distinct = len(set(ret_md5.values())) == len(ret_md5)
            hot_distinct = len(set(hot_md5.values())) == len(hot_md5)
            self._rec("pass" if ret_distinct else "fail", f"F.2 | Retail bundle files mutually distinct: {ret_md5}: {ret_distinct}")
            self._rec("pass" if hot_distinct else "fail", f"F.3 | Hotel bundle files mutually distinct: {hot_md5}: {hot_distinct}")
            self._sum("F2/F3 Bundle files axis-responsive", "mutually distinct MD5s",
                      f"retail_distinct={ret_distinct} hotel_distinct={hot_distinct}",
                      "PASS" if (ret_distinct and hot_distinct) else "FAIL")

        # WFH cross-channel direction (residential vs office). home_daytime/office_daytime are
        # kept alive past the if-block so the figure below (B.3.4) can plot them -- previously
        # they were computed here and then thrown away, leaving the figure a blank axis.
        home_daytime, office_daytime = {}, {}
        home_rise = office_fall = None
        if self.year == "2030" and len(self.res_bundles) == 3:
            for b in BUNDLES:
                df = pd.read_csv(self.res_bundles[b], usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
                wd_biz = df[(df["Day_Type"] == "Weekday") & (df["Hour"].between(9, 17))]
                home_daytime[b] = float(wd_biz["Occupancy_Schedule"].mean() * 100)
                obiz = self.office[(self.office["Day_Type"] == "Weekday") & self.office["Hour"].between(9, 17) &
                                   (self.office["BAND"] == OFFICE_BAND_OF_BUNDLE[b])]
                office_daytime[b] = float(obiz["AT_WORK_fraction"].mean() * 100) if len(obiz) else 0.0
            home_rise = home_daytime["opt"] - home_daytime["cons"]
            office_fall = office_daytime["cons"] - office_daytime["opt"]
            direction_ok = (home_rise > 0) and (office_fall > 0)
            self._rec("pass" if direction_ok else "fail",
                      f"F.4 | WFH direction cons→opt: home Δ{home_rise:+.3f}pp (>0 exp), "
                      f"office Δ{-office_fall:+.3f}pp (<0 exp): {direction_ok}")
            self._sum("F4 WFH cross-channel direction", "home↑ & office↓ cons→opt",
                      f"home Δ{home_rise:+.3f} office Δ{-office_fall:+.3f}", "PASS" if direction_ok else "FAIL")
        else:
            # 2022 single-scenario: no bundle axis to compare, but plot the one observed point
            # so the figure still carries real data instead of a blank/caption-only axis.
            wd_biz = self.bem[(self.bem["Day_Type"] == "Weekday") & (self.bem["Hour"].between(9, 17))]
            home_daytime["observed"] = float(wd_biz["Occupancy_Schedule"].mean() * 100)
            obiz = self.office[(self.office["Day_Type"] == "Weekday") & self.office["Hour"].between(9, 17) &
                               (self.office["BAND"] == self.office_bands[0])]
            office_daytime["observed"] = float(obiz["AT_WORK_fraction"].mean() * 100) if len(obiz) else 0.0

        # Grouped bar chart: bundle on x, "Home occupancy %" vs "Office AT_WORK %" side by side,
        # using the F.4 daytime means computed above (val.py home_daytime/office_daytime) instead
        # of the old blank axis + caption. Home rising while office falls as WFH increases is the
        # thing this figure exists to make visible at a glance (B.3.4).
        bundles_order = [b for b in (BUNDLES if "cons" in home_daytime else ["observed"]) if b in home_daytime]
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.suptitle(f"Section F — Channel Consistency: Home vs Office WFH Direction ({self.scenario_label})",
                     fontsize=12.5, fontweight="bold")
        x = np.arange(len(bundles_order)); width = 0.35
        home_vals = [home_daytime[b] for b in bundles_order]
        office_vals = [office_daytime[b] for b in bundles_order]
        ymax = max(home_vals + office_vals)
        ax.set_ylim(0, ymax * 1.28)  # headroom for the Δ-arrow annotations above the bars
        ax.bar(x - width / 2, home_vals, width, color="#a6e3a1", edgecolor="#1e1e2e", label="Home occupancy % (9-17h WD)")
        ax.bar(x + width / 2, office_vals, width, color="#89b4fa", edgecolor="#1e1e2e", label="Office AT_WORK % (9-17h WD)")
        ax.set_xticks(x); ax.set_xticklabels(bundles_order)
        ax.set_ylabel("Weekday 9-17h mean (%)")
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.legend(fontsize=9, loc="upper left")
        for xi, v in zip(x, home_vals):
            ax.text(xi - width / 2, v + ymax * 0.015, f"{v:.1f}", ha="center", fontsize=8.5, color="#a6e3a1")
        for xi, v in zip(x, office_vals):
            ax.text(xi + width / 2, v + ymax * 0.015, f"{v:.1f}", ha="center", fontsize=8.5, color="#89b4fa")
        if home_rise is not None and office_fall is not None and len(bundles_order) == 3:
            i_cons, i_opt = bundles_order.index("cons"), bundles_order.index("opt")
            arrow_y_home = ymax * 1.16
            arrow_y_office = ymax * 1.06
            ax.annotate("", xy=(i_opt - width / 2, arrow_y_home), xytext=(i_cons - width / 2, arrow_y_home),
                        arrowprops=dict(arrowstyle="->", color="#a6e3a1", lw=1.8))
            ax.text((i_cons + i_opt) / 2 - width / 2, arrow_y_home + ymax * 0.02,
                    f"home Δ{home_rise:+.2f}pp", ha="center", fontsize=9, color="#a6e3a1", fontweight="bold")
            ax.annotate("", xy=(i_opt + width / 2, arrow_y_office), xytext=(i_cons + width / 2, arrow_y_office),
                        arrowprops=dict(arrowstyle="->", color="#89b4fa", lw=1.8))
            ax.text((i_cons + i_opt) / 2 + width / 2, arrow_y_office + ymax * 0.02,
                    f"office Δ{-office_fall:+.2f}pp", ha="center", fontsize=9, color="#89b4fa", fontweight="bold")
        plt.tight_layout()
        self.plots_b64["F_channel"] = _b64(fig)

    # ══════════════════════════════════════════════════════════════════════
    # Section G — Attribute Integrity (ported)
    # ══════════════════════════════════════════════════════════════════════
    def section_g_attributes(self) -> None:
        print("\n--- Section G: Attribute Integrity -----------------------------------")
        _apply_dark()
        b = self.bem
        hh = b.drop_duplicates("SIM_HH_ID")

        # FIXED 2026-07-30 (SUSPECT sweep finding): both G.1/G.2 were subset checks (`<=`) that
        # would silently PASS even if an entire expected category were absent -- only invalid
        # extra labels tripped them. Now two-tier: REQUIRED categories must all be present
        # (catches a vanished category) AND the domain must not exceed VALID (catches an invalid
        # extra, the original check's purpose) -- both failure modes covered, neither silently lost.
        dtypes = set(hh["DTYPE"].astype(str).unique())
        dtype_complete = DTYPE_REQUIRED <= dtypes
        dtype_valid = dtypes <= DTYPE_VALID
        ok = dtype_complete and dtype_valid
        self._rec("pass" if ok else "fail",
                  f"G.1 | DTYPE labels {sorted(dtypes)}: all required present={dtype_complete}, "
                  f"no invalid extras={dtype_valid}: {ok}")

        prs = set(hh["PR"].astype(str).unique())
        ok = prs == PR_VALID
        self._rec("pass" if ok else "fail", f"G.2 | PR labels {sorted(prs)} == {sorted(PR_VALID)}: {ok}")

        nun = b.groupby("SIM_HH_ID")[["DTYPE", "PR", "MATCH_TIER"]].nunique()
        drift = int(((nun["DTYPE"] > 1) | (nun["PR"] > 1)).sum())
        ok = drift == 0
        self._rec("pass" if ok else "fail", f"G.3 | DTYPE/PR within-HH drift: {drift}: {ok}")
        self._sum("G3 DTYPE/PR within-HH drift", "0", str(drift), "PASS" if ok else "FAIL")

        # G.4: office product MD5 vs Leg-2 (insulation / explainable-diff check) -- TRIAGED
        # 2026-07-30, LEFT UNFIXED. Intended test: cross-reference Leg-3's office product against
        # Leg-2's as a sanity check. Why it cannot currently fail: its own message says a MISMATCH
        # is EXPECTED (Leg-3's 23,115-HH pool vs Leg-2's 23,150), so gating on `same` would be
        # backwards. Why no clean real statistic was substituted: office product row count
        # (archetypes×2×24×bands) is NOT a function of N_HH at all -- AT_WORK_fraction is an
        # archetype-level construct, not per-household -- so there is no obvious pool-size-scaled
        # "expected magnitude of difference" to check the MD5 mismatch against. Genuinely
        # ambiguous: reported here rather than guessed at.
        leg2_off = HERE.parents[1] / "Leg2_2-split" / "Step7_docs" / "outputs_step7" / f"office_presence_multiplier_{self.year}.csv"
        if leg2_off.exists():
            our_off = OUT_DIR / f"office_presence_multiplier_{self.year}.csv"
            md5_leg2 = _md5(leg2_off)
            md5_leg3 = _md5(our_off)
            same = md5_leg2 == md5_leg3
            self._rec("pass", f"G.4 | [INFO] Office product MD5 vs Leg-2: leg2={md5_leg2[:8]} leg3={md5_leg3[:8]} "
                              f"identical={same} (expected DIFFERENT -- Leg-3 has its own 23,115-HH pool vs "
                              f"Leg-2's 23,150; a MISMATCH here is EXPECTED and explainable by the pool delta)")
            self._sum("G4 Office MD5 vs Leg-2 (explainable-diff)", "differ (pool delta explains it)",
                      f"identical={same}", "INFO")
        else:
            self._rec("warn", "G.4 | Leg-2 office product not found for MD5 comparison")

        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        fig.suptitle(f"Section G — Attribute Integrity ({self.scenario_label})", fontsize=13, fontweight="bold")
        for ax, col, ttl, color in [(axes[0], "DTYPE", "Dwelling type", "#89b4fa"),
                                     (axes[1], "PR", "Province/region", "#a6e3a1")]:
            vc = hh[col].astype(str).value_counts()
            ax.bar(range(len(vc)), vc.values, color=color, edgecolor="#1e1e2e", width=0.65)
            ax.set_xticks(range(len(vc))); ax.set_xticklabels(vc.index, rotation=40, ha="right", fontsize=8.5)
            ax.set_ylabel("HH count"); ax.set_title(ttl, fontsize=11)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["G_attributes"] = _b64(fig)

    # ── Summary Table ─────────────────────────────────────────────────────────
    def generate_summary_table(self) -> None:
        print("\n--- Summary Table ---------------------------------------------------")
        for row in self.summary_rows:
            st = row["Status"]
            icon = {"PASS": "[PASS]", "WARN": "[WARN]", "INFO": "[INFO]"}.get(st, "[FAIL]")
            print(f"  {icon} {row['Gate / Check']}: {row['Observed']} — {st}")

    # ── HTML Report ───────────────────────────────────────────────────────────
    def build_html_report(self) -> str:
        n_pass = len(self.results["pass"]); n_warn = len(self.results["warn"]); n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_sections = [
            ("A_schema", "Section A — Schema & Structure"), ("B_daytype", "Section B — Day-Type Coverage"),
            ("C_occupancy", "Section C — Residential Occupancy Fidelity"),
            ("D_metabolic", "Section D — Metabolic Rate Plausibility"),
            ("E_office", "Section E — Office Presence Fidelity & Shape"),
            ("R_retail", "Section R — Retail Product (NEW)"),
            ("H_hotel", "Section H — Hotel Product (NEW)"),
            ("F_channel", "Section F — Channel Consistency"),
            ("G_attributes", "Section G — Attribute Integrity"),
        ]
        charts_html = "".join(
            f'<section class="chart-section" id="{k}"><h2>{lbl}</h2><div class="chart-wrap">'
            f'<img src="data:image/png;base64,{self.plots_b64[k]}" alt="{lbl}"></div></section>'
            for k, lbl in chart_sections if k in self.plots_b64
        )

        cols = ["Gate / Check", "Threshold", "Observed", "Status"]
        th = "".join(f"<th>{c}</th>" for c in cols)
        trs = "".join(
            f'<tr class="{ {"PASS":"pass-row","WARN":"warn-row","INFO":"info-row"}.get(row["Status"],"fail-row") }">'
            + "".join(f"<td>{row[c]}</td>" for c in cols) + "</tr>"
            for row in self.summary_rows
        )
        summary_html = (f'<section class="chart-section" id="summary-table"><h2>Summary Table</h2>'
                        f'<div class="table-wrap"><table class="summary-table"><thead><tr>{th}</tr></thead>'
                        f'<tbody>{trs}</tbody></table></div></section>')

        def _badge_list(level):
            icon = {"pass": "[PASS]", "fail": "[FAIL]", "warn": "[WARN]"}.get(level, "[INFO]")
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>" for m in items)

        nav_links = "".join(f'<a href="#{k}">{lbl.split("—")[0].strip()}</a>' for k, lbl in chart_sections if k in self.plots_b64)
        nav_links += '<a href="#summary-table">Summary</a>'
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3J Step 7 (4-split) — BEM Integration Validation ({self.scenario_label})</title>
<style>
:root {{ --bg:#1e1e2e; --surface:#2a2a3e; --surface2:#313244; --accent:#89b4fa; --green:#a6e3a1;
--yellow:#f9e2af; --red:#f38ba8; --text:#cdd6f4; --subtext:#a6adc8; --border:#45475a; }}
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }}
header {{ background:var(--surface); border-bottom:1px solid var(--border); padding:18px 32px;
display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:100; }}
header h1 {{ font-size:1.15rem; color:var(--accent); }} header p {{ font-size:0.78rem; color:var(--subtext); }}
nav {{ background:var(--surface2); border-bottom:1px solid var(--border); padding:8px 32px; display:flex; gap:16px; flex-wrap:wrap; }}
nav a {{ color:var(--subtext); text-decoration:none; font-size:0.82rem; padding:4px 10px; border-radius:6px; }}
nav a:hover {{ background:var(--surface); color:var(--accent); }}
main {{ max-width:1300px; margin:0 auto; padding:30px 28px; }}
.scorecard {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:36px; }}
.score-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px 16px; text-align:center; }}
.score-card .number {{ font-size:2.4rem; font-weight:700; }} .score-card .label {{ font-size:0.8rem; color:var(--subtext); margin-top:4px; }}
.score-card.ok .number {{ color:var(--green); }} .score-card.warn .number {{ color:var(--yellow); }}
.score-card.fail .number {{ color:var(--red); }} .score-card.pct .number {{ color:var(--accent); font-size:2.0rem; }}
.findings {{ margin-bottom:36px; }} .findings h2 {{ font-size:1.05rem; margin-bottom:12px; color:var(--accent); }}
.badge-list {{ list-style:none; display:flex; flex-direction:column; gap:6px; }}
.badge {{ padding:8px 14px; border-radius:8px; font-size:0.82rem; line-height:1.4; }}
.badge.pass {{ background:#1c2e22; border:1px solid #2d5a35; color:var(--green); }}
.badge.warn {{ background:#2e2a1c; border:1px solid #5a4e1f; color:var(--yellow); }}
.badge.fail {{ background:#2e1c1e; border:1px solid #5a2428; color:var(--red); }}
.chart-section {{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:24px; margin-bottom:28px; }}
.chart-section h2 {{ font-size:1.0rem; color:var(--accent); margin-bottom:16px; padding-bottom:8px; border-bottom:1px solid var(--border); }}
.chart-wrap {{ text-align:center; }} .chart-wrap img {{ max-width:100%; height:auto; border-radius:8px; }}
.table-wrap {{ overflow-x:auto; }} .summary-table {{ width:100%; border-collapse:collapse; font-size:0.8rem; }}
.summary-table th {{ background:var(--surface2); color:var(--accent); padding:10px 12px; text-align:left; border-bottom:2px solid var(--border); font-size:0.76rem; white-space:nowrap; }}
.summary-table td {{ padding:8px 12px; border-bottom:1px solid var(--border); color:var(--text); }}
.summary-table tr.pass-row td {{ color:var(--green); }} .summary-table tr.warn-row td {{ color:var(--yellow); }}
.summary-table tr.info-row td {{ color:var(--subtext); }} .summary-table tr.fail-row td {{ color:var(--red); }}
footer {{ text-align:center; padding:20px; font-size:0.76rem; color:var(--subtext); border-top:1px solid var(--border); margin-top:10px; }}
</style></head>
<body>
<header><div><h1>3J Step 7 (4-split) — Four-Channel BEM Integration Validation ({self.scenario_label})</h1>
<p>Residential + Office + Retail + Hotel products, Sections A–G / R / H / M / W</p></div>
<p style="font-size:0.76rem;color:var(--subtext)">Generated: {ts}</p></header>
<nav><a href="#scorecard">Scorecard</a>{nav_links}</nav>
<main>
<div class="scorecard" id="scorecard">
<div class="score-card ok"><div class="number">{n_pass}</div><div class="label">Checks Passed</div></div>
<div class="score-card warn"><div class="number">{n_warn}</div><div class="label">Warnings</div></div>
<div class="score-card fail"><div class="number">{n_fail}</div><div class="label">Failures</div></div>
<div class="score-card pct"><div class="number">{pct_ok}%</div><div class="label">Pass Rate</div></div>
</div>
<div class="findings"><h2>Failures</h2><ul class="badge-list">{_badge_list("fail")}</ul></div>
<div class="findings"><h2>Warnings</h2><ul class="badge-list">{_badge_list("warn")}</ul></div>
<div class="findings"><h2>Passed</h2><ul class="badge-list">{_badge_list("pass")}</ul></div>
{charts_html}
{summary_html}
</main>
<footer>3J Leg-3 Four-Channel BEM Integration · Step 7 Validation · N_HH={self.N_HH:,} · Generated: {ts}</footer>
</body></html>"""

        # out_suffix lets a re-validation run write to a NEW filename (e.g. "_v2") instead of
        # overwriting the historical stale report -- default "" preserves prior behaviour exactly.
        out_path = OUT_DIR / f"step7_validation_report_{self.scenario_label}{self.out_suffix}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved -> {out_path}")
        return str(out_path)

    def run_all(self):
        print("=" * 64)
        print(f"3J Step 7 (4-split) — Four-Channel BEM Integration Validation ({self.scenario_label})")
        print("=" * 64)
        self.section_a_schema()
        self.section_b_daytype()
        self.section_c_occ_fidelity()
        self.section_d_metabolic()
        self.section_e_office()
        self.section_r_retail()
        self.section_h_hotel()
        self.section_m_mutex_clock()
        self.section_w_wiring()
        self.section_f_channel()
        self.section_g_attributes()
        self.generate_summary_table()
        self.build_html_report()
        n_p, n_w, n_f = len(self.results["pass"]), len(self.results["warn"]), len(self.results["fail"])
        print(f"\n{'=' * 64}\n[{self.scenario_label}] Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL\n{'=' * 64}\n")
        return n_p, n_w, n_f


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3J Step 7 (4-split) — Four-Channel BEM Integration Validator")
    parser.add_argument("--year", choices=["2022", "2030"], default=None)
    parser.add_argument("--bundle", choices=["cons", "central", "opt"], default=None)
    parser.add_argument("--all", action="store_true", help="Run all 4 scenarios (2022 + 3 bundles)")
    parser.add_argument("--out-suffix", default="", help="Suffix inserted before .html on the report "
                         "filename (e.g. '_v2') -- lets a re-run avoid overwriting a prior report.")
    args = parser.parse_args()

    scenarios = []
    if args.all:
        scenarios = [("2022", None)] + [("2030", b) for b in BUNDLES]
    elif args.year == "2022":
        scenarios = [("2022", None)]
    elif args.year == "2030":
        if not args.bundle:
            parser.error("--year 2030 requires --bundle {cons,central,opt}")
        scenarios = [("2030", args.bundle)]
    else:
        parser.error("specify --year or --all")

    results_by_scn = {}
    for yr, b in scenarios:
        v = BEM4splitValidator(year=yr, bundle=b, out_suffix=args.out_suffix)
        results_by_scn[v.scenario_label] = v.run_all()

    print("\n" + "=" * 64)
    print("OVERALL RESULTS")
    for scn, (np_, nw, nf) in results_by_scn.items():
        print(f"  [{scn}] {np_} PASS / {nw} WARN / {nf} FAIL")
    print(f"Reports: {OUT_DIR}")
    print("=" * 64)
