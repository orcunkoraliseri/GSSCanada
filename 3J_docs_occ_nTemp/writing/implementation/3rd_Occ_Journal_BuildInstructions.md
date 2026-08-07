# Build Instructions — 3rd Occupancy Journal Manuscript (3J)

**Document type:** Claude Code task brief · **Date:** 2026-08-06
**Project:** GSSCanada — Journal 3 · *Leg-2 (2-split) + Leg-3 (4-split)*
**Modelled on:** `2J_docs_occ_nTemp/writing/resources/2nd_Occ_Journal_BuildInstructions.md`
**Target folder structure:** mirror of `2J_docs_occ_nTemp/writing/fullSet`

## Which project is which

| role | path | what it is for |
|---|---|---|
| **the project** | `3J_docs_occ_nTemp/` | **all content, all numbers, all figures.** Leg-2 and Leg-3 both live here |
| **reference** | `2J_docs_occ_nTemp/` | **form, not content** — structure, section pattern, table style, prose conventions. Cite its *results* only where 3J genuinely builds on them, and then only the **post-`V4-B4` corrected** values (§1.2) |
| **reference** | `eSim_writing/methodology/` | 1st-journal methodology notes: default-schedule standardization, floor-area normalization |

Nothing is written into `2J_docs_occ_nTemp/` or `eSim_writing/` by this task. They are read-only here.

---

## 0. Scope of the paper — read this before anything else

The subject is the **multi-use extension** of the pipeline: one jointly-trained occupancy model
producing several independent presence channels, injected into mixed-use tower prototypes.

**One paper. Leg-3 is the result; Leg-2 is a construction step, not a co-headline.**

| Leg | Channels | Building domain | Role in the paper |
|---|---|---|---|
| **Leg-2 (2-split)** | Residential (AT_HOME) + Office (AT_WORK) | PNNL Tall / SuperTall office zones + residential archetypes | **a step in building Leg-3.** It is where the multi-channel machinery was built and where the wiring-bug lesson was learned. It belongs in **Methods**, as the stage the four-channel model was grown from |
| **Leg-3 (4-split)** | + Retail (AT_RETAIL, GSS) + Hotel (non-GSS, tourism statistics) | PNNL **Tall + SuperTall** mixed-use towers, Montréal 6A + Calgary 7A | **the paper.** Four uses inside one stacked building — every headline result comes from here |

**What this means concretely for the writing.** Do not give Leg-2 a results section, a parallel
narrative, or equal billing in the abstract. Leg-2 appears where it does work:

- **Methods** — the two-channel stage the three-head model was grown from; the `modulate`-vs-`replace`
  distinction was settled here.
- **Methods, as a hard gate** — the Leg-2 People-field wiring bug
  (`Number_of_People_Schedule_Name`, not `Schedule_Name`) passed *every input-side check* and was only
  caught output-side. It is the reason Leg-3 runs a mandatory scenario-differentiation probe. This is
  a methods contribution, and it came from Leg-2.
- **Table 6** — the additive ledger showing residential and office paths unchanged, which is what lets
  the paper claim Leg-3 invalidates no prior figure.

**One reporting duty that survives the demotion.** Leg-2's own scorecards
(`Leg2_2-split/Step8_docs/`, `Step9_docs/`) are the evidence behind Table 6's "bit-identical" column.
Read them; do not assert the claim from the pipeline overview's prose.

### 🔴 One phrase in the brief needs correcting before it reaches the abstract

The framing sentence *"four building archetypes"* is inherited from **2J**, where the four archetypes
were SingleDetached / OtherDwelling / MidRise / HighRise. **Leg-3 has no such set.** Leg-3 is:

> **four occupancy channels** × **two tower prototypes** (Tall, SuperTall) × **two cities**
> (CAN_MTL 6A, CAN_CLG 7A) = the 56-cell Step-8 campaign.

Write the contribution as *four channels driving four uses inside one building*, not *four
archetypes*. The residential archetype set belongs to Leg-1/Leg-2 and to the 2J paper.

### What is already done

Steps 1–9 are built and run for both legs. Nothing in Leg-3 remains `PLANNED`
(`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, status convention superseded
2026-08-05 by V2-G2). Improvement rounds v0–v5 are recorded under `improvements/`.
**This brief is a writing task, not a simulation task. No cell is re-run to produce this manuscript.**

---

## 1. Prerequisites and standing hazards

These are not optional caveats — each one changes what the manuscript may claim.

### 1.1 🔴 Three EUI gates are still FAILING and stay failing

`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` § LIMITATIONS records sixteen
limitations in five groups, **fifteen of sixteen carrying a number**. Three of them are live gate
failures, and **in all three cases the band value was deliberately left where it was**:

- **L4 — Office.** The *uninjected* `Default_NECB` control scores **85.45** against a floor of
  **100**. A gate no untreated control can pass measures the band, not the model. Two explanatory
  mechanisms were tested and **both refuted (56/56 cells)**.
- **L5 — Hotel.** `S9-EUI-hotel` FAILs **28/56**, every failure **above the 300 ceiling** and every
  failure on **`Tall`**; range **203.33–318.42** (count corrected 2026-08-06 by V4-A4 against the
  frozen `outputs_step9_deliverable/`).
- **L7 — Retail.** Median-in-band rule, not all-cells; the gate was turning on **0.15 % of its floor**.

**Writing rule:** the paper reports these as findings about band applicability, at full strength.
It does **not** widen a band, re-basis a metric, or select the rule that passes. That prohibition is
a standing project rule (R1, 2026-07-21) and it is also the most defensible thing in the paper.

### 1.2 🔴 The 2J numbers this paper will cite changed on 2026-08-06

Item `V4-B4` recomputed all 6,000 runs behind 2J's Table 5. The corrected residential EUI values are
**SingleDetached 115 · OtherDwelling 100 · MidRise 108 · HighRise 78 kWh/m²·yr**, and **all four now
sit below** their NRCan SHEU bands (three of four verdicts changed).

- Any 3J sentence citing the 2J EUI magnitudes **must use the corrected values**.
- The corrected source of truth is `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`
  (Table 5 + §5.2), **not** the archived pre-`V4-B4` copies and **not**
  `writing/sharingCHV/2ndOcc_Journal.docx`, which still carries the stale table.
- The underlying cause — a double-counted demand table plus an SI-only water guard in
  `calculate_eui()` — is worth one sentence in 3J's Limitations as a *reproducibility* point, because
  Leg-3 was **verified immune** (it reads hourly meters, not the tabular summary).

### 1.3 Two blocked inputs

- **`V4-C1` severities** (five retail-quarantine lines regraded to FAIL) exist **in the code only**;
  the shipped Step-4 validator report on the cluster has not been regenerated. If the manuscript
  quotes a Step-4 scorecard count, quote the **code's** severities and say the published report
  predates them.
- **`V4-C3` / prompt `V07`** — Quebec hotel occupancy before 2019 has no open source yet. The hotel
  channel is **uninjected before 2019** and one long-run check therefore passes for a reason that has
  nothing to do with hotel behaviour. This must appear in Limitations regardless of whether `V07`
  ever returns.

---

## 2. Destination folder convention

Mirror the 2J layout exactly, under `3J_docs_occ_nTemp/writing/`:

```
writing/
  implementation/     <- this brief
  chapters/           <- Chapter_00..Chapter_08 markdown, one file per chapter
  tables/             <- Table_01..Table_NN markdown
  tables/SI/
  figures/            <- Figure_01..Figure_NN png (+ .md prompt beside each schematic)
  figures/SI/
  resources/          <- skeleton, prior-paper copies, docx exports
  fullSet/            <- the assembled single-file manuscript
```

Create folders that do not exist. **Copy, never move; never delete or overwrite a source file.**
Archive any predecessor to `archive/<name>.<YYYY-MM-DD>_pre_<reason>.md` before editing it
(standing project rule).

---

## 3. STEP 1 — Verify existing assets first (do this before writing anything)

List and report the exact filenames found in:

- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` — **the frozen deliverable**, 5 PNGs
- `Leg3_4-split/Step5_docs/outputs_step5/` — 2 PNGs
- `Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png` — graphical abstract, exists
- `Leg2_2-split/Residential-Office_Pipeline.png` — Leg-2 pipeline diagram, exists

Report back before proceeding. Do not assume a filename.

### 3.1 The two-directory hazard — RESOLVED 2026-08-06, and here is what to do about it

`Step9_docs/` contains **two** sibling directories carrying **the same 11 filenames**:
`outputs_step9_deliverable/` (frozen 2026-08-06 00:05, canonical) and `outputs_step9/`
(2026-07-31 11:42, superseded). Reading the wrong one is the `V4-A1` error: office and retail differ
by ~0.1 %, so nothing looks wrong, but **the hotel channel inverts** — 28 cells *below the floor*
versus 28 *above the ceiling*. **Both directories report "28 of 56"**, so every count-based check
passes straight through it.

**The hazard is now handled by three mechanisms. Use them; do not re-derive the comparison.**

1. **`_PROVENANCE.md` in both directories.** Each states which arm it is, the full 11-row collision
   table with md5s, and what depends on it. Read the one in whichever directory you land in.
2. **The freeze document carries an asset manifest.**
   `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` § *Step-9 deliverable assets* registers the md5 of
   every canonical figure and table.
3. **`improvements/v5/f3_asset_provenance_check.py`** verifies copied assets **by content**, so it
   still works after a file has been renamed to `Figure_07_eui_4ch.png`. Run it after STEP 4.

> ⚠️ **`outputs_step9/` is NOT deletable and must not be renamed.** It holds 8 files that exist
> nowhere else — `step9_envelope_exposure.csv` and the three `finding9_verify/` IDFs, including the
> **uninjected control** behind the office band-applicability finding. The directory is legitimately
> needed; that is precisely why the name collision cannot be engineered away.

> 🔴 **One file the check cannot cover, and it is the one that looks safest.**
> **`fig_diurnal_4ch.png` is byte-identical in both arms.** Content cannot establish its origin —
> both directories are correct answers. Two consequences:
> (a) **record its provenance at copy time**, because it cannot be recovered afterwards; and
> (b) **never generalise from it** — finding one figure identical and concluding "the two directories
> agree" is what licenses copying the other four, which do not agree.

**Deliverable for this sub-step:** in the build report, state the source directory for every asset,
and paste the output of `f3_asset_provenance_check.py`.

---

## 4. STEP 2 — Bucket A: schematics to create

Eight diagrams do not exist. For each, emit a fenced code block labelled with the figure filename,
containing a prompt suitable for Mermaid / draw.io / an image tool. Style: clean white background,
sans-serif, restrained academic palette, no decoration. Save each prompt as
`figures/<Figure_NN_name>.md` beside where the PNG will land (the 2J convention).

**Figure 1 — `Figure_01_pipeline_4split.png`** — end-to-end Steps 1–9 for the 4-split. Nine blocks.
Annotate each with its §section reference. Mark the two channels inherited from Leg-2 in one colour
and the two Leg-3 additions in another; mark the **hotel side-track as bypassing the Transformer
entirely**. Source: `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` box diagram.

**Figure 2 — `Figure_02_three_leg_roadmap.png`** — Leg-1 → Leg-2 → Leg-3, showing what each leg
added and which artefacts were reused bit-identically. This figure is what makes the *additive*
claim visible; it is the paper's structural argument in one image.

**Figure 3 — `Figure_03_three_head_transformer.png`** — shared encoder, three GSS decoder heads
(resid / AT_WORK / AT_RETAIL). Annotate: loss weights **1.0 : 0.5 : 0.3**, fixed-weight scalarization
+ **PCGrad**, `pos_weight = 49` with the **−ln 49** logit shift, warmup 5 ep → joint 15 ep,
decode T = 0.7 + 2-slot min-dwell, thresholds 0.50 / 0.40 / 0.15.
**Label the diagram "3 GSS heads + 1 non-GSS side-track" — the existing PNG's "4 heads" is shorthand
and is not authoritative.**

**Figure 4 — `Figure_04_exclusivity_projection.png`** — independent binary heads → threshold-normalized
argmax projection. Show ISR ≤ 0.5 % raw → 0 % after projection. Source: dr_L3-12.

**Figure 5 — `Figure_05_tag2_dispatch.png`** — Tag-2 exact-match routing inside one tower: apartment
tags → **REPLACE**; office / retail / guest-room tags → **MODULATE**; amenity + service/MEP →
untouched NECB baseline; missing channel → NECB fallback. Include the **hard wiring gate**
(`Number_of_People_Schedule_Name`, not `Schedule_Name`) as a call-out — this is the Leg-2 bug that
passed every input-side check.

**Figure 6 — `Figure_06_hotel_sidetrack.png`** — ISQ (QC) / CBRE (AB) monthly series → SARIMA(1,1,1)(1,1,1,12)
+ COVID indicator (2020-03…2022-06) → `hotel_multiplier(t, month, PR) = s(t) × monthly rate`.
Show `s(t)`: overnight plateau **1.00** (22:00–06:00), day trough **0.200** weekday / **0.308** weekend.
Backcast gate QC+AB 2015–2019 **MAE < 0.05**. 2030 bands 0.92 / 1.00 / 1.05.

**Figure S1 — `SI/Figure_S01_occupiable_shares.png`** — measured occupiable-area shares per tower.
Use the **corrected 2026-07-31 (Défaut 7) parse**, never the document's old table:
SuperTall · Tall — office **44.33 / 44.65 %**, hotel **26.37 / 24.91 %**, residential **22.50 / 22.40 %**,
retail **4.39 / 5.53 %**; service/MEP **20.6 / 21.4 % of gross**; totals **135,857.6 / 72,623.1 m²**.
Add a footnote that the superseded figures (40,846 / 26,750 m²) were 2.7–3.3× too small and shifted
every EUI proportionally.

**Figure S2 — `SI/Figure_S02_scenario_levers.png`** — one lever per channel: office WFH
(conservative / hybrid / fullyhybrid), retail in-store share (0.97 default / 0.90 / 1.05), hotel
SARIMA band (0.92 / 1.00 / 1.05). Residential has no lever. This is the reviewer-defusing pattern
carried from Leg-2.

---

## 5. STEP 3 — Bucket B: tables to author from project sources

**Read every number from the cited source. Do not fabricate. If a value is not found, leave the cell
blank and write `⚠ check source`.** Pre-filled values below were read on 2026-08-06 and are safe to
use; everything else must be looked up.

### Table 1 — `Table_01_gap_matrix.md` — competitor positioning
Source: `deepResearch_Resources/` dr_L3-10 report + the 2J gap matrix
(`2J_docs_occ_nTemp/writing/tables/Table_01_gap_matrix.md`).
Columns: Study | Time-series occupancy | Multi-channel (>1 use) | Calibrated behavioural model |
Forecast to a future year | Mixed-use single building | Activity/end-use resolved | Stock-scale.
Rows must include **Doma & Ouf (2023/2024)**, **Buttitta & Finn (2020)**, **Widén & Wäckelgård (2010)**
— dr_L3-10 names these three as the differentiation targets — plus **this study (Leg-3)** and
**this study (2J)** as separate rows, so the increment is visible. Bold both "this study" rows.

### Table 2 — `Table_02_channels.md` — the four channels and their provenance
Columns: Channel | Source | Derivation | Injection mode | Scenario lever.
Rows (content confirmed in the pipeline overview):
- Residential AT_HOME · GSS · Leg-1 · **REPLACE** (`Number_of_People` = HHSIZE) · none
- Office AT_WORK · GSS · Leg-2 · MODULATE NECB office density · WFH band
- Retail AT_RETAIL · GSS · **Leg-3, the one new GSS channel** ·
  MODULATE, `0.95 × peak-normalized shape` · in-store share
- Hotel · **non-GSS**, ISQ/CBRE tourism statistics · Leg-3 side-track · MODULATE guest-room schedule
  × monthly multiplier · SARIMA band

Footnote the AT_RETAIL rule frozen 2026-07-02 (OD-1):
`AT_RETAIL = (occPRE==5) | ((occACT==4) & occPRE ∈ {5,9})`, with the online-shopping leak cross-tab
still reported per cycle. Footnote that **retail staff are invisible in GSS** (logged as AT_WORK) and
therefore stay in the NECB baseline — retail models **customer presence only**.

### Table 3 — `Table_03_sim_domain.md` — simulation domain
Source: `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md` + `agg_meta.csv`.
Columns: Prototype | Total area (m²) | Cities | ASHRAE CZ | EPW | Standard | Cells.
Rows: **SuperTall 135,857.6** · **Tall 72,623.1** · CAN_MTL (6A) + CAN_CLG (7A) · NECB-2017.
Footer: **56/56 cells**, geometry-identical IDFs so EUI deltas isolate climate.

### Table 4 — `Table_04_validation_gates.md` — the gate set and its provenance
Source: pipeline overview § VALIDATION GATES (both legs).
Three sections: Tiered gates (Tier 1 distributional / Tier 2 structural / Tier 3 ASHRAE G14),
channel-specific gates, wiring + differentiation gates.
**A `Provenance` column is mandatory** and must separate:
- **ASHRAE Guideline 14** — NMBE ±5 % monthly / ±10 % hourly, CV(RMSE) 15 % / 30 % → cite the standard
- **project-chosen, set before tuning** — every `< 0.05`, ±15 %, ≤ 1 h, the 0.06–0.10 retail rate,
  hotel MAE < 0.05, ISR ≤ 0.5 %, decode thresholds, and the ±2 pp EUI-share gate
- **heuristic** — PR-AUC ≥ 0.15, F1 ≥ 0.25

This column is the honesty of the paper. Never cite a project-chosen threshold to the literature.

### Table 5 — `Table_05_eui_bands.md` — per-channel EUI vs plausibility bands
Source: `Step9_docs/outputs_step9_deliverable/` **only**, plus dr_L3-02 / dr_L3-03.
Columns: Channel | as-modelled band (PASS criterion) | empirical band (INFO criterion) |
measured range | cells passing | verdict.
Known values: retail as-modelled **[80, 110, 155]**, empirical **[150, 280, 380]**;
hotel as-modelled **[180, 240, 300]**, empirical **[220, 350, 480]**;
hotel measured **203.33–318.42**, **28/56 FAIL**, all above the ceiling, all `Tall`.
Office row must carry the **uninjected control at 85.45 against a floor of 100**.
Report **dual-basis EUI** (CFA primary + occupiable-GFA share) per dr_L3-10.

### Table 6 — `Table_06_leg2_leg3_delta.md` — what Leg-3 added
Columns: Pipeline step | Leg-2 artefact | Leg-3 change | Bit-identical? | Evidence.
This table carries the *additive* claim: residential and office paths are unchanged, so **no prior
figure is invalidated**. Every "bit-identical" cell needs a file or md5 behind it, not an assertion.

### Table 7 — `Table_07_limitations.md` — the sixteen limitations
Source: `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` → **LIMITATIONS — CONSOLIDATED**.
**Do not re-write them here — transcribe.** Two copies of a limitations list drift, and the drifted
one is always the one a reviewer reads.
Columns: ID | Group | Statement | Bounding measurement.
Groups: **A Frame** (L1–L3) · **B Reference bands** (L4–L8) · **C Internal gains** (L9–L11) ·
**D Method conventions** (L12–L14) · **E Physical model** (L15–L16).
**L15 must stay marked *not quantified*** — it is the only one without a number and inventing one
would destroy the point of the table.

### Tables A1–A2 — `SI/Table_A1_A2.md` — model card + retail codebook
A1: three-head architecture, conditioning vector, training regimen (dr_L3-11/12/13), gate record.
A2: AT_RETAIL derivation per cycle — 2005/2010 `PLACE = 06+07`, 2015 `LOCATION = 306`,
2022 `LOCATION = 3306`; note grocery vs merchandise **not separable** in 2015/2022.

### Table B1 — `SI/Table_B1_improvement_rounds.md` — v0…v5 disclosure ledger
Source: `improvements/v0…v5/` plan docs and their Progress Logs.
Columns: Round | Items | Done | Withdrawn | Blocked | Gates moved | Bands moved | Headline finding.
**"Bands moved" must read 0 in every row.** This table is the paper's strongest methodological
claim: an improvement process that never resolved a failure by moving the target.

### Appendix C — `SI/Appendix_C_corrections.md` — documented corrections
One numbered entry each, with *what it was, why it needed correcting, how it was resolved, and
whether any reported result moved*. At minimum: Défaut 7 (tower surfaces, 2.7–3.3×);
the retail density conversion-factor error (B-11 retired — 3.72 occ/1000 ft² **is** 24.97 m²/person;
the real defect is retail running the **office** 24.97 where NECB gives **29.97**, ≈ 20 % over-crowded,
and NECB schedule type C never loaded); the unsourced **0.95** peak against NECB retail's **0.80**;
the retail episode-time share (**1.50–2.14 %, ≈ 25 % decline**, not "stable"); the Richardson
attribution correction (V2-C8); the `dr_L3-03` primaries that **do not exist** (PNNL-28543 resolves to
a nuclear-fuel report) and the first-party replacement (DOE/PNNL Large Hotel 90.1-2019,
**284.44 kWh/m²·yr** CZ 6A / **299.28** CZ 7); and the `V4-B4` 2J EUI extraction defect with its
Leg-3 immunity argument.

---

## 6. STEP 4 — Bucket C: relocate existing result figures

Copy from `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` — **the deliverable directory,
confirmed in STEP 1** — into `writing/figures/`:

| Manuscript label | Source file | Destination |
|---|---|---|
| Figure 7 | `fig_eui_4ch.png` | `figures/Figure_07_eui_4ch.png` |
| Figure 8 | `fig_diurnal_4ch.png` | `figures/Figure_08_diurnal_4ch.png` |
| Figure 9 | `fig_peakhour_4ch.png` | `figures/Figure_09_peakhour_4ch.png` |
| Figure 10 | `fig_longitudinal_4ch.png` | `figures/Figure_10_longitudinal_4ch.png` |
| Figure 11 | `fig_scenario_4ch.png` | `figures/Figure_11_scenario_4ch.png` |
| Graphical abstract | `Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png` | `figures/graphicalAbstract.png` |
| Figure S3 | `Leg2_2-split/Residential-Office_Pipeline.png` | `figures/SI/Figure_S03_leg2_pipeline.png` |

Record the source directory for each in the build report, then **run the content check**:

```
py -3 improvements/v5/f3_asset_provenance_check.py
```

Expected: **5 PASS / 0 FAIL**, with `fig_diurnal_4ch.png` listed as AMBIGUOUS. A **C1 failure names the
asset and the superseded original it came from** — re-copy that file from the deliverable directory
and re-run. A **C2 failure** means an asset matches neither arm: it was regenerated, edited, or came
from somewhere else, and that must be explained in the build report rather than waved through.

If any figure needs regenerating, that is a **separate task requiring authorisation** — it is not part
of this brief.

---

## 7. STEP 5 — Bucket D: chapter skeleton

One file per chapter in `writing/chapters/`, following the 2J naming
(`Chapter_00_FrontMatter.md` … `Chapter_08_Conclusion.md`). Section depth: `#` for chapters,
`###` for numbered subsections — the 2J convention exactly.

**Working title (draft):** *From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for
Mixed-Use Building Energy Simulation (Canada, 2005–2030)*

- **1 Introduction** — 1.1 the multi-use gap (single-channel occupancy in stacked buildings);
  1.2 two literatures that rarely meet, now with the mixed-use axis added; 1.3 behaviour is
  non-stationary **per use**, and the uses move in different directions; 1.4 the authors' prior line
  (Leg-1 → 2J → Leg-2), the departure point; 1.5 contributions.
- **2 Datasets** — GSS Time-Use cycles; Census PUMF; **provincial tourism statistics (ISQ, CBRE)** as
  a non-survey channel source; NECB/PNNL prototypes; weather.
- **3 Methods** — 3.1 harmonization + the AT_RETAIL derivation; 3.2 the three-head Transformer;
  3.3 linkage and the population-level retail/hotel fallbacks; 3.4 forecasting + the hotel SARIMA
  side-track; 3.5 Tag-2 dispatch and modulate-vs-replace; 3.6 end-use loads.
- **4 Experimental Design** — towers, cities, the 56-cell campaign, the scenario levers, and the
  **two mandatory probes** (scenario-differentiation; stale-output guard).
- **5 Results** — 5.1 four channels move differently over 2005–2030 (the driver); 5.2 per-channel EUI
  and the band verdicts, **including the three failures**; 5.3 load-shape and peak-hour behaviour in a
  stacked building; 5.4 scenario sensitivity, one lever per channel.
- **6 Discussion** — what a multi-channel model buys; why the office band failure is a finding about
  band applicability rather than a model error, evidenced by the **uninjected control**.
- **7 Limitations** — the sixteen, transcribed from the consolidated section.
- **8 Conclusion.**

### Prose rules carried from 2J
- No em dashes or en dashes in text that came back from an external research tool.
- Keep **as-modelled** and **empirical** figures strictly separate; never average them.
- Every number in the prose must be traceable to a table, and every table cell to a file.
- A failing gate is stated with its number in the sentence that states it.

---

## 8. STEP 6 — Assembly

Assemble into `writing/fullSet/3J_full_manuscript.md`, following the 2J pattern
(`2J_docs_occ_nTemp/writing/fullSet/archive/assemble.ps1` is the working precedent).
Keep a single-file `readySubmission.md` as the submission copy, and archive every predecessor before
overwriting.

> ⚠️ **The 2J lesson:** `2J_full_manuscript.md` and `readySubmission.md` silently diverged — one was
> built on a superseded campaign, both carried the same modification date, and the difference was
> invisible until each table was rebuilt from its own data. **Either assemble both from one source, or
> record the campaign identifier inside each file.**

---

## 9. STEP 7 — Final build report

```
## 3J build status report

### STEP 1 — Asset verification
- deliverable figures found: [list]
- source directory used for every result figure: [path]
- f3_asset_provenance_check.py output: [paste; expect 5 PASS / 0 FAIL]
- provenance recorded for fig_diurnal_4ch.png (the check cannot see it): [source dir]

### Bucket A — Schematics (8)
- [ ] Fig 1 pipeline   [ ] Fig 2 roadmap   [ ] Fig 3 three-head   [ ] Fig 4 projection
- [ ] Fig 5 tag2       [ ] Fig 6 hotel     [ ] Fig S1 shares      [ ] Fig S2 levers

### Bucket B — Tables (10)
- [ ] T1 gap  [ ] T2 channels  [ ] T3 domain  [ ] T4 gates  [ ] T5 EUI bands
- [ ] T6 leg2/leg3 delta  [ ] T7 limitations  [ ] A1-A2  [ ] B1 rounds  [ ] Appendix C

### Bucket C — Relocations (7)
[✓ relocated / ✗ source not found, with source path each]

### Bucket D — Chapters (9)
[✓ drafted / ✗ blocked]

### Flags
- values left blank with `⚠ check source`: [list]
- any place a project-chosen threshold was at risk of being cited to the literature
- confirmation that no band value was moved and no gate verdict was changed
```

---

## 10. Hard rules for whoever executes this

1. **No simulation.** No `sbatch`, no campaign cell, no EnergyPlus run. This is a writing task.
2. **Never resolve a gate by picking the rule that passes.** (R1, 2026-07-21.)
3. **Read from `outputs_step9_deliverable/`**, and prove it with
   `improvements/v5/f3_asset_provenance_check.py` rather than asserting it. The identically-named
   superseded directory has already caused one inverted result (§3.1).
4. **Do not fabricate a number.** `⚠ check source` in a cell is a successful outcome; an invented
   value is not.
5. **Archive before editing**, and keep corrections additive — strike through, do not delete.
6. **Deep research is external.** If the manuscript needs a source it does not have, the deliverable
   is a `V<NN>` prompt in `deepResearch_Resources/`, not an answer.
