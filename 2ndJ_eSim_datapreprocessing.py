import pandas as pd
import re
from typing import Dict, Any, List, Union
def read_select_and_save(dat_file_path, sps_file_path, columns_to_select, output_csv_path):
    with open(sps_file_path, 'r', encoding='latin-1') as f:
        sps_content = f.read()

    data_list_match = re.search(
        r'DATA\s+LIST\s+FILE=DATA/\s*(.*?)\s*\.',
        sps_content,
        re.IGNORECASE | re.DOTALL
    )

    if not data_list_match:
        print("Error: 'DATA LIST FILE=DATA/' block not found in .sps file.")
        return None

    var_definitions = data_list_match.group(1)
    var_regex = re.compile(r'([a-zA-Z0-9_]+)\s+(\d+)(?:-(\d+))?')

    all_sps_col_names = []
    col_specs = []

    matches = var_regex.findall(var_definitions)

    if not matches:
        print("Error: No variable definitions found in the DATA LIST block.")
        return None

    for match in matches:
        var_name, start_pos_str, end_pos_str = match
        start_pos = int(start_pos_str) - 1

        if end_pos_str:
            end_pos = int(end_pos_str)
        else:
            end_pos = start_pos + 1

        all_sps_col_names.append(var_name)
        col_specs.append((start_pos, end_pos))

    # --- 1. FAST READ ---
    print(f"Starting fast read of {dat_file_path}...")
    df = pd.read_fwf(
        dat_file_path,
        colspecs=col_specs,
        names=all_sps_col_names,
        header=None,
        dtype='str'  # Read all as strings for max speed
    )
    print("Data loaded. Filtering columns...")

    # --- 2. CASE-INSENSITIVE FILTERING ---
    # Create a mapping of {UPPERCASE_NAME: Original-Case-Name}
    # e.g., {'AGEGRP': 'AGEGRP', 'HH_ID': 'HH_ID'}
    sps_name_map = {name.upper(): name for name in all_sps_col_names}

    final_columns_to_keep = []
    missing_cols = []

    # Loop through user's list and find the correct original-case name
    for col in columns_to_select:
        col_upper = col.upper()
        if col_upper in sps_name_map:
            # Add the correctly cased name from the file (e.g., 'AGEGRP')
            final_columns_to_keep.append(sps_name_map[col_upper])
        else:
            missing_cols.append(col)

    if missing_cols:
        print(f"Warning: The following requested columns were not found in the .sps file: {missing_cols}")

    # Select the columns
    df_filtered = df[final_columns_to_keep]

    # --- 3. SAVE TO CSV ---
    print(f"Saving {len(final_columns_to_keep)} columns to {output_csv_path}...")
    df_filtered.to_csv(output_csv_path, index=False)

    print("Save complete.")
    print(df_filtered.head())
    return df_filtered


def filter_and_save(csv_file_path: str,
                        values_to_remove_dict: Dict[str, Any],
                        output_csv_path: str,
                        value_replace_dict: Dict[str, Dict] = None,
                        column_rename_dict: Dict[str, str] = None):
    """
    Reads a CSV, removes rows (by dict and negatives), replaces
    values (if provided), renames columns (if provided),
    and saves the cleaned data to a new CSV.
    """
    # 1. Read the CSV (as strings for safe filtering).
    df = pd.read_csv(csv_file_path, dtype=str)

    initial_rows = len(df)
    print(f"Read {initial_rows} rows from {csv_file_path}.")

    # 2. Perform dictionary-based filtering
    for column_name, values_to_remove in values_to_remove_dict.items():
        if column_name not in df.columns:
            print(f"Warning: Column '{column_name}' not found. Skipping filter.")
            continue

        if not isinstance(values_to_remove, (list, set, tuple)):
            values_to_remove = [values_to_remove]
        values_to_remove_str = [str(v) for v in values_to_remove]

        mask = ~df[column_name].isin(values_to_remove_str)
        df = df[mask]
    print(f"Rows remaining after dictionary filtering: {len(df)}")

    # 3. Remove rows with any negative values
    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    rows_with_negatives_mask = (df_numeric < 0).any(axis=1)
    df = df[~rows_with_negatives_mask]
    print(f"Rows remaining after removing negative values: {len(df)}")

    # --- 4. NEW STEP: Replace unique values ---
    if value_replace_dict:
        print("Starting value replacement...")
        for col_name, replacement_map in value_replace_dict.items():
            if col_name not in df.columns:
                print(f"  - Warning: Column '{col_name}' not found. Skipping replacement.")
                continue

            # Convert map keys/values to string to match the str-read dataframe
            replacement_map_str = {str(k): str(v) for k, v in replacement_map.items()}

            # .replace() handles simultaneous swaps (e.g., 0->1 and 1->2) correctly
            df[col_name] = df[col_name].replace(replacement_map_str)
            print(f"  - Values replaced in column '{col_name}'.")

    # --- 5. Rename columns ---
    if column_rename_dict:
        missing_keys = list(set(column_rename_dict.keys()) - set(df.columns))
        if missing_keys:
            print(f"  - Warning: Original columns not found for renaming: {missing_keys}")

        df = df.rename(columns=column_rename_dict)
        print("Column renaming step complete.")

    # --- 6. Save the final filtered DataFrame ---
    rows_removed = initial_rows - len(df)
    print(f"\nRemoved {rows_removed} rows in total.")
    print(f"Saving {len(df)} rows to {output_csv_path}...")

    # 4. Print the head of the resulting DataFrame
    print("\n--- Head of the final, filtered data ---")
    print(df.head())

    df.to_csv(output_csv_path, index=False)

    print("Save complete.")
    return df

# BALANCE & CHECK
def print_column_info(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # 1. Print total row count
    print(f"--- Total Row Count: {len(df)} ---")

    # 2. Calculate and print empty (NaN) counts
    empty_counts = df.isnull().sum()
    print(f"\n--- Empty Row Counts for: {csv_file_path} ---")
    print(empty_counts)

    # 3. Find and print unique values for each column
    print("\n--- Unique Values for Each Column ---")
    for column in df.columns:
        # Get unique values
        unique_values = df[column].unique()

        # Check if number of unique values is large
        if len(unique_values) > 100:
            print(f"Column '{column}': (Too many unique values to display > 100)")
        else:
            print(f"Column '{column}': {unique_values}")

if __name__ == '__main__':
    census_2006 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2006/Hier2006.dat"
    census_2006_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2006/English/SAS - SPSS Command files/Hier_en.sps"
    census_2006_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2006_filtered.csv"
    census_2006_filtered2 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2006_filtered2.csv"

    census_2011 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2011/data_donnees.dat"
    census_2011_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2011/English/SAS, SPSS and STATA command files/SPSS.sps"
    census_2011_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2011_filtered.csv"
    census_2011_filtered2 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2011_filtered2.csv"

    census_2016 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2016/data_donnees_2016_hier.dat"
    census_2016_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2016/English/SAS, SPSS and STATA command files/2016 Hierarchical PUMF SPSS EN.sps"
    census_2016_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2016_filtered.csv"
    census_2016_filtered2 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2016_filtered2.csv"

    census_2021 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2021/data_donnees_2021_hier_v2.dat"
    census_2021_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2021/English/SAS, SPSS and STATA command files/PUMF2021_Hierarchical_spss_en.sps"
    census_2021_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2021_filtered.csv"
    census_2021_filtered2 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2021_filtered2.csv"

    """
    #CENSUS2006
    #read_select_and_save(census_2006, census_2006_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AgeGrp", "SEX", "KOL", "AttSch", "CIP", "NOCS", "EmpIn", "TotInc", "BROOMH", "Room", "DType"], census_2006_filtered)
    filter_and_save(csv_file_path=census_2006_filtered, 
                    values_to_remove_dict={'AGEGRP': [88],  'ATTSCH': '9', 'CIP': [12, 88, 99],'NOCS': [88, 99]}, 
                    output_csv_path=census_2006_filtered2, 
                    column_rename_dict={"BROOMH": "BEDRM"})
    print_column_info(census_2006_filtered2) # unique values, total row count, empty rows
    #CENSUS2011
    #read_select_and_save(census_2011, census_2011_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "KOL", "ATTSCH", "CIP2011", "NOCS", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"], census_2011_filtered)
    filter_and_save(csv_file_path=census_2011_filtered, 
                    values_to_remove_dict={'AGEGRP': [88],  'ATTSCH': '9', 'CIP2011': [12, 88, 99],'NOCS': [88, 99], "BEDRM": [8], "ROOM": [88]}, 
                    output_csv_path=census_2011_filtered2, 
                    column_rename_dict={"CIP2011": "CIP"})
    print_column_info(census_2011_filtered2) # unique values, total row count, empty rows
    """
    """
    #CENSUS2016
    #read_select_and_save(census_2016, census_2016_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "KOL", "ATTSCH", "CIP2011", "NOCS", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"], census_2016_filtered)
    filter_and_save(csv_file_path=census_2016_filtered, 
                    values_to_remove_dict={'AGEGRP': [88], 'ATTSCH': '9', "BEDRM": [8], 'CIP2011': [88, 99], "DTYPE": [8],"KOL": [8], 'NOCS': [88, 99], "ROOM": [88], "SEX": [8]}, 
                    output_csv_path=census_2016_filtered2, 
                    column_rename_dict={"CIP2011": "CIP"})
    print_column_info(census_2016_filtered2) # unique values, total row count, empty rows
    
    #CENSUS2021
    #read_select_and_save(census_2021, census_2021_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "GENDER", "KOL", "ATTSCH", "CIP2021", "NOC21", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"], census_2021_filtered)
    filter_and_save(csv_file_path=census_2021_filtered,
                    values_to_remove_dict={'AGEGRP': [88], 'ATTSCH': [8], "BEDRM": [8], 'CIP2021': [12, 88, 99], "DTYPE": [8], "GENDER": [8], "KOL": [8], 'NOC21': [88, 99], "ROOM": [88], "SEX": [8]},
                    output_csv_path=census_2021_filtered2,
                    column_rename_dict={"NOC21": "NOCS", "CIP2021": "CIP", "GENDER": "SEX"},
                    value_replace_dict= {"ATTSCH": {0: 1, 1: 2}})
    print_column_info(census_2021_filtered2) # unique values, total row count, empty rows
    """