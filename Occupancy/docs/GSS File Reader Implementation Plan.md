# GSS File Reader Implementation Plan

This plan outlines the implementation of a Python module to read GSS (General Social Survey) main files from different years and extract their column headers to a CSV file.

## Background & Context

The GSS datasets contain time-use survey data from Statistics Canada across three years with different file formats:

| Year | File Format | Size | Columns | Metadata |
|------|-------------|------|---------|----------|
| 2005 | `.sas7bdat` | ~321 MB | 2,531 | Embedded in file |
| 2015 | `.txt` + `.sps` | ~102 MB | 848 | Separate SPS specification |
| 2022 | `.sas7bdat` | ~41 MB | 968 | Embedded in file |

### Key Observations

1. **SAS7BDAT files (2005, 2022)**: Can be read directly using `pandas.read_sas()` - headers are embedded in the file format.

2. **TXT + SPS pair (2015)**: The `.txt` file is a fixed-width format without headers. The `.sps` file is an SPSS syntax file that defines:
   - Variable names and their column positions
   - Data types and decimal places
   - The format follows: `VARNAME  start_col - end_col`

## Proposed Changes

### occ_utils (Utility Module)

#### [NEW] [gss_reader.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/occ_utils/gss_reader.py)

A Python module located in `eSim/occ_utils/` with the following structure:

```python
"""
GSS (General Social Survey) File Reader Module

Provides functionality to read GSS main files from different years
and extract column headers to CSV format.
"""

# Functions implemented:

def read_sas7bdat_headers(filepath: str) -> list[str]:
    """Read headers from a SAS7BDAT file."""
    
def parse_sps_headers(sps_filepath: str) -> list[str]:
    """Parse variable names from SPSS syntax (.sps) file."""
    
def read_gss_headers(data_dir: str) -> dict[str, list[str]]:
    """
    Read headers from all GSS files in a directory.
    
    Returns:
        Dictionary mapping year/filename to list of headers
    """

def save_headers_to_csv(headers_dict: dict[str, list[str]], output_path: str) -> None:
    """
    Save headers to CSV with each dataset as a separate column.
    
    Output format (wide format):
        column_index,GSSMain_2005,GSSMain_2015,GSSMain_2022
        0,MSS_Q140,PUMFID,PUMFID
        1,MSS_Q115,WGHT_PER,WGHT_PER
        ...
    """

def main():
    """Entry point for reading all GSS files and saving headers."""
```

**Key Implementation Details:**

1. **SAS7BDAT Reading:**
   - Use `pandas.read_sas()` with `chunksize` parameter to avoid loading entire dataset
   - Only read first row to get column names efficiently

2. **SPS Parsing:**
   - Parse the `DATA LIST` section using regex
   - Extract variable names from lines matching pattern: `VARNAME  start - end`
   - Handle optional decimal specifiers like `(4)`

3. **Output CSV Format (Wide Format):**
   - Each dataset becomes a separate column
   - Rows are aligned by column index
   - Empty cells for datasets with fewer columns
   - Format: `column_index,GSSMain_2005,GSSMain_2015,GSSMain_2022`

---

### Occupancy/DataSources_GSS

#### [NEW] [gss_headers.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy/DataSources_GSS/gss_headers.csv)

Output file containing all extracted headers in wide format:
```csv
column_index,GSSMain_2005,GSSMain_2015,GSSMain_2022
0,MSS_Q140,PUMFID,PUMFID
1,MSS_Q115,WGHT_PER,WGHT_PER
2,MSS_Q110,SURVMNTH,SURVMNTH
3,ACT7DAYS,AGEGR10,EQFLAG
...
```

**Note:** The 2005 dataset has the most columns (2,531), so rows 849-2530 will have empty values for 2015 and rows 969-2530 will have empty values for 2022.

## Project Structure

```
eSim/
├── occ_utils/
│   └── gss_reader.py           <- Main Python module
└── Occupancy/
    ├── DataSources_GSS/
    │   ├── Main_files/
    │   │   ├── GSSMain_2005.sas7bdat
    │   │   ├── GSSMain_2015.txt
    │   │   ├── GSSMain_2015.sps
    │   │   └── GSSMain_2022.sas7bdat
    │   └── gss_headers.csv     <- Output file
    └── docs/
        ├── GSS File Reader Implementation Plan.md
        └── GSS File Reader Implementation Plan.pdf
```

## Verification Plan

### Automated Tests

1. **Run the script:**
   ```bash
   cd /Users/orcunkoraliseri/Desktop/Postdoc/eSim/occ_utils
   python3 gss_reader.py
   ```

2. **Verify output file exists and contains expected data:**
   ```bash
   head -20 /Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy/DataSources_GSS/gss_headers.csv
   wc -l gss_headers.csv
   ```

3. **Validate header counts match file structures:**
   - 2005: 2,531 headers
   - 2015: 848 headers
   - 2022: 968 headers
   - Total rows in CSV: 2,532 (2,531 data rows + 1 header row)

### Manual Verification

- Review the CSV output to confirm headers are correctly extracted and formatted
- Verify that each dataset appears as a separate column
- Compare a sample of headers between the output CSV and original files
