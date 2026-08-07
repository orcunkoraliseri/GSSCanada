# Progress Log: `plots_tempo_Nontempo.md`

Date: 2026-04-03

## Task 1: Load and validate all cycle CSV data
Status: Completed

Progress:
- Implemented shared loader in `eSim_occ_utils/plotting/cross_cycle_plot_utils.py`.
- Used `Path(__file__).resolve().parent.parent.parent` for base-path resolution.
- Added `REQUIRED_COLUMNS` validation and `load_all_cycles(columns_needed)`.
- Verified all five CSV files were found and readable.
- Printed per-cycle row counts and unique household counts during script execution.

Observed counts:
- 2005: 1,365,840 rows, 28,455 households
- 2010: 1,559,040 rows, 32,480 households
- 2015: 1,495,824 rows, 31,163 households
- 2022: 1,771,632 rows, 36,909 households
- 2025: 15,504 rows, 323 households

## Task 2: Build non-temporal category harmonization logic
Status: Completed

Progress:
- Implemented harmonization in `build_non_temporal_distributions(...)`.
- Deduplicated to one row per `SIM_HH_ID` before counting non-temporal variables.
- Built union category sets for `DTYPE`, `BEDRM`, and `ROOM`.
- Applied explicit region normalization for `PR` to align real data with the target comparison categories:
  - `Atlantic` and `Eastern Canada` -> `Atlantic/Eastern Canada`
  - `BC` and `British Columbia` -> `BC`
  - `Alberta` -> `Prairies`
- Applied explicit `DTYPE` cleanup for the stray `2022` category value `8` -> `OtherDwelling`.
- Normalized all counts to percentages.

## Task 3: Implement `plot_nontemporal_comparison.py`
Status: Completed

Progress:
- Created `eSim_occ_utils/plotting/plot_nontemporal_comparison.py`.
- Generated a 4x5 comparison figure with shared row-wise y-axes.
- Used green-teal colors for 2005-2022 and orange for 2025.
- Added cycle headers and household-count annotations.
- Saved output:
  - `eSim_occ_utils/plotting/BEM_NonTemporal_CrossCycle_Comparison.png`

## Task 4: Compute occupancy and metabolic rate distributions for temporal Section A & B
Status: Completed

Progress:
- Implemented histogram and KDE preparation in `compute_distribution_histograms(...)`.
- Occupancy histograms use 20 bins on `[0, 1]`.
- Metabolic histograms use 50 bins on `[0, 250]` after filtering `Metabolic_Rate > 0`.
- Used `scipy.stats.gaussian_kde` for overlays.

## Task 5: Sample and prepare household-level data for heatmap visualization
Status: Completed

Progress:
- Implemented reproducible household sampling in `prepare_heatmap_matrices(...)`.
- Used `seed=42`.
- Sampled up to 150 unique households per cycle.
- Pivoted to household-by-hour matrices for weekday and weekend.
- Sorted households by mean occupancy during hours `9` to `16`.

## Task 6: Implement `plot_temporal_comparison.py` (primary figure)
Status: Completed

Progress:
- Created `eSim_occ_utils/plotting/plot_temporal_comparison.py`.
- Generated the primary temporal figure with:
  - Row 1: occupancy histograms
  - Row 2: metabolic histograms
  - Rows 3-4: weekday heatmap slices
  - Rows 5-6: weekend heatmap slices
- Used actual 6x5 axes by splitting each heatmap into upper/lower household slices for readability.
- Added a shared heatmap colorbar.
- Saved output:
  - `eSim_occ_utils/plotting/BEM_Temporal_CrossCycle_Comparison.png`

## Task 7: Implement spaghetti plot (supplementary figure)
Status: Completed

Progress:
- Added supplementary spaghetti plotting to `plot_temporal_comparison.py`.
- Used up to 80 sampled households per cycle/day type.
- Overlaid full-population mean and interquartile band.
- Saved output:
  - `eSim_occ_utils/plotting/BEM_Temporal_Spaghetti_Comparison.png`

## Task 8: Final styling pass and paper-readiness check
Status: Completed with automated checks

Progress:
- Confirmed all three PNG outputs exist.
- Confirmed all outputs were saved at ~300 DPI.
- Confirmed output pixel sizes:
  - `BEM_NonTemporal_CrossCycle_Comparison.png`: `6289 x 4109`
  - `BEM_Temporal_CrossCycle_Comparison.png`: `6616 x 5076`
  - `BEM_Temporal_Spaghetti_Comparison.png`: `6312 x 2349`
- Applied consistent historical vs. 2025 color treatment across figures.

Notes:
- Automated artifact checks passed.
- Manual visual review in an image viewer was not performed from the terminal session; if needed, that can be done as a follow-up pass.

## Task 9: Visual improvements (post-review)
Status: Completed

Date: 2026-04-03

Changes applied based on visual review of generated figures:

### Non-temporal plot (`plot_nontemporal_comparison.py`)
- Reduced bar opacity from 1.0 to 0.7 (`alpha=0.7`) for softer colors
- Reduced vertical spacing between subplot rows from `hspace=0.48` to `hspace=0.30`
- Fixed cycle titles: replaced `fig.text()` annotations (which were misaligned/overlapping) with centered `ax.set_title()` on row-0 axes, formatted as "YEAR\nN=XX,XXX"
- Changed PR x-tick label from "Atlantic/Eastern Canada" to "Atlantic" — updated canonical mapping in `cross_cycle_plot_utils.py` (`REGION_CANONICAL_MAP` and `REGION_ORDER`)

### Temporal plot (`plot_temporal_comparison.py`)
- Removed occupancy distribution row (Section A) and metabolic distribution row (Section B) entirely
- Reduced figure from 6 rows to 4 rows (heatmaps only: 2 weekday + 2 weekend)
- Minimized inter-row spacing (`hspace=0.08`) to maximize heatmap subplot size
- Reduced figure height from 18 to 12 inches; adjusted margins and colorbar placement
- Removed unused imports (`compute_distribution_histograms`, `FORECAST_COLOR`) and the `_plot_hist_row` helper function

### Spaghetti plot
- No changes (confirmed acceptable as-is)

### Files modified
- `cross_cycle_plot_utils.py`: region naming ("Atlantic/Eastern Canada" → "Atlantic")
- `plot_nontemporal_comparison.py`: opacity, spacing, title alignment
- `plot_temporal_comparison.py`: removed histogram rows, tighter layout
