# occModeling

**Synthetic occupancy schedules for Canadian buildings, driven by Statistics Canada Census + General Social Survey (GSS) time-use data, and consumed by EnergyPlus building energy simulations.**

This repository is research code for a longitudinal (2005–2030) occupancy-modeling program. It turns raw StatCan microdata into hour-by-hour occupant presence and activity schedules, augments them with a Conditional Transformer, links them to Census-scale synthetic populations, and injects the result into EnergyPlus `.idf` models for building- and urban-scale energy simulation.

The codebase is **script-driven, not package-driven** — most workflows are run one file at a time rather than through a single automated entry point — and is organized around three linked, progressively extending workflows:

- **Occupancy modeling** — from StatCan Census and GSS Time-Use data
- **Building energy modeling (BEM)** — EnergyPlus simulation using the generated occupancy schedules
- **Urban / mixed-use modeling (UBEM)** — extension to office, retail, and hotel building types for tall mixed-use buildings

> **New here?** Jump to [Quick Start](#quick-start) to install and run, or [Repository Layout](#repository-layout) to find your way around. For the research narrative, see [Research Roadmap & Status](#research-roadmap--status).

---

## Table of Contents

- [Research Roadmap & Status](#research-roadmap--status)
- [Quick Start](#quick-start)
- [Repository Layout](#repository-layout)
- [Pipeline Architecture](#pipeline-architecture)
- [Data Sources](#data-sources)
- [Publication Details](#publication-details)
- [Claude for OSS Application](#claude-for-oss-application-open-source-ubem--occupancy-framework)
- [Environment Notes](#environment-notes)
- [Repository Conventions](#repository-conventions)
- [Citation, License & Contact](#citation-license--contact)

---

## Research Roadmap & Status

The project is structured as a sequence of publications, each building on the last.

| Publication | Scope | Status |
|---|---|---|
| **eSim 2026 Conference Paper** | Residential occupancy pipeline — proof of concept (GSS 2005–2022 → EnergyPlus) | ✅ **COMPLETE** |
| **1st Journal Paper** | Extended residential methodology, validation, and HPC-scale BEM simulations | ✅ **COMPLETE** |
| **2nd Journal Paper** | Full 9-step longitudinal residential pipeline (2005–2030) with Conditional Transformer augmentation, Census linkage, and activity-driven end-use loads | ✅ **COMPLETE** |
| **3rd Journal Paper** | Multi-channel (Residential + Office + Retail + Hotel) mixed-use tall-building UBEM pipeline | 🔄 **IN PROGRESS** |

---

## Quick Start

Full setup instructions live in [`INSTALLATION.md`](INSTALLATION.md). The short version:

### 1. Prerequisites

- **Python 3.9+**
- **EnergyPlus 24.2.0** (required only for the BEM/simulation stages)
  - macOS default: `/Applications/EnergyPlus-24-2-0`
  - Windows default: `C:\EnergyPlusV24-2-0`
  - Override with the `ENERGYPLUS_DIR` environment variable.

### 2. Install Python dependencies

```bash
# Recommended: isolate in a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Core dependency groups (see [`INSTALLATION.md`](INSTALLATION.md) for the annotated list):

| Area | Packages |
|---|---|
| Data processing | `pandas`, `numpy`, `scipy`, `pyreadstat`, `openpyxl` |
| Machine learning | `scikit-learn`, `torch` (or `tensorflow`), `tqdm` |
| Building energy modeling | `eppy`, `geomeppy` |
| Visualization & reporting | `matplotlib`, `seaborn`, `fpdf`, `PyPDF2` |

### 3. Configure data paths

Before running anything, point the config files at your local data:

- **Occupancy data** — `eSim_occ_utils/occ_config.py` (or set `GSS_BASE_DIR` to your `0_Occupancy` folder)
- **EnergyPlus** — `eSim_bem_utils/config.py` (or set `ENERGYPLUS_DIR`)

### 4. Run a workflow

```bash
# --- Census-year occupancy pipelines (classical alignment-based) ---
python3 eSim_occ_utils/06CEN05GSS/06CEN05GSS_main.py --help   # Census 2006 ↔ GSS 2005
python3 eSim_occ_utils/11CEN10GSS/11CEN10GSS_main.py --help   # Census 2011 ↔ GSS 2010
python3 eSim_occ_utils/16CEN15GSS/16CEN15GSS_main.py --help   # Census 2016 ↔ GSS 2015

# --- ML pipeline (Conditional Transformer, 2025 Census / 2022 GSS) ---
# Flag-driven: toggle the RUN_* booleans in the file rather than passing a full CLI.
python3 eSim_occ_utils/25CEN22GSS_classification/main_classification.py

# --- BEM workflow (interactive / menu-driven) ---
python3 run_bem.py
```

> **Note:** This is research code — scripts are typically run individually and in sequence, not through one orchestrated command.

---

## Repository Layout

```
GSSCanada-main/
├── 0_Occupancy/                     # Census/GSS inputs, aligned datasets, pipeline outputs, saved models
│   ├── DataSources_CENSUS/          #   raw Census microdata (sensitive)
│   ├── DataSources_GSS/             #   raw GSS Time-Use microdata (sensitive)
│   ├── Outputs_Aligned/             #   harmonized Census–GSS datasets & matched schedules
│   └── saved_models_cvae/           #   expensive trained model artifacts
│
├── 0_BEM_Setup/                     # IDF/EPW assets, templates, neighbourhood/building models, sim outputs
│                                    #   (git-ignored; holds large generated artifacts)
│
├── eSim_occ_utils/                  # Occupancy pipelines & helpers
│   ├── 06CEN05GSS/ 11CEN10GSS/      #   year-pair pipelines (alignment → match → aggregate → BEM)
│   │   16CEN15GSS/ 21CEN22GSS/
│   ├── 25CEN22GSS_classification/   #   current ML pipeline (Conditional Transformer + forecast)
│   ├── cen_reader.py                #   Census microdata reader
│   ├── gss_reader.py                #   GSS microdata reader
│   ├── occ_config.py                #   occupancy data-path configuration
│   └── plotting/                    #   paper figures & tables
│
├── eSim_bem_utils/                  # BEM: schedule injection, IDF prep, simulation, reporting
│   ├── config.py                    #   EnergyPlus path configuration
│   ├── integration.py               #   schedule → IDF injection
│   ├── schedule_generator.py        #   occupancy → EnergyPlus schedule objects
│   ├── simulation.py                #   EnergyPlus run harness
│   ├── run_batch_hpc.py             #   HPC batch (Calcul Québec / Speed) driver
│   └── main.py                      #   interactive menu entrypoint (launched by run_bem.py)
│
├── eSim_tests/                      # Validation scripts and lightweight checks
│
├── 2J_docs_occ_nTemp/               # 2nd journal — full 9-step pipeline (00_…–09_…) + validation reports
├── 3J_docs_occ_nTemp/               # 3rd journal — 2-channel & 4-channel multi-use pipeline specs
│   ├── Leg2_2-split/                #   Residential + Office spec
│   └── Leg3_4-split/                #   + Retail + Hotel spec
│
├── eSim_docs_occ_utils/             # Occupancy workflow docs
├── eSim_docs_bem_utils/             # BEM workflow docs
├── eSim_docs_cloudSims/             # HPC / cluster batch docs
├── eSim_docs_ubem_utils/            # Urban-scale geometry & aggregation docs
├── eSim_docs_report/                # Validation, analysis, figures, paper sections
│
├── run_bem.py                       # Interactive entry point for the BEM workflow
├── INSTALLATION.md                  # Detailed setup & dependency guide
├── AGENTS.md / CLAUDE.md            # Agent workflow conventions & guardrails
└── README.md
```

### Key files

| File | Purpose |
|---|---|
| `run_bem.py` | Interactive entry point for the BEM workflow |
| `eSim_occ_utils/occ_config.py` | Occupancy data-path configuration (`GSS_BASE_DIR`) |
| `eSim_bem_utils/config.py` | EnergyPlus path configuration (`ENERGYPLUS_DIR`) |
| `2J_docs_occ_nTemp/04B_model.py` | Conditional Transformer (J3) model definition |
| `2J_docs_occ_nTemp/04D_train.py` | Transformer training harness |
| `2J_docs_occ_nTemp/04E_inference.py` | Inference / synthetic diary generation |
| `eSim_occ_utils/25CEN22GSS_classification/run_step1.py` | ML: preprocessing, training, forecasting, validation |
| `eSim_occ_utils/25CEN22GSS_classification/run_step2.py` | ML: household assembly + profile matching |
| `eSim_occ_utils/25CEN22GSS_classification/run_step3.py` | ML: occupancy-to-BEM conversion |

---

## Pipeline Architecture

There are **two occupancy pipelines** in this repo — a classical alignment-based one used for the earlier Census-year pairs, and an ML-based one that produces the longitudinal 2005–2030 dataset.

### A. Classical Census-year pipeline (`06/11/16/21`)

Each year-pair folder runs the same five-stage flow, typically converting 5-minute source diaries into 30-minute or hourly EnergyPlus schedules:

1. `*_alignment.py` — harmonize demographic columns between the Census and GSS cycle
2. `*_ProfileMatcher.py` — match Census agents to GSS schedules by demographic similarity (tiered fallback)
3. `*_HH_aggregation.py` — aggregate matched persons into complete households
4. `*_occToBEM.py` — convert occupancy diaries into EnergyPlus schedule objects
5. `*_main.py` — orchestrate the run

**Profile matching** uses a four-tier fallback so every agent gets a schedule while maximizing demographic fidelity:

| Tier | Match basis |
|---|---|
| Tier 1 | Perfect match (all harmonized columns) |
| Tier 2 | Core demographics (~6 key columns) |
| Tier 3 | Key constraints (~3 essential columns) |
| Tier 4 | Fail-safe (household size only) — kept near-zero in practice |

### B. ML pipeline (`25CEN22GSS_classification`)

The current production path replaces tiered matching with a deep-learning generator and a 2030 forecast. It is driven by three wrappers:

- `run_step1.py` — preprocessing, Conditional Transformer training, forecasting, validation
- `run_step2.py` — household assembly + probabilistic Census linkage + profile matching
- `run_step3.py` — occupancy-to-BEM schedule conversion

The full nine-step methodology (data collection → harmonization → tiling → augmentation → linkage → forecast → BEM integration → simulation → end-use loads) is documented step-by-step under [`2J_docs_occ_nTemp/`](2J_docs_occ_nTemp/). See the [2nd Journal Paper](#2nd-journal-paper--complete) section for the step-by-step status table and model architecture.

### C. BEM / UBEM integration (`eSim_bem_utils`)

Generated schedules are injected into EnergyPlus `.idf` models via `eppy`/`geomeppy`, simulated (locally or as HPC batches on the Speed cluster), and post-processed into 8760-hour load profiles and validation reports.

---

## Data Sources

| Source | Cycles used | Role |
|---|---|---|
| **StatCan GSS — Time Use** | 2005, 2010, 2015, 2022 | Episode-level activity & presence diaries |
| **StatCan Census PUMF** | 2006, 2011, 2016, 2021/2025 | Demographic frame for population synthesis |
| **StatCan Table 24-10-0048-01** | monthly | Hotel-occupancy series (3rd-journal hotel channel) |
| **PNNL prototype buildings** | — | Tall / SuperTall mixed-use IDF prototypes (CZ6A/CZ7A) |

> ⚠️ Raw Census and GSS microdata under `0_Occupancy/DataSources_*` are **sensitive and large**. Do not rename, move, delete, or rewrite them casually, and do not commit them.

---

## Publication Details

### eSim 2026 Conference Paper — COMPLETE

**Title:** Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030): A GSS-Based Framework

**Scope:** Proof-of-concept demonstration of the GSS → occupancy schedule → EnergyPlus pipeline for Canadian residential buildings. Introduced the core data-alignment methodology linking StatCan GSS Time-Use cycles (2005, 2010, 2015, 2022) with Census PUMF data.

**Key contributions:**
- First published implementation of a GSS-to-EnergyPlus occupancy pipeline for Canada
- Validated activity-based occupancy harmonization across four GSS cycles
- Demonstrated longitudinal AT_HOME rate shifts (2005: 63.5% → 2022: 72.3%, capturing the COVID-19 behavioral signal)

---

### 1st Journal Paper — COMPLETE

**Scope:** Expanded methodology with a full validation suite, peer-review-ready documentation, and an HPC-scale BEM simulation campaign across Canadian climate zones.

**Key contributions:**
- Complete Census–GSS alignment and profile-matching pipeline
- HPC batch simulation infrastructure (Calcul Québec / Speed cluster)
- Paired Monte Carlo BEM analysis: frozen-frame (IDF + TMY), occupancy varied
- Activity-driven end-use loads for equipment and lighting

---

### 2nd Journal Paper — COMPLETE

**Title:** Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM — Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)

**Scope:** Full 9-step pipeline from raw GSS episodes to 8760-hour EnergyPlus schedules, with deep-learning augmentation and a 2030 forecast.

**Pipeline summary (all 9 steps COMPLETE):**

| Step | Description | Status |
|---|---|---|
| 1 | Data Collection & Column Selection (GSS Main + Episode + Census PUMF) | ✅ 100% (39/39 checks) |
| 2 | Data Harmonization — TUI_01 crosswalk, AT_HOME derivation, co-presence OR-merge | ✅ 100% (54/54 checks) |
| 3 | Merge & Temporal Tiling — 10-min HETUS → 30-min downsampling (48 slots/day); 64,061 respondents | ✅ 99% (81/82 checks) |
| 4 | Model 1: Conditional Transformer — cross-cycle DDAY augmentation; production model = J3 (4/4 gates) | ✅ COMPLETE |
| 5 | Census–GSS Probabilistic Linkage — 286,537 persons; 144,507 HH BEM frame (2005-2015; 2022/2030 refreshed 2026-07-09 to 144,465 HH) | ✅ COMPLETE |
| 6 | Model 2: Progressive Fine-Tuning + 2030 Forecast — DRIFT_MATRIX captures COVID-19 shift | ✅ COMPLETE |
| 7 | BEM Integration — schedule injection, metabolic map, HVAC setback | ✅ COMPLETE |
| 8 | BEM Simulation — HPC Monte Carlo campaigns; 8760-hour load profiles | ✅ COMPLETE |
| 9 | Activity-Driven End-Use Loads — equipment + lighting scaled by occupant activity | ✅ COMPLETE |

**Model architecture (Step 4 — J3):**
- Shared 6-layer encoder + 6-layer auto-regressive activity decoder + parallel non-AR binary heads
- `d_model = 384`; ~29.25M parameters
- Input: 48 slots × 11 features/slot (occACT ×14, AT_HOME, 9 co-presence columns)
- Output: synthetic schedules for unobserved DDAY_STRATA; ~192,183 augmented diary-days
- Validation gates passed: `act_JS` 0.019 / `AT_HOME_RMS` 4.57 pp / co-presence max ~2.03 pp
- MDLM/SEDD searched and rejected (best composite score, but only 2/4 hard gates)

**Key dataset:**
- `hetus_30min.csv`: 64,061 rows × 96 columns (48 activity + 48 AT_HOME slots per respondent)
- Resolution: 30-min (BEM/UBEM-ready); ~9× reduction in Transformer attention operations vs. 10-min

---

### 3rd Journal Paper — IN PROGRESS

**Title:** Longitudinal Occupancy-Driven Energy Demand in Canadian Mixed-Use Tall Buildings: GSS-Derived 4-Channel Occupancy Pipeline (2005–2030)

**Scope:** Extends the residential pipeline into a multi-channel generator targeting PNNL Tall and SuperTall mixed-use building prototypes (Calgary CZ7A, Montreal CZ6A).

#### Three-Leg Roadmap

| Leg | Channels | Status |
|---|---|---|
| Leg 1 | Residential only (AT_HOME replaces BEM baseline) | ✅ COMPLETE (2nd Journal) |
| Leg 2 | Residential + Office (AT_WORK modulates code-compliant densities) | ✅ COMPLETE — validated end-to-end, paper-ready |
| Leg 3 | + Retail + Hotel (full 4-channel mixed-use) | 🔄 DESIGN FROZEN — build begins at Step 3 |

#### 4-Channel Architecture (Leg 3 target)

| Channel | Data Source | Drives | Occupiable Area Share |
|---|---|---|---|
| **Residential** | GSS `LOCATION = 300` → `AT_HOME` | HighRiseApartment zones | SuperTall 24.1% · Tall 24.4% |
| **Office** | GSS workplace LOCATION codes → `AT_WORK` | OpenOffice / ClosedOffice / Conference / Classroom | SuperTall 30.3% · Tall 24.4% |
| **Retail** | GSS retail LOCATION codes + TUI_01 shopping → `AT_RETAIL` | Retail / Back_Space / Point_of_Sale / Entry | SuperTall 16.1% · Tall 24.4% |
| **Hotel** | StatCan monthly hotel-occupancy stats (Table 24-10-0048-01) | LargeHotel GuestRooms + amenities | SuperTall 29.5% · Tall 26.8% |

> Service / MEP / Circulation (~52% of gross floor area) stays on ASHRAE 90.1 / NECB17 defaults — not modulated.

**Key design decisions for Leg 2/3:**
- **Residential replaces** BEM baseline schedules (`Number_of_People = HHSIZE`)
- **Office, Retail, Hotel modulate** code-compliant peak densities (W/m², people/m²), preserving regulatory comparability
- Shared encoder between residential and office channels (universal time-of-day / day-of-week structure; only output heads are channel-specific)
- SLAW/UW loss weighting + PCGrad gradient surgery — mandatory (equal-weight MSE multi-head collapses COP peaks)
- WFH rate exposed as an explicit model-output scalar with 2030 sensitivity bands (Conservative 15–20% / Hybrid ~30% / Fully Hybrid ~40%)
- Hotel forecast uses SARIMA, not the Conditional Transformer (population-aggregate time series, not individual-respondent diary)
- Pareto model selection (Wasserstein + ACF-MAE + downstream peak) — never a single composite

**Target buildings:**
- `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf` (Montreal, 40,846 m²)
- `SuperTallBuilding_…_Z7A_v221.idf` (Calgary, 26,750 m²)

**Leg 2 (2-split) status — COMPLETE & paper-ready (July 2026):**

All nine pipeline steps are built and validated end-to-end for the two-channel (Residential + Office) model:

- **Two EnergyPlus campaigns drained clean** — residential (8,400 paired Monte Carlo cells: 4 archetypes × 6 climate zones × 7 scenarios × N=50) + office (252 deterministic runs: 3 archetypes × Tall/SuperTall × 6 climate zones × 7 scenarios).
- **7 scenarios per channel:** `2005 · 2010 · 2015 · 2022 · 2030-conservative · 2030-hybrid · 2030-fullyhybrid`.
- Residential schedules **replace** the BEM baseline; office presence **modulates** NECB/90.1 code-compliant peak densities (preserving regulatory comparability).
- **Step-8 simulation scorecard:** 46 PASS / 1 WARN / 13 INFO / 0 FAIL.
- **Step-9 bi-channel activity-driven loads scorecard:** 10 PASS / 1 WARN / 0 FAIL; gate **G8o** confirms the 2030 WFH bands produce a distinct office energy spread (office median EUI ≈ 173 kWh/m², in-band vs. the as-modelled NECB2020 / 90.1-2019 DOE-PNNL prototype).
- **Acceptance review verdict:** PAPER-READY — 0 FAIL across all four validation reports.

**Documentation:**
- [`3J_docs_occ_nTemp/Leg2_2-split/`](3J_docs_occ_nTemp/Leg2_2-split/) — 2-channel (Residential + Office) pipeline spec — **DESIGN FROZEN, pipeline COMPLETE**
- [`3J_docs_occ_nTemp/Leg3_4-split/`](3J_docs_occ_nTemp/Leg3_4-split/) — 4-channel (+ Retail + Hotel) pipeline spec — **DESIGN FROZEN** (all 13 reports integrated, 15 open decisions resolved; build begins at Step 3)

---

## Claude for OSS Application: Open-Source UBEM & Occupancy Framework

### 1. Project Overview & Vision

**Working title:** OpenUBEM-Occupancy

**Core technologies:** Python, `eppy`, `geomeppy`, EnergyPlus

This project aims to develop a comprehensive, fully open-source Urban Building Energy Modeling (UBEM) framework that integrates high-resolution occupancy data. While urban-scale energy modeling is growing quickly, many existing solutions are either proprietary, commercialized, or lack deep integration with complex occupancy behavior.

The goal is to build a Python-native framework on top of `eppy` and `geomeppy` that makes urban energy modeling more accessible, transparent, and extensible for the research community. By keeping the framework open-source, researchers worldwide can use, modify, and improve it without restrictive licensing.

### 2. About Me & Available Resources

I am a researcher at Concordia University specializing in building engineering and urban energy simulations. My background spans both UBEM and occupancy modeling, and I have authored several papers in these areas that inform the framework's development.

To support the computational demands of urban-scale simulations, I have access to substantial cloud-computing resources through Concordia University and Calcul Québec (Speed HPC cluster). With the infrastructure in place, the main bottleneck is rapid software development, structuring, and implementation.

### 3. How I Plan to Use Claude

- **Code development:** Draft, refactor, and debug Python workflows built on `eppy` and `geomeppy`, including automation around large numbers of EnergyPlus `.idf` files.
- **Data integration:** Build pipelines that clean, process, and map stochastic occupancy data into urban energy models.
- **Documentation and maintenance:** Generate docstrings, READMEs, and tutorials that keep the framework usable for the broader research community.
- **Research synthesis:** Help structure technical documentation and upcoming publications released alongside the software.

### 4. Expected Impact & Outputs

- a fully open-source, well-documented Python framework on GitHub for UBEM and occupancy integration
- open-access datasets and scripts that bridge stochastic human behavior and urban energy demand
- peer-reviewed academic publications that document the methodology, validate the framework, and support open-source collaboration in the built-environment sector

---

## Environment Notes

- **Python 3.9+** is expected.
- No `requirements.txt`-guaranteed lockfile is enforced across every stage; use the repo's existing environment before proposing new packages. Common dependencies: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `tqdm`, `scikit-learn`, `eppy`, `geomeppy`, `torch`/`tensorflow`, `pyreadstat`, `fpdf`.
- Occupancy data paths are configured in `eSim_occ_utils/occ_config.py` (override the root with `GSS_BASE_DIR`).
- EnergyPlus paths are configured in `eSim_bem_utils/config.py` (override with `ENERGYPLUS_DIR`); EnergyPlus **24.2.0** is assumed.
- **HPC execution** targets Concordia's **Speed cluster** (`o_iseri@speed.encs.concordia.ca`). All Python execution on the cluster must go through the scheduler (`sbatch`) — bare `python3` and blocking `srun` on the login node are prohibited.

---

## Repository Conventions

- This is **research code**: scripts are run one at a time, not through a single automated pipeline. Do not assume an end-to-end command exists.
- Some scripts still reference a legacy `BEM_Setup/` folder while the real top-level directory is `0_BEM_Setup/`. Verify path assumptions before editing BEM code.
- **Do not modify** these production files unless explicitly instructed — they are tied to published results:
  - `eSim_occ_utils/25CEN22GSS_classification/eSim_datapreprocessing.py`
  - `eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py`
  - `eSim_occ_utils/25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py`
- **Sensitive / expensive artifacts** — treat carefully, do not overwrite without intent:
  - raw microdata under `0_Occupancy/DataSources_*`
  - trained models under `0_Occupancy/saved_models_cvae/`
  - large generated result trees under `0_BEM_Setup/` (git-ignored)
- Commit messages follow `[type]: Brief description`, where `type` ∈ `data · ml · pipeline · bem · fix · docs`.
- Agent/workflow conventions are documented in [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md).

---

## Citation, License & Contact

**Citation:**

```
Koraliseri, O. (2026). occModeling / eSim: Occupancy-Based Building Energy Simulation Framework.
GitHub: https://github.com/orcunkoraliseri/GSSCanada
```

**License:** Research use only. Contact the author for commercial applications.

**Contact:** Orcun Koraliseri · orcunkoral.oseri@concordia.ca · [@orcunkoraliseri](https://github.com/orcunkoraliseri)

---

*Last updated: 9 July 2026*
