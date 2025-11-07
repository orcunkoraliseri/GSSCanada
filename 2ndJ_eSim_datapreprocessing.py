import pandas as pd
import re
def read_filter_and_save(dat_file_path, sps_file_path, columns_to_select, output_csv_path):
    """
    Reads a .dat file using an .sps file, filters for specific columns,
    and saves the result to a new CSV file.

    This function is case-insensitive for the 'columns_to_select' list.
    """
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

if __name__ == '__main__':
    census_2006 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2006/Hier2006.dat"
    census_2006_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2006/English/SAS - SPSS Command files/Hier_en.sps"
    census_2006_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2006_filtered.csv"

    census_2011 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2011/data_donnees.dat"
    census_2011_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2011/English/SAS, SPSS and STATA command files/SPSS.sps"
    census_2011_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2011_filtered.csv"

    census_2016 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2016/data_donnees_2016_hier.dat"
    census_2016_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2016/English/SAS, SPSS and STATA command files/2016 Hierarchical PUMF SPSS EN.sps"
    census_2016_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2016_filtered.csv"

    census_2021 = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2021/data_donnees_2021_hier_v2.dat"
    census_2021_sps = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Data Sources - Census/census_2021/English/SAS, SPSS and STATA command files/PUMF2021_Hierarchical_spss_en.sps"
    census_2021_filtered = "/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs/Census/census_2021_filtered.csv"

    """
    #CENSUS2006
    read_filter_and_save(census_2006, census_2006_sps, 
                         ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AgeGrp", "SEX", "KOL", "AttSch", "CIP", "NOCS", "EmpIn", "TotInc", "BROOMH", "Room", "DType"], 
                         census_2006_filtered)
    
    
    #CENSUS2011
    read_filter_and_save(census_2011, census_2011_sps,
                         ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "KOL", "ATTSCH", "CIP2011", "NOCS", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"],
                         census_2011_filtered)
    
    #CENSUS2016
    read_filter_and_save(census_2016, census_2016_sps,
                         ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "SEX", "KOL", "ATTSCH", "CIP2011", "NOCS", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"],
                         census_2016_filtered)
    """
    #CENSUS2021
    read_filter_and_save(census_2021, census_2021_sps,
                         ["HH_ID", "EF_ID", "CF_ID", "PP_ID", "CMA", "AGEGRP", "GENDER", "KOL", "ATTSCH", "CIP2021", "NOC21", "EMPIN", "TOTINC", "BEDRM", "ROOM", "DTYPE"],
                         census_2021_filtered)
