# Implementation Plan — `01_readingGSS.py`
## STEP 1: Data Collection & Column Selection

---

## Goal

Create a modular Python script (`01_readingGSS.py`) that reads and extracts the required columns from **GSS Main** and **GSS Episode** files for all four survey cycles (2005, 2010, 2015, 2022). This is the first step of the occupancy modeling pipeline — no harmonization, merging, or recoding occurs here; the output is one pair of raw DataFrames (Main + Episode) per cycle with only the pipeline-relevant columns retained.

**Bootstrap weight columns (`WTBS_*`, `WTBS_EPI_*`) are excluded** from this pipeline as they contain no useful information for the occupancy modeling workflow.

---

## Reference

- **Pipeline overview**: [0_GSS_Occupancy_Pipeline_Overview.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/0_GSS_Occupancy_Pipeline_Overview.md)
- **Detailed documentation**: [0_GSS_Occupancy_Documentation.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/0_GSS_Occupancy_Documentation.md)
- **Reference script**: [2ndJ_datapreprocessing.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/examples/2ndJ_datapreprocessing.py)
- **Column name reference**: [gss_headers.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/0_Occupancy/DataSources_GSS/gss_headers.csv)

---

## Data Source Inventory

All data files are located under:
```
/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/0_Occupancy/DataSources_GSS/
```

### Main Files

| Cycle | File | Format | Reader |
|---|---|---|---|
| 2005 | `Main_files/GSSMain_2005.sas7bdat` (321 MB) | SAS | `read_sas_file()` |
| 2010 | `Main_files/GSSMain_2010.DAT` + `GSSMain_2010_syntax.SPS` | Fixed-width `.DAT` + `.SPS` | `load_dat_with_sps_layout()` |
| 2015 | `Main_files/GSSMain_2015.txt` + `GSSMain_2015.sps` (102 MB) | Fixed-width + SPSS syntax | `read_gss_data_selective()` |
| 2022 | `Main_files/GSSMain_2022.sas7bdat` (41 MB) | SAS | `read_sas_file()` |

### Episode Files

| Cycle | File | Format | Reader |
|---|---|---|---|
| 2005 | `Episode_files/GSS_2005_episode/C19PUMFE_NUM.SAV` (27 MB) | SPSS `.SAV` | `load_spss_file()` |
| 2010 | `Episode_files/GSS_2010_episode/C24EPISODE_withno_bootstrap.DAT` + `C24_Episode File_SPSS_withno_bootstrap.SPS` (22 MB) | Fixed-width `.DAT` + `.SPS` | `load_dat_with_sps_layout()` |
| 2015 | `Episode_files/GSS_2015_episode/GSS29PUMFE.txt` + `c29pumfe_e.sps` (1.4 GB) | Fixed-width `.txt` + `.sps` | `read_gss_data_selective()` |
| 2022 | `Episode_files/GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat` (471 MB) | SAS | `read_sas_file()` |

> [!NOTE]
> The 2005 episode directory also contains `C19PUMFM_NUM.SAV` (a Main file in SPSS format, 216 MB). The script can load either the `.sas7bdat` from `Main_files/` or this `.SAV` as a fallback — both contain the same 2005 Main data.

---

## Proposed Changes

### [NEW] [01_readingGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/01_readingGSS.py)

---

### A. File-Format Reader Functions

Adapted from `2ndJ_datapreprocessing.py` with PEP 8 compliance, type hints, and Google-style docstrings.

| Function | Format | Used For | Based On |
|---|---|---|---|
| `load_spss_file()` | `.SAV` (SPSS) | 2005 Episode | Reference `load_spss_file()` |
| `load_dat_with_sps_layout()` | `.DAT` + `.SPS` | 2010 Main + Episode | Reference `load_dat_with_sps_layout()` |
| `parse_spss_syntax_selective()` | `.sps` parser | Helper for 2015 | Reference `parse_spss_syntax_selective()` |
| `read_gss_data_selective()` | `.txt` + `.sps` | 2015 Main + Episode | Reference `read_gss_data_selective()` |
| `read_sas_file()` | `.sas7bdat` | 2005 Main, 2022 Main + Episode | Reference `read_SAS()` |

Each reader accepts `file_path`, `selected_columns`, `output_csv` (optional), and `verbose` parameters.

---

### B. Column Selection Constants

Extracted from the pipeline documentation and cross-referenced with `gss_headers.csv`.

#### Main File Columns (from `gss_headers.csv` + pipeline documentation)

```python
# Columns verified against gss_headers.csv
MAIN_COLS_2005: list[str] = [
    "RECID",        # occID (PUMFID equivalent for 2005)
    "AGEGR10",      # AGEGRP  → row 514
    "sex",          # SEX     → row 260 (lowercase in 2005)
    "marstat",      # MARSTH  → row 32  (lowercase in 2005)
    "HSDSIZEC",     # HHSIZE  → row 597
    "REGION",       # PR      → row 360
    "LUC_RST",      # CMA     → row 208
    "WKWE",         # COW / HRSWRK-adjacent
    # Additional columns to verify from SPSS metadata:
    # SURVYEAR, SURVMNTH, LAN_01, ATTSCH, NOCLBR_Y, LFACT,
    # WET_120C, WHWD140G, ATT_150C, CTW_140I, INC_C
    "wght_per",     # WGHT_PER → row 596 (lowercase in 2005)
    "DVTDAY",       # DDAY    → row 267
]

MAIN_COLS_2015: list[str] = [
    "PUMFID",       # occID
    "SURVMNTH",     # row 2
    "AGEGR10",      # row 3
    "SEX",          # row 4 → actually named SEX (not GENDER2 as in doc)
    "MARSTAT",      # row 5
    "HSDSIZEC",     # row 20
    "PRV",          # row 23
    "LUC_RST",      # row 24
    "ACT7DAYS",     # LFTAG → row 250
    "WET_110",      # COW → row 258
    "NOC1110Y",     # NOCS → row 263
    "WHW_110",      # HRSWRK → row 271
    "WHWD140C",     # HRSWRK grouped → row 277
    "CTW_140I",     # POWST → row 315
    "EDC_10",       # ATTSCH → row 318 (via EHG_ALL)
    "LAN_01",       # KOL → row 341
    "INCG1",        # TOTINC → row 346
    "WGHT_PER",     # row 1
    "DVTDAY",       # DDAY → row 27
]

MAIN_COLS_2022: list[str] = [
    "PUMFID",       # occID
    "SURVMNTH",     # row 2
    "AGEGR10",      # row 8
    "GENDER2",      # SEX → row 9
    "MARSTAT",      # row 10
    "HSDSIZEC",     # row 7
    "PRV",          # row 4
    "LUC_RST",      # row 5
    "ACT7DAYC",     # LFTAG → row 67
    "WET_120",      # COW → row 71
    "NOCLBR_Y",     # NOCS → row 89
    "WHWD140G",     # HRSWRK → row 74
    "CTW_140I",     # POWST → row 132
    "ATT_150C",     # MODE → row 114
    "EDC_10",       # ATTSCH → row 141
    "LAN_01",       # KOL → row 156
    "INC_C",        # TOTINC → row 159
    "WGHT_PER",     # row 1
    "DDAY",         # row 164
]
```

> [!IMPORTANT]
> The 2005 Main file column names in `gss_headers.csv` use a different naming convention from later cycles (e.g., `sex` lowercase, `marstat` lowercase, `RECID` instead of `PUMFID`). Some pipeline-required columns (e.g., `SURVYEAR`, `SURVMNTH`, `LAN_01`, `INC_C`) are **not immediately visible** in `gss_headers.csv` for 2005. During execution, the script will first load all columns from the 2005 Main file to inspect what is actually available, then finalize the column list.

#### Episode File Columns

```python
EPISODE_COLS_2005: list[str] = [
    "RECID", "EPINO", "WGHT_EPI", "ACTCODE",
    "STARTIME", "ENDTIME", "PLACE", "ALONE",
    "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM",
    "NHSDCL15", "NHSDC15P", "OTHERS", "PARHSD",
    "NHSDPAR", "MEMBHSD",
]

EPISODE_COLS_2010: list[str] = [
    "RECID", "EPINO", "WGHT_EPI", "ACTCODE",
    "STARTIME", "ENDTIME", "PLACE", "ALONE",
    "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM",
    "NHSDCL15", "NHSDC15P", "OTHERS", "PARHSD",
    "NHSDPAR", "MEMBHSD",
]

EPISODE_COLS_2015: list[str] = [
    "PUMFID", "EPINO", "WGHT_EPI", "TOTEPISO",
    "TUI_01", "STARTIME", "ENDTIME", "LOCATION",
    "TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D",
    "TUI_06E", "TUI_06F", "TUI_06G", "TUI_06H",
    "TUI_06I", "TUI_06J",
    "TUI_07",  # techUse (available from 2015)
    "TUI_10",  # wellbeing (available from 2015)
]

EPISODE_COLS_2022: list[str] = [
    "PUMFID", "INSTANCE", "WGHT_EPI",
    "TUI_01", "STARTIME", "ENDTIME", "LOCATION",
    "TUI_06A", "TUI_06B", "TUI_06C", "TUI_06D",
    "TUI_06E", "TUI_06F", "TUI_06G", "TUI_06H",
    "TUI_06I", "TUI_06J",
    "TUI_07",  # techUse
    "TUI_10",  # wellbeing
]
```

These episode column lists are **verified** against the working reference script (`2ndJ_datapreprocessing.py`).

---

### C. Orchestrator Functions

```python
def read_gss_main(
    cycle_year: int,
    file_path: str,
    syntax_path: str | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Read GSS Main file for a given cycle year."""

def read_gss_episode(
    cycle_year: int,
    file_path: str,
    syntax_path: str | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Read GSS Episode file for a given cycle year."""

def read_all_cycles(
    file_paths: dict[int, dict[str, str]],
    output_dir: str | None = None,
    verbose: bool = False,
) -> dict[int, dict[str, pd.DataFrame]]:
    """Read Main + Episode files for all available cycles.

    Args:
        file_paths: Nested dict mapping cycle_year ->
            {"main": path, "episode": path,
             "syntax_main": path, "syntax_episode": path}.
        output_dir: Optional directory to save CSV outputs.
        verbose: Print progress and diagnostics.

    Returns:
        Dict mapping cycle_year ->
            {"main": df_main, "episode": df_episode}.
    """
```

---

### D. Utility Functions

| Function | Purpose |
|---|---|
| `save_df_to_csv()` | Save DataFrame to CSV (optional, for inspection) |
| `describe_unique_values()` | Print unique values per column (for QA) |
| `print_nan_counts()` | Report NaN counts per column (for QA) |

---

### E. `__main__` Block

Example entry point using the confirmed file paths:

```python
DATA_ROOT = (
    "/Users/orcunkoraliseri/Desktop/Postdoc/occModeling"
    "/0_Occupancy/DataSources_GSS"
)

FILE_PATHS = {
    2005: {
        "main": f"{DATA_ROOT}/Main_files/GSSMain_2005.sas7bdat",
        "episode": f"{DATA_ROOT}/Episode_files/GSS_2005_episode/C19PUMFE_NUM.SAV",
    },
    2010: {
        "main": f"{DATA_ROOT}/Main_files/GSSMain_2010.DAT",
        "syntax_main": f"{DATA_ROOT}/Main_files/GSSMain_2010_syntax.SPS",
        "episode": f"{DATA_ROOT}/Episode_files/GSS_2010_episode/C24EPISODE_withno_bootstrap.DAT",
        "syntax_episode": f"{DATA_ROOT}/Episode_files/GSS_2010_episode/C24_Episode File_SPSS_withno_bootstrap.SPS",
    },
    2015: {
        "main": f"{DATA_ROOT}/Main_files/GSSMain_2015.txt",
        "syntax_main": f"{DATA_ROOT}/Main_files/GSSMain_2015.sps",
        "episode": f"{DATA_ROOT}/Episode_files/GSS_2015_episode/GSS29PUMFE.txt",
        "syntax_episode": f"{DATA_ROOT}/Episode_files/GSS_2015_episode/c29pumfe_e.sps",
    },
    2022: {
        "main": f"{DATA_ROOT}/Main_files/GSSMain_2022.sas7bdat",
        "episode": f"{DATA_ROOT}/Episode_files/GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat",
    },
}
```

---

## Module Structure Summary

```
01_readingGSS.py
├── Constants
│   ├── MAIN_COLS_2005, _2010, _2015, _2022
│   └── EPISODE_COLS_2005, _2010, _2015, _2022
├── File-Format Readers
│   ├── load_spss_file()              — .SAV (2005 Episode)
│   ├── load_dat_with_sps_layout()    — .DAT + .SPS (2010 Main + Episode)
│   ├── parse_spss_syntax_selective() — .sps parser helper
│   ├── read_gss_data_selective()     — .txt + .sps (2015 Main + Episode)
│   └── read_sas_file()               — .sas7bdat (2005/2022 Main, 2022 Episode)
├── Orchestrators
│   ├── read_gss_main()
│   ├── read_gss_episode()
│   └── read_all_cycles()
├── Utilities
│   ├── save_df_to_csv()
│   ├── describe_unique_values()
│   └── print_nan_counts()
└── __main__
    └── Example with confirmed file paths
```

---

## Key Differences from Reference Script

| Aspect | Reference (`2ndJ_datapreprocessing.py`) | New (`01_readingGSS.py`) |
|---|---|---|
| **Scope** | Episode files only + full preprocessing | **Reading & column selection only** (Step 1) |
| **Main file** | Not loaded | **Loaded for all 4 cycles** (2005/2010/2015/2022) |
| **Activity/presence recoding** | Done inline | **Deferred to Step 2** |
| **Co-presence merging** | Done inline | **Deferred to Step 2** |
| **Column renaming** | Done inline | **Deferred to Step 2** |
| **Paths** | Hard-coded old paths | **Updated confirmed paths** under `0_Occupancy/DataSources_GSS/` |
| **Bootstrap weights** | Not loaded | **Excluded entirely** |
| **Type hints / Docstrings** | Minimal | **Full PEP 8 + Google style** |

---

## Verification Plan

### Manual Verification (data-dependent — requires microdata files)

1. **Run `01_readingGSS.py`** with `verbose=True` for one cycle at a time:
   - Confirm file loads without errors
   - Confirm DataFrame shape (row count and column count)
   - Print `df.columns.tolist()` to verify selected columns
   - Print `df.head(10)` for visual inspection
   - Print NaN counts to identify missing columns

2. **Expected column counts** (excluding bootstrap):
   - Main files: ~18–20 demographic + socioeconomic columns
   - Episode files: ~18–20 columns (activity, presence, co-presence)

3. **Verify no preprocessing** occurred:
   - `occACT` / `ACTCODE` / `TUI_01` values should be raw codes, not recoded
   - `PLACE` / `LOCATION` values should be raw, not mapped

4. **Cross-check with reference script output**:
   - Compare Episode columns loaded by `01_readingGSS.py` vs those in `2ndJ_datapreprocessing.py` → should match (same raw columns, before any recoding)

> [!NOTE]
> Since the 2005 Main file column names need verification during the first run, the execution phase will begin with a column discovery step: load the 2005 `.sas7bdat` without column filtering to inspect all available column names, then finalize `MAIN_COLS_2005`.
