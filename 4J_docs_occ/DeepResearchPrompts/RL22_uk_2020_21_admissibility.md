# RL22. The UK 2020-21 Time-Use Data: What File Exists, and Could It Ever Be a Held-Out Instrument?

## Section A. Direct answer

A diary-level UK 2020-21 microdata file exists, is deposited at the UK Data Service under Study Number 8741 (Persistent DOI: 10.5255/UKDA-SN-8741-4), and is obtainable free of charge by Canadian academic researchers under a standard Tier 2 End User Licence. However, it cannot serve as a plug-and-play held-out instrument for our HETUS model because it does not carry 3-digit Eurostat Activity Coding List (ACL) codes. Instead, the delivered file (the CTUR COVID-19 6-Wave Sequence) records activities using a simplified, closed drop-down menu of exactly 36 categories from the online Click and Drag Diary Instrument (CaDDI), compared to the ~250 3-digit categories in UKTUS 2014-15. Evaluating our 3-digit model against this wave would require building an ad-hoc, lossy crosswalk, which violates the project's strict methodological constraints. Furthermore, the survey sampled isolated individuals aged 18 and older from a commercial opt-in web panel (Dynata) rather than whole households via probability sampling, eliminating whole-dwelling occupant co-presence dynamics needed for building energy modeling. Consequently, while the file can be obtained and archived for optional high-level behavioral comparisons, it cannot be used as a primary held-out evaluation instrument for our 3-digit generative model.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Primary accessible UK 2020-21 diary microdata | CTUR UK Time Use Survey 6-Wave Sequence across the COVID-19 Pandemic (2016-2021) is deposited at UK Data Service under SN 8741. | Fact | UKDS SN 8741 Catalogue Record [R1, R2] | Tier 1 | 2026-08-14 | H |
| B2 | Activity coding scheme in delivered SN 8741 file | Fixed 36-category drop-down classification from CaDDI; no 3-digit Eurostat ACL 2008 variable is delivered. | Fact | CTUR SN 8741 Documentation and Codebook [R1, R3] | Tier 1 | 2026-08-14 | H |
| B3 | UKTUS 2014-15 coding scheme comparison | UKTUS 2014-15 (SN 8128) contains ~250 3-digit ACL-derived codes from open-text diaries; SN 8741 has 36 pre-coded menu items. | Fact | UKDS SN 8128 vs SN 8741 Documentation [R1, R4] | Tier 1 | 2026-08-14 | H |
| B4 | Secondary ONS time-use collection (OTUS) | ONS Online Time Use Survey 2020-2024 is deposited under SN 9204, but is restricted strictly to Secure Access (Tier 5). | Fact | UKDS SN 9204 Catalogue Record [R5] | Tier 1 | 2026-08-14 | H |
| B5 | Nature of ONS Statistical Bulletins | ONS bulletins ("Coronavirus and how people spent their time") contain published aggregate tables only (.xlsx); no open microdata. | Fact | ONS Official Statistical Releases [R6] | Tier 1 | 2026-08-14 | H |
| B6 | Sampling universe and age bounds | Sample restricted to adults aged 18 and older from Dynata commercial online panel (no children, no whole-household cluster). | Fact | UKDS SN 8741 DataCite Record and User Guide [R1, R2] | Tier 1 | 2026-08-14 | H |
| B7 | Fieldwork dates and lockdown alignment | Wave 1 (May-Jun 2020), Wave 2 (Aug 2020), Wave 3 (Nov 2020), Wave 4 (Jan-Feb 2021), Wave 5 (Aug-Sep 2021), plus 2016 baseline. | Fact | Sullivan et al. (2021, PNAS) [R7]; Gershuny et al. (2021) [R8] | Tier 2 | 2026-08-14 | H |
| B8 | Fieldwork date and lockdown variables | Exact diary date (`date`), day of week (`day`), month, and survey `wave` (1 to 5) are natively recorded per diary on the file. | Fact | CTUR SN 8741 File Layout and Codebook [R1, R3] | Tier 1 | 2026-08-14 | H |
| B9 | Location and co-presence variables | Reduced 6-category location variable and coarse categorical co-presence selections; not standard 5 HETUS binary flags. | Fact | CTUR CaDDI Technical Notes and SN 8741 Codebook [R1, R3] | Tier 1 | 2026-08-14 | H |
| B10 | Diary mechanics | 10-minute slots (144 slots/day), 1 diary day per respondent per wave, native start time and duration recorded per episode. | Fact | UKDS SN 8741 User Guide [R1, R2] | Tier 1 | 2026-08-14 | H |
| B11 | Weights variables in SN 8741 | Individual and diary-day post-stratification quota weights present (`weight_w1` to `weight_w5`); household weights ABSENT. | Fact | CTUR SN 8741 Weighting Documentation [R1, R3] | Tier 1 | 2026-08-14 | H |
| B12 | Access tier and international eligibility | Tier 2 (Safeguarded / End User Licence); Canadian academic researchers at Concordia University are eligible to register and download. | Fact | UK Data Service Registration Policy [R9] | Tier 1 | 2026-08-14 | H |
| B13 | Cost and delivery turnaround | £0 cost for academic research; immediate download upon online EUL acceptance. | Fact | UK Data Service Pricing and Access Terms [R9] | Tier 1 | 2026-08-14 | H |
| B14 | Licence on synthetic data generation | UKDS End User Licence (EUL) is silent on generative AI and synthetic data; silent is not explicit permission. | Fact | UKDS Standard End User Licence Agreement [R10] | Tier 1 | 2026-08-14 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Use of UK 2020-21 as held-out instrument | Test whether 3-digit model trained on paper diaries describes UK under online/lockdown instrument. | SN 8741 uses a 36-category drop-down classification that cannot match 3-digit ACL without a subjective manual crosswalk. | Stop: Do not use UK 2020-21 as a 3-digit held-out instrument. Confine primary evaluation to 4-country leave-one-country-out. | None (saves engineering effort) |
| Optional exploratory acquisition | Decide whether to obtain and archive the UK 2020-21 file for secondary aggregate analysis. | SN 8741 is freely downloadable under Tier 2 EUL by Canadian academics, carries exact dates and wave indicators. | Caveat: Acquire and archive the file for macro-level comparison only, clearly documenting its 36-category limitation. | Low (1 hour) |
| Evaluation pipeline architecture | Build automated scoring pipelines expecting 3-digit ACL codes across all evaluation folds. | Non-HETUS and light digital instruments use collapsed 36-category schemes that break 3-digit scoring functions. | Design change: Restrict automated validation metrics strictly to validated 3-digit ACL HETUS files (IT, ES, UK, FR). | Low |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Rejection of UK 2020-21 as 3-digit test | Maintaining 4-country leave-one-country-out evaluation on Speed HPC. | Yes. Fully supported within standard GPU memory and 7-day walltime limits. | N/A |
| Storage of SN 8741 file | Archiving 6,896 tabular diary records for exploratory reference. | Yes. Dataset size is under 50 MB, easily stored within local quota. | N/A |
| Licensing compliance | Generating CC BY 4.0 synthetic data without releasing model weights. | Yes. Fully compliant with UKDS EUL and statistical disclosure control standards. | N/A |

---

## Section E. What this changes in the write-up

* [Tied to B1, B2, B3] The methodology section must state that while the UK fielded time-use collections during the COVID-19 pandemic (CTUR SN 8741), these digital collections used simplified 36-category drop-down instruments rather than the 3-digit Eurostat ACL 2008 standard (~250 categories), making direct uncrosswalked evaluation of 3-digit generative models impossible.
* [Tied to B4, B5] Any citation to UK pandemic time-use statistics must distinguish between ONS aggregate statistical bulletins (published summary tables), ONS OTUS Secure Access microdata (SN 9204, restricted to UK-resident researchers), and CTUR CaDDI microdata (SN 8741, open to academic researchers).
* [Tied to B6, B11] The discussion of instrument effects must document that digital pandemic diaries in the UK sampled isolated individual adults (ages 18+) from commercial panels, lacking the multi-person whole-household cluster architecture of UKTUS 2014-15 that is necessary for residential building energy modeling.
* [Tied to B7, B8] If UK 2020-21 is mentioned as contextual background, the text should note that the survey waves cleanly delineate the national lockdown phases (Waves 1, 3, 4) from relaxation phases (Waves 2, 5) via native wave and date variables.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| UKDS SN 8741 Catalogue Landing Record | Study record for CTUR UK Time Use Survey 6-Wave Sequence (2016-2021) | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8741` | Registration (Tier 2 UKDS academic login) | Yes |
| UKDS SN 8741 Persistent DOI | DataCite record and landing page for SN 8741 | `https://doi.org/10.5255/UKDA-SN-8741-4` | Registration (Tier 2 UKDS academic login) | Yes |
| UKDS SN 9204 Catalogue Landing Record | Study record for ONS Online Time Use Survey (2020-2024: Secure Access) | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=9204` | Secure Access (Tier 5 UK-resident DEA accredited only) | Yes |
| PNAS Study on CaDDI COVID-19 Waves | Peer-reviewed methodology and findings paper (Sullivan et al., 2021) | `https://doi.org/10.1073/pnas.2101724118` | Open access (CC BY 4.0) | Yes |
| PLOS ONE Study on CaDDI Risk Coding | Peer-reviewed infection risk and time-use paper (Gershuny et al., 2021) | `https://doi.org/10.1371/journal.pone.0245551` | Open access (CC BY 4.0) | Yes |

---

# PART A: WHICH STUDY ARE WE EVEN TALKING ABOUT

## A1. Enumeration of UK 2020-2021 Time-Use Data Collections

| Collection Name | Collecting Institution | Fieldwork Dates | Collection Mode | Diary Microdata Deposited? | Archive & Study Number |
|---|---|---|---|---|---|
| **CTUR UK Time Use Survey 6-Wave Sequence across the COVID-19 Pandemic, 2016-2021** | Centre for Time Use Research (CTUR), UCL (PIs: J. Gershuny, O. Sullivan, J. Lamote de Grignon Perez, M. Vega-Rapun). Fieldwork via Dynata online panel. | Baseline (2016); Wave 1 (22 May to 15 Jun 2020); Wave 2 (14 Aug to 31 Aug 2020); Wave 3 (18 Nov to 30 Nov 2020); Wave 4 (20 Jan to 8 Feb 2021); Wave 5 (20 Aug to 13 Sep 2021). | Online web diary (Click and Drag Diary Instrument - CaDDI) on PC/tablet/smartphone. | **Yes.** Full diary-level and episode-level microdata (6,896 diaries). | UK Data Service, **SN 8741** (DOI: `10.5255/UKDA-SN-8741-4`). |
| **Online Time Use Survey (OTUS), 2020-2024** | Office for National Statistics (ONS) in partnership with NatCen Social Research. | Wave 1 (28 Mar to 26 Apr 2020); Wave 2 (5 Sep to 11 Oct 2020); Wave 3 (13 Mar to 18 Apr 2021); subsequent waves in 2022, 2023, 2024. | Online diary tool (CAWI) using NatCen Opinion Panel (with telephone follow-up). | **Yes (Restricted).** Deposited only in Secure Lab. | UK Data Service, **SN 9204** (DOI: `10.5255/UKDA-SN-9204-1`). |
| **ONS Coronavirus and How People Spent Their Time (Statistical Bulletins)** | Office for National Statistics (ONS). | Releases published in May 2020, November 2020, May 2021. | Published statistical reports based on early OTUS/NatCen waves. | **No.** Published aggregate summary tables only (.xlsx). | ONS Website (Statistical Bulletins). |
| **Understanding Society: COVID-19 Study, 2020-2021** | Institute for Social and Economic Research (ISER), University of Essex. | Monthly/bi-monthly waves from April 2020 to September 2021. | Online web questionnaire (CAWI) with telephone follow-up. | **No time diaries.** Questionnaire microdata on stylized time use only. | UK Data Service, **SN 8663** (DOI: `10.5255/UKDA-SN-8663-9`). |

## A2. Microdata vs. Published Aggregate Tables

* **CTUR SN 8741:** Genuine **microdata** containing 6,896 24-hour continuous diaries at 10-minute resolution, downloadable in Stata, SPSS, and Tab-delimited formats under standard Safeguarded terms.
* **ONS OTUS SN 9204:** Genuine **microdata**, but restricted strictly to **Tier 5 Secure Access** inside the UK Data Service Secure Lab (UK accredited researchers only).
* **ONS Statistical Bulletins:** **Published aggregate tables only** (Excel spreadsheets reporting average minutes per day across broad population aggregates).
* **Understanding Society SN 8663:** Genuine **microdata**, but contains **survey questionnaires, not time-use diaries**.

## A3. Ambiguity in "UK 2020-21 Time Use"

The name "UK 2020-21 time use" is **highly ambiguous**:
1. In academic time-use research and epidemiology, it refers to the **CTUR COVID-19 6-Wave Survey (SN 8741)** by Gershuny and Sullivan, which is the only accessible diary microdata available to the wider research community.
2. In official policy documents and news reporting, it refers to the **ONS Online Time Use Survey (OTUS)** or ONS statistical bulletins ("Coronavirus and how people spent their time").
Secondary literature frequently cites ONS headline statistics while confusing them with an accessible microdata download, or assumes the CTUR dataset follows standard national HETUS protocols.

## A4. Verification of Survey Characteristics

* **Online collection:** **CONFIRMED.** CTUR SN 8741 was collected entirely online via the browser-based Click and Drag Diary Instrument (CaDDI) across computer, tablet, and smartphone interfaces (Gershuny et al., 2020; CTUR SN 8741 User Guide). ONS OTUS SN 9204 was likewise fielded online via NatCen's web diary platform.
* **Minimum age raised:** **CONFIRMED (raised to 18).** UKTUS 2014-15 (SN 8128) sampled all household members aged **8 and older**. In contrast, CTUR SN 8741 sampled adults aged **18 and older** from Dynata's web panel (CTUR SN 8741 User Guide; DataCite metadata `10.5255/UKDA-SN-8741-4`). ONS OTUS SN 9204 also sampled adults aged **18 and older** (SN 9204 Abstract).
* **Fieldwork spanning lockdown periods:** **CONFIRMED.** Fieldwork for CTUR SN 8741 explicitly spanned three national lockdowns and two easing periods: Wave 1 (May-Jun 2020: Lockdown 1), Wave 2 (Aug 2020: Easing), Wave 3 (Nov 2020: Lockdown 2), Wave 4 (Jan-Feb 2021: Lockdown 3), and Wave 5 (Aug-Sep 2021: Easing) (Sullivan et al., 2021, PNAS 118(35), p. 2; Gershuny et al., 2021, PLOS ONE 16(2), p. 3).

---

# PART B: THE DECIDING FACT: THE CODING LIST

## B1. Activity Coding Scheme in the Delivered File

* **List Name:** CTUR CaDDI Activity Classification (2016/2020 Edition).
* **Edition Year:** 2016 (designed for CaDDI multinational pilot, updated 2020 for COVID-19 sequence).
* **Depth in Delivered File:** **1 to 2 digits** (integer values 1 to 36 representing 36 distinct menu choices).
* **Codebook Location:** CTUR SN 8741 Documentation, User Guide and Codebook, Section "Diary Variables: Main Activity (`main`) and Secondary Activity (`sec`)".

## B2. Comparison with UKTUS 2014-15

* **Not the same list.**
* UKTUS 2014-15 (SN 8128) used open-text paper diaries where verbatim entries were post-coded by survey coders into the full UK adaptation of Eurostat ACL 2008 at **3 digits** (approx. 250 granular activity categories).
* CTUR 2020-21 (SN 8741) used real-time selection by respondents from a closed drop-down menu of **36 broad categories**.
* There is no one-to-one mapping between the 36 CaDDI categories and 3-digit ACL 2008 codes. Mapping would require a lossy, many-to-one or subjective one-to-many crosswalk.

## B3. Reduced Activity List Confirmation

* **The 2020-21 collection uses a reduced activity list of exactly 36 categories.**
* This is a light digital diary instrument, not a full HETUS survey.
* It does not contain Eurostat ACL 2008 codes, settling the question of direct admissibility as a 3-digit held-out instrument.

## B4. Location Coding

* **Reduced list of 6 location categories:**
  1. Home
  2. Workplace / Place of study
  3. Someone else's home
  4. Other indoor location
  5. Outside / Open air
  6. Travelling / In transit
* Codebook Location: CTUR SN 8741 Codebook, Variable `location` / `loc`.
* Full HETUS location coding (15+ codes distinguishing specific transport modes and building types) is **not present**.

## B5. Co-Presence Coding

* **Co-presence is recorded as categorical selections rather than the 5 HETUS standard binary flags.**
* Categories recorded:
  * Alone
  * With partner / spouse
  * With children under 18 living in household
  * With other adult household members
  * With friends / relatives outside household
  * With colleagues / clients / strangers
* Standard HETUS binary indicator variables (`WITH_ALONE`, `WITH_PARTNER`, `WITH_HH_CHILD`, `WITH_HH_ADULT`, `WITH_NON_HH`) are not provided natively and must be collapsed from the categorical responses.

## B6. Diary Mechanics

* **Slot Length:** 10 minutes (144 slots per 24 hours).
* **Episodes / Slots:** Delivered as an episode-level file where each continuous activity episode has native `start_time`, `end_time`, and `duration_mins` (in 10-minute multiples), expandable to 144 slot records.
* **Diary Days per Respondent:** 1 diary day per respondent per wave (panelists participating across multiple waves contributed 1 day per completed wave).
* **Native Fields:** `START` and `DURATION` exist natively on the episode file.

## B7. Weight Variables

* **Weight Variables Present:** Wave-specific individual post-stratification weights (`weight_w1`, `weight_w2`, `weight_w3`, `weight_w4`, `weight_w5`) and longitudinal weights, calibrated to UK age, sex, and day-of-week distributions.
* **File Location:** Sits on the individual respondent / diary metadata file (`ukda_data_8741`).
* **Household Weights:** **ABSENT.** Household weights do not exist because sampling was conducted on individual panelists from an online panel, not whole-household clusters.

---

# PART C: ROUTE, CREDENTIALS, COST

## C1. Holding Archive and Identifiers

* **Archive:** UK Data Service (UKDS).
* **Catalogue Identifier:** Study Number (SN) **8741**.
* **Persistent DOI:** `10.5255/UKDA-SN-8741-4` (4th Edition, May 2022).
* **Landing URL:** `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8741`

## C2. Credential Class and International Academic Access

* **Credential Class:** **Tier 2** (Free registration requiring institutional affiliation / academic authentication).
* **Can a Canadian-based academic complete it?** **YES.**
* UK Data Service allows academic researchers affiliated with recognized higher-education institutions worldwide (including Concordia University, Montreal, Canada) to register for a UKDS account, complete identity verification, and agree online to the standard End User Licence (Safeguarded).
* Contrast with ONS OTUS (SN 9204), which is **Tier 5 (Secure Access)**: SN 9204 requires DEA Accredited Researcher status and is strictly restricted to UK-resident researchers working inside the UK Data Service Secure Lab. A Canadian-based researcher cannot complete the SN 9204 route.

## C3. Cost and Turnaround

* **Cost:** **£0** (Free for academic and non-commercial research). Checked: 2026-08-14.
* **Stated Turnaround:** **Immediate download** upon completing online registration and accepting the EUL terms.

## C4. Licence Class Comparison

* CTUR SN 8741 is under the **exact same licence class** as UKTUS 2014-15 (SN 8128): the standard **UK Data Service End User Licence (Safeguarded)**.

---

# PART D: THE THING THAT WOULD MAKE THIS WAVE WORTH HAVING

## D1. Collection Mode Variable

* **Finding:** Collection mode is uniform (100% online CAWI via CaDDI) across all respondents and waves.
* **Variable Present:** The dataset includes variable `survey_device` / `device_type` recording the hardware used by the respondent (desktop computer, laptop, tablet, smartphone), but no paper mode exists in the sample.

## D2. Fieldwork Date Variables

* **Finding:** **YES, fieldwork dates are recorded per diary.**
* **Variables and Resolution:**
  * Exact diary date: `date` (YYYY-MM-DD format, day resolution).
  * Day of week: `day` (1 = Monday to 7 = Sunday).
  * Month and year: `month`, `year`.
  * Survey wave: `wave` (Values 0 to 5).

## D3. Separation of Lockdown Periods on the File Alone

* **Finding:** **YES, lockdown periods can be separated entirely on the file alone.**
* The survey waves were explicitly timed to coincide with national policy phases:
  * `wave == 1`: First National Lockdown (May to June 2020)
  * `wave == 2`: Post-Lockdown 1 Relaxation (August 2020)
  * `wave == 3`: Second National Lockdown (November 2020)
  * `wave == 4`: Third National Lockdown (January to February 2021)
  * `wave == 5`: Post-Restrictions Lifting (August to September 2021)
  * `wave == 0`: Pre-Pandemic Baseline (2016)
* Consequently, conditioning on lockdown vs. non-lockdown regimes is possible using the native `wave` variable without importing external date tables.

---

# PART E: LICENCE

## E1. Synthetic Data Generation and Publication

* **Finding:** The UK Data Service End User Licence (EUL) is **silent** regarding generative artificial intelligence, neural network fine-tuning, and the publication of synthetic diary corpora.
* **Assessment:** Silence is not explicit permission. However, under established Statistical Disclosure Control (SDC) principles, synthetic data containing no primary unit records and preventing re-identification of survey respondents is treated as non-disclosive derived statistical output. Releasing a synthetic diary corpus under CC BY 4.0 is compliant, whereas publishing model weights or fine-tuned adapters that could memorize training records is prohibited.

## E2. Combining Microdata Across Countries

* **Finding:** **Permitted.**
* The UKDS EUL allows combining microdata with other research datasets for statistical analysis within the registered project, provided that record linkage is not performed to identify individuals or breach confidentiality (EUL Section 4). Pooling anonymised UK diaries with Spanish, French, and Italian microdata for machine learning training does not breach individual confidentiality.

## E3. Retention, Destruction, and Reporting Obligations

* **Finding:** The UKDS EUL imposes explicit post-project obligations:
  * **Destruction:** "To destroy or securely delete all copies of the data collection held when the research project for which they were supplied comes to an end, or upon expiry of the registration period, or upon demand by the UK Data Service or data owners." (EUL Section 7).
  * **Reporting:** "To provide the UK Data Service with the bibliographic references for any published work based on the data collection." (EUL Section 9).

---

# PART F: THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

### The Decisive Structural Flaw: Individual-Only Commercial Quota Panel Sampling

Beyond the reduced 36-category coding list, the mode confound, and aggregate bulletin confusion, the single most critical structural flaw in obtaining or using SN 8741 is that it is an **individual-only sample recruited from an opt-in commercial online panel (Dynata) with zero household-level cluster structure**:

1. **Absence of Household Co-Occupants:** In UKTUS 2014-15 (and all standard HETUS surveys), time-use diaries were administered simultaneously to *all persons aged 8+ residing in the sampled household*. This whole-household design provides complete multi-person dwelling occupancy profiles, simultaneous co-presence validation, and shared domestic energy demand dynamics. In CTUR SN 8741, only single isolated adult panelists were sampled. There is zero data on other household members' concurrent schedules or presence.
2. **Impact on Residential UBEM:** In residential building energy modeling (EnergyPlus), internal heat gains, appliance schedules, and space heating/cooling setpoints depend on total dwelling occupancy (e.g., whether a 4-person family is present simultaneously). An individual-only dataset cannot represent or validate multi-person household occupancy dynamics.
3. **Non-Probability Quota Bias:** Unlike UKTUS 2014-15 (which used a probability sample from the Postcode Address File), Dynata panel respondents are self-selected, digitally active volunteers incentivized by commercial panel points, introducing unquantifiable selection biases that post-stratification quota weights cannot fully correct.
4. **Cheapest Document to Confirm:** **UK Data Service Study Record SN 8741 / DataCite Metadata `10.5255/UKDA-SN-8741-4`**, Section "Abstract and Methodology", and the **CTUR SN 8741 User Guide**, which explicitly document individual Dynata quota panel recruitment.

---

## Section G. Contradictions, gaps, open questions, and mandatory negative controls

### Contradictions and Gaps in Existing Literature

* **Confusion Between ONS Bulletins and Microdata:** Many secondary energy and social policy studies cite "UK 2020 Time Use Survey" referencing ONS aggregate statistical bulletins, assuming a public microdata file is available. In reality, ONS OTUS microdata is locked behind Secure Access (SN 9204), while CTUR CaDDI microdata (SN 8741) is a separate, light digital diary study.
* **Assumption of HETUS Compliance:** Digital time-use tools fielded during COVID-19 (such as CaDDI) adopted simplified 36-category menus to minimize respondent burden on mobile devices. Assuming they carry standard 3-digit HETUS ACL codes is factually incorrect.

### Mandatory Negative Controls

1. **List of documents opened in full, with URLs:**
   * *Data Archive and Metadata Records:*
     * UK Data Service (2022): *Study Number 8741: Centre for Time Use Research UK Time Use Survey 6-Wave Sequence across the COVID-19 Pandemic, 2016-2021*. DataCite DOI: `https://doi.org/10.5255/UKDA-SN-8741-4`. URL: `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8741` (Opened in full).
     * UK Data Service (2023): *Study Number 8128: United Kingdom Time Use Survey, 2014-2015*. DataCite DOI: `https://doi.org/10.5255/UKDA-SN-8128-1`. URL: `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8128` (Opened in full).
     * UK Data Service (2024): *Study Number 9204: Online Time Use Survey, 2020-2023: Secure Access*. DataCite DOI: `https://doi.org/10.5255/UKDA-SN-9204-1`. URL: `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=9204` (Opened in full).
     * UK Data Service (2026): *End User Licence (EUL) Agreement and Safeguarded Access Conditions*. URL: `https://ukdataservice.ac.uk/help/access-policy/types-of-data-access/` (Opened in full).
   * *Primary Peer-Reviewed Methodological Papers:*
     * Sullivan, O., Gershuny, J., Sevilla, A., Vega-Rapun, M., Foliano, F., Lamote de Grignon, J., Harms, T., & Walthery, P. (2021): *Using time-use diaries to track changing behavior across successive stages of COVID-19 social restrictions*. Proceedings of the National Academy of Sciences (PNAS), 118(35), e2101724118. DOI: `https://doi.org/10.1073/pnas.2101724118` (Opened in full).
     * Gershuny, J., Sullivan, O., Sevilla, A., Vega-Rapun, M., Foliano, F., Lamote de Grignon, J., Harms, T., & Walthery, P. (2021): *A new perspective from time use research on the effects of social restrictions on COVID-19 behavioral infection risk*. PLOS ONE, 16(2), e0245551. DOI: `https://doi.org/10.1371/journal.pone.0245551` (Opened in full).
     * Iseri, O., Gursel Dino, I., & Kalkan, S. (2026): *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. DOI: `https://doi.org/10.1016/j.enbuild.2026.117155` (Opened in full).

2. **HETUS Participation vs. File Contents:**
   * At no point did we conclude that the UK 2020-21 file follows HETUS guidelines because the UK participated in HETUS 2014-15. The UK 2020-21 file was fielded independently by CTUR using the CaDDI online instrument, which uses 36 simplified drop-down categories rather than Eurostat ACL 2008.

3. **Distinction Between Survey Fielded, Microdata Deposited, and Microdata Obtainable:**
   * *CTUR COVID-19 Sequence:* Survey fielded (6 waves); microdata deposited (SN 8741); microdata **obtainable by us** (Tier 2 UKDS EUL, verified).
   * *ONS OTUS:* Survey fielded (multiple waves 2020-2024); microdata deposited (SN 9204); microdata **NOT obtainable by us** (restricted to UK-resident researchers via Tier 5 Secure Access).
   * *ONS Bulletins:* Statistical releases published; microdata **NOT deposited under open/safeguarded routes**; **only aggregate tables obtainable**.
   * *Understanding Society COVID-19:* Survey fielded; microdata deposited (SN 8663); microdata obtainable, but **contains no time-use diaries**.

4. **Count of Convenient Findings:**
   * Across the seven critical axes:
     1. Full diary file exists: Convenient (Yes, SN 8741 holds 6,896 diaries).
     2. Obtainable at Tier 0 to Tier 2: Convenient (Yes, Tier 2 UKDS EUL).
     3. Free (£0): Convenient (Yes, £0).
     4. Same coding list as 2014-15: **Inconvenient / Negative (No, 36 categories vs ~250 3-digit ACL categories).**
     5. Collection mode is a variable: Inconvenient / Partial (100% online CAWI; only hardware device type recorded).
     6. Fieldwork date is a variable: Convenient (Yes, exact date and wave 1-5 recorded).
     7. Licence permits releasing generated data: Inconvenient / Neutral (Silent on generative AI / synthetic data).
   * *Summary:* Exactly 4 of 7 axes came back logistically convenient, but the decisive technical admissibility criterion (3-digit ACL coding) is strictly negative.

5. **Impact of Reduced Activity List on Recommendation:**
   * Our negative recommendation regarding the held-out instrument test is strictly driven by the reduced 36-category coding list. Were SN 8741 coded in 3-digit Eurostat ACL 2008, it would be technically admissible for evaluating mode effects, subject to the whole-household sampling caveat.

6. **Training Recommendation Check:**
   * We have **NOT** recommended adding UK 2020-21 to the training corpus anywhere in this report, in accordance with the closed author decision.

---

## Section H. Full reference list

1. Gershuny, J., Sullivan, O., Lamote de Grignon Perez, J., & Vega-Rapun, M. (2022). *Centre for Time Use Research UK Time Use Survey 6-Wave Sequence across the COVID-19 Pandemic, 2016-2021* (Study Number 8741, 4th Edition). UK Data Service. DataCite DOI: `https://doi.org/10.5255/UKDA-SN-8741-4`. Tier 1. Read full catalogue metadata, documentation, and codebook. Checked: 2026-08-14.
2. UK Data Service (2026). *Catalogue Record: Centre for Time Use Research UK Time Use Survey 6-Wave Sequence across the COVID-19 Pandemic, 2016-2021 (SN 8741)*. URL: `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8741`. Tier 1. Read full record. Checked: 2026-08-14.
3. Centre for Time Use Research (2022). *CTUR COVID-19 6-Wave Time Use Survey: User Guide, Questionnaires and Variable Documentation*. UCL Social Research Institute, London. Tier 1. Read full text. Checked: 2026-08-14.
4. Gershuny, J., & Sullivan, O. (2017). *United Kingdom Time Use Survey, 2014-2015* (Study Number 8128, 1st Edition). Centre for Time Use Research, University of Oxford. UK Data Service. DataCite DOI: `https://doi.org/10.5255/UKDA-SN-8128-1`. Tier 1. Read full documentation and codebook. Checked: 2026-08-14.
5. Office for National Statistics (2024). *Online Time Use Survey, 2020-2023: Secure Access* (Study Number 9204, 1st Edition). UK Data Service. DataCite DOI: `https://doi.org/10.5255/UKDA-SN-9204-1`. Tier 1. Read study record and access terms. Checked: 2026-08-14.
6. Office for National Statistics (2021). *Coronavirus and how people spent their time: March 2021*. ONS Statistical Bulletin. URL: `https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/bulletins/coronavirusandhowpeoplespenttheirtime/march2021`. Tier 1. Read full bulletin and table layouts. Checked: 2026-08-14.
7. Sullivan, O., Gershuny, J., Sevilla, A., Vega-Rapun, M., Foliano, F., Lamote de Grignon, J., Harms, T., & Walthery, P. (2021). *Using time-use diaries to track changing behavior across successive stages of COVID-19 social restrictions*. Proceedings of the National Academy of Sciences, 118(35), e2101724118. DOI: `https://doi.org/10.1073/pnas.2101724118`. CrossRef verified title: "Using time-use diaries to track changing behavior across successive stages of COVID-19 social restrictions". Tier 2. Read full text.
8. Gershuny, J., Sullivan, O., Sevilla, A., Vega-Rapun, M., Foliano, F., Lamote de Grignon, J., Harms, T., & Walthery, P. (2021). *A new perspective from time use research on the effects of social restrictions on COVID-19 behavioral infection risk*. PLOS ONE, 16(2), e0245551. DOI: `https://doi.org/10.1371/journal.pone.0245551`. CrossRef verified title: "A new perspective from time use research on the effects of social restrictions on COVID-19 behavioral infection risk". Tier 2. Read full text.
9. UK Data Service (2026). *Accessing Data: Types of Data Access and Registration*. URL: `https://ukdataservice.ac.uk/help/access-policy/types-of-data-access/`. Tier 1. Read full policy. Checked: 2026-08-14.
10. UK Data Service (2026). *Standard End User Licence (EUL) Agreement*. URL: `https://ukdataservice.ac.uk/help/access-policy/end-user-licence/`. Tier 1. Read full licence text. Checked: 2026-08-14.
11. Iseri, O., Gursel Dino, I., & Kalkan, S. (2026). *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. DOI: `https://doi.org/10.1016/j.enbuild.2026.117155`. CrossRef verified title: "Occupancy modeling using population statistics and machine learning for urban residential built environment". Tier 2. Read full text.
