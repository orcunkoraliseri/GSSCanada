# Deep Research Dossier: Floor Layout Generation, Thermal Zoning, and European Building Standards in UBEM

This dossier contains seven comprehensive, publication-grade deep research reports investigating procedural floor layout generation, spatial subdivision, unconditioned circulation cores, zone-level building physics, and the adaptation of Urban Building Energy Modeling (UBEM) engines to European and national building standards.

```
IMP_step8/DeepResearch/
├── README.md                                                 <- Master Index and Research Synthesis
├── DR01_residential_floor_layout_generation_state_of_art.md  <- SOTA Generative Layout Paradigms
├── DR02_floor_to_unit_division_and_staircase_methods.md      <- Spatial Slicing & Staircase Physics
├── DR03_thermal_zoning_resolution_and_energy_impacts.md      <- Multi-Zone Resolution Sensitivities
├── DR04_comparative_matrix_and_synthesis_for_ubem.md         <- 25-Tool Benchmarking Matrix
├── DR05_european_building_standards_and_epbd_framework.md   <- CEN/ISO Standards & EPBD Directives
├── DR06_national_standards_spain_uk_italy.md                 <- National Codes (Spain, UK, Italy)
└── DR07_adapting_openubem_to_european_standards.md           <- OpenUBEM Parameterization Roadmap
```

---

## Index of Deep Research Reports

### 1. [`DR01: State of the Art in Residential Floor Layout Generation`](DR01_residential_floor_layout_generation_state_of_art.md)
* **Scope**: Comprehensive taxonomy across 5 computational lineages (Parametric Slicing, Space Syntax / Shape Grammars, Constraint Satisfaction / FloorSP, Deep Generative Graph Networks, ASHRAE Core-Perimeter).
* **Key Finding**: Deep generative AI (HouseGAN++, Graph2Plan) creates non-watertight vector geometry with loose tolerances ($\pm 0.05\text{ m}$) that crash EnergyPlus; parametric orthogonal slicing (`EdgeTo4` + $(U, V)$ grid) guarantees 100% simulation-grade watertightness.

### 2. [`DR02: Floor-to-Unit Division and Staircase Buffer Methods`](DR02_floor_to_unit_division_and_staircase_methods.md)
* **Scope**: Typological slicing rules (Rectangular, L-shape reflex decomposition, I-shape linear spine, U-shape courtyard), unconditioned staircase thermal buffer physics ($12\text{--}16^\circ\text{C}$ seasonal mean), and the *Windowless Unit Diagnostic* ($L_{\text{ext}} \ge 2.50\text{ m}$).
* **Key Finding**: Stairwell buffer zones moderate internal party wall transmission losses by $30\%\text{--}50\%$ ($b_u = 0.50\text{--}0.80$ per EN ISO 52016-1).

### 3. [`DR03: Thermal Zoning Resolution & Energy Sensitivity`](DR03_thermal_zoning_resolution_and_energy_impacts.md)
* **Scope**: Quantitative sensitivities of annual space heating ($Q_H$), peak heating/cooling loads, and Indoor Overheating Degree ($IOD$) to thermal zoning granularity.
* **Key Finding**: Zone-level multi-dwelling resolution captures a $+18.0\%$ increase in mean space heating demand and a $+76.7\%$ expansion in inter-dwelling energy variance across 6,458 dwelling units.

### 4. [`DR04: Comparative Matrix and Synthesis for UBEM`](DR04_comparative_matrix_and_synthesis_for_ubem.md)
* **Scope**: Benchmarking matrix comparing 25 urban modeling tools, generative frameworks, and UBEM engines across 9 evaluation dimensions.

### 5. [`DR05: European Building Standards & EPBD Framework`](DR05_european_building_standards_and_epbd_framework.md)
* **Scope**: Pan-European regulatory framework (EPBD Directives 2010/31/EU & 2024/1275 Recast), dynamic calculation standards (**EN ISO 52016-1:2017**, EN ISO 13790:2008), indoor environmental quality (**EN 16798-1:2019**), and standard thermal capacitance ($c_m = 45\text{ Wh}/(\text{m}^2\text{K})$).
* **Key Finding**: Establishes the flat continuous $3.0\text{ W}/\text{m}^2$ (TABULA EU boundary condition) and $4.0\text{ W}/\text{m}^2$ (ISO 13790 / UNI/TS 11300) baseline internal gain rates as the exact open benchmark foil.

### 6. [`DR06: National Standards: Spain, United Kingdom, and Italy`](DR06_national_standards_spain_uk_italy.md)
* **Scope**: Detailed national regulatory engineering specifications:
  - **Spain**: Código Técnico de la Edificación (**CTE DB-HE** 1979, 2006, 2013, 2019), RITE HVAC efficiencies, CTE DB-HS 3 ventilation ($0.40\text{ ACH}$), and 12 climate zones (Madrid `D3`).
  - **United Kingdom**: Building Regulations **Approved Document L1A/L1B** (Part L), **SAP 2012 / SAP 10.2**, Approved Document F, and **CIBSE TM59** overheating criteria.
  - **Italy**: Legge 373/1976 $\rightarrow$ Legge 10/1991 $\rightarrow$ **DM 26/06/2015 "Requisiti Minimi"**, **UNI/TS 11300** standard series (Parts 1–4), and Degree-Day climate zones (Zones A–F).

### 7. [`DR07: Engineering Roadmap for Adapting OpenUBEM to European Standards`](DR07_adapting_openubem_to_european_standards.md)
* **Scope**: Technical implementation blueprint for parameterizing the OpenUBEM codebase (`openubem/`) with European CEN/ISO standards, replacing US ASHRAE defaults with TABULA envelope assemblies, hydronic radiator heating systems, explicit internal mass injection ($c_m = 45\text{ Wh}/(\text{m}^2\text{K})$), and the 5-level $\phi_{\text{int}}$ sensitivity sweep.

---

## Associated Master Implementation & Results Dossiers
* **Step 8 Master Results Dossier**: [`../step8_master_results_dossier.md`](../step8_master_results_dossier.md)
* **Step 8 Implementation Specification**: [`../4thJ_08_bemSimulation_IMP.md`](../4thJ_08_bemSimulation_IMP.md)
* **Ankara KBEM Baseline Report**: [`../kbem_ankara_report.md`](../kbem_ankara_report.md)
* **Floor Layout Generation Report**: [`../floor_layout_generation_report.md`](../floor_layout_generation_report.md)

