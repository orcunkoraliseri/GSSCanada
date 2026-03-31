import uuid
import pathlib
import os
import re
import pandas as pd
from pathlib import Path
from typing import Union, Tuple, List

# =============================================================================
# GSS 2010 COLUMN DEFINITIONS
# =============================================================================

COLS_MAIN_10 = [
    'RECID',       # Key for merging -> occID
    'PRV',         # Province -> PR
    'HSDSIZEC',    # Household Size -> HHSIZE
    'AGEGR10',     # Age group -> AGEGRP
    'SEX',         # Sex -> SEX
    'MARSTAT',     # Marital Status -> MARSTH
    'LANHSDC',     # Language -> KOL
    'ACT7DAYS',    # Labour Force -> LFTAG
    'LUC_RST',     # Urban/Rural -> CMA
    'INCM',        # Income -> TOTINC
    'DVTDAY',      # Day Type (Weekday/Weekend) -> DDAY
    'WGHT_PER',    # Weight
    'NOCS2006_C10' # NOCS
]

RENAME_MAP_10 = {
    'RECID': 'occID',
    'PRV': 'PR',
    'HSDSIZEC': 'HHSIZE',
    'AGEGR10': 'AGEGRP',
    'SEX': 'SEX',
    'MARSTAT': 'MARSTH',
    'LANHSDC': 'KOL',
    'ACT7DAYS': 'LFTAG',
    'LUC_RST': 'CMA',
    'INCM': 'TOTINC',
    'DVTDAY': 'DDAY',
    'NOCS2006_C10': 'NOCS'
}

# =============================================================================
# HOUSEHOLD ASSEMBLY (Census 2011)
# =============================================================================

def assemble_households(
    csv_file_path: Union[str, pathlib.Path],
    target_year: int,
    output_dir: Union[str, pathlib.Path],
    start_id: int = 100
) -> pd.DataFrame:
    """Reads filtered Census CSV, reconstructs households, saves LINKED CSV."""
    print(f"\n--- Assembling Households for {target_year} ---")
    print(f"   Loading data from: {csv_file_path}")

    # 1. LOAD DATA
    df_population = pd.read_csv(csv_file_path)
    
    # Generate PIDs
    df_population['PID'] = [str(uuid.uuid4())[:8] for _ in range(len(df_population))]

    # Ensure Types
    if 'HHSIZE' not in df_population.columns:
        print("   HHSIZE not found. Deriving from HH_ID counts...")
        df_population['HHSIZE'] = df_population.groupby('HH_ID')['HH_ID'].transform('count')
        df_population.loc[df_population['HHSIZE'] >= 7, 'HHSIZE'] = 6

    df_population['HHSIZE'] = pd.to_numeric(df_population['HHSIZE'], errors='coerce').fillna(1).astype(int)
    df_population['CF_RP'] = df_population['CF_RP'].astype(str).str.replace('.0', '', regex=False)

    final_households = []
    current_hh_id = start_id

    # PHASE 1: SINGLES
    singles_mask = df_population['HHSIZE'] == 1
    df_singles = df_population[singles_mask].copy()

    if not df_singles.empty:
        num_singles = len(df_singles)
        df_singles['SIM_HH_ID'] = range(current_hh_id, current_hh_id + num_singles)
        current_hh_id += num_singles
        final_households.append(df_singles)

    print(f"   Processed {len(df_singles)} Single-Person Households.")

    df_remaining = df_population[~singles_mask].copy()

    # PHASE 2: FAMILIES
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

    # PHASE 3: ROOMMATES
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

    # Combine
    if final_households:
        df_assembled = pd.concat(final_households, ignore_index=True)
    else:
        df_assembled = pd.DataFrame()

    print(f"--- Assembly Complete. Last ID used: {current_hh_id - 1} ---")

    if not df_assembled.empty:
        size_counts = df_assembled.groupby('SIM_HH_ID')['PID'].count()
        target_sizes = df_assembled.groupby('SIM_HH_ID')['HHSIZE'].first()
        mismatches = size_counts != target_sizes
        if mismatches.any():
            print(f"[!] WARNING: {mismatches.sum()} households have mismatched sizes!")
        else:
            print("[OK] VALIDATION: All households have correct member counts.")

    os.makedirs(output_dir, exist_ok=True)
    save_filename = f"{target_year}_LINKED.csv"
    save_path = pathlib.Path(output_dir) / save_filename
    df_assembled.to_csv(save_path, index=False)
    print(f"[OK] Saved linked {target_year} data to: {save_path}")

    return df_assembled


# =============================================================================
# GSS 2010 FILE READING
# =============================================================================

def parse_sps_colspec(sps_filepath: Union[str, Path]) -> Tuple[List[str], List[tuple]]:
    colspec = []
    var_names = []
    var_pattern = re.compile(r'^/?\s*([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)\s*-\s*(\d+)')

    with open(sps_filepath, 'r', encoding='latin1', errors='replace') as f:
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

def read_gss_2010_main(
    txt_path: Path,
    sps_path: Path,
    cols_to_extract: List[str]
) -> pd.DataFrame:
    print(f"   Parsing SPS file: {sps_path.name}")
    var_names, colspec = parse_sps_colspec(sps_path)

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
    df = pd.read_fwf(txt_path, colspecs=extract_spec, names=extract_names, encoding='latin1')
    return df

def read_merge_save_gss_2010(
    main_txt_path: Path,
    main_sps_path: Path,
    episode_path: Path,
    cols_main: list,
    rename_dict: dict,
    output_csv_path: Path
) -> pd.DataFrame:
    print(f"--- Starting GSS 2010 Processing ---")
    df_main = read_gss_2010_main(main_txt_path, main_sps_path, cols_main)
    print(f"   Loaded Main Data: {len(df_main)} people.")

    if not os.path.exists(episode_path):
        print(f"   Error: Episode file not found.")
        return None

    df_episode = pd.read_csv(episode_path, low_memory=False)
    print(f"   Loaded Episode Data: {len(df_episode)} rows.")

    print(f"3. Merging Main Demographics onto Episodes...")
    if 'occID' in df_episode.columns and 'RECID' in df_main.columns:
        df_main = df_main.rename(columns={'RECID': 'occID'})
    
    df_merged = pd.merge(df_episode, df_main, on='occID', how='left')
    print(f"   Merged Data: {len(df_merged)} rows.")

    print(f"4. Renaming columns to Census standards...")
    # Drop DVTDAY before renaming: DDAY is already present from the episode file.
    # Renaming DVTDAY -> DDAY after merge would create a duplicate column (DDAY / DDAY.1).
    if 'DVTDAY' in df_merged.columns and 'DDAY' in df_merged.columns:
        df_merged = df_merged.drop(columns=['DVTDAY'])
    rename_adjusted = {k: v for k, v in rename_dict.items() if k != 'RECID' and k in df_merged.columns}
    df_merged = df_merged.rename(columns=rename_adjusted)

    print(f"5. Saving GSS Merged Data to: {output_csv_path.name}")
    df_merged.to_csv(output_csv_path, index=False)
    print(f"   [OK] Saved {len(df_merged)} rows.")

    return df_merged

# =============================================================================
# HARMONIZATION FUNCTIONS
# =============================================================================

def harmonize_agegrp(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing AGEGRP...")
    df_gss = df_gss[~df_gss['AGEGRP'].isin(['97', '98', '99', 97, 98, 99])].copy()
    df_gss['AGEGRP'] = pd.to_numeric(df_gss['AGEGRP'], errors='coerce').fillna(96).astype(int)

    def map_census_age_to_gss(x):
        try:
            x = int(float(x))
        except:
            return 96
        if x <= 2: return 96
        if x in [3, 4]: return 1
        if x in [5, 6]: return 2
        if x in [7, 8]: return 3
        if x in [9, 10]: return 4
        if x == 11: return 5
        if x == 12: return 6
        if x >= 13: return 7
        return 96

    df_census['AGEGRP'] = df_census['AGEGRP'].apply(map_census_age_to_gss).astype(int)
    df_census = df_census[~df_census['AGEGRP'].isin([96])].copy()
    return df_census, df_gss

def harmonize_sex(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing SEX...")
    df_gss['SEX'] = pd.to_numeric(df_gss['SEX'], errors='coerce').astype(int)
    df_census['SEX'] = pd.to_numeric(df_census['SEX'], errors='coerce').astype(int)
    return df_census, df_gss

def harmonize_marsth(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing MARSTH...")
    df_gss['MARSTH'] = pd.to_numeric(df_gss['MARSTH'], errors='coerce').fillna(99).astype(int)

    def map_gss_marsth(x):
        if x in [1, 2]: return 1
        if x == 6: return 2
        if x in [3, 4, 5]: return 3
        return 99

    # Census 2011 MARSTH codebook labels are:
    #   1 = Never legally married (and not living common law)
    #   2 = Legally married (and not separated)
    #   3 = Living common law
    # Collapse Census and GSS into the shared 1-3 matching space:
    #   1 = Married/Common-law, 2 = Single, 3 = Widowed/Sep/Div
    census_marsth_map = {
        1: 2,  # single
        2: 1,  # married
        3: 1,  # common-law
        4: 3,  # separated
        5: 3,  # divorced
        6: 3,  # widowed
    }
    df_gss['MARSTH'] = df_gss['MARSTH'].apply(map_gss_marsth).astype(int)
    df_gss = df_gss[~df_gss['MARSTH'].isin([99])].copy()
    df_census['MARSTH'] = pd.to_numeric(df_census['MARSTH'], errors='coerce').fillna(99).astype(int)
    df_census['MARSTH'] = df_census['MARSTH'].map(census_marsth_map).fillna(99).astype(int)
    df_census = df_census[~df_census['MARSTH'].isin([99])].copy()
    return df_census, df_gss

def harmonize_hhsize(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing HHSIZE...")
    df_gss['HHSIZE'] = pd.to_numeric(df_gss['HHSIZE'], errors='coerce').fillna(99).astype(int)
    df_census['HHSIZE'] = pd.to_numeric(df_census['HHSIZE'], errors='coerce').fillna(99).astype(int)
    df_census.loc[df_census['HHSIZE'] >= 7, 'HHSIZE'] = 6
    return df_census, df_gss

def harmonize_lftag(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing LFTAG...")
    df_gss['LFTAG'] = pd.to_numeric(df_gss['LFTAG'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['LFTAG'].isin([6, 8, 9, 97, 98, 99])].copy()

    def map_census_lftag(x):
        try: x = int(float(x))
        except: return 99
        if x == 1: return 1
        if x in [2, 3, 4, 5, 6]: return 2
        if x in [7, 8, 9, 10, 11]: return 3
        if x in [12, 13]: return 4
        if x == 14: return 5
        return 99

    df_census['LFTAG'] = df_census['LFTAG'].apply(map_census_lftag).astype(int)
    df_census = df_census[~df_census['LFTAG'].isin([99])].copy()
    return df_census, df_gss

def harmonize_cma(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing CMA...")
    def map_census_cma(x):
        try: x = int(float(x))
        except: return 99
        if x in [505, 535, 462, 825, 835, 933, 408]: return 1 # Major CMAs
        if x in [996, 999]: return 2 # Other CAs/Non-CMA urban
        if x in [997]: return 99 # Rural wait, plan says "Drop Rural (3) from GSS". Census rural (997) dropped too
        return 2

    df_census['CMA'] = df_census['CMA'].apply(map_census_cma).astype(int)
    df_census = df_census[~df_census['CMA'].isin([99])].copy()

    df_gss['CMA'] = pd.to_numeric(df_gss['CMA'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['CMA'].isin([3, 99])].copy()
    return df_census, df_gss

def harmonize_pr(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing PR...")
    # Census 2011 uses 2-digit Statistics Canada province codes directly
    # (unlike Census 2006 which used aggregated 1-6 regional codes)
    cen11_pr_map = {
        10: 10, 11: 10, 12: 10, 13: 10,  # Atlantic provinces -> NL representative
        24: 24,                             # Quebec
        35: 35,                             # Ontario
        46: 46, 47: 46,                    # MB + SK -> MB (Prairies representative)
        48: 48,                             # Alberta
        59: 59,                             # British Columbia
        # 60 (YT), 61 (NT), 62 (NU) not in map -> fillna(99) -> dropped
    }
    df_census['PR'] = pd.to_numeric(df_census['PR'], errors='coerce').fillna(99).astype(int)
    df_census['PR'] = df_census['PR'].map(cen11_pr_map).fillna(99).astype(int)
    df_census = df_census[~df_census['PR'].isin([99])].copy()

    gss_pr_mapping = {10: 10, 11: 10, 12: 10, 13: 10, 24: 24, 35: 35, 46: 46, 47: 46, 48: 48, 59: 59}
    df_gss['PR'] = pd.to_numeric(df_gss['PR'], errors='coerce').fillna(99).astype(int)
    df_gss['PR'] = df_gss['PR'].map(gss_pr_mapping).fillna(99).astype(int)
    df_gss = df_gss[~df_gss['PR'].isin([99])].copy()

    print(f"    Census PR unique: {sorted(df_census['PR'].unique())}")
    print(f"    GSS PR unique: {sorted(df_gss['PR'].unique())}")
    return df_census, df_gss

def harmonize_kol(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing KOL...")
    df_gss['KOL'] = pd.to_numeric(df_gss['KOL'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['KOL'].isin([8, 9, 99])].copy() # LANHSDC map DK/NS drops

    df_census['KOL'] = pd.to_numeric(df_census['KOL'], errors='coerce').fillna(99).astype(int)
    df_census = df_census[~df_census['KOL'].isin([4, 99])].copy()
    return df_census, df_gss

def harmonize_nocs(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing NOCS...")
    df_gss['NOCS'] = pd.to_numeric(df_gss['NOCS'], errors='coerce').fillna(99).astype(int)
    def map_gss_nocs(x):
        if x in [97, 98]: return 99
        return x
    df_gss['NOCS'] = df_gss['NOCS'].apply(map_gss_nocs).astype(int)
    
    df_census['NOCS'] = pd.to_numeric(df_census['NOCS'], errors='coerce').fillna(99).astype(int)
    df_census.loc[df_census['NOCS'].isin([88]), 'NOCS'] = 99
    return df_census, df_gss

def map_income_to_category(x):
    try: x = float(x)
    except: return 99
    if x <= 0: return 1
    if x < 5000: return 2
    if x < 10000: return 3
    if x < 15000: return 4
    if x < 20000: return 5
    if x < 30000: return 6
    if x < 40000: return 7
    if x < 50000: return 8
    if x < 60000: return 9
    if x < 80000: return 10
    if x < 100000: return 11
    if x < 99999999: return 12
    return 99

def harmonize_totinc(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing TOTINC...")
    # Census 2011 TOTINC is continuous dollars and gets binned to 1-12.
    # GSS 2010 INCM/TOTINC is already coded as 1-12 income categories, with
    # 97/98/99 reserved for missing/refusal values.
    df_gss['TOTINC'] = pd.to_numeric(df_gss['TOTINC'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['TOTINC'].isin([97, 98, 99])].copy()
    
    df_census['TOTINC'] = pd.to_numeric(df_census['TOTINC'], errors='coerce')
    df_census['TOTINC'] = df_census['TOTINC'].apply(map_income_to_category).astype(int)
    df_census = df_census[~df_census['TOTINC'].isin([99])].copy()
    return df_census, df_gss

TARGET_COLS_10 = ['AGEGRP', 'CMA', 'HHSIZE', 'KOL', 'LFTAG', 'MARSTH', 'NOCS', 'PR', 'SEX', 'TOTINC']

def data_alignment(
    census_csv_path: Path,
    gss_csv_path: Path,
    output_dir: Path,
    target_year: str = "2010"
) -> tuple:
    print("=" * 60)
    print("2010 DATA ALIGNMENT")
    print("=" * 60)

    print("\n--- Step 1: Loading Datasets ---")
    df_census = pd.read_csv(census_csv_path)
    df_gss = pd.read_csv(gss_csv_path, dtype=str, low_memory=False)

    print("\n--- Step 2: Running Harmonization Pipeline ---")
    df_census, df_gss = harmonize_agegrp(df_census, df_gss)
    df_census, df_gss = harmonize_sex(df_census, df_gss)
    df_census, df_gss = harmonize_marsth(df_census, df_gss)
    df_census, df_gss = harmonize_hhsize(df_census, df_gss)
    df_census, df_gss = harmonize_lftag(df_census, df_gss)
    df_census, df_gss = harmonize_cma(df_census, df_gss)
    df_census, df_gss = harmonize_pr(df_census, df_gss)
    df_census, df_gss = harmonize_kol(df_census, df_gss)
    df_census, df_gss = harmonize_nocs(df_census, df_gss)
    df_census, df_gss = harmonize_totinc(df_census, df_gss)

    output_dir.mkdir(parents=True, exist_ok=True)
    census_out = output_dir / f"Aligned_Census_2010.csv"
    gss_out = output_dir / f"Aligned_GSS_2010.csv"

    df_census.to_csv(census_out, index=False)
    df_gss.to_csv(gss_out, index=False)
    return df_census, df_gss

def check_value_alignment(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Census",
    df2_name: str = "GSS",
    target_cols: list = None
) -> pd.DataFrame:
    if target_cols is None: target_cols = TARGET_COLS_10
    cols1 = [c for c in target_cols if c in df1.columns]
    cols2 = [c for c in target_cols if c in df2.columns]
    common_cols = sorted(list(set(cols1).intersection(set(cols2))))

    results = []
    for col in common_cols:
        u1 = sorted(df1[col].dropna().astype(str).unique())
        u2 = sorted(df2[col].dropna().astype(str).unique())
        match = set(u1) == set(u2)
        status = "MATCH" if match else "MISMATCH"
        results.append({"Column": col, "Status": status})
        print(f"  {col:10s} {status:10s} Census={len(u1):2d} GSS={len(u2):2d}")
    return pd.DataFrame(results)

def main():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR
    
    census_csv = BASE_DIR / "Outputs_CENSUS" / "cen11_filtered.csv"
    gss_main_txt = BASE_DIR / "DataSources_GSS" / "Main_files" / "GSSMain_2010.DAT"
    gss_main_sps = BASE_DIR / "DataSources_GSS" / "Main_files" / "GSSMain_2010_syntax.SPS"
    gss_episode = BASE_DIR / "DataSources_GSS" / "Episode_files" / "GSS_2010_episode" / "out10EP_ACT_PRE_coPRE.csv"
    
    out_dir_gss_merged = BASE_DIR / "DataSources_GSS" / "Main_files" # temp
    merged_gss = out_dir_gss_merged / "GSS_2010_Merged.csv"
    
    output_dir = BASE_DIR / "Outputs_11CEN10GSS" / "alignment"
    
    # Assembly
    census_linked_dir = BASE_DIR / "DataSources_CENSUS" / "census_2011"
    assemble_households(census_csv.resolve(), 2011, census_linked_dir.resolve())
    census_linked = census_linked_dir / "2011_LINKED.csv"
    
    # Merge GSS
    read_merge_save_gss_2010(
        main_txt_path=gss_main_txt.resolve(),
        main_sps_path=gss_main_sps.resolve(),
        episode_path=gss_episode.resolve(),
        cols_main=COLS_MAIN_10,
        rename_dict=RENAME_MAP_10,
        output_csv_path=merged_gss.resolve()
    )
    
    # Align
    df_cen, df_gss = data_alignment(
        census_csv_path=census_linked.resolve(),
        gss_csv_path=merged_gss.resolve(),
        output_dir=output_dir.resolve(),
        target_year="2010"
    )
    
    # Check
    check_value_alignment(df_cen, df_gss)

if __name__ == "__main__":
    main()
