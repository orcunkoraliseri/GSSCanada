"""
3rdJ_05_censusLinkage_4split_val.py — Step 5 Validation: 3J Leg-3 Four-Channel Census-GSS Linkage.

Forked from 3rdJ_05_censusLinkage_2split_val.py (Leg-2). Sections 1,2,4,5,6 (and
Section 3 AT_WORK W1-W4) are ported VERBATIM. Adds (Delta E, per
3rdJ_05_censusLinkage_4split_val.md):
  - Section 0 (NEW) — join-key connectivity audit (the Leg-2 PR-remap lesson)
  - Section 3r (NEW) — AT_RETAIL consistency (R1-R4)

Class renamed CensusLinkageValidator4CH. Generates an HTML report to
outputs_step5/3rdJ_step5_validation_report.html with residential + AT_WORK +
AT_RETAIL sections.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util as _ilu
import io
import os
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

# ── Paths ─────────────────────────────────────────────────────────────────────
# parents[0] = Step5_docs/
# parents[1] = Leg3_4-split/
# parents[2] = 3J_docs_occ_nTemp/
# parents[3] = GSSCanada-main/
BASE = Path(__file__).resolve().parents[3]

CENSUS_FILE   = BASE / "0_Occupancy" / "Outputs_Aligned" / "Aligned_Census_2025.csv"
OUT_DIR       = BASE / "3J_docs_occ_nTemp" / "Leg3_4-split" / "Step5_docs" / "outputs_step5"
SMOKE_DIR     = OUT_DIR / "smoke"
ARCHETYPE_LUT = BASE / "0_Occupancy" / "processed" / "office_archetype_lookup.csv"

# The Leg-3 LOCKED pool (with ret30_*) — needed by Section 0 (connectivity audit)
# and Section 3r (R1/R2 matched-vs-pool retail comparison). MUST be the exact same
# file the main script uses for --smoke/--full; assigned from _main_mod below (single
# source of truth) — do NOT hand-code a second copy of the pool path here (a stale
# hand-coded copy pointing at the pre-W3-fix pool was the 2026-07-21 staleness bug).

# ── Reuse the main script's match-key lists + PR remap (Delta D principle: one
# source of truth, never a second hand-coded copy of the remap) ───────────────
_MAIN_SCRIPT_PATH = Path(__file__).resolve().parent / "3rdJ_05_censusLinkage_4split.py"
_spec = _ilu.spec_from_file_location("_censusLinkage4split_main", _MAIN_SCRIPT_PATH)
_main_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_main_mod)

MATCH_KEYS          = _main_mod.MATCH_KEYS
DDAY_COL_MAIN        = _main_mod.DDAY_COL
_T1_KEYS             = _main_mod._T1_KEYS
_T2_KEYS             = _main_mod._T2_KEYS
_PROVINCE_TO_REGION  = _main_mod._PROVINCE_TO_REGION
harmonize_cma        = _main_mod.harmonize_cma
harmonize_lftag_census = _main_mod.harmonize_lftag_census

# Pool path: single source of truth — the exact file the main script links against
# (currently the W3-fixed seed_3_g3fix_raked3_mindwell_actv pool). See note above.
POOL_FILE            = _main_mod.FULL_POOL

# ── Constants ──────────────────────────────────────────────────────────────────

ACT_LABELS: dict[int, str] = {
    1: "Work", 2: "HH Work", 3: "Caregiving", 4: "Purchasing",
    5: "Sleep & Rest", 6: "Eating", 7: "Personal Care", 8: "Education",
    9: "Socializing", 10: "Passive Leisure", 11: "Active Leisure",
    12: "Community", 13: "Travel", 14: "Misc",
}

# Unrotated 04:00-origin diary: slots 1-8 = 04:00-08:00 (morning rush),
# slots 41-48 = 00:00-04:00 (true overnight / sleep window).
NIGHT_SLOTS = slice(-8, None)  # slots 41-48 = 00:00-04:00 (unrotated 04:00-origin 48x30min diary)

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


def _apply_dark() -> None:
    plt.rcParams.update(_DARK)


def _b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ── Validator ──────────────────────────────────────────────────────────────────

class CensusLinkageValidator4CH:
    """
    Validates 3J Leg-3 4-channel Step 5 outputs.
    Residential gates: match tier, AT_HOME consistency, schedule shape,
      HH aggregation, BEM format, regression. (Sections 1,2,4,5,6 — verbatim Leg-2)
    AT_WORK gates: per-slot rate, LFTAG sanity, colleagues, archetype distribution.
      (Section 3 W1-W4 — verbatim Leg-2)
    Section 0 (NEW): join-key connectivity audit (census domain ⊆ pool domain;
      Tier-1/Tier-2 pool reachability) — the Leg-2 PR-remap lesson.
    Section 3r (NEW): AT_RETAIL consistency (R1-R4) — ret30 is per-person,
      never HH-maxed; v1 has no retail_archetype (single "Retail Retail").
    """

    ACT_COLS     = [f"act30_{i:03d}"     for i in range(1, 49)]
    HOM_COLS     = [f"hom30_{i:03d}"     for i in range(1, 49)]
    WRK_COLS     = [f"wrk30_{i:03d}"     for i in range(1, 49)]
    RET_COLS     = [f"ret30_{i:03d}"     for i in range(1, 49)]
    SPOUSE_COLS  = [f"Spouse30_{i:03d}"  for i in range(1, 49)]
    COL_COLS     = [f"colleagues30_{i:03d}" for i in range(1, 49)]
    HH_HOM_COLS  = [f"HH_hom30_{i:03d}" for i in range(1, 49)]

    def __init__(
        self,
        aug_dir: str,
        census_path: str,
        outputs_dir: str,
        file_suffix: str = "",
        is_smoke: bool = False,
    ) -> None:
        self.aug_dir      = aug_dir
        self.census_path  = census_path
        self.outputs_dir  = outputs_dir
        self.file_suffix  = file_suffix
        self.is_smoke     = is_smoke
        os.makedirs(outputs_dir, exist_ok=True)

        prefix = "3rdJ_25CEN_aug"
        suf    = file_suffix
        smoke_sfx = "_smoke" if is_smoke else ""

        _p = lambda f: os.path.join(aug_dir, f)

        print(f"Loading {prefix}_Matched_Keys{suf}{smoke_sfx}.csv ...")
        self.keys = pd.read_csv(
            _p(f"{prefix}_Matched_Keys{suf}{smoke_sfx}.csv"),
            low_memory=False)
        print(f"  -> {len(self.keys):,} rows")

        print(f"Loading {prefix}_Full_Schedules{suf}{smoke_sfx}.csv ...")
        _sw = ({"PID", "IS_SYNTHETIC", "DTYPE", "SIM_HH_ID", "DDAY_STRATA",
                "LFTAG", "NOCS", "office_archetype_ID", "CYCLE_YEAR"}
               | set(self.ACT_COLS) | set(self.HOM_COLS)
               | set(self.WRK_COLS) | set(self.RET_COLS)
               | set(self.SPOUSE_COLS) | set(self.COL_COLS))
        self.sched = pd.read_csv(
            _p(f"{prefix}_Full_Schedules{suf}{smoke_sfx}.csv"),
            usecols=lambda c: c in _sw, low_memory=False)
        if "DDAY_STRATA" not in self.sched.columns and "PID" in self.sched.columns:
            self.sched = self.sched.merge(
                self.keys[["PID", "DDAY_STRATA"]], on="PID", how="left")
        print(f"  -> {len(self.sched):,} rows x {self.sched.shape[1]} cols")
        self.keys = self.keys[self.keys["PID"].isin(self.sched["PID"])].copy()

        # Aggregated + BEM only for non-smoke runs
        self.agg = None
        self.bem = None
        if not is_smoke:
            print(f"Loading {prefix}_Full_Aggregated{suf}.csv ...")
            _aw = ({"PID", "SIM_HH_ID", "N_HH_MEMBERS", "HHSIZE"}
                   | set(self.HH_HOM_COLS) | set(self.RET_COLS))
            self.agg = pd.read_csv(
                _p(f"{prefix}_Full_Aggregated{suf}.csv"),
                usecols=lambda c: c in _aw, low_memory=False)
            print(f"  -> {len(self.agg):,} rows")

            print(f"Loading {prefix}_BEM_Schedules{suf}.csv ...")
            _bw = ({"PID", "DTYPE", "BEDRM", "ROOM", "CONDO", "REPAIR",
                    "office_archetype_ID"}
                   | set(self.ACT_COLS) | set(self.HOM_COLS) | set(self.WRK_COLS)
                   | set(self.RET_COLS))
            self.bem = pd.read_csv(
                _p(f"{prefix}_BEM_Schedules{suf}.csv"),
                usecols=lambda c: c in _bw, low_memory=False)
            print(f"  -> {len(self.bem):,} rows")

        print(f"Loading Census {os.path.basename(census_path)} ...")
        self.census = pd.read_csv(census_path, low_memory=False)
        self.n_census = len(self.census.drop_duplicates(subset="PID"))
        print(f"  -> {self.n_census:,} unique PIDs")

        # Expected row count: dynamic from deduped Census
        self.expected_rows = self.n_census
        if file_suffix == "_excl" and not is_smoke:
            _excl = os.path.join(aug_dir, "3rdJ_25CEN_aug_excluded_pids.csv")
            if os.path.exists(_excl):
                n_excl = sum(1 for _ in open(_excl, encoding="utf-8")) - 1
                self.expected_rows = self.n_census - n_excl
                print(f"  [--excl] expected={self.n_census:,} - {n_excl:,} = {self.expected_rows:,}")

        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        self.summary_rows: list[dict] = []
        self.section0_rows: list[dict] = []

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = "[PASS]" if level == "pass" else ("[FAIL]" if level == "fail" else "[WARN]")
        print(f"  {icon} {msg}")

    # ── Section 0 (NEW, Leg-3) — Join-Key Connectivity Audit ───────────────────
    # The load-bearing checkpoint: catches the Leg-2-class silent PR-remap
    # truncation of the matchable pool before it hides inside healthy-looking
    # tier rates. Runs independently of the main script's own Delta-D audit
    # (belt-and-suspenders — the validator re-derives from the artifacts, not
    # from the pipeline's own log claims).

    def validate_join_key_connectivity(self) -> dict:
        print("\n--- Section 0 (NEW): Join-Key Connectivity Audit ---")
        _apply_dark()

        # Per-agent census-side key table: 7 census-native keys + DDAY_STRATA
        # (DDAY_STRATA is assigned during matching, not present in raw Census,
        # so it comes from the Matched_Keys file, joined on PID).
        cen_native = [k for k in MATCH_KEYS if k in self.census.columns]
        cen_base = self.census[["PID"] + cen_native].drop_duplicates(subset="PID")
        # CMA harmonization (census side) — reuses the main script's harmonize_cma
        # (one source of truth, no second hand-coded copy), mirrors the PR-remap
        # pattern below. Remaps raw StatCan CMA/CA code -> binary metro(1)/non-metro(2).
        cen_base = harmonize_cma(cen_base, side="census")
        # LFTAG not-stated harmonization (99 -> NaN) — same one-source-of-truth
        # helper the main script applies; closes the Section-0 LFTAG overlap FAIL
        # (census literal-99 sentinel the pool codes as NaN), no matching change.
        cen_base = harmonize_lftag_census(cen_base)
        if "DDAY_STRATA" in self.keys.columns:
            keys_dday = self.keys[["PID", "DDAY_STRATA"]].drop_duplicates(subset="PID")
            cen_full = cen_base.merge(keys_dday, on="PID", how="inner")
        else:
            cen_full = cen_base
            self._rec("warn", "0.0 | DDAY_STRATA not found in Matched_Keys — Section 0 "
                               "DDAY check skipped")

        # Pool match-key columns, PR-remapped exactly as the matcher does
        # (reusing _PROVINCE_TO_REGION imported from the main script — no
        # second hand-coded copy of the remap).
        pool_usecols = set(_T1_KEYS)
        try:
            df_pool_keys = pd.read_csv(
                POOL_FILE, usecols=lambda c: c in pool_usecols, low_memory=False)
        except FileNotFoundError:
            self._rec("fail", f"0.1 | Pool file not found: {POOL_FILE} — cannot audit connectivity")
            return {}

        if "PR" in df_pool_keys.columns:
            remapped = df_pool_keys["PR"].map(_PROVINCE_TO_REGION)
            unmapped = df_pool_keys.loc[remapped.isna(), "PR"].unique().tolist()
            if unmapped:
                self._rec("fail", f"0.1 | Unmapped pool PR values (remap incomplete): {unmapped}")
            df_pool_keys["PR"] = remapped

        # CMA harmonization (pool side) — reuses the main script's harmonize_cma.
        # Pool CMA is LUC_RST-coded {1,2,3}; harmonize_cma raises on any value
        # outside that domain (real data corruption, not an edge case) — caught
        # here and recorded as a validator FAIL rather than crashing the report.
        try:
            df_pool_keys = harmonize_cma(df_pool_keys, side="pool")
        except ValueError as e:
            self._rec("fail", f"0.1 | {e}")
            return {}

        any_fail = False
        for k in _T1_KEYS:
            if k not in cen_full.columns or k not in df_pool_keys.columns:
                self._rec("warn", f"0.1 | key {k} missing from census or pool — skip")
                continue
            cen_dom = set(cen_full[k].dropna().unique().tolist())
            pool_dom = set(df_pool_keys[k].dropna().unique().tolist())
            missing = cen_dom - pool_dom
            subset_ok = len(missing) == 0
            overlap_pct = 100.0 * len(cen_dom & pool_dom) / len(cen_dom) if cen_dom else 100.0
            if not subset_ok:
                any_fail = True
            lvl = "pass" if subset_ok else "fail"
            self._rec(lvl, f"0.1 | {k}: census⊆pool={'YES' if subset_ok else 'NO'} "
                           f"(overlap={overlap_pct:.1f}%, census_n={len(cen_dom)}, pool_n={len(pool_dom)})"
                           + ("" if subset_ok else f"  missing={sorted(missing, key=str)[:10]}"))
            self.section0_rows.append({
                "Key": k, "Census domain n": len(cen_dom), "Pool domain n": len(pool_dom),
                "Overlap %": f"{overlap_pct:.1f}%",
                "census⊆pool": "YES" if subset_ok else "NO",
                "Status": "PASS" if subset_ok else "FAIL",
            })

        # 0.2: Tier-1 / Tier-2 pool reachability
        t1_cols = [c for c in _T1_KEYS if c in cen_full.columns and c in df_pool_keys.columns]
        t2_cols = [c for c in _T2_KEYS if c in cen_full.columns and c in df_pool_keys.columns]
        t1_share = t2_share = float("nan")
        if t1_cols:
            cen_t1 = cen_full[t1_cols].dropna().drop_duplicates().assign(_hit1=1)
            pool_t1_valid = df_pool_keys.dropna(subset=t1_cols)
            m1 = pool_t1_valid[t1_cols].merge(cen_t1, on=t1_cols, how="left")
            t1_share = 100.0 * m1["_hit1"].notna().sum() / len(df_pool_keys) if len(df_pool_keys) else 0.0
        if t2_cols:
            cen_t2 = cen_full[t2_cols].dropna().drop_duplicates().assign(_hit2=1)
            pool_t2_valid = df_pool_keys.dropna(subset=t2_cols)
            m2 = pool_t2_valid[t2_cols].merge(cen_t2, on=t2_cols, how="left")
            t2_share = 100.0 * m2["_hit2"].notna().sum() / len(df_pool_keys) if len(df_pool_keys) else 0.0

        lvl1 = "pass" if t1_share >= 95 else "warn"
        lvl2 = "pass" if t2_share >= 95 else "warn"
        self._rec(lvl1, f"0.2 | Tier-1 (8-key) pool reachable share: {t1_share:.2f}% (>=95% gate)")
        self._rec(lvl2, f"0.2 | Tier-2 (5-key) pool reachable share: {t2_share:.2f}% (>=95% gate)")
        self.section0_rows.append({
            "Key": "Tier-1 reachable", "Census domain n": "-", "Pool domain n": "-",
            "Overlap %": f"{t1_share:.2f}%", "census⊆pool": "-",
            "Status": "PASS" if t1_share >= 95 else "WARN",
        })
        self.section0_rows.append({
            "Key": "Tier-2 reachable", "Census domain n": "-", "Pool domain n": "-",
            "Overlap %": f"{t2_share:.2f}%", "census⊆pool": "-",
            "Status": "PASS" if t2_share >= 95 else "WARN",
        })

        if any_fail:
            print("  [Section 0] *** At least one key has <100% census⊆pool overlap — "
                  "this is the Leg-2 PR-remap bug class ***")

        return {"rows": self.section0_rows, "t1_share": t1_share, "t2_share": t2_share}

    # ── Section 1 — Match Tier Distribution ────────────────────────────────────

    def validate_match_tier_distribution(self) -> dict:
        print("\n--- Section 1: Match Tier Distribution ---")
        _apply_dark()
        k = self.keys
        n = len(k)

        ok11 = n == self.expected_rows
        self._rec("pass" if ok11 else ("warn" if self.is_smoke else "fail"),
                  f"1.1 | Row count: {n:,} (expected {self.expected_rows:,})"
                  + (" [smoke: subset expected]" if self.is_smoke else ""))
        self.summary_rows.append({
            "Gate / Check": "Row count",
            "Threshold": f"== {self.expected_rows:,}",
            "Observed": f"{n:,}",
            "Status": "PASS" if ok11 else ("WARN" if self.is_smoke else "FAIL"),
        })

        wd = k[k["DDAY_STRATA"] == 1]
        wd_rate = (wd["MATCH_TIER"] == "4_FailSafe").sum() / len(wd) * 100 if len(wd) > 0 else 0.0
        lv = "pass" if wd_rate <= 10 else ("warn" if wd_rate <= (40 if self.is_smoke else 12) else "fail")
        self._rec(lv, f"1.2 | WD FailSafe rate: {wd_rate:.2f}%"
                  + (" [smoke: high rate expected]" if self.is_smoke else " (<=10% gate)"))

        we = k[k["DDAY_STRATA"].isin([2, 3])]
        we_rate = (we["MATCH_TIER"] == "4_FailSafe").sum() / len(we) * 100 if len(we) > 0 else 0.0
        lv2 = "pass" if we_rate <= 12 else ("warn" if self.is_smoke else "fail")
        self._rec(lv2, f"1.3 | WE FailSafe rate: {we_rate:.2f}%"
                  + (" [smoke: high rate expected]" if self.is_smoke else " (<=12% gate)"))

        t12_rate = k["MATCH_TIER"].isin(["1_Perfect", "2_Core"]).sum() / n * 100 if n > 0 else 0.0
        lv3 = "pass" if t12_rate >= 60 else ("warn" if self.is_smoke else "fail")
        self._rec(lv3, f"1.4 | Tier1+2 proportion: {t12_rate:.2f}%"
                  + (" [smoke: low expected]" if self.is_smoke else " (>=60% gate)"))

        dupes = k["PID"].duplicated().sum()
        self._rec("pass" if dupes == 0 else "fail", f"1.5 | Duplicate PIDs: {dupes}")

        null_occ = k["occID"].isna().sum() if "occID" in k.columns else -1
        self._rec("pass" if null_occ == 0 else "fail", f"1.6 | Null occIDs: {null_occ}")

        tier_order  = ["1_Perfect", "2_Core", "3_Constraints", "4_FailSafe"]
        tier_colors = ["#a6e3a1", "#89b4fa", "#f9e2af", "#f38ba8"]
        wd_c = {t: (wd["MATCH_TIER"] == t).sum() for t in tier_order}
        we_c = {t: (we["MATCH_TIER"] == t).sum() for t in tier_order}

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.array([0, 1])
        bottoms = np.zeros(2)
        for tier, col in zip(tier_order, tier_colors):
            vals = np.array([wd_c[tier], we_c[tier]], dtype=float)
            ax.bar(x, vals, 0.5, bottom=bottoms, label=tier,
                   color=col, edgecolor="#1e1e2e", linewidth=0.8)
            bottoms += vals
        ax.set_xticks(x)
        ax.set_xticklabels(["Weekday (DDAY=1)", "Weekend (DDAY=2,3)"])
        ax.set_ylabel("Count")
        ax.set_title("Section 1 — Match Tier Distribution: WD vs WE", fontsize=12)
        ax.legend(title="Match Tier", fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["1_tier_distribution"] = _b64(fig)

        return {"n": n, "wd_rate": wd_rate, "we_rate": we_rate}

    # ── Section 2 — AT_HOME Consistency ────────────────────────────────────────

    def validate_at_home_consistency(self) -> dict:
        print("\n--- Section 2: AT_HOME Consistency ---")
        _apply_dark()
        df = self.sched
        hom_p = [c for c in self.HOM_COLS if c in df.columns]
        if not hom_p:
            self._rec("fail", "2.x | hom30 cols missing")
            return {}

        obs = df[df["IS_SYNTHETIC"] == 0] if "IS_SYNTHETIC" in df.columns else df
        base_means = obs[hom_p].mean(axis=0).values * 100
        aug_means  = df[hom_p].mean(axis=0).values * 100

        aug_overall = aug_means.mean()
        base_overall = base_means.mean()
        diff21 = abs(aug_overall - base_overall)
        self._rec("pass" if diff21 <= 5 else ("warn" if self.is_smoke else "fail"),
                  f"2.1 | Overall mean AT_HOME: aug={aug_overall:.2f}% base={base_overall:.2f}% diff={diff21:.2f}pp")

        # 2.2 Raw IS_SYNTHETIC split printed as INFO only; verdict is within-day-type.
        # IS_SYNTHETIC proxies day-type composition (obs ~92.8% WD, syn ~44.6% WD) — comparing
        # IS_SYN=0 vs all conflates model error with weekday/weekend day-type artifact.
        slot_diffs_raw = aug_means - base_means
        max_diff_raw = np.abs(slot_diffs_raw).max()
        fail_slots_raw = int((np.abs(slot_diffs_raw) > 3).sum())
        print(f"  [2.2-INFO raw IS_SYNTHETIC split] aug vs obs(IS_SYN=0): "
              f"max_diff={max_diff_raw:.2f}pp, {fail_slots_raw} slot(s)>3pp "
              f"(day-type composition artifact — not PASS/FAIL basis)")

        # 2.2 PASS/FAIL: within-day-type comparison (DDAY==1 Weekday, DDAY∈{2,3} Weekend).
        has_dday_hom = "DDAY_STRATA" in df.columns and "IS_SYNTHETIC" in df.columns
        if has_dday_hom:
            diffs_22 = []
            for dday_grp, label22 in [([1], "WD"), ([2, 3], "WE")]:
                syn_g = df[(df["IS_SYNTHETIC"] == 1) & (df["DDAY_STRATA"].isin(dday_grp))]
                obs_g = df[(df["IS_SYNTHETIC"] == 0) & (df["DDAY_STRATA"].isin(dday_grp))]
                if len(syn_g) > 0 and len(obs_g) > 0:
                    d_g = np.abs(syn_g[hom_p].mean(axis=0).values - obs_g[hom_p].mean(axis=0).values) * 100
                    diffs_22.append(d_g)
                    print(f"  [2.2-{label22}] syn={len(syn_g)}, obs={len(obs_g)}, "
                          f"max_diff={d_g.max():.2f}pp, slots>3pp={int((d_g>3).sum())}")
            if diffs_22:
                combined_22 = np.concatenate(diffs_22)
                max_diff = float(combined_22.max())
                fail_slots = int((combined_22 > 3).sum())
            else:
                max_diff, fail_slots = float(max_diff_raw), fail_slots_raw
        else:
            max_diff, fail_slots = float(max_diff_raw), fail_slots_raw

        lv = "pass" if fail_slots == 0 else ("warn" if self.is_smoke else "fail")
        self._rec(lv, f"2.2 | Per-slot max diff (within-day-type): {max_diff:.2f}pp — {fail_slots} slot(s) >+-3pp"
                  + (" [smoke: may exceed]" if self.is_smoke else ""))
        self.summary_rows.append({
            "Gate / Check": "AT_HOME max slot deviation",
            "Threshold": "<= +-3 pp",
            "Observed": f"{max_diff:.2f} pp",
            "Status": "PASS" if fail_slots == 0 else ("WARN" if self.is_smoke else "FAIL"),
        })

        if "DDAY_STRATA" in df.columns:
            wd_m = df[df["DDAY_STRATA"] == 1][hom_p].mean().mean() * 100
            we_m = df[df["DDAY_STRATA"].isin([2, 3])][hom_p].mean().mean() * 100
            # In smoke mode small samples can flip WD/WE ordering → WARN not FAIL
            lv_23 = "pass" if wd_m < we_m else ("warn" if self.is_smoke else "fail")
            self._rec(lv_23, f"2.3 | WD AT_HOME={wd_m:.2f}% < WE AT_HOME={we_m:.2f}%"
                      + (" [smoke: small-sample; WD shift-workers may flip]" if self.is_smoke else ""))

        night_mean = df[hom_p[NIGHT_SLOTS]].mean().mean() * 100
        # Smoke sample may contain shift-worker diaries pulling down slots 5-8 → WARN
        lv_24 = "pass" if night_mean >= 85 else ("warn" if self.is_smoke else "fail")
        self._rec(lv_24, f"2.4 | Slots 41-48 (00:00-04:00) mean AT_HOME: {night_mean:.2f}% (>=85%)"
                  + (" [smoke: shift-workers in pool lower night AT_HOME]" if self.is_smoke else ""))
        self.summary_rows.append({
            "Gate / Check": "Night AT_HOME rate (slots 41-48, 00:00-04:00)",
            "Threshold": ">= 85%",
            "Observed": f"{night_mean:.2f}%",
            "Status": "PASS" if night_mean >= 85 else ("WARN" if self.is_smoke else "FAIL"),
        })

        fig, ax = plt.subplots(figsize=(14, 5))
        x = np.arange(1, 49)
        ax.plot(x, aug_means, color="#89b4fa", linewidth=2, label="Augmented")
        ax.plot(x, base_means, color="#a6e3a1", linewidth=2, linestyle="--",
                label="IS_SYNTHETIC=0 baseline")
        ax.fill_between(x, base_means - 3, base_means + 3,
                        alpha=0.15, color="#f9e2af", label="+-3 pp band")
        ax.axhline(85, color="#f38ba8", linestyle=":", linewidth=1, label="85% night threshold")
        ax.set_xlabel("30-min slot")
        ax.set_ylabel("Mean AT_HOME (%)")
        ax.set_title("Section 2 — AT_HOME 48-slot Overlay: Augmented vs Observed Baseline")
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["2_at_home_overlay"] = _b64(fig)

        return {"aug_overall": aug_overall, "max_diff": max_diff, "night_mean": night_mean}

    # ── Section 3 — AT_WORK Consistency (NEW) ──────────────────────────────────

    def validate_at_work_consistency(self) -> dict:
        print("\n--- Section 3 (NEW): AT_WORK Consistency ---")
        _apply_dark()
        df = self.sched
        wrk_p = [c for c in self.WRK_COLS if c in df.columns]
        col_p = [c for c in self.COL_COLS if c in df.columns]

        if not wrk_p:
            self._rec("fail", "W1.x | wrk30 cols missing from Full_Schedules")
            return {}

        obs = df[df["IS_SYNTHETIC"] == 0] if "IS_SYNTHETIC" in df.columns else df
        wrk_all = df[wrk_p].mean(axis=0).values * 100
        wrk_obs = obs[wrk_p].mean(axis=0).values * 100 if len(obs) > 0 else wrk_all

        # W1: per-slot mean AT_WORK — raw IS_SYNTHETIC split (diagnostic only; not the PASS/FAIL basis)
        # IS_SYNTHETIC proxies day-type composition: obs ~92.8% WD, syn ~44.6% WD → comparing
        # across IS_SYNTHETIC is comparing weekday-heavy vs weekend-heavy groups (day-type artifact).
        diff_wrk_raw = np.abs(wrk_all - wrk_obs)
        max_diff_wrk_raw = float(diff_wrk_raw.max()) if len(diff_wrk_raw) > 0 else float("nan")
        fail_wrk_raw = int((diff_wrk_raw > 3).sum()) if len(diff_wrk_raw) > 0 else 0
        print(f"  [W1-INFO raw IS_SYNTHETIC split] all vs obs(IS_SYN=0): "
              f"max_diff={max_diff_wrk_raw:.2f}pp, {fail_wrk_raw} slot(s)>3pp "
              f"(day-type composition artifact — not PASS/FAIL basis)")

        # W1 PASS/FAIL: within-day-type comparison (synthetic-weekday vs observed-weekday,
        # synthetic-weekend vs observed-weekend) — like-with-like, same correction as night-gate fix.
        # DDAY==1 = Weekday; DDAY∈{2,3} = Weekend.
        has_dday = "DDAY_STRATA" in df.columns and "IS_SYNTHETIC" in df.columns
        if has_dday:
            syn_wd  = df[(df["IS_SYNTHETIC"] == 1) & (df["DDAY_STRATA"] == 1)]
            obs_wd  = df[(df["IS_SYNTHETIC"] == 0) & (df["DDAY_STRATA"] == 1)]
            syn_we  = df[(df["IS_SYNTHETIC"] == 1) & (df["DDAY_STRATA"].isin([2, 3]))]
            obs_we  = df[(df["IS_SYNTHETIC"] == 0) & (df["DDAY_STRATA"].isin([2, 3]))]
            diffs_w1 = []
            if len(syn_wd) > 0 and len(obs_wd) > 0:
                d_wd = np.abs(syn_wd[wrk_p].mean(axis=0).values - obs_wd[wrk_p].mean(axis=0).values) * 100
                diffs_w1.append(d_wd)
                print(f"  [W1-WD] syn_wd={len(syn_wd)}, obs_wd={len(obs_wd)}, "
                      f"max_diff={d_wd.max():.2f}pp, slots>3pp={int((d_wd>3).sum())}")
            if len(syn_we) > 0 and len(obs_we) > 0:
                d_we = np.abs(syn_we[wrk_p].mean(axis=0).values - obs_we[wrk_p].mean(axis=0).values) * 100
                diffs_w1.append(d_we)
                print(f"  [W1-WE] syn_we={len(syn_we)}, obs_we={len(obs_we)}, "
                      f"max_diff={d_we.max():.2f}pp, slots>3pp={int((d_we>3).sum())}")
            if diffs_w1:
                combined = np.concatenate(diffs_w1)
                max_diff_wrk = float(combined.max())
                fail_wrk = int((combined > 3).sum())
            else:
                max_diff_wrk, fail_wrk = max_diff_wrk_raw, fail_wrk_raw
        else:
            max_diff_wrk, fail_wrk = max_diff_wrk_raw, fail_wrk_raw

        lv = "pass" if fail_wrk == 0 else ("warn" if self.is_smoke else "fail")
        self._rec(lv, f"W1 | AT_WORK per-slot max diff (within-day-type): {max_diff_wrk:.2f}pp — "
                  f"{fail_wrk} slot(s) >+-3pp" + (" [smoke: may exceed]" if self.is_smoke else ""))
        self.summary_rows.append({
            "Gate / Check": "AT_WORK max slot deviation",
            "Threshold": "<= +-3 pp",
            "Observed": f"{max_diff_wrk:.2f} pp",
            "Status": "PASS" if fail_wrk == 0 else ("WARN" if self.is_smoke else "FAIL"),
        })

        # W2: AT_WORK rate by LFTAG
        lftag_gate = False
        if "LFTAG" in df.columns:
            wrk_by_lftag = df.groupby("LFTAG")[wrk_p].mean().mean(axis=1) * 100
            employed_rate = float(wrk_by_lftag[wrk_by_lftag.index.isin([1, 2])].max()) \
                            if any(lf in wrk_by_lftag.index for lf in [1, 2]) else 0.0
            noninlf_vals  = wrk_by_lftag[~wrk_by_lftag.index.isin([1, 2])]
            noninlf_rate  = float(noninlf_vals.max()) if len(noninlf_vals) > 0 else 0.0
            lftag_gate = employed_rate > noninlf_rate
            self._rec("pass" if lftag_gate else "fail",
                      f"W2 | LFTAG AT_WORK: employed_max={employed_rate:.2f}% "
                      f"not-in-LF_max={noninlf_rate:.2f}% (employed >> not-in-LF)")
            for lf, rate in wrk_by_lftag.items():
                print(f"     LFTAG={lf}: {rate:.2f}%")
        else:
            self._rec("warn", "W2 | LFTAG column missing — skip AT_WORK sanity by LFTAG")

        # W3: colleagues co-presence
        # Raw IS_SYNTHETIC split printed as INFO only; verdict is within-day-type (same artifact
        # as W1: IS_SYNTHETIC proxies day-type composition, so raw diff conflates model vs calendar).
        col_gate = False
        max_col_diff = float("nan")
        if col_p and len(obs) > 0:
            col_all = float(df[col_p].mean().mean() * 100)
            col_obs = float(obs[col_p].mean().mean() * 100)
            raw_diff = abs(col_all - col_obs)
            print(f"  [W3-INFO raw IS_SYNTHETIC split] all={col_all:.2f}%  obs(IS_SYN=0)={col_obs:.2f}%  "
                  f"diff={raw_diff:.3f}pp (day-type composition artifact — not PASS/FAIL basis)")

            # W3 PASS/FAIL: within-day-type comparison (DDAY==1 Weekday, DDAY∈{2,3} Weekend).
            if "DDAY_STRATA" in df.columns and "IS_SYNTHETIC" in df.columns:
                diffs_w3 = []
                for dday_grp, label in [([1], "WD"), ([2, 3], "WE")]:
                    syn_g = df[(df["IS_SYNTHETIC"] == 1) & (df["DDAY_STRATA"].isin(dday_grp))]
                    obs_g = df[(df["IS_SYNTHETIC"] == 0) & (df["DDAY_STRATA"].isin(dday_grp))]
                    if len(syn_g) > 0 and len(obs_g) > 0:
                        # NaN in colleagues30 = not-applicable slot = 0 colleagues present.
                        # fillna(0) on both channels gives a consistent all-slot denominator
                        # (syn already has 0% NaN; fillna is a no-op there but makes symmetry explicit).
                        col_syn_g = float(syn_g[col_p].fillna(0).mean().mean() * 100)
                        col_obs_g = float(obs_g[col_p].fillna(0).mean().mean() * 100)
                        d = abs(col_syn_g - col_obs_g)
                        diffs_w3.append(d)
                        print(f"  [W3-{label}] syn={col_syn_g:.2f}%  obs={col_obs_g:.2f}%  diff={d:.3f}pp")
                max_col_diff = float(max(diffs_w3)) if diffs_w3 else raw_diff
            else:
                max_col_diff = raw_diff

            col_gate = max_col_diff <= 3.0
            lv2 = "pass" if col_gate else ("warn" if self.is_smoke else "fail")
            self._rec(lv2, f"W3 | Colleagues co-presence (within-day-type): "
                      f"max_diff={max_col_diff:.3f}pp (<=3pp)")
        else:
            self._rec("warn", "W3 | colleagues30 cols missing or no observed rows — skip")

        # W4: office archetype distribution
        arch_gate = False
        if "office_archetype_ID" in df.columns:
            arch_dist = df["office_archetype_ID"].value_counts(normalize=True) * 100
            nonoffice  = float(arch_dist.get("NonOffice",    0.0))
            unknown    = float(arch_dist.get("Unknown_NOCS", 0.0))
            arch_gate  = nonoffice < 60.0 and unknown < 10.0
            self._rec("pass" if arch_gate else "fail",
                      f"W4 | Archetype: NonOffice={nonoffice:.2f}% (<60%) "
                      f"Unknown_NOCS={unknown:.2f}% (<10%)")
            for a, pct in arch_dist.items():
                print(f"     {a}: {pct:.2f}%")
            self.summary_rows.append({
                "Gate / Check": "Office archetype distribution",
                "Threshold": "NonOffice<60%, Unknown<10%",
                "Observed": f"NonOffice={nonoffice:.1f}%, Unknown={unknown:.1f}%",
                "Status": "PASS" if arch_gate else "FAIL",
            })
        else:
            self._rec("warn", "W4 | office_archetype_ID not in Full_Schedules — skip")

        # Plot: AT_WORK diurnal
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        x = np.arange(1, 49)
        axes[0].plot(x, wrk_all, color="#f38ba8", linewidth=2, label="All agents")
        if len(obs) > 0:
            axes[0].plot(x, wrk_obs, color="#a6e3a1", linewidth=2, linestyle="--",
                         label="IS_SYNTHETIC=0")
            axes[0].fill_between(x, wrk_obs - 3, wrk_obs + 3,
                                 alpha=0.15, color="#f9e2af", label="+-3pp band")
        axes[0].set_title("Section 3 — AT_WORK 48-slot: All vs Observed")
        axes[0].set_xlabel("30-min slot")
        axes[0].set_ylabel("Mean AT_WORK (%)")
        axes[0].legend(fontsize=9)
        axes[0].yaxis.grid(True, linestyle="--", alpha=0.3)

        if "office_archetype_ID" in df.columns:
            arch_dist_abs = df["office_archetype_ID"].value_counts()
            axes[1].bar(range(len(arch_dist_abs)), arch_dist_abs.values,
                        tick_label=arch_dist_abs.index, color="#89b4fa",
                        edgecolor="#1e1e2e")
            axes[1].set_title("Office Archetype Distribution")
            axes[1].set_xlabel("Archetype")
            axes[1].set_ylabel("Count")
            axes[1].tick_params(axis='x', rotation=25)
            axes[1].yaxis.grid(True, linestyle="--", alpha=0.3)

        plt.tight_layout()
        self.plots_b64["3_at_work"] = _b64(fig)

        return {"max_diff_wrk": max_diff_wrk, "lftag_gate": lftag_gate,
                "col_gate": col_gate, "arch_gate": arch_gate}

    # ── Section 3r (NEW, Leg-3) — AT_RETAIL Consistency ────────────────────────
    # ret30 is a per-person population-fraction channel that mirrors wrk30 in
    # every respect: carried, never re-derived, never HH-maxed. v1 retail has
    # no respondent-level archetype (single "Retail Retail" population multiplier).

    def validate_at_retail_consistency(self) -> dict:
        print("\n--- Section 3r (NEW): AT_RETAIL Consistency ---")
        _apply_dark()
        df = self.sched
        ret_p = [c for c in self.RET_COLS if c in df.columns]

        if not ret_p:
            self._rec("fail", "R.x | ret30 cols missing from Full_Schedules")
            return {}

        # Load pool ret30 + CYCLE_YEAR + DDAY_STRATA for R1 (matched-output vs pool,
        # per cycle x stratum) and R2 (population-level retail sanity uses matched
        # frame only, no pool needed).
        pool_usecols = set(ret_p) | {"CYCLE_YEAR", "DDAY_STRATA"}
        df_pool = None
        try:
            df_pool = pd.read_csv(POOL_FILE, usecols=lambda c: c in pool_usecols, low_memory=False)
        except FileNotFoundError:
            self._rec("warn", f"R1 | Pool file not found: {POOL_FILE} — skip matched-vs-pool check")

        # ── R1: per-slot max deviation, matched-output vs pool, per (cycle x stratum)
        r1_max = float("nan")
        have_cyc = "CYCLE_YEAR" in df.columns and "DDAY_STRATA" in df.columns
        if df_pool is not None and have_cyc and "CYCLE_YEAR" in df_pool.columns \
           and "DDAY_STRATA" in df_pool.columns:
            diffs = []
            for (cyc, dday), grp_out in df.groupby(["CYCLE_YEAR", "DDAY_STRATA"]):
                grp_pool = df_pool[(df_pool["CYCLE_YEAR"] == cyc) & (df_pool["DDAY_STRATA"] == dday)]
                if len(grp_out) == 0 or len(grp_pool) == 0:
                    continue
                d = np.abs(grp_out[ret_p].mean().values - grp_pool[ret_p].mean().values) * 100
                diffs.append(float(d.max()))
                print(f"  [R1] cycle={cyc} dday={dday}: n_out={len(grp_out)} n_pool={len(grp_pool)} "
                      f"max_diff={d.max():.3f}pp")
            if diffs:
                r1_max = float(max(diffs))
                lvl = "pass" if r1_max <= 1.0 else ("warn" if r1_max <= 3.0 else "fail")
                self._rec(lvl, f"R1 | AT_RETAIL per-slot max deviation (matched vs pool, "
                               f"by cycle x stratum): {r1_max:.3f}pp (FAIL>3, WARN 1-3, expect <<1)")
            else:
                self._rec("warn", "R1 | No overlapping (cycle, stratum) groups to compare — skip"
                                   " (expected in smoke: tiny sample may not span all groups)")
        else:
            self._rec("warn", "R1 | CYCLE_YEAR/DDAY_STRATA unavailable in schedules or pool — skip")
        self.summary_rows.append({
            "Gate / Check": "R1 AT_RETAIL max slot deviation (matched vs pool)",
            "Threshold": "<= 3.0 pp (WARN 1-3)",
            "Observed": f"{r1_max:.3f} pp" if r1_max == r1_max else "N/A",
            "Status": "PASS" if r1_max == r1_max and r1_max <= 1.0
                      else ("WARN" if r1_max == r1_max and r1_max <= 3.0
                            else ("FAIL" if r1_max == r1_max else "WARN")),
        })

        # ── R2: population-level retail sanity on the matched frame ──────────────
        # Unrotated 04:00-origin 48x30min diary: slot 17-20 = 12:00-14:00 (weekday);
        # slots 41-48 (NIGHT_SLOTS) = 00:00-04:00, same window as Section 2.4/4.3.
        midday_slots = ret_p[16:20] if len(ret_p) >= 20 else []
        night_slots = ret_p[NIGHT_SLOTS] if ret_p else []
        wd_mask = (df["DDAY_STRATA"] == 1) if "DDAY_STRATA" in df.columns else pd.Series(True, index=df.index)

        midday_rate = float(df.loc[wd_mask, midday_slots].mean().mean()) if midday_slots else float("nan")
        night_rate = float(df[night_slots].mean().mean()) if night_slots else float("nan")

        r2a_ok = 0.06 <= midday_rate <= 0.10
        r2b_ok = 0.000 <= night_rate <= 0.003
        self._rec("pass" if r2a_ok else "warn",
                  f"R2a | Weekday 12:00-14:00 AT_RETAIL rate: {midday_rate:.4f} (band 0.06-0.10)"
                  + (" [smoke: small sample, wide variance expected]" if self.is_smoke else ""))
        self._rec("pass" if r2b_ok else "warn",
                  f"R2b | Night (00:00-04:00) AT_RETAIL rate: {night_rate:.4f} (band 0.000-0.003)"
                  + (" [smoke: small sample, wide variance expected]" if self.is_smoke else ""))
        self.summary_rows.append({
            "Gate / Check": "R2 AT_RETAIL population sanity (weekday 12-14h / night)",
            "Threshold": "0.06-0.10 / 0.000-0.003",
            "Observed": f"{midday_rate:.4f} / {night_rate:.4f}",
            "Status": "PASS" if (r2a_ok and r2b_ok) else "WARN",
        })

        # ── R3: aggregation semantics — ret30 never HH-maxed (exact match) ────────
        r3_diff = float("nan")
        if self.agg is None:
            self._rec("warn", "R3 | Aggregation not run yet (smoke mode or --aggregate not "
                               "called) — skip")
        else:
            ret_agg_p = [c for c in self.RET_COLS if c in self.agg.columns]
            if ret_p and ret_agg_p:
                mean_sched = float(df[ret_p].mean().mean())
                mean_agg = float(self.agg[ret_agg_p].mean().mean())
                r3_diff = abs(mean_sched - mean_agg)
                r3_ok = r3_diff < 1e-9
                self._rec("pass" if r3_ok else "fail",
                          f"R3 | ret30 per-person mean: Full_Schedules={mean_sched:.6f} "
                          f"Full_Aggregated={mean_agg:.6f} diff={r3_diff:.2e} (exact match required)")
            else:
                self._rec("fail", "R3 | ret30 cols missing from schedules or aggregate")

        # ── R4: no retail_archetype column (deferred-decision guard) ─────────────
        all_cols = (list(df.columns)
                    + (list(self.agg.columns) if self.agg is not None else [])
                    + (list(self.bem.columns) if self.bem is not None else []))
        has_retail_arch = any("retail_archetype" in c.lower() for c in all_cols)
        self._rec("warn" if has_retail_arch else "pass",
                  f"R4 | retail_archetype column present: {has_retail_arch} "
                  f"(should be absent in v1 — deferred decision guard)")

        # ── Plot: AT_RETAIL diurnal (mirrors Section 3's AT_WORK panel) ──────────
        ret_all = df[ret_p].mean(axis=0).values * 100
        fig, ax = plt.subplots(figsize=(14, 5))
        x = np.arange(1, 49)
        ax.plot(x, ret_all, color="#f9e2af", linewidth=2, label="Matched output (all agents)")
        if df_pool is not None:
            pool_ret_mean = df_pool[ret_p].mean(axis=0).values * 100
            ax.plot(x, pool_ret_mean, color="#89b4fa", linewidth=2, linestyle="--", label="Pool")
        ax.axvspan(17, 20, alpha=0.1, color="#a6e3a1", label="12:00-14:00 window")
        ax.set_title("Section 3r — AT_RETAIL 48-slot: Matched Output vs Pool")
        ax.set_xlabel("30-min slot")
        ax.set_ylabel("Mean AT_RETAIL (%)")
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["3r_at_retail"] = _b64(fig)

        return {"r1_max": r1_max, "midday_rate": midday_rate, "night_rate": night_rate,
                "r3_diff": r3_diff, "has_retail_arch": has_retail_arch}

    # ── Section 4 — Schedule Shape Plausibility ─────────────────────────────────

    def validate_schedule_shape(self) -> dict:
        print("\n--- Section 4: Schedule Shape Plausibility ---")
        _apply_dark()
        df = self.sched
        act_p    = [c for c in self.ACT_COLS    if c in df.columns]
        spouse_p = [c for c in self.SPOUSE_COLS if c in df.columns]

        if not act_p:
            self._rec("fail", "4.x | act30 cols missing")
            return {}

        obs = df[df["IS_SYNTHETIC"] == 0] if "IS_SYNTHETIC" in df.columns else df

        # 4.1 OOR values
        af = df[act_p].values.flatten().astype(float)
        af = af[~np.isnan(af)].astype(int)
        oor = int(((af < 1) | (af > 14)).sum())
        self._rec("pass" if oor == 0 else "fail", f"4.1 | Out-of-range act30 values: {oor}")

        # 4.2 Top-5 activity share
        of = obs[act_p].values.flatten().astype(float)
        of = of[~np.isnan(of)].astype(int)
        aug_share = {a: float((af == a).mean() * 100) for a in range(1, 15)}
        obs_share = {a: float((of == a).mean() * 100) for a in range(1, 15)}
        top5 = sorted(obs_share, key=obs_share.get, reverse=True)[:5]
        max_diff = max(abs(aug_share[a] - obs_share[a]) for a in top5)
        fail5 = sum(1 for a in top5 if abs(aug_share[a] - obs_share[a]) > 5)
        lv = "pass" if fail5 == 0 else ("warn" if self.is_smoke else "fail")
        self._rec(lv, f"4.2 | Top-5 act share max diff: {max_diff:.2f}pp ({fail5} > +-5pp)")
        self.summary_rows.append({
            "Gate / Check": "Top-5 activity deviation",
            "Threshold": "<= +-5 pp",
            "Observed": f"{max_diff:.2f} pp",
            "Status": "PASS" if fail5 == 0 else ("WARN" if self.is_smoke else "FAIL"),
        })

        # 4.3 Night sleep dominance
        night_flat = df[act_p[NIGHT_SLOTS]].values.flatten().astype(float)
        night_flat = night_flat[~np.isnan(night_flat)].astype(int)
        sleep_rate = float((night_flat == 5).mean() * 100)
        # Smoke: small pool with shift-worker diaries reduces sleep dominance → WARN
        lv_43 = "pass" if sleep_rate >= 70 else ("warn" if self.is_smoke else "fail")
        self._rec(lv_43, f"4.3 | Night sleep dominance slots 41-48 (00:00-04:00): {sleep_rate:.2f}% (>=70%)"
                  + (" [smoke: shift-workers lower night sleep rate]" if self.is_smoke else ""))
        self.summary_rows.append({
            "Gate / Check": "Night sleep dominance (slots 41-48, 00:00-04:00)",
            "Threshold": ">= 70%",
            "Observed": f"{sleep_rate:.2f}%",
            "Status": "PASS" if sleep_rate >= 70 else ("WARN" if self.is_smoke else "FAIL"),
        })

        # Heatmap chart
        fig, axes = plt.subplots(1, 2, figsize=(18, 6),
                                 gridspec_kw={"width_ratios": [3, 1]})
        total = len(df)
        heat = np.zeros((14, len(act_p)))
        for i, a in enumerate(range(1, 15)):
            heat[i] = (df[act_p].values == a).sum(axis=0) / total * 100
        heat_norm = heat.copy()
        for i in range(14):
            rm = heat_norm[i].max()
            if rm > 0:
                heat_norm[i] /= rm

        ax = axes[0]
        im = ax.imshow(heat_norm, aspect="auto", cmap="plasma",
                       interpolation="nearest", vmin=0, vmax=1)
        plt.colorbar(im, ax=ax, fraction=0.015)
        ax.set_yticks(range(14))
        ax.set_yticklabels([ACT_LABELS[a] for a in range(1, 15)], fontsize=8.5)
        ax.set_title("Activity Heatmap 14x48 (augmented)", fontsize=11)
        ax.set_xlabel("30-min slot")

        ax2 = axes[1]
        y = np.arange(5)
        ax2.barh(y + 0.2, [aug_share[a] for a in top5], 0.35,
                 label="Augmented", color="#89b4fa", edgecolor="#1e1e2e")
        ax2.barh(y - 0.2, [obs_share[a] for a in top5], 0.35,
                 label="IS_SYN=0", color="#a6e3a1", edgecolor="#1e1e2e")
        ax2.set_yticks(y)
        ax2.set_yticklabels([ACT_LABELS[a] for a in top5], fontsize=9)
        ax2.set_xlabel("Time share (%)")
        ax2.set_title("Top-5 Activity Shares", fontsize=11)
        ax2.legend(fontsize=8)

        plt.suptitle("Section 4 — Schedule Shape Plausibility", fontsize=13, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["4_schedule_shape"] = _b64(fig)

        return {"oor": oor, "max_diff": max_diff, "sleep_rate": sleep_rate}

    # ── Section 5 — HH Aggregation (skipped in smoke) ─────────────────────────

    def validate_hh_aggregation(self) -> dict:
        print("\n--- Section 5: HH Aggregation Integrity ---")
        if self.agg is None:
            self._rec("warn", "5.x | Aggregation not run yet (smoke mode or --aggregate not called)")
            return {}
        _apply_dark()
        df = self.agg
        hh_hom_p = [c for c in self.HH_HOM_COLS if c in df.columns]

        null_hh = df["SIM_HH_ID"].isna().sum() if "SIM_HH_ID" in df.columns else -1
        self._rec("pass" if null_hh == 0 else "fail",
                  f"5.1 | Null SIM_HH_IDs: {null_hh}")

        mean_hhsize = float("nan")
        if "N_HH_MEMBERS" in df.columns:
            mean_hhsize = float(df["N_HH_MEMBERS"].mean())
            flag = abs(mean_hhsize - 2.80) > 0.5
            self._rec("warn" if flag else "pass",
                      f"5.2 | Mean N_HH_MEMBERS: {mean_hhsize:.3f} (Census ref ~2.80)")
        else:
            self._rec("warn", "5.2 | N_HH_MEMBERS not found")

        n = len(df)
        self._rec("pass" if n == self.expected_rows else "fail",
                  f"5.3 | Aggregated row count: {n:,} (expected {self.expected_rows:,})")

        # Verify wrk30 NOT aggregated to HH level (per-person only)
        hh_wrk_present = any(c.startswith("HH_wrk30_") for c in df.columns)
        self._rec("pass" if not hh_wrk_present else "fail",
                  f"5.4 | HH_wrk30 columns absent (wrk30 per-person only): "
                  f"{'PASS — no HH_wrk30 cols' if not hh_wrk_present else 'FAIL — HH_wrk30 cols found'}")

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("Section 5 — HH Aggregation", fontsize=13, fontweight="bold")
        if "N_HH_MEMBERS" in df.columns:
            cnt = df["N_HH_MEMBERS"].dropna().astype(int).value_counts().sort_index()
            axes[0].bar(cnt.index, cnt.values, color="#89b4fa", edgecolor="#1e1e2e", width=0.7)
            axes[0].set_title(f"HH Members (mean={mean_hhsize:.2f})")
        if hh_hom_p:
            hh_means = df[hh_hom_p].mean(axis=1)
            axes[1].boxplot(hh_means.dropna().values, patch_artist=True,
                            medianprops=dict(color="#1e1e2e", linewidth=2))
            axes[1].set_title("Per-HH Mean AT_HOME")
            axes[1].axhline(0.3, color="#f38ba8", linestyle="--", label="0.3 lower bound")
            axes[1].legend(fontsize=9)
        plt.tight_layout()
        self.plots_b64["5_hh_agg"] = _b64(fig)

        return {"n": n, "null_hh": null_hh, "mean_hhsize": mean_hhsize}

    # ── Section 6 — BEM Output Format (skipped in smoke) ──────────────────────

    def validate_bem_output(self) -> dict:
        print("\n--- Section 6: BEM Output Format ---")
        if self.bem is None:
            self._rec("warn", "6.x | BEM output not available (smoke mode or --bem not called)")
            return {}
        _apply_dark()
        b = self.bem
        act_p = [c for c in self.ACT_COLS if c in b.columns]
        hom_p = [c for c in self.HOM_COLS if c in b.columns]
        wrk_p = [c for c in self.WRK_COLS if c in b.columns]

        self._rec("pass" if (len(act_p) == 48 and len(hom_p) == 48 and len(wrk_p) == 48) else "fail",
                  f"6.1 | Schema: act30={len(act_p)}/48 hom30={len(hom_p)}/48 wrk30={len(wrk_p)}/48")
        self.summary_rows.append({
            "Gate / Check": "BEM schema (act/hom/wrk 48 cols each)",
            "Threshold": "48/48/48",
            "Observed": f"{len(act_p)}/{len(hom_p)}/{len(wrk_p)}",
            "Status": "PASS" if (len(act_p)==48 and len(hom_p)==48 and len(wrk_p)==48) else "FAIL",
        })

        arch_present = "office_archetype_ID" in b.columns
        self._rec("pass" if arch_present else "fail",
                  f"6.2 | office_archetype_ID in BEM: {'YES' if arch_present else 'NO'}")

        n = len(b)
        self._rec("pass" if n == self.expected_rows else "fail",
                  f"6.3 | BEM row count: {n:,} (expected {self.expected_rows:,})")

        fig, ax = plt.subplots(figsize=(10, 5))
        if arch_present:
            arch_dist = b["office_archetype_ID"].value_counts()
            ax.bar(range(len(arch_dist)), arch_dist.values,
                   tick_label=arch_dist.index, color="#89b4fa", edgecolor="#1e1e2e")
            ax.set_title("Section 6 — Office Archetype in BEM Output")
            ax.set_xlabel("Archetype")
            ax.set_ylabel("Count")
            ax.tick_params(axis='x', rotation=25)
        plt.tight_layout()
        self.plots_b64["6_bem"] = _b64(fig)

        return {"n": n, "arch_present": arch_present}

    # ── Section 7 — Summary Table ───────────────────────────────────────────────

    def generate_summary_table(self) -> list[dict]:
        print("\n--- Summary Table ---")
        for row in self.summary_rows:
            st = row["Status"]
            icon = "[PASS]" if st == "PASS" else ("[WARN]" if st == "WARN" else "[FAIL]")
            print(f"  {icon} {row['Gate / Check']}: {row['Observed']} — {st}")
        return self.summary_rows

    # ── HTML Report ─────────────────────────────────────────────────────────────

    def build_html_report(self) -> str:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total  = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_sections = [
            ("1_tier_distribution", "Section 1 — Match Tier Distribution"),
            ("2_at_home_overlay",   "Section 2 — AT_HOME Consistency"),
            ("3_at_work",           "Section 3 — AT_WORK Consistency"),
            ("3r_at_retail",        "Section 3r — AT_RETAIL Consistency (NEW, Leg-3)"),
            ("4_schedule_shape",    "Section 4 — Schedule Shape Plausibility"),
            ("5_hh_agg",            "Section 5 — HH Aggregation Integrity"),
            ("6_bem",               "Section 6 — BEM Output Format"),
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

        if self.summary_rows:
            cols = ["Gate / Check", "Threshold", "Observed", "Status"]
            th = "".join(f"<th>{c}</th>" for c in cols)
            trs = ""
            for row in self.summary_rows:
                st  = row["Status"]
                cls = "pass-row" if st == "PASS" else ("warn-row" if st == "WARN" else "fail-row")
                tds = "".join(f"<td>{row[c]}</td>" for c in cols)
                trs += f'<tr class="{cls}">{tds}</tr>'
            summary_html = f"""
        <section class="chart-section" id="summary-table">
          <h2>Summary Table</h2>
          <table class="summary-table">
            <thead><tr>{th}</tr></thead>
            <tbody>{trs}</tbody>
          </table>
        </section>"""
        else:
            summary_html = ""

        def _badge_list(level: str) -> str:
            icon = "[PASS]" if level == "pass" else ("[FAIL]" if level == "fail" else "[WARN]")
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>" for m in items)

        # Section 0 — join-key connectivity table (load-bearing; surfaced prominently
        # right after the scorecard, before the pass/warn/fail badge lists).
        section0_html = ""
        if self.section0_rows:
            s0_cols = ["Key", "Census domain n", "Pool domain n", "Overlap %", "census⊆pool", "Status"]
            s0_th = "".join(f"<th>{c}</th>" for c in s0_cols)
            s0_trs = ""
            any_s0_fail = False
            for row in self.section0_rows:
                st = row["Status"]
                if st == "FAIL":
                    any_s0_fail = True
                cls = "pass-row" if st == "PASS" else ("warn-row" if st == "WARN" else "fail-row")
                tds = "".join(f"<td>{row[c]}</td>" for c in s0_cols)
                s0_trs += f'<tr class="{cls}">{tds}</tr>'
            banner = ('<p class="s0-banner s0-fail">*** FAIL: at least one join key has &lt;100% '
                      'census⊆pool overlap — Leg-2 PR-remap bug class ***</p>') if any_s0_fail else \
                     ('<p class="s0-banner s0-ok">All match keys 100% census⊆pool overlap.</p>')
            section0_html = f"""
    <section class="chart-section" id="section0-table">
      <h2>Section 0 — Join-Key Connectivity Audit (load-bearing checkpoint)</h2>
      {banner}
      <table class="summary-table">
        <thead><tr>{s0_th}</tr></thead>
        <tbody>{s0_trs}</tbody>
      </table>
    </section>"""

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        smoke_tag = " [SMOKE]" if self.is_smoke else ""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>3J Leg-3 Step 5 4-Channel Validation{smoke_tag}</title>
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
              padding:18px 32px; position:sticky; top:0; z-index:100; }}
    header h1 {{ font-size:1.2rem; color:var(--accent); }}
    header p  {{ font-size:0.78rem; color:var(--subtext); }}
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
    .badge {{ padding:8px 14px; border-radius:8px; font-size:0.85rem; }}
    .badge.pass {{ background:#1c2e22; border:1px solid #2d5a35; color:var(--green); }}
    .badge.warn {{ background:#2e2a1c; border:1px solid #5a4e1f; color:var(--yellow); }}
    .badge.fail {{ background:#2e1c1e; border:1px solid #5a2428; color:var(--red); }}
    .chart-section {{ background:var(--surface); border:1px solid var(--border);
                      border-radius:14px; padding:24px; margin-bottom:28px; }}
    .chart-section h2 {{ font-size:1.0rem; color:var(--accent); margin-bottom:16px; }}
    .chart-wrap {{ text-align:center; }}
    .chart-wrap img {{ max-width:100%; border-radius:8px; }}
    .summary-table {{ width:100%; border-collapse:collapse; font-size:0.82rem; margin-top:8px; }}
    .summary-table th {{ background:var(--surface2); color:var(--accent); padding:10px 12px;
                          text-align:left; border-bottom:2px solid var(--border); }}
    .summary-table td {{ padding:8px 12px; border-bottom:1px solid var(--border); }}
    .summary-table tr.pass-row td {{ color:var(--green); }}
    .summary-table tr.warn-row td {{ color:var(--yellow); }}
    .summary-table tr.fail-row td {{ color:var(--red); }}
    .s0-banner {{ font-weight:600; padding:10px 14px; border-radius:8px; margin-bottom:14px; }}
    .s0-banner.s0-ok {{ background:#1c2e22; border:1px solid #2d5a35; color:var(--green); }}
    .s0-banner.s0-fail {{ background:#2e1c1e; border:1px solid #5a2428; color:var(--red); }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem;
              color:var(--subtext); border-top:1px solid var(--border); margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <h1>3J Leg-3 Step 5 — 4-Channel Census-GSS Linkage Validation{smoke_tag}</h1>
    <p>Residential AT_HOME + Office AT_WORK + Retail AT_RETAIL channels | Generated: {ts}</p>
  </header>
  <main>
    <div class="scorecard" id="scorecard">
      <div class="score-card ok"><div class="number">{n_pass}</div>
        <div class="label">Checks Passed</div></div>
      <div class="score-card warn"><div class="number">{n_warn}</div>
        <div class="label">Warnings</div></div>
      <div class="score-card fail"><div class="number">{n_fail}</div>
        <div class="label">Failures</div></div>
      <div class="score-card pct"><div class="number">{pct_ok}%</div>
        <div class="label">Pass Rate</div></div>
    </div>
    {section0_html}
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
  </main>
  <footer>3J Leg-3 Occupancy Pipeline &middot; Step 5 4-Channel Validation &middot; {ts}</footer>
</body>
</html>"""

        suffix_str = f"{self.file_suffix}"
        smoke_str  = "_smoke" if self.is_smoke else ""
        out_path   = os.path.join(self.outputs_dir,
                                  f"3rdJ_step5_validation_report{suffix_str}{smoke_str}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report -> {out_path}")
        return out_path

    # ── Run All ─────────────────────────────────────────────────────────────────

    def run_all(self) -> None:
        _apply_dark()
        print("=" * 60)
        print("3J Leg-3 Step 5 — 4-Channel Census-GSS Linkage Validation")
        print("=" * 60)
        self.validate_join_key_connectivity()
        self.validate_match_tier_distribution()
        self.validate_at_home_consistency()
        self.validate_at_work_consistency()
        self.validate_at_retail_consistency()
        self.validate_schedule_shape()
        self.validate_hh_aggregation()
        self.validate_bem_output()
        self.generate_summary_table()
        self.build_html_report()
        n_p = len(self.results["pass"])
        n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 60}")
        print(f"Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="3J Leg-3 Step 5 4-channel Linkage Validation"
    )
    parser.add_argument("--excl",  action="store_true", help="Validate _excl files")
    parser.add_argument("--smoke", action="store_true",
                        help="Validate smoke outputs (outputs_step5/smoke/)")
    args = parser.parse_args()

    suf = "_excl" if args.excl else ""
    is_smoke = args.smoke

    aug_dir = str(SMOKE_DIR) if is_smoke else str(OUT_DIR)

    CensusLinkageValidator4CH(
        aug_dir=aug_dir,
        census_path=str(CENSUS_FILE),
        outputs_dir=str(OUT_DIR),
        file_suffix=suf,
        is_smoke=is_smoke,
    ).run_all()
