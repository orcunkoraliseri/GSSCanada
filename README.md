# occModeling

Research code for generating synthetic residential occupancy schedules for Canadian housing and using those schedules in EnergyPlus building energy simulations.

This repository is script-driven and organized around two linked workflows:
- occupancy modeling from Statistics Canada Census and General Social Survey (GSS) data
- building energy modeling through EnergyPlus using the generated occupancy schedules

## Claude for OSS Application: Open-Source UBEM & Occupancy Framework

### 1. Project Overview & Vision

**Working title:** OpenUBEM-Occupancy

**Core technologies:** Python, `eppy`, `geomeppy`, EnergyPlus

My project aims to develop a comprehensive, fully open-source Urban Building Energy Modeling (UBEM) framework that integrates high-resolution occupancy data. While urban-scale energy modeling is growing quickly, many existing solutions are either proprietary, commercialized, or lack deep integration with complex occupancy behavior.

The goal is to build a Python-native framework on top of `eppy` and `geomeppy` that makes urban energy modeling more accessible, transparent, and extensible for the research community. By keeping the framework open-source, researchers worldwide can use, modify, and improve it without restrictive licensing.

### 2. About Me & Available Resources

I am a researcher at Concordia University specializing in building engineering and urban energy simulations. My background spans both UBEM and occupancy modeling, and I have authored several papers in these areas that will inform the framework’s development.

To support the computational demands of urban-scale simulations, I have access to substantial cloud computing resources through Concordia University and Calcul Québec. With the infrastructure in place, the main bottleneck is rapid software development, structuring, and implementation.

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

## Project Snapshot

This repository currently focuses on generating realistic occupancy schedules for Canadian residential buildings by aligning Census demographic data with GSS time-use data, then converting those schedules for EnergyPlus simulation.

### Main Areas

- `0_Occupancy/`: raw Census and GSS inputs, aligned datasets, pipeline outputs, and saved CVAE models
- `0_BEM_Setup/`: IDF and EPW assets, templates, neighborhood/building models, and simulation outputs
- `eSim_occ_utils/`: occupancy pipelines, alignment logic, profile matching, aggregation, and conversion utilities
- `eSim_bem_utils/`: schedule injection, IDF preprocessing, simulation, plotting, and reporting
- `eSim_tests/`: validation scripts and lightweight checks
- `run_bem.py`: interactive entry point for the BEM workflow

## Main Entry Points

- `python3 eSim_occ_utils/06CEN05GSS/06CEN05GSS_main.py --help`
- `python3 eSim_occ_utils/11CEN10GSS/11CEN10GSS_main.py --help`
- `python3 eSim_occ_utils/16CEN15GSS/16CEN15GSS_main.py --help`
- `python3 eSim_occ_utils/25CEN22GSS_classification/main_classification.py`
- `python3 run_bem.py`

## Environment Notes

- Python 3.9+ is expected.
- Common dependencies include `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `tqdm`, `scikit-learn`, `eppy`, `tensorflow`, and `fpdf`.
- Occupancy data paths are configured in `eSim_occ_utils/occ_config.py`.
- Override the occupancy data root with `GSS_BASE_DIR` if needed.
- EnergyPlus paths are configured in `eSim_bem_utils/config.py`.
- Override the EnergyPlus installation with `ENERGYPLUS_DIR` if needed.

## Notes

- This is research code, so scripts are typically run one at a time rather than through a single automated pipeline.
- The repository contains sensitive Census and GSS source data under `0_Occupancy/DataSources_*`; those files should be treated carefully.

