import pandas as pd
import pyreadstat
import re, os
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)  # Adjust as needed, or use None
#--------------------------------------- GEMINI - 2005
def load_spss_file(file_path, selected_columns=None):
    print(f"Reading file: {file_path}...")

    if selected_columns is not None:
        df, meta = pyreadstat.read_sav(file_path, usecols=selected_columns)
    else:
        df, meta = pyreadstat.read_sav(file_path)
    print("Loaded shape:", df.shape)
    return df, meta
#--------------------------------------- GEMINI - 2010
def load_dat_with_sps_layout(dat_file_path, sps_file_path, selected_columns=None):
    """
    Reads a fixed-width .DAT file using SPSS .sps layout (DATA LIST),
    with optional column filtering via `selected_columns`.
    """
    var_regex = re.compile(r"^\s*/?\s*([a-zA-Z0-9_]+)\s+(\d+)\s+-\s+(\d+)")

    column_names = []
    col_specs = []

    print(f"Parsing syntax file: {sps_file_path}")

    with open(sps_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.strip().upper().startswith('VARIABLE LABELS'):
                break  # Stop at label section

            match = var_regex.match(line)
            if match:
                name = match.group(1)
                start_pos = int(match.group(2))
                end_pos = int(match.group(3))

                # Append only if selection is not active OR name is in selection
                if selected_columns is None or name in selected_columns:
                    column_names.append(name)
                    col_specs.append((start_pos - 1, end_pos))

    print(f"Parsing complete. Loading {len(column_names)} column(s).")

    if not column_names:
        print("Error: No matching columns found. Check column names.")
        return None

    print(f"Loading data from: {dat_file_path}")
    df = pd.read_fwf(
        dat_file_path,
        colspecs=col_specs,
        names=column_names,
        dtype="str"
    )
    print("Data loaded successfully.")
    return df
#--------------------------------------- Claude - 2015
def parse_spss_syntax_selective(syntax_file, columns_to_keep=None):
    """
    Parse SPSS syntax file and extract only specified columns.

    Parameters:
    -----------
    syntax_file : str
        Path to the SPSS syntax (.sps) file
    columns_to_keep : list or None
        List of column names to extract. If None, extracts all columns.

    Returns:
    --------
    list : List of tuples (name, start, end, width, dtype) for selected columns
    """
    with open(syntax_file, 'r', encoding='latin-1') as f:
        content = f.read()

    # Extract DATA LIST section
    data_list_match = re.search(r'DATA LIST.*?/(.*?)(?:VARIABLE LABELS|VALUE LABELS|EXECUTE|\Z)',
                                content, re.DOTALL | re.IGNORECASE)

    if not data_list_match:
        raise ValueError("Could not find DATA LIST section in syntax file")

    data_list_section = data_list_match.group(1)

    # Parse variable definitions
    var_pattern = r'(\w+)\s+(\d+)\s*-\s*(\d+)(?:\s*\(([A\d]+)\))?'
    matches = re.findall(var_pattern, data_list_section)

    variables = []
    columns_to_keep_set = set(columns_to_keep) if columns_to_keep else None

    for var_name, start, end, format_spec in matches:
        # Skip if we're filtering and this column is not in the list
        if columns_to_keep_set and var_name not in columns_to_keep_set:
            continue

        start_pos = int(start) - 1  # Convert to 0-based
        end_pos = int(end)
        width = end_pos - start_pos

        # Determine dtype
        if format_spec == 'A':
            dtype = 'str'
        elif format_spec and format_spec.isdigit():
            dtype = 'float'
        else:
            dtype = 'int'

        variables.append((var_name, start_pos, end_pos, width, dtype))

    return variables
def read_gss_data_selective(data_file, syntax_file, columns_to_keep=None, chunksize=10000):
    """
    Fast reading of only selected columns from GSS data file.

    Parameters:
    -----------
    data_file : str
        Path to the GSS data file (.txt)
    syntax_file : str
        Path to the SPSS syntax file (.sps)
    columns_to_keep : list or None
        List of column names to read. If None, reads all columns.
    chunksize : int
        Number of rows to process at a time (default: 10000)

    Returns:
    --------
    pandas.DataFrame : DataFrame containing only the selected columns
    """
    # Parse syntax file for selected columns only
    variables = parse_spss_syntax_selective(syntax_file, columns_to_keep)

    if columns_to_keep:
        print(f"Reading {len(variables)} out of requested {len(columns_to_keep)} columns")
        missing = set(columns_to_keep) - {v[0] for v in variables}
        if missing:
            print(f"Warning: Columns not found in syntax file: {missing}")
    else:
        print(f"Reading all {len(variables)} columns")

    print("Reading data in chunks...")

    # Prepare column specifications
    colspecs = [(var[1], var[2]) for var in variables]
    names = [var[0] for var in variables]

    # Read in chunks - much faster with fewer columns!
    chunks = []
    for i, chunk in enumerate(pd.read_fwf(data_file,
                                          colspecs=colspecs,
                                          names=names,
                                          encoding='latin-1',
                                          chunksize=chunksize,
                                          dtype_backend='numpy_nullable')):
        chunks.append(chunk)
        if (i + 1) % 10 == 0:
            print(f"  Processed {(i + 1) * chunksize} rows...")

    print("Concatenating chunks...")
    df = pd.concat(chunks, ignore_index=True)

    # Convert dtypes based on syntax
    print("Converting data types...")
    for var_name, _, _, _, dtype in variables:
        if dtype == 'float':
            df[var_name] = pd.to_numeric(df[var_name], errors='coerce')
        elif dtype == 'int':
            df[var_name] = pd.to_numeric(df[var_name], errors='coerce').astype('Int64')

    # Reorder columns to match the requested order if specified
    if columns_to_keep:
        # Only keep columns that exist in both lists
        final_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[final_columns]

    return df
def read_gss_data_numpy_selective(data_file, syntax_file, columns_to_keep=None):
    """
    Ultra-fast reading of only selected columns using numpy.

    Parameters:
    -----------
    data_file : str
        Path to the GSS data file (.txt)
    syntax_file : str
        Path to the SPSS syntax file (.sps)
    columns_to_keep : list or None
        List of column names to read. If None, reads all columns.

    Returns:
    --------
    pandas.DataFrame : DataFrame containing only the selected columns
    """
    variables = parse_spss_syntax_selective(syntax_file, columns_to_keep)

    if columns_to_keep:
        print(f"Reading {len(variables)} out of requested {len(columns_to_keep)} columns")
    else:
        print(f"Reading all {len(variables)} columns")

    print("Reading file with numpy...")

    # Read entire file as string array
    with open(data_file, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    print(f"Processing {len(lines)} records...")

    # Extract each column
    data = {}
    for var_name, start_pos, end_pos, width, dtype in variables:
        col_data = [line[start_pos:end_pos].strip() if len(line) > start_pos else '' for line in lines]

        if dtype == 'str':
            data[var_name] = col_data
        else:
            # Convert to numeric
            numeric_data = []
            for val in col_data:
                try:
                    numeric_data.append(float(val) if val else np.nan)
                except ValueError:
                    numeric_data.append(np.nan)

            if dtype == 'int':
                data[var_name] = pd.array(numeric_data, dtype='Int64')
            else:
                data[var_name] = numeric_data

    print("Creating DataFrame...")
    df = pd.DataFrame(data)

    # Reorder columns to match the requested order if specified
    if columns_to_keep:
        final_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[final_columns]

    return df
#--------------------------------------- GEMINI - 2022
def load_sas_filtered_by_chunk(sas_file_path, columns_to_keep, chunk_size=100000):
    """
    Loads specific columns from a SAS (.sas7bdat) file efficiently
    by reading in chunks and filtering each chunk.

    Args:
        sas_file_path (str): The full path to the .sas7bdat file.
        columns_to_keep (list): A list of column names to retain.
        chunk_size (int): The number of rows to read per chunk.

    Returns:
        pandas.DataFrame: The loaded data containing only the specified columns,
                          or None if an error occurs.
    """
    print(f"Reading SAS file in chunks: {sas_file_path}...")
    if not os.path.exists(sas_file_path):
        print(f"❌ Error: File not found at {sas_file_path}")
        return None

    filtered_chunks = []
    try:
        # Create an iterator that yields DataFrame chunks
        reader = pd.read_sas(sas_file_path, chunksize=chunk_size, iterator=True)

        print(f"Processing chunks and keeping only {len(columns_to_keep)} columns...")
        # Iterate through the chunks
        for chunk in reader:
            # Check which of the desired columns actually exist in this chunk
            cols_exist_in_chunk = [col for col in columns_to_keep if col in chunk.columns]
            if not cols_exist_in_chunk:
                print(f"Warning: None of the desired columns found in a chunk. Skipping.")
                continue

            # Filter the chunk to keep only the existing desired columns
            filtered_chunk = chunk[cols_exist_in_chunk]
            filtered_chunks.append(filtered_chunk)

        if not filtered_chunks:
             print("❌ Error: No data loaded. Check if column names are correct.")
             return None

        # Combine all filtered chunks into one DataFrame
        print("Concatenating filtered chunks...")
        full_df = pd.concat(filtered_chunks, ignore_index=True)
        print("✅ Data loaded and filtered successfully.")
        return full_df

    except Exception as e:
        print(f"❌ Error loading or processing SAS file in chunks: {e}")
        return None
#--------------------------------------- EXTRAS
def describe_unique_values(df, exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = []

    for col in df.columns:
        if col in exclude_cols:
            continue

        uniques = df[col].unique()
        print(f"\n--- Column: {col} ---")
        print(f"Unique count: {len(uniques)}")
        print("Unique values:", uniques)
def save_df_to_csv(df, csv_file_path, num_rows=None):
    print(f"Attempting to save data to: {csv_file_path}")

    if num_rows is not None and isinstance(num_rows, int) and num_rows > 0:
        # Save only the first 'num_rows'
        rows_to_save = df.head(num_rows)
        rows_to_save.to_csv(csv_file_path, index=False)
        print(f"✅ Successfully saved the first {len(rows_to_save)} rows to CSV.")
    elif num_rows is None:
        # Save the entire DataFrame
        df.to_csv(csv_file_path, index=False)
        print(f"✅ Successfully saved all {len(df)} rows to CSV.")
    else:
         print("❌ Error: 'num_rows' must be a positive integer or None.")
         return
def load_csv_to_dataframe(csv_file_path):
  """
  Reads a CSV file into a pandas DataFrame.

  Args:
      csv_file_path (str): The full path to the .csv file.

  Returns:
      pandas.DataFrame: The loaded DataFrame, or None if an error occurs.
  """
  print(f"Reading file: {csv_file_path}...")
  if not os.path.exists(csv_file_path):
    print(f"❌ Error: File not found at {csv_file_path}")
    return None

  try:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    print("✅ File loaded successfully.")
    return df
  except Exception as e:
    print(f"❌ Error reading CSV file: {e}")
    return None
def print_nan_counts(csv_file_path):
    """
    Reads a CSV file into a pandas DataFrame, checks for NaN (missing)
    values, and prints the count of NaNs for each column that has them.

    Args:
        csv_file_path (str): The full path to the .csv file.

    Returns:
        pandas.DataFrame: The loaded DataFrame, or None if an error occurs.
    """

    # --- 1. Read the CSV File ---
    print(f"Reading file: {csv_file_path}...")
    if not os.path.exists(csv_file_path):
        print(f"❌ Error: File not found at {csv_file_path}")
        return None

    try:
        # Read the CSV. Using dtype='str' is safer for mixed-type
        # data and avoids many parsing errors.
        df = pd.read_csv(csv_file_path, dtype='str')
        print("✅ File loaded successfully.")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None

    # --- 2. Calculate NaN (Missing) Counts ---

    # Get the sum of nulls for every column
    nan_counts_all = df.isnull().sum()

    # Filter this list to get only columns that *have* missing values
    nan_counts_filtered = nan_counts_all[nan_counts_all > 0]

    # --- 3. Print the Results ---
    print("\n--- NaN (Missing) Value Counts ---")

    if nan_counts_filtered.empty:
        print("✅ No missing (NaN) values found in any column.")
    else:
        # Ensure pandas prints all columns/rows if the list is long
        original_max_rows = pd.get_option('display.max_rows')
        try:
            pd.set_option('display.max_rows', None)  # Temporarily allow unlimited rows
            print(nan_counts_filtered)
        finally:
            pd.set_option('display.max_rows', original_max_rows)  # Reset to default

    return df
#--------------------------------------- EDITING
def load_map_and_save(csv_file_path, column_to_map, activity_mapping, output_csv_path):
    """
    Reads a CSV, converts a specific column based on a mapping dictionary,
    saves the result to a new CSV, prints unmapped values, and returns
    the modified DataFrame.
    """

    # --- 1. Read the CSV ---
    print(f"Reading file: {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"❌ Error: File not found at {csv_file_path}")
        return None

    try:
        df = pd.read_csv(csv_file_path, dtype='str')
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None

    # --- 2. Check if column exists ---
    if column_to_map not in df.columns:
        print(f"❌ Error: Column '{column_to_map}' not found in the CSV.")
        print(f"Available columns are: {df.columns.tolist()}")
        return None

    # --- 3. Store original values & Invert the mapping dictionary ---
    print("Inverting activity mapping dictionary...")

    # *** NEW: Store a copy of the original string values for comparison ***
    original_values_str = df[column_to_map].copy()

    try:
        inverted_map = {
            old_val: new_val
            for new_val, old_val_list in activity_mapping.items()
            for old_val in old_val_list
        }
    except Exception as e:
        print(f"❌ Error processing the mapping dictionary: {e}")
        return None

    # --- 4. Convert target column and map values ---
    print(f"Mapping values in column: {column_to_map}...")

    # Convert original column to numeric to match the map's keys
    # Note: This will turn non-numeric strings (like "Not Stated") into NaN
    df[column_to_map] = pd.to_numeric(df[column_to_map], errors='coerce')

    # Apply the map. Values not in the map will also become NaN.
    df[column_to_map] = df[column_to_map].map(inverted_map)

    # *** NEW: Get a mask of all rows that are now NaN ***
    nan_mask = df[column_to_map].isnull()

    print("✅ Mapping complete.")

    # --- 5. Save the modified DataFrame to a new CSV ---
    print(f"Attempting to save modified data to: {output_csv_path}")
    try:
        output_dir = os.path.dirname(output_csv_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        df.to_csv(output_csv_path, index=False)
        print(f"✅ Successfully saved modified file to: {output_csv_path}")
    except Exception as e:
        print(f"❌ Error saving new CSV: {e}")
        return None

    # --- 6. *** NEW: Report on Unmapped Values *** ---
    print("\n--- Unmapped Values Report ---")

    # Use the nan_mask to find the *original string values* that are now NaN
    unmapped_original_values = original_values_str[nan_mask].unique()

    if len(unmapped_original_values) > 0:
        print(
            f"❌ Found {len(unmapped_original_values)} original values in '{column_to_map}' that were not in the mapping and became NaN:")
        # We print these *original* values so you can see what they were
        print(list(unmapped_original_values))
        print("Note: These might include 'Not Stated', 'Refused', or other codes you need to add to your map.")
    else:
        print("✅ All values were successfully mapped or were already blank.")

    # --- 7. Return the DataFrame for further use ---
    return df

if __name__ == '__main__':
    """
    C19PUMFM_NUM.SAV: This is the Main file containing the core socio-demographic data and the 24-hour time-use diary for all survey respondents.
    C19PUMFE_NUM.SAV: This is the Extended file containing the split-sample variables (e.g., culture, sports, social networks, transportation) that were asked of only a random subset of respondents.
    """
    GSS_2005_SPSS_full = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2005/Data Files SPSS/C19PUMFM_NUM.SAV"
    GSS_2005_SPSS_episode = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2005/Data Files SPSS/C19PUMFE_NUM.SAV"

    GSS_2010_SPSS_episode = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2010/Data_Donn‚es/C24EPISODE_withno_bootstrap.DAT"
    sps_syntax_2010 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2010/Syntax_Syntaxe/SPSS/C24_Episode File_SPSS_withno_bootstrap.SPS"

    GSS_2015_SPSS_episode = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2015/c29_2015/Data_Donn‚es/GSS29PUMFE.txt"
    sps_syntax_2015 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2015/c29_2015/Syntax_Syntaxe/Episode/SPSS/c29pumfe_e.sps"

    GSS_2022_SPSS_episode = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources/Canada_2022/Data_Données/TU_ET_2022_Episode_PUMF.sas7bdat"

    #2005
    columns_to_load_2005 = ["RECID", "EPINO", "WGHT_EPI","ACTCODE", "STARTIME", "ENDTIME", "PLACE",
        "ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "NHSDCL15", "NHSDC15P", "OTHERS", "PARHSD", "NHSDPAR", "MEMBHSD"]

    # READING
    #df_2005_episode, meta = load_spss_file(GSS_2005_SPSS_episode, selected_columns=columns_to_load_2005)
    #print("df_2005_episode", df_2005_episode.head(50))
    #describe_unique_values(df_2005_episode, exclude_cols=["RECID", "PUMFID", "WGHT_PER"])
    df_2005_episode_filtered =  "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/full_2005.csv"
    #save_df_to_csv(df_2005_episode, df_2005_episode_filtered, num_rows=None)

    # EDITING
    # 1. Your mapping dictionary
    mapping_2005 = {
        1: [2, 11, 12, 21, 22, 23, 40, 50, 60, 70, 80, 600, 832, 842],
        13: [30, 90, 190, 291, 292, 390, 491, 492, 590, 674, 691, 692, 791, 792, 793, 871, 872, 873, 891, 892, 893, 894, 990],
        2: [101, 102, 110, 120, 130, 140, 151, 152, 161, 162, 163, 164, 171, 172, 173, 181, 182, 183, 184, 185, 186],
        3: [200, 211, 212, 213, 220, 230, 240, 250, 260, 271, 272, 281, 282, 671, 672, 673, 675, 676, 677, 678],
        4: [301, 302, 303, 304, 310, 320, 331, 332, 340, 350, 361, 362, 370, 380],
        7: [400, 410, 411, 480],
        6: [430, 431],
        9: [440, 751, 752, 753, 754, 760, 770, 780],
        5: [450, 460, 470],
        8: [500, 511, 512, 520, 530, 540, 550, 560, 580],
        12: [610, 620, 630, 640, 642, 651, 652, 660, 661, 680, 800],
        10: [701, 702, 711, 712, 713, 720, 730, 741, 742, 743, 831, 841, 850, 861, 862, 863, 864, 865, 866, 867, 880, 900, 911, 912, 913, 914, 920, 931, 932, 940, 950, 951, 961, 962, 980, 995],
        11: [801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 821, 822]}
    csv_2005_episode_converted =  "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/full_2005_converted.csv"
    #modified_df_2005 = load_map_and_save(df_2005_episode_filtered, "ACTCODE", mapping_2005, csv_2005_episode_converted)
    #df_2005_episode_converted = load_csv_to_dataframe(csv_2005_episode_converted)
    #print_nan_counts(csv_2005_episode_converted)
    #print("df_2005_episode", df_2005_episode_converted.head(50))
    csv_2005_episode_converted_sample = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/sample_2005_converted.csv"
    #save_df_to_csv(df_2005_episode_converted, csv_2005_episode_converted_sample, num_rows=100)

    ####################################################################################################################

    #2010 - gemini
    columns_to_load_2010 = ["RECID", "EPINO", "WGHT_EPI","ACTCODE", "STARTIME", "ENDTIME", "PLACE",
        "ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "NHSDCL15", "NHSDC15P", "OTHERS", "PARHSD", "NHSDPAR", "MEMBHSD"]
    df_2010_episode = load_dat_with_sps_layout(GSS_2010_SPSS_episode, sps_syntax_2010, selected_columns=columns_to_load_2010)
    #print("df_2010_episode", df_2010_episode.head(10))
    #describe_unique_values(df_2010_episode, exclude_cols=["RECID"])
    df_2010_episode_filtered =  "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/full_2010.csv"
    save_df_to_csv(df_2010_episode, df_2010_episode_filtered, num_rows=None)

    # EDITING
    # 1. Your mapping dictionary
    mapping_2010 = {
        1: ["11", "12", "21", "22", "23", "40", "50", "60", "70", "80.1", "80.2", "80.3", "600", "832", "842"],
        13: ["30", "90", "190", "291", "292", "390", "491", "492", "590", "674", "691", "692", "791", "792", "793", "871", "872", "873", "891", "892", "893", "894", "990"],
        2: ["101", "102", "110", "120", "130", "140", "151", "152", "161", "162", "163", "164", "171.1", "171.2", "172", "173", "181.1", "181.2", "181.3", "182", "183", "184", "185", "186", "671.2"],
        3: ["200.1", "200.2", "200.3", "211", "212", "213", "220", "230.1", "230.2", "240", "250.1", "250.2", "260.1", "271.1", "271.2", "271.3", "272.1", "272.2", "281.4", "281.5", "281.8", "281.9", "282.1", "282.2", "282.9", "671.1", "672", "673.1", "673.2", "673.3", "673.4", "673.5", "673.9", "675.1", "675.2", "675.3", "675.4", "675.9", "676", "677", "678"],
        4: ["301", "302.1", "302.2", "302.3", "302.4", "302.9", "303", "304", "310.1", "310.2", "310.3", "320", "331", "332.1", "332.2", "340.1", "340.2", "350.1", "350.2", "350.3", "350.9", "361", "362", "370", "380.1", "380.2", "380.3", "380.4", "380.9"],
        7: ["400", "410.1", "410.2", "410.3", "411", "480"],
        6: ["430", "431"],
        9: ["440", "751", "752", "753", "754", "760", "770", "780.2"],
        5: ["450", "460", "470"],
        8: ["500", "511", "512", "520", "530.1", "530.2", "540", "550", "560.1", "560.2", "580.1", "580.9"],
        12: ["610", "620", "630", "640", "642", "651", "652", "660.1", "660.2", "660.3", "660.4", "660.5", "660.9", "661", "680.1", "680.2", "800"],
        10: ["701", "702", "711", "720", "730", "741", "742", "743", "831", "841", "850.1", "850.2", "861", "862", "862.2", "863", "864", "865", "866", "867.1", "867.9", "880", "900.1", "900.2", "911", "912", "913", "914.1", "914.9", "920", "931", "932.1", "932.2", "940.1", "940.2", "950", "951", "951.1", "951.3", "961", "962", "980.1", "980.9", "995"],
        11: ["801.1", "801.2", "801.4", "801.5", "801.6", "801.7", "801.8", "802.1", "802.2", "803.1", "803.2", "804.1", "804.2", "805.1", "805.2", "805.3", "806.1", "806.2", "807.1", "807.2", "807.3", "807.4", "808", "809", "810", "810.9", "811", "812", "813", "814", "815", "816", "821.1", "821.2", "821.3", "822"]}

    csv_2010_episode_converted =  "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/full_2010_converted.csv"
    modified_df_2010 = load_map_and_save(df_2010_episode_filtered, "ACTCODE", mapping_2010, csv_2010_episode_converted)
    df_2010_episode_converted = load_csv_to_dataframe(csv_2010_episode_converted)
    print_nan_counts(csv_2010_episode_converted)
    #print("df_2010_episode", df_2010_episode_converted.head(50))
    #df_2010_episode_converted_sample = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/sample_2010_converted.csv"
    #save_df_to_csv(df_2010_episode_converted, df_2010_episode_converted_sample, num_rows=100)

    ####################################################################################################################

    # 2015 - Claude
    # Specify only the columns you need
    columns_needed = ['PUMFID', 'EPINO', 'WGHT_EPI', 'TOTEPISO', 'TUI_01', 'STARTIME', 'ENDTIME',
                      'LOCATION', 'TUI_06A', 'TUI_06B', 'TUI_06C', 'TUI_06D', 'TUI_06E', 'TUI_06F', 'TUI_06G', 'TUI_06H', 'TUI_06I',
                      'TUI_06J']

    # Method 1: Chunked reading (recommended for large files)
    #df_2015_episode = read_gss_data_selective(GSS_2015_SPSS_episode, sps_syntax_2015, columns_to_keep=columns_needed, chunksize=10000)
    #print(df_2015_episode.head(10))
    #describe_unique_values(df_2015_episode, exclude_cols=["PUMFID"])

    #2022 - gemini
    # --- Define your desired columns ---
    # Copied from your list (ensure these names exactly match the SAS file)
    cols_i_want = ['PUMFID', 'INSTANCE', 'WGHT_EPI', 'ENDTIME', 'LOCATION', 'STARTIME', 'TUI_01',
        'TUI_06A', 'TUI_06B', 'TUI_06C', 'TUI_06D', 'TUI_06E','TUI_06F', 'TUI_06G', 'TUI_06H', 'TUI_06I', 'TUI_06J',]
    # Load the episode data
    #df_episode_2022 = load_sas_filtered_by_chunk(GSS_2022_SPSS_episode, cols_i_want, chunk_size=100000)
    #print(df_episode_2022.head(10))
    #describe_unique_values(df_episode_2022, exclude_cols=["PUMFID"])





