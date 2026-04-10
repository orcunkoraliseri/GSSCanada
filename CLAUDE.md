# CLAUDE.md — Occupancy Modeling Project (occModeling)

## Project Overview

This project generates realistic occupancy schedules for Canadian residential buildings to use as inputs in EnergyPlus building energy models (BEM). It does this by aligning Statistics Canada Census demographic data with General Social Survey (GSS) time-use data across multiple census years, then using machine learning to forecast synthetic future populations.

**Research context:** Postdoctoral research for eSim 2026 paper — "Longitudinal Occupancy-Driven Energy Demand in Canadian Residential Buildings"

**Platform:** macOS, Python 3.9+, scripts run manually (not via CLI automation)

---

## Project Structure

```
occModeling/
├── 0_Occupancy/                    # Raw data inputs and processed outputs
│   ├── DataSources_CENSUS/         # Census PUMF files (2006, 2011, 2016, 2021)
│   ├── DataSources_GSS/            # GSS time-use survey files (2005–2022)
│   ├── Outputs_06CEN05GSS/         # Outputs: 2006 Census + 2005 GSS
│   ├── Outputs_11CEN10GSS/         # Outputs: 2011 Census + 2010 GSS
│   ├── Outputs_16CEN15GSS/         # Outputs: 2016 Census + 2015 GSS
│   ├── Outputs_Aligned/            # Cross-year aligned datasets
│   └── saved_models_cvae/          # Saved ML model weights
│
├── 0_BEM_Setup/                    # EnergyPlus IDF files, weather data, sim results
│
├── eSim_occ_utils/                 # Core occupancy modeling library
│   ├── occ_config.py               # Cross-platform path config (macOS/Windows)
│   ├── gss_reader.py               # GSS file parser (.sas7bdat, .sps formats)
│   ├── cen_reader.py               # Census DTYPE reader and validator
│   ├── 06CEN05GSS/                 # Pipeline: 2006 Census + 2005 GSS
│   ├── 11CEN10GSS/                 # Pipeline: 2011 Census + 2010 GSS
│   ├── 16CEN15GSS/                 # Pipeline: 2016 Census + 2015 GSS
│   ├── 25CEN22GSS_classification/  # Pipeline: 2022 Census + ML classification (active)
│   ├── plotting/                   # 15+ visualization scripts
│   └── docs_pipelines/             # Pipeline documentation
│
├── eSim_bem_utils/                 # EnergyPlus BEM integration
│   ├── main.py                     # Menu-driven entry point
│   ├── simulation.py               # EnergyPlus runner
│   ├── idf_optimizer.py            # IDF preprocessing (inject meters/outputs)
│   ├── integration.py              # Link occupancy schedules to BEM
│   └── plotting.py / reporting.py  # Results extraction and visualization
│
├── eSim_docs_occ_utils/            # Occupancy pipeline documentation (Markdown + PDF)
├── eSim_docs_bem_utils/            # BEM documentation
├── eSim_writing/                   # Academic writing (methodology, results)
├── eSim_tests/                     # Test suite and benchmarks
├── eSim_README.md                  # Main project overview
└── run_bem.py                      # BEM workflow entry point
```

---

## Core Pipelines

### Occupancy Pipeline (per census year)
Each pipeline follows the same 5-step structure:

```
Census PUMF data
    ↓ *_alignment.py          — Harmonize demographic columns between Census & GSS
    ↓ *_ProfileMatcher.py     — Tiered matching (Tier 1–4) of Census agents to GSS schedules
    ↓ *_HH_aggregation.py     — Aggregate individual profiles to household level
    ↓ *_occToBEM.py           — Convert 5-min ABM schedules → hourly BEM format
    ↓ *_main.py               — Orchestration script (runs all above)
```

**Matching tiers:**
- Tier 1: Perfect match on all demographic columns
- Tier 2: Match on core columns (28.4% weekday, 41.5% weekend)
- Tier 3: Match on key columns only
- Tier 4: Fail-safe fallback — measured rates: 2005 WD 0.53% / WE 0.29%; 2010 WD 1.14% / WE 4.41%; 2015 WD 0.30% / WE 0.26%; 2022 WD 2.91% / WE 4.84% (see eSim_tests/task33_tier_summary_all_cycles.csv). The original "< 0.5%" claim is a prospective target, not a measured outcome.

### 25CEN22GSS Classification Pipeline (active ML pipeline)
Located in `eSim_occ_utils/25CEN22GSS_classification/`

**Three source files (do not modify without explicit instruction):**
- `eSim_datapreprocessing.py` — Census data ingestion and cleaning
- `eSim_dynamicML_mHead.py` — Main ML pipeline: CVAE architecture, household assembly, profile matching, BEM conversion
- `eSim_dynamicML_mHead_alignment.py` — GSS-to-Census demographic harmonization

**11-step pipeline organized in 3 phases:**
- **Step 1** (run_step1.py): Data prep → CVAE training → forecasting 2025/2030 → visual validation
- **Step 2** (run_step2.py): Household assembly → Profile Matcher → Post-processing → HH Aggregation
- **Step 3** (run_step3.py): OCC to BEM Input conversion

Modular runner plan documented in `docs_classification/`.

---

## Configuration

### Path Configuration
`eSim_occ_utils/occ_config.py` handles cross-platform paths:
- macOS base: `/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/0_Occupancy`
- Override with env var: `GSS_BASE_DIR`

`eSim_bem_utils/config.py` handles EnergyPlus paths:
- macOS: `/Applications/EnergyPlus-24-2-0`
- Override with env var: `ENERGYPLUS_DIR`

---

## Coding Standards

- **Style:** PEP 8, plain readable code (no over-engineering)
- **No premature abstractions:** Add helpers only when used in 2+ places
- **No extra features:** Only change what was asked; don't refactor surrounding code
- **Comments:** Explain *why*, not *what*
- **Do not modify existing source files** in `25CEN22GSS_classification/` unless explicitly asked — the modular runner pattern sits on top of them

## Prompt Format

### Prompt Intake Rule
Before acting on any user request, normalize it into this shape:
- `Setting the stage`: who is acting, what the objective is, and any relevant context
- `Defining the task`: the exact action requested, such as write, analyze, build, review, or debug
- `Specifying rules`: style, tone, constraints, examples, and other preferences
- If the user omits a part, infer it from the surrounding context
- Then carry out the request directly using that normalized interpretation

### Task List Format
When preparing a task list as a separate document or as an additional chapter inside a document, organize each task in a way that is easy to understand and step-by-step using this structure:
- aim of task
- what to do
- how to do
- why to do this task
- what will impact on
- what are the step(s)/sub-step(s)
- what to expect as result
- if possible or needed how to test

Keep the task list clear, ordered, and consistent across documents.

---

## Key Dependencies

```
pandas, numpy, scipy, matplotlib, seaborn
tqdm, eppy
scikit-learn (Random Forest for DTYPE expansion)
torch or tensorflow (CVAE in 25CEN22GSS classification)
```

No requirements.txt currently exists. Dependencies are documented in `eSim_README.md`.

---

## Data Notes

- Census data: Statistics Canada PUMF files (not publicly redistributable, stored locally)
- GSS data: General Social Survey time-use files (.sas7bdat format)
- Outputs are 5-minute resolution activity grids → converted to 48-slot (30-min) or hourly BEM schedules
- Key validated metrics: 28,454 households sampled; work duration ~542 min/day for employed agents

---

## BEM Integration

EnergyPlus 24.2 is used for simulation. Occupancy schedules generated by the pipeline are injected into IDF files via `eSim_bem_utils/integration.py`. Simulation outputs are extracted from `eplusout.sql` for EUI analysis.

---

## Git Commit Style

```
[type]: Brief description
- Detail 1
- Detail 2
```

Types: `[data]`, `[ml]`, `[pipeline]`, `[bem]`, `[fix]`, `[docs]`

---

## Session Tips

- Scripts are run manually, one at a time — suggest individual script runs, not bash pipelines
- When referencing code, include `file_path:line_number` for easy navigation
- Keep explanations plain-language; this researcher codes pragmatically, not as a software engineer
- Before suggesting changes to any file, read it first
