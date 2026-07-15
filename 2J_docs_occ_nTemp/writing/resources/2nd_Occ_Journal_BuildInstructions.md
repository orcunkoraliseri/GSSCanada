# Build Instructions — 2nd Occupancy Journal Manuscript
**Document type:** Claude Code task brief · **Date:** 2026-06-10
**Project:** GSS Occupancy Pipeline — Journal 2 (*From "How Much" to "When"*)
**Read alongside:** `2nd_Occ_Journal_Skeleton.md` (the manuscript skeleton; all figure/table references below map to that document)

---

## Context for the agent

This is the second paper in a series on Canadian residential occupancy modelling. The full pipeline runs from four GSS Time-Use cycles (2005–2030) through a gate-selected conditional Transformer generator, a Census linkage, a longitudinal forecast, and 6,000 paired EnergyPlus runs. All simulation campaigns are complete and verified (Step-8 v2 and Step-9, both 2026-06-10). The task is to assemble the manuscript figure and table set. There are three buckets of work:

- **Bucket A:** Schematics that do not yet exist — create prompts or diagrams.
- **Bucket B:** Tables that need to be authored as markdown from the project source documents.
- **Bucket C:** Result figures that already exist on disk — verify filenames, then relocate/copy to the manuscript folder.

**Destination folder convention:**
- Main figures → `manuscript_2/figures/`
- Supplementary figures → `manuscript_2/figures/SI/`
- Tables → `manuscript_2/tables/`

Create these folders if they do not exist. Do not delete or overwrite any source file — copy only.

---

## STEP 1 — Verify existing figure assets (do this first)

Before relocating anything, list the contents of the following source folders and confirm which files are present:

- `outputs_step8_v2/figures/` — Step-8 whole-building occupancy results
- `Step9_docs/figures/` — Step-9 activity/equipment/lighting results (corrected campaign)
- `outputs_step9/` — Step-9 diagnostic outputs

Report back the exact filenames found. The internal asset names in Bucket C below (`fig01`, `figS6`, etc.) are shorthand from the figure guides; the actual filenames on disk may have descriptive suffixes. Match them by the shorthand prefix.

---

## STEP 2 — Bucket A: Schematics to create

These eight figures do not exist yet. For each one, generate a prompt suitable for a web-based diagramming or LLM image tool (Mermaid, draw.io, DALL-E, or similar). Output each prompt as a fenced code block labelled with the figure name so it can be copy-pasted directly into the tool. Style guidance: clean white background, sans-serif font, blue/grey colour scheme consistent with academic figures, no decorative elements.

---

### Figure 1 — `Figure_01_pipeline.png`
**End-to-end pipeline overview (Steps 1–9)**

Block-flow diagram. Left-to-right or top-to-bottom. Nine labelled blocks connected by arrows:

1. **GSS Time-Use (4 cycles)** + **Census PUMF** — data inputs, shown as cylinders or document icons
2. **Step 2–3: Harmonization & 30-min diary** — rectangle; annotate "64,061 diaries · 14-category scheme · 48 × 30-min slots"
3. **Step 4: Generative augmentation (calibrated J3)** — rectangle; annotate "~192,183 diary-days · gate-selected Transformer"
4. **Step 5: Census–GSS linkage** — rectangle; annotate "144,507 households"
5. **Step 6: Longitudinal forecast to 2030** — rectangle; annotate "True-Future-Test · progressive fine-tuning"
6. **Step 7: BEM schedule conversion** — rectangle; annotate "4 × Schedule:Compact channels"
7. **Step 8: Paired EnergyPlus simulation** — rectangle; annotate "6,000 runs · 4 archetypes × 6 cities × 5 years"
8. **Step 9: Activity-resolved end-use loads** — rectangle; annotate "48/48 cells ≤ ±2.7 % of SHEU"
9. **Outputs: Load-shape metrics + EUI** — output node (rounded rectangle or parallelogram)

Label each block with its §section reference from the skeleton (§2, §3.1, §3.2 … §3.6). Show the section number in small text below each block name.

---

### Figure 2 — `Figure_02_dataprep.png`
**Dataset preprocessing and harmonization flow**

Detailed flow diagram. Shows the journey from raw microdata to the analysis-ready 48 × 30-min diary. Include:

- Four input lanes (one per GSS cycle: 2005, 2010, 2015, 2022), each with a sample-size annotation (19,221 / 15,114 / 17,390 / 12,336)
- A funnel or merge block labelled "1,440-min closure filter → 64,061 valid diaries"
- Block: "Cross-cycle schema harmonization → 14-category activity scheme (0.00 % unmapped)"
- Block: "Episode → HETUS 144 × 10-min tiling"
- Block: "Presence-priority majority-vote downsample → 48 × 30-min slots (3-way tie rate 0.82 %)"
- A terminal annotation: "04:00 → 00:00 circular shift (diary origin → simulation clock)"
- DDAY_STRATA output: Weekday / Saturday / Sunday

Show Census PUMF as a parallel input lane that joins at Step 5 (does not go through the diary preprocessing).

---

### Figure 3 — `Figure_03_J3_architecture.png`
**Calibrated-J3 conditional generator architecture**

Neural-network architecture diagram. Components from left (input) to right (output):

- **Input block:** 48-slot multivariate diary token stream (observed day-type)
- **Conditioning vector block:** 90-dimensional vector — demographics, cycle-year, COLLECT_MODE, ATTSCH, POWST (work-from-home), MODE — injected at both encoder and decoder (show two arrows)
- **Shared Transformer encoder:** 6 layers, label "d_model = 384, ~29.25 M params"
- **Split to two decoder heads** (show a fork):
  - Left head: **Autoregressive (AR) activity decoder** — 6 layers → 14-category activity sequence (48 slots)
  - Right head: **Non-autoregressive (NAT) binary heads** — AT_HOME head + 9 co-presence heads, behind a **gradient-detach barrier** (show as a dashed line or stop-gradient symbol)
- **Terminal block:** Post-hoc marginal raking — "per (cycle × stratum × slot), Phase-8B" → calibrated diary-day output

Annotate the hard gates inline: "activity JS ≤ 0.05 · AT_HOME RMS ≤ 5.3 pp · co-presence max ≤ 5.0 pp · sole 4/4-gate model"

---

### Figure 4 — `Figure_04_schedule_integration.png`
**Occupancy-to-EnergyPlus schedule integration**

Process diagram. Shows how one calibrated diary-day becomes four EnergyPlus `Schedule:Compact` channels. Steps:

1. **Input:** Predicted 30-min AT_HOME fraction + 14-category activity sequence (48 slots)
2. **Clock alignment block:** "04:00 → 00:00 circular shift · `np.roll(..., 4)`" — show explicitly; this is the bug-fix
3. **Mapping block:** Activity → MET via ASHRAE 55 / ISO 7730 / 2024 Compendium
4. **Four output channels** (show as four parallel output lanes):
   - Occupancy fraction (from AT_HOME)
   - Metabolic rate (from activity → MET)
   - Equipment load (from activity crosswalk + co-presence scaling)
   - Lighting (binary occupied-and-awake × SHEU scale)
5. **Day-completion note:** Donor-draw preserves the calibrated weekend marginal
6. **Output:** Per-household `Schedule:Compact` IDF block → EnergyPlus simulation

---

### Figure S1 — `SI/Figure_S01_search_funnel.png`
**Gated generative architecture search (40+ trials)**

Funnel or decision-tree diagram. Three stages of the progressive data funnel:

- **Stage 1 (2 % data):** Wide funnel mouth — all 40+ model families enter: Markov, AR, VAE, GAN-adjacent, cross-attention, masked discrete diffusion (MDLM/SEDD)
- **Stage 2 (20 % data):** Funnel narrows — survivors annotated
- **Stage 3 (100 % data):** Funnel narrows further → final evaluation

Four hard gates shown as horizontal filter bars across the funnel:
1. Activity distribution JS ≤ 0.05
2. AT_HOME RMS ≤ 5.3 pp
3. Co-presence max ≤ 5.0 pp
4. Composite score threshold

Two call-out boxes at the bottom:
- **"Calibrated J3 — PASS (4/4 gates)"** — highlighted in green
- **"MDLM — best composite score (0.559) but FAIL (2/4 gates)"** — highlighted in amber
- Note: "Best-training-loss cross-attention: collapsed 20+ pp co-presence at inference (exposure bias)"

---

### Figure S2 — `SI/Figure_S02_linkage.png`
**Census–GSS probabilistic linkage workflow**

Converging two-lane flow diagram (method = slot-native 4-tier demographic key-descent match; NOT K-means/Random-Forest — that was the superseded 1st-journal pipeline):

- **GSS lane:** Augmented GSS diary-days (~192,183) → per-day-type donor pools (Weekday / Saturday / Sunday strata)
- **Census lane:** Census PUMF 2021 (286,537 individuals) → demographics (7 match keys) + dwelling variables carried from the matched record
- **Central match:** 7 match keys — AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA (+ day-type stratum); four descending tiers — Tier-1 Perfect (all 7 + stratum) 44.94 % / Tier-2 Core (AGEGRP, SEX, LFTAG, PR + stratum) 21.39 % / Tier-3 Constraints (AGEGRP, SEX + stratum) 33.67 % / Tier-4 FailSafe (stratum only) 0.00 %
- **Post-match:** per-slot MAX AT_HOME household aggregation → plausibility gate

Terminal block: "Plausibility gate (mean HH AT_HOME < 0.30) → removes 1,082 households → **144,507-household frame**"

---

### Figure S3 — `SI/Figure_S03_forecasting.png`
**Progressive fine-tuning and True-Future-Test protocol**

Timeline diagram. Horizontal time axis with five nodes: 2005, 2010, 2015, 2022, 2030.

For each transition show:
- A **weight-inheritance arrow** (solid, labelled "fine-tune")
- A **holdout test arrow** (dashed, labelled "True-Future-Test on unseen cycle")
- A **DRIFT_MATRIX block** at each transition
- Recency weights annotated at each node: 0.10 / 0.20 / 0.30 / 0.40

At the 2030 node show:
- "StatCan M1 scenario injection — 37,008 diary-rows"
- "AGEGRP resampling · POWST (WFH) shift"

Add a validation call-out: "WD JS = 0.0630 PASS · weekend ceiling 0.16 data-intrinsic"

---

### Figure S4 — `SI/Figure_S04_enduse_model.png`
**Activity-driven end-use load model structure**

Two-tier vertical diagram:

**Tier 1 — Flat baseload (top box):**
"24/7 non-behavioural: fridge 448 kWh + freezer 343 kWh + standby ~400–430 kWh · never occupancy-modulated"

**Tier 2 — Transient activity tier (main body):**
- 14-category activity sequence (input)
- 9-end-use × 14-activity crosswalk (show as a small matrix icon)
- Co-presence effective-occupancy scaling block:
  - Shared devices (cooking, dishwasher, washer, dryer, TV): EFF(N) = 1.0 / 1.4 / 1.7 / 1.9 / 2.0
  - Personal devices (PC, hair-dryer, DHW): linear scaling
- Per-end-use SHEU calibration scalar: `f_e = SHEU_target_e / simulated_annual_e`

**Output:** Equipment + lighting time-series → EnergyPlus schedule channels

Annotate: "48/48 cell-years ≤ ±2.7 % of SHEU · max +2.33 % equipment · +2.63 % lighting"

---

## STEP 3 — Bucket B: Tables to author from project source documents

For each table below, read the cited source documents from the project folder and produce the table as a markdown file. Do not fabricate numbers — read them from the source. If a value is not found, leave the cell blank and add a `⚠ check source` annotation.

---

### Table 1 — `Table_01_gap_matrix.md`
**Six-dimension competitor positioning matrix**

Source: `methodology_assessment_and_paper_skeleton.md` (Part 2, the literature matrix section)

Columns: Study | Time-series occupancy | Calibrated behavioural model | Forecast to future year | Activity & end-use resolved | Stock-scale | Load-shape & peak focus

Rows (at minimum): Richardson et al. 2010 · Widén & Wäckelgård 2010 · Aerts et al. 2014 · Armstrong et al. 2009 · Osman et al. 2023 · Reinhart & Cerezo Davila 2016 · Chen et al. 2022 · Yin et al. 2025 · **This study** (all ✓)

Use ✓ / ✗ / partial as cell values. Bold the "This study" row.

---

### Table 2 — `Table_02_gss_cycles.md`
**GSS Time-Use cycle summary**

Source: `methodology_assessment_and_paper_skeleton.md` (Step 1–2 section) and `00_GSS_Occupancy_Pipeline.md`

Columns: Cycle year | n valid diaries | DIARY_VALID exclusion % | Weighted AT_HOME % | Collection mode | TUI_10 available

Rows: 2005 | 2010 | 2015 | 2022 | **Total**

Values to fill: 19,221 / 15,114 / 17,390 / 12,336 · exclusions 1.92 / 1.79 / 0.00 / 0.00 % · AT_HOME 62.7 / 62.3 / 64.5 / 70.6 % · modes CATI / CATI / CATI / EQ · total 64,061

---

### Table 3 — `Table_03_sim_domain.md`
**Simulation domain: archetype × city × climate zone**

Source: `methodology_assessment_and_paper_skeleton.md` (Step-8 section) and `00_GSS_Occupancy_Pipeline.md`

Columns: City | Province | ASHRAE climate zone | TMY weather file (EPW) | Archetype standard

Rows: Toronto · Kelowna · Vancouver · Montréal · Calgary · Winnipeg

Note at bottom: "4 archetypes per city: SingleDetached, OtherDwelling, MidRise, HighRise (NECB17/NBC936 Z6). Atlantic provinces mapped to Montréal EPW — stated limitation."

---

### Table 4 — `Table_04_paired_design.md`
**Paired frozen-frame experimental design**

Source: `methodology_assessment_and_paper_skeleton.md` (Step-8 / experimental design section)

Two-section table:

Section A — Held constant: IDF geometry & envelope (all 5 cycle-years) | TMY weather file (all 5 cycle-years) | Household IDs (SIM_HH_ID) — **two independent fixed panels**, each held constant only *within* its own cycle-years: (i) 2005/2010/2015, N = 50 sampled from the original 144,507-household frame; (ii) 2022/2030, a *separate* N = 50 sampled from the refined 144,465-household frame (2026-07-09 region-tier relink). Household identity is not carried across the two panels. | n per cell (50 households per panel)

Section B — Varied: Occupancy time-series (one per cycle-year) | Cycle-years: 2005 / 2010 / 2015 / 2022 / 2030

Footer: "Total runs = 4 archetypes × 6 cities × 5 years × 50 households = 6,000. Within-household differencing removes between-household MC variance *within each panel*; cross-year Δ is purely the predicted behavioural change for comparisons made within a panel (2005↔2010↔2015 among themselves; 2022↔2030 between themselves). The 2015→2022 transition crosses the panel boundary and is a cross-sectional, not within-household, comparison."

Note DX-coil footnote: "1 of 6,000 runs (OtherDwelling × Kelowna 5B × 2010) required a DX-coil sizing fix (Sub-step 8G); effect ≤ 0.013 kWh/m²."

---

### Table 5 — `Table_05_eui_sheu.md`
**Annual EUI vs NRCan SHEU plausibility bands**

Source: `methodology_assessment_and_paper_skeleton.md` (Q1.2 + Step-8 v2 outputs)

Columns: Archetype | Simulated EUI (kWh/m²) | NRCan SHEU lower band | NRCan SHEU upper band | Within band?

Rows: SingleDetached 208 · MidRise 152 · OtherDwelling 128 · HighRise 117

Footer: "Values from Step-8 v2 corrected campaign, verified 2026-06-10. Ordered by envelope-to-occupant ratio (colder zones higher)."

---

### Tables A1–A3 — `SI/Table_A1_A2_A3.md`
**End-use load model reference tables**

Source: Step-9 docs in the project folder (search for `09_activityDrivenLoads.md` or equivalent)

- **A1:** 9-end-use × 14-activity weight matrix (rows = end uses, columns = activity categories, cells = fractional weights)
- **A2:** Appliance wattages + sub-30-min prorating rules
- **A3:** Baseload roster: fridge 448 kWh, freezer 343 kWh, standby ~400–430 kWh, with source/basis noted

---

### Tables B1–B2 — `SI/Table_B1_B2.md`
**Generator model card and activity codebook**

Source: Step-4 docs and Step-2 docs in the project folder

- **B1 (model card):** Architecture (encoder/decoder layers, d_model, n_params) · conditioning vector d_cond = 90 (list variables) · training protocol · hard gate thresholds · raking procedure · 4/4-gate pass record
- **B2 (codebook):** 14-category activity scheme with category name, code(s), raw-code count (magnitudes: 182/264/64/121), and co-presence columns (10 raw → 9 unified; note `colleagues` not collected 2005/2010)

---

### Tables C1–C2 — `SI/Table_C1_C2.md`
**Validation scorecards**

Source: `00_GSS_Occupancy_Pipeline.md` and per-step validation reports in the project folder

- **C1:** Per-step validation summary: Step | Key gate | Metric | Value | Pass/Fail — for Steps 1–9
- **C2:** True-Future-Test results: Phase | Train cycles | Test cycle | WD JS | Weekend JS | Pass/Fail; plus DRIFT_MATRIX outputs (AT_HOME shift per transition)

---

### Appendix D — `SI/Appendix_D_deviations.md`
**Documented deviations and corrections**

Source: `methodology_assessment_and_paper_skeleton.md` (Q2 deviations table) and Step-9 docs

List each documented deviation as a numbered entry:
- D1: Derived apartment SHEU targets (MidRise/HighRise not directly in SHEU — derivation method)
- D8: Multi-unit fridge correction (gross vs net 3,700/3,252 kWh)
- R1: Lighting definition (binary occupied-and-awake, no daylight gate)
- R4: Fridge gross/net correction
- MARSTH/LFTAG: NaN handling protocol
- 8G: DX-coil sizing fix (OtherDwelling × Kelowna × 2010)

For each: describe what it is, why it was needed, how it was resolved, and whether it affects any reported result.

---

## STEP 4 — Bucket C: Relocate existing figures

After completing STEP 1 (filename verification), copy each file below from its source to its manuscript destination. Use the exact filenames you confirmed in STEP 1 — do not use the shorthand names below if the real names differ.

| Manuscript label | Internal shorthand | Source folder | Destination filename |
|---|---|---|---|
| Figure 5 | `fig01` | `outputs_step8_v2/figures/` | `manuscript_2/figures/Figure_05_occupancy_driver.png` |
| Figure 6 | `fig10` | `outputs_step8_v2/figures/` | `manuscript_2/figures/Figure_06_eui.png` |
| Figure 7 | `fig02` | `outputs_step8_v2/figures/` | `manuscript_2/figures/Figure_07_diurnal.png` |
| Figure 8 | `fig04` | `outputs_step8_v2/figures/` | `manuscript_2/figures/Figure_08_paired_delta.png` |
| Figure 9 | `fig09` | `outputs_step8_v2/figures/` | `manuscript_2/figures/Figure_09_longitudinal.png` |
| Figure 10 | `fig08` | `outputs_step8_v2/figures/` | `manuscript_2/figures/Figure_10_ensemble.png` |
| Figure 11 | `figV1` | `Step9_docs/figures/` | `manuscript_2/figures/Figure_11_validation.png` |
| Figure 12 | `figS6` | `Step9_docs/figures/` | `manuscript_2/figures/Figure_12_equip_shape.png` |
| Figure S5 | `fig02b` | `outputs_step8_v2/figures/` | `manuscript_2/figures/SI/Figure_S05_diurnal_archetype.png` |
| Figure S6 | `fig03` | `outputs_step8_v2/figures/` | `manuscript_2/figures/SI/Figure_S06_peak_hour.png` |
| Figure S7 | `fig05` | `outputs_step8_v2/figures/` | `manuscript_2/figures/SI/Figure_S07_seasonal.png` |
| Figure S8 | `fig06` | `outputs_step8_v2/figures/` | `manuscript_2/figures/SI/Figure_S08_carpet.png` |
| Figure S9 | `fig07` | `outputs_step8_v2/figures/` | `manuscript_2/figures/SI/Figure_S09_delta_cz.png` |
| Figure S10 | `figS1` | `Step9_docs/figures/` | `manuscript_2/figures/SI/Figure_S10_calibration.png` |
| Figure S11 | `figS3` | `Step9_docs/figures/` | `manuscript_2/figures/SI/Figure_S11_sheu_pct.png` |
| Figure S12 | `figS7` | `Step9_docs/figures/` | `manuscript_2/figures/SI/Figure_S12_peak_shift_null.png` |
| Figure S13 | `figS8` | `Step9_docs/figures/` | `manuscript_2/figures/SI/Figure_S13_light_shape.png` |
| Figure S14 | `figS5` | `Step9_docs/figures/` | `manuscript_2/figures/SI/Figure_S14_differential.png` |
| Figure S15 | `figS4` | `outputs_step9/` | `manuscript_2/figures/SI/Figure_S15_sleep_check.png` |

---

## STEP 5 — Final report

After completing all steps, produce a short status report:

```
## Build status report

### Bucket A — Schematics (8 figures)
- [ ] Figure 1: pipeline
- [ ] Figure 2: dataprep
- [ ] Figure 3: J3 architecture
- [ ] Figure 4: schedule integration
- [ ] Figure S1: search funnel
- [ ] Figure S2: linkage
- [ ] Figure S3: forecasting
- [ ] Figure S4: end-use model

### Bucket B — Tables (9 items)
- [ ] Table 1: gap matrix
- [ ] Table 2: GSS cycles
- [ ] Table 3: simulation domain
- [ ] Table 4: paired design
- [ ] Table 5: EUI vs SHEU
- [ ] Tables A1–A3: end-use model
- [ ] Tables B1–B2: model card + codebook
- [ ] Tables C1–C2: validation
- [ ] Appendix D: deviations

### Bucket C — Relocations (19 figures)
[list each as ✓ relocated / ✗ source not found]

### Flags
[any filename mismatches or missing source files found in STEP 1]
```
