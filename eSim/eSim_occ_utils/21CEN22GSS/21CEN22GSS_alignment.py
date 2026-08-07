"""
21CEN22GSS Alignment Module

Reads GSS 2022 data, merges with episode schedules, and aligns the merged GSS
table with Census 2021 for occupancy modeling.
"""

import os
import pathlib
import re
import uuid
from pathlib import Path
from typing import List, Tuple, Union

import pandas as pd


# =============================================================================
# GSS 2022 COLUMN DEFINITIONS
# =============================================================================

COLS_MAIN_22 = [
    "PUMFID",
    "PRV",
    "HSDSIZEC",
    "AGEGR10",
    "GENDER2",
    "MARSTAT",
    "LANHSDC",
    "ACT7DAYC",
    "LUC_RST",
    "INC_C",
    "DDAY",
    "WGHT_PER",
    "PHSDFLG",
    "CXRFLAG",
    "PARNUM",
]

RENAME_MAP_22 = {
    "PUMFID": "occID",
    "PRV": "PR",
    "HSDSIZEC": "HHSIZE",
    "AGEGR10": "AGEGRP",
    "GENDER2": "SEX",
    "MARSTAT": "MARSTH",
    "LANHSDC": "KOL",
    "ACT7DAYC": "LFTAG",
    "LUC_RST": "CMA",
    # Keep INC_C as-is for V1; TOTINC mapping is intentionally deferred.
}

TARGET_COLS_22 = ["HHSIZE", "AGEGRP", "SEX", "MARSTH", "KOL", "PR", "LFTAG", "CMA"]

SOCIAL_ALIAS_COLUMNS_22 = {
    "TUI_06A": "Alone",
    "TUI_06B": "Spouse",
    "TUI_06C": "Children",
    "TUI_06D": "otherInFAMs",
    "TUI_06E": "parents",
    "TUI_06G": "otherHHs",
    "TUI_06H": "Friends",
    "TUI_06I": "colleagues",
    "TUI_06J": "Others",
    "TUI_07": "techUse",
    "TUI_15": "wellbeing",
}


# =============================================================================
# HOUSEHOLD ASSEMBLY (Census 2021)
# =============================================================================

def assemble_households(
    csv_file_path: Union[str, pathlib.Path],
    target_year: int,
    output_dir: Union[str, pathlib.Path],
    start_id: int = 100,
) -> pd.DataFrame:
    """
    Read the cleaned Census 2021 CSV, reconstruct households, and save LINKED CSV.
    """
    print(f"\n--- Assembling Households for {target_year} ---")
    print(f"   Loading data from: {csv_file_path}")

    df_population = pd.read_csv(csv_file_path)
    df_population["PID"] = [str(uuid.uuid4())[:8] for _ in range(len(df_population))]

    if "HHSIZE" not in df_population.columns:
        print("   HHSIZE not found. Deriving from HH_ID counts...")
        if "HH_ID" not in df_population.columns:
            raise KeyError("HH_ID is required to derive HHSIZE for Census 2021")
        df_population["HHSIZE"] = df_population.groupby("HH_ID")["HH_ID"].transform("count")

    df_population["HHSIZE"] = pd.to_numeric(df_population["HHSIZE"], errors="coerce").fillna(1).astype(int)
    df_population.loc[df_population["HHSIZE"] >= 5, "HHSIZE"] = 5

    if "ROOM" in df_population.columns:
        df_population["ROOM"] = pd.to_numeric(df_population["ROOM"], errors="coerce")
        room_mask = df_population["ROOM"].isna() | (df_population["ROOM"] <= 15)
        removed_room = int((~room_mask).sum())
        if removed_room > 0:
            print(f"   Filtering {removed_room} Census records with ROOM > 15...")
        df_population = df_population[room_mask].copy()

    if "CF_RP" not in df_population.columns:
        raise KeyError("CF_RP is required for household assembly")
    df_population["CF_RP"] = df_population["CF_RP"].astype(str).str.replace(".0", "", regex=False)

    rename_candidates = {}
    if "GENDER" in df_population.columns:
        rename_candidates["GENDER"] = "SEX"
    if "LFACT" in df_population.columns:
        rename_candidates["LFACT"] = "LFTAG"
    if rename_candidates:
        df_population = df_population.rename(columns=rename_candidates)

    final_households = []
    current_hh_id = start_id

    # Phase 1: singles
    singles_mask = df_population["HHSIZE"] == 1
    df_singles = df_population[singles_mask].copy()
    if not df_singles.empty:
        num_singles = len(df_singles)
        df_singles["SIM_HH_ID"] = range(current_hh_id, current_hh_id + num_singles)
        current_hh_id += num_singles
        final_households.append(df_singles)

    print(f"   Processed {len(df_singles)} Single-Person Households.")

    # Phase 2: families
    df_remaining = df_population[~singles_mask].copy()
    df_family_heads = df_remaining[df_remaining["CF_RP"] == "1"].copy()
    df_members_2 = df_remaining[df_remaining["CF_RP"] == "2"].copy()
    df_members_3 = df_remaining[df_remaining["CF_RP"] == "3"].copy()

    pool_family_mem = df_members_2.sample(frac=1.0).to_dict("records")
    pool_non_family = df_members_3.sample(frac=1.0).to_dict("records")

    print(f"   Assembling {len(df_family_heads)} Family Households (Heads)...")

    family_batch = []
    for _, head_series in df_family_heads.iterrows():
        head = head_series.to_dict()
        house_id = current_hh_id
        current_hh_id += 1
        head["SIM_HH_ID"] = house_id
        family_batch.append(head)

        slots_needed = int(head["HHSIZE"]) - 1
        for _ in range(slots_needed):
            if pool_family_mem:
                member = pool_family_mem.pop()
            elif pool_non_family:
                member = pool_non_family.pop()
            else:
                if not df_members_2.empty:
                    member = df_members_2.sample(1).to_dict("records")[0]
                else:
                    member = df_remaining.sample(1).to_dict("records")[0]
                member["PID"] = str(uuid.uuid4())[:8]
            member["SIM_HH_ID"] = house_id
            family_batch.append(member)

    if family_batch:
        final_households.append(pd.DataFrame(family_batch))

    # Phase 3: roommates / leftover non-family agents
    leftover_roommates = pd.DataFrame(pool_non_family)
    if not leftover_roommates.empty:
        print(f"   Assembling {len(leftover_roommates)} Roommate/Non-Family Agents...")
        for size in sorted(leftover_roommates["HHSIZE"].unique()):
            if size == 1:
                continue
            mates_of_size = leftover_roommates[leftover_roommates["HHSIZE"] == size]
            mate_list = mates_of_size.to_dict("records")
            roommate_batch = []

            while mate_list:
                head = mate_list.pop()
                house_id = current_hh_id
                current_hh_id += 1
                head["SIM_HH_ID"] = house_id
                roommate_batch.append(head)

                slots_needed = int(size) - 1
                for _ in range(slots_needed):
                    if mate_list:
                        member = mate_list.pop()
                    else:
                        member = mates_of_size.sample(1).to_dict("records")[0]
                        member["PID"] = str(uuid.uuid4())[:8]
                    member["SIM_HH_ID"] = house_id
                    roommate_batch.append(member)

            if roommate_batch:
                final_households.append(pd.DataFrame(roommate_batch))

    if final_households:
        df_assembled = pd.concat(final_households, ignore_index=True)
    else:
        df_assembled = pd.DataFrame()

    print(f"--- Assembly Complete. Last ID used: {current_hh_id - 1} ---")

    if not df_assembled.empty:
        size_counts = df_assembled.groupby("SIM_HH_ID")["PID"].count()
        target_sizes = df_assembled.groupby("SIM_HH_ID")["HHSIZE"].first()
        mismatches = size_counts != target_sizes
        if mismatches.any():
            print(f"[!] WARNING: {mismatches.sum()} households have mismatched sizes!")
        else:
            print("[OK] VALIDATION: All households have correct member counts.")

    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / f"{target_year}_LINKED.csv"
    df_assembled.to_csv(save_path, index=False)
    print(f"[OK] Saved linked {target_year} data to: {save_path}")

    return df_assembled


# =============================================================================
# GSS 2022 FILE READING
# =============================================================================

def read_gss_2022_main(sas_path: Path, cols_to_extract: List[str]) -> pd.DataFrame:
    """
    Read the GSS 2022 main file from SAS format.
    """
    print(f"   Reading SAS main file: {sas_path.name}")
    df = pd.read_sas(sas_path, format="sas7bdat", encoding="latin1")

    available_cols = [c for c in cols_to_extract if c in df.columns]
    missing_cols = [c for c in cols_to_extract if c not in df.columns]
    if missing_cols:
        print(f"   [!] Missing columns in GSS main file: {missing_cols}")

    return df[available_cols].copy()


def read_merge_save_gss_2022(
    main_sas_path: Path,
    episode_path: Path,
    cols_main: list,
    rename_dict: dict,
    output_csv_path: Path,
) -> pd.DataFrame:
    """
    Merge GSS 2022 main demographics onto the processed episode file.
    """
    print("--- Starting GSS 2022 Processing ---")
    df_main = read_gss_2022_main(main_sas_path, cols_main)
    print(f"   Loaded Main Data: {len(df_main)} people.")

    if not os.path.exists(episode_path):
        print("   Error: Episode file not found.")
        return None

    df_episode = pd.read_csv(episode_path, low_memory=False)
    print(f"   Loaded Episode Data: {len(df_episode)} rows.")

    if "PUMFID" in df_main.columns and "occID" not in df_main.columns:
        df_main = df_main.rename(columns={"PUMFID": "occID"})

    print("3. Merging Main Demographics onto Episodes...")
    df_merged = pd.merge(df_episode, df_main, on="occID", how="left")
    print(f"   Merged Data: {len(df_merged)} rows.")

    print("4. Renaming columns to Census standards...")
    rename_adjusted = {
        k: v
        for k, v in rename_dict.items()
        if k in df_merged.columns and k != "PUMFID"
    }
    df_merged = df_merged.rename(columns=rename_adjusted)

    # Create stable alias columns for the co-presence / context fields so the
    # downstream aggregation step can reuse the legacy social-column names.
    for source_col, alias_col in SOCIAL_ALIAS_COLUMNS_22.items():
        if source_col in df_merged.columns and alias_col not in df_merged.columns:
            df_merged[alias_col] = df_merged[source_col]

    if "TUI_06D" in df_merged.columns or "TUI_06F" in df_merged.columns:
        d_series = pd.to_numeric(df_merged.get("TUI_06D"), errors="coerce")
        f_series = pd.to_numeric(df_merged.get("TUI_06F"), errors="coerce")
        merged_other = pd.Series(9, index=df_merged.index, dtype="Int64")
        merged_other[(d_series == 1) | (f_series == 1)] = 1
        merged_other[
            ((d_series == 2) | d_series.isna() | (d_series == 9))
            & ((f_series == 2) | f_series.isna() | (f_series == 9))
        ] = 2
        df_merged["otherInFAMs"] = merged_other.astype("Int64")

    print(f"5. Saving GSS Merged Data to: {output_csv_path.name}")
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(output_csv_path, index=False)
    print(f"   [OK] Saved {len(df_merged)} rows.")

    return df_merged


# =============================================================================
# HARMONIZATION FUNCTIONS
# =============================================================================

def harmonize_agegrp(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing AGEGRP...")

    df_gss["AGEGRP"] = pd.to_numeric(df_gss["AGEGRP"], errors="coerce").fillna(96).astype(int)
    df_gss = df_gss[~df_gss["AGEGRP"].isin([96, 97, 98, 99])].copy()

    def map_census_age_to_gss(x):
        try:
            x = int(float(x))
        except Exception:
            return 96
        if x <= 2:
            return 96
        if x in [3, 4]:
            return 1
        if x in [5, 6]:
            return 2
        if x in [7, 8]:
            return 3
        if x in [9, 10]:
            return 4
        if x == 11:
            return 5
        if x == 12:
            return 6
        if x >= 13:
            return 7
        return 96

    df_census["AGEGRP"] = df_census["AGEGRP"].apply(map_census_age_to_gss).astype(int)
    df_census = df_census[~df_census["AGEGRP"].isin([96])].copy()

    print(f"    Census AGEGRP unique: {sorted(df_census['AGEGRP'].unique())}")
    print(f"    GSS AGEGRP unique: {sorted(df_gss['AGEGRP'].unique())}")
    return df_census, df_gss


def harmonize_hhsize(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing HHSIZE...")

    if "HHSIZE" not in df_census.columns and "HH_ID" in df_census.columns:
        df_census["HHSIZE"] = df_census.groupby("HH_ID")["HH_ID"].transform("count")

    df_gss["HHSIZE"] = pd.to_numeric(df_gss["HHSIZE"], errors="coerce").fillna(99).astype(int)
    df_census["HHSIZE"] = pd.to_numeric(df_census["HHSIZE"], errors="coerce").fillna(99).astype(int)

    df_gss = df_gss[df_gss["HHSIZE"].isin([1, 2, 3, 4, 5])].copy()
    df_census.loc[df_census["HHSIZE"] >= 5, "HHSIZE"] = 5
    df_census = df_census[df_census["HHSIZE"].isin([1, 2, 3, 4, 5])].copy()

    print(f"    Census HHSIZE unique: {sorted(df_census['HHSIZE'].unique())}")
    print(f"    GSS HHSIZE unique: {sorted(df_gss['HHSIZE'].unique())}")
    return df_census, df_gss


def harmonize_sex(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    """
    Harmonize SEX using the 2021/2022 convention already used in the
    classification alignment code:
    Census keeps 1=Female, 2=Male; GSS is swapped to match.
    """
    print("  Harmonizing SEX...")

    df_census["SEX"] = pd.to_numeric(df_census["SEX"], errors="coerce")
    df_census = df_census[df_census["SEX"].isin([1, 2])].copy()
    df_census["SEX"] = df_census["SEX"].astype(int)

    df_gss["SEX"] = pd.to_numeric(df_gss["SEX"], errors="coerce")
    df_gss = df_gss[df_gss["SEX"].isin([1, 2])].copy()
    df_gss["SEX"] = df_gss["SEX"].map({1: 2, 2: 1}).astype(int)

    print(f"    Census SEX unique: {sorted(df_census['SEX'].unique())}")
    print(f"    GSS SEX unique: {sorted(df_gss['SEX'].unique())}")
    return df_census, df_gss


def harmonize_marsth(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing MARSTH...")

    df_gss["MARSTH"] = pd.to_numeric(df_gss["MARSTH"], errors="coerce").fillna(99).astype(int)

    def map_gss_marsth(x):
        if x == 3:
            return 1
        if x in [1, 2]:
            return 2
        if x in [4, 5, 6]:
            return 3
        return 99

    df_gss["MARSTH"] = df_gss["MARSTH"].apply(map_gss_marsth).astype(int)
    df_gss = df_gss[df_gss["MARSTH"] != 99].copy()

    df_census["MARSTH"] = pd.to_numeric(df_census["MARSTH"], errors="coerce").fillna(99).astype(int)

    census_marsth_map = {
        1: 1,  # never married
        2: 2,  # married
        3: 1,  # common law -> grouped with never married in the existing 2021 preprocessing
        4: 3,  # separated/divorced/widowed
    }
    df_census["MARSTH"] = df_census["MARSTH"].map(census_marsth_map).fillna(99).astype(int)
    df_census = df_census[df_census["MARSTH"] != 99].copy()

    print(f"    Census MARSTH unique: {sorted(df_census['MARSTH'].unique())}")
    print(f"    GSS MARSTH unique: {sorted(df_gss['MARSTH'].unique())}")
    return df_census, df_gss


def harmonize_kol(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing KOL...")

    df_gss["KOL"] = pd.to_numeric(df_gss["KOL"], errors="coerce").fillna(99).astype(int)
    df_gss = df_gss[df_gss["KOL"].isin([1, 2, 3])].copy()

    df_census["KOL"] = pd.to_numeric(df_census["KOL"], errors="coerce").fillna(99).astype(int)
    df_census = df_census[df_census["KOL"].isin([1, 2, 3])].copy()

    print(f"    Census KOL unique: {sorted(df_census['KOL'].unique())}")
    print(f"    GSS KOL unique: {sorted(df_gss['KOL'].unique())}")
    return df_census, df_gss


def harmonize_pr(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing PR...")

    census_to_gss_pr = {
        10: 10, 11: 10, 12: 10, 13: 10,  # Atlantic
        24: 24,                          # Quebec
        35: 35,                          # Ontario
        46: 46, 47: 46,                  # Prairies -> MB representative
        48: 48,                          # Alberta
        59: 59,                          # BC
    }
    df_census["PR"] = pd.to_numeric(df_census["PR"], errors="coerce").fillna(99).astype(int)
    df_census["PR"] = df_census["PR"].map(census_to_gss_pr).fillna(99).astype(int)
    df_census = df_census[df_census["PR"] != 99].copy()

    gss_pr_mapping = {10: 10, 11: 10, 12: 10, 13: 10, 24: 24, 35: 35, 46: 46, 47: 46, 48: 48, 59: 59}
    df_gss["PR"] = pd.to_numeric(df_gss["PR"], errors="coerce").fillna(99).astype(int)
    df_gss["PR"] = df_gss["PR"].map(gss_pr_mapping).fillna(99).astype(int)
    df_gss = df_gss[df_gss["PR"] != 99].copy()

    print(f"    Census PR unique: {sorted(df_census['PR'].unique())}")
    print(f"    GSS PR unique: {sorted(df_gss['PR'].unique())}")
    return df_census, df_gss


def harmonize_lftag(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing LFTAG...")

    df_gss["LFTAG"] = pd.to_numeric(df_gss["LFTAG"], errors="coerce").fillna(99).astype(int)
    df_gss = df_gss[df_gss["LFTAG"].isin([1, 2, 3, 4, 5])].copy()

    def map_census_lftag(x):
        try:
            x = int(float(x))
        except Exception:
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

    df_census["LFTAG"] = df_census["LFTAG"].apply(map_census_lftag).astype(int)
    df_census = df_census[df_census["LFTAG"] != 99].copy()

    print(f"    Census LFTAG unique: {sorted(df_census['LFTAG'].unique())}")
    print(f"    GSS LFTAG unique: {sorted(df_gss['LFTAG'].unique())}")
    return df_census, df_gss


def harmonize_cma(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing CMA...")

    def map_census_cma(x):
        try:
            x = int(float(x))
        except Exception:
            return 99
        if x in [462, 535, 825, 835, 933]:
            return 1
        if x == 999:
            return 2
        return 99

    df_census["CMA"] = df_census["CMA"].apply(map_census_cma).astype(int)
    df_census = df_census[df_census["CMA"] != 99].copy()

    df_gss["CMA"] = pd.to_numeric(df_gss["CMA"], errors="coerce").fillna(99).astype(int)
    df_gss = df_gss[df_gss["CMA"].isin([1, 2])].copy()

    print(f"    Census CMA unique: {sorted(df_census['CMA'].unique())}")
    print(f"    GSS CMA unique: {sorted(df_gss['CMA'].unique())}")
    return df_census, df_gss


# =============================================================================
# VALUE COMPARISON
# =============================================================================

def check_value_alignment(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Census",
    df2_name: str = "GSS",
    target_cols: list = None,
) -> pd.DataFrame:
    """
    Compare unique values across aligned columns and print a compact report.
    """
    if target_cols is None:
        target_cols = TARGET_COLS_22

    cols1 = [c for c in target_cols if c in df1.columns]
    cols2 = [c for c in target_cols if c in df2.columns]
    common_cols = sorted(list(set(cols1).intersection(set(cols2))))

    print(f"\n{'=' * 80}")
    print(f"   DATA VALUE ALIGNMENT CHECK: {df1_name} vs {df2_name}")
    print(f"   (Restricted to {len(target_cols)} specific demographic columns)")
    print(f"{'=' * 80}")

    missing_targets = set(target_cols) - set(common_cols)
    if missing_targets:
        print("⚠️  Warning: The following target columns were NOT found in both datasets:")
        print(f"    {sorted(list(missing_targets))}")

    results = []
    for col in common_cols:
        u1 = sorted(df1[col].dropna().astype(str).unique())
        u2 = sorted(df2[col].dropna().astype(str).unique())
        set1 = set(u1)
        set2 = set(u2)
        match = set1 == set2
        status = "✅ MATCH" if match else "❌ MISMATCH"

        results.append(
            {
                "Column": col,
                "Status": status,
                f"Unique_{df1_name}": len(u1),
                f"Unique_{df2_name}": len(u2),
                f"Val_{df1_name}": u1,
                f"Val_{df2_name}": u2,
                f"Missing_in_{df2_name}": sorted(list(set1 - set2)),
                f"Missing_in_{df1_name}": sorted(list(set2 - set1)),
            }
        )

    if not results:
        print("❌ No common columns found from the target list.")
        return pd.DataFrame()

    df_res = pd.DataFrame(results)
    summary_cols = ["Column", "Status", f"Unique_{df1_name}", f"Unique_{df2_name}"]
    print(df_res[summary_cols].to_string(index=False))

    print(f"\n{'=' * 80}")
    print(f"   DETAILED VALUE REPORT")
    print(f"{'=' * 80}")
    for _, row in df_res.iterrows():
        print(f"\nColumn: [{row['Column']}]  {row['Status']}")
        if row[f"Unique_{df1_name}"] > 20 or row[f"Unique_{df2_name}"] > 20:
            try:
                min1, max1 = min(df1[row["Column"]]), max(df1[row["Column"]])
                min2, max2 = min(df2[row["Column"]]), max(df2[row["Column"]])
                print(f"   Range {df1_name}: {min1} to {max1}")
                print(f"   Range {df2_name}: {min2} to {max2}")
            except Exception:
                print("   (Could not determine numeric range, likely string data)")
        else:
            print(f"   {df1_name:<10} Values: {row[f'Val_{df1_name}']}")
            print(f"   {df2_name:<10} Values: {row[f'Val_{df2_name}']}")

    return df_res


# =============================================================================
# MAIN ALIGNMENT PIPELINE
# =============================================================================

def data_alignment(
    census_csv_path: Path,
    gss_csv_path: Path,
    output_dir: Path,
    target_year: str = "2022",
) -> tuple:
    """
    Load Census and GSS data, harmonize the shared variables, and save aligned CSVs.
    """
    print("=" * 60)
    print("2022 DATA ALIGNMENT")
    print("=" * 60)

    print("\n--- Step 1: Loading Datasets ---")
    print(f"  Loading Census: {census_csv_path.name}...")
    df_census = pd.read_csv(census_csv_path, low_memory=False)
    print(f"    Census loaded: {len(df_census)} rows")

    print(f"  Loading GSS: {gss_csv_path.name}...")
    df_gss = pd.read_csv(gss_csv_path, dtype=str, low_memory=False)
    print(f"    GSS loaded: {len(df_gss)} rows")

    print("\n--- Step 2: Running Harmonization Pipeline ---")
    df_census, df_gss = harmonize_agegrp(df_census, df_gss)
    df_census, df_gss = harmonize_hhsize(df_census, df_gss)
    df_census, df_gss = harmonize_sex(df_census, df_gss)
    df_census, df_gss = harmonize_marsth(df_census, df_gss)
    df_census, df_gss = harmonize_kol(df_census, df_gss)
    df_census, df_gss = harmonize_pr(df_census, df_gss)
    df_census, df_gss = harmonize_lftag(df_census, df_gss)
    df_census, df_gss = harmonize_cma(df_census, df_gss)

    print("\n--- Step 3: Alignment Complete ---")
    print(f"  Census Shape: {df_census.shape}")
    print(f"  GSS Shape:    {df_gss.shape}")

    output_dir.mkdir(parents=True, exist_ok=True)
    census_out = output_dir / f"Aligned_Census_{target_year}.csv"
    gss_out = output_dir / f"Aligned_GSS_{target_year}.csv"

    print("\n--- Step 4: Saving Aligned DataFrames ---")
    print(f"  Saving Census to: {census_out.name}...")
    df_census.to_csv(census_out, index=False)
    print(f"  Saving GSS to:    {gss_out.name}...")
    df_gss.to_csv(gss_out, index=False)

    report_df = check_value_alignment(df_census, df_gss, target_cols=TARGET_COLS_22)
    report_csv = output_dir / "21CEN22GSS_alignment_summary.csv"
    report_txt = output_dir / "21CEN22GSS_alignment_summary.txt"
    report_df.to_csv(report_csv, index=False)
    report_txt.write_text(report_df[["Column", "Status", "Unique_Census", "Unique_GSS"]].to_string(index=False), encoding="utf-8")
    print(f"  Saved alignment summary to: {report_csv.name}")
    print(f"  Saved alignment text report to: {report_txt.name}")

    return df_census, df_gss


def main() -> None:
    """
    Run the Census 2021 / GSS 2022 alignment workflow.
    """
    import sys

    # Ensure stdout supports Unicode emoji (✅, ❌, ⚠️) on Windows cp1252 consoles.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR

    census_csv = BASE_DIR / "Outputs_CENSUS" / "cen21_filtered.csv"
    gss_main_sas = BASE_DIR / "DataSources_GSS" / "Main_files" / "GSSMain_2022.sas7bdat"
    gss_episode = BASE_DIR / "DataSources_GSS" / "Episode_files" / "GSS_2022_episode" / "out22EP_ACT_PRE_coPRE.csv"

    output_dir = BASE_DIR / "Outputs_21CEN22GSS" / "alignment"
    linked_dir = output_dir
    merged_gss = output_dir / "GSS_2022_Merged.csv"

    census_linked = assemble_households(census_csv.resolve(), 2021, linked_dir.resolve())
    census_linked_csv = linked_dir / "2021_LINKED.csv"
    if census_linked.empty:
        print("[!] Warning: Census linked output is empty.")

    read_merge_save_gss_2022(
        main_sas_path=gss_main_sas.resolve(),
        episode_path=gss_episode.resolve(),
        cols_main=COLS_MAIN_22,
        rename_dict=RENAME_MAP_22,
        output_csv_path=merged_gss.resolve(),
    )

    df_census, df_gss = data_alignment(
        census_csv_path=census_linked_csv.resolve(),
        gss_csv_path=merged_gss.resolve(),
        output_dir=output_dir.resolve(),
        target_year="2022",
    )


if __name__ == "__main__":
    main()
