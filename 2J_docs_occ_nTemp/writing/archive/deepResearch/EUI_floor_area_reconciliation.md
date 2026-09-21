# EUI Floor-Area Basis Reconciliation
**Date:** 2026-06-11  
**Scope:** Read-only analysis. No EnergyPlus runs. No manuscript edits.  
**Question:** Does a floor-area denominator mismatch between the simulation EUI and SHEU-2019 explain SingleDetached's 208.13 kWh/m² sitting ~12% above the SHEU upper bound of 186.1 kWh/m²?

---

## 1. Production IDF Files Confirmed

Source: `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/main.py` lines 76–86.

```python
STEP8_BUILDINGS_DIR = os.path.join(BASE_DIR, "2J_docs_occ_nTemp", "BEM_setup", "Buildings_MTL_v242")
STEP8_ARCHETYPES = [
    {"name": "SingleD",       "dtype": "SingleD",       "idf": "DetachedHouse"},
    {"name": "OtherDwelling", "dtype": "OtherDwelling", "idf": "AttachedHouse"},
    {"name": "MidRise",       "dtype": "MidRise",       "idf": "ApartmentMidRise"},
    {"name": "HighRise",      "dtype": "HighRise",      "idf": "ApartmentHighRise"},
]
```

The four v242 production IDFs:

| Archetype | IDF file (Buildings_MTL_v242/) |
|-----------|-------------------------------|
| SingleD | `DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` |
| OtherDwelling | `AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` |
| MidRise | `ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf` |
| HighRise | `ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf` |

---

## 2. EUI Denominator Basis in Code

Source: `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/plotting.py` lines 257–374.

`calculate_eui(conn)` queries the EnergyPlus SQL `TabularDataWithStrings` table:

```python
# plotting.py line 370
area_for_eui = results['conditioned_floor_area'] or results['total_floor_area']
```

Where `conditioned_floor_area` is populated by `RowName == 'Net Conditioned Building Area'` from EnergyPlus's "Building Area" tabular report (lines 300–315 of plotting.py). This value is stored in `agg_annual.csv` as `conditioned_floor_area_m2` and `eui_kWh_m2`.

**Conclusion: The simulation EUI denominator is EnergyPlus "Net Conditioned Building Area", which is the sum of floor areas of all zones where E+ determines HVAC is present.**

The smoke-test path (`step8_val_v2.py` lines 70–88, `read_eui_eplustbl()`) also uses per-conditioned-area via `eplustbl.csv`'s "Utility Use Per Conditioned Floor Area" section, and agrees in basis.

---

## 3. Zone Inventory and Conditioning Status

### 3a. DetachedHouse (SingleD)

**Zones** (IDF lines 2304–2335):
- `living_unit1` — has thermostat (`ZoneControl:Thermostat`, IDF line 3994) → **conditioned**
- `attic_unit1` — no thermostat → **unconditioned**
- `unheatedbsmt_unit1` — no thermostat, name explicitly "unheated" → **unconditioned**

No garage zone exists.

`GroundHeatTransfer:Basement:Interior COND=True` (IDF line 3027) is a thermal-coupling preprocessor directive; it does not designate the basement zone as HVAC-conditioned. E+ will not count `unheatedbsmt_unit1` in "Net Conditioned Building Area".

### 3b. AttachedHouse (OtherDwelling)

**Zones** (IDF lines 2303–2533): 21 zones = 7 units × 3 zone types each.
- `living_unit1` through `living_unit7` — thermostats at IDF lines 9632–9679 → **conditioned** (7 zones)
- `attic_unit1–7` — no thermostat → **unconditioned**
- `unheatedbsmt_unit1–7` — no thermostat → **unconditioned**

No garage zone exists.

### 3c. MidRise (ApartmentMidRise)

**Zones** (IDF lines 2013–2272): 27 zone objects total.

Zone grouping via `ZONEGROUP "Middle Floors"` (IDF line 2269–2272):
```
Zone List Multiplier: 2
```
Effective floor count: G×1 + M×2 + T×1 = **4 floors**.

Per-floor zone inventory:
- **G floor (×1):** G SW, G NW, G NE, G N1, G N2, G S1, G S2 Apartments (7 residential) + Office (1, occupies SE slot) + G Corridor (1) = 9 zones
- **M floor template (×2):** M SW, NW, SE, NE, N1, N2, S1, S2 Apartments (8) + M Corridor (1) = 9 zones
- **T floor (×1):** T SW, NW, SE, NE, N1, N2, S1, S2 Apartments (8) + T Corridor (1) = 9 zones

No "Part of Total Floor Area = No" tags in old-format ZONE objects (no such field present) → all 27 zones treated as conditioned by E+.

### 3d. HighRise (ApartmentHighRise)

**Zones** (IDF lines 2057–2461): 27 zone objects total (identical structure to MidRise).

Zone grouping via `ZoneGroup "Middle Floors"` (IDF line 2475–2478):
```
Zone List Multiplier: 8
```
Effective floor count: G×1 + M×8 + T×1 = **10 floors**.

- **G floor (×1):** 7 apartments + Office + G Corridor = 9 zones (all `Part of Total Floor Area = Yes`)
- **M floor template (×8):** 8 apartments + M Corridor = 9 zones (all `Yes`)
- **T floor (×1):** 8 apartments + T Corridor = 9 zones (all `Yes`)

---

## 4. Floor Area Extraction and Arithmetic

### 4a. DetachedHouse — living_unit1 floor area

**Source surfaces** (IDF lines 3942–3965 for Inter zone floor 1, and 2787–2802 for Floor_unit1):

Both floor surfaces share identical vertices:
```
Vertex 1: (0, 0, z)
Vertex 2: (0, 9.09982, z)
Vertex 3: (12.13309, 9.09982, z)
Vertex 4: (12.13309, 0, z)
```
- X_span = 12.13309 m, Y_span = 9.09982 m
- Per-floor area = 12.13309 × 9.09982 = **110.408 m²**

Computation:
- 12 × 9.09982 = 109.198
- 0.13309 × 9.09982 = 1.210
- Total = **110.408 m²**

Two living stories (floor 1 at Z = 0.0101→2.60156, floor 2 at Z = 2.60156→5.19303):
- A_conditioned = 2 × 110.408 = **220.816 m²**

Basement (unheatedbsmt_unit1): V = 235.63 m³ from IDF, footprint ≈ 110.41 m², not conditioned.

### 4b. AttachedHouse — living_unit1 floor area

**Source surface** Floor_unit1 (IDF line 2787–2802):
```
Vertex 1: (0, 0, 0.0101)
Vertex 2: (0, 8.215838, 0.0101)
Vertex 3: (10.954451, 8.215838, 0.0101)
Vertex 4: (10.954451, 0, 0.0101)
```
- X_span = 10.954451 m, Y_span = 8.215838 m
- Per-floor area = 10.954451 × 8.215838 = **90.001 m²**

Computation:
- 10 × 8.215838 = 82.158
- 0.954451 × 8.215838 = 7.843
- Total = **90.001 m²**

7 units × 2 stories:
- A_conditioned = 7 × 2 × 90.001 = **1,260.01 m²**

Basement (unheatedbsmt_unit1–7): V = 191.77 m³ per unit, not conditioned.

### 4c. Apartment zone floor area (applies to both MidRise and HighRise)

**Source surface** g GFloor SWA (MidRise IDF lines 2479–2493; HighRise IDF lines similar):
```
Vertex 1: (0, 0, 0)
Vertex 2: (11.581835, 0, 0)
Vertex 3: (11.581835, 7.619628, 0)
Vertex 4: (0, 7.619628, 0)
```
- X_span = 11.581835 m, Y_span = 7.619628 m
- Per-apartment area = 11.581835 × 7.619628 = **88.250 m²**

Computation:
- 11 × 7.619628 = 83.816
- 0.581835 × 7.619628 = 4.434
- Total = **88.250 m²**

**Office zone** uses same footprint vertices (IDF line 2499–2510) → **88.250 m²**

### 4d. Corridor floor area (applies to both MidRise and HighRise)

**Source surface** g Floor C (MidRise IDF lines 3889–3904; HighRise IDF lines 3245–3260):
```
Vertex 1: (0, 0, 0)
Vertex 2: (46.327341, 0, 0)   [MidRise uses 46.327341; HighRise uses 46.3273 — same to 4 sig.fig.]
Vertex 3: (46.327341, 1.676318, 0)
Vertex 4: (0, 1.676318, 0)
```
- X_span = 46.327341 m, Y_span = 1.676318 m
- Corridor area = 46.327341 × 1.676318 = **77.659 m²**

Computation:
- 46 × 1.676318 = 77.111
- 0.327341 × 1.676318 = 0.549
- Total = **77.660 m²**

---

## 5. Reconciliation Table

### 5a. Area Summary

**MidRise conditioned area** (4 effective floors):
- G floor: (8 zones × 88.250) + 77.660 = 706.000 + 77.660 = **783.660 m²**
- M floors ×2: 783.660 × 2 = **1,567.320 m²**
- T floor: **783.660 m²**
- **A_sim (total) = 783.660 + 1,567.320 + 783.660 = 3,134.640 m²**

MidRise dwelling-only (apartments + Office, no corridors):
- G: 8 × 88.250 = 706.000 m²
- M×2: 8 × 88.250 × 2 = 1,412.000 m²
- T: 8 × 88.250 = 706.000 m²
- **A_sheu_basis = 2,824.000 m²**

**HighRise conditioned area** (10 effective floors):
- G floor: (8 × 88.250) + 77.660 = **783.660 m²**
- M floors ×8: 783.660 × 8 = **6,269.280 m²**
- T floor: **783.660 m²**
- **A_sim (total) = 783.660 + 6,269.280 + 783.660 = 7,836.600 m²**

HighRise dwelling-only:
- G: 8 × 88.250 = 706.000 m²
- M×8: 8 × 88.250 × 8 = 5,648.000 m²
- T: 8 × 88.250 = 706.000 m²
- **A_sheu_basis = 7,060.000 m²**

### 5b. Main Reconciliation Table

| Archetype | A_sim (m²) | A_sheu_basis (m²) | Basement (m²) | Garage (m²) | A_sim / A_sheu | EUI_sim (kWh/m²) | EUI_matched (kWh/m²) | SHEU range (kWh/m²) | Within band? |
|-----------|-----------|------------------|--------------|------------|---------------|----------------|---------------------|--------------------:|:------------|
| SingleD | 220.82 | 220.82 | 110.41 (excl.) | 0 | 1.000 | 208.13 | **208.13** | 130.6–186.1 | NO (above by 22.0) |
| OtherDwelling | 1,260.01 | 1,260.01 | ~630.07 (excl.) | 0 | 1.000 | 127.80 | **127.80** | 136.1–186.1 | NO (below by 8.3) |
| MidRise | 3,134.64 | 2,824.00 | 0 | 0 | 1.110 | 151.79 | **168.49** | 111.1–216.7 | YES |
| HighRise | 7,836.60 | 7,060.00 | 0 | 0 | 1.110 | 117.01 | **129.88** | 113.9–147.2 | YES |

**Arithmetic for EUI_matched:**
- SingleD: 208.13 × (220.82 / 220.82) = 208.13 × 1.000 = **208.13**
- OtherDwelling: 127.80 × (1,260.01 / 1,260.01) = 127.80 × 1.000 = **127.80**
- MidRise: 151.79 × (3,134.64 / 2,824.00) = 151.79 × 1.110 = **168.49**
- HighRise: 117.01 × (7,836.60 / 7,060.00) = 117.01 × 1.110 = **129.88**

---

## 6. Findings and Bottom Line

### 6a. Does the floor-area basis explain SingleDetached's over-band position?

**No.**

For single-family archetypes (DetachedHouse, AttachedHouse), the IDF conditioning structure exactly mirrors SHEU's definition: E+ marks the basement zones (`unheatedbsmt_unit*`) as unconditioned (no thermostat, no HVAC object), and there are no garage zones in either IDF. Therefore E+'s "Net Conditioned Building Area" = the above-grade living area = A_sheu_basis. The ratio A_sim / A_sheu_basis = 1.000 for both, so EUI_matched = EUI_sim.

SingleDetached's 208.13 kWh/m² remains ~22 kWh/m² above the SHEU 186.1 upper bound after the correction. The floor-area mismatch hypothesis is rejected for this archetype.

### 6b. Apartments — corridor dilution matters

For the apartment archetypes, E+'s conditioned area includes conditioned corridors and the ground-floor Office zone, while SHEU measures EUI per household using dwelling-unit area only. The corridor fraction is:
- MidRise: 4 corridors × 77.66 m² = 310.64 m² out of 3,134.64 m² total = **9.9% dilution** (G + M×2 + T = 4 effective floors, one corridor each; consistent with the §5b ratio 1.110)
- HighRise: 10 corridors × 77.66 m² = 776.60 m² out of 7,836.60 m² total = **9.9% dilution**

After applying the dwelling-unit-basis correction (EUI_matched):
- MidRise: 151.79 → **168.49 kWh/m²** (within SHEU [111.1–216.7])
- HighRise: 117.01 → **129.88 kWh/m²** (within SHEU [113.9–147.2])

Both apartment archetypes pass the SHEU plausibility check on either basis (uncorrected or corrected), because they fall well within the wide SHEU bands even before correction.

### 6c. OtherDwelling under-band flag

OtherDwelling (AttachedHouse rowhouse) has EUI_sim = 127.80 kWh/m², which is 8.3 kWh/m² below the SHEU lower bound of 136.1 kWh/m² for single attached/row dwellings. Since A_sim = A_sheu_basis (ratio = 1.000), no area correction changes this. This is a model-physics difference (e.g., shared-wall heat loss reduction in rowhouse vs. semi-detached SHEU sample), not a denominator error.

### 6d. Summary verdict

| Finding | Result |
|---------|--------|
| Area basis explains SingleD over-band? | **No — ratio = 1.000, EUI_matched = EUI_sim = 208.13** |
| Area basis affects apartment archetypes? | **Yes, 10–11% upward correction, but both stay within SHEU bands** |
| Legitimate explanation for SingleD 208 kWh/m²? | **Needs physical explanation; cold-climate/all-electric framing (heating-dominant zone) remains the most credible account** |
| OtherDwelling under-band? | **Yes, independently, by ~8.3 kWh/m² — rowhouse shared-wall effect likely** |

---

## 7. Cluster Commands for Authoritative Area Numbers

Local `agg_annual.csv` is not available (outputs_step8_v2/agg/ was empty on this machine). To retrieve authoritative `conditioned_floor_area_m2` values from the campaign results on Speed cluster:

On the cluster (srun wrapper required per HARD RULE — no bare python on login node):
```
srun -p ps --mem=4G -t 00:20:00 python3 -c "import pandas as pd; df=pd.read_csv('/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/agg/agg_annual.csv'); print(df.groupby('archetype')['conditioned_floor_area_m2'].mean())"
```

This would provide the E+-computed conditioned area averaged across all 6000 runs per archetype, as the authoritative check against the manual IDF-derived values above.

---

## 8. Key Code References

| Item | File | Lines |
|------|------|-------|
| Production IDF directory & archetype→IDF mapping | `Step8_docs/eSim_bem_utils_2J/main.py` | 76–86 |
| EUI computation (SQL, conditioned area denominator) | `Step8_docs/eSim_bem_utils_2J/plotting.py` | 257–374 |
| `area_for_eui` assignment | `Step8_docs/eSim_bem_utils_2J/plotting.py` | 370 |
| Smoke-test EUI (eplustbl.csv, conditioned area) | `Step8_docs/step8_val_v2.py` | 70–88 |
| SHEU bands (internal validation only) | `2J_docs_occ_nTemp/08_simulation_val.py` | 46–52 |
| DetachedHouse zone definitions | `BEM_setup/Buildings_MTL_v242/DetachedHouse+...v242.idf` | 2304–2335 |
| DetachedHouse floor surfaces | `BEM_setup/Buildings_MTL_v242/DetachedHouse+...v242.idf` | ~3942–3965 |
| AttachedHouse floor surface (Floor_unit1) | `BEM_setup/Buildings_MTL_v242/AttachedHouse+...v242.idf` | 2787–2802 |
| MidRise zone list + ZoneGroup multiplier (×2) | `BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentMidRise_...v242.idf` | 2013–2272 |
| HighRise zone list + ZoneGroup multiplier (×8) | `BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentHighRise_...v242.idf` | 2057–2478 |
| MidRise G Corridor floor surface (46.33 × 1.68 m) | `BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentMidRise_...v242.idf` | 3889–3904 |
| HighRise G Corridor floor surface | `BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentHighRise_...v242.idf` | 3245–3260 |
| EUI basis caution note (smoke-test vs. agg) | `Step8_docs/cluster_rerun.md` | 199–202 |
