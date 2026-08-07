# Table 4.2: Quantified Schedule Discrepancies (Default vs 2025 GSS)

**Goal**: Translate the visual discrepancies from Figure 4.1.3 into precise, citable numerical "error metrics" that quantify how wrong default schedules are.

**Key message**: Enables statements like *"Default schedules overestimate mean weekday occupancy by 32%"* for policy documents, building codes, and practitioner guidelines.

---

## Data Sources

| Series | Source |
|--------|--------|
| **Default** | `0_BEM_Setup/Templates/schedule.json` via `eSim_bem_utils.idf_optimizer` |
| **2025 GSS** | `0_BEM_Setup/BEM_Schedules_2025.csv` (Weekday + Weekend) |

---

## Table Layout (Pre-computed Values)

| Parameter | Default | 2025 GSS | Difference | % Error |
|-----------|---------|----------|------------|---------|
| Mean weekday occupancy (0–1) | 0.684 | 0.465 | +0.219 | +32.1% |
| Mean weekend occupancy (0–1) | 0.684 | 0.502 | +0.182 | +26.6% |
| Peak occupancy time (weekday) | 00:00 | 04:00 | Δ 4 h | — |
| Daytime occupancy (09–17) | 25.6% | 27.6% | −2.0 pp | — |
| Mean metabolic rate (W) | 95.0 | 72.7 | +22.3 W | +23.5% |
| Peak metabolic rate (W) | 95.0 | 95.0 | 0 W | 0% |

> [!IMPORTANT]
> Discrepancies expressed as **both** absolute differences AND percentage errors to convey practical significance.

---

## Proposed Changes

#### [NEW] [generate_schedule_discrepancy_table.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/plotting/generate_schedule_discrepancy_table.py)

- Load Default schedules from JSON (via `eSim_bem_utils.idf_optimizer`)
- Load 2025 GSS data (both Weekday and Weekend)
- Compute 6 metrics for each, plus absolute and % error
- Output: Console, CSV (`Table_4_2_Schedule_Discrepancies.csv`), and Markdown (`Table_4_2_Schedule_Discrepancies.md`)

---

## Verification Plan

1. Run: `python3 eSim_occ_utils/plotting/generate_schedule_discrepancy_table.py`
2. Confirm values match the pre-computed table above
3. Cross-validate against Figure 4.1.3 visual gaps
