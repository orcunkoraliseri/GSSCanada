"""Step 3 — Merge & Temporal Feature Derivation: Validation & Report Generation.

Validates merged_episodes.csv and hetus_wide.csv against Step 2 reference files.
Generates an HTML report with embedded base64 PNG charts.

Input:  outputs_step3/merged_episodes.csv, outputs_step3/hetus_wide.csv
Ref:    outputs_step2/main_*.csv, outputs_step2/episode_*.csv
Output: outputs_step3/step3_validation_report.html
"""

from __future__ import annotations

import base64
import io
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ── Constants ──────────────────────────────────────────────────────────────────

CYCLES = [2005, 2010, 2015, 2022]

STEP3_OVERVIEW = """\
╔══════════════════════════════════════════════════════════════════════════╗
║  STEP 3 — MERGE & TEMPORAL FEATURE DERIVATION                          ║
║                                                                          ║
║  LEFT JOIN: Episode ← Main on occID                                    ║
║  Weight rule: WGHT_EPI (episode-level) / WGHT_PER (person-level)       ║
║                                                                          ║
║  Derived columns:                                                        ║
║  • SEASON       ← SURVMNTH (Dec/Jan/Feb=Winter … Sep/Oct/Nov=Fall)     ║
║  • DAYTYPE      ← DDAY (Mon–Fri=Weekday / Sat–Sun=Weekend)             ║
║  • HOUR_OF_DAY  ← startMin // 60  → 0–23                              ║
║  • TIMESLOT_10  ← startMin // 10 + 1  → slots 1–144 (HETUS format)    ║
║  • AT_HOME      ← LOCATION==300 → binary 1/0                          ║
║  • STRATA_ID    ← DDAY × SURVMNTH → integer 1–84                      ║
║                                                                          ║
║  HETUS 144-slot conversion:                                             ║
║  Variable-length episodes → 144 fixed 10-min activity tokens per person ║
║  (4:00 AM start; diary integrity: sum(duration)==1440 enforced)        ║
║                                                                          ║
║  DIARY_VALID QA filter: respondents with sum(duration) ≠ 1440 min     ║
║  are excluded before HETUS conversion (corrupted diaries)              ║
║                                                                          ║
║  Output: ~64,000 diary rows (each has 1 of 84 strata observed)         ║
║  ┌────────────┬────────────┬────────────┬────────────┬────────────┐    ║
║  │ 2005 (C19) │ 2010 (C24) │ 2015 (C29) │ 2022 GSSP  │  TOTAL     │    ║
║  │  19,221    │  15,114    │  17,390    │  12,336    │  64,061    │    ║
║  └────────────┴────────────┴────────────┴────────────┴────────────┘    ║
║                                                                          ║
║  Files produced:                                                         ║
║  • merged_episodes.csv / .parquet  (episode-level, ~1.05M rows)        ║
║  • hetus_wide.csv  (one row per respondent, 288 slot columns)          ║
╚══════════════════════════════════════════════════════════════════════════╝"""

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

# HETUS night slots: 22:00–06:00 in 4AM-origin slot numbering
# Slot 1=04:00, slot 109=22:00, slots 1-12=04:00-06:00, slots 109-144=22:00-04:00
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

class GSSMergeValidator:
    """Validates Step 3 merge & temporal feature derivation outputs."""

    def __init__(self, step2_dir: str, step3_dir: str) -> None:
        print("Loading Step 2 reference files…")
        self.main_s2: dict[int, pd.DataFrame] = {}
        self.epi_s2: dict[int, pd.DataFrame] = {}
        for c in CYCLES:
            self.main_s2[c] = pd.read_csv(
                f"{step2_dir}/main_{c}.csv", low_memory=False)
            self.epi_s2[c] = pd.read_csv(
                f"{step2_dir}/episode_{c}.csv", low_memory=False)
            print(f"  main_{c}: {len(self.main_s2[c]):,}  "
                  f"episode_{c}: {len(self.epi_s2[c]):,}")

        print("Loading Step 3 outputs…")
        self.merged = pd.read_csv(
            f"{step3_dir}/merged_episodes.csv", low_memory=False)
        print(f"  merged_episodes: {len(self.merged):,} rows × "
              f"{self.merged.shape[1]} cols")

        self.hetus = pd.read_csv(
            f"{step3_dir}/hetus_wide.csv", low_memory=False)
        print(f"  hetus_wide: {len(self.hetus):,} rows × "
              f"{self.hetus.shape[1]} cols")

        h30_path = f"{step3_dir}/hetus_30min.csv"
        if os.path.exists(h30_path):
            self.hetus_30min = pd.read_csv(h30_path, low_memory=False)
            print(f"  hetus_30min: {len(self.hetus_30min):,} rows × "
                  f"{self.hetus_30min.shape[1]} cols")
        else:
            self.hetus_30min = None
            print("  hetus_30min: NOT FOUND — Section 7 will be skipped")

        self.step3_dir = step3_dir
        self.results: dict[str, list[str]] = {"pass": [], "fail": [], "warn": []}
        self.plots_b64: dict[str, str] = {}
        self.summary_data: dict = {}

    # ── helpers ────────────────────────────────────────────────────────────────

    def _rec(self, level: str, msg: str) -> None:
        self.results[level].append(msg)
        icon = "✅" if level == "pass" else ("❌" if level == "fail" else "⚠️")
        print(f"  {icon} {msg}")

    # ── Section 1: Row Count Preservation ─────────────────────────────────────

    def validate_row_counts(self) -> dict:
        print("\n─── Section 1: Row Count Preservation ────────────────────────")
        _apply_dark()

        s2_main_counts = {c: len(self.main_s2[c]) for c in CYCLES}
        s2_epi_counts = {c: len(self.epi_s2[c]) for c in CYCLES}

        # Post-filter per-cycle respondents and episodes from merged_episodes
        post_resp: dict[int, int] = {}
        post_epi: dict[int, int] = {}
        for c in CYCLES:
            cyc = self.merged[self.merged["CYCLE_YEAR"] == c]
            post_resp[c] = cyc[["occID", "CYCLE_YEAR"]].drop_duplicates().shape[0]
            post_epi[c] = len(cyc)

        # Check 1.1: main row counts (step2 = source of truth)
        for c in CYCLES:
            self._rec("pass",
                      f"1.1 | {c} Main rows (Step 2 reference): "
                      f"{s2_main_counts[c]:,}")

        # Check 1.2: episode row counts step2 vs post-filter
        for c in CYCLES:
            pre = s2_epi_counts[c]
            post = post_epi[c]
            if pre >= post:
                self._rec("pass",
                          f"1.2 | {c} Episodes: Step2={pre:,} → "
                          f"post-filter={post:,} ({pre - post:,} removed)")
            else:
                self._rec("fail",
                          f"1.2 | {c} Episode count INCREASED: "
                          f"{pre:,} → {post:,}")

        # Check 1.3: merged total <= step2 episode total (LEFT JOIN + filter)
        total_s2_epi = sum(s2_epi_counts.values())
        total_merged = len(self.merged)
        if total_merged <= total_s2_epi:
            self._rec("pass",
                      f"1.3 | Total episodes Step2={total_s2_epi:,} → "
                      f"merged={total_merged:,} (after DIARY_VALID filter)")
        else:
            self._rec("fail",
                      f"1.3 | Merged episodes {total_merged:,} exceeds "
                      f"Step2 total {total_s2_epi:,}")

        # Check 1.4: DIARY_VALID exclusion rates
        exclusion_rows: list[dict] = []
        for c in CYCLES:
            pre = s2_main_counts[c]
            post = post_resp[c]
            excluded = pre - post
            rate = excluded / pre * 100 if pre > 0 else 0.0
            level = "pass" if rate < 3 else ("warn" if rate < 5 else "fail")
            self._rec(level,
                      f"1.4 | {c} Exclusion: {excluded:,}/{pre:,} "
                      f"({rate:.2f}%)")
            exclusion_rows.append({
                "Cycle": str(c),
                "Step2 Resp": pre,
                "Post-filter Resp": post,
                "Excluded": excluded,
                "Rate (%)": round(rate, 2),
            })

        # Check 1.5: informational totals
        self._rec("pass",
                  f"1.5 | Post-filter totals: "
                  f"{sum(post_resp.values()):,} respondents | "
                  f"{sum(post_epi.values()):,} episodes")

        # Chart 1a: respondents bar + exclusion rate bar
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("Row Count Preservation — Step 2 vs. Step 3",
                     fontsize=14, fontweight="bold")

        x = np.arange(len(CYCLES))
        w = 0.35

        ax = axes[0]
        ax.bar(x - w / 2, [s2_main_counts[c] for c in CYCLES], w,
               label="Step 2 Resp.", color="#89b4fa",
               edgecolor="#1e1e2e", linewidth=0.8)
        ax.bar(x + w / 2, [post_resp[c] for c in CYCLES], w,
               label="Step 3 Post-filter", color="#a6e3a1",
               edgecolor="#1e1e2e", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_title("Respondents: Step 2 vs. Step 3 Post-filter", fontsize=12)
        ax.set_ylabel("Count")
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        for i, c in enumerate(CYCLES):
            ax.text(i - w / 2, s2_main_counts[c] + 100,
                    f"{s2_main_counts[c]:,}", ha="center",
                    fontsize=7.5, color="#cdd6f4")
            ax.text(i + w / 2, post_resp[c] + 100,
                    f"{post_resp[c]:,}", ha="center",
                    fontsize=7.5, color="#a6e3a1")

        ax2 = axes[1]
        rates = [r["Rate (%)"] for r in exclusion_rows]
        colors = ["#a6e3a1" if r < 3 else ("#f9e2af" if r < 5 else "#f38ba8")
                  for r in rates]
        bars = ax2.bar([str(c) for c in CYCLES], rates,
                       color=colors, edgecolor="#1e1e2e",
                       linewidth=0.8, width=0.55)
        ax2.axhline(5, color="#f38ba8", linestyle="--",
                    linewidth=1.2, label="5% FAIL threshold")
        ax2.axhline(3, color="#f9e2af", linestyle="--",
                    linewidth=1.0, label="3% WARN threshold")
        ax2.set_title("DIARY_VALID Exclusion Rate per Cycle", fontsize=12)
        ax2.set_ylabel("Exclusion Rate (%)")
        ax2.legend(fontsize=9)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        for bar, val in zip(bars, rates):
            ax2.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.05,
                     f"{val:.2f}%", ha="center",
                     fontsize=10, fontweight="bold")

        plt.tight_layout()
        self.plots_b64["1_row_counts"] = _b64(fig)

        result = {
            "s2_main_counts": s2_main_counts,
            "s2_epi_counts": s2_epi_counts,
            "post_resp": post_resp,
            "post_epi": post_epi,
            "exclusion_rows": exclusion_rows,
        }
        self.summary_data["section1"] = result
        return result

    # ── Section 2: Merge Key Integrity ─────────────────────────────────────────

    def validate_merge_integrity(self) -> dict:
        print("\n─── Section 2: Merge Key Integrity ─────────────────────────────")
        _apply_dark()

        # Check 2.1: orphan episodes (null WGHT_PER = no Main match)
        orphans = self.merged["WGHT_PER"].isna().sum()
        level = "pass" if orphans == 0 else "fail"
        self._rec(level, f"2.1 | Orphan episodes (null WGHT_PER): {orphans}")

        # Check 2.2: no duplicate (occID, CYCLE_YEAR) in hetus_wide
        hetus_dupes = self.hetus.duplicated(subset=["occID", "CYCLE_YEAR"]).sum()
        level = "pass" if hetus_dupes == 0 else "fail"
        self._rec(level,
                  f"2.2 | Duplicate (occID, CYCLE_YEAR) in hetus_wide "
                  f"(proxy for Main uniqueness): {hetus_dupes}")

        # Check 2.3: WGHT_PER 100% non-null
        null_wght = self.merged["WGHT_PER"].isna().sum()
        null_rate = null_wght / len(self.merged) * 100
        level = "pass" if null_wght == 0 else "fail"
        self._rec(level,
                  f"2.3 | WGHT_PER null count: {null_wght} "
                  f"({null_rate:.3f}%)")

        # Check 2.4: CYCLE_YEAR only expected values
        actual_years = set(self.merged["CYCLE_YEAR"].dropna().unique().astype(int))
        expected_years = set(CYCLES)
        unexpected = actual_years - expected_years
        level = "pass" if not unexpected else "fail"
        self._rec(level,
                  f"2.4 | CYCLE_YEAR values: {sorted(actual_years)} "
                  f"{'✓ all expected' if not unexpected else '— unexpected: ' + str(unexpected)}")

        # Per-cycle stats for chart
        per_cycle_stats = []
        for c in CYCLES:
            cyc = self.merged[self.merged["CYCLE_YEAR"] == c]
            n_epi = len(cyc)
            n_resp = cyc[["occID", "CYCLE_YEAR"]].drop_duplicates().shape[0]
            n_orphan = cyc["WGHT_PER"].isna().sum()
            wght = pd.to_numeric(cyc["WGHT_PER"], errors="coerce").dropna()
            per_cycle_stats.append({
                "cycle": c,
                "n_epi": n_epi,
                "n_resp": n_resp,
                "n_orphan": n_orphan,
                "wght_mean": wght.mean(),
                "wght_median": wght.median(),
                "wght_min": wght.min(),
                "wght_max": wght.max(),
                "wght_vals": wght,
            })

        # Chart: 3-panel layout
        # Left  — check results summary table
        # Centre — per-cycle episode & respondent counts
        # Right  — WGHT_PER box plot per cycle
        fig = plt.figure(figsize=(17, 5))
        fig.suptitle("Merge Key Integrity", fontsize=14, fontweight="bold")
        gs = fig.add_gridspec(1, 3, wspace=0.35)
        ax_tbl = fig.add_subplot(gs[0])
        ax_cnt = fig.add_subplot(gs[1])
        ax_wgt = fig.add_subplot(gs[2])

        # ── Panel 1: check results table ──────────────────────────────────────
        ax_tbl.axis("off")
        checks = [
            ("2.1", "Orphan episodes", orphans, "= 0"),
            ("2.2", "Dup. (occID,CYCLE_YEAR)\nin hetus_wide", hetus_dupes, "= 0"),
            ("2.3", "WGHT_PER null count", null_wght, "= 0"),
            ("2.4", "Unexpected CYCLE_YEAR\nvalues",
             len(unexpected), "= 0"),
        ]
        row_h = 0.18
        top = 0.92
        ax_tbl.text(0.5, 1.0, "Check Results", ha="center", va="top",
                    fontsize=11, fontweight="bold", color="#cdd6f4",
                    transform=ax_tbl.transAxes)
        for i, (chk, label, val, criterion) in enumerate(checks):
            y = top - i * row_h
            ok = val == 0
            badge_col = "#1c2e22" if ok else "#2e1c1e"
            border_col = "#2d5a35" if ok else "#5a2428"
            text_col = "#a6e3a1" if ok else "#f38ba8"
            icon = "✓" if ok else "✗"
            # Background rectangle
            rect = plt.Rectangle((0.01, y - 0.13), 0.98, 0.15,
                                  facecolor=badge_col, edgecolor=border_col,
                                  linewidth=1.0, transform=ax_tbl.transAxes,
                                  clip_on=False)
            ax_tbl.add_patch(rect)
            ax_tbl.text(0.06, y - 0.05, f"{icon} {chk}",
                        ha="left", va="center", fontsize=9,
                        fontweight="bold", color=text_col,
                        transform=ax_tbl.transAxes)
            ax_tbl.text(0.22, y - 0.05, label,
                        ha="left", va="center", fontsize=8,
                        color="#cdd6f4", transform=ax_tbl.transAxes)
            ax_tbl.text(0.78, y - 0.05, f"{val:,}  ({criterion})",
                        ha="left", va="center", fontsize=8.5,
                        fontweight="bold", color=text_col,
                        transform=ax_tbl.transAxes)

        # ── Panel 2: episode & respondent counts per cycle ────────────────────
        x = np.arange(len(CYCLES))
        w = 0.35
        ep_vals = [s["n_epi"] for s in per_cycle_stats]
        resp_vals = [s["n_resp"] for s in per_cycle_stats]
        ax_cnt.bar(x - w / 2, ep_vals, w, label="Episodes",
                   color="#fab387", edgecolor="#1e1e2e", linewidth=0.8)
        ax_cnt.bar(x + w / 2, resp_vals, w, label="Respondents",
                   color="#89b4fa", edgecolor="#1e1e2e", linewidth=0.8)
        ax_cnt.set_xticks(x)
        ax_cnt.set_xticklabels([str(c) for c in CYCLES])
        ax_cnt.set_title("Episodes & Respondents\nper Cycle (post-filter)",
                         fontsize=11)
        ax_cnt.set_ylabel("Count")
        ax_cnt.legend(fontsize=8.5)
        ax_cnt.yaxis.grid(True, linestyle="--", alpha=0.3)
        for i, (ep, rp) in enumerate(zip(ep_vals, resp_vals)):
            ax_cnt.text(i - w / 2, ep + ep * 0.01, f"{ep:,}",
                        ha="center", fontsize=6.5, color="#fab387")
            ax_cnt.text(i + w / 2, rp + rp * 0.01, f"{rp:,}",
                        ha="center", fontsize=6.5, color="#89b4fa")

        # ── Panel 3: WGHT_PER box plot per cycle ──────────────────────────────
        wgt_data = [s["wght_vals"].values for s in per_cycle_stats]
        bp = ax_wgt.boxplot(wgt_data, patch_artist=True,
                            medianprops=dict(color="#1e1e2e", linewidth=2),
                            flierprops=dict(marker="o", markersize=1.5,
                                            alpha=0.4),
                            whiskerprops=dict(linewidth=1.0),
                            capprops=dict(linewidth=1.0))
        for patch, col in zip(bp["boxes"], CYCLE_COLORS):
            patch.set_facecolor(col)
            patch.set_alpha(0.85)
        for flier, col in zip(bp["fliers"], CYCLE_COLORS):
            flier.set(markerfacecolor=col, markeredgecolor=col)
        ax_wgt.set_xticks(range(1, len(CYCLES) + 1))
        ax_wgt.set_xticklabels([str(c) for c in CYCLES])
        ax_wgt.set_title("WGHT_PER Distribution\nper Cycle", fontsize=11)
        ax_wgt.set_ylabel("Person Weight")
        ax_wgt.yaxis.grid(True, linestyle="--", alpha=0.3)
        for i, s in enumerate(per_cycle_stats):
            ax_wgt.text(i + 1, s["wght_median"],
                        f"  med={s['wght_median']:,.0f}",
                        va="center", fontsize=7.5, color="#cdd6f4")

        plt.tight_layout()
        self.plots_b64["2_merge_integrity"] = _b64(fig)

        return {"orphans": orphans, "hetus_dupes": hetus_dupes,
                "null_wght": null_wght}

    # ── Section 3: Derived Feature Verification ────────────────────────────────

    def validate_derived_features(self) -> dict:
        print("\n─── Section 3: Derived Feature Verification ────────────────────")
        _apply_dark()
        df = self.merged

        # Check 3.1: DAYTYPE values
        daytype_vals = set(df["DAYTYPE"].dropna().unique())
        unexpected_dt = daytype_vals - {"Weekday", "Weekend"}
        level = "pass" if not unexpected_dt else "fail"
        self._rec(level,
                  f"3.1 | DAYTYPE values: {daytype_vals} "
                  f"{'✓' if not unexpected_dt else '— unexpected: ' + str(unexpected_dt)}")

        # Check 3.2: Weekday ratio 65–77%
        wday_rate = (df["DAYTYPE"] == "Weekday").mean() * 100
        level = "pass" if 65 <= wday_rate <= 77 else "warn"
        self._rec(level,
                  f"3.2 | Weekday ratio: {wday_rate:.1f}% (expected 65–77%)")

        # Check 3.3: HOUR_OF_DAY range
        if "HOUR_OF_DAY" in df.columns:
            hod_vals = sorted(df["HOUR_OF_DAY"].dropna().unique().astype(int))
            missing_hours = set(range(24)) - set(hod_vals)
            oor = ((df["HOUR_OF_DAY"] < 0) | (df["HOUR_OF_DAY"] > 23)).sum()
            level = ("pass" if not missing_hours and oor == 0
                     else ("warn" if not missing_hours else "fail"))
            self._rec(level,
                      f"3.3 | HOUR_OF_DAY: range {min(hod_vals)}–{max(hod_vals)}, "
                      f"{len(hod_vals)} unique hours, out-of-range={oor} "
                      f"{'✓' if not missing_hours else '— missing: ' + str(missing_hours)}")
        else:
            self._rec("fail", "3.3 | HOUR_OF_DAY column missing")

        # Check 3.4: TIMESLOT_10 range 1–144
        if "TIMESLOT_10" in df.columns:
            ts_vals = sorted(df["TIMESLOT_10"].dropna().unique().astype(int))
            missing_slots = set(range(1, 145)) - set(ts_vals)
            oor_ts = ((df["TIMESLOT_10"] < 1) | (df["TIMESLOT_10"] > 144)).sum()
            level = ("pass" if not missing_slots and oor_ts == 0
                     else "warn")
            self._rec(level,
                      f"3.4 | TIMESLOT_10: range {min(ts_vals)}–{max(ts_vals)}, "
                      f"{len(ts_vals)} unique slots, out-of-range={oor_ts} "
                      f"{'✓' if not missing_slots else '— missing ' + str(len(missing_slots)) + ' slots'}")
        else:
            self._rec("fail", "3.4 | TIMESLOT_10 column missing")

        # Check 3.5: startMin range 0–1439
        if "startMin" in df.columns:
            oor_sm = ((df["startMin"] < 0) | (df["startMin"] > 1439)).sum()
            sm_min = df["startMin"].min()
            sm_max = df["startMin"].max()
            level = "pass" if oor_sm == 0 else "fail"
            self._rec(level,
                      f"3.5 | startMin: range {sm_min}–{sm_max}, "
                      f"out-of-range={oor_sm}")
        else:
            self._rec("fail", "3.5 | startMin column missing")

        # Check 3.6: DDAY_STRATA ∈ {1, 2, 3}  (3-category: 1=Weekday, 2=Sat, 3=Sun)
        if "DDAY_STRATA" in df.columns:
            ds_vals = set(df["DDAY_STRATA"].dropna().unique().astype(int))
            unexpected_ds = ds_vals - {1, 2, 3}
            level = "pass" if not unexpected_ds else "fail"
            self._rec(level,
                      f"3.6 | DDAY_STRATA values: {sorted(ds_vals)} "
                      f"{'✓' if not unexpected_ds else '— unexpected: ' + str(unexpected_ds)}")
        else:
            self._rec("fail", "3.6 | DDAY_STRATA column missing")

        # Check 3.7: DAYTYPE ↔ DDAY_STRATA consistency
        if "DDAY_STRATA" in df.columns and "DAYTYPE" in df.columns:
            consistent = (
                ((df["DAYTYPE"] == "Weekday") & (df["DDAY_STRATA"] == 1)) |
                ((df["DAYTYPE"] == "Weekend") & df["DDAY_STRATA"].isin([2, 3]))
            )
            inconsistent = (~consistent).sum()
            level = "pass" if inconsistent == 0 else "fail"
            self._rec(level,
                      f"3.7 | DAYTYPE↔DDAY_STRATA inconsistencies: {inconsistent}")
        else:
            self._rec("fail", "3.7 | DDAY_STRATA or DAYTYPE column missing")

        # ── Charts ──────────────────────────────────────────────────────────────

        # Chart 3a: DAYTYPE distribution (overall + per cycle)
        _apply_dark()
        subsets = [("Overall", df)] + [
            (str(c), df[df["CYCLE_YEAR"] == c]) for c in CYCLES]
        fig, axes = plt.subplots(1, 5, figsize=(16, 4))
        fig.suptitle("DAYTYPE Distribution — Overall and Per Cycle",
                     fontsize=13, fontweight="bold")
        cat_list = ["Weekday", "Weekend"]
        dt_colors = ["#89b4fa", "#f38ba8"]
        for idx, (lbl, sub) in enumerate(subsets):
            ax = axes[idx]
            vc = sub["DAYTYPE"].value_counts(normalize=True) * 100
            vals = [vc.get(cat, 0) for cat in cat_list]
            x_pos = np.arange(len(cat_list))
            bars = ax.bar(x_pos, vals, color=dt_colors,
                          edgecolor="#1e1e2e", linewidth=0.8, width=0.6)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(cat_list, fontsize=9)
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        val + 1, f"{val:.1f}%",
                        ha="center", fontsize=9, fontweight="bold")
            ax.axhline(71, color="#f9e2af", linestyle="--",
                       linewidth=0.8, alpha=0.7)
            ax.set_ylim(0, 108)
            ax.set_title(lbl, fontsize=11, fontweight="bold")
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
            if idx > 0:
                ax.set_yticks([])
        plt.tight_layout()
        self.plots_b64["3a_daytype"] = _b64(fig)

        # Chart 3b: HOUR_OF_DAY histogram
        _apply_dark()
        fig, ax = plt.subplots(figsize=(13, 4))
        if "HOUR_OF_DAY" in df.columns:
            hod_counts = df["HOUR_OF_DAY"].value_counts().sort_index()
            ax.bar(hod_counts.index, hod_counts.values,
                   color="#89b4fa", edgecolor="#1e1e2e",
                   linewidth=0.6, width=0.8)
            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Episode Count")
            ax.set_title(
                "Episode Start Times — HOUR_OF_DAY Distribution",
                fontsize=13)
            ax.set_xticks(range(0, 24))
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        self.plots_b64["3b_hour_of_day"] = _b64(fig)

        # Chart 3c: TIMESLOT_10 distribution
        _apply_dark()
        fig, ax = plt.subplots(figsize=(13, 4))
        if "TIMESLOT_10" in df.columns:
            ts_counts = df["TIMESLOT_10"].value_counts().sort_index()
            ax.bar(ts_counts.index, ts_counts.values,
                   color="#fab387", edgecolor="#1e1e2e",
                   linewidth=0.3, width=1.0)
            ax.set_xlabel("HETUS Slot (1–144, 4AM origin)")
            ax.set_ylabel("Episode Count")
            ax.set_title(
                "Episode Start Slot Distribution — TIMESLOT_10",
                fontsize=13)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
            # Vertical time markers every 3 hours
            for hr_off in range(0, 24, 3):
                slot_n = hr_off * 6 + 1
                t_lbl = f"{(4 + hr_off) % 24:02d}:00"
                ax.axvline(slot_n, color="#555", linestyle="--",
                           linewidth=0.8, alpha=0.7)
                ax.text(slot_n + 0.3, ax.get_ylim()[1] * 0.95,
                        t_lbl, fontsize=7.5, color="#a6adc8",
                        rotation=90, va="top")
        self.plots_b64["3c_timeslot"] = _b64(fig)

        # Chart 3d: DDAY_STRATA per cycle
        _apply_dark()
        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        fig.suptitle(
            "DDAY_STRATA Distribution per Cycle "
            "(1=Weekday, 2=Saturday, 3=Sunday)",
            fontsize=12, fontweight="bold")
        dday_cats = [1, 2, 3]
        dday_lbls = ["Weekday", "Saturday", "Sunday"]
        dday_colors = ["#89b4fa", "#f38ba8", "#fab387"]
        for idx, c in enumerate(CYCLES):
            ax = axes[idx]
            cyc = df[df["CYCLE_YEAR"] == c]
            if "DDAY_STRATA" in cyc.columns:
                vc = (cyc["DDAY_STRATA"].dropna().astype(int)
                      .value_counts(normalize=True).sort_index() * 100)
                vals = [vc.get(cat, 0) for cat in dday_cats]
                x_pos = np.arange(len(dday_cats))
                bars = ax.bar(x_pos, vals, color=dday_colors,
                              edgecolor="#1e1e2e", linewidth=0.8, width=0.6)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(dday_lbls, fontsize=8)
                for bar, val in zip(bars, vals):
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            val + 0.5, f"{val:.1f}%",
                            ha="center", fontsize=8.5, fontweight="bold")
            ax.set_title(str(c), fontsize=12, fontweight="bold",
                         color=CYCLE_COLORS[idx])
            ax.set_ylim(0, 100)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["3d_dday_strata"] = _b64(fig)

        return {"wday_rate": wday_rate}

    # ── Section 4: HETUS 144-Slot Integrity ────────────────────────────────────

    def validate_hetus_slots(self) -> dict:
        print("\n─── Section 4: HETUS 144-Slot Integrity ────────────────────────")
        _apply_dark()
        h = self.hetus

        SLOT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
        HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]
        slot_present = [c for c in SLOT_COLS if c in h.columns]
        home_present = [c for c in HOME_COLS if c in h.columns]

        # Check 4.1: slot completeness
        if slot_present:
            incomplete = h[slot_present].isna().any(axis=1).sum()
            pct = (1 - incomplete / len(h)) * 100
            level = ("pass" if incomplete == 0
                     else ("warn" if pct > 99 else "fail"))
            self._rec(level,
                      f"4.1 | Activity slot completeness: {pct:.2f}% "
                      f"({incomplete} respondents with NaN slots)")
        else:
            self._rec("fail", "4.1 | slot_* columns missing from hetus_wide")

        # Check 4.2: activity codes ∈ {1…14}
        if slot_present:
            slot_data = h[slot_present].values.flatten()
            slot_data = slot_data[~pd.isna(slot_data)].astype(int)
            invalid = ((slot_data < 1) | (slot_data > 14)).sum()
            level = "pass" if invalid == 0 else "fail"
            self._rec(level,
                      f"4.2 | Invalid activity codes (outside 1–14): {invalid}")

        # Check 4.3: AT_HOME completeness
        if home_present:
            incomplete_h = h[home_present].isna().any(axis=1).sum()
            pct_h = (1 - incomplete_h / len(h)) * 100
            level = ("pass" if incomplete_h == 0
                     else ("warn" if pct_h > 99 else "fail"))
            self._rec(level,
                      f"4.3 | AT_HOME slot completeness: {pct_h:.2f}% "
                      f"({incomplete_h} respondents with NaN home slots)")
        else:
            self._rec("fail", "4.3 | home_* columns missing from hetus_wide")

        # Check 4.4: AT_HOME binary only
        if home_present:
            home_data = h[home_present].values.flatten()
            home_data = home_data[~pd.isna(home_data)].astype(int)
            non_binary = (~np.isin(home_data, [0, 1])).sum()
            level = "pass" if non_binary == 0 else "fail"
            self._rec(level,
                      f"4.4 | Non-binary AT_HOME values: {non_binary}")

        # Check 4.5: HETUS row count == unique merged respondents
        unique_merged = (self.merged[["occID", "CYCLE_YEAR"]]
                         .drop_duplicates().shape[0])
        hetus_rows = len(h)
        level = "pass" if hetus_rows == unique_merged else "fail"
        self._rec(level,
                  f"4.5 | HETUS rows {hetus_rows:,} vs. unique merged "
                  f"respondents {unique_merged:,} "
                  f"{'✓' if hetus_rows == unique_merged else '✗ MISMATCH'}")

        # Check 4.6: Sleep & Rest (occACT=5) dominance in night slots
        night_slot_cols = [f"slot_{i:03d}" for i in NIGHT_SLOTS
                           if f"slot_{i:03d}" in h.columns]
        sleep_rate = 0.0
        if night_slot_cols:
            night_data = h[night_slot_cols].values.flatten()
            night_data = night_data[~pd.isna(night_data)].astype(int)
            sleep_rate = (night_data == 5).mean() * 100  # 5 = Sleep & Rest
            level = "pass" if sleep_rate > 50 else "warn"
            self._rec(level,
                      f"4.6 | Night slots Sleep & Rest (occACT=5) rate: "
                      f"{sleep_rate:.1f}% (expected >50%)")

        # Check 4.7: AT_HOME night rate > 80%
        night_home_cols = [f"home_{i:03d}" for i in NIGHT_SLOTS
                           if f"home_{i:03d}" in h.columns]
        night_home_rate = 0.0
        if night_home_cols:
            nh_data = h[night_home_cols].values.flatten()
            nh_data = nh_data[~pd.isna(nh_data)]
            night_home_rate = nh_data.mean() * 100
            level = "pass" if night_home_rate > 80 else "warn"
            self._rec(level,
                      f"4.7 | Night AT_HOME rate: {night_home_rate:.1f}% "
                      f"(expected >80%)")

        # ── Charts ──────────────────────────────────────────────────────────────

        # Chart 4a: Activity heatmap 14 × 144
        if slot_present:
            _apply_dark()
            slot_matrix = h[slot_present].values  # (n, 144)
            heat = np.zeros((14, len(slot_present)))
            total = len(h)
            for act in range(1, 15):
                heat[act - 1] = (slot_matrix == act).sum(axis=0) / total * 100

            # Row-wise normalisation: scale each activity to its own peak
            # so rare and common activities are equally readable.
            # Raw % values kept as annotation reference.
            heat_norm = heat.copy()
            for i in range(14):
                row_max = heat_norm[i].max()
                if row_max > 0:
                    heat_norm[i] /= row_max   # 0 → 1 per row

            fig, ax = plt.subplots(figsize=(18, 6))
            im = ax.imshow(heat_norm, aspect="auto", cmap="plasma",
                           interpolation="nearest", vmin=0, vmax=1)
            cb = plt.colorbar(im, ax=ax, fraction=0.015, pad=0.01)
            cb.set_label("Relative intensity (row-normalised to activity peak)",
                         fontsize=9)
            ax.set_yticks(range(14))
            ax.set_yticklabels([ACT_LABELS[i + 1] for i in range(14)],
                               fontsize=8.5)
            # x-axis labels every 18 slots = 3 hours
            xtick_pos = list(range(0, 144, 18))
            xtick_lbl = [f"{(4 + i * 10 // 60) % 24:02d}:{(i * 10) % 60:02d}"
                         for i in xtick_pos]
            ax.set_xticks(xtick_pos)
            ax.set_xticklabels(xtick_lbl, fontsize=8.5, rotation=45)
            ax.set_xlabel("Time of Day (4AM origin, 10-min slots)")
            ax.set_title(
                "Activity Distribution Heatmap — "
                "14 Activities × 144 HETUS Slots",
                fontsize=13, pad=10)
            plt.tight_layout()
            self.plots_b64["4a_activity_heatmap"] = _b64(fig)

        # Chart 4b: AT_HOME curve across 144 slots
        if home_present:
            _apply_dark()
            home_means = h[home_present].mean(axis=0).values * 100
            fig, ax = plt.subplots(figsize=(14, 4))
            x = np.arange(1, len(home_means) + 1)
            ax.plot(x, home_means, color="#89b4fa", linewidth=1.5)
            ax.fill_between(x, home_means, alpha=0.25, color="#89b4fa")
            ax.axhline(80, color="#f9e2af", linestyle="--",
                       linewidth=1, label="80% reference")
            ax.set_ylim(0, 105)
            ax.set_xlabel("HETUS Slot (1–144, 4AM origin)")
            ax.set_ylabel("Mean AT_HOME Rate (%)")
            ax.set_title("AT_HOME Rate Across 144 HETUS Slots", fontsize=13)
            ax.legend(fontsize=9)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3)
            for hr_off in range(0, 24, 4):
                slot_n = hr_off * 6 + 1
                t_lbl = f"{(4 + hr_off) % 24:02d}:00"
                ax.axvline(slot_n, color="#555", linestyle="--",
                           linewidth=0.7, alpha=0.5)
                ax.text(slot_n + 0.3, 102, t_lbl, fontsize=7.5,
                        color="#a6adc8", rotation=90, va="top")
            self.plots_b64["4b_at_home_curve"] = _b64(fig)

        # Chart 4c: Slot completeness by cycle
        _apply_dark()
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.suptitle("HETUS Slot Completeness by Cycle",
                     fontsize=13, fontweight="bold")

        for ax_idx, (cols, title) in enumerate([
            (slot_present, "Activity Slots"),
            (home_present, "AT_HOME Slots"),
        ]):
            ax = axes[ax_idx]
            pcts = []
            for c in CYCLES:
                cyc = h[h["CYCLE_YEAR"] == c] if "CYCLE_YEAR" in h.columns else h
                inc = cyc[cols].isna().any(axis=1).sum() if cols else len(cyc)
                pcts.append((1 - inc / len(cyc)) * 100 if len(cyc) > 0 else 0.0)
            bars = ax.bar([str(c) for c in CYCLES], pcts,
                          color=CYCLE_COLORS, edgecolor="#1e1e2e",
                          linewidth=0.8, width=0.55)
            ax.axhline(99, color="#f9e2af", linestyle="--",
                       linewidth=1, label="99% threshold")
            ax.set_ylim(95, 101)
            ax.set_title(f"{title} Completeness", fontsize=11)
            ax.set_ylabel("% Complete")
            ax.legend(fontsize=9)
            for bar, val in zip(bars, pcts):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.03,
                        f"{val:.2f}%", ha="center",
                        fontsize=9, fontweight="bold")

        plt.tight_layout()
        self.plots_b64["4c_slot_completeness"] = _b64(fig)

        return {"hetus_rows": hetus_rows, "unique_merged": unique_merged,
                "sleep_rate": sleep_rate, "night_home_rate": night_home_rate}

    # ── Section 5: Cross-Cycle Consistency ─────────────────────────────────────

    def validate_cross_cycle_consistency(self) -> dict:
        print("\n─── Section 5: Cross-Cycle Consistency ─────────────────────────")
        _apply_dark()
        df = self.merged

        # Check 5.1: Weighted activity distribution per cycle
        act_dist: dict[int, dict[int, float]] = {}
        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            wt = pd.to_numeric(cyc.get("WGHT_EPI", pd.Series(
                np.ones(len(cyc)))), errors="coerce").fillna(1.0)
            acts = pd.to_numeric(cyc["occACT"], errors="coerce")
            valid = acts.notna()
            dist: dict[int, float] = {}
            wt_total = wt[valid].sum()
            for code in range(1, 15):
                mask = (acts == code) & valid
                dist[code] = (wt[mask].sum() / wt_total * 100
                              if wt_total > 0 else 0.0)
            act_dist[c] = dist
        self._rec("pass",
                  f"5.1 | Weighted activity distribution computed for "
                  f"{len(act_dist)} cycles")

        # Check 5.2: Weighted AT_HOME rate per cycle (55–75%)
        home_rates: dict[int, float] = {}
        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            wt = pd.to_numeric(cyc.get("WGHT_EPI", pd.Series(
                np.ones(len(cyc)))), errors="coerce").fillna(1.0)
            home = pd.to_numeric(cyc["AT_HOME"], errors="coerce")
            valid = home.notna()
            if valid.any():
                rate = (wt[valid] * home[valid]).sum() / wt[valid].sum() * 100
            else:
                rate = 0.0
            home_rates[c] = rate
            level = "pass" if 55 <= rate <= 75 else "warn"
            self._rec(level,
                      f"5.2 | {c} Weighted AT_HOME rate: {rate:.1f}% "
                      f"(expected 55–75%)")

        # Check 5.3: Demographic marginals Step2 vs Step3
        for var in ["SEX", "AGEGRP", "MARSTH", "HHSIZE", "CMA", "LFTAG", "HRSWRK", "KOL", "TOTINC"]: # "MODE",
            for c in CYCLES:
                if var not in self.main_s2[c].columns:
                    continue
                s2_dist = (self.main_s2[c][var]
                           .value_counts(normalize=True)
                           .sort_index())
                s3_resp = (df[df["CYCLE_YEAR"] == c]
                           .drop_duplicates(subset=["occID", "CYCLE_YEAR"]))
                if var not in s3_resp.columns:
                    continue
                s3_dist = (s3_resp[var]
                           .value_counts(normalize=True)
                           .sort_index())
                diff = (s2_dist - s3_dist.reindex(
                    s2_dist.index, fill_value=0)).abs().max()
                level = "pass" if diff < 0.02 else "warn"
                self._rec(level,
                          f"5.3 | {c} {var} max marginal diff "
                          f"(Step2 vs Step3): {diff:.4f} "
                          f"{'✓' if diff < 0.02 else '⚠ >2%'}")

        # Check 5.4: Episodes per respondent (10–30)
        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            ep_per = cyc.groupby("occID").size()
            mean_ep = ep_per.mean()
            median_ep = ep_per.median()
            level = "pass" if 10 <= mean_ep <= 30 else "warn"
            self._rec(level,
                      f"5.4 | {c} Episodes/respondent: "
                      f"mean={mean_ep:.1f}, median={median_ep:.1f} "
                      f"(expected 10–30)")

        # ── Charts ──────────────────────────────────────────────────────────────

        # Chart 5a: Stacked bar — weighted activity proportions per cycle
        _apply_dark()
        fig, ax = plt.subplots(figsize=(12, 6))
        cmap_ = plt.colormaps["tab20"].resampled(14)
        act_colors = [cmap_(i) for i in range(14)]
        x = np.arange(len(CYCLES))
        bottoms = np.zeros(len(CYCLES))
        for act_code in range(1, 15):
            vals = [act_dist.get(c, {}).get(act_code, 0) for c in CYCLES]
            ax.bar(x, vals, 0.6, bottom=bottoms,
                   label=ACT_LABELS[act_code],
                   color=act_colors[act_code - 1],
                   edgecolor="#1e1e2e", linewidth=0.3)
            for i, (val, bot) in enumerate(zip(vals, bottoms)):
                if val > 3:
                    ax.text(i, bot + val / 2, f"{val:.1f}",
                            ha="center", va="center",
                            fontsize=7, color="white", fontweight="bold")
            bottoms += np.array(vals)
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in CYCLES])
        ax.set_ylim(0, 108)
        ax.set_ylabel("Weighted Activity Proportion (%)")
        ax.set_title(
            "Weighted Activity Distribution per Cycle (14 categories)",
            fontsize=13)
        ax.legend(loc="upper right", fontsize=7.5, ncol=2, framealpha=0.8)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["5a_activity_dist"] = _b64(fig)

        # Chart 5b: Line chart — weighted AT_HOME per cycle
        _apply_dark()
        fig, ax = plt.subplots(figsize=(8, 4))
        cyc_list = list(home_rates.keys())
        rate_vals = [home_rates[c] for c in cyc_list]
        ax.plot(cyc_list, rate_vals, color="#89b4fa",
                marker="o", linewidth=2, markersize=8)
        ax.fill_between(cyc_list, rate_vals, alpha=0.2, color="#89b4fa")
        ax.axhline(55, color="#f38ba8", linestyle="--",
                   linewidth=1, label="55% lower bound")
        ax.axhline(75, color="#a6e3a1", linestyle="--",
                   linewidth=1, label="75% upper bound")
        for c, r in home_rates.items():
            ax.text(c, r + 0.5, f"{r:.1f}%",
                    ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(40, 90)
        ax.set_xticks(cyc_list)
        ax.set_title("Weighted AT_HOME Rate per Cycle (expected 55–75%)",
                     fontsize=12)
        ax.set_ylabel("Weighted AT_HOME (%)")
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["5b_at_home_rate"] = _b64(fig)

        # Chart 5c: Demographics Step2 vs Step3 per cycle
        _apply_dark()
        demo_vars = ["SEX", "AGEGRP", "MARSTH", "HHSIZE", "CMA", "LFTAG", "HRSWRK", "KOL", "TOTINC"] # "MODE",
        fig, axes = plt.subplots(
            len(demo_vars), len(CYCLES),
            figsize=(16, 4 * len(demo_vars)))
        fig.suptitle(
            "Demographic Distributions — Step 2 vs. Step 3 (post-filter)",
            fontsize=13, fontweight="bold")
        for row_i, var in enumerate(demo_vars):
            for col_i, c in enumerate(CYCLES):
                ax = axes[row_i, col_i]
                s2_d = (self.main_s2[c][var]
                        .value_counts(normalize=True).sort_index() * 100
                        if var in self.main_s2[c].columns
                        else pd.Series(dtype=float))
                s3_resp = (df[df["CYCLE_YEAR"] == c]
                           .drop_duplicates(subset=["occID", "CYCLE_YEAR"]))
                s3_d = (s3_resp[var]
                        .value_counts(normalize=True).sort_index() * 100
                        if var in s3_resp.columns
                        else pd.Series(dtype=float))
                cats = sorted(set(s2_d.index) | set(s3_d.index))
                x_pos = np.arange(len(cats))
                w = 0.35
                ax.bar(x_pos - w / 2,
                       [s2_d.get(cat, 0) for cat in cats], w,
                       label="Step 2", color="#89b4fa",
                       edgecolor="#1e1e2e", linewidth=0.6)
                ax.bar(x_pos + w / 2,
                       [s3_d.get(cat, 0) for cat in cats], w,
                       label="Step 3", color="#a6e3a1",
                       edgecolor="#1e1e2e", linewidth=0.6)
                ax.set_xticks(x_pos)
                ax.set_xticklabels([str(cat) for cat in cats], fontsize=8)
                ax.yaxis.grid(True, linestyle="--", alpha=0.3)
                if row_i == 0:
                    ax.set_title(str(c), fontsize=12, fontweight="bold",
                                 color=CYCLE_COLORS[col_i])
                if col_i == 0:
                    ax.set_ylabel(var, fontsize=10)
                if row_i == 0 and col_i == 0:
                    ax.legend(fontsize=8)
        plt.tight_layout()
        self.plots_b64["5c_demographics"] = _b64(fig)

        # Chart 5d: Box plot — episodes per respondent by cycle
        _apply_dark()
        ep_data = []
        for c in CYCLES:
            cyc = df[df["CYCLE_YEAR"] == c]
            ep_per = cyc.groupby("occID").size().reset_index(name="n")
            ep_per["Cycle"] = str(c)
            ep_data.append(ep_per)
        combined = pd.concat(ep_data, ignore_index=True)
        palette = {str(c): col for c, col in zip(CYCLES, CYCLE_COLORS)}
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.boxplot(data=combined, x="Cycle", y="n",
                    hue="Cycle", palette=palette,
                    linewidth=1.2, fliersize=2, legend=False, ax=ax)
        ax.axhline(10, color="#f38ba8", linestyle="--",
                   linewidth=1, label="10 lower bound")
        ax.axhline(30, color="#a6e3a1", linestyle="--",
                   linewidth=1, label="30 upper bound")
        ax.set_title("Episodes per Respondent by Cycle (expected 10–30)",
                     fontsize=12)
        ax.set_xlabel("Survey Cycle")
        ax.set_ylabel("Episode Count")
        ax.legend(fontsize=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        self.plots_b64["5d_episodes_per_resp"] = _b64(fig)

        return {"home_rates": home_rates, "act_dist": act_dist}

    # ── Section 6: Summary Statistics Table ────────────────────────────────────

    def generate_summary_table(self) -> pd.DataFrame:
        print("\n─── Section 6: Summary Statistics Table ────────────────────────")

        s1 = self.summary_data.get("section1", {})
        s2_main = s1.get("s2_main_counts", {})
        post_resp = s1.get("post_resp", {})
        post_epi = s1.get("post_epi", {})
        excl_map = {r["Cycle"]: r for r in s1.get("exclusion_rows", [])}

        SLOT_COLS = [f"slot_{i:03d}" for i in range(1, 145)]
        HOME_COLS = [f"home_{i:03d}" for i in range(1, 145)]
        slot_present = [c for c in SLOT_COLS if c in self.hetus.columns]

        rows = []
        totals = dict(s2=0, pre=0, post=0, ep=0, hetus=0)

        for c in CYCLES:
            cyc_m = self.merged[self.merged["CYCLE_YEAR"] == c]
            cyc_h = (self.hetus[self.hetus["CYCLE_YEAR"] == c]
                     if "CYCLE_YEAR" in self.hetus.columns
                     else self.hetus)

            ep_per = cyc_m.groupby("occID").size()
            excl = excl_map.get(str(c), {})
            excl_rate = excl.get("Rate (%)", 0.0)

            slot_valid = ((1 - cyc_h[slot_present].isna().any(axis=1).mean())
                          * 100 if slot_present and len(cyc_h) > 0 else 0.0)

            wt = pd.to_numeric(cyc_m.get("WGHT_EPI", pd.Series(
                np.ones(len(cyc_m)))), errors="coerce").fillna(1.0)
            home = pd.to_numeric(cyc_m["AT_HOME"], errors="coerce")
            valid = home.notna()
            at_home_pct = ((wt[valid] * home[valid]).sum() / wt[valid].sum()
                           * 100 if valid.any() else 0.0)

            wday_pct = ((cyc_m["DAYTYPE"] == "Weekday").mean() * 100
                        if "DAYTYPE" in cyc_m.columns else 0.0)

            s2r = s2_main.get(c, 0)
            postr = post_resp.get(c, 0)
            poste = post_epi.get(c, 0)
            hrows = len(cyc_h)

            totals["s2"] += s2r
            totals["pre"] += s2r
            totals["post"] += postr
            totals["ep"] += poste
            totals["hetus"] += hrows

            rows.append({
                "Cycle": str(c),
                "Resp (Step 2)": f"{s2r:,}",
                "Resp (pre-filter)": f"{s2r:,}",
                "Resp (post-filter)": f"{postr:,}",
                "Excl. Rate": f"{excl_rate:.2f}%",
                "Total Episodes": f"{poste:,}",
                "Mean Eps/Resp": f"{ep_per.mean():.1f}",
                "Median Eps/Resp": f"{ep_per.median():.1f}",
                "HETUS Rows": f"{hrows:,}",
                "Slots Valid (%)": f"{slot_valid:.1f}%",
                "Wtd AT_HOME (%)": f"{at_home_pct:.1f}%",
                "Weekday (%)": f"{wday_pct:.1f}%",
                "Weekend (%)": f"{100 - wday_pct:.1f}%",
            })

        # Total row
        all_ep = self.merged.groupby("occID").size()
        total_excl_rate = (
            (totals["pre"] - totals["post"]) / totals["pre"] * 100
            if totals["pre"] > 0 else 0.0)
        rows.append({
            "Cycle": "Total",
            "Resp (Step 2)": f"{totals['s2']:,}",
            "Resp (pre-filter)": f"{totals['pre']:,}",
            "Resp (post-filter)": f"{totals['post']:,}",
            "Excl. Rate": f"{total_excl_rate:.2f}%",
            "Total Episodes": f"{len(self.merged):,}",
            "Mean Eps/Resp": f"{all_ep.mean():.1f}",
            "Median Eps/Resp": f"{all_ep.median():.1f}",
            "HETUS Rows": f"{len(self.hetus):,}",
            "Slots Valid (%)": "—",
            "Wtd AT_HOME (%)": "—",
            "Weekday (%)": "—",
            "Weekend (%)": "—",
        })

        self._rec("pass",
                  f"6.1 | Summary table: {len(rows) - 1} cycles + total row")
        summary_df = pd.DataFrame(rows)
        self.summary_data["summary_df"] = summary_df
        return summary_df

    # ── Section 7: 30-Minute Resolution Downsampling ────────────────────────────

    def validate_30min_downsampling(self) -> None:
        print("\n─── Section 7: 30-Minute Resolution Downsampling ─────────────────")
        if self.hetus_30min is None:
            print("  ⚠️  hetus_30min not loaded — Section 7 skipped")
            return

        _apply_dark()
        h30 = self.hetus_30min
        hw = self.hetus

        STRATA_LABELS = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
        STRATA_COLORS = {1: "#89b4fa", 2: "#f38ba8", 3: "#a6e3a1"}

        ACT_COLS_30 = [f"act30_{i:03d}" for i in range(1, 49)]
        HOM_COLS_30 = [f"hom30_{i:03d}" for i in range(1, 49)]
        SLOT_COLS_10 = [f"slot_{i:03d}" for i in range(1, 145)]

        act_cols_30_present = [c for c in ACT_COLS_30 if c in h30.columns]
        hom_cols_30_present = [c for c in HOM_COLS_30 if c in h30.columns]
        slot_cols_10_present = [c for c in SLOT_COLS_10 if c in hw.columns]

        act_ids = sorted(ACT_LABELS.keys())
        act_names = [ACT_LABELS[a] for a in act_ids]

        # ── 7a: Activity distribution comparison ──────────────────────────
        fig7a, axes = plt.subplots(1, 3, figsize=(21, 9), sharey=True)
        fig7a.suptitle(
            "Section 7a — Activity Distribution: 10-min vs 30-min by Day Type",
            color="#cdd6f4", fontsize=13, y=1.01)

        for ax, (sid, sname) in zip(axes, STRATA_LABELS.items()):
            mask_hw = (hw["DDAY_STRATA"] == sid
                       if "DDAY_STRATA" in hw.columns
                       else pd.Series(True, index=hw.index))
            hw_sub = hw[mask_hw]
            if len(hw_sub) > 0 and slot_cols_10_present:
                vals_10 = hw_sub[slot_cols_10_present].values.flatten()
                vals_10 = vals_10[~np.isnan(vals_10.astype(float))].astype(int)
                props_10 = np.array([np.mean(vals_10 == a) for a in act_ids])
            else:
                props_10 = np.zeros(len(act_ids))

            mask_h30 = (h30["DDAY_STRATA"] == sid
                        if "DDAY_STRATA" in h30.columns
                        else pd.Series(True, index=h30.index))
            h30_sub = h30[mask_h30]
            if len(h30_sub) > 0 and act_cols_30_present:
                arr_30 = h30_sub[act_cols_30_present].values.flatten()
                arr_30 = arr_30[~np.isnan(arr_30.astype(float))].astype(int)
                props_30 = np.array([np.mean(arr_30 == a) for a in act_ids])
            else:
                props_30 = np.zeros(len(act_ids))

            y = np.arange(len(act_ids))
            bar_h = 0.35
            ax.barh(y + bar_h / 2, props_10 * 100, bar_h,
                    color="#89b4fa", alpha=0.85, label="10-min")
            ax.barh(y - bar_h / 2, props_30 * 100, bar_h,
                    color=STRATA_COLORS[sid], alpha=0.85, label="30-min")

            ax.set_yticks(y)
            ax.set_yticklabels(act_names, fontsize=9)
            ax.set_xlabel("% of slots", color="#cdd6f4", fontsize=10)
            ax.set_title(sname, color="#cdd6f4", fontsize=11, pad=8)
            ax.legend(fontsize=8)
            ax.grid(axis="x", alpha=0.3)

        plt.tight_layout()
        self.plots_b64["7a_act_dist_30min"] = _b64(fig7a)
        print("  ✅ 7a: Activity distribution (10-min vs 30-min by stratum)")

        # ── 7b: AT_HOME daily rhythm ───────────────────────────────────────
        fig7b, ax = plt.subplots(figsize=(16, 5))
        fig7b.suptitle("Section 7b — AT_HOME Daily Rhythm at 30-min Resolution",
                       color="#cdd6f4", fontsize=13)

        slot_labels = []
        for i in range(48):
            total_min = 4 * 60 + i * 30
            hh = (total_min // 60) % 24
            mm = total_min % 60
            slot_labels.append(f"{hh:02d}:{mm:02d}" if mm == 0 else "")

        x = np.arange(48)
        for sid, sname in STRATA_LABELS.items():
            mask = (h30["DDAY_STRATA"] == sid
                    if "DDAY_STRATA" in h30.columns
                    else pd.Series(True, index=h30.index))
            sub = h30[mask]
            if len(sub) > 0 and hom_cols_30_present:
                rates = sub[hom_cols_30_present].mean().values * 100
                ax.plot(x, rates, color=STRATA_COLORS[sid], linewidth=2,
                        label=sname, marker="o", markersize=3)

        ax.set_xticks(x)
        ax.set_xticklabels(slot_labels, rotation=45, fontsize=7)
        ax.set_xlabel("30-min slot (04:00 AM origin)", color="#cdd6f4")
        ax.set_ylabel("AT_HOME rate (%)", color="#cdd6f4")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        self.plots_b64["7b_at_home_rhythm"] = _b64(fig7b)
        print("  ✅ 7b: AT_HOME daily rhythm (30-min by stratum)")

        # ── 7c: Activity heatmap ───────────────────────────────────────────
        fig7c, axes = plt.subplots(1, 3, figsize=(21, 7), sharey=True)
        fig7c.suptitle(
            "Section 7c — Activity Heatmap at 30-min Resolution (% of respondents)",
            color="#cdd6f4", fontsize=13, y=1.02)

        tick_pos = list(range(0, 48, 4))
        tick_lbl = []
        for t in tick_pos:
            total_min = 4 * 60 + t * 30
            hh = (total_min // 60) % 24
            tick_lbl.append(f"{hh:02d}h")

        for ax, (sid, sname) in zip(axes, STRATA_LABELS.items()):
            mask = (h30["DDAY_STRATA"] == sid
                    if "DDAY_STRATA" in h30.columns
                    else pd.Series(True, index=h30.index))
            sub = h30[mask]

            mat = np.zeros((len(act_ids), 48))
            if len(sub) > 0 and act_cols_30_present:
                arr = sub[act_cols_30_present].values.astype(float)
                for ai, act_id in enumerate(act_ids):
                    mat[ai] = np.nanmean(arr == act_id, axis=0) * 100

            im = ax.imshow(mat, aspect="auto", cmap="plasma",
                           interpolation="nearest", vmin=0)
            ax.set_yticks(range(len(act_ids)))
            ax.set_yticklabels(act_names, fontsize=8)
            ax.set_xlabel("30-min slot", color="#cdd6f4", fontsize=9)
            ax.set_title(sname, color="#cdd6f4", fontsize=11, pad=8)
            ax.set_xticks(tick_pos)
            ax.set_xticklabels(tick_lbl, fontsize=8)
            plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02,
                         label="% of respondents")

        plt.tight_layout()
        self.plots_b64["7c_act_heatmap"] = _b64(fig7c)
        print("  ✅ 7c: Activity heatmap (30-min, 3 panels by stratum)")

    # ── HTML Report ─────────────────────────────────────────────────────────────

    def build_html_report(self) -> str:
        n_pass = len(self.results["pass"])
        n_warn = len(self.results["warn"])
        n_fail = len(self.results["fail"])
        total = n_pass + n_warn + n_fail
        pct_ok = round(100 * n_pass / total) if total else 0

        chart_sections = [
            ("1_row_counts",
             "Section 1 — Row Count Preservation"),
            ("2_merge_integrity",
             "Section 2 — Merge Key Integrity"),
            ("3a_daytype",
             "Section 3a — DAYTYPE Distribution"),
            ("3b_hour_of_day",
             "Section 3b — Episode Start Times (HOUR_OF_DAY)"),
            ("3c_timeslot",
             "Section 3c — HETUS Slot Distribution (TIMESLOT_10)"),
            ("3d_dday_strata",
             "Section 3d — DDAY_STRATA Distribution per Cycle"),
            ("4a_activity_heatmap",
             "Section 4a — Activity Heatmap (14 Activities × 144 Slots)"),
            ("4b_at_home_curve",
             "Section 4b — AT_HOME Rate Curve Across 144 Slots"),
            ("4c_slot_completeness",
             "Section 4c — HETUS Slot Completeness by Cycle"),
            ("5a_activity_dist",
             "Section 5a — Weighted Activity Distribution per Cycle"),
            ("5b_at_home_rate",
             "Section 5b — Weighted AT_HOME Rate per Cycle"),
            ("5c_demographics",
             "Section 5c — Demographic Distributions: Step 2 vs. Step 3"),
            ("5d_episodes_per_resp",
             "Section 5d — Episodes per Respondent by Cycle"),
            ("7a_act_dist_30min",
             "Section 7a — Activity Distribution: 10-min vs 30-min by Day Type"),
            ("7b_at_home_rhythm",
             "Section 7b — AT_HOME Daily Rhythm at 30-min Resolution"),
            ("7c_act_heatmap",
             "Section 7c — Activity Heatmap at 30-min Resolution"),
        ]

        charts_html = ""
        for key, label in chart_sections:
            if key in self.plots_b64:
                charts_html += f"""
        <section class="chart-section" id="{key}">
          <h2>{label}</h2>
          <div class="chart-wrap">
            <img src="data:image/png;base64,{self.plots_b64[key]}"
                 alt="{label}">
          </div>
        </section>"""

        # Summary table HTML
        summary_df = self.summary_data.get("summary_df")
        if summary_df is not None:
            th = "".join(f"<th>{col}</th>" for col in summary_df.columns)
            trs = ""
            for _, row in summary_df.iterrows():
                cls = ' class="total-row"' if row["Cycle"] == "Total" else ""
                tds = "".join(f"<td>{v}</td>" for v in row.values)
                trs += f"<tr{cls}>{tds}</tr>"
            summary_html = f"""
        <section class="chart-section" id="summary-table">
          <h2>Section 6 — Dataset Statistics Summary Table</h2>
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
            icon = ("✅" if level == "pass"
                    else ("❌" if level == "fail" else "⚠️"))
            items = self.results[level]
            if not items:
                return f"<li class='badge {level}'>{icon} None</li>"
            return "".join(
                f"<li class='badge {level}'>{icon} {m}</li>"
                for m in items)

        nav_links = "".join(
            f'<a href="#{k}">{lbl.split("—")[0].strip()}</a>'
            for k, lbl in chart_sections
            if k in self.plots_b64)
        nav_links += '<a href="#summary-table">Section 6</a>'
        if "7a_act_dist_30min" in self.plots_b64:
            nav_links += '<a href="#7a_act_dist_30min">Section 7</a>'

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSS Step 3 — Merge &amp; Temporal Feature Derivation Validation</title>
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
             padding:4px 10px; border-radius:6px;
             transition:background 0.2s,color 0.2s; }}
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
    .badge {{ padding:8px 14px; border-radius:8px; font-size:0.85rem;
              line-height:1.4; }}
    .badge.pass {{ background:#1c2e22; border:1px solid #2d5a35;
                   color:var(--green); }}
    .badge.warn {{ background:#2e2a1c; border:1px solid #5a4e1f;
                   color:var(--yellow); }}
    .badge.fail {{ background:#2e1c1e; border:1px solid #5a2428;
                   color:var(--red); }}
    .chart-section {{ background:var(--surface); border:1px solid var(--border);
                      border-radius:14px; padding:24px; margin-bottom:28px; }}
    .chart-section h2 {{ font-size:1.0rem; color:var(--accent);
                         margin-bottom:16px; padding-bottom:8px;
                         border-bottom:1px solid var(--border); }}
    .chart-wrap {{ text-align:center; }}
    .chart-wrap img {{ max-width:100%; height:auto; border-radius:8px; }}
    .pipeline-section {{ background:var(--surface); border:1px solid var(--border);
                         border-radius:14px; padding:24px; margin-bottom:28px; }}
    .pipeline-section h2 {{ font-size:1.0rem; color:var(--accent);
                             margin-bottom:16px; padding-bottom:8px;
                             border-bottom:1px solid var(--border); }}
    .pipeline-pre {{ font-family:'Courier New',Consolas,monospace;
                     font-size:0.78rem; color:var(--subtext); white-space:pre;
                     overflow-x:auto; background:var(--surface2); padding:16px;
                     border-radius:8px; border:1px solid var(--border);
                     line-height:1.5; }}
    .table-wrap {{ overflow-x:auto; }}
    .summary-table {{ width:100%; border-collapse:collapse;
                      font-size:0.82rem; }}
    .summary-table th {{ background:var(--surface2); color:var(--accent);
                          padding:10px 12px; text-align:left;
                          border-bottom:2px solid var(--border);
                          font-size:0.78rem; white-space:nowrap; }}
    .summary-table td {{ padding:8px 12px;
                          border-bottom:1px solid var(--border);
                          color:var(--text); white-space:nowrap; }}
    .summary-table tr:hover td {{ background:var(--surface2); }}
    .summary-table tr.total-row td {{ font-weight:700; color:var(--accent);
                                       border-top:2px solid var(--border); }}
    footer {{ text-align:center; padding:20px; font-size:0.78rem;
              color:var(--subtext); border-top:1px solid var(--border);
              margin-top:10px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>GSS Step 3 — Merge &amp; Temporal Feature Derivation
          Validation Report</h1>
      <p>Validates merged_episodes.csv and hetus_wide.csv
         against Step 2 reference files · Cycles 2005, 2010, 2015, 2022</p>
    </div>
    <p style="font-size:0.78rem;color:var(--subtext)">Generated: {ts}</p>
  </header>
  <nav>
    <a href="#pipeline-overview">Pipeline Overview</a>
    <a href="#scorecard">Scorecard</a>
    {nav_links}
  </nav>
  <main>
    <!-- Pipeline Overview -->
    <section class="pipeline-section" id="pipeline-overview">
      <h2>Pipeline Overview — Step 3: Merge &amp; Temporal Feature Derivation</h2>
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
      <h2>❌ Failures</h2>
      <ul class="badge-list">{_badge_list("fail")}</ul>
    </div>
    <div class="findings">
      <h2>⚠️ Warnings</h2>
      <ul class="badge-list">{_badge_list("warn")}</ul>
    </div>
    <div class="findings">
      <h2>✅ Passed</h2>
      <ul class="badge-list">{_badge_list("pass")}</ul>
    </div>
    {charts_html}
    {summary_html}
  </main>
  <footer>
    Occupancy Modeling Pipeline · Step 3 Merge &amp; Temporal Feature
    Derivation Validation ·
    Inputs: outputs_step2/ + outputs_step3/merged_episodes.csv +
    outputs_step3/hetus_wide.csv ·
    Output: outputs_step3/step3_validation_report.html ·
    Generated: {ts}
  </footer>
</body>
</html>"""

        out_path = os.path.join(self.step3_dir, "step3_validation_report.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML Report saved → {out_path}")
        return out_path

    # ── Run All ─────────────────────────────────────────────────────────────────

    def run_all(self) -> None:
        _apply_dark()
        print("=" * 60)
        print("Step 3 — Merge & Temporal Feature Derivation Validation")
        print("=" * 60)
        self.validate_row_counts()
        self.validate_merge_integrity()
        self.validate_derived_features()
        self.validate_hetus_slots()
        self.validate_cross_cycle_consistency()
        self.generate_summary_table()
        self.validate_30min_downsampling()
        self.build_html_report()
        n_p = len(self.results["pass"])
        n_w = len(self.results["warn"])
        n_f = len(self.results["fail"])
        print(f"\n{'=' * 60}")
        print(f"Validation complete: {n_p} PASS / {n_w} WARN / {n_f} FAIL")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    GSSMergeValidator("outputs_step2", "outputs_step3").run_all()
