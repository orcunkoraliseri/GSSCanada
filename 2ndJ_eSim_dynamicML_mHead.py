from typing import List, Dict, Tuple
import tensorflow as tf
from tensorflow import keras
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import pathlib
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
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
def train_temporal_model(encoder, df_processed, demo_cols, bldg_cols):
    print("--- Starting Step 3: Temporal Modeling ---")

    # Find all 'YEAR_...' columns
    year_cols = sorted([col for col in demo_cols if col.startswith('YEAR_')])
    years = [int(col.split('_')[1]) for col in year_cols]

    X_temporal = []
    y_temporal = []
    last_avg_log_var = None

    print(f"Extracting latent archetypes for years: {years}")
    for year, col_name in zip(years, year_cols):
        year_df = df_processed[df_processed[col_name] == 1]
        if len(year_df) == 0: continue

        demo_data = year_df[demo_cols].values.astype(np.float32)
        bldg_data = year_df[bldg_cols].values.astype(np.float32)

        # Predict latent space
        z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data], verbose=0)

        avg_z_mean = np.mean(z_mean, axis=0)
        X_temporal.append([year])
        y_temporal.append(avg_z_mean)
        last_avg_log_var = np.mean(z_log_var, axis=0)

    print("--- Training LinearRegression on temporal drift... ---")
    temporal_model = LinearRegression()
    temporal_model.fit(X_temporal, y_temporal)

    return temporal_model, last_avg_log_var
# --- 4. Generation Function (Updated for Multi-Head) ---
def generate_future_population(decoder, temporal_model, last_avg_log_var, df_processed, bldg_cols, target_year, n_samples):
    """
    Generates a new synthetic population for a target future year.
    Handles Multi-Head Decoder output.
    """
    print(f"--- Starting Step 4: Generating Population for {target_year} ---")

    # 1. Predict the future "archetype" (mean)
    predicted_z_mean = temporal_model.predict([[target_year]])

    # 2. Get realistic building conditions (from 2021)
    year_2021_col = [col for col in df_processed.columns if col.startswith('YEAR_')][-1]
    bldg_conditions_2021 = df_processed[df_processed[year_2021_col] == 1][bldg_cols]

    bldg_future_samples = bldg_conditions_2021.sample(
        n_samples,
        replace=True
    ).values.astype(np.float32)

    # 3. Generate new latent vectors (z)
    latent_dim = len(predicted_z_mean[0])
    z_std_dev = np.exp(0.5 * last_avg_log_var)

    z_new = np.random.normal(
        loc=predicted_z_mean,
        scale=z_std_dev,
        size=(n_samples, latent_dim)
    )

    # 4. Use the Decoder
    print(f"   Using decoder to generate {n_samples} new demographic profiles...")
    generated_list = decoder.predict([z_new, bldg_future_samples])

    # --- FIX: Concatenate Multi-Head Output ---
    # The decoder returns a list of arrays. We merge them into one big matrix.
    generated_raw_matrix = np.concatenate(generated_list, axis=1)
    # --- END FIX ---

    print("--- Generation Complete ---")
    return generated_raw_matrix, bldg_future_samples
# --- 5. Post-Processing Function ---
def post_process_generated_data(generated_raw_data, demo_cols, generated_bldg_data, bldg_cols, scalers):
    """
    Converts the raw generated data (probabilities) back into a
    human-readable, decoded DataFrame.
    """
    print("--- Starting Post-Processing ---")

    df_gen_demo = pd.DataFrame(generated_raw_data, columns=demo_cols)
    df_gen_bldg = pd.DataFrame(generated_bldg_data, columns=bldg_cols)
    df_final = pd.DataFrame()

    # 1. Inverse-scale the continuous columns
    for col_name, scaler in scalers.items():
        if col_name in df_gen_demo.columns:
            # Reshape to (N, 1) for the scaler
            col_data = df_gen_demo[col_name].values.reshape(-1, 1)

            # --- FIX IS HERE ---
            # Inverse transform returns (N, 1), but pandas needs (N,).
            # We use .flatten() to convert it to a 1D array.
            df_final[col_name] = scaler.inverse_transform(col_data).flatten()
            # --- END FIX ---

    # 2. Decode the One-Hot Encoded demographic columns
    all_prefixes = set()
    for col in demo_cols:
        if '_' in col and col not in scalers:
            all_prefixes.add(col.rsplit('_', 1)[0])

    for prefix in all_prefixes:
        cat_cols = [col for col in demo_cols if col.startswith(f"{prefix}_")]
        if cat_cols:
            predicted_col = df_gen_demo[cat_cols].idxmax(axis=1)
            df_final[prefix] = predicted_col.str.replace(f"{prefix}_", "")

    # 3. Decode the One-Hot Encoded building columns
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
#VALIDATION OF FORECASTING ---------------------------------------------------------------------------------------------
def generate_validation_report(encoder, decoder, df_processed, demo_cols, bldg_cols, scalers,output_folder=None):
    """
    Performs hindcasting for 2021 (training drift on 06-16)
    and generates comparison plots for EVERY column.
    """
    save_dir = pathlib.Path(output_folder)
    save_dir.mkdir(parents=True, exist_ok=True)
    print(f"--- Starting Comprehensive Validation (Saving to {save_dir}) ---")

    # 1. Train Temporal Model on 2006-2016 ONLY
    print("   Training Temporal Model on 2006, 2011, 2016...")
    years_train = [2006, 2011, 2016]
    target_year = 2021

    X_temporal = []
    y_temporal = []
    last_avg_log_var = None

    for year in years_train:
        col_name = f"YEAR_{year}"
        # Handle year columns
        if col_name not in df_processed.columns:
            print(f"Skipping {year} (Column not found)")
            continue

        year_df = df_processed[df_processed[col_name] == 1]
        demo_data = year_df[demo_cols].values.astype(np.float32)
        bldg_data = year_df[bldg_cols].values.astype(np.float32)

        z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data], verbose=0)

        X_temporal.append([year])
        y_temporal.append(np.mean(z_mean, axis=0))
        if year == 2016: last_avg_log_var = np.mean(z_log_var, axis=0)

    temporal_model = LinearRegression()
    temporal_model.fit(X_temporal, y_temporal)

    # 2. Generate Synthetic 2021
    print("   Generating Synthetic 2021 Population...")
    real_2021_df = df_processed[df_processed[f"YEAR_{target_year}"] == 1]
    bldg_conditions = real_2021_df[bldg_cols].values.astype(np.float32)

    pred_z_mean = temporal_model.predict([[target_year]])
    latent_dim = len(pred_z_mean[0])
    z_std_dev = np.exp(0.5 * last_avg_log_var)

    # Match size of real data for fair comparison
    n_samples = len(real_2021_df)
    z_new = np.random.normal(loc=pred_z_mean, scale=z_std_dev, size=(n_samples, latent_dim))

    gen_list = decoder.predict([z_new, bldg_conditions], verbose=0)
    gen_matrix = np.concatenate(gen_list, axis=1)

    # 3. Create DataFrames for Comparison
    df_real_decoded = pd.DataFrame()
    df_gen_decoded = pd.DataFrame()

    # Helper to decode continuous
    print("   Decoding and Plotting...")

    # --- A) CONTINUOUS COLUMNS ---
    for col_name in scalers.keys():
        if col_name in demo_cols:
            idx = demo_cols.index(col_name)

            # Inverse Scale Real
            real_val = real_2021_df[col_name].values.reshape(-1, 1)
            real_val = scalers[col_name].inverse_transform(real_val).flatten()

            # Inverse Scale Gen
            gen_val = gen_matrix[:, idx].reshape(-1, 1)
            gen_val = scalers[col_name].inverse_transform(gen_val).flatten()

            # Plot
            plt.figure(figsize=(10, 6))
            sns.kdeplot(real_val, label='Real 2021', fill=True, color='skyblue')
            sns.kdeplot(gen_val, label='Forecast 2021', fill=True, color='orange')
            plt.title(f"Validation: {col_name}")
            plt.legend()
            plt.savefig(save_dir / f"Continuous_{col_name}.png")
            plt.close()

    # --- B) CATEGORICAL COLUMNS ---
    # Find prefixes
    all_prefixes = set()
    for col in demo_cols:
        if '_' in col and col not in scalers:
            all_prefixes.add(col.rsplit('_', 1)[0])

    for prefix in sorted(list(all_prefixes)):
        if prefix == 'YEAR': continue  # Skip Year

        # Get columns for this feature
        cat_cols = [c for c in demo_cols if c.startswith(f"{prefix}_")]
        indices = [demo_cols.index(c) for c in cat_cols]

        # 1. Calculate Distribution for Real Data
        # (Sum the one-hot values)
        real_counts = real_2021_df[cat_cols].sum().values
        real_dist = real_counts / real_counts.sum()

        # 2. Calculate Distribution for Generated Data
        # (Sum the probabilities)
        gen_probs = gen_matrix[:, indices]
        gen_dist = gen_probs.sum(axis=0) / gen_probs.sum()

        # 3. Plot Side-by-Side Bar Chart
        labels = [c.replace(f"{prefix}_", "") for c in cat_cols]
        x = np.arange(len(labels))
        width = 0.35

        plt.figure(figsize=(12, 6))
        plt.bar(x - width / 2, real_dist, width, label='Real 2021', color='skyblue')
        plt.bar(x + width / 2, gen_dist, width, label='Forecast 2021', color='orange')

        plt.xticks(x, labels, rotation=45)
        plt.title(f"Validation: {prefix}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_dir / f"Categorical_{prefix}.png")
        plt.close()

    print(f"--- Validation Complete. Check folder: {save_dir} ---")
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

    save_path = OUTPUT_DIR / "Latent_Trajectory_Plot.png"
    plt.savefig(save_path)
    print(f"   Plot saved to {save_path}")
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
def check_reconstruction_quality_expanded(encoder, decoder, df_processed, demo_cols, bldg_cols, continuous_cols, output_dir, n_samples=5):
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
    output_path = pathlib.Path(output_dir) / "reconstruction_check_results.csv"
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
class MatchProfiler:
    """
    Phase 2 & 3: Assigns GSS Schedule IDs to Census Agents.
    """

    def __init__(self, df_census, df_gss, dday_col="DDAY", id_col="occID", cols_match_t1=None):
        print(f"\n{'=' * 60}")
        print(f"⚙️  INITIALIZING PHASE 2: MATCH PROFILER")
        print(f"{'=' * 60}")

        self.df_census = df_census.copy()
        self.id_col = id_col
        self.dday_col = dday_col

        # Define Tiers
        if cols_match_t1 is None:
            self.cols_t1 = ["HHSIZE", "HRSWRK", "AGEGRP", "MARSTH", "SEX", "KOL", "NOCS", "PR", "COW", "MODE"]
        else:
            self.cols_t1 = cols_match_t1

        self.cols_t2 = ["HHSIZE", "HRSWRK", "AGEGRP", "SEX", "COW"]
        self.cols_t3 = ["HHSIZE", "HRSWRK", "AGEGRP"]
        self.cols_t4 = ["HHSIZE"]

        # Split & Flatten GSS to create "Catalogs"
        print(f"   Splitting GSS by Day Type ({dday_col})...")
        catalog_cols = list(set([self.id_col] + self.cols_t1 + ["HHSIZE"]))

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
        # Tier 1
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t1: mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "1_Perfect"

        # Tier 2
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t2: mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "2_Drivers"

        # Tier 3
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t3: mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "3_Constraints"

        # Tier 4
        mask = (catalog["HHSIZE"] == agent["HHSIZE"])
        matches = catalog[mask]
        if not matches.empty: return matches.sample(1)[self.id_col].values[0], "4_FailSafe"

        return catalog.sample(1)[self.id_col].values[0], "5_Random"
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
# --- Helper Function for Verification ---
def verify_sample(df_matched, expander, n=3):
    """
    Verifies that we can successfully retrieve episode rows for the matched agents.
    """
    print(f"\n🔎 VERIFYING EXPANSION (Sample of {n})")

    for i, agent in df_matched.head(n).iterrows():
        # 1. Extract the Assigned IDs from the dataframe row
        id_wd = agent['MATCH_ID_WD']
        id_we = agent['MATCH_ID_WE']

        # 2. Use the new 'get_episodes' method with the ID directly
        ep_wd = expander.get_episodes(id_wd)
        ep_we = expander.get_episodes(id_we)

        # 3. Safely count rows (handle None if ID wasn't found)
        count_wd = len(ep_wd) if ep_wd is not None else 0
        count_we = len(ep_we) if ep_we is not None else 0

        print(f"   User {i}: WD={count_wd} rows | WE={count_we} rows")
# Function to Save the Massive File
def generate_full_expansion(df_matched, expander, output_path):
    print(f"\n💾 Expanding Schedules for {len(df_matched)} agents...")
    all_episodes = []

    for _, agent in tqdm(df_matched.iterrows(), total=len(df_matched), desc="Expanding"):
        # Expand Weekday
        ep_wd = expander.get_episodes(agent['MATCH_ID_WD'])
        if ep_wd is not None:
            ep_wd['SIM_HH_ID'] = agent['SIM_HH_ID']  # Link to House
            ep_wd['Day_Type'] = 'Weekday'
            all_episodes.append(ep_wd)

        # Expand Weekend
        ep_we = expander.get_episodes(agent['MATCH_ID_WE'])
        if ep_we is not None:
            ep_we['SIM_HH_ID'] = agent['SIM_HH_ID']
            ep_we['Day_Type'] = 'Weekend'
            all_episodes.append(ep_we)

    if all_episodes:
        full_df = pd.concat(all_episodes)

        # --- NEW: SORTING LOGIC ---
        # Sorts by Household first, then Day Type, then Person ID
        print(f"   Sorting expanded data by SIM_HH_ID...")
        full_df = full_df.sort_values(by=['SIM_HH_ID', 'Day_Type', 'occID'])

        full_df.to_csv(output_path)  # Index is PUMFID/occID
        print(f"✅ Saved Expanded File: {len(full_df):,} rows to {output_path.name}")
#VALIDATION: PROFILE MATCHER ---------------------------------------------------------------------------------------
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
    VALIDATION_DIR = OUTPUT_DIR / "Validation_Report_2021"

    #DATA LOADING ------------------------------------------------------------------------------------------------------
    """
    file_paths = {2006: cen06_filtered2, 2011: cen11_filtered2, 2016: cen16_filtered2, 2021: cen21_filtered2}
    processed_data, demo_cols, bldg_cols, data_scalers = prepare_data_for_generative_model(file_paths,sample_frac=1)
    """
    #TRAINING ----------------------------------------------------------------------------------------------------------
    """
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
    encoder = keras.models.load_model(MODEL_DIR / 'cvae_encoder.keras', custom_objects={'Sampling': Sampling})
    decoder = keras.models.load_model(MODEL_DIR / 'cvae_decoder.keras')
    print("--- Models loaded successfully! ---")
    check_reconstruction_quality_expanded(encoder, decoder, processed_data, demo_cols, bldg_cols, continuous_cols=['EMPIN', 'TOTINC', 'INCTAX', 'VALUE'], n_samples=10, output_dir=OUTPUT_DIR)
    """
    #FORECASTING -------------------------------------------------------------------------------------------------------
    """
    # 3. Train Temporal Drift
    print("\n=== Step 3: Modeling Temporal Drift ===")
    temporal_model, last_variance = train_temporal_model(encoder,processed_data, demo_cols, bldg_cols)
    
    # --- NEW: Plot the Trajectory ---
    plot_latent_trajectory(encoder, temporal_model, processed_data, demo_cols, bldg_cols)

    # 4. Generate Forecasts
    TARGET_YEARS = [2025, 2030]
    N_SAMPLES = 10000

    for year in TARGET_YEARS:
        print(f"\n=== Step 4: Forecasting for {year} ===")
        # Generate
        gen_raw, bldg_raw = generate_future_population(decoder, temporal_model, last_variance, processed_data, bldg_cols, target_year=year, n_samples=N_SAMPLES)
        # Post-Process
        df_forecast = post_process_generated_data(gen_raw, demo_cols, bldg_raw, bldg_cols, data_scalers )
        # Add Year Column
        df_forecast['YEAR'] = year
        # Save
        save_path = OUTPUT_DIR / f"forecasted_population_{year}.csv"
        df_forecast.to_csv(save_path, index=False)
        print(f"✅ Saved {year} forecast to: {save_path}")
        print(df_forecast.head())

    #VALIDATION OF FORECASTING -----------------------------------------------------------------------------------------
    # --- Execute (Assuming models/data loaded) ---
    generate_validation_report(encoder, decoder, processed_data, demo_cols, bldg_cols, data_scalers, output_folder=VALIDATION_DIR)
    """
    #ASSEMBLE HOUSEHOLD ------------------------------------------------------------------------------------------------
    """
    # --- Run Assembly for 2025 ---
    df_linked_2025 = assemble_households(cen25, target_year=2025, output_dir=OUTPUT_DIR)
    """
    #PROFILE MATCHER ---------------------------------------------------------------------------------------------------
    """
    # 1. Paths & Load
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
    expanded_path = OUTPUT_DIR_ALIGNED / "Full_Expanded_Schedules.csv"
    generate_full_expansion(df_matched, expander, expanded_path)

    print("\n✅ Workflow Complete.")
    """
    #VALIDATION: PROFILE MATCHER ---------------------------------------------------------------------------------------
    """
    IO_DIR = Path(OUTPUT_DIR_ALIGNED)
    df_matched = pd.read_csv(IO_DIR / "Matched_Population_Keys.csv")
    df_gss = pd.read_csv(IO_DIR / "Aligned_GSS_2022.csv", low_memory=False)

    # Re-initialize Expander
    # We need to import or paste the ScheduleExpander class here first!
    expander = ScheduleExpander(df_gss, id_col="occID")

    # Run Validation
    validate_matching_quality(df_matched, expander, save_path=(IO_DIR / "Validation_ProfileMatcher_2025.txt"))
    """
    #HOUSEHOLD AGGREGATION ---------------------------------------------------------------------------------------------



