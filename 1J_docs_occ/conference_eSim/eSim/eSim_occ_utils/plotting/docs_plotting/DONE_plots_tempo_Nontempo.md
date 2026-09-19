# Implementation Plan: Cross-Cycle Comparison Plots (Temporal & Non-Temporal)

**Purpose:** Two Python scripts to compare occupancy-derived BEM schedules across all five census/GSS cycles (2005, 2010, 2015, 2022, 2025-classified) for use in the eSim 2026 research paper.

**Output location:** `eSim_occ_utils/plotting/`

---

## Data Sources (all cycles share the same 12-column CSV schema)

| Cycle Label | CSV Path |
|---|---|
| 2005 | `0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct.csv` |
| 2010 | `0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv` |
| 2015 | `0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct.csv` |
| 2022 | `0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct.csv` |
| 2025 | `0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv` |

**Shared columns:** `SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, Occupancy_Schedule, Metabolic_Rate`

**Note:** 2025 is the classified/forecasted cycle and should be visually distinguished (e.g., red-orange palette) from the four historical GSS-based cycles (green-teal palette), consistent with existing plots in this directory.

---

## Script 1: `plot_nontemporal_comparison.py`

### Goal
Compare the four non-temporal distribution subplots across all five cycles side-by-side. Each column is a cycle, each row is a variable.

### Layout: 4 rows x 5 columns grid (20 subplots)

| | 2005 | 2010 | 2015 | 2022 | 2025 |
|---|---|---|---|---|---|
| **Row 1** | DTYPE | DTYPE | DTYPE | DTYPE | DTYPE |
| **Row 2** | BEDRM | BEDRM | BEDRM | BEDRM | BEDRM |
| **Row 3** | ROOM | ROOM | ROOM | ROOM | ROOM |
| **Row 4** | PR | PR | PR | PR | PR |

### Implementation Details

#### Row 1 — Dwelling Type (DTYPE)
- Bar chart of DTYPE value counts per cycle
- **Key challenge:** DTYPE categories differ across cycles (2006/2016 use SemiD, SingleD, MidRise, HighRise, Attached, OtherA, DuplexD, Movable; 2011/2021 use Apartment, OtherDwelling, SemiD and fewer categories)
- **Approach:** Use union of all DTYPE values across all cycles as x-axis, with missing categories shown as zero-height bars. This makes the category shifts immediately visible
- Normalize y-axis to proportions (%) rather than raw counts so cycles with different sample sizes are comparable
- Annotate each subplot header with total household count N

#### Row 2 — Bedroom Count (BEDRM)
- Bar chart of BEDRM value counts
- **Key challenge:** 2006/2016 have only 3 categories (1, 2, 3), while 2011/2021 have finer granularity (0, 1, 2, 3, 4, 5, 6, 7, 8)
- **Approach:** Use union of all BEDRM values as x-axis; normalize to %
- Color bars by BEDRM value (consistent legend across panels)

#### Row 3 — Room Count (ROOM)
- Bar chart of ROOM value counts
- **Key challenge:** 2006/2016 use half-integer bins (0.5, 1.0, 1.5, ..., 4.5) while 2011/2021 use integers (0, 1, 2, ..., 12)
- **Approach:** Shared x-axis range covering union of all bin values; normalize to %

#### Row 4 — Province/Region (PR)
- Bar chart of PR value counts
- Region categories are fairly stable across cycles (Quebec, Ontario, Prairies, Atlantic/Eastern Canada, BC)
- Normalize to %; sort regions consistently (e.g., West-to-East geographic order)

### Styling
- Figure size: ~22 x 14 inches (landscape, paper-ready)
- Historical cycles (2005-2022): each cycle gets a distinct single color from a sequential green-teal palette
- 2025 classified: red-orange palette
- Shared y-axis per row (percentage) to allow direct visual comparison
- Column headers: cycle years; Row headers: variable names
- Font sizes appropriate for journal figures (12-14pt titles, 10pt tick labels)

### Output
- `BEM_NonTemporal_CrossCycle_Comparison.png`

---

## Script 2: `plot_temporal_comparison.py`

### Goal
Compare temporal (time-varying) occupancy characteristics across all five cycles. Focus on:
1. Occupancy fraction distributions (histogram comparison)
2. Metabolic rate distributions (histogram comparison)
3. Sample household schedules — creative multi-household visualizations showing weekday/weekend differences between cycles

**Skip:** Average presence schedule and average metabolic rate trends (already covered by `BEM_Presence_Evolution_Comparison.png` and `BEM_Activity_Metabolic_Comparison.png`).

### Layout: Multi-panel figure with 3 sections

---

### Section A — Occupancy Fraction Distributions (1 row x 5 columns)

- One subplot per cycle showing the histogram of `Occupancy_Schedule` values (all hours pooled)
- Consistent x-axis (0 to 1), consistent y-axis (% of observations)
- Overlay KDE curve on each histogram for visual smoothness
- This reveals how the bimodal pattern (empty vs. full occupancy) evolves across decades
- **Key insight to highlight:** The relative weight of the 0.0 peak (away) vs. the 1.0 peak (full occupancy) shifts across cycles, reflecting changing work-from-home and lifestyle patterns

### Section B — Metabolic Rate Distributions (1 row x 5 columns)

- One subplot per cycle showing the histogram of `Metabolic_Rate` values (only rows where Metabolic_Rate > 0, i.e., occupied hours)
- Consistent x-axis (0 to 250 W), consistent y-axis (%)
- Overlay KDE curve
- The spike around 65-75 W (sleeping/sedentary) vs. the shoulder at 100-175 W (active) tells the story of changing activity patterns

---

### Section C — Sample Household Visualizations (creative ideas)

This section is the most important for showing how individual household schedules differ between cycles. Below are **four visualization ideas** — implement the most effective 2-3 depending on paper space.

#### Idea C1: Spaghetti Plot (Recommended — high impact)
**Layout:** 2 rows (Weekday, Weekend) x 5 columns (cycles)
- For each cycle, randomly sample ~50-100 households
- Plot each household's 24-hour `Occupancy_Schedule` as a semi-transparent line (alpha=0.05-0.10)
- Overlay the population mean as a bold line
- This creates a "cloud" that reveals:
  - How diverse household schedules are within each cycle
  - Whether certain cycles have tighter or looser clustering around the mean
  - The spread of departure/return times
- **Color:** Light gray or cycle-specific light shade for individual lines; bold cycle color for the mean

#### Idea C2: Heatmap Grid (Recommended — compact, information-dense)
**Layout:** 2 rows (Weekday, Weekend) x 5 columns (cycles)
- For each cycle, sample ~100-200 households
- Each subplot is a heatmap: x-axis = Hour (0-23), y-axis = sampled household index, color = `Occupancy_Schedule` (0=away in white, 1=full in dark green/orange)
- Sort households by a summary metric (e.g., mean daily occupancy, or morning departure hour) so patterns emerge as gradients
- This visualization instantly shows:
  - The fraction of households that are "always home" vs. "classic 9-to-5 away"
  - How departure/return time distributions differ across cycles
  - Emergence of work-from-home patterns in 2022 and 2025

#### Idea C3: Ridgeline / Joy Plot (Compact alternative)
**Layout:** 2 panels (Weekday, Weekend), each containing 5 stacked ridgelines
- For each cycle and each hour (0-23), compute the distribution of `Occupancy_Schedule` across all households
- Select 6-8 key hours (e.g., 0, 4, 8, 10, 12, 14, 17, 20, 23) to avoid clutter
- Stack the density curves vertically by cycle (2005 at bottom, 2025 at top)
- This reveals how the occupancy distribution at each hour has shifted over 20 years
- Particularly effective at showing the "flattening" of the daytime dip in 2022/2025

#### Idea C4: Archetype Comparison Panel
**Layout:** 3 rows (archetypes) x 5 columns (cycles) x 2 sub-rows (Weekday/Weekend)
- Define 3 household archetypes based on HHSIZE:
  - Single-person (HHSIZE=1)
  - Couple (HHSIZE=2)
  - Family (HHSIZE=3+)
- For each archetype and cycle, compute the mean occupancy profile with CI bands
- Side-by-side comparison reveals how different household structures respond to societal shifts differently
- E.g., single-person households may show the strongest work-from-home shift

---

### Recommended Combination for Paper

**Primary figure (full-page):**
- Section A (occupancy distributions) + Section B (metabolic distributions) + Idea C2 (heatmap) 
- Layout: 6 rows x 5 columns
- Rows 1-2: Sections A-B (distributions)
- Rows 3-4: Heatmap weekday
- Rows 5-6: Heatmap weekend

**Supplementary / alternative figure:**
- Idea C1 (spaghetti plot) as standalone 2x5 figure — excellent for presentations

**Optional compact alternative:**
- Idea C3 (ridgeline) if paper space is limited — packs the most information into the smallest area

### Styling (Temporal)
- Figure size: ~22 x 18 inches for the primary figure
- Historical cycles: green-teal gradient palette (matching existing plots)
- 2025 classified: red-orange palette
- Heatmaps: `Greens` colormap for historical, `Oranges` for 2025
- All panels share consistent x-axes (Hour 0-23) where applicable
- Sample seed fixed (e.g., `np.random.seed(42)`) for reproducibility

### Output
- `BEM_Temporal_CrossCycle_Comparison.png` (primary)
- `BEM_Temporal_Spaghetti_Comparison.png` (supplementary, if implemented)

---

## Implementation Notes

1. **Data loading:** Follow the pattern in `plot_presence_evolution_v2.py` — use `pd.read_csv(usecols=[...])` to avoid loading unnecessary columns from the large 25pct CSVs
2. **Performance:** The 25pct CSVs are 77-102 MB each. For the heatmap and spaghetti plots, sample households *after* loading, not during. Consider using `nrows` or chunked reading if memory is an issue
3. **DTYPE harmonization (non-temporal):** Build a union set of all category values across cycles before plotting, so the x-axis is consistent
4. **Normalization:** Always normalize counts to percentages for cross-cycle comparison since sample sizes differ dramatically (15K for 2025 vs. 1.5M+ for historical 25pct samples)
5. **Household sampling for Section C:** Extract unique `SIM_HH_ID` values first, then sample from those, then filter the full dataframe — avoids bias toward households with more rows
6. **2025 visual distinction:** The 2025 column should always use a warm palette (reds/oranges) to signal that it is ML-classified/forecasted rather than survey-derived

---

## Summary Table

| Script | Output PNG | # Subplots | Key Comparison |
|---|---|---|---|
| `plot_nontemporal_comparison.py` | `BEM_NonTemporal_CrossCycle_Comparison.png` | 20 (4x5) | DTYPE, BEDRM, ROOM, PR distributions |
| `plot_temporal_comparison.py` | `BEM_Temporal_CrossCycle_Comparison.png` | 30 (6x5) | Occupancy/metabolic histograms + household heatmaps |
| (optional) | `BEM_Temporal_Spaghetti_Comparison.png` | 10 (2x5) | Individual household schedule clouds |

---

## Task List

---

### Task 1: Load and validate all cycle CSV data

**Aim:** Establish a reliable, shared data-loading module that both scripts can use, and confirm all five CSV files are readable with consistent column schemas.

**What to do:** Write a data-loading function (or shared config block) that reads each of the five `BEM_Schedules` CSV files, validates column presence, and returns a dictionary keyed by cycle label.

**How to do:**
1. Define the five file paths using `Path(__file__).resolve().parent.parent.parent` as `BASE_DIR` (same pattern as `plot_presence_evolution_v2.py`)
2. For each file, call `pd.read_csv(file_path, usecols=[...])` — load only the columns needed for the calling script
3. Print row counts and unique `SIM_HH_ID` counts per cycle for verification
4. Return a dict: `{'2005': df_2005, '2010': df_2010, ...}`

**Why:** Both scripts need the same data. A consistent loading pattern avoids bugs from mismatched paths or missing columns, and the column validation catches schema drift early.

**Impact:** Foundation for all subsequent tasks. If this fails, nothing else works.

**Steps:**
1. Copy the path config block from `plot_presence_evolution_v2.py` as a starting template
2. Add all 12 column names to a `REQUIRED_COLUMNS` list
3. Write `load_all_cycles(columns_needed)` function that loads each CSV with only the requested columns
4. Add a check: if any file is missing, print a warning and skip that cycle (do not crash)
5. Print summary table: cycle, file found (yes/no), row count, unique household count

**Expected result:** Console output confirming all 5 files loaded successfully with their respective row counts (~1.3M-1.7M for historical 25pct samples, ~15K for 2025).

**How to test:** Run the loading function standalone. Verify row counts match the known file sizes. Verify that column names match `REQUIRED_COLUMNS` for each cycle.

---

### Task 2: Build non-temporal category harmonization logic

**Aim:** Create a harmonization step that aligns the differing category values (DTYPE, BEDRM, ROOM, PR) across all five cycles so they can be plotted on shared axes.

**What to do:** For each of the four non-temporal variables, compute the union of all unique values across all cycles. Map each cycle's data to this unified category set.

**How to do:**
1. After loading all cycles, extract unique values for DTYPE, BEDRM, ROOM, and PR from each cycle
2. Compute the union: `all_dtypes = sorted(set().union(*[df['DTYPE'].unique() for df in data.values()]))`
3. For each cycle, compute value counts and reindex to the union set, filling missing categories with 0
4. Normalize to percentages: `counts / counts.sum() * 100`

**Why:** DTYPE categories differ significantly (e.g., 2006 has 8 types, 2021 has 3 types). Without harmonization, bar charts would have different x-axes and visual comparison would be impossible. The zero-height bars for missing categories are themselves informative — they show which housing types were not tracked or not present in that cycle.

**Impact:** Directly determines the quality and interpretability of `plot_nontemporal_comparison.py` (Row 1-4).

**Steps:**
1. Load all cycles with columns `['SIM_HH_ID', 'DTYPE', 'BEDRM', 'ROOM', 'PR']`
2. For each variable, deduplicate per household first (each household has 48 rows — take the first occurrence)
3. Compute union of categories across all 5 cycles
4. For ROOM, decide on bin strategy: if a cycle uses half-integers and another uses integers, keep them as-is (the union will include both)
5. For PR, define a fixed geographic ordering: `['BC', 'Prairies', 'Ontario', 'Quebec', 'Atlantic/Eastern Canada']`
6. Build a normalized percentage DataFrame for each variable per cycle

**Expected result:** Four dictionaries (one per variable), each containing 5 Series (one per cycle) indexed by the unified category set, with values in percentages summing to 100%.

**How to test:** For each cycle, verify percentages sum to ~100%. Verify that the union set includes all categories found in any individual cycle. Spot-check a few values against the raw per-cycle non-temporal PNG plots.

---

### Task 3: Implement `plot_nontemporal_comparison.py`

**Aim:** Produce a single publication-ready figure (`BEM_NonTemporal_CrossCycle_Comparison.png`) with a 4x5 grid comparing DTYPE, BEDRM, ROOM, and PR distributions across all five cycles.

**What to do:** Write the full plotting script that loads data (Task 1), harmonizes categories (Task 2), and renders the 20-subplot figure.

**How to do:**
1. Create `eSim_occ_utils/plotting/plot_nontemporal_comparison.py`
2. Use `matplotlib.gridspec.GridSpec(4, 5)` for the layout
3. Loop: for each row (variable) and each column (cycle), plot a bar chart of the normalized percentages
4. Apply styling: palette, font sizes, shared y-axes per row, column/row headers

**Why:** The non-temporal distributions reveal how the Canadian housing stock composition has changed across census cycles (e.g., shift from SingleD-dominated to Apartment-dominated, bedroom count granularity changes, regional population shifts). These are key contextual figures for the paper.

**Impact:** Produces a core figure for the paper's methodology or data description section. Also serves as a quality check — if distributions look unreasonable, it flags upstream pipeline issues.

**Steps:**
1. Set up the script with path config, imports, and constants (cycle labels, colors, figure size)
2. Load data using the pattern from Task 1 — load columns `['SIM_HH_ID', 'DTYPE', 'BEDRM', 'ROOM', 'PR']`
3. Deduplicate: for each cycle, `df.drop_duplicates(subset='SIM_HH_ID')` to get one row per household (non-temporal variables are constant per household)
4. Harmonize categories per Task 2
5. Create the figure with `GridSpec(4, 5, hspace=0.35, wspace=0.25)`
6. For each of the 20 subplots:
   - Plot bar chart with `ax.bar(categories, percentages, color=cycle_color)`
   - Set x-tick labels with rotation (45° for DTYPE and PR, 0° for BEDRM and ROOM)
   - Set y-label to "%" on the leftmost column only
   - Add subplot title: cycle year + "(N=XX,XXX)" on the top row only
   - Add row label (variable name) on the leftmost column only
7. Apply shared y-axis limits within each row using `sharey` or manual `set_ylim`
8. Add column headers (cycle years) as `fig.text()` annotations above the top row
9. Add the 2025 column with red-orange bars; historical columns with green-teal shades
10. Save as PNG at 300 DPI

**Expected result:** A ~22x14 inch figure with 20 bar chart subplots. Visual inspection should show:
- DTYPE: clear shift from many categories (2005/2015) to fewer (2010/2022), with 2025 matching the classified pipeline categories
- BEDRM: shift from 3-bin to finer granularity in 2010/2022
- ROOM: half-integer vs integer bins visible as different bar positions
- PR: Ontario and Quebec consistently dominant, proportions relatively stable

**How to test:**
- Run the script: `python plot_nontemporal_comparison.py`
- Verify output PNG exists and opens correctly
- Compare individual subplots visually against the per-cycle `*_BEM_non_temporals.png` files — distributions should match (though normalized to % rather than raw counts)
- Verify all percentage columns sum to ~100%

---

### Task 4: Compute occupancy and metabolic rate distributions for temporal Section A & B

**Aim:** Prepare the histogram data for occupancy fraction and metabolic rate distributions across all five cycles.

**What to do:** For each cycle, compute binned histograms (normalized to %) of `Occupancy_Schedule` (all rows) and `Metabolic_Rate` (rows where > 0).

**How to do:**
1. Load all cycles with columns `['Occupancy_Schedule', 'Metabolic_Rate']`
2. For occupancy: use `np.histogram(df['Occupancy_Schedule'], bins=20, range=(0, 1), density=True)`
3. For metabolic rate: filter `df[df['Metabolic_Rate'] > 0]`, then `np.histogram(..., bins=50, range=(0, 250), density=True)`
4. Also compute KDE curves using `scipy.stats.gaussian_kde` for overlay

**Why:** These distributions reveal macro-level shifts in how occupied or vacant Canadian homes are (occupancy) and how active residents are when home (metabolic). The bimodal occupancy pattern and the metabolic spike shapes are key findings.

**Impact:** Forms the top 2 rows of the primary temporal comparison figure. These are the most directly comparable subplots since they use the same variable with the same value range across all cycles.

**Steps:**
1. Load data for all 5 cycles (only `Occupancy_Schedule` and `Metabolic_Rate` columns needed)
2. For each cycle, compute occupancy histogram with 20 bins in [0, 1]
3. For each cycle, filter Metabolic_Rate > 0, compute histogram with 50 bins in [0, 250]
4. For each histogram, compute KDE using `gaussian_kde` on the raw values
5. Store results as dicts: `occ_hists = {'2005': (bin_edges, counts, kde), ...}`

**Expected result:** 5 occupancy histograms showing the characteristic bimodal shape (peaks at 0.0 and 1.0) and 5 metabolic histograms showing the dominant spike near 65-75 W. Differences between cycles should be subtle but visible.

**How to test:** Compare each cycle's histogram visually against the top 2 subplots of the corresponding `*_BEM_temporals.png` file. The shapes should match closely.

---

### Task 5: Sample and prepare household-level data for heatmap visualization (Section C2)

**Aim:** Extract and prepare a reproducible sample of individual household schedules from each cycle, formatted for heatmap rendering.

**What to do:** For each cycle and day type (Weekday/Weekend), sample ~150 unique households, pivot their occupancy data into a 2D matrix (households x hours), and sort by a meaningful metric.

**How to do:**
1. Load all cycles with columns `['SIM_HH_ID', 'Day_Type', 'Hour', 'Occupancy_Schedule']`
2. For each cycle, extract unique household IDs: `hh_ids = df['SIM_HH_ID'].unique()`
3. Sample 150 IDs using `np.random.seed(42)` for reproducibility
4. Filter the dataframe to sampled households
5. For each day type, pivot: `pivot_table(index='SIM_HH_ID', columns='Hour', values='Occupancy_Schedule')`
6. Compute a sort metric per household: mean occupancy during hours 9-16 (daytime vacancy indicator)
7. Sort rows by this metric (low daytime occupancy at top, high at bottom)

**Why:** The heatmap is the most information-dense way to show individual household differences. Sorting by daytime occupancy creates a visual gradient that immediately communicates the fraction of "9-to-5 away" vs. "always home" households. Using the same random seed ensures the figure is reproducible.

**Impact:** Produces the core data for Rows 3-6 of the primary temporal figure. This is the most novel visualization in the plan — it shows something the existing plots do not.

**Steps:**
1. Load data for all 5 cycles
2. Set `np.random.seed(42)`
3. For each cycle:
   a. Get unique `SIM_HH_ID` list
   b. Sample `min(150, len(hh_ids))` IDs (2025 has fewer households so may need fewer)
   c. Filter dataframe to sampled IDs
   d. Split by `Day_Type` into weekday and weekend subsets
   e. Pivot each subset to a matrix: rows = households (150), columns = hours (24), values = occupancy (0-1)
   f. Compute sort key: `matrix.loc[:, 9:16].mean(axis=1)`
   g. Sort matrix by sort key ascending (lowest daytime occupancy = most "away" = top)
4. Store 10 matrices total (5 cycles x 2 day types) in a dict

**Expected result:** 10 DataFrames, each ~150 rows x 24 columns, with values between 0 and 1. When plotted as heatmaps, they should show a gradient from "mostly dark during day" (top rows, households away at work) to "mostly light all day" (bottom rows, households always home).

**How to test:**
- Verify each matrix has the expected shape (150 x 24 or fewer for 2025)
- Verify values range [0, 1]
- Verify sorting: `matrix.iloc[0, 9:16].mean()` should be <= `matrix.iloc[-1, 9:16].mean()`
- Quick `plt.imshow()` of one matrix to confirm the gradient pattern

---

### Task 6: Implement `plot_temporal_comparison.py` (primary figure)

**Aim:** Produce the primary temporal comparison figure (`BEM_Temporal_CrossCycle_Comparison.png`) combining occupancy/metabolic histograms (Sections A-B) and household heatmaps (Section C2).

**What to do:** Write the full plotting script that combines Task 4 (histograms) and Task 5 (heatmaps) into a single 6-row x 5-column figure.

**How to do:**
1. Create `eSim_occ_utils/plotting/plot_temporal_comparison.py`
2. Use `GridSpec(6, 5)` with height ratios `[1, 1, 2, 2]` (histograms shorter, heatmaps taller) — or `GridSpec` with custom row heights
3. Row 1: occupancy histograms with KDE overlays (Section A)
4. Row 2: metabolic rate histograms with KDE overlays (Section B)
5. Rows 3-4: weekday heatmaps (Section C2)
6. Rows 5-6: weekend heatmaps (Section C2)

**Why:** This figure is the centrepiece of the temporal comparison. It combines population-level statistics (histograms) with individual-level detail (heatmaps) in a single figure, giving the reader both the forest and the trees.

**Impact:** Produces a key figure for the paper's results section. The heatmap section in particular provides a novel visual narrative about changing occupancy patterns in Canada.

**Steps:**
1. Set up script with imports, path config, constants
2. Load data using Task 1 pattern — columns: `['SIM_HH_ID', 'Day_Type', 'Hour', 'Occupancy_Schedule', 'Metabolic_Rate']`
3. Compute histograms per Task 4
4. Compute heatmap matrices per Task 5
5. Create figure: `fig = plt.figure(figsize=(22, 18))`
6. Set up GridSpec with 6 rows: `gs = GridSpec(6, 5, height_ratios=[1, 1, 1.5, 1.5, 1.5, 1.5], hspace=0.3, wspace=0.2)`
7. **Row 1 (Occupancy histograms):** For each of 5 columns:
   - `ax.bar(bin_centers, counts, width, color=cycle_color, alpha=0.7)`
   - `ax.plot(kde_x, kde_y, color=cycle_color, lw=1.5)`
   - Shared x-axis [0, 1], shared y-axis across row
   - Title: cycle year
8. **Row 2 (Metabolic histograms):** Same approach, x-axis [0, 250]
9. **Rows 3-4 (Weekday heatmaps):** For each of 5 columns:
   - `ax.imshow(matrix, aspect='auto', cmap=cmap, vmin=0, vmax=1)`
   - x-ticks at hours 0, 4, 8, 12, 16, 20, 24
   - y-axis: "Household Index" (no individual labels)
   - Use `Greens` cmap for 2005-2022, `Oranges` for 2025
10. **Rows 5-6 (Weekend heatmaps):** Same as rows 3-4
11. Add section labels: "Weekday" and "Weekend" as `fig.text()` annotations on the left
12. Add row group titles: "Occupancy Distribution", "Metabolic Rate Distribution", "Sample Households (Weekday)", "Sample Households (Weekend)"
13. Add a shared colorbar for the heatmaps
14. Save at 300 DPI

**Expected result:** A single large figure with:
- Top 2 rows: 10 histograms showing distribution shapes across cycles
- Bottom 4 rows: 10 heatmaps showing individual household schedule gradients
- Clear visual distinction between historical (green) and classified (orange) cycles
- The 2022 and 2025 heatmaps should show more "always home" households (more solid color during daytime) compared to 2005/2010/2015

**How to test:**
- Run: `python plot_temporal_comparison.py`
- Verify output PNG exists, opens correctly, and all 30 subplots are populated
- Compare histogram shapes against individual cycle `*_BEM_temporals.png` files
- Verify heatmap sorting: top rows should have daytime gaps, bottom rows should be solid
- Check that 2025 column uses orange colormap, others use green

---

### Task 7: Implement spaghetti plot (supplementary figure)

**Aim:** Produce a supplementary figure (`BEM_Temporal_Spaghetti_Comparison.png`) showing individual household schedule lines overlaid to form a cloud pattern for each cycle.

**What to do:** For each cycle and day type, plot ~80 randomly sampled household schedules as semi-transparent lines, with the population mean overlaid as a bold line.

**How to do:**
1. Add a spaghetti-plot section at the end of `plot_temporal_comparison.py` (or as a separate callable function)
2. Use `GridSpec(2, 5)` — Row 1 = Weekday, Row 2 = Weekend
3. For each subplot, loop through sampled households and plot with low alpha

**Why:** The spaghetti plot complements the heatmap by showing continuous profiles rather than discretized color. It is particularly effective for presentations (more visually engaging than a heatmap) and for illustrating the variance and clustering of schedules.

**Impact:** Provides an alternative/supplementary figure. Useful if reviewers request a different visualization or for conference slide decks.

**Steps:**
1. Reuse household sampling from Task 5 (same seed, same 150 households, but use ~80 for plotting to avoid over-clutter)
2. Create figure: `fig, axes = plt.subplots(2, 5, figsize=(22, 8), sharey=True)`
3. For each cycle and day type:
   a. Loop through sampled households
   b. Plot: `ax.plot(hours, occupancy_values, color=light_color, alpha=0.08, lw=0.5)`
   c. Compute population mean (from full dataset, not just sampled): `mean_profile = df.groupby('Hour')['Occupancy_Schedule'].mean()`
   d. Plot mean: `ax.plot(hours, mean_profile, color=bold_color, lw=2.5)`
   e. Optionally add 25th-75th percentile shading: `ax.fill_between(hours, q25, q75, alpha=0.15)`
4. Set shared axes: x = [0, 23], y = [0, 1]
5. Add row labels: "Weekday", "Weekend"
6. Add column headers: cycle years
7. Save at 300 DPI

**Expected result:** A 2x5 figure where each subplot shows a "cloud" of ~80 thin lines converging around a bold mean. The cloud width indicates schedule diversity. Key visual findings:
- All cycles show the nighttime cluster (hours 0-6, most households at high occupancy)
- Daytime dip (hours 8-16) should be deepest and narrowest in 2005, progressively flatter in 2022/2025
- Weekend clouds should be tighter (less variation) than weekday clouds

**How to test:**
- Run the script and verify the output PNG
- Verify the bold mean line aligns with the average presence schedule from `BEM_Presence_Evolution_Comparison.png`
- Verify all individual lines fall within [0, 1]

---

### Task 8: Final styling pass and paper-readiness check

**Aim:** Ensure both figures meet publication standards for the eSim 2026 paper.

**What to do:** Review both output PNGs for font sizes, label clarity, color consistency, legend completeness, and DPI.

**How to do:**
1. Open each PNG at 100% zoom and check readability of all text
2. Verify color consistency: 2005-2022 in green-teal family, 2025 in red-orange
3. Check that axis labels, tick marks, and titles are not clipped or overlapping
4. Verify DPI is 300+ (suitable for journal print)

**Why:** Publication figures have strict readability requirements. A figure that looks fine on screen may have unreadable axis labels when printed or shrunk to column width.

**Impact:** Determines whether the figures can go directly into the paper draft or need iteration.

**Steps:**
1. Check font sizes: titles >= 12pt, axis labels >= 10pt, tick labels >= 8pt
2. Check that the 2025 column visually "pops" as distinct from historical columns
3. Check that no subplot has clipped bars, truncated labels, or overlapping text
4. Check that heatmap colorbars have clear labels (0 = Away, 1 = Full Occupancy)
5. Verify figure dimensions are compatible with typical journal column/page widths
6. If any issues found, adjust `figsize`, `fontsize`, `hspace/wspace`, or `rotation` parameters and re-run

**Expected result:** Two (or three) publication-ready PNG files that can be inserted into the paper LaTeX/Word document without further editing.

**How to test:** Print each figure on A4 paper (or view at journal-column width ~3.5 inches for single-column, ~7 inches for full-width). All text should remain legible at that size.
