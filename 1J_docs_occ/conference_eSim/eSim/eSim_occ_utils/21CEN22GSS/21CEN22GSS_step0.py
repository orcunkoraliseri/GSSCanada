"""
21CEN22GSS Step 0

Preprocess GSS 2022 episode data into the compact CSV format consumed by the
legacy-style occupancy pipeline.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


EPISODE_COLUMNS = [
    "PUMFID",
    "INSTANCE",
    "ACTIVITY",
    "STARTMIN",
    "ENDMIN",
    "DURATION",
    "LOCATION",
    "TUI_06A",
    "TUI_06B",
    "TUI_06C",
    "TUI_06D",
    "TUI_06E",
    "TUI_06F",
    "TUI_06G",
    "TUI_06H",
    "TUI_06I",
    "TUI_06J",
    "TUI_07",
    "TUI_15",
]

ACT_MAP_22 = {
    100: 5,
    125: 5,
    150: 7,
    200: 2,
    230: 2,
    260: 2,
    300: 3,
    350: 3,
    400: 1,
    500: 8,
    600: 4,
    700: 12,
    800: 9,
    900: 10,
    1000: 11,
    1100: 13,
    1200: 10,
    1300: 14,
    9999: 14,
}

OUTPUT_COLUMNS = [
    "occID",
    "EPINO",
    "ACTCODE",
    "occACT",
    "STARTMIN",
    "ENDMIN",
    "start",
    "end",
    "DURATION",
    "LOCATION",
    "PRE",
    "coPRE",
    "Alone",
    "Spouse",
    "Children",
    "otherInFAMs",
    "parents",
    "Friends",
    "otherHHs",
    "colleagues",
    "Others",
    "techUse",
    "wellbeing",
    "TUI_06A",
    "TUI_06B",
    "TUI_06C",
    "TUI_06D",
    "TUI_06E",
    "TUI_06F",
    "TUI_06G",
    "TUI_06H",
    "TUI_06I",
    "TUI_06J",
    "TUI_07",
    "TUI_15",
]


def _map_actcode(code_raw) -> int:
    """
    Map raw GSS 2022 activity codes to harmonized 1-14 categories.
    """
    try:
        code = int(float(code_raw))
    except (TypeError, ValueError):
        return 14
    return ACT_MAP_22.get(code, 14)


def _min_to_hhmm(minutes_raw) -> int:
    """
    Convert decimal minutes from midnight into HHMM integer format.
    """
    try:
        minutes = int(float(minutes_raw)) % 1440
    except (TypeError, ValueError):
        return 0
    hours = minutes // 60
    mins = minutes % 60
    return hours * 100 + mins


def read_episode_file(episode_path: Path) -> pd.DataFrame:
    """
    Read the GSS 2022 episode SAS file and keep the step-0 columns.
    """
    df = pd.read_sas(episode_path, format="sas7bdat", encoding="latin1")

    missing = [col for col in EPISODE_COLUMNS if col not in df.columns]
    if missing:
        raise KeyError(f"Missing expected columns in episode file: {missing}")

    df = df[EPISODE_COLUMNS].copy()
    df = df.rename(
        columns={
            "PUMFID": "occID",
            "INSTANCE": "EPINO",
            "ACTIVITY": "ACTCODE",
        }
    )
    return df


def build_step0_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive PRE and coPRE while normalizing basic numeric columns.
    """
    df = df.copy()

    numeric_cols = ["occID", "EPINO", "ACTCODE", "STARTMIN", "ENDMIN", "DURATION", "LOCATION"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["PRE"] = (df["LOCATION"] == 3300.0).astype(int)
    df["coPRE"] = (
        (pd.to_numeric(df["TUI_06B"], errors="coerce") == 1.0)
        | (pd.to_numeric(df["TUI_06C"], errors="coerce") == 1.0)
        | (pd.to_numeric(df["TUI_06D"], errors="coerce") == 1.0)
    ).astype(int)
    df["occACT"] = df["ACTCODE"].apply(_map_actcode).astype(int)
    df["start"] = df["STARTMIN"].apply(_min_to_hhmm).astype(int)
    df["end"] = df["ENDMIN"].apply(_min_to_hhmm).astype(int)

    alias_sources = {
        "Alone": "TUI_06A",
        "Spouse": "TUI_06B",
        "Children": "TUI_06C",
        "otherInFAMs": "TUI_06D",
        "parents": "TUI_06E",
        "Friends": "TUI_06F",
        "otherHHs": "TUI_06G",
        "colleagues": "TUI_06H",
        "Others": "TUI_06I",
        "techUse": "TUI_07",
        "wellbeing": "TUI_15",
    }
    for alias, source in alias_sources.items():
        df[alias] = (pd.to_numeric(df[source], errors="coerce") == 1.0).astype(int)

    df = df[OUTPUT_COLUMNS].copy()
    df["occID"] = df["occID"].astype("Int64")
    df["EPINO"] = df["EPINO"].astype("Int64")
    df["ACTCODE"] = df["ACTCODE"].astype("Int64")
    df["occACT"] = df["occACT"].astype(int)
    df["STARTMIN"] = df["STARTMIN"].astype("Int64")
    df["ENDMIN"] = df["ENDMIN"].astype("Int64")
    df["start"] = df["start"].astype(int)
    df["end"] = df["end"].astype(int)
    df["DURATION"] = df["DURATION"].astype("Int64")
    df["LOCATION"] = df["LOCATION"].astype("Int64")
    df["PRE"] = df["PRE"].astype(int)
    df["coPRE"] = df["coPRE"].astype(int)
    for col in ["Alone", "Spouse", "Children", "otherInFAMs", "parents", "Friends", "otherHHs", "colleagues", "Others", "techUse", "wellbeing"]:
        df[col] = df[col].astype(int)
    return df


def save_step0_outputs(df: pd.DataFrame, output_path: Path, compatibility_path: Optional[Path] = None) -> None:
    """
    Save the processed episode CSV to the canonical pipeline location.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    if compatibility_path is not None:
        compatibility_path.parent.mkdir(parents=True, exist_ok=True)
        if compatibility_path != output_path:
            df.to_csv(compatibility_path, index=False)


def main(project_root: Optional[Path] = None) -> pd.DataFrame:
    """
    Run Step 0 end-to-end.
    """
    project_root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    episode_dir = project_root / "0_Occupancy" / "DataSources_GSS" / "Episode_files" / "GSS_2022_episode"

    episode_path = episode_dir / "TU_ET_2022_Episode_PUMF.sas7bdat"
    canonical_output = episode_dir / "out22EP_ACT_PRE_coPRE.csv"
    compatibility_output = project_root / "0_Occupancy" / "Outputs_GSS" / "out22EP_ACT_PRE_coPRE.csv"

    print(f"Reading episode file: {episode_path}")
    df_raw = read_episode_file(episode_path)
    print(f"Loaded {len(df_raw):,} episode rows from {df_raw['occID'].nunique():,} respondents")

    df_step0 = build_step0_frame(df_raw)
    print(
        "Derived PRE/coPRE: "
        f"PRE mean={df_step0['PRE'].mean():.3f}, "
        f"coPRE mean={df_step0['coPRE'].mean():.3f}"
    )

    save_step0_outputs(df_step0, canonical_output, compatibility_output)
    print(f"Saved canonical CSV: {canonical_output}")
    if compatibility_output != canonical_output:
        print(f"Saved compatibility CSV: {compatibility_output}")

    return df_step0


if __name__ == "__main__":
    main()
