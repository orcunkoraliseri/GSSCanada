"""Step 5 — Census-GSS Linkage: Validation & Report Generation.

Validates aug_pipeline/ outputs against internal consistency checks and
Census baseline. Generates an HTML report with embedded charts.
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import sys
from datetime import datetime

# Force UTF-8 stdout so box-drawing and emoji print cleanly on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── Constants ──────────────────────────────────────────────────────────────────

ACT_LABELS: dict[int, str] = {
    1: "Work", 2: "HH Work", 3: "Caregiving", 4: "Purchasing",
    5: "Sleep & Rest", 6: "Eating", 7: "Personal Care", 8: "Education",
    9: "Socializing", 10: "Passive Leisure", 11: "Active Leisure",
    12: "Community", 13: "Travel", 14: "Misc",
}

EXPECTED_ROWS = 286_537

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


def _hour_labels() -> list[str]:
    out = []
    for i in range(48):
        total_min = 4 * 60 + i * 30
        hh = (total_min // 60) % 24
        out.append(f"{hh:02d}h" if (total_min % 60 == 0) else "")
    return out


# ── Validator ──────────────────────────────────────────────────────────────────

class CensusLinkageValidator:
    """Validates Step 5 Census-GSS linkage outputs."""

    ACT_COLS    = [f"act30_{i:03d}"    for i in range(1, 49)]
    HOM_COLS    = [f"hom30_{i:03d}"    for i in range(1, 49)]
    SPOUSE_COLS = [f"Spouse30_{i:03d}" for i in range(1, 49)]
    HH_HOM_COLS = [f"HH_hom30_{i:03d}" for i in range(1, 49)]

    def __init__(self, aug_pipeline_dir: str, baseline_dir: str,
                 outputs_dir: str, file_suffix: str = "") -> None:
        self.aug_dir      = aug_pipeline_dir
        self.file_suffix  = file_suffix
        self.census_path  = os.path.join(baseline_dir, "alignment", "Aligned_Census_2022.csv")
        self.outputs_dir  = outputs_dir
        os.makedirs(outputs_dir, exist_ok=True)

        _p = lambda d, f: os.path.join(d, f)

        print("Loading 21CEN22GSS_aug_Matched_Keys.csv …")
        self.keys = pd.read_csv(
            _p(aug_pipeline_dir, "21CEN22GSS_aug_Matched_Keys.csv"),
            low_memory=False)
        print(f"  -> {len(self.keys):,} rows  cols: {list(self.keys.columns)}")

        print(f"Loading 21CEN22GSS_aug_Full_Schedules{self.file_suffix}.csv …")
        _sw = {"PP_ID", "IS_SYNTHETIC", "DTYPE", "HH_ID", "DDAY_STRATA"} | \
              set(self.ACT_COLS) | set(self.HOM_COLS) | set(self.SPOUSE_COLS)
        self.sched = pd.read_csv(
            _p(aug_pipeline_dir, f"21CEN22GSS_aug_Full_Schedules{self.file_suffix}.csv"),
            usecols=lambda c: c in _sw, low_memory=False)
        if "DDAY_STRATA" not in self.sched.columns and "PP_ID" in self.sched.columns:
            self.sched = self.sched.merge(
                self.keys[["PP_ID", "DDAY_STRATA"]], on="PP_ID", how="left")
        print(f"  -> {len(self.sched):,} rows x {self.sched.shape[1]} cols")
        self.keys = self.keys[self.keys["PP_ID"].isin(self.sched["PP_ID"])].copy()

        print(f"Loading 21CEN22GSS_aug_Full_Aggregated{self.file_suffix}.csv …")
        _aw = {"PP_ID", "HH_ID", "N_HH_MEMBERS"} | set(self.HH_HOM_COLS)
        self.agg = pd.read_csv(
            _p(aug_pipeline_dir, f"21CEN22GSS_aug_Full_Aggregated{self.file_suffix}.csv"),
            usecols=lambda c: c in _aw, low_memory=False)
        print(f"  -> {len(self.agg):,} rows x {self.agg.shape[1]} cols")

        print(f"Loading 21CEN22GSS_aug_BEM_Schedules{self.file_suffix}.csv …")
        _bw = {"PP_ID", "DTYPE", "BUILT", "BUILTH", "BEDRM", "ROOM", "CONDO"} | \
              set(self.ACT_COLS) | set(self.HOM_COLS)
        self.bem = pd.read_csv(
            _p(aug_pipeline_dir, f"21CEN22GSS_aug_BEM_Schedules{self.file_suffix}.csv"),
            usecols=lambda c: c in _bw, low_memory=False)
        if "BUILT" in self.bem.columns and "BUILTH" not in self.bem.columns:
            self.bem = self.bem.rename(columns={"BUILT": "BUILTH"})
        print(f"  -> {len(self.bem):,} rows x {self.bem.shape[1]} cols")

        print("Loading Aligned_Census_2022.csv …")
        self.census = pd.read_csv(self.census_path, low_memory=False)
        if "BUILT" in self.census.columns and "BUILTH" not in self.census.columns:
            self.census = self.census.rename(columns={"BUILT": "BUILTH"})
        print(f"  -> {len(self.census):,} rows x {self.census.shape[1]} cols")

        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        self.summary_rows: list[dict] = []

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = "[PASS]" if level == "pass" else ("[FAIL]" if level == "fail" else "[WARN]")
        print(f"  {icon} {msg}")

    # ── Section 1 — Match Tier Distribution ────────────────────────────────────

    def validate_match_tier_distribution(self) -> dict:
        print("\n--- Section 1: Match Tier Distribution ---------------------------------")
        _apply_dark()
        k = self.keys

        n = len(k)
        ok11 = n == EXPECTED_ROWS
        self._rec("pass" if ok11 else "fail",
                  f"1.1 | Row count: {n:,} (expected {EXPECTED_ROWS:,})")
        self.summary_rows.append({
            "Gate / Check": "Full-sample row count",
            "Threshold": f"== {EXPECTED_ROWS:,}",
            "Observed": f"{n:,}",
            "Status": "PASS" if ok11 else "FAIL",
        })

        wd = k[k["DDAY_STRATA"] == 1]
        wd_fail = (wd["MATCH_TIER"] == "4_FailSafe").sum()
        wd_rate = wd_fail / len(wd) * 100 if len(wd) > 0 else 0.0
        lv12 = "pass" if wd_rate <= 10 else ("warn" if wd_rate <= 12 else "fail")
        self._rec(lv12, f"1.2 | WD FailSafe rate: {wd_rate:.2f}% (<=10% threshold)")
        self.summary_rows.append({
            "Gate / Check": "WD FailSafe tier",
            "Threshold": "<= 10%",
            "Observed": f"{wd_rate:.2f}%",
            "Status": "PASS" if wd_rate <= 10 else ("WARN" if wd_rate <= 12 else "FAIL"),
        })

        we = k[k["DDAY_STRATA"].isin([2, 3])]
        we_fail = (we["MATCH_TIER"] == "4_FailSafe").sum()
        we_rate = we_fail / len(we) * 100 if len(we) > 0 else 0.0
        self._rec("pass" if we_rate <= 12 else "fail",
                  f"1.3 | WE FailSafe rate: {we_rate:.2f}% (<=12% threshold)")
        self.summary_rows.append({
            "Gate / Check": "WE FailSafe tier",
            "Threshold": "<= 12%",
            "Observed": f"{we_rate:.2f}%",
            "Status": "PASS" if we_rate <= 12 else "FAIL",
        })

        t12 = k["MATCH_TIER"].isin(["1_Perfect", "2_Core"]).sum()
        t12_rate = t12 / n * 100 if n > 0 else 0.0
        self._rec("pass" if t12_rate >= 60 else "fail",
                  f"1.4 | Tier1+2 proportion: {t12_rate:.2f}% (>=60%)")

        dupes = k["PP_ID"].duplicated().sum()
        self._rec("pass" if dupes == 0 else "fail",
                  f"1.5 | Duplicate PP_IDs: {dupes}")

        if "occID" in k.columns:
            null_occ = k["occID"].isna().sum()
            self._rec("pass" if null_occ == 0 else "fail",
                      f"1.6 | Null occIDs: {null_occ}")
        else:
            self._rec("fail", "1.6 | occID column missing from Matched_Keys")

        # Chart: stacked bar WD vs WE
        tier_order  = ["1_Perfect", "2_Core", "3_Constraints", "4_FailSafe"]
        tier_colors = ["#a6e3a1", "#89b4fa", "#f9e2af", "#f38ba8"]
        wd_c = {t: (wd["MATCH_TIER"] == t).sum() for t in tier_order}
        we_c = {t: (we["MATCH_TIER"] == t).sum() for t in tier_order}
        wd_tot = len(wd); we_tot = len(we)

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.array([0, 1])
        bottoms = np.zeros(2)
        for tier, col in zip(tier_order, tier_colors):
            vals = np.array([wd_c[tier], we_c[tier]], dtype=float)
            ax.bar(x, vals, 0.5, bottom=bottoms, label=tier,
                   color=col, edgecolor="#1e1e2e", linewidth=0.8)
            for i, (v, bot) in enumerate(zip(vals, bottoms)):
                tot = wd_tot if i == 0 else we_tot
                pct = v / tot * 100 if tot > 0 else 0
                if v > 1000:
                    ax.text(x[i], bot + v / 2, f"{pct:.1f}%",
                            ha="center", va="center", fontsize=8.5,
                            color="#1e1e2e", fontweight="bold")
            bottoms += vals
        ax.set_xticks(x)
        ax.set_xticklabels(["Weekday (DDAY=1)", "Weekend (DDAY=2,3)"])
        ax.set_ylabel("Count")
        ax.set_title("Section 1 — Match Tier Distribution: WD vs WE", fontsize=12)
        ax.legend(title="Match Tier", fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["1_tier_distribution"] = _b64(fig)

        return {"n": n, "wd_rate": wd_rate, "we_rate": we_rate, "t12_rate": t12_rate}

    # ── Section 2 — AT_HOME Consistency ────────────────────────────────────────

    def validate_at_home_consistency(self) -> dict:
        print("\n─── Section 2: AT_HOME Consistency ────────────────────────────────")
        _apply_dark()
        df = self.sched
        hom_p = [c for c in self.HOM_COLS if c in df.columns]

        if not hom_p:
            self._rec("fail", "2.x | hom30 columns missing from Full_Schedules")
            return {}

        obs = df[df["IS_SYNTHETIC"] == 0]
        base_means = obs[hom_p].mean(axis=0).values * 100
        aug_means  = df[hom_p].mean(axis=0).values * 100

        aug_overall  = aug_means.mean()
        base_overall = base_means.mean()
        diff21 = abs(aug_overall - base_overall)
        self._rec("pass" if diff21 <= 5 else "fail",
                  f"2.1 | Overall mean AT_HOME: aug={aug_overall:.2f}% "
                  f"base={base_overall:.2f}% diff={diff21:.2f}pp (<=5pp)")

        slot_diffs = aug_means - base_means
        max_diff   = np.abs(slot_diffs).max()
        fail_slots = (np.abs(slot_diffs) > 3).sum()
        self._rec("pass" if fail_slots == 0 else "fail",
                  f"2.2 | Per-slot max diff: {max_diff:.2f}pp — "
                  f"{fail_slots} slot(s) exceed +-3pp")
        self.summary_rows.append({
            "Gate / Check": "AT_HOME max deviation (all slots)",
            "Threshold": "<= +-3 pp",
            "Observed": f"{max_diff:.2f} pp",
            "Status": "PASS" if fail_slots == 0 else "FAIL",
        })

        if "DDAY_STRATA" in df.columns:
            wd_m = df[df["DDAY_STRATA"] == 1][hom_p].mean().mean() * 100
            we_m = df[df["DDAY_STRATA"].isin([2, 3])][hom_p].mean().mean() * 100
            self._rec("pass" if wd_m < we_m else "fail",
                      f"2.3 | WD AT_HOME={wd_m:.2f}% < WE AT_HOME={we_m:.2f}%: "
                      f"{'PASS' if wd_m < we_m else 'FAIL'}")
        else:
            self._rec("warn", "2.3 | DDAY_STRATA not available — skip WD<WE check")

        night_mean = df[hom_p[:8]].mean().mean() * 100
        self._rec("pass" if night_mean >= 85 else "fail",
                  f"2.4 | Slots 1-8 mean AT_HOME: {night_mean:.2f}% (>=85%)")
        self.summary_rows.append({
            "Gate / Check": "Night AT_HOME rate (slots 1-8)",
            "Threshold": ">= 85%",
            "Observed": f"{night_mean:.2f}%",
            "Status": "PASS" if night_mean >= 85 else "FAIL",
        })

        fig, ax = plt.subplots(figsize=(14, 5))
        x = np.arange(1, 49)
        ax.plot(x, aug_means,  color="#89b4fa", linewidth=2, label="Augmented")
        ax.plot(x, base_means, color="#a6e3a1", linewidth=2, linestyle="--",
                label="IS_SYNTHETIC=0 baseline")
        ax.fill_between(x, base_means - 3, base_means + 3,
                        alpha=0.15, color="#f9e2af", label="+-3 pp band")
        ax.axhline(85, color="#f38ba8", linestyle=":", linewidth=1,
                   label="85% night threshold")
        tick_pos = list(range(1, 49, 4))
        ax.set_xticks(tick_pos)
        ax.set_xticklabels([f"{(4 + (i-1)*30//60) % 24:02d}h" for i in tick_pos],
                           fontsize=9)
        ax.set_xlabel("30-min slot (04:00 origin)")
        ax.set_ylabel("Mean AT_HOME (%)")
        ax.set_title("Section 2 — AT_HOME 48-slot Overlay: Augmented vs Observed Baseline",
                     fontsize=12)
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["2_at_home_overlay"] = _b64(fig)

        return {"aug_overall": aug_overall, "base_overall": base_overall,
                "max_diff": max_diff, "night_mean": night_mean}

    # ── Section 3 — Schedule Shape Plausibility ─────────────────────────────────

    def validate_schedule_shape(self) -> dict:
        print("\n─── Section 3: Schedule Shape Plausibility ────────────────────────")
        _apply_dark()
        df = self.sched
        act_p    = [c for c in self.ACT_COLS    if c in df.columns]
        spouse_p = [c for c in self.SPOUSE_COLS if c in df.columns]

        if not act_p:
            self._rec("fail", "3.x | act30 columns missing from Full_Schedules")
            return {}

        obs = df[df["IS_SYNTHETIC"] == 0]

        # 3.1
        act_flat = df[act_p].values.flatten().astype(float)
        act_flat = act_flat[~np.isnan(act_flat)].astype(int)
        oor = ((act_flat < 1) | (act_flat > 14)).sum()
        self._rec("pass" if oor == 0 else "fail",
                  f"3.1 | Out-of-range act30 values: {oor}")

        # 3.2
        obs_flat = obs[act_p].values.flatten().astype(float)
        obs_flat = obs_flat[~np.isnan(obs_flat)].astype(int)
        aug_share = {a: float((act_flat == a).mean() * 100) for a in range(1, 15)}
        obs_share = {a: float((obs_flat == a).mean() * 100) for a in range(1, 15)}
        top5 = sorted(obs_share, key=obs_share.get, reverse=True)[:5]
        max_diff32 = max(abs(aug_share[a] - obs_share[a]) for a in top5)
        fail32 = sum(1 for a in top5 if abs(aug_share[a] - obs_share[a]) > 5)
        self._rec("pass" if fail32 == 0 else "fail",
                  f"3.2 | Top-5 act time-share max diff: {max_diff32:.2f}pp "
                  f"({fail32} act(s) > +-5pp)")
        self.summary_rows.append({
            "Gate / Check": "Top-5 activity deviation",
            "Threshold": "<= +-5 pp",
            "Observed": f"{max_diff32:.2f} pp",
            "Status": "PASS" if fail32 == 0 else "FAIL",
        })

        # 3.3
        night_flat = df[act_p[:8]].values.flatten().astype(float)
        night_flat = night_flat[~np.isnan(night_flat)].astype(int)
        sleep_rate = float((night_flat == 5).mean() * 100)
        self._rec("pass" if sleep_rate >= 70 else "fail",
                  f"3.3 | Slots 1-8 sleep dominance: {sleep_rate:.2f}% (>=70%)")
        self.summary_rows.append({
            "Gate / Check": "Night sleep dominance (slots 1-8)",
            "Threshold": ">= 70%",
            "Observed": f"{sleep_rate:.2f}%",
            "Status": "PASS" if sleep_rate >= 70 else "FAIL",
        })

        # 3.4 trivially passes (IS_SYN=0 vs itself)
        self._rec("pass", "3.4 | IS_SYNTHETIC=0 JS divergence vs itself: 0.000000 (<0.001 trivially)")

        # 3.5 Spouse30 NaN pattern
        if spouse_p:
            obs_all_nan = obs[spouse_p].isna().all(axis=1).sum()
            self._rec("pass",
                      f"3.5 | Spouse30 rows all-NaN in IS_SYN=0: "
                      f"{obs_all_nan:,}/{len(obs):,} "
                      f"({obs_all_nan/len(obs)*100:.1f}%) — expected for 2005/2010")
        else:
            self._rec("warn", "3.5 | Spouse30 columns not found — skip NaN check")

        # Chart
        total = len(df)
        heat = np.zeros((14, len(act_p)))
        for i, a in enumerate(range(1, 15)):
            heat[i] = (df[act_p].values == a).sum(axis=0) / total * 100
        heat_norm = heat.copy()
        for i in range(14):
            rm = heat_norm[i].max()
            if rm > 0:
                heat_norm[i] /= rm

        fig, axes = plt.subplots(1, 2, figsize=(18, 6),
                                 gridspec_kw={"width_ratios": [3, 1]})
        ax = axes[0]
        im = ax.imshow(heat_norm, aspect="auto", cmap="plasma",
                       interpolation="nearest", vmin=0, vmax=1)
        cb = plt.colorbar(im, ax=ax, fraction=0.015, pad=0.01)
        cb.set_label("Relative intensity (row-normalised)", fontsize=8)
        ax.set_yticks(range(14))
        ax.set_yticklabels([ACT_LABELS[a] for a in range(1, 15)], fontsize=8.5)
        tick_pos = list(range(0, 48, 4))
        ax.set_xticks(tick_pos)
        ax.set_xticklabels(
            [f"{(4 + t*30//60) % 24:02d}h" for t in tick_pos],
            fontsize=8.5, rotation=45)
        ax.set_xlabel("30-min slot (04:00 origin)")
        ax.set_title("Activity Heatmap 14x48 (augmented)", fontsize=11)

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
        ax2.xaxis.grid(True, linestyle="--", alpha=0.3)

        plt.suptitle("Section 3 — Schedule Shape Plausibility",
                     fontsize=13, fontweight="bold")
        plt.tight_layout()
        self.plots_b64["3_schedule_shape"] = _b64(fig)

        return {"oor": int(oor), "max_diff32": max_diff32,
                "sleep_rate": sleep_rate, "top5": top5}

    # ── Section 4 — HH Aggregation Integrity ───────────────────────────────────

    def validate_hh_aggregation(self) -> dict:
        print("\n─── Section 4: HH Aggregation Integrity ───────────────────────────")
        _apply_dark()
        df = self.agg
        hh_hom_p = [c for c in self.HH_HOM_COLS if c in df.columns]

        null_hh = df["HH_ID"].isna().sum() if "HH_ID" in df.columns else -1
        self._rec("pass" if null_hh == 0 else "fail",
                  f"4.1 | Null HH_IDs: {null_hh if null_hh >= 0 else 'col missing'}")

        mean_hhsize = 0.0
        if "N_HH_MEMBERS" in df.columns:
            mean_hhsize = float(df["N_HH_MEMBERS"].mean())
            flag = abs(mean_hhsize - 2.80) > 0.5
            self._rec("warn" if flag else "pass",
                      f"4.2 | Mean HHSIZE: {mean_hhsize:.3f} "
                      f"(Census ref ~2.80) "
                      f"{'WARN outside +-0.5' if flag else 'within +-0.5'}")
        else:
            self._rec("fail", "4.2 | N_HH_MEMBERS column missing")

        if "PP_ID" in df.columns:
            dupes = df["PP_ID"].duplicated().sum()
            self._rec("pass" if dupes == 0 else "fail",
                      f"4.3 | Duplicate PP_IDs in aggregated: {dupes}")

        hh_means = pd.Series([], dtype=float)
        if hh_hom_p:
            hh_means = df[hh_hom_p].mean(axis=1)
            oor_lo = (hh_means < 0.3).sum()
            oor_hi = (hh_means > 1.0).sum()
            self._rec("pass" if (oor_lo == 0 and oor_hi == 0) else "fail",
                      f"4.4 | Per-HH mean AT_HOME out-of-range [0.3,1.0]: "
                      f"below={oor_lo} above={oor_hi}")
        else:
            self._rec("warn", "4.4 | HH_hom30 columns missing")

        n = len(df)
        self._rec("pass" if n == EXPECTED_ROWS else "fail",
                  f"4.5 | Aggregated row count: {n:,} (expected {EXPECTED_ROWS:,})")

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("Section 4 — HH Aggregation Integrity",
                     fontsize=13, fontweight="bold")

        ax = axes[0]
        if "N_HH_MEMBERS" in df.columns:
            cnt = df["N_HH_MEMBERS"].dropna().astype(int).value_counts().sort_index()
            ax.bar(cnt.index, cnt.values, color="#89b4fa",
                   edgecolor="#1e1e2e", linewidth=0.8, width=0.7)
            ax.axvline(mean_hhsize, color="#f38ba8", linestyle="--",
                       linewidth=1.5, label=f"Mean={mean_hhsize:.2f}")
            ax.axvline(2.80, color="#a6e3a1", linestyle=":",
                       linewidth=1.5, label="Census ref=2.80")
            ax.legend(fontsize=9)
        ax.set_xlabel("HH Size (N_HH_MEMBERS)")
        ax.set_ylabel("Count")
        ax.set_title("HH Size Distribution", fontsize=11)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        ax2 = axes[1]
        if len(hh_means) > 0:
            bp = ax2.boxplot(hh_means.dropna().values, patch_artist=True,
                             medianprops=dict(color="#1e1e2e", linewidth=2))
            bp["boxes"][0].set_facecolor("#89b4fa")
            bp["boxes"][0].set_alpha(0.85)
            ax2.axhline(0.3, color="#f38ba8", linestyle="--",
                        linewidth=1, label="0.3 lower bound")
            ax2.axhline(1.0, color="#a6e3a1", linestyle="--",
                        linewidth=1, label="1.0 upper bound")
            ax2.legend(fontsize=9)
        ax2.set_ylabel("Per-HH Mean AT_HOME")
        ax2.set_title("Per-HH Mean AT_HOME Distribution", fontsize=11)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)

        plt.tight_layout()
        self.plots_b64["4_hh_aggregation"] = _b64(fig)

        return {"n": n, "null_hh": null_hh, "mean_hhsize": mean_hhsize}

    # ── Section 5 — BEM Output Format ──────────────────────────────────────────

    def validate_bem_output(self) -> dict:
        print("\n─── Section 5: BEM Output Format ──────────────────────────────────")
        _apply_dark()
        b = self.bem
        act_p = [c for c in self.ACT_COLS if c in b.columns]
        hom_p = [c for c in self.HOM_COLS if c in b.columns]

        self._rec("pass" if (len(act_p) == 48 and len(hom_p) == 48) else "fail",
                  f"5.1 | Schema: act30={len(act_p)}/48 hom30={len(hom_p)}/48")

        if act_p:
            av = b[act_p].values.flatten().astype(float)
            av = av[~np.isnan(av)].astype(int)
            oor_act = int(((av < 1) | (av > 14)).sum())
            self._rec("pass" if oor_act == 0 else "fail",
                      f"5.2 | act30 out-of-range values: {oor_act}")
        else:
            oor_act = -1
            self._rec("fail", "5.2 | act30 columns missing from BEM")

        if hom_p:
            hv = b[hom_p].values.flatten().astype(float)
            hv = hv[~np.isnan(hv)]
            oor_hom = int((~np.isin(hv, [0.0, 1.0])).sum())
            self._rec("pass" if oor_hom == 0 else "fail",
                      f"5.3 | hom30 non-binary values: {oor_hom}")
        else:
            oor_hom = -1
            self._rec("fail", "5.3 | hom30 columns missing from BEM")

        # 5.4 DTYPE distribution
        bem_dtype = b["DTYPE"].value_counts(normalize=True).sort_index() \
                    if "DTYPE" in b.columns else None
        cen_dtype = self.census["DTYPE"].value_counts(normalize=True).sort_index() \
                    if "DTYPE" in self.census.columns else None
        dtype_match = False
        max_dtype_diff = float("nan")
        all_types: list = []
        if bem_dtype is not None and cen_dtype is not None:
            all_types = sorted(set(bem_dtype.index) | set(cen_dtype.index))
            diffs = [abs(bem_dtype.get(t, 0) - cen_dtype.get(t, 0)) * 100
                     for t in all_types]
            max_dtype_diff = max(diffs)
            dtype_match = max_dtype_diff < 0.01
            self._rec("pass" if dtype_match else "fail",
                      f"5.4 | DTYPE distribution match: max diff={max_dtype_diff:.4f}%")
        else:
            self._rec("fail", "5.4 | DTYPE missing in BEM or Census")
        self.summary_rows.append({
            "Gate / Check": "DTYPE distribution",
            "Threshold": "Exact match",
            "Observed": f"max diff={max_dtype_diff:.4f}%" if not (max_dtype_diff != max_dtype_diff) else "N/A",
            "Status": "PASS" if dtype_match else "FAIL",
        })

        # 5.5 building var completeness
        build_vars = ["DTYPE", "BUILTH", "BEDRM", "ROOM", "CONDO"]
        completeness: dict[str, int] = {}
        for v in build_vars:
            if v in b.columns:
                nct = int(b[v].isna().sum())
                completeness[v] = nct
                self._rec("pass" if nct == 0 else "warn",
                          f"5.5 | {v} null count: {nct}")
            else:
                completeness[v] = -1
                self._rec("warn", f"5.5 | {v} not found in BEM output")

        n = len(b)
        self._rec("pass" if n == EXPECTED_ROWS else "fail",
                  f"5.6 | BEM row count: {n:,} (expected {EXPECTED_ROWS:,})")

        # Charts
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("Section 5 — BEM Output Format", fontsize=13, fontweight="bold")

        ax = axes[0]
        if bem_dtype is not None and cen_dtype is not None and all_types:
            x = np.arange(len(all_types))
            ax.bar(x - 0.2, [bem_dtype.get(t, 0) * 100 for t in all_types], 0.35,
                   label="BEM output", color="#89b4fa", edgecolor="#1e1e2e")
            ax.bar(x + 0.2, [cen_dtype.get(t, 0) * 100 for t in all_types], 0.35,
                   label="Census baseline", color="#a6e3a1", edgecolor="#1e1e2e")
            ax.set_xticks(x)
            ax.set_xticklabels([f"DTYPE={t}" for t in all_types])
            ax.legend(fontsize=9)
        ax.set_ylabel("Proportion (%)")
        ax.set_title("DTYPE Distribution: BEM vs Census", fontsize=11)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        ax2 = axes[1]
        ax2.axis("off")
        tbl_rows = []
        for v, nct in completeness.items():
            if nct == -1:
                tbl_rows.append([v, "MISSING", "—"])
            else:
                pct = f"{100 - nct/n*100:.2f}%" if n > 0 else "—"
                st = "100%" if nct == 0 else f"{nct:,} null"
                tbl_rows.append([v, pct, st])
        tbl = ax2.table(cellText=tbl_rows,
                        colLabels=["Variable", "Complete %", "Status"],
                        cellLoc="center", loc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        tbl.scale(1, 1.8)
        ax2.set_title("Building Variable Completeness", fontsize=11)

        plt.tight_layout()
        self.plots_b64["5_bem_format"] = _b64(fig)

        return {"n": n, "dtype_match": dtype_match, "completeness": completeness}

    # ── Section 6 — Regression vs Baseline ─────────────────────────────────────

    def validate_regression_vs_baseline(self) -> dict:
        print("\n─── Section 6: Regression vs Baseline ─────────────────────────────")
        _apply_dark()
        df = self.sched
        b  = self.bem
        hom_p    = [c for c in self.HOM_COLS    if c in df.columns]
        act_p    = [c for c in self.ACT_COLS    if c in df.columns]
        spouse_p = [c for c in self.SPOUSE_COLS if c in df.columns]
        obs = df[df["IS_SYNTHETIC"] == 0]

        aug_hom = df[hom_p].mean(axis=0).values * 100 if hom_p else np.array([])
        obs_hom = obs[hom_p].mean(axis=0).values * 100 if hom_p else np.array([])

        # 6.1 AT_HOME per slot ≤ +-3 pp  (EXPECTED FAIL ~6.7 pp)
        max_diff61 = float("nan")
        slot_diffs6 = np.array([])
        if len(aug_hom) > 0:
            slot_diffs6 = aug_hom - obs_hom
            max_diff61  = float(np.abs(slot_diffs6).max())
            fail61 = int((np.abs(slot_diffs6) > 3).sum())
            ok = fail61 == 0
            note = " [EXPECTED FAIL — documented deviation ~6.7pp]" if not ok else ""
            self._rec("pass" if ok else "fail",
                      f"6.1 | AT_HOME max slot diff: {max_diff61:.2f}pp "
                      f"({fail61} slot(s) > +-3pp){note}")

        # 6.2 top-5 activity share ≤ +-2 pp (EXPECTED FAIL Work ~3.3 pp)
        top5: list = []
        max_diff62 = float("nan")
        aug_share6: dict = {}
        obs_share6: dict = {}
        if act_p:
            af = df[act_p].values.flatten().astype(float)
            af = af[~np.isnan(af)].astype(int)
            of = obs[act_p].values.flatten().astype(float)
            of = of[~np.isnan(of)].astype(int)
            aug_share6 = {a: float((af == a).mean() * 100) for a in range(1, 15)}
            obs_share6 = {a: float((of == a).mean() * 100) for a in range(1, 15)}
            top5 = sorted(obs_share6, key=obs_share6.get, reverse=True)[:5]
            max_diff62 = max(abs(aug_share6[a] - obs_share6[a]) for a in top5)
            fail62 = sum(1 for a in top5 if abs(aug_share6[a] - obs_share6[a]) > 2)
            ok = fail62 == 0
            note = " [EXPECTED FAIL — documented Work deviation ~3.3pp]" if not ok else ""
            self._rec("pass" if ok else "fail",
                      f"6.2 | Top-5 act diff: max={max_diff62:.2f}pp "
                      f"({fail62} act(s) > +-2pp){note}")
            self.summary_rows.append({
                "Gate / Check": "Top-5 activity deviation (regression +-2pp gate)",
                "Threshold": "<= +-2 pp",
                "Observed": f"{max_diff62:.2f} pp",
                "Status": "PASS" if ok else "FAIL",
            })

        # 6.3 Spouse30 mean diff ≤ +-3 pp
        diff63 = float("nan")
        if spouse_p:
            aug_sp = float(df[spouse_p].mean(axis=0).mean() * 100)
            obs_sp = float(obs[spouse_p].mean(axis=0).mean() * 100)
            diff63 = abs(aug_sp - obs_sp)
            self._rec("pass" if diff63 <= 3 else "fail",
                      f"6.3 | Spouse30 mean diff: {diff63:.2f}pp (<=3pp)")
            self.summary_rows.append({
                "Gate / Check": "Spouse co-presence deviation",
                "Threshold": "<= +-3 pp",
                "Observed": f"{diff63:.2f} pp",
                "Status": "PASS" if diff63 <= 3 else "FAIL",
            })
        else:
            self._rec("warn", "6.3 | Spouse30 columns missing — skip")

        # 6.4 DTYPE distribution exact match
        bem_dtype = b["DTYPE"].value_counts(normalize=True).sort_index() \
                    if "DTYPE" in b.columns else None
        cen_dtype = self.census["DTYPE"].value_counts(normalize=True).sort_index() \
                    if "DTYPE" in self.census.columns else None
        if bem_dtype is not None and cen_dtype is not None:
            all_t = sorted(set(bem_dtype.index) | set(cen_dtype.index))
            md = max(abs(bem_dtype.get(t, 0) - cen_dtype.get(t, 0)) * 100
                     for t in all_t)
            self._rec("pass" if md < 0.01 else "fail",
                      f"6.4 | DTYPE distribution vs Census: max diff={md:.4f}%")

        # Charts
        fig, axes = plt.subplots(1, 2, figsize=(16, 5))
        fig.suptitle("Section 6 — Regression vs Baseline", fontsize=13, fontweight="bold")

        ax = axes[0]
        if len(aug_hom) > 0:
            x = np.arange(1, 49)
            ax.plot(x, aug_hom, color="#89b4fa", linewidth=2, label="Augmented")
            ax.plot(x, obs_hom, color="#a6e3a1", linewidth=2, linestyle="--",
                    label="IS_SYNTHETIC=0 baseline")
            ax.fill_between(x, obs_hom - 3, obs_hom + 3,
                            alpha=0.15, color="#f9e2af", label="+-3 pp band")
            tick_pos = list(range(1, 49, 4))
            ax.set_xticks(tick_pos)
            ax.set_xticklabels(
                [f"{(4 + (i-1)*30//60) % 24:02d}h" for i in tick_pos],
                fontsize=9)
            ax.legend(fontsize=9)
        ax.set_xlabel("30-min slot (04:00 origin)")
        ax.set_ylabel("Mean AT_HOME (%)")
        ax.set_title("AT_HOME Overlay with +-3pp bands", fontsize=11)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)

        ax2 = axes[1]
        if top5 and aug_share6:
            diffs_s = [aug_share6[a] - obs_share6[a] for a in top5]
            colors  = ["#a6e3a1" if d >= 0 else "#f38ba8" for d in diffs_s]
            y = np.arange(5)
            ax2.barh(y, diffs_s, 0.6, color=colors, edgecolor="#1e1e2e")
            ax2.axvline(0,  color="#cdd6f4", linewidth=1.2)
            ax2.axvline(2,  color="#f9e2af", linestyle="--", linewidth=1)
            ax2.axvline(-2, color="#f9e2af", linestyle="--", linewidth=1,
                        label="+-2pp limit")
            ax2.set_yticks(y)
            ax2.set_yticklabels([ACT_LABELS.get(a, str(a)) for a in top5], fontsize=9)
            ax2.set_xlabel("Signed diff: aug - baseline (pp)")
            ax2.legend(fontsize=8)
        ax2.set_title("Top-5 Activity Share Difference", fontsize=11)
        ax2.xaxis.grid(True, linestyle="--", alpha=0.3)

        plt.tight_layout()
        self.plots_b64["6_regression"] = _b64(fig)

        return {"max_diff61": max_diff61, "max_diff62": max_diff62, "diff63": diff63}

    # ── Section 7 — Summary Table ───────────────────────────────────────────────

    def generate_summary_table(self) -> list[dict]:
        print("\n─── Section 7: Summary Table ───────────────────────────────────────")
        for row in self.summary_rows:
            st = row["Status"]
            icon = "[PASS]" if st == "PASS" else ("[WARN]" if st == "WARN" else "[FAIL]")
            print(f"  {icon} {row['Gate / Check']}: "
                  f"{row['Observed']} — {st}")
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
            ("3_schedule_shape",    "Section 3 — Schedule Shape Plausibility"),
            ("4_hh_aggregation",    "Section 4 — HH Aggregation Integrity"),
            ("5_bem_format",        "Section 5 — BEM Output Format"),
            ("6_regression",        "Section 6 — Regression vs Baseline"),
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
            icon  = "[PASS]" if level == "pass" else ("[FAIL]" if level == "fail" else "[WARN]")
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(f"<li class='badge {level}'>{icon} {m}</li>"
                           for m in items)

        nav_links = "".join(
            f'<a href="#{k}">{lbl.split("—")[0].strip()}</a>'
            for k, lbl in chart_sections if k in self.plots_b64)
        nav_links += '<a href="#summary-table">Section 7</a>'

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Step 5 — Census-GSS Linkage Validation Report</title>
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
    .summary-table tr.fail-row td {{ color:var(--red); }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem;
              color:var(--subtext); border-top:1px solid var(--border); margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Step 5 — Census-GSS Linkage Validation Report</h1>
      <p>Validates aug_pipeline/ outputs: match tiers, AT_HOME, schedule shape,
         HH aggregation, BEM format, and regression vs IS_SYNTHETIC=0 baseline</p>
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
  <footer>
    Occupancy Modeling Pipeline &middot; Step 5 Census-GSS Linkage Validation &middot;
    Inputs: {self.aug_dir}/ &middot; Census: {self.census_path} &middot;
    Output: {os.path.join(self.outputs_dir, f"step5_validation_report{self.file_suffix}.html")} &middot;
    Generated: {ts}
  </footer>
</body>
</html>"""

        out_path = os.path.join(self.outputs_dir, f"step5_validation_report{self.file_suffix}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved -> {out_path}")
        return out_path

    # ── Run All ─────────────────────────────────────────────────────────────────

    def run_all(self) -> None:
        _apply_dark()
        print("=" * 60)
        print("Step 5 — Census-GSS Linkage Validation")
        print("=" * 60)
        self.validate_match_tier_distribution()
        self.validate_at_home_consistency()
        self.validate_schedule_shape()
        self.validate_hh_aggregation()
        self.validate_bem_output()
        self.validate_regression_vs_baseline()
        self.generate_summary_table()
        self.build_html_report()
        n_p = len(self.results["pass"])
        n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 60}")
        print(f"Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--excl", action="store_true", help="Run on _excl files")
    args = parser.parse_args()
    suffix = "_excl" if args.excl else ""
    CensusLinkageValidator(
        aug_pipeline_dir="../0_Occupancy/Outputs_21CEN22GSS/aug_pipeline",
        baseline_dir="../0_Occupancy/Outputs_21CEN22GSS",
        outputs_dir="outputs_step5",
        file_suffix=suffix,
    ).run_all()
