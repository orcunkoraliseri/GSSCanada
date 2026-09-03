> 🟡 **NO-CORE REGIME, 2026-09-03 (`D-IMP-1`, ruled (a)).** The owner ruled the no-core regime on the
> OpenUBEM side (`D-EU-79`/`80`/`81`, 2026-09-02/03): *"a floor plate divides into dwellings only, no
> core, corridor, access band or unconditioned zone; every square metre belongs to a flat; nothing
> narrower than 2 m; one flat = one zone."* **Everything below in this document that names a core,
> corridor, stairwell or `b_u` is SUPERSEDED by `D-EU-79` and kept only as the record of what was
> considered** during the OpenUBEM-adaptation design phase (2026-08 architecture). No section below is
> deleted; each superseded block carries its own dated marker. See
> `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` I-1 and
> `IMP/docs/DONE/2026-09-03_D-IMP-1_D-IMP-2_D-IMP-3_nocore-review-rulings.md`.

# Step 8 — BEM / UBEM Simulation: Implementation Specification (Unified OpenUBEM + GSSCanada Architecture)

### 4J HETUS LLM Pipeline & OpenUBEM Framework Integration.
#### Parent Specification: `../4thJ_08_bemSimulation.md` (Read-Only). Validation Gates: `../4thJ_08_bemSimulation_val.md` (Pre-Registered).
#### OpenUBEM Engine Documentation: `C:\Users\o_iseri\Desktop\OpenUBEM\docs\docs_EXPLANATION\`
- [`OpenUBEM_fundamentals.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_fundamentals.md) (Architecture & 5-Stage Pipeline)
- [`OpenUBEM_inputs_reference.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_inputs_reference.md) (Input Registry & Standards)
- [`OpenUBEM_imputation_methods.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_imputation_methods.md) (4-Tier Imputation Cascade)
- [`simulated_vs_reconstructed_methodology.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/simulated_vs_reconstructed_methodology.md) (Fraction-Split EUI Completion)
- [`OpenUBEM_debug_References.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_debug_References.md) (Diagnostic Error Registry: ~200 Error Patterns)
#### Deep Research Dossier: `IMP_step8/DeepResearch/`
- [`DR01: State of the Art in Residential Floor Layout Generation`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR01_residential_floor_layout_generation_state_of_art.md)
- [`DR02: Floor-to-Unit Division and Staircase Buffer Methods`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR02_floor_to_unit_division_and_staircase_methods.md)
- [`DR03: Thermal Zoning Resolution & Energy Sensitivity`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR03_thermal_zoning_resolution_and_energy_impacts.md)
- [`DR04: Comparative Matrix and Synthesis for UBEM`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR04_comparative_matrix_and_synthesis_for_ubem.md)
- [`DR05: European Building Standards & EPBD Framework`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR05_european_building_standards_and_epbd_framework.md)
- [`DR06: National Standards: Spain, United Kingdom, and Italy`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR06_national_standards_spain_uk_italy.md)
- [`DR07: Engineering Roadmap for Adapting OpenUBEM to European Standards`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/DeepResearch/DR07_adapting_openubem_to_european_standards.md)
#### Methodological Provenance: `IMP_step8/outputs/kbem_ankara_report.md`, `IMP_step8/outputs/floor_layout_generation_report.md`, and *Iseri et al. (2025), Energy and Buildings 337, 115620*.

> 🟡 **Added 2026-09-03.** `DR02` (staircase buffer methods) and `DR03`/`DR04`'s core/corridor synthesis
> fed a **circulation-core recommendation** — an unconditioned stair/corridor zone, 6–12 % of GFA — that
> was **considered and retired** by the owner's `D-EU-79` no-core ruling: *"a floor plate divides into
> dwellings only, no core, corridor, access band or unconditioned zone."* The dossiers are kept as the
> literature record (DR02/DR03 cited as literature, never as a district number); no plan below built on
> them is live.

---

## 1. Executive Summary & Strategic Integration Architecture

This document establishes the **unified implementation methodology** merging the **OpenUBEM** urban building energy simulation framework with **GSSCanada** (the 4J HETUS Large Language Model demographic occupancy pipeline).

Rather than developing a one-off simulation harness from scratch, Step 8 configures and deploys the modular Python package `openubem` ([`C:\Users\o_iseri\Desktop\OpenUBEM\openubem`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/openubem)) as its core computational engine. OpenUBEM provides the production-grade geometry generators, watertight EnergyPlus IDF assembly pipelines, SLURM HPC array runners, and post-processing tools required to execute the 510-cell pre-registered simulation campaign across the 102 European residential archetypes **(clarified 2026-09-03: "510-cell / 102 archetypes" names the OpenUBEM archetype campaign, `EU-08`, on the OpenUBEM side — not this 4J Step 8 campaign, which is 88 archetypes × 5 `f`-levels × 10 diaries; see `4thJ_08_bemSimulation.md:796-799`)**.

```mermaid
flowchart TD
    subgraph GSSCanada["1. GSSCanada Pipeline (4J HETUS Step 7 -> Step 8)"]
        A1["Step 7 LLM Demographic Diaries<br/>(Spain 'es', UK 'uk', Italy 'it')"] --> A2["Presence Signals g(t)<br/>Fractional Curves [0.0, 1.0]"]
        A3["102 TABULA Archetypes (outputs_step8/)<br/>(24 ES, 36 UK, 42 IT)"] --> A4["5-Level phi_int Sweep<br/>f in {0.00, 0.15, 0.30, 0.50, 1.00}<br/>phi_int(t) = (1-f)*3.0 + f*3.0*g(t)/mean(g(t))"]
    end

    subgraph Standards["2. European & National Standards Engine (DR05, DR06, DR07)"]
        B1["Pan-European CEN/ISO: EN ISO 52016-1, EN 16798-1, EPBD 2024"]
        B2["Spain: CTE DB-HE (ES.01-06), RITE, DB-HS 3, Madrid D3"]
        B3["UK: Approved Doc L (GB.01-08), SAP 2012, CIBSE TM59, London"]
        B4["Italy: DM 26/06/2015, UNI/TS 11300 (IT.01-08), Zone E Bologna"]
    end

    subgraph OpenUBEM["3. OpenUBEM Computational Backbone (openubem/)"]
        C1["openubem.geometry.layoutGenerator<br/>Dwelling Subdivision (1x1, 2x1, 2x2, 3x2, 4x2)<br/>Unconditioned Stair Core (6% - 12% GFA)"]
        %% SUPERSEDED by D-EU-79 (2026-09-03): the stair-core fraction above is retired, no-core regime
        C2["openubem.idf.builder & opaque_assembly<br/>Parametric Insulation (U_wall, U_roof, U_window)<br/>Internal Thermal Mass Injection (c_m = 45 Wh/m2K)"]
        C3["openubem.simulation.runner & parallel<br/>EnergyPlus 9.2 Execution on SLURM Cluster<br/>(510 Injected Cells + 102 Uninjected Controls)"]
        C4["openubem.results.service_loads<br/>Simulated 4-End-Use EUI + Reconstructed Whole EUI"]
    end

    subgraph Validation["4. Pre-Registered Validation (4thJ_08_bemSimulation_val.md)"]
        D1["Gate G8.0: Uninjected Control (f = 0.00)"]
        D2["Gate G8.8: Scenario Differentiation Check"]
        D3["Gate G8.13: Interpolate to Timestep = No"]
        D4["Gate G8.16: Held-Out Fold Verification"]
        D5["OpenUBEM_debug_References.md: Diagnostic Registry (~200 Errors)"]
    end

    A3 & B1 & B2 & B3 & B4 --> C1
    C1 --> C2
    A2 & A4 --> C2
    C2 --> C3
    C3 --> C4
    C3 --> D1 & D2 & D3 & D4 & D5
```

---

## 2. European & National Building Standards Engineering Framework (`DR05` & `DR06`)

OpenUBEM's default configuration references North American commercial standards (ASHRAE 90.1, DOE Prototypes, IBC 2021). To execute the simulation of European residential building stocks, OpenUBEM is parameterized against the European Committee for Standardization (CEN), International Organization for Standardization (ISO), and national statutory building codes.

### 2.1. Pan-European Framework (CEN / ISO / EPBD)
* **Governing Directives**: Energy Performance of Buildings Directive (EPBD 2010/31/EU, Directive (EU) 2018/844, and Directive (EU) 2024/1275 Recast for Zero-Emission Buildings ZEB).
* **Dynamic Energy Calculation Standard**: **EN ISO 52016-1:2017** (*Energy performance of buildings - Energy needs for heating and cooling*), defining an hourly dynamic RC network with explicit zone-surface heat balances (superseding EN ISO 13790:2008).
* **Indoor Environmental Quality & Thermal Comfort**: **EN 16798-1:2019** (Module M1-6) Category II standard comfort bounds ($20.0^\circ\text{C}$ heating setpoint, $26.0^\circ\text{C}$ cooling setpoint).
* **Harmonized European Typologies**: Master building stock database from **TABULA / EPISCOPE** (`tabula-values.xlsx` 4.0 MB, `tabula-calculator.xlsx` 34.4 MB), covering 102 archetypes across 22 construction-year epochs.
* **Standard European Internal Heat Gain Baseline**:
  - Normative statutory baseline: Flat continuous **$3.0\text{ W}/\text{m}^2$** under TABULA EU boundary conditions (`EU.SUH`/`EU.MUH`) and **$4.0\text{ W}/\text{m}^2$** under EN ISO 13790:2008 Annex G Table G.12 and Italian UNI/TS 11300-1 Table 1.
  - This open statutory value serves as the exact uninjected control benchmark ($f = 0.00$) against which the LLM occupancy schedules are evaluated.

### 2.2. Country-Specific Regulatory Engineering Specifications

```
+-------------------------------------------------------------------------------------------------------------------+
|                        NATIONAL BUILDING REGULATION MATRIX: SPAIN, UNITED KINGDOM, ITALY                          |
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Parameter / Standard     | Spain (ES)                      | United Kingdom (GB / UK)        | Italy (IT)         |
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Primary Energy Code      | Código Técnico de la Edificación| Building Regulations Part L     | DM 26/06/2015      |
|                          | (CTE DB-HE 1979, 2006, 2013, 19)| (Approved Document L1A/L1B)     | (Requisiti Minimi) |
+--------------------------+---------------------------------+---------------------------------+--------------------+
| National Engine / Method | HULC (LIDER-CALENER)            | SAP 2012 / SAP 10.2 / RdSAP     | UNI/TS 11300 (1-4) |
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Construction Epochs      | 6 Epochs (ES.01 to ES.06)       | 8 Epochs (GB.01 to GB.08)       | 8 Epochs (IT.01-08)|
| Historical Epoch Span    | Pre-1900 to Post-2007 (CTE-79)  | Pre-1918 to Post-2010 (Part L)  | Pre-1900 to Post-06|
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Space Heating System     | Hydronic baseboard / Gas boiler | Hydronic wet radiators / Gas    | Central/individual |
|                          | or individual split heat pumps  | condensing boiler (86% share)   | hydronic radiators |
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Statutory Ventilation    | CTE DB-HS 3 (0.40 ACH)          | Approved Document F (0.59 ACH)  | UNI/TS 11300 (0.30)|
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Reference Climate Zone   | Madrid (Zone D3 / ES.ME)        | London / England (GB.ENG)       | Bologna (Zone E)   |
| Fieldwork AMY Year       | 2009-2010 Actual Weather        | 2014-2015 Actual Weather        | 2013-2014 Weather  |
+--------------------------+---------------------------------+---------------------------------+--------------------+
| Archetype Dataset Size   | 24 Archetypes (Complete 4x6)    | 36 Archetypes (29 of 32 Bins)   | 42 Archetypes      |
+--------------------------+---------------------------------+---------------------------------+--------------------+
```

---

## 3. OpenUBEM Codebase Adaptation Roadmap (`DR07`)

To bridge OpenUBEM's architecture with the European CEN/ISO and TABULA specifications, six core modules are parameterized:

```
+---------------------------------------------------------------------------------------------------------+
|                  COMPARATIVE ARCHITECTURE: US ASHRAE DEFAULTS VS. EUROPEAN CEN/ISO STANDARDS            |
+------------------------------------+---------------------------------+----------------------------------+
| Subsystem                          | OpenUBEM US Default (ASHRAE)    | Adapted European Configuration   |
+------------------------------------+---------------------------------+----------------------------------+
| Governing Energy Framework         | ASHRAE 90.1-2019 / IECC 2021    | CEN/ISO (EN ISO 52016-1, EPBD)   |
| National Archetype Source          | US DOE Prototypes (NREL)        | TABULA / EPISCOPE (102 Types)    |
| Envelope Construction & Mass       | Lightweight wood/steel-frame    | Heavy clay brick & concrete mass |
| Internal Thermal Capacity (c_m)    | Minimal internal mass node      | Explicit InternalMass (45 Wh/m²K)|
| Glazing Performance Metric         | Solar Heat Gain Coeff (SHGC)    | Total Solar Transmittance (g_gl) |
| Space Heating Distribution         | Forced-air furnace / Heat pump  | Hydronic baseboard hot-water     |
| Baseline Internal Heat Gain        | Dynamic Space-by-Space Profiles | Flat 3.0 W/m² (TABULA EU Standard|
| Residential Ventilation Rate       | ASHRAE 62.2 mechanical outdoor  | Continuous trickle (0.40 ACH)    |
| Zoning & Compartmentalization      | Commercial Core-and-Perimeter   | Multi-Dwelling + Unheated Stair  |
+------------------------------------+---------------------------------+----------------------------------+
```

> 🟡 **SUPERSEDED by `D-EU-79` (2026-09-03).** The "Zoning & Compartmentalization" row above
> ("Multi-Dwelling + Unheated Stair") names the retired core-era plan; kept as the record of what was
> considered. No-core regime: dwellings only, no unheated stair zone.

### 3.1. Module-by-Module Technical Adaptation
1. **Opaque Assembly Builder (`openubem.idf.opaque_assembly`)**:
   - Calculates insulation layer thickness ($d_{\text{ins}}$) parametrically from TABULA $U$-values ($U_{\text{wall}}, U_{\text{roof}}, U_{\text{ground}}$):
     $$d_{\text{ins}} = \lambda_{\text{ins}} \cdot \left(\frac{1}{U_{\text{target}}} - R_{\text{si}} - R_{\text{se}} - \sum \frac{d_j}{\lambda_j}\right)$$
   - Uses European standard material thermal conductivity values: outer clay brick ($\lambda = 0.79\text{ W}/(\text{m}\cdot\text{K})$), concrete panel ($\lambda = 1.40$), expanded polystyrene EPS ($\lambda = 0.038$), interior gypsum plaster ($\lambda = 0.25$).
2. **Glazing Parameterization (`openubem.idf.surfaces`)**:
   - Ingests European total solar energy transmittance ($g_{\text{gl}}$ per EN 410 / TABULA `Tab.U.Class.Window`) into EnergyPlus `WindowMaterial:SimpleGlazingSystem` setting $\text{SHGC} = g_{\text{gl}}$ and $U_{\text{factor}} = U_w$.
3. **Internal Thermal Mass Injection (`openubem.idf.builder`)**:
   - Injects explicit `InternalMass` objects ($A_{\text{mass}} = 1.5 \times A_{\text{floor}}$) into every dwelling zone calibrated to European thermal mass capacity ($c_m = 45\text{ Wh}/(\text{m}^2\cdot\text{K})$ for EU.SUH/EU.MUH, $87$ for IT, $32.8$ for GB per EN ISO 52016-1 Table B.14). This prevents numerical temperature spikes and reflects European solid interior partitions.
4. **Space Heating & Plant Loops (`openubem.idf.hvac`)**:
   - Configures hydronic baseboard convective radiators with hot-water boiler efficiency curves ($\eta_{\text{seasonal}} = 0.88\text{--}0.94$) representing European gas condensing boilers.
5. **Stochastic Schedule Coupling (`openubem.semantic.schedules`)**:
   - Generates external CSV files containing the 8,760 hourly presence multipliers and references them in the IDF using `Schedule:File` (`Interpolate to Timestep = No` per Gate **G8.13**).
6. **Weather Manager (`openubem.acquisition.epw_manager`)**:
   - Ingests ERA5 reanalysis Actual Meteorological Year (AMY) hourly weather files for Madrid (2009–2010), London (2014–2015), and Bologna (2013–2014).

---

## 4. Procedural Multi-Zone Floor Layout & Geometry Engine

> 🟡 **THIS ENTIRE SECTION (§4) SUPERSEDED by `D-EU-79` (2026-09-03).** The MFH/AB grids, the corridor
> spine, the 8 % circulation core, `b_u`, and the `units_corridor` diagram below all describe the
> retired core-era subdivision. Owner's ruling: *"a floor plate divides into dwellings only, no core,
> corridor, access band or unconditioned zone; every square metre belongs to a flat; nothing narrower
> than 2 m; one flat = one zone."* Kept as the record of what was considered; no plan below is live.

OpenUBEM's `openubem.geometry.layoutGenerator` implements the procedural spatial slicing and typological rules established in [`floor_layout_generation_report.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step8_docs/IMP_step8/outputs/floor_layout_generation_report.md) and *Iseri et al. (2025)*:

```
+---------------------------------------------------------------------------------------------------+
|                     OPENUBEM RESIDENTIAL DWELLING SUBDIVISION (units_corridor)                    |
+------------------------------------+--------------------------------------------------------------+
| Point-Block Quadrant (2x2 Grid):   | Double-Loaded Corridor Slab (3x2 / 4x2 Grid):                |
|                                    |                                                              |
| +----------------+---------------+ | +---------------+--------------+---------------------------+ |
| |  Dwelling 1    |  Dwelling 2   | | |    Unit 1     |    Unit 2    |          Unit 3           | |
| |  (North-West)  |  (North-East) | | |  (North-West) |   (North)    |       (North-East)        | |
| +--------+-------+-------+-------+ | +---------------+-------+------+---------------------------+ |
| |        |  UNCONDITIONED|       | | |===================+======+==============================| |
| | Dwell 3|  STAIR CORE   |Dwell 4| | | [CENTRAL UNCONDITIONED CIRCULATION CORRIDOR SPINE]      | |
| | (SW)   +-------+-------+ (SE)  | | |===================+======+==============================| |
| +----------------+---------------+ | |    Unit 4     |    Unit 5    |          Unit 6           | |
|                                    | | (South-West)  |   (South)    |       (South-East)        | |
|                                    | +---------------+--------------+---------------------------+ |
+------------------------------------+--------------------------------------------------------------+
```

### 4.1. Slicing Rules and Typology Mapping
* **Single-Family / Terraced (`SFH / TH`)**: 1 conditioned thermal zone per dwelling, multi-storey inter-floor coupling.
* **Multi-Family (`MFH`)**: $2\times 2$ grid (4 corner quadrant flats per floor) surrounding a central unconditioned stairwell core.
* **Apartment Blocks (`AB`)**: $3\times 2$ or $4\times 2$ grid (6 to 8 flats per floor) along a central double-loaded circulation corridor spine.
* **Circulation Core Area**: $8\%$ of gross floor area ($12.0\text{--}25.0\text{ m}^2$), unconditioned floating temperature zone ($12\text{--}16^\circ\text{C}$ winter mean, $b_u = 0.50\text{--}0.80$).
* **Windowless Unit Diagnostic**:
  $$L_{\text{exterior}} = \text{Length}\left(\partial \Omega_u \cap \partial \Omega_{\text{ext}}\right) \ge 2.50\text{ m}$$
  Automatically verifies that every generated dwelling zone maintains exterior facade contact for natural ventilation and daylight (IRC Sec R303 / Turkish Zoning Law).

---

## 5. Stochastic Occupancy Injection & 5-Level Sensitivity Sweep

### 5.1. Mathematical Ingestion Formulation
The occupancy-driven internal gain schedule $\phi_{\text{int}}(t)$ is defined by the pre-registered five-level sensitivity formula:
$$\phi_{\text{int}}(t) = (1 - f) \cdot 3.0 + f \cdot 3.0 \cdot \frac{g(t)}{\text{mean}_{8760}(g(t))}, \quad f \in \{0.00, 0.15, 0.30, 0.50, 1.00\}$$

Three fundamental properties govern this injection:
1. **Strict Energy Conservation**: Annual mean internal gain remains exactly $3.0\text{ W}/\text{m}^2$ across all five $f$-levels, ensuring differences in heating demand represent pure temporal redistribution.
2. **Uninjected Control at $f = 0.00$**: The flat $3.0\text{ W}/\text{m}^2$ run is the zero-point of the exact same sweep, eliminating structural bias between control and experimental models.
3. **Intermittent Heating Factor Preservation**: Transmission reduction factors ($0.90/0.80$ SUH, $0.95/0.85$ MUH) are maintained as transmission scalars on UA per TABULA `FINDING 57`, with **no scheduled thermostat night setback added** to avoid confounding the LOCO occupancy signal.

### 5.2. Multi-Occupant Schedule Assignment in Multi-Family Archetypes

> 🟡 **SUPERSEDED by `D-EU-79` (2026-09-03).** "Dwelling unit" below assumed the core-era MFH/AB grid
> (§4). Under no-core, the unit *is* the drawn flat directly (no corridor-served unit count); the
> per-unit independent-diary principle survives and is restated for the no-core regime as `D-IMP-3`
> (`IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` I-5).
>
> 🟢 **Corrected 2026-09-03 (`D-IMP-4`), same day.** This note first said "Step 12". **There is no
> Step 12**: the no-core campaign is **Step 10 campaign `C2`**
> (`Step10_docs/4thJ_10_nocoreRealStock.md`, gate series `G10N.x`), and the core-era campaign `C1`
> is archived at `Step10_docs/archive_C1_core_era/`. Docket:
> `IMP/docs/DONE/2026-09-03_D-IMP-4_no-step-12-fold-into-step-10.md`.

In multi-family archetypes (MFH / AB), `openubem` assigns an **independent stochastic diary** from the held-out LOCO fold population to each dwelling unit $u \in \{1, \dots, N_{\text{units}}\}$, capturing inter-household demographic heterogeneity across identical physical envelopes.

---

## 6. Simulated vs. Reconstructed EUI Methodology

OpenUBEM implements the **Simulated vs. Reconstructed EUI Accounting Framework** ([`simulated_vs_reconstructed_methodology.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/simulated_vs_reconstructed_methodology.md)):

```
+-------------------------------------------------------------------------+
|                    SIMULATED VS. RECONSTRUCTED EUI                      |
+-------------------------------------------------------------------------+
| 1. Simulated EUI (Direct EnergyPlus Output):                            |
|    EUI_sim = Heating + Cooling + Lighting + Equipment (Fans/Plugs)      |
|    - Evaluates the physics of envelope heat balance & presence.         |
|                                                                         |
| 2. Reconstructed EUI (Whole-Building Energy Total):                     |
|    EUI_reconstructed = EUI_sim + EUI_service_loads                      |
|    - Fraction-split completion adding unsimulated auxiliary loads       |
|      (Domestic Hot Water DHW, Cooking, Distribution Parasitics).        |
|    - Reconstructed using TABULA Table 4 national end-use share splits.  |
+-------------------------------------------------------------------------+
```

---

## 7. HPC SLURM Execution & Diagnostic Architecture

Simulations execute via OpenUBEM's parallel HPC array runner (`openubem.simulation.parallel`):

### 7.1. Cluster Execution Discipline (Concordia Speed Cluster)
* **Non-Login Node Execution**: All simulations submitted via `sbatch --array`, fire-and-forget.
* **Remote Shell Wrapper**: Commands wrapped with `bash -lc` to ensure proper environment loading over remote tcsh.
* **Parallel Throughput**: 16 parallel CPU cores complete the 510 campaign runs in under 15 minutes.

### 7.2. Per-Cell Manifest (`manifest.json`)
Every simulation cell writes an immutable execution manifest:
```json
{
  "cell_id": "es_ES04_MFH_f030_AMY2009",
  "fold": "es",
  "country": "Spain",
  "construction_period": "ES.04",
  "building_type": "MFH",
  "sensitivity_f": 0.30,
  "openubem_engine_version": "1.2.0",
  "archetype_idf_md5": "a8f9e2b1c4d3e5f6...",
  "schedule_file_md5": "7b8c9d0e1f2a3b4c...",
  "weather_file": "ES_Madrid_AMY2009.epw",
  "weather_file_md5": "5e6f7a8b9c0d1e2f...",
  "energyplus_version": "9.2.0",
  "energyplus_build_hash": "921312ec02",
  "platform_measured": "Linux-5.15.0-105-generic-x86_64",
  "execution_timestamp": "2026-08-22T19:45:12Z",
  "metrics": {
    "simulated_heating_eui_kwh_m2": 104.28,
    "simulated_electricity_eui_kwh_m2": 58.45,
    "reconstructed_total_eui_kwh_m2": 182.10,
    "indoor_overheating_degree_c": 0.142,
    "peak_heating_load_w_m2": 48.90,
    "peak_cooling_load_w_m2": 32.15
  }
}
```

### 7.3. Diagnostic Error Handling (`OpenUBEM_debug_References.md`)
Any EnergyPlus runtime warning or error during simulation execution is triaged directly against the ~200 documented error patterns in [`OpenUBEM_debug_References.md`](file:///C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_debug_References.md).

---

## 8. Pre-Registered Gate Conformance Matrix

| Gate ID | Gate Description | Target / Requirement | OpenUBEM Enforcement Mechanism | Status |
| :--- | :--- | :--- | :--- | :---: |
| **G8.0** | Uninjected Control | Run $f=0.00$ before any injected cell | Executed as Batch 1 via `openubem.simulation.runner`. | 🟢 READY |
| **G8.8** | Scenario Differentiation | Byte-identical outputs across scenarios = FAIL | Automated SHA-256 check across result `.csv` files. | 🟢 READY |
| **G8.9** | Stale-Output Guard | Cache invalidation on wiring/schedule change | MD5 manifest comparison in `openubem.simulation`. | 🟢 READY |
| **G8.10**| End-Use Meter Tripwire | $\sum \text{EndUses} \approx \text{Electricity:Facility} \pm 0.5\%$ | Built-in meter summation audit (`openubem.results`). | 🟢 READY |
| **G8.11**| Meter-Name Validity | No unrecognised or zero-filled meters | Regex assertion against E+ 9.2 `.mdd` output dict. | 🟢 READY |
| **G8.12**| Schedule Ingestion | Ingested schedule matches Step 7 MD5 | Saved IDF re-parsed independently from disk. | 🟢 READY |
| **G8.13**| Interpolation Setting | `Interpolate to Timestep = No` | Regex assertion on saved IDF `Schedule:File` blocks. | 🟢 READY |
| **G8.14**| Manifest Completeness | Measured platform, build hash, MD5s | Automated `manifest.json` schema validator. | 🟢 READY |
| **G8.16**| Fold Correctness | Country driven by held-out fold | Checked against Step 7 schedule metadata table. | 🟢 READY |
| **G8.15**| Convergence & Warnings | Zero severe errors; triaged warnings | Automated `.err` log parser against debug registry. | 🟢 READY |

---

## 9. Concrete Implementation Workflow & Clean Repository Layout

```
IMP_step8/
├── 4thJ_08_bemSimulation_IMP.md        <- Master Unified Implementation Specification (This File)
├── DeepResearch/                        <- 7-Part Deep Research Literature Dossier
│   ├── README.md                       <- Master Dossier Index & Synthesis
│   ├── DR01_residential_floor_layout_generation_state_of_art.md
│   ├── DR02_floor_to_unit_division_and_staircase_methods.md
│   ├── DR03_thermal_zoning_resolution_and_energy_impacts.md
│   ├── DR04_comparative_matrix_and_synthesis_for_ubem.md
│   ├── DR05_european_building_standards_and_epbd_framework.md
│   ├── DR06_national_standards_spain_uk_italy.md
│   └── DR07_adapting_openubem_to_european_standards.md
├── extracted_scripts/                   <- 57 Extracted GhPython Component Algorithms
├── outputs/                             <- Detailed Analysis & Baseline Reports Repository
│   ├── floor_layout_generation_report.md
│   ├── kbem_ankara_pipeline.py
│   ├── kbem_ankara_report.md
│   ├── simulation_results_analysis_report.md
│   └── step8_master_results_dossier.md
└── resources/                           <- Raw Data, CAD Geometry & GH Pipeline Files
    ├── 1-s2.0-S0378778825003500-main.pdf (Published Research Paper)
    ├── AllV1_updated2023June.csv to AllV4_updated2023June.csv (6,458 Simulation Runs)
    ├── KBEM_Ankara_220622.gh & Ankara_040423_Retrofit.gh
    └── KBEM_Ankara_03052022.3dm (Rhino 3D Urban Geometry)

OpenUBEM Engine Modules Consumed (C:\Users\o_iseri\Desktop\OpenUBEM\openubem\):
├── geometry/layoutGenerator.py  -> Procedural floor-to-dwelling subdivision & stairwell core
├── idf/builder.py               -> Watertight IDF assembly & envelope construction injection
├── idf/opaque_assembly.py       -> Parametric insulation thickness sizing from TABULA U-values
├── semantic/schedules.py        -> Schedule:File stochastic presence injection
├── simulation/parallel.py       -> SLURM array execution harness for 510 campaign runs
└── results/service_loads.py     -> Fraction-split EUI completion (simulated vs reconstructed)
```

---

## 10. Direction from the OpenUBEM European Locations Arc — Step 7 Decision 14 (Diary-Day Chaining Rule) — added 2026-08-23

> 🟢 **STATUS: ANSWERED AND CLOSED, 2026-08-26 (night). THIS IS NO LONGER A BLOCKER OF ANYTHING.**
> The requested experiment ran (9,000 EnergyPlus runs, re-run on rotated schedules after `D-S9-3`), the
> author ruled decision 14 on 2026-08-25, and work item 10.1 **filed the four artefacts item 10.2/6 asks
> for** at `Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md`. **Adopted convention:
> `independent`, seed 1.** The `G7.18` trigger of 25 % on peak demand is **not approached in any fold**
> — measured **0.2892 / 0.1936 / 0.0285 %** — and the seed spread beats the rule spread on every metric
> in every fold, so the pre-registered **null is the deliverable**. 🔴 **`FINDING 136`'s
> `17–60×` occupancy-to-convention comparison is WITHDRAWN** (9.4× / 0.2× / 22.6× after the rotation);
> do not quote it. The `f > 0` occupant cells (408 runs, Q4) are unblocked **by reference to the
> notice** — read it, not the request below. 🔴 **MVP §12.11's receiving step is still stale on
> the OpenUBEM side and is theirs to correct.**
>
> ---
>
> ⚪ **SUPERSEDED, KEPT AS THE RECORD OF WHAT WAS ASKED FOR.** *Status: OPEN REQUEST to the GSSCanada /
> Step 7 side. This is the only remaining blocker of the OpenUBEM European campaign.* Every other open decision was closed on 2026-08-23 (rulings D-EU-01…08/10/11 and accepted deep-research reports DR08–DR11 in `C:\Users\o_iseri\Desktop\OpenUBEM\docs\docs_ACTIVE\europeanLocations\` — see `debugs/docs/DECISIONS_parent-open-items-2026-08-23.md` and MVP §11.13). It gates **only the `f > 0` occupant cells (408 runs, Q4)**; the `f = 0` controls, Q1–Q3 and the France baseline run without it.

### 10.1 The problem

Step 7 delivers **single diary days** of at-home presence per respondent, not annual series. An annual `Schedule:File` (8,760 h) therefore requires a **chaining rule**: which diary day is placed on which calendar day (weekday/weekend matching, seasonal matching, within-household vs pooled resampling, treatment of holidays). Step 8's own pre-registration (decision 14) warns that candidate rules can differ by **> 25 % on peak demand** — a casually chosen rule would make the campaign measure the chaining convention, not the occupant effect. No literature settles it for this corpus; it is an experiment on Step 7's own diaries, which is why no DR brief was written for it.

### 10.2 Requested experiment (protocol proposal — amend freely on the Step 7 side)

1. **Candidate rules (2–3, pre-declared before any simulation):**
   - **C1 — day-type + season matched, within household:** resample the household's own diary days by {weekday/weekend} × {heating/non-heating season}; fall back to pooled only when the household has no day of that type.
   - **C2 — day-type + season matched, pooled within stratum:** resample from all households of the same country × household-size stratum.
   - **C3 (control convention) — single repeated day:** each household's one diary day tiled over the year with day-type correction only. (Cheapest; included to bound the effect.)
2. **Sample:** ~20–50 dwellings per country fold (es / uk / it), each chained under every candidate rule with a fixed RNG seed per (dwelling, rule).
3. **Simulation:** identical buildings, identical weather (the fold's ruled AMY), `f = 1.00` injection only — the rule effect is largest there.
4. **Measure:** per dwelling, the spread across rules of (a) annual heating demand and (b) annual peak heating power; report the distribution of spreads, not just the mean.
5. **Decision criterion (pre-registered):** if the across-rule spread is **< 25 % on peak and < 10 % on annual demand** for ≥ 90 % of the sample → adopt the **simplest** rule (lowest C-number that passes) and freeze it; otherwise the chaining rule becomes a **declared design factor** of the campaign (reported per rule), and the choice escalates to a user ruling.
6. **Artefacts owed back to the OpenUBEM arc:** the frozen rule text, the seed policy, the script that implements it, and the spread table — filed so the OpenUBEM director can lift the `f > 0` block by reference.

### 10.3 Constraints inherited from the pre-registration (do not violate)

- **No thermostat schedule may be introduced** by the chaining experiment (`FINDING 57` / G8-series: intermittency stays a transmission scalar; a scheduled setback would confound the LOCO occupancy signal).
- **Held-out-fold correctness (G8.16)** applies to the experiment itself: a fold's chained schedules must not use diary information from its held-out records.
- Annual mean gain must remain exactly `3.0 W/m²` after chaining at every `f` (strict energy conservation, §5.1) — chaining redistributes time, never energy.
- Leap days and DST: the ruled EPW windows are non-leap, LST without DST; the chaining script must produce exactly 8,760 rows and declare its day-boundary convention.

*Requested by the OpenUBEM European Locations arc (director session, 2026-08-23). Contact artefact: `OpenUBEM/docs/docs_ACTIVE/europeanLocations/prompts/DIRECTOR_PROMPT_european_locations.md` §4.3 (D-EU-09).*

---

## Progress Log

Append-only. Never delete or reformat an existing entry.

### 2026-09-03 — no-core review, `D-IMP-1` ruled (a): dated header and SUPERSEDED markers applied

`IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` I-1, docket
`IMP/docs/DONE/2026-09-03_D-IMP-1_D-IMP-2_D-IMP-3_nocore-review-rulings.md`. Added: a dated
no-core regime header above the title, quoting `D-EU-79`; SUPERSEDED markers on the mermaid `C1`
node, the §3 table row ("Multi-Dwelling + Unheated Stair"), the whole §4 section (MFH/AB grids,
corridor spine, 8% core, `b_u`, `units_corridor` diagram), and §5.2 (with a `D-IMP-3` pointer for
the no-core per-flat restatement); one paragraph under the `DR01`–`DR04` links; a 510-vs-88
disambiguation. Same device on `outputs/step8_master_results_dossier.md:217` and on
`outputs/floor_layout_generation_report.md` (document-level header, its core content proved
pervasive beyond the three run-book anchor lines). Check: `grep -n -i
"corridor\|circulation\|stair\|core\b\|b_u"` on the IMP file returns 33 hits, all under the
document header's blanket declaration (6 accepted false positives — generic "core" word-boundary
collisions, out of I-1's scope); perturbation seen felling on scratch copies (§4 marker removed →
6 unmarked hits exposed; document header removed on the report file → ~10 unmarked hits exposed).
No plate cut, no cell run, no EnergyPlus invoked.
