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
    columns_to_load_2005 = ["RECID", "EPINO", "WGHT_EPI","ACTCODE", "STARTIME", "ENDTIME", "DURATION", "PLACE",
        "ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "NHSDCL15", "NHSDC15P", "OTHERS", "PARHSD", "NHSDPAR", "MEMBHSD"]

    #df_2005_episode, meta = load_spss_file(GSS_2005_SPSS_episode, selected_columns=columns_to_load_2005)
    #print("df_2005_episode", df_2005_episode.head(10))
    #describe_unique_values(df_2005_episode, exclude_cols=["RECID", "PUMFID", "WGHT_PER"])

    #2010 - gemini
    columns_to_load_2010 = ["RECID", "EPINO", "WGHT_EPI","ACTCODE", "STARTIME", "ENDTIME", "DURATION", "PLACE",
        "ALONE", "SPOUSE", "CHILDHSD", "FRIENDS", "OTHFAM", "NHSDCL15", "NHSDC15P", "OTHERS", "PARHSD", "NHSDPAR", "MEMBHSD"]
    #df_2010_episode = load_dat_with_sps_layout(GSS_2010_SPSS_episode, sps_syntax_2010, selected_columns=columns_to_load_2010)
    #print("df_2010_episode", df_2010_episode.head(10))
    #describe_unique_values(df_2010_episode, exclude_cols=["RECID"])

    # 2015 - Claude
    # Specify only the columns you need
    columns_needed = ['PUMFID', 'EPINO', 'WGHT_EPI', 'TOTEPISO', 'TUI_01', 'STARTIME', 'ENDTIME', 'DURATION',
                      'LOCATION', 'TUI_06A', 'TUI_06B', 'TUI_06C', 'TUI_06D', 'TUI_06E', 'TUI_06F', 'TUI_06G', 'TUI_06H', 'TUI_06I',
                      'TUI_06J']

    # Method 1: Chunked reading (recommended for large files)
    #df_2015_episode = read_gss_data_selective(GSS_2015_SPSS_episode, sps_syntax_2015, columns_to_keep=columns_needed, chunksize=10000)
    #print(df_2015_episode.head(10))
    #describe_unique_values(df_2015_episode, exclude_cols=["PUMFID"])

    #2022 - gemini
    # --- Define your desired columns ---
    # Copied from your list (ensure these names exactly match the SAS file)
    cols_i_want = ['PUMFID', 'INSTANCE', 'WGHT_EPI', 'DUR_03', 'DURATION', 'ENDTIME', 'LOCATION', 'STARTIME', 'TUI_01',
        'TUI_06A', 'TUI_06B', 'TUI_06C', 'TUI_06D', 'TUI_06E','TUI_06F', 'TUI_06G', 'TUI_06H', 'TUI_06I', 'TUI_06J',]
    # Load the episode data
    df_episode_2022 = load_sas_filtered_by_chunk(GSS_2022_SPSS_episode, cols_i_want, chunk_size=100000)
    print(df_episode_2022.head(10))
    #describe_unique_values(df_episode_2022, exclude_cols=["PUMFID"])





