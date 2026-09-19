# Implementation Plan - K-Fold Comparative Simulation

Implement a new simulation option that runs comparative simulations X times with different random households per iteration, then aggregates results to reduce single-household bias.

---

## Goal

*   **Problem:** Current Option 3 selects **one random household per year**, which can produce biased results if that household has unusual occupancy patterns.
*   **Solution:** Run the comparative simulation **K times** (e.g., K=5), each time selecting a different random household for each year. Aggregate results (mean ± std) across all K runs.

---

## User Review Required

> [!IMPORTANT]
> **Number of Iterations (K):** Default to `K=5`? User should be able to specify this at runtime.

> [!WARNING]
> **Compute Time:** Each K iteration runs 4 simulations (2025, 2015, 2005, Default). So `K=5` means **20 EnergyPlus runs**. Consider warning the user.

---

## Proposed Changes

### Menu (run_bem.py / main.py)

#### [NEW] Option 4: `option_kfold_comparative_simulation()`

*   **User Input:**
    1.  Select IDF file.
    2.  Select Weather file.
    3.  Select Region / Dwelling Type (for schedule filtering).
    4.  **Specify K** (number of iterations, default=5).
*   **Core Logic:**
    ```
    FOR k = 1 to K:
        # Select a NEW random household for each year (hhsize-matched)
        Run 4 simulations in parallel (2025, 2015, 2005, Default)
        Extract EUI results → Store in results_list[k]
    ```
*   **Aggregation:**
    After all K iterations:
    ```python
    eui_aggregated = {
        'mean': { scenario: mean(eui_values) },
        'std':  { scenario: std(eui_values) }
    }
    ```
*   **Output:**
    *   **Summary CSV:** `Sim_Results/KFold_Results/aggregated_eui.csv`
    *   **Averaged Bar Chart:** `Sim_Results_Plotting/KFold_Comparative_EUI_Mean.png` (with error bars)
    *   **Individual Run Data:** `Sim_Results/KFold_Results/run_k/...`

---

### Plotting Module (eSim_bem_utils/plotting.py)

#### [MODIFY/NEW] `plot_kfold_comparative_eui()`

*   **Input:** `eui_aggregated` dict (mean + std per scenario per end-use category).
*   **Output:** Bar chart with error bars (std) for each end-use category.

---

### Data Flow Diagram

```mermaid
flowchart TD
    A[User Selects IDF, EPW, Region, K] --> B{Loop k=1 to K}
    B --> C[Select Random HH for 2025]
    B --> D[Select Random HH for 2015]
    B --> E[Select Random HH for 2005]
    B --> F[Default - No HH]
    C & D & E & G --> G[inject_schedules x 4]
    G --> H[run_simulations_parallel]
    H --> I[Extract EUI from SQL]
    I --> J{Store results_list[k]}
    J --> B
    B --All K done--> K[Aggregate Mean/Std]
    K --> L[Save CSV + Generate Plot with Error Bars]
```

---

## Verification Plan

### Functional Tests
1.  Run with `K=2` (minimum for std calculation).
2.  Confirm 8 simulations run (2 iterations × 4 scenarios).
3.  Confirm aggregated CSV has mean/std columns.
4.  Confirm bar chart has visible error bars.

### Bias Reduction Check
*   Compare the "mean EUI" from K-Fold to a single Option 3 run. The K-Fold mean should be more stable across multiple executions.
