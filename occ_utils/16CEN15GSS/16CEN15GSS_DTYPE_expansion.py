"""
16CEN15GSS DTYPE Expansion Module

Refines coarse DTYPE values (1-3) from Census 2016 into detailed DTYPE (1-8)
using machine learning models trained on historic Census data (2006, 2011).

DTYPE Mapping:
    Coarse 1 -> Detailed 1 (Single-detached, no change)
    Coarse 2 -> Detailed 5 or 6 (Apartments: High-rise vs Low-rise)
    Coarse 3 -> Detailed 2, 3, 4, 7, 8 (Semi, Row, Duplex, Other, Mobile)

Pipeline:
1. Load matched Census 2016 data with coarse DTYPE
2. Load historic Census data (2006, 2011) with detailed DTYPE
3. Train Random Forest classifiers for apartment and other dwelling refinement
4. Apply refinement with quota calibration to maintain realistic distributions
5. Validate against historic distributions
"""

import pandas as pd
import numpy as np
import pathlib
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from sklearn.ensemble import RandomForestClassifier


# =============================================================================
# MERGE KEYS FUNCTION
# =============================================================================

def merge_keys_into_forecast(
    df_forecast: pd.DataFrame,
    df_keys: pd.DataFrame
) -> pd.DataFrame:
    """
    Merges authoritative Census columns (CFSIZE, TOTINC) from the Keys file
    into the Forecast file using 'AgentID'.

    Args:
        df_forecast: DataFrame with expanded schedules.
        df_keys: DataFrame with matched Census keys.

    Returns:
        DataFrame with merged columns.
    """
    print("\n🔗 Merging Keys (CFSIZE, TOTINC) into Forecast...")

    # Validation
    if 'AgentID' not in df_forecast.columns:
        print("❌ Error: Forecast file missing 'AgentID'. Cannot merge keys.")
        return df_forecast

    # Select columns to retrieve - include DTYPE and residential features
    cols_to_retrieve = [
        'DTYPE', 'ROOM', 'BEDRM', 'CONDO', 'REPAIR',  # For DTYPE expansion
        'CFSIZE', 'TOTINC', 'CF_RP'  # Demographics
    ]
    available_cols = [c for c in cols_to_retrieve if c in df_keys.columns]

    if not available_cols:
        print("⚠️ Warning: Keys file missing CFSIZE/TOTINC columns.")
        return df_forecast

    print(f"   Retrieved columns: {available_cols}")

    # Prepare Lookup DataFrame
    df_lookup = df_keys[available_cols].copy()
    df_lookup['AgentID'] = df_lookup.index

    # Merge
    df_merged = df_forecast.merge(
        df_lookup, on='AgentID', how='left', suffixes=('_old', '')
    )

    # Cleanup: Drop duplicate columns
    for col in available_cols:
        old_col = f"{col}_old"
        if old_col in df_merged.columns:
            df_merged[col] = df_merged[col].fillna(df_merged[old_col])
            df_merged.drop(columns=[old_col], inplace=True)

    print(f"   ✅ Merge complete. Forecast now has accurate {available_cols}")
    return df_merged


# =============================================================================
# DTYPE REFINER CLASS
# =============================================================================

class DTypeRefiner:
    """
    Refines coarse DTYPE (1-3) to detailed DTYPE (1-8) using ML classifiers
    trained on historic Census data.

    Models:
        Apt: Splits coarse 2 -> 5 (High-rise) or 6 (Low-rise)
        Other: Splits coarse 3 -> 2, 3, 4, 7, 8
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the DTypeRefiner.

        Args:
            output_dir: Directory to save model outputs.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, RandomForestClassifier] = {}

        self.base_features = [
            'BEDRM', 'ROOM', 'PR', 'HHSIZE', 'CONDO', 'REPAIR', 'TOTINC', 'CFSIZE'
        ]
        self.train_features = self.base_features + [
            'ROOM_PER_PERSON', 'BEDRM_RATIO', 'INCOME_PER_PERSON'
        ]

    def _ensure_consistent_scaling(
        self,
        df: pd.DataFrame,
        is_training: bool = False
    ) -> pd.DataFrame:
        """Detect and fix log-scaled income values."""
        if 'TOTINC' not in df.columns:
            return df

        mean_inc = df['TOTINC'].mean()
        max_inc = df['TOTINC'].max()

        status = "Training" if is_training else "Forecast"
        if mean_inc < 50 and max_inc < 50:
            print(f"   ⚠️ [{status}] DETECTED LOG/SCALED INCOME (Mean={mean_inc:.2f}).")
            print(f"      🔄 Converting Log -> Dollars (exp(x) - 1)...")
            df['TOTINC'] = np.expm1(df['TOTINC'])

        return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for model training."""
        df = df.copy()
        
        # Ensure all required columns exist with defaults
        required_cols = {
            'HHSIZE': 1, 'ROOM': 4, 'BEDRM': 2, 'TOTINC': 50000,
            'CFSIZE': 1, 'CONDO': 0, 'REPAIR': 1, 'PR': 35
        }
        for col, default in required_cols.items():
            if col not in df.columns:
                print(f"   ⚠️ Missing column '{col}', filling with default: {default}")
                df[col] = default
        
        # Convert to numeric
        cols_to_numeric = ['HHSIZE', 'ROOM', 'BEDRM', 'TOTINC', 'CFSIZE']
        for c in cols_to_numeric:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Ratios (avoid division by zero)
        df['HHSIZE'] = df['HHSIZE'].replace(0, 1)
        df['ROOM'] = df['ROOM'].replace(0, 1)

        df['ROOM_PER_PERSON'] = df['ROOM'] / df['HHSIZE']
        df['BEDRM_RATIO'] = df['BEDRM'] / df['ROOM']

        if 'TOTINC' in df.columns:
            df['INCOME_PER_PERSON'] = df['TOTINC'] / df['HHSIZE']
        else:
            df['INCOME_PER_PERSON'] = 0

        return df.fillna(0)

    def train_models(self, df_historic: pd.DataFrame) -> None:
        """
        Train DTYPE refinement models on historic Census data.

        Args:
            df_historic: Historic Census DataFrame with detailed DTYPE (1-8).
        """
        print(f"\n🧠 Training DTYPE Refinement Models...")
        df_historic = self._ensure_consistent_scaling(df_historic, is_training=True)
        df_historic = self._add_derived_features(df_historic)

        # --- MODEL A: APARTMENTS (Coarse 2 -> 5, 6) ---
        subset_apt = df_historic[df_historic['DTYPE'].isin([5, 6])]
        if len(subset_apt) > 100:
            clf_apt = RandomForestClassifier(
                n_estimators=200, max_depth=20, min_samples_leaf=4,
                random_state=42, class_weight='balanced', n_jobs=-1
            )
            clf_apt.fit(subset_apt[self.train_features], subset_apt['DTYPE'])
            self.models['Apt'] = clf_apt
            print(f"   ✅ Trained Apartment Splitter (n={len(subset_apt):,})")

        # --- MODEL B: OTHER DWELLINGS (Coarse 3 -> 2, 3, 4, 7, 8) ---
        subset_other = df_historic[df_historic['DTYPE'].isin([2, 3, 4, 7, 8])]
        if len(subset_other) > 100:
            custom_weights = {2: 2.0, 3: 2.0, 4: 1.0, 7: 1.0, 8: 1.0}
            clf_other = RandomForestClassifier(
                n_estimators=200, max_depth=20, min_samples_leaf=2,
                random_state=42, class_weight=custom_weights, n_jobs=-1
            )
            clf_other.fit(subset_other[self.train_features], subset_other['DTYPE'])
            self.models['Other'] = clf_other
            print(f"   ✅ Trained 'Other' Decoder (n={len(subset_other):,})")

    def apply_refinement(self, df_forecast: pd.DataFrame) -> pd.DataFrame:
        """
        Apply DTYPE refinement with quota calibration.

        Args:
            df_forecast: Census DataFrame with coarse DTYPE (1-3).

        Returns:
            DataFrame with refined DTYPE (1-8).
        """
        print(f"\n✨ Applying Refinement with Quota Calibration...")

        df_forecast = self._ensure_consistent_scaling(df_forecast, is_training=False)
        df_enhanced = self._add_derived_features(df_forecast)

        # Ensure features exist
        missing = [c for c in self.train_features if c not in df_enhanced.columns]
        if missing:
            print(f"   ⚠️ Warning: Still missing features: {missing}. Filling 0.")
            for c in missing:
                df_enhanced[c] = 0

        X = df_enhanced[self.train_features].fillna(0)
        refined_dtype = df_forecast['DTYPE'].copy()

        # --- HELPER: Quota Sampling ---
        def apply_quota_sampling(
            model: RandomForestClassifier,
            X_subset: pd.DataFrame,
            mask_subset: pd.Series,
            target_ratios: Dict[int, float]
        ) -> pd.Series:
            if mask_subset.sum() == 0:
                return pd.Series(dtype=int)

            probs = model.predict_proba(X_subset)
            classes = model.classes_
            df_probs = pd.DataFrame(probs, columns=classes, index=X_subset.index)

            final_assignments = pd.Series(index=X_subset.index, dtype=int)
            total_n = len(X_subset)
            available_indices = set(X_subset.index)

            # Iterate through classes
            for cls, ratio in target_ratios.items():
                if cls not in df_probs.columns:
                    continue
                target_count = int(total_n * ratio)

                if target_count > 0 and available_indices:
                    # Pick top N most likely candidates
                    candidates = df_probs.loc[
                        list(available_indices), cls
                    ].sort_values(ascending=False)
                    selected = candidates.head(target_count).index
                    final_assignments.loc[selected] = cls
                    available_indices -= set(selected)

            # Fill remainder
            if available_indices:
                remaining = list(available_indices)
                fallback = df_probs.loc[remaining].idxmax(axis=1)
                final_assignments.loc[remaining] = fallback

            return final_assignments

        # --- APPLY MODEL A: APARTMENTS ---
        if 'Apt' in self.models:
            mask = (df_forecast['DTYPE'] == 2)
            if mask.sum() > 0:
                # Historic Split: 34% High Rise, 66% Low Rise
                ratios_apt = {5: 0.34, 6: 0.66}
                assignments = apply_quota_sampling(
                    self.models['Apt'], X[mask], mask, ratios_apt
                )
                refined_dtype.loc[mask] = assignments
                print(f"   Refined {mask.sum():,} Apartments (Calibrated)")

        # --- APPLY MODEL B: OTHER DWELLINGS ---
        if 'Other' in self.models:
            mask = (df_forecast['DTYPE'] == 3)
            if mask.sum() > 0:
                # Historic Split: Row(33%), Semi(29%), Duplex(29%), Mobile(7%), Other(2%)
                ratios_other = {3: 0.33, 2: 0.29, 4: 0.29, 8: 0.07, 7: 0.02}
                assignments = apply_quota_sampling(
                    self.models['Other'], X[mask], mask, ratios_other
                )
                refined_dtype.loc[mask] = assignments
                print(f"   Refined {mask.sum():,} 'Other' dwellings (Calibrated)")

        df_forecast['DTYPE'] = refined_dtype
        df_forecast['DTYPE_Detailed'] = refined_dtype
        return df_forecast


# =============================================================================
# VALIDATION FUNCTION
# =============================================================================

def validate_refinement_model(
    historic_input: List[Path],
    forecast_refined_path: Path,
    output_dir: Path
) -> None:
    """
    Validate DTYPE refinement by comparing distributions.

    Args:
        historic_input: List of paths to historic Census files.
        forecast_refined_path: Path to refined forecast file.
        output_dir: Directory to save validation report.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "Validation_Report_DTYPE.txt"
    report_buffer = []

    def log(message: str = "") -> None:
        print(message)
        report_buffer.append(str(message))

    log(f"\n{'=' * 60}")
    log(f"🕵️‍♂️ VALIDATING DTYPE REFINEMENT")

    # Load historic data
    if isinstance(historic_input, list):
        dfs = []
        for p in historic_input:
            if Path(p).exists():
                dfs.append(pd.read_csv(p, low_memory=False))
        if dfs:
            df_hist = pd.concat(dfs, ignore_index=True)
        else:
            log("❌ No historic data files found.")
            return
    else:
        df_hist = pd.read_csv(historic_input, low_memory=False)

    df_future = pd.read_csv(forecast_refined_path, low_memory=False)

    # Check stats
    if 'TOTINC' in df_hist.columns and 'TOTINC' in df_future.columns:
        log(f"   Stats Check: Historic TOTINC Mean: {df_hist['TOTINC'].mean():.2f}")
        log(f"   Stats Check: Forecast TOTINC Mean: {df_future['TOTINC'].mean():.2f}")

    dtype_labels = {
        1: "Single-detached",
        2: "Semi-detached",
        3: "Row house",
        4: "Duplex",
        5: "Apt 5+ Storeys",
        6: "Apt <5 Storeys",
        7: "Other single-attached",
        8: "Movable"
    }

    dist_hist = df_hist['DTYPE'].value_counts(normalize=True).sort_index() * 100
    dist_fut = df_future['DTYPE'].value_counts(normalize=True).sort_index() * 100

    df_comp = pd.DataFrame({
        'Historic': dist_hist,
        'Forecast': dist_fut
    }).fillna(0)
    df_comp.index = [dtype_labels.get(i, f"Code {i}") for i in df_comp.index]

    log("\n   --- Distribution Comparison (%) ---")
    log(df_comp.round(2).to_string())

    # Save Report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_buffer))

    log(f"\n   ✅ Validation Report saved to: {report_path.name}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main(sample_pct: float = 100.0) -> None:
    """
    Entry point for DTYPE expansion.

    Args:
        sample_pct: Percentage identifier (only used for file naming).
    """
    # --- CONFIGURATION ---
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy")

    # Historic data (Teacher) - Census 2006 and 2011 with detailed DTYPE 1-8
    HISTORIC_DATA_PATHS = [
        BASE_DIR / "Outputs_CENSUS" / "cen06_filtered2.csv",
        BASE_DIR / "Outputs_CENSUS" / "cen11_filtered2.csv"
    ]

    # ProfileMatching outputs (Student) - has coarse DTYPE 1-3
    suffix = f"_sample{int(sample_pct)}pct" if sample_pct < 100 else ""
    INPUT_DIR = BASE_DIR / "Outputs_16CEN15GSS" / "ProfileMatching"
    INPUT_FORECAST_PATH = INPUT_DIR / f"16CEN15GSS_Full_Schedules{suffix}.csv"
    INPUT_KEYS_PATH = INPUT_DIR / f"16CEN15GSS_Matched_Keys{suffix}.csv"

    # Output directory
    OUTPUT_DIR = BASE_DIR / "Outputs_16CEN15GSS" / "DTYPE_expansion"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REFINED_PATH = OUTPUT_DIR / f"16CEN15GSS_Full_Schedules_Refined{suffix}.csv"
    VALIDATION_DIR = OUTPUT_DIR / "Validation"

    print("=" * 60)
    print("  16CEN15GSS DTYPE EXPANSION")
    print("  Refining DTYPE 1-3 -> 1-8")
    print("=" * 60)

    # --- Step 1: Load Forecast ---
    print(f"\n1. Loading ProfileMatching output...")
    if not INPUT_FORECAST_PATH.exists():
        print(f"❌ Error: Forecast file not found at {INPUT_FORECAST_PATH}")
        print("   Please run ProfileMatcher first.")
        return

    df_forecast = pd.read_csv(INPUT_FORECAST_PATH, low_memory=False)
    print(f"   Loaded: {len(df_forecast):,} rows")

    # --- Step 2: Merge Keys (if available) ---
    if INPUT_KEYS_PATH.exists():
        df_keys = pd.read_csv(INPUT_KEYS_PATH, low_memory=False)
        df_forecast = merge_keys_into_forecast(df_forecast, df_keys)
    else:
        print("⚠️ Keys file not found. Proceeding with existing columns.")

    # --- Step 3: Load Historic Data for Training ---
    print("\n2. Loading Historic Data for Training...")
    historic_dfs = []
    for path in HISTORIC_DATA_PATHS:
        if path.exists():
            print(f"   Loading: {path.name}")
            historic_dfs.append(pd.read_csv(path, low_memory=False))
        else:
            print(f"   ⚠️ Not found: {path.name}")

    if not historic_dfs:
        print("❌ No historic data found for training. Cannot proceed.")
        return

    df_hist = pd.concat(historic_dfs, ignore_index=True)
    print(f"   Combined historic data: {len(df_hist):,} rows")

    # --- Step 4: Train & Apply ---
    refiner = DTypeRefiner(OUTPUT_DIR)
    refiner.train_models(df_hist)

    df_refined = refiner.apply_refinement(df_forecast)

    # --- Step 5: Save ---
    print(f"\n3. Saving Refined Data...")
    df_refined.to_csv(OUTPUT_REFINED_PATH, index=False)
    print(f"   ✅ Saved: {OUTPUT_REFINED_PATH.name}")

    # --- Step 6: Validate ---
    print("\n4. Running Validation...")
    validate_refinement_model(HISTORIC_DATA_PATHS, OUTPUT_REFINED_PATH, VALIDATION_DIR)

    print("\n" + "=" * 60)
    print("  DTYPE EXPANSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="DTYPE Expansion: Refine Census DTYPE 1-3 to 1-8"
    )
    parser.add_argument(
        "--sample",
        type=float,
        default=5,
        help="Sample percentage identifier (default: 5)"
    )
    args = parser.parse_args()

    main(sample_pct=args.sample)
