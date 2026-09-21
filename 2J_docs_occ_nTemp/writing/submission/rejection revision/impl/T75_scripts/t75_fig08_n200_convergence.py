"""
T75 -- WP11 Figure 8: convergence of the 2022->2030 change estimate with
sample size N, for the four Montreal archetype cells scored by T28's B4
convergence check (t28_check.py::b4_convergence).

INPUT (already-accepted, not recomputed): T28's own
`out/t28_b4_convergence.csv`. T54 (job 1329670) already validated T28's B0/B1/
B2/B5 bands PASS and its own hand-arithmetic control (control 4) agreed with
t28_check.py's `_paired_t_ci()` to 5-6 significant figures. B3 and B4 are
REPORT-type (no PASS/FAIL band, CSV only) -- T54's own verdict block says so
explicitly ("B4=REPORT (convergence curve, CSV only, no PASS/FAIL band)").
This script does not recompute any mean/halfwidth -- it only reads and plots
the numbers T28 already wrote.

DEFINITION OF "CONVERGENCE" USED (read directly from t28_check.py, not
invented): b4_convergence() takes the 200-household pool per cell, computes
each metric's mean and paired-t 95% CI half-width on the FULL 200 (row with
N=200 in the CSV: `_paired_t_ci()`, a parametric Student-t CI), THEN, for
each subsample size N in {10,20,50,100,150}, draws 1000 samples of size N
WITHOUT replacement from the same 200 households, computes each draw's mean,
and reports halfwidth = (97.5th pctile - 2.5th pctile)/2 of the 1000 draw
means (a nonparametric percentile CI on the *sampling distribution* of the
subsample mean). These are two DIFFERENT statistics that happen to share a
"halfwidth" column name:
  - N=200 row: parametric Student-t CI half-width on the actual full sample.
  - N=10..150 rows: percentile spread of 1000 bootstrap-style subsample means.
This means the N=200 point is not simply "the limit of the N<200 curve" --
it is measuring something formally different. The real data show a
non-monotonic artifact: halfwidth shrinks N=10->150 then JUMPS UP again at
N=200 for many metrics (confirmed by direct inspection of the CSV before
writing this script, not invented). This script does NOT hide or smooth this
-- the N=200 point is drawn with a distinct marker/color and a vertical
guide line, and the figure caption states the method switch explicitly.

SCOPE: plots only the `<metric>_delta_2022to2030` variant (6 of the CSV's 18
metric labels) -- the 2022->2030 CHANGE, which is what this project's own
"quotable" convention (2J plan, 2026-09-18 entries (cg)-(cs)) actually scores
and quotes in the manuscript. The `<metric>@2022` / `<metric>@2030` LEVEL
rows exist in the same source CSV (12 more metric labels) but are not
plotted here -- see the task's IMPL doc "Decisions" section for why.

Output:
  out/figures/fig08_n200_convergence.png
  out/figures/fig08_n200_convergence.csv   (exactly the rows plotted, plus a
                                             ci_method column distinguishing
                                             the two statistics above)
  logs/t75_run_meta.json
"""
import csv
import json
import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

T75_ROOT = "/speed-scratch/o_iseri/2J_revision/T75"
T28_CSV = "/speed-scratch/o_iseri/2J_revision/T28/out/t28_b4_convergence.csv"
T54_REPORT = "/speed-scratch/o_iseri/2J_revision/T54/logs/t54_t28_report.txt"

OUT_DIR = os.path.join(T75_ROOT, "out", "figures")
LOG_DIR = os.path.join(T75_ROOT, "logs")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

PNG_PATH = os.path.join(OUT_DIR, "fig08_n200_convergence.png")
CSV_PATH = os.path.join(OUT_DIR, "fig08_n200_convergence.csv")
META_PATH = os.path.join(LOG_DIR, "t75_run_meta.json")

DPI = 600
CELLS = ["SingleD__Montreal_6A", "OtherDwelling__Montreal_6A",
         "MidRise__Montreal_6A", "HighRise__Montreal_6A"]
CELL_LABELS = {"SingleD__Montreal_6A": "SingleD",
               "OtherDwelling__Montreal_6A": "OtherDwelling",
               "MidRise__Montreal_6A": "MidRise",
               "HighRise__Montreal_6A": "HighRise"}
CELL_COLORS = {"SingleD__Montreal_6A": "#1b7837",
               "OtherDwelling__Montreal_6A": "#762a83",
               "MidRise__Montreal_6A": "#2166ac",
               "HighRise__Montreal_6A": "#b2182b"}

# base_metric -> (label, unit)
METRICS = [
    ("elec_facility_kWh", "annual electricity, whole building (kWh)"),
    ("mean_daily_peak_kW", "mean daily peak load (kW)"),
    ("mean_peak_hour", "mean hour-of-day of daily peak (h)"),
    ("load_factor", "load factor (mean/max, unitless 0-1)"),
    ("midday_share", "share of annual kWh in hours 9-17 (unitless 0-1)"),
    ("evening_ramp_kW_mean", "mean evening ramp, hour17-hour14 (kW)"),
]
N_VALUES = [10, 20, 50, 100, 150, 200]


def main():
    t0 = time.time()
    notes = []

    # ------------------------------------------------------------------
    # 0. Precondition: T54's own verdict on T28's B4 output must be read
    #    and recorded before any number from t28_b4_convergence.csv is used.
    # ------------------------------------------------------------------
    if not os.path.exists(T54_REPORT):
        print("FATAL: T54 report not found, refusing to build figure without "
              "its precondition check.", file=sys.stderr)
        sys.exit(2)
    with open(T54_REPORT, encoding="utf-8") as f:
        t54_text = f.read()
    t54_verdict_lines = [ln for ln in t54_text.splitlines() if ln.startswith("VERDICT:")]
    b4_line = [ln for ln in t54_verdict_lines if ln.startswith("VERDICT: B4")]
    if not b4_line or "REPORT" not in b4_line[0]:
        print(f"FATAL: T54's own B4 verdict line not found or not REPORT as "
              f"expected: {b4_line}", file=sys.stderr)
        sys.exit(3)
    print(f"[precondition] T54 verdict lines: {t54_verdict_lines}")
    t54_all_pass = all(
        ("PASS" in ln or "REPORT" in ln) for ln in t54_verdict_lines
    )
    print(f"[precondition] T54 all bands PASS or REPORT (no FAIL): {t54_all_pass}")
    if not t54_all_pass:
        print("FATAL: T54 reported a non-PASS/REPORT band -- stopping, this "
              "figure must not be built.", file=sys.stderr)
        sys.exit(4)

    # ------------------------------------------------------------------
    # 1. Load T28's convergence CSV (already-accepted data, not recomputed)
    # ------------------------------------------------------------------
    df = pd.read_csv(T28_CSV)
    assert list(df.columns) == ["cell", "metric", "N", "mean", "halfwidth"], \
        f"unexpected columns: {list(df.columns)}"
    n_rows_total = len(df)
    cells_seen = sorted(df["cell"].unique().tolist())
    metrics_seen = sorted(df["metric"].unique().tolist())
    n_values_seen = sorted(df["N"].unique().tolist())
    print(f"[data] {n_rows_total} rows, {len(cells_seen)} cells, "
          f"{len(metrics_seen)} metric labels, N values {n_values_seen}")
    assert cells_seen == sorted(CELLS), f"cell mismatch: {cells_seen}"
    assert n_values_seen == N_VALUES, f"N mismatch: {n_values_seen}"

    delta_labels = [f"{m}_delta_2022to2030" for m, _ in METRICS]
    level_labels = [f"{m}@{y}" for m, _ in METRICS for y in (2022, 2030)]
    all_expected = set(delta_labels) | set(level_labels)
    assert set(metrics_seen) == all_expected, (
        f"metric label set mismatch. Missing: {all_expected - set(metrics_seen)}; "
        f"Extra: {set(metrics_seen) - all_expected}"
    )

    # ------------------------------------------------------------------
    # 2. Row-count / completeness control: every (cell, delta-metric, N)
    #    combination expected must be present exactly once.
    # ------------------------------------------------------------------
    plot_df = df[df["metric"].isin(delta_labels)].copy()
    expected_n_plot_rows = len(CELLS) * len(delta_labels) * len(N_VALUES)
    completeness_ok = len(plot_df) == expected_n_plot_rows
    missing_combos = []
    for cell in CELLS:
        for label in delta_labels:
            for n in N_VALUES:
                match = plot_df[(plot_df.cell == cell) & (plot_df.metric == label)
                                 & (plot_df.N == n)]
                if len(match) != 1:
                    missing_combos.append(
                        {"cell": cell, "metric": label, "N": n, "n_found": len(match)})
    print(f"[control: row-count/completeness] expected {expected_n_plot_rows} "
          f"delta rows, found {len(plot_df)}, missing/duplicate combos: "
          f"{len(missing_combos)}")

    level_rows_in_source = len(df[df["metric"].isin(level_labels)])
    notes.append(
        f"Source CSV also carries {level_rows_in_source} LEVEL rows "
        f"(<metric>@2022, <metric>@2030) not plotted in this figure -- see "
        f"IMPL doc Decisions. Full source data (levels + deltas) is at "
        f"{T28_CSV} on the cluster, unmodified."
    )

    # ------------------------------------------------------------------
    # 3. Seen-working control: hand-pick 2 (cell, metric, N) rows directly
    #    from the dataframe (independent boolean mask, not the plotting path)
    #    and record their raw values for the manager to cross-check against
    #    both the CSV and the rendered figure.
    # ------------------------------------------------------------------
    seen_working = []
    for cell, metric, n in [
        ("SingleD__Montreal_6A", "elec_facility_kWh_delta_2022to2030", 200),
        ("MidRise__Montreal_6A", "mean_peak_hour_delta_2022to2030", 100),
    ]:
        row = df[(df.cell == cell) & (df.metric == metric) & (df.N == n)]
        assert len(row) == 1, f"expected exactly 1 row for {cell},{metric},{n}"
        r = row.iloc[0]
        seen_working.append({
            "cell": cell, "metric": metric, "N": int(n),
            "mean": float(r["mean"]), "halfwidth": float(r["halfwidth"]),
        })
        print(f"[control: seen-working] {cell} {metric} N={n} -> "
              f"mean={r['mean']!r} halfwidth={r['halfwidth']!r}")

    # ------------------------------------------------------------------
    # 4. Non-monotonic N=200 finding: detect and record which (cell,metric)
    #    combos have halfwidth(N=200) > halfwidth(N=150), i.e. the
    #    method-switch jump, so the figure's own visual flag is data-driven,
    #    not asserted from memory of the earlier reconnaissance.
    # ------------------------------------------------------------------
    jump_combos = []
    for cell in CELLS:
        for label in delta_labels:
            h150 = plot_df[(plot_df.cell == cell) & (plot_df.metric == label)
                            & (plot_df.N == 150)]["halfwidth"].iloc[0]
            h200 = plot_df[(plot_df.cell == cell) & (plot_df.metric == label)
                            & (plot_df.N == 200)]["halfwidth"].iloc[0]
            if h200 > h150:
                jump_combos.append({"cell": cell, "metric": label,
                                     "halfwidth_n150": float(h150),
                                     "halfwidth_n200": float(h200)})
    print(f"[finding] {len(jump_combos)} / {len(CELLS) * len(delta_labels)} "
          f"(cell, metric) combos show halfwidth(N=200) > halfwidth(N=150) "
          f"-- the parametric-vs-bootstrap method switch at N=200.")

    # ------------------------------------------------------------------
    # 5. Plot: 2x3 grid, one panel per base metric, one line per cell,
    #    N=10..150 solid circles (bootstrap-subsample percentile CI),
    #    N=200 distinct star marker + vertical dashed guide line
    #    (parametric full-sample Student-t CI -- different statistic).
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 8.2))
    axes = axes.ravel()
    for i, (base_metric, unit_label) in enumerate(METRICS):
        ax = axes[i]
        label = f"{base_metric}_delta_2022to2030"
        for cell in CELLS:
            sub = plot_df[(plot_df.cell == cell) & (plot_df.metric == label)].sort_values("N")
            n_lt200 = sub[sub.N < 200]
            n_eq200 = sub[sub.N == 200]
            ax.plot(n_lt200["N"], n_lt200["halfwidth"], "-o",
                    color=CELL_COLORS[cell], label=CELL_LABELS[cell],
                    markersize=4, linewidth=1.3)
            ax.plot(n_eq200["N"], n_eq200["halfwidth"], "*",
                    color=CELL_COLORS[cell], markersize=11,
                    markeredgecolor="black", markeredgewidth=0.5, zorder=5)
        ax.axvline(200, color="grey", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.set_title(unit_label, fontsize=9)
        ax.set_xlabel("subsample size N", fontsize=8)
        ax.set_ylabel("95% CI half-width", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_xticks(N_VALUES)

    handles, labels_ = axes[0].get_legend_handles_labels()
    star_proxy = plt.Line2D([0], [0], marker="*", color="grey", linestyle="None",
                             markersize=11, markeredgecolor="black",
                             label="N=200 (parametric t-CI, full sample -- different statistic, see caption)")
    fig.tight_layout(rect=[0.02, 0.10, 0.98, 0.83])
    fig.legend(handles + [star_proxy], labels_ + [star_proxy.get_label()],
               loc="lower center", ncol=3, fontsize=7.5, frameon=False,
               bbox_to_anchor=(0.5, 0.005))
    fig.suptitle(
        "Figure 8. Convergence of the 2022->2030 change estimate with subsample size N\n"
        "(4 Montreal archetype cells; N=200 is the sample size used throughout the paper)",
        fontsize=10.5, y=0.985)
    fig.text(0.5, 0.885,
              "N=10-150: percentile CI of 1000 subsample-mean draws from the 200-household pool (no replacement).\n"
              "N=200: parametric Student-t CI on the full pool -- a different statistic (source: t28_check.py b4_convergence()).\n"
              "Non-monotonic jumps at N=200 reflect this method switch, not a real widening of uncertainty.",
              ha="center", va="top", fontsize=6.8, style="italic", color="#333333")
    fig.savefig(PNG_PATH, dpi=DPI)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 6. Read back the saved PNG's dpi metadata (do not trust the kwarg)
    # ------------------------------------------------------------------
    with Image.open(PNG_PATH) as im:
        dpi_readback = im.info.get("dpi")
        px_size = im.size

    # ------------------------------------------------------------------
    # 7. Write companion CSV (exactly the plotted rows + ci_method column)
    # ------------------------------------------------------------------
    plot_df = plot_df.copy()
    plot_df["ci_method"] = plot_df["N"].apply(
        lambda n: "parametric_student_t_full_sample" if n == 200
        else "bootstrap_subsample_percentile_1000draws")
    plot_df.sort_values(["cell", "metric", "N"]).to_csv(CSV_PATH, index=False)

    # ------------------------------------------------------------------
    # 8. Write run_meta.json
    # ------------------------------------------------------------------
    meta = {
        "task": "T75",
        "figure": "fig08_n200_convergence",
        "elapsed_sec": round(time.time() - t0, 2),
        "dpi_kwarg": DPI,
        "dpi_readback_from_png": dpi_readback,
        "png_pixel_size": list(px_size),
        "input_csv": T28_CSV,
        "input_csv_rows_total": n_rows_total,
        "input_csv_cells": cells_seen,
        "input_csv_metric_labels": metrics_seen,
        "input_csv_N_values": n_values_seen,
        "t54_precondition": {
            "report_path": T54_REPORT,
            "verdict_lines": t54_verdict_lines,
            "all_bands_pass_or_report": t54_all_pass,
            "note": "T54 verdict read and confirmed BEFORE any t28_b4_convergence.csv "
                    "number was used in this script. B0/B1/B2/B5 = PASS, B3/B4 = REPORT "
                    "(no PASS/FAIL band; CSV-only report type by t28_check.py's own design).",
        },
        "t48_relevance_judgement": {
            "files_checked": [
                "/speed-scratch/o_iseri/2J_revision/T48/pub_loadshape/peak_shift_summary.csv",
                "/speed-scratch/o_iseri/2J_revision/T48/pub_loadshape/loadshape_profiles.csv",
                "/speed-scratch/o_iseri/2J_revision/T48/pub_loadshape/peak_hours.csv",
            ],
            "columns_seen": {
                "peak_shift_summary.csv": "cell,year,equip_bldg_shift,equip_zone_shift,light_bldg_shift,light_zone_shift",
                "loadshape_profiles.csv": "cell,year,arm,hour_of_day,equip_bldg_W,equip_zone_W,light_bldg_W,light_zone_W,facility_W,n_hh",
                "peak_hours.csv": "cell,year,arm,equip_bldg_peak_h,equip_zone_peak_h,light_bldg_peak_h,light_zone_peak_h,n_hh",
            },
            "verdict": "EXCLUDED. This is a Step-9 activity-vs-baseline schedule peak-hour-shift "
                       "check (n_hh=50 fixed per row, arm=activity/baseline, equip/light building/zone "
                       "peak-hour columns) -- confirmed by the scripts in T48/scripts/ "
                       "(step9_validate_full.py, step9_loadshape_aggregate.py, t48_helpers.py), "
                       "matching this project's Step-9 A6 peak-shift work, NOT a sample-size "
                       "N=10..200 convergence study. No column here is 'N' or 'halfwidth'. "
                       "Unrelated to Figure 8's story; shares only the task NUMBER '48' with an "
                       "earlier candidate guess in plan entry (di), not the content. Excluded "
                       "entirely from this figure.",
        },
        "figure_scope": {
            "plotted_metric_labels": delta_labels,
            "n_plotted_rows": int(len(plot_df)),
            "excluded_level_metric_labels": level_labels,
            "n_excluded_level_rows": int(level_rows_in_source),
            "reason": "Figure headlines the 2022->2030 CHANGE half-width (this project's "
                      "'quotable' convention), not the raw 2022/2030 level half-widths. "
                      "Level rows remain in the source CSV, untouched, for any future figure.",
        },
        "controls": {
            "row_count_completeness": {
                "expected_delta_rows": expected_n_plot_rows,
                "found_delta_rows": int(len(plot_df)),
                "missing_or_duplicate_combos": missing_combos,
                "pass": completeness_ok and len(missing_combos) == 0,
            },
            "seen_working": seen_working,
        },
        "finding_n200_method_switch": {
            "description": "N=200 row uses a parametric Student-t CI on the real full "
                            "200-household sample; N=10-150 rows use a percentile CI of "
                            "1000 bootstrap-style subsample means drawn without replacement "
                            "from that same 200. These are different statistics. Verified "
                            "directly from t28_check.py's b4_convergence()/_paired_t_ci() "
                            "source (T28_scripts/t28_check.py:353-380, 288-300).",
            "n_combos_with_halfwidth_n200_gt_n150": len(jump_combos),
            "n_combos_total": len(CELLS) * len(delta_labels),
            "examples": jump_combos[:6],
        },
        "notes": notes,
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[done] png={PNG_PATH} dpi_readback={dpi_readback} "
          f"px={px_size} elapsed={meta['elapsed_sec']}s")
    print(f"[done] csv={CSV_PATH} rows={len(plot_df)}")
    print(f"[done] meta={META_PATH}")


if __name__ == "__main__":
    main()
