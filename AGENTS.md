# AGENTS.md

## Project Purpose
- Research code for generating synthetic residential occupancy schedules for Canadian housing from Census + GSS time-use data, then using those schedules in EnergyPlus building energy simulations.
- The repo is script-driven, not package-driven. Most workflows are run manually from specific Python files.

## Repository Map
- `0_Occupancy/`: raw Census/GSS inputs, aligned datasets, pipeline outputs, saved CVAE models.
- `0_BEM_Setup/`: IDF/EPW assets, templates, neighbourhood/building models, simulation outputs. Mostly ignored in git.
- `eSim_occ_utils/`: occupancy pipelines and helpers.
- `eSim_occ_utils/06CEN05GSS/`, `11CEN10GSS/`, `16CEN15GSS/`: year-pair pipelines with alignment, profile matching, aggregation, and BEM conversion stages.
- `eSim_occ_utils/25CEN22GSS_classification/`: current ML-based classification pipeline. `run_step1.py`, `run_step2.py`, and `run_step3.py` wrap the legacy source.
- `eSim_bem_utils/`: BEM schedule injection, IDF prep, simulation, plotting, reporting, and menu entrypoint.
- `eSim_tests/`: ad hoc validation scripts plus a few unit/integration-style checks.
- `eSim_docs_*`, `2J_docs_occ_nTemp/`, `eSim_writing/`: documentation, paper support material, and working research outputs.

## Main Entry Points
- Occupancy pipelines:
  - `python3 eSim_occ_utils/06CEN05GSS/06CEN05GSS_main.py --help`
  - `python3 eSim_occ_utils/11CEN10GSS/11CEN10GSS_main.py --help`
  - `python3 eSim_occ_utils/16CEN15GSS/16CEN15GSS_main.py --help`
- Classification pipeline:
  - `python3 eSim_occ_utils/25CEN22GSS_classification/main_classification.py`
  - This file is flag-driven. Toggle `RUN_*` booleans instead of expecting a full CLI.
- BEM workflow:
  - `python3 run_bem.py`
  - This launches `eSim_bem_utils.main`, which is interactive/menu-driven.

## Environment Setup
- Python 3.9+ expected.
- Common dependencies seen in code: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `tqdm`, `scikit-learn`, `eppy`, `tensorflow`, `fpdf`.
- No `requirements.txt` or `pyproject.toml` is present. Do not invent one unless asked.
- Path configuration:
  - Occupancy data root comes from `eSim_occ_utils/occ_config.py`.
  - Override with `GSS_BASE_DIR` if the local `0_Occupancy` path differs.
  - EnergyPlus path comes from `eSim_bem_utils/config.py`.
  - Override with `ENERGYPLUS_DIR` if EnergyPlus is not installed at the default location.
- EnergyPlus 24.2 is the assumed version on macOS/Windows.

## Repo-Specific Working Rules
- Read `CLAUDE.md` for additional project context before making broad changes.
- Keep changes local and pragmatic. This codebase is script-oriented and researcher-maintained; avoid unnecessary abstraction or broad refactors.
- Prefer editing wrappers, controllers, or adjacent utilities over rewriting established pipeline code.
- When a user writes a free-form prompt, normalize it into this structure before acting:
  - `Setting the stage`: role, objectives, and any project context
  - `Defining the task`: the action requested, such as write, analyze, build, or debug
  - `Specifying rules`: style, tone, constraints, and any examples
  - Then carry out the request using that structured interpretation
- Treat these files as sensitive unless the task explicitly targets them:
  - `eSim_occ_utils/25CEN22GSS_classification/eSim_datapreprocessing.py`
  - `eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py`
  - `eSim_occ_utils/25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py`
- Use `occ_config.py` and `eSim_bem_utils/config.py` for path logic instead of hardcoding new absolute paths.
- Scripts are usually run one at a time. Do not assume there is a single automated end-to-end command.

## Prompt Intake Rule
- Before acting on any user request, normalize it into this shape:
  - `Setting the stage`: who is acting, what the objective is, and any relevant context
  - `Defining the task`: the exact action requested, such as write, analyze, build, review, or debug
  - `Specifying rules`: style, tone, constraints, examples, and other preferences
- If the user omits a part, infer it from the surrounding context.
- Then carry out the request directly using that normalized interpretation.

## Task List Format
- When preparing a task list as a separate document or as an additional chapter inside a document, organize each task easy to understand, step-by-step using this structure:
  - aim of task
  - what to do
  - how to do
  - why to do this task
  - what will impact on
  - what are the step(s)/sub-step(s)
  - what to expect as result
  - if possible or needed how to test
- Keep the task list clear, ordered, and consistent across documents.

## Validation Expectations
- Use the narrowest validation that matches the change.
- Safe checks:
  - `python3 ... --help` for CLI controllers
  - targeted unit or script runs in `eSim_tests/`
- Heavy checks:
  - anything that needs local Census/GSS data
  - anything that runs EnergyPlus or writes large outputs under `0_BEM_Setup/` or `0_Occupancy/`
- If you change BEM integration, prefer targeted checks in `eSim_tests/` before attempting full simulations.
- The current repo state is not fully green: `python3 -m unittest eSim_tests.test_integration_logic` fails at present because it does not find the projected electric equipment schedule object. Do not claim the suite is clean without rerunning and confirming.

## Constraints And Sensitive Data
- Raw Statistics Canada and GSS microdata under `0_Occupancy/DataSources_*` are sensitive and large. Do not rename, move, delete, or rewrite them casually.
- `0_BEM_Setup/` is ignored in git and holds large generated artifacts. Avoid deleting or regenerating large result trees unless required.
- Saved model artifacts under `0_Occupancy/saved_models_cvae/` are expensive outputs; do not overwrite them without intent.
- Watch for legacy path inconsistencies: some scripts still refer to `BEM_Setup` while the real top-level folder is `0_BEM_Setup`. Verify path assumptions before editing BEM code.
