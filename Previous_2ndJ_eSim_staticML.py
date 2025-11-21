import pathlib
from typing import List, Tuple, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.multioutput import MultiOutputClassifier
from lightgbm import LGBMClassifier
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

def prepare_data_for_ml(
        train_file_paths: List[str],
        test_file_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads, preprocesses, and splits data into training and testing
    sets for a multi-output classification model.
    """
    print("--- 1. Loading and Concatenating Training Data ---")
    train_dfs = []
    for f in train_file_paths:
        try:
            df = pd.read_csv(f, dtype=str)
            train_dfs.append(df)
        except FileNotFoundError:
            print(f"Warning: File not found {f}. Skipping.")

    train_df = pd.concat(train_dfs, ignore_index=True)

    print("--- 2. Loading Test Data ---")
    test_df = pd.read_csv(test_file_path, dtype=str)

    # Example of editing:
    columns_to_use = ['HH_ID', 'EF_ID', 'CF_ID', 'PP_ID',
                      'MARSTH', 'EMPIN', 'TOTINC', 'EFSIZE', 'CFSIZE', 'KOL', 'ATTSCH', 'CIP', 'NOCS', "GENSTAT", "POWST",
                      "CITIZEN", "LFTAG", "CF_RP", "COW", 'CMA', 'AGEGRP', 'SEX', 'CFSTAT', 'BEDRM', 'ROOM', 'DTYPE', 'HHSIZE',
                      "BUILT", "TENUR", "CONDO", "PR"]

    # Filter both dataframes to only use these columns
    # (Also ensures test_df doesn't have extra cols)
    train_df = train_df[columns_to_use]
    test_df = test_df[columns_to_use]
    print(f"Using {len(columns_to_use)} manually selected columns.")
    # --- END OF NEW SECTION ---

    # --- 4. Define Column Lists ---
    target_cols = ['BEDRM','ROOM', 'DTYPE', "BUILT"]
    id_cols = ['HH_ID', 'EF_ID', 'CF_ID', 'PP_ID']

    # This logic now automatically uses your filtered 'columns_to_use' list
    feature_cols = [
        col for col in train_df.columns
        if col not in target_cols and col not in id_cols
    ]

    continuous_cols = ['EMPIN', 'TOTINC']
    categorical_cols = [col for col in feature_cols if col not in continuous_cols]

    print(f"Identified {len(feature_cols)} features (e.g., DTYPE, ROOM, EMPIN...).")
    print(f"Identified {len(target_cols)} targets (AGEGRP, SEX...).")

    # --- 5. Separate X and y (using .copy() to avoid warnings) ---
    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_cols].copy()
    X_test = test_df[feature_cols].copy()
    y_test = test_df[target_cols].copy()

    # --- 6. Convert Continuous Columns ---
    for col in continuous_cols:
        if col in X_train.columns:
            X_train[col] = pd.to_numeric(X_train[col], errors='coerce')
        if col in X_test.columns:
            X_test[col] = pd.to_numeric(X_test[col], errors='coerce')

    X_train[continuous_cols] = X_train[continuous_cols].fillna(0)
    X_test[continuous_cols] = X_test[continuous_cols].fillna(0)

    # Fill missing categorical values with a placeholder
    X_train[categorical_cols] = X_train[categorical_cols].fillna('Missing')
    X_test[categorical_cols] = X_test[categorical_cols].fillna('Missing')

    print("--- 7. Ordinal (Integer) Encoding Categorical Features ---")

    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    encoder.fit(X_train[categorical_cols])

    X_train[categorical_cols] = encoder.transform(X_train[categorical_cols])
    X_test[categorical_cols] = encoder.transform(X_test[categorical_cols])

    print(f"Preprocessing complete. Final feature count: {len(X_train.columns)}")

    return X_train, y_train, X_test, y_test
def train_classification_model(
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_test: pd.DataFrame,
        model_type: str = 'random_forest',
        use_class_weight: bool = True
) -> Any:

    if model_type == 'random_forest':
        print("\n--- 1. Initializing the RandomForestClassifier ---")
        weight = 'balanced' if use_class_weight else None

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            n_jobs=-1,
            random_state=42,
            class_weight=weight
        )

    elif model_type == 'lgbm':
        print("\n--- 1. Initializing the LGBMClassifier (wrapped) ---")
        is_unbalance = True if use_class_weight else False

        base_lgbm = LGBMClassifier(
            n_estimators=100,
            max_depth=20,
            n_jobs=-1,
            random_state=42,
            is_unbalance=is_unbalance
        )

        model = MultiOutputClassifier(base_lgbm, n_jobs=-1)

    else:
        print(f"Error: Unknown model_type '{model_type}'")
        return None

    print("--- 2. Training the Model (this may take a few minutes) ---")
    model.fit(X_train, y_train)

    print("--- 3. Making Predictions on the Test Set (2021 data) ---")
    y_pred = model.predict(X_test)

    y_pred_df = pd.DataFrame(y_pred, columns=y_train.columns)

    print("\n--- 4. Model Evaluation Reports ---")

    for col in y_train.columns:
        print("=" * 50)
        print(f"Classification Report for: {col}")
        print("=" * 50)

        y_true_col = y_test[col]
        y_pred_col = y_pred_df[col]

        # --- FIX IS HERE ---
        # Replaced .append() with pd.concat()
        labels = pd.unique(pd.concat([y_true_col, y_pred_col]))
        # --- END FIX ---

        report = classification_report(
            y_true_col,
            y_pred_col,
            labels=labels,
            zero_division=0
        )
        print(report)

    return model

if __name__ == '__main__':
    # BASE_DIR = pathlib.Path("C:/Users/o_iseri/Desktop/2ndJournal")
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal")

    DATA_DIR = BASE_DIR / "DataSources_CENSUS"
    OUTPUT_DIR = BASE_DIR / "Outputs_CENSUS"

    # --- 2006 Files ---
    cen06_filtered2 = OUTPUT_DIR / "cen06_filtered2.csv"
    cen11_filtered2 = OUTPUT_DIR / "cen11_filtered2.csv"
    cen16_filtered2 = OUTPUT_DIR / "cen16_filtered2.csv"
    cen21_filtered2 = OUTPUT_DIR / "cen21_filtered2.csv"

    # 2. Define your file lists
    train_files = [cen06_filtered2, cen11_filtered2, cen16_filtered2]
    test_file = cen21_filtered2

    # 3. Run the function
    X_train, y_train, X_test, y_test = prepare_data_for_ml(train_files, test_file)
    # 4. Inspect the results
    print("\n--- X_train Head ---")
    print(X_train.head())
    print("\n--- y_train Head ---")
    print(y_train.head())

    # 3. Run the new training function
    if X_train is not None:
        trained_model = train_classification_model(X_train, y_train, X_test, y_test, model_type='lgbm', use_class_weight=True) # 'lgbm'
