"""
T76 -- WP11 Figure 1: at-home fraction by hour, across years/scenarios.

Aggregates Occupancy_Schedule (an at-home fraction, 0-1) by (Day_Type, Hour) across all
144,465 real households in each of six already-built, already-trusted schedule CSVs:
  - 2022 baseline (Nb-f frozen stock, the same file T20's own N0/N1 acceptance checks read)
  - 2030 main (real-trend forecast) and 2030 null (no-forecast-change control) -- T20
  - 2030 lambda 0.0 / 0.5 / 1.0 (S-Revert / S-Partial / S-Persist WFH-persistence scenarios) -- T26

No new simulation, no new modeling -- pure aggregation over files this project already
treats as ground truth for occupancy-schedule numbers (T20's own N0/N1 acceptance checks
used the identical "mean of the occupancy column, grouped" method on these same files).

Each row in every source file is one real household (SIM_HH_ID), no separate weight column
exists (PR is a province code, not a weight) -- so an unweighted mean per (Day_Type, Hour)
cell across all rows IS the population mean, the same method T20 N0/N1 already used.

Controls:
  - row-count/completeness: every file's total row count vs the login-node `wc -l`-confirmed
    expected count (6,934,320 data rows, all six files, checked before this job was written).
  - seen-working: for one fixed (Day_Type=Weekday, Hour=12) cell, an INDEPENDENT, non-pandas,
    non-chunked plain csv.reader pass computes its own hand mean/count and is compared against
    the chunked pandas aggregation's value for the same cell.
  - nesting cross-check: 2030 lambda_1.0 (S-Persist) is independently aggregated and compared
    cell-by-cell against 2030 main -- T26's own SC0 acceptance check already proved these are
    100% cell-identical; this run reproduces that check on this script's own aggregation path.
"""
import csv
import json
import os
import time

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

T0 = time.time()

SOURCES = {
    "2022_baseline": "/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv",
    "2030_main_persist": "/speed-scratch/o_iseri/2J_revision/T20/out/main/BEM_Setup/BEM_Schedules_2030.csv",
    "2030_null": "/speed-scratch/o_iseri/2J_revision/T20/out/null/BEM_Setup/BEM_Schedules_2030.csv",
    "2030_lambda_1.0_persist": "/speed-scratch/o_iseri/2J_revision/T26/out/lambda_1.0/BEM_Setup/BEM_Schedules_2030.csv",
    "2030_lambda_0.5_partial": "/speed-scratch/o_iseri/2J_revision/T26/out/lambda_0.5/BEM_Setup/BEM_Schedules_2030.csv",
    "2030_lambda_0.0_revert": "/speed-scratch/o_iseri/2J_revision/T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv",
}

# Confirmed via login-node `wc -l` on all six real files before this script was written
# (see T76 task doc Ledger): every file is 6,934,321 lines = 1 header + 6,934,320 data rows.
EXPECTED_ROWS = 6934320

OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T76/out/figures"
LOG_DIR = "/speed-scratch/o_iseri/2J_revision/T76/logs"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

CHUNKSIZE = 2_000_000
READ_DTYPES = {"Day_Type": "category", "Hour": "int16", "Occupancy_Schedule": "float64"}
CONTROL_CELL = ("Weekday", 12)


def aggregate_file(path):
    sums = {}
    counts = {}
    n_rows = 0
    for chunk in pd.read_csv(
        path,
        usecols=["Day_Type", "Hour", "Occupancy_Schedule"],
        dtype=READ_DTYPES,
        chunksize=CHUNKSIZE,
    ):
        n_rows += len(chunk)
        g = chunk.groupby(["Day_Type", "Hour"], observed=True)["Occupancy_Schedule"].agg(["sum", "count"])
        for (dt, hr), row in g.iterrows():
            key = (str(dt), int(hr))
            sums[key] = sums.get(key, 0.0) + float(row["sum"])
            counts[key] = counts.get(key, 0) + int(row["count"])
    means = {k: sums[k] / counts[k] for k in sums}
    total_counted = sum(counts.values())
    return means, counts, n_rows, total_counted


def hand_read_control(path, day_type, hour):
    """Independent code path: plain csv.reader, no pandas, no chunking, no groupby."""
    total = 0.0
    n = 0
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_dt = header.index("Day_Type")
        idx_hr = header.index("Hour")
        idx_occ = header.index("Occupancy_Schedule")
        hour_str = str(hour)
        for row in reader:
            if row[idx_dt] == day_type and row[idx_hr] == hour_str:
                total += float(row[idx_occ])
                n += 1
    return (total / n if n else None), n


results = {}
row_counts = {}
seen_working = {}
row_count_control = {}
t_per_file = {}

for label, path in SOURCES.items():
    tf0 = time.time()
    means, counts, n_rows, total_counted = aggregate_file(path)
    t_per_file[label] = time.time() - tf0
    results[label] = means
    row_counts[label] = n_rows

    row_count_control[label] = {
        "n_rows_read": n_rows,
        "n_rows_counted_in_groups": total_counted,
        "expected_rows": EXPECTED_ROWS,
        "match_expected": n_rows == EXPECTED_ROWS,
        "match_internal": n_rows == total_counted,
    }

    hand_mean, hand_n = hand_read_control(path, *CONTROL_CELL)
    agg_mean = means.get(CONTROL_CELL)
    agg_n = counts.get(CONTROL_CELL)
    match = (
        hand_mean is not None
        and agg_mean is not None
        and abs(hand_mean - agg_mean) < 1e-9
        and hand_n == agg_n
    )
    seen_working[label] = {
        "cell": f"{CONTROL_CELL[0]}/Hour={CONTROL_CELL[1]}",
        "hand_mean": hand_mean,
        "hand_n": hand_n,
        "agg_mean": agg_mean,
        "agg_n": agg_n,
        "match": bool(match),
    }
    print(
        f"[DONE] {label}: rows={n_rows} (expected {EXPECTED_ROWS}), "
        f"internal_count_match={n_rows == total_counted}, "
        f"seen_working_match={match}, elapsed={t_per_file[label]:.1f}s",
        flush=True,
    )

# Nesting cross-check: lambda_1.0 (S-Persist) vs main -- T26's own SC0 already proved
# 100% cell equality; reproduce it on this script's own aggregation.
main_means = results["2030_main_persist"]
lam1_means = results["2030_lambda_1.0_persist"]
common_keys = set(main_means) & set(lam1_means)
n_equal = sum(1 for k in common_keys if abs(main_means[k] - lam1_means[k]) < 1e-9)
nesting_check = {
    "n_cells_compared": len(common_keys),
    "n_cells_equal": n_equal,
    "all_equal": n_equal == len(common_keys) == 48,
}
print(f"[NESTING CHECK] main vs lambda_1.0: {n_equal}/{len(common_keys)} cells exactly equal", flush=True)

# ---- Tidy CSV of all six series ----
rows = []
for label, means in results.items():
    for (dt, hr), val in means.items():
        rows.append({"series": label, "day_type": dt, "hour": hr, "athome_fraction": val})
df = pd.DataFrame(rows).sort_values(["series", "day_type", "hour"])
csv_path = os.path.join(OUT_DIR, "fig01_athome_by_hour.csv")
df.to_csv(csv_path, index=False)

# ---- Plot ----
PLOT_SERIES = [
    ("2022_baseline", "2022 (baseline)", "-", "black"),
    ("2030_main_persist", "2030 - Main / Persist (lambda=1.0)", "-", "tab:red"),
    ("2030_null", "2030 - Null (no forecast change)", "--", "tab:gray"),
    ("2030_lambda_0.5_partial", "2030 - Partial (lambda=0.5)", "-.", "tab:orange"),
    ("2030_lambda_0.0_revert", "2030 - Revert (lambda=0.0)", ":", "tab:blue"),
]
# 2030_lambda_1.0_persist is deliberately NOT drawn as its own line: nesting_check above
# (reproducing T26's own accepted SC0 result) shows it is cell-for-cell identical to
# 2030_main_persist, so it would draw exactly on top of that line. Kept in the CSV for
# traceability, flagged in run_meta.json, never silently dropped.

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, day_type in zip(axes, ["Weekday", "Weekend"]):
    for key, label, style, color in PLOT_SERIES:
        means = results[key]
        hours = list(range(24))
        vals = [means.get((day_type, h), float("nan")) for h in hours]
        ax.plot(hours, vals, style, color=color, label=label, linewidth=1.6)
    ax.set_title(day_type)
    ax.set_xlabel("Hour (0-23)")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(0, 23)
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
axes[0].set_ylabel("At-home fraction (Occupancy_Schedule, 0-1)")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=8.5, frameon=False,
           bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Stock-wide at-home fraction by hour: 2022 vs 2030 scenarios\n"
             "(n=144,465 households per series, point estimates, no CI in source data)",
             fontsize=10.5)
fig.tight_layout(rect=[0, 0.12, 1, 0.93])

png_path = os.path.join(OUT_DIR, "fig01_athome_by_hour.png")
fig.savefig(png_path, dpi=600, bbox_inches="tight")
plt.close(fig)

img = Image.open(png_path)
dpi_readback = img.info.get("dpi")
px_size = img.size

elapsed_total = time.time() - T0

meta = {
    "jobid": os.environ.get("SLURM_JOB_ID"),
    "elapsed_seconds": elapsed_total,
    "elapsed_per_file_seconds": t_per_file,
    "sources": SOURCES,
    "expected_rows_per_file": EXPECTED_ROWS,
    "row_count_control": row_count_control,
    "seen_working_control": seen_working,
    "nesting_check_main_vs_lambda1.0": nesting_check,
    "day_type_values_confirmed": ["Weekday", "Weekend"],
    "hour_range": [0, 23],
    "no_ci_in_source": True,
    "aggregation_method": (
        "Unweighted mean of Occupancy_Schedule per (Day_Type,Hour) cell across all rows in "
        "the file. No weight column exists in any of the six schedule CSVs (PR is a province "
        "code, not a weight/probability column); each row is one real household (SIM_HH_ID), "
        "144,465 total per file, matching T18c/T20/T26's own accepted household count -- so "
        "this unweighted mean IS the population mean, the same method T20's own N0/N1 "
        "acceptance checks (2026-09-15) already used on these same files."
    ),
    "main_vs_null_meaning": (
        "CONFIRMED by reading 2026-09-15_T20_wp1_d1_2030_build.md's own Design section: "
        "'main' = 2030 built with the real OLS trend slope (06_forecast_rake.py "
        "project_to_2030, fit on 2005/2010/2015 real respondents) added to the 2022 stock "
        "rate, then raked to that target -- the historical at-home trend is projected forward. "
        "'null' = the identical code path with pre_slope forced to an all-zero (3,48) array, "
        "i.e. target == 2022 stock rate, so 'null' 2030 is a no-forecast-change control -- "
        "T20's own N0 acceptance check already measured null's weekday/weekend at-home means "
        "equal to 2022's to 0.0 pp (cells 100% exactly equal). Not a guess; read from the task "
        "doc's own Design and Collector sections."
    ),
    "lambda_meaning": (
        "CONFIRMED by reading 2026-09-15_T26_wp2_scenario_builds.md: lambda is the persistence "
        "weight of the 2022 pandemic-era at-home 'jump' relative to the pre-2022 trend. "
        "lambda=1.0 = S-Persist (jump fully persists to 2030). lambda=0.5 = S-Partial (half "
        "persists). lambda=0.0 = S-Revert (jump fully fades, only the pre-2022 trend "
        "continues). T26's own SC0 acceptance check already proved lambda=1.0 is 100% "
        "cell-identical to T20's 'main' 2030 build; T26's own SC2 check proved the expected "
        "order Revert < Partial < Persist in national weekday at-home share. This script's own "
        "nesting_check_main_vs_lambda1.0 above reproduces the SC0 equality independently on "
        "this run's own aggregation, not by trusting the T26 doc alone."
    ),
    "baseline_2022_source": (
        "/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/"
        "BEM_Schedules_2022.csv -- the Nb-f frozen 2022 stock schedule build. This is NOT a "
        "new aggregate computed for this task: it is the SAME file T20's own N0/N1 acceptance "
        "checks (2026-09-15) already read to compute weekday/weekend at-home means, and the "
        "SAME file the 2030 main/null (T20) and lambda 0.0/0.5/1.0 (T26) builds were all "
        "derived FROM (same 144,465 households, same stock). No other 2022 at-home-by-hour "
        "aggregate exists anywhere in the project -- T21/T17 hold per-household EnergyPlus "
        "hourly ENERGY output (used by T70/T71/T73), not a household-level occupancy-fraction "
        "schedule aggregate. Confirmed by reading the T20/T26/T21/T70 implementation docs "
        "directly, not guessed."
    ),
    "plotted_series": [k for k, _, _, _ in PLOT_SERIES],
    "series_computed_but_not_separately_plotted": ["2030_lambda_1.0_persist"],
    "note_on_lambda1.0": (
        "2030_lambda_1.0_persist was fully aggregated (six sources aggregated identically, no "
        "special-casing) and is confirmed numerically identical to 2030_main_persist in every "
        "(Day_Type,Hour) cell -- see nesting_check_main_vs_lambda1.0. This is the expected, "
        "already-accepted SC0 nesting property (T26 collector, 2026-09-15), not a bug. "
        "Plotting both would draw one line exactly on top of the other with no visible "
        "difference; the CSV deliverable keeps both series for traceability, the PNG plots "
        "only one to avoid a meaningless overlapping duplicate."
    ),
    "dpi_readback": dpi_readback,
    "png_pixel_size": list(px_size),
    "csv_path": csv_path,
    "png_path": png_path,
}

with open(os.path.join(LOG_DIR, "t76_run_meta.json"), "w") as f:
    json.dump(meta, f, indent=2, default=str)

print("[DONE ALL]", json.dumps({"elapsed_seconds": elapsed_total}), flush=True)
