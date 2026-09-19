# Occupancy Classification Framework (eSim_occ_utils)

This document provides a high-level architectural overview of the entire `eSim_occ_utils` suite, explaining the methodologies used to bridge Census demographics and Building Energy Modeling (BEM).

---

## 1. Architectural Evolution

The framework is structured as a progressive stack, moving from static validation to dynamic prediction.

### Phase 1: Legacy Static Pipelines (`06CEN05GSS`, `16CEN15GSS`)
*   **Role:** These directories contain the original logic for harmonizing specific historic Census years with GSS data.
*   **Legacy Value:** They established the **data filtering and cleaning standards** for the Canadian Census (2006, 2011, 2016) that are still used today.
*   **Workflow:** Alignment → Profile Matching → HH Aggregation → BEM.

### Phase 2: Dynamic Generative Pipeline (`25CEN22GSS_classification`)
*   **Role:** The "Active" production pipeline for future forecasting (2025–2030).
*   **Data Usage:** While it operates independently of the Phase 1 *scripts*, it **requires the data outputs** (specifically `cen06_filtered.csv` and `cen11_filtered.csv`) to train the Random Forest models used for building-type refinement.
*   **Innovation:** Decouples from specific historic years by using CVAE-based population synthesis.

---

## 2. System Interconnections

The pipelines are unified by a shared infrastructure rather than direct code-to-code calls:

### 2.1 Shared Configuration (`occ_config.py`)
A central "brain" that defines global paths (`DATA_DIR`, `OUTPUT_DIR`). This ensures that Phase 2 knows exactly where to find the historic files processed by the Phase 1 logic.

### 2.2 Shared File Parsers (`cen_reader.py`, `gss_reader.py`)
Root-level utilities that provide a standardized way to parse Census `.dat` and GSS `.sas7bdat` files across all pipeline versions.

### 2.3 The "Previous" Logic Bridge
The `25CEN22GSS_classification` directory includes a `previous/` folder. This represents the **conceptual bridge** where Phase 1 logic was integrated into the generative framework, allowing Step 2 of the modern pipeline to leverage historic trends for better prediction accuracy.

---

## 3. Comprehensive Data Coverage

Phase 2 acts as a "Master" pipeline that consumes the full spectrum of available data to ensure high-fidelity forecasting.

### 3.1 Census: The 15-Year Sequence
The CVAE and Temporal Drift models are trained on a continuous sequence of Census data:
*   **2006, 2011, 2016, 2021:** These years are not treated as isolated folders but are integrated directly into the `run_step1.py` training logic. This allows the model to learn the "momentum" of demographic and building shifts over a 15-year span.

### 3.2 GSS: The Behavior Engine
*   **GSS 2022:** The pipeline uses the most recent General Social Survey (2022) to assign schedules to synthetic 2025 populations. It assumes that future behavior patterns will most closely align with the latest surveyed trends.

---

## 4. Directory Structure Overview

| Directory | Role | Relation to Modern Pipeline |
| :--- | :--- | :--- |
| `eSim_occ_utils/` | Core Engine | **Shared Infrastructure** |
| `06CEN05GSS/` | 2006 Baseline | Established historic cleaning standards |
| `16CEN15GSS/` | 2016 Validation | Established validation benchmarks |
| `25CEN22GSS_cl../` | 2025 Forecasting | **Main Execution Point** |
