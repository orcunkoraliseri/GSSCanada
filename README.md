# occModeling

Research code for generating synthetic residential occupancy schedules for Canadian housing and using those schedules in EnergyPlus building energy simulations.

This repository is script-driven and organized around three linked, progressively extending workflows:
- occupancy modeling from Statistics Canada Census and General Social Survey (GSS) data
- building energy modeling (BEM) through EnergyPlus using the generated occupancy schedules
- extension to mixed-use commercial building types (office, retail, hotel) for urban-scale energy modeling (UBEM)

---

## Research Roadmap & Status

The project is structured as a sequence of three publications, each building on the last.

| Publication | Scope | Status |
|---|---|---|
| **eSim 2026 Conference Paper** | Residential occupancy pipeline — proof of concept (GSS 2005–2022 → EnergyPlus) | ✅ **COMPLETE** |
| **1st Journal Paper** | Extended residential methodology, validation, and HPC-scale BEM simulations | ✅ **COMPLETE** |
| **2nd Journal Paper** | Full 9-step longitudinal residential pipeline (2005–2030) with Conditional Transformer augmentation, Census linkage, and activity-driven end-use loads | ✅ **COMPLETE** |
| **3rd Journal Paper** | Multi-channel (Residential + Office + Retail + Hotel) mixed-use tall building UBEM pipeline | 🔄 **IN PROGRESS** |

---

## Claude for OSS Application: Open-Source UBEM & Occupancy Framework

### 1. Project Overview & Vision

**Working title:** OpenUBEM-Occupancy

**Core technologies:** Python, `eppy`, `geomeppy`, EnergyPlus

My project aims to develop a comprehensive, fully open-source Urban Building Energy Modeling (UBEM) framework that integrates high-resolution occupancy data. While urban-scale energy modeling is growing quickly, many existing solutions are either proprietary, commercialized, or lack deep integration with complex occupancy behavior.

The goal is to build a Python-native framework on top of `eppy` and `geomeppy` that makes urban energy modeling more accessible, transparent, and extensible for the research community. By keeping the framework open-source, researchers worldwide can use, modify, and improve it without restrictive licensing.

### 2. About Me & Available Resources

I am a researcher at Concordia University specializing in building engineering and urban energy simulations. My background spans both UBEM and occupancy modeling, and I have authored several papers in these areas that will inform the framework's development.

To support the computational demands of urban-scale simulations, I have access to substantial cloud computing resources through Concordia University and Calcul Québec (Speed HPC cluster). With the infrastructure in place, the main bottleneck is rapid software development, structuring, and implementation.

### 3. How I Plan to Use Claude

I plan to use Claude to accelerate four areas:

- **Code development:** Draft, refactor, and debug Python workflows built on `eppy` and `geomeppy`, including automation around large numbers of EnergyPlus `.idf` files.
- **Data integration:** Build pipelines that clean, process, and map stochastic occupancy data into urban energy models.
- **Documentation and maintenance:** Generate docstrings, READMEs, and tutorials that keep the framework usable for the broader research community.
- **Research synthesis:** Help structure technical documentation and upcoming publications that will be released with the software.

### 4. Expected Impact & Outputs

With support from the Claude for OSS program and university cloud resources, this project aims to deliver:

- a fully open-source, well-documented Python framework on GitHub for UBEM and occupancy integration
- open-access datasets and scripts that bridge stochastic human behavior and urban energy demand
- peer-reviewed academic publications that document the methodology, validate the framework, and support open-source collaboration in the built environment sector

---

## Publication Details

### eSim 2026 Conference Paper — COMPLETE

**Title:** Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030): A GSS-Based Framework

**Scope:** Proof-of-concept demonstration of the GSS → occupancy schedule → EnergyPlus pipeline for Canadian residential buildings. Introduced the core data alignment methodology linking Statistics Canada GSS Time-Use cycles (2005, 2010, 2015, 2022) with Census PUMF data.

**Key contributions:**
- First published implementation of a GSS-to-EnergyPlus occupancy pipeline for Canada
- Validated activity-based occupancy harmonization across four GSS cycles
- Demonstrated longitudinal AT_HOME rate shifts (2005: 63.5% → 2022: 72.3%, COVID-19 behavioral signal captured)

---

### 1st Journal Paper — COMPLETE

**Scope:** Expanded methodology with full validation suite, peer-review-ready documentation, and HPC-scale BEM simulation campaign across Canadian climate zones.

**Key contributions:**
- Complete Census–GSS alignment and profile-matching pipeline
- HPC batch simulation infrastructure (Calcul Québec / Speed cluster)
- Paired Monte Carlo BEM analysis: frozen-frame (IDF + TMY), occupancy varied
- Activity-driven end-use loads for equipment and lighting

---

### 2nd Journal Paper — COMPLETE

**Title:** Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM — Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)

**Scope:** Full 9-step pipeline from raw GSS episodes to 8760 h EnergyPlus schedules, with deep-learning augmentation and a 2030 forecast.

**Pipeline summary (all 9 steps COMPLETE):**

| Step | Description | Status |
|---|---|---|
| 1 | Data Collection & Column Selection (GSS Main + Episode + Census PUMF) | ✅ 100% (39/39 checks) |
| 2 | Data Harmonization — TUI_01 crosswalk, AT_HOME derivation, co-presence OR-merge | ✅ 100% (54/54 checks) |
| 3 | Merge & Temporal Tiling — 10-min HETUS → 30-min downsampling (48 slots/day); 64,061 respondents | ✅ 99% (81/82 checks) |
| 4 | Model 1: Conditional Transformer — cross-cycle DDAY augmentation; production model = J3 (4/4 gates) | ✅ COMPLETE |
| 5 | Census–GSS Probabilistic Linkage — 286,537 persons; 144,507 HH BEM frame | ✅ COMPLETE |
| 6 | Model 2: Progressive Fine-Tuning + 2030 Forecast — DRIFT_MATRIX captures COVID-19 shift | ✅ COMPLETE |
| 7 | BEM Integration — schedule injection, metabolic map, HVAC setback | ✅ COMPLETE |
| 8 | BEM Simulation — HPC Monte Carlo campaigns; 8760 h load profiles | ✅ COMPLETE |
| 9 | Activity-Driven End-Use Loads — equipment + lighting scaled by occupant activity | ✅ COMPLETE |

**Model architecture (Step 4 — J3):**
- Shared 6-layer encoder + 6-layer auto-regressive activity decoder + parallel non-AR binary heads
- d_model = 384; ~29.25M parameters
- Input: 48 slots × 11 features/slot (occACT ×14, AT_HOME, 9 co-presence columns)
- Output: synthetic schedules for unobserved DDAY_STRATA; ~192,183 augmented diary-days
- Validation gates passed: `act_JS` 0.019 / `AT_HOME_RMS` 4.57 pp / co-presence max ~2.03 pp
- MDLM/SEDD searched and rejected (best composite score, but only 2/4 hard gates)

**Key dataset:**
- `hetus_30min.csv`: 64,061 rows × 96 columns (48 activity + 48 AT_HOME slots per respondent)
- Resolution: 30-min (BEM/UBEM-ready); 9× reduction in Transformer attention operations vs. 10-min

---

### 3rd Journal Paper — IN PROGRESS

**Title:** Longitudinal Occupancy-Driven Energy Demand in Canadian Mixed-Use Tall Buildings: GSS-Derived 4-Channel Occupancy Pipeline (2005–2030)

**Scope:** Extends the residential pipeline into a multi-channel generator targeting PNNL Tall and SuperTall mixed-use building prototypes (Calgary CZ7A, Montreal CZ6A).

#### Three-Leg Roadmap

| Leg | Channels | Status |
|---|---|---|
| Leg 1 | Residential only (AT_HOME replaces BEM baseline) | ✅ COMPLETE (2nd Journal) |
| Leg 2 | Residential + Office (AT_WORK modulates code-compliant densities) | 🔄 IN PROGRESS |
| Leg 3 | + Retail + Hotel (full 4-channel mixed-use) | 📋 PLANNED |

#### 4-Channel Architecture (Leg 3 target)

| Channel | Data Source | Drives | Occupiable Area Share |
|---|---|---|---|
| **Residential** | GSS `LOCATION = 300` → `AT_HOME` | HighRiseApartment zones | SuperTall 24.1% · Tall 24.4% |
| **Office** | GSS workplace LOCATION codes → `AT_WORK` | OpenOffice / ClosedOffice / Conference / Classroom | SuperTall 30.3% · Tall 24.4% |
| **Retail** | GSS retail LOCATION codes + TUI_01 shopping → `AT_RETAIL` | Retail Retail / Back_Space / Point_of_Sale / Entry | SuperTall 16.1% · Tall 24.4% |
| **Hotel** | StatCan monthly hotel-occupancy stats (Table 24-10-0048-01) | LargeHotel GuestRooms + amenities | SuperTall 29.5% · Tall 26.8% |

> Service / MEP / Circulation (~52% of gross floor area) stays on ASHRAE 90.1 / NECB17 defaults — not modulated.

**Key design decisions for Leg 2/3:**
- **Residential replaces** BEM baseline schedules (`Number_of_People = HHSIZE`)
- **Office, Retail, Hotel modulate** code-compliant peak densities (W/m², people/m²), preserving regulatory comparability
- Shared encoder between residential and office channels (universal time-of-day/day-of-week structure; only output heads are channel-specific)
- SLAW/UW loss weighting + PCGrad gradient surgery — mandatory (equal-weight MSE multi-head collapses COP peaks)
- WFH rate exposed as an explicit model-output scalar with 2030 sensitivity bands (Conservative 15–20% / Hybrid ~30% / Fully Hybrid ~40%)
- Hotel forecast uses SARIMA, not the Conditional Transformer (population-aggregate time series, not individual-respondent diary)
- Pareto model selection (Wasserstein + ACF-MAE + downstream peak) — never a single composite

**Target buildings:**
- `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf` (Montreal, 40,846 m²)
- `SuperTallBuilding_…_Z7A_v221.idf` (Calgary, 26,750 m²)

**Documentation in progress:**
- `3J_docs_occ_nTemp/Leg2_2-split/` — 2-channel (Residential + Office) pipeline spec
- `3J_docs_occ_nTemp/Leg3_4-split/` — 4-channel (+ Retail + Hotel) pipeline spec

---

## Project Snapshot

This repository generates realistic occupancy schedules for Canadian residential and mixed-use buildings by aligning Census demographic data with GSS time-use data, augmenting via deep learning, and converting those schedules for EnergyPlus simulation.

### Main Areas

- `0_Occupancy/`: raw Census and GSS inputs, aligned datasets, pipeline outputs, and saved model artifacts
- `0_BEM_Setup/`: IDF and EPW assets, templates, neighborhood/building models, and simulation outputs
- `eSim_occ_utils/`: occupancy pipelines, alignment logic, profile matching, aggregation, and conversion utilities
- `eSim_occ_utils/25CEN22GSS_classification/`: ML pipeline (Conditional Transformer + progressive fine-tuning + 2030 forecast)
- `eSim_bem_utils/`: schedule injection, IDF preprocessing, simulation, plotting, and reporting
- `eSim_tests/`: validation scripts and lightweight checks
- `2J_docs_occ_nTemp/`: 2nd journal — full 9-step pipeline documentation and validation reports
- `3J_docs_occ_nTemp/`: 3rd journal — 2-channel and 4-channel multi-use pipeline specs
- `eSim_docs_occ_utils/`, `eSim_docs_bem_utils/`, `eSim_docs_cloudSims/`, `eSim_docs_report/`: workflow and reporting docs

### Key Files

| File | Purpose |
|---|---|
| `run_bem.py` | Interactive entry point for the BEM workflow |
| `eSim_occ_utils/occ_config.py` | Occupancy data path configuration |
| `eSim_bem_utils/config.py` | EnergyPlus path configuration |
| `2J_docs_occ_nTemp/04B_model.py` | Conditional Transformer (J3) model definition |
| `2J_docs_occ_nTemp/04D_train.py` | Transformer training harness |
| `2J_docs_occ_nTemp/04E_inference.py` | Inference and synthetic diary generation |
| `eSim_occ_utils/25CEN22GSS_classification/run_step1.py` | ML pipeline: preprocessing, training, forecasting, validation |
| `eSim_occ_utils/25CEN22GSS_classification/run_step2.py` | ML pipeline: household assembly + profile matching |
| `eSim_occ_utils/25CEN22GSS_classification/run_step3.py` | ML pipeline: occupancy-to-BEM conversion |

---

## Main Entry Points

```bash
# Census-year occupancy pipelines (classical alignment-based)
python3 eSim_occ_utils/06CEN05GSS/06CEN05GSS_main.py --help
python3 eSim_occ_utils/11CEN10GSS/11CEN10GSS_main.py --help
python3 eSim_occ_utils/16CEN15GSS/16CEN15GSS_main.py --help

# ML pipeline (Conditional Transformer, 2025 Census / 2022 GSS)
python3 eSim_occ_utils/25CEN22GSS_classification/main_classification.py

# BEM workflow
python3 run_bem.py
```

---

## Environment Notes

- Python 3.9+ is expected.
- Common dependencies include `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `tqdm`, `scikit-learn`, `eppy`, `tensorflow` (or `torch`), and `fpdf`.
- Occupancy data paths are configured in `eSim_occ_utils/occ_config.py`. Override the occupancy data root with `GSS_BASE_DIR` if needed.
- EnergyPlus paths are configured in `eSim_bem_utils/config.py`. Override the EnergyPlus installation with `ENERGYPLUS_DIR` if needed.
- HPC execution targets Concordia's **Speed cluster** (`o_iseri@speed.encs.concordia.ca`). All Python execution on the cluster must go through the scheduler (`sbatch` or `srun`); bare `python3` on the login node is prohibited.

---

## Notes

- This is research code, so scripts are typically run one at a time rather than through a single automated pipeline.
- The repository contains sensitive Census and GSS source data under `0_Occupancy/DataSources_*`; those files should be treated carefully.
- Do not modify `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, or `eSim_dynamicML_mHead_alignment.py` unless explicitly instructed — these are production pipeline files tied to published results.

---

*Last updated: June 2026*
