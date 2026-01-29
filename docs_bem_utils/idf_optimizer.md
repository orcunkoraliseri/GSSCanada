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

---

## Speed Optimization Process

The IDF optimizer now includes **speed optimizations** that are automatically applied to all simulations. These optimizations reduce simulation time by up to **2.5x** while maintaining acceptable accuracy (~3% difference).

### Key Optimizations Applied

- **Shadow Calculation**
  - Method: `PixelCounting` (faster than PolygonClipping)
  - Resolution: 512 pixels
  - Update Frequency: Every 60 days (vs. daily)
  - Max Figures: 5,000 (vs. 15,000)

- **HVAC Convergence**
  - Maximum Iterations: 10 (vs. default 20)
  - Reduces HVAC loop calculation time by ~10%

- **Convection Algorithms**
  - Inside: `TARP` (accurate for heating/cooling)
  - Outside: `DOE-2` (balanced speed/accuracy)

- **Timestep Optimization**
  - 4 timesteps per hour (vs. 6)
  - ~15% faster calculations

### Run Period Modes

The optimizer supports three run period configurations:

| Mode | Days Simulated | Speedup | Use Case |
|------|----------------|---------|----------|
| `standard` | 365 | 1.0x | Final validation |
| `weekly` | 168 (24 TMY weeks) | ~2.5x | Iteration/testing |
| `design_day` | 2-4 | ~33x | HVAC sizing only |

### Benchmark Results (Montreal TMY)

| Profile | Time | vs Baseline | EUI Accuracy |
|---------|------|-------------|--------------|
| Standard (Full Year) | 54.8s | baseline | exact |
| Fast (24 TMY Weeks) | 21.7s | **2.52x faster** | ~3.3% diff |
| Design-Day Only | 1.7s | **33x faster** | sizing only |

### Functions

| Function | Description |
|----------|-------------|
| `apply_speed_optimizations(idf)` | Applies shadow, HVAC, convection settings |
| `configure_run_period(idf, mode)` | Sets standard/weekly/design_day mode |
| `prune_output_objects(idf)` | Removes unnecessary Output:* objects |

### Usage Example

```python
from bem_utils import idf_optimizer
from eppy.modeleditor import IDF

idf = IDF("building.idf")

# Apply all speed optimizations
idf_optimizer.apply_speed_optimizations(idf, verbose=True)

# Configure for fast simulation (24 TMY weeks)
idf_optimizer.configure_run_period(idf, mode='weekly', verbose=True)

idf.saveas("optimized.idf")
```
