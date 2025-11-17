import pathlib
import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Tuple, Any
import numpy as np  # <-- Make sure to import numpy
from sklearn.linear_model import LinearRegression

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
        'BUILTH', 'TENUR', 'CONDO', 'BEDRM', 'ROOM', 'DTYPE', 'REPAIR', 'VALUE'
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
def train_cvae(df_processed, demo_cols, bldg_cols, continuous_cols=['EMPIN', 'TOTINC', 'INCTAX', 'VALUE'], latent_dim=48, epochs=100, batch_size=4096):
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
def post_process_generated_data(generated_raw_data, demo_cols,generated_bldg_data, bldg_cols,scalers):
    """
    Converts the raw generated data (probabilities) back into a
    human-readable, decoded DataFrame.
    """
    print("--- Starting Post-Processing ---")

    # 1. Create DataFrames
    # generated_raw_data is now a matrix, so this works directly
    df_gen_demo = pd.DataFrame(generated_raw_data, columns=demo_cols)
    df_gen_bldg = pd.DataFrame(generated_bldg_data, columns=bldg_cols)
    df_final = pd.DataFrame()

    # 2. Inverse-scale the continuous columns
    for col_name, scaler in scalers.items():
        if col_name in df_gen_demo.columns:
            col_data = df_gen_demo[col_name].values.reshape(-1, 1)
            df_final[col_name] = scaler.inverse_transform(col_data)

    # 3. Decode the One-Hot Encoded demographic columns
    all_prefixes = set()
    for col in demo_cols:
        if '_' in col and col not in scalers:  # Exclude continuous cols
            all_prefixes.add(col.rsplit('_', 1)[0])

    for prefix in all_prefixes:
        cat_cols = [col for col in demo_cols if col.startswith(f"{prefix}_")]
        if cat_cols:
            # For multi-head softmax, finding the max is the correct way to decode
            predicted_col = df_gen_demo[cat_cols].idxmax(axis=1)
            df_final[prefix] = predicted_col.str.replace(f"{prefix}_", "")

    # 4. Decode the One-Hot Encoded building columns
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
def check_reconstruction_quality_expanded(encoder, decoder, df_processed, demo_cols, bldg_cols, continuous_cols, n_samples=5):
    """
    Expanded evaluation: Checks multiple samples, groups one-hot columns
    back into features, and compares Original vs. Reconstructed values
    with Pass/Fail indicators.
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

    # 5. Identify Feature Groups (group 'AGEGRP_1', 'AGEGRP_2' -> 'AGEGRP')
    # We exclude continuous cols from this grouping
    categorical_prefixes = set()
    for col in demo_cols:
        if col not in continuous_cols:
            # Split 'AGEGRP_1' into 'AGEGRP'
            prefix = col.rsplit('_', 1)[0]
            categorical_prefixes.add(prefix)

    sorted_prefixes = sorted(list(categorical_prefixes))

    # 6. Loop through each sample
    for i in range(n_samples):
        print(f"\n--- Sample {i + 1} / {n_samples} ---")
        print(f"{'FEATURE':<15} | {'ORIGINAL':<15} | {'PREDICTED':<15} | {'CONFIDENCE':<10} | {'STATUS'}")
        print("-" * 75)

        # A) Check Categorical Features
        for prefix in sorted_prefixes:
            # Get all columns for this feature
            cols = [c for c in demo_cols if c.startswith(prefix + '_')]

            # Find the column name with the max value (The "Winner")
            # Original
            orig_row = df_orig.iloc[i][cols]
            orig_cat = orig_row.idxmax().replace(f"{prefix}_", "")  # e.g. "1"

            # Reconstructed
            recon_row = df_recon.iloc[i][cols]
            pred_cat = recon_row.idxmax().replace(f"{prefix}_", "")  # e.g. "1"
            confidence = recon_row.max()

            # Status Check
            status = "✅" if orig_cat == pred_cat else "❌"

            print(f"{prefix:<15} | {orig_cat:<15} | {pred_cat:<15} | {confidence:.4f}     | {status}")

        # B) Check Continuous Features
        for col in continuous_cols:
            if col in demo_cols:
                val_orig = df_orig.iloc[i][col]
                val_pred = df_recon.iloc[i][col]
                diff = abs(val_orig - val_pred)

                # For continuous, we consider it "Good" if error is low (e.g., < 0.05 in scaled space)
                status = "✅" if diff < 0.05 else "⚠️"

                print(f"{col:<15} | {val_orig:.4f}          | {val_pred:.4f}          | Diff: {diff:.3f}  | {status}")

if __name__ == '__main__':
    #DIRECTORIES -------------------------------------------------------------------------------------------------------
    # BASE_DIR = pathlib.Path("C:/Users/o_iseri/Desktop/2ndJournal")
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal")

    DATA_DIR = BASE_DIR / "DataSources_CENSUS"
    OUTPUT_DIR = BASE_DIR / "Outputs_CENSUS"

    # --- NEW: Define a directory to save your trained models ---
    MODEL_DIR = BASE_DIR / "saved_models_cvae"
    MODEL_DIR.mkdir(parents=True, exist_ok=True)  # This creates the folder

    # --- 2006 Files ---
    cen06_filtered2 = OUTPUT_DIR / "cen06_filtered2.csv"
    cen11_filtered2 = OUTPUT_DIR / "cen11_filtered2.csv"
    cen16_filtered2 = OUTPUT_DIR / "cen16_filtered2.csv"
    cen21_filtered2 = OUTPUT_DIR / "cen21_filtered2.csv"

    file_paths = {2006: cen06_filtered2, 2011: cen11_filtered2, 2016: cen16_filtered2, 2021: cen21_filtered2}
    processed_data, demo_cols, bldg_cols, data_scalers = prepare_data_for_generative_model(file_paths,sample_frac=1)
    """
    #TRAINING ----------------------------------------------------------------------------------------------------------
    encoder, decoder, cvae_model, training_history = train_cvae(df_processed=processed_data, demo_cols=demo_cols, bldg_cols=bldg_cols,
        latent_dim=128,  epochs=200, batch_size=4096)

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
    encoder = keras.models.load_model(MODEL_DIR / 'cvae_encoder.keras', custom_objects={'Sampling': Sampling})
    decoder = keras.models.load_model(MODEL_DIR / 'cvae_decoder.keras')
    print("--- Models loaded successfully! ---")
    #check_reconstruction_quality_expanded(encoder, decoder, processed_data, demo_cols, bldg_cols, continuous_cols=['EMPIN', 'TOTINC', 'INCTAX', 'VALUE'], n_samples=5)

    #FORECASTING -------------------------------------------------------------------------------------------------------
    """"""
    # 3. Train Temporal Drift
    print("\n=== Step 3: Modeling Temporal Drift ===")
    temporal_model, last_variance = train_temporal_model( encoder,processed_data, demo_cols, bldg_cols)

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
