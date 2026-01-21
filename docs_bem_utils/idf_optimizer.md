# IDF Optimizer Module

The `idf_optimizer.py` module automatically prepares IDF files for EnergyPlus 24.2 simulation.

## Workflow Integration

```
User runs run_bem.py
        ↓
Selects schedule file, IDF, weather, dwelling type
        ↓
┌─────────────────────────────────────────────┐
│  For each household:                        │
│    1. Load base IDF                         │
│    2. Inject occupancy/metabolic schedules  │
│    3. idf_optimizer.optimize_idf() ← HERE   │
│    4. Save modified IDF                     │
└─────────────────────────────────────────────┘
        ↓
Run EnergyPlus simulation
        ↓
Extract results & plot
```

## Optimizations Performed

| Check | Action if Needed |
|-------|------------------|
| Version ≠ 24.2 | Updates to 24.2 |
| `ZoneAveraged` in People | Changes to `EnclosureAveraged` |
| Missing `Output:SQLite` | Adds `SimpleAndTabular` |
| Missing output variables | Adds 7 energy analysis variables |
| Missing surface objects | Injects `OtherSideCoefficients` |
| Timestep ≠ 4 | Sets to 4 |
| Solar Distribution inefficient | Changes to `FullExterior` |

## Output Variables Added

1. Zone Lights Electricity Energy
2. Zone Electric Equipment Electricity Energy
3. Fan Electricity Energy
4. Zone Air System Sensible Heating Energy
5. Zone Air System Sensible Cooling Energy
6. Zone Ideal Loads Supply Air Total Heating Energy
7. Zone Ideal Loads Supply Air Total Cooling Energy

## Example Output

```
  Fixed PEOPLE.Mean_Radiant_Temperature_Calculation_Type: ZoneAveraged -> EnclosureAveraged
  Updated Version: 23.1 -> 24.2
  Added Output:SQLite (SimpleAndTabular)
  Added 7 output variables
  Injected missing SurfaceProperty:OtherSideCoefficients: SURFPROPOTHSDCOEFSLABAVERAGE
  Updated Timestep: 6 -> 4
```

## Neighbourhood Default Schedule Alignment

For neighbourhood simulations (where the input IDF often lacks occupancy schedules), the workflow aligns the "Default" scenario with your Single Building simulations to ensure consistent baselines.

| Step | Description |
| :--- | :--- |
| **1. Optimization Check** | Checks if the Neighbourhood IDF has internal load schedules (Lights, Equipment). |
| **2. Fallback Search** | If missing, looks for a Single Building IDF in `BEM_Setup/Buildings/*.idf`. |
| **3. Alignment** | Parses `Lights`, `ElectricEquipment`, and `WaterUse` schedules from the single building reference. |
| **4. Integration** | Uses these single-building schedules as the "Default" baseline for the neighbourhood. |

**Benefit:** This implementation ensures that "Default" vs "Integrated" comparisons in neighbourhood simulations rely on the same baseline physics as single-building comparisons, rather than using arbitrary or overly conservative synthesized defaults.

## Usage

The optimizer runs automatically during schedule injection. No manual intervention required.

For standalone use:
```python
from bem_utils import idf_optimizer

# Prepare a single IDF
idf_optimizer.prepare_idf_for_simulation("path/to/file.idf", "path/to/output.idf")
```
