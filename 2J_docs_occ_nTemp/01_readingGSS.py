"""
01_readingGSS.py

Step 1 of the Occupancy Modeling Pipeline: Data Collection & Column Selection.
Reads GSS Main and Episode files for survey cycles 2005, 2010, 2015, and 2022.
Selects required columns without performing any harmonization or recoding.
Bootstrap weights are excluded.
"""

import os
import re

import numpy as np
import pandas as pd
import pyreadstat


# --- COLUMN SELECTION CONSTANTS ---

# Main file columns selected based on raw data headers
MAIN_COLS_2005: list[str] = [
    "RECID", "AGEGR10", "sex", "marstat", "HSDSIZEC", "REGION", "LUC_RST",
    "WKWE", "wght_per", "DVTDAY", "LANCH", "LFSGSS", "INCM", "EDU10", "WKWEHR_C",
    "MAR_Q172",    # Class of Worker
]

MAIN_COLS_2010: list[str] = [
    "RECID", "AGEGR10", "SEX", "MARSTAT", "HSDSIZEC", "PRV", "LUC_RST",
    "WKWE", "WGHT_PER", "DVTDAY", "LANCH", "LFSGSS", "INCM", "EDU10",
    "WKWEHR_C",
    "CTW_Q140_C01", "CTW_Q140_C02", "CTW_Q140_C03", "CTW_Q140_C04", "CTW_Q140_C05",
    "CTW_Q140_C06", "CTW_Q140_C07", "CTW_Q140_C08", "CTW_Q140_C09",
    "MAR_Q172",    # Class of Worker
]

MAIN_COLS_2015: list[str] = [
    "PUMFID", "SURVMNTH", "AGEGR10", "SEX", "MARSTAT", "HSDSIZEC", "PRV",
    "LUC_RST", "ACT7DAYS", "WET_110", "NOC1110Y", "WHW_110", "WHWD140C",
    "CTW_140A", "CTW_140B", "CTW_140C", "CTW_140D", "CTW_140E",
    "CTW_140F", "CTW_140G", "CTW_140H", "CTW_140I",
    "EHG_ALL", "LAN_01", "INCG1", "WGHT_PER", "DVTDAY"
]

MAIN_COLS_2022: list[str] = [
    "PUMFID", "SURVMNTH", "AGEGR10", "GENDER2", "MARSTAT", "HSDSIZEC", "PRV",
    "LUC_RST", "ACT7DAYC", "WET_120", "NOCLBR_Y", "WHWD140G",
    "CTW_140A", "CTW_140B", "CTW_140C", "CTW_140D", "CTW_140E", "CTW_140I",
    "ATT_150C", "EDC_10", "LAN_01", "INC_C", "WGHT_PER", "DDAY"
]

# Episode file columns verified from reference script and documentation
EPISODE_COLS_2005: list[str] = [
    "RECID", "EPINO", "WGHT_EPI", "ACTCODE", "STARTIME", "ENDTIME", "PLACE",
    "ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "NHSDCL15", "NHSDC15P",
    "OTHERS", "PARHSD", "NHSDPAR", "MEMBHSD"
]

EPISODE_COLS_2010: list[str] = [
    "RECID", "EPINO", "WGHT_EPI", "ACTCODE", "STARTIME", "ENDTIME", "PLACE",
    "ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "NHSDCL15", "NHSDC15P",
    "OTHERS", "PARHSD", "NHSDPAR", "MEMBHSD"
]

EPISODE_COLS_2015: list[str] = [
    "PUMFID", "EPINO", "WGHT_EPI", "TOTEPISO", "TUI_01", "STARTIME", "ENDTIME",
    "LOCATION", "TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D", "TUI_06E", "TUI_06F",
    "TUI_06G", "TUI_06H", "TUI_06I", "TUI_06J", "TUI_07", "TUI_10"
]

EPISODE_COLS_2022: list[str] = [
    "PUMFID", "INSTANCE", "WGHT_EPI", "TUI_01", "STARTIME", "ENDTIME", "LOCATION",
    "TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D", "TUI_06E", "TUI_06F", "TUI_06G",
    "TUI_06H", "TUI_06I", "TUI_06J", "TUI_07", "TUI_15"
]


# --- RENAME MAPS (Moved from Step 2) ---
MAIN_RENAME_MAP = {
    2005: {
        "RECID": "occID", "AGEGR10": "AGEGRP", "sex": "SEX", "marstat": "MARSTH",
        "HSDSIZEC": "HHSIZE", "REGION": "PR", "LUC_RST": "CMA", "wght_per": "WGHT_PER",
        "DVTDAY": "DDAY", "LANCH": "KOL", "LFSGSS": "LFTAG", "INCM": "TOTINC",
        "WKWEHR_C": "HRSWRK", "WKWE": "WKSWRK", "MAR_Q172": "COW",
    },
    2010: {
        "RECID": "occID", "AGEGR10": "AGEGRP", "SEX": "SEX", "MARSTAT": "MARSTH",
        "HSDSIZEC": "HHSIZE", "PRV": "PR", "LUC_RST": "CMA", "wght_per": "WGHT_PER",
        "DVTDAY": "DDAY", "LANCH": "KOL", "LFSGSS": "LFTAG", "INCM": "TOTINC",
        "WKWEHR_C": "HRSWRK", "WKWE": "WKSWRK", "MAR_Q172": "COW",
    },
    2015: {
        "PUMFID": "occID", "AGEGR10": "AGEGRP", "SEX": "SEX", "MARSTAT": "MARSTH",
        "HSDSIZEC": "HHSIZE", "PRV": "PR", "LUC_RST": "CMA", "WGHT_PER": "WGHT_PER",
        "DVTDAY": "DDAY", "LAN_01": "KOL", "ACT7DAYS": "LFTAG", "INCG1": "TOTINC",
        "WHWD140C": "HRSWRK", "NOC1110Y": "NOCS", "SURVMNTH": "SURVMNTH",
        "WET_110": "WKSWRK", "WHW_110": "COW",
    },
    2022: {
        "PUMFID": "occID", "AGEGR10": "AGEGRP", "GENDER2": "SEX", "MARSTAT": "MARSTH",
        "HSDSIZEC": "HHSIZE", "PRV": "PR", "LUC_RST": "CMA", "WGHT_PER": "WGHT_PER",
        "DVTDAY": "DDAY", "LAN_01": "KOL", "ACT7DAYC": "LFTAG", "INC_C": "TOTINC",
        "WHWD140G": "HRSWRK", "NOCLBR_Y": "NOCS", # "ATT_150C": "MODE",
        "SURVMNTH": "SURVMNTH", "WET_120": "COW",
    },
}

EPISODE_RENAME_MAP = {
    2005: {"RECID": "occID", "STARTIME": "start", "ENDTIME": "end"},
    2010: {"RECID": "occID", "STARTIME": "start", "ENDTIME": "end"},
    2015: {"PUMFID": "occID", "STARTIME": "start", "ENDTIME": "end"},
    2022: {"PUMFID": "occID", "INSTANCE": "EPINO", "STARTIME": "start", "ENDTIME": "end"},
}

def apply_rename_map(df: pd.DataFrame, cycle: int, rename_map: dict) -> pd.DataFrame:
    """Applies the specified rename map to the dataframe for unified schema target names."""
    if df.empty or cycle not in rename_map:
        return df
    return df.rename(columns=rename_map[cycle])


# --- FILE FORMAT READER FUNCTIONS ---

def load_spss_file(
    file_path: str,
    selected_columns: list[str] | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Reads an SPSS (.SAV) file, optionally extracting only selected columns.

    Args:
        file_path: Path to the .SAV file.
        selected_columns: List of columns to keep. If None, reads all columns.
        output_csv: Optional path to save the resulting DataFrame to CSV.
        verbose: Whether to print diagnostic information.

    Returns:
        pd.DataFrame containing the loaded data.
    """
    if verbose:
        print(f"Reading SPSS file: {file_path}")

    try:
        if selected_columns is not None:
            _, meta = pyreadstat.read_sav(file_path, metadataonly=True)
            available_cols = set(meta.column_names)
            valid_cols = [c for c in selected_columns if c in available_cols]
            
            if verbose:
                missing = set(selected_columns) - set(valid_cols)
                if missing:
                    print(f"  Warning: Columns not found in file: {missing}")
            
            df, _ = pyreadstat.read_sav(file_path, usecols=valid_cols)
        else:
            df, _ = pyreadstat.read_sav(file_path)

        if verbose:
            print(f"  Loaded shape: {df.shape}")

        if output_csv:
            save_df_to_csv(df, output_csv)

        return df

    except Exception as e:
        print(f"Error reading SPSS file {file_path}: {e}")
        return pd.DataFrame()


def load_dat_with_sps_layout(
    dat_file_path: str,
    sps_file_path: str,
    selected_columns: list[str] | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Reads a fixed-width (.DAT) file using an SPSS (.sps) layout file.

    Args:
        dat_file_path: Path to the .DAT file.
        sps_file_path: Path to the .SPS syntax file defining the layout.
        selected_columns: List of columns to keep. If None, extracts all.
        output_csv: Optional path to save the resulting DataFrame to CSV.
        verbose: Whether to print diagnostic information.

    Returns:
        pd.DataFrame containing the loaded data.
    """
    var_regex = re.compile(r"^\s*/?\s*([a-zA-Z0-9_]+)\s+(\d+)\s+-\s+(\d+)")
    column_names = []
    col_specs = []

    if verbose:
        print(f"Parsing syntax file: {sps_file_path}")

    try:
        with open(sps_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.strip().upper().startswith("VARIABLE LABELS"):
                    break

                match = var_regex.match(line)
                if match:
                    name = match.group(1)
                    start_pos = int(match.group(2))
                    end_pos = int(match.group(3))

                    if selected_columns is None or name in selected_columns:
                        column_names.append(name)
                        col_specs.append((start_pos - 1, end_pos))

        if not column_names:
            print("Error: No matching columns found in syntax file.")
            return pd.DataFrame()

        if verbose:
            print(f"  Loading {len(column_names)} column(s) from {dat_file_path}")

        df = pd.read_fwf(
            dat_file_path,
            colspecs=col_specs,
            names=column_names,
            dtype="str"
        )
        
        if verbose:
            print(f"  Loaded shape: {df.shape}")

        if output_csv:
            save_df_to_csv(df, output_csv)

        return df

    except Exception as e:
        print(f"Error reading DAT/SPS files: {e}")
        return pd.DataFrame()


def parse_spss_syntax_selective(
    syntax_file: str,
    columns_to_keep: list[str] | None = None
) -> list[tuple[str, int, int, int, str]]:
    """
    Parse SPSS .sps syntax file to extract variable specs for fixed-width reading.

    Args:
        syntax_file: Path to the .sps file.
        columns_to_keep: List of names to extract. None extracts all.

    Returns:
        List of tuples: (name, start_pos, end_pos, width, dtype).
    """
    with open(syntax_file, "r", encoding="latin-1") as f:
        content = f.read()

    data_list_match = re.search(
        r"DATA LIST.*?/(.*?)(?:VARIABLE LABELS|VALUE LABELS|EXECUTE|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not data_list_match:
        raise ValueError("Could not find DATA LIST section in syntax file.")

    data_list_section = data_list_match.group(1)
    var_pattern = r"(\w+)\s+(\d+)\s*-\s*(\d+)(?:\s*\(([A\d]+)\))?"
    matches = re.findall(var_pattern, data_list_section)

    variables = []
    columns_set = set(columns_to_keep) if columns_to_keep else None

    for var_name, start, end, format_spec in matches:
        if columns_set and var_name not in columns_set:
            continue

        start_pos = int(start) - 1
        end_pos = int(end)
        width = end_pos - start_pos

        if format_spec == "A":
            dtype = "str"
        elif format_spec and format_spec.isdigit():
            dtype = "float"
        else:
            dtype = "int"

        variables.append((var_name, start_pos, end_pos, width, dtype))

    return variables


def read_gss_data_selective(
    data_file: str,
    syntax_file: str,
    columns_to_keep: list[str] | None = None,
    chunksize: int = 100000,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Read fixed-width TXT file selectively based on SPS syntax in chunks.

    Args:
        data_file: Path to the fixed-width text file.
        syntax_file: Path to the .sps syntax file.
        columns_to_keep: Specific columns to load to reduce memory footprint.
        chunksize: Number of lines to process in one chunk.
        output_csv: Optional path to save results.
        verbose: Print diagnostic info.

    Returns:
        pd.DataFrame containing the loaded data.
    """
    try:
        variables = parse_spss_syntax_selective(syntax_file, columns_to_keep)
        
        if verbose:
            print(f"Parsing {data_file} via {syntax_file}")
            if columns_to_keep:
                missing = set(columns_to_keep) - {v[0] for v in variables}
                if missing:
                    print(f"  Warning: Syntax missing expected columns: {missing}")

        colspecs = [(v[1], v[2]) for v in variables]
        names = [v[0] for v in variables]

        chunks = []
        for i, chunk in enumerate(
            pd.read_fwf(
                data_file,
                colspecs=colspecs,
                names=names,
                encoding="latin-1",
                chunksize=chunksize,
                dtype_backend="numpy_nullable"
            )
        ):
            chunks.append(chunk)

        df = pd.concat(chunks, ignore_index=True)

        for var_name, _, _, _, dtype in variables:
            if dtype == "float":
                df[var_name] = pd.to_numeric(df[var_name], errors="coerce")
            elif dtype == "int":
                df[var_name] = pd.to_numeric(df[var_name], errors="coerce").astype("Int64")

        if columns_to_keep:
            final_columns = [col for col in columns_to_keep if col in df.columns]
            df = df[final_columns]

        if verbose:
            print(f"  Loaded shape: {df.shape}")

        if output_csv:
            save_df_to_csv(df, output_csv)

        return df

    except Exception as e:
        print(f"Error reading GSS fixed-width file: {e}")
        return pd.DataFrame()


def read_sas_file(
    sas_file_path: str,
    selected_columns: list[str] | None = None,
    chunk_size: int = 100000,
    encoding: str = "utf-8",
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Reads a SAS (.sas7bdat) file in chunks to handle memory properly.

    Args:
        sas_file_path: Path to the SAS file.
        selected_columns: Columns to retain.
        chunk_size: Processing chunk size.
        encoding: Primary encoding attempt. Falls back to latin-1 on error.
        output_csv: Optional CSV save path.
        verbose: Diagnostic printing.

    Returns:
        pd.DataFrame containing the loaded data.
    """
    if verbose:
        print(f"Reading SAS file: {sas_file_path}")

    if not os.path.exists(sas_file_path):
        print(f"Error: SAS file not found at {sas_file_path}")
        return pd.DataFrame()

    def process_reader(reader, cols_to_keep):
        chunks = []
        for chunk in reader:
            if cols_to_keep is not None:
                valid_cols = [c for c in cols_to_keep if c in chunk.columns]
                chunk = chunk[valid_cols]
            chunks.append(chunk)
        return chunks

    filtered_chunks = []
    try:
        reader = pd.read_sas(
            sas_file_path,
            chunksize=chunk_size,
            iterator=True,
            encoding=encoding
        )
        filtered_chunks = process_reader(reader, selected_columns)
    except UnicodeDecodeError:
        if verbose:
            print(f"  Warning: {encoding} failed, trying latin-1...")
        try:
            reader = pd.read_sas(
                sas_file_path,
                chunksize=chunk_size,
                iterator=True,
                encoding="latin-1"
            )
            filtered_chunks = process_reader(reader, selected_columns)
        except Exception as e:
            print(f"Error with fallback encoding reading SAS: {e}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error reading SAS file: {e}")
        return pd.DataFrame()

    if not filtered_chunks:
        return pd.DataFrame()

    full_df = pd.concat(filtered_chunks, ignore_index=True)
    
    if verbose:
        print(f"  Loaded shape: {full_df.shape}")

    if output_csv:
        save_df_to_csv(full_df, output_csv)

    return full_df


# --- ORCHESTRATOR FUNCTIONS ---

def read_gss_main(
    cycle_year: int,
    file_path: str,
    syntax_path: str | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Read the GSS Main file for a specific cycle year.

    Args:
        cycle_year: 2005, 2010, 2015, or 2022.
        file_path: Path to the data file.
        syntax_path: Path to the syntax file if required (.DAT/.txt).
        output_csv: Optional CSV save path.
        verbose: Boolean to log progress.

    Returns:
        pd.DataFrame for the specified Main file.
    """
    if cycle_year == 2005:
        if file_path.lower().endswith(".sas7bdat"):
            df = read_sas_file(
                file_path, selected_columns=MAIN_COLS_2005, 
                output_csv=None, verbose=verbose
            )
        elif file_path.lower().endswith(".sav"):
            df = load_spss_file(
                file_path, selected_columns=MAIN_COLS_2005, 
                output_csv=None, verbose=verbose
            )
        else:
            print(f"Unsupported extension for 2005 Main file: {file_path}")
            df = pd.DataFrame()

    elif cycle_year == 2010:
        if not syntax_path:
            print("Error: syntax_path is required for 2010 Main file.")
            df = pd.DataFrame()
        else:
            df = load_dat_with_sps_layout(
                file_path, syntax_path, selected_columns=MAIN_COLS_2010,
                output_csv=None, verbose=verbose
            )

    elif cycle_year == 2015:
        if not syntax_path:
            print("Error: syntax_path is required for 2015 Main file.")
            df = pd.DataFrame()
        else:
            df = read_gss_data_selective(
                file_path, syntax_path, columns_to_keep=MAIN_COLS_2015,
                output_csv=None, verbose=verbose
            )

    elif cycle_year == 2022:
        df = read_sas_file(
            file_path, selected_columns=MAIN_COLS_2022, 
            output_csv=None, verbose=verbose
        )

    else:
        print(f"Unsupported cycle year: {cycle_year}")
        df = pd.DataFrame()
        
    df = apply_rename_map(df, cycle_year, MAIN_RENAME_MAP)
    if output_csv:
        save_df_to_csv(df, output_csv)
    return df


def read_gss_episode(
    cycle_year: int,
    file_path: str,
    syntax_path: str | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Read the GSS Episode file for a specific cycle year.

    Args:
        cycle_year: 2005, 2010, 2015, or 2022.
        file_path: Path to the data file.
        syntax_path: Path to the syntax file if required (.DAT/.txt).
        output_csv: Optional CSV save path.
        verbose: Boolean to log progress.

    Returns:
        pd.DataFrame for the specified Episode file.
    """
    if cycle_year == 2005:
        df = load_spss_file(
            file_path, selected_columns=EPISODE_COLS_2005,
            output_csv=None, verbose=verbose
        )

    elif cycle_year == 2010:
        if not syntax_path:
            print("Error: syntax_path is required for 2010 Episode file.")
            df = pd.DataFrame()
        else:
            df = load_dat_with_sps_layout(
                file_path, syntax_path, selected_columns=EPISODE_COLS_2010,
                output_csv=None, verbose=verbose
            )

    elif cycle_year == 2015:
        if not syntax_path:
            print("Error: syntax_path is required for 2015 Episode file.")
            df = pd.DataFrame()
        else:
            df = read_gss_data_selective(
                file_path, syntax_path, columns_to_keep=EPISODE_COLS_2015,
                output_csv=None, verbose=verbose
            )

    elif cycle_year == 2022:
        df = read_sas_file(
            file_path, selected_columns=EPISODE_COLS_2022,
            output_csv=None, verbose=verbose
        )

    else:
        print(f"Unsupported cycle year: {cycle_year}")
        df = pd.DataFrame()
        
    df = apply_rename_map(df, cycle_year, EPISODE_RENAME_MAP)
    if output_csv:
        save_df_to_csv(df, output_csv)
    return df


def read_all_cycles(
    file_paths: dict[int, dict[str, str]],
    output_dir: str | None = None,
    verbose: bool = False,
) -> dict[int, dict[str, pd.DataFrame]]:
    """
    Read Main + Episode files for all available cycles based on provided paths.

    Args:
        file_paths: Nested dictionary containing paths for 'main', 'episode',
            'syntax_main', and 'syntax_episode' per cycle year.
        output_dir: Optional root directory to save CSV extracts.
        verbose: Logging verbosity.

    Returns:
        Nested dict with DataFrames: {cycle_year: {'main': df, 'episode': df}}
    """
    results: dict[int, dict[str, pd.DataFrame]] = {}

    for year, paths in file_paths.items():
        if verbose:
            print(f"\n{'='*40}\nProcessing Cycle: {year}\n{'='*40}")

        results[year] = {}
        
        main_csv = os.path.join(output_dir, f"main_{year}.csv") if output_dir else None
        epi_csv = os.path.join(output_dir, f"episode_{year}.csv") if output_dir else None

        if "main" in paths:
            results[year]["main"] = read_gss_main(
                cycle_year=year,
                file_path=paths["main"],
                syntax_path=paths.get("syntax_main"),
                output_csv=main_csv,
                verbose=verbose
            )

        if "episode" in paths:
            results[year]["episode"] = read_gss_episode(
                cycle_year=year,
                file_path=paths["episode"],
                syntax_path=paths.get("syntax_episode"),
                output_csv=epi_csv,
                verbose=verbose
            )

    return results


# --- UTILITY FUNCTIONS ---

def save_df_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """Save DataFrame to CSV, creating parent directories if needed."""
    if df.empty:
        return
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        print(f"  Successfully saved {len(df)} rows to {file_path}")
    except Exception as e:
        print(f"  Failed to save CSV {file_path}: {e}")


def describe_unique_values(df: pd.DataFrame, exclude_cols: list[str] | None = None) -> None:
    """Print unique value counts and actual values for each column."""
    exclude_cols = exclude_cols or []
    for col in df.columns:
        if col in exclude_cols:
            continue
        uniques = df[col].dropna().unique()
        print(f"[{col}] Count: {len(uniques)} | Values: {uniques}")


def print_nan_counts(df: pd.DataFrame) -> None:
    """Print counts of NaN values per column, if any exist."""
    nan_counts = df.isnull().sum()
    filtered = nan_counts[nan_counts > 0]
    if filtered.empty:
        print("  No missing values found.")
    else:
        print("  Missing values count:")
        print(filtered)


# --- ENTRY POINT ---

if __name__ == "__main__":
    DATA_ROOT = "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/0_Occupancy/DataSources_GSS"
    
    FILE_PATHS_CONFIG = {
        2005: {
            "main": f"{DATA_ROOT}/Main_files/GSSMain_2005.sas7bdat",
            "episode": f"{DATA_ROOT}/Episode_files/GSS_2005_episode/C19PUMFE_NUM.SAV"
        },
        2010: {
            "main": f"{DATA_ROOT}/Main_files/GSSMain_2010.DAT",
            "syntax_main": f"{DATA_ROOT}/Main_files/GSSMain_2010_syntax.SPS",
            "episode": f"{DATA_ROOT}/Episode_files/GSS_2010_episode/C24EPISODE_withno_bootstrap.DAT",
            "syntax_episode": f"{DATA_ROOT}/Episode_files/GSS_2010_episode/C24_Episode File_SPSS_withno_bootstrap.SPS"
        },
        2015: {
            "main": f"{DATA_ROOT}/Main_files/GSSMain_2015.txt",
            "syntax_main": f"{DATA_ROOT}/Main_files/GSSMain_2015.sps",
            "episode": f"{DATA_ROOT}/Episode_files/GSS_2015_episode/GSS29PUMFE.txt",
            "syntax_episode": f"{DATA_ROOT}/Episode_files/GSS_2015_episode/c29pumfe_e.sps"
        },
        2022: {
            "main": f"{DATA_ROOT}/Main_files/GSSMain_2022.sas7bdat",
            "episode": f"{DATA_ROOT}/Episode_files/GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat"
        }
    }

    OUTPUT_DIRECTORY = "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step1"

    print("Starting GSS Data Collection (Step 1)...")
    
    # Pass FILE_PATHS_CONFIG to run all 4 cycles
    test_paths = FILE_PATHS_CONFIG
    
    dfs = read_all_cycles(test_paths, output_dir=OUTPUT_DIRECTORY, verbose=True)

    for year, dataset in dfs.items():
        print(f"\n--- Output Validation for {year} ---")
        if "main" in dataset:
            main_df = dataset["main"]
            print(f"MAIN shape: {main_df.shape}")
            print(f"MAIN columns: {main_df.columns.tolist()}")
            if year == 2005:
                print_nan_counts(main_df)
                
        if "episode" in dataset:
            epi_df = dataset["episode"]
            print(f"EPISODE shape: {epi_df.shape}")
            print(f"EPISODE columns: {epi_df.columns.tolist()}")
            
    print("\nGSS Data Collection complete.")

    import subprocess
    print("\nRunning Step 1 Validation...")
    subprocess.run(["python", "01_readingGSS_val.py"], check=True)
