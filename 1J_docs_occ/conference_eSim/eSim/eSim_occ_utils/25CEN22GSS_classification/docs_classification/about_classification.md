# About Occupancy Classification (25CEN22GSS)

This document details the specific execution pipeline and dataset requirements for the dynamic generative occupancy model as controlled by `main_classification.py`.

---

## 1. Pipeline Execution Flow & Dataset Mapping

The pipeline is organized into three major stages. Each sub-step is mapped to its specific data dependencies below.

### STEP 1: CVAE Model & Forecasting
*   **1a — Training:** Trains the CVAE from scratch.
    *   **Inputs:** `cen06_filtered2.csv`, `cen11_filtered2.csv`, `cen16_filtered2.csv`, `cen21_filtered2.csv`.
    *   **Outputs:** `cvae_encoder.keras`, `cvae_decoder.keras`.
*   **1b — Testing:** Validates reconstruction quality.
    *   **Inputs:** Historic Census CSVs (Step 1a) + Saved Keras models.
*   **1c — Forecasting:** Models temporal drift and generates future populations.
    *   **Inputs:** Historic Census CSVs (to model drift) + Saved Keras models.
    *   **Outputs:** `forecasted_population_2025.csv`.
*   **1d — Visual Validation:** Generates latent-space trajectory plots.
    *   **Inputs:** Historic Census CSVs + Saved Keras models.

### STEP 2: Schedule Assignment & Processing
*   **2a — Household Assembly:** Links individual agents into households.
    *   **Inputs:** `forecasted_population_2025.csv`.
    *   **Outputs:** `forecasted_population_2025_LINKED.csv`.
*   **2b — Profile Matcher:** Matches Census agents to time-use schedules.
    *   **Inputs:** `Aligned_Census_2025.csv`, `Aligned_GSS_2022.csv`.
    *   **Outputs:** `Matched_Population_Keys.csv`, `Full_Expanded_Schedules.csv`.
*   **2c — Validation (PM):** Statistical quality check of matching.
    *   **Inputs:** `Matched_Population_Keys.csv`, `Aligned_GSS_2022.csv`.
*   **2d — Post-Processing:** Refines Dwelling Type (DTYPE) labels.
    *   **Inputs:** `Full_Expanded_Schedules.csv`, `Matched_Population_Keys.csv`, `cen06_filtered.csv`, `cen11_filtered.csv`.
    *   **Outputs:** `Full_Expanded_Schedules_Refined.csv`.
*   **2e — Household Aggregation:** Consolidates to 5-minute time-grid.
    *   **Inputs:** `Full_Expanded_Schedules_Refined.csv`.
    *   **Outputs:** `Full_data.csv`.
*   **2f — Validation (HH):** Completeness and logic check.
    *   **Inputs:** `Full_data.csv`.

### STEP 3: BEM Output
*   **3a — BEM Conversion:** Hourly schedule generation for EnergyPlus.
    *   **Inputs:** `Full_data.csv`.

---

## 2. Dataset Summary Table

| Stage | Key Input Datasets | Primary Output |
| :--- | :--- | :--- |
| **Model Training** | Census 2006, 2011, 2016, 2021 (`filtered2`) | `cvae_encoder.keras` |
| **Forecasting** | Latent drift from 2006-2021 sequence | `forecasted_population_2025.csv` |
| **Matching** | Forecasted 2025 population + GSS 2022 | `Full_Expanded_Schedules.csv` |
| **Refinement** | Census 2006, 2011 (`filtered`) | `Full_Expanded_Schedules_Refined.csv` |
| **Aggregation** | Refined expanded schedules | `Full_data.csv` |
| **BEM Export** | Aggregated 5-min household data | EnergyPlus Schedules (IDF/SQL) |

---

## 3. Data Source Distinction (Census vs. GSS)

A critical distinction in this pipeline is how the different data types are utilized:

*   **Generative Stage (Step 1):** Uses **100% Census data**. The CVAE and temporal drift models are trained exclusively on Census demographic and building features (2006–2021) to learn and extrapolate population trends. **No GSS data is used to train these generative models.**
*   **Behavioral Stage (Step 2):** Integrates **GSS data**. The matching process (`Profile Matcher`) is where demographics meet behavior. It bridges the synthetic Census population with real-world time-use patterns from the **GSS 2022** dataset.
*   **Final Result:** The final EnergyPlus-ready schedules represent the behaviors of real GSS participants mapped onto the forecasted demographics of synthetic future Census populations.

---

## 4. Usage Instructions

To run the pipeline, edit the `RUN_...` boolean flags in `main_classification.py` and execute:

```bash
python main_classification.py
```
