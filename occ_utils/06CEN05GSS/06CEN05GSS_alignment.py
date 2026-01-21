"""
06CEN05GSS Alignment Module

Reads GSS 2005 data, merges with demographics, and aligns with Census 2006
for occupancy modeling. Maps Census values to GSS value schemes for consistent
comparison.
"""

import pandas as pd
import pathlib
import os
import math
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# =============================================================================
# HARMONIZATION FUNCTIONS
# =============================================================================

def harmonize_agegrp(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes AGEGRP.
    Census: 3-13 (5-year age groups starting at 15)
    GSS: 1-7 (different 10-year groupings)
    
    Census mapping:
        3,4 -> 1 (15-24)
        5,6 -> 2 (25-34)
        7,8 -> 3 (35-44)
        9,10 -> 4 (45-54)
        11 -> 5 (55-64)
        12 -> 6 (65-74)
        13 -> 7 (75+)
    """
    print("  Harmonizing AGEGRP...")
    
    # GSS: Filter bad values, keep numeric
    df_gss = df_gss[~df_gss['AGEGRP'].isin(['97', '98', '99', 97, 98, 99])].copy()
    df_gss['AGEGRP'] = pd.to_numeric(df_gss['AGEGRP'], errors='coerce').fillna(96).astype(int)
    
    # Census: Map to GSS categories
    def map_census_age_to_gss(x):
        try:
            x = int(float(x))
        except:
            return 96
        if x <= 2: return 96  # 0-14 -> Skip (children)
        if x in [3, 4]: return 1  # 15-24
        if x in [5, 6]: return 2  # 25-34
        if x in [7, 8]: return 3  # 35-44
        if x in [9, 10]: return 4  # 45-54
        if x == 11: return 5  # 55-64
        if x == 12: return 6  # 65-74
        if x >= 13: return 7  # 75+
        return 96
    
    df_census['AGEGRP'] = df_census['AGEGRP'].apply(map_census_age_to_gss).astype(int)
    df_census = df_census[~df_census['AGEGRP'].isin([96])].copy()
    
    print(f"    Census AGEGRP unique: {sorted(df_census['AGEGRP'].unique())}")
    print(f"    GSS AGEGRP unique: {sorted(df_gss['AGEGRP'].unique())}")
    return df_census, df_gss


def harmonize_attsch(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes ATTSCH (School Attendance).
    Census: 1=Attending, 2=Not attending
    GSS: 1=Full-time, 2=Part-time, 7=Not attending, 8=DK, 9=NS
    
    Map GSS to Census scheme (simpler):
        GSS 1,2 -> 1 (Attending)
        GSS 7 -> 2 (Not attending)
        GSS 8,9 -> Drop
    """
    print("  Harmonizing ATTSCH...")
    
    # GSS: Map to Census categories
    df_gss['ATTSCH'] = pd.to_numeric(df_gss['ATTSCH'], errors='coerce')
    
    def map_gss_attsch(x):
        try:
            x = int(float(x))
        except:
            return 99
        if x in [1, 2]: return 1  # Attending
        if x == 7: return 2  # Not attending
        return 99  # DK/NS
    
    df_gss['ATTSCH'] = df_gss['ATTSCH'].apply(map_gss_attsch).astype(int)
    df_gss = df_gss[~df_gss['ATTSCH'].isin([99])].copy()
    
    # Census: Already [1,2], just ensure int
    df_census['ATTSCH'] = pd.to_numeric(df_census['ATTSCH'], errors='coerce').astype(int)
    
    print(f"    Census ATTSCH unique: {sorted(df_census['ATTSCH'].unique())}")
    print(f"    GSS ATTSCH unique: {sorted(df_gss['ATTSCH'].unique())}")
    return df_census, df_gss


def harmonize_cma(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes CMA (Census Metropolitan Area).
    Census: 462=Ottawa, 535=Toronto, 825=Calgary, 835=Edmonton, 933=Vancouver, 999=Other
    GSS: 1=CMA 500k+, 2=CA 10k-100k, 3=Rural
    
    Map Census to GSS urban/rural categories:
        462,535,825,835,933 -> 1 (Major CMA)
        999 -> 2 (CA/Other)
    
    Map GSS to match Census (drop Rural):
        GSS 3 (Rural) -> drop (Census doesn't have rural category)
    """
    print("  Harmonizing CMA...")
    
    # Census: Map CMA codes to GSS urban categories
    def map_census_cma(x):
        try:
            x = int(float(x))
        except:
            return 99
        if x in [462, 535, 825, 835, 933]:  # Major CMAs
            return 1
        if x == 999:  # Other/Not CMA
            return 2
        return 99
    
    df_census['CMA'] = df_census['CMA'].apply(map_census_cma).astype(int)
    df_census = df_census[~df_census['CMA'].isin([99])].copy()
    
    # GSS: Drop Rural (3) to match Census [1, 2]
    df_gss['CMA'] = pd.to_numeric(df_gss['CMA'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['CMA'].isin([3, 99])].copy()  # Drop Rural and invalid
    
    print(f"    Census CMA unique: {sorted(df_census['CMA'].unique())}")
    print(f"    GSS CMA unique: {sorted(df_gss['CMA'].unique())}")
    return df_census, df_gss


def harmonize_hhsize(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes HHSIZE (Household Size).
    Census: 1-7
    GSS: 1-6
    
    Map: 7+ -> 6 (cap at 6)
    """
    print("  Harmonizing HHSIZE...")
    
    # GSS: Already 1-6
    df_gss['HHSIZE'] = pd.to_numeric(df_gss['HHSIZE'], errors='coerce').fillna(99).astype(int)
    
    # Census: Cap 7+ to 6
    df_census['HHSIZE'] = pd.to_numeric(df_census['HHSIZE'], errors='coerce').fillna(99).astype(int)
    df_census.loc[df_census['HHSIZE'] >= 7, 'HHSIZE'] = 6
    
    print(f"    Census HHSIZE unique: {sorted(df_census['HHSIZE'].unique())}")
    print(f"    GSS HHSIZE unique: {sorted(df_gss['HHSIZE'].unique())}")
    return df_census, df_gss


def harmonize_kol(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes KOL (Knowledge of Official Languages).
    Census: 1=English only, 2=French only, 3=Both, 4=Neither
    GSS: 1=English, 2=French, 3=Both, 8=DK, 9=NS
    
    Map:
        Census 4 (Neither) -> 99 (drop)
        GSS 8,9 -> drop
    """
    print("  Harmonizing KOL...")
    
    # GSS: Filter DK/NS
    df_gss['KOL'] = pd.to_numeric(df_gss['KOL'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['KOL'].isin([8, 9, 99])].copy()
    
    # Census: Filter Neither (4)
    df_census['KOL'] = pd.to_numeric(df_census['KOL'], errors='coerce').fillna(99).astype(int)
    df_census = df_census[~df_census['KOL'].isin([4, 99])].copy()
    
    print(f"    Census KOL unique: {sorted(df_census['KOL'].unique())}")
    print(f"    GSS KOL unique: {sorted(df_gss['KOL'].unique())}")
    return df_census, df_gss


def harmonize_lftag(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes LFTAG (Labour Force Activity).
    Census: 1-14 (detailed categories)
    GSS: 1-6,8,9
    
    Map Census to GSS:
        1 -> 1 (Employed full-time)
        2-6 -> 2 (Employed part-time/self-employed)
        7-11 -> 3 (Unemployed/looking)
        12,13 -> 4 (Not in labour force)
        14 -> 5 (Retired/Other)
    
    Map GSS to match Census (after Census mapping):
        GSS 6 -> drop (Census doesn't have this category)
    """
    print("  Harmonizing LFTAG...")
    
    # GSS: Filter DK/NS and drop category 6
    df_gss['LFTAG'] = pd.to_numeric(df_gss['LFTAG'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['LFTAG'].isin([6, 8, 9, 99])].copy()  # Drop 6 and DK/NS
    
    # Census: Map to GSS categories
    def map_census_lftag(x):
        try:
            x = int(float(x))
        except:
            return 99
        if x == 1: return 1  # Employed full-time
        if x in [2, 3, 4, 5, 6]: return 2  # Employed other
        if x in [7, 8, 9, 10, 11]: return 3  # Unemployed
        if x in [12, 13]: return 4  # Not in labour force
        if x == 14: return 5  # Retired/Other
        return 99
    
    df_census['LFTAG'] = df_census['LFTAG'].apply(map_census_lftag).astype(int)
    df_census = df_census[~df_census['LFTAG'].isin([99])].copy()
    
    print(f"    Census LFTAG unique: {sorted(df_census['LFTAG'].unique())}")
    print(f"    GSS LFTAG unique: {sorted(df_gss['LFTAG'].unique())}")
    return df_census, df_gss


def harmonize_marsth(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes MARSTH (Marital Status).
    Census: 1=Married, 2=Common-law, 3=Not married
    GSS: 1=Married, 2=Common-law, 3=Widowed, 4=Separated, 5=Divorced, 6=Single, 8=DK, 9=NS
    
    Map GSS to Census scheme:
        1 -> 1 (Married)
        2 -> 2 (Common-law)
        3,4,5,6 -> 3 (Not married)
        8,9 -> Drop
    """
    print("  Harmonizing MARSTH...")
    
    # GSS: Map to Census categories
    df_gss['MARSTH'] = pd.to_numeric(df_gss['MARSTH'], errors='coerce').fillna(99).astype(int)
    
    def map_gss_marsth(x):
        if x == 1: return 1  # Married
        if x == 2: return 2  # Common-law
        if x in [3, 4, 5, 6]: return 3  # Not married
        return 99
    
    df_gss['MARSTH'] = df_gss['MARSTH'].apply(map_gss_marsth).astype(int)
    df_gss = df_gss[~df_gss['MARSTH'].isin([99])].copy()
    
    # Census: Already [1,2,3]
    df_census['MARSTH'] = pd.to_numeric(df_census['MARSTH'], errors='coerce').astype(int)
    
    print(f"    Census MARSTH unique: {sorted(df_census['MARSTH'].unique())}")
    print(f"    GSS MARSTH unique: {sorted(df_gss['MARSTH'].unique())}")
    return df_census, df_gss


def harmonize_nocs(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes NOCS (Occupation Classification).
    Census: 1-10, 99
    GSS: 1-10, 97, 98, 99
    
    Map:
        GSS 97,98 -> 99 (Not applicable/DK)
    """
    print("  Harmonizing NOCS...")
    
    # GSS: Map 97,98 to 99
    df_gss['NOCS'] = pd.to_numeric(df_gss['NOCS'], errors='coerce').fillna(99).astype(int)
    df_gss.loc[df_gss['NOCS'].isin([97, 98]), 'NOCS'] = 99
    
    # Census: Already compatible
    df_census['NOCS'] = pd.to_numeric(df_census['NOCS'], errors='coerce').astype(int)
    
    print(f"    Census NOCS unique: {sorted(df_census['NOCS'].unique())}")
    print(f"    GSS NOCS unique: {sorted(df_gss['NOCS'].unique())}")
    return df_census, df_gss


def harmonize_pr(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes PR (Province/Region).
    Census: 1-6 (aggregated regions)
    GSS: 10,11,12,13 (Atlantic), 24 (Quebec), 35 (Ontario), 46,47,48 (Prairies), 59 (BC)
    
    Map Census to GSS region codes:
        1 -> 10 (Atlantic - use NL as representative)
        2 -> 24 (Quebec)
        3 -> 35 (Ontario)
        4 -> 46 (Prairies - use Manitoba)
        5 -> 48 (Alberta)
        6 -> 59 (BC)
    
    Map GSS to match Census:
        11,12,13 -> 10 (Atlantic region -> NL representative)
        47 -> 46 (Saskatchewan -> Manitoba as Prairie representative)
    """
    print("  Harmonizing PR...")
    
    # Census: Map region codes to GSS province codes
    census_to_gss_pr = {
        1: 10,  # Atlantic -> NL
        2: 24,  # Quebec
        3: 35,  # Ontario
        4: 46,  # Prairie -> MB
        5: 48,  # Alberta
        6: 59   # BC
    }
    
    df_census['PR'] = pd.to_numeric(df_census['PR'], errors='coerce').fillna(99).astype(int)
    df_census['PR'] = df_census['PR'].map(census_to_gss_pr).fillna(99).astype(int)
    df_census = df_census[~df_census['PR'].isin([99])].copy()
    
    # GSS: Map provinces to regional representatives to match Census
    gss_pr_mapping = {
        10: 10,  # NL -> Atlantic
        11: 10,  # PEI -> Atlantic (map to NL)
        12: 10,  # NS -> Atlantic (map to NL)
        13: 10,  # NB -> Atlantic (map to NL)
        24: 24,  # Quebec
        35: 35,  # Ontario
        46: 46,  # Manitoba
        47: 46,  # Saskatchewan -> Manitoba (Prairie representative)
        48: 48,  # Alberta
        59: 59   # BC
    }
    
    df_gss['PR'] = pd.to_numeric(df_gss['PR'], errors='coerce').fillna(99).astype(int)
    df_gss['PR'] = df_gss['PR'].map(gss_pr_mapping).fillna(99).astype(int)
    df_gss = df_gss[~df_gss['PR'].isin([99])].copy()
    
    print(f"    Census PR unique: {sorted(df_census['PR'].unique())}")
    print(f"    GSS PR unique: {sorted(df_gss['PR'].unique())}")
    return df_census, df_gss


def harmonize_sex(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes SEX.
    Both datasets use: 1=Male, 2=Female
    Already aligned - just ensure numeric type.
    """
    print("  Harmonizing SEX...")
    
    df_gss['SEX'] = pd.to_numeric(df_gss['SEX'], errors='coerce').astype(int)
    df_census['SEX'] = pd.to_numeric(df_census['SEX'], errors='coerce').astype(int)
    
    print(f"    Census SEX unique: {sorted(df_census['SEX'].unique())}")
    print(f"    GSS SEX unique: {sorted(df_gss['SEX'].unique())}")
    return df_census, df_gss


def harmonize_totinc(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonizes TOTINC (Total Income).
    Census: Continuous values (actual dollars)
    GSS: 1-12 categorical, 98=DK, 99=NS
    
    Map Census continuous to GSS categories (2005 brackets):
        1: No income or loss
        2: Under $5,000
        3: $5,000-$9,999
        4: $10,000-$14,999
        5: $15,000-$19,999
        6: $20,000-$29,999
        7: $30,000-$39,999
        8: $40,000-$49,999
        9: $50,000-$59,999
        10: $60,000-$79,999
        11: $80,000-$99,999
        12: $100,000 or more
    """
    print("  Harmonizing TOTINC...")
    
    # GSS: Filter DK/NS
    df_gss['TOTINC'] = pd.to_numeric(df_gss['TOTINC'], errors='coerce').fillna(99).astype(int)
    df_gss = df_gss[~df_gss['TOTINC'].isin([98, 99])].copy()
    
    # Census: Map continuous to categories
    def map_census_income(x):
        try:
            x = float(x)
        except:
            return 99
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
        return 12
    
    df_census['TOTINC'] = df_census['TOTINC'].apply(map_census_income).astype(int)
    df_census = df_census[~df_census['TOTINC'].isin([99])].copy()
    
    print(f"    Census TOTINC unique: {sorted(df_census['TOTINC'].unique())}")
    print(f"    GSS TOTINC unique: {sorted(df_gss['TOTINC'].unique())}")
    return df_census, df_gss


# =============================================================================
# MAIN ALIGNMENT FUNCTION
# =============================================================================

def data_alignment(
    census_csv_path: Path,
    gss_csv_path: Path,
    output_dir: Path,
    target_year: str = "2005"
) -> tuple:
    """
    Loads Census 2006 and GSS 2005 data.
    Applies all harmonization functions to align columns and categories.
    Saves the resulting aligned DataFrames to CSV.
    
    Args:
        census_csv_path: Path to Census CSV file.
        gss_csv_path: Path to GSS CSV file.
        output_dir: Directory to save aligned outputs.
        target_year: Year label for output files.
        
    Returns:
        Tuple of (aligned_census_df, aligned_gss_df)
    """
    print("=" * 60)
    print("2005 DATA ALIGNMENT")
    print("=" * 60)
    
    print("\n--- Step 1: Loading Datasets ---")
    
    # Read Census
    print(f"  Loading Census: {census_csv_path.name}...")
    df_census = pd.read_csv(census_csv_path)
    print(f"    Census loaded: {len(df_census)} rows, {len(df_census.columns)} columns")
    
    # Read GSS (use dtype=str for safe handling)
    print(f"  Loading GSS: {gss_csv_path.name}...")
    df_gss = pd.read_csv(gss_csv_path, dtype=str, low_memory=False)
    print(f"    GSS loaded: {len(df_gss)} rows, {len(df_gss.columns)} columns")
    
    print("\n--- Step 2: Running Harmonization Pipeline ---")
    
    # Apply harmonization functions
    df_census, df_gss = harmonize_agegrp(df_census, df_gss)
    df_census, df_gss = harmonize_attsch(df_census, df_gss)
    df_census, df_gss = harmonize_cma(df_census, df_gss)
    df_census, df_gss = harmonize_hhsize(df_census, df_gss)
    df_census, df_gss = harmonize_kol(df_census, df_gss)
    df_census, df_gss = harmonize_lftag(df_census, df_gss)
    df_census, df_gss = harmonize_marsth(df_census, df_gss)
    df_census, df_gss = harmonize_nocs(df_census, df_gss)
    df_census, df_gss = harmonize_pr(df_census, df_gss)
    df_census, df_gss = harmonize_sex(df_census, df_gss)
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
# CHECK & BALANCE FUNCTIONS
# =============================================================================

# Target columns for alignment validation
TARGET_COLS = ['AGEGRP', 'ATTSCH', 'CMA', 'HHSIZE', 'KOL', 'LFTAG', 'MARSTH', 'NOCS', 'PR', 'SEX', 'TOTINC']


def check_value_alignment(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Census",
    df2_name: str = "GSS",
    target_cols: list = None
) -> pd.DataFrame:
    """
    Compares the unique values of SPECIFIC columns that exist in both DataFrames.
    Prints a summary table and a detailed report including ALL unique values.
    
    Args:
        df1, df2: DataFrames to compare.
        df1_name, df2_name: Labels for the datasets.
        target_cols: List of column names to check.
        
    Returns:
        DataFrame with comparison results.
    """
    if target_cols is None:
        target_cols = TARGET_COLS
    
    # Filter to only valid target columns
    cols1 = [c for c in target_cols if c in df1.columns]
    df1_sub = df1[cols1].copy()
    
    cols2 = [c for c in target_cols if c in df2.columns]
    df2_sub = df2[cols2].copy()
    
    print(f"\n{'=' * 80}")
    print(f"   DATA VALUE ALIGNMENT CHECK: {df1_name} vs {df2_name}")
    print(f"   (Restricted to {len(target_cols)} specific demographic columns)")
    print(f"{'=' * 80}")
    
    # Find common columns within the filtered subsets
    common_cols = sorted(list(set(df1_sub.columns).intersection(set(df2_sub.columns))))
    
    # Warn if targets are missing
    missing_targets = set(target_cols) - set(common_cols)
    if missing_targets:
        print(f"\u26a0\ufe0f  Warning: The following target columns were NOT found in both datasets:")
        print(f"    {sorted(list(missing_targets))}")
    
    print(f"Analyzing {len(common_cols)} common columns...\n")
    
    results = []
    
    for col in common_cols:
        # Get unique values as sorted strings for robust comparison
        u1 = sorted(df1_sub[col].dropna().astype(str).unique())
        u2 = sorted(df2_sub[col].dropna().astype(str).unique())
        
        set1 = set(u1)
        set2 = set(u2)
        
        match = set1 == set2
        
        # Calculate differences
        only_in_1 = sorted(list(set1 - set2))
        only_in_2 = sorted(list(set2 - set1))
        
        status = "MATCH" if match else "MISMATCH"
        
        results.append({
            "Column": col,
            "Status": status,
            f"Unique_{df1_name}": len(u1),
            f"Unique_{df2_name}": len(u2),
            f"Val_{df1_name}": u1,
            f"Val_{df2_name}": u2,
            f"Missing_in_{df2_name}": only_in_1,
            f"Missing_in_{df1_name}": only_in_2
        })
    
    if not results:
        print("No common columns found from the target list.")
        return None
    
    # Convert to DataFrame for clean printing
    df_res = pd.DataFrame(results)
    
    # Print Summary Table
    summary_cols = ["Column", "Status", f"Unique_{df1_name}", f"Unique_{df2_name}"]
    print(df_res[summary_cols].to_string(index=False))
    
    # Print Detailed Report
    print(f"\n\n{'=' * 80}")
    print(f"   DETAILED VALUE REPORT")
    print(f"{'=' * 80}")
    
    for _, row in df_res.iterrows():
        col = row['Column']
        status = row['Status']
        status_icon = "OK" if status == "MATCH" else "!!"
        print(f"\nColumn: [{col}]  {status_icon} {status}")
        
        # Check if continuous variable (too many values)
        if row[f"Unique_{df1_name}"] > 20 or row[f"Unique_{df2_name}"] > 20:
            print("   (Continuous/High-Cardinality variable detected)")
            try:
                min1, max1 = min(df1_sub[col]), max(df1_sub[col])
                min2, max2 = min(df2_sub[col]), max(df2_sub[col])
                print(f"   Range {df1_name}: {min1} to {max1}")
                print(f"   Range {df2_name}: {min2} to {max2}")
            except:
                print(f"   (Could not determine numeric range)")
        else:
            print(f"   {df1_name:<10} Values: {row[f'Val_{df1_name}']}")
            print(f"   {df2_name:<10} Values: {row[f'Val_{df2_name}']}")
            
            if status == "MISMATCH":
                if row[f"Missing_in_{df2_name}"]:
                    print(f"   >> In {df1_name} ONLY: {row[f'Missing_in_{df2_name}']}")
                if row[f"Missing_in_{df1_name}"]:
                    print(f"   >> In {df2_name} ONLY: {row[f'Missing_in_{df1_name}']}")
    
    return df_res


def plot_distribution_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Census",
    df2_name: str = "GSS",
    target_cols: list = None,
    output_path: str = None
) -> None:
    """
    Plots side-by-side bar charts (normalized to percentage) for common columns.
    Useful for visually verifying if the distribution of GSS matches the Census.
    
    Args:
        df1, df2: DataFrames to compare.
        df1_name, df2_name: Labels for the legend.
        target_cols: List of column names to plot.
        output_path: Path to save the plot. If None, shows the plot instead.
    """
    if target_cols is None:
        target_cols = TARGET_COLS
    
    # Check if data exists
    if df1 is None or df2 is None:
        print("Error: One of the DataFrames is None. Cannot plot.")
        return
    
    # Identify common columns from the target list
    common_cols = sorted(list(
        set(target_cols).intersection(set(df1.columns)).intersection(set(df2.columns))
    ))
    
    if not common_cols:
        print("No common columns found to plot.")
        return
    
    print(f"\nPlotting distributions for {len(common_cols)} columns...")
    
    # Setup plot grid
    num_plots = len(common_cols)
    cols_per_row = 3
    rows = math.ceil(num_plots / cols_per_row)
    
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(18, 5 * rows))
    axes = axes.flatten()
    
    # Loop through columns and plot
    for i, col in enumerate(common_cols):
        ax = axes[i]
        
        # Prepare data for Seaborn
        d1 = df1[[col]].dropna().copy()
        d1['Source'] = df1_name
        
        d2 = df2[[col]].dropna().copy()
        d2['Source'] = df2_name
        
        combined = pd.concat([d1, d2], ignore_index=True)
        
        # Determine if discrete or continuous
        n_unique = combined[col].nunique()
        is_discrete = n_unique < 25
        
        # Plot
        sns.histplot(
            data=combined,
            x=col,
            hue='Source',
            stat='percent',
            common_norm=False,
            multiple='dodge',
            shrink=0.8,
            discrete=is_discrete,
            ax=ax,
            palette={df1_name: "#1f77b4", df2_name: "#ff7f0e"}
        )
        
        ax.set_title(f"Distribution: {col}", fontsize=12, fontweight='bold')
        ax.set_ylabel("Percent (%)")
        ax.grid(axis='y', alpha=0.3)
    
    # Hide empty subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout()
    
    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  Plot saved to: {output_path}")
        plt.close()
    else:
        plt.show()


# =============================================================================
# GSS READ & MERGE FUNCTION
# =============================================================================

def read_merge_save_gss(
    main_path: Path,
    episode_path: Path,
    cols_main: list,
    rename_dict: dict,
    output_csv_path: Path,
    chunk_size: int = 100000
) -> pd.DataFrame:
    """
    1. Reads MAIN file fully (Demographics - SAS format).
    2. Reads EPISODE file in chunks (Pre-processed CSV format).
    3. Merges Demographics onto Episodes.
    4. Saves to CSV.
    5. Prints unique values for verification.
    
    Args:
        main_path: Path to the main SAS file with demographics.
        episode_path: Path to the pre-processed episode CSV.
        cols_main: List of columns to extract from main file.
        rename_dict: Dictionary for renaming columns.
        output_csv_path: Path to save the merged output.
        chunk_size: Number of rows per chunk for episode processing.
        
    Returns:
        DataFrame with merged GSS data.
    """
    print(f"--- Starting GSS Processing ---")

    # --- STEP 1: Read Main File (Demographics) ---
    print(f"1. Reading Main File: {main_path.name}...")
    if not os.path.exists(main_path):
        print(f"Error: Main file not found.")
        return None

    try:
        # Reading SAS file for Demographics
        df_main = pd.read_sas(main_path, encoding='latin-1')

        # Keep only the relevant demographic columns
        valid_main_cols = [c for c in cols_main if c in df_main.columns]
        df_main = df_main[valid_main_cols]
        print(f"   Loaded Main Data: {len(df_main)} people.")

    except Exception as e:
        print(f"Error reading Main file: {e}")
        return None

    # --- STEP 2: Read Episode File (Schedules) & Merge ---
    print(f"2. Reading Episode File in chunks: {episode_path.name}...")
    if not os.path.exists(episode_path):
        print(f"Error: Episode file not found.")
        return None

    merged_chunks = []

    try:
        # Read CSV in chunks
        reader = pd.read_csv(
            episode_path,
            chunksize=chunk_size,
            encoding='utf-8',
            low_memory=False
        )

        for i, chunk in enumerate(reader):
            # Handle 'occID' in pre-processed CSV vs 'RECID' in Main SAS
            if 'occID' in chunk.columns:
                chunk = chunk.rename(columns={'occID': 'RECID'})
            elif 'RECID' not in chunk.columns:
                print("Error: Merge key ('occID' or 'RECID') missing in Episode chunk.")
                return None

            # Merge Main Data onto Episode Chunk
            chunk_merged = pd.merge(chunk, df_main, on='RECID', how='left')
            merged_chunks.append(chunk_merged)
            print(f"   Processed & Merged chunk {i + 1}...")

    except Exception as e:
        print(f"Error reading Episode file: {e}")
        return None

    # --- STEP 3: Concatenate & Rename ---
    print("3. Concatenating all chunks...")
    full_df = pd.concat(merged_chunks, ignore_index=True)

    print("4. Renaming columns...")
    full_df = full_df.rename(columns=rename_dict)

    # --- STEP 4: Save ---
    print(f"5. Saving merged data to {output_csv_path}...")
    full_df.to_csv(output_csv_path, index=False)

    # --- STEP 5: Print Unique Values ---
    print("\n6. Unique Values Check:")
    print("-" * 40)
    for col in full_df.columns:
        try:
            unique_vals = full_df[col].unique()
            count = len(unique_vals)
            if count <= 20:
                print(f"[{col}] ({count}): {unique_vals}")
            else:
                print(f"[{col}] ({count}): {unique_vals[:5]} ... (truncated)")
        except Exception:
            print(f"[{col}] (Check skipped - likely unhashable)")

    print("-" * 40)
    print(f"Success! Saved {len(full_df)} rows (Episodes).")
    return full_df


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    """Entry point for 2005 GSS-Census alignment."""
    # --- 1. Define Paths ---
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy")

    # Output directories
    OUTPUT_DIR_GSS = BASE_DIR / "Outputs_GSS"
    OUTPUT_DIR_ALIGNED = BASE_DIR / "Outputs_06CEN05GSS" / "alignment"
    OUTPUT_DIR_GSS.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_ALIGNED.mkdir(parents=True, exist_ok=True)

    # GSS output file
    GSS_FILE_05 = OUTPUT_DIR_GSS / "GSS_2005_Merged_Episodes.csv"

    # Input files for 2005
    DATA_DIR_GSS_05 = BASE_DIR / "DataSources_GSS/Main_files"
    FILE_MAIN_05 = DATA_DIR_GSS_05 / "GSSMain_2005.sas7bdat"
    FILE_EPISODE_05 = OUTPUT_DIR_GSS / "out05EP_ACT_PRE_coPRE.csv"
    CENSUS_FILE_06 = BASE_DIR / "Outputs_CENSUS/2006_LINKED.csv"

    # --- 2. Column Configuration ---
    # A) MAIN FILE COLUMNS (Demographics - The "Bridge")
    COLS_MAIN_05 = [
        'RECID',  # Key for merging
        'PRV',  # Geography
        'REGION',  # Geography
        'DVTDAY',
        'HSDSIZEC',  # Household Size
        'AGEGR10',  # Age
        'sex',  # Sex
        'marstat',  # Marital Status
        'LANHSDC',  # Language (KOL)
        'EDUSTAT',  # School Attendance (ATTSCH)
        'EDU5',  # Degree (HDGREE)
        'SOC91C10',  # Occupation (NOCS)
        'NAICS2002_C16',  # Industry (NAICS)
        'ACT7DAYS',  # Labor Force (LFTAG Proxy)
        'INCM',  # Total Income (TOTINC)
        'LUC_RST',  # Urban/Rural (CMA Proxy)
    ]

    # B) RENAME MAP (Census Standards + Episode Names)
    RENAME_MAP_05 = {
        # Demographics (Census Standard)
        'PRV': 'PR',
        'DVTDAY': 'DDAY',
        'HSDSIZEC': 'HHSIZE',
        'AGEGR10': 'AGEGRP',
        'sex': 'SEX',
        'marstat': 'MARSTH',
        'LANHSDC': 'KOL',
        'EDUSTAT': 'ATTSCH',
        'EDU5': 'HDGREE',
        'SOC91C10': 'NOCS',
        'NAICS2002_C16': 'NAICS',
        'ACT7DAYS': 'LFTAG',
        'INCM': 'TOTINC',
        'LUC_RST': 'CMA',
        'RECID': 'occID',
    }

    # --- 3. Read & Merge GSS ---
    print("\n" + "=" * 60)
    print("STEP 0: GSS DATA PREPARATION")
    print("=" * 60)
    read_merge_save_gss(
        main_path=FILE_MAIN_05,
        episode_path=FILE_EPISODE_05,
        cols_main=COLS_MAIN_05,
        rename_dict=RENAME_MAP_05,
        output_csv_path=GSS_FILE_05
    )

    # --- 4. Run Alignment ---
    df_census, df_gss = data_alignment(
        census_csv_path=CENSUS_FILE_06,
        gss_csv_path=GSS_FILE_05,
        output_dir=OUTPUT_DIR_ALIGNED,
        target_year="2005"
    )

    # --- 5. Run Check & Balance ---
    print("\n--- Step 5: Running Alignment Validation ---")
    check_value_alignment(df_census, df_gss, "Census", "GSS", TARGET_COLS)

    # --- 6. Plot Distribution Comparison ---
    print("\n--- Step 6: Plotting Distribution Comparison ---")
    plot_output = OUTPUT_DIR_ALIGNED / "06CEN05GSS_alignment_validation.png"
    plot_distribution_comparison(df_census, df_gss, "Census", "GSS", TARGET_COLS, str(plot_output))


if __name__ == "__main__":
    main()
