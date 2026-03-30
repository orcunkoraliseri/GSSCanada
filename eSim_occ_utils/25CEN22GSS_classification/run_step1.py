# =============================================================================
# run_step1.py
# Step 1 Runner: CVAE Training, Testing, Forecasting & Visual Validation
#
# This file wraps the four Step 1 blocks from eSim_dynamicML_mHead.py into
# callable functions. No existing file is modified.
# =============================================================================

from __future__ import annotations

import pathlib
import sys
from pathlib import Path

import pandas as pd
import tensorflow as tf

# --- Path Configuration ---
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from previous.eSim_dynamicML_mHead import (
    Sampling,
    check_reconstruction_quality,
    generate_future_population,
    plot_training_history,
    post_process_generated_data,
    prepare_data_for_generative_model,
    train_cvae,
    train_temporal_model,
    validate_forecast_distributions,
    validate_forecast_trajectory,
    validate_vae_reconstruction,
)
from eSim_occ_utils.occ_config import (
    BASE_DIR,
    DATA_DIR,
    MODEL_DIR,
    OUTPUT_DIR,
    OUTPUT_DIR_ALIGNED,
)

keras = tf.keras

# --- Shared path variables (mirrors the DIRECTORIES block in eSim_dynamicML_mHead.py) ---
cen06_filtered2: Path = OUTPUT_DIR / "cen06_filtered2.csv"
cen11_filtered2: Path = OUTPUT_DIR / "cen11_filtered2.csv"
cen16_filtered2: Path = OUTPUT_DIR / "cen16_filtered2.csv"
cen21_filtered2: Path = OUTPUT_DIR / "cen21_filtered2.csv"
VALIDATION_FORECASTVIS_DIR: Path = OUTPUT_DIR / "Validation_Forecasting_Visual"
VALIDATION_FORECAST_DIR: Path = OUTPUT_DIR / "Validation_Forecasting_VisualbyColumn"


# =============================================================================
# SUB-STEP 1a: TRAINING
# =============================================================================
def run_training() -> None:
    """
    Trains the CVAE model from scratch using census data from 2006–2021.

    Saves the encoder and decoder to MODEL_DIR.

    Inputs:
        OUTPUT_DIR/cen06_filtered2.csv … cen21_filtered2.csv

    Outputs:
        MODEL_DIR/cvae_encoder.keras
        MODEL_DIR/cvae_decoder.keras

    Returns:
        None
    """
    file_paths: dict[int, Path] = {
        2006: cen06_filtered2,
        2011: cen11_filtered2,
        2016: cen16_filtered2,
        2021: cen21_filtered2,
    }
    processed_data, demo_cols, bldg_cols, data_scalers = (
        prepare_data_for_generative_model(file_paths, sample_frac=1)
    )

    encoder, decoder, cvae_model, training_history = train_cvae(
        df_processed=processed_data,
        demo_cols=demo_cols,
        bldg_cols=bldg_cols,
        continuous_cols=["EMPIN", "TOTINC", "INCTAX", "VALUE"],
        latent_dim=128,
        epochs=100,
        batch_size=4096,
    )

    print("--- Training complete. Saving models to disk... ---")
    encoder.save(MODEL_DIR / "cvae_encoder.keras")
    decoder.save(MODEL_DIR / "cvae_decoder.keras")
    print("--- Models successfully saved! ---")

    print("\n--- C-VAE Training Complete ---")
    plot_training_history(training_history)
    check_reconstruction_quality(
        encoder, decoder, processed_data, demo_cols, bldg_cols
    )
    print(f"--- Models saved to: {MODEL_DIR} ---")


# =============================================================================
# SUB-STEP 1b: TESTING
# =============================================================================
def run_testing() -> None:
    """
    Loads saved CVAE models and validates reconstruction quality.

    Validates against the original census data.

    Inputs:
        MODEL_DIR/cvae_encoder.keras
        MODEL_DIR/cvae_decoder.keras
        OUTPUT_DIR/cen06_filtered2.csv … cen21_filtered2.csv

    Outputs:
        OUTPUT_DIR/Validation_VAE_Reconstruction/validation_vae_reconstruction.csv

    Returns:
        None
    """
    file_paths: dict[int, Path] = {
        2006: cen06_filtered2,
        2011: cen11_filtered2,
        2016: cen16_filtered2,
        2021: cen21_filtered2,
    }
    processed_data, demo_cols, bldg_cols, data_scalers = (
        prepare_data_for_generative_model(file_paths, sample_frac=1)
    )

    # IMPORTANT: Sampling must be passed as a custom_object when loading the encoder
    encoder = keras.models.load_model(
        MODEL_DIR / "cvae_encoder.keras", custom_objects={"Sampling": Sampling}
    )
    decoder = keras.models.load_model(MODEL_DIR / "cvae_decoder.keras")
    print("--- Models loaded successfully! ---")

    (OUTPUT_DIR / "Validation_VAE_Reconstruction").mkdir(parents=True, exist_ok=True)
    validate_vae_reconstruction(
        encoder,
        decoder,
        processed_data,
        demo_cols,
        bldg_cols,
        continuous_cols=["EMPIN", "TOTINC", "INCTAX", "VALUE"],
        n_samples=10,
        output_dir=OUTPUT_DIR,
    )


# =============================================================================
# SUB-STEP 1c: FORECASTING
# =============================================================================
def run_forecasting(
    target_years: list[int] | None = None, n_samples: int = 2000
) -> None:
    """
    Models temporal drift in latent space and generates forecasted populations.

    Parameters:
        target_years: The years to forecast. Defaults to [2025, 2030].
        n_samples: Number of synthetic individuals to generate per year.

    Inputs:
        MODEL_DIR/cvae_encoder.keras
        MODEL_DIR/cvae_decoder.keras
        OUTPUT_DIR/cen06_filtered2.csv … cen21_filtered2.csv

    Outputs:
        OUTPUT_DIR/Generated/forecasted_population_2025.csv
        OUTPUT_DIR/Generated/forecasted_population_2030.csv

    Returns:
        None
    """
    if target_years is None:
        target_years = [2025, 2030]

    file_paths: dict[int, Path] = {
        2006: cen06_filtered2,
        2011: cen11_filtered2,
        2016: cen16_filtered2,
        2021: cen21_filtered2,
    }
    processed_data, demo_cols, bldg_cols, data_scalers = (
        prepare_data_for_generative_model(file_paths, sample_frac=1)
    )

    # IMPORTANT: Sampling must be passed as a custom_object when loading the encoder
    encoder = keras.models.load_model(
        MODEL_DIR / "cvae_encoder.keras", custom_objects={"Sampling": Sampling}
    )
    decoder = keras.models.load_model(MODEL_DIR / "cvae_decoder.keras")

    print("\n=== Step 3: Modeling Temporal Drift ===")
    temporal_model, last_population_z, last_year = train_temporal_model(
        encoder, processed_data, demo_cols, bldg_cols
    )

    # Use a local variable for the Generated subfolder — do NOT overwrite OUTPUT_DIR
    output_dir_gen: Path = Path(OUTPUT_DIR) / "Generated"
    output_dir_gen.mkdir(parents=True, exist_ok=True)

    for year in target_years:
        print(f"\n=== Step 4: Forecasting for {year} ===")

        gen_raw, bldg_raw, _ = generate_future_population(
            decoder,
            temporal_model,
            last_population_z,
            last_year,
            processed_data,
            bldg_cols,
            target_year=year,
            n_samples=n_samples,
            variance_factor=1.15,
        )

        df_forecast = post_process_generated_data(
            gen_raw,
            demo_cols,
            bldg_raw,
            bldg_cols,
            data_scalers,
            ref_df=processed_data,
        )

        df_forecast["YEAR"] = year
        save_path: Path = output_dir_gen / f"forecasted_population_{year}.csv"
        df_forecast.to_csv(save_path, index=False)
        print(f"✅ Saved {year} forecast to: {save_path}")
        print(df_forecast.head())


# =============================================================================
# SUB-STEP 1d: VISUAL VALIDATION OF FORECASTING
# =============================================================================
def run_visual_validation() -> None:
    """
    Generates latent-space trajectory plots to visually validate forecast quality.

    Inputs:
        MODEL_DIR/cvae_encoder.keras
        MODEL_DIR/cvae_decoder.keras
        OUTPUT_DIR/cen06_filtered2.csv … cen21_filtered2.csv

    Outputs:
        Validation plots saved to OUTPUT_DIR/Validation_Forecasting_Visual/

    Returns:
        None
    """
    file_paths: dict[int, Path] = {
        2006: cen06_filtered2,
        2011: cen11_filtered2,
        2016: cen16_filtered2,
        2021: cen21_filtered2,
    }
    processed_data, demo_cols, bldg_cols, data_scalers = (
        prepare_data_for_generative_model(file_paths, sample_frac=1)
    )

    # IMPORTANT: Sampling must be passed as a custom_object when loading the encoder
    encoder = keras.models.load_model(
        MODEL_DIR / "cvae_encoder.keras", custom_objects={"Sampling": Sampling}
    )
    # decoder = keras.models.load_model(MODEL_DIR / 'cvae_decoder.keras')

    VALIDATION_FORECASTVIS_DIR.mkdir(parents=True, exist_ok=True)
    validate_forecast_trajectory(
        encoder, processed_data, demo_cols, bldg_cols, VALIDATION_FORECASTVIS_DIR
    )


# =============================================================================
# CONTROL PANEL
# Set each flag to True to run that sub-step when executing this file directly.
# =============================================================================
if __name__ == "__main__":
    RUN_TRAINING: bool = False  # trains from scratch, saves encoder/decoder
    RUN_TESTING: bool = False  # loads saved models, validates reconstruction
    RUN_FORECASTING: bool = False  # generates forecasted_population_YYYY.csv
    RUN_VISUAL_VALIDATION: bool = False  # plots latent-space validation figures

    if RUN_TRAINING:
        run_training()
    if RUN_TESTING:
        run_testing()
    if RUN_FORECASTING:
        run_forecasting()
    if RUN_VISUAL_VALIDATION:
        run_visual_validation()
