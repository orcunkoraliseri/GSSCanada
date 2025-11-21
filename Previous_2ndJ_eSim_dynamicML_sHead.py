import pathlib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Tuple
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

keras = tf.keras
layers = tf.keras.layers

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Tuple, Any
import numpy as np  # <-- Make sure to import numpy

def prepare_data_for_generative_model(
        file_paths_dict: Dict[int, str],
        sample_frac: float = 1.0,  # <-- NEW: Set to < 1.0 to sample
        random_state: int = 42  # <-- NEW: For reproducible samples
) -> Tuple[pd.DataFrame, List[str], List[str], Dict[str, MinMaxScaler]]:
    """
    Loads, combines, samples (optional), and preprocesses all census datasets
    for a temporal generative model (C-VAE).
    """

    # --- 1. Load and Combine All Datasets ---
    print("--- 1. Loading and combining all datasets... ---")
    all_dfs = []
    for year, path in file_paths_dict.items():
        try:
            df = pd.read_csv(path, dtype=str)
            df['YEAR'] = str(year)
            all_dfs.append(df)
        except FileNotFoundError:
            print(f"Warning: File not found {path}. Skipping.")
    full_df = pd.concat(all_dfs, ignore_index=True)

    # --- 2. NEW: Household-level Sampling ---
    if sample_frac < 1.0:
        print(f"--- 2. Sampling {sample_frac * 100}% of households... ---")

        # Create a globally unique ID for households (HH_ID + YEAR)
        full_df['GLOBAL_HH_ID'] = full_df['YEAR'].astype(str) + '_' + full_df['HH_ID'].astype(str)

        # Get all unique household IDs
        unique_hh_ids = full_df['GLOBAL_HH_ID'].unique()

        # Calculate sample size
        n_households = len(unique_hh_ids)
        sample_size = int(n_households * sample_frac)

        # Get a reproducible random sample of household IDs
        rng = np.random.RandomState(random_state)
        sampled_hh_ids = rng.choice(unique_hh_ids, size=sample_size, replace=False)

        # Filter the main DataFrame to keep only these households
        full_df = full_df[full_df['GLOBAL_HH_ID'].isin(sampled_hh_ids)].copy()

        # Clean up the temporary column
        full_df = full_df.drop(columns=['GLOBAL_HH_ID'])

        print(f"   Sampled {sample_size} unique households, {len(full_df)} total person-rows.")
    else:
        print("--- 2. Using 100% of data (no sampling). ---")

    # --- 3. Define Feature and Condition Columns ---
    ID_COLS_TO_DROP = ['HH_ID', 'EF_ID', 'CF_ID', 'PP_ID']
    DEMOGRAPHIC_FEATURES = ['MARSTH','EMPIN', 'TOTINC', 'KOL', 'ATTSCH', 'CIP', 'NOCS', "GENSTAT", "POWST", "CITIZEN",
                            "LFTAG", "CF_RP", "COW", 'CMA', 'AGEGRP', 'SEX', 'CFSTAT', "INCTAX", 'HHSIZE', "EFSIZE",
                            "CFSIZE","PR","VALUE","HRSWRK", "MODE"]

    BUILDING_FEATURES = ["BUILTH", "TENUR", "CONDO", 'BEDRM', 'ROOM', 'DTYPE', "REPAIR",]
    CONTINUOUS_COLS = ['EMPIN', 'TOTINC', 'INCTAX',"VALUE"]

    # --- 4. Filter and Preprocess ---
    print("--- 4. Filtering to relevant columns... ---")
    all_features = list(set(DEMOGRAPHIC_FEATURES + BUILDING_FEATURES))
    all_cols_to_use = [
        col for col in all_features
        if col in full_df.columns and col not in ID_COLS_TO_DROP
    ]
    df_filtered = full_df[all_cols_to_use].copy()
    print(f"--- 5. Identified {len(all_cols_to_use)} total columns. ---")

    # --- 6. Scale and Encode ---
    print("--- 6. Scaling continuous data (MinMax) and one-hot encoding... ---")
    continuous_to_scale = [col for col in CONTINUOUS_COLS if col in df_filtered.columns]
    categorical_to_encode = [col for col in all_cols_to_use if col not in continuous_to_scale]

    df_filtered[categorical_to_encode] = df_filtered[categorical_to_encode].fillna('Missing')

    scalers = {}
    for col in continuous_to_scale:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
        scaler = MinMaxScaler()
        df_filtered[col] = scaler.fit_transform(df_filtered[[col]])
        scalers[col] = scaler

    df_processed = pd.get_dummies(df_filtered, columns=categorical_to_encode, dtype=int)

    # --- 7. Get Final, Encoded Column Lists ---
    print("--- 7. Finalizing feature lists... ---")

    def get_final_col_names(feature_list, continuous_list, processed_cols):
        final_cols = []
        for col in feature_list:
            if col in continuous_list:
                if col in processed_cols:
                    final_cols.append(col)
            elif col in all_cols_to_use:
                final_cols.extend(
                    [c for c in processed_cols if c.startswith(f"{col}_")]
                )
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
def build_decoder(n_demo_features, n_bldg_features, latent_dim):
    """Builds the Decoder model with Batch Normalization."""
    latent_input = keras.Input(shape=(latent_dim,), name="z_input")
    bldg_input = keras.Input(shape=(n_bldg_features,), name="bldg_input")

    merged_input = layers.concatenate([latent_input, bldg_input])

    # --- UPDATED BLOCK ---
    x = layers.Dense(256)(merged_input)  # 1. Linear part
    x = layers.BatchNormalization()(x)  # 2. Normalize
    x = layers.ReLU()(x)  # 3. Activate

    x = layers.Dense(512)(x)  # 1. Linear part
    x = layers.BatchNormalization()(x)  # 2. Normalize
    x = layers.ReLU()(x)  # 3. Activate
    # --- END UPDATE ---

    reconstruction = layers.Dense(
        n_demo_features,
        activation="sigmoid",
        name="reconstruction"
    )(x)

    decoder = keras.Model(
        [latent_input, bldg_input],
        reconstruction,
        name="decoder"
    )
    return decoder

class CVAE(keras.Model):
    """Combines the encoder and decoder into one model with custom loss."""

    def __init__(self, encoder, decoder, beta=1.0, **kwargs):
        super().__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.beta = beta

        # --- NEW: Add more metrics to track ---
        self.total_loss_tracker = keras.metrics.Mean(name="total_loss")
        self.recon_loss_tracker = keras.metrics.Mean(name="recon_loss")
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")
        self.mse_tracker = keras.metrics.MeanSquaredError(name="mse")  # <-- ADDED
        # --- END NEW ---

    @property
    def metrics(self):
        # Return all metrics to be displayed
        return [
            self.total_loss_tracker,
            self.recon_loss_tracker,
            self.kl_loss_tracker,
            self.mse_tracker,  # <-- ADDED
        ]

    def call(self, inputs):
        demo_input, bldg_input = inputs
        z_mean, z_log_var, z = self.encoder([demo_input, bldg_input])
        reconstruction = self.decoder([z, bldg_input])
        return reconstruction, z_mean, z_log_var

    def train_step(self, data):
        inputs, output = data
        demo_input, bldg_input = inputs

        with tf.GradientTape() as tape:
            reconstruction, z_mean, z_log_var = self([demo_input, bldg_input])

            # 1. Reconstruction Loss (for training)
            recon_loss = tf.reduce_mean(
                tf.reduce_sum(
                    keras.losses.binary_crossentropy(output, reconstruction),
                    axis=-1
                )
            )

            # 2. KL Divergence
            kl_loss = -0.5 * (1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
            kl_loss = tf.reduce_mean(tf.reduce_sum(kl_loss, axis=1))

            # 3. Total loss
            total_loss = recon_loss + (self.beta * kl_loss)

        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))

        # --- Update all trackers ---
        self.total_loss_tracker.update_state(total_loss)
        self.recon_loss_tracker.update_state(recon_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        self.mse_tracker.update_state(output, reconstruction)  # <-- ADDED

        return {m.name: m.result() for m in self.metrics}  # Return all metrics

def train_cvae(
    df_processed,
    demo_cols,
    bldg_cols,
    latent_dim=32,
    epochs=100,
    batch_size=256
):
    """
    Main function to build and train the CVAE model.
    *** UPDATED: Removed LR Scheduler. ***
    """
    print("--- Preparing data for TensorFlow ---")

    n_demo_features = len(demo_cols)
    n_bldg_features = len(bldg_cols)

    demo_data = df_processed[demo_cols].values.astype(np.float32)
    bldg_data = df_processed[bldg_cols].values.astype(np.float32)

    dataset = tf.data.Dataset.from_tensor_slices((
        (demo_data, bldg_data),
        demo_data
    ))
    dataset = dataset.shuffle(buffer_size=1024).batch(batch_size).prefetch(tf.data.AUTOTUNE)

    print("--- Building C-VAE model ---")
    # Assumes build_encoder/decoder now have BatchNormalization
    encoder = build_encoder(n_demo_features, n_bldg_features, latent_dim)
    decoder = build_decoder(n_demo_features, n_bldg_features, latent_dim)

    beta_weight = latent_dim / n_demo_features
    print(f"Using KL Loss Beta weight: {beta_weight:.4f}")

    cvae = CVAE(encoder, decoder, beta=beta_weight)

    # --- Optimizer Reverted ---
    # Using a fixed (but fast) learning rate
    # This is recommended when using Batch Normalization
    stable_optimizer = keras.optimizers.Adam(
        learning_rate=1e-4,  # Fixed "fast" rate
        clipvalue=1.0        # Keep clipping as a safety rail
    )
    cvae.compile(optimizer=stable_optimizer)
    # --- END ---

    print(f"Model built. Latent dim: {latent_dim}")
    encoder.summary()

    print("--- Starting C-VAE Training ---")
    history = cvae.fit(dataset, epochs=epochs)

    print("--- Training Complete ---")
    return encoder, decoder, cvae, history
def plot_training_history(history):
    """
    Plots the total, reconstruction, and KL loss from the C-VAE
    training history.
    """
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # --- FIX IS HERE ---
    # Changed 'loss' to 'total_loss'
    ax1.plot(history.history['total_loss'], label='Total Loss')
    # --- END FIX ---

    ax1.set_title('Total Training Loss over Epochs')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss Value')
    ax1.legend()
    ax1.grid(True)

    # --- Plot 2: Loss Components ---
    # These keys are already correct
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
    reconstruction.
    """
    # 1. Select a few random samples
    data_sample = df_processed.sample(n_samples)

    # 2. Prepare the data
    demo_data = data_sample[demo_cols].values.astype(np.float32)
    bldg_data = data_sample[bldg_cols].values.astype(np.float32)

    # 3. Run data through the full VAE (Encode -> Decode)
    z_mean, z_log_var, z = encoder.predict([demo_data, bldg_data])
    reconstructed_data = decoder.predict([z, bldg_data])

    # 4. Convert back to DataFrames for easy comparison
    original_df = pd.DataFrame(demo_data, columns=demo_cols)
    reconstructed_df = pd.DataFrame(reconstructed_data, columns=demo_cols)

    print("--- Checking Reconstruction Quality (Sample 1) ---")
    print("\n--- ORIGINAL ---")
    # Show the 10 most "active" features for the first person
    print(original_df.iloc[0].nlargest(10))

    print("\n--- RECONSTRUCTED ---")
    # Show the same 10 features from the reconstructed data
    print(reconstructed_df.iloc[0][original_df.iloc[0].nlargest(10).index])

if __name__ == '__main__':
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

    encoder, decoder, cvae_model, training_history = train_cvae(
        df_processed=processed_data,
        demo_cols=demo_cols,
        bldg_cols=bldg_cols,
        latent_dim=256,  # You can experiment with this (e.g., 32, 64)
        epochs=300,  # You can start with fewer epochs (e.g., 50)
        batch_size=256
    )

    # --- 3. THIS IS THE NEW PART: Save your models ---
    print("--- Training complete. Saving models to disk... ---")

    # Save the components to your new MODEL_DIR
    encoder.save(MODEL_DIR / 'cvae_encoder.keras')
    decoder.save(MODEL_DIR / 'cvae_decoder.keras')

    print("--- Models successfully saved! ---")

    print("\n--- C-VAE Training Complete ---")
    plot_training_history(training_history)

    check_reconstruction_quality(encoder, decoder, processed_data, demo_cols, bldg_cols)

