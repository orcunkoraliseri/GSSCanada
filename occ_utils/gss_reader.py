"""
GSS (General Social Survey) File Reader Module.

Provides functionality to read GSS main files from different years
(2005, 2015, 2022) and extract column headers to CSV format.

Supported file formats:
    - .sas7bdat: SAS data files (headers embedded)
    - .txt + .sps: Fixed-width text files with SPSS syntax specification
"""

import os
import re
import csv
from pathlib import Path

import pandas as pd


def read_sas7bdat_headers(filepath: str) -> list[str]:
    """
    Read column headers from a SAS7BDAT file.
    
    Uses chunked reading to avoid loading the entire dataset into memory.
    
    Args:
        filepath: Path to the .sas7bdat file.
        
    Returns:
        List of column names from the file.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed as SAS7BDAT.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        # Read with iterator to get only column names without loading all data
        reader = pd.read_sas(filepath, encoding='latin1', chunksize=1)
        chunk = next(reader)
        headers = list(chunk.columns)
        reader.close()
        return headers
    except Exception as e:
        raise ValueError(f"Error reading SAS7BDAT file: {e}") from e


def parse_sps_headers(sps_filepath: str) -> list[str]:
    """
    Parse variable names from an SPSS syntax (.sps) file.
    
    The SPS file defines fixed-width column positions in the format:
        VARNAME  start_col - end_col [decimal_places]
    
    Args:
        sps_filepath: Path to the .sps file.
        
    Returns:
        List of variable names in order of appearance.
        
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(sps_filepath):
        raise FileNotFoundError(f"File not found: {sps_filepath}")
    
    headers = []
    
    # Pattern to match variable definitions:
    # VARNAME  start - end [decimal]
    # Examples:
    #   PUMFID                                1 -       5
    #   WGHT_PER                              6 -      15   (4)
    var_pattern = re.compile(
        r'^\s+([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)\s*-\s*(\d+)'
    )
    
    with open(sps_filepath, 'r', encoding='utf-8', errors='replace') as f:
        in_data_list = False
        
        for line in f:
            # Check if we're in the DATA LIST section
            if 'DATA LIST' in line.upper():
                in_data_list = True
                continue
            
            # End of variable definitions (usually marked by a period or new command)
            if in_data_list and line.strip() == '.':
                break
            
            if in_data_list:
                match = var_pattern.match(line)
                if match:
                    var_name = match.group(1)
                    headers.append(var_name)
    
    return headers


def read_gss_headers(data_dir: str) -> dict[str, list[str]]:
    """
    Read headers from all GSS files in a directory.
    
    Automatically detects file types and uses appropriate parsing method:
        - .sas7bdat files: Read directly with pandas
        - .txt files: Look for corresponding .sps file for column definitions
    
    Args:
        data_dir: Path to directory containing GSS files.
        
    Returns:
        Dictionary mapping source filename to list of headers.
        
    Example:
        >>> headers = read_gss_headers('/path/to/Main_files')
        >>> headers['GSSMain_2005']
        ['PUMFID', 'WGHT_PER', ...]
    """
    data_path = Path(data_dir)
    headers_dict = {}
    
    # Find all SAS7BDAT files
    for sas_file in data_path.glob('*.sas7bdat'):
        source_name = sas_file.stem
        print(f"Reading SAS file: {sas_file.name}")
        headers_dict[source_name] = read_sas7bdat_headers(str(sas_file))
        print(f"  Found {len(headers_dict[source_name])} columns")
    
    # Find all TXT files with corresponding SPS files
    for txt_file in data_path.glob('*.txt'):
        sps_file = txt_file.with_suffix('.sps')
        if sps_file.exists():
            source_name = txt_file.stem
            print(f"Reading TXT+SPS pair: {txt_file.name}")
            headers_dict[source_name] = parse_sps_headers(str(sps_file))
            print(f"  Found {len(headers_dict[source_name])} columns")
        else:
            print(f"Warning: No SPS file found for {txt_file.name}, skipping")
    
    return headers_dict


def save_headers_to_csv(
    headers_dict: dict[str, list[str]], 
    output_path: str
) -> None:
    """
    Save headers to CSV with each dataset as a separate column.
    
    Output format:
        column_index,GSSMain_2005,GSSMain_2015,GSSMain_2022
        0,MSS_Q140,PUMFID,PUMFID
        1,MSS_Q115,WGHT_PER,WGHT_PER
        ...
    
    Args:
        headers_dict: Dictionary mapping source name to list of headers.
        output_path: Path for the output CSV file.
    """
    # Get sorted source names for consistent column order
    source_names = sorted(headers_dict.keys())
    
    # Find the maximum number of columns across all datasets
    max_columns = max(len(headers) for headers in headers_dict.values())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header row: column_index, dataset1, dataset2, ...
        writer.writerow(['column_index'] + source_names)
        
        # Write each row with column index and header names from each dataset
        for idx in range(max_columns):
            row = [idx]
            for source_name in source_names:
                headers = headers_dict[source_name]
                # Use empty string if this dataset has fewer columns
                if idx < len(headers):
                    row.append(headers[idx])
                else:
                    row.append('')
            writer.writerow(row)
    
    print(f"\nHeaders saved to: {output_path}")


def main() -> None:
    """
    Entry point for reading all GSS files and saving headers.
    
    Reads GSS files from the Main_files directory and saves
    all column headers to a CSV file.
    """
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Define paths - navigate from occ_utils to Occupancy/DataSources_GSS
    occupancy_dir = script_dir.parent / 'Occupancy'
    main_files_dir = occupancy_dir / 'DataSources_GSS' / 'Main_files'
    output_csv = occupancy_dir / 'DataSources_GSS' / 'gss_headers.csv'
    
    print("=" * 60)
    print("GSS File Reader - Header Extraction")
    print("=" * 60)
    print(f"\nSource directory: {main_files_dir}")
    print(f"Output file: {output_csv}\n")
    
    # Read headers from all files
    headers_dict = read_gss_headers(str(main_files_dir))
    
    # Save to CSV
    save_headers_to_csv(headers_dict, str(output_csv))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    total_headers = 0
    for source_name, headers in sorted(headers_dict.items()):
        print(f"  {source_name}: {len(headers)} columns")
        total_headers += len(headers)
    print(f"\nTotal: {total_headers} column headers extracted")


if __name__ == '__main__':
    main()
