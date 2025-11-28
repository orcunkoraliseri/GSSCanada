from typing import List, Dict, Tuple
import tensorflow as tf
from tensorflow import keras
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import uuid
import pathlib
from tqdm import tqdm
import math
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

keras = tf.keras
layers = tf.keras.layers
# PREPARATION ----------------------------------------------------------------------------------------------------------
def get_feature_metadata(demo_cols, continuous_cols):
    """
    Creates a dictionary mapping logical feature names to their
    one-hot encoded column names.

    Example output:
    {
        'AGEGRP': {'type': 'categorical', 'columns': ['AGEGRP_1', ...]},
        'EMPIN':  {'type': 'continuous',  'columns': ['EMPIN']}
    }
    """
    feature_meta = {}

    # 1. Group Categorical Features (based on prefixes like 'AGEGRP_')
    # We find prefixes by splitting on the last underscore
    prefixes = set()
    for col in demo_cols:
        if col not in continuous_cols:
            # Assuming format "NAME_VALUE", extract "NAME"
            # We use rsplit to handle names that might contain underscores
            prefix = col.rsplit('_', 1)[0]
            prefixes.add(prefix)

    for prefix in prefixes:
        cols = [c for c in demo_cols if c.startswith(prefix + '_')]
        # Sort to ensure consistent order
        cols.sort()
        if cols:
            feature_meta[prefix] = {'type': 'categorical', 'columns': cols}

    # 2. Add Continuous Features
    for col in continuous_cols:
        if col in demo_cols:
            feature_meta[col] = {'type': 'continuous', 'columns': [col]}

    return feature_meta
def prepare_data_for_generative_model(file_paths_dict: Dict[int, str], sample_frac: float = 1.0, random_state: int = 42
) -> Tuple[pd.DataFrame, List[str], List[str], Dict[str, MinMaxScaler]]:
    """
    MASTER FUNCTION: Loads, combines, samples, and preprocesses census data.
    Used for both Training (Script 1) and Forecasting (Script 2).
    """

    # --- 1. Load and Combine All Datasets ---
    print("--- 1. Loading and combining all datasets... ---")
    all_dfs = []
    for year, path in file_paths_dict.items():
        try:
            df = pd.read_csv(path, dtype=str)
            df['YEAR'] = str(year)  # Create the YEAR column
            all_dfs.append(df)
        except FileNotFoundError:
            print(f"Warning: File not found {path}. Skipping.")

    if not all_dfs:
        raise ValueError("No data files were loaded. Check your file paths.")

    full_df = pd.concat(all_dfs, ignore_index=True)

    # --- 2. Household-level Sampling ---
    if sample_frac < 1.0:
        print(f"--- 2. Sampling {sample_frac * 100}% of households... ---")
        full_df['GLOBAL_HH_ID'] = full_df['YEAR'].astype(str) + '_' + full_df['HH_ID'].astype(str)
        unique_hh_ids = full_df['GLOBAL_HH_ID'].unique()
        sample_size = int(len(unique_hh_ids) * sample_frac)

        rng = np.random.RandomState(random_state)
        sampled_hh_ids = rng.choice(unique_hh_ids, size=sample_size, replace=False)

        full_df = full_df[full_df['GLOBAL_HH_ID'].isin(sampled_hh_ids)].copy()
        full_df = full_df.drop(columns=['GLOBAL_HH_ID'])
        print(f"   Sampled {sample_size} unique households.")
    else:
        print("--- 2. Using 100% of data. ---")

    # --- 3. Define Feature Lists ---

    # ID Columns to remove (Noise)
    ID_COLS_TO_DROP = ['HH_ID', 'EF_ID', 'CF_ID', 'PP_ID']

    # DEMOGRAPHICS (Outputs the model will Generate)
    DEMOGRAPHIC_FEATURES = [
        'YEAR', 'MARSTH', 'EMPIN', 'TOTINC', 'KOL', 'ATTSCH', 'CIP', 'NOCS',
        'GENSTAT', 'POWST', 'CITIZEN', 'LFTAG', 'CF_RP', 'COW', 'CMA',
        'AGEGRP', 'SEX', 'CFSTAT', 'INCTAX', 'HHSIZE', 'EFSIZE', 'CFSIZE',
        'PR', 'HRSWRK', 'MODE'
    ]

    # BUILDINGS (Inputs/Conditions the model uses to predict)
    # VALUE is here because it is a property of the building stock
    BUILDING_FEATURES = [
        'BUILTH', 'CONDO', 'BEDRM', 'ROOM', 'DTYPE', 'REPAIR', 'VALUE'
    ]

    # CONTINUOUS (To be scaled 0-1)
    CONTINUOUS_COLS = ['EMPIN', 'TOTINC', 'INCTAX', 'VALUE']

    # --- 4. Filter and Preprocess ---
    print("--- 3. Filtering to relevant columns... ---")
    all_features = list(set(DEMOGRAPHIC_FEATURES + BUILDING_FEATURES))
    all_cols_to_use = [
        col for col in all_features
        if col in full_df.columns and col not in ID_COLS_TO_DROP
    ]
    df_filtered = full_df[all_cols_to_use].copy()
    print(f"--- 4. Identified {len(all_cols_to_use)} total columns. ---")

    # --- 5. Scale and Encode ---
    print("--- 5. Scaling continuous data (MinMax) and one-hot encoding... ---")

    continuous_to_scale = [col for col in CONTINUOUS_COLS if col in df_filtered.columns]
    categorical_to_encode = [col for col in all_cols_to_use if col not in continuous_to_scale]

    # Fill missing values
    df_filtered[categorical_to_encode] = df_filtered[categorical_to_encode].fillna('Missing')

    scalers = {}
    for col in continuous_to_scale:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
        scaler = MinMaxScaler()
        df_filtered[col] = scaler.fit_transform(df_filtered[[col]])
        scalers[col] = scaler

    # One-Hot Encode
    df_processed = pd.get_dummies(df_filtered, columns=categorical_to_encode, dtype=int)

    # --- 6. Get Final Column Lists ---
    def get_final_col_names(feature_list, continuous_list, processed_cols):
        final_cols = []
        for col in feature_list:
            if col in continuous_list:
                if col in processed_cols:
                    final_cols.append(col)
            elif col in all_cols_to_use:
                # Find all one-hot columns starting with this feature name
                # We sort them to ensure the order is always 1, 10, 11... same as training
                cols = [c for c in processed_cols if c.startswith(f"{col}_")]
                final_cols.extend(sorted(cols))
        return sorted(list(set(final_cols)))

    processed_columns_set = set(df_processed.columns)

    final_demographic_cols = get_final_col_names(
        DEMOGRAPHIC_FEATURES,
        continuous_to_scale,
        processed_columns_set
    )

    final_building_cols = get_final_col_names(
        BUILDING_FEATURES,
        continuous_to_scale,
        processed_columns_set
    )

    print("Data preparation complete.")
    return df_processed, final_demographic_cols, final_building_cols, scalers
class Sampling(layers.Layer):
    """Uses (z_mean, z_log_var) to sample z, the latent vector."""

    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon
# ARCHITECTURE ---------------------------------------------------------------------------------------------------------
def build_encoder(n_demo_features, n_bldg_features, latent_dim):
    """Builds the Encoder model with Batch Normalization."""
    demo_input = keras.Input(shape=(n_demo_features,), name="demo_input")
    bldg_input = keras.Input(shape=(n_bldg_features,), name="bldg_input")

    merged_input = layers.concatenate([demo_input, bldg_input])

    # --- UPDATED BLOCK ---
    x = layers.Dense(512)(merged_input)  # 1. Linear part
    x = layers.BatchNormalization()(x)  # 2. Normalize
    x = layers.ReLU()(x)  # 3. Activate

    x = layers.Dense(256)(x)  # 1. Linear part
    x = layers.BatchNormalization()(x)  # 2. Normalize
    x = layers.ReLU()(x)  # 3. Activate
    # --- END UPDATE ---

    z_mean = layers.Dense(latent_dim, name="z_mean")(x)
    z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)

    z = Sampling()([z_mean, z_log_var])

    encoder = keras.Model(
        [demo_input, bldg_input],
        [z_mean, z_log_var, z],
        name="encoder"
    )
    return encoder
def build_decoder(n_bldg_features, latent_dim, feature_meta):
    """
    Builds a Multi-Head Decoder.
    Outputs a LIST of tensors (one per feature).
    """
    latent_input = keras.Input(shape=(latent_dim,), name="z_input")
    bldg_input = keras.Input(shape=(n_bldg_features,), name="bldg_input")

    merged_input = layers.concatenate([latent_input, bldg_input])

    # --- Shared Hidden Layers ---
    x = layers.Dense(256)(merged_input)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    x = layers.Dense(512)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    # --- Multi-Head Outputs ---
    outputs = []

    # We sort keys to ensure deterministic order
    for name in sorted(feature_meta.keys()):
        info = feature_meta[name]
        output_dim = len(info['columns'])

        if info['type'] == 'categorical':
            # Head for Categorical (Softmax for probability distribution)
            head = layers.Dense(output_dim, activation='softmax', name=f"out_{name}")(x)
        else:
            # Head for Continuous (Sigmoid for 0-1 scaling)
            head = layers.Dense(output_dim, activation='sigmoid', name=f"out_{name}")(x)

        outputs.append(head)

    # Define model
    decoder = keras.Model(
        [latent_input, bldg_input],
        outputs,  # Returns a list of outputs
        name="decoder"
    )
    return decoder
class MultiHeadCVAE(keras.Model):
    def __init__(self, encoder, decoder, feature_meta, beta=1.0, **kwargs):
        super().__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.feature_meta = feature_meta  # Store metadata to slice inputs
        self.beta = beta

        self.total_loss_tracker = keras.metrics.Mean(name="total_loss")
        self.recon_loss_tracker = keras.metrics.Mean(name="recon_loss")
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")

    @property
    def metrics(self):
        return [self.total_loss_tracker, self.recon_loss_tracker, self.kl_loss_tracker]

    def train_step(self, data):
        # Inputs are (demo_data, bldg_data)
        # We need demo_data BOTH as input to encoder AND as ground truth
        inputs, _ = data
        demo_input, bldg_input = inputs

        with tf.GradientTape() as tape:
            # 1. Encode
            z_mean, z_log_var, z = self.encoder([demo_input, bldg_input])

            # 2. Decode (returns a list of outputs)
            reconstructions = self.decoder([z, bldg_input])

            # 3. Calculate Reconstruction Loss (Sum of all heads)
            total_recon_loss = 0.0

            # We need to slice the 'demo_input' to match each head
            # We iterate in the SAME sorted order as the decoder
            sorted_features = sorted(self.feature_meta.keys())

            current_idx = 0
            for i, name in enumerate(sorted_features):
                info = self.feature_meta[name]
                dim = len(info['columns'])

                # Slice the true data for this feature
                y_true = demo_input[:, current_idx: current_idx + dim]
                y_pred = reconstructions[i]

                # Calculate appropriate loss
                if info['type'] == 'categorical':
                    # Categorical Crossentropy
                    loss = keras.losses.categorical_crossentropy(y_true, y_pred)
                else:
                    # Mean Squared Error (or Binary Crossentropy for 0-1)
                    loss = keras.losses.binary_crossentropy(y_true, y_pred)

                # Sum over batch and add to total
                total_recon_loss += tf.reduce_mean(loss)

                current_idx += dim

            # 4. KL Divergence
            kl_loss = -0.5 * (1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
            kl_loss = tf.reduce_mean(tf.reduce_sum(kl_loss, axis=1))

            # 5. Total Loss
            total_loss = total_recon_loss + (self.beta * kl_loss)

        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))

        self.total_loss_tracker.update_state(total_loss)
        self.recon_loss_tracker.update_state(total_recon_loss)
        self.kl_loss_tracker.update_state(kl_loss)

        return {
            "loss": self.total_loss_tracker.result(),
            "recon_loss": self.recon_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
        }
# TRAINING -------------------------------------------------------------------------------------------------------------
def train_cvae(df_processed, demo_cols, bldg_cols, continuous_cols=None, latent_dim=48, epochs=100, batch_size=4096):
    print("--- Preparing data for TensorFlow ---")

    feature_meta = get_feature_metadata(demo_cols, continuous_cols)
    n_demo_features = len(demo_cols)
    n_bldg_features = len(bldg_cols)

    demo_data = df_processed[demo_cols].values.astype(np.float32)
    bldg_data = df_processed[bldg_cols].values.astype(np.float32)

    dataset = tf.data.Dataset.from_tensor_slices(((demo_data, bldg_data), demo_data))
    dataset = dataset.shuffle(buffer_size=1024).batch(batch_size).prefetch(tf.data.AUTOTUNE)

    print("--- Building Multi-Head C-VAE ---")

    encoder = build_encoder(n_demo_features, n_bldg_features, latent_dim)
    decoder = build_decoder(n_bldg_features, latent_dim, feature_meta)

    # --- IMPROVEMENT 2: Lower Beta Manually ---
    # We force Beta to 0.1 to prioritize Reconstruction accuracy
    beta_weight = 0.1
    print(f"Using Manual KL Loss Beta weight: {beta_weight}")

    cvae = MultiHeadCVAE(encoder, decoder, feature_meta, beta=beta_weight)

    # --- IMPROVEMENT 3: Aggressive Learning Rate ---
    # Increased to 1e-3 to unstuck the model
    optimizer = keras.optimizers.Adam(learning_rate=1e-3, clipvalue=1.0)

    cvae.compile(optimizer=optimizer)

    print("--- Starting Training ---")
    history = cvae.fit(dataset, epochs=epochs)

    return encoder, decoder, cvae, history
#FORECASTING -------------------------------------------------------------------------------------------------------
# --- 3. Temporal Modeling Function ---
#FORECASTING -----------------------------------------------------------------------------------------------------------
# FORECASTING -------------------------------------------------------------------------------------------------------------
class VectorMomentumModel:
    """
    Models temporal drift as a weighted velocity vector.
    Captures non-linear turns (e.g., 2011->2016 shift) better than Linear Regression.
    """

    def __init__(self, decay_factor=0.95, recent_weight=0.5):
        self.decay = decay_factor  # Damping factor for long-term (prevent runaway)
        self.alpha = recent_weight  # Weight for recent trend (11->16)
        self.velocity = None
        self.last_point = None
        self.last_year = None

    def fit(self, years, points):
        """
        Calculates weighted momentum vector.
        years: List of years [2006, 2011, 2016]
        points: List of latent vectors (archetypes).
        """
        # Ensure sorted
        sorted_indices = np.argsort(years)
        years = np.array(years)[sorted_indices]
        points = np.array(points)[sorted_indices]

        # Calculate Historic Velocity (2006 -> 2011)
        dt_old = years[1] - years[0]
        v_old = (points[1] - points[0]) / dt_old

        # Calculate Recent Velocity (2011 -> 2016)
        dt_recent = years[2] - years[1]
        v_recent = (points[2] - points[1]) / dt_recent

        # Weighted Average Velocity
        self.velocity = (self.alpha * v_recent) + ((1 - self.alpha) * v_old)

        # Store anchor
        self.last_point = points[-1]
        self.last_year = years[-1]

        print(f"   -> Momentum Vector Calculated (Recent Weight: {self.alpha:.0%})")

    def predict(self, target_year_array):
        """
        Projects future points. Input is [[year]] to match sklearn API style.
        """
        target_year = target_year_array[0][0]
        delta_t = target_year - self.last_year

        # Apply projection with decay
        # Effective velocity slows down over time
        effective_velocity = self.velocity * (self.decay ** (delta_t / 5))

        prediction = self.last_point + (effective_velocity * delta_t)

        return np.array([prediction])

    # --- 1. Train Temporal Model ---
def train_temporal_model(encoder, df_processed, demo_cols, bldg_cols):
    print("--- Starting Step 3: Temporal Modeling (Vector Momentum) ---")

    # Find all 'YEAR_...' columns
    year_cols = sorted([col for col in demo_cols if col.startswith('YEAR_')])
    years = [int(col.split('_')[1]) for col in year_cols]

    X_temporal = []
    y_temporal = []
    last_avg_log_var = None

    print(f"   Extracting archetypes for years: {years}")
    for year, col_name in zip(years, year_cols):
        year_df = df_processed[df_processed[col_name] == 1]
        if len(year_df) == 0: continue

        demo_data = year_df[demo_cols].values.astype(np.float32)
        bldg_data = year_df[bldg_cols].values.astype(np.float32)

        # Predict latent space
        z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data], verbose=0)

        avg_z_mean = np.mean(z_mean, axis=0)
        X_temporal.append(year)
        y_temporal.append(avg_z_mean)

        if year == years[-1]:
            last_avg_log_var = np.mean(z_log_var, axis=0)

    print("--- Fitting Vector Momentum Model... ---")
    # Using Custom Vector Model instead of LinearRegression
    temporal_model = VectorMomentumModel(decay_factor=0.95, recent_weight=0.5)
    temporal_model.fit(X_temporal, y_temporal)

    return temporal_model, last_avg_log_var
# --- 3. Generation Function ---
def generate_future_population(decoder, temporal_model, last_avg_log_var, df_processed, bldg_cols, target_year,
                               n_samples):
    print(f"--- Starting Step 4: Generating Population for {target_year} ---")

    # 1. Predict future archetype
    predicted_z_mean = temporal_model.predict([[target_year]])

    # 2. Get realistic building conditions (from 2021)
    year_cols = sorted([col for col in df_processed.columns if col.startswith('YEAR_')])
    year_2021_col = year_cols[-1]
    bldg_conditions_2021 = df_processed[df_processed[year_2021_col] == 1][bldg_cols]

    bldg_future_samples = bldg_conditions_2021.sample(n_samples, replace=True).values.astype(np.float32)

    # 3. Generate new latent vectors
    latent_dim = len(predicted_z_mean[0])
    z_std_dev = np.exp(0.5 * last_avg_log_var)

    z_new = np.random.normal(loc=predicted_z_mean, scale=z_std_dev, size=(n_samples, latent_dim))

    # 4. Decode
    print(f"   Using decoder to generate {n_samples} profiles...")
    generated_list = decoder.predict([z_new, bldg_future_samples], verbose=0)

    # Concatenate Multi-Head Output
    generated_raw_matrix = np.concatenate(generated_list, axis=1)

    print("--- Generation Complete ---")
    return generated_raw_matrix, bldg_future_samples
# --- 4. Post-Processing Function ---
def post_process_generated_data(generated_raw_data, demo_cols, generated_bldg_data, bldg_cols, scalers):
    print("--- Starting Post-Processing ---")
    df_gen_demo = pd.DataFrame(generated_raw_data, columns=demo_cols)
    df_gen_bldg = pd.DataFrame(generated_bldg_data, columns=bldg_cols)
    df_final = pd.DataFrame()

    # Inverse Scale Continuous
    for col_name, scaler in scalers.items():
        if col_name in df_gen_demo.columns:
            col_data = df_gen_demo[col_name].values.reshape(-1, 1)
            df_final[col_name] = scaler.inverse_transform(col_data).flatten()

    # Decode One-Hot (Demographics)
    all_prefixes = set()
    for col in demo_cols:
        if '_' in col and col not in scalers:
            all_prefixes.add(col.rsplit('_', 1)[0])

    for prefix in all_prefixes:
        cat_cols = [col for col in demo_cols if col.startswith(f"{prefix}_")]
        if cat_cols:
            predicted_col = df_gen_demo[cat_cols].idxmax(axis=1)
            df_final[prefix] = predicted_col.str.replace(f"{prefix}_", "")

    # Decode One-Hot (Buildings)
    bldg_prefixes = set()
    for col in bldg_cols:
        if '_' in col and col not in scalers:
            bldg_prefixes.add(col.rsplit('_', 1)[0])

    for prefix in bldg_prefixes:
        cat_cols = [col for col in bldg_cols if col.startswith(f"{prefix}_")]
        if cat_cols:
            predicted_col = df_gen_bldg[cat_cols].idxmax(axis=1)
            df_final[prefix] = predicted_col.str.replace(f"{prefix}_", "")

    print("--- Post-Processing Complete ---")
    return df_final

#VISUALIZATION FOR FORECASTING -----------------------------------------------------------------------------------------
def plot_latent_trajectory(encoder, temporal_model, df_processed, demo_cols, bldg_cols):
    print("--- Generating Latent Space Trajectory Plot ---")

    # 1. Get Historical Means (2006-2021)
    years = [2006, 2011, 2016, 2021]
    history_vectors = []

    for year in years:
        col_name = f"YEAR_{year}"
        if col_name in df_processed.columns:
            year_df = df_processed[df_processed[col_name] == 1]
            demo_data = year_df[demo_cols].values.astype(np.float32)
            bldg_data = year_df[bldg_cols].values.astype(np.float32)

            # Get latent positions
            z_mean, _, _ = encoder.predict([demo_data, bldg_data], verbose=0)

            # Calculate average center
            history_vectors.append(np.mean(z_mean, axis=0))

    # 2. Get Forecasted Means (2025, 2030)
    future_years = [2025, 2030]
    future_vectors = []
    for year in future_years:
        pred_z = temporal_model.predict([[year]])[0]
        future_vectors.append(pred_z)

    # 3. Fit PCA on History + Future to find the best 2D plane
    all_vectors = np.array(history_vectors + future_vectors)
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(all_vectors)

    # 4. Plot
    plt.figure(figsize=(10, 8))

    # Plot History (Blue line)
    plt.plot(pca_result[:4, 0], pca_result[:4, 1], 'o-', label='Historical (06-21)', color='blue', markersize=8)

    # Plot Future (Red dashed line)
    # Connect 2021 to 2025
    plt.plot(pca_result[3:, 0], pca_result[3:, 1], 'o--', label='Forecast (25-30)', color='red', markersize=8)

    # Annotate points
    labels = years + future_years
    for i, txt in enumerate(labels):
        plt.annotate(txt, (pca_result[i, 0], pca_result[i, 1]), xytext=(5, 5), textcoords='offset points')

    plt.title(
        f"Demographic Drift in Latent Space (PCA Projection)\nExplained Variance: {np.sum(pca.explained_variance_ratio_):.2%}")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    save_path = VALIDATION_FORECASTVIS_DIR /"Latent_Trajectory_Plot.png"
    plt.savefig(save_path)
    print(f"   Plot saved to {save_path}")
#VALIDATION OF FORECASTING ---------------------------------------------------------------------------------------------
def validate_forecast_trajectory(encoder, df_processed, demo_cols, bldg_cols, output_dir):
    """
    Validates the forecasting logic by visualizing the latent space trajectory.
    Generates a 2-panel subplot:
      1. 2D PCA Trajectory (Map view)
      2. Component Evolution over Time (Time-series view)
    """
    print(f"\n{'=' * 60}")
    print(f"🔮 VALIDATING FORECAST TRAJECTORY (Vector Momentum)")
    print(f"{'=' * 60}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extract Historical Archetypes (2006, 2011, 2016)
    print("1. Extracting Historical Latent Points...")
    year_cols = sorted([col for col in demo_cols if col.startswith('YEAR_')])
    years_hist = [int(col.split('_')[1]) for col in year_cols]

    latent_points = []
    labels = []
    years_all = []

    for year, col_name in zip(years_hist, year_cols):
        year_df = df_processed[df_processed[col_name] == 1]
        if len(year_df) == 0: continue

        # Get mean latent vector for this year
        demo_data = year_df[demo_cols].values.astype(np.float32)
        bldg_data = year_df[bldg_cols].values.astype(np.float32)
        z_mean, _, _ = encoder.predict([demo_data, bldg_data], verbose=0)

        centroid = np.mean(z_mean, axis=0)
        latent_points.append(centroid)
        labels.append(f"{year}")
        years_all.append(year)

    # 2. Train Vector Model & Predict Future (2021, 2025, 2030)
    print("2. Projecting Future Points...")
    model = VectorMomentumModel(decay_factor=0.95, recent_weight=0.5)
    model.fit(years_hist, latent_points)

    years_future = [2021, 2025, 2030]
    for year in years_future:
        pred = model.predict([[year]])[0]  # Returns [1, dim] array
        latent_points.append(pred)
        labels.append(f"{year}")
        years_all.append(year)

    # 3. PCA Projection (Latent Dim -> 2D)
    print("3. Generating Plots...")
    all_points = np.array(latent_points)
    pca = PCA(n_components=2)
    points_2d = pca.fit_transform(all_points)

    # 4. PLOTTING (Subplots)
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    # --- SUBPLOT 1: Trajectory Map (PC1 vs PC2) ---
    ax1 = axes[0]
    n_hist = len(years_hist)

    # History Line
    ax1.plot(points_2d[:n_hist, 0], points_2d[:n_hist, 1], 'o-',
             color='blue', linewidth=2, label='History (06-16)', markersize=8)

    # Forecast Line (Connect from last history point)
    forecast_indices = range(n_hist - 1, len(points_2d))
    ax1.plot(points_2d[forecast_indices, 0], points_2d[forecast_indices, 1], 'o--',
             color='red', linewidth=2, label='Forecast (Vector)', markersize=8)

    for i, txt in enumerate(labels):
        ax1.annotate(txt, (points_2d[i, 0], points_2d[i, 1]),
                     xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')

    ax1.set_title(f"Latent Space Trajectory (PCA Map)\nExplained Variance: {np.sum(pca.explained_variance_ratio_):.1%}")
    ax1.set_xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]:.1%})")
    ax1.set_ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]:.1%})")
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend()

    # --- SUBPLOT 2: Time Series View (PC1 & PC2 over Years) ---
    ax2 = axes[1]
    ax2.plot(years_all, points_2d[:, 0], 's-', color='purple', label='PC1 Value', linewidth=2)
    ax2.plot(years_all, points_2d[:, 1], '^-', color='orange', label='PC2 Value', linewidth=2)
    ax2.axvline(x=2016, color='gray', linestyle=':', label='Forecast Start')

    ax2.set_title("Evolution of Principal Components Over Time")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Component Value (Z-Score Space)")
    ax2.set_xticks(years_all)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plot_path = output_dir / "Validation_Forecast_Trajectory.png"
    plt.savefig(plot_path)
    print(f"   ✅ Trajectory Subplots saved to: {plot_path}")
def validate_forecast_distributions(encoder, decoder, df_processed, demo_cols, bldg_cols, scalers, output_dir):
    """
    Performs 'Hindcasting' (Train 06-16, Forecast 21) and plots Real vs Forecast distributions
    for all variables in a single subplot grid.
    """
    print(f"\n{'=' * 60}")
    print(f"📊 VALIDATING FORECAST DISTRIBUTIONS (Hindcast 2021)")
    print(f"{'=' * 60}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Train Temporal Model on 2006-2016 ONLY
    print("1. Training Temporal Model (2006, 2011, 2016)...")
    years_train = [2006, 2011, 2016]
    target_year = 2021

    years_hist = []
    points_hist = []
    last_avg_log_var = None

    for year in years_train:
        col_name = f"YEAR_{year}"
        if col_name not in df_processed.columns: continue

        year_df = df_processed[df_processed[col_name] == 1]
        demo_data = year_df[demo_cols].values.astype(np.float32)
        bldg_data = year_df[bldg_cols].values.astype(np.float32)

        # Get Mean Latent Vector
        z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data], verbose=0)

        years_hist.append(year)
        points_hist.append(np.mean(z_mean, axis=0))

        if year == 2016:
            last_avg_log_var = np.mean(z_log_var, axis=0)

    # Use Vector Momentum Model (Consistent with Forecast Step)
    temporal_model = VectorMomentumModel(decay_factor=0.95, recent_weight=0.5)
    temporal_model.fit(years_hist, points_hist)

    # 2. Generate Synthetic 2021
    print("2. Generating Synthetic 2021 Population...")
    # Get Real 2021 Building Conditions for fair comparison
    real_2021_df = df_processed[df_processed[f"YEAR_{target_year}"] == 1]
    if len(real_2021_df) == 0:
        print("❌ Error: No Real 2021 data found for validation.")
        return

    bldg_conditions = real_2021_df[bldg_cols].values.astype(np.float32)

    # Predict 2021 Latent Mean
    pred_z_mean = temporal_model.predict([[target_year]])

    # Sample Z
    n_samples = len(real_2021_df)
    latent_dim = len(pred_z_mean[0])
    z_std_dev = np.exp(0.5 * last_avg_log_var)
    z_new = np.random.normal(loc=pred_z_mean, scale=z_std_dev, size=(n_samples, latent_dim))

    # Decode
    gen_list = decoder.predict([z_new, bldg_conditions], verbose=0)
    gen_matrix = np.concatenate(gen_list, axis=1)  # Multi-head concat

    # 3. Prepare Plotting Grid
    print("3. Generating Distribution Plots...")

    # Identify variables to plot
    # Continuous
    cont_cols = [c for c in scalers.keys() if c in demo_cols]

    # Categorical Prefixes
    cat_prefixes = set()
    for col in demo_cols:
        if '_' in col and col not in scalers and not col.startswith('YEAR_'):
            cat_prefixes.add(col.rsplit('_', 1)[0])
    cat_prefixes = sorted(list(cat_prefixes))

    total_plots = len(cont_cols) + len(cat_prefixes)
    cols_grid = 6
    rows_grid = math.ceil(total_plots / cols_grid)

    fig, axes = plt.subplots(rows_grid, cols_grid, figsize=(18, 3 * rows_grid))
    axes = axes.flatten()
    plot_idx = 0

    # --- A) Plot Continuous Variables ---
    for col_name in cont_cols:
        ax = axes[plot_idx]
        idx = demo_cols.index(col_name)

        # Inverse Scale
        real_val = real_2021_df[col_name].values.reshape(-1, 1)
        real_val = scalers[col_name].inverse_transform(real_val).flatten()

        gen_val = gen_matrix[:, idx].reshape(-1, 1)
        gen_val = scalers[col_name].inverse_transform(gen_val).flatten()

        # KDE Plot
        sns.kdeplot(real_val, label='Real 2021', fill=True, color='skyblue', ax=ax)
        sns.kdeplot(gen_val, label='Forecast 2021', fill=True, color='orange', ax=ax)
        ax.set_title(f"{col_name} (Continuous)")
        ax.legend()
        plot_idx += 1

    # --- B) Plot Categorical Variables ---
    for prefix in cat_prefixes:
        ax = axes[plot_idx]

        # Get one-hot columns for this feature
        cat_cols = [c for c in demo_cols if c.startswith(f"{prefix}_")]
        indices = [demo_cols.index(c) for c in cat_cols]

        # Calculate Real Distribution
        real_counts = real_2021_df[cat_cols].sum().values
        real_dist = real_counts / real_counts.sum()

        # Calculate Gen Distribution
        gen_probs = gen_matrix[:, indices]
        gen_dist = gen_probs.sum(axis=0) / gen_probs.sum()

        # Bar Plot
        labels = [c.replace(f"{prefix}_", "") for c in cat_cols]
        x = np.arange(len(labels))
        width = 0.35

        ax.bar(x - width / 2, real_dist, width, label='Real 2021', color='skyblue')
        ax.bar(x + width / 2, gen_dist, width, label='Forecast 2021', color='orange')

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax.set_title(f"{prefix} (Categorical)")
        ax.legend()
        plot_idx += 1

    # Hide unused subplots
    for i in range(plot_idx, len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    plot_path = output_dir / "Validation_Forecast_Distributions.png"
    plt.savefig(plot_path)
    print(f"   ✅ Distribution Subplots saved to: {plot_path}")
# VISUALIZATION & TESTING ----------------------------------------------------------------------------------------------
def plot_training_history(history):
    """
    Plots the total, reconstruction, and KL loss from the Multi-Head C-VAE
    training history.
    """
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # --- FIX IS HERE ---
    # Switched back to 'loss' because Keras standardizes the main loss key
    ax1.plot(history.history['loss'], label='Total Loss')
    # --- END FIX ---

    ax1.set_title('Total Training Loss over Epochs')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss Value')
    ax1.legend()
    ax1.grid(True)

    # --- Plot 2: Loss Components ---
    ax2.plot(history.history['recon_loss'], label='Reconstruction Loss')
    ax2.plot(history.history['kl_loss'], label='KL Loss')
    ax2.set_title('Loss Components over Epochs')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss Value')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
def check_reconstruction_quality(encoder, decoder, df_processed, demo_cols, bldg_cols, n_samples=3):
    """
    Picks a few real samples and compares them to the model's
    reconstruction. Handles Multi-Head Decoder output.
    """
    # 1. Select a few random samples
    data_sample = df_processed.sample(n_samples)

    # 2. Prepare the data
    demo_data = data_sample[demo_cols].values.astype(np.float32)
    bldg_data = data_sample[bldg_cols].values.astype(np.float32)

    # 3. Run data through the full VAE (Encode -> Decode)
    z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data])
    reconstructed_data_list = decoder.predict([z, bldg_data])

    # --- FIX IS HERE ---
    # The multi-head decoder returns a LIST of arrays.
    # We must concatenate them horizontally (axis=1) to form one big matrix.
    # Since 'demo_cols' is sorted alphabetically, and the decoder builds heads
    # alphabetically, the order will match perfectly.
    reconstructed_matrix = np.concatenate(reconstructed_data_list, axis=1)
    # --- END FIX ---

    # 4. Convert back to DataFrames for easy comparison
    original_df = pd.DataFrame(demo_data, columns=demo_cols)

    # Use the concatenated matrix here
    reconstructed_df = pd.DataFrame(reconstructed_matrix, columns=demo_cols)

    print("--- Checking Reconstruction Quality (Sample 1) ---")
    print("\n--- ORIGINAL ---")
    # Show the 10 most "active" features for the first person
    print(original_df.iloc[0].nlargest(10))

    print("\n--- RECONSTRUCTED ---")
    # Show the same 10 features from the reconstructed data
    print(reconstructed_df.iloc[0][original_df.iloc[0].nlargest(10).index])
def validate_vae_reconstruction(encoder, decoder, df_processed, demo_cols, bldg_cols, continuous_cols, output_dir, n_samples=5):
    """
    Expanded evaluation: Checks samples, compares Original vs. Reconstructed,
    prints to console, AND saves the detailed report to a CSV file.
    """
    print(f"\n{'=' * 60}")
    print(f"  EXPANDED RECONSTRUCTION CHECK ({n_samples} Samples)")
    print(f"{'=' * 60}")

    # 1. Select random samples
    data_sample = df_processed.sample(n_samples)

    # 2. Prepare data
    demo_data = data_sample[demo_cols].values.astype(np.float32)
    bldg_data = data_sample[bldg_cols].values.astype(np.float32)

    # 3. Predict
    z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data], verbose=0)
    reconstructed_list = decoder.predict([z, bldg_data], verbose=0)

    # Concatenate multi-head output into one matrix
    reconstructed_matrix = np.concatenate(reconstructed_list, axis=1)

    # 4. Create DataFrames
    df_orig = pd.DataFrame(demo_data, columns=demo_cols)
    df_recon = pd.DataFrame(reconstructed_matrix, columns=demo_cols)

    # 5. Identify Feature Groups
    categorical_prefixes = set()
    for col in demo_cols:
        if col not in continuous_cols:
            prefix = col.rsplit('_', 1)[0]
            categorical_prefixes.add(prefix)

    sorted_prefixes = sorted(list(categorical_prefixes))

    # --- LIST TO STORE RESULTS FOR CSV ---
    results_list = []

    # 6. Loop through each sample
    for i in range(n_samples):
        print(f"\n--- Sample {i + 1} / {n_samples} ---")
        print(f"{'FEATURE':<15} | {'ORIGINAL':<15} | {'PREDICTED':<15} | {'CONFIDENCE':<10} | {'STATUS'}")
        print("-" * 75)

        # A) Check Categorical Features
        for prefix in sorted_prefixes:
            cols = [c for c in demo_cols if c.startswith(prefix + '_')]

            # Original
            orig_row = df_orig.iloc[i][cols]
            orig_cat = orig_row.idxmax().replace(f"{prefix}_", "")

            # Reconstructed
            recon_row = df_recon.iloc[i][cols]
            pred_cat = recon_row.idxmax().replace(f"{prefix}_", "")
            confidence = recon_row.max()

            status = "Pass" if orig_cat == pred_cat else "Fail"
            status_icon = "✅" if status == "Pass" else "❌"

            print(f"{prefix:<15} | {orig_cat:<15} | {pred_cat:<15} | {confidence:.4f}     | {status_icon}")

            # Add to results list
            results_list.append({
                "Sample_ID": i + 1,
                "Feature": prefix,
                "Type": "Categorical",
                "Original": orig_cat,
                "Predicted": pred_cat,
                "Confidence/Diff": confidence,
                "Status": status
            })

        # B) Check Continuous Features
        for col in continuous_cols:
            if col in demo_cols:
                val_orig = df_orig.iloc[i][col]
                val_pred = df_recon.iloc[i][col]
                diff = abs(val_orig - val_pred)

                status = "Pass" if diff < 0.05 else "Fail"  # Threshold can be adjusted
                status_icon = "✅" if status == "Pass" else "⚠️"

                print(
                    f"{col:<15} | {val_orig:.4f}          | {val_pred:.4f}          | Diff: {diff:.3f}  | {status_icon}")

                # Add to results list
                results_list.append({
                    "Sample_ID": i + 1,
                    "Feature": col,
                    "Type": "Continuous",
                    "Original": val_orig,
                    "Predicted": val_pred,
                    "Confidence/Diff": diff,  # Storing Diff here for continuous
                    "Status": status
                })

    # --- 7. Save to CSV ---
    output_path = pathlib.Path(output_dir) / "Validation_VAE_Reconstruction/validation_vae_reconstruction.csv"
    df_results = pd.DataFrame(results_list)
    df_results.to_csv(output_path, index=False)
    print(f"\n✅ Detailed reconstruction report saved to: {output_path}")
#ASSEMBLE HOUSEHOLD ----------------------------------------------------------------------------------------------------
def assemble_households(csv_file_path, target_year, output_dir, start_id=100):
    """
    Reads forecasted CSV, reconstructs households, saves the LINKED CSV.
    Uses simple sequential IDs (100, 101, 102...) for households.
    """
    print(f"\n--- Assembling Households for {target_year} ---")
    print(f"   Loading data from: {csv_file_path}")

    # 1. LOAD DATA
    df_population = pd.read_csv(csv_file_path)

    # Generate PIDs (Personal IDs) - We keep these as UUIDs or Random strings
    # to distinguish people within the house.
    df_population['PID'] = [str(uuid.uuid4())[:8] for _ in range(len(df_population))]

    # Ensure Types
    df_population['HHSIZE'] = pd.to_numeric(df_population['HHSIZE'], errors='coerce').fillna(1).astype(int)
    df_population['CF_RP'] = df_population['CF_RP'].astype(str).str.replace('.0', '', regex=False)

    final_households = []

    # --- INITIALIZE COUNTER ---
    current_hh_id = start_id

    # --- PHASE 1: SINGLES (HHSIZE = 1) ---
    singles_mask = df_population['HHSIZE'] == 1
    df_singles = df_population[singles_mask].copy()

    if not df_singles.empty:
        # Assign a range of IDs to singles all at once
        num_singles = len(df_singles)
        df_singles['SIM_HH_ID'] = range(current_hh_id, current_hh_id + num_singles)
        current_hh_id += num_singles  # Increment counter
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

        # Assign Simple ID
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
                # Clone fallback
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
            if size == 1: continue

            mates_of_size = leftover_roommates[leftover_roommates['HHSIZE'] == size]
            mate_list = mates_of_size.to_dict('records')

            roommate_batch = []
            while mate_list:
                head = mate_list.pop()

                # Assign Simple ID
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
            print(f"⚠️ WARNING: {mismatches.sum()} households have mismatched sizes!")
        else:
            print("✅ VALIDATION SUCCESS: All households have correct member counts.")

    # --- SAVE TO CSV ---
    save_filename = f"forecasted_population_{target_year}_LINKED.csv"
    save_path = pathlib.Path(output_dir) / save_filename
    df_assembled.to_csv(save_path, index=False)
    print(f"✅ Saved linked {target_year} data to: {save_path}")

    return df_assembled
#PROFILE MATCHER -------------------------------------------------------------------------------------------------------
# =============================================================================
# CLASS 1: MatchProfiler (The Linker)
# =============================================================================
class MatchProfiler:
    """
    Phase 2 & 3: Assigns GSS Schedule IDs to Census Agents.
    Updated to include Residential Variables (DTYPE, BEDRM, etc.) in matching logic.
    """

    def __init__(self, df_census, df_gss, dday_col="DDAY", id_col="occID", cols_match_t1=None):
        print(f"\n{'=' * 60}")
        print(f"⚙️  INITIALIZING PHASE 2: MATCH PROFILER")
        print(f"{'=' * 60}")

        self.df_census = df_census.copy()
        self.id_col = id_col
        self.dday_col = dday_col

        # --- UPDATED TIERS WITH RESIDENTIAL VARIABLES ---
        # Tier 1: Perfect Match
        if cols_match_t1 is None:
            self.cols_t1 = [
                "HHSIZE", "HRSWRK", "AGEGRP", "MARSTH", "SEX",
                "KOL", "NOCS", "PR", "COW", "MODE",
                "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR"
            ]
        else:
            self.cols_t1 = cols_match_t1

        # Tier 2: Energy Drivers (Physical Dwelling Attributes + Key Drivers)
        self.cols_t2 = [
            "HHSIZE", "HRSWRK", "AGEGRP", "SEX", "COW",
            "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR"
        ]

        # Tier 3: Constraints (Occupancy physics only)
        self.cols_t3 = ["HHSIZE", "HRSWRK", "AGEGRP"]

        # Tier 4: Fail-safe
        self.cols_t4 = ["HHSIZE"]

        # Split & Flatten GSS to create "Catalogs"
        print(f"   Splitting GSS by Day Type ({dday_col})...")

        # --- FIX: Only include columns that actually exist in GSS ---
        # This prevents KeyError if residential variables (DTYPE, etc.) are missing in GSS
        available_t1 = [c for c in self.cols_t1 if c in df_gss.columns]
        missing_t1 = list(set(self.cols_t1) - set(available_t1))

        if missing_t1:
            print(f"⚠️  Warning: The following match columns are MISSING in GSS and will be ignored in matching:")
            print(f"    {missing_t1}")

        # We must include all AVAILABLE match columns in the catalog
        catalog_cols = list(set([self.id_col] + available_t1 + ["HHSIZE"]))

        # Weekday Catalog (Unique Profiles)
        raw_wd = df_gss[df_gss[self.dday_col].isin([2, 3, 4, 5, 6])]
        self.catalog_wd = raw_wd[catalog_cols].drop_duplicates(subset=[self.id_col])

        # Weekend Catalog (Unique Profiles)
        raw_we = df_gss[df_gss[self.dday_col].isin([1, 7])]
        self.catalog_we = raw_we[catalog_cols].drop_duplicates(subset=[self.id_col])

        print(f"   ✅ Catalogs Created: WD={len(self.catalog_wd):,}, WE={len(self.catalog_we):,}")

    def run_matching(self):
        print(f"\n🚀 Starting Matching Loop...")
        results = []
        for idx, agent in tqdm(self.df_census.iterrows(), total=len(self.df_census), desc="Matching"):
            # 1. Find Weekday Match
            wd_id, wd_tier = self._find_best_match(agent, self.catalog_wd)
            # 2. Find Weekend Match
            we_id, we_tier = self._find_best_match(agent, self.catalog_we)

            row = agent.to_dict()
            row['MATCH_ID_WD'] = wd_id
            row['MATCH_TIER_WD'] = wd_tier
            row['MATCH_ID_WE'] = we_id
            row['MATCH_TIER_WE'] = we_tier
            results.append(row)

        return pd.DataFrame(results)

    def _find_best_match(self, agent, catalog):
        # Tier 1: Perfect Match
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t1:
            if col in catalog.columns and col in agent:
                mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "1_Perfect"

        # Tier 2: Energy Drivers
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t2:
            if col in catalog.columns and col in agent:
                mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "2_Drivers"

        # Tier 3: Constraints
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t3:
            if col in catalog.columns and col in agent:
                mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "3_Constraints"

        # Tier 4: FailSafe
        mask = (catalog["HHSIZE"] == agent["HHSIZE"])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "4_FailSafe"

        return catalog.sample(1)[self.id_col].values[0], "5_Random"
# =============================================================================
# CLASS 2: ScheduleExpander (The Retriever)
# =============================================================================
class ScheduleExpander:
    """
    Phase 4: Retrieval & Expansion.
    Takes the Matched Census DF and the Raw GSS DF.
    Retrieves the original variable-length episode lists.
    """

    def __init__(self, df_gss_raw, id_col="occID"):
        print(f"\n{'=' * 60}")
        print(f"📂 INITIALIZING PHASE 4: SCHEDULE EXPANDER")
        print(f"{'=' * 60}")

        self.df_gss_raw = df_gss_raw
        self.id_col = id_col

        # Indexing the Raw GSS by occID for instant retrieval
        print("   Indexing GSS Episodes for fast retrieval...")
        self.gss_indexed = self.df_gss_raw.set_index(self.id_col).sort_index()
        print("   ✅ Indexing complete.")

    def get_episodes(self, matched_id):
        """
        Directly retrieves episodes based on the Schedule ID.
        Used by generate_full_expansion.
        """
        try:
            # .loc[[id]] ensures we return a DataFrame, not a Series
            return self.gss_indexed.loc[[matched_id]].copy()
        except KeyError:
            # If ID is missing (shouldn't happen if matching worked), return None
            return None
# =============================================================================
# HELPER FUNCTIONS & MAIN EXECUTION
# =============================================================================
def verify_sample(df_matched, expander, n=3):
    print(f"\n🔎 VERIFYING EXPANSION (Sample of {n})")
    for i, agent in df_matched.head(n).iterrows():
        id_wd = agent['MATCH_ID_WD']
        id_we = agent['MATCH_ID_WE']
        ep_wd = expander.get_episodes(id_wd)
        ep_we = expander.get_episodes(id_we)
        count_wd = len(ep_wd) if ep_wd is not None else 0
        count_we = len(ep_we) if ep_we is not None else 0
        print(f"   User {i}: WD={count_wd} rows | WE={count_we} rows")
def generate_full_expansion(df_matched, expander, output_path):
    print(f"\n💾 Expanding Schedules for {len(df_matched)} agents...")
    all_episodes = []

    # Use 'idx' as the Unique Agent ID
    for idx, agent in tqdm(df_matched.iterrows(), total=len(df_matched), desc="Expanding"):

        # List of residential variables to carry over
        res_vars = ["DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR"]

        # Expand Weekday
        ep_wd = expander.get_episodes(agent['MATCH_ID_WD'])
        if ep_wd is not None:
            ep_wd = ep_wd.copy()
            ep_wd['SIM_HH_ID'] = agent['SIM_HH_ID']
            ep_wd['Day_Type'] = 'Weekday'
            ep_wd['AgentID'] = idx  # Unique ID

            # --- CRITICAL: Ensure Residential Variables are carried over ---
            for var in res_vars:
                if var in agent:
                    ep_wd[var] = agent[var]

            all_episodes.append(ep_wd)

        # Expand Weekend
        ep_we = expander.get_episodes(agent['MATCH_ID_WE'])
        if ep_we is not None:
            ep_we = ep_we.copy()
            ep_we['SIM_HH_ID'] = agent['SIM_HH_ID']
            ep_we['Day_Type'] = 'Weekend'
            ep_we['AgentID'] = idx  # Unique ID

            # --- CRITICAL: Ensure Residential Variables are carried over ---
            for var in res_vars:
                if var in agent:
                    ep_we[var] = agent[var]

            all_episodes.append(ep_we)

    if all_episodes:
        full_df = pd.concat(all_episodes)
        print(f"   Sorting expanded data...")
        full_df = full_df.sort_values(by=['SIM_HH_ID', 'Day_Type', 'AgentID'])
        full_df.to_csv(output_path, index=False)
        print(f"✅ Saved Expanded File: {len(full_df):,} rows to {output_path.name}")
#-----------------------------------------------------------------------------------------------------------------------

#VALIDATION: PROFILE MATCHER -------------------------------------------------------------------------------------------
def validate_matching_quality(df_matched, expander, save_path=None):
    """
    Calculates validation metrics and saves the report to a text file.
    """
    # --- Buffer to capture output ---
    report_buffer = []

    def log(message):
        """Helper to print to console AND append to buffer."""
        print(message)
        report_buffer.append(message)

    log(f"\n{'=' * 60}")
    log(f"📊 VALIDATION REPORT (CORRECTED)")
    log(f"{'=' * 60}")

    # --- METHOD 1: TIER DISTRIBUTION ---
    log(f"\n1. MATCH QUALITY (TIER DISTRIBUTION)")
    log("-" * 40)

    for day_type in ['WD', 'WE']:
        col = f'MATCH_TIER_{day_type}'
        if col in df_matched.columns:
            counts = df_matched[col].value_counts(normalize=True) * 100
            log(f"\n   [{day_type} Matching Tiers]")
            for tier, pct in counts.items():
                log(f"      - {tier}: {pct:.1f}%")

    # --- METHOD 2: BEHAVIORAL CONSISTENCY ---
    log(f"\n2. BEHAVIORAL CONSISTENCY (Workers vs. Non-Workers)")
    log("-" * 40)

    # Filter for Employees (COW 1 or 2)
    # We take a larger sample (up to 500) for better accuracy
    sample_size = min(500, len(df_matched))
    workers = df_matched[df_matched['COW'].isin([1, 2])].sample(sample_size)

    work_minutes = []

    for _, agent in workers.iterrows():
        # Get Weekday episodes
        ep_wd = expander.get_episodes(agent['MATCH_ID_WD'])

        if ep_wd is not None:
            # Filter for Work Activities
            # Standard GSS Work Codes often start with '1' or '0'. Adjust if needed.
            work_acts = ep_wd[ep_wd['occACT'].astype(str).str.startswith(('1', '0', '8'))]

            total_duration = 0
            for _, row in work_acts.iterrows():
                s = row['start']
                e = row['end']

                # --- FIX FOR MIDNIGHT WRAP ---
                # If end time is smaller than start time (e.g. 02:00 < 23:00), adds 24h (1440 min)
                if e < s:
                    duration = (e + 1440) - s
                else:
                    duration = e - s

                total_duration += duration

            work_minutes.append(total_duration)

    avg_work = np.mean(work_minutes) if work_minutes else 0
    log(f"   👉 Average Work Duration for 'Employees' (n={sample_size}): {avg_work:.0f} minutes/day")

    if avg_work < 60:
        log("      ⚠️ WARNING: Low work duration. Check if 'occACT' filter matches your GSS codes.")
    elif avg_work > 300:
        log("      ✅ Success: Employees are performing ~5-8 hours of work.")
    else:
        log("      ℹ️ Note: Work duration is moderate. Verify part-time vs full-time mix.")

    # --- STEP 3: SAVE TO FILE ---
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(report_buffer))
            print(f"\n✅ Validation Report saved to: {save_path}")
        except Exception as e:
            print(f"\n❌ Error saving report: {e}")
#PROFILE MATCHER: POST-PROCESSING --------------------------------------------------------------------------------------
class DTypeRefiner:
    """
    Refines coarse DTYPE categories (1, 2, 3) into detailed categories (1-8)
    using STOCHASTIC SAMPLING and DERIVED FEATURES to improve accuracy.
    """

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}

        # Base Features + Derived Features
        self.base_features = ['BEDRM', 'ROOM', 'PR', 'HHSIZE', 'CONDO', 'REPAIR']
        self.train_features = self.base_features + ['ROOM_PER_PERSON', 'BEDRM_RATIO']

        self.dtype_labels = {
            1: "Single-detached",
            2: "Semi-detached",
            3: "Row house",
            4: "Duplex",
            5: "Apt 5+ Storeys",
            6: "Apt <5 Storeys",
            7: "Other single-attached",
            8: "Movable"
        }

    def _add_derived_features(self, df):
        """
        Creates ratio-based features to help distinguish similar housing types.
        """
        df = df.copy()
        # Avoid division by zero
        df['HHSIZE'] = df['HHSIZE'].replace(0, 1)
        df['ROOM'] = df['ROOM'].replace(0, 1)

        # 1. Crowding Metric: Rooms per Person
        # (Row houses often have more space per person than Duplexes)
        df['ROOM_PER_PERSON'] = df['ROOM'] / df['HHSIZE']

        # 2. Structural Metric: Bedroom to Room Ratio
        # (Apartments often have higher bedroom ratios than Houses which have living/dining rooms)
        df['BEDRM_RATIO'] = df['BEDRM'] / df['ROOM']

        return df.fillna(0)

    def train_models(self, df_historic):
        print(f"\n🧠 Training DTYPE Refinement Models (With Derived Features)...")

        # Pre-process Historic Data
        for col in self.base_features:
            if col in df_historic.columns:
                df_historic[col] = pd.to_numeric(df_historic[col], errors='coerce').fillna(0)

        # Add the new "Smart" features
        df_historic = self._add_derived_features(df_historic)

        # --- MODEL A: APARTMENTS (2 -> 5, 6) ---
        subset_apt = df_historic[df_historic['DTYPE'].isin([5, 6])]
        if len(subset_apt) > 100:
            clf_apt = RandomForestClassifier(
                n_estimators=150,  # More trees
                max_depth=15,  # Prevent overfitting to majority
                min_samples_leaf=5,  # Smooth out noise
                random_state=42,
                class_weight='balanced'  # Critical for minority classes
            )
            clf_apt.fit(subset_apt[self.train_features], subset_apt['DTYPE'])
            self.models['Apt'] = clf_apt
            print(f"   ✅ Trained Apartment Splitter (n={len(subset_apt)})")

        # --- MODEL B: OTHER DWELLINGS (3 -> 2, 3, 4, 7, 8) ---
        subset_other = df_historic[df_historic['DTYPE'].isin([2, 3, 4, 7, 8])]
        if len(subset_other) > 100:
            clf_other = RandomForestClassifier(
                n_estimators=150,
                max_depth=15,
                min_samples_leaf=5,
                random_state=42,
                class_weight='balanced'
            )
            clf_other.fit(subset_other[self.train_features], subset_other['DTYPE'])
            self.models['Other'] = clf_other
            print(f"   ✅ Trained 'Other' Decoder (n={len(subset_other)})")

    def apply_refinement(self, df_forecast):
        print(f"\n✨ Applying Refinement with Enhanced Features...")

        # Generate the same features for the forecast data
        df_enhanced = self._add_derived_features(df_forecast)
        X = df_enhanced[self.train_features].fillna(0)

        refined_dtype = df_forecast['DTYPE'].copy()

        # --- APPLY MODEL A (Apartments) ---
        if 'Apt' in self.models:
            mask = (df_forecast['DTYPE'] == 2)
            if mask.sum() > 0:
                probs = self.models['Apt'].predict_proba(X[mask])
                classes = self.models['Apt'].classes_
                # Stochastic Sample
                choices = [np.random.choice(classes, p=p) for p in probs]
                refined_dtype.loc[mask] = choices
                print(f"   Refined {mask.sum()} Apartments (Stochastic)")

        # --- APPLY MODEL B (Other) ---
        if 'Other' in self.models:
            mask = (df_forecast['DTYPE'] == 3)
            if mask.sum() > 0:
                probs = self.models['Other'].predict_proba(X[mask])
                classes = self.models['Other'].classes_
                # Stochastic Sample
                choices = [np.random.choice(classes, p=p) for p in probs]
                refined_dtype.loc[mask] = choices
                print(f"   Refined {mask.sum()} 'Other' dwellings (Stochastic)")

        # Update DataFrame
        df_forecast['DTYPE_Detailed'] = refined_dtype
        df_forecast['DTYPE'] = refined_dtype

        return df_forecast
def validate_refinement_model(historic_input, forecast_refined_path, output_dir):
    # --- Setup Output Directory & Logging ---
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "Validation_Report_DTYPE.txt"
    report_buffer = []

    def log(message=""):
        """Helper to print to console and save to buffer."""
        print(message)
        report_buffer.append(str(message))

    log(f"\n{'=' * 60}")
    log(f"🕵️‍♂️ VALIDATING DTYPE REFINEMENT LOGIC")
    log(f"{'=' * 60}")
    log(f"   📂 Output Folder: {output_dir}")

    # 1. Load Data
    log("\n1. Loading Datasets...")

    # Handle List of Paths vs Single Path
    if isinstance(historic_input, list):
        log(f"   Loading {len(historic_input)} historic files...")
        dfs = []
        for p in historic_input:
            dfs.append(pd.read_csv(p, low_memory=False))
        df_hist = pd.concat(dfs, ignore_index=True)
    else:
        df_hist = pd.read_csv(historic_input, low_memory=False)

    df_future = pd.read_csv(forecast_refined_path, low_memory=False)

    log(f"   Historic Data: {len(df_hist):,} rows")
    log(f"   Refined Forecast: {len(df_future):,} rows")

    # Features used in Step 2b
    features = ['BEDRM', 'ROOM', 'PR', 'HHSIZE', 'CONDO', 'REPAIR', 'ROOM_PER_PERSON', 'BEDRM_RATIO']

    # Create derived features for validation if missing in historic
    if 'ROOM_PER_PERSON' not in df_hist.columns:
        df_hist['HHSIZE'] = df_hist['HHSIZE'].replace(0, 1)
        df_hist['ROOM'] = df_hist['ROOM'].replace(0, 1)
        df_hist['ROOM_PER_PERSON'] = df_hist['ROOM'] / df_hist['HHSIZE']
        df_hist['BEDRM_RATIO'] = df_hist['BEDRM'] / df_hist['ROOM']

    dtype_labels = {
        1: "Single-detached", 2: "Semi-detached", 3: "Row house",
        4: "Duplex", 5: "Apt 5+ Storeys", 6: "Apt <5 Storeys",
        7: "Other single-attached", 8: "Movable"
    }

    # =========================================================
    # PART A: INTERNAL VALIDITY
    # =========================================================
    log(f"\n2. INTERNAL VALIDATION (Train/Test Split)...")

    # Filter for complex categories 'Other' (2,3,4,7,8)
    mask_other = df_hist['DTYPE'].isin([2, 3, 4, 7, 8])
    X = df_hist.loc[mask_other, features].fillna(0)
    y = df_hist.loc[mask_other, 'DTYPE']

    if len(X) > 100:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced')
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)

        report = classification_report(y_test, preds, output_dict=True, zero_division=0)
        log(f"   👉 Accuracy on 'Other' Dwellings: {report['accuracy']:.2%}")
        log("   👉 Breakdown by Class (Precision/Recall):")
        for cls, metrics in report.items():
            if cls.isdigit():
                label = dtype_labels.get(int(cls), cls)
                log(f"      - {label:<22}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}")
    else:
        log("   ⚠️ Not enough historic data to validate model performance.")

    # =========================================================
    # PART B: EXTERNAL VALIDITY
    # =========================================================
    log(f"\n3. EXTERNAL VALIDATION (Distribution Comparison)...")

    dist_hist = df_hist['DTYPE'].value_counts(normalize=True).sort_index() * 100
    dist_fut = df_future['DTYPE'].value_counts(normalize=True).sort_index() * 100

    df_comp = pd.DataFrame({
        'Historic (Combined)': dist_hist,
        'Forecast (2030 Refined)': dist_fut
    }).fillna(0)

    df_comp.index = [dtype_labels.get(i, f"Code {i}") for i in df_comp.index]

    log("\n   --- Distribution Comparison (%) ---")
    log(df_comp.round(1).to_string())

    # =========================================================
    # PART C: VISUALIZATION
    # =========================================================
    log(f"\n4. GENERATING PLOT...")
    plt.figure(figsize=(12, 6))
    df_plot = df_comp.reset_index().melt(id_vars='index', var_name='Dataset', value_name='Percentage')

    sns.barplot(data=df_plot, x='index', y='Percentage', hue='Dataset', palette='viridis')
    plt.title("Dwelling Type Distribution: Historic Baseline vs. Refined Forecast")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save Plot to Specific Folder
    plot_path = output_dir / "Validation_DTYPE_Refinement.png"
    plt.savefig(plot_path)
    log(f"   ✅ Plot saved to: {plot_path}")

    # --- SAVE TEXT REPORT ---
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_buffer))
        print(f"\n✅ Validation Report saved to: {report_path}")
    except Exception as e:
        print(f"❌ Error saving text report: {e}")
#HOUSEHOLD AGGREGATION -------------------------------------------------------------------------------------------------
class HouseholdAggregator:
    """
    Transforms individual episode lists into aggregated Household Profiles.
    Resolution: 5 Minutes (288 slots per 24 hours).

    Step A: Grid Construction (Individual)
    Step B: Binary Presence (Household) -> 'occPre'
    Step C: Social Density (Household)    -> 'occDensity'
    Step D: Activity Sets (Household)     -> 'occActivity'
    """

    def __init__(self, resolution_min=5):
        self.res = resolution_min
        self.slots = int(1440 / self.res)  # 288 slots for 24h

        # Social columns to sum for Step C (excluding 'Alone')
        self.social_cols = [
            'Spouse', 'Children', 'parents', 'friends',
            'otherHHs', 'others', 'otherInFAMs'
        ]

    def process_all(self, df_expanded):
        """
        Main driver function.
        Groups data by Household and Day Type, aggregates,
        and then merges aggregation back to individual grids.
        Includes ALL static columns from the input CSV (Demographics, etc.).
        """
        print(f"   Grouping data by Household and Day Type...")

        # Columns that change per episode and shouldn't be broadcasted statically
        time_varying_cols = [
            'start', 'end', 'EPINO', 'occACT', 'occPRE', 'social_sum',
            'Spouse', 'Children', 'parents', 'friends',
            'otherHHs', 'others', 'otherInFAMs'
        ]

        # Group by Household AND Day
        groups = df_expanded.groupby(['SIM_HH_ID', 'Day_Type'])

        full_data_results = []

        # Iterate through each household scenario
        for (hh_id, day_type), group_df in tqdm(groups, desc="Processing Households"):

            # 1. Map AgentID -> Grid DataFrame
            people_grids_map = {}
            # 2. Map AgentID -> Static Metadata (Series)
            people_meta_map = {}

            # FIX 1: Group by 'AgentID' (Unique Index) instead of 'occID'
            # This ensures distinct people with the same GSS ID are treated separately
            if 'AgentID' not in group_df.columns:
                raise ValueError(
                    "❌ Error: 'AgentID' column missing. Please re-run Step 2 (Expansion) with the updated script.")

            for agent_id, person_data in group_df.groupby('AgentID'):
                # Step A: Create 5-min grid for this person
                grid = self._create_individual_grid(person_data)
                people_grids_map[agent_id] = grid

                # Capture Static Metadata (Take 1st row, drop time-varying)
                meta = person_data.iloc[0].drop(labels=time_varying_cols, errors='ignore')
                people_meta_map[agent_id] = meta

            # 3. Steps B, C, D: Aggregate the household
            hh_profile = self._aggregate_household(list(people_grids_map.values()))

            # 4. INTEGRATION: Merge Household Data + Individual Grid + Static Metadata
            for agent_id, p_grid in people_grids_map.items():
                # a. Concatenate Household Profile + Individual Grid
                combined = pd.concat([hh_profile, p_grid], axis=1)

                # b. Add Static Metadata
                meta = people_meta_map[agent_id]
                for col_name, val in meta.items():
                    combined[col_name] = val

                # Ensure essential keys are correct
                combined['SIM_HH_ID'] = hh_id
                combined['Day_Type'] = day_type
                combined['AgentID'] = agent_id  # Persist Unique ID

                full_data_results.append(combined)

        # Combine all individuals into one big dataframe
        return pd.concat(full_data_results, ignore_index=True)

    def _create_individual_grid(self, episodes):
        """
        Step A: 5-Minute Grid Construction (Standardization)
        Converts variable start/end times into a fixed length array (288 slots).
        """
        # Initialize blank arrays
        loc_grid = np.zeros(self.slots, dtype=int)
        act_grid = np.zeros(self.slots, dtype=int)
        dens_grid = np.zeros(self.slots, dtype=int)

        # --- FIX 2: Density Logic (Ghost Density Fix) ---
        valid_social = [c for c in self.social_cols if c in episodes.columns]

        # Convert 1=Yes, 2=No, 9=Unknown to Binary (1=Yes, 0=Else)
        episodes_social = episodes[valid_social].replace({1: 1, 2: 0, 9: 0}).fillna(0)

        # MASK: Only count social density if occPRE == 1 (Home)
        # If occPRE is NOT 1 (e.g. Work/Travel), density becomes 0
        is_home = (episodes['occPRE'] == 1).astype(int)

        # Assign to copy to avoid warnings
        episodes = episodes.copy()
        episodes['social_sum'] = episodes_social.sum(axis=1) * is_home

        # Fill the grid based on episodes
        for _, row in episodes.iterrows():
            # Convert minutes to slot index
            s_idx = int(np.floor(row['start'] / self.res))
            e_idx = int(np.floor(row['end'] / self.res))

            s_idx = max(0, min(s_idx, self.slots - 1))
            e_idx = max(0, min(e_idx, self.slots))

            # Fill range
            if e_idx > s_idx:
                loc_grid[s_idx:e_idx] = row['occPRE']
                act_grid[s_idx:e_idx] = row['occACT']
                dens_grid[s_idx:e_idx] = row['social_sum']

        # Return dataframe for this individual
        return pd.DataFrame({
            'ind_occPRE': loc_grid,
            'ind_occACT': act_grid,
            'ind_density': dens_grid
        })

    def _aggregate_household(self, people_grids):
        """
        Executes Steps B, C, and D combining multiple individual grids.
        """
        # Create Time Index (00:00, 00:05, ... 23:55)
        time_slots = pd.date_range("00:00", "23:55", freq=f"{self.res}min").strftime('%H:%M')

        # Dataframe to store final household results
        hh_df = pd.DataFrame({'Time_Slot': time_slots})

        if not people_grids:
            hh_df['occPre'] = 0
            hh_df['occDensity'] = 0
            hh_df['occActivity'] = ""
            return hh_df

        # --- STEP B: Aggregated Presence (Binary) -> occPre ---
        # 1. Stack location arrays (using 'ind_occPRE')
        loc_stack = np.vstack([p['ind_occPRE'].values for p in people_grids])

        # 2. Convert to Binary Presence (1=Home, 0=Outside)
        presence_binary = (loc_stack == 1).astype(int)

        # 3. Sum vertically (How many people home?)
        occupancy_count = presence_binary.sum(axis=0)

        # 4. Household Binary Status (1 if anyone is home, else 0)
        hh_df['occPre'] = (occupancy_count >= 1).astype(int)

        # --- STEP C: Social Density -> occDensity ---
        # 1. Stack density arrays (using 'ind_density')
        dens_stack = np.vstack([p['ind_density'].values for p in people_grids])

        # 2. Sum vertically
        hh_df['occDensity'] = dens_stack.sum(axis=0)

        # --- STEP D: Aggregated Activity Sets -> occActivity ---
        # 1. Stack activity arrays (using 'ind_occACT')
        act_stack = np.vstack([p['ind_occACT'].values for p in people_grids])

        activity_sets = []

        # Iterate through each time slot (column)
        for t in range(self.slots):
            # Get activities and presence for this moment
            acts_at_t = act_stack[:, t]
            pres_at_t = presence_binary[:, t]  # Only consider people AT HOME

            # Filter: Keep activities only for people who are PRESENT (1)
            valid_acts = acts_at_t[pres_at_t == 1]

            # Get Unique, Sort, Convert to String
            if len(valid_acts) > 0:
                unique_acts = sorted(np.unique(valid_acts))
                # Remove 0 or NaNs if any slipped in
                unique_acts = [str(a) for a in unique_acts if a > 0]
                act_str = ",".join(unique_acts)
            else:
                act_str = "0"  # "0" indicates Unoccupied/No Activity

            activity_sets.append(act_str)

        hh_df['occActivity'] = activity_sets

        return hh_df
#VALIDATION OF AGGREGATION ---------------------------------------------------------------------------------------------
def validate_household_aggregation(df_full, report_path=None):
    """
    Performs logical checks on the aggregated data and saves report to txt.
    """
    # Buffer to hold log messages
    logs = []

    def log(message):
        print(message)
        logs.append(str(message))

    log(f"\n{'=' * 60}")
    log(f"🔎 VALIDATING HOUSEHOLD AGGREGATION")
    log(f"{'=' * 60}")

    # --- CHECK 1: COMPLETENESS ---
    log(f"\n1. CHECKING TIME GRID COMPLETENESS...")
    if 'AgentID' not in df_full.columns:
        log("   ❌ Error: 'AgentID' column missing. Cannot validate completeness.")
        return False

    counts = df_full.groupby(['AgentID', 'Day_Type']).size()

    if (counts == 288).all():
        log(f"   ✅ Success: All {len(counts)} person-days have exactly 288 time slots.")
    else:
        errors = counts[counts != 288]
        log(f"   ❌ Error: Found {len(errors)} incomplete profiles.")
        log(errors.head())

    # --- CHECK 2: LOGIC (Presence vs. Density) ---
    log(f"\n2. CHECKING LOGIC (Presence vs. Density)...")
    empty_house = df_full[df_full['occPre'] == 0]
    ghosts = empty_house[empty_house['occDensity'] > 0]

    if len(ghosts) == 0:
        log(f"   ✅ Success: No social density detected in empty houses.")
    else:
        log(f"   ❌ Error: Found {len(ghosts)} rows where House is Empty but Density > 0.")

    # --- CHECK 3: ACTIVITY CONSISTENCY ---
    log(f"\n3. CHECKING ACTIVITY STRINGS...")
    if 'occActivity' in empty_house.columns:
        ghost_activities = empty_house[empty_house['occActivity'].astype(str) != "0"]
        if len(ghost_activities) == 0:
            log(f"   ✅ Success: Activity is correctly marked '0' when empty.")
        else:
            log(f"   ❌ Error: Found {len(ghost_activities)} rows with activities in empty house.")

    # --- SAVE REPORT TO FILE ---
    if report_path:
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("\n".join(logs))
                f.write("\n")  # Add newline at end
            # We don't print "Saved" here to avoid cluttering the console output if it's called often
        except Exception as e:
            print(f"   ❌ Error writing report file: {e}")

    return True
def visualize_multiple_households(df_full, n_samples=10, output_img_path=None, report_path=None):
    """
    Generates a Grid Plot for 'n_samples' random households.
    Optionally appends status to the report file.
    """
    if output_img_path is None:
        output_img_path = Path("Validation_Plot_Batch.png")

    msg_start = f"\n4. GENERATING VISUAL VERIFICATION PLOT ({n_samples} Households)..."
    print(msg_start)

    if report_path:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(msg_start + "\n")

    # 1. Filter for households with some activity (Density > 1)
    interesting_ids = df_full[df_full['occDensity'] > 1]['SIM_HH_ID'].unique()

    if len(interesting_ids) == 0:
        print("   ⚠️ No high-density households found. Sampling random ones.")
        interesting_ids = df_full['SIM_HH_ID'].unique()

    # 2. Random Sample
    actual_n = min(n_samples, len(interesting_ids))
    sample_ids = np.random.choice(interesting_ids, actual_n, replace=False)

    # 3. Setup Grid
    cols = 4
    rows = math.ceil(actual_n / cols)
    figsize_height = rows * 3

    fig, axes = plt.subplots(rows, cols, figsize=(15, figsize_height), sharex=False)
    axes = axes.flatten()

    # 4. Plot Loop
    for i, ax in enumerate(axes):
        if i < actual_n:
            hh_id = sample_ids[i]

            # Get Data (Priority: Weekday -> Weekend)
            mask = (df_full['SIM_HH_ID'] == hh_id) & (df_full['Day_Type'] == 'Weekday')
            df_hh = df_full[mask].copy()

            if df_hh.empty:
                mask = (df_full['SIM_HH_ID'] == hh_id) & (df_full['Day_Type'] == 'Weekend')
                df_hh = df_full[mask].copy()

            df_plot = df_hh[['Time_Slot', 'occPre', 'occDensity']].drop_duplicates()
            x = range(len(df_plot))

            if df_plot.empty:
                ax.text(0.5, 0.5, "No Data", ha='center')
                continue

            # Plot
            ax.fill_between(x, df_plot['occPre'], step="pre", color='green', alpha=0.3, label='Occupied')
            ax.set_ylim(0, 1.2)
            ax.set_yticks([])
            ax.set_ylabel("Presence", fontsize=8, color='green')

            ax2 = ax.twinx()
            ax2.plot(x, df_plot['occDensity'], color='blue', linewidth=1.5, label='Density')
            ax2.set_ylabel("Density", fontsize=8, color='blue')
            ax2.tick_params(axis='y', labelsize=8)

            ax.set_title(f"Household #{hh_id}", fontsize=10, fontweight='bold', pad=3)

            ticks = np.arange(0, 288, 48)
            labels = [df_plot['Time_Slot'].iloc[j] for j in ticks]
            ax.set_xticks(ticks)
            ax.set_xticklabels(labels, rotation=45, fontsize=8)
            ax.grid(True, alpha=0.2)

            if i == 0:
                lines, lbls = ax.get_legend_handles_labels()
                lines2, lbls2 = ax2.get_legend_handles_labels()
                ax.legend(lines + lines2, lbls + lbls2, loc='upper left', fontsize=8)
        else:
            ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_img_path)

    msg_end = f"   ✅ Batch Plot saved to: {output_img_path.name}"
    print(msg_end)

    if report_path:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(msg_end + "\n")
#OCC to BEM input ------------------------------------------------------------------------------------------------------
class BEMConverter:
    """
    Converts 5-minute ABM profiles into Hourly BEM Schedules.
    Output format: 60-minute resolution, fractional occupancy (0-1), metabolic rate (W).
    Includes Residential variables (DTYPE, BEDRM, etc.) for building matching.
    """

    def __init__(self, output_dir):
        self.output_dir = output_dir

        # 2024 Compendium of Physical Activities Mapping (Activity Code -> Watts)
        # Assumes 1 MET ~= 70 Watts (Avg adult 70kg)
        self.metabolic_map = {
            '1': 125,  # Work & Related (~1.8 MET - Standing/Office)
            '2': 175,  # Household Work (~2.5 MET - Cleaning/Cooking)
            '3': 190,  # Caregiving (~2.7 MET - Active child/elder care)
            '4': 195,  # Shopping (~2.8 MET - Walking with cart)
            '5': 70,  # Sleep (~1.0 MET - Sleeping/Lying quietly)
            '6': 105,  # Eating (~1.5 MET - Sitting eating)
            '7': 170,  # Personal Care (~2.4 MET - Dressing/Showering)
            '8': 110,  # Education (~1.6 MET - Sitting in class/Studying)
            '9': 90,  # Socializing (~1.3 MET - Sitting talking)
            '10': 85,  # Passive Leisure (~1.2 MET - TV/Reading + fidgeting)
            '11': 245,  # Active Leisure (~3.5 MET - Walking/Exercise)
            '12': 105,  # Volunteer (~1.5 MET - Light effort)
            '13': 140,  # Travel (~2.0 MET - Driving/Walking mix)
            '14': 135,  # Miscellaneous (~1.9 MET - Standing/Misc tasks)
            '0': 0  # Empty
        }

        # DTYPE Mapping (Code -> Description)
        self.dtype_map = {
            '1': "SingleD", # Detached
            '2': "SemiD",
            '3': "Attached",
            '4': "DuplexD",
            '5': "HighRise",
            '6': "MidRise",
            '7': "OtherA", # Attached
            '8': "Movable",
            # Fallbacks
            'Apartment': "Apt (Unspec.)",
            'Other dwelling': "Other"
        }

    def process_households(self, df_full):
        print(f"\n🚀 Starting BEM Conversion (Hourly Resampling)...")

        # 1. Prepare Time Index
        # We need a dummy date to enable resampling
        df_full['datetime'] = pd.to_datetime(df_full['Time_Slot'], format='%H:%M')

        # 2. Map Activities to Watts (Vectorized)
        print("   Mapping metabolic rates...")
        df_full['watts_5min'] = df_full['occActivity'].apply(self._calculate_watts)

        # 3. Group by Household & DayType
        groups = df_full.groupby(['SIM_HH_ID', 'Day_Type'])

        bem_schedules = []

        # List of residential variables to carry over
        target_res_cols = ['DTYPE', 'BEDRM', 'CONDO', 'ROOM', 'REPAIR']

        for (hh_id, day_type), group in tqdm(groups, desc="Generating Schedules"):
            # Get Static Attributes (First row of the group)
            hh_size = group['HHSIZE'].iloc[0]

            # Extract residential vars safely (handle if missing)
            res_data = {}
            for col in target_res_cols:
                val = group[col].iloc[0] if col in group.columns else "Unknown"

                # Apply DTYPE Mapping
                if col == 'DTYPE':
                    # Convert to string and strip decimals (e.g. 1.0 -> '1') for lookup
                    val_str = str(int(val)) if pd.notnull(val) and val != "Unknown" else str(val)
                    res_data[col] = self.dtype_map.get(val_str, val)  # Fallback to original if not found
                else:
                    res_data[col] = val

            # --- HOURLY RESAMPLING ---
            # Set index to datetime for resampling
            g_indexed = group.set_index('datetime')

            # Resample 5min -> 60min (Mean)
            hourly = g_indexed.resample('60min').agg({
                'occPre': 'mean',  # Fraction of hour home (0.0 - 1.0)
                'occDensity': 'mean',  # Avg social density
                'watts_5min': 'mean'  # Avg metabolic rate
            }).reset_index()

            # --- BEM FORMULAS ---

            # 1. Reconstruct People Count: (1 person + Social Density) * Presence Fraction
            estimated_count = hourly['occPre'] * (hourly['occDensity'] + 1)

            # 2. Normalize to Schedule (0-1) by dividing by HH Capacity
            occupancy_sched = (estimated_count / hh_size).clip(upper=1.0)

            # 3. Create Result DataFrame
            # Construct the dictionary with all columns
            data_dict = {
                'SIM_HH_ID': hh_id,
                'Day_Type': day_type,
                'Hour': hourly['datetime'].dt.hour,
                'HHSIZE': hh_size,
                # Unpack the residential variables here
                **res_data,
                'Occupancy_Schedule': occupancy_sched.round(3),  # 0 to 1
                'Metabolic_Rate': hourly['watts_5min'].round(1)  # Watts
            }

            hourly_df = pd.DataFrame(data_dict)
            bem_schedules.append(hourly_df)

        # Combine
        return pd.concat(bem_schedules, ignore_index=True)

    def _calculate_watts(self, act_str):
        """
        Parses activity string '1,5' -> maps to Watts -> returns average.
        """
        if act_str == "0": return 0

        codes = str(act_str).split(',')
        watts = [self.metabolic_map.get(c.strip(), 100) for c in codes]  # Default 100W if unknown
        return sum(watts) / len(watts)
def visualize_bem_distributions(df_bem, output_dir=None):
    """
    Generates two validation plot files:
    1. 'BEM_Schedules_2025_temporals.png':
       - Row 1: Population Distributions (Histograms)
       - Row 2: Population Averages (Line Plots)
       - Row 3: SAMPLE HOUSEHOLD SCHEDULE (Specific Weekday vs Weekend)
    2. 'BEM_Schedules_2025_non_temporals.png': Residential stats.
    """
    print(f"\n📊 GENERATING BEM DISTRIBUTION PLOTS...")

    if output_dir is None:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Define paths
    path_temporal = output_dir / "BEM_Schedules_2025_temporals.png"
    path_nontemporal = output_dir / "BEM_Schedules_2025_non_temporals.png"

    # Set style
    sns.set_theme(style="whitegrid")

    # =========================================================
    # 1. TEMPORAL PLOTS (3x2 Grid)
    # =========================================================
    # Increased figure height to accommodate the new 3rd row
    fig1, axes1 = plt.subplots(3, 2, figsize=(16, 15))

    # --- ROW 1: HISTOGRAMS ---
    # Top-Left: Occupancy Distribution
    sns.histplot(
        data=df_bem, x='Occupancy_Schedule', bins=20, kde=False,
        color='green', alpha=0.6, ax=axes1[0, 0]
    )
    axes1[0, 0].set_title("Population Distribution: Occupancy Fractions")
    axes1[0, 0].set_xlabel("Occupancy (0=Empty, 1=Full)")

    # Top-Right: Metabolic Distribution
    active_watts = df_bem[df_bem['Metabolic_Rate'] > 0]
    sns.histplot(
        data=active_watts, x='Metabolic_Rate', bins=30, kde=True,
        color='orange', alpha=0.6, ax=axes1[0, 1]
    )
    axes1[0, 1].set_title("Population Distribution: Metabolic Rates (Occupied)")
    axes1[0, 1].set_xlabel("Watts per Person")

    # --- ROW 2: AVERAGE PROFILES (RENAMED) ---
    # Mid-Left: Average Presence
    sns.lineplot(
        data=df_bem, x='Hour', y='Occupancy_Schedule', hue='Day_Type',
        estimator='mean', errorbar=('sd', 1),
        palette={'Weekday': 'green', 'Weekend': 'teal'}, ax=axes1[1, 0]
    )
    axes1[1, 0].set_title("Population Trend: Average Presence Schedule")
    axes1[1, 0].set_ylim(0, 1.05)
    axes1[1, 0].set_xticks(range(0, 25, 4))

    # Mid-Right: Average Metabolic
    sns.lineplot(
        data=active_watts, x='Hour', y='Metabolic_Rate', hue='Day_Type',
        estimator='mean', errorbar=None,
        palette={'Weekday': 'orange', 'Weekend': 'red'}, ax=axes1[1, 1]
    )
    axes1[1, 1].set_title("Population Trend: Average Metabolic Intensity (Heat Output)")
    axes1[1, 1].set_xticks(range(0, 25, 4))

    # --- ROW 3: SAMPLE HOUSEHOLD (NEW) ---
    # Pick a random household that has some activity
    # We group by ID and find max occupancy to avoid picking empty houses
    occupancy_check = df_bem.groupby('SIM_HH_ID')['Occupancy_Schedule'].max()
    valid_ids = occupancy_check[occupancy_check > 0].index

    if len(valid_ids) > 0:
        sample_id = np.random.choice(valid_ids)
        sample_data = df_bem[df_bem['SIM_HH_ID'] == sample_id]

        # Split into Weekday/Weekend
        wd_data = sample_data[sample_data['Day_Type'] == 'Weekday'].sort_values('Hour')
        we_data = sample_data[sample_data['Day_Type'] == 'Weekend'].sort_values('Hour')

        # Helper to plot dual axis
        def plot_dual_axis(ax, data, title):
            if data.empty: return
            x = data['Hour']

            # Primary Y: Occupancy (Green Area)
            ax.fill_between(x, data['Occupancy_Schedule'], color='green', alpha=0.3, label='Occupancy')
            ax.set_ylim(0, 1.1)
            ax.set_ylabel("Occupancy Fraction", color='green', fontsize=10)
            ax.tick_params(axis='y', labelcolor='green')

            # Secondary Y: Metabolic (Orange Line)
            ax2 = ax.twinx()
            ax2.plot(x, data['Metabolic_Rate'], color='darkorange', linewidth=2.5, label='Heat Gain')
            ax2.set_ylabel("Metabolic Rate (W)", color='darkorange', fontsize=10)
            ax2.tick_params(axis='y', labelcolor='darkorange')
            ax2.set_ylim(0, 250)  # Fixed scale for comparison

            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xticks(range(0, 25, 4))
            ax.set_xlabel("Hour of Day")

            # Combined Legend
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')

        # Bottom-Left: Sample Weekday
        plot_dual_axis(axes1[2, 0], wd_data, f"Sample Household #{sample_id}: Weekday Schedule")

        # Bottom-Right: Sample Weekend
        plot_dual_axis(axes1[2, 1], we_data, f"Sample Household #{sample_id}: Weekend Schedule")

    else:
        axes1[2, 0].text(0.5, 0.5, "No Valid Samples Found", ha='center')
        axes1[2, 1].axis('off')

    plt.tight_layout()
    fig1.savefig(path_temporal)
    plt.close(fig1)
    print(f"   ✅ Temporal Plot saved: {path_temporal.name}")

    # =========================================================
    # 2. NON-TEMPORAL PLOTS (Residential Variables)
    # =========================================================
    cols_static = [c for c in ['SIM_HH_ID', 'DTYPE', 'BEDRM', 'ROOM'] if c in df_bem.columns]
    df_static = df_bem[cols_static].drop_duplicates(subset=['SIM_HH_ID'])

    if len(df_static) > 0 and len(cols_static) > 1:
        fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))

        # Plot DTYPE
        if 'DTYPE' in df_static.columns:
            sns.countplot(
                data=df_static, x='DTYPE', hue='DTYPE',
                palette='viridis', ax=axes2[0], legend=False
            )
            axes2[0].set_title("Distribution of Dwelling Types")
            axes2[0].tick_params(axis='x', rotation=15, labelsize=8)  # Smaller labels
            axes2[0].set_ylabel("Count of Households")
        else:
            axes2[0].text(0.5, 0.5, "DTYPE missing", ha='center')

        # Plot BEDRM
        if 'BEDRM' in df_static.columns:
            sns.countplot(
                data=df_static, x='BEDRM', hue='BEDRM',
                palette='magma', ax=axes2[1], legend=False
            )
            axes2[1].set_title("Distribution of Bedroom Counts")
            axes2[1].set_ylabel("Count of Households")
        else:
            axes2[1].text(0.5, 0.5, "BEDRM missing", ha='center')

        # Plot ROOM
        if 'ROOM' in df_static.columns:
            sns.histplot(
                data=df_static, x='ROOM', discrete=True,
                color='purple', alpha=0.7, ax=axes2[2]
            )
            axes2[2].set_title("Distribution of Total Room Counts")
            axes2[2].set_ylabel("Count of Households")
        else:
            axes2[2].text(0.5, 0.5, "ROOM missing", ha='center')

        plt.tight_layout()
        fig2.savefig(path_nontemporal)
        plt.close(fig2)
        print(f"   ✅ Non-Temporal Plot saved: {path_nontemporal.name}")
    else:
        print("   ⚠️ Skipped Non-Temporal plots (Residential columns missing or empty data).")
if __name__ == '__main__':
    #DIRECTORIES -------------------------------------------------------------------------------------------------------
    # BASE_DIR = pathlib.Path("C:/Users/o_iseri/Desktop/2ndJournal")
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal")

    DATA_DIR = BASE_DIR / "DataSources_CENSUS"
    OUTPUT_DIR = BASE_DIR / "Outputs_CENSUS"
    OUTPUT_DIR_ALIGNED = BASE_DIR / "Outputs_Aligned"
    OUTPUT_DIR_ALIGNED.mkdir(parents=True, exist_ok=True)

    # --- NEW: Define a directory to save your trained models ---
    MODEL_DIR = BASE_DIR / "saved_models_cvae"
    MODEL_DIR.mkdir(parents=True, exist_ok=True)  # This creates the folder

    # --- Raw Files ---
    cen06_filtered = OUTPUT_DIR / "cen06_filtered.csv"
    cen11_filtered = OUTPUT_DIR / "cen11_filtered.csv"

    # --- Edited Files ---
    cen06_filtered2 = OUTPUT_DIR / "cen06_filtered2.csv"
    cen11_filtered2 = OUTPUT_DIR / "cen11_filtered2.csv"
    cen16_filtered2 = OUTPUT_DIR / "cen16_filtered2.csv"
    cen21_filtered2 = OUTPUT_DIR / "cen21_filtered2.csv"

    # --- Forecasted Files ---
    cen25 = OUTPUT_DIR / "forecasted_population_2025.csv"
    cen30 = OUTPUT_DIR / "forecasted_population_2030.csv"

    # --- Aligned Files ---
    aligned_CENSUS = OUTPUT_DIR_ALIGNED / "Aligned_Census_2025.csv"
    aligned_GSS = OUTPUT_DIR_ALIGNED / "Aligned_GSS_2022.csv"

    # VALIDATION
    VALIDATION_FORECAST_DIR = OUTPUT_DIR / "Validation_Forecasting_VisualbyColumn"
    VALIDATION_FORECASTVIS_DIR = OUTPUT_DIR / "Validation_Forecasting_Visual"
    VALIDATION_PR_MATCH_DIR = OUTPUT_DIR / "Validation_ProfileMatcher"
    VALIDATION_HH_AGG_DIR = OUTPUT_DIR / "Validation_HHaggregation"

    #TRAINING ----------------------------------------------------------------------------------------------------------
    """
    file_paths = {2006: cen06_filtered2, 2011: cen11_filtered2, 2016: cen16_filtered2, 2021: cen21_filtered2}
    processed_data, demo_cols, bldg_cols, data_scalers = prepare_data_for_generative_model(file_paths,sample_frac=1)
    encoder, decoder, cvae_model, training_history = train_cvae(df_processed=processed_data, demo_cols=demo_cols, bldg_cols=bldg_cols,
                                                                continuous_cols= ['EMPIN', 'TOTINC', 'INCTAX', 'VALUE'],
                                                                latent_dim=128,  epochs=100, batch_size=4096)
  
    # --- 3. THIS IS THE NEW PART: Save your models ---
    print("--- Training complete. Saving models to disk... ---")

    # Save the components to your new MODEL_DIR
    encoder.save(MODEL_DIR / 'cvae_encoder.keras')
    decoder.save(MODEL_DIR / 'cvae_decoder.keras')

    print("--- Models successfully saved! ---")

    print("\n--- C-VAE Training Complete ---")
    plot_training_history(training_history)

    check_reconstruction_quality(encoder, decoder, processed_data, demo_cols, bldg_cols)

    # --- B: Load Pre-Trained Models (Replaces training) ---
    print(f"--- Loading pre-trained models from: {MODEL_DIR} ---")
    """
    #TESTING -----------------------------------------------------------------------------------------------------------
    """
    file_paths = {2006: cen06_filtered2, 2011: cen11_filtered2, 2016: cen16_filtered2, 2021: cen21_filtered2}
    processed_data, demo_cols, bldg_cols, data_scalers = prepare_data_for_generative_model(file_paths,sample_frac=1)
    encoder = keras.models.load_model(MODEL_DIR / 'cvae_encoder.keras', custom_objects={'Sampling': Sampling})
    decoder = keras.models.load_model(MODEL_DIR / 'cvae_decoder.keras')
    print("--- Models loaded successfully! ---")
    validate_vae_reconstruction(encoder, decoder, processed_data, demo_cols, bldg_cols, continuous_cols=['EMPIN', 'TOTINC', 'INCTAX', 'VALUE'], n_samples=10, output_dir=OUTPUT_DIR)
    """
    #FORECASTING -------------------------------------------------------------------------------------------------------
    """"""
    file_paths = {2006: cen06_filtered2, 2011: cen11_filtered2, 2016: cen16_filtered2, 2021: cen21_filtered2}
    processed_data, demo_cols, bldg_cols, data_scalers = prepare_data_for_generative_model(file_paths,sample_frac=1)
    encoder = keras.models.load_model(MODEL_DIR / 'cvae_encoder.keras', custom_objects={'Sampling': Sampling})
    decoder = keras.models.load_model(MODEL_DIR / 'cvae_decoder.keras')
    # 3. Train Temporal Drift
    print("\n=== Step 3: Modeling Temporal Drift ===")
    temporal_model, last_variance = train_temporal_model(encoder, processed_data, demo_cols, bldg_cols)

    # 4. Generate Forecasts
    TARGET_YEARS = [2025, 2030]
    N_SAMPLES = 1000
    OUTPUT_DIR = Path(OUTPUT_DIR / "Generated") # Example path
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for year in TARGET_YEARS:
        print(f"\n=== Step 4: Forecasting for {year} ===")
        # Generate
        gen_raw, bldg_raw = generate_future_population(decoder, temporal_model, last_variance, processed_data, bldg_cols, target_year=year, n_samples=N_SAMPLES)
        # Post-Process
        df_forecast = post_process_generated_data(gen_raw, demo_cols, bldg_raw, bldg_cols, data_scalers)
        # Add Year
        df_forecast['YEAR'] = year
        # Save
        save_path = OUTPUT_DIR / f"forecasted_population_{year}.csv"
        df_forecast.to_csv(save_path, index=False)
        print(f"✅ Saved {year} forecast to: {save_path}")
        print(df_forecast.head())

    #VALIDATION OF FORECASTING_VISUAL ----------------------------------------------------------------------------------
    """"""
    file_paths = {2006: cen06_filtered2, 2011: cen11_filtered2, 2016: cen16_filtered2, 2021: cen21_filtered2}
    processed_data, demo_cols, bldg_cols, data_scalers = prepare_data_for_generative_model(file_paths, sample_frac=1)
    encoder = keras.models.load_model(MODEL_DIR / 'cvae_encoder.keras', custom_objects={'Sampling': Sampling})
    decoder = keras.models.load_model(MODEL_DIR / 'cvae_decoder.keras')
    # Run Validation
    validate_forecast_trajectory(encoder, processed_data, demo_cols, bldg_cols, VALIDATION_FORECASTVIS_DIR)
    validate_forecast_distributions(encoder=encoder, decoder=decoder, df_processed=processed_data, demo_cols=demo_cols,
                                    bldg_cols=bldg_cols, scalers=data_scalers, output_dir=VALIDATION_FORECAST_DIR)
    #ASSEMBLE HOUSEHOLD ------------------------------------------------------------------------------------------------
    """
    # --- Run Assembly for 2025 ---
    df_linked_2025 = assemble_households(cen25, target_year=2025, output_dir=OUTPUT_DIR)
    """
    #PROFILE MATCHER ---------------------------------------------------------------------------------------------------
    """
    IO_DIR = Path(OUTPUT_DIR)
    print("1. Loading Data...")
    df_census = pd.read_csv(aligned_CENSUS)
    df_gss = pd.read_csv(aligned_GSS, low_memory=False)

    # 2. Run Matching
    matcher = MatchProfiler(df_census, df_gss, dday_col="DDAY", id_col="occID")
    df_matched = matcher.run_matching()

    # 3. Save Matched Keys (Lightweight)
    df_matched.to_csv(OUTPUT_DIR_ALIGNED / "Matched_Population_Keys.csv", index=False)
    print(f"   Saved Keys: Matched_Population_Keys.csv")

    # 4. Expand & Save Full Schedules (Heavyweight)
    expander = ScheduleExpander(df_gss, id_col="occID")
    verify_sample(df_matched, expander)

    # Define output path for the massive file
    expanded_path = IO_DIR / "Full_Expanded_Schedules.csv"
    generate_full_expansion(df_matched, expander, expanded_path)

    print("\n✅ Workflow Complete.")
    """
    #VALIDATION: PROFILE MATCHER ---------------------------------------------------------------------------------------
    """
    IO_DIR_ALIGNED = Path(OUTPUT_DIR_ALIGNED)
    IO_DIR_VALID = Path(VALIDATION_PR_MATCH_DIR)
    df_matched = pd.read_csv(IO_DIR_ALIGNED / "Matched_Population_Keys.csv")
    df_gss = pd.read_csv(IO_DIR_ALIGNED / "Aligned_GSS_2022.csv", low_memory=False)

    # Re-initialize Expander
    # We need to import or paste the ScheduleExpander class here first!
    expander = ScheduleExpander(df_gss, id_col="occID")

    # Run Validation
    validate_matching_quality(df_matched, expander, save_path=(IO_DIR_VALID / "Validation_ProfileMatcher_2025.txt"))
"""
    #PROFILE MATCHER: POST-PROCESSING ----------------------------------------------------------------------------------
    """
    import pandas as pd
    from pathlib import Path
    # =============================================================================
    # CONFIGURATION
    # =============================================================================
    IO_DIR = Path(OUTPUT_DIR)
    # 1. The "Teacher": Historic Data (Must have detailed DTYPE 1-8)
    # Replace this with the actual path to your 2006 or 2011 raw data
    HISTORIC_DATA_PATHS = [cen06_filtered, cen11_filtered]
    # 2. The "Student": Step 2 Output (Has coarse DTYPE 1-3)
    INPUT_FORECAST_PATH = IO_DIR / "Full_Expanded_Schedules.csv"
    # 3. The Result: Input for Step 3
    OUTPUT_REFINED_PATH = IO_DIR / "Full_Expanded_Schedules_Refined.csv"
    VALIDATION_DIR = IO_DIR / "Validation_ProfileMatcher_PostProcessing"
    # =============================================================================
    # EXECUTION
    # =============================================================================
    if __name__ == "__main__":
        print(f"\n🚀 Starting Step 2b: DTYPE Refinement (Multi-Year Training)...")

        # 1. Validation Checks
        if not INPUT_FORECAST_PATH.exists():
            print(f"❌ Error: Forecast file not found at: {INPUT_FORECAST_PATH}")
            print("   Please run Step 2 (Expansion) first.")
            exit()

        # 2. Load and Merge Historic Data
        print("1. Loading Datasets...")
        historic_dfs = []

        for path in HISTORIC_DATA_PATHS:
            p = Path(path)
            if p.exists():
                print(f"   - Loading: {p.name} ...")
                df = pd.read_csv(p, low_memory=False)
                historic_dfs.append(df)
            else:
                print(f"   ⚠️ Warning: File not found: {path}")

        if not historic_dfs:
            print("❌ Error: No valid historic data found.")
            exit()

        # Concatenate all historic years into one big training set
        df_hist_combined = pd.concat(historic_dfs, ignore_index=True)
        print(f"   -> Combined Training Set: {len(df_hist_combined):,} rows")

        # Load Forecast
        df_forecast = pd.read_csv(INPUT_FORECAST_PATH, low_memory=False)
        print(f"   Forecast Data: {len(df_forecast):,} rows")

        # 3. Initialize & Train
        # The Refiner will now learn from the combined patterns of 06 and 11
        refiner = DTypeRefiner(output_dir=IO_DIR)
        refiner.train_models(df_hist_combined)

        # 4. Apply Refinement
        df_refined = refiner.apply_refinement(df_forecast)

        # 5. Save
        print(f"2. Saving Refined Data to: {OUTPUT_REFINED_PATH.name}...")
        df_refined.to_csv(OUTPUT_REFINED_PATH, index=False)

        # 6. Verification
        print("\n--- Verification: New DTYPE Distribution ---")
        dist = df_refined['DTYPE'].value_counts().sort_index()
        for code, count in dist.items():
            label = refiner.dtype_labels.get(code, "Unknown")
            print(f"   Code {code} ({label}): {count:,} rows")

        print("\n✅ Step 2b Complete.")

    validate_refinement_model(HISTORIC_DATA_PATHS, OUTPUT_REFINED_PATH, VALIDATION_DIR)
    """
    #HOUSEHOLD AGGREGATION ---------------------------------------------------------------------------------------------
    """
    IO_DIR = Path(OUTPUT_DIR)
    expanded_file = IO_DIR / "Full_Expanded_Schedules_Refined.csv"
    output_full = IO_DIR / "Full_data.csv"

    # 2. Load Data
    print("1. Loading Expanded Schedules...")
    if not expanded_file.exists():
        print(f"❌ Error: {expanded_file} not found. Run Step 2 first.")
    else:
        df_expanded = pd.read_csv(expanded_file, low_memory=False)

        # 3. Initialize Aggregator
        aggregator = HouseholdAggregator(resolution_min=5)

        # 4. Run Process
        print("2. Starting Process (Padding + Aggregation)...")
        # Now returns the full dataset with all original columns integrated
        df_final = aggregator.process_all(df_expanded)

        # 5. Save
        print(f"3. Saving Full Integrated Data to: {output_full.name}...")
        df_final.to_csv(output_full, index=False)

        # 6. Verification
        print("\n--- Verification: Columns in Output ---")
        print(f"Total Columns: {len(df_final.columns)}")
        print(f"Sample Columns: {list(df_final.columns[:10])} ... {list(df_final.columns[-3:])}")

        print("\n✅ Step 3 Complete. Full Integrated Data generated.")
    """
    #VALIDATION: HOUSEHOLD AGGREGATION ---------------------------------------------------------------------------------
    """
    IO_DIR = Path(OUTPUT_DIR)
    IO_VALID_HHagg_DIR = Path(VALIDATION_HH_AGG_DIR)
    full_data_path = IO_DIR / "Full_data.csv"
    plot_path = IO_VALID_HHagg_DIR / "Validation_Plot_Batch.png"
    report_path = IO_VALID_HHagg_DIR / "Validation_Report_HH.txt"  # New Output File

    if not full_data_path.exists():
        print("❌ Error: Full_data.csv not found.")
    else:
        print("Loading data for validation...")
        df_full = pd.read_csv(full_data_path, low_memory=False)

        # Run Checks (Writes 1-3 to file)
        validate_household_aggregation(df_full, report_path=report_path)

        # Run Visuals (Appends 4 to file)
        visualize_multiple_households(df_full, n_samples=16, output_img_path=plot_path, report_path=report_path)

        print(f"\n✅ Full Validation Report saved to: {report_path.name}")
    """
    #OCC to BEM input --------------------------------------------------------------------------------------------------
    """ 
    IO_DIR = Path(OUTPUT_DIR)
    full_data_path = IO_DIR / "Full_data.csv"
    output_path = IO_DIR / "BEM_Schedules_2025.csv"
    output_path_vis = IO_DIR

    if not full_data_path.exists():
        print("❌ Error: Full_data.csv not found.")
    else:
        print("1. Loading Household Data...")
        df_full = pd.read_csv(full_data_path, low_memory=False)

        # Initialize Converter
        converter = BEMConverter(output_dir=IO_DIR)

        # Run
        df_bem = converter.process_households(df_full)

        # Save
        # float_format='%.3f' ensures 0.333 is written as "0.333" not ".333"
        print(f"2. Saving Hourly BEM Input to: {output_path.name}")
        df_bem.to_csv(output_path, index=False, float_format='%.3f')

        # Verify
        print("\n--- Verification: Sample Household ---")

        # Force pandas to show 3 decimal places with leading zero
        pd.options.display.float_format = '{:.3f}'.format

        # Show relevant columns including new residential ones
        cols_to_show = ['SIM_HH_ID', 'Hour', 'DTYPE', 'BEDRM',"ROOM", 'Occupancy_Schedule', 'Metabolic_Rate']
        # Filter cols that actually exist in output
        valid_cols = [c for c in cols_to_show if c in df_bem.columns]

        print(df_bem[valid_cols].head(12).to_string(index=False))

        print("\n✅ Step 4 Complete. Ready for EnergyPlus/Honeybee.")
        visualize_bem_distributions(df_bem, output_dir=output_path_vis)
        """

