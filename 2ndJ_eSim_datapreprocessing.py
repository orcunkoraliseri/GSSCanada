import math
import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import re
from typing import Dict, Any, List, Union
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
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
                        recategorize_dict: Dict[str, Dict] = None,
                        column_rename_dict: Dict[str, str] = None):
    """
    Reads a CSV, removes rows, replaces values, re-categorizes values,
    renames columns, and saves the cleaned data to a new CSV.

    Args:
        csv_file_path (str): Path to the input CSV file.
        values_to_remove_dict (dict): Dict of values to remove.
        output_csv_path (str): Path to save the filtered output CSV file.
        value_replace_dict (dict, optional): Nested dict for 1-to-1
            replacements, e.g., {'COL_A': {1: 2, 0: 1}}.
        recategorize_dict (dict, optional): Nested dict for many-to-one
            replacements, e.g., {'COL_B': {'NewVal_A': [1, 2, 3],
                                           'NewVal_B': [4, 5, 6]}}.
        column_rename_dict (dict, optional): A dictionary to rename
            columns, e.g., {'OldName': 'NewName'}.
    """
    # 1. Read the CSV (as strings for safe filtering).
    df = pd.read_csv(csv_file_path, dtype=str)
    initial_rows = len(df)
    print(f"Read {initial_rows} rows from {csv_file_path}.")

    # 2. Perform dictionary-based filtering
    for col_name, values in values_to_remove_dict.items():
        if col_name not in df.columns:
            print(f"Warning: Column '{col_name}' not found. Skipping filter.")
            continue
        if not isinstance(values, (list, set, tuple)):
            values = [values]
        values_str = [str(v) for v in values]
        df = df[~df[col_name].isin(values_str)]
    print(f"Rows remaining after dictionary filtering: {len(df)}")

    # 3. Remove rows with any negative values
    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    rows_with_negatives_mask = (df_numeric < 0).any(axis=1)
    df = df[~rows_with_negatives_mask]
    print(f"Rows remaining after removing negative values: {len(df)}")

    # 4. Replace 1-to-1 unique values
    if value_replace_dict:
        print("Starting 1-to-1 value replacement...")
        for col_name, replace_map in value_replace_dict.items():
            if col_name not in df.columns:
                print(f"  - Warning: Column '{col_name}' not found. Skipping 1-to-1 replacement.")
                continue
            replace_map_str = {str(k): str(v) for k, v in replace_map.items()}
            df[col_name] = df[col_name].replace(replace_map_str)
            print(f"  - 1-to-1 values replaced in column '{col_name}'.")

    # --- 5. NEW STEP: Re-categorize (many-to-one) values ---
    if recategorize_dict:
        print("Starting value re-categorization...")
        for col_name, mapping in recategorize_dict.items():
            if col_name not in df.columns:
                print(f"  - Warning: Column '{col_name}' not found. Skipping re-categorization.")
                continue

            # Invert the user's mapping to create the final replacement dict
            # e.g., {'NewVal_A': [1, 2], 'NewVal_B': [3, 4]}
            # becomes: {1: 'NewVal_A', 2: 'NewVal_A', 3: 'NewVal_B', 4: 'NewVal_B'}

            # We must convert all items to strings for safe .replace()
            final_replace_map = {}
            for new_value, list_of_old_values in mapping.items():
                new_value_str = str(new_value)
                for old_value in list_of_old_values:
                    final_replace_map[str(old_value)] = new_value_str

            # Apply the replacement
            df[col_name] = df[col_name].replace(final_replace_map)
            print(f"  - Values re-categorized in column '{col_name}'.")

    # --- 6. Rename columns ---
    if column_rename_dict:
        missing_keys = list(set(column_rename_dict.keys()) - set(df.columns))
        if missing_keys:
            print(f"  - Warning: Original columns not found for renaming: {missing_keys}")

        df = df.rename(columns=column_rename_dict)
        print("Column renaming step complete.")

    # --- 7. Save the final filtered DataFrame ---
    rows_removed = initial_rows - len(df)
    print(f"\nRemoved {rows_removed} rows in total.")
    print(f"Saving {len(df)} rows to {output_csv_path}...")

    df.to_csv(output_csv_path, index=False)

    # 4. Print the head of the resulting DataFrame
    print("\n--- Head of the final, filtered data ---")
    print(df)

    return df

def add_household_size_to_csv(csv_file_path: str):
    """
    Reads a CSV file, adds an 'HHSIZE' column based on 'HH_ID'
    counts, and saves back to the same file.

    Note: This function has no error handling.
    """
    # 1. Read the CSV file
    df = pd.read_csv(csv_file_path)

    # 2. Calculate HHSIZE
    # This will raise a KeyError if 'HH_ID' is not in df.columns
    hh_size_series = df.groupby('HH_ID')['HH_ID'].transform('count')

    # 3. Add or update the 'HHSIZE' column
    df['HHSIZE'] = hh_size_series

    # 4. Save the modified DataFrame back to the same file
    df.to_csv(csv_file_path, index=False)

    print(f"Successfully added 'HHSIZE' and saved to {csv_file_path}")

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

    # 4. Print the head of the resulting DataFrame
    print("\n--- Head of the final, filtered data ---")
    print(df)

# VISUALIZATION
def plot_value_counts(csv_file_path, columns_to_exclude: list, output_image_path: str):
    # 1. Ensure output directory exists (by checking the file's parent)
    output_file = pathlib.Path(output_image_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 2. Read the CSV data
    df = pd.read_csv(csv_file_path, dtype=str)

    # 3. Determine which columns to plot
    all_columns = df.columns.tolist()

    # Filter out excluded columns
    columns_to_plot_prelim = [
        col for col in all_columns if col not in columns_to_exclude
    ]

    # Filter out columns with too many unique values (guardrail)
    columns_to_plot = []
    for col in columns_to_plot_prelim:
        if df[col].nunique() > 50:
            print(f"Info: Column '{col}' has > 50 unique values. Skipping plot.")
        else:
            columns_to_plot.append(col)

    if not columns_to_plot:
        print("No columns to plot. Aborting.")
        return

    # 4. Calculate subplot grid size
    n_plots = len(columns_to_plot)
    ncols = 5  # Let's fix at 2 columns for better readability
    nrows = int(math.ceil(n_plots / ncols))

    # 5. Create the subplots
    # We create a figure 'fig' and an array of axes 'axes'
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 3.5 * nrows))

    # Flatten the 2D 'axes' array into a 1D list for easy iteration
    axes_flat = axes.flatten()

    print(f"--- Generating {n_plots} subplots in one image ---")

    # 6. Loop through each column and its assigned subplot axis
    for i, col in enumerate(columns_to_plot):
        ax = axes_flat[i]  # Get the current axis

        # Get the value counts and sort by the index (the category)
        counts = df[col].value_counts().sort_index()

        # Plot *directly onto the axis* (ax)
        counts.plot(kind='bar', ax=ax)

        # Set titles and labels *on the axis*
        ax.set_title(f"Value Counts for Column: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency / Count")
        ax.tick_params(axis='x', rotation=45)

    # 7. Turn off any unused subplots
    # (e.g., if we have 5 plots in a 3x2 grid, turn off the 6th)
    for j in range(n_plots, len(axes_flat)):
        axes_flat[j].axis('off')

    # 8. Adjust layout and save the *entire figure*
    fig.tight_layout()
    fig.savefig(output_image_path)
    plt.close(fig)  # Close the figure to free memory

    print(f"Successfully saved combined chart to: {output_image_path}")

def plot_comparison_by_column(csv_files_dict: Dict[str, str],
                              columns_to_exclude: List[str],
                              output_dir: str):
    # 1. Ensure output directory exists
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 2. Get columns to plot
    first_file_path = list(csv_files_dict.values())[0]
    df_temp = pd.read_csv(first_file_path, dtype=str, nrows=0)
    all_columns = df_temp.columns.tolist()

    columns_to_plot = [
        col for col in all_columns if col not in columns_to_exclude
    ]

    print(f"--- Starting Comparison Plots (excluding {columns_to_exclude}) ---")

    # 3. Loop through each COLUMN we want to compare (e.g., 'AGEGRP')
    for col in columns_to_plot:

        # Guardrail: Check for too many unique values
        df_proxy = pd.read_csv(first_file_path, dtype=str, usecols=[col])
        if df_proxy[col].nunique() > 50:
            print(f"Info: Column '{col}' has > 50 unique values. Skipping plot.")
            continue

        print(f"Processing column: {col}")

        # 4. Create a new figure with 4 subplots (2x2 grid)
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 12))
        axes_flat = axes.flatten()
        fig.suptitle(f"Comparison of Column: {col} (2006-2021)", fontsize=16)

        # 5. Loop through the CSV files dictionary
        plot_num = 0
        for year, file_path in csv_files_dict.items():
            if plot_num >= 4:
                break

            ax = axes_flat[plot_num]
            df = pd.read_csv(file_path, dtype=str, usecols=[col])

            # 6. Plot the data for this year/file
            counts = df[col].value_counts()

            # --- FIX FOR SORTING IS HERE ---
            # Try to convert the index (categories) to numeric
            # This allows sorting 1, 2, ... 10, 11 instead of 1, 10, 11, 2
            try:
                # Convert index to numeric and sort
                counts.index = pd.to_numeric(counts.index)
                counts = counts.sort_index()
            except ValueError:
                # If conversion fails (e.g., 'M', 'F'), just sort alphabetically
                counts = counts.sort_index()
            # --- END FIX ---

            counts.plot(kind='bar', ax=ax)

            ax.set_title(f"Year: {year}")
            ax.set_xlabel(None)
            ax.set_ylabel("Frequency / Count")
            ax.tick_params(axis='x', rotation=45)

            plot_num += 1

        # 7. Turn off any unused subplots
        for i in range(plot_num, 4):
            axes_flat[i].axis('off')

        # 8. Save the combined figure
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        save_path = output_path / f"{col}_comparison.png"
        fig.savefig(save_path)
        plt.close(fig)

        print(f"  -> Saved comparison plot to: {save_path}")

if __name__ == '__main__':
    BASE_DIR = pathlib.Path("C:/Users/o_iseri/Desktop/2ndJournal")

    DATA_DIR = BASE_DIR / "DataSources"
    OUTPUT_DIR = BASE_DIR / "Outputs"

    # --- 2006 Files ---
    cen06 = DATA_DIR / "cen06.dat"
    cen06_sps = DATA_DIR / "cen06.sps"
    cen06_filtered = OUTPUT_DIR / "cen06_filtered.csv"
    cen06_filtered2 = OUTPUT_DIR / "cen06_filtered2.csv"

    # --- 2011 Files ---
    cen11 = DATA_DIR / "cen11.dat"
    cen11_sps = DATA_DIR / "cen11.sps"
    cen11_filtered = OUTPUT_DIR / "cen11_filtered.csv"
    cen11_filtered2 = OUTPUT_DIR / "cen11_filtered2.csv"

    # --- 2016 Files ---
    cen16 = DATA_DIR / "cen16.dat"
    cen16_sps = DATA_DIR / "cen16.sps"
    cen16_filtered = OUTPUT_DIR / "cen16_filtered.csv"
    cen16_filtered2 = OUTPUT_DIR / "cen16_filtered2.csv"

    # --- 2021 Files ---
    cen21 = DATA_DIR / "cen21.dat"
    cen21_sps = DATA_DIR / "cen21.sps"
    cen21_filtered = OUTPUT_DIR / "cen21_filtered.csv"
    cen21_filtered2 = OUTPUT_DIR / "cen21_filtered2.csv"

    """
    #CENSUS2006
    #read_select_and_save(cen06, cen06_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AgeGrp", "SEX", "KOL", "AttSch", "CIP", "NOCS", "EmpIn", "TotInc", "BROOMH", "Room", "DType"], cen06_filtered)
    #filter_and_save(csv_file_path=cen06_filtered,
    #                values_to_remove_dict={'AGEGRP': [88],  'ATTSCH': '9', 'CIP': [12, 88, 99],'NOCS': [88, 99]},
    #                output_csv_path=cen06_filtered2,
    #                column_rename_dict={"BROOMH": "BEDRM"},
    #                recategorize_dict={"DTYPE": {1: [1],  2: [4, 5, 6],   3: [2, 3, 7, 8] }})
    #add_household_size_to_csv(csv_file_path=cen06_filtered2)
    #print_column_info(cen06_filtered2) # unique values, total row count, empty rows
    #plot_value_counts(csv_file_path=cen06_filtered2, columns_to_exclude= ["HH_ID", "EF_ID", "CF_ID", "PP_ID",], output_image_path=OUTPUT_DIR / "plot06.png")

    #CENSUS2011
    #read_select_and_save(cen11, cen11_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "KOL", "ATTSCH", "CIP2011", "NOCS", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"], cen11_filtered)
    #filter_and_save(csv_file_path=cen11_filtered,
    #                values_to_remove_dict={'AGEGRP': [88],  'ATTSCH': '9', 'CIP2011': [12, 88, 99],'NOCS': [88, 99], "BEDRM": [8], "ROOM": [88]},
    #                output_csv_path=cen11_filtered2,
    #                column_rename_dict={"CIP2011": "CIP"},
    #                recategorize_dict={"DTYPE": {1: [1],  2: [4, 5, 6],   3: [2, 3, 7, 8] }})
    #add_household_size_to_csv(csv_file_path=cen11_filtered2)
    #print_column_info(cen11_filtered2) # unique values, total row count, empty rows
    plot_value_counts(csv_file_path=cen11_filtered2, columns_to_exclude= ["HH_ID", "EF_ID", "CF_ID", "PP_ID",], output_image_path=OUTPUT_DIR / "plot11.png")
    """
    """
    #CENSUS2016
    #read_select_and_save(cen16, cen16_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "KOL", "ATTSCH", "CIP2011", "NOCS", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"], cen16_filtered)
    #filter_and_save(csv_file_path=cen16_filtered,
    #                values_to_remove_dict={'AGEGRP': [88], 'ATTSCH': '9', "BEDRM": [8], 'CIP2011': [88, 99], "DTYPE": [8],"KOL": [8], 'NOCS': [88, 99], "ROOM": [88], "SEX": [8]},
    #                output_csv_path=cen16_filtered2,
    #                column_rename_dict={"CIP2011": "CIP"})
    #add_household_size_to_csv(csv_file_path=cen16_filtered2)
    #print_column_info(cen16_filtered2) # unique values, total row count, empty rows
    plot_value_counts(csv_file_path=cen16_filtered2, columns_to_exclude= ["HH_ID", "EF_ID", "CF_ID", "PP_ID",], output_image_path=OUTPUT_DIR / "plot16.png")

   
    #CENSUS2021
    #read_select_and_save(cen21, cen21_sps, ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "GENDER", "KOL", "ATTSCH", "CIP2021", "NOC21", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"], cen21_filtered)
    #filter_and_save(csv_file_path=cen21_filtered,
    #                values_to_remove_dict={'AGEGRP': [88], 'ATTSCH': [8], "BEDRM": [8], 'CIP2021': [12, 88, 99], "DTYPE": [8], "GENDER": [8], "KOL": [8], 'NOC21': [88, 99], "ROOM": [88], "SEX": [8]},
    #                output_csv_path=cen21_filtered2, column_rename_dict={"NOC21": "NOCS", "CIP2021": "CIP", "GENDER": "SEX"},
    #                value_replace_dict= {"ATTSCH": {0: 1, 1: 2}})
    #add_household_size_to_csv(csv_file_path=cen21_filtered2)
    #print_column_info(cen21_filtered2) # unique values, total row count, empty rows
    plot_value_counts(csv_file_path=cen21_filtered2, columns_to_exclude= ["HH_ID", "EF_ID", "CF_ID", "PP_ID",], output_image_path=OUTPUT_DIR / "plot21.png")
    """

    # 2. Define your inputs
    csv_paths = {'2006': cen06_filtered2, '2011': cen11_filtered2, '2016': cen16_filtered2, '2021': cen21_filtered2}
    # Define which columns you want to *skip*
    cols_to_exclude = ["HH_ID", "EF_ID", "CF_ID", "PP_ID",]
    # 3. Run the function
    plot_comparison_by_column(csv_paths, cols_to_exclude, OUTPUT_DIR)
