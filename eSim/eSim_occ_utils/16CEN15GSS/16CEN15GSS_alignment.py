"""
16CEN15GSS Alignment Module

Reads GSS 2015 data, merges with demographics, and aligns with Census 2016
for occupancy modeling. Maps Census values to GSS value schemes for consistent
comparison.

Usage:
    python 16CEN15GSS_alignment.py
"""

import uuid
import pathlib
import os
import math
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Union, Tuple, List


# =============================================================================
# GSS 2015 COLUMN DEFINITIONS
# =============================================================================

# Columns to extract from GSS 2015 Main file
COLS_MAIN_15 = [
    'PUMFID',      # Key for merging -> occID
    'PRV',         # Province -> PR
    'HSDSIZEC',    # Household Size -> HHSIZE
    'AGEGR10',     # Age group -> AGEGRP
    'SEX',         # Sex -> SEX (direct)
    'MARSTAT',     # Marital Status -> MARSTH
    'LAN_01',      # Language -> KOL
    'ACT7DAYS',    # Labour Force -> LFTAG
    'LUC_RST',     # Urban/Rural -> CMA
    'INCG1',       # Income Group -> TOTINC
    'PHSDFLG',     # Reference Person Helper
    'CXRFLAG',     # Reference Person Helper
    'PARNUM',      # Parent Number Helper
    'DVTDAY',      # Day Type (Weekday/Weekend) -> DDAY
]

# Rename map: GSS 2015 names -> Census standard names
RENAME_MAP_15 = {
    'PUMFID': 'occID',
    'PRV': 'PR',
    'HSDSIZEC': 'HHSIZE',
    'AGEGR10': 'AGEGRP',
    'SEX': 'SEX',
    'MARSTAT': 'MARSTH',
    'LAN_01': 'KOL',
    'ACT7DAYS': 'LFTAG',
    'LUC_RST': 'CMA',
    'INCG1': 'TOTINC',
    'DVTDAY': 'DDAY',
}


# =============================================================================
# HOUSEHOLD ASSEMBLY (Census 2016)
# =============================================================================

def assemble_households(
    csv_file_path: Union[str, pathlib.Path],
    target_year: int,
    output_dir: Union[str, pathlib.Path],
    start_id: int = 100
) -> pd.DataFrame:
    """
    Reads filtered Census CSV, reconstructs households, saves the LINKED CSV.

    Uses simple sequential IDs (100, 101, 102...) for households.

    Args:
        csv_file_path: Path to the filtered census CSV file.
        target_year: Target year for the data (e.g., 2016).
        output_dir: Directory to save the linked output.
        start_id: Starting household ID number.

    Returns:
        DataFrame with assembled household data.
    """
    print(f"\n--- Assembling Households for {target_year} ---")
    print(f"   Loading data from: {csv_file_path}")

    # 1. LOAD DATA
    df_population = pd.read_csv(csv_file_path)

    # Generate PIDs (Personal IDs) - UUIDs to distinguish people within house
    df_population['PID'] = [str(uuid.uuid4())[:8] for _ in range(len(df_population))]

    # Ensure Types
    df_population['HHSIZE'] = (
        pd.to_numeric(df_population['HHSIZE'], errors='coerce')
        .fillna(1)
        .astype(int)
    )
    df_population['CF_RP'] = (
        df_population['CF_RP']
        .astype(str)
        .str.replace('.0', '', regex=False)
    )

    final_households = []
    current_hh_id = start_id

    # --- PHASE 1: SINGLES (HHSIZE = 1) ---
    singles_mask = df_population['HHSIZE'] == 1
    df_singles = df_population[singles_mask].copy()

    if not df_singles.empty:
        num_singles = len(df_singles)
        df_singles['SIM_HH_ID'] = range(current_hh_id, current_hh_id + num_singles)
        current_hh_id += num_singles
        final_households.append(df_singles)

    print(f"   Processed {len(df_singles)} Single-Person Households.")

    # Remove singles from the pool
    df_remaining = df_population[~singles_mask].copy()

    # --- PHASE 2: FAMILIES (Heads = 1) ---
    df_family_heads = df_remaining[df_remaining['CF_RP'] == '1'].copy()
    df_members_2 = df_remaining[df_remaining['CF_RP'] == '2'].copy()
    df_members_3 = df_remaining[df_remaining['CF_RP'] == '3'].copy()

    pool_family_mem = df_members_2.sample(frac=1.0).to_dict('records')
    pool_non_family = df_members_3.sample(frac=1.0).to_dict('records')

    print(f"   Assembling {len(df_family_heads)} Family Households (Heads)...")

    family_batch = []
    for _, head_series in df_family_heads.iterrows():
        head = head_series.to_dict()
        house_id = current_hh_id
        current_hh_id += 1
        head['SIM_HH_ID'] = house_id
        family_batch.append(head)

        slots_needed = head['HHSIZE'] - 1
        for _ in range(slots_needed):
            if pool_family_mem:
                member = pool_family_mem.pop()
            elif pool_non_family:
                member = pool_non_family.pop()
            else:
                if not df_members_2.empty:
                    member = df_members_2.sample(1).to_dict('records')[0]
                else:
                    member = df_remaining.sample(1).to_dict('records')[0]
                member['PID'] = str(uuid.uuid4())[:8]
            member['SIM_HH_ID'] = house_id
            family_batch.append(member)

    if family_batch:
        final_households.append(pd.DataFrame(family_batch))

    # --- PHASE 3: ROOMMATES (Leftover CF_RP 3s) ---
    leftover_roommates = pd.DataFrame(pool_non_family)

    if not leftover_roommates.empty:
        print(f"   Assembling {len(leftover_roommates)} Roommate/Non-Family Agents...")

        for size in sorted(leftover_roommates['HHSIZE'].unique()):
            if size == 1:
                continue
            mates_of_size = leftover_roommates[leftover_roommates['HHSIZE'] == size]
            mate_list = mates_of_size.to_dict('records')
            roommate_batch = []

            while mate_list:
                head = mate_list.pop()
                house_id = current_hh_id
                current_hh_id += 1
                head['SIM_HH_ID'] = house_id
                roommate_batch.append(head)

                slots_needed = size - 1
                for _ in range(slots_needed):
                    if mate_list:
                        member = mate_list.pop()
                    else:
                        member = mates_of_size.sample(1).to_dict('records')[0]
                        member['PID'] = str(uuid.uuid4())[:8]
                    member['SIM_HH_ID'] = house_id
                    roommate_batch.append(member)

            if roommate_batch:
                final_households.append(pd.DataFrame(roommate_batch))

    # --- Combine All ---
    if final_households:
        df_assembled = pd.concat(final_households, ignore_index=True)
    else:
        df_assembled = pd.DataFrame()

    print(f"--- Assembly Complete. Last ID used: {current_hh_id - 1} ---")

    # Final Validation
    if not df_assembled.empty:
        size_counts = df_assembled.groupby('SIM_HH_ID')['PID'].count()
        target_sizes = df_assembled.groupby('SIM_HH_ID')['HHSIZE'].first()
        mismatches = size_counts != target_sizes
        if mismatches.any():
            print(f"[!] WARNING: {mismatches.sum()} households have mismatched sizes!")
        else:
            print("[OK] VALIDATION: All households have correct member counts.")

    # --- SAVE TO CSV ---
    save_filename = f"{target_year}_LINKED.csv"
    save_path = pathlib.Path(output_dir) / save_filename
    df_assembled.to_csv(save_path, index=False)
    print(f"[OK] Saved linked {target_year} data to: {save_path}")

    return df_assembled


# =============================================================================
# GSS 2015 FILE READING
# =============================================================================

def parse_sps_colspec(sps_filepath: Union[str, Path]) -> Tuple[List[str], List[tuple]]:
    """
    Parse variable names and column positions from SPSS .sps file.

    Args:
        sps_filepath: Path to the .sps file.

    Returns:
        Tuple of (variable_names, column_specs)
    """
    colspec = []
    var_names = []

    var_pattern = re.compile(r'^\s+([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)\s*-\s*(\d+)')

    with open(sps_filepath, 'r', encoding='utf-8', errors='replace') as f:
        in_data_list = False
        for line in f:
            if 'DATA LIST' in line.upper():
                in_data_list = True
                continue
            if in_data_list and line.strip() == '.':
                break
            if in_data_list:
                match = var_pattern.match(line)
                if match:
                    var_name = match.group(1)
                    start = int(match.group(2)) - 1
                    end = int(match.group(3))
                    var_names.append(var_name)
                    colspec.append((start, end))

    return var_names, colspec


def read_gss_2015_main(
    txt_path: Path,
    sps_path: Path,
    cols_to_extract: List[str]
) -> pd.DataFrame:
    """
    Read GSS 2015 Main file (fixed-width text format).

    Args:
        txt_path: Path to GSSMain_2015.txt
        sps_path: Path to GSSMain_2015.sps
        cols_to_extract: List of column names to extract

    Returns:
        DataFrame with extracted columns
    """
    print(f"   Parsing SPS file: {sps_path.name}")
    var_names, colspec = parse_sps_colspec(sps_path)

    # Find positions for target columns
    extract_spec = []
    extract_names = []
    for col in cols_to_extract:
        if col in var_names:
            idx = var_names.index(col)
            extract_spec.append(colspec[idx])
            extract_names.append(col)
        else:
            print(f"   [!] Column {col} not found in SPS")

    print(f"   Reading TXT file: {txt_path.name}")
    df = pd.read_fwf(txt_path, colspecs=extract_spec, names=extract_names)

    return df


def read_merge_save_gss_2015(
    main_txt_path: Path,
    main_sps_path: Path,
    episode_path: Path,
    cols_main: list,
    rename_dict: dict,
    output_csv_path: Path
) -> pd.DataFrame:
    """
    1. Reads GSS 2015 MAIN file (fixed-width text).
    2. Reads EPISODE file (pre-processed CSV).
    3. Merges Demographics onto Episodes.
    4. Renames columns to Census standard.
    5. Saves to CSV.

    Args:
        main_txt_path: Path to GSSMain_2015.txt
        main_sps_path: Path to GSSMain_2015.sps
        episode_path: Path to pre-processed episode CSV
        cols_main: List of columns to extract from main file
        rename_dict: Dictionary for renaming columns
        output_csv_path: Path to save the merged output

    Returns:
        DataFrame with merged GSS data
    """
    print(f"--- Starting GSS 2015 Processing ---")

    # --- STEP 1: Read Main File (Demographics) ---
    print(f"1. Reading Main File...")
    df_main = read_gss_2015_main(main_txt_path, main_sps_path, cols_main)
    print(f"   Loaded Main Data: {len(df_main)} people.")

    # --- STEP 2: Read Episode File ---
    print(f"2. Reading Episode File: {episode_path.name}...")
    if not os.path.exists(episode_path):
        print(f"   Error: Episode file not found.")
        return None

    df_episode = pd.read_csv(episode_path, low_memory=False)
    print(f"   Loaded Episode Data: {len(df_episode)} rows.")

    # --- STEP 3: Merge ---
    print(f"3. Merging Main Demographics onto Episodes...")
    
    # Check merge key
    if 'occID' in df_episode.columns and 'PUMFID' in df_main.columns:
        df_main = df_main.rename(columns={'PUMFID': 'occID'})
    
    df_merged = pd.merge(df_episode, df_main, on='occID', how='left')
    print(f"   Merged Data: {len(df_merged)} rows.")

    # --- STEP 4: Rename Columns ---
    print(f"4. Renaming columns to Census standards...")
    # Adjust rename_dict to skip occID (already renamed)
    rename_adjusted = {k: v for k, v in rename_dict.items() if k != 'PUMFID'}
    df_merged = df_merged.rename(columns=rename_adjusted)

    # --- STEP 5: Save ---
    print(f"5. Saving GSS Merged Data to: {output_csv_path.name}")
    df_merged.to_csv(output_csv_path, index=False)
    print(f"   [OK] Saved {len(df_merged)} rows.")

    return df_merged


# =============================================================================
# HARMONIZATION FUNCTIONS
# =============================================================================

def harmonize_agegrp(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes AGEGRP.
    Census 2016: 1-13 (5-year age groups)
    GSS 2015: 1-7 (10-year age groups)

    Census mapping:
        1,2 -> Skip (0-14, children)
        3,4 -> 1 (15-24)
        5,6 -> 2 (25-34)
        7,8 -> 3 (35-44)
        9,10 -> 4 (45-54)
        11 -> 5 (55-64)
        12 -> 6 (65-74)
        13 -> 7 (75+)
    """
    print("  Harmonizing AGEGRP...")

    # GSS: Filter bad values
    df_gss = df_gss[~df_gss['AGEGRP'].isin(['97', '98', '99', 97, 98, 99])].copy()
    df_gss['AGEGRP'] = pd.to_numeric(df_gss['AGEGRP'], errors='coerce').fillna(96).astype(int)

    # Census: Map to GSS categories
    def map_census_age_to_gss(x):
        try:
            x = int(float(x))
        except:
            return 96
        if x <= 2:
            return 96  # 0-14 -> Skip
        if x in [3, 4]:
            return 1  # 15-24
        if x in [5, 6]:
            return 2  # 25-34
        if x in [7, 8]:
            return 3  # 35-44
        if x in [9, 10]:
            return 4  # 45-54
        if x == 11:
            return 5  # 55-64
        if x == 12:
            return 6  # 65-74
        if x >= 13:
            return 7  # 75+
        return 96

    df_census['AGEGRP'] = df_census['AGEGRP'].apply(map_census_age_to_gss).astype(int)
    df_census = df_census[~df_census['AGEGRP'].isin([96])].copy()

    print(f"    Census AGEGRP unique: {sorted(df_census['AGEGRP'].unique())}")
    print(f"    GSS AGEGRP unique: {sorted(df_gss['AGEGRP'].unique())}")
    return df_census, df_gss


def harmonize_sex(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes SEX.
    Both use: 1=Male, 2=Female (direct match)
    """
    print("  Harmonizing SEX...")

    df_gss['SEX'] = pd.to_numeric(df_gss['SEX'], errors='coerce').astype(int)
    df_census['SEX'] = pd.to_numeric(df_census['SEX'], errors='coerce').astype(int)

    print(f"    Census SEX unique: {sorted(df_census['SEX'].unique())}")
    print(f"    GSS SEX unique: {sorted(df_gss['SEX'].unique())}")
    return df_census, df_gss


def harmonize_marsth(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes MARSTH (Marital Status).
    Census 2016: 1=Married/CL, 2=Never Married, 3=Sep/Div/Widowed
    GSS 2015: 1=Married, 2=Common-law, 3=Widowed, 4=Separated, 5=Divorced, 6=Single

    Map GSS to Census:
        1,2 -> 1 (Married/CL)
        6 -> 2 (Never Married)
        3,4,5 -> 3 (Sep/Div/Widowed)
    """
    print("  Harmonizing MARSTH...")

    df_gss['MARSTH'] = pd.to_numeric(df_gss['MARSTH'], errors='coerce').fillna(99).astype(int)

    def map_gss_marsth(x):
        if x in [1, 2]:
            return 1  # Married/CL
        if x == 6:
            return 2  # Never Married
        if x in [3, 4, 5]:
            return 3  # Sep/Div/Widowed
        return 99

    df_gss['MARSTH'] = df_gss['MARSTH'].apply(map_gss_marsth).astype(int)
    df_gss = df_gss[~df_gss['MARSTH'].isin([99])].copy()

    df_census['MARSTH'] = pd.to_numeric(df_census['MARSTH'], errors='coerce').astype(int)

    print(f"    Census MARSTH unique: {sorted(df_census['MARSTH'].unique())}")
    print(f"    GSS MARSTH unique: {sorted(df_gss['MARSTH'].unique())}")
    return df_census, df_gss


def harmonize_hhsize(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes HHSIZE (Household Size).
    Census: 1-7
    GSS: 1-6

    Map: Census 7 -> 6 (cap at 6)
    """
    print("  Harmonizing HHSIZE...")

    df_gss['HHSIZE'] = pd.to_numeric(df_gss['HHSIZE'], errors='coerce').fillna(99).astype(int)
    df_census['HHSIZE'] = pd.to_numeric(df_census['HHSIZE'], errors='coerce').fillna(99).astype(int)
    df_census.loc[df_census['HHSIZE'] >= 7, 'HHSIZE'] = 6

    print(f"    Census HHSIZE unique: {sorted(df_census['HHSIZE'].unique())}")
    print(f"    GSS HHSIZE unique: {sorted(df_gss['HHSIZE'].unique())}")
    return df_census, df_gss


def harmonize_lftag(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes LFTAG (Labour Force Activity).
    Census 2016: 1-14, 99 (detailed categories)
    GSS 2015: 1-6, 97-99

    Map Census to GSS:
        1 -> 1 (Employed full-time)
        2-6 -> 2 (Employed other)
        7-11 -> 3 (Unemployed/looking)
        12,13 -> 4 (Not in labour force)
        14 -> 5 (Retired/Other)
    """
    print("  Harmonizing LFTAG...")

    # GSS: Filter DK/NS and drop category 6
    df_gss['LFTAG'] = pd.to_numeric(df_gss['LFTAG'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['LFTAG'].isin([6, 97, 98, 99])].copy()

    # Census: Map to GSS categories
    def map_census_lftag(x):
        try:
            x = int(float(x))
        except:
            return 99
        if x == 1:
            return 1
        if x in [2, 3, 4, 5, 6]:
            return 2
        if x in [7, 8, 9, 10, 11]:
            return 3
        if x in [12, 13]:
            return 4
        if x == 14:
            return 5
        return 99

    df_census['LFTAG'] = df_census['LFTAG'].apply(map_census_lftag).astype(int)
    df_census = df_census[~df_census['LFTAG'].isin([99])].copy()

    print(f"    Census LFTAG unique: {sorted(df_census['LFTAG'].unique())}")
    print(f"    GSS LFTAG unique: {sorted(df_gss['LFTAG'].unique())}")
    return df_census, df_gss


def harmonize_cma(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes CMA (Census Metropolitan Area / Urban-Rural).
    Census 2016: 462=Ottawa, 535=Toronto, etc., 999=Other
    GSS 2015: 1=CMA 500k+, 2=CA 10k-100k, 3=Rural

    Map Census to GSS:
        462,535,825,835,933 -> 1 (Major CMA)
        999 -> 2 (Other/CA)

    Map GSS: Drop 3 (Rural) to match Census
    """
    print("  Harmonizing CMA...")

    def map_census_cma(x):
        try:
            x = int(float(x))
        except:
            return 99
        if x in [462, 535, 825, 835, 933]:
            return 1
        if x == 999:
            return 2
        return 99

    df_census['CMA'] = df_census['CMA'].apply(map_census_cma).astype(int)
    df_census = df_census[~df_census['CMA'].isin([99])].copy()

    df_gss['CMA'] = pd.to_numeric(df_gss['CMA'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['CMA'].isin([3, 99])].copy()

    print(f"    Census CMA unique: {sorted(df_census['CMA'].unique())}")
    print(f"    GSS CMA unique: {sorted(df_gss['CMA'].unique())}")
    return df_census, df_gss


def harmonize_pr(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes PR (Province/Region).
    Census 2016: 1-6 (aggregated regions)
    GSS 2015: 10-59 (individual provinces)

    Map Census to GSS province codes:
        1 -> 10 (Atlantic)
        2 -> 24 (Quebec)
        3 -> 35 (Ontario)
        4 -> 46 (Manitoba - Prairie)
        5 -> 48 (Alberta)
        6 -> 59 (BC)

    Map GSS Atlantic (10-13) -> 10, Saskatchewan (47) -> 46
    """
    print("  Harmonizing PR...")

    census_to_gss_pr = {
        1: 10, 2: 24, 3: 35, 4: 46, 5: 48, 6: 59
    }

    df_census['PR'] = pd.to_numeric(df_census['PR'], errors='coerce').fillna(99).astype(int)
    df_census['PR'] = df_census['PR'].map(census_to_gss_pr).fillna(99).astype(int)
    df_census = df_census[~df_census['PR'].isin([99])].copy()

    gss_pr_mapping = {
        10: 10, 11: 10, 12: 10, 13: 10,  # Atlantic -> NL
        24: 24, 35: 35, 46: 46, 47: 46, 48: 48, 59: 59
    }

    df_gss['PR'] = pd.to_numeric(df_gss['PR'], errors='coerce').fillna(99).astype(int)
    df_gss['PR'] = df_gss['PR'].map(gss_pr_mapping).fillna(99).astype(int)
    df_gss = df_gss[~df_gss['PR'].isin([99])].copy()

    print(f"    Census PR unique: {sorted(df_census['PR'].unique())}")
    print(f"    GSS PR unique: {sorted(df_gss['PR'].unique())}")
    return df_census, df_gss


def harmonize_kol(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes KOL (Knowledge of Official Languages).
    Census 2016: 1=English, 2=French, 3=Both, 4=Neither
    GSS 2015: 1=English, 2=French, 3=Both, 4=Other, 7-9=DK/NS

    Map: Drop Census 4, GSS 4,7,8,9
    """
    print("  Harmonizing KOL...")

    df_gss['KOL'] = pd.to_numeric(df_gss['KOL'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['KOL'].isin([4, 7, 8, 9, 99])].copy()

    df_census['KOL'] = pd.to_numeric(df_census['KOL'], errors='coerce').fillna(99).astype(int)
    df_census = df_census[~df_census['KOL'].isin([4, 99])].copy()

    print(f"    Census KOL unique: {sorted(df_census['KOL'].unique())}")
    print(f"    GSS KOL unique: {sorted(df_gss['KOL'].unique())}")
    return df_census, df_gss


def harmonize_totinc(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes TOTINC (Total Income).
    Census 2016: Continuous values (actual dollars)
    GSS 2015: 1-7 categorical income groups

    Map Census continuous to 7 brackets matching GSS 2015:
        1: No income / loss
        2: Under $20,000
        3: $20,000-$39,999
        4: $40,000-$59,999
        5: $60,000-$79,999
        6: $80,000-$99,999
        7: $100,000 or more
    """
    print("  Harmonizing TOTINC...")

    # GSS: Already 1-7
    df_gss['TOTINC'] = pd.to_numeric(df_gss['TOTINC'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['TOTINC'].isin([97, 98, 99])].copy()

    # Census: Map continuous to 7 categories
    def map_census_income(x):
        try:
            x = float(x)
        except:
            return 99
        if x <= 0:
            return 1
        if x < 20000:
            return 2
        if x < 40000:
            return 3
        if x < 60000:
            return 4
        if x < 80000:
            return 5
        if x < 100000:
            return 6
        return 7

    df_census['TOTINC'] = df_census['TOTINC'].apply(map_census_income).astype(int)
    df_census = df_census[~df_census['TOTINC'].isin([99])].copy()

    print(f"    Census TOTINC unique: {sorted(df_census['TOTINC'].unique())}")
    print(f"    GSS TOTINC unique: {sorted(df_gss['TOTINC'].unique())}")
    return df_census, df_gss


# =============================================================================
# MAIN ALIGNMENT FUNCTION
# =============================================================================

TARGET_COLS_16 = ['AGEGRP', 'SEX', 'MARSTH', 'HHSIZE', 'LFTAG', 'CMA', 'PR', 'KOL', 'TOTINC']


def data_alignment(
    census_csv_path: Path,
    gss_csv_path: Path,
    output_dir: Path,
    target_year: str = "2015"
) -> tuple:
    """
    Loads Census 2016 and GSS 2015 data.
    Applies all harmonization functions.
    Saves aligned DataFrames to CSV.
    """
    print("=" * 60)
    print("2015 DATA ALIGNMENT")
    print("=" * 60)

    print("\n--- Step 1: Loading Datasets ---")
    print(f"  Loading Census: {census_csv_path.name}...")
    df_census = pd.read_csv(census_csv_path)
    print(f"    Census loaded: {len(df_census)} rows")

    print(f"  Loading GSS: {gss_csv_path.name}...")
    df_gss = pd.read_csv(gss_csv_path, dtype=str, low_memory=False)
    print(f"    GSS loaded: {len(df_gss)} rows")

    print("\n--- Step 2: Running Harmonization Pipeline ---")
    df_census, df_gss = harmonize_agegrp(df_census, df_gss)
    df_census, df_gss = harmonize_sex(df_census, df_gss)
    df_census, df_gss = harmonize_marsth(df_census, df_gss)
    df_census, df_gss = harmonize_hhsize(df_census, df_gss)
    df_census, df_gss = harmonize_lftag(df_census, df_gss)
    df_census, df_gss = harmonize_cma(df_census, df_gss)
    df_census, df_gss = harmonize_pr(df_census, df_gss)
    df_census, df_gss = harmonize_kol(df_census, df_gss)
    df_census, df_gss = harmonize_totinc(df_census, df_gss)

    print("\n--- Step 3: Alignment Complete ---")
    print(f"  Census Shape: {df_census.shape}")
    print(f"  GSS Shape: {df_gss.shape}")

    # Save aligned data
    print("\n--- Step 4: Saving Aligned DataFrames ---")
    output_dir.mkdir(parents=True, exist_ok=True)

    census_out = output_dir / f"Aligned_Census_{target_year}.csv"
    gss_out = output_dir / f"Aligned_GSS_{target_year}.csv"

    print(f"  Saving Census to: {census_out.name}...")
    df_census.to_csv(census_out, index=False)

    print(f"  Saving GSS to: {gss_out.name}...")
    df_gss.to_csv(gss_out, index=False)

    print("\n" + "=" * 60)
    print("ALIGNMENT COMPLETE")
    print("=" * 60)

    return df_census, df_gss


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def check_value_alignment(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Census",
    df2_name: str = "GSS",
    target_cols: list = None
) -> pd.DataFrame:
    """Compare unique values between Census and GSS for alignment validation."""
    if target_cols is None:
        target_cols = TARGET_COLS_16

    cols1 = [c for c in target_cols if c in df1.columns]
    cols2 = [c for c in target_cols if c in df2.columns]
    common_cols = sorted(list(set(cols1).intersection(set(cols2))))

    print(f"\n{'=' * 60}")
    print(f"   VALUE ALIGNMENT CHECK: {df1_name} vs {df2_name}")
    print(f"{'=' * 60}")
    print(f"Analyzing {len(common_cols)} common columns...\n")

    results = []
    for col in common_cols:
        u1 = sorted(df1[col].dropna().astype(str).unique())
        u2 = sorted(df2[col].dropna().astype(str).unique())
        match = set(u1) == set(u2)
        status = "MATCH" if match else "MISMATCH"
        results.append({
            "Column": col,
            "Status": status,
            f"Unique_{df1_name}": len(u1),
            f"Unique_{df2_name}": len(u2),
        })
        print(f"  {col:10s} {status:10s} Census={len(u1):2d} GSS={len(u2):2d}")

    return pd.DataFrame(results)


def plot_distribution_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Census",
    df2_name: str = "GSS",
    target_cols: list = None,
    output_path: str = None
) -> None:
    """Plot side-by-side bar charts comparing distributions."""
    if target_cols is None:
        target_cols = TARGET_COLS_16

    common_cols = sorted(list(
        set(target_cols).intersection(set(df1.columns)).intersection(set(df2.columns))
    ))

    if not common_cols:
        print("No common columns found to plot.")
        return

    print(f"\nPlotting distributions for {len(common_cols)} columns...")

    num_plots = len(common_cols)
    cols_per_row = 3
    rows = math.ceil(num_plots / cols_per_row)

    fig, axes = plt.subplots(rows, cols_per_row, figsize=(18, 5 * rows))
    axes = axes.flatten()

    for i, col in enumerate(common_cols):
        ax = axes[i]
        d1 = df1[[col]].dropna().copy()
        d1['Source'] = df1_name
        d2 = df2[[col]].dropna().copy()
        d2['Source'] = df2_name
        combined = pd.concat([d1, d2], ignore_index=True)

        sns.histplot(
            data=combined, x=col, hue='Source',
            stat='percent', common_norm=False, multiple='dodge',
            shrink=0.8, discrete=True, ax=ax,
            palette={df1_name: "#1f77b4", df2_name: "#ff7f0e"}
        )
        ax.set_title(f"Distribution: {col}", fontsize=12, fontweight='bold')
        ax.set_ylabel("Percent (%)")
        ax.grid(axis='y', alpha=0.3)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  Plot saved to: {output_path}")
        plt.close()
    else:
        plt.show()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> None:
    """Main entry point for 16CEN15GSS alignment."""
    # --- Configuration (Cross-platform) ---
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR

    # Output directories
    OUTPUT_DIR_GSS = BASE_DIR / "Outputs_GSS"
    OUTPUT_DIR_16CEN15GSS = BASE_DIR / "Outputs_16CEN15GSS" / "alignment"
    OUTPUT_DIR_GSS.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_16CEN15GSS.mkdir(parents=True, exist_ok=True)

    # Input files
    DATA_DIR_GSS_15 = BASE_DIR / "DataSources_GSS" / "Main_files"
    FILE_MAIN_15_TXT = DATA_DIR_GSS_15 / "GSSMain_2015.txt"
    FILE_MAIN_15_SPS = DATA_DIR_GSS_15 / "GSSMain_2015.sps"
    # Episode file is in 2ndJournal project
    FILE_EPISODE_15 = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs_GSS/out15EP_ACT_PRE_coPRE.csv")
    CENSUS_FILE_16 = OUTPUT_DIR_16CEN15GSS / "2016_LINKED.csv"

    print("=" * 60)
    print("  16CEN15GSS ALIGNMENT")
    print("  Census 2016 + GSS 2015 Integration")
    print("=" * 60)

    # --- Check if Census 2016 linked file exists ---
    if not CENSUS_FILE_16.exists():
        print("\n[!] Census 2016 linked file not found, assembling households...")
        cen16_filtered = BASE_DIR / "Outputs_CENSUS" / "cen16_filtered2.csv"
        if cen16_filtered.exists():
            assemble_households(cen16_filtered, 2016, OUTPUT_DIR_16CEN15GSS)
        else:
            print(f"ERROR: Census filtered file not found: {cen16_filtered}")
            return

    # --- Check if GSS 2015 episode file exists ---
    if not FILE_EPISODE_15.exists():
        print(f"\n[!] GSS 2015 episode file not found: {FILE_EPISODE_15}")
        print("    Please run GSS 2015 episode processing first.")
        return

    # --- Step 1: Read & Merge GSS 2015 ---
    gss_merged_path = OUTPUT_DIR_GSS / "GSS_2015_Merged_Main.csv"
    if not gss_merged_path.exists():
        print("\n--- Step 0: Processing GSS 2015 Main + Episodes ---")
        df_gss = read_merge_save_gss_2015(
            main_txt_path=FILE_MAIN_15_TXT,
            main_sps_path=FILE_MAIN_15_SPS,
            episode_path=FILE_EPISODE_15,
            cols_main=COLS_MAIN_15,
            rename_dict=RENAME_MAP_15,
            output_csv_path=gss_merged_path
        )
    else:
        print(f"\n[OK] GSS 2015 Merged file already exists: {gss_merged_path.name}")

    # --- Step 2: Run Alignment ---
    df_census, df_gss = data_alignment(
        census_csv_path=CENSUS_FILE_16,
        gss_csv_path=gss_merged_path,
        output_dir=OUTPUT_DIR_16CEN15GSS,
        target_year="2015"
    )

    # --- Step 3: Validation ---
    print("\n--- Step 5: Running Alignment Validation ---")
    check_value_alignment(df_census, df_gss)

    # --- Step 4: Plot ---
    print("\n--- Step 6: Plotting Distribution Comparison ---")
    plot_path = OUTPUT_DIR_16CEN15GSS / "16CEN15GSS_alignment_validation.png"
    plot_distribution_comparison(df_census, df_gss, output_path=str(plot_path))

    print("\n" + "=" * 60)
    print("  [OK] 16CEN15GSS ALIGNMENT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
