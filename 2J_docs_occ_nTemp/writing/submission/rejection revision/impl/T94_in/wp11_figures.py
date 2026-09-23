#!/usr/bin/env python3
"""
T71 -- WP11: the four WP6-derived figures (annual by end use, intraday load shape by scenario,
peak/load-factor/ramp with CI, end-use x hour percent-change heatmap).

Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/2026-09-21_T71_wp11_figures_wp6_set.md
Implementation doc: impl/2026-09-21_T71_wp11_figures_wp6_set_IMPL.md

Inputs (read-only, never edited by this script):
  T68/out/enduse_annual.csv, enduse_hourly_profile.csv, grid_metrics.csv, enduse_change_2022_2030.csv
  T69/out/{S-None,S-Partial,S-Revert-std}/{same 4 files}
  T69/out/cross_scenario_common_basis.csv

STOCK_WEIGHTS, ARCH_NAMES and the divisor/QUOTABLE conventions are copied VERBATIM from
T68_scripts/enduse_hour_corrected.py (never re-derived) -- see that file's own header comment
for the original citation chain (T66 -> T68).

Two real findings this script's design had to reconcile (see IMPL doc Decisions for the full
reasoning):
  (1) enduse_change_2022_2030.csv only ever carries a bootstrapped CI for the 8 end-use energy
      meters (percent change) and for midday_share/load_factor (absolute-fraction change). It
      NEVER carries a CI for peak_kW_annual or any ramp metric -- confirmed by reading the
      script's own "shape metrics" loop (`for metric in ("midday_share", "load_factor")`) and by
      loading the real file and listing every `metric` value with a `stock_weighted` row. Figure 4
      therefore shows load_factor with its real CI, and peak/ramp as 2022-vs-2030 POINT VALUES
      ONLY, explicitly marked "no CI available in accepted WP6 output" -- never silently plotted
      as if they were CI-backed (ruling 4).
  (2) For midday_share/load_factor, the `point_change_pct`/`ci_low_pct`/`ci_high_pct` column
      NAMES say "pct" but `change_type == "absolute_fraction"` -- the values are an absolute
      fraction-point delta (e.g. 0.0049 = +0.49 percentage points of load factor), NOT a percent.
      This script reads `change_type` and labels the axis correctly; it does not trust the column
      name.
"""
import os
import io
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
# Paths
# --------------------------------------------------------------------------------------------
T68_DIR = "/speed-scratch/o_iseri/2J_revision/T68/out"
T69_DIR = "/speed-scratch/o_iseri/2J_revision/T69/out"
OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T71/out/figures"
LOG_DIR = "/speed-scratch/o_iseri/2J_revision/T71/logs"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

SCEN_DIR = {
    "S-Full": T68_DIR,
    "S-None": os.path.join(T69_DIR, "S-None"),
    "S-Partial": os.path.join(T69_DIR, "S-Partial"),
    "S-Revert-std": os.path.join(T69_DIR, "S-Revert-std"),
}
SCENARIOS = ["S-Full", "S-None", "S-Partial", "S-Revert-std"]

# --------------------------------------------------------------------------------------------
# Constants copied VERBATIM from T68_scripts/enduse_hour_corrected.py -- DO NOT re-derive.
# --------------------------------------------------------------------------------------------
ARCH_NAMES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

FACILITY = "Electricity:Facility"
M_LIGHTS = "InteriorLights:Electricity"
M_EQUIP = "InteriorEquipment:Electricity"
M_FAN = "Fan Electricity Energy"
M_HEAT = "Heating:EnergyTransfer"
M_COOL = "Cooling:EnergyTransfer"
M_WATER = "WaterSystems:EnergyTransfer"
M_REMAINDER = "HVACDHW:Electricity"

ANN_COL = {FACILITY: "elec_facility_kWh", M_LIGHTS: "lights_kWh", M_EQUIP: "equip_kWh",
           M_FAN: "fan_kWh", M_HEAT: "heating_ET_kWh", M_COOL: "cooling_ET_kWh",
           M_WATER: "water_ET_kWh"}
REMAINDER_ANN_COL = "hvac_dhw_elec_kWh"

METER_LABEL = {
    "elec_facility_kWh": "Electricity:Facility (total)",
    "lights_kWh": "Interior lights",
    "equip_kWh": "Interior equipment",
    "fan_kWh": "Fan electricity",
    "heating_ET_kWh": "Heating (EnergyTransfer)",
    "cooling_ET_kWh": "Cooling (EnergyTransfer)",
    "water_ET_kWh": "Water systems (EnergyTransfer)",
    "hvac_dhw_elec_kWh": "HVAC+DHW electricity (remainder)",
}
ANN_COL_ORDER = ["elec_facility_kWh", "lights_kWh", "equip_kWh", "fan_kWh",
                 "heating_ET_kWh", "cooling_ET_kWh", "water_ET_kWh", "hvac_dhw_elec_kWh"]

METER_LABEL_HOURLY = {
    "elec_facility_kWh": FACILITY, "lights_kWh": M_LIGHTS, "equip_kWh": M_EQUIP,
    "fan_kWh": M_FAN, "heating_ET_kWh": M_HEAT, "cooling_ET_kWh": M_COOL,
    "water_ET_kWh": M_WATER, "hvac_dhw_elec_kWh": M_REMAINDER,
}

DPI = 600
FIG_WIDTH_IN = 7.0  # print-width default for a two-column journal figure; see IMPL doc Decisions

RUN_META = {"figures": {}, "seen_working_control": {}, "notes": []}


def log(msg):
    print(f"[T71] {msg}", flush=True)


# --------------------------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------------------------
def stock_weighted_point(df, value_col, arch_col="arch"):
    """Pool all rows of a given archetype (across cities, exactly as
    T68's stock_weighted_cluster_bootstrap.stock_mean() pools households), take the arch mean,
    then STOCK_WEIGHTS-weight across archetypes. Point value only -- no resampling here, this is
    the plain stock-weighted mean, reusing the identical pooling structure T68 uses for its point
    estimate (the unresampled `stock_mean(cells)` call in that function)."""
    vals = pd.to_numeric(df[value_col], errors="coerce")
    sub = df.assign(_v=vals)
    acc = 0.0
    n_used = {}
    for arch in ARCH_NAMES:
        arr = sub.loc[sub[arch_col] == arch, "_v"].dropna()
        n_used[arch] = int(len(arr))
        if len(arr) == 0:
            continue
        acc += STOCK_WEIGHTS[arch] * float(arr.mean())
    return acc, n_used


def read_annual(scenario, year=None):
    path = os.path.join(SCEN_DIR[scenario], "enduse_annual.csv")
    df = pd.read_csv(path, dtype={"sim_hh_id": str})
    if year is not None:
        df = df[df["year"] == year]
    return df


def read_grid(scenario, year=None):
    path = os.path.join(SCEN_DIR[scenario], "grid_metrics.csv")
    df = pd.read_csv(path, dtype={"sim_hh_id": str})
    if year is not None:
        df = df[df["year"] == year]
    return df


def read_change(scenario):
    path = os.path.join(SCEN_DIR[scenario], "enduse_change_2022_2030.csv")
    return pd.read_csv(path)


PROFILE_USECOLS = ["arch", "city", "sim_hh_id", "year", "meter", "season", "daytype", "hour", "load_kW"]


def load_filtered_profile(scenario, meter=None, season=None, daytype=None, year=None,
                           household_set=None, chunksize=300_000):
    """Chunked read of a (large, ~500MB / ~4M row) enduse_hourly_profile.csv, filtering as early
    as possible per chunk so the accumulated result stays small (one arm processed at a time,
    discarded before the next -- per the task doc's memory-safety instruction)."""
    path = os.path.join(SCEN_DIR[scenario], "enduse_hourly_profile.csv")
    keep = []
    n_rows_seen = 0
    for chunk in pd.read_csv(path, usecols=PROFILE_USECOLS, dtype={"sim_hh_id": str},
                              chunksize=chunksize):
        n_rows_seen += len(chunk)
        m = pd.Series(True, index=chunk.index)
        if meter is not None:
            m &= chunk["meter"] == meter
        if season is not None:
            m &= chunk["season"] == season
        if daytype is not None:
            m &= chunk["daytype"] == daytype
        if year is not None:
            m &= chunk["year"] == year
        sub = chunk[m]
        if household_set is not None and len(sub) > 0:
            key = list(zip(sub["arch"], sub["city"], sub["sim_hh_id"]))
            mask2 = [k in household_set for k in key]
            sub = sub[mask2]
        if len(sub):
            keep.append(sub)
    out = pd.concat(keep, ignore_index=True) if keep else pd.DataFrame(columns=PROFILE_USECOLS)
    return out, n_rows_seen


def stock_weighted_hourly(df, value_col="load_kW"):
    """Group by (arch, hour), pool households across cities within an arch (mean), then
    STOCK_WEIGHTS-combine across archs, per hour. Returns a dict hour -> value plus per-arch
    household counts used (for QC)."""
    if df.empty:
        return {h: np.nan for h in range(24)}, {}
    by_arch_hour = df.groupby(["arch", "hour"])[value_col].mean()
    n_hh = df.groupby(["arch"])[["sim_hh_id"]].nunique()["sim_hh_id"].to_dict()
    out = {}
    for h in range(24):
        acc = 0.0
        any_data = False
        for arch in ARCH_NAMES:
            if (arch, h) in by_arch_hour.index:
                acc += STOCK_WEIGHTS[arch] * float(by_arch_hour.loc[(arch, h)])
                any_data = True
        out[h] = acc if any_data else np.nan
    return out, n_hh


def save_fig(fig, name, caption_note=""):
    png_path = os.path.join(OUT_DIR, f"{name}.png")
    fig.savefig(png_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    # Confirm actual saved dpi/size -- do not just assert the dpi= kwarg (ruling 2).
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
    RUN_META["figures"][name] = meta
    log(f"saved {name}: {px_w}x{px_h}px, dpi={dpi_meta}, width_in={width_in}")
    return meta


# --------------------------------------------------------------------------------------------
# Seen-working control (task doc section 4) -- separate code path from the aggregation above.
# --------------------------------------------------------------------------------------------
HAND_HH = {"arch": "SingleD", "city": "Toronto_5A", "sim_hh_id": "32811"}


def seen_working_control():
    """Hand-verify one (end use, hour, scenario) cell of enduse_hourly_profile.csv, read via a
    plain boolean-mask pandas read that shares NO code with load_filtered_profile()/
    stock_weighted_hourly() above. Also hand-verify one CI cell of enduse_change_2022_2030.csv."""
    result = {}
    # -- (a) hourly profile cell: S-Full, household sample_001_HH32811 (SingleD__Toronto_5A),
    #    Electricity:Facility, season=all, daytype=weekday, year=2030, hour=17 --
    path = os.path.join(SCEN_DIR["S-Full"], "enduse_hourly_profile.csv")
    df_full = pd.read_csv(path, dtype={"sim_hh_id": str})
    mask = ((df_full["arch"] == HAND_HH["arch"]) & (df_full["city"] == HAND_HH["city"]) &
            (df_full["sim_hh_id"] == HAND_HH["sim_hh_id"]) & (df_full["meter"] == FACILITY) &
            (df_full["season"] == "all") & (df_full["daytype"] == "weekday") &
            (df_full["year"] == 2030) & (df_full["hour"] == 17))
    row = df_full[mask]
    hand_value = float(row.iloc[0]["load_kW"]) if len(row) == 1 else None
    del df_full  # free ~500MB before continuing

    # now pull the same cell via the pipeline's own chunked reader, for comparison
    pipeline_df, _ = load_filtered_profile("S-Full", meter=FACILITY, season="all",
                                            daytype="weekday", year=2030,
                                            household_set={(HAND_HH["arch"], HAND_HH["city"], HAND_HH["sim_hh_id"])})
    pipeline_row = pipeline_df[pipeline_df["hour"] == 17]
    pipeline_value = float(pipeline_row.iloc[0]["load_kW"]) if len(pipeline_row) == 1 else None

    result["hourly_profile_cell"] = {
        "household": HAND_HH, "meter": FACILITY, "season": "all", "daytype": "weekday",
        "year": 2030, "hour": 17,
        "hand_read_value_kW": hand_value, "pipeline_read_value_kW": pipeline_value,
        "match": (hand_value is not None and pipeline_value is not None and
                  abs(hand_value - pipeline_value) < 1e-9),
    }

    # -- (b) CI cell: S-Full, stock_weighted, load_factor, from enduse_change_2022_2030.csv --
    ch_path = os.path.join(SCEN_DIR["S-Full"], "enduse_change_2022_2030.csv")
    ch = pd.read_csv(ch_path)
    hand_row = ch[(ch["level"] == "stock_weighted") & (ch["metric"] == "load_factor")]
    hand_ci = None
    if len(hand_row) == 1:
        r = hand_row.iloc[0]
        hand_ci = {"point": float(r["point_change_pct"]), "lo": float(r["ci_low_pct"]),
                   "hi": float(r["ci_high_pct"]), "change_type": str(r["change_type"])}
    result["change_table_cell"] = {
        "level": "stock_weighted", "metric": "load_factor", "hand_read": hand_ci,
        "note": "compared against fig04's own read of the identical row below",
    }
    return result


# --------------------------------------------------------------------------------------------
# Figure 2 -- annual energy by end use, S-Full, stock-weighted, 2022 vs 2030
# --------------------------------------------------------------------------------------------
def figure_02():
    log("figure 2: annual energy by end use (S-Full)")
    df = read_annual("S-Full")
    n_by_year = df.groupby("year").size().to_dict()

    rows = []
    whole = {2022: {}, 2030: {}}
    per_dwelling = {2022: {}, 2030: {}}
    for year in (2022, 2030):
        sub = df[df["year"] == year]
        for col in ANN_COL_ORDER:
            point, n_used = stock_weighted_point(sub, col)
            whole[year][col] = point
            row = {"end_use": METER_LABEL[col], "ann_col": col, "year": year,
                   "stock_weighted_whole_building_kWh": point,
                   "n_households_by_arch": json.dumps(n_used)}
            if col in ("equip_kWh", "lights_kWh"):
                pd_col = col + "_per_dwelling"
                vals = pd.to_numeric(sub[pd_col], errors="coerce")
                sub2 = sub.assign(_pd=vals)
                acc = 0.0
                any_data = False
                for arch in ARCH_NAMES:
                    arr = sub2.loc[sub2["arch"] == arch, "_pd"].dropna()
                    if len(arr) == 0:
                        continue
                    acc += STOCK_WEIGHTS[arch] * float(arr.mean())
                    any_data = True
                pdv = acc if any_data else None
                per_dwelling[year][col] = pdv
                row["stock_weighted_per_dwelling_kWh"] = pdv
            else:
                row["stock_weighted_per_dwelling_kWh"] = "NOT_EVALUABLE (no derived unit divisor -- T66 covers equip+light only)"
            rows.append(row)

    out_csv = pd.DataFrame(rows)
    out_csv.to_csv(os.path.join(OUT_DIR, "fig02_annual_by_enduse.csv"), index=False)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_WIDTH_IN, 8.5))

    labels = [METER_LABEL[c] for c in ANN_COL_ORDER]
    x = np.arange(len(ANN_COL_ORDER))
    w = 0.38
    v22 = [whole[2022][c] for c in ANN_COL_ORDER]
    v30 = [whole[2030][c] for c in ANN_COL_ORDER]
    ax1.bar(x - w / 2, v22, width=w, label="2022", color="#4C72B0")
    ax1.bar(x + w / 2, v30, width=w, label="2030", color="#DD8452")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=30, ha="right")
    ax1.set_ylabel("Stock-weighted annual energy\n(whole building, kWh/yr)")
    ax1.set_title(f"Annual energy by end use, main rebuild (S-Full), n={n_by_year.get(2022)} paired households")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    cols_pd = ["equip_kWh", "lights_kWh"]
    labels_pd = [METER_LABEL[c] for c in cols_pd]
    xp = np.arange(len(cols_pd))
    v22p = [per_dwelling[2022][c] for c in cols_pd]
    v30p = [per_dwelling[2030][c] for c in cols_pd]
    ax2.bar(xp - w / 2, v22p, width=w, label="2022", color="#4C72B0")
    ax2.bar(xp + w / 2, v30p, width=w, label="2030", color="#DD8452")
    ax2.set_xticks(xp)
    ax2.set_xticklabels(labels_pd)
    ax2.set_ylabel("Stock-weighted annual energy\n(per dwelling unit, kWh/yr)")
    ax2.set_title("Per-dwelling basis -- only end uses with a derived unit divisor (T66); all others\nhave NO valid per-dwelling number and are NEVER shown on this basis (see panel above)")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    save_fig(fig, "fig02_annual_by_enduse",
             "Panel A: whole-building stock-weighted annual kWh, all 8 end uses, S-Full only. "
             "Panel B: per-dwelling basis, equip+lights only (the only end uses with a derived "
             "unit divisor; ruling 3/4).")
    RUN_META["figure_02_household_count"] = n_by_year


# --------------------------------------------------------------------------------------------
# Figure 3 -- intraday load shape by scenario, weekday, year 2030, common households only
# --------------------------------------------------------------------------------------------
def figure_03():
    log("figure 3: intraday load shape by scenario")
    # -- common household set across all four arms, year 2030, via own directory-existence-style
    #    check (mirrors T69's discover_paired_household_set(), but against the four annual CSVs
    #    already produced, not a fresh directory walk -- these CSVs already ARE the discovered
    #    paired sets per arm) --
    hh_sets = {}
    for scen in SCENARIOS:
        df = read_annual(scen, year=2030)
        hh_sets[scen] = set(zip(df["arch"], df["city"], df["sim_hh_id"]))
    common = set.intersection(*hh_sets.values())
    n_common = len(common)
    log(f"common household set across all 4 arms (year 2030): n={n_common} "
        f"(per-arm sizes: {[len(v) for v in hh_sets.values()]})")
    RUN_META["figure_03_household_basis"] = {
        "n_common_computed": n_common,
        "per_arm_sizes": {k: len(v) for k, v in hh_sets.items()},
        "expected_from_cross_scenario_common_basis_csv": 1198,
        "matches_expected": (n_common == 1198),
    }
    if n_common != 1198:
        RUN_META["notes"].append(
            f"FIGURE 3 HOUSEHOLD-BASIS MISMATCH: computed four-way common set = {n_common}, "
            f"but T69/out/cross_scenario_common_basis.csv records 1198. Figure 3 uses the "
            f"COMPUTED set as the source of truth for its own filtering (it is what the plotting "
            f"code actually applies), but this discrepancy must be resolved before quoting n in "
            f"the manuscript.")

    rows = []
    curves = {}
    for scen in SCENARIOS:
        prof, n_seen = load_filtered_profile(scen, meter=FACILITY, season="all", daytype="weekday",
                                              year=2030, household_set=common)
        hourly, n_hh_by_arch = stock_weighted_hourly(prof, "load_kW")
        curves[scen] = hourly
        n_hh_total = prof[["arch", "city", "sim_hh_id"]].drop_duplicates().shape[0]
        for h in range(24):
            rows.append({"scenario": scen, "hour": h, "stock_weighted_load_kW": hourly[h],
                         "n_households_used": n_hh_total, "n_rows_scanned_in_source_file": n_seen})
        del prof  # discard before the next arm's ~500MB file, per the task doc's memory rule
        log(f"  {scen}: n_rows_scanned={n_seen}, n_households_in_filtered_set={n_hh_total}")

    out_csv = pd.DataFrame(rows)
    out_csv.to_csv(os.path.join(OUT_DIR, "fig03_intraday_load_shape.csv"), index=False)

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 4.5))
    colors = {"S-Full": "#4C72B0", "S-None": "#DD8452", "S-Partial": "#55A868", "S-Revert-std": "#C44E52"}
    for scen in SCENARIOS:
        ys = [curves[scen][h] for h in range(24)]
        ax.plot(range(24), ys, marker="o", markersize=3, label=scen, color=colors[scen])
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Stock-weighted Electricity:Facility load (kW)")
    ax.set_xticks(range(0, 24, 2))
    ax.set_title(f"Intraday load shape by scenario, 2030, weekday, n={n_common} common households")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "fig03_intraday_load_shape",
             f"Weekday, season='all' (whole-year weekday average), year 2030, meter=Electricity:"
             f"Facility, restricted to the {n_common} households common to all four scenario arms "
             f"(ruling 1).")


# --------------------------------------------------------------------------------------------
# Figure 4 -- peak, load factor, ramp, 2022 vs 2030, S-Full, with CI where one exists
# --------------------------------------------------------------------------------------------
def figure_04():
    log("figure 4: peak / load factor / ramp, S-Full")
    grid22 = read_grid("S-Full", year=2022)
    grid30 = read_grid("S-Full", year=2030)
    change = read_change("S-Full")

    peak22, _ = stock_weighted_point(grid22, "peak_kW_annual")
    peak30, _ = stock_weighted_point(grid30, "peak_kW_annual")
    ramp22, _ = stock_weighted_point(grid22, "evening_ramp_kW_mean")
    ramp30, _ = stock_weighted_point(grid30, "evening_ramp_kW_mean")
    lf22, _ = stock_weighted_point(grid22, "load_factor")
    lf30, _ = stock_weighted_point(grid30, "load_factor")

    lf_row = change[(change["level"] == "stock_weighted") & (change["metric"] == "load_factor")]
    if len(lf_row) != 1:
        raise RuntimeError("expected exactly one stock_weighted load_factor row in enduse_change_2022_2030.csv")
    lf_row = lf_row.iloc[0]
    lf_delta = float(lf_row["point_change_pct"])
    lf_lo = float(lf_row["ci_low_pct"])
    lf_hi = float(lf_row["ci_high_pct"])
    lf_change_type = str(lf_row["change_type"])
    lf_quotable = str(lf_row["change_quotable"])
    assert lf_change_type == "absolute_fraction", (
        f"load_factor change_type expected 'absolute_fraction', got {lf_change_type!r} -- "
        f"axis units would be wrong if this changed upstream")

    # -- confirm: no stock_weighted CI row exists for peak_kW_annual or any ramp metric (finding 1) --
    ci_metrics_present = set(change[change["level"] == "stock_weighted"]["metric"].unique())
    peak_has_ci = "peak_kW_annual" in ci_metrics_present
    ramp_has_ci = any("ramp" in m.lower() for m in ci_metrics_present)
    RUN_META["figure_04_ci_availability"] = {
        "metrics_with_stock_weighted_ci_in_file": sorted(ci_metrics_present),
        "peak_has_ci": peak_has_ci, "ramp_has_ci": ramp_has_ci,
        "load_factor_change_type": lf_change_type, "load_factor_quotable": lf_quotable,
    }
    if peak_has_ci or ramp_has_ci:
        RUN_META["notes"].append(
            "FIGURE 4: peak or ramp unexpectedly HAS a stock_weighted CI row in "
            "enduse_change_2022_2030.csv -- the assumption below (point-only, no CI) is now "
            "STALE and this figure needs re-checking before trusting it.")
    else:
        RUN_META["notes"].append(
            "FIGURE 4 FINDING: enduse_change_2022_2030.csv has NO stock_weighted CI row for "
            "peak_kW_annual or any ramp metric (only the 8 end-use energy meters + midday_share + "
            "load_factor get one). Per ruling 3 (never recompute a CI) and ruling 4 (never hide "
            "a NOT_EVALUABLE value), figure 4 shows peak and ramp as 2022-vs-2030 POINT VALUES "
            "with NO interval, visually distinct (hatched, grey) from load_factor's real CI band.")

    rows = [
        {"metric": "peak_kW_annual", "unit": "kW", "value_2022": peak22, "value_2030": peak30,
         "delta_or_point_change": peak30 - peak22, "ci_low": None, "ci_high": None,
         "ci_units": None, "status": "NOT_EVALUABLE (no CI in accepted WP6 output)"},
        {"metric": "evening_ramp_kW_mean", "unit": "kW", "value_2022": ramp22, "value_2030": ramp30,
         "delta_or_point_change": ramp30 - ramp22, "ci_low": None, "ci_high": None,
         "ci_units": None, "status": "NOT_EVALUABLE (no CI in accepted WP6 output)"},
        {"metric": "load_factor", "unit": "fraction (0-1)", "value_2022": lf22, "value_2030": lf30,
         "delta_or_point_change": lf_delta, "ci_low": lf_lo, "ci_high": lf_hi,
         "ci_units": "absolute fraction points (change_type=absolute_fraction, NOT percent)",
         "status": lf_quotable},
    ]
    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "fig04_peak_loadfactor_ramp_ci.csv"), index=False)

    fig, axes = plt.subplots(1, 3, figsize=(FIG_WIDTH_IN, 3.2))

    def bar_no_ci(ax, title, ylab, v2022, v2030):
        ax.bar([0, 1], [v2022, v2030], color=["#4C72B0", "#DD8452"], hatch="///", edgecolor="grey")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["2022", "2030"])
        ax.set_ylabel(ylab)
        ax.set_title(title + "\n(no CI computed)", fontsize=8)

    bar_no_ci(axes[0], "Peak demand", "Stock-weighted\npeak (kW)", peak22, peak30)
    bar_no_ci(axes[1], "Evening ramp\n(14h->17h mean)", "Stock-weighted\nramp (kW)", ramp22, ramp30)

    ax = axes[2]
    ax.bar([0, 1], [lf22, lf30], color=["#4C72B0", "#DD8452"])
    yerr_lo = lf_delta - lf_lo
    yerr_hi = lf_hi - lf_delta
    ax.errorbar([1], [lf30], yerr=[[yerr_lo], [yerr_hi]], fmt="none", ecolor="black", capsize=4,
                label="95% CI on the 2022->2030 delta")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["2022", "2030"])
    ax.set_ylabel("Stock-weighted load factor (fraction)")
    ax.set_title(f"Load factor\n(CI on delta: QUOTABLE={lf_quotable})", fontsize=8)

    fig.suptitle("Peak / ramp (point only, no CI available) vs. load factor (real CI) -- S-Full, 2022 vs 2030")
    fig.tight_layout()
    save_fig(fig, "fig04_peak_loadfactor_ramp_ci",
             "Peak and ramp: point values only, hatched, NO confidence interval exists in the "
             "accepted WP6 output for these two metrics. Load factor: real bootstrapped CI on the "
             "2022->2030 delta, reused verbatim from enduse_change_2022_2030.csv (T67-sourced).")


# --------------------------------------------------------------------------------------------
# Figure 5 -- end use x hour percent-change heatmap, S-Full, stock-weighted
# --------------------------------------------------------------------------------------------
def figure_05():
    log("figure 5: end use x hour percent-change heatmap (S-Full)")
    meters_hourly = [METER_LABEL_HOURLY[c] for c in ANN_COL_ORDER]
    prof, n_seen = load_filtered_profile("S-Full", season="all", daytype="all")
    log(f"  n_rows_scanned={n_seen}, n_rows_after_filter={len(prof)}")

    matrix = np.full((len(ANN_COL_ORDER), 24), np.nan)
    status_matrix = np.empty((len(ANN_COL_ORDER), 24), dtype=object)
    rows = []
    for i, ann_col in enumerate(ANN_COL_ORDER):
        meter = METER_LABEL_HOURLY[ann_col]
        sub = prof[prof["meter"] == meter]
        v22, _ = stock_weighted_hourly(sub[sub["year"] == 2022], "load_kW")
        v30, _ = stock_weighted_hourly(sub[sub["year"] == 2030], "load_kW")
        for h in range(24):
            a, b = v22.get(h, np.nan), v30.get(h, np.nan)
            if np.isnan(a) or np.isnan(b):
                pct, status = None, "NOT_EVALUABLE (missing hour/meter data)"
            elif a == 0:
                pct, status = None, "NOT_EVALUABLE (zero 2022 stock-weighted denominator)"
            else:
                pct = 100.0 * (b - a) / a
                status = "POINT_ONLY_NO_CI"
            matrix[i, h] = pct if pct is not None else np.nan
            status_matrix[i, h] = status
            rows.append({"end_use": METER_LABEL[ann_col], "hour": h,
                        "stock_weighted_2022_kW": a, "stock_weighted_2030_kW": b,
                        "pct_change": pct, "status": status})
    del prof

    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "fig05_enduse_hour_diff.csv"), index=False)

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 4.5))
    vmax = np.nanmax(np.abs(matrix)) if np.any(~np.isnan(matrix)) else 1.0
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax.set_yticks(range(len(ANN_COL_ORDER)))
    ax.set_yticklabels([METER_LABEL[c] for c in ANN_COL_ORDER], fontsize=8)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel("Hour of day")
    ax.set_title("End use x hour: 2022->2030 percent-change POINT ESTIMATE (S-Full, stock-weighted)\n"
                  "no confidence interval computed at this granularity -- not a quoted claim",
                  fontsize=9)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("% change, stock-weighted mean load (2022->2030)")

    # mark NOT_EVALUABLE cells distinctly (ruling 4): black 'x' hatch overlay
    for i in range(len(ANN_COL_ORDER)):
        for h in range(24):
            if status_matrix[i, h] != "POINT_ONLY_NO_CI":
                ax.text(h, i, "x", ha="center", va="center", color="black", fontsize=7)

    fig.tight_layout()
    save_fig(fig, "fig05_enduse_hour_diff",
             "Percent-change POINT ESTIMATES only (season='all', daytype='all' -- whole-year "
             "average day). 'x' marks a NOT_EVALUABLE cell (zero 2022 denominator or missing "
             "data), never plotted as if it were a real number. No bootstrap interval exists at "
             "this end-use x hour granularity; this heatmap is descriptive, not a quotable change "
             "claim on its own (ruling 5's QUOTABLE gate applies only to the CI-backed rows in "
             "enduse_change_2022_2030.csv, which this heatmap does not carry).")


def main():
    t0 = time.time()
    swc = seen_working_control()
    RUN_META["seen_working_control"] = swc
    log(f"seen-working control: {json.dumps(swc, default=str)}")

    figure_02()
    figure_03()
    figure_04()
    figure_05()

    RUN_META["elapsed_sec"] = time.time() - t0
    RUN_META["dpi_setting"] = DPI
    RUN_META["fig_width_in_setting"] = FIG_WIDTH_IN
    with open(os.path.join(OUT_DIR, "run_meta.json"), "w") as f:
        json.dump(RUN_META, f, indent=2, default=str)
    log(f"done in {RUN_META['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
