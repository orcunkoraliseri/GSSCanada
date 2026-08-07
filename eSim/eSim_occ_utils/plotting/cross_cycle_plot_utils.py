from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent

REQUIRED_COLUMNS = [
    "SIM_HH_ID",
    "Day_Type",
    "Hour",
    "HHSIZE",
    "DTYPE",
    "BEDRM",
    "CONDO",
    "ROOM",
    "REPAIR",
    "PR",
    "Occupancy_Schedule",
    "Metabolic_Rate",
]

CYCLE_FILES = {
    "2005": BASE_DIR / "0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct.csv",
    "2010": BASE_DIR / "0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv",
    "2015": BASE_DIR / "0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct.csv",
    "2022": BASE_DIR / "0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct.csv",
    "2025": BASE_DIR / "0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv",
}

HISTORICAL_COLORS = {
    "2005": "#1b9e77",
    "2010": "#2ca25f",
    "2015": "#41ae76",
    "2022": "#66c2a4",
}
FORECAST_COLOR = "#e67e22"
CYCLE_COLORS = {**HISTORICAL_COLORS, "2025": FORECAST_COLOR}

REGION_CANONICAL_MAP = {
    "Atlantic": "Atlantic",
    "Eastern Canada": "Atlantic",
    "BC": "BC",
    "British Columbia": "BC",
    "Alberta": "Prairies",
    "Prairies": "Prairies",
    "Ontario": "Ontario",
    "Quebec": "Quebec",
}
REGION_ORDER = ["BC", "Prairies", "Ontario", "Quebec", "Atlantic"]

DTYPE_CANONICAL_MAP = {
    "8": "OtherDwelling",
}


def canonicalize_region(value: object) -> str | None:
    if pd.isna(value):
        return None
    return REGION_CANONICAL_MAP.get(str(value), str(value))


def canonicalize_dtype(value: object) -> str | None:
    if pd.isna(value):
        return None
    return DTYPE_CANONICAL_MAP.get(str(value), str(value))


def load_all_cycles(columns_needed: Iterable[str]) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    columns = list(dict.fromkeys(columns_needed))
    missing_required = sorted(set(columns) - set(REQUIRED_COLUMNS))
    if missing_required:
        raise ValueError(f"Unsupported columns requested: {missing_required}")

    data_map: dict[str, pd.DataFrame] = {}
    summary_rows: list[dict[str, object]] = []

    print("=" * 72)
    print("Cross-cycle BEM data load summary")
    print("=" * 72)

    for cycle, file_path in CYCLE_FILES.items():
        if not file_path.exists():
            print(f"[WARN] {cycle}: missing file {file_path}")
            summary_rows.append(
                {
                    "Cycle": cycle,
                    "File_Found": "No",
                    "Rows": 0,
                    "Unique_Households": 0,
                    "Path": str(file_path),
                }
            )
            continue

        try:
            df = pd.read_csv(file_path, usecols=columns)
        except Exception as exc:
            print(f"[WARN] {cycle}: failed to read {file_path.name}: {exc}")
            summary_rows.append(
                {
                    "Cycle": cycle,
                    "File_Found": "Yes",
                    "Rows": 0,
                    "Unique_Households": 0,
                    "Path": str(file_path),
                }
            )
            continue

        if "DTYPE" in df.columns:
            df["DTYPE"] = df["DTYPE"].map(canonicalize_dtype)
        if "PR" in df.columns:
            df["PR"] = df["PR"].map(canonicalize_region)

        household_count = int(df["SIM_HH_ID"].nunique()) if "SIM_HH_ID" in df.columns else 0
        summary_rows.append(
            {
                "Cycle": cycle,
                "File_Found": "Yes",
                "Rows": int(len(df)),
                "Unique_Households": household_count,
                "Path": str(file_path),
            }
        )
        data_map[cycle] = df
        print(
            f"{cycle}: rows={len(df):,} unique_households={household_count:,} "
            f"columns={','.join(df.columns)}"
        )

    summary_df = pd.DataFrame(summary_rows)
    print("-" * 72)
    if not summary_df.empty:
        print(summary_df[["Cycle", "File_Found", "Rows", "Unique_Households"]].to_string(index=False))
    print("=" * 72)
    return data_map, summary_df


def household_level_frame(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    keep_cols = ["SIM_HH_ID", *[col for col in columns if col != "SIM_HH_ID"]]
    deduped = df[keep_cols].drop_duplicates(subset="SIM_HH_ID").copy()
    return deduped


def _sort_mixed_categories(values: Iterable[object]) -> list[object]:
    def sort_key(value: object) -> tuple[int, float | str]:
        try:
            return (0, float(value))
        except (TypeError, ValueError):
            return (1, str(value))

    return sorted(values, key=sort_key)


def build_non_temporal_distributions(
    data_map: dict[str, pd.DataFrame],
) -> tuple[dict[str, dict[str, pd.Series]], dict[str, list[object]]]:
    variables = ["DTYPE", "BEDRM", "ROOM", "PR"]
    household_maps = {
        cycle: household_level_frame(df, ["DTYPE", "BEDRM", "ROOM", "PR"])
        for cycle, df in data_map.items()
    }

    category_orders: dict[str, list[object]] = {}
    distributions: dict[str, dict[str, pd.Series]] = {var: {} for var in variables}

    for variable in variables:
        if variable == "PR":
            category_orders[variable] = REGION_ORDER
        else:
            union_values = set()
            for df in household_maps.values():
                union_values.update(df[variable].dropna().tolist())
            category_orders[variable] = _sort_mixed_categories(union_values)

        for cycle, df in household_maps.items():
            counts = df[variable].value_counts(dropna=False)
            counts = counts.reindex(category_orders[variable], fill_value=0)
            total = counts.sum()
            percentages = (counts / total * 100.0) if total else counts.astype(float)
            distributions[variable][cycle] = percentages.astype(float)

    return distributions, category_orders


def compute_distribution_histograms(
    data_map: dict[str, pd.DataFrame],
) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, dict[str, np.ndarray]]]:
    occupancy_results: dict[str, dict[str, np.ndarray]] = {}
    metabolic_results: dict[str, dict[str, np.ndarray]] = {}

    occ_bins = np.linspace(0.0, 1.0, 21)
    met_bins = np.linspace(0.0, 250.0, 51)
    occ_kde_x = np.linspace(0.0, 1.0, 250)
    met_kde_x = np.linspace(0.0, 250.0, 400)

    for cycle, df in data_map.items():
        occ_values = df["Occupancy_Schedule"].dropna().to_numpy(dtype=float)
        occ_counts, occ_edges = np.histogram(occ_values, bins=occ_bins)
        occ_pct = occ_counts / occ_counts.sum() * 100.0 if occ_counts.sum() else np.zeros_like(occ_counts, dtype=float)

        occupancy_results[cycle] = {
            "bin_edges": occ_edges,
            "bin_centers": (occ_edges[:-1] + occ_edges[1:]) / 2.0,
            "percentages": occ_pct,
            "kde_x": occ_kde_x,
            "kde_y": _compute_kde_percent(occ_values, occ_kde_x, domain_width=1.0),
        }

        met_values = df.loc[df["Metabolic_Rate"] > 0, "Metabolic_Rate"].dropna().to_numpy(dtype=float)
        met_counts, met_edges = np.histogram(met_values, bins=met_bins)
        met_pct = met_counts / met_counts.sum() * 100.0 if met_counts.sum() else np.zeros_like(met_counts, dtype=float)

        metabolic_results[cycle] = {
            "bin_edges": met_edges,
            "bin_centers": (met_edges[:-1] + met_edges[1:]) / 2.0,
            "percentages": met_pct,
            "kde_x": met_kde_x,
            "kde_y": _compute_kde_percent(met_values, met_kde_x, domain_width=250.0),
        }

    return occupancy_results, metabolic_results


def _compute_kde_percent(values: np.ndarray, x_grid: np.ndarray, domain_width: float) -> np.ndarray:
    if values.size < 2 or np.allclose(values, values[0]):
        return np.zeros_like(x_grid)
    kde = gaussian_kde(values)
    density = kde(x_grid)
    return density * (100.0 * domain_width / len(x_grid))


def prepare_heatmap_matrices(
    data_map: dict[str, pd.DataFrame],
    sample_size: int = 150,
    seed: int = 42,
) -> dict[str, dict[str, pd.DataFrame]]:
    rng = np.random.default_rng(seed)
    matrices: dict[str, dict[str, pd.DataFrame]] = {}

    for cycle, df in data_map.items():
        hh_ids = df["SIM_HH_ID"].dropna().unique()
        if hh_ids.size == 0:
            matrices[cycle] = {"Weekday": pd.DataFrame(), "Weekend": pd.DataFrame()}
            continue

        sample_n = min(sample_size, hh_ids.size)
        sampled_ids = rng.choice(hh_ids, size=sample_n, replace=False)
        sampled = df[df["SIM_HH_ID"].isin(sampled_ids)].copy()
        matrices[cycle] = {}

        for day_type in ["Weekday", "Weekend"]:
            subset = sampled[sampled["Day_Type"] == day_type]
            pivot = (
                subset.pivot_table(
                    index="SIM_HH_ID",
                    columns="Hour",
                    values="Occupancy_Schedule",
                    aggfunc="mean",
                )
                .reindex(columns=range(24))
                .fillna(0.0)
            )
            if pivot.empty:
                matrices[cycle][day_type] = pivot
                continue

            sort_key = pivot.loc[:, 9:16].mean(axis=1)
            pivot = pivot.assign(_sort_key=sort_key).sort_values("_sort_key").drop(columns="_sort_key")
            matrices[cycle][day_type] = pivot

    return matrices


def compute_mean_profiles(data_map: dict[str, pd.DataFrame]) -> dict[str, dict[str, pd.DataFrame]]:
    profiles: dict[str, dict[str, pd.DataFrame]] = {}

    for cycle, df in data_map.items():
        profiles[cycle] = {}
        for day_type in ["Weekday", "Weekend"]:
            subset = df[df["Day_Type"] == day_type]
            grouped = subset.groupby("Hour")["Occupancy_Schedule"]
            stats = pd.DataFrame(
                {
                    "mean": grouped.mean(),
                    "q25": grouped.quantile(0.25),
                    "q75": grouped.quantile(0.75),
                }
            ).reindex(range(24))
            profiles[cycle][day_type] = stats

    return profiles
