# Implementation Plan — `01_readingGSS_2split.py`
## STEP 1: Data Collection & Column Selection

---

## Goal

Document the data collection and column selection step for the **Leg-2 two-channel (Residential + Office/AT_WORK)** pipeline. This step is a **reuse + delta**: the Leg-1 reader (`01_readingGSS.py`) already extracts all residential Main and Episode columns for all four GSS cycles (2005, 2010, 2015, 2022) and is **reused unchanged**. The Leg-2 delta is solely the addition of **office employment-gating Main columns** to the per-cycle `MAIN_COLS_*` lists. The Episode side needs **no new columns**: `occPRE` (the harmonized 18-category location variable) is already extracted and carried through the Leg-1 pipeline; `AT_WORK = (occPRE == 2)` is a derived flag computed later at Step 2/3 tiling — not at read time.

The suggested script name for the Leg-2 reader is `01_readingGSS_2split.py`. It would live alongside this doc in `Step1_docs/` and write outputs to `Step1_docs/outputs_step1/`. This file is a **documentation deliverable only** — no Python code is written or executed in this step.

**Bootstrap weight columns (`WTBS_*`, `WTBS_EPI_*`) remain excluded** from this pipeline, as in Leg 1.

---

## Reference

- **Leg-2 pipeline overview**: `3J_docs_occ_nTemp\Leg2_2-split\00_2split_Occupancy_Pipeline.md` (Step 1 and Step 2 sections)
- **Leg-1 reader doc (template)**: `2J_docs_occ_nTemp\01_readingGSS.md`
- **Leg-1 reader script (reused)**: `01_readingGSS.py`
- **Split suitability audit**: `3J_docs_occ_nTemp\00_GSS_split_suitability_audit.md` (Section 4 — office employment variables; Section 3 — `occPRE` wiring)
- **Column name reference**: `0_Occupancy\DataSources_GSS\gss_headers.csv`

---

## Data Source Inventory

All data files are located under:
```
C:\Users\o_iseri\Desktop\Postdoc\occModeling\0_Occupancy\DataSources_GSS\
```

### Main Files

| Cycle | File | Format | Reader |
|---|---|---|---|
| 2005 | `Main_files\GSSMain_2005.sas7bdat` (321 MB) | SAS | `read_sas_file()` |
| 2010 | `Main_files\GSSMain_2010.DAT` + `GSSMain_2010_syntax.SPS` | Fixed-width `.DAT` + `.SPS` | `load_dat_with_sps_layout()` |
| 2015 | `Main_files\GSSMain_2015.txt` + `GSSMain_2015.sps` (102 MB) | Fixed-width + SPSS syntax | `read_gss_data_selective()` |
| 2022 | `Main_files\GSSMain_2022.sas7bdat` (41 MB) | SAS | `read_sas_file()` |

### Episode Files

| Cycle | File | Format | Reader |
|---|---|---|---|
| 2005 | `Episode_files\GSS_2005_episode\C19PUMFE_NUM.SAV` (27 MB) | SPSS `.SAV` | `load_spss_file()` |
| 2010 | `Episode_files\GSS_2010_episode\C24EPISODE_withno_bootstrap.DAT` + `C24_Episode File_SPSS_withno_bootstrap.SPS` (22 MB) | Fixed-width `.DAT` + `.SPS` | `load_dat_with_sps_layout()` |
| 2015 | `Episode_files\GSS_2015_episode\GSS29PUMFE.txt` + `c29pumfe_e.sps` (1.4 GB) | Fixed-width `.txt` + `.sps` | `read_gss_data_selective()` |
| 2022 | `Episode_files\GSS_2022_episode\TU_ET_2022_Episode_PUMF.sas7bdat` (471 MB) | SAS | `read_sas_file()` |

> [!NOTE]
> The 2005 episode directory also contains `C19PUMFM_NUM.SAV` (a Main file in SPSS format, 216 MB). Either the `.sas7bdat` from `Main_files\` or this `.SAV` fallback can be loaded — both contain the same 2005 Main data.

---

## Proposed Changes

### [NEW] `Step1_docs\01_readingGSS_2split.py`

---

### A. File-Format Reader Functions

**✅ DONE (Leg 1, reused)** — All five reader functions are carried forward from `01_readingGSS.py` with no modification.

| Function | Format | Used For | Status |
|---|---|---|---|
| `load_spss_file()` | `.SAV` (SPSS) | 2005 Episode | ✅ DONE (Leg 1, reused) |
| `load_dat_with_sps_layout()` | `.DAT` + `.SPS` | 2010 Main + Episode | ✅ DONE (Leg 1, reused) |
| `parse_spss_syntax_selective()` | `.sps` parser | Helper for 2015 | ✅ DONE (Leg 1, reused) |
| `read_gss_data_selective()` | `.txt` + `.sps` | 2015 Main + Episode | ✅ DONE (Leg 1, reused) |
| `read_sas_file()` | `.sas7bdat` | 2005 Main, 2022 Main + Episode | ✅ DONE (Leg 1, reused) |

Each reader accepts `file_path`, `selected_columns`, `output_csv` (optional), and `verbose` parameters.

---

### B. Column Selection Constants

#### Main File Columns — Office Gating Delta (⚠️ PLANNED, Leg 2)

The residential `MAIN_COLS_*` lists (occID, SURVMNTH, PR, HHSIZE, AGEGRP, SEX, MARSTH, KOL, ATTSCH, NOCS, LFTAG, COW, HRSWRK, CMA, POWST, TOTINC, WGHT_PER, DDAY) are **reused unchanged from Leg 1**. The Leg-2 delta appends the office employment-gating variables below — shown here as additions only, not full replacement lists.

Column names are sourced from `00_GSS_split_suitability_audit.md` §4 (employment gating table), cross-referenced with `00_2split_Occupancy_Pipeline.md` §1A.

```python
# ── 2005 (C19 PUMF) — Office gating additions ──────────────────────────────
# Source: audit §4; raw cycle codebook Codebook_2005/
MAIN_COLS_2005 += [
    "MAR_Q100",      # Main activity last week (also gates worked-last-week; no separate WKLTWE in 2005)
    "LFSGSS",        # Labour-force status (exclude retired / unemployed)
    "WKWEHR_C",      # Usual hours worked per week (cross-check diary AT_WORK hours)
    "MAR_Q172",      # Class of worker (employee / self-employed / etc.)
    "SOC91C10",      # Occupation — NOC 1991 10-cat (office vs non-office bucket)
    "NAICS2002_C16", # Industry — NAICS 2002, 16-cat (office vs non-office bucket)
    # Telework / WFH: no variable available in 2005 PUMF
]
```

```python
# ── 2010 (C24 PUMF) — Office gating additions ──────────────────────────────
# Source: audit §4; raw cycle codebook Codebook_2010/
MAIN_COLS_2010 += [
    "MAR_Q100",       # Main activity last week (primary gate; see also ACT7DAYS if available)
    "WKLTWE",         # Worked last week Y/N (dedicated gate — not available in 2005)
    "LFSGSS",         # Labour-force status
    "WKWEHR_C",       # Usual hours worked per week
    "MAR_Q172",       # Class of worker
    "NOCS2006_C10",   # Occupation — NOC 2006, 10-cat
    "NAICS2007_C16",  # Industry — NAICS 2007, 16-cat
    "MAR_Q190",       # Telework / works at home (WFH signal for 2010)
]
```

```python
# ── 2015 (C29 PUMF) — Office gating additions ──────────────────────────────
# Source: audit §4; raw cycle codebook Codebook_2015/
# ⚠️ WET_120 (class of worker) is SUPPRESSED in the 2015 PUMF — see note below.
MAIN_COLS_2015 += [
    "ACT7DAYS",      # Main activity last week
    "MRW_D40B",      # Worked last week Y/N
    # Labour-force status: derived from existing residential vars; no separate LFSGSS in 2015
    "WHWD140C",      # Hours worked per week — grouped (preferred)
    # "WHW_D141",    # Hours worked continuous (alternative; include if WHWD140C is insufficient)
    # "WET_120",     # Class of worker ⚠️ SUPPRESSED in 2015 PUMF — DO NOT REQUEST
    #                #   Fallback: WLY_150 (terms of employment) for employee-vs-self-employed proxy
    "NOC1110Y",      # Occupation — NOC 2011, 10-cat, main job (use NOC1110W for second job if needed)
    "NAIC12CY",      # Industry — NAICS 2012, collapsed, main job
    "WTI_130",       # Telework / reason for working at home (WFH signal for 2015)
]
```

```python
# ── 2022 (GSSP PUMF) — Office gating additions ─────────────────────────────
# Source: audit §4; raw cycle codebook Codebook_2022/
MAIN_COLS_2022 += [
    "ACT7DAYC",      # Main activity last week
    "MRW_D40B",      # Worked last week Y/N
    # Labour-force status: derived; no separate LFSGSS in 2022 PUMF
    "WHWD140G",      # Hours worked per week — grouped
    "WET_120",       # Class of worker (available and unsuppressed in 2022)
    "NOCLBR_Y",      # Occupation — NOC 2021, collapsed — already in residential list; confirm no duplicate
    "NAIC22CY",      # Industry — NAICS 2022, collapsed
    "TLWK_01A",      # Telework: did any telework last week (Y/N)
    "TLWK_01B",      # Telework: telework days (if available in PUMF)
    "TLWK_01C",      # Telework: hours teleworked
    "TLWK_01D",      # Telework: additional telework detail
    "TLWK_02G",      # Telework: employer expectation / arrangement type
]
```

> [!IMPORTANT]
> **2015 class-of-worker suppression.** `WET_120` (class of worker) is suppressed in the 2015 PUMF and must NOT be requested — doing so will either raise a `KeyError` or return an all-NaN column depending on the reader. Use `WLY_150` (terms of employment) as an employee-vs-self-employed proxy for 2015 if the archetype step requires that distinction. Source: `00_GSS_split_suitability_audit.md` §4.

> [!NOTE]
> **2022 TLWK columns.** `TLWK_01A–D` and `TLWK_02G` are listed in the audit table. The exact availability of `TLWK_01B/C/D` in the public PUMF (vs the master file) should be confirmed during the initial column-discovery load of the 2022 `.sas7bdat`. If any are absent, `TLWK_01A` alone is sufficient to flag whether telework occurred.

> [!NOTE]
> **`NOCLBR_Y` overlap (2022).** The residential `MAIN_COLS_2022` list already includes `NOCLBR_Y` (mapped to NOCS in Leg 1). When constructing the combined column list, deduplicate — include it once.

#### Episode File Columns — Unchanged (✅ DONE, Leg 1, reused)

The Episode column lists are reused without modification. The key fact for Leg 2: `occPRE` is already extracted as part of the harmonized episode output produced by `02_harmonizeGSS.py` and is present on every episode row in all four cycles. `AT_WORK = (occPRE == 2)` is derived at Step 2/3 tiling — it is not a new survey column and requires no change here.

| Cycle | Episode columns | Status |
|---|---|---|
| 2005 | `RECID`, `EPINO`, `WGHT_EPI`, `ACTCODE`, `STARTIME`, `ENDTIME`, `PLACE`, `ALONE`, `SPOUSE`, `CHILDHSD`, `FRIENDS`, `OTHFAM`, `NHSDCL15`, `NHSDC15P`, `OTHERS`, `PARHSD`, `NHSDPAR`, `MEMBHSD` | ✅ DONE (Leg 1, reused) |
| 2010 | Same as 2005 | ✅ DONE (Leg 1, reused) |
| 2015 | `PUMFID`, `EPINO`, `WGHT_EPI`, `TOTEPISO`, `TUI_01`, `STARTIME`, `ENDTIME`, `LOCATION`, `TUI_06A–J`, `TUI_07`, `TUI_10` | ✅ DONE (Leg 1, reused) |
| 2022 | `PUMFID`, `INSTANCE`, `WGHT_EPI`, `TUI_01`, `STARTIME`, `ENDTIME`, `LOCATION`, `TUI_06A–J`, `TUI_07`, `TUI_10` | ✅ DONE (Leg 1, reused) |

---

### C. Orchestrator Functions

**✅ DONE (Leg 1, reused)** — The three orchestrators carry forward with no structural change. The only modification is that the `MAIN_COLS_*` dicts passed to `read_gss_main()` are the expanded (residential + office) lists from Section B above.

```python
def read_gss_main(
    cycle_year: int,
    file_path: str,
    syntax_path: str | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Read GSS Main file for a given cycle year.
    Leg 2: receives the expanded MAIN_COLS_* that include office gating columns."""

def read_gss_episode(
    cycle_year: int,
    file_path: str,
    syntax_path: str | None = None,
    output_csv: str | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Read GSS Episode file for a given cycle year.
    Leg 2: unchanged — occPRE (AT_WORK source) already extracted in Leg 1."""

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
            Leg 2 target: Step1_docs/outputs_step1/
        verbose: Print progress and diagnostics.

    Returns:
        Dict mapping cycle_year ->
            {"main": df_main, "episode": df_episode}.
    """
```

---

### D. Utility Functions

**✅ DONE (Leg 1, reused)** — All three utility functions carry forward unchanged.

| Function | Purpose | Status |
|---|---|---|
| `save_df_to_csv()` | Save DataFrame to CSV (optional, for inspection) | ✅ DONE (Leg 1, reused) |
| `describe_unique_values()` | Print unique values per column (for QA) | ✅ DONE (Leg 1, reused) |
| `print_nan_counts()` | Report NaN counts per column (for QA) | ✅ DONE (Leg 1, reused) |

---

### E. `__main__` Block

**⚠️ PLANNED (Leg 2)** — Entry point for `01_readingGSS_2split.py`. Writes outputs to `Step1_docs\outputs_step1\`.

```python
DATA_ROOT = (
    r"C:\Users\o_iseri\Desktop\Postdoc\occModeling"
    r"\0_Occupancy\DataSources_GSS"
)
OUTPUT_DIR = r"Step1_docs\outputs_step1"  # relative to script location

FILE_PATHS = {
    2005: {
        "main":    f"{DATA_ROOT}\\Main_files\\GSSMain_2005.sas7bdat",
        "episode": f"{DATA_ROOT}\\Episode_files\\GSS_2005_episode\\C19PUMFE_NUM.SAV",
    },
    2010: {
        "main":         f"{DATA_ROOT}\\Main_files\\GSSMain_2010.DAT",
        "syntax_main":  f"{DATA_ROOT}\\Main_files\\GSSMain_2010_syntax.SPS",
        "episode":      f"{DATA_ROOT}\\Episode_files\\GSS_2010_episode\\C24EPISODE_withno_bootstrap.DAT",
        "syntax_episode": (
            f"{DATA_ROOT}\\Episode_files\\GSS_2010_episode"
            "\\C24_Episode File_SPSS_withno_bootstrap.SPS"
        ),
    },
    2015: {
        "main":          f"{DATA_ROOT}\\Main_files\\GSSMain_2015.txt",
        "syntax_main":   f"{DATA_ROOT}\\Main_files\\GSSMain_2015.sps",
        "episode":       f"{DATA_ROOT}\\Episode_files\\GSS_2015_episode\\GSS29PUMFE.txt",
        "syntax_episode": f"{DATA_ROOT}\\Episode_files\\GSS_2015_episode\\c29pumfe_e.sps",
    },
    2022: {
        "main":    f"{DATA_ROOT}\\Main_files\\GSSMain_2022.sas7bdat",
        "episode": f"{DATA_ROOT}\\Episode_files\\GSS_2022_episode\\TU_ET_2022_Episode_PUMF.sas7bdat",
    },
}

# Output: main_<cycle>.csv and episode_<cycle>.csv written to OUTPUT_DIR
# e.g. outputs_step1/main_2005.csv, outputs_step1/episode_2005.csv, ...
```

---

## Module Structure Summary

```
01_readingGSS_2split.py
├── Constants
│   ├── MAIN_COLS_2005  = Leg-1 residential cols + office gating additions  ⚠️ PLANNED (Leg 2)
│   ├── MAIN_COLS_2010  = Leg-1 residential cols + office gating additions  ⚠️ PLANNED (Leg 2)
│   ├── MAIN_COLS_2015  = Leg-1 residential cols + office gating additions  ⚠️ PLANNED (Leg 2)
│   │                     (⚠️ WET_120 suppressed — excluded; WLY_150 proxy if needed)
│   ├── MAIN_COLS_2022  = Leg-1 residential cols + office gating additions  ⚠️ PLANNED (Leg 2)
│   └── EPISODE_COLS_2005/_2010/_2015/_2022  — unchanged from Leg 1        ✅ DONE (Leg 1)
├── File-Format Readers                                                     ✅ DONE (Leg 1, reused)
│   ├── load_spss_file()              — .SAV (2005 Episode)
│   ├── load_dat_with_sps_layout()    — .DAT + .SPS (2010 Main + Episode)
│   ├── parse_spss_syntax_selective() — .sps parser helper
│   ├── read_gss_data_selective()     — .txt + .sps (2015 Main + Episode)
│   └── read_sas_file()               — .sas7bdat (2005/2022 Main, 2022 Episode)
├── Orchestrators                                                           ✅ DONE (Leg 1, reused)
│   ├── read_gss_main()      — receives expanded MAIN_COLS_* in Leg 2
│   ├── read_gss_episode()   — unchanged
│   └── read_all_cycles()    — output_dir → Step1_docs/outputs_step1/
├── Utilities                                                               ✅ DONE (Leg 1, reused)
│   ├── save_df_to_csv()
│   ├── describe_unique_values()
│   └── print_nan_counts()
└── __main__                                                                ⚠️ PLANNED (Leg 2)
    └── FILE_PATHS + OUTPUT_DIR → outputs_step1/main_<cycle>.csv
                                  outputs_step1/episode_<cycle>.csv
```

---

## Key Differences from Reference Script

The reference for this table is the Leg-1 reader `01_readingGSS.py`, not the older `2ndJ_datapreprocessing.py`.

| Aspect | Leg-1 (`01_readingGSS.py`) | Leg-2 (`01_readingGSS_2split.py`) |
|---|---|---|
| **Main columns — residential** | Full residential set (18–20 cols/cycle) | Reused unchanged ✅ DONE |
| **Main columns — office gating** | Not included | Added per cycle: `MAR_Q100/ACT7DAYS/ACT7DAYC`, `WKLTWE/MRW_D40B`, `LFSGSS`, hours, COW, NOC, NAICS, telework ⚠️ PLANNED |
| **2015 class-of-worker** | N/A (not selected) | `WET_120` suppressed — excluded; `WLY_150` proxy documented ⚠️ PLANNED |
| **Episode columns** | Full episode set (18–20 cols/cycle) | Reused unchanged — `occPRE` already present ✅ DONE |
| **AT_WORK derivation** | Not performed | Deferred to Step 2/3 tiling: `AT_WORK = (occPRE == 2)` — not at read time ⚠️ PLANNED |
| **Output directory** | `outputs/` (Leg-1 default) | `Step1_docs/outputs_step1/` ⚠️ PLANNED |
| **Output filenames** | `main_<cycle>.csv`, `episode_<cycle>.csv` | Same naming convention ⚠️ PLANNED |
| **File-format readers** | 5 readers (SPSS, DAT/SPS, SAS) | Reused unchanged ✅ DONE |
| **Orchestrators** | `read_gss_main/episode/all_cycles` | Reused; MAIN_COLS_* expanded in Leg 2 |

---

## Verification Plan

### Step 1 — Column Discovery (run before final column lists are locked)

For each cycle, load the Main file **without column filtering** and print `df.columns.tolist()`. This is especially important for:
- **2005**: confirms whether `MAR_Q100`, `LFSGSS`, `WKWEHR_C`, `MAR_Q172`, `SOC91C10`, `NAICS2002_C16` are present under those exact names (2005 column names can be lowercase or use alternate spellings).
- **2022 telework**: confirms which of `TLWK_01A/B/C/D` and `TLWK_02G` are present in the public PUMF vs the master file.
- **2015**: confirms `WET_120` is absent (suppressed), `MRW_D40B` is present, and telework variable `WTI_130` name is correct.

### Step 2 — Load with Selected Columns

Run `01_readingGSS_2split.py` with `verbose=True` for one cycle at a time:
- Confirm file loads without `KeyError` or shape mismatch.
- Print `df.shape` — Main row counts should match Leg-1 outputs exactly (same respondents; only more columns selected).
- Print `df[office_cols].head(10)` to spot-check values look like expected codes (not all-NaN, not all-zero).
- Print `print_nan_counts(df)` to confirm office columns are populated (non-trivial NaN rate is expected for non-workers, but should not be 100%).

### Step 3 — Episode Unchanged Verification

Confirm `episode_<cycle>.csv` output is bit-identical to the Leg-1 `01_readingGSS.py` episode output for the same cycle — no new episode columns should have been added.

### Step 4 — Expected Column Counts

| Cycle | Leg-1 Main cols | Leg-2 Main cols (approx.) | Episode cols |
|---|---|---|---|
| 2005 | ~18 | ~24–25 (+ 6 office cols, no telework) | ~18 (unchanged) |
| 2010 | ~18 | ~26–27 (+ 8 office cols) | ~18 (unchanged) |
| 2015 | ~20 | ~27–28 (+ 7 office cols, WET_120 excluded) | ~20 (unchanged) |
| 2022 | ~20 | ~27–30 (+ 7–10 office cols, depending on TLWK availability) | ~20 (unchanged) |

> [!NOTE]
> Since the 2005 Main file uses non-standard column name casing and some office-gating names are confirmed from the codebook but not yet verified against the live `.sas7bdat`, the execution phase must begin with a full column-discovery load of the 2005 file. Finalize `MAIN_COLS_2005` after inspection.

---

## Progress Log

### 2026-06-13 — Initial Leg-2 Step-1 doc authored

Authored the Leg-2 Step-1 detail document (`01_readingGSS.md`) for the two-channel Residential + Office pipeline. The doc covers: (1) the reuse-plus-delta framing — Leg-1 reader and all five format readers are carried forward unchanged; (2) the per-cycle office employment-gating Main column additions (`MAR_Q100`/`ACT7DAYS`/`ACT7DAYC` for main activity, `WKLTWE`/`MRW_D40B` for worked-last-week, `LFSGSS` for LF status, hours-worked grouped variables, class-of-worker, NOC occupation, NAICS industry, and telework variables per cycle); (3) the Episode-side rationale for no new columns (`occPRE == 2` → `AT_WORK` is deferred to Step 2/3 tiling); (4) verification plan including column-discovery pre-check.

**Open caveat: 2015 class-of-worker suppression.** `WET_120` is confirmed suppressed in the 2015 PUMF (source: `00_GSS_split_suitability_audit.md` §4). It is excluded from `MAIN_COLS_2015` in this doc. If the archetype step (Step 5) requires an employee-vs-self-employed split for the 2015 cycle, the proxy variable `WLY_150` (terms of employment) should be evaluated and added. This decision is deferred to Step 5 planning.

---

### 2026-06-13 — Reader implemented (`01_readingGSS_2split.py`)

**Copied from Leg 1:**
All five file-format readers (`load_spss_file`, `load_dat_with_sps_layout`, `parse_spss_syntax_selective`, `read_gss_data_selective`, `read_sas_file`), three orchestrators (`read_gss_main`, `read_gss_episode`, `read_all_cycles`), three utility functions (`save_df_to_csv`, `describe_unique_values`, `print_nan_counts`), all rename maps (`MAIN_RENAME_MAP`, `EPISODE_RENAME_MAP`, `apply_rename_map`), all four `EPISODE_COLS_*` constants, and the cross-platform `__main__` block are reproduced verbatim from `2J_docs_occ_nTemp/01_readingGSS.py`. The `__main__` subprocess call to `01_readingGSS_val.py` was intentionally dropped (no Leg-2 validation script exists yet).

**Office columns added per cycle (net of dedupe):**

| Cycle | Columns already in Leg-1 (deduped) | Net additions |
|---|---|---|
| 2005 | `LFSGSS`, `WKWEHR_C`, `MAR_Q172` | `MAR_Q100`, `SOC91C10`, `NAICS2002_C16` (no telework in 2005) |
| 2010 | `LFSGSS`, `WKWEHR_C`, `MAR_Q172` | `MAR_Q100`, `WKLTWE`, `NOCS2006_C10`, `NAICS2007_C16`, `MAR_Q190` |
| 2015 | `ACT7DAYS`, `WHWD140C`, `NOC1110Y` | `MRW_D40B`, `NAIC12CY`, `WTI_130` (`WET_120` excluded — suppressed) |
| 2022 | `ACT7DAYC`, `WET_120`, `NOCLBR_Y`, `WHWD140G` | `MRW_D40B`, `NAIC22CY`, `TLWK_01A`, `TLWK_01B`, `TLWK_01C`, `TLWK_01D`, `TLWK_02G` |

**Dedupe handled:** 2005: 3 columns skipped (LFSGSS, WKWEHR_C, MAR_Q172). 2010: 3 columns skipped (same). 2015: 3 columns skipped (ACT7DAYS, WHWD140C, NOC1110Y); WET_120 intentionally excluded (suppressed). 2022: 4 columns skipped (ACT7DAYC, WET_120, NOCLBR_Y, WHWD140G). Also: 2010 `MAR_Q190` was already in the Leg-1 residential list (as POWST source) — confirmed present in Leg-1 2010 list; excluded from the office delta row above.

**Best-effort / missing-column behaviour:** No new wrapping was added. The existing readers already handle absent columns gracefully: `load_spss_file` intersects against metadata before calling `read_sav`; `load_dat_with_sps_layout` and `parse_spss_syntax_selective` filter to columns found in the syntax file; `read_sas_file` filters each chunk to columns present in that chunk. Missing office columns will trigger the existing `Warning: Columns not found` print at `verbose=True` and be silently omitted from the output — residential columns are unaffected. The module docstring calls this out explicitly and flags which TLWK columns (01B/C/D) are unconfirmed in the public PUMF.

**Output directory:** `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step1_docs\outputs_step1` (Windows); analogous path on macOS. Output filenames: `main_<cycle>.csv` / `episode_<cycle>.csv` (unchanged from Leg 1).

**py_compile result:** `py -3 -m py_compile 01_readingGSS_2split.py` → CLEAN (exit 0, no errors or warnings).
