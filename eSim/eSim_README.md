# eSim: Occupancy-Based Building Energy Simulation

A comprehensive framework for generating synthetic occupant schedules and integrating them with building energy simulations using Census and General Social Survey (GSS) data.

## Overview

This project creates realistic occupant behavior profiles by:
1. Aligning Census demographic data with GSS time-use survey data
2. Matching Census agents to GSS schedules based on demographic similarity
3. Generating full temporal schedules for building energy modeling

## Project Structure

```
eSim/
├── eSim_occ_utils/                          # Core utilities
│   ├── 06CEN05GSS_alignment.py        # Census 2006 + GSS 2005 alignment
│   ├── 06CEN05GSS_ProfileMatcher.py   # Profile matching & schedule generation
│   └── gss_reader.py                  # GSS data reader
├── 0_Occupancy/
│   ├── DataSources_GSS/               # GSS raw data
│   ├── DataSources_CENSUS/            # Census raw data
│   ├── Outputs_Aligned/               # Aligned datasets
│   │   ├── 06CEN05GSS_alignment/     # Harmonized Census-GSS data
│   │   └── 06CEN05GSS_ProfileMatching/ # Matched schedules
│   └── docs/                          # Documentation
└── README.md

```

## Workflow

### 1. Data Alignment (Census 2006 ↔ GSS 2005)

**Script:** `eSim_occ_utils/06CEN05GSS_alignment.py`

Harmonizes 11 demographic columns between Census 2006 and GSS 2005:
- `AGEGRP`, `ATTSCH`, `CMA`, `HHSIZE`, `KOL`, `LFTAG`, `MARSTH`, `NOCS`, `PR`, `SEX`, `TOTINC`

**Run:**
```bash
python eSim_occ_utils/06CEN05GSS_alignment.py
```

**Outputs:**
- `Aligned_Census_2005.csv` - Harmonized Census data
- `Aligned_GSS_2005.csv` - Harmonized GSS data
- Validation plots and reports

### 2. Profile Matching

**Script:** `eSim_occ_utils/06CEN05GSS_ProfileMatcher.py`

Matches Census agents to GSS schedules using tiered demographic matching:
- **Tier 1:** Perfect match (all 11 columns)
- **Tier 2:** Core demographics (6 key columns)
- **Tier 3:** Key constraints (3 essential columns)
- **Tier 4:** Fail-safe (household size only)

**Features:**
- Household-based sampling (preserves family integrity)
- Configurable sample percentage
- Validation with behavioral consistency checks

**Run:**
```bash
# Full dataset
python eSim_occ_utils/06CEN05GSS_ProfileMatcher.py

# 25% sample (recommended for testing)
python eSim_occ_utils/06CEN05GSS_ProfileMatcher.py --sample 25
```

**Outputs:**
- `06CEN05GSS_Matched_Keys_sampleXXpct.csv` - Matched Census-GSS pairs
- `06CEN05GSS_Full_Schedules_sampleXXpct.csv` - Expanded temporal schedules
- `06CEN05GSS_Validation_sampleXXpct.txt` - Validation report

## Validation Results (25% Sample)

| Metric | Value | Status |
|--------|-------|--------|
| Households Sampled | 28,454 (25%) | ✅ |
| Persons Included | 54,503 | ✅ |
| Tier 2 Match (Weekday) | 28.4% | ✅ Good |
| Tier 2 Match (Weekend) | 41.5% | ✅ Excellent |
| Fail-safe Rate | 0.2-0.5% | ✅ Near-zero |
| Work Duration (Employed) | 542 min/day | ✅ Realistic |

## Requirements

```bash
pip install pandas numpy matplotlib seaborn tqdm
```

**Python Version:** 3.9+

## Data Sources

- **Census 2006:** Canadian Census microdata
- **GSS 2005:** General Social Survey - Time Use

## Key Features

✅ **Household Integrity:** Sampling preserves complete household units  
✅ **Tiered Matching:** Prioritizes demographic similarity  
✅ **Validation:** Behavioral consistency checks (work patterns, episode counts)  
✅ **Scalable:** Configurable sampling for performance vs. quality trade-off  
✅ **Reproducible:** Fixed random seeds for consistent results  

## Citation

If you use this code, please cite:

```
Koraliseri, O. (2026). eSim: Occupancy-Based Building Energy Simulation Framework.
GitHub: https://github.com/orcunkoraliseri/GSSCanada
```

## License

Research use only. Contact author for commercial applications.

## Contact

**Orcun Koraliseri**  
Email: orcunkoraliseri@gmail.com  
GitHub: [@orcunkoraliseri](https://github.com/orcunkoraliseri)

---

**Last Updated:** January 2026  
**Branch:** eSim_NonTemporal
