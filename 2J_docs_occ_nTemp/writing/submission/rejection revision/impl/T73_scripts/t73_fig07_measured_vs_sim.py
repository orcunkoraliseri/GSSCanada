#!/usr/bin/env python3
"""
T73 -- WP11 Figure 7: measured (IESO) vs. simulated 2022 daily-shape metrics, REBUILT runs.

Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/2026-09-21_T73_wp11_figure7_measured_vs_sim.md
Implementation doc: impl/2026-09-21_T73_wp11_figure7_measured_vs_sim.md (same file, filled in as work went)

Input (read-only, ACCEPTED by the manager, NOTHING recomputed here):
  T70/out/sim_vs_measured_toronto_2022_shape_rebuilt.csv

REAL FINDING this script's design had to reconcile (see task doc Decisions for full reasoning):
  (1) The task brief assumes an hourly (24-point) load curve exists in T70's output. It does not.
      T70's own script (t70_sim_vs_measured_rebuilt.py) computes an hourly `profile_rows` list
      inside compute_slice_outputs() but the variable is captured as `_profile_rows` (underscore,
      discarded) in main() and NEVER written to any CSV -- confirmed by reading the script, not
      inferred. The only saved outputs are scalar per-(period,daytype,series,calendar,scope) SHAPE
      metrics: max_kwh_per_premise, load_factor, peak_to_avg, midday_share, mean_peak_hour. This
      figure plots those five metrics across period x daytype cells -- not an hourly curve --
      because recomputing the hourly profile from raw run files would violate the task doc's
      explicit "do not recompute anything" instruction.
  (2) `max_kwh_per_premise`'s SIM side is NOT on the same physical unit as its MEASURED side, even
      though both share one column name. Confirmed by reading T70's script: the sim series is
      scale-free normalized (each household run divided by its OWN annual mean before aggregation,
      docstring line ~383-390), so sim `max_kwh_per_premise` is a dimensionless ratio (order ~2),
      while measured `max_kwh_per_premise` is read straight from T02/out/ieso_metrics.csv with NO
      such normalization (independently confirmed here by reading that file directly: its
      full_year mean_kwh_per_premise is ~0.82-0.88, not ~1.0, so it is real kWh/premise, not a
      normalized ratio). T15/T70 already made the accepted decision to keep this column in the
      join despite this mismatch (T70 script comment: "max_kwh_per_premise KEPT... task text names
      only mean_kwh_per_premise for removal"). This script does not re-litigate that decision, but
      it never plots the two sides as if they were unit-comparable: the sim bar in that one panel
      is hatched and the panel title says explicitly "NOT unit-comparable" (same hatch/grey
      convention T71 used for NOT_EVALUABLE values).
  load_factor, peak_to_avg, midday_share and mean_peak_hour ARE scale-invariant ratios/positions
  (dividing a series by a constant does not change mean/max, max/mean, or which hour is the peak),
  so those four are genuinely comparable sim-vs-measured and are plotted as ordinary paired bars.

Headline scope (documented decision, not an accidental drop -- see completeness control):
  calendar='eplus' (T70's own primary calendar: "the day type the occupancy schedule actually ran
  against", confirmed by that script's own comment), series='facility' (whole-building electricity,
  the physically meaningful series to compare against IESO's grid-metered load), measured_scope=
  'Toronto' (the local, most direct comparison; 'Ontario' is a broader province-level companion
  already in the CSV, not re-plotted here), period restricted to T70's own headline 4-period set
  ['shoulder','winter','summer','full_year'] -- literally the prefix order T70's own script uses
  for period_order before appending the 12 individual months -- excluding the 12-month breakdown
  (too fine-grained for one figure; the completeness control below states this explicitly rather
  than silently dropping rows).
"""
import os
import json
import time
import traceback

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# --------------------------------------------------------------------------------------------
T70_DIR = "/speed-scratch/o_iseri/2J_revision/T70/out"
OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T73/out/figures"
LOG_DIR = "/speed-scratch/o_iseri/2J_revision/T73/logs"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

JOIN_CSV = os.path.join(T70_DIR, "sim_vs_measured_toronto_2022_shape_rebuilt.csv")

DPI = 600
FIG_WIDTH_IN = 7.0

CALENDAR = "eplus"
SERIES = "facility"
SCOPE = "Toronto"
PERIOD_ORDER = ["shoulder", "winter", "summer", "full_year"]
DAYTYPE_ORDER = ["weekday", "weekend", "holiday"]
COMBOS = [(p, d) for p in PERIOD_ORDER for d in DAYTYPE_ORDER]  # 12, T70's own iteration order

METRICS = [
    ("load_factor", "Load factor\n(mean load / peak load, fraction 0-1)", "Load factor", False),
    ("peak_to_avg", "Peak-to-average ratio\n(dimensionless)", "Peak-to-average ratio", False),
    ("midday_share", "Midday (hour-ending 10-17) share\nof daily energy (fraction 0-1)", "Midday share", False),
    ("mean_peak_hour", "Mean hour of daily peak\n(hour-ending, 1-24)", "Mean peak hour", False),
    ("max_kwh_per_premise", "Max per-premise load\n(units NOT comparable -- see caption)",
     "Max per-premise load (NOT unit-comparable)", True),
]

RUN_META = {"figure": {}, "seen_working_control": {}, "row_count_control": {}, "notes": []}


def log(msg):
    print(f"[T73] {msg}", flush=True)


def save_fig(fig, name, caption_note=""):
    png_path = os.path.join(OUT_DIR, f"{name}.png")
    fig.savefig(png_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    im = Image.open(png_path)
    dpi_meta = im.info.get("dpi", (None, None))
    px_w, px_h = im.size
    width_in = px_w / dpi_meta[0] if dpi_meta[0] else None
    height_in = px_h / dpi_meta[1] if dpi_meta[1] else None
    meta = {
        "png_path": png_path, "px_width": px_w, "px_height": px_h,
        "dpi_x": dpi_meta[0], "dpi_y": dpi_meta[1],
        "width_in": width_in, "height_in": height_in,
        "note": caption_note,
    }
    RUN_META["figure"] = meta
    log(f"saved {name}: {px_w}x{px_h}px, dpi={dpi_meta}, width_in={width_in}")
    return meta


def seen_working_control(full_df):
    """Independently re-read one (period, daytype, calendar, series, scope, metric) cell via a
    fresh boolean-mask read, isolated from build_plot_frame() below (separate code path)."""
    cell = dict(period="shoulder", daytype="weekday", calendar=CALENDAR, series=SERIES,
                measured_scope=SCOPE, metric="max_kwh_per_premise")
    mask = ((full_df["period"] == cell["period"]) & (full_df["daytype"] == cell["daytype"]) &
            (full_df["calendar"] == cell["calendar"]) & (full_df["series"] == cell["series"]) &
            (full_df["measured_scope"] == cell["measured_scope"]) &
            (full_df["metric"] == cell["metric"]))
    row = full_df[mask]
    hand_sim = float(row.iloc[0]["sim"]) if len(row) == 1 else None
    hand_measured = float(row.iloc[0]["measured"]) if len(row) == 1 else None
    return {
        "cell": cell,
        "hand_read_sim": hand_sim,
        "hand_read_measured": hand_measured,
        "n_rows_matched": int(len(row)),
    }


def build_plot_frame(full_df):
    """Filter to the headline scope and pivot -- separate code path from seen_working_control()."""
    sub = full_df[(full_df["calendar"] == CALENDAR) & (full_df["series"] == SERIES) &
                   (full_df["measured_scope"] == SCOPE) & (full_df["period"].isin(PERIOD_ORDER))]
    return sub.copy()


def main():
    t0 = time.time()
    log(f"reading {JOIN_CSV}")
    full_df = pd.read_csv(JOIN_CSV)
    log(f"full join CSV: {len(full_df)} rows, columns={list(full_df.columns)}")

    # -- seen-working control (independent re-read) --
    swc = seen_working_control(full_df)
    RUN_META["seen_working_control"] = swc
    log(f"seen-working control: {json.dumps(swc, default=str)}")

    # -- row-count / completeness control --
    all_combos = full_df[["period", "daytype"]].drop_duplicates()
    n_all_combos = len(all_combos)
    headline_sub = build_plot_frame(full_df)
    headline_combos = headline_sub[["period", "daytype"]].drop_duplicates()
    n_headline_combos_present = len(headline_combos)
    expected_headline_combos = set(COMBOS)
    present_headline_combos = set(zip(headline_combos["period"], headline_combos["daytype"]))
    missing_from_figure = expected_headline_combos - present_headline_combos
    extra_in_data_not_in_figure = present_headline_combos - expected_headline_combos
    excluded_periods = sorted(set(full_df["period"].unique()) - set(PERIOD_ORDER))
    RUN_META["row_count_control"] = {
        "n_period_x_daytype_combos_in_full_raw_csv": n_all_combos,
        "n_period_x_daytype_combos_in_headline_scope_(calendar=eplus,series=facility,scope=Toronto)": n_headline_combos_present,
        "expected_headline_combo_count": len(COMBOS),
        "missing_from_figure": sorted(missing_from_figure),
        "unexpected_extra_combos": sorted(extra_in_data_not_in_figure),
        "periods_excluded_by_design_(not_a_silent_drop)": excluded_periods,
        "n_metrics_per_combo_expected": len(METRICS),
        "n_rows_used_in_figure": int(len(headline_sub[headline_sub["metric"].isin([m[0] for m in METRICS])])),
    }
    if missing_from_figure:
        RUN_META["notes"].append(
            f"ROW-COUNT CONTROL FAILED: {sorted(missing_from_figure)} expected period x daytype "
            f"combos are missing from the headline-scope data -- figure is INCOMPLETE, do not "
            f"trust caption claims of full coverage.")
    else:
        RUN_META["notes"].append(
            f"Row-count control OK: all {len(COMBOS)} headline period x daytype combos "
            f"(periods={PERIOD_ORDER}, daytypes={DAYTYPE_ORDER}) present in the figure. "
            f"{len(excluded_periods)} finer-grained periods (the 12 individual months) exist in "
            f"the raw CSV but are deliberately excluded from this figure (too fine-grained for "
            f"one plot) -- stated here explicitly, not a silent drop.")

    # -- build per-metric pivot tables (sim, measured) over the 12 combos --
    combo_labels = [f"{p}\n{d}" for p, d in COMBOS]
    csv_rows = []
    metric_data = {}
    for metric, ylab, title, hatch_sim in METRICS:
        msub = headline_sub[headline_sub["metric"] == metric]
        sims, meas = [], []
        for p, d in COMBOS:
            r = msub[(msub["period"] == p) & (msub["daytype"] == d)]
            if len(r) != 1:
                sims.append(np.nan)
                meas.append(np.nan)
                csv_rows.append({"period": p, "daytype": d, "metric": metric, "sim": np.nan,
                                  "measured": np.nan, "status": "NOT_EVALUABLE (missing row)"})
                continue
            row = r.iloc[0]
            sv, mv = float(row["sim"]), float(row["measured"])
            sims.append(sv)
            meas.append(mv)
            csv_rows.append({
                "period": p, "daytype": d, "metric": metric, "sim": sv, "measured": mv,
                "sim_minus_measured": sv - mv,
                "status": "NOT_UNIT_COMPARABLE (sim scale-free normalized, measured real kWh)"
                          if hatch_sim else "COMPARABLE (scale-invariant ratio/position)",
            })
        metric_data[metric] = (sims, meas)

    out_csv_df = pd.DataFrame(csv_rows)
    out_csv_path = os.path.join(OUT_DIR, "fig07_measured_vs_simulated_shape.csv")
    out_csv_df.to_csv(out_csv_path, index=False)
    log(f"wrote {out_csv_path} ({len(out_csv_df)} rows)")

    # -- figure: 2x3 grid, 5 panels used, 6th holds the shared legend + scope note --
    fig, axes = plt.subplots(2, 3, figsize=(FIG_WIDTH_IN * 1.5, 6.0))
    axes_flat = axes.flatten()
    x = np.arange(len(COMBOS))
    w = 0.38

    for i, (metric, ylab, title, hatch_sim) in enumerate(METRICS):
        ax = axes_flat[i]
        sims, meas = metric_data[metric]
        ax.bar(x - w / 2, meas, width=w, label="Measured (IESO)", color="#4C72B0")
        if hatch_sim:
            ax.bar(x + w / 2, sims, width=w, label="Simulated (rebuilt)", color="#DD8452",
                   hatch="///", edgecolor="grey")
        else:
            ax.bar(x + w / 2, sims, width=w, label="Simulated (rebuilt)", color="#DD8452")
        ax.set_xticks(x)
        ax.set_xticklabels(combo_labels, fontsize=6, rotation=45, ha="right")
        ax.set_ylabel(ylab, fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.grid(axis="y", alpha=0.3)

    # 6th cell: legend + scope note, no axes
    ax_note = axes_flat[5]
    ax_note.axis("off")
    handles, labels = axes_flat[0].get_legend_handles_labels()
    ax_note.legend(handles, labels, loc="upper left", fontsize=9)
    ax_note.text(
        0.0, 0.55,
        f"Toronto, 2022, rebuilt runs.\ncalendar={CALENDAR}, series={SERIES},\n"
        f"measured_scope={SCOPE}.\nn={len(COMBOS)} period x daytype cells\n"
        f"(shoulder/winter/summer/full_year\nx weekday/weekend/holiday).\n"
        f"Hatched sim bar = not unit-\ncomparable to measured (see caption).",
        fontsize=7, va="top", transform=ax_note.transAxes)

    fig.suptitle("Measured (IESO) vs. simulated (rebuilt 2022 runs) daily-shape metrics, Toronto",
                  fontsize=11)
    fig.tight_layout()
    caption = (
        "Five shape metrics from T70's accepted sim-vs-measured join, Toronto 2022, rebuilt runs, "
        "calendar=eplus, series=facility, measured_scope=Toronto, 12 period x daytype cells "
        "(shoulder/winter/summer/full_year x weekday/weekend/holiday -- T70's own headline period "
        "set; the 12 individual months exist in the source CSV but are excluded from this figure, "
        "see run_meta.json row_count_control). load_factor/peak_to_avg/midday_share/mean_peak_hour "
        "are scale-invariant and directly comparable. max_kwh_per_premise's simulated bar is "
        "hatched: the sim series is normalized to each household run's own annual mean (order ~1-3, "
        "dimensionless) while the measured series is real, unnormalized kWh/premise -- the two are "
        "NOT on the same physical unit despite the shared column name (T15/T70's already-accepted "
        "decision keeps this column in the join; this figure never plots it as if it were "
        "comparable). No hourly (24-point) load curve exists in T70's accepted output -- its own "
        "script computes one internally but discards it before writing any CSV -- so this figure "
        "plots the five SAVED scalar shape metrics per period x daytype cell instead of an hourly "
        "curve, per the 'do not recompute' instruction."
    )
    save_fig(fig, "fig07_measured_vs_simulated_shape", caption)

    RUN_META["elapsed_sec"] = time.time() - t0
    RUN_META["dpi_setting"] = DPI
    RUN_META["fig_width_in_setting"] = FIG_WIDTH_IN * 1.5
    RUN_META["input_csv"] = JOIN_CSV
    RUN_META["input_csv_n_rows"] = int(len(full_df))
    RUN_META["headline_scope"] = {
        "calendar": CALENDAR, "series": SERIES, "measured_scope": SCOPE,
        "periods": PERIOD_ORDER, "daytypes": DAYTYPE_ORDER,
    }
    RUN_META["metrics_plotted"] = [m[0] for m in METRICS]
    RUN_META["output_csv"] = out_csv_path
    with open(os.path.join(OUT_DIR, "run_meta.json"), "w") as f:
        json.dump(RUN_META, f, indent=2, default=str)
    log(f"done in {RUN_META['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
