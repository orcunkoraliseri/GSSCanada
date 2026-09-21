# Deep-Research Synthesis Report (dr_2J-04)

**Manuscript Title:** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*  
**Authors:** O.K. Iseri, C. Hachem-Vermette, Concordia University, Montreal, Canada  
**Synthesis Role:** Submission strategist and scientific editor adjudicating between `dr_2J-01` (Fit & Review Burden), `dr_2J-02` (Rejection Diagnosis & Positioning), and `dr_2J-03` / live requirements data.

---

## REQUIRED OUTPUT TABLES

### Table 1: Cross-Report Agreement Matrix

| Journal (evaluated across top three of any report) | `dr_2J-01` rank + basis | `dr_2J-02` verdict (framing risk, editor match) | `dr_2J-03` verdict (package effort, blocking gaps) | Agreement: UNANIMOUS / SPLIT / CONFLICTED | If split, which report's evidence is stronger and why |
|---|---|---|---|---|---|
| **Building Simulation** (Springer / Tsinghua) | **Rank 1**: Native BPS scope; 6,000 EnergyPlus runs match house style; 100% CRKN APC waiver (`dr_2J-01` Table 1, Table 4). | **Lowest framing risk**: BPS campaign and generative occupancy models are core topics; handling editor Prof. Bing Dong matches portfolio (`dr_2J-02` Table 2, Table 3). | **Low effort**: Accepts single-file or separate figures; 200-word abstract cap; standard Springer author-date references; no heavy reformatting needed. | **UNANIMOUS** | Reports agree unanimously that Building Simulation offers the best alignment between paper content and venue scope with lowest process friction. |
| **Applied Energy** (Elsevier) | **Rank 3** in `dr_2J-01` Table 6 / **Rank 2** in README: Native vocabulary for load shape, load factor, and diurnal peak shifting; 100% CRKN APC waiver (`dr_2J-01` Table 1, Table 4). | **High desk-reject risk**: Turning away papers that stop at load shape without modeling grid power flow, tariffs, or emissions (`dr_2J-02` Table 2). | **Moderate to high effort**: Requires 1 to 2 pages of added discussion on grid flexibility and ramping consequences; strict 3 to 5 highlights (max 85 characters each). | **SPLIT** | `dr_2J-02` evidence is stronger: `dr_2J-01` scores scope fit on topic keywords, but `dr_2J-02` documents that Applied Energy desk-rejects simulation studies that omit macro-energy or power system consequence. |
| **Sustainable Cities and Society** (Elsevier) | **Rank 2** in `dr_2J-01` Table 6 / **Rank 3** in README: Strong urban/stock scale fit; 144,507 Census frame fits scope; 100% CRKN APC waiver (`dr_2J-01` Table 1, Table 4). | **Moderate framing risk**: Requires urban housing stock framing; **identifies institutional conflict of interest** (Editor-in-Chief affiliated with Concordia University) requiring explicit routing (`dr_2J-02` Table 2, Table 3). | **Moderate effort**: Requires abstract reframing toward urban energy transition; standard Elsevier submission format. | **SPLIT** | `dr_2J-02` evidence is stronger: The institutional conflict of interest at Concordia University must be formally declared and routed around, making it a higher administrative burden than Building Simulation. |
| **Energy and Buildings** (Elsevier) | **Benchmark only**: Scored 5/5 on content match, but author-excluded due to 4 revision rounds on prior paper (`dr_2J-01` Table 1, Table 3). | **Benchmark only**: Closest historical scope match, but high revision burden confirmed (`dr_2J-02` Table 1). | **Benchmark only**: Standard Elsevier workflow. | **UNANIMOUS** | Retained strictly as the benchmark against which the decision is measured; author exclusion maintained. |
| **Journal of Building Performance Simulation** (Taylor & Francis) | **Excluded**: Methodological twin, but companion paper is currently under review there (`dr_2J-01` Table 1). | **High series risk**: Salami-slicing concern and reviewer pool overlap with companion paper (`dr_2J-02` Table 5). | **High risk**: Requires resolving status of under-review predecessor. | **UNANIMOUS** | Reports agree to avoid submitting to the exact venue where the predecessor manuscript is currently under review. |
| **Building and Environment** (Elsevier) | **Excluded**: Prior rejection in this research line; tight focus on indoor environmental quality / IEQ (`dr_2J-01` Table 1; `dr_2J-02` Table 1). | **High desk-reject risk**: Rejects macro load forecasting without physical IEQ or indoor environmental measurements (`dr_2J-02` Table 1). | **High risk**: Prior rejection history. | **UNANIMOUS** | Reports agree that B&E is a scope mismatch for a macro load-shape forecasting paper without measured IEQ data. |

---

### Table 2: THE DECISION

| Slot | Journal | The single strongest reason (cite report and table) | The strongest argument against it, stated fairly | What tips it |
|---|---|---|---|---|
| **Target** | **Building Simulation** (Springer Nature / Tsinghua University Press) | Native venue for a 6,000-run EnergyPlus campaign and generative occupancy validation ladder (`dr_2J-01` Table 1, Table 2; `dr_2J-02` Table 2). | Lower general citation reach than Applied Energy; the 2030 forecasting claim may be received as simulation setup rather than a standalone headline (`dr_2J-01` Table 3; `02_journal_options.md`). | Minimal pre-submission rework (~1 hour), lowest desk-reject risk, fully covered APC via CRKN Springer agreement, and matched handling editor (Prof. Bing Dong). |
| **Second choice, if rejected** | **Applied Energy** (Elsevier) | Native readership for load shape, load factor, and diurnal peak demand shifting (`dr_2J-01` Table 1; `02_journal_options.md`). | Genuine desk-reject risk because the paper stops at building load metrics and does not model grid power dispatch, tariffs, or emissions (`dr_2J-02` Table 2). | Retained as the ambitious backup; submitting here requires adding a 1 to 2 page discussion on grid flexibility and ramping implications before submission. |
| **Third choice** | **Sustainable Cities and Society** (Elsevier) | Strong fit for national housing stock and scenario-to-2030 longitudinal modeling across climate zones (`dr_2J-01` Table 1). | Requires reframing toward urban transition; Editor-in-Chief is affiliated with Concordia University, creating an institutional conflict of interest that requires mandatory routing (`dr_2J-02` Table 2, Table 3). | Serves as a viable stock-scale alternative if Building Simulation and Applied Energy are both unsuitable, provided the EiC conflict is declared upfront. |
| **Benchmark not pursued** | **Energy and Buildings** (Elsevier) | Closest historical scope match on record (`dr_2J-01` Table 1, Table 2). | Process fatigue: prior group submission required 4 rounds of revision (`00_README_journal_targeting.md`). | Author exclusion constraint: the submission strategy prioritizes avoiding another prolonged multi-round revision cycle. |

---

### Table 3: Abstract Pruning Log (Current: 239 words -> Target: 194 words, cap <= 200 words)

*Target journal limit:* 200 words (Building Simulation / Springer standard abstract guideline).

| # | Sentence (first 8 words) | Words | Claim it carries | Load-bearing for contribution? | Action | Words after |
|---|---|---|---|---|---|---|
| 1 | Stock-scale building energy models still run on static, | 19 | Static pre-COVID schedules fail to capture temporal shift (when vs how much). | YES | COMPRESS: cut filler phrasing, sharpen contrast. | 16 |
| 2 | This study forecasts the Canadian residential load shape | 24 | Forecasts 2005 to 2030 Canadian load shape through COVID/WFH break from calibrated occupancy. | YES | COMPRESS: streamline descriptor clauses. | 19 |
| 3 | Four General Social Survey time-use cycles (64,061 | 31 | Method pipeline: 4 GSS cycles (64,061 diaries), Transformer, 144,507 Census frame, True-Future-Test. | YES | COMPRESS: condense pipeline description without dropping sample sizes. | 24 |
| 4 | A campaign of 6,000 paired EnergyPlus runs | 46 | Simulation design: 6,000 paired EnergyPlus runs, frozen panels/archetypes/weather, SHEU-2019 calibration within +-2.7%. | YES | COMPRESS: tighten panel description while preserving the 48 cell-year +-2.7% calibration stat. | 36 |
| 5 | Weekday at-home occupancy breaks +5.2 pp at | 36 | Occupancy break (+5.2 pp at COVID, +2.2 to +3.9 pp in 2030) decouples from annual electricity (+1.4 to +2.6%). | YES | COMPRESS: streamline number presentation. | 28 |
| 6 | The load shape, however, changes structurally | 48 | Headline load shape: midday fill (+0.37 pp), load factor (+0.012), fixed evening peak (~17:30, shift 0 +- 1 h). | YES | COMPRESS: remove redundant clauses, keep exact statistical parameters. | 38 |
| 7 | Time-varying, survey-grounded schedules are therefore feasible at | 21 | Survey-grounded schedules are feasible at stock scale and reveal ramping metrics invisible to static profiles. | YES | COMPRESS: synthesize final punchline into one concise closing sentence. | 18 |

#### Rewritten Abstract (Unstructured Form - Exact Word Count: 194 words)

> Stock-scale building energy models rely on static, pre-COVID occupancy schedules, yet behavioural shifts altered when residential energy is used. This study forecasts the Canadian residential load shape from 2005 to 2030 using a calibrated behavioural occupancy time-series through the COVID/work-from-home structural break. Four General Social Survey cycles (64,061 diaries) are harmonized, augmented by a gate-selected hybrid conditional Transformer, linked to a 144,507-household Census frame, and forecast under a True-Future-Test protocol. A campaign of 6,000 paired EnergyPlus simulations (fixed 50-household panels, frozen archetypes and weather) isolates the pure occupancy effect, with activity-resolved end uses calibrated to SHEU-2019 microdata within +-2.7% in all 48 cell-years. Weekday at-home occupancy breaks +5.2 percentage points at COVID and persists to 2030 (+2.2 to +3.9 percentage points), while annual electricity increases by only +1.4 to +2.6% across the break and +0.6 to +1.2% to 2030. Structurally, the load shape exhibits midday fill and flattening (delta midday share +0.37 percentage points, delta load factor +0.012, both confidence intervals excluding zero) with the evening peak fixed at ~17:30 (building-level peak shift 0 +- 1 h). Survey-grounded time-varying schedules are feasible at stock scale and capture critical ramping metrics that static profiles miss.

*Word count validation:* 194 words (strictly below the 200-word cap).

#### Rewritten Abstract (Structured Variant - for Springer Editorial Manager fields)

- **Introduction/Background:** Stock-scale building energy models rely on static, pre-COVID occupancy schedules, yet behavioural shifts altered when residential energy is used. This study forecasts the Canadian residential load shape from 2005 to 2030 using a calibrated behavioural occupancy time-series through the COVID/work-from-home structural break.
- **Methods:** Four General Social Survey cycles (64,061 diaries) are harmonized, augmented by a gate-selected hybrid conditional Transformer, linked to a 144,507-household Census frame, and forecast under a True-Future-Test protocol. A campaign of 6,000 paired EnergyPlus simulations (fixed 50-household panels, frozen archetypes and weather) isolates the pure occupancy effect, with activity-resolved end uses calibrated to SHEU-2019 microdata within +-2.7% in all 48 cell-years.
- **Results:** Weekday at-home occupancy breaks +5.2 percentage points at COVID and persists to 2030 (+2.2 to +3.9 percentage points), while annual electricity increases by only +1.4 to +2.6% across the break and +0.6 to +1.2% to 2030. Structurally, the load shape exhibits midday fill and flattening (delta midday share +0.37 percentage points, delta load factor +0.012, both confidence intervals excluding zero) with the evening peak fixed at ~17:30 (building-level peak shift 0 +- 1 h).
- **Conclusions:** Survey-grounded time-varying schedules are feasible at stock scale and capture critical ramping metrics that static profiles miss.

---

### Table 4: Package Build Checklist

| # | File / Item | Source (existing file or to create) | Journal requirement satisfied (`dr_2J-03`) | Status | Action |
|---|---|---|---|---|---|
| 1 | Cover Letter | `writing/submission/` (Section C2 below) | Editorial requirement; handling editor routing (`dr_2J-02` Table 3) | **READY** | Copy and paste Section C2 into submission portal. |
| 2 | Manuscript Main Text | `2J_manuscript_submission.docx` / `.md` | Main text file with lines/double spacing | **READY** | Render clean DOCX/PDF with updated abstract and verified affiliations. |
| 3 | Title Page (Unblinded) | `2J_manuscript_submission.md` front matter | Author affiliations, corresponding email, ORCIDs | **NEEDS EDIT** | Fill department line and ORCIDs (`[confirm]`). |
| 4 | Abstract | Table 3 above | Word count <= 200 words | **READY** | Paste 194-word abstract into submission system. |
| 5 | Highlights | `2J_manuscript_submission.md` (lines 21-28) | 5 bullet points, each <= 85 characters | **READY** | Retain existing 5 bullets (all under 85 characters). |
| 6 | Keywords | `2J_manuscript_submission.md` (lines 15-18) | 5 to 8 keywords | **READY** | Retain 7 keywords: Occupancy Modelling; Building Performance Simulation; Time-Use Survey; Load Shape; Peak Demand; Longitudinal Forecasting; COVID-19 / Work-From-Home. |
| 7 | Main-Text Figures (7) | `figures/` directory | High resolution (>= 300 DPI), TIFF/PNG/EPS | **READY** | Verify resolution and ensure standalone files are indexed Fig 1 to Fig 7. |
| 8 | Main-Text Tables (5) | `tables/` directory | Editable table format in Word/LaTeX | **READY** | Retain editable DOCX tables (Tables 1 to 5). |
| 9 | Supplementary Material | `2J_manuscript_submission.md` appendices | Appendices A1-A3, B1-B2, C1-C2, Figs S1-S9 | **READY** | Compile into a single PDF document labelled Supplementary Information. |
| 10 | Graphical Abstract | `figures/` (3 candidate files exist) | 1 image file (aspect ratio ~2:1 or 16:9, PNG/TIFF) | **BLOCKED ON USER** | User must select one of the three candidate images. |
| 11 | Data Availability Statement | `2J_manuscript_submission.md` (lines 49-50) | StatCan PUMF & GSS catalog citations | **READY** | Included in manuscript text; cite public catalogue numbers. |
| 12 | CRediT Statement | `2J_manuscript_submission.md` (lines 53-54) | Formal contributor roles | **READY** | Retain CRediT statement for Iseri and Hachem-Vermette. |
| 13 | Declarations & Funding | `2J_manuscript_submission.md` (lines 43-52) | Funding, competing interests, acknowledgements | **READY** | Confirm NSERC and Voltage-Age Seed fund acknowledgements. |
| 14 | Suggested Reviewers List | `dr_2J-02` Table 4 | 3 to 5 non-conflict expert reviewers | **READY** | Use 5 reviewers from `dr_2J-02` Table 4. |

---

### Table 5: Blocked on the User

| # | Open item | Why it cannot be resolved from the reports | What the user must decide | Blocks upload? |
|---|---|---|---|---|
| 1 | Department / institute affiliation and ORCIDs | Marked `[confirm]` in front matter; institutional metadata is user-specific. | Provide exact department name (e.g., Department of Building, Civil and Environmental Engineering / Next-Generation Cities Institute) and both ORCID strings. | **YES** |
| 2 | Building and Environment rejection history | Project records do not state whether the prior rejection was this paper or an earlier pipeline manuscript. | Confirm whether this specific manuscript or an earlier paper received the B&E rejection (select Cover Letter Variant A or B). | **YES** (for letter choice) |
| 3 | Venue and status of companion paper | Predecessor manuscript is cited as *(under review)* at *Journal of Building Performance Simulation*. | Confirm that the companion paper is still currently under review at JBPS. | **NO** (can submit with under-review tag) |
| 4 | Graphical abstract selection | Three candidate image files exist in the repository; none is designated as primary. | Pick candidate 1, 2, or 3 from the `figures/` folder as the graphical abstract. | **YES** |
| 5 | Submission account credentials | Springer Editorial Manager portal requires active corresponding author login for *Building Simulation*. | Ensure corresponding author account (orcunkoral.oseri@concordia.ca) is active on the Springer Editorial Manager site. | **YES** |

---

## Part C: The Deliverables

### C1. The Decision, in One Paragraph

We recommend submitting this manuscript to **Building Simulation** (Springer Nature / Tsinghua University Press) as the primary target. The two strongest reasons are (1) perfect methodological alignment with a large-scale, gate-validated 6,000-run EnergyPlus campaign and generative Transformer occupancy model, which represents the core house style of the journal (`dr_2J-01` Table 1; `dr_2J-02` Table 2), and (2) the lowest desk-reject and revision friction among high-impact options, backed by a 100% open-access APC waiver under the Canadian CRKN Springer Nature agreement (`dr_2J-01` Table 4) and an ideal handling editor in Prof. Bing Dong (`dr_2J-02` Table 3). The single real cost of this choice is that the journal has a more specialized building-physics reach than broad-scale energy venues like *Applied Energy*, meaning the 2030 national load-shape forecast may be received as a rigorous simulation demonstration rather than as a headline power-grid policy finding.

---

### C2. The Cover Letter, Ready to Paste

*(Addressed to Prof. Bing Dong, Associate Editor for occupant behaviour modeling and building performance simulation at Building Simulation. Formatted with no em dashes and no en dashes.)*

#### Variant A: If the Building and Environment rejection applied to an earlier draft of this research line

```
Prof. Bing Dong
Associate Editor, Building Simulation
Springer Nature / Tsinghua University Press

[Date]

Dear Prof. Dong,

We are pleased to submit our original research manuscript entitled "From 'How Much' to 'When': Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)" for consideration as a Research Article in Building Simulation.

This study presents a national longitudinal building performance simulation campaign demonstrating how behavioural occupant time-series forecasting through a structural break reshapes residential diurnal load curves and peak demand across multi-climate building stocks. Across 6,000 paired EnergyPlus simulations, we show that while post-pandemic weekday at-home occupancy breaks +5.2 percentage points and persists to 2030 (+2.2 to +3.9 percentage points), annual electricity demand increases by only +1.4 to +2.6%, whereas the load shape exhibits structural midday filling (+0.37 percentage points) and load factor flattening (+0.012) while fixing the evening peak near 17:30.

We specifically target Building Simulation because our contribution is grounded in simulation methodology, gate-validated generative occupancy modeling, and multi-archetype EnergyPlus execution across six ASHRAE climate zones. Your journal is the premier venue for research that bridges rigorous occupant time-use modeling with physics-based building energy simulation tools. Our work occupies an unaddressed gap in the building simulation literature: transforming empirical, multi-cycle time-use microdata through a gate-selected conditional Transformer into calibrated, activity-resolved EnergyPlus schedules capable of forecasting stock load shapes through historical structural disruptions.

Relationship to Prior and Concurrent Work:
This paper is the second study in a structured research pipeline. The predecessor paper (currently under review at the Journal of Building Performance Simulation) established "how much" survey-grounded occupancy shifts annual building energy demand relative to static default schedules within a single climate zone. The present manuscript addresses "when": it implements a paired cycle-versus-cycle simulation design, forecasts behavioural trajectories through the COVID/work-from-home structural break to 2030 under a True-Future-Test protocol, broadens the spatial scope to four code archetypes across six climate zones, and calibrates activity-resolved end uses to national survey microdata (SHEU-2019) within +-2.7% in all 48 cell-years. The two manuscripts answer distinct scientific questions using different modeling architectures, simulation designs, and output metrics. An earlier exploratory framing in this research line was previously reviewed at an indoor-environment journal; the present manuscript has been completely refocused on stock-scale building performance simulation rigor, generative model validation, and diurnal load shape dynamics.

Declarations:
This manuscript represents original work that has not been published previously and is not under consideration for publication elsewhere. Its submission has been approved by all authors and by the responsible authorities at Concordia University. The authors declare no competing financial or personal interests.

Suggested Reviewers:
1. Prof. Stefano Schiavon, University of California, Berkeley (schiavon@berkeley.edu) - Expert in occupant behaviour schedules and building energy simulation.
2. Prof. Tianzhen Hong, Lawrence Berkeley National Laboratory (thong@lbl.gov) - Global leader in occupant modeling and stock simulation campaigns.
3. Dr. Cristina Piselli, University of Perugia (cristina.piselli@unipg.it) - Specialist in stochastic occupancy models and load shape forecasting.
4. Prof. Dirk Saelens, KU Leuven / EnergyVille (dirk.saelens@kuleuven.be) - Expert in time-use survey integration and residential demand profiling.
5. Prof. Joana Ortiz, IREC (jortiz@irec.cat) - Specialist in residential occupant behaviour and work-from-home load shifts.

Thank you for your time and consideration of our manuscript.

Sincerely,

Orcun Koral Iseri, Ph.D. (Corresponding Author)
Caroline Hachem-Vermette, Ph.D.
Concordia University
Montreal, Quebec, Canada
Email: orcunkoral.oseri@concordia.ca
```

---

#### Variant B: Standard clean submission (if no prior rejection disclosure is required)

```
Prof. Bing Dong
Associate Editor, Building Simulation
Springer Nature / Tsinghua University Press

[Date]

Dear Prof. Dong,

We are pleased to submit our original research manuscript entitled "From 'How Much' to 'When': Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)" for consideration as a Research Article in Building Simulation.

This study presents a national longitudinal building performance simulation campaign demonstrating how behavioural occupant time-series forecasting through a structural break reshapes residential diurnal load curves and peak demand across multi-climate building stocks. Across 6,000 paired EnergyPlus simulations, we show that while post-pandemic weekday at-home occupancy breaks +5.2 percentage points and persists to 2030 (+2.2 to +3.9 percentage points), annual electricity demand increases by only +1.4 to +2.6%, whereas the load shape exhibits structural midday filling (+0.37 percentage points) and load factor flattening (+0.012) while fixing the evening peak near 17:30.

We specifically target Building Simulation because our contribution is grounded in simulation methodology, gate-validated generative occupancy modeling, and multi-archetype EnergyPlus execution across six ASHRAE climate zones. Your journal is the premier venue for research that bridges rigorous occupant time-use modeling with physics-based building energy simulation tools. Our work occupies an unaddressed gap in the building simulation literature: transforming empirical, multi-cycle time-use microdata through a gate-selected conditional Transformer into calibrated, activity-resolved EnergyPlus schedules capable of forecasting stock load shapes through historical structural disruptions.

Relationship to Companion Work:
This paper is the second study in a structured research pipeline. The predecessor paper (currently under review at the Journal of Building Performance Simulation) established "how much" survey-grounded occupancy shifts annual building energy demand relative to static default schedules within a single climate zone. The present manuscript addresses "when": it implements a paired cycle-versus-cycle simulation design, forecasts behavioural trajectories through the COVID/work-from-home structural break to 2030 under a True-Future-Test protocol, broadens the spatial scope to four code archetypes across six climate zones, and calibrates activity-resolved end uses to national survey microdata (SHEU-2019) within +-2.7% in all 48 cell-years. The two manuscripts answer distinct scientific questions using different modeling architectures, simulation designs, and output metrics.

Declarations:
This manuscript represents original work that has not been published previously and is not under consideration for publication elsewhere. Its submission has been approved by all authors and by the responsible authorities at Concordia University. The authors declare no competing financial or personal interests.

Suggested Reviewers:
1. Prof. Stefano Schiavon, University of California, Berkeley (schiavon@berkeley.edu) - Expert in occupant behaviour schedules and building energy simulation.
2. Prof. Tianzhen Hong, Lawrence Berkeley National Laboratory (thong@lbl.gov) - Global leader in occupant modeling and stock simulation campaigns.
3. Dr. Cristina Piselli, University of Perugia (cristina.piselli@unipg.it) - Specialist in stochastic occupancy models and load shape forecasting.
4. Prof. Dirk Saelens, KU Leuven / EnergyVille (dirk.saelens@kuleuven.be) - Expert in time-use survey integration and residential demand profiling.
5. Prof. Joana Ortiz, IREC (jortiz@irec.cat) - Specialist in residential occupant behaviour and work-from-home load shifts.

Thank you for your time and consideration of our manuscript.

Sincerely,

Orcun Koral Iseri, Ph.D. (Corresponding Author)
Caroline Hachem-Vermette, Ph.D.
Concordia University
Montreal, Quebec, Canada
Email: orcunkoral.oseri@concordia.ca
```

---

### C3. The Submission-Day Sequence

Follow this step-by-step sequence on the day of upload:

1. **Front-Matter Resolution (Table 5 Item 1):**
   - Confirm department/institute line and insert both ORCID strings into the title page of `2J_manuscript_submission.docx`.
2. **Graphical Abstract Selection (Table 5 Item 4):**
   - Select one image file from `figures/` (Candidate 1, 2, or 3) and save as `Graphical_Abstract.png`.
3. **Manuscript File Generation (Table 4 Items 2 & 9):**
   - Verify that `2J_manuscript_submission.docx` contains the pruned 194-word abstract from Table 3.
   - Generate `Supplementary_Information.pdf` containing Appendices A1 to C2 and Figures S1 to S9.
4. **Log in to Springer Editorial Manager:**
   - Navigate to the *Building Simulation* Editorial Manager portal (`https://www.editorialmanager.com/buis/` or Springer Nature equivalent).
   - Log in using corresponding author credentials (orcunkoral.oseri@concordia.ca).
5. **Select Article Type:**
   - Choose **Original Research Paper** (or **Research Article**).
6. **Upload Package Files (in exact upload order):**
   - Item 1: Cover Letter (upload DOCX or paste text from Section C2).
   - Item 2: Title Page (with author affiliations, corresponding author details, and ORCIDs).
   - Item 3: Main Manuscript Text (DOCX or PDF with line numbering enabled).
   - Item 4: Figures (7 high-resolution image files, Fig 1 to Fig 7).
   - Item 5: Tables (5 editable tables).
   - Item 6: Supplementary Material (`Supplementary_Information.pdf`).
   - Item 7: Graphical Abstract (`Graphical_Abstract.png`).
7. **Enter Metadata in Submission Portal:**
   - Paste Title: *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*.
   - Paste Abstract: 194-word text from Table 3 (or structured version into respective fields).
   - Paste 7 Keywords: Occupancy Modelling; Building Performance Simulation; Time-Use Survey; Load Shape; Peak Demand; Longitudinal Forecasting; COVID-19 / Work-From-Home.
   - Paste 5 Highlights from Table 4 Item 5.
8. **Handling Editor & Reviewer Routing (Table 4 Item 14):**
   - Request Associate Editor **Prof. Bing Dong** in the editor selection dropdown or cover letter field.
   - Enter the 5 suggested reviewers from Section C2.
9. **Declarations & Open Access Agreement:**
   - Check boxes for originality, all-author approval, and no competing interests.
   - For Open Access / CRKN institutional waiver, select **Concordia University** to activate the 100% APC waiver agreement.
10. **Build PDF & Final Review:**
    - Generate the merged submission PDF, inspect layout and figures for rendering errors, and click **Submit**.

---

### C4. What to Do If It Is Rejected

If *Building Simulation* rejects the manuscript, execute the following three concrete changes before submitting to the second-choice journal (**Applied Energy**), ranked by how much they address the primary rejection vulnerability identified in `dr_2J-02` Table 6:

1. **Add a 1 to 2 Page Discussion Subsection on Grid Flexibility, Ramping, and Tariff Implications:**
   - *Rationale:* Applied Energy desk-rejects papers that stop at building-level load shape without demonstrating power-system or grid consequences (`dr_2J-02` Table 2).
   - *Action:* Using the numbers already computed (+0.012 load factor flattening, +0.37 pp midday fill, evening peak locked at 17:30), explicitly discuss what this means for distribution feeder ramping duty, duck-curve mitigation, and residential demand-response program windows.
2. **Reframe Abstract and Introduction Around Energy System Demand-Side Flexibility:**
   - *Rationale:* Applied Energy readers are energy engineers and system modelers rather than BPS specialists (`02_journal_options.md`).
   - *Action:* Shift emphasis from "EnergyPlus campaign setup and generative Transformer validation" to "quantifying post-structural-break demand flexibility and peak load shifts for power systems".
3. **Condense Simulation Engine Details into Supplementary Information:**
   - *Rationale:* Applied Energy prioritizes energy-system insights over detailed EnergyPlus input files and archetype physics.
   - *Action:* Move detailed EnergyPlus HVAC parameters and archetype geometry tables into the supplementary material, keeping main text focused on load profiles, load factors, and grid-relevant metrics.

---

## Confidence and Caveats

- **The One Part of the Decision Most Likely to Be Wrong:**
  The assumption that *Building Simulation* reviewers will view a national longitudinal forecasting claim to 2030 as a natural extension of a BPS campaign, rather than criticizing it as an econometric or statistical projection that extends beyond physical simulation boundaries.
- **The One Piece of Information That Would Change It:**
  If the companion paper at the *Journal of Building Performance Simulation* is accepted immediately with high praise for its occupancy-generation method, it would significantly reduce the risk of submitting this second paper to *Applied Energy* or *Sustainable Cities and Society*, because the core methodology would already be published and citable as an established standard.

---
*Report synthesis complete. Inputs cited: `dr_2J-01` (Fit & Review Burden), `dr_2J-02` (Rejection Diagnosis & Positioning), `dr_2J-03` (Requirements), `00_README_journal_targeting.md`, and `01_originality_statement.md`.*
